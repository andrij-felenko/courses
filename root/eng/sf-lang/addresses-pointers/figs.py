# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

RED, BLUE, GREEN, GREY = POS, NEG, FIELD, MUTED


# ── pointer: дві комірки — у x дані, у p адреса x ─────────────────────────────
# Ідея: показати наочно «де/що»: змінна тримає значення, покажчик — адресу,
# і стрілка веде від покажчика до змінної, на яку він указує.

def fig_pointer():
    W, H = 700, 250
    p = []
    yb = 120
    bw, bh = 130, 44

    # покажчик p (ліворуч)
    px = 90
    p.append(text(px + bw / 2, yb - 18, "покажчик p", size=12, color=RED, bold=True))
    p.append(rect(px, yb, bw, bh, fill="#fdf4f4", stroke=RED, sw=2, rx=4))
    p.append(text(px - 8, yb + bh / 2 + 4, "0x10", size=10, color=GREY, anchor="end", bold=True))
    p.append(text(px + bw / 2, yb + bh / 2 + 5, "0x20", size=14, color=INK, bold=True))
    p.append(text(px + bw / 2, yb + bh + 20, "значення p = адреса x", size=10, color=GREY, italic=True))

    # змінна x (праворуч)
    xx = 480
    p.append(text(xx + bw / 2, yb - 18, "змінна x", size=12, color=GREEN, bold=True))
    p.append(rect(xx, yb, bw, bh, fill="#eef7ee", stroke=GREEN, sw=2, rx=4))
    p.append(text(xx - 8, yb + bh / 2 + 4, "0x20", size=10, color=GREY, anchor="end", bold=True))
    p.append(text(xx + bw / 2, yb + bh / 2 + 5, "42", size=15, color=INK, bold=True))
    p.append(text(xx + bw / 2, yb + bh + 20, "значення x = самі дані", size=10, color=GREY, italic=True))

    # стрілка p → x
    p.append(arrow(px + bw + 4, yb + bh / 2, xx - 4, yb + bh / 2, color=RED, sw=2.4))
    p.append(text((px + bw + xx) / 2, yb + bh / 2 - 12, "p вказує на x", size=11, color=RED, bold=True))

    render(os.path.join(OUT, "pointer.svg"), W, H, *p,
           title="Покажчик тримає адресу x; сам x тримає дані")


# ── ops: дві зворотні операції & і * ─────────────────────────────────────────
# Ідея: & веде від значення до адреси, * — назад; підкреслено, що через *p
# можна не лише читати, а й писати чужу змінну.

def fig_ops():
    W, H = 700, 280
    p = []
    cw, ch = 300, 110

    # ліва картка: & — адреса від
    lx = 40
    p.append(rect(lx, 60, cw, ch, fill="#f3f5fd", stroke=BLUE, sw=1.8, rx=10))
    p.append(text(lx + cw / 2, 86, "&  —  «адреса від»", size=12, color=BLUE, bold=True))
    p.append(text(lx + cw / 2, 116, "&x  →  0x20", size=16, color=INK, bold=True))
    p.append(text(lx + cw / 2, 140, "дай, ДЕ лежить x", size=10.5, color=GREY))
    p.append(text(lx + cw / 2, 160, "p = &x  — так націлюють покажчик", size=10, color=BLUE, bold=True))

    # права картка: * — розіменування
    rx = 360
    p.append(rect(rx, 60, cw, ch, fill="#eef7ee", stroke=GREEN, sw=1.8, rx=10))
    p.append(text(rx + cw / 2, 86, "*  —  «розіменування»", size=12, color=GREEN, bold=True))
    p.append(text(rx + cw / 2, 116, "*p  →  42", size=16, color=INK, bold=True))
    p.append(text(rx + cw / 2, 140, "піди за p і візьми значення", size=10.5, color=GREY))
    p.append(text(rx + cw / 2, 160, "*p = 99  — так МІНЯЮТЬ x через p", size=10, color=GREEN, bold=True))

    # зворотність унизу
    p.append(arrow(250, 205, 450, 205, color=BLUE, sw=2))
    p.append(text(350, 198, "&  (значення → адреса)", size=10.5, color=BLUE, bold=True))
    p.append(arrow(450, 235, 250, 235, color=GREEN, sw=2))
    p.append(text(350, 256, "*  (адреса → значення)", size=10.5, color=GREEN, bold=True))
    p.append(text(150, 222, "значення x", size=11, color=INK, bold=True))
    p.append(text(550, 222, "адреса в p", size=11, color=RED, bold=True))

    render(os.path.join(OUT, "ops.svg"), W, H, *p,
           title="Дві зворотні операції: взяти адресу (&) і піти за нею (*)")


# ── number: покажчик — просто число-адреса, тип лише для компілятора ──────────
# Ідея: те саме число-адреса; «тип» каже компілятору розмір кроку й скільки
# байтів читати, а саме число — як будь-яке інше.

def fig_number():
    W, H = 700, 250
    p = []

    # центральне число-адреса
    b, bw, bh = textbox(W / 2, 90, "0x2000  —  лише адреса-число", size=14, bold=True,
                        fill=FILL, stroke=INK, sw=2, pad=14)
    p.append(b)
    p.append(text(W / 2, 90 + bh / 2 + 16, "на 32-бітній машині — 4 байти, як будь-яке інше число",
                  size=10.5, color=GREY, italic=True))

    # дві лінзи типу
    ly = 175
    lw = 300
    p.append(rect(40, ly - 22, lw, 50, fill="#f3f5fd", stroke=BLUE, sw=1.6, rx=8))
    p.append(text(40 + lw / 2, ly - 4, "int*  →  читати 4 байти", size=11.5, color=BLUE, bold=True))
    p.append(text(40 + lw / 2, ly + 16, "крок p+1 зсуває на 4 байти", size=10, color=GREY))

    p.append(rect(360, ly - 22, lw, 50, fill="#eef7ee", stroke=GREEN, sw=1.6, rx=8))
    p.append(text(360 + lw / 2, ly - 4, "char*  →  читати 1 байт", size=11.5, color=GREEN, bold=True))
    p.append(text(360 + lw / 2, ly + 16, "крок p+1 зсуває на 1 байт", size=10, color=GREY))

    p.append(text(W / 2, 235, "тип потрібен КОМПІЛЯТОРУ (скільки читати, який крок), не самому числу",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "number.svg"), W, H, *p,
           title="Покажчик — це просто число-адреса плюс тип")


# ── analogy: адреса будинку на папірці ───────────────────────────────────────
# Ідея: папірець з адресою — не будинок; його можна копіювати, передавати,
# піти за ним; ламається на старій/хибній адресі.

def fig_analogy():
    W, H = 700, 280
    p = []

    # папірець (покажчик)
    px, py = 70, 110
    p.append(rect(px, py, 150, 56, fill="#fffdf2", stroke=RED, sw=1.8, rx=4))
    p.append(text(px + 75, py - 12, "папірець (покажчик)", size=11, color=RED, bold=True))
    p.append(text(px + 75, py + 26, "адреса:", size=10.5, color=GREY))
    p.append(text(px + 75, py + 44, "вул. Пам'яті, 0x20", size=11.5, color=INK, bold=True))

    # будинок (дані)
    hx, hy = 470, 104
    p.append(rect(hx, hy, 150, 70, fill="#eef7ee", stroke=GREEN, sw=1.8, rx=4))
    p.append(text(hx + 75, hy - 12, "будинок (дані)", size=11, color=GREEN, bold=True))
    p.append(text(hx + 75, hy + 32, "0x20", size=11, color=GREY))
    p.append(text(hx + 75, hy + 52, "42", size=16, color=INK, bold=True))

    p.append(arrow(px + 152, py + 28, hx - 4, hy + 35, color=RED, sw=2.2))
    p.append(text(W / 2, 100, "«піди за адресою» = розіменування", size=10.5, color=RED, bold=True))

    # три дії з папірцем
    p.append(text(W / 2, 210, "копіювати папірець (два → той самий будинок · кілька покажчиків на ті самі дані)",
                  size=10.5, color=INK))
    p.append(text(W / 2, 230, "дати другові (піде за адресою й перефарбує будинок · функція змінить ваші дані)",
                  size=10.5, color=INK))
    p.append(text(W / 2, 256, "ламається: стара / хибна адреса → знесений чи чужий будинок (висячий / дикий)",
                  size=10.5, color=RED, bold=True))

    render(os.path.join(OUT, "analogy.svg"), W, H, *p,
           title="Покажчик — це адреса будинку, записана на папірці")


# ── uses: чотири застосунки непрямості ───────────────────────────────────────
# Ідея: одна ідея (тримати вказівку, не значення) дає чотири різні вигоди.

def fig_uses():
    W, H = 700, 250
    p = []
    cells = [
        (185, 95, "передати без копіювання", "велику структуру шлють\nза адресою (кілька байтів)", BLUE),
        (515, 95, "змінити чужу змінну", "функція пише в неї\nчерез *p — «вернути назовні»", GREEN),
        (185, 185, "пройти масив / пам'ять", "p+1, p+2 … крокують\nпо сусідніх комірках", RED),
        (515, 185, "зв'язані структури", "комірка тримає адресу\nнаступної → списки, дерева", "#8a5fb0"),
    ]
    for cx, cy, head, body, col in cells:
        b, bw, bh = textbox(cx, cy + 8, body, size=10.5, pad=10, fill="#fafafa",
                            stroke=col, sw=1.6, color=INK, min_w=270)
        p.append(b)
        p.append(text(cx, cy - bh / 2 - 4, head, size=11.5, color=col, bold=True))

    render(os.path.join(OUT, "uses.svg"), W, H, *p,
           title="Навіщо покажчики: чотири вигоди однієї непрямості")


# ── dangers: три зламані покажчики ───────────────────────────────────────────
# Ідея: нульовий → нікуди, висячий → недійсна пам'ять, дикий → випадкова;
# на МК без захисту пам'яті будь-який тихо псує сусіднє.

def fig_dangers():
    W, H = 700, 280
    p = []
    cards = [
        (130, "нульовий (null)", "адреса 0 — указує\n«в нікуди»; піти за\nним → аварія", BLUE),
        (350, "висячий (dangling)", "вказує на вже\nнедійсну пам'ять\n(звільнену) → сміття", RED),
        (570, "дикий (wild)", "неініціалізований —\nвипадкова адреса →\nпсує випадкову пам'ять", "#8a5fb0"),
    ]
    for cx, head, body, col in cards:
        b, bw, bh = textbox(cx, 110, body, size=10.5, pad=10, fill="#fafafa",
                            stroke=col, sw=1.7, color=INK, min_w=190)
        p.append(b)
        p.append(text(cx, 110 - bh / 2 - 8, head, size=12, color=col, bold=True))

    # смуга-попередження про МК
    p.append(rect(40, 190, 620, 64, fill="#fdf4f4", stroke=RED, sw=1.6, rx=8))
    p.append(text(W / 2, 214, "На МК немає захисту пам'яті: хибний покажчик тихо «надряпає» поверх коду,",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 234, "чужих даних чи регістра периферії (він теж на адресі!) — і чип збоїть загадково.",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "dangers.svg"), W, H, *p,
           title="Три зламані покажчики: нульовий, висячий, дикий")


# ─────────────────────────────────────────────────────────────────────────────
# Фігури вставки proj-pointer-arithmetic.md (та сама тека теми)
# ─────────────────────────────────────────────────────────────────────────────

# ── scaling: p+1 рахується в елементах, не в байтах ──────────────────────────

def fig_scaling():
    W, H = 700, 300
    p = []
    ox = 70
    cell = 34
    ytop = 90

    # стрічка пам'яті — 12 байтів
    p.append(text(W / 2, 70, "пам'ять, той самий початок  p = 0x1000", size=12, color=INK, bold=True))
    for i in range(12):
        x = ox + i * cell
        p.append(rect(x, ytop, cell, 34, fill="#fafafa", stroke=GREY, sw=1.0, rx=0))
        p.append(text(x + cell / 2, ytop - 8, "%X" % (0x1000 + i & 0xF), size=9, color=GREY))

    # char*: крок 1 байт
    cy = 175
    p.append(text(ox, cy - 18, "char*  —  крок 1 байт:", size=11, color=GREEN, anchor="start", bold=True))
    p.append(circle(ox + 0 * cell + cell / 2, ytop + 17, 5, fill=GREEN, stroke=GREEN, sw=1))
    p.append(arrow(ox + 0 * cell + cell / 2, cy, ox + 1 * cell + cell / 2, cy, color=GREEN, sw=2))
    p.append(text(ox + 1.6 * cell, cy - 6, "p+1 → 0x1001", size=10.5, color=GREEN, anchor="start", bold=True))

    # int*: крок 4 байти
    iy = 240
    p.append(text(ox, iy - 18, "int*  —  крок 4 байти:", size=11, color=BLUE, anchor="start", bold=True))
    p.append(arrow(ox + 0 * cell + cell / 2, iy, ox + 4 * cell + cell / 2, iy, color=BLUE, sw=2))
    p.append(text(ox + 4.6 * cell, iy - 6, "p+1 → 0x1004", size=10.5, color=BLUE, anchor="start", bold=True))

    p.append(text(W / 2, 285, "байтовий зсув = індекс × sizeof(*p)   ·   тому  a[i] ≡ *(a + i)",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "scaling.svg"), W, H, *p,
           title="Крок p+1 міряється в елементах, не в байтах")


# ── casts: приведення міняє лінзу й крок, не адресу ──────────────────────────

def fig_casts():
    W, H = 700, 300
    p = []

    # одне ціле за адресою 0x2000
    p.append(text(W / 2, 66, "одне ціле  0x12345678  за адресою 0x2000", size=12, color=INK, bold=True))
    ox = 250
    bw = 50
    bytes_ = ["78", "56", "34", "12"]
    for i, bv in enumerate(bytes_):
        x = ox + i * bw
        p.append(rect(x, 84, bw, 36, fill="#fafafa", stroke=GREY, sw=1.0, rx=0))
        p.append(text(x + bw / 2, 106, bv, size=12, color=INK, bold=True))
    p.append(text(ox, 132, "молодший", size=9, color=GREY, anchor="start"))
    p.append(text(ox + 4 * bw, 132, "старший", size=9, color=GREY, anchor="end"))

    # лінза int*
    p.append(rect(60, 165, 280, 48, fill="#f3f5fd", stroke=BLUE, sw=1.6, rx=8))
    p.append(text(200, 184, "крізь int*:  *p → одне число", size=11, color=BLUE, bold=True))
    p.append(text(200, 203, "0x12345678", size=11, color=INK, bold=True))

    # лінза char*
    p.append(rect(360, 165, 280, 48, fill="#eef7ee", stroke=GREEN, sw=1.6, rx=8))
    p.append(text(500, 184, "крізь char*:  *q → молодший байт", size=10.5, color=GREEN, bold=True))
    p.append(text(500, 203, "0x78  (little-endian)", size=11, color=INK, bold=True))

    # дозволено / UB
    p.append(text(200, 248, "можна: оглядати байти через char*,", size=10, color=GREEN, bold=True))
    p.append(text(200, 266, "ходити через void*", size=10, color=GREEN, bold=True))
    p.append(text(500, 248, "UB: читати об'єкт крізь чужий тип", size=10, color=RED, bold=True))
    p.append(text(500, 266, "(strict aliasing) · int* на непідрівняну адресу", size=10, color=RED, bold=True))

    render(os.path.join(OUT, "casts.svg"), W, H, *p,
           title="Приведення покажчика міняє крок і лінзу, а не адресу")


# ── mistakes: каталог класичних помилок ──────────────────────────────────────

def fig_mistakes():
    W, H = 700, 320
    p = []

    # два корені
    p.append(rect(60, 70, 280, 46, fill="#fdf4f4", stroke=RED, sw=1.8, rx=8))
    p.append(text(200, 90, "корінь 1: «адреса не туди»", size=11.5, color=RED, bold=True))
    p.append(text(200, 108, "вихід за межу · висячий · дикий", size=10, color=INK))

    p.append(rect(360, 70, 280, 46, fill="#f3f5fd", stroke=BLUE, sw=1.8, rx=8))
    p.append(text(500, 90, "корінь 2: «крок не той»", size=11.5, color=BLUE, bold=True))
    p.append(text(500, 108, "плутанина байт/елемент · поза масивом", size=9.5, color=INK))

    # специфічні для C/МК
    rows = [
        "непідрівняний доступ  →  HardFault на Cortex-M",
        "порушення strict aliasing  →  оптимізатор викидає доступи",
        "подвійне free та витоки купи",
    ]
    for i, r in enumerate(rows):
        y = 160 + i * 34
        p.append(rect(110, y, 480, 26, fill="#fafafa", stroke=GREY, sw=1.2, rx=6))
        p.append(text(W / 2, y + 17, r, size=10.5, color=INK))

    p.append(rect(40, 272, 620, 36, fill="#fdf4f4", stroke=RED, sw=1.5, rx=8))
    p.append(text(W / 2, 294, "На МК без захисту пам'яті жодна не дає чесної аварії — псування тихе.",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "mistakes.svg"), W, H, *p,
           title="Класичні помилки покажчиків зводяться до двох коренів")


if __name__ == "__main__":
    fig_pointer()
    fig_ops()
    fig_number()
    fig_analogy()
    fig_uses()
    fig_dangers()
    fig_scaling()
    fig_casts()
    fig_mistakes()
    print("OK: figures written to", OUT)
