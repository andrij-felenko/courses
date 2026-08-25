# -*- coding: utf-8 -*-
"""Фігури для теми «Ізоляція таблиць сторінок ядра (KPTI)» (довідник Unix і Linux)."""
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


# ── 1. Пара кореневих таблиць процесу ──────────────────────────────────────
def fig_two_tables():
    W, H = 1300, 700
    F = []

    # підписи над копіями
    F.append(text(320, 76, "CR3, поки виконується ядро", size=16, bold=True))
    F.append(text(980, 76, "CR3, поки виконується програма", size=16, bold=True))

    # ядерна копія кореня
    F.append(fitbox(110, 100, 420, 140,
                    "верхня половина простору\nусе ядро: код, дані,\nбуфери, ключі",
                    size=16, fill=RED_F))
    F.append(fitbox(110, 240, 420, 110,
                    "нижня половина\nзаписи процесу", size=16, fill=BLU_F))

    # користувацька копія кореня
    F.append(fitbox(770, 100, 420, 140,
                    "верхня половина простору\nлише вхідна ділянка:\nтамбур, IDT, TSS, стеки винятків",
                    size=16, fill=GRN_F))
    F.append(fitbox(770, 240, 420, 110,
                    "нижня половина\nті самі записи", size=16, fill=BLU_F))

    # проміжок між копіями: різниця в один біт
    F.append(text(650, 140, "+4096 байтів", size=15, bold=True))
    F.append(arrow(548, 172, 752, 172))
    F.append(arrow(752, 200, 548, 200))
    F.append(text(650, 240, "перемикання копії", size=14, color=MUTED))
    F.append(text(650, 262, "= один біт у CR3", size=14, color=MUTED))

    # спільне піддерево
    F.append(fitbox(440, 480, 420, 110,
                    "спільне піддерево процесу:\nусі відображення програми\nв одному екземплярі",
                    size=16, fill=FILL))
    F.append(arrow(320, 355, 555, 476))
    F.append(arrow(980, 355, 745, 476))

    return render(os.path.join(IMG, 'two-tables.svg'), W, H, *F,
                  title="Дві копії кореневої таблиці процесу")


# ── 2. Ланцюг витоку Meltdown і місце розтину ──────────────────────────────
def fig_meltdown_path():
    W, H = 1160, 740
    F = []

    BX, BW, BH = 140, 560, 95
    steps = [
        (70,  "1 · читання за адресою ядра —\nпереклад у чинній таблиці є", RED_F),
        (195, "2 · значення вже роздане залежним інструкціям,\nпоки триває перевірка прав", FILL),
        (320, "3 · залежна інструкція чіпає рядок кешу\nза номером секретного байта", FILL),
        (445, "4 · усе скасовано: регістри чисті,\nвиняток оголошено", BLU_F),
        (570, "5 · рядок кешу лишився теплим —\nбайт відновлюють вимірюванням часу", YEL_F),
    ]
    for y, s, fill in steps:
        F.append(fitbox(BX, y, BW, BH, s, size=16, fill=fill))
    for y in (70, 195, 320, 445):
        F.append(arrow(BX + BW / 2, y + BH + 3, BX + BW / 2, y + 122))

    # праворуч — два коментарі
    F.append(fitbox(790, 72, 330, 92,
                    "KPTI розтинає ланцюг тут:\nу користувацькій копії перекладу\nнемає — братися нема звідки",
                    size=14, fill=GRN_F))
    F.append(arrow(786, 118, 706, 118))

    F.append(fitbox(790, 447, 330, 92,
                    "кеш до архітектурного стану\nне належить — його ніхто\nне відкочує",
                    size=14, fill=YEL_F))
    F.append(arrow(786, 493, 706, 493))

    return render(os.path.join(IMG, 'meltdown-path.svg'), W, H, *F,
                  title="Ланцюг витоку і єдина ланка, яку можна розірвати програмно")


# ── 3. Перетин межі до KPTI і після ────────────────────────────────────────
def fig_entry_cost():
    W, H = 1320, 540
    F = []

    F.append(text(70, 86, "Було: спільна таблиця", size=16, bold=True, anchor="start"))
    row1 = [
        (70, 200, "програма", FILL),
        (290, 220, "зміна рівня\nпривілею", BLU_F),
        (530, 240, "вхідний код ядра", FILL),
        (790, 220, "робота\nсистемного виклику", FILL),
        (1030, 220, "повернення", FILL),
    ]
    for x, w, s, fill in row1:
        F.append(fitbox(x, 106, w, 88, s, size=15, fill=fill))

    F.append(text(70, 286, "Стало: дві копії кореня", size=16, bold=True, anchor="start"))
    row2 = [
        (70, 150, "програма", FILL),
        (235, 140, "зміна рівня", BLU_F),
        (390, 175, "тамбур:\nCR3 ← ядерна", RED_F),
        (580, 160, "вхідний код", FILL),
        (755, 160, "робота", FILL),
        (930, 195, "CR3 ←\nкористувацька", RED_F),
        (1140, 125, "повернення", FILL),
    ]
    for x, w, s, fill in row2:
        F.append(fitbox(x, 306, w, 88, s, size=15, fill=fill))

    F.append(text(660, 450, "два записи в CR3 на кожен перетин межі, приблизно по сотні тактів кожен",
                  size=15))
    F.append(text(660, 482, "ядерні переклади втратили глобальність — рятує лише мітка адресного простору (PCID)",
                  size=14, color=MUTED))

    return render(os.path.join(IMG, 'entry-cost.svg'), W, H, *F,
                  title="Ціна межі: що додалося на вході в ядро й на виході з нього")


# ── 4. Анатомія одного заміру (вставка proj-kpti-cost) ─────────────────────
def fig_bench_window():
    W, H = 1250, 580
    F = []

    F.append(text(60, 84, "Вікно з викликом", size=16, bold=True, anchor="start"))
    rowA = [
        (60,   190, "lfence\nrdtsc", BLU_F),
        (280,  330, "×64 кроки ланцюгом\nпо сторінках буфера", FILL),
        (640,  330, "виклик, що перетинає межу\nsyscall(SYS_getppid)", RED_F),
        (1000, 190, "rdtscp\nlfence", BLU_F),
    ]
    for x, w, s, fill in rowA:
        F.append(fitbox(x, 104, w, 90, s, size=15, fill=fill))

    F.append(text(60, 264, "Те саме вікно без виклику — тло, яке віднімають",
                  size=16, bold=True, anchor="start"))
    rowB = [
        (60,   190, "lfence\nrdtsc", BLU_F),
        (280,  330, "×64 кроки ланцюгом\nпо тих самих сторінках", FILL),
        (640,  330, "нічого", GRN_F),
        (1000, 190, "rdtscp\nlfence", BLU_F),
    ]
    for x, w, s, fill in rowB:
        F.append(fitbox(x, 284, w, 90, s, size=15, fill=fill))

    F.append(minus(30, 239, r=11))
    F.append(arrow(625, 378, 625, 424))
    F.append(fitbox(200, 428, 850, 96,
                    "(найменший прогін A − найменший прогін B) ÷ кількість ітерацій\n"
                    "= такти на один перетин межі при цьому тиску на TLB",
                    size=16, fill=YEL_F))

    return render(os.path.join(IMG, 'bench-window.svg'), W, H, *F,
                  title="Що всередині вікна заміру й що з нього віднімають")


# ── 5. Форма залежності ціни від робочої множини ───────────────────────────
def fig_cost_curve():
    W, H = 1420, 710
    F = []

    XS = [200, 370, 540, 710, 880, 1050]
    Y0, YTOP = 560, 130

    def curve(ys, color, sw=2.6):
        for i in range(len(XS) - 1):
            F.append(line(XS[i], ys[i], XS[i + 1], ys[i + 1], color=color, sw=sw))

    # осі
    F.append(line(200, Y0, 1060, Y0))
    F.append(line(200, YTOP, 200, Y0))
    for i, x in enumerate(XS):
        F.append(line(x, Y0, x, Y0 + 10))
    for x, s in zip(XS, ["0", "64 КіБ", "1 МіБ", "16 МіБ", "64 МіБ", "256 МіБ"]):
        F.append(text(x, 592, s, size=14, color=MUTED))
    F.append(text(630, 632, "розмір робочої множини, якої торкаємося між викликами",
                  size=15))
    F.append(text(60, 118, "такти на один перетин межі", size=15, anchor="start"))

    curve([543, 543, 542, 542, 541, 540], MUTED, sw=2.2)
    curve([478, 474, 468, 460, 452, 446], FIELD)
    curve([428, 421, 408, 386, 366, 348], NEG)
    curve([372, 352, 312, 258, 208, 162], POS)

    F.append(text(1075, 546, "vDSO — межі не перетинає",
                  size=14, color=MUTED, anchor="start"))
    F.append(text(1075, 450, "pti=off", size=14, color=FIELD, anchor="start", bold=True))
    F.append(text(1075, 472, "(лишилася сама зміна кільця)",
                  size=13, color=MUTED, anchor="start"))
    F.append(text(1075, 352, "PTI + PCID", size=14, color=NEG, anchor="start", bold=True))
    F.append(text(1075, 166, "PTI, nopcid", size=14, color=POS, anchor="start", bold=True))
    F.append(text(1075, 188, "(повне скидання TLB на кожному перетині)",
                  size=13, color=MUTED, anchor="start"))

    F.append(text(600, 100, "тут робоча множина перестала", size=14, color=MUTED))
    F.append(text(600, 120, "вміщатися в TLB", size=14, color=MUTED))
    F.append(line(600, 144, 600, Y0, color=MUTED, sw=1.4, dash="6 5"))

    F.append(text(710, 678,
                  "форма, а не числа: абсолютні значення залежать від машини, ядра й набору пом'якшень",
                  size=14, color=MUTED))

    return render(os.path.join(IMG, 'cost-curve.svg'), W, H, *F,
                  title="Ціна перетину межі як функція робочої множини")


if __name__ == '__main__':
    for f in (fig_two_tables, fig_meltdown_path, fig_entry_cost,
              fig_bench_window, fig_cost_curve):
        print(f())
