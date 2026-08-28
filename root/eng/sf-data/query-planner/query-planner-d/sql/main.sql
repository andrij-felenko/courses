-- ❌ НЕ-SARGable: функція date_part ламає індекс за created_at. Повний Seq Scan!
SELECT * FROM orders WHERE date_part('year', created_at) = 2026;

-- ✅ SARGable: пряме порівняння константного діапазону. Швидкий Index Scan!
SELECT * FROM orders 
WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01';

-- ❌ НЕ-SARGable: функція lower() над стовпцем
SELECT * FROM users WHERE lower(email) = 'user@example.com';

-- ✅ Рішення: створення функціонального індексу за виразом
CREATE INDEX idx_users_lower_email ON users (lower(email));
