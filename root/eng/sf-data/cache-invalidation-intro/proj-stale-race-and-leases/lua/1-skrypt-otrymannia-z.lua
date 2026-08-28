local key = KEYS[1]
local lease_ttl_sec = tonumber(ARGV[1]) or 5

local val = redis.call('HGET', key, 'val')
local is_valid = redis.call('HGET', key, 'valid')

if is_valid == '1' then
    return {'HIT', val, '0'}
end

local active_token = redis.call('HGET', key, 'token')
local now = redis.call('TIME')[1]
local expiry = tonumber(redis.call('HGET', key, 'expiry') or '0')

if active_token and tonumber(now) < expiry then
    return {'BUSY', '', '0'}
end

local next_token = tostring(redis.call('INCR', 'global:lease:counter'))
redis.call('HSET', key, 'token', next_token, 'expiry', tostring(tonumber(now) + lease_ttl_sec), 'valid', '0')

return {'GRANTED', '', next_token}
