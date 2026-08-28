CREATE TABLE warehouse_inventory (
    sku VARCHAR(64) PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    available_stock INT NOT NULL CHECK (available_stock >= 0),
    reserved_stock INT NOT NULL DEFAULT 0,
    lock_version BIGINT NOT NULL DEFAULT 1,
    last_updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Початкові дані
INSERT INTO warehouse_inventory (sku, item_name, available_stock, reserved_stock, lock_version)
VALUES ('CPU-RYZEN-9', 'AMD Ryzen 9 7950X', 15, 0, 1);
