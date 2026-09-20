-- test_rate_limiter.lua
-- Модульні тести для перевірки логіки sliding_window.lua без підключення до живого Redis.
-- Містить локальний mock оточення Redis (redis.call, ZSET, PEXPIRE).

-- ============================================================================
-- 1. Mock середовища Redis в пам'яті
-- ============================================================================

local redis_mock = {
    data = {},         -- key -> list of { score = number, member = string }
    expirations = {}   -- key -> ttl_ms
}

function redis_mock.reset()
    redis_mock.data = {}
    redis_mock.expirations = {}
end

local function mock_call(cmd, ...)
    local args = { ... }
    local command = string.upper(cmd)

    if command == 'ZREMRANGEBYSCORE' then
        local key = args[1]
        local min_val = args[2]
        local max_arg = args[3]
        local zset = redis_mock.data[key] or {}

        local new_zset = {}
        local removed = 0
        for _, item in ipairs(zset) do
            local matches_min = (min_val == '-inf') or (item.score >= tonumber(min_val))
            local matches_max = (max_arg == '+inf') or (item.score <= tonumber(max_arg))
            if matches_min and matches_max then
                removed = removed + 1
            else
                table.insert(new_zset, item)
            end
        end
        redis_mock.data[key] = new_zset
        return removed

    elseif command == 'ZCARD' then
        local key = args[1]
        local zset = redis_mock.data[key] or {}
        return #zset

    elseif command == 'ZADD' then
        local key = args[1]
        local score = tonumber(args[2])
        local member = tostring(args[3])
        local zset = redis_mock.data[key] or {}

        local found = false
        for _, item in ipairs(zset) do
            if item.member == member then
                item.score = score
                found = true
                break
            end
        end

        local added = 0
        if not found then
            table.insert(zset, { score = score, member = member })
            added = 1
        end

        -- Підтримуємо елементи впорядкованими за score
        table.sort(zset, function(a, b)
            if a.score == b.score then
                return a.member < b.member
            end
            return a.score < b.score
        end)
        redis_mock.data[key] = zset
        return added

    elseif command == 'PEXPIRE' then
        local key = args[1]
        local ttl = tonumber(args[2])
        redis_mock.expirations[key] = ttl
        return 1

    elseif command == 'ZRANGE' then
        local key = args[1]
        local start_idx = tonumber(args[2]) -- 0-based
        local stop_idx = tonumber(args[3])
        local with_scores = (args[4] and string.upper(tostring(args[4])) == 'WITHSCORES')
        local zset = redis_mock.data[key] or {}
        local res = {}

        if #zset == 0 then return res end

        local s = start_idx + 1
        local e = (stop_idx == -1) and #zset or (stop_idx + 1)
        if s < 1 then s = 1 end
        if e > #zset then e = #zset end

        for i = s, e do
            table.insert(res, zset[i].member)
            if with_scores then
                table.insert(res, tostring(zset[i].score))
            end
        end
        return res

    else
        error("Невідома команда Redis у mock-об'єкті: " .. tostring(cmd))
    end
end

-- Реєструємо глобальне середовище Redis
_G.redis = {
    call = mock_call,
    error_reply = function(msg) return { err = msg } end
}

-- ============================================================================
-- 2. Завантаження цільового скрипта sliding_window.lua
-- ============================================================================

local function load_sliding_window()
    local filename = "sliding_window.lua"
    local file = io.open(filename, "r")
    if not file then
        local dir = ""
        if arg and arg[0] then
            dir = arg[0]:match("^(.*[/\\])") or ""
        elseif debug and debug.getinfo then
            local info = debug.getinfo(1, "S")
            if info and info.source then
                dir = info.source:match("^@?(.*[/\\])") or ""
            end
        end
        file = io.open(dir .. filename, "r")
    end

    if not file then
        error("Не вдалося відкрити файл " .. filename .. " для тестування")
    end

    local code = file:read("*a")
    file:close()

    local loader = loadstring or load
    local chunk, err = loader(code, filename)
    if not chunk then
        error("Помилка компіляції скрипта " .. filename .. ": " .. tostring(err))
    end
    return chunk
end

local script_runner = load_sliding_window()

local function execute_limiter(key, now_ms, window_ms, limit, req_id)
    _G.KEYS = { key }
    _G.ARGV = {
        tostring(now_ms),
        tostring(window_ms),
        tostring(limit),
        req_id and tostring(req_id) or nil
    }
    return script_runner()
end

-- ============================================================================
-- 3. Набір тестів
-- ============================================================================

local passed_tests = 0

local function assert_equal(actual, expected, message)
    if actual ~= expected then
        error(string.format("ASSERT FAILED: %s (Очікувалося: %s, Отримано: %s)",
            message or "", tostring(expected), tostring(actual)))
    end
end

local function run_suite()
    print("--- Старт тестування атомарного ковзного лімітера Redis Lua ---")

    -- Тест 1: Дозволені запити в межах ліміту
    do
        redis_mock.reset()
        local key = "rate:client_1"
        local window = 1000 -- 1 секунда
        local limit = 3

        local res1 = execute_limiter(key, 1000, window, limit, "req_1")
        assert_equal(res1[1], 1, "Запит 1 має бути дозволено")
        assert_equal(res1[2], 2, "Залишок після запиту 1 має дорівнювати 2")

        local res2 = execute_limiter(key, 1100, window, limit, "req_2")
        assert_equal(res2[1], 1, "Запит 2 має бути дозволено")
        assert_equal(res2[2], 1, "Залишок після запиту 2 має дорівнювати 1")

        local res3 = execute_limiter(key, 1200, window, limit, "req_3")
        assert_equal(res3[1], 1, "Запит 3 має бути дозволено")
        assert_equal(res3[2], 0, "Залишок після запиту 3 має бути 0")

        passed_tests = passed_tests + 1
        print("[PASS] Тест 1: Послідовні запити в межах квоти успішно дозволено.")
    end

    -- Тест 2: Перевищення ліміту блокується з коректним retry_after
    do
        local key = "rate:client_1"
        local window = 1000
        local limit = 3

        -- 4-й запит у межах того ж вікна (t = 1300)
        local res4 = execute_limiter(key, 1300, window, limit, "req_4")
        assert_equal(res4[1], 0, "Запит 4 має бути відхилено")
        assert_equal(res4[2], 0, "Залишок має бути 0")

        -- Найстаріший запит був на t = 1000. Він вийде з вікна на t = 2000.
        -- Зараз t = 1300, отже retry_after = 2000 - 1300 = 700 мс.
        assert_equal(res4[3], 700, "Очікуваний час очікування 700 мс")

        passed_tests = passed_tests + 1
        print("[PASS] Тест 2: Перевищення ліміту блокується, час retry-after розраховано коректно.")
    end

    -- Тест 3: Зсув вікна у часі вичищає застарілі мітки та повертає квоту
    do
        local key = "rate:client_1"
        local window = 1000
        local limit = 3

        -- Робимо запит у момент t = 2050 (минуло 1050 мс від req_1)
        -- req_1 (t=1000) вже вийшов за межу вікна (2050 - 1000 = 1050 >= 1000)
        -- Але req_2 (t=1100) та req_3 (t=1200) ще всередині вікна.
        local res5 = execute_limiter(key, 2050, window, limit, "req_5")
        assert_equal(res5[1], 1, "Запит на t=2050 має бути дозволено після зсуву вікна")
        -- У вікні лишилися req_2, req_3 і додався req_5 -> всього 3, залишок 0
        assert_equal(res5[2], 0, "Залишок має бути 0, бо у вікні активні 3 запити")

        passed_tests = passed_tests + 1
        print("[PASS] Тест 3: Зсув ковзного вікна коректно видаляє застарілі події.")
    end

    -- Тест 4: Запити в одну й ту саму мілісекунду з унікальними ID не перезаписуються
    do
        redis_mock.reset()
        local key = "rate:client_concurrent"
        local window = 1000
        local limit = 2

        -- Два запити в однаковий момент t = 5000, але з різними req_id
        local r1 = execute_limiter(key, 5000, window, limit, "uuid_alpha")
        local r2 = execute_limiter(key, 5000, window, limit, "uuid_beta")
        local r3 = execute_limiter(key, 5000, window, limit, "uuid_gamma")

        assert_equal(r1[1], 1, "Перший одночасний запит дозволено")
        assert_equal(r2[1], 1, "Другий одночасний запит дозволено")
        assert_equal(r3[1], 0, "Третій одночасний запит заблоковано")

        local total_in_zset = redis.call('ZCARD', key)
        assert_equal(total_in_zset, 2, "У множині ZSET мають зберегтися обидва унікальні записи")

        passed_tests = passed_tests + 1
        print("[PASS] Тест 4: Колізії в одну мілісекунду успішно розв'язуються за req_id.")
    end

    -- Тест 5: Поновлення TTL (PEXPIRE) під час кожного успішного запиту
    do
        local key = "rate:client_concurrent"
        local ttl = redis_mock.expirations[key]
        assert_equal(ttl, 1000, "Ключ отримав актуальний TTL відповідно до розміру вікна")

        passed_tests = passed_tests + 1
        print("[PASS] Тест 5: Поновлення PEXPIRE запобігає витокам пам'яті в Redis.")
    end

    -- Тест 6: Захист від граничного сплеску трафіку (перевага ковзного вікна над фіксованим)
    do
        redis_mock.reset()
        local key = "rate:burst_protection"
        local window = 1000
        local limit = 3

        -- Сплеск із 3 запитів наприкінці першої секунди
        assert_equal(execute_limiter(key, 900, window, limit, "b1")[1], 1, "Сплеск 1 дозволено")
        assert_equal(execute_limiter(key, 950, window, limit, "b2")[1], 1, "Сплеск 2 дозволено")
        assert_equal(execute_limiter(key, 990, window, limit, "b3")[1], 1, "Сплеск 3 дозволено")

        -- У фіксованому вікні на t=1010 лічильник скинувся б, дозволивши ще 3 запити (подвоєння на стику).
        -- У ковзному вікні події 900, 950, 990 все ще активні (1010 - 1000 = 10 < 900).
        local burst_next = execute_limiter(key, 1010, window, limit, "b4")
        assert_equal(burst_next[1], 0, "Ковзне вікно блокує граничний сплеск на початку наступної секунди")
        assert_equal(burst_next[3], 900 + 1000 - 1010, "Час очікування до звільнення найдавнішого запису (890 мс)")

        passed_tests = passed_tests + 1
        print("[PASS] Тест 6: Захист від подвоєння ліміту на стику інтервалів успішно підтверджено.")
    end

    -- Тест 7: Захист від некоректних аргументів
    do
        _G.KEYS = {}
        _G.ARGV = {}
        local res_err = script_runner()
        assert_equal(type(res_err), "table", "Очікується таблиця помилки від Redis")
        assert_equal(res_err.err ~= nil, true, "Повинно бути зафіксовано повідомлення про помилку")

        passed_tests = passed_tests + 1
        print("[PASS] Тест 7: Некоректні параметри відхиляються без аварійного завершення.")
    end

    print(string.format("=== Усі %d тестів успішно виконано! ===", passed_tests))
end

run_suite()
