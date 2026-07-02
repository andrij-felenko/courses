# -*- coding: utf-8 -*-
"""Фігури до теми «Коефіцієнт шуму» (аналогова електроніка, кутом теорії кіл).
Чотири фігури:
  snr-drop.svg     — F = SNR_вх / SNR_вих: ідеальний елемент SNR зберігає, реальний — псує
  noise-floor.svg  — звідки беруться kT₀ і −174 дБм/Гц; реальний шум = підлога + власний внесок
  attenuator-nf.svg— пасивний атенюатор: NF дорівнює його ж втратам L
  friis-chain.svg  — внесок кожного каскаду до F ділиться на добуток підсилень попередніх
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _wiggle(seed):
    """Детермінований псевдошум у [-1,1] — без залежностей."""
    x = math.sin(seed * 12.9898) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


def snr_drop():
    """F = SNR_вх / SNR_вих. Зліва вхід (чистий сигнал на тонкому шумі),
    справа два виходи: ідеальний (та сама тиша) і реальний (шум підрос)."""
    W, H = 720, 380
    p = []
    base_y = 175
    amp = 34

    def trace(x0, w, nlev, col, seed):
        pts_sig, pts_mix = [], []
        N = 80
        for k in range(N + 1):
            xx = x0 + w * k / N
            ph = 2 * math.pi * 2.0 * k / N
            s = math.sin(ph) * amp
            n = _wiggle(k * 1.7 + seed) * amp * nlev
            pts_sig.append((xx, base_y - s))
            pts_mix.append((xx, base_y - s - n))
        d_sig = "M" + " L".join("%.1f %.1f" % q for q in pts_sig)
        d_mix = "M" + " L".join("%.1f %.1f" % q for q in pts_mix)
        out = ['<path d="%s" fill="none" stroke="%s" stroke-width="1" stroke-dasharray="3 3"/>' % (d_sig, MUTED)]
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d_mix, col))
        return out

    # вхід
    p.append(rect(30, 95, 180, 160, fill=BG, stroke=MUTED, sw=1))
    p += trace(40, 160, 0.18, NEG, 10)
    p.append(text(120, 88, "вхід", size=13, bold=True))
    p.append(text(120, 274, "SNR_вх — високий", size=12, color=NEG))

    # підсилювач-трикутник посередині
    ax = 250
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (ax, base_y - 34, ax, base_y + 34, ax + 74, base_y, FILL, LINE))
    p.append(text(ax + 26, base_y + 5, "×G", size=17, bold=True))
    p.append(text(ax + 37, base_y + 58, "+ власний шум", size=12, color=POS))

    # реальний вихід (праворуч згори): шум підріс
    p.append(rect(400, 60, 290, 120, fill=BG, stroke=MUTED, sw=1))
    p += trace(412, 266, 0.52, POS, 33)
    p.append(text(545, 52, "реальний вихід", size=13, bold=True, color=POS))
    p.append(text(545, 172, "SNR_вих нижчий  →  F > 1", size=12, color=POS))

    # ідеальний вихід (праворуч знизу): шум той самий
    p.append(rect(400, 210, 290, 120, fill=BG, stroke=MUTED, sw=1))
    p2_base = base_y
    # малюємо у власній смузі
    pts_sig, pts_mix = [], []
    N = 80
    yb = 270
    for k in range(N + 1):
        xx = 412 + 266 * k / N
        ph = 2 * math.pi * 2.0 * k / N
        s = math.sin(ph) * amp
        n = _wiggle(k * 1.7 + 10) * amp * 0.18
        pts_sig.append((xx, yb - s)); pts_mix.append((xx, yb - s - n))
    d_sig = "M" + " L".join("%.1f %.1f" % q for q in pts_sig)
    d_mix = "M" + " L".join("%.1f %.1f" % q for q in pts_mix)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1" stroke-dasharray="3 3"/>' % (d_sig, MUTED))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d_mix, FIELD))
    p.append(text(545, 202, "ідеальний вихід", size=13, bold=True, color=FIELD))
    p.append(text(545, 322, "SNR_вих = SNR_вх  →  F = 1", size=12, color=FIELD))

    render(os.path.join(OUT, 'snr-drop.svg'), W, H, *p,
           title="Коефіцієнт шуму: на скільки елемент псує SNR")


def noise_floor():
    """Звідки −174 дБм/Гц і як власний шум елемента додається до теплової підлоги."""
    W, H = 700, 380
    p = []
    ox, oy = 110, 310
    ax_h = 240
    p.append(line(ox, oy, ox, oy - ax_h - 10, color=INK, sw=2))
    p.append(text(ox - 64, oy - ax_h / 2, "шум", size=13, bold=True))
    p.append(text(ox - 64, oy - ax_h / 2 + 18, "(дБм/Гц)", size=12, bold=True))

    bx = ox + 30
    bw = 150
    # теплова підлога джерела kT₀ = −174 дБм/Гц
    floor_y = oy - 50
    p.append(rect(bx, floor_y, bw, 50, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    p.append(text(bx + bw / 2, floor_y + 30, "kT₀", size=15, bold=True, color=NEG))
    p.append(text(bx + bw + 10, floor_y + 22, "−174 дБм/Гц", size=13, bold=True, color=NEG, anchor="start"))
    p.append(text(bx + bw + 10, floor_y + 40, "тепловий шум джерела (290 К)", size=11, color=MUTED, anchor="start"))

    # власний внесок елемента згори
    add_h = 70
    add_y = floor_y - add_h
    p.append(rect(bx, add_y, bw, add_h, fill="#fdecea", stroke=POS, sw=1.8, rx=3))
    p.append(text(bx + bw / 2, add_y + add_h / 2 + 5, "+ власний", size=13, bold=True, color=POS))
    p.append(text(bx + bw + 10, add_y + add_h / 2, "внесок елемента", size=12, color=POS, anchor="start"))

    # сумарна верхівка — рівень виходу
    top_y = add_y
    p.append(line(bx - 8, top_y, bx + bw + 8, top_y, color=INK, sw=2.2, dash="5 4"))
    p.append(text(bx + bw / 2, top_y - 12, "рівень шуму на виході", size=12, bold=True))

    # F як відношення (повна висота / підлога)
    fx = bx + bw + 210
    p.append(line(fx, top_y, fx, oy, color=FIELD, sw=2))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>' % (fx - 4, top_y + 6, fx + 4, top_y + 6, fx, top_y, FIELD))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>' % (fx - 4, oy - 6, fx + 4, oy - 6, fx, oy, FIELD))
    p.append(text(fx + 8, (top_y + oy) / 2 - 8, "F =", size=13, bold=True, color=FIELD, anchor="start"))
    p.append(text(fx + 8, (top_y + oy) / 2 + 10, "усе / підлога", size=12, bold=True, color=FIELD, anchor="start"))

    b, _, _ = textbox(W / 2, 356,
                      "Підлога — тепловий шум самого джерела (kT₀ = −174 дБм/Гц при 290 К).\n"
                      "Коефіцієнт шуму F = у скільки разів елемент підняв шум над цією підлогою.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'noise-floor.svg'), W, H, *p,
           title="Шумова підлога kT₀ і власний внесок елемента")


def attenuator_nf():
    """Пасивний атенюатор: сигнал падає в L разів, шум на виході лишається kT₀ — тож NF = L."""
    W, H = 700, 340
    p = []
    cy = 150

    def bars(cx, sig_h, noise_h, lbl):
        out = []
        bw = 46
        b0 = cy + 70
        out.append(rect(cx - bw / 2, b0 - noise_h, bw, noise_h, fill="#eaf0fd", stroke=NEG, sw=1.6))
        out.append(rect(cx - bw / 2, b0 - noise_h - sig_h, bw, sig_h, fill="#fdecea", stroke=POS, sw=1.6))
        out.append(text(cx, b0 + 20, lbl, size=12, bold=True))
        return out

    # вхід: великий сигнал, маленька теплова підлога
    p += bars(120, 110, 22, "вхід")
    p.append(text(120, cy - 78, "сигнал", size=11, color=POS))
    p.append(text(120, cy + 30, "шум kT₀", size=11, color=NEG))

    # атенюатор-прямокутник із L
    axx = 250
    p.append(rect(axx, cy - 28, 90, 56, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(axx + 45, cy - 4, "атенюатор", size=12, bold=True))
    p.append(text(axx + 45, cy + 16, "втрати L", size=12, color=MUTED))
    p.append(arrow(axx + 90, cy, axx + 140, cy, color=INK, sw=2))

    # вихід: сигнал упав у L разів, шум так само kT₀ (тепловий, той самий)
    p += bars(470, 110 / 4.0, 22, "вихід")
    p.append(text(470, cy - 50, "сигнал ÷ L", size=11, color=POS))
    p.append(text(470, cy + 30, "шум так само kT₀", size=11, color=NEG))

    b, _, _ = textbox(W / 2, 312,
                      "Атенюатор тисне сигнал у L разів, але на виході знов стоїть теплова підлога kT₀.\n"
                      "SNR упав рівно в L разів — тому коефіцієнт шуму пасивних втрат: NF = L (у дБ = втрати).",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'attenuator-nf.svg'), W, H, *p,
           title="Пасивні втрати: коефіцієнт шуму дорівнює самим втратам")


def friis_chain():
    """Внесок кожного каскаду до повного F ділиться на добуток підсилень попередніх —
    тому перший каскад вирішує, а втрати на вході б'ють у повну силу."""
    W, H = 720, 470
    p = []
    cy = 92
    stages = [("LNA", "G₁=20 дБ", "F₁=1 дБ"),
              ("змішувач", "G₂=6 дБ", "F₂=10 дБ"),
              ("ПЧ-каскад", "G₃=30 дБ", "F₃=8 дБ")]
    x = 70
    for i, (lbl, glbl, flbl) in enumerate(stages):
        p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (x, cy - 26, x, cy + 26, x + 60, cy, FILL, LINE))
        p.append(text(x + 21, cy - 36, lbl, size=12, color=MUTED))
        p.append(text(x + 20, cy + 4, glbl.split("=")[0] + "=" + glbl.split("=")[1].split(" ")[0], size=11, bold=True))
        p.append(text(x + 2, cy + 50, flbl, size=12, bold=True, color=POS, anchor="start"))
        if i < 2:
            p.append(arrow(x + 60, cy, x + 96, cy, color=INK, sw=2))
        x += 96
    p.append(arrow(x - 36, cy, x + 4, cy, color=INK, sw=2))
    p.append(text(x + 40, cy + 5, "вихід", size=12, color=MUTED, anchor="start"))
    p.append(text(40, cy + 5, "вхід", size=12, color=MUTED, anchor="end"))
    p.append(arrow(8, cy, 40, cy, color=INK, sw=2))

    # нижній ряд: внесок кожного каскаду в F (у «разах», умовно)
    base_y = 350
    bx0 = 120
    gap = 175
    bw = 64
    bars = [
        ("F₁ − 1", 1.00, "÷ 1", POS),
        ("(F₂−1)/G₁", 0.085, "÷ 100", NEG),
        ("(F₃−1)/(G₁G₂)", 0.013, "÷ 400", FIELD),
    ]
    maxh = 180
    for i, (lbl, frac, divlbl, col) in enumerate(bars):
        cx = bx0 + i * gap
        h = max(8, maxh * frac)
        fillc = {"#c0392b": "#fdecea", "#2457d6": "#eaf0fd", "#27ae60": "#eafaf0"}[col]
        p.append(rect(cx - bw / 2, base_y - h, bw, h, fill=fillc, stroke=col, sw=1.8))
        p.append(text(cx, base_y + 18, lbl, size=12, bold=True, color=col))
        p.append(text(cx, base_y + 36, divlbl, size=11, color=MUTED))
        lab = "%.0f%%" % (frac * 100) if frac >= 0.1 else "%.1f%%" % (frac * 100)
        p.append(text(cx, base_y - h - 6, lab, size=11, bold=True, color=col))
    p.append(line(bx0 - bw / 2 - 14, base_y, bx0 + 2 * gap + bw / 2 + 14, base_y, color=INK, sw=1.5))
    p.append(text(bx0 + gap, base_y + 56, "внесок каскаду в повний коефіцієнт шуму", size=12, bold=True, color=MUTED))

    b, _, _ = textbox(W / 2, 442,
                      "Внесок кожного каскаду в F ділиться на ДОБУТОК підсилень усіх попередніх.\n"
                      "Перший каскад не поділений нічим — його шум і ставить коефіцієнт шуму всього тракту.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'friis-chain.svg'), W, H, *p,
           title="Формула Фрііса: перший каскад вирішує коефіцієнт шуму")


def refer_to_input():
    """Зведення до входу: власний шум кожної ланки народжується у СВОЇЙ точці,
    а щоб порівняти з вхідним сигналом — ділимо на підсилення всього, що було ДО нього."""
    W, H = 720, 420
    p = []
    cy = 110
    # ланцюг трьох ланок
    stages = [("ланка 1", "G₁"), ("ланка 2", "G₂"), ("ланка 3", "G₃")]
    x = 120
    centers = []
    for i, (lbl, glbl) in enumerate(stages):
        p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (x, cy - 24, x, cy + 24, x + 58, cy, FILL, LINE))
        p.append(text(x + 19, cy + 4, glbl, size=14, bold=True))
        p.append(text(x + 21, cy - 34, lbl, size=11, color=MUTED))
        centers.append(x + 29)
        if i < 2:
            p.append(arrow(x + 58, cy, x + 94, cy, color=INK, sw=2))
        x += 152
    p.append(arrow(60, cy, 120, cy, color=INK, sw=2))
    p.append(text(56, cy + 4, "вхід", size=12, color=MUTED, anchor="end"))
    p.append(arrow(x - 94, cy, x - 50, cy, color=INK, sw=2))
    p.append(text(x - 44, cy + 4, "вихід", size=12, color=MUTED, anchor="start"))

    # власний шум народжується у виході кожної ланки
    src = [("N₁", POS), ("N₂", NEG), ("N₃", FIELD)]
    for i, (nm, col) in enumerate(src):
        bx = centers[i] + 29
        p.append(circle(bx, cy + 54, 13, fill="#fff", stroke=col, sw=2))
        p.append(text(bx, cy + 59, nm, size=12, bold=True, color=col))
        p.append(line(bx, cy + 24, bx, cy + 41, color=col, sw=1.6, dash="3 3"))

    # стрілки «зведення до входу» — кожен внесок котиться ліворуч, ділячись
    base_y = 300
    p.append(line(80, base_y, 660, base_y, color=INK, sw=1.5))
    p.append(text(70, base_y + 4, "вхід", size=11, color=MUTED, anchor="end"))
    refs = [
        ("N₁",            "÷ 1",        POS,   "#fdecea"),
        ("N₂ ÷ G₁",       "÷ G₁",       NEG,   "#eaf0fd"),
        ("N₃ ÷ (G₁G₂)",   "÷ G₁G₂",     FIELD, "#eafaf0"),
    ]
    heights = [150, 58, 16]   # умовно: після поділу внесок різко меншає
    bw = 78
    bx0 = 150
    gap = 195
    for i, (lbl, _, col, fillc) in enumerate(refs):
        cx = bx0 + i * gap
        h = heights[i]
        p.append(rect(cx - bw / 2, base_y - h, bw, h, fill=fillc, stroke=col, sw=1.8))
        p.append(text(cx, base_y + 18, lbl, size=12, bold=True, color=col))
    p.append(text(W / 2, base_y - 178, "усе зведено до спільної точки — ВХОДУ", size=12, bold=True, color=MUTED))

    b, _, _ = textbox(W / 2, 392,
                      "Власний шум ланки n народжується ПІСЛЯ n−1 підсилень — на вході він менший у стільки ж разів.\n"
                      "Тому в сумі кожен внесок поділений на добуток підсилень усіх ланок ПЕРЕД ним: ось і вся формула.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'refer-to-input.svg'), W, H, *p,
           title="Зведення власного шуму кожної ланки до входу")


def order_matters():
    """Ті самі дві ланки у двох порядках: LNA-перший vs змішувач-перший —
    повний коефіцієнт шуму різниться на порядок. Ціна порядку ланок."""
    W, H = 720, 400
    p = []

    def chain(y, a, b, total_lbl, good):
        out = []
        x = 150
        for (lbl, sub) in (a, b):
            out.append(rect(x, y - 24, 96, 48, fill=FILL, stroke=LINE, sw=1.8))
            out.append(text(x + 48, y - 3, lbl, size=12, bold=True))
            out.append(text(x + 48, y + 15, sub, size=11, color=MUTED))
            x += 150
        out.append(arrow(x - 54, y, x - 6, y, color=INK, sw=2))
        out.append(arrow(96, y, 150, y, color=INK, sw=2))
        out.append(text(92, y + 4, "вхід", size=11, color=MUTED, anchor="end"))
        col = FIELD if good else POS
        fillc = "#eafaf0" if good else "#fdecea"
        bb, _, _ = textbox(x + 90, y, total_lbl, size=14, bold=True,
                           fill=fillc, stroke=col, color=col)
        out.append(bb)
        return out

    p.append(text(W / 2, 70, "ті самі дві ланки — два порядки", size=14, bold=True, color=MUTED))
    p += chain(150,
               ("LNA", "F=1.26 · G=100"),
               ("змішувач", "F=10 · G=4"),
               "F ≈ 1.35\n≈ 1.3 дБ", good=True)
    p += chain(270,
               ("змішувач", "F=10 · G=4"),
               ("LNA", "F=1.26 · G=100"),
               "F ≈ 10.1\n≈ 10 дБ", good=False)

    b, _, _ = textbox(W / 2, 362,
                      "LNA попереду: його велике підсилення тисне надлишок змішувача в сто разів → повний F ≈ 1.3 дБ.\n"
                      "Змішувач попереду: перед LNA підсилення вже немає, шум змішувача лягає майже повністю → ≈ 10 дБ.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'order-matters.svg'), W, H, *p,
           title="Ціна порядку: перший каскад вирішує")


def friis_unification():
    """Історична фігура до hist-friis.md: до 1944 приймачі описували купою
    несумісних мірок; стаття Фрііса звела все до одного числа F."""
    W, H = 720, 360
    p = []
    cy0 = 80

    # ── ліворуч: какофонія несумісних описів ──
    lx = 60
    p.append(text(lx + 115, 56, "до 1944: кожен мірив по-своєму", size=13, bold=True, color=POS))
    descs = [
        "«опір шуму 1.2 кОм»",
        "«мін. сигнал 3 мкВ»",
        "«напруга шуму нВ/√Гц»",
        "(а тут — лише підсилення)",
    ]
    by = cy0
    for i, d in enumerate(descs):
        yy = by + i * 44
        p.append(rect(lx, yy, 230, 32, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
        p.append(text(lx + 115, yy + 21, d, size=12, color=INK))
    p.append(text(lx + 115, by + 4 * 44 + 14, "не зводяться одне до одного", size=11, color=MUTED, italic=True))

    # ── стрілка через статтю Фрііса ──
    mx = lx + 295
    b, _, _ = textbox(mx + 45, 120,
                      "Фрііс, 1944\n«Noise Figures\nof Radio Receivers»",
                      size=11, fill=FILL, stroke=LINE, bold=True)
    p.append(b)
    p.append(arrow(mx, 200, mx + 90, 200, color=INK, sw=2.4))

    # ── праворуч: одне число ──
    rx = mx + 110
    p.append(text(rx + 110, 56, "після: одна лінійка для всіх", size=13, bold=True, color=FIELD))
    p.append(rect(rx, cy0 + 6, 222, 92, fill="#eef7f0", stroke=FIELD, sw=2, rx=8))
    p.append(text(rx + 111, cy0 + 44, "F = (S/N)вх / (S/N)вих", size=15, bold=True, color=INK))
    p.append(text(rx + 111, cy0 + 72, "одне число, будь-який вузол", size=11, color=MUTED))
    p.append(text(rx + 111, cy0 + 132, "ідеал → F = 1", size=12, color=FIELD))
    p.append(text(rx + 111, cy0 + 154, "реальний → F > 1", size=12, color=POS))

    b2, _, _ = textbox(W / 2, 334,
                       "До статті 1944 року приймачі описували несумісними мірками — порівняти було годі.\n"
                       "Фрііс звів усе до одного відношення сигнал/шум на вході до виходу: спільна лінійка.",
                       size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b2)
    render(os.path.join(OUT, 'friis-unification.svg'), W, H, *p,
           title="Що дав Фрііс: одна мірка замість какофонії")


if __name__ == '__main__':
    snr_drop()
    noise_floor()
    attenuator_nf()
    friis_chain()
    refer_to_input()
    order_matters()
    friis_unification()
    print("OK: 7 figures ->", OUT)
