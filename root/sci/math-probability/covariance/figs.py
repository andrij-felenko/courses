# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Чотири квадранти коваріації ─────────────────────────────────────
# Показує площину відхилень навколо (μ_X, μ_Y).
# Квадранти I і III дають додатні добутки (+), квадранти II і IV — від'ємні (−).
# Хмара точок з позитивним зв'язком концентрується в I і III квадрантах.
def fig_covariance_quadrants():
    W, H = 680, 420
    cx, cy = 340, 220
    pw, ph = 260, 160  # напівширина й напіввисота поля графіка

    p = []

    # Фонова розмітка квадрантів
    # Квадрант I (вгорі праворуч): (+) * (+) = +
    p.append(rect(cx, cy - ph, pw, ph, fill="#edf7ee", stroke="none", rx=0))
    # Квадрант III (внизу ліворуч): (−) * (−) = +
    p.append(rect(cx - pw, cy, pw, ph, fill="#edf7ee", stroke="none", rx=0))
    # Квадрант II (вгорі ліворуч): (−) * (+) = −
    p.append(rect(cx - pw, cy - ph, pw, ph, fill="#eef3fd", stroke="none", rx=0))
    # Квадрант IV (внизу праворуч): (+) * (−) = −
    p.append(rect(cx, cy, pw, ph, fill="#eef3fd", stroke="none", rx=0))

    # Рамка графіка
    p.append(rect(cx - pw, cy - ph, 2 * pw, 2 * ph, fill="none", stroke="#d0d7de", sw=1.2, rx=4))

    # Осі середніх μ_X та μ_Y (пунктир)
    p.append(line(cx - pw, cy, cx + pw, cy, color=LINE, sw=1.5, dash="5 4"))
    p.append(line(cx, cy - ph, cx, cy + ph, color=LINE, sw=1.5, dash="5 4"))

    # Стрілки осей координат X та Y
    p.append(line(cx - pw - 20, cy + ph + 10, cx + pw + 25, cy + ph + 10, color=MUTED, sw=1.3))
    p.append(arrow(cx + pw + 10, cy + ph + 10, cx + pw + 26, cy + ph + 10, color=MUTED, sw=1.3))
    p.append(text(cx + pw + 32, cy + ph + 14, "X", 13, MUTED, "start", bold=True))

    p.append(line(cx - pw - 10, cy + ph + 20, cx - pw - 10, cy - ph - 25, color=MUTED, sw=1.3))
    p.append(arrow(cx - pw - 10, cy - ph - 10, cx - pw - 10, cy - ph - 26, color=MUTED, sw=1.3))
    p.append(text(cx - pw - 10, cy - ph - 30, "Y", 13, MUTED, "middle", bold=True))

    # Підписи середніх
    p.append(text(cx, cy + ph + 26, "μ_X (середнє X)", 12, INK, "middle", bold=True))
    p.append(text(cx - pw - 22, cy + 4, "μ_Y", 12, INK, "end", bold=True))

    # Позначки квадрантів та знаку добутку
    p.append(text(cx + pw * 0.52, cy - ph * 0.75, "Квадрант I", 12, FIELD, "middle", bold=True))
    p.append(text(cx + pw * 0.52, cy - ph * 0.55, "(X − μ_X) > 0,  (Y − μ_Y) > 0", 11, FIELD, "middle"))
    p.append(text(cx + pw * 0.52, cy - ph * 0.35, "добуток (+)", 12, FIELD, "middle", bold=True))

    p.append(text(cx - pw * 0.52, cy + ph * 0.35, "Квадрант III", 12, FIELD, "middle", bold=True))
    p.append(text(cx - pw * 0.52, cy + ph * 0.55, "(X − μ_X) < 0,  (Y − μ_Y) < 0", 11, FIELD, "middle"))
    p.append(text(cx - pw * 0.52, cy + ph * 0.75, "добуток (+)", 12, FIELD, "middle", bold=True))

    p.append(text(cx - pw * 0.52, cy - ph * 0.75, "Квадрант II", 12, NEG, "middle", bold=True))
    p.append(text(cx - pw * 0.52, cy - ph * 0.55, "(X − μ_X) < 0,  (Y − μ_Y) > 0", 11, NEG, "middle"))
    p.append(text(cx - pw * 0.52, cy - ph * 0.35, "добуток (−)", 12, NEG, "middle", bold=True))

    p.append(text(cx + pw * 0.52, cy + ph * 0.35, "Квадрант IV", 12, NEG, "middle", bold=True))
    p.append(text(cx + pw * 0.52, cy + ph * 0.55, "(X − μ_X) > 0,  (Y − μ_Y) < 0", 11, NEG, "middle"))
    p.append(text(cx + pw * 0.52, cy + ph * 0.75, "добуток (−)", 12, NEG, "middle", bold=True))

    # Хмара точок з позитивною коваріацією (витягнута вздовж діагоналі)
    pts = [
        (-210, -120), (-180, -100), (-160, -115), (-150, -80), (-130, -65),
        (-110, -75), (-90, -40), (-70, -55), (-60, -25), (-40, -15),
        (-30, 20), (-15, -30), (10, -15), (20, 25), (45, 10),
        (60, 45), (75, 30), (90, 70), (110, 50), (130, 85),
        (150, 75), (170, 110), (190, 95), (210, 130), (-80, 15),
        (70, -20)  # пара точок у квадрантах II/IV для реалістичного розкиду
    ]
    for dx, dy in pts:
        px = cx + dx
        py = cy - dy  # екранна координата Y росте вниз
        col = POS if (dx * dy > 0) else NEG
        p.append(circle(px, py, 4.5, fill=col, stroke=INK, sw=1.0))

    p.append(text(W / 2, H - 8,
                  "Коваріація усереднює добутки відхилень: при прямому зв'язку переважають плюси I і III квадрантів.",
                  11, MUTED, "middle"))

    render(os.path.join(OUT, "covariance-quadrants.svg"), W, H, *p,
           title="Квадранти площини відхилень: формування знака коваріації")


# ── Фігура 2: Патерни кореляції Пірсона ─────────────────────────────────────────
# Порівняння 5 типів взаємозв'язку:
# ρ = +1.0, ρ = +0.8, ρ = 0.0 (шум), ρ = -0.8, ρ = 0.0 (нелінійний параболічний зв'язок)
def fig_correlation_patterns():
    W, H = 820, 260
    panels = [
        ("ρ = +1.0", "строга лінія", "line_pos"),
        ("ρ = +0.8", "сильний прямий", "cloud_pos"),
        ("ρ = 0.0", "некорельованість", "noise"),
        ("ρ = −0.8", "сильний зворотний", "cloud_neg"),
        ("ρ = 0.0", "нелінійний зв'язок", "parabola")
    ]
    pw, ph = 140, 140
    gap = 20
    start_x = 30
    top_y = 60

    p = []

    for i, (title_text, subtitle, mode) in enumerate(panels):
        bx = start_x + i * (pw + gap)
        by = top_y
        bcx = bx + pw / 2
        bcy = by + ph / 2

        # Рамка панелі
        p.append(rect(bx, by, pw, ph, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=4))

        # Осі всередині панелі
        p.append(line(bx + 10, bcy, bx + pw - 10, bcy, color="#e1e4e8", sw=1.0, dash="3 3"))
        p.append(line(bcx, by + 10, bcx, by + ph - 10, color="#e1e4e8", sw=1.0, dash="3 3"))

        # Підпис зверху панелі
        p.append(text(bcx, by - 14, title_text, 13, INK, "middle", bold=True))
        p.append(text(bcx, by - 2, subtitle, 10.5, MUTED, "middle"))

        # Генерація точок
        if mode == "line_pos":
            for t in range(-50, 55, 10):
                p.append(circle(bcx + t, bcy - t, 3.2, fill=POS, stroke=POS, sw=0.8))
            p.append(line(bcx - 55, bcy + 55, bcx + 55, bcy - 55, color=POS, sw=1.5, dash="2 2"))

        elif mode == "cloud_pos":
            offsets = [
                (-50, -45), (-40, -30), (-35, -45), (-30, -20), (-25, -35),
                (-15, -10), (-10, -25), (0, 5), (5, -10), (15, 10),
                (20, 30), (30, 20), (35, 40), (45, 35), (50, 50),
                (-20, 5), (10, -25)
            ]
            for dx, dy in offsets:
                p.append(circle(bcx + dx, bcy - dy, 3.2, fill=POS, stroke=POS, sw=0.8))

        elif mode == "noise":
            offsets = [
                (-40, 20), (-35, -30), (-25, 45), (-20, -10), (-15, 25),
                (-10, -40), (0, 0), (5, 35), (10, -20), (20, 40),
                (25, -35), (35, 15), (40, -15), (-45, -5), (45, 5),
                (0, -45), (0, 45), (-30, -35), (30, 30)
            ]
            for dx, dy in offsets:
                p.append(circle(bcx + dx, bcy - dy, 3.2, fill=MUTED, stroke=MUTED, sw=0.8))

        elif mode == "cloud_neg":
            offsets = [
                (-50, 45), (-40, 30), (-35, 45), (-30, 20), (-25, 35),
                (-15, 10), (-10, 25), (0, -5), (5, 10), (15, -10),
                (20, -30), (30, -20), (35, -40), (45, -35), (50, -50),
                (-20, -5), (10, 25)
            ]
            for dx, dy in offsets:
                p.append(circle(bcx + dx, bcy - dy, 3.2, fill=NEG, stroke=NEG, sw=0.8))

        elif mode == "parabola":
            # Y = a * X^2 - b (детермінована залежність, але симетрична, ρ = 0)
            for x_val in range(-50, 55, 7):
                y_val = 0.022 * (x_val ** 2) - 30
                p.append(circle(bcx + x_val, bcy - y_val, 3.2, fill=FIELD, stroke=FIELD, sw=0.8))

    p.append(text(W / 2, H - 10,
                  "Кореляція Пірсона фіксує виключно лінійний тренд: при нелінійній залежності (крайня справа) ρ може дорівнювати 0.",
                  11, MUTED, "middle"))

    render(os.path.join(OUT, "correlation-patterns.svg"), W, H, *p,
           title="Спектр коефіцієнтів кореляції Пірсона: лінійність проти нелінійності")


# ── Фігура 3: Геометрія довірчого еліпсоїда коваріації ────────────────────────
# Центр (μ_X, μ_Y), головні осі вздовж власних векторів v1, v2.
# Довжини півосей дорівнюють √λ_1 та √λ_2.
# Порівняння з прямокутником окремих відхилень ±σ_X, ±σ_Y.
def fig_covariance_ellipsoid():
    W, H = 700, 440
    cx, cy = 350, 225

    p = []

    # Осі вихідної системи координат (X, Y)
    p.append(line(cx - 280, cy, cx + 280, cy, color="#d0d7de", sw=1.3))
    p.append(arrow(cx + 265, cy, cx + 285, cy, color=MUTED, sw=1.3))
    p.append(text(cx + 292, cy + 4, "X", 13, MUTED, "start", bold=True))

    p.append(line(cx, cy + 180, cx, cy - 180, color="#d0d7de", sw=1.3))
    p.append(arrow(cx, cy - 165, cx, cy - 185, color=MUTED, sw=1.3))
    p.append(text(cx, cy - 192, "Y", 13, MUTED, "middle", bold=True))

    # Центр розподілу (μ_X, μ_Y)
    p.append(circle(cx, cy, 4.5, fill=INK, stroke=BG, sw=1.5))
    p.append(text(cx - 12, cy + 18, "μ (центр)", 12, INK, "end", bold=True))

    # Кут нахилу головної осі (наприклад, 32 градуси)
    angle_deg = 32
    theta = math.radians(angle_deg)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    a1 = 180  # велика піввісь (k * √λ_1)
    b1 = 65   # мала піввісь (k * √λ_2)

    # 1-сигма та 2-сигма еліпси
    # Еліпс генеруємо через поворот параметричних точок
    def make_ellipse_poly(a, b, n=80):
        pts = []
        for i in range(n + 1):
            phi = 2 * math.pi * i / n
            ex = a * math.cos(phi)
            ey = b * math.sin(phi)
            rx = cx + ex * cos_t - ey * sin_t
            ry = cy - (ex * sin_t + ey * cos_t)
            pts.append("%.1f,%.1f" % (rx, ry))
        return " ".join(pts)

    # 2-сигма контур
    p.append('<polygon points="%s" fill="#eafaf1" fill-opacity="0.3" stroke="%s" stroke-width="1.3" stroke-dasharray="5 4"/>' %
             (make_ellipse_poly(a1 * 1.5, b1 * 1.5), FIELD))

    # 1-сигма контур
    p.append('<polygon points="%s" fill="#eafaf1" fill-opacity="0.6" stroke="%s" stroke-width="2.2"/>' %
             (make_ellipse_poly(a1, b1), FIELD))

    # Головна вісь (власний вектор v_1)
    vx1_end_x = cx + (a1 + 35) * cos_t
    vx1_end_y = cy - (a1 + 35) * sin_t
    vx1_start_x = cx - (a1 + 25) * cos_t
    vx1_start_y = cy + (a1 + 25) * sin_t
    p.append(line(vx1_start_x, vx1_start_y, vx1_end_x, vx1_end_y, color=POS, sw=1.6, dash="6 4"))
    p.append(arrow(cx + a1 * cos_t, cy - a1 * sin_t, vx1_end_x, vx1_end_y, color=POS, sw=1.8))
    p.append(text(vx1_end_x + 10, vx1_end_y - 6, "v₁ (головний напрямок)", 12, POS, "start", bold=True))

    # Мала вісь (власний вектор v_2)
    vx2_end_x = cx - (b1 + 30) * sin_t
    vx2_end_y = cy - (b1 + 30) * cos_t
    vx2_start_x = cx + (b1 + 20) * sin_t
    vx2_start_y = cy + (b1 + 20) * cos_t
    p.append(line(vx2_start_x, vx2_start_y, vx2_end_x, vx2_end_y, color=NEG, sw=1.6, dash="6 4"))
    p.append(arrow(cx - b1 * sin_t, cy - b1 * cos_t, vx2_end_x, vx2_end_y, color=NEG, sw=1.8))
    p.append(text(vx2_end_x - 12, vx2_end_y - 8, "v₂", 12, NEG, "end", bold=True))

    # Підписи довжин півосей
    p.append(text(cx + (a1 * 0.52) * cos_t + 12, cy - (a1 * 0.52) * sin_t - 14,
                  "піввісь = √λ₁", 12, POS, "start", bold=True))
    p.append(text(cx - (b1 * 0.55) * sin_t - 14, cy - (b1 * 0.55) * cos_t + 12,
                  "√λ₂", 12, NEG, "end", bold=True))

    # Прямокутник автономних меж ±σ_X, ±σ_Y (ілюстрація наївного прямокутного наближення)
    # Оцінка σ_X = √(a1^2 cos^2 + b1^2 sin^2), σ_Y = √(a1^2 sin^2 + b1^2 cos^2)
    sig_x = math.sqrt((a1 * cos_t) ** 2 + (b1 * sin_t) ** 2)
    sig_y = math.sqrt((a1 * sin_t) ** 2 + (b1 * cos_t) ** 2)

    p.append(rect(cx - sig_x, cy - sig_y, 2 * sig_x, 2 * sig_y,
                  fill="none", stroke="#9ca3af", sw=1.2, rx=0))
    p.append(text(cx + sig_x + 6, cy - sig_y + 14, "наївна рамка ±σ_X, ±σ_Y", 10.5, MUTED, "start"))

    p.append(text(W / 2, H - 10,
                  "Власні вектори v₁, v₂ задають напрямки осей еліпсоїда, а власні числа λ₁, λ₂ — дисперсії вздовж цих осей.",
                  11, MUTED, "middle"))

    render(os.path.join(OUT, "covariance-ellipsoid.svg"), W, H, *p,
           title="Довірчий еліпс коваріаційної матриці: власні вектори та власні значення")


if __name__ == "__main__":
    fig_covariance_quadrants()
    fig_correlation_patterns()
    fig_covariance_ellipsoid()
    print("Done generating covariance figures.")
