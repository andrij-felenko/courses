# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми 'Кабелі й конектори'."""

import os
import sys

# Підключення svgkit із кореневої теки scripts (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_contact_constriction():
    """Фігура 1: Анатомія контакту, мікронерівності, лінії струму та золочення над нікелем."""
    w, h = 820, 430
    frags = []

    # Заголовок / фон
    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 36, "Мікроструктура електричного контакту: опір стягування (a-spots)", size=16, bold=True))

    # Верхній контакт (штекер / pin)
    frags.append(rect(60, 65, 320, 55, fill="#dbeafe", stroke=NEG, sw=2, rx=4))
    frags.append(text(220, 92, "Базовий метал штекера (Бронза / Латунь)", size=12, color=NEG, bold=True))
    frags.append(text(220, 108, "Пружна основа контакту", size=11, color=MUTED))

    # Шар нікелю та золота зверху
    frags.append(rect(60, 120, 320, 14, fill="#cbd5e1", stroke="#64748b", sw=1, rx=0))
    frags.append(text(220, 131, "Бар'єрний підшар Ni (1.3–2.5 мкм)", size=10, color="#334155"))
    frags.append(rect(60, 134, 320, 8, fill="#fef08a", stroke="#ca8a04", sw=1, rx=0))
    frags.append(text(220, 141, "Покриття Au (0.76 мкм / 30 µin)", size=9, color="#854d0e", bold=True))

    # Нижній контакт (гніздо / socket)
    frags.append(rect(60, 172, 320, 8, fill="#fef08a", stroke="#ca8a04", sw=1, rx=0))
    frags.append(rect(60, 180, 320, 14, fill="#cbd5e1", stroke="#64748b", sw=1, rx=0))
    frags.append(text(220, 191, "Бар'єрний підшар Ni (1.3–2.5 мкм)", size=10, color="#334155"))
    frags.append(rect(60, 194, 320, 55, fill="#dbeafe", stroke=NEG, sw=2, rx=4))
    frags.append(text(220, 222, "Базовий метал гнізда (Фосфориста бронза)", size=12, color=NEG, bold=True))
    frags.append(text(220, 238, "Нормальне зусилля притискання F_N = 1.0–2.5 Н", size=11, color=MUTED))

    # Сила притискання F_N
    frags.append(arrow(220, 48, 220, 64, color=POS, sw=2.5))
    frags.append(text(255, 58, "F_N (сила)", size=11, color=POS, bold=True))
    frags.append(arrow(220, 265, 220, 250, color=POS, sw=2.5))

    # Збільшена зона мікроконтактів (a-spots) праворуч
    frags.append(rect(430, 65, 340, 185, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(600, 86, "Збільшення контактної поверхні (×5000)", size=13, bold=True))

    # Профіль нерівностей (хвилясті метали)
    frags.append('<path d="M 450 120 Q 480 145 510 125 T 570 150 T 630 125 T 690 152 T 750 120 L 750 100 L 450 100 Z" fill="#fef08a" stroke="#ca8a04" stroke-width="1.5"/>')
    frags.append('<path d="M 450 200 Q 480 175 510 195 T 570 150 T 630 195 T 690 152 T 750 200 L 750 220 L 450 220 Z" fill="#fef08a" stroke="#ca8a04" stroke-width="1.5"/>')

    # Точки дотику (a-spots) біля X=570 та X=690
    frags.append(circle(570, 150, 4, fill=POS, stroke=POS, sw=1))
    frags.append(circle(690, 152, 4, fill=POS, stroke=POS, sw=1))
    frags.append(text(570, 140, "a-spot 1", size=10, color=POS, bold=True))
    frags.append(text(690, 142, "a-spot 2", size=10, color=POS, bold=True))

    # Лінії струму, що звужуються
    frags.append(line(540, 110, 565, 147, color=POS, sw=1.5, dash="3,2"))
    frags.append(line(570, 110, 570, 146, color=POS, sw=2))
    frags.append(line(600, 110, 575, 147, color=POS, sw=1.5, dash="3,2"))
    frags.append(line(565, 153, 540, 190, color=POS, sw=1.5, dash="3,2"))
    frags.append(line(570, 154, 570, 190, color=POS, sw=2))
    frags.append(line(575, 153, 600, 190, color=POS, sw=1.5, dash="3,2"))

    # Пояснення опору
    box_calc, _, _ = textbox(w / 2, 335,
                             "Повний опір контакту: R_contact = R_constriction + R_film + R_bulk\n"
                             "• Опір стягування (R_constriction): лінії струму стискаються до крихітних a-spots (0.01% площі)\n"
                             "• Опір плівки (R_film): оксиди й забруднення руйнуються зусиллям F_N та золоченням\n"
                             "• Типові значення: R_contact = 5–20 мОм для нового якісного роз'єму (до 100+ мОм при зносі)",
                             size=12, pad=12, fill="#f8fafc", stroke="#cbd5e1", min_w=740)
    frags.append(box_calc)

    render(os.path.join(IMG_DIR, "contact-constriction-resistance.svg"), w, h, *frags)


def fig_crimp_cross_section():
    """Фігура 2: Поперечний переріз якісного обтиску B-crimp (F-crimp)."""
    w, h = 820, 440
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 36, "Геометрія та якість холодного обтиску: B-crimp (F-crimp)", size=16, bold=True))

    # Ліва панель: переріз B-crimp
    frags.append(rect(40, 65, 360, 240, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(220, 88, "Переріз провідникового кримпу", size=14, bold=True))

    # Контур гільзи B-crimp (F-crimp)
    frags.append('<path d="M 120 180 C 120 240 320 240 320 180 C 320 130 250 120 220 160 C 190 120 120 130 120 180 Z" fill="#fed7aa" stroke="#ea580c" stroke-width="3"/>')

    # Деформовані жилки міді всередині (шестигранні соти)
    centers = [
        (180, 175), (200, 170), (220, 185), (240, 170), (260, 175),
        (170, 195), (190, 190), (210, 205), (230, 205), (250, 190), (270, 195),
        (190, 215), (210, 222), (230, 222), (250, 215)
    ]
    for cx, cy in centers:
        frags.append(circle(cx, cy, 9.5, fill="#f97316", stroke="#c2410c", sw=1.2))

    frags.append(text(220, 140, "Крила гільзи загнуті всередину", size=11, color="#c2410c", bold=True))
    frags.append(text(220, 260, "Газонепроникна зона (Gas-Tight Zone)", size=11, color=FIELD, bold=True))
    frags.append(text(220, 276, "Компактизація жил: 15–20% деформації", size=10, color=MUTED))

    # Стрілки висоти обтиску
    frags.append(line(335, 145, 335, 235, color=INK, sw=1.5))
    frags.append(arrow(335, 135, 335, 145, color=INK, sw=1.5))
    frags.append(arrow(335, 245, 335, 235, color=INK, sw=1.5))
    frags.append(text(370, 190, "Crimp\nHeight", size=10, bold=True))

    # Права панель: поздовжній вигляд контакту
    frags.append(rect(420, 65, 360, 240, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(600, 88, "Поздовжні зони обтискного контакту", size=14, bold=True))

    # Кабель з ізоляцією
    frags.append(rect(440, 160, 70, 45, fill="#3b82f6", stroke="#1d4ed8", sw=1.5, rx=3))
    frags.append(text(475, 186, "Ізоляція", size=10, color="#ffffff", bold=True))

    # Ізоляційний кримп
    frags.append(rect(510, 155, 45, 55, fill="#fdba74", stroke="#ea580c", sw=2, rx=2))
    frags.append(text(532, 145, "Кримп\nізоляції", size=9, bold=True))

    # Зазор
    frags.append(rect(555, 168, 25, 30, fill="#f97316", stroke="#c2410c", sw=1.5, rx=1))
    frags.append(text(567, 215, "Вікно", size=9, color=MUTED))

    # Провідниковий кримп
    frags.append(rect(580, 162, 50, 42, fill="#fb923c", stroke="#ea580c", sw=2, rx=2))
    frags.append(text(605, 145, "Провідниковий\nкримп", size=9, color=POS, bold=True))

    # Щітка жил попереду (Wire brush)
    frags.append(rect(630, 170, 20, 25, fill="#ea580c", stroke="#c2410c", sw=1.2, rx=1))
    frags.append(text(640, 215, "Вихід жил\n0.5–1 мм", size=9, color=MUTED))

    # Контактна частина (штир / гніздо)
    frags.append(rect(650, 166, 110, 32, fill="#fef08a", stroke="#ca8a04", sw=2, rx=2))
    frags.append(text(705, 185, "Контактний штир (Au/Sn)", size=10, color="#854d0e", bold=True))

    # Нижній блок критеріїв
    box_crimp, _, _ = textbox(w / 2, 360,
                              "Критерії надійності: (1) Відсутність надрізаних жилок • (2) Наявність переднього й заднього розтрубів (bellmouth 0.2–0.5 мм)\n"
                              "• (3) Ізоляція надійно охоплена без протикання • (4) Зусилля на виривання (Pull-out force) відповідає стандарту UL 486A\n"
                              "• Недотиск → перегрів та окиснення жил; Перетиск → розрив і втоминне стоншення міді біля розтруба",
                              size=12, pad=12, fill="#f8fafc", stroke="#cbd5e1", min_w=760)
    frags.append(box_crimp)

    render(os.path.join(IMG_DIR, "crimp-cross-section.svg"), w, h, *frags)


def fig_harness_ground_shift():
    """Фігура 3: Зсув потенціалу землі (Ground Shift) та деградація рівнів логіки."""
    w, h = 820, 420
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 36, "Вплив струму навантаження на опорну землю: Ground Shift у джгуті", size=16, bold=True))

    # Головна плата (Master PCB)
    frags.append(rect(40, 65, 200, 225, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=6))
    frags.append(text(140, 90, "Головний контролер", size=13, color="#1e40af", bold=True))
    frags.append(text(140, 108, "(Master MCU: 3.3V)", size=11, color=MUTED))

    frags.append(rect(60, 130, 160, 30, fill="#ffffff", stroke="#93c5fd", sw=1.5, rx=4))
    frags.append(text(140, 149, "TXD (3.3V логіка)", size=11, bold=True))

    frags.append(rect(60, 175, 160, 30, fill="#ffffff", stroke="#93c5fd", sw=1.5, rx=4))
    frags.append(text(140, 194, "VBUS (5.0V Джерело)", size=11, color=POS, bold=True))

    frags.append(rect(60, 220, 160, 30, fill="#ffffff", stroke="#93c5fd", sw=1.5, rx=4))
    frags.append(text(140, 239, "GND_Master (0.00 В)", size=11, color=NEG, bold=True))

    # Віддалений модуль (Slave Node: Серво + Сенсор)
    frags.append(rect(580, 65, 200, 225, fill="#fef2f2", stroke=POS, sw=2, rx=6))
    frags.append(text(680, 90, "Віддалений модуль", size=13, color="#991b1b", bold=True))
    frags.append(text(680, 108, "(Двигун + Датчик)", size=11, color=MUTED))

    frags.append(rect(600, 130, 160, 30, fill="#ffffff", stroke="#fca5a5", sw=1.5, rx=4))
    frags.append(text(680, 149, "RXD (Вхід логіки)", size=11, bold=True))

    frags.append(rect(600, 175, 160, 30, fill="#ffffff", stroke="#fca5a5", sw=1.5, rx=4))
    frags.append(text(680, 194, "V_local = 4.35 В", size=11, color=POS, bold=True))

    frags.append(rect(600, 220, 160, 30, fill="#ffffff", stroke="#fca5a5", sw=1.5, rx=4))
    frags.append(text(680, 239, "GND_Slave = +0.65 В!", size=11, color=POS, bold=True))

    # Джгут провідників посередині
    # Лінія живлення VBUS
    frags.append(line(220, 190, 600, 190, color=POS, sw=2.5))
    frags.append(arrow(360, 190, 420, 190, color=POS, sw=2.5))
    frags.append(text(410, 178, "I_load = 2.5 A (R_wire = 0.26 Ом)", size=11, color=POS, bold=True))

    # Сигнальна лінія
    frags.append(line(220, 145, 600, 145, color=FIELD, sw=1.8))
    frags.append(arrow(380, 145, 420, 145, color=FIELD, sw=1.8))
    frags.append(text(410, 133, "Сигнал UART: V_OL = 0.1 В від GND_Master", size=10, color=FIELD))

    # Зворотна шина землі GND
    frags.append(line(600, 235, 220, 235, color=NEG, sw=2.5))
    frags.append(arrow(440, 235, 380, 235, color=NEG, sw=2.5))
    frags.append(text(410, 252, "I_return = 2.5 A  →  ΔU_GND = +0.65 В", size=11, color=NEG, bold=True))

    # Блок наслідків
    box_conseq, _, _ = textbox(w / 2, 345,
                               "Механізм спотворення: Струм навантаження 2.5 А на сумарному опорі проводу й контактів (0.26 Ом) створює падіння ΔU_GND = 0.65 В.\n"
                               "• Для Slave-модуля напруга сигналу від Master сприймається як: V_in = 0.10 В − (+0.65 В) = −0.55 В (вибиває ESD-діоди)!\n"
                               "• При передачі від Slave до Master: нуль передається як 0.1 В + 0.65 В = 0.75 В (майже сягає V_IL_max = 0.80 В — помилки зв'язку)\n"
                               "• Рішення: товстіший AWG для GND, виділений окремий зворотний дріт сигнальної землі або диференційний RS-485 / CAN",
                               size=11.5, pad=12, fill="#f8fafc", stroke="#cbd5e1", min_w=760)
    frags.append(box_conseq)

    render(os.path.join(IMG_DIR, "harness-ground-shift.svg"), w, h, *frags)


def fig_shield_termination():
    """Фігура 4: Підключення екрана: кругове 360° заземлення проти 'свинячого хвоста' (Pigtail)."""
    w, h = 820, 410
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 36, "Заземлення екрана кабелю: круговий контакт 360° проти Pigtail", size=16, bold=True))

    # Ліва панель: НЕПРАВИЛЬНО - Pigtail
    frags.append(rect(40, 65, 350, 220, fill="#fef2f2", stroke=POS, sw=2, rx=6))
    frags.append(text(215, 88, "ПОМИЛКА: Свинячий хвіст (Pigtail)", size=14, color=POS, bold=True))

    # Кабель з екраном
    frags.append(rect(60, 140, 120, 40, fill="#64748b", stroke="#334155", sw=1.5, rx=3))
    frags.append(text(120, 164, "Екран кабелю", size=10, color="#ffffff", bold=True))

    # Сигнальні жили
    frags.append(line(180, 150, 310, 150, color=FIELD, sw=2))
    frags.append(line(180, 170, 310, 170, color=FIELD, sw=2))
    frags.append(text(245, 140, "Сигнальні жили", size=10, color=FIELD))

    # Скручений хвіст
    frags.append('<path d="M 170 175 C 190 220 220 220 250 200 L 310 200" fill="none" stroke="#c0392b" stroke-width="2.5"/>')
    frags.append(text(240, 220, "L_pigtail ≈ 30–60 нГн", size=11, color=POS, bold=True))
    frags.append(text(240, 235, "Випромінює завади на плату!", size=10, color=POS))

    # Роз'єм / плата
    frags.append(rect(310, 130, 60, 85, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=2))
    frags.append(text(340, 175, "Плата", size=11, bold=True))

    # Права панель: ПРАВИЛЬНО - 360° обтиск
    frags.append(rect(430, 65, 350, 220, fill="#f0fdf4", stroke=FIELD, sw=2, rx=6))
    frags.append(text(605, 88, "ПРАВИЛЬНО: Кругове заземлення 360°", size=14, color=FIELD, bold=True))

    # Кабель з екраном
    frags.append(rect(450, 140, 100, 40, fill="#64748b", stroke="#334155", sw=1.5, rx=3))
    frags.append(text(500, 164, "Екран кабелю", size=10, color="#ffffff", bold=True))

    # Металевий роз'єм / цанга 360°
    frags.append(rect(550, 125, 60, 70, fill="#cbd5e1", stroke="#475569", sw=2, rx=3))
    frags.append(text(580, 155, "Металевий\nкожух 360°", size=9, bold=True))

    # Металевий корпус приладу
    frags.append(rect(610, 105, 30, 110, fill="#94a3b8", stroke="#334155", sw=2, rx=1))
    frags.append(text(625, 230, "Корпус шасі", size=10, color="#334155", bold=True))

    # Сигнальні жили всередині
    frags.append(line(580, 150, 720, 150, color=FIELD, sw=2))
    frags.append(line(580, 170, 720, 170, color=FIELD, sw=2))

    # Плата
    frags.append(rect(720, 130, 45, 60, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=2))
    frags.append(text(742, 162, "PCB", size=10, bold=True))

    frags.append(text(680, 105, "Z_shield ≈ 0 Ом на ВЧ", size=11, color=FIELD, bold=True))
    frags.append(text(680, 120, "Струми завад стікають на шасі", size=10, color=FIELD))

    # Нижній висновок
    box_shield, _, _ = textbox(w / 2, 340,
                               "Фізична суть: Довгий тонкий дріт заземлення (pigtail 5 см) має індуктивність L ≈ 50 нГн.\n"
                               "• На частоті 100 МГц його імпеданс: X_L = 2π·f·L = 2π·100·10⁶ · 50·10⁻⁹ ≈ 31.4 Ом!\n"
                               "• Такий високий імпеданс повністю зводить нанівець дію екрана і перетворює його на передавальну антену.\n"
                               "• Круговий контакт 360° забезпечує низькоіндуктивний стік ВЧ струмів безпосередньо на металеве шасі.",
                               size=11.5, pad=12, fill="#f8fafc", stroke="#cbd5e1", min_w=760)
    frags.append(box_shield)

    render(os.path.join(IMG_DIR, "shield-termination-methods.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_contact_constriction()
    fig_crimp_cross_section()
    fig_harness_ground_shift()
    fig_shield_termination()
    print("Всі 4 фігури успішно згенеровано в img/")
