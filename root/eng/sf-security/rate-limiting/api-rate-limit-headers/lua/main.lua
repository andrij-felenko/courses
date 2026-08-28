-- Отримання вхідних аргументів
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local cost = tonumber(ARGV[3])
local now = tonumber(ARGV[4])

-- Зчитування поточного стану з Redis Hash
local data = redis.call("HMGET", key, "tokens", "last_updated")
local tokens = tonumber(data[1])
local last_updated = tonumber(data[2])

if tokens == nil then
    -- Перший запит: відро повністю заповнене
    tokens = capacity
    last_updated = now
else
    -- Обчислення лінивого поповнення токенів
    local elapsed = math.max(0, now - last_updated)
    tokens = math.min(capacity, tokens + elapsed * refill_rate)
    last_updated = now
end

local allowed = 0
local remaining = tokens
local retry_after = 0

if tokens >= cost then
    -- Запит дозволено
    allowed = 1
    tokens = tokens - cost
    remaining = tokens
else
    -- Запит відхилено: розрахунок часу очікування до накопичення необхідних токенів
    allowed = 0
    local needed = cost - tokens
    retry_after = math.ceil(needed / refill_rate)
end

-- Збереження оновленого стану
redis.call("HMSET", key, "tokens", tokens, "last_updated", last_updated)

-- Встановлення TTL: час до повного поповнення порожнього відра + запас 60 с
local ttl = math.ceil(capacity / refill_rate) + 60
redis.call("EXPIRE", key, ttl)

-- Повернення масиву результату: [allowed (1 або 0), remaining_tokens, retry_after_sec]
return { allowed, math.floor(remaining), retry_after }
