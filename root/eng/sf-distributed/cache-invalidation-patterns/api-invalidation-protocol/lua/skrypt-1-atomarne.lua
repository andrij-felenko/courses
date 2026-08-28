-- KEYS[1]: Ключ тегу (наприклад, "tag:item:42")
-- Повертає: Кількість видалених ключів

local tag_key = KEYS[1]
local keys_to_del = redis.call('SMEMBERS', tag_key)

if #keys_to_del == 0 then
    redis.call('UNLINK', tag_key)
    return 0
end

-- Неблокуюче видалення всіх пов'язаних ключів у фоновому потоці Redis
local deleted_count = redis.call('UNLINK', unpack(keys_to_del))

-- Видаляємо сам індексний ключ тегу
redis.call('UNLINK', tag_key)

return deleted_count
