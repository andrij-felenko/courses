# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Поділ складності між SoM та платою-носієм ──────────────────────
def som_carrier_split():
    W, H = 940, 520
    frags = []

    # Загальний заголовок
    frags.append(text(W / 2, 46, "Фізичний та програмний поділ між обчислювальним модулем (SoM) і платою-носієм",
                      size=13, color=MUTED))

    # Лівий блок: Обчислювальний модуль (SoM)
    som_x, som_y, som_w, som_h = 40, 80, 360, 390
    frags.append(rect(som_x, som_y, som_w, som_h, fill="#fdf6f5", stroke=POS, sw=2, rx=8))
    frags.append(text(som_x + som_w / 2, som_y + 28, "Обчислювальний модуль (SoM / CM4)", size=14, color=POS, bold=True))
    frags.append(text(som_x + som_w / 2, som_y + 46, "Високощільна плата: 6–10 шарів HDI", size=11, color=MUTED))

    # Внутрішні вузли SoM
    frags.append(fitbox(som_x + 20, som_y + 65, 150, 60, "MPU / SoC\nCortex-A / 64-bit", size=12, bold=True, fill="#fff", stroke=POS))
    frags.append(fitbox(som_x + 190, som_y + 65, 150, 60, "LPDDR4 RAM\n1–8 ГБ, 32-bit bus", size=12, bold=True, fill="#fff", stroke=LINE))
    frags.append(fitbox(som_x + 20, som_y + 140, 150, 60, "eMMC / Flash\n8–64 ГБ пам'ять", size=12, bold=True, fill="#fff", stroke=LINE))
    frags.append(fitbox(som_x + 190, som_y + 140, 150, 60, "PMIC живлення\n0.8В, 1.1В, 1.8В, 3.3В", size=12, bold=True, fill="#fff", stroke=POS))

    # Властивості розводки SoM
    frags.append(rect(som_x + 20, som_y + 215, 320, 75, fill="#fff", stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(som_x + 180, som_y + 238,
                       ["Критична трасування швидкісних шин",
                        "Вирівнювання довжин DDR4 (±0.1 мм)",
                        "Послідовність живлення (Power Sequencing)"],
                       size=10, color=INK, lh=1.35))

    # Опис у дереві пристроїв для SoM
    frags.append(fitbox(som_x + 20, som_y + 305, 320, 65,
                        "Опис у Linux: soc.dtsi + som.dtsi\n(ядро, контролери шин, пам'ять eMMC, PMIC)",
                        size=11, bold=True, fill="#fbebe8", stroke=POS))

    # Правий блок: Плата-носій (Carrier Board)
    car_x, car_y, car_w, car_h = 540, 80, 360, 390
    frags.append(rect(car_x, car_y, car_w, car_h, fill="#f2f7f4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(car_x + car_w / 2, car_y + 28, "Плата-носій (Carrier Board)", size=14, color=FIELD, bold=True))
    frags.append(text(car_x + car_w / 2, car_y + 46, "Цільова плата: 2–4 шари, 6/6 mil", size=11, color=MUTED))

    # Вузли плати-носія
    frags.append(fitbox(car_x + 20, car_y + 65, 150, 60, "Живлення 9–36 В\nDC-DC Buck → 5В/3.3В", size=12, bold=True, fill="#fff", stroke=FIELD))
    frags.append(fitbox(car_x + 190, car_y + 65, 150, 60, "Ethernet MagJack\n+ RS-485 / CAN PHY", size=12, bold=True, fill="#fff", stroke=LINE))
    frags.append(fitbox(car_x + 20, car_y + 140, 150, 60, "I2C RTC + EEPROM\nДатчики температури", size=12, bold=True, fill="#fff", stroke=LINE))
    frags.append(fitbox(car_x + 190, car_y + 140, 150, 60, "Роз'єми I/O\nUSB, клемники, реле", size=12, bold=True, fill="#fff", stroke=FIELD))

    # Властивості плати-носія
    frags.append(rect(car_x + 20, car_y + 215, 320, 75, fill="#fff", stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(car_x + 180, car_y + 238,
                       ["Низька вартість виготовлення плати",
                        "Змінні формфактори під корпус приладу",
                        "Захист інтерфейсів (TVS, ізоляція)"],
                       size=10, color=INK, lh=1.35))

    # Опис у дереві пристроїв для плати-носія
    frags.append(fitbox(car_x + 20, car_y + 305, 320, 65,
                        "Опис у Linux: carrier-board.dts\n(ввімкнення I2C/SPI, пінмукс, адреси датчиків)",
                        size=11, bold=True, fill="#e5f2ea", stroke=FIELD))

    # З'єднувальні стрілки (Board-to-Board роз'єм) у проміжку 400..540
    frags.append(arrow(som_x + som_w, 230, 420, 230, color=LINE, sw=1.8))
    frags.append(arrow(car_x, 270, 520, 270, color=LINE, sw=1.8))
    frags.append(rect(420, 215, 100, 70, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    frags.append(mtext(470, 244, ["B2B роз'єм", "100–260 pin", "Hirose / M.2"], size=10, color=INK, bold=True))

    render(os.path.join(OUT, 'som-carrier-split.svg'), W, H, *frags,
           title="Архітектурний розподіл: модуль SoM та плата-носій")


# ── Фігура 2: Ієрархія файлів DTS та процес завантаження ─────────────────────
def device_tree_compilation_flow():
    W, H = 860, 490
    frags = []

    frags.append(text(W / 2, 46, "Від вихідних файлів DTS до структур ядра Linux під час завантаження",
                      size=13, color=MUTED))

    # 1. Шар вихідних файлів (DTS / DTSI)
    x1 = 40
    frags.append(rect(x1, 80, 200, 360, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(x1 + 100, 106, "1. Декларативний опис", size=12, color=INK, bold=True))

    frags.append(fitbox(x1 + 15, 125, 170, 55, "soc.dtsi\n(Базовий SoC від кремнієвого вендора)", size=10, fill="#ffffff", stroke=MUTED))
    frags.append(arrow(x1 + 100, 180, x1 + 100, 195, color=MUTED, sw=1.5))
    frags.append(fitbox(x1 + 15, 200, 170, 55, "som.dtsi\n(Обв'язка модуля від виробника SoM)", size=10, fill="#ffffff", stroke=POS))
    frags.append(arrow(x1 + 100, 255, x1 + 100, 270, color=MUTED, sw=1.5))
    frags.append(fitbox(x1 + 15, 275, 170, 65, "carrier-board.dts\n(Виводи й сенсори вашої плати-носія)", size=10, bold=True, fill="#eaf6ec", stroke=FIELD))
    frags.append(fitbox(x1 + 15, 360, 170, 60, "overlay.dtso\n(Динамічні оверлеї для плат розширення)", size=10, fill="#fdf3e7", stroke="#d97706"))

    # Стрілка компілятора dtc
    frags.append(arrow(x1 + 200, 290, 280, 290, color=LINE, sw=2))
    frags.append(text(240, 280, "dtc", size=12, color=INK, bold=True))

    # 2. Шар скомпільованого блобу (DTB)
    x2 = 280
    frags.append(rect(x2, 190, 170, 190, fill="#f0f4f8", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(x2 + 85, 218, "2. Бінарний блоб", size=12, color=INK, bold=True))
    frags.append(fitbox(x2 + 15, 240, 140, 55, "carrier.dtb\n(Плоске дерево FDT)", size=11, bold=True, fill="#fff", stroke=LINE))
    frags.append(fitbox(x2 + 15, 310, 140, 55, "overlay.dtbo\n(Фрагменти з phandle)", size=10, fill="#fff", stroke="#d97706"))

    # Стрілка передачі в завантажувач
    frags.append(arrow(x2 + 170, 290, 490, 290, color=LINE, sw=2))
    frags.append(text(470, 280, "U-Boot", size=11, color=MUTED))

    # 3. Шар ядра Linux під час завантаження
    x3 = 490
    frags.append(rect(x3, 80, 330, 360, fill="#eef2ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(x3 + 165, 106, "3. Ядро Linux (Runtime)", size=12, color=NEG, bold=True))

    frags.append(fitbox(x3 + 20, 125, 290, 60, "of_fdt_unflatten_tree()\nРозгортання блобу в пам'ять RAM у дерево struct device_node", size=10, fill="#fff", stroke=NEG))
    frags.append(arrow(x3 + 165, 185, x3 + 165, 205, color=NEG, sw=1.5))
    frags.append(fitbox(x3 + 20, 205, 290, 60, "of_platform_default_populate()\nРеєстрація вузлів платформи, шин I2C, SPI, UART та пінмуксу", size=10, fill="#fff", stroke=NEG))
    frags.append(arrow(x3 + 165, 265, x3 + 165, 285, color=NEG, sw=1.5))
    frags.append(fitbox(x3 + 20, 285, 290, 60, "Зіставлення драйверів (Driver Probe)\nof_match_table узгоджує сумісність за рядком compatible", size=10, bold=True, fill="#eef6ee", stroke=FIELD))
    frags.append(fitbox(x3 + 20, 360, 290, 60, "Експорт у простір користувача:\n/sys/firmware/devicetree/base  та  /proc/device-tree", size=10, fill="#fff", stroke=LINE))

    render(os.path.join(OUT, 'device-tree-compilation-flow.svg'), W, H, *frags,
           title="Ланцюг Device Tree: від опису до зв'язування драйверів")


# ── Фігура 3: Механізм конфігурації виводів (pinctrl) та драйверного зв'язування ─
def pinmux_and_probe_flow():
    W, H = 840, 480
    frags = []

    frags.append(text(W / 2, 44, "Механізм зв'язування: вузол DTS → налаштування pinctrl → виклик probe() драйвера",
                      size=13, color=MUTED))

    # Верхній блок: Вузол у Device Tree
    dts_x, dts_y, dts_w, dts_h = 60, 70, 720, 110
    frags.append(rect(dts_x, dts_y, dts_w, dts_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(dts_x + 180, dts_y + 22, "Вузол пристрою у файлі carrier-board.dts", size=12, color=INK, bold=True))
    frags.append(rect(dts_x + 20, dts_y + 32, 680, 66, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(dts_x + 360, dts_y + 54,
                       ["&i2c1 { status = \"okay\"; pinctrl-0 = <&i2c1_pins>;",
                        "  temp_sensor: sensor@48 { compatible = \"ti,tmp102\"; reg = <0x48>; };",
                        "};"],
                       size=11, color=INK, lh=1.35))

    # Стрілка вниз до розділення на дві підсистеми (з відступом для підписів)
    frags.append(arrow(210, dts_y + dts_h, 210, 230, color=LINE, sw=1.8))
    frags.append(text(225, 205, "pinctrl phandle", size=10, color=MUTED, anchor="start"))

    frags.append(arrow(580, dts_y + dts_h, 580, 230, color=LINE, sw=1.8))
    frags.append(text(595, 205, "compatible + reg", size=10, color=MUTED, anchor="start"))

    # Ліва колонка: Підсистема Pinctrl (Апаратні мультиплексори виводів)
    px, py, pw, ph = 60, 230, 340, 200
    frags.append(rect(px, py, pw, ph, fill="#fef8f6", stroke=POS, sw=1.5, rx=6))
    frags.append(text(px + pw / 2, py + 24, "Підсистема pinctrl / pinmux", size=13, color=POS, bold=True))

    frags.append(fitbox(px + 20, py + 42, 300, 48, "1. Читання групи пінів\nGPIO2 (SDA), GPIO3 (SCL)", size=10, fill="#fff", stroke=POS))
    frags.append(fitbox(px + 20, py + 98, 300, 48, "2. Запис у регістри SoC\nALT0 (I2C функція) + Pull-up", size=10, fill="#fff", stroke=POS))
    frags.append(fitbox(px + 20, py + 154, 300, 36, "Фізичні виводи B2B підключені до шини", size=10, bold=True, fill="#fbebe8", stroke=POS))

    # Права колонка: Підсистема драйверів I2C (Driver Core Matching)
    dx, dy, dw, dh = 440, 230, 340, 200
    frags.append(rect(dx, dy, dw, dh, fill="#f2f7f4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(dx + dw / 2, dy + 24, "Підсистема I2C та Driver Core", size=13, color=FIELD, bold=True))

    frags.append(fitbox(dx + 20, dy + 42, 300, 48, "1. Створення клієнта I2C\nАдреса 0x48 на шині /dev/i2c-1", size=10, fill="#fff", stroke=FIELD))
    frags.append(fitbox(dx + 20, dy + 98, 300, 48, "2. Зіставлення of_match_table\nРядок \"ti,tmp102\" знаходить tmp102.c", size=10, fill="#fff", stroke=FIELD))
    frags.append(fitbox(dx + 20, py + 154, 300, 36, "Виклик probe() → поява /sys/class/hwmon/", size=10, bold=True, fill="#e5f2ea", stroke=FIELD))

    render(os.path.join(OUT, 'pinmux-and-probe-flow.svg'), W, H, *frags,
           title="Маршрутизація властивостей DTS: пінмукс і зв'язування драйвера")


if __name__ == '__main__':
    som_carrier_split()
    device_tree_compilation_flow()
    pinmux_and_probe_flow()
    print("Figures generated successfully!")
