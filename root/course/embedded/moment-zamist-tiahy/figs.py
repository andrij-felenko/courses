# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Баланс сил і моментів на колесі ровера на схилі ─────────────────
def f_force_balance():
    W, H = 760, 460
    frags = []
    frags.append(text(W/2, 28, "Баланс сил і крутного моменту колеса на схилі", size=16, bold=True))

    x1, y1 = 60, 380
    x2, y2 = 690, 150
    frags.append(line(x1, y1, x2, y2, color=MUTED, sw=2.5))
    frags.append(line(x1, y1, x2, y1, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(text(140, y1 - 10, "кут схилу θ", size=12, color=MUTED))

    R = 85
    cx = 404
    cy = 185

    frags.append(circle(cx, cy, R, fill="#f0f4f8", stroke=LINE, sw=2.5))
    frags.append(circle(cx, cy, 14, fill="#ffffff", stroke=INK, sw=2))
    frags.append(circle(cx, cy, 4, fill=INK, stroke=INK, sw=1))

    frags.append(line(cx, cy, cx - int(0.939*R), cy - int(0.343*R), color=MUTED, sw=1.5, dash="3 3"))
    frags.append(text(cx - 45, cy - 30, "r", size=13, color=MUTED, italic=True, bold=True))

    frags.append('<path d="M %d %d A 32 32 0 1 1 %d %d" fill="none" stroke="%s" stroke-width="2.5" marker-end="url(#arrow)"/>' %
                 (cx - 28, cy - 14, cx + 18, cy - 26, POS))
    frags.append(text(cx + 42, cy - 36, "T_колеса", size=13, color=POS, bold=True))

    contact_x = 375
    contact_y = 265

    frags.append(arrow(contact_x, contact_y, contact_x + int(0.939*130), contact_y - int(0.343*130), color=FIELD, sw=2.5))
    frags.append(text(contact_x + int(0.939*130) + 10, contact_y - int(0.343*130) - 12, "F_тяга = T / r", size=13, color=FIELD, bold=True))

    frags.append(arrow(contact_x, contact_y, contact_x - int(0.939*70), contact_y + int(0.343*70), color=NEG, sw=2))
    frags.append(text(contact_x - int(0.939*70) - 15, contact_y + int(0.343*70) + 20, "F_rr (опір коченню)", size=12, color=NEG))

    frags.append(arrow(cx, cy, cx - int(0.939*90), cy + int(0.343*90), color=POS, sw=2))
    frags.append(text(cx - int(0.939*90) - 40, cy + int(0.343*90) + 16, "F_схил = m·g·sin(θ)", size=12, color=POS))

    frags.append(arrow(cx, cy, cx - int(0.939*50), cy + int(0.343*50) - 25, color="#d35400", sw=2))
    frags.append(text(cx - int(0.939*50) - 45, cy + int(0.343*50) - 32, "F_розгін = m·a", size=12, color="#d35400"))

    frags.append(arrow(cx, cy, cx, cy + 100, color=INK, sw=2))
    frags.append(text(cx + 8, cy + 115, "W = m·g", size=13, color=INK, bold=True))

    frags.append(arrow(contact_x, contact_y, contact_x - int(0.343*80), contact_y - int(0.939*80), color=MUTED, sw=2))
    frags.append(text(contact_x - int(0.343*80) - 15, contact_y - int(0.939*80) - 10, "N = m·g·cos(θ)", size=12, color=MUTED))

    box_txt = "Рівновага тяги:  F_тяга ≥ F_rr + F_схил + F_розгін  =>  T_колеса = F_тяга · r_колеса\nМежа зчеплення:   T_макс ≤ μ · N · r_колеса  (інакше колесо буксує)"
    frags.append(fitbox(140, 395, 480, 52, box_txt, size=12, pad=6, fill="#f8fafc", stroke=LINE))

    render(os.path.join(OUT, 'force-balance.svg'), W, H, *frags)


# ── Фігура 2: Механічна характеристика двигуна (T–ω) і робочі зони ───────────
def f_torque_speed_zones():
    W, H = 760, 440
    frags = []
    frags.append(text(W/2, 28, "Механічна характеристика електродвигуна: зони роботи та ККД", size=16, bold=True))

    ox, oy = 90, 360
    gw, gh = 580, 290
    frags.append(arrow(ox, oy, ox + gw + 30, oy, color=LINE, sw=2))
    frags.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=2))

    frags.append(text(ox + gw + 35, oy + 5, "ω (оберти)", size=13, color=INK, anchor="start", bold=True))
    frags.append(text(ox - 10, oy - gh - 20, "T (момент)", size=13, color=INK, anchor="end", bold=True))

    y_stall = oy - 260
    x_noload = ox + 520

    y_cont = oy - 75
    frags.append(rect(ox, y_cont, 420, oy - y_cont, fill="#eafaf0", stroke="#27ae60", sw=1.2, rx=0))
    frags.append(text(ox + 210, (oy + y_cont)/2 + 4, "Тривалий режим (S1) — безпечний тепловий баланс", size=12, color="#27ae60", bold=True))

    frags.append(rect(ox, y_stall + 40, 220, y_cont - (y_stall + 40), fill="#fef9e7", stroke="#d35400", sw=1.2, rx=0))
    frags.append(text(ox + 110, (y_cont + y_stall + 40)/2 + 4, "Піковий розгін (S3)", size=11, color="#d35400", bold=True))

    frags.append(rect(ox, y_stall, 100, 40, fill="#fdecea", stroke=POS, sw=1.2, rx=0))
    frags.append(text(ox + 50, y_stall + 24, "Перегрів!", size=10, color=POS, bold=True))

    frags.append(line(ox, y_stall, x_noload, oy, color=POS, sw=3))

    p_pts = []
    for i in range(21):
        t_frac = i / 20.0
        px_i = ox + t_frac * 520
        p_val = 4 * 160 * t_frac * (1 - t_frac)
        py_i = oy - p_val
        p_pts.append((px_i, py_i))
    for i in range(len(p_pts)-1):
        frags.append(line(p_pts[i][0], p_pts[i][1], p_pts[i+1][0], p_pts[i+1][1], color=NEG, sw=2, dash="5 3"))
    frags.append(text(ox + 260, oy - 170, "P_мех = T · ω (максимум на ω_хх / 2)", size=11, color=NEG, bold=True))

    frags.append(circle(ox, y_stall, 4, fill=POS, stroke=POS, sw=1))
    frags.append(text(ox - 10, y_stall + 4, "T_пуск (Stall)", size=12, color=POS, anchor="end", bold=True))

    frags.append(circle(ox, y_cont, 4, fill="#27ae60", stroke="#27ae60", sw=1))
    frags.append(text(ox - 10, y_cont + 4, "T_ном (Rated)", size=12, color="#27ae60", anchor="end", bold=True))

    frags.append(circle(x_noload, oy, 4, fill=POS, stroke=POS, sw=1))
    frags.append(text(x_noload, oy + 20, "ω_хх (No-load)", size=12, color=POS, anchor="middle", bold=True))

    opt_x = ox + 410
    opt_y = oy - (260 * (1 - 410.0/520))
    frags.append(circle(opt_x, opt_y, 6, fill="#ffffff", stroke="#8e44ad", sw=2))
    frags.append(arrow(opt_x + 50, opt_y - 35, opt_x + 8, opt_y - 6, color="#8e44ad", sw=1.8))
    frags.append(text(opt_x + 55, opt_y - 40, "Пік ККД η_макс (75–85% ω_хх)", size=11, color="#8e44ad", bold=True))

    render(os.path.join(OUT, 'torque-speed-zones.svg'), W, H, *frags)


# ── Фігура 3: Порівняння 4 типів приводів і редукторів ровера ─────────────────
def f_gearbox_types():
    W, H = 760, 460
    frags = []
    frags.append(text(W/2, 26, "Топології приводів ровера: компроміс ККД, реверсивності та габаритів", size=16, bold=True))

    cards = [
        {
            "x": 40, "y": 55, "w": 325, "h": 180,
            "title": "Планетарний редуктор (Planetary)",
            "color": "#27ae60", "bg": "#f0fdf4",
            "items": [
                "• Передавальне число i: 4:1 – 100:1 (багатоступеневий)",
                "• ККД: 75–90% (падає як η^n зі ступенями)",
                "• Зворотний хід: високий (ровер котиться зі схилу)",
                "• Застосування: тягові колеса всюдиходів, 4WD/6WD"
            ]
        },
        {
            "x": 395, "y": 55, "w": 325, "h": 180,
            "title": "Черв'ячний редуктор (Worm Drive)",
            "color": "#d35400", "bg": "#fefaf6",
            "items": [
                "• Передавальне число i: 20:1 – 80:1 в 1 ступені",
                "• ККД: 45–70% (високе тертя ковзання витків)",
                "• Зворотний хід: самогальмування (тримає схил без струму!)",
                "• Застосування: роботи-маніпулятори, круті ухили, лебідки"
            ]
        },
        {
            "x": 40, "y": 255, "w": 325, "h": 180,
            "title": "Циклоїдний / Хвильовий (Cycloidal/Strain-wave)",
            "color": "#2980b9", "bg": "#f0f8ff",
            "items": [
                "• Передавальне число i: 30:1 – 150:1 в 1 ступені",
                "• ККД: 70–85%, нульовий люфт (zero-backlash)",
                "• Висока жорсткість на скручування й ударні піки",
                "• Застосування: поворотні модулі осей, точні шарніри"
            ]
        },
        {
            "x": 395, "y": 255, "w": 325, "h": 180,
            "title": "Прямий привід (Direct Drive / Hub Motor)",
            "color": "#8e44ad", "bg": "#faf5ff",
            "items": [
                "• Передавальне число i: 1:1 (без зубчастих передач)",
                "• ККД: 85–95%, нульовий знос механіки, тиша",
                "• Недолік: малий крутний момент на низьких RPM",
                "• Застосування: швидкісні легкі патрульні ровери"
            ]
        }
    ]

    for c in cards:
        frags.append(rect(c["x"], c["y"], c["w"], c["h"], fill=c["bg"], stroke=c["color"], sw=1.8, rx=8))
        frags.append(text(c["x"] + c["w"]/2, c["y"] + 24, c["title"], size=13, color=c["color"], bold=True))
        frags.append(line(c["x"] + 12, c["y"] + 36, c["x"] + c["w"] - 12, c["y"] + 36, color=c["color"], sw=1, dash="3 3"))
        for idx, item in enumerate(c["items"]):
            frags.append(text(c["x"] + 14, c["y"] + 62 + idx * 27, item, size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, 'gearbox-types.svg'), W, H, *frags)


# ── Фігура 4: Тепловий баланс обмотки й обмеження струму ──────────────────────
def f_thermal_envelope():
    W, H = 760, 420
    frags = []
    frags.append(text(W/2, 28, "Тепловий баланс двигуна: нагрів I²·R та часові межі перевантаження", size=16, bold=True))

    ox, oy = 80, 350
    gw, gh = 590, 270
    frags.append(arrow(ox, oy, ox + gw + 30, oy, color=LINE, sw=2))
    frags.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=2))

    frags.append(text(ox + gw + 35, oy + 5, "Час t (хвилини / секунди)", size=12, color=INK, anchor="start", bold=True))
    frags.append(text(ox - 10, oy - gh - 20, "Температура обмотки T (°C)", size=12, color=INK, anchor="end", bold=True))

    y_iso = oy - 220
    frags.append(line(ox, y_iso, ox + gw, y_iso, color=POS, sw=1.5, dash="6 3"))
    frags.append(text(ox + gw - 8, y_iso - 8, "Критична межа ізоляції (155°C / 180°C) — вигорання", size=11, color=POS, anchor="end", bold=True))

    y_mag = oy - 140
    frags.append(line(ox, y_mag, ox + gw, y_mag, color="#d35400", sw=1.5, dash="4 3"))
    frags.append(text(ox + gw - 8, y_mag - 8, "Межа деградації NdFeB магнітів (~90–100°C)", size=11, color="#d35400", anchor="end"))

    y_amb = oy - 20
    frags.append(line(ox, y_amb, ox + gw, y_amb, color=MUTED, sw=1, dash="2 2"))
    frags.append(text(ox - 10, y_amb + 4, "T_навк (25°C)", size=11, color=MUTED, anchor="end"))

    pts1 = []
    for i in range(25):
        t = i / 24.0
        x_i = ox + t * gw
        temp = 20 + 75 * (1 - pow(2.718, -3.5 * t))
        pts1.append((x_i, oy - temp))
    for i in range(len(pts1)-1):
        frags.append(line(pts1[i][0], pts1[i][1], pts1[i+1][0], pts1[i+1][1], color="#27ae60", sw=2.5))
    frags.append(text(ox + 460, oy - 105, "I = I_ном: стабільний тепловий баланс (S1)", size=11, color="#27ae60", bold=True))

    pts2 = []
    for i in range(16):
        t = i / 15.0
        x_i = ox + t * (gw * 0.5)
        temp = 20 + 200 * (1 - pow(2.718, -2.5 * t))
        pts2.append((x_i, oy - temp))
    for i in range(len(pts2)-1):
        frags.append(line(pts2[i][0], pts2[i][1], pts2[i+1][0], pts2[i+1][1], color="#d35400", sw=2.5))
    frags.append(text(ox + 180, oy - 175, "I = 2·I_ном (розгін, макс 30–60 с)", size=11, color="#d35400", bold=True))

    pts3 = []
    for i in range(10):
        t = i / 9.0
        x_i = ox + t * (gw * 0.15)
        temp = 20 + 350 * (t * 0.7)
        pts3.append((x_i, oy - temp))
    for i in range(len(pts3)-1):
        frags.append(line(pts3[i][0], pts3[i][1], pts3[i+1][0], pts3[i+1][1], color=POS, sw=3))
    frags.append(text(ox + 95, oy - 235, "I = I_пуск (заклинювання: дим через 3–6 с!)", size=11, color=POS, bold=True))

    render(os.path.join(OUT, 'thermal-envelope.svg'), W, H, *frags)


if __name__ == '__main__':
    f_force_balance()
    f_torque_speed_zones()
    f_gearbox_types()
    f_thermal_envelope()
    print("All figures generated successfully.")
