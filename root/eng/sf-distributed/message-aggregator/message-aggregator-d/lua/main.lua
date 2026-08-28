-- Lua-скрипт атомарного додавання та оцінки завершення
local corr_id = KEYS[1]
local seq_num = ARGV[1]
local expected_total = tonumber(ARGV[2])
local payload = ARGV[3]
local now_ts = tonumber(ARGV[4])

-- 1. Перевірка надгробка
if redis.call('EXISTS', 'tombstone:' .. corr_id) == 1 then
    return -1 -- TOMBSTONE_REJECTED
end

-- 2. Дедуплікація та додавання елемента
local added = redis.call('HSETNX', 'bucket:' .. corr_id, seq_num, payload)
if added == 0 then
    return 0 -- DUPLICATE
end

-- 3. Оновлення таймера бездіяльності у Sorted Set
redis.call('ZADD', 'active_buckets_ttl', now_ts, corr_id)

-- 4. Перевірка повноти
local count = redis.call('HLEN', 'bucket:' .. corr_id)
if expected_total > 0 and count == expected_total then
    local items = redis.call('HGETALL', 'bucket:' .. corr_id)
    redis.call('DEL', 'bucket:' .. corr_id)
    redis.call('ZREM', 'active_buckets_ttl', corr_id)
    redis.call('SETEX', 'tombstone:' .. corr_id, 3600, '1')
    return items -- Повернення повного комплекту для емісії
end

return 1 -- Накопичення триває
