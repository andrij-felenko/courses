   -- KEYS[1] = key, ARGV[1] = payload_hash, ARGV[2] = lease_sec, ARGV[3] = now
   local current = redis.call('HMGET', KEYS[1], 'state', 'hash', 'code', 'body', 'expires')
   local state = current[1]
   local hash = current[2]
   local code = current[3]
   local body = current[4]
   local expires = tonumber(current[5] or 0)
   local now = tonumber(ARGV[3])

   if not state then
       -- Новий ключ: резервуємо
       redis.call('HMSET', KEYS[1], 'state', 'IN_PROGRESS', 'hash', ARGV[1], 'expires', now + tonumber(ARGV[2]))
       redis.call('EXPIRE', KEYS[1], 86400)
       return { 'EXECUTE' }
   elseif state == 'COMMITTED' then
       if hash ~= ARGV[1] then
           return { 'MISMATCH' }
       end
       return { 'CACHED', code, body }
   elseif state == 'IN_PROGRESS' then
       if now < expires then
           return { 'CONFLICT' }
       else
           -- Перехоплення оренди
           redis.call('HSET', KEYS[1], 'hash', ARGV[1], 'expires', now + tonumber(ARGV[2]))
           return { 'EXECUTE' }
       end
   end
