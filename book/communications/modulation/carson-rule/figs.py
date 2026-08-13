# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні кольори
COLOR_CARRIER = NEG      # Синій для несучої та основних ліній
COLOR_SIDEBAND = FIELD   # Зелений для бічних смуг
COLOR_WARN = POS         # Червоний для акцентів / завад / обрізання
COLOR_MUTED = MUTED      # Сірий для осей і сітки

def fig_fm_bessel_spectrum():
    W, H = 760, 520
    p = []
    
    # Заголовок малюнка
    p.append(text(W / 2, 30, "Спектральний склад ЧМ-сигналу при різних індексах модуляції β", size=15, color=INK, bold=True, anchor="middle"))

    panels = [
        (0.5, "а) Вузькосмугова ЧМ (β = 0.5): дві значущі бічні лінії, B ≈ 2·f☵", 80, 150),
        (2.4, "б) Перший нуль Бесселя (β = 2.4): несуча f☵ повністю відсутня (J₀ = 0)", 230, 300),
        (5.0, "в) Широкосмугова ЧМ (β = 5.0): розширений спектр, межа Карсона N = 6", 380, 450)
    ]

    # Коефіцієнти Бесселя для тестових β
    bessel_data = {
        0.5: [(0, 0.938), (1, 0.242), (2, 0.031)],
        2.4: [(0, 0.000), (1, 0.519), (2, 0.432), (3, 0.198), (4, 0.065)],
        5.0: [(0, 0.178), (1, 0.328), (2, 0.047), (3, 0.365), (4, 0.391), (5, 0.261), (6, 0.131), (7, 0.053)]
    }

    cx = W / 2
    scale_y = 70.0

    for beta, title_str, y_top, y_bot in panels:
        base_y = y_bot - 20
        # Заголовок панелі
        p.append(text(40, y_top, title_str, size=12.5, color=INK, bold=True, anchor="start"))
        # Вісь частот
        p.append(line(50, base_y, W - 50, base_y, color=COLOR_MUTED, sw=1.2))
        p.append(text(W - 45, base_y + 4, "f", size=12, color=COLOR_MUTED, bold=True, anchor="start"))

        # Центральна несуча f0
        p.append(line(cx, base_y, cx, base_y - 8, color=COLOR_MUTED, sw=1.0, dash="2 2"))
        p.append(text(cx, base_y + 16, "f☵", size=11, color=COLOR_MUTED, bold=True, anchor="middle"))

        lines_info = bessel_data[beta]
        dx = 32.0

        for n, amp in lines_info:
            h = amp * scale_y
            col = COLOR_CARRIER if n == 0 else COLOR_SIDEBAND
            
            # Лінія f0 + n*fm
            x_pos = cx + n * dx
            if x_pos < W - 60:
                p.append(line(x_pos, base_y, x_pos, base_y - h, color=col, sw=2.5))
                p.append(circle(x_pos, base_y - h, 3, fill=col))
                if amp > 0.05:
                    p.append(text(x_pos, base_y - h - 6, "%.2f" % amp, size=9.5, color=col, anchor="middle"))

            # Лінія f0 - n*fm
            if n > 0:
                x_neg = cx - n * dx
                if x_neg > 60:
                    p.append(line(x_neg, base_y, x_neg, base_y - h, color=col, sw=2.5))
                    p.append(circle(x_neg, base_y - h, 3, fill=col))
                    if amp > 0.05:
                        p.append(text(x_neg, base_y - h - 6, "%.2f" % amp, size=9.5, color=col, anchor="middle"))

        # Позначення смуги Карсона для β = 5.0
        if beta == 5.0:
            carson_n = 6
            x_left = cx - carson_n * dx
            x_right = cx + carson_n * dx
            p.append(line(x_left, base_y + 5, x_right, base_y + 5, color=COLOR_WARN, sw=1.8))
            p.append(line(x_left, base_y, x_left, base_y + 10, color=COLOR_WARN, sw=1.8))
            p.append(line(x_right, base_y, x_right, base_y + 10, color=COLOR_WARN, sw=1.8))
            p.append(text(cx, base_y + 24, "Смуга за Карсоном: B = 2·(5+1)·f☵ = 12·f☵ (98.8% енергії)", size=11, color=COLOR_WARN, bold=True, anchor="middle"))

    render(os.path.join(OUT, "fm-bessel-spectrum.svg"), W, H, *p, title="Спектральний склад ЧМ при різних індексах модуляції")

def fig_carson_power_distribution():
    W, H = 720, 420
    p = []

    p.append(text(W / 2, 28, "Розподіл спектральної потужності ЧМ-сигналу (β = 5.0)", size=15, color=INK, bold=True, anchor="middle"))

    ox, oy = 80, 340
    pw, ph = 580, 260

    # Осi
    p.append(line(ox, oy, ox + pw, oy, color=COLOR_MUTED, sw=1.5))
    p.append(line(ox, oy, ox, oy - ph, color=COLOR_MUTED, sw=1.5))

    p.append(text(ox + pw + 10, oy + 4, "Смуга B / f☵", size=12, color=COLOR_MUTED, bold=True, anchor="start"))
    p.append(text(ox - 10, oy - ph - 10, "Потужність (%)", size=12, color=COLOR_MUTED, bold=True, anchor="end"))

    # Сітка по Y (0%, 50%, 98%, 100%)
    y_levels = [(0, "0%"), (0.5, "50%"), (0.98, "98%"), (1.0, "100%")]
    for val, lbl in y_levels:
        y_pos = oy - val * ph
        col = COLOR_WARN if val == 0.98 else COLOR_MUTED
        dash_str = "4 3" if val == 0.98 else "2 4"
        p.append(line(ox, y_pos, ox + pw, y_pos, color=col, sw=1.0, dash=dash_str))
        p.append(text(ox - 8, y_pos + 4, lbl, size=11, color=col, bold=True, anchor="end"))

    # Точки накопиченої потужності для β = 5.0
    power_pts = [
        (0, 3.15),
        (2, 24.6),
        (4, 25.0),
        (6, 51.6),
        (8, 82.2),
        (10, 95.8),
        (12, 99.3),
        (14, 99.9),
        (16, 100.0)
    ]

    curve_pts = []
    for b_units, pct in power_pts:
        x = ox + (b_units / 16.0) * pw
        y = oy - (pct / 100.0) * ph
        curve_pts.append((x, y))

    # Малюємо криву
    path_d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in curve_pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (path_d, COLOR_CARRIER))

    for x, y in curve_pts:
        p.append(circle(x, y, 4, fill=COLOR_CARRIER))

    # Вертикальна лінія Карсона (B = 12 fm)
    x_carson = ox + (12.0 / 16.0) * pw
    y_carson = oy - 0.988 * ph
    p.append(line(x_carson, oy, x_carson, oy - ph, color=COLOR_WARN, sw=2.0, dash="5 4"))
    p.append(circle(x_carson, y_carson, 6, fill=COLOR_WARN))

    p.append(text(x_carson, oy + 20, "B_Carson = 12·f☵", size=12, color=COLOR_WARN, bold=True, anchor="middle"))

    b, bw, bh = textbox(x_carson - 140, oy - ph + 40,
                        "Правило Карсона B = 2·(Δf + f☵)\nутримує 98.8% всієї потужності",
                        size=11.5, color=COLOR_WARN, fill="#fff5f5", stroke=COLOR_WARN, min_w=200)
    p.append(b)

    render(os.path.join(OUT, "carson-power-distribution.svg"), W, H, *p, title="Розподіл спектральної потужності ЧМ")

def fig_fm_filter_distortion():
    W, H = 760, 360
    p = []

    p.append(text(W / 2, 28, "Вплив звуження смуги фільтра ПЧ на ЧМ-сигнал", size=15, color=INK, bold=True, anchor="middle"))

    # Три блоки
    box1_x, box1_y = 40, 70
    box_w, box_h = 200, 220

    # Блок 1: Вхідний ЧМ
    p.append(fitbox(box1_x, box1_y, box_w, box_h, "1. Вхідний ЧМ-сигнал\n(стала амплітуда A)", size=12, color=INK, fill="#f0f4f8", stroke=COLOR_CARRIER))

    # Сигнал у блоці 1
    cy1 = box1_y + 140
    pts1 = []
    for i in range(160):
        t = i / 159.0
        x = box1_x + 20 + t * 160
        freq = 3.0 + 2.0 * math.sin(2 * math.pi * t)
        y = cy1 - 35 * math.sin(2 * math.pi * freq * t * 4)
        pts1.append((x, y))
    p.append('<path d="M %s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" L ".join("%.1f,%.1f" % pt for pt in pts1), COLOR_CARRIER))
    p.append(line(box1_x + 20, cy1 - 35, box1_x + 180, cy1 - 35, color=MUTED, sw=1.0, dash="2 2"))
    p.append(line(box1_x + 20, cy1 + 35, box1_x + 180, cy1 + 35, color=MUTED, sw=1.0, dash="2 2"))

    # Стрілка 1 -> 2
    p.append(line(245, 180, 275, 180, color=INK, sw=2.0))
    p.append('<polygon points="275,175 283,180 275,185" fill="%s"/>' % INK)

    # Блок 2: Завузький Фільтр ПЧ
    box2_x = 285
    p.append(fitbox(box2_x, box1_y, box_w, box_h, "2. Фільтр ПЧ\n(B_filter < B_Carson)\nзрізає бокові гармоніки", size=12, color=COLOR_WARN, fill="#fff0f0", stroke=COLOR_WARN))

    # Малюємо АЧХ фільтра в блоці 2
    cy2 = box1_y + 140
    f_pts = []
    for i in range(100):
        t = i / 99.0
        x = box2_x + 30 + t * 140
        gain = math.exp(-pow((t - 0.5) / 0.2, 2))
        y = cy2 + 35 - gain * 70
        f_pts.append((x, y))
    p.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" L ".join("%.1f,%.1f" % pt for pt in f_pts), COLOR_WARN))
    p.append(text(box2_x + 100, cy2 + 50, "зрізано крайні гармоніки!", size=10.5, color=COLOR_WARN, bold=True, anchor="middle"))

    # Стрілка 2 -> 3
    p.append(line(490, 180, 520, 180, color=INK, sw=2.0))
    p.append('<polygon points="520,175 528,180 520,185" fill="%s"/>' % INK)

    # Блок 3: Вихідний сигнал з спотвореннями
    box3_x = 530
    p.append(fitbox(box3_x, box1_y, box_w, box_h, "3. Спотворений сигнал\n(Паразитна АМ +\nнелінійні фазові шуми)", size=12, color=INK, fill="#fff8e7", stroke=COLOR_WARN))

    # Сигнал у блоці 3 з пульсуючою амплітудою
    cy3 = box1_y + 140
    pts3 = []
    env_up = []
    env_dn = []
    for i in range(160):
        t = i / 159.0
        x = box3_x + 20 + t * 160
        amp = 35 * (0.7 + 0.3 * math.cos(4 * math.pi * t))
        freq = 3.0 + 2.0 * math.sin(2 * math.pi * t)
        y = cy3 - amp * math.sin(2 * math.pi * freq * t * 4)
        pts3.append((x, y))
        env_up.append((x, cy3 - amp))
        env_dn.append((x, cy3 + amp))

    p.append('<path d="M %s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" L ".join("%.1f,%.1f" % pt for pt in pts3), COLOR_CARRIER))
    p.append('<path d="M %s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3 3"/>' % (" L ".join("%.1f,%.1f" % pt for pt in env_up), COLOR_WARN))
    p.append('<path d="M %s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3 3"/>' % (" L ".join("%.1f,%.1f" % pt for pt in env_dn), COLOR_WARN))

    p.append(text(W / 2, 325, "Підсумок: звуження смуги фільтра породжує паразитну АМ та нелінійні гармонійні спотворення (THD)", size=12, color=INK, bold=True, anchor="middle"))

    render(os.path.join(OUT, "fm-filter-distortion.svg"), W, H, *p, title="Вплив звуження смуги фільтра ПЧ на ЧМ-сигнал")

if __name__ == "__main__":
    fig_fm_bessel_spectrum()
    fig_carson_power_distribution()
    fig_fm_filter_distortion()
    print("Figures generated successfully.")
