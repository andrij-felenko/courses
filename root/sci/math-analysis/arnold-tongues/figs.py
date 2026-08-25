# -*- coding: utf-8 -*-
"""Фігури до статті «Язики Арнольда».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── Fig 1: Діаграма язиків Арнольда у просторі параметрів (Omega, K) ──────────
def fig_arnold_tongues_map():
    W, H = 820, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Діаграма язиків Арнольда в просторі параметрів (Ω, K)", size=16, bold=True))

    PL, PW = 80, 680
    PT, PH = 60, 420

    f.append(rect(PL, PT, PW, PH, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=4))

    YK1 = PT + PH - (1.0 / 1.3) * PH
    f.append(line(PL, YK1, PL + PW, YK1, color=POS, sw=1.8, dash="6,4"))
    f.append(text(PL + PW - 10, YK1 - 8, "Критична межа K = 1 (втрата інвертованості)", size=12, color=POS, anchor="end", bold=True))

    f.append(rect(PL, PT, PW, YK1 - PT, fill="#fff5f5", stroke="none", sw=0, rx=0))
    f.append(text(PL + 120, PT + 24, "Область перекриття язиків та хаосу (K > 1)", size=13, color="#b91c1c", anchor="start", bold=True, italic=True))

    tongues = [
        (0.0, 0.0, 0.08, "#e2e8f0", "0/1"),
        (0.2, 1.0/5.0, 0.09, "#fed7aa", "1/5"),
        (0.25, 1.0/4.0, 0.11, "#fde68a", "1/4"),
        (1.0/3.0, 1.0/3.0, 0.16, "#bfdbfe", "1/3"),
        (0.4, 2.0/5.0, 0.10, "#fed7aa", "2/5"),
        (0.5, 1.0/2.0, 0.28, "#bbf7d0", "1/2"),
        (0.6, 3.0/5.0, 0.10, "#fed7aa", "3/5"),
        (2.0/3.0, 2.0/3.0, 0.16, "#bfdbfe", "2/3"),
        (0.75, 3.0/4.0, 0.11, "#fde68a", "3/4"),
        (0.8, 4.0/5.0, 0.09, "#fed7aa", "4/5"),
        (1.0, 1.0, 0.08, "#e2e8f0", "1/1"),
    ]

    def Xom(om):
        return PL + om * PW

    def Yk(k):
        return PT + PH - (k / 1.3) * PH

    for om_val, ratio_val, w_fac, col, lbl in tongues:
        x_center = Xom(ratio_val)
        pts = []
        n_steps = 30
        for i in range(n_steps + 1):
            k = 1.2 * (i / n_steps)
            om_l = ratio_val - (w_fac / 2.0) * k * (1.0 + 0.2 * k**1.5)
            pts.append("%.1f,%.1f" % (Xom(om_l), Yk(k)))
        for i in range(n_steps, -1, -1):
            k = 1.2 * (i / n_steps)
            om_r = ratio_val + (w_fac / 2.0) * k * (1.0 + 0.2 * k**1.5)
            pts.append("%.1f,%.1f" % (Xom(om_r), Yk(k)))

        poly_str = " ".join(pts)
        f.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.2" opacity="0.85"/>' % (poly_str, col, INK))

        if lbl in ["1/3", "1/2", "2/3", "1/4", "3/4"]:
            y_lbl = Yk(0.55)
            f.append(text(x_center, y_lbl, lbl, size=12, color=INK, anchor="middle", bold=True))

    f.append(line(PL, PT + PH, PL + PW, PT + PH, color=INK, sw=2.0))
    f.append(line(PL, PT, PL, PT + PH, color=INK, sw=2.0))

    ticks_om = [(0.0, "0"), (0.2, "0.2"), (0.333, "1/3"), (0.5, "1/2"), (0.667, "2/3"), (0.8, "0.8"), (1.0, "1")]
    for om_v, om_lbl in ticks_om:
        x = Xom(om_v)
        f.append(line(x, PT + PH, x, PT + PH + 6, color=INK, sw=1.5))
        f.append(text(x, PT + PH + 22, om_lbl, size=12, color=INK, anchor="middle"))

    ticks_k = [(0.0, "0.0"), (0.5, "0.5"), (1.0, "1.0"), (1.3, "1.3")]
    for k_v, k_lbl in ticks_k:
        y = Yk(k_v)
        f.append(line(PL - 6, y, PL, y, color=INK, sw=1.5))
        f.append(text(PL - 12, y + 4, k_lbl, size=12, color=INK, anchor="end"))

    f.append(text(PL + PW / 2, PT + PH + 46, "Частотне відношення несбуреного руху Ω = ω₁ / ω₂", size=14, color=INK, anchor="middle", bold=True))
    f.append(text(PL - 54, PT + PH / 2, "Сила зв'язку K", size=14, color=INK, anchor="middle", bold=True))

    lb, tw, th = textbox(PL + 140, PT + PH - 70, "Дерево Фарея:\n1/3 та 1/2 → 2/5\n(медіанта розширює язики)", size=11, pad=6, fill="#ffffff", stroke="#94a3b8", sw=1.2, color=INK, bold=False)
    f.append(lb)

    render(os.path.join(IMG, 'arnold-tongues-map.svg'), W, H, *f)

# ── Fig 2: Драбина диявола (W(Omega) при K=0, K=0.5, K=1.0) ─────────────────
def fig_devils_staircase():
    W, H = 820, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Драбина диявола: число обертання W(Ω) при різних значеннях K", size=16, bold=True))

    PL, PW = 80, 680
    PT, PH = 60, 420

    f.append(rect(PL, PT, PW, PH, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=4))

    N = 400

    def get_rotation_num(om, k):
        if k == 0:
            return om
        res = [
            (0.0, 0.04), (1.0/5.0, 0.02), (1.0/4.0, 0.025), (1.0/3.0, 0.04),
            (2.0/5.0, 0.02), (1.0/2.0, 0.07), (3.0/5.0, 0.02), (2.0/3.0, 0.04),
            (3.0/4.0, 0.025), (4.0/5.0, 0.02), (1.0, 0.04)
        ]
        for r_val, half_w in res:
            w_act = half_w * (k ** 0.8)
            if abs(om - r_val) <= w_act:
                return r_val
        lower_r, lower_b = 0.0, 0.04 * (k ** 0.8)
        upper_r, upper_b = 1.0, 1.0 - 0.04 * (k ** 0.8)
        for r_val, half_w in res:
            w_act = half_w * (k ** 0.8)
            if r_val + w_act < om and r_val + w_act > lower_r + lower_b:
                lower_r, lower_b = r_val, r_val + w_act
            if r_val - w_act > om and r_val - w_act < upper_r - upper_b:
                upper_r, upper_b = r_val, r_val - w_act
        if upper_b <= lower_b:
            return lower_r
        t = (om - lower_b) / (upper_b - lower_b)
        t_smooth = t * t * (3 - 2 * t)
        return lower_r + t_smooth * (upper_r - lower_r)

    def Xom(om):
        return PL + om * PW

    def Yw(w):
        return PT + PH - w * PH

    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#94a3b8" stroke-width="1.8" stroke-dasharray="5,5"/>' % (Xom(0), Yw(0), Xom(1), Yw(1)))

    pts_k1_str = []
    for i in range(N + 1):
        om = i / N
        w_val = get_rotation_num(om, 1.0)
        pts_k1_str.append("%.1f,%.1f" % (Xom(om), Yw(w_val)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_k1_str), POS))

    plateaus = [
        (1.0/3.0, "W = 1/3"),
        (1.0/2.0, "W = 1/2"),
        (2.0/3.0, "W = 2/3")
    ]
    for w_val, lbl in plateaus:
        y = Yw(w_val)
        f.append(line(PL, y, PL + PW, y, color="#cbd5e1", sw=1.0, dash="3,3"))
        f.append(text(PL + 12, y - 6, lbl, size=12, color=INK, anchor="start", bold=True))

    f.append(line(PL, PT + PH, PL + PW, PT + PH, color=INK, sw=2.0))
    f.append(line(PL, PT, PL, PT + PH, color=INK, sw=2.0))

    for om_v in [0.0, 0.2, 0.333, 0.5, 0.667, 0.8, 1.0]:
        x = Xom(om_v)
        f.append(line(x, PT + PH, x, PT + PH + 6, color=INK, sw=1.5))
        lbl = "%.2f" % om_v if om_v not in [0.333, 0.667] else ("1/3" if om_v < 0.5 else "2/3")
        f.append(text(x, PT + PH + 22, lbl, size=12, color=INK, anchor="middle"))

    for w_v in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = Yw(w_v)
        f.append(line(PL - 6, y, PL, y, color=INK, sw=1.5))
        f.append(text(PL - 12, y + 4, "%.2f" % w_v, size=12, color=INK, anchor="end"))

    f.append(text(PL + PW / 2, PT + PH + 46, "Несбурене частотне відношення Ω", size=14, color=INK, anchor="middle", bold=True))
    f.append(text(PL - 54, PT + PH / 2, "Число обертання W(Ω)", size=14, color=INK, anchor="middle", bold=True))

    lx = PL + 340
    ly = PT + 340
    f.append(rect(lx, ly, 300, 64, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    f.append(line(lx + 14, ly + 20, lx + 44, ly + 20, color="#94a3b8", sw=2.0, dash="5,5"))
    f.append(text(lx + 52, ly + 24, "K = 0 (лінійний режим W = Ω)", size=12, color=INK, anchor="start"))
    f.append(line(lx + 14, ly + 44, lx + 44, ly + 44, color=POS, sw=2.5))
    f.append(text(lx + 52, ly + 48, "K = 1 (фрактальна драбина диявола)", size=12, color=INK, anchor="start", bold=True))

    render(os.path.join(IMG, 'devils-staircase.svg'), W, H, *f)

# ── Fig 3: Динаміка кругового відображення та втрата інвертованості ─────────
def fig_circle_map_dynamics():
    W, H = 820, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Геометрія синус-кругового відображення при K < 1 та K = 1", size=16, bold=True))

    PW, PH = 320, 320
    PT = 70
    PL1 = 70
    PL2 = 450

    f.append(rect(PL1, PT, PW, PH, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=4))
    f.append(text(PL1 + PW / 2, PT - 12, "Гладка строго монотонна крива (K = 0.5)", size=13, color=INK, anchor="middle", bold=True))

    f.append(rect(PL2, PT, PW, PH, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=4))
    f.append(text(PL2 + PW / 2, PT - 12, "Критичний стан з горизонтальною дотичною (K = 1.0)", size=13, color=POS, anchor="middle", bold=True))

    def X1(th): return PL1 + th * PW
    def Y1(th_next): return PT + PH - th_next * PH
    def X2(th): return PL2 + th * PW
    def Y2(th_next): return PT + PH - th_next * PH

    f.append(line(PL1, PT + PH, PL1 + PW, PT, color="#94a3b8", sw=1.5, dash="4,4"))
    f.append(line(PL2, PT + PH, PL2 + PW, PT, color="#94a3b8", sw=1.5, dash="4,4"))

    om = 0.2
    N = 200
    pts1, pts2 = [], []
    for i in range(N + 1):
        th = i / N
        f1 = th + om - (0.5 / (2 * math.pi)) * math.sin(2 * math.pi * th)
        f2 = th + om - (1.0 / (2 * math.pi)) * math.sin(2 * math.pi * th)
        pts1.append("%.1f,%.1f" % (X1(th), Y1(f1)))
        pts2.append("%.1f,%.1f" % (X2(th), Y2(f2)))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts1), NEG))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts2), POS))

    f.append(circle(X2(0.0), Y2(om), 5, fill=POS, stroke=INK, sw=1.5))
    f.append(line(X2(0.0), Y2(om), X2(0.25), Y2(om), color=POS, sw=1.8, dash="3,3"))
    lb, tw, th_b = textbox(X2(0.32), Y2(om) - 35, "f'(θ) = 0 (дотична = 0)", size=11, pad=5, fill="#fff5f5", stroke=POS, sw=1.0, color=POS, bold=True)
    f.append(lb)

    for PL, Xfn, Yfn in [(PL1, X1, Y1), (PL2, X2, Y2)]:
        f.append(line(PL, PT + PH, PL + PW, PT + PH, color=INK, sw=1.8))
        f.append(line(PL, PT, PL, PT + PH, color=INK, sw=1.8))
        f.append(text(PL + PW / 2, PT + PH + 36, "Фаза θₙ", size=13, color=INK, anchor="middle", bold=True))
        f.append(text(PL - 38, PT + PH / 2, "Фаза θₙ₊₁", size=13, color=INK, anchor="middle", bold=True))

    render(os.path.join(IMG, 'circle-map-dynamics.svg'), W, H, *f)

# ── Fig 4: Механізм фазового захоплення (синхронізація осциляторів) ─────────
def fig_synchronization_mechanism():
    W, H = 820, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Механізм фазового захоплення у збуреному осциляторі", size=16, bold=True))

    PL, PT = 60, 70
    PW, PH = 700, 360

    f.append(rect(PL, PT, PW, PH, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=4))

    b1, w1, h1 = textbox(PL + 180, PT + 80, "Автономний осцилятор\nВласна частота ω₀\nФаза дрейфує: θ(t) = ω₀ t", size=13, pad=12, fill="#eff6ff", stroke=NEG, sw=1.5, color=INK, bold=False)
    f.append(b1)

    b2, w2, h2 = textbox(PL + 520, PT + 80, "Зовнішній періодичний сигнал\nЧастота збудження ωₑ\nЗахоплення: θₙ₊₁ − θₙ = p/q", size=13, pad=12, fill="#f0fdf4", stroke=FIELD, sw=1.5, color=INK, bold=False)
    f.append(b2)

    f.append(arrow(PL + 300, PT + 80, PL + 390, PT + 80, color=POS, sw=2.5))
    f.append(text(PL + 345, PT + 58, "Зв'язок K", size=13, color=POS, anchor="middle", bold=True))

    PY = PT + 200
    f.append(line(PL + 40, PY + 120, PL + PW - 40, PY + 120, color="#94a3b8", sw=1.2))
    f.append(text(PL + 60, PY - 10, "Потенціал фазової пастки V(Δϕ) = −Δ·Δϕ − K·cos(Δϕ)", size=13, color=INK, anchor="start", bold=True))

    N = 250
    pts_v = []
    for i in range(N + 1):
        x_rel = i / N
        phi = 4 * math.pi * x_rel - 2 * math.pi
        v = -0.15 * phi - 0.8 * math.cos(phi)
        px = PL + 100 + x_rel * 500
        py = PY + 60 + v * 25
        pts_v.append("%.1f,%.1f" % (px, py))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_v), INK))

    phi_m = math.asin(-0.15 / 0.8) + 2 * math.pi
    x_rel_m = (phi_m) / (4 * math.pi)
    ball_x = PL + 100 + x_rel_m * 500
    ball_y = PY + 60 + (-0.15 * (phi_m - 2*math.pi) - 0.8 * math.cos(phi_m - 2*math.pi)) * 25

    f.append(circle(ball_x, ball_y - 8, 8, fill=POS, stroke=INK, sw=1.5))
    f.append(arrow(ball_x + 60, ball_y - 35, ball_x + 12, ball_y - 14, color=POS, sw=1.5))

    lb, tw, th = textbox(ball_x + 120, ball_y - 45, "Стійка фазова яма (lock-in)\nСистема заблокована у мінімумі", size=11, pad=6, fill="#ffffff", stroke=POS, sw=1.0, color=POS, bold=True)
    f.append(lb)

    render(os.path.join(IMG, 'arnold-tongues-map.svg'), W, H, *f)

if __name__ == "__main__":
    fig_arnold_tongues_map()
    fig_devils_staircase()
    fig_circle_map_dynamics()
    fig_synchronization_mechanism()
    print("Всі 4 фігури успішно згенеровано.")
