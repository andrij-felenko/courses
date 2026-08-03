# -*- coding: utf-8 -*-
"""Фігури для теми «Великі сторінки: HugeTLB і прозорі великі сторінки»."""
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


# ── 1. На якому рівні зупинити переклад ────────────────────────────────────
def fig_leaf_level():
    W, H = 1400, 580
    F = []

    BX, BW = 220, 880          # смуга адреси
    PER_BIT = BW / 48.0
    ROW_H = 84
    rows = [
        (104, "кінцевий запис\nна 4-му рівні", 4, 12, "сторінка 4 КіБ",
         "обхват при 2048\nзаписах TLB:\n8 МіБ"),
        (244, "кінцевий запис\nна 3-му рівні", 3, 21, "сторінка 2 МіБ",
         "обхват при 2048\nзаписах TLB:\n4 ГіБ"),
        (384, "кінцевий запис\nна 2-му рівні", 2, 30, "сторінка 1 ГіБ",
         "обхват при 2048\nзаписах TLB:\n2 ТіБ"),
    ]

    for y, left, levels, off_bits, name, reach in rows:
        F.append(fitbox(30, y, 172, ROW_H, left, size=13, fill=FILL))
        x = BX
        for i in range(levels):
            w = 9 * PER_BIT
            last = (i == levels - 1)
            F.append(fitbox(x, y, w - 4, ROW_H,
                            "рівень %d\n9 біт" % (i + 1), size=13,
                            fill=(YEL_F if last else BLU_F),
                            stroke=(POS if last else LINE),
                            sw=(2.0 if last else 1.5)))
            x += w
        F.append(fitbox(x, y, BX + BW - x, ROW_H,
                        "зміщення у сторінці · %d біт" % off_bits, size=13,
                        fill=GRN_F))
        F.append(text(BX + BW / 2, y + ROW_H + 26, name, size=14, bold=True))
        F.append(fitbox(1130, y, 240, ROW_H, reach, size=13, fill=FILL))

    F.append(text(W / 2, 532,
                  "біти, які більше нікого не індексують, приєднуються до зміщення — "
                  "саме звідси беруться розміри сторінок",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "leaf-level.svg"), W, H, *F,
                  title="одна адреса, три місця зупинки перекладу")


# ── 2. Дві відповіді на потребу в суцільності ──────────────────────────────
def fig_two_answers():
    W, H = 1320, 620
    F = []

    LX, LW = 30, 268           # стовпчик питань
    AX, AW = 320, 470          # HugeTLB
    BX, BW = 812, 470          # THP

    F.append(fitbox(AX, 56, AW, 62, "HugeTLB — пул, відрізаний наперед",
                    size=15, bold=True, fill=BLU_F))
    F.append(fitbox(BX, 56, BW, 62, "THP — прозорі сторінки на льоту",
                    size=15, bold=True, fill=GRN_F))

    rows = [
        ("звідки береться\nпам'ять",
         "кадри вилучені з обігу\nй недоступні нікому іншому",
         "звичайна пам'ять,\nблок збирається в роботі"),
        ("хто платить\nза суцільність",
         "адміністратор, до запуску,\nодин раз",
         "процес, посеред збою,\nщоразу заново"),
        ("що буде,\nякщо не вдалося",
         "SIGBUS у процесі\nабо відмова стартувати",
         "мовчки беруться\nдрібні сторінки"),
        ("чи можна\nзабрати назад",
         "ні: не витісняється,\nне розбивається",
         "так: розбивається\nй витісняється"),
        ("хто вирішує",
         "програма просить явно\n(hugetlbfs, MAP_HUGETLB)",
         "ядро вирішує саме,\nпрограма може порадити"),
    ]

    y = 142
    for q, a, b in rows:
        F.append(fitbox(LX, y, LW, 78, q, size=13, fill=FILL))
        F.append(fitbox(AX, y, AW, 78, a, size=13, fill=BLU_F))
        F.append(fitbox(BX, y, BW, 78, b, size=13, fill=GRN_F))
        y += 92

    F.append(text(W / 2, 596,
                  "кінцевий запис у таблиці в обох випадках однаковий — "
                  "різниця тільки в ціні та в тому, хто її платить",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "two-answers.svg"), W, H, *F,
                  title="два способи дістати суцільний блок на 2 МіБ")


# ── 3. Життя прозорої великої сторінки ─────────────────────────────────────
def _strip(x, y, w, h, n, fill, stroke=LINE, dash_fill=None):
    """Смужка з n однакових комірок — образ дрібних сторінок."""
    out = []
    gap = 5
    cw = (w - (n - 1) * gap) / n
    for i in range(n):
        out.append(rect(x + i * (cw + gap), y, cw, h,
                        fill=(dash_fill if dash_fill else fill),
                        stroke=stroke, sw=1.2, rx=3))
    return "".join(out)


def fig_thp_lifecycle():
    W, H = 1300, 700
    F = []

    SX, SW = 270, 250          # ліва фігура
    EX, EW = 700, 250          # права фігура
    NX, NW = 980, 270          # примітка про ціну

    panels = [
        (66, "народження\nна збої",
         "порожнє вирівняне вікно", "cells-empty",
         "одна велика сторінка", "big",
         "збій на першій\nадресі у вікні",
         "потрібен вільний\nсуцільний блок;\nінакше — дрібні сторінки"),
        (278, "згортання\n(khugepaged)",
         "512 присутніх дрібних сторінок", "cells-full",
         "одна велика сторінка", "big",
         "копіювання\nдвох мегабайтів",
         "фонова робота:\nвміст переїжджає,\nадреси лишаються"),
        (490, "розбиття",
         "одна велика сторінка", "big",
         "512 записів у ті самі кадри", "cells-full",
         "mprotect або munmap\nна частину вікна",
         "нічого не копіюється:\nміняється лише\nформа запису"),
    ]

    for y0, title, lcap, lkind, rcap, rkind, mid, note in panels:
        F.append(fitbox(30, y0 + 22, 210, 96, title, size=14, bold=True, fill=FILL))

        for x, w, cap, kind in ((SX, SW, lcap, lkind), (EX, EW, rcap, rkind)):
            if kind == "big":
                F.append(rect(x, y0 + 34, w, 58, fill=YEL_F, stroke=POS, sw=2))
                F.append(text(x + w / 2, y0 + 69, "2 МіБ одним записом",
                              size=13, color=INK))
            elif kind == "cells-full":
                F.append(_strip(x, y0 + 34, w, 58, 8, BLU_F))
            else:
                F.append(_strip(x, y0 + 34, w, 58, 8, BG, stroke=MUTED))
            F.append(text(x + w / 2, y0 + 122, cap, size=12, color=MUTED))

        F.append(arrow(SX + SW + 26, y0 + 63, EX - 26, y0 + 63))
        F.append(fitbox(SX + SW + 5, y0 + 84, EX - SX - SW - 10, 44,
                        mid, size=11, fill=BG, stroke=BG, color=FIELD))

        F.append(fitbox(NX, y0 + 22, NW, 96, note, size=12, fill=FILL))

    F.append(text(W / 2, 664,
                  "адреси процесу не змінюються в жодному з трьох випадків — "
                  "змінюється тільки те, як їх описано в таблиці",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "thp-lifecycle.svg"), W, H, *F,
                  title="три події з життя прозорої великої сторінки")


# ── 4. Дві лінії: апаратна й ядрова ────────────────────────────────────────
def fig_timeline():
    W, H = 1520, 640
    F = []
    AX = 330
    X0, X1 = 160, 1400
    BW, BH = 164, 122

    ev = [
        ("1993", "hw", "Pentium, прапорець PSE:\nсторінка 4 МіБ\nу 32-бітному режимі"),
        ("1995", "hw", "Pentium Pro, PAE:\nвелика сторінка\nстає 2 МіБ"),
        ("2002", "os", "гілка 2.5: hugetlbfs,\nпул, порахований\nнаперед"),
        ("2007", "hw", "AMD родина 10h:\nсторінка 1 ГіБ\n(CPUID pdpe1gb)"),
        ("2008", "os", "2.6.26: гігабайтні\nсторінки в ядрі"),
        ("2011", "os", "2.6.38: прозорі великі\nсторінки, khugepaged"),
        ("2022", "os", "6.1: MADV_COLLAPSE —\nзбирання на вимогу"),
        ("2024", "os", "6.8 і 6.10: проміжні\nрозміри (mTHP)"),
    ]

    F.append(line(X0 - 60, AX, X1 + 60, AX, color=MUTED, sw=2))

    step = (X1 - X0) / float(len(ev) - 1)
    for i, (year, kind, txt) in enumerate(ev):
        cx = X0 + i * step
        up = (kind == "hw")
        F.append(circle(cx, AX, 7, fill=(NEG if up else FIELD),
                        stroke=(NEG if up else FIELD)))
        F.append(text(cx, AX + (-26 if up else 44), year, size=15, bold=True))
        by = (AX - 52 - BH) if up else (AX + 62)
        y_from = (AX - 36) if up else (AX + 52)
        y_to = (by + BH) if up else by
        F.append(line(cx, y_from, cx, y_to, color=MUTED, sw=1.2, dash="4,4"))
        F.append(fitbox(cx - BW / 2, by, BW, BH, txt, size=12,
                        fill=(BLU_F if up else GRN_F)))

    F.append(text(W / 2, H - 28,
                  "згори — апаратура, знизу — ядро; апаратура вміла великі сторінки за дев'ять років до того, "
                  "як їх почало роздавати ядро",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "huge-pages-timeline.svg"), W, H, *F,
                  title="дві незалежні лінії великих сторінок")



# ── 5. Кодування розміру в бітах прапорців (вставка api) ───────────────────
def fig_huge_flag_bits():
    W, H = 1180, 430
    F = []

    X0, X1 = 70, W - 70
    BY, BH = 92, 68
    SPLIT = X0 + (X1 - X0) * 6.0 / 32.0     # шість старших бітів із тридцяти двох

    F.append(rect(X0, BY, X1 - X0, BH, fill=BG, stroke=LINE, sw=2))
    F.append(rect(X0, BY, SPLIT - X0, BH, fill=YEL_F, stroke=LINE, sw=2))
    F.append(line(SPLIT, BY, SPLIT, BY + BH, color=LINE, sw=2))

    F.append(text((X0 + SPLIT) / 2, BY + BH / 2 + 6, "log₂(розмір)", size=16, bold=True))
    F.append(text((SPLIT + X1) / 2, BY + BH / 2 + 6,
                  "звичайні прапорці виклику (MAP_PRIVATE, MAP_ANONYMOUS, MAP_HUGETLB…)",
                  size=15))

    F.append(text(X0, BY - 16, "біт 31", size=13, color=MUTED, anchor="start"))
    F.append(text(SPLIT, BY - 16, "біт 26", size=13, color=MUTED, anchor="middle"))
    F.append(text(X1, BY - 16, "біт 0", size=13, color=MUTED, anchor="end"))

    F.append(text((X0 + SPLIT) / 2, BY + BH + 30, "шість бітів", size=13, color=MUTED))

    # приклади значень
    ROW = 235
    CW, CH = 240, 78
    GAP = (X1 - X0 - 4 * CW) / 3.0
    cells = [
        ("0", "розмір за домовленістю", "(Hugepagesize)"),
        ("16", "64 КіБ", "ARM64, гранула 4 КіБ"),
        ("21", "2 МіБ", "MAP_HUGE_2MB"),
        ("30", "1 ГіБ", "MAP_HUGE_1GB"),
    ]
    for i, (val, size_s, note) in enumerate(cells):
        x = X0 + i * (CW + GAP)
        F.append(fitbox(x, ROW, CW, CH,
                        ["log₂ = " + val, size_s, note], size=14,
                        fill=(GRN_F if i else FILL)))

    F.append(text(W / 2, ROW + CH + 46,
                  "flags |= (21 << MAP_HUGE_SHIFT)   —   MAP_HUGE_SHIFT = 26, MAP_HUGE_MASK = 0x3f",
                  size=16, bold=True))
    F.append(text(W / 2, ROW + CH + 76,
                  "той самий зсув і та сама шістка бітів у SHM_HUGE_SHIFT для shmget і MFD_HUGE_SHIFT для memfd_create",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "huge-flag-bits.svg"), W, H, *F,
                  title="розмір сторінки, зашитий у слово прапорців")


# ── 6. Що саме рахують лічильники пулу (вставка api) ───────────────────────
def fig_pool_accounting():
    W, H = 1180, 440
    F = []

    X0, X1 = 70, W - 70
    BY, BH = 118, 72
    S1 = X0 + 0.40 * (X1 - X0)
    S2 = X0 + 0.64 * (X1 - X0)

    F.append(fitbox(X0, BY, S1 - X0, BH, ["роздані й заповнені", "процесами"],
                    size=14, fill=BLU_F))
    F.append(fitbox(S1, BY, S2 - S1, BH, ["обіцяні", "(Rsvd)"], size=14, fill=YEL_F))
    F.append(fitbox(S2, BY, X1 - S2, BH, ["нікому не обіцяні", "й нічим не зайняті"],
                    size=14, fill=GRN_F))

    # верхня дужка — Total
    TY = BY - 30
    F.append(line(X0, TY, X1, TY, color=LINE, sw=1.6))
    F.append(line(X0, TY, X0, TY + 12, color=LINE, sw=1.6))
    F.append(line(X1, TY, X1, TY + 12, color=LINE, sw=1.6))
    F.append(text((X0 + X1) / 2, TY - 12, "HugePages_Total  =  nr_hugepages  (+ Surp)",
                  size=16, bold=True))

    # нижня дужка — Free
    FY = BY + BH + 34
    F.append(line(S1, FY, X1, FY, color=FIELD, sw=1.6))
    F.append(line(S1, FY, S1, FY - 12, color=FIELD, sw=1.6))
    F.append(line(X1, FY, X1, FY - 12, color=FIELD, sw=1.6))
    F.append(text((S1 + X1) / 2, FY + 24, "HugePages_Free", size=16, bold=True, color=FIELD))

    lines = [
        "HugePages_Free  включає  HugePages_Rsvd  —  обіцяне лежить вільним, але вже нічиє",
        "справді доступно новому охочому  =  HugePages_Free − HugePages_Rsvd",
        "HugePages_Surp  —  узяте понад nr_hugepages динамічно, стеля  =  nr_overcommit_hugepages",
        "Hugetlb (кБ)  =  Σ по всіх розмірах  HugePages_Total · розмір  —  скільки пам'яті вилучено із системи",
    ]
    ly = FY + 66
    for i, s in enumerate(lines):
        F.append(text(X0, ly + i * 27, s, size=14, anchor="start",
                      color=(INK if i < 2 else MUTED)))

    return render(os.path.join(IMG, "pool-accounting.svg"), W, H, *F,
                  title="чотири числа пулу HugeTLB і що між ними спільного")


# ── 7. Чому вимірювати треба залежним ланцюгом (вставка proj) ──────────────
def fig_chase_vs_parallel():
    W, H = 1320, 600
    F = []

    TX = 340          # ліва межа «осі часу»
    L = 108           # довжина одного звернення
    BH = 19
    STEP = 26
    N = 6

    # верхня половина: незалежні звернення накладаються одне на одне
    F.append(text(30, 54,
                  "незалежні звернення: усі адреси відомі наперед, "
                  "процесор запускає їх майже одночасно",
                  size=15, bold=True, anchor="start"))
    y0 = 76
    for i in range(N):
        x = TX + i * 12
        y = y0 + i * STEP
        F.append(rect(x, y, L, BH, fill=BLU_F, stroke=NEG, sw=1.2, rx=4))
        F.append(text(TX - 18, y + BH - 4, "звернення %d" % (i + 1),
                      size=12, color=MUTED, anchor="end"))
    end_top = TX + (N - 1) * 12 + L
    yb = y0 + N * STEP + 4
    F.append(line(TX, yb, end_top, yb, color=NEG, sw=2))
    F.append(line(TX, yb - 8, TX, yb + 8, color=NEG, sw=2))
    F.append(line(end_top, yb - 8, end_top, yb + 8, color=NEG, sw=2))
    F.append(text(end_top + 22, yb + 5,
                  "шість затримок наклалися майже в одну",
                  size=13, color=NEG, anchor="start"))

    # нижня половина: залежний ланцюг
    F.append(text(30, 320,
                  "залежний ланцюг: адреса наступного звернення лежить "
                  "у даних попереднього",
                  size=15, bold=True, anchor="start"))
    y1 = 342
    for i in range(N):
        x = TX + i * L
        y = y1 + i * STEP
        F.append(rect(x, y, L, BH, fill=RED_F, stroke=POS, sw=1.2, rx=4))
        F.append(text(TX - 18, y + BH - 4, "звернення %d" % (i + 1),
                      size=12, color=MUTED, anchor="end"))
        if i < N - 1:
            F.append(line(x + L, y + BH, x + L, y + STEP,
                          color=MUTED, sw=1.2, dash="3,3"))
    end_bot = TX + N * L
    yc = y1 + N * STEP + 4
    F.append(line(TX, yc, end_bot, yc, color=POS, sw=2))
    F.append(line(TX, yc - 8, TX, yc + 8, color=POS, sw=2))
    F.append(line(end_bot, yc - 8, end_bot, yc + 8, color=POS, sw=2))
    F.append(text(end_bot + 22, yc + 5, "шість затримок поспіль",
                  size=13, color=POS, anchor="start"))

    F.append(text(W / 2, H - 26,
                  "поділивши час на кількість звернень, угорі дістанете "
                  "пропускну здатність, а внизу — справжню затримку одного звернення",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "chase-vs-parallel.svg"), W, H, *F,
                  title="незалежні звернення проти залежного ланцюга")


# ── 8. Куди йдуть наносекунди одного звернення (вставка proj) ──────────────
def fig_walk_budget():
    W, H = 1260, 540
    F = []

    X0, X1 = 300, 1110
    NS_MAX = 210.0

    def px(ns):
        return X0 + (X1 - X0) * ns / NS_MAX

    # шкала: тільки поділки згори, без ліній крізь підписи
    for t in (0, 50, 100, 150, 200):
        F.append(line(px(t), 72, px(t), 84, color=MUTED, sw=1.4))
        F.append(text(px(t), 62, "%d нс" % t, size=12, color=MUTED))

    DATA = 92.4
    rows = [
        (104, "дрібні 4 КіБ", 103.6,
         "таблиця останнього рівня — 32 МіБ; у кеш вона не вміщається, "
         "тож останнє читання обходу йде в DRAM"),
        (222, "2 МіБ — THP або HugeTLB", 19.9,
         "кінцевих записів лише 8192, це 64 КіБ; вони живуть у кеші другого рівня"),
        (340, "1 ГіБ — HugeTLB", 0.5,
         "шістнадцять перекладів на весь буфер просто лежать у TLB — обходу немає"),
    ]
    BH = 54
    for y, label, tax, note in rows:
        F.append(text(X0 - 22, y + BH / 2 + 5, label, size=14, bold=True,
                      anchor="end"))
        F.append(rect(px(0), y, px(DATA) - px(0), BH,
                      fill=BLU_F, stroke=NEG, sw=1.5, rx=4))
        F.append(rect(px(DATA), y, px(DATA + tax) - px(DATA), BH,
                      fill=RED_F, stroke=POS, sw=1.5, rx=4))
        F.append(text(px(DATA + tax) + 16, y + BH / 2 + 5,
                      "%.1f нс" % (DATA + tax), size=15, bold=True,
                      anchor="start"))
        F.append(text(X0, y + BH + 21, note, size=12, color=MUTED,
                      anchor="start"))

    # легенда
    LY = 452
    F.append(rect(X0, LY, 26, 20, fill=BLU_F, stroke=NEG, sw=1.5, rx=3))
    F.append(text(X0 + 36, LY + 16, "звернення до самих даних",
                  size=13, anchor="start"))
    F.append(rect(X0 + 300, LY, 26, 20, fill=RED_F, stroke=POS, sw=1.5, rx=3))
    F.append(text(X0 + 336, LY + 16, "переклад адреси",
                  size=13, anchor="start"))

    F.append(text(W / 2, H - 26,
                  "синя частина однакова в усіх трьох рядках — це та сама "
                  "пам'ять і те саме залізо; різниця вся в червоній",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "walk-budget.svg"), W, H, *F,
                  title="з чого складається час одного випадкового звернення")


if __name__ == "__main__":
    print(fig_leaf_level())
    print(fig_two_answers())
    print(fig_thp_lifecycle())
    print(fig_timeline())
    print(fig_huge_flag_bits())
    print(fig_pool_accounting())
    print(fig_chase_vs_parallel())
    print(fig_walk_budget())
