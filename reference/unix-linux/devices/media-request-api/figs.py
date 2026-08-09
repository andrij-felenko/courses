# -*- coding: utf-8 -*-
"""Фігури до теми «Медіазапити: параметри й буфер, застосовані до кадру атомарно»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

REQ_FILL = "#eef4ff"
HOT_FILL = "#fdecea"
OK_FILL = "#eafaf0"


def fig_timing():
    """Один момент часу дивиться у два різні кадри: забраний буфер уже старий,
    записане значення подіє лише за кілька проміжків."""
    W, H = 1060, 430
    f = []

    x0, sw_, gap = 130, 140, 10
    cx = lambda i: x0 + sw_ * i + (sw_ - gap) / 2

    # лінія часу з кадровими проміжками
    for i in range(6):
        f.append(fitbox(x0 + sw_ * i, 175, sw_ - gap, 56, "кадр %d" % (i + 1), size=15))
    f.append(text(x0 - 20, 208, "сенсор", size=13, color=MUTED, anchor="end"))
    f.append(arrow(x0, 258, x0 + sw_ * 6 - gap, 258, color=MUTED, sw=1.4))
    f.append(text(x0 + sw_ * 6 - gap, 280, "час", size=12, color=MUTED, anchor="end"))

    # момент виклику
    mx = cx(3)
    f.append(line(mx, 60, mx, 268, color=POS, sw=2, dash="7 5"))
    f.append(text(mx, 44, "один момент: програма робить два виклики", size=13, color=POS))

    # назад — забраний буфер
    f.append(arrow(mx - 12, 300, cx(1), 300, color=NEG))
    f.append(fitbox(200, 315, 330, 62,
                    "DQBUF повертає кадр 2:\nйого зняли два проміжки тому",
                    size=13, fill=OK_FILL, stroke=NEG))

    # вперед — нове значення керування
    f.append(arrow(mx + 12, 120, cx(5), 120, color=POS))
    f.append(fitbox(730, 60, 300, 62,
                    "S_CTRL діє з кадру 6:\nсенсор перечитує регістри",
                    size=13, fill=HOT_FILL, stroke=POS))

    render(os.path.join(IMG, "frame-timing.svg"), W, H, *f)


def fig_request():
    """Запит — контейнер: виклики кладуть у нього, а не в залізо; залізо чіпає лише QUEUE."""
    W, H = 1020, 470
    f = []

    # виклики програми
    calls = [
        (95, "MEDIA_IOC_REQUEST_ALLOC\nна /dev/mediaN"),
        (215, "VIDIOC_S_EXT_CTRLS\nwhich = REQUEST_VAL"),
        (335, "VIDIOC_QBUF\nflag = REQUEST_FD"),
    ]
    for y, s in calls:
        f.append(fitbox(40, y, 290, 76, s, size=13))
    f.append(text(185, 60, "виклики програми", size=13, color=MUTED))

    # сам запит
    f.append(rect(430, 80, 300, 300, fill=REQ_FILL, stroke=NEG, sw=2))
    f.append(text(580, 62, "запит: окремий дескриптор", size=14, color=NEG, bold=True))
    f.append(fitbox(465, 145, 230, 66, "значення керувань", size=13, fill=BG))
    f.append(fitbox(465, 245, 230, 66, "буфер № 2", size=13, fill=BG))
    f.append(text(580, 350, "залізо ще не чіпали", size=12, color=MUTED))

    # стрілки всередину
    f.append(arrow(334, 253, 426, 200, color=MUTED))
    f.append(arrow(334, 373, 426, 290, color=MUTED))

    # queue → драйвер
    f.append(arrow(734, 230, 830, 230, color=POS, sw=2.2))
    f.append(fitbox(838, 175, 150, 110, "драйвер\nі залізо", size=14, fill=HOT_FILL, stroke=POS))
    f.append(mtext(782, 300, ["MEDIA_REQUEST_", "IOC_QUEUE"], size=12, color=POS))

    f.append(fitbox(40, 405, 948, 46,
                    "лише після QUEUE драйвер бачить обидві частини — і застосовує їх у ту мить, "
                    "коли бере цей буфер у роботу", size=13, fill=OK_FILL, stroke=FIELD))

    render(os.path.join(IMG, "request-contents.svg"), W, H, *f)


def fig_stateless():
    """Декодер без стану: кожен зріз їде з власним описом; вихідні буфери — окремою чергою."""
    W, H = 1080, 460
    f = []

    f.append(text(300, 46, "черга OUTPUT: запити", size=14, color=NEG, bold=True))
    for i in range(3):
        x = 60 + i * 210
        f.append(rect(x, 66, 190, 150, fill=REQ_FILL, stroke=NEG, sw=2))
        f.append(fitbox(x + 18, 88, 154, 48, "SPS, PPS,\nпараметри зрізу", size=12, fill=BG))
        f.append(fitbox(x + 18, 148, 154, 48, "байти зрізу %d" % (i + 1), size=12, fill=BG))

    f.append(arrow(345, 228, 345, 282, color=NEG))
    f.append(fitbox(215, 292, 260, 76, "декодер\nбез власного стану", size=14, fill=HOT_FILL, stroke=POS))

    f.append(text(830, 46, "черга CAPTURE: сама по собі", size=14, color=FIELD, bold=True))
    for i in range(4):
        f.append(fitbox(690 + i * 96, 74, 84, 56, "кадр %d" % (i + 1), size=12,
                        fill=OK_FILL, stroke=FIELD))
    f.append(arrow(483, 322, 690, 322, color=MUTED))
    f.append(fitbox(700, 292, 300, 76,
                    "готовий кадр: сюди його поклали,\nале жодних параметрів він не ніс",
                    size=12, fill=BG, stroke=MUTED))

    f.append(line(850, 288, 850, 240, color=MUTED, sw=1.6, dash="6 5"))
    f.append(arrow(850, 240, 500, 240, color=MUTED, sw=1.6))
    f.append(text(676, 226, "опорний кадр — за міткою часу", size=12, color=MUTED))

    f.append(fitbox(60, 398, 960, 44,
                    "запит описує, що зробити з цим шматком потоку; куди покласти результат — "
                    "не частина опису", size=13, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, "stateless-requests.svg"), W, H, *f)


def fig_states():
    """Стан запиту вирішує, який виклик пройде, а який поверне помилку."""
    W, H = 1200, 470
    f = []

    xs = [40, 450, 860]
    bw = 290

    names = [
        ("порожній", ["щойно виділений", "або очищений REINIT"]),
        ("у черзі", ["ядро роздало вміст", "драйверам"]),
        ("завершений", ["буфери можна забирати,", "значення застигли"]),
    ]
    for x, (t, s) in zip(xs, names):
        f.append(rect(x, 86, bw, 104, fill=REQ_FILL, stroke=NEG, sw=2))
        f.append(text(x + bw / 2, 118, t, size=16, color=NEG, bold=True))
        f.append(mtext(x + bw / 2, 144, s, size=12, color=MUTED))

    f.append(arrow(xs[0] + bw + 6, 138, xs[1] - 6, 138, color=POS, sw=2))
    f.append(mtext((xs[0] + bw + xs[1]) / 2, 100, ["MEDIA_REQUEST_", "IOC_QUEUE"],
                   size=11, color=POS))
    f.append(arrow(xs[1] + bw + 6, 138, xs[2] - 6, 138, color=FIELD, sw=2))
    f.append(mtext((xs[1] + bw + xs[2]) / 2, 100, ["останній об'єкт", "завершився"],
                   size=11, color=FIELD))

    # зворотний шлях: REINIT
    f.append(line(xs[2] + bw / 2, 84, xs[2] + bw / 2, 44, color=MUTED, sw=1.6))
    f.append(line(xs[2] + bw / 2, 44, xs[0] + bw / 2, 44, color=MUTED, sw=1.6))
    f.append(arrow(xs[0] + bw / 2, 46, xs[0] + bw / 2, 84, color=MUTED, sw=1.6))
    f.append(text((xs[0] + xs[2] + bw) / 2, 30,
                  "MEDIA_REQUEST_IOC_REINIT — той самий дескриптор іде на наступний кадр",
                  size=12, color=MUTED))

    rows = [
        ["S_EXT_CTRLS, QBUF — кладуть у запит",
         "G_EXT_CTRLS → EACCES",
         "QUEUE без буфера → ENOENT",
         "poll → POLLERR одразу",
         "REINIT — дозволено"],
        ["S_EXT_CTRLS → EBUSY",
         "QUEUE вдруге → EBUSY",
         "REINIT → EBUSY",
         "G_EXT_CTRLS → EACCES",
         "poll — чекає"],
        ["G_EXT_CTRLS — віддає застосоване",
         "poll → POLLPRI одразу",
         "REINIT — очищає під наступний кадр",
         "close — звільняє"],
    ]
    for x, lines in zip(xs, rows):
        f.append(rect(x, 232, bw, 148, fill=BG, stroke=MUTED, sw=1.4))
        f.append(mtext(x + 16, 258, lines, size=12, color=INK, anchor="start", lh=1.55))

    f.append(text(600, 216, "що приймає, а чим відмовляє кожен стан", size=13, color=MUTED))

    f.append(fitbox(40, 400, 1110, 46,
                    "майже кожна відмова механізму запитів — це виклик, зроблений не в тому стані, "
                    "у якому запит зараз перебуває", size=13, fill=OK_FILL, stroke=FIELD))

    render(os.path.join(IMG, "request-states.svg"), W, H, *f)


def fig_pipeline():
    """Робочий ритм програми: три слоти стоять у черзі, голова завершується першою,
    оброблений слот повертається в хвіст."""
    W, H = 1090, 500
    f = []

    f.append(text(545, 32, "черга: три запити, поставлені наперед", size=14, color=MUTED))

    exps = ["2", "10", "50"]
    for i in range(3):
        x = 60 + i * 340
        head = (i == 0)
        f.append(rect(x, 52, 260, 172, fill=REQ_FILL,
                      stroke=(POS if head else NEG), sw=(2.4 if head else 1.6)))
        f.append(text(x + 130, 78, "слот %d" % i, size=14, bold=True))
        f.append(fitbox(x + 20, 92, 220, 52, "витримка %s мс" % exps[i], size=13, fill=BG))
        f.append(fitbox(x + 20, 156, 220, 52, "буфер %d" % i, size=13, fill=BG))
        if i < 2:
            f.append(arrow(x + 264, 138, x + 336, 138, color=MUTED))

    f.append(text(190, 248, "голова: завершиться першою", size=12, color=POS))

    f.append(text(545, 300, "що робимо з головою, коли poll дав POLLPRI", size=14, color=MUTED))
    steps = [
        "G_EXT_CTRLS:\nяку витримку\nсправді застосовано",
        "DQBUF:\nзабрати кадр",
        "REINIT:\nочистити запит",
        "нова витримка,\nбуфер,\nQUEUE",
    ]
    bw, gap = 224, 32
    for j, s in enumerate(steps):
        xx = 60 + j * (bw + gap)
        f.append(fitbox(xx, 318, bw, 92, s, size=12, fill=OK_FILL, stroke=FIELD))
        if j < 3:
            f.append(arrow(xx + bw + 4, 364, xx + bw + gap - 4, 364, color=MUTED))

    f.append(fitbox(60, 432, 992, 48,
                    "оброблений слот повертається в хвіст черги — "
                    "тому чекати завжди треба саме на голову",
                    size=13, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, "request-pipeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_timing()
    fig_request()
    fig_stateless()
    fig_states()
    fig_pipeline()
    print("ok")
