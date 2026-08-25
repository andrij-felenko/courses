# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def ang(a):
    return math.radians(a)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Поляризаційний еліпс електричного поля
# ═══════════════════════════════════════════════════════════════════════════
def fig_polarization_ellipse():
    W, H = 680, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Геометрія поляризаційного еліпса електричного поля', 16, INK, 'middle', bold=True))

    cx, cy = 270, 220
    ax_a, ax_b = 150, 80  # півосі еліпса
    psi_deg = 30.0         # азимутальний кут ψ
    psi = ang(psi_deg)

    # Габаритний прямокутник (2E_0x × 2E_0y)
    ex0 = 160
    ey0 = 120
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="0" fill="#f8fafc" stroke="%s" stroke-width="1.2" stroke-dasharray="4,4"/>' %
             (cx - ex0, cy - ey0, 2 * ex0, 2 * ey0, MUTED))

    # Осі координат Ex та Ey
    f.append(arrow(cx - ex0 - 30, cy, cx + ex0 + 40, cy, color=INK, sw=1.5))
    f.append(arrow(cx, cy + ey0 + 30, cx, cy - ey0 - 40, color=INK, sw=1.5))
    f.append(text(cx + ex0 + 45, cy + 4, 'Eₓ', 14, INK, 'start', bold=True, italic=True))
    f.append(text(cx - 12, cy - ey0 - 44, 'Eᵧ', 14, INK, 'middle', bold=True, italic=True))

    # Пунктирні позначки E_0x та E_0y
    f.append(line(cx + ex0, cy, cx + ex0, cy + ey0, color=MUTED, sw=1, dash='2,2'))
    f.append(line(cx, cy - ey0, cx + ex0, cy - ey0, color=MUTED, sw=1, dash='2,2'))
    f.append(text(cx + ex0, cy + 18, 'E₀ₓ', 12, MUTED, 'middle', italic=True))
    f.append(text(cx - 18, cy - ey0 + 4, 'E₀ᵧ', 12, MUTED, 'end', italic=True))

    # Головні осі еліпса (нахилені під кутом ψ)
    cos_p, sin_p = math.cos(psi), math.sin(psi)
    # Велика піввісь a
    ax_x1, ax_y1 = cx - (ax_a + 25) * cos_p, cy + (ax_a + 25) * sin_p
    ax_x2, ax_y2 = cx + (ax_a + 25) * cos_p, cy - (ax_a + 25) * sin_p
    f.append(line(ax_x1, ax_y1, ax_x2, ax_y2, color=FIELD, sw=1.2, dash='5,3'))
    f.append(text(ax_x2 + 10, ax_y2 - 6, 'головна вісь a', 11, FIELD, 'start', bold=True))

    # Мала піввісь b
    bx_x1, bx_y1 = cx - (ax_b + 15) * sin_p, cy - (ax_b + 15) * cos_p
    bx_x2, bx_y2 = cx + (ax_b + 15) * sin_p, cy + (ax_b + 15) * cos_p
    f.append(line(bx_x1, bx_y1, bx_x2, bx_y2, color=FIELD, sw=1.2, dash='5,3'))
    f.append(text(bx_x1 - 10, bx_y1 - 6, 'мала вісь b', 11, FIELD, 'end', bold=True))

    # Побудова самого еліпса через параметричні точки
    pts = []
    N = 120
    for i in range(N + 1):
        t = (2 * math.pi * i) / N
        x_prime = ax_a * math.cos(t)
        y_prime = ax_b * math.sin(t)
        x_rot = cx + x_prime * cos_p - y_prime * sin_p
        y_rot = cy - (x_prime * sin_p + y_prime * cos_p)
        pts.append((x_rot, y_rot))

    d_ellipse = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d_ellipse, POS))

    # Вектор миттєвого поля E(t)
    t_inst = ang(50)
    x_pr = ax_a * math.cos(t_inst)
    y_pr = ax_b * math.sin(t_inst)
    ex_inst = cx + x_pr * cos_p - y_pr * sin_p
    ey_inst = cy - (x_pr * sin_p + y_pr * cos_p)
    f.append(arrow(cx, cy, ex_inst, ey_inst, color=NEG, sw=2.5))
    f.append(circle(ex_inst, ey_inst, 4, fill=NEG, stroke=INK, sw=1))
    f.append(text(ex_inst + 12, ey_inst - 6, 'E(t)', 13, NEG, 'start', bold=True, italic=True))

    # Стрілка напрямку обертання вектора E
    t_arrow = ang(70)
    x_ar = cx + ax_a * math.cos(t_arrow) * cos_p - ax_b * math.sin(t_arrow) * sin_p
    y_ar = cy - (ax_a * math.cos(t_arrow) * sin_p + ax_b * math.sin(t_arrow) * cos_p)
    f.append(arrow(x_ar - 10, y_ar - 5, x_ar + 5, y_ar - 12, color=POS, sw=2))

    # Позначення азимутального кута ψ
    f.append(text(cx + 65, cy - 18, 'ψ', 13, POS, 'middle', bold=True, italic=True))

    # Інформаційний блок праворуч
    f.append(fitbox(470, 75, 195, 290,
                    'Параметри еліпса:\n\n' +
                    '• Азимут ψ: кут нахилу\n  головної осі (0 ≤ ψ < π)\n\n' +
                    '• Еліптичність tg χ = b / a\n  (-π/4 ≤ χ ≤ π/4)\n\n' +
                    '• Фазовий зсув Δφ = φᵧ - φₓ:\n' +
                    '  Δφ = 0, π  → лінійна\n' +
                    '  Δφ = ±π/2  → колова\n' +
                    '  знак χ    → напрям руху',
                    size=11, color=INK, fill='#f1f5f9', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'polarization-ellipse.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Сфера Пуанкаре для відображення станів поляризації
# ═══════════════════════════════════════════════════════════════════════════
def fig_poincare_sphere():
    W, H = 720, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Сфера Пуанкаре для відображення станів поляризації', 16, INK, 'middle', bold=True))

    cx, cy = 270, 235
    R = 130

    # Задня півсфера (сітка)
    f.append(circle(cx, cy, R, fill='#fafbfc', stroke=LINE, sw=1.5))

    # Екватор (перспектива — еліпс)
    f.append('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4,4"/>' %
             (cx, cy, R, 42, MUTED))

    # Осі координат Стокса S1, S2, S3
    # S3 (вертикальна вісь: колові поляризації)
    f.append(arrow(cx, cy + R + 25, cx, cy - R - 25, color=INK, sw=1.8))
    f.append(text(cx, cy - R - 32, 'S₃ (Колова)', 11, INK, 'middle', bold=True))

    # S1 (горизонтальна вісь вправо: H / V)
    f.append(arrow(cx - R - 25, cy, cx + R + 45, cy, color=INK, sw=1.8))
    f.append(text(cx + R + 50, cy + 4, 'S₁ (H/V)', 11, INK, 'start', bold=True))

    # S2 (нахилена вісь перспективи: +45° / -45°)
    s2_dx, s2_dy = 75, 45
    f.append(arrow(cx + s2_dx + 15, cy - s2_dy - 10, cx - s2_dx - 20, cy + s2_dy + 12, color=INK, sw=1.8))
    f.append(text(cx - s2_dx - 25, cy + s2_dy + 24, 'S₂ (±45°)', 11, INK, 'end', bold=True))

    # Полюси сфери
    # Північний полюс: RCP
    f.append(circle(cx, cy - R, 6, fill=POS, stroke=INK, sw=1.2))
    f.append(text(cx + 12, cy - R + 14, 'RCP (S₃=+1)', 10, POS, 'start', bold=True))

    # Південний полюс: LCP
    f.append(circle(cx, cy + R, 6, fill=NEG, stroke=INK, sw=1.2))
    f.append(text(cx + 12, cy + R + 14, 'LCP (S₃=-1)', 10, NEG, 'start', bold=True))

    # Екваторіальні точки
    # H (S1 = +1)
    f.append(circle(cx + R, cy, 5, fill=FIELD, stroke=INK, sw=1.2))
    f.append(text(cx + R + 6, cy - 10, 'H (0°)', 10, FIELD, 'start', bold=True))

    # V (S1 = -1)
    f.append(circle(cx - R, cy, 5, fill=FIELD, stroke=INK, sw=1.2))
    f.append(text(cx - R - 6, cy - 10, 'V (90°)', 10, FIELD, 'end', bold=True))

    # +45° (S2 = +1)
    p45_x, p45_y = cx - 60, cy + 34
    f.append(circle(p45_x, p45_y, 5, fill=FIELD, stroke=INK, sw=1.2))
    f.append(text(p45_x - 8, p45_y + 14, '+45°', 10, FIELD, 'end', bold=True))

    # Центр сфери
    f.append(circle(cx, cy, 5, fill=MUTED, stroke=INK, sw=1.2))
    f.append(text(cx + 10, cy + 18, 'Центр: P=0', 10, MUTED, 'start'))

    # Інформаційна панель праворуч
    f.append(fitbox(495, 65, 210, 330,
                    'Властивості сфери:\n\n' +
                    '• Радіус сфери R = S₀\n' +
                    '• Поверхня (R=1): P = 1\n  (повністю поляризоване)\n\n' +
                    '• Всередині (R<1): P < 1\n  (частково поляризоване)\n\n' +
                    '• Екватор (S₃=0):\n  лінійні поляризації\n\n' +
                    '• Кути в просторі Стокса:\n  2ψ (азимут), 2χ (еліптичність)\n\n' +
                    '• Фазові платівки:\n  повертають дугу на сфері',
                    size=10, color=INK, fill='#f4f6f8', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'poincare-sphere.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Порівняння формалізмів Джонса та Мюллера
# ═══════════════════════════════════════════════════════════════════════════
def fig_jones_vs_mueller_pipeline():
    W, H = 700, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Порівняння числення Джонса та Мюллера', 16, INK, 'middle', bold=True))

    # Лівий блок — формалізм Джонса
    bx1, by1, bw, bh = 40, 70, 290, 250
    f.append(rect(bx1, by1, bw, bh, fill='#f0f9ff', stroke=POS, sw=1.5, rx=6))
    f.append(text(bx1 + bw / 2, by1 + 25, 'Числення Джонса (2×2)', 14, POS, 'middle', bold=True))
    f.append(line(bx1 + 15, by1 + 38, bx1 + bw - 15, by1 + 38, color=POS, sw=1))

    f.append(fitbox(bx1 + 15, by1 + 50, bw - 30, 180,
                    '• Світло: Вектор Джонса J (2×1, ℂ)\n' +
                    '  з амплітудами та фазами (Eₓ, Eᵧ)\n\n' +
                    '• Елементи: Матриця Джонса M (2×2, ℂ)\n\n' +
                    '• Трансформація: J_out = M_N ... M₁ · J_in\n\n' +
                    '• Обмеження:\n' +
                    '  - ТІЛЬКИ когерентне світло (P = 1)\n' +
                    '  - Не описує деполяризацію\n' +
                    '  - Враховує абсолютну фазу',
                    size=10, color=INK, fill='none', stroke='none', sw=0))

    # Правий блок — формалізм Мюллера
    bx2, by2 = 370, 70
    f.append(rect(bx2, by2, bw, bh, fill='#fdf2f8', stroke=NEG, sw=1.5, rx=6))
    f.append(text(bx2 + bw / 2, by2 + 25, 'Числення Мюллера (4×4)', 14, NEG, 'middle', bold=True))
    f.append(line(bx2 + 15, by2 + 38, bx2 + bw - 15, by2 + 38, color=NEG, sw=1))

    f.append(fitbox(bx2 + 15, by2 + 50, bw - 30, 180,
                    '• Світло: Вектор Стокса S (4×1, ℝ)\n' +
                    '  з інтенсивностями (S₀, S₁, S₂, S₃)\n\n' +
                    '• Елементи: Матриця Мюллера M (4×4, ℝ)\n\n' +
                    '• Трансформація: S_out = M_N ... M₁ · S_in\n\n' +
                    '• Переваги:\n' +
                    '  - Будь-яке світло (0 ≤ P ≤ 1)\n' +
                    '  - Описує деполяризацію й розсіяння\n' +
                    '  - Працює з некогерентними сумішами',
                    size=10, color=INK, fill='none', stroke='none', sw=0))

    # Нижній місток зв'язку
    f.append(fitbox(180, 328, 340, 26,
                    'Конверсія: M_Mueller = 1/2 · Tr(σ_i · J · σ_j · J†) [для недополяризуючих систем]',
                    size=9, color=MUTED, fill='#f8fafc', stroke=LINE, sw=1))

    render(os.path.join(IMG, 'jones-vs-mueller-pipeline.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Схема ЖК-пікселя на основі скрученого нематика (TN)
# ═══════════════════════════════════════════════════════════════════════════
def fig_tn_lcd_polarization():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Схема ЖК-комірки Twisted Nematic (TN) у матричному численні', 16, INK, 'middle', bold=True))

    y_center = 175

    # 1. Вхідне неполяризоване світло (S_in)
    f.append(arrow(30, y_center, 90, y_center, color=MUTED, sw=3))
    f.append(text(60, y_center - 18, 'Джерело світла', 10, MUTED, 'middle', bold=True))
    f.append(text(60, y_center + 20, 'S_in = (I₀,0,0,0)ᵀ', 9, MUTED, 'middle'))

    # 2. Вхідний поляризатор (Horizontal: 0°)
    f.append(rect(95, y_center - 60, 20, 120, fill='#e0f2fe', stroke=POS, sw=1.5, rx=3))
    f.append(line(105, y_center - 50, 105, y_center + 50, color=POS, sw=2))
    f.append(text(105, y_center - 70, 'Поляризатор 0°', 10, POS, 'middle', bold=True))
    f.append(text(105, y_center + 75, 'J = (1, 0)ᵀ', 9, POS, 'middle'))

    # Світло після поляризатора
    f.append(arrow(120, y_center, 180, y_center, color=POS, sw=2.5))

    # 3. РК-шар (TN 90°)
    f.append(rect(185, y_center - 70, 170, 140, fill='#fef3c7', stroke=FIELD, sw=1.5, rx=4))
    f.append(text(270, y_center - 50, 'РК-комірка (TN 90°)', 11, FIELD, 'middle', bold=True))

    for ix in range(6):
        x_m = 205 + ix * 26
        angle_m = (ix / 5.0) * (math.pi / 2)
        dx_m = 12 * math.cos(angle_m)
        dy_m = 12 * math.sin(angle_m)
        f.append(line(x_m - dx_m, y_center - dy_m, x_m + dx_m, y_center + dy_m, color=FIELD, sw=2.5))

    f.append(text(270, y_center + 52, 'Без напруги (V=0): повертає E на 90°', 9, INK, 'middle'))

    # Світло після РК-шару
    f.append(arrow(360, y_center, 420, y_center, color=NEG, sw=2.5))
    f.append(text(390, y_center - 18, 'J = (0, 1)ᵀ', 9, NEG, 'middle', bold=True))

    # 4. Вихідний аналізатор (Vertical: 90°)
    f.append(rect(425, y_center - 60, 20, 120, fill='#fce7f3', stroke=NEG, sw=1.5, rx=3))
    f.append(line(435, y_center - 50, 435, y_center + 50, color=NEG, sw=2))
    f.append(text(435, y_center - 70, 'Аналізатор 90°', 10, NEG, 'middle', bold=True))

    # Вихідне світло
    f.append(arrow(450, y_center, 530, y_center, color=POS, sw=3))
    f.append(text(490, y_center - 18, 'Світло проходить!', 10, POS, 'middle', bold=True))
    f.append(text(490, y_center + 20, 'Стан "Ввімкнено" (Яскравий)', 9, POS, 'middle'))

    # Інформаційна рамка праворуч
    f.append(fitbox(545, 80, 165, 230,
                    'При поданні напруги V:\n\n' +
                    '• Молекули РК випрямляються\n  вздовж поля\n\n' +
                    '• Скручування зникає (J_LC = I)\n\n' +
                    '• Поляризація залишається H (0°)\n\n' +
                    '• Аналізатор 90° блокує H-хвилю\n\n' +
                    '• Світло НЕ проходить\n  (Темний піксель)',
                    size=10, color=INK, fill='#f8fafc', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'tn-lcd-polarization.svg'), W, H, *f)

if __name__ == '__main__':
    fig_polarization_ellipse()
    fig_poincare_sphere()
    fig_jones_vs_mueller_pipeline()
    fig_tn_lcd_polarization()
    print("All figures for polarization-matrix-calculus generated successfully!")
