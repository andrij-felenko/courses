# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. scaffolding-vs-custom: анатомія девборди проти власної плати ──────────
def fig_scaffolding_vs_custom():
    W, H = 820, 360
    p = []
    
    # Ліва половина: Девборда
    p.append(rect(30, 40, 360, 290, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(210, 65, "Оціночна девборда (STM32 Nucleo / DevKit)", size=12, color=INK, bold=True))
    
    # Блок «Риштування»
    p.append(rect(45, 85, 330, 130, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    p.append(text(210, 105, "Інженерне риштування (зникає на своїй платі)", size=11, color=POS, bold=True))
    
    p.append(fitbox(55, 118, 150, 40, "ST-Link / CMSIS-DAP\n(чип-відлагоджувач)", size=10, fill="#ffffff", stroke=POS, sw=1.2))
    p.append(fitbox(215, 118, 150, 40, "USB-UART міст\n(віртуальний COM-порт)", size=10, fill="#ffffff", stroke=POS, sw=1.2))
    p.append(fitbox(55, 165, 150, 40, "LDO 5V → 3.3V (500mA)\n+ автоскидання DTR/RTS", size=10, fill="#ffffff", stroke=POS, sw=1.2))
    p.append(fitbox(215, 165, 150, 40, "Світлодіоди користувача\n+ тактовий кварц 8 МГц", size=10, fill="#ffffff", stroke=POS, sw=1.2))
    
    # Цільовий МК на девборді
    p.append(fitbox(110, 225, 200, 42, "Цільовий мікроконтролер\n(Cortex-M / ESP32)", size=11, fill="#eafaf0", stroke=FIELD, sw=1.5, bold=True))
    
    # Гребінки штирів
    p.append(fitbox(45, 280, 330, 35, "Штирьові роз'єми 2.54 мм (Arduino / Morpho)\nзручні для щупів осцилографа й DuPont-дротів", size=9.5, fill="#ffffff", stroke=MUTED, sw=1.2))
    
    # Права половина: Власна плата
    p.append(rect(430, 40, 360, 290, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(610, 65, "Власна цільова плата (Custom PCB)", size=12, color=FIELD, bold=True))
    
    # Вузли власної плати
    p.append(fitbox(445, 85, 160, 45, "Джерело живлення\n(Li-Po АКБ або 24V DC-DC)", size=10, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(fitbox(615, 85, 160, 45, "Сенсори / Актюатори\n(робоче навантаження)", size=10, fill="#ffffff", stroke=MUTED, sw=1.2))
    
    p.append(fitbox(510, 150, 200, 55, "Цільовий МК\n(чистий кремній без обв'язки)\nQFN / BGA без світлодіодів", size=11, fill="#eafaf0", stroke=FIELD, sw=1.5, bold=True))
    
    p.append(fitbox(445, 225, 160, 45, "Мініатюрний SWD роз'єм\n(Cortex 10-pin / Tag-Connect)", size=10, fill="#ffffff", stroke=NEG, sw=1.2))
    p.append(fitbox(615, 225, 160, 45, "Контрольні площадки (TP)\nпід голчасті щупи", size=10, fill="#ffffff", stroke=NEG, sw=1.2))
    
    p.append(fitbox(445, 280, 330, 35, "Висока щільність SMD 0402: немає штирів 2.54 мм,\nнемає вбудованого USB-UART, немає надлишкових LED", size=9.5, fill="#fdecea", stroke=POS, sw=1.2))
    
    render(os.path.join(OUT, "scaffolding-vs-custom.svg"), W, H, *p,
           title="Анатомія девборди проти власної плати")


# ── 2. swd-connector-vtref: лінії SWD та рівні напруг ───────────────────────
def fig_swd_connector_vtref():
    W, H = 820, 360
    p = []
    
    # Зонд ліворуч
    p.append(rect(40, 40, 200, 280, fill="#eef3ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(140, 70, "Зовнішній зонд", size=13, color=NEG, bold=True))
    p.append(text(140, 92, "(ST-Link V3 / J-Link)", size=11, color=MUTED))
    p.append(fitbox(55, 120, 170, 50, "Двонапрямні транслятори\nрівнів (Level Shifter)", size=10, fill="#ffffff", stroke=NEG, sw=1.2))
    p.append(fitbox(55, 190, 170, 50, "Генератор SWD такту\nта логіка скидання", size=10, fill="#ffffff", stroke=NEG, sw=1.2))
    p.append(text(140, 290, "Живиться від хоста (5V USB)", size=10, color=MUTED))
    
    # Цільовий МК праворуч
    p.append(rect(580, 40, 200, 280, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(680, 70, "Цільовий МК на платі", size=13, color=FIELD, bold=True))
    p.append(text(680, 92, "Живлення VDD (1.8V ... 3.3V)", size=10.5, color=FIELD, bold=True))
    p.append(fitbox(595, 120, 170, 50, "SWD периферія ядра\n(Cortex-M DP / AP)", size=10, fill="#ffffff", stroke=FIELD, sw=1.2))
    p.append(fitbox(595, 190, 170, 50, "Апаратне скидання\n(NRST з RC-ланцюжком)", size=10, fill="#ffffff", stroke=FIELD, sw=1.2))
    p.append(text(680, 290, "Автономне живлення", size=10, color=MUTED))
    
    # Лінії зв'язку між зондом і платою
    lines_info = [
        (65, "VTref (Target VDD)", "Опора транслятора: без неї зонд видає 0V або палить МК", POS),
        (115, "SWCLK", "Тактовий сигнал (з резистором 22-47 Ом від дзвіну)", INK),
        (165, "SWDIO", "Двонапрямні дані (критична ємність траси)", INK),
        (215, "nRESET", "Апаратне скидання (Connect Under Reset при аварії)", NEG),
        (265, "GND", "Спільна земля (обов'язковий зворотний шлях струму)", INK)
    ]
    
    for y_rel, label, desc, col in lines_info:
        y = 35 + y_rel
        p.append(line(240, y, 580, y, color=col, sw=2))
        p.append(text(410, y - 7, label, size=11, color=col, bold=True))
        p.append(text(410, y + 15, desc, size=9.5, color=MUTED))
    
    render(os.path.join(OUT, "swd-connector-vtref.svg"), W, H, *p,
           title="Інтерфейс SWD: чому чотирьох ліній замало")


# ── 3. autoreset-transistor-logic: автоскидання через DTR/RTS ────────────────
def fig_autoreset_transistor_logic():
    W, H = 820, 320
    p = []
    
    # Ліворуч: сигнали від USB-UART
    p.append(fitbox(40, 80, 150, 50, "USB-UART міст\n(CP2102 / CH340)", size=11, fill="#eef3ff", stroke=NEG, sw=1.5, bold=True))
    p.append(text(115, 170, "DTR (Data Terminal Ready)", size=10, color=INK))
    p.append(text(115, 230, "RTS (Request To Send)", size=10, color=INK))
    
    # Центр: Транзисторна схема (міст на двох NPN)
    p.append(rect(230, 60, 280, 210, fill="#fdf6e3", stroke="#b8860b", sw=1.5, rx=8))
    p.append(text(370, 85, "Схема автоскидання (Auto-Program)", size=11.5, color="#b8860b", bold=True))
    
    p.append(fitbox(250, 110, 110, 45, "Q1 (NPN)\nБаза: RTS\nКолектор: EN", size=9.5, fill="#ffffff", stroke="#b8860b", sw=1.2))
    p.append(fitbox(380, 110, 110, 45, "Q2 (NPN)\nБаза: DTR\nКолектор: IO0", size=9.5, fill="#ffffff", stroke="#b8860b", sw=1.2))
    
    # Логічна таблиця
    p.append(rect(250, 170, 240, 85, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(text(370, 188, "Стани керування:", size=9.5, color=MUTED, bold=True))
    p.append(text(370, 206, "DTR=1, RTS=0 → EN=0, IO0=1 (Скидання)", size=9.5, color=INK))
    p.append(text(370, 224, "DTR=0, RTS=1 → EN=1, IO0=0 (Вхід у бут)", size=9.5, color=POS, bold=True))
    p.append(text(370, 242, "DTR=1, RTS=1 → EN=1, IO0=1 (Робочий хід)", size=9.5, color=FIELD))
    
    # Стрілки до схеми
    p.append(arrow(190, 130, 250, 130, color=INK, sw=1.5))
    p.append(arrow(190, 210, 250, 210, color=INK, sw=1.5))
    
    # Праворуч: Цільовий МК
    p.append(rect(550, 60, 230, 210, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(665, 85, "Мікроконтролер (ESP32)", size=12, color=FIELD, bold=True))
    
    p.append(fitbox(570, 110, 190, 45, "EN / NRST (Скидання)\nпідтягнуто до VDD через 10 кОм", size=9.5, fill="#ffffff", stroke=FIELD, sw=1.2))
    p.append(fitbox(570, 175, 190, 45, "GPIO0 / BOOT0 (Режим)\n0: ROM Bootloader, 1: Flash", size=9.5, fill="#ffffff", stroke=FIELD, sw=1.2))
    
    p.append(arrow(510, 132, 570, 132, color=POS, sw=1.8))
    p.append(arrow(510, 197, 570, 197, color=POS, sw=1.8))
    
    p.append(text(W / 2, H - 18, "На власній платі цієї схеми немає: прошивка вимагає кнопок або стенду з голками", size=10.5, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "autoreset-transistor-logic.svg"), W, H, *p,
           title="Схема автоскидання: як DTR/RTS керують завантажувачем")


# ── 4. power-profiles-comparison: порівняння профілів живлення ───────────────
def fig_power_profiles_comparison():
    W, H = 820, 320
    p = []
    
    # 3 блоки порівняння
    col_w = 230
    gap = 25
    x0 = 40
    
    # 1. USB на девборді
    x1 = x0
    p.append(rect(x1, 50, col_w, 240, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(x1 + col_w / 2, 75, "1. Девборда: USB + LDO", size=11.5, color=FIELD, bold=True))
    p.append(fitbox(x1 + 15, 95, col_w - 30, 45, "Вхід 5.0V від USB\n→ LDO 3.3V (до 800 мА)", size=10, fill="#ffffff", stroke=FIELD, sw=1.2))
    p.append(fitbox(x1 + 15, 150, col_w - 30, 60, "• Чиста напруга без пульсацій\n• Величезний запас струму\n• Власний струм 20-50 мА\n  (не критичний для столу)", size=9.5, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(text(x1 + col_w / 2, 245, "Комфортно для коду,", size=10, color=FIELD, bold=True))
    p.append(text(x1 + col_w / 2, 265, "ховає проблеми живлення", size=9.5, color=MUTED))
    
    # 2. Li-Po акумулятор
    x2 = x1 + col_w + gap
    p.append(rect(x2, 50, col_w, 240, fill="#fdf6e3", stroke="#b8860b", sw=1.5, rx=8))
    p.append(text(x2 + col_w / 2, 75, "2. АКБ: Li-Po (3.0...4.2V)", size=11.5, color="#b8860b", bold=True))
    p.append(fitbox(x2 + 15, 95, col_w - 30, 45, "LDO з малим падінням (LDO)\nабо Buck-Boost 3.3V", size=10, fill="#ffffff", stroke="#b8860b", sw=1.2))
    p.append(fitbox(x2 + 15, 150, col_w - 30, 60, "• Просідання при сплесках RF\n• Вимога Deep Sleep < 20 мкА\n• Висячі ніжки їдять міліампери\n• Ризик Brown-Out Reset", size=9.5, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(text(x2 + col_w / 2, 245, "Вимагає керування сном", size=10, color="#b8860b", bold=True))
    p.append(text(x2 + col_w / 2, 265, "і паркування виводів", size=9.5, color=MUTED))
    
    # 3. Промислові 24V
    x3 = x2 + col_w + gap
    p.append(rect(x3, 50, col_w, 240, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    p.append(text(x3 + col_w / 2, 75, "3. Промислові: 24V DC-DC", size=11.5, color=POS, bold=True))
    p.append(fitbox(x3 + 15, 95, col_w - 30, 45, "Імпульсний Step-Down\n(Step-Down Buck 24V→3.3V)", size=10, fill="#ffffff", stroke=POS, sw=1.2))
    p.append(fitbox(x3 + 15, 150, col_w - 30, 60, "• Пульсації 50-100 мВ (шум АЦП)\n• Кидки напруги при гарячій пайці\n• Дзвін індуктивності\n• Розділення силової й аналог. землі", size=9.5, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(text(x3 + col_w / 2, 245, "Вимагає фільтрації LC", size=10, color=POS, bold=True))
    p.append(text(x3 + col_w / 2, 265, "та захисних TVS-діодів", size=9.5, color=MUTED))
    
    render(os.path.join(OUT, "power-profiles-comparison.svg"), W, H, *p,
           title="Профіль живлення: стабільний USB проти батареї та DC-DC")


# ── 5. clock-hse-trap: пастка тактування HSE ─────────────────────────────────
def fig_clock_hse_trap():
    W, H = 820, 320
    p = []
    
    # Ліва колонка: Наївний код з девборди (зависання)
    p.append(rect(40, 45, 350, 255, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    p.append(text(215, 70, "Код із девборди (Небезпечний)", size=12, color=POS, bold=True))
    
    p.append(fitbox(55, 90, 320, 38, "1. RCC->CR |= RCC_CR_HSEON;\n(Увімкнути зовнішній кварц 8 МГц)", size=10, fill="#ffffff", stroke=POS, sw=1.2))
    p.append(fitbox(55, 138, 320, 45, "2. while (!(RCC->CR & RCC_CR_HSERDY))\n   { /* нескінченне очікування */ }", size=10, fill="#ffffff", stroke=POS, sw=1.2))
    
    p.append(fitbox(55, 195, 320, 85, "Аварія на власній платі:\n• Кварц не розпаяно (економія BOM)\n• Невідповідні конденсатори C_L\n• Мікротріщина в пайці / флюс\n→ МК НАЗАВЖДИ ЗАВИСАЄ В ЦИКЛІ!", size=9.5, fill="#ffffff", stroke=POS, sw=1.2))
    
    # Права колонка: Надійний код з таймаутом і Fallback
    p.append(rect(430, 45, 350, 255, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(605, 70, "Надійний код (Production-Ready)", size=12, color=FIELD, bold=True))
    
    p.append(fitbox(445, 90, 320, 38, "1. Увімкнути HSE + запустити таймер", size=10, fill="#ffffff", stroke=FIELD, sw=1.2))
    p.append(fitbox(445, 138, 320, 45, "2. while (!HSERDY && --timeout > 0)\n   { /* обмежене очікування */ }", size=10, fill="#ffffff", stroke=FIELD, sw=1.2))
    
    p.append(fitbox(445, 195, 320, 85, "Безпечна поведінка:\n• Якщо HSE готовий → перехід на PLL (HSE)\n• Якщо таймаут вичерпано →\n  Fallback на внутрішній RC-генератор (HSI)\n  + запис прапорця аварії в EEPROM/лог", size=9.5, fill="#ffffff", stroke=FIELD, sw=1.2))
    
    render(os.path.join(OUT, "clock-hse-trap.svg"), W, H, *p,
           title="Пастка тактування: де зависає SystemClock_Config()")


if __name__ == "__main__":
    fig_scaffolding_vs_custom()
    fig_swd_connector_vtref()
    fig_autoreset_transistor_logic()
    fig_power_profiles_comparison()
    fig_clock_hse_trap()
    print("OK: figures generated successfully")
