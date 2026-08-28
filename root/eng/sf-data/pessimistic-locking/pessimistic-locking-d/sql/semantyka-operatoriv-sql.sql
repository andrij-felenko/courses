-- 1. Монопольне блокування для наступного оновлення або видалення
SELECT balance, status 
FROM accounts 
WHERE id = 42 
FOR UPDATE;

-- 2. Блокування модифікації без зміни унікальних ключів (PostgreSQL)
SELECT balance, updated_at 
FROM accounts 
WHERE id = 42 
FOR NO KEY UPDATE;

-- 3. Спільне блокування читання (захист від паралельних змін)
SELECT rate 
FROM currency_rates 
WHERE currency = 'USD' 
FOR SHARE;

-- 4. Слабке блокування для перевірки цілісності зовнішніх ключів (PostgreSQL)
SELECT id 
FROM users 
WHERE id = 100 
FOR KEY SHARE;
