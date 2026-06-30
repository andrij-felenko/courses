# -*- coding: utf-8 -*-
"""Фігури до статті «ESR конденсатора» (book/electronics/analog/esr-capacitor).
Фігури статті:
  model.svg      — модель реального конденсатора: ідеальна ємність + ESR (+ ESL) послідовно
  impedance-v.svg— «галочка» |Z|(f): спад −20 дБ/дек, дно = ESR на резонансі, підйом ESL
  ripple-heat.svg— петля смерті: пульсівний струм → P = I²·ESR → нагрів → ще гірший ESR
  loss-angle.svg — фазори: ідеальний Xc прямо вниз vs реальний Z, нахилений на кут втрат δ
Фігури вставки comp-low-esr-types.md:
  esr-ladder.svg    — драбина класів за ESR: електроліт → low-ESR/полімер → тантал → MLCC → плівка
  parallel-bank.svg — електроліт||кераміка: хто бере яку смугу частот (НЧ-пульсація vs швидкі викиди)
  mlcc-stack.svg    — внутрішня геометрія MLCC: багато коротких широких пластин паралельно → малий ESR/ESL
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ────────────────────────────────────────────────────────
def cap(cx, cy, label=None, col=INK):
    """Символ ідеальної ємності — дві паралельні пластини, виводи горизонтально."""
    g = 7
    out = [line(cx - 22, cy, cx - g, cy, color=col, sw=1.8),
           line(cx - g, cy - 15, cx - g, cy + 15, color=col, sw=2.6),
           line(cx + g, cy - 15, cx + g, cy + 15, color=col, sw=2.6),
           line(cx + g, cy, cx + 22, cy, color=col, sw=1.8)]
    if label:
        out.append(text(cx, cy - 24, label, size=12, color=col, bold=True))
    return "".join(out)


def res(cx, cy, label=None, col=POS):
    """Горизонтальний резистор-зигзаг, виводи по краях (центр cx, ширина ~44)."""
    x0, x1 = cx - 22, cx + 22
    n = 6
    seg = (x1 - x0) / (n + 2)
    amp = 7
    out = [line(x0, cy, x0 + seg, cy, color=col, sw=1.8)]
    xx = x0 + seg
    for i in range(n):
        ny = cy + (amp if i % 2 == 0 else -amp)
        out.append(line(xx, cy if i == 0 else (cy - amp if i % 2 == 1 else cy + amp),
                        xx + seg, ny, color=col, sw=1.8))
        xx += seg
    out.append(line(xx, cy + (amp if (n - 1) % 2 == 0 else -amp), xx + seg, cy, color=col, sw=1.8))
    out.append(line(x1 - seg, cy, x1, cy, color=col, sw=1.8))
    if label:
        out.append(text(cx, cy - 16, label, size=12, color=col, bold=True))
    return "".join(out)


def coil(cx, cy, label=None, col=MUTED):
    """Горизонтальна котушка — чотири дуги-горбики (ESL, паразитна індуктивність)."""
    x0 = cx - 22
    r = 5.5
    out = [line(x0, cy, x0 + 3, cy, color=col, sw=1.8)]
    bx = x0 + 3
    for i in range(4):
        out.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                   'fill="none" stroke="%s" stroke-width="1.8"/>'
                   % (bx, cy, r, r, bx + 2 * r, cy, col))
        bx += 2 * r
    out.append(line(bx, cy, cx + 22, cy, color=col, sw=1.8))
    if label:
        out.append(text(cx, cy - 16, label, size=12, color=col, bold=True))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. model.svg — реальний конденсатор = ідеальна C + ESR (+ ESL) послідовно
# ════════════════════════════════════════════════════════════════════════════
def fig_model():
    W, H = 660, 300
    f = []
    f.append(text(W / 2, 34, "Що ховається в «конденсаторі»", size=16, bold=True))

    # ліворуч — мітка «реальний конденсатор» як одна рамка-обгортка
    bx, by, bw, bh = 70, 96, 520, 96
    f.append(rect(bx, by, bw, bh, fill="#fbfbfc", stroke=MUTED, sw=1.6, rx=12))
    f.append(text(bx + bw / 2, by - 8, "один справжній конденсатор — а всередині три елементи поспіль", size=12, color=MUTED))

    yc = by + bh / 2
    # вивід ліворуч
    f.append(line(40, yc, 92, yc, color=INK, sw=1.8))
    f.append(text(40, yc - 12, "вивід", size=10, color=MUTED, anchor="start"))
    # ESL
    f.append(coil(150, yc, label="ESL", col=MUTED))
    f.append(line(172, yc, 196, yc, color=INK, sw=1.8))
    # ESR
    f.append(res(250, yc, label="ESR", col=POS))
    f.append(line(272, yc, 320, yc, color=INK, sw=1.8))
    # ідеальна C
    f.append(cap(360, yc, label="C", col=NEG))
    f.append(line(382, yc, 560, yc, color=INK, sw=1.8))
    # вивід праворуч
    f.append(text(572, yc - 12, "вивід", size=10, color=MUTED, anchor="end"))

    # підписи знизу — що є що
    f.append(text(150, yc + 44, "індуктивність", size=10, color=MUTED))
    f.append(text(150, yc + 58, "виводів і обкладок", size=10, color=MUTED))
    f.append(text(250, yc + 44, "увесь опір втрат:", size=10, color=POS))
    f.append(text(250, yc + 58, "фольга · виводи · діелектрик", size=10, color=POS))
    f.append(text(360, yc + 44, "чиста ємність —", size=10, color=NEG))
    f.append(text(360, yc + 58, "лише запасає заряд", size=10, color=NEG))

    body, w0, h0 = textbox(W / 2, 256,
                           "ESR — не окрема деталь, а зведений в одне число опір усіх втрат,\nначе маленький резистор, упаяний послідовно з ідеальною ємністю",
                           size=12, color=INK, fill="#fdecea", stroke=POS)
    f.append(body)
    render(os.path.join(IMG, "model.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. impedance-v.svg — «галочка» повного опору від частоти
# ════════════════════════════════════════════════════════════════════════════
def fig_impedance_v():
    W, H = 660, 400
    f = []
    f.append(text(W / 2, 32, "Повний опір конденсатора від частоти", size=16, bold=True))

    ox, oy = 92, 320            # початок осей (низ-ліво)
    axw, axh = 470, 240
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))            # вісь X (частота, log)
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))           # вісь Y (|Z|, log)
    f.append(text(ox + axw - 4, oy + 24, "частота (лог)", size=12, color=INK, anchor="end"))
    f.append(text(ox - 14, oy - axh + 8, "|Z|", size=13, color=INK, bold=True, anchor="end"))
    f.append(text(ox - 14, oy - axh + 24, "(лог)", size=10, color=MUTED, anchor="end"))

    # «галочка»: ліва вітка спадає (ємнісна, −20 дБ/дек), дно = ESR, права росте (ESL, +20 дБ/дек)
    xL, yTopL = ox + 8, oy - axh + 30        # старт лівої гілки (високий |Z| на низькій f)
    xmin, ymin = ox + 250, oy - 60           # дно галочки (резонанс)
    xR, yTopR = ox + axw - 14, oy - axh + 60  # підйом правої гілки
    f.append(line(xL, yTopL, xmin, ymin, color=NEG, sw=2.8))
    f.append(line(xmin, ymin, xR, yTopR, color=MUTED, sw=2.8))

    # пунктирна «ідеальна» ємнісна вітка, що пішла б і далі вниз, якби не ESR
    f.append(line(xmin, ymin, xmin + 90, ymin + 70, color=NEG, sw=1.4, dash="6 5"))
    f.append(text(xmin + 96, ymin + 78, "ідеальна C", size=10, color=NEG, anchor="start"))
    f.append(text(xmin + 96, ymin + 92, "пішла б далі вниз", size=10, color=MUTED, anchor="start"))

    # горизонталь дна = рівень ESR
    f.append(line(ox, ymin, xmin, ymin, color=POS, sw=1.6, dash="5 4"))
    f.append(text(ox + 4, ymin - 8, "ESR — рівень дна", size=11, color=POS, bold=True, anchor="start"))

    # підписи нахилів
    f.append(text(xL + 70, yTopL + 24, "Xc = 1/(2π f C)", size=11, color=NEG, anchor="start"))
    f.append(text(xL + 70, yTopL + 40, "ємнісна: спад", size=10, color=MUTED, anchor="start"))
    f.append(text(xR - 30, yTopR + 4, "ESL: підйом", size=11, color=MUTED, anchor="end"))
    f.append(text(xR - 30, yTopR + 20, "2π f L", size=10, color=MUTED, anchor="end"))

    # точка резонансу
    f.append(circle(xmin, ymin, 4.5, fill="#ffffff", stroke=POS, sw=2.4))
    f.append(text(xmin, oy + 24, "власний резонанс", size=11, color=POS, anchor="middle"))
    f.append(line(xmin, oy, xmin, ymin, color="#e3e6ea", sw=1.2))

    body, w0, h0 = textbox(W / 2, 372,
                           "На резонансі реактивності взаємно гасяться — лишається сам ESR.\nНижче за ESR конденсатор не «коротшає» хоч би яка частота: дно галочки і є ESR",
                           size=11, color=INK, fill="#fdecea", stroke=POS)
    f.append(body)
    render(os.path.join(IMG, "impedance-v.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. ripple-heat.svg — петля саморуйнування від пульсівного струму
# ════════════════════════════════════════════════════════════════════════════
def fig_ripple_heat():
    W, H = 600, 380
    f = []
    f.append(text(W / 2, 32, "Чому конденсатор гріється й гине", size=16, bold=True))

    # чотири вузли по колу
    cxm, cym = W / 2, 200
    nodes = [
        (cxm, 86,  "пульсівний струм\nI тече крізь ESR", NEG),
        (470, 200, "втрати P = I²·ESR\nгріють кристал", POS),
        (cxm, 314, "тепло піднімає\nтемпературу", POS),
        (130, 200, "гарячий ESR\nросте ще більше", POS),
    ]
    boxes = []
    for x, y, s, col in nodes:
        b, w0, h0 = textbox(x, y, s, size=11, color=INK,
                            fill=("#eaf0fd" if col == NEG else "#fdecea"), stroke=col)
        boxes.append((x, y, w0, h0))
        f.append(b)

    # стрілки по колу (за годинниковою)
    def edge(a, b, col):
        ax, ay, aw, ah = boxes[a]
        bx, by, bw, bh = boxes[b]
        # від краю a до краю b — простий прямий відрізок між центрами, обрізаний по «радіусу»
        import math as _m
        dx, dy = bx - ax, by - ay
        d = _m.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        sa = max(aw, ah) / 2 + 6
        sb = max(bw, bh) / 2 + 10
        f.append(arrow(ax + ux * sa, ay + uy * sa, bx - ux * sb, by - uy * sb, color=col, sw=2.4))

    edge(0, 1, POS)
    edge(1, 2, POS)
    edge(2, 3, POS)
    edge(3, 0, POS)

    # центральна підказка
    f.append(text(cxm, cym - 6, "петля", size=12, color=MUTED, bold=True))
    f.append(text(cxm, cym + 10, "розгону", size=12, color=MUTED, bold=True))

    body, w0, h0 = textbox(W / 2, 358,
                           "Поки тепловідвід відводить P швидше, ніж ESR його народжує, петля згасає.\nЯкщо ні — конденсатор закипає, тиск рве корпус. Тому й нормують гранична пульсація",
                           size=10, color=INK, fill="#fbfbfc", stroke=MUTED)
    f.append(body)
    render(os.path.join(IMG, "ripple-heat.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. loss-angle.svg — фазори: ідеальний Xc vs реальний Z, кут втрат δ
# ════════════════════════════════════════════════════════════════════════════
def fig_loss_angle():
    W, H = 600, 380
    f = []
    f.append(text(W / 2, 32, "Кут втрат: наскільки конденсатор «нечистий»", size=16, bold=True))

    ox, oy = 180, 110          # вершина (вузол), звідки ростуть вектори
    # вісь дійсна (вправо) — опір; вісь уявна (вниз) — реактивність ємності
    f.append(arrow(ox, oy, ox + 300, oy, color=INK, sw=1.6))           # R-вісь
    f.append(arrow(ox, oy, ox, oy + 230, color=INK, sw=1.6))          # −X (ємнісна, вниз)
    f.append(text(ox + 296, oy - 10, "опір R (втрати)", size=11, color=INK, anchor="end"))
    f.append(text(ox + 8, oy + 226, "реактивність Xc (запас)", size=11, color=INK, anchor="start"))

    # ідеальний конденсатор: чисто вниз
    f.append(line(ox, oy, ox, oy + 190, color=NEG, sw=2.6, dash="6 5"))
    f.append(text(ox - 8, oy + 150, "ідеал:", size=11, color=NEG, anchor="end"))
    f.append(text(ox - 8, oy + 166, "лише Xc", size=11, color=NEG, anchor="end"))

    # реальний: вниз + трохи вправо (ESR) → вектор Z під кутом
    esr_dx = 86
    zx, zy = ox + esr_dx, oy + 190
    f.append(line(ox, oy, zx, zy, color=POS, sw=2.8))
    f.append(text(zx + 8, zy + 4, "реальний Z", size=12, color=POS, bold=True, anchor="start"))
    # горизонтальна складова ESR (проєкція дна вектора на R-вісь)
    f.append(line(ox, oy + 190, zx, zy, color=MUTED, sw=1.4, dash="4 4"))
    f.append(text(ox + esr_dx / 2, zy + 18, "ESR", size=11, color=POS, bold=True))

    # дуга кута втрат δ біля вертикалі
    f.append('<path d="M %.1f %.1f A 60 60 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (ox, oy + 60, ox + 60 * esr_dx / 190 * 0.95, oy + 60, FIELD))
    f.append(text(ox + 30, oy + 50, "δ", size=15, color=FIELD, bold=True, anchor="middle"))
    f.append(text(ox + 92, oy + 96, "кут втрат δ", size=11, color=FIELD, anchor="start"))
    f.append(text(ox + 92, oy + 112, "tan δ = ESR / Xc", size=11, color=FIELD, anchor="start"))
    f.append(text(ox + 92, oy + 128, "= коефіцієнт втрат (DF)", size=10, color=MUTED, anchor="start"))

    body, w0, h0 = textbox(W / 2, 350,
                           "Чим більший ESR, тим сильніше вектор Z відхиляється від чистої вертикалі —\nтим «брудніший» конденсатор. Кут δ і його тангенс прямо міряють цю нечистоту",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "loss-angle.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. esr-ladder.svg (вставка) — драбина класів за рівнем ESR
# ════════════════════════════════════════════════════════════════════════════
def fig_esr_ladder():
    W, H = 720, 430
    f = []
    f.append(text(W / 2, 30, "Класи конденсаторів за рівнем ESR", size=16, bold=True))

    L, R = 210, 690                 # межі поля смуг
    Tb, Bb = 78, 360
    # шкала ESR: лог, зліва гірше (1 Ом), справа краще (1 мОм)
    f.append(line(L, Bb + 8, R, Bb + 8, color=INK, sw=1.6))
    decades = ["1 Ом", "100 мОм", "10 мОм", "1 мОм"]
    for i, d in enumerate(decades):
        x = L + i * (R - L) / (len(decades) - 1)
        f.append(line(x, Bb + 4, x, Bb + 12, color=INK, sw=1.4))
        f.append(text(x, Bb + 26, d, size=10.5, color=MUTED))
    f.append(text(L, Bb + 44, "← вищий ESR (гірше для струму)", size=10.5, color=MUTED, anchor="start"))
    f.append(text(R, Bb + 44, "нижчий ESR (краще) →", size=10.5, color=MUTED, anchor="end"))

    # класи: (назва, lo_frac, hi_frac, колір, ESL-мітка)
    # frac: 0 = 1 Ом (ліво), 1 = 1 мОм (право)
    classes = [
        ("Алюм. електроліт", 0.04, 0.46, POS,      "ESL висока"),
        ("Тантал",            0.30, 0.60, "#7b5cc4", "ESL середня"),
        ("Плівковий",         0.18, 0.55, NEG,      "ESL низька"),
        ("Low-ESR · полімер", 0.50, 0.82, "#e08e0b", "ESL середня"),
        ("MLCC (кераміка)",   0.72, 0.985, FIELD,   "ESL найнижча"),
    ]
    rowh = (Bb - Tb) / len(classes)
    for i, (name, lo, hi, col, esl) in enumerate(classes):
        yc = Tb + i * rowh + rowh / 2
        x1 = L + lo * (R - L)
        x2 = L + hi * (R - L)
        # назва ліворуч від поля
        f.append(text(L - 12, yc + 4, name, size=12, color=col, bold=True, anchor="end"))
        # смуга діапазону
        f.append(rect(x1, yc - 12, x2 - x1, 24, fill=col, stroke=col, sw=1, rx=12))
        f.append(text((x1 + x2) / 2, yc + 4, esl, size=10.5, color=BG, bold=True))

    body, w0, h0 = textbox(W / 2, 402,
                           "Кожна смуга — типовий розкид ESR класу (ширина = розкид між виробами й ємностями).\nESL-мітка всередині: чим коротший і ширший шлях струму, тим нижча паразитна індуктивність",
                           size=10.5, color=INK, fill="#fbfbfc", stroke=MUTED)
    f.append(body)
    render(os.path.join(IMG, "esr-ladder.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 6. parallel-bank.svg (вставка) — електроліт || кераміка: розподіл за частотою
# ════════════════════════════════════════════════════════════════════════════
def fig_parallel_bank():
    W, H = 720, 410
    f = []
    f.append(text(W / 2, 30, "Електроліт і кераміка паралельно: поділ за частотою", size=16, bold=True))

    ox, oy = 92, 320
    axw, axh = 560, 250
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 4, oy + 22, "частота (лог)", size=12, color=INK, anchor="end"))
    f.append(text(ox - 14, oy - axh + 10, "|Z|", size=13, color=INK, bold=True, anchor="end"))

    # V-крива в координатах осей: повертає список точок
    def vpts(floor_y, res_x, top_y_left, top_y_right):
        x_lo, x_hi = ox + 10, ox + axw - 14
        pts = []
        steps = 60
        for i in range(steps + 1):
            t = i / steps
            x = x_lo + t * (x_hi - x_lo)
            if x <= res_x:
                # ліва (ємнісна) вітка
                tt = (x - x_lo) / max(res_x - x_lo, 1)
                y = top_y_left + (floor_y - top_y_left) * tt
            else:
                tt = (x - res_x) / max(x_hi - res_x, 1)
                y = floor_y - (floor_y - top_y_right) * tt
            pts.append((x, max(min(y, oy - 2), oy - axh + 4)))
        return pts

    res_el = ox + 0.30 * axw
    res_ce = ox + 0.70 * axw
    el = vpts(floor_y=oy - 70, res_x=res_el, top_y_left=oy - axh + 30, top_y_right=oy - 150)
    ce = vpts(floor_y=oy - 130, res_x=res_ce, top_y_left=oy - axh + 100, top_y_right=oy - 90)

    def poly(pts, col, sw, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        s = " ".join("%.1f,%.1f" % p for p in pts)
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, col, sw, d)

    # огинальна (банк) = поточковий мінімум
    env = [(a[0], min(a[1], b[1])) for a, b in zip(el, ce)]
    f.append(poly(env, INK, 5.0))                 # сумарний опір банку — товста
    f.append(poly(el, POS, 2.2))
    f.append(poly(ce, FIELD, 2.2))

    f.append(text(ox + 60, oy - 96, "електроліт", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(ox + axw - 30, oy - 150, "кераміка (MLCC)", size=12, color=FIELD, bold=True, anchor="end"))
    f.append(text(ox + axw / 2, oy - axh + 14, "товста лінія — сумарний опір банку (мінімум із двох)",
                  size=10.5, color=INK))

    # зони знизу
    f.append(text(ox + 0.22 * axw, oy + 22, "НЧ-пульсація", size=11, color=POS))
    f.append(text(ox + 0.22 * axw, oy + 38, "бере електроліт", size=10.5, color=MUTED))
    f.append(text(ox + 0.78 * axw, oy + 22, "швидкі викиди", size=11, color=FIELD))
    f.append(text(ox + 0.78 * axw, oy + 38, "бере кераміка", size=10.5, color=MUTED))

    body, w0, h0 = textbox(W / 2, 388,
                           "Електроліт дає велику ємність — низький опір на низькій частоті, але ESR і ESL швидко стелять його.\nКераміка з малим ESR/ESL підхоплює там, де електроліт уже безпорадний. Разом — низько в усій смузі",
                           size=10, color=INK, fill="#fbfbfc", stroke=MUTED)
    f.append(body)
    render(os.path.join(IMG, "parallel-bank.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 7. mlcc-stack.svg (вставка) — внутрішня геометрія MLCC: чому ESR/ESL найнижчі
# ════════════════════════════════════════════════════════════════════════════
def fig_mlcc_stack():
    W, H = 700, 360
    f = []
    f.append(text(W / 2, 30, "Чому в MLCC ESR і ESL найнижчі", size=16, bold=True))

    bx, by, bw, bh = 190, 78, 320, 150
    f.append(rect(bx, by, bw, bh, fill="#f0ece2", stroke=INK, sw=2, rx=8))
    tw = 34
    f.append(rect(bx - 6, by - 6, tw, bh + 12, fill=MUTED, stroke=INK, sw=1.5, rx=4))
    f.append(rect(bx + bw - tw + 6, by - 6, tw, bh + 12, fill=MUTED, stroke=INK, sw=1.5, rx=4))
    f.append(text(bx - 6 + tw / 2, by - 12, "контакт", size=10, color=MUTED))
    f.append(text(bx + bw - tw / 2 + 6, by - 12, "контакт", size=10, color=MUTED))

    # пластини-гребінка: парні від лівого контакту, непарні від правого
    n = 7
    inner_l = bx + tw + 4
    inner_r = bx + bw - tw - 4
    span = (by + bh - 22) - (by + 22)
    for i in range(n):
        py = by + 22 + i * span / (n - 1)
        if i % 2 == 0:
            f.append(line(inner_l, py, inner_r - 20, py, color=POS, sw=3.4))
        else:
            f.append(line(inner_l + 20, py, inner_r, py, color=NEG, sw=3.4))
    f.append(text(bx + bw / 2, by + bh + 24,
                  "десятки коротких широких пластин — усі паралельно", size=12, color=INK))

    b1, w1, h1 = textbox(180, 300,
                         "багато пластин ПАРАЛЕЛЬНО\nопори діляться → ESR малий",
                         size=11, color=INK, fill="#fdecea", stroke=POS)
    f.append(b1)
    b2, w2, h2 = textbox(515, 300,
                         "шлях струму короткий і широкий\nмала петля → ESL малий, SRF висока",
                         size=11, color=INK, fill="#eaf0fd", stroke=NEG)
    f.append(b2)
    render(os.path.join(IMG, "mlcc-stack.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 8. formula-chain.svg (вставка hist) — як украдена формула обійшла світ
# ════════════════════════════════════════════════════════════════════════════
def fig_formula_chain():
    W, H = 720, 430
    f = []
    f.append(text(W / 2, 30, "Як украдена формула обійшла світ", size=16, bold=True))

    # Верхній ряд — географічний ланцюг із чотирьох вузлів
    y0 = 100
    nodes = [
        (112, "Японія: Rubycon\nсправжній електроліт\n(серії ZA, ZL)", NEG),
        (300, "Китай: інженер\nкопіює формулу\nз пам'яті", MUTED),
        (486, "Тайвань: перебіжчики\nпродають неповну\nверсію дешево", POS),
        (640, "материнські плати,\nвідеокарти, БЖ\nпо світу", POS),
    ]
    cx_list = []
    for cx, s, col in nodes:
        b, w0, h0 = textbox(cx, y0, s, size=10.5, color=INK,
                            fill=("#eaf0fd" if col == NEG else ("#fbfbfc" if col == MUTED else "#fdecea")),
                            stroke=col)
        f.append(b)
        cx_list.append((cx, w0))

    for i in range(3):
        ax, aw = cx_list[i]
        bx, bw = cx_list[i + 1]
        f.append(arrow(ax + aw / 2 + 4, y0, bx - bw / 2 - 6, y0, color=INK, sw=2.2))

    f.append(text((cx_list[1][0] + cx_list[2][0]) / 2, y0 - 44, "загублені присадки", size=10, color=POS, bold=True))
    f.append(text((cx_list[2][0] + cx_list[3][0]) / 2, y0 - 44, "ціна нижча — беруть усі", size=9.5, color=MUTED))

    f.append(line(60, 164, W - 40, 164, color="#e3e6ea", sw=1.2))

    bx, by, bw, bh = 60, 188, 270, 168
    f.append(rect(bx, by, bw, bh, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=10))
    f.append(text(bx + bw / 2, by + 22, "Чого бракувало в електроліті", size=12, color=NEG, bold=True))
    items = [
        "• присадки-пасиватори (фосфати) —",
        "   тримали міцну плівку оксиду",
        "• деполяризатори (аміни) —",
        "   зв'язували зайвий водень",
        "• правильна кислотність pH ≈ 4",
        "   (у браку було лужне pH 7–8)",
    ]
    for i, it in enumerate(items):
        f.append(text(bx + 16, by + 50 + i * 19, it, size=10.5, color=INK, anchor="start"))

    rx = 470
    chain = [
        ("вода роз'їдає алюміній", POS, 200),
        ("росте лише гідроксид Al(OH)₃", POS, 240),
        ("виділяється водень H₂", POS, 280),
        ("ESR злітає · газ роздуває", POS, 320),
        ("банка пухне й рветься", POS, 352),
    ]
    for i, (s, col, yy) in enumerate(chain):
        b, w0, h0 = textbox(rx, yy, s, size=10.5, color=INK, fill="#fdecea", stroke=col)
        f.append(b)
        if i > 0:
            f.append(arrow(rx, chain[i - 1][2] + 11, rx, yy - 11, color=col, sw=2.0))

    render(os.path.join(IMG, "formula-chain.svg"), W, H, *f)


if __name__ == "__main__":
    fig_model()
    fig_impedance_v()
    fig_ripple_heat()
    fig_loss_angle()
    fig_esr_ladder()
    fig_parallel_bank()
    fig_mlcc_stack()
    fig_formula_chain()
    print("OK: 8 фігур у", IMG)
