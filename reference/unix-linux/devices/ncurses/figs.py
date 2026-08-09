# -*- coding: utf-8 -*-
"""Фігури до теми «ncurses: бібліотека повноекранних програм у терміналі»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_layers():
    """Хто що знає між програмою і склом термінала."""
    W, H = 1120, 660
    g = []

    g.append(text(W / 2, 44, "від наміру програми до точок на склі: що знає кожен шар",
                  size=15, bold=True))

    bx, bw = 70, 430          # колонка шарів
    ax, aw = 610, 440         # колонка «чого шар не знає»
    bh = 82
    ys = [88, 200, 312, 424, 536]

    layers = [
        ("програма\nмалює у вікна в пам'яті", FILL),
        ("ncurses\nдві копії екрана, вибір найдешевших дій", "#eaf7ee"),
        ("terminfo\nназва можливості → байти цього термінала", "#eaf7ee"),
        ("tty / termios у ядрі\nрежим, відлуння, розмір вікна", FILL),
        ("термінал\nтлумачить байти й малює", FILL),
    ]
    notes = [
        "не знає ні байтів,\nні моделі термінала",
        "не бачить скла:\nвірить власній копії",
        "не перевіряє,\nчи ім'я TERM правдиве",
        "у вміст не дивиться:\nпереганяє байти далі",
        "не має зворотного каналу:\nнамальоване не читається",
    ]
    edges = ["малює комірки", "яка команда тут потрібна", "готові байти", "той самий потік"]

    for y, (t, fill), note in zip(ys, layers, notes):
        g.append(fitbox(bx, y, bw, bh, t, size=14, fill=fill, stroke=LINE))
        g.append(fitbox(ax, y, aw, bh, note, size=13, fill="#fff8e6", stroke=MUTED, sw=1,
                        color=MUTED))

    for k, lab in enumerate(edges):
        y0 = ys[k] + bh
        g.append(arrow(bx + 110, y0, bx + 110, y0 + 30, color=LINE, sw=1.8))
        g.append(text(bx + 130, y0 + 22, lab, size=12.5, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, 'layers.svg'), W, H, *g,
                  title="Шари між програмою й екраном термінала")


def fig_two_screens():
    """Дві копії екрана, дві відмінні комірки, вісім байтів у дріт."""
    W, H = 1120, 560
    g = []

    g.append(text(W / 2, 42, "оновлення екрана: порівнюють пам'ять із пам'яттю",
                  size=15, bold=True))

    rows_old = ["CPU   12% ", "MEM  3.4G ", "          ", "1 bash    ", "2 vim     "]
    rows_new = ["CPU   47% ", "MEM  3.4G ", "          ", "1 bash    ", "2 vim     "]
    diff = {(0, 6), (0, 7)}

    cw, ch = 34, 30
    grids = [
        (110, rows_old, "curscr — що, за нашими даними, на склі"),
        (670, rows_new, "newscr — що програма намалювала в пам'яті"),
    ]
    gy = 150
    for gx, rows, head in grids:
        g.append(fitbox(gx, 84, cw * 10, 46, head, size=12.5, bold=True,
                        fill="#eef2f7", stroke=MUTED, sw=1))
        for r, line_s in enumerate(rows):
            for c, symb in enumerate(line_s):
                hot = (r, c) in diff
                x, y = gx + c * cw, gy + r * ch
                g.append(rect(x, y, cw, ch,
                              fill="#fdecea" if hot else "#ffffff",
                              stroke=POS if hot else MUTED,
                              sw=2 if hot else 1, rx=2))
                if symb != " ":
                    g.append(text(x + cw / 2, y + ch * 0.68, symb, size=14,
                                  color=POS if hot else INK, bold=hot))

    g.append(text(W / 2, gy + 5 * ch + 34,
                  "відмінні дві комірки з п'ятдесяти — решту порівняння відкидає",
                  size=13, color=MUTED))

    g.append(arrow(W / 2, gy + 5 * ch + 52, W / 2, gy + 5 * ch + 84, color=LINE, sw=1.8))

    g.append(fitbox(160, gy + 5 * ch + 88, 800, 52,
                    "doupdate надсилає:   ESC [ 1 ; 7 H   4 7        —  8 байтів",
                    size=14, bold=True, fill="#eaf7ee", stroke=FIELD))
    g.append(fitbox(160, gy + 5 * ch + 150, 800, 46,
                    "повне перемальовування екрана 80×24 коштувало б 1920 байтів",
                    size=13, fill="#fff8e6", stroke=MUTED, sw=1))

    return render(os.path.join(IMG, 'two-screens.svg'), W, H, *g,
                  title="Дві копії екрана й мінімальне оновлення")


def fig_input_decode():
    """Три байти стають однією клавішею; самотній ESC розрізняє тільки час."""
    W, H = 1140, 620
    g = []

    g.append(text(W / 2, 42, "зворотний бік: потік байтів треба зібрати назад у клавішу",
                  size=15, bold=True))

    # ── смуга А: послідовність прийшла цілком ────────────────────────────
    g.append(fitbox(60, 78, 380, 40, "послідовність прийшла цілком", size=13, bold=True,
                    fill="#eef2f7", stroke=MUTED, sw=1))

    g.append(fitbox(60, 168, 250, 64, "з дроту:\n1B  5B  41", size=14,
                    fill=FILL, stroke=LINE))
    g.append(arrow(310, 200, 372, 200))

    g.append(fitbox(372, 172, 118, 56, "ESC", size=14, bold=True,
                    fill="#eaf7ee", stroke=FIELD))

    g.append(arrow(490, 190, 596, 140))
    g.append(text(536, 152, "[", size=14, bold=True))
    g.append(arrow(490, 214, 596, 288))
    g.append(text(536, 268, "O", size=14, bold=True))

    g.append(fitbox(596, 112, 118, 54, "ESC [", size=13, bold=True,
                    fill="#eaf7ee", stroke=FIELD))
    g.append(fitbox(596, 262, 118, 54, "ESC O", size=13, bold=True,
                    fill="#eaf7ee", stroke=FIELD))

    g.append(arrow(714, 128, 812, 106))
    g.append(text(762, 100, "A", size=13, bold=True))
    g.append(arrow(714, 150, 812, 178))
    g.append(text(762, 178, "B", size=13, bold=True))
    g.append(arrow(714, 289, 812, 289))
    g.append(text(762, 280, "P", size=13, bold=True))

    g.append(fitbox(830, 88, 250, 44, "KEY_UP   (0403)", size=13, bold=True,
                    fill=FILL, stroke=LINE))
    g.append(fitbox(830, 160, 250, 44, "KEY_DOWN (0402)", size=13, bold=True,
                    fill=FILL, stroke=LINE))
    g.append(fitbox(830, 266, 250, 44, "KEY_F(1) (0411)", size=13, bold=True,
                    fill=FILL, stroke=LINE))

    g.append(fitbox(60, 268, 250, 66,
                    "гілки дерева взяті\nз можливостей terminfo\nцього самого TERM",
                    size=12, color=MUTED, fill="#fff8e6", stroke=MUTED, sw=1))

    g.append(line(60, 372, W - 60, 372, color=MUTED, sw=1, dash="6 5"))

    # ── смуга Б: самотній ESC ────────────────────────────────────────────
    g.append(fitbox(60, 396, 380, 40, "прийшов самотній ESC", size=13, bold=True,
                    fill="#eef2f7", stroke=MUTED, sw=1))

    g.append(fitbox(60, 466, 230, 62, "з дроту:\n1B  і тиша", size=13,
                    fill=FILL, stroke=LINE))
    g.append(arrow(290, 497, 352, 497))
    g.append(fitbox(352, 462, 300, 70,
                    "чекати ESCDELAY\n(типово 1000 мс)", size=13,
                    fill="#fdecea", stroke=POS))
    g.append(arrow(652, 497, 714, 497))
    g.append(fitbox(714, 466, 366, 62, "віддати ESC (27) як клавішу", size=13,
                    fill=FILL, stroke=LINE))

    g.append(text(60, 566,
                  "ESC — водночас клавіша й початок кожної послідовності: "
                  "за вмістом потоку це не розрізнити, тільки за часом",
                  size=12.5, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, 'input-decode.svg'), W, H, *g,
                  title="Розбір вхідного потоку в коди клавіш")


def fig_chtype_bits():
    """Розкладка бітів у chtype: знак, пара, ознаки."""
    W, H = 1160, 520
    g = []

    g.append(text(W / 2, 40, "один chtype: знак, номер пари й ознаки в одному цілому",
                  size=15, bold=True))
    g.append(text(W / 2, 66, "старший біт ліворуч, як у curses.h", size=12, color=MUTED))

    x0, cw, sy, sh = 68, 32, 88, 42
    for i in range(32):
        b = 31 - i
        if b >= 16:
            fill = "#eef2f7"
        elif b >= 8:
            fill = "#eaf7ee"
        else:
            fill = "#fff8e6"
        x = x0 + i * cw
        g.append(rect(x, sy, cw, sh, fill=fill, stroke=MUTED, sw=1, rx=2))
        g.append(text(x + cw / 2, sy + 27, str(b), size=10, color=INK))

    groups = [
        (x0, 16 * cw, "біти 31…16 — ознаки накреслення\nмаска A_ATTRIBUTES"),
        (x0 + 16 * cw, 8 * cw, "біти 15…8 — номер пари\nмаска A_COLOR"),
        (x0 + 24 * cw, 8 * cw, "біти 7…0 — код знака\nмаска A_CHARTEXT"),
    ]
    for gx, gw, label in groups:
        g.append(fitbox(gx, 150, gw, 62, label, size=13, fill=FILL, stroke=LINE))

    g.append(fitbox(x0, 228, 32 * cw, 44,
                    "COLOR_PAIR(n) зсуває n на вісім бітів: у chtype влазять пари 1…255 "
                    "і рівно один байт знака",
                    size=13, fill="#fdecea", stroke=POS))

    g.append(text(x0, 302, "шістнадцять ознак — по одному біту, у тому самому порядку:",
                  size=13, bold=True, anchor="start"))

    names = ["A_ITALIC", "A_VERTICAL", "A_TOP", "A_RIGHT",
             "A_LOW", "A_LEFT", "A_HORIZONTAL", "A_PROTECT",
             "A_INVIS", "A_ALTCHARSET", "A_BOLD", "A_DIM",
             "A_BLINK", "A_REVERSE", "A_UNDERLINE", "A_STANDOUT"]
    for k, nm in enumerate(names):
        col, row = k % 4, k // 4
        bx = x0 + col * 258
        by = 316 + row * 42
        g.append(fitbox(bx, by, 250, 34, "%d  ·  %s" % (31 - k, nm),
                        size=13, fill="#eef2f7", stroke=MUTED, sw=1))

    g.append(mtext(x0, 498,
                   ["A_HORIZONTAL, A_LEFT, A_LOW, A_RIGHT, A_TOP і A_VERTICAL описані в X/Open,",
                    "але майже жоден термінал їх не показує; A_ITALIC — розширення ncurses."],
                   size=12, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, 'chtype-bits.svg'), W, H, *g,
                  title="Розкладка бітів у chtype")


def fig_gap_vs_jump():
    """Розрив в один знак дешевше передрукувати, ніж перестрибнути."""
    W, H = 1120, 600
    g = []

    g.append(text(W / 2, 40, "той самий рядок стану, два способи — і різні числа в байтах",
                  size=15, bold=True))

    old = " 12:04:59"
    new = " 12:05:00"
    changed = {5, 7, 8}
    cw, ch = 46, 40
    x0, ytop = 300, 108

    for i in range(len(old)):
        g.append(text(x0 + i * cw + cw / 2, ytop - 14, str(i), size=11, color=MUTED))

    for y, s, name, mark in ((ytop, old, "було на склі", False),
                             (ytop + ch + 18, new, "треба показати", True)):
        g.append(text(x0 - 24, y + ch * 0.66, name, size=13, color=MUTED, anchor="end"))
        for i, symb in enumerate(s):
            hot = mark and i in changed
            g.append(rect(x0 + i * cw, y, cw, ch,
                          fill="#fdecea" if hot else "#ffffff",
                          stroke=POS if hot else MUTED, sw=2 if hot else 1, rx=2))
            if symb != " ":
                g.append(text(x0 + i * cw + cw / 2, y + ch * 0.68, symb, size=15,
                              color=POS if hot else INK, bold=hot))

    gapx = x0 + 6 * cw + cw / 2
    g.append(arrow(gapx, ytop + 2 * ch + 46, gapx, ytop + 2 * ch + 20, color=MUTED, sw=1.5))
    g.append(text(gapx, ytop + 2 * ch + 66, "розрив: один незмінний знак",
                  size=12.5, color=MUTED))

    by = ytop + 2 * ch + 92
    g.append(fitbox(60, by, 480, 128,
                    "стрибок на кожну групу\n"
                    "ESC [ 2 4 ; 6 H   ESC [ 0 ; 3 4 m   5\n"
                    "ESC [ 2 4 ; 8 H   0   0\n"
                    "разом 24 байти",
                    size=13, fill=FILL, stroke=LINE))
    g.append(fitbox(580, by, 480, 128,
                    "пройти розрив наскрізь\n"
                    "ESC [ 2 4 ; 6 H   ESC [ 0 ; 3 4 m   5\n"
                    ":   0   0\n"
                    "разом 18 байтів",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    g.append(fitbox(60, by + 148, 1000, 54,
                    "порівнюємо однорідне: довжина розриву проти довжини "
                    "команди позиціювання — 1 проти 7",
                    size=13, fill="#fff8e6", stroke=MUTED, sw=1, color=MUTED))

    return render(os.path.join(IMG, 'gap-vs-jump.svg'), W, H, *g,
                  title="Розрив між змінами проти вартості позиціювання")


if __name__ == '__main__':
    fig_layers()
    fig_two_screens()
    fig_input_decode()
    fig_chtype_bits()
    fig_gap_vs_jump()
    print("готово:", os.listdir(IMG))
