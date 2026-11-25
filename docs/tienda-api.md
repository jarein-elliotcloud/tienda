# TIENDA-1 · API de pedidos

## Arquitectura
Navegador/curl ─(Host: tienda.localhost)─> localhost:8080 ─> Traefik
  ─> Ingress "tienda" ─> Service "back" ─> 2 pods FastAPI
  ─> postgres.postgres.svc.cluster.local:5432 ─> postgres-0 (usuario app_rw)

## Decisiones
| Tema | Decisión | Motivo |
|---|---|---|
| Lenguaje | Python + FastAPI + psycopg 3 (pool) | Validación automática; reconexión del pool |
| Imagen | `k3d image import`, etiquetas versionadas (nunca `latest`) | Simple; registro + CI en ticket posterior |
| Usuario BBDD | `app_rw` estático, mínimo privilegio | Vault aún no existe (ticket posterior) |
| SQL de roles | `db/roles/app_rw.sql`, ejecución manual | El init solo corre con BBDD vacía; migraciones en ticket posterior |
| Contraseña | Secret `db-app` en ns `tienda`, creado a mano | Los Secrets no se leen entre namespaces; nunca en Git |

## Deuda técnica
- Imagen importada a mano (→ registro + CI).
- Usuario estático (→ credenciales dinámicas con Vault).
- Rol creado a mano (→ migraciones).

## Cómo probar
Ver pruebas de aceptación del ticket (curl con cabecera Host).
