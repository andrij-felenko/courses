# -*- coding: utf-8 -*-
"""Фігури до теми «Віртуальний адресний простір процесу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_same_address():
    """Та сама віртуальна адреса → різні кадри; спільний кадр libc у двох просторах."""
    W, H = 980, 470
    f = []

    # заголовки колонок
    f.append(text(135, 68, "Простір процесу A", size=15, bold=True))
    f.append(text(490, 68, "Фізична пам'ять", size=15, bold=True))
    f.append(text(845, 68, "Простір процесу B", size=15, bold=True))

    bw, bh = 210, 56
    ax, bx, mx = 30, 740, 385

    # процес A
    f.append(fitbox(ax, 90, bw, bh, "0x7f9a12c00000\nкод libc", size=13))
    f.append(fitbox(ax, 180, bw, bh, "0x404018\nдані програми", size=13))
    # процес B
    f.append(fitbox(bx, 90, bw, bh, "0x7fc3ee400000\nкод libc", size=13))
    f.append(fitbox(bx, 180, bw, bh, "0x404018\nдані програми", size=13))

    # фізичні кадри
    f.append(fitbox(mx, 90, bw, bh, "кадр 0x3d0000\nкод libc", size=13,
                    fill="#eaf7ee", stroke=FIELD))
    f.append(fitbox(mx, 180, bw, bh, "кадр 0x1a2000", size=13))
    f.append(fitbox(mx, 285, bw, bh, "кадр 0x77f000", size=13))

    # стрілки зліва
    f.append(arrow(ax + bw + 6, 118, mx - 8, 118, color=FIELD))
    f.append(arrow(ax + bw + 6, 208, mx - 8, 208))
    # стрілки справа
    f.append(arrow(bx - 6, 118, mx + bw + 8, 118, color=FIELD))
    f.append(arrow(bx - 6, 208, mx + bw + 8, 300))

    # пояснення знизу
    f.append(text(490, 392, "однакове число 0x404018 у двох процесах — різні кадри", size=14))
    f.append(text(490, 424, "різні числа в двох процесах — один і той самий кадр libc",
                 size=14, color=FIELD))

    render(os.path.join(IMG, 'same-address.svg'), W, H, *f)


def fig_layout():
    """Розкладка адресного простору процесу на x86-64."""
    W, H = 940, 640
    f = []
    bx, bw = 305, 265

    rows = [
        (70, 122, "Половина ядра", "недоступна з режиму користувача", "#eef1f6"),
        (122, 168, "Неканонічна діра", "апаратно не існує", "#f0f0f0"),
        (168, 230, "Стек   ↓", "росте вниз; під ним порожній\nпроміжок 1 МіБ", FILL),
        (230, 268, "vDSO і vvar", "сторінки, які кладе ядро", FILL),
        (268, 340, "Ділянка відображень   ↓", "libc, відображені файли,\nвеликі шматки від mmap", FILL),
        (340, 432, "вільно", "запас, за рахунок якого зустрічні\nділянки не впираються одна в одну", "#fbfbfb"),
        (432, 484, "Купа   ↑", "верхню межу зсуває brk", FILL),
        (484, 522, "Дані та bss", "приватні для запису", FILL),
        (522, 574, "Код і сталі", "читати й виконувати; спільні\nз іншими запусками", FILL),
        (574, 604, "нульова сторінка", "не відображена — щоб NULL падав", "#f0f0f0"),
    ]
    for y0, y1, label, note, fill in rows:
        f.append(fitbox(bx, y0, bw, y1 - y0, label, size=14, fill=fill))
        lines = note.split("\n")
        cy = (y0 + y1) / 2 - (len(lines) - 1) * 13 * 1.3 / 2 + 5
        f.append(mtext(bx + bw + 26, cy, lines, size=13, color=MUTED, anchor="start"))

    # адреси меж — ліворуч від смуги, поза нею
    marks = [(70, "2⁶⁴ − 1"), (122, "0xffff800000000000"),
             (168, "0x00007ffffffff000"), (604, "0x0")]
    for y, s in marks:
        f.append(text(bx - 22, y + 5, s, size=13, color=INK, anchor="end"))

    f.append(text(W / 2, 630, "адреси зростають угору", size=13, color=MUTED))
    render(os.path.join(IMG, 'address-space-layout.svg'), W, H, *f)


def fig_vma_vs_pagetable():
    """Три долі адреси залежно від того, що про неї кажуть VMA й таблиця сторінок."""
    W, H = 980, 470
    f = []

    cols = [(30, 195, "адреса"), (270, 165, "список VMA"),
            (490, 150, "таблиця сторінок"), (680, 270, "що станеться")]
    for x, w, title in cols:
        f.append(text(x + w / 2, 72, title, size=15, bold=True))

    rows = [
        (100, "0x50000000", "немає такої\nділянки", "—",
         "SIGSEGV\nчисло без змісту", "#fdecea", POS),
        (222, "0x7f9a12c04000", "є: код libc,\nчитати й виконувати", "запису немає",
         "сторінковий збій:\nядро підкладає сторінку,\nпрограма нічого не помічає", FILL, LINE),
        (344, "0x404018", "є: дані,\nчитати й писати", "запис є",
         "звернення йде\nпрямо в кадр", "#eaf7ee", FIELD),
    ]
    bh = 76
    for y, addr, vma, pte, out, fill, stroke in rows:
        cy = y + bh / 2
        f.append(fitbox(30, y, 195, bh, addr, size=13))
        f.append(fitbox(270, y, 165, bh, vma, size=13))
        f.append(fitbox(490, y, 150, bh, pte, size=13))
        f.append(fitbox(680, y, 270, bh, out, size=13, fill=fill, stroke=stroke, sw=2))
        f.append(arrow(231, cy, 264, cy))
        f.append(arrow(441, cy, 484, cy))
        f.append(arrow(646, cy, 674, cy))

    render(os.path.join(IMG, 'vma-vs-pagetable.svg'), W, H, *f)


def fig_maps_line():
    """Рядок /proc/<pid>/maps, розібраний по полях."""
    W, H = 1020, 430
    f = []

    f.append(text(W / 2, 46, "один рядок /proc/<pid>/maps — це одна VMA",
                  size=15, bold=True))

    y0, bh = 70, 52
    boxes = [
        (40, 250, "7f2a1c000000-\n7f2a1c1f4000"),
        (302, 74, "r-xp"),
        (388, 108, "00028000"),
        (508, 78, "08:02"),
        (598, 88, "173521"),
        (698, 282, "/usr/lib/libc.so.6"),
    ]
    for i, (x, w, s) in enumerate(boxes):
        f.append(fitbox(x, y0, w, bh, s, size=13))
        cx = x + w / 2
        f.append(circle(cx, y0 + bh + 26, 13))
        f.append(text(cx, y0 + bh + 31, str(i + 1), size=13, bold=True))

    notes = [
        "1  діапазон адрес — 16-кова без «0x», кінець НЕ входить у ділянку",
        "2  права: r w x, четвертий символ — p (приватна) або s (спільна); брак права — «-»",
        "3  зсув у підпертому файлі, у байтах, 16-кова; для анонімної ділянки — нулі",
        "4  пристрій major:minor, 16-кова; анонімна ділянка дає 00:00",
        "5  inode — ДЕСЯТКОВА; нуль означає «файлу під ділянкою немає»",
        "6  шлях, псевдоім'я в дужках або порожньо; вилучений файл дістає « (deleted)»",
    ]
    yn = 210
    for i, s in enumerate(notes):
        f.append(text(50, yn + i * 34, s, size=14, anchor="start"))

    f.append(text(50, yn + len(notes) * 34 + 16,
                  "два числа в 16-ковій, одне в десятковій — розбір рядка це мусить враховувати",
                  size=13, color=POS, anchor="start"))

    render(os.path.join(IMG, 'maps-line-anatomy.svg'), W, H, *f)


def fig_page_accounting():
    """Куди одна сторінка ділянки потрапляє в лічильниках smaps."""
    W, H = 1010, 470
    f = []

    f.append(text(W / 2, 32, "куди одна сторінка ділянки лягає в лічильниках smaps",
                  size=15, bold=True))

    bh = 62
    f.append(fitbox(30, 220, 150, bh, "сторінка\nз ділянки", size=13))

    # верхня гілка — у пам'яті
    f.append(fitbox(230, 122, 210, bh, "у пам'яті\nRss += 4 КіБ", size=13,
                    fill="#eaf7ee", stroke=FIELD))
    # нижня гілка — у свопі
    f.append(fitbox(230, 322, 210, bh, "викинута у своп\nSwap += 4 КіБ", size=13,
                    fill="#fdecea", stroke=POS))

    f.append(arrow(184, 244, 224, 156))
    f.append(arrow(184, 256, 224, 346))

    # розгалуження за mapcount
    f.append(fitbox(500, 60, 230, bh, "mapcount ≥ 2 → Shared_*\nPss += 4 КіБ ÷ mapcount", size=13))
    f.append(fitbox(500, 182, 230, bh, "mapcount = 1 → Private_*\nPss += 4 КіБ", size=13))
    f.append(arrow(444, 142, 494, 92))
    f.append(arrow(444, 166, 494, 206))

    f.append(fitbox(500, 322, 230, bh, "SwapPss += 4 КіБ ÷ swp_swapcount", size=13))
    f.append(arrow(444, 353, 494, 353))

    # розгалуження за брудністю
    f.append(fitbox(790, 60, 190, bh, "брудна → *_Dirty\nчиста → *_Clean", size=13))
    f.append(fitbox(790, 182, 190, bh, "брудна → *_Dirty\nчиста → *_Clean", size=13))
    f.append(arrow(734, 91, 784, 91))
    f.append(arrow(734, 213, 784, 213))

    f.append(text(W / 2, 422,
                  "Rss = Shared_Clean + Shared_Dirty + Private_Clean + Private_Dirty",
                  size=14, bold=True))
    f.append(text(W / 2, 448,
                  "Swap і SwapPss живуть поза Rss: цих сторінок у пам'яті немає",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'smaps-page-accounting.svg'), W, H, *f)


def fig_gib_stages():
    """Що робиться з гігабайтом ділянки на кожному кроці досліду."""
    W, H = 1060, 530
    f = []

    LX, LW = 20, 232          # колонка з міткою кроку
    BX, BW = 262, 600         # смуга, що зображає 1024 МіБ ділянки
    NX = 878                  # колонка з числами

    PROMISE = (FILL, "#b9c0c8")
    RESIDENT = ("#eaf7ee", FIELD)
    NOACCESS = ("#fdecea", POS)
    GONE = (BG, "#cfcfcf")

    def seg(y, h, a, b, pair):
        x0 = BX + BW * a / 1024.0
        x1 = BX + BW * b / 1024.0
        return rect(x0, y, x1 - x0, h, fill=pair[0], stroke=pair[1], sw=1.2, rx=2)

    f.append(text(LX + LW, 66, "крок", size=15, bold=True, anchor="end"))
    f.append(text(BX + BW / 2, 66, "ділянка на 1 ГіБ", size=15, bold=True))
    f.append(text(NX, 66, "що показує ядро", size=15, bold=True, anchor="start"))

    rows = [
        ("mmap 1 ГіБ",
         [(0, 1024, PROMISE)], "1026.4", "1.61"),
        ("запис у перші 256 МіБ",
         [(0, 256, RESIDENT), (256, 1024, PROMISE)], "1026.4", "257.61"),
        ("mprotect PROT_NONE\nна 64…128 МіБ",
         [(0, 64, RESIDENT), (64, 128, NOACCESS), (128, 256, RESIDENT),
          (256, 1024, PROMISE)], "1026.4", "257.62"),
        ("madvise MADV_DONTNEED\nна 0…64 МіБ",
         [(0, 64, PROMISE), (64, 128, NOACCESS), (128, 256, RESIDENT),
          (256, 1024, PROMISE)], "1026.4", "193.62"),
        ("munmap 64…128 МіБ",
         [(0, 64, PROMISE), (64, 128, GONE), (128, 256, RESIDENT),
          (256, 1024, PROMISE)], "962.4", "129.62"),
    ]

    y, bh, step = 86, 46, 74
    for label, segs, vsz, rss in rows:
        cy = y + bh / 2
        lines = label.split("\n")
        ly = cy - (len(lines) - 1) * 13 * 1.3 / 2 + 5
        f.append(mtext(LX + LW, ly, lines, size=13, anchor="end"))
        for a, b, pair in segs:
            f.append(seg(y, bh, a, b, pair))
        f.append(text(NX, cy - 4, "VSZ " + vsz + " МіБ", size=12, color=MUTED, anchor="start"))
        f.append(text(NX, cy + 14, "RSS " + rss + " МіБ", size=12, anchor="start"))
        y += step

    # шкала під смугою
    base = y - step + bh
    for mib, lab in [(0, "0"), (256, "256"), (512, "512"), (1024, "1024 МіБ")]:
        x = BX + BW * mib / 1024.0
        f.append(line(x, base, x, base + 7, color=MUTED, sw=1))
        anc = "start" if mib == 0 else ("end" if mib == 1024 else "middle")
        f.append(text(x, base + 24, lab, size=12, color=MUTED, anchor=anc))

    # легенда
    ly = 492
    legend = [(PROMISE, "обіцяно, сторінок немає"), (RESIDENT, "сторінки в пам'яті"),
              (NOACCESS, "сторінки є, прав немає"), (GONE, "поза простором")]
    gap = 30
    total = sum(24 + 8 + text_width(t, 12) + gap for _, t in legend) - gap
    x = (W - total) / 2
    for pair, t in legend:
        f.append(rect(x, ly - 12, 24, 16, fill=pair[0], stroke=pair[1], sw=1.2, rx=2))
        f.append(text(x + 32, ly + 1, t, size=12, color=MUTED, anchor="start"))
        x += 24 + 8 + text_width(t, 12) + gap

    render(os.path.join(IMG, 'gib-stages.svg'), W, H, *f)


fig_same_address()
fig_layout()
fig_vma_vs_pagetable()
fig_maps_line()
fig_page_accounting()
fig_gib_stages()
print("ok")
