# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PIN  = "#8a6a1e"   # золотисто-бурштиновий — ніжка / контакт
WARM = "#fbf3e0"   # теплий фон контакту
GP   = FIELD       # зелений — вільний / узгоджений шлях
PERI = NEG         # синій — периферійний блок
HOT  = POS         # червоний — конфлікт / перевантаження / небезпека
WARN = "#d97706"   # бурштиновий / попередження


def draw_polyline(pts, color=LINE, sw=1.5, dash=None):
    res = []
    for i in range(len(pts) - 1):
        res.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=color, sw=sw, dash=dash))
    return "".join(res)


# ── 1. pinout-matrix-conflict: Конфлікт альтернативних функцій на виводах ───────
def fig_pinout_matrix_conflict():
    W, H = 840, 430
    p = []

    # Заголовок блоків периферії ліворуч
    p.append(text(125, 32, "Внутрішня периферія", size=13, color=PERI, bold=True))
    # Заголовок матриці та виводів праворуч
    p.append(text(660, 32, "Фізичні ніжки мікроконтролера", size=13, color=PIN, bold=True))

    periphs = [
        ("USART1 (TX/RX)", 65, PERI, "#eef2fb"),
        ("SPI1 (SCK/MOSI)", 135, PERI, "#eef2fb"),
        ("I2C1 (SCL/SDA)", 205, PERI, "#eef2fb"),
        ("TIM1 (CH1/CH2)", 275, PERI, "#eef2fb"),
        ("ADC1 (IN5/IN6)", 345, PERI, "#eef2fb"),
    ]

    for name, y, col, fill in periphs:
        p.append(fitbox(20, y, 190, 38, name, size=11, color=col, stroke=col, fill=fill, bold=True))

    pins = [
        ("PA5 (AF5: SPI1_SCK / AF1: TIM2 / ADC1_IN5)", 65, HOT, "#fdecea"),
        ("PA6 (AF5: SPI1_MISO / AF1: TIM3 / ADC1_IN6)", 135, GP, "#eaf6ee"),
        ("PA9 (AF7: USART1_TX / AF1: TIM1_CH2)", 205, HOT, "#fdecea"),
        ("PB6 (AF4: I2C1_SCL / AF7: USART1_TX / TIM4)", 275, GP, "#eaf6ee"),
        ("PB7 (AF4: I2C1_SDA / AF7: USART1_RX / TIM4)", 345, GP, "#eaf6ee"),
    ]

    for name, y, col, fill in pins:
        p.append(fitbox(500, y, 320, 38, name, size=10.5, color=col, stroke=col, fill=fill, bold=True))

    # Центральний блок мультиплексора (MUX Matrix)
    p.append(fitbox(250, 50, 210, 345, "МАТРИЦЯ МУЛЬТИПЛЕКСУВАННЯ\n(Alternate Function MUX)\n\nРегістри AFR[0..1]\nAF0 .. AF15\n\nСелектор комутації\nу кремнії",
                    size=11, color=INK, stroke=INK, fill="#f8fafc", bold=True))

    # Лінії зв'язку
    # USART1 -> PA9
    p.append(line(210, 84, 250, 110, color=PERI, sw=1.5))
    p.append(line(460, 110, 500, 224, color=HOT, sw=2))
    # SPI1 -> PA5 (КОНФЛІКТ: одночасно хочемо ADC1 на PA5)
    p.append(line(210, 154, 250, 160, color=PERI, sw=1.5))
    p.append(line(460, 160, 500, 84, color=HOT, sw=2))
    # ADC1 -> PA5
    p.append(line(210, 364, 250, 320, color=PERI, sw=1.5))
    p.append(line(460, 320, 500, 84, color=HOT, sw=2, dash="4 4"))

    # I2C1 -> PB6/PB7
    p.append(line(210, 224, 250, 230, color=PERI, sw=1.5))
    p.append(line(460, 230, 500, 294, color=GP, sw=1.5))
    p.append(line(460, 250, 500, 364, color=GP, sw=1.5))

    # Мітка колізії
    p.append(fitbox(330, 18, 160, 24, "⚡ КОНФЛІКТ РЕСУРСУ", size=10, color=HOT, stroke=HOT, fill="#fff0f0", bold=True))

    p.append(text(W/2, 415, "Фізичний пін має фіксоване меню альтернативних функцій (AF): кілька модулів не можуть зайняти його водночас.", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "pinout-matrix-conflict.svg"), W, H, *p,
           title="Конфлікт альтернативних функцій на виводах мікроконтролера")


# ── 2. swd-lockout-scenario: Блокування ліній налагодження SWD ─────────────────
def fig_swd_lockout():
    W, H = 840, 360
    p = []

    # Зліва: штатна конфігурація
    p.append(text(210, 30, "Штатний режим: SWD активний", size=12.5, color=GP, bold=True))
    p.append(fitbox(30, 55, 140, 50, "Програматор\nST-Link / J-Link", size=11, color=INK, stroke=INK, fill="#f0f4f8", bold=True))
    p.append(fitbox(250, 55, 140, 50, "Cortex-M Ядро\n(Debug Port)", size=11, color=GP, stroke=GP, fill="#eaf6ee", bold=True))
    p.append(line(170, 70, 250, 70, color=GP, sw=2))
    p.append(text(210, 64, "SWDIO (PA13)", size=9, color=GP, bold=True))
    p.append(line(170, 90, 250, 90, color=GP, sw=2))
    p.append(text(210, 102, "SWCLK (PA14)", size=9, color=GP, bold=True))

    p.append(fitbox(30, 130, 360, 70, "1. Прошивка стартує після скидання (Reset).\n2. Виконується код за замовчуванням.\n3. Налагоджувач вільно читає та прошиває пам'ять.",
                    size=10, color=INK, stroke=MUTED, fill="#fafafa"))

    # Розділова лінія (зупиняється ПЕРЕД нижнім блоком)
    p.append(line(420, 25, 420, 220, color="#dcdcdc", sw=1.5, dash="5 5"))

    # Справа: режим блокування (Lockout)
    p.append(text(630, 30, "Конфлікт: захоплення під GPIO", size=12.5, color=HOT, bold=True))
    p.append(fitbox(440, 55, 130, 50, "Програматор\nST-Link", size=11, color=MUTED, stroke=MUTED, fill="#f4f4f4"))
    p.append(fitbox(670, 55, 140, 50, "Силове реле / LED\n(GPIO Output)", size=11, color=HOT, stroke=HOT, fill="#fdecea", bold=True))

    # Перекреслений зв'язок
    p.append(line(570, 70, 615, 70, color=HOT, sw=2))
    p.append(line(615, 62, 629, 78, color=HOT, sw=2.5))
    p.append(line(629, 62, 615, 78, color=HOT, sw=2.5))
    p.append(line(630, 70, 670, 70, color=HOT, sw=2))
    p.append(text(622, 96, "PA13 перемкнуто на вихід!", size=9.5, color=HOT, bold=True))

    p.append(fitbox(440, 130, 370, 85, "1. Користувач призначив PA13/PA14 під звичайний GPIO.\n2. Через 50 мкс після старту SWD-інтерфейс вимикається.\n3. Програматор видає 'Cannot connect to target'.\n4. Потрібно Connect Under Reset або вхід у Bootloader через BOOT0.",
                    size=9.5, color=HOT, stroke=HOT, fill="#fff5f5"))

    # Нижня плашка з правилом безпеки
    p.append(fitbox(60, 240, 720, 65, "ПРАВИЛО БЕЗПЕКИ РОЗПІНОВКИ:\nНе призначайте лінії налагодження (SWDIO/SWCLK) під загальні GPIO,\nякщо на платі немає виведеної апаратної лінії скидання (NRST) або піна BOOT0.",
                    size=10.5, color=INK, stroke=WARN, fill="#fffbeb", bold=True))

    p.append(text(W/2, 345, "Перепризначення виводів SWD блокує зв'язок із чипом одразу після виконання перших інструкцій.", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "swd-lockout-scenario.svg"), W, H, *p,
           title="Сценарій апаратного блокування відлагоджувача SWD")


# ── 3. pin-electrical-classes: Електричні класи пінів (FT vs TTa) ───────────────
def fig_pin_classes():
    W, H = 840, 420
    p = []

    # Ліва половина: 5V-толерантний вхід (FT)
    p.append(text(210, 28, "5V-толерантний цифровий пін (FT)", size=12.5, color=GP, bold=True))
    p.append(rect(40, 46, 340, 305, fill="#fcfdfd", stroke=GP, sw=1.5))

    p.append(text(80, 76, "VDD (3.3V)", size=11, color=PERI, bold=True))
    p.append(line(80, 84, 80, 105, color=PERI, sw=1.5))
    p.append(line(80, 105, 160, 105, color=PERI, sw=1.5))

    # Спеціальна схема захисту FT без прямого діода на VDD
    p.append(fitbox(120, 115, 130, 36, "Зсувний каскад\n(VSS + 5.5V Clamp)", size=9.5, color=GP, stroke=GP, fill="#eaf6ee", bold=True))

    # Вхідний пін
    p.append(line(60, 180, 160, 180, color=PIN, sw=2.5))
    p.append(circle(60, 180, 5, fill=PIN, stroke=LINE, sw=1))
    p.append(text(60, 202, "Vin = 5.0V", size=10, color=GP, bold=True))

    # Діод на землю VSS
    p.append(line(180, 180, 180, 205, color=LINE, sw=1.5))
    p.append(fitbox(160, 205, 40, 22, "ESD", size=8.5, color=MUTED, stroke=MUTED, fill="#f0f0f0"))
    p.append(line(180, 227, 180, 245, color=LINE, sw=1.5))
    p.append(text(180, 258, "GND (0V)", size=10, color=MUTED, bold=True))

    # Пояснення FT
    p.append(fitbox(50, 275, 320, 65, "✓ Немає діода на шину VDD.\n✓ Напруга до 5.5 В не створює струму витоку в 3.3 В.\n✓ Безпечно для сигналів 5 В без перетворювача рівнів.",
                    size=9.5, color=GP, stroke=GP, fill="#f0fdf4"))

    # Права половина: Аналоговий пін (TTa / ADC In)
    p.append(text(630, 28, "Аналоговий / стандартний пін (TTa / ADC)", size=12.5, color=HOT, bold=True))
    p.append(rect(460, 46, 340, 305, fill="#fffbfb", stroke=HOT, sw=1.5))

    p.append(text(500, 76, "VDDA (3.3V)", size=11, color=PERI, bold=True))
    p.append(line(500, 84, 500, 105, color=PERI, sw=1.5))
    p.append(line(500, 105, 580, 105, color=PERI, sw=1.5))

    # Верхній діод захисту
    p.append(fitbox(560, 115, 50, 26, "Діод D1", size=9, color=HOT, stroke=HOT, fill="#fdecea", bold=True))
    p.append(line(585, 141, 585, 180, color=HOT, sw=2))

    # Вхідний пін
    p.append(line(480, 180, 585, 180, color=PIN, sw=2.5))
    p.append(circle(480, 180, 5, fill=PIN, stroke=LINE, sw=1))
    p.append(text(480, 202, "Vin = 5.0V", size=10, color=HOT, bold=True))

    # Струм інжекції
    p.append(arrow(520, 175, 575, 145, color=HOT, sw=2))
    p.append(text(660, 160, "Струм інжекції > 5 мА!\n(Паразитне живлення VDDA)", size=9.5, color=HOT, bold=True))

    # Нижній діод на землю
    p.append(line(585, 180, 585, 205, color=LINE, sw=1.5))
    p.append(fitbox(560, 205, 50, 22, "Діод D2", size=8.5, color=MUTED, stroke=MUTED, fill="#f0f0f0"))
    p.append(line(585, 227, 585, 245, color=LINE, sw=1.5))
    p.append(text(585, 258, "GND (0V)", size=10, color=MUTED, bold=True))

    # Пояснення TTa
    p.append(fitbox(470, 275, 320, 65, "✗ Прямий діод D1 відкривається при Vin > VDDA + 0.3V.\n✗ Паразитне живлення схеми крізь вхідний пін.\n✗ Викривлення показів сусідніх каналів АЦП.",
                    size=9.5, color=HOT, stroke=HOT, fill="#fff0f0"))

    p.append(text(W/2, 395, "Аналогові піни (TTa) містять верхній діод захисту до VDDA: подача 5 В перепалює діод або живить чип через пін.", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "pin-electrical-classes.svg"), W, H, *p,
           title="Електричні класи пінів: 5V-толерантність проти аналогових входів")


# ── 4. gpio-speed-emi: Вплив GPIO Slew Rate / Speed на завади ──────────────────
def fig_gpio_speed_emi():
    W, H = 840, 360
    p = []

    # Ліва колонка: Low Speed
    p.append(text(210, 30, "Низька швидкість (Low Speed / Slew Rate Limit)", size=12, color=GP, bold=True))
    p.append(rect(40, 50, 340, 255, fill="#fafdfa", stroke=GP, sw=1.5))

    p.append(text(80, 75, "Форма сигналу (Осцилограф):", size=10.5, color=INK, bold=True))
    p.append(draw_polyline([(70, 160), (110, 160), (140, 100), (200, 100), (230, 160), (280, 160)],
                           color=GP, sw=2.5))
    p.append(text(125, 88, "tr ≈ 30 нс", size=9.5, color=GP, bold=True))
    p.append(text(180, 175, "Чистий сигнал без викидів", size=10, color=GP, italic=True))

    p.append(fitbox(55, 195, 310, 95, "• Струм перезаряджання ємності траси малий.\n• Практично відсутній високочастотний спектр EMI.\n• Відсутній дзвін (ringing) та Ground Bounce.\n• Ідеально для LED, кнопок, I2C (100–400 кГц), UART.",
                    size=9.5, color=INK, stroke=MUTED, fill="#ffffff"))

    # Права колонка: Very High Speed
    p.append(text(630, 30, "Максимальна швидкість (Very High Speed)", size=12, color=HOT, bold=True))
    p.append(rect(460, 50, 340, 255, fill="#fdfafa", stroke=HOT, sw=1.5))

    p.append(text(500, 75, "Форма сигналу (Осцилограф):", size=10.5, color=INK, bold=True))
    p.append(draw_polyline([(490, 160), (520, 160), (524, 80), (532, 115), (540, 92), (548, 104), (600, 100), (604, 180), (612, 145), (620, 168), (660, 160)],
                           color=HOT, sw=2.5))
    p.append(text(540, 72, "tr < 2 нс (Дзвін!)", size=9.5, color=HOT, bold=True))
    p.append(text(585, 175, "Викиди вище VDD та нижче GND", size=10, color=HOT, italic=True))

    p.append(fitbox(475, 195, 310, 95, "• Величезний піковий струм перемикання транзисторів.\n• Потужні гармоніки до сотень МГц (радіозавади EMI).\n• Перехресні наводки (crosstalk) на сусідні аналогові траси.\n• Потрібно ЛИШЕ для SPI > 20 МГц, SDIO, паралельних шин.",
                    size=9.5, color=INK, stroke=MUTED, fill="#ffffff"))

    p.append(text(W/2, 335, "Правило налаштування OSPEEDR: ставте найменшу швидкість, при якій інтерфейс працює надійно.", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "gpio-speed-emi.svg"), W, H, *p,
           title="Вплив швидкості перемикання GPIO (Slew Rate) на шум та електромагнітні завади")


# ── 5. pcb-escape-routing: Топологічний аналіз трасування виводів ────────────────
def fig_pcb_escape():
    W, H = 840, 400
    p = []

    # Ліва частина: Хаотичний вибір пінів
    p.append(text(210, 26, "Хаотичний розподіл: конфлікт трасування", size=12, color=HOT, bold=True))
    p.append(rect(40, 42, 340, 305, fill="#fffaf9", stroke=HOT, sw=1.5))

    # Корпус МК
    p.append(fitbox(70, 80, 100, 100, "MCU\nLQFP", size=11, color=PIN, stroke=PIN, fill=WARM, bold=True))
    # Периферійні мікросхеми праворуч
    p.append(fitbox(270, 60, 85, 35, "SPI Flash", size=10, color=PERI, stroke=PERI, fill="#eef2fb", bold=True))
    p.append(fitbox(270, 120, 85, 35, "I2C Sensor", size=10, color=PERI, stroke=PERI, fill="#eef2fb", bold=True))
    p.append(fitbox(270, 180, 85, 35, "RS-485", size=10, color=PERI, stroke=PERI, fill="#eef2fb", bold=True))

    # Заплутані траси з переходами (Via)
    p.append(draw_polyline([(120, 180), (120, 230), (220, 230), (220, 75), (270, 75)], color=HOT, sw=2))
    p.append(draw_polyline([(120, 80), (120, 55), (190, 55), (190, 195), (270, 195)], color=HOT, sw=2))
    p.append(draw_polyline([(170, 130), (270, 130)], color=HOT, sw=2))

    # Перехідні отвори (Vias)
    vias_bad = [(220, 130), (190, 130), (120, 230), (190, 55)]
    for vx, vy in vias_bad:
        p.append(circle(vx, vy, 4.5, fill="#ffffff", stroke=HOT, sw=1.8))
    p.append(fitbox(55, 255, 310, 50, "4+ перехідних отвори (Vias)\nРозірваний полігон землі GND\nЗбільшена індуктивність трас", size=9.5, color=HOT, stroke=HOT, fill="#fff0f0", bold=True))

    # Права частина: Оптимізований вибір пінів
    p.append(text(630, 26, "Оптимізований вибір: прямий вихід (Escape)", size=12, color=GP, bold=True))
    p.append(rect(460, 42, 340, 305, fill="#f9fdfa", stroke=GP, sw=1.5))

    p.append(fitbox(490, 80, 100, 100, "MCU\nLQFP", size=11, color=PIN, stroke=PIN, fill=WARM, bold=True))
    p.append(fitbox(690, 60, 85, 35, "SPI Flash", size=10, color=PERI, stroke=PERI, fill="#eef2fb", bold=True))
    p.append(fitbox(690, 120, 85, 35, "I2C Sensor", size=10, color=PERI, stroke=PERI, fill="#eef2fb", bold=True))
    p.append(fitbox(690, 180, 85, 35, "RS-485", size=10, color=PERI, stroke=PERI, fill="#eef2fb", bold=True))

    # Прямі паралельні траси без переходів
    p.append(line(590, 95, 690, 75, color=GP, sw=2))
    p.append(line(590, 130, 690, 135, color=GP, sw=2))
    p.append(line(590, 165, 690, 195, color=GP, sw=2))

    p.append(fitbox(480, 240, 300, 80, "✓ Використано функцію ремапу пінів (Remap).\n✓ Траси розташовані на одному шарі без жодного Via.\n✓ Суцільний зворотний шар землі (GND Return Plane).\n✓ Мінімальна довжина провідників і нульовий crosstalk.",
                    size=9.5, color=GP, stroke=GP, fill="#f0fdf4"))

    p.append(text(W/2, 375, "Планування розпіновки визначає топологію друкованої плати: ремап функцій запобігає перехрещенню трас.", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "pcb-escape-routing.svg"), W, H, *p,
           title="Вплив розкладки виводів на топологію та якість трасування плати")


def main():
    fig_pinout_matrix_conflict()
    fig_swd_lockout()
    fig_pin_classes()
    fig_gpio_speed_emi()
    fig_pcb_escape()
    print("All 5 figures generated successfully.")

if __name__ == "__main__":
    main()
