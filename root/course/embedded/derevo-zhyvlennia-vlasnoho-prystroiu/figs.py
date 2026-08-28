# -*- coding: utf-8 -*-
"""Фігури для статті derevo-zhyvlennia-vlasnoho-prystroiu («Дерево живлення власного пристрою»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. power-tree-topology: ієрархія перетворення та рейок ───────────────────
def fig_power_tree_topology():
    W, H = 840, 520
    p = []

    # Тло та секції
    p.append(rect(20, 20, 800, 480, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Стовпчик 1: Вхідні джерела
    p.append(rect(35, 35, 140, 450, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(105, 60, "Вхідні джерела", size=13, color=INK, bold=True))

    b1, _, _ = textbox(105, 110, "USB Type-C\n5.0 В (до 3 А)", size=11, fill="#eef2f6", stroke="#94a3b8", sw=1.2)
    b2, _, _ = textbox(105, 200, "Li-Po / Li-ion\n3.0…4.2 В (1S)", size=11, fill="#eef2f6", stroke="#94a3b8", sw=1.2)
    b3, _, _ = textbox(105, 290, "Шина DC\n9…28 В (пром)", size=11, fill="#eef2f6", stroke="#94a3b8", sw=1.2)
    p.extend([b1, b2, b3])

    # Стовпчик 2: Вхідний захист
    p.append(rect(195, 35, 140, 450, fill="#fdf2f2", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(265, 60, "Вхідний захист", size=13, color=POS, bold=True))

    b_tvs, _, _ = textbox(265, 110, "TVS-супресор\n(ESD + сплески)", size=11, fill="#ffffff", stroke=POS, sw=1.2)
    b_rev, _, _ = textbox(265, 200, "P-MOSFET\n(переполюсовка)", size=11, fill="#ffffff", stroke=POS, sw=1.2)
    b_ovp, _, _ = textbox(265, 290, "OVP ключ\n(перенапруга)", size=11, fill="#ffffff", stroke=POS, sw=1.2)
    p.extend([b_tvs, b_rev, b_ovp])

    # Стрілки від джерел до захисту
    p.append(arrow(155, 110, 195, 110, color=LINE, sw=1.4))
    p.append(arrow(155, 200, 195, 200, color=LINE, sw=1.4))
    p.append(arrow(155, 290, 195, 290, color=LINE, sw=1.4))

    # Стовпчик 3: Перший ступінь (Buck)
    p.append(rect(355, 35, 140, 450, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(425, 60, "I ступінь (DC-DC)", size=13, color=FIELD, bold=True))

    b_buck5, _, _ = textbox(425, 150, "Step-Down Buck\n5.0 В (ККД 92%)\nшинне живлення", size=11, fill="#ffffff", stroke=FIELD, sw=1.3)
    b_buck3, _, _ = textbox(425, 320, "Step-Down Buck\n3.3 В (ККД 90%)\nголовна шина", size=11, fill="#ffffff", stroke=FIELD, sw=1.3)
    p.extend([b_buck5, b_buck3])

    # З'єднання від захисту до Buck
    p.append(arrow(315, 200, 355, 150, color=LINE, sw=1.4))
    p.append(arrow(315, 290, 355, 320, color=LINE, sw=1.4))

    # Стовпчик 4: Другий ступінь (LDO / Політика рейок)
    p.append(rect(515, 35, 140, 450, fill="#f5f3ff", stroke="#c4b5fd", sw=1.2, rx=6))
    p.append(text(585, 60, "II ступінь (Чистота)", size=13, color="#6b21a8", bold=True))

    b_ldo_a, _, _ = textbox(585, 110, "LDO (High PSRR)\n3.3 В AVDD\n(шум < 10 мкВ)", size=11, fill="#ffffff", stroke="#8b5cf6", sw=1.3)
    b_vref, _, _ = textbox(585, 200, "Опора VREF\n2.500 В (дрейф\n< 5 ppm/°C)", size=11, fill="#ffffff", stroke="#8b5cf6", sw=1.3)
    b_core, _, _ = textbox(585, 300, "Buck / LDO\n1.2 В / 1.8 В\nVCORE (ядро)", size=11, fill="#ffffff", stroke="#8b5cf6", sw=1.3)
    b_sw, _, _ = textbox(585, 410, "Load Switch\n(секвенсер 3.3 В\nпериферії)", size=11, fill="#ffffff", stroke="#8b5cf6", sw=1.3)
    p.extend([b_ldo_a, b_vref, b_core, b_sw])

    # З'єднання з I ступеня на II ступінь
    p.append(arrow(475, 150, 515, 110, color=LINE, sw=1.4))
    p.append(arrow(475, 320, 515, 200, color=LINE, sw=1.4))
    p.append(arrow(475, 320, 515, 300, color=LINE, sw=1.4))
    p.append(arrow(475, 320, 515, 410, color=LINE, sw=1.4))

    # Стовпчик 5: Навантаження (Кінцеві споживачі)
    p.append(rect(675, 35, 130, 450, fill="#faf5ff", stroke="#e9d5ff", sw=1.2, rx=6))
    p.append(text(740, 60, "Споживачі", size=13, color=INK, bold=True))

    b_rf, _, _ = textbox(740, 110, "RF / Радіо\nADC / Сенсори", size=11, fill="#ffffff", stroke="#a855f7", sw=1.2)
    b_adc_ref, _, _ = textbox(740, 200, "Прецизійний\nАЦП / ЦАП", size=11, fill="#ffffff", stroke="#a855f7", sw=1.2)
    b_mcu, _, _ = textbox(740, 300, "MCU Core\nRAM / DSP", size=11, fill="#ffffff", stroke="#a855f7", sw=1.2)
    b_ext, _, _ = textbox(740, 410, "Дисплей / SD\nДатчики I2C/SPI", size=11, fill="#ffffff", stroke="#a855f7", sw=1.2)
    p.extend([b_rf, b_adc_ref, b_mcu, b_ext])

    # З'єднання з II ступеня на споживачів
    p.append(arrow(635, 110, 675, 110, color=LINE, sw=1.4))
    p.append(arrow(635, 200, 675, 200, color=LINE, sw=1.4))
    p.append(arrow(635, 300, 675, 300, color=LINE, sw=1.4))
    p.append(arrow(635, 410, 675, 410, color=LINE, sw=1.4))

    render(os.path.join(OUT, "power-tree-topology.svg"), W, H, *p,
           title="Ієрархічна структура дерева живлення вбудованого пристрою")


# ── 2. rail-domains-isolation: розділення цифрової, аналогової та силової зон ─
def fig_rail_domains_isolation():
    W, H = 840, 490
    p = []

    p.append(rect(20, 20, 800, 450, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Зона 1: Силова (PVDD / PGND) 35..265
    p.append(rect(35, 45, 230, 290, fill="#fff1f2", stroke="#f43f5e", sw=1.5, rx=6))
    p.append(text(150, 75, "Силовий домен (PVDD)", size=13, color="#be123c", bold=True))
    b_p1, _, _ = textbox(150, 130, "Мотори, реле, MOSFET\nСтруми: 1…10 А\nВисокі сплески di/dt", size=11, fill="#ffffff", stroke="#f43f5e", sw=1.2)
    b_pgnd, _, _ = textbox(150, 230, "Силова земля PGND\nШирокі полігони\nШум комутації: 100+ мВ", size=11, fill="#ffffff", stroke="#f43f5e", sw=1.2)
    p.extend([b_p1, b_pgnd])

    # Зона 2: Цифрова (DVDD / DGND) 285..535
    p.append(rect(285, 45, 250, 290, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    p.append(text(410, 75, "Цифровий домен (DVDD)", size=13, color="#1d4ed8", bold=True))
    b_d1, _, _ = textbox(410, 130, "MCU, Flash, RAM, шини\nРейки: 3.3 В, 1.8 В, 1.2 В\nШвидкі фронти 1…3 нс", size=11, fill="#ffffff", stroke="#3b82f6", sw=1.2)
    b_dgnd, _, _ = textbox(410, 230, "Цифрова земля DGND\nСуцільний шар плати L2\nПовернення ВЧ-струмів", size=11, fill="#ffffff", stroke="#3b82f6", sw=1.2)
    p.extend([b_d1, b_dgnd])

    # Зона 3: Аналогова (AVDD / AGND) 555..785
    p.append(rect(555, 45, 230, 290, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    p.append(text(670, 75, "Аналоговий домен (AVDD)", size=13, color="#15803d", bold=True))
    b_a1, _, _ = textbox(670, 115, "АЦП, ОП, VREF, PLL\nЧисте живлення від LDO\nЧутливість: мкВ", size=10, fill="#ffffff", stroke="#22c55e", sw=1.2)
    b_fb, _, _ = textbox(670, 180, "Фільтр: Ferrite Bead\n+ 10 мкФ // 0.1 мкФ", size=9, fill="#fef9c3", stroke="#ca8a04", sw=1.0)
    b_agnd, _, _ = textbox(670, 250, "Аналогова земля AGND\nОкремий острів без\nчужих зворотних струмів", size=10, fill="#ffffff", stroke="#22c55e", sw=1.2)
    p.extend([b_a1, b_fb, b_agnd])

    # Лінії заземлення вниз до зірки
    p.append(line(150, 280, 150, 365, color=LINE, sw=1.5))
    p.append(line(410, 280, 410, 365, color=LINE, sw=1.5))
    p.append(line(670, 280, 670, 365, color=LINE, sw=1.5))

    p.append(line(150, 365, 670, 365, color=LINE, sw=2.0))
    b_star, _, _ = textbox(410, 415, "Єдина точка з'єднання (Star Ground / місток 0 Ом біля джерела живлення)", size=11, fill="#ffffff", stroke=LINE, bold=True)
    p.append(b_star)

    render(os.path.join(OUT, "rail-domains-isolation.svg"), W, H, *p,
           title="Розділення та ізоляція силового, цифрового й аналогового доменів живлення")


# ── 3. phantom-powering-hazard: паразитне живлення через ESD-діоди ────────────
def fig_phantom_powering_hazard():
    W, H = 820, 460
    p = []

    p.append(rect(20, 20, 780, 420, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Лівий блок: Зовнішній сенсор (живлення є, 3.3 В)
    p.append(rect(40, 45, 210, 290, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    p.append(text(145, 75, "Зовнішній сенсор", size=13, color="#15803d", bold=True))
    p.append(text(145, 95, "(УВІМКНЕНО: VCC = 3.3 В)", size=11, color="#15803d"))

    b_tx, _, _ = textbox(145, 170, "Вихідна лінія (TX / SDA)\nРівень логічної «1»\nV_out = 3.30 В", size=11, fill="#ffffff", stroke="#22c55e", sw=1.2)
    p.append(b_tx)

    # Правий блок: Мікроконтролер (живлення ВИМКНЕНО, VDD = 0 В)
    p.append(rect(450, 45, 330, 290, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    p.append(text(615, 75, "Мікроконтролер (MCU)", size=13, color="#b91c1c", bold=True))
    p.append(text(615, 95, "(ГОЛОВНА РЕЙКА VDD = 0 В)", size=11, color="#b91c1c", bold=True))

    # Схема вхідного піна MCU з ESD-діодами
    p.append(rect(470, 115, 290, 205, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(615, 133, "Вхідний буфер GPIO", size=11, color=INK, bold=True))

    # Шина VDD MCU
    p.append(line(490, 155, 740, 155, color=POS, sw=2.0))
    p.append(text(730, 147, "Внутрішня шина VDD", size=10, color=POS, anchor="end", bold=True))

    # Вхідний пін
    p.append(line(450, 220, 530, 220, color=LINE, sw=1.8))
    p.append(circle(530, 220, 3, fill=LINE, stroke=LINE))
    p.append(text(475, 210, "GPIO Pin", size=10, color=INK, bold=True))

    # Верхній ESD-діод (від піна до VDD) — сегментовані лінії без перетину тексту
    b_diode_top, _, _ = textbox(615, 185, "Верхній захисний ESD-діод\n(ПРЯМИЙ СТРУМ)", size=9, fill="#fee2e2", stroke=POS, sw=1.2)
    p.append(line(530, 220, 530, 185, color=POS, sw=2.0))
    p.append(line(530, 185, 550, 185, color=POS, sw=2.0))
    p.append(b_diode_top)
    p.append(line(680, 185, 700, 185, color=POS, sw=2.0))
    p.append(line(700, 185, 700, 155, color=POS, sw=2.0))

    # Нижній ESD-діод (від GND до піна)
    p.append(line(490, 295, 740, 295, color=LINE, sw=1.8))
    p.append(text(730, 310, "GND (0 В)", size=10, color=LINE, anchor="end"))
    b_diode_bot, _, _ = textbox(615, 260, "Нижній ESD-діод (закритий)", size=9, fill="#f8fafc", stroke="#94a3b8", sw=1.0)
    p.append(b_diode_bot)

    # Червона стрілка струму паразитної зачитки від сенсора до піна
    p.append(arrow(225, 170, 450, 220, color=POS, sw=2.4))
    b_leak, _, _ = textbox(335, 160, "Паразитний струм I_leak\nчерез лінію зв'язку (~20 мА)", size=10, fill="#fee2e2", stroke=POS, bold=True)
    p.append(b_leak)

    # Наслідок: підйом VDD до ~2.7 В (розміщено окремо внизу)
    b_result, _, _ = textbox(410, 385, "Наслідок: шина VDD MCU підскакує до 3.3 В − 0.6 В = 2.7 В!\nMCU зависає в некерованому циклі перезапуску (Brown-Out Lockup)", size=11, fill="#fef2f2", stroke=POS, bold=True)
    p.append(b_result)

    render(os.path.join(OUT, "phantom-powering-hazard.svg"), W, H, *p,
           title="Механізм паразитної зачитки мікроконтролера через верхній захисний діод")


# ── 4. reverse-and-ovp-schemes: схеми вхідного захисту ───────────────────────
def fig_reverse_and_ovp_schemes():
    W, H = 840, 460
    p = []

    p.append(rect(20, 20, 800, 420, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Схема A: Діод Шотткі
    p.append(rect(35, 40, 240, 380, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(155, 68, "А. Діод Шотткі", size=13, color=INK, bold=True))
    b_sch_desc, _, _ = textbox(155, 125, "Простий послідовний діод\n+ Дешево, 1 компонент\n− Падіння Vf = 0.35…0.6 В\n− Тепловтрати P = I × Vf", size=11, fill="#ffffff", stroke="#cbd5e1", sw=1.0)
    p.append(b_sch_desc)

    p.append(line(60, 230, 110, 230, color=LINE, sw=1.5))
    b_d, _, _ = textbox(135, 230, "Діод\nШотткі", size=10, fill="#fee2e2", stroke=POS, sw=1.2)
    p.append(b_d)
    p.append(arrow(160, 230, 220, 230, color=LINE, sw=1.5))
    p.append(text(75, 215, "VIN", size=10, color=LINE, bold=True))
    p.append(text(210, 215, "VOUT", size=10, color=LINE, bold=True))

    b_sch_crit, _, _ = textbox(155, 330, "При I = 2 А втрати:\nP = 2 А × 0.5 В = 1.0 Вт!\n(потрібен радіатор)", size=10, fill="#fef2f2", stroke=POS, bold=True)
    p.append(b_sch_crit)

    # Схема B: P-MOSFET ключ
    p.append(rect(295, 40, 250, 380, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=6))
    p.append(text(420, 68, "Б. P-MOSFET захист", size=13, color="#15803d", bold=True))
    b_pmos_desc, _, _ = textbox(420, 125, "P-канальний польовик\n+ Падіння < 10…30 мВ\n+ ККД > 99.8%\n+ Затвор притиснутий до GND", size=11, fill="#ffffff", stroke="#86efac", sw=1.0)
    p.append(b_pmos_desc)

    p.append(line(320, 210, 370, 210, color=LINE, sw=1.5))
    b_mos, _, _ = textbox(410, 210, "P-MOSFET\n(Source-Drain)", size=10, fill="#dcfce7", stroke="#16a34a", sw=1.2)
    p.append(b_mos)
    p.append(arrow(450, 210, 510, 210, color=LINE, sw=1.5))

    p.append(line(410, 230, 410, 280, color=LINE, sw=1.2))
    b_zener, _, _ = textbox(410, 275, "R_pull (100 кОм) до GND\n+ Стабілітрон 12 В (Vgs)", size=9, fill="#ffffff", stroke="#16a34a", sw=1.0)
    p.append(b_zener)

    b_pmos_crit, _, _ = textbox(420, 345, "При I = 2 А та Rds=15 мОм:\nP = 4 × 0.015 = 0.06 Вт!\n(корпус лишається холодним)", size=10, fill="#f0fdf4", stroke="#15803d", bold=True)
    p.append(b_pmos_crit)

    # Схема C: OVP + Супресор (TVS)
    p.append(rect(565, 40, 255, 380, fill="#faf5ff", stroke="#a855f7", sw=1.5, rx=6))
    p.append(text(692, 68, "В. OVP + TVS захист", size=13, color="#6b21a8", bold=True))
    b_ovp_desc, _, _ = textbox(692, 125, "Супресор + OVP-контролер\n+ Зрізання наносекундних піків\n+ Миттєве відсікання > 5.8 В\n+ Захист від згоряння плати", size=11, fill="#ffffff", stroke="#d8b4fe", sw=1.0)
    p.append(b_ovp_desc)

    p.append(line(585, 210, 630, 210, color=LINE, sw=1.5))
    b_ovp_ic, _, _ = textbox(675, 210, "OVP Switch\n(N-MOS + IC)", size=10, fill="#f3e8ff", stroke="#9333ea", sw=1.2)
    p.append(b_ovp_ic)
    p.append(arrow(720, 210, 785, 210, color=LINE, sw=1.5))

    b_tvs_box, _, _ = textbox(605, 275, "TVS діод\nна вході", size=9, fill="#fee2e2", stroke=POS, sw=1.0)
    p.append(b_tvs_box)
    p.append(line(605, 210, 605, 255, color=LINE, sw=1.2))

    b_ovp_crit, _, _ = textbox(692, 345, "Час спрацьовування < 50 нс\nБлокує напругу до 40 В при\nпереплутаному БЖ 12В/24В", size=10, fill="#faf5ff", stroke="#6b21a8", bold=True)
    p.append(b_ovp_crit)

    render(os.path.join(OUT, "reverse-and-ovp-schemes.svg"), W, H, *p,
           title="Порівняння топологій захисту від переполюсовки та перенапруги")


# ── 5. power-sequencing-timing: часова діаграма послідовності вмикання ────────
def fig_power_sequencing_timing():
    W, H = 820, 460
    p = []

    p.append(rect(20, 20, 780, 420, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    ox = 180
    aw = 560

    # Рейка 1: VIN (Головне живлення 12 В / USB 5 В)
    y1 = 80
    p.append(text(ox - 15, y1 + 5, "1. Вхід VIN (5V/12V)", size=11, color=INK, anchor="end", bold=True))
    p.append(line(ox, y1 + 10, ox + 40, y1 + 10, color=LINE, sw=1.5))
    p.append(line(ox + 40, y1 + 10, ox + 80, y1 - 20, color=LINE, sw=2.2))
    p.append(line(ox + 80, y1 - 20, ox + aw, y1 - 20, color=LINE, sw=2.2))

    # Пунктир моменту t0
    p.append(line(ox + 80, y1 - 25, ox + 80, 400, color="#cbd5e1", sw=1.0, dash="4 4"))
    p.append(text(ox + 80, 415, "t0: Подача VIN", size=10, color=MUTED, anchor="middle"))

    # Рейка 2: VCORE (1.2 В)
    y2 = 145
    p.append(text(ox - 15, y2 + 5, "2. Ядро VCORE (1.2V)", size=11, color="#7c3aed", anchor="end", bold=True))
    p.append(line(ox, y2 + 10, ox + 110, y2 + 10, color=LINE, sw=1.5))
    p.append(line(ox + 110, y2 + 10, ox + 150, y2 - 20, color="#7c3aed", sw=2.2))
    p.append(line(ox + 150, y2 - 20, ox + aw, y2 - 20, color="#7c3aed", sw=2.2))

    # Пунктир t1 (PGOOD1)
    p.append(line(ox + 160, y2 - 25, ox + 160, 400, color="#cbd5e1", sw=1.0, dash="4 4"))
    p.append(text(ox + 160, 415, "t1: PGOOD1", size=10, color=MUTED, anchor="middle"))

    # Рейка 3: VDD / VIO (3.3 В)
    y3 = 210
    p.append(text(ox - 15, y3 + 5, "3. Логіка VDD (3.3V)", size=11, color="#2563eb", anchor="end", bold=True))
    p.append(line(ox, y3 + 10, ox + 190, y3 + 10, color=LINE, sw=1.5))
    p.append(line(ox + 190, y3 + 10, ox + 240, y3 - 20, color="#2563eb", sw=2.2))
    p.append(line(ox + 240, y3 - 20, ox + aw, y3 - 20, color="#2563eb", sw=2.2))

    # Пунктир t2 (PGOOD2)
    p.append(line(ox + 250, y3 - 25, ox + 250, 400, color="#cbd5e1", sw=1.0, dash="4 4"))
    p.append(text(ox + 250, 415, "t2: PGOOD2", size=10, color=MUTED, anchor="middle"))

    # Рейка 4: VPERIPH (Живлення датчиків / Load Switch)
    y4 = 275
    p.append(text(ox - 15, y4 + 5, "4. Периферія VPERIPH", size=11, color="#059669", anchor="end", bold=True))
    p.append(line(ox, y4 + 10, ox + 280, y4 + 10, color=LINE, sw=1.5))
    p.append(line(ox + 280, y4 + 10, ox + 330, y4 - 20, color="#059669", sw=2.2))
    p.append(line(ox + 330, y4 - 20, ox + aw, y4 - 20, color="#059669", sw=2.2))

    # Рейка 5: NRST (Скидання MCU)
    y5 = 340
    p.append(text(ox - 15, y5 + 5, "5. Скидання NRST", size=11, color=POS, anchor="end", bold=True))
    p.append(line(ox, y5 + 10, ox + 380, y5 + 10, color=POS, sw=1.5))
    p.append(line(ox + 380, y5 + 10, ox + 400, y5 - 20, color=POS, sw=2.2))
    p.append(line(ox + 400, y5 - 20, ox + aw, y5 - 20, color=POS, sw=2.2))

    # Пунктир t3 (Старт коду)
    p.append(line(ox + 400, y5 - 25, ox + 400, 400, color="#cbd5e1", sw=1.0, dash="4 4"))
    p.append(text(ox + 400, 415, "t3: Старт коду", size=10, color=POS, anchor="middle", bold=True))

    # Анотація безпеки
    b_seq_safe, _, _ = textbox(ox + 380, 50, "Всі внутрішні рейки та периферія стабілізовані ДО зняття сигналу скидання NRST", size=10, fill="#f0fdf4", stroke="#16a34a", bold=True)
    p.append(b_seq_safe)

    render(os.path.join(OUT, "power-sequencing-timing.svg"), W, H, *p,
           title="Послідовність подачі живлення: наростання рейок та зняття скидання")


if __name__ == "__main__":
    fig_power_tree_topology()
    fig_rail_domains_isolation()
    fig_phantom_powering_hazard()
    fig_reverse_and_ovp_schemes()
    fig_power_sequencing_timing()
    print("All figures generated successfully.")
