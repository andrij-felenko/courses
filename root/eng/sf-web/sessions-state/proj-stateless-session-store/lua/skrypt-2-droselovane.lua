local raw = redis.call('GET', KEYS[1])
if not raw then
  return 0
end

local doc = cjson.decode(raw)
local now = tonumber(ARGV[1])
local threshold = tonumber(ARGV[2])

if (now - doc.lastTouch) >= threshold then
  doc.lastTouch = now
  local updated_json = cjson.encode(doc)
  redis.call('SET', KEYS[1], updated_json, 'EX', tonumber(ARGV[3]))
  return 1
end

return 2 -- дійсний стан, оновлення TTL наразі не потрібне
