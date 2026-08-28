-- KEYS[1]: ключ ресурсу даних (наприклад, "data:account:48291")
-- KEYS[2]: ключ метаданих токена (наприклад, "token:account:48291")
-- ARGV[1]: новий токен (fencing_token)
-- ARGV[2]: нові дані (payload)

local current_token = redis.call('GET', KEYS[2])
local req_token = tonumber(ARGV[1])

if not current_token or req_token >= tonumber(current_token) then
    redis.call('SET', KEYS[2], req_token)
    redis.call('SET', KEYS[1], ARGV[2])
    return {1, req_token} -- Успіх: статус 1
else
    return {0, tonumber(current_token)} -- Відхилено: статус 0, поточний максимум
end
