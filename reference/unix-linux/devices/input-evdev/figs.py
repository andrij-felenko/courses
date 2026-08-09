# -*- coding: utf-8 -*-
"""Фігури до теми «Підсистема вводу й evdev»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_event_frame():
    """Кадр подій: чому межа важливіша за окрему подію."""
    W, H = 1120, 390
    f = []

    f.append(text(40, 40, "Що прочитає read() з /dev/input/eventN",
                  size=13, color=MUTED, anchor="start"))

    rows = [
        ("EV_REL · REL_X · +7", FILL, LINE),
        ("EV_REL · REL_Y · −3", FILL, LINE),
        ("EV_KEY · BTN_LEFT · 1", FILL, LINE),
        ("EV_SYN · SYN_REPORT · 0", "#eaf7ee", FIELD),
    ]
    bx, bw, bh = 40, 430, 44
    for i, (s, fill, stroke) in enumerate(rows):
        f.append(fitbox(bx, 70 + i * 52, bw, bh, s, size=14, fill=fill, stroke=stroke))

    f.append(text(40, 296, "по 24 байти кожна: час, тип, код, значення",
                  size=12, color=MUTED, anchor="start"))

    rx, rw = 620, 460
    f.append(text(rx, 62, "Читач діє на кожній події", size=13, color=MUTED, anchor="start"))
    f.append(fitbox(rx, 76, rw, 96,
                    "курсор смикнувся вправо, потім угору —\n"
                    "діагональ стала сходинкою,\n"
                    "а клік трапився вже в третій точці",
                    size=13, fill="#fdecea", stroke=POS))

    f.append(text(rx, 226, "Читач діє на межі кадру", size=13, color=MUTED, anchor="start"))
    f.append(fitbox(rx, 240, rw, 96,
                    "одне переміщення по діагоналі\n"
                    "і клік рівно там, де курсор опинився",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    f.append(arrow(486, 140, 610, 124))
    f.append(arrow(486, 250, 610, 288))

    render(os.path.join(IMG, 'event-frame.svg'), W, H, *f)


def fig_three_layers():
    """Драйвер — ядро вводу — обробники: потік не ділиться, а дублюється."""
    W, H = 1120, 470
    f = []

    f.append(text(40, 60, "кожен обробник дістає КОЖНУ подію — потік не ділиться, а дублюється",
                  size=13, color=MUTED, anchor="start"))

    cols = [(40, 310), (395, 310), (750, 330)]

    handlers = [
        "evdev\n/dev/input/eventN",
        "клавіатурний обробник\nвіртуальна консоль",
        "joydev\n/dev/input/jsN",
    ]
    for (x, w), s in zip(cols, handlers):
        f.append(fitbox(x, 110, w, 68, s, size=13, fill="#eaf0fd", stroke=NEG))

    f.append(fitbox(40, 250, 1040, 76,
                    "ядро вводу: перевіряє код за бітовими масками пристрою, "
                    "глушить повтор того самого стану, веде автоповтор",
                    size=14, fill=FILL, stroke=LINE))

    devices = [
        "USB-клавіатура\nдрайвер hid-generic",
        "тачпад ноутбука\nдрайвер psmouse",
        "кнопка на GPIO\nдрайвер gpio-keys",
    ]
    for (x, w), s in zip(cols, devices):
        f.append(fitbox(x, 380, w, 60, s, size=13, fill="#eaf7ee", stroke=FIELD))

    for x, w in cols:
        cx = x + w / 2
        f.append(arrow(cx, 378, cx, 330))
        f.append(arrow(cx, 248, cx, 182))

    render(os.path.join(IMG, 'three-layers.svg'), W, H, *f)


def fig_syn_dropped():
    """Переповнення черги: чому ядро викидає все, а не найстаріше."""
    W, H = 1120, 440
    f = []

    f.append(text(40, 44, "Черга подій — своя на КОЖНЕ відкриття файлу",
                  size=13, color=MUTED, anchor="start"))

    cw = 120
    for i in range(6):
        f.append(fitbox(40 + i * cw, 64, cw - 6, 52, "подія",
                        size=13, fill=FILL, stroke=LINE))
    f.append(mtext(790, 82, "буфер повний:\nчитач не встиг", size=13,
                   color=MUTED, anchor="start"))

    f.append(text(40, 172, "Що робити з подією, яка вже не влазить?",
                  size=14, color=INK, anchor="start", bold=True))

    f.append(fitbox(40, 196, 500, 110,
                    "Викинути найстаріші\n"
                    "зникне «відпускання клавіші»,\n"
                    "і клавіша лишиться натиснутою назавжди",
                    size=13, fill="#fdecea", stroke=POS))

    f.append(fitbox(580, 196, 500, 110,
                    "Викинути ВСЕ й покласти SYN_DROPPED\n"
                    "читач дізнається, що його картина світу\n"
                    "недійсна, і перепитує стан заново",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    f.append(fitbox(40, 340, 1040, 56,
                    "після SYN_DROPPED: пропустити все до наступного SYN_REPORT, "
                    "потім EVIOCGKEY та EVIOCGABS — і почати з реального стану",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'syn-dropped.svg'), W, H, *f)


def fig_bitmask():
    """Як розбирати відповідь EVIOCGBIT: біт = код, слово рідного розміру."""
    W, H = 1120, 420
    f = []

    f.append(text(40, 40,
                  "ioctl(fd, EVIOCGBIT(EV_KEY, sizeof bits), bits)  →  "
                  "повертає кількість записаних БАЙТІВ",
                  size=13, color=MUTED, anchor="start"))

    bw, gap = 160, 12
    labels = ["bits[0]\nкоди 0…63", "bits[1]\n64…127", "bits[2]\n128…191",
              "bits[3]\n192…255", "bits[4]\n256…319", "bits[5]\n320…383"]
    for i, s in enumerate(labels):
        f.append(fitbox(40 + i * (bw + gap), 70, bw, 64, s,
                        size=13, fill=FILL, stroke=LINE))

    f.append(fitbox(40, 210, 460, 92,
                    "KEY_A = 30\n"
                    "слово bits[0], біт 30",
                    size=13, fill="#eaf7ee", stroke=FIELD))
    f.append(fitbox(580, 210, 500, 92,
                    "BTN_LEFT = 0x110 = 272\n"
                    "272 / 64 = 4 → слово bits[4], біт 272 % 64 = 16",
                    size=13, fill="#eaf0fd", stroke=NEG))

    f.append(arrow(270, 206, 120, 142))
    f.append(arrow(830, 206, 808, 142))

    f.append(fitbox(40, 330, 1040, 60,
                    "один біт — один код; слово рідного розміру: "
                    "64 біти на LP64, 32 на 32-бітній програмі",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'evdev-bitmask.svg'), W, H, *f)


def fig_uinput_race():
    """Вікно між UI_DEV_CREATE і першим читачем: куди діваються перші події."""
    W, H = 1160, 470
    f = []

    f.append(text(40, 40, "Що встигає статися між народженням пристрою і першим читачем",
                  size=13, color=MUTED, anchor="start"))

    f.append(fitbox(120, 64, 880, 62,
                    "усе, що програма пише в цьому вікні, зникає безслідно:\n"
                    "черг читачів ще не існує, а ядро нічого не притримує",
                    size=14, fill="#fdecea", stroke=POS))

    ax_y = 206
    f.append(arrow(60, ax_y, 1100, ax_y))

    marks = [
        (120, "UI_DEV_CREATE\nповернувся"),
        (340, "devtmpfs створив\n/dev/input/eventN,\nвласник — root"),
        (565, "udev наклав правила:\nгрупа, список доступу,\nID_INPUT_KEYBOARD"),
        (790, "композитор побачив\nпристрій у розсилці\nвід udev"),
        (1000, "open(), запит\nможливостей —\nаж тепер читає"),
    ]
    for x, s in marks:
        f.append(line(x, ax_y - 13, x, ax_y + 13))
        f.append(fitbox(x - 105, ax_y + 24, 210, 100, s, size=12,
                        fill=FILL, stroke=LINE))

    f.append(fitbox(60, 366, 1040, 62,
                    "надійний порядок: створити пристрій → дочекатися вузла → "
                    "витримати паузу\nі лише тоді забирати справжню клавіатуру собі",
                    size=14, fill="#eaf7ee", stroke=FIELD))

    render(os.path.join(IMG, 'uinput-race-window.svg'), W, H, *f)


if __name__ == '__main__':
    fig_event_frame()
    fig_three_layers()
    fig_syn_dropped()
    fig_bitmask()
    fig_uinput_race()
    print('ok')
