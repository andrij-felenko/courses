# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. board-anatomy: Функціональні зони плати розробника ─────────────────────
def fig_board_anatomy():
    W, H = 960, 520
    p = []

    # Загальний контур плати
    p.append(rect(40, 30, 880, 460, fill="#f8fafc", stroke="#94a3b8", sw=2, rx=12))
    p.append(text(80, 58, "ПЛАТА РОЗРОБНИКА (DEVELOPMENT BOARD)", size=13, color=MUTED, bold=True, anchor="start"))

    # Лінія розлому (перфорація)
    p.append(line(310, 30, 310, 490, color="#64748b", sw=2, dash="6,6"))
    p.append(text(310, 506, "лінія механічного розлому (break-off)", size=10, color=MUTED, bold=False))

    # ЗОНА 1: Вбудований зневаджувач (ліва частина)
    p.append(rect(55, 75, 235, 395, fill="#f1f5f9", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(172, 100, "Вбудований зневаджувач", size=12, color=NEG, bold=True))
    p.append(text(172, 116, "(ST-Link / CMSIS-DAP)", size=10, color=MUTED))

    # USB роз'єм
    p.append(rect(65, 140, 70, 50, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))
    p.append(text(100, 168, "USB (PC)", size=10, color=INK, bold=True))

    # Debug MCU
    p.append(rect(160, 140, 115, 80, fill="#dbeafe", stroke=NEG, sw=1.5, rx=6))
    p.append(text(217, 172, "Зневаджувальний", size=10, color=NEG, bold=True))
    p.append(text(217, 188, "МК (STM32F103)", size=10, color=INK))

    # VCP міст
    p.append(rect(75, 245, 195, 55, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(172, 268, "Віртуальний COM-порт (VCP)", size=10, color=INK, bold=True))
    p.append(text(172, 286, "UART ↔ USB CDC-ACM", size=9.5, color=MUTED))

    # Джампери SWD
    p.append(rect(75, 325, 195, 65, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(172, 348, "Перемички CN2 (SWD)", size=10, color=INK, bold=True))
    p.append(text(172, 365, "ON: зв'язок із цільовим МК", size=9.5, color=FIELD))
    p.append(text(172, 380, "OFF: зневадження зовні", size=9.5, color=MUTED))

    # Світлодіоди відладчика
    p.append(circle(120, 425, 7, fill="#ef4444", stroke="#b91c1c", sw=1.5))
    p.append(circle(145, 425, 7, fill="#22c55e", stroke="#15803d", sw=1.5))
    p.append(text(172, 429, "LED стану / TX-RX", size=9.5, color=MUTED, anchor="start"))

    # ЗОНА 2: Цільова система (права частина)
    # Цільовий мікроконтролер
    p.append(rect(520, 180, 170, 170, fill="#fef3c7", stroke="#d97706", sw=2, rx=10))
    p.append(text(605, 255, "Цільовий МК", size=14, color="#b45309", bold=True))
    p.append(text(605, 275, "(STM32 / ESP32)", size=12, color=INK, bold=True))
    p.append(text(605, 295, "Робоче ядро системи", size=10, color=MUTED))

    # Лінії SWD між відладчиком та МК
    p.append(line(275, 180, 520, 205, color=NEG, sw=1.8))
    p.append(text(395, 188, "SWD (SWCLK, SWDIO, NRST)", size=9.5, color=NEG, bold=True))

    p.append(line(270, 272, 520, 240, color="#d97706", sw=1.8))
    p.append(text(395, 248, "VCP UART (TX, RX)", size=9.5, color="#d97706", bold=True))

    # Підсистема живлення (вгорі праворуч)
    p.append(rect(340, 75, 230, 85, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(455, 98, "Дерево живлення", size=11, color=FIELD, bold=True))
    p.append(text(455, 116, "USB 5V / VIN 7-12V → LDO 3.3V", size=9.5, color=INK))
    p.append(text(455, 134, "Перемичка струму IDD (міст)", size=9.5, color=MUTED))
    p.append(arrow(455, 160, 540, 180, color=FIELD, sw=1.5))

    # Тактування (HSE + LSE)
    p.append(rect(730, 75, 165, 85, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(812, 98, "Кварцові резонатори", size=11, color=INK, bold=True))
    p.append(text(812, 116, "HSE: 8–25 МГц (системний)", size=9.5, color=MUTED))
    p.append(text(812, 134, "LSE: 32.768 кГц (RTC)", size=9.5, color=MUTED))
    p.append(arrow(730, 120, 685, 195, color=LINE, sw=1.4))

    # Інтерфейс користувача: Кнопки й світлодіоди (знизу)
    p.append(rect(340, 385, 230, 85, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(455, 408, "Кнопки скидання та користувача", size=11, color=INK, bold=True))
    p.append(text(455, 426, "Reset (RC-ланка 10k + 100nF)", size=9.5, color=MUTED))
    p.append(text(455, 444, "User Button (B1, підтяжка)", size=9.5, color=MUTED))
    p.append(arrow(455, 385, 540, 345, color=LINE, sw=1.4))

    # BOOT & User LEDs (знизу праворуч)
    p.append(rect(600, 385, 180, 85, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(690, 408, "Конфігурація й індикація", size=11, color=INK, bold=True))
    p.append(text(690, 426, "Джампер BOOT0 / Strapping", size=9.5, color=MUTED))
    p.append(text(690, 444, "Світлодіод користувача (LD2)", size=9.5, color=MUTED))
    p.append(arrow(670, 385, 640, 350, color=LINE, sw=1.4))

    # Штирі контактних колодок (Headers) по периметру
    p.append(rect(895, 160, 20, 220, fill="#334155", stroke="#1e293b", sw=1, rx=2))
    p.append(text(870, 275, "GPIO штирі →", size=10, color=MUTED, bold=True, anchor="end"))

    p.append(rect(320, 160, 16, 220, fill="#334155", stroke="#1e293b", sw=1, rx=2))
    p.append(text(342, 275, "← Морфо / Arduino штирі", size=10, color=MUTED, bold=True, anchor="start"))

    render(os.path.join(OUT, "board-anatomy.svg"), W, H, *p,
           title="Анатомія типової відлагоджувальної плати: зневаджувач, живлення, такти, обв'язка")


# ── 2. swd-breakoff: Інтерфейс SWD та лінія механічного розлому ───────────────
def fig_swd_breakoff():
    W, H = 920, 400
    p = []

    # Ліва секція (Debug MCU)
    p.append(rect(40, 50, 240, 300, fill="#f1f5f9", stroke=NEG, sw=2, rx=8))
    p.append(text(160, 80, "Зневаджувач (ST-Link)", size=13, color=NEG, bold=True))
    p.append(text(160, 100, "STM32F103 / F723", size=11, color=MUTED))

    # Виводи зневаджувача
    pins_dbg = [
        (130, "SWCLK (вихід такту)"),
        (170, "SWDIO (двонаправлені дані)"),
        (210, "NRST (апаратне скидання)"),
        (250, "SWO / TRACE (трасування)"),
        (290, "VCP RX / TX (UART лог)"),
    ]
    for y, label in pins_dbg:
        p.append(rect(60, y - 14, 200, 26, fill="#ffffff", stroke="#94a3b8", sw=1, rx=4))
        p.append(text(160, y + 4, label, size=10, color=INK, bold=True))

    # Центральна секція: Лінія розлому та комутація перемичок
    p.append(line(450, 20, 450, 380, color="#ef4444", sw=2, dash="5,5"))
    p.append(text(450, 35, "Лінія розлому PCB", size=10, color=POS, bold=True))

    # Перемички CN2
    p.append(rect(360, 110, 180, 210, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    p.append(text(450, 135, "Блок перемичок CN2", size=11, color=INK, bold=True))

    # Режим 1: Встановлені джампери
    p.append(rect(375, 155, 150, 60, fill="#ecfdf5", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(450, 175, "Джампери ON", size=10, color=FIELD, bold=True))
    p.append(text(450, 195, "Робота з чипом на платі", size=9.5, color=INK))

    # Режим 2: Зняті джампери
    p.append(rect(375, 235, 150, 65, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    p.append(text(450, 255, "Джампери OFF", size=10, color=POS, bold=True))
    p.append(text(450, 273, "Зовнішній роз'єм SWD", size=9.5, color=INK))
    p.append(text(450, 290, "Програмування своєї плати", size=9, color=MUTED))

    # Права секція (Target MCU)
    p.append(rect(630, 50, 250, 300, fill="#fffbeb", stroke="#d97706", sw=2, rx=8))
    p.append(text(755, 80, "Цільовий МК", size=13, color="#b45309", bold=True))
    p.append(text(755, 100, "STM32G4 / STM32F4 / ESP32", size=11, color=MUTED))

    # Виводи цільового МК
    pins_tgt = [
        (130, "PA14 / SWCLK"),
        (170, "PA13 / SWDIO"),
        (210, "NRST (Reset)"),
        (250, "PB3 / SWO (ITM)"),
        (290, "PA2/PA3 (USART2 TX/RX)"),
    ]
    for y, label in pins_tgt:
        p.append(rect(650, y - 14, 210, 26, fill="#ffffff", stroke="#d97706", sw=1, rx=4))
        p.append(text(755, y + 4, label, size=10, color=INK, bold=True))

    # З'єднувальні лінії
    p.append(line(260, 130, 360, 130, color=NEG, sw=1.5))
    p.append(arrow(540, 130, 650, 130, color=NEG, sw=1.5))

    p.append(line(260, 170, 360, 170, color=NEG, sw=1.5))
    p.append(arrow(540, 170, 650, 170, color=NEG, sw=1.5))

    p.append(line(260, 210, 360, 210, color=NEG, sw=1.5))
    p.append(arrow(540, 210, 650, 210, color=NEG, sw=1.5))

    p.append(line(260, 250, 360, 250, color=LINE, sw=1.5))
    p.append(arrow(540, 250, 650, 250, color=LINE, sw=1.5))

    p.append(line(260, 290, 360, 290, color="#d97706", sw=1.5))
    p.append(arrow(540, 290, 650, 290, color="#d97706", sw=1.5))

    render(os.path.join(OUT, "swd-breakoff.svg"), W, H, *p,
           title="Інтерфейс SWD, лінія розлому та використання зневаджувача для зовнішньої плати")


# ── 3. power-tree: Дерево живлення плати, LDO та перемичка IDD ────────────────
def fig_power_tree():
    W, H = 940, 430
    p = []

    # Входи живлення
    # Вхід 1: USB VBUS
    p.append(rect(40, 60, 160, 80, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    p.append(text(120, 88, "USB VBUS (5V)", size=12, color=INK, bold=True))
    p.append(text(120, 108, "Ліміт хоста 500 мА", size=10, color=MUTED))
    p.append(text(120, 126, "Polyfuse PTC 500mA", size=9.5, color=FIELD))

    # Вхід 2: Зовнішній VIN
    p.append(rect(40, 210, 160, 80, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    p.append(text(120, 238, "VIN (7–12V)", size=12, color=INK, bold=True))
    p.append(text(120, 258, "Роз'єм або штир VIN", size=10, color=MUTED))
    p.append(text(120, 276, "Зовнішній БЖ", size=9.5, color=MUTED))

    # Вузол автокомутації джерел
    p.append(rect(260, 110, 180, 140, fill="#ecfdf5", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(350, 138, "Селектор джерела", size=12, color=FIELD, bold=True))
    p.append(text(350, 160, "Діоди Шотткі /", size=10, color=INK))
    p.append(text(350, 178, "P-MOSFET ідеальний діод", size=10, color=INK))
    p.append(text(350, 202, "Пріоритет: VIN > USB", size=9.5, color=MUTED))
    p.append(text(350, 224, "Захист порту ПК", size=9.5, color=POS))

    # Стрілки входів до комутатора
    p.append(arrow(200, 100, 260, 150, color=LINE, sw=1.5))
    p.append(arrow(200, 250, 260, 200, color=LINE, sw=1.5))

    # Шина 5V (силовий вихід комутатора)
    p.append(line(440, 180, 500, 180, color=FIELD, sw=2.5))
    p.append(text(470, 170, "5V_MAIN", size=10, color=FIELD, bold=True))

    # Стабілізатор LDO 5V -> 3.3V
    p.append(rect(500, 130, 150, 100, fill="#fff1f2", stroke=POS, sw=1.8, rx=6))
    p.append(text(575, 158, "LDO стабілізатор", size=11, color=POS, bold=True))
    p.append(text(575, 178, "5V → 3.3V", size=12, color=INK, bold=True))
    p.append(text(575, 198, "LD39050 / AMS1117", size=9.5, color=MUTED))
    p.append(text(575, 216, "I_max ≈ 300–800 мА", size=9.5, color=POS))

    # Перемичка IDD (IDD Jumper)
    p.append(rect(700, 145, 80, 70, fill="#ffffff", stroke="#2563eb", sw=1.5, rx=6))
    p.append(text(740, 170, "IDD JP", size=11, color=NEG, bold=True))
    p.append(circle(725, 195, 4, fill=NEG, stroke=INK, sw=1))
    p.append(circle(755, 195, 4, fill=NEG, stroke=INK, sw=1))
    p.append(line(725, 195, 755, 195, color=NEG, sw=3))

    p.append(arrow(650, 180, 700, 180, color=LINE, sw=1.8))
    p.append(text(675, 170, "3.3V", size=10, color=INK, bold=True))

    # Вихід на цільовий МК
    p.append(arrow(780, 180, 830, 180, color=LINE, sw=1.8))
    p.append(rect(830, 135, 95, 90, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    p.append(text(877, 168, "Цільовий МК", size=10.5, color="#b45309", bold=True))
    p.append(text(877, 188, "VDD шина", size=10, color=INK))
    p.append(text(877, 206, "100nF розв'язка", size=9.5, color=MUTED))

    # Блок вимірювання струму (підказка до IDD)
    p.append(rect(670, 270, 240, 130, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=6))
    p.append(text(790, 295, "Вимірювання струму сну (IDD)", size=11, color=NEG, bold=True))
    p.append(text(790, 318, "1. Зняти перемичку IDD", size=9.5, color=INK))
    p.append(text(790, 338, "2. Під'єднати амперметр у розрив", size=9.5, color=INK))
    p.append(text(790, 358, "3. Вимірювати чистий струм ядра", size=9.5, color=FIELD))
    p.append(text(790, 378, "без споживання LDO та LED плати", size=9, color=MUTED))
    p.append(arrow(740, 270, 740, 215, color=NEG, sw=1.2))

    # Штирі живлення 5V та 3.3V назовні
    p.append(rect(460, 310, 170, 80, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(545, 332, "Штирі живлення плати", size=10.5, color=INK, bold=True))
    p.append(text(545, 352, "5V (вихід комутатора)", size=9.5, color=FIELD))
    p.append(text(545, 370, "3.3V (вихід LDO)", size=9.5, color=POS))

    render(os.path.join(OUT, "power-tree.svg"), W, H, *p,
           title="Дерево живлення плати: захист, перемикання джерел, LDO та вимірювальний міст IDD")


# ── 4. pierce-and-cl: Генератор Пірса та розрахунок ємностей кварцу ───────────
def fig_pierce_and_cl():
    W, H = 920, 420
    p = []

    # Ліва частина: Схема генератора Пірса всередині й зовні МК
    p.append(rect(40, 40, 480, 350, fill="#f8fafc", stroke="#94a3b8", sw=1.8, rx=8))
    p.append(text(280, 68, "Схема генератора Пірса (HSE / LSE)", size=12, color=INK, bold=True))

    # Кремній МК (межа)
    p.append(rect(55, 90, 200, 280, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(155, 115, "Всередині чипа МК", size=10.5, color="#b45309", bold=True))

    # Інвертор
    p.append(rect(90, 180, 70, 60, fill="#ffffff", stroke=INK, sw=1.5, rx=4))
    p.append(text(125, 215, "Інвертор", size=10, color=INK, bold=True))

    # Резистор зворотного зв'язку Rf
    p.append(rect(90, 140, 70, 24, fill="#ffffff", stroke=INK, sw=1.2, rx=2))
    p.append(text(125, 156, "Rf ≈ 1–10 MΩ", size=9, color=MUTED))
    p.append(line(75, 152, 90, 152, color=LINE, sw=1.2))
    p.append(line(160, 152, 175, 152, color=LINE, sw=1.2))
    p.append(line(75, 152, 75, 210, color=LINE, sw=1.2))
    p.append(line(175, 152, 175, 210, color=LINE, sw=1.2))

    # Виводи МК: OSC_IN та OSC_OUT
    p.append(circle(255, 180, 5, fill="#d97706", stroke=INK, sw=1))
    p.append(text(215, 175, "OSC_IN", size=9.5, color=INK, bold=True))

    p.append(circle(255, 240, 5, fill="#d97706", stroke=INK, sw=1))
    p.append(text(215, 245, "OSC_OUT", size=9.5, color=INK, bold=True))

    # Зовнішній кварц
    p.append(rect(340, 185, 50, 50, fill="#ffffff", stroke=NEG, sw=1.8, rx=4))
    p.append(text(365, 214, "Кварц", size=10, color=NEG, bold=True))
    p.append(text(365, 252, "Q1", size=10, color=INK))

    p.append(line(255, 180, 340, 195, color=LINE, sw=1.5))
    p.append(line(255, 240, 340, 225, color=LINE, sw=1.5))

    # Конденсатори навантаження C1 та C2
    p.append(rect(320, 290, 35, 25, fill="#ffffff", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(337, 307, "C1", size=10, color=FIELD, bold=True))
    p.append(line(337, 195, 337, 290, color=LINE, sw=1.2))
    p.append(line(337, 315, 337, 340, color=LINE, sw=1.2))

    p.append(rect(390, 290, 35, 25, fill="#ffffff", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(407, 307, "C2", size=10, color=FIELD, bold=True))
    p.append(line(392, 225, 407, 225, color=LINE, sw=1.2))
    p.append(line(407, 225, 407, 290, color=LINE, sw=1.2))
    p.append(line(407, 315, 407, 340, color=LINE, sw=1.2))

    # Земля для C1, C2
    p.append(line(320, 340, 425, 340, color=LINE, sw=1.5))
    p.append(line(355, 345, 390, 345, color=LINE, sw=1.5))
    p.append(line(365, 350, 380, 350, color=LINE, sw=1.5))

    # Права частина: Формули розрахунку та тактування MCO
    # Блок формули CL
    p.append(rect(550, 40, 330, 165, fill="#ecfdf5", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(715, 68, "Розрахунок ємностей навантаження", size=12, color=FIELD, bold=True))
    p.append(text(715, 96, "C_L = (C1 · C2) / (C1 + C2) + C_stray", size=11, color=INK, bold=True))
    p.append(text(715, 120, "При C1 = C2 = C:", size=10, color=MUTED))
    p.append(text(715, 142, "C = 2 · (C_L − C_stray)", size=12, color=POS, bold=True))
    p.append(text(715, 168, "C_stray PCB ≈ 2–5 пФ (паразитна ємність)", size=9.5, color=MUTED))
    p.append(text(715, 186, "Для C_L = 12 пФ, Cs = 4 пФ → C = 16 пФ", size=9.5, color=FIELD, bold=True))

    # Блок MCO тактування (Nucleo)
    p.append(rect(550, 225, 330, 165, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8))
    p.append(text(715, 252, "Альтернатива: тактування MCO (Nucleo)", size=11.5, color=NEG, bold=True))
    p.append(text(715, 276, "Зневаджувач ST-Link генерує 8 МГц", size=10, color=INK))
    p.append(text(715, 296, "і подає його на вивід OSC_IN цільового МК.", size=9.5, color=MUTED))
    p.append(text(715, 324, "Вивід OSC_OUT лишається вільним (NC).", size=9.5, color=MUTED))
    p.append(text(715, 348, "Економія вартості: мінус один кварц.", size=9.5, color=FIELD))
    p.append(text(715, 370, "Мінус: без USB-відладчика такт зникає.", size=9.5, color=POS))

    render(os.path.join(OUT, "pierce-and-cl.svg"), W, H, *p,
           title="Генератор Пірса, розрахунок ємностей CL та альтернативне тактування MCO від зневаджувача")


# ── 5. pin-header-traps: Пастки штирьових роз'ємів та імпульсні перешкоди ───────
def fig_pin_header_traps():
    W, H = 920, 420
    p = []

    # Ліва частина: Плата розробника
    p.append(rect(40, 50, 220, 320, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=8))
    p.append(text(150, 80, "Плата розробника", size=13, color=INK, bold=True))

    # LDO на платі
    p.append(rect(60, 110, 180, 60, fill="#fff1f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(150, 134, "Вбудований LDO", size=11, color=POS, bold=True))
    p.append(text(150, 154, "3.3V (I_max ≈ 150–300 мА)", size=9.5, color=INK))

    # Штирі роз'єму
    p.append(circle(240, 200, 6, fill="#f59e0b", stroke=INK, sw=1.2))
    p.append(text(220, 195, "Pin 3.3V", size=9.5, color=INK, bold=True, anchor="end"))

    p.append(circle(240, 270, 6, fill="#3b82f6", stroke=INK, sw=1.2))
    p.append(text(220, 265, "Pin GND", size=9.5, color=INK, bold=True, anchor="end"))

    # Центральна частина: Паразитні елементи дротів і breadboard
    p.append(rect(310, 80, 260, 260, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(440, 105, "Паразити з'єднання (Dupont + макетка)", size=10.5, color=NEG, bold=True))

    # Лінія живлення з паразитами
    p.append(line(240, 200, 330, 200, color=POS, sw=2))
    # Резистор R_contact
    p.append(rect(330, 190, 45, 20, fill="#ffffff", stroke=POS, sw=1.2, rx=2))
    p.append(text(352, 204, "R_конт", size=9, color=POS))
    # Індуктивність L_wire
    p.append(rect(390, 190, 45, 20, fill="#ffffff", stroke=POS, sw=1.2, rx=2))
    p.append(text(412, 204, "L_дроту", size=9, color=POS))
    p.append(line(435, 200, 570, 200, color=POS, sw=2))

    # Лінія землі з паразитами
    p.append(line(240, 270, 330, 270, color=NEG, sw=2))
    # R_gnd
    p.append(rect(330, 260, 45, 20, fill="#ffffff", stroke=NEG, sw=1.2, rx=2))
    p.append(text(352, 274, "R_конт", size=9, color=NEG))
    # L_gnd
    p.append(rect(390, 260, 45, 20, fill="#ffffff", stroke=NEG, sw=1.2, rx=2))
    p.append(text(412, 274, "L_дроту", size=9, color=NEG))
    p.append(line(435, 270, 570, 270, color=NEG, sw=2))

    # Міжвивідна ємність
    p.append(line(490, 200, 490, 225, color=LINE, sw=1.2))
    p.append(line(490, 270, 490, 245, color=LINE, sw=1.2))
    p.append(rect(475, 225, 30, 20, fill="#ffffff", stroke=MUTED, sw=1.2, rx=2))
    p.append(text(490, 239, "C_пар", size=9, color=MUTED))

    p.append(text(440, 310, "R_конт ≈ 20–100 мОм", size=9.5, color=MUTED))
    p.append(text(440, 326, "L_дроту ≈ 150 нГн (20 см дріт)", size=9.5, color=MUTED))

    # Права частина: Навантаження та аварійний сплеск
    p.append(rect(610, 50, 270, 320, fill="#fef2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(745, 80, "Потужне навантаження", size=12, color=POS, bold=True))
    p.append(text(745, 100, "(Wi-Fi / 4G модем / Сервопривід)", size=10, color=INK))

    p.append(rect(630, 120, 230, 75, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(text(745, 142, "Сплеск струму ΔI = 500 мА", size=10.5, color=POS, bold=True))
    p.append(text(745, 160, "Час фронту Δt = 10 нс", size=9.5, color=INK))
    p.append(text(745, 178, "di/dt = 50 000 000 А/с", size=9.5, color=POS, bold=True))

    p.append(rect(630, 210, 230, 140, fill="#ffffff", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(745, 232, "Наслідки для плати:", size=11, color="#b45309", bold=True))
    p.append(text(745, 254, "ΔV_L = L · (di/dt) ≈ 7.5 В", size=10.5, color=POS, bold=True))
    p.append(text(745, 276, "Індуктивний підскок / провал", size=9.5, color=INK))
    p.append(text(745, 298, "Ground Bounce (перекіс нуля)", size=9.5, color=POS))
    p.append(text(745, 320, "Провал 3.3V < 2.7V → Brownout Reset!", size=9.5, color=POS, bold=True))
    p.append(text(745, 338, "МК циклічно перезавантажується", size=9, color=MUTED))

    p.append(arrow(570, 200, 610, 200, color=POS, sw=2))
    p.append(arrow(570, 270, 610, 270, color=NEG, sw=2))

    render(os.path.join(OUT, "pin-header-traps.svg"), W, H, *p,
           title="Пастки штирьових роз'ємів: індуктивність дротів, падіння напруги та перевантаження LDO")


if __name__ == "__main__":
    fig_board_anatomy()
    fig_swd_breakoff()
    fig_power_tree()
    fig_pierce_and_cl()
    fig_pin_header_traps()
    print("OK: all figures generated in", OUT)
