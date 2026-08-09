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


# ── 1. Що де лежить: розділ даних, розділ гешів, корінь поза носієм ─────────
def fig_hash_device_layout():
    W, H = 1300, 880
    p = []

    cx = 470          # вісь смуг
    note_x = 1080     # вісь пояснень праворуч
    link_x0, link_x1 = 810, 970

    def band(cy, lines, fill, note):
        frag, w, h = textbox(cx, cy, lines, size=13, pad=16, fill=fill,
                             stroke=LINE, sw=1.5, min_w=620)
        p.append(frag)
        nfrag, nw, nh = textbox(note_x, cy, note, size=12, pad=12,
                                fill=GREY_FILL, stroke=MUTED, sw=1.2)
        p.append(nfrag)
        p.append(line(link_x0, cy, link_x1, cy, color=MUTED, sw=1.1, dash="5 4"))
        return h

    y_data, y_l0, y_l1, y_l2, y_root = 105, 265, 400, 530, 680

    h_data = band(y_data,
                  ["розділ із даними   /dev/sda1",
                   "4 ГіБ   =   1 048 576 блоків по 4 КіБ"],
                  GREEN_FILL,
                  ["це те, що бачить", "файлова система"])

    h_l0 = band(y_l0,
                ["рівень 0   —   геші блоків даних",
                 "1 048 576 · 32 Б   =   8192 блоки   (32 МіБ)"],
                BLUE_FILL,
                ["у блок 4 КіБ входить", "4096 / 32 = 128 гешів"])

    h_l1 = band(y_l1,
                ["рівень 1   —   геші блоків рівня 0",
                 "8192 · 32 Б   =   64 блоки   (256 КіБ)"],
                BLUE_FILL,
                ["кожен рівень", "коротший у 128 разів"])

    h_l2 = band(y_l2,
                ["рівень 2   —   верхній, один блок",
                 "64 · 32 Б   =   2048 Б"],
                WARM_FILL,
                ["далі скорочувати", "нема чого"])

    rfrag, rw, rh = textbox(cx, y_root,
                            ["кореневий геш   —   32 байти",
                             "у таблиці device mapper, а НЕ на носії"],
                            size=13, pad=16, fill=RED_FILL, stroke=POS, sw=2,
                            min_w=620)
    p.append(rfrag)
    nfrag, nw, nh = textbox(note_x, y_root,
                            ["єдине число, якому", "довіряють ззовні"],
                            size=12, pad=12, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(nfrag)
    p.append(line(link_x0, y_root, link_x1, y_root, color=MUTED, sw=1.1, dash="5 4"))

    p.append(arrow(cx, y_data + h_data / 2, cx, y_l0 - h_l0 / 2))
    p.append(arrow(cx, y_l0 + h_l0 / 2, cx, y_l1 - h_l1 / 2))
    p.append(arrow(cx, y_l1 + h_l1 / 2, cx, y_l2 - h_l2 / 2))
    p.append(arrow(cx, y_l2 + h_l2 / 2, cx, y_root - rh / 2))

    p.append(text(120, y_l0 - 68, "гешуємо", size=12, color=MUTED, anchor="start"))
    p.append(text(120, y_l1 - 60, "гешуємо", size=12, color=MUTED, anchor="start"))
    p.append(text(120, y_l2 - 60, "гешуємо", size=12, color=MUTED, anchor="start"))
    p.append(text(120, y_root - 60, "гешуємо", size=12, color=MUTED, anchor="start"))

    # фізичний порядок на розділі гешів
    strip_y = 790
    p.append(text(80, strip_y - 42,
                  "порядок на розділі гешів /dev/sda2 — від верхнього рівня до нижнього:",
                  size=13, bold=True, anchor="start"))
    seg = [("суперблок 512 Б", GREY_FILL, 250),
           ("рівень 2 — 1 блок", WARM_FILL, 250),
           ("рівень 1 — 64 блоки", BLUE_FILL, 270),
           ("рівень 0 — 8192 блоки", BLUE_FILL, 300)]
    x = 80
    for lbl, fill, wseg in seg:
        p.append(fitbox(x, strip_y, wseg, 60, [lbl], size=12, pad=10,
                        fill=fill, stroke=LINE, sw=1.4))
        x += wseg + 14

    render(os.path.join(IMG, 'hash-device-layout.svg'), W, H, *p,
           title="Два розділи, три рівні гешів і корінь поза носієм")


# ── 2. Що ціль робить із запитом і як піднімається деревом ─────────────────
def fig_read_path():
    W, H = 1400, 900
    p = []

    lx, rx = 350, 1010
    p.append(line(690, 90, 690, 830, color=MUTED, sw=1.2, dash="6 5"))

    p.append(text(lx, 92, "шлях запиту", size=14, bold=True))
    p.append(text(rx, 92, "підйом деревом для одного блока", size=14, bold=True))

    left_rows = [
        (["bio від файлової системи", "читання блока 700 000"], GREEN_FILL),
        (["ціль verity забирає запит собі", "і пересилає його на /dev/sda1"], WARM_FILL),
        (["дані прийшли — але у верхніх шарах", "їх ще ніхто не бачив"], BLUE_FILL),
        (["робоча черга: гешування може заснути,", "тож у перериванні його не роблять"], WARM_FILL),
        (["збіглося: сторінки віддано вгору", "не збіглося: EIO і рядок у журналі"], GREY_FILL),
    ]
    ys_l = [175, 325, 475, 625, 780]

    boxes = []
    for (lines, fill), cy in zip(left_rows, ys_l):
        frag, w, h = textbox(lx, cy, lines, size=13, pad=14, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)
        boxes.append((cy, h))
    for i in range(len(boxes) - 1):
        p.append(arrow(lx, boxes[i][0] + boxes[i][1] / 2,
                       lx, boxes[i + 1][0] - boxes[i + 1][1] / 2))

    # окрема гілка: запис
    p.append(text(lx, 130, "запис сюди не доходить ніколи: DM_MAPIO_KILL, одразу EIO",
                  size=12, color=POS))

    right_rows = [
        (["очікуваний геш := корінь із таблиці"], RED_FILL),
        (["блок рівня 2: звірити з очікуваним,", "узяти з нього геш потрібного сусіда"], WARM_FILL),
        (["блок рівня 1: звірити,", "узяти геш потрібного сусіда"], BLUE_FILL),
        (["блок рівня 0: звірити,", "узяти геш самого блока даних"], BLUE_FILL),
        (["геш прочитаних 4 КіБ", "проти взятого з рівня 0"], GREEN_FILL),
    ]
    ys_r = [175, 325, 475, 625, 780]

    rboxes = []
    for (lines, fill), cy in zip(right_rows, ys_r):
        frag, w, h = textbox(rx, cy, lines, size=13, pad=14, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)
        rboxes.append((cy, h))
    for i in range(len(rboxes) - 1):
        p.append(arrow(rx, rboxes[i][0] + rboxes[i][1] / 2,
                       rx, rboxes[i + 1][0] - rboxes[i + 1][1] / 2))

    p.append(line(560, 625, 810, 400, color=MUTED, sw=1.1, dash="5 4"))
    p.append(text(1330, 250, "блоки", size=12, color=MUTED, anchor="end"))
    p.append(text(1330, 272, "рівнів 2 і 1", size=12, color=MUTED, anchor="end"))
    p.append(text(1330, 294, "майже завжди", size=12, color=MUTED, anchor="end"))
    p.append(text(1330, 316, "вже в кеші", size=12, color=MUTED, anchor="end"))

    render(os.path.join(IMG, 'read-path.svg'), W, H, *p,
           title="Читання через verity: пересилання, робоча черга, підйом деревом")


# ── 3. Звідки береться довіра до 32 байтів кореня ──────────────────────────
def fig_trust_chain():
    W, H = 1340, 820
    p = []

    cx = 400
    ys = [100, 230, 360, 490, 620]
    rows = [
        (["ключ, випалений у кристалі"], GREEN_FILL),
        (["прошивка перевіряє завантажувач"], GREEN_FILL),
        (["завантажувач перевіряє ядро", "разом із його командним рядком"], GREEN_FILL),
        (["у командному рядку — корінь дерева:", "32 байти, які ядро кладе в таблицю"], WARM_FILL),
        (["ціль verity звіряє з ним кожен", "прочитаний блок розділу"], WARM_FILL),
    ]

    boxes = []
    for (lines, fill), cy in zip(rows, ys):
        frag, w, h = textbox(cx, cy, lines, size=13, pad=14, fill=fill,
                             stroke=LINE, sw=1.5, min_w=520)
        p.append(frag)
        boxes.append((cy, h))
    for i in range(len(boxes) - 1):
        p.append(arrow(cx, boxes[i][0] + boxes[i][1] / 2,
                       cx, boxes[i + 1][0] - boxes[i + 1][1] / 2))

    # праворуч: те, чому не вірять
    sfrag, sw_, sh = textbox(1030, 360,
                             ["під підозрою цілком:",
                              "",
                              "розділ із даними",
                              "розділ гешів",
                              "суперблок на ньому",
                              "",
                              "ядро не читає звідти",
                              "жодного параметра —",
                              "усі приходять таблицею"],
                             size=13, pad=18, fill=RED_FILL, stroke=POS, sw=2)
    p.append(sfrag)
    p.append(line(700, 490, 900, 400, color=POS, sw=1.3, dash="6 5"))

    # варіант без ланцюга завантаження
    afrag, aw, ah = textbox(cx, 745,
                            ["якщо ланцюг завантаження сюди не дістає:",
                             "корінь приходить із підписом PKCS#7,",
                             "а його перевіряє кільце ключів ядра"],
                            size=13, pad=14, fill=BLUE_FILL, stroke=NEG, sw=1.8,
                            min_w=520)
    p.append(afrag)
    p.append(line(cx, 620 + boxes[4][1] / 2 + 8, cx, 745 - ah / 2 - 8,
                  color=NEG, sw=1.3, dash="6 5"))

    render(os.path.join(IMG, 'trust-chain.svg'), W, H, *p,
           title="Ланцюг довіри до кореневого гешу")


# ── 4. Стенд досліду: що стоїть між зіпсованим байтом і читанням ───────────
def fig_lab_caches():
    W, H = 1420, 900
    p = []

    cx = 430
    note_x = 1080
    link_x0, link_x1 = 750, 872

    p.append(text(120, 58, "знизу вгору — шлях байта до програми; праворуч — де він може застрягти",
                  size=14, bold=True, anchor="start"))

    ys = [150, 300, 450, 600, 760]
    rows = [
        (["cat /var/tmp/veritylab/mnt/one.bin"], GREEN_FILL,
         ["перше читання після псування", "може віддати старі байти —", "і це не помилка стенда"], POS),
        (["ext4, змонтована ro на /dev/mapper/vlab"], BLUE_FILL,
         ["кеш сторінок файлу:", "прочитане лежить у пам'яті", "→ echo 3 > drop_caches"], MUTED),
        (["ціль verity: підйом деревом до кореня"], WARM_FILL,
         ["блоки дерева кешує dm-bufio,", "блоки даних — ні:", "перевірка щоразу"], MUTED),
        (["/dev/loop0 → файл data.img"], GREY_FILL,
         ["loop читає бекінг-файл", "через його ж кеш сторінок", "→ sync після dd"], MUTED),
        (["байт 12288 файлу one.bin  =  блок 4112 пристрою"], RED_FILL,
         ["сюди й б'є", "dd ... conv=notrunc"], POS),
    ]

    boxes = []
    for (lines, fill, note, ncolor), cy in zip(rows, ys):
        frag, w, h = textbox(cx, cy, lines, size=13, pad=16, fill=fill,
                             stroke=POS if fill is RED_FILL else LINE,
                             sw=2 if fill is RED_FILL else 1.5, min_w=620)
        p.append(frag)
        boxes.append((cy, h))
        nfrag, nw, nh = textbox(note_x, cy, note, size=12, pad=13,
                                fill=GREY_FILL, stroke=ncolor, sw=1.3)
        p.append(nfrag)
        p.append(line(link_x0, cy, link_x1, cy, color=MUTED, sw=1.1, dash="5 4"))

    for i in range(len(boxes) - 1, 0, -1):
        p.append(arrow(cx - 250, boxes[i][0] - boxes[i][1] / 2,
                       cx - 250, boxes[i - 1][0] + boxes[i - 1][1] / 2))

    p.append(text(120, 455, "читання", size=12, color=MUTED, anchor="start"))
    p.append(text(120, 477, "іде вгору", size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'lab-caches.svg'), W, H, *p,
           title="Стенд: кеші між зіпсованим байтом і читанням файлу")


if __name__ == '__main__':
    fig_hash_device_layout()
    fig_read_path()
    fig_trust_chain()
    fig_lab_caches()
    print("ok")
