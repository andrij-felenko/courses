-- KEYS[1]: Ключ кешу (наприклад, "product:42")
-- ARGV[1]: Нове значення (JSON рядок)
-- ARGV[2]: TTL у секундах
-- ARGV[3]: Токен лізи клієнта (lease_token)

local key = KEYS[1]
local value = ARGV[1]
local ttl = tonumber(ARGV[2])
local client_lease = tonumber(ARGV[3])
local lease_key = "lease:" .. key

local current_lease = tonumber(redis.call('GET', lease_key))

-- Якщо ліза в системі змінилася (відбувся запис/інвалідація), відхиляємо запізнілий запис
if current_lease and current_lease > client_lease then
    return 0 -- Відхилено: застаріла ліза (захист від Stale-Read Race)
end

redis.call('SET', key, value, 'EX', ttl)
return 1 -- Успішно записано
