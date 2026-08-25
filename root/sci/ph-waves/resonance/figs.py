# -*- coding: utf-8 -*-
"""Генератор фігур для теми «Резонанс»."""

import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

img_dir = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(img_dir, exist_ok=True)


def fig_afc_curves():
    """Фігура 1: Амплітудно-частотна характеристика (АЧХ) вимушених коливань."""
    w, h = 760, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Амплітудно-частотна характеристика (АЧХ) за різної добротності Q", size=16, bold=True))

    # Область графіка
    ox, oy = 80, 400
    gx_w, gy_h = 600, 330

    # Сітка та осі
    frags.append(line(ox, oy, ox + gx_w, oy, color="#d1d5db", sw=1.5))
    frags.append(line(ox, oy, ox, oy - gy_h, color="#d1d5db", sw=1.5))

    # Стрілки осей
    frags.append(arrow(ox + gx_w, oy, ox + gx_w + 25, oy, color=LINE, sw=1.5))
    frags.append(arrow(ox, oy - gy_h, ox, oy - gy_h - 20, color=LINE, sw=1.5))

    frags.append(text(ox + gx_w + 30, oy + 5, "ω / ω₀", size=13, bold=True, anchor="start"))
    frags.append(text(ox - 10, oy - gy_h - 15, "A / A_стат", size=13, bold=True, anchor="end"))

    # Поділки X: 0, 0.5, 1.0 (резонанс), 1.5, 2.0
    for r in [0.5, 1.0, 1.5, 2.0]:
        px = ox + (r / 2.0) * gx_w
        frags.append(line(px, oy, px, oy + 5, color=LINE, sw=1.0))
        lbl = "1.0 (ω₀)" if r == 1.0 else "%.1f" % r
        frags.append(text(px, oy + 20, lbl, size=12, bold=(r == 1.0), color=POS if r == 1.0 else INK))
        if r == 1.0:
            frags.append(line(px, oy, px, oy - gy_h + 20, color="#fca5a5", sw=1.2, dash="4,4"))

    # Поділки Y: 1, 2, 4, 6, 8, 10
    scale_y = gy_h / 10.0
    for val in [1, 2, 4, 6, 8, 10]:
        py = oy - val * scale_y
        frags.append(line(ox - 5, py, ox, py, color=LINE, sw=1.0))
        frags.append(text(ox - 12, py + 4, str(val), size=12, anchor="end"))

    # Статичне зміщення (A/A_stat = 1)
    frags.append(line(ox, oy - scale_y, ox + gx_w, oy - scale_y, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(text(ox + 10, oy - scale_y - 6, "A_стат (ω → 0)", size=11, color=MUTED, anchor="start"))

    # Функція АЧХ: A_rel(r, Q) = 1 / sqrt((1 - r^2)^2 + (r / Q)^2)
    def calc_a(r, Q):
        if r < 0.001:
            return 1.0
        val = (1.0 - r * r) ** 2 + (r / Q) ** 2
        return 1.0 / math.sqrt(val)

    # Криві для Q = 10, Q = 3, Q = 1, Q = 0.5
    curves_data = [
        (10.0, POS, "Q = 10 (високодобротний)"),
        (3.0, NEG, "Q = 3 (помірний)"),
        (1.0, FIELD, "Q = 1 (критичний)"),
        (0.5, MUTED, "Q = 0.5 (сильне демпфування)")
    ]

    for Q_val, col, label_str in curves_data:
        pts = []
        steps = 200
        for i in range(steps + 1):
            r = (i / float(steps)) * 2.0
            a_rel = calc_a(r, Q_val)
            # Обмежуємо по висоті для відображення
            a_clamped = min(a_rel, 10.2)
            px = ox + (r / 2.0) * gx_w
            py = oy - a_clamped * scale_y
            pts.append("%.1f,%.1f" % (px, py))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), col))

    # Легенда
    lx, ly = 460, 70
    frags.append(rect(lx, ly, 260, 115, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=6))
    for idx, (Q_val, col, label_str) in enumerate(curves_data):
        item_y = ly + 22 + idx * 24
        frags.append(line(lx + 15, item_y, lx + 45, item_y, color=col, sw=2.5))
        frags.append(text(lx + 55, item_y + 4, label_str, size=12, color=INK, anchor="start", bold=(Q_val == 10.0)))

    # Точка максимуму для Q=10
    peak_x = ox + (1.0 / 2.0) * gx_w
    peak_y = oy - 10.0 * scale_y
    frags.append(circle(peak_x, peak_y, 4, fill=POS, stroke="#ffffff", sw=1.5))

    # Аннотаційна рамка резонансу
    tb, tw, th = textbox(ox + 230, oy - 270, "Резонансний пік:\nA_макс ≈ Q · A_стат\nω_р = ω₀ √(1 − 1/(2Q²))", size=12, pad=8, fill="#fff5f5", stroke=POS)
    frags.append(tb)

    render(os.path.join(img_dir, "afc-curves.svg"), w, h, *frags)


def fig_phase_response():
    """Фігура 2: Фазово-частотна характеристика та механічний зсув фаз."""
    w, h = 760, 450
    frags = []

    frags.append(text(w / 2, 28, "Зсув фаз φ між збуджувальною силою F(t) та відгуком x(t)", size=16, bold=True))

    ox, oy = 80, 370
    gx_w, gy_h = 600, 280

    # Осi
    frags.append(line(ox, oy, ox + gx_w, oy, color="#d1d5db", sw=1.5))
    frags.append(line(ox, oy, ox, oy - gy_h, color="#d1d5db", sw=1.5))

    frags.append(arrow(ox + gx_w, oy, ox + gx_w + 25, oy, color=LINE, sw=1.5))
    frags.append(arrow(ox, oy - gy_h, ox, oy - gy_h - 20, color=LINE, sw=1.5))

    frags.append(text(ox + gx_w + 30, oy + 5, "ω / ω₀", size=13, bold=True, anchor="start"))
    frags.append(text(ox - 10, oy - gy_h - 15, "Фаза φ", size=13, bold=True, anchor="end"))

    # Поділки X
    for r in [0.5, 1.0, 1.5, 2.0]:
        px = ox + (r / 2.0) * gx_w
        frags.append(line(px, oy, px, oy + 5, color=LINE, sw=1.0))
        frags.append(text(px, oy + 20, "1.0 (ω₀)" if r == 1.0 else "%.1f" % r, size=12, bold=(r == 1.0), color=POS if r == 1.0 else INK))
        if r == 1.0:
            frags.append(line(px, oy, px, oy - gy_h, color="#fca5a5", sw=1.2, dash="4,4"))

    # Поділки Y: 0, 45° (π/4), 90° (π/2), 135° (3π/4), 180° (π)
    phases = [(0, "0°"), (45, "45° (π/4)"), (90, "90° (π/2)"), (135, "135°"), (180, "180° (π)")]
    scale_y = gy_h / 180.0

    for deg, lbl in phases:
        py = oy - deg * scale_y
        frags.append(line(ox - 5, py, ox, py, color=LINE, sw=1.0))
        frags.append(text(ox - 12, py + 4, lbl, size=11, anchor="end", bold=(deg == 90), color=POS if deg == 90 else INK))
        if deg in [0, 90, 180]:
            frags.append(line(ox, py, ox + gx_w, py, color="#e2e8f0", sw=1.0, dash="3,3"))

    # Функція фази: phi(r, Q) = atan2(r / Q, 1 - r^2)
    def calc_phi_deg(r, Q):
        num = r / Q
        den = 1.0 - r * r
        phi_rad = math.atan2(num, den)
        if phi_rad < 0:
            phi_rad += math.pi
        return math.degrees(phi_rad)

    curves = [
        (10.0, POS, "Q = 10 (крутий перехід)"),
        (2.0, NEG, "Q = 2 (помірний)"),
        (0.7, FIELD, "Q = 0.7 (плавний)")
    ]

    for Q_val, col, label_str in curves:
        pts = []
        steps = 200
        for i in range(steps + 1):
            r = (i / float(steps)) * 2.0
            phi_d = calc_phi_deg(r, Q_val)
            px = ox + (r / 2.0) * gx_w
            py = oy - phi_d * scale_y
            pts.append("%.1f,%.1f" % (px, py))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), col))

    # Точка 90 градусів при резонансі
    res_x = ox + (1.0 / 2.0) * gx_w
    res_y = oy - 90 * scale_y
    frags.append(circle(res_x, res_y, 5, fill=POS, stroke="#ffffff", sw=1.5))

    # Рамка з поясненням фіз змісту 90 град
    tb, tw, th = textbox(ox + 420, oy - 210, "На резонансі (ω = ω₀):\n• Зсув фаз φ = 90° (π/2)\n• Сила F(t) збігається за фазою зі швидкістю v(t)\n• Передача потужності P = F · v максимальна!", size=12, pad=10, fill="#f0fdf4", stroke=FIELD)
    frags.append(tb)

    render(os.path.join(img_dir, "phase-response.svg"), w, h, *frags)


def fig_transient_buildup():
    """Фігура 3: Наростання коливань при резонансному розкачуванні."""
    w, h = 760, 420
    frags = []

    frags.append(text(w / 2, 28, "Перехідний процес розкачування осцилятора на резонансній частоті", size=16, bold=True))

    ox, oy = 70, 220
    gx_w, gy_h = 620, 150

    # Ось часу та нуль
    frags.append(line(ox, oy, ox + gx_w, oy, color=MUTED, sw=1.2))
    frags.append(arrow(ox + gx_w, oy, ox + gx_w + 25, oy, color=LINE, sw=1.5))
    frags.append(text(ox + gx_w + 30, oy + 4, "Час t", size=13, bold=True, anchor="start"))
    frags.append(text(ox - 15, oy - gy_h + 10, "Зміщення x(t)", size=13, bold=True, anchor="start"))

    # Стала амплітуда A_max = Q * A_stat
    a_max_y = gy_h - 20
    frags.append(line(ox, oy - a_max_y, ox + gx_w, oy - a_max_y, color=POS, sw=1.0, dash="4,4"))
    frags.append(line(ox, oy + a_max_y, ox + gx_w, oy + a_max_y, color=POS, sw=1.0, dash="4,4"))
    frags.append(text(ox - 10, oy - a_max_y + 4, "+A_макс", size=11, color=POS, anchor="end"))
    frags.append(text(ox - 10, oy + a_max_y + 4, "−A_макс", size=11, color=POS, anchor="end"))

    tau = 2.0
    w0 = 15.0
    t_max = 8.0

    pts = []
    env_pos = []
    env_neg = []
    steps = 400

    for i in range(steps + 1):
        t = (i / float(steps)) * t_max
        envelope = a_max_y * (1.0 - math.exp(-t / tau))
        val = envelope * math.sin(w0 * t)

        px = ox + (t / t_max) * gx_w
        py = oy - val
        pts.append("%.1f,%.1f" % (px, py))
        env_pos.append("%.1f,%.1f" % (px, oy - envelope))
        env_neg.append("%.1f,%.1f" % (px, oy + envelope))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,3"/>' % (" ".join(env_pos), POS))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,3"/>' % (" ".join(env_neg), POS))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(pts), NEG))

    tau_px = ox + (tau / t_max) * gx_w
    frags.append(line(tau_px, oy - a_max_y - 15, tau_px, oy + a_max_y + 15, color=FIELD, sw=1.2, dash="3,3"))
    frags.append(text(tau_px, oy + a_max_y + 30, "t = τ = 2Q / ω₀", size=12, color=FIELD, bold=True))

    tb, tw, th = textbox(ox + 440, oy + 70, "Час встановлення розкачування:\nτ ≈ 2Q / ω₀\nЩо вища добротність Q, то довше\nнаростає амплітуда до максимуму!", size=12, pad=8, fill="#f8fafc", stroke=FIELD)
    frags.append(tb)

    render(os.path.join(img_dir, "transient-buildup.svg"), w, h, *frags)


def fig_rlc_resonance():
    """Фігура 4: Послідовний RLC-контур та характеристика опору/струму."""
    w, h = 760, 440
    frags = []

    frags.append(text(w / 2, 28, "Електричний резонанс напруг у послідовному RLC-контурі", size=16, bold=True))

    sx, sy = 50, 100
    sw_w, sh_h = 260, 240

    frags.append(line(sx, sy, sx + sw_w, sy, color=LINE, sw=2.0))
    frags.append(line(sx + sw_w, sy, sx + sw_w, sy + sh_h, color=LINE, sw=2.0))
    frags.append(line(sx + sw_w, sy + sh_h, sx, sy + sh_h, color=LINE, sw=2.0))
    frags.append(line(sx, sy + sh_h, sx, sy, color=LINE, sw=2.0))

    gen_cy = sy + sh_h / 2
    frags.append(rect(sx - 15, gen_cy - 20, 30, 40, fill="#ffffff", stroke=LINE, sw=2.0))
    frags.append(circle(sx, gen_cy, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(sx, gen_cy + 4, "~", size=18, bold=True))
    frags.append(text(sx - 25, gen_cy + 4, "U(t)", size=12, bold=True, anchor="end", color=POS))

    rx = sx + 50
    frags.append(rect(rx, sy - 12, 40, 24, fill="#ffffff", stroke=LINE, sw=1.8))
    frags.append(text(rx + 20, sy - 20, "R", size=13, bold=True))

    lx = sx + 130
    for i in range(4):
        cx = lx + i * 10
        frags.append('<path d="M %d %d A 6 8 0 0 1 %d %d" fill="none" stroke="%s" stroke-width="2.0"/>' % (cx, sy, cx + 10, sy, LINE))
    frags.append(text(lx + 20, sy - 20, "L", size=13, bold=True))

    cx_pos = sx + 200
    frags.append(line(cx_pos, sy - 15, cx_pos, sy + 15, color=LINE, sw=2.5))
    frags.append(line(cx_pos + 10, sy - 15, cx_pos + 10, sy + 15, color=LINE, sw=2.5))
    frags.append(text(cx_pos + 5, sy - 20, "C", size=13, bold=True))

    frags.append(arrow(sx + 80, sy + sh_h + 15, sx + 180, sy + sh_h + 15, color=NEG, sw=2.0))
    frags.append(text(sx + 130, sy + sh_h + 35, "Струм I(t)", size=13, bold=True, color=NEG))

    gx, gy = 380, 360
    gw, gh = 320, 250

    frags.append(line(gx, gy, gx + gw, gy, color="#d1d5db", sw=1.5))
    frags.append(line(gx, gy, gx, gy - gh, color="#d1d5db", sw=1.5))

    frags.append(arrow(gx + gw, gy, gx + gw + 20, gy, color=LINE, sw=1.5))
    frags.append(arrow(gx, gy - gh, gx, gy - gh - 15, color=LINE, sw=1.5))

    frags.append(text(gx + gw + 25, gy + 4, "ω", size=13, bold=True))
    frags.append(text(gx - 10, gy - gh - 10, "Z, I", size=13, bold=True))

    w0_x = gx + gw * 0.5
    frags.append(line(w0_x, gy, w0_x, gy - gh + 20, color="#fca5a5", sw=1.2, dash="4,4"))
    frags.append(text(w0_x, gy + 20, "ω₀ = 1 / √(LC)", size=12, bold=True, color=POS))

    frags.append(line(gx + 20, gy - 20, gx + gw - 20, gy - gh + 40, color=POS, sw=1.8))
    frags.append(text(gx + gw - 15, gy - gh + 35, "X_L = ωL", size=11, color=POS, bold=True))

    xc_pts = []
    for i in range(10, 100):
        frac = i / 100.0
        px = gx + frac * gw
        py = gy - min(gh - 10, (15.0 / frac))
        xc_pts.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(xc_pts), NEG))
    frags.append(text(gx + 40, gy - 210, "X_C = 1/(ωC)", size=11, color=NEG, bold=True))

    i_pts = []
    for i in range(5, 95):
        frac = i / 100.0
        r_ratio = frac / 0.5
        dev = (r_ratio - 1.0 / r_ratio) * 3.0
        amp = 1.0 / math.sqrt(1.0 + dev * dev)
        px = gx + frac * gw
        py = gy - amp * (gh - 40)
        i_pts.append("%.1f,%.1f" % (px, py))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(i_pts), FIELD))
    frags.append(text(w0_x, gy - gh + 30, "I_макс = U / R", size=12, color=FIELD, bold=True))

    render(os.path.join(img_dir, "rlc-resonance.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_afc_curves()
    fig_phase_response()
    fig_transient_buildup()
    fig_rlc_resonance()
    print("Всі фігури успішно згенеровано у", img_dir)
