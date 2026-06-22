# -*- coding: utf-8 -*-
"""Фігури теми «Регістрова карта» (book/communications/buses/register-map).
Чистий Python без залежностей; svgkit імпортуємо зі scripts/, не переписуємо.
Усі приклади прив'язані до реального чіпа MPU-6050 (даташит InvenSense
RM-MPU-6000A): WHO_AM_I 0x75 = 0x68, PWR_MGMT_1 0x6B, ACCEL_CONFIG 0x1C
(AFS_SEL — біти 4:3), ACCEL_XOUT_H 0x3B, чутливість ±2g = 16384 LSB/g.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Регістрова карта: таблиця регістрів реального чіпа ────────────────────
# Ідея: карта = таблиця (адреса · назва · доступ · скидання · призначення),
# а її рядки діляться на чотири ролі (ID, налаштування, дані, стан).
def fig_map():
    W, H = 920, 430
    p = []
    p.append(text(W/2, 32, "Регістрова карта: таблиця регістрів чіпа", size=20, bold=True))
    p.append(text(W/2, 54, "адреса · назва · доступ · значення після скидання · призначення",
                  size=12.5, color=MUTED, italic=True))

    cols = [86, 190, 372, 452, 572]            # x-початки колонок
    head = ["адреса", "назва", "R/W", "скид.", "призначення"]
    hy = 92
    p.append(rect(70, hy, 780, 30, fill="#eef1f4", stroke=MUTED, sw=1.2, rx=5))
    for cx, h in zip(cols, head):
        p.append(text(cx, hy+20, h, size=11.5, anchor="start", bold=True))

    rows = [
        ("0x75", "WHO_AM_I", "R",   "0x68", "сталий код чіпа — звірити, що це він", "id"),
        ("0x6B", "PWR_MGMT_1", "R/W", "0x40", "сон / пробудження, джерело такту",   "cfg"),
        ("0x1C", "ACCEL_CONFIG", "R/W", "0x00", "діапазон прискорення (біти 4:3)",  "cfg"),
        ("0x3B", "ACCEL_XOUT_H", "R", "0x00", "вимір осі X, старший байт",          "data"),
        ("0x3C", "ACCEL_XOUT_L", "R", "0x00", "вимір осі X, молодший байт",         "data"),
        ("0x3A", "INT_STATUS", "R",  "0x00", "готовність нового виміру",            "stat"),
    ]
    name_color = {"id": NEG, "cfg": "#b07a00", "data": FIELD, "stat": INK}
    y = hy + 30
    rh = 38
    for addr, name, rw, rst, desc, role in rows:
        p.append(rect(70, y, 780, rh, fill=BG, stroke="#c8ccd0", sw=1.0, rx=0))
        p.append(text(cols[0], y+24, addr, size=11.5, color="#a85c00", anchor="start", bold=True))
        p.append(text(cols[1], y+24, name, size=11.5, color=name_color[role], anchor="start", bold=True))
        p.append(text(cols[2], y+24, rw, size=11.5, anchor="start"))
        p.append(text(cols[3], y+24, rst, size=11.5, color=MUTED, anchor="start"))
        p.append(text(cols[4], y+24, desc, size=10.8, anchor="start"))
        y += rh

    by = y + 8
    p.append(rect(60, by, 800, 44, fill="#eef6ef", stroke=FIELD, sw=1.3, rx=10))
    p.append(text(W/2, by+27,
                  "Чотири ролі рядків: ID (перевірка) · CONFIG/PWR (налаштування) · DATA (виміри) · STATUS (стан).",
                  size=11.5, bold=True))
    render(os.path.join(OUT, "register-map.svg"), W, H, *p)


# ── 2. Бітові поля: один байт пакує кілька налаштувань ──────────────────────
# Ідея: ACCEL_CONFIG — це не «одне значення», а набір полів по бітах;
# щоб змінити одне, не зачепивши інших, потрібен read-modify-write.
def fig_bitfields():
    W, H = 920, 380
    p = []
    p.append(text(W/2, 32, "Один регістр — кілька полів: біти ACCEL_CONFIG", size=19.5, bold=True))
    p.append(text(W/2, 54, "у байт напхано кілька параметрів; кожен займає свої біти",
                  size=12.5, color=MUTED, italic=True))

    # 8 клітинок бітів b7..b0
    cells = [
        ("b7", "ST", POS),  ("b6", "ST", POS),  ("b5", "ST", POS),
        ("b4", "AFS", "#b07a00"), ("b3", "AFS", "#b07a00"),
        ("b2", "—", MUTED), ("b1", "—", MUTED), ("b0", "—", MUTED),
    ]
    cw, ch, x0, yb = 76, 50, 150, 110
    for i, (lbl, txt, col) in enumerate(cells):
        x = x0 + i*cw
        p.append(rect(x, yb, cw, ch, fill=BG, stroke=col, sw=1.8, rx=4))
        p.append(text(x+cw/2, yb+ch/2+5, txt, size=11, color=col, bold=True))
        p.append(text(x+cw/2, yb-8, lbl, size=10, color=MUTED))
    # підписи полів
    p.append(text(x0+cw*1.5, yb+ch+24, "ST: самоперевірка (3 біти)", size=10.5, color=POS, bold=True))
    p.append(text(x0+cw*3.5, yb+ch+24, "AFS: діапазон (2 біти)", size=10.5, color="#b07a00", bold=True))
    p.append(text(x0+cw*6.5, yb+ch+24, "— : не задіяні", size=10.5, color=MUTED, bold=True))

    # пояснення read-modify-write
    bx, by = 60, 220
    p.append(rect(bx, by, 800, 130, fill="#f2f4f6", stroke=MUTED, sw=1.3, rx=10))
    p.append(text(W/2, by+26, "Щоб змінити ОДНЕ поле, не зачепивши решти, роблять «читай-зміни-запиши»:",
                  size=12, bold=True))
    steps = [
        "1. прочитати поточний байт регістра;",
        "2. замаскувати потрібні біти (AND з ~маска) і вставити нове значення (OR);",
        "3. записати байт назад — решта налаштувань збереглася.",
    ]
    for i, s in enumerate(steps):
        p.append(text(bx+22, by+54+i*24, s, size=11.5, anchor="start"))
    render(os.path.join(OUT, "bitfields.svg"), W, H, *p)


# ── 3. Універсальний рецепт оживлення: 4 кроки ──────────────────────────────
# Ідея: скан → who_am_i → налаштувати → читати; перші три раз, четвертий у циклі.
def fig_recipe():
    W, H = 940, 360
    p = []
    p.append(text(W/2, 32, "Універсальний рецепт «оживлення» I2C-чіпа", size=19, bold=True))
    p.append(text(W/2, 54, "ті самі чотири кроки працюють майже для кожного давача",
                  size=12.5, color=MUTED, italic=True))

    boxes = [
        ("1. СКАН", ["знайти адресу", "на шині"], NEG),
        ("2. WHO_AM_I", ["звірити ID —", "це справді він?"], "#b07a00"),
        ("3. НАЛАШТУВАТИ", ["розбудити, задати", "діапазон, частоту"], FIELD),
        ("4. ЧИТАТИ", ["пакетом виміри,", "скласти й масштабувати"], INK),
    ]
    bw, bh, y = 195, 90, 130
    xs = [60, 285, 510, 735]
    for i, ((title, lines, col), x) in enumerate(zip(boxes, xs)):
        p.append(rect(x, y, bw, bh, fill="#fbfcfd", stroke=col, sw=2.2, rx=12))
        p.append(text(x+bw/2, y+28, title, size=13, color=col, bold=True))
        for j, ln in enumerate(lines):
            p.append(text(x+bw/2, y+52+j*16, ln, size=10.5))
        if i < 3:
            p.append(arrow(x+bw+2, y+bh/2, x+bw+28, y+bh/2, color=INK, sw=2))
    # петля на 4-му кроці
    cx = xs[3]+bw/2
    p.append('<path d="M %.1f,%d C %.1f,270 %d,270 %d,222" fill="none" stroke="%s" '
             'stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#arrow)"/>'
             % (cx, y+bh, cx, xs[3]+bw-10, xs[3]+bw-10, INK))
    p.append(text(cx, y+bh+66, "повторювати в циклі", size=10.5, color=MUTED, italic=True))

    by = 300
    p.append(rect(60, by, 820, 44, fill="#eef6ef", stroke=FIELD, sw=1.3, rx=10))
    p.append(text(W/2, by+27,
                  "Перші три кроки — раз при старті; четвертий — у головному циклі стільки разів, скільки треба.",
                  size=11.5, bold=True))
    render(os.path.join(OUT, "recipe.svg"), W, H, *p)


# ── 4. WHO_AM_I: перша перевірка ────────────────────────────────────────────
# Ідея: один обмін відділяє «чіп живий» від «біда з підключенням».
def fig_whoami():
    W, H = 900, 350
    p = []
    p.append(text(W/2, 32, "WHO_AM_I: найперша перевірка перед будь-чим", size=19.5, bold=True))
    p.append(text(W/2, 54, "прочитати сталий ID-регістр і звірити з очікуваним",
                  size=12.5, color=MUTED, italic=True))

    p.append(rect(80, 100, 320, 130, fill="none", stroke="#e0e0e0", sw=2, rx=12))
    p.append(text(240, 126, "читаємо 0x75 (WHO_AM_I)", size=12, bold=True))
    p.append(text(240, 160, "очікуємо: 0x68", size=12.5, color=MUTED))
    p.append(text(240, 196, "отримали: 0x68 ✓", size=13, color=FIELD, bold=True))

    p.append(arrow(410, 165, 478, 165, color=FIELD, sw=2.4))
    p.append(rect(490, 120, 330, 90, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    p.append(text(655, 150, "збіглося →", size=12.5, color=FIELD, bold=True))
    p.append(text(655, 174, "це той чіп, адреса й дроти справні", size=11.5, bold=True))
    p.append(text(655, 196, "можна налаштовувати далі", size=10.5, color=MUTED))

    p.append(rect(60, 250, 780, 80, fill="#fbecec", stroke=POS, sw=1.4, rx=10))
    p.append(text(W/2, 276,
                  "Не збіглося (0x00, 0xFF, інше) → не починай налаштування: спершу розберись із дротами й адресою.",
                  size=12, bold=True))
    p.append(text(W/2, 298,
                  "0xFF на всіх регістрах — типова ознака обірваної лінії; 0x00 — часто відсутнє живлення.",
                  size=11, color=MUTED, italic=True))
    p.append(text(W/2, 318,
                  "Один обмін відділяє «чіп живий» від «щось із підключенням».",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "whoami.svg"), W, H, *p)


# ── 5. Читай-зміни-запиши: бітова арифметика на прикладі ────────────────────
# Ідея: AND з ~маска обнуляє поле, OR вставляє нове; решта байта недоторкана.
def fig_rmw():
    W, H = 920, 360
    p = []
    p.append(text(W/2, 32, "Читай-зміни-запиши: змінити одне поле, решту лишити", size=18.5, bold=True))
    p.append(text(W/2, 54, "ставимо діапазон AFS = 10, а решту бітів не чіпаємо",
                  size=12.5, color=MUTED, italic=True))

    # три ряди по 8 біт: прочитали 0x1A, маска поля, результат 0x12
    bx0, cw, bw = 250, 46, 46
    def bitrow(y, label, bits, mark, tail, tail_col=INK):
        out = [text(bx0-16, y+24, label, size=11.5, anchor="end", bold=True)]
        for i, b in enumerate(bits):
            x = bx0 + i*cw
            on = mark[i]
            fill = "#fbecec" if on else BG
            stroke = POS if on else "#9aa0a6"
            col = POS if on else INK
            out.append(rect(x, y, bw, 36, fill=fill, stroke=stroke, sw=1.4, rx=0))
            out.append(text(x+bw/2, y+24, str(b), size=12, color=col, bold=True))
        out.append(text(bx0+8*cw+10, y+24, tail, size=12, color=tail_col, anchor="start", bold=True))
        return out

    z = [0,0,0,0,0,0,0,0]
    # 0x1A = 0001 1010
    p += bitrow(100, "прочитали:", [0,0,0,1,1,0,1,0], z, "= 0x1A")
    # маска поля 4:3 = 0001 1000
    p += bitrow(160, "поле 4:3:", [0,0,0,1,1,0,0,0], [0,0,0,1,1,0,0,0], "біти діапазону", "#b07a00")
    # результат 0x12 = 0001 0010
    p += bitrow(220, "результат:", [0,0,0,1,0,0,1,0], [0,0,0,1,1,0,0,0], "= 0x12 (AFS=10)", FIELD)

    p.append(rect(60, 280, 800, 56, fill="#f2f4f6", stroke=MUTED, sw=1.3, rx=10))
    p.append(text(W/2, 304,
                  "reg = (reg & ~0x18) | (0b10 << 3);  — обнулити старе поле, вставити нове, решта недоторкана.",
                  size=12, bold=True))
    p.append(text(W/2, 324,
                  "Сліпо записати весь байт означало б випадково перезатерти інші налаштування.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "rmw.svg"), W, H, *p)


# ── 6. Сирий відлік → фізична величина через масштаб ────────────────────────
# Ідея: counts самі по собі нічого не значать; даташит дає чутливість.
def fig_scale():
    W, H = 900, 350
    p = []
    p.append(text(W/2, 32, "Сирий відлік → фізична величина: масштаб із даташита", size=19, bold=True))
    p.append(text(W/2, 54, "чіп віддає «голі» числа; даташит дає чутливість для переведення",
                  size=12.5, color=MUTED, italic=True))

    p.append(rect(120, 100, 200, 70, fill="#e9eefb", stroke=NEG, sw=2, rx=8))
    p.append(text(220, 130, "сирий int16", size=11, color=MUTED))
    p.append(text(220, 154, "8192", size=17, bold=True))
    p.append(arrow(322, 135, 390, 135, color=FIELD, sw=2.4))
    p.append(text(357, 122, "÷ чутливість", size=10.5, color=FIELD, bold=True))
    p.append(rect(400, 100, 230, 70, fill="#fbfcfd", stroke=MUTED, sw=1.6, rx=8))
    p.append(text(515, 128, "16384 LSB/g", size=12.5, bold=True))
    p.append(text(515, 152, "(з даташита, ±2g)", size=10, color=MUTED))
    p.append(arrow(632, 135, 700, 135, color=FIELD, sw=2.4))
    p.append(rect(710, 100, 150, 70, fill="#eef6ef", stroke=FIELD, sw=2, rx=8))
    p.append(text(785, 138, "0.5 g", size=18, color=FIELD, bold=True))

    p.append(rect(60, 200, 780, 130, fill="#f2f4f6", stroke=MUTED, sw=1.3, rx=10))
    p.append(text(W/2, 226, "величина = сирий_відлік / чутливість = 8192 / 16384 = 0.5 g",
                  size=13.5, bold=True))
    p.append(text(W/2, 252,
                  "для гіроскопа — LSB/(°/с), для барометра — свої формули, для температури — зсув і масштаб.",
                  size=11.5))
    p.append(text(W/2, 276,
                  "Часто ще потрібне калібрування (прибрати зсув нуля): відлік → масштаб → калібрування.",
                  size=11.5, color=MUTED, italic=True))
    p.append(text(W/2, 300,
                  "Без масштабу «8192» нічого не означає; саме даташит робить із відліку фізику.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "scale.svg"), W, H, *p)


# ── 7. Протокол + даташит = розмова з будь-яким чіпом ────────────────────────
def fig_mindset():
    W, H = 900, 340
    p = []
    p.append(text(W/2, 32, "Протокол + даташит = розмова з будь-яким чіпом", size=18.5, bold=True))
    p.append(text(W/2, 54, "механіка I2C однакова для всіх; даташит підставляє адресу, регістри й масштаби",
                  size=12.5, color=MUTED, italic=True))

    p.append(rect(80, 100, 320, 120, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    p.append(text(240, 128, "протокол I2C", size=13.5, color=FIELD, bold=True))
    p.append(text(240, 150, "(універсальний)", size=10.5, color=MUTED))
    p.append(text(100, 176, "старт · адреса · R/W · ACK", size=11, anchor="start"))
    p.append(text(100, 198, "регістри · повторний старт · пакет", size=11, anchor="start"))

    p.append(text(420, 167, "+", size=26, bold=True))

    p.append(rect(470, 100, 350, 120, fill="#e9eefb", stroke=NEG, sw=2, rx=12))
    p.append(text(645, 128, "даташит чіпа", size=13.5, color=NEG, bold=True))
    p.append(text(645, 150, "(специфічний для пристрою)", size=10.5, color=MUTED))
    p.append(text(490, 176, "адреса · карта регістрів", size=11, anchor="start"))
    p.append(text(490, 198, "біти налаштувань · масштаби", size=11, anchor="start"))

    p.append(rect(60, 244, 780, 80, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=10))
    p.append(text(W/2, 270,
                  "Знаючи протокол, нову мікросхему вмикаєш швидко: відкрив даташит, знайшов адресу й регістри — і говориш.",
                  size=11.5, bold=True))
    p.append(text(W/2, 292,
                  "Суть уміння: не завчити один давач, а вміти прочитати й оживити будь-який.",
                  size=11.5, bold=True))
    p.append(text(W/2, 312,
                  "Готові бібліотеки — зручність, але тепер видно, що саме вони роблять усередині.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "mindset.svg"), W, H, *p)


if __name__ == "__main__":
    fig_map()
    fig_bitfields()
    fig_recipe()
    fig_whoami()
    fig_rmw()
    fig_scale()
    fig_mindset()
    print("ok: 7 figures ->", OUT)
