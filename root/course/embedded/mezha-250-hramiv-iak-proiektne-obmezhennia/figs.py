# -*- coding: utf-8 -*-
import sys, os
# Four levels up to reach scripts/ from root/course/embedded/mezha-250-hramiv-iak-proiektne-obmezhennia
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Залежність кінетичної енергії удару від швидкості та маси
# ─────────────────────────────────────────────────────────────────────────────
def fig_kinetic_energy():
    W, H = 880, 460
    frags = []

    # Заголовок діаграми
    frags.append(text(W / 2, 28, "Кінетична енергія вільного падіння БПЛА та регуляторна межа 80 Дж", size=15, bold=True))

    # Вісь X: швидкість падіння (м/с), вісь Y: кінетична енергія (Дж)
    ox, oy = 90, 390
    gw, gh = 720, 320

    # Сітка та осі
    frags.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=4))

    # Горизонтальна лінія критичного порогу 80 Дж
    # Масштаб Y: 0..200 Дж -> gh = 320 px (1 Дж = 1.6 px)
    # y = oy - (E * 1.6)
    y80 = oy - (80 * 1.6) # 390 - 128 = 262
    frags.append(line(ox, y80, ox + gw, y80, color=POS, sw=2, dash="6,4"))
    frags.append(rect(ox + 440, y80 - 24, 260, 20, fill="#fdeeee", stroke=POS, sw=1, rx=3))
    frags.append(text(ox + 570, y80 - 10, "Критичний поріг важкої травми (80 Дж)", size=11, bold=True, color=POS))

    # Зона вище 80 Дж
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.06"/>' % (ox + 1, oy - gh + 1, gw - 2, y80 - (oy - gh), POS))
    frags.append(text(ox + 130, oy - gh + 22, "ЗОНА РЕГУЛЯТОРНИХ ОБМЕЖЕНЬ (E_k ≥ 80 Дж)", size=11, bold=True, color=POS))

    # Зона нижче 80 Дж
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.04"/>' % (ox + 1, y80, gw - 2, oy - y80 - 1, FIELD))
    frags.append(text(ox + 130, y80 + 20, "БЕЗПЕЧНА ЗОНА SUB-250G (E_k < 80 Дж)", size=11, bold=True, color=FIELD))

    # Позначки осі Y
    for e_val in [0, 40, 80, 120, 160, 200]:
        y_pos = oy - (e_val * 1.6)
        frags.append(line(ox - 6, y_pos, ox, y_pos, color=LINE, sw=1.2))
        frags.append(text(ox - 12, y_pos + 4, str(e_val) + " Дж", size=10.5, color=MUTED, anchor="end"))
        if e_val > 0 and e_val != 80:
            frags.append(line(ox, y_pos, ox + gw, y_pos, color="#e1e4e8", sw=1, dash="3,3"))

    # Позначки осі X: 0..30 м/с (1 м/с = 24 px)
    for v_val in [0, 5, 10, 15, 20, 25, 30]:
        x_pos = ox + (v_val * 24)
        frags.append(line(x_pos, oy, x_pos, oy + 6, color=LINE, sw=1.2))
        frags.append(text(x_pos, oy + 20, str(v_val), size=11, color=MUTED))
        if v_val > 0:
            frags.append(line(x_pos, oy - gh, x_pos, oy, color="#e1e4e8", sw=1, dash="3,3"))

    frags.append(text(ox + gw / 2, oy + 42, "Швидкість падіння / зіткнення v (м/с)", size=12, bold=True))
    frags.append(text(ox - 55, oy - gh / 2, "Енергія удару (Дж)", size=12, bold=True, anchor="middle"))

    # Криві E_k = 0.5 * m * v^2
    # 1) m = 150 г (0.15 кг) -> при v=30 м/с, E = 0.5 * 0.15 * 900 = 67.5 Дж
    pts_150 = []
    for v in range(0, 31):
        x = ox + (v * 24)
        e = 0.5 * 0.15 * (v ** 2)
        y = oy - (e * 1.6)
        pts_150.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="#27ae60" stroke-width="2.4"/>' % " ".join(pts_150))
    frags.append(text(ox + (28 * 24) + 10, oy - (0.5 * 0.15 * (28**2) * 1.6) + 16, "150 г (Whoop/Micro)", size=10.5, bold=True, color="#27ae60", anchor="start"))

    # 2) m = 249 г (0.249 кг)
    pts_249 = []
    for v in range(0, 31):
        x = ox + (v * 24)
        e = 0.5 * 0.249 * (v ** 2)
        y = oy - (e * 1.6)
        if y < (oy - gh):
            break
        pts_249.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="#2457d6" stroke-width="3"/>' % " ".join(pts_249))
    frags.append(text(ox + (23 * 24) - 20, oy - (0.5 * 0.249 * (23**2) * 1.6) - 10, "249 г (Sub-250g границя)", size=11, bold=True, color="#2457d6", anchor="end"))

    # Термінальна швидкість для 249г: v_t ≈ 19.5 м/с (E_k ≈ 47.3 Дж)
    vt_x = ox + (19.5 * 24)
    vt_y = oy - (47.3 * 1.6)
    frags.append(circle(vt_x, vt_y, 5, fill=POS, stroke=BG, sw=1.5))
    frags.append(rect(vt_x - 140, vt_y - 36, 130, 28, fill="#ffffff", stroke="#2457d6", sw=1.2, rx=3))
    frags.append(text(vt_x - 75, vt_y - 20, "v_терм ≈ 19.5 м/с (47.3 Дж)", size=9.5, bold=True, color=INK))

    # 3) m = 500 г (0.50 кг) -> при v=17.9 м/с: E = 80 Дж
    pts_500 = []
    for v in range(0, 31):
        x = ox + (v * 24)
        e = 0.5 * 0.50 * (v ** 2)
        y = oy - (e * 1.6)
        if y < (oy - gh):
            break
        pts_500.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="#e67e22" stroke-width="2.2" stroke-dasharray="4,3"/>' % " ".join(pts_500))
    frags.append(text(ox + (18 * 24) + 12, oy - gh + 50, "500 г (Open A2)", size=10.5, bold=True, color="#e67e22", anchor="start"))

    # 4) m = 900 г (0.90 кг) -> при v=13.3 м/с: E = 80 Дж
    pts_900 = []
    for v in range(0, 31):
        x = ox + (v * 24)
        e = 0.5 * 0.90 * (v ** 2)
        y = oy - (e * 1.6)
        if y < (oy - gh):
            break
        pts_900.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="#c0392b" stroke-width="2.2" stroke-dasharray="2,2"/>' % " ".join(pts_900))
    frags.append(text(ox + (12 * 24) + 12, oy - gh + 20, "900 г (5-inch)", size=10.5, bold=True, color="#c0392b", anchor="start"))

    render(os.path.join(IMG, 'sub250-kinetic-energy-velocity.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Структура вагового бюджету (3-inch Freestyle vs 4-inch Long-Range)
# ─────────────────────────────────────────────────────────────────────────────
def fig_mass_breakdown():
    W, H = 880, 480
    frags = []

    frags.append(text(W / 2, 28, "Ваговий баланс суб-250г квадрокоптера: маневреність проти дальності", size=15, bold=True))

    col1_x = 70
    col2_x = 480
    box_w = 330
    box_h = 400

    # Колонка 1: 3-inch Micro Freestyle
    frags.append(rect(col1_x, 50, box_w, box_h, fill="#f8fafc", stroke="#3b6fd4", sw=1.8, rx=6))
    frags.append(text(col1_x + box_w / 2, 76, "3-INCH MICRO FREESTYLE (4S)", size=13, bold=True, color="#274b8f"))
    frags.append(text(col1_x + box_w / 2, 94, "Висока міцність, тягооснащеність TWR > 5.0", size=10.5, color=MUTED))

    # Стек компонентів ліворуч (загальна висота 249г)
    stack_y = 114
    items_3in = [
        ("Рама 3.0 мм T700 карбон", 42, "#dbeafe", "#1e40af"),
        ("Мотори 1404 3800KV (4 шт)", 38, "#e0e7ff", "#3730a3"),
        ("AIO FC + ESC 20A + RX", 9, "#ede9fe", "#5b21b6"),
        ("HD VTX + Камера (DJI O3 / Walksnail)", 34, "#fae8ff", "#86198f"),
        ("Пропелери 3018 + Кріплення", 12, "#fce7f3", "#9d174d"),
        ("Батарея LiPo 4S 650 мАг (75C)", 114, "#dcfce7", "#166534"),
    ]

    curr_y = stack_y
    for label, mass, fill_c, text_c in items_3in:
        h = mass * 1.02
        frags.append(rect(col1_x + 20, curr_y, box_w - 40, h, fill=fill_c, stroke=text_c, sw=1.2, rx=3))
        frags.append(text(col1_x + 30, curr_y + h / 2 + 4, label, size=10.5, color=text_c, anchor="start", bold=True))
        frags.append(text(col1_x + box_w - 30, curr_y + h / 2 + 4, str(mass) + " г", size=10.5, color=text_c, anchor="end", bold=True))
        curr_y += h

    # Підсумок 1
    frags.append(line(col1_x + 20, curr_y + 10, col1_x + box_w - 20, curr_y + 10, color="#1e40af", sw=1.5))
    frags.append(text(col1_x + 30, curr_y + 28, "Повна злітна маса (AUW):", size=11, bold=True))
    frags.append(text(col1_x + box_w - 30, curr_y + 28, "249.0 г", size=12, bold=True, color=POS))
    frags.append(text(col1_x + box_w / 2, curr_y + 46, "Час польоту: 4.5 – 6.5 хв | Тяга: 1350 г", size=10.5, color=MUTED, italic=True))


    # Колонка 2: 4-inch Long-Range Ultralight
    frags.append(rect(col2_x, 50, box_w, box_h, fill="#f8fafc", stroke="#059669", sw=1.8, rx=6))
    frags.append(text(col2_x + box_w / 2, 76, "4-INCH LONG RANGE (2S Li-Ion)", size=13, bold=True, color="#065f46"))
    frags.append(text(col2_x + box_w / 2, 94, "Низьке навантаження на диск, дальність > 10 км", size=10.5, color=MUTED))

    items_4in = [
        ("Ультралегка рама 1.5 мм", 24, "#dbeafe", "#1e40af"),
        ("Мотори 1404 2750KV (4 шт)", 34, "#e0e7ff", "#3730a3"),
        ("AIO FC + ESC 12A + ELRS", 7, "#ede9fe", "#5b21b6"),
        ("Аналоговий VTX + Micro Cam", 12, "#fae8ff", "#86198f"),
        ("Пропелери 4025 (2-лопатеві)", 8, "#fce7f3", "#9d174d"),
        ("Батарея Li-Ion 2S 18650 3500мАг", 164, "#dcfce7", "#166534"),
    ]

    curr_y = stack_y
    for label, mass, fill_c, text_c in items_4in:
        h = mass * 1.02
        frags.append(rect(col2_x + 20, curr_y, box_w - 40, h, fill=fill_c, stroke=text_c, sw=1.2, rx=3))
        frags.append(text(col2_x + 30, curr_y + h / 2 + 4, label, size=10.5, color=text_c, anchor="start", bold=True))
        frags.append(text(col2_x + box_w - 30, curr_y + h / 2 + 4, str(mass) + " г", size=10.5, color=text_c, anchor="end", bold=True))
        curr_y += h

    # Підсумок 2
    frags.append(line(col2_x + 20, curr_y + 10, col2_x + box_w - 20, curr_y + 10, color="#065f46", sw=1.5))
    frags.append(text(col2_x + 30, curr_y + 28, "Повна злітна маса (AUW):", size=11, bold=True))
    frags.append(text(col2_x + box_w - 30, curr_y + 28, "249.0 г", size=12, bold=True, color=POS))
    frags.append(text(col2_x + box_w / 2, curr_y + 46, "Час польоту: 22.0 – 28.0 хв | Тяга: 680 г", size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, 'sub250-mass-breakdown-tradeoffs.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Порівняння електричних топологій 1S/2S проти 4S
# ─────────────────────────────────────────────────────────────────────────────
def fig_electrical_topology():
    W, H = 880, 430
    frags = []

    frags.append(text(W / 2, 26, "Енергетичні втрати й струми в суб-250г: 1S-2S проти 4S (при P = 120 Вт)", size=15, bold=True))

    top_y = 54
    card_w = 370
    card_h = 340

    # Ліва картка: Низьковольтна 1S / 2S
    x1 = 50
    frags.append(rect(x1, top_y, card_w, card_h, fill="#fff8f8", stroke=POS, sw=1.8, rx=6))
    frags.append(text(x1 + card_w / 2, top_y + 24, "ТОПОЛОГІЯ 1S / 2S (НИЗЬКА НАПРУГА)", size=12.5, bold=True, color=POS))

    frags.append(rect(x1 + 16, top_y + 42, card_w - 32, 54, fill="#ffffff", stroke="#d0d7de", sw=1, rx=4))
    frags.append(text(x1 + 30, top_y + 62, "Напруга живлення V_bat:", size=11, color=MUTED, anchor="start"))
    frags.append(text(x1 + card_w - 30, top_y + 62, "3.7 В – 7.4 В", size=12, bold=True, anchor="end"))
    frags.append(text(x1 + 30, top_y + 84, "Струм при 120 Вт (висіння/маневр):", size=11, color=MUTED, anchor="start"))
    frags.append(text(x1 + card_w - 30, top_y + 84, "16.2 А – 32.4 А", size=12, bold=True, color=POS, anchor="end"))

    # Блок втрат
    frags.append(rect(x1 + 16, top_y + 106, card_w - 32, 130, fill="#fdeeee", stroke=POS, sw=1.2, rx=4))
    frags.append(text(x1 + card_w / 2, top_y + 126, "ОМІЧНІ ВТРАТИ (I² · R):", size=11, bold=True, color=POS))
    frags.append(text(x1 + 26, top_y + 148, "• Падіння на роз'ємі BT2.0/XT30 (15 мОм):", size=10.5, anchor="start"))
    frags.append(text(x1 + card_w - 26, top_y + 148, "ΔV ≈ 0.48 В", size=11, bold=True, color=POS, anchor="end"))
    frags.append(text(x1 + 26, top_y + 172, "• Теплові втрати на ключах ESC (R_ds=5мОм):", size=10.5, anchor="start"))
    frags.append(text(x1 + card_w - 26, top_y + 172, "P_loss ≈ 5.25 Вт", size=11, bold=True, color=POS, anchor="end"))
    frags.append(text(x1 + 26, top_y + 196, "• Просадка шини живлення 5V BEC:", size=10.5, anchor="start"))
    frags.append(text(x1 + card_w - 26, top_y + 196, "Критична (ризик brownout)", size=10.5, bold=True, color=POS, anchor="end"))
    frags.append(text(x1 + 26, top_y + 222, "• Потрібний дріт AWG18 (важкий джгут)", size=10.5, color=MUTED, anchor="start"))

    frags.append(rect(x1 + 16, top_y + 248, card_w - 32, 74, fill="#ffffff", stroke="#e0a04a", sw=1.2, rx=4))
    frags.append(text(x1 + card_w / 2, top_y + 268, "НАСЛІДОК ДЛЯ ПРОЄКТУВАННЯ:", size=10.5, bold=True, color="#b06f1e"))
    frags.append(text(x1 + card_w / 2, top_y + 288, "Вимагає моторів > 10000 KV для 1S,", size=10.5, color=INK))
    frags.append(text(x1 + card_w / 2, top_y + 306, "товстих силових доріжок і низького ESR.", size=10.5, color=INK))


    # Права картка: Високовольтна 4S
    x2 = 460
    frags.append(rect(x2, top_y, card_w, card_h, fill="#f8fdf9", stroke="#059669", sw=1.8, rx=6))
    frags.append(text(x2 + card_w / 2, top_y + 24, "ТОПОЛОГІЯ 4S (ВИСОКА НАПРУГА)", size=12.5, bold=True, color="#065f46"))

    frags.append(rect(x2 + 16, top_y + 42, card_w - 32, 54, fill="#ffffff", stroke="#d0d7de", sw=1, rx=4))
    frags.append(text(x2 + 30, top_y + 62, "Напруга живлення V_bat:", size=11, color=MUTED, anchor="start"))
    frags.append(text(x2 + card_w - 30, top_y + 62, "14.8 В – 16.8 В", size=12, bold=True, anchor="end"))
    frags.append(text(x2 + 30, top_y + 84, "Струм при 120 Вт (висіння/маневр):", size=11, color=MUTED, anchor="start"))
    frags.append(text(x2 + card_w - 30, top_y + 84, "7.1 А – 8.1 А", size=12, bold=True, color="#059669", anchor="end"))

    # Блок втрат
    frags.append(rect(x2 + 16, top_y + 106, card_w - 32, 130, fill="#e8f8f0", stroke="#059669", sw=1.2, rx=4))
    frags.append(text(x2 + card_w / 2, top_y + 126, "ОМІЧНІ ВТРАТИ (I² · R):", size=11, bold=True, color="#065f46"))
    frags.append(text(x2 + 26, top_y + 148, "• Падіння на роз'ємі XT30 (15 мОм):", size=10.5, anchor="start"))
    frags.append(text(x2 + card_w - 26, top_y + 148, "ΔV ≈ 0.12 В (у 4 рази менше)", size=11, bold=True, color="#065f46", anchor="end"))
    frags.append(text(x2 + 26, top_y + 172, "• Теплові втрати на ключах ESC (R_ds=5мОм):", size=10.5, anchor="start"))
    frags.append(text(x2 + card_w - 26, top_y + 172, "P_loss ≈ 0.33 Вт (у 16 разів менше)", size=11, bold=True, color="#065f46", anchor="end"))
    frags.append(text(x2 + 26, top_y + 196, "• Просадка шини живлення 5V BEC:", size=10.5, anchor="start"))
    frags.append(text(x2 + card_w - 26, top_y + 196, "Мінімальна (стабільні 5 В)", size=10.5, bold=True, color="#065f46", anchor="end"))
    frags.append(text(x2 + 26, top_y + 222, "• Достатній тонкий дріт AWG22 (економія 6 г)", size=10.5, color=MUTED, anchor="start"))

    frags.append(rect(x2 + 16, top_y + 248, card_w - 32, 74, fill="#ffffff", stroke="#059669", sw=1.2, rx=4))
    frags.append(text(x2 + card_w / 2, top_y + 268, "НАСЛІДОК ДЛЯ ПРОЄКТУВАННЯ:", size=10.5, bold=True, color="#065f46"))
    frags.append(text(x2 + card_w / 2, top_y + 288, "Мотори 2750–3800 KV, вищий ККД силового тракту,", size=10.5, color=INK))
    frags.append(text(x2 + card_w / 2, top_y + 306, "стабільне керування на всьому розряді.", size=10.5, color=INK))

    render(os.path.join(IMG, 'sub250-electrical-topology-comparison.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_kinetic_energy()
    fig_mass_breakdown()
    fig_electrical_topology()
    print("ok")
