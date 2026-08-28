# -*- coding: utf-8 -*-
"""figs.py — генератор ілюстрацій для теми batareia-u-vyrobi (sys-notary).
Генерує 4 SVG-схеми в ./img/ за допомогою спільного svgkit.
"""
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(SCRIPT_DIR, "img"), exist_ok=True)


# ── Фігура 1: Послідовність випробувань UN 38.3 ──────────────────────────────
def fig_un383_test_sequence():
    W, H = 1000, 580
    P = []
    P.append(text(W / 2, 28, "Послідовність випробувань літієвих джерел за стандартом UN 38.3", size=16, bold=True))

    # Верхній контур: Послідовний ланцюг T.1 -> T.5 на тих самих зразках
    P.append(rect(30, 55, 940, 255, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(500, 78, "ПОСЛІДОВНИЙ ЛАНЦЮГ КЛІМАТИЧНИХ І МЕХАНІЧНИХ НАВАНТАЖЕНЬ (ТІ САМІ ЗРАЗКИ)", size=12, bold=True, color="#1e293b"))

    tests_seq = [
        ("T.1 Висота / вакуум", "P ≤ 11.6 кПа\n(15 240 м)\n6 год, 20 °C\nГерметичність", "#e0e7ff", "#4338ca"),
        ("T.2 Термоцикли", "+72 °C ↔ -40 °C\n10 циклів (по 6 год)\nПерехід ≤ 30 хв\nТермовтома", "#fef3c7", "#b45309"),
        ("T.3 Вібрація", "7–200–7 Гц\n15 хв/цикл, 12 разів\n3 осі (9 год), 8 gn\nРезонанс швів", "#ecfdf5", "#047857"),
        ("T.4 Механічний удар", "150 gn / 6 мс\n3 удари ± по 3 осях\n(18 ударів)\nСтійкість шасі", "#fdf2f8", "#be185d"),
        ("T.5 Зовнішнє КЗ", "57 ± 4 °C\nR < 0.1 Ом\nT_case ≤ 170 °C\nВідмова без вогню", "#fee2e2", "#b91c1c")
    ]

    bw = 165
    gap = 22
    x_start = 55

    for i, (title, desc, fill_c, strk_c) in enumerate(tests_seq):
        bx = x_start + i * (bw + gap)
        by = 95
        P.append(rect(bx, by, bw, 125, fill=fill_c, stroke=strk_c, sw=1.8, rx=6))
        P.append(text(bx + bw / 2, by + 22, title, size=11.5, bold=True, color=strk_c))
        P.append(mtext(bx + bw / 2, by + 46, desc, size=10, color=INK, lh=1.25))

        if i < len(tests_seq) - 1:
            P.append(arrow(bx + bw + 2, by + 62, bx + bw + gap - 4, by + 62, color="#64748b", sw=2))

    # Спільний вердикт ланцюга T.1-T.5
    P.append(rect(55, 235, 890, 60, fill="#ffffff", stroke="#059669", sw=1.4, rx=6))
    verdict_seq = "Критерії проходження T.1–T.5: відсутність втрати маси (< 0.1% для великих, < 0.2% для малих), протікань,\nрозгерметизації, вибуху чи займання; збереження залишкової напруги розімкненого кола OCV ≥ 90%."
    P.append(mtext(500, 258, verdict_seq, size=10, color=INK, lh=1.3))

    # Нижні паралельні тести руйнівного контролю: T.6, T.7, T.8
    P.append(rect(30, 325, 940, 235, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(500, 348, "ОКРЕМІ ВИПРОБУВАННЯ РУЙНІВНОГО ТА ЕЛЕКТРИЧНОГО КОНТРОЛЮ (ОКРЕМІ ВИБІРКИ ЗРАЗКІВ)", size=12, bold=True, color="#1e293b"))

    tests_par = [
        ("T.6 Роздавлювання / Удар", "Циліндричні > 18 мм:\nтягар 9.1 кг з висоти 61 см\nПризматичні / пакетні:\nпрес 13 кН (швидкість 1.5 см/с)\nдо ΔU = 100 мВ або 50% товщини\nВимога: T ≤ 170 °C, без вогню", "#fef3c7", "#d97706"),
        ("T.7 Перезаряд пакета", "Тільки для акумуляторів із BMS\nСтрум: 2 × I_charge_max\nНапруга: min(2 × U_max, 22 В)\nТривалість: 24 год заряду\nСпостереження: 7 діб\nВимога: без розриву та пожежі", "#ede9fe", "#7c3aed"),
        ("T.8 Форсований розряд", "Для елементів у послідовних збірках\nЗворотна полярність від джерела 12 В\nСтрум: I_discharge_max\nТривалість: t = Q_rated / I_test\nСпостереження: 7 діб\nВимога: без розриву та займання", "#ffe4e6", "#e11d48")
    ]

    pw = 285
    pgap = 30
    px_start = 55

    for i, (title, desc, fill_c, strk_c) in enumerate(tests_par):
        bx = px_start + i * (pw + pgap)
        by = 365
        P.append(rect(bx, by, pw, 175, fill=fill_c, stroke=strk_c, sw=1.8, rx=6))
        P.append(text(bx + pw / 2, by + 22, title, size=12, bold=True, color=strk_c))
        P.append(mtext(bx + pw / 2, by + 48, desc, size=10, color=INK, lh=1.3))

    render(os.path.join(SCRIPT_DIR, "img", "un383-test-sequence.svg"), W, H, *P)


# ── Фігура 2: Дерево рішень IATA DGR ─────────────────────────────────────────
def fig_iata_classification_tree():
    W, H = 1000, 570
    P = []
    P.append(text(W / 2, 28, "Дерево рішень логістичної класифікації літієвих батарей за IATA DGR", size=16, bold=True))

    # Корінь: Вхідна вибірка
    b_root, _, _ = textbox(500, 68, "Літієве джерело живлення: вибір хімії та конфігурації", size=12, bold=True, fill="#e2e8f0", stroke="#334155", sw=1.8, min_w=460)
    P.append(b_root)

    # Рівень 1: Хімія
    b_ion, _, _ = textbox(270, 130, "Літій-іонні (вторинні / перезарядні)\nТелефони, дрони, інструмент, АКБ", size=11, bold=True, fill="#e0f2fe", stroke="#0284c7", sw=1.6, min_w=340)
    b_met, _, _ = textbox(730, 130, "Літій-металеві (первинні / одноразові)\nCR2032, Li-SOCl2, лічильники, трекери", size=11, bold=True, fill="#fef3c7", stroke="#d97706", sw=1.6, min_w=340)
    P.append(b_ion + b_met)

    P.append(arrow(400, 85, 270, 110, color=LINE, sw=1.5))
    P.append(arrow(600, 85, 730, 110, color=LINE, sw=1.5))

    # Рівень 2: Конфігурація упаковки (3 гілки для Li-ion)
    b_c1, _, _ = textbox(110, 215, "Окремо батареї\n(UN 3480 / PI 965)\nТільки вантажний борт (CAO)\nSoC ≤ 30% обов'язково", size=9.5, fill="#fee2e2", stroke="#dc2626", sw=1.5, min_w=190)
    b_c2, _, _ = textbox(280, 215, "Разом з обладнанням\n(UN 3481 / PI 966)\nБатарея у тій самій коробці\nпоруч із приладом", size=9.5, fill="#f1f5f9", stroke="#475569", sw=1.5, min_w=140)
    b_c3, _, _ = textbox(440, 215, "Вмонтовані в прилад\n(UN 3481 / PI 967)\nБатарея встановлена всередині\nкорпусу пристрою", size=9.5, fill="#f0fdf4", stroke="#16a34a", sw=1.5, min_w=160)
    P.append(b_c1 + b_c2 + b_c3)

    P.append(arrow(220, 155, 110, 190, color=LINE, sw=1.2))
    P.append(arrow(270, 155, 280, 190, color=LINE, sw=1.2))
    P.append(arrow(320, 155, 440, 190, color=LINE, sw=1.2))

    # Рівень 2: Конфігурація для Li-metal (3 гілки)
    b_m1, _, _ = textbox(590, 215, "Окремо елементи\n(UN 3090 / PI 968)\nТільки вантажний борт (CAO)\nЗаборонено пасажирськими", size=9.5, fill="#fee2e2", stroke="#dc2626", sw=1.5, min_w=130)
    b_m2, _, _ = textbox(730, 215, "Разом з обладнанням\n(UN 3091 / PI 969)\nКомплект у коробці\nпоруч із приладом", size=9.5, fill="#f1f5f9", stroke="#475569", sw=1.5, min_w=135)
    b_m3, _, _ = textbox(880, 215, "Вмонтовані в прилад\n(UN 3091 / PI 970)\nВпаяні/вставлені в холдер\nусередині приладу", size=9.5, fill="#f0fdf4", stroke="#16a34a", sw=1.5, min_w=145)
    P.append(b_m1 + b_m2 + b_m3)

    P.append(arrow(680, 155, 590, 190, color=LINE, sw=1.2))
    P.append(arrow(730, 155, 730, 190, color=LINE, sw=1.2))
    P.append(arrow(780, 155, 880, 190, color=LINE, sw=1.2))

    # Рівень 3: Пороги енергії та Секції (Section IA, IB, II)
    P.append(rect(40, 290, 920, 260, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    P.append(text(500, 312, "КРИТЕРІЇ ПОДІЛУ НА СЕКЦІЇ ТА РЕЖИМИ РЕГУЛЮВАННЯ (PACKING SECTIONS)", size=12, bold=True, color="#0f172a"))

    sec_boxes = [
        ("СЕКЦІЯ IA (Повне регулювання Class 9)", "Поріг: Комірка > 20 Вт·год або АКБ > 100 Вт·год\n(для Li-metal: комірка > 1 г або АКБ > 2 г літію)\n\n• Сертифікована UN-тара (UN Specification 4G, PG II)\n• Декларація небезпечного вантажу (DGD / Shipper's Dec)\n• Знак небезпеки Class 9A + наліпка CAO (для UN 3480/3090)\n• Сертифікований персонал з підготовкою DGR", "#fef2f2", "#b91c1c"),
        ("СЕКЦІЯ IB (Малі елементи у великій кількості)", "Поріг: Комірка ≤ 20 Вт·год, АКБ ≤ 100 Вт·год\n(але вага пакунка або кількість перевищує Section II)\n\n• Жорстка міцна тара (випробування падінням 1.2 м)\n• Декларація небезпечного вантажу (DGD)\n• Маркування: Знак Lithium Battery Mark + Class 9A Label\n• Обмеження ваги: макс. 10 кг нетто на вантажний борт", "#fffbeb", "#b45309"),
        ("СЕКЦІЯ II (Виняток / Спрощений режим)", "Поріг: Комірка ≤ 20 Вт·год, АКБ ≤ 100 Вт·год\n(PI 966/967/969/970, обмежена кількість)\n\n• Без декларації DGD, без UN-специфікації тари\n• Знак Lithium Battery Mark (якщо > 2 приладів у пакунку)\n• Захист клем від КЗ, фіксація всередині корпусу\n• Випробування тари на падіння з висоти 1.2 м", "#f0fdf4", "#15803d")
    ]

    sw_w = 285
    sw_gap = 20
    sw_x = 55

    for i, (title, desc, fill_c, strk_c) in enumerate(sec_boxes):
        bx = sw_x + i * (sw_w + sw_gap)
        by = 330
        P.append(rect(bx, by, sw_w, 205, fill=fill_c, stroke=strk_c, sw=1.6, rx=6))
        P.append(text(bx + sw_w / 2, by + 20, title, size=11, bold=True, color=strk_c))
        P.append(mtext(bx + 14, by + 44, desc, size=9.5, color=INK, anchor="start", lh=1.26))

    render(os.path.join(SCRIPT_DIR, "img", "iata-classification-tree.svg"), W, H, *P)


# ── Фігура 3: Апаратна схема Ship Mode ──────────────────────────────────────
def fig_transport_ship_mode_circuit():
    W, H = 1000, 480
    P = []
    P.append(text(W / 2, 28, "Апаратна та програмна архітектура транспортного режиму (Ship Mode)", size=16, bold=True))

    # Ліва частина: Батарейний блок і багаторівневий захист
    b_pack, _, _ = textbox(130, 110, "Li-Ion Акумулятор\n3.7 В (1S / 3S)\nSoC ≤ 30% при відвантаженні", size=11, bold=True, fill="#e0f2fe", stroke="#0284c7", sw=1.8, min_w=180)
    P.append(b_pack)

    b_bms, _, _ = textbox(130, 230, "Первинний захист BMS IC\n(BQ29700 / DW01A)\nКонтроль OVP / UVP / OCP\nКлючі Dual N-MOSFET", size=10.5, fill="#f8fafc", stroke="#475569", sw=1.5, min_w=180)
    P.append(b_bms)

    b_scp, _, _ = textbox(130, 350, "Вторинний захист (SCP)\nТриполюсний керований\nхімічний плавкий запобіжник\n(самознищення при відмові)", size=10.5, fill="#fee2e2", stroke="#dc2626", sw=1.5, min_w=180)
    P.append(b_scp)

    P.append(arrow(130, 145, 130, 185, color=LINE, sw=1.5))
    P.append(arrow(130, 275, 130, 310, color=LINE, sw=1.5))

    # Центральна частина: PMIC / Ship Mode Power Gate Controller
    P.append(rect(300, 70, 370, 370, fill="#f8fafc", stroke="#4338ca", sw=2, rx=8))
    P.append(text(485, 96, "КОНТРОЛЕР ЖИВЛЕННЯ ТА SHIP MODE (PMIC / GATE)", size=12, bold=True, color="#4338ca"))

    b_gate, _, _ = textbox(485, 155, "Силовий ключ розриву навантаження (Load Switch)\nP-MOSFET / E-Fuse з витоком I_leak < 100 нА", size=10, fill="#e0e7ff", stroke="#6366f1", min_w=330)
    b_latch, _, _ = textbox(485, 245, "Апаратний тригер стану (Ship Mode Latch)\nБлокує подачу живлення на шину V_SYS\nСпоживання у сні: I_q ≤ 0.5 мкА (проти 50 мкА штатно)", size=10, fill="#ffffff", stroke="#475569", min_w=330)
    b_wake, _, _ = textbox(485, 345, "Логіка розблокування (Wake-up Engine)\n• Детекція підключення зарядного пристрою (V_BUS)\n• Апаратний дебаунс кнопки: утримання > 3–5 секунд", size=10, fill="#fef3c7", stroke="#d97706", min_w=330)
    P.append(b_gate + b_latch + b_wake)

    # Зв'язки між блоками
    P.append(arrow(220, 230, 300, 155, color=LINE, sw=1.8))
    P.append(arrow(485, 285, 485, 310, color="#64748b", sw=1.5))

    # Права частина: Системне навантаження та MCU
    b_sys, _, _ = textbox(830, 155, "Системна шина V_SYS\nDC-DC перетворювачі\nПовністю знеструмлені (0 В)\nВиключено випадковий запуск", size=10.5, fill="#f1f5f9", stroke="#64748b", sw=1.5, min_w=220)
    b_mcu, _, _ = textbox(830, 285, "Мікроконтролер (MCU)\nПрошивка контролює перехід:\n1. Перевірка SoC ≤ 30%\n2. Запис прапорця в EEPROM\n3. Команда I2C: ENTER_SHIP_MODE", size=10, fill="#f0fdf4", stroke="#16a34a", sw=1.5, min_w=220)
    P.append(b_sys + b_mcu)

    P.append(arrow(650, 155, 720, 155, color=LINE, sw=1.8))
    P.append(arrow(830, 230, 830, 215, color=MUTED, sw=1.2))
    P.append(arrow(720, 320, 650, 260, color="#16a34a", sw=1.5)) # MCU commands to PMIC

    # Нижній банер результату
    b_res, _, _ = textbox(500, 460, "Захист від глибокого саморозряду (U < 2.0 В) протягом 12 місяців складування та захист від вібраційного ввімкнення під час руху", size=10, bold=True, fill="#ecfdf5", stroke="#059669", min_w=900)
    P.append(b_res)

    render(os.path.join(SCRIPT_DIR, "img", "transport-ship-mode-circuit.svg"), W, H, *P)


# ── Фігура 4: Маркування та знаки небезпеки ──────────────────────────────────
def fig_hazard_labels_and_marks():
    W, H = 1000, 450
    P = []
    P.append(text(W / 2, 28, "Анатомія транспортного маркування та знаків небезпеки літієвих вантажів", size=16, bold=True))

    # Знак 1: Lithium Battery Mark (Секція II та IB)
    P.append(rect(50, 60, 280, 350, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(190, 85, "Знак літієвої батареї", size=13, bold=True, color="#1e293b"))
    P.append(text(190, 102, "Lithium Battery Mark (100×100 мм)", size=10, color=MUTED))

    # Рамка зі штрихами (червона)
    P.append(rect(80, 120, 220, 190, fill="#ffffff", stroke="#dc2626", sw=4, rx=4))
    # Піктограма батареї та вогню
    P.append(rect(110, 145, 65, 90, fill="#f1f5f9", stroke="#0f172a", sw=2, rx=3))
    P.append(rect(125, 135, 35, 10, fill="#0f172a", stroke="#0f172a", sw=1))
    P.append(text(142, 195, "Li-ion", size=12, bold=True, color="#0f172a"))

    # Вогонь праворуч
    P.append(text(220, 195, "🔥", size=32))

    # Текстові обов'язкові поля
    P.append(text(190, 260, "UN 3481", size=14, bold=True, color="#0f172a"))
    P.append(text(190, 285, "+380 44 123 4567", size=10.5, bold=True, color="#0f172a"))

    P.append(mtext(190, 340, "Застосування: PI 966/967/969/970 (Sec II/IB)\nЧервона штрихована облямівка (min 5 мм)\nОбов'язковий номер UN та телефон техпідтримки", size=9.5, color=INK, lh=1.25))

    # Знак 2: Class 9A Miscellaneous Hazard Label (Секція IA та IB)
    P.append(rect(360, 60, 280, 350, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(500, 85, "Знак небезпеки Class 9A", size=13, bold=True, color="#1e293b"))
    P.append(text(500, 102, "Class 9 Lithium Battery (ромб 100×100 мм)", size=10, color=MUTED))

    # Ромб знака 9A
    P.append('<polygon points="500,125 590,215 500,305 410,215" fill="#ffffff" stroke="#0f172a" stroke-width="2.5"/>')
    # Смуги у верхній половині
    P.append('<line x1="450" y1="175" x2="450" y2="215" stroke="#0f172a" stroke-width="3"/>')
    P.append('<line x1="470" y1="155" x2="470" y2="215" stroke="#0f172a" stroke-width="3"/>')
    P.append('<line x1="490" y1="135" x2="490" y2="215" stroke="#0f172a" stroke-width="3"/>')
    P.append('<line x1="510" y1="135" x2="510" y2="215" stroke="#0f172a" stroke-width="3"/>')
    P.append('<line x1="530" y1="155" x2="530" y2="215" stroke="#0f172a" stroke-width="3"/>')
    P.append('<line x1="550" y1="175" x2="550" y2="215" stroke="#0f172a" stroke-width="3"/>')
    # Символ батареї та вогню в нижній половині
    P.append(text(500, 255, "🔋🔥", size=16))
    P.append(text(500, 290, "9", size=16, bold=True, color="#0f172a"))

    P.append(mtext(500, 340, "Застосування: Секція IA та Секція IB\n7 чорних вертикальних смуг у верхній частині\nПіктограма палаючої батареї та підкреслена цифра 9", size=9.5, color=INK, lh=1.25))

    # Знак 3: Cargo Aircraft Only (CAO)
    P.append(rect(670, 60, 280, 350, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(810, 85, "Тільки вантажним бортом", size=13, bold=True, color="#1e293b"))
    P.append(text(810, 102, "Cargo Aircraft Only (120×110 мм)", size=10, color=MUTED))

    # Помаранчевий прямокутник
    P.append(rect(705, 125, 210, 175, fill="#ea580c", stroke="#0f172a", sw=2, rx=4))
    P.append(text(810, 160, "✈️ ✋", size=26))
    P.append(text(810, 205, "CARGO AIRCRAFT", size=12, bold=True, color="#ffffff"))
    P.append(text(810, 225, "ONLY", size=14, bold=True, color="#ffffff"))
    P.append(text(810, 260, "FORBIDDEN IN PASSENGER AIRCRAFT", size=9.5, bold=True, color="#ffffff"))

    P.append(mtext(810, 340, "Застосування: UN 3480 та UN 3090 (окремі АКБ)\nОбов'язкова наклейка на пакунку\nСувора заборона завантаження на пасажирські рейси", size=9.5, color=INK, lh=1.25))

    render(os.path.join(SCRIPT_DIR, "img", "hazard-labels-and-marks.svg"), W, H, *P)


if __name__ == "__main__":
    fig_un383_test_sequence()
    fig_iata_classification_tree()
    fig_transport_ship_mode_circuit()
    fig_hazard_labels_and_marks()
    print("OK: 4 figures generated in img/")
