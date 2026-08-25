# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. arc-formation-physics.svg ─────────────────────────────────────────────
def fig_arc_formation_physics():
    W, H = 840, 360
    p = []
    
    stages = [
        ("1. Металевий контакт", "Струм тече через\nмікронерівності (a-плями)\nГустина струму > 10⁶ А/см²", 115),
        ("2. Рідкий місток", "Розігрів Джоулевим теплом\nПлавлення металу контакту\nУтворення шийки розплаву", 315),
        ("3. Вибух і пробій", "Розрив містка, пара металу\nТермо- та автоемісія\nЛавинна іонізація газу", 515),
        ("4. Стійка дуга", "Стовп плазми (4000–6000 K)\nПадіння напруги U_arc ~ 12–20 В\nІнтенсивна ерозія металу", 715)
    ]
    
    for title_text, desc_text, cx in stages:
        p.append(rect(cx - 95, 20, 190, 315, fill=FILL, stroke="#d0d7de", sw=1.2, rx=6))
        p.append(text(cx, 44, title_text, size=12, color=INK, bold=True))
        p.append(line(cx - 80, 56, cx + 80, 56, color="#e1e4e8", sw=1))
        p.append(mtext(cx, 265, desc_text.split("\n"), size=10, color=MUTED, lh=1.3))
    
    # Етап 1
    p.append(rect(65, 80, 100, 30, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    p.append(rect(65, 115, 100, 30, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    p.append(circle(115, 112, 4, fill=POS, stroke=POS, sw=1))
    p.append(text(115, 170, "a-пляма дотику", size=10, color=POS, bold=True))
    p.append(arrow(115, 70, 115, 80, color=POS, sw=1.5))
    p.append(text(115, 65, "I_нав", size=9, color=POS, bold=True))

    # Етап 2
    p.append(rect(265, 75, 100, 28, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    p.append(rect(265, 125, 100, 28, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    p.append('<path d="M 310 103 Q 315 114 310 125 L 320 125 Q 315 114 320 103 Z" fill="#e67e22" stroke="#d35400" stroke-width="1"/>')
    p.append(text(315, 170, "рідкий розплав", size=10, color="#d35400", bold=True))
    p.append(arrow(265, 89, 250, 89, color=NEG, sw=1.2))
    p.append(arrow(265, 139, 250, 139, color=NEG, sw=1.2))

    # Етап 3
    p.append(rect(465, 70, 100, 28, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    p.append(rect(465, 135, 100, 28, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    p.append(circle(515, 116, 12, fill="#fef3c7", stroke="#f59e0b", sw=1.2))
    p.append(line(505, 110, 498, 105, color=POS, sw=1))
    p.append(line(525, 110, 532, 105, color=POS, sw=1))
    p.append(line(505, 122, 498, 127, color=POS, sw=1))
    p.append(line(525, 122, 532, 127, color=POS, sw=1))
    p.append(text(515, 170, "вибух + e⁻ емісія", size=10, color=POS, bold=True))

    # Етап 4
    p.append(rect(665, 65, 100, 28, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    p.append(rect(665, 140, 100, 28, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    p.append('<path d="M 705 93 Q 695 116 705 140 L 725 140 Q 735 116 725 93 Z" fill="#fee2e2" stroke="#dc2626" stroke-width="1.8"/>')
    p.append(circle(715, 116, 5, fill="#ef4444", stroke="#b91c1c", sw=1))
    p.append(text(715, 170, "дугова плазма", size=10, color=POS, bold=True))
    p.append(text(715, 186, "T = 4000...6000 K", size=9, color=POS))

    # Стрілки
    p.append(arrow(213, 114, 218, 114, color=LINE, sw=1.8))
    p.append(arrow(413, 114, 418, 114, color=LINE, sw=1.8))
    p.append(arrow(613, 114, 618, 114, color=LINE, sw=1.8))

    render(os.path.join(OUT, "arc-formation-physics.svg"), W, H, *p,
           title="Фізика утворення комутаційної дуги при розмиканні контактів")


# ── 2. paschen-curve-and-limits.svg ──────────────────────────────────────────
def fig_paschen_curve_and_limits():
    W, H = 840, 360
    p = []
    
    # Лівий блок
    p.append(rect(30, 20, 370, 320, fill=FILL, stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(215, 42, "Крива Пашена: пробій газу", size=12, color=INK, bold=True))
    
    ox, oy = 85, 245
    p.append(line(ox, oy, ox + 280, oy, color=LINE, sw=1.5))
    p.append(line(ox, oy, ox, oy - 175, color=LINE, sw=1.5))
    p.append(arrow(ox + 275, oy, ox + 285, oy, color=LINE, sw=1.5))
    p.append(arrow(ox, oy - 170, ox, oy - 180, color=LINE, sw=1.5))
    
    p.append(text(ox + 280, oy + 18, "p · d", size=10, color=INK, anchor="end"))
    p.append(text(ox - 8, oy - 170, "U, В", size=10, color=INK, anchor="end"))
    
    curve_pts = [
        (95, 90), (110, 125), (135, 170), (160, 190), (180, 195),
        (210, 190), (250, 165), (295, 130), (345, 95)
    ]
    path_d = "M " + " L ".join(f"{x} {y}" for x, y in curve_pts)
    p.append(f'<path d="{path_d}" fill="none" stroke="{NEG}" stroke-width="2.2"/>')
    
    p.append(circle(180, 195, 4, fill=POS, stroke=POS, sw=1))
    p.append(line(ox, 195, 180, 195, color="#f87171", sw=1, dash="3,3"))
    p.append(line(180, 195, 180, oy, color="#f87171", sw=1, dash="3,3"))
    p.append(text(ox - 6, 199, "≈ 327 В", size=9, color=POS, anchor="end", bold=True))
    p.append(text(180, oy + 14, "(p·d)_min", size=9, color=POS))
    
    p.append(text(125, 90, "Мало зіткнень", size=9, color=MUTED))
    p.append(text(125, 104, "(вакуум/малий d)", size=9, color=MUTED))
    p.append(text(305, 75, "Втрати енергії e⁻", size=9, color=MUTED))
    p.append(text(305, 89, "(великий зазор)", size=9, color=MUTED))
    
    p.append(mtext(215, 290, [
        "Зазор d < 5 мкм: вмикається автоемісія (E > 10⁷ В/см),",
        "пробій стається навіть при напрузі U < 300 В!"
    ], size=9, color=POS, lh=1.3, bold=True))

    # Правий блок
    p.append(rect(420, 20, 390, 320, fill=FILL, stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(615, 42, "Порогові умови існування дуги", size=12, color=INK, bold=True))
    
    dox, doy = 480, 175
    p.append(line(dox, doy, dox + 300, doy, color=LINE, sw=1.5))
    p.append(line(dox, doy, dox, doy - 110, color=LINE, sw=1.5))
    p.append(arrow(dox + 295, doy, dox + 305, doy, color=LINE, sw=1.5))
    p.append(arrow(dox, doy - 105, dox, doy - 115, color=LINE, sw=1.5))
    p.append(text(dox + 300, doy + 18, "Струм I, А", size=9, color=INK, anchor="end"))
    p.append(text(dox - 10, doy - 105, "Напруга U, В", size=9, color=INK, anchor="end"))
    
    p.append(rect(dox + 60, doy - 90, 220, 65, fill="#fee2e2", stroke="none"))
    p.append(line(dox + 60, doy, dox + 60, doy - 90, color=POS, sw=1.5, dash="4,3"))
    p.append(line(dox, doy - 25, dox + 280, doy - 25, color=POS, sw=1.5, dash="4,3"))
    p.append(text(dox + 60, doy + 14, "I_arc (≈0.4 А)", size=9, color=POS))
    p.append(text(dox - 6, doy - 21, "U_arc (≈12 В)", size=9, color=POS, anchor="end"))
    p.append(text(dox + 160, doy - 60, "ЗОНА СТІЙКОЇ ДУГИ", size=10, color=POS, bold=True))
    p.append(text(dox + 160, doy - 44, "(U > U_arc та I > I_arc)", size=9, color=POS))
    p.append(text(615, 215, "Бездугове розмикання: U < 12 В або I < 0.4 А", size=9, color=FIELD, bold=True))

    p.append(rect(435, 235, 360, 90, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(445, 252, "Метал контакту", size=9, color=MUTED, anchor="start", bold=True))
    p.append(text(620, 252, "U_arc (поріг)", size=9, color=MUTED, bold=True))
    p.append(text(730, 252, "I_arc (поріг)", size=9, color=MUTED, bold=True))
    p.append(line(435, 260, 795, 260, color="#e2e8f0", sw=1))
    
    rows_m = [
        ("Срібло (Ag, AgNi)", "11.5...12.0 В", "0.40...0.45 А"),
        ("Мідь (Cu), Золото (Au)", "12.5...15.0 В", "0.38...0.43 А"),
        ("Вольфрам (W)", "15.0...16.0 В", "0.80...1.00 А")
    ]
    my = 276
    for mname, uval, ival in rows_m:
        p.append(text(445, my, mname, size=9, color=INK, anchor="start"))
        p.append(text(620, my, uval, size=9, color=POS, bold=True))
        p.append(text(730, my, ival, size=9, color=POS, bold=True))
        my += 16

    render(os.path.join(OUT, "paschen-curve-and-limits.svg"), W, H, *p,
           title="Крива Пашена та порогові умови горіння електричної дуги")


# ── 3. contact-erosion-mechanisms.svg ────────────────────────────────────────
def fig_contact_erosion_mechanisms():
    W, H = 840, 360
    p = []
    
    boxes = [
        ("Анодно-катодне перенесення", 155),
        ("Окиснення й нагар", 420),
        ("Брязкіт і зварювання (Bounce)", 685)
    ]
    
    for title_text, cx in boxes:
        p.append(rect(cx - 120, 20, 240, 320, fill=FILL, stroke="#d0d7de", sw=1.2, rx=6))
        p.append(text(cx, 44, title_text, size=12, color=INK, bold=True))
        p.append(line(cx - 105, 56, cx + 105, 56, color="#e1e4e8", sw=1))

    # Секція 1
    p.append('<path d="M 95 75 L 135 75 Q 155 98 175 75 L 215 75 L 215 95 L 95 95 Z" fill="#e2e8f0" stroke="#475569" stroke-width="1.5"/>')
    p.append(text(155, 68, "Анод (+) — кратер вигоряння", size=9, color=POS, bold=True))
    
    p.append(circle(155, 112, 5, fill="#fee2e2", stroke="#dc2626", sw=1.2))
    p.append(text(205, 114, "e⁻ потік", size=9, color=NEG))
    p.append(arrow(185, 120, 165, 105, color=NEG, sw=1.2))

    p.append('<path d="M 95 150 L 135 150 Q 155 128 175 150 L 215 150 L 215 130 L 95 130 Z" fill="#e2e8f0" stroke="#475569" stroke-width="1.5"/>')
    p.append(text(155, 168, "Катод (−) — наростання конуса", size=9, color=NEG, bold=True))
    
    p.append(mtext(155, 215, [
        "У колах DC струм тече в один бік.",
        "Електрони бомбардують анод,",
        "вибиваючи метал.",
        "Утворюється голка та ямка,",
        "що веде до заклинювання."
    ], size=9, color=MUTED, lh=1.3))

    # Секція 2
    p.append(rect(345, 75, 150, 20, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    p.append(rect(355, 95, 130, 5, fill="#9a3412", stroke="#9a3412", sw=1))
    
    p.append(rect(355, 125, 130, 5, fill="#9a3412", stroke="#9a3412", sw=1))
    p.append(rect(345, 130, 150, 20, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    
    p.append(text(420, 115, "Оксидна / вуглецева плівка", size=9, color="#9a3412", bold=True))
    
    p.append(mtext(420, 215, [
        "Висока температура дуги",
        "окиснює базовий метал (Cu, Ag).",
        "Органічні пари розкладаються",
        "на вуглець (нагар).",
        "R_контакту зростає в сотні разів,",
        "викликаючи саморозігрів."
    ], size=9, color=MUTED, lh=1.3))

    # Секція 3
    bx, by = 600, 140
    p.append(line(bx, by, bx + 160, by, color=LINE, sw=1.2))
    p.append(line(bx, by, bx, by - 60, color=LINE, sw=1.2))
    p.append(f'<path d="M {bx} {by-50} L {bx+30} {by-50} L {bx+35} {by} L {bx+50} {by} L {bx+55} {by-50} L {bx+75} {by-50} L {bx+80} {by} L {bx+90} {by} L {bx+95} {by-50} L {bx+150} {by-50}" fill="none" stroke="{POS}" stroke-width="1.8"/>')
    p.append(text(bx + 60, by - 62, "Мікророзмикання (1–5 мс)", size=9, color=POS, bold=True))
    
    p.append(mtext(685, 215, [
        "Пружний удар контактів при",
        "вмиканні викликає брязкіт.",
        "Пусковий струм (Inrush I) у мить",
        "розриву запалює мікродуги.",
        "Метал плавиться, і контакти",
        "намертво зварюються."
    ], size=9, color=MUTED, lh=1.3))

    render(os.path.join(OUT, "contact-erosion-mechanisms.svg"), W, H, *p,
           title="Механізми ерозії, деградації та зварювання контактів")


# ── 4. suppression-topologies-comparison.svg ─────────────────────────────────
def fig_suppression_topologies_comparison():
    W, H = 840, 360
    p = []
    
    col_w = 185
    xs = [40, 240, 440, 640]
    topos = [
        ("1. Зворотний діод", "Постійний струм (DC)\nU_peak = V_cc + 0.7 В\nt_вимк = повільне (4–5 L/R)\nРизик затягування дуги!", xs[0]),
        ("2. Діод + TVS / Zener", "Постійний струм (DC)\nU_peak = V_cc + V_z\nt_вимк = ШВИДКЕ (у 5–10 разів)\nІдеально для реле!", xs[1]),
        ("3. RC-демпфер", "AC і DC сумісний\nОбмежує dV/dt та f_дзвону\nГасить енергію на R\nСтрум витоку на AC!", xs[2]),
        ("4. Варистор (MOV)", "AC і DC мережі\nСиметричний кламп\nВелика поглинана енергія\nДеградує від імпульсів", xs[3])
    ]
    
    for title_text, desc_text, cx in topos:
        p.append(rect(cx, 20, col_w, 320, fill=FILL, stroke="#d0d7de", sw=1.2, rx=6))
        p.append(text(cx + col_w/2, 44, title_text, size=11, color=INK, bold=True))
        p.append(line(cx + 15, 56, cx + col_w - 15, 56, color="#e1e4e8", sw=1))
        p.append(mtext(cx + col_w/2, 255, desc_text.split("\n"), size=9, color=MUTED, lh=1.3))

    # Схема 1
    sx, sy = xs[0] + col_w/2, 130
    p.append(rect(sx - 35, sy - 40, 30, 45, fill="#ffffff", stroke="#475569", sw=1.2, rx=3))
    p.append(text(sx - 20, sy - 18, "L", size=10, color=INK, bold=True))
    p.append(line(sx + 20, sy - 40, sx + 20, sy + 5, color=LINE, sw=1.2))
    p.append(f'<polygon points="{sx+12},{sy-12} {sx+28},{sy-12} {sx+20}, {sy-28}" fill="{NEG}" stroke="{NEG}"/>')
    p.append(line(sx + 12, sy - 28, sx + 28, sy - 28, color=NEG, sw=1.5))
    p.append(line(sx - 20, sy - 40, sx + 20, sy - 40, color=LINE, sw=1.2))
    p.append(line(sx - 20, sy + 5, sx + 20, sy + 5, color=LINE, sw=1.2))
    p.append(rect(sx - 65, sy + 25, 130, 45, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
    p.append(line(sx - 55, sy + 60, sx + 55, sy + 60, color=LINE, sw=1))
    p.append(f'<path d="M {sx-55} {sy+35} L {sx-30} {sy+35} L {sx-30} {sy+58} L {sx+50} {sy+58}" fill="none" stroke="{FIELD}" stroke-width="1.5"/>')
    p.append(text(sx, sy + 45, "Низька U, довгий спад I", size=9, color=MUTED))

    # Схема 2
    sx = xs[1] + col_w/2
    p.append(rect(sx - 35, sy - 40, 30, 45, fill="#ffffff", stroke="#475569", sw=1.2, rx=3))
    p.append(text(sx - 20, sy - 18, "L", size=10, color=INK, bold=True))
    p.append(line(sx + 20, sy - 40, sx + 20, sy + 5, color=LINE, sw=1.2))
    p.append(f'<polygon points="{sx+14},{sy-28} {sx+26},{sy-28} {sx+20}, {sy-38}" fill="{NEG}" stroke="{NEG}"/>')
    p.append(f'<polygon points="{sx+14},{sy-8} {sx+26},{sy-8} {sx+20}, {sy+2}" fill="{POS}" stroke="{POS}"/>')
    p.append(line(sx - 20, sy - 40, sx + 20, sy - 40, color=LINE, sw=1.2))
    p.append(line(sx - 20, sy + 5, sx + 20, sy + 5, color=LINE, sw=1.2))
    p.append(rect(sx - 65, sy + 25, 130, 45, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
    p.append(line(sx - 55, sy + 60, sx + 55, sy + 60, color=LINE, sw=1))
    p.append(f'<path d="M {sx-55} {sy+55} L {sx-30} {sy+55} L {sx-30} {sy+35} L {sx-10} {sy+58} L {sx+50} {sy+58}" fill="none" stroke="{POS}" stroke-width="1.5"/>')
    p.append(text(sx, sy + 45, "Кламп V_z, швидкий спад", size=9, color=POS, bold=True))

    # Схема 3
    sx = xs[2] + col_w/2
    p.append(rect(sx - 35, sy - 40, 30, 45, fill="#ffffff", stroke="#475569", sw=1.2, rx=3))
    p.append(text(sx - 20, sy - 18, "L", size=10, color=INK, bold=True))
    p.append(rect(sx + 12, sy - 38, 16, 18, fill="#ffffff", stroke=INK, sw=1.2))
    p.append(text(sx + 20, sy - 25, "R", size=9, color=INK))
    p.append(line(sx + 10, sy - 10, sx + 30, sy - 10, color=INK, sw=1.5))
    p.append(line(sx + 10, sy - 6, sx + 30, sy - 6, color=INK, sw=1.5))
    p.append(text(sx + 36, sy - 6, "C", size=9, color=INK))
    p.append(line(sx + 20, sy - 40, sx + 20, sy - 38, color=LINE, sw=1.2))
    p.append(line(sx + 20, sy - 20, sx + 20, sy - 10, color=LINE, sw=1.2))
    p.append(line(sx + 20, sy - 6, sx + 20, sy + 5, color=LINE, sw=1.2))
    p.append(line(sx - 20, sy - 40, sx + 20, sy - 40, color=LINE, sw=1.2))
    p.append(line(sx - 20, sy + 5, sx + 20, sy + 5, color=LINE, sw=1.2))
    p.append(rect(sx - 65, sy + 25, 130, 45, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
    p.append(line(sx - 55, sy + 60, sx + 55, sy + 60, color=LINE, sw=1))
    p.append(f'<path d="M {sx-55} {sy+58} L {sx-30} {sy+58} Q {sx-15} {sy+30} {sx} {sy+48} T {sx+25} {sy+55} L {sx+50} {sy+58}" fill="none" stroke="{NEG}" stroke-width="1.5"/>')
    p.append(text(sx, sy + 40, "М'яке згасання LC", size=9, color=NEG))

    # Схема 4
    sx = xs[3] + col_w/2
    p.append(rect(sx - 35, sy - 40, 30, 45, fill="#ffffff", stroke="#475569", sw=1.2, rx=3))
    p.append(text(sx - 20, sy - 18, "L", size=10, color=INK, bold=True))
    p.append(rect(sx + 10, sy - 28, 20, 16, fill="#ffffff", stroke=INK, sw=1.2))
    p.append(line(sx + 5, sy - 8, sx + 35, sy - 32, color=INK, sw=1.2))
    p.append(line(sx + 5, sy - 8, sx + 5, sy - 4, color=INK, sw=1.2))
    p.append(line(sx + 20, sy - 40, sx + 20, sy - 28, color=LINE, sw=1.2))
    p.append(line(sx + 20, sy - 12, sx + 20, sy + 5, color=LINE, sw=1.2))
    p.append(line(sx - 20, sy - 40, sx + 20, sy - 40, color=LINE, sw=1.2))
    p.append(line(sx - 20, sy + 5, sx + 20, sy + 5, color=LINE, sw=1.2))
    p.append(rect(sx - 65, sy + 25, 130, 45, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
    p.append(line(sx - 55, sy + 60, sx + 55, sy + 60, color=LINE, sw=1))
    p.append(f'<path d="M {sx-55} {sy+58} L {sx-30} {sy+58} L {sx-25} {sy+38} L {sx-10} {sy+38} L {sx-5} {sy+58} L {sx+50} {sy+58}" fill="none" stroke="#d97706" stroke-width="1.5"/>')
    p.append(text(sx, sy + 45, "Жорсткий кламп MOV", size=9, color="#d97706"))

    render(os.path.join(OUT, "suppression-topologies-comparison.svg"), W, H, *p,
           title="Порівняння чотирьох топологій гасіння перенапруг та захисту контактів")


# ── 5. rc-damping-waveforms.svg ──────────────────────────────────────────────
def fig_rc_damping_waveforms():
    W, H = 840, 360
    p = []
    
    p.append(rect(40, 20, 760, 320, fill=FILL, stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(420, 45, "Перехідний процес розмикання: вплив коефіцієнта демпфування ζ", size=13, color=INK, bold=True))
    
    ox, oy = 100, 270
    p.append(line(ox, oy, ox + 650, oy, color=LINE, sw=1.5))
    p.append(line(ox, oy, ox, oy - 200, color=LINE, sw=1.5))
    p.append(arrow(ox + 640, oy, ox + 655, oy, color=LINE, sw=1.5))
    p.append(arrow(ox, oy - 195, ox, oy - 205, color=LINE, sw=1.5))
    
    p.append(text(ox + 650, oy + 20, "Час t", size=10, color=INK, anchor="end"))
    p.append(text(ox - 10, oy - 195, "Напруга на ключі V(t)", size=10, color=INK, anchor="end"))
    
    p.append(line(ox, oy - 70, ox + 630, oy - 70, color="#94a3b8", sw=1, dash="4,4"))
    p.append(text(ox - 8, oy - 66, "V_cc", size=10, color=MUTED, anchor="end"))

    # 1. Недодемпфована
    pts_under = []
    for step in range(300):
        t = step / 30.0
        val = 1.0 - math.exp(-0.35 * t) * (math.cos(2.2 * t) + 0.15 * math.sin(2.2 * t))
        x = ox + step * 2.0
        y = oy - val * 70.0
        pts_under.append((x, y))
    path_under = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_under)
    p.append(f'<path d="{path_under}" fill="none" stroke="{POS}" stroke-width="2.2"/>')

    # 2. Критично демпфована
    pts_crit = []
    for step in range(300):
        t = step / 30.0
        val = 1.0 - (1.0 + 1.2 * t) * math.exp(-1.2 * t)
        x = ox + step * 2.0
        y = oy - val * 70.0
        pts_crit.append((x, y))
    path_crit = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_crit)
    p.append(f'<path d="{path_crit}" fill="none" stroke="{FIELD}" stroke-width="2.2"/>')

    # 3. Передемпфована
    pts_over = []
    for step in range(300):
        t = step / 30.0
        val = 1.0 + 0.6 * math.exp(-0.3 * t) - 1.6 * math.exp(-1.8 * t)
        x = ox + step * 2.0
        y = oy - val * 70.0
        pts_over.append((x, y))
    path_over = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_over)
    p.append(f'<path d="{path_over}" fill="none" stroke="{NEG}" stroke-width="2.0" stroke-dasharray="6,3"/>')

    p.append(line(ox + 42, oy - 128, ox + 150, oy - 150, color=POS, sw=1))
    p.append(text(ox + 155, oy - 150, "V_max > 2·V_cc (небезпека пробою!)", size=9, color=POS, anchor="start", bold=True))

    lx, ly = 500, 90
    p.append(rect(lx, ly, 280, 110, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    
    p.append(line(lx + 15, ly + 25, lx + 45, ly + 25, color=POS, sw=2.5))
    p.append(text(lx + 55, ly + 29, "R < 2·√(L/C) (Недодемпфовано: дзвін)", size=9, color=POS, anchor="start", bold=True))
    
    p.append(line(lx + 15, ly + 55, lx + 45, ly + 55, color=FIELD, sw=2.5))
    p.append(text(lx + 55, ly + 59, "R = 2·√(L/C) (Критичне: оптимум)", size=9, color=FIELD, anchor="start", bold=True))

    p.append(line(lx + 15, ly + 85, lx + 45, ly + 85, color=NEG, sw=2, dash="5,3"))
    p.append(text(lx + 55, ly + 89, "R > 2·√(L/C) (Передемпфовано: I₀·R)", size=9, color=NEG, anchor="start", bold=True))

    p.append(text(420, 312, "Характеристичний опір Z₀ = √(L/C) визначає масштаб. R_opt = (0.5...1.0)·Z₀ для мінімізації як піка, так і dV/dt.", size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "rc-damping-waveforms.svg"), W, H, *p,
           title="Перехідні процеси та осцилограми напруги при різних значеннях опору демпфування")


# ── 6. rcd-flyback-clamp.svg ─────────────────────────────────────────────────
def fig_rcd_flyback_clamp():
    W, H = 840, 360
    p = []
    
    # Лівий блок
    p.append(rect(30, 20, 370, 320, fill=FILL, stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(215, 45, "Схема RCD-снабера (Flyback Clamp)", size=12, color=INK, bold=True))
    
    p.append(text(60, 80, "+ V_in (DC)", size=10, color=POS, bold=True))
    p.append(line(60, 90, 340, 90, color=LINE, sw=1.5))
    
    p.append(rect(300, 110, 30, 35, fill="#ffffff", stroke="#475569", sw=1.2, rx=3))
    p.append(text(315, 128, "L_m", size=9, color=INK, bold=True))
    p.append(rect(300, 155, 30, 25, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    p.append(text(315, 170, "L_leak", size=9, color=POS, bold=True))
    p.append(line(315, 90, 315, 110, color=LINE, sw=1.5))
    p.append(line(315, 145, 315, 155, color=LINE, sw=1.5))
    p.append(line(315, 180, 315, 205, color=LINE, sw=1.5))

    p.append(line(160, 90, 160, 115, color=LINE, sw=1.5))
    p.append(line(240, 90, 240, 115, color=LINE, sw=1.5))
    p.append(rect(148, 115, 24, 40, fill="#ffffff", stroke=INK, sw=1.2))
    p.append(text(160, 138, "R_s", size=9, color=INK, bold=True))
    p.append(line(225, 130, 255, 130, color=INK, sw=1.8))
    p.append(line(225, 136, 255, 136, color=INK, sw=1.8))
    p.append(text(268, 134, "C_s", size=9, color=INK, bold=True))
    p.append(line(240, 115, 240, 130, color=LINE, sw=1.5))
    p.append(line(240, 136, 240, 165, color=LINE, sw=1.5))
    p.append(line(160, 155, 160, 165, color=LINE, sw=1.5))
    p.append(line(160, 165, 240, 165, color=LINE, sw=1.5))
    
    p.append(line(200, 165, 200, 180, color=LINE, sw=1.5))
    p.append(f'<polygon points="{200},{180} {192},{192} {208},{192}" fill="{NEG}" stroke="{NEG}"/>')
    p.append(line(192, 180, 208, 180, color=NEG, sw=1.5))
    p.append(text(175, 188, "D_s", size=9, color=NEG, bold=True))
    p.append(line(200, 192, 200, 205, color=LINE, sw=1.5))
    p.append(line(200, 205, 315, 205, color=LINE, sw=1.5))

    p.append(rect(295, 215, 40, 45, fill="#e2e8f0", stroke="#334155", sw=1.5, rx=3))
    p.append(text(315, 238, "MOSFET", size=9, color=INK, bold=True))
    p.append(line(315, 205, 315, 215, color=LINE, sw=1.5))
    p.append(line(315, 260, 315, 280, color=LINE, sw=1.5))
    p.append(text(315, 295, "GND", size=9, color=MUTED))
    p.append(line(285, 240, 295, 240, color=LINE, sw=1.2))
    p.append(text(265, 243, "PWM", size=9, color=MUTED))

    # Правий блок
    p.append(rect(420, 20, 390, 320, fill=FILL, stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(615, 45, "Осцилограма V_ds на стоку MOSFET", size=12, color=INK, bold=True))
    
    eox, eoy = 475, 270
    p.append(line(eox, eoy, eox + 305, eoy, color=LINE, sw=1.5))
    p.append(line(eox, eoy, eox, eoy - 200, color=LINE, sw=1.5))
    p.append(arrow(eox + 300, eoy, eox + 310, eoy, color=LINE, sw=1.5))
    p.append(arrow(eox, eoy - 195, eox, eoy - 205, color=LINE, sw=1.5))
    p.append(text(eox + 305, eoy + 18, "Час t", size=9, color=INK, anchor="end"))
    p.append(text(eox - 8, eoy - 195, "V_ds, В", size=9, color=INK, anchor="end"))
    
    p.append(line(eox, eoy - 45, eox + 295, eoy - 45, color="#94a3b8", sw=1, dash="3,3"))
    p.append(text(eox - 6, eoy - 42, "V_in", size=9, color=MUTED, anchor="end"))
    
    p.append(line(eox, eoy - 95, eox + 295, eoy - 95, color="#3b82f6", sw=1, dash="3,3"))
    p.append(text(eox - 6, eoy - 92, "V_in + V_or", size=9, color=NEG, anchor="end"))

    p.append(line(eox, eoy - 145, eox + 295, eoy - 145, color=POS, sw=1, dash="3,3"))
    p.append(text(eox - 6, eoy - 142, "V_clamp (снабер)", size=9, color=POS, anchor="end", bold=True))

    p.append(line(eox, eoy - 180, eox + 295, eoy - 180, color="#b91c1c", sw=1.2, dash="4,2"))
    p.append(text(eox + 290, eoy - 184, "V_DS(max) запас", size=9, color="#b91c1c", anchor="end", bold=True))

    p.append(f'<path d="M {eox+40} {eoy} L {eox+45} {eoy-200} L {eox+55} {eoy-95}" fill="none" stroke="{POS}" stroke-width="1.5" stroke-dasharray="3,3"/>')
    p.append(text(eox + 50, eoy - 205, "БЕЗ снабера: ПРОБІЙ!", size=9, color=POS, bold=True))

    p.append(f'<path d="M {eox} {eoy} L {eox+40} {eoy} L {eox+45} {eoy-145} L {eox+75} {eoy-145} Q {eox+85} {eoy-95} {eox+110} {eoy-95} L {eox+180} {eoy-95} Q {eox+200} {eoy-45} {eox+220} {eoy-45} L {eox+250} {eoy} L {eox+295} {eoy}" fill="none" stroke="{FIELD}" stroke-width="2.2"/>')

    p.append(text(eox + 60, eoy - 155, "Кламп L_leak", size=9, color=FIELD, bold=True))
    p.append(text(eox + 140, eoy - 105, "Передача у вихід (V_or)", size=9, color=NEG))
    p.append(text(eox + 210, eoy - 30, "Квазірезонанс", size=9, color=MUTED))

    render(os.path.join(OUT, "rcd-flyback-clamp.svg"), W, H, *p,
           title="RCD-снабер у Flyback-перетворювачі та фіксація перенапруги індуктивності розсіювання")


def main():
    fig_arc_formation_physics()
    fig_paschen_curve_and_limits()
    fig_contact_erosion_mechanisms()
    fig_suppression_topologies_comparison()
    fig_rc_damping_waveforms()
    fig_rcd_flyback_clamp()
    print("All figures generated successfully.")

if __name__ == "__main__":
    main()
