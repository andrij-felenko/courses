-- Lua script executed inside Redis Cluster for atomic queue token release
-- KEYS[1]: Active Queue Key (ZSET: queue:event_123)
-- KEYS[2]: Admitted Users Counter Key (STRING: counter:event_123)
-- ARGV[1]: Current Time (Epoch Seconds)
-- ARGV[2]: Batch Size (Capacity limit r(t))
-- ARGV[3]: Token TTL (Seconds, e.g., 600)

local queue_key = KEYS[1]
local counter_key = KEYS[2]
local current_time = tonumber(ARGV[1])
local batch_size = tonumber(ARGV[2])
local ttl = tonumber(ARGV[3])

-- 1. Витягуємо перших batch_size користувачів за найменшим timestamp/position score
local users = redis.call('ZRANGE', queue_key, 0, batch_size - 1)

if #users == 0 then
    return {}
end

local admitted_users = {}

for i, user_id in ipairs(users) do
    -- 2. Видаляємо користувача із ZSET черги
    redis.call('ZREM', queue_key, user_id)
    
    -- 3. Інкрементуємо лічильник допущених
    local new_pos = redis.call('INCR', counter_key)
    
    table.insert(admitted_users, user_id .. ":" .. tostring(new_pos))
end

return admitted_users
