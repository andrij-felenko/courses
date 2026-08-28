-- У межах транзакції додавання позиції товару:
INSERT INTO order_items (order_id, sku, price_cents, quantity)
VALUES (101, 'MOUSE', 5000, 1);

-- Примусовий інкремент версії батьківського замовлення:
UPDATE orders
SET lock_version = lock_version + 1,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 101
  AND lock_version = 5;
