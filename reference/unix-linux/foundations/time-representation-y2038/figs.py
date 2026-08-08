# -*- coding: utf-8 -*-
"""Фігури до теми «Час як число: time_t, епоха і межа 2038 року»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def out(name):
    return os.path.join(IMG, name)


# ── 1. Високосна секунда не вміщається у шкалу time_t ────────────────────────
def fig_leap():
    W, H = 900, 450
    f = []

    f.append(text(450, 62, "мить на шкалі UTC", size=13, color=MUTED))

    utc = [("23:59:58", False), ("23:59:59", False),
           ("23:59:60", True), ("00:00:00", False)]
    utc_x = [150, 350, 550, 750]
    for (lbl, hot), x in zip(utc, utc_x):
        f.append(textbox(x, 105, lbl, size=16, pad=12,
                         stroke=POS if hot else LINE,
                         fill="#fdecea" if hot else FILL,
                         color=POS if hot else INK,
                         bold=hot, sw=2.2 if hot else 1.5)[0])

    val = [("1483228798", False), ("1483228799", True), ("1483228800", False)]
    val_x = [150, 450, 750]
    for (lbl, hot), x in zip(val, val_x):
        f.append(textbox(x, 300, lbl, size=15, pad=12,
                         stroke=POS if hot else LINE,
                         fill="#fdecea" if hot else FILL,
                         color=POS if hot else INK,
                         bold=hot, sw=2.2 if hot else 1.5)[0])

    f.append(arrow(150, 133, 150, 272))
    f.append(arrow(350, 133, 445, 272))
    f.append(arrow(550, 133, 462, 272, color=POS))
    f.append(arrow(750, 133, 750, 272))

    f.append(text(450, 358, "значення time_t", size=13, color=MUTED))
    f.append(mtext(450, 400,
                   ["доба у цій шкалі за визначенням має 86400 секунд,",
                    "тож зайвій секунді немає куди стати — значення повторюють"],
                   size=13, color=POS))

    render(out("leap-second-collapse.svg"), W, H, *f,
           title="Високосна секунда й одне значення на дві миті")


# ── 2. Вікно 32-бітного знакового time_t ────────────────────────────────────
def fig_window():
    W, H = 900, 360
    f = []
    x0, xm, x1, ay = 110, 450, 790, 185

    f.append(text(280, 108, "68 років", size=13, color=MUTED))
    f.append(text(620, 108, "68 років", size=13, color=MUTED))
    f.append(line(x0, 132, xm, 132, color=MUTED, sw=1, dash="5,4"))
    f.append(line(xm, 132, x1, 132, color=MUTED, sw=1, dash="5,4"))

    f.append(line(x0, ay, x1, ay, sw=2))
    for x in (x0, xm, x1):
        f.append(line(x, ay - 12, x, ay + 12, sw=2))

    f.append(text(x0, 168, "−2³¹", size=15, bold=True))
    f.append(text(xm, 168, "0", size=15, bold=True))
    f.append(text(x1, 168, "2³¹−1", size=15, bold=True))

    f.append(text(x0, 222, "1901-12-13 20:45:52", size=13, color=MUTED))
    f.append(text(xm, 222, "1970-01-01 00:00:00", size=13, color=MUTED))
    f.append(text(x1, 222, "2038-01-19 03:14:07", size=13, color=MUTED))

    f.append(line(x1, 244, x1, 278, color=POS, sw=2))
    f.append(line(x1, 278, x0, 278, color=POS, sw=2))
    f.append(arrow(x0, 278, x0, 246, color=POS))
    f.append(text(450, 306, "ще одна секунда: 2147483647 → −2147483648",
                  size=13, color=POS, bold=True))

    render(out("signed-window.svg"), W, H, *f,
           title="Уся історія, доступна 32-бітному знаковому time_t")


# ── 3. Дві межі одного системного виклику ───────────────────────────────────
def fig_twins():
    W, H = 900, 450
    f = []
    xl, xr = 245, 655

    f.append(textbox(xl, 92, ["програма, зібрана", "до переходу"],
                     size=14, pad=12)[0])
    f.append(textbox(xr, 92, ["програма, перезібрана", "з _TIME_BITS=64"],
                     size=14, pad=12)[0])

    f.append(line(40, 158, 860, 158, color=MUTED, sw=1.5, dash="7,5"))
    f.append(text(450, 182, "межа до простору користувача", size=12, color=MUTED))

    f.append(textbox(xl, 252, ["clock_gettime_time32", "tv_sec — 32 біти"],
                     size=14, pad=12, stroke=POS, fill="#fdecea", color=POS)[0])
    f.append(textbox(xr, 252, ["clock_gettime_time64", "tv_sec — 64 біти"],
                     size=14, pad=12, stroke=FIELD, fill="#eaf7ee", color=FIELD)[0])

    f.append(arrow(xl, 120, xl, 222))
    f.append(arrow(xr, 120, xr, 222))

    f.append(textbox(450, 388, "час усередині ядра — 64 біти на всіх архітектурах",
                     size=14, pad=14, bold=True)[0])
    f.append(arrow(xl, 284, 395, 362))
    f.append(arrow(xr, 284, 505, 362))

    render(out("two-syscall-twins.svg"), W, H, *f,
           title="Стару межу не міняють — поруч ставлять другу")


# ── 4. Межі різних представлень часу ────────────────────────────────────────
def fig_bounds():
    W, H = 1000, 400
    f = []
    ay = 232
    xs = [130, 315, 500, 685, 870]
    years = ["2036", "2038", "2106", "2446", "2486"]
    hot = [True, True, False, False, False]
    desc = [
        ["NTP: 32 біти", "беззнакові, від 1900"],
        ["time_t: 32 біти", "зі знаком, від 1970"],
        ["32 біти беззнакові", "від 1970"],
        ["ext4: 34 біти секунд", "в inode 256 байтів"],
        ["XFS bigtime: 64 біти", "наносекунд"],
    ]

    f.append(line(60, ay, 940, ay, sw=2))
    f.append(arrow(920, ay, 952, ay))

    for x, y, h, d in zip(xs, years, hot, desc):
        f.append(textbox(x, 186, y, size=17, pad=11, bold=True,
                         stroke=POS if h else LINE,
                         fill="#fdecea" if h else FILL,
                         color=POS if h else INK)[0])
        f.append(line(x, ay - 11, x, ay + 11, sw=2))
        f.append(mtext(x, 282, d, size=12, color=MUTED))

    f.append(text(500, 352,
                  "для порівняння: 64-бітний time_t вичерпається приблизно "
                  "через 292 мільярди років",
                  size=13, color=FIELD))

    render(out("boundaries-scale.svg"), W, H, *f,
           title="Кожен формат має власну межу — за власною домовленістю")


# ── 5. Як пересували нуль у ранніх редакціях ────────────────────────────────
def fig_epochs():
    W, H = 1000, 430
    f = []
    ay = 345

    def X(year):
        return 90 + (year - 1970) * 145

    f.append(line(70, ay, 900, ay, sw=2))
    f.append(arrow(900, ay, 945, ay))
    for y in (1970, 1971, 1972, 1973, 1974, 1975):
        f.append(line(X(y), ay - 9, X(y), ay + 9, sw=1.6, color=MUTED))
        f.append(text(X(y), ay + 30, str(y), size=12, color=MUTED))

    # перша редакція: нуль 1971, крок 1/60 с
    f.append(text(X(1971), 88, "1-ша редакція (3 листопада 1971): нуль 1971-01-01, крок 1/60 с",
                  size=13, anchor="start", color=POS))
    f.append(line(X(1971), 110, X(1971) + 2.27 * 145, 110, color=POS, sw=9))
    f.append(text(X(1971) + 2.27 * 145 + 14, 115, "≈2.27 року — і все",
                  size=13, anchor="start", color=POS))

    # третя редакція: нуль пересунуто на 1972
    f.append(text(X(1972), 168, "3-тя редакція: нуль пересунуто на 1972-01-01, крок той самий",
                  size=13, anchor="start", color=POS))
    f.append(line(X(1972), 190, X(1972) + 2.27 * 145, 190, color=POS, sw=9))
    f.append(text(X(1972) + 2.27 * 145 + 14, 195, "ще стільки ж",
                  size=13, anchor="start", color=POS))

    # секунди від 1970
    f.append(text(X(1970), 243, "від 1973 року: нуль 1970-01-01, крок — ціла секунда",
                  size=13, anchor="start", color=FIELD))
    f.append(line(X(1970), 265, 900, 265, color=FIELD, sw=9))
    f.append(arrow(890, 265, 945, 265, color=FIELD))
    f.append(text(X(1970), 292, "≈136 років уперед і назад — нуль більше не рухали",
                  size=12, anchor="start", color=FIELD))

    f.append(text(500, 405,
                  "пересувати нуль було дешево, поки збережених позначок часу майже не існувало",
                  size=13, color=MUTED))

    render(out("epoch-moves.svg"), W, H, *f,
           title="Три нулі відліку за перші три роки")


# ── 6. IPC: 64-бітна позначка, розкладена на два слова ──────────────────────
def fig_ipc_split():
    W, H = 940, 400
    f = []

    f.append(text(470, 62,
                  "структура не виросла — поля _high посіли місце колишньої набивки",
                  size=13, color=MUTED))

    cells = [("sem_otime", "молодші 32 біти", "+0"),
             ("sem_otime_high", "старші 32 біти", "+4"),
             ("sem_ctime", "молодші 32 біти", "+8"),
             ("sem_ctime_high", "старші 32 біти", "+12")]
    xs = [55, 265, 475, 685]
    for (name, half, off), x in zip(cells, xs):
        hot = name.endswith("_high")
        f.append(rect(x, 100, 200, 70,
                      fill="#eaf7ee" if hot else FILL,
                      stroke=FIELD if hot else LINE,
                      sw=2 if hot else 1.5))
        f.append(text(x + 100, 128, name, size=15, bold=True,
                      color=FIELD if hot else INK))
        f.append(text(x + 100, 152, half, size=12, color=MUTED))
        f.append(text(x + 100, 193, off, size=12, color=MUTED))

    for left, right, mid in ((155, 365, 260), (575, 785, 680)):
        f.append(line(left, 208, left, 228))
        f.append(line(left, 228, right, 228))
        f.append(line(right, 208, right, 228))
        f.append(arrow(mid, 228, mid, 270))

    f.append(textbox(260, 298,
                     "sem_otime + ((long long)sem_otime_high << 32)",
                     size=14, pad=12)[0])
    f.append(mtext(680, 292, ["так само", "для sem_ctime"],
                   size=13, color=MUTED))

    f.append(mtext(470, 358,
                   ["ядро віддає два окремі беззнакові слова —",
                    "зібрати з них одне число має сама програма"],
                   size=13, color=POS))

    render(out("ipc-time-split.svg"), W, H, *f,
           title="64-бітна позначка IPC, розкладена на два 32-бітні слова")


fig_leap()
fig_window()
fig_twins()
fig_bounds()
fig_epochs()
fig_ipc_split()
print("ok")


# ── Аудит: чотири поля, і найвужче вирішує ──────────────────────────────────
def fig_audit_fields():
    W, H = 1040, 450
    f = []
    xs = [160, 400, 640, 880]

    names = [
        ["змінна time_t", "у програмі"],
        ["struct timespec", "на межі з ядром"],
        ["внутрішній час", "ядра"],
        ["поле часу", "в inode"],
    ]
    widths = [180, 180, 180, 90]
    is64 = [True, True, True, False]
    probes = [
        ["sizeof(time_t)"],
        ["nm -D | grep time64"],
        ["clock_gettime64()"],
        ["записати 2039", "і прочитати назад"],
    ]
    verdicts = [
        ["«ні» → перезібрати", "з _TIME_BITS=64"],
        ["«ні» → оновити", "бібліотеку C"],
        ["«ні» → ядро", "старше за 5.1"],
        ["«ні» → ФС тільки", "створити заново"],
    ]

    for x, nm, bw, ok, pr, vd in zip(xs, names, widths, is64, probes, verdicts):
        f.append(textbox(x, 68, nm, size=13, pad=11)[0])
        f.append(fitbox(x - bw / 2.0, 153, bw, 34,
                        "64 біти" if ok else "32 біти",
                        size=14, bold=True,
                        fill="#eaf7ee" if ok else "#fdecea",
                        stroke=FIELD if ok else POS,
                        color=FIELD if ok else POS, sw=2))
        f.append(mtext(x, 248, pr, size=12))
        f.append(mtext(x, 320, vd, size=12, color=MUTED))

    for i in range(3):
        x1 = xs[i] + widths[i] / 2.0 + 8
        x2 = xs[i + 1] - widths[i + 1] / 2.0 - 8
        f.append(arrow(x1, 170, x2, 170, color=MUTED))

    f.append(text(520, 402,
                  "три «так» із чотирьох не дають нічого: "
                  "значення підріже найвужче поле",
                  size=13, color=POS, bold=True))

    render(out("audit-four-fields.svg"), W, H, *f,
           title="Чотири поля, крізь які проходить одна позначка часу")


# ── Два прочитання тих самих байтів ─────────────────────────────────────────
def fig_mixed_objects():
    W, H = 1000, 380
    f = []
    x0, x4, x8, x12, x16 = 90, 295, 500, 705, 910

    f.append(text(500, 32, "зсув у байтах від початку структури",
                  size=12, color=MUTED))
    for x, lbl in zip((x0, x4, x8, x12, x16), ("0", "4", "8", "12", "16")):
        f.append(text(x, 56, lbl, size=11, color=MUTED))
        f.append(line(x, 64, x, 74, color=MUTED, sw=1))
    f.append(line(x0, 69, x16, 69, color=MUTED, sw=1))

    f.append(text(500, 100, "розкладка, яку створила бібліотека з _TIME_BITS=64",
                  size=13))
    f.append(fitbox(x0, 112, x8 - x0, 42, "tv_sec — 8 байтів", size=14,
                    fill="#eaf7ee", stroke=FIELD, color=FIELD, sw=2))
    f.append(fitbox(x8, 112, x12 - x8, 42, "tv_nsec — 4", size=13,
                    fill="#eaf7ee", stroke=FIELD, color=FIELD, sw=2))
    f.append(fitbox(x12, 112, x16 - x12, 42, "набивка — 4", size=13,
                    fill=FILL, stroke=MUTED, color=MUTED))

    f.append(text(500, 196, "ті самі байти очима файлу, зібраного без прапорця",
                  size=13, color=POS))
    f.append(fitbox(x0, 208, x4 - x0, 42, "tv_sec — 4", size=13,
                    fill="#fdecea", stroke=POS, color=POS, sw=2))
    f.append(fitbox(x4, 208, x8 - x4, 42, "tv_nsec — 4", size=13,
                    fill="#fdecea", stroke=POS, color=POS, sw=2))
    f.append(fitbox(x8, 208, x16 - x8, 42, "структура вже скінчилася",
                    size=13, fill=BG, stroke=MUTED, color=MUTED))

    for x in (x4, x8):
        f.append(line(x, 154, x, 208, color=POS, sw=1.5, dash="5,4"))

    f.append(mtext(190, 288,
                   ["молодша половина секунд —", "доки вона менша за 2³¹,", "збігається"],
                   size=12, color=POS))
    f.append(mtext(520, 288,
                   ["старша половина секунд —", "сьогодні нулі, тож", "наносекунди виходять 0"],
                   size=12, color=POS))
    f.append(mtext(820, 288,
                   ["наступне поле більшої", "структури він візьме", "з байта 8"],
                   size=12, color=MUTED))

    render(out("mixed-object-layout.svg"), W, H, *f,
           title="Одні байти, дві розкладки — і жодного повідомлення про помилку")


fig_audit_fields()
fig_mixed_objects()
print("ok (audit)")
