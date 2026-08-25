# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACC = "#caa24a"   # акцент «підпису» (контрольної суми) — теплий жовтий


# ── sum: проста сума байтів і її сліпа пляма (перестановка) ───────────────────
# Ідея: чотири байти складаються в один «підпис»; нижче ті самі байти переставлено
# місцями — а сума та сама, тож проста сума перестановки не бачить.

def fig_sum():
    W, H = 700, 360
    p = []
    bw, bh, gap = 64, 36, 40
    x0 = 70

    def row(y, vals, box_fill, box_stroke, op):
        xs = []
        x = x0
        for i, v in enumerate(vals):
            p.append(rect(x, y, bw, bh, fill=box_fill, stroke=box_stroke, sw=1.6, rx=5))
            p.append(text(x + bw / 2, y + bh / 2 + 5, v, size=14, color=INK, bold=True))
            xs.append(x)
            if i < len(vals) - 1:
                p.append(text(x + bw + (gap - bw) / 2 + bw / 2, y + bh / 2 + 6, op, size=17, color=INK, bold=True))
            x += gap + bw
        # «=» і рамка підпису
        p.append(text(x + 4, y + bh / 2 + 6, "=", size=17, color=INK, bold=True))
        sx = x + 26
        p.append(rect(sx, y, bw + 8, bh, fill="#fff8e8", stroke=ACC, sw=2.4, rx=5))
        p.append(text(sx + (bw + 8) / 2, y + bh / 2 + 5, "0x14", size=14, color=ACC, bold=True))
        return sx + (bw + 8) / 2

    # верхній рядок: оригінал
    cx = row(96, ["0x12", "0x34", "0x56", "0x78"], "#eaf0ff", NEG, "+")
    p.append(text(cx, 96 - 10, "підпис", size=11, color=ACC, bold=True))
    p.append(text(x0, 80, "сума = (b₁ + b₂ + … + bₙ) mod 256", size=12, color=MUTED, anchor="start", italic=True))

    # роздільник
    p.append(line(50, 188, 650, 188, color="#e4e4e4", sw=1.4))
    p.append(text(50, 210, "Сліпа пляма: переставимо байти місцями —", size=13, color=POS, anchor="start", bold=True))

    # нижній рядок: переставлені
    row(228, ["0x34", "0x12", "0x78", "0x56"], "#fdeceb", POS, "+")

    p.append(text(W / 2, 300, "сума ТА САМА — а дані інші: додавання не залежить від порядку",
                  size=13, color=POS, bold=True))
    p.append(text(W / 2, 324, "так само сума не бачить взаємних +1 / −1 у різних байтах",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "sum.svg"), W, H, *p,
           title="Проста сума: чотири байти згортаються в один підпис")


# ── fletcher: дві суми, друга зважує байт позицією ───────────────────────────
# Ідея: таблиця кроків — sum1 накопичує байти, sum2 накопичує sum1; нижче пояснено,
# чому ранній байт важить більше і чому це ловить перестановку.

def fig_fletcher():
    W, H = 700, 420
    p = []
    cols = [90, 210, 340, 510]            # крок · байт · sum1 · sum2
    head = ["крок", "байт", "sum1 += байт", "sum2 += sum1"]
    for cx, h in zip(cols, head):
        p.append(text(cx, 96, h, size=13, color=INK, anchor="start", bold=True))
    p.append(line(90, 106, 660, 106, color=MUTED, sw=1.4))

    rows = [
        ("1", "0x12", "18", "18"),
        ("2", "0x34", "70", "88"),
        ("3", "0x56", "156", "244"),
        ("4", "0x78", "21", "10"),
    ]
    y = 134
    for step, byte, s1, s2 in rows:
        p.append(text(cols[0], y, step, size=13, color=MUTED, anchor="start"))
        p.append(text(cols[1], y, byte, size=13.5, color=NEG, anchor="start", bold=True))
        p.append(text(cols[2], y, s1, size=13.5, color=INK, anchor="start"))
        p.append(text(cols[3], y, s2, size=13.5, color=ACC, anchor="start", bold=True))
        y += 32

    p.append(line(90, y - 6, 660, y - 6, color="#e4e4e4", sw=1.2))
    p.append(text(cols[1], y + 16, "контрольна сума:", size=13, color=INK, anchor="start", bold=True))
    p.append(text(cols[2], y + 16, "sum1 = 21", size=13.5, color=INK, anchor="start", bold=True))
    p.append(text(cols[3], y + 16, "sum2 = 10", size=13.5, color=ACC, anchor="start", bold=True))

    p.append(line(50, y + 44, 650, y + 44, color="#e4e4e4", sw=1.4))
    p.append(text(50, y + 64, "Чому Флетчер ловить те, що проста сума пропускає:",
                  size=13, color=FIELD, anchor="start", bold=True))
    p.append(text(70, y + 86, "байт на позиції 1 доливає в sum2 на кожному з наступних кроків,",
                  size=12, color=INK, anchor="start"))
    p.append(text(70, y + 105, "а байт на позиції 4 — лише раз; тож переставлені байти дають іншу sum2.",
                  size=12, color=INK, anchor="start"))
    p.append(text(70, y + 126, "Ціна — вдвічі ширший підпис; виявлення натомість майже як у CRC.",
                  size=11.5, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "fletcher.svg"), W, H, *p,
           title="Флетчер: друга сума запам'ятовує позицію байта")


# ── internet-checksum: сума 16-бітних слів, загорнутий перенос, інверсія ───────
# Ідея: слова заголовка складаються у 32-бітний акумулятор; верхні біти
# (перенос) завертаються вниз, результат інвертується — і на приймачі сума всіх
# слів РАЗОМ із контрольною дає нуль.

def fig_internet_checksum():
    W, H = 720, 340
    p = []
    # стрічка слів
    words = ["0x4500", "0x003c", "0x1c46", "0x4000", "0x4006", "0x0000", "0x...."]
    bw, bh = 78, 34
    x = 40
    y = 92
    for i, w in enumerate(words):
        p.append(rect(x, y, bw, bh, fill="#eaf0ff", stroke=NEG, sw=1.4, rx=5))
        p.append(text(x + bw / 2, y + bh / 2 + 5, w, size=12, color=INK, bold=True))
        if i < len(words) - 1:
            p.append(text(x + bw + 4, y + bh / 2 + 5, "+", size=14, color=INK, bold=True))
        x += bw + 18
    p.append(text(40, y - 14, "16-бітні слова (тут — поля заголовка IPv4)", size=11, color=MUTED, anchor="start", italic=True))

    # крок 1: акумулятор
    b1, w1, h1 = textbox(W / 2, 168, "32-бітний акумулятор: складаємо всі слова",
                         size=12.5, bold=True, fill=FILL, stroke=INK, sw=1.6)
    p.append(b1)
    p.append(arrow(W / 2, y + bh + 4, W / 2, 168 - h1 / 2 - 2, color=INK, sw=1.6))

    # крок 2: загорнути перенос
    b2, w2, h2 = textbox(W / 2, 224, "загорнути перенос:  (s & 0xFFFF) + (s >> 16)",
                         size=12.5, bold=True, fill="#eef7f0", stroke=FIELD, sw=1.8, color=FIELD)
    p.append(b2)
    p.append(arrow(W / 2, 168 + h1 / 2, W / 2, 224 - h2 / 2 - 2, color=INK, sw=1.6))

    # крок 3: інверсія
    b3, w3, h3 = textbox(W / 2, 280, "інвертувати (~) → контрольна сума",
                         size=12.5, bold=True, fill="#fff8e8", stroke=ACC, sw=2.0, color=ACC)
    p.append(b3)
    p.append(arrow(W / 2, 224 + h2 / 2, W / 2, 280 - h3 / 2 - 2, color=INK, sw=1.6))

    p.append(text(W / 2, 318, "на приймачі додають усі слова РАЗОМ із сумою: правильний пакет дає 0x0000",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "internet-checksum.svg"), W, H, *p,
           title="Internet checksum: сума слів, загорнутий перенос, інверсія")


# ── fletcher-order: та сама трійка в двох порядках, sum2 різна ────────────────
# Ідея: sum1 однакова в обох порядках (їй порядок байдужий), а sum2 зважує байт
# позицією (×3, ×2, ×1), тож перестановка її зрушує.

def fig_fletcher_order():
    W, H = 720, 360
    p = []
    bw, bh, gap = 70, 38, 26

    def triple(y, vals, weights, label, col):
        p.append(text(60, y - 14, label, size=12, color=col, anchor="start", bold=True))
        x = 60
        for v, w in zip(vals, weights):
            p.append(rect(x, y, bw, bh, fill="#eaf0ff", stroke=NEG, sw=1.4, rx=5))
            p.append(text(x + bw / 2, y + bh / 2 + 5, v, size=14, color=INK, bold=True))
            p.append(text(x + bw / 2, y + bh + 16, "×%d" % w, size=11, color=ACC, bold=True))
            x += bw + gap
        return x

    triple(96, ["A", "B", "C"], [3, 2, 1], "порядок A B C:", FIELD)
    triple(216, ["B", "A", "C"], [3, 2, 1], "порядок B A C (переставлено):", POS)

    # підсумкові суми
    p.append(rect(360, 84, 300, 62, fill="#fafafa", stroke="#e4e4e4", sw=1.4, rx=6))
    p.append(text(376, 108, "sum1 = A+B+C", size=13, color=INK, anchor="start", bold=True))
    p.append(text(376, 130, "sum2 = 3A+2B+C", size=13, color=ACC, anchor="start", bold=True))

    p.append(rect(360, 204, 300, 62, fill="#fafafa", stroke="#e4e4e4", sw=1.4, rx=6))
    p.append(text(376, 228, "sum1 = B+A+C  (та сама!)", size=13, color=MUTED, anchor="start", bold=True))
    p.append(text(376, 250, "sum2 = 3B+2A+C  (інша!)", size=13, color=POS, anchor="start", bold=True))

    p.append(line(50, 296, 670, 296, color="#e4e4e4", sw=1.4))
    p.append(text(W / 2, 318, "sum1 порядку не бачить; sum2 зважує байт позицією — і ловить перестановку",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, 340, "готова сума Флетчера = (sum2 << 8) | sum1", size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "fletcher-order.svg"), W, H, *p,
           title="Чому Флетчер ловить перестановку, яку проста сума пропускає")


# ── matrix: що ловить кожен метод і де його сліпа пляма ───────────────────────
# Ідея: таблиця класів поломок × методів; видно, як ціна зростає разом із
# надійністю (проста сума → Internet → Флетчер → CRC).

def fig_matrix():
    W, H = 940, 470
    p = []
    methods = ["Проста\nсума 8-біт", "Internet\nchecksum 16", "Флетчер-16", "CRC-16"]
    mx = [320, 470, 620, 770]
    mw = 150
    for cx, m in zip(mx, methods):
        p.append(fitbox(cx, 92, mw, 48, m, size=12.5, fill="#eef2fb", stroke=NEG, sw=1.4, bold=True))

    GOOD, PART, BAD = "#1f8a3b", ACC, POS
    GFILL, PFILL, BFILL = "#eef7f0", "#faf3e0", "#fbeceb"
    rows = [
        ("Один перевернутий біт",        [(GOOD, GFILL, "✓"), (GOOD, GFILL, "✓"), (GOOD, GFILL, "✓"), (GOOD, GFILL, "✓")]),
        ("Кілька бітів в одному байті",  [(PART, PFILL, "~"), (GOOD, GFILL, "✓"), (GOOD, GFILL, "✓"), (GOOD, GFILL, "✓")]),
        ("Переставлені байти",           [(BAD, BFILL, "✗"), (BAD, BFILL, "✗"), (GOOD, GFILL, "✓"), (GOOD, GFILL, "✓")]),
        ("Вставлені / зайві нулі",       [(PART, PFILL, "~"), (PART, PFILL, "~"), (GOOD, GFILL, "✓"), (GOOD, GFILL, "✓")]),
        ("Серія підряд (burst) ≤ 16 біт",[(PART, PFILL, "~"), (PART, PFILL, "~"), (PART, PFILL, "~"), (GOOD, GFILL, "✓")]),
    ]
    ry = 148
    rh = 46
    for label, cells in rows:
        p.append(rect(70, ry, 250, rh, fill="#fafafa", stroke="#e4e4e4", sw=1.4, rx=6))
        p.append(text(82, ry + rh / 2 + 5, label, size=12, color=INK, anchor="start", bold=True))
        for cx, (col, fill, mark) in zip(mx, cells):
            p.append(rect(cx, ry, mw, rh, fill=fill, stroke=col, sw=1.4, rx=6))
            p.append(text(cx + mw / 2, ry + rh / 2 + 7, mark, size=19, color=col, bold=True))
        ry += rh

    # рядок ціни
    p.append(rect(70, ry, 250, rh, fill="#faf3e0", stroke=ACC, sw=1.4, rx=6))
    p.append(text(82, ry + rh / 2 + 5, "Ціна (час / код)", size=12, color=INK, anchor="start", bold=True))
    costs = ["найдешевше", "дешеве", "дешеве", "дорожче"]
    for cx, c in zip(mx, costs):
        p.append(rect(cx, ry, mw, rh, fill=BG, stroke="#e4e4e4", sw=1.2, rx=6))
        p.append(text(cx + mw / 2, ry + rh / 2 + 5, c, size=12, color=INK, bold=True))

    # легенда
    ly = ry + rh + 22
    p.append(text(70, ly, "✓", size=17, color=GOOD, anchor="start", bold=True))
    p.append(text(90, ly, "майже завжди ловить", size=12, color=INK, anchor="start"))
    p.append(text(300, ly, "~", size=17, color=PART, anchor="start", bold=True))
    p.append(text(318, ly, "ловить не все (є сліпі плями)", size=12, color=INK, anchor="start"))
    p.append(text(580, ly, "✗", size=17, color=BAD, anchor="start", bold=True))
    p.append(text(600, ly, "не бачить узагалі", size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "matrix.svg"), W, H, *p,
           title="Що ловить кожен метод — і де його сліпа пляма")


if __name__ == "__main__":
    fig_sum()
    fig_fletcher()
    fig_internet_checksum()
    fig_fletcher_order()
    fig_matrix()
    print("OK: figures written to", OUT)
