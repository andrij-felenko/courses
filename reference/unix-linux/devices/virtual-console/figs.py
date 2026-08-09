# -*- coding: utf-8 -*-
"""Фігури до теми «Віртуальна консоль Linux: емулятор термінала всередині ядра»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_vt_loop():
    """Дві половини віртуальної консолі: шлях виводу вниз і шлях вводу вгору."""
    W, H = 1120, 660
    g = []

    LX, RX, CW = 40, 640, 440
    LC, RC = LX + CW / 2.0, RX + CW / 2.0
    ROWS = [130, 218, 306, 394, 482]
    BH = 60

    g.append(fitbox(240, 44, 640, 52,
                    "оболонка на цій консолі: write(1, …) і read(0, …)",
                    size=15, bold=True, fill="#eef2f7", stroke=NEG))

    out_rows = [
        "лінійна дисципліна на виході:\nOPOST, ONLCR — що дописати перед видачею",
        "емулятор VT (drivers/tty/vt/vt.c):\nавтомат над потоком, стан курсора й кольорів",
        "буфер екрана: на кожне знакомісце\n16 біт — номер гліфа й атрибут",
        "драйвер консолі (struct consw):\nfbcon, vgacon або dummycon",
        "текстова пам'ять плати\nабо пікселі кадрового буфера → екран",
    ]
    in_rows = [
        "лінійна дисципліна на вході:\nICANON, ECHO, ISIG — рядок, відлуння, сигнали",
        "черга вводу того tty,\nдо якого прив'язана поточна консоль",
        "keyboard.c: розкладка перетворює\nклавішу на байти або на дію",
        "підсистема вводу: номер клавіші\nплюс позначка натиску чи відпускання",
        "клавіатура: PS/2, USB або Bluetooth",
    ]

    for i, y in enumerate(ROWS):
        g.append(fitbox(LX, y, CW, BH, out_rows[i], size=12.5,
                        fill="#fdf3f2" if i < 4 else "#f7f3e8", stroke=POS if i < 4 else MUTED))
        g.append(fitbox(RX, y, CW, BH, in_rows[i], size=12.5,
                        fill="#eaf0fd" if i > 0 else "#eaf0fd", stroke=NEG))

    g.append(arrow(LC, 100, LC, ROWS[0] - 4, color=POS, sw=1.7))
    for i in range(len(ROWS) - 1):
        y0 = ROWS[i] + BH
        y1 = ROWS[i + 1]
        g.append(arrow(LC, y0 + 4, LC, y1 - 4, color=POS, sw=1.7))

    g.append(arrow(RC, ROWS[0] - 4, RC, 100, color=NEG, sw=1.7))
    for i in range(len(ROWS) - 1):
        y0 = ROWS[i] + BH
        y1 = ROWS[i + 1]
        g.append(arrow(RC, y1 - 4, RC, y0 + 4, color=NEG, sw=1.7))

    g.append(text(150, 118, "вивід: байти треба зрозуміти",
                  size=13, color=POS, bold=True, anchor="start"))
    g.append(text(1010, 118, "ввід: байтів немає, їх треба вигадати",
                  size=13, color=NEG, bold=True, anchor="end"))

    g.append(fitbox(40, 566, 1040, 62,
                    "Alt+F2 далі keyboard.c не йде: перемикання консолі — це дія розкладки, а не байт.\n"
                    "Тому воно спрацьовує й тоді, коли програма на екрані зависла і нічого не читає",
                    size=13.5, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, 'vt-loop.svg'), W, H, *g,
           title="Шлях виводу й шлях вводу у віртуальній консолі")


def fig_cell_to_pixels():
    """Одна комірка буфера екрана й два перетворення, які з неї роблять зображення."""
    W, H = 1080, 560
    g = []

    g.append(fitbox(60, 36, 400, 54,
                    "поточні кольори емулятора:\nтекст, тло, яскравість, блимання",
                    size=13, fill="#fdf3f2", stroke=POS))
    g.append(fitbox(620, 36, 400, 54,
                    "байти від програми: UTF-8 →\nкод символу Unicode, напр. U+0414",
                    size=13, fill="#eaf0fd", stroke=NEG))

    g.append(fitbox(620, 126, 400, 54,
                    "таблиця unimap:\nкод Unicode → номер гліфа",
                    size=13, fill="#eaf0fd", stroke=NEG))

    g.append(arrow(820, 96, 820, 120, color=NEG, sw=1.7))
    g.append(arrow(260, 96, 260, 214, color=POS, sw=1.7))
    g.append(arrow(820, 186, 820, 214, color=NEG, sw=1.7))

    g.append(text(540, 208, "комірка буфера екрана — 16 біт",
                  size=13, color=MUTED, bold=True))
    g.append(fitbox(60, 220, 400, 60, "старший байт: атрибут", size=14, bold=True,
                    fill="#fdecea", stroke=POS))
    g.append(fitbox(620, 220, 400, 60, "молодший байт: номер гліфа", size=14, bold=True,
                    fill="#eaf0fd", stroke=NEG))

    g.append(arrow(260, 286, 260, 334, color=POS, sw=1.7))
    g.append(arrow(820, 286, 820, 334, color=NEG, sw=1.7))

    g.append(fitbox(60, 340, 400, 64,
                    "палітра: 8 кольорів, окремий біт\nяскравості й окремий біт блимання",
                    size=13, fill=FILL, stroke=MUTED))
    g.append(fitbox(620, 340, 400, 64,
                    "шрифт консолі: 256 матриць пікселів,\nнапр. 8 на 16 точок",
                    size=13, fill=FILL, stroke=MUTED))

    g.append(arrow(260, 410, 470, 442, color=POS, sw=1.7))
    g.append(arrow(820, 410, 610, 442, color=NEG, sw=1.7))

    g.append(fitbox(300, 448, 480, 54,
                    "fbcon розкладає матрицю в кадровий буфер:\n"
                    "одиничні біти — колір тексту, нульові — колір тла",
                    size=13, fill="#eaf6ee", stroke=FIELD))

    g.append(fitbox(60, 516, 960, 34,
                    "vgacon не робить нічого з цього: та сама пара байтів і є вміст текстової пам'яті відеоплати",
                    size=13, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, 'cell-to-pixels.svg'), W, H,  *g,
           title="Комірка буфера екрана й два перетворення на шляху до пікселів")


def fig_vt_handover():
    """Передача екрана під час перемикання консолі в режимі VT_PROCESS."""
    W, H = 1060, 640
    g = []

    X, BW, BH = 50, 960, 62
    ROWS = [40, 136, 232, 328, 424]

    steps = [
        ("процес", "ioctl(VT_SETMODE) з полем mode = VT_PROCESS: «перемикання цієї консолі\n"
                   "більше не автоматичне; ось номери двох сигналів — relsig і acqsig»", "#eaf0fd", NEG),
        ("ядро", "людина натиснула Alt+F1. Перемалювати екран не можна: відеорежим чужий,\n"
                 "графічним пристроєм порядкує процес. Ядро шле relsig і чекає", "#f7f3e8", MUTED),
        ("процес", "наводить лад: вертає текстовий режим і віддає право розпоряджатися\n"
                   "графічним пристроєм", "#eaf0fd", NEG),
        ("процес", "ioctl(VT_RELDISP, 1) — «віддав, перемикай»", "#eaf0fd", NEG),
        ("ядро", "аж тепер перемикає: зберігає стан старої консолі, повідомляє драйвер консолі\n"
                 "й перемальовує екран з буфера нової", "#eaf6ee", FIELD),
    ]

    for i, (who, what, fill, stroke) in enumerate(steps):
        y = ROWS[i]
        g.append(fitbox(X, y, 130, BH, who, size=14, bold=True, fill=fill, stroke=stroke))
        g.append(fitbox(X + 146, y, BW - 146, BH, what, size=13, fill=BG, stroke=stroke))
        if i < len(steps) - 1:
            g.append(arrow(X + 65, y + BH + 3, X + 65, ROWS[i + 1] - 3, color=MUTED, sw=1.6))

    g.append(fitbox(X, 512, BW, 52,
                    "Крок 4 не настав — не настає й крок 5: ядро пообіцяло не перемикати самовільно\n"
                    "й чекатиме далі. Саме так виглядає зависання з чорним екраном після падіння графіки",
                    size=13, fill="#fdecea", stroke=POS))
    g.append(fitbox(X, 576, BW, 44,
                    "Повернення дзеркальне: ядро шле acqsig, процес забирає екран назад "
                    "і знову відповідає VT_RELDISP",
                    size=13, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, 'vt-handover.svg'), W, H, *g,
           title="Передача екрана під час перемикання консолі")


if __name__ == '__main__':
    fig_vt_loop()
    fig_cell_to_pixels()
    fig_vt_handover()
    print("ok")
