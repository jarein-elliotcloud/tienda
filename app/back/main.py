"""API de pedidos de la tienda (TIENDA-1)."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from psycopg import OperationalError, errors
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool, PoolTimeout

# --- Conexión: todo viene de variables de entorno (nada escrito en el código) ---
pool = ConnectionPool(
    kwargs={
        "host": os.environ["DB_HOST"],
        "port": os.environ.get("DB_PORT", "5432"),
        "dbname": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "connect_timeout": 3,
    },
    min_size=1,
    max_size=5,
    open=False,                             # se abre en el arranque (lifespan)
    check=ConnectionPool.check_connection,  # comprueba cada conexión antes de prestarla
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open(wait=False)   # no bloquear el arranque si Postgres no está
    yield
    pool.close()


app = FastAPI(title="Tienda · API de pedidos", lifespan=lifespan)


# --- Si la base de datos no responde: 503, nunca 500 ---
@app.exception_handler(PoolTimeout)
@app.exception_handler(OperationalError)
async def bbdd_no_disponible(request: Request, exc: Exception):
    return JSONResponse(status_code=503, content={"detail": "Base de datos no disponible"})


# --- Modelos: validan el JSON de entrada ---
class Linea(BaseModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0)


class PedidoIn(BaseModel):
    cliente_id: int = Field(gt=0)
    lineas: list[Linea] = Field(min_length=1)


# --- Endpoints ---
@app.get("/vivo")
def vivo():
    """Liveness: el proceso responde. NO mira la base de datos."""
    return {"estado": "vivo"}


@app.get("/salud")
def salud():
    """Readiness: solo OK si podemos hablar con Postgres."""
    with pool.connection(timeout=2) as conn:
        conn.execute("SELECT 1")
    return {"estado": "ok"}


@app.post("/pedidos", status_code=201)
def crear_pedido(pedido: PedidoIn):
    try:
        # Una transacción: COMMIT al salir del bloque, ROLLBACK si hay excepción
        with pool.connection() as conn:
            pedido_id = conn.execute(
                "INSERT INTO pedidos (cliente_id) VALUES (%s) RETURNING id",
                (pedido.cliente_id,),
            ).fetchone()[0]
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO lineas_pedido (pedido_id, producto_id, cantidad) "
                    "VALUES (%s, %s, %s)",
                    [(pedido_id, l.producto_id, l.cantidad) for l in pedido.lineas],
                )
    except errors.ForeignKeyViolation:
        raise HTTPException(422, "El cliente o algún producto no existe")
    except errors.UniqueViolation:
        raise HTTPException(422, "Hay productos repetidos en las líneas")
    except errors.CheckViolation:
        raise HTTPException(422, "Algún valor está fuera de rango")
    return {"id": pedido_id}


@app.get("/pedidos/{pedido_id}")
def obtener_pedido(pedido_id: int):
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id, cliente_id, fecha, estado FROM pedidos WHERE id = %s",
                (pedido_id,),
            )
            pedido = cur.fetchone()
            if pedido is None:
                raise HTTPException(404, "Pedido no encontrado")
            cur.execute(
                "SELECT producto_id, cantidad FROM lineas_pedido "
                "WHERE pedido_id = %s ORDER BY producto_id",
                (pedido_id,),
            )
            pedido["lineas"] = cur.fetchall()
    return pedido
