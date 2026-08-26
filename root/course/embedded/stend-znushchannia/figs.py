# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. halt-hass-margins: межі робочих режимів, HALT та HASS ────────────────
def fig_halt_hass_margins():
    W, H = 840, 430
    p = []
    
    # Заголовок осі
    y_axis = 180
    x_min, x_max = 70, 750
    
    p.append(arrow(x_min - 20, y_axis, x_max + 40, y_axis, color=INK, sw=2.0))
    p.append(text(x_max + 45, y_axis + 4, "Стрес (T, V, G)", size=12, color=INK, bold=True, anchor="start"))
    
    # Ключові точки на осі стресу
    x_ldl = 120
    x_lol = 230
    x_lsl = 320
    x_nom = 410
    x_usl = 500
    x_uol = 590
    x_udl = 700
    
    # Зони на фоні
    # Зона безпечної штатної роботи (LSL .. USL)
    p.append(rect(x_lsl, y_axis - 55, x_usl - x_lsl, 110, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    # Зона незворотного руйнування (крайні зони)
    p.append(rect(x_min - 10, y_axis - 55, x_ldl - (x_min - 10), 110, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    p.append(rect(x_udl, y_axis - 55, (x_max + 20) - x_udl, 110, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    
    # Вертикальні мітки на осі
    points = [
        (x_ldl, "LDL", "Нижня межа\nруйнування", POS, "#fdecea"),
        (x_lol, "LOL", "Нижня робоча\nмежа (збій)", "#b9770e", "#fff3e0"),
        (x_lsl, "LSL", "Нижня межа\nспецифікації", FIELD, "#eafaf0"),
        (x_nom, "НОМІНАЛ", "Штатний\nрежим", INK, "#ffffff"),
        (x_usl, "USL", "Верхня межа\nспецифікації", FIELD, "#eafaf0"),
        (x_uol, "UOL", "Верхня робоча\nмежа (збій)", "#b9770e", "#fff3e0"),
        (x_udl, "UDL", "Верхня межа\nруйнування", POS, "#fdecea"),
    ]
    
    for x, tag, desc, col, fill in points:
        p.append(line(x, y_axis - 45, x, y_axis + 45, color=col, sw=1.5))
        p.append(circle(x, y_axis, 5, fill=col, stroke=col, sw=1.5))
        p.append(text(x, y_axis - 52, tag, size=11, bold=True, color=col))
        
        # Опис внизу
        b, bw, bh = textbox(x, y_axis + 80, desc, size=10, bold=True, color=col, fill=fill, stroke=col, sw=1.2, min_w=85)
        p.append(b)
    
    # Стрілки запасів надійності зверху
    # Запас робочої надійності (Operating Margin)
    p.append(line(x_usl, 60, x_uol, 60, color="#b9770e", sw=2.0))
    p.append(line(x_usl, 52, x_usl, 68, color="#b9770e", sw=1.5))
    p.append(line(x_uol, 52, x_uol, 68, color="#b9770e", sw=1.5))
    p.append(text((x_usl + x_uol) / 2, 44, "Робочий запас (Operating Margin)", size=11, color="#b9770e", bold=True))
    
    # Запас руйнування (Destruct Margin)
    p.append(line(x_uol, 95, x_udl, 95, color=POS, sw=2.0))
    p.append(line(x_uol, 87, x_uol, 103, color=POS, sw=1.5))
    p.append(line(x_udl, 87, x_udl, 103, color=POS, sw=1.5))
    p.append(text((x_uol + x_udl) / 2, 112, "Запас міцності (Destruct Margin)", size=11, color=POS, bold=True))
    
    # Позначення для HALT і HASS
    b_halt, _, _ = textbox(x_nom, 330, "HALT (розробка): крок за кроком тиснемо за межі специфікації (LSL/USL),\nдоки не знайдемо LOL/UOL, а потім руйнування LDL/UDL для усунення слабких місць",
                           size=11, bold=True, color="#b9770e", fill="#fffbf0", stroke="#b9770e", sw=1.4, min_w=680)
    b_hass, _, _ = textbox(x_nom, 390, "HASS (серія): скринінг готових плат стресом вище LSL/USL, але суворо нижче LOL/UOL,\nщоб відсіяти приховані виробничі дефекти монтажу без вичерпання ресурсу виробу",
                           size=11, bold=True, color=FIELD, fill="#f3fcf6", stroke=FIELD, sw=1.4, min_w=680)
    p.append(b_halt)
    p.append(b_hass)

    render(os.path.join(OUT, "halt-hass-margins.svg"), W, H, *p,
           title="Граничні межі працездатності: співвідношення областей HALT і HASS")


# ── 2. stress-bench-architecture: архітектура автоматизованого HIL-стенду ────
def fig_stress_bench_architecture():
    W, H = 860, 480
    p = []
    
    # Лівий блок: Host PC
    b_host, w_host, h_host = textbox(130, 240, "ХОСТОВИЙ ПК (HOST)\n• Python Test Suite\n• Генератор сценаріїв\n• Shmoo-plot аналіз\n• База збоїв / логів",
                                     size=11, bold=True, color=INK, fill="#f4f6f8", stroke=INK, sw=1.6, min_w=170)
    p.append(b_host)
    
    # Центральний блок: Контролер стенду
    b_ctrl, w_ctrl, h_ctrl = textbox(390, 240, "КОНТРОЛЕР СТЕНДУ\n(MCU Testbench Rig)\n• Hardware Timers (глітч 1 мкс)\n• Швидкий ЦАП (1.8–5.5 В)\n• Драйвер реле завад / EFT\n• Телеметрія струму (INA226)",
                                     size=11, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.8, min_w=220)
    p.append(b_ctrl)
    
    # Зв'язок Host <-> Controller
    p.append(arrow(130 + w_host / 2, 234, 390 - w_ctrl / 2, 234, color=INK, sw=1.8))
    p.append(arrow(390 - w_ctrl / 2, 246, 130 + w_host / 2, 246, color=INK, sw=1.8))
    p.append(text(255, 218, "USB-CDC / UART", size=10, bold=True, color=INK))
    
    # Правий блок: Випробуваний пристрій (DUT)
    b_dut, w_dut, h_dut = textbox(720, 240, "ДОСЛІДЖУВАНИЙ ПРИСТРІЙ\n(DUT Target Board)\n• MCU + Flash + RAM\n• Аналогові давачі\n• Інтерфейси CAN/RS485\n• Джерело живлення / LDO",
                                  size=11, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=200)
    p.append(b_dut)
    
    # Блоки впливу навколо DUT
    # Зверху: Модуль живлення та глітчер
    b_pwr, _, _ = textbox(560, 75, "МОДУЛЬ ПРОСАДОК І ГЛІТЧІВ (Power Rig)\n• P-MOSFET обрив (<50 нс) + N-MOSFET pull-down\n• Керування напругою (Voltage Margining 2.7–5.5 В)",
                          size=10, bold=True, color="#b9770e", fill="#fff3e0", stroke="#e67e22", sw=1.5, min_w=360)
    p.append(b_pwr)
    p.append(arrow(390, 240 - h_ctrl / 2, 450, 75 + 28, color="#e67e22", sw=1.6))
    p.append(arrow(670, 75 + 28, 720, 240 - h_dut / 2, color="#e67e22", sw=2.0))
    p.append(text(725, 145, "VDD_DUT (стрес)", size=9.5, bold=True, color="#e67e22"))
    
    # Знизу: Модуль ЕМ-завад і кліматичний контур
    b_emi, _, _ = textbox(560, 415, "ІНЖЕКТОР ЗАВАД ТА ТЕРМОСТЕНД\n• Іскровий розрядник / EFT реле (індуктивний удар)\n• Модуль Пельтьє H-Bridge (-40..+85 °C) + матриця КЗ",
                          size=10, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.5, min_w=360)
    p.append(b_emi)
    p.append(arrow(390, 240 + h_ctrl / 2, 450, 415 - 28, color=POS, sw=1.6))
    p.append(arrow(670, 415 - 28, 720, 240 + h_dut / 2, color=POS, sw=2.0))
    p.append(text(725, 335, "Іскри, сплески, T°", size=9.5, bold=True, color=POS))
    
    # Зворотний зв'язок від DUT до Controller (UART/SWD/Telemetry)
    p.append(arrow(720 - w_dut / 2, 240, 390 + w_ctrl / 2, 240, color=FIELD, sw=2.0))
    p.append(text(555, 226, "UART Log / Reset Pin", size=10, bold=True, color=FIELD))

    render(os.path.join(OUT, "stress-bench-architecture.svg"), W, H, *p,
           title="Апаратна архітектура автоматизованого стрес-стенду HIL")


# ── 3. power-glitch-profile: часові діаграми глітчів та просідань ────────────
def fig_power_glitch_profile():
    W, H = 820, 440
    p = []
    
    # Сценарій 1: Мікрообрив (Micro-Dropout / Power Glitch)
    y1 = 80
    p.append(text(70, y1 - 25, "1. Мікрообрив живлення (Micro-Dropout, 10 мкс .. 5 мс)", size=11, bold=True, color=INK, anchor="start"))
    p.append(arrow(70, y1 + 35, 750, y1 + 35, color="#80868b", sw=1.2))
    p.append(text(755, y1 + 38, "t", size=11, italic=True, color="#80868b", anchor="start"))
    
    # Осцилограма 1: 3.3V -> спад до 0.8V -> повернення до 3.3V
    p.append(line(80, y1 - 15, 240, y1 - 15, color=NEG, sw=2.4))
    p.append(line(240, y1 - 15, 245, y1 + 25, color=NEG, sw=2.4))
    p.append(line(245, y1 + 25, 295, y1 + 25, color=NEG, sw=2.4))
    p.append(line(295, y1 + 25, 300, y1 - 15, color=NEG, sw=2.4))
    p.append(line(300, y1 - 15, 500, y1 - 15, color=NEG, sw=2.4))
    
    # Рівень 3.3 В і поріг BOD
    p.append(line(80, y1 - 15, 500, y1 - 15, color="#c2c8cf", sw=1.0, dash="3 3"))
    p.append(text(65, y1 - 12, "3.3 В", size=10, bold=True, color=NEG, anchor="end"))
    p.append(line(80, y1 + 10, 500, y1 + 10, color=POS, sw=1.2, dash="4 4"))
    p.append(text(65, y1 + 12, "BOD (2.7 В)", size=9.5, bold=True, color=POS, anchor="end"))
    
    # Пояснення до 1
    p.append(rect(530, y1 - 30, 240, 65, fill="#fff3e0", stroke="#e67e22", sw=1.2, rx=6))
    p.append(mtext(650, y1 + 2, "Небезпечна зона: напруга впала\nнижче порогу логіки, але вище BOD.\nВиникає зависання або бітовий збій",
                   size=9.5, bold=True, color="#b9770e", lh=1.2))
    
    # Сценарій 2: Повільне просідання (Slow Brownout Ramp)
    y2 = 210
    p.append(text(70, y2 - 25, "2. Повільне плавне просідання (Slow Brownout Ramp)", size=11, bold=True, color=INK, anchor="start"))
    p.append(arrow(70, y2 + 35, 750, y2 + 35, color="#80868b", sw=1.2))
    p.append(text(755, y2 + 38, "t", size=11, italic=True, color="#80868b", anchor="start"))
    
    # Осцилограма 2: пологий спад
    p.append(line(80, y2 - 15, 180, y2 - 15, color="#e67e22", sw=2.4))
    p.append(line(180, y2 - 15, 380, y2 + 30, color="#e67e22", sw=2.4))
    p.append(line(380, y2 + 30, 440, y2 + 30, color="#e67e22", sw=2.4))
    p.append(line(440, y2 + 30, 445, y2 - 15, color="#e67e22", sw=2.4))
    p.append(line(445, y2 - 15, 500, y2 - 15, color="#e67e22", sw=2.4))
    
    p.append(line(80, y2 + 10, 500, y2 + 10, color=POS, sw=1.2, dash="4 4"))
    p.append(text(65, y2 + 12, "BOD поріг", size=9.5, bold=True, color=POS, anchor="end"))
    
    # Пояснення до 2
    p.append(rect(530, y2 - 30, 240, 65, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=6))
    p.append(mtext(650, y2 + 2, "Перевірка гістерезису: чи не йде\nMCU в нескінченний рестарт\n(Reset oscillation) на межі спрацювання",
                   size=9.5, bold=True, color=FIELD, lh=1.2))
    
    # Сценарій 3: Ступеневе марджинування (Voltage Margining Staircase)
    y3 = 340
    p.append(text(70, y3 - 25, "3. Ступеневе варіювання напруги (Voltage Margining Staircase)", size=11, bold=True, color=INK, anchor="start"))
    p.append(arrow(70, y3 + 35, 750, y3 + 35, color="#80868b", sw=1.2))
    p.append(text(755, y3 + 38, "t", size=11, italic=True, color="#80868b", anchor="start"))
    
    # Осцилограма 3: сходинки
    p.append(line(80, y3 - 22, 160, y3 - 22, color=FIELD, sw=2.4))
    p.append(line(160, y3 - 22, 160, y3 - 10, color=FIELD, sw=2.4))
    p.append(line(160, y3 - 10, 240, y3 - 10, color=FIELD, sw=2.4))
    p.append(line(240, y3 - 10, 240, y3 + 8, color=FIELD, sw=2.4))
    p.append(line(240, y3 + 8, 320, y3 + 8, color=FIELD, sw=2.4))
    p.append(line(320, y3 + 8, 320, y3 + 22, color=FIELD, sw=2.4))
    p.append(line(320, y3 + 22, 400, y3 + 22, color=FIELD, sw=2.4))
    p.append(line(400, y3 + 22, 400, y3 + 30, color=FIELD, sw=2.4))
    p.append(line(400, y3 + 30, 480, y3 + 30, color=FIELD, sw=2.4))
    
    p.append(text(65, y3 - 20, "5.5 В", size=9.5, color=INK, anchor="end"))
    p.append(text(65, y3 + 8, "3.3 В", size=9.5, bold=True, color=FIELD, anchor="end"))
    p.append(text(65, y3 + 30, "2.5 В", size=9.5, color=POS, anchor="end"))
    
    # Пояснення до 3
    p.append(rect(530, y3 - 30, 240, 65, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=6))
    p.append(mtext(650, y3 + 2, "Пошук таймінг-збоїв (Setup/Hold)\nFlash-пам'яті та PLL при крайніх\nзначеннях напруги живлення ядра",
                   size=9.5, bold=True, color=NEG, lh=1.2))

    render(os.path.join(OUT, "power-glitch-profile.svg"), W, H, *p,
           title="Профілі напруги стрес-стенду: мікрообриви, просідання та сходинки")


# ── 4. eft-spark-relay-circuit: схема інжектора завад та іскрового розряду ──
def fig_eft_spark_circuit():
    W, H = 840, 400
    p = []
    
    # Блок зліва: Генератор індуктивного удару
    p.append(rect(60, 60, 320, 300, fill="#fffbf0", stroke="#e67e22", sw=1.5, rx=8))
    p.append(text(220, 85, "ГЕНЕРАТОР ІМПУЛЬСНИХ ЗАВАД (EFT / SPARK)", size=11, bold=True, color="#b9770e"))
    
    # Вузол котушки
    b_coil, _, _ = textbox(150, 160, "Котушка реле / L\n(без діода снабера!)\nЕнергія: ½ L·I²",
                           size=10, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.4, min_w=140)
    p.append(b_coil)
    
    # Ключ розриву
    b_sw, _, _ = textbox(150, 270, "MOSFET / Механічний\nконтакт зумера\n(розрив за <10 нс)",
                         size=10, bold=True, color=INK, fill="#f4f6f8", stroke=INK, sw=1.4, min_w=140)
    p.append(b_sw)
    p.append(line(150, 160 + 26, 150, 270 - 26, color=INK, sw=1.8))
    
    # Ударна напруга
    p.append(text(280, 200, "V = −L·(di/dt)\nСплеск: 500 В .. 2 кВ\nЧастота: 100 кГц", size=10, bold=True, color=POS))
    p.append(arrow(150, 210, 220, 200, color=POS, sw=1.5))
    
    # Ємнісна муфта зв'язку (Coupling Clamp)
    p.append(rect(420, 125, 145, 85, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    p.append(mtext(492, 165, "Ємнісна муфта\nінжекції (100 пФ .. 1 нФ\n3 кВ ізоляція)", size=10, bold=True, color=FIELD, lh=1.2))
    
    p.append(arrow(220, 170, 420, 170, color=POS, sw=2.2))
    
    # Блок справа: Плата DUT під випробуванням
    p.append(rect(605, 60, 185, 300, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=8))
    p.append(text(697, 85, "ДОСЛІДЖУВАНА ПЛАТА", size=11, bold=True, color=NEG))
    
    b_io, _, _ = textbox(697, 160, "Лінії живлення\nта зв'язку (CAN, I²C)\nСинфазна завада",
                         size=10, bold=True, color=NEG, fill="#ffffff", stroke=NEG, sw=1.4, min_w=150)
    p.append(b_io)
    
    b_mcu, _, _ = textbox(697, 270, "Мікроконтролер\n(MCU Core)\nТест Latch-up / Reset",
                          size=10, bold=True, color=INK, fill="#f4f6f8", stroke=INK, sw=1.4, min_w=150)
    p.append(b_mcu)
    p.append(line(697, 160 + 26, 697, 270 - 26, color=NEG, sw=1.8))
    
    p.append(arrow(565, 170, 620, 170, color=POS, sw=2.2))
    
    # Підпис унизу
    p.append(text(W / 2, 380, "Індуктивний сплеск самоіндукції без захисного діода наводить наносекундні пакети завад на шини DUT",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "eft-spark-relay-circuit.svg"), W, H, *p,
           title="Схема інжекції наносекундних електромагнітних завад та іскрового розряду")


if __name__ == "__main__":
    fig_halt_hass_margins()
    fig_stress_bench_architecture()
    fig_power_glitch_profile()
    fig_eft_spark_circuit()
    print("All figures successfully generated in", OUT)
