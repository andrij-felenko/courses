# -*- coding: utf-8 -*-
import sys, os, math

# Import svgkit from scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Palette ────────────────────────────────────────────────────────────────
WAVE_INC = "#2457d6"    # падаюча хвиля V+ (синій)
WAVE_REF = "#c0392b"    # відбита хвиля V- (червоний)
WAVE_TOT = "#8e44ad"    # сумарна стояча хвиля / обвідна (фіолетовий)
GND_COL  = "#444a52"    # земля
BOX_BG   = "#f8f9fa"    # фон блоків
ACCENT   = "#27ae60"    # зелений акцент / узгодження


def fig_vswr_and_s11_physics():
    """Фігура 1: Фізика відбиття сигналу, формування стоячої хвилі та зв'язок між Gamma, VSWR і S11."""
    W, H = 840, 500
    p = []

    # Заголовок
    p.append(text(W / 2, 28, "Хвильовий процес у неузгодженому тракті: відбиття, КСХ та зворотні втрати", size=15, bold=True, color=INK))

    # 1. Схема тракту (верхня частина)
    gy = 80
    # Джерело / Генератор
    p.append(rect(40, gy, 120, 60, fill="#eaf2f8", stroke=WAVE_INC, sw=1.5, rx=5))
    p.append(text(100, gy + 26, "ВЧ-генератор", size=11, bold=True, color=WAVE_INC))
    p.append(text(100, gy + 44, "Z_src = 50 Ω", size=10, color=INK))

    # Лінія передачі
    lx0, lx1 = 160, 640
    p.append(line(lx0, gy + 15, lx1, gy + 15, color=INK, sw=2.0))
    p.append(line(lx0, gy + 45, lx1, gy + 45, color=GND_COL, sw=2.0))
    p.append(text((lx0 + lx1) / 2, gy + 8, "Сигнальний провідник / Мікросмужка (Z₀ = 50 Ω)", size=11, color=INK, bold=True))
    p.append(text((lx0 + lx1) / 2, gy + 58, "Опорна земля (Ground Plane)", size=10, color=MUTED))

    # Навантаження (Антена Z_L)
    p.append(rect(lx1, gy, 140, 60, fill="#fdecea", stroke=WAVE_REF, sw=1.5, rx=5))
    p.append(text(lx1 + 70, gy + 24, "Антена (Z_L ≠ Z₀)", size=11, bold=True, color=WAVE_REF))
    p.append(text(lx1 + 70, gy + 44, "Z_L = R_A + jX_A", size=10.5, color=INK))

    # Стрілки хвиль у лінії
    p.append(arrow(210, gy + 23, 350, gy + 23, color=WAVE_INC, sw=2.0))
    p.append(text(280, gy + 36, "Падаюча хвиля V⁺", size=10, bold=True, color=WAVE_INC))

    p.append(arrow(590, gy + 37, 450, gy + 37, color=WAVE_REF, sw=2.0))
    p.append(text(520, gy + 27, "Відбита хвиля V⁻ = Γ · V⁺", size=10, bold=True, color=WAVE_REF))

    # Коефіцієнт відбиття на межі
    b, _, _ = textbox(lx1 - 10, gy - 26, "Межа розділу (Порт антени)\nΓ = (Z_L − Z₀) / (Z_L + Z₀)", size=10, pad=6, fill="#ffffff", stroke=WAVE_REF, sw=1.2)
    p.append(b)

    # 2. Графік стоячої хвилі вздовж лінії (середня частина)
    plot_y0 = 265
    plot_x0 = 120
    plot_w = 600
    plot_h = 100

    p.append(text(W / 2, plot_y0 - 55, "Розподіл амплітуди напруги вздовж лінії передачі: утворення стоячої хвилі", size=12, bold=True, color=INK))

    # Вісь X та Y
    p.append(line(plot_x0, plot_y0 + plot_h / 2, plot_x0 + plot_w, plot_y0 + plot_h / 2, color="#bdc3c7", sw=1.0, dash="4,4"))
    p.append(line(plot_x0, plot_y0 - 45, plot_x0, plot_y0 + plot_h + 15, color=INK, sw=1.5))
    p.append(line(plot_x0 + plot_w, plot_y0 - 45, plot_x0 + plot_w, plot_y0 + plot_h + 15, color=WAVE_REF, sw=1.5, dash="3,3"))
    p.append(text(plot_x0 - 15, plot_y0 - 35, "|V(x)|", size=11, bold=True, color=INK, anchor="end"))
    p.append(text(plot_x0 + plot_w + 10, plot_y0 - 35, "x = 0 (Антена)", size=10.5, bold=True, color=WAVE_REF, anchor="start"))
    p.append(text(plot_x0, plot_y0 + plot_h + 28, "Генератор (x = −l)", size=10, color=MUTED, anchor="middle"))

    # Обвідна стоячої хвилі
    points_max = []
    points_min = []
    num_pts = 100
    wavelength_px = plot_w / 2.5
    beta = 2 * math.pi / wavelength_px
    gamma_mag = 0.5
    v_plus = 35.0

    for i in range(num_pts + 1):
        x = plot_x0 + plot_w - (i * plot_w / num_pts)
        dist = (plot_x0 + plot_w) - x
        phase = 2 * beta * dist
        env_val = v_plus * math.sqrt(1 + gamma_mag**2 + 2 * gamma_mag * math.cos(phase))
        
        y_top = plot_y0 + plot_h / 2 - env_val
        y_bot = plot_y0 + plot_h / 2 + env_val
        points_max.append((x, y_top))
        points_min.append((x, y_bot))

    d_max = "M " + " ".join(f"{x:.1f},{y:.1f}" for x, y in points_max)
    d_min = "M " + " ".join(f"{x:.1f},{y:.1f}" for x, y in points_min)
    p.append(f'<path d="{d_max}" fill="none" stroke="{WAVE_TOT}" stroke-width="2.2"/>')
    p.append(f'<path d="{d_min}" fill="none" stroke="{WAVE_TOT}" stroke-width="1.4" stroke-dasharray="3,3"/>')

    # Миттєва хвиля
    wave_pts = []
    for i in range(num_pts * 2 + 1):
        x = plot_x0 + plot_w - (i * plot_w / (num_pts * 2))
        dist = (plot_x0 + plot_w) - x
        val = v_plus * (math.cos(-beta * dist) + gamma_mag * math.cos(beta * dist))
        y = plot_y0 + plot_h / 2 - val
        wave_pts.append((x, y))
    d_wave = "M " + " ".join(f"{x:.1f},{y:.1f}" for x, y in wave_pts)
    p.append(f'<path d="{d_wave}" fill="none" stroke="{WAVE_INC}" stroke-width="1.0" opacity="0.6"/>')

    # Позначення V_max та V_min
    x_vmax = plot_x0 + plot_w - (wavelength_px / 2)
    y_vmax = plot_y0 + plot_h / 2 - v_plus * (1 + gamma_mag)
    p.append(circle(x_vmax, y_vmax, 3.5, fill=WAVE_REF, stroke=WAVE_REF))
    b, _, _ = textbox(x_vmax + 75, y_vmax - 18, "V_max = |V⁺| (1 + |Γ|)", size=10, pad=4, fill="#ffffff", stroke=WAVE_REF, sw=1.0)
    p.append(b)

    x_vmin = plot_x0 + plot_w - (wavelength_px / 4)
    y_vmin = plot_y0 + plot_h / 2 - v_plus * (1 - gamma_mag)
    p.append(circle(x_vmin, y_vmin, 3.5, fill=WAVE_INC, stroke=WAVE_INC))
    b, _, _ = textbox(x_vmin + 75, y_vmin - 14, "V_min = |V⁺| (1 − |Γ|)", size=10, pad=4, fill="#ffffff", stroke=WAVE_INC, sw=1.0)
    p.append(b)

    # Позначення періоду стоячої хвилі
    p.append(line(x_vmin, plot_y0 + plot_h + 10, x_vmax, plot_y0 + plot_h + 10, color=MUTED, sw=1.2))
    p.append(line(x_vmin, plot_y0 + plot_h + 6, x_vmin, plot_y0 + plot_h + 14, color=MUTED, sw=1.2))
    p.append(line(x_vmax, plot_y0 + plot_h + 6, x_vmax, plot_y0 + plot_h + 14, color=MUTED, sw=1.2))
    p.append(text((x_vmin + x_vmax) / 2, plot_y0 + plot_h + 24, "Δx = λ / 2", size=10, color=MUTED))

    # 3. Інженерний блок взаємозв'язку метрик
    by = 445
    box_w = 235
    box_h = 50

    p.append(rect(45, by - 25, box_w, box_h, fill="#fdfefe", stroke=INK, sw=1.2, rx=5))
    p.append(text(45 + box_w / 2, by - 9, "КСХ (VSWR)", size=11, bold=True, color=INK))
    p.append(text(45 + box_w / 2, by + 11, "VSWR = V_max / V_min = (1 + |Γ|) / (1 − |Γ|)", size=9.5, color=MUTED))

    p.append(rect(300, by - 25, box_w, box_h, fill="#fdfefe", stroke=INK, sw=1.2, rx=5))
    p.append(text(300 + box_w / 2, by - 9, "Зворотні втрати (Return Loss)", size=11, bold=True, color=INK))
    p.append(text(300 + box_w / 2, by + 11, "RL = −20 log₁₀|Γ| [дБ] = −|S₁₁| [дБ]", size=9.5, color=MUTED))

    p.append(rect(555, by - 25, box_w, box_h, fill="#eafaf1", stroke=ACCENT, sw=1.2, rx=5))
    p.append(text(555 + box_w / 2, by - 9, "Потужність у навантаженні", size=11, bold=True, color=ACCENT))
    p.append(text(555 + box_w / 2, by + 11, "P_load / P_inc = 1 − |Γ|² = 1 − 10^(−RL/10)", size=9.5, color=INK))

    render(os.path.join(OUT, "vswr-and-s11-reflection-physics.svg"), W, H, *p)


def fig_smith_chart_matching():
    """Фігура 2: Діаграма Сміта з траєкторією узгодження імпедансу антени L/Pi-ланцюгом."""
    W, H = 840, 520
    p = []

    p.append(text(W / 2, 28, "Діаграма Сміта: комплексна площина імпедансу та траєкторія узгодження", size=15, bold=True, color=INK))

    cx = 265
    cy = 270
    R = 180.0

    # 1. Сміт-діаграма: фон та сітка
    p.append(circle(cx, cy, R, fill="#fafbfc", stroke=INK, sw=2.0))
    p.append(line(cx - R, cy, cx + R, cy, color=INK, sw=1.5))

    def draw_r_circle(r_val, col="#bdc3c7", sw=1.0):
        cen_x = cx + (r_val / (r_val + 1.0)) * R
        rad = R / (r_val + 1.0)
        p.append(circle(cen_x, cy, rad, fill="none", stroke=col, sw=sw))

    def draw_x_arc(x_val, col="#bdc3c7", sw=1.0):
        gx = (x_val**2 - 1.0) / (x_val**2 + 1.0)
        gy = 2.0 * x_val / (x_val**2 + 1.0)
        x_rim = cx + gx * R
        y_rim = cy - gy * R
        rad = R / abs(x_val)
        sweep = 0 if x_val > 0 else 1
        p.append(f'<path d="M {x_rim:.1f} {y_rim:.1f} A {rad:.1f} {rad:.1f} 0 0 {sweep} {cx + R:.1f} {cy:.1f}" fill="none" stroke="{col}" stroke-width="{sw}"/>')

    for r_val in [0.2, 0.5, 2.0, 5.0]:
        draw_r_circle(r_val, col="#d0d7de", sw=0.9)
    draw_r_circle(1.0, col=ACCENT, sw=1.5)

    for x_val in [0.5, 1.0, 2.0, -0.5, -1.0, -2.0]:
        draw_x_arc(x_val, col="#d0d7de", sw=0.9)

    p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R * 0.5:.1f}" fill="none" stroke="{WAVE_INC}" stroke-width="1.2" stroke-dasharray="4,4"/>')

    # 2. Координати точок та дуги трансформацій (малюємо ДО текстових блоків)
    gamma_x = -0.255 * R
    gamma_y = 0.556 * R
    p1_x = cx + gamma_x
    p1_y = cy + gamma_y

    p2_x = cx - 0.146 * R
    p2_y = cy - 0.463 * R

    # Дуга трансформації 1: Послідовна індуктивність L_series
    p.append(f'<path d="M {p1_x:.1f} {p1_y:.1f} A {R/1.4:.1f} {R/1.4:.1f} 0 0 1 {p2_x:.1f} {p2_y:.1f}" fill="none" stroke="#e74c3c" stroke-width="3.0"/>')

    # Дуга трансформації 2: Паралельна ємність C_shunt
    p.append(f'<path d="M {p2_x:.1f} {p2_y:.1f} A {R/2.0:.1f} {R/2.0:.1f} 0 0 1 {cx:.1f} {cy:.1f}" fill="none" stroke="{ACCENT}" stroke-width="3.0"/>')

    # 3. Маркери та текстові блоки поверх сітки та ліній
    b, _, _ = textbox(cx - R - 35, cy, "Short\n(0 Ω)", size=10, pad=4, fill="#ffffff", stroke=WAVE_REF, sw=1.0)
    p.append(b)
    b, _, _ = textbox(cx + R + 35, cy, "Open\n(∞ Ω)", size=10, pad=4, fill="#ffffff", stroke=INK, sw=1.0)
    p.append(b)

    # Підписи областей
    b, _, _ = textbox(cx - 50, cy - R + 35, "+jX (Індуктивна реактивність)", size=10, pad=3, fill="#ffffff", stroke="#2980b9", sw=1.0)
    p.append(b)
    b, _, _ = textbox(cx - 50, cy + R - 35, "−jX (Ємнісна реактивність)", size=10, pad=3, fill="#ffffff", stroke="#e67e22", sw=1.0)
    p.append(b)

    # Точка 1 (Start / Antenna)
    p.append(circle(p1_x, p1_y, 5.0, fill=WAVE_REF, stroke=INK, sw=1.5))
    b, _, _ = textbox(p1_x - 65, p1_y + 24, "A: Неузгоджена антена\nZ_A = 20 − j45 Ω", size=10, pad=4, fill="#ffffff", stroke=WAVE_REF, sw=1.1)
    p.append(b)

    # Точка 2 (Intermediate)
    p.append(circle(p2_x, p2_y, 4.5, fill="#e67e22", stroke=INK, sw=1.5))
    b, _, _ = textbox(p2_x - 70, p2_y - 20, "B: + Послідовна індуктивність L\n(рух вгору по колу r = const)", size=9.5, pad=4, fill="#ffffff", stroke="#e67e22", sw=1.1)
    p.append(b)

    # Точка 3 (Центр 50 Ом)
    p.append(circle(cx, cy, 6.0, fill=ACCENT, stroke=INK, sw=1.5))
    b, _, _ = textbox(cx + 90, cy + 28, "C: + Паралельна ємність C\n→ Центр 50 Ω (Γ = 0)", size=10, pad=4, fill="#ffffff", stroke=ACCENT, sw=1.1)
    p.append(b)

    # Права панель: Електрична схема та правила трансформації
    px0 = 540
    p.append(rect(px0, 65, 285, 440, fill=BOX_BG, stroke=INK, sw=1.2, rx=6))

    p.append(text(px0 + 142, 90, "Топологія узгодження (L-Network)", size=12, bold=True, color=INK))

    # Схема L-ланцюга
    sy = 145
    p.append(line(px0 + 20, sy, px0 + 65, sy, color=INK, sw=1.8))
    p.append(text(px0 + 40, sy - 10, "RF In (50 Ω)", size=9.5, bold=True, color=ACCENT))

    # Котушка L (послідовна)
    for k in range(3):
        p.append(f'<path d="M {px0+65+k*14:.1f} {sy:.1f} q 7 -14 14 0" fill="none" stroke="#e74c3c" stroke-width="2.2"/>')
    p.append(text(px0 + 86, sy - 14, "L_series", size=10, bold=True, color="#e74c3c"))

    # Вузол після котушки
    p.append(line(px0 + 107, sy, px0 + 175, sy, color=INK, sw=1.8))
    p.append(circle(px0 + 140, sy, 3.0, fill=INK, stroke=INK))

    # Шунтовий конденсатор C
    p.append(line(px0 + 140, sy, px0 + 140, sy + 25, color=INK, sw=1.8))
    p.append(line(px0 + 128, sy + 25, px0 + 152, sy + 25, color=ACCENT, sw=2.2))
    p.append(line(px0 + 128, sy + 32, px0 + 152, sy + 32, color=ACCENT, sw=2.2))
    p.append(line(px0 + 140, sy + 32, px0 + 140, sy + 55, color=INK, sw=1.8))
    # Земля
    p.append(line(px0 + 125, sy + 55, px0 + 155, sy + 55, color=GND_COL, sw=2.0))
    p.append(line(px0 + 130, sy + 59, px0 + 150, sy + 59, color=GND_COL, sw=1.5))
    p.append(line(px0 + 136, sy + 63, px0 + 144, sy + 63, color=GND_COL, sw=1.2))
    p.append(text(px0 + 180, sy + 30, "C_shunt", size=10, bold=True, color=ACCENT))

    # Вихід на антену
    p.append(rect(px0 + 175, sy - 18, 85, 36, fill="#fdecea", stroke=WAVE_REF, sw=1.2, rx=4))
    p.append(text(px0 + 217, sy + 4, "Антена Z_A", size=10, bold=True, color=WAVE_REF))

    # Довідкова таблиця напрямків на діаграмі
    ty = 250
    p.append(line(px0 + 15, ty - 12, px0 + 270, ty - 12, color="#d0d7de", sw=1.0))
    p.append(text(px0 + 142, ty + 5, "Напрямки переміщення на Сміті:", size=11, bold=True, color=INK))

    rules = [
        ("Послідовна L (+jX)", "По колу r = const за год. стрілкою", "#e74c3c"),
        ("Послідовна C (−jX)", "По колу r = const проти год. стрілки", "#3498db"),
        ("Паралельна L (−jB)", "По колу g = const проти год. стрілки", "#9b59b6"),
        ("Паралельна C (+jB)", "По колу g = const за год. стрілкою", ACCENT),
        ("Відрізок лінії (Z₀)", "Коло довкола центру за год. стрілкою", MUTED)
    ]

    for idx, (elem, action, col) in enumerate(rules):
        row_y = ty + 30 + idx * 36
        p.append(rect(px0 + 14, row_y - 10, 6, 20, fill=col, stroke="none", rx=1))
        p.append(text(px0 + 28, row_y, elem, size=10, bold=True, color=INK, anchor="start"))
        p.append(text(px0 + 28, row_y + 13, action, size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "smith-chart-matching-network.svg"), W, H, *p)


if __name__ == "__main__":
    fig_vswr_and_s11_physics()
    fig_smith_chart_matching()
    print("Figures generated successfully.")
