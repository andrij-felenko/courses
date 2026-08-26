# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def svg_path(d, fill="none", stroke=LINE, sw=1.5):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


def fig_thermal_telemetry_nodes():
    w, h = 820, 480
    frags = []

    # Тло блоку плати
    frags.append(rect(20, 20, 780, 440, fill="#f8fafc", stroke="#0f172a", sw=2, rx=10))
    frags.append(text(410, 48, "Архітектура температурної телеметрії у вбудованій системі", size=16, bold=True, color="#0f172a"))

    # Домен 1: MCU / SoC Die
    frags.append(rect(40, 75, 230, 225, fill="#eff6ff", stroke="#2563eb", sw=1.8, rx=8))
    frags.append(text(155, 102, "Кристал MCU / SoC (T_j)", size=13, bold=True, color="#1d4ed8"))
    frags.append(rect(55, 118, 200, 48, fill="#ffffff", stroke="#93c5fd", sw=1, rx=5))
    frags.append(text(155, 137, "Вбудований p-n перехід", size=11, bold=True, color="#1e40af"))
    frags.append(text(155, 153, "Калібрування: TS_CAL1/2", size=10, color="#3b82f6"))
    frags.append(text(155, 185, "Теплова стала: τ ≈ 20–50 мс", size=11, bold=True, color="#0f172a"))
    frags.append(text(155, 205, "Швидкий відгук на частоту", size=10, color="#475569"))
    frags.append(text(155, 225, "Локальний градієнт ядра", size=10, color="#475569"))
    frags.append(text(155, 250, "Межа: T_max = +105 °C", size=11, bold=True, color="#b91c1c"))
    frags.append(text(155, 275, "Телеметрія: Внутрішній АЦП", size=10, color="#1e293b"))

    # Домен 2: Power MOSFETs / DC-DC
    frags.append(rect(295, 75, 230, 225, fill="#fef2f2", stroke="#dc2626", sw=1.8, rx=8))
    frags.append(text(410, 102, "Силовий каскад (T_fet)", size=13, bold=True, color="#b91c1c"))
    frags.append(rect(310, 118, 200, 48, fill="#ffffff", stroke="#fca5a5", sw=1, rx=5))
    frags.append(text(410, 137, "SMD NTC на мідному стоку", size=11, bold=True, color="#991b1b"))
    frags.append(text(410, 153, "Пакет 0603 / 0402 біля Drain", size=10, color="#ef4444"))
    frags.append(text(410, 185, "Теплова стала: τ ≈ 1–3 с", size=11, bold=True, color="#0f172a"))
    frags.append(text(410, 205, "Втрати I²R + комутація", size=10, color="#475569"))
    frags.append(text(410, 225, "Залежить від струму мотора", size=10, color="#475569"))
    frags.append(text(410, 250, "Межа: T_max = +90 °C", size=11, bold=True, color="#b91c1c"))
    frags.append(text(410, 275, "Телеметрія: Дільник на АЦП", size=10, color="#1e293b"))

    # Домен 3: Battery Pack
    frags.append(rect(550, 75, 230, 225, fill="#fffbeb", stroke="#d97706", sw=1.8, rx=8))
    frags.append(text(665, 102, "Акумулятор (T_batt)", size=13, bold=True, color="#b45309"))
    frags.append(rect(565, 118, 200, 48, fill="#ffffff", stroke="#fcd34d", sw=1, rx=5))
    frags.append(text(665, 137, "NTC терморезистор у паку", size=11, bold=True, color="#92400e"))
    frags.append(text(665, 153, "Контакт із тілом комірки", size=10, color="#f59e0b"))
    frags.append(text(665, 185, "Теплова стала: τ ≈ 30–90 с", size=11, bold=True, color="#0f172a"))
    frags.append(text(665, 205, "Велика теплоємність комірки", size=10, color="#475569"))
    frags.append(text(665, 225, "Захист від теплового розгону", size=10, color="#475569"))
    frags.append(text(665, 250, "Межа: T_max = +60 °C", size=11, bold=True, color="#b91c1c"))
    frags.append(text(665, 275, "Телеметрія: BMS / АЦП вхід", size=10, color="#1e293b"))

    # Стрілки зведення телеметрії
    frags.append(arrow(155, 300, 260, 345, color="#2563eb", sw=2))
    frags.append(arrow(410, 300, 410, 345, color="#dc2626", sw=2))
    frags.append(arrow(665, 300, 560, 345, color="#d97706", sw=2))

    # Нижній блок: Max Envelope Selector & Thermal Manager
    frags.append(rect(180, 350, 460, 95, fill="#ffffff", stroke="#0f172a", sw=2, rx=8))
    frags.append(text(410, 375, "Блок узгодження теплового профілю (Thermal Envelope Engine)", size=13, bold=True, color="#0f172a"))
    frags.append(text(410, 398, "Нормалізація: e_i = T_i / T_limit_i  |  e_worst = max(e_die, e_fet, e_batt)", size=11, bold=True, color="#1e293b"))
    frags.append(text(410, 422, "Вихід на скінченний автомат FSM + ПІ-регулятор обмеження потужності", size=11, color="#047857"))

    render(os.path.join(IMG_DIR, "thermal-telemetry-nodes.svg"), w, h, *frags)


def fig_cascade_zones():
    w, h = 840, 460
    frags = []

    frags.append(rect(20, 20, 800, 420, fill="#f8fafc", stroke="#0f172a", sw=2, rx=10))
    frags.append(text(420, 48, "Багаторівневий каскад термозахисту та діапазони регулювання", size=16, bold=True, color="#0f172a"))

    zones = [
        ("0–55 °C", "ШТАТНИЙ РЕЖИМ (NORMAL)", "100% продуктивність. Частота CPU макс, радіо 20 dBm, повний струм двигунів.", "#f0fdf4", "#16a34a", "#15803d"),
        ("55–70 °C", "ПОПЕРЕДЖЕННЯ (WARMING)", "Вмикання охолодження / кулера. Підготовка буферів, прискорення телеметрії.", "#fefce8", "#ca8a04", "#a16207"),
        ("70–85 °C", "АКТИВНИЙ ТРОТЛІНГ (THROTTLED)", "ПІ-регулювання: CPU DVFS (100%→25%), обмеження струму ШІМ, радіо 14 dBm.", "#fff7ed", "#ea580c", "#c2410c"),
        ("85–95 °C", "КРИТИЧНИЙ РЕЖИМ (CRITICAL)", "Limp mode: скидання корисного навантаження, вимкнення підсвітки, мінімум такту.", "#fef2f2", "#dc2626", "#b91c1c"),
        ("> 95 °C", "АВАРІЙНЕ ВИМКНЕННЯ (SHUTDOWN)", "Збереження логу в EEPROM → розмикання eFuse / силове відсікання живлення.", "#450a0a", "#991b1b", "#ffffff"),
    ]

    y_start = 75
    box_h = 58
    gap = 12

    for i, (temp, title, desc, bg_c, stroke_c, text_c) in enumerate(zones):
        curr_y = y_start + i * (box_h + gap)
        frags.append(rect(40, curr_y, 760, box_h, fill=bg_c, stroke=stroke_c, sw=1.8, rx=6))
        
        frags.append(rect(50, curr_y + 8, 110, box_h - 16, fill="#ffffff" if bg_c != "#ffffff" else "#f1f5f9", stroke=stroke_c, sw=1.2, rx=4))
        frags.append(text(105, curr_y + 30, temp, size=13, bold=True, color="#0f172a" if bg_c != "#450a0a" else stroke_c))

        frags.append(text(180, curr_y + 24, title, size=12, bold=True, color=text_c, anchor="start"))
        frags.append(text(180, curr_y + 44, desc, size=10, color=text_c if bg_c == "#450a0a" else "#334155", anchor="start"))

    render(os.path.join(IMG_DIR, "cascade-zones.svg"), w, h, *frags)


def fig_chattering_vs_hysteresis():
    w, h = 840, 480
    frags = []

    frags.append(rect(20, 20, 800, 440, fill="#f8fafc", stroke="#0f172a", sw=2, rx=10))
    frags.append(text(420, 46, "Динаміка термозахисту: релейне деренчання проти гістерезису з ПІ", size=15, bold=True, color="#0f172a"))

    # Верхній графік: Релейне керування без гістерезису
    frags.append(rect(40, 70, 760, 175, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(55, 92, "А. Без гістерезису (Bang-Bang): поріг 75.0 °C викликає високу частоту перемикань (15 Гц)", size=12, bold=True, color="#b91c1c", anchor="start"))

    frags.append(line(70, 215, 770, 215, color="#94a3b8", sw=1))
    frags.append(line(70, 105, 70, 215, color="#94a3b8", sw=1))
    frags.append(text(60, 115, "T", size=11, bold=True, color="#64748b"))
    frags.append(text(765, 230, "t (час)", size=10, color="#64748b"))

    frags.append(line(70, 145, 770, 145, color="#ef4444", sw=1.2, dash="4,4"))
    frags.append(text(135, 140, "Поріг T_trip = 75.0 °C", size=10, bold=True, color="#ef4444"))

    pts_top = [
        (70, 205), (150, 170), (220, 148), (240, 142), (255, 148), (270, 142), (285, 148), (300, 142),
        (315, 148), (330, 142), (345, 148), (360, 142), (375, 148), (390, 142), (405, 148), (420, 142),
        (435, 148), (450, 142), (465, 148), (480, 142), (495, 148), (510, 142), (525, 148), (540, 142),
        (555, 148), (570, 142), (585, 148), (600, 142), (615, 148), (630, 142), (645, 148), (660, 142),
        (675, 148), (690, 142), (705, 148), (720, 142), (735, 148), (750, 142), (765, 148)
    ]
    path_d_top = "M " + " L ".join("%d,%d" % p for p in pts_top)
    frags.append(svg_path(path_d_top, fill="none", stroke="#dc2626", sw=2))

    frags.append(rect(480, 100, 270, 36, fill="#fee2e2", stroke="#ef4444", sw=1, rx=4))
    frags.append(text(615, 115, "Термічне деренчання (Thermal Chattering)", size=10, bold=True, color="#991b1b"))
    frags.append(text(615, 128, "EMI шум на живленні, знос ключів", size=9, color="#7f1d1d"))

    # Нижній графік: Гістерезис + ПІ тротлінг
    frags.append(rect(40, 260, 760, 185, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(55, 282, "Б. Гістерезис (T_on = 75 °C, T_off = 68 °C) + ПІ-регулятор потужності", size=12, bold=True, color="#15803d", anchor="start"))

    frags.append(line(70, 415, 770, 415, color="#94a3b8", sw=1))
    frags.append(line(70, 295, 70, 415, color="#94a3b8", sw=1))
    frags.append(text(60, 305, "T", size=11, bold=True, color="#64748b"))
    frags.append(text(765, 430, "t (час)", size=10, color="#64748b"))

    frags.append(line(70, 330, 770, 330, color="#ef4444", sw=1.2, dash="4,4"))
    frags.append(text(130, 325, "T_trip = 75.0 °C", size=10, bold=True, color="#ef4444"))

    frags.append(line(70, 375, 770, 375, color="#16a34a", sw=1.2, dash="4,4"))
    frags.append(text(135, 370, "T_release = 68.0 °C", size=10, bold=True, color="#16a34a"))

    frags.append(rect(74, 331, 690, 43, fill="#f0fdf4", stroke="none"))
    frags.append(text(650, 355, "Зона гістерезису ΔT = 7 °C", size=10, bold=True, color="#15803d"))

    pts_bot = [
        (70, 405), (140, 375), (200, 335), (250, 328), (300, 338), (350, 345),
        (420, 348), (500, 348), (580, 348), (660, 348), (765, 348)
    ]
    path_d_bot = "M " + " L ".join("%d,%d" % p for p in pts_bot)
    frags.append(svg_path(path_d_bot, fill="none", stroke="#15803d", sw=2.5))

    frags.append(rect(410, 370, 240, 36, fill="#dcfce7", stroke="#22c55e", sw=1, rx=4))
    frags.append(text(530, 385, "Плавна стабілізація на T_target = 72 °C", size=10, bold=True, color="#166534"))
    frags.append(text(530, 398, "Коефіцієнт K_throttle = 64%, без стрибків", size=9, color="#14532d"))

    render(os.path.join(IMG_DIR, "chattering-vs-hysteresis.svg"), w, h, *frags)


def fig_thermal_fsm():
    w, h = 840, 490
    frags = []

    frags.append(rect(20, 20, 800, 450, fill="#f8fafc", stroke="#0f172a", sw=2, rx=10))
    frags.append(text(420, 48, "Скінченний автомат термоконтролера (Thermal FSM)", size=16, bold=True, color="#0f172a"))

    # Стан 1: NORMAL
    frags.append(rect(45, 175, 125, 80, fill="#dcfce7", stroke="#16a34a", sw=2, rx=8))
    frags.append(text(107, 205, "NORMAL", size=13, bold=True, color="#15803d"))
    frags.append(text(107, 225, "100% потужність", size=10, color="#166534"))
    frags.append(text(107, 242, "Всі системи штатно", size=9, color="#14532d"))

    # Стан 2: WARMING
    frags.append(rect(205, 175, 125, 80, fill="#fef9c3", stroke="#ca8a04", sw=2, rx=8))
    frags.append(text(267, 205, "WARMING", size=13, bold=True, color="#a16207"))
    frags.append(text(267, 225, "Кулер / охолодження", size=10, color="#854d0e"))
    frags.append(text(267, 242, "Телеметрія 50 мс", size=9, color="#713f12"))

    # Стан 3: THROTTLED (PI loop)
    frags.append(rect(365, 160, 145, 110, fill="#ffedd5", stroke="#ea580c", sw=2, rx=8))
    frags.append(text(437, 188, "THROTTLED", size=13, bold=True, color="#c2410c"))
    frags.append(rect(375, 200, 125, 60, fill="#ffffff", stroke="#fdba74", sw=1, rx=4))
    frags.append(text(437, 218, "ПІ-контур:", size=10, bold=True, color="#9a3412"))
    frags.append(text(437, 233, "CPU DVFS / ШІМ", size=9, color="#7c2d12"))
    frags.append(text(437, 248, "K_throttle: 25..95%", size=9, bold=True, color="#c2410c"))

    # Стан 4: CRITICAL
    frags.append(rect(545, 175, 125, 80, fill="#fee2e2", stroke="#dc2626", sw=2, rx=8))
    frags.append(text(607, 205, "CRITICAL", size=13, bold=True, color="#b91c1c"))
    frags.append(text(607, 225, "Limp Mode", size=10, bold=True, color="#991b1b"))
    frags.append(text(607, 242, "Payload вимкнено", size=9, color="#7f1d1d"))

    # Стан 5: SHUTDOWN
    frags.append(rect(695, 175, 110, 80, fill="#450a0a", stroke="#991b1b", sw=2, rx=8))
    frags.append(text(750, 205, "SHUTDOWN", size=12, bold=True, color="#ffffff"))
    frags.append(text(750, 225, "EEPROM дамп", size=9, color="#fecaca"))
    frags.append(text(750, 242, "eFuse OFF / Latch", size=9, color="#fca5a5"))

    # Прямі переходи вперед (зліва направо)
    frags.append(arrow(170, 200, 205, 200, color="#ca8a04", sw=2))
    frags.append(text(187, 192, "T > T_w", size=9, bold=True, color="#a16207"))

    frags.append(arrow(330, 200, 365, 200, color="#ea580c", sw=2))
    frags.append(text(347, 192, "T > T_t", size=9, bold=True, color="#c2410c"))

    frags.append(arrow(510, 200, 545, 200, color="#dc2626", sw=2))
    frags.append(text(527, 192, "T > T_c", size=9, bold=True, color="#b91c1c"))

    frags.append(arrow(670, 200, 695, 200, color="#7f1d1d", sw=2))
    frags.append(text(682, 192, "T > T_s", size=9, bold=True, color="#7f1d1d"))

    # Зворотні переходи назад з гістерезисом і dwell таймером (дуги знизу)
    # CRITICAL -> THROTTLED
    frags.append(arrow(570, 255, 480, 270, color="#ea580c", sw=1.8))
    frags.append(text(540, 285, "T < T_c − ΔT  &&  t >= t_dwell", size=9, color="#9a3412"))

    # THROTTLED -> WARMING
    frags.append(arrow(390, 270, 300, 255, color="#ca8a04", sw=1.8))
    frags.append(text(340, 305, "T < T_t − ΔT  &&  t >= t_dwell", size=9, color="#854d0e"))

    # WARMING -> NORMAL
    frags.append(arrow(230, 255, 140, 255, color="#16a34a", sw=1.8))
    frags.append(text(180, 325, "T < T_w − ΔT  &&  t >= t_dwell", size=9, color="#15803d"))

    # Аварійний тригер швидкого зростання температури (Thermal Shock Fast-Path)
    frags.append(rect(180, 85, 480, 45, fill="#ffffff", stroke="#b91c1c", sw=1.5, rx=6))
    frags.append(text(420, 103, "Захист від теплового удару (Thermal Shock Rate-of-Rise)", size=11, bold=True, color="#b91c1c"))
    frags.append(text(420, 118, "Якщо dT/dt > 5 °C/с  →  Миттєвий перехід у CRITICAL або SHUTDOWN", size=10, color="#7f1d1d"))

    frags.append(arrow(420, 130, 607, 175, color="#b91c1c", sw=2))

    # Пояснення умов унізу
    frags.append(rect(45, 365, 760, 85, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(425, 388, "Параметри переходів автомата:", size=11, bold=True, color="#0f172a"))
    frags.append(text(425, 408, "• T_w = 55 °C, T_t = 70 °C, T_c = 85 °C, T_s = 95 °C | Гістерезис ΔT = 5..8 °C", size=10, color="#334155"))
    frags.append(text(425, 428, "• t_dwell ≥ 5.0 с (таймер очікування для розсіювання теплової маси перед підвищенням потужності)", size=10, color="#334155"))

    render(os.path.join(IMG_DIR, "thermal-fsm.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_thermal_telemetry_nodes()
    fig_cascade_zones()
    fig_chattering_vs_hysteresis()
    fig_thermal_fsm()
    print("All figures generated successfully.")
