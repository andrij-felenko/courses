local raw = redis.call('GET', KEYS[1])
if not raw then
  return {0, 'NOT_FOUND'}
end

local current = cjson.decode(raw)
local expected_version = tonumber(ARGV[1])

if current.version ~= expected_version then
  return {0, 'VERSION_CONFLICT', tostring(current.version)}
end

redis.call('SET', KEYS[1], ARGV[2], 'EX', tonumber(ARGV[3]))
return {1, 'OK'}
