# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HOT  = "#c0392b"   # гарячі спиці
COLD = "#2457d6"   # холодний розмаз
GRN  = FIELD


# ── 1. Спектр: частокіл спиць на fsw і гармоніках → низькі горби ────────────
def fig_spectrum():
    W, H = 780, 470
    els = []
    # дві панелі
    px0, py = 70, 60
    pw, ph = 640, 130
    gap = 60

    limit_frac = 0.32   # де стоїть нормативна стеля (від верху панелі)

    def panel(y0, spikes, spread, caption):
        out = []
        # осі
        out.append(line(px0, y0 + ph, px0 + pw, y0 + ph, INK, 2))      # X
        out.append(line(px0, y0, px0, y0 + ph, INK, 2))                # Y
        out.append(arrow(px0 + pw, y0 + ph, px0 + pw + 22, y0 + ph, INK, 2))
        out.append(arrow(px0, y0, px0, y0 - 18, INK, 2))
        # нормативна стеля
        ly = y0 + ph * limit_frac
        out.append(line(px0, ly, px0 + pw, ly, HOT, 2.2, dash="7 5"))
        out.append(text(px0 + pw - 4, ly - 7, "нормативна стеля", size=12,
                        color=HOT, anchor="end"))
        # спиці / горби
        base = y0 + ph
        for i, (fx, amp) in enumerate(spikes):
            x = px0 + fx * pw
            top = base - amp * ph
            if not spread:
                out.append(line(x, base, x, top, HOT, 4))
                out.append(circle(x, top, 3.5, fill=HOT, stroke=HOT, sw=1))
            else:
                # горб-парабола тієї самої «площі», але нижчий і ширший
                hw = 26 + i * 9            # вищі гармоніки — ширший розмаз
                new_amp = amp * (7.0 / (7.0 + i)) * 0.34   # осідає під стелю
                pts = []
                n = 24
                for k in range(n + 1):
                    t = (k / n) * 2 - 1     # −1..1
                    xx = x + t * hw
                    yy = base - new_amp * ph * (1 - t * t)
                    pts.append("%.1f,%.1f" % (xx, yy))
                out.append('<polyline points="%s" fill="none" stroke="%s" '
                           'stroke-width="2.6"/>' % (" ".join(pts), COLD))
        return out

    # спиці: (частка ширини, амплітуда 0..1)
    spikes = [(0.10, 0.90), (0.28, 0.66), (0.46, 0.50),
              (0.64, 0.40), (0.82, 0.33)]

    els += panel(py, spikes, False, "фіксована частота")
    els.append(text(px0 - 10, py - 8, "рівень", size=12, color=MUTED, anchor="end"))
    els.append(text(px0 + 8, py + 14, "fsw", size=12, color=INK, anchor="start"))
    els.append(text(px0 + 0.28 * pw, py + ph + 20, "2·fsw", size=11,
                    color=MUTED, anchor="middle"))
    els.append(text(px0 + 0.46 * pw, py + ph + 20, "3·fsw", size=11,
                    color=MUTED, anchor="middle"))
    b1, _, _ = textbox(px0 + pw / 2, py - 34,
                       "ФІКСОВАНА fsw: вся енергія — у тонких спицях, пік лізе за стелю",
                       size=13, bold=True, fill="#fdecea", stroke=HOT)
    els.append(b1)

    y2 = py + ph + gap + 40
    els += panel(y2, spikes, True, "розмазана частота")
    els.append(text(px0 - 10, y2 - 8, "рівень", size=12, color=MUTED, anchor="end"))
    els.append(text(px0 + pw / 2, y2 + ph + 34, "частота  →", size=12,
                    color=MUTED, anchor="middle"))
    b2, _, _ = textbox(px0 + pw / 2, y2 - 34,
                       "СПРЕД-СПЕКТРУМ: та сама енергія розсипана в горби — пік осів під стелю",
                       size=13, bold=True, fill="#eaf0fd", stroke=COLD)
    els.append(b2)

    render(os.path.join(OUT, "spectrum-spread.svg"), W, H, *els)


# ── 2. Дизеринг у часі: fsw повільно гуляє (трикутник) ──────────────────────
def fig_dither():
    W, H = 760, 360
    els = []
    ox, oy = 80, 60
    aw, ah = 600, 210

    els.append(line(ox, oy, ox, oy + ah, INK, 2))
    els.append(line(ox, oy + ah, ox + aw, oy + ah, INK, 2))
    els.append(arrow(ox + aw, oy + ah, ox + aw + 22, oy + ah, INK, 2))
    els.append(arrow(ox, oy, ox, oy - 16, INK, 2))
    els.append(text(ox - 10, oy - 2, "fsw", size=13, color=INK, anchor="end"))
    els.append(text(ox + aw / 2, oy + ah + 34, "час  →", size=12, color=MUTED))

    fnom_y = oy + ah * 0.28    # номінальна частота
    fmin_y = oy + ah * 0.70    # нижня межа розмазу
    fmid_y = (fnom_y + fmin_y) / 2

    # смуга розмазу
    els.append(rect(ox, fnom_y, aw, fmin_y - fnom_y, fill="#eef4ff",
                    stroke="none", rx=0))
    els.append(line(ox, fnom_y, ox + aw, fnom_y, MUTED, 1.6, dash="5 5"))
    els.append(line(ox, fmin_y, ox + aw, fmin_y, MUTED, 1.6, dash="5 5"))
    els.append(text(ox + aw + 6, fnom_y + 4, "fnom", size=12, color=INK, anchor="start"))
    els.append(text(ox + aw + 6, fmin_y + 4, "fnom−Δf", size=12, color=NEG, anchor="start"))

    # трикутна модуляція частоти (розмаз униз): гуляє між fnom і fmin
    pts = []
    n = 400
    periods = 3.0
    for k in range(n + 1):
        t = k / n
        ph = (t * periods) % 1.0
        tri = abs(ph * 2 - 1)           # 0..1..0
        yy = fnom_y + (fmin_y - fnom_y) * tri
        pts.append("%.1f,%.1f" % (ox + t * aw, yy))
    els.append('<polyline points="%s" fill="none" stroke="%s" '
               'stroke-width="3"/>' % (" ".join(pts), COLD))

    # мітка «повільно» — стрілки над модуляцією
    els.append(text(ox + aw * 0.5, oy - 4,
                    "частота такту повільно гуляє (модуляція ~ десятки кГц)",
                    size=12, color=COLD, bold=True))

    # праворуч — пояснювальний блок
    b, bw, bh = textbox(ox + aw / 2, oy + ah + 74,
                        "fsw ~ сотні кГц • розмах Δf ~ ±5…±10 % • fмод > 20 кГц (щоб не свистіло)",
                        size=12.5, bold=True, fill="#f4f6f8", stroke=INK)
    els.append(b)

    render(os.path.join(OUT, "dither-time.svg"), W, H, *els)


# ── 3. Детектор: чому середній виграє більше за піковий ─────────────────────
def fig_detector():
    W, H = 760, 340
    els = []
    ox, oy = 70, 74
    aw, ah = 620, 150

    els.append(line(ox, oy, ox, oy + ah, INK, 2))
    els.append(line(ox, oy + ah, ox + aw, oy + ah, INK, 2))
    els.append(arrow(ox + aw, oy + ah, ox + aw + 20, oy + ah, INK, 2))
    els.append(text(ox + aw / 2, oy + ah + 30, "частота  →", size=12, color=MUTED))
    els.append(text(ox - 10, oy - 4, "рівень", size=12, color=MUTED, anchor="end"))

    base = oy + ah
    # розмазаний горб
    cx = ox + aw * 0.44
    hw = 150
    amp = 0.62
    pts = []
    n = 40
    for k in range(n + 1):
        t = (k / n) * 2 - 1
        xx = cx + t * hw
        yy = base - amp * ah * (1 - t * t)
        pts.append("%.1f,%.1f" % (xx, yy))
    els.append('<polyline points="%s" fill="none" stroke="%s" '
               'stroke-width="2.6"/>' % (" ".join(pts), COLD))
    els.append(text(cx, base - amp * ah - 12, "розмазана гармоніка", size=12,
                    color=COLD, anchor="middle"))

    # вікно RBW ковзає — показуємо одну позицію біля вершини
    win = 40
    wx = cx - win / 2
    els.append(rect(wx, oy - 6, win, ah + 6, fill="#eafaf0", stroke=GRN, sw=2, rx=3))
    els.append(text(cx, oy - 14, "вікно приймача (RBW)", size=11, color=GRN,
                    anchor="middle", bold=True))

    # ПІКОВИЙ рівень (вершина того, що у вікні) — вища риска
    peak_y = base - amp * ah * (1 - ((win / 2) / hw) ** 2)
    els.append(line(ox, peak_y, ox + aw, peak_y, HOT, 1.8, dash="6 4"))
    els.append(text(ox + aw - 4, peak_y - 6, "піковий детектор: ловить вершину",
                    size=12, color=HOT, anchor="end"))

    # СЕРЕДНІЙ рівень — набагато нижче (усереднення в часі, поки горб «проходить» вікно)
    avg_y = base - amp * ah * 0.22
    els.append(line(ox, avg_y, ox + aw, avg_y, NEG, 2, dash="3 4"))
    els.append(text(ox + aw - 4, avg_y + 16, "середній детектор: усереднює в часі — ще нижче",
                    size=12, color=NEG, anchor="end"))

    # підпис-різниця
    els.append(line(ox + 40, peak_y, ox + 40, avg_y, MUTED, 1.4))
    els.append(text(ox + 48, (peak_y + avg_y) / 2, "виграш", size=11,
                    color=MUTED, anchor="start"))

    b, _, _ = textbox(ox + aw / 2, oy + ah + 66,
                      "піковий детектор бачить частку горба; середній — ще менше, бо гармоніка лише зрідка навідується у вікно",
                      size=12, fill="#f4f6f8", stroke=INK)
    els.append(b)

    render(os.path.join(OUT, "detector-avg.svg"), W, H, *els)


if __name__ == "__main__":
    fig_spectrum()
    fig_dither()
    fig_detector()
    print("figs done")
