# -*- coding: utf-8 -*-
"""Фігури до теми «Protocol Buffers і схемні формати».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

RED_BG   = "#fdecea"   # небезпека / старий читач / wire-type
BLUE_BG  = "#eaf0fd"   # корисне навантаження / зміщення
GREEN_BG = "#eaf6ee"   # успіх / сумісність / vtable
GRAY_BG  = "#e9ecef"   # набивка / незнайомі теги
AMBER    = "#b8860b"
AMBER_BG = "#fdf6e3"
PURPLE_BG = "#f3e8fd"
MONO     = "Consolas, 'DejaVu Sans Mono', monospace"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


def cell(x, y, w, h, s, bg=FILL, stroke=LINE, color=INK, size=13, bold=False, sw=1.5):
    return (rect(x, y, w, h, fill=bg, stroke=stroke, sw=sw, rx=4) +
            ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
             'text-anchor="middle"%s>%s</text>'
             % (x + w / 2, y + h / 2 + size * 0.35, MONO, size, color,
                ' font-weight="700"' if bold else '', esc(s))))


# ════════════ 1. Varint і структура тега полів ═════════════════════════════════
def fig_varint_and_wire():
    W, H = 900, 520
    f = []
    f.append(text(W / 2, 28, "Фізичний рівень Protobuf: структура Varint і тега поля", size=16, bold=True))
    f.append(text(W / 2, 48, "Кодування цілих змінною довжиною (Base-128) та зшивання номера поля з wire type", size=12, color=MUTED))

    # ── Блок 1: Анатомія Varint ──
    y = 80
    f.append(text(40, y, "1 · Анатомія Varint: число 300 (0x012C = 0b00000001_00101100)", size=13, color=INK, anchor="start", bold=True))
    
    bw = 36
    # Байт 0
    x0 = 60
    f.append(text(x0 + 4 * (bw + 2), y + 22, "Байт 0 (молодша 7-бітна група)", size=11, color=MUTED))
    bits0 = [("1", POS), ("0", INK), ("1", INK), ("0", INK), ("1", INK), ("1", INK), ("0", INK), ("0", INK)]
    for i, (b, col) in enumerate(bits0):
        bg = RED_BG if i == 0 else BLUE_BG
        f.append(cell(x0 + i * (bw + 2), y + 36, bw, 32, b, bg=bg, color=col, bold=(i == 0), size=12))
    f.append(text(x0 + bw / 2, y + 84, "MSB=1 (далі)", size=10, color=POS))
    f.append(text(x0 + 4.5 * (bw + 2), y + 84, "7 бітів корисних: 0101100 (0x2C)", size=10, color=NEG))

    # Байт 1
    x1 = 480
    f.append(text(x1 + 4 * (bw + 2), y + 22, "Байт 1 (старша група, термінальний)", size=11, color=MUTED))
    bits1 = [("0", FIELD), ("0", INK), ("0", INK), ("0", INK), ("0", INK), ("0", INK), ("1", INK), ("0", INK)]
    for i, (b, col) in enumerate(bits1):
        bg = GREEN_BG if i == 0 else BLUE_BG
        f.append(cell(x1 + i * (bw + 2), y + 36, bw, 32, b, bg=bg, color=col, bold=(i == 0), size=12))
    f.append(text(x1 + bw / 2, y + 84, "MSB=0 (стоп)", size=10, color=FIELD))
    f.append(text(x1 + 4.5 * (bw + 2), y + 84, "7 бітів корисних: 0000010 (0x02)", size=10, color=NEG))

    # ── Блок 2: Тег поля (Key = field_number << 3 | wire_type) ──
    y = 205
    f.append(text(40, y, "2 · Структура ключа (Key): поле №2, тип LEN (wire type 2) → (2 << 3) | 2 = 18 (0x12)", size=13, color=INK, anchor="start", bold=True))
    
    x_tag = 60
    # 8 бітів числа 18 = 00010010
    tag_bits = [("0", MUTED), ("0", MUTED), ("0", FIELD), ("1", FIELD), ("0", FIELD),
                ("0", POS), ("1", POS), ("0", POS)]
    for i, (b, col) in enumerate(tag_bits):
        bg = GREEN_BG if i < 5 else RED_BG
        f.append(cell(x_tag + i * (bw + 2), y + 20, bw, 32, b, bg=bg, color=col, bold=True, size=12))
    
    f.append(text(x_tag + 2.5 * (bw + 2), y + 68, "Номер поля: 2 (біти 7..3)", size=11, color=FIELD, bold=True))
    f.append(text(x_tag + 6.5 * (bw + 2), y + 68, "Wire type: 2 (біти 2..0)", size=11, color=POS, bold=True))

    # ── Блок 3: Wire Types таблиця ──
    y = 310
    f.append(text(40, y, "3 · Основні типи на дроті (Wire Types)", size=13, color=INK, anchor="start", bold=True))
    
    wt = [
        ("0", "VARINT", "int32, int64, uint32, sint32, bool, enum", "Змінна довжина (1–10 Б)", AMBER_BG, AMBER),
        ("1", "I64", "fixed64, sfixed64, double", "Фіксовано 8 байтів (little-endian)", BLUE_BG, NEG),
        ("2", "LEN", "string, bytes, вкладені повідомлення, packed repeated", "Varint довжина L + L байтів", GREEN_BG, FIELD),
        ("5", "I32", "fixed32, sfixed32, float", "Фіксовано 4 байти (little-endian)", PURPLE_BG, "#6b21a8")
    ]
    
    row_y = y + 16
    for code, name, types_str, desc, bg, col in wt:
        f.append(cell(60, row_y, 32, 22, code, bg=bg, color=col, bold=True, size=11))
        f.append(mono(105, row_y + 16, name, size=12, bold=True))
        f.append(text(200, row_y + 16, types_str, size=11, color=INK, anchor="start"))
        f.append(text(620, row_y + 16, desc, size=11, color=MUTED, anchor="start"))
        row_y += 26

    f.append(fitbox(40, 445, W - 80, 52,
                    ["Поля з номерами 1..15 укладають тег у 1 байт ((15 << 3) | 7 = 127). Номери 16..2047 потребують 2 байти.",
                     "Правило: найчастіші поля телеметрії отримують номери 1..15 для максимальної щільності потоку."],
                    size=11, fill=AMBER_BG, stroke=AMBER, color=INK))

    out("varint-and-wire-types.svg", W, H, *f)


# ════════════ 2. ZigZag кодування для знакових чисел ═══════════════════════════
def fig_zigzag():
    W, H = 900, 480
    f = []
    f.append(text(W / 2, 28, "ZigZag кодування: усунення 10-байтового розширення від'ємних чисел", size=16, bold=True))
    f.append(text(W / 2, 48, "Відображення знакових чисел на беззнакові цілі: (n << 1) ^ (n >> 31)", size=12, color=MUTED))

    # ── Проблема two's complement ──
    y = 80
    f.append(text(40, y, "Проблема: -1 у додатковому коді (Two's Complement) та звичайний Varint", size=13, color=POS, anchor="start", bold=True))
    f.append(mono(60, y + 24, "int32 -1 = 0xFFFFFFFF  →  розширення до 64 біт  →  10 байтів у потоці:", size=12))
    
    bw = 72
    x0 = 60
    for i, b in enumerate(["FF", "FF", "FF", "FF", "FF", "FF", "FF", "FF", "FF", "01"]):
        f.append(cell(x0 + i * (bw + 6), y + 36, bw, 28, b, bg=RED_BG, color=POS, bold=True, size=11))
    f.append(text(W / 2, y + 80, "Кожне від'ємне число без ZigZag роздувається до 10 байтів (катастрофа для каналу)", size=11, color=POS))

    # ── Вісь ZigZag ──
    y = 200
    f.append(text(40, y, "Розв'язок ZigZag: малі за модулем числа стають малими додатними", size=13, color=FIELD, anchor="start", bold=True))

    pairs = [
        ("0", "0", "1 байт (0x00)"),
        ("−1", "1", "1 байт (0x01)"),
        ("1", "2", "1 байт (0x02)"),
        ("−2", "3", "1 байт (0x03)"),
        ("2", "4", "1 байт (0x04)"),
        ("−3", "5", "1 байт (0x05)"),
        ("2147483647", "4294967294", "5 байтів"),
        ("−2147483648", "4294967295", "5 байтів")
    ]

    card_w = 96
    card_h = 76
    x_start = 50
    for i, (orig, enc, sz) in enumerate(pairs[:6]):
        xc = x_start + i * (card_w + 10)
        bg = BLUE_BG if orig.startswith("−") else FILL
        col = NEG if orig.startswith("−") else INK
        f.append(rect(xc, y + 16, card_w, card_h, fill=bg, stroke=LINE, sw=1.2, rx=4))
        f.append(text(xc + card_w / 2, y + 36, orig, size=13, color=col, bold=True))
        f.append(text(xc + card_w / 2, y + 54, "↓ zigzag", size=10, color=MUTED))
        f.append(text(xc + card_w / 2, y + 72, enc, size=13, color=FIELD, bold=True))
        f.append(text(xc + card_w / 2, y + 104, sz, size=10, color=MUTED))

    # ── Формули ──
    y = 345
    f.append(fitbox(40, y, W - 80, 110,
                    ["Кодування sint32:  z = (n << 1) ^ (n >> 31)   [арифметичний зсув вправо копіює знаковий біт у всі позиції]",
                     "Розкодування sint32: n = (z >> 1) ^ -(z & 1)    [молодший біт визначає від'ємність та розгортає маску]",
                     "Результат: -1 перетворюється на 1 (один байт 0x01 на дроті замість десяти байтів 0xFF...01)."],
                    size=12, fill=GREEN_BG, stroke=FIELD, color=INK, bold=False))

    out("zigzag-number-line.svg", W, H, *f)


# ════════════ 3. Схемна еволюція та правила сумісності ═════════════════════════
def fig_schema_evolution():
    W, H = 900, 520
    f = []
    f.append(text(W / 2, 28, "Схемна еволюція: пряма і зворотна сумісність у часі", size=16, bold=True))
    f.append(text(W / 2, 48, "Як старі та нові вузли обмінюються даними без збоїв і без втрати пам'яті", size=12, color=MUTED))

    box_w = 380
    box_h = 160

    # ── Лівий блок: Пряма сумісність (Forward) ──
    f.append(rect(50, 75, box_w, box_h, fill=FILL, stroke=FIELD, sw=2, rx=6))
    f.append(text(50 + box_w / 2, 98, "Пряма сумісність (Forward Compatibility)", size=13, color=FIELD, bold=True))
    f.append(text(50 + box_w / 2, 118, "Старий читач (v1) ← Новий відправник (v2)", size=11, color=MUTED))
    f.append(text(70, 142, "• Новий вузол надсилає додаткове поле (тег 3).", size=11, color=INK, anchor="start"))
    f.append(text(70, 162, "• Старий вузол бачить незнайомий тег 3 і wire type.", size=11, color=INK, anchor="start"))
    f.append(text(70, 182, "• Читач пропускає поле за правилами wire type.", size=11, color=INK, anchor="start"))
    f.append(text(70, 202, "• Поля 1 і 2 прочитано успішно; збою немає.", size=11, color=FIELD, anchor="start", bold=True))

    # ── Правий блок: Зворотна сумісність (Backward) ──
    f.append(rect(470, 75, box_w, box_h, fill=FILL, stroke=NEG, sw=2, rx=6))
    f.append(text(470 + box_w / 2, 98, "Зворотна сумісність (Backward Compatibility)", size=13, color=NEG, bold=True))
    f.append(text(470 + box_w / 2, 118, "Новий читач (v2) ← Старий відправник (v1)", size=11, color=MUTED))
    f.append(text(490, 142, "• Старий вузол надсилає лише поля 1 і 2.", size=11, color=INK, anchor="start"))
    f.append(text(490, 162, "• У схемі v2 є поле 3, але в потоці воно відсутнє.", size=11, color=INK, anchor="start"))
    f.append(text(490, 182, "• Читач підставляє значення за замовчуванням (0/empty).", size=11, color=INK, anchor="start"))
    f.append(text(490, 202, "• Відсутність 'required' у proto3 рятує парсер.", size=11, color=NEG, anchor="start", bold=True))

    # ── Несумісні зміни (Критичні помилки) ──
    y = 255
    f.append(text(40, y, "Критичні порушення: що ламає сумісність назавжди", size=13, color=POS, anchor="start", bold=True))

    hazards = [
        ("Зміна номера поля", "Поле перейменовано з тега 2 на тег 4 → старі вузли не побачать значення взагалі."),
        ("Повторне використання тега", "Видалили поле 3 (int32) і призначили тег 3 для string url → старі вузли розберуть байти як сміття."),
        ("Зміна wire type", "Перехід з int32 (wire 0) на fixed32 (wire 5) або string (wire 2) призводить до синтаксичної помилки розбору.")
    ]

    for i, (title, desc) in enumerate(hazards):
        hy = y + 16 + i * 36
        f.append(cell(50, hy, 210, 28, title, bg=RED_BG, color=POS, bold=True, size=11))
        f.append(text(275, hy + 18, desc, size=11, color=INK, anchor="start"))

    # ── Reserved ──
    y = 405
    f.append(fitbox(40, y, W - 80, 85,
                    ["Захист від повторного використання: директива reserved у .proto-файлі",
                     "reserved 3, 7 to 10;          // забороняє компілятору призначати ці номери новим полям",
                     "reserved \"old_humidity\";       // забороняє використання старого імені поля у JSON-відображеннях",
                     "Правило: видалене поле назавжди резервується і ніколи не передається іншим типам даних."],
                    size=11, fill=AMBER_BG, stroke=AMBER, color=INK, bold=False))

    out("schema-evolution-rules.svg", W, H, *f)


# ════════════ 4. Декодування в C-структури проти In-Place доступу ═══════════════
def fig_decode_vs_inplace():
    W, H = 900, 520
    f = []
    f.append(text(W / 2, 28, "Дві парадигми: декодування у структури проти прямого доступу", size=16, bold=True))
    f.append(text(W / 2, 48, "NanoPB / Protobuf (Parse & Copy) проти FlatBuffers / Cap'n Proto (Zero-Copy In-Place)", size=12, color=MUTED))

    # ── Ліва колонка: Parse & Copy (NanoPB) ──
    LX = 230
    f.append(text(LX, 85, "NanoPB / Protobuf (Parse & Copy)", size=14, color=POS, bold=True))
    
    # Буфер на дроті
    f.append(rect(40, 105, 380, 40, fill=AMBER_BG, stroke=AMBER, sw=1.5, rx=4))
    f.append(text(40 + 190, 128, "Вхідний байтовий буфер (RX DMA / UART)", size=11, color=INK))
    
    # Стрілка вниз через парсер
    f.append(arrow(LX, 145, LX, 185, color=POS))
    f.append(rect(LX - 110, 185, 220, 36, fill=RED_BG, stroke=POS, sw=1.5, rx=4))
    f.append(text(LX, 206, "Парсер: varint-цикл + копіювання", size=11, color=POS, bold=True))
    
    # Виділена C-структура в RAM
    f.append(arrow(LX, 221, LX, 255, color=POS))
    f.append(rect(40, 255, 380, 80, fill=FILL, stroke=LINE, sw=1.5, rx=4))
    f.append(text(40 + 190, 275, "Окрема C-структура в RAM (sizeof = 24 Б)", size=11, color=INK, bold=True))
    f.append(mono(55, 300, "uint32_t ts; float temp; uint8_t status;", size=11))
    f.append(text(40 + 190, 322, "Вимагає подвійної пам'яті (буфер + структура) і такти CPU", size=10, color=POS))

    # ── Права колонка: Zero-Copy In-Place (FlatBuffers) ──
    RX = 670
    f.append(text(RX, 85, "FlatBuffers / Cap'n Proto (Zero-Copy)", size=14, color=FIELD, bold=True))

    # Буфер на дроті
    f.append(rect(480, 105, 380, 40, fill=AMBER_BG, stroke=AMBER, sw=1.5, rx=4))
    f.append(text(480 + 190, 128, "Вхідний байтовий буфер (RX DMA / Flash)", size=11, color=INK))

    # Пряма стрілка доступу
    f.append(arrow(RX, 145, RX, 255, color=FIELD, sw=2.5))
    f.append(text(RX + 80, 195, "Зсув за vtable: O(1)", size=11, color=FIELD, bold=True))
    f.append(text(RX + 80, 215, "0 тактів розбору", size=10, color=MUTED))

    # Пряме читання
    f.append(rect(480, 255, 380, 80, fill=GREEN_BG, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(480 + 190, 275, "Прямий доступ: msg->temperature()", size=11, color=FIELD, bold=True))
    f.append(mono(495, 300, "const float *p = (const float*)(buf + off);", size=11))
    f.append(text(480 + 190, 322, "0 байтів додаткової RAM, читання прямо з буфера", size=10, color=FIELD))

    # ── Порівняльна плашка ──
    y = 360
    f.append(fitbox(40, y, W - 80, 130,
                    ["Критерій порівняння              | NanoPB (Protobuf)               | FlatBuffers (Zero-Copy)",
                     "---------------------------------|---------------------------------|---------------------------------",
                     "Додаткова RAM для читання        | Розмір C-структури (20..200 Б)  | 0 байтів (читання на місці)",
                     "Час доступу до 1 поля            | Повний розбір усього пакета     | O(1) за індексом у vtable",
                     "Розмір на дроті (Wire size)      | Мінімальний (varint-пакування)  | На 20..50% більший (вирівнювання)",
                     "Придатність для Flash/ROM прямо  | Ні (потрібна десеріалізація)    | Так (читання прямо з адрес Flash)"],
                    size=11, fill=FILL, stroke=LINE, color=INK, bold=False))

    out("decode-vs-inplace.svg", W, H, *f)


# ════════════ 5. Внутрішня структура FlatBuffers та vtable ═════════════════════
def fig_flatbuffers_vtable():
    W, H = 900, 520
    f = []
    f.append(text(W / 2, 28, "Внутрішня будова FlatBuffers: зв'язок vtable і Table", size=16, bold=True))
    f.append(text(W / 2, 48, "Зворотне зміщення до vtable, карта полів та зміщення непрямого доступу", size=12, color=MUTED))

    # ── vtable блок ──
    vx = 60
    vy = 85
    f.append(text(vx + 160, vy, "vtable (Таблиця віртуальних зсувів)", size=13, color=FIELD, bold=True))
    
    v_cells = [
        ("vtable_size = 8", "2 Б", GREEN_BG),
        ("object_size = 12", "2 Б", GREEN_BG),
        ("offset(поле 0: id) = 4", "2 Б", BLUE_BG),
        ("offset(поле 1: temp) = 8", "2 Б", BLUE_BG)
    ]
    for i, (lab, sz, bg) in enumerate(v_cells):
        cy = vy + 18 + i * 34
        f.append(rect(vx, cy, 260, 30, fill=bg, stroke=LINE, sw=1.2, rx=3))
        f.append(text(vx + 130, cy + 19, lab, size=11, color=INK, bold=True))
        f.append(text(vx + 290, cy + 19, sz, size=10, color=MUTED, anchor="start"))

    # ── Table Data блок ──
    tx = 480
    ty = 85
    f.append(text(tx + 160, ty, "Table Data (Тіло об'єкта в буфері)", size=13, color=NEG, bold=True))

    t_cells = [
        ("vtable_offset = -20", "4 Б (відносний зсув назад)", RED_BG),
        ("id = 42", "4 Б (uint32_t за зміщенням +4)", BLUE_BG),
        ("temp = 23.5", "4 Б (float за зміщенням +8)", BLUE_BG)
    ]
    for i, (lab, sz, bg) in enumerate(t_cells):
        cy = ty + 18 + i * 40
        f.append(rect(tx, cy, 280, 34, fill=bg, stroke=LINE, sw=1.2, rx=3))
        f.append(text(tx + 140, cy + 21, lab, size=11, color=INK, bold=True))
        f.append(text(tx + 310, cy + 21, sz, size=10, color=MUTED, anchor="start"))

    # ── Стрілка від vtable_offset назад до vtable ──
    f.append(arrow(tx, ty + 35, vx + 260, vy + 35, color=POS, sw=2))
    f.append(text((tx + vx + 260) / 2, ty + 22, "зсув назад до vtable (-20 байтів)", size=10, color=POS, bold=True))

    # ── Стрілка від vtable field offset до даних поля ──
    f.append(arrow(vx + 260, vy + 120, tx, ty + 115, color=NEG, sw=2))
    f.append(text((tx + vx + 260) / 2, vy + 135, "vtable каже: temp лежить за зсувом +8", size=10, color=NEG, bold=True))

    # ── Механіка відсутніх полів та значень за замовчуванням ──
    y = 270
    f.append(fitbox(50, y, W - 100, 100,
                    ["Як обробляються поля за замовчуванням і нові поля:",
                     "1. Якщо поле дорівнює значенню за замовчуванням, FlatBufferBuilder записує offset = 0 у vtable.",
                     "2. Поле НЕ займає жодного байта в Table Data (економія пам'яті).",
                     "3. Якщо читач звертається до нового поля, якого немає у старій vtable (номер > vtable_size),",
                     "   генерований код миттєво повертає дефолтне значення без звернення до пам'яті."],
                    size=11, fill=AMBER_BG, stroke=AMBER, color=INK, bold=False))

    # ── Корінь буфера ──
    y = 395
    f.append(fitbox(50, y, W - 100, 95,
                    ["Розкладка буфера FlatBuffers у пам'яті (будується з кінця до початку):",
                     "[Зсув до кореня: 4 Б] → [Вектори / Рядки] → [vtable: 8 Б] → [Table Data: 12 Б (Корінь)]",
                     "Перші 4 байти буфера завжди містять uoffset_t (зсув до головного кореневого об'єкта).",
                     "Перевірка цілісності виконується класом flatbuffers::Verifier (захист від зациклень і виходу за межі)."],
                    size=11, fill=FILL, stroke=LINE, color=INK, bold=False))

    out("flatbuffers-vtable-layout.svg", W, H, *f)


if __name__ == "__main__":
    fig_varint_and_wire()
    fig_zigzag()
    fig_schema_evolution()
    fig_decode_vs_inplace()
    fig_flatbuffers_vtable()
    print("OK: figures written to", IMG)
