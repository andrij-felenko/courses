# -*- coding: utf-8 -*-
"""Фігури теми «Температурні коефіцієнти сонячної панелі»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def iv(V, Isc, Voc, Vk):
    """Проста форма ВАХ панелі з коліном біля Voc."""
    return max(0.0, Isc * (1.0 - math.exp((V - Voc) / Vk)))


def polyline(pts, color, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


# ── Фігура 1: ВАХ холодної та гарячої панелі ───────────────────────────────
def fig_iv_shift():
    w, h = 660, 450
    x0, y0 = 100, 370            # початок координат (V=0, I=0)
    xs, ys = 420, 258            # масштаби осей
    def X(V): return x0 + V * xs
    def Y(I): return y0 - I * ys

    parts = []
    # осі
    parts.append(line(x0, y0, x0 + 470, y0, INK, 2.0))          # V
    parts.append(line(x0, y0, x0, 78, INK, 2.0))                # I
    parts.append(text(x0 + 470, y0 + 46, "напруга V", 14, MUTED, anchor="end"))
    parts.append(text(x0 - 12, 88, "струм I", 14, MUTED, anchor="end"))

    # криві
    cool = [(X(v), Y(iv(v, 1.00, 1.00, 0.05))) for v in [i / 200 for i in range(0, 201)]]
    hot = [(X(v), Y(iv(v, 1.035, 0.86, 0.05))) for v in [i / 200 for i in range(0, 173)]]
    parts.append(polyline(cool, NEG))
    parts.append(polyline(hot, POS))

    # MPP-точки (максимум V·I)
    def mpp(Isc, Voc, Vk):
        best = (0, 0, 0)
        for k in range(1, 200):
            v = Voc * k / 200
            p = v * iv(v, Isc, Voc, Vk)
            if p > best[0]:
                best = (p, v, iv(v, Isc, Voc, Vk))
        return best[1], best[2]
    vmc, imc = mpp(1.00, 1.00, 0.05)
    vmh, imh = mpp(1.035, 0.86, 0.05)
    parts.append(circle(X(vmc), Y(imc), 5.5, NEG, NEG, 1))
    parts.append(circle(X(vmh), Y(imh), 5.5, POS, POS, 1))
    parts.append(text(X(vmc) + 12, Y(imc) - 10, "MPP 25°", 12, NEG, anchor="start"))
    parts.append(text(X(vmh) - 12, Y(imh) - 12, "MPP 65°", 12, POS, anchor="end"))

    # позначки Voc і ΔVoc
    parts.append(line(X(1.0), y0, X(1.0), Y(0.05), NEG, 1.2, dash="4,4"))
    parts.append(line(X(0.86), y0, X(0.86), Y(0.05), POS, 1.2, dash="4,4"))
    parts.append(text(X(1.0), y0 + 22, "Voc 25°", 12, NEG))
    parts.append(text(X(0.86), y0 + 40, "Voc 65°", 12, POS))
    # стрілка ΔVoc
    parts.append(line(X(0.86), y0 - 8, X(1.0), y0 - 8, INK, 1.6))
    parts.append(text((X(0.86) + X(1.0)) / 2, y0 - 14, "ΔVoc", 12, INK, bold=True))

    # позначка Isc (гарячий трохи вище)
    parts.append(text(x0 + 14, Y(1.05) - 4, "Isc ↑ трохи", 12, FIELD, anchor="start"))

    # легенда (у порожньому полі під пласкими ділянками кривих, лівіше колін)
    lx, ly = 150, 300
    parts.append(line(lx, ly, lx + 34, ly, NEG, 3))
    parts.append(text(lx + 42, ly + 5, "холодна · 25 °C", 13, INK, anchor="start"))
    parts.append(line(lx, ly + 26, lx + 34, ly + 26, POS, 3))
    parts.append(text(lx + 42, ly + 31, "гаряча · 65 °C", 13, INK, anchor="start"))

    render(os.path.join(IMG, "iv-shift.svg"), w, h, *parts,
           title="Нагрів тягне криву вліво: Voc падає, площа під MPP меншає")


# ── Фігура 2: три коефіцієнти проти температури ────────────────────────────
def fig_coeff():
    w, h = 760, 430
    x0, xR = 100, 520            # T = 25 … 75 °C
    def X(T): return x0 + (T - 25) * (xR - x0) / 50.0
    def Y(v): return 365 - (v - 0.80) * 1080   # v=0.80→365, v=1.05→95

    parts = []
    # осі
    parts.append(line(x0, 365, xR + 8, 365, INK, 2.0))
    parts.append(line(x0, 365, x0, 90, INK, 2.0))
    for T in (25, 45, 55, 65, 75):
        parts.append(line(X(T), 365, X(T), 370, INK, 1.5))
        parts.append(text(X(T), 388, "%d" % T, 12, MUTED))
    parts.append(text((x0 + xR) / 2, 412, "температура елемента, °C", 13, MUTED))

    # базова лінія 1.0
    parts.append(line(x0, Y(1.0), xR, Y(1.0), MUTED, 1.2, dash="5,5"))
    parts.append(text(x0 - 10, Y(1.0) + 4, "1.0", 12, MUTED, anchor="end"))

    # три прямі від STC-точки
    parts.append(line(X(25), Y(1.0), X(75), Y(1.025), FIELD, 3))     # Isc +0.05
    parts.append(line(X(25), Y(1.0), X(75), Y(0.85), NEG, 3))        # Voc -0.30
    parts.append(line(X(25), Y(1.0), X(75), Y(0.80), POS, 3, dash="7,4"))  # Pmax -0.40

    parts.append(circle(X(25), Y(1.0), 6, INK, INK, 1))
    parts.append(text(X(25) + 6, Y(1.0) - 12, "STC (25 °C)", 12, INK, anchor="start"))

    # підписи праворуч із запасом
    parts.append(text(xR + 14, Y(1.025) + 4, "Isc  +0.05 %/°C", 13, FIELD, anchor="start"))
    parts.append(text(xR + 14, Y(0.85) + 4, "Voc  −0.30 %/°C", 13, NEG, anchor="start"))
    parts.append(text(xR + 14, Y(0.80) - 6, "Pmax −0.40 %/°C", 13, POS, anchor="start"))

    parts.append(text(x0 - 10, 100, "частка від", 12, MUTED, anchor="end"))
    parts.append(text(x0 - 10, 116, "значення STC", 12, MUTED, anchor="end"))

    render(os.path.join(IMG, "coeff-vs-temp.svg"), w, h, *parts,
           title="Три коефіцієнти й різна крутість: Voc падає, Pmax сильніше, Isc трохи росте")


# ── Фігура 3: холодний ранок задає межу довжини рядка ──────────────────────
def fig_string():
    w, h = 700, 440
    base = 378                  # вісь V=0
    def Y(V): return base - V * 0.445    # 0→378, 680→378-302.6

    parts = []
    parts.append(line(90, base, 640, base, INK, 2.0))
    parts.append(line(90, base, 90, 92, INK, 2.0))
    parts.append(text(70, 100, "В", 13, MUTED, anchor="end"))

    # стеля інвертора 600 В
    parts.append(line(90, Y(600), 620, Y(600), POS, 2.2, dash="8,5"))
    parts.append(text(624, Y(600) + 5, "макс. вхід", 12, POS, anchor="start"))
    parts.append(text(624, Y(600) + 20, "інвертора", 12, POS, anchor="start"))
    parts.append(text(624, Y(600) + 35, "600 В", 12, POS, anchor="start", bold=True))

    bars = [
        (175, 533, FIELD, "#e8f6ee", ["13 панелей", "25 °C (STC)"], "533 В"),
        (350, 613, POS, "#fdecea", ["13 панелей", "−25 °C"], "613 В ⚠"),
        (525, 566, FIELD, "#e8f6ee", ["12 панелей", "−25 °C"], "566 В"),
    ]
    bw = 96
    for cx, V, col, fillc, cap, val in bars:
        parts.append(rect(cx - bw / 2, Y(V), bw, base - Y(V), fill=fillc, stroke=col, sw=2.2, rx=4))
        parts.append(text(cx, Y(V) - 10, val, 13, col, bold=True))
        parts.append(text(cx, base + 22, cap[0], 12, INK))
        parts.append(text(cx, base + 39, cap[1], 12, MUTED))

    render(os.path.join(IMG, "string-cold-voc.svg"), w, h, *parts,
           title="Холодний ранок, а не STC, задає найбільшу довжину рядка")


# ── Фігура 4: двобічне вікно довжини рядка (для калькулятора) ───────────────
def fig_window():
    w, h = 820, 472
    def X(N): return 100 + N * (580.0 / 14.0)
    def Y(V): return 410 - V * (340.0 / 700.0)
    voc_cold = 46.945      # Voc однієї панелі на морозі −25 °C
    vmpp_hot = 28.822      # Vmpp однієї панелі на спеці +71 °C
    vmax, vmin = 600.0, 150.0

    parts = []
    # безпечна смуга 6…12 панелей (позаду всього)
    parts.append(rect(X(6), 66, X(12) - X(6), 410 - 66,
                      fill="#e8f6ee", stroke="none", sw=0, rx=0))
    parts.append(text(X(9), 92, "дозволено: 6 … 12 панелей", 13, FIELD, bold=True))

    # осі
    parts.append(line(100, 410, 700, 410, INK, 2.0))
    parts.append(line(100, 410, 100, 60, INK, 2.0))
    for N in range(0, 15, 2):
        parts.append(line(X(N), 410, X(N), 415, INK, 1.5))
        col, bold = INK, False
        if N == 6:  col, bold = POS, True
        if N == 12: col, bold = NEG, True
        parts.append(text(X(N), 432, "%d" % N, 13, col, bold=bold))
    parts.append(text((X(0) + X(14)) / 2, 458, "панелей у рядку, N", 13, MUTED))
    for V, lab in [(0, "0"), (150, "150"), (600, "600")]:
        parts.append(text(92, Y(V) + 4, lab, 12, MUTED, anchor="end"))
    parts.append(text(108, 54, "напруга рядка, В", 12, MUTED, anchor="start"))

    # межі інвертора
    parts.append(line(100, Y(vmax), 660, Y(vmax), INK, 2.0, dash="9,5"))
    parts.append(line(100, Y(vmin), 660, Y(vmin), MUTED, 2.0, dash="6,5"))
    parts.append(text(666, Y(vmax) - 5, "макс. вхід інвертора", 12, INK, anchor="start"))
    parts.append(text(666, Y(vmax) + 12, "600 В — стеля", 12, INK, anchor="start", bold=True))
    parts.append(text(666, Y(vmin) - 5, "нижнє вікно MPPT", 12, MUTED, anchor="start"))
    parts.append(text(666, Y(vmin) + 12, "150 В — підлога", 12, MUTED, anchor="start", bold=True))

    # похилі лінії напруги рядка
    parts.append(line(X(0), Y(0), X(14), Y(voc_cold * 14), NEG, 3.2))
    parts.append(line(X(0), Y(0), X(14), Y(vmpp_hot * 14), POS, 3.2))
    parts.append(text(X(7.6), Y(voc_cold * 7.6) - 15, "Voc рядка · холод −25 °C", 12, NEG))
    parts.append(text(X(9.8), Y(vmpp_hot * 9.8) + 20, "Vmpp рядка · спека +71 °C", 12, POS))

    # точки перетину зі стелею й підлогою
    nx_cold = vmax / voc_cold    # 12.78
    nx_hot = vmin / vmpp_hot     # 5.20
    parts.append(circle(X(nx_cold), Y(vmax), 5.5, BG, NEG, 2))
    parts.append(circle(X(nx_hot), Y(vmin), 5.5, BG, POS, 2))
    parts.append(text(X(nx_cold) - 2, Y(vmax) - 12, "N=12.8", 12, NEG, bold=True))
    parts.append(text(X(nx_hot) - 6, Y(vmin) + 22, "N=5.2", 12, POS, bold=True))

    render(os.path.join(IMG, "string-window.svg"), w, h, *parts,
           title="Вікно довжини рядка: холод ставить стелю, спека — підлогу")


# ── Фігура 5 (вставка math): розклад нахилу dVoc/dT на три сили ─────────────
def fig_slope_decomp():
    w, h = 720, 470
    def Y(v): return 235 - v * 63.5          # v у мВ/К: 0→235, +2.6→70, −2.6→400

    parts = []
    parts.append(line(88, 60, 88, 410, INK, 2.0))            # вісь значень
    parts.append(text(58, 246, "внесок,", 12, MUTED))
    parts.append(text(58, 262, "мВ/К", 12, MUTED))
    for v in (2, 1, 0, -1, -2):
        y = Y(v)
        parts.append(line(84, y, 92, y, INK, 1.5))
        parts.append(text(78, y + 4, ("%+d" % v) if v else "0", 12, MUTED, anchor="end"))
        parts.append(line(92, y, 690, y, INK if v == 0 else "#e5e7eb", 1.6 if v == 0 else 1.0))

    bw = 92
    cols = [130, 300, 470, 620]

    # 1) +Voc/T — єдина сила вгору (зелена): 0 → +2.02
    x = cols[0]
    parts.append(rect(x - bw / 2, Y(2.02), bw, Y(0) - Y(2.02), fill="#e8f6ee", stroke=FIELD, sw=2.2, rx=4))
    parts.append(text(x, Y(2.02) - 22, "+Voc/T", 13, FIELD, bold=True))
    parts.append(text(x, Y(2.02) - 7, "+2.02", 13, FIELD, bold=True))
    parts.append(text(x, 432, "явний", 12, INK))
    parts.append(text(x, 448, "потенціал", 12, MUTED))

    # 2) −Eg0/qT — головний обвал (синій): +2.02 → −2.01
    x = cols[1]
    parts.append(rect(x - bw / 2, Y(2.02), bw, Y(-2.01) - Y(2.02), fill="#eaf0fd", stroke=NEG, sw=2.2, rx=4))
    parts.append(text(x, Y(-2.01) + 20, "−Eg0/qT", 13, NEG, bold=True))
    parts.append(text(x, Y(-2.01) + 36, "−4.03", 13, NEG, bold=True))
    parts.append(text(x, 432, "обвал", 12, INK))
    parts.append(text(x, 448, "струмів", 12, MUTED))

    # 3) −γk/q — дрібний вниз (синій): −2.01 → −2.27
    x = cols[2]
    parts.append(rect(x - bw / 2, Y(-2.01), bw, Y(-2.27) - Y(-2.01), fill="#eaf0fd", stroke=NEG, sw=2.2, rx=4))
    parts.append(text(x, Y(-2.01) - 9, "−γk/q  −0.26", 12, NEG, bold=True))
    parts.append(text(x, 432, "густина", 12, INK))
    parts.append(text(x, 448, "станів", 12, MUTED))

    # 4) разом: 0 → −2.27
    x = cols[3]
    parts.append(rect(x - bw / 2, Y(0), bw, Y(-2.27) - Y(0), fill="#f0f0f0", stroke=INK, sw=2.4, rx=4))
    parts.append(text(x, Y(-2.27) + 20, "разом", 13, INK, bold=True))
    parts.append(text(x, Y(-2.27) + 36, "−2.27", 13, INK, bold=True))
    parts.append(text(x, 432, "нахил", 12, INK))
    parts.append(text(x, 448, "dVoc/dT", 12, MUTED))

    # пунктирні звʼязки каскаду (рівні накопичення)
    parts.append(line(cols[0] + bw / 2, Y(2.02), cols[1] - bw / 2, Y(2.02), MUTED, 1.2, dash="4,3"))
    parts.append(line(cols[1] + bw / 2, Y(-2.01), cols[2] - bw / 2, Y(-2.01), MUTED, 1.2, dash="4,3"))
    parts.append(line(cols[2] + bw / 2, Y(-2.27), cols[3] - bw / 2, Y(-2.27), MUTED, 1.2, dash="4,3"))

    render(os.path.join(IMG, "voc-slope-decomp.svg"), w, h, *parts,
           title="Одна сила вгору, дві вниз: обвал перемагає надію вдвічі")


# ── Фігура 6 (вставка math): βVoc як функція самої Voc ──────────────────────
def fig_beta_voc():
    w, h = 740, 450
    x0, xR = 110, 650
    def X(Voc): return x0 + (Voc - 0.54) * (xR - x0) / (0.78 - 0.54)
    def Y(b):   return 80 + (-b) * 625.0         # b у %/°C (відʼємне): 0→80, −0.48→380

    def beta(Voc):
        dV = -(1.277 - Voc) / 298.0              # В/К
        return dV / Voc * 100.0                  # %/°C

    parts = []
    parts.append(line(x0, 78, x0, 388, INK, 2.0))
    parts.append(line(x0, Y(0), xR + 10, Y(0), INK, 2.0))
    for v in (0.55, 0.60, 0.65, 0.70, 0.75):
        parts.append(line(X(v), Y(0), X(v), Y(0) + 5, INK, 1.5))
        parts.append(text(X(v), Y(0) + 22, "%.2f" % v, 12, MUTED))
    parts.append(text((x0 + xR) / 2, Y(0) + 44, "напруга холостого ходу Voc, В", 13, MUTED))
    for b in (0.0, -0.1, -0.2, -0.3, -0.4):
        parts.append(line(x0 - 5, Y(b), x0, Y(b), INK, 1.5))
        parts.append(text(x0 - 10, Y(b) + 4, "%.1f" % b, 12, MUTED, anchor="end"))
        if b != 0.0:
            parts.append(line(x0, Y(b), xR, Y(b), "#eef0f2", 1.0))
    parts.append(text(x0 - 40, 68, "βVoc, %/°C", 12, MUTED, anchor="start"))

    # крива βVoc(Voc)
    pts, v = [], 0.54
    while v <= 0.7801:
        pts.append((X(v), Y(beta(v))))
        v += 0.005
    parts.append(polyline(pts, NEG, sw=3))

    def dot(Voc, col):
        b = beta(Voc)
        parts.append(circle(X(Voc), Y(b), 6, col, col, 1))
        return X(Voc), Y(b), b

    # звичайний моно-Si
    mx, my, mb = dot(0.64, NEG)
    parts.append(line(mx, my, 258, 178, MUTED, 1.0))
    parts.append(mtext(258, 166, ["звичайний моно-Si", "≈ 0.64 В → %.2f %%/°C" % mb], 12, INK))
    # даташитні −0.30
    dx, dy, db = dot(0.68, INK)
    parts.append(line(dx, dy, 476, 352, MUTED, 1.0))
    parts.append(mtext(476, 356, ["даташитні −0.30 %/°C —", "це вже Voc ≈ 0.68 В"], 12, INK))
    # гетероперехід
    hx, hy, hb = dot(0.73, FIELD)
    parts.append(line(hx, hy, 590, 168, MUTED, 1.0))
    parts.append(mtext(590, 156, ["гетероперехід", "0.73 В → %.2f %%/°C" % hb], 12, FIELD))

    render(os.path.join(IMG, "beta-vs-voc.svg"), w, h, *parts,
           title="Менший температурний коефіцієнт — це просто вища Voc")


if __name__ == "__main__":
    fig_iv_shift()
    fig_coeff()
    fig_string()
    fig_window()
    fig_slope_decomp()
    fig_beta_voc()
    print("ok: iv-shift, coeff-vs-temp, string-cold-voc, string-window, voc-slope-decomp, beta-vs-voc")
