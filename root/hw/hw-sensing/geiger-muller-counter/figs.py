# -*- coding: utf-8 -*-
"""Фігури до теми «Іонізуюче тло: лічильник Гейгера–Мюллера».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (scripts/svgkit.py)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Конструкція трубки Гейгера-Мюллера та розвиток лавини ─────────────────
def fig_geiger_tube_construction():
    W, H = 840, 500
    f = [text(W / 2, 26, "Будова трубки Гейгера–Мюллера та розвиток таунсендівської лавини", size=15, bold=True)]

    # Стінки циліндричного катода (розріз трубки)
    cx, cy, cw, ch = 60, 60, 720, 240
    f.append(rect(cx, cy, cw, ch, fill="#f6f9fc", stroke="#475569", sw=2.0, rx=10))

    # Металевий катод (штриховка стінок)
    f.append(rect(cx, cy, cw, 22, fill="#e2e8f0", stroke="#475569", sw=1.5))
    f.append(rect(cx, cy + ch - 22, cw, 22, fill="#e2e8f0", stroke="#475569", sw=1.5))
    f.append(text(cx + 140, cy + 15, "Катод: циліндрична гільза (R = b, GND)", size=11, bold=True, color="#334155"))
    f.append(text(cx + cw - 120, cy + ch - 7, "Метал / тонке скло з напиленням", size=10, color=MUTED))

    # Слюдяне торцеве вікно зліва
    f.append(rect(cx, cy + 22, 14, ch - 44, fill="#fed7aa", stroke="#ea580c", sw=1.8))
    f.append(text(cx + 8, cy + ch / 2 - 25, "Слюдяне", size=9.5, bold=True, color="#c2410c"))
    f.append(text(cx + 8, cy + ch / 2 - 12, "вікно", size=9.5, bold=True, color="#c2410c"))
    f.append(text(cx + 8, cy + ch / 2 + 3, "(α, β)", size=9.5, color="#c2410c"))

    # Центральна анодна нитка
    ay = cy + ch / 2
    f.append(line(cx + 14, ay, cx + cw - 30, ay, color=POS, sw=2.5))
    f.append(circle(cx + cw - 30, ay, 4, fill=POS, stroke="#991b1b", sw=1.5))
    f.append(text(cx + cw - 120, ay - 12, "Анод: нитка W (r = a ≈ 25 мкм, +400 В)", size=11, bold=True, color=POS))

    # Газове наповнення трубки
    f.append(text(cx + 200, cy + 42, "Газ: Ne / Ar (99%) + гасник Br₂ / Cl₂ (1%), P ≈ 0.1 атм", size=10.5, color="#0f766e", bold=True))

    # Проліт іонізуючої частинки (гамма / бета)
    f.append(line(20, 110, 190, 160, color="#d97706", sw=2.0, dash="5,3"))
    f.append('<polygon points="190,160 178,153 182,163" fill="#d97706"/>')
    f.append(text(75, 120, "Квант γ / e⁻ (β)", size=11, bold=True, color="#b45309"))

    # Первинний акт іонізації в точці (200, 165)
    f.append(circle(200, 165, 12, fill="#fef3c7", stroke="#d97706", sw=1.8))
    f.append(text(200, 169, "Ar", size=11, bold=True, color="#b45309"))
    f.append(text(200, 142, "Первинна іонізація", size=10, bold=True, color=INK))

    # Дрейф первинного електрона до анодної нитки
    f.append(line(208, 172, 280, ay - 6, color=NEG, sw=2.0))
    f.append('<polygon points="280,%d 268,%d 273,%d" fill="%s"/>' % (ay - 6, ay - 13, ay - 4, NEG))
    f.append(text(250, 170, "e⁻", size=11, bold=True, color=NEG))
    f.append(text(230, 205, "Швидкий дрейф\nв область E > 10⁶ В/м", size=9.5, color=NEG))

    # Таунсендівська лавина біля нитки (спалах)
    f.append(circle(300, ay, 20, fill="#fee2e2", stroke=POS, sw=1.5))
    f.append(circle(300, ay, 12, fill="#fca5a5", stroke=POS, sw=1.2))
    f.append(text(300, ay - 26, "Лавина Таунсенда (M ≈ 10⁸)", size=10.5, bold=True, color=POS))

    # Поширення розряду вздовж нитки через УФ-фотони (UV photons)
    f.append(line(315, ay - 8, 440, ay - 8, color="#7c3aed", sw=1.5, dash="4,2"))
    f.append(line(315, ay + 8, 440, ay + 8, color="#7c3aed", sw=1.5, dash="4,2"))
    f.append(text(380, ay - 14, "УФ-фотони (h·ν_uv)", size=10, bold=True, color="#6d28d9"))
    f.append(text(380, ay + 20, "Поширення розряду вздовж усієї нитки", size=9.5, color="#6d28d9"))

    # Вторинний лавинний спалах праворуч
    f.append(circle(460, ay, 18, fill="#fee2e2", stroke=POS, sw=1.5))
    f.append(circle(530, ay, 18, fill="#fee2e2", stroke=POS, sw=1.5))

    # Позитивний іонний чохол (екранування поля)
    f.append(rect(580, ay - 35, 120, 70, fill="#fef2f2", stroke="#ef4444", sw=1.4, rx=6))
    f.append(text(640, ay - 18, "Іонний чохол", size=10.5, bold=True, color="#b91c1c"))
    f.append(text(640, ay - 4, "Ne⁺, Ar⁺, Br₂⁺", size=10, color="#b91c1c"))
    f.append(text(640, ay + 12, "Повільний дрейф до катода", size=9.5, color=MUTED))
    f.append(text(640, ay + 25, "→ Екранування нитки (Мертвий час)", size=9.5, color="#991b1b", bold=True))

    # Нижній блок: Графік радіального поля E(r)
    bx, by, bw, bh = 60, 320, 720, 150
    f.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    f.append(text(bx + 20, by + 22, "Радіальний профіль електричного поля в циліндричній трубці:", size=11, bold=True, color=INK, anchor="start"))

    # Формула поля та значення
    f.append(text(bx + 40, by + 54, "E(r) = V₀ / [ r · ln(b / a) ]", size=13, bold=True, color="#0369a1", anchor="start"))
    f.append(text(bx + 40, by + 82, "Біля анода (r = a = 25 мкм):    E(a) ≈ 2.2 · 10⁶ В/м   → зона лавинного множення", size=10.5, color=POS, anchor="start"))
    f.append(text(bx + 40, by + 108, "Біля катода (r = b = 5 мм):     E(b) ≈ 1.1 · 10⁴ В/м   → зона повільного дрейфу іонів", size=10.5, color=NEG, anchor="start"))

    # Схематичний графік поля E(r) праворуч
    gx, gy = 560, 440
    f.append(line(gx, gy, gx + 150, gy, color=LINE, sw=1.2))
    f.append(line(gx, gy, gx, gy - 95, color=LINE, sw=1.2))
    f.append(text(gx + 155, gy + 4, "r", size=10, bold=True, color=LINE, anchor="start"))
    f.append(text(gx - 5, gy - 95, "E(r)", size=10, bold=True, color=LINE, anchor="end"))

    # Гіпербола 1/r
    pts = []
    for step in range(130):
        rx_val = 6 + step
        ey_val = gy - min(90, int(500 / rx_val))
        pts.append("%d,%d" % (gx + rx_val, ey_val))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), "#0369a1"))
    f.append(text(gx + 8, gy + 14, "r=a", size=9.5, bold=True, color=POS))
    f.append(text(gx + 135, gy + 14, "r=b", size=9.5, bold=True, color=NEG))

    return render(os.path.join(IMG, "geiger-tube-construction-and-avalanche.svg"), W, H, *f)


# ── 2. Області газового розряду (від іонізаційної камери до Гейгера) ───────────
def fig_gas_discharge_regimes():
    W, H = 840, 480
    f = [text(W / 2, 26, "Режими газового детектора: від іонізаційної камери до плато Гейгера", size=15, bold=True)]

    ox, oy = 80, 400
    gw, gh = 700, 330

    # Сітка та осі
    f.append(rect(ox, oy - gh, gw, gh, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))
    f.append(text(ox + gw / 2, oy + 38, "Прикладена висока напруга HV [Вольти]", size=12, bold=True, color=INK))
    f.append(text(ox - 45, oy - gh / 2, "Амплітуда заряду Q (логарифмічна шкала, lg N)", size=12, bold=True, color=INK, anchor="middle"))

    # Секції за напругою (вертикальні смуги)
    regions = [
        (80, 110, "#f8fafc", "I. Рекомбінація"),
        (190, 110, "#eff6ff", "II. Іонізаційна\nкамера (M=1)"),
        (300, 130, "#f0fdf4", "III. Пропорційний\nлічильник (M∝V)"),
        (430, 90, "#fefce8", "IV. Обмежена\nпропорційність"),
        (520, 170, "#fef2f2", "V. Плато Гейгера–Мюллера\n(M ≈ 10⁸..10¹⁰, Q = const)"),
        (690, 90, "#faf5ff", "VI. Неперервний\nпробій")
    ]
    for rx, rw, rfill, rlabel in regions:
        f.append(rect(rx, oy - gh, rw, gh, fill=rfill, stroke="#cbd5e1", sw=0.8))
        lines = rlabel.split("\n")
        for idx, l in enumerate(lines):
            f.append(text(rx + rw / 2, oy - gh + 18 + idx * 13, l, size=9.5, bold=True, color="#334155"))

    # Крива для альфа-частинки (висока первинна іонізація)
    alpha_path = (
        "M 85,380 C 130,340 160,320 200,320 "
        "L 290,320 "
        "C 340,270 390,200 440,160 "
        "C 480,135 505,120 530,115 "
        "L 680,110 "
        "C 700,90 730,60 760,50"
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (alpha_path, POS))
    f.append(text(240, 310, "α-частинка (висока dE/dx)", size=10, bold=True, color=POS))

    # Крива для бета/гамма-частинки (низька первинна іонізація)
    beta_path = (
        "M 85,390 C 130,370 160,360 200,360 "
        "L 290,360 "
        "C 340,310 390,240 440,180 "
        "C 480,145 505,125 530,115 "
        "L 680,110 "
        "C 700,90 730,60 760,50"
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8" stroke-dasharray="6,3"/>' % (beta_path, NEG))
    f.append(text(240, 375, "β / γ (низька dE/dx)", size=10, bold=True, color=NEG))

    # Позначка злиття кривих на плато Гейгера
    f.append(circle(530, 115, 6, fill="#ef4444", stroke="#991b1b", sw=1.5))
    f.append(text(605, 90, "Повне насичення: сигнал не залежить від енергії!", size=10, bold=True, color="#991b1b"))

    # Позначка робочої напруги СБМ-20 (400 В)
    f.append(line(600, oy, 600, oy - gh, color="#059669", sw=1.5, dash="4,3"))
    f.append(rect(555, oy + 6, 90, 20, fill="#d1fae5", stroke="#059669", sw=1.0, rx=3))
    f.append(text(600, oy + 20, "V_op ≈ 400 В", size=10.5, bold=True, color="#065f46"))

    return render(os.path.join(IMG, "gas-discharge-regimes.svg"), W, H, *f)


# ── 3. Високовольтне джерело (Flyback/Boost) та дискримінатор імпульсів ────────
def fig_high_voltage_circuit():
    W, H = 840, 500
    f = [text(W / 2, 24, "Схема високовольтного живлення (400 В) та формувача імпульсів трубки", size=15, bold=True)]

    # Блок 1: Генератор високої напруги (Flyback/Boost)
    b1_x, b1_y, b1_w, b1_h = 30, 50, 370, 420
    f.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(b1_x + b1_w / 2, b1_y + 20, "1. Джерело +400 В (Flyback / Boost)", size=12, bold=True, color=INK))

    # Схема перетворювача
    f.append(text(b1_x + 35, b1_y + 55, "+3.3 В / +5 В", size=10.5, bold=True, color=POS))
    f.append(line(b1_x + 95, b1_y + 52, b1_x + 130, b1_y + 52, color=POS, sw=2.0))

    # Індуктивність L1
    f.append(rect(b1_x + 130, b1_y + 42, 50, 20, fill="#fef08a", stroke="#ca8a04", sw=1.4, rx=4))
    f.append(text(b1_x + 155, b1_y + 56, "L 10 мГн", size=9.5, bold=True, color="#854d0e"))

    # Вузол комутації
    f.append(line(b1_x + 180, b1_y + 52, b1_x + 220, b1_y + 52, color=LINE, sw=2.0))
    f.append(circle(b1_x + 220, b1_y + 52, 3, fill=INK))

    # Ключ MOSFET вниз
    f.append(line(b1_x + 220, b1_y + 52, b1_x + 220, b1_y + 90, color=LINE, sw=1.8))
    f.append(rect(b1_x + 205, b1_y + 90, 30, 36, fill="#e0e7ff", stroke="#4338ca", sw=1.4, rx=4))
    f.append(text(b1_x + 220, b1_y + 112, "FET", size=10, bold=True, color="#3730a3"))
    f.append(line(b1_x + 220, b1_y + 126, b1_x + 220, b1_y + 150, color=LINE, sw=1.8))
    f.append(text(b1_x + 220, b1_y + 164, "GND", size=9.5, bold=True, color=MUTED))

    # Керування ШІМ від МК
    f.append(line(b1_x + 130, b1_y + 108, b1_x + 205, b1_y + 108, color="#2563eb", sw=1.6))
    f.append(text(b1_x + 105, b1_y + 102, "PWM", size=10, bold=True, color="#2563eb"))
    f.append(text(b1_x + 105, b1_y + 118, "20 кГц, 3 мкс", size=9.5, color=MUTED))

    # Високовольтний діод D1 вправо
    f.append(line(b1_x + 220, b1_y + 52, b1_x + 260, b1_y + 52, color=LINE, sw=2.0))
    f.append(rect(b1_x + 260, b1_y + 42, 45, 20, fill="#fee2e2", stroke=POS, sw=1.4, rx=3))
    f.append(text(b1_x + 282, b1_y + 56, "UF4007", size=9.5, bold=True, color=POS))

    # Фільтруючий конденсатор C_hv на 400 В
    f.append(line(b1_x + 305, b1_y + 52, b1_x + 335, b1_y + 52, color=LINE, sw=2.0))
    f.append(circle(b1_x + 335, b1_y + 52, 3, fill=INK))
    f.append(line(b1_x + 335, b1_y + 52, b1_x + 335, b1_y + 85, color=LINE, sw=1.8))
    f.append(rect(b1_x + 320, b1_y + 85, 30, 26, fill="#dbeafe", stroke="#1d4ed8", sw=1.4, rx=3))
    f.append(text(b1_x + 335, b1_y + 102, "4.7 нФ", size=9.5, bold=True, color="#1e40af"))
    f.append(text(b1_x + 335, b1_y + 124, "1 кВ", size=9.5, color=MUTED))
    f.append(line(b1_x + 335, b1_y + 111, b1_x + 335, b1_y + 150, color=LINE, sw=1.8))
    f.append(text(b1_x + 335, b1_y + 164, "GND", size=9.5, bold=True, color=MUTED))

    # Вихід +400 В
    f.append(line(b1_x + 335, b1_y + 52, b1_x + b1_w, b1_y + 52, color=POS, sw=2.5))
    f.append(text(b1_x + 310, b1_y + 36, "+400 В HV", size=10.5, bold=True, color=POS))

    # Зворотний зв'язок 1 ГОм подільник
    f.append(rect(b1_x + 20, b1_y + 200, 330, 190, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=6))
    f.append(text(b1_x + 35, b1_y + 225, "Гігаомний подільник зворотного зв'язку:", size=10.5, bold=True, color=INK, anchor="start"))
    f.append(text(b1_x + 35, b1_y + 260, "R_fb1 = 1.0 ГОм (3 × 330 МОм SMD 1206)", size=10, color=POS, anchor="start"))
    f.append(text(b1_x + 35, b1_y + 295, "R_fb2 = 8.2 МОм + ОП буфер до ADC МК", size=10, color=NEG, anchor="start"))
    f.append(text(b1_x + 35, b1_y + 335, "Струм подільника:", size=10, bold=True, color="#059669", anchor="start"))
    f.append(text(b1_x + 35, b1_y + 360, "I_fb = 400 В / 1 ГОм = 0.4 мкА (P = 0.16 мВт)", size=10, bold=True, color="#059669", anchor="start"))

    # Блок 2: Трубка Гейгера та формувач імпульсів
    b2_x, b2_y, b2_w, b2_h = 420, 50, 390, 420
    f.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(b2_x + b2_w / 2, b2_y + 20, "2. Трубка Гейгера та логічний формувач", size=12, bold=True, color=INK))

    # Анодний резистор R_a
    f.append(line(b2_x, b2_y + 52, b2_x + 30, b2_y + 52, color=POS, sw=2.5))
    f.append(rect(b2_x + 30, b2_y + 42, 55, 20, fill="#fef2f2", stroke=POS, sw=1.4, rx=4))
    f.append(text(b2_x + 57, b2_y + 56, "R_a 5.1M", size=9.5, bold=True, color=POS))

    # Підключення до трубки GM
    f.append(line(b2_x + 85, b2_y + 52, b2_x + 130, b2_y + 52, color=LINE, sw=2.0))
    f.append(circle(b2_x + 130, b2_y + 52, 3, fill=INK))

    # Трубка СБМ-20 (схематично)
    f.append(rect(b2_x + 115, b2_y + 80, 30, 45, fill="#e2e8f0", stroke="#334155", sw=1.5, rx=4))
    f.append(line(b2_x + 130, b2_y + 52, b2_x + 130, b2_y + 80, color=POS, sw=1.8))
    f.append(text(b2_x + 130, b2_y + 106, "СБМ-20", size=9.5, bold=True, color="#1e293b"))
    f.append(line(b2_x + 130, b2_y + 125, b2_x + 130, b2_y + 145, color=LINE, sw=1.8))
    f.append(text(b2_x + 130, b2_y + 158, "GND (катод)", size=9.5, bold=True, color=MUTED))

    # Розділовий конденсатор C_c
    f.append(line(b2_x + 130, b2_y + 52, b2_x + 185, b2_y + 52, color=LINE, sw=1.8))
    f.append(rect(b2_x + 185, b2_y + 42, 35, 20, fill="#e0e7ff", stroke="#3730a3", sw=1.4, rx=3))
    f.append(text(b2_x + 202, b2_y + 56, "47 пФ", size=9.5, bold=True, color="#3730a3"))

    # Дискримінатор на NPN / Schmitt
    f.append(line(b2_x + 220, b2_y + 52, b2_x + 255, b2_y + 52, color=LINE, sw=1.8))
    f.append(rect(b2_x + 255, b2_y + 32, 70, 40, fill="#fef08a", stroke="#ca8a04", sw=1.4, rx=6))
    f.append(text(b2_x + 290, b2_y + 49, "Компаратор", size=9.5, bold=True, color="#854d0e"))
    f.append(text(b2_x + 290, b2_y + 63, "з гістерезисом", size=9.5, color="#854d0e"))

    # Вихід на переривання МК
    f.append(line(b2_x + 325, b2_y + 52, b2_x + 375, b2_y + 52, color=FIELD, sw=2.5))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>' % (b2_x + 375, b2_y + 52, b2_x + 365, b2_y + 47, b2_x + 365, b2_y + 57, FIELD))
    f.append(text(b2_x + 290, b2_y + 95, "Логічний вихід → EXTI МК", size=10.5, bold=True, color=FIELD))

    # Осцилограма імпульсів унизу блоку 2
    f.append(rect(b2_x + 15, b2_y + 180, 360, 220, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=6))
    f.append(text(b2_x + 30, b2_y + 205, "Форма сигналу на аноді та виході компаратора:", size=10.5, bold=True, color=INK, anchor="start"))

    # Анодний сплеск
    f.append(text(b2_x + 30, b2_y + 230, "Анод V_a (400 В спадає на ~50 В за 1 мкс, потім RC-релаксація):", size=9.5, color=POS, anchor="start"))
    f.append(line(b2_x + 35, b2_y + 255, b2_x + 85, b2_y + 255, color=POS, sw=1.8))
    f.append(line(b2_x + 85, b2_y + 255, b2_x + 90, b2_y + 285, color=POS, sw=1.8))
    f.append(line(b2_x + 90, b2_y + 285, b2_x + 185, b2_y + 255, color=POS, sw=1.8))
    f.append(line(b2_x + 185, b2_y + 255, b2_x + 260, b2_y + 255, color=POS, sw=1.8))
    f.append(text(b2_x + 105, b2_y + 298, "τ_RC ≈ R_a · C_stray ≈ 150 мкс", size=9.5, color=POS, anchor="start"))

    # Прямокутний логічний імпульс
    f.append(text(b2_x + 30, b2_y + 325, "Вихід компаратора (чистий логічний 3.3 В прямокутник):", size=9.5, color=FIELD, anchor="start"))
    f.append(line(b2_x + 35, b2_y + 368, b2_x + 88, b2_y + 368, color=FIELD, sw=2.0))
    f.append(line(b2_x + 88, b2_y + 368, b2_x + 88, b2_y + 345, color=FIELD, sw=2.0))
    f.append(line(b2_x + 88, b2_y + 345, b2_x + 125, b2_y + 345, color=FIELD, sw=2.0))
    f.append(line(b2_x + 125, b2_y + 345, b2_x + 125, b2_y + 368, color=FIELD, sw=2.0))
    f.append(line(b2_x + 125, b2_y + 368, b2_x + 260, b2_y + 368, color=FIELD, sw=2.0))
    f.append(text(b2_x + 135, b2_y + 358, "Ширина ≈ 20..50 мкс", size=9.5, color=FIELD, anchor="start"))

    return render(os.path.join(IMG, "high-voltage-flyback-and-pulse-shaping.svg"), W, H, *f)


# ── 4. Таймлайн мертвого часу та непаралізовна корекція ───────────────────────
def fig_geiger_dead_time():
    W, H = 840, 500
    f = [text(W / 2, 24, "Часова динаміка: Мертвий час (Dead Time) та час відновлення трубки", size=15, bold=True)]

    # Вісь часу t
    ox, oy = 80, 220
    f.append(line(ox, oy, ox + 680, oy, color=LINE, sw=1.5))
    f.append(line(ox, oy, ox, oy - 140, color=LINE, sw=1.5))
    f.append(text(ox + 685, oy + 4, "t", size=11, bold=True, color=LINE, anchor="start"))
    f.append(text(ox - 10, oy - 145, "Чутливість трубки до нової іонізації", size=10.5, bold=True, color=INK, anchor="start"))

    # Подія 1 в t = 0
    t0 = ox + 40
    f.append(line(t0, oy + 20, t0, oy - 130, color=POS, sw=2.0, dash="4,2"))
    f.append(circle(t0, oy - 110, 8, fill="#fee2e2", stroke=POS, sw=1.8))
    f.append(text(t0, oy - 125, "1-ша частинка (розряд)", size=10, bold=True, color=POS))

    # Зона мертвого часу (Dead time tau_dead)
    t_dead = t0 + 180
    f.append(rect(t0, oy - 100, 180, 100, fill="#fee2e2", stroke="#ef4444", sw=1.0))
    f.append(text(t0 + 90, oy - 55, "МЕРТВИЙ ЧАС  τ_dead", size=11, bold=True, color="#b91c1c"))
    f.append(text(t0 + 90, oy - 38, "≈ 50 .. 150 мкс", size=10, color="#b91c1c"))
    f.append(text(t0 + 90, oy - 20, "Чутливість = 0% (іонний чохол блокує поле)", size=9.5, color="#7f1d1d"))

    # Втрачена частинка під час мертвого часу
    t_lost = t0 + 100
    f.append(line(t_lost, oy + 30, t_lost, oy - 90, color="#9ca3af", sw=1.5, dash="3,2"))
    f.append(circle(t_lost, oy - 70, 6, fill="#f3f4f6", stroke="#9ca3af", sw=1.4))
    f.append(text(t_lost, oy + 42, "Частинка 2 (ПРОПУЩЕНА!)", size=9.5, bold=True, color="#4b5563"))

    # Зона відновлення (Recovery time)
    t_rec = t_dead + 200
    f.append(rect(t_dead, oy - 100, 200, 100, fill="#fef9c3", stroke="#ca8a04", sw=1.0))
    # Крива відновлення чутливості
    rec_curve = "M %d,%d C %d,%d %d,%d %d,%d" % (t_dead, oy, t_dead + 60, oy - 20, t_dead + 140, oy - 90, t_rec, oy - 100)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (rec_curve, "#ca8a04"))
    f.append(text(t_dead + 100, oy - 65, "ЧАС ВІДНОВЛЕННЯ  τ_rec", size=10.5, bold=True, color="#854d0e"))
    f.append(text(t_dead + 100, oy - 48, "≈ 100 .. 300 мкс", size=9.5, color="#854d0e"))
    f.append(text(t_dead + 100, oy - 15, "Іони нейтралізуються на катоді", size=9.5, color="#854d0e"))

    # Повне відновлення (100% готовність)
    f.append(rect(t_rec, oy - 100, 160, 100, fill="#dcfce7", stroke="#16a34a", sw=1.0))
    f.append(text(t_rec + 80, oy - 55, "ПОВНА ГОТОВНІСТЬ", size=10.5, bold=True, color="#15803d"))
    f.append(text(t_rec + 80, oy - 38, "100% амплітуда", size=9.5, color="#15803d"))

    # Нижній блок: Порівняння непаралізовного та паралізовного лічильника
    bx, by, bw, bh = 80, 270, 680, 200
    f.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    f.append(text(bx + 20, by + 24, "Математична модель поправки на пропущені відліки:", size=12, bold=True, color=INK, anchor="start"))

    f.append(text(bx + 40, by + 56, "Непаралізовна модель (Non-paralyzable):", size=11, bold=True, color="#0369a1", anchor="start"))
    f.append(text(bx + 60, by + 80, "N_true = N_meas / [ 1 − N_meas · τ ]", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(bx + 60, by + 104, "При τ = 100 мкс і N_meas = 1 000 с⁻¹:    N_true = 1000 / (1 − 0.1) = 1 111 с⁻¹ (+11.1% недообліку)", size=9.5, color=INK, anchor="start"))
    f.append(text(bx + 60, by + 126, "При τ = 100 мкс і N_meas = 5 000 с⁻¹:    N_true = 5000 / (1 − 0.5) = 10 000 с⁻¹ (+100% недообліку)", size=9.5, color=POS, anchor="start"))

    f.append(text(bx + 40, by + 158, "Паралізовна небезпека (Paralyzable saturation):", size=10.5, bold=True, color="#b91c1c", anchor="start"))
    f.append(text(bx + 60, by + 180, "У надвисоких полях кожна нова частинка подовжує мертвий стан: лічильник показує 0 CPM у смертельній зоні!", size=9.5, color="#991b1b", bold=True, anchor="start"))

    return render(os.path.join(IMG, "geiger-dead-time-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_geiger_tube_construction()
    fig_gas_discharge_regimes()
    fig_high_voltage_circuit()
    fig_geiger_dead_time()
    print("SVG figures generated successfully in ./img/")
