# -*- coding: utf-8 -*-
"""Фігури до теми «DMA і відображення буферів у ядрі»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_four_views():
    """Одні й ті самі байти під трьома різними адресами."""
    W, H = 1000, 480
    f = []

    f.append(text(W / 2, 32, "Той самий буфер під трьома адресами", size=17, bold=True))

    # три погляди зверху
    vw, vh = 260, 74
    xs = [40, 370, 700]
    heads = ["Процес", "Ядро", "Пристрій"]
    bodies = ["віртуальна адреса\n0x7f2c00001000",
              "віртуальна адреса\n0xffff8880a1b02000",
              "адреса шини (dma_addr_t)\n0x00000000fffb1000"]
    for i, x in enumerate(xs):
        f.append(fitbox(x, 66, vw, 30, heads[i], size=15, bold=True))
        f.append(fitbox(x, 100, vw, vh, bodies[i], size=13))

    # IOMMU у шляху пристрою
    f.append(fitbox(700, 216, vw, 46, "IOMMU: власна таблиця сторінок",
                    size=13, fill="#eaf0fd", stroke=NEG, color=NEG))

    # спільний ряд фізичних сторінок
    py, ph = 316, 66
    f.append(text(W / 2, py - 16, "Фізичні сторінки оперативної пам'яті", size=14, bold=True))
    px = [110, 300, 490, 680]
    for i, x in enumerate(px):
        f.append(fitbox(x, py, 160, ph, "сторінка %d\n4 КіБ" % (i + 1), size=13))

    # стрілки від поглядів до сторінок
    f.append(arrow(170, 174, 180, py))
    f.append(text(60, 250, "MMU процесора", size=12, color=MUTED, anchor="start"))
    f.append(arrow(500, 174, 470, py))
    f.append(text(400, 250, "пряме відображення ядра", size=12, color=MUTED, anchor="start"))
    f.append(arrow(830, 174, 830, 216, color=NEG))
    f.append(arrow(830, 262, 790, py, color=NEG))

    f.append(text(W / 2, 428,
                  "жодна з трьох адрес не годиться замість іншої — переклад між ними робить окреме залізо",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'four-views.svg'), W, H, *f)


def fig_ownership():
    """Відображення як передача володіння буфером між процесором і пристроєм."""
    W, H = 1020, 440
    f = []

    f.append(text(W / 2, 30, "Хто володіє буфером у кожен момент", size=17, bold=True))

    # вісь
    f.append(line(50, 250, 970, 250, color=MUTED))

    xs = [60, 260, 460, 660, 860]
    calls = ["dma_map_single()",
             "sync_for_cpu()",
             "sync_for_device()",
             "dma_unmap_single()",
             "буфер вільний"]
    for i, x in enumerate(xs):
        f.append(fitbox(x - 5, 62, 170, 52, calls[i], size=12,
                        fill="#ffffff", stroke=MUTED))
        f.append(line(x + 80, 114, x + 80, 250, color=MUTED, dash="4 4"))

    # смуги володіння
    owner = [
        (145, 355, "пристрій\nпише в пам'ять", POS, "#fdecea"),
        (355, 555, "процесор\nчитає й править", NEG, "#eaf0fd"),
        (555, 745, "пристрій\nчитає далі", POS, "#fdecea"),
        (745, 945, "процесор\nволодіє повністю", NEG, "#eaf0fd"),
    ]
    for x1, x2, label, col, fillc in owner:
        f.append(fitbox(x1, 156, x2 - x1 - 12, 66, label, size=13,
                        fill=fillc, stroke=col, color=col))

    f.append(fitbox(120, 300, 380, 82,
                    "поки володіє пристрій:\nчитати або писати цей буфер\nпроцесору заборонено",
                    size=13, fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(560, 300, 380, 82,
                    "поки володіє процесор:\nпристрій уже не бачить\nсвіжих байтів",
                    size=13, fill="#eaf0fd", stroke=NEG, color=NEG))

    f.append(text(W / 2, 420, "виклики DMA API не рухають байти — вони переставляють право доступу",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'ownership.svg'), W, H, *f)


def fig_scatter_gather():
    """Суцільний буфер програми — розсипані сторінки — що бачить пристрій."""
    W, H = 1020, 520
    f = []

    f.append(text(W / 2, 30, "Суцільний для програми, розсипаний у пам'яті", size=17, bold=True))

    # 1. буфер програми
    f.append(text(60, 76, "Буфер програми: 512 КіБ підряд", size=14, bold=True, anchor="start"))
    f.append(rect(60, 88, 900, 44))
    f.append(text(510, 116, "один діапазон віртуальних адрес", size=13))

    # 2. фізичні сторінки
    f.append(text(60, 186, "Фізична пам'ять: сторінки де завгодно", size=14, bold=True, anchor="start"))
    pgs = [(60, "0x1a2000"), (260, "0x77f000"), (460, "0x0c1000"), (660, "0x9e4000"), (860, "…")]
    for x, lab in pgs:
        f.append(fitbox(x, 200, 140, 52, lab, size=13))

    # 3. список сегментів
    f.append(text(60, 306, "Список сегментів (scatterlist): адреса + довжина", size=14, bold=True, anchor="start"))
    for x, lab in pgs[:4]:
        f.append(fitbox(x, 320, 140, 50, "сегмент", size=12, fill="#ffffff"))
        f.append(arrow(x + 70, 252, x + 70, 320, color=MUTED))

    # 4. що бачить пристрій
    f.append(text(60, 424, "Що дістає пристрій", size=14, bold=True, anchor="start"))
    f.append(fitbox(60, 438, 420, 58,
                    "без IOMMU: 4 окремі адреси —\nпристрій має вміти збирати сам",
                    size=13, fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(540, 438, 420, 58,
                    "з IOMMU: один суцільний діапазон —\nсегменти склеєно в таблиці",
                    size=13, fill="#eaf0fd", stroke=NEG, color=NEG))
    f.append(arrow(200, 370, 200, 438, color=POS))
    f.append(arrow(700, 370, 700, 438, color=NEG))

    render(os.path.join(IMG, 'scatter-gather.svg'), W, H, *f)


def fig_irreversible():
    """Чому арифметика virt_to_bus не могла вціліти: один виклик — три різні відповіді."""
    W, H = 1060, 560
    f = []

    f.append(text(W / 2, 34, "Одна й та сама адреса — три різні відповіді платформи",
                  size=17, bold=True))

    # виток: старий шлях
    f.append(fitbox(60, 66, 400, 74,
                    "Було: bus = virt_to_bus(buf)\nчиста арифметика, оборотна в обидва боки",
                    size=13, fill="#f4f6f8", stroke=MUTED, color=MUTED))

    f.append(fitbox(60, 176, 400, 62,
                    "Стало: da = dma_map_single(dev, buf, len, dir)",
                    size=13, bold=True))

    # три гілки
    ys = [284, 384, 484]
    labels = [
        "пряме відображення\nадреса шини = фізична + стала різниця",
        "через IOMMU\nадресу видано з таблиці перекладу",
        "через swiotlb\nадреса вказує на ІНШИЙ буфер, не на buf",
    ]
    cols = [FIELD, NEG, POS]
    fills = ["#eafaf0", "#eaf0fd", "#fdecea"]
    for y, lab, c, fl in zip(ys, labels, cols, fills):
        f.append(fitbox(200, y - 32, 400, 64, lab, size=13,
                        fill=fl, stroke=c, color=c))
        f.append(arrow(260, 238, 260, y - 32, color=c))

    # права колонка: наслідок
    f.append(fitbox(660, 176, 340, 62, "Що дістав драйвер: dma_addr_t",
                    size=13, bold=True))
    for y, c in zip(ys, cols):
        f.append(arrow(600, y, 660, y, color=c))
    f.append(fitbox(660, 252, 340, 96,
                    "Число залежить від платформи,\nвід наявності IOMMU\nі від того, чи спрацював обхід",
                    size=13, fill="#f4f6f8", stroke=LINE))
    f.append(fitbox(660, 384, 340, 96,
                    "Зворотної функції bus_to_virt\nнемає й бути не може:\nз числа не видно, звідки воно",
                    size=13, fill="#fdecea", stroke=POS, color=POS, bold=True))
    f.append(fitbox(660, 500, 340, 46,
                    "Тому dma_addr_t зберігає драйвер",
                    size=13, fill="#eafaf0", stroke=FIELD, color=FIELD))

    render(os.path.join(IMG, 'irreversible.svg'), W, H, *f)


def fig_transfer_path():
    """Повний шлях однієї передачі: вісім кроків і три місця, де важить порядок."""
    W, H = 1120, 760
    f = []

    f.append(text(W / 2, 34, "Шлях однієї передачі: що робить драйвер і що це означає для заліза",
                  size=17, bold=True))

    f.append(text(275, 74, "Драйвер", size=14, bold=True))
    f.append(text(830, 74, "Наслідок для заліза", size=14, bold=True))

    steps = [
        ("1.  dma_map_sgtable(sgt, dir)",
         "кеш скинуто в пам'ять,\nбуфер тепер належить пристроєві", NEG, "#eaf0fd"),
        ("2.  обхід по sgt->nents",
         "після злиття в IOMMU сегментів\nменше, ніж було в списку", None, None),
        ("3.  d->addr, d->len через cpu_to_le",
         "числа лягають у порядку байтів\nпристрою, не процесора", None, None),
        ("4.  dma_wmb()",
         "адреса й довжина мусять дійти\nДО прапорця власника", POS, "#fdecea"),
        ("5.  d->flags = OWN",
         "з цієї миті дескриптор читає\nпристрій, а не драйвер", None, None),
        ("6.  writel(tail) — дзвінок у регістр",
         "writel сам чекає попередніх\nзаписів; writel_relaxed — ні", POS, "#fdecea"),
        ("7.  переривання: OWN знято, далі dma_rmb()",
         "прапорець прочитано — лише тепер\nрешта полів справді наша", POS, "#fdecea"),
        ("8.  dma_unmap_sgtable(sgt, той самий dir)",
         "буфер повернувся процесорові,\nчитати його можна аж тепер", NEG, "#eaf0fd"),
    ]

    lx, lw = 50, 450
    rx, rw = 620, 450
    y0, bh, gap = 96, 62, 20

    for i, (left, right, col, fillc) in enumerate(steps):
        y = y0 + i * (bh + gap)
        f.append(fitbox(lx, y, lw, bh, left, size=13, bold=(col == POS)))
        f.append(fitbox(rx, y, rw, bh, right, size=13,
                        fill=fillc or "#ffffff",
                        stroke=col or MUTED,
                        color=col or MUTED))
        f.append(arrow(lx + lw + 10, y + bh / 2, rx - 10, y + bh / 2,
                       color=col or MUTED))
        if i + 1 < len(steps):
            f.append(arrow(lx + 40, y + bh, lx + 40, y + bh + gap, color=MUTED))

    render(os.path.join(IMG, 'transfer-path.svg'), W, H, *f)


if __name__ == '__main__':
    fig_four_views()
    fig_ownership()
    fig_scatter_gather()
    fig_irreversible()
    fig_transfer_path()
    print("ok")
