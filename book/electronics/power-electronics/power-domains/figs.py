# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ORANGE = "#d97706"
PURPLE = "#7c3aed"
TEAL   = "#0d9488"


# ── 1. Архітектура силових доменів мікроконтролера ──────────────────────────
def fig_mcu_power_domains_arch():
    W, H = 880, 520
    p = []

    # Загальний контур кристала SoC / мікроконтролера
    p.append(rect(30, 40, 820, 455, fill="#fafbfc", stroke="#94a3b8", sw=2, rx=10))
    p.append(text(440, 64, "Архітектура розділених силових доменів мікроконтролера", size=15, bold=True))

    # Зовнішні входи живлення (ліворуч)
    # VDD 3.3 В
    p.append(rect(45, 100, 115, 42, fill="#f0fdf4", stroke=FIELD, sw=1.6))
    p.append(text(102, 118, "VDD (3.3 В)", size=12, color=FIELD, bold=True))
    p.append(text(102, 134, "головна шина", size=10, color=MUTED))

    # VDDA 3.3 В
    p.append(rect(45, 230, 115, 42, fill="#fdf4ff", stroke=PURPLE, sw=1.6))
    p.append(text(102, 248, "VDDA (3.3 В)", size=12, color=PURPLE, bold=True))
    p.append(text(102, 264, "аналогова шина", size=10, color=MUTED))

    # VBAT 3.0 В
    p.append(rect(45, 335, 115, 42, fill="#fffbeb", stroke=ORANGE, sw=1.6))
    p.append(text(102, 353, "VBAT (3.0 В)", size=12, color=ORANGE, bold=True))
    p.append(text(102, 369, "батарейка CR2032", size=10, color=MUTED))

    # VDDIO2 1.8 В
    p.append(rect(45, 425, 115, 42, fill="#ecfeff", stroke=TEAL, sw=1.6))
    p.append(text(102, 443, "VDDIO2 (1.8 В)", size=12, color=TEAL, bold=True))
    p.append(text(102, 459, "зовнішня шина", size=10, color=MUTED))

    # Внутрішній перетворювач (Step-down Buck / LDO)
    p.append(rect(190, 95, 135, 65, fill="#eff6ff", stroke=NEG, sw=1.8))
    p.append(text(257, 118, "Вбудований Buck / LDO", size=11, color=NEG, bold=True))
    p.append(text(257, 134, "ККД 85–92%", size=10, color=MUTED))
    p.append(text(257, 149, "3.3 В → 1.0 В", size=10, color=NEG, bold=True))

    p.append(arrow(160, 121, 190, 121, color=FIELD, sw=2))

    # Домен 1: Цифрове ядро V_CORE (1.0 В)
    p.append(rect(365, 85, 230, 145, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    p.append(text(480, 108, "Домен ядра V_CORE (1.0 В)", size=13, color=NEG, bold=True))
    p.append(fitbox(380, 122, 95, 40, "CPU Core\nCortex-M", size=10, fill=BG, stroke=NEG, color=INK, bold=True))
    p.append(fitbox(485, 122, 95, 40, "SRAM пам'ять\nі кеш", size=10, fill=BG, stroke=NEG, color=INK, bold=True))
    p.append(fitbox(380, 172, 200, 46, "Швидкісна цифрова логіка\nP_dyn = C · V² · f мінімальна", size=10, fill="#dbeafe", stroke=NEG, color=NEG, bold=True))

    p.append(arrow(325, 121, 365, 121, color=NEG, sw=2.2))

    # Домен 2: Головна периферія та GPIO V_DD (3.3 В)
    p.append(rect(635, 85, 195, 145, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    p.append(text(732, 108, "Домен периферії VDD", size=13, color=FIELD, bold=True))
    p.append(fitbox(650, 122, 165, 38, "GPIO Порти A–F\n(буфери 3.3 В)", size=10, fill=BG, stroke=FIELD, color=INK, bold=True))
    p.append(fitbox(650, 168, 165, 50, "Таймери, SPI, I2C, UART\nСумісність із зовнішніми IC", size=10, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True))

    # Межа між V_CORE та V_DD: Level Shifter та Isolation
    p.append(line(595, 157, 635, 157, color=LINE, sw=1.6))
    p.append(fitbox(588, 138, 55, 36, "LS / ISO\nвентилі", size=9, fill="#fff", stroke=INK, color=INK, bold=True))

    # Домен 3: Аналоговий домен V_DDA / V_SSA
    p.append(rect(365, 245, 230, 95, fill="#fdf4ff", stroke=PURPLE, sw=2, rx=8))
    p.append(text(480, 268, "Аналоговий домен VDDA / VSSA", size=12, color=PURPLE, bold=True))
    p.append(fitbox(380, 280, 95, 48, "16-біт SAR АЦП\nі ЦАП", size=10, fill=BG, stroke=PURPLE, color=INK, bold=True))
    p.append(fitbox(485, 280, 95, 48, "Опори VREF,\nкомпаратори", size=10, fill=BG, stroke=PURPLE, color=INK, bold=True))

    p.append(arrow(160, 251, 365, 251, color=PURPLE, sw=2))
    p.append(text(260, 243, "окремий LC-фільтр", size=10, color=PURPLE))

    # Домен 4: Резервне живлення V_BAT
    p.append(rect(365, 355, 230, 60, fill="#fffbeb", stroke=ORANGE, sw=2, rx=8))
    p.append(text(480, 376, "Домен бекапу VBAT (3.0 В)", size=12, color=ORANGE, bold=True))
    p.append(fitbox(380, 385, 200, 24, "RTC + LSE 32 кГц + Backup SRAM", size=9, fill=BG, stroke=ORANGE, color=INK, bold=True))

    p.append(arrow(160, 356, 365, 375, color=ORANGE, sw=1.8))
    p.append(arrow(140, 142, 365, 365, color=FIELD, sw=1.5))
    p.append(text(250, 393, "автоперемикач живлення (Power Switch)", size=9, color=ORANGE))

    # Домен 5: Низьковольтні I/O V_DDIO2 (1.8 В)
    p.append(rect(635, 245, 195, 95, fill="#ecfeff", stroke=TEAL, sw=2, rx=8))
    p.append(text(732, 268, "Домен VDDIO2 (1.8 В)", size=12, color=TEAL, bold=True))
    p.append(fitbox(650, 280, 165, 48, "Порт G: швидкісні датчики,\nLPDDR / MIPI інтерфейси", size=10, fill=BG, stroke=TEAL, color=INK, bold=True))

    p.append(arrow(160, 446, 635, 310, color=TEAL, sw=1.8))

    return render(os.path.join(OUT, "mcu-power-domains-arch.svg"), W, H, *p)


# ── 2. Силові ключі Header PMOS vs Footer NMOS (Power Gating) ───────────────
def fig_power_gating_switches():
    W, H = 880, 440
    p = []

    # Ліва панель: Header Switch (PMOS)
    p.append(rect(30, 35, 395, 380, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=8))
    p.append(text(227, 62, "Header Switch: PMOS на шині живлення", size=13, color=POS, bold=True))

    # Рейка VDD
    p.append(line(50, 95, 400, 95, color=POS, sw=3))
    p.append(text(70, 86, "Головна шина VDD (1.0 В)", size=11, color=POS, bold=True))

    # PMOS ключ
    p.append(rect(155, 125, 145, 55, fill="#fef2f2", stroke=POS, sw=1.8, rx=6))
    p.append(text(227, 146, "PMOS Ключ (Header)", size=11, color=POS, bold=True))
    p.append(text(227, 166, "Керування: SLEEP = 1 → OFF", size=9, color=MUTED))

    p.append(line(227, 95, 227, 125, color=POS, sw=2.2))
    p.append(line(227, 180, 227, 210, color=NEG, sw=2.2))

    # Віртуальна шина VDD_VIRTUAL
    p.append(line(80, 210, 375, 210, color=NEG, sw=2.2, dash="4,3"))
    p.append(text(227, 202, "Віртуальна шина VDD_VIRTUAL", size=10, color=NEG, bold=True))

    # Блок логіки
    p.append(rect(110, 230, 235, 75, fill="#eff6ff", stroke=NEG, sw=1.6, rx=6))
    p.append(text(227, 255, "Вимкнений функціональний блок", size=11, color=INK, bold=True))
    p.append(text(227, 275, "(CPU / Crypto / RAM)", size=10, color=MUTED))
    p.append(text(227, 293, "Струм витоку I_leak = 0", size=10, color=FIELD, bold=True))

    # Земля VSS
    p.append(line(227, 305, 227, 340, color=LINE, sw=2.2))
    p.append(line(80, 340, 375, 340, color=LINE, sw=3))
    p.append(text(227, 360, "Справжня земля VSS (0 В збережено)", size=10, color=FIELD, bold=True))

    # Перевага/недолік
    p.append(fitbox(50, 375, 355, 30, "Плюс: спільна земля не зміщується; Мінус: більша площа PMOS", size=9, fill="#fff", stroke="#94a3b8", color=INK))


    # Права панель: Footer Switch (NMOS)
    p.append(rect(455, 35, 395, 380, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=8))
    p.append(text(652, 62, "Footer Switch: NMOS на шині землі", size=13, color=NEG, bold=True))

    # Рейка VDD
    p.append(line(475, 95, 825, 95, color=POS, sw=3))
    p.append(text(500, 86, "Головна шина VDD (1.0 В)", size=11, color=POS, bold=True))

    p.append(line(652, 95, 652, 130, color=POS, sw=2.2))

    # Блок логіки
    p.append(rect(535, 130, 235, 75, fill="#eff6ff", stroke=NEG, sw=1.6, rx=6))
    p.append(text(652, 155, "Вимкнений функціональний блок", size=11, color=INK, bold=True))
    p.append(text(652, 175, "(CPU / Crypto / RAM)", size=10, color=MUTED))
    p.append(text(652, 193, "Струм витоку I_leak = 0", size=10, color=FIELD, bold=True))

    # Віртуальна земля VSS_VIRTUAL
    p.append(line(652, 205, 652, 230, color=ORANGE, sw=2.2))
    p.append(line(505, 230, 800, 230, color=ORANGE, sw=2.2, dash="4,3"))
    p.append(text(652, 222, "Віртуальна земля VSS_VIRTUAL (+ΔV)", size=10, color=ORANGE, bold=True))

    # NMOS ключ
    p.append(rect(580, 250, 145, 55, fill="#eef2ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(652, 271, "NMOS Ключ (Footer)", size=11, color=NEG, bold=True))
    p.append(text(652, 291, "Керування: SLEEP_N = 0 → OFF", size=9, color=MUTED))

    p.append(line(652, 305, 652, 340, color=LINE, sw=2.2))
    p.append(line(475, 340, 825, 340, color=LINE, sw=3))
    p.append(text(652, 360, "Справжня земля VSS (0 В)", size=10, color=LINE, bold=True))

    # Перевага/недолік
    p.append(fitbox(475, 375, 355, 30, "Плюс: компактний NMOS (рухливість e⁻ вища); Мінус: плаває земля", size=9, fill="#fff", stroke="#94a3b8", color=INK))

    return render(os.path.join(OUT, "power-gating-switches.svg"), W, H, *p)


# ── 3. Транслятори рівнів (Level Shifters) та ізоляційні вентилі (Isolation) ───
def fig_level_shifter_and_isolation():
    W, H = 880, 440
    p = []

    # Ліва половина: Level Shifter (1.0 В -> 3.3 В)
    p.append(rect(30, 35, 395, 380, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=8))
    p.append(text(227, 62, "Трансляція рівнів (1.0 В → 3.3 В)", size=13, color=PURPLE, bold=True))

    # Домен 1.0 В (Ядро)
    p.append(rect(50, 95, 120, 100, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(110, 118, "Домен 1.0 В", size=11, color=NEG, bold=True))
    p.append(text(110, 142, "Логічна «1»", size=10))
    p.append(text(110, 162, "= 1.0 В", size=12, color=NEG, bold=True))

    # Домен 3.3 В без LS - Помилка
    p.append(rect(230, 95, 175, 100, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(317, 118, "Без транслятора (3.3 В)", size=11, color=POS, bold=True))
    p.append(text(317, 138, "PMOS не закривається:", size=9, color=POS))
    p.append(text(317, 154, "V_GS = 1.0 - 3.3 = -2.3 В", size=9, color=POS, bold=True))
    p.append(text(317, 175, "Наскрізний струм (Crowbar)!", size=9, color=POS, bold=True))

    p.append(arrow(170, 145, 230, 145, color=POS, sw=2))

    # З диференційним транслятором рівнів
    p.append(rect(50, 230, 355, 165, fill="#f5f3ff", stroke=PURPLE, sw=1.8, rx=6))
    p.append(text(227, 254, "Диференційний транслятор рівнів (Level Shifter)", size=11, color=PURPLE, bold=True))

    p.append(fitbox(70, 275, 110, 50, "Вхід:\n0 В / 1.0 В", size=10, fill=BG, stroke=NEG, color=NEG, bold=True))
    p.append(arrow(180, 300, 220, 300, color=PURPLE, sw=2))
    p.append(fitbox(220, 275, 80, 50, "Cross-coupled\nPMOS пара", size=9, fill="#ede9fe", stroke=PURPLE, color=PURPLE, bold=True))
    p.append(arrow(300, 300, 335, 300, color=PURPLE, sw=2))
    p.append(fitbox(335, 275, 55, 50, "Вихід:\n0..3.3 В", size=10, fill=BG, stroke=FIELD, color=FIELD, bold=True))
    p.append(text(227, 360, "Повний розмах 0..3.3 В без наскрізних витоків", size=10, color=FIELD, bold=True))


    # Права половина: Ізоляція вимкненого домену (Isolation Cell)
    p.append(rect(455, 35, 395, 380, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=8))
    p.append(text(652, 62, "Ізоляція вимкненого домену (Isolation Cell)", size=13, color=TEAL, bold=True))

    # Вимкнений блок
    p.append(rect(475, 95, 140, 120, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(545, 120, "Вимкнений домен", size=11, color=MUTED, bold=True))
    p.append(text(545, 140, "VDD_OFF = 0 В", size=11, color=POS, bold=True))
    p.append(text(545, 168, "Плаваючий вихід", size=10, color=MUTED))
    p.append(text(545, 188, "(Z-стан / шум)", size=10, color=MUTED))

    # Активний блок праворуч
    p.append(rect(715, 95, 120, 120, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(775, 120, "Активний домен", size=11, color=FIELD, bold=True))
    p.append(text(775, 140, "VDD_ON = 3.3 В", size=11, color=FIELD, bold=True))
    p.append(text(775, 168, "Вхідний буфер", size=10))
    p.append(text(775, 188, "очікує 0 або 1", size=10, color=MUTED))

    # Ізоляційний вентиль AND між ними
    p.append(rect(515, 245, 275, 150, fill="#ecfeff", stroke=TEAL, sw=1.8, rx=6))
    p.append(text(652, 268, "Ізоляційний вентиль AND (Clamp to 0)", size=11, color=TEAL, bold=True))

    p.append(fitbox(535, 290, 85, 40, "Плаваючий\nсигнал X", size=9, fill="#f1f5f9", stroke="#94a3b8", color=MUTED))
    p.append(arrow(620, 310, 645, 310, color=TEAL, sw=1.8))
    p.append(fitbox(645, 285, 60, 50, "AND\nвентиль", size=10, fill=BG, stroke=TEAL, color=TEAL, bold=True))
    p.append(arrow(705, 310, 735, 310, color=FIELD, sw=2))
    p.append(fitbox(735, 290, 45, 40, "Чистий\n0 В", size=10, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True))

    # Сигнал керування ISO_ENABLE
    p.append(arrow(675, 380, 675, 335, color=POS, sw=2))
    p.append(text(675, 395, "ISO_ENABLE = 0 (блокування)", size=9, color=POS, bold=True))

    return render(os.path.join(OUT, "level-shifter-and-isolation.svg"), W, H, *p)


# ── 4. Секвенування живлення та захист від Latch-up ──────────────────────────
def fig_power_sequencing_latchup():
    W, H = 880, 450
    p = []

    # Ліва половина: Часова діаграма коректного секвенування
    p.append(rect(30, 35, 420, 395, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=8))
    p.append(text(240, 62, "Правильне секвенування подачі живлення", size=13, color=FIELD, bold=True))

    ox, oy = 80, 370
    p.append(arrow(ox, oy, ox + 350, oy, color=INK, sw=1.6))
    p.append(text(ox + 350, oy + 18, "час", size=11, italic=True))

    # Сигнали: VDD 3.3 В -> VDDA -> VCORE -> RESET_N
    # 1. VDD (3.3 В)
    p.append(text(ox - 10, 115, "VDD (3.3 В)", size=10, color=FIELD, bold=True, anchor="end"))
    p.append(line(ox, 130, ox + 40, 130, color=FIELD, sw=2))
    p.append(line(ox + 40, 130, ox + 100, 105, color=FIELD, sw=2.2))
    p.append(line(ox + 100, 105, ox + 330, 105, color=FIELD, sw=2.2))

    # 2. VDDA (3.3 В)
    p.append(text(ox - 10, 175, "VDDA (3.3 В)", size=10, color=PURPLE, bold=True, anchor="end"))
    p.append(line(ox, 190, ox + 80, 190, color=PURPLE, sw=2))
    p.append(line(ox + 80, 190, ox + 140, 165, color=PURPLE, sw=2.2))
    p.append(line(ox + 140, 165, ox + 330, 165, color=PURPLE, sw=2.2))

    # 3. VCORE (1.0 В)
    p.append(text(ox - 10, 235, "VCORE (1.0 В)", size=10, color=NEG, bold=True, anchor="end"))
    p.append(line(ox, 250, ox + 140, 250, color=NEG, sw=2))
    p.append(line(ox + 140, 250, ox + 190, 225, color=NEG, sw=2.2))
    p.append(line(ox + 190, 225, ox + 330, 225, color=NEG, sw=2.2))

    # 4. RESET_N (Скидання знято)
    p.append(text(ox - 10, 295, "RESET_N", size=10, color=POS, bold=True, anchor="end"))
    p.append(line(ox, 310, ox + 240, 310, color=POS, sw=2))
    p.append(line(ox + 240, 310, ox + 255, 285, color=POS, sw=2.2))
    p.append(line(ox + 255, 285, ox + 330, 285, color=POS, sw=2.2))

    # Вертикальні лінії послідовності
    p.append(line(ox + 100, 105, ox + 100, oy, color=FIELD, sw=1, dash="3,3"))
    p.append(line(ox + 190, 225, ox + 190, oy, color=NEG, sw=1, dash="3,3"))
    p.append(line(ox + 255, 285, ox + 255, oy, color=POS, sw=1, dash="3,3"))

    p.append(text(ox + 100, oy - 10, "1. VDD OK", size=9, color=FIELD))
    p.append(text(ox + 190, oy - 10, "2. VCORE OK", size=9, color=NEG))
    p.append(text(ox + 265, oy - 10, "3. Старт CPU", size=9, color=POS))

    p.append(fitbox(50, 385, 380, 35, "Правило: напруга на виводах I/O не повинна з'являтися раніше за живлення домену", size=9, fill="#fff", stroke="#94a3b8", color=INK))


    # Права половина: Фізика тиристорного засуву (CMOS Latch-up)
    p.append(rect(475, 35, 375, 395, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=8))
    p.append(text(662, 62, "Механізм тиристорної засувки (Latch-up)", size=13, color=POS, bold=True))

    # Схема паразитного SCR (PNP + NPN)
    p.append(rect(500, 95, 325, 140, fill="#fef2f2", stroke=POS, sw=1.8, rx=6))
    p.append(text(662, 118, "Паразитна 4-шарова p-n-p-n структура (SCR)", size=11, color=POS, bold=True))

    p.append(fitbox(520, 135, 120, 45, "Паразитний PNP\n(Q1 у N-Well)", size=9, fill=BG, stroke=POS, color=POS, bold=True))
    p.append(fitbox(685, 135, 120, 45, "Паразитний NPN\n(Q2 у P-Substrate)", size=9, fill=BG, stroke=POS, color=POS, bold=True))

    p.append(arrow(640, 150, 685, 150, color=POS, sw=2))
    p.append(arrow(685, 165, 640, 165, color=POS, sw=2))
    p.append(text(662, 205, "Регенеративний зв'язок: I_C1 годує I_B2, I_C2 годує I_B1", size=9, color=POS, bold=True))
    p.append(text(662, 222, "Коротке замикання VDD → VSS через кристал!", size=10, color=POS, bold=True))

    # Причина виникнення
    p.append(rect(500, 250, 325, 120, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(662, 272, "Як виникає пусковий струм тригера:", size=11, color=NEG, bold=True))
    p.append(fitbox(515, 285, 295, 75, "1. На вхід I/O подано 3.3 В, коли VDD = 0 В\n2. Пряме зміщення ESD-діода або p-n переходу\n3. Інжекція дірок/електронів відкриває базу Q1/Q2\n4. Струм зростає до амперів → тепловий пробій", size=9, fill=BG, stroke=NEG, color=INK))

    p.append(fitbox(500, 385, 325, 35, "Захист: правильний порядок старту, захисні резистори та guard rings", size=9, fill="#fff", stroke=FIELD, color=FIELD, bold=True))

    return render(os.path.join(OUT, "power-sequencing-latchup.svg"), W, H, *p)


if __name__ == "__main__":
    fig_mcu_power_domains_arch()
    fig_power_gating_switches()
    fig_level_shifter_and_isolation()
    fig_power_sequencing_latchup()
    print("OK figs generated in:", OUT)
