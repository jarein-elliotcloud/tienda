INSERT INTO clientes (nombre, email)
SELECT 'Cliente ' || g, 'cliente' || g || '@ejemplo.com'
FROM generate_series(1, 10000) g;

INSERT INTO productos (nombre, precio)
SELECT 'Producto ' || g, round((random() * 100)::numeric, 2)
FROM generate_series(1, 500) g;

INSERT INTO pedidos (cliente_id, fecha)
SELECT (random() * 9999)::int + 1,
       now() - ((random() * 365) || ' days')::interval
FROM generate_series(1, 200000);

INSERT INTO lineas_pedido (pedido_id, producto_id, cantidad)
SELECT p.id, ((p.id * 7 + n) % 500) + 1, (random() * 4)::int + 1
FROM pedidos p, generate_series(1, 3) n;

ANALYZE;   -- actualiza las estadísticas que usa el planificador
