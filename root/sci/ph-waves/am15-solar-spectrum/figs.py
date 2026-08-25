# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1: Порівняння спектрів AM0, AM1.5G та AM1.5D
# ═══════════════════════════════════════════════════════════════════════════
def fig_am15_spectrum_comparison():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 25, 'Спектральний розподіл сонячного випромінювання (AM0, AM1.5G, AM1.5D)', 16, INK, 'middle', bold=True))

    ox, oy = 75, 360
    pw, ph = 660, 290

    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.5))
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.5))

    f.append(text(ox + pw / 2, oy + 42, 'Довжина хвилі λ (нм)', 12, INK, 'middle', bold=True))
    f.append(text(ox - 10, oy - ph - 10, 'Спектральна густина E_λ [Вт/(м²·нм)]', 11, INK, 'start', bold=True))

    w_min, w_max = 200, 2000
    for w_val in range(400, 2001, 200):
        px = ox + (w_val - w_min) / (w_max - w_min) * pw
        f.append(line(px, oy, px, oy - ph, color="#e5e7eb", sw=1, dash="3,3"))
        f.append(line(px, oy, px, oy + 5, color=INK, sw=1))
        f.append(text(px, oy + 18, str(w_val), 11, MUTED, 'middle'))

    for y_val in [0.5, 1.0, 1.5, 2.0]:
        py = oy - (y_val / 2.2) * ph
        f.append(line(ox, py, ox + pw, py, color="#e5e7eb", sw=1, dash="3,3"))
        f.append(line(ox - 5, py, ox, py, color=INK, sw=1))
        f.append(text(ox - 10, py + 4, "%.1f" % y_val, 11, MUTED, 'end'))

    x_uv1 = ox + (280 - w_min) / (w_max - w_min) * pw
    x_uv2 = ox + (400 - w_min) / (w_max - w_min) * pw
    x_vis2 = ox + (700 - w_min) / (w_max - w_min) * pw

    f.append(rect(x_uv1, oy - ph, x_uv2 - x_uv1, ph, fill="#f3e8ff", stroke="none", rx=0))
    f.append(rect(x_uv2, oy - ph, x_vis2 - x_uv2, ph, fill="#fef9c3", stroke="none", rx=0))
    f.append(rect(x_vis2, oy - ph, ox + pw - x_vis2, ph, fill="#ffedd5", stroke="none", rx=0))

    f.append(text((x_uv1 + x_uv2) / 2, oy - ph + 15, 'УФ', 10, "#6b21a8", 'middle', bold=True))
    f.append(text((x_uv2 + x_vis2) / 2, oy - ph + 15, 'Видиме світло (400–700 нм)', 11, "#854d0e", 'middle', bold=True))
    f.append(text((x_vis2 + ox + pw) / 2, oy - ph + 15, 'Інфрачервоне випромінювання (>700 нм)', 11, "#9a3412", 'middle', bold=True))

    def get_am0(w):
        x = 14387769.0 / (w * 5778.0)
        if x > 50: return 0.0
        r = (1.0 / (w**5 * (math.exp(x) - 1.0))) * 3.8e17
        return r

    def get_am15g(w):
        base = get_am0(w) * 0.76
        if w < 500:
            base *= (w / 500.0)**0.7
        if w < 290: base *= 0.01
        elif w < 320: base *= ((w - 290) / 30.0)**2
        if 755 <= w <= 770: base *= 0.35
        if 920 <= w <= 970: base *= 0.25
        if 1110 <= w <= 1160: base *= 0.30
        if 1340 <= w <= 1450: base *= 0.08
        if 1800 <= w <= 1950: base *= 0.05
        return base

    def get_am15d(w):
        return get_am15g(w) * 0.82

    pts_am0, pts_g, pts_d = [], [], []
    for w in range(250, 2001, 10):
        px = ox + (w - w_min) / (w_max - w_min) * pw
        v_am0 = get_am0(w)
        v_g = get_am15g(w)
        v_d = get_am15d(w)
        py_am0 = oy - (v_am0 / 2.2) * ph
        py_g = oy - (v_g / 2.2) * ph
        py_d = oy - (v_d / 2.2) * ph
        pts_am0.append("%.1f,%.1f" % (px, py_am0))
        pts_g.append("%.1f,%.1f" % (px, py_g))
        pts_d.append("%.1f,%.1f" % (px, py_d))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,4"/>' % (" ".join(pts_am0), MUTED))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_g), POS))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(pts_d), NEG))

    px_o2 = ox + (760 - w_min) / (w_max - w_min) * pw
    py_o2 = oy - (get_am15g(760) / 2.2) * ph
    f.append(line(px_o2, py_o2 - 5, px_o2, py_o2 - 40, color=LINE, sw=1.2))
    f.append(textbox(px_o2 + 25, py_o2 - 52, "O₂ (760 нм)", size=10, pad=4, fill="#ffffff", color=INK)[0])

    px_h2o1 = ox + (940 - w_min) / (w_max - w_min) * pw
    py_h2o1 = oy - (get_am15g(940) / 2.2) * ph
    f.append(line(px_h2o1, py_h2o1 - 5, px_h2o1, py_h2o1 - 35, color=LINE, sw=1.2))
    f.append(textbox(px_h2o1 + 25, py_h2o1 - 47, "H₂O (940 нм)", size=10, pad=4, fill="#ffffff", color=INK)[0])

    px_h2o2 = ox + (1380 - w_min) / (w_max - w_min) * pw
    py_h2o2 = oy - (get_am15g(1380) / 2.2) * ph
    f.append(line(px_h2o2, py_h2o2 - 5, px_h2o2, py_h2o2 - 35, color=LINE, sw=1.2))
    f.append(textbox(px_h2o2 + 30, py_h2o2 - 47, "H₂O/CO₂ (1.38 мкм)", size=10, pad=4, fill="#ffffff", color=INK)[0])

    f.append(rect(ox + pw - 230, oy - ph + 25, 220, 85, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    f.append(line(ox + pw - 215, oy - ph + 45, ox + pw - 185, oy - ph + 45, color=MUTED, sw=1.8, dash="5,4"))
    f.append(text(ox + pw - 175, oy - ph + 49, 'AM0 (Космос, 1361 Вт/м²)', 11, INK, 'start'))

    f.append(line(ox + pw - 215, oy - ph + 65, ox + pw - 185, oy - ph + 65, color=POS, sw=2.5))
    f.append(text(ox + pw - 175, oy - ph + 69, 'AM1.5G (Глобальний, 1000 Вт/м²)', 11, INK, 'start', bold=True))

    f.append(line(ox + pw - 215, oy - ph + 85, ox + pw - 185, oy - ph + 85, color=NEG, sw=2.0))
    f.append(text(ox + pw - 175, oy - ph + 89, 'AM1.5D (Прямий, 900 Вт/м²)', 11, INK, 'start'))

    render(os.path.join(IMG, 'am15-spectrum-comparison.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2: Геометрія маси атмосфери та 37° нахилу
# ═══════════════════════════════════════════════════════════════════════════
def fig_airmass_geometry_37deg():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 25, 'Геометрія сонячного випромінювання AM1.5G та оптичний шлях', 16, INK, 'middle', bold=True))

    gy = 330
    f.append(rect(40, gy, 680, 40, fill="#e5e7eb", stroke=LINE, sw=1.5, rx=0))
    f.append(text(100, gy + 24, 'Поверхня Землі (Альбедо ρ = 0.2)', 12, INK, 'start', bold=True))

    ay = 110
    f.append(line(40, ay, 720, ay, color=NEG, sw=1.5, dash="6,4"))
    f.append(text(80, ay - 10, 'Верхня межа атмосфери (AM0)', 11, NEG, 'start', bold=True))

    rx, ry = 420, gy

    f.append(line(rx, ay, rx, ry, color=MUTED, sw=1.5, dash="4,4"))
    f.append(arrow(rx, ay, rx, ay + 40, color=MUTED, sw=1.5))
    f.append(text(rx + 10, ay + 60, 'Зеніт (AM1.0, θ = 0°)', 11, MUTED, 'start'))

    theta_rad = math.radians(48.19)
    length = (gy - ay) / math.cos(theta_rad)
    sx = rx - length * math.sin(theta_rad)
    sy = ay

    f.append(arrow(sx, sy, rx, ry, color=POS, sw=3.0))

    f.append(circle(sx - 15, sy - 15, 20, fill="#fef08a", stroke="#eab308", sw=2))
    f.append(text(sx - 15, sy - 10, 'Сонце', 10, "#854d0e", 'middle', bold=True))

    f.append(text(rx - 30, ry - 140, 'θ_z = 48.19°', 12, POS, 'end', bold=True))
    f.append(text(rx - 70, (ay + gy) / 2, 'Оптичний шлях = 1.5 атмосфери (AM1.5)', 12, POS, 'middle', bold=True))

    pw = 90
    tilt_rad = math.radians(37)
    px1 = rx - (pw / 2) * math.cos(tilt_rad)
    py1 = ry + (pw / 2) * math.sin(tilt_rad) - 5
    px2 = rx + (pw / 2) * math.cos(tilt_rad)
    py2 = ry - (pw / 2) * math.sin(tilt_rad) - 5

    f.append(line(px1, py1, px2, py2, color="#1e3a8a", sw=8))
    f.append(line(px1, py1, px2, py2, color="#3b82f6", sw=5))

    f.append(line(px1, py1, px1 + 60, py1, color=LINE, sw=1.2, dash="3,3"))
    f.append(text(px1 + 45, py1 - 8, '37°', 11, INK, 'middle', bold=True))

    f.append(text(rx - 120, ry - 35, 'Пряме випромінювання (D)', 11, POS, 'end', bold=True))

    f.append(arrow(rx + 80, ay + 90, rx + 20, ry - 40, color="#0284c7", sw=1.8))
    f.append(arrow(rx - 60, ay + 110, rx - 10, ry - 40, color="#0284c7", sw=1.8))
    f.append(text(rx + 110, ay + 100, 'Дифузне світло неба (Diff)', 11, "#0284c7", 'start', bold=True))

    f.append(arrow(rx - 100, gy - 2, rx - 35, ry - 10, color=FIELD, sw=1.8))
    f.append(text(rx - 140, gy - 15, 'Відбите світло (Альбедо)', 11, FIELD, 'end', bold=True))

    info_box = ("Глобальний спектр AM1.5G (1000 Вт/м²)\n"
                "• Маса атмосфери AM = 1/cos(48.19°) ≈ 1.5\n"
                "• Нахил поверхні: 37° на південь (Пн. півкуля)\n"
                "• AM1.5G = Пряме + Дифузне + Відбите")
    f.append(textbox(570, 260, info_box, size=11, pad=10, fill="#f0f9ff", stroke="#0284c7", color=INK)[0])

    render(os.path.join(IMG, 'airmass-geometry-37deg.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3: Спектральний відгук напівпровідника та втрати
# ═══════════════════════════════════════════════════════════════════════════
def fig_pv_spectral_response():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 25, 'Спектральний відгук напівпровідника та втрати енергії в спектрі AM1.5G', 16, INK, 'middle', bold=True))

    ox, oy = 75, 360
    pw, ph = 640, 290

    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.5))
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.5))

    f.append(text(ox + pw / 2, oy + 42, 'Довжина хвилі λ (нм)', 12, INK, 'middle', bold=True))
    f.append(text(ox - 10, oy - ph - 10, 'Спектральна інтенсивність E_λ [Вт/(м²·нм)]', 11, INK, 'start', bold=True))

    w_min, w_max = 300, 1600
    for w_val in range(400, 1601, 200):
        px = ox + (w_val - w_min) / (w_max - w_min) * pw
        f.append(line(px, oy, px, oy - ph, color="#e5e7eb", sw=1, dash="3,3"))
        f.append(line(px, oy, px, oy + 5, color=INK, sw=1))
        f.append(text(px, oy + 18, str(w_val), 11, MUTED, 'middle'))

    px_cut = ox + (1100 - w_min) / (w_max - w_min) * pw
    # Пунктирна лінія з розривом під рамку напису (від y=70 до 75 і від 125 до oy)
    box_top, box_bot = oy - ph + 10, oy - ph + 55
    f.append(line(px_cut, oy - ph, px_cut, box_top, color=POS, sw=2.0, dash="5,4"))
    f.append(line(px_cut, box_bot, px_cut, oy, color=POS, sw=2.0, dash="5,4"))
    f.append(textbox(px_cut, (box_top + box_bot) / 2, "Край поглинання Si\nλ_cut = 1100 нм (1.12 еВ)", size=10, pad=5, fill="#ffe4e6", stroke=POS, color=POS)[0])

    def get_am15g_simple(w):
        if w < 290: return 0.0
        val = 1.55 * math.exp(-((w - 500) / 350.0)**2)
        if 755 <= w <= 770: val *= 0.4
        if 920 <= w <= 970: val *= 0.3
        if 1110 <= w <= 1160: val *= 0.35
        if 1340 <= w <= 1450: val *= 0.1
        return val

    # 1. Термалізація
    pts_therm = ["%.1f,%.1f" % (ox, oy)]
    for w in range(300, 1101, 10):
        px = ox + (w - w_min) / (w_max - w_min) * pw
        val = get_am15g_simple(w)
        py = oy - (val / 2.0) * ph
        pts_therm.append("%.1f,%.1f" % (px, py))
    pts_therm.append("%.1f,%.1f" % (px_cut, oy))
    f.append('<polygon points="%s" fill="#fed7aa" opacity="0.8"/>' % " ".join(pts_therm))

    # 2. Корисна електрична потужність
    pts_useful = ["%.1f,%.1f" % (ox, oy)]
    for w in range(300, 1101, 10):
        px = ox + (w - w_min) / (w_max - w_min) * pw
        val = get_am15g_simple(w)
        val_useful = val * (w / 1100.0)
        py = oy - (val_useful / 2.0) * ph
        pts_useful.append("%.1f,%.1f" % (px, py))
    pts_useful.append("%.1f,%.1f" % (px_cut, oy))
    f.append('<polygon points="%s" fill="#bbf7d0" opacity="0.8"/>' % " ".join(pts_useful))

    # 3. Підпорогова прозорість
    pts_transp = ["%.1f,%.1f" % (px_cut, oy)]
    for w in range(1100, 1601, 10):
        px = ox + (w - w_min) / (w_max - w_min) * pw
        val = get_am15g_simple(w)
        py = oy - (val / 2.0) * ph
        pts_transp.append("%.1f,%.1f" % (px, py))
    pts_transp.append("%.1f,%.1f" % (ox + pw, oy))
    f.append('<polygon points="%s" fill="#e2e8f0" opacity="0.9"/>' % " ".join(pts_transp))

    pts_am15 = []
    for w in range(300, 1601, 10):
        px = ox + (w - w_min) / (w_max - w_min) * pw
        val = get_am15g_simple(w)
        py = oy - (val / 2.0) * ph
        pts_am15.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_am15), INK))

    # Анотаційні блоки з рамками
    f.append(textbox(ox + 160, oy - 140, "Втрати термалізації\n(hν − Eg → тепло)", size=10, pad=5, fill="#fff7ed", stroke="#c2410c", color="#c2410c")[0])
    f.append(textbox(ox + 220, oy - 45, "Корисна потужність (Eg)", size=10, pad=5, fill="#f0fdf4", stroke="#15803d", color="#15803d")[0])
    f.append(textbox(ox + 480, oy - 80, "Підпорогова прозорість\n(hν < Eg, λ > 1100 нм)", size=10, pad=5, fill="#f8fafc", stroke="#475569", color="#475569")[0])

    render(os.path.join(IMG, 'pv-spectral-response.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4: Оптична схема сонячного імітатора
# ═══════════════════════════════════════════════════════════════════════════
def fig_solar_simulator_class():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 25, 'Схема лабораторного імітатора сонячного спектра (клас AAA)', 16, INK, 'middle', bold=True))

    b1 = textbox(110, 140, "Джерело світла\n(Xe лампа 1000 Вт\nабо LED масив)", size=11, pad=8, fill="#fef08a", stroke="#eab308", color=INK)[0]
    f.append(b1)

    b2 = textbox(270, 140, "Оптична система\nконденсора та\nвідбивача", size=11, pad=8, fill="#f4f6f8", stroke=LINE, color=INK)[0]
    f.append(b2)

    b3 = textbox(430, 140, "Спектральний\nфільтр AM1.5G\n(Air Mass Filter)", size=11, pad=8, fill="#e0e7ff", stroke="#4338ca", color="#3730a3", bold=True)[0]
    f.append(b3)

    b4 = textbox(590, 140, "Оптичний\nгомогенізатор\n(рівномірність плями)", size=11, pad=8, fill="#f4f6f8", stroke=LINE, color=INK)[0]
    f.append(b4)

    f.append(arrow(180, 140, 205, 140, color=POS, sw=2.5))
    f.append(arrow(335, 140, 360, 140, color=POS, sw=2.5))
    f.append(arrow(500, 140, 525, 140, color=POS, sw=2.5))

    f.append(arrow(590, 185, 590, 250, color=POS, sw=3.0))

    f.append(rect(450, 260, 280, 70, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    f.append(rect(510, 270, 160, 15, fill="#1e40af", stroke="none", rx=2))
    f.append(text(590, 282, 'Досліджуваний сонячний елемент', 10, "#ffffff", 'middle', bold=True))

    f.append(rect(470, 298, 90, 22, fill="#ecfdf5", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(515, 313, 'Еталонний фотодіод', 9, FIELD, 'middle', bold=True))

    f.append(rect(610, 298, 100, 22, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    f.append(text(660, 313, 'Термостатування 25°C', 9, NEG, 'middle', bold=True))

    req_text = ("Вимоги до імітатора класу AAA (IEC 60904-9):\n"
                "1. Спектральний збіг (Spectral Match): відхилення 0.75…1.25 від AM1.5G\n"
                "2. Просторова нерівномірність (Non-uniformity): < 2% по всій площі плями\n"
                "3. Часова нестабільність (Temporal Instability): < 2% протягом вимірювання")
    f.append(textbox(240, 295, req_text, size=10, pad=8, fill="#f0fdf4", stroke=FIELD, color=INK)[0])

    render(os.path.join(IMG, 'solar-simulator-class.svg'), W, H, *f)


if __name__ == '__main__':
    fig_am15_spectrum_comparison()
    fig_airmass_geometry_37deg()
    fig_pv_spectral_response()
    fig_solar_simulator_class()
    print("All figures successfully generated in img/")
