# -*- coding: utf-8 -*-
"""Фігури до теми «Псевдотермінал: термінал без заліза»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_tty_vs_pty():
    """Що саме замінили: усе вище межі — той самий код ядра."""
    W, H = 1040, 520
    g = []

    LX, LW = 30, 460
    RX, RW = 550, 460

    g.append(fitbox(LX, 54, LW, 42, "справжній послідовний термінал",
                    size=15, bold=True, fill="#fdecea", stroke=POS))
    g.append(fitbox(RX, 54, RW, 42, "псевдотермінал",
                    size=15, bold=True, fill="#eaf7ee", stroke=FIELD))

    rows = [
        ("програма\nread / write на /dev/ttyS0",
         "програма\nread / write на /dev/pts/N", 62, FILL),
        ("лінійна дисципліна\nвідлуння · буфер рядка · ISIG · ONLCR",
         "лінійна дисципліна\nвідлуння · буфер рядка · ISIG · ONLCR", 62, "#eef2f7"),
        ("драйвер UART",
         "драйвер pty", 46, "#eef2f7"),
    ]

    y = 116
    for left, right, h, fill in rows:
        g.append(fitbox(LX, y, LW, h, left, size=13, fill=fill))
        g.append(fitbox(RX, y, RW, h, right, size=13, fill=fill))
        g.append(arrow(LX + LW / 2, y + h + 3, LX + LW / 2, y + h + 21, color=MUTED, sw=1.4))
        g.append(arrow(RX + RW / 2, y + h + 3, RX + RW / 2, y + h + 21, color=MUTED, sw=1.4))
        y += h + 24

    ymid = y + 6
    g.append(line(20, ymid, W - 20, ymid, color=MUTED, sw=1.6, dash="7 6"))
    g.append(text(W / 2, ymid - 10, "межа заміни", size=12, color=MUTED))

    y = ymid + 22
    g.append(fitbox(LX, y, LW, 74,
                    "залізо\nUART → дріт → термінал\nіз клавіатурою й екраном",
                    size=13, fill="#fdecea", stroke=POS))
    g.append(fitbox(RX, y, RW, 74,
                    "ведучий кінець\nзвичайний процес, який пише в нього\nй читає з нього",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    g.append(text(W / 2, y + 106,
                  "усе вище межі — той самий код ядра в обох випадках",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, 'tty-vs-pty.svg'), W, H, *g,
                  title="Що в терміналі було залізом, а що — ядром")


def fig_pty_flows():
    """Два напрямки проходять різну обробку; відлуння народжується в ядрі."""
    W, H = 1080, 540
    g = []

    # межі ядра
    g.append(rect(250, 70, 580, 330, fill="#f8fafc", stroke=MUTED, sw=1.4))
    g.append(text(540, 92, "ядро: пара псевдотермінала", size=13, color=MUTED))

    b, bw, bh = textbox(130, 200,
                        "процес на ведучому кінці\nемулятор, sshd, tmux",
                        size=13, fill="#eaf7ee", stroke=FIELD)
    g.append(b)
    b2, _, _ = textbox(950, 200,
                       "процес на підлеглому кінці\nоболонка, редактор",
                       size=13, fill=FILL)
    g.append(b2)

    # верхня доріжка: ведучий → підлеглий
    g.append(text(540, 128, "напрямок «клавіатура»: write на ведучому → read на підлеглому",
                  size=12, color=MUTED))
    g.append(fitbox(280, 142, 230, 62,
                    "вхідна обробка\nICRNL · ISIG · ECHO", size=12, fill="#eef2f7"))
    g.append(fitbox(560, 142, 230, 62,
                    "канонічний буфер\nрядок віддають після \\n", size=12, fill="#eef2f7"))
    g.append(arrow(212, 173, 278, 173))
    g.append(arrow(512, 173, 558, 173))
    g.append(arrow(792, 173, 878, 173))

    # відлуння
    g.append(arrow(320, 214, 170, 244, color=FIELD, sw=1.6))
    g.append(text(310, 240, "відлуння: байт повертає ядро само,",
                  size=12, color=FIELD, anchor="end"))
    g.append(text(310, 258, "програма на підлеглому кінці ні до чого",
                  size=12, color=FIELD, anchor="end"))

    # сигнал
    g.append(arrow(430, 214, 430, 300, color=POS, sw=1.6))
    g.append(text(444, 300, "SIGINT групі процесів переднього плану",
                  size=12, color=POS, anchor="start"))

    # нижня доріжка: підлеглий → ведучий
    g.append(fitbox(560, 330, 230, 56,
                    "вихідна обробка\nONLCR: \\n → \\r\\n", size=12, fill="#eef2f7"))
    g.append(arrow(878, 358, 794, 358))
    g.append(arrow(558, 358, 212, 358))
    g.append(text(540, 404, "напрямок «екран»: write на підлеглому → read на ведучому",
                  size=12, color=MUTED))

    return render(os.path.join(IMG, 'pty-flows.svg'), W, H, *g,
                  title="Що ядро робить із байтом у кожному напрямку")


def fig_ctrl_c():
    """Одна й та сама одиниця даних має дві долі — вирішує стан termios."""
    W, H = 1040, 500
    g = []

    b, bw, bh = textbox(150, 150, "процес на ведучому кінці\nwrite(m, \"\\x03\", 1)",
                        size=13, fill="#eaf7ee", stroke=FIELD)
    g.append(b)

    g.append(fitbox(320, 118, 220, 66, "лінійна дисципліна\nISIG увімкнено?",
                    size=13, fill="#eef2f7"))
    g.append(arrow(252, 151, 318, 151))

    # гілка «увімкнено»
    g.append(arrow(430, 116, 430, 84))
    g.append(text(444, 100, "так", size=12, color=MUTED, anchor="start"))
    g.append(arrow(540, 78, 618, 78))

    g.append(rect(620, 40, 390, 150, fill="#fdf6f5", stroke=POS, sw=1.4))
    g.append(text(815, 64, "сеанс цього керуючого термінала", size=13, color=POS))
    g.append(fitbox(646, 78, 168, 94, "група\nпереднього плану\nbash · make",
                    size=12, fill="#fdecea", stroke=POS))
    g.append(fitbox(824, 78, 168, 94, "фонова група\nrsync",
                    size=12, fill=FILL))
    g.append(text(815, 214, "SIGINT дістається лише групі переднього плану",
                  size=12, color=POS))

    # гілка «вимкнено»
    g.append(arrow(430, 186, 430, 300))
    g.append(text(444, 250, "ні — сирий режим", size=12, color=MUTED, anchor="start"))
    g.append(arrow(540, 330, 618, 330))
    g.append(fitbox(620, 292, 390, 76,
                    "вхідна черга: 0x03 лежить як звичайні дані\nредактор читає його сам",
                    size=12, fill=FILL))
    g.append(text(815, 400, "той самий байт — і жодного сигналу", size=12, color=MUTED))

    return render(os.path.join(IMG, 'ctrl-c-path.svg'), W, H, *g,
                  title="Дві долі байта 0x03")


def fig_two_terminals():
    """У грі два термінали; обробку має робити рівно один із них."""
    W, H = 1120, 470
    g = []

    g.append(text(560, 34, "натиснуто одну клавішу «l»", size=13, color=MUTED))

    g.append(fitbox(40, 60, 300, 96,
                    "наш термінал і наш процес\n"
                    "сирий режим: ECHO, ICANON, ISIG вимкнено\n"
                    "read(0) → write(ведучий)",
                    size=12, fill="#eaf7ee", stroke=FIELD))
    g.append(arrow(346, 112, 434, 112))

    g.append(fitbox(440, 60, 320, 96,
                    "ядро pty\n"
                    "ECHO повертає байт назад\n"
                    "ICANON тримає рядок до Enter",
                    size=12, fill="#eef2f7"))

    g.append(text(812, 92, "після Enter", size=11, color=MUTED))
    g.append(arrow(766, 116, 854, 116))
    g.append(fitbox(860, 60, 220, 96,
                    "оболонка\nчитає підлеглий кінець",
                    size=12, fill=FILL))

    g.append(arrow(600, 160, 600, 248, color=FIELD, sw=1.6))
    g.append(text(620, 206, "відлуння: той самий байт на ведучому кінці",
                  size=12, color=FIELD, anchor="start"))

    g.append(fitbox(400, 252, 400, 84,
                    "наш процес\nread(ведучий) → write(1)",
                    size=12, fill="#eaf7ee", stroke=FIELD))
    g.append(arrow(394, 294, 306, 294))
    g.append(fitbox(40, 252, 260, 84,
                    "наш екран\n«l» з'являється один раз",
                    size=12, fill=FILL))

    g.append(text(560, 400,
                  "лишили ECHO в себе — на екрані «ll»:",
                  size=13, color=POS))
    g.append(text(560, 422,
                  "символ намалювали б і ми, і ядро pty",
                  size=13, color=POS))

    return render(os.path.join(IMG, 'two-terminals.svg'), W, H, *g,
                  title="Два термінали в одній програмі")


if __name__ == '__main__':
    fig_tty_vs_pty()
    fig_pty_flows()
    fig_ctrl_c()
    fig_two_terminals()
    print("готово:", os.listdir(IMG))
