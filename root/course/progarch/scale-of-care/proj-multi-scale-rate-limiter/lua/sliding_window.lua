-- sliding_window.lua
-- Атомарний розподілений лімітер інтенсивності запитів (Sliding Window Rate Limiter)
-- Виконується безпосередньо в середовищі Redis через команду EVAL / EVALSHA.
--
-- Параметри:
-- KEYS[1] - ключ лімітера для ресурсу або клієнта (наприклад, "ratelimit:user:42:api")
-- ARGV[1] - поточний час у мілісекундах (now_ms)
-- ARGV[2] - розмір ковзного вікна у мілісекундах (window_ms)
-- ARGV[3] - максимально допустима кількість запитів у вікні (max_requests)
-- ARGV[4] - унікальний ідентифікатор запиту (request_id, необов'язковий)
--
-- Повертає масив:
-- [1] - вердикт: 1 (дозволено) або 0 (відхилено)
-- [2] - залишок квоти у поточному вікні (remaining)
-- [3] - час до звільнення найближчого слота в мілісекундах (retry_after_ms)

local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local req_id = ARGV[4]

-- Перевірка валідності вхідних параметрів
if not key or key == "" then
    return redis.error_reply("KEYS[1] (ключ лімітера) є обов'язковим")
end

if not now or not window or not limit or window <= 0 or limit <= 0 then
    return redis.error_reply("Некоректні аргументи ARGV: очікуються додатні числа now_ms, window_ms, limit")
end

-- 1. Обчислюємо ліву (застарілу) межу ковзного вікна.
-- Будь-які події з міткою часу <= window_start вийшли за межі вікна тривалістю window_ms.
local window_start = now - window

-- 2. Атомарно видаляємо з упорядкованої множини (ZSET) усі застарілі записи.
-- Очищення відбувається безпосередньо в сховищі без пересилання даних через мережу.
redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

-- 3. Зчитуємо поточну кількість актуальних запитів у вікні
local current_requests = tonumber(redis.call('ZCARD', key)) or 0

if current_requests < limit then
    -- Ліміт не перевищено: реєструємо новий запит у ZSET.
    -- Якщо унікальний request_id не передано, формуємо суфікс із лічильника активних запитів,
    -- що гарантує унікальність елемента й запобігає колізіям однакових міток часу.
    local unique_suffix = (req_id and req_id ~= "") and req_id or tostring(current_requests + 1)
    local member = now .. ":" .. unique_suffix
    redis.call('ZADD', key, now, member)

    -- Поновлюємо час життя ключа на розмір вікна (PEXPIRE у мс),
    -- щоб неактивні лімітери автоматично вилучалися з оперативної пам'яті Redis.
    redis.call('PEXPIRE', key, window)

    local remaining = limit - current_requests - 1
    return { 1, remaining, 0 }
else
    -- Ліміт вичерпано: запит блокується без модифікації ZSET.
    -- Знаходимо найстаріший запис у поточному вікні, щоб розрахувати паузу до вивільнення слота.
    local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
    local retry_after = 0

    if oldest and #oldest >= 2 then
        local oldest_time = tonumber(oldest[2])
        if oldest_time then
            local slot_freed_at = oldest_time + window
            if slot_freed_at > now then
                retry_after = slot_freed_at - now
            else
                retry_after = 1
            end
        else
            retry_after = window
        end
    else
        -- Запобіжник на випадок граничних умов
        retry_after = window
    end

    return { 0, 0, retry_after }
end
