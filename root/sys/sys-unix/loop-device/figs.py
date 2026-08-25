# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
RED_FILL = "#fdecea"
GREY_FILL = "#eceff1"


def chain(p, cx, ys, cells, gap=14):
    """Вертикальний ланцюг рамок із стрілками між ними. Повертає список (y, h)."""
    geo = []
    for y, (lines, fill) in zip(ys, cells):
        frag, w, h = textbox(cx, y, lines, size=13, pad=14, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)
        geo.append((y, w, h))
    for (y1, _, h1), (y2, _, h2) in zip(geo, geo[1:]):
        p.append(arrow(cx, y1 + h1 / 2 + gap, cx, y2 - h2 / 2 - gap))
    return geo


# ── 1. Шлях одного запиту: із блокового шару у файловий і назад ─────────────
def fig_request_path():
    W, H = 1280, 940
    p = []
    cx = 400
    nx = 960          # вісь правих приміток

    ys = [95, 215, 340, 470, 600, 725, 855]
    cells = [
        (["файлова система всередині образу,", "змонтована на /dev/loop0"], GREEN_FILL),
        (["блоковий шар: запит до /dev/loop0", "сектори 2048…2055"], BLUE_FILL),
        (["драйвер loop", "зсув у файлі = offset + 2048 · 512"], WARM_FILL),
        (["читання/запис у disk.img", "через звичайний файловий інтерфейс"], WARM_FILL),
        (["файлова система, на якій лежить disk.img", "розкладає зсув по своїх екстентах"], GREEN_FILL),
        (["блоковий шар: запит до /dev/sda2"], BLUE_FILL),
        (["справжній носій"], GREY_FILL),
    ]
    geo = chain(p, cx, ys, cells)

    def note(y, lines, fill=GREY_FILL):
        frag, w, h = textbox(nx, y, lines, size=12.5, pad=12, fill=fill,
                             stroke=MUTED, sw=1.2)
        p.append(frag)
        p.append(line(cx + 250, y, nx - w / 2 - 16, y, color=MUTED, sw=1.1, dash="5 4"))

    note(215, ["номер сектора —", "єдине, що знає", "верхня файлова система"])
    note(405, ["тут запит покидає блоковий шар",
               "і повертається у файловий:",
               "петля всередині того самого ядра"], WARM_FILL)
    note(725, ["звідси й далі — шлях,", "яким іде будь-який файл"])

    p.append(text(W / 2, H - 22,
                  "Ніщо в цьому ланцюгу не виходить у простір користувача: обидві половини — підсистеми ядра.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'request-path.svg'), W, H, *p,
           title="Шлях запиту до сектора крізь loop-пристрій")


# ── 2. Ті самі байти двічі в пам'яті — і як цього уникнути ─────────────────
def fig_double_cache():
    W, H = 1300, 700
    p = []
    lx, rx = 340, 960

    p.append(text(lx, 78, "буферизований режим (типово)", size=15, bold=True))
    p.append(text(rx, 78, "прямий ввід-вивід: --direct-io=on", size=15, bold=True))

    ys = [175, 300, 425, 560]

    left = [
        (["сторінки /dev/loop0", "кеш файлової системи в образі"], BLUE_FILL),
        (["сторінки disk.img", "кеш файлової системи-господаря"], RED_FILL),
        (["запис на носій"], GREY_FILL),
    ]
    chain(p, lx, ys[:3], left)

    right = [
        (["сторінки /dev/loop0", "кеш файлової системи в образі"], BLUE_FILL),
        (["кеш disk.img обійдено", "драйвер пише в файл напряму"], GREEN_FILL),
        (["запис на носій"], GREY_FILL),
    ]
    chain(p, rx, ys[:3], right)

    frag, w, h = textbox(lx, ys[3],
                         ["ті самі байти лежать у пам'яті двічі,",
                          "і брудні сторінки скидаються теж двічі"],
                         size=13, pad=13, fill=RED_FILL, stroke=POS, sw=1.4)
    p.append(frag)

    frag, w, h = textbox(rx, ys[3],
                         ["одна копія в пам'яті,",
                          "але зсуви й довжини мусять бути",
                          "вирівняні на розмір блока"],
                         size=13, pad=13, fill=GREEN_FILL, stroke=FIELD, sw=1.4)
    p.append(frag)

    p.append(line(W / 2, 110, W / 2, H - 60, color=MUTED, sw=1.2, dash="6 5"))

    render(os.path.join(IMG, 'double-cache.svg'), W, H, *p,
           title="Два кеші на одні дані — і режим, який лишає один")


# ── 3. Видалення всередині образу віддає місце господареві ─────────────────
def fig_discard_hole():
    W, H = 1280, 720
    p = []

    n = 14
    cw, ch = 62, 54
    x0 = 300
    gap = 6

    def row(y, filled, label, sub):
        for i in range(n):
            x = x0 + i * (cw + gap)
            if filled[i] == 1:
                p.append(rect(x, y, cw, ch, fill=BLUE_FILL, stroke=LINE, sw=1.4))
            elif filled[i] == 2:
                p.append(rect(x, y, cw, ch, fill="#ffffff", stroke=MUTED, sw=1.2))
            else:
                p.append(rect(x, y, cw, ch, fill=GREY_FILL, stroke=MUTED, sw=1.2))
        frag, w, h = textbox(150, y + ch / 2, label, size=13, pad=12,
                             fill=WARM_FILL, stroke=LINE, sw=1.3)
        p.append(frag)
        p.append(text(x0 + n * (cw + gap) / 2 - gap / 2, y + ch + 34, sub,
                      size=13, color=MUTED))

    full = [1] * 10 + [0] * 4
    holed = [1, 1, 2, 2, 2, 2, 1, 1, 2, 2] + [0] * 4

    row(150, full, ["disk.img", "до очищення"],
        "десять блоків справді виділено у файлі — du показує їхній обсяг")
    row(400, holed, ["disk.img", "після fstrim"],
        "шість блоків вибито в діри — місце повернуто файловій системі-господареві")

    frag, w, h = textbox(W / 2, 300,
                         ["файлова система в образі каже «ці сектори більше не потрібні» (discard)",
                          "драйвер loop перекладає це у fallocate(PUNCH_HOLE) на disk.img"],
                         size=13, pad=13, fill=GREEN_FILL, stroke=FIELD, sw=1.4)
    p.append(frag)

    lg_y = 585
    p.append(rect(x0, lg_y, 34, 26, fill=BLUE_FILL, stroke=LINE, sw=1.3))
    p.append(text(x0 + 48, lg_y + 18, "зайнятий блок", size=13, anchor="start"))
    p.append(rect(x0 + 250, lg_y, 34, 26, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(text(x0 + 298, lg_y + 18, "діра: блоку немає, читається як нулі",
                  size=13, anchor="start"))
    p.append(rect(x0 + 700, lg_y, 34, 26, fill=GREY_FILL, stroke=MUTED, sw=1.2))
    p.append(text(x0 + 748, lg_y + 18, "хвіст образу, ще не займаний", size=13, anchor="start"))

    p.append(text(W / 2, 665,
                  "Логічний розмір образу не змінюється — змінюється лише те, скільки він насправді займає.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'discard-hole.svg'), W, H, *p,
           title="Discard усередині образу стає дірою в файлі")


# ── 4. Життя cryptoloop: від появи до вилучення (вставка hist) ──────────────
def fig_cryptoloop_timeline():
    W, H = 1300, 500
    p = []

    ax_y = 250
    p.append(line(70, ax_y, 1230, ax_y, color=MUTED, sw=2))

    events = [
        (180, 'up', ["ядро 2.5.x", "cryptoloop стає над", "новим Crypto API"], BLUE_FILL),
        (425, 'down', ["ядро 2.6.4, 2004", "з'являється dm-crypt:", "«прибрати cryptoloop", "якнайшвидше»"], GREEN_FILL),
        (670, 'up', ["util-linux 2.23, 2013", "losetup втрачає", "прапорці -e / -E"], WARM_FILL),
        (905, 'down', ["ядро 5.15, 2021", "Kconfig обіцяє", "вилучення в 5.16"], WARM_FILL),
        (1140, 'up', ["ядро 5.16, 2022", "код cryptoloop", "видалено з дерева"], RED_FILL),
    ]

    for x, side, lines, fill in events:
        cy = 120 if side == 'up' else 385
        frag, w, h = textbox(x, cy, lines, size=13, pad=13, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)
        if side == 'up':
            p.append(line(x, cy + h / 2 + 6, x, ax_y - 12, color=MUTED, sw=1.3))
        else:
            p.append(line(x, cy - h / 2 - 6, x, ax_y + 12, color=MUTED, sw=1.3))
        p.append(circle(x, ax_y, 7, fill="#ffffff", stroke=LINE, sw=2))

    p.append(text(70, ax_y - 22, "шифрування всередині loop", size=13,
                  color=MUTED, anchor="start"))
    p.append(text(1230, ax_y - 22, "шифрування окремим шаром", size=13,
                  color=MUTED, anchor="end"))

    render(os.path.join(IMG, 'cryptoloop-timeline.svg'), W, H, *p,
           title="Cryptoloop: від появи над Crypto API до вилучення у 5.16")


# ── 5. Життя однієї прив'язки: від вільного номера до відчеплення ───────────
def fig_attach_lifecycle():
    W, H = 1440, 900
    p = []
    cx = 680

    steps = [
        (70,  ["fd_ctl = open(\"/dev/loop-control\", O_RDWR)"], GREY_FILL),
        (172, ["n = ioctl(fd_ctl, LOOP_CTL_GET_FREE)",
               "ядро віддає номер вільного пристрою"], BLUE_FILL),
        (285, ["fd_dev = open(\"/dev/loopN\", O_RDWR)"], BLUE_FILL),
        (380, ["fd_img = open(\"disk.img\", O_RDWR)"], GREEN_FILL),
        (498, ["ioctl(fd_dev, LOOP_CONFIGURE, &cfg)",
               "дескриптор образу · зсув · sizelimit · розмір блока · прапорці"], GREEN_FILL),
        (618, ["pread(fd_dev, …) — пристрій уже працює"], WARM_FILL),
        (722, ["ioctl(fd_dev, LOOP_CLR_FD) повертає 0",
               "ядро лише ставить прапорець LO_FLAGS_AUTOCLEAR"], WARM_FILL),
        (830, ["close(fd_dev)",
               "ось тут прив'язка справді розпадається"], RED_FILL),
    ]

    geo = []
    for y, lines, fill in steps:
        frag, w, h = textbox(cx, y, lines, size=13.5, pad=14, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)
        geo.append((y, w, h))
    for (y1, _, h1), (y2, _, h2) in zip(geo, geo[1:]):
        p.append(arrow(cx, y1 + h1 / 2 + 8, cx, y2 - h2 / 2 - 8))

    def note(i, lines, fill=GREY_FILL, nx=1180):
        y, w0, _ = geo[i]
        frag, w, h = textbox(nx, y, lines, size=12.5, pad=12, fill=fill,
                             stroke=MUTED, sw=1.2)
        p.append(frag)
        p.append(line(cx + w0 / 2 + 12, y, nx - w / 2 - 12, y,
                      color=MUTED, sw=1.1, dash="5 4"))

    note(2, ["ENOENT або EACCES: вузла ще немає",
             "або udev не встиг виставити права —",
             "пауза 25 мс і нова спроба, до шістнадцяти"], WARM_FILL)
    note(4, ["один виклик замість LOOP_SET_FD",
             "плюс LOOP_SET_STATUS64: між ними пристрій",
             "жив би з неправильними параметрами"], GREEN_FILL)
    note(6, ["доки на пристрої стоїть монтування",
             "чи відкритий чужий дескриптор —",
             "відчеплення тільки відкладається"], WARM_FILL)

    # гілка EBUSY: назад по вільний номер
    lx = 56
    y5, w5, h5 = geo[4]
    y2, w2, _ = geo[1]
    p.append(line(cx - w5 / 2 - 12, y5 + h5 / 2 - 6, lx, y5 + h5 / 2 - 6,
                  color=POS, sw=1.4, dash="6 4"))
    p.append(line(lx, y5 + h5 / 2 - 6, lx, y2, color=POS, sw=1.4, dash="6 4"))
    p.append(arrow(lx, y2, cx - w2 / 2 - 12, y2, color=POS))

    frag, _, _ = textbox(250, 350, ["EBUSY: той самий номер устиг",
                                    "зайняти інший процес —",
                                    "беремо наступний і пробуємо знову"],
                         size=12.5, pad=12, fill=RED_FILL, stroke=POS, sw=1.3)
    p.append(frag)

    render(os.path.join(IMG, 'attach-lifecycle.svg'), W, H, *p,
           title="Життя однієї прив'язки: від вільного номера до відчеплення")


if __name__ == '__main__':
    fig_request_path()
    fig_double_cache()
    fig_discard_hole()
    fig_cryptoloop_timeline()
    fig_attach_lifecycle()
    print("ok")
