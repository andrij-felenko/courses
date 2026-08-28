# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. factory-test-timeline: часовий бюджет фабричного експрес-тестування ───
def fig_factory_test_timeline():
    W, H = 860, 420
    p = []

    # Межі діаграми
    left_lbl_w = 245
    bar_x1 = 260
    bar_x2 = 740
    bar_w_total = bar_x2 - bar_x1
    t_max = 8.0

    def t_to_x(t):
        return bar_x1 + (t / t_max) * bar_w_total

    # Часова вісь зверху і знизу
    grid_y_top = 55
    grid_y_bot = 355

    # Вертикальні лінії сітки часу (0..8 с)
    for t_step in range(9):
        gx = t_to_x(t_step)
        p.append(line(gx, grid_y_top, gx, grid_y_bot, color="#e5e8ec", sw=1.0))
        p.append(text(gx, grid_y_top - 8, "%d.0 с" % t_step, size=10, color=MUTED, anchor="middle"))
        p.append(text(gx, grid_y_bot + 16, "%d.0 с" % t_step, size=10, color=MUTED, anchor="middle"))

    # Рядки етапів тестування
    phases = [
        ("Фаза 0: Живлення та ICT", 0.0, 0.5, "Inrush < 150 мА, Iq спокою, захист КЗ", POS, "#fdecea"),
        ("Фаза 1: Ядро, тактування й ОЗП", 0.5, 1.2, "March C- ОЗП, частота HSE/PLL, Flash CRC", "#e67e22", "#fef5e7"),
        ("Фаза 2: Інвентаризація I2C/SPI", 1.2, 2.0, "WHO_AM_I IMU, JEDEC ID Flash, АЦП", "#27ae60", "#eafaf1"),
        ("Фаза 3: Валідація радіотракту RF", 2.0, 4.0, "CW несуча 2.4 ГГц, P_out ±1.5 dBm, RSSI", "#2980b9", "#ebf5fb"),
        ("Фаза 4: Персоналізація eFuse/OTP", 4.0, 5.5, "Запис UID, MAC, ключів Secure Boot", "#8e44ad", "#f4ecf7"),
        ("Фаза 5: Фінальний захист і реліз", 5.5, 7.5, "RDP lock, запис робочої прошивки", "#34495e", "#eaeded"),
    ]

    row_h = 45
    start_y = 65

    for i, (title_str, t_start, t_end, desc_str, col_stroke, col_fill) in enumerate(phases):
        ry = start_y + i * row_h
        # Підпис фази зліва
        p.append(text(left_lbl_w, ry + 18, title_str, size=11, color=INK, anchor="end", bold=True))
        p.append(text(left_lbl_w, ry + 32, "%0.1f–%0.1f с" % (t_start, t_end), size=9.5, color=MUTED, anchor="end"))

        # Смужка Ганта
        bx1 = t_to_x(t_start)
        bx2 = t_to_x(t_end)
        bw = bx2 - bx1

        p.append(rect(bx1, ry + 4, bw, 32, fill=col_fill, stroke=col_stroke, sw=1.5, rx=4))
        
        # Для смужок від 80px підпис всередині, для вузьких (Фаза 0: 0.5s = 30px) підпис праворуч
        if bw >= 80:
            p.append(text(bx1 + bw / 2, ry + 24, desc_str, size=9.5, color=col_stroke, bold=True, anchor="middle"))
        else:
            p.append(text(bx1 + bw / 2, ry + 24, "%0.1f" % (t_end - t_start), size=9.0, color=col_stroke, bold=True, anchor="middle"))
            p.append(text(bx2 + 8, ry + 24, desc_str, size=9.5, color=INK, anchor="start"))

    # Фінальна лінія й позначка PASS на 7.5с
    pass_x = t_to_x(7.5)
    p.append(line(pass_x, grid_y_top, pass_x, grid_y_bot, color="#1e8449", sw=1.8, dash="4,4"))
    p.append(rect(pass_x + 12, start_y + 5 * row_h + 5, 75, 30, fill="#d4efdf", stroke="#1e8449", sw=1.8, rx=4))
    p.append(text(pass_x + 49, start_y + 5 * row_h + 24, "PASS ✓", size=11, color="#1e8449", bold=True, anchor="middle"))

    # Підпис знизу
    p.append(text(W / 2, H - 12, "Загальний цикл перевірки на тестовому стенді: 7.5 секунди на одну плату", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "factory-test-timeline.svg"), W, H, *p,
           title="Хронометраж фабричного експрес-тестування плати (5–10 секунд)")


# ── 2. bringup-vs-product-architecture: різниця архітектур ───────────────────
def fig_architecture_comparison():
    W, H = 840, 420
    p = []

    # Ліва колонка: Робоча прошивка продукту
    col1_x, col1_w = 40, 365
    p.append(rect(col1_x, 50, col1_w, 330, fill="#fdf2e9", stroke="#e67e22", sw=1.8, rx=6))
    p.append(text(col1_x + col1_w / 2, 75, "Робоча прошивка продукту (App)", size=13, color="#b95e04", bold=True))
    p.append(text(col1_x + col1_w / 2, 94, "Оптимізована під функціонал і справне залізо", size=10, color=MUTED))

    app_layers = [
        ("Хмарні сервіси, MQTT, TLS, NTP", "#f8d7da", "#721c24", "Очікує сертифікати й IP-з'єднання"),
        ("BLE / Wi-Fi Provisioning стек", "#fce4ec", "#880e4f", "Таймаут очікування мобільного додатку (60 с)"),
        ("Файлова система LittleFS / NVS", "#fff3cd", "#856404", "Падає з помилкою на чистій/збійній Flash"),
        ("RTOS ядра, потоки, черги, семафори", "#e8f4f8", "#1a5276", "Блокування задач на непропаяній периферії"),
        ("Складні високорівневі драйвери", "#eaeded", "#2c3e50", "Нескінченні while(!ready) або HardFault"),
    ]

    cur_y = 112
    for title_l, fill_c, text_c, warn_c in app_layers:
        p.append(rect(col1_x + 15, cur_y, col1_w - 30, 42, fill=fill_c, stroke=text_c, sw=1.2, rx=4))
        p.append(text(col1_x + col1_w / 2, cur_y + 17, title_l, size=10.5, color=text_c, bold=True))
        p.append(text(col1_x + col1_w / 2, cur_y + 33, warn_c, size=9.5, color=MUTED, italic=True))
        cur_y += 48

    # Права колонка: Bring-up / Factory Test Firmware
    col2_x, col2_w = 435, 365
    p.append(rect(col2_x, 50, col2_w, 330, fill="#eafaf1", stroke="#27ae60", sw=1.8, rx=6))
    p.append(text(col2_x + col2_w / 2, 75, "Технологічна Bring-up прошивка (FCT)", size=13, color="#1e8449", bold=True))
    p.append(text(col2_x + col2_w / 2, 94, "Оптимізована під миттєву локалізацію дефектів", size=10, color=MUTED))

    test_layers = [
        ("UART / USB CDC діагностичний репортер", "#d4efdf", "#196f3d", "Миттєвий JSON / бінарний звіт стенду"),
        ("Модуль eFuse / OTP персоналізації", "#d1f2eb", "#117a65", "Стабільне пропалювання ключів та MAC"),
        ("RF тестовий модуль (CW Mode / RSSI)", "#ebf5fb", "#21618c", "Прямий запуск генератора без асоціації"),
        ("Ізольований I2C/SPI Sweep & March C-", "#fef9e7", "#7d6608", "Апаратні таймаути й Bus Recovery 9 тактів"),
        ("Bare-metal супер-цикл без купи (heap)", "#f5eef8", "#5b2c6f", "Нуль залежностей, запуск на 'голому' чипі"),
    ]

    cur_y = 112
    for title_l, fill_c, text_c, note_c in test_layers:
        p.append(rect(col2_x + 15, cur_y, col2_w - 30, 42, fill=fill_c, stroke=text_c, sw=1.2, rx=4))
        p.append(text(col2_x + col2_w / 2, cur_y + 17, title_l, size=10.5, color=text_c, bold=True))
        p.append(text(col2_x + col2_w / 2, cur_y + 33, note_c, size=9.5, color=MUTED, italic=True))
        cur_y += 48

    # Підпис знизу
    p.append(text(W / 2, H - 12, "Робоча прошивка вимагає працездатного заліза; прошивка тестування перевіряє його працездатність", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "bringup-vs-product-architecture.svg"), W, H, *p,
           title="Архітектура: робоча прошивка продукту проти Bring-up прошивки")


# ── 3. bed-of-nails-test-fixture: схема стенду з голчастим ложем ─────────────
def fig_test_fixture():
    W, H = 840, 400
    p = []

    # Верхня частина: Тестована плата (DUT - Device Under Test)
    dut_x, dut_y, dut_w, dut_h = 170, 50, 500, 75
    p.append(rect(dut_x, dut_y, dut_w, dut_h, fill="#1c2833", stroke="#2c3e50", sw=2.0, rx=4))
    p.append(text(dut_x + dut_w / 2, dut_y + 22, "Тестована плата (DUT — Device Under Test)", size=12, color="#ffffff", bold=True))

    # Компоненти на платі
    p.append(rect(dut_x + 25, dut_y + 35, 80, 28, fill="#2e4053", stroke="#5d6d7e", sw=1.0, rx=2))
    p.append(text(dut_x + 65, dut_y + 53, "MCU + RF", size=10, color="#ffffff"))

    p.append(rect(dut_x + 120, dut_y + 35, 65, 28, fill="#2e4053", stroke="#5d6d7e", sw=1.0, rx=2))
    p.append(text(dut_x + 152, dut_y + 53, "I2C IMU", size=10, color="#ffffff"))

    p.append(rect(dut_x + 200, dut_y + 35, 75, 28, fill="#2e4053", stroke="#5d6d7e", sw=1.0, rx=2))
    p.append(text(dut_x + 237, dut_y + 53, "SPI Flash", size=10, color="#ffffff"))

    p.append(rect(dut_x + 290, dut_y + 35, 85, 28, fill="#2e4053", stroke="#5d6d7e", sw=1.0, rx=2))
    p.append(text(dut_x + 332, dut_y + 53, "Power/LDO", size=10, color="#ffffff"))

    p.append(rect(dut_x + 390, dut_y + 35, 85, 28, fill="#2e4053", stroke="#5d6d7e", sw=1.0, rx=2))
    p.append(text(dut_x + 432, dut_y + 53, "RF Антена", size=10, color="#ffffff"))

    # Контрольні точки (Test Pads) на нижній грані плати
    pad_xs = [210, 265, 320, 375, 430, 485, 540, 595, 650]
    pad_labels = ["VCC", "GND", "SWCLK", "SWDIO", "TX", "RX", "SDA", "SCL", "RF_TP"]

    for px, plab in zip(pad_xs, pad_labels):
        p.append(circle(px, dut_y + dut_h, 3.5, fill="#f1c40f", stroke="#d4ac0d", sw=1.0))
        # Голчастий пружинний контакт (Pogo Pin)
        p.append(line(px, dut_y + dut_h, px, dut_y + dut_h + 40, color="#d4ac0d", sw=2.2))
        p.append(circle(px, dut_y + dut_h + 40, 2.5, fill="#b7950b", stroke=LINE, sw=0.5))

    # Текстова плашка голчастого ложа
    p.append(text(dut_x + dut_w / 2, dut_y + dut_h + 26, "Підпружинені голки Pogo Pins до тестових площадок (Test Pads)", size=10, color="#b7950b", bold=True))

    # Нижня частина: Блоки тестового стенду
    bottom_y = 190

    # Блок 1: Кероване джерело живлення зі шунтом
    p.append(rect(30, bottom_y, 175, 130, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    p.append(text(117, bottom_y + 22, "Кероване живлення", size=11, color=POS, bold=True))
    p.append(text(117, bottom_y + 38, "та монітор струму", size=10.5, color=POS))
    p.append(text(117, bottom_y + 62, "• Захист від КЗ (<1 мс)", size=10, color=INK))
    p.append(text(117, bottom_y + 80, "• Вимірювання Inrush", size=10, color=INK))
    p.append(text(117, bottom_y + 98, "• Струм спокою Iq", size=10, color=INK))
    p.append(text(117, bottom_y + 116, "• Напруга V_PP eFuse", size=10, color=INK))
    p.append(line(117, bottom_y, 210, dut_y + dut_h + 40, color=POS, sw=1.5, dash="2,2"))

    # Блок 2: SWD/JTAG Програматор
    p.append(rect(225, bottom_y, 175, 130, fill="#fef5e7", stroke="#e67e22", sw=1.5, rx=5))
    p.append(text(312, bottom_y + 22, "SWD Програматор", size=11, color="#e67e22", bold=True))
    p.append(text(312, bottom_y + 38, "та налагоджувач", size=10.5, color="#e67e22"))
    p.append(text(312, bottom_y + 62, "• Завантаження тестера", size=10, color=INK))
    p.append(text(312, bottom_y + 80, "• Зчитування логів SWO", size=10, color=INK))
    p.append(text(312, bottom_y + 98, "• Прошивка релізу", size=10, color=INK))
    p.append(text(312, bottom_y + 116, "• Захист RDP lock", size=10, color=INK))
    p.append(line(312, bottom_y, 350, dut_y + dut_h + 40, color="#e67e22", sw=1.5, dash="2,2"))

    # Блок 3: Хост-контролер стенду (FCT Master)
    p.append(rect(420, bottom_y, 185, 130, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=5))
    p.append(text(512, bottom_y + 22, "Хост-контролер стенду", size=11, color="#27ae60", bold=True))
    p.append(text(512, bottom_y + 38, "(ПК або Master MCU)", size=10.5, color="#27ae60"))
    p.append(text(512, bottom_y + 62, "• UART/USB діагностика", size=10, color=INK))
    p.append(text(512, bottom_y + 80, "• Генерація ключів/MAC", size=10, color=INK))
    p.append(text(512, bottom_y + 98, "• База даних серійників", size=10, color=INK))
    p.append(text(512, bottom_y + 116, "• Рішення PASS / FAIL", size=10, color=INK))
    p.append(line(512, bottom_y, 485, dut_y + dut_h + 40, color="#27ae60", sw=1.5, dash="2,2"))

    # Блок 4: RF Спектроаналізатор / Golden Receiver
    p.append(rect(625, bottom_y, 185, 130, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=5))
    p.append(text(717, bottom_y + 22, "RF Аналізатор", size=11, color="#2980b9", bold=True))
    p.append(text(717, bottom_y + 38, "(в RF-екрані)", size=10.5, color="#2980b9"))
    p.append(text(717, bottom_y + 62, "• Вимірювач потужності", size=10, color=INK))
    p.append(text(717, bottom_y + 80, "• Зсув частоти (ppm)", size=10, color=INK))
    p.append(text(717, bottom_y + 98, "• Loopback RSSI тест", size=10, color=INK))
    p.append(text(717, bottom_y + 116, "• Оцінка антени/балуна", size=10, color=INK))
    p.append(line(717, bottom_y, 650, dut_y + dut_h + 40, color="#2980b9", sw=1.5, dash="2,2"))

    # Підпис знизу
    p.append(text(W / 2, H - 14, "Стенд контролює живлення, прошиває ядро, опитує шини, міряє радіоефір і виносить вердикт за секунди", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "bed-of-nails-test-fixture.svg"), W, H, *p,
           title="Функціональний тестовий стенд (FCT) з голчастим ложем")


if __name__ == "__main__":
    fig_factory_test_timeline()
    fig_architecture_comparison()
    fig_test_fixture()
    print("All figures generated successfully.")
