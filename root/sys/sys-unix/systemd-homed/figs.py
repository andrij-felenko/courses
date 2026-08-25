# -*- coding: utf-8 -*-
"""Фігури до теми «systemd-homed: домівка як переносний підписаний образ»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_image_layers():
    """Шари образу домівки й межа, яку проводить пароль."""
    W, H = 1340, 700
    f = []

    # вкладені прямокутники: кожен наступний вужчий і нижчий
    layers = [
        (70,  100, 780, 520, "#ffffff", MUTED,  "файл  /home/andrij.home", 16),
        (110, 168, 700, 432, "#f4f6f8", LINE,   "loop-пристрій:  файл поданий ядру як диск", 15),
        (150, 236, 620, 344, "#eef3fd", NEG,    "таблиця GPT:  рівно один розділ", 15),
        (190, 304, 540, 256, "#fdf4e8", POS,    "том LUKS2:  заголовок і зашифровані сектори", 15),
        (230, 372, 460, 168, "#eafaf0", FIELD,  "файлова система:  ext4 / Btrfs / XFS", 15),
    ]
    for x, y, w, h, fill, edge, label, fs in layers:
        f.append(rect(x, y, w, h, fill=fill, stroke=edge, sw=1.8))
        f.append(text(x + w / 2, y + 30, label, size=fs, bold=True, color=INK))

    f.append(fitbox(270, 440, 380, 62, "тека andrij  →  стане /home/andrij",
                    size=15, fill="#ffffff", stroke=FIELD))

    # підписи до GPT-розділу
    f.append(text(895, 300, "тип розділу", size=14, color=MUTED, anchor="start"))
    f.append(text(895, 326, "773f91ef-66d4-49b5-bd83-d683bf40ad16",
                  size=13, color=NEG, anchor="start", bold=True))
    f.append(text(895, 366, "мітка розділу", size=14, color=MUTED, anchor="start"))
    f.append(text(895, 392, "andrij  —  ім'я користувача", size=14, color=NEG,
                  anchor="start", bold=True))
    f.append(line(772, 340, 885, 340, color=NEG, sw=1.2, dash="4 4"))

    # межа пароля
    f.append(line(70, 660, 1270, 660, color=POS, sw=2, dash="8 6"))
    f.append(text(70, 646, "без пароля читаються:  файл, GPT, тип і мітка розділу, заголовок LUKS2",
                  size=15, color=NEG, anchor="start", bold=True))
    f.append(text(70, 690, "потребує ключа тому:  сектори LUKS2, файлова система і весь її вміст",
                  size=15, color=POS, anchor="start", bold=True))

    return render(os.path.join(OUT, 'image-layers.svg'), W, H,
                  *f, title="Домівка як образ: файл, у якому лежить диск")


def fig_three_copies():
    """Три копії запису й мить, коли кожна доступна."""
    W, H = 1420, 620
    f = []

    cols = [
        (110, "на машині", "/var/lib/systemd/home/",
         "домівка ще ЗАМКНЕНА", "назвати користувача,\nпоказати його у списку входу", "#eef3fd", NEG),
        (530, "у заголовку LUKS2", "маркер типу systemd-homed",
         "ключ тому вже здобуто", "прочитати запис\nдо будь-якого монтування", "#fdf4e8", POS),
        (950, "у файловій системі", "~/.identity",
         "домівка ЗМОНТОВАНА", "копія, що їде разом\nіз вмістом домівки", "#eafaf0", FIELD),
    ]

    for x, name, where, when, why, fill, edge in cols:
        f.append(fitbox(x, 96, 360, 56, name, size=17, bold=True, fill=fill, stroke=edge))
        f.append(fitbox(x, 164, 360, 52, where, size=14, fill="#ffffff", stroke=edge))
        f.append(text(x + 180, 258, when, size=14, color=edge, bold=True))
        b, _, _ = textbox(x + 180, 352, why, size=14, fill="#ffffff", min_w=360)
        f.append(b)

    # спільне поле версії
    f.append(arrow(290, 420, 590, 468, color=MUTED, sw=1.4))
    f.append(arrow(710, 420, 710, 468, color=MUTED, sw=1.4))
    f.append(arrow(1130, 420, 830, 468, color=MUTED, sw=1.4))

    b, _, _ = textbox(710, 508, ["lastChangeUSec  —  мить останньої зміни",
                                 "при розбіжності перемагає найновіша копія"],
                      size=15, fill="#f4f6f8", stroke=LINE, min_w=700)
    f.append(b)

    return render(os.path.join(OUT, 'three-copies.svg'), W, H,
                  *f, title="Той самий запис у трьох місцях — кожне доступне у свою мить")


def fig_home_lifecycle():
    """Життя домівки від входу до розмонтування, зі сном посередині."""
    W, H = 1460, 640
    AXIS = 330
    BW, BH = 260, 74
    f = []

    f.append(line(70, AXIS, 1390, AXIS, color=MUTED, sw=2))

    # ключ тому існує лише в цих проміжках — дві смуги над віссю
    f.append(rect(300, AXIS - 22, 340, 44, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=8))
    f.append(rect(940, AXIS - 22, 310, 44, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=8))
    f.append(rect(640, AXIS - 22, 300, 44, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    f.append(text(470, AXIS + 6, "ключ тому в пам'яті", size=14, color=FIELD, bold=True))
    f.append(text(790, AXIS + 6, "ключа немає", size=14, color=POS, bold=True))
    f.append(text(1095, AXIS + 6, "ключ тому в пам'яті", size=14, color=FIELD, bold=True))

    above = [
        (170, "завантаження", "нічого не відмикається:\nмашина не має ключа", "#f4f6f8", MUTED),
        (640, "засинання", "suspend=  викидає ключ\nіз пам'яті ядра", "#fdecea", POS),
        (1250, "останній сеанс зник", "розмонтування,\nключ зникає", "#eef3fd", NEG),
    ]
    for x, when, what, fill, edge in above:
        f.append(line(x, AXIS - 24, x, 214 + BH / 2, color=edge, sw=1.2, dash="4 4"))
        f.append(circle(x, AXIS, 6, fill=edge, stroke=edge))
        f.append(fitbox(x - BW / 2, 214 - BH / 2, BW, BH, [when, what.split("\n")[0], what.split("\n")[1]],
                        size=13, fill=fill, stroke=edge, color=INK))

    below = [
        (300, "вхід:  фаза auth", "пароль → ключ тому →\nчужий власник? рекурсивний chown", "#eafaf0", FIELD),
        (940, "пробудження", "повторна автентифікація,\nдомівка відмикається наново", "#eafaf0", FIELD),
    ]
    for x, when, what, fill, edge in below:
        f.append(line(x, AXIS + 24, x, 470 - BH / 2, color=edge, sw=1.2, dash="4 4"))
        f.append(circle(x, AXIS, 6, fill=edge, stroke=edge))
        f.append(fitbox(x - BW / 2 - 30, 470 - BH / 2, BW + 60, BH,
                        [when, what.split("\n")[0], what.split("\n")[1]],
                        size=13, fill=fill, stroke=edge, color=INK))

    f.append(text(730, 588, "автентифікація і відмикання — одна дія, а не дві",
                  size=15, color=MUTED))

    return render(os.path.join(OUT, 'home-lifecycle.svg'), W, H,
                  *f, title="Домівка існує в дереві рівно доти, доки людина в системі")


if __name__ == '__main__':
    print(fig_image_layers())
    print(fig_three_copies())
    print(fig_home_lifecycle())
