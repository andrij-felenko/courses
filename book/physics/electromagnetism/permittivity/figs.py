# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def make_dipole_polarization():
    w, h = 740, 320
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'dipole-polarization.svg')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Ліва панель: E = 0
    p1 = rect(20, 20, 340, 280, fill="#fcfcfc", stroke=MUTED, sw=1.2)
    t1 = text(190, 45, "А: Без зовнішнього поля (E = 0)", size=14, bold=True)
    
    # Пластини длялівої панелі
    pl1_l = rect(40, 70, 14, 180, fill="#d0d7de", stroke=LINE, sw=1.5)
    pl1_r = rect(306, 70, 14, 180, fill="#d0d7de", stroke=LINE, sw=1.5)
    lbl_pl1 = text(190, 70, "Хаотична орієнтація диполів", size=12, color=MUTED, italic=True)

    # Хаотичні диполі
    dips1 = [
        (90, 110, 25), (150, 130, 140), (220, 100, 220), (270, 120, 80),
        (100, 170, 310), (170, 180, 45), (240, 165, 190), (130, 220, 110),
        (200, 230, 280), (260, 215, 15)
    ]
    dip_elements1 = []
    import math
    for cx, cy, angle_deg in dips1:
        rad = math.radians(angle_deg)
        dx = 14 * math.cos(rad)
        dy = 14 * math.sin(rad)
        # Овал / гантель диполя
        dip_elements1.append(line(cx - dx, cy - dy, cx + dx, cy + dy, color=MUTED, sw=2))
        dip_elements1.append(minus(cx - dx, cy - dy, r=7))
        dip_elements1.append(plus(cx + dx, cy + dy, r=7))

    t1_sum = text(190, 275, "Суммарна поляризація P = 0", size=13, color=MUTED, bold=True)

    # Права панель: E_ext > 0
    p2 = rect(380, 20, 340, 280, fill="#fcfcfc", stroke=MUTED, sw=1.2)
    t2 = text(550, 45, "Б: У зовнішньому полі (E > 0)", size=14, bold=True)

    # Заряджені пластини
    pl2_l = rect(400, 70, 14, 180, fill="#fdecea", stroke=POS, sw=2)
    pl2_r = rect(666, 70, 14, 180, fill="#eaf0fd", stroke=NEG, sw=2)
    q_pos = text(407, 60, "+Q", size=12, color=POS, bold=True)
    q_neg = text(673, 60, "−Q", size=12, color=NEG, bold=True)

    # Впорядковані диполі
    dips2 = [
        (460, 110), (530, 110), (600, 110),
        (460, 160), (530, 160), (600, 160),
        (460, 210), (530, 210), (600, 210)
    ]
    dip_elements2 = []
    for cx, cy in dips2:
        dip_elements2.append(line(cx - 15, cy, cx + 15, cy, color=LINE, sw=2))
        dip_elements2.append(minus(cx - 15, cy, r=7))
        dip_elements2.append(plus(cx + 15, cy, r=7))

    # Зв'язані поверхневі заряди
    b_neg = text(428, 165, "− σ_b", size=14, color=NEG, bold=True)
    b_pos = text(632, 165, "+ σ_b", size=14, color=POS, bold=True)

    # Стрілки полів
    e_ext_arrow = arrow(430, 80, 650, 80, color=POS, sw=2)
    lbl_e_ext = text(540, 72, "E_ext (зовнішнє поле)", size=11, color=POS, bold=True)

    e_ind_arrow = arrow(620, 240, 460, 240, color=NEG, sw=1.8)
    lbl_e_ind = text(540, 252, "E_ind (поле зв'язаних зарядів)", size=11, color=NEG, bold=True)

    t2_sum = text(550, 280, "Результуюче поле E = E_ext / ε_r", size=13, color=FIELD, bold=True)

    render(out_path, w, h, p1, t1, pl1_l, pl1_r, lbl_pl1, *dip_elements1, t1_sum,
           p2, t2, pl2_l, pl2_r, q_pos, q_neg, *dip_elements2, b_neg, b_pos,
           e_ext_arrow, lbl_e_ext, e_ind_arrow, lbl_e_ind, t2_sum)

def make_capacitor_dielectric():
    w, h = 740, 300
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'capacitor-dielectric.svg')

    # Вакуумний конденсатор
    p1 = rect(20, 20, 340, 260, fill="#ffffff", stroke=MUTED, sw=1.2)
    t1 = text(190, 45, "Вакуумний конденсатор C₀", size=15, bold=True)

    plate1_l = rect(70, 70, 16, 150, fill="#fdecea", stroke=POS, sw=2)
    plate1_r = rect(290, 70, 16, 150, fill="#eaf0fd", stroke=NEG, sw=2)

    # Вільні заряди на пластинах
    q1_l = text(78, 60, "+Q₀", size=13, color=POS, bold=True)
    q1_r = text(298, 60, "−Q₀", size=13, color=NEG, bold=True)

    # Поле у вакуумі
    arr1_1 = arrow(100, 100, 275, 100, color=FIELD, sw=1.8)
    arr1_2 = arrow(100, 145, 275, 145, color=FIELD, sw=1.8)
    arr1_3 = arrow(100, 190, 275, 190, color=FIELD, sw=1.8)
    lbl_e0 = text(187, 135, "E₀ = V / d", size=13, color=FIELD, bold=True)

    box1 = fitbox(60, 230, 260, 36, "Ємність: C₀ = ε₀ · A / d\nЗаряд: Q₀ = C₀ · V", size=12, fill="#f4f6f8")

    # Конденсатор з діелектриком
    p2 = rect(380, 20, 340, 260, fill="#ffffff", stroke=MUTED, sw=1.2)
    t2 = text(550, 45, "Конденсатор із діелектриком C", size=15, bold=True)

    # Діелектричний блок
    diel_block = rect(460, 70, 160, 150, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4)
    lbl_diel = text(540, 145, "Діелектрик (ε_r)", size=14, color=FIELD, bold=True)

    plate2_l = rect(430, 70, 16, 150, fill="#fdecea", stroke=POS, sw=2)
    plate2_r = rect(630, 70, 16, 150, fill="#eaf0fd", stroke=NEG, sw=2)

    # Більший заряд на пластинах при точу ж самому V
    q2_l = text(438, 60, "+Q = ε_r·Q₀", size=13, color=POS, bold=True)
    q2_r = text(638, 60, "−Q = −ε_r·Q₀", size=13, color=NEG, bold=True)

    # Зв'язаний заряд нейтралізує частину поля
    b2_l = text(472, 85, "−q_b", size=12, color=NEG, bold=True)
    b2_r = text(608, 85, "+q_b", size=12, color=POS, bold=True)

    box2 = fitbox(420, 230, 260, 36, "Ємність: C = ε_r · C₀\nНакопичений заряд у ε_r разів більший!", size=12, fill="#eafaf1", stroke=FIELD)

    render(out_path, w, h, p1, t1, plate1_l, plate1_r, q1_l, q1_r, arr1_1, arr1_2, arr1_3, lbl_e0, box1,
           p2, t2, diel_block, lbl_diel, plate2_l, plate2_r, q2_l, q2_r, b2_l, b2_r, box2)

def make_lorentz_local_field():
    w, h = 680, 340
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'lorentz-local-field.svg')

    title = text(340, 30, "Модель сфери Лоренца для локального поля E_loc", size=16, bold=True)

    # Фоновий діелектрик
    bg_box = rect(40, 50, 600, 240, fill="#fafafa", stroke=MUTED, sw=1.2)

    # Сфера Лоренца
    cavity = circle(340, 170, 75, fill="#ffffff", stroke=FIELD, sw=2)

    # Центральна молекула
    center_mol = circle(340, 170, 8, fill=POS, stroke=LINE, sw=1.5)
    lbl_mol = text(340, 145, "Молекула", size=12, bold=True)

    # Інші молекули всередині сфери
    mols = [(300, 150), (370, 140), (320, 210), (365, 195), (290, 185)]
    m_elems = []
    for mx, my in mols:
        m_elems.append(circle(mx, my, 5, fill="#d0d7de", stroke=LINE, sw=1))

    # Зв'язані заряди на внутрішній поверхні сфери Лоренца
    b_charges = [
        (275, 170, "−"), (280, 135, "−"), (280, 205, "−"),
        (405, 170, "+"), (400, 135, "+"), (400, 205, "+")
    ]
    b_elems = []
    for bx, by, ch in b_charges:
        col = POS if ch == "+" else NEG
        b_elems.append(text(bx, by, ch, size=14, color=col, bold=True))

    # Зовнішнє макроскопічне поле
    arr_e = arrow(60, 80, 620, 80, color=LINE, sw=2)
    lbl_e = text(140, 72, "Макроскопічне поле E", size=12, bold=True)

    # Вектор поляризації P
    arr_p = arrow(60, 260, 200, 260, color=FIELD, sw=2)
    lbl_p = text(130, 252, "Поляризація P⃗", size=12, color=FIELD, bold=True)

    # Формула локального поля
    f_box = fitbox(230, 295, 420, 36, "E_loc = E + P / (3·ε₀)   [для ізотропного кубічного діелектрика]", size=13, fill="#eafaf1", stroke=FIELD)

    render(out_path, w, h, title, bg_box, cavity, center_mol, lbl_mol, *m_elems, *b_elems,
           arr_e, lbl_e, arr_p, lbl_p, f_box)

def make_frequency_dispersion():
    w, h = 740, 360
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'frequency-dispersion.svg')

    title = text(370, 28, "Частотна дисперсія діелектричної проникності ε'(ω) та втрат ε''(ω)", size=15, bold=True)

    # Осі координат
    axis_x = arrow(70, 290, 700, 290, color=LINE, sw=1.8)
    axis_y = arrow(70, 290, 70, 50, color=LINE, sw=1.8)

    lbl_x = text(670, 312, "Частота f (Гц, лог-шкала)", size=12, bold=True)
    lbl_y = text(65, 40, "ε', ε''", size=13, bold=True)

    # Частотні позначки на осі X
    freqs = [
        (120, "10³"), (250, "10⁶"), (380, "10⁹ (СВЧ)"),
        (510, "10¹² (ІЧ)"), (630, "10¹⁵ (УФ)")
    ]
    f_elems = []
    for fx, flbl in freqs:
        f_elems.append(line(fx, 287, fx, 293, color=LINE, sw=1.5))
        f_elems.append(text(fx, 308, flbl, size=11, color=MUTED))

    # Зони поляризації
    grid1 = line(200, 60, 200, 285, color="#e0e0e0", sw=1, dash="4 4")
    grid2 = line(440, 60, 440, 285, color="#e0e0e0", sw=1, dash="4 4")
    grid3 = line(580, 60, 580, 285, color="#e0e0e0", sw=1, dash="4 4")

    z1 = text(135, 75, "Міжфазна", size=11, color=MUTED)
    z2 = text(320, 75, "Орієнтаційна (дипольна)", size=11, color=POS, bold=True)
    z3 = text(490, 75, "Іонна", size=11, color=NEG, bold=True)
    z4 = text(635, 75, "Електронна", size=11, color=FIELD, bold=True)

    # Схематичні криві ε' (дійсне) та ε'' (уявне/втрати)
    # ε' - спадаючі сходинки
    eps_real_path = ('<path d="M 70 100 L 150 100 Q 180 100 200 140 T 250 140 '
                     'L 350 140 Q 380 140 420 190 T 470 190 '
                     'L 530 190 Q 560 190 590 240 T 680 240" '
                     'fill="none" stroke="%s" stroke-width="2.5"/>' % FIELD)

    # ε'' - піки втрат у зонах релаксації/резонансу
    eps_loss_path = ('<path d="M 70 280 L 140 280 Q 180 280 200 170 T 230 280 '
                     'L 340 280 Q 400 280 420 180 T 450 280 '
                     'L 540 280 Q 570 280 590 200 T 610 280 L 680 280" '
                     'fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6 3"/>' % POS)

    lbl_eps_r = text(260, 125, "ε' (проникність)", size=13, color=FIELD, bold=True)
    lbl_eps_i = text(225, 195, "ε'' (втрати tan δ)", size=13, color=POS, bold=True)

    box_note = fitbox(200, 335, 480, 24, "Примітка: Вода має ε' ≈ 80 при НЧ, drops to ~70 на 2.45 ГГц (мікрохвильовка), and n² ≈ 1.77 у світлі", size=11, fill="#f4f6f8")

    render(out_path, w, h, title, axis_x, axis_y, lbl_x, lbl_y, *f_elems,
           grid1, grid2, grid3, z1, z2, z3, z4,
           eps_real_path, eps_loss_path, lbl_eps_r, lbl_eps_i, box_note)

if __name__ == '__main__':
    make_dipole_polarization()
    make_capacitor_dielectric()
    make_lorentz_local_field()
    make_frequency_dispersion()
    print("Generated 4 SVG figures for permittivity.")
