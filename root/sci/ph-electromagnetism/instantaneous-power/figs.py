# -*- coding: utf-8 -*-
"""Фігури до теми «Миттєва та середня потужність».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_V = "#2457d6"      # Напруга v(t) - синій
COLOR_I = "#27ae60"      # Струм i(t) - зелений
COLOR_P = "#c0392b"      # Миттєва потужність p(t) - червоний
COLOR_PA = "#8e44ad"     # Активна складова pa(t) - пурпуровий
COLOR_PQ = "#d35400"     # Реактивна складова pq(t) - помаранчевий
COLOR_AVG = "#7f8c8d"    # Середнє значення P - сірий
COLOR_NEG = "#e74c3c"    # Зона повернення енергії

def path_element(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    st = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{st}/>'

# ── Фігура 1: Потужність на чисто активному навантаженні (R) ─────────────────
def fig_instantaneous_power_resistive():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Миттєва потужність на резистивному навантаженні (зсув фаз φ = 0)", size=16, bold=True))

    x0, y0 = 70, 220
    x_max = 680
    w_px = x_max - x0
    amp_v = 70
    amp_i = 50
    amp_p = 100

    # Осі
    f.append(line(x0 - 20, y0, x_max + 20, y0, color=LINE, sw=1.5))
    f.append(text(x_max + 30, y0 + 4, "ωt", size=13, bold=True, color=INK))

    f.append(line(x0, 45, x0, 350, color=LINE, sw=1.5))
    f.append(text(x0, 36, "v, i, p", size=13, bold=True, color=INK))

    # Позначки фаз (0, π, 2π, 3π, 4π)
    ticks = [(0, "0"), (math.pi, "π"), (math.pi*2, "2π"), (math.pi*3, "3π"), (math.pi*4, "4π")]
    for rad, label in ticks:
        px = x0 + (rad / (4 * math.pi)) * w_px
        f.append(line(px, y0 - 6, px, y0 + 6, color=LINE, sw=1.2))
        f.append(text(px, y0 + 22, label, size=11, color=MUTED))
        f.append(line(px, 50, px, 330, color="#f1f5f9", sw=1, dash="2,2"))

    # Лінія середньої потужності P
    y_p_avg = y0 - amp_p / 2
    f.append(line(x0, y_p_avg, x_max, y_p_avg, color=COLOR_AVG, sw=1.5, dash="4,4"))
    f.append(text(x0 - 32, y_p_avg + 4, "P = V·I", size=11, color=COLOR_AVG, bold=True))

    # Побудова v(t), i(t), p(t)
    pts_v, pts_i, pts_p = [], [], []
    steps = 200
    for i in range(steps + 1):
        t = (i / steps) * (4 * math.pi)
        px = x0 + (t / (4 * math.pi)) * w_px
        
        v = math.cos(t)
        i_val = math.cos(t)
        p_val = v * i_val  # cos^2(t) = 0.5 * (1 + cos(2t))
        
        py_v = y0 - amp_v * v
        py_i = y0 - amp_i * i_val
        py_p = y0 - amp_p * p_val
        
        pts_v.append(f"{px:.1f},{py_v:.1f}")
        pts_i.append(f"{px:.1f},{py_i:.1f}")
        pts_p.append(f"{px:.1f},{py_p:.1f}")

    f.append(path_element("M " + " L ".join(pts_v), stroke=COLOR_V, sw=2.0, dash="5,3"))
    f.append(path_element("M " + " L ".join(pts_i), stroke=COLOR_I, sw=2.0, dash="3,3"))
    f.append(path_element("M " + " L ".join(pts_p), stroke=COLOR_P, sw=2.8))

    # Легенда
    f.append(rect(500, 48, 230, 95, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))
    f.append(line(510, 64, 535, 64, color=COLOR_V, sw=2.0, dash="5,3"))
    f.append(text(545, 68, "v(t) = Vm·cos(ωt)", size=11, color=COLOR_V, anchor="start", bold=True))

    f.append(line(510, 88, 535, 88, color=COLOR_I, sw=2.0, dash="3,3"))
    f.append(text(545, 92, "i(t) = Im·cos(ωt)", size=11, color=COLOR_I, anchor="start", bold=True))

    f.append(line(510, 112, 535, 112, color=COLOR_P, sw=2.8))
    f.append(text(545, 116, "p(t) = P·[1 + cos(2ωt)] ≥ 0", size=11, color=COLOR_P, anchor="start", bold=True))

    # Пояснювальний бокс
    b, w, h = textbox(W / 2, 365, "Потужність p(t) пульсує з подвійною частотою 2ω і завжди ≥ 0. Енергія тече лише від джерела до резистора.",
                      size=12, pad=7, fill="#fff5f5", stroke="#feb2b2", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "instantaneous-power-resistive.svg"), W, H, *f)


# ── Фігура 2: Потужність при наявності фазового зсуву (L або C) ───────────────
def fig_instantaneous_power_reactive():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Миттєва потужність при реактивному зсуві фаз (φ = 60°)", size=16, bold=True))

    x0, y0 = 70, 220
    x_max = 680
    w_px = x_max - x0
    amp_v = 70
    amp_i = 50
    amp_p = 90
    phi = math.pi / 3  # 60 градусів

    # Осі
    f.append(line(x0 - 20, y0, x_max + 20, y0, color=LINE, sw=1.5))
    f.append(text(x_max + 30, y0 + 4, "ωt", size=13, bold=True, color=INK))

    f.append(line(x0, 45, x0, 360, color=LINE, sw=1.5))
    f.append(text(x0, 36, "v, i, p", size=13, bold=True, color=INK))

    # Лінія середньої потужності P = V*I*cos(phi)
    p_avg_val = 0.5 * math.cos(phi)  # 0.5 * 0.5 = 0.25
    y_p_avg = y0 - amp_p * p_avg_val
    f.append(line(x0, y_p_avg, x_max, y_p_avg, color=COLOR_AVG, sw=1.5, dash="4,4"))
    f.append(text(x0 - 45, y_p_avg + 4, "P = V·I·cos φ", size=10, color=COLOR_AVG, bold=True))

    # Побудова повернення енергії (зафарбування від'ємної потужності)
    steps = 300
    pts_v, pts_i, pts_p = [], [], []
    neg_polys = []
    current_neg = []

    for i in range(steps + 1):
        t = (i / steps) * (4 * math.pi)
        px = x0 + (t / (4 * math.pi)) * w_px
        
        v = math.cos(t)
        i_val = math.cos(t - phi)
        p_val = v * i_val
        
        py_v = y0 - amp_v * v
        py_i = y0 - amp_i * i_val
        py_p = y0 - amp_p * p_val
        
        pts_v.append(f"{px:.1f},{py_v:.1f}")
        pts_i.append(f"{px:.1f},{py_i:.1f}")
        pts_p.append(f"{px:.1f},{py_p:.1f}")

        if p_val < 0:
            current_neg.append((px, py_p))
        else:
            if current_neg:
                # закрити полігон від'ємної зони
                poly_pts = [f"{current_neg[0][0]:.1f},{y0:.1f}"] + [f"{pt[0]:.1f},{pt[1]:.1f}" for pt in current_neg] + [f"{current_neg[-1][0]:.1f},{y0:.1f}"]
                neg_polys.append(" ".join(poly_pts))
                current_neg = []

    if current_neg:
        poly_pts = [f"{current_neg[0][0]:.1f},{y0:.1f}"] + [f"{pt[0]:.1f},{pt[1]:.1f}" for pt in current_neg] + [f"{current_neg[-1][0]:.1f},{y0:.1f}"]
        neg_polys.append(" ".join(poly_pts))

    for poly_d in neg_polys:
        f.append(f'<polygon points="{poly_d}" fill="#fecaca" opacity="0.7" stroke="none"/>')

    f.append(path_element("M " + " L ".join(pts_v), stroke=COLOR_V, sw=2.0, dash="5,3"))
    f.append(path_element("M " + " L ".join(pts_i), stroke=COLOR_I, sw=2.0, dash="3,3"))
    f.append(path_element("M " + " L ".join(pts_p), stroke=COLOR_P, sw=2.8))

    # Легенда
    f.append(rect(480, 48, 250, 105, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))
    f.append(line(490, 64, 515, 64, color=COLOR_V, sw=2.0, dash="5,3"))
    f.append(text(525, 68, "v(t) = Vm·cos(ωt)", size=11, color=COLOR_V, anchor="start", bold=True))

    f.append(line(490, 84, 515, 84, color=COLOR_I, sw=2.0, dash="3,3"))
    f.append(text(525, 88, "i(t) = Im·cos(ωt − 60°)", size=11, color=COLOR_I, anchor="start", bold=True))

    f.append(line(490, 104, 515, 104, color=COLOR_P, sw=2.8))
    f.append(text(525, 108, "p(t) = v(t)·i(t)", size=11, color=COLOR_P, anchor="start", bold=True))

    f.append(rect(490, 122, 16, 12, fill="#fecaca", stroke="#e74c3c", sw=1, rx=2))
    f.append(text(515, 132, "p(t) < 0: повернення енергії", size=10, color="#b91c1c", anchor="start", bold=True))

    # Пояснювальний бокс
    b, w, h = textbox(W / 2, 385, "Коли v(t) та i(t) мають протилежні знаки, миттєва потужність p(t) < 0 — енергія повертається з реактивного поля у джерело.",
                      size=12, pad=7, fill="#fff5f5", stroke="#feb2b2", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "instantaneous-power-reactive.svg"), W, H, *f)


# ── Фігура 3: Розклад миттєвої потужності на активну та реактивну складові ────
def fig_power_decomposition():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Розклад миттєвої потужності: p(t) = pa(t) + pq(t)", size=16, bold=True))

    x0, y0 = 70, 220
    x_max = 680
    w_px = x_max - x0
    amp_scale = 100

    phi = math.pi / 3  # 60 deg
    P_val = 0.5 * math.cos(phi)  # 0.25
    Q_val = 0.5 * math.sin(phi)  # ~0.433

    # Осі
    f.append(line(x0 - 20, y0, x_max + 20, y0, color=LINE, sw=1.5))
    f.append(text(x_max + 30, y0 + 4, "ωt", size=13, bold=True, color=INK))

    f.append(line(x0, 45, x0, 360, color=LINE, sw=1.5))
    f.append(text(x0, 36, "Потужність", size=13, bold=True, color=INK))

    # Нульовий рівень і рівень P
    f.append(line(x0, y0 - amp_scale * P_val, x_max, y0 - amp_scale * P_val, color=COLOR_AVG, sw=1.2, dash="4,4"))
    f.append(text(x0 - 32, y0 - amp_scale * P_val + 4, "P (активна)", size=10, color=COLOR_AVG, bold=True))

    pts_p, pts_pa, pts_pq = [], [], []
    steps = 200
    for i in range(steps + 1):
        t = (i / steps) * (4 * math.pi)
        px = x0 + (t / (4 * math.pi)) * w_px
        
        pa = P_val * (1 + math.cos(2 * t))
        pq = Q_val * math.sin(2 * t)
        p_total = pa + pq
        
        py_pa = y0 - amp_scale * pa
        py_pq = y0 - amp_scale * pq
        py_p = y0 - amp_scale * p_total
        
        pts_pa.append(f"{px:.1f},{py_pa:.1f}")
        pts_pq.append(f"{px:.1f},{py_pq:.1f}")
        pts_p.append(f"{px:.1f},{py_p:.1f}")

    f.append(path_element("M " + " L ".join(pts_pa), stroke=COLOR_PA, sw=2.2, dash="6,3"))
    f.append(path_element("M " + " L ".join(pts_pq), stroke=COLOR_PQ, sw=2.2, dash="3,3"))
    f.append(path_element("M " + " L ".join(pts_p), stroke=COLOR_P, sw=2.8))

    # Легенда
    f.append(rect(460, 48, 270, 105, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))
    f.append(line(470, 64, 495, 64, color=COLOR_PA, sw=2.2, dash="6,3"))
    f.append(text(505, 68, "pa(t) = P·[1 + cos(2ωt)] ≥ 0", size=11, color=COLOR_PA, anchor="start", bold=True))

    f.append(line(470, 88, 495, 88, color=COLOR_PQ, sw=2.2, dash="3,3"))
    f.append(text(505, 92, "pq(t) = Q·sin(2ωt) (середнє = 0)", size=11, color=COLOR_PQ, anchor="start", bold=True))

    f.append(line(470, 112, 495, 112, color=COLOR_P, sw=2.8))
    f.append(text(505, 116, "p(t) = pa(t) + pq(t) (сумарна)", size=11, color=COLOR_P, anchor="start", bold=True))

    # Пояснювальний бокс
    b, w, h = textbox(W / 2, 385, "Активна складова pa(t) передає незворотну енергію P. Реактивна pq(t) лише коливається навколо нуля з амплітудою Q.",
                      size=12, pad=7, fill="#f3e8ff", stroke="#d8b4fe", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "power-decomposition.svg"), W, H, *f)


# ── Фігура 4: Трикутник потужностей та комплексний простір ───────────────────
def fig_power_triangle():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Трикутник потужностей: зв'язок між P, Q, S та коефіцієнтом потужності cos φ", size=16, bold=True))

    # Ліва частина: Трикутник потужностей
    x_off = 100
    y_off = 250
    p_len = 260
    q_len = 150
    s_end_x = x_off + p_len
    s_end_y = y_off - q_len

    # Лінії трикутника
    # Катет P (Активна потужність)
    f.append(line(x_off, y_off, s_end_x, y_off, color=COLOR_PA, sw=3))
    f.append(text(x_off + p_len / 2, y_off + 25, "P = V·I·cos φ (Активна, Вт)", size=12, bold=True, color=COLOR_PA))

    # Катет Q (Реактивна потужність)
    f.append(line(s_end_x, y_off, s_end_x, s_end_y, color=COLOR_PQ, sw=3))
    f.append(text(s_end_x + 15, y_off - q_len / 2, "Q = V·I·sin φ (Реактивна, вар)", size=12, bold=True, color=COLOR_PQ, anchor="start"))

    # Гіпотенуза S (Повна потужність)
    f.append(line(x_off, y_off, s_end_x, s_end_y, color=COLOR_V, sw=3))
    f.append(text(x_off + p_len / 2 - 20, y_off - q_len / 2 - 15, "S = V·I (Повна, В·А)", size=12, bold=True, color=COLOR_V))

    # Кут phi (дуга)
    arc_d = f"M {x_off + 50},{y_off} A 50 50 0 0 0 {x_off + 43},{y_off - 25}"
    f.append(path_element(arc_d, stroke=INK, sw=1.8))
    f.append(text(x_off + 65, y_off - 12, "φ", size=14, bold=True, color=INK))

    # Прямий кут позначка
    f.append(line(s_end_x - 15, y_off, s_end_x - 15, y_off - 15, color=MUTED, sw=1.2))
    f.append(line(s_end_x - 15, y_off - 15, s_end_x, y_off - 15, color=MUTED, sw=1.2))

    # Права частина: Співвідношення та формули
    f.append(rect(450, 50, 270, 210, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(585, 75, "Основні формули", size=14, bold=True, color=INK))

    f.append(text(470, 110, "S² = P² + Q²", size=13, bold=True, color=INK, anchor="start"))
    f.append(text(470, 140, "S = Vrms · Irms", size=12, color=COLOR_V, anchor="start"))
    f.append(text(470, 170, "P = S · cos φ", size=12, color=COLOR_PA, anchor="start"))
    f.append(text(470, 200, "Q = S · sin φ", size=12, color=COLOR_PQ, anchor="start"))

    f.append(line(470, 218, 700, 218, color="#cbd5e1", sw=1))
    f.append(text(470, 242, "PF = cos φ = P / S", size=13, bold=True, color=COLOR_PA, anchor="start"))

    # Пояснювальний бокс
    b, w, h = textbox(W / 2, 340, "Коефіцієнт потужності PF = cos φ вимірює ефективність використання джерела.\nЧим більша реактивна потужність Q, тим більший струм потрібен для передачі того самого P.",
                      size=11, pad=6, fill="#f0f9ff", stroke="#bae6fd", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "power-triangle.svg"), W, H, *f)

if __name__ == "__main__":
    fig_instantaneous_power_resistive()
    fig_instantaneous_power_reactive()
    fig_power_decomposition()
    fig_power_triangle()
    print("Всі фігури успішно згенеровано у ./img/")
