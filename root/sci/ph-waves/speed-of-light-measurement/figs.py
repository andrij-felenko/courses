# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Астрономічний метод Ремера (1676)
# ═══════════════════════════════════════════════════════════════════════════
def fig_roemer_method():
    W, H = 760, 440
    f = []
    f.append(text(W / 2, 28, "Астрономічний метод Ремера: затримка затемнень супутника Юпітера Іо", 16, INK, 'middle', bold=True))

    # Сонце в центрі
    sun_x, sun_y = 260, 220
    f.append(circle(sun_x, sun_y, 30, fill='#fef08a', stroke='#eab308', sw=2))
    f.append(text(sun_x, sun_y + 4, "Сонце", 11, INK, 'middle', bold=True))

    # Орбіта Землі
    r_earth = 120
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,4"/>' % (sun_x, sun_y, r_earth))
    f.append(text(sun_x, sun_y - r_earth - 12, "Орбіта Землі (1 АО)", 11, MUTED, 'middle'))

    # Земля в сполученні (E1 - найближче до Юпітера)
    e1_x = sun_x + r_earth
    e1_y = sun_y
    f.append(circle(e1_x, e1_y, 10, fill='#60a5fa', stroke='#2563eb', sw=2))
    f.append(text(e1_x + 18, e1_y - 16, "Земля E₁", 12, INK, 'start', bold=True))
    f.append(text(e1_x + 18, e1_y + 6, "(найближча)", 10, MUTED, 'start'))

    # Земля у протистоянні (E2 - найвіддаленіша від Юпітера)
    e2_x = sun_x - r_earth
    e2_y = sun_y
    f.append(circle(e2_x, e2_y, 10, fill='#93c5fd', stroke='#1d4ed8', sw=2))
    f.append(text(e2_x - 18, e2_y - 16, "Земля E₂", 12, INK, 'end', bold=True))
    f.append(text(e2_x - 18, e2_y + 6, "(найвіддаленіша)", 10, MUTED, 'end'))

    # Напрямок руху Землі
    f.append(arrow(sun_x, sun_y - r_earth, sun_x - 40, sun_y - r_earth, color='#2563eb', sw=1.8))
    f.append(text(sun_x - 20, sun_y - r_earth - 18, "v_орб", 10, '#2563eb', 'middle', bold=True, italic=True))

    # Юпітер праворуч
    jup_x, jup_y = 620, 220
    f.append(circle(jup_x, jup_y, 34, fill='#fed7aa', stroke='#ea580c', sw=2))
    f.append(text(jup_x, jup_y + 4, "Юпітер", 12, INK, 'middle', bold=True))

    # Тінь Юпітера (конус тіні ззаду від Сонця)
    shadow_pts = "%f,%f %f,%f %f,%f" % (jup_x + 20, jup_y - 32, jup_x + 120, jup_y - 45, jup_x + 120, jup_y + 45)
    f.append('<polygon points="%s" fill="#e2e8f0" opacity="0.6" stroke="#94a3b8" stroke-dasharray="3,3"/>' % shadow_pts)
    f.append(text(jup_x + 70, jup_y + 4, "Тінь Юпітера", 10, MUTED, 'middle', italic=True))

    # Орбіта Іо навколо Юпітера
    r_io = 60
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#f97316" stroke-width="1.5" stroke-dasharray="3,3"/>' % (jup_x, jup_y, r_io))

    # Супутник Іо заходить у тінь
    io_x = jup_x + r_io * math.cos(math.pi / 4)
    io_y = jup_y - r_io * math.sin(math.pi / 4)
    f.append(circle(io_x, io_y, 6, fill='#fde047', stroke='#ca8a04', sw=1.5))
    f.append(text(io_x + 16, io_y - 12, "Супутник Іо", 11, INK, 'start', bold=True))

    # Світлові промені від Іо до Землі
    # Промінь до E1
    f.append(line(io_x, io_y, e1_x + 10, e1_y, color=POS, sw=1.8))
    f.append(text((io_x + e1_x) / 2 + 10, e1_y - 30, "Шлях світла L₁", 11, POS, 'middle', bold=True))

    # Промінь до E2 (довший на діаметр орбіти Землі 2R)
    f.append(line(io_x, io_y, e2_x - 10, e2_y, color=NEG, sw=1.8, dash='6,3'))
    f.append(text((io_x + e2_x) / 2 - 30, e2_y + 35, "Додатковий шлях ΔL = 2 R_орб", 11, NEG, 'middle', bold=True))

    # Інформаційний блок знизу
    info_txt = "Час затримки появи Іо з тіні: Δt = ΔL / c ≈ 1000 с (22 хв за вимірами Ремера 1676 року)"
    tb, tw, th = textbox(W / 2, H - 40, info_txt, size=12, pad=8, fill='#f8fafc', stroke='#cbd5e1', sw=1.5)
    f.append(tb)

    render(os.path.join(IMG, 'roemer-astronomical-method.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Лабораторний метод зубчастого колеса Фізо (1849)
# ═══════════════════════════════════════════════════════════════════════════
def fig_fizeau_toothed_wheel():
    W, H = 760, 460
    f = []
    f.append(text(W / 2, 28, "Наземний оптико-механічний метод Фізо із зубчастим колесом", 16, INK, 'middle', bold=True))

    # 1. Джерело світла (ліворуч)
    src_x, src_y = 60, 220
    f.append(circle(src_x, src_y, 14, fill='#fef08a', stroke='#eab308', sw=2))
    f.append(text(src_x, src_y - 24, "Джерело S", 12, INK, 'middle', bold=True))

    # Фокусуюча лінза L1
    f.append(rect(src_x + 40, src_y - 25, 8, 50, fill='#e0f2fe', stroke='#0284c7', sw=1.5, rx=4))
    f.append(text(src_x + 44, src_y - 32, "Лінза L₁", 10, MUTED, 'middle'))

    # Напівпрозоре дзеркало M1
    bs_x, bs_y = 160, 220
    f.append('<g transform="rotate(-45 %.1f %.1f)">' % (bs_x, bs_y))
    f.append(rect(bs_x - 3, bs_y - 25, 6, 50, fill='#e0f2fe', stroke=NEG, sw=1.5, rx=2))
    f.append(line(bs_x - 3, bs_y - 25, bs_x - 3, bs_y + 25, color=POS, sw=2))
    f.append('</g>')
    f.append(text(bs_x, bs_y - 38, "Напівпрозоре дзеркало", 11, INK, 'middle', bold=True))

    # Детектор/Окуляр внизу
    eye_x, eye_y = bs_x, 370
    f.append(rect(eye_x - 35, eye_y - 12, 70, 24, fill='#334155', stroke=INK, sw=1.5, rx=4))
    f.append(text(eye_x, eye_y + 4, "Окуляр / Детектор", 10, '#ffffff', 'middle', bold=True))

    # 2. Зубчасте колесо, що обертається
    wheel_x, wheel_y = 280, 220
    f.append(circle(wheel_x, wheel_y, 45, fill='#f1f5f9', stroke=INK, sw=2))
    # Зубці колеса
    for i in range(12):
        ang = i * (2 * math.pi / 12)
        tx = wheel_x + 45 * math.cos(ang)
        ty = wheel_y + 45 * math.sin(ang)
        tx2 = wheel_x + 55 * math.cos(ang)
        ty2 = wheel_y + 55 * math.sin(ang)
        f.append(line(tx, ty, tx2, ty2, color=INK, sw=4))
    f.append(circle(wheel_x, wheel_y, 8, fill='#94a3b8', stroke=INK, sw=1.5))
    f.append(text(wheel_x, wheel_y - 65, "Зубчасте колесо (N зубців)", 12, INK, 'middle', bold=True))
    # Стрілка обертання
    f.append(arrow(wheel_x + 30, wheel_y - 45, wheel_x + 45, wheel_y - 30, color=POS, sw=2))
    f.append(text(wheel_x + 52, wheel_y - 50, "ω = 2πν", 11, POS, 'start', bold=True, italic=True))

    # 3. Віддалене плоске дзеркало M2 (Сюрен -> Монмартр, L = 8.63 км)
    m2_x, m2_y = 660, 220
    f.append(rect(m2_x - 4, m2_y - 35, 8, 70, fill='#94a3b8', stroke=INK, sw=2, rx=2))
    f.append(line(m2_x - 4, m2_y - 35, m2_x - 4, m2_y + 35, color=NEG, sw=2))
    f.append(text(m2_x + 14, m2_y - 12, "Віддалене дзеркало M₂", 12, INK, 'start', bold=True))
    f.append(text(m2_x + 14, m2_y + 8, "(на відстані L = 8.63 км)", 10, MUTED, 'start'))

    # Лінза L2 біля віддаленого дзеркала
    f.append(rect(m2_x - 45, m2_y - 30, 8, 60, fill='#e0f2fe', stroke='#0284c7', sw=1.5, rx=4))
    f.append(text(m2_x - 41, m2_y - 38, "Об'єктив L₂", 10, MUTED, 'middle'))

    # 4. Хід світлових імпульсів
    # Від джерела до дзеркала M1
    f.append(line(src_x + 14, src_y, bs_x - 15, bs_y, color=POS, sw=2))
    # Від M1 через проміжок між зубцями до M2
    f.append(line(bs_x + 15, bs_y - 2, m2_x - 4, m2_y - 2, color='#dc2626', sw=2))
    f.append(text((wheel_x + m2_x) / 2, m2_y - 14, "Прямий світловий імпульс", 11, '#dc2626', 'middle', bold=True))

    # Зворотний промінь від M2 до колеса й окуляра
    f.append(line(m2_x - 4, m2_y + 2, bs_x + 15, bs_y + 2, color='#2563eb', sw=2, dash='5,3'))
    f.append(text((wheel_x + m2_x) / 2, m2_y + 18, "Зворотний промінь (після t = 2L/c)", 11, '#2563eb', 'middle', bold=True))

    # Зворотне відбиття від M1 до окуляра
    f.append(line(bs_x, bs_y + 15, eye_x, eye_y - 12, color='#2563eb', sw=2, dash='5,3'))

    # Умова затемнення (зубець перекриває зворотний промінь)
    formula_txt = "Умова першого затемнення в окулярі: c = 4 N L ν  (де ν — частота обертання)"
    tb, tw, th = textbox(W / 2, H - 40, formula_txt, size=13, pad=10, fill='#fefce8', stroke='#eab308', sw=1.8, bold=True)
    f.append(tb)

    render(os.path.join(IMG, 'fizeau-toothed-wheel.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Метод обертового дзеркала Фуко — Майкельсона (1850 / 1926)
# ═══════════════════════════════════════════════════════════════════════════
def fig_foucault_rotating_mirror():
    W, H = 760, 480
    f = []
    f.append(text(W / 2, 28, "Метод обертового кутового дзеркала (Фуко — Майкельсон)", 16, INK, 'middle', bold=True))

    # 1. Точкове джерело світла S та шкала вимірювання зміщення
    src_x, src_y = 80, 160
    f.append(circle(src_x, src_y, 12, fill='#fef08a', stroke='#eab308', sw=2))
    f.append(text(src_x, src_y - 20, "Джерело S", 11, INK, 'middle', bold=True))

    # Вимірювальна шкала поруч із джерелом
    scale_x, scale_y = 80, 280
    f.append(rect(scale_x - 20, scale_y - 40, 40, 80, fill='#f8fafc', stroke=INK, sw=1.5, rx=2))
    for i in range(-30, 31, 10):
        f.append(line(scale_x + 10, scale_y + i, scale_x + 18, scale_y + i, color=INK, sw=1))
    f.append(text(scale_x - 30, scale_y + 4, "Шкала Δx", 11, INK, 'end', bold=True))

    # 2. Обертове дзеркало R (восьмигранне дзеркальна призма Майкельсона)
    r_x, r_y = 300, 220
    # Восьмикутник для призми
    oct_pts = []
    r_oct = 35
    for i in range(8):
        ang = i * (2 * math.pi / 8) + math.pi / 8
        px = r_x + r_oct * math.cos(ang)
        py = r_y + r_oct * math.sin(ang)
        oct_pts.append("%.1f,%.1f" % (px, py))
    f.append('<polygon points="%s" fill="#e2e8f0" stroke="%s" stroke-width="2"/>' % (" ".join(oct_pts), INK))
    f.append(circle(r_x, r_y, 6, fill='#94a3b8', stroke=INK, sw=1.5))
    f.append(text(r_x, r_y - 50, "Обертове восьмигранне дзеркало R", 12, INK, 'middle', bold=True))

    # Стрілка кутової швидкості обертання ω
    f.append(arrow(r_x + 25, r_y - 35, r_x + 40, r_y - 20, color=POS, sw=2))
    f.append(text(r_x + 48, r_y - 35, "ω = 2πν", 11, POS, 'start', bold=True, italic=True))

    # 3. Віддалене увігнуте/плоске дзеркало M (Маунт-Вільсон -> Маунт-Сан-Антоніо, L = 35 км)
    m_x, m_y = 660, 220
    f.append(rect(m_x - 4, m_y - 45, 8, 90, fill='#94a3b8', stroke=INK, sw=2, rx=2))
    f.append(line(m_x - 4, m_y - 45, m_x - 4, m_y + 45, color=NEG, sw=2.5))
    f.append(text(m_x + 14, m_y - 12, "Віддалене дзеркало M", 12, INK, 'start', bold=True))
    f.append(text(m_x + 14, m_y + 8, "База L (35 км)", 11, MUTED, 'start'))

    # 4. Промені світла
    # Прямий промінь S -> R -> M
    f.append(line(src_x + 12, src_y, r_x - 20, r_y - 15, color=POS, sw=2))
    f.append(line(r_x + 25, r_y, m_x - 4, m_y, color='#dc2626', sw=2))
    f.append(text((r_x + m_x) / 2, m_y - 12, "Прямий промінь (L)", 11, '#dc2626', 'middle', bold=True))

    # Зворотний промінь M -> R' (після повороту дзеркала R на кут Δθ)
    # Зворотне дзеркало повернулося на кут Δθ за час t = 2L/c
    f.append(line(m_x - 4, m_y + 4, r_x + 25, r_y + 6, color='#2563eb', sw=2, dash='5,3'))
    # Зміщений відбитий промінь до шкали
    f.append(line(r_x - 20, r_y + 15, scale_x + 18, scale_y + 15, color='#2563eb', sw=2))
    f.append(text((src_x + r_x) / 2 + 10, scale_y + 32, "Кутове зміщення променя Δθ = 4 ω L / c", 11, '#2563eb', 'middle', bold=True))

    # Математична формула
    formula_txt = "Швидкість світла за кутовим зміщенням зображення:  c = (4 · ω · L) / Δθ"
    tb, tw, th = textbox(W / 2, H - 40, formula_txt, size=13, pad=10, fill='#eff6ff', stroke='#3b82f6', sw=1.8, bold=True)
    f.append(tb)

    render(os.path.join(IMG, 'foucault-michelson-rotating-mirror.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Сучасний електрооптичний фазовий метод (LiDAR / ТоФ)
# ═══════════════════════════════════════════════════════════════════════════
def fig_laser_phase_shift_method():
    W, H = 760, 460
    f = []
    f.append(text(W / 2, 28, "Сучасна електрооптична фазово-часопролітна техніка (LiDAR / ToF)", 16, INK, 'middle', bold=True))

    # 1. Генератор ВЧ сигналу та Лазерний діод
    rf_x, rf_y = 80, 140
    tb1, tw1, th1 = textbox(rf_x, rf_y, "ВЧ Генератор\nf_m = 10..100 МГц", size=11, pad=8, fill='#e0e7ff', stroke='#4338ca', sw=1.5, bold=True)
    f.append(tb1)

    laser_x, laser_y = 80, 240
    f.append(rect(laser_x - 45, laser_y - 20, 90, 40, fill='#fee2e2', stroke='#dc2626', sw=2, rx=4))
    f.append(text(laser_x, laser_y + 4, "Лазерний діод", 11, '#991b1b', 'middle', bold=True))

    # Зв'язок ВЧ генератора з лазером
    f.append(arrow(rf_x, rf_y + th1 / 2, laser_x, laser_y - 20, color='#4338ca', sw=1.8))
    f.append(text(rf_x + 35, (rf_y + laser_y) / 2 - 5, "Модуляція", 10, '#4338ca', 'start', italic=True))

    # 2. Оптичний світлодільник BS
    bs_x, bs_y = 240, 240
    f.append('<g transform="rotate(-45 %.1f %.1f)">' % (bs_x, bs_y))
    f.append(rect(bs_x - 3, bs_y - 25, 6, 50, fill='#e0f2fe', stroke=NEG, sw=1.5, rx=2))
    f.append(line(bs_x - 3, bs_y - 25, bs_x - 3, bs_y + 25, color=POS, sw=2))
    f.append('</g>')

    # 3. Опорний фотодетектор D_ref (внизу від BS)
    ref_x, ref_y = bs_x, 370
    f.append(rect(ref_x - 40, ref_y - 15, 80, 30, fill='#f1f5f9', stroke=INK, sw=1.5, rx=4))
    f.append(text(ref_x, ref_y + 4, "Опорний ФД (D_ref)", 10, INK, 'middle', bold=True))

    # 4. Об'єкт / Цільове віддалене дзеркало M
    m_x, m_y = 640, 240
    f.append(rect(m_x - 4, m_y - 40, 8, 80, fill='#94a3b8', stroke=INK, sw=2, rx=2))
    f.append(line(m_x - 4, m_y - 40, m_x - 4, m_y + 40, color=POS, sw=2.5))
    f.append(text(m_x + 14, m_y - 10, "Віддалена ціль / Дзеркало", 11, INK, 'start', bold=True))
    f.append(text(m_x + 14, m_y + 8, "Відстань L", 11, MUTED, 'start'))

    # 5. Вимірювальний фотодетектор D_meas
    meas_x, meas_y = 440, 370
    f.append(rect(meas_x - 45, meas_y - 15, 90, 30, fill='#dcfce7', stroke='#16a34a', sw=1.8, rx=4))
    f.append(text(meas_x, meas_y + 4, "Вимірювальний ФД", 10, '#15803d', 'middle', bold=True))

    # 6. Фазометр / Обчислювач фазового зсуву
    pm_x, pm_y = 340, 370
    # Зв'язок від детектора D_ref та D_meas до Фазометра
    f.append(rect(pm_x - 35, pm_y - 15, 70, 30, fill='#fef3c7', stroke='#d97706', sw=1.8, rx=4))
    f.append(text(pm_x, pm_y + 4, "Фазометр Δφ", 11, '#b45309', 'middle', bold=True))

    f.append(line(ref_x + 40, ref_y, pm_x - 35, pm_y, color='#4338ca', sw=1.5))
    f.append(line(meas_x - 45, meas_y, pm_x + 35, pm_y, color='#15803d', sw=1.5))

    # 7. Хід випромінювання
    # Лазер -> BS
    f.append(line(laser_x + 45, laser_y, bs_x - 15, bs_y, color='#dc2626', sw=2))
    # BS -> Опорний ФД (відбитий опорний імпульс)
    f.append(line(bs_x, bs_y + 15, ref_x, ref_y - 15, color='#4338ca', sw=1.8, dash='4,3'))
    # BS -> Ціль M (прямий вимірювальний пучок)
    f.append(line(bs_x + 15, bs_y - 2, m_x - 4, m_y - 2, color='#dc2626', sw=2))
    f.append(text((bs_x + m_x) / 2, m_y - 14, "Модульований світловий пучок E(t) = E₀ cos(2π f_m t)", 11, '#dc2626', 'middle', bold=True))
    # Ціль M -> Вимірювальний ФД (відбитий затриманий пучок)
    f.append(line(m_x - 4, m_y + 2, meas_x + 20, meas_y - 15, color='#16a34a', sw=1.8, dash='5,3'))

    # Формульне пояснення
    formula_txt = "Зв'язок фазового різниці Δφ та швидкості світла c:  Δφ = 2π f_m · (2L / c)  ⇒  c = (4π f_m L) / Δφ"
    tb, tw, th = textbox(W / 2, H - 35, formula_txt, size=12, pad=10, fill='#fef8ec', stroke='#f59e0b', sw=1.8, bold=True)
    f.append(tb)

    render(os.path.join(IMG, 'laser-phase-shift-method.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Main execution
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    fig_roemer_method()
    fig_fizeau_toothed_wheel()
    fig_foucault_rotating_mirror()
    fig_laser_phase_shift_method()
    print("SVG figures generated successfully with render()")
