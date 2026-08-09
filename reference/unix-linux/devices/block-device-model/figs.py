# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"


# ── 1. Шлях запиту: від bio до пристрою і назад ─────────────────────────────
def fig_bio_path():
    W, H = 1300, 860
    p = []

    cx = 470              # вісь основного стовпця
    nx = 1010             # вісь бічних приміток

    def note(cy, lines):
        frag, w, h = textbox(nx, cy, lines, size=13, pad=13,
                             fill=GREY, stroke=MUTED, sw=1.2)
        p.append(frag)
        return w, h

    # верх: джерело запиту
    y_src = 90
    f, w_src, h_src = textbox(cx, y_src,
                              ["файлова система: треба записати вміст",
                               "двох сусідніх блоків файлу"],
                              size=14, pad=16, fill=GREEN, stroke=LINE)
    p.append(f)

    # два bio
    y_bio = 265
    bio_l_x, bio_r_x = 250, 700
    f1, w1, h1 = textbox(bio_l_x, y_bio,
                         ["bio", "напрямок: запис",
                          "перший сектор: 8000", "довжина: 8 секторів",
                          "сторінки: p1, p2", "завершення: end_io"],
                         size=13, pad=15, fill=BLUE, stroke=LINE)
    f2, w2, h2 = textbox(bio_r_x, y_bio,
                         ["bio", "напрямок: запис",
                          "перший сектор: 8008", "довжина: 8 секторів",
                          "сторінки: p3, p4", "завершення: end_io"],
                         size=13, pad=15, fill=BLUE, stroke=LINE)
    p.append(f1)
    p.append(f2)
    p.append(arrow(cx - 90, y_src + h_src / 2 + 6, bio_l_x, y_bio - h1 / 2 - 6))
    p.append(arrow(cx + 90, y_src + h_src / 2 + 6, bio_r_x, y_bio - h2 / 2 - 6))
    note(y_bio, ["запит живе окремо від того,",
                 "хто його подав: подавач", "не чекає на пристрій"])

    # черга зі злиттям
    y_q = 500
    f, w_q, h_q = textbox(cx, y_q,
                          ["черга блокового рівня",
                           "сектори 8000–8007 і 8008–8015 суміжні →",
                           "обидва bio зшито в ОДИН запит 8000–8015"],
                          size=14, pad=17, fill=WARM, stroke=LINE)
    p.append(f)
    p.append(arrow(bio_l_x, y_bio + h1 / 2 + 6, cx - 120, y_q - h_q / 2 - 6))
    p.append(arrow(bio_r_x, y_bio + h2 / 2 + 6, cx + 120, y_q - h_q / 2 - 6))
    note(y_q, ["одне звертання замість двох —",
               "заради цього черга й потрібна"])

    # драйвер
    y_drv = 670
    f, w_d, h_d = textbox(cx, y_drv,
                          ["драйвер: сторінки запиту → таблиця сегментів DMA"],
                          size=14, pad=16, fill=GREY, stroke=LINE)
    p.append(f)
    p.append(arrow(cx, y_q + h_q / 2 + 6, cx, y_drv - h_d / 2 - 6))
    note(y_drv, ["межі запиту диктує контролер:",
                 "скільки секторів і скільки", "сегментів він здатен узяти"])

    # пристрій
    y_dev = 800
    f, w_v, h_v = textbox(cx, y_dev, ["носій"], size=15, pad=16,
                          fill=GREEN, stroke=LINE, bold=True, min_w=200)
    p.append(f)
    p.append(arrow(cx, y_drv + h_d / 2 + 6, cx, y_dev - h_v / 2 - 6))

    # зворотний шлях завершення — окремою колонкою ліворуч
    bx = 85
    p.append(arrow(bx, y_dev - 10, bx, y_bio + h1 / 2 + 30))
    f, wb, hb = textbox(bx + 130, (y_dev + y_bio) / 2 + 40,
                        ["переривання", "→ відкладена", "частина",
                         "→ end_io", "кожного bio"],
                        size=12, pad=11, fill=RED, stroke=POS, sw=1.2)
    p.append(f)

    render(os.path.join(IMG, 'bio-path.svg'), W, H, *p,
           title="Від наміру файлової системи до секторів і назад")


# ── 2. Логічний сектор проти фізичного блока: ціна зсуву ───────────────────
def fig_alignment():
    W, H = 1220, 620
    p = []

    bw, bh = 210, 62          # фізичний блок
    x0 = 150

    def strip(y, n=4):
        for i in range(n):
            x = x0 + i * bw
            p.append(fitbox(x, y, bw, bh, "фізичний блок 4 КіБ",
                            size=13, fill=GREY, stroke=LINE))

    # ── панель А: вирівняно
    p.append(text(x0, 92, "Запис 4 КіБ, що лягає рівно на фізичний блок",
                  size=15, anchor="start", bold=True))
    y_a = 120
    strip(y_a)
    p.append(rect(x0 + bw, y_a - 34, bw, 26, fill=GREEN, stroke=FIELD, sw=2))
    p.append(text(x0 + bw + bw / 2, y_a - 15, "блок файлової системи",
                  size=12, color=INK))
    p.append(text(x0, y_a + bh + 32,
                  "носій просто пише один блок:  1 запис",
                  size=14, anchor="start", color=FIELD))

    # ── панель Б: зсунуто
    p.append(text(x0, 330, "Той самий запис, зсунутий на 512 байтів",
                  size=15, anchor="start", bold=True))
    y_b = 358
    strip(y_b)
    off = bw // 8            # 512 Б від 4 КіБ
    p.append(rect(x0 + bw + off, y_b - 34, bw, 26, fill=RED, stroke=POS, sw=2))
    p.append(text(x0 + bw + off + bw / 2, y_b - 15, "блок файлової системи",
                  size=12, color=INK))
    # підсвітка двох зачеплених блоків
    p.append(rect(x0 + bw, y_b, bw, bh, fill="none", stroke=POS, sw=2.5))
    p.append(rect(x0 + 2 * bw, y_b, bw, bh, fill="none", stroke=POS, sw=2.5))
    p.append(text(x0, y_b + bh + 32,
                  "зачеплено два блоки: прочитати 2 → змінити → записати 2",
                  size=14, anchor="start", color=POS))
    p.append(text(x0, y_b + bh + 60,
                  "той самий обсяг даних коштує вчетверо більше роботи носія",
                  size=13, anchor="start", color=MUTED))

    render(os.path.join(IMG, 'sector-alignment.svg'), W, H, *p,
           title="Чому початок розділу вирівнюють")


# ── 3. Одна черга проти багатьох ────────────────────────────────────────────
def fig_single_vs_mq():
    W, H = 1380, 720
    p = []

    p.append(line(W / 2, 60, W / 2, H - 30, color=MUTED, sw=1.2, dash="6 6"))

    def cpus(cx, y, span=270):
        xs = [cx - span, cx - span / 3, cx + span / 3, cx + span]
        hh = 0
        for i, x in enumerate(xs):
            f, w, h = textbox(x, y, "ядро %d" % i, size=13, pad=11,
                              fill=BLUE, stroke=LINE)
            p.append(f)
            hh = h
        return xs, hh

    # ── ліворуч: одна черга
    lx = 350
    p.append(text(lx, 75, "Одна черга на пристрій", size=16, bold=True))
    xs, ch = cpus(lx, 150)
    f_lock, wl, hl = textbox(lx, 300, ["спільний замок черги"], size=14,
                             pad=15, fill=RED, stroke=POS, sw=2)
    p.append(f_lock)
    for x in xs:
        p.append(arrow(x, 150 + ch / 2 + 6, lx + (x - lx) * 0.25, 300 - hl / 2 - 6))
    f_q, wq, hq = textbox(lx, 430, ["черга: злиття й упорядкування",
                                    "за номером сектора"],
                          size=13, pad=15, fill=WARM, stroke=LINE)
    p.append(f_q)
    p.append(arrow(lx, 300 + hl / 2 + 6, lx, 430 - hq / 2 - 6))
    f_d, wd, hd = textbox(lx, 560, ["диск, що обертається"], size=14, pad=15,
                          fill=GREY, stroke=LINE)
    p.append(f_d)
    p.append(arrow(lx, 430 + hq / 2 + 6, lx, 560 - hd / 2 - 6))
    p.append(text(lx, 655, "сотні звертань на секунду —", size=13, color=MUTED))
    p.append(text(lx, 678, "замок не заважає", size=13, color=MUTED))

    # ── праворуч: багато черг
    rx = 1030
    p.append(text(rx, 75, "Черга на кожне ядро", size=16, bold=True))
    xs2, ch2 = cpus(rx, 150)
    swq_h = 0
    for x in xs2:
        f, w, h = textbox(x, 285, ["своя", "черга"], size=12, pad=10,
                          fill=GREEN, stroke=FIELD, sw=1.6)
        p.append(f)
        swq_h = h
        p.append(arrow(x, 150 + ch2 / 2 + 6, x, 285 - h / 2 - 6))
    f_h, wh, hh = textbox(rx, 430, ["апаратні черги носія"], size=14, pad=15,
                          fill=WARM, stroke=LINE)
    p.append(f_h)
    for x in xs2:
        p.append(arrow(x, 285 + swq_h / 2 + 6,
                       rx + (x - rx) * 0.35, 430 - hh / 2 - 6))
    f_n, wn, hn = textbox(rx, 560, ["носій без рухомих частин"], size=14,
                          pad=15, fill=GREY, stroke=LINE)
    p.append(f_n)
    p.append(arrow(rx, 430 + hh / 2 + 6, rx, 560 - hn / 2 - 6))
    p.append(text(rx, 655, "мільйон звертань на секунду —", size=13, color=MUTED))
    p.append(text(rx, 678, "спільного замка на шляху подачі немає", size=13, color=MUTED))

    render(os.path.join(IMG, 'single-vs-multiqueue.svg'), W, H, *p,
           title="Що змінилося, коли носій став швидким і паралельним")


# ── 4. Часова смуга: від ліфта до багатьох черг (для hist-вставки) ──────────
def fig_scheduler_timeline():
    W, H = 1180, 1010
    p = []

    ax = 250          # вісь смуги
    bx = 300          # ліва межа рамок подій
    bw = 800          # ширина рамок

    rows = [
        ("січень 2002", ["Єнс Аксбо надсилає в розсилку ядра першу чернетку deadline:",
                         "у кожного запиту свій строк, прострочений іде поза чергою"], BLUE),
        ("червень 2001", ["Сітарам Айєр і Петер Друшель описують на SOSP оманливе неробство",
                          "й передбачливе впорядкування — ідея, ще не код Linux"], GREY),
        ("2003", ["Ендрю Мортон приносить передбачливий упорядкувальник у гілку -mm;",
                  "того ж року Єнс Аксбо пише CFQ"], BLUE),
        ("грудень 2003", ["2.6.0: типовий — передбачливий (anticipatory)"], GREEN),
        ("травень 2004", ["2.6.6: CFQ входить у ядро як один із варіантів"], GREEN),
        ("вересень 2006", ["2.6.18: CFQ стає типовим замість передбачливого"], GREEN),
        ("лютий 2010", ["2.6.33: передбачливий упорядкувальник прибрано зовсім"], RED),
        ("2013", ["SYSTOR: Бʼйорлінг, Аксбо, Нелланс і Бонне описують два яруси черг"], WARM),
        ("січень 2014", ["3.13: blk-mq у ядрі — поки з єдиним драйвером virtio"], WARM),
        ("липень 2017", ["4.12: до mq-deadline додано BFQ (Паоло Валенте)",
                         "і Kyber (Омар Сандовал)"], WARM),
        ("березень 2019", ["5.0: одночерговий рівень і cfq, deadline, noop вилучено"], RED),
    ]

    y = 78
    for label, lines, col in rows:
        h = 34 + (len(lines) - 1) * 22
        cy = y + h / 2
        p.append(text(ax - 32, cy + 5, label, size=14, anchor="end", bold=True))
        p.append(circle(ax, cy, 7, fill="#ffffff", stroke=LINE, sw=2))
        p.append(fitbox(bx, y, bw, h, lines, size=14, fill=col, stroke=LINE))
        y += h + 32

    p.insert(0, line(ax, 66, ax, y - 26, color=LINE, sw=2))

    render(os.path.join(IMG, 'scheduler-timeline.svg'), W, H, *p,
           title="Впорядкування запитів у Linux: що коли сталося")


# ── 5. Шов зсуву оплачує кожен запит окремо ─────────────────────────────────
def fig_merge_seams():
    W, H = 1260, 620
    p = []

    x0 = 60
    bw, bh = 74, 56
    off = bw // 8              # 512 Б у масштабі блока 4 КіБ
    gw = 240                   # ширина проміжку з «…»

    def blocks(y, n, xs_start):
        xs = []
        for i in range(n):
            x = xs_start + i * bw
            p.append(rect(x, y, bw, bh, fill=GREY, stroke=LINE, sw=1.2))
            xs.append(x)
        return xs

    # ── ряд А: злитий запит
    p.append(text(x0, 62, "Злитий запит 1280 КіБ, зсунутий на 512 байтів",
                  size=16, anchor="start", bold=True))
    yA = 148
    left = blocks(yA, 6, x0)
    gxA = x0 + 6 * bw
    p.append(rect(gxA, yA, gw, bh, fill=BG, stroke=MUTED, sw=1.2))
    p.append(text(gxA + gw / 2, yA + bh / 2 + 5, "… ще 309 цілих блоків …",
                  size=13, color=MUTED))
    right = blocks(yA, 6, gxA + gw)
    endA = right[-1] + bw

    p.append(rect(x0 + off, yA - 44, endA - x0, 28, fill=BLUE, stroke=NEG, sw=2))
    p.append(text((x0 + endA) / 2, yA - 24, "один запит: 320 блоків даних",
                  size=13, color=INK))

    p.append(rect(left[0], yA, bw, bh, fill=RED, stroke=POS, sw=2.5))
    p.append(rect(right[-1], yA, bw, bh, fill=RED, stroke=POS, sw=2.5))
    p.append(text(x0, yA + bh + 40,
                  "часткові лише два крайні блоки: 2 із 321 — менше відсотка зайвої роботи",
                  size=14, anchor="start", color=FIELD))

    # ── ряд Б: незлитий запит
    p.append(text(x0, 400, "Незлитий запит 4 КіБ, зсунутий на 512 байтів",
                  size=16, anchor="start", bold=True))
    yB = 486
    two = blocks(yB, 2, x0)
    endB = two[-1] + bw

    p.append(rect(x0 + off, yB - 44, bw, 28, fill=BLUE, stroke=NEG, sw=2))
    p.append(text(x0 + off + bw / 2, yB - 24, "4 КіБ", size=13, color=INK))

    p.append(rect(two[0], yB, bw, bh, fill=RED, stroke=POS, sw=2.5))
    p.append(rect(two[1], yB, bw, bh, fill=RED, stroke=POS, sw=2.5))
    p.append(text(endB + 40, yB + bh / 2 + 5,
                  "часткові обидва: на 4 КіБ даних — 8 КіБ читання й 8 КіБ запису",
                  size=14, anchor="start", color=POS))

    render(os.path.join(IMG, 'merge-seams.svg'), W, H, *p,
           title="Зсув оплачується на кінцях запиту, а не всередині")


if __name__ == '__main__':
    fig_bio_path()
    fig_alignment()
    fig_single_vs_mq()
    fig_scheduler_timeline()
    fig_merge_seams()
    print("ok")
