# -*- coding: utf-8 -*-
"""Фігури до теми «Як міряти пам'ять процесу: VSZ, RSS, PSS»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_one_frame():
    """Один спільний кадр — і три різні відповіді на питання «чий він»."""
    W, H = 1000, 430
    f = []

    # ── три процеси ліворуч
    px, pw, ph = 50, 190, 62
    ys = [95, 195, 295]
    for name, y in zip(("процес A", "процес B", "процес C"), ys):
        f.append(fitbox(px, y, pw, ph, name, size=15, bold=True))

    # ── кадр посередині
    fx, fy, fw, fh = 345, 165, 215, 122
    f.append(fitbox(fx, fy, fw, fh,
                    "один кадр\nфізичної пам'яті\n4 КіБ\nmapcount = 3",
                    size=14, fill="#eaf0fd", stroke=NEG, sw=2))

    # стрілки процеси → кадр
    for y in ys:
        f.append(arrow(px + pw + 8, y + ph / 2, fx - 8, fy + fh / 2, color=MUTED))

    # ── три відповіді праворуч
    rx, rw, rh = 630, 330, 78
    rys = [78, 176, 274]
    texts = [
        "RSS: кожному по 4 КіБ\nразом нарахували 12 КіБ",
        "PSS: кожному по 1.33 КіБ\nразом рівно 4 КіБ",
        "USS: нікому нічого\nкадр не приватний",
    ]
    cols = [(POS, "#fdecea"), (FIELD, "#eafaf0"), (MUTED, FILL)]
    for t, y, (st, fl) in zip(texts, rys, cols):
        f.append(fitbox(rx, y, rw, rh, t, size=14, stroke=st, fill=fl, sw=2))
        f.append(arrow(fx + fw + 8, fy + fh / 2, rx - 8, y + rh / 2, color=MUTED))

    f.append(text(W / 2, H - 22,
                  "один і той самий кадр рахують тричі, один раз або жодного разу",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'one-frame-three-counts.svg'), W, H, *f,
           title="Три показники про один спільний кадр")


def fig_vsz_vs_rss():
    """Карта простору процесу: скільки в кожній ділянці VSZ і скільки RSS."""
    W, H = 1010, 566
    f = []

    rows = [
        ("код і дані програми",          12,   3.0),
        ("бібліотеки (libc та інші)",     40,   6.0),
        ("купа: арени алокатора",        256,  18.0),
        ("стеки 8 потоків × 8 МіБ",       64,   0.3),
        ("файл, відображений mmap",     4096,  12.0),
        ("сторожові ділянки PROT_NONE",    8,   0.0),
    ]

    bx, bw = 320, 330          # смуга ділянки
    y0, rh, gap = 70, 52, 14

    for i, (name, vsz, rss) in enumerate(rows):
        y = y0 + i * (rh + gap)
        # ліва підпис-колонка
        f.append(text(bx - 18, y + rh / 2 + 5, name, size=13, anchor="end"))
        # уся ділянка = VSZ
        f.append(rect(bx, y, bw, rh, fill="#f7f8fa", stroke=MUTED, sw=1.5))
        # заселена частина = RSS
        frac = rss / vsz if vsz else 0
        w = max(7.0, bw * frac)
        f.append(rect(bx, y, w, rh, fill="#cfe0f7", stroke=NEG, sw=1.5))
        # права колонка з числами
        f.append(text(bx + bw + 22, y + rh / 2 + 5,
                      "VSZ %s МіБ   ·   RSS %s МіБ" % (
                          ("%d" % vsz), ("%.1f" % rss).rstrip("0").rstrip(".")),
                      size=13, anchor="start", color=INK))

    ytot = y0 + len(rows) * (rh + gap) + 16
    f.append(text(bx + bw / 2, ytot + 20,
                  "разом: VSZ 4476 МіБ   ·   RSS 39.3 МіБ", size=15, bold=True))
    f.append(text(bx + bw / 2, ytot + 44,
                  "світле — адреси, які процесові дозволено називати; синє — кадри, що справді є",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'vsz-vs-rss-map.svg'), W, H, *f,
           title="Одна карта пам'яті, два стовпчики")


def fig_page_life():
    """Що робить із показниками кожна подія в житті однієї сторінки."""
    W, H = 1130, 640
    f = []

    steps = [
        ("mmap 1 ГіБ анонімно",
         "VSZ +1 ГіБ · RSS 0 · PSS 0\nвідображення є, кадрів немає"),
        ("перший запис у сторінку",
         "збій → кадр\nRSS +4 КіБ · PSS +4 КіБ · USS +4 КіБ"),
        ("fork(): дитина взяла ту саму карту",
         "кадр один на двох\nRSS +4 КіБ кожному · PSS по 2 КіБ · USS 0"),
        ("дитина пише в цю сторінку",
         "копіювання при записі: кадрів стало два\nPSS знову по 4 КіБ · USS по 4 КіБ"),
        ("ядро витіснило сторінку у своп",
         "RSS −4 КіБ · Swap +4 КіБ\nVSZ не змінився"),
        ("програма викликала free()",
         "жодне число не змінилося\nкадр лишився в алокатора"),
    ]

    lx, lw = 40, 400
    rx, rw = 610, 480
    y0, rh, gap = 62, 76, 20

    for i, (ev, res) in enumerate(steps):
        y = y0 + i * (rh + gap)
        f.append(fitbox(lx, y, lw, rh, ev, size=14, bold=True))
        f.append(fitbox(rx, y, rw, rh, res, size=13,
                        fill="#eaf0fd", stroke=NEG))
        f.append(arrow(lx + lw + 12, y + rh / 2, rx - 12, y + rh / 2, color=MUTED))
        if i + 1 < len(steps):
            f.append(line(lx + lw / 2, y + rh, lx + lw / 2, y + rh + gap,
                          color=MUTED, sw=1.2, dash="4,4"))

    render(os.path.join(IMG, 'page-life-counters.svg'), W, H, *f,
           title="Життя однієї сторінки очима лічильників")


def fig_pss_lineage():
    """Чотири кроки родоводу PSS — і та сама причина під кожним."""
    W, H = 1180, 590
    f = []

    rows = [
        ("2007\nELC, доповідь",
         "Метт Мекелл показує: жоден показник\nне відповідає «скільки їсть застосунок»",
         "RSS рахує спільний кадр\nповністю кожному, хто в нього дивиться"),
        ("2008\nядро 2.6.25",
         "серія maps4: pagemap, kpagecount\nі рядок Pss у smaps",
         "тепер сума PSS по процесах\nдорівнює зайнятій оперативці"),
        ("2015\nядро 4.3",
         "Мінчан Кім додає SwapPss:\nспільна сторінка й у свопі спільна",
         "без нього сума Swap по процесах\nбула більша за сам своп"),
        ("2017\nядро 4.14",
         "Даніел Коласьйоне додає smaps_rollup:\nпідсумок без друку всіх ділянок",
         "Android опитує PSS постійно,\nповний smaps коштував сотні мілісекунд"),
    ]

    cx, cw = 40, 210
    mx, mw = 285, 470
    rx, rw = 790, 350
    y0, rh, gap = 62, 100, 24

    for i, (when, what, why) in enumerate(rows):
        y = y0 + i * (rh + gap)
        f.append(fitbox(cx, y, cw, rh, when, size=15, bold=True))
        f.append(fitbox(mx, y, mw, rh, what, size=13,
                        fill="#eaf0fd", stroke=NEG))
        f.append(fitbox(rx, y, rw, rh, why, size=13,
                        fill="#fdecea", stroke=POS))
        f.append(arrow(cx + cw + 12, y + rh / 2, mx - 12, y + rh / 2, color=MUTED))
        f.append(arrow(mx + mw + 12, y + rh / 2, rx - 12, y + rh / 2, color=MUTED))
        if i + 1 < len(rows):
            f.append(line(cx + cw / 2, y + rh, cx + cw / 2, y + rh + gap,
                          color=MUTED, sw=1.2, dash="4,4"))

    render(os.path.join(IMG, 'pss-lineage.svg'), W, H, *f,
           title="Родовід PSS: коли, що додали й чому сума не сходилася")


def fig_smaps_to_counters():
    """Один блок smaps і шість лічильників, які з нього складаються."""
    W, H = 1140, 592
    f = []

    # ── ліва панель: блок smaps як він є
    px, py, pw, ph = 40, 56, 484, 474
    f.append(rect(px, py, pw, ph, fill="#f7f8fa", stroke=MUTED, sw=1.5))

    rows = [
        ("7f2a…-7f2b… rw-p  /usr/lib/libc.so.6", None),
        ("Size:", "2048 kB"),
        ("KernelPageSize:", "4 kB"),
        ("Rss:", "760 kB"),
        ("Pss:", "63 kB"),
        ("Pss_Dirty:", "0 kB"),
        ("Shared_Clean:", "748 kB"),
        ("Shared_Dirty:", "0 kB"),
        ("Private_Clean:", "12 kB"),
        ("Private_Dirty:", "0 kB"),
        ("AnonHugePages:", "0 kB"),
        ("Swap:", "128 kB"),
        ("SwapPss:", "43 kB"),
        ("VmFlags: rd ex mr mw me", None),
    ]
    y_of = {}
    ly0, lstep = 88, 30
    for i, (name, val) in enumerate(rows):
        y = ly0 + i * lstep
        y_of[name] = y
        f.append(text(px + 18, y, name, size=13, anchor="start",
                      bold=(val is None),
                      color=(INK if val is not None else NEG)))
        if val:
            f.append(text(px + 276, y, val, size=13, anchor="end", color=MUTED))

    # ── праві лічильники
    bx, bw, bh = 700, 400, 54
    boxes = [
        ("VSZ  +=  Size", 70),
        ("RSS  +=  Rss", 148),
        ("PSS  +=  Pss", 226),
        ("USS  +=  Private_Clean + Private_Dirty", 304),
        ("Swap  +=  Swap", 382),
        ("SwapPSS  +=  SwapPss", 460),
    ]
    cols = [MUTED, NEG, FIELD, POS, MUTED, MUTED]
    fills = ["#f7f8fa", "#eaf0fd", "#eafaf0", "#fdecea", "#f7f8fa", "#f7f8fa"]
    for (label, by), st, fl in zip(boxes, cols, fills):
        f.append(fitbox(bx, by, bw, bh, label, size=14, bold=True,
                        stroke=st, fill=fl, sw=2))

    # ── стрілки: поле → лічильник (смуга 530…692 навмисно без тексту)
    links = [("Size:", 70), ("Rss:", 148), ("Pss:", 226),
             ("Private_Clean:", 304), ("Private_Dirty:", 304),
             ("Swap:", 382), ("SwapPss:", 460)]
    for name, by in links:
        f.append(arrow(px + pw + 6, y_of[name] - 4, bx - 8, by + bh / 2,
                       color=MUTED, sw=1.5))

    f.append(text(W / 2, H - 20,
                  "решту полів блоку розбирач пропускає — і не ламається на нових",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'smaps-to-counters.svg'), W, H, *f,
           title="Один блок smaps живить шість різних лічильників")


def fig_one_read():
    """Чому знімок треба забирати одним read(), а не кількома."""
    W, H = 1120, 508
    f = []

    # ── зверху: одне велике читання
    f.append(fitbox(40, 76, 250, 58, "одне read()\nу буфер на 4 МіБ",
                    size=15, bold=True, stroke=NEG, fill="#eaf0fd", sw=2))
    f.append(rect(320, 82, 700, 46, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(670, 111, "ядро йде всіма 2874 ділянками, не відпускаючи карти",
                  size=14))
    f.append(fitbox(320, 148, 700, 46,
                    "усі рядки описують ОДИН стан карти — суми сходяться",
                    size=14, stroke=FIELD, fill="#eafaf0", sw=2))

    # ── знизу: кілька дрібних читань
    f.append(fitbox(40, 262, 250, 58, "кілька read()\nпо 128 КіБ",
                    size=15, bold=True, stroke=POS, fill="#fdecea", sw=2))
    chunks = [(320, 200, "ділянки 1–840"), (560, 200, "841–1690"),
              (800, 220, "1691–2874")]
    for cx, cw, lab in chunks:
        f.append(rect(cx, 262, cw, 46, fill="#fdecea", stroke=POS, sw=2))
        f.append(text(cx + cw / 2, 291, lab, size=13))

    for gx in (540, 780):
        f.append(line(gx, 248, gx, 322, color=POS, sw=1.6, dash="5,4"))
    f.append(text(540, 344, "тут процес зробив munmap", size=12, color=POS))
    f.append(text(780, 344, "а тут — новий mmap", size=12, color=POS))

    f.append(fitbox(320, 372, 700, 62,
                    "рядки з різних станів карти: одну ділянку пропущено,\n"
                    "іншу надруковано двічі — підсумок не описує жодної миті",
                    size=14, stroke=POS, fill="#fdecea", sw=2))

    f.append(text(W / 2, H - 18,
                  "ядро обіцяє злагодженість лише в межах одного виклику read()",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'one-read-snapshot.svg'), W, H, *f,
           title="Знімок карти цілий рівно доти, доки триває один read()")


def fig_field_routing():
    """Лічильник у ядрі → файл /proc → стовпчик, який бачить людина."""
    W, H = 1220, 660
    f = []

    # ── колонка 1: що ядро тримає в mm_struct
    c1x, c1w = 36, 268
    src = [
        ("mm->total_vm",                            64,  62),
        ("MM_ANONPAGES\nMM_FILEPAGES\nMM_SHMEMPAGES", 156, 86),
        ("mm->data_vm\nmm->stack_vm",               282, 68),
        ("MM_SWAPENTS",                             378, 56),
        ("обхід таблиць\nсторінок процесу",         460, 72),
    ]
    for label, y, h in src:
        f.append(fitbox(c1x, y, c1w, h, label, size=13, bold=True,
                        fill=FILL, stroke=MUTED, sw=1.5))

    # ── колонка 2: файли
    c2x, c2w = 452, 252
    files = [
        ("/proc/<pid>/statm\nсторінки",     70,  70),
        ("/proc/<pid>/status\nkB",         192,  70),
        ("/proc/<pid>/smaps\nkB, по ділянці", 330, 74),
        ("/proc/<pid>/smaps_rollup\nkB, підсумок", 452, 74),
    ]
    for label, y, h in files:
        f.append(fitbox(c2x, y, c2w, h, label, size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=2))

    # ── колонка 3: те, що бачить людина
    c3x, c3w = 852, 332
    outs = [
        ("top: VIRT · RES · SHR\nCODE · DATA",            60,  70),
        ("ps: VSZ · RSS · RSZ\nSZ · SIZE · %MEM",        176,  70),
        ("top: SWAP · USED\nRSan · RSfd · RSsh · RSlk",  292,  70),
        ("PSS · USS · SwapPss\nу ps і top їх немає",     430,  70),
    ]
    fills = ["#f7f8fa", "#f7f8fa", "#f7f8fa", "#eafaf0"]
    strokes = [MUTED, MUTED, MUTED, FIELD]
    for (label, y, h), fl, st in zip(outs, fills, strokes):
        f.append(fitbox(c3x, y, c3w, h, label, size=13, bold=True,
                        fill=fl, stroke=st, sw=2))

    def mid(col, item):
        return col[item][1] + col[item][2] / 2

    # ── стрілки: лічильники → файли (проміжок 304…452 тексту не має)
    for si, fi in ((0, 0), (0, 1), (1, 0), (1, 1),
                   (2, 0), (2, 1), (3, 1), (4, 2), (4, 3)):
        f.append(arrow(c1x + c1w + 8, mid(src, si),
                       c2x - 8, mid(files, fi), color=MUTED, sw=1.3))

    # ── стрілки: файли → стовпчики (проміжок 704…852 тексту не має)
    for fi, oi in ((0, 0), (1, 1), (1, 2), (2, 3), (3, 3)):
        f.append(arrow(c2x + c2w + 8, mid(files, fi),
                       c3x - 8, mid(outs, oi), color=MUTED, sw=1.3))

    # ── підписи колонок
    f.append(text(c1x + c1w / 2, 40, "лічильники ядра", size=14, bold=True, color=MUTED))
    f.append(text(c2x + c2w / 2, 40, "файли /proc", size=14, bold=True, color=MUTED))
    f.append(text(c3x + c3w / 2, 40, "що бачить людина", size=14, bold=True, color=MUTED))

    f.append(text(W / 2, H - 42,
                  "верхні чотири лічильники читаються без обходу таблиць — тому statm і status дешеві",
                  size=13, color=MUTED, italic=True))
    f.append(text(W / 2, H - 18,
                  "PSS і USS живуть лише в нижній гілці: за них платять обходом таблиць сторінок",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'field-routing.svg'), W, H, *f,
           title="Звідки береться кожне число про пам'ять процесу")


if __name__ == '__main__':
    fig_one_frame()
    fig_vsz_vs_rss()
    fig_page_life()
    fig_pss_lineage()
    fig_smaps_to_counters()
    fig_one_read()
    fig_field_routing()
    print("ok")
