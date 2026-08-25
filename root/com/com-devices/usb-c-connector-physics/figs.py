# -*- coding: utf-8 -*-
"""Фігури до теми «Фізика роз'єму USB-C».
Імпортує спільний svgkit зі scripts/ (НЕ переписувати тут). Вивід — у ./img/.
Запуск:  python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

VBUS_COL = "#c0392b"
GND_COL  = "#2c3e50"
CC_COL   = "#27ae60"
SBU_COL  = "#8e44ad"
USB2_COL = "#d35400"
SS_TX    = "#2980b9"
SS_RX    = "#16a085"
HOT      = POS
COOL     = NEG


# ── 1. Геометрія та матриця 24 контактів (точкова симетрія 180°) ─────────────
def fig_pinout_geometry():
    W, H = 880, 480
    p = []
    
    ox, oy = 40, 50
    rw, rh = 800, 250
    p.append(rect(ox, oy, rw, rh, fill="#ffffff", stroke="#2c3e50", sw=2.5, rx=24))
    p.append(rect(ox + 10, oy + 10, rw - 20, rh - 20, fill="#f8f9fa", stroke="#bdc3c7", sw=1.2, rx=16))
    
    tw, th = 740, 160
    tx, ty = ox + 30, oy + 40
    p.append(rect(tx, ty, tw, th, fill="#eef2f5", stroke="#7f8c8d", sw=1.8, rx=8))
    
    col_w = 56
    gap = 5
    start_x = tx + 14
    
    row_a = [
        ("A1", "GND", GND_COL, "#d5dbdb"),
        ("A2", "TX1+", SS_TX, "#d4e6f1"),
        ("A3", "TX1−", SS_TX, "#d4e6f1"),
        ("A4", "VBUS", VBUS_COL, "#fadbd8"),
        ("A5", "CC1", CC_COL, "#d4efdf"),
        ("A6", "D+", USB2_COL, "#fdebd0"),
        ("A7", "D−", USB2_COL, "#fdebd0"),
        ("A8", "SBU1", SBU_COL, "#ebdef0"),
        ("A9", "VBUS", VBUS_COL, "#fadbd8"),
        ("A10", "RX2−", SS_RX, "#d1f2eb"),
        ("A11", "RX2+", SS_RX, "#d1f2eb"),
        ("A12", "GND", GND_COL, "#d5dbdb")
    ]
    
    row_b = [
        ("B12", "GND", GND_COL, "#d5dbdb"),
        ("B11", "RX1+", SS_RX, "#d1f2eb"),
        ("B10", "RX1−", SS_RX, "#d1f2eb"),
        ("B9", "VBUS", VBUS_COL, "#fadbd8"),
        ("B8", "SBU2", SBU_COL, "#ebdef0"),
        ("B7", "D−", USB2_COL, "#fdebd0"),
        ("B6", "D+", USB2_COL, "#fdebd0"),
        ("B5", "CC2", CC_COL, "#d4efdf"),
        ("B4", "VBUS", VBUS_COL, "#fadbd8"),
        ("B3", "TX2−", SS_TX, "#d4e6f1"),
        ("B2", "TX2+", SS_TX, "#d4e6f1"),
        ("B1", "GND", GND_COL, "#d5dbdb")
    ]
    
    ay = ty + 12
    for i, (pin, name, col, bg_col) in enumerate(row_a):
        px = start_x + i * (col_w + gap)
        p.append(rect(px, ay, col_w, 44, fill=bg_col, stroke=col, sw=1.6, rx=4))
        p.append(text(px + col_w / 2, ay + 17, pin, size=11, bold=True, color=col))
        p.append(text(px + col_w / 2, ay + 34, name, size=11, bold=True, color=col))
        
    p.append(rect(start_x, ty + 70, tw - 28, 16, fill="#b2bec3", stroke="#636e72", sw=1.2, rx=2))
    p.append(text(tx + tw / 2, ty + 82, "Центральний екран (Mid-plate GND) — бар'єр між рядами", size=10, bold=True, color="#2d3436"))
    
    by = ty + 98
    for i, (pin, name, col, bg_col) in enumerate(row_b):
        px = start_x + i * (col_w + gap)
        p.append(rect(px, by, col_w, 44, fill=bg_col, stroke=col, sw=1.6, rx=4))
        p.append(text(px + col_w / 2, by + 17, pin, size=11, bold=True, color=col))
        p.append(text(px + col_w / 2, by + 34, name, size=11, bold=True, color=col))

    p.append(line(tx + tw / 2 - 140, oy + 24, tx + tw / 2 + 140, oy + 24, color="#e67e22", sw=1.5, dash="4 3"))
    p.append(text(tx + tw / 2, oy + 20, "Точкова симетрія: поворот на 180° зберігає призначення контактів", size=11.5, bold=True, color="#d35400"))

    leg_y = 325
    items = [
        ("4× VBUS + 4× GND", "живлення до 5 А", VBUS_COL, "#fadbd8", 40, 190),
        ("CC1 / CC2", "детекція та PD", CC_COL, "#d4efdf", 245, 170),
        ("4× пари TX/RX", "SuperSpeed до 40G", SS_TX, "#d4e6f1", 430, 190),
        ("D+ / D− і SBU", "USB 2.0 та Alt Mode", USB2_COL, "#fdebd0", 635, 205),
    ]
    for title, sub, col, bgc, lx, lw in items:
        p.append(rect(lx, leg_y, lw, 54, fill=bgc, stroke=col, sw=1.5, rx=6))
        p.append(text(lx + lw / 2, leg_y + 22, title, size=12, bold=True, color=col))
        p.append(text(lx + lw / 2, leg_y + 40, sub, size=11, color=INK))

    b, w, h = textbox(W / 2, 435,
                      "24 контакти у 2 ряди. Живлення та земля розміщені по кутах і всередині симетрично",
                      size=12, fill="#f4f6f8", bold=True)
    p.append(b)

    render(os.path.join(IMG, "pinout-geometry.svg"), W, H, *p,
           title="Геометрія та матриця 24 контактів USB-C")


# ── 2. Ієрархія довжини контактів і послідовність замикання (Wipe sequence) ────
def fig_pin_staggering():
    W, H = 860, 470
    p = []
    
    box_w = 250
    box_h = 320
    y0 = 60
    
    phases = [
        (45, "Фаза 1: Екран (Корпус)", [
            ("Металевий кожух", "торкається першим", "#2c3e50"),
            ("Скидання ESD", "на шасі до контактів", POS),
            ("Захист чіпів", "струм статики оминає схему", FIELD)
        ], "#eaf0fd", "#2457d6"),
        (305, "Фаза 2: GND та VBUS", [
            ("Подовжені піни", "висунуті на +0.3–0.5 мм", "#c0392b"),
            ("Вирівнювання мас", "GND замикає опорний 0 В", "#2c3e50"),
            ("Передзаряд ємностей", "VBUS готова без сплесків", "#c0392b")
        ], "#fdecea", "#c0392b"),
        (565, "Фаза 3: Сигнали та CC", [
            ("Вкорочені піни", "CC, SBU, D+/-, SS TX/RX", "#27ae60"),
            ("CC бачить Rd", "дозвіл увімкнути навантаження", FIELD),
            ("Старт передачі", "дані йдуть на стабільній шині", "#2980b9")
        ], "#eaf3ea", "#27ae60")
    ]
    
    for px, title, lines_info, bgc, col in phases:
        p.append(rect(px, y0, box_w, box_h, fill=bgc, stroke=col, sw=2, rx=8))
        p.append(text(px + box_w / 2, y0 + 26, title, size=13, bold=True, color=col))
        
        diag_y = y0 + 50
        p.append(rect(px + 15, diag_y, box_w - 30, 110, fill="#ffffff", stroke="#bdc3c7", sw=1.2, rx=4))
        
        p.append(rect(px + 25, diag_y + 12, 140, 8, fill="#7f8c8d", stroke="none"))
        p.append(text(px + 175, diag_y + 20, "Shell", size=9.5, color=MUTED, anchor="start"))
        
        gnd_len = 125 if px >= 305 else 90
        p.append(rect(px + 25, diag_y + 40, gnd_len, 10, fill=VBUS_COL if px >= 305 else "#bdc3c7", stroke="none"))
        p.append(text(px + 175, diag_y + 49, "GND/VBUS", size=9.5, color=MUTED, anchor="start"))
        
        sig_len = 90 if px == 565 else 60
        p.append(rect(px + 25, diag_y + 70, sig_len, 10, fill=CC_COL if px == 565 else "#bdc3c7", stroke="none"))
        p.append(text(px + 175, diag_y + 79, "Signals/CC", size=9.5, color=MUTED, anchor="start"))
        
        if px == 45:
            p.append(line(px + 115, diag_y + 92, px + 150, diag_y + 92, color=HOT, sw=1.2))
            p.append(text(px + 85, diag_y + 96, "ΔL ≈ 0.4 мм", size=9.5, color=HOT, bold=True))
            
        desc_y = y0 + 180
        for h_txt, b_txt, c_col in lines_info:
            p.append(circle(px + 25, desc_y + 6, 3.5, fill=c_col, stroke=c_col))
            p.append(text(px + 38, desc_y + 10, h_txt, size=11, bold=True, color=c_col, anchor="start"))
            p.append(text(px + 38, desc_y + 26, b_txt, size=10, color=INK, anchor="start"))
            desc_y += 38

    p.append(arrow(296, y0 + 130, 304, y0 + 130, color=INK, sw=2))
    p.append(arrow(556, y0 + 130, 564, y0 + 130, color=INK, sw=2))
    
    b, w, h = textbox(W / 2, 420,
                      "Make-First, Break-Last: спершу заземлення, потім живлення, і лише в кінці — сигнальні контролери",
                      size=12, fill="#f4f6f8", bold=True)
    p.append(b)

    render(os.path.join(IMG, "pin-staggering.svg"), W, H, *p,
           title="Ієрархія довжини контактів і послідовність з'єднання")


# ── 3. Мікрофізика контакту: плями стягування та металургія ──────────────────
def fig_contact_micro_physics():
    W, H = 840, 480
    p = []
    
    lx, ly, lw, lh = 45, 50, 360, 350
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#2c3e50", sw=2, rx=8))
    p.append(text(lx + lw / 2, ly + 24, "Мікрорельєф контакту (A-spots)", size=13, bold=True, color="#2c3e50"))
    
    p.append(rect(lx + 30, ly + 42, lw - 60, 40, fill="#d5dbdb", stroke="#7f8c8d", sw=1.5))
    p.append(text(lx + lw / 2, ly + 66, "Пружинний контакт гнізда (Au/Ni/Cu)", size=11, bold=True, color="#2c3e50"))
    
    p.append('<path d="M %d %d Q %d %d, %d %d T %d %d T %d %d T %d %d T %d %d" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (lx + 30, ly + 120, lx + 70, ly + 105, lx + 110, ly + 120, lx + 150, ly + 135, lx + 190, ly + 120, lx + 230, ly + 105, lx + 330, ly + 120, "#e67e22"))
    
    asp = [(lx + 110, ly + 120), (lx + 210, ly + 115), (lx + 280, ly + 122)]
    for ax, ay in asp:
        p.append(circle(ax, ay, 5, fill=HOT, stroke=HOT, sw=1))
        
    p.append(text(lx + 110, ly + 96, "a-spot 1", size=9.5, bold=True, color=HOT))
    p.append(text(lx + 210, ly + 96, "a-spot 2", size=9.5, bold=True, color=HOT))
    
    p.append(rect(lx + 30, ly + 145, lw - 60, 40, fill="#fdebd0", stroke="#d35400", sw=1.5))
    p.append(text(lx + lw / 2, ly + 170, "Язичок штекера (Au/Ni/Cu)", size=11, bold=True, color="#d35400"))
    
    p.append(text(lx + lw / 2, ly + 220, "Фактична площа контакту A_r << A_геом (≈ 1–2%)", size=11, bold=True, color=HOT))
    p.append(text(lx + lw / 2, ly + 250, "Опір стягування: R_c = ρ / (2 · Σ a_i)", size=11.5, bold=True, color=INK))
    p.append(text(lx + lw / 2, ly + 280, "Струм 5 А створює високу густину в плямах", size=10.5, color=MUTED))
    p.append(text(lx + lw / 2, ly + 305, "Локальне джоулеве нагрівання в точках дотику", size=10.5, color=MUTED))

    rx = 435
    p.append(rect(rx, ly, lw, lh, fill="#ffffff", stroke="#2c3e50", sw=2, rx=8))
    p.append(text(rx + lw / 2, ly + 24, "Металургійний захисний стек", size=13, bold=True, color="#2c3e50"))
    
    sy = ly + 46
    layers = [
        ("Тверде золото (Hard Gold / Au-Co)", "0.76 мкм (30 μin) — захист від окиснення", "#f1c40f", "#fef9e7", 42),
        ("Нікелевий підшар (Ni Barrier)", "1.27–2.54 мкм — бар'єр проти дифузії Cu в Au", "#95a5a6", "#eaeded", 48),
        ("Мідна основа (CuSn / CuBe сплав)", "Пружна фосфориста бронза / берилієва мідь", "#e67e22", "#fbeee6", 54)
    ]
    
    for l_title, l_desc, stroke_c, fill_c, l_h in layers:
        p.append(rect(rx + 20, sy, lw - 40, l_h, fill=fill_c, stroke=stroke_c, sw=1.8, rx=4))
        p.append(text(rx + lw / 2, sy + 18, l_title, size=11, bold=True, color=stroke_c))
        p.append(text(rx + lw / 2, sy + 34, l_desc, size=9.5, color=INK))
        sy += l_h + 10
        
    p.append(text(rx + lw / 2, ly + 230, "Сила притискання: F_n = 0.3–0.5 Н на контакт", size=11, bold=True, color="#2c3e50"))
    p.append(text(rx + lw / 2, ly + 260, "R_контакту: номінал 30–40 мОм (макс. 50 мОм)", size=11, bold=True, color=FIELD))
    p.append(text(rx + lw / 2, ly + 290, "Знос золота після 10 000 циклів оголює нікель", size=10.5, color=HOT))

    b, w, h = textbox(W / 2, 435,
                      "Опір контакту визначається мікроплямами a-spots. Покриття золотом з нікелевим бар'єром рятує від окиснення",
                      size=12, fill="#f4f6f8", bold=True)
    p.append(b)

    render(os.path.join(IMG, "contact-micro-physics.svg"), W, H, *p,
           title="Мікрофізика контакту та металургійний стек")


# ── 4. Фізика дугового пробою при гарячому розмиканні (Arcing at 48 V / 5 A) ───
def fig_arcing_hot_unplug():
    W, H = 860, 480
    p = []
    
    lx, ly, lw, lh = 45, 50, 365, 355
    p.append(rect(lx, ly, lw, lh, fill="#fdecea", stroke=HOT, sw=2, rx=8))
    p.append(text(lx + lw / 2, ly + 24, "Аварійне розмикання 48 В під 5 А", size=13, bold=True, color=HOT))
    
    cy_arc = ly + 70
    p.append(rect(lx + 40, cy_arc, 80, 24, fill="#bdc3c7", stroke="#7f8c8d", sw=1.5))
    p.append(text(lx + 80, cy_arc + 16, "Штекер", size=11, bold=True, color=INK))
    
    p.append(rect(lx + 245, cy_arc, 80, 24, fill="#bdc3c7", stroke="#7f8c8d", sw=1.5))
    p.append(text(lx + 285, cy_arc + 16, "Гніздо", size=11, bold=True, color=INK))
    
    p.append(circle(lx + 182, cy_arc + 12, 18, fill="#f39c12", stroke="#d35400", sw=2))
    p.append(circle(lx + 182, cy_arc + 12, 9, fill="#ffffff", stroke="#f1c40f", sw=1.5))
    p.append(text(lx + 182, cy_arc + 44, "Плазмова дуга (T > 4000 K)", size=10, bold=True, color=HOT))
    
    p.append(text(lx + lw / 2, ly + 145, "1. Мікромісток розплавленого золота/міді", size=11, color=INK))
    p.append(text(lx + lw / 2, ly + 175, "2. Випаровування металу та іонізація повітря", size=11, color=INK))
    p.append(text(lx + lw / 2, ly + 205, "3. Напруга 48 В перевищує поріг дуги (12 В)", size=11, bold=True, color=HOT))
    p.append(text(lx + lw / 2, ly + 235, "4. Ерозія золота, нагар, деградація контактів", size=11, color=HOT))
    p.append(text(lx + lw / 2, ly + 280, "Без захисту роз'єм руйнується за десятки циклів!", size=11.5, bold=True, color=HOT))

    rx = 450
    p.append(rect(rx, ly, lw, lh, fill="#eaf3ea", stroke=FIELD, sw=2, rx=8))
    p.append(text(rx + lw / 2, ly + 24, "Захист: CC рветься першим", size=13, bold=True, color=FIELD))
    
    ty_d = ly + 55
    p.append(line(rx + 30, ty_d + 30, rx + lw - 30, ty_d + 30, color=INK, sw=1.2))
    p.append(text(rx + lw - 25, ty_d + 34, "t", size=12, color=INK))
    
    p.append(line(rx + 40, ty_d + 15, rx + 140, ty_d + 15, color=CC_COL, sw=2.5))
    p.append(line(rx + 140, ty_d + 15, rx + 140, ty_d + 30, color=CC_COL, sw=1.5, dash="2 2"))
    p.append(text(rx + 90, ty_d + 8, "CC розімкнувся", size=10, bold=True, color=CC_COL))
    
    p.append(line(rx + 40, ty_d + 75, rx + 170, ty_d + 75, color=VBUS_COL, sw=2.5))
    p.append(line(rx + 170, ty_d + 75, rx + 190, ty_d + 95, color=VBUS_COL, sw=2.5))
    p.append(line(rx + 190, ty_d + 95, rx + lw - 40, ty_d + 95, color=VBUS_COL, sw=1.5))
    p.append(text(rx + 90, ty_d + 68, "Ключ розімкнув струм", size=10, bold=True, color=VBUS_COL))
    
    p.append(line(rx + 240, ty_d + 40, rx + 240, ty_d + 115, color=HOT, sw=1.5, dash="3 3"))
    p.append(text(rx + 240, ty_d + 128, "Механічний розрив VBUS (t > 1 мс)", size=10.5, bold=True, color=HOT))
    
    p.append(text(rx + lw / 2, ly + 210, "1. CC коротший на 0.4 мм → втрата контакту", size=11, color=INK))
    p.append(text(rx + lw / 2, ly + 240, "2. PD контролер закриває MOSFET за < 500 мкс", size=11, bold=True, color=FIELD))
    p.append(text(rx + lw / 2, ly + 270, "3. До розриву пінів VBUS струм дорівнює 0 А", size=11, bold=True, color=FIELD))
    p.append(text(rx + lw / 2, ly + 300, "Дуговий розряд відсутній, контакти цілі", size=11.5, bold=True, color=FIELD))

    b, w, h = textbox(W / 2, 435,
                      "Гаряче висмикування на 48 В гаситься електронно: лінія CC відключає навантаження раніше за піни живлення",
                      size=12, fill="#f4f6f8", bold=True)
    p.append(b)

    render(os.path.join(IMG, "arcing-hot-unplug.svg"), W, H, *p,
           title="Фізика дугового розряду та захист через CC")


# ── 5. Екранування, хвильовий імпеданс 85 Ом та перехресні завади ─────────────
def fig_tongue_shielding_impedance():
    W, H = 860, 480
    p = []
    
    lx, ly, lw, lh = 45, 50, 370, 355
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#2c3e50", sw=2, rx=8))
    p.append(text(lx + lw / 2, ly + 24, "Переріз язичка гнізда (Mid-plate)", size=13, bold=True, color="#2c3e50"))
    
    p.append(rect(lx + 35, ly + 45, lw - 70, 180, fill="#eaeded", stroke="#95a5a6", sw=1.5, rx=6))
    p.append(text(lx + 50, ly + 65, "LCP пластик (ε_r ≈ 3.5)", size=10, color=MUTED, anchor="start"))
    
    p.append(rect(lx + 60, ly + 55, 50, 18, fill="#d4e6f1", stroke=SS_TX, sw=1.5, rx=2))
    p.append(text(lx + 85, ly + 68, "TX1+", size=10, bold=True, color=SS_TX))
    p.append(rect(lx + 130, ly + 55, 50, 18, fill="#d4e6f1", stroke=SS_TX, sw=1.5, rx=2))
    p.append(text(lx + 155, ly + 68, "TX1−", size=10, bold=True, color=SS_TX))
    
    p.append(rect(lx + 200, ly + 55, 50, 18, fill="#fadbd8", stroke=VBUS_COL, sw=1.5, rx=2))
    p.append(text(lx + 225, ly + 68, "VBUS", size=10, bold=True, color=VBUS_COL))
    
    p.append(rect(lx + 45, ly + 125, lw - 90, 24, fill="#7f8c8d", stroke="#2c3e50", sw=2, rx=2))
    p.append(text(lx + lw / 2, ly + 141, "Mid-plate Shield (GND)", size=11, bold=True, color="#ffffff"))
    
    p.append(rect(lx + 60, ly + 195, 50, 18, fill="#d1f2eb", stroke=SS_RX, sw=1.5, rx=2))
    p.append(text(lx + 85, ly + 208, "RX1+", size=10, bold=True, color=SS_RX))
    p.append(rect(lx + 130, ly + 195, 50, 18, fill="#d1f2eb", stroke=SS_RX, sw=1.5, rx=2))
    p.append(text(lx + 155, ly + 208, "RX1−", size=10, bold=True, color=SS_RX))
    
    p.append(rect(lx + 200, ly + 195, 50, 18, fill="#ebdef0", stroke=SBU_COL, sw=1.5, rx=2))
    p.append(text(lx + 225, ly + 208, "SBU2", size=10, bold=True, color=SBU_COL))
    
    p.append(line(lx + 110, ly + 80, lx + 110, ly + 120, color="#27ae60", sw=1.5, dash="2 2"))
    p.append(line(lx + 110, ly + 155, lx + 110, ly + 190, color="#27ae60", sw=1.5, dash="2 2"))
    
    p.append(text(lx + lw / 2, ly + 250, "Mid-plate ізолює TX від RX (NEXT < −40 dB)", size=11, bold=True, color=FIELD))
    p.append(text(lx + lw / 2, ly + 280, "Зовнішній кожух замикає 360° екран від EMI", size=10.5, color=INK))
    p.append(text(lx + lw / 2, ly + 310, "Запобігання завадам на Wi-Fi 2.4 ГГц", size=10.5, color=MUTED))

    rx = 445
    p.append(rect(rx, ly, lw, lh, fill="#ffffff", stroke="#2c3e50", sw=2, rx=8))
    p.append(text(rx + lw / 2, ly + 24, "Диференційний імпеданс Z_diff", size=13, bold=True, color="#2c3e50"))
    
    gx, gy, gw, gh = rx + 30, ly + 50, lw - 60, 150
    p.append(rect(gx, gy, gw, gh, fill="#f8f9fa", stroke="#bdc3c7", sw=1.2))
    
    p.append(line(gx, gy + gh / 2, gx + gw, gy + gh / 2, color="#27ae60", sw=1.8, dash="4 3"))
    p.append(text(gx + gw - 35, gy + gh / 2 - 8, "85 Ом", size=11, bold=True, color=FIELD))
    
    p.append(line(gx, gy + gh / 2 - 30, gx + gw, gy + gh / 2 - 30, color="#e74c3c", sw=1, dash="2 2"))
    p.append(text(gx + 50, gy + gh / 2 - 34, "94 Ом (+9 Ом)", size=9.5, color=HOT))
    
    p.append(line(gx, gy + gh / 2 + 30, gx + gw, gy + gh / 2 + 30, color="#e74c3c", sw=1, dash="2 2"))
    p.append(text(gx + 50, gy + gh / 2 + 42, "76 Ом (−9 Ом)", size=9.5, color=HOT))
    
    tdr_pts = [
        '%.1f,%.1f' % (gx + 10, gy + gh / 2),
        '%.1f,%.1f' % (gx + 60, gy + gh / 2 + 2),
        '%.1f,%.1f' % (gx + 100, gy + gh / 2 + 22),
        '%.1f,%.1f' % (gx + 150, gy + gh / 2 - 12),
        '%.1f,%.1f' % (gx + 200, gy + gh / 2),
        '%.1f,%.1f' % (gx + 270, gy + gh / 2)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (' '.join(tdr_pts), '#2980b9'))
    
    p.append(text(rx + lw / 2, ly + 230, "USB4 / Thunderbolt / PCIe: Z_diff = 85 Ом ± 9 Ом", size=11, bold=True, color=INK))
    p.append(text(rx + lw / 2, ly + 260, "USB 3.1 Gen1/Gen2: спадщина 90 Ом", size=10.5, color=MUTED))
    p.append(text(rx + lw / 2, ly + 290, "Паразитна ємність C_p компенсується вирізами", size=10.5, color=INK))

    b, w, h = textbox(W / 2, 435,
                      "Центральний екран Mid-plate пригнічує перехресні завади, а точна геометрія пелюсток тримає імпеданс 85 Ом",
                      size=12, fill="#f4f6f8", bold=True)
    p.append(b)

    render(os.path.join(IMG, "tongue-shielding-impedance.svg"), W, H, *p,
           title="Екранування язичка та хвильовий імпеданс 85 Ом")


# ── 6. Механічна фіксація, зносостійкість і сили з'єднання ───────────────────
def fig_mechanical_latching_wear():
    W, H = 840, 480
    p = []
    
    lx, ly, lw, lh = 45, 50, 365, 355
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#2c3e50", sw=2, rx=8))
    p.append(text(lx + lw / 2, ly + 24, "Бічні пружинні замки (Latches)", size=13, bold=True, color="#2c3e50"))
    
    sy_m = ly + 50
    p.append(rect(lx + 60, sy_m, 140, 110, fill="#f8f9fa", stroke="#7f8c8d", sw=1.5, rx=4))
    p.append(text(lx + 130, sy_m + 55, "Корпус вилки", size=11, bold=True, color="#2c3e50"))
    
    p.append(rect(lx + 180, sy_m + 15, 18, 16, fill="#bdc3c7", stroke="#2c3e50", sw=1.2))
    p.append(rect(lx + 180, sy_m + 75, 18, 16, fill="#bdc3c7", stroke="#2c3e50", sw=1.2))
    
    p.append('<path d="M %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (lx + 260, sy_m - 10, lx + 230, sy_m + 15, lx + 188, sy_m + 23, lx + 230, sy_m + 32, "#e67e22"))
    p.append(circle(lx + 188, sy_m + 23, 4, fill=HOT, stroke=HOT))
    
    p.append('<path d="M %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (lx + 260, sy_m + 115, lx + 230, sy_m + 90, lx + 188, sy_m + 83, lx + 230, sy_m + 73, "#e67e22"))
    p.append(circle(lx + 188, sy_m + 83, 4, fill=HOT, stroke=HOT))
    
    p.append(text(lx + 270, sy_m + 26, "Замок 1", size=10, bold=True, color=HOT, anchor="start"))
    p.append(text(lx + 270, sy_m + 86, "Замок 2", size=10, bold=True, color=HOT, anchor="start"))
    
    p.append(text(lx + lw / 2, ly + 190, "Замки тримають механічне навантаження,", size=11, bold=True, color=INK))
    p.append(text(lx + lw / 2, ly + 215, "захищаючи контакти від виламування", size=11, bold=True, color=INK))
    p.append(text(lx + lw / 2, ly + 245, "Сила вставляння: F_ins ≤ 35 Н", size=11, color="#2c3e50"))
    p.append(text(lx + lw / 2, ly + 270, "Сила виймання: F_ext = 8–20 Н (початкова)", size=11, color="#2c3e50"))
    p.append(text(lx + lw / 2, ly + 295, "F_ext ≥ 6–20 Н (після 10 000 циклів)", size=11, bold=True, color=FIELD))

    rx = 440
    p.append(rect(rx, ly, lw, lh, fill="#ffffff", stroke="#2c3e50", sw=2, rx=8))
    p.append(text(rx + lw / 2, ly + 24, "Зносостійкість (10 000 циклів)", size=13, bold=True, color="#2c3e50"))
    
    gx2, gy2, gw2, gh2 = rx + 35, ly + 50, lw - 70, 150
    p.append(rect(gx2, gy2, gw2, gh2, fill="#f8f9fa", stroke="#bdc3c7", sw=1.2))
    
    p.append(line(gx2, gy2 + gh2 - 20, gx2 + gw2, gy2 + gh2 - 20, color=INK, sw=1.2))
    p.append(line(gx2 + 25, gy2, gx2 + 25, gy2 + gh2, color=INK, sw=1.2))
    
    p.append(text(gx2 + gw2 - 10, gy2 + gh2 - 6, "N (цикли)", size=10, color=MUTED, anchor="end"))
    p.append(text(gx2 + 20, gy2 + 15, "R_c", size=10, color=MUTED, anchor="end"))
    
    p.append(text(gx2 + 35, gy2 + gh2 - 6, "0", size=9.5, color=MUTED))
    p.append(text(gx2 + 140, gy2 + gh2 - 6, "5 000", size=9.5, color=MUTED))
    p.append(text(gx2 + 250, gy2 + gh2 - 6, "10 000", size=9.5, color=MUTED))
    
    p.append(line(gx2 + 25, gy2 + 40, gx2 + gw2, gy2 + 40, color=HOT, sw=1.2, dash="3 3"))
    p.append(text(gx2 + gw2 - 10, gy2 + 35, "Макс. 50 мОм", size=9.5, bold=True, color=HOT, anchor="end"))
    
    rc_pts = [
        '%.1f,%.1f' % (gx2 + 35, gy2 + 105),
        '%.1f,%.1f' % (gx2 + 100, gy2 + 102),
        '%.1f,%.1f' % (gx2 + 180, gy2 + 90),
        '%.1f,%.1f' % (gx2 + 250, gy2 + 65)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (' '.join(rc_pts), FIELD))
    
    p.append(text(rx + lw / 2, ly + 225, "Пружини розташовані в гнізді (female),", size=11, bold=True, color=INK))
    p.append(text(rx + lw / 2, ly + 245, "щоб знос припадав на кабель, а не пристрій", size=11, color=MUTED))
    p.append(text(rx + lw / 2, ly + 275, "Трибологія контакту: мікроковзання стирає оксиди,", size=10.5, color=INK))
    p.append(text(rx + lw / 2, ly + 295, "але з часом виснажує тонкий шар золота 0.76 мкм", size=10.5, color=INK))

    b, w, h = textbox(W / 2, 435,
                      "Ресурс 10 000 циклів досягається розділенням функцій: бічні замки тримають механіку, пружини — електричний контакт",
                      size=12, fill="#f4f6f8", bold=True)
    p.append(b)

    render(os.path.join(IMG, "mechanical-latching-wear.svg"), W, H, *p,
           title="Механічна фіксація та зносостійкість 10 000 циклів")


if __name__ == "__main__":
    fig_pinout_geometry()
    fig_pin_staggering()
    fig_contact_micro_physics()
    fig_arcing_hot_unplug()
    fig_tongue_shielding_impedance()
    fig_mechanical_latching_wear()
    print("figs.py completed successfully")
