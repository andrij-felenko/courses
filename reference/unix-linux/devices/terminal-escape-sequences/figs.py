# -*- coding: utf-8 -*-
"""Фігури до теми «Керуючі послідовності термінала»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_csi_anatomy():
    """Чому приймач знаходить кінець команди, не знаючи самої команди."""
    W, H = 1000, 480
    g = []

    chars = ["ESC", "[", "1", ";", "3", "1", "m"]
    hexes = ["1B", "5B", "31", "3B", "33", "31", "6D"]
    x0, cw, ch, cy = 120, 96, 64, 156

    groups = [
        (0, 2, "початок команди\n0x1B 0x5B", "#eaf7ee", FIELD),
        (2, 6, "байти параметрів\n0x30 – 0x3F", FILL, LINE),
        (6, 7, "кінцевий байт\n0x40 – 0x7E", "#fdecea", POS),
    ]
    for i, j, label, fill, stroke in groups:
        gx = x0 + i * cw + 4
        gw = (j - i) * cw - 8
        g.append(fitbox(gx, 76, gw, 54, label, size=13, fill=fill, stroke=stroke))

    for k, (c, hx) in enumerate(zip(chars, hexes)):
        x = x0 + k * cw
        fill = "#eaf7ee" if k < 2 else ("#fdecea" if k == 6 else FILL)
        g.append(fitbox(x + 4, cy, cw - 8, ch, c, size=18, bold=True, fill=fill))
        g.append(text(x + cw / 2, cy + ch + 26, hx, size=13, color=MUTED))

    notes = [
        (30, "0x1B перемикає приймач із «друкую» на «слухаю команду»,\n"
             "а «[» каже, що в команді будуть числа"),
        (350, "цифри й «;» — аргументи;\n"
              "пропущений аргумент означає\nстандартне значення"),
        (670, "перший байт із верхнього діапазону\n"
              "і завершує послідовність,\nі називає команду"),
    ]
    for nx, s in notes:
        g.append(fitbox(nx, 300, 300, 102, s, size=12.5, fill="#f8fafc", stroke=MUTED))

    g.append(text(W / 2, 442,
                  "команда «m» з аргументами 1 і 31 — жирний червоний текст",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, 'csi-anatomy.svg'), W, H, *g,
                  title="Будова керуючої послідовності")


def fig_one_stream():
    """Команди йдуть тим самим потоком, що й текст, а відповіді — тим самим, що й клавіші."""
    W, H = 1120, 500
    g = []

    g.append(text(W / 2, 76,
                  "уперед: літери й команди — один потік байтів",
                  size=13, color=MUTED))
    g.append(fitbox(40, 96, 250, 96,
                    "програма\nwrite(1, …)", size=13, fill="#eaf7ee", stroke=FIELD))
    g.append(fitbox(360, 96, 340, 96,
                    "ядро: лінійна дисципліна\nдописує \\r перед \\n,\n"
                    "послідовностей не розбирає", size=13, fill="#eef2f7"))
    g.append(fitbox(770, 96, 310, 96,
                    "емулятор термінала\nрозбирає команди й малює", size=13, fill=FILL))
    g.append(arrow(292, 144, 356, 144))
    g.append(arrow(702, 144, 766, 144))

    g.append(fitbox(360, 232, 340, 44,
                    "курсор, кольори, розмір екрана — стан живе тут",
                    size=12, fill="#fff8e6", stroke=MUTED))
    g.append(arrow(925, 200, 800, 230, color=MUTED, sw=1.4))

    g.append(text(W / 2, 316,
                  "назад: натиснуті клавіші й відповіді термінала — теж один потік",
                  size=13, color=MUTED))
    g.append(fitbox(40, 336, 250, 96,
                    "програма\nread(0, …)", size=13, fill="#eaf7ee", stroke=FIELD))
    g.append(fitbox(360, 336, 340, 96,
                    "ядро: ICANON, ISIG, ECHO\nтеж лише байти", size=13, fill="#eef2f7"))
    g.append(fitbox(770, 336, 310, 96,
                    "емулятор термінала\nклавіші · відповіді на запити",
                    size=13, fill=FILL))
    g.append(arrow(766, 384, 702, 384))
    g.append(arrow(356, 384, 292, 384))

    g.append(text(W / 2, 470,
                  "відповідь на запит приходить упереміш із тим, що набрала людина",
                  size=13, color=POS))

    return render(os.path.join(IMG, 'one-stream.svg'), W, H, *g,
                  title="Один потік на текст, команди й відповіді")


def fig_esc_ambiguity():
    """Ті самі три байти — два різні наміри; розрізняє тільки пауза."""
    W, H = 1000, 430
    g = []

    g.append(text(W / 2, 46, "той самий потік байтів — два різні наміри",
                  size=14, color=INK, bold=True))

    chars = ["ESC", "[", "A"]
    hexes = ["0x1B", "0x5B", "0x41"]
    x0, cw, ch, cy = 335, 110, 60, 72
    for k, (c, hx) in enumerate(zip(chars, hexes)):
        x = x0 + k * cw
        g.append(fitbox(x + 5, cy, cw - 10, ch, c, size=17, bold=True, fill=FILL))
        g.append(text(x + cw / 2, cy + ch + 24, hx, size=12, color=MUTED))

    g.append(arrow(470, 178, 250, 236, color=MUTED, sw=1.6))
    g.append(arrow(530, 178, 750, 236, color=MUTED, sw=1.6))

    g.append(fitbox(60, 240, 380, 96,
                    "одне натиснення: стрілка вгору\nтри байти приходять упритул",
                    size=13, fill="#eaf7ee", stroke=FIELD))
    g.append(fitbox(560, 240, 380, 96,
                    "три натиснення: Esc, «[», «A»\nміж байтами — людська пауза",
                    size=13, fill="#fdecea", stroke=POS))

    g.append(text(W / 2, 384,
                  "розрізнити можна лише за часом — звідси затримка після Esc",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, 'esc-ambiguity.svg'), W, H, *g,
                  title="Чому Esc не спрацьовує миттєво")


def fig_input_fsm():
    """Машина станів розбирача: переходи задано діапазонами байтів і паузою."""
    W, H = 1080, 420
    g = []

    states = [
        (60, 230, "GROUND\nбайт < 0x80 — символ\n0xC0 і вище — початок UTF-8", "#eaf7ee", FIELD),
        (420, 200, "ESC\nбачили 0x1B\n«[» → CSI, «O» → SS3", FILL, LINE),
        (750, 270, "CSI_PARAM\n0x30–0x3F — аргументи\n0x40–0x7E — кінець", "#fff8e6", MUTED),
    ]
    for x, w, label, fill, stroke in states:
        g.append(fitbox(x, 150, w, 110, label, size=13, fill=fill, stroke=stroke))

    g.append(arrow(296, 205, 414, 205))
    g.append(text(355, 176, "0x1B", size=13, color=MUTED))
    g.append(arrow(626, 205, 744, 205))
    g.append(text(685, 176, "«[»", size=13, color=MUTED))

    # пауза скидає обидва стани назад у GROUND
    g.append(line(520, 150, 520, 90, color=POS, sw=1.4, dash="6 5"))
    g.append(line(885, 150, 885, 90, color=POS, sw=1.4, dash="6 5"))
    g.append(line(175, 90, 885, 90, color=POS, sw=1.4, dash="6 5"))
    g.append(arrow(175, 90, 175, 148, color=POS, sw=1.4))
    g.append(fitbox(300, 26, 480, 46,
                    "тиша ESC_WAIT_MS — послідовності не було",
                    size=13, fill="#fdecea", stroke=POS))

    # кінцевий байт завершує послідовність
    g.append(line(885, 260, 885, 340))
    g.append(line(885, 340, 175, 340))
    g.append(arrow(175, 340, 175, 262))
    g.append(text(530, 366, "кінцевий байт 0x40–0x7E: подія готова, стан скинуто",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, 'input-fsm.svg'), W, H, *g,
                  title="Машина станів вхідного розбирача")


if __name__ == '__main__':
    fig_csi_anatomy()
    fig_one_stream()
    fig_esc_ambiguity()
    fig_input_fsm()
    print("готово:", os.listdir(IMG))
