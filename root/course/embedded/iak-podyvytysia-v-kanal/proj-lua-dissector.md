# Власний Lua-дисектор для Wireshark

Коли вбудований пристрій передає дані через послідовний порт, радіомодуль чи сокет у власному бінарному форматі, стандартний мережевий аналізатор Wireshark не має жодної інформації про внутрішню семантику цих байтів. У вікні списку пакетів такий трафік позначається загальним тегом «Data» або «UDP Payload», а в нижній панелі інженер бачить суцільний шістнадцятковий масив.

Діагностика складних розподілених систем за сирими дампами перетворюється на виснажливу рутину: кожен байт доводиться співвідносити зі специфікацією вручну, вираховувати зміщення вказівників, переводити прямий і зворотний порядок байтів (Little-Endian / Big-Endian) та розгортати окремі біти прапорців стану на папері.

Створення кастомного дисектора (Dissector) мовою Lua перетворює Wireshark на повноцінну діагностичну станцію для конкретного вбудованого виробу. Дисектор автоматично виділяє межі кадрів, розбирає заголовок, ідентифікує тип повідомлення, будує ієрархічне дерево полів із фізичними одиницями вимірювання, перевіряє цілісність контрольних сум і маркує збійні пакети попередженнями у вікні аналізатора.

## Модель обробки пакетів та інтерфейси Wireshark Lua

Wireshark виконує код дисектора в ізольованому середовищі вбудованого інтерпретатора Lua. Для взаємодії з ядром аналізатора використовуються три базові класи об'єктів:

1. **`Proto` (Опис протоколу)**: головний вузол розширення, що реєструє ім'я протоколу, його скорочену назву для фільтрів пошуку (Display Filters) та текстовий опис у дереві шарів моделі OSI.
2. **`ProtoField` (Оголошення полів)**: типізовані структури, що описують семантику окремих фрагментів кадру. Кожне поле визначає тип даних (`uint8`, `uint16`, `uint32`, `int16`, `float`, `string`, `bytes`, `bool`), числову систему числення для відображення (десяткова, шістнадцяткова, двійкова) та бітову маску для виділення прапорців.
3. **`Tvb` (Testy Virtual Buffer)**: віртуальний буфер пам'яті, що містить сирі байти отриманого пакета. Доступ до байтів здійснюється через зрізи `tvb(offset, length)`. Зверніть увагу: на відміну від стандартних масивів мови Lua, де індексація починається з одиниці, адресація зміщень у буфері `Tvb` є 0-індексованою, відповідно до правил мови C.

## Специфікація цільового бінарного протоколу

Для практичної демонстрації розберемо бінарний протокол зв'язку бортового контролера безпілотного апарата або промислового датчика, що передає пакети через послідовний міст або UDP-сокети.

Кадр протоколу складається з фіксованого заголовка (7 байтів), поля корисного навантаження змінної довжини (від 0 до 512 байтів) та кінцевої контрольної суми CRC16:

```
+---------------+---------------+---------------+-------------------+-----------------------+---------------+
|  Преамбула    | Номер кадру   | Команда       | Довжина корисного | Корисне навантаження  | Контрольна    |
|  (0xAA 0x55)  | (Seq, uint16) | (Cmd, uint8)  | навантаження (N)  | (Payload, N байтів)   | сума (CRC16)  |
|  2 байти      | 2 байти (LE)  | 1 байт        | 2 байти (LE)      | N байтів              | 2 байти (LE)  |
+---------------+---------------+---------------+-------------------+-----------------------+---------------+
```

Семантика полів заголовка:
- **Преамбула (Magic)**: 2 байти зі значенням `0xAA 0x55` (маркер початку валідного кадру);
- **Seq (Sequence Number)**: 16-бітний лічильник пакетів у порядку Little-Endian (зростає з кожним відправленим повідомленням);
- **Cmd (Command Identifier)**: 8-бітний код типу повідомлення:
  - `0x01` — **Ping / Heartbeat**: перевірка зв'язку та передача часу безперервної роботи (Uptime, мс);
  - `0x02` — **Telemetry Report**: параметри бортового живлення (напруга, струм, температура) та бітові прапорці апаратного статусу;
  - `0x03` — **Motor Drive Command**: завдання швидкості приводів та тривалості імпульсу;
  - `0x04` — **ACK / NACK Response**: підтвердження отримання із кодом завершення;
- **Payload Length**: 16-бітне число Little-Endian, що вказує точну кількість байтів даних, які йдуть після заголовка;
- **CRC16-CCITT**: 16-бітна контрольна сума, розрахована за всіма байтами кадру, починаючи від першого байта преамбули до останнього байта корисного навантаження включно.

## Повна реалізація дисектора на Lua

Створимо файл `myproto.lua`, що містить повний логічний ланцюг обробки: від оголошення полів і таблиць назв до перевірки цілісності та динамічного склеювання фрагментів потоку.

```lua
-- myproto.lua — Дисектор бінарного протоколу вбудованої системи для Wireshark

local myproto = Proto("myproto", "Embedded Telemetry & Control Protocol")

-- ── 1. Оголошення полів протоколу (ProtoField) ──────────────────────────────
local f_magic    = ProtoField.uint16("myproto.magic",    "Преамбула (Magic)",      base.HEX)
local f_seq      = ProtoField.uint16("myproto.seq",      "Номер кадру (Seq)",      base.DEC)
local f_cmd      = ProtoField.uint8( "myproto.cmd",      "Код команди (Cmd)",      base.HEX)
local f_len      = ProtoField.uint16("myproto.len",      "Довжина навантаження",   base.DEC)
local f_payload  = ProtoField.bytes( "myproto.payload",  "Сире навантаження",      base.SPACE)
local f_crc      = ProtoField.uint16("myproto.crc",      "Контрольна сума CRC16",  base.HEX)

-- Поля телеметрії (Cmd = 0x02)
local f_telem_uptime = ProtoField.uint32("myproto.telem.uptime", "Час роботи (Uptime, мс)", base.DEC)
local f_telem_temp   = ProtoField.float( "myproto.telem.temp",   "Температура датчика (°C)", base.DEC)
local f_telem_vbat   = ProtoField.float( "myproto.telem.vbat",   "Напруга акумулятора (В)",  base.DEC)
local f_telem_curr   = ProtoField.int16( "myproto.telem.current","Струм споживання (мА)",    base.DEC)

-- Бітові прапорці стану телеметрії (16 біт, розкладаються на окремі булеві поля)
local f_flags_low_bat  = ProtoField.bool("myproto.flags.low_bat",  "Низький заряд батареї (< 3.3 В)", 16, nil, 0x0001)
local f_flags_sens_err = ProtoField.bool("myproto.flags.sens_err", "Помилка шини сенсорів (I2C/SPI)", 16, nil, 0x0002)
local f_flags_link_ok  = ProtoField.bool("myproto.flags.link_ok",  "Радіолінк синхронізовано",        16, nil, 0x0004)
local f_flags_armed    = ProtoField.bool("myproto.flags.armed",    "Силові приводи активовано",       16, nil, 0x0008)

-- Поля керування двигунами (Cmd = 0x03)
local f_motor_left  = ProtoField.int16( "myproto.motor.left",  "Швидкість лівого мотора (PWM)", base.DEC)
local f_motor_right = ProtoField.int16( "myproto.motor.right", "Швидкість правого мотора (PWM)",base.DEC)
local f_motor_dur   = ProtoField.uint16("myproto.motor.dur",   "Час утримання тяги (мс)",       base.DEC)

-- Поля підтвердження (Cmd = 0x04)
local f_ack_seq  = ProtoField.uint16("myproto.ack.seq",  "Підтверджений Seq кадру", base.DEC)
local f_ack_code = ProtoField.uint8( "myproto.ack.code", "Код статусу виконання",   base.HEX)

-- Реєстрація масиву полів у протоколі
myproto.fields = {
    f_magic, f_seq, f_cmd, f_len, f_payload, f_crc,
    f_telem_uptime, f_telem_temp, f_telem_vbat, f_telem_curr,
    f_flags_low_bat, f_flags_sens_err, f_flags_link_ok, f_flags_armed,
    f_motor_left, f_motor_right, f_motor_dur,
    f_ack_seq, f_ack_code
}

-- ── 2. Словники та експертні сповіщення (Expert Info) ───────────────────────
local CMD_NAMES = {
    [0x01] = "Ping / Heartbeat",
    [0x02] = "Telemetry Report",
    [0x03] = "Motor Drive Cmd",
    [0x04] = "ACK Response"
}

local ACK_CODES = {
    [0x00] = "OK / Success",
    [0x01] = "ERR_BAD_CRC",
    [0x02] = "ERR_UNKNOWN_CMD",
    [0x03] = "ERR_BUSY",
    [0x04] = "ERR_INVALID_PARAM"
}

local ef_crc_error = ProtoExpert.new("myproto.expert.crc_bad", "Помилка контрольної суми CRC16",
                                     expert.group.CHECKSUM, expert.severity.WARN)
local ef_too_short  = ProtoExpert.new("myproto.expert.short", "Пакет коротший за мінімальний заголовок",
                                     expert.group.MALFORMED, expert.severity.ERROR)

myproto.experts = { ef_crc_error, ef_too_short }

-- ── 3. Табличний розрахунок CRC16-CCITT ────────────────────────────────────
local function calc_crc16(tvb, offset, length)
    local crc = 0xFFFF
    for i = 0, length - 1 do
        local byte = tvb(offset + i, 1):uint()
        crc = bit.bxor(crc, bit.lshift(byte, 8))
        for _ = 1, 8 do
            if bit.band(crc, 0x8000) ~= 0 then
                crc = bit.bxor(bit.lshift(crc, 1), 0x1021)
            else
                crc = bit.lshift(crc, 1)
            end
            crc = bit.band(crc, 0xFFFF)
        end
    end
    return crc
end

-- ── 4. Головна функція дисекції ─────────────────────────────────────────────
function myproto.dissector(buffer, pinfo, tree)
    local buf_len = buffer:len()
    local HEADER_SIZE = 7  -- 2 (Magic) + 2 (Seq) + 1 (Cmd) + 2 (Len)
    local CRC_SIZE = 2

    -- Захист від занадто коротких фрагментів
    if buf_len < (HEADER_SIZE + CRC_SIZE) then
        return
    end

    -- Перевірка преамбули 0xAA 0x55 (Big-Endian у байтах)
    local magic = buffer(0, 2):uint()
    if magic ~= 0xAA55 and magic ~= 0x55AA then
        return -- Преамбула не збігається, передаємо пакет іншим дисекторам
    end

    -- Вичитування довжини корисного навантаження (Little-Endian)
    local payload_len = buffer(5, 2):le_uint()
    local total_packet_len = HEADER_SIZE + payload_len + CRC_SIZE

    -- Якщо пакет у TCP-потоці прийшов не повністю, сигналізуємо механізму десегментації
    if buf_len < total_packet_len then
        pinfo.desegment_len = total_packet_len - buf_len
        pinfo.desegment_offset = 0
        return
    end

    -- Оновлення глобальних колонок списку пакетів Wireshark
    pinfo.cols.protocol:set("MyProto")

    local seq = buffer(2, 2):le_uint()
    local cmd = buffer(4, 1):uint()
    local cmd_str = CMD_NAMES[cmd] or string.format("Unknown (0x%02X)", cmd)

    pinfo.cols.info:set(string.format("[%s] Seq=%d, PayloadLen=%d", cmd_str, seq, payload_len))

    -- Створення кореневого дерева протоколу
    local root_tree = tree:add(myproto, buffer(0, total_packet_len),
                               string.format("MyProto: %s (Seq: %d, Len: %d)", cmd_str, seq, payload_len))

    -- Розділ заголовка
    local hdr_tree = root_tree:add(myproto, buffer(0, HEADER_SIZE), "Заголовок кадру (Header)")
    hdr_tree:add(f_magic, buffer(0, 2))
    hdr_tree:add_le(f_seq, buffer(2, 2))
    hdr_tree:add(f_cmd, buffer(4, 1)):append_text(string.format(" (%s)", cmd_str))
    hdr_tree:add_le(f_len, buffer(5, 2))

    -- Розбір корисного навантаження залежно від типу команди
    if payload_len > 0 then
        local pld_tvb = buffer(HEADER_SIZE, payload_len)
        local pld_tree = root_tree:add(f_payload, pld_tvb)
        pld_tree:set_text(string.format("Корисне навантаження (%s, %d байтів)", cmd_str, payload_len))

        if cmd == 0x01 and payload_len >= 4 then
            -- Розбір Heartbeat
            pld_tree:add_le(f_telem_uptime, pld_tvb(0, 4))

        elseif cmd == 0x02 and payload_len >= 10 then
            -- Розбір Telemetry Report
            local raw_uptime = pld_tvb(0, 4):le_uint()
            local raw_temp   = pld_tvb(4, 2):le_int()
            local raw_vbat   = pld_tvb(6, 2):le_uint()
            local raw_curr   = pld_tvb(8, 2):le_int()

            pld_tree:add_le(f_telem_uptime, pld_tvb(0, 4))
            pld_tree:add(f_telem_temp, pld_tvb(4, 2), raw_temp / 100.0)
            pld_tree:add(f_telem_vbat, pld_tvb(6, 2), raw_vbat / 1000.0)
            pld_tree:add_le(f_telem_curr, pld_tvb(8, 2))

            if payload_len >= 12 then
                local flags_tree = pld_tree:add(myproto, pld_tvb(10, 2), "Прапорці стану пристрою (Bitmask)")
                flags_tree:add_le(f_flags_low_bat,  pld_tvb(10, 2))
                flags_tree:add_le(f_flags_sens_err, pld_tvb(10, 2))
                flags_tree:add_le(f_flags_link_ok,  pld_tvb(10, 2))
                flags_tree:add_le(f_flags_armed,    pld_tvb(10, 2))
            end

        elseif cmd == 0x03 and payload_len >= 6 then
            -- Розбір Motor Drive Command
            pld_tree:add_le(f_motor_left,  pld_tvb(0, 2))
            pld_tree:add_le(f_motor_right, pld_tvb(2, 2))
            pld_tree:add_le(f_motor_dur,   pld_tvb(4, 2))

        elseif cmd == 0x04 and payload_len >= 3 then
            -- Розбір ACK / Response
            local ack_seq  = pld_tvb(0, 2):le_uint()
            local ack_code = pld_tvb(2, 1):uint()
            local code_str = ACK_CODES[ack_code] or string.format("Unknown (0x%02X)", ack_code)

            pld_tree:add_le(f_ack_seq, pld_tvb(0, 2))
            pld_tree:add(f_ack_code, pld_tvb(2, 1)):append_text(string.format(" (%s)", code_str))
        end
    end

    -- Верифікація контрольної суми
    local crc_offset = HEADER_SIZE + payload_len
    local received_crc = buffer(crc_offset, 2):le_uint()
    local calculated_crc = calc_crc16(buffer, 0, crc_offset)

    local crc_item = root_tree:add_le(f_crc, buffer(crc_offset, 2))
    if received_crc == calculated_crc then
        crc_item:append_text(" [OK: Збігається]")
    else
        crc_item:append_text(string.format(" [ПОМИЛКА: обчислено 0x%04X, отримано 0x%04X]",
                                           calculated_crc, received_crc))
        root_tree:add_expert_info(ef_crc_error)
    end
end

-- ── 5. Реєстрація дисектора ────────────────────────────────────────────────
-- Реєстрація за фіксованими портами UDP
local udp_table = DissectorTable.get("udp.port")
udp_table:add(8888, myproto)
udp_table:add(9999, myproto)

-- Евристична реєстрація для аналізу дампів із довільних джерел
myproto:register_heuristic("udp", function(buffer, pinfo, tree)
    if buffer:len() >= 9 and buffer(0, 2):uint() == 0xAA55 then
        myproto.dissector(buffer, pinfo, tree)
        return true
    end
    return false
end)
```

## Механізм десегментації та обробки потокових з'єднань

Коли протокол працює через TCP-сокет або через безперервний потік UART, межі переданих блоків даних на транспортному рівні не збігаються з межами логічних пакетів застосунку. В один TCP-сегмент може потрапити півтора пакета, або навпаки — один великий пакет виявиться розбитим на кілька дрібних фрагментів (TCP Segmentation).

Для вирішення цієї проблеми Wireshark надає механізм `pinfo.desegment_len` та `pinfo.desegment_offset`. 

Коли дисектор зчитує 7 байтів заголовка і з'ясовує, що повний пакет має містити 100 байтів, але поточний буфер `Tvb` містить лише 40 байтів, він виконує такі кроки:
1. Встановлює `pinfo.desegment_offset = 0`, повідомляючи рушій, що поточний кадр починається з нульового зміщення;
2. Встановлює `pinfo.desegment_len = 60`, вказуючи ядру Wireshark, скільки саме байтів бракує до повного завершення кадру;
3. Завершує виконання функції без створення дерева розбору.

Отримавши таку відповідь, Wireshark призупиняє розбір даного пакета, очікує надходження наступного TCP-сегмента з цього сокета, склеює байти в єдиний буфер і викликає функцію дисекції повторно вже для повного, зібраного кадру.

## Встановлення та гаряче перезавантаження

1. **Копіювання у теку плагінів**:
   - У середовищі Windows файл зберігають за адресою `%APPDATA%\Wireshark\plugins\myproto.lua` (наприклад, `C:\Users\<Ім'я>\AppData\Roaming\Wireshark\plugins\`);
   - У середовищі Linux/macOS — у теці `~/.local/lib/wireshark/plugins/myproto.lua` або `~/.config/wireshark/plugins/myproto.lua`.

2. **Перезавантаження без перезапуску**:
   Під час налагодження самого Lua-скрипту немає потреби закривати й знову відкривати Wireshark. Комбінація клавіш `Ctrl + Shift + L` (у macOS `Cmd + Shift + L`) ініціює перезавантаження всіх плагінів і миттєво перемальовує відкритий дамп з урахуванням внесених правок.

3. **Практична фільтрація у вікні пошуку**:
   Після завантаження дисектора користувач отримує повний доступ до фільтрів Wireshark:
   - `myproto.cmd == 0x02 and myproto.telem.vbat < 3.4` — ізолювати телеметрію з критичним розрядом живлення;
   - `myproto.flags.sens_err == 1` — знайти моменти відмови шин опитування сенсорів;
   - `myproto.expert.crc_bad` — відфільтрувати виключно ті кадри, де дані були пошкоджені завадами в каналі зв'язку;
   - `myproto.seq > 1000 and myproto.motor.left > 500` — знайти епізоди інтенсивного маневрування на пізніх етапах тестування.

Завдяки цьому аналіз багатогігабайтних записів випробувань скорочується з годин ручного перегляду шістнадцяткових таблиць до створення одного лаконічного виразу у вікні дисплейного фільтра.
