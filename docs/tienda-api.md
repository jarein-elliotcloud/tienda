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

## Resultados de aceptación (2026-11-26)
| Criterio | Prueba | Resultado |
|---|---|---|
| 1 Transacción | POST con producto inexistente → sin pedido huérfano | ✅ 422, id consumido y deshecho |
| 2 GET | `/pedidos/{id}` y `/pedidos/99999999` | ✅ 200 / 404 |
| 3 Errores 4xx | cliente inexistente, cantidad 0, producto repetido | ✅ 422 (BBDD) / 422 (Pydantic) |
| 4 Salud | `/salud` con y sin Postgres | ✅ 200 / 503 |
| 5–6 Imagen y Argo | `tienda-back:0.1.0`, Application `tienda` | ✅ Synced / Healthy |
| 7 Ingress | `tienda.localhost:8080` | ✅ |
| 8 Réplicas y probes | 2 réplicas; liveness `/vivo`, readiness `/salud` | ✅ |
| 9 Sin secretos en Git | `git grep password` | ✅ solo referencias |
| 10 Mínimo privilegio | `pg_stat_activity` | ✅ `app_rw` desde IPs de los pods |
| 11 Resiliencia | `kubectl delete pod postgres-0` | ✅ pods 0/1 sin reinicios, vuelven solos |

## Lecciones
- La liveness nunca depende de otros servicios: si mirase Postgres, su caída reiniciaría la API en bucle (CrashLoopBackOff).
- Traefik: 404 = ninguna regla coincide; 503 = regla sin pods listos detrás.
- Un Ingress sin `host:` actúa como comodín (lo comprobamos con un `Host` mal escrito que acabó en whoami).
