# -*- coding: utf-8 -*-
"""Фігури до статті «Межа CCM/DCM у DC-DC перетворювачах»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1. Трикутник струму сповзає до нуля: CCM → межа → DCM ────────────
def fig_boundary():
    W, H = 760, 380
    f = []
    # три панелі поруч: важке / межа / легке навантаження
    px = [40, 290, 540]
    pw = 190
    base_y = 250          # рівень нуля струму
    top_y = 80            # стеля панелі
    labels = ["CCM (важке)", "МЕЖА (I = ΔI/2)", "DCM (легке)"]
    # середні струми (частка від розмаху) — трикутник однакового розмаху 'amp'
    amp = 70              # ΔI/2 у пікселях (піврозмах)
    means = [base_y - 120, base_y - amp, base_y - amp * 0.55]  # середина трикутника
    for i, x0 in enumerate(px):
        x1 = x0 + pw
        # вісь часу й нуля
        f.append(line(x0, base_y, x1, base_y, color=INK, sw=1.6))
        f.append(text(x0 - 6, base_y + 4, "0", size=12, color=MUTED, anchor="end"))
        f.append(text(x0 + pw / 2, top_y - 12, labels[i], size=13, bold=True))
        mid = means[i]
        # трикутна хвиля струму: наростання (+, червоне) і спад (−, синє)
        if i < 2:
            # два повні періоди трикутника навколо mid
            seg = pw / 4.0
            pts = []
            xx = x0
            up = True
            y = mid + (amp if not up else -amp)
            # почнемо з нижньої точки
            ylow = mid + amp
            yhigh = mid - amp
            path_pts = [(x0, ylow)]
            xx = x0
            for k in range(4):
                xx += seg
                path_pts.append((xx, yhigh if k % 2 == 0 else ylow))
            d = "M " + " L ".join("%.1f %.1f" % (a, b) for a, b in path_pts)
            f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, POS))
            # середня лінія
            f.append(line(x0, mid, x1, mid, color=MUTED, sw=1.2, dash="4 4"))
            f.append(text(x1 + 4, mid + 4, "I", size=12, color=MUTED, anchor="start"))
            # розмах ΔI на першому періоді
            xa = x0 + seg
            f.append(line(xa, yhigh, xa, ylow, color=FIELD, sw=1.2, dash="3 3"))
        else:
            # DCM: острівці з відчутною паузою на нулі
            yhigh = base_y - amp * 1.15   # пік острівця
            rise = pw * 0.16              # ширина підйому
            fall = pw * 0.16              # ширина спаду
            pause = pw * 0.16             # пауза на нулі
            period = rise + fall + pause
            x_start = x0 + 2
            isl = 0
            while x_start + rise + fall <= x1 and isl < 3:
                x_peak = x_start + rise
                x_zero = x_peak + fall
                d = "M %.1f %.1f L %.1f %.1f L %.1f %.1f" % (
                    x_start, base_y, x_peak, yhigh, x_zero, base_y)
                f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, POS))
                # пауза на нулі (жирна ділянка нуля)
                x_end = min(x_zero + pause, x1)
                f.append(line(x_zero, base_y, x_end, base_y, color="#b45309", sw=3.4))
                x_start += period
                isl += 1
            f.append(text(x0 + pw / 2, base_y + 34, "струм лежить на 0",
                          size=11, color="#b45309"))
    # стрілка «зменшуємо навантаження»
    f.append(arrow(px[0] + pw / 2, H - 20, px[2] + pw / 2, H - 20, color=MUTED, sw=2))
    f.append(text((px[0] + px[2] + pw) / 2, H - 26, "← менше навантаження",
                  size=12, color=MUTED))
    # позначка межі на середній панелі: нижній край торкається нуля
    xa = px[1] + pw / 4
    f.append(circle(xa, base_y, 4, fill=POS, stroke=POS))
    b, bw, bh = textbox(px[1] + pw / 2, top_y + 18, "дно → 0",
                        size=11, fill="#fff7ed", stroke="#b45309", color="#b45309")
    f.append(b)
    render(os.path.join(IMG, 'boundary.svg'), W, H, *f,
           title="Один перетворювач, три режими: трикутник струму сповзає до нуля")


# ── Фігура 2. Критична індуктивність / межовий струм vs навантаження ────────
def fig_critical():
    W, H = 720, 400
    f = []
    ox, oy = 90, 320      # початок осей
    aw, ah = 560, 250
    # осі
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    f.append(text(ox + aw - 4, oy + 26, "струм навантаження I", size=13, anchor="end"))
    f.append(text(ox - 60, oy - ah + 10, "розмах", size=12, anchor="start", color=MUTED))
    f.append(text(ox - 60, oy - ah + 26, "ΔI/2", size=12, anchor="start", color=MUTED))
    # горизонталь ΔI/2 (стала для CCM) — межа проходить де I = ΔI/2
    yb = oy - 150
    f.append(line(ox, yb, ox + aw, yb, color=FIELD, sw=2, dash="6 4"))
    f.append(text(ox + aw - 4, yb - 8, "ΔI/2  (пів-розмаху пульсації)",
                  size=12, color=FIELD, anchor="end"))
    # діагональ I = I (робоча точка: середній струм)
    f.append(line(ox, oy, ox + aw, oy - ah + 20, color=INK, sw=1.4, dash="2 4"))
    # точка перетину = межовий струм I_bnd
    xb = ox + (yb - oy) / ((oy - ah + 20) - oy) * aw  # де діагональ = yb
    f.append(circle(xb, yb, 6, fill=POS, stroke=POS))
    f.append(line(xb, oy, xb, yb, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(xb, oy + 20, "I_межа", size=12, color=POS))
    # заливка зон
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eaf7ef" opacity="0.6"/>'
             % (xb, oy - ah + 20, ox + aw - xb, ah - 20))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdf0ee" opacity="0.6"/>'
             % (ox, oy - ah + 20, xb - ox, ah - 20))
    f.append(text((ox + xb) / 2, oy - ah + 44, "DCM", size=15, bold=True, color=POS))
    f.append(text((ox + xb) / 2, oy - ah + 62, "I < ΔI/2", size=11, color=MUTED))
    f.append(text((xb + ox + aw) / 2, oy - ah + 44, "CCM", size=15, bold=True, color=FIELD))
    f.append(text((xb + ox + aw) / 2, oy - ah + 62, "I > ΔI/2", size=11, color=MUTED))
    # підпис формули межі
    b, bw, bh = textbox(ox + aw / 2, H - 26,
                        "межа: I = ΔI/2   →   L_крит утримує CCM до цього струму",
                        size=12, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, 'critical.svg'), W, H, *f,
           title="Межовий струм: де середній струм дорівнює пів-розмаху пульсації")


# ── Фігура 3. Що ламається: коефіцієнт передачі стає залежним від струму ────
def fig_ratio():
    W, H = 720, 380
    f = []
    ox, oy = 90, 300
    aw, ah = 560, 230
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    f.append(text(ox + aw - 4, oy + 26, "струм навантаження I →", size=13, anchor="end"))
    f.append(text(ox + 4, oy - ah + 4, "Vвих / Vвх", size=13, anchor="start", color=MUTED))
    # межа
    xb = ox + aw * 0.42
    f.append(line(xb, oy, xb, oy - ah, color=MUTED, sw=1.3, dash="4 4"))
    f.append(text(xb, oy + 20, "I_межа", size=12, color=MUTED))
    f.append(text((xb + ox + aw) / 2, oy - ah + 20, "CCM", size=13, bold=True, color=FIELD))
    f.append(text((ox + xb) / 2, oy - ah + 20, "DCM", size=13, bold=True, color=POS))
    # рівень M = D (плаский у CCM)
    ycc = oy - 90
    f.append(line(xb, ycc, ox + aw, ycc, color=FIELD, sw=2.6))
    f.append(text(ox + aw - 4, ycc - 8, "M = D  (не залежить від I)",
                  size=12, color=FIELD, anchor="end"))
    # у DCM крива підіймається вліво (buck: M росте при I→0)
    pts = []
    import math
    for k in range(0, 41):
        t = k / 40.0
        x = xb - t * (xb - ox)
        # M росте вгору при русі вліво (спад струму)
        rise = 90 * (t ** 0.55)
        y = ycc - rise
        pts.append((x, y))
    d = "M " + " L ".join("%.1f %.1f" % (a, b) for a, b in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))
    f.append(text(ox + 6, ycc - 96, "M росте", size=12, color=POS, anchor="start"))
    f.append(text(ox + 6, ycc - 80, "↑ (buck)", size=11, color=POS, anchor="start"))
    # рамка-висновок
    b, bw, bh = textbox(ox + aw * 0.70, oy - 165,
                        ["У CCM коефіцієнт передачі M сталий:",
                         "тримається лише на D.",
                         "У DCM M «відривається» й залежить від I."],
                        size=11.5, fill="#fff7ed", stroke="#b45309")
    f.append(b)
    render(os.path.join(IMG, 'ratio.svg'), W, H, *f,
           title="Що ламається за межею: коефіцієнт передачі стає залежним від струму")


# ═══ Фігури до вставки math-critical-inductance.md ═════════════════════════

# ── Виведення для buck: ланцюжок від закону котушки до L_крит ────────────────
def fig_derive_buck():
    W, H = 760, 300
    f = []
    # чотири рамки в ряд, стрілки між ними — «одна дія = одна стрілка»
    cy = 150
    boxes = [
        ("Закон котушки\n(фаза спаду)", "ΔI = V_вих·(1−D)\n────────────\nL·f", FILL, LINE),
        ("Умова межі\nI_сер = ΔI/2", "I_межа =\nV_вих·(1−D)\n────────\n2·L·f", "#eaf7ef", FIELD),
        ("Читаємо назад:\nL при I_сер=I_вих", "L = V_вих·(1−D)\n──────────\n2·f·I_вих", FILL, LINE),
        ("Згорнути\nV_вих/I_вих = R", "L_крит =\n(1−D)·R\n──────\n2·f", "#fff7ed", "#b45309"),
    ]
    n = len(boxes)
    gap = 22
    bw = (W - 2 * 20 - (n - 1) * gap) / n
    x = 20
    centers = []
    for i, (cap, body, fill, stroke) in enumerate(boxes):
        # верхня підпис-рамка
        f.append(fitbox(x, cy - 78, bw, 44, cap, size=12, fill="#ffffff",
                        stroke=MUTED, bold=True))
        # тіло-формула
        f.append(fitbox(x, cy - 26, bw, 96, body, size=13, fill=fill, stroke=stroke))
        centers.append(x + bw / 2)
        if i < n - 1:
            xs = x + bw + 3
            xe = x + bw + gap - 3
            f.append(arrow(xs, cy + 12, xe, cy + 12, color=INK, sw=2))
        x += bw + gap
    render(os.path.join(IMG, 'derive-buck.svg'), W, H, *f,
           title="Виведення для buck: від закону котушки до критичної індуктивності")


# ── Критичний множник K_крит(D) для трьох топологій ─────────────────────────
def fig_kcrit():
    W, H = 720, 420
    f = []
    ox, oy = 80, 340
    aw, ah = 570, 270
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    f.append(text(ox + aw - 4, oy + 26, "коефіцієнт заповнення D", size=13, anchor="end"))
    f.append(text(ox - 8, oy - ah + 2, "K_крит", size=13, anchor="end", color=MUTED))
    # шкала: K від 0 до 1 (buck дає max=1 при D=0)
    Kmax = 1.0
    def X(D): return ox + D * aw
    def Y(K): return oy - (K / Kmax) * ah
    # сітка по осі D
    for d in (0.0, 0.25, 0.5, 0.75, 1.0):
        f.append(line(X(d), oy, X(d), oy + 5, color=INK, sw=1.2))
        f.append(text(X(d), oy + 20, ("%.2f" % d).rstrip("0").rstrip("."), size=11, color=MUTED))
    for kk in (0.25, 0.5, 0.75, 1.0):
        f.append(line(ox - 5, Y(kk), ox, Y(kk), color=INK, sw=1.2))
        f.append(text(ox - 10, Y(kk) + 4, "%.2f" % kk, size=11, color=MUTED, anchor="end"))
        f.append(line(ox, Y(kk), ox + aw, Y(kk), color="#e5e7eb", sw=1))
    curves = [
        ("buck: (1−D)", POS, lambda D: (1 - D)),
        ("buck-boost: (1−D)²", NEG, lambda D: (1 - D) ** 2),
        ("boost: D(1−D)²", FIELD, lambda D: D * (1 - D) ** 2),
    ]
    N = 60
    for name, col, fn in curves:
        pts = []
        for k in range(N + 1):
            D = k / float(N)
            pts.append((X(D), Y(fn(D))))
        d = "M " + " L ".join("%.1f %.1f" % (a, b) for a, b in pts)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, col))
    # легенда
    ly = oy - ah + 12
    for i, (name, col, fn) in enumerate(curves):
        yy = ly + i * 22
        f.append(line(ox + aw - 190, yy, ox + aw - 165, yy, color=col, sw=3))
        f.append(text(ox + aw - 160, yy + 4, name, size=12, color=col, anchor="start"))
    # позначка горба boost біля D≈1/3
    xh = X(1.0 / 3.0)
    f.append(circle(xh, Y(1.0 / 3.0 * (1 - 1.0 / 3.0) ** 2), 4, fill=FIELD, stroke=FIELD))
    f.append(text(xh + 6, Y(0.15) + 4, "горб boost", size=11, color=FIELD, anchor="start"))
    render(os.path.join(IMG, 'kcrit.svg'), W, H, *f,
           title="Критичний множник K_крит проти D для трьох топологій")


# ── Коефіцієнт передачі в DCM проти K для трьох топологій ────────────────────
def fig_dcm_ratio():
    import math
    W, H = 720, 420
    f = []
    ox, oy = 80, 340
    aw, ah = 570, 275
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    f.append(text(ox + aw - 4, oy + 26, "K = 2Lf/R  (мале K = легке навантаження →)",
                  size=12, anchor="end"))
    f.append(text(ox + 6, oy - ah + 2, "M = V_вих/V_вх", size=13, anchor="start", color=MUTED))
    D = 0.5                      # фіксуємо приклад-D для наочності
    Kmax = 0.9
    Mmax = 4.0
    def X(K): return ox + (K / Kmax) * aw
    def Y(M): return oy - min(M, Mmax) / Mmax * ah
    for kk in (0.0, 0.25, 0.5, 0.75, 0.9):
        f.append(line(X(kk), oy, X(kk), oy + 5, color=INK, sw=1.2))
        f.append(text(X(kk), oy + 20, ("%.2f" % kk).rstrip("0").rstrip("."), size=11, color=MUTED))
    for mm in (1, 2, 3, 4):
        f.append(line(ox - 5, Y(mm), ox, Y(mm), color=INK, sw=1.2))
        f.append(text(ox - 10, Y(mm) + 4, "%d" % mm, size=11, color=MUTED, anchor="end"))
    # межі та CCM-рівні для D=0.5
    Kc_buck = 1 - D                 # 0.5
    Kc_boost = D * (1 - D) ** 2     # 0.125
    Kc_bb = (1 - D) ** 2            # 0.25
    Mccm_buck = D                   # 0.5
    Mccm_boost = 1 / (1 - D)        # 2.0
    Mccm_bb = D / (1 - D)           # 1.0
    N = 80
    def draw_dcm(fnM, Kc, Mccm, col, name):
        # DCM-гілка: від малого K до K_крит
        pts = []
        k0 = 0.02
        for i in range(N + 1):
            K = k0 + (Kc - k0) * i / float(N)
            pts.append((X(K), Y(fnM(K))))
        d = "M " + " L ".join("%.1f %.1f" % (a, b) for a, b in pts)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, col))
        # CCM-рівень (пунктир) праворуч від межі
        f.append(line(X(Kc), Y(Mccm), X(Kmax), Y(Mccm), color=col, sw=1.8, dash="6 4"))
        # позначка межі
        f.append(circle(X(Kc), Y(Mccm), 4, fill=col, stroke=col))
    draw_dcm(lambda K: 2 / (1 + math.sqrt(1 + 4 * K / D ** 2)), Kc_buck, Mccm_buck, POS, "buck")
    draw_dcm(lambda K: (1 + math.sqrt(1 + 4 * D ** 2 / K)) / 2, Kc_boost, Mccm_boost, FIELD, "boost")
    draw_dcm(lambda K: D / math.sqrt(K), Kc_bb, Mccm_bb, NEG, "buck-boost")
    # легенда + підпис-умова
    leg = [("buck → насич. до 1", POS), ("boost → злітає", FIELD), ("buck-boost = D/√K", NEG)]
    for i, (name, col) in enumerate(leg):
        yy = oy - ah + 14 + i * 22
        f.append(line(ox + aw - 210, yy, ox + aw - 185, yy, color=col, sw=3))
        f.append(text(ox + aw - 180, yy + 4, name, size=12, color=col, anchor="start"))
    f.append(text(ox + 10, oy - 10, "(приклад D = 0.5; ● — межа K_крит)",
                  size=11, color=MUTED, anchor="start"))
    render(os.path.join(IMG, 'dcm-ratio.svg'), W, H, *f,
           title="Коефіцієнт передачі в DCM проти K для трьох топологій")


if __name__ == '__main__':
    fig_boundary()
    fig_critical()
    fig_ratio()
    fig_derive_buck()
    fig_kcrit()
    fig_dcm_ratio()
    print("figures written to", IMG)
