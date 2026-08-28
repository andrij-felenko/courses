-- KEYS[1] = назва ключа лічильника, наприклад "quota:org_982:monthly_api_calls:2026-08"
-- ARGV[1] = запитувана кількість (amount)
-- ARGV[2] = максимальний ліміт (limit)
-- ARGV[3] = TTL вікна в секундах (windowSec)

local current = redis.call('GET', KEYS[1])
local usage = 0
if current then
    usage = tonumber(current)
end

local requested = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])

if usage + requested > limit then
    -- Перевищення ліміту: повертаємо 0 (заборонено) і поточне значення
    return {0, usage}
else
    -- Ліміт не вичерпано: збільшуємо лічильник атомарно
    local new_val = redis.call('INCRBY', KEYS[1], requested)
    if not current then
        redis.call('EXPIRE', KEYS[1], tonumber(ARGV[3]))
    end
    return {1, new_val}
end
