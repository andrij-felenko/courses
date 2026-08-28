local key = KEYS[1]
local val = ARGV[1]
local token = ARGV[2]

local active_token = redis.call('HGET', key, 'token')

if active_token == token then
    redis.call('HSET', key, 'val', val, 'valid', '1', 'token', '')
    redis.call('HDEL', key, 'expiry')
    return 1 -- Успішний запис
else
    return 0 -- Відхилено: токен застарів (stale token)
end
