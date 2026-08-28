-- KEYS[1]: ключ замка (наприклад, "lock:cache:product:7821")
-- ARGV[1]: унікальний токен клієнта (UUID + ID горутини/потоку)
-- ARGV[2]: таймаут оренди в мілісекундах (lease TTL, наприклад 5000)

local acquired = redis.call('SET', KEYS[1], ARGV[1], 'NX', 'PX', ARGV[2])
if acquired then
    return 1
else
    return 0
end
