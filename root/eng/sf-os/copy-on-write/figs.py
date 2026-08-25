# -*- coding: utf-8 -*-
"""Фігури до теми «Копіювання при записі» (reference/unix-linux/memory)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def edgepoint(cx, cy, w, h, tx, ty, pad=7):
    """Точка на межі рамки (cx,cy,w,h) у напрямку до (tx,ty), з відступом pad."""
    dx, dy = tx - cx, ty - cy
    sx = (w / 2.0 + pad) / abs(dx) if dx else 1e9
    sy = (h / 2.0 + pad) / abs(dy) if dy else 1e9
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


# ── 1. Права записано двічі: у ділянці й у таблиці сторінок ──────────────────
def fig_pte_vs_vma():
    W, H = 1000, 400
    frags = []

    cx1, w1 = 26, 236          # колонка «ділянка»
    cx2, w2 = 282, 168         # колонка «запис у таблиці»
    cx3, w3 = 470, 504         # колонка «наслідок»

    hy, hh = 52, 44
    frags.append(fitbox(cx1, hy, w1, hh, "Права ділянки (VMA)", size=15, bold=True,
                        fill="#eef2f7"))
    frags.append(fitbox(cx2, hy, w2, hh, "Біт W у таблиці", size=15, bold=True,
                        fill="#eef2f7"))
    frags.append(fitbox(cx3, hy, w3, hh, "Що станеться при записі", size=15, bold=True,
                        fill="#eef2f7"))

    rows = [
        ("читання + запис", "W = 1",
         "запис іде прямо в пам'ять;\nядро про нього навіть не дізнається",
         FILL, LINE),
        ("читання + запис", "W = 0",
         "пастка; ядро бачить дозвіл у ділянці —\nотже, це збій копіювання при записі",
         "#fdecea", POS),
        ("тільки читання", "W = 0",
         "пастка; дозволу нема й у ділянці —\nотже, це справжнє порушення, SIGSEGV",
         "#eaf0fd", NEG),
    ]

    y = 116
    rh, gap = 82, 18
    for vma, pte, effect, fill, stroke in rows:
        frags.append(fitbox(cx1, y, w1, rh, vma, size=15, fill=fill, stroke=stroke))
        frags.append(fitbox(cx2, y, w2, rh, pte, size=16, bold=True, fill=fill, stroke=stroke))
        frags.append(fitbox(cx3, y, w3, rh, effect, size=15, fill=fill, stroke=stroke))
        y += rh + gap

    render(os.path.join(OUT, 'pte-vs-vma.svg'), W, H, *frags,
           title="Дозвіл на запис записано двічі — і працює саме розбіжність")


# ── 2. Хто ще може дотягтися до фізичного кадру ─────────────────────────────
def fig_who_holds():
    W, H = 980, 520
    frags = []

    ccx, ccy, cw, ch = 490, 268, 250, 74
    holders = [
        (168, 128, "Таблиця сторінок\nпроцесу-батька", FILL, LINE),
        (812, 128, "Таблиця сторінок\nпроцесу-дитини", FILL, LINE),
        (150, 268, "Кеш свопу", "#fdecea", POS),
        (830, 268, "Кеш сторінок\nфайлу", "#fdecea", POS),
        (168, 412, "Буфер каналу\n(vmsplice)", "#fdecea", POS),
        (812, 412, "Закріплення\nпід DMA", "#fdecea", POS),
    ]

    for hx, hy, label, fill, stroke in holders:
        body, bw, bh = textbox(hx, hy, label, size=15, pad=12, fill=fill, stroke=stroke)
        frags.append(body)
        sx, sy = edgepoint(hx, hy, bw, bh, ccx, ccy)
        ex, ey = edgepoint(ccx, ccy, cw, ch, hx, hy, pad=9)
        frags.append(arrow(sx, sy, ex, ey, color=stroke))

    frags.append(fitbox(ccx - cw / 2, ccy - ch / 2, cw, ch,
                        "Фізичний кадр\nіз даними сторінки", size=16, bold=True,
                        fill="#e8f6ee", stroke=FIELD))

    render(os.path.join(OUT, 'who-holds-the-frame.svg'), W, H, *frags,
           title="Скільки посилань на кадр — питання не лише до таблиць сторінок")


# ── 3. Приватне відображення файлу до й після запису ─────────────────────────
def fig_private_file_map():
    W, H = 1000, 470
    frags = []

    def panel(px, title, split):
        out = [rect(px, 56, 450, 386, fill="#fbfcfd", stroke="#c9d2dc", sw=1.2, rx=10)]
        out.append(text(px + 225, 84, title, size=16, bold=True))

        if not split:
            out.append(fitbox(px + 105, 108, 240, 62,
                              "Запис у таблиці\nкадр 41, W = 0", size=14))
            out.append(arrow(px + 225, 172, px + 225, 214))
            out.append(fitbox(px + 85, 218, 280, 62,
                              "Кадр 41 — сторінка\nкешу цього файлу", size=14,
                              fill="#e8f6ee", stroke=FIELD))
            out.append(arrow(px + 225, 282, px + 225, 324))
            out.append(fitbox(px + 105, 328, 240, 62, "Файл на диску", size=14,
                              fill="#eef2f7"))
        else:
            out.append(fitbox(px + 240, 108, 190, 62,
                              "Запис у таблиці\nкадр 88, W = 1", size=14,
                              fill="#fdecea", stroke=POS))
            out.append(arrow(px + 335, 172, px + 335, 214))
            out.append(fitbox(px + 240, 218, 190, 62,
                              "Кадр 88 — приватна\nанонімна копія", size=14,
                              fill="#fdecea", stroke=POS))
            out.append(fitbox(px + 24, 218, 190, 62,
                              "Кадр 41 — сторінка\nкешу файлу", size=14,
                              fill="#e8f6ee", stroke=FIELD))
            out.append(arrow(px + 119, 282, px + 119, 324))
            out.append(fitbox(px + 24, 328, 190, 62, "Файл на диску", size=14,
                              fill="#eef2f7"))
            out.append(line(px + 214, 300, px + 240, 300, color=MUTED, sw=1.4, dash="5 5"))
            out.append(text(px + 335, 372, "запис сюди файлу", size=13, color=MUTED))
            out.append(text(px + 335, 392, "вже не досягає", size=13, color=MUTED))
        return out

    frags += panel(24, "До першого запису", False)
    frags += panel(526, "Після першого запису", True)

    render(os.path.join(OUT, 'private-file-map.svg'), W, H, *frags,
           title="Приватне відображення файлу відколюється від файлу при першому записі")


# ── 4. Стрічка часу Dirty COW (до вставки hist-dirty-cow) ────────────────────
def fig_dirty_cow_timeline():
    W, H = 1000, 748
    frags = []

    xd, wd = 26, 230
    xe, we = 272, 702

    frags.append(fitbox(xd, 52, wd, 44, "Коли", size=15, bold=True, fill="#eef2f7"))
    frags.append(fitbox(xe, 52, we, 44, "Що сталося", size=15, bold=True, fill="#eef2f7"))

    NEU = "#f4f6f8"
    BAD = "#fdecea"
    GOOD = "#e8f6ee"

    rows = [
        ("1 серпня 2005",
         "Лінус Торвальдс закриває перегони в get_user_pages\nкомітом 4ceb5db9757a",
         NEU, LINE),
        ("3 серпня 2005",
         "Нік Піґґін відкочує латку через s390 (f33ea7f404e5)\nі ставить на її місце компроміс із VM_FAULT_WRITE",
         BAD, POS),
        ("липень 2007",
         "ядро 2.6.22 — від цієї версії відлічують вразливі ядра",
         BAD, POS),
        ("квітень 2013",
         "s390 дістає програмний біт «брудна» (ядро 3.9):\nпричина відкоту зникла, про помилку не згадали",
         BAD, POS),
        ("жовтень 2016",
         "Філ Оестер знаходить готовий експлойт\nу записаному трафіку зламаного вебсервера",
         BAD, POS),
        ("13–18 жовтня 2016",
         "Торвальдс пише коміт 19be0eaffa3a — прапорець FOLL_COW\nзамість ігор із FOLL_WRITE",
         GOOD, FIELD),
        ("19 жовтня 2016",
         "публічне розкриття: CVE-2016-5195, ім'я Dirty COW;\nстабільні 4.8.3, 4.7.9, 4.4.26",
         GOOD, FIELD),
        ("27 листопада 2017",
         "латку доводиться доповнювати для великих сторінок\n(CVE-2017-1000405)",
         GOOD, FIELD),
    ]

    y = 116
    rh, gap = 64, 12
    for when, what, fill, stroke in rows:
        frags.append(fitbox(xd, y, wd, rh, when, size=15, bold=True, fill=fill, stroke=stroke))
        frags.append(fitbox(xe, y, we, rh, what, size=14, fill=fill, stroke=stroke))
        y += rh + gap

    render(os.path.join(OUT, 'dirty-cow-timeline.svg'), W, H, *frags,
           title="Дванадцять років: від першої латки до останньої")


# ── 5. Що переживає fork, а що execve (до вставки api-cow-controls) ──────────
def fig_controls_lifetime():
    W, H = 1040, 594
    frags = []

    xl, wl = 24, 286
    x1, w1 = 318, 222
    x2, w2 = 548, 222
    x3, w3 = 778, 238

    hy, hh = 52, 46
    frags.append(fitbox(xl, hy, wl, hh, "Важіль або позначка", size=15, bold=True,
                        fill="#eef2f7"))
    frags.append(fitbox(x1, hy, w1, hh, "У того, хто поставив", size=15, bold=True,
                        fill="#eef2f7"))
    frags.append(fitbox(x2, hy, w2, hh, "У дитини після fork", size=15, bold=True,
                        fill="#eef2f7"))
    frags.append(fitbox(x3, hy, w3, hh, "Після execve", size=15, bold=True,
                        fill="#eef2f7"))

    GOOD, GONE, ABS = "#e8f6ee", "#eef2f7", "#eaf0fd"

    rows = [
        ("Прапорці mmap ділянки\n(MAP_PRIVATE, MAP_NORESERVE)",
         ("діють", GOOD, FIELD),
         ("ті самі —\nділянку успадковано", GOOD, FIELD),
         ("простір новий,\nділянки немає", GONE, MUTED)),
        ("MADV_DONTFORK\n(код dc у VmFlags)",
         ("діє", GOOD, FIELD),
         ("ділянки в дитині\nнемає взагалі", ABS, NEG),
         ("стерто разом\nіз простором", GONE, MUTED)),
        ("MADV_WIPEONFORK\n(код wf у VmFlags)",
         ("діє", GOOD, FIELD),
         ("ділянка є, вміст —\nнулі; позначка чинна", GOOD, FIELD),
         ("стерто разом\nіз простором", GONE, MUTED)),
        ("prctl(PR_SET_THP_DISABLE)",
         ("діє", GOOD, FIELD),
         ("успадковано", GOOD, FIELD),
         ("лишається чинним", GOOD, FIELD)),
        ("pagemap, біт 56\n«сторінка виключна»",
         ("1 — сторінка\nналежить лише мені", FILL, LINE),
         ("0 в обох, поки\nхтось не напише", FILL, LINE),
         ("сторінки нові —\nзнову 1", FILL, LINE)),
    ]

    y = 124
    rh, gap = 78, 14
    for label, c1, c2, c3 in rows:
        frags.append(fitbox(xl, y, wl, rh, label, size=14, bold=True, fill="#f8fafc"))
        for (x, w), (txt, fill, stroke) in zip(((x1, w1), (x2, w2), (x3, w3)),
                                               (c1, c2, c3)):
            frags.append(fitbox(x, y, w, rh, txt, size=14, fill=fill, stroke=stroke))
        y += rh + gap

    render(os.path.join(OUT, 'controls-lifetime.svg'), W, H, *frags,
           title="Настанова живе на ділянці — а ділянка не переживає execve")


fig_pte_vs_vma()
fig_who_holds()
fig_private_file_map()
fig_dirty_cow_timeline()
fig_controls_lifetime()
print("ok")
