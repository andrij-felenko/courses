# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для теми "Чисельне диференціювання".
Використовує бібліотеку svgkit з кореневої теки scripts.
"""

import sys
import os
import math

# Підключаємо scripts/ з кореня репо (4 рівні вгору від root/sci/math-numeric/numerical-differentiation)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def draw_differentiation_dilemma():
    """Фігура 1: Фундаментальна дилема чисельного диференціювання: похибка апроксимації vs шум вимірювань/заокруглення."""
    w, h = 760, 420
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%">' % (w, h)]
    
    svg.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    
    # Заголовок панелі
    tb, _, _ = textbox(w/2, 28, "Фундаментальна дилема: похибка формули vs шум вимірювань (Log-Log)", size=14, bold=True, fill="#eef2f7", stroke="#4a5568")
    svg.append(tb)
    
    # Система координат (Log-Log)
    ox, oy = 90, 340
    pw, ph = 420, 260
    
    # Сітка
    svg.append(line(ox, oy, ox + pw, oy, color=LINE, sw=1.5))
    svg.append(line(ox, oy, ox, oy - ph, color=LINE, sw=1.5))
    
    # Позначки осей
    svg.append(text(ox + pw + 15, oy + 4, "Крок h", size=12, color=INK, bold=True, anchor="start"))
    svg.append(text(ox, oy - ph - 15, "Похибка E(h)", size=12, color=INK, bold=True, anchor="middle"))
    
    # Допоміжна сітка Log-Log
    for i in range(1, 5):
        gx = ox + i * (pw / 4.0)
        svg.append(line(gx, oy, gx, oy - ph, color="#f1f5f9", sw=1.0, dash="3,3"))
        gy = oy - i * (ph / 4.0)
        svg.append(line(ox, gy, ox + pw, gy, color="#f1f5f9", sw=1.0, dash="3,3"))
    
    svg.append(text(ox + 40, oy + 20, "10⁻⁸ (дрібний крок)", size=11, color=MUTED))
    svg.append(text(ox + pw - 40, oy + 20, "10⁻¹ (великий крок)", size=11, color=MUTED))
    
    # Криві
    pts_trunc = []
    pts_noise = []
    pts_total = []
    
    steps = 150
    for i in range(steps + 1):
        t = i / float(steps)
        px = ox + t * pw
        
        noise_err_val = 0.82 - 0.72 * t
        trunc_err_val = 0.08 + 0.80 * t
        
        py_noise = oy - noise_err_val * ph
        py_trunc = oy - trunc_err_val * ph
        
        diff_from_opt = t - 0.47
        total_val = 0.32 + 1.8 * (diff_from_opt ** 2) if abs(diff_from_opt) > 0.1 else 0.32 + 1.2 * (diff_from_opt ** 2)
        py_total = oy - total_val * ph
        
        pts_noise.append("%.1f,%.1f" % (px, py_noise))
        pts_trunc.append("%.1f,%.1f" % (px, py_trunc))
        pts_total.append("%.1f,%.1f" % (px, py_total))
        
    # Лінії
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,4"/>' % (" ".join(pts_trunc), FIELD))
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,4"/>' % (" ".join(pts_noise), POS))
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (" ".join(pts_total), NEG))
    
    # Оптимальна точка h_opt
    opt_x = ox + 0.47 * pw
    opt_y = oy - 0.32 * ph
    svg.append(circle(opt_x, opt_y, 6.0, fill=NEG, stroke=BG, sw=2.0))
    svg.append(line(opt_x, oy, opt_x, opt_y, color=NEG, sw=1.5, dash="4,4"))
    svg.append(text(opt_x, oy + 20, "h_opt", size=12, color=NEG, bold=True))
    
    # Підпис зон
    svg.append(text(ox + 80, oy - ph + 25, "Зона катастрофи шуму", size=11, color=POS, bold=True))
    svg.append(text(ox + 80, oy - ph + 42, "(Шум ε/h домінує)", size=10, color=POS))
    
    svg.append(text(ox + pw - 90, oy - ph + 25, "Зона усікання Тейлора", size=11, color=FIELD, bold=True))
    svg.append(text(ox + pw - 90, oy - ph + 42, "(Похибка O(h²) завеликий крок)", size=10, color=FIELD))
    
    # Картка-легенда праворуч
    lx, ly = 530, 75
    svg.append(rect(lx, ly, 215, 175, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    svg.append(text(lx + 107, ly + 22, "Складові похибки", size=12, bold=True, color=INK))
    
    svg.append(line(lx + 15, ly + 52, lx + 45, ly + 52, color=NEG, sw=3.0))
    svg.append(text(lx + 55, ly + 56, "Сумарна E_total(h)", size=11, color=NEG, bold=True, anchor="start"))
    
    svg.append(line(lx + 15, ly + 87, lx + 45, ly + 87, color=FIELD, sw=2.2, dash="5,3"))
    svg.append(text(lx + 55, ly + 91, "Усікання: O(h²)", size=11, color=FIELD, bold=True, anchor="start"))
    
    svg.append(line(lx + 15, ly + 122, lx + 45, ly + 122, color=POS, sw=2.2, dash="5,3"))
    svg.append(text(lx + 55, ly + 126, "Шум / кодування: 2ε/h", size=11, color=POS, bold=True, anchor="start"))
    
    svg.append(line(lx + 10, ly + 145, lx + 205, ly + 145, color="#e2e8f0", sw=1.0))
    svg.append(text(lx + 107, ly + 163, "h_opt ≈ (3ε / M₃)¹/³", size=11, color=INK, bold=True))
    
    svg.append(rect(lx, 265, 215, 115, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=6))
    inf = [
        "Некоректність за Адамаром:",
        "Зменшення кроку h → 0",
        "не наближає розв'язок,",
        "а експоненційно підсилює",
        "шум вимірювань і розряду!"
    ]
    svg.append(mtext(lx + 107, 285, inf, size=10, color="#1e3a8a", lh=1.35))
    
    svg.append('</svg>')
    return "\n".join(svg)

def draw_finite_difference_stencils():
    """Фігура 2: Геометричне порівняння триточкових схем: Forward, Backward, Central difference."""
    w, h = 760, 360
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%">' % (w, h)]
    
    svg.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    
    # Заголовок
    tb, _, _ = textbox(w/2, 26, "Геометрія скінченно-різницевих схем: пряма, зворотна та центральна різниці", size=13, bold=True, fill="#eef2f7", stroke="#4a5568")
    svg.append(tb)
    
    ox, oy = 80, 290
    scale_x = 130
    scale_y = 200
    
    def f_curve(x):
        return 0.25 + 0.55 * math.sin(1.1 * x - 0.3)
        
    pts = []
    for i in range(301):
        x_val = 0.2 + 3.8 * i / 300.0
        y_val = f_curve(x_val)
        px = ox + x_val * scale_x
        py = oy - y_val * scale_y
        pts.append("%.1f,%.1f" % (px, py))
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), INK))
    
    # Вузли x-h, x, x+h
    x_mid = 2.0
    h_step = 1.0
    x_prev = x_mid - h_step
    x_next = x_mid + h_step
    
    px_prev = ox + x_prev * scale_x
    py_prev = oy - f_curve(x_prev) * scale_y
    
    px_mid = ox + x_mid * scale_x
    py_mid = oy - f_curve(x_mid) * scale_y
    
    px_next = ox + x_next * scale_x
    py_next = oy - f_curve(x_next) * scale_y
    
    # Вертикальні лінії сітки
    for px_n, lbl in zip([px_prev, px_mid, px_next], ["x - h", "x", "x + h"]):
        svg.append(line(px_n, oy + 5, px_n, oy - 230, color="#e2e8f0", sw=1.0, dash="3,3"))
        svg.append(text(px_n, oy + 22, lbl, size=12, color=INK, bold=True))
    
    # Вісь X
    svg.append(line(ox - 20, oy, ox + 520, oy, color=LINE, sw=1.2))
    
    # 1. Пряма різниця
    svg.append(line(px_mid - 20, py_mid + (py_next - py_mid)*(-20)/(px_next - px_mid),
                    px_next + 30, py_next + (py_next - py_mid)*(30)/(px_next - px_mid),
                    color=POS, sw=1.8, dash="5,3"))
    
    # 2. Зворотна різниця
    svg.append(line(px_prev - 30, py_prev + (py_mid - py_prev)*(-30)/(px_mid - px_prev),
                    px_mid + 20, py_mid + (py_mid - py_prev)*(20)/(px_mid - px_prev),
                    color="#ea580c", sw=1.8, dash="5,3"))
    
    # 3. Центральна різниця
    svg.append(line(px_prev - 30, py_prev + (py_next - py_prev)*(-30)/(px_next - px_prev),
                    px_next + 30, py_next + (py_next - py_prev)*(30)/(px_next - px_prev),
                    color=FIELD, sw=2.4))
    
    # 4. Справжня дотична
    df_true = 0.55 * 1.1 * math.cos(1.1 * x_mid - 0.3)
    slope_px = - df_true * (scale_y / float(scale_x))
    svg.append(line(px_mid - 70, py_mid - 70 * slope_px,
                    px_mid + 70, py_mid + 70 * slope_px,
                    color=NEG, sw=2.0))
    
    # Точки
    svg.append(circle(px_prev, py_prev, 5.0, fill=INK, stroke=BG, sw=1.5))
    svg.append(circle(px_mid, py_mid, 6.0, fill=NEG, stroke=BG, sw=1.5))
    svg.append(circle(px_next, py_next, 5.0, fill=INK, stroke=BG, sw=1.5))
    
    svg.append(text(px_prev - 10, py_prev - 12, "f(x-h)", size=11, color=INK, anchor="end"))
    svg.append(text(px_mid + 12, py_mid - 15, "f(x)", size=11, color=NEG, bold=True, anchor="start"))
    svg.append(text(px_next + 10, py_next - 12, "f(x+h)", size=11, color=INK, anchor="start"))
    
    # Легенда
    lx, ly = 500, 50
    svg.append(rect(lx, ly, 245, 255, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    svg.append(text(lx + 122, ly + 22, "Порівняння січних і порядку O", size=12, bold=True, color=INK))
    
    svg.append(line(lx + 15, ly + 52, lx + 45, ly + 52, color=NEG, sw=2.2))
    svg.append(text(lx + 55, ly + 56, "Справжня дотична f′(x)", size=11, color=NEG, bold=True, anchor="start"))
    
    svg.append(line(lx + 15, ly + 90, lx + 45, ly + 90, color=FIELD, sw=2.4))
    svg.append(text(lx + 55, ly + 94, "Центральна: O(h²)", size=11, color=FIELD, bold=True, anchor="start"))
    svg.append(text(lx + 55, ly + 110, "[f(x+h) - f(x-h)] / (2h)", size=10, color=MUTED, anchor="start"))
    
    svg.append(line(lx + 15, ly + 145, lx + 45, ly + 145, color=POS, sw=2.0, dash="5,3"))
    svg.append(text(lx + 55, ly + 149, "Пряма: O(h)", size=11, color=POS, bold=True, anchor="start"))
    svg.append(text(lx + 55, ly + 165, "[f(x+h) - f(x)] / h", size=10, color=MUTED, anchor="start"))
    
    svg.append(line(lx + 15, ly + 200, lx + 45, ly + 200, color="#ea580c", sw=2.0, dash="5,3"))
    svg.append(text(lx + 55, ly + 204, "Зворотна: O(h)", size=11, color="#ea580c", bold=True, anchor="start"))
    svg.append(text(lx + 55, ly + 220, "[f(x) - f(x-h)] / h", size=10, color=MUTED, anchor="start"))
    
    svg.append(line(lx + 10, ly + 235, lx + 235, ly + 235, color="#e2e8f0", sw=1.0))
    svg.append(text(lx + 122, ly + 248, "Центральна січна паралельна дотичній!", size=10, color=FIELD, bold=True))
    
    svg.append('</svg>')
    return "\n".join(svg)

def draw_savitzky_golay_fit():
    """Фігура 3: Принцип роботи фільтра Савицького–Голея: локальна поліноміальна апроксимація у ковзному вікні."""
    w, h = 760, 400
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%">' % (w, h)]
    
    svg.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    
    # Заголовок
    tb, _, _ = textbox(w/2, 26, "Фільтр Савицького–Голея: аналітична похідна локального МНК-полінома", size=13, bold=True, fill="#eef2f7", stroke="#4a5568")
    svg.append(tb)
    
    ox, oy = 60, 240
    scale_x = 45
    scale_y = 130
    
    # Вісь X і дискретні точки
    svg.append(line(ox - 10, oy + 20, ox + 640, oy + 20, color=LINE, sw=1.2))
    
    xs = [-3, -2, -1, 0, 1, 2, 3]
    def f_true(x): return 0.5 + 0.35 * math.cos(0.45 * x)
    noise_offsets = [0.08, -0.06, 0.05, -0.04, 0.07, -0.05, 0.04]
    
    center_idx = 7
    
    # Зона вікна апроксимації
    w_start_px = ox + (center_idx - 3.5) * scale_x
    w_end_px = ox + (center_idx + 3.5) * scale_x
    svg.append(rect(w_start_px, 50, w_end_px - w_start_px, oy - 25, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    svg.append(text((w_start_px + w_end_px)/2, 68, "Ковзне вікно Савицького–Голея (2m + 1 = 7 точок)", size=11, color=FIELD, bold=True))
    
    # Зашумлені точки всередині вікна
    for i, offset_val in enumerate(xs):
        gx = center_idx + offset_val
        px = ox + gx * scale_x
        y_val = f_true(offset_val) + noise_offsets[i]
        py = oy - y_val * scale_y
        
        svg.append(line(px, oy + 20, px, py, color="#cbd5e1", sw=1.0, dash="2,2"))
        c_fill = POS if offset_val == 0 else "#64748b"
        svg.append(circle(px, py, 4.5, fill=c_fill, stroke=BG, sw=1.2))
        
        lbl = "k" if offset_val == 0 else ("k%+d" % offset_val)
        svg.append(text(px, oy + 38, lbl, size=11, color=INK, bold=(offset_val == 0)))
        
    # Локальний підігнаний параболічний поліном
    poly_pts = []
    for step in range(101):
        t = -3.2 + 6.4 * step / 100.0
        gx = center_idx + t
        px = ox + gx * scale_x
        y_poly = 0.81 - 0.05 * t - 0.035 * (t ** 2)
        py = oy - y_poly * scale_y
        poly_pts.append("%.1f,%.1f" % (px, py))
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(poly_pts), FIELD))
    
    # Похідна у центральній точці t=0
    c_px = ox + center_idx * scale_x
    c_py = oy - 0.81 * scale_y
    c_slope_px = - (-0.05) * (scale_y / float(scale_x))
    svg.append(line(c_px - 75, c_py - 75 * c_slope_px, c_px + 75, c_py + 75 * c_slope_px, color=NEG, sw=2.5))
    svg.append(circle(c_px, c_py, 6.5, fill=NEG, stroke=BG, sw=2.0))
    
    # Пояснювальна виноска
    svg.append(arrow(c_px + 45, c_py - 40, c_px + 10, c_py - 10, color=NEG, sw=1.8))
    svg.append(text(c_px + 60, c_py - 45, "Аналітична похідна P′(0) = c₁", size=12, color=NEG, bold=True, anchor="start"))
    svg.append(text(c_px + 60, c_py - 30, "= ∑ wᵢ · y[k+i]  (згортка)", size=11, color=MUTED, anchor="start"))
    
    # Нижня інформаційна плашка (зсунута нижче oy + 60 = 300)
    svg.append(rect(ox + 20, 310, 600, 70, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    card_text = [
        "Суть методу: замість чисельного ділення зашумлених точок, обчислюється МНК-поліном P(t).",
        "Коефіцієнт c₁ визначає швидкість (1-шу похідну), а 2·c₂ — прискорення (2-гу похідну) через FIR-згортку."
    ]
    svg.append(mtext(ox + 320, 335, card_text, size=11, color=INK, lh=1.4))
    
    svg.append('</svg>')
    return "\n".join(svg)

def draw_encoder_velocity_quantization():
    """Фігура 4: Обчислення швидкості з дискретних імпульсів енкодера: наївна різниця vs диференціатор з фільтром."""
    w, h = 760, 390
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%">' % (w, h)]
    
    svg.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    
    # Заголовок
    tb, _, _ = textbox(w/2, 26, "Швидкість із квантованого енкодера: наївна різниця Δx/Δt vs фільтрований диференціатор", size=13, bold=True, fill="#eef2f7", stroke="#4a5568")
    svg.append(tb)
    
    # Верхній графік: Квантоване положення енкодера x(t)
    p1_ox, p1_oy = 135, 150
    p1_w, p1_h = 360, 90
    
    svg.append(line(p1_ox, p1_oy, p1_ox + p1_w, p1_oy, color=LINE, sw=1.2))
    svg.append(line(p1_ox, p1_oy, p1_ox, p1_oy - p1_h, color=LINE, sw=1.2))
    svg.append(text(p1_ox - 15, p1_oy - p1_h/2, "Положення x(t)", size=11, color=INK, bold=True, anchor="end"))
    
    # Сходинки енкодера
    enc_steps = [(0, 0.0), (35, 0.0), (35, 15.0), (75, 15.0), (75, 30.0), 
                 (115, 30.0), (115, 45.0), (150, 45.0), (150, 60.0), 
                 (180, 60.0), (180, 75.0), (210, 75.0), (210, 90.0), (360, 90.0)]
    pts_enc = ["%.1f,%.1f" % (p1_ox + s[0], p1_oy - s[1]) for s in enc_steps]
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_enc), "#475569"))
    
    svg.append(line(p1_ox, p1_oy, p1_ox + p1_w, p1_oy - p1_h, color=NEG, sw=1.5, dash="4,4"))
    
    # Нижній графік: Оцінена швидкість v(t) = dx/dt
    p2_ox, p2_oy = 135, 335
    p2_w, p2_h = 360, 130
    
    svg.append(line(p2_ox, p2_oy, p2_ox + p2_w, p2_oy, color=LINE, sw=1.2))
    svg.append(line(p2_ox, p2_oy, p2_ox, p2_oy - p2_h, color=LINE, sw=1.2))
    svg.append(text(p2_ox - 15, p2_oy - p2_h/2, "Швидкість v(t)", size=11, color=INK, bold=True, anchor="end"))
    svg.append(text(p2_ox + p2_w + 10, p2_oy + 4, "Час t", size=11, color=INK, anchor="start"))
    
    naive_spikes = [
        (0, 0), (33, 0), (34, 110), (36, 110), (37, 0),
        (73, 0), (74, 110), (76, 110), (77, 0),
        (113, 0), (114, 110), (116, 110), (117, 0),
        (148, 0), (149, 110), (151, 110), (152, 0),
        (178, 0), (179, 110), (181, 110), (182, 0),
        (208, 0), (209, 110), (211, 110), (212, 0), (360, 0)
    ]
    pts_naive = ["%.1f,%.1f" % (p2_ox + s[0], p2_oy - s[1]) for s in naive_spikes]
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(pts_naive), POS))
    
    v_true_y = p2_oy - 45
    svg.append(line(p2_ox, v_true_y, p2_ox + p2_w, v_true_y, color=NEG, sw=1.8, dash="4,4"))
    
    pts_filt = []
    for step in range(201):
        tx = step * (p2_w / 200.0)
        if tx < 35:
            vy = 18 + 27 * (tx / 35.0)
        else:
            vy = 45 + 5.0 * math.sin(0.14 * tx)
        pts_filt.append("%.1f,%.1f" % (p2_ox + tx, p2_oy - vy))
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts_filt), FIELD))
    
    # Картка-легенда праворуч
    lx, ly = 515, 65
    svg.append(rect(lx, ly, 230, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    svg.append(text(lx + 115, ly + 22, "Порівняння методів", size=12, bold=True, color=INK))
    
    # 1. Положення
    svg.append(line(lx + 15, ly + 50, lx + 45, ly + 50, color="#475569", sw=2.2))
    svg.append(text(lx + 55, ly + 54, "Квантоване x(t) [тіки]", size=11, color=INK, anchor="start"))
    
    # 2. Справжня
    svg.append(line(lx + 15, ly + 82, lx + 45, ly + 82, color=NEG, sw=1.8, dash="4,4"))
    svg.append(text(lx + 55, ly + 86, "Справжня швидкість v(t)", size=11, color=NEG, bold=True, anchor="start"))
    
    # 3. Наївна
    svg.append(line(lx + 15, ly + 118, lx + 45, ly + 118, color=POS, sw=2.0))
    svg.append(text(lx + 55, ly + 122, "Наївна різниця Δx/Δt", size=11, color=POS, bold=True, anchor="start"))
    svg.append(text(lx + 55, ly + 138, "Руйнівні сплески шуму!", size=10, color=POS, anchor="start"))
    
    # 4. Фільтрована
    svg.append(line(lx + 15, ly + 172, lx + 45, ly + 172, color=FIELD, sw=2.8))
    svg.append(text(lx + 55, ly + 176, "Фільтр Савицького–Голея", size=11, color=FIELD, bold=True, anchor="start"))
    svg.append(text(lx + 55, ly + 192, "Гладка та стійка оцінка", size=10, color=FIELD, anchor="start"))
    
    svg.append(line(lx + 10, ly + 215, lx + 220, ly + 215, color="#e2e8f0", sw=1.0))
    conc = [
        "Наслідки наївної різниці:",
        "• Перегрів двигунів від D-члена PID",
        "• Механічні вібрації та свист",
        "• Втрата стійкості контуру"
    ]
    svg.append(mtext(lx + 115, ly + 235, conc, size=10, color="#b91c1c", lh=1.35))
    
    svg.append('</svg>')
    return "\n".join(svg)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    files = {
        'differentiation-dilemma-step.svg': draw_differentiation_dilemma(),
        'finite-difference-stencils.svg': draw_finite_difference_stencils(),
        'savitzky-golay-smoothing.svg': draw_savitzky_golay_fit(),
        'encoder-velocity-quantization.svg': draw_encoder_velocity_quantization()
    }
    
    for fname, content in files.items():
        fpath = os.path.join(img_dir, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated: {fpath}")

if __name__ == '__main__':
    main()
