# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Оптична схема та багатопроменеве відбиття в інтерферометрі
# ═══════════════════════════════════════════════════════════════════════════
def fig_fabry_perot_setup():
    W, H = 780, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Оптична схема ресонатора Фабрі — Перо та багатопроменева інтерференція', 15, INK, 'middle', bold=True))

    # Дзеркала / пластини Фабрі — Перо
    m1_x, m2_x = 260, 440
    m_y, m_h, m_w = 70, 320, 24

    # Дзеркало 1 (ліве)
    f.append(rect(m1_x - m_w, m_y, m_w, m_h, fill='#e0f2fe', stroke='#0284c7', sw=1.5, rx=2))
    # Високовідбивальне покриття R на внутрішній грані (права грань дзеркала 1)
    f.append(line(m1_x, m_y, m1_x, m_y + m_h, color=POS, sw=3))

    # Дзеркало 2 (праве)
    f.append(rect(m2_x, m_y, m_w, m_h, fill='#e0f2fe', stroke='#0284c7', sw=1.5, rx=2))
    # Високовідбивальне покриття R на внутрішній грані (ліва грань дзеркала 2)
    f.append(line(m2_x, m_y, m2_x, m_y + m_h, color=POS, sw=3))

    # Позначення дзеркал та проміжку
    f.append(text(m1_x - m_w / 2, m_y - 14, 'Дзеркало M₁', 11, INK, 'middle', bold=True))
    f.append(text(m2_x + m_w / 2, m_y - 14, 'Дзеркало M₂', 11, INK, 'middle', bold=True))
    f.append(text(m1_x - 4, m_y + m_h + 18, 'Покриття R', 10, POS, 'end', bold=True))
    f.append(text(m2_x + 4, m_y + m_h + 18, 'Покриття R', 10, POS, 'start', bold=True))

    # Відстань між дзеркалами d
    d_y = m_y + m_h + 35
    f.append(line(m1_x, d_y, m2_x, d_y, color=INK, sw=1.5))
    f.append(line(m1_x, d_y - 5, m1_x, d_y + 5, color=INK, sw=1.5))
    f.append(line(m2_x, d_y - 5, m2_x, d_y + 5, color=INK, sw=1.5))
    f.append(text((m1_x + m2_x) / 2, d_y - 6, 'Товщина проміжку d (показник заломлення n)', 11, INK, 'middle', bold=True, italic=True))

    # Джерело світла та вхідний промінь
    src_x, src_y = 60, 200
    f.append(circle(src_x, src_y, 14, fill='#fef08a', stroke='#eab308', sw=2))
    f.append(text(src_x, src_y - 22, 'Джерело S', 11, INK, 'middle', bold=True))
    f.append(text(src_x, src_y + 26, 'хвиля E₀', 10, MUTED, 'middle'))

    # Вхідний промінь під кутом θ
    in_y1 = 140
    in_y2 = 180
    f.append(line(src_x + 14, src_y - 10, m1_x - m_w, in_y1, color=POS, sw=2))
    f.append(line(m1_x - m_w, in_y1, m1_x, in_y2, color=POS, sw=2))
    f.append(text(src_x + 100, in_y1 - 12, 'Вхідна хвиля E₀', 11, POS, 'middle', bold=True))

    # Штрихова нормаль та кут падіння θ
    f.append(line(m1_x - 50, in_y2, m1_x + 50, in_y2, color=MUTED, sw=1, dash='3,3'))
    f.append(text(m1_x - 30, in_y2 - 8, 'θ', 11, INK, 'middle', bold=True, italic=True))

    # Зігзаг багаторазового відбиття всередині ресонатора
    pts = [
        (m1_x, in_y2),         # P0 на M1
        (m2_x, in_y2 + 45),    # P1 на M2
        (m1_x, in_y2 + 90),    # P2 на M1
        (m2_x, in_y2 + 135),   # P3 на M2
        (m1_x, in_y2 + 180)    # P4 на M1
    ]

    # Внутрішнє проходження хвилі
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color='#e11d48', sw=1.8))

    # Пропущені промені T1, T2, T3 (виходять праворуч)
    t_length = 120
    dx_t = t_length * math.cos(math.radians(22))
    dy_t = t_length * math.sin(math.radians(22))

    t_sources = [pts[1], pts[3]]
    t_labels = ['T₁ (амплітуда t₁t₂ E₀)', 'T₂ (амплітуда t₁t₂ R E₀)', 'T₃ ...']

    for idx, pt in enumerate(t_sources):
        tx1, ty1 = pt[0] + m_w, pt[1]
        tx2, ty2 = tx1 + dx_t, ty1 + dy_t
        f.append(line(tx1, ty1, tx2, ty2, color='#2563eb', sw=2))
        f.append(text(tx2 + 10, ty2 + 4, t_labels[idx], 10, '#1e40af', 'start', bold=True))

    # Третій пропущений промінь для ілюстрації
    tx1_3, ty1_3 = m2_x + m_w, in_y2 + 225
    f.append(line(tx1_3, ty1_3, tx1_3 + dx_t, ty1_3 + dy_t, color='#2563eb', sw=1.8, dash='4,3'))
    f.append(text(tx1_3 + dx_t + 10, ty1_3 + dy_t + 4, t_labels[2], 10, '#1e40af', 'start', italic=True))

    # Відбиті промені R0, R1, R2 (виходять ліворуч)
    r_sources = [(m1_x - m_w, in_y1), (m1_x - m_w, pts[2][1]), (m1_x - m_w, pts[4][1])]
    r_labels = ['R₀', 'R₁', 'R₂ ...']
    dx_r = -90
    dy_r = 35

    for idx, pt in enumerate(r_sources):
        rx1, ry1 = pt[0], pt[1]
        rx2, ry2 = rx1 + dx_r, ry1 + dy_r
        f.append(line(rx1, ry1, rx2, ry2, color='#d97706', sw=1.8))
        f.append(text(rx2 - 8, ry2 + 4, r_labels[idx], 10, '#b45309', 'end', bold=True))

    # Лінза та зведення пропущених променів
    lens_x = 640
    f.append(rect(lens_x, 120, 10, 260, fill='#e0f2fe', stroke=NEG, sw=1.5, rx=5))
    f.append(text(lens_x + 5, 106, 'Лінза L', 10, INK, 'middle', bold=True))

    # Сфокусований інтерференційний пік на екрані
    screen_x = 730
    f.append(rect(screen_x, 140, 6, 220, fill='#334155', stroke=INK, sw=1.5, rx=2))
    f.append(text(screen_x + 12, 250, 'Екран D', 10, INK, 'start', bold=True))

    # Промені від лінзи до точки фокусування на екрані
    foc_y = 270
    for pt in t_sources:
        tx1, ty1 = pt[0] + m_w, pt[1]
        lx, ly = lens_x, ty1 + (lens_x - (tx1 + dx_t)) * (dy_t / dx_t)
        f.append(line(lx + 10, ly, screen_x, foc_y, color='#2563eb', sw=1.5))

    # Яскрава точка фокусу
    f.append(circle(screen_x, foc_y, 5, fill='#38bdf8', stroke='#0284c7', sw=1.5))
    f.append(text(screen_x - 15, foc_y - 12, 'Конструктивна інтерференція', 9, POS, 'end', bold=True))

    # Підпис
    f.append(text(W / 2, H - 12, 'Формування багатопроменевої інтерференційної картини на проходження в ресонаторі Фабрі — Перо.', 10, MUTED, 'middle', italic=True))

    render(os.path.join(IMG, 'fabry-perot-setup.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Розподіл Ейрі (залежність I_T/I_0 від фази для різних R)
# ═══════════════════════════════════════════════════════════════════════════
def fig_airy_distribution():
    W, H = 760, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Спектр пропускання Ейрі для різних коефіцієнтів відбиття R', 15, INK, 'middle', bold=True))

    # Область графіка
    gx, gy, gw, gh = 80, 70, 620, 310

    # Сітка та осі
    f.append(rect(gx, gy, gw, gh, fill='#f8fafc', stroke='#cbd5e1', sw=1))

    # Горизонтальні лінії I_T/I_0 = 0.5 та 1.0
    y_10 = gy
    y_05 = gy + gh / 2
    y_00 = gy + gh

    f.append(line(gx, y_05, gx + gw, y_05, color='#cbd5e1', sw=1, dash='4,4'))
    f.append(text(gx - 10, y_10 + 4, '1.0', 10, INK, 'end'))
    f.append(text(gx - 10, y_05 + 4, '0.5', 10, INK, 'end'))
    f.append(text(gx - 10, y_00 + 4, '0.0', 10, INK, 'end'))
    f.append(text(gx - 35, gy + gh / 2, 'I_T / I₀', 11, INK, 'middle', bold=True))

    # Вертикальні лінії для phase = -2pi, -pi, 0, +pi, +2pi
    x_m2pi = gx
    x_mpi  = gx + gw * 0.25
    x_0    = gx + gw * 0.5
    x_ppi  = gx + gw * 0.75
    x_p2pi = gx + gw

    x_ticks = [(x_m2pi, '-2π'), (x_mpi, '-π'), (x_0, '0'), (x_ppi, '+π'), (x_p2pi, '+2π')]
    for xt, label in x_ticks:
        f.append(line(xt, gy, xt, gy + gh, color='#e2e8f0', sw=1, dash='3,3'))
        f.append(text(xt, gy + gh + 18, label, 11, INK, 'middle', bold=True))

    f.append(text(gx + gw / 2, gy + gh + 38, 'Фазовий набіг δ (радіани)', 11, INK, 'middle', bold=True))

    # Функція для побудови кривої Ейрі: I_T/I_0 = 1 / (1 + F_coeff * sin^2(delta / 2))
    def build_airy_path(R, color, sw, dash=None):
        F_coeff = (4 * R) / ((1 - R) ** 2)
        pts = []
        num_pts = 300
        for i in range(num_pts + 1):
            t = i / num_pts
            # delta від -2pi до +2pi
            delta = -2 * math.pi + t * (4 * math.pi)
            val = 1.0 / (1.0 + F_coeff * (math.sin(delta / 2.0) ** 2))
            px = gx + t * gw
            py = gy + gh * (1.0 - val)
            pts.append((px, py))
        
        path_str = 'M ' + ' L '.join(['%.2f,%.2f' % (p[0], p[1]) for p in pts])
        d_attr = f" dash=\"{dash}\"" if dash else ""
        return f'<path d="{path_str}" fill="none" stroke="{color}" stroke-width="{sw}"{d_attr}/>'

    # Малюємо криві для R = 0.4, R = 0.7, R = 0.9
    f.append(build_airy_path(0.4, '#94a3b8', 2, dash='5,4'))
    f.append(build_airy_path(0.7, '#f59e0b', 2))
    f.append(build_airy_path(0.9, '#2563eb', 2.5))

    # Позначення FSR (Free Spectral Range) між піками 0 та +2pi
    fsr_y = gy + 25
    f.append(line(x_0, fsr_y, x_p2pi, fsr_y, color=POS, sw=1.8))
    f.append(line(x_0, fsr_y - 5, x_0, fsr_y + 5, color=POS, sw=1.8))
    f.append(line(x_p2pi, fsr_y - 5, x_p2pi, fsr_y + 5, color=POS, sw=1.8))
    f.append(text((x_0 + x_p2pi) / 2, fsr_y - 8, 'Область вільної дисперсії (FSR = 2π)', 11, POS, 'middle', bold=True))

    # Позначення FWHM (Full Width at Half Maximum) для піку R=0.9 біля x_0
    # delta_FWHM = 2 * (1 - R) / sqrt(R) рад => для R=0.9 це ~0.21 rad, в пікселях:
    fwhm_rad = 2.0 * (1.0 - 0.9) / math.sqrt(0.9)
    fwhm_px = (fwhm_rad / (4.0 * math.pi)) * gw
    
    fwhm_y = y_05
    f.append(line(x_0 - fwhm_px / 2, fwhm_y, x_0 + fwhm_px / 2, fwhm_y, color='#dc2626', sw=2.5))
    f.append(line(x_0 - fwhm_px / 2, fwhm_y - 8, x_0 - fwhm_px / 2, fwhm_y + 8, color='#dc2626', sw=1.5))
    f.append(line(x_0 + fwhm_px / 2, fwhm_y - 8, x_0 + fwhm_px / 2, fwhm_y + 8, color='#dc2626', sw=1.5))
    f.append(text(x_0 + 65, fwhm_y + 4, 'FWHM (δFWHM)', 10, '#dc2626', 'start', bold=True))

    # Легенда
    leg_x, leg_y = gx + 20, gy + 20
    f.append(rect(leg_x, leg_y, 170, 75, fill='#ffffff', stroke='#cbd5e1', sw=1, rx=3))
    
    # Рядки легенди
    f.append(line(leg_x + 10, leg_y + 18, leg_x + 40, leg_y + 18, color='#2563eb', sw=2.5))
    f.append(text(leg_x + 48, leg_y + 22, 'R = 0.90 (висока різкість)', 10, INK, 'start', bold=True))

    f.append(line(leg_x + 10, leg_y + 38, leg_x + 40, leg_y + 38, color='#f59e0b', sw=2))
    f.append(text(leg_x + 48, leg_y + 42, 'R = 0.70 (середня різкість)', 10, INK, 'start'))

    f.append(line(leg_x + 10, leg_y + 58, leg_x + 40, leg_y + 58, color='#94a3b8', sw=2, dash='5,4'))
    f.append(text(leg_x + 48, leg_y + 62, 'R = 0.40 (низька різкість)', 10, INK, 'start'))

    # Підпис
    f.append(text(W / 2, H - 10, 'Вплив коефіцієнта відбиття дзеркал R на ширину інтерференційних піків та контраст.', 10, MUTED, 'middle', italic=True))

    render(os.path.join(IMG, 'airy-distribution.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Кільця рівного нахилу (смуги Хайдінгера) у фокальній площині
# ═══════════════════════════════════════════════════════════════════════════
def fig_fringes_equal_inclination():
    W, H = 760, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Кільця рівного нахилу (смуги Хайдінгера) у фокальній площині', 15, INK, 'middle', bold=True))

    # Ліва частина: схема фокусування розбіжних променів (X: 40..420)
    # Розсіяне джерело (матове скло / світлодіод)
    src_x = 60
    f.append(rect(src_x - 10, 120, 20, 200, fill='#fef08a', stroke='#eab308', sw=1.5, rx=2))
    f.append(text(src_x, 105, 'Просторове джерело', 10, INK, 'middle', bold=True))

    # Еталон Фабрі — Перо
    fp_x = 180
    f.append(rect(fp_x, 120, 12, 200, fill='#e0f2fe', stroke=POS, sw=1.5, rx=1))
    f.append(rect(fp_x + 35, 120, 12, 200, fill='#e0f2fe', stroke=POS, sw=1.5, rx=1))
    f.append(text(fp_x + 23, 105, 'Еталон FP (d)', 10, INK, 'middle', bold=True))

    # Сфокусувальна лінза L
    lens_x = 300
    f.append(rect(lens_x, 110, 12, 220, fill='#e0f2fe', stroke=NEG, sw=1.5, rx=6))
    f.append(text(lens_x + 6, 95, 'Лінза (f)', 10, INK, 'middle', bold=True))

    # Екран у фокальній площині
    scr_x = 420
    f.append(line(scr_x, 100, scr_x, 340, color=INK, sw=2))
    f.append(text(scr_x, 90, 'Фокальна площина', 10, INK, 'middle', bold=True))

    # Промені під різними кутами θ1, θ2
    foc_c = 220  # оптична вісь Y
    f.append(line(src_x - 30, foc_c, scr_x + 20, foc_c, color=MUTED, sw=1, dash='4,4'))
    f.append(text(scr_x + 10, foc_c + 15, 'Оптична вісь', 9, MUTED, 'start'))

    # Пучок 1 (паралельний осьовий θ = 0 -> фокус у центрі)
    f.append(line(fp_x + 47, foc_c - 15, lens_x, foc_c - 15, color='#2563eb', sw=1.5))
    f.append(line(fp_x + 47, foc_c + 15, lens_x, foc_c + 15, color='#2563eb', sw=1.5))
    f.append(line(lens_x + 12, foc_c - 15, scr_x, foc_c, color='#2563eb', sw=1.5))
    f.append(line(lens_x + 12, foc_c + 15, scr_x, foc_c, color='#2563eb', sw=1.5))

    # Пучок 2 (наклон під кутом θ -> фокус на радіусі r_m)
    r_m_y = foc_c - 70
    f.append(line(fp_x + 47, foc_c - 50, lens_x, foc_c - 80, color='#dc2626', sw=1.5))
    f.append(line(fp_x + 47, foc_c - 30, lens_x, foc_c - 60, color='#dc2626', sw=1.5))
    f.append(line(lens_x + 12, foc_c - 80, scr_x, r_m_y, color='#dc2626', sw=1.5))
    f.append(line(lens_x + 12, foc_c - 60, scr_x, r_m_y, color='#dc2626', sw=1.5))

    # Позначення радіуса r_m
    f.append(line(scr_x + 15, foc_c, scr_x + 15, r_m_y, color='#dc2626', sw=1.5))
    f.append(line(scr_x + 10, foc_c, scr_x + 20, foc_c, color='#dc2626', sw=1))
    f.append(line(scr_x + 10, r_m_y, scr_x + 20, r_m_y, color='#dc2626', sw=1))
    f.append(text(scr_x + 22, (foc_c + r_m_y) / 2 + 4, 'r_m = f · θ_m', 10, '#dc2626', 'start', bold=True))

    # Права частина: вигляд картини на екрані (концентричні кільця, X: 520..720)
    cx, cy = 610, 220
    f.append(rect(cx - 120, cy - 120, 240, 240, fill='#0f172a', stroke='#334155', sw=2, rx=8))

    # Кільця інтерференції
    radii = [95, 75, 52, 28]
    colors = ['#38bdf8', '#38bdf8', '#38bdf8', '#0284c7']
    widths = [3.5, 4.5, 5.5, 7]

    for r, col, w in zip(radii, colors, widths):
        f.append(circle(cx, cy, r, fill='none', stroke=col, sw=w))

    # Центральна яскрава пляма
    f.append(circle(cx, cy, 6, fill='#e0f2fe', stroke='#38bdf8', sw=1))

    # Позначення порядків інтерференції
    f.append(text(cx + radii[3] + 8, cy - 8, 'm', 10, '#e0f2fe', 'start', bold=True))
    f.append(text(cx + radii[2] + 8, cy - 8, 'm - 1', 10, '#38bdf8', 'start', bold=True))
    f.append(text(cx + radii[1] + 8, cy - 8, 'm - 2', 10, '#38bdf8', 'start'))

    f.append(text(cx, cy + 138, 'Картина кілець на екрані', 11, INK, 'middle', bold=True))

    # Підпис
    f.append(text(W / 2, H - 12, 'Формування концентричних кілець рівного нахилу у фокальній площині сфокусувальної лінзи.', 10, MUTED, 'middle', italic=True))

    render(os.path.join(IMG, 'fringes-equal-inclination.svg'), W, H, *f)

if __name__ == '__main__':
    fig_fabry_perot_setup()
    fig_airy_distribution()
    fig_fringes_equal_inclination()
    print("Successfully generated all Fabry-Perot figures.")
