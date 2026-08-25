# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_percentile_cdf():
    """Кумулятивна функція розподілу (CDF) із позначеннями медіани p50, p90, p99 та p99.9."""
    W, H = 820, 480
    left = 90
    right = 770
    top = 50
    bottom = 410
    plot_w = right - left
    plot_h = bottom - top

    frags = []

    # Горизонтальні граничні лінії ймовірностей: 0.0 та 1.0
    for prob_val, prob_lbl in [(0.0, "0.00 (0%)"), (1.0, "1.00 (100%)")]:
        y = bottom - prob_val * plot_h
        frags.append(line(left, y, right, y, color="#e2e8f0", sw=1.0, dash="4,4"))
        frags.append(text(left - 12, y + 4, prob_lbl, size=11, color=INK, anchor="end"))

    # Осі зі стрілками
    frags.append(arrow(left, bottom, right + 20, bottom, color=INK, sw=1.8))
    frags.append(arrow(left, bottom, left, top - 20, color=INK, sw=1.8))

    # Підписи осей
    frags.append(text(right - 20, bottom + 25, "Затримка x (мс)", size=12, color=INK, bold=True, anchor="middle"))
    frags.append(text(left - 10, top - 28, "F(x) = P(X ≤ x)", size=12, color=INK, bold=True, anchor="end"))

    def cdf_func(x):
        if x < 5:
            return 0.0
        z1 = (math.log(x) - math.log(12)) / 0.5
        cdf1 = 0.5 * (1.0 + math.erf(z1 / math.sqrt(2)))
        z2 = (math.log(x) - math.log(120)) / 1.1
        cdf2 = 0.5 * (1.0 + math.erf(z2 / math.sqrt(2)))
        return 0.88 * cdf1 + 0.12 * cdf2

    x_max = 240.0
    pts = []
    num_steps = 150
    for i in range(num_steps + 1):
        x_val = i * (x_max / num_steps)
        f_val = cdf_func(x_val)
        px = left + (x_val / x_max) * plot_w
        py = bottom - f_val * plot_h
        pts.append(f"{px:.1f},{py:.1f}")

    frags.append(f'<polyline points="{" ".join(pts)}" stroke="{FIELD}" stroke-width="3" fill="none"/>')

    quantiles = [
        (0.50, "0.50 (p50)", "#2563eb"),
        (0.90, "0.90 (p90)", "#0891b2"),
        (0.99, "0.99 (p99)", "#dc2626")
    ]

    for target_p, p_label, q_color in quantiles:
        cur_x = 5.0
        for step in range(5000):
            cur_x += 0.05
            if cdf_func(cur_x) >= target_p:
                break
        
        qx = left + (cur_x / x_max) * plot_w
        qy = bottom - target_p * plot_h

        # Пунктири від осей до точки на кривій
        frags.append(line(left, qy, qx, qy, color=q_color, sw=1.5, dash="4,3"))
        frags.append(line(qx, qy, qx, bottom, color=q_color, sw=1.5, dash="4,3"))
        frags.append(circle(qx, qy, 5, fill=q_color, stroke=BG, sw=1.5))

        # Підпис на осі Y
        frags.append(text(left - 12, qy + 4, p_label, size=11, color=q_color, bold=True, anchor="end"))
        # Підпис на осі X
        frags.append(text(qx, bottom + 18, f"{cur_x:.0f} мс", size=11, color=q_color, bold=True, anchor="middle"))

    info_box, _, _ = textbox(
        570, 240,
        "Чому виникає небезпека на хвості:\n"
        "• Від p50 до p90 затримка зростає всього на 16 мс.\n"
        "• Від p90 до p99 затримка злітає на 167 мс.\n"
        "• Крива виходить на пологе плато: мізерний\n"
        "  приріст частки (+1%) коштує десятикратного\n"
        "  погіршення часу очікування.",
        size=11, color=INK, fill="#f8fafc", stroke=MUTED, rx=4, pad=10
    )
    frags.append(info_box)

    render(os.path.join(OUT, "percentile-cdf.svg"), W, H, *frags)


def fig_tail_amplification():
    """Підсилення затримки на хвості в розподілених системах при fan-out запитах."""
    W, H = 820, 480
    left = 90
    right = 760
    top = 60
    bottom = 400
    plot_w = right - left
    plot_h = bottom - top

    frags = []

    for prob in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        y = bottom - prob * plot_h
        frags.append(line(left, y, right, y, color="#e2e8f0", sw=1.0, dash="4,4"))
        frags.append(text(left - 12, y + 4, f"{int(prob * 100)}%", size=11, color=INK, anchor="end"))

    k_ticks = [1, 10, 25, 50, 75, 100]
    for k_val in k_ticks:
        x = left + ((k_val - 1) / 99.0) * plot_w
        frags.append(line(x, bottom, x, bottom + 5, color=INK, sw=1.2))
        frags.append(text(x, bottom + 18, str(k_val), size=11, color=INK, anchor="middle"))

    frags.append(arrow(left, bottom, right + 20, bottom, color=INK, sw=1.8))
    frags.append(arrow(left, bottom, left, top - 20, color=INK, sw=1.8))

    frags.append(text(right - 50, bottom + 38, "Кількість паралельних підзапитів K (Fan-out)", size=12, color=INK, bold=True, anchor="middle"))
    frags.append(text(left - 10, top - 26, "P(хоча б один запит потрапив у хвіст) = 1 - p^K", size=12, color=INK, bold=True, anchor="end"))

    curves = [
        (0.90, "#ef4444", "Вузол p90 (10% збійних)"),
        (0.99, "#f59e0b", "Вузол p99 (1% хвіст)"),
        (0.999, "#10b981", "Вузол p99.9 (0.1% хвіст)")
    ]

    for p_single, col, label in curves:
        pts = []
        for k_idx in range(1, 101):
            prob_tail = 1.0 - math.pow(p_single, k_idx)
            px = left + ((k_idx - 1) / 99.0) * plot_w
            py = bottom - prob_tail * plot_h
            pts.append(f"{px:.1f},{py:.1f}")
        frags.append(f'<polyline points="{" ".join(pts)}" stroke="{col}" stroke-width="2.8" fill="none"/>')

    k_target = 100
    prob_100 = 1.0 - math.pow(0.99, 100)
    pt_x = left + ((k_target - 1) / 99.0) * plot_w
    pt_y = bottom - prob_100 * plot_h
    frags.append(line(left, pt_y, pt_x, pt_y, color="#f59e0b", sw=1.4, dash="4,3"))
    frags.append(circle(pt_x, pt_y, 6, fill="#f59e0b", stroke=BG, sw=2))

    frags.append(text(pt_x - 12, pt_y - 12, "K=100: 63.4% клієнтів уповільнені!", size=11, color="#b45309", bold=True, anchor="end"))

    leg_x, leg_y = 350, 150
    leg_box, _, _ = textbox(
        leg_x, leg_y,
        "Рівень якості одного мікросервісу:\n"
        "■ Вузол p90 (хвіст 10%): при K=50 вже 99.5% запитів повільні\n"
        "■ Вузол p99 (хвіст 1%): при K=100 сповільнюється 63.4% запитів\n"
        "■ Вузол p99.9 (хвіст 0.1%): при K=100 лише 9.5% запитів у хвості",
        size=11, color=INK, fill="#f8fafc", stroke=MUTED, rx=4, pad=10
    )
    frags.append(leg_box)

    render(os.path.join(OUT, "tail-amplification.svg"), W, H, *frags)


def fig_distribution_comparison():
    """Порівняння симетричного нормального розподілу та реального системного розподілу з важким хвостом."""
    W, H = 820, 480
    left = 80
    right = 770
    top = 60
    bottom = 400
    plot_w = right - left
    plot_h = bottom - top

    frags = []

    frags.append(arrow(left, bottom, right + 20, bottom, color=INK, sw=1.8))
    frags.append(arrow(left, bottom, left, top - 20, color=INK, sw=1.8))

    frags.append(text(right - 20, bottom + 25, "Час відгуку (мс)", size=12, color=INK, bold=True, anchor="middle"))
    frags.append(text(left - 10, top - 26, "Густина ймовірності p(x)", size=12, color=INK, bold=True, anchor="end"))

    def gauss_pdf(x):
        mu = 50.0
        sigma = 18.0
        return (1.0 / (sigma * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x - mu) / sigma) ** 2)

    def system_pdf(x):
        if x <= 2:
            return 0.0
        z1 = (math.log(x) - math.log(18)) / 0.45
        p1 = (1.0 / (x * 0.45 * math.sqrt(2 * math.pi))) * math.exp(-0.5 * z1 * z1)
        z2 = (math.log(x) - math.log(90)) / 0.8
        p2 = (1.0 / (x * 0.8 * math.sqrt(2 * math.pi))) * math.exp(-0.5 * z2 * z2)
        return 0.75 * p1 + 0.25 * p2

    x_max = 200.0
    steps = 200

    pts_gauss = []
    pts_system = []

    max_val = 0.040

    for i in range(steps + 1):
        x_val = i * (x_max / steps)
        g_val = gauss_pdf(x_val)
        s_val = system_pdf(x_val)

        px = left + (x_val / x_max) * plot_w
        py_g = bottom - (g_val / max_val) * plot_h
        py_s = bottom - (s_val / max_val) * plot_h

        pts_gauss.append(f"{px:.1f},{py_g:.1f}")
        pts_system.append(f"{px:.1f},{py_s:.1f}")

    frags.append(f'<polyline points="{" ".join(pts_gauss)}" stroke="#94a3b8" stroke-width="2.2" stroke-dasharray="5,4" fill="none"/>')

    # Системний розподіл із заповненням
    poly_pts = [f"{left:.1f},{bottom:.1f}"] + pts_system + [f"{right:.1f},{bottom:.1f}"]
    frags.append(f'<polygon points="{" ".join(poly_pts)}" fill="#eff6ff" stroke="none"/>')
    frags.append(f'<polyline points="{" ".join(pts_system)}" stroke="#2563eb" stroke-width="2.8" fill="none"/>')

    markers = [
        (20.0, "Медіана p50\n(20 мс)", "#16a34a", 0.032),
        (42.0, "Середнє Mean\n(42 мс)", "#ea580c", 0.018),
        (165.0, "Хвіст p99\n(165 мс)", "#dc2626", 0.003)
    ]

    for m_x, m_label, m_color, m_prob in markers:
        mx = left + (m_x / x_max) * plot_w
        my = bottom - (m_prob / max_val) * plot_h
        frags.append(line(mx, bottom, mx, top + 30, color=m_color, sw=1.6, dash="4,3"))
        frags.append(circle(mx, my, 5, fill=m_color, stroke=BG, sw=1.5))
        
        lines = m_label.split("\n")
        frags.append(text(mx, top + 15, lines[0], size=11, color=m_color, bold=True, anchor="middle"))
        frags.append(text(mx, top + 28, lines[1], size=10, color=m_color, anchor="middle"))

    leg_box, _, _ = textbox(
        570, 130,
        "Порівняння моделей:\n"
        "╌╌ Нормальний розподіл (Гаусс): симетричний,\n"
        "    хвости швидко зникають (правило 3σ).\n"
        "──  Реальний системний розподіл: сильна асиметрія,\n"
        "    середнє (Mean) зсунуте праворуч від медіани,\n"
        "    а p99 лежить глибоко у важкому хвості.",
        size=11, color=INK, fill="#f8fafc", stroke=MUTED, rx=4, pad=10
    )
    frags.append(leg_box)

    render(os.path.join(OUT, "distribution-comparison.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_percentile_cdf()
    fig_tail_amplification()
    fig_distribution_comparison()
    print("Figures generated successfully in img/")
