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


# ── 1. Один том, чотири імені ──────────────────────────────────────────────
def fig_one_disk_many_names():
    W, H = 1500, 900
    p = []

    lx, rx = 260, 560          # два стовпці «заліза»
    cx = (lx + rx) / 2
    px = 1130                  # стовпець «що бачить ядро»

    p.append(text(cx, 70, "залізо", size=15, bold=True))
    p.append(text(px, 70, "що бачить ядро", size=15, bold=True))

    srv, sw_, sh_ = textbox(cx, 140, ["сервер"], size=14, pad=16,
                            fill=GREY_FILL, stroke=LINE)
    p.append(srv)

    ports = []
    for x, lbl in ((lx, "порт адаптера 1"), (rx, "порт адаптера 2")):
        fr, w, h = textbox(x, 265, [lbl], size=13, pad=14,
                           fill=GREEN_FILL, stroke=LINE)
        p.append(fr)
        ports.append((x, w, h))
    p.append(arrow(cx - 60, 140 + sh_ / 2, lx, 265 - ports[0][2] / 2))
    p.append(arrow(cx + 60, 140 + sh_ / 2, rx, 265 - ports[1][2] / 2))

    fabrics = []
    for x, lbl in ((lx, "комутатор A"), (rx, "комутатор B")):
        fr, w, h = textbox(x, 415, [lbl], size=13, pad=14,
                           fill=BLUE_FILL, stroke=LINE)
        p.append(fr)
        fabrics.append((x, w, h))
    for i in range(2):
        p.append(arrow(ports[i][0], 265 + ports[i][2] / 2,
                       fabrics[i][0], 415 - fabrics[i][2] / 2))

    ctrls = []
    for x, lbl in ((lx, "контролер 1"), (rx, "контролер 2")):
        fr, w, h = textbox(x, 585, [lbl], size=13, pad=14,
                           fill=WARM_FILL, stroke=LINE)
        p.append(fr)
        ctrls.append((x, w, h))

    # кожен комутатор бачить обидва контролери → 2 × 2 = 4 дороги
    for i in range(2):
        for j in range(2):
            p.append(arrow(fabrics[i][0], 415 + fabrics[i][2] / 2,
                           ctrls[j][0], 585 - ctrls[j][2] / 2))

    lun, lw, lh = textbox(cx, 745, ["том", "один диск, одна копія даних"],
                          size=14, pad=16, fill=RED_FILL, stroke=LINE)
    p.append(lun)
    p.append(arrow(lx, 585 + ctrls[0][2] / 2, cx - 70, 745 - lh / 2))
    p.append(arrow(rx, 585 + ctrls[1][2] / 2, cx + 70, 745 - lh / 2))

    names = [
        (150, "/dev/sdb", "порт 1 · контролер 1"),
        (270, "/dev/sdc", "порт 1 · контролер 2"),
        (390, "/dev/sdd", "порт 2 · контролер 1"),
        (510, "/dev/sde", "порт 2 · контролер 2"),
    ]
    for y, dev, via in names:
        fr, w, h = textbox(px, y, [dev, via], size=13, pad=13,
                           fill=GREY_FILL, stroke=MUTED, sw=1.2)
        p.append(fr)

    wid, ww, wh = textbox(px, 680,
                          ["у всіх чотирьох INQUIRY 0x83 віддає",
                           "той самий ідентифікатор тому"],
                          size=13, pad=14, fill=GREEN_FILL, stroke=LINE)
    p.append(wid)

    p.append(text(px, 790,
                  "єдина ознака, з якої видно, що диск один",
                  size=13, color=MUTED))
    p.append(text(px, 818,
                  "розмір і модель у сусідніх томів такі самі",
                  size=13, color=POS))

    render(os.path.join(IMG, 'one-disk-many-names.svg'), W, H, *p,
           title="Чотири дороги дають чотири імені й один ідентифікатор")


# ── 2. Групи пріоритету ────────────────────────────────────────────────────
def fig_path_groups():
    W, H = 1560, 780
    p = []

    ax, bx = 330, 760          # дві дороги в групі
    mid = (ax + bx) / 2
    nx = 1290                  # стовпець приміток

    g1, g1w, g1h = textbox(mid, 130,
                           ["група 1 · prio 50 · active/optimized",
                            "стан: робоча"],
                           size=14, pad=15, fill=GREEN_FILL, stroke=LINE)
    p.append(g1)
    p.append(text(mid, 235,
                  "селектор шляху обирає дорогу для кожного запиту",
                  size=13, color=MUTED))

    for x, lbl in ((ax, "sdb — порт 1"), (bx, "sdd — порт 2")):
        fr, w, h = textbox(x, 320, [lbl, "через контролер-власник"],
                           size=13, pad=14, fill=BLUE_FILL, stroke=LINE)
        p.append(fr)
        p.append(arrow(mid + (x - mid) * 0.35, 130 + g1h / 2, x, 320 - h / 2))

    g2, g2w, g2h = textbox(mid, 500,
                           ["група 2 · prio 10 · active/non-optimized",
                            "стан: резерв, запитів не отримує"],
                           size=14, pad=15, fill=WARM_FILL, stroke=LINE)
    p.append(g2)

    for x, lbl in ((ax, "sdc — порт 1"), (bx, "sde — порт 2")):
        fr, w, h = textbox(x, 660, [lbl, "через контролер-партнер"],
                           size=13, pad=14, fill=GREY_FILL, stroke=MUTED, sw=1.2)
        p.append(fr)
        p.append(arrow(mid + (x - mid) * 0.35, 500 + g2h / 2, x, 660 - h / 2))

    p.append(arrow(mid, 130 + g1h / 2 + 5, mid, 500 - g2h / 2))
    p.append(text(mid, 395,
                  "перемикання: лише коли в групі 1 не лишилося живих доріг",
                  size=13, color=POS))

    n1, n1w, n1h = textbox(nx, 200,
                           ["усередині групи —", "розподіл навантаження"],
                           size=13, pad=13, fill="#ffffff", stroke=MUTED, sw=1.1)
    p.append(n1)
    n2, n2w, n2h = textbox(nx, 480,
                           ["між групами —", "впорядкований список"],
                           size=13, pad=13, fill="#ffffff", stroke=MUTED, sw=1.1)
    p.append(n2)
    n3, n3w, n3h = textbox(nx, 680,
                           ["номер групи оголошує", "сама полиця через ALUA"],
                           size=13, pad=13, fill="#ffffff", stroke=MUTED, sw=1.1)
    p.append(n3)

    render(os.path.join(IMG, 'path-groups.svg'), W, H, *p,
           title="Два поверхи карти: балансування всередині групи, перемикання між групами")


# ── 3. bio-режим проти запитоорієнтованого ─────────────────────────────────
def fig_request_vs_bio():
    W, H = 1520, 900
    p = []

    lx, rx = 390, 1130
    p.append(line(760, 100, 760, 800, color=MUTED, sw=1.2, dash="6 5"))

    p.append(text(lx, 90, "queue_mode bio", size=15, bold=True))
    p.append(text(rx, 90, "запитоорієнтований режим", size=15, bold=True))

    ys = [175, 315, 455, 595, 730]

    left = [
        (["три сусідні bio: сектори 100, 108, 116"], GREEN_FILL),
        (["дорогу обирають для КОЖНОГО bio"], BLUE_FILL),
        (["сусідні bio розійшлися", "по двох різних чергах"], WARM_FILL),
        (["склеювати нема з чим:", "три дрібні запити замість одного"], RED_FILL),
        (["виграє там, де склеювання не потрібне:", "NVMe з десятками черг"], GREEN_FILL),
    ]

    right = [
        (["три сусідні bio: сектори 100, 108, 116"], GREEN_FILL),
        (["власна черга multipath", "склеює їх в один запит"], WARM_FILL),
        (["дорогу обирають один раз —", "для готового запиту"], BLUE_FILL),
        (["клон запиту йде в чергу дороги", "цілим шматком"], BLUE_FILL),
        (["помилка → той самий запит,", "інша дорога, жодного дроблення"], GREEN_FILL),
    ]

    def col(x, rows):
        boxes = []
        for cy, (lines, fill) in zip(ys, rows):
            fr, w, h = textbox(x, cy, lines, size=13, pad=14, fill=fill, stroke=LINE)
            p.append(fr)
            boxes.append((cy, h))
        for a, b in zip(boxes, boxes[1:]):
            p.append(arrow(x, a[0] + a[1] / 2, x, b[0] - b[1] / 2))

    col(lx, left)
    col(rx, right)

    p.append(text(lx, 840, "затримка менша, склеювання немає", size=13, color=MUTED))
    p.append(text(rx, 840, "склеювання є, ціна — зайвий поверх черги", size=13, color=MUTED))

    render(os.path.join(IMG, 'request-vs-bio.svg'), W, H, *p,
           title="Де саме обирається дорога — до склеювання чи після")


# ── 4. Остання дорога впала: два налаштування ──────────────────────────────
def fig_no_path_timeline():
    W, H = 1500, 700
    p = []

    xs = [270, 730, 1200]

    def band(y_title, y_row, title, cells, tail):
        p.append(text(W / 2, y_title, title, size=15, bold=True))
        boxes = []
        for x, (lines, fill) in zip(xs, cells):
            fr, w, h = textbox(x, y_row, lines, size=13, pad=14,
                               fill=fill, stroke=LINE)
            p.append(fr)
            boxes.append((x, w, h))
        for a, b in zip(boxes, boxes[1:]):
            p.append(arrow(a[0] + a[1] / 2, y_row, b[0] - b[1] / 2, y_row))
        p.append(text(W / 2, y_row + boxes[1][2] / 2 + 48, tail,
                      size=13, color=MUTED))

    band(90, 195, "no_path_retry 12 · перевірка кожні 5 секунд",
         [(["0 с", "впала остання дорога"], RED_FILL),
          (["0…60 с", "запити чекають у черзі,", "процеси просто не рухаються"], WARM_FILL),
          (["60 с", "прапорець знято,", "черга віддає помилки"], GREEN_FILL)],
         "аварія на хвилину проходить непоміченою, довша перетворюється на чесну помилку")

    band(400, 505, "queue_if_no_path без обмеження",
         [(["0 с", "впала остання дорога"], RED_FILL),
          (["0…∞", "запити чекають у черзі"], WARM_FILL),
          (["ніколи", "процеси в непереривному сні,", "umount не завершується"], RED_FILL)],
         "рятує будь-яку аварію, з якої сховище повертається, і вішає машину, якщо не повертається")

    render(os.path.join(IMG, 'no-path-timeline.svg'), W, H, *p,
           title="Що стається із запитами, коли живих доріг не лишилося")


# ── 5. Стенд на петльових пристроях ────────────────────────────────────────
def fig_loop_stand():
    W, H = 1560, 1010
    p = []

    ax, bx = 420, 830          # дві дороги
    mid = (ax + bx) / 2
    nx = 1310                  # стовпець приміток

    top, tw, th = textbox(mid, 90, ["dd — той, хто пише"],
                          size=14, pad=14, fill=GREY_FILL, stroke=LINE)
    p.append(top)

    mp, mpw, mph = textbox(mid, 250,
                           ["/dev/mapper/mp — ціль multipath",
                            "дві групи по одній дорозі, queue_if_no_path"],
                           size=14, pad=16, fill=WARM_FILL, stroke=LINE)
    p.append(mp)
    p.append(arrow(mid, 90 + th / 2, mid, 250 - mph / 2))

    roads = []
    for x, lbl, mm in ((ax, "/dev/mapper/patha", "253:0"),
                       (bx, "/dev/mapper/pathb", "253:1")):
        fr, w, h = textbox(x, 470, [lbl + "   " + mm,
                                    "ціль linear — саме її таблицю",
                                    "підміняємо на error"],
                           size=13, pad=15, fill=GREEN_FILL, stroke=LINE)
        p.append(fr)
        p.append(arrow(mid + (x - mid) * 0.3, 250 + mph / 2, x, 470 - h / 2))
        roads.append((x, w, h))

    loops = []
    for (x, _, rh), lbl in zip(roads, ("/dev/loop0", "/dev/loop1")):
        fr, w, h = textbox(x, 680, [lbl, "таблиці не має —", "ламати нема що"],
                           size=13, pad=15, fill=BLUE_FILL, stroke=LINE)
        p.append(fr)
        p.append(arrow(x, 470 + rh / 2, x, 680 - h / 2))
        loops.append((x, w, h))

    fl, flw, flh = textbox(mid, 900,
                           ["lun.img — ОДИН файл на 128 МіБ",
                            "262144 сектори по 512 байтів"],
                           size=14, pad=16, fill=RED_FILL, stroke=LINE)
    p.append(fl)
    for x, _, lh in loops:
        p.append(arrow(x, 680 + lh / 2, mid + (x - mid) * 0.3, 900 - flh / 2))

    for y, lines in ((250, ["карта над dm-пристроями", "мусить бути в режимі bio"]),
                     (470, ["зламати можна лише те,", "що має власну таблицю"]),
                     (790, ["обидві петлі пишуть", "в ту саму сторінку файла —", "том справді один"])):
        fr, w, h = textbox(nx, y, lines, size=13, pad=13,
                           fill="#ffffff", stroke=MUTED, sw=1.1)
        p.append(fr)

    render(os.path.join(IMG, 'loop-stand.svg'), W, H, *p,
           title="Стенд: один файл, дві петлі, дві ламкі дороги й карта над ними")


if __name__ == '__main__':
    fig_one_disk_many_names()
    fig_path_groups()
    fig_request_vs_bio()
    fig_no_path_timeline()
    fig_loop_stand()
    print("ok")
