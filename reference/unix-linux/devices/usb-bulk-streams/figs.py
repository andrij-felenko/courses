# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"
GREY_FILL = "#eeeeee"


# ── 1. Одне кільце проти масиву кілець ──────────────────────────────────────
def fig_streams_vs_one_ring():
    W, H = 1420, 700
    p = []

    p.append(text(60, 50, "звичайна bulk-точка", size=16, bold=True, anchor="start"))
    p.append(text(780, 50, "та сама точка зі стримами", size=16, bold=True, anchor="start"))

    # ліворуч
    p.append(fitbox(60, 80, 560, 100,
                    "Endpoint Context\n"
                    "адреса кільця + очікуваний біт циклу",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(340, 182, 340, 226))

    p.append(fitbox(60, 230, 560, 100,
                    "єдине кільце заявок\n"
                    "комірки вичитуються підряд",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(60, 380, 560, 110,
                    "порядок відповідей = порядок запитань:\n"
                    "у пакеті немає поля, яким пристрій\n"
                    "назвав би іншу відповідь",
                    size=14, fill=RED_FILL, stroke=POS))

    # праворуч
    p.append(fitbox(780, 80, 580, 100,
                    "Endpoint Context\n"
                    "MaxPStreams → 2^(MaxPStreams+1) записів · LSA",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(1070, 182, 1070, 226))

    p.append(fitbox(780, 230, 580, 100,
                    "масив контекстів стримів\n"
                    "запис = адреса кільця + біт циклу + тип",
                    size=14, fill=WARM_FILL, stroke=WARM))

    xs = [790, 930, 1070, 1210]
    p.append(line(1070, 332, 1070, 352))
    p.append(line(xs[0] + 65, 352, xs[-1] + 65, 352))
    for i, x in enumerate(xs):
        p.append(arrow(x + 65, 352, x + 65, 386))
        p.append(fitbox(x, 390, 130, 100,
                        "кільце\nстриму %d" % (i + 1),
                        size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(60, 560, 1300, 100,
                    "Дзвінок тепер називає й номер стриму: «на цій точці в цьому кільці є робота».\n"
                    "Подія про завершення теж несе номер — інакше драйвер не знав би, "
                    "до якого зі своїх кілець прив'язати відповідь.",
                    size=14, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'streams-vs-one-ring.svg'), W, H, *p)


# ── 2. Хто називає стрим на дротах ──────────────────────────────────────────
def fig_stream_handshake():
    W, H = 1320, 720
    p = []

    hx, dx = 250, 1010
    p.append(text(hx, 56, "хост", size=16, bold=True))
    p.append(text(dx, 56, "пристрій", size=16, bold=True))
    p.append(line(hx, 76, hx, 590, color=MUTED, sw=1.2, dash="6 6"))
    p.append(line(dx, 76, dx, 590, color=MUTED, sw=1.2, dash="6 6"))

    steps = [
        (130, "right", "команди 1 і 2 вже лежать у своїх кільцях", MUTED, True),
        (200, "left", "ERDY · Stream ID = 2", FIELD, False),
        (270, "right", "транзакція на Stream ID = 2", FIELD, False),
        (340, "left", "дані команди 2", FIELD, False),
        (430, "left", "ERDY · Stream ID = 1", NEG, False),
        (500, "right", "транзакція на Stream ID = 1", NEG, False),
        (570, "left", "дані команди 1", NEG, False),
    ]
    for y, direction, label, color, dashed in steps:
        if dashed:
            p.append(text((hx + dx) / 2, y - 12, label, size=14, color=color))
            continue
        if direction == "right":
            p.append(arrow(hx + 10, y, dx - 10, y, color=color))
        else:
            p.append(arrow(dx - 10, y, hx + 10, y, color=color))
        p.append(text((hx + dx) / 2, y - 12, label, size=14, color=color, bold=True))

    p.append(fitbox(60, 620, 600, 76,
                    "усередині транзакції стрим не міняється:\n"
                    "перемикання можливе лише в проміжку між ними",
                    size=14, fill=FILL, stroke=LINE))
    p.append(fitbox(700, 620, 560, 76,
                    "для запису хост будить пристрій\n"
                    "службовим номером Prime 0xFFFE",
                    size=14, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'stream-handshake.svg'), W, H, *p)


# ── 3. Що дає глибина черги в часі ──────────────────────────────────────────
def fig_queue_depth_timeline():
    W, H = 1420, 640
    p = []

    x0 = 300                      # початок осі часу
    span = 1020                   # пікселів на 400 мкс
    per_us = span / 400.0

    def bar(y, t0, dur, label, fill, stroke, h=46):
        return rect(x0 + t0 * per_us, y, max(dur * per_us, 3), h,
                    fill=fill, stroke=stroke, sw=1.2, rx=3), \
               text(x0 + (t0 + dur / 2) * per_us, y + h / 2 + 5, label, size=13)

    # шкала
    p.append(line(x0, 560, x0 + span, 560, color=MUTED, sw=1.2))
    for t in range(0, 401, 50):
        x = x0 + t * per_us
        p.append(line(x, 555, x, 565, color=MUTED, sw=1.2))
        p.append(text(x, 588, str(t), size=12, color=MUTED))
    p.append(text(x0 + span / 2, 616, "мікросекунди", size=13, color=MUTED))

    # BOT
    p.append(mtext(280, 110, ["BOT — одна команда за раз",
                              "глибина черги 1"], size=14, anchor="end", bold=True))
    y = 90
    for k in range(3):
        t = k * 120
        r, s = bar(y, t + 0, 6, "к", WARM_FILL, WARM)
        p.append(r); p.append(s)
        r, s = bar(y, t + 6, 100, "диск шукає дані", GREY_FILL, MUTED)
        p.append(r); p.append(s)
        r, s = bar(y, t + 106, 9, "дані", GREEN_FILL, FIELD)
        p.append(r); p.append(s)
        r, s = bar(y, t + 115, 5, "с", BLUE_FILL, NEG)
        p.append(r); p.append(s)

    # UAS
    p.append(mtext(280, 300, ["стрими — три в польоті",
                              "глибина черги 3"], size=14, anchor="end", bold=True))
    lanes = [
        (250, 0, 100, "команда 1 · стрим 1"),
        (320, 8, 60, "команда 2 · стрим 2"),
        (390, 16, 130, "команда 3 · стрим 3"),
    ]
    for y2, t0, wait, label in lanes:
        tdata = t0 + 6 + wait
        r, s = bar(y2, t0, 6, "к", WARM_FILL, WARM, h=40)
        p.append(r); p.append(s)
        r, s = bar(y2, t0 + 6, wait, "диск шукає дані", GREY_FILL, MUTED, h=40)
        p.append(r); p.append(s)
        r, s = bar(y2, tdata, 9, "дані", GREEN_FILL, FIELD, h=40)
        p.append(r); p.append(s)
        r, s = bar(y2, tdata + 9, 5, "с", BLUE_FILL, NEG, h=40)
        p.append(r); p.append(s)
        p.append(text(x0 + (t0 + 6 + wait / 2) * per_us, y2 - 8, label, size=12, color=MUTED))

    p.append(text(x0 + 175 * per_us, 470,
                  "відповіді приходять у порядку готовності: 2, 1, 3",
                  size=14, bold=True, anchor="start"))

    legend = [(WARM_FILL, WARM, "к — блок команди"),
              (GREY_FILL, MUTED, "очікування всередині диска"),
              (GREEN_FILL, FIELD, "дані на дротах"),
              (BLUE_FILL, NEG, "с — блок статусу")]
    for i, (f, s, cap) in enumerate(legend):
        ly = 430 + i * 36
        p.append(rect(50, ly, 22, 18, fill=f, stroke=s, sw=1.2, rx=2))
        p.append(text(82, ly + 14, cap, size=13, anchor="start"))

    render(os.path.join(IMG, 'queue-depth-timeline.svg'), W, H, *p)


# ── 4. Хронологія: специфікація та ядро ─────────────────────────────────────
def fig_uas_history():
    W, H = 1520, 680
    AX = 250
    p = []

    p.append(text(90, 30, "стандарти", size=16, bold=True, anchor="start"))
    p.append(text(90, 625, "Linux", size=16, bold=True, anchor="start"))

    p.append(arrow(80, AX, 1470, AX, color=MUTED, sw=2))
    p.append(text(1440, AX - 16, "час", size=13, color=MUTED))

    def node(cx, y, h, s, fill, stroke, w=200):
        end = y + h if y < AX else y
        p.append(line(cx, AX, cx, end, color=MUTED, sw=1.2, dash="4,4"))
        p.append(circle(cx, AX, 6, fill=stroke, stroke=stroke))
        p.append(fitbox(cx - w / 2, y, w, h, s, size=13, fill=fill, stroke=stroke))

    node(149, 45, 80, "17.11.2008\nспецифікація USB 3.0:\nстрими в §4.4.6.4", WARM_FILL, WARM)
    node(276, 150, 70, "24.06.2009\nUASP 1.0 від USB-IF", WARM_FILL, WARM)
    node(425, 45, 80, "09.03.2010\nUAS r04 → стандарт\nANSI INCITS 471-2010", WARM_FILL, WARM)

    node(430, 290, 78, "квітень 2010 · 2.6.35\nстрими в xHCI\n(Sarah / Sage Sharp)", BLUE_FILL, NEG)
    node(548, 395, 78, "07.10.2010 · 2.6.37\nдрайвер uas\n(Matthew Wilcox)", BLUE_FILL, NEG)
    node(999, 500, 78, "28.11.2012\n«mark uas driver\nas BROKEN»", RED_FILL, "#c0392b")
    node(1180, 290, 92, "вересень–жовтень 2013\nBROKEN знято; Ганс де Гуде\nбере драйвер на себе", GREEN_FILL, FIELD)
    node(1322, 395, 78, "08.06.2014 · 3.15\nUAS нарешті працює", GREEN_FILL, FIELD)

    p.append(line(149, 605, 1322, 605, color=MUTED, sw=1.5, dash="6,5"))
    p.append(line(149, 597, 149, 613, color=MUTED, sw=1.5))
    p.append(line(1322, 597, 1322, 613, color=MUTED, sw=1.5))
    p.append(text(735, 648,
                  "від запису в специфікації до працездатного UAS у Linux — п'ять із половиною років",
                  size=14, bold=True))

    render(os.path.join(IMG, 'uas-history-timeline.svg'), W, H, *p)


# ── 5. Тег → номер стриму → заявка й назад ──────────────────────────────────
def fig_tag_to_stream():
    W, H = 1320, 620
    p = []

    # бітова мапа вільних тегів
    p.append(text(60, 44, "бітова мапа вільних тегів", size=15, bold=True, anchor="start"))
    busy = {0, 1, 2, 3, 5, 7}
    for i in range(10):
        x = 60 + i * 34
        if i == 4:
            f, s = WARM_FILL, WARM
        elif i in busy:
            f, s = GREY_FILL, MUTED
        else:
            f, s = FILL, LINE
        p.append(rect(x, 62, 30, 34, fill=f, stroke=s, sw=1.2, rx=3))
        p.append(text(x + 15, 85, str(i), size=13, color=MUTED))
    p.append(text(60, 122, "find_first_zero_bit → 4", size=13, color=WARM, anchor="start"))

    p.append(arrow(211, 138, 211, 184, color=WARM))

    p.append(fitbox(60, 188, 340, 100,
                    "cmds[4] — структура команди\n"
                    "тег 4 · stream_id = 4 + 1 = 5",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    # шина від команди до трьох її втілень
    p.append(line(400, 238, 478, 238, color=NEG))
    p.append(line(478, 106, 478, 370, color=NEG))
    for y in (106, 238, 370):
        p.append(arrow(478, y, 556, y, color=NEG))

    p.append(fitbox(560, 58, 420, 96,
                    "блок команди на bulk-OUT\n"
                    "число 5 лежить у корисних даних\n"
                    "самій точці команд стрими не потрібні",
                    size=13, fill=WARM_FILL, stroke=WARM))
    p.append(fitbox(560, 190, 420, 96,
                    "заявка на дані\nurb->stream_id = 5",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(560, 322, 420, 96,
                    "заявка на статус\nurb->stream_id = 5",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(980, 238, 1026, 238, color=FIELD))
    p.append(arrow(980, 370, 1026, 370, color=FIELD))
    p.append(fitbox(1030, 190, 232, 228,
                    "на кожній із цих точок\nстоїть по кільцю на номер;\n"
                    "рухається те кільце,\nяке назве пристрій",
                    size=13, fill=FILL, stroke=LINE))

    p.append(arrow(1146, 422, 1146, 462, color=MUTED))
    p.append(fitbox(60, 466, 1202, 116,
                    "Завершення: заявка, яка завершилася, лежала в кільці свого номера.\n"
                    "Драйвер бере urb->stream_id, віднімає одиницю й дістає команду з cmds[].\n"
                    "Порожній слот означає, що пристрій назвав тег, якого йому не давали.",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'tag-to-stream.svg'), W, H, *p)


fig_streams_vs_one_ring()
fig_stream_handshake()
fig_queue_depth_timeline()
fig_uas_history()
fig_tag_to_stream()
print("ok")
