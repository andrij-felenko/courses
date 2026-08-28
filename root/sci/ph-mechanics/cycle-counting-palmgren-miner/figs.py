# -*- coding: utf-8 -*-
"""Фігури до теми «Rainflow і правило Майнера».
Запуск: python figs.py  → генерує SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── 1. Діаграма Хейга (Haigh Diagram): криві Гудмана, Гербера, Зедерберга ────
def fig_haigh_diagram():
    W, H = 840, 480
    f = []
    
    # Координатні осі
    ox, oy = 280, 380  # початок координат (sigma_m = 0, sigma_a = 0)
    
    # Сітка та фон
    f.append(rect(40, 40, 760, 400, fill="#ffffff", stroke="#e5e7eb", sw=1.0, rx=4))
    
    # Осі
    f.append(arrow(60, oy, 770, oy, color=INK, sw=1.8))
    f.append(text(760, oy + 25, "Середнє напруження σ_m", size=13, color=INK, anchor="end", bold=True))
    
    f.append(arrow(ox, oy + 30, ox, 50, color=INK, sw=1.8))
    f.append(text(ox - 15, 60, "Амплітуда σ_a", size=13, color=INK, anchor="end", bold=True))
    
    # Характерні точки
    se_y = oy - 220
    sy_y = oy - 300
    sy_x = ox + 300
    sy_neg_x = ox - 180
    su_x = ox + 420
    
    # Заливка під Гудманом
    f.append(f'<polygon points="{ox},{oy} {ox},{se_y} {su_x},{oy}" fill="#f0fdf4" stroke="none"/>')
    
    # Лінія Зедерберга (Soderberg): від (ox, se_y) до (sy_x, oy)
    f.append(line(ox, se_y, sy_x, oy, color="#d97706", sw=2.2, dash="5,4"))
    f.append(text(ox + 90, oy - 185, "Зедерберг (консервативна, по σ_y)", size=11, color="#b45309", bold=True, anchor="start"))
    
    # Лінія Гудмана (Goodman): від (ox, se_y) до (su_x, oy)
    f.append(line(ox, se_y, su_x, oy, color=POS, sw=2.5))
    f.append(text(ox + 220, oy - 130, "Гудман (лінійна, по σ_u)", size=12, color=POS, bold=True, anchor="start"))
    
    # Крива Гербера (Gerber): парабола від (ox, se_y) до (su_x, oy)
    pts_gerber = []
    for i in range(21):
        xm = i / 20.0 * 420
        ya = 220 * (1.0 - (xm / 420.0) ** 2)
        pts_gerber.append(f"{ox + xm:.1f},{oy - ya:.1f}")
    d_gerber = "M " + " L ".join(pts_gerber)
    f.append(f'<path d="{d_gerber}" fill="none" stroke="{NEG}" stroke-width="2.2" stroke-dasharray="6,3"/>')
    f.append(text(ox + 260, oy - 175, "Гербер (параболічна, пластичні сталі)", size=11, color=NEG, bold=True, anchor="start"))
    
    # Лінія статичної плинності (Langer yield line): sigma_a + sigma_m = sigma_y
    f.append(line(ox, sy_y, sy_x, oy, color="#4b5563", sw=2.0, dash="3,3"))
    f.append(text(ox + 125, oy - 275, "Границя статичної плинності (σ_a + σ_m = σ_y)", size=11, color="#4b5563", italic=True, anchor="start"))
    
    # Позначки на осях
    # Межа витривалості sigma_e
    f.append(circle(ox, se_y, 4, fill=POS, stroke=INK, sw=1.2))
    f.append(text(ox - 10, se_y + 4, "σ_e (R = −1)", size=12, color=POS, bold=True, anchor="end"))
    
    # Межа плинності sigma_y на осі Y
    f.append(circle(ox, sy_y, 3.5, fill="#4b5563", stroke=INK, sw=1.2))
    f.append(text(ox - 10, sy_y + 4, "σ_y", size=12, color="#4b5563", bold=True, anchor="end"))
    
    # Межа плинності sigma_y на осі X
    f.append(circle(sy_x, oy, 4, fill="#4b5563", stroke=INK, sw=1.2))
    f.append(text(sy_x, oy + 20, "σ_y", size=12, color="#4b5563", bold=True, anchor="middle"))
    
    # Межа міцності sigma_u на осі X
    f.append(circle(su_x, oy, 4, fill=POS, stroke=INK, sw=1.2))
    f.append(text(su_x, oy + 20, "σ_u", size=12, color=POS, bold=True, anchor="middle"))
    
    # Стискальне напруження (ліва частина)
    f.append(text(ox - 90, oy - 60, "Стиск (σ_m < 0)\nпідвищує витривалість", size=11, color=FIELD, bold=True, anchor="middle"))
    f.append(line(ox - 160, oy - 220, ox, se_y, color=FIELD, sw=2.0, dash="4,4"))
    
    # Текстова плашка безпечної зони
    f.append(rect(ox + 40, oy - 70, 130, 40, fill="#dcfce7", stroke="#86efac", sw=1.2, rx=4))
    f.append(text(ox + 105, oy - 45, "Безпечна зона\n(нескінченний ресурс)", size=11, color="#166534", bold=True, anchor="middle"))
    
    # Зона руйнування
    f.append(text(ox + 340, oy - 240, "Зона втомного\nруйнування", size=13, color=POS, bold=True, anchor="middle"))
    
    return render(os.path.join(IMG, "haigh-diagram.svg"), W, H, *f, title="Діаграма Хейга: границі витривалості за різного середнього напруження")


# ── 2. Петлі пружнопластичного гістерезису (Rainflow hysteresis) ─────────────
def fig_rainflow_hysteresis():
    W, H = 880, 440
    f = []
    
    # Фон
    f.append(rect(20, 40, 840, 380, fill="#ffffff", stroke="#e5e7eb", sw=1.0, rx=4))
    
    # Ліва панель: часовий сигнал напруження sigma(t)
    lx0, ly0 = 60, 240
    f.append(text(220, 70, "Часовий сигнал напруження σ(t)", size=14, color=INK, bold=True, anchor="middle"))
    
    # Вісь часу та напруження
    f.append(arrow(lx0, ly0 + 130, lx0 + 340, ly0 + 130, color=INK, sw=1.5))
    f.append(text(lx0 + 335, ly0 + 150, "Час t", size=11, color=MUTED, anchor="end"))
    
    f.append(arrow(lx0, ly0 + 140, lx0, ly0 - 150, color=INK, sw=1.5))
    f.append(text(lx0 - 10, ly0 - 140, "Напруження σ", size=11, color=MUTED, anchor="end"))
    
    # Точки сигналу: 1 (min) -> 2 (sub-peak) -> 3 (sub-valley) -> 4 (sub-peak) -> 5 (max) -> 6 (min)
    pts_t = [
        (lx0 + 20, ly0 + 80, "1", "#2563eb"),
        (lx0 + 80, ly0 - 40, "2", "#d97706"),
        (lx0 + 130, ly0 + 20, "3", "#dc2626"),
        (lx0 + 180, ly0 - 20, "4", "#dc2626"),
        (lx0 + 240, ly0 - 110, "5", "#16a34a"),
        (lx0 + 310, ly0 + 80, "6", "#2563eb")
    ]
    
    # Лінія сигналу
    sig_d = "M " + " L ".join(f"{pt[0]},{pt[1]}" for pt in pts_t)
    f.append(f'<path d="{sig_d}" fill="none" stroke="{LINE}" stroke-width="2.2"/>')
    
    # Виділення малого циклу 2-3-4
    f.append(f'<path d="M {pts_t[1][0]},{pts_t[1][1]} L {pts_t[2][0]},{pts_t[2][1]} L {pts_t[3][0]},{pts_t[3][1]}" fill="none" stroke="#dc2626" stroke-width="2.8"/>')
    
    for x, y, lbl, col in pts_t:
        f.append(circle(x, y, 5, fill=col, stroke="#ffffff", sw=1.5))
        f.append(text(x, y - 12 if "2" in lbl or "4" in lbl or "5" in lbl else y + 20, lbl, size=12, color=col, bold=True, anchor="middle"))
        
    f.append(text(lx0 + 155, ly0 + 65, "Малий вкладений\nцикл 2–3–4", size=11, color="#dc2626", bold=True, anchor="middle"))
    f.append(text(lx0 + 160, ly0 + 115, "Великий макроцикл 1–5–6", size=11, color="#2563eb", bold=True, anchor="middle"))
    
    # Розділювач панелей
    f.append(line(430, 60, 430, 390, color="#e5e7eb", sw=1.5, dash="4,4"))
    
    # Права панель: петлі пружнопластичного гістерезису sigma-epsilon
    rx0, ry0 = 500, 240
    f.append(text(660, 70, "Петлі гістерезису в матеріалі (σ–ε)", size=14, color=INK, bold=True, anchor="middle"))
    
    # Осі деформація-напруження
    f.append(arrow(rx0, ry0, rx0 + 320, ry0, color=INK, sw=1.5))
    f.append(text(rx0 + 315, ry0 + 20, "Деформація ε", size=11, color=MUTED, anchor="end"))
    
    f.append(arrow(rx0 + 140, ry0 + 140, rx0 + 140, ry0 - 150, color=INK, sw=1.5))
    f.append(text(rx0 + 130, ry0 - 140, "Напруження σ", size=11, color=MUTED, anchor="end"))
    
    cx = rx0 + 140
    cy = ry0
    
    p1 = (cx - 90, cy + 80)
    p2 = (cx - 10, cy - 40)
    p3 = (cx - 50, cy + 20)
    p4 = (cx - 10, cy - 40)
    p5 = (cx + 100, cy - 110)
    p6 = (cx - 90, cy + 80)
    
    # 1 -> 2
    f.append(f'<path d="M {p1[0]},{p1[1]} Q {cx - 60},{cy - 10} {p2[0]},{p2[1]}" fill="none" stroke="#2563eb" stroke-width="2.2"/>')
    # 2 -> 3
    f.append(f'<path d="M {p2[0]},{p2[1]} Q {cx - 20},{cy} {p3[0]},{p3[1]}" fill="none" stroke="#dc2626" stroke-width="2.5"/>')
    # 3 -> 4
    f.append(f'<path d="M {p3[0]},{p3[1]} Q {cx - 40},{cy - 30} {p4[0]},{p4[1]}" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="4,3"/>')
    # 4 -> 5
    f.append(f'<path d="M {p4[0]},{p4[1]} Q {cx + 40},{cy - 80} {p5[0]},{p5[1]}" fill="none" stroke="#2563eb" stroke-width="2.2"/>')
    # 5 -> 6
    f.append(f'<path d="M {p5[0]},{p5[1]} Q {cx + 10},{cy + 40} {p6[0]},{p6[1]}" fill="none" stroke="#2563eb" stroke-width="2.2"/>')
    
    h_pts = [
        (p1[0], p1[1], "1", "#2563eb"),
        (p2[0], p2[1], "2, 4 (замикання)", "#d97706"),
        (p3[0], p3[1], "3", "#dc2626"),
        (p5[0], p5[1], "5", "#16a34a"),
        (p6[0], p6[1], "6", "#2563eb")
    ]
    for x, y, lbl, col in h_pts:
        f.append(circle(x, y, 5, fill=col, stroke="#ffffff", sw=1.5))
        if "2" in lbl:
            f.append(text(x - 10, y - 10, lbl, size=11, color=col, bold=True, anchor="end"))
        elif "5" in lbl:
            f.append(text(x + 10, y - 8, lbl, size=12, color=col, bold=True, anchor="start"))
        elif "3" in lbl:
            f.append(text(x - 10, y + 14, lbl, size=12, color=col, bold=True, anchor="end"))
        else:
            f.append(text(x - 12, y + 12, lbl, size=12, color=col, bold=True, anchor="end"))
            
    f.append(rect(cx - 30, cy + 60, 180, 48, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=4))
    f.append(text(cx + 60, cy + 80, "Петля 2–3–4 замкнулась!\nПам'ять матеріалу відновлено.", size=10.5, color="#991b1b", bold=True, anchor="middle"))

    return render(os.path.join(IMG, "rainflow-hysteresis.svg"), W, H, *f, title="Фізична сутність Rainflow: замикання петель пружнопластичного гістерезису")


# ── 3. Чотириточковий алгоритм Rainflow за ASTM E1049 ───────────────────────
def fig_rainflow_astm_steps():
    W, H = 860, 420
    f = []
    
    f.append(rect(20, 40, 820, 360, fill="#ffffff", stroke="#e5e7eb", sw=1.0, rx=4))
    
    # Панель 1: Стек реверсів A, B, C, D та вимірювання розмахів
    f.append(text(230, 70, "1. Стек реверсів та оцінка розмахів", size=13.5, color=INK, bold=True, anchor="middle"))
    
    x_base = 70
    y_base = 250
    
    pts = [
        (x_base + 30, y_base + 60, "A (10)"),
        (x_base + 100, y_base - 80, "B (80)"),
        (x_base + 170, y_base + 10, "C (35)"),
        (x_base + 240, y_base - 110, "D (95)")
    ]
    
    f.append(line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], color=LINE, sw=2.0))
    f.append(line(pts[1][0], pts[1][1], pts[2][0], pts[2][1], color="#dc2626", sw=2.6))
    f.append(line(pts[2][0], pts[2][1], pts[3][0], pts[3][1], color=LINE, sw=2.0))
    
    for px, py, lbl in pts:
        f.append(circle(px, py, 6, fill="#2563eb", stroke="#ffffff", sw=1.5))
        f.append(text(px, py - 12 if py < y_base else py + 20, lbl, size=11.5, color=INK, bold=True, anchor="middle"))
        
    # X1 = |B - A|
    f.append(line(pts[0][0] - 15, pts[0][1], pts[0][0] - 15, pts[1][1], color="#4b5563", sw=1.5))
    f.append(arrow(pts[0][0] - 15, (pts[0][1] + pts[1][1])/2 + 10, pts[0][0] - 15, pts[1][1], color="#4b5563", sw=1.5))
    f.append(arrow(pts[0][0] - 15, (pts[0][1] + pts[1][1])/2 - 10, pts[0][0] - 15, pts[0][1], color="#4b5563", sw=1.5))
    f.append(text(pts[0][0] - 25, (pts[0][1] + pts[1][1])/2 + 4, "X₁ = 70", size=11, color="#4b5563", anchor="end", bold=True))
    
    # Y = |C - B|
    f.append(line(pts[2][0] + 15, pts[2][1], pts[2][0] + 15, pts[1][1], color="#dc2626", sw=1.8))
    f.append(arrow(pts[2][0] + 15, (pts[2][1] + pts[1][1])/2 + 10, pts[2][0] + 15, pts[1][1], color="#dc2626", sw=1.8))
    f.append(arrow(pts[2][0] + 15, (pts[2][1] + pts[1][1])/2 - 10, pts[2][0] + 15, pts[2][1], color="#dc2626", sw=1.8))
    f.append(text(pts[2][0] + 25, (pts[2][1] + pts[1][1])/2 + 4, "Y = 45", size=12, color="#dc2626", anchor="start", bold=True))
    
    # X2 = |D - C|
    f.append(line(pts[3][0] + 15, pts[3][1], pts[3][0] + 15, pts[2][1], color="#4b5563", sw=1.5))
    f.append(arrow(pts[3][0] + 15, (pts[3][1] + pts[2][1])/2 - 10, pts[3][0] + 15, pts[3][1], color="#4b5563", sw=1.5))
    f.append(arrow(pts[3][0] + 15, (pts[3][1] + pts[2][1])/2 + 10, pts[3][0] + 15, pts[2][1], color="#4b5563", sw=1.5))
    f.append(text(pts[3][0] + 25, (pts[3][1] + pts[2][1])/2 + 4, "X₂ = 60", size=11, color="#4b5563", anchor="start", bold=True))
    
    # Умова
    f.append(rect(60, 335, 300, 48, fill="#eff6ff", stroke="#bfdbfe", sw=1.2, rx=4))
    f.append(text(210, 355, "Умова ASTM: Y ≤ X₁ та Y ≤ X₂", size=11.5, color="#1e40af", bold=True, anchor="middle"))
    f.append(text(210, 372, "45 ≤ 70 і 45 ≤ 60 → ІСТИНА (цикл замкнено)", size=11, color="#16a34a", bold=True, anchor="middle"))
    
    # Розділювач
    f.append(line(420, 60, 420, 380, color="#e5e7eb", sw=1.5, dash="4,4"))
    
    # Панель 2: Вилучення циклу B-C та змикання A-D
    f.append(text(640, 70, "2. Вилучення циклу та змикання стеку", size=13.5, color=INK, bold=True, anchor="middle"))
    
    x_r = 480
    
    f.append(rect(x_r + 20, 110, 280, 65, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=6))
    f.append(text(x_r + 160, 132, "Вилучено повний цикл B–C:", size=12, color="#991b1b", bold=True, anchor="middle"))
    f.append(text(x_r + 160, 155, "Розмах Δσ = 45 | Середнє σ_m = (80+35)/2 = 57.5", size=11.5, color="#dc2626", bold=True, anchor="middle"))
    
    # Стрілка переходу вниз
    f.append(arrow(x_r + 160, 185, x_r + 160, 215, color="#4b5563", sw=2.0))
    f.append(text(x_r + 175, 203, "вилучити B, C", size=11, color="#4b5563", anchor="start"))
    
    pts_new = [
        (x_r + 50, y_base + 60, "A (10)"),
        (x_r + 250, y_base - 110, "D (95)")
    ]
    
    f.append(line(pts_new[0][0], pts_new[0][1], pts_new[1][0], pts_new[1][1], color="#16a34a", sw=2.5))
    
    for px, py, lbl in pts_new:
        f.append(circle(px, py, 6, fill="#16a34a", stroke="#ffffff", sw=1.5))
        f.append(text(px, py - 12 if py < y_base else py + 20, lbl, size=11.5, color=INK, bold=True, anchor="middle"))
        
    f.append(rect(x_r + 30, 335, 260, 48, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=4))
    f.append(text(x_r + 160, 355, "Точки A і D зімкнулись у стеку", size=11.5, color="#166534", bold=True, anchor="middle"))
    f.append(text(x_r + 160, 372, "Перевірка триває для наступної точки E...", size=11, color="#15803d", italic=True, anchor="middle"))

    return render(os.path.join(IMG, "rainflow-astm-steps.svg"), W, H, *f, title="Чотириточковий алгоритм Rainflow за ASTM E1049: виявлення циклу та редукція стеку")


# ── 4. Накопичення пошкоджень за Пальмгреном — Майнером ─────────────────────
def fig_palmgren_miner_accumulation():
    W, H = 880, 430
    f = []
    
    f.append(rect(20, 40, 840, 370, fill="#ffffff", stroke="#e5e7eb", sw=1.0, rx=4))
    
    # Блок 1: Гістограма циклів (Бін розмахів)
    b1_x, b1_y = 40, 85
    f.append(rect(b1_x, b1_y, 230, 245, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    f.append(text(b1_x + 115, b1_y + 25, "1. Спектр циклів Rainflow", size=12.5, color=INK, bold=True, anchor="middle"))
    
    bins = [
        ("Δσ₁ = 50 МПа", "n₁ = 80 000", 40, "#93c5fd"),
        ("Δσ₂ = 120 МПа", "n₂ = 12 000", 85, "#60a5fa"),
        ("Δσ₃ = 200 МПа", "n₃ = 1 500", 135, "#2563eb"),
        ("Δσ₄ = 280 МПа", "n₄ = 80", 185, "#1d4ed8")
    ]
    for i, (s_lbl, n_lbl, h_bar, col) in enumerate(bins):
        yy = b1_y + 55 + i * 42
        f.append(text(b1_x + 15, yy + 14, s_lbl, size=10.5, color=INK, anchor="start"))
        f.append(text(b1_x + 130, yy + 14, n_lbl, size=10.5, color=MUTED, anchor="start"))
        f.append(rect(b1_x + 15, yy + 20, h_bar, 10, fill=col, stroke="none", rx=2))
        
    # Стрілка 1 -> 2
    f.append(arrow(b1_x + 235, b1_y + 120, b1_x + 275, b1_y + 120, color="#4b5563", sw=2.0))
    f.append(text(b1_x + 255, b1_y + 108, "S–N", size=11, color="#4b5563", bold=True, anchor="middle"))
    
    # Блок 2: Граничний ресурс N_i за кривою Веллера
    b2_x, b2_y = 285, 85
    f.append(rect(b2_x, b2_y, 235, 245, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    f.append(text(b2_x + 117, b2_y + 25, "2. Граничний ресурс N_i", size=12.5, color=INK, bold=True, anchor="middle"))
    
    res_list = [
        ("N₁ = 5.0 · 10⁷", "d₁ = 0.0016"),
        ("N₂ = 4.5 · 10⁵", "d₂ = 0.0267"),
        ("N₃ = 1.8 · 10⁴", "d₃ = 0.0833"),
        ("N₄ = 850", "d₄ = 0.0941")
    ]
    for i, (n_val, d_val) in enumerate(res_list):
        yy = b2_y + 55 + i * 42
        f.append(text(b2_x + 15, yy + 14, n_val, size=11, color="#1e40af", bold=True, anchor="start"))
        f.append(text(b2_x + 130, yy + 14, f"d = n/N = {d_val.split('= ')[1]}", size=10.5, color=POS, bold=True, anchor="start"))
        f.append(line(b2_x + 15, yy + 28, b2_x + 220, yy + 28, color="#e2e8f0", sw=1.0))
        
    # Стрілка 2 -> 3
    f.append(arrow(b2_x + 240, b2_y + 120, b2_x + 280, b2_y + 120, color="#4b5563", sw=2.0))
    f.append(text(b2_x + 260, b2_y + 108, "∑", size=13, color="#4b5563", bold=True, anchor="middle"))
    
    # Блок 3: Сумарне накопичення шкоди D
    b3_x, b3_y = 575, 85
    f.append(rect(b3_x, b3_y, 260, 245, fill="#fff7ed", stroke="#fdba74", sw=1.4, rx=6))
    f.append(text(b3_x + 130, b3_y + 25, "3. Накопичення шкоди D", size=12.5, color="#9a3412", bold=True, anchor="middle"))
    
    # Стовпчик накопичення
    bar_x = b3_x + 30
    bar_y = b3_y + 50
    bar_w = 35
    bar_h = 120
    
    # Контур стовпчика D
    f.append(rect(bar_x, bar_y, bar_w, bar_h, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=3))
    
    # Секції накопиченої шкоди (загальна висота 25px з 120px)
    h_d1 = 25 * (0.0016 / 0.2057)
    h_d2 = 25 * (0.0267 / 0.2057)
    h_d3 = 25 * (0.0833 / 0.2057)
    h_d4 = 25 * (0.0941 / 0.2057)
    
    curr_y = bar_y + bar_h
    curr_y -= h_d1
    f.append(rect(bar_x, curr_y, bar_w, h_d1, fill="#93c5fd", stroke="none"))
    curr_y -= h_d2
    f.append(rect(bar_x, curr_y, bar_w, h_d2, fill="#60a5fa", stroke="none"))
    curr_y -= h_d3
    f.append(rect(bar_x, curr_y, bar_w, h_d3, fill="#2563eb", stroke="none"))
    curr_y -= h_d4
    f.append(rect(bar_x, curr_y, bar_w, h_d4, fill="#1d4ed8", stroke="none"))
    
    # Межа D = 1.0
    f.append(line(bar_x - 8, bar_y, bar_x + bar_w + 8, bar_y, color=POS, sw=2.0, dash="4,3"))
    f.append(text(bar_x + bar_w + 12, bar_y + 4, "D = 1.0 (Злам)", size=11, color=POS, bold=True, anchor="start"))
    
    # Поточне значення D_блок
    f.append(text(bar_x + bar_w + 12, curr_y + 10, "D = 0.206 (20.6%)", size=11, color="#1e40af", bold=True, anchor="start"))
    
    # Прогноз ресурсу (розташовано нижче стовпчика, без накладання!)
    f.append(rect(b3_x + 15, b3_y + 185, 230, 48, fill="#ffffff", stroke="#fdba74", sw=1.0, rx=4))
    f.append(text(b3_x + 130, b3_y + 203, "Прогноз ресурсу деталі:", size=10.5, color=MUTED, anchor="middle"))
    f.append(text(b3_x + 130, b3_y + 221, "N_блоків = 1 / D_блок ≈ 4.85 блоків", size=11.5, color="#9a3412", bold=True, anchor="middle"))
    
    # Підсумковий висновок внизу
    f.append(rect(40, 345, 795, 45, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=4))
    f.append(text(437, 372, "Рідкісні високоамплітудні цикли (d₄) вносять левову частку пошкодження попри малу кількість!", size=12, color=INK, bold=True, anchor="middle"))

    return render(os.path.join(IMG, "palmgren-miner-accumulation.svg"), W, H, *f, title="Лінійна гіпотеза Пальмгрена — Майнера: розрахунок сумарного пошкодження D")


if __name__ == "__main__":
    fig_haigh_diagram()
    fig_rainflow_hysteresis()
    fig_rainflow_astm_steps()
    fig_palmgren_miner_accumulation()
    print("Всі 4 фігури успішно згенеровано у ./img/")
