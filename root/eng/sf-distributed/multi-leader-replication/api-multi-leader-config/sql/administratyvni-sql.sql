-- 1. Створення та реєстрація локального лідера в кластері
SELECT bdr.create_node(
    node_name := 'node_frankfurt_1',
    local_dsn := 'host=10.0.1.5 port=5432 dbname=production user=bdr_admin password=secret'
);

-- 2. Приєднання до існуючого кластера через віддалений лідер
SELECT bdr.join_node_group(
    join_target_dsn := 'host=10.0.2.5 port=5432 dbname=production user=bdr_admin password=secret',
    node_group_name := 'global_ecommerce_cluster',
    pause_on_join := false
);

-- 3. Реєстрація спеціалізованого резолвера для конкретної таблиці
SELECT bdr.alter_table_conflict_handler(
    relation := 'orders'::regclass,
    handler_name := 'orders_crdt_field_merge',
    handler_type := 'custom_function',
    function_name := 'public.resolve_orders_conflict(bdr.conflict_data)'
);
