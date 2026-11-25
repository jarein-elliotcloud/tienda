-- Rol de la API (TIENDA-1). Ejecutar como tienda_admin, UNA vez.
-- Uso: psql -v app_password='...' -f app_rw.sql
CREATE ROLE app_rw LOGIN PASSWORD :'app_password';

GRANT CONNECT ON DATABASE tienda TO app_rw;
GRANT USAGE   ON SCHEMA public   TO app_rw;

GRANT SELECT         ON clientes, productos       TO app_rw;
GRANT SELECT, INSERT ON pedidos, lineas_pedido    TO app_rw;
GRANT USAGE          ON SEQUENCE pedidos_id_seq   TO app_rw;
