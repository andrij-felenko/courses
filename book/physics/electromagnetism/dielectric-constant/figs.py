# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def svg_ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (cx, cy, rx, ry, fill, stroke, sw))

def svg_circle(cx, cy, r, fill=FILL, stroke=LINE, sw=1.5, dash=None):
    d = (' stroke-dasharray="%s"' % dash) if dash else ''
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (cx, cy, r, fill, stroke, sw, d))

def polyline(pts, color=LINE, sw=1.5, dash=None):
    d = (' stroke-dasharray="%s"' % dash) if dash else ''
    pts_str = " ".join(["%.1f,%.1f" % (x, y) for x, y in pts])
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (pts_str, color, sw, d))

def make_dipole_mechanisms():
    w, h = 760, 420
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'dipole-mechanisms.svg')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    bg = rect(0, 0, w, h, fill="#ffffff", stroke="none")
    title = text(380, 25, "Чотири мікроскопічні механізми поляризації діелектриків", size=16, bold=True)

    # 1. Електронна поляризація
    b1 = rect(20, 55, 350, 165, fill="#fdfdfd", stroke=MUTED, sw=1.2)
    t1 = text(195, 75, "1. Електронна (зсув електронної хмари)", size=13, bold=True, color="#1f2328")
    # Атом без поля
    c1_1 = circle(100, 130, 32, fill="#eaf0fd", stroke="#0969da", sw=1.5)
    n1_1 = circle(100, 130, 8, fill="#d97706", stroke="none")
    lbl1_1 = text(100, 178, "E = 0 (симетрія)", size=11, color=MUTED)

    # Атом у полі
    c1_2 = svg_ellipse(290, 130, 42, 28, fill="#eaf0fd", stroke="#0969da", sw=1.5)
    n1_2 = circle(278, 130, 8, fill="#d97706", stroke="none")
    arr1 = arrow(220, 100, 340, 100, color=POS, sw=1.8)
    lbl_e1 = text(280, 92, "E⃗_ext", size=11, color=POS, bold=True)
    lbl1_2 = text(280, 178, "Зсув хмари (до 10¹⁵ Гц)", size=11, color=FIELD, bold=True)

    # 2. Іонна поляризація
    b2 = rect(390, 55, 350, 165, fill="#fdfdfd", stroke=MUTED, sw=1.2)
    t2 = text(565, 75, "2. Іонна (деформація решітки)", size=13, bold=True, color="#1f2328")
    # Решітка без поля
    ion1_a = plus(460, 130, r=12)
    ion1_b = minus(510, 130, r=12)
    l1 = line(472, 130, 498, 130, color=MUTED, sw=2, dash="3,3")
    lbl2_1 = text(485, 178, "E = 0 (d₀)", size=11, color=MUTED)

    # Решітка у полі
    ion2_a = plus(620, 130, r=12)
    ion2_b = minus(690, 130, r=12)
    l2 = line(632, 130, 678, 130, color=POS, sw=2)
    arr2 = arrow(590, 100, 710, 100, color=POS, sw=1.8)
    lbl_e2 = text(650, 92, "E⃗_ext", size=11, color=POS, bold=True)
    lbl2_2 = text(655, 178, "Збільшення d (до 10¹³ Гц)", size=11, color=FIELD, bold=True)

    # 3. Орієнтаційна поляризація
    b3 = rect(20, 235, 350, 170, fill="#fdfdfd", stroke=MUTED, sw=1.2)
    t3 = text(195, 255, "3. Орієнтаційна (повертання диполів)", size=13, bold=True, color="#1f2328")
    # Диполі
    d3_1 = line(70, 310, 110, 330, color=LINE, sw=2)
    m3_1 = minus(70, 310, r=7)
    p3_1 = plus(110, 330, r=7)

    d3_2 = line(110, 370, 80, 340, color=LINE, sw=2)
    m3_2 = minus(110, 370, r=7)
    p3_2 = plus(80, 340, r=7)

    lbl3_1 = text(100, 395, "E = 0 (хаос, T > 0)", size=11, color=MUTED)

    # У полі
    d3_3 = line(250, 310, 290, 310, color=LINE, sw=2)
    m3_3 = minus(250, 310, r=7)
    p3_3 = plus(290, 310, r=7)

    d3_4 = line(250, 360, 290, 360, color=LINE, sw=2)
    m3_4 = minus(250, 360, r=7)
    p3_4 = plus(290, 360, r=7)

    arr3 = arrow(220, 280, 320, 280, color=POS, sw=1.8)
    lbl_e3 = text(270, 272, "E⃗_ext", size=11, color=POS, bold=True)
    lbl3_2 = text(270, 395, "Орієнтація по полю (до 10¹⁰ Гц)", size=11, color=FIELD, bold=True)

    # 4. Міжповерхнева поляризація
    b4 = rect(390, 235, 350, 170, fill="#fdfdfd", stroke=MUTED, sw=1.2)
    t4 = text(565, 255, "4. Міжповерхнева (накопичення на межах)", size=13, bold=True, color="#1f2328")
    
    grain1 = rect(420, 285, 130, 90, fill="#f4f6f8", stroke=MUTED, sw=1.5)
    grain2 = rect(570, 285, 130, 90, fill="#eaf0fd", stroke=MUTED, sw=1.5)
    g_border = line(550, 285, 550, 375, color="#1f2328", sw=2.5)

    q_acc_m = text(540, 330, "−−−", size=12, color=NEG, bold=True)
    q_acc_p = text(560, 330, "+++", size=12, color=POS, bold=True)

    arr4 = arrow(420, 272, 680, 272, color=POS, sw=1.8)
    lbl_e4 = text(550, 264, "E⃗_ext", size=11, color=POS, bold=True)
    lbl4 = text(565, 395, "Захоплення носіїв дефектами (< 10³ Гц)", size=11, color=FIELD, bold=True)

    render(out_path, w, h, bg, title,
           b1, t1, c1_1, n1_1, lbl1_1, c1_2, n1_2, arr1, lbl_e1, lbl1_2,
           b2, t2, ion1_a, ion1_b, l1, lbl2_1, ion2_a, ion2_b, l2, arr2, lbl_e2, lbl2_2,
           b3, t3, d3_1, m3_1, p3_1, d3_2, m3_2, p3_2, lbl3_1, d3_3, m3_3, p3_3, d3_4, m3_4, p3_4, arr3, lbl_e3, lbl3_2,
           b4, t4, grain1, grain2, g_border, q_acc_m, q_acc_p, arr4, lbl_e4, lbl4)

def make_complex_permittivity():
    w, h = 760, 360
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'complex-permittivity.svg')

    bg = rect(0, 0, w, h, fill="#ffffff", stroke="none")
    title = text(380, 25, "Комплексна проникність та спектр релаксації Дебая", size=16, bold=True)

    # Осі координат
    ax_x = arrow(80, 300, 700, 300, color=LINE, sw=1.8)
    ax_y = arrow(80, 300, 80, 50, color=LINE, sw=1.8)

    lbl_x = text(670, 325, "Частота ω (логарифмічна шкала)", size=12, bold=True)
    lbl_y = text(75, 40, "ε', ε''", size=13, bold=True)

    # Крива ε' (дієлектрична проникність - накопичення)
    pts_real = []
    import math
    for px in range(80, 700, 5):
        x_norm = (px - 390) / 60.0
        val = 60 + 180 / (1.0 + math.exp(x_norm))
        pts_real.append((px, 300 - val))

    path_real = polyline(pts_real, color="#0969da", sw=2.5)

    # Крива ε'' (дієлектричні втрати - поглинання)
    pts_imag = []
    for px in range(80, 700, 5):
        x_norm = (px - 390) / 60.0
        val = 110 / (math.cosh(x_norm))
        pts_imag.append((px, 300 - val))

    path_imag = polyline(pts_imag, color="#cf222e", sw=2.5, dash="6,3")

    # Позначки рівнів
    l_eps_s = line(70, 300 - 240, 90, 300 - 240, color="#0969da", sw=1.5)
    t_eps_s = text(45, 300 - 236, "ε_s", size=13, bold=True, color="#0969da")

    l_eps_inf = line(70, 300 - 60, 90, 300 - 60, color="#0969da", sw=1.5)
    t_eps_inf = text(40, 300 - 56, "ε_∞", size=13, bold=True, color="#0969da")

    # Частота релаксації ω_0 = 1/tau
    l_w0 = line(390, 50, 390, 300, color=MUTED, sw=1.2, dash="3,3")
    t_w0 = text(390, 320, "ω₀ = 1/τ (релаксація)", size=12, bold=True, color="#1f2328")

    # Легенда
    leg1 = line(480, 75, 520, 75, color="#0969da", sw=2.5)
    t_leg1 = text(530, 79, "Дійсна частина ε' (накопичення енергії)", size=12, bold=True, color="#0969da")

    leg2 = line(480, 100, 520, 100, color="#cf222e", sw=2.5, dash="6,3")
    t_leg2 = text(530, 104, "Уявна частина ε'' (дієлектричні втрати)", size=12, bold=True, color="#cf222e")

    box_tan = fitbox(480, 125, 250, 50, "Тангенс кута втрат:\ntan δ = ε'' / ε'", size=12, fill="#fff8c5", stroke="#d97706")

    render(out_path, w, h, bg, title, ax_x, ax_y, lbl_x, lbl_y,
           path_real, path_imag, l_eps_s, t_eps_s, l_eps_inf, t_eps_inf,
           l_w0, t_w0, leg1, t_leg1, leg2, t_leg2, box_tan)

def make_local_field_clausius():
    w, h = 740, 340
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'local-field-clausius.svg')

    bg = rect(0, 0, w, h, fill="#ffffff", stroke="none")
    title = text(370, 25, "Сфера Лоренца та мікроскопічне локальне поле E_loc", size=16, bold=True)

    # Макроскопічний діелектрик
    diel = rect(40, 60, 660, 240, fill="#f8f9fa", stroke=LINE, sw=1.5)
    lbl_diel = text(120, 85, "Макроскопічне середовище", size=13, color=MUTED, bold=True)

    # Зовнішнє поле
    arr_e = arrow(60, 110, 680, 110, color=POS, sw=2)
    lbl_e = text(370, 100, "Макроскопічне поле E⃗", size=13, color=POS, bold=True)

    # Сфера Лоренца
    sphere = svg_circle(370, 200, 75, fill="#ffffff", stroke="#0969da", sw=2, dash="4,4")
    lbl_sph = text(370, 140, "Уявна сфера Лоренца", size=12, color="#0969da", bold=True)

    # Центральний атом
    atom = circle(370, 200, 10, fill="#d97706", stroke="none")
    lbl_atom = text(370, 225, "Центральний диполь", size=11, bold=True)

    # Зв'язані заряди на поверхні сфери Лоренца
    charge_neg = text(300, 200, "−−−", size=13, color=NEG, bold=True)
    charge_pos = text(440, 200, "+++", size=13, color=POS, bold=True)

    # Формула поля Лоренца
    fbox = fitbox(60, 220, 220, 65, "Локальне поле:\nE_loc = E + P / (3·ε₀)\n\nРівняння Клаузіуса—Моссотті:\n(ε_r − 1)/(ε_r + 2) = N·α / (3·ε₀)", size=11, fill="#f4f6f8", stroke=MUTED)

    render(out_path, w, h, bg, title, diel, lbl_diel, arr_e, lbl_e,
           sphere, lbl_sph, atom, lbl_atom, charge_neg, charge_pos, fbox)

def make_dielectric_materials_spectrum():
    w, h = 760, 300
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'dielectric-materials-spectrum.svg')

    bg = rect(0, 0, w, h, fill="#ffffff", stroke="none")
    title = text(380, 25, "Частотні діапазони механізмів поляризації", size=16, bold=True)

    # Осі частот
    ax = arrow(50, 240, 710, 240, color=LINE, sw=2)
    lbl_f = text(670, 265, "Частота f (Гц)", size=12, bold=True)

    # Частотні блоки
    b1 = rect(60, 80, 140, 120, fill="#fdecea", stroke=NEG, sw=1.5)
    t1 = text(130, 105, "Міжповерхнева", size=13, bold=True, color=NEG)
    t1_f = text(130, 130, "< 10³ Гц", size=12)
    t1_ex = text(130, 165, "Границі зерен,\nдефекти", size=11, color=MUTED)

    b2 = rect(215, 80, 150, 120, fill="#fff8c5", stroke="#d97706", sw=1.5)
    t2 = text(290, 105, "Орієнтаційна", size=13, bold=True, color="#d97706")
    t2_f = text(290, 130, "10³ – 10¹⁰ Гц", size=12)
    t2_ex = text(290, 165, "Полярні молекули\n(H₂O, полімери)", size=11, color=MUTED)

    b3 = rect(380, 80, 150, 120, fill="#eaf0fd", stroke="#0969da", sw=1.5)
    t3 = text(455, 105, "Іонна", size=13, bold=True, color="#0969da")
    t3_f = text(455, 130, "10¹¹ – 10¹³ Гц", size=12)
    t3_ex = text(455, 165, "Іонні кристали\n(ІЧ-діапазон)", size=11, color=MUTED)

    b4 = rect(545, 80, 150, 120, fill="#dafbe1", stroke=FIELD, sw=1.5)
    t4 = text(620, 105, "Електронна", size=13, bold=True, color=FIELD)
    t4_f = text(620, 130, "10¹⁴ – 10¹⁵ Гц", size=12)
    t4_ex = text(620, 165, "Усі атоми\n(Оптичний/УФ)", size=11, color=MUTED)

    # Позначки частот на осі
    m1 = line(60, 235, 60, 245, color=LINE, sw=1.5)
    tm1 = text(60, 255, "1 Гц", size=11)

    m2 = line(200, 235, 200, 245, color=LINE, sw=1.5)
    tm2 = text(200, 255, "1 кГц", size=11)

    m3 = line(365, 235, 365, 245, color=LINE, sw=1.5)
    tm3 = text(365, 255, "10 ГГц", size=11)

    m4 = line(530, 235, 530, 245, color=LINE, sw=1.5)
    tm4 = text(530, 255, "10 ТГц", size=11)

    m5 = line(695, 235, 695, 245, color=LINE, sw=1.5)
    tm5 = text(695, 255, "1 ПГц", size=11)

    render(out_path, w, h, bg, title, ax, lbl_f,
           b1, t1, t1_f, t1_ex, b2, t2, t2_f, t2_ex,
           b3, t3, t3_f, t3_ex, b4, t4, t4_f, t4_ex,
           m1, tm1, m2, tm2, m3, tm3, m4, tm4, m5, tm5)

if __name__ == '__main__':
    make_dipole_mechanisms()
    make_complex_permittivity()
    make_local_field_clausius()
    make_dielectric_materials_spectrum()
    print("All dielectric-constant figures generated successfully.")
