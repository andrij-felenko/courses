CREATE TABLE product_stock_shards (
    product_id BIGINT NOT NULL,
    shard_id INT NOT NULL,
    available_stock INT NOT NULL CHECK (available_stock >= 0),
    lock_version BIGINT NOT NULL DEFAULT 1,
    PRIMARY KEY (product_id, shard_id)
);

-- Розбиваємо 100 одиниць товару на 10 незалежних слотів:
INSERT INTO product_stock_shards (product_id, shard_id, available_stock)
VALUES 
    (501, 0, 10), (501, 1, 10), (501, 2, 10), (501, 3, 10), (501, 4, 10),
    (501, 5, 10), (501, 6, 10), (501, 7, 10), (501, 8, 10), (501, 9, 10);
