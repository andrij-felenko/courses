# -*- coding: utf-8 -*-
"""Фігури до теми «Захист аналогового входу» (аналогова електроніка, кутом теорії кіл).
Фігури теми:
  clamp-diodes.svg   — вхідний вивід із двома фіксувальними діодами на шини: куди стікає надлишок
  series-clamp.svg   — послідовний резистор + фіксатор: резистор перетворює перенапругу на безпечний струм
  safe-window.svg    — «вікно» допустимих напруг між шинами; за ним діод відкривається й тече струм
  three-lines.svg    — три рубежі оборони: TVS на роз'ємі, послідовний R, фіксатор біля кристала
Фігури вставки comp-input-clamp-array:
  clamp-family.svg   — клас жертовних деталей: фіксатор-діод проти повноцінного TVS (вісь енергії/спаду)
  steering-array.svg — діодна збірка зі спільним катодом: шлях фіксації верхівки на шину, мала ємність
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _diode(x, y, up=True, col=INK, sw=2.0):
    """Маленький символ діода у вертикальному дроті; up=True — анод знизу, провідність угору.
    Повертає список фрагментів. Трикутник вказує напрям провідності."""
    out = []
    s = 9  # півширина трикутника
    if up:
        # провідність угору: вершина трикутника зверху, риска (катод) над нею
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="%.1f"/>'
                   % (x - s, y + s, x + s, y + s, x, y - s, "none", col, sw))
        out.append(line(x - s, y - s, x + s, y - s, color=col, sw=sw))   # катодна риска
    else:
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="%.1f"/>'
                   % (x - s, y - s, x + s, y - s, x, y + s, "none", col, sw))
        out.append(line(x - s, y + s, x + s, y + s, color=col, sw=sw))
    return out


def clamp_diodes():
    """Вхідний вивід кристала з двома діодами на V+ і V−: надлишок угору стікає у V+, провал — із V−."""
    W, H = 700, 400
    p = []
    # ── дві шини живлення ──
    vtop, vbot = 80, 320
    railL, railR = 90, 560
    p.append(line(railL, vtop, railR, vtop, color=POS, sw=2.6))
    p.append(text(railL - 6, vtop + 5, "V+", size=15, bold=True, color=POS, anchor="end"))
    p.append(line(railL, vbot, railR, vbot, color=NEG, sw=2.6))
    p.append(text(railL - 6, vbot + 5, "V−", size=15, bold=True, color=NEG, anchor="end"))

    # ── вхідний вузол (вивід кристала) ──
    nx = 330
    ny = 200
    # дріт від входу ліворуч
    p.append(arrow(150, ny, nx - 12, ny, color=INK, sw=2))
    p.append(text(150, ny - 12, "вхідний сигнал", size=13, anchor="start"))
    p.append(circle(nx, ny, 5, fill=INK, stroke=INK))
    p.append(text(nx, ny + 26, "вивід", size=12, color=MUTED))
    p.append(text(nx, ny + 42, "кристала", size=12, color=MUTED))
    # дріт від вузла праворуч у трикутник підсилювача
    ax = 430
    p.append(line(nx, ny, ax, ny, color=INK, sw=2))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (ax, ny - 34, ax, ny + 34, ax + 64, ny, FILL, LINE))
    p.append(text(ax + 20, ny + 5, "вхід", size=12, bold=True))
    p.append(text(ax + 30, ny - 44, "підсилювач / АЦП", size=12, color=MUTED))

    # ── верхній діод: від вузла до V+ (провідність угору) ──
    p.append(line(nx, ny, nx, vtop + 40, color=INK, sw=2))
    p += _diode(nx, (ny + vtop) / 2 - 10, up=True, col=POS)
    p.append(line(nx, vtop + 40, nx, vtop, color=INK, sw=2))
    p.append(text(nx + 18, (ny + vtop) / 2 - 6, "відкриється, якщо", size=12, color=POS, anchor="start"))
    p.append(text(nx + 18, (ny + vtop) / 2 + 10, "вхід > V+ + 0.6 В", size=12, color=POS, anchor="start"))

    # ── нижній діод: від V− до вузла (провідність угору, тобто з V− у вузол) ──
    p.append(line(nx, ny, nx, vbot - 40, color=INK, sw=2))
    p += _diode(nx, (ny + vbot) / 2 + 10, up=True, col=NEG)
    p.append(line(nx, vbot - 40, nx, vbot, color=INK, sw=2))
    p.append(text(nx + 18, (ny + vbot) / 2 + 6, "відкриється, якщо", size=12, color=NEG, anchor="start"))
    p.append(text(nx + 18, (ny + vbot) / 2 + 22, "вхід < V− − 0.6 В", size=12, color=NEG, anchor="start"))

    b, _, _ = textbox(W / 2, 372,
                      "Два діоди стережуть вивід: поки сигнал між шинами — обидва закриті, входу байдуже.\n"
                      "Виліз вище V+ або нижче V− — найближчий діод відкривається й стікає надлишок на шину.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'clamp-diodes.svg'), W, H, *p,
           title="Фіксувальні діоди: вхід тримають у межах шин живлення")


def series_clamp():
    """Послідовний резистор перед фіксатором: він перетворює перенапругу на безпечний струм діода."""
    W, H = 720, 360
    p = []
    vtop = 70
    y = 200
    # ── джерело перенапруги ліворуч ──
    p.append(text(70, y - 40, "аварія на вході", size=13, bold=True, color=POS))
    p.append(text(70, y - 22, "+30 В", size=15, bold=True, color=POS))
    p.append(circle(80, y, 6, fill="#fdecea", stroke=POS, sw=2))
    # ── послідовний резистор ──
    rx0, rx1 = 150, 250
    p.append(line(80, y, rx0, y, color=INK, sw=2))
    p.append(rect(rx0, y - 14, rx1 - rx0, 28, fill="#eef2ff", stroke=NEG, sw=2))
    p.append(text((rx0 + rx1) / 2, y - 24, "Rпосл", size=13, bold=True, color=NEG))
    p.append(text((rx0 + rx1) / 2, y + 5, "10 кОм", size=12, bold=True, color=NEG))
    # ── вузол фіксатора ──
    nx = 360
    p.append(line(rx1, y, nx, y, color=INK, sw=2))
    p.append(circle(nx, y, 5, fill=INK, stroke=INK))
    # шина V+
    p.append(line(nx - 40, vtop, nx + 230, vtop, color=POS, sw=2.6))
    p.append(text(nx - 46, vtop + 5, "V+ = +15 В", size=13, bold=True, color=POS, anchor="end"))
    # фіксувальний діод угору на V+
    p.append(line(nx, y, nx, vtop + 36, color=INK, sw=2))
    p += _diode(nx, (y + vtop) / 2, up=True, col=POS)
    p.append(line(nx, vtop + 36, nx, vtop, color=INK, sw=2))
    # струм через діод — стрілка
    p.append(text(nx + 16, (y + vtop) / 2 + 4, "Iфікс ≈ 1.45 мА", size=12, bold=True, color=POS, anchor="start"))
    p.append(text(nx + 16, (y + vtop) / 2 + 20, "(діод тримає вузол ≈ 15.6 В)", size=11, color=MUTED, anchor="start"))
    # ── до підсилювача праворуч ──
    ax = 470
    p.append(line(nx, y, ax, y, color=INK, sw=2))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (ax, y - 30, ax, y + 30, ax + 60, y, FILL, LINE))
    p.append(text(ax + 18, y + 5, "вхід", size=12, bold=True))
    p.append(text(ax + 28, y + 48, "вузол ≈ 15.6 В — у безпеці", size=12, color=FIELD))

    # розрахунок збоку
    calc = ("30 − 15.6 = 14.4 В на Rпосл\n"
            "I = 14.4 / 10 000 ≈ 1.45 мА\n"
            "1.45 мА < 10 мА → діод цілий")
    bb, _, _ = textbox(600, 150, calc, size=12, fill="#eafaf0", stroke=FIELD)
    p.append(bb)

    b, _, _ = textbox(W / 2, 332,
                      "Резистор приймає всю різницю напруг на себе, а діодові лишає крихітний струм.\n"
                      "Без резистора діод спробував би провести десятки ампер і згорів би першим.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'series-clamp.svg'), W, H, *p,
           title="Послідовний резистор + фіксатор: перенапруга стає безпечним струмом")


def safe_window():
    """Вертикальна шкала напруг: безпечне «вікно» між шинами, за ним відкривається діод."""
    W, H = 680, 420
    p = []
    ox = 250
    top, bot = 70, 360
    # вісь
    p.append(line(ox, bot, ox, top, color=INK, sw=2))
    p.append(text(ox, top - 14, "напруга на вході", size=13, bold=True))

    # рівні
    def lvl(yfrac):
        return bot - (bot - top) * yfrac
    yVp = lvl(0.72)   # V+
    yVm = lvl(0.28)   # V−
    yDp = lvl(0.80)   # V+ + 0.6
    yDm = lvl(0.20)   # V− − 0.6

    # безпечне вікно — зелена смуга між шинами
    p.append(rect(ox - 70, yVp, 140, yVm - yVp, fill="#eafaf0", stroke=FIELD, sw=1.5))
    p.append(text(ox, (yVp + yVm) / 2 - 6, "безпечне вікно", size=13, bold=True, color=FIELD))
    p.append(text(ox, (yVp + yVm) / 2 + 12, "обидва діоди закриті", size=11, color=FIELD))

    # шини
    for yy, lbl, col in [(yVp, "V+", POS), (yVm, "V−", NEG)]:
        p.append(line(ox - 90, yy, ox + 90, yy, color=col, sw=2.4))
        p.append(text(ox - 96, yy + 5, lbl, size=14, bold=True, color=col, anchor="end"))
    # пороги відкриття діодів
    for yy, lbl, col in [(yDp, "V+ + 0.6 В — верхній діод відкривається", POS),
                         (yDm, "V− − 0.6 В — нижній діод відкривається", NEG)]:
        p.append(line(ox - 70, yy, ox + 70, yy, color=col, sw=1.4, dash="5 4"))
        p.append(text(ox + 96, yy + 4, lbl, size=11, color=col, anchor="start"))

    # зони фіксації — рожеві
    p.append(rect(ox - 70, top, 140, yDp - top, fill="#fdecea", stroke=POS, sw=1.2))
    p.append(text(ox, (top + yDp) / 2 + 4, "діод тече у V+", size=11, color=POS))
    p.append(rect(ox - 70, yDm, 140, bot - yDm, fill="#fdecea", stroke=NEG, sw=1.2))
    p.append(text(ox, (yDm + bot) / 2 + 4, "діод тече з V−", size=11, color=NEG))

    b, _, _ = textbox(W / 2, 396,
                      "Поки сигнал у вікні V− … V+, вхід нічого не «бачить» — обидва діоди закриті.\n"
                      "Лише за ~0.6 В поза шиною найближчий діод відкривається й починає текти.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'safe-window.svg'), W, H, *p,
           title="Абсолютна межа входу: безпечне вікно між шинами живлення")


def three_lines():
    """Три рубежі оборони вздовж тракту: TVS на роз'ємі, послідовний R, фіксатор біля кристала."""
    W, H = 740, 360
    p = []
    y = 180
    # горизонтальний тракт від роз'єму до кристала
    xs = [70, 230, 420, 610]
    p.append(line(xs[0], y, xs[-1] + 40, y, color=INK, sw=2))

    # 1) роз'єм + TVS на землю
    p.append(circle(xs[0], y, 7, fill="#fff", stroke=INK, sw=2))
    p.append(text(xs[0], y - 22, "роз'єм", size=12, bold=True))
    p.append(text(xs[0], y - 6, "(зовнішній світ)", size=10, color=MUTED))
    tx = xs[0] + 70
    p.append(line(tx, y, tx, y + 60, color=INK, sw=2))
    p += _diode(tx, y + 32, up=False, col=FIELD)   # TVS на землю
    p.append(line(tx, y + 50, tx, y + 70, color=INK, sw=2))
    p.append(line(tx - 14, y + 70, tx + 14, y + 70, color=INK, sw=2.4))  # земля
    p.append(text(tx, y - 14, "TVS", size=13, bold=True, color=FIELD))
    p.append(text(tx, y + 92, "рубіж 1", size=11, color=FIELD))
    p.append(text(tx, y + 108, "ловить кидок", size=10, color=MUTED))

    # 2) послідовний резистор
    rx0, rx1 = xs[1] + 40, xs[1] + 140
    p.append(rect(rx0, y - 13, rx1 - rx0, 26, fill="#eef2ff", stroke=NEG, sw=2))
    p.append(text((rx0 + rx1) / 2, y - 22, "Rпосл", size=12, bold=True, color=NEG))
    p.append(text((rx0 + rx1) / 2, y + 40, "рубіж 2", size=11, color=NEG))
    p.append(text((rx0 + rx1) / 2, y + 56, "обмежує струм", size=10, color=MUTED))

    # 3) фіксувальні діоди на шини біля кристала
    cx = xs[2] + 120
    p.append(line(cx, y, cx, y - 60, color=INK, sw=2))
    p += _diode(cx, y - 32, up=True, col=POS)
    p.append(line(cx, y - 60, cx, y - 76, color=INK, sw=2))
    p.append(line(cx - 16, y - 76, cx + 16, y - 76, color=POS, sw=2.4))
    p.append(text(cx + 22, y - 72, "V+", size=12, bold=True, color=POS, anchor="start"))
    p.append(line(cx, y, cx, y + 60, color=INK, sw=2))
    p += _diode(cx, y + 32, up=True, col=NEG)
    p.append(line(cx, y + 60, cx, y + 76, color=INK, sw=2))
    p.append(line(cx - 16, y + 76, cx + 16, y + 76, color=NEG, sw=2.4))
    p.append(text(cx + 22, y + 80, "V−", size=12, bold=True, color=NEG, anchor="start"))
    p.append(text(cx, y - 96, "рубіж 3", size=11, color=POS))
    p.append(text(cx, y - 112, "фіксатор біля кристала", size=10, color=MUTED))

    # кристал праворуч
    ax = xs[3]
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (ax, y - 28, ax, y + 28, ax + 56, y, FILL, LINE))
    p.append(text(ax + 16, y + 5, "вхід", size=12, bold=True))
    p.append(text(ax + 28, y + 44, "кристал", size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 330,
                      "Оборона ешелонована: TVS на роз'ємі гасить грубий кидок, резистор обмежує струм,\n"
                      "а слабкий фіксатор біля кристала ловить лише те, що прорвалося. Кожен рубіж — на своє.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'three-lines.svg'), W, H, *p,
           title="Три рубежі захисту входу: TVS, послідовний резистор, фіксатор")


def clamp_family():
    """Дві жертовні деталі поряд: слабкий фіксатор-діод (мало енергії, малий спад, мала ємність)
    проти повноцінного TVS (багато енергії, більший спад, велика ємність). Спільна вісь — енергія кидка."""
    W, H = 740, 380
    p = []
    # дві колонки-картки
    colW, colH = 290, 250
    y0 = 70
    xL = 60
    xR = 390

    def card(x, title, col, rows):
        out = []
        out.append(rect(x, y0, colW, colH, fill="#f7f9fc", stroke=col, sw=2))
        out.append(text(x + colW / 2, y0 + 30, title, size=15, bold=True, color=col))
        out.append(line(x + 18, y0 + 44, x + colW - 18, y0 + 44, color=col, sw=1.2))
        yy = y0 + 74
        for lbl, val in rows:
            out.append(text(x + 20, yy, lbl, size=12, color=MUTED, anchor="start"))
            out.append(text(x + colW - 20, yy, val, size=12, bold=True, anchor="end"))
            yy += 32
        return out

    p += card(xL, "Діод-фіксатор", NEG, [
        ("роль", "стерегти точність"),
        ("енергія кидка", "мала"),
        ("прямий спад", "≈ 0.3–0.7 В"),
        ("ємність на лінію", "мала (пФ)"),
        ("де стоїть", "біля кристала"),
    ])
    p += card(xR, "Повноцінний TVS", POS, [
        ("роль", "жертовний щит"),
        ("енергія кидка", "велика (Дж-кидки)"),
        ("прямий спад", "вищий, росте зі струмом"),
        ("ємність на лінію", "велика (десятки пФ)"),
        ("де стоїть", "на роз'ємі"),
    ])

    # стрілка-вісь «енергія кидка» під картками
    ay = y0 + colH + 36
    p.append(text(W / 2, ay - 14, "що більша енергія кидка — то ближче до TVS", size=12, color=INK))
    p.append(arrow(xL + 40, ay, xR + colW - 40, ay, color=INK, sw=2))
    p.append(text(xL + 40, ay + 22, "ESD: кіловольти, та мізерні джоулі", size=11, color=NEG, anchor="start"))
    p.append(text(xR + colW - 40, ay + 22, "розряд лінії, блискавка поряд", size=11, color=POS, anchor="end"))

    render(os.path.join(OUT, 'clamp-family.svg'), W, H, *p,
           title="Один клас, два краї: слабкий фіксатор проти жертовного TVS")


def steering_array():
    """Діодна збірка зі спільним катодом: два діоди від лінії — угору на шину й униз на землю,
    повноцінний TVS винесено на шину. Показано шлях фіксації додатної верхівки й чому ємність на лінію мала."""
    W, H = 760, 420
    p = []
    # шини
    vtop, vbot = 70, 350
    railL, railR = 110, 560
    p.append(line(railL, vtop, railR, vtop, color=POS, sw=2.6))
    p.append(text(railL - 8, vtop + 5, "шина", size=13, bold=True, color=POS, anchor="end"))
    p.append(line(railL, vbot, railR, vbot, color=NEG, sw=2.6))
    p.append(text(railL - 8, vbot + 5, "земля", size=13, bold=True, color=NEG, anchor="end"))

    # лінія сигналу (центральний відвід) ліворуч
    ny = (vtop + vbot) / 2
    nx = 300
    p.append(line(150, ny, nx, ny, color=INK, sw=2))
    p.append(circle(nx, ny, 5, fill=INK, stroke=INK))
    p.append(text(150, ny - 12, "лінія I/O", size=13, bold=True, anchor="start"))
    p.append(text(150, ny + 22, "(центральний відвід)", size=11, color=MUTED, anchor="start"))

    # верхній діод: від лінії на шину (провідність угору)
    p.append(line(nx, ny, nx, vtop + 42, color=INK, sw=2))
    p += _diode(nx, (ny + vtop) / 2, up=True, col=POS)
    p.append(line(nx, vtop + 42, nx, vtop, color=INK, sw=2))
    p.append(text(nx + 16, (ny + vtop) / 2 - 4, "верхній діод", size=12, bold=True, color=POS, anchor="start"))
    p.append(text(nx + 16, (ny + vtop) / 2 + 12, "веде верхівку на шину", size=11, color=MUTED, anchor="start"))

    # нижній діод: від землі на лінію (провідність угору)
    p.append(line(nx, ny, nx, vbot - 42, color=INK, sw=2))
    p += _diode(nx, (ny + vbot) / 2, up=True, col=NEG)
    p.append(line(nx, vbot - 42, nx, vbot, color=INK, sw=2))
    p.append(text(nx + 16, (ny + vbot) / 2 + 4, "нижній діод", size=12, bold=True, color=NEG, anchor="start"))
    p.append(text(nx + 16, (ny + vbot) / 2 + 20, "підтягує з землі", size=11, color=MUTED, anchor="start"))

    # центральний TVS на шину-землю (праворуч), велике вістря
    tx = 470
    p.append(line(tx, vtop, tx, vtop + 80, color=INK, sw=2))
    # символ TVS: два діоди спина-до-спини (двобічний) у вертикалі
    p += _diode(tx, vtop + 100, up=False, col=FIELD)
    p += _diode(tx, vtop + 140, up=True, col=FIELD)
    p.append(line(tx, vtop + 150, tx, vbot, color=INK, sw=2))
    p.append(text(tx - 18, vtop + 113, "TVS", size=12, bold=True, color=FIELD, anchor="end"))
    p.append(text(tx - 18, vtop + 131, "на шині", size=12, bold=True, color=FIELD, anchor="end"))

    # шлях фіксації — підпис із формулою спаду (праворуч, нижче рівня TVS-символу)
    calc = ("Додатна верхівка:\n"
            "лінія → верхній діод (Vf) → шина → TVS\n"
            "Uфікс ≈ Uшина + Vf + спад TVS")
    bb, _, _ = textbox(620, vtop + 36, calc, size=11, fill="#eafaf0", stroke=FIELD)
    p.append(bb)

    b, _, _ = textbox(W / 2, 396,
                      "На лінію дивляться лише два маленькі діоди-стрілочники — їхня ємність мала, швидкий сигнал не валиться.\n"
                      "Громіздкий TVS, що тримає всю енергію, сидить осторонь на шині, не навантажуючи лінію своєю ємністю.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'steering-array.svg'), W, H, *p,
           title="Діодна збірка зі спільним катодом: верхівку — на шину, ємність — мала")


if __name__ == '__main__':
    clamp_diodes()
    series_clamp()
    safe_window()
    three_lines()
    clamp_family()
    steering_array()
    print("OK: 6 figures ->", OUT)
