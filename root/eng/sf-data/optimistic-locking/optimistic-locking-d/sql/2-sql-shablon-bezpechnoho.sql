-- Крок 1: Читання поточного стану без блокувань
SELECT sku, available_stock, reserved_stock, lock_version
FROM warehouse_inventory
WHERE sku = 'CPU-RYZEN-9';
-- Отримано: available_stock = 15, reserved_stock = 0, lock_version = 1

-- Крок 2: Бізнес-перевірка в пам'яті: 15 >= 2 (потрібно зарезервувати 2 шт.)

-- Крок 3: Атомарна фіксація з предикатом версії
UPDATE warehouse_inventory
SET available_stock = available_stock - 2,
    reserved_stock = reserved_stock + 2,
    lock_version = lock_version + 1,
    last_updated_at = CURRENT_TIMESTAMP
WHERE sku = 'CPU-RYZEN-9'
  AND lock_version = 1;
