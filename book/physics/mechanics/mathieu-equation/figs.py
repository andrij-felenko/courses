# -*- coding: utf-8 -*-
"""Фігури до статті «Рівняння Матьє».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline_path(pts, color=LINE, sw=1.5, dash=None, fill="none"):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    path_d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return f'<path d="{path_d}" fill="{fill}" stroke="{color}" stroke-width="{sw:.1f}"{d_attr}/>'


def polygon_path(pts, fill=FILL, stroke="none", sw=0):
    path_d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts) + " Z"
    return f'<path d="{path_d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'


# ── Fig 1: Діаграма стійкості Інса — Стратта (q, a) ───────────────────────────
def fig_ince_strutt_diagram():
    W, H = 820, 560
    f = []
    f.append(text(W / 2, 28, "Діаграма стійкості Інса — Стратта (рівняння Матьє)", size=16, bold=True))

    PL, PW = 80, 680
    PT, PH = 60, 430

    def Xq(q):
        return PL + (q / 3.5) * PW

    def Ya(a):
        return PT + PH - ((a - (-1.5)) / 11.0) * PH

    f.append(rect(PL, PT, PW, PH, fill="#e0f2fe", stroke="#94a3b8", sw=1.5, rx=4))

    N_PTS = 80
    q_vals = [3.5 * i / N_PTS for i in range(N_PTS + 1)]

    def get_a0(q):
        return -0.5 * q**2 + (q**4) / 128.0

    def get_b1(q):
        return 1.0 - q - 0.125 * q**2 + (q**3) / 64.0 + (q**4) / 1536.0

    def get_a1(q):
        return 1.0 + q - 0.125 * q**2 - (q**3) / 64.0 + (q**4) / 1536.0

    def get_b2(q):
        return 4.0 - (q**2) / 12.0 + 5.0 * (q**4) / 13824.0

    def get_a2(q):
        return 4.0 + 5.0 * (q**2) / 12.0 - 11.0 * (q**4) / 13824.0

    def get_b3(q):
        return 9.0 - (q**2) / 16.0

    def get_a3(q):
        return 9.0 + (q**2) / 16.0

    pts_u0 = [(Xq(q), Ya(-1.5)) for q in q_vals]
    pts_u0_top = [(Xq(q), Ya(get_a0(q))) for q in reversed(q_vals)]
    f.append(polygon_path(pts_u0 + pts_u0_top, fill="#fee2e2"))

    pts_b1 = [(Xq(q), Ya(get_b1(q))) for q in q_vals]
    pts_a1_rev = [(Xq(q), Ya(get_a1(q))) for q in reversed(q_vals)]
    f.append(polygon_path(pts_b1 + pts_a1_rev, fill="#fee2e2"))

    pts_b2 = [(Xq(q), Ya(get_b2(q))) for q in q_vals]
    pts_a2_rev = [(Xq(q), Ya(get_a2(q))) for q in reversed(q_vals)]
    f.append(polygon_path(pts_b2 + pts_a2_rev, fill="#fee2e2"))

    pts_b3 = [(Xq(q), Ya(get_b3(q))) for q in q_vals]
    pts_a3_rev = [(Xq(q), Ya(get_a3(q))) for q in reversed(q_vals)]
    f.append(polygon_path(pts_b3 + pts_a3_rev, fill="#fee2e2"))

    f.append(polyline_path([(Xq(q), Ya(get_a0(q))) for q in q_vals], color=POS, sw=2.0))
    f.append(polyline_path([(Xq(q), Ya(get_b1(q))) for q in q_vals], color=POS, sw=2.0))
    f.append(polyline_path([(Xq(q), Ya(get_a1(q))) for q in q_vals], color=POS, sw=2.0))
    f.append(polyline_path([(Xq(q), Ya(get_b2(q))) for q in q_vals], color=POS, sw=2.0))
    f.append(polyline_path([(Xq(q), Ya(get_a2(q))) for q in q_vals], color=POS, sw=2.0))
    f.append(polyline_path([(Xq(q), Ya(get_b3(q))) for q in q_vals], color=POS, sw=2.0))

    for a_grid in range(0, 10, 2):
        f.append(line(PL, Ya(a_grid), PL + PW, Ya(a_grid), color="#cbd5e1", sw=1.0, dash="4,4"))
        f.append(text(PL - 10, Ya(a_grid) + 4, str(a_grid), size=12, color=MUTED, anchor="end"))
    f.append(text(PL - 10, Ya(-1) + 4, "-1", size=12, color=MUTED, anchor="end"))

    for q_grid in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        f.append(line(Xq(q_grid), PT, Xq(q_grid), PT + PH, color="#cbd5e1", sw=1.0, dash="4,4"))
        f.append(text(Xq(q_grid), PT + PH + 20, f"{q_grid:.1f}", size=12, color=MUTED, anchor="middle"))
    f.append(text(Xq(0), PT + PH + 20, "0", size=12, color=MUTED, anchor="middle"))

    f.append(line(PL, Ya(0), PL + PW, Ya(0), color=INK, sw=1.5))
    f.append(line(Xq(0), PT, Xq(0), PT + PH, color=INK, sw=1.5))

    f.append(text(PL + PW / 2, PT + PH + 45, "Параметр амплітуди модуляції q", size=14, bold=True))
    f.append(text(PL - 45, PT + PH / 2, "Параметр відношення частот a", size=14, bold=True, anchor="middle"))

    f.append(text(Xq(1.2), Ya(1.0), "Головний язик нестійкості (n = 1)", size=13, color=POS, bold=True))
    f.append(text(Xq(2.2), Ya(4.0), "Другий язик (n = 2)", size=12, color=POS, bold=True))
    f.append(text(Xq(0.8), Ya(2.5), "Область стійкості", size=14, color=NEG, bold=True))
    f.append(text(Xq(0.5), Ya(-0.8), "Нестійкість (a < a₀)", size=12, color=POS, bold=True))

    f.append(circle(Xq(0.7), Ya(0.2), 6, fill=FIELD, stroke=INK, sw=1.5))
    f.append(arrow(Xq(1.5), Ya(-0.2), Xq(0.75), Ya(0.15), color=FIELD, sw=1.5))
    tb_paul, _, _ = textbox(Xq(2.2), Ya(-0.2), "Робоча точка пастки Поля\n(q = 0.706, a = 0.237)", size=11, fill="#ecfdf5", stroke=FIELD)
    f.append(tb_paul)

    render(os.path.join(IMG, "ince-strutt-diagram.svg"), W, H, *f)


# ── Fig 2: Фізичні системи Матьє ─────────────────────────────────────────────
def fig_mathieu_physical_systems():
    W, H = 860, 440
    f = []
    f.append(text(W / 2, 28, "Фізичні системи з динаміката Матьє", size=16, bold=True))

    w_card = 260
    h_card = 350
    y_card = 55

    # Panel A: Kapitza Pendulum
    x_a = 20
    f.append(rect(x_a, y_card, w_card, h_card, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(x_a + w_card / 2, y_card + 28, "Параметричний маятник", size=14, bold=True, color=INK))
    f.append(text(x_a + w_card / 2, y_card + 46, "(Маятник Капіци)", size=12, italic=True, color=MUTED))

    cx_a = x_a + w_card / 2
    cy_a = y_card + 190

    # Base vibrator
    f.append(rect(cx_a - 30, cy_a - 40, 60, 20, fill="#e2e8f0", stroke=INK, sw=1.5, rx=3))
    f.append(arrow(cx_a, cy_a - 55, cx_a, cy_a - 25, color=POS, sw=2.0))
    f.append(text(cx_a + 42, cy_a - 30, "z(t) = A cos(Ωt)", size=11, color=POS, bold=True))

    # Inverted rod
    f.append(line(cx_a, cy_a - 30, cx_a - 22, cy_a - 100, color=LINE, sw=2.5))
    f.append(circle(cx_a - 22, cy_a - 100, 10, fill=POS, stroke=INK, sw=1.5))
    f.append(text(cx_a - 40, cy_a - 100, "m", size=12, bold=True))
    f.append(line(cx_a, cy_a - 30, cx_a, cy_a - 110, color=MUTED, sw=1.0, dash="3,3"))

    tb_a, _, _ = textbox(cx_a, y_card + 290, "Вертикальна вібрація підвісу\nстабілізує перевернутий стан\nпри високій частоті Ω", size=11, fill="#ffffff", stroke="#cbd5e1")
    f.append(tb_a)

    # Panel B: Paul Ion Trap
    x_b = 300
    f.append(rect(x_b, y_card, w_card, h_card, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(x_b + w_card / 2, y_card + 28, "Квадрупольна пастка Поля", size=14, bold=True, color=INK))
    f.append(text(x_b + w_card / 2, y_card + 46, "(Сепарація іонів)", size=12, italic=True, color=MUTED))

    cx_b = x_b + w_card / 2
    cy_b = y_card + 160

    f.append(circle(cx_b - 55, cy_b, 22, fill="#fed7aa", stroke="#ea580c", sw=1.5))
    f.append(circle(cx_b + 55, cy_b, 22, fill="#fed7aa", stroke="#ea580c", sw=1.5))
    f.append(circle(cx_b, cy_b - 55, 22, fill="#bfdbfe", stroke="#2563eb", sw=1.5))
    f.append(circle(cx_b, cy_b + 55, 22, fill="#bfdbfe", stroke="#2563eb", sw=1.5))

    f.append(text(cx_b - 55, cy_b + 4, "+V", size=11, bold=True, color="#c2410c"))
    f.append(text(cx_b + 55, cy_b + 4, "+V", size=11, bold=True, color="#c2410c"))
    f.append(text(cx_b, cy_b - 51, "-V", size=11, bold=True, color="#1d4ed8"))
    f.append(text(cx_b, cy_b + 59, "-V", size=11, bold=True, color="#1d4ed8"))

    f.append(circle(cx_b, cy_b, 8, fill=FIELD, stroke=INK, sw=1.5))
    f.append(text(cx_b + 14, cy_b - 10, "e⁺", size=12, bold=True, color=FIELD))

    tb_b, _, _ = textbox(cx_b, y_card + 290, "ВЧ + ДК електричні поля\nутримують іони певного m/e\nвсередині зони стійкості", size=11, fill="#ffffff", stroke="#cbd5e1")
    f.append(tb_b)

    # Panel C: Elliptic Membrane
    x_c = 580
    f.append(rect(x_c, y_card, w_card, h_card, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(x_c + w_card / 2, y_card + 28, "Еліптична мембрана", size=14, bold=True, color=INK))
    f.append(text(x_c + w_card / 2, y_card + 46, "(Історичний витік 1868 р.)", size=12, italic=True, color=MUTED))

    cx_c = x_c + w_card / 2
    cy_c = y_card + 160

    f.append(f'<ellipse cx="{cx_c:.1f}" cy="{cy_c:.1f}" rx="75" ry="48" fill="#f1f5f9" stroke="{INK}" stroke-width="2.0"/>')
    f.append(circle(cx_c - 40, cy_c, 3, fill=POS, stroke=POS, sw=1))
    f.append(circle(cx_c + 40, cy_c, 3, fill=POS, stroke=POS, sw=1))
    f.append(f'<ellipse cx="{cx_c:.1f}" cy="{cy_c:.1f}" rx="50" ry="32" fill="none" stroke="{NEG}" stroke-width="1.2" stroke-dasharray="4,3"/>')
    f.append(line(cx_c, cy_c - 48, cx_c, cy_c + 48, color=NEG, sw=1.2, dash="4,3"))

    tb_c, _, _ = textbox(cx_c, y_card + 290, "Коливання мембрани в еліптичних\nкоординатах розділяються на\nфункції Матьє ceₙ(z) та seₙ(z)", size=11, fill="#ffffff", stroke="#cbd5e1")
    f.append(tb_c)

    render(os.path.join(IMG, "mathieu-physical-systems.svg"), W, H, *f)


# ── Fig 3: Динаміка у фазовому просторі та в часі ─────────────────────────────
def fig_floquet_dynamics_phase():
    W, H = 840, 480
    f = []
    f.append(text(W / 2, 28, "Динаміка розв'язків у часовій та фазовій областях", size=16, bold=True))

    w_panel = 380
    h_panel = 390
    y_p = 60

    # Left Panel: Stable
    x_l = 30
    f.append(rect(x_l, y_p, w_panel, h_panel, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=8))
    f.append(text(x_l + w_panel / 2, y_p + 25, "Стійка область (обмежені коливання)", size=13, bold=True, color="#0369a1"))

    cx_lt = x_l + 30
    cy_lt = y_p + 110
    w_t = 320
    f.append(line(cx_lt, cy_lt, cx_lt + w_t, cy_lt, color=MUTED, sw=1.0))
    pts_st = []
    for i in range(160):
        t = i * 0.15
        val = math.cos(t) * math.cos(0.2 * t) + 0.2 * math.sin(1.8 * t)
        x_pix = cx_lt + (i / 160.0) * w_t
        y_pix = cy_lt - val * 30.0
        pts_st.append((x_pix, y_pix))
    f.append(polyline_path(pts_st, color=NEG, sw=1.8))
    f.append(text(cx_lt + w_t - 20, cy_lt - 35, "y(t)", size=12, color=NEG, bold=True))
    f.append(text(cx_lt + w_t / 2, cy_lt + 48, "Час t", size=11, color=MUTED))

    cx_lp = x_l + w_panel / 2
    cy_lp = y_p + 270
    f.append(line(cx_lp - 90, cy_lp, cx_lp + 90, cy_lp, color=MUTED, sw=1.0))
    f.append(line(cx_lp, cy_lp - 60, cx_lp, cy_lp + 60, color=MUTED, sw=1.0))

    pts_phase_st = []
    for i in range(200):
        t = i * 0.1
        y_val = math.cos(t) * math.cos(0.15 * t)
        dy_val = -math.sin(t) * math.cos(0.15 * t) - 0.15 * math.cos(t) * math.sin(0.15 * t)
        pts_phase_st.append((cx_lp + y_val * 65.0, cy_lp - dy_val * 45.0))
    f.append(polyline_path(pts_phase_st, color=NEG, sw=1.5))
    f.append(text(cx_lp + 100, cy_lp + 4, "y", size=12, bold=True))
    f.append(text(cx_lp + 4, cy_lp - 65, "dy/dt", size=12, bold=True))
    f.append(text(cx_lp, cy_lp + 80, "Обмежений фазовий торус", size=11, color=NEG, italic=True))

    # Right Panel: Unstable
    x_r = 430
    f.append(rect(x_r, y_p, w_panel, h_panel, fill="#fff1f2", stroke="#e11d48", sw=1.5, rx=8))
    f.append(text(x_r + w_panel / 2, y_p + 25, "Нестійка область (експоненційне зростання)", size=13, bold=True, color="#be123c"))

    cx_rt = x_r + 30
    cy_rt = y_p + 110
    f.append(line(cx_rt, cy_rt, cx_rt + w_t, cy_rt, color=MUTED, sw=1.0))
    pts_ust = []
    for i in range(160):
        t = i * 0.12
        amp = math.exp(0.025 * i)
        val = amp * math.cos(t)
        x_pix = cx_rt + (i / 160.0) * w_t
        y_pix = cy_rt - val * 6.0
        y_pix = max(cy_rt - 60, min(cy_rt + 60, y_pix))
        pts_ust.append((x_pix, y_pix))
    f.append(polyline_path(pts_ust, color=POS, sw=1.8))
    f.append(text(cx_rt + w_t - 20, cy_rt - 40, "y(t) ~ e^μt", size=12, color=POS, bold=True))
    f.append(text(cx_rt + w_t / 2, cy_rt + 48, "Час t", size=11, color=MUTED))

    cx_rp = x_r + w_panel / 2
    cy_rp = y_p + 270
    f.append(line(cx_rp - 90, cy_rp, cx_rp + 90, cy_rp, color=MUTED, sw=1.0))
    f.append(line(cx_rp, cy_rp - 60, cx_rp, cy_rp + 60, color=MUTED, sw=1.0))

    pts_phase_ust = []
    for i in range(180):
        t = i * 0.1
        amp = math.exp(0.015 * i)
        y_val = amp * math.cos(t)
        dy_val = amp * (-math.sin(t) + 0.15 * math.cos(t))
        pts_phase_ust.append((cx_rp + y_val * 6.0, cy_rp - dy_val * 5.0))
    f.append(polyline_path(pts_phase_ust, color=POS, sw=1.5))
    f.append(text(cx_rp + 100, cy_rp + 4, "y", size=12, bold=True))
    f.append(text(cx_rp + 4, cy_rp - 65, "dy/dt", size=12, bold=True))
    f.append(text(cx_rp, cy_rp + 80, "Розбіжна спіраль (експоненційний розгін)", size=11, color=POS, italic=True))

    render(os.path.join(IMG, "floquet-dynamics-phase.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ince_strutt_diagram()
    fig_mathieu_physical_systems()
    fig_floquet_dynamics_phase()
    print("Всі фігури успішно згенеровано у ./img/")
