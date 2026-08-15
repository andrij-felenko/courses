# -*- coding: utf-8 -*-
"""Фігури до теми «KSM: злиття однакових сторінок» (reference/unix-linux/memory)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Спільність за походженням проти однакового вмісту ────────────────────
def fig_origin_vs_content():
    W, H = 1080, 430
    f = []

    # панелі
    f.append(rect(24, 46, 496, 350, fill="#fbfcfd", stroke=MUTED, sw=1.2))
    f.append(rect(560, 46, 496, 350, fill="#fbfcfd", stroke=MUTED, sw=1.2))

    f.append(fitbox(56, 66, 432, 46, "Спільне за походженням", size=16, bold=True,
                    fill="#eef7f0", stroke=FIELD))
    f.append(fitbox(592, 66, 432, 46, "Однаковий вміст без спорідненості", size=16,
                    bold=True, fill="#fdecea", stroke=POS))

    # ліва панель: два процеси — один кадр
    f.append(fitbox(72, 148, 170, 48, "Процес A", size=15))
    f.append(fitbox(302, 148, 170, 48, "Процес B", size=15))
    f.append(fitbox(148, 250, 248, 62, "один кадр", size=15, bold=True,
                    fill="#eef7f0", stroke=FIELD))
    f.append(arrow(157, 200, 232, 246, color=FIELD))
    f.append(arrow(387, 200, 312, 246, color=FIELD))
    f.append(mtext(272, 344, ["той самий файл і зміщення",
                              "або спільний предок після fork"], size=14, color=MUTED))

    # права панель: два процеси — два кадри з однаковим вмістом
    f.append(fitbox(608, 148, 170, 48, "Процес C", size=15))
    f.append(fitbox(838, 148, 170, 48, "Процес D", size=15))
    f.append(fitbox(586, 250, 214, 62, "кадр 1\n7f 45 4c 46 …", size=14,
                    fill="#fdecea", stroke=POS))
    f.append(fitbox(816, 250, 214, 62, "кадр 2\n7f 45 4c 46 …", size=14,
                    fill="#fdecea", stroke=POS))
    f.append(arrow(693, 200, 693, 246, color=POS))
    f.append(arrow(923, 200, 923, 246, color=POS))
    f.append(mtext(808, 344, ["байти збігаються, а запису про це немає —",
                              "помітити можна лише порівнявши 4096 байтів"],
                   size=14, color=MUTED))

    render(os.path.join(OUT, 'origin-vs-content.svg'), W, H, *f,
           title="Два джерела спільної сторінки — і лише одне з них безкоштовне")


# ── 2. Шлях відсканованої сторінки через два дерева ─────────────────────────
def fig_two_trees():
    W, H = 1100, 600
    f = []

    xl, wl = 48, 350          # ліва колонка — питання
    xr, wr = 590, 470         # права колонка — результат

    f.append(fitbox(xl, 56, wl, 56, "сторінка, яку взяв ksmd", size=15, bold=True,
                    fill="#eef2f7"))

    rows = [
        (168, "збіг у стабільному дереві?",
         "приєднатися до готової спільної\nсторінки, свій кадр звільнити", "#eef7f0", FIELD),
        (296, "збіг у нестабільному дереві?",
         "злити дві звичайні сторінки в одну\nспільну, вузол — у стабільне дерево", "#eef7f0", FIELD),
        (424, "контрольна сума не змінилася?",
         "покласти в нестабільне дерево\nй чекати на пару", FILL, LINE),
    ]

    hq = 68
    for y, q, res, fill, stroke in rows:
        f.append(fitbox(xl, y, wl, hq, q, size=15, fill="#f8fafc"))
        f.append(fitbox(xr, y, wr, hq, res, size=14, fill=fill, stroke=stroke))
        f.append(arrow(xl + wl + 8, y + hq / 2, xr - 8, y + hq / 2, color=stroke))
        f.append(text((xl + wl + xr) / 2, y + hq / 2 - 16, "так", size=14, color=MUTED))

    xc = xl + wl / 2
    f.append(arrow(xc, 112, xc, 164))
    for y0, y1 in ((236, 292), (364, 420), (492, 516)):
        f.append(arrow(xc, y0, xc, y1))
        f.append(text(xc + 18, (y0 + y1) / 2 + 5, "ні", size=14,
                      color=MUTED, anchor="start"))

    f.append(fitbox(xl, 520, wl, 56, "летюча сторінка — пропустити", size=15,
                    fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, 'two-trees.svg'), W, H, *f,
           title="Три розвилки, які проходить кожна відсканована сторінка")


# ── 3. Ланцюжок двійників після стелі спільності ────────────────────────────
def fig_sharing_chain():
    W, H = 1100, 440
    f = []

    f.append(fitbox(48, 150, 258, 86, "вузол стабільного\nдерева · вміст X", size=15,
                    bold=True, fill="#eef2f7"))

    dups = [
        (368, "двійник 1", "256 користувачів"),
        (614, "двійник 2", "256 користувачів"),
        (860, "двійник 40", "16 користувачів"),
    ]
    for x, name, users in dups:
        f.append(fitbox(x, 150, 206, 86, name + "\n" + users, size=14,
                        fill="#eef7f0", stroke=FIELD))

    f.append(arrow(314, 193, 360, 193, color=FIELD))
    f.append(arrow(582, 193, 606, 193, color=FIELD))
    f.append(arrow(828, 193, 852, 193, color=FIELD))
    f.append(text(840, 132, "… ще 37 …", size=13, color=MUTED))

    f.append(mtext(550, 276, ["усі 40 кадрів містять однакові байти;",
                              "новий охочий іде до того, у кого лишилося місце"],
                   size=14, color=MUTED))

    f.append(fitbox(160, 326, 780, 62,
                    "без стелі: 1 кадр, обхід до 10 000 кроків     ·     "
                    "зі стелею 256: 40 кадрів, обхід ≤ 256 кроків",
                    size=15, fill="#f8fafc"))

    render(os.path.join(OUT, 'sharing-chain.svg'), W, H, *f,
           title="Стеля спільності: трохи зайвих кадрів замість довгого обходу")


# ── 4. Три згоди перед злиттям і три місця, де читати результат ─────────────
def fig_three_gates():
    W, H = 1140, 552
    f = []

    cols = (40, 410, 780)
    cw = 320

    gates = [
        ["1 · уся система", "/sys/kernel/mm/ksm/run = 1"],
        ["2 · дозвіл на ділянку", "madvise(MADV_MERGEABLE)", "або prctl(PR_SET_MEMORY_MERGE)"],
        ["3 · тип ділянки підходить", "анонімна приватна;", "не спільна, не hugetlb,", "не DAX, не VM_IO"],
    ]
    for x, lines in zip(cols, gates):
        f.append(fitbox(x, 64, cw, 110, "\n".join(lines), size=15,
                        fill="#eef2f7", stroke=LINE))

    f.append(text(385, 124, "та", size=14, color=MUTED))
    f.append(text(755, 124, "та", size=14, color=MUTED))

    f.append(fitbox(290, 250, 560, 64, "ksmd бере цю сторінку в роботу", size=16,
                    bold=True, fill="#eef7f0", stroke=FIELD))

    f.append(arrow(200, 178, 440, 244))
    f.append(arrow(570, 178, 570, 244))
    f.append(arrow(940, 178, 700, 244))

    reads = [
        ["/sys/kernel/mm/ksm/", "уся система:", "pages_sharing · general_profit"],
        ["/proc/<pid>/ksm_stat", "один процес:", "ksm_merging_pages,", "ksm_process_profit"],
        ["/proc/<pid>/smaps", "одна ділянка:", "рядок KSM · VmFlags: mg"],
    ]
    for x, lines in zip(cols, reads):
        f.append(fitbox(x, 384, cw, 120, "\n".join(lines), size=15,
                        fill="#f8fafc", stroke=MUTED))

    f.append(arrow(440, 318, 200, 378, color=MUTED))
    f.append(arrow(570, 318, 570, 378, color=MUTED))
    f.append(arrow(700, 318, 940, 378, color=MUTED))

    render(os.path.join(OUT, 'ksm-gates-and-readouts.svg'), W, H, *f,
           title="Три умови злиття і три рівні, на яких видно результат")


# ── 5. Лабораторія: що зрушило після злиття, а що ні ───────────────────────
def _sp(n):
    """1234567 → «1 234 567» (нерозривний пробіл не потрібен — це svg)."""
    s, out = str(int(n)), ""
    while len(s) > 3:
        out, s = " " + s[-3:] + out, s[:-3]
    return s + out


def fig_lab_counters():
    W, H = 1030, 462
    f = []
    x0 = 306.0
    k = 600.0 / 65536.0          # 65536 кБ → 600 px

    f.append(rect(x0, 38, 20, 20, fill="#e5e7eb", stroke=MUTED, sw=1.2, rx=3))
    f.append(text(x0 + 30, 54, "до сканування", size=14, color=MUTED, anchor="start"))
    f.append(rect(x0 + 190, 38, 20, 20, fill="#eef7f0", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(x0 + 220, 54, "після трьох проходів ksmd", size=14,
                  color=MUTED, anchor="start"))

    rows = [
        (96,  "Rss\nскільки сторінок відображено", 65536, 65536, "#e5e7eb", MUTED),
        (204, "Pss\nчастка процесу в кадрах",      65536, 32768, "#eaf0fd", NEG),
        (312, "KSM\nз них злитих",                     0, 65536, "#eef7f0", FIELD),
    ]
    for y, label, before, after, fill_a, stroke_a in rows:
        f.append(fitbox(40, y, 246, 80, label, size=15, fill="#f8fafc", stroke=MUTED))
        pair = ((before, "#e5e7eb", MUTED), (after, fill_a, stroke_a))
        for i, (val, fl, st) in enumerate(pair):
            by = y + 6 + i * 40
            w = val * k
            if w >= 3:
                f.append(rect(x0, by, w, 28, fill=fl, stroke=st, sw=1.4, rx=4))
            f.append(text(x0 + (w if w >= 3 else 0) + 12, by + 20,
                          _sp(val) + " кБ", size=13, anchor="start"))

    f.append(fitbox(40, 402, 950, 46,
                    "звільнилося насправді 16 384 кадрів = 64 МіБ — і про це каже "
                    "лише система: pages_sharing та MemFree",
                    size=14, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, 'lab-counters.svg'), W, H, *f,
           title="Ділянка на 64 МіБ після злиття: Rss не зрушив, Pss удвічі менший")


# ── 6. Лабораторія: два згустки часу запису й проміжок між ними ─────────────
def fig_write_cost_gap():
    W, H = 1040, 376
    f = []
    xa, xb, tmax = 200.0, 950.0, 3.6

    def X(t):
        return xa + (xb - xa) * t / tmax

    ay = 288
    f.append(line(xa, ay, xb, ay, color=INK, sw=1.4))
    t = 0.0
    while t <= tmax + 1e-9:
        f.append(line(X(t), ay, X(t), ay + 7, color=INK, sw=1.2))
        f.append(text(X(t), ay + 26, "%.1f" % t, size=13, color=MUTED))
        t += 0.5
    f.append(text((xa + xb) / 2, ay + 52, "час запису одного байта, мкс",
                  size=14, color=MUTED))

    f.append(rect(X(0.194), 154, X(2.204) - X(0.194), 24,
                  fill="#f3f4f6", stroke=MUTED, sw=1.0, rx=4))
    f.append(text((X(0.194) + X(2.204)) / 2, 171,
                  "проміжок 2.0 мкс — згустки не перекриваються", size=13, color=MUTED))

    f.append(fitbox(24, 104, 168, 46, "незлита\nсторінка", size=14,
                    fill="#f8fafc", stroke=MUTED))
    f.append(rect(X(0.121), 108, max(X(0.194) - X(0.121), 4), 38,
                  fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    f.append(line(X(0.148), 102, X(0.148), 152, color=NEG, sw=2.4))
    f.append(text(262, 96, "медіана 0.148 мкс · від 0.121 до 0.194",
                  size=13, color=NEG, anchor="start"))

    f.append(fitbox(24, 182, 168, 46, "злита\nсторінка", size=14,
                    fill="#f8fafc", stroke=MUTED))
    f.append(rect(X(2.204), 186, X(3.310) - X(2.204), 38,
                  fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    f.append(line(X(2.631), 180, X(2.631), 230, color=POS, sw=2.4))
    f.append(text(X(2.631), 254, "медіана 2.631 мкс · від 2.204 до 3.310",
                  size=13, color=POS))

    render(os.path.join(OUT, 'write-cost-gap.svg'), W, H, *f,
           title="Запис одного байта: два розділені згустки замість одного")


fig_origin_vs_content()
fig_two_trees()
fig_sharing_chain()
fig_three_gates()
fig_lab_counters()
fig_write_cost_gap()
print("ok")
