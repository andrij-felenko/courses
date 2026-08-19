# -*- coding: utf-8 -*-
"""Фігури до теми «Радар із синтезованою апертурою та інтерферометрія» (SAR/InSAR).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (scripts/svgkit.py).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

C_BLUE   = "#2457d6"
C_RED    = "#c0392b"
C_GREEN  = "#27ae60"
C_PURPLE = "#8e44ad"
C_ORANGE = "#d35400"
C_DARK   = "#1a1a1a"
C_MUTED  = "#6b7280"
C_BG_BOX = "#f8fafc"
C_BORDER = "#cbd5e1"

def poly(pts, color=LINE, sw=1.5, dash=None, fill="none"):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, color, sw, da)

# ── 1. Геометрія SAR та парадокс азимутальної роздільності ─────────────────────
def fig_sar_geometry():
    W, H = 960, 520
    f = []

    # Заголовок зверху
    f.append(text(W / 2, 28, "Реальна апертура (RAR) проти синтезованої (SAR)", size=16, bold=True))

    # Ліва панель: Реальна апертура (RAR)
    f.append(fitbox(20, 50, 440, 450, "", fill=C_BG_BOX, stroke=C_BORDER, rx=8))
    f.append(text(240, 75, "Реальна апертура (RAR)", size=15, bold=True, color=C_RED))
    f.append(text(240, 95, "Роздільність погіршується з відстанню: δ_az = R · λ / D", size=12, color=C_MUTED))

    # Промінь RAR
    f.append(poly([(240, 144), (90, 420), (390, 420)], color=C_RED, sw=1.5, dash="4,4", fill="#fef2f2"))
    f.append(line(240, 144, 240, 420, color=C_MUTED, sw=1.2, dash="3,3"))
    f.append(arrow(240, 200, 200, 200, color=C_RED, sw=1.2))
    f.append(arrow(240, 200, 280, 200, color=C_RED, sw=1.2))
    f.append(text(240, 190, "θ = λ / D", size=11, bold=True, color=C_RED))

    # Радарний носій ліворуч (поверх променя)
    f.append(rect(200, 120, 80, 24, fill="#fee2e2", stroke=C_RED, sw=2, rx=4))
    f.append(text(240, 136, "Антена D", size=12, bold=True, color=C_RED))

    # Земна поверхня
    f.append(line(50, 420, 430, 420, color=C_DARK, sw=2.5))
    f.append(text(70, 440, "Земля", size=11, color=C_MUTED))

    # Пляма на землі
    f.append(line(90, 420, 390, 420, color=C_RED, sw=4))
    f.append(arrow(240, 455, 90, 455, color=C_RED, sw=1.5))
    f.append(arrow(240, 455, 390, 455, color=C_RED, sw=1.5))
    f.append(text(240, 475, "Пляма на землі: δ_az = 12 км (при R = 800 км)", size=12, bold=True, color=C_RED))
    f.append(text(240, 493, "Неможливо розрізнити деталі рельєфу", size=11, color=C_MUTED))

    # Права панель: Синтезована апертура (SAR)
    f.append(fitbox(490, 50, 450, 450, "", fill=C_BG_BOX, stroke=C_BORDER, rx=8))
    f.append(text(715, 75, "Синтезована апертура (SAR)", size=15, bold=True, color=C_BLUE))
    f.append(text(715, 95, "Роздільність не залежить від R та λ: δ_az = D / 2", size=12, color=C_MUTED))

    # Ціль на землі
    target_x, target_y = 710, 420

    # Промені когерентного спостереження від крайніх точок до цілі
    f.append(poly([(560, 132), (target_x, target_y), (860, 132)], color=C_BLUE, sw=1.5, dash="4,4", fill="#eff6ff"))
    f.append(line(710, 132, target_x, target_y, color=C_MUTED, sw=1.2, dash="3,3"))
    f.append(text(725, 270, "Дальність R", size=11, color=C_MUTED))

    # Траєкторія руху носія
    f.append(line(520, 132, 910, 132, color=C_BLUE, sw=2, dash="5,5"))
    f.append(arrow(850, 132, 915, 132, color=C_BLUE, sw=2))
    f.append(text(880, 118, "Швидкість v", size=11, bold=True, color=C_BLUE))

    # Позиції носія (синтез)
    for pos_x in [560, 620, 680, 740, 800, 860]:
        f.append(circle(pos_x, 132, 5, fill="#dbeafe", stroke=C_BLUE, sw=1.5))

    # Синтезована довжина L_sa
    f.append(rect(550, 118, 320, 28, fill="none", stroke=C_BLUE, sw=1.5, rx=4))
    f.append(text(710, 108, "Синтезована апертура L_sa = R · θ_beam = R · λ / D", size=11, bold=True, color=C_BLUE))

    # Земна лінія та точкова ціль
    f.append(line(520, 420, 910, 420, color=C_DARK, sw=2.5))
    f.append(circle(target_x, target_y, 6, fill=C_GREEN, stroke=C_DARK, sw=2))
    f.append(text(target_x, 442, "Точкова ціль P", size=12, bold=True, color=C_GREEN))

    # Фокусована роздільність
    f.append(line(target_x - 20, 420, target_x + 20, 420, color=C_GREEN, sw=5))
    f.append(arrow(target_x, 470, target_x - 20, 470, color=C_GREEN, sw=1.5))
    f.append(arrow(target_x, 470, target_x + 20, 470, color=C_GREEN, sw=1.5))
    f.append(text(target_x, 488, "Сфокусована роздільність: δ_az = D / 2 = 1.0 м", size=12, bold=True, color=C_GREEN))

    return render(os.path.join(IMG, "sar-geometry-resolution.svg"), W, H, *f)

# ── 2. Стиснення імпульсів за дальністю (Chirp Matched Filter) ─────────────────
def fig_chirp_matched_filter():
    W, H = 960, 460
    f = []

    f.append(text(W / 2, 26, "Стиснення імпульсів за дальністю (ЛЧМ-сигнал та узгоджений фільтр)", size=16, bold=True))

    # Блок 1: Випромінений ЛЧМ-імпульс
    f.append(fitbox(20, 50, 280, 380, "", fill=C_BG_BOX, stroke=C_BORDER, rx=8))
    f.append(text(160, 75, "1. Зондувальний ЛЧМ (Chirp)", size=13, bold=True, color=C_DARK))
    f.append(text(160, 95, "Тривалий імпульс T_p, смуга B", size=11, color=C_MUTED))

    # Вісь часу імпульсу
    f.append(line(40, 200, 280, 200, color=C_MUTED, sw=1.2))
    f.append(arrow(260, 200, 285, 200, color=C_MUTED, sw=1.2))
    f.append(text(280, 215, "t", size=11, italic=True, color=C_MUTED))

    # Намалюємо графік ЛЧМ сигналу (частота зростає)
    chirp_pts = []
    for i in range(200):
        t_norm = i / 200.0
        val = math.sin(2 * math.pi * (1.0 + 8.0 * t_norm) * t_norm) * 55.0
        chirp_pts.append((50 + i * 1.1, 200 - val))
    f.append(poly(chirp_pts, color=C_BLUE, sw=1.8))

    # Підписи тривалості
    f.append(line(50, 275, 270, 275, color=C_BLUE, sw=1.5))
    f.append(line(50, 270, 50, 280, color=C_BLUE, sw=1.5))
    f.append(line(270, 270, 270, 280, color=C_BLUE, sw=1.5))
    f.append(text(160, 295, "Тривалість T_p = 40 мкс", size=12, bold=True, color=C_BLUE))
    f.append(text(160, 315, "Енергія велика, пікова потужність мала", size=10, color=C_MUTED))
    f.append(text(160, 345, "Спектральна смуга: B = 100 МГц", size=11, bold=True, color=C_DARK))
    f.append(text(160, 365, "База сигналу: B · T_p = 4000", size=11, color=C_PURPLE))

    # Стрілка переходу 1 -> 2
    f.append(arrow(305, 240, 335, 240, color=C_DARK, sw=2))

    # Блок 2: Узгоджений фільтр
    f.append(fitbox(340, 130, 270, 220, "", fill="#f3f4f6", stroke=C_DARK, sw=1.5, rx=8))
    f.append(text(475, 155, "2. Узгоджена фільтрація", size=13, bold=True, color=C_DARK))
    f.append(text(475, 180, "H(f) = S*(f) · e^{-j 2π f T_p}", size=12, bold=True, color=C_PURPLE))
    f.append(text(475, 205, "Згортка з інвертованим", size=11, color=C_MUTED))
    f.append(text(475, 220, "комплексно-спряженим імпульсом", size=11, color=C_MUTED))
    f.append(rect(360, 245, 230, 80, fill="#ffffff", stroke=C_BORDER, rx=6))
    f.append(text(475, 268, "Компенсація квадратичної фази", size=11, bold=True, color=C_BLUE))
    f.append(text(475, 290, "Когерентне додавання всіх", size=11, color=C_MUTED))
    f.append(text(475, 308, "спектральних гармонік у піку", size=11, color=C_MUTED))

    # Стрілка переходу 2 -> 3
    f.append(arrow(615, 240, 645, 240, color=C_DARK, sw=2))

    # Блок 3: Стиснутий імпульс (Sinc)
    f.append(fitbox(650, 50, 290, 380, "", fill=C_BG_BOX, stroke=C_BORDER, rx=8))
    f.append(text(795, 75, "3. Стиснутий відгук (sinc)", size=13, bold=True, color=C_GREEN))
    f.append(text(795, 95, "Гострий пік роздільної здатності", size=11, color=C_MUTED))

    # Вісь для sinc
    f.append(line(670, 250, 920, 250, color=C_MUTED, sw=1.2))
    f.append(arrow(900, 250, 925, 250, color=C_MUTED, sw=1.2))
    f.append(text(920, 265, "t", size=11, italic=True, color=C_MUTED))

    # Графік функції sinc
    sinc_pts = []
    for i in range(220):
        t_val = (i - 110) / 14.0
        if abs(t_val) < 1e-4:
            s = 1.0
        else:
            s = math.sin(math.pi * t_val) / (math.pi * t_val)
        y_val = 250 - s * 110.0
        sinc_pts.append((680 + i * 1.05, y_val))
    f.append(poly(sinc_pts, color=C_GREEN, sw=2.2))

    # Позначення ширини піка
    f.append(line(788, 250, 788, 140, color=C_RED, sw=1.2, dash="3,3"))
    f.append(line(802, 250, 802, 140, color=C_RED, sw=1.2, dash="3,3"))
    f.append(arrow(780, 160, 788, 160, color=C_RED, sw=1.2))
    f.append(arrow(810, 160, 802, 160, color=C_RED, sw=1.2))
    f.append(text(795, 130, "τ_eff = 1 / B", size=11, bold=True, color=C_RED))

    # Параметри після стиснення
    f.append(text(795, 300, "Ефективна тривалість: 10 нс", size=12, bold=True, color=C_GREEN))
    f.append(text(795, 325, "Роздільність: δ_r = c / (2B) = 1.5 м", size=12, bold=True, color=C_DARK))
    f.append(text(795, 350, "Підсилення обробки: +36 дБ", size=11, bold=True, color=C_PURPLE))
    f.append(text(795, 370, "10 · log10(B · T_p)", size=10, color=C_MUTED))

    return render(os.path.join(IMG, "chirp-matched-filter.svg"), W, H, *f)

# ── 3. Інтерферометрична геометрія (InSAR Baseline) ───────────────────────────
def fig_insar_geometry():
    W, H = 960, 540
    f = []

    f.append(text(W / 2, 28, "Геометрія інтерферометричної зйомки (InSAR) та фазовий трикутник", size=16, bold=True))

    # Координатні центри супутників S1 і S2
    s1_x, s1_y = 200, 110
    s2_x, s2_y = 350, 65

    # Ціль на рельєфі
    target_x, target_y = 780, 440

    # Рельєф (земна поверхня з пагорбом)
    terrain_pts = [(450, 480), (550, 475), (660, 465), (780, 440), (840, 455), (930, 480)]
    f.append(poly(terrain_pts, color="#15803d", sw=3, fill="none"))
    f.append(line(450, 480, 930, 480, color=C_MUTED, sw=1.2, dash="4,4"))
    f.append(text(890, 500, "Опорний еліпсоїд (h = 0)", size=11, color=C_MUTED))

    # Висота цілі h
    f.append(line(target_x, target_y, target_x, 480, color=C_RED, sw=2))
    f.append(arrow(target_x + 20, 480, target_x + 20, target_y, color=C_RED, sw=1.5))
    f.append(text(target_x + 45, 460, "Висота h", size=12, bold=True, color=C_RED))

    # Вектор просторової бази B
    f.append(line(s1_x, s1_y, s2_x, s2_y, color=C_PURPLE, sw=3))
    f.append(arrow(s1_x, s1_y, s2_x, s2_y, color=C_PURPLE, sw=2.5))
    f.append(text(275, 75, "База B", size=13, bold=True, color=C_PURPLE))

    # Промені до цілі R1 і R2
    f.append(line(s1_x, s1_y, target_x, target_y, color=C_BLUE, sw=2))
    f.append(line(s2_x, s2_y, target_x, target_y, color=C_ORANGE, sw=2))
    f.append(text(460, 300, "Похила дальність R₁", size=12, bold=True, color=C_BLUE))
    f.append(text(600, 240, "Дальність R₂", size=12, bold=True, color=C_ORANGE))

    # Кут візування theta біля S1
    f.append(line(s1_x, s1_y, s1_x, s1_y + 120, color=C_MUTED, sw=1.2, dash="4,4"))
    f.append(text(s1_x + 18, s1_y + 80, "θ", size=14, bold=True, color=C_DARK))

    # Перпендикулярна база B_perp
    dx = target_x - s1_x
    dy = target_y - s1_y
    r1_len = math.hypot(dx, dy)
    ux, uy = dx / r1_len, dy / r1_len

    bx = s2_x - s1_x
    by = s2_y - s1_y
    b_par = bx * ux + by * uy
    proj_x = s1_x + ux * b_par
    proj_y = s1_y + uy * b_par

    f.append(line(proj_x, proj_y, s2_x, s2_y, color=C_RED, sw=2.5, dash="3,3"))
    f.append(text(s2_x - 55, s2_y + 35, "B_⊥ = B·cos(θ−α)", size=11, bold=True, color=C_RED))

    # Різниця ходу Delta R біля S2
    r2_len = math.hypot(target_x - s2_x, target_y - s2_y)
    u2x, u2y = (target_x - s2_x) / r2_len, (target_y - s2_y) / r2_len
    q_x = target_x - u2x * r1_len
    q_y = target_y - u2y * r1_len

    f.append(circle(q_x, q_y, 4, fill=C_RED, stroke=C_DARK, sw=1.5))
    f.append(line(s2_x, s2_y, q_x, q_y, color=C_RED, sw=4))
    f.append(text(s2_x + 40, s2_y + 65, "ΔR = R₁ − R₂", size=11, bold=True, color=C_RED))

    # Супутник 1 (Master) - поверх ліній
    f.append(rect(s1_x - 55, s1_y - 20, 110, 40, fill="#dbeafe", stroke=C_BLUE, sw=2, rx=6))
    f.append(text(s1_x, s1_y + 5, "S₁ (Головний)", size=11, bold=True, color=C_BLUE))

    # Супутник 2 (Slave) - поверх ліній
    f.append(rect(s2_x - 55, s2_y - 20, 110, 40, fill="#fef3c7", stroke=C_ORANGE, sw=2, rx=6))
    f.append(text(s2_x, s2_y + 5, "S₂ (Ведений)", size=11, bold=True, color=C_ORANGE))

    # Інформаційний блок із формулами праворуч/знизу
    f.append(fitbox(20, 310, 380, 200, "", fill=C_BG_BOX, stroke=C_BORDER, rx=8))
    f.append(text(210, 335, "Інтерферометрична фаза:", size=13, bold=True, color=C_DARK))
    f.append(text(210, 360, "Δφ = φ₁ − φ₂ = −(4π / λ) · ΔR", size=13, bold=True, color=C_PURPLE))
    f.append(text(210, 390, "Топографічна чутливість:", size=12, bold=True, color=C_BLUE))
    f.append(text(210, 412, "Δφ_topo = −(4π / λ) · (B_⊥ / (R · sin θ)) · h", size=12, color=C_BLUE))
    f.append(text(210, 445, "Висота невизначеності (фазовий цикл 2π):", size=11, bold=True, color=C_DARK))
    f.append(text(210, 467, "h_2π = (λ · R · sin θ) / (2 · B_⊥)", size=12, bold=True, color=C_RED))
    f.append(text(210, 492, "Зміщення поверхні: Δφ_disp = −(4π / λ) · Δr", size=11, bold=True, color=C_GREEN))

    return render(os.path.join(IMG, "insar-geometry.svg"), W, H, *f)

# ── 4. Фазове розгортання та сингулярні залишки (Phase Unwrapping & Residues) ──
def fig_phase_unwrapping():
    W, H = 960, 480
    f = []

    f.append(text(W / 2, 26, "Фазове розгортання (Phase Unwrapping) та сингулярні залишки (Residues)", size=16, bold=True))

    # Ліва панель: Згорнута фаза проти неперервної
    f.append(fitbox(20, 50, 420, 405, "", fill=C_BG_BOX, stroke=C_BORDER, rx=8))
    f.append(text(230, 75, "1. Згортання фази за модулем 2π", size=14, bold=True, color=C_DARK))
    f.append(text(230, 95, "Інтерферограма фіксує лише ψ = W(φ) ∈ [−π, +π)", size=11, color=C_MUTED))

    # Графік дійсної фази (пряма лінія)
    f.append(line(50, 240, 400, 240, color=C_MUTED, sw=1.2)) # вісь 0
    f.append(line(50, 160, 400, 160, color=C_MUTED, sw=1.0, dash="3,3")) # +pi
    f.append(line(50, 320, 400, 320, color=C_MUTED, sw=1.0, dash="3,3")) # -pi
    f.append(text(40, 164, "+π", size=11, bold=True, color=C_MUTED, anchor="end"))
    f.append(text(40, 244, "0", size=11, bold=True, color=C_MUTED, anchor="end"))
    f.append(text(40, 324, "−π", size=11, bold=True, color=C_MUTED, anchor="end"))

    # Дійсна неперервна фаза (синя пунктирна лінія, що росте)
    f.append(line(60, 340, 390, 130, color=C_BLUE, sw=2, dash="4,4"))
    f.append(text(340, 120, "Істинна фаза φ(x)", size=11, bold=True, color=C_BLUE))

    # Згорнута пилкоподібна фаза (червона лінія)
    sawtooth = [
        (60, 340), (120, 160),
        (120, 320), (230, 160),
        (230, 320), (340, 160),
        (340, 320), (390, 250)
    ]
    f.append(poly(sawtooth[0:2], color=C_RED, sw=2.5))
    f.append(poly(sawtooth[2:4], color=C_RED, sw=2.5))
    f.append(poly(sawtooth[4:6], color=C_RED, sw=2.5))
    f.append(poly(sawtooth[6:8], color=C_RED, sw=2.5))
    # стрибки 2pi
    f.append(line(120, 160, 120, 320, color=C_RED, sw=1.2, dash="2,2"))
    f.append(line(230, 160, 230, 320, color=C_RED, sw=1.2, dash="2,2"))
    f.append(line(340, 160, 340, 320, color=C_RED, sw=1.2, dash="2,2"))
    f.append(text(190, 360, "Інтерференційні смуги (fringe pattern)", size=12, bold=True, color=C_RED))
    f.append(text(230, 420, "Задача розгортання: відновити неперервний профіль φ = ψ + 2π·k", size=11, bold=True, color=C_DARK))

    # Права панель: Сингулярні залишки та розрізи Гольдштейна (Branch Cuts)
    f.append(fitbox(470, 50, 470, 405, "", fill=C_BG_BOX, stroke=C_BORDER, rx=8))
    f.append(text(705, 75, "2. Сингулярні залишки та розрізи (Branch Cuts)", size=14, bold=True, color=C_DARK))
    f.append(text(705, 95, "Теорема про контурний інтеграл: ∮ ∇ψ · dr = 2π · q (q ∈ {−1, 0, +1})", size=11, color=C_MUTED))

    # Сітка пікселів 2D
    grid_x, grid_y = 520, 130
    step = 55
    for i in range(7):
        f.append(line(grid_x + i * step, grid_y, grid_x + i * step, grid_y + 4 * step, color="#e2e8f0", sw=1.5))
    for j in range(5):
        f.append(line(grid_x, grid_y + j * step, grid_x + 6 * step, grid_y + j * step, color="#e2e8f0", sw=1.5))

    pos_res_x = grid_x + 2 * step
    pos_res_y = grid_y + 2 * step
    neg_res_x = grid_x + 4 * step
    neg_res_y = grid_y + 2 * step

    # Контур інтегрування навколо +1 (помилковий шлях)
    loop_pts = [
        (pos_res_x - 22, pos_res_y - 22), (pos_res_x + 22, pos_res_y - 22),
        (pos_res_x + 22, pos_res_y + 22), (pos_res_x - 22, pos_res_y + 22),
        (pos_res_x - 22, pos_res_y - 22)
    ]
    f.append(poly(loop_pts, color=C_RED, sw=1.5, dash="3,3"))
    f.append(arrow(pos_res_x, pos_res_y - 22, pos_res_x + 10, pos_res_y - 22, color=C_RED, sw=1.5))
    f.append(text(pos_res_x, pos_res_y - 32, "∮ = +2π (Помилка!)", size=10, bold=True, color=C_RED))

    # Лінія розрізу (Branch Cut) між +1 та -1
    f.append(line(pos_res_x + 14, pos_res_y, neg_res_x - 14, neg_res_y, color=C_PURPLE, sw=4))

    # Дозволений шлях інтегрування в обхід бар'єра
    valid_path = [
        (grid_x + step, grid_y + 3 * step + 20),
        (grid_x + step, grid_y + step / 2),
        (grid_x + 5 * step, grid_y + step / 2),
        (grid_x + 5 * step, grid_y + 3 * step + 20)
    ]
    f.append(poly(valid_path, color=C_GREEN, sw=2.5))
    f.append(arrow(grid_x + 3 * step, grid_y + step / 2, grid_x + 3.5 * step, grid_y + step / 2, color=C_GREEN, sw=2))
    f.append(text(grid_x + 3 * step, grid_y + step / 2 - 10, "Коректний шлях інтегрування", size=11, bold=True, color=C_GREEN))

    # Напис на бар'єрі Гольдштейна (із білим непрозорим фоном, щоб не перетинати сітку)
    f.append(rect(grid_x + 3 * step - 60, pos_res_y - 28, 120, 20, fill="#ffffff", stroke=C_PURPLE, sw=1, rx=4))
    f.append(text(grid_x + 3 * step, pos_res_y - 14, "Бар'єр Гольдштейна", size=11, bold=True, color=C_PURPLE))

    # Кружечки залишків поверх сітки
    f.append(circle(pos_res_x, pos_res_y, 14, fill="#fee2e2", stroke=C_RED, sw=2))
    f.append(text(pos_res_x, pos_res_y + 4, "+1", size=12, bold=True, color=C_RED))

    f.append(circle(neg_res_x, neg_res_y, 14, fill="#dbeafe", stroke=C_BLUE, sw=2))
    f.append(text(neg_res_x, neg_res_y + 4, "−1", size=12, bold=True, color=C_BLUE))

    f.append(text(705, 385, "Алгоритм Гольдштейна з'єднує заряди розрізами", size=12, bold=True, color=C_DARK))
    f.append(text(705, 407, "Запобігає поширенню помилок розгортання на все зображення", size=11, color=C_MUTED))
    f.append(text(705, 427, "Застосовують також Minimum Cost Flow (MCF) та метод найменших квадратів", size=10, color=C_MUTED))

    return render(os.path.join(IMG, "phase-unwrapping-residues.svg"), W, H, *f)

def main():
    print("Генерація фігур...")
    fig_sar_geometry()
    fig_chirp_matched_filter()
    fig_insar_geometry()
    fig_phase_unwrapping()
    print("Готово!")

if __name__ == "__main__":
    main()
