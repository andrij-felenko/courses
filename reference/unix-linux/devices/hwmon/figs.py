# -*- coding: utf-8 -*-
"""Фігури до теми «hwmon: клас датчиків у ядрі й одиниці в sysfs»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_BG = "#eaf0fd"
GREEN_BG = "#e6f5ec"
WARM_BG = "#fff4e0"
GREY_BG = "#eef0f3"
GOLD = "#b8860b"


# ── 1. Від регістра до числа на екрані ──────────────────────────────────────
def fig_raw_to_file():
    W, H = 1420, 560
    P = []
    P.append(text(W / 2, 42, "Сире число має сенс лише поруч зі своєю мікросхемою",
                  size=18, bold=True))

    boxes = [
        (40, "МІКРОСХЕМА\n\nрегістр 0x1A80\n9 значущих бітів,\nкрок 0.5 °C", BLUE_BG, NEG),
        (390, "ДРАЙВЕР\n\n(s16)reg >> 7 → 53\n53 × 500 → 26500\nзнає саме цей чип", WARM_BG, GOLD),
        (740, "ЯДРО, клас hwmon\n\ntemp1_input = 26500\nодиниця задана\nтипом каналу", GREY_BG, INK),
        (1090, "ПРОГРАМА\n\nчитає текст «26500»\nділить на 1000\nпоказує 26.5 °C", GREEN_BG, FIELD),
    ]
    for x, s, fill, stroke in boxes:
        P.append(fitbox(x, 90, 290, 190, s, size=14, fill=fill, stroke=stroke, sw=2))

    for x in (330, 680, 1030):
        P.append(arrow(x, 185, x + 56, 185, color=MUTED, sw=2))

    P.append(text(358, 165, "I²C", size=12, color=MUTED))
    P.append(text(708, 165, "long", size=12, color=MUTED))
    P.append(text(1058, 165, "sysfs", size=12, color=MUTED))

    P.append(fitbox(40, 330, 640, 90,
                    "ЛІВОРУЧ ВІД МЕЖІ\nтреба знати мікросхему: розрядність,\nкрок, вирівнювання, знак",
                    size=13.5, fill=BG, stroke=NEG, sw=2))
    P.append(fitbox(780, 330, 600, 90,
                    "ПРАВОРУЧ ВІД МЕЖІ\nдосить знати одиницю:\nмілі°C для будь-якого чипа",
                    size=13.5, fill=BG, stroke=FIELD, sw=2))
    P.append(line(720, 300, 720, 450, color=POS, sw=2.5, dash="7,5"))
    P.append(text(720, 470, "межа знання про залізо", size=13, color=POS))

    P.append(fitbox(40, 480, 1340, 56,
                    "мороз перевіряє знак: 0xE480 → як s16 −7040 → >> 7 = −55 → × 500 = −27500 → −27.5 °C",
                    size=13.5, fill=GREY_BG, stroke=MUTED, sw=1.5))

    render(os.path.join(OUT, "raw-to-file.svg"), W, H, *P)


# ── 2. Дві проєкції одного пристрою hwmon ───────────────────────────────────
def fig_hwmon_tree():
    W, H = 1400, 620
    P = []
    P.append(text(W / 2, 42, "Один пристрій — два шляхи до нього", size=18, bold=True))

    P.append(text(280, 92, "КЛАС: плаский список", size=15, bold=True, color=NEG))
    P.append(fitbox(60, 115, 460, 210,
                    "/sys/class/hwmon/\n"
                    "    hwmon0  →  …\n"
                    "    hwmon1  →  …\n"
                    "    hwmon3  →  наш датчик\n\n"
                    "номер = порядок реєстрації,\nпісля перезавантаження інший",
                    size=13.5, fill=BLUE_BG, stroke=NEG, sw=2))

    P.append(text(1010, 92, "ДЕРЕВО: фізична адреса", size=15, bold=True, color=FIELD))
    P.append(fitbox(700, 115, 640, 210,
                    "/sys/devices/platform/soc/i2c-1/\n"
                    "    1-004c/            ← чип за адресою 0x4c\n"
                    "        driver  →  lm75\n"
                    "        hwmon/hwmon3/  ← справжнє місце\n\n"
                    "шлях міняється лише разом із залізом",
                    size=13.5, fill=GREEN_BG, stroke=FIELD, sw=2))

    P.append(arrow(524, 195, 696, 195, color=NEG, sw=2))
    P.append(text(610, 175, "символьне посилання", size=12.5, color=MUTED))
    P.append(arrow(696, 250, 524, 250, color=FIELD, sw=2))
    P.append(text(610, 285, "файл device веде назад", size=12.5, color=MUTED))

    P.append(fitbox(60, 370, 1280, 130,
                    "ЩО ЛЕЖИТЬ У КАТАЛОЗІ hwmon3\n"
                    "name  ← єдиний обов'язковий: «lm75», малими, без пробілів і дефісів\n"
                    "temp1_input  temp1_max  temp1_crit  temp1_label   fan1_input  fan1_fault   pwm1  pwm1_enable",
                    size=13.5, fill=GREY_BG, stroke=INK, sw=2))

    P.append(fitbox(60, 530, 1280, 66,
                    "шукати датчик треба за вмістом name, а не за числом у hwmonN: "
                    "число нічого не гарантує між завантаженнями",
                    size=13.5, fill=BG, stroke=POS, sw=2))

    render(os.path.join(OUT, "hwmon-tree.svg"), W, H, *P)


# ── 3. Оголошення каналів → файли ───────────────────────────────────────────
def fig_channels_to_files():
    W, H = 1400, 640
    P = []
    P.append(text(W / 2, 42, "Драйвер оголошує канали — файли створює ядро",
                  size=18, bold=True))

    P.append(fitbox(50, 90, 430, 230,
                    "ДРАЙВЕР ОГОЛОШУЄ\n\n"
                    "temp: INPUT | MAX | CRIT\n"
                    "temp: INPUT | LABEL\n"
                    "fan:  INPUT | FAULT\n\n"
                    "жодного імені файла тут нема",
                    size=14, fill=WARM_BG, stroke=GOLD, sw=2))

    P.append(fitbox(560, 90, 280, 230,
                    "ЯДРО, клас hwmon\n\nрозгортає маски\nв атрибути\n\nперевіряє ім'я\nпристрою",
                    size=14, fill=GREY_BG, stroke=INK, sw=2))

    P.append(fitbox(920, 90, 430, 230,
                    "ЯДРО СТВОРЮЄ ФАЙЛИ\n\n"
                    "temp1_input  temp1_max\n"
                    "temp1_crit\n"
                    "temp2_input  temp2_label\n"
                    "fan1_input   fan1_fault",
                    size=14, fill=GREEN_BG, stroke=FIELD, sw=2))

    P.append(arrow(484, 170, 556, 170, color=GOLD, sw=2))
    P.append(arrow(844, 170, 916, 170, color=FIELD, sw=2))

    P.append(text(700, 372, "звертання йде у зворотний бік", size=15, bold=True, color=NEG))

    P.append(fitbox(920, 400, 430, 92,
                    "читання файла temp2_input\nз простору користувача",
                    size=13.5, fill=BLUE_BG, stroke=NEG, sw=2))
    P.append(fitbox(50, 400, 430, 92,
                    "read(dev, hwmon_temp,\n     hwmon_temp_input, channel = 1, &val)",
                    size=13.5, fill=BLUE_BG, stroke=NEG, sw=2))
    P.append(arrow(916, 446, 486, 446, color=NEG, sw=2))
    P.append(text(700, 428, "ядро перекладає ім'я на трійку", size=12.5, color=MUTED))

    P.append(fitbox(50, 530, 1300, 88,
                    "драйвер повертає число в одиниці свого типу — і не має можливості "
                    "ані назвати файл по-своєму,\nані підсунути градуси туди, де ядро вже пообіцяло мілі°C",
                    size=13.5, fill=BG, stroke=MUTED, sw=2))

    render(os.path.join(OUT, "channels-to-files.svg"), W, H, *P)


# ── 4. Знак у зсуві: та сама шістнадцяткова, два різні типи ─────────────────
def fig_sign_extension():
    W, H = 1340, 520
    P = []
    P.append(text(W / 2, 44, "Одне слово з шини, два типи змінної — і два різні світи",
                  size=18, bold=True))

    P.append(fitbox(330, 78, 680, 76,
                    "з шини прийшло слово 0xE480\n1110 0100 1000 0000₂",
                    size=15, fill=GREY_BG, stroke=INK, sw=2, bold=True))

    P.append(fitbox(60, 200, 580, 200,
                    "ПОМИЛКОВО — беззнаковий тип\n"
                    "u16 reg = 0xE480;          →   58496\n"
                    "reg >> 7   (зсув затягує нулі)  →   457\n"
                    "457 × 500                       →   228500\n"
                    "temp1_input = 228500   =   +228.5 °C",
                    size=14, fill="#fdecea", stroke=POS, sw=2))

    P.append(fitbox(700, 200, 580, 200,
                    "ПРАВИЛЬНО — знаковий тип\n"
                    "s16 reg = 0xE480;          →   −7040\n"
                    "reg >> 7   (зсув тягне знак)    →   −55\n"
                    "−55 × 500                       →   −27500\n"
                    "temp1_input = −27500   =   −27.5 °C",
                    size=14, fill=GREEN_BG, stroke=FIELD, sw=2))

    P.append(fitbox(60, 434, 1220, 62,
                    "Різниця вся в типі: над беззнаковим зсув вправо затягує згори нулі, "
                    "над знаковим — копії старшого біта.\nМороз перетворюється на пожежу, і жоден "
                    "компілятор про це не попередить.",
                    size=13.5, fill=BG, stroke=MUTED, sw=2))

    render(os.path.join(OUT, "sign-extension.svg"), W, H, *P)


# ── 5. Чому пара «вибір регістра + читання» мусить бути неподільною ─────────
def fig_bus_race():
    W, H = 1420, 660
    P = []
    P.append(text(W / 2, 40, "Вибір регістра й читання розірвано — читачі забирають відповіді один в одного",
                  size=18, bold=True))

    P.append(text(96, 118, "Читач A", size=14, bold=True, anchor="start", color=NEG))
    P.append(text(96, 232, "Читач B", size=14, bold=True, anchor="start", color=POS))

    P.append(fitbox(220, 84, 300, 68, "пише 0x00\n«далі — температура»",
                    size=13, fill=BLUE_BG, stroke=NEG, sw=2))
    P.append(fitbox(560, 198, 300, 68, "пише 0x03\n«далі — межа»",
                    size=13, fill="#fdecea", stroke=POS, sw=2))
    P.append(fitbox(900, 84, 320, 68, "читає слово →\nдістає МЕЖУ",
                    size=13, fill=BLUE_BG, stroke=POS, sw=2))
    P.append(fitbox(1240, 198, 150, 68, "читає\nмежу",
                    size=13, fill="#fdecea", stroke=POS, sw=2))

    P.append(arrow(200, 316, 1390, 316, color=MUTED, sw=2))
    P.append(text(200, 340, "час на шині", size=13, color=MUTED, anchor="start"))

    P.append(fitbox(220, 356, 1170, 62,
                    "покажчик регістра один на всіх — його перезаписав той, хто прийшов другим;\n"
                    "так буває, коли вибір і читання зроблено двома окремими командами",
                    size=13.5, fill=BG, stroke=POS, sw=2))

    P.append(line(60, 448, 1380, 448, color=MUTED, sw=1.5, dash="6 6"))

    P.append(text(W / 2, 490, "З м'ютексом пара «вибір регістра + читання» неподільна",
                  size=18, bold=True))

    P.append(fitbox(220, 520, 470, 76,
                    "A тримає замок:\n0x00 → читання → температура",
                    size=13, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(fitbox(830, 520, 470, 76,
                    "потім замок у B:\n0x03 → читання → межа",
                    size=13, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(arrow(700, 558, 820, 558, color=FIELD, sw=2))

    P.append(fitbox(220, 614, 1080, 40,
                    "той самий замок закриває і кеш — тож ніхто не побачить напівоновленого запису",
                    size=13.5, fill=BG, stroke=MUTED, sw=2))

    render(os.path.join(OUT, "bus-race.svg"), W, H, *P)


if __name__ == "__main__":
    fig_raw_to_file()
    fig_hwmon_tree()
    fig_channels_to_files()
    fig_sign_extension()
    fig_bus_race()
    print("готово")
