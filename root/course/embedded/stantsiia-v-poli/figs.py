# -*- coding: utf-8 -*-
"""Генератор векторних схем для теми «Станція в полі: планшет, ноутбук, ретранслятор»."""

import os
import sys
import math

# Підключаємо svgkit із scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_field_gcs_architectures():
    """Порівняння трьох архітектурних форм польової наземної станції."""
    w, h = 980, 440
    frags = []

    frags.append(text(w / 2, 28, "Порівняння апаратних форм польової станції керування (GCS)", size=16, bold=True))

    cards = [
        {
            "title": "Захищений ноутбук (Rugged)",
            "subtitle": "Panasonic Toughbook / Dell Rugged",
            "x": 30, "w": 285,
            "pros": ["Яскравість >1000 nit (пряме сонце)", "Повний софт (QGC, MP, аналіз логів)", "Hot-Swap батареї, порти RS-232/LAN", "Фізична клавіатура у рукавицях"],
            "cons": ["Велика маса (3.5–5 кг)", "Високе споживання (45–70 Вт)", "Потребує столу або стійки"],
            "color": "#1e3d59"
        },
        {
            "title": "Польовий планшет (Tablet)",
            "subtitle": "Android / Windows QGroundControl",
            "x": 345, "w": 285,
            "pros": ["Мобільність, робота «з колін»", "Мала маса (600–900 г)", "Низьке споживання (15–22 Вт)", "Швидке тактичне розгортання"],
            "cons": ["Хибні натискання від крапель дощу", "Перегрів на сонці (термотротлінг)", "Обмежені фізичні інтерфейси"],
            "color": "#17b978"
        },
        {
            "title": "Інтегрований пульт (All-in-One)",
            "subtitle": "Herelink / SIYI / Smart Controller",
            "x": 660, "w": 290,
            "pros": ["Стіки RC + телеметрія + відео в одному", "Мінімальна затримка прямого керування", "Компактність, відсутність дротів", "Готовність до роботи за 30 секунд"],
            "cons": ["Неможливо винести радіо без реле", "Малий екран (5.5–7 дюймів)", "Складність підключення трекера"],
            "color": "#845ec2"
        }
    ]

    for c in cards:
        cx = c["x"]
        cw = c["w"]
        frags.append(rect(cx, 55, cw, 365, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
        frags.append(rect(cx, 55, cw, 56, fill=FILL, stroke="#cbd5e1", sw=1.5, rx=8))
        frags.append(text(cx + cw / 2, 80, c["title"], size=13, bold=True, color=c["color"]))
        frags.append(text(cx + cw / 2, 98, c["subtitle"], size=10, color=MUTED))

        frags.append(text(cx + 14, 132, "Переваги:", size=11, bold=True, color=FIELD, anchor="start"))
        y_cur = 152
        for p in c["pros"]:
            frags.append(circle(cx + 20, y_cur - 4, 3, fill=FIELD, stroke=FIELD))
            frags.append(text(cx + 30, y_cur, p, size=10.5, anchor="start"))
            y_cur += 24

        frags.append(line(cx + 14, y_cur + 4, cx + cw - 14, y_cur + 4, color="#e2e8f0", sw=1))
        y_cur += 22

        frags.append(text(cx + 14, y_cur, "Обмеження:", size=11, bold=True, color=POS, anchor="start"))
        y_cur += 20
        for cn in c["cons"]:
            frags.append(circle(cx + 20, y_cur - 4, 3, fill=POS, stroke=POS))
            frags.append(text(cx + 30, y_cur, cn, size=10.5, anchor="start"))
            y_cur += 24

    render(os.path.join(IMG_DIR, "field-gcs-architectures.svg"), w, h, *frags)


def fig_mast_repeater_topology():
    """Топологія зв'язку щогла-бліндаж: чому радіо виноситься нагору."""
    w, h = 980, 480
    frags = []

    frags.append(text(w / 2, 26, "Топологія виносного радіотракту: подолання рельєфу та втрат у кабелі", size=16, bold=True))

    # Ліва частина — бліндаж / оператор
    frags.append(rect(30, 60, 240, 390, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(150, 88, "Укриття / Позиція оператора", size=13, bold=True, color="#0f172a"))
    frags.append(line(45, 98, 255, 98, color="#cbd5e1", sw=1))

    frags.append(fitbox(45, 115, 210, 50, "GCS Термінал\n(Ноутбук / Планшет)", size=11, bold=True))
    frags.append(fitbox(45, 180, 210, 50, "Мережевий комутатор\n(Ethernet Switch + PoE)", size=11, fill="#e0f2fe", stroke="#0284c7"))
    frags.append(fitbox(45, 245, 210, 50, "Медіаконвертер SFP\n(Оптика BiDi 1.25G)", size=11, fill="#fef3c7", stroke="#d97706"))
    frags.append(fitbox(45, 310, 210, 50, "Буферне живлення\nLiFePO4 12.8V / 24V", size=11, fill="#dcfce7", stroke="#16a34a"))
    frags.append(fitbox(45, 375, 210, 55, "Штир заземлення\n(Вирівнювання потенціалу)", size=10, fill="#f1f5f9", stroke="#475569"))

    # Лінія зв'язку (кабель у траншеї / по землі)
    frags.append(rect(295, 195, 270, 140, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(430, 218, "Магістральна лінія (50–300 м)", size=11.5, bold=True, color="#334155"))
    frags.append(text(430, 242, "Варіант А: Оптоволокно (Tactical Fiber)", size=10.5, color="#d97706", bold=True))
    frags.append(text(430, 258, "100% гальванорозв'язка, TEMPEST-захист", size=9.5, color=MUTED))
    frags.append(text(430, 282, "Варіант Б: STP Cat6 + Passive PoE 48V", size=10.5, color="#0284c7", bold=True))
    frags.append(text(430, 298, "Дані UDP/RTSP + живлення в одному дроті", size=9.5, color=MUTED))
    frags.append(text(430, 320, "Нульові втрати ВЧ сигналу на дистанції!", size=10, color=FIELD, bold=True))

    frags.append(arrow(255, 205, 295, 205, color="#0284c7", sw=2))
    frags.append(arrow(255, 270, 295, 270, color="#d97706", sw=2))
    frags.append(arrow(565, 235, 605, 235, color="#0284c7", sw=2))

    # Права частина — щогла з ретранслятором
    frags.append(rect(605, 60, 345, 390, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(777, 88, "Телескопічна щогла (8–15 м)", size=13, bold=True, color="#0f172a"))
    frags.append(line(620, 98, 935, 98, color="#cbd5e1", sw=1))

    # Верхівка щогли
    frags.append(rect(620, 115, 315, 125, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(777, 134, "Masthead Box (Блок на верхівці)", size=11.5, bold=True, color=POS))
    frags.append(fitbox(630, 145, 145, 42, "Трансивер телеметрії\n(433/868/915 MHz)", size=9.5, fill="#ffffff"))
    frags.append(fitbox(780, 145, 145, 42, "Відеоприймач / OFDM\n(1.4 / 2.4 / 5.8 GHz)", size=9.5, fill="#ffffff"))
    frags.append(fitbox(630, 192, 145, 40, "Короткий ВЧ кабель\n(< 0.3 м, втрати <0.2 dB)", size=9, fill="#ffffff", stroke=FIELD))
    frags.append(fitbox(780, 192, 145, 40, "DC-DC Step-Down\n(48V -> 12V / 5V)", size=9, fill="#ffffff"))

    # Антена
    frags.append(fitbox(620, 250, 315, 45, "Спрямована / Всеспрямована антена (Gain 5–16 dBi)\nЧиста перша зона Френеля над лісосмугою", size=10, fill="#eff6ff", stroke="#3b82f6", bold=True))

    # Антенний трекер
    frags.append(fitbox(620, 305, 315, 55, "Опційний модуль: Антенний трекер (AAT)\nПриводи Pan/Tilt + Ковзне кільце (Slip Ring)\nАвтоматичне стеження за азимутом і кутом місця", size=9.5, fill="#f5f3ff", stroke="#7c3aed"))

    # Заземлення щогли
    frags.append(fitbox(620, 370, 315, 60, "Захист від наведеної електрики та блискавки\nІзолятори TVS/GDT на вході + контур заземлення щогли\n(Запобігає вигоранню портів при статиці)", size=9, fill="#f1f5f9", stroke="#475569"))

    render(os.path.join(IMG_DIR, "mast-repeater-topology.svg"), w, h, *frags)


def fig_antenna_tracker_geometry():
    """Геометрія розрахунку кутів азимуту та елевації трекера."""
    w, h = 940, 460
    frags = []

    frags.append(text(w / 2, 26, "Векторна геометрія наведення антенного трекера", size=16, bold=True))

    # Ліва панель: просторовий трикутник GCS - UAV
    frags.append(rect(30, 60, 470, 375, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(265, 85, "Просторова схема наведення", size=13, bold=True))

    # Точки
    gcs_x, gcs_y = 90, 360
    uav_x, uav_y = 420, 160
    proj_x, proj_y = 420, 360

    # Осі та площина горизонту
    frags.append(line(50, gcs_y, 470, gcs_y, color="#94a3b8", sw=1.2, dash="4,4"))
    frags.append(text(460, gcs_y + 18, "Горизонт", size=10, color=MUTED, anchor="end"))

    # Лінії трикутника
    frags.append(line(gcs_x, gcs_y, proj_x, proj_y, color="#2563eb", sw=2)) # d_ground
    frags.append(line(proj_x, proj_y, uav_x, uav_y, color=POS, sw=2))       # d_alt
    frags.append(line(gcs_x, gcs_y, uav_x, uav_y, color="#7c3aed", sw=2.5)) # d_slant

    # Точка GCS
    frags.append(circle(gcs_x, gcs_y, 7, fill="#2563eb", stroke="#1d4ed8", sw=2))
    frags.append(text(gcs_x, gcs_y + 24, "Трекер (GCS)", size=11, bold=True, color="#1d4ed8"))
    frags.append(text(gcs_x, gcs_y + 38, "(lat₁, lon₁, alt₁)", size=9.5, color=MUTED))

    # Точка UAV
    frags.append(circle(uav_x, uav_y, 7, fill=POS, stroke="#b91c1c", sw=2))
    frags.append(text(uav_x, uav_y - 22, "Борт (UAV)", size=11, bold=True, color=POS))
    frags.append(text(uav_x, uav_y - 8, "(lat₂, lon₂, alt₂)", size=9.5, color=MUTED))

    # Підписи сторін трикутника
    frags.append(text(250, gcs_y + 18, "Горизонтальна відстань (d_ground)", size=10.5, color="#2563eb", bold=True))
    frags.append(text(proj_x + 10, 260, "Різниця висот (Δh)", size=10.5, color=POS, bold=True, anchor="start"))
    frags.append(text(220, 230, "Прямий промінь (d_slant)", size=10.5, color="#7c3aed", bold=True))

    # Кут елевації (дуга)
    frags.append('<path d="M 140 360 A 50 50 0 0 0 134 326" fill="none" stroke="#d97706" stroke-width="2"/>')
    frags.append(text(155, 340, "Кут місця (El)", size=10.5, color="#d97706", bold=True, anchor="start"))

    # Права панель: формули та розрахунок азимуту
    frags.append(rect(520, 60, 390, 375, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(715, 85, "Математичний апарат розрахунку", size=13, bold=True))

    frags.append(rect(535, 105, 360, 95, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=6))
    frags.append(text(550, 125, "1. Розрахунок Азимуту (Bearing / Az):", size=11, bold=True, color="#1e40af", anchor="start"))
    frags.append(text(550, 146, "y = sin(Δlon) · cos(lat₂)", size=10, color=INK, anchor="start"))
    frags.append(text(550, 164, "x = cos(lat₁) · sin(lat₂) - sin(lat₁) · cos(lat₂) · cos(Δlon)", size=9.5, color=INK, anchor="start"))
    frags.append(text(550, 184, "Az = atan2(y, x)  [0° .. 360° від True North]", size=10, bold=True, color="#1e40af", anchor="start"))

    frags.append(rect(535, 210, 360, 95, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=6))
    frags.append(text(550, 230, "2. Розрахунок Елевації (Elevation / El):", size=11, bold=True, color="#991b1b", anchor="start"))
    frags.append(text(550, 251, "d_ground = R_землі · c  (ортодромічна дуга)", size=10, color=INK, anchor="start"))
    frags.append(text(550, 270, "Δh_eff = alt₂ - alt₁ - (d_ground² / 2R_землі)", size=9.5, color=INK, anchor="start"))
    frags.append(text(550, 290, "El = atan2(Δh_eff, d_ground)  [0° .. 90°]", size=10, bold=True, color="#991b1b", anchor="start"))

    frags.append(rect(535, 315, 360, 105, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(550, 335, "3. Коригування та фільтрація:", size=11, bold=True, color="#334155", anchor="start"))
    frags.append(text(550, 356, "• Компенсація власного курсу трекера: Az_cmd = Az - Yaw_base", size=9, color=INK, anchor="start"))
    frags.append(text(550, 374, "• Deadband зона: не рухати при зміні кута < 1.5° (антитільпання)", size=9, color=INK, anchor="start"))
    frags.append(text(550, 392, "• Обмеження кутової швидкості: Slew-rate limiter (макс. 45°/с)", size=9, color=INK, anchor="start"))
    frags.append(text(550, 410, "• Failsafe: утримання напрямку при втраті пакетів > 3.0 с", size=9, color=INK, anchor="start"))

    render(os.path.join(IMG_DIR, "antenna-tracker-geometry.svg"), w, h, *frags)


def fig_slip_ring_vs_wrap():
    """Порівняння механіки повороту: стандартний сервопривід проти ковзного кільця (Slip Ring)."""
    w, h = 940, 400
    frags = []

    frags.append(text(w / 2, 26, "Проблема скручування кабелів (Cable Wrap) та розв'язання через Slip Ring", size=16, bold=True))

    # Ліва колонка — Сервопривід з обмеженим кутом
    frags.append(rect(30, 55, 420, 325, fill="#fef2f2", stroke="#f87171", sw=1.5, rx=8))
    frags.append(text(240, 82, "Звичайна серво / прямий кабель (Безперервність порушена)", size=12, bold=True, color=POS))

    frags.append(fitbox(45, 100, 390, 60, "Апарат перетинає лінію 0°/360° (Північ / Задній сектор):\nСервопривід доходить до механічного упору 360°\nі змушений робити зворотний поворот (Unwrap) на -360°", size=10, fill="#ffffff", stroke="#fca5a5"))

    frags.append(fitbox(45, 170, 390, 75, "НАСЛІДОК ДЛЯ ЗВ'ЯЗКУ:\n• Час розвороту антени: 2.5–4.5 секунди\n• Повна втрата вузького радіопроменя під час маневру\n• Зрив відеопотоку та буферів MAVLink у критичний момент\n• Ризик перетирання та урвища сигнальних жил", size=9.5, fill="#ffffff", stroke=POS, bold=False))

    frags.append(fitbox(45, 255, 390, 110, "Симптом відмови:\nВтрата телеметрії щоразу, коли борт робить коло довкола станції\nабо виходить на глісаду посадки над точкою старту.\nКабелі дубіють на морозі і зламують роз'єми SMA/Ethernet.", size=9.5, fill="#ffffff", stroke="#94a3b8"))

    # Права колонка — Система з Slip Ring
    frags.append(rect(490, 55, 420, 325, fill="#f0fdf4", stroke="#4ade80", sw=1.5, rx=8))
    frags.append(text(700, 82, "Система з ковзним кільцем (Slip Ring / Rotary Joint)", size=12, bold=True, color=FIELD))

    frags.append(fitbox(505, 100, 390, 60, "Нескінченне обертання 360° по осі панорами (Yaw):\nСтатор з'єднаний з нерухомою щоглою,\nротор обертається разом з антенною платформою", size=10, fill="#ffffff", stroke="#86efac"))

    frags.append(fitbox(505, 170, 390, 75, "ПЕРЕВАГИ ДЛЯ ОПЕРАЦІЙНОЇ НАДІЙНОСТІ:\n• Найкоротший шлях наведення: поворот на мінімальний кут Δθ\n• Нульова затримка: промінь безперервно утримує ціль\n• Відсутність механічного натягу та втоми кабелю\n• Золото-золоті ковзні контакти для Ethernet 100M / RS-485", size=9.5, fill="#ffffff", stroke=FIELD, bold=False))

    frags.append(fitbox(505, 255, 390, 110, "Інженерне правило:\nВЧ радіомодуль монтується НА роторі поруч з антеною,\nа через Slip Ring спускаються виключно цифрові шини (Ethernet / RS-485)\nта живлення DC 12–24V. Це усуває втрати в ВЧ переході.", size=9.5, fill="#ffffff", stroke="#94a3b8"))

    render(os.path.join(IMG_DIR, "slip-ring-vs-wrap.svg"), w, h, *frags)


def fig_gcs_power_isolation_schematic():
    """Електрична схема живлення, гальванічної розв'язки та заземлення польової станції."""
    w, h = 980, 450
    frags = []

    frags.append(text(w / 2, 26, "Енергопостачання, гальванічна розв'язка та захист від завад польової GCS", size=16, bold=True))

    # Секція 1: Батарейний блок
    frags.append(rect(25, 55, 210, 375, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(130, 80, "Силове живлення", size=12, bold=True, color="#0f172a"))
    frags.append(fitbox(35, 95, 190, 60, "LiFePO4 Батарея 4S/8S\n(12.8V / 25.6V 60–100Ah)\nРобота від -20°C до +60°C", size=9.5, fill="#dcfce7", stroke="#16a34a"))
    frags.append(fitbox(35, 165, 190, 50, "BMS з захистом\n(Струм розряду до 50A,\nбалансування комірок)", size=9.5, fill="#ffffff", stroke="#94a3b8"))
    frags.append(fitbox(35, 225, 190, 55, "Плавкий запобіжник\n(Fuse 30A) +\nЗахист переполюсовки", size=9.5, fill="#ffffff", stroke=POS))
    frags.append(fitbox(35, 290, 190, 60, "Вхід резервного ДВЗ\nабо автогенератора\n(Шунт + TVS діод 1500W)", size=9, fill="#ffffff", stroke="#d97706"))
    frags.append(fitbox(35, 360, 190, 55, "Штир заземлення №1\n(Заземлення мінуса батареї\nв одній зірковій точці)", size=9, fill="#f1f5f9", stroke="#475569"))

    frags.append(arrow(235, 125, 275, 125, color="#16a34a", sw=2))

    # Секція 2: Блок розподілу та перетворення
    frags.append(rect(275, 55, 380, 375, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(465, 80, "Блок ізоляції та розподілу (GCS Power Hub)", size=12, bold=True, color="#0369a1"))

    # Канали живлення
    frags.append(rect(290, 95, 350, 72, fill="#f0f9ff", stroke="#bae6fd", sw=1.2, rx=6))
    frags.append(text(300, 115, "Канал А: Ноутбук / Планшет (19V / 12V Type-C PD)", size=10, bold=True, color="#0369a1", anchor="start"))
    frags.append(text(300, 133, "DC-DC Synchronous Buck-Boost (90W, ККД 96%)", size=9.5, color=MUTED, anchor="start"))
    frags.append(text(300, 151, "Фільтр синфазних завад (Common Mode Choke) на виході", size=9.5, color=FIELD, anchor="start"))

    frags.append(rect(290, 175, 350, 72, fill="#f0fdf4", stroke="#bbf7d0", sw=1.2, rx=6))
    frags.append(text(300, 195, "Канал Б: Щогла та Радіомодуль (48V PoE Injector)", size=10, bold=True, color="#15803d", anchor="start"))
    frags.append(text(300, 213, "Гальванічно ізольований DC-DC 12V -> 48V (1500V Isolation)", size=9.5, color=MUTED, anchor="start"))
    frags.append(text(300, 231, "Розриває земляну петлю між щоглою та укриттям!", size=9.5, color=FIELD, bold=True, anchor="start"))

    frags.append(rect(290, 255, 350, 75, fill="#fefce8", stroke="#fef08a", sw=1.2, rx=6))
    frags.append(text(300, 275, "Канал В: Сигнальні інтерфейси (RS-232 / RS-485 / USB)", size=10, bold=True, color="#a16207", anchor="start"))
    frags.append(text(300, 293, "Цифрові ізолятори (ADuM1401 / ISO7741 / Оптопари)", size=9.5, color=MUTED, anchor="start"))
    frags.append(text(300, 311, "TVS-діодні збірки на лініях даних (Захист від ESD до 15 kV)", size=9.5, color=POS, anchor="start"))

    frags.append(fitbox(290, 340, 350, 75, "Мережевий бар'єр Ethernet:\nТрансформаторна розв'язка 100/1000Base-T (1500 Vrms)\n+ Газорозрядники GDT на екранованій крученій парі STP", size=9.5, fill="#f8fafc", stroke="#64748b"))

    frags.append(arrow(655, 130, 695, 130, color="#0369a1", sw=2))
    frags.append(arrow(655, 210, 695, 210, color="#15803d", sw=2))
    frags.append(arrow(655, 290, 695, 290, color="#a16207", sw=2))

    # Секція 3: Споживачі
    frags.append(rect(695, 55, 260, 375, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(825, 80, "Польові споживачі", size=12, bold=True, color="#0f172a"))
    frags.append(fitbox(705, 95, 240, 65, "Робоче місце оператора\nНоутбук / Планшет\n(Чисте живлення без наведень\nвід генераторів)", size=9.5, fill="#ffffff", stroke="#0284c7"))
    frags.append(fitbox(705, 175, 240, 70, "Виносний блок щогли\n(Masthead Box / Радіомодуль)\nЖивлення 48V PoE по STP кабелю\nбез падіння напруги", size=9.5, fill="#ffffff", stroke="#16a34a"))
    frags.append(fitbox(705, 260, 240, 75, "Антенний трекер\nСервоприводи Pan/Tilt\n(Окремий ізольований DC-DC\nдля відсікання імпульсних завад)", size=9.5, fill="#ffffff", stroke="#d97706"))
    frags.append(fitbox(705, 345, 240, 70, "Штир заземлення №2\n(Заземлення щогли на місці монтажу;\nзавдяки розв'язці немає струмів у петлі)", size=9, fill="#f1f5f9", stroke="#475569"))

    render(os.path.join(IMG_DIR, "gcs-power-isolation-schematic.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_field_gcs_architectures()
    fig_mast_repeater_topology()
    fig_antenna_tracker_geometry()
    fig_slip_ring_vs_wrap()
    fig_gcs_power_isolation_schematic()
    print("Усі фігури згенеровано успішно.")
