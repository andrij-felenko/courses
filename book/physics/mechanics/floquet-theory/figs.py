# -*- coding: utf-8 -*-
"""Фігури до статті «Теорія Флоке».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── Fig 1: Періодична система та оператор монодромії M = Φ(T) ─────────────────
def fig_floquet_system_concept():
    W, H = 820, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Періодична лінійна система та оператор монодромії M = Φ(T)", size=16, bold=True))

    # Ліва панель: часова динаміка x(t) та коефіцієнтів A(t)
    PL, PW = 50, 340
    PT, PH = 60, 380
    f.append(rect(PL, PT, PW, PH, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(PL + PW / 2, PT + 24, "Неперервний часовий простір: dx/dt = A(t)·x", size=13, color=INK, bold=True))

    # Вісь часу t
    f.append(line(PL + 30, PT + PH - 40, PL + PW - 20, PT + PH - 40, color=INK, sw=1.8))
    f.append(text(PL + PW - 15, PT + PH - 35, "t", size=13, color=INK, bold=True, anchor="start"))

    # Маркери періодів T, 2T, 3T
    x0_t = PL + 45
    x1_t = PL + 130
    x2_t = PL + 215
    x3_t = PL + 300

    for xt, lbl in [(x0_t, "0"), (x1_t, "T"), (x2_t, "2T"), (x3_t, "3T")]:
        f.append(line(xt, PT + 45, xt, PT + PH - 35, color="#cbd5e1", sw=1.2, dash="4,4"))
        f.append(text(xt, PT + PH - 20, lbl, size=13, color=INK, bold=True))

    # Періодичний коефіцієнт A(t) (хвиля згори)
    pts_A = []
    for i in range(120):
        t_val = i / 119.0
        x_px = x0_t + t_val * (x3_t - x0_t)
        y_px = (PT + 80) - 15 * math.sin(2 * math.pi * (t_val * 3.0))
        pts_A.append("%.1f,%.1f" % (x_px, y_px))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(pts_A), FIELD))
    f.append(text(PL + PW / 2, PT + 48, "Періодичний коефіцієнт: A(t + T) = A(t)", size=12, color=FIELD, bold=True))

    # Траєкторія x(t)
    pts_x = []
    for i in range(120):
        t_val = i / 119.0
        x_px = x0_t + t_val * (x3_t - x0_t)
        env = math.exp(0.35 * (t_val * 3.0))
        mod = 1.0 + 0.25 * math.sin(2 * math.pi * (t_val * 3.0) - 0.5)
        y_val = (PT + PH - 100) - 22 * env * mod
        pts_x.append("%.1f,%.1f" % (x_px, y_val))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_x), POS))

    # Точки перетину
    for xt in [x0_t, x1_t, x2_t, x3_t]:
        t_val = (xt - x0_t) / (x3_t - x0_t)
        env = math.exp(0.35 * (t_val * 3.0))
        mod = 1.0 + 0.25 * math.sin(2 * math.pi * (t_val * 3.0) - 0.5)
        y_val = (PT + PH - 100) - 22 * env * mod
        f.append(circle(xt, y_val, 4.5, fill=POS, stroke=INK, sw=1.2))

    f.append(text(PL + 30, PT + PH - 160, "Траєкторія x(t) = P(t)·e^(μ·t)", size=12, color=POS, bold=True, anchor="start"))

    # Права панель: Дискретне відображення Пуанкаре / монодромія
    PR, RW = 430, 340
    f.append(rect(PR, PT, RW, PH, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(PR + RW / 2, PT + 24, "Дискретне стробоскопічне відображення", size=13, color=INK, bold=True))

    # Вузли фазових станів x(0) -> x(T) -> x(2T) -> x(3T)
    states = [
        (PR + 50, PT + 130, "x(0)"),
        (PR + 130, PT + 130, "x(T)"),
        (PR + 210, PT + 130, "x(2T)"),
        (PR + 290, PT + 130, "x(3T)"),
    ]

    for i in range(len(states) - 1):
        x_from, y_from, lbl_from = states[i]
        x_to, y_to, lbl_to = states[i + 1]

        # Стрілка відображення M
        f.append('<path d="M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.0"/>' %
                 (x_from + 16, y_from, (x_from + x_to) / 2, y_from - 30, x_to - 16, y_to, NEG))
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' %
                 (x_to - 16, y_to, x_to - 22, y_to - 5, x_to - 22, y_to + 5, NEG))
        f.append(text((x_from + x_to) / 2, y_from - 34, "M", size=13, color=NEG, bold=True))

    for x_s, y_s, lbl_s in states:
        f.append(circle(x_s, y_s, 16, fill="#eff6ff", stroke=NEG, sw=1.8))
        f.append(text(x_s, y_s + 4, lbl_s, size=11, color=INK, bold=True))

    # Рамка з поясненням
    lb, tw, th = textbox(PR + RW / 2, PT + PH - 90,
                         "Оператор монодромії M = Φ(T):\n"
                         "• x((n+1)·T) = M · x(n·T)\n"
                         "• x(n·T) = Mⁿ · x(0)\n"
                         "• Зводить ODE з A(t) до Mⁿ",
                         size=12, pad=8, fill="#ffffff", stroke="#94a3b8", sw=1.2, color=INK, bold=False)
    f.append(lb)

    render(os.path.join(IMG, 'floquet-system-concept.svg'), W, H, *f)

# ── Fig 2: Мультиплікатори Флоке та деформація фазового простору ──────────────
def fig_monodromy_mapping():
    W, H = 820, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Дія оператора монодромії M та мультиплікатори Флоке на комплексній площині", size=16, bold=True))

    # Ліва частина: Комплексна площина мультиплікаторів |λ|
    PL, PW = 50, 350
    PT, PH = 60, 400
    f.append(rect(PL, PT, PW, PH, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(PL + PW / 2, PT + 24, "Комплексна площина власного значення λ", size=13, color=INK, bold=True))

    CX, CY = PL + PW / 2, PT + PH / 2 + 10
    R_unit = 105

    # Заповнення областей
    f.append(rect(PL + 10, PT + 40, PW - 20, PH - 50, fill="#fef2f2", stroke="none", sw=0, rx=4))
    f.append(circle(CX, CY, R_unit, fill="#f0fdf4", stroke="none", sw=0))

    # Одиничне коло |λ| = 1
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5,4"/>' %
             (CX, CY, R_unit, FIELD))
    f.append(text(CX + R_unit * 0.707 + 16, CY - R_unit * 0.707 - 6, "|λ| = 1", size=12, color=FIELD, bold=True))

    # Осі Re(λ) та Im(λ)
    f.append(line(PL + 20, CY, PL + PW - 20, CY, color="#94a3b8", sw=1.5))
    f.append(line(CX, PT + 40, CX, PT + PH - 20, color="#94a3b8", sw=1.5))
    f.append(text(PL + PW - 15, CY - 8, "Re(λ)", size=12, color=INK, bold=True))
    f.append(text(CX + 10, PT + 48, "Im(λ)", size=12, color=INK, bold=True))

    # Приклади мультиплікаторів
    l1_x, l1_y = CX + 0.45 * R_unit, CY - 0.3 * R_unit
    f.append(circle(l1_x, l1_y, 5, fill=NEG, stroke=INK, sw=1.2))
    f.append(text(l1_x + 12, l1_y - 4, "λ₁ (|λ₁| < 1)", size=11, color=NEG, bold=True))

    l2_x, l2_y = CX - 1.35 * R_unit, CY - 0.1 * R_unit
    f.append(circle(l2_x, l2_y, 5, fill=POS, stroke=INK, sw=1.2))
    f.append(text(l2_x - 12, l2_y - 8, "λ₂ (|λ₂| > 1)", size=11, color=POS, anchor="end", bold=True))

    # Підписи областей
    f.append(text(CX, CY + 45, "Стійка область (|λ| < 1)", size=11, color="#15803d", anchor="middle", bold=True))
    f.append(text(PL + 65, PT + 60, "Нестійкість (|λ| > 1)", size=11, color="#b91c1c", anchor="start", bold=True))

    # Права частина: Деформація фазового об'єму (початковий круг -> еліпс)
    PR, RW = 430, 340
    f.append(rect(PR, PT, RW, PH, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(PR + RW / 2, PT + 24, "Трансформація фазового об'єму за період T", size=13, color=INK, bold=True))

    # Початковий фазовий кружечок t = 0
    C0_x, C0_y = PR + 75, PT + PH / 2 - 10
    f.append(circle(C0_x, C0_y, 40, fill="#e0f2fe", stroke=NEG, sw=1.8))
    f.append(text(C0_x, C0_y + 4, "V(0)", size=12, color=NEG, bold=True))
    f.append(text(C0_x, C0_y + 58, "Початковий стан", size=11, color=INK))

    # Стрілка дії M
    f.append(line(C0_x + 48, C0_y, PR + RW - 120, C0_y, color=INK, sw=2.0))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' %
             (PR + RW - 120, C0_y, PR + RW - 128, C0_y - 5, PR + RW - 128, C0_y + 5, INK))
    f.append(text((C0_x + PR + RW - 120) / 2, C0_y - 12, "Матриця M", size=12, color=INK, bold=True))

    # Кінцевий деформований еліпс t = T
    CE_x, CE_y = PR + RW - 65, PT + PH / 2 - 10
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="18" ry="70" transform="rotate(-25 %.1f %.1f)" fill="#fee2e2" stroke="%s" stroke-width="1.8"/>' %
             (CE_x, CE_y, CE_x, CE_y, POS))
    f.append(text(CE_x, CE_y + 4, "V(T)", size=12, color=POS, bold=True))
    f.append(text(CE_x, CE_y + 85, "Деформація", size=11, color=INK))

    f.append(text(PR + RW / 2, PT + PH - 35, "det M = exp(∫₀ᵀ tr A(s) ds) = λ₁·λ₂", size=12, color=INK, bold=True))

    render(os.path.join(IMG, 'monodromy-mapping.svg'), W, H, *f)

# ── Fig 3: Діаграма Інса — Стретта (карта стійкості Матьє) ────────────────────
def fig_stability_diagram_mathieu():
    W, H = 820, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Діаграма Інса — Стретта: язики нестійкості рівняння Матьє", size=16, bold=True))

    PL, PW = 70, 690
    PT, PH = 60, 410

    # Фон системи - зелений (стійкість)
    f.append(rect(PL, PT, PW, PH, fill="#f0fdf4", stroke="#cbd5e1", sw=1.5, rx=6))

    # Розмітка осей: q на ові X (0 .. 3.5), a на осі Y (-1 .. 9)
    def Xq(q):
        return PL + (q / 3.5) * PW

    def Ya(a):
        return PT + PH - ((a - (-1.0)) / 10.0) * PH

    # Зони нестійкості (клини / язики |tr M| > 2)
    pts_zone1 = []
    n_pts = 40
    for i in range(n_pts + 1):
        q = 3.5 * (i / n_pts)
        a_low = 1.0 - q - (q**2)/8.0 + (q**3)/64.0
        pts_zone1.append("%.1f,%.1f" % (Xq(q), Ya(a_low)))
    for i in range(n_pts, -1, -1):
        q = 3.5 * (i / n_pts)
        a_high = 1.0 + q - (q**2)/8.0 - (q**3)/64.0
        pts_zone1.append("%.1f,%.1f" % (Xq(q), Ya(a_high)))

    f.append('<polygon points="%s" fill="#fef2f2" stroke="%s" stroke-width="1.8"/>' % (" ".join(pts_zone1), POS))
    f.append(text(Xq(1.8), Ya(1.8), "Зона 1: |tr M| > 2\n(Головний резонанс a ≈ 1)", size=11, color=POS, bold=True))

    pts_zone2 = []
    for i in range(n_pts + 1):
        q = 3.5 * (i / n_pts)
        a_low = 4.0 - (1.0/12.0)*(q**2)
        pts_zone2.append("%.1f,%.1f" % (Xq(q), Ya(a_low)))
    for i in range(n_pts, -1, -1):
        q = 3.5 * (i / n_pts)
        a_high = 4.0 + (5.0/12.0)*(q**2)
        pts_zone2.append("%.1f,%.1f" % (Xq(q), Ya(a_high)))

    f.append('<polygon points="%s" fill="#fef2f2" stroke="%s" stroke-width="1.8"/>' % (" ".join(pts_zone2), POS))
    f.append(text(Xq(2.2), Ya(4.5), "Зона 2: a ≈ 4", size=11, color=POS, bold=True))

    pts_zone3 = []
    for i in range(n_pts + 1):
        q = 3.5 * (i / n_pts)
        a_low = 9.0 - (1.0/30.0)*(q**3)
        pts_zone3.append("%.1f,%.1f" % (Xq(q), Ya(a_low)))
    for i in range(n_pts, -1, -1):
        q = 3.5 * (i / n_pts)
        a_high = 9.0 + (1.0/30.0)*(q**3)
        pts_zone3.append("%.1f,%.1f" % (Xq(q), Ya(a_high)))

    f.append('<polygon points="%s" fill="#fef2f2" stroke="%s" stroke-width="1.8"/>' % (" ".join(pts_zone3), POS))

    # Осі координат
    f.append(line(PL, Ya(0), PL + PW, Ya(0), color=INK, sw=1.5, dash="4,4"))
    f.append(line(PL, PT + PH, PL + PW, PT + PH, color=INK, sw=2.0))
    f.append(line(PL, PT, PL, PT + PH, color=INK, sw=2.0))

    # Засічки q
    for q_v in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]:
        x = Xq(q_v)
        f.append(line(x, PT + PH, x, PT + PH + 6, color=INK, sw=1.5))
        f.append(text(x, PT + PH + 22, "%.1f" % q_v, size=12, color=INK))

    # Засічки a
    for a_v in [-1, 0, 1, 3, 5, 7, 9]:
        y = Ya(a_v)
        f.append(line(PL - 6, y, PL, y, color=INK, sw=1.5))
        f.append(text(PL - 12, y + 4, "%d" % a_v, size=12, color=INK, anchor="end"))

    # Підписи осей
    f.append(text(PL + PW / 2, PT + PH + 46, "Параметр амплітуди збудження q", size=14, color=INK, anchor="middle", bold=True))
    f.append(text(PL - 46, PT + PH / 2, "Параметр частоти a = (ω₀ / ω)²", size=14, color=INK, anchor="middle", bold=True))

    # Пояснювальні рамки
    lb1, w1, h1 = textbox(PL + PW - 230, PT + 40, "Стійка область (|tr M| < 2):\nОбмежені коливання\n|λ₁| = |λ₂| = 1", size=11, pad=6, fill="#ffffff", stroke="#16a34a", sw=1.2, color="#15803d")
    f.append(lb1)

    lb2, w2, h2 = textbox(PL + PW - 230, PT + 115, "Нестійка область (|tr M| > 2):\nЕкспоненціальний розмах\n|λ₁| > 1 (Резонанс)", size=11, pad=6, fill="#ffffff", stroke="#dc2626", sw=1.2, color="#b91c1c")
    f.append(lb2)

    render(os.path.join(IMG, 'stability-diagram-mathieu.svg'), W, H, *f)

if __name__ == "__main__":
    fig_floquet_system_concept()
    fig_monodromy_mapping()
    fig_stability_diagram_mathieu()
    print("Згенеровано 3 SVG фігури у folder img/")
