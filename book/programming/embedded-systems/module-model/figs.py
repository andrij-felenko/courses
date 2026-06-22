# -*- coding: utf-8 -*-
"""Фігури до теми «Модель модуля».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b9770e"   # захист / увага (тепле, але читабельне)


# ── 1. Модуль як «чорна скринька»: думай про піни, не про нутрощі ────────────
def fig_blackbox():
    W, H = 720, 340
    f = [text(W / 2, 30, "Модуль — «чорна скринька»: важать піни, не нутрощі",
              size=16, bold=True)]

    # сам модуль
    f.append(rect(90, 96, 230, 188, fill=FILL, stroke=INK, sw=2, rx=12))
    f.append(text(205, 128, "МОДУЛЬ", size=15, color=INK, bold=True))
    f.append(text(205, 148, "(давач / периферія)", size=10, color=MUTED))
    f.append(text(205, 206, "усередині:", size=10, color=MUTED))
    f.append(text(205, 226, "транзистори? чіп?", size=12, color=INK, bold=True))
    f.append(text(205, 246, "— нам байдуже", size=10, color=MUTED, italic=True))

    # живлення зліва
    f.append(line(90, 140, 44, 140, color=POS, sw=2.4))
    f.append(text(40, 144, "VCC", size=10, color=POS, anchor="end", bold=True))
    f.append(line(90, 252, 44, 252, color=NEG, sw=2.4))
    f.append(text(40, 256, "GND", size=10, color=NEG, anchor="end", bold=True))

    # сигнал праворуч у МК
    f.append(circle(320, 190, 4, fill=INK, stroke=INK, sw=0))
    f.append(text(326, 180, "OUT (сигнал)", size=10, color=INK, anchor="start", bold=True))
    f.append(arrow(324, 190, 470, 190, color=INK, sw=2.2))

    f.append(rect(470, 132, 200, 116, fill="none", stroke=NEG, sw=2, rx=12))
    f.append(text(570, 158, "мікроконтролер", size=12, color=NEG, bold=True))
    f.append(text(570, 196, "читає один біт:", size=10, color=INK))
    f.append(text(570, 216, "є сигнал / нема", size=11, color=INK, bold=True))

    # нижня плашка-думка
    f.append(fitbox(110, 300, 500, 28,
                    "Те саме приховування, що з функцією в коді чи регістром: нутрощі — за інтерфейсом.",
                    size=11, fill="#fdf6e3", stroke=GOLD, sw=1.3, bold=True))
    render(os.path.join(IMG, "blackbox.svg"), W, H, *f)


# ── 2. Чотири питання для будь-якого з'єднання ───────────────────────────────
def fig_four_questions():
    W, H = 760, 380
    f = [text(W / 2, 28, "Чотири питання, щоб під'єднати будь-який модуль",
              size=16, bold=True)]

    cards = [
        ("1 · Живлення", POS, "Яка напруга —", "3.3 чи 5 В?",
         "сумісність рівнів;", "ESP32 не 5-В-терпимий"),
        ("2 · Напрям", NEG, "Жене сам", "чи «відпускає»?",
         "push-pull → прямо;", "ключ → підтяжка"),
        ("3 · Логіка", FIELD, "Активний рівень —", "1 чи 0?",
         "active-high / -low;", "що читати в коді"),
        ("4 · Захист", GOLD, "Струми й пороги", "в нормі?",
         "послідовний R,", "межі струму, діоди"),
    ]
    x0, cw, gap, top, ch = 30, 165, 12, 72, 232
    for i, (ttl, col, l1, l2, s1, s2) in enumerate(cards):
        x = x0 + i * (cw + gap)
        f.append(rect(x, top, cw, ch, fill=FILL, stroke=col, sw=1.8, rx=12))
        f.append(text(x + cw / 2, top + 30, ttl, size=13, color=col, bold=True))
        f.append(line(x + 16, top + 44, x + cw - 16, top + 44, color=col, sw=1.1))
        f.append(text(x + cw / 2, top + 78, l1, size=11, color=INK, bold=True))
        f.append(text(x + cw / 2, top + 96, l2, size=11, color=INK, bold=True))
        f.append(text(x + cw / 2, top + 150, s1, size=9.5, color=MUTED))
        f.append(text(x + cw / 2, top + 168, s2, size=9.5, color=MUTED))

    f.append(fitbox(110, 326, 540, 30,
                    "І наскрізна умова — спільна земля (GND): без неї модуль і МК не «бачать» рівнів.",
                    size=11, fill="#eef7f0", stroke=FIELD, sw=1.3, bold=True))
    render(os.path.join(IMG, "four-questions.svg"), W, H, *f)


# ── 3. Дискретний давач: вихід — один біт ────────────────────────────────────
def fig_discrete_sensor():
    W, H = 720, 360
    f = [text(W / 2, 28, "Дискретний давач: вихід — лише «0 або 1»",
              size=16, bold=True)]

    names = ["рух (PIR)", "геркон", "кінцевик", "ІЧ-перешкода"]
    bw, gap, x0, top = 150, 14, 40, 64
    for i, nm in enumerate(names):
        x = x0 + i * (bw + gap)
        f.append(rect(x, top, bw, 52, fill=FILL, stroke=INK, sw=1.6, rx=10))
        f.append(text(x + bw / 2, top + 24, nm, size=11, color=INK, bold=True))
        f.append(text(x + bw / 2, top + 42, "0 або 1", size=9, color=MUTED))

    # часова діаграма HIGH/LOW
    yhi, ylo = 196, 248
    f.append(text(56, 188, "OUT", size=10, color=INK, anchor="start", bold=True))
    pts = [(110, ylo), (230, ylo), (230, yhi), (400, yhi), (400, ylo),
           (540, ylo), (540, yhi), (660, yhi), (660, ylo), (690, ylo)]
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (poly, FIELD))
    f.append(text(315, yhi - 8, "є подія (HIGH)", size=9, color=FIELD))
    f.append(text(170, ylo + 16, "спокій (LOW)", size=9, color=MUTED))

    f.append(fitbox(90, 304, 540, 30,
                    "Прошивка читає його як звичайний цифровий вхід: пороги, підтяжка, брязкіт.",
                    size=11, fill="#fdf6e3", stroke=GOLD, sw=1.3, bold=True))
    render(os.path.join(IMG, "discrete-sensor.svg"), W, H, *f)


# ── 4. Випадок А: давач-«перемикач» + підтяжка (active-low) ──────────────────
def fig_switch_sensor():
    W, H = 760, 380
    f = [text(W / 2, 28, "Давач-«ключ»: підтяжка тримає HIGH, давач садить LOW",
              size=15, bold=True)]

    # шина VCC і GND
    f.append(line(110, 92, 470, 92, color=POS, sw=2.2))
    f.append(text(110, 84, "VCC = 3.3 В", size=10, color=POS, anchor="start", bold=True))
    f.append(line(110, 330, 470, 330, color=NEG, sw=2.2))
    f.append(text(110, 350, "GND (спільна)", size=10, color=NEG, anchor="start", bold=True))

    # резистор підтяжки
    f.append(line(250, 92, 250, 112, color=INK, sw=2))
    f.append(rect(238, 112, 24, 38, fill=BG, stroke=GOLD, sw=1.8, rx=3))
    f.append(line(250, 150, 250, 168, color=INK, sw=2))
    f.append(text(268, 134, "pull-up", size=9.5, color=GOLD, anchor="start", bold=True))
    f.append(text(268, 150, "(можна внутрішню)", size=9, color=MUTED, anchor="start"))

    # вузол → вхід МК
    f.append(circle(250, 168, 4, fill=INK, stroke=INK, sw=0))
    f.append(line(250, 168, 360, 168, color=INK, sw=2.2))
    f.append(rect(360, 134, 110, 70, fill="none", stroke=NEG, sw=2, rx=10))
    f.append(text(415, 158, "вхід МК", size=11, color=NEG, bold=True))
    f.append(text(415, 178, "чекаємо LOW", size=10, color=INK, bold=True))

    # давач-ключ вниз до GND
    f.append(line(250, 168, 250, 250, color=INK, sw=2))
    f.append(rect(200, 250, 100, 56, fill=FILL, stroke=INK, sw=1.6, rx=8))
    f.append(text(250, 274, "давач", size=10, color=INK, bold=True))
    f.append(text(250, 292, "(ключ на GND)", size=8.5, color=MUTED))
    f.append(line(250, 306, 250, 330, color=INK, sw=2))

    # права плашка: логіка
    f.append(rect(520, 96, 210, 210, fill="none", stroke="#e4e4e4", sw=1.6, rx=10))
    f.append(text(625, 122, "Логіка active-low:", size=11, color=INK, bold=True))
    f.append(text(536, 150, "спокій → підтяжка", size=10, color=INK, anchor="start"))
    f.append(text(536, 168, "тримає HIGH (1)", size=10, color=INK, anchor="start"))
    f.append(text(536, 196, "спрацював → давач", size=10, color=INK, anchor="start"))
    f.append(text(536, 214, "садить LOW (0)", size=10, color=FIELD, anchor="start", bold=True))
    f.append(text(536, 250, "if (read == LOW)", size=9.5, color=INK, anchor="start", bold=True))
    f.append(text(536, 268, "{ /* подія */ }", size=9.5, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "switch-sensor.svg"), W, H, *f)


# ── 5. Випадок Б: давач із двотактним виходом (прямо / через зсув) ───────────
def fig_driven_sensor():
    W, H = 760, 360
    f = [text(W / 2, 28, "Давач сам жене вихід: 3.3 В — прямо, 5 В — лише через зсув",
              size=14.5, bold=True)]

    # ліва панель: 3.3 В прямо
    f.append(rect(30, 60, 340, 270, fill="none", stroke="#e4e4e4", sw=1.6, rx=12))
    f.append(text(200, 86, "Однакова напруга (3.3 В) → прямо", size=11.5, color=FIELD, bold=True))
    f.append(rect(56, 150, 120, 64, fill=FILL, stroke=INK, sw=1.6, rx=8))
    f.append(text(116, 178, "давач 3.3 В", size=10, color=INK, bold=True))
    f.append(text(116, 196, "push-pull OUT", size=8.5, color=MUTED))
    f.append(arrow(176, 182, 250, 182, color=INK, sw=2.2))
    f.append(text(213, 174, "прямо", size=9, color=FIELD, bold=True))
    f.append(rect(250, 150, 96, 64, fill="none", stroke=NEG, sw=2, rx=8))
    f.append(text(298, 186, "вхід МК", size=10, color=NEG, bold=True))
    f.append(text(200, 256, "однакові рівні — просто з'єднати", size=10, color=INK))
    f.append(text(200, 276, "(і спільна земля)", size=9, color=MUTED))

    # права панель: 5 В через зсув
    f.append(rect(390, 60, 340, 270, fill="none", stroke="#e4e4e4", sw=1.6, rx=12))
    f.append(text(560, 86, "Давач 5 В → обов'язково зсув", size=11.5, color=POS, bold=True))
    f.append(rect(408, 150, 96, 64, fill=FILL, stroke=INK, sw=1.6, rx=8))
    f.append(text(456, 178, "давач 5 В", size=10, color=INK, bold=True))
    f.append(text(456, 196, "OUT = 5 В", size=8.5, color=POS))
    f.append(line(504, 182, 528, 182, color=INK, sw=2))
    f.append(rect(528, 158, 70, 48, fill="#fdf6e3", stroke=GOLD, sw=1.6, rx=6))
    f.append(text(563, 180, "зсув", size=9.5, color=GOLD, bold=True))
    f.append(text(563, 196, "рівнів", size=9, color=GOLD))
    f.append(line(598, 182, 622, 182, color=INK, sw=2))
    f.append(rect(622, 150, 86, 64, fill="none", stroke=NEG, sw=2, rx=8))
    f.append(text(665, 186, "вхід МК", size=10, color=NEG, bold=True))
    f.append(text(560, 256, "5 В прямо = спалена ніжка!", size=10, color=POS, bold=True))
    f.append(text(560, 276, "лише дільник чи перетворювач рівнів", size=9, color=MUTED))
    render(os.path.join(IMG, "driven-sensor.svg"), W, H, *f)


# ── 6. Повна модель ніжки: вихід · вхід · захист · код ───────────────────────
def fig_pin_model():
    W, H = 760, 420
    f = [text(W / 2, 30, "Повна модель ніжки: вихід · вхід · захист · код",
              size=16, bold=True)]

    cx, cy = 380, 232
    quads = [
        (NEG,   188, 132, "Вихід",  "push-pull", "open-drain"),
        (FIELD, 572, 132, "Вхід",   "пороги",    "підтяжки"),
        (POS,   188, 332, "Захист", "струм/діоди", "брязкіт"),
        (GOLD,  572, 332, "Код",    "регістри",  "маски, біти"),
    ]
    # промені від центра
    for col, qx, qy, *_ in quads:
        f.append(line(cx, cy, qx, qy, color=col, sw=1.6, dash="5,3"))
    # центр
    f.append(circle(cx, cy, 52, fill="#fdf6e3", stroke=GOLD, sw=2.6))
    f.append(text(cx, cy - 4, "НІЖКА", size=13, color=INK, bold=True))
    f.append(text(cx, cy + 14, "(GPIO)", size=10, color=MUTED))
    # картки граней
    for col, qx, qy, ttl, a, b in quads:
        f.append(rect(qx - 112, qy - 44, 224, 88, fill=FILL, stroke=col, sw=1.8, rx=12))
        f.append(text(qx, qy - 14, ttl, size=13, color=col, bold=True))
        f.append(text(qx, qy + 8, a, size=10, color=INK))
        f.append(text(qx, qy + 26, b, size=10, color=INK))

    f.append(fitbox(110, 388, 540, 28,
                    "Та сама ніжка одночасно: два транзистори, вхід із порогами, біт у регістрі, вивід модуля.",
                    size=11, fill="#eef7f0", stroke=FIELD, sw=1.3, bold=True))
    render(os.path.join(IMG, "pin-model.svg"), W, H, *f)


# ── Вставка «Матриця кнопок»: 1) сітка й сканування ──────────────────────────
def fig_matrix_grid():
    W, H = 760, 360
    f = [text(W / 2, 28, "Матриця кнопок: 16 клавіш — 8 ніжок", size=16, bold=True)]

    xs = [330, 420, 510, 600]      # стовпці C0..C3
    ys = [120, 165, 210, 255]      # рядки R0..R3
    act_col, act_row = 2, 1        # активний рядок R1, озвався стовпець C2

    # стовпці (вертикалі)
    for i, x in enumerate(xs):
        on = (i == act_col)
        f.append(line(x, 100, x, 275, color=FIELD if on else MUTED, sw=2.2 if on else 1.4))
        f.append(text(x, 90, "C%d" % i, size=10, color=FIELD if on else MUTED, bold=True))
    # рядки (горизонталі) + вузли
    for j, y in enumerate(ys):
        on = (j == act_row)
        f.append(line(310, y, 620, y, color=FIELD if on else MUTED, sw=2.4 if on else 1.4))
        f.append(text(290, y + 4, "R%d" % j, size=10, color=FIELD if on else MUTED,
                      anchor="end", bold=True))
        for i, x in enumerate(xs):
            pressed = (i == act_col and j == act_row)
            f.append(circle(x, y, 6, fill="#eef7f0" if pressed else BG,
                            stroke=FIELD if pressed else MUTED, sw=1.6))

    f.append(text(150, 130, "R1 активний →", size=9.5, color=FIELD, anchor="start", bold=True))
    f.append(text(648, 165, "натиск (R1,C2)", size=9.5, color=FIELD, anchor="start", bold=True))
    f.append(text(648, 120, "C2 озвався", size=9, color=FIELD, anchor="start"))

    f.append(fitbox(150, 300, 460, 46,
                    ["R+C ніжок дають R×C клавіш.",
                     "4 + 4 = 8 ніжок -> 16 клавіш (а не 16 окремих виводів)."],
                    size=10.5, fill="#fafafa", stroke=MUTED, sw=1.3, bold=True))
    render(os.path.join(IMG, "matrix-grid.svg"), W, H, *f)


# ── Вставка «Матриця кнопок»: 2) привид і ліки діодом ────────────────────────
def fig_matrix_ghost():
    W, H = 760, 330
    f = [text(W / 2, 28, "Привид (ghosting) і ліки — діод у кожній клавіші",
              size=15.5, bold=True)]

    def cell(cx, cy, fill, stroke):
        return circle(cx, cy, 7, fill=fill, stroke=stroke, sw=1.8)

    def diode(cx, cy):  # маленький трикутник збоку клавіші
        return ('<path d="M%.0f,%.0f l 8,5 l -8,5 Z" fill="%s"/>'
                % (cx - 14, cy - 5, GOLD))

    # ── ліва половина: без діодів ──
    f.append(text(180, 92, "Без діодів", size=12, color=POS, bold=True))
    lx = [130, 230]; ly = [134, 214]
    for x in lx:
        f.append(line(x, 114, x, 234, color=MUTED, sw=1.4))
    for y in ly:
        f.append(line(110, y, 250, y, color=MUTED, sw=1.4))
    f.append(cell(130, 134, "#eef7f0", FIELD))
    f.append(cell(230, 134, "#eef7f0", FIELD))
    f.append(cell(130, 214, "#eef7f0", FIELD))
    f.append(cell(230, 214, "#fdecea", POS))
    f.append(text(246, 218, "✗ привид", size=8.6, color=POS, anchor="start", bold=True))
    f.append(line(130, 134, 230, 134, color=POS, sw=1.8, dash="5 4"))
    f.append(line(230, 134, 230, 214, color=POS, sw=1.8, dash="5 4"))
    f.append(text(180, 252, "струм «крадеться» в обхід -> фальшива 4-та",
                  size=8.6, color=POS))

    # ── права половина: з діодами ──
    f.append(text(580, 92, "З діодами", size=12, color=FIELD, bold=True))
    rx = [530, 630]; ry = [134, 214]
    for x in rx:
        f.append(line(x, 114, x, 234, color=MUTED, sw=1.4))
    for y in ry:
        f.append(line(510, y, 650, y, color=MUTED, sw=1.4))
    for j, y in enumerate(ry):
        for i, x in enumerate(rx):
            empty = (i == 1 and j == 1)
            f.append(cell(x, y, BG if empty else "#eef7f0", MUTED if empty else FIELD))
            f.append(diode(x, y))
    f.append(text(580, 252, "діод пускає струм лише в один бік ->", size=8.6, color=FIELD))
    f.append(text(580, 268, "обхідний шлях закрито ✓", size=8.6, color=FIELD, bold=True))

    f.append(fitbox(120, 296, 520, 26,
                    "Три натиснуті в куті прямокутника без діодів дають уявну четверту; діод це лікує.",
                    size=10, fill="#fafafa", stroke=MUTED, sw=1.3, bold=True))
    render(os.path.join(IMG, "matrix-ghost.svg"), W, H, *f)


if __name__ == "__main__":
    fig_blackbox()
    fig_four_questions()
    fig_discrete_sensor()
    fig_switch_sensor()
    fig_driven_sensor()
    fig_pin_model()
    fig_matrix_grid()
    fig_matrix_ghost()
    print("figs.py: 8 SVG -> ./img/")
