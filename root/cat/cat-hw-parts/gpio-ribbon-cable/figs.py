# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори за функцією піна
C_33 = "#fde3c7"   # 3.3 В — теплий пісочний
C_5V = "#f6c9c2"   # 5 В — теплий червонястий
C_GND = "#d8dee6"  # земля — сірий
C_IO = "#e6eefb"   # сигнальний GPIO — холодний блакитний
ACCENT = "#2457d6"
REDW = "#c0392b"

# Повна розпіновка 40-pin заголовка RPi: (фізичний_пін, підпис, колір)
# Дані звірені з pinout.xyz / SparkFun (усталено).
PINS = {
    1: ("3.3 В", C_33),   2: ("5 В", C_5V),
    3: ("GPIO2 SDA", C_IO), 4: ("5 В", C_5V),
    5: ("GPIO3 SCL", C_IO), 6: ("GND", C_GND),
    7: ("GPIO4", C_IO),   8: ("GPIO14 TX", C_IO),
    9: ("GND", C_GND),   10: ("GPIO15 RX", C_IO),
    11: ("GPIO17", C_IO), 12: ("GPIO18", C_IO),
    13: ("GPIO27", C_IO), 14: ("GND", C_GND),
    15: ("GPIO22", C_IO), 16: ("GPIO23", C_IO),
    17: ("3.3 В", C_33), 18: ("GPIO24", C_IO),
    19: ("GPIO10 MOSI", C_IO), 20: ("GND", C_GND),
    21: ("GPIO9 MISO", C_IO), 22: ("GPIO25", C_IO),
    23: ("GPIO11 SCLK", C_IO), 24: ("GPIO8 CE0", C_IO),
    25: ("GND", C_GND), 26: ("GPIO7 CE1", C_IO),
    27: ("ID_SD", C_IO), 28: ("ID_SC", C_IO),
    29: ("GPIO5", C_IO), 30: ("GND", C_GND),
    31: ("GPIO6", C_IO), 32: ("GPIO12", C_IO),
    33: ("GPIO13", C_IO), 34: ("GND", C_GND),
    35: ("GPIO19", C_IO), 36: ("GPIO16", C_IO),
    37: ("GPIO26", C_IO), 38: ("GPIO20", C_IO),
    39: ("GND", C_GND), 40: ("GPIO21", C_IO),
}


def _pin_cell(x, y, w, h, num, label, color):
    """Одна клітинка піна: номер + підпис усередині рамки."""
    out = rect(x, y, w, h, fill=color, stroke="#7c8798", sw=1.2, rx=4)
    out += text(x + 22, y + h / 2 + 5, str(num), size=14, bold=True, color="#1a2330")
    out += text(x + 46, y + h / 2 + 5, label, size=12.5, anchor="start", color="#1a2330")
    return out


def fig_map():
    """Що несе шлейф: увесь 40-pin заголовок, дві колонки, підсвічені за функцією."""
    cw, ch = 160, 30       # клітинка піна
    colgap = 26            # проміжок між колонками (де ключ-паз)
    top = 92
    x_odd = 60
    x_even = x_odd + cw + colgap
    rows = 20
    W = x_even + cw + 60
    H = top + rows * (ch + 4) + 44

    parts = []
    # Тонка «стрічка» шлейфа зверху, з червоною жилою біля піна 1
    ribbon_y = top - 34
    parts.append(rect(x_odd, ribbon_y, x_even + cw - x_odd, 14, fill="#eceff3", stroke="#9aa4b2", sw=1.2, rx=3))
    parts.append(rect(x_odd, ribbon_y, 6, 14, fill=REDW, stroke=REDW, sw=1, rx=2))
    parts.append(text(x_even + cw, ribbon_y + 11, "червона жила = пін 1", size=12, anchor="end", color=REDW, bold=True))

    # Дві колонки: непарні ліворуч (зовнішній край), парні праворуч
    for r in range(rows):
        y = top + r * (ch + 4)
        odd = 2 * r + 1
        even = 2 * r + 2
        lo, co = PINS[odd]
        le, ce = PINS[even]
        parts.append(_pin_cell(x_odd, y, cw, ch, odd, lo, co))
        parts.append(_pin_cell(x_even, y, cw, ch, even, le, ce))

    # Позначка кутового піна 1 (квадратна пляма)
    parts.append(rect(x_odd - 12, top - 2, 8, 8, fill=REDW, stroke=REDW, sw=1, rx=0))
    parts.append(text(x_odd - 8, top + ch + 26, "◤ пін 1", size=12, anchor="middle", color=REDW, bold=True))

    # Легенда кольорів — компактні плашки внизу
    ly = H - 22
    lx = 60
    for lbl, col in [("3.3 В", C_33), ("5 В", C_5V), ("GND", C_GND), ("сигнал GPIO", C_IO)]:
        parts.append(rect(lx, ly - 12, 16, 16, fill=col, stroke="#7c8798", sw=1, rx=3))
        w = text_width(lbl, 12) + 30
        parts.append(text(lx + 22, ly, lbl, size=12, anchor="start", color="#1a2330"))
        lx += w + 26

    render(os.path.join(IMG, "pinout-map.svg"), W, H, *parts,
           title="Що несе 40-жильний шлейф: увесь заголовок RPi пін-у-пін")


def fig_flip():
    """Пастка дзеркала: 1:1-шлейф, але дальній роз'єм не з того боку — парні й непарні міняються."""
    W, H = 860, 470
    parts = []

    bx, bw = 60, 300      # ліва плата (RPi)
    px = 500              # права плата (периферія)
    top = 74
    ch = 26
    rowsN = 6             # покажемо перші 6 пінів — досить, щоб побачити ефект

    # Заголовки колонок
    parts.append(text(bx + bw / 2, top - 18, "Raspberry Pi (пін 1 угорі)", size=14, bold=True, color=ACCENT))
    parts.append(text(px + bw / 2, top - 18, "периферія — роз'єм з НЕ того боку", size=14, bold=True, color=REDW))

    left_pins = [(i + 1, PINS[i + 1][0], PINS[i + 1][1]) for i in range(rowsN)]
    # Праворуч роз'єм перевернувся боком → у тій самій фізичній позиції опиняється сусідній пін:
    # 1↔2, 3↔4, 5↔6 (парні й непарні помінялись). Показуємо, куди фактично лягла жила.
    swap = {1: 2, 2: 1, 3: 4, 4: 3, 5: 6, 6: 5}

    for r in range(rowsN):
        y = top + r * (ch + 8)
        num, lbl, col = left_pins[r]
        # ліва клітинка
        parts.append(rect(bx, y, bw, ch, fill=col, stroke="#7c8798", sw=1.2, rx=4))
        parts.append(text(bx + 20, y + ch / 2 + 5, str(num), size=13, bold=True, color="#1a2330"))
        parts.append(text(bx + 40, y + ch / 2 + 5, lbl, size=12, anchor="start", color="#1a2330"))

        # права клітинка — той пін, що фактично там опинився
        rn = swap[num]
        rl, rc = PINS[rn][0], PINS[rn][1]
        parts.append(rect(px, y, bw, ch, fill=rc, stroke="#7c8798", sw=1.2, rx=4))
        parts.append(text(px + 20, y + ch / 2 + 5, str(rn), size=13, bold=True, color="#1a2330"))
        parts.append(text(px + 40, y + ch / 2 + 5, rl, size=12, anchor="start", color="#1a2330"))

        # лінія-жила через увесь проміжок (1:1 фізично, але дзеркало міняє сусідів)
        parts.append(line(bx + bw, y + ch / 2, px, y + ch / 2, color="#9aa4b2", sw=1.4, dash="4 4"))

    # Підсвітити небезпеку: 5 В (пін 2) лягла туди, де RPi чекає 3.3 В (пін 1)
    warn_y = top
    parts.append(rect(bx - 6, warn_y - 6, bw + 12, ch + 12, fill="none", stroke=REDW, sw=2.2, rx=7))
    parts.append(text(W / 2, H - 40, "пін 1 (3.3 В) ліворуч зустрічає пін 2 (5 В) праворуч → на 3.3-вольтову лінію йде 5 В",
                      size=13, color=REDW, bold=True))
    parts.append(text(W / 2, H - 20, "жили йдуть 1:1 через стрічку — плутає не шлейф, а бік роз'єму на дальній платі",
                      size=12.5, color="#4a5568"))

    render(os.path.join(IMG, "mirror-flip.svg"), W, H, *parts,
           title="Пастка дзеркала: сам шлейф прямий, а перевернутий бік міняє сусідів")


if __name__ == "__main__":
    fig_map()
    fig_flip()
    print("OK: figures written")
