# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Макростан і мікростани: незворотне розширення газу в об'ємі
# ════════════════════════════════════════════════════════════════════════════
def fig_microstates_box():
    W, H = 820, 400
    f = []

    # Тло розділювач між початковим та кінцевим станом
    f.append(line(410, 20, 410, 380, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва частина: Початковий макростан A (Газ стиснутий у лівій половині) ──
    f.append(text(205, 40, "Початковий стан A (Нерівноважний)", size=14, bold=True, color=INK))
    f.append(text(205, 60, "Перегородка закрита: об'єм V_1 = V / 2", size=12, color=MUTED))

    # Контур коробки
    f.append(rect(40, 90, 330, 220, fill="#f8f9fa", stroke=DARK, sw=2))
    # Перегородка
    f.append(line(205, 90, 205, 310, color="#c0392b", sw=3.5))
    f.append(text(205, 328, "Закрита перегородка", size=11, color="#c0392b", bold=True))

    # Газові частинки у лівій половині (12 частинок)
    particles_left = [
        (75, 120), (120, 150), (160, 110), (90, 200), (140, 190), (180, 170),
        (65, 250), (115, 270), (160, 240), (100, 290), (150, 220), (80, 160)
    ]
    for px, py in particles_left:
        f.append(circle(px, py, 6, fill="#2980b9", stroke="#1b4f72", sw=1.5))
        # Маленький вектор швидкості
        vx = (px * 17) % 15 - 7
        vy = (py * 13) % 15 - 7
        f.append(line(px, py, px + vx, py + vy, color="#2980b9", sw=1.2))

    f.append(text(122, 108, "N частинок у V_1", size=11, bold=True, color="#2980b9"))
    f.append(text(287, 200, "Порожнеча (V_2)", size=11, color=MUTED))

    f.append(text(205, 360, "Число мікростанів W_A = (V_1)^N", size=12, bold=True, color=INK))

    # ── Права частина: Кінцевий макростан B (Рівноважне розширення) ──
    f.append(text(615, 40, "Кінцевий стан B (Рівновага)", size=14, bold=True, color=INK))
    f.append(text(615, 60, "Перегородка відкрита: об'єм V_2 = V", size=12, color=MUTED))

    # Контур коробки
    f.append(rect(450, 90, 330, 220, fill="#f8f9fa", stroke=DARK, sw=2))
    # Пунктир колишньої перегородки
    f.append(line(615, 90, 615, 310, color=MUTED, sw=1.5, dash="3 3"))
    f.append(text(615, 328, "Перегородку знято", size=11, color="#27ae60", bold=True))

    # Рівномірно розподілені частинки (24 частинки по всьому об'єму)
    particles_all = [
        (475, 120), (520, 150), (560, 110), (490, 200), (540, 190), (580, 170),
        (465, 250), (515, 270), (560, 240), (500, 290), (550, 220), (480, 160),
        (645, 130), (690, 160), (730, 120), (660, 210), (710, 195), (750, 180),
        (635, 260), (685, 280), (730, 245), (670, 295), (720, 225), (650, 165)
    ]
    for px, py in particles_all:
        f.append(circle(px, py, 6, fill="#27ae60", stroke="#1e8449", sw=1.5))
        vx = (px * 19) % 15 - 7
        vy = (py * 11) % 15 - 7
        f.append(line(px, py, px + vx, py + vy, color="#27ae60", sw=1.2))

    f.append(text(615, 360, "W_B = (V_2)^N >> W_A   ⇒   ΔS = k_B ln(W_B / W_A) > 0", size=12, bold=True, color="#27ae60"))

    render(os.path.join(OUT, "fig1-microstates-box.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Гострота максимуму ймовірності макростану при збільшенні N
# ════════════════════════════════════════════════════════════════════════════
def fig_gaussian_probability_peak():
    W, H = 780, 420
    f = []

    # Осі координат
    ox, oy = 80, 340
    f.append(line(ox, oy, 720, oy, color=DARK, sw=1.5)) # k / N (частка частинок ліворуч)
    f.append(line(ox, oy, ox, 40, color=DARK, sw=1.5))  # W(k) / W_max (відносна ймовірність)

    # Стрілки
    f.append(polygon([(720, oy - 4), (730, oy), (720, oy + 4)], fill=DARK))
    f.append(polygon([(ox - 4, 40), (ox, 30), (ox + 4, 40)], fill=DARK))

    f.append(text(710, oy + 25, "Частка частинок ліворуч x = k / N", size=12, bold=True, color=DARK))
    f.append(text(35, 30, "Ймовірність макростану P(x)", size=12, bold=True, color=DARK))

    # Позначки на осі x
    f.append(line(ox, oy, ox, oy + 6, color=DARK, sw=1.5))
    f.append(text(ox, oy + 20, "0.0", size=11, color=MUTED))

    f.append(line(400, oy, 400, oy + 6, color=DARK, sw=1.5))
    f.append(text(400, oy + 20, "0.5 (Рівновага)", size=11, bold=True, color=DARK))
    f.append(line(400, 40, 400, oy - 2, color=MUTED, sw=1, dash="3 3"))

    f.append(line(720, oy, 720, oy + 6, color=DARK, sw=1.5))
    f.append(text(720, oy + 20, "1.0", size=11, color=MUTED))

    # Гаусові піки для різних N
    # Curve 1: N = 20 (широка крива)
    path_n20 = "M 80 335 C 180 335 280 310 340 220 C 370 160 390 70 400 70 C 410 70 430 160 460 220 C 520 310 620 335 720 335"
    f.append(svg_path(path_n20, stroke="#e67e22", sw=2.5, fill="none"))
    f.append(text(240, 270, "N = 20 (широкі флуктуації)", size=11, bold=True, color="#e67e22"))

    # Curve 2: N = 200 (середня крива)
    path_n200 = "M 80 339 C 280 339 340 330 370 230 C 388 150 396 60 400 50 C 404 50 412 150 430 230 C 460 330 520 339 720 339"
    f.append(svg_path(path_n200, stroke="#2980b9", sw=2.5, fill="none"))
    f.append(text(285, 170, "N = 200", size=11, bold=True, color="#2980b9"))

    # Curve 3: N = 10^23 (дельта-подібна голка)
    f.append(line(400, oy, 400, 45, color="#c0392b", sw=3))
    f.append(circle(400, 45, 4, fill="#c0392b", stroke="#7b241c", sw=1.5))
    f.append(text(412, 55, "N ≈ 10²³ (Δx ≈ 10⁻¹²)", size=11, bold=True, color="#c0392b"))

    # Пояснювальний блок
    f.append(rect(480, 100, 220, 110, fill="#fcf3cf", stroke="#f39c12", sw=1.5))
    f.append(text(590, 120, "Відносна ширина піку:", size=11, bold=True, color=DARK))
    f.append(text(590, 142, "σ / N = 1 / (2 √N)", size=12, bold=True, color="#c0392b"))
    f.append(text(590, 168, "При N → ∞ флуктуації", size=10.5, color=MUTED))
    f.append(text(590, 186, "прямують до 0 (термодинамічна межа)", size=10.5, color=MUTED))

    render(os.path.join(OUT, "fig2-gaussian-probability-peak.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Розподіл Максвелла-Больцмана по енергетичних рівнях
# ════════════════════════════════════════════════════════════════════════════
def fig_stirling_maxwell_boltzmann():
    W, H = 800, 420
    f = []

    # Осі координат
    ox, oy = 90, 340
    f.append(line(ox, oy, 740, oy, color=DARK, sw=1.5)) # Енергія E_i
    f.append(line(ox, oy, ox, 40, color=DARK, sw=1.5))  # Число частинок N_i

    # Стрілки
    f.append(polygon([(740, oy - 4), (750, oy), (740, oy + 4)], fill=DARK))
    f.append(polygon([(ox - 4, 40), (ox, 30), (ox + 4, 40)], fill=DARK))

    f.append(text(730, oy + 25, "Енергія рівня E_i", size=12, bold=True, color=DARK))
    f.append(text(35, 30, "Заселеність N_i", size=12, bold=True, color=DARK))

    # Дискретні енергетичні рівні та гістограма заселеності N_i
    levels = [
        (130, 270, "E_0 = 0", 270),
        (230, 205, "E_1", 205),
        (330, 155, "E_2", 155),
        (430, 118, "E_3", 118),
        (530, 90, "E_4", 90),
        (630, 68, "E_5", 68)
    ]

    for lx, height, label_e, y_top in levels:
        bar_w = 40
        x_left = lx - bar_w / 2
        bar_h = oy - y_top
        f.append(rect(x_left, y_top, bar_w, bar_h, fill="#d6eaf8", stroke="#2980b9", sw=1.5))
        f.append(circle(lx, y_top, 4, fill="#2980b9", stroke="#1b4f72", sw=1))
        f.append(text(lx, oy + 18, label_e, size=11, color=DARK))

    # Експоненціальна крива Больцмана
    boltzmann_exp = "M 90 45 C 110 250 180 270 230 205 C 280 150 380 115 530 90 C 620 75 680 65 730 58"
    f.append(svg_path(boltzmann_exp, stroke="#c0392b", sw=2.5, fill="none"))

    f.append(text(460, 50, "N_i = N_0 · exp(-E_i / (k_B T))", size=13, bold=True, color="#c0392b"))

    # Позначення фактора Больцмана
    f.append(rect(165, 70, 215, 95, fill="#eaafaf", stroke="#c0392b", sw=1.5))
    f.append(text(272, 90, "Фактор Больцмана:", size=11, bold=True, color="#7b241c"))
    f.append(text(272, 110, "exp(-ΔE / (k_B T))", size=12.5, bold=True, color="#c0392b"))
    f.append(text(272, 132, "Виникає з максимізації W", size=10, color=DARK))
    f.append(text(272, 148, "при фіксованій енергії E", size=10, color=DARK))

    render(os.path.join(OUT, "fig3-stirling-maxwell-boltzmann.svg"), W, H, *f)

if __name__ == '__main__':
    fig_microstates_box()
    fig_gaussian_probability_peak()
    fig_stirling_maxwell_boltzmann()
    print("Figures generated successfully.")
