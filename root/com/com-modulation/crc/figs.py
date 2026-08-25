# -*- coding: utf-8 -*-
"""Фігури до теми «CRC» (book/communications/coding-theory/crc).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. CRC як ділення в стовпчик над GF(2): віднімання — це XOR ────────────────
# Ідея, яку важко передати словами: CRC — це звичайне ділення «в стовпчик», де на
# кожному кроці замість «відняти дільник» роблять XOR, а остача коротша за дільник
# і є контрольним кодом. Показуємо повне трасування на даних 1101 з поліномом 1011.
def fig_division():
    W, H = 760, 540
    f = []
    f.append(text(W / 2, 30, "CRC: дані ділимо «в стовпчик» на поліном, остача — і є контроль",
                  16, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "ділення двійкове, але без позик: віднімання — це XOR",
                  12.5, MUTED, "middle", italic=True))

    # дільник
    f.append(text(W / 2, 82, "дільник (поліном): x³ + x + 1  →  1011", 14, FIELD, "middle", bold=True))

    # розкладка біт-стовпчиків
    x0 = 250
    step = 26

    def bits(y, s, color_map=None, color=INK, bold=True):
        for i, ch in enumerate(s):
            c = color
            if color_map == "ud":            # дані/остача: 1 червоне, 0 синє
                c = POS if ch == "1" else NEG
            elif color_map == "g":           # дільник — зелений
                c = FIELD
            f.append(text(x0 + i * step, y, ch, 17, c, "middle", bold=bold))

    def note(y, s):
        f.append(text(x0 + 12 * step, y, s, 12, MUTED, "start", italic=True))

    def bar(y, n0, n1):
        f.append(line(x0 + n0 * step - 10, y, x0 + n1 * step + 10, y, color=MUTED, sw=1.3))

    y = 122
    bits(y, "1101000", "ud");                         note(y, "дані 1101 + 3 нулі (ширина CRC)")
    y = 152
    bits(y, "1011", "g");                             note(y, "XOR (старший біт = 1)")
    bar(160, 0, 3)
    y = 182
    bits(y, "0110000", "ud")
    y = 212
    f.append(text(x0 + step, y, "1", 17, FIELD, "middle", bold=True))
    f.append(text(x0 + 2 * step, y, "0", 17, FIELD, "middle", bold=True))
    f.append(text(x0 + 3 * step, y, "1", 17, FIELD, "middle", bold=True))
    f.append(text(x0 + 4 * step, y, "1", 17, FIELD, "middle", bold=True))
    note(y, "XOR")
    bar(220, 1, 4)
    y = 242
    bits(y, "0011000", "ud")
    y = 272
    for i, ch in enumerate("1011"):
        f.append(text(x0 + (i + 2) * step, y, ch, 17, FIELD, "middle", bold=True))
    note(y, "XOR")
    bar(280, 2, 5)
    y = 302
    bits(y, "0000100", "ud")
    note(y, "старші біти вже 0")

    y = 340
    f.append(text(x0, y, "остача (CRC) = 100", 16, FIELD, "start", bold=True))
    f.append(text(x0 + 9 * step, y, "← її дописують замість нулів", 12.5, MUTED, "start", italic=True))

    # блок перевірки на приймачі
    f.append(line(40, 372, W - 40, 372, color="#e5e7eb", sw=1))
    f.append(text(60, 400, "Приймач ділить ВЕСЬ блок (дані + CRC) на той самий поліном:",
                  13.5, INK, "start", bold=True))
    f.append(fitbox(80, 416, 300, 34, "остача 0  →  помилки немає",
                    size=13, fill="#eef6ef", stroke=FIELD, color=INK))
    f.append(fitbox(400, 416, 300, 34, "остача ≠ 0  →  блок битий",
                    size=13, fill="#fdecea", stroke=POS, color=INK))
    f.append(text(W / 2, 480, "Йому навіть не треба окремо звіряти CRC — нульова остача вже підтверджує цілість.",
                  12.5, MUTED, "middle", italic=True))
    f.append(text(W / 2, 506, "Те саме ділення апаратно робить один зсувний регістр зі зворотним XOR — біт за такт.",
                  12.5, MUTED, "middle", italic=True))

    render(os.path.join(IMG, "division-xor.svg"), W, H, *f)


# ── 2. Залізо CRC: зсувний регістр зі зворотними XOR (LFSR) ───────────────────
# Ідея: те саме ділення лягає на кілька тригерів і вентилів XOR — «крани» стоять
# там, де в поліномі одиниці; біти вливаються по одному, біт за такт.
def fig_lfsr():
    W, H = 760, 360
    f = []
    f.append(text(W / 2, 30, "Залізо CRC: зсувний регістр зі зворотним XOR за одиницями полінома",
                  15.5, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "XOR-«крани» стоять там, де в поліномі одиниці; біти даних вливаються по одному",
                  12.5, MUTED, "middle", italic=True))

    # три тригери
    cells = [("D0", 250), ("D1", 400), ("D2", 550)]
    cy = 175
    for name, cx in cells:
        f.append(rect(cx - 45, cy - 28, 90, 56, fill=BG, stroke=INK, sw=2))
        f.append(text(cx, cy + 6, name, 18, INK, "middle", bold=True))

    # стрілки між тригерами
    f.append(arrow(295, cy, 355, cy, color=INK, sw=2))
    f.append(arrow(445, cy, 505, cy, color=INK, sw=2))

    # вхід даних
    f.append(arrow(120, cy, 205, cy, color=FIELD, sw=2.2))
    f.append(text(120, cy - 14, "біти даних →", 12.5, FIELD, "start", bold=True))

    # зворотний звязок (контур з виходу назад)
    f.append(line(595, cy, 650, cy, color=INK, sw=2))
    f.append(line(650, cy, 650, 270, color=INK, sw=2))
    f.append(line(650, 270, 120, 270, color=INK, sw=2))
    f.append(line(120, 270, 120, cy, color=INK, sw=2))

    # XOR-кран
    f.append(circle(370, cy, 13, fill=BG, stroke=POS, sw=2))
    f.append(text(370, cy + 6, "⊕", 16, POS, "middle", bold=True))
    f.append(line(370, 270, 370, cy + 13, color=POS, sw=1.8, dash="4 3"))
    f.append(text(382, 262, "кран на місці одиниці полінома", 11.5, POS, "start"))

    f.append(text(W / 2, 320, "Щотакту: зсув + XOR у «кранах». Після останнього біта в регістрі лежить готова CRC.",
                  12.5, INK, "middle", italic=True))
    f.append(text(W / 2, 340, "Уся схема — кілька тригерів і вентилів XOR, тож рахує біт за такт майже задарма.",
                  12, MUTED, "middle", italic=True))

    render(os.path.join(IMG, "lfsr-hardware.svg"), W, H, *f)


# ── 3. Карта застосувань CRC ──────────────────────────────────────────────────
# Ідея: один і той самий прийом стоїть у кожному надійному каналі — різняться лише
# ширина CRC і поліном. Шість карток із реальними ширинами.
def fig_everywhere():
    W, H = 760, 430
    f = []
    f.append(text(W / 2, 30, "Чому CRC скрізь: один прийом у кожному надійному каналі",
                  15.5, INK, "middle", bold=True))

    cards = [
        ("CAN-шина", "CRC-15", "кадр у машині / дроні", POS),
        ("Ethernet", "CRC-32", "кінець кожного кадру", NEG),
        ("SD-карта", "CRC-7/16", "команди й блоки даних", FIELD),
        ("USB", "CRC-5/16", "токени й пакети даних", "#7a3da8"),
        ("Кадр поверх UART", "CRC-16", "ваш протокол", "#caa24a"),
        ("ZIP / PNG", "CRC-32", "цілість файлу на диску", INK),
    ]
    cw, ch = 224, 116
    gap_x, gap_y = 20, 20
    x_left = (W - (3 * cw + 2 * gap_x)) / 2
    y_top = 64
    for idx, (name, code, sub, col) in enumerate(cards):
        r, c = divmod(idx, 3)
        x = x_left + c * (cw + gap_x)
        y = y_top + r * (ch + gap_y)
        f.append(rect(x, y, cw, ch, fill=BG, stroke=col, sw=2.2, rx=9))
        f.append(text(x + cw / 2, y + 30, name, 15, col, "middle", bold=True))
        f.append(text(x + cw / 2, y + 62, code, 18, INK, "middle", bold=True))
        f.append(text(x + cw / 2, y + 90, sub, 11.5, MUTED, "middle"))

    f.append(text(W / 2, 414, "Скрізь та сама ідея: дописати остачу від ділення на поліном. Різні лише ширина CRC і поліном.",
                  12.5, INK, "middle", italic=True))

    render(os.path.join(IMG, "crc-everywhere.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури вставки ⚙️ (proj-crc-implementation.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── proj-1. Бітовий CRC: ділення на многочлен крок за кроком у коді ────────────
# Ідея: правило одного такту (зсув, і за потреби XOR полінома) — це стиснуте
# ділення в стовпчик над GF(2); праворуч — повне трасування восьми тактів.
def fig_bitloop():
    W, H = 760, 620
    f = []
    f.append(text(W / 2, 28, "Бітовий CRC: те саме ділення на многочлен, крок за кроком у коді",
                  15.5, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "Приклад: CRC-8, поліном 0x07 (x⁸+x²+x+1), регістр 8 біт, один байт 0x31",
                  11.5, MUTED, "middle", italic=True))

    # ліва картка: правило одного такту
    f.append(fitbox(40, 70, 330, 156,
                    "Правило одного такту циклу\n\n"
                    "msb = старший біт crc\n"
                    "crc <<= 1            (зсув уліво)\n"
                    "if (msb == 1)\n"
                    "    crc ^= 0x07      (XOR поліном)\n\n"
                    "Зсув = «опустити наступний біт»;\n"
                    "XOR на 1 угорі = «відняти дільник».",
                    size=11.5, fill="#f4f7ff", stroke=NEG, color=INK))

    # права картка: походження
    f.append(fitbox(390, 70, 330, 156,
                    "Звідки це: ділення в стовпчик над GF(2)\n\n"
                    "CRC — це остача від ділення повідомлення\n"
                    "на многочлен. Над GF(2) віднімання = XOR,\n"
                    "а «чи ділиться» вирішує лише старший біт.\n"
                    "Тож шкільне ділення стовпчиком стискається\n"
                    "до двох дій: зсунути регістр і, якщо зверху\n"
                    "була 1, XOR-нути поліном. Більше нічого.",
                    size=11, fill="#f0fff2", stroke=FIELD, color=INK))

    # трасування
    f.append(text(W / 2, 258, "Трасування восьми тактів над байтом 0x31 = 0011 0001",
                  12.5, INK, "middle", bold=True))
    # заголовки колонок
    f.append(text(80, 286, "такт", 11, MUTED, "start", bold=True))
    f.append(text(150, 286, "біт", 11, MUTED, "start", bold=True))
    f.append(text(430, 286, "регістр CRC після такту", 11, MUTED, "middle", bold=True))
    f.append(text(660, 286, "дія", 11, MUTED, "middle", bold=True))

    # 8 тактів CRC-8/0x07 над 0x31: відомий результат 0x97
    rows = [
        (1, "0", "00110001", "зсув"),
        (2, "0", "01100010", "зсув"),
        (3, "1", "11000100", "зсув"),
        (4, "1", "10001011", "зсув + XOR"),
        (5, "0", "00010110", "зсув"),
        (6, "0", "00101100", "зсув"),
        (7, "0", "01011000", "зсув"),
        (8, "1", "10010111", "зсув + XOR"),
    ]
    y = 312
    cell = 28
    for i, (t, b, reg, act) in enumerate(rows):
        xored = "XOR" in act
        col = POS if xored else NEG
        if i % 2 == 1:
            f.append(rect(70, y - 18, 620, 26, fill="#fafafa", stroke="#fafafa", sw=0, rx=4))
        f.append(text(86, y, str(t), 13, INK, "middle", bold=True))
        f.append(text(156, y, b, 13, POS if b == "1" else NEG, "middle", bold=True))
        bx = 300
        for j, ch in enumerate(reg):
            f.append(text(bx + j * cell, y, ch, 12.5,
                          POS if ch == "1" else NEG, "middle", bold=True))
        f.append(text(660, y, act, 10.5, col, "middle", bold=xored))
        y += 30

    f.append(fitbox(80, y + 4, 600, 32,
                    "Остача = CRC-8 байта:  0b10010111 = 0x97",
                    size=12.5, fill="#f0fff2", stroke=FIELD, color=INK, bold=True))
    f.append(text(W / 2, y + 56, "Для кадру з кількох байтів цикл просто повторюють, заводячи кожен наступний байт.",
                  10.5, MUTED, "middle", italic=True))

    render(os.path.join(IMG, "bitloop-trace.svg"), W, H, *f)


# ── proj-2. Таблична версія: вісім тактів згорнуто в одне читання ──────────────
def fig_table():
    W, H = 760, 470
    f = []
    f.append(text(W / 2, 28, "Таблична версія: вісім бітових тактів згорнуто в одне читання",
                  15.5, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "Ідея Сарвейта: наслідок восьми тактів залежить лише від байта зверху — рахуймо його заздалегідь",
                  11, MUTED, "middle", italic=True))

    f.append(fitbox(50, 70, 300, 110,
                    "Бітовий цикл — 8 тактів на байт\n\n"
                    "8 розгалужень «if msb»\n"
                    "на кожен байт даних",
                    size=12, fill=BG, stroke=MUTED, color=INK))
    f.append(arrow(360, 125, 420, 125, color=FIELD, sw=3))
    f.append(text(390, 112, "одне", 11, FIELD, "middle", bold=True))
    f.append(text(390, 152, "читання", 11, FIELD, "middle", bold=True))
    f.append(fitbox(430, 70, 280, 110,
                    "Таблична версія — 1 крок на байт\n\n"
                    "idx = (crc >> 8) ^ byte\n"
                    "crc = (crc << 8) ^ T[idx]\n\n"
                    "Жодних гілок у гарячому циклі.",
                    size=11.5, fill="#f0fff2", stroke=FIELD, color=INK))

    # як народжується рядок таблиці
    f.append(text(W / 2, 212, "Як народжується один рядок T[i]: проганяємо «бітовим» циклом самé значення i",
                  12, INK, "middle", bold=True))
    f.append(fitbox(70, 230, 150, 56, "байт i\n0x00 … 0xFF",
                    size=12, fill=BG, stroke="#7a3ea8", color=INK))
    f.append(arrow(225, 258, 290, 258, color=INK, sw=2.4))
    f.append(fitbox(290, 230, 200, 56, "бітовий цикл 8 разів\n(той самий, що ліворуч)",
                    size=11, fill="#f4f7ff", stroke=NEG, color=INK))
    f.append(arrow(495, 258, 560, 258, color=INK, sw=2.4))
    f.append(fitbox(560, 230, 150, 56, "T[i]\nзапис у таблицю",
                    size=11, fill="#f0fff2", stroke=FIELD, color=INK))
    f.append(text(W / 2, 304, "Це роблять один раз — на старті програми; далі таблиця лежить готова.",
                  10.5, MUTED, "middle", italic=True))

    # фрагмент таблиці CRC-32
    f.append(text(W / 2, 332, "Фрагмент готової таблиці (CRC-32, рефлексований варіант)",
                  12, INK, "middle", bold=True))
    tbl = [("0x00", "0x00000000"), ("0x01", "0x77073096"), ("0x02", "0xEE0E612C"),
           ("0x03", "0x990951BA"), ("0x04", "0x076DC419")]
    cw = 130
    x0 = (W - len(tbl) * cw) / 2
    for i, (idx, val) in enumerate(tbl):
        x = x0 + i * cw
        f.append(rect(x + 4, 346, cw - 8, 54, fill="#fcfcfc", stroke="#e4e4e4", sw=1.4))
        f.append(text(x + cw / 2, 368, idx, 12, "#7a3ea8", "middle", bold=True))
        f.append(text(x + cw / 2, 390, val, 11, INK, "middle"))

    f.append(fitbox(50, 414, 660, 44,
                    "Платимо пам'яттю: таблиця CRC-32 — 256×4 = 1024 байти Flash (CRC-8 — 256 байтів).\n"
                    "Виграємо ~увосьмеро менше тактів і жодних гілок — на МК без апаратного CRC це найходовіший компроміс.",
                    size=10.5, fill="#fff7ec", stroke="#caa24a", color=INK))

    render(os.path.join(IMG, "table-version.svg"), W, H, *f)


# ── proj-3. Вибір CRC: ширина — покриття, параметри — сумісність ───────────────
def fig_params():
    W, H = 760, 560
    f = []
    f.append(text(W / 2, 28, "Вибір CRC: ширина вирішує покриття, параметри вирішують сумісність",
                  15, INK, "middle", bold=True))

    widths = [
        ("CRC-8", "0x07", "8 біт", "короткі кадри давачів", "≤ 8 біт; пропуск ≈ 2⁻⁸", NEG),
        ("CRC-16", "0x1021", "16 біт", "пакети, карти пам'яті", "≤ 16 біт; пропуск ≈ 2⁻¹⁶", FIELD),
        ("CRC-32", "0x04C11DB7", "32 біти", "Ethernet, великі блоки", "≤ 32 біт; пропуск ≈ 2⁻³²", "#7a3ea8"),
    ]
    cw = 224
    x0 = (W - (3 * cw + 2 * 16)) / 2
    for i, (name, poly, wbits, where, catch, col) in enumerate(widths):
        x = x0 + i * (cw + 16)
        f.append(rect(x, 52, cw, 150, fill="#fcfcfc", stroke=col, sw=2.2, rx=10))
        f.append(rect(x, 52, cw, 28, fill=col, stroke=col, sw=0, rx=10))
        f.append(text(x + cw / 2, 72, name, 15, BG, "middle", bold=True))
        f.append(text(x + 14, 104, "поліном " + poly, 12, col, "start", bold=True))
        f.append(text(x + 14, 124, "ширина: " + wbits, 11, INK, "start"))
        f.append(text(x + 14, 150, "де: " + where, 10.5, INK, "start"))
        f.append(text(x + 14, 176, "ловить: " + catch, 10, MUTED, "start"))
    f.append(text(W / 2, 222, "Ширша остача — рідший хибний пропуск і довший спійманий сплеск, але більше байтів і такти/таблиця.",
                  10.5, MUTED, "middle", italic=True))

    # пятірка параметрів
    f.append(text(W / 2, 256, "Чому дві коректні реалізації того самого полінома дають різні числа",
                  12.5, INK, "middle", bold=True))
    params = [
        ("init", "чим заряджено регістр\nперед першим байтом", POS),
        ("refin / refout", "чи перевертати порядок\nбітів у байті й на виході", "#caa24a"),
        ("xorout", "чим XOR-нути остачу\nнаприкінці", NEG),
    ]
    pw = 224
    px0 = (W - (3 * pw + 2 * 16)) / 2
    for i, (name, desc, col) in enumerate(params):
        x = px0 + i * (pw + 16)
        f.append(rect(x, 270, pw, 80, fill=BG, stroke=col, sw=1.8, rx=9))
        f.append(text(x + pw / 2, 292, name, 13, col, "middle", bold=True))
        for j, ln in enumerate(desc.split("\n")):
            f.append(text(x + pw / 2, 314 + j * 16, ln, 10.5, INK, "middle"))
    f.append(text(W / 2, 368, "Поміняй будь-що одне — і число зміниться, хоч поліном той самий.",
                  11, POS, "middle", bold=True))

    # дерево вибору
    f.append(text(W / 2, 400, "Як обрати на практиці", 13, FIELD, "middle", bold=True))
    tree = [
        ("Є апаратний блок CRC у МК?", "беремо саме його поліном і параметри", FIELD),
        ("Говоримо з готовим протоколом?", "копіюємо ВСІ параметри з його специфікації", NEG),
        ("Свій формат, кадри короткі?", "CRC-8/16 таблицею — дешево", "#caa24a"),
        ("Свій формат, блоки великі/критичні?", "CRC-32 — найменший хибний пропуск", "#7a3ea8"),
    ]
    y = 420
    for q, a, col in tree:
        f.append(circle(70, y - 4, 5, fill=col, stroke=col, sw=1))
        f.append(text(86, y, q, 11.5, INK, "start", bold=True))
        f.append(arrow(390, y - 4, 420, y - 4, color=col, sw=2))
        f.append(text(428, y, a, 11, col, "start"))
        y += 30
    f.append(text(W / 2, 548, "Головне правило: CRC задають не лише поліном, а й init, refin/refout і xorout — звіряти всю п'ятірку.",
                  11, FIELD, "middle", bold=True))

    render(os.path.join(IMG, "crc-choice.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури вставки 🔌 (comp-hardware-crc.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── comp-1. Периферійний блок CRC у мікроконтролері ───────────────────────────
def fig_block():
    W, H = 760, 470
    f = []
    f.append(text(W / 2, 28, "Апаратний блок CRC у мікроконтролері (STM32-клас)",
                  15.5, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "Процесор лише пише слова в регістр і читає готову остачу — такти зсуву й XOR блок робить сам",
                  11, MUTED, "middle", italic=True))

    # шина
    f.append(line(60, 150, 700, 150, color=INK, sw=3))
    f.append(text(70, 138, "внутрішня шина МК (AHB / APB)", 11, MUTED, "start", bold=True))

    # ядро
    f.append(rect(70, 96, 150, 90, fill="#f4f7ff", stroke=NEG, sw=2))
    f.append(text(145, 120, "Ядро (CPU)", 13, NEG, "middle", bold=True))
    f.append(text(145, 142, "пише слово →", 10.5, INK, "middle"))
    f.append(text(145, 158, "← читає остачу", 10.5, INK, "middle"))
    f.append(text(145, 178, "вільне для іншого", 9.5, FIELD, "middle", italic=True))

    # блок CRC
    f.append(rect(280, 200, 420, 200, fill="#fffdf6", stroke="#caa24a", sw=2.4, rx=12))
    f.append(text(490, 224, "Периферійний блок CRC", 14, "#caa24a", "middle", bold=True))

    f.append(fitbox(310, 246, 180, 50, "DR — регістр даних\nCRC->DR = word;",
                    size=11, fill=BG, stroke=NEG, color=INK))
    f.append(text(400, 314, "сюди процесор кладе 32-бітне слово", 9.5, MUTED, "middle"))

    f.append(rect(310, 326, 180, 60, fill="#fdeeee", stroke=POS, sw=2, rx=8))
    f.append(text(400, 348, "зсувний регістр + XOR", 11, POS, "middle", bold=True))
    f.append(text(400, 368, "відводи = поліном", 9.5, INK, "middle"))
    f.append(text(400, 380, "за такт — зсув і XOR", 9.5, INK, "middle"))
    f.append(arrow(400, 296, 400, 324, color=INK, sw=2.2))

    f.append(fitbox(520, 246, 160, 50, "акумулятор остачі\ncrc = CRC->DR;",
                    size=10.5, fill="#f0fff2", stroke=FIELD, color=INK))
    f.append(text(600, 314, "читання = готовий CRC", 9.5, MUTED, "middle"))
    f.append(arrow(490, 350, 520, 290, color=FIELD, sw=2))

    f.append(fitbox(520, 326, 160, 60,
                    "фіксоване в залізі:\nполіном, init;\nдеякі блоки — настроювані",
                    size=9.5, fill=BG, stroke="#7a3ea8", color=INK))

    f.append(fitbox(60, 416, 640, 40,
                    "Суть: апаратний CRC — той самий бітовий цикл, виконаний електронікою за частку такту на біт.\n"
                    "Ядро не крутить цикл — лише годує блок словами й наприкінці читає остачу.",
                    size=10.5, fill="#f0fff2", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "mcu-crc-block.svg"), W, H, *f)


# ── comp-2. CRC на дроті в контролерах CAN і SD ───────────────────────────────
def fig_inline():
    W, H = 760, 480
    f = []
    f.append(text(W / 2, 28, "Інша оселя того ж CRC: усередині контролерів CAN і SD він живе прямо на лінії",
                  14.5, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "Тут CRC не послуга для процесора, а вартовий на дроті: рахується сам, на льоту, повз ядро",
                  11, MUTED, "middle", italic=True))

    def frame(y, label):
        f.append(text(70, y - 14, label, 12.5, INK, "start", bold=True))
        names = ["ідентиф.", "дані", "дані", "дані"]
        for i, nm in enumerate(names):
            x = 70 + i * 86
            f.append(rect(x, y, 80, 38, fill="#f4f7ff", stroke=NEG, sw=1.8, rx=6))
            f.append(text(x + 40, y + 23, nm, 11, NEG, "middle", bold=True))
        # CRC-поле
        x = 70 + 4 * 86
        f.append(rect(x, y, 80, 38, fill="#fdeeee", stroke=POS, sw=2.2, rx=6))
        f.append(text(x + 40, y + 17, "CRC", 11.5, POS, "middle", bold=True))
        f.append(text(x + 40, y + 31, "15/16 біт", 9, POS, "middle"))
        return x

    # передавання
    cx = frame(110, "Передавання кадру")
    f.append(text(cx + 130, 133, "→ на шину", 10.5, MUTED, "start"))
    f.append(fitbox(180, 170, 240, 48,
                    "апаратний генератор CRC\nрахує остачу з усіх байтів кадру",
                    size=10, fill="#fffdf6", stroke="#caa24a", color=INK))
    f.append(arrow(420, 188, cx + 40, 150, color=POS, sw=2.2))
    f.append(text(430, 180, "сам дописує", 10, POS, "start", bold=True))

    # лінія
    f.append(line(60, 248, 700, 248, color=INK, sw=3))
    f.append(text(W / 2, 240, "фізична лінія (CAN-шина / SPI до картки) — біти летять як є",
                  10.5, MUTED, "middle", bold=True))

    # приймання
    cx = frame(296, "Приймання кадру")
    f.append(fitbox(180, 352, 240, 48,
                    "той самий генератор у приймачі\nрахує CRC заново з прийнятих байтів",
                    size=10, fill="#fffdf6", stroke="#caa24a", color=INK))
    f.append(rect(470, 352, 230, 48, fill="#f0fff2", stroke=FIELD, sw=2, rx=9))
    f.append(text(585, 372, "звіряє: свій CRC = CRC з кадру?", 10.5, FIELD, "middle", bold=True))
    f.append(text(585, 390, "збіглися → прийнято · ні → відкинуто", 9.5, POS, "middle", bold=True))
    f.append(arrow(420, 376, 468, 376, color=FIELD, sw=2.2))

    f.append(fitbox(60, 426, 640, 44,
                    "Ключова відмінність від блока в МК: тут CRC вбудований у протокол і працює автоматично —\n"
                    "апаратура сама додає його при передачі й перевіряє при прийомі, ще до того, як байти дійдуть до коду.",
                    size=10.5, fill="#f4f7ff", stroke=NEG, color=INK))

    render(os.path.join(IMG, "inline-can-sd.svg"), W, H, *f)


# ── comp-3. Граблі: чому апаратний і програмний CRC дають різні числа ──────────
def fig_gotchas():
    W, H = 760, 540
    f = []
    f.append(text(W / 2, 28, "Граблі апаратного CRC: те саме число лише за повного збігу всіх правил",
                  15, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "Поліном — лише одне з п'яти. Розбіжність у будь-якому пункті — і блок та бібліотека дають різні остачі",
                  10.5, MUTED, "middle", italic=True))

    cards = [
        ("Порядок згодовування", "блок ковтає 32-бітні слова,\nбібліотека — окремі байти", POS),
        ("Рефлексії бітів", "частина блоків НЕ перевертає біти,\nа ходовий CRC-32 у софті — перевертає", "#caa24a"),
        ("init та xorout", "блок може стартувати з 0xFFFFFFFF\nі не робити фінального XOR, або навпаки", "#7a3ea8"),
        ("Поліном за замовчуванням", "у простих блоків зашитий жорстко\n(часто 0x04C11DB7)", NEG),
    ]
    y = 76
    for name, desc, col in cards:
        f.append(rect(40, y, 400, 72, fill="#fcfcfc", stroke=col, sw=2, rx=9))
        f.append(rect(40, y, 6, 72, fill=col, stroke=col, sw=0))
        f.append(text(58, y + 24, name, 12.5, col, "start", bold=True))
        for j, ln in enumerate(desc.split("\n")):
            f.append(text(58, y + 44 + j * 15, ln, 10.5, INK, "start"))
        y += 80

    f.append(fitbox(460, 76, 260, 86,
                    "Симптом, який усіх ловить\n\n"
                    "«CRC рахується і там, і там, обидва\n"
                    "коди коректні — а числа різні».\n"
                    "Причина — один із пунктів зліва.",
                    size=10, fill="#fff7ec", stroke="#caa24a", color=INK))
    f.append(fitbox(460, 172, 260, 144,
                    "Рецепт: звіряти всю п'ятірку\n\n"
                    "1. поліном\n"
                    "2. ширина (8 / 16 / 32 біти)\n"
                    "3. init — заряд регістра\n"
                    "4. refin / refout — рефлексії\n"
                    "5. xorout — фінальний XOR",
                    size=11, fill="#f0fff2", stroke=FIELD, color=INK))

    f.append(line(40, 336, 720, 336, color="#e4e4e4", sw=1.4))
    f.append(text(W / 2, 360, "Коли вмикати апаратний блок, а коли лишитися на софті",
                  13, FIELD, "middle", bold=True))
    rules = [
        ("Великі блоки (кілобайти): прошивка, лог, кадр", "блок МК: розвантажує ядро", FIELD),
        ("CRC уже робить периферія (CAN, SD-контролер)", "нічого не пишемо — рахується сам", NEG),
        ("Формат чужого протоколу (Modbus, своя п'ятірка)", "часто легше софт: гнучкі рефлексії", "#caa24a"),
        ("Кілька байтів зрідка чи економимо код", "табличний софт — простий і переносний", "#7a3ea8"),
    ]
    y = 384
    for q, a, col in rules:
        f.append(circle(58, y - 4, 5, fill=col, stroke=col, sw=1))
        f.append(text(74, y, q, 11, INK, "start", bold=True))
        f.append(arrow(470, y - 4, 500, y - 4, color=col, sw=2))
        f.append(text(508, y, a, 10.5, col, "start"))
        y += 30
    f.append(text(W / 2, 524, "Апаратний CRC економить такти, але остача однакова лише тоді, коли однакова вся п'ятірка параметрів.",
                  11, FIELD, "middle", bold=True))

    render(os.path.join(IMG, "hw-sw-gotchas.svg"), W, H, *f)


if __name__ == "__main__":
    fig_division()
    fig_lfsr()
    fig_everywhere()
    fig_bitloop()
    fig_table()
    fig_params()
    fig_block()
    fig_inline()
    fig_gotchas()
    print("OK: figures written to", IMG)
