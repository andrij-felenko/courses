# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
NEUT    = "#eef2f6"


def fig_fates():
    """Один давач відпав — три долі того самого циклу: ігнор / проковтнути / зловити."""
    W, H = 960, 330
    frags = []

    panels = [
        ("нічого не ловимо",        "виняток рве цикл",             "дім тихо холоне",        POS,   RED_T),
        ("ловимо все, мовчимо",     "цикл живий — на брехні",       "грій за застарілим t",   AMBER, AMBER_T),
        ("ловимо там, де є рішення", "переклали: давач недоступний", "лог раз · тримати стан", FIELD, GREEN_T),
    ]
    pw, gap = 280, 30
    for i, (head, mid, verdict, col, tint) in enumerate(panels):
        px = 30 + i * (pw + gap)
        frags.append(rect(px, 70, pw, 232, fill=BG, stroke="#dfe3e8", sw=1.2))
        frags.append(fitbox(px + 18, 82, pw - 36, 44, head, size=14, bold=True, stroke=col, fill=BG))
        frags.append(arrow(px + pw / 2, 128, px + pw / 2, 150))
        frags.append(fitbox(px + 18, 152, pw - 36, 50, mid, size=13))
        frags.append(arrow(px + pw / 2, 204, px + pw / 2, 230))
        frags.append(fitbox(px + 18, 232, pw - 36, 52, verdict, size=13, stroke=col, fill=tint))

    render(os.path.join(OUT, 'three-fates.svg'), W, H, *frags,
           title="Один давач відпав — три долі того самого циклу")


def fig_fork():
    """Перше питання про будь-який збій: баг у коді чи факт про світ?"""
    W, H = 920, 420
    frags = []

    frags.append(fitbox(360, 52, 200, 42, "щось пішло не так", size=14, bold=True))
    frags.append(arrow(460, 94, 460, 128))
    frags.append(fitbox(300, 130, 320, 46, "баг у коді — чи факт про світ?", size=15, bold=True,
                        stroke=AMBER, fill=AMBER_T))

    # ліва гілка — світ (зелене): злови й вирішуй
    frags.append(arrow(398, 176, 258, 224))
    frags.append(fitbox(90, 226, 320, 54, "факт про світ\nдавач офлайн · розетка мовчить", size=13))
    frags.append(arrow(250, 282, 250, 326))
    frags.append(fitbox(90, 328, 320, 54, "помилка-значення:\nзлови · переклади · вирішуй", size=13,
                        stroke=FIELD, fill=GREEN_T))

    # права гілка — баг (червоне): впасти голосно
    frags.append(arrow(522, 176, 662, 224))
    frags.append(fitbox(510, 226, 320, 54, "баг у коді\nroom не в списку · поріг = None", size=13))
    frags.append(arrow(670, 282, 670, 326))
    frags.append(fitbox(510, 328, 320, 54, "assert / впасти голосно,\nблизько до причини", size=13,
                        stroke=POS, fill=RED_T))

    render(os.path.join(OUT, 'error-fork.svg'), W, H, *frags,
           title="Перше питання про будь-який збій")


def fig_stack():
    """Помилка підіймається крізь шари й перевдягається на кожній межі."""
    W, H = 900, 380
    frags = []

    # три шари ліворуч (низ → верх): драйвер, політика, застосунок
    frags.append(fitbox(90, 272, 300, 60, "драйвер давача · I2C", size=14, bold=True, fill=NEUT))
    frags.append(fitbox(90, 170, 300, 60, "політика · t < поріг", size=14, bold=True, fill=NEUT))
    frags.append(fitbox(90, 68, 300, 60, "цикл + журнал", size=14, bold=True, fill=NEUT))

    # висхідна стрілка в проході між шарами й токенами
    frags.append(arrow(410, 322, 410, 92))

    # конектори шар → токен (лінії в порожньому проході)
    for cy in (302, 200, 98):
        frags.append(line(390, cy, 450, cy, color="#c8ced6", sw=1.2))

    # токени праворуч — той самий збій, перевдягнений на кожному рівні
    frags.append(fitbox(450, 280, 250, 44, "ETIMEDOUT — сире", size=13, stroke=POS, fill=RED_T))
    frags.append(fitbox(450, 178, 300, 44, "SensorUnavailable(«спальня»)", size=13, stroke=FIELD, fill=GREEN_T))
    frags.append(fitbox(450, 76, 300, 44, "лог раз · тримати стан", size=13, stroke=INK, fill=NEUT))

    render(os.path.join(OUT, 'error-stack.svg'), W, H, *frags,
           title="Помилка підіймається — і перевдягається на кожній межі")


def fig_swing():
    """Маятник коди↔винятки за півстоліття: де стояла індустрія в кожен момент."""
    W, H = 1040, 430
    f = []

    # заголовки двох смуг (два канали для збою)
    f.append(fitbox(44, 44, 372, 26, "↑ ВИНЯТКИ — окремий канал для збою",
                    size=12, stroke=AMBER, fill=AMBER_T, bold=True))
    f.append(fitbox(44, 388, 392, 26, "↓ ПОМИЛКА-ЗНАЧЕННЯ — збій у типі результату",
                    size=12, stroke=FIELD, fill=GREEN_T, bold=True))

    # вісь часу
    f.append(line(60, 215, 968, 215, color="#c8ced6", sw=1.6))
    f.append(arrow(940, 215, 980, 215, color="#c8ced6"))
    f.append(text(916, 206, "час", size=12, color=MUTED))

    # дві дуги маятника: угору (до винятків), потім назад униз (до значень)
    f.append(arrow(280, 246, 280, 150, color=AMBER, sw=2.6))
    f.append(arrow(760, 150, 760, 246, color=NEG, sw=2.6))

    xs   = [100, 220, 340, 460, 580, 700, 820, 940]
    top  = [False, False, True, True, True, True, False, False]
    labels = [
        "1965\nnull\nALGOL W",
        "≈1972\nerrno\nC · Unix",
        "1975\nвинятки\nPL/I · Goodenough",
        "1979\nCLU · термінація\nLiskov",
        "1990\nC++\nвинятки",
        "1995\nJava\nchecked",
        "2009\nGo · error\nзначення",
        "2015\nRust · Result\nзначення",
    ]
    strokes = [POS, INK, AMBER, AMBER, AMBER, POS, FIELD, FIELD]
    tints   = [RED_T, NEUT, AMBER_T, AMBER_T, AMBER_T, RED_T, GREEN_T, GREEN_T]
    bw, bh = 112, 66
    for x, is_top, lab, st, tn in zip(xs, top, labels, strokes, tints):
        f.append(circle(x, 215, 5, fill=st, stroke=st, sw=1))
        if is_top:
            f.append(line(x, 215, x, 142, color=st, sw=1.4))
            f.append(fitbox(x - bw / 2, 142 - bh, bw, bh, lab, size=12,
                            stroke=st, fill=tn, bold=True))
        else:
            f.append(line(x, 215, x, 268, color=st, sw=1.4))
            f.append(fitbox(x - bw / 2, 268, bw, bh, lab, size=12,
                            stroke=st, fill=tn, bold=True))

    render(os.path.join(OUT, 'codes-exceptions-swing.svg'), W, H, *f,
           title="Коди проти винятків — маятник за півстоліття")


def fig_channels():
    """Процес має три канали назовні: stdout (результат), stderr (діагностика),
    код виходу (тег результату) — проти одного return + throw усередині функції."""
    W, H = 860, 340
    frags = []

    # процес — один високий блок ліворуч, з якого віялом виходять три канали
    frags.append(fitbox(45, 100, 185, 170, "процес\n\ndh-temp",
                        size=17, bold=True, fill=NEUT, stroke="#c8ced6"))

    rows = [
        (120, "stdout — РЕЗУЛЬТАТ\nчисло → у конвеєр",            FIELD, GREEN_T),
        (185, "stderr — ДІАГНОСТИКА\nповідомлення, лог → людині", AMBER, AMBER_T),
        (250, "код виходу — ТЕГ\n0 / ≠0 → скриптові",             NEG,   NEUT),
    ]
    for cy, label, col, tint in rows:
        frags.append(arrow(232, cy, 356, cy))
        frags.append(fitbox(360, cy - 26, 320, 52, label, size=13, stroke=col, fill=tint))

    render(os.path.join(OUT, 'proc-channels.svg'), W, H, *frags,
           title="Три канали процесу — три частини контракту межі")


def fig_contract():
    """Матриця контракту dh-temp: чотири результати проти трьох каналів."""
    W, H = 860, 366
    frags = []

    cols = [(30, 220), (250, 90), (340, 180), (520, 300)]   # (x, w): результат/код/stdout/stderr
    head = ["результат", "код", "stdout", "stderr"]
    rows = [
        (["температура є", "0",  "19.4", "—"],                   GREEN_T),
        (["давач офлайн",  "3",  "—",    "«давач недоступний»"], AMBER_T),
        (["нема кімнати",  "2",  "—",    "«немає кімнати …»"],   NEUT),
        (["баг у коді",    "70", "—",    "трейсбек / стек"],     RED_T),
    ]

    def cell(x, w, y, s, tint, bold=False, size=13):
        return fitbox(x + 2, y, w - 4, 52, s, size=size, bold=bold, fill=tint,
                      stroke="#d3d9e0")

    y = 56
    for (x, w), h in zip(cols, head):                     # шапка
        frags.append(cell(x, w, y, h, NEUT, bold=True, size=14))
    for cells, tint in rows:                              # рядки-результати
        y += 56
        for i, (x, w) in enumerate(cols):
            big = (i == 1)                                # колонка коду — велика й жирна
            frags.append(cell(x, w, y, cells[i], tint, bold=big, size=20 if big else 13))

    render(os.path.join(OUT, 'error-contract.svg'), W, H, *frags,
           title="Контракт dh-temp: результат × канал")


if __name__ == '__main__':
    fig_fates()
    fig_fork()
    fig_stack()
    fig_swing()
    fig_channels()
    fig_contract()
    print("figures written to", OUT)
