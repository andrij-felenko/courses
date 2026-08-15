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


# ── 1. Добуток проти суми: вузький пояс інтерфейсу ───────────────────────────
def fig_narrow_waist():
    W, H = 880, 520
    p = []

    progs = ["wc", "cat", "grep", "sort"]
    srcs = ["диск", "порт", "канал", "/proc"]
    bw, bh = 74, 40
    ptop, sbot = 110, 380          # низ програм / верх джерел

    def column_x(px, i, n=4, span=330):
        step = (span - bw) / (n - 1)
        return px + i * step

    # ── ЛІВОРУЧ: кожна пара має власний код ──
    lx = 40
    p.append(text(lx + 165, 62, "без спільного інтерфейсу", size=15, bold=True, color=POS))
    for i, s in enumerate(progs):
        x = column_x(lx, i)
        p.append(rect(x, ptop - bh, bw, bh, fill=RED_FILL, stroke=POS, sw=1.6, rx=8))
        p.append(text(x + bw / 2, ptop - bh / 2 + 5, s, size=13, bold=True))
    for i, s in enumerate(srcs):
        x = column_x(lx, i)
        p.append(rect(x, sbot, bw, bh, fill=FILL, stroke=LINE, sw=1.6, rx=8))
        p.append(text(x + bw / 2, sbot + bh / 2 + 5, s, size=13))
    for i in range(4):
        for j in range(4):
            p.append(line(column_x(lx, i) + bw / 2, ptop,
                          column_x(lx, j) + bw / 2, sbot, color=POS, sw=1.0))
    p.append(text(lx + 165, 455, "4 × 4 = 16 шматків коду", size=14, bold=True, color=POS))
    p.append(text(lx + 165, 480, "новий пристрій — правити всі програми", size=12.5, color=MUTED))

    # ── ПРАВОРУЧ: усе проходить крізь пояс ──
    rx0 = 510
    p.append(text(rx0 + 165, 62, "зі спільним інтерфейсом", size=15, bold=True, color=FIELD))
    for i, s in enumerate(progs):
        x = column_x(rx0, i)
        p.append(rect(x, ptop - bh, bw, bh, fill=GREEN_FILL, stroke=FIELD, sw=1.6, rx=8))
        p.append(text(x + bw / 2, ptop - bh / 2 + 5, s, size=13, bold=True))
    for i, s in enumerate(srcs):
        x = column_x(rx0, i)
        p.append(rect(x, sbot, bw, bh, fill=FILL, stroke=LINE, sw=1.6, rx=8))
        p.append(text(x + bw / 2, sbot + bh / 2 + 5, s, size=13))

    band_y, band_h = 222, 56
    p.append(fitbox(rx0 - 10, band_y, 350, band_h,
                    ["open · read · write · close · lseek"],
                    size=14, bold=True, fill=WARM_FILL, stroke=WARM, sw=2, rx=10))
    for i in range(4):
        p.append(line(column_x(rx0, i) + bw / 2, ptop,
                      column_x(rx0, i) + bw / 2, band_y, color=FIELD, sw=1.6))
        p.append(line(column_x(rx0, i) + bw / 2, band_y + band_h,
                      column_x(rx0, i) + bw / 2, sbot, color=FIELD, sw=1.6))
    p.append(text(rx0 + 165, 455, "4 + 4 = 8 зв'язків", size=14, bold=True, color=FIELD))
    p.append(text(rx0 + 165, 480, "новий пристрій — лише ще одна реалізація пояса",
                  size=12.5, color=MUTED))

    render(os.path.join(IMG, 'narrow-waist.svg'), W, H, *p)


# ── 2. Шлях виклику read: число → таблиця → f_op → реалізація ────────────────
def fig_dispatch():
    W, H = 1080, 430
    p = []

    # програма
    box, bw, bh = textbox(103, 229, "програма\nread(3, buf, 4096)", size=13,
                          fill=BLUE_FILL, stroke=NEG, sw=1.8, pad=12)
    p.append(box)
    p.append(text(103, 78, "виклик", size=12, color=MUTED))

    # таблиця дескрипторів
    tx, tw, rh = 210, 130, 34
    p.append(text(tx + tw / 2, 78, "таблиця дескрипторів", size=12, color=MUTED))
    for i in range(4):
        y = 110 + i * rh
        hot = (i == 3)
        p.append(rect(tx, y, tw, rh, fill=GREEN_FILL if hot else FILL,
                      stroke=FIELD if hot else LINE, sw=1.8 if hot else 1.2, rx=4))
        p.append(text(tx + tw / 2, y + rh / 2 + 5, "fd %d" % i,
                      size=13, bold=hot, color=INK))
    p.append(arrow(103 + bw / 2 + 4, 229, tx - 6, 229, color=NEG))

    # опис відкритого файлу
    fx, fw = 390, 210
    p.append(text(fx + fw / 2, 78, "опис відкритого файлу", size=12, color=MUTED))
    p.append(fitbox(fx, 140, fw, 140,
                    ["struct file", "позиція: 8192", "прапорці: O_RDONLY", "f_op →"],
                    size=13, fill=FILL, stroke=LINE, sw=1.8, rx=8))
    p.append(arrow(tx + tw + 6, 229, fx - 6, 215))

    # таблиця операцій
    ox, ow, orh = 660, 170, 32
    p.append(text(ox + ow / 2, 78, "таблиця операцій", size=12, color=MUTED))
    ops = ["read", "write", "llseek", "poll", "ioctl"]
    for i, o in enumerate(ops):
        y = 110 + i * orh
        hot = (i == 0)
        p.append(rect(ox, y, ow, orh, fill=GREEN_FILL if hot else FILL,
                      stroke=FIELD if hot else LINE, sw=1.8 if hot else 1.2, rx=4))
        p.append(text(ox + ow / 2, y + orh / 2 + 5, o, size=13, bold=hot))
    p.append(arrow(fx + fw + 6, 250, ox - 6, 200))

    # три реалізації
    impls = [(97, "файлова система ext4"),
             (212, "драйвер\nпослідовного порту"),
             (327, "канал у пам'яті ядра")]
    ix, iw, ih = 890, 170, 54
    for cy, label in impls:
        lines = label.split("\n")
        p.append(fitbox(ix, cy - ih / 2, iw, ih, lines, size=12,
                        fill=WARM_FILL, stroke=WARM, sw=1.6, rx=8))
        p.append(arrow(ox + ow + 6, 126, ix - 6, cy, color=WARM))

    p.append(text(540, 400,
                  "вибір реалізації стався один раз — під час open; далі це перехід за вказівником",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'dispatch.svg'), W, H, *p)


# ── 3. Перенаправлення й конвеєр — перестановка вказівників ──────────────────
def fig_redirect():
    W, H = 1050, 375
    p = []

    panels = [
        ("запуск у терміналі", "термінал", "термінал",
         ["нічого не переставляли"], LINE, FILL),
        ("перенаправлення у файл", "термінал", "out.txt на диску",
         ["оболонка зробила dup2(fd, 1)", "перед запуском програми"], FIELD, GREEN_FILL),
        ("конвеєр", "термінал", "канал у пам'яті",
         ["другий кінець каналу стане", "нульовим дескриптором сусіда"], NEG, BLUE_FILL),
    ]

    for k, (title, t0, t1, note, hue, fillc) in enumerate(panels):
        px = 30 + k * 335
        p.append(text(px + 155, 62, title, size=14, bold=True, color=hue))
        p.append(fitbox(px, 88, 310, 46, ["програма: читає з fd 0, пише в fd 1"],
                        size=12.5, fill="#f0f0f2", stroke=LINE, sw=1.6, rx=8))

        for j, (lbl, tgt) in enumerate([("fd 0", t0), ("fd 1", t1)]):
            y = 165 + j * 62
            hot = (j == 1)
            p.append(rect(px, y, 88, 42, fill=fillc if hot else FILL,
                          stroke=hue if hot else LINE, sw=1.8 if hot else 1.3, rx=6))
            p.append(text(px + 44, y + 27, lbl, size=13, bold=hot))
            p.append(arrow(px + 96, y + 21, px + 122, y + 21,
                           color=hue if hot else LINE))
            p.append(fitbox(px + 128, y, 182, 42, [tgt], size=12,
                            fill=fillc if hot else FILL,
                            stroke=hue if hot else LINE, sw=1.6 if hot else 1.3, rx=6))

        p.append(mtext(px + 155, 315, note, size=12, color=MUTED))

    render(os.path.join(IMG, 'redirect.svg'), W, H, *p)


# ── 4. Що справді стало файлом, що лише дескриптором, а що ніяк ──────────────
def fig_what_is_a_file():
    W, H = 1030, 490
    p = []

    cols = [
        (30, FIELD, GREEN_FILL, ["ім'я в дереві", "+ спільні дієслова"],
         ["звичайний файл", "каталог", "файл пристрою в /dev",
          "іменований канал FIFO", "файли в /proc і /sys"]),
        (360, NEG, BLUE_FILL, ["дескриптор є,", "імені в дереві немає"],
         ["сокет", "безіменний канал", "epoll", "eventfd, timerfd, signalfd",
          "memfd", "pidfd", "кільце io_uring"]),
        (690, POS, RED_FILL, ["ні імені,", "ні дескриптора"],
         ["сигнал сам по собі", "процес за номером PID", "системний час",
          "розподіл пам'яті через brk", "змінні оточення"]),
    ]

    for cx, hue, fillc, head, items in cols:
        p.append(fitbox(cx, 50, 310, 62, head, size=13.5, bold=True,
                        fill=fillc, stroke=hue, sw=2, rx=10))
        for i, it in enumerate(items):
            y = 140 + i * 44
            p.append(fitbox(cx + 14, y, 282, 34, [it], size=12,
                            fill=FILL, stroke=hue, sw=1.3, rx=6))

    p.append(text(515, 465,
                  "усе нове за останні двадцять років осідає в середньому стовпці",
                  size=13, bold=True, color=MUTED))

    render(os.path.join(IMG, 'what-is-a-file.svg'), W, H, *p)


# ── 5. Хроніка: що потрапило в дерево імен, а що пішло повз ─────────────────
def fig_namespace_timeline():
    W, H = 940, 800
    p = []

    p.append(text(W / 2, 34, "Чи дістала річ ім'я в спільному дереві", size=17, bold=True))

    IN_TREE = "#1e7a46"      # потрапило в дерево
    PAST = POS               # пішло повз дерево
    DONE = NEG               # ідею доведено до кінця

    rows = [
        ("1969–70", "PDP-7: пристрій дістає ім'я в каталозі, як звичайний файл", IN_TREE, GREEN_FILL),
        ("1974", "CACM: спеціальні файли — «найнезвичніша риса»; усі вони в /dev", IN_TREE, GREEN_FILL),
        ("1979", "сьоме видання: ioctl замінює stty/gtty — аварійний вихід із пояса", PAST, RED_FILL),
        ("1983", "4.2BSD: сокети — власні дієслова, імені в дереві немає", PAST, RED_FILL),
        ("1984", "Кілліан: /proc — сам процес нарешті стає файлом", IN_TREE, GREEN_FILL),
        ("1984", "Рітчі: потоки замість сокетів (8-ме видання, 1985)", IN_TREE, GREEN_FILL),
        ("1986→", "SVR3 бере STREAMS, та в 1990-х перемагають сокети", PAST, RED_FILL),
        ("1989–92", "Plan 9: протокол 9P, керувальні файли, мережа як /net", DONE, BLUE_FILL),
        ("1992", "Linux: /proc з версії 0.97.3, далі — /sys і решта", IN_TREE, GREEN_FILL),
    ]

    x_axis = 150
    y0, step = 92, 68
    box_x, box_w, box_h = 190, 700, 46

    p.append(line(x_axis, y0 - 18, x_axis, y0 + (len(rows) - 1) * step + 30,
                  color=MUTED, sw=2, dash="6 5"))

    for i, (year, txt, hue, fillc) in enumerate(rows):
        cy = y0 + i * step + box_h / 2
        p.append(text(x_axis - 22, cy + 5, year, size=13.5, bold=True,
                      color=MUTED, anchor="end"))
        p.append(circle(x_axis, cy, 7, fill=fillc, stroke=hue, sw=2.2))
        p.append(line(x_axis + 8, cy, box_x - 4, cy, color=hue, sw=1.4))
        p.append(fitbox(box_x, y0 + i * step, box_w, box_h, txt, size=13.5,
                        fill=fillc, stroke=hue, sw=1.8, rx=8))

    ly = y0 + len(rows) * step + 12
    legend = [("потрапило в дерево імен", IN_TREE, GREEN_FILL),
              ("пішло повз дерево", PAST, RED_FILL),
              ("ідею доведено до кінця", DONE, BLUE_FILL)]
    lx = 190
    for label, hue, fillc in legend:
        p.append(circle(lx, ly, 7, fill=fillc, stroke=hue, sw=2.2))
        p.append(text(lx + 16, ly + 5, label, size=13, color=MUTED, anchor="start"))
        lx += text_width(label, 13) + 66

    render(os.path.join(IMG, 'namespace-timeline.svg'), W, H, *p)


# ── 6. Анатомія одного оберту петлі переливача (вставка proj) ────────────────
def fig_copy_loop():
    W, H = 1120, 580
    p = []

    def panel(x0, title, call, rows, note=None):
        out = []
        out.append(text(x0 + 250, 42, title, size=15, bold=True))
        out.append(fitbox(x0 + 95, 66, 310, 46, [call], size=14, bold=True,
                          fill=FILL, stroke=LINE, sw=1.8, rx=8))
        out.append(text(x0 + 250, 134, "що повернулось", size=12.5, color=MUTED))
        for i, (cond, act, hue, fillc) in enumerate(rows):
            y = 150 + i * 68
            out.append(fitbox(x0 + 10, y, 170, 52, [cond], size=13, bold=True,
                              fill=fillc, stroke=hue, sw=1.7, rx=7))
            out.append(arrow(x0 + 186, y + 26, x0 + 214, y + 26, color=hue))
            out.append(fitbox(x0 + 220, y, 270, 52, [act], size=13,
                              fill=FILL, stroke=hue, sw=1.5, rx=7))
        if note:
            out.append(mtext(x0 + 250, 150 + len(rows) * 68 + 26, note,
                             size=12.5, color=MUTED))
        return out

    p += panel(30, "зовнішня петля: read", "n = read(in, buf, N)", [
        ("n > 0", "write_all(out, buf, n) → знову", FIELD, GREEN_FILL),
        ("n == 0", "джерело скінчилося → вихід", NEG, BLUE_FILL),
        ("n < 0, EINTR", "нічого не сталося → знову", WARM, WARM_FILL),
        ("n < 0, EAGAIN", "даних поки нема → чекати", WARM, WARM_FILL),
        ("n < 0, решта", "справжня помилка → перервати", POS, RED_FILL),
    ])

    p += panel(590, "внутрішня петля: write_all", "m = write(out, p, left)", [
        ("m > 0", "p += m; left −= m; знову", FIELD, GREEN_FILL),
        ("m < 0, EINTR", "той самий шматок ще раз", WARM, WARM_FILL),
        ("m < 0, EAGAIN", "чекати готовності запису", WARM, WARM_FILL),
        ("m < 0, EPIPE", "читач зник — перервати", POS, RED_FILL),
    ], note=["поки left > 0 — повторюємо той самий буфер;",
             "left == 0 — шматок дописано, вертаємось до read"])

    p.append(line(560, 30, 560, 500, color=MUTED, sw=1.2, dash="5 5"))
    p.append(text(560, 548,
                  "жоден із цих випадків не питає, що стоїть за дескриптором",
                  size=13, bold=True, color=MUTED))

    render(os.path.join(IMG, 'copy-loop.svg'), W, H, *p)


# ── 7. Короткий запис: де наївний код мовчки губить дані ─────────────────────
def fig_short_write():
    W, H = 1000, 420
    p = []
    X0, BARW = 185, 760          # 760 px = 65536 байтів
    px = BARW / 65536.0

    p.append(text(X0 + BARW / 2, 55, "доля буфера після одного read",
                  size=13.5, bold=True))

    def label(y, lines):
        p.append(mtext(163, y, lines, size=12.5, color=MUTED, anchor="end"))

    # 1. прочитано
    y1 = 95
    p.append(rect(X0, y1, BARW, 46, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=6))
    p.append(text(X0 + BARW / 2, y1 + 29, "65536 байтів у буфері", size=13, bold=True))
    label(y1 + 29, ["read повернув"])

    # 2. наївно: один write
    y2 = 190
    w_ok = 8192 * px
    p.append(rect(X0, y2, w_ok, 46, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=6))
    p.append(text(X0 + w_ok / 2, y2 + 29, "8192", size=11.5))
    p.append(rect(X0 + w_ok, y2, BARW - w_ok, 46, fill=RED_FILL, stroke=POS, sw=1.8, rx=6))
    p.append(text(X0 + w_ok + (BARW - w_ok) / 2, y2 + 29,
                  "57344 байтів зникли: write узяв менше, а код цього не глянув",
                  size=12, color=POS))
    label(y2 + 22, ["наївно:", "один write"])

    # 3. цикл write_all
    y3 = 285
    xc = X0
    for nb in (8192, 16384, 40960):
        w = nb * px
        p.append(rect(xc, y3, w, 46, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=6))
        p.append(text(xc + w / 2, y3 + 29, str(nb), size=11.5))
        xc += w
    label(y3 + 22, ["цикл", "write_all"])

    p.append(text(500, 372,
                  "read має право дати менше, ніж просили — це не шкодить; "
                  "write має право взяти менше, ніж дали — і це губить хвіст",
                  size=12.5, color=MUTED))

    render(os.path.join(IMG, 'short-write.svg'), W, H, *p)


# ── 8. Скільки разів байти перетинають межу ядра ─────────────────────────────
def fig_copy_paths():
    W, H = 1200, 470
    p = []

    p.append(rect(365, 72, 170, 328, fill="#faf7f0", stroke=WARM, sw=1.4, rx=10))
    p.append(text(450, 57, "простір користувача", size=12.5, bold=True, color=WARM))
    p.append(text(970, 90, "чим за це заплачено", size=13, bold=True, color=MUTED))

    rows = [
        (140, "read + write", ["буфер", "програми"], ("read", "write"), NEG, BLUE_FILL,
         ["працює на будь-якій парі дескрипторів,",
          "та байти двічі йдуть через межу"]),
        (250, "splice", ["канал: лише", "посилання на сторінки"], ("splice", "splice"),
         FIELD, GREEN_FILL,
         ["один із двох дескрипторів",
          "мусить бути каналом"]),
        (360, "sendfile", None, None, FIELD, GREEN_FILL,
         ["in_fd має підтримувати mmap:",
          "ні сокет, ні канал не годяться"]),
    ]

    for cy, name, mbox, arrows, hue, fillc, price in rows:
        top = cy - 27
        p.append(fitbox(30, top, 150, 54, [name], size=13, bold=True,
                        fill=fillc, stroke=hue, sw=1.8, rx=8))
        p.append(fitbox(200, top, 130, 54, ["кеш сторінок", "у ядрі"], size=11.5,
                        fill=FILL, stroke=LINE, sw=1.5, rx=8))
        p.append(fitbox(570, top, 140, 54, ["буфер сокета", "в ядрі"], size=11.5,
                        fill=FILL, stroke=LINE, sw=1.5, rx=8))
        if mbox:
            p.append(fitbox(385, top, 130, 54, mbox, size=11.5,
                            fill=fillc, stroke=hue, sw=1.6, rx=8))
            p.append(arrow(332, cy, 383, cy, color=hue))
            p.append(arrow(517, cy, 568, cy, color=hue))
            p.append(text(357, cy - 38, arrows[0], size=11.5, color=hue))
            p.append(text(542, cy - 38, arrows[1], size=11.5, color=hue))
        else:
            p.append(arrow(332, cy, 568, cy, color=hue))
            p.append(text(450, cy - 18, "sendfile", size=12, bold=True, color=hue))
            p.append(text(450, cy + 28, "дані не виходять із ядра",
                          size=11.5, color=MUTED))
        p.append(fitbox(760, top, 420, 54, price, size=12,
                        fill=FILL, stroke=MUTED, sw=1.3, rx=8))

    p.append(text(600, 442,
                  "швидше — означає вужче: кожен крок економії відбирає в петлі "
                  "частину її всеїдності",
                  size=13, bold=True, color=MUTED))

    render(os.path.join(IMG, 'copy-paths.svg'), W, H, *p)


if __name__ == '__main__':
    fig_narrow_waist()
    fig_dispatch()
    fig_redirect()
    fig_what_is_a_file()
    fig_namespace_timeline()
    fig_copy_loop()
    fig_short_write()
    fig_copy_paths()
    print("ok:", sorted(os.listdir(IMG)))
