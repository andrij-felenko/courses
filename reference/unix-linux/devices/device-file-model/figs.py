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


# ── 1. Що тримає inode: дані проти мітки ────────────────────────────────────
def fig_node_anatomy():
    W, H = 1000, 450
    p = []

    p.append(text(250, 42, "звичайний файл", size=15, bold=True, color=FIELD))
    p.append(text(750, 42, "файл пристрою", size=15, bold=True, color=WARM))

    # ── ліва колонка ──
    p.append(fitbox(150, 70, 200, 46, "каталог: report.txt", size=13))
    p.append(arrow(250, 116, 250, 148))
    p.append(fitbox(110, 152, 280, 108,
                    ["inode", "тип: звичайний файл",
                     "розмір: 13 байтів", "блоки: три покажчики"],
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(arrow(250, 260, 250, 296))
    for i in range(3):
        x = 110 + i * 95
        p.append(rect(x, 300, 80, 50, fill=FILL, stroke=LINE, sw=1.5, rx=6))
        p.append(text(x + 40, 331, "дані", size=13))
    p.append(text(250, 398, "вміст лежить на носії", size=13, color=MUTED))

    # ── права колонка ──
    p.append(fitbox(650, 70, 200, 46, "каталог: ttyUSB0", size=13))
    p.append(arrow(750, 116, 750, 148))
    p.append(fitbox(596, 152, 308, 128,
                    ["inode", "тип: символьний пристрій",
                     "розмір: 0    блоків: 0", "мітка: 188 : 0"],
                    size=13, fill=WARM_FILL, stroke=WARM, sw=1.8))
    p.append(arrow(750, 280, 750, 314))
    p.append(fitbox(596, 318, 308, 52, "реєстр драйверів у ядрі",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(text(750, 410, "на носії — лише сам inode", size=13, color=MUTED))

    render(os.path.join(IMG, 'node-anatomy.svg'), W, H, *p)


# ── 2. Що відбувається на open: мітка → таблиця операцій драйвера ────────────
def fig_open_dispatch():
    W, H = 1240, 330
    p = []

    bw, bh, by = 200, 72, 88
    xs = [40, 280, 520, 760, 1000]
    boxes = [
        (['open("/dev/ttyUSB0")'], FILL, LINE),
        (["розбір шляху", "дає inode"], GREEN_FILL, FIELD),
        (["у inode: тип «c»", "мітка 188 : 0"], WARM_FILL, WARM),
        (["реєстр символьних", "пристроїв → cdev"], BLUE_FILL, NEG),
        (["struct file:", "операції ← драйвер"], BLUE_FILL, NEG),
    ]
    for x, (lines, fill, stroke) in zip(xs, boxes):
        p.append(fitbox(x, by, bw, bh, lines, size=13, fill=fill, stroke=stroke, sw=1.8))
    for x in xs[:-1]:
        p.append(arrow(x + bw + 4, by + bh / 2, x + bw + 36, by + bh / 2))

    p.append(text(400, 58, "працює файлова система", size=13, color=FIELD))
    p.append(text(980, 58, "працює ядро за міткою", size=13, color=NEG))

    p.append(arrow(1100, by + bh + 2, 1100, 202))
    p.append(fitbox(760, 206, 440, 56,
                    "далі read, write, ioctl ідуть просто в драйвер",
                    size=13, fill=WARM_FILL, stroke=WARM, sw=1.8))
    p.append(text(980, 296, "файлова система, де лежав вузол, більше не бере участі",
                  size=12.5, color=MUTED))

    render(os.path.join(IMG, 'open-dispatch.svg'), W, H, *p)


# ── 3. Хто стоїть між викликом і залізом ────────────────────────────────────
def fig_char_vs_block():
    W, H = 1160, 630
    p = []

    p.append(text(280, 40, "символьний", size=16, bold=True, color=POS))
    p.append(text(780, 40, "блоковий", size=16, bold=True, color=NEG))

    # ── ліва колонка: майже порожньо ──
    lw, lh = 280, 48
    lx = 140
    left = [(75, "read(fd)", FILL, LINE),
            (145, "VFS", FILL, LINE),
            (215, "функція .read драйвера", RED_FILL, POS),
            (495, "залізо", FILL, LINE)]
    for y, s, fill, stroke in left:
        p.append(fitbox(lx, y, lw, lh, s, size=13, fill=fill, stroke=stroke, sw=1.8))
    p.append(arrow(280, 123, 280, 143))
    p.append(arrow(280, 193, 280, 213))
    p.append(arrow(280, 263, 280, 493))
    p.append(text(280, 578, "між викликом і залізом — ніхто", size=13, color=MUTED))

    # ── права колонка: кеш і черга ──
    rw, rh = 300, 48
    rx0 = 630
    right = [(75, "read(fd)", FILL, LINE),
             (145, "VFS", FILL, LINE),
             (215, "кеш сторінок", GREEN_FILL, FIELD),
             (285, "запит bio", GREEN_FILL, FIELD),
             (355, "черга: злиття й порядок", GREEN_FILL, FIELD),
             (425, "драйвер обробляє запит", BLUE_FILL, NEG),
             (495, "залізо", FILL, LINE)]
    for y, s, fill, stroke in right:
        p.append(fitbox(rx0, y, rw, rh, s, size=13, fill=fill, stroke=stroke, sw=1.8))
    for y in (75, 145, 215, 285, 355, 425):
        p.append(arrow(780, y + rh + 2, 780, y + 68))

    # зворотний шлях: переривання завершення
    p.append(line(rx0 + rw, 519, 970, 519, color=NEG, sw=1.6))
    p.append(line(970, 519, 970, 239, color=NEG, sw=1.6))
    p.append(arrow(970, 239, rx0 + rw + 2, 239, color=NEG, sw=1.6))
    p.append(text(986, 384, "переривання", size=12.5, color=NEG, anchor="start"))
    p.append(text(986, 404, "завершення", size=12.5, color=NEG, anchor="start"))

    p.append(text(780, 578, "кеш і черга вільні зливати,", size=13, color=MUTED))
    p.append(text(780, 600, "переставляти й відкладати", size=13, color=MUTED))

    render(os.path.join(IMG, 'char-vs-block.svg'), W, H, *p)


# ── 4. Хто створює вузли в /dev ─────────────────────────────────────────────
def fig_dev_population():
    W, H = 1100, 350
    p = []

    p.append(text(24, 60, "ядро", size=15, bold=True, color=NEG, anchor="start"))
    p.append(text(24, 220, "простір користувача", size=15, bold=True,
                  color=FIELD, anchor="start"))

    bw, bh = 230, 74
    top, bot = 76, 236

    p.append(fitbox(40, top, bw, bh, ["під'єднано", "пристрій"],
                    size=13, fill=FILL, stroke=LINE, sw=1.8))
    p.append(fitbox(300, top, bw, bh, ["драйвер реєструє:", "клас і номери"],
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(560, top, bw, bh, ["devtmpfs: вузол у /dev", "з типовими правами"],
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(arrow(274, top + bh / 2, 296, top + bh / 2))
    p.append(arrow(534, top + bh / 2, 556, top + bh / 2))

    p.append(fitbox(300, bot, bw, bh, ["подія (uevent)", "надходить до udev"],
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(560, bot, bw, bh, ["правила udev:", "власник, група, права"],
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(820, bot, bw, bh, ["стійкі імена:", "/dev/disk/by-id/…"],
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(arrow(534, bot + bh / 2, 556, bot + bh / 2))
    p.append(arrow(794, bot + bh / 2, 816, bot + bh / 2))

    p.append(arrow(415, top + bh + 2, 415, bot - 4))
    p.append(arrow(675, bot - 4, 675, top + bh + 2, color=FIELD))
    p.append(text(660, 186, "міняє права на вже створеному вузлі",
                  size=12.5, color=MUTED, anchor="end"))

    render(os.path.join(IMG, 'dev-population.svg'), W, H, *p)


# ── 5. Дві незалежні реєстрації в module_init (вставка proj-char-driver) ────
def fig_two_registrations():
    W, H = 1080, 440
    BW, BH = 300, 82
    X1, X2, X3 = 30, 380, 730
    YA, YB = 92, 268

    p = []
    p.append(text(540, 34, "module_init(): дві незалежні реєстрації",
                  size=16, bold=True))

    # ── верхній рядок: підсистема символьних пристроїв ──
    p.append(text(30, 78, "1 · реєстр символьних пристроїв: номери → операції",
                  size=13, bold=True, color=NEG, anchor="start"))

    p.append(fitbox(X1, YA, BW, BH,
                    ["alloc_chrdev_region()", "ядро видає вільний",
                     "старший номер, скажімо 511"],
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(X2, YA, BW, BH,
                    ["cdev_init() + cdev_add()", "у реєстрі з'являється",
                     "511:0 → file_operations"],
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(X3, YA, BW, BH,
                    ["open() по цих номерах", "уже потрапляє в драйвер —",
                     "але вузла в /dev ще немає"],
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.8))

    p.append(arrow(X1 + BW, YA + BH / 2, X2 - 4, YA + BH / 2))
    p.append(arrow(X2 + BW, YA + BH / 2, X3 - 4, YA + BH / 2))

    # ── нижній рядок: модель пристроїв ──
    p.append(text(30, 254, "2 · модель пристроїв у sysfs: звідки береться вузол",
                  size=13, bold=True, color=FIELD, anchor="start"))

    p.append(fitbox(X1, YB, BW, BH,
                    ["class_create() + device_create()", "пристрій стає в модель,",
                     "несучи в собі той самий dev_t"],
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(X2, YB, BW, BH,
                    ["devtmpfs підвішено до самої", "реєстрації: вузол /dev/lichylnyk",
                     "з'являється одразу"],
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(X3, YB, BW, BH,
                    ["udev дістає подію, читає", "«511:0» з файла dev у sysfs",
                     "і доводить права та імена"],
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    p.append(arrow(X1 + BW, YB + BH / 2, X2 - 4, YB + BH / 2))
    p.append(arrow(X2 + BW, YB + BH / 2, X3 - 4, YB + BH / 2))

    # ── спільний dev_t ──
    p.append(arrow(150, YA + BH + 4, 150, YB - 6, color=MUTED, sw=1.4))
    p.append(text(166, YB - 40, "той самий dev_t",
                  size=12.5, color=MUTED, anchor="start"))

    p.append(mtext(540, 384,
                   ["Прибрати верхній рядок — вузол у /dev є, а open дає ENXIO.",
                    "Прибрати нижній — драйвер працює, тільки вузол доводиться робити mknod вручну."],
                   size=12.5, color=MUTED))

    render(os.path.join(IMG, 'two-registrations.svg'), W, H, *p)


fig_node_anatomy()
fig_open_dispatch()
fig_char_vs_block()
fig_dev_population()
fig_two_registrations()
print("готово")
