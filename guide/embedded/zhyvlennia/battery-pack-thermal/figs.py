# -*- coding: utf-8 -*-
"""Фігури до теми «Тепловий менеджмент батарейного пакета».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

HOT  = POS        # гаряче — червоне
COOL = NEG        # прохолодне — синє
OK   = FIELD      # зелене виділення


# ── 1. Звідки тепло й куди воно йде ──────────────────────────────────────────
def fig_heat_flow():
    """Джерела тепла в комірці (омічне + ентропійне) і ланцюжок теплового
    опору до повітря. Аналогія з електричним колом: P тече, ΔT падає."""
    W, H = 780, 360
    f = [text(W / 2, 30, "Звідки тепло в комірці й куди воно тече", size=16, bold=True)]

    # комірка — гарячий прямокутник ліворуч
    cx, cy, cw, ch = 90, 120, 150, 150
    f.append(rect(cx, cy, cw, ch, fill="#fdecea", stroke=HOT, sw=2.2))
    f.append(text(cx + cw / 2, cy + 26, "Комірка", size=13, color=HOT, bold=True))
    f.append(text(cx + cw / 2, cy + 72, "P = I²·R", size=15, color=INK, bold=True))
    f.append(text(cx + cw / 2, cy + 98, "омічне — головне", size=10, color=MUTED))
    f.append(text(cx + cw / 2, cy + 122, "+ ентропійне (мале)", size=9.5, color=MUTED))

    # ланцюжок теплового опору: три послідовні ланки
    y = cy + ch / 2
    x = cx + cw + 24
    links = [("корпус", 0), ("радіатор", 0), ("повітря", 0)]
    boxw, gap = 118, 26
    for i, (nm, _) in enumerate(links):
        f.append(arrow(x, y, x + gap - 4, y, color=INK, sw=2))
        bx = x + gap
        last = (i == len(links) - 1)
        col = COOL if last else INK
        fill = "#eaf0fd" if last else "#fff"
        f.append(rect(bx, y - 30, boxw, 60, fill=fill, stroke=col, sw=1.8))
        f.append(text(bx + boxw / 2, y - 6, nm, size=11.5, color=col, bold=True))
        if not last:
            f.append(text(bx + boxw / 2, y + 16, "Rθ", size=12, color=MUTED, bold=True))
        else:
            f.append(text(bx + boxw / 2, y + 16, "30 °C", size=10.5, color=COOL))
        x = bx + boxw

    # підпис температурного падіння над ланцюгом
    f.append(text((cx + cw + x) / 2 + 10, cy - 8, "ΔT = P · Rθ  (падіння на кожній ланці)",
                  size=11, color=INK, bold=True))

    f.append(fitbox(70, 300, W - 140, 30,
                    "Менший струм (квадратично!) або менша сума Rθ — нижча температура комірки.",
                    size=10.5, fill="#eafaf0", stroke=OK, sw=1.3))
    render(os.path.join(IMG, "heat-flow.svg"), W, H, *f)


# ── 2. Градієнт у збірці: центр гарячіший за край ────────────────────────────
def fig_gradient():
    """Сітка комірок, забарвлена за температурою: гарячий центр, прохолодний
    край. Найгарячіша комірка старіє першою — і тягне весь послідовний пакет."""
    W, H = 780, 420
    f = [text(W / 2, 30, "Чому центр пакета гарячіший — і чим це загрожує", size=16, bold=True)]

    # сітка 5×4 комірок; температуру моделюємо за відстанню від центру
    cols, rows = 5, 4
    cell = 56
    gx, gy = 70, 70
    midc, midr = (cols - 1) / 2.0, (rows - 1) / 2.0
    maxd = (midc ** 2 + midr ** 2) ** 0.5
    hot_cell = None
    for r in range(rows):
        for c in range(cols):
            d = ((c - midc) ** 2 + (r - midr) ** 2) ** 0.5
            heat = 1.0 - d / maxd            # 1 у центрі, 0 на куті
            x = gx + c * (cell + 8)
            y = gy + r * (cell + 8)
            # колір: від синього (край) до червоного (центр) через теплу заливку
            t = 30 + int(heat * 22)          # 30..52 °C
            op = 0.12 + heat * 0.55
            f.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="8" '
                     'fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="1.4"/>'
                     % (x, y, cell, cell, HOT, op, HOT if heat > 0.5 else MUTED))
            f.append(text(x + cell / 2, y + cell / 2 + 4, "%d°" % t, size=11,
                          color=INK if heat > 0.45 else MUTED, bold=(heat > 0.85)))
            if heat > 0.99:
                hot_cell = (x + cell / 2, y + cell / 2)

    # стрілки тепла від центру назовні (символічно — чотири промені)
    if hot_cell:
        hcx, hcy = hot_cell
        f.append(circle(hcx, hcy, cell / 2 + 4, fill="none", stroke=HOT, sw=2))

    # права колонка-пояснення (рядки розбито вручну, щоб кожен влазив без дрібного шрифту)
    px = gx + cols * (cell + 8) + 24
    pw = W - px - 30
    f.append(fitbox(px, 76, pw, 70,
                    "Тепло центральних комірок іде\nкрізь усю збірку; крайні\nохолоджує повітря.",
                    size=10.5, fill="#fdf3f2", stroke=HOT, sw=1.4))
    f.append(fitbox(px, 158, pw, 78,
                    "Найгарячіша старіє найшвидше:\nросте її опір, а з ним нагрів.\nПетля сама себе жене.",
                    size=10.5, fill="#fff", stroke=MUTED, sw=1.3))
    f.append(fitbox(px, 248, pw, 70,
                    "Послідовний пакет упирається\nв найслабшу ланку — тож гине\nвесь, хоч решта ще бадьора.",
                    size=10.5, fill="#fff", stroke=INK, sw=1.3))

    f.append(fitbox(gx, gy + rows * (cell + 8) + 12, W - 2 * gx, 28,
                    "Мета охолодження — не лише холод, а РІВНІСТЬ: краще всі при 40°, ніж край 30° і центр 52°.",
                    size=10.5, fill="#eafaf0", stroke=OK, sw=1.3))
    render(os.path.join(IMG, "gradient.svg"), W, H, *f)


# ── 3. Сходи охолодження ─────────────────────────────────────────────────────
def fig_cooling_ladder():
    """П'ять сходинок від теплової маси до занурення: ефективність росте
    разом із ціною й складністю. Лізти вгору лише за потреби."""
    W, H = 800, 430
    f = [text(W / 2, 30, "Сходи охолодження: ефективність ↔ ціна й складність", size=16, bold=True)]

    steps = [
        ("0",  "Теплова маса й компонувка", "поглинути пік, рознести центр", OK),
        ("1",  "Пасив: кондукція",          "пластина/рамка → корпус",      OK),
        ("2",  "Активне повітря",           "вентилятор, обдув",            "#caa24a"),
        ("3",  "Рідина (cold plate)",       "теплоносій крізь канали",      HOT),
        ("4",  "Занурення (immersion)",     "комірки в діелектрику",        HOT),
    ]
    n = len(steps)
    # сходинки — прямокутники, що ростуть угору вправо
    base_y = 350
    step_h = 46
    x0 = 70
    bw = 300
    dx = (W - x0 - bw - 40) / (n - 1)
    for i, (num, title, sub, col) in enumerate(steps):
        x = x0 + i * dx
        y = base_y - i * step_h
        f.append(rect(x, y, bw, step_h - 8, fill="#fff", stroke=col, sw=1.9))
        f.append('<rect x="%.1f" y="%.1f" width="34" height="%d" rx="6" fill="%s" fill-opacity="0.18"/>'
                 % (x, y, step_h - 8, col))
        f.append(text(x + 17, y + (step_h - 8) / 2 + 5, num, size=14, color=col, bold=True))
        f.append(text(x + 44, y + 16, title, size=11.5, color=INK, bold=True, anchor="start"))
        f.append(text(x + 44, y + 31, sub, size=9.5, color=MUTED, anchor="start"))

    # осі-підказки напрямків
    f.append(arrow(46, base_y + 6, 46, base_y - (n - 1) * step_h + 10, color=MUTED, sw=1.6))
    f.append('<text x="40" y="%d" font-family="%s" font-size="10" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 40 %d)">ефективність →</text>'
             % (base_y - (n - 1) * step_h / 2, FONT, MUTED, base_y - (n - 1) * step_h / 2))
    f.append(arrow(x0 + 20, base_y + 40, x0 + (n - 1) * dx + 60, base_y + 40, color=MUTED, sw=1.6))
    f.append(text(x0 + (n - 1) * dx / 2 + 40, base_y + 58, "ціна, вага, точки відмови →",
                  size=10, color=MUTED))

    f.append(fitbox(W - 250, 70, 220, 56,
                    "Підігрів — окрема гілка: на морозі пакет спершу гріють, тоді заряджають.",
                    size=10, fill="#eaf0fd", stroke=COOL, sw=1.3))
    render(os.path.join(IMG, "cooling-ladder.svg"), W, H, *f)


# ── 4. Сигнальний шлях: NTC → АЦП → °C → foldback → струм (вставка proj) ─────
def fig_signal_chain():
    """Повний шлях у прошивці: дільник із NTC дає напругу, АЦП — код, таблиця
    чи Стейнгарт-Гарт — °C, max() обирає найгарячішу, foldback — дозволений струм."""
    W, H = 820, 250
    f = [text(W / 2, 30, "Шлях сигналу: від опору NTC до дозволеного струму", size=16, bold=True)]

    boxes = [
        ("N×NTC", "опір → напруга", COOL, "#eaf0fd"),
        ("АЦП", "напруга → код", INK, "#fff"),
        ("медіана", "фільтр шуму", INK, "#fff"),
        ("°C", "код → температура", INK, "#fff"),
        ("max()", "найгарячіша", HOT, "#fdecea"),
        ("foldback", "°C → струм", OK, "#eafaf0"),
    ]
    n = len(boxes)
    bw, bh = 108, 64
    gap = (W - 60 - n * bw) / (n - 1)
    y = 110
    x = 30
    for i, (nm, sub, col, fill) in enumerate(boxes):
        f.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.9))
        f.append(text(x + bw / 2, y + 26, nm, size=13, color=col, bold=True))
        f.append(text(x + bw / 2, y + 46, sub, size=9, color=MUTED))
        if i < n - 1:
            f.append(arrow(x + bw, y + bh / 2, x + bw + gap, y + bh / 2, color=INK, sw=2))
        x += bw + gap

    f.append(fitbox(30, 200, W - 60, 30,
                    "Кожна ланка — окрема функція; рішення завжди за МАКСИМУМОМ температури, не за середньою.",
                    size=10.5, fill="#fff", stroke=MUTED, sw=1.3))
    render(os.path.join(IMG, "signal-chain.svg"), W, H, *f)


# ── 5. Foldback із гістерезисом: чому потрібні два пороги ─────────────────────
def fig_foldback_hyst():
    """Профіль дозволеного струму від температури. Лінійне зрізання у вікні
    WARM..HOT; гарячий і холодний пороги мають гістерезис проти «дзвону»."""
    W, H = 820, 430
    f = [text(W / 2, 30, "Зрізання струму за температурою з гістерезисом", size=16, bold=True)]

    # осі
    ox, oy = 90, 330            # початок координат (ліво-низ)
    axw, axh = 640, 250
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))          # вісь T
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))          # вісь I
    f.append(text(ox + axw - 10, oy + 26, "температура °C", size=11, color=INK, anchor="end"))
    f.append('<text x="%d" y="%d" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %d %d)">дозволений струм</text>'
             % (40, oy - axh / 2, FONT, INK, 40, oy - axh / 2))

    # температурна шкала: -10 .. 55 °C
    tmin, tmax = -10.0, 55.0
    def tx(t): return ox + (t - tmin) / (tmax - tmin) * axw
    imax_y = oy - axh + 20
    def iy(frac): return oy - frac * (oy - imax_y)

    # рівень повного струму
    f.append(line(ox, iy(1.0), ox + axw, iy(1.0), color=MUTED, sw=1, dash="3 4"))
    f.append(text(ox - 8, iy(1.0) + 4, "I_MAX", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 8, oy + 4, "0", size=10, color=MUTED, anchor="end"))

    WARM, HOT_, COLD = 35.0, 45.0, 0.0
    # профіль струму (гарячий бік): 0 до COLD, повний COLD..WARM, лінійно вниз WARM..HOT, 0 далі
    pts = [(tmin, 0.0), (COLD, 0.0), (COLD, 1.0), (WARM, 1.0), (HOT_, 0.0), (tmax, 0.0)]
    path = "M " + " L ".join("%.1f %.1f" % (tx(t), iy(v)) for t, v in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, HOT))

    # вертикальні пороги
    for t, lab, col in [(COLD, "0°", COOL), (WARM, "35°", "#caa24a"), (HOT_, "45°", HOT)]:
        f.append(line(tx(t), oy, tx(t), iy(1.0), color=col, sw=1, dash="2 4"))
        f.append(text(tx(t), oy + 16, lab, size=10, color=col, bold=True))

    # гістерезис на гарячому порозі: відновлення нижче (42°)
    f.append(circle(tx(HOT_), iy(0.0), 3.5, fill=HOT, stroke=HOT, sw=1))
    f.append(circle(tx(42.0), iy(0.0), 3.5, fill="#fff", stroke=HOT, sw=1.6))
    f.append(arrow(tx(HOT_) - 2, iy(0.06), tx(42.0) + 2, iy(0.06), color=HOT, sw=1.4))
    f.append(text(tx(43.5), iy(0.16), "відновлення", size=9, color=HOT))
    f.append(text(tx(43.5), iy(0.10), "лише на 42°", size=9, color=HOT))

    # зони-підписи
    f.append(mtext(tx(-5), iy(0.62), ["мороз:", "заряд", "заборонено"], size=9.5, color=COOL))
    f.append(fitbox(tx(COLD) + 6, iy(1.0) - 26, tx(WARM) - tx(COLD) - 12, 22,
                    "повний струм", size=9.5, fill="#eafaf0", stroke=OK, sw=1.1))
    f.append(mtext(tx(40), iy(0.66), ["лінійне", "зрізання"], size=9.5, color="#caa24a"))

    f.append(fitbox(ox, oy + 40, axw, 30,
                    "Гістерезис: зрізав на 45° — вертай повний струм лише коли охолоне до 42°, інакше струм «дзвенить» на порозі.",
                    size=10, fill="#fdf3f2", stroke=HOT, sw=1.3))
    render(os.path.join(IMG, "foldback-hyst.svg"), W, H, *f)


# ── 6. Машина станів теплового регулятора ────────────────────────────────────
def fig_thermal_fsm():
    """Стани: COLD_WAIT / (HEATING) / CHARGE / FOLDBACK / STOP / FAULT.
    Переходи за температурою найгарячішої комірки й за відмовою давача."""
    W, H = 820, 470
    f = [text(W / 2, 30, "Машина станів теплового регулятора заряду", size=16, bold=True)]

    # координати станів
    S = {
        "COLD":   (150, 130, "COLD_WAIT", COOL, "T < 0°\nгрій / чекай"),
        "CHARGE": (410, 130, "CHARGE",    OK,   "0..35°\nповний струм"),
        "FOLD":   (660, 130, "FOLDBACK",  "#caa24a", "35..45°\nзрізаю струм"),
        "STOP":   (410, 300, "STOP",      HOT,  "≥45° (гіст.)\nструм = 0"),
        "FAULT":  (660, 340, "FAULT",     POS,  "давач збрехав\nбезпечний нуль"),
    }
    rw, rh = 150, 64
    def node(key):
        cx, cy, lab, col, sub = S[key]
        f.append(rect(cx - rw / 2, cy - rh / 2, rw, rh, fill="#fff", stroke=col, sw=2.0))
        f.append(text(cx, cy - 8, lab, size=12.5, color=col, bold=True))
        for j, ln in enumerate(sub.split("\n")):
            f.append(text(cx, cy + 10 + j * 13, ln, size=9, color=MUTED))
    for k in S:
        node(k)

    def edge(a, b, lab, col=INK, curve=0):
        ax, ay = S[a][0], S[a][1]
        bx, by = S[b][0], S[b][1]
        # точки на межах прямокутників (грубо — по центрах із зсувом)
        f.append(arrow(ax, ay, bx, by, color=col, sw=1.7))
        mx, my = (ax + bx) / 2, (ay + by) / 2 + curve
        f.append(text(mx, my - 4, lab, size=9, color=col, bold=True))

    # головна лінія
    f.append(arrow(S["COLD"][0] + rw / 2, S["COLD"][1], S["CHARGE"][0] - rw / 2, S["CHARGE"][1], color=OK, sw=1.9))
    f.append(text((S["COLD"][0] + S["CHARGE"][0]) / 2, S["COLD"][1] - 12, "потеплішало >2°", size=9, color=OK, bold=True))
    f.append(arrow(S["CHARGE"][0] + rw / 2, S["CHARGE"][1], S["FOLD"][0] - rw / 2, S["FOLD"][1], color="#caa24a", sw=1.9))
    f.append(text((S["CHARGE"][0] + S["FOLD"][0]) / 2, S["CHARGE"][1] - 12, ">35°", size=9, color="#caa24a", bold=True))
    # назад FOLD->CHARGE (гістерезис)
    f.append(arrow(S["FOLD"][0] - rw / 2, S["FOLD"][1] + 16, S["CHARGE"][0] + rw / 2, S["CHARGE"][1] + 16, color=MUTED, sw=1.4))
    f.append(text((S["CHARGE"][0] + S["FOLD"][0]) / 2, S["FOLD"][1] + 34, "<33°", size=9, color=MUTED))
    # FOLD->STOP
    f.append(arrow(S["FOLD"][0], S["FOLD"][1] + rh / 2, S["STOP"][0] + rw / 2 + 4, S["STOP"][1] - rh / 2, color=HOT, sw=1.8))
    f.append(text(S["FOLD"][0] - 30, S["STOP"][1] - 40, "≥45°", size=9, color=HOT, bold=True))
    # STOP->CHARGE (охолов)
    f.append(arrow(S["STOP"][0], S["STOP"][1] - rh / 2, S["CHARGE"][0], S["CHARGE"][1] + rh / 2, color=MUTED, sw=1.5))
    f.append(text(S["STOP"][0] + 36, (S["STOP"][1] + S["CHARGE"][1]) / 2, "охолов <42°", size=9, color=MUTED))
    # CHARGE->COLD (похолодало)
    f.append(arrow(S["CHARGE"][0] - rw / 2, S["CHARGE"][1] + 18, S["COLD"][0] + rw / 2, S["COLD"][1] + 18, color=COOL, sw=1.4))
    f.append(text((S["COLD"][0] + S["CHARGE"][0]) / 2, S["CHARGE"][1] + 34, "<0°", size=9, color=COOL))

    # будь-який стан -> FAULT (символічно — товста червона шина знизу)
    f.append(line(150, 410, 660, 410, color=POS, sw=2.2, dash="6 5"))
    for sx in (150, 410, 660):
        f.append(line(sx, 410, sx, 405, color=POS, sw=1.4))
    f.append(arrow(660, 410, S["FAULT"][0], S["FAULT"][1] + rh / 2 + 4, color=POS, sw=1.8))
    f.append(text(300, 426, "обрив / КЗ / абсурдне значення давача → FAULT з будь-якого стану", size=9.5, color=POS, bold=True))

    render(os.path.join(IMG, "thermal-fsm.svg"), W, H, *f)


# ── 7. Q10 проти енергії активації (вставка math) ────────────────────────────
def fig_q10_vs_ea():
    """Температурний коефіцієнт Q10 як функція енергії активації Ea (коло 25°C).
    «×2 на +10°C» правдиве лише у вузькій смузі Ea — саме там, де лежить SEI."""
    import math
    R = 8.314
    T = 298.15
    def q10(Ea):                       # Ea у Дж/моль
        return math.exp((Ea / R) * (1.0 / T - 1.0 / (T + 10.0)))

    W, H = 780, 430
    f = [text(W / 2, 30, "Q10 росте з висотою бар'єра: «×2» — лише у смузі SEI", size=16, bold=True)]

    # осі
    ox, oy = 95, 350
    axw, axh = 590, 270
    ea_min, ea_max = 10.0, 90.0        # кДж/моль
    q_min, q_max = 1.0, 3.6
    def ex(ea): return ox + (ea - ea_min) / (ea_max - ea_min) * axw
    def ey(q):  return oy - (q - q_min) / (q_max - q_min) * axh

    # зелена смуга SEI (50..55 кДж/моль) — позаду кривої
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
             'fill-opacity="0.16"/>' % (ex(50), oy - axh, ex(55) - ex(50), axh, OK))
    f.append(text((ex(50) + ex(55)) / 2, oy - axh - 6, "SEI літію", size=10, color=OK, bold=True))

    # горизонталь Q10 = 2 («правило вдвічі»)
    f.append(line(ox, ey(2.0), ox + axw, ey(2.0), color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(ox - 8, ey(2.0) + 4, "Q10=2", size=10, color=MUTED, anchor="end", bold=True))

    # осі-стрілки
    f.append(arrow(ox, oy, ox + axw + 6, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh - 6, color=INK, sw=1.8))
    f.append(text(ox + axw, oy + 28, "енергія активації Ea, кДж/моль", size=11, color=INK, anchor="end"))
    f.append('<text x="%d" y="%d" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %d %d)">Q10 (×швидкості на +10°C)</text>'
             % (38, oy - axh / 2, FONT, INK, 38, oy - axh / 2))

    # поділки по осі Ea
    for ea in (10, 30, 50, 70, 90):
        f.append(line(ex(ea), oy, ex(ea), oy + 5, color=INK, sw=1.2))
        f.append(text(ex(ea), oy + 18, str(ea), size=9.5, color=MUTED))
    for q in (1, 2, 3):
        f.append(line(ox - 5, ey(q), ox, ey(q), color=INK, sw=1.2))
        f.append(text(ox - 10, ey(q) + 4, str(q), size=9.5, color=MUTED, anchor="end"))

    # сама крива Q10(Ea)
    pts = []
    ea = ea_min
    while ea <= ea_max + 0.01:
        pts.append((ex(ea), ey(q10(ea * 1000.0))))
        ea += 1.0
    path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, POS))

    # маркер у центрі смуги SEI
    qx, qy = ex(52.5), ey(q10(52500.0))
    f.append(circle(qx, qy, 4.5, fill=POS, stroke="#fff", sw=1.6))

    f.append(fitbox(ex(12), oy - axh + 6, 196, 46,
                    "Нижчий бар'єр → пологіша крива:\nнаївне «вдвічі» переоцінює шкоду.",
                    size=9.5, fill="#fff", stroke=MUTED, sw=1.2))
    f.append(fitbox(ox, oy + 38, axw, 28,
                    "«×2 на +10°C» — не константа, а наслідок типової Ea літію (~50–55 кДж/моль).",
                    size=10.5, fill="#eafaf0", stroke=OK, sw=1.3))
    render(os.path.join(IMG, "q10-vs-ea.svg"), W, H, *f)


# ── NTC проти термопари: чому в embedded переміг опір (вставка hist) ──────────
def fig_ntc_vs_thermocouple():
    """Дві колонки. Ліворуч NTC: один резистор у дільнику → вольти прямо в АЦП.
    Праворуч термопара: мікровольти → підсилювач + компенсація холодного спаю.
    Вага фігури — показати, чому для близьких до кімнатної температур пакета
    великий розмах опору зручніший за мізерний термо-сигнал."""
    W, H = 820, 430
    f = [text(W / 2, 30, "Чому в embedded переміг опір, а не термопара", size=16, bold=True)]

    colw = 350
    lx = 40             # ліва колонка — NTC
    rx = W - 40 - colw  # права колонка — термопара
    top = 56
    bot = H - 58

    f.append(rect(lx, top, colw, bot - top, fill="#eafaf0", stroke=OK, sw=1.8))
    f.append(rect(rx, top, colw, bot - top, fill="#fdf3f2", stroke=HOT, sw=1.8))
    f.append(text(lx + colw / 2, top + 24, "NTC-термістор", size=14, color=OK, bold=True))
    f.append(text(rx + colw / 2, top + 24, "Термопара", size=14, color=HOT, bold=True))

    # ── ЛІВО: дільник NTC → АЦП ──
    dx = lx + 64
    dy = top + 52
    f.append(text(dx, dy, "Vref", size=10.5, color=MUTED))
    f.append(line(dx, dy + 6, dx, dy + 26, color=INK, sw=1.6))
    f.append(rect(dx - 16, dy + 26, 32, 30, fill="#fff", stroke=INK, sw=1.6))
    f.append(text(dx, dy + 45, "R", size=11, color=INK, bold=True))
    f.append(line(dx, dy + 56, dx, dy + 70, color=INK, sw=1.6))
    f.append(rect(dx - 16, dy + 70, 32, 30, fill="#eafaf0", stroke=OK, sw=2))
    f.append(text(dx, dy + 89, "NTC", size=9.5, color=OK, bold=True))
    f.append(line(dx, dy + 100, dx, dy + 114, color=INK, sw=1.6))
    f.append(text(dx, dy + 128, "GND", size=10, color=MUTED))
    f.append(arrow(dx + 16, dy + 63, dx + 92, dy + 63, color=INK, sw=2))
    f.append(text(dx + 54, dy + 54, "вольти", size=10, color=OK, bold=True))
    f.append(rect(dx + 92, dy + 43, 84, 40, fill="#fff", stroke=INK, sw=1.8))
    f.append(text(dx + 134, dy + 67, "АЦП", size=12, color=INK, bold=True))

    f.append(fitbox(lx + 18, bot - 96, colw - 36, 78,
                    "~4 % на градус → розмах у кілооми.\n"
                    "Один резистор, два дроти, один канал.\n"
                    "Без підсилювача, без компенсації спаю.",
                    size=10.5, fill="#fff", stroke=OK, sw=1.3))

    # ── ПРАВО: спай → мкВ → підсилювач → АЦП, плюс компенсація спаю ──
    sx = rx + 36
    sy = top + 66
    f.append(line(sx, sy, sx + 24, sy - 13, color="#b8860b", sw=3))
    f.append(line(sx, sy, sx + 24, sy + 13, color=MUTED, sw=3))
    f.append(circle(sx, sy, 4, fill=HOT, stroke=HOT, sw=1))
    f.append(text(sx, sy + 32, "спай", size=10, color=MUTED))
    f.append(arrow(sx + 28, sy, sx + 70, sy, color=INK, sw=1.8))
    f.append(text(sx + 49, sy - 8, "мкВ", size=10, color=HOT, bold=True))
    ax = sx + 72
    f.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f z" fill="#fff" stroke="%s" stroke-width="1.8"/>'
             % (ax, sy - 20, ax, sy + 20, ax + 40, sy, HOT))
    f.append(text(ax + 13, sy + 4, "×100", size=9.5, color=HOT, bold=True))
    f.append(arrow(ax + 42, sy, ax + 84, sy, color=INK, sw=1.8))
    f.append(rect(ax + 84, sy - 20, 80, 40, fill="#fff", stroke=INK, sw=1.8))
    f.append(text(ax + 124, sy + 5, "АЦП", size=12, color=INK, bold=True))
    f.append(rect(sx + 4, sy + 50, 156, 34, fill="#fff", stroke=HOT, sw=1.5))
    f.append(text(sx + 82, sy + 71, "+ давач хол. спаю", size=10, color=HOT, bold=True))

    f.append(fitbox(rx + 18, bot - 96, colw - 36, 78,
                    "~41 мкВ на градус → лише мілівольти.\n"
                    "Треба підсилювати в сотні разів\n"
                    "І ще компенсувати холодний спай.",
                    size=10.5, fill="#fff", stroke=HOT, sw=1.3))

    f.append(fitbox(40, H - 44, W - 80, 30,
                    "Температури пакета близькі до кімнатної й потрібне абсолютне число — "
                    "тут жирний сигнал NTC прямо в АЦП б'є мікровольти термопари.",
                    size=10.5, fill="#eaf0fd", stroke=COOL, sw=1.3))
    render(os.path.join(IMG, "ntc-vs-thermocouple.svg"), W, H, *f)


if __name__ == "__main__":
    fig_heat_flow()
    fig_gradient()
    fig_cooling_ladder()
    fig_signal_chain()
    fig_foldback_hyst()
    fig_thermal_fsm()
    fig_q10_vs_ea()
    fig_ntc_vs_thermocouple()
    print("OK: 8 figures ->", IMG)
