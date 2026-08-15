# -*- coding: utf-8 -*-
"""Фігури для теми «Сторінки, таблиці сторінок і MMU» (довідник Unix і Linux)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GRN_F = "#eafaf0"
BLU_F = "#eaf0fd"
RED_F = "#fdecea"
YEL_F = "#fff5e0"


# ── 1. Розклад адреси й обхід чотирьох таблиць ─────────────────────────────
def fig_translate():
    W, H = 1340, 790
    F = []

    SY, SH = 56, 74
    cells = [
        (110, 170, "канонічні\n63…48", FILL),
        (280, 185, "рівень 1\n47…39", BLU_F),
        (465, 185, "рівень 2\n38…30", BLU_F),
        (650, 185, "рівень 3\n29…21", BLU_F),
        (835, 185, "рівень 4\n20…12", BLU_F),
        (1020, 210, "зміщення\n11…0", GRN_F),
    ]
    for x, w, s, fill in cells:
        F.append(fitbox(x, SY, w, SH, s, size=15, fill=fill))

    idx = [(372.5, "індекс 254"), (557.5, "індекс 242"),
           (742.5, "індекс 208"), (927.5, "індекс 434")]
    for cx, s in idx:
        F.append(text(cx, 152, s, size=13, color=MUTED))
    F.append(text(1125, 152, "0xC48", size=13, color=MUTED))

    TY, TW, TH = 240, 200, 185
    tx = [140, 380, 620, 860]
    hit = [7, 3, 5, 2]           # який рядок підсвічено в кожній таблиці
    labels = ["запис 254", "запис 242", "запис 208", "запис 434"]

    for i, x0 in enumerate(tx):
        F.append(rect(x0, TY, TW, TH, fill=BG, stroke=LINE, sw=1.6))
        F.append(text(x0 + TW / 2, TY + 26, "таблиця рівня %d" % (i + 1),
                      size=13, bold=True))
        by = TY + 42
        for k in range(9):
            y = by + k * 15
            if k == hit[i]:
                F.append(fitbox(x0 + 14, y - 2, TW - 28, 19, labels[i],
                                size=11, pad=4, fill=YEL_F, stroke=POS, sw=1.4, rx=3))
            else:
                F.append(rect(x0 + 14, y, TW - 28, 11, fill=FILL, stroke=MUTED,
                              sw=0.8, rx=2))

    # корінь
    F.append(textbox(76, TY + 92, "CR3\nкорінь", size=12, fill=GRN_F, pad=8)[0])
    F.append(arrow(112, TY + 92, tx[0] - 4, TY + 92))

    # адреса → таблиці
    for (cx, _), x0 in zip(idx, tx):
        F.append(arrow(cx, 168, x0 + TW / 2, TY - 6))

    # таблиця → таблиця
    for i in range(3):
        F.append(arrow(tx[i] + TW, TY + 95, tx[i + 1] - 4, TY + 95))

    F.append(text(600, 490,
                  "кожна таблиця — це рівно одна сторінка: 512 записів по 8 байтів",
                  size=13, color=MUTED))
    F.append(text(600, 520,
                  "знайдений запис містить фізичну адресу таблиці наступного рівня",
                  size=13, color=MUTED))

    BY, BH = 615, 72
    F.append(fitbox(110, BY, 910, BH, "номер кадру 0x1a2f3", size=16, fill=BLU_F))
    F.append(fitbox(1020, BY, 210, BH, "зміщення 0xC48", size=15, fill=GRN_F))

    F.append(arrow(960, TY + TH, 960, BY - 4))
    F.append(line(1125, 168, 1125, BY - 10, color=FIELD, sw=1.6, dash="6 5"))
    F.append(arrow(1125, BY - 22, 1125, BY - 4, color=FIELD))

    F.append(arrow(670, BY + BH, 670, BY + BH + 26))
    F.append(text(670, BY + BH + 52, "фізична адреса = 0x1a2f3c48", size=16, bold=True))

    return render(os.path.join(IMG, "translate.svg"), W, H, *F,
                  title="віртуальна адреса 0x00007f3c9a1b2c48")


# ── 2. Швидкий і повільний шлях перекладу ──────────────────────────────────
def fig_tlb_path():
    W, H = 1280, 570
    F = []

    F.append(fitbox(40, 220, 150, 76, "адреса\nвід процесора", size=13, fill=FILL))
    F.append(arrow(192, 258, 212, 258))
    F.append(fitbox(214, 208, 150, 100, "TLB\nкеш готових\nперекладів",
                    size=13, fill=BLU_F))

    # верхня смуга — влучання
    F.append(arrow(366, 232, 432, 152))
    F.append(fitbox(436, 116, 600, 66,
                    "влучання (понад 99 % звернень) — кадр відомий одразу",
                    size=14, fill=GRN_F))

    # нижня смуга — промах і обхід
    F.append(arrow(366, 284, 432, 366))
    F.append(text(700, 340, "промах — обхід дерева: до чотирьох звернень до пам'яті",
                  size=13, color=MUTED))
    wx = [436, 586, 736, 886]
    for i, x0 in enumerate(wx):
        F.append(fitbox(x0, 352, 120, 78, "таблиця\nрівня %d" % (i + 1),
                        size=12, fill=FILL))
        if i < 3:
            F.append(arrow(x0 + 120, 391, x0 + 146, 391))

    F.append(fitbox(1096, 214, 150, 88, "номер\nкадру", size=15, fill=YEL_F))
    F.append(arrow(1038, 152, 1092, 224))
    F.append(arrow(1008, 391, 1092, 296))

    # результат осідає в TLB
    F.append(line(1171, 304, 1171, 480, color=FIELD, sw=1.6, dash="6 5"))
    F.append(line(1171, 480, 289, 480, color=FIELD, sw=1.6, dash="6 5"))
    F.append(arrow(289, 480, 289, 312, color=FIELD))
    F.append(text(700, 508, "знайдений переклад осідає в TLB — наступні звернення "
                            "в цю саму сторінку йдуть коротким шляхом",
                  size=13, color=FIELD))

    return render(os.path.join(IMG, "tlb-path.svg"), W, H, *F,
                  title="один переклад: коротким шляхом і довгим")


# ── 3. Два читання одного запису таблиці ───────────────────────────────────
def fig_pte_bits():
    W, H = 1300, 580
    F = []

    F.append(text(70, 68, "біт присутності = 1 — запис читає апаратура",
                  size=15, bold=True, anchor="start"))
    RY, RH = 84, 66
    F.append(fitbox(70, RY, 70, RH, "NX\n63", size=13, fill=RED_F))
    F.append(fitbox(140, RY, 110, RH, "ключ\n62…59", size=13, fill=FILL))
    F.append(fitbox(250, RY, 120, RH, "вільні для ОС\n58…52", size=12, fill=FILL))
    F.append(fitbox(370, RY, 580, RH, "номер кадру · біти 51…12", size=16, fill=BLU_F))
    F.append(fitbox(950, RY, 280, RH, "прапорці\n11…0", size=13, fill=YEL_F))

    # збільшення: прапорці прав і стану, розкидані по всьому запису
    F.append(line(70, RY + RH, 300, 240, color=MUTED, sw=1.1, dash="5 4"))
    F.append(line(1230, RY + RH, 1230, 240, color=MUTED, sw=1.1, dash="5 4"))

    flags = [
        "NX · біт 63\nне виконувати",
        "D · біт 6\nзмінена",
        "A · біт 5\nдо неї зверталися",
        "U/S · біт 2\nвидно програмі",
        "R/W · біт 1\nможна писати",
        "P · біт 0\nприсутня",
    ]
    fx, fw = 300, 155
    for i, s in enumerate(flags):
        fill = RED_F if i == len(flags) - 1 else YEL_F
        F.append(fitbox(fx + i * fw, 242, fw - 6, 74, s, size=12, pad=6, fill=fill))

    F.append(text(70, 400, "біт присутності = 0 — апаратура спиняється, "
                           "решта бітів належить ядру",
                  size=15, bold=True, anchor="start"))
    F.append(fitbox(70, 416, 1105, 66,
                    "де шукати вміст: тип пристрою підкачки + номер слоту",
                    size=16, fill=GRN_F))
    F.append(fitbox(1175, 416, 55, 66, "0", size=16, fill=RED_F))

    F.append(text(650, 524, "той самий запис: поки біт стоїть — його тлумачить MMU, "
                            "щойно скинуто — тільки ядро",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "pte-bits.svg"), W, H, *F,
                  title="запис таблиці сторінок — 64 біти на дві ролі")


# ── 4. Ціна таблиці: плоска проти розрідженого дерева ──────────────────────
def fig_table_cost():
    W, H = 1300, 690
    F = []

    # ліворуч — перепис вузлів по рівнях
    F.append(text(185, 62, "рівень дерева", size=13, color=MUTED, bold=True))
    F.append(text(385, 62, "таблиць", size=13, color=MUTED, bold=True))
    F.append(text(545, 62, "покриває одна", size=13, color=MUTED, bold=True))

    levels = [
        ("рівень 1 · корінь", "1", "256 ТіБ"),
        ("рівень 2", "3", "512 ГіБ"),
        ("рівень 3", "3", "1 ГіБ"),
        ("рівень 4 · листя", "147", "2 МіБ"),
    ]
    for i, (name, cnt, cover) in enumerate(levels):
        y = 82 + i * 84
        fill = YEL_F if i == 3 else BLU_F
        F.append(fitbox(60, y, 250, 64, name, size=15, fill=fill))
        F.append(fitbox(330, y, 110, 64, cnt, size=18, fill=BG, bold=True))
        F.append(fitbox(460, y, 170, 64, cover, size=15, fill=FILL))

    # праворуч — звідки взялися 149 таблиць листя
    F.append(text(960, 62, "звідки беруться таблиці листя",
                  size=13, color=MUTED, bold=True))
    leafs = [
        ("код і дані виконуваного файлу · 6 МіБ", "4"),
        ("купа · 64 МіБ", "33"),
        ("бібліотеки й завантажувач · 9 МіБ", "9"),
        ("файл через mmap · 200 МіБ", "101"),
        ("стек · торкнуто 128 КіБ", "1"),
        ("vdso й vvar · 8 КіБ", "1"),
    ]
    for i, (name, cnt) in enumerate(leafs):
        y = 82 + i * 54
        F.append(fitbox(690, y, 390, 44, name, size=14, pad=10, fill=FILL))
        F.append(fitbox(1100, y, 140, 44, cnt, size=16, fill=YEL_F, bold=True))

    F.append(text(960, 424,
                  "сума 149, мінус два вікна, спільні на стиках → 147",
                  size=13, color=MUTED))

    # підсумок
    F.append(fitbox(60, 452, 570, 92,
                    "розріджене дерево\n154 сторінки = 616 КіБ",
                    size=18, fill=GRN_F))
    F.append(fitbox(690, 452, 550, 92,
                    "плоска таблиця\n2³⁶ записів × 8 Б = 512 ГіБ",
                    size=18, fill=RED_F))

    F.append(text(650, 590, "616 КіБ проти 512 ГіБ — у 870 000 разів менше",
                  size=18, bold=True))
    F.append(text(650, 624,
                  "дерево платить лише за ті вікна по 2 МіБ, у яких справді щось відображено",
                  size=14, color=MUTED))
    F.append(text(650, 654,
                  "надлишок над підлогою «8 байтів на сторінку» — усього десята частина",
                  size=14, color=MUTED))

    return render(os.path.join(IMG, "table-cost.svg"), W, H, *F,
                  title="ціна таблиці для одного звичайного процесу")


# ── 5. Обхват TLB і три смуги робочої множини ──────────────────────────────
def fig_tlb_reach():
    W, H = 1300, 590
    F = []

    X0, X1 = 90.0, 1210.0          # 1 МіБ … 1 ТіБ, крок — подвоєння
    K = (X1 - X0) / 20.0

    def px(log2_mib):
        return X0 + K * log2_mib

    x_reach = px(2.5849625)        # 6 МіБ
    x_dram = px(14.0)              # 16 ГіБ

    BY, BH = 120, 72
    F.append(fitbox(X0, BY, x_reach - X0, BH, "усе в TLB", size=14, pad=6, fill=GRN_F))
    F.append(fitbox(x_reach, BY, x_dram - x_reach, BH,
                    "обхід читає таблиці з кешу", size=14, fill=YEL_F))
    F.append(fitbox(x_dram, BY, X1 - x_dram, BH, "обхід іде в DRAM",
                    size=14, fill=RED_F))

    ticks = [(0.0, "1 МіБ"), (2.5849625, "6 МіБ"), (6.0, "64 МіБ"),
             (10.0, "1 ГіБ"), (14.0, "16 ГіБ"), (20.0, "1 ТіБ")]
    for lg, lab in ticks:
        x = px(lg)
        F.append(line(x, BY + BH, x, BY + BH + 12, color=MUTED, sw=1.2))
        F.append(text(x, BY + BH + 32, lab, size=13, color=MUTED))

    F.append(text(650, 262, "робоча множина процесу, логарифмічна шкала",
                  size=13, color=MUTED))

    rows = [
        (GRN_F, FIELD,
         "множина ≤ 6 МіБ — це рівно обхват: 1536 записів × 4 КіБ.\n"
         "промахи поодинокі, переклад не коштує майже нічого"),
        (YEL_F, "#b8860b",
         "6 МіБ < множина ≤ 512 · L3 ≈ 16 ГіБ — промах майже на кожному зверненні,\n"
         "але таблиці листя (множина / 512) ще вміщаються в L3: обхід коштує 20–30 тактів"),
        (RED_F, POS,
         "множина > 512 · L3 — таблиці листя більші за L3, обхід сам іде в DRAM:\n"
         "переклад коштує стільки ж, скільки саме звернення до даних"),
    ]
    for i, (fill, stroke, txt) in enumerate(rows):
        y = 296 + i * 76
        F.append(rect(90, y, 42, 58, fill=fill, stroke=stroke, sw=1.6))
        F.append(fitbox(152, y, 1058, 58, txt, size=14, fill=BG, stroke=MUTED, sw=1.0))

    F.append(text(650, 556,
                  "сторінки на 2 МіБ зсувають обидва пороги: обхват 3 ГіБ, друга межа ≈ 8 ТіБ",
                  size=14, color=MUTED))

    return render(os.path.join(IMG, "tlb-reach.svg"), W, H, *F,
                  title="обхват TLB і три смуги робочої множини (сторінки 4 КіБ)")


# ── 6. Три різновиди запису x86-64, біт за бітом (вставка api) ─────────────
def _bitrow(x0, y, cells, num_y, size=13):
    """Смуга бітових полів: cells = [(ширина, підпис бітів, текст, заливка)].
    Номери бітів — над коміркою, назва поля — всередині."""
    out = []
    x = x0
    for w, bits, txt, fill in cells:
        out.append(fitbox(x, y, w, 54, txt, size=size, pad=5, fill=fill))
        out.append(text(x + w / 2, num_y, bits, size=11, color=MUTED))
        x += w
    return out


def fig_pte_variants():
    W, H = 1400, 512
    F = []
    X0 = 45

    PERM = "#fdecea"   # права доступу
    ADDR = "#eaf0fd"   # адреса
    SOFT = "#fff5e0"   # вільне для ОС
    HW   = "#eafaf0"   # ставить апаратура

    # ── кінцевий запис на 4 КіБ ──
    F.append(text(X0, 70, "кінцевий запис PTE — сторінка на 4 КіБ",
                  size=15, bold=True, anchor="start"))
    F += _bitrow(X0, 104, [
        (48,  "63",     "XD",                        PERM),
        (132, "62…59",  "ключ\nзахисту",             SOFT),
        (170, "58…52",  "вільні\nдля ОС",            SOFT),
        (340, "51…12",  "номер кадру",               ADDR),
        (160, "11…9",   "вільні\nдля ОС",            SOFT),
        (48,  "8",      "G",                         FILL),
        (52,  "7",      "PAT",                       FILL),
        (48,  "6",      "D",                         HW),
        (48,  "5",      "A",                         HW),
        (52,  "4",      "PCD",                       FILL),
        (52,  "3",      "PWT",                       FILL),
        (52,  "2",      "U/S",                       PERM),
        (52,  "1",      "R/W",                       PERM),
        (48,  "0",      "P",                         PERM),
    ], 96)

    # ── проміжний запис із PS = 1 (велика сторінка на 2 МіБ) ──
    F.append(text(X0, 198, "запис рівня PMD із PS = 1 — велика сторінка на 2 МіБ",
                  size=15, bold=True, anchor="start"))
    F += _bitrow(X0, 232, [
        (48,  "63",     "XD",                 PERM),
        (132, "62…59",  "ключ\nзахисту",      SOFT),
        (170, "58…52",  "вільні\nдля ОС",     SOFT),
        (200, "51…21",  "номер кадру",        ADDR),
        (90,  "20…13",  "нулі",               BG),
        (50,  "12",     "PAT",                FILL),
        (160, "11…9",   "вільні\nдля ОС",     SOFT),
        (48,  "8",      "G",                  FILL),
        (52,  "7",      "PS=1",               HW),
        (48,  "6",      "D",                  HW),
        (48,  "5",      "A",                  HW),
        (52,  "4",      "PCD",                FILL),
        (52,  "3",      "PWT",                FILL),
        (52,  "2",      "U/S",                PERM),
        (52,  "1",      "R/W",                PERM),
        (48,  "0",      "P",                  PERM),
    ], 224)

    # ── запис, що вказує на таблицю нижчого рівня ──
    F.append(text(X0, 326, "запис, що вказує на таблицю нижчого рівня (PS = 0)",
                  size=15, bold=True, anchor="start"))
    F += _bitrow(X0, 360, [
        (48,  "63",     "XD",                          PERM),
        (302, "62…52",  "ігноровані апаратурою",       SOFT),
        (340, "51…12",  "фізична адреса\nтаблиці",     ADDR),
        (208, "11…8",   "ігноровані",                  SOFT),
        (52,  "7",      "PS=0",                        HW),
        (48,  "6",      "—",                           BG),
        (48,  "5",      "A",                           HW),
        (52,  "4",      "PCD",                         FILL),
        (52,  "3",      "PWT",                         FILL),
        (52,  "2",      "U/S",                         PERM),
        (52,  "1",      "R/W",                         PERM),
        (48,  "0",      "P",                           PERM),
    ], 352)

    F.append(text(W / 2, 452,
                  "рожеве — права доступу, синє — адреса, жовте — вільне для ядра, "
                  "зелене — ставить сама апаратура",
                  size=13, color=MUTED))
    F.append(text(W / 2, 480,
                  "верхня межа поля адреси — MAXPHYADDR процесора (не більше за біт 51); "
                  "біти вище неї мусять бути нулями",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "pte-variants.svg"), W, H, *F,
                  title="три різновиди запису таблиці на x86-64")


# ── 7. CR3 і відсутній запис під підкачку (вставка api) ────────────────────
def fig_cr3_and_swap():
    W, H = 1400, 560
    F = []
    X0 = 45
    ADDR = "#eaf0fd"
    SOFT = "#fff5e0"
    PERM = "#fdecea"
    HW   = "#eafaf0"

    F.append(text(X0, 70, "CR3, коли CR4.PCIDE = 0", size=15, bold=True, anchor="start"))
    F += _bitrow(X0, 104, [
        (200, "63…52", "нулі",                              BG),
        (570, "51…12", "фізична адреса кореневої таблиці",  ADDR),
        (190, "11…5",  "ігноровані",                        SOFT),
        (80,  "4",     "PCD",                               FILL),
        (80,  "3",     "PWT",                               FILL),
        (170, "2…0",   "ігноровані",                        SOFT),
    ], 96)

    F.append(text(X0, 198, "CR3, коли CR4.PCIDE = 1", size=15, bold=True, anchor="start"))
    F += _bitrow(X0, 232, [
        (140, "63",    "NOFLUSH",                           HW),
        (140, "62…52", "нулі",                              BG),
        (570, "51…12", "фізична адреса кореневої таблиці",  ADDR),
        (440, "11…0",  "PCID — мітка адресного простору",   SOFT),
    ], 224)

    F.append(line(X0, 314, W - X0, 314, color=MUTED, sw=1.0, dash="6 5"))

    F.append(text(X0, 356, "відсутній запис (P = 0): опис місця в підкачці, "
                           "як його кодує Linux на x86-64",
                  size=15, bold=True, anchor="start"))
    F += _bitrow(X0, 392, [
        (230, "63…59", "тип — номер\nобласті підкачки", HW),
        (520, "58…9",  "зміщення, записане\nінверсією", ADDR),
        (60,  "8",     "0",  PERM),
        (60,  "7",     "0",  BG),
        (60,  "6",     "×",  BG),
        (60,  "5",     "×",  BG),
        (60,  "4",     "×",  BG),
        (60,  "3",     "E",  SOFT),
        (60,  "2",     "F",  SOFT),
        (60,  "1",     "SD", SOFT),
        (60,  "0",     "0",  PERM),
    ], 384)

    F.append(text(W / 2, 490,
                  "SD — soft-dirty · F — захист від запису через userfaultfd · "
                  "E — сторінка належить одному процесу",
                  size=13, color=MUTED))
    F.append(text(W / 2, 516,
                  "× — біти 6…4 ядро свідомо не займає: на Knights Landing апаратура "
                  "вміла псувати A і D у відсутньому записі",
                  size=13, color=MUTED))
    F.append(text(W / 2, 542,
                  "нуль у біті 8 відрізняє запис підкачки від позначки PROT_NONE, "
                  "нуль у біті 0 спиняє апаратуру",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "cr3-and-swap.svg"), W, H, *F,
                  title="корінь дерева і запис, який апаратура вже не читає")


# ── 4. Слово pagemap: 64 біти, які ядро віддає про сторінку ────────────────
def fig_pagemap_word():
    W, H = 1340, 660
    F = []

    BX, BY, BH = 60, 62, 72
    cells = [
        (60, 86, "63\nP"),
        (146, 86, "62\nSw"),
        (232, 86, "61\nF"),
        (318, 96, "60…58"),
        (414, 86, "57\nwp"),
        (500, 86, "56\nex"),
        (586, 86, "55\nsd"),
        (672, 608, "біти 54…0\nкорисне навантаження"),
    ]
    for x, w, s in cells:
        fill = BLU_F if x == 672 else YEL_F
        F.append(fitbox(x, BY, w, BH, s, size=14, pad=6, fill=fill))

    F.append(text(60, 172, "старші біти — прапорці стану; молодші 55 читають "
                           "по-різному, залежно від бітів 63 і 62:",
                  size=14, color=MUTED, anchor="start"))

    rows = [
        ("біт 63 = 1\nсторінка присутня", GRN_F,
         [(340, 940, "номер кадру — біти 54…0     (нулі, якщо немає CAP_SYS_ADMIN)", BLU_F)]),
        ("біт 62 = 1\nвміст у підкачці", YEL_F,
         [(340, 620, "номер слоту — біти 54…5", FILL),
          (980, 300, "тип пристрою — біти 4…0", FILL)]),
        ("обидва = 0\nкадру немає", RED_F,
         [(340, 940, "усе слово нульове — сторінки ще не торкалися", FILL)]),
    ]
    ry, rh = 196, 68
    for i, (lab, lfill, boxes) in enumerate(rows):
        y = ry + i * (rh + 16)
        F.append(fitbox(60, y, 260, rh, lab, size=13, pad=6, fill=lfill))
        for x, w, s, fill in boxes:
            F.append(fitbox(x, y, w, rh, s, size=14, pad=8, fill=fill))

    LY = 460
    F.append(line(60, LY - 18, 1280, LY - 18, color=MUTED, sw=1.0, dash="5 4"))
    left = [
        "63 P — сторінка присутня, кадр існує",
        "62 Sw — вміст витіснено в підкачку",
        "61 F — файлова або спільна анонімна",
        "60…59 — зарезервовано, завжди нулі",
    ]
    right = [
        "58 — сторожова ділянка (з ядра 6.15)",
        "57 wp — запис перехоплює userfaultfd (з 5.13)",
        "56 ex — на кадр дивиться лише це відображення (з 4.2)",
        "55 sd — сторінку чіпали після скидання лічильника",
    ]
    for i, s in enumerate(left):
        F.append(text(60, LY + 14 + i * 28, s, size=14, color=MUTED, anchor="start"))
    for i, s in enumerate(right):
        F.append(text(690, LY + 14 + i * 28, s, size=14, color=MUTED, anchor="start"))

    F.append(text(670, LY + 158,
                  "зміщення потрібного слова у файлі = (адреса / розмір сторінки) · 8",
                  size=15, bold=True))

    return render(os.path.join(IMG, "pagemap-word.svg"), W, H, *F,
                  title="8 байтів /proc/<pid>/pagemap про одну віртуальну сторінку")


# ── 5. Копіювання при записі очима pagemap ─────────────────────────────────
def fig_cow_frames():
    W, H = 1340, 560
    F = []

    F.append(line(452, 56, 452, 470, color=MUTED, sw=1.1, dash="6 5"))
    F.append(line(896, 56, 896, 470, color=MUTED, sw=1.1, dash="6 5"))

    heads = [(246, "1 · до fork"), (674, "2 · після fork"),
             (1118, "3 · дитина написала")]
    for cx, s in heads:
        F.append(text(cx, 82, s, size=16, bold=True))

    # ── панель 1
    F.append(fitbox(56, 168, 180, 70, "батько\nva 0x…a000", size=13, fill=FILL))
    F.append(arrow(240, 203, 266, 203))
    F.append(fitbox(270, 168, 150, 70, "кадр A", size=15, fill=BLU_F))
    F.append(text(246, 288, "біт 56 = 1 · «власна»", size=14, color=FIELD))

    # ── панель 2
    F.append(fitbox(486, 116, 180, 70, "батько\nva 0x…a000", size=13, fill=FILL))
    F.append(fitbox(486, 226, 180, 70, "дитина\nva 0x…a000", size=13, fill=FILL))
    F.append(fitbox(714, 168, 150, 70, "кадр A", size=15, fill=BLU_F))
    F.append(arrow(670, 151, 710, 190))
    F.append(arrow(670, 261, 710, 216))
    F.append(text(674, 316, "біт 56 = 0 · «спільна»", size=14, color=POS))
    F.append(text(674, 344, "право запису знято в обох", size=13, color=MUTED))

    # ── панель 3
    F.append(fitbox(926, 116, 180, 70, "батько\nva 0x…a000", size=13, fill=FILL))
    F.append(fitbox(926, 226, 180, 70, "дитина\nva 0x…a000", size=13, fill=FILL))
    F.append(arrow(1110, 151, 1146, 151))
    F.append(arrow(1110, 261, 1146, 261))
    F.append(fitbox(1150, 116, 150, 70, "кадр A", size=15, fill=BLU_F))
    F.append(fitbox(1150, 226, 150, 70, "кадр B", size=15, fill=GRN_F))
    F.append(text(1118, 344, "у кожного знову «власна»", size=14, color=FIELD))

    F.append(line(60, 402, 1280, 402, color=MUTED, sw=1.0, dash="5 4"))
    F.append(text(670, 438,
                  "віртуальна адреса в усіх трьох станах та сама — змінюється лише те, "
                  "у який кадр вона веде",
                  size=15, bold=True))
    F.append(text(670, 476,
                  "перший же запис у спільну сторінку робить кадр-копію: "
                  "далі батько й дитина бачать різні дані за однією адресою",
                  size=14, color=MUTED))

    return render(os.path.join(IMG, "cow-frames.svg"), W, H, *F,
                  title="один кадр на двох — і як він розділяється на записі")


if __name__ == "__main__":
    print(fig_translate())
    print(fig_tlb_path())
    print(fig_pte_bits())
    print(fig_pagemap_word())
    print(fig_cow_frames())
    print(fig_table_cost())
    print(fig_tlb_reach())
    print(fig_pte_variants())
    print(fig_cr3_and_swap())
