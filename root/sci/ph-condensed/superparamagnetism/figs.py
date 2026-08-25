# -*- coding: utf-8 -*-
"""Фігури до теми «Суперпарамагнетизм та суперпарамагнітна межа».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Перехід до однодоменності та межа суперпарамагнетизму ─────────────
def fig_single_domain_critical_size():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 25, "Залежність стану магнітної наночастинки від її діаметра D", size=15, bold=True, color=INK))

    x_zero = 80
    x_sp = 260
    x_crit = 500
    x_max = 700
    y_top = 55
    y_bot = 350

    # Області станів
    f.append(rect(x_zero, y_top, x_sp - x_zero, y_bot - y_top, fill="#fef2f2", stroke="none"))
    f.append(rect(x_sp, y_top, x_crit - x_sp, y_bot - y_top, fill="#f0fdf4", stroke="none"))
    f.append(rect(x_crit, y_top, x_max - x_crit, y_bot - y_top, fill="#eff6ff", stroke="none"))

    # Пунктирні лінії розділу
    f.append(path_svg(f"M {x_sp} {y_top} L {x_sp} {y_bot}", stroke="#dc2626", sw=2, dash="4,4"))
    f.append(path_svg(f"M {x_crit} {y_top} L {x_crit} {y_bot}", stroke="#2563eb", sw=2, dash="4,4"))

    # Заголовки областей
    f.append(text((x_zero + x_sp) / 2, y_top + 20, "Суперпарамагнітна", size=12, bold=True, color="#991b1b"))
    f.append(text((x_zero + x_sp) / 2, y_top + 36, "область (D < D_sp)", size=11, color="#991b1b"))

    f.append(text((x_sp + x_crit) / 2, y_top + 20, "Заблокована однодоменна", size=12, bold=True, color="#166534"))
    f.append(text((x_sp + x_crit) / 2, y_top + 36, "область (D_sp < D < D_crit)", size=11, color="#166534"))

    f.append(text((x_crit + x_max) / 2, y_top + 20, "Багатодоменна", size=12, bold=True, color="#1e40af"))
    f.append(text((x_crit + x_max) / 2, y_top + 36, "область (D > D_crit)", size=11, color="#1e40af"))

    # Осі координат
    f.append(arrow(x_zero, y_bot, x_max + 25, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 35, y_bot + 4, "D", size=13, bold=True, italic=True, color=INK))
    f.append(arrow(x_zero, y_bot, x_zero, y_top - 10, color=INK, sw=1.5))
    f.append(text(x_zero - 25, y_top - 5, "E, H_c", size=12, bold=True, color=INK))

    # Мітки по осі X
    f.append(text(x_sp, y_bot + 18, "D_sp (~10 нм)", size=11, bold=True, color="#dc2626"))
    f.append(text(x_crit, y_bot + 18, "D_crit (~50 нм)", size=11, bold=True, color="#2563eb"))

    # Крива коерцитивної сили H_c(D)
    pts_hc = []
    # D < D_sp: H_c = 0
    for i in range(51):
        x = x_zero + (i / 50.0) * (x_sp - x_zero)
        pts_hc.append((x, y_bot))
    # D_sp <= D <= D_crit: H_c зростає від 0 до H_c_max
    y_hc_max = y_top + 80
    for i in range(1, 101):
        t = i / 100.0
        x = x_sp + t * (x_crit - x_sp)
        val = 1.0 - (1.0 - t)**1.5
        y = y_bot - val * (y_bot - y_hc_max)
        pts_hc.append((x, y))
    # D > D_crit: H_c спадає як 1/D
    for i in range(1, 101):
        t = i / 100.0
        x = x_crit + t * (x_max - x_crit)
        val = 1.0 / (1.0 + 2.0 * t)
        y = y_bot - val * (y_bot - y_hc_max)
        pts_hc.append((x, y))

    d_hc = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_hc)
    f.append(path_svg(d_hc, stroke="#059669", sw=3))
    f.append(text(x_crit - 60, y_hc_max - 15, "Коерцитивна сила H_c(D)", size=12, bold=True, color="#059669"))

    # Криві енергій: E_demag (~ D^3) та E_dw (~ D^2)
    pts_demag = []
    pts_dw = []
    for i in range(101):
        t = i / 100.0
        x = x_zero + t * (x_max - x_zero)
        # demag
        y_dem = y_bot - (t**2.5) * (y_bot - (y_top + 60))
        pts_demag.append((x, y_dem))
        # dw
        y_w = y_bot - (t**1.6) * (y_bot - (y_top + 100))
        pts_dw.append((x, y_w))

    d_demag = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_demag)
    d_dw = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_dw)

    f.append(path_svg(d_demag, stroke="#dc2626", sw=1.8, dash="6,3"))
    f.append(text(x_max - 100, y_top + 70, "E_demag ~ D^3", size=10, bold=True, color="#dc2626"))

    f.append(path_svg(d_dw, stroke="#2563eb", sw=1.8, dash="3,3"))
    f.append(text(x_max - 100, y_top + 115, "E_dw ~ D^2", size=10, bold=True, color="#2563eb"))

    # Схематичні малюнки частинок
    # Суперпарамагнітна частинка
    f.append(circle(x_zero + 40, y_bot - 60, 16, fill="#fca5a5", stroke="#dc2626", sw=1.5))
    f.append(arrow(x_zero + 40, y_bot - 50, x_zero + 40, y_bot - 72, color="#991b1b", sw=2))

    # Однодоменна заблокована
    f.append(circle((x_sp + x_crit) / 2, y_bot - 80, 24, fill="#86efac", stroke="#16a34a", sw=1.5))
    f.append(arrow((x_sp + x_crit) / 2, y_bot - 62, (x_sp + x_crit) / 2, y_bot - 98, color="#15803d", sw=2.5))

    # Багатодоменна
    cx, cy = (x_crit + x_max) / 2, y_bot - 90
    f.append(circle(cx, cy, 32, fill="#93c5fd", stroke="#2563eb", sw=1.5))
    f.append(line(cx - 32, cy, cx + 32, cy, color="#1e40af", sw=1.5))
    f.append(line(cx, cy - 32, cx, cy + 32, color="#1e40af", sw=1.5))
    f.append(arrow(cx - 16, cy - 16, cx - 16, cy - 28, color="#1e40af", sw=1.5))
    f.append(arrow(cx + 16, cy - 16, cx + 16, cy - 4, color="#1e40af", sw=1.5))
    f.append(arrow(cx - 16, cy + 16, cx - 28, cy + 16, color="#1e40af", sw=1.5))
    f.append(arrow(cx + 16, cy + 16, cx + 28, cy + 16, color="#1e40af", sw=1.5))

    f.append(text(W / 2, H - 12, "При D < D_sp теплова енергія k_B T перевищує бар'єр анізотропії K_u V, і коерцитивна сила зникає (H_c = 0)", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'single-domain-critical-size.svg'), W, H, "\n".join(f))

# ── Фігура 2: Енергетичний бар'єр анізотропії та термофлуктуації ────────────────
def fig_energy_barrier_neel_relaxation():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 25, "Енергетичний профіль одновісної анізотропії E(θ) = K_u V sin²(θ)", size=15, bold=True, color=INK))

    x_left = 100
    x_mid = 380
    x_right = 660
    y_bot = 320
    y_top = 90

    # Осі
    f.append(arrow(x_left - 40, y_bot, x_right + 50, y_bot, color=INK, sw=1.5))
    f.append(text(x_right + 60, y_bot + 4, "θ", size=13, bold=True, italic=True, color=INK))
    f.append(arrow(x_left, y_bot, x_left, y_top - 30, color=INK, sw=1.5))
    f.append(text(x_left - 20, y_top - 25, "E(θ)", size=12, bold=True, color=INK))

    # Потенціальна яма E(θ) = K_u V sin^2(θ)
    pts_e = []
    for i in range(181):
        angle_rad = (i / 180.0) * math.pi
        x = x_left + (i / 180.0) * (x_right - x_left)
        sin_val = math.sin(angle_rad)
        y = y_bot - (sin_val**2) * (y_bot - y_top)
        pts_e.append((x, y))

    d_e = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_e)
    f.append(path_svg(d_e, stroke="#2563eb", sw=3))

    # Лінії мінімумів та максимуму
    f.append(line(x_left, y_top, x_right, y_top, color="#94a3b8", sw=1, dash="3,3"))
    f.append(line(x_mid, y_top, x_mid, y_bot, color="#dc2626", sw=1.5, dash="4,4"))

    # Стрілка висоти бар'єра Delta E = K_u V
    f.append(arrow(x_mid + 40, y_bot, x_mid + 40, y_top, color="#dc2626", sw=2))
    f.append(arrow(x_mid + 40, y_top, x_mid + 40, y_bot, color="#dc2626", sw=2))
    f.append(rect(x_mid + 50, (y_top + y_bot) / 2 - 14, 150, 28, fill="#ffffff", stroke="#dc2626", sw=1.5, rx=4))
    f.append(text(x_mid + 125, (y_top + y_bot) / 2 + 4, "ΔE = K_u V", size=12, bold=True, color="#dc2626"))

    # Лінія теплової енергії k_B T
    y_kbt = y_bot - 0.25 * (y_bot - y_top)
    f.append(line(x_left, y_kbt, x_right, y_kbt, color="#d97706", sw=2, dash="6,3"))
    f.append(text(x_right - 60, y_kbt - 10, "k_B T (теплова енергія)", size=11, bold=True, color="#d97706"))

    # Хвиляста стрілка термофлуктуацій (перескок через бар'єр)
    d_jump = f"M {x_left + 40} {y_bot - 40} Q {x_mid} {y_top - 40} {x_right - 40} {y_bot - 40}"
    f.append(path_svg(d_jump, stroke="#ea580c", sw=2.5, dash="4,2"))
    f.append(arrow(x_right - 50, y_bot - 45, x_right - 35, y_bot - 35, color="#ea580c", sw=2.5))
    f.append(text(x_mid, y_top - 45, "Термофлуктуаційний перескок τ = τ_0 exp(K_u V / k_B T)", size=11, bold=True, color="#ea580c"))

    # Спінові вектора у мінімумах
    f.append(arrow(x_left, y_bot - 10, x_left, y_bot - 65, color="#16a34a", sw=3))
    f.append(text(x_left, y_bot + 20, "θ = 0° (+M_z)", size=11, bold=True, color="#16a34a"))

    f.append(arrow(x_right, y_bot - 10, x_right, y_bot - 65, color="#16a34a", sw=3))
    f.append(text(x_right, y_bot + 20, "θ = 180° (-M_z)", size=11, bold=True, color="#16a34a"))

    f.append(text(x_mid, y_bot + 20, "θ = 90° (важка вісь)", size=11, color=MUTED))

    f.append(text(W / 2, H - 12, "Коли K_u V <= 25 k_B T, тепловий рух хаотично перевертає макроспін між станами +M_z та -M_z", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'energy-barrier-neel-relaxation.svg'), W, H, "\n".join(f))

# ── Фігура 3: Гістерезис та безгістерезисна крива Ланжевена ───────────────────────
def fig_superparamagnetic_hysteresis_blocking():
    W, H = 760, 380
    f = []

    f.append(text(W / 2, 25, "Порівняння кривих намагнічування M(H) заблокованого та суперпарамагнітного станів", size=14, bold=True, color=INK))

    bw, bh = 330, 280
    y_top = 50

    # Ліва панель: T < T_B (Заблокований стан, феромагнітний гістерезис)
    x1 = 30
    f.append(rect(x1, y_top, bw, bh, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(x1 + bw / 2, y_top + 20, "T < T_B (Заблокований стан, τ >> τ_meas)", size=11, bold=True, color="#1e40af"))

    cx1, cy1 = x1 + bw / 2, y_top + bh / 2 + 10
    f.append(arrow(cx1 - 130, cy1, cx1 + 130, cy1, color=INK, sw=1.2))
    f.append(text(cx1 + 140, cy1 + 4, "H", size=11, bold=True, italic=True, color=INK))
    f.append(arrow(cx1, cy1 + 110, cx1, cy1 - 110, color=INK, sw=1.2))
    f.append(text(cx1 - 18, cy1 - 105, "M", size=11, bold=True, color=INK))

    # Петля гістерезису
    pts_hyst_top = []
    pts_hyst_bot = []
    for i in range(-120, 121):
        h = i / 100.0
        # Верхня гілка (від +H_sat до -H_sat)
        m_top = math.tanh(h + 0.4)
        x_t = cx1 + h * 90
        y_t = cy1 - m_top * 80
        pts_hyst_top.append((x_t, y_t))
        # Нижня гілка
        m_bot = math.tanh(h - 0.4)
        y_b = cy1 - m_bot * 80
        pts_hyst_bot.append((x_t, y_b))

    d_hyst = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_hyst_top) + " L " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in reversed(pts_hyst_bot)) + " Z"
    f.append(path_svg(d_hyst, fill="#eff6ff", stroke="#2563eb", sw=2))

    # Позначення H_c та M_r
    f.append(circle(cx1 - 0.4 * 90, cy1, 4, fill="#dc2626", stroke="none"))
    f.append(text(cx1 - 0.4 * 90 - 15, cy1 + 16, "-H_c", size=10, bold=True, color="#dc2626"))
    f.append(circle(cx1 + 0.4 * 90, cy1, 4, fill="#dc2626", stroke="none"))
    f.append(text(cx1 + 0.4 * 90 + 15, cy1 + 16, "+H_c", size=10, bold=True, color="#dc2626"))

    f.append(circle(cx1, cy1 - math.tanh(0.4) * 80, 4, fill="#059669", stroke="none"))
    f.append(text(cx1 + 18, cy1 - math.tanh(0.4) * 80, "M_r", size=10, bold=True, color="#059669"))

    f.append(mtext(cx1, y_top + bh - 20, "Коерцитивна сила H_c > 0\nЄ остаточна намагніченість M_r", size=10, color=MUTED))

    # Права панель: T > T_B (Суперпарамагнітний стан, безгістерезисний)
    x2 = 400
    f.append(rect(x2, y_top, bw, bh, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(x2 + bw / 2, y_top + 20, "T > T_B (Суперпарамагнетизм, τ << τ_meas)", size=11, bold=True, color="#c2410c"))

    cx2, cy2 = x2 + bw / 2, y_top + bh / 2 + 10
    f.append(arrow(cx2 - 130, cy2, cx2 + 130, cy2, color=INK, sw=1.2))
    f.append(text(cx2 + 140, cy2 + 4, "H", size=11, bold=True, italic=True, color=INK))
    f.append(arrow(cx2, cy2 + 110, cx2, cy2 - 110, color=INK, sw=1.2))
    f.append(text(cx2 - 18, cy2 - 105, "M", size=11, bold=True, color=INK))

    # Безгістерезисна функція Ланжевена L(x)
    pts_lang = []
    for i in range(-120, 121):
        h = i / 100.0
        # Langevin function L(x) approx tanh(x*1.2)
        m_l = math.tanh(h * 1.5)
        x_l = cx2 + h * 90
        y_l = cy2 - m_l * 80
        pts_lang.append((x_l, y_l))

    d_lang = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_lang)
    f.append(path_svg(d_lang, stroke="#ea580c", sw=2.5))

    f.append(circle(cx2, cy2, 5, fill="#dc2626", stroke="none"))
    f.append(text(cx2 + 45, cy2 + 18, "H_c = 0, M_r = 0", size=10, bold=True, color="#dc2626"))
    f.append(text(cx2 + 65, cy2 - 50, "M(H) = M_s L(μH / k_B T)", size=10, bold=True, color="#ea580c"))

    f.append(mtext(cx2, y_top + bh - 20, "Гістерезис повністю відсутній!\nВисока початкова сприйнятливість", size=10, color=MUTED))

    f.append(text(W / 2, H - 12, "У суперпарамагнітному стані теплові флуктуації усереднюють намагніченість до нуля за відсутності поля", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'superparamagnetic-hysteresis-blocking.svg'), W, H, "\n".join(f))

# ── Фігура 4: Магнітна тріада та технології подолання межі (HAMR/PMR) ───────────
def fig_magnetic_recording_trilemma():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 25, "Магнітна тріада запису та концепція HAMR для подолання межі", size=15, bold=True, color=INK))

    # Схема трикутника тріади (ліворуч)
    tx, ty = 200, 210
    r_tri = 110

    p1 = (tx, ty - r_tri)
    p2 = (tx - r_tri * math.cos(math.pi / 6), ty + r_tri * math.sin(math.pi / 6))
    p3 = (tx + r_tri * math.cos(math.pi / 6), ty + r_tri * math.sin(math.pi / 6))

    f.append(path_svg(f"M {p1[0]} {p1[1]} L {p2[0]} {p2[1]} L {p3[0]} {p3[1]} Z", fill="#f8fafc", stroke="#64748b", sw=2, dash="4,4"))

    # Вершини тріади
    # 1. Щільність (малий V)
    f.append(rect(p1[0] - 80, p1[1] - 30, 160, 36, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=5))
    f.append(text(p1[0], p1[1] - 12, "Висока щільність", size=11, bold=True, color="#1e40af"))
    f.append(text(p1[0], p1[1] + 2, "Малий об'єм V (SNR)", size=9, color="#1e40af"))

    # 2. Термічна стабільність (K_u V >= 60 k_B T)
    f.append(rect(p2[0] - 85, p2[1] - 5, 170, 40, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=5))
    f.append(text(p2[0], p2[1] + 12, "Термічна стабільність", size=11, bold=True, color="#166534"))
    f.append(text(p2[0], p2[1] + 26, "K_u V >= 60 k_B T", size=10, bold=True, color="#166534"))

    # 3. Записуваність (H_c <= H_head)
    f.append(rect(p3[0] - 85, p3[1] - 5, 170, 40, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=5))
    f.append(text(p3[0], p3[1] + 12, "Записуваність біта", size=11, bold=True, color="#c2410c"))
    f.append(text(p3[0], p3[1] + 26, "H_c <= H_head (~2.4 Тл)", size=10, bold=True, color="#c2410c"))

    f.append(text(tx, ty + 10, "Магнітна", size=12, bold=True, color="#dc2626"))
    f.append(text(tx, ty + 26, "тріада запису", size=12, bold=True, color="#dc2626"))

    # Права частина: Схема HAMR (Heat-Assisted Magnetic Recording)
    hx = 450
    hy = 70
    hw, hh = 280, 290
    f.append(rect(hx, hy, hw, hh, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    f.append(text(hx + hw / 2, hy + 22, "Розв'язок: Технологія HAMR", size=13, bold=True, color="#991b1b"))

    # Графік H_c(T) для FePt матеріалу
    gx0, gy0 = hx + 40, hy + 240
    gx_max, gy_max = hx + 240, hy + 65

    f.append(arrow(gx0, gy0, gx_max + 15, gy0, color=INK, sw=1.2))
    f.append(text(gx_max + 20, gy0 + 4, "T", size=11, bold=True, italic=True, color=INK))
    f.append(arrow(gx0, gy0, gx0, gy_max - 10, color=INK, sw=1.2))
    f.append(text(gx0 - 15, gy_max - 10, "H_c", size=11, bold=True, color=INK))

    # Спадання коерцитивного поля з температурою
    pts_hamr = []
    for i in range(101):
        t = i / 100.0
        x = gx0 + t * (gx_max - gx0)
        # H_c drops near Curie point T_C
        val = math.sqrt(max(0.0, 1.0 - t**1.4))
        y = gy0 - val * (gy0 - gy_max)
        pts_hamr.append((x, y))

    d_hamr = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_hamr)
    f.append(path_svg(d_hamr, stroke="#dc2626", sw=2.5))

    # Поле голівки H_head
    y_hhead = gy0 - 0.3 * (gy0 - gy_max)
    f.append(line(gx0, y_hhead, gx_max, y_hhead, color="#ea580c", sw=1.5, dash="4,3"))
    f.append(text(gx0 + 60, y_hhead - 8, "Поле голівки H_head", size=10, bold=True, color="#ea580c"))

    # Позначення кімнатної T_room та T_write (поблизу T_C)
    x_troom = gx0 + 0.15 * (gx_max - gx0)
    x_twrite = gx0 + 0.85 * (gx_max - gx0)

    f.append(line(x_troom, gy0, x_troom, gy_max, color="#2563eb", sw=1, dash="2,2"))
    f.append(text(x_troom, gy0 + 16, "T_room", size=10, bold=True, color="#2563eb"))
    f.append(text(x_troom, gy_max + 20, "H_c >> H_head", size=9, bold=True, color="#2563eb"))
    f.append(text(x_troom, gy_max + 32, "(Стабільність)", size=9, color="#2563eb"))

    f.append(line(x_twrite, gy0, x_twrite, gy_max, color="#dc2626", sw=1, dash="2,2"))
    f.append(text(x_twrite, gy0 + 16, "T_write ~ T_C", size=10, bold=True, color="#dc2626"))
    f.append(text(x_twrite, gy0 - 35, "H_c < H_head", size=9, bold=True, color="#dc2626"))
    f.append(text(x_twrite, gy0 - 23, "(Запис лазером!)", size=9, color="#dc2626"))

    # Стрілка нагріву
    f.append(arrow(x_troom + 15, gy0 - 45, x_twrite - 15, gy0 - 45, color="#e11d48", sw=2))
    f.append(text((x_troom + x_twrite) / 2, gy0 - 55, "Лазерний нагрів (<1 нс)", size=9, bold=True, color="#e11d48"))

    f.append(text(W / 2, H - 12, "HAMR локально нагріває носій з високим K_u до T_C, тимчасово зменшуючи H_c для запису біта", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'magnetic-recording-trilemma.svg'), W, H, "\n".join(f))

def main():
    fig_single_domain_critical_size()
    fig_energy_barrier_neel_relaxation()
    fig_superparamagnetic_hysteresis_blocking()
    fig_magnetic_recording_trilemma()
    print("Фігури суперпарамагнетизму успішно згенеровано у ./img/")

if __name__ == '__main__':
    main()
