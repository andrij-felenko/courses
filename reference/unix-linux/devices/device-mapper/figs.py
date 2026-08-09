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


# ── 1. Стек шарів і розкладання номера сектора по таблиці ───────────────────
def fig_stack_and_table():
    W, H = 1240, 700
    p = []

    cx = 380          # вісь стека
    ax = 950          # вісь правої колонки з адресами
    link_x0, link_x1 = 640, 800

    def level(cy, lines, fill, note):
        frag, w, h = textbox(cx, cy, lines, size=13, pad=14, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)
        nfrag, nw, nh = textbox(ax, cy, note, size=13, pad=12, fill=GREY_FILL,
                                stroke=MUTED, sw=1.2)
        p.append(nfrag)
        p.append(line(link_x0, cy, link_x1, cy, color=MUTED, sw=1.1, dash="5 4"))
        return h

    y_fs, y_crypt, y_lin, y_disk = 95, 250, 420, 610

    h_fs = level(y_fs,
                 ["файлова система на /dev/mapper/home"],
                 GREEN_FILL,
                 ["читає сектор", "5 000 000"])

    h_cr = level(y_crypt,
                 ["/dev/mapper/home   —   ціль crypt",
                  "0   6291456   crypt   aes-xts   /dev/mapper/vg-raw   0"],
                 WARM_FILL,
                 ["номер той самий,", "інші будуть байти"])

    h_li = level(y_lin,
                 ["/dev/mapper/vg-raw   —   ціль linear, два відрізки",
                  "0         2097152   linear   /dev/sdb   0",
                  "2097152   4194304   linear   /dev/sdc   2048"],
                 BLUE_FILL,
                 ["5 000 000 лягає", "у другий відрізок"])

    # два фізичні носії
    dfrag_b, wb, hb = textbox(250, y_disk, ["/dev/sdb", "1 ГіБ"], size=13,
                              pad=13, fill=GREY_FILL, stroke=LINE)
    dfrag_c, wc, hc = textbox(520, y_disk, ["/dev/sdc", "2 ГіБ"], size=13,
                              pad=13, fill=GREY_FILL, stroke=LINE)
    p.append(dfrag_b)
    p.append(dfrag_c)

    nfrag, nw, nh = textbox(ax, y_disk,
                            ["5 000 000 − 2 097 152 + 2 048", "= сектор 2 904 896 на /dev/sdc"],
                            size=13, pad=12, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(nfrag)
    p.append(line(link_x0, y_disk, link_x1, y_disk, color=MUTED, sw=1.1, dash="5 4"))

    # стрілки вниз по стеку
    p.append(arrow(cx, y_fs + h_fs / 2, cx, y_crypt - h_cr / 2))
    p.append(arrow(cx, y_crypt + h_cr / 2, cx, y_lin - h_li / 2))
    p.append(arrow(320, y_lin + h_li / 2, 250, y_disk - hb / 2))
    p.append(arrow(440, y_lin + h_li / 2, 520, y_disk - hc / 2))

    p.append(text(120, y_disk - 60, "відрізок 1", size=12, color=MUTED, anchor="start"))
    p.append(text(600, y_disk - 60, "відрізок 2", size=12, color=MUTED, anchor="end"))

    render(os.path.join(IMG, 'stack-and-table.svg'), W, H, *p,
           title="Стек шарів: один запит, три системи координат")


# ── 2. Дві долі bio: переадресація або власна обробка ───────────────────────
def fig_two_fates():
    W, H = 1240, 760
    p = []

    lx, rx = 320, 900
    p.append(line(610, 90, 610, 690, color=MUTED, sw=1.2, dash="6 5"))

    p.append(text(lx, 92, "ціль лише переписала адресу", size=14, bold=True))
    p.append(text(rx, 92, "ціль забрала запит собі", size=14, bold=True))
    p.append(text(lx, 116, "DM_MAPIO_REMAPPED", size=12, color=MUTED))
    p.append(text(rx, 116, "DM_MAPIO_SUBMITTED", size=12, color=MUTED))

    left_rows = [
        ["bio від файлової системи", "сектор 100 у /dev/mapper/home"],
        ["ціль linear: два поля змінено"],
        ["той самий bio", "сектор 4196 у /dev/sdc"],
        ["черга блокового шару й залізо"],
        None,
    ]
    left_fills = [GREEN_FILL, WARM_FILL, GREEN_FILL, GREY_FILL, None]

    right_rows = [
        ["bio від файлової системи", "сектор 100 у /dev/mapper/home"],
        ["ціль crypt: власні сторінки", "і прохід шифру"],
        ["клон bio на нові сторінки", "сектор 4196 у /dev/sdc"],
        ["черга блокового шару й залізо"],
        ["клон завершився —", "ціль завершує оригінал"],
    ]
    right_fills = [GREEN_FILL, RED_FILL, BLUE_FILL, GREY_FILL, WARM_FILL]

    ys = [180, 300, 420, 540, 655]

    def draw_col(x, rows, fills):
        boxes = []
        for cy, lines, fill in zip(ys, rows, fills):
            if lines is None:
                boxes.append(None)
                continue
            frag, w, h = textbox(x, cy, lines, size=13, pad=13, fill=fill,
                                 stroke=LINE, sw=1.5)
            p.append(frag)
            boxes.append((cy, h))
        for i in range(len(boxes) - 1):
            a, b = boxes[i], boxes[i + 1]
            if a and b:
                p.append(arrow(x, a[0] + a[1] / 2, x, b[0] - b[1] / 2))
        return boxes

    draw_col(lx, left_rows, left_fills)
    draw_col(rx, right_rows, right_fills)

    p.append(text(lx, 600, "жодного копіювання даних", size=12, color=MUTED))
    p.append(text(lx, 622, "ціна ≈ одне додавання", size=12, color=MUTED))
    p.append(text(rx, 718, "ціна: сторінка пам'яті й шифр на кожен блок",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'two-fates.svg'), W, H, *p,
           title="Дві поведінки цілі на один і той самий запит")


# ── 3. Підміна таблиці наживо ──────────────────────────────────────────────
def fig_table_swap():
    W, H = 1320, 620
    p = []

    label_x, label_w = 55, 235
    col_x = [305, 555, 805, 1055]
    col_w = 230
    head_y = 105
    row_y = [150, 275, 400]
    row_h = 95

    heads = ["звичайна робота", "suspend", "load --table", "resume"]
    for x, hd in zip(col_x, heads):
        p.append(text(x + col_w / 2, head_y, hd, size=14, bold=True))

    rows = [
        ("нові запити",
         [["ідуть за", "живою таблицею"],
          ["стають", "у чергу"],
          ["стають", "у чергу"],
          ["виходять із черги", "вже за новою"]],
         [GREEN_FILL, WARM_FILL, WARM_FILL, GREEN_FILL]),
        ("запити в польоті",
         [["виконуються"],
          ["каркас їх", "дочікує"],
          ["їх уже", "немає"],
          ["—"]],
         [GREEN_FILL, WARM_FILL, GREY_FILL, GREY_FILL]),
        ("таблиці пристрою",
         [["жива: A"],
          ["жива: A"],
          ["жива: A", "неактивна: B"],
          ["жива: B", "A розібрано"]],
         [BLUE_FILL, BLUE_FILL, BLUE_FILL, GREEN_FILL]),
    ]

    for (name, cells, fills), y in zip(rows, row_y):
        p.append(text(label_x, y + row_h / 2 + 5, name, size=13, bold=True,
                      anchor="start"))
        for x, lines, fill in zip(col_x, cells, fills):
            p.append(fitbox(x, y, col_w, row_h, lines, size=13, pad=12,
                            fill=fill, stroke=LINE, sw=1.4))

    p.append(text(W / 2, 545,
                  "Пара номерів пристрою, файл у /dev, відкриті дескриптори й монтування — незмінні на всіх кроках.",
                  size=13, color=MUTED))
    p.append(text(W / 2, 573,
                  "Змінився зміст пристрою, а не його тотожність.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'table-swap.svg'), W, H, *p,
           title="Заміна таблиці під працюючою файловою системою")


# ── 4. Розкладка буфера ioctl для DM_TABLE_LOAD ────────────────────────────
def fig_ioctl_buffer():
    W, H = 1300, 800
    p = []

    off_x = 130          # колонка зсувів
    cx = 520             # вісь блоків буфера
    nx = 1010            # колонка приміток
    link_x0, link_x1 = 790, 890

    p.append(text(off_x, 78, "зсув, байтів", size=12, bold=True))
    p.append(text(cx, 78, "один суцільний шматок пам'яті", size=14, bold=True))
    p.append(text(nx, 78, "що з чим звірено", size=12, bold=True))

    rows = [
        ("0",
         ["struct dm_ioctl   —   312 байтів",
          "data_size = 424      data_start = 312",
          "target_count = 2     name = \"home\""],
         GREY_FILL,
         ["data_start показує,", "де починається перший spec"]),
        ("312",
         ["dm_target_spec №1   —   40 байтів",
          "sector_start = 0      length = 2097152",
          "target_type = \"linear\"      next = 56"],
         BLUE_FILL,
         ["312 + 56 = 368 —", "початок другого spec"]),
        ("352",
         ["\"/dev/sdb 0\" і нульовий байт   —   11 байтів",
          "доповнення нулями до 16"],
         WARM_FILL,
         ["рядок лежить одразу за spec,", "доповнення вирівнює наступний"]),
        ("368",
         ["dm_target_spec №2",
          "sector_start = 2097152      length = 4194304",
          "target_type = \"linear\"      next = 56"],
         BLUE_FILL,
         ["останній spec —", "далі ядро вже не йде"]),
        ("408",
         ["\"/dev/sdc 2048\" і нульовий байт   —   14 байтів",
          "доповнення нулями до 16"],
         WARM_FILL,
         ["424 байти всього —", "це і є data_size"]),
    ]

    ys = [135, 275, 405, 530, 660]

    for (off, lines, fill, note), cy in zip(rows, ys):
        frag, w, h = textbox(cx, cy, lines, size=13, pad=14, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)
        p.append(text(off_x, cy + 5, off, size=13, bold=True))
        nfrag, nw, nh = textbox(nx, cy, note, size=12, pad=11, fill=GREY_FILL,
                                stroke=MUTED, sw=1.2)
        p.append(nfrag)
        p.append(line(link_x0, cy, link_x1, cy, color=MUTED, sw=1.1, dash="5 4"))

    p.append(text(W / 2, 745,
                  "На DM_TABLE_LOAD поле next рахують від початку СВОГО spec; на DM_TABLE_STATUS ядро",
                  size=13, color=MUTED))
    p.append(text(W / 2, 770,
                  "заповнює його інакше — від початку ПЕРШОГО spec. Одне поле, два способи читати.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'ioctl-buffer.svg'), W, H, *p,
           title="Буфер DM_TABLE_LOAD: заголовок, специфікації відрізків і рядки параметрів")


# ── 5. Стенд досліду: два файли → два loop → один dm → ext4 ────────────────
def fig_lab_stack():
    W, H = 1220, 780
    p = []
    cx, ax = 390, 900
    lx0 = 620

    def note(cy, lines):
        frag, w, h = textbox(ax, cy, lines, size=13, pad=12, fill=GREY_FILL,
                             stroke=MUTED, sw=1.2)
        p.append(frag)
        p.append(line(lx0, cy, ax - w / 2 - 8, cy, color=MUTED, sw=1.1,
                      dash="5 4"))

    def box(cx_, cy, lines, fill, pad=14):
        frag, w, h = textbox(cx_, cy, lines, size=13, pad=pad, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)
        return h

    y_fd, y_fs, y_dm, y_loop, y_file = 90, 215, 360, 545, 685

    h_fd = box(cx, y_fd, ["відкритий дескриптор 9", "на /mnt/payload.bin"],
               GREEN_FILL)
    note(y_fd, ["переживає підміну:", "той самий файл і та сама позиція"])

    h_fs = box(cx, y_fs, ["ext4, змонтована в /mnt"], GREEN_FILL)
    note(y_fs, ["знає свій розмір із суперблока,", "а таблиці не бачить зовсім"])

    h_dm = box(cx, y_dm,
               ["/dev/mapper/lab   —   ціль linear",
                "0        262144   linear   /dev/loop0   0",
                "262144   262144   linear   /dev/loop1   0"], BLUE_FILL)
    note(y_dm, ["розмір = сума довжин рядків:", "524288 секторів = 256 МіБ"])

    ha = box(250, y_loop, ["/dev/loop0", "262144 секторів"], WARM_FILL, pad=13)
    hb = box(500, y_loop, ["/dev/loop1", "262144 секторів"], WARM_FILL, pad=13)
    note(y_loop, ["blockdev --getsz дає число", "в тих самих секторах по 512 Б"])

    hc = box(250, y_file, ["a.img", "128 МіБ, розріджений"], GREY_FILL, pad=13)
    hd = box(500, y_file, ["b.img", "128 МіБ, розріджений"], GREY_FILL, pad=13)
    note(y_file, ["лежать на /var/tmp,", "а не всередині /mnt"])

    p.append(arrow(cx, y_fd + h_fd / 2, cx, y_fs - h_fs / 2))
    p.append(arrow(cx, y_fs + h_fs / 2, cx, y_dm - h_dm / 2))
    p.append(arrow(320, y_dm + h_dm / 2, 250, y_loop - ha / 2))
    p.append(arrow(460, y_dm + h_dm / 2, 500, y_loop - hb / 2))
    p.append(arrow(250, y_loop + ha / 2, 250, y_file - hc / 2))
    p.append(arrow(500, y_loop + hb / 2, 500, y_file - hd / 2))

    render(os.path.join(IMG, 'lab-stack.svg'), W, H, *p,
           title="Стенд досліду: від двох файлів до змонтованої файлової системи")


# ── 6. Довжина таблиці й розмір файлової системи — два різні числа ──────────
def fig_grow_mismatch():
    W, H = 1300, 600
    p = []
    x0, xm, x1 = 300, 730, 1160
    bar_h = 58
    ys = [140, 300, 460]

    titles = [
        ("1. перед підміною", "таблиця з одного рядка"),
        ("2. після resume", "таблиця з двох рядків"),
        ("3. після resize2fs", "таблиця з двох рядків"),
    ]
    for (t1, t2), cy in zip(titles, ys):
        p.append(text(40, cy - 8, t1, size=13, bold=True, anchor="start"))
        p.append(text(40, cy + 14, t2, size=13, color=MUTED, anchor="start"))

    def bar(xa, xb, cy, lines, fill):
        p.append(fitbox(xa, cy - bar_h / 2, xb - xa, bar_h, lines,
                        size=13, pad=10, fill=fill, stroke=LINE, sw=1.5))

    bar(x0, xm, ys[0], ["ext4 на 262144 секторах"], GREEN_FILL)
    p.append(text(xm + 16, ys[0] + 5, "пристрій тут закінчується", size=12,
                  color=MUTED, anchor="start"))

    bar(x0, xm, ys[1], ["ext4 — усе ще 262144 сектори"], GREEN_FILL)
    bar(xm, x1, ys[1], ["сектори є, файлова", "система про них не знає"],
        RED_FILL)

    bar(x0, x1, ys[2], ["ext4 на 524288 секторах"], GREEN_FILL)

    scale_y = ys[2] + bar_h / 2 + 18
    for x, lab in ((x0, "сектор 0"), (xm, "262144"), (x1, "524288")):
        p.append(line(x, ys[2] + bar_h / 2 + 4, x, scale_y - 2, color=MUTED,
                      sw=1.1))
        p.append(text(x, scale_y + 18, lab, size=12, color=MUTED))

    render(os.path.join(IMG, 'grow-mismatch.svg'), W, H, *p,
           title="Пристрій подовшав, файлова система — ні")


if __name__ == '__main__':
    fig_stack_and_table()
    fig_two_fates()
    fig_table_swap()
    fig_ioctl_buffer()
    fig_lab_stack()
    fig_grow_mismatch()
    print("ok")
