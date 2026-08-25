# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Оптична схема інтерферометра Майкельсона
# ═══════════════════════════════════════════════════════════════════════════
def fig_michelson_setup():
    W, H = 760, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Оптична схема інтерферометра Майкельсона', 16, INK, 'middle', bold=True))

    # Координати центрального світлодільника BS
    bs_x, bs_y = 320, 260

    # 1. Джерело світла (ліворуч)
    src_x, src_y = 60, bs_y
    f.append(circle(src_x, src_y, 14, fill='#fef08a', stroke='#eab308', sw=2))
    f.append(text(src_x, src_y - 24, 'Лазерне джерело (S)', 11, INK, 'middle', bold=True))
    f.append(text(src_x, src_y + 30, 'когерентне випромінювання', 9, MUTED, 'middle'))

    # Коліматорна лінза біля джерела
    f.append(rect(src_x + 40, src_y - 25, 8, 50, fill='#e0f2fe', stroke=NEG, sw=1.5, rx=4))
    f.append(text(src_x + 44, src_y - 32, 'Лінза', 9, MUTED, 'middle'))

    # 2. Дзеркало M1 (нерухоме, вгорі)
    m1_x, m1_y = bs_x, 80
    f.append(rect(m1_x - 45, m1_y - 8, 90, 10, fill='#94a3b8', stroke=INK, sw=1.8, rx=2))
    # Відбивний шар (нижня грань M1)
    f.append(line(m1_x - 45, m1_y + 2, m1_x + 45, m1_y + 2, color=NEG, sw=2))
    f.append(text(m1_x, m1_y - 18, 'Нерухоме дзеркало (M₁)', 11, INK, 'middle', bold=True))
    f.append(text(m1_x + 75, m1_y + 2, 'Плече 1 (L₁)', 11, POS, 'start', bold=True))

    # 3. Дзеркало M2 (рухоме, праворуч)
    m2_x, m2_y = 580, bs_y
    f.append(rect(m2_x - 2, m2_y - 45, 10, 90, fill='#94a3b8', stroke=INK, sw=1.8, rx=2))
    # Відбивний шар (ліва грань M2)
    f.append(line(m2_x - 2, m2_y - 45, m2_x - 2, m2_y + 45, color=POS, sw=2))
    f.append(text(m2_x + 16, m2_y - 55, 'Рухоме дзеркало (M₂)', 11, INK, 'start', bold=True))
    f.append(text(m2_x - 30, m2_y + 65, 'Плече 2 (L₂)', 11, POS, 'middle', bold=True))

    # Стрілка мікрометричного зсуву для M2
    f.append(line(m2_x + 25, m2_y, m2_x + 55, m2_y, color=POS, sw=2))
    f.append(line(m2_x + 48, m2_y - 5, m2_x + 58, m2_y, color=POS, sw=2))
    f.append(line(m2_x + 48, m2_y + 5, m2_x + 58, m2_y, color=POS, sw=2))
    f.append(text(m2_x + 40, m2_y + 18, 'ΔL', 11, POS, 'middle', bold=True, italic=True))

    # 4. Світлодільник BS (напівпрозоре дзеркало 50:50 під кутом 45°)
    f.append('<g transform="rotate(-45 %.1f %.1f)">' % (bs_x, bs_y))
    f.append(rect(bs_x - 4, bs_y - 35, 8, 70, fill='#e0f2fe', stroke=NEG, sw=1.5, rx=2))
    f.append(line(bs_x - 4, bs_y - 35, bs_x - 4, bs_y + 35, color=POS, sw=2))
    f.append('</g>')
    f.append(text(bs_x - 35, bs_y - 25, 'Світлодільник (BS)', 11, INK, 'end', bold=True))
    f.append(text(bs_x - 35, bs_y - 10, '50:50', 10, MUTED, 'end'))

    # 5. Компенсаційна пластина C (паралельно BS у плечі 2)
    comp_x, comp_y = bs_x + 110, bs_y
    f.append('<g transform="rotate(-45 %.1f %.1f)">' % (comp_x, comp_y))
    f.append(rect(comp_x - 4, comp_y - 30, 8, 60, fill='#e0f2fe', stroke=NEG, sw=1.5, rx=2))
    f.append('</g>')
    f.append(text(comp_x, comp_y - 35, 'Компенсаційна', 10, INK, 'middle', bold=True))
    f.append(text(comp_x, comp_y - 22, 'пластина (C)', 10, INK, 'middle', bold=True))

    # 6. Детектор / Екран (внизу)
    det_x, det_y = bs_x, 440
    f.append(rect(det_x - 50, det_y - 5, 100, 12, fill='#334155', stroke=INK, sw=1.5, rx=3))
    f.append(text(det_x, det_y + 24, 'Спостережний екран / Детектор (D)', 11, INK, 'middle', bold=True))

    # 7. Хід променів (Лазер -> BS -> M1/M2 -> D)
    # Вхідний промінь від джерела до BS
    f.append(line(src_x + 14, src_y, bs_x, bs_y, color=POS, sw=2))
    f.append(line(src_x + 120, src_y - 4, src_x + 130, src_y, color=POS, sw=2))
    f.append(line(src_x + 120, src_y + 4, src_x + 130, src_y, color=POS, sw=2))

    # Пучок 1 (вгору до M1 і назад до BS)
    f.append(line(bs_x - 2, bs_y, m1_x - 2, m1_y + 2, color='#dc2626', sw=1.8))
    f.append(line(bs_x + 2, m1_y + 2, bs_x + 2, bs_y, color='#b91c1c', sw=1.8, dash='4,3'))
    # Стрілки напрямку
    f.append(line(bs_x - 6, bs_y - 80, bs_x - 2, bs_y - 90, color='#dc2626', sw=2))
    f.append(line(bs_x + 2, bs_y - 90, bs_x + 6, bs_y - 80, color='#b91c1c', sw=2))

    # Пучок 2 (вправо до M2 і назад до BS)
    f.append(line(bs_x, bs_y - 2, m2_x - 2, m2_y - 2, color='#2563eb', sw=1.8))
    f.append(line(m2_x - 2, m2_y + 2, bs_x, bs_y + 2, color='#1d4ed8', sw=1.8, dash='4,3'))
    # Стрілки напрямку
    f.append(line(bs_x + 140, bs_y - 6, bs_x + 150, bs_y - 2, color='#2563eb', sw=2))
    f.append(line(bs_x + 150, bs_y + 2, bs_x + 140, bs_y + 6, color='#1d4ed8', sw=2))

    # Зведені промені від BS до екрана D
    f.append(line(bs_x - 3, bs_y, det_x - 3, det_y - 5, color='#dc2626', sw=1.8))
    f.append(line(bs_x + 3, bs_y, det_x + 3, det_y - 5, color='#2563eb', sw=1.8))
    f.append(line(bs_x - 7, bs_y + 80, bs_x - 3, bs_y + 90, color=POS, sw=2))
    f.append(line(bs_x + 3, bs_y + 90, bs_x + 7, bs_y + 80, color=NEG, sw=2))

    # Пояснювальний підпис внизу
    f.append(text(W / 2, H - 12, 'Розщеплення амплітуди на світлодільнику BS та інтерференція після відбиття від дзеркал M₁ і M₂.', 10, MUTED, 'middle', italic=True))

    render(os.path.join(IMG, 'michelson-setup.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Концепція ефірного дрейфу в досліді Майкельсона — Морлі
# ═══════════════════════════════════════════════════════════════════════════
def fig_aether_drift():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Ефірний вітер і тривалість прольоту в плечах інтерферометра', 16, INK, 'middle', bold=True))

    # Ліва панель (а) — поздовжнє плече (уздовж руху Землі)
    p1_x, p1_y, pw, ph = 30, 50, 320, 280
    f.append(rect(p1_x, p1_y, pw, ph, fill='#fafafa', stroke=INK, sw=1.2, rx=6))
    f.append(text(p1_x + pw / 2, p1_y + 22, 'а) Поздовжнє плече (паралельно v)', 12, INK, 'middle', bold=True))

    # Стрілка ефірного вітру (вліво відносний рух ефіру)
    f.append(line(p1_x + 40, p1_y + 45, p1_x + 280, p1_y + 45, color=MUTED, sw=1.5, dash='5,3'))
    f.append(arrow(p1_x + 220, p1_y + 45, p1_x + 80, p1_y + 45, color=MUTED, sw=1.5))
    f.append(text(p1_x + pw / 2, p1_y + 40, 'Ефірний вітер (швидкість −v)', 10, MUTED, 'middle'))

    # Схема прольоту туда і назад
    # BS -> M2
    f.append(circle(p1_x + 50, p1_y + 110, 8, fill='#e0f2fe', stroke=NEG, sw=1.5))
    f.append(text(p1_x + 50, p1_y + 130, 'BS', 10, INK, 'middle', bold=True))

    f.append(rect(p1_x + 260, p1_y + 90, 6, 40, fill='#94a3b8', stroke=INK, sw=1.5))
    f.append(text(p1_x + 263, p1_y + 145, 'M₂', 10, INK, 'middle', bold=True))

    # Промінь вперед (проти ефіру: c - v)
    f.append(line(p1_x + 58, p1_y + 105, p1_x + 258, p1_y + 105, color=POS, sw=2))
    f.append(line(p1_x + 145, p1_y + 101, p1_x + 155, p1_y + 105, color=POS, sw=2))
    f.append(text(p1_x + 150, p1_y + 95, 'вперед: c − v', 10, POS, 'middle', bold=True))

    # Промінь назад (за ефіром: c + v)
    f.append(line(p1_x + 258, p1_y + 115, p1_x + 58, p1_y + 115, color=NEG, sw=2))
    f.append(line(p1_x + 155, p1_y + 119, p1_x + 145, p1_y + 115, color=NEG, sw=2))
    f.append(text(p1_x + 150, p1_y + 130, 'назад: c + v', 10, NEG, 'middle', bold=True))

    # Формула для t_long
    f.append(textbox(p1_x + pw / 2, p1_y + 210, 't_поздовжнє = L/(c−v) + L/(c+v)\n= (2 L c) / (c² − v²) ≈ (2L/c) · (1 + v²/c²)', size=11, color=INK, fill='#ffffff', stroke=LINE)[0])

    # Права панель (б) — поперечне плече (перпендикулярно до v)
    p2_x, p2_y = 380, 50
    f.append(rect(p2_x, p2_y, pw, ph, fill='#fafafa', stroke=INK, sw=1.2, rx=6))
    f.append(text(p2_x + pw / 2, p2_y + 22, 'б) Поперечне плече (перпендикулярно v)', 12, INK, 'middle', bold=True))

    # Трикутник швидкостей
    bs2_x, bs2_y = p2_x + 60, p2_y + 150
    m1_x, m1_y = p2_x + 160, p2_y + 70
    bs2_end_x = p2_x + 260

    # Траєкторія зигзаг у лабораторії
    f.append(line(bs2_x, bs2_y, m1_x, m1_y, color=POS, sw=2))
    f.append(line(m1_x, m1_y, bs2_end_x, bs2_y, color=NEG, sw=2))

    f.append(circle(bs2_x, bs2_y, 6, fill='#e0f2fe', stroke=NEG, sw=1.5))
    f.append(text(bs2_x, bs2_y + 16, 'BS (t=0)', 9, INK, 'middle', bold=True))

    f.append(rect(m1_x - 20, m1_y - 6, 40, 6, fill='#94a3b8', stroke=INK, sw=1.5))
    f.append(text(m1_x, m1_y - 12, 'M₁', 10, INK, 'middle', bold=True))

    f.append(circle(bs2_end_x, bs2_y, 6, fill='#e0f2fe', stroke=NEG, sw=1.5))
    f.append(text(bs2_end_x, bs2_y + 16, 'BS (t=t₂)', 9, INK, 'middle', bold=True))

    f.append(text(p2_x + pw / 2, p2_y + 105, 'в ефективне c_eff = √(c² − v²)', 10, FIELD, 'middle', bold=True))

    # Формула для t_trans
    f.append(textbox(p2_x + pw / 2, p2_y + 210, 't_поперечне = (2 L) / √(c² − v²)\n≈ (2L/c) · (1 + v²/(2c²))', size=11, color=INK, fill='#ffffff', stroke=LINE)[0])

    f.append(text(W / 2, H - 12, 'Різниця часу Δt ≈ L·v²/c³ викликає зсув смуг ΔN = 2L·v²/(λ·c²) при повороті установки на 90°.', 10, MUTED, 'middle', italic=True))

    render(os.path.join(IMG, 'aether-drift.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Типи інтерференційних картин
# ═══════════════════════════════════════════════════════════════════════════
def fig_fringe_types():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Типи інтерференційних смуг в інтерферометрі Майкельсона', 16, INK, 'middle', bold=True))

    # Ліва панель (а) — Смуги рівного нахилу (паралельні дзеркала M1 || M2')
    p1_x, p1_y, pw, ph = 30, 50, 310, 270
    f.append(rect(p1_x, p1_y, pw, ph, fill='#fafafa', stroke=INK, sw=1.2, rx=6))
    f.append(text(p1_x + pw / 2, p1_y + 22, 'а) Смуги рівного нахилу (M₁ ∥ M₂\')', 12, INK, 'middle', bold=True))

    # Концентричні кільця Гайдінгера
    cx, cy = p1_x + pw / 2, p1_y + 115
    f.append(circle(cx, cy, 75, fill='#0f172a', stroke=INK, sw=1))

    radii = [70, 58, 46, 34, 22, 10]
    for i, r in enumerate(radii):
        c_fill = '#38bdf8' if i % 2 == 0 else '#0f172a'
        f.append(circle(cx, cy, r, fill=c_fill, stroke='none', sw=0))

    f.append(text(p1_x + pw / 2, p1_y + 210, 'Кільця Гайдінгера (Haidinger rings)', 11, INK, 'middle', bold=True))
    f.append(text(p1_x + pw / 2, p1_y + 230, 'Строго паралельні дзеркала, Δs = 2d·cos θ', 10, MUTED, 'middle'))
    f.append(text(p1_x + pw / 2, p1_y + 246, 'Центр кільця локалізований у нескінченності', 9, POS, 'middle'))

    # Права панель (б) — Смуги рівної товщини (клин між дзеркалами)
    p2_x, p2_y = 380, 50
    f.append(rect(p2_x, p2_y, pw, ph, fill='#fafafa', stroke=INK, sw=1.2, rx=6))
    f.append(text(p2_x + pw / 2, p2_y + 22, 'б) Смуги рівної товщини (клин α > 0)', 12, INK, 'middle', bold=True))

    # Прямі смуги Фізо (вертикальні)
    fx, fy, fw, fh = p2_x + pw / 2 - 75, p2_y + 115 - 75, 150, 150
    f.append(rect(fx, fy, fw, fh, fill='#0f172a', stroke=INK, sw=1, rx=4))

    stripe_w = 15
    for i in range(10):
        if i % 2 == 0:
            f.append(rect(fx + i * stripe_w, fy, stripe_w, fh, fill='#38bdf8', stroke='none', sw=0))

    f.append(text(p2_x + pw / 2, p2_y + 210, 'Смуги Фізо (Fizeau fringes)', 11, INK, 'middle', bold=True))
    f.append(text(p2_x + pw / 2, p2_y + 230, 'Невеликий кут клина α між M₁ та M₂\'', 10, MUTED, 'middle'))
    f.append(text(p2_x + pw / 2, p2_y + 246, 'Прямі смуги, локалізовані біля дзеркала', 9, POS, 'middle'))

    f.append(text(W / 2, H - 10, 'Зміна відстані d змінює радіус кілець, а зміна кута α змінює нахил і крок прямих смуг.', 10, MUTED, 'middle', italic=True))

    render(os.path.join(IMG, 'fringe-types.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Схема гравітаційно-хвильового детектора Advanced LIGO
# ═══════════════════════════════════════════════════════════════════════════
def fig_gw_detector_ligo():
    W, H = 760, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Оптична схема детектора гравітаційних хвиль Advanced LIGO', 16, INK, 'middle', bold=True))

    bs_x, bs_y = 300, 240

    # 1. Лазер + PRM (Power Recycling Mirror)
    src_x, src_y = 60, bs_y
    f.append(rect(src_x - 30, src_y - 20, 60, 40, fill='#fef08a', stroke='#eab308', sw=1.8, rx=4))
    f.append(text(src_x, src_y - 4, 'Лазер', 11, INK, 'middle', bold=True))
    f.append(text(src_x, src_y + 12, '1064 нм / 200 Вт', 9, MUTED, 'middle'))

    # PRM
    prm_x = 160
    f.append(rect(prm_x - 4, src_y - 25, 8, 50, fill='#93c5fd', stroke=NEG, sw=1.5, rx=2))
    f.append(text(prm_x, src_y - 32, 'PRM (Рециркуляція)', 9, NEG, 'middle', bold=True))

    # 2. Світлодільник BS
    f.append('<g transform="rotate(-45 %.1f %.1f)">' % (bs_x, bs_y))
    f.append(rect(bs_x - 4, bs_y - 30, 8, 60, fill='#e0f2fe', stroke=NEG, sw=1.5, rx=2))
    f.append('</g>')
    f.append(text(bs_x - 25, bs_y - 25, 'BS (50:50)', 11, INK, 'end', bold=True))

    # 3. Вертикальне плече (Y-arm, 4 км, резонатор Фабрі — Перо)
    itm_y_x, itm_y_y = bs_x, 150
    etm_y_x, etm_y_y = bs_x, 60

    # ITM Y (вхідне дзеркало)
    f.append(rect(itm_y_x - 25, itm_y_y - 4, 50, 8, fill='#cbd5e1', stroke=INK, sw=1.5, rx=2))
    f.append(text(itm_y_x + 32, itm_y_y + 3, 'ITM_Y (Вхідне)', 9, INK, 'start', bold=True))

    # ETM Y (кінцеве дзеркало на підвісі)
    f.append(rect(etm_y_x - 30, etm_y_y - 6, 60, 10, fill='#64748b', stroke=INK, sw=1.8, rx=2))
    f.append(text(etm_y_x + 36, etm_y_y + 3, 'ETM_Y (Кінцеве)', 9, INK, 'start', bold=True))

    f.append(text(bs_x - 35, 105, 'Резонатор Y (4 км)', 10, POS, 'end', bold=True))

    # 4. Горизонтальне плече (X-arm, 4 км, резонатор Фабрі — Перо)
    itm_x_x, itm_x_y = 430, bs_y
    etm_x_x, etm_x_y = 660, bs_y

    # ITM X
    f.append(rect(itm_x_x - 4, itm_x_y - 25, 8, 50, fill='#cbd5e1', stroke=INK, sw=1.5, rx=2))
    f.append(text(itm_x_x, itm_x_y + 36, 'ITM_X', 9, INK, 'middle', bold=True))

    # ETM X
    f.append(rect(etm_x_x - 6, etm_x_y - 30, 12, 60, fill='#64748b', stroke=INK, sw=1.8, rx=2))
    f.append(text(etm_x_x, etm_x_y + 42, 'ETM_X', 9, INK, 'middle', bold=True))

    f.append(text(545, bs_y - 18, 'Резонатор X (4 км)', 10, POS, 'middle', bold=True))

    # 5. SRM та Детектор (внизу)
    srm_y = 330
    f.append(rect(bs_x - 25, srm_y - 4, 50, 8, fill='#93c5fd', stroke=NEG, sw=1.5, rx=2))
    f.append(text(bs_x + 32, srm_y + 3, 'SRM (Сигнальна рециркуляція)', 9, NEG, 'start', bold=True))

    det_y = 400
    f.append(rect(bs_x - 45, det_y - 8, 90, 16, fill='#334155', stroke=INK, sw=1.5, rx=3))
    f.append(text(bs_x, det_y + 4, 'Фотодетектор (D)', 11, BG, 'middle', bold=True))

    # 6. Лазерні промені у плечах
    # Від лазера через PRM до BS
    f.append(line(src_x + 30, src_y, bs_x, bs_y, color=POS, sw=2))

    # Багаторазове відбиття в плечах (товсті лінії у резонаторах)
    f.append(line(bs_x, bs_y, bs_x, etm_y_y + 4, color='#dc2626', sw=3))
    f.append(line(bs_x, bs_y, etm_x_x - 6, bs_y, color='#dc2626', sw=3))

    # До детектора
    f.append(line(bs_x, bs_y, bs_x, det_y - 8, color='#dc2626', sw=1.8))

    # 7. Значок гравітаційної хвилі h(t)
    f.append(text(540, bs_y + 85, 'Гравітаційна хвиля h ~ 10⁻²¹', 12, POS, 'middle', bold=True))
    f.append(text(540, bs_y + 102, 'розтягує X-плече, стискає Y-плече', 10, MUTED, 'middle'))

    f.append(text(W / 2, H - 10, 'Завдяки резонаторам Фабрі — Перо ефективна довжина плечей сягає 300 км, реєструючи ΔL ≈ 10⁻¹⁹ м.', 10, MUTED, 'middle', italic=True))

    render(os.path.join(IMG, 'gw-detector-ligo.svg'), W, H, *f)

if __name__ == '__main__':
    fig_michelson_setup()
    fig_aether_drift()
    fig_fringe_types()
    fig_gw_detector_ligo()
    print("All Michelson interferometer figures generated successfully!")
