# -*- coding: utf-8 -*-
"""Фігури до теми «Активні фільтри на ОП» (аналогова електроніка, кутом теорії кіл).
Фігури:
  passive-sag.svg   — пасивне RC «провисає» біля зрізу (Q=0.5); активний фільтр тримає форму (Q=0.707, навіть піком)
  sallen-key.svg    — схема ФНЧ Саллена–Кі: два RC + повторювач, конденсатор зворотного зв'язку «накачує» резонанс
  order-slope.svg    — крутість спаду: 1-й (−20), 2-й (−40), 4-й (−80 дБ/дек); вищий порядок — стрімкіша стіна
  pole-plane.svg    — (вставка math) пара полюсів на s-площині: ω0 = радіус, Q = кут; що вищий Q, то ближче до осі jω (самозбудження)
  cascade-q.svg     — (вставка proj) дві ланки 4-го порядку: низький Q (полога) × високий Q (пік) = рівна полиця Баттерворта
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _axes(p, ox, oy, w, h, xlbl, ylbl):
    """Осі з підписами; повертає нічого, малює в p."""
    p.append(line(ox, oy, ox + w, oy, color=INK, sw=1.8))          # X
    p.append(line(ox, oy, ox, oy - h, color=INK, sw=1.8))          # Y
    p.append(text(ox + w, oy + 18, xlbl, size=12, color=MUTED, anchor="end"))
    p.append(text(ox - 6, oy - h - 6, ylbl, size=12, color=MUTED, anchor="middle"))


def passive_sag():
    """Магнітудна характеристика біля зрізу: пасивне RC провисає (Q=0.5),
    активний другого порядку тримає рівну полицю (Q=0.707) або навіть із піком."""
    W, H = 720, 380
    p = []
    ox, oy, gw, gh = 90, 300, 560, 230
    _axes(p, ox, oy, gw, gh, "частота (log)", "підсилення")

    # рівень 0 дБ (полиця пропускання)
    flat_y = oy - gh + 40
    p.append(line(ox, flat_y, ox + gw, flat_y, color=MUTED, sw=1, dash="4 4"))
    p.append(text(ox - 8, flat_y + 4, "0 дБ", size=11, color=MUTED, anchor="end"))

    # вертикаль частоти зрізу
    fc_x = ox + gw * 0.52
    p.append(line(fc_x, oy, fc_x, flat_y - 50, color=MUTED, sw=1, dash="3 3"))
    p.append(text(fc_x, oy + 18, "f зрізу", size=11, color=MUTED))

    # три криві: будуємо як |H| другого порядку з різним Q, у дБ, по log-осі
    def curve(Q, col, sw, dash=None):
        pts = []
        N = 140
        for k in range(N + 1):
            # лог-вісь: октава ліворуч і праворуч від зрізу
            dec = -1.6 + 3.4 * k / N           # decades відносно зрізу
            r = 10 ** dec                       # ω/ωc
            mag = 1.0 / math.sqrt((1 - r * r) ** 2 + (r / Q) ** 2)
            db = 20 * math.log10(mag)
            xx = fc_x + (gw * 0.30) * dec       # px на декаду
            yy = flat_y - db * 3.1              # px на дБ (вниз — менше)
            if ox <= xx <= ox + gw and yy <= oy:
                pts.append((xx, yy))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        extra = ' stroke-dasharray="%s"' % dash if dash else ''
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, col, sw, extra))

    curve(0.50, POS, 2.6)        # пасивне RC×RC — провисає
    curve(0.707, FIELD, 2.6)     # Баттерворт — максимально рівно
    curve(2.0, NEG, 2.0, dash="6 3")   # з піком — резонанс, який пасив не вміє

    # підписи кривих
    p.append(text(ox + 150, flat_y - 6, "Q = 0.707 — рівна полиця (Баттерворт)", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(text(ox + 150, oy - 28, "Q = 0.5 — пасивне RC×RC: провисає рано", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(fc_x + 70, flat_y - 58, "Q = 2 — пік (резонанс)", size=12, color=NEG, bold=True, anchor="start"))

    b, _, _ = textbox(W / 2, 354,
                      "Два пасивні RC підряд дають Q = 0.5 — характеристика провисає ще до зрізу.\n"
                      "Активна ланка задає Q вільно: рівну полицю Баттерворта чи навіть пік — без котушки.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'passive-sag.svg'), W, H, *p,
           title="Чому пасивному RC бракує Q, а активному — ні")


def sallen_key():
    """Схема ФНЧ Саллена–Кі: R1–R2 послідовно, C2 на землю, повторювач,
    C1 із виходу назад у середину — додатний ЗЗ, що «накачує» резонанс."""
    W, H = 720, 400
    p = []
    yline = 180

    # вхід
    p.append(text(40, yline - 14, "вхід", size=12, color=MUTED, anchor="start"))
    p.append(arrow(38, yline, 78, yline, color=INK, sw=2))

    # R1
    def res(x, y, lbl):
        out = [rect(x, y - 11, 54, 22, fill=FILL, stroke=LINE, sw=1.6, rx=3),
               text(x + 27, y + 5, lbl, size=12, bold=True)]
        return out
    p += res(80, yline, "R1")
    p.append(line(134, yline, 178, yline, color=INK, sw=1.8))
    nodeA = 178
    p.append(circle(nodeA, yline, 3.5, fill=INK, stroke=INK))
    p += res(nodeA + 4, yline, "R2")
    p.append(line(nodeA + 58, yline, 300, yline, color=INK, sw=1.8))
    nodeB = 300
    p.append(circle(nodeB, yline, 3.5, fill=INK, stroke=INK))

    # C2 з вузла B на землю
    def cap_v(x, y0, y1, lbl):
        ym = (y0 + y1) / 2
        out = [line(x, y0, x, ym - 6, color=INK, sw=1.8),
               line(x - 14, ym - 6, x + 14, ym - 6, color=INK, sw=2.2),
               line(x - 14, ym + 6, x + 14, ym + 6, color=INK, sw=2.2),
               line(x, ym + 6, x, y1, color=INK, sw=1.8),
               text(x + 20, ym + 4, lbl, size=12, bold=True, anchor="start", color=NEG)]
        return out
    p += cap_v(nodeB, yline, yline + 90, "C2")
    # земля
    gy = yline + 90
    p.append(line(nodeB - 16, gy, nodeB + 16, gy, color=INK, sw=2))
    p.append(line(nodeB - 10, gy + 6, nodeB + 10, gy + 6, color=INK, sw=2))
    p.append(line(nodeB - 5, gy + 12, nodeB + 5, gy + 12, color=INK, sw=2))

    # ОП-повторювач (трикутник)
    ax = 360
    ay = yline
    p.append(line(nodeB, yline, ax, ay, color=INK, sw=1.8))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (ax, ay - 34, ax, ay + 34, ax + 70, ay, FILL, LINE))
    p.append(text(ax + 18, ay - 12, "+", size=18, color=POS, bold=True))
    p.append(text(ax + 18, ay + 22, "−", size=18, color=NEG, bold=True))
    p.append(text(ax + 30, ay + 5, "×1", size=12, bold=True))
    # вихід
    outx = ax + 70
    p.append(line(outx, ay, outx + 80, ay, color=INK, sw=1.8))
    nodeOut = outx + 80
    p.append(circle(nodeOut, ay, 3.5, fill=INK, stroke=INK))
    p.append(arrow(nodeOut, ay, nodeOut + 40, ay, color=INK, sw=2))
    p.append(text(nodeOut + 44, ay - 14, "вихід", size=12, color=MUTED, anchor="start"))
    # від'ємний ЗЗ повторювача (вихід → інв. вхід)
    p.append(line(nodeOut, ay, nodeOut, ay + 50, color=MUTED, sw=1.4))
    p.append(line(nodeOut, ay + 50, ax - 14, ay + 50, color=MUTED, sw=1.4))
    p.append(line(ax - 14, ay + 50, ax - 14, ay + 22, color=MUTED, sw=1.4))
    p.append(line(ax - 14, ay + 22, ax, ay + 22, color=MUTED, sw=1.4))

    # C1 — додатний ЗЗ: з виходу назад у вузол A (зверху)
    fy = yline - 90
    p.append(line(nodeOut, ay, nodeOut, fy, color=POS, sw=2))
    p.append(line(nodeOut, fy, nodeA, fy, color=POS, sw=2))
    # горизонтальний конденсатор у цій гілці
    cmx = (nodeOut + nodeA) / 2
    p.append(line(cmx - 6, fy - 14, cmx - 6, fy + 14, color=POS, sw=2.4))
    p.append(line(cmx + 6, fy - 14, cmx + 6, fy + 14, color=POS, sw=2.4))
    p.append(text(cmx, fy - 20, "C1 — додатний ЗЗ", size=12, bold=True, color=POS))
    p.append(line(nodeA, fy, nodeA, yline, color=POS, sw=2))
    p.append(circle(nodeA, fy, 3.5, fill=POS, stroke=POS))

    # пояснення вузлів
    p.append(text(nodeA - 8, yline + 28, "вузол A", size=11, color=MUTED, anchor="end"))
    p.append(text(nodeB + 22, yline - 14, "вузол B", size=11, color=MUTED, anchor="start"))

    b, _, _ = textbox(W / 2, 372,
                      "Два RC дають спад другого порядку; повторювач не навантажує їх і повторює вузол B.\n"
                      "Конденсатор C1 повертає вихід угору в вузол A — цей додатний ЗЗ і «накачує» резонанс (Q).",
                      size=12, fill="#fdecea", stroke=POS)
    p.append(b)
    render(os.path.join(OUT, 'sallen-key.svg'), W, H, *p,
           title="ФНЧ Саллена–Кі: два RC, повторювач і конденсатор додатного ЗЗ")


def order_slope():
    """Крутість спаду в смузі затримання: 1-й, 2-й, 4-й порядок — −20/−40/−80 дБ/дек."""
    W, H = 720, 380
    p = []
    ox, oy, gw, gh = 90, 300, 560, 230
    _axes(p, ox, oy, gw, gh, "частота (декади →)", "підсилення (дБ)")

    flat_y = oy - gh + 30
    p.append(line(ox, flat_y, ox + gw, flat_y, color=MUTED, sw=1, dash="4 4"))
    p.append(text(ox - 8, flat_y + 4, "0 дБ", size=11, color=MUTED, anchor="end"))

    fc_x = ox + gw * 0.30
    p.append(line(fc_x, oy, fc_x, flat_y, color=MUTED, sw=1, dash="3 3"))
    p.append(text(fc_x, oy + 18, "f зрізу", size=11, color=MUTED))

    px_per_decade = (ox + gw - fc_x) / 3.0   # 3 декади поміщаємо праворуч
    bottom = oy - 6                           # куди лінії спадають (над віссю X)
    px_per_db = (bottom - flat_y) / 60.0      # 60 дБ запасу по висоті

    def slope(db_per_dec, col, lbl):
        # пряма зі спаду db_per_dec; обриваємо там, де впираємось у дно
        x1, y1 = fc_x, flat_y
        # на скільки декад опуститься до дна
        dd_max = (60.0) / abs(db_per_dec)
        dd_end = min(3.0, dd_max)
        x2 = fc_x + dd_end * px_per_decade
        y2 = flat_y + abs(db_per_dec) * dd_end * px_per_db
        p.append(line(x1, y1, x2, y2, color=col, sw=2.4))
        # підпис уздовж лінії, трохи нижче її середини
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        p.append(text(mx + 10, my + 14, lbl, size=12, bold=True, color=col, anchor="start"))

    # полиця пропускання — спільний рівний відрізок до зрізу
    p.append(line(ox, flat_y, fc_x, flat_y, color=INK, sw=2.4))
    slope(-20, FIELD, "1-й: −20 дБ/дек")
    slope(-40, NEG, "2-й: −40 дБ/дек")
    slope(-80, POS, "4-й: −80 дБ/дек")

    b, _, _ = textbox(W / 2, 354,
                      "Кожен порядок фільтра додає −20 дБ/декаду до спаду в смузі затримання.\n"
                      "Складаючи ланки другого порядку, будуємо стрімку «стіну» — без жодної котушки.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'order-slope.svg'), W, H, *p,
           title="Порядок фільтра й крутість спаду: −20 дБ/дек на кожен порядок")


def pole_plane():
    """s-площина: пара комплексно-спряжених полюсів ФНЧ другого порядку.
    Відстань полюса від початку = ω0; кут від уявної осі задає Q (cosθ = 1/2Q,
    рахуючи від від'ємної дійсної півосі). Що вищий Q, то ближче полюси до осі jω;
    на осі (Q→∞) коло самозбуджується. Показуємо три Q: 0.5, 0.707, висока."""
    W, H = 720, 430
    p = []
    cx, cy = 300, 215          # початок координат (0,0) s-площини
    Rrad = 150.0               # піксельний радіус для ω0 (однаковий для всіх Q)

    # осі: σ (дійсна, горизонталь) і jω (уявна, вертикаль)
    p.append(line(cx - 250, cy, cx + 110, cy, color=INK, sw=1.8))     # дійсна вісь σ
    p.append(arrow(cx + 70, cy, cx + 110, cy, color=INK, sw=1.8))
    p.append(text(cx + 116, cy + 5, "σ", size=14, color=MUTED, anchor="start", italic=True))
    p.append(line(cx, cy + 170, cx, cy - 190, color=INK, sw=1.8))     # уявна вісь jω
    p.append(arrow(cx, cy - 150, cx, cy - 190, color=INK, sw=1.8))
    p.append(text(cx + 8, cy - 184, "jω", size=14, color=MUTED, anchor="start", italic=True))
    p.append(text(cx + 8, cy + 16, "0", size=12, color=MUTED, anchor="start"))

    # дуга кола радіуса ω0 (на ньому лежать усі полюси — ω0 спільне)
    import math as _m
    arc = []
    for k in range(61):
        th = _m.pi / 2 + (_m.pi / 2) * k / 60      # від +jω-осі до −σ-осі (верхня ліва чверть)
        arc.append((cx + Rrad * _m.cos(th), cy - Rrad * _m.sin(th)))
    da = "M" + " L".join("%.1f %.1f" % q for q in arc)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4 4"/>' % (da, MUTED))
    p.append(text(cx - Rrad * 0.72 - 4, cy - Rrad * 0.72 - 8, "радіус = ω0", size=11, color=MUTED, anchor="middle"))

    # полюс для заданого Q: дійсна частина = −ω0/(2Q), уявна = ω0·√(1−1/4Q²)
    def pole_for(Q, col, lbl, lbldy):
        sigma = -1.0 / (2 * Q)                       # у частках ω0
        if Q <= 0.5:
            # дійсні полюси (перегашене): обидва на від'ємній дійсній осі
            disc = _m.sqrt(0.25 / (Q * Q) - 1.0) if Q < 0.5 else 0.0
            x1 = sigma - disc; x2 = sigma + disc      # у частках ω0 (обидва ≤0)
            for xr in (x1, x2):
                px = cx + Rrad * xr
                p.append(_xmark(px, cy, col))
            p.append(text(cx + Rrad * sigma, cy + 26 + lbldy, lbl, size=12, color=col, bold=True))
            return
        wd = _m.sqrt(1.0 - 1.0 / (4 * Q * Q))         # уявна частина у частках ω0
        px = cx + Rrad * sigma
        py = cy - Rrad * wd
        py2 = cy + Rrad * wd
        # лінія від початку до верхнього полюса — показує радіус ω0
        p.append(line(cx, cy, px, py, color=col, sw=1.4))
        p.append(_xmark(px, py, col))
        p.append(_xmark(px, py2, col))               # спряжений
        p.append(text(px - 6, py - 10, lbl, size=12, color=col, bold=True, anchor="end"))

    def _xmark(x, y, col):
        d = 6
        return (line(x - d, y - d, x + d, y + d, color=col, sw=2.4) +
                line(x - d, y + d, x + d, y - d, color=col, sw=2.4))

    pole_for(0.5, POS, "Q = 0.5 (на дійсній осі)", 0)
    pole_for(0.707, FIELD, "Q = 0.707", 0)
    pole_for(3.0, NEG, "Q = 3 (близько до jω)", 0)

    # кут θ біля початку (для Q=0.707): між −σ-піввіссю й променем до полюса
    Qd = 0.707
    th = _m.acos(1.0 / (2 * Qd))                      # кут від від'ємної дійсної осі
    p.append(text(cx - 40, cy - 18, "θ", size=14, color=FIELD, bold=True, italic=True))
    p.append(text(cx - 150, cy - 150, "cos θ = 1 / (2Q)", size=12, color=INK, anchor="start", bold=True))

    # стрілка «вище Q → до осі»
    p.append(arrow(cx - 70, cy - 130, cx - 18, cy - 175, color=NEG, sw=1.6))
    p.append(text(cx - 95, cy - 120, "Q ↑", size=12, color=NEG, bold=True, anchor="end"))

    b, _, _ = textbox(W / 2, 400,
                      "Полюси ланки другого порядку лежать на колі радіуса ω0; кут θ задає Q.\n"
                      "Q = 0.5 — полюси на дійсній осі (перегашене); більший Q повертає їх до осі jω.\n"
                      "На самій осі jω (Q → ∞) коло самозбуджується — стає генератором.",
                      size=12, fill="#eef2f7", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'pole-plane.svg'), W, H, *p,
           title="Полюси на s-площині: ω0 — радіус, Q — кут до осі jω")


def sk_buffer_era():
    """Той самий буфер у топології Саллена–Кі через три епохи деталі:
    ламповий катодний повторювач (1955) → транзисторний → операційний.
    Топологія описана через ФУНКЦІЮ (×1, високий вхід, низький вихід),
    тому деталь міняється, а схема лишається."""
    W, H = 760, 410
    p = []

    # верхня плашка — спільна функція буфера
    bb, _, _ = textbox(W / 2, 46,
                       "Топологія бачить лише ФУНКЦІЮ буфера:  підсилення ×1 · вхід ≈ ∞ · вихід ≈ 0",
                       size=13, fill="#eef7f0", stroke=FIELD, bold=True)
    p.append(bb)

    cx = [150, 380, 610]               # центри трьох панелей
    pty, pby = 92, 318                 # верх/низ області панелей
    for x in cx:
        p.append(rect(x - 108, pty, 216, pby - pty, fill=BG, stroke=MUTED, sw=1.3, rx=8))

    def in_arrow(x):
        p.append(arrow(x - 100, 150, x - 68, 150, color=INK, sw=1.8))
        p.append(text(x - 100, 138, "вхід", size=10, color=MUTED, anchor="start"))

    def out_arrow(x):
        p.append(line(x + 60, 150, x + 96, 150, color=INK, sw=1.8))
        p.append(arrow(x + 96, 150, x + 100, 150, color=INK, sw=1.8))
        p.append(text(x + 100, 138, "вихід ×1", size=10, color=MUTED, anchor="end"))

    def ground(x, y):
        p.append(line(x - 12, y, x + 12, y, color=INK, sw=2))
        p.append(line(x - 7, y + 5, x + 7, y + 5, color=INK, sw=2))
        p.append(line(x - 3, y + 10, x + 3, y + 10, color=INK, sw=2))

    # ── панель 1: ламповий катодний повторювач (триод) ────────────────────
    x = cx[0]
    p.append(text(x, pty + 22, "1955 · лампа", size=13, color=POS, bold=True))
    p.append(text(x, pty + 40, "катодний повторювач", size=11, color=MUTED))
    in_arrow(x); out_arrow(x)
    # колба триода
    p.append(circle(x, 168, 34, fill=FILL, stroke=INK, sw=1.8))
    # анод (зверху), сітка (вхід зліва), катод (вихід знизу)
    p.append(line(x - 14, 150, x + 14, 150, color=INK, sw=2.4))         # анодна пластина
    p.append(line(x, 134, x, 150, color=INK, sw=1.8))                  # вивід анода вгору
    p.append(line(x, 116, x, 134, color=INK, sw=1.8))
    p.append(text(x + 18, 130, "+B", size=10, color=MUTED, anchor="start"))
    # сітка — штрихова, вхід зліва
    p.append(line(x - 30, 170, x - 10, 170, color=INK, sw=1.6, dash="3 3"))
    p.append(line(x - 68, 150, x - 68, 170, color=INK, sw=1.8))
    p.append(line(x - 68, 170, x - 30, 170, color=INK, sw=1.8))
    p.append(text(x - 40, 164, "сітка", size=9, color=MUTED, anchor="middle"))
    # катод — вихід знизу
    p.append(line(x - 10, 188, x + 10, 188, color=INK, sw=2.4))
    p.append(line(x, 188, x, 210, color=INK, sw=1.8))
    p.append(line(x, 210, x + 60, 210, color=INK, sw=1.8))             # до виходу
    p.append(line(x + 60, 210, x + 60, 150, color=INK, sw=1.8))
    p.append(circle(x + 60, 150, 3, fill=INK, stroke=INK))
    p.append(text(x + 8, 206, "катод", size=9, color=MUTED, anchor="start"))
    # катодний резистор на землю
    p.append(line(x, 210, x, 230, color=INK, sw=1.8))
    p.append(rect(x - 9, 230, 18, 30, fill=FILL, stroke=LINE, sw=1.4, rx=3))
    p.append(line(x, 260, x, 282, color=INK, sw=1.8))
    ground(x, 282)
    p.append(text(x, 305, "K ≈ µ/(µ+1) < 1", size=11, color=INK, bold=True))

    # ── панель 2: транзисторний повторювач ───────────────────────────────
    x = cx[1]
    p.append(text(x, pty + 22, "транзистор", size=13, color=NEG, bold=True))
    p.append(text(x, pty + 40, "емітерний / витоковий", size=11, color=MUTED))
    in_arrow(x); out_arrow(x)
    # коло транзистора
    p.append(circle(x, 168, 30, fill=FILL, stroke=INK, sw=1.8))
    # база — вертикальна лінія всередині
    p.append(line(x - 6, 150, x - 6, 186, color=INK, sw=2.6))
    p.append(line(x - 30, 168, x - 6, 168, color=INK, sw=1.8))          # вхід у базу
    p.append(line(x - 68, 150, x - 68, 168, color=INK, sw=1.8))
    p.append(line(x - 68, 168, x - 30, 168, color=INK, sw=1.8))
    p.append(text(x - 40, 162, "база", size=9, color=MUTED, anchor="middle"))
    # колектор угору (+живлення)
    p.append(line(x - 6, 156, x + 18, 150, color=INK, sw=1.8))
    p.append(line(x + 18, 150, x + 18, 120, color=INK, sw=1.8))
    p.append(text(x + 22, 130, "+V", size=10, color=MUTED, anchor="start"))
    # емітер униз → вихід
    p.append(line(x - 6, 180, x + 18, 186, color=INK, sw=1.8))
    p.append(line(x + 18, 186, x + 18, 210, color=INK, sw=1.8))
    p.append(line(x + 18, 210, x + 60, 210, color=INK, sw=1.8))
    p.append(line(x + 60, 210, x + 60, 150, color=INK, sw=1.8))
    p.append(circle(x + 60, 150, 3, fill=INK, stroke=INK))
    p.append(text(x - 2, 200, "емітер", size=9, color=MUTED, anchor="end"))
    # емітерний резистор на землю
    p.append(line(x + 18, 210, x + 18, 230, color=INK, sw=1.8))
    p.append(rect(x + 9, 230, 18, 30, fill=FILL, stroke=LINE, sw=1.4, rx=3))
    p.append(line(x + 18, 260, x + 18, 282, color=INK, sw=1.8))
    ground(x + 18, 282)
    p.append(text(x, 305, "вихід «йде» за входом", size=11, color=INK, bold=True))

    # ── панель 3: операційний повторювач ─────────────────────────────────
    x = cx[2]
    p.append(text(x, pty + 22, "операційний ПС", size=13, color=FIELD, bold=True))
    p.append(text(x, pty + 40, "повторювач напруги", size=11, color=MUTED))
    in_arrow(x); out_arrow(x)
    # трикутник ОП
    ax = x - 30
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (ax, 150 - 34, ax, 150 + 34, ax + 70, 150, FILL, LINE))
    p.append(text(ax + 16, 150 - 12, "+", size=17, color=POS, bold=True))
    p.append(text(ax + 16, 150 + 22, "−", size=17, color=NEG, bold=True))
    p.append(text(ax + 30, 150 + 5, "×1", size=12, bold=True))
    # вихід вузол
    nout = ax + 70
    p.append(circle(nout, 150, 3, fill=INK, stroke=INK))
    # від'ємний ЗЗ — вихід назад на інв. вхід
    p.append(line(nout, 150, nout, 200, color=MUTED, sw=1.4))
    p.append(line(nout, 200, ax - 16, 200, color=MUTED, sw=1.4))
    p.append(line(ax - 16, 200, ax - 16, 150 + 22, color=MUTED, sw=1.4))
    p.append(line(ax - 16, 150 + 22, ax, 150 + 22, color=MUTED, sw=1.4))
    p.append(text(x, 305, "точно ×1, вхід ≈ ∞", size=11, color=INK, bold=True))

    # стрілки «деталь міняється» між панелями
    p.append(arrow(cx[0] + 110, 168, cx[1] - 110, 168, color=MUTED, sw=1.6))
    p.append(arrow(cx[1] + 110, 168, cx[2] - 110, 168, color=MUTED, sw=1.6))

    b, _, _ = textbox(W / 2, 384,
                      "Саллен і Кі описали буфер через те, ЩО він робить, а не з ЧОГО зроблений.\n"
                      "Тому лампа змінилася транзистором, далі операційним ПС — а топологія лишилась тією самою.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'sk-buffer-era.svg'), W, H, *p,
           title="Буфер у топології Саллена–Кі: лампа → транзистор → операційний ПС")


def cascade_q():
    """Каскад двох ланок ФНЧ 4-го порядку (Баттерворт): низькодобротна ланка
    (Q=0.541) полого сповзає, високодобротна (Q=1.307) дає пік перед зрізом,
    а їхній ДОБУТОК — рівна полиця Баттерворта 4-го порядку зі спадом −80 дБ/дек.
    Горбик другої ланки рівно затикає раннє провисання першої."""
    W, H = 720, 400
    p = []
    ox, oy, gw, gh = 90, 310, 560, 250
    _axes(p, ox, oy, gw, gh, "частота (log)", "підсилення (дБ)")

    # рівень 0 дБ
    flat_y = oy - gh + 70
    p.append(line(ox, flat_y, ox + gw, flat_y, color=MUTED, sw=1, dash="4 4"))
    p.append(text(ox - 8, flat_y + 4, "0 дБ", size=11, color=MUTED, anchor="end"))

    # вертикаль частоти зрізу fc (обидві ланки на ній: fmul=1 у Баттерворта)
    fc_x = ox + gw * 0.46
    p.append(line(fc_x, oy, fc_x, flat_y - 40, color=MUTED, sw=1, dash="3 3"))
    p.append(text(fc_x, oy + 18, "f зрізу", size=11, color=MUTED))

    px_dec = gw * 0.30        # пікселів на декаду
    px_db = 4.2               # пікселів на дБ

    def stage_db(Q, r):
        # магнітуда ланки 2-го порядку у дБ; r = f/f0
        mag = 1.0 / math.sqrt((1 - r * r) ** 2 + (r / Q) ** 2)
        return 20 * math.log10(mag)

    def plot(fn, col, sw, dash=None):
        pts = []
        N = 160
        for k in range(N + 1):
            dec = -1.3 + 2.6 * k / N           # декади відносно зрізу
            r = 10 ** dec
            db = fn(r)
            xx = fc_x + px_dec * dec
            yy = flat_y - db * px_db
            if ox <= xx <= ox + gw and yy <= oy - 2:
                pts.append((xx, yy))
        if not pts:
            return
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        extra = ' stroke-dasharray="%s"' % dash if dash else ''
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, col, sw, extra))

    Q1, Q2 = 0.5412, 1.3066    # ланки Баттерворта 4-го порядку
    plot(lambda r: stage_db(Q1, r), POS, 2.0, dash="6 3")           # ланка 1 — полога
    plot(lambda r: stage_db(Q2, r), NEG, 2.0, dash="6 3")           # ланка 2 — з піком
    plot(lambda r: stage_db(Q1, r) + stage_db(Q2, r), FIELD, 3.0)   # добуток (сума дБ)

    # підписи кривих
    p.append(text(ox + 8, flat_y + 40, "ланка 1: Q = 0.54 — полого сповзає", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(fc_x + 24, flat_y - 30, "ланка 2: Q = 1.31 — пік", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(ox + 8, flat_y - 14, "добуток — рівна полиця Баттерворта-4", size=11, color=FIELD, bold=True, anchor="start"))

    b, _, _ = textbox(W / 2, 374,
                      "Окремо ланки криві (штрихові): одна полого сповзає, друга дає пік.\n"
                      "Їхній добуток (жирна зелена) — максимально рівна полиця 4-го порядку, спад −80 дБ/дек.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'cascade-q.svg'), W, H, *p,
           title="Каскад різних Q: горбик однієї затикає ямку іншої")


if __name__ == '__main__':
    passive_sag()
    sallen_key()
    order_slope()
    pole_plane()
    sk_buffer_era()
    cascade_q()
    print("OK: 6 figures ->", OUT)
