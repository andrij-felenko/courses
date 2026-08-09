# -*- coding: utf-8 -*-
"""Фігури для теми «Міжпроцесорні переривання»."""
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


# ── 1. Анатомія виклику функції на чужому ядрі ─────────────────────────────
def fig_ipi_anatomy():
    W, H = 1340, 780
    F = []

    CW = 300                      # ширина колонки ядра
    LX, RX = 40, W - 40 - CW      # ліва й права колонки
    MX, MW = 470, 400             # середня смуга

    # ── заголовки колонок
    F.append(fitbox(LX, 30, CW, 54, "ядро процесора 0 — ініціатор",
                    size=16, bold=True, fill=BLU_F))
    F.append(fitbox(RX, 30, CW, 54, "ядро процесора 3 — ціль",
                    size=16, bold=True, fill=BLU_F))

    # ── кроки ініціатора
    SH = 62
    steps_l = [
        (120, "1 · заповнює описувач csd:\nфункція, аргумент, прапорець"),
        (206, "2 · вкладає його в чергу цілі"),
        (292, "3 · пише вектор у регістр\nконтролера переривань"),
        (378, "4 · крутиться, чекаючи,\nдоки прапорець знімуть"),
    ]
    for y, s in steps_l:
        F.append(fitbox(LX, y, CW, SH, s, size=13, fill=FILL))

    # ── кроки цілі
    steps_r = [
        (206, "5 · переривання: прийшов вектор"),
        (292, "6 · вичерпує всю чергу"),
        (378, "7 · виконує функцію\nй знімає прапорець"),
    ]
    for y, s in steps_r:
        F.append(fitbox(RX, y, CW, SH, s, size=13, fill=FILL))

    # ── середина: пам'ять
    MY = 140
    F.append(rect(MX, MY, MW, 150, fill=GRN_F))
    F.append(text(MX + MW / 2, MY + 28, "ПАМ'ЯТЬ", size=13, bold=True, color=MUTED))
    F.append(text(MX + MW / 2, MY + 52, "черга запитів ядра 3", size=14, bold=True))
    F.append(fitbox(MX + 26, MY + 70, 160, 56, "csd\nвід ядра 0", size=12, fill="#ffffff"))
    F.append(fitbox(MX + 214, MY + 70, 160, 56, "csd\nвід ядра 5", size=12, fill="#ffffff"))

    # ── середина: залізо
    HY = 340
    F.append(rect(MX, HY, MW, 116, fill=YEL_F))
    F.append(text(MX + MW / 2, HY + 28, "ЗАЛІЗО", size=13, bold=True, color=MUTED))
    F.append(text(MX + MW / 2, HY + 56, "контролер переривань", size=14, bold=True))
    F.append(text(MX + MW / 2, HY + 84, "вантаж — лише номер вектора", size=13, color=MUTED))

    # ── стрілки: вантаж у пам'ять і читання з неї
    F.append(arrow(LX + CW + 12, 232, MX - 12, MY + 100))
    F.append(arrow(MX + MW + 12, MY + 100, RX - 12, 318))
    # дзвінок
    F.append(arrow(LX + CW + 12, 318, MX - 12, HY + 58))
    F.append(arrow(MX + MW + 12, HY + 58, RX - 12, 236))

    # ── зворотний шлях: прапорець знято
    BY = 540
    F.append(line(RX + CW / 2, 440, RX + CW / 2, BY, dash="6 5"))
    F.append(line(RX + CW / 2, BY, LX + CW / 2, BY, dash="6 5"))
    F.append(arrow(LX + CW / 2, BY, LX + CW / 2, 442))
    F.append(text(W / 2, BY - 16, "прапорець знято — ініціатор іде далі",
                  size=14, color=MUTED))

    # ── підсумкові смуги
    F.append(fitbox(LX, 630, 560, 64,
                    "черга була порожня — дзвонимо",
                    size=15, bold=True, fill=GRN_F))
    F.append(fitbox(LX + 596, 630, 560, 64,
                    "черга не порожня — дзвінок уже в дорозі",
                    size=15, bold=True, fill=GRY_F))
    F.append(text(W / 2, 726,
                  "саме звідси береться безкоштовне групування запитів",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'ipi-anatomy.svg'), W, H, *F)


# ── 2. Повідомлення у векторі проти повідомлення в черзі ───────────────────
def fig_vector_vs_queue():
    W, H = 1320, 560
    F = []

    LX, LW = 40, 250
    B1, B1W = 330, 300
    B2, B2W = 690, 300
    B3, B3W = 1050, 230
    BH = 96

    # ── верхня смуга: перепланування
    yA = 80
    F.append(fitbox(LX, yA, LW, BH, "перепланування", size=16, bold=True, fill=BLU_F))
    F.append(fitbox(B1, yA, B1W, BH, "вектор 0xfd —\nце все повідомлення",
                    size=14, fill=GRN_F))
    F.append(arrow(B1 + B1W + 14, yA + BH / 2, B2 - 14, yA + BH / 2))
    F.append(fitbox(B2, yA, B2W, BH, "що робити, ціль дізнається\nзі своєї черги виконання",
                    size=14, fill=FILL))
    F.append(arrow(B2 + B2W + 14, yA + BH / 2, B3 - 14, yA + BH / 2))
    F.append(fitbox(B3, yA, B3W, BH, "зміна задачі —\nна виході з переривання",
                    size=13, fill=FILL))
    F.append(text((B1 + B3 + B3W) / 2, yA + BH + 46,
                  "ані вставки в чергу, ані прапорця, ані очікування",
                  size=14, color=MUTED))

    # ── нижня смуга: виклик функції
    yB = 300
    F.append(fitbox(LX, yB, LW, BH, "виклик функції", size=16, bold=True, fill=BLU_F))
    F.append(fitbox(B1, yB, B1W, BH, "вектор 0xfb —\n«глянь у свою чергу»",
                    size=14, fill=YEL_F))
    F.append(arrow(B1 + B1W + 14, yB + BH / 2, B2 - 14, yB + BH / 2))
    F.append(fitbox(B2, yB, B2W, BH, "у пам'яті: вказівник на функцію,\nаргумент, прапорець",
                    size=13, fill=FILL))
    F.append(arrow(B2 + B2W + 14, yB + BH / 2, B3 - 14, yB + BH / 2))
    F.append(fitbox(B3, yB, B3W, BH, "ціль вичерпує\nувесь список", size=13, fill=FILL))
    F.append(text((B1 + B3 + B3W) / 2, yB + BH + 46,
                  "універсально — і рівно тому дорожче",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'vector-vs-queue.svg'), W, H, *F)


# ── 3. Три способи не надсилати переривання ────────────────────────────────
def fig_not_sending():
    W, H = 1300, 700
    F = []

    LX, LW = 40, 290
    MX, MW = 380, 480
    RX, RW = 920, 340
    BH = 104

    rows = [
        (80,  "вузьке коло",
              "маска будується за правдою:\nлише ті ядра, яких дія стосується",
              "з 64 ядер —\nтри переривання", GRN_F),
        (240, "згруповані запити",
              "черга цілі не порожня, отже\nдзвінок уже в дорозі",
              "другий запит їде\nтим самим перериванням", YEL_F),
        (400, "ціль слухає сама",
              "ядро простоює в циклі, що стежить\nза прапорцем у пам'яті",
              "ставимо прапорець —\nпереривань нуль", BLU_F),
    ]
    for y, name, mid, right, col in rows:
        F.append(fitbox(LX, y, LW, BH, name, size=17, bold=True, fill=col))
        F.append(arrow(LX + LW + 14, y + BH / 2, MX - 14, y + BH / 2))
        F.append(fitbox(MX, y, MW, BH, mid, size=14, fill=FILL))
        F.append(arrow(MX + MW + 14, y + BH / 2, RX - 14, y + BH / 2))
        F.append(fitbox(RX, y, RW, BH, right, size=14, fill=GRY_F))

    F.append(line(LX, 566, W - 40, 566, color=MUTED, dash="6 5"))
    F.append(fitbox(LX, 596, W - 80, 76,
                    "зворотний бік: щоб розбудити задачу на чужому ядрі, одне переривання "
                    "дешевше за похід по чужий замок",
                    size=15, bold=True, fill=RED_F))

    render(os.path.join(IMG, 'not-sending.svg'), W, H, *F)


# ── 4. Життєвий цикл прапорця зайнятості в описувачі csd ───────────────────
def fig_csd_lifecycle():
    W, H = 1240, 780
    F = []

    CW = 470
    LX, RX = 60, 710
    BH = 84
    GAP = 30
    Y0 = 130

    F.append(fitbox(LX, 40, CW, 62,
                    "CSD_TYPE_SYNC — ініціатор чекає",
                    size=17, bold=True, fill=BLU_F))
    F.append(fitbox(RX, 40, CW, 62,
                    "CSD_TYPE_ASYNC — ініціатор пішов",
                    size=17, bold=True, fill=YEL_F))

    left = [
        ("ініціатор ставить прапорець LOCK\nу власному описувачі на стеку", FILL),
        ("вставка в чергу цілі, надсилання вектора,\nініціатор крутиться на прапорці", FILL),
        ("ціль виконує func(info)", RED_F),
        ("ціль знімає прапорець LOCK", GRN_F),
        ("ініціатор бачить нуль і йде далі", GRY_F),
    ]
    right = [
        ("прапорець уже стоїть — одразу −EBUSY;\nінакше ініціатор ставить LOCK", FILL),
        ("вставка в чергу цілі, надсилання вектора,\nініціатор повертається негайно", FILL),
        ("ціль знімає прапорець LOCK", GRN_F),
        ("ціль виконує func(info)", RED_F),
        ("описувач вільний ще до кінця func", GRY_F),
    ]

    for i in range(5):
        y = Y0 + i * (BH + GAP)
        F.append(fitbox(LX, y, CW, BH, left[i][0], size=14, fill=left[i][1]))
        F.append(fitbox(RX, y, CW, BH, right[i][0], size=14, fill=right[i][1]))
        if i < 4:
            F.append(arrow(LX + CW / 2, y + BH + 4, LX + CW / 2, y + BH + GAP - 4))
            F.append(arrow(RX + CW / 2, y + BH + 4, RX + CW / 2, y + BH + GAP - 4))

    yb = Y0 + 5 * (BH + GAP) + 16
    F.append(fitbox(LX, yb, RX + CW - LX, 74,
                    "порядок двох середніх кроків — увесь зміст різниці: "
                    "асинхронний описувач можна перезарядити зсередини його ж обробника, "
                    "синхронний до кінця func лишається зайнятим",
                    size=15, bold=True, fill=GRN_F))

    render(os.path.join(IMG, 'csd-lifecycle.svg'), W, H, *F)


# ── 5. Три мітки часу й три різні числа (вставка proj-ipi-latency) ─────────
def fig_three_marks():
    W, H = 1300, 680
    F = []

    LX, LW = 40, 250              # колонка підписів доріжок
    T0, TS, T1, TE, T2 = 400, 470, 640, 780, 900
    Y0, Y3 = 137, 300             # доріжки ядер
    BXH = 38                      # висота смужок на доріжці

    F.append(fitbox(LX, Y0 - 27, LW, 54, "ядро 2 — ініціатор",
                    size=16, bold=True, fill=BLU_F))
    F.append(fitbox(LX, Y3 - 27, LW, 54, "ядро 3 — ціль",
                    size=16, bold=True, fill=BLU_F))
    F.append(line(320, Y0, 1260, Y0, color=MUTED, dash="5 5"))
    F.append(line(320, Y3, 1260, Y3, color=MUTED, dash="5 5"))

    F.append(fitbox(T0, Y0 - BXH / 2, TS - T0, BXH, "ICR", size=12, fill=YEL_F))
    F.append(fitbox(TS, Y0 - BXH / 2, T2 - TS, BXH,
                    "крутиться, чекаючи знятого прапорця", size=13, fill=GRY_F))
    F.append(fitbox(320, Y3 - BXH / 2, T1 - 320, BXH,
                    "робить своє", size=13, fill=GRY_F))
    F.append(fitbox(T1, Y3 - BXH / 2, TE - T1, BXH,
                    "обробник", size=13, bold=True, fill=GRN_F))

    F.append(text(T0, Y0 - 42, "t₀", size=17, bold=True))
    F.append(text(T2, Y0 - 42, "t₂", size=17, bold=True))
    F.append(text(T1, Y3 + 58, "t₁", size=17, bold=True))

    F.append(arrow(TS + 6, Y0 + BXH / 2, T1 - 6, Y3 - BXH / 2 - 4))
    F.append(text(496, 250, "дзвінок", size=14, color=MUTED))
    F.append(arrow(TE + 6, Y3 - BXH / 2 - 4, T2 - 6, Y0 + BXH / 2))
    F.append(text(1010, 236, "прапорець знято", size=14, color=MUTED))

    BH = 22
    rows = [
        (430, T0, TS, YEL_F, "надсилання", 435,
         570, 370, "ціна для того, хто шле: виклик без очікування"),
        (520, T0, T1, RED_F, "одностороння затримка  t₁ − t₀", 520,
         720, 430, "правдива лише за синхронного TSC — тобто в межах одного кристала"),
        (610, T0, T2, GRN_F, "повний оберт  t₂ − t₀", 650,
         970, 290, "обидві мітки на одному ядрі — синхронність не потрібна"),
    ]
    for y, xa, xb, col, name, nx, cx, cw, note in rows:
        F.append(rect(xa, y, xb - xa, BH, fill=col))
        F.append(text(nx, y - 16, name, size=14, bold=True))
        F.append(fitbox(cx, y - 11, cw, 44, note, size=13, fill=FILL))

    render(os.path.join(IMG, 'three-marks.svg'), W, H, *F)


if __name__ == '__main__':
    fig_ipi_anatomy()
    fig_vector_vs_queue()
    fig_not_sending()
    fig_csd_lifecycle()
    fig_three_marks()
    print("ok")
