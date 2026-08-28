# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Ближня зона: зондування плати» (near-field-probing).

Фігури:
  1) near-vs-far-field-zones.svg        — хвильовий імпеданс Z_w = |E|/|H| від відстані r/(lambda/2pi) для електричного та магнітного джерел;
  2) shielded-loop-probe-anatomy.svg    — будова екранованої H-петлі (shielded loop) із розрізом екрана (gap) та придушенням E-поля;
  3) e-field-monopole-probe.svg         — ємнісний E-зонд: модель зв'язку C_couple із високоімпедансним вузлом dV/dt;
  4) pcb-emc-hotspots-probing.svg       — практичне зондування плати: струмова петля DC-DC, розріз землі (slot) та синфазний витік;
  5) emc-measurement-chain-spectrum.svg — вимірювальний тракт (зонд -> LNA -> аналізатор) та спектрограма гармонік.

Запуск: python figs.py
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GOLD    = "#caa24a"
GREEN_F = "#eef6ef"
BLUE_F  = "#e9eefb"
GOLD_F  = "#fff6e0"
RED_F   = "#fdecea"


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (s, color, sw, d))


# ── 1. Зони випромінювання та хвильовий опір простору ────────────────────────
def fig_zones():
    W, H = 960, 460
    f = [
        text(W / 2, 28, "Хвильовий імпеданс Zw = |E| / |H| залежно від відстані до джерела", size=16, bold=True),
        text(W / 2, 48, "у ближній реактивній зоні переважає вихідне поле джерела; у дальній зоні Zw стабілізується на 377 Ом", size=11, color=MUTED, italic=True)
    ]

    # Зони (фонові прямокутники)
    f.append(fitbox(90, 75, 300, 325, "", fill="#fbf0f0", stroke="#e0b4b4", sw=1.0, rx=4))
    f.append(text(240, 95, "Реактивна ближня зона (r < λ / 2π)", size=12, bold=True, color=POS))
    f.append(text(240, 112, "квазістатичні поля, енергія не відривається", size=10, color=MUTED))

    f.append(fitbox(390, 75, 290, 325, "", fill="#fffceb", stroke="#e6db9c", sw=1.0, rx=4))
    f.append(text(535, 95, "Зона випромінювання / Френеля", size=12, bold=True, color=GOLD))
    f.append(text(535, 112, "формування електромагнітної хвилі", size=10, color=MUTED))

    f.append(fitbox(680, 75, 230, 325, "", fill=BLUE_F, stroke="#a9bfec", sw=1.0, rx=4))
    f.append(text(795, 95, "Дальня зона (Far-Field)", size=12, bold=True, color=NEG))
    f.append(text(795, 112, "поперечна хвиля TEM, r > 2D²/λ", size=10, color=MUTED))

    # Вісь X та Y
    origin_x, origin_y = 90, 360
    axis_w, axis_h = 820, 260
    f.append(line(origin_x, origin_y, origin_x + axis_w, origin_y, color=INK, sw=1.5))
    f.append(line(origin_x, origin_y, origin_x, origin_y - axis_h, color=INK, sw=1.5))

    # Стрілки осей
    f.append(arrow(origin_x + axis_w - 5, origin_y, origin_x + axis_w + 15, origin_y, color=INK, sw=1.5))
    f.append(arrow(origin_x, origin_y - axis_h + 5, origin_x, origin_y - axis_h - 15, color=INK, sw=1.5))

    f.append(text(origin_x + axis_w + 20, origin_y + 4, "Відстань r", size=11, bold=True, anchor="start"))
    f.append(text(origin_x - 10, origin_y - axis_h - 18, "Імпеданс Zw (Ом)", size=11, bold=True, anchor="middle"))

    # Рівень 377 Ом (Z0)
    z0_y = 230
    f.append(line(origin_x, z0_y, origin_x + axis_w, z0_y, color=FIELD, sw=1.8, dash="5,4"))
    f.append(circle(origin_x, z0_y, 3, fill=FIELD, stroke=FIELD))
    f.append(text(origin_x - 15, z0_y + 4, "377 Ом", size=11, bold=True, color=FIELD, anchor="end"))
    f.append(text(origin_x - 15, z0_y + 18, "(Z₀ = √(μ₀/ε₀))", size=9, color=MUTED, anchor="end"))
    f.append(text(850, z0_y - 10, "Z₀ = 377 Ом (вільний простір)", size=11, bold=True, color=FIELD, anchor="end"))

    # Межова лінія r = lambda / (2pi)
    boundary_x = 390
    f.append(line(boundary_x, origin_y, boundary_x, 125, color=POS, sw=1.5, dash="4,3"))
    f.append(text(boundary_x, origin_y + 20, "r = λ / (2π)", size=11, bold=True, color=POS, anchor="middle"))
    f.append(text(boundary_x, origin_y + 34, "≈ 0.159 · λ", size=9, color=MUTED, anchor="middle"))

    # Позначки на осі X
    f.append(text(680, origin_y + 20, "r = λ", size=11, color=MUTED, anchor="middle"))
    f.append(line(680, origin_y - 3, 680, origin_y + 3, color=INK, sw=1.2))

    # Крива для електричного джерела (високий dV/dt, монополь): спадає від 4000 Ом до 377 Ом
    e_curve = [
        (110, 140), (140, 150), (180, 166), (230, 185), (290, 205),
        (340, 218), (390, 224), (460, 227), (550, 229), (680, 230), (880, 230)
    ]
    f.append(polyline(e_curve, color=POS, sw=2.5))
    f.append(text(120, 130, "Електричний диполь (E-джерело, dV/dt)", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(120, 145, "Zw >> 377 Ом у реактивній зоні (Zw ∝ 1/r³)", size=9, color=POS, anchor="start"))

    # Крива для магнітного джерела (високий dI/dt, струмова петля): зростає від 20 Ом до 377 Ом
    h_curve = [
        (110, 345), (140, 335), (180, 318), (230, 292), (290, 265),
        (340, 246), (390, 236), (460, 233), (550, 231), (680, 230), (880, 230)
    ]
    f.append(polyline(h_curve, color=NEG, sw=2.5))
    f.append(text(120, 320, "Магнітна петля (H-джерело, dI/dt)", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(120, 335, "Zw << 377 Ом у реактивній зоні (Zw ∝ r³)", size=9, color=NEG, anchor="start"))

    # Підсумковий блок унизу
    f.append(fitbox(90, 410, 820, 40, "", fill=FILL, stroke=LINE, sw=1.0, rx=4))
    f.append(text(500, 428, "Практичний висновок: на друкованій платі (r < 10 мм) магнітні й електричні поля розділені — їх шукають окремими H- та E-зондами", size=10, bold=True, color=INK, anchor="middle"))

    render(os.path.join(IMG, "near-vs-far-field-zones.svg"), W, H, *f)


# ── 2. Будова екранованої петлі H-поля ───────────────────────────────────────
def fig_shielded_loop():
    W, H = 960, 460
    f = [
        text(W / 2, 28, "Будова екранованої петлі магнітного поля (Shielded Loop Probe)", size=16, bold=True),
        text(W / 2, 48, "розріз екрана усуває паразитно замкнений екранний виток і забезпечує придушення синфазного E-поля", size=11, color=MUTED, italic=True)
    ]

    # Ліва частина: креслення самої петлі
    f.append(fitbox(20, 70, 450, 370, "", fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(245, 95, "Фізична конструкція петлі (коаксіал)", size=13, bold=True, color=INK))

    cx, cy, radius = 245, 230, 85

    gap_w = 12
    # Ліва півпетля екрана
    f.append('<path d="M %d %d A %d %d 0 1 0 %d %d" fill="none" stroke="%s" stroke-width="8"/>' %
             (cx - gap_w, cy - radius, radius, radius, cx - 18, cy + radius, GOLD))
    # Права півпетля екрана
    f.append('<path d="M %d %d A %d %d 0 0 1 %d %d" fill="none" stroke="%s" stroke-width="8"/>' %
             (cx + gap_w, cy - radius, radius, radius, cx + 18, cy + radius, GOLD))

    # Центральна жила всередині
    f.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (cx, cy, radius, POS))

    # Щілина у верхній точці (Gap)
    f.append(rect(cx - gap_w - 2, cy - radius - 10, (gap_w + 2) * 2, 20, fill="#ffffff", stroke=POS, sw=1.5, rx=2))
    f.append(text(cx, cy - radius - 16, "Щілина в екрані (Gap)", size=10, bold=True, color=POS))
    f.append(text(cx, cy - radius + 24, "розрив суцільного екрана", size=9, color=MUTED))

    # З'єднання в розрізі: центральна жила з'єднується з протилежним екраном праворуч
    f.append(circle(cx + gap_w + 2, cy - radius, 3, fill=POS, stroke=POS))
    f.append(line(cx - 2, cy - radius, cx + gap_w + 2, cy - radius, color=POS, sw=2))

    # Магнітний потік B через петлю
    f.append(circle(cx, cy, 30, fill=GREEN_F, stroke=FIELD, sw=1.5))
    f.append(text(cx, cy - 6, "Магнітний потік", size=10, bold=True, color=FIELD))
    f.append(text(cx, cy + 10, "Φ = ∫ B · dA", size=10, bold=True, color=FIELD))
    f.append(text(cx, cy + 26, "Bind -> Vind", size=9, color=FIELD))

    # Вихідна коаксіальна трубка до роз'єму SMA
    f.append(rect(cx - 16, cy + radius - 4, 32, 70, fill=GOLD, stroke=LINE, sw=1.2, rx=2))
    f.append(text(cx, cy + radius + 40, "SMA", size=10, bold=True, color=INK))
    f.append(text(cx, cy + radius + 90, "Коаксіальний роз'єм SMA (50 Ом)", size=10, bold=True, color=INK))

    # Права частина: Схема заміщення та дія екрана
    f.append(fitbox(490, 70, 450, 370, "", fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(715, 95, "Чому екран пригнічує електричне E-поле", size=13, bold=True, color=INK))

    # Блок 1: Індукція корисного сигналу H-полем
    f.append(fitbox(510, 120, 410, 85, "", fill=GREEN_F, stroke=FIELD, sw=1.2, rx=6))
    f.append(text(525, 140, "1. Магнітна компонента (H-поле, диференційний сигнал):", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(525, 160, "• Змінне поле H проникає крізь щілину в тіло петлі;", size=10, color=INK, anchor="start"))
    f.append(text(525, 178, "• Індукує ЕРС за законом Фарадея: Vind = -μ₀ · A · (dH/dt);", size=10, bold=True, color=INK, anchor="start"))
    f.append(text(525, 194, "• Створює чистий поперечний ВЧ-сигнал на навантаженні 50 Ом.", size=10, color=INK, anchor="start"))

    # Блок 2: Стікання паразитної синфазної завади E-поля
    f.append(fitbox(510, 218, 410, 95, "", fill=RED_F, stroke=POS, sw=1.2, rx=6))
    f.append(text(525, 238, "2. Електрична компонента (E-поле, синфазна завада):", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(525, 258, "• Перепад напруги dV/dt наводить ємнісний струм на екран;", size=10, color=INK, anchor="start"))
    f.append(text(525, 276, "• Симетричний екран ділить струм на дві рівні протифазні гілки;", size=10, color=INK, anchor="start"))
    f.append(text(525, 294, "• Паразитний струм стікає на землю приладу, не потрапляючи в жилу.", size=10, bold=True, color=INK, anchor="start"))

    # Блок 3: Просторова роздільна здатність залежно від діаметра
    f.append(fitbox(510, 325, 410, 100, "", fill=BLUE_F, stroke=NEG, sw=1.2, rx=6))
    f.append(text(525, 345, "3. Розміри петель та призначення:", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(525, 365, "• ⌀ 30–50 мм: висока чутливість, оглядовий пошук витоків;", size=10, color=INK, anchor="start"))
    f.append(text(525, 385, "• ⌀ 10–15 мм: локалізація функціонального блока (DC-DC, PHY);", size=10, color=INK, anchor="start"))
    f.append(text(525, 405, "• ⌀ 2–5 мм: точкова локалізація конкретної доріжки чи виводу IC.", size=10, bold=True, color=INK, anchor="start"))

    render(os.path.join(IMG, "shielded-loop-probe-anatomy.svg"), W, H, *f)


# ── 3. Будова та еквівалентна схема електричного E-зонда ────────────────────
def fig_e_field_probe():
    W, H = 960, 420
    f = [
        text(W / 2, 28, "Електричний E-зонд: ємнісний зв'язок із високоімпедансними вузлами dV/dt", size=16, bold=True),
        text(W / 2, 48, "виявляє лінії тактових сигналів, виводи ШІМ, непідключені виводи мікросхем та радіатори охолодження", size=11, color=MUTED, italic=True)
    ]

    # Ліва частина: Конструкція E-зонда біля друкованої плати
    f.append(fitbox(20, 70, 430, 330, "", fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(235, 95, "Фізична взаємодія вістря E-зонда з платою", size=13, bold=True, color=INK))

    # Корпус зонда (коаксіал)
    f.append(rect(205, 120, 60, 100, fill=GOLD, stroke=LINE, sw=1.5, rx=3))
    f.append(text(235, 160, "Екран", size=11, bold=True, color=INK))
    f.append(text(235, 180, "(GND)", size=10, color=MUTED))

    # Оголений штир (монополь 1–2 мм) - починається від нижнього краю екрана
    f.append(line(235, 220, 235, 275, color=POS, sw=3))
    f.append(circle(235, 275, 4, fill=POS, stroke=POS))
    f.append(text(295, 265, "Оголене вістря", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(295, 280, "(монополь 1–2 мм)", size=9, color=MUTED, anchor="start"))

    # Лінії електричного поля E до доріжки
    for dx in [-25, -15, 0, 15, 25]:
        f.append(line(235, 275, 235 + dx * 1.5, 325, color="#e74c3c", sw=1.2, dash="3,2"))
    f.append(text(150, 305, "Поле E (dV/dt)", size=10, bold=True, color=POS))

    # Доріжка друкованої плати
    f.append(rect(100, 325, 270, 14, fill="#2ecc71", stroke="#27ae60", sw=1.5, rx=2))
    f.append(text(235, 336, "Доріжка PCB з високим dV/dt (напр. SW вузол DC-DC)", size=10, bold=True, color="#ffffff"))

    # Діелектрик плати FR-4
    f.append(rect(80, 342, 310, 20, fill="#d4efdf", stroke="#a9dfbf", sw=1.0))
    f.append(text(235, 356, "Діелектрик FR-4 (εr ≈ 4.3)", size=9, color="#1e8449"))

    # Суцільна земля плати
    f.append(rect(80, 364, 310, 10, fill=GOLD, stroke=LINE, sw=1.2))
    f.append(text(235, 388, "Опорна площина землі (GND Plane)", size=10, bold=True, color=GOLD))

    # Права частина: Еквівалентна електрична схема
    f.append(fitbox(470, 70, 470, 330, "", fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(705, 95, "Еквівалентна схема ємнісного вимірювального тракту", size=13, bold=True, color=INK))

    # Генератор напруги dV/dt
    f.append(circle(530, 200, 18, fill="#ffffff", stroke=POS, sw=1.8))
    f.append(text(530, 205, "V(t)", size=11, bold=True, color=POS))
    f.append(text(530, 168, "Джерело dV/dt", size=9, color=MUTED, anchor="middle"))

    # Лінія до ємності зв'язку C_couple
    f.append(line(548, 200, 610, 200, color=INK, sw=1.8))

    # Конденсатор C_couple (0.1 .. 1 пФ)
    f.append(line(610, 185, 610, 215, color=INK, sw=2.5))
    f.append(line(618, 185, 618, 215, color=INK, sw=2.5))
    f.append(text(614, 170, "C_couple", size=11, bold=True, color=POS))
    f.append(text(614, 235, "0.1–1.0 пФ", size=9, color=MUTED))

    f.append(line(618, 200, 690, 200, color=INK, sw=1.8))

    # Вхідний опір вимірювача 50 Ом
    f.append(line(690, 200, 760, 200, color=INK, sw=1.8))
    f.append(circle(690, 200, 3, fill=INK, stroke=INK))

    # Навантаження R_in = 50 Ом
    f.append(line(690, 200, 690, 240, color=INK, sw=1.8))
    f.append(rect(678, 240, 24, 45, fill="#ffffff", stroke=NEG, sw=1.8, rx=2))
    f.append(text(690, 266, "50 Ω", size=10, bold=True, color=NEG))
    f.append(text(725, 266, "R_вх", size=10, color=MUTED, anchor="start"))
    f.append(line(690, 285, 690, 320, color=INK, sw=1.8))

    # Спектроаналізатор / приймач
    f.append(fitbox(760, 160, 150, 80, "", fill=BLUE_F, stroke=NEG, sw=1.5, rx=6))
    f.append(text(835, 190, "Аналізатор / LNA", size=11, bold=True, color=NEG))
    f.append(text(835, 210, "V_out = I_probe · 50 Ом", size=9, bold=True, color=INK))

    # Спільна земля
    f.append(line(530, 218, 530, 320, color=INK, sw=1.8))
    f.append(line(510, 320, 800, 320, color=INK, sw=1.8))
    f.append(text(655, 340, "Спільна ВЧ-земля системи", size=10, color=MUTED))

    # Формула струму зонда
    f.append(fitbox(490, 355, 430, 35, "", fill="#fff9e6", stroke=GOLD, sw=1.0, rx=4))
    f.append(text(705, 377, "I_probe = C_couple · (dV / dt)  =>  V_out ∝ f · C_couple · V_peak", size=10, bold=True, color=INK))

    render(os.path.join(IMG, "e-field-monopole-probe.svg"), W, H, *f)


# ── 4. Практичне зондування плати: 3 ключові гарячі точки ЕМС ────────────────
def fig_pcb_hotspots():
    W, H = 960, 480
    f = [
        text(W / 2, 28, "Типові джерела електромагнітної емісії на друкованій платі", size=16, bold=True),
        text(W / 2, 48, "три головні дефекти: комутаційна петля DC-DC, розріз земляного полігону та синфазний витік у кабель", size=11, color=MUTED, italic=True)
    ]

    # Панель 1: Струмова петля DC-DC (Buck Converter)
    f.append(fitbox(20, 70, 295, 390, "", fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(167, 95, "1. Комутаційна петля DC-DC", size=12, bold=True, color=POS))
    f.append(text(167, 112, "Швидкий струм dI/dt (H-поле)", size=10, color=MUTED))

    # Схема розташування елементів на платі
    f.append(rect(45, 135, 60, 40, fill="#e8f8f5", stroke="#1abc9c", sw=1.5, rx=3))
    f.append(text(75, 160, "Cin", size=11, bold=True, color="#16a085"))

    f.append(rect(145, 135, 75, 40, fill="#fdebd0", stroke="#e67e22", sw=1.5, rx=3))
    f.append(text(182, 160, "MOSFET/IC", size=11, bold=True, color="#d35400"))

    f.append(rect(230, 205, 65, 40, fill="#ebf5fb", stroke="#3498db", sw=1.5, rx=3))
    f.append(text(262, 230, "L_out", size=11, bold=True, color="#2980b9"))

    # Червона струмова петля
    loop_pts = [(105, 155), (145, 155), (180, 175), (180, 220), (75, 220), (75, 175)]
    f.append(polyline(loop_pts + [(105, 155)], color=POS, sw=2.5))
    f.append(text(128, 195, "Гаряча петля", size=10, bold=True, color=POS))
    f.append(text(128, 209, "dI/dt до 10 А/нс", size=9, color=POS))

    # H-зонд над петлею
    f.append(circle(128, 265, 20, fill="none", stroke=POS, sw=2.5))
    f.append(line(128, 285, 128, 330, color=GOLD, sw=3))
    f.append(text(128, 345, "H-зонд паралельно платі", size=10, bold=True, color=INK))

    f.append(fitbox(30, 365, 275, 80, "", fill=RED_F, stroke=POS, sw=1.0, rx=4))
    f.append(text(167, 385, "Дефект: велика площа петлі Cin -> Q1 -> GND.", size=9, bold=True, color=POS))
    f.append(text(167, 403, "Рішення: конденсатор Cin впритул до виводів", size=9, color=INK))
    f.append(text(167, 421, "живлення і землі мікросхеми перетворювача.", size=9, color=INK))

    # Панель 2: Перетин розрізу землі (Ground Slot Crossing)
    f.append(fitbox(330, 70, 295, 390, "", fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(477, 95, "2. Перетин розрізу землі", size=12, bold=True, color=GOLD))
    f.append(text(477, 112, "Розрив зворотного струму", size=10, color=MUTED))

    # Земляний полігон з розрізом
    f.append(rect(350, 135, 115, 110, fill="#d5dbdb", stroke="#95a5a6", sw=1.2))
    f.append(rect(490, 135, 115, 110, fill="#d5dbdb", stroke="#95a5a6", sw=1.2))
    f.append(text(407, 185, "GND (Аналог)", size=9, bold=True, color="#566573"))
    f.append(text(547, 185, "GND (Цифра)", size=9, bold=True, color="#566573"))

    # Розріз (слот)
    f.append(rect(465, 135, 25, 110, fill="#ffffff", stroke="#c0392b", sw=1.2))
    f.append(text(477, 260, "Щілина (Slot)", size=9, bold=True, color=POS))

    # Сигнальна доріжка через щілину
    f.append(line(360, 155, 590, 155, color="#27ae60", sw=2.5))
    f.append(text(477, 148, "Сигнал (CLK)", size=9, bold=True, color="#27ae60"))

    # Обхідний зворотний струм навколо щілини (пунктирна петля нижче)
    return_pts = [(570, 165), (570, 230), (370, 230), (370, 165)]
    f.append(polyline(return_pts, color=POS, sw=2.0, dash="4,3"))
    f.append(text(477, 215, "Обхідний струм повернення", size=9, bold=True, color=POS))

    # H-зонд над щілиною
    f.append(circle(477, 290, 18, fill="none", stroke=POS, sw=2.5))
    f.append(line(477, 308, 477, 340, color=GOLD, sw=3))
    f.append(text(477, 352, "Потужне поле витоку над щілиною", size=9, bold=True, color=INK))

    f.append(fitbox(340, 365, 275, 80, "", fill=GOLD_F, stroke=GOLD, sw=1.0, rx=4))
    f.append(text(477, 385, "Дефект: зворотний струм огинає розріз,", size=9, bold=True, color=GOLD))
    f.append(text(477, 403, "утворюючи величезну рамкову антену.", size=9, color=INK))
    f.append(text(477, 421, "Рішення: суцільна земля без поперечних щілин.", size=9, color=INK))

    # Панель 3: Синфазне випромінювання кабелю (Common-Mode Cable)
    f.append(fitbox(645, 70, 295, 390, "", fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(792, 95, "3. Синфазний витік у кабель", size=12, bold=True, color=NEG))
    f.append(text(792, 112, "Кабель як дипольна антена", size=10, color=MUTED))

    # Плата та роз'єм
    f.append(rect(665, 140, 120, 100, fill="#e8f6f3", stroke="#1abc9c", sw=1.5, rx=4))
    f.append(text(725, 180, "Друкована", size=10, bold=True, color=INK))
    f.append(text(725, 196, "плата (PCB)", size=10, bold=True, color=INK))

    # Джерело шуму землі всередині плати
    f.append(text(725, 225, "ΔVgnd = L · dI/dt", size=9, color=POS))

    # Роз'єм
    f.append(rect(785, 165, 25, 50, fill=GOLD, stroke=LINE, sw=1.2))
    f.append(text(797, 192, "IO", size=9, bold=True))

    # Кабель, що відходить
    f.append(rect(810, 183, 110, 14, fill="#34495e", stroke=LINE, sw=1.2, rx=2))
    f.append(text(865, 172, "Зовнішній кабель (USB/шлейф)", size=9, bold=True, color=INK))

    # Синфазний струм I_cm по кабелю
    f.append(arrow(820, 190, 890, 190, color=POS, sw=2.0))
    f.append(text(865, 210, "Синфазний I_cm (мкА)", size=9, bold=True, color=POS))

    # Струмові кліщі або H-зонд біля роз'єму
    f.append(circle(805, 280, 18, fill="none", stroke=NEG, sw=2.5))
    f.append(line(805, 298, 805, 340, color=GOLD, sw=3))
    f.append(text(792, 352, "Зондування вхідної горловини кабелю", size=9, bold=True, color=INK))

    f.append(fitbox(655, 365, 275, 80, "", fill=BLUE_F, stroke=NEG, sw=1.0, rx=4))
    f.append(text(792, 385, "Дефект: струм 5–10 мкА в кабель 1 м", size=9, bold=True, color=NEG))
    f.append(text(792, 403, "провалює сертифікацію CISPR Class B.", size=9, color=INK))
    f.append(text(792, 421, "Рішення: феритовий фільтр, синфазний дросель.", size=9, color=INK))

    render(os.path.join(IMG, "pcb-emc-hotspots-probing.svg"), W, H, *f)


# ── 5. Вимірювальний тракт та спектрограма гармонік ──────────────────────────
def fig_spectrum_analysis():
    W, H = 960, 460
    f = [
        text(W / 2, 28, "Вимірювальний тракт зондування та ідентифікація гармонік", size=16, bold=True),
        text(W / 2, 48, "поєднання зонда, підсилювача LNA та аналізатора спектра дозволяє виявити джерело за кроком гребінки", size=11, color=MUTED, italic=True)
    ]

    # Верхній блок: Апаратний вимірювальний ланцюг
    f.append(fitbox(20, 70, 920, 90, "", fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(480, 88, "Апаратний вимірювальний тракт (RF Signal Chain)", size=12, bold=True, color=INK))

    # Блоки тракту: Зонд -> Атенюатор/Захист -> LNA -> Спектроаналізатор
    f.append(fitbox(40, 105, 140, 45, "", fill=GOLD_F, stroke=GOLD, sw=1.5, rx=4))
    f.append(text(110, 125, "H/E-зонд", size=11, bold=True, color=GOLD))
    f.append(text(110, 140, "AF(f) / ZT(f)", size=9, color=MUTED))

    f.append(arrow(180, 127, 230, 127, color=LINE, sw=1.8))

    f.append(fitbox(230, 105, 150, 45, "", fill="#fcf3cf", stroke="#f39c12", sw=1.2, rx=4))
    f.append(text(305, 125, "Атенюатор 10 дБ", size=10, bold=True, color="#b7950b"))
    f.append(text(305, 140, "Захист входу LNA", size=9, color=MUTED))

    f.append(arrow(380, 127, 430, 127, color=LINE, sw=1.8))

    f.append(fitbox(430, 105, 160, 45, "", fill=GREEN_F, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(510, 125, "ВЧ-підсилювач LNA", size=11, bold=True, color=FIELD))
    f.append(text(510, 140, "Підсилення +20–30 дБ", size=9, color=MUTED))

    f.append(arrow(590, 127, 640, 127, color=LINE, sw=1.8))

    f.append(fitbox(640, 105, 280, 45, "", fill=BLUE_F, stroke=NEG, sw=1.5, rx=4))
    f.append(text(780, 125, "Спектроаналізатор / SDR (50 Ом)", size=11, bold=True, color=NEG))
    f.append(text(780, 140, "RBW: 9–120 кГц, Detector: Peak / QP", size=9, color=MUTED))

    # Нижній блок: Спектрограма на екрані приладу
    f.append(fitbox(20, 175, 920, 270, "", fill="#151922", stroke="#2c3e50", sw=1.5, rx=8))
    f.append(text(480, 198, "Спектр електромагнітної емісії (дБмкВ проти Частоти)", size=12, bold=True, color="#ecf0f1"))

    # Сітка спектрограми
    gx0, gy0, gw, gh = 80, 220, 800, 180
    f.append(rect(gx0, gy0, gw, gh, fill="#0d1117", stroke="#30363d", sw=1.0))

    # Горизонтальні лінії сітки (рівні напруги в дБмкВ)
    for i, db in enumerate([60, 45, 30, 15, 0]):
        y = gy0 + i * 36
        f.append(line(gx0, y, gx0 + gw, y, color="#21262d", sw=1.0, dash="2,4"))
        f.append(text(gx0 - 10, y + 4, "%d" % db, size=9, color="#8b949e", anchor="end"))
    f.append(text(gx0 - 15, gy0 - 10, "дБмкВ", size=9, bold=True, color="#8b949e", anchor="end"))

    # Вертикальні лінії сітки (частота 0 .. 200 МГц)
    for i, freq in enumerate([0, 25, 50, 75, 100, 125, 150, 175, 200]):
        x = gx0 + i * 100
        f.append(line(x, gy0, x, gy0 + gh, color="#21262d", sw=1.0, dash="2,4"))
        f.append(text(x, gy0 + gh + 15, "%d МГц" % freq, size=9, color="#8b949e"))

    # Ліміт CISPR 32 Class B (червона лінія)
    f.append(line(gx0 + 120, gy0 + 60, gx0 + gw, gy0 + 60, color="#e74c3c", sw=1.8, dash="6,3"))
    f.append(text(gx0 + gw - 10, gy0 + 52, "Ліміт CISPR 32 Class B (37 дБмкВ/м)", size=9, bold=True, color="#e74c3c", anchor="end"))

    # Шумова підлога спектра (Noise Floor ~ 10 дБмкВ)
    floor_pts = []
    for x in range(gx0, gx0 + gw + 1, 10):
        noise = math.sin(x * 0.2) * 3 + math.cos(x * 0.47) * 2
        floor_pts.append((x, gy0 + gh - 25 + noise))
    f.append(polyline(floor_pts, color="#484f58", sw=1.0))
    f.append(text(gx0 + 70, gy0 + gh - 8, "Шумова підлога вимірювального тракту", size=9, color="#8b949e"))

    # Гармонійна гребінка тактового генератора 25 МГц (Ethernet PHY): 25, 50, 75, 100, 125, 150, 175, 200 МГц
    harmonics = [
        (25, 48, "1-ша (25 МГц)"),
        (50, 42, "2-га (50 МГц)"),
        (75, 52, "3-тя (75 МГц) - ПЕРЕВИЩЕННЯ!"),
        (100, 36, "4-та (100 МГц)"),
        (125, 46, "5-та (125 МГц) - ПЕРЕВИЩЕННЯ!"),
        (150, 32, "6-та (150 МГц)"),
        (175, 38, "7-ма (175 МГц)"),
        (200, 26, "8-ма (200 МГц)")
    ]

    for freq, db, lbl in harmonics:
        x = gx0 + int((freq / 200.0) * gw)
        y = gy0 + int(((60 - db) / 60.0) * gh)
        # Пік спектра
        peak_color = "#e74c3c" if db > 40 else "#2ecc71"
        f.append(line(x, gy0 + gh - 25, x, y, color=peak_color, sw=2.5))
        f.append(circle(x, y, 3.5, fill=peak_color, stroke="#ffffff", sw=1.0))

        # Позначка для критичних піків
        if "ПЕРЕВИЩЕННЯ" in lbl:
            f.append(arrow(x + 25, y - 15, x + 4, y - 2, color="#e74c3c", sw=1.2))
            f.append(text(x + 28, y - 18, lbl, size=9, bold=True, color="#e74c3c", anchor="start"))

    # Висновок під спектрограмою
    f.append(text(gx0 + 20, gy0 + 25, "Δf = 25 МГц постійний інтервал між піками -> джерело: тактовий кварц / лінія TX Ethernet", size=10, bold=True, color="#f39c12", anchor="start"))

    render(os.path.join(IMG, "emc-measurement-chain-spectrum.svg"), W, H, *f)


def main():
    fig_zones()
    fig_shielded_loop()
    fig_e_field_probe()
    fig_pcb_hotspots()
    fig_spectrum_analysis()
    print("All figures successfully generated in %s" % IMG)


if __name__ == "__main__":
    main()
