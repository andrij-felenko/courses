# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"


# ── 1. Як пара чисел лежить у слові ──────────────────────────────────────────
def fig_number_split():
    W, H = 1080, 500
    p = []

    X0, BARW = 90, 900

    # ── рядок А: ядро, 32 біти, 12 + 20 ──
    p.append(text(X0, 68, "усередині ядра: одне 32-бітне слово, 12 + 20",
                  size=15, bold=True, anchor="start"))
    ay, ah = 84, 58
    split = X0 + BARW * 12.0 / 32.0
    p.append(rect(X0, ay, split - X0, ah, fill=BLUE_FILL, stroke=NEG, sw=2, rx=8))
    p.append(text((X0 + split) / 2, ay + ah / 2 + 5, "старший — 12 бітів",
                  size=14, bold=True, color=NEG))
    p.append(rect(split, ay, X0 + BARW - split, ah, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=8))
    p.append(text((split + X0 + BARW) / 2, ay + ah / 2 + 5, "молодший — 20 бітів",
                  size=14, bold=True, color=FIELD))

    by = ay + ah + 22
    p.append(text(X0, by, "біт 31", size=12, color=MUTED, anchor="start"))
    p.append(text(split - 16, by, "біт 20", size=12, color=MUTED, anchor="end"))
    p.append(text(split + 16, by, "біт 19", size=12, color=MUTED, anchor="start"))
    p.append(text(X0 + BARW, by, "біт 0", size=12, color=MUTED, anchor="end"))

    p.append(text(X0 + BARW / 2, by + 32,
                  "MKDEV(ma, mi) = (ma << 20) | mi     MAJOR(dev) = dev >> 20     "
                  "MINOR(dev) = dev & 0xFFFFF",
                  size=13.5, color=INK))

    # ── рядок Б: класичні 8 + 8 ──
    cy = 250
    p.append(text(X0, cy, "класичний Unix і Linux до 2.6: 16 бітів порівну",
                  size=15, bold=True, anchor="start"))
    dy, dh, dw = cy + 16, 46, 430
    p.append(rect(X0, dy, dw / 2, dh, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=8))
    p.append(text(X0 + dw / 4, dy + dh / 2 + 5, "старший — 8", size=13, color=NEG))
    p.append(rect(X0 + dw / 2, dy, dw / 2, dh, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(X0 + dw * 3 / 4, dy + dh / 2 + 5, "молодший — 8", size=13, color=FIELD))
    p.append(mtext(X0 + dw + 60, dy + 18,
                   ["256 драйверів і по 256 примірників на кожен —",
                    "цей простір вичерпали ще у 1990-х"],
                   size=13, color=MUTED, anchor="start"))

    # ── рядок В: перетасоване 64-бітне слово glibc ──
    ey = 390
    p.append(text(X0, ey, "те саме число у програмі (glibc, 64 біти): частини переставлені",
                  size=15, bold=True, anchor="start"))
    fy, fh = ey + 16, 44
    pattern = ['M'] * 5 + ['m'] * 6 + ['M'] * 3 + ['m'] * 2   # від старшої тетради
    nw = BARW / 16.0
    for i, kind in enumerate(pattern):
        x = X0 + i * nw
        is_major = (kind == 'M')
        p.append(rect(x, fy, nw, fh,
                      fill=BLUE_FILL if is_major else GREEN_FILL,
                      stroke=NEG if is_major else FIELD, sw=1.4, rx=4))
        p.append(text(x + nw / 2, fy + fh / 2 + 5, kind, size=13, bold=True,
                      color=NEG if is_major else FIELD))

    p.append(text(X0 + BARW / 2, fy + fh + 32,
                  "тому зсуви руками дають сміття: числа дістають лише major() і minor()",
                  size=13.5, color=POS))

    render(os.path.join(IMG, 'number-split.svg'), W, H, *p)


# ── 2. Шлях open: старший веде до коду, молодший іде наскрізь ────────────────
def fig_open_dispatch():
    W, H = 1260, 470
    p = []

    cap_y, box_y, box_h = 96, 118, 132
    mid = box_y + box_h / 2

    # 1. виклик
    p.append(text(130, cap_y, "виклик", size=12.5, color=MUTED))
    p.append(fitbox(30, box_y + 30, 200, 72, ['open("/dev/ttyS3")'], size=13,
                    fill=FILL, stroke=LINE, sw=1.8, rx=8))

    # 2. інод
    p.append(text(410, cap_y, "інод файла пристрою", size=12.5, color=MUTED))
    p.append(fitbox(290, box_y, 240, box_h,
                    ["тип: символьний", "старший 4", "молодший 67", "вмісту немає"],
                    size=13, fill=WARM_FILL, stroke=WARM, sw=1.8, rx=8))

    # 3. таблиця драйверів за старшим
    p.append(text(680, cap_y, "таблиця за старшим", size=12.5, color=MUTED))
    rows = [("1", "пам'ять"), ("4", "порти tty"), ("5", "консоль"), ("10", "misc")]
    rh = 33
    for i, (num, name) in enumerate(rows):
        y = box_y + i * rh
        hot = (i == 1)
        p.append(rect(590, y, 180, rh, fill=GREEN_FILL if hot else FILL,
                      stroke=FIELD if hot else LINE, sw=1.8 if hot else 1.2, rx=4))
        p.append(text(680, y + rh / 2 + 5, num + "  " + name, size=12.5, bold=hot))

    # 4. драйвер
    p.append(text(935, cap_y, "код драйвера", size=12.5, color=MUTED))
    p.append(fitbox(830, box_y, 210, box_h,
                    ["таблиця операцій", "read · write · ioctl"],
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=8))

    # 5. примірник
    p.append(text(1160, cap_y, "примірник", size=12.5, color=MUTED))
    p.append(fitbox(1100, box_y + 36, 130, 60, ["порт 3"], size=14, bold=True,
                    fill=WARM_FILL, stroke=WARM, sw=1.8, rx=8))

    p.append(arrow(234, mid, 286, mid))
    p.append(arrow(534, mid, 586, mid, color=FIELD))
    p.append(arrow(774, mid, 826, mid, color=FIELD))
    p.append(arrow(1044, mid, 1096, mid, color=FIELD))

    p.append(text(680, 62, "ядро доводить пару до запису, зробленого драйвером",
                  size=13.5, bold=True, color=FIELD))

    # обхідний шлях молодшого
    ly = 356
    p.append(line(410, box_y + box_h, 410, ly, color=WARM, sw=2, dash="6 5"))
    p.append(line(410, ly, 1165, ly, color=WARM, sw=2, dash="6 5"))
    p.append(arrow(1165, ly, 1165, box_y + 100, color=WARM))
    p.append(text(700, 400,
                  "молодший 67 ядро віддає драйверові недоторканим; "
                  "той віднімає 64 і дістає свій третій порт",
                  size=13.5, bold=True, color=WARM))

    render(os.path.join(IMG, 'open-dispatch.svg'), W, H, *p)


# ── 3. Молодший означає те, що вирішив драйвер ───────────────────────────────
def fig_minor_meanings():
    W, H = 1120, 440
    p = []

    p.append(text(W / 2, 46, "той самий молодший — три різні домовленості",
                  size=16, bold=True))

    cols = [
        (30, NEG, BLUE_FILL, "драйвер послідовних портів",
         "молодший = номер порту",
         ["64 → ttyS0", "67 → ttyS3", "порти рівноправні"]),
        (390, FIELD, GREEN_FILL, "драйвер дисків sd",
         "молодший = диск і розділ разом",
         ["0 → sda", "3 → sda3", "16 → sdb", "по 16 номерів на диск"]),
        (750, WARM, WARM_FILL, "драйвер стрічкового приводу",
         "молодший = той самий привід, інший режим",
         ["0 → st0: перемотати", "128 → nst0: не перемотувати"]),
    ]

    for cx, hue, fillc, head, rule, items in cols:
        p.append(fitbox(cx, 78, 340, 56, [head], size=13.5, bold=True,
                        fill=fillc, stroke=hue, sw=2, rx=10))
        p.append(fitbox(cx, 148, 340, 52, [rule], size=12.5,
                        fill=FILL, stroke=hue, sw=1.5, rx=8))
        for i, it in enumerate(items):
            p.append(fitbox(cx + 24, 216 + i * 42, 292, 34, [it], size=12,
                            fill=FILL, stroke=MUTED, sw=1.2, rx=6))

    p.append(text(W / 2, 412,
                  "ядро не знає жодного з цих значень: молодший — приватна справа драйвера",
                  size=13.5, bold=True, color=MUTED))

    render(os.path.join(IMG, 'minor-meanings.svg'), W, H, *p)


# ── 4. Чому стабільним стало ім'я, а не число ────────────────────────────────
def fig_number_to_name():
    W, H = 860, 660
    p = []

    X, BW, BH, STEP = 60, 740, 58, 84

    p.append(text(W / 2, 46, "чому опорою стало ім'я, а не число", size=16, bold=True))

    steps = [
        ("старших номерів усього 4096, а драйверів усе більшає", NEG, BLUE_FILL),
        ("старший номер видає саме ядро — у мить, коли драйвер завантажився", NEG, BLUE_FILL),
        ("номер тепер залежить від порядку завантаження й може змінитися", POS, RED_FILL),
        ("тека /dev, зроблена наперед, починає вказувати не туди", POS, RED_FILL),
        ("вузол мусить творити той, хто бачить появу пристрою, — devtmpfs", FIELD, GREEN_FILL),
        ("стале ім'я й посилання на нього довішує udev", FIELD, GREEN_FILL),
    ]

    y = 78
    for i, (txt, hue, fillc) in enumerate(steps):
        p.append(fitbox(X, y, BW, BH, [txt], size=13.5, fill=fillc, stroke=hue,
                        sw=1.7, rx=9))
        if i < len(steps) - 1:
            p.append(arrow(X + BW / 2, y + BH, X + BW / 2, y + STEP - 2, color=hue))
        y += STEP

    p.append(text(W / 2, y + 22,
                  "число лишилося адресою всередині ядра; назовні його заступило ім'я",
                  size=13.5, bold=True, color=MUTED))

    render(os.path.join(IMG, 'number-to-name.svg'), W, H, *p)


# ── 5. Резервування номерів і реєстрація коду — різні дії ────────────────────
def fig_cdev_span():
    W, H = 1160, 470
    p = []

    p.append(text(W / 2, 40, "зарезервувати номери — ще не означає поставити за ними код",
                  size=16, bold=True))

    # спільна для обох випадків смуга резервування
    p.append(fitbox(70, 60, 1020, 48,
                    ["alloc_chrdev_region(&first, 0, 4, \"fanout\")  —  "
                     "в обох випадках однаково: пари 511:0 … 511:3 записано за модулем"],
                    size=13, fill=WARM_FILL, stroke=WARM, sw=1.8, rx=9))

    PW = 470
    LX, RX = 70, 620
    HEADY, ROWY, ROWH, BANDY, BANDH = 142, 210, 54, 292, 52
    bw, gap = (PW - 3 * 10) / 4.0, 10

    def minors(px, good_upto):
        for i in range(4):
            x = px + i * (bw + gap)
            ok = i < good_upto
            p.append(rect(x, ROWY, bw, ROWH,
                          fill=GREEN_FILL if ok else RED_FILL,
                          stroke=FIELD if ok else POS, sw=1.8, rx=7))
            p.append(text(x + bw / 2, ROWY + ROWH / 2 + 5, "511:%d" % i,
                          size=13.5, bold=True, color=FIELD if ok else POS))

    # ── ліворуч: cdev на весь відтинок ──
    p.append(fitbox(LX, HEADY, PW, 48, ["cdev_add(&cdev, first, 4)"],
                    size=14, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=9))
    minors(LX, 4)
    p.append(rect(LX, BANDY, PW, BANDH, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=8))
    p.append(text(LX + PW / 2, BANDY + BANDH / 2 + 5,
                  "один cdev · одна таблиця операцій", size=13.5, bold=True, color=FIELD))
    for i in range(4):
        cx = LX + i * (bw + gap) + bw / 2
        p.append(arrow(cx, BANDY - 4, cx, ROWY + ROWH + 6, color=FIELD, sw=1.6))
    p.append(mtext(LX + PW / 2, BANDY + BANDH + 34,
                   ["open будь-якого з чотирьох вузлів доходить до драйвера,",
                    "а той обирає примірник за молодшим номером"],
                   size=13, color=MUTED))

    # ── праворуч: cdev на один номер ──
    p.append(fitbox(RX, HEADY, PW, 48, ["cdev_add(&cdev, first, 1)"],
                    size=14, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=9))
    minors(RX, 1)
    p.append(rect(RX, BANDY, bw, BANDH, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=8))
    p.append(text(RX + bw / 2, BANDY + BANDH / 2 + 5, "cdev",
                  size=13.5, bold=True, color=FIELD))
    cx0 = RX + bw / 2
    p.append(arrow(cx0, BANDY - 4, cx0, ROWY + ROWH + 6, color=FIELD, sw=1.6))
    p.append(rect(RX + bw + gap, BANDY, PW - bw - gap, BANDH,
                  fill=RED_FILL, stroke=POS, sw=1.6, rx=8))
    p.append(text(RX + bw + gap + (PW - bw - gap) / 2, BANDY + BANDH / 2 + 5,
                  "у мапі порожньо", size=13.5, bold=True, color=POS))
    p.append(mtext(RX + PW / 2, BANDY + BANDH + 34,
                   ["open /dev/fanout1 віддає ENXIO,",
                    "хоча вузол і пара чисел бездоганні"],
                   size=13, color=MUTED))

    render(os.path.join(IMG, 'cdev-span.svg'), W, H, *p)


if __name__ == '__main__':
    fig_number_split()
    fig_open_dispatch()
    fig_minor_meanings()
    fig_number_to_name()
    fig_cdev_span()
    print("ok:", sorted(os.listdir(IMG)))
