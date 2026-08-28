-- KEYS[1]: Ключ бакета орендаря (наприклад, "quota:tenant_123:requests")
-- ARGV[1]: Максимальна місткість бакета (Max Tokens / Capacity)
-- ARGV[2]: Швидкість поповнення (Refill Rate, токенів на секунду)
-- ARGV[3]: Поточний Unix-час у мілісекундах
-- ARGV[4]: Кількість запитуваних токенів (Requested Tokens)

local bucket_key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now_ms = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

-- Зчитуємо поточний стан бакета (наявні токени та час останнього оновлення)
local data = redis.call("HMGET", bucket_key, "tokens", "last_updated_ms")
local current_tokens = tonumber(data[1])
local last_updated_ms = tonumber(data[2])

if current_tokens == nil then
    -- Перший запит: ініціалізуємо бакет повним обсягом
    current_tokens = capacity
    last_updated_ms = now_ms
else
    -- Розраховуємо кількість токенів, накопичених за час простою
    local elapsed_seconds = math.max(0, (now_ms - last_updated_ms) / 1000.0)
    local generated_tokens = elapsed_seconds * refill_rate
    current_tokens = math.min(capacity, current_tokens + generated_tokens)
    last_updated_ms = now_ms
end

-- Перевіряємо, чи достатньо токенів для задоволення запиту
local allowed = 0
local remaining = current_tokens
local retry_after_ms = 0

if current_tokens >= requested then
    allowed = 1
    current_tokens = current_tokens - requested
    remaining = current_tokens
else
    allowed = 0
    local missing_tokens = requested - current_tokens
    retry_after_ms = math.ceil((missing_tokens / refill_rate) * 1000.0)
end

-- Зберігаємо оновлений стан із TTL (подвійний час заповнення для автоочищення пам'яті)
local ttl_seconds = math.ceil((capacity / refill_rate) * 2)
redis.call("HMSET", bucket_key, "tokens", current_tokens, "last_updated_ms", last_updated_ms)
redis.call("EXPIRE", bucket_key, math.max(3600, ttl_seconds))

-- Повертаємо: [чи дозволено (1/0), залишок токенів, час очікування в мс]
return { allowed, math.floor(remaining), retry_after_ms }
