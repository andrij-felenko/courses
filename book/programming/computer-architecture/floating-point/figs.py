# -*- coding: utf-8 -*-
"""Фігури до теми «Числа з плаваючою комою».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
GOLD = "#b9770e"     # «проміжне», тепле застереження
PALE_R = "#fdecea"   # світло-червона заливка
PALE_B = "#eaf0fd"   # світло-синя
PALE_G = "#eaf7ee"   # світло-зелена
PALE_Y = "#fbf4e6"   # світло-жовта


# ── 1. Наукова нотація: кома пливе (мантиса × основа^порядок) ────────────────
def fig_scientific():
    W, H = 720, 300
    f = []
    # десятковий рядок
    f.append(text(70, 96, "десятково:", size=13, color=INK, anchor="start", bold=True))
    f.append(text(270, 98, "6.022", size=20, color=FIELD, bold=True))
    f.append(text(345, 98, "× 10", size=17, color=INK, anchor="start", bold=True))
    f.append(text(398, 86, "23", size=12, color=POS, anchor="start", bold=True))
    f.append(text(270, 122, "мантиса", size=10, color=FIELD))
    f.append(text(385, 122, "порядок", size=10, color=POS))
    # двійковий рядок
    f.append(text(70, 176, "двійково:", size=13, color=INK, anchor="start", bold=True))
    f.append(text(255, 178, "1.101", size=20, color=FIELD, bold=True))
    f.append(text(330, 178, "× 2", size=17, color=INK, anchor="start", bold=True))
    f.append(text(362, 166, "3", size=12, color=POS, anchor="start", bold=True))
    f.append(text(400, 178, "= 1.625 × 8 = 13", size=15, color=INK, anchor="start", bold=True))
    # підсумкова рамка
    box = fitbox(60, 210, 600, 66,
                 "Порядок рухає кому куди завгодно — звідси «плаваюча».\n"
                 "Мантиса несе значущі цифри (точність), порядок — масштаб (діапазон).",
                 size=13, fill=PALE_G, stroke=FIELD, sw=1.6)
    f.append(box)
    render(os.path.join(IMG, "scientific.svg"), W, H, *f,
           title="Як наукова нотація: мантиса × основа^порядок")


# ── 2. Формат IEEE 754 float32: знак · порядок · мантиса ─────────────────────
def fig_format():
    W, H = 760, 320
    f = []
    y = 96
    # знак
    f.append(rect(70, y, 46, 50, fill=PALE_Y, stroke=GOLD, sw=2))
    f.append(text(93, y + 32, "S", size=16, color=GOLD, bold=True))
    f.append(text(93, y - 8, "1", size=10, color=MUTED))
    f.append(text(93, y + 70, "знак", size=11, color=GOLD, bold=True))
    # порядок
    f.append(rect(120, y, 210, 50, fill=PALE_B, stroke=NEG, sw=2))
    f.append(text(225, y + 31, "порядок", size=14, color=NEG, bold=True))
    f.append(text(225, y - 8, "8 бітів", size=10, color=MUTED))
    f.append(text(225, y + 70, "куди «пливе» кома", size=11, color=NEG, bold=True))
    # мантиса
    f.append(rect(334, y, 356, 50, fill=PALE_G, stroke=FIELD, sw=2))
    f.append(text(512, y + 31, "мантиса", size=14, color=FIELD, bold=True))
    f.append(text(512, y - 8, "23 біти", size=10, color=MUTED))
    f.append(text(512, y + 70, "значущі цифри (точність)", size=11, color=FIELD, bold=True))
    # формула + пояснення
    box = fitbox(60, 196, 630, 104,
                 "значення = (−1)ˢ × 1.мантиса × 2^(порядок − 127)\n"
                 "Старша 1 мантиси «мається на увазі» (1.xxxx) — даровий зайвий біт.\n"
                 "float32 ≈ 7 значущих цифр; float64 (1+11+52) ≈ 16 цифр.",
                 size=13, fill=FILL, stroke=FIELD, sw=1.6)
    f.append(box)
    render(os.path.join(IMG, "format.svg"), W, H, *f,
           title="Формат IEEE 754 (float32 = 32 біти)")


# ── 3. Величезний динамічний діапазон ───────────────────────────────────────
def fig_range():
    W, H = 720, 300
    f = []
    ax0, ax1, ay = 95, 665, 150
    f.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    ticks = [(ax0, "10⁻³⁸"), ((ax0 + ax1) / 2 - 140, "10⁻¹⁹"),
             ((ax0 + ax1) / 2, "1"), ((ax0 + ax1) / 2 + 140, "10¹⁹"),
             (ax1, "10³⁸")]
    for x, lab in ticks:
        f.append(line(x, ay - 6, x, ay + 6, color=MUTED, sw=1.4))
        f.append(text(x, ay + 24, lab, size=11, color=INK, bold=True))
    f.append(text(ax0, ay - 14, "крихітне ←", size=11, color=NEG, anchor="start", bold=True))
    f.append(text(ax1, ay - 14, "→ величезне", size=11, color=POS, anchor="end", bold=True))
    # вузеньке віконце фіксованої коми
    cx = (ax0 + ax1) / 2
    f.append(rect(cx - 52, ay + 44, 104, 22, fill=PALE_Y, stroke=GOLD, sw=1.6))
    f.append(text(cx, ay + 90, "фіксована кома —", size=11, color=GOLD, bold=True))
    f.append(text(cx, ay + 107, "лише вузьке вікно посередині", size=10.5, color=MUTED))
    box = fitbox(60, 232, 600, 40,
                 "Той самий float тримає і масу електрона, і відстань до зір.",
                 size=12.5, fill=FILL, stroke=FIELD, sw=1.6)
    f.append(box)
    render(os.path.join(IMG, "range.svg"), W, H, *f,
           title="Виграш: величезний динамічний діапазон float32")


# ── 4. Чому float підступний: неточність + відносна точність ─────────────────
def fig_tricky():
    W, H = 760, 372
    f = []
    # Пастка 1
    f.append(rect(50, 64, 330, 124, fill="none", stroke=POS, sw=1.7))
    f.append(text(215, 88, "Пастка 1: неточність", size=12.5, color=POS, bold=True))
    f.append(text(66, 116, "0.1 + 0.2 = 0.300000000000000044", size=12, color=INK, anchor="start", bold=True))
    f.append(text(66, 144, "бо 0.1 у двійковій — нескінченний дріб", size=11, color=MUTED, anchor="start"))
    f.append(text(66, 164, "(як 1/3 у десятковій), тож зберігається", size=11, color=MUTED, anchor="start"))
    f.append(text(66, 182, "з крихітною похибкою округлення.", size=11, color=MUTED, anchor="start"))
    # Пастка 2
    f.append(rect(400, 64, 310, 124, fill="none", stroke=GOLD, sw=1.7))
    f.append(text(555, 88, "Пастка 2: відносна точність", size=12, color=GOLD, bold=True))
    f.append(text(416, 116, "крок між числами росте з величиною:", size=11, color=INK, anchor="start"))
    f.append(text(416, 138, "біля 1 → крок ≈ 0.0000001", size=11, color=INK, anchor="start"))
    f.append(text(416, 158, "біля мільйона → крок ≈ 0.06", size=11, color=INK, anchor="start"))
    f.append(text(416, 180, "біля мільярда → крок > 1 (!)", size=11.5, color=POS, anchor="start", bold=True))
    # Наслідок
    f.append(rect(50, 204, 330, 104, fill=PALE_R, stroke=POS, sw=1.6))
    f.append(text(215, 228, "Наслідок", size=12, color=POS, bold=True))
    f.append(text(66, 254, "1 000 000 000 + 1 = 1 000 000 000", size=12.5, color=INK, anchor="start", bold=True))
    f.append(text(66, 278, "(float32): доданок просто «зник»,", size=11, color=MUTED, anchor="start"))
    f.append(text(66, 296, "бо 1 менше за крок на цій величині.", size=11, color=MUTED, anchor="start"))
    # Рівність
    f.append(rect(400, 204, 310, 104, fill=PALE_R, stroke=POS, sw=1.6))
    f.append(text(555, 228, "Результати — не через ==", size=11.5, color=POS, bold=True))
    f.append(text(416, 254, "погано:  if (x == 0.3)", size=12, color=INK, anchor="start", bold=True))
    f.append(text(416, 278, "добре:   if (|x − 0.3| < ε)", size=12, color=FIELD, anchor="start", bold=True))
    f.append(text(416, 298, "(для точних 0.0, цілих — == доречне)", size=10.5, color=MUTED, anchor="start", italic=True))
    box = fitbox(60, 326, 620, 36,
                 "float чудовий для діапазону, та оманливий для точності.",
                 size=12, fill=FILL, stroke=INK, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "tricky.svg"), W, H, *f,
           title="Чому float підступний: неточність і відносна точність")


# ── 5. Особливі значення й ціна ─────────────────────────────────────────────
def fig_special():
    W, H = 760, 330
    f = []
    # Особливі значення
    f.append(rect(50, 64, 330, 210, fill="none", stroke=NEG, sw=1.7))
    f.append(text(215, 88, "Особливі значення", size=13, color=NEG, bold=True))
    rows = [("+∞ / −∞", "переповнення, ділення на 0"),
            ("NaN", "«не число»: 0/0, √(−1) — заразне!"),
            ("+0 / −0", "два нулі (нешкідливо)"),
            ("денормалі", "найдрібніші, біля нуля")]
    yy = 120
    for a, b in rows:
        f.append(text(66, yy, a, size=13, color=POS, anchor="start", bold=True))
        f.append(text(186, yy, b, size=11, color=INK, anchor="start"))
        yy += 36
    # Ціна
    f.append(rect(400, 64, 310, 210, fill="none", stroke=GOLD, sw=1.7))
    f.append(text(555, 88, "Ціна", size=13, color=GOLD, bold=True))
    cost = ["арифметика складна: вирівняти",
            "порядки, нормалізувати, округлити;",
            "без апаратного FPU — емуляція",
            "програмою → повільно (десятки тактів);",
            "ESP32 має FPU (одинарна точність),",
            "дрібні 8-біт МК — ні, тому там",
            "фіксована кома часто швидша."]
    yy = 116
    for ln in cost:
        f.append(text(414, yy, ln, size=11, color=INK, anchor="start"))
        yy += 22
    box = fitbox(60, 292, 620, 32,
                 "На МК: float — для зручності й діапазону; фіксована кома — для швидкості й точності.",
                 size=11.5, fill=FILL, stroke=INK, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "special.svg"), W, H, *f,
           title="Особливі значення й ціна плаваючої коми")


# ── proj-1. Крок між float росте → фіксований ε не годиться ──────────────────
def fig_spacing():
    W, H = 760, 430
    f = []
    rows = [(96, NEG, "біля 1.0", "крок ≈ 1.2×10⁻⁷"),
            (196, GOLD, "біля 1 000 000", "крок ≈ 0.06"),
            (296, POS, "біля 1 000 000 000", "крок ≈ 64 (!)")]
    for ay, col, left, right in rows:
        f.append(line(70, ay, 600, ay, color=INK, sw=2))
        f.append(arrow(600, ay, 624, ay, color=INK, sw=1.8))
        for i in range(6):
            x = 100 + i * 96
            f.append(line(x, ay - 9, x, ay + 9, color=col, sw=2.4))
            f.append(circle(x, ay, 3.2, fill=col, stroke=col, sw=0))
        f.append(text(70, ay - 18, left, size=13, color=col, anchor="start", bold=True))
        f.append(text(636, ay + 5, right, size=12.5, color=col, anchor="start", bold=True))
    # дві пастки
    f.append(rect(50, 356, 330, 58, fill=PALE_R, stroke=POS, sw=1.7))
    f.append(text(215, 379, "ε завеликий (0.001)", size=12.5, color=POS, bold=True))
    f.append(text(215, 399, "біля мільярда числа за 64 одиниці «зіллються»", size=10.5, color=INK))
    f.append(rect(400, 356, 310, 58, fill=PALE_R, stroke=POS, sw=1.7))
    f.append(text(555, 379, "ε замалий (10⁻⁹)", size=12.5, color=POS, bold=True))
    f.append(text(555, 399, "біля 1.0 жодні сусіди не «рівні» — крок більший", size=10.5, color=INK))
    render(os.path.join(IMG, "spacing.svg"), W, H, *f,
           title="Крок між float росте — один фіксований ε не годиться")


# ── proj-2. Три види допуску: абсолютний · відносний · комбінований ──────────
def fig_three_kinds():
    W, H = 760, 470
    f = []
    cols = [
        (48, NEG, "Абсолютний", "|a − b| ≤ εабс",
         ["Один сталий допуск.", "Працює БІЛЯ НУЛЯ", "(де відносний ділив би", "на ≈0 і вибухав).",
          "", "Хибний на великих:", "при a=10⁶ поріг 10⁻⁶", "недосяжний."], "±", GOLD),
        (262, GOLD, "Відносний", "|a−b| ≤ εвідн·max(|a|,|b|)",
         ["Допуск росте з числом —", "як і крок float.", "Універсальний для", "звичайних величин.",
          "", "Ламається БІЛЯ НУЛЯ:", "max→0, поріг→0,", "0.0 vs 10⁻³⁰ «нерівні»."], "±", GOLD),
        (476, FIELD, "Комбінований", "абс. якщо малі, інакше відн.",
         ["Спершу абсолютна гілка", "для околу нуля,", "далі — відносна.", "Саме так і роблять:",
          "одна функція", "nearEqual(a, b).", "", "Покриває весь діапазон."], "✓", FIELD),
    ]
    for x, col, head, formula, lines, badge, bcol in cols:
        f.append(rect(x, 64, 200, 386, fill="#fafafa", stroke=col, sw=1.8))
        f.append(text(x + 100, 92, head, size=15, color=col, bold=True))
        f.append(fitbox(x + 10, 106, 180, 32, formula, size=11, fill=BG, stroke=col, sw=1.2))
        yy = 168
        for ln in lines:
            if ln:
                cc = POS if ("Хибний" in ln or "Ламається" in ln) else INK
                bold = cc == POS
                f.append(text(x + 14, yy, ln, size=11.5, color=cc, anchor="start", bold=bold))
            yy += 22
        f.append(circle(x + 100, 424, 13, fill=bcol, stroke=bcol, sw=0))
        f.append(text(x + 100, 429, badge, size=16, color=BG, bold=True))
    render(os.path.join(IMG, "three-kinds.svg"), W, H, *f,
           title="Три види допуску — і чому потрібні всі три")


# ── proj-3. ULP-порівняння: біти float як ціле нумерують сусідів ─────────────
def fig_ulp():
    W, H = 760, 460
    f = []
    f.append(text(380, 96, "послідовні float-значення (один крок ULP між сусідами)",
                  size=12, color=MUTED, italic=True))
    cells = [("1.0000000", "0x3F800000", "N", FIELD),
             ("1.0000001", "0x3F800001", "N+1", POS),
             ("1.0000002", "0x3F800002", "N+2", POS),
             ("1.0000004", "0x3F800003", "N+3", POS),
             ("1.0000005", "0x3F800004", "N+4", POS),
             ("1.0000006", "0x3F800005", "N+5", POS)]
    x0, w, gap = 60, 104, 14
    for i, (val, hexcode, lab, col) in enumerate(cells):
        x = x0 + i * (w + gap)
        fillc = PALE_G if i == 0 else "#fafafa"
        strokec = FIELD if i == 0 else INK
        f.append(rect(x, 130, w, 54, fill=fillc, stroke=strokec, sw=1.6))
        f.append(text(x + w / 2, 153, val, size=12.5, color=INK))
        f.append(text(x + w / 2, 174, hexcode, size=11, color=NEG))
        f.append(text(x + w / 2, 206, lab, size=13, color=col, bold=True))
        if i > 0:
            f.append(arrow(x - gap, 157, x, 157, color=MUTED, sw=1.6))
    f.append(text(380, 240, "ті самі біти як 32-бітне ціле → рівно +1 на кожен крок",
                  size=12.5, color=NEG, bold=True))
    f.append(fitbox(150, 262, 460, 84,
                    "ulpDiff = | bitsAsInt(a) − bitsAsInt(b) |\n"
                    "«рівні» ⇔ ulpDiff ≤ maxUlps (типово 1…4)\n"
                    "поріг у ULP сам масштабується — окремий ε не потрібен",
                    size=13, fill=PALE_B, stroke=NEG, sw=1.7))
    f.append(rect(50, 366, 660, 78, fill=PALE_R, stroke=POS, sw=1.6))
    f.append(text(66, 390, "Пастки ULP:", size=12.5, color=POS, anchor="start", bold=True))
    f.append(text(66, 412, "• знак: від'ємні float як ціле йдуть «навспак» — різні знаки обробляємо окремо;",
                  size=11, color=INK, anchor="start"))
    f.append(text(66, 432, "• NaN не «рівний» нічому (перевірка перша); ±0 — окремий випадок; біти — через memcpy/union.",
                  size=11, color=INK, anchor="start"))
    render(os.path.join(IMG, "ulp.svg"), W, H, *f,
           title="ULP: біти float як ціле нумерують представні числа")


# ── hist-1. До й після IEEE 754: хаос → один стандарт ───────────────────────
def fig_chaos():
    W, H = 760, 400
    f = []
    f.append(text(200, 88, "ДО: Вавилон форматів", size=13, color=POS, bold=True))
    f.append(text(560, 88, "ПІСЛЯ: один стандарт", size=13, color=FIELD, bold=True))
    before = [(60, 120, "IBM", "16-кова основа", "= 3.1399"),
              (60, 216, "DEC VAX", "свій формат", "= 3.1416"),
              (200, 120, "Cray", "інше округлення", "= 3.14001"),
              (200, 216, "CDC", "60-біт слова", "= 3.1420")]
    for x, y, name, sub, res in before:
        f.append(rect(x, y, 124, 84, fill="#fafafa", stroke=INK, sw=1.7))
        f.append(text(x + 62, y + 22, name, size=12, color=INK, bold=True))
        f.append(text(x + 62, y + 42, sub, size=9.5, color=MUTED))
        f.append(text(x + 62, y + 66, res, size=12, color=POS, bold=True))
    f.append(text(200, 320, "різні відповіді → нікому не вірити", size=11, color=POS, bold=True))
    # стрілка 754
    f.append(arrow(338, 220, 408, 220, color=INK, sw=2.4))
    f.append(text(373, 208, "754", size=11, color=FIELD, bold=True))
    after = [(440, 120, "Intel"), (568, 120, "ARM"),
             (440, 216, "ESP32"), (568, 216, "ПК")]
    for x, y, name in after:
        f.append(rect(x, y, 124, 84, fill="#fafafa", stroke=INK, sw=1.7))
        f.append(text(x + 62, y + 22, name, size=12, color=INK, bold=True))
        f.append(text(x + 62, y + 42, "IEEE 754", size=9.5, color=MUTED))
        f.append(text(x + 62, y + 66, "= 3.14159", size=12, color=FIELD, bold=True))
    f.append(text(564, 320, "формат → базові операції біт-у-біт", size=11, color=FIELD, bold=True))
    f.append(fitbox(60, 348, 640, 40,
                    "IEEE 754 (1985) зробив плаваючу кому передбачуваною й переносною.",
                    size=12, fill=FILL, stroke=INK, sw=1.4))
    render(os.path.join(IMG, "chaos.svg"), W, H, *f,
           title="До й після IEEE 754: від хаосу форматів до стандарту")


# ── hist-2. Що саме стандартизував IEEE 754 ─────────────────────────────────
def fig_fixed():
    W, H = 760, 392
    f = []
    rows = [("Формати", "одинарна (32) і подвійна (64) точність — однакові скрізь"),
            ("Коректне округлення", "результат +−×÷ і √ — це точно округлене істинне значення"),
            ("Округлення до парного", "round-to-nearest-even за замовчуванням (без зсуву)"),
            ("Особливі значення", "±∞, NaN, ±0 — означені однозначно"),
            ("Поступове зникання", "денормалі: біля нуля числа «згасають» плавно"),
            ("Винятки/прапорці", "ділення на 0, переповнення, неточність — сигналізуються")]
    y = 84
    for i, (a, b) in enumerate(rows):
        fillc = "#f6f8f6" if i % 2 == 0 else BG
        f.append(rect(60, y, 640, 36, fill=fillc, stroke=MUTED, sw=1, rx=6))
        f.append(text(78, y + 23, a, size=12.5, color=FIELD, anchor="start", bold=True))
        f.append(text(300, y + 23, b, size=11.5, color=INK, anchor="start"))
        y += 42
    f.append(fitbox(60, y + 4, 640, 34,
                    "Найреволюційніша — «коректне округлення»: воно зробило результат float однозначним.",
                    size=11.5, fill=FILL, stroke=FIELD, sw=1.4))
    render(os.path.join(IMG, "fixed.svg"), W, H, *f,
           title="Що саме стандартизував IEEE 754")


# ── hist-3. Сума Кехена: компенсоване підсумовування ────────────────────────
def fig_kahan():
    W, H = 760, 360
    f = []
    # наївна
    f.append(rect(50, 64, 330, 230, fill="none", stroke=POS, sw=1.7))
    f.append(text(215, 88, "Наївна сума", size=12.5, color=POS, bold=True))
    f.append(text(66, 116, "sum = 0", size=12, color=INK, anchor="start", bold=True))
    f.append(text(66, 138, "for x: sum += x", size=12, color=INK, anchor="start", bold=True))
    f.append(text(66, 172, "додаючи дрібне до великого,", size=11, color=MUTED, anchor="start"))
    f.append(text(66, 190, "молодші біти «зрізаються» —", size=11, color=MUTED, anchor="start"))
    f.append(text(66, 208, "і губляться назавжди.", size=11, color=POS, anchor="start", bold=True))
    f.append(text(66, 242, "сумуючи мільйон чисел,", size=11, color=MUTED, anchor="start"))
    f.append(text(66, 260, "похибка накопичується помітно.", size=11, color=MUTED, anchor="start"))
    # Кехена
    f.append(rect(400, 64, 310, 230, fill="none", stroke=FIELD, sw=1.7))
    f.append(text(555, 88, "Сума Кехена (компенсована)", size=11.5, color=FIELD, bold=True))
    f.append(text(416, 116, "тримаємо «загублене» c:", size=11.5, color=INK, anchor="start", bold=True))
    f.append(text(416, 140, "y = x − c", size=12, color=INK, anchor="start"))
    f.append(text(416, 160, "t = sum + y", size=12, color=INK, anchor="start"))
    f.append(text(416, 180, "c = (t − sum) − y", size=12, color=FIELD, anchor="start", bold=True))
    f.append(text(416, 200, "sum = t", size=12, color=INK, anchor="start"))
    f.append(text(416, 234, "c ловить зрізані біти й", size=11, color=MUTED, anchor="start"))
    f.append(text(416, 252, "повертає їх наступного кроку →", size=11, color=MUTED, anchor="start"))
    f.append(text(416, 270, "похибка лишається ~ сталою.", size=11, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(60, 312, 640, 34,
                    "Той самий Кехен, що творив IEEE 754, дав і цей прийом — щоб дрібниці не губилися в сумах.",
                    size=11.5, fill=FILL, stroke=INK, sw=1.4))
    render(os.path.join(IMG, "kahan.svg"), W, H, *f,
           title="Спадок Кехена: компенсоване підсумовування")


if __name__ == "__main__":
    fig_scientific()
    fig_format()
    fig_range()
    fig_tricky()
    fig_special()
    fig_spacing()
    fig_three_kinds()
    fig_ulp()
    fig_chaos()
    fig_fixed()
    fig_kahan()
    print("OK: 11 фігур у", IMG)
