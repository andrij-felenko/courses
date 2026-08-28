# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. mcu-reference-contract: Контракт між кремнієм та зовнішньою обв'язкою ──
def fig_mcu_reference_contract():
    W, H = 920, 480
    p = []

    # Центральний блок: Кремнієвий кристал МК (IC Silicon Die)
    p.append(rect(290, 45, 340, 390, fill="#fdfefe", stroke=LINE, sw=2, rx=10))
    p.append(rect(305, 60, 310, 360, fill="#edf2f7", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(460, 85, "Кремнієвий кристал МК (Silicon Die)", size=14, color=INK, bold=True))
    p.append(text(460, 103, "Внутрішня архітектура підігнана під номінали", size=11, color=MUTED, italic=True))

    # Внутрішні блоки МК
    p.append(rect(320, 120, 280, 50, fill="#ffffff", stroke=NEG, sw=1.2, rx=5))
    p.append(text(460, 142, "Внутрішній DC-DC / LDO (VCORE)", size=12, color=NEG, bold=True))
    p.append(text(460, 158, "ШІМ 1.2 В, стабільний лише при точному L та C", size=10, color=MUTED))

    p.append(rect(320, 180, 280, 50, fill="#ffffff", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(460, 202, "Генератор Пірса (HSE / LSE)", size=12, color=FIELD, bold=True))
    p.append(text(460, 218, "Інвертор з фіксованою крутизною gm", size=10, color=MUTED))

    p.append(rect(320, 240, 280, 50, fill="#ffffff", stroke=POS, sw=1.2, rx=5))
    p.append(text(460, 262, "Аналоговий домен (PLL / ADC)", size=12, color=POS, bold=True))
    p.append(text(460, 278, "Чутливий до пульсацій живлення (PSRR)", size=10, color=MUTED))

    p.append(rect(320, 300, 280, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
    p.append(text(460, 321, "Тригер Шмітта NRST / BOOT-семплер", size=11.5, color=INK, bold=True))
    p.append(text(460, 337, "Фіксація логічного стану в момент скидання", size=10, color=MUTED))

    p.append(rect(320, 358, 280, 50, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
    p.append(text(460, 379, "Цифрове ядро та I/O кільце (VDD/VSS)", size=11.5, color=INK, bold=True))
    p.append(text(460, 396, "Імпульсні струми перемикання di/dt > 10^8 A/s", size=10, color=MUTED))

    # Лівий зовнішній блок: Живлення та фільтрація
    p.append(rect(30, 45, 225, 185, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(142, 70, "Фільтрація живлення", size=13, color=FIELD, bold=True))
    p.append(text(142, 88, "VDDA, VREF+, VCORE L/C", size=11, color=INK))
    p.append(text(142, 110, "• Феритова бусина (FB)", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(142, 126, "• Кераміка 100 nF + 1 uF + 10 uF", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(142, 142, "• Котушка з запасом по Isat", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(142, 165, "Вимога: Z(ω) < 0.1 Ом на ВЧ", size=10.5, color=FIELD, bold=True))

    p.append(arrow(255, 145, 288, 145, color=FIELD, sw=2))
    p.append(arrow(255, 260, 288, 260, color=FIELD, sw=2))

    # Лівий ніжній блок: Розв'язка цифрових ніжок
    p.append(rect(30, 250, 225, 185, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(142, 275, "Розподілена розв'язка", size=13, color=NEG, bold=True))
    p.append(text(142, 293, "Decoupling біля кожної пари", size=11, color=INK))
    p.append(text(142, 316, "• 100 nF біля кожного VDD", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(142, 332, "• Мінімальна петля монтажу", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(142, 348, "• Запобігання Ground Bounce", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(142, 375, "Вимога: L_trace < 1 нГн", size=10.5, color=NEG, bold=True))

    p.append(arrow(255, 380, 288, 380, color=NEG, sw=2))

    # Правий верхній блок: Кварцовий резонатор
    p.append(rect(665, 45, 225, 185, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    p.append(text(777, 70, "Обв'язка кварцу", size=13, color=NEG, bold=True))
    p.append(text(777, 88, "HSE (8–25 МГц) / LSE (32 кГц)", size=11, color=INK))
    p.append(text(777, 110, "• Розрахунок CL1, CL2 (pF)", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(777, 126, "• Врахування C_stray (2–5 pF)", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(777, 142, "• Демпфуючий резистор Rd", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(777, 165, "Вимога: Gain Margin ≥ 5", size=10.5, color=NEG, bold=True))

    p.append(arrow(665, 200, 632, 200, color=NEG, sw=2))

    # Правий ніжній блок: Скидання та конфігурація
    p.append(rect(665, 250, 225, 185, fill="#fff7ed", stroke=POS, sw=1.5, rx=8))
    p.append(text(777, 275, "Скидання та BOOT-піни", size=13, color=POS, bold=True))
    p.append(text(777, 293, "NRST, BOOT0, BOOT1", size=11, color=INK))
    p.append(text(777, 316, "• RC-фільтр від завад", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(777, 332, "• Діод швидкого розряду", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(777, 348, "• Жорсткі підтяжки BOOT", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(777, 375, "Вимога: захист від плавання", size=10.5, color=POS, bold=True))

    p.append(arrow(665, 325, 632, 325, color=POS, sw=2))

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, 455,
                          "Референсна схема — це єдиний набір граничних умов, за яких гарантовано паспортні характеристики ІС.\n"
                          "Будь-яка самовільна зміна ламає внутрішні зворотні зв'язки та стабільність кремнієвого кристала.",
                          size=11, stroke=LINE, fill="#f8fafc")
    p.append(b_bot)

    render(os.path.join(OUT, "mcu-reference-contract.svg"), W, H, *p,
           title="Референсна схема як інженерний контракт із кремнієвим кристалом")


# ── 2. analog-power-filter-pi: Фільтрація аналогового живлення VDDA/VREF+ ──────
def fig_analog_power_filter_pi():
    W, H = 900, 420
    p = []

    # Вхідна цифрова лінія VDD
    p.append(text(60, 110, "VDD (Цифра 3.3 В)", size=12, color=POS, bold=True))
    p.append(text(60, 128, "Шум di/dt, гармоніки ШІМ", size=10, color=MUTED))
    p.append(circle(140, 140, 5, fill=POS, stroke=LINE, sw=1.5))
    p.append(line(140, 140, 220, 140, color=LINE, sw=2))

    # Конденсатор на вході фільтра C_in
    p.append(line(220, 140, 220, 180, color=LINE, sw=1.8))
    p.append(rect(205, 180, 30, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(rect(205, 196, 30, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(line(220, 208, 220, 250, color=LINE, sw=1.8))
    p.append(text(220, 270, "10 мкФ", size=11, color=INK, bold=True))
    p.append(text(220, 285, "C_in (MLCC)", size=10, color=MUTED))

    # Феритова бусина FB
    p.append(line(220, 140, 310, 140, color=LINE, sw=2))
    p.append(rect(310, 125, 80, 30, fill="#e2e8f0", stroke=LINE, sw=1.8, rx=4))
    p.append(text(350, 143, "FB", size=13, color=INK, bold=True))
    p.append(text(350, 172, "600 Ом @ 100 МГц", size=10.5, color=FIELD, bold=True))
    p.append(text(350, 187, "R_DCR < 0.2 Ом", size=10, color=MUTED))
    p.append(line(390, 140, 480, 140, color=LINE, sw=2))

    # Вихідний блок конденсаторів (0.1 мкФ + 1 мкФ + 100 пФ)
    # C1 (100 нФ)
    p.append(line(480, 140, 480, 180, color=LINE, sw=1.8))
    p.append(rect(465, 180, 30, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(rect(465, 196, 30, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(line(480, 208, 480, 250, color=LINE, sw=1.8))
    p.append(text(480, 270, "100 нФ", size=11, color=INK, bold=True))
    p.append(text(480, 285, "ВЧ шунт", size=10, color=MUTED))

    # C2 (1 мкФ)
    p.append(line(480, 140, 590, 140, color=LINE, sw=2))
    p.append(line(590, 140, 590, 180, color=LINE, sw=1.8))
    p.append(rect(575, 180, 30, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(rect(575, 196, 30, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(line(590, 208, 590, 250, color=LINE, sw=1.8))
    p.append(text(590, 270, "1 мкФ", size=11, color=INK, bold=True))
    p.append(text(590, 285, "СЧ фільтр", size=10, color=MUTED))

    # C3 (100 пФ NP0/C0G)
    p.append(line(590, 140, 700, 140, color=LINE, sw=2))
    p.append(line(700, 140, 700, 180, color=LINE, sw=1.8))
    p.append(rect(685, 180, 30, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(rect(685, 196, 30, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(line(700, 208, 700, 250, color=LINE, sw=1.8))
    p.append(text(700, 270, "100 пФ NP0", size=11, color=INK, bold=True))
    p.append(text(700, 285, "ГГц шунт", size=10, color=MUTED))

    # Земляна шина знизу (на y=250)
    p.append(line(180, 250, 740, 250, color=FIELD, sw=2.5))
    p.append(text(460, 315, "Аналогова земляна площина (AGND / Solid Ground Plane)", size=11.5, color=FIELD, bold=True))

    # Вихід на VDDA та VREF+
    p.append(arrow(700, 140, 810, 140, color=POS, sw=2.5))
    p.append(circle(815, 140, 5, fill=FIELD, stroke=LINE, sw=1.5))
    p.append(text(825, 115, "VDDA / VREF+", size=13, color=FIELD, bold=True, anchor="start"))
    p.append(text(825, 133, "Чисте живлення аналогу", size=10.5, color=MUTED, anchor="start"))
    p.append(text(825, 150, "Пульсації < 1 мВ RMS", size=10, color=FIELD, anchor="start"))

    # Пояснювальний бокс знизу
    b_bot, _, _ = textbox(W / 2, 375,
                          "Феритова бусина створює опір високочастотному шуму (>10 МГц), розсіюючи його в тепло,\n"
                          "а каскад паралельних конденсаторів формує низький імпеданс на землю в широкому діапазоні частот.",
                          size=11, stroke=MUTED, fill="#f8fafc")
    p.append(b_bot)

    render(os.path.join(OUT, "analog-power-filter-pi.svg"), W, H, *p,
           title="П-подібний фільтр аналогового живлення (VDDA / VREF+)")


# ── 3. nrst-circuit-structure: Схема апаратного скидання NRST з діодом ────────
def fig_nrst_circuit_structure():
    W, H = 920, 440
    p = []

    # Лінія живлення VDD зверху
    p.append(line(120, 60, 450, 60, color=POS, sw=2))
    p.append(text(280, 45, "Шина живлення VDD (3.3 В)", size=12, color=POS, bold=True))

    # Підтягуючий резистор R_pullup
    p.append(line(200, 60, 200, 100, color=LINE, sw=1.8))
    p.append(rect(185, 100, 30, 60, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(200, 133, "R_pu", size=11, color=INK, bold=True))
    p.append(text(145, 133, "10 кОм", size=10.5, color=MUTED, anchor="end"))
    p.append(line(200, 160, 200, 220, color=LINE, sw=1.8))

    # Розрядний діод Шотткі (паралельно R_pu)
    p.append(line(310, 60, 310, 105, color=LINE, sw=1.8))
    # Катод зверху, анод знизу (щоб розряджати ємність у VDD при вимкненні)
    p.append(line(295, 105, 325, 105, color=LINE, sw=1.8)) # катод
    p.append(line(295, 105, 295, 100, color=LINE, sw=1.5))
    p.append(line(325, 105, 325, 110, color=LINE, sw=1.5))
    p.append(line(295, 140, 325, 140, color=LINE, sw=1.8)) # анод
    p.append(line(295, 140, 310, 105, color=LINE, sw=1.8))
    p.append(line(325, 140, 310, 105, color=LINE, sw=1.8))
    p.append(line(310, 140, 310, 220, color=LINE, sw=1.8))
    p.append(text(370, 120, "Діод Шотткі (BAT54)", size=11, color=POS, bold=True))
    p.append(text(370, 138, "Швидкий розряд при зникненні VDD", size=10, color=MUTED))

    # З'єднання вузла NRST
    p.append(line(200, 220, 620, 220, color=LINE, sw=2))
    p.append(circle(200, 220, 4, fill=INK, stroke=LINE))
    p.append(circle(310, 220, 4, fill=INK, stroke=LINE))
    p.append(circle(440, 220, 4, fill=INK, stroke=LINE))
    p.append(circle(530, 220, 4, fill=INK, stroke=LINE))

    # Фільтруючий конденсатор C_rst (100 нФ)
    p.append(line(440, 220, 440, 260, color=LINE, sw=1.8))
    p.append(rect(425, 260, 30, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(rect(425, 276, 30, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(line(440, 288, 440, 330, color=LINE, sw=1.8))
    p.append(text(440, 350, "C_rst (100 нФ)", size=11, color=INK, bold=True))
    p.append(text(440, 368, "Фільтр брязкоту й завад", size=10, color=MUTED))

    # Кнопка ручного скидання з послідовним резистором
    p.append(line(530, 220, 530, 250, color=LINE, sw=1.8))
    p.append(rect(515, 250, 30, 35, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(530, 270, "R_s", size=11, color=INK, bold=True))
    p.append(text(560, 270, "100 Ом", size=10, color=MUTED, anchor="start"))
    p.append(line(530, 285, 530, 305, color=LINE, sw=1.8))
    # Контакти кнопки
    p.append(circle(530, 308, 3, fill="#ffffff", stroke=LINE))
    p.append(circle(530, 322, 3, fill="#ffffff", stroke=LINE))
    p.append(line(520, 308, 520, 320, color=POS, sw=2)) # важіль
    p.append(line(530, 325, 530, 350, color=LINE, sw=1.8))
    p.append(text(555, 316, "Кнопка RESET", size=11, color=INK, bold=True, anchor="start"))

    # Земля знизу
    p.append(line(400, 350, 560, 350, color=FIELD, sw=2))
    p.append(line(440, 330, 440, 350, color=FIELD, sw=1.8))
    p.append(text(480, 375, "GND", size=11, color=FIELD, bold=True))

    # Блок МК праворуч
    p.append(rect(630, 150, 260, 180, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(760, 175, "Мікроконтролер (MCU)", size=13, color=INK, bold=True))
    p.append(circle(630, 220, 5, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(645, 212, "NRST", size=12, color=POS, bold=True, anchor="start"))

    # Внутрішній тригер Шмітта МК
    p.append(rect(680, 200, 180, 45, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(770, 220, "Тригер Шмітта", size=11.5, color=INK, bold=True))
    p.append(text(770, 236, "Гістерезис ~ 200–400 мВ", size=10, color=MUTED))

    # Внутрішня підтяжка
    p.append(line(710, 200, 710, 265, color=MUTED, sw=1.2, dash="3 3"))
    p.append(rect(695, 265, 30, 30, fill="#ffffff", stroke=MUTED, sw=1, rx=2))
    p.append(text(710, 283, "R_int", size=10, color=MUTED))
    p.append(text(740, 283, "40 кОм", size=10, color=MUTED, anchor="start"))

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, 410,
                          "Діод Шотткі миттєво розряджає конденсатор C_rst при просіданні живлення VDD,\n"
                          "запобігаючи зависанню ядра та забезпечуючи гарантований апаратний Reset при швидкому перезапуску.",
                          size=10.5, stroke=MUTED, fill="#fffaf0")
    p.append(b_bot)

    render(os.path.join(OUT, "nrst-circuit-structure.svg"), W, H, *p,
           title="Апаратний ланцюг скидання (NRST) з діодним захистом")


# ── 4. inductor-saturation-failure: Струм насичення індуктивності VCORE ────────
def fig_inductor_saturation_failure():
    W, H = 900, 420
    p = []

    # Лівий графік: L vs I_current (Крива насичення сердечника)
    p.append(rect(40, 50, 380, 300, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(230, 75, "Крива насичення індуктивності L(I)", size=13, color=INK, bold=True))

    # Осі лівого графіка
    p.append(line(80, 310, 390, 310, color=LINE, sw=1.5)) # вісь I
    p.append(arrow(390, 310, 405, 310, color=LINE, sw=1.5))
    p.append(text(400, 328, "Струм I (мА)", size=10.5, color=INK))

    p.append(line(80, 310, 80, 100, color=LINE, sw=1.5)) # вісь L
    p.append(arrow(80, 100, 80, 85, color=LINE, sw=1.5))
    p.append(text(65, 95, "L (мкГн)", size=10.5, color=INK, anchor="end"))

    # Нормальна крива L (номінальна з високим Isat)
    p.append(line(80, 140, 240, 140, color=FIELD, sw=2.5))
    p.append(line(240, 140, 370, 220, color=FIELD, sw=2.5))
    p.append(text(240, 125, "Правильна котушка (Isat = 1.2 А)", size=10, color=FIELD, bold=True))

    # Погана крива L (дешева з малим Isat)
    p.append(line(80, 140, 160, 145, color=POS, sw=2.5, dash="4 3"))
    p.append(line(160, 145, 220, 300, color=POS, sw=2.5, dash="4 3"))
    p.append(text(160, 175, "Невдала заміна (Isat = 200 мА)", size=10, color=POS, bold=True))

    p.append(line(180, 100, 180, 310, color=POS, sw=1, dash="2 2"))
    p.append(text(180, 325, "I_peak навантаження", size=9.5, color=POS))

    # Правий графік: Наслідки для напруги VCORE та струму ключа
    p.append(rect(460, 50, 410, 300, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(665, 75, "Наслідки насичення сердечника", size=13, color=POS, bold=True))

    # Струм через ключ ШІМ
    p.append(text(490, 110, "1. Струм через внутрішній ключ:", size=11, color=INK, bold=True, anchor="start"))
    p.append(line(500, 160, 600, 160, color=MUTED, sw=1))
    p.append(line(500, 160, 540, 130, color=FIELD, sw=2)) # нормальний лінійний підйом
    p.append(line(540, 130, 540, 160, color=FIELD, sw=1.5))
    p.append(text(540, 120, "Норма (ΔI помірний)", size=9.5, color=FIELD))

    p.append(line(640, 160, 740, 160, color=MUTED, sw=1))
    p.append(line(640, 160, 665, 145, color=POS, sw=2))
    p.append(line(665, 145, 680, 95, color=POS, sw=2.5)) # вибуховий підйом через падіння L
    p.append(line(680, 95, 680, 160, color=POS, sw=1.5))
    p.append(text(680, 90, "НАСИЧЕННЯ (di/dt = V/L → ∞)", size=9.5, color=POS, bold=True))

    # Просідання напруги VCORE
    p.append(text(490, 195, "2. Напруга живлення ядра VCORE (1.2 В):", size=11, color=INK, bold=True, anchor="start"))
    p.append(line(500, 240, 830, 240, color=FIELD, sw=2))
    p.append(line(660, 240, 680, 290, color=POS, sw=2.5)) # провал напруги
    p.append(line(680, 290, 710, 290, color=POS, sw=2.5))
    p.append(line(710, 290, 730, 240, color=POS, sw=2))
    p.append(line(500, 265, 830, 265, color=POS, sw=1, dash="3 3"))
    p.append(text(835, 265, "V_min (HardFault)", size=9.5, color=POS, anchor="start"))
    p.append(text(700, 310, "Просідання нижче порогу POR/BOR → аварійне перезавантаження", size=10, color=POS))

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, 385,
                          "Коли струм перевищує Isat, індуктивність L падає до нуля. Котушка перетворюється на звичайний дріт,\n"
                          "викликаючи перегрів ключа ШІМ, провал напруги ядра VCORE і спонтанні падіння мікроконтролера в HardFault.",
                          size=10.5, stroke=POS, fill="#fff5f5")
    p.append(b_bot)

    render(os.path.join(OUT, "inductor-saturation-failure.svg"), W, H, *p,
           title="Фізика насичення індуктивності та збій живлення цифрового ядра")


if __name__ == "__main__":
    fig_mcu_reference_contract()
    fig_analog_power_filter_pi()
    fig_nrst_circuit_structure()
    fig_inductor_saturation_failure()
    print("All figures generated successfully.")
