# -*- coding: utf-8 -*-
"""Фігури для теми «Розсилання скидань TLB»."""
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
GRY_F = "#eef0f2"


# ── 1. Чому кеш даних когерентний, а TLB — ні ──────────────────────────────
def fig_cache_vs_tlb():
    W, H = 1280, 660
    F = []

    LX, LW = 30, 210
    B1, B1W = 270, 240
    B2, B2W = 570, 200
    B3, B3W = 830, 260
    BH = 96

    # верхня смуга — рядок даних
    yA = 70
    F.append(fitbox(LX, yA, LW, BH, "рядок даних\nу кеші", size=15, bold=True, fill=FILL))
    F.append(fitbox(B1, yA, B1W, BH, "ядро 0 пише\nв комірку", size=14, fill=BLU_F))
    F.append(arrow(B1 + B1W + 10, yA + BH / 2, B2 - 10, yA + BH / 2))
    F.append(fitbox(B2, yA, B2W, BH, "протокол\nкогерентності", size=14, fill=GRN_F))
    F.append(arrow(B2 + B2W + 10, yA + BH / 2, B3 - 10, yA + BH / 2))
    F.append(fitbox(B3, yA, B3W, BH, "копія в кеші ядра 1\nстає недійсною", size=14, fill=BLU_F))
    F.append(text((B1 + B3 + B3W) / 2, yA + BH + 42,
                  "залізо стежить саме — жоден рядок коду цього не робить",
                  size=13, color=MUTED))

    # нижня смуга — запис TLB
    yB = 280
    F.append(fitbox(LX, yB, LW, BH, "переклад\nу TLB", size=15, bold=True, fill=FILL))
    F.append(fitbox(B1, yB, B1W, BH, "ядро 0 стирає PTE —\nце теж комірка", size=14, fill=BLU_F))
    F.append(arrow(B1 + B1W + 10, yB + BH / 2, B2 - 10, yB + BH / 2))
    F.append(fitbox(B2, yB, B2W, BH, "протокол\nкогерентності", size=14, fill=GRN_F))
    F.append(arrow(B2 + B2W + 10, yB + BH / 2, B3 - 10, yB + BH / 2))
    F.append(fitbox(B3, yB, B3W, BH, "рядок із PTE в кеші\nядра 1 недійсний", size=14, fill=BLU_F))

    # обрив: до самого перекладу протокол не дотягується
    cx = B3 + B3W / 2
    yC = yB + BH + 60
    F.append(line(cx, yB + BH + 8, cx, yC - 8, color=MUTED, sw=1.6, dash="5,5"))
    F.append(text(cx - 22, yC - 26, "зв'язку немає", size=13, color=POS, anchor="end"))
    F.append(fitbox(B3, yC, B3W, BH, "а переклад у TLB\nядра 1 — чинний",
                    size=14, fill=RED_F, stroke=POS, sw=2))

    F.append(text(W / 2, 590,
                  "переклад зібрано з чотирьох читань дерева таблиць — "
                  "у ньому не лишилося сліду, звідки він узятий,",
                  size=13, color=MUTED))
    F.append(text(W / 2, 616,
                  "а шукають його за віртуальним номером, тож за фізичною адресою PTE "
                  "його й не знайти",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "cache-vs-tlb.svg"), W, H, *F,
                  title="чому когерентність рятує кеш даних і не рятує TLB")


# ── 2. Хід розсилання в часі ───────────────────────────────────────────────
def fig_shootdown_timeline():
    W, H = 1420, 640
    F = []

    LX, LW = 30, 210
    BH = 54
    y0, y1, y2, y3 = 90, 200, 290, 380
    ACK = 1105

    for y, name in ((y0, "ядро 0 — ініціатор"), (y1, "ядро 1"),
                    (y2, "ядро 2"), (y3, "ядро 3 — зайняте")):
        F.append(fitbox(LX, y, LW, BH, name, size=14, bold=True, fill=FILL))

    # ініціатор
    F.append(fitbox(280, y0, 130, BH, "стирає записи", size=13, fill=BLU_F))
    F.append(fitbox(415, y0, 110, BH, "своє скидання", size=13, fill=BLU_F))
    F.append(fitbox(530, y0, 100, BH, "надсилає IPI", size=13, fill=YEL_F))
    F.append(fitbox(635, y0, ACK - 635, BH, "стоїть і чекає підтверджень",
                    size=15, bold=True, fill=RED_F, stroke=POS, sw=2))
    F.append(fitbox(ACK + 5, y0, 205, BH, "звільняє кадри", size=13, fill=GRN_F))

    # цілі
    F.append(fitbox(700, y1, 190, BH, "скидає, підтверджує", size=13, fill=BLU_F))
    F.append(fitbox(760, y2, 190, BH, "скидає, підтверджує", size=13, fill=BLU_F))
    F.append(fitbox(640, y3, 340, BH, "переривання вимкнені: критична секція",
                    size=13, fill=GRY_F, stroke=MUTED))
    F.append(fitbox(985, y3, 120, BH, "скидає,\nпідтверджує", size=12, fill=BLU_F))

    # мить останнього підтвердження
    F.append(line(ACK, 66, ACK, 452, color=POS, sw=1.6, dash="6,5"))
    F.append(text(ACK, 52, "останнє підтвердження", size=13, color=POS))

    # вісь часу
    F.append(arrow(280, 470, 1330, 470, color=MUTED, sw=1.6))
    F.append(text(1352, 475, "час", size=13, color=MUTED, anchor="start"))

    # дужка ціни
    BY = 512
    F.append(line(635, BY, ACK, BY, color=POS, sw=2))
    F.append(line(635, BY - 9, 635, BY + 9, color=POS, sw=2))
    F.append(line(ACK, BY - 9, ACK, BY + 9, color=POS, sw=2))
    F.append(text((635 + ACK) / 2, BY + 30,
                  "ціна для ініціатора = час до найповільнішої цілі",
                  size=14, bold=True, color=POS))

    F.append(text(W / 2, 604,
                  "робота на цілях коротка й іде паралельно — довгою операцію "
                  "робить не вона, а очікування",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "shootdown-timeline.svg"), W, H, *F,
                  title="розсилання скидань у часі: хто працює, а хто чекає")


# ── 3. Кому дійсно йде переривання ─────────────────────────────────────────
def fig_who_gets_ipi():
    W, H = 1300, 580
    F = []

    GX, GY = 70, 110
    CELL, GAP = 30, 6
    PITCH = CELL + GAP

    flush = {(1, 2), (3, 5), (6, 1)}
    lazy = {(2, 6), (5, 3)}
    gone = {(4, 4)}

    for r in range(8):
        for c in range(8):
            x = GX + c * PITCH
            y = GY + r * PITCH
            if (r, c) in flush:
                F.append(rect(x, y, CELL, CELL, fill=BLU_F, stroke=NEG, sw=2, rx=4))
            elif (r, c) in lazy:
                F.append(rect(x, y, CELL, CELL, fill=YEL_F, stroke=POS, sw=2, rx=4))
            elif (r, c) in gone:
                F.append(rect(x, y, CELL, CELL, fill=FILL, stroke=LINE, sw=1.6, rx=4))
            else:
                F.append(rect(x, y, CELL, CELL, fill=BG, stroke=MUTED, sw=1.0, rx=4))

    grid_w = 8 * PITCH - GAP
    F.append(text(GX + grid_w / 2, GY - 26, "64 ядра машини", size=15, bold=True))

    # правила
    RX, RW, RH = 500, 750, 76
    SX = 440
    rules = [
        (BG, MUTED, 1.0,
         "58 ядер поза маскою простору —\nпереривання не отримують зовсім"),
        (BLU_F, NEG, 2.0,
         "3 ядра справді тримають цей простір —\nотримують переривання й скидають записи"),
        (YEL_F, POS, 2.0,
         "2 ядра ліниві: виконують потік ядра на позиченому просторі —\nобробник лише перемикає їх на службовий простір"),
        (FILL, LINE, 1.6,
         "1 ядро вже перемкнулося на інший простір —\nініціатор відсіює його перед надсиланням"),
    ]
    for i, (fill, stroke, sw, txt) in enumerate(rules):
        y = 100 + i * 96
        F.append(rect(SX, y + (RH - 34) / 2, 34, 34, fill=fill, stroke=stroke, sw=sw, rx=4))
        F.append(fitbox(RX, y, RW, RH, txt, size=14, fill=FILL))

    F.append(text(W / 2, 530,
                  "коли звільняються самі таблиці сторінок, сита скасовуються: "
                  "переривання йде всім у масці, включно з лінивими",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "who-gets-ipi.svg"), W, H, *F,
                  title="три сита між правкою таблиці й міжпроцесорним перериванням")


# ── 4. Лічильник поколінь: як безпечно пропустити ядро ─────────────────────
def fig_tlb_gen():
    W, H = 1400, 530
    F = []

    LX, LW = 30, 250
    BH = 56
    yG, yC0, yC1 = 70, 180, 290
    S1, S2 = 645, 965

    F.append(fitbox(LX, yG, LW, BH, "покоління простору", size=14, bold=True, fill=FILL))
    F.append(fitbox(LX, yC0, LW, BH, "ядро 0", size=14, bold=True, fill=FILL))
    F.append(fitbox(LX, yC1, LW, BH, "ядро 1", size=14, bold=True, fill=FILL))

    F.append(fitbox(300, yG, S1 - 300 - 5, BH, "покоління 5", size=15, fill=GRN_F))
    F.append(fitbox(S1 + 5, yG, S2 - S1 - 10, BH, "покоління 6", size=15, fill=GRN_F))
    F.append(fitbox(S2 + 5, yG, 1300 - S2 - 5, BH, "покоління 7", size=15, fill=GRN_F))

    for sx in (S1, S2):
        F.append(line(sx, yG + BH + 6, sx, yC0 - 6, color=MUTED, sw=1.4, dash="4,4"))
    F.append(fitbox(S1 - 75, yC0, 150, BH, "скидання", size=14, fill=RED_F, stroke=POS, sw=2))
    F.append(fitbox(S2 - 75, yC0, 150, BH, "скидання", size=14, fill=RED_F, stroke=POS, sw=2))

    F.append(fitbox(300, yC1, 240, BH, "виконує процес,\nзапам'ятало 5", size=13, fill=BLU_F))
    F.append(fitbox(560, yC1, 480, BH, "виконує інший процес — розсилання його не чіпає",
                    size=13, fill=GRY_F, stroke=MUTED))
    F.append(fitbox(1060, yC1, 240, BH, "повертається:\n5 < 7 → скидає мітку",
                    size=13, fill=YEL_F, stroke=POS, sw=2))

    F.append(text(W / 2, 400,
                  "TLB ядра 1 весь цей час тримає застарілі переклади — "
                  "але простір на ньому не завантажений, тож нікому не шкодить",
                  size=13, color=MUTED))
    F.append(text(W / 2, 466,
                  "пропущене не губиться: борг записаний одним числом "
                  "і сплачується тоді, коли за нього дешево платити",
                  size=14, bold=True))

    return render(os.path.join(IMG, "tlb-gen.svg"), W, H, *F,
                  title="лічильник поколінь дозволяє пропустити ядро й не збрехати")


# ── 5. Чотири фази алгоритму Mach (1989) ───────────────────────────────────
def fig_mach_phases():
    W, H = 1440, 570
    F = []

    LX, LW = 30, 240
    BH = 76
    yI, yR1, yR2 = 92, 202, 302

    cols = [(290, 265), (565, 265), (840, 265), (1115, 265)]
    names = ["Фаза 1", "Фаза 2", "Фаза 3", "Фаза 4"]
    for (cx, cw), nm in zip(cols, names):
        F.append(text(cx + cw / 2, 50, nm, size=15, bold=True, color=MUTED))
    for sx in (555, 830, 1105):
        F.append(line(sx, 64, sx, 412, color=MUTED, sw=1.2, dash="4,5"))

    for y, nm in ((yI, "ініціатор"), (yR1, "ціль, що лишилась"),
                  (yR2, "ціль, що пішла")):
        F.append(fitbox(LX, y, LW, BH, nm, size=14, bold=True, fill=FILL))

    # ініціатор
    F.append(fitbox(cols[0][0], yI, cols[0][1], BH,
                    "ставить прапорці всім,\nхто тримає цей pmap,\nі шле переривання",
                    size=13, fill=BLU_F))
    F.append(fitbox(cols[1][0], yI, cols[1][1], BH,
                    "чекає, поки кожна ціль\nвийде з набору активних",
                    size=13, fill=RED_F, stroke=POS, sw=2))
    F.append(fitbox(cols[2][0], yI, cols[2][1], BH,
                    "править pmap\nі знімає з нього замок",
                    size=13, fill=GRN_F))
    F.append(fitbox(cols[3][0], yI, cols[3][1], BH,
                    "працює далі", size=13, fill=GRY_F, stroke=MUTED))

    # ціль, що лишилась
    F.append(fitbox(cols[0][0], yR1, cols[0][1], BH,
                    "своя робота", size=13, fill=GRY_F, stroke=MUTED))
    F.append(fitbox(cols[1][0], yR1, cols[1][1], BH,
                    "заходить в обробник\nі виходить\nз набору активних",
                    size=13, fill=BLU_F))
    F.append(fitbox(cols[2][0], yR1, cols[2][1], BH,
                    "крутиться на місці:\nне читає й не пише pmap",
                    size=13, fill=RED_F, stroke=POS, sw=2))
    F.append(fitbox(cols[3][0], yR1, cols[3][1], BH,
                    "скидає записи TLB,\nвертається в активні",
                    size=13, fill=GRN_F))

    # ціль, що перестала користуватися простором
    F.append(fitbox(cols[0][0], yR2, cols[0][1], BH,
                    "своя робота", size=13, fill=GRY_F, stroke=MUTED))
    F.append(fitbox(cols[1][0], yR2,
                    cols[3][0] + cols[3][1] - cols[1][0], BH,
                    "перемкнулося на інший адресний простір — "
                    "ініціатор перестає його чекати",
                    size=14, fill=YEL_F, stroke=POS, sw=2))

    F.append(text(W / 2, 460,
                  "цілі спиняються ДО правки, а скидають ПІСЛЯ: інакше апаратне "
                  "дозавантаження встигне втягнути напівзмінений запис назад у TLB,",
                  size=13, color=MUTED))
    F.append(text(W / 2, 486,
                  "а самі TLB тим часом дописують у таблицю біти звертання й "
                  "змінення — і псують правку",
                  size=13, color=MUTED))
    F.append(text(W / 2, 528,
                  "ініціатор теж виходить із набору активних і глушить переривання — "
                  "тому двоє, що стріляють один в одного, не зчіплюються намертво",
                  size=14, bold=True))

    return render(os.path.join(IMG, "mach-phases.svg"), W, H, *F,
                  title="чотири фази алгоритму Mach: бар'єр між правкою й скиданням")


# ── 6. Який лічильник спрацьовує в якій точці шляху (вставка api) ──────────
def fig_counters_map():
    W, H = 1300, 748
    F = []

    CW = 360
    C0, C1, C2 = 40, 460, 880
    SH, TH = 92, 116

    yTag1, ySt1 = 74, 208           # ініціатор: тег зверху, дія знизу
    ySt2, yTag2 = 416, 524          # ціль: дія зверху, тег знизу
    midSt1 = ySt1 + SH / 2
    midSt2 = ySt2 + SH / 2

    # ── смуга ініціатора ──
    F.append(text(C0, 58, "ЯДРО-ІНІЦІАТОР — те, що править таблицю сторінок",
                  size=15, bold=True, anchor="start"))

    F.append(fitbox(C0, yTag1, CW, TH,
                    "керує стеля\ntlb_single_page_flush_ceiling\nсторінок більше за 33 →\nвесь діапазон стає TLB_FLUSH_ALL",
                    size=13, fill=YEL_F))
    F.append(fitbox(C1, yTag1, CW, TH,
                    "nr_tlb_remote_flush   +1\ntrace tlb_flush\nreason = remote IPI send\npages = сторінок у діапазоні",
                    size=13, fill=GRN_F))
    F.append(fitbox(C2, yTag1, CW, TH,
                    "nr_tlb_local_flush_all   +1\nабо nr_tlb_local_flush_one += сторінки\ntrace tlb_flush\nreason = local (MM) shootdown",
                    size=13, fill=GRN_F))

    F.append(fitbox(C0, ySt1, CW, SH,
                    "get_flush_tlb_info()\nзбирає опис скидання", size=14, fill=BLU_F))
    F.append(fitbox(C1, ySt1, CW, SH,
                    "native_flush_tlb_multi()\nшле IPI по масці простору", size=14, fill=BLU_F))
    F.append(fitbox(C2, ySt1, CW, SH,
                    "flush_tlb_func(local = true)\nскидає свій власний TLB", size=14, fill=BLU_F))

    F.append(arrow(C0 + CW + 8, midSt1, C1 - 8, midSt1))
    F.append(arrow(C1 + CW + 8, midSt1, C2 - 8, midSt1))

    # ── смуга цілі ──
    F.append(text(C0, 396, "ЯДРО-ЦІЛЬ — те, що отримало переривання",
                  size=15, bold=True, anchor="start"))

    F.append(fitbox(C1, ySt2, CW, SH,
                    "flush_tlb_func(local = false)\nцей простір і тут завантажений", size=14, fill=BLU_F))
    F.append(fitbox(C2, ySt2, CW, SH,
                    "flush_tlb_func(local = false)\nтут завантажений уже інший", size=14, fill=GRY_F, stroke=MUTED))

    F.append(fitbox(C1, yTag2, CW, TH,
                    "рядок TLB у /proc/interrupts   +1\nрядок CAL там само   +1\nnr_tlb_remote_flush_received   +1\ntrace tlb_flush: remote shootdown",
                    size=13, fill=GRN_F))
    F.append(fitbox(C2, yTag2, CW, TH,
                    "trace tlb_flush\nreason = remote wrong CPU\nядро вибуває з маски простору\nжоден лічильник не росте",
                    size=13, fill=GRY_F, stroke=MUTED))

    xIPI = C1 + CW / 2
    F.append(arrow(xIPI, ySt1 + SH + 6, xIPI, ySt2 - 8))
    F.append(text(xIPI + 14, (ySt1 + SH + ySt2) / 2 + 5, "IPI", size=14, bold=True, anchor="start"))
    F.append(arrow(C1 + CW - 30, ySt1 + SH + 6, C2 + 130, ySt2 - 8, color=MUTED))

    # ── підпис знизу ──
    F.append(text(W / 2, 690,
                  "чотири лічильники nr_tlb_* є в /proc/vmstat ЛИШЕ при CONFIG_DEBUG_TLBFLUSH",
                  size=15, bold=True))
    F.append(text(W / 2, 720,
                  "рядок TLB у /proc/interrupts і трасувальна точка tlb_flush є завжди",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "counters-map.svg"), W, H, *F,
                  title="де на шляху розсилання спрацьовує який лічильник")


# ══ фігури вставки proj-shootdown-cost ═════════════════════════════════════

GRID = "#d7dbe0"


def poly(pts, color=LINE, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%g" '
            'stroke-linejoin="round"%s/>' % (s, color, sw, d))


def dot(x, y, color, r=4.6):
    return circle(x, y, r, fill=color, stroke=color, sw=1)


def frame(x0, xw, yt, yb):
    return (line(x0, yt, x0, yb, color=MUTED, sw=1.4) +
            line(x0, yb, x0 + xw, yb, color=MUTED, sw=1.4))


# ── 5. Що потрапляє у вимірюване вікно ─────────────────────────────────────
def fig_probe_window():
    W, H = 1400, 560
    F = []

    BY, BH = 165, 118

    # ліворуч — підготовка поза виміром
    F.append(fitbox(40, BY, 300, BH,
                    "mmap K сторінок\nMADV_NOHUGEPAGE\nдотик кожної сторінки",
                    size=14, fill=GRY_F, stroke=MUTED))
    F.append(text(190, BY + BH + 34, "поза виміром", size=13, color=MUTED))
    F.append(text(190, BY + BH + 58, "тут мінорні збої й ріст таблиць",
                  size=12, color=MUTED))

    # усередині — сама проба
    F.append(fitbox(380, BY, 200, BH, "стерти біт W\nу K записах", size=14, fill=BLU_F))
    F.append(arrow(586, BY + BH / 2, 614, BY + BH / 2))
    F.append(fitbox(620, BY, 200, BH, "IPI на всі ядра\nв масці простору",
                    size=14, fill=YEL_F))
    F.append(arrow(826, BY + BH / 2, 854, BY + BH / 2))
    F.append(fitbox(860, BY, 230, BH, "стояти, доки не\nвідзвітує остання ціль",
                    size=14, fill=RED_F, stroke=POS, sw=2))

    # дужка вимірюваного вікна
    F.append(line(370, 118, 1100, 118, color=POS, sw=2))
    F.append(line(370, 118, 370, BY - 6, color=POS, sw=2))
    F.append(line(1100, 118, 1100, BY - 6, color=POS, sw=2))
    F.append(text(735, 104, "вимірюване вікно: t₁ − t₀ навколо одного mprotect",
                  size=15, bold=True, color=POS))

    # праворуч — повернення прав
    F.append(fitbox(1140, BY, 230, BH,
                    "mprotect назад на RW:\nбіт W повертається,\nскидання немає",
                    size=13, fill=GRN_F))
    F.append(text(1255, BY + BH + 34, "поза виміром", size=13, color=MUTED))
    F.append(text(1255, BY + BH + 58, "без цього кроку наступна", size=12, color=MUTED))
    F.append(text(1255, BY + BH + 80, "проба нічого не змінить", size=12, color=MUTED))

    # вісь часу
    F.append(arrow(40, 400, 1350, 400, color=MUTED, sw=1.6))
    F.append(text(1372, 405, "час", size=13, color=MUTED, anchor="start"))

    F.append(text(W / 2, 452,
                  "звуження прав стирає біт запису — і саме тому вимагає скидання; "
                  "розширення його повертає й не вимагає нічого",
                  size=13, color=MUTED))
    F.append(text(W / 2, 490,
                  "усе, що лишилося ліворуч і праворуч від дужки, "
                  "інакше стало б тим, що ви зміряли замість розсилання",
                  size=14, bold=True))

    return render(os.path.join(IMG, "probe-window.svg"), W, H, *F,
                  title="одна проба: що всередині секундоміра, а що поза ним")


# ── 6. Ціна проти кількості ядер-власників ─────────────────────────────────
def fig_cores_curve():
    W, H = 1200, 640
    F = []

    X0, XW = 175, 750
    YT, YB = 100, 470
    YMAX = 45.0

    xs = [0, 1, 2, 4, 8, 16, 32]
    p50 = [0.9, 1.7, 2.0, 2.5, 3.1, 3.9, 5.0]
    p99 = [1.3, 3.7, 5.3, 9.1, 16.2, 27.4, 41.0]

    def px(i):
        return X0 + i * XW / (len(xs) - 1.0)

    def py(v):
        return YB - v / YMAX * (YB - YT)

    for v in (10, 20, 30, 40):
        F.append(line(X0, py(v), X0 + XW, py(v), color=GRID, sw=1.2, dash="4,5"))
        F.append(text(X0 - 14, py(v) + 5, "%d" % v, size=13, color=MUTED, anchor="end"))
    F.append(text(X0 - 14, py(0) + 5, "0", size=13, color=MUTED, anchor="end"))
    F.append(frame(X0, XW, YT, YB))

    for i, n in enumerate(xs):
        F.append(text(px(i), YB + 30, "%d" % n, size=14, color=MUTED))

    F.append(poly([(px(i), py(p99[i])) for i in range(len(xs))], color=POS))
    F.append(poly([(px(i), py(p50[i])) for i in range(len(xs))], color=NEG))
    for i in range(len(xs)):
        F.append(dot(px(i), py(p99[i]), POS))
        F.append(dot(px(i), py(p50[i]), NEG))

    F.append(text(X0, 74, "мікросекунд на одну операцію", size=14, bold=True, anchor="start"))
    F.append(text(X0 + XW / 2, YB + 66, "ядер, що тримають простір", size=14, color=MUTED))

    LX = X0 + XW + 55
    F.append(line(LX, 150, LX + 40, 150, color=POS, sw=3))
    F.append(text(LX + 50, 155, "p99 — хвіст", size=14, anchor="start"))
    F.append(line(LX, 200, LX + 40, 200, color=NEG, sw=3))
    F.append(text(LX + 50, 205, "p50 — типова", size=14, anchor="start"))
    F.append(text(LX, 260, "робота на кожній", size=13, color=MUTED, anchor="start"))
    F.append(text(LX, 282, "цілі не змінилася —", size=13, color=MUTED, anchor="start"))
    F.append(text(LX, 304, "змінилася лише", size=13, color=MUTED, anchor="start"))
    F.append(text(LX, 326, "кількість цілей", size=13, color=MUTED, anchor="start"))

    F.append(text(W / 2, 570,
                  "типова ціна росте помалу, а хвіст — різко: чим більше цілей, "
                  "тим важче, щоб ЖОДНА не забарилася",
                  size=14, bold=True))
    F.append(text(W / 2, 606,
                  "саме тому середнє тут бреше — воно змішує обидві криві в одне число",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, "cores-curve.svg"), W, H, *F,
                  title="ціна операції проти числа ядер, що тримають простір")


# ── 7. Поріг у 33 сторінки: кому стало дешевше ─────────────────────────────
def fig_page_threshold():
    W, H = 1280, 800
    F = []

    X0, XW = 190, 830
    AT, AB = 110, 350          # верхня панель: мікросекунди ініціатора
    BT, BB = 480, 660          # нижня панель: кіл за секунду у власників
    AMAX, BMAX = 7.0, 120.0

    def px(k):
        return X0 + (k - 1) / 63.0 * XW

    def ay(v):
        return AB - v / AMAX * (AB - AT)

    def by(v):
        return BB - v / BMAX * (BB - BT)

    ks = list(range(1, 65))
    init = [2.0 + k * 0.10 if k <= 33 else 2.6 for k in ks]
    hold = [100.0 if k <= 33 else 82.0 for k in ks]

    for v in (2, 4, 6):
        F.append(line(X0, ay(v), X0 + XW, ay(v), color=GRID, sw=1.2, dash="4,5"))
        F.append(text(X0 - 14, ay(v) + 5, "%d" % v, size=13, color=MUTED, anchor="end"))
    F.append(text(X0 - 14, ay(0) + 5, "0", size=13, color=MUTED, anchor="end"))
    F.append(frame(X0, XW, AT, AB))

    for v in (50, 100):
        F.append(line(X0, by(v), X0 + XW, by(v), color=GRID, sw=1.2, dash="4,5"))
        F.append(text(X0 - 14, by(v) + 5, "%d" % v, size=13, color=MUTED, anchor="end"))
    F.append(text(X0 - 14, by(0) + 5, "0", size=13, color=MUTED, anchor="end"))
    F.append(frame(X0, XW, BT, BB))

    # межа порога — наскрізь через обидві панелі
    xt = (px(33) + px(34)) / 2
    F.append(line(xt, AT - 26, xt, BB + 8, color=POS, sw=1.6, dash="6,5"))
    F.append(text(xt, AT - 36, "33 → 34", size=14, bold=True, color=POS))

    F.append(poly([(px(k), ay(v)) for k, v in zip(ks, init)], color=NEG))
    F.append(poly([(px(k), by(v)) for k, v in zip(ks, hold)], color=FIELD))

    for k in (1, 16, 33, 48, 64):
        F.append(text(px(k), BB + 30, "%d" % k, size=14, color=MUTED))
    F.append(text(X0 + XW / 2, BB + 66, "сторінок у діапазоні однієї правки",
                  size=14, color=MUTED))

    F.append(text(X0, 86, "ініціатор: мікросекунд на операцію",
                  size=14, bold=True, anchor="start"))
    F.append(text(X0, 456, "власники: кіл за секунду, % від вільного ходу",
                  size=14, bold=True, anchor="start"))

    F.append(text(X0 + 22, 148,
                  "по одному знеправленню на сторінку, ≈100 нс кожне",
                  size=13, color=MUTED, anchor="start"))
    F.append(text(X0 + XW, 316, "одне повне скидання — ініціаторові дешевше",
                  size=13, color=MUTED, anchor="end"))
    F.append(text(X0 + XW, 624, "а власники заново прогрівають свої TLB",
                  size=13, color=MUTED, anchor="end"))

    F.append(text(W / 2, 740,
                  "за порогом секундомір ініціатора показує полегшення — "
                  "бо рахунок переїхав на тих, кого він не міряє",
                  size=14, bold=True))

    return render(os.path.join(IMG, "page-threshold.svg"), W, H, *F,
                  title="поріг у 33 сторінки: кому саме стало дешевше")


if __name__ == "__main__":
    print(fig_cache_vs_tlb())
    print(fig_shootdown_timeline())
    print(fig_who_gets_ipi())
    print(fig_tlb_gen())
    print(fig_probe_window())
    print(fig_cores_curve())
    print(fig_page_threshold())
    print(fig_mach_phases())
    print(fig_counters_map())
