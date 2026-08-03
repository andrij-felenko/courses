# -*- coding: utf-8 -*-
"""Фігури до теми «Годинник, мітки часу й синхронізація потоків» (GStreamer)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Три шкали часу ───────────────────────────────────────────────────────
def fig_three_axes():
    W, H = 960, 560
    f = []

    x0, x1 = 60, 900
    xp, xr = 330, 690           # момент PLAYING і момент показу кадру
    yA, yB, yC = 130, 290, 450  # три осі

    def axis(y, name, subtitle):
        out = [arrow(x0, y, x1, y)]
        out.append(text(x0, y - 44, name, size=15, color=INK, anchor="start", bold=True))
        out.append(text(x0, y - 24, subtitle, size=12, color=MUTED, anchor="start"))
        return "".join(out)

    f.append(axis(yA, "час годинника  (absolute_time)",
                  "спільний лічильник наносекунд; не скидається й не починається з нуля"))
    f.append(axis(yB, "running_time",
                  "скільки конвеєр пробув у PLAYING; нуль у мить запуску"))
    f.append(axis(yC, "мітка часу буфера  (PTS у сегменті)",
                  "позиція всередині медіа; своя для кожного файлу й кожного seek"))

    # вертикальні звʼязки
    for x in (xp, xr):
        f.append(line(x, yA - 14, x, yC + 14, color=MUTED, sw=1.2, dash="5 5"))

    def tick(x, y):
        return line(x, y - 12, x, y + 12, color=INK, sw=2.2)

    for x in (xp, xr):
        for y in (yA, yB, yC):
            f.append(tick(x, y))

    # підписи значень — праворуч від вертикалі, щоб лінія не перетинала текст
    f.append(text(xp + 12, yA + 30, "1205.400 с", size=13, anchor="start"))
    f.append(text(xr + 12, yA + 30, "1207.900 с", size=13, anchor="start"))
    f.append(text(xp + 12, yB + 30, "0.000 с", size=13, anchor="start"))
    f.append(text(xr + 12, yB + 30, "2.500 с", size=13, anchor="start"))
    f.append(text(xp + 12, yC + 30, "PTS 10.000 с", size=13, anchor="start"))
    f.append(text(xr + 12, yC + 30, "PTS 12.500 с", size=13, anchor="start"))

    # підписи подій — ліворуч від вертикалі
    f.append(text(xp - 12, yA - 4, "перехід у PLAYING", size=12, color=POS, anchor="end"))
    f.append(text(xr - 12, yA - 4, "мить показу кадру", size=12, color=POS, anchor="end"))
    f.append(text(xp - 12, yC - 4, "segment.start", size=12, color=FIELD, anchor="end"))

    # base_time — відрізок від початку осі до моменту PLAYING
    yb = yA + 62
    f.append(line(x0 + 4, yb, xp - 4, yb, color=NEG, sw=2))
    f.append(line(x0 + 4, yb - 7, x0 + 4, yb + 7, color=NEG, sw=2))
    f.append(line(xp - 4, yb - 7, xp - 4, yb + 7, color=NEG, sw=2))
    f.append(text((x0 + xp) / 2, yb - 14, "base_time = 1205.400 с", size=13, color=NEG, bold=True))

    # формули знизу
    box, bw, bh = textbox(W / 2, H - 62,
                          ["running_time = (PTS − segment.start) / |rate| + segment.base",
                           "час_показу_за_годинником = running_time + base_time"],
                          size=15, pad=18, min_w=640)
    f.append(box)

    render(os.path.join(OUT, 'three-time-axes.svg'), W, H, *f,
           title="Три шкали часу конвеєра й дві рівності, що їх зшивають")


# ── 2. Рішення споживача ────────────────────────────────────────────────────
def fig_sink_decision():
    W, H = 1020, 470
    f = []

    x0, x1 = 210, 790
    xs = 600                     # sync_time
    rows = [
        (150, 320, "прийшов рано",   "чекаємо на годиннику\nдо sync_time",       NEG),
        (280, 578, "прийшов вчасно", "показуємо одразу",                         FIELD),
        (410, 706, "спізнився",      "викидаємо кадр\nі шлемо QoS проти течії",  POS),
    ]

    # спільна вертикаль sync_time
    f.append(line(xs, 118, xs, 442, color=INK, sw=1.6, dash="6 4"))
    f.append(text(xs, 100, "sync_time = running_time + base_time", size=14, bold=True))

    for y, xb, left, right, col in rows:
        f.append(arrow(x0, y, x1, y))
        f.append(text(30, y - 6, left, size=13, anchor="start", bold=True))
        f.append(text(30, y + 14, "буфер", size=12, color=MUTED, anchor="start"))
        f.append(circle(xb, y, 9, fill="#ffffff", stroke=col, sw=2.6))
        f.append(mtext(812, y - 4, right, size=12, color=col, anchor="start"))

    f.append(text((x0 + x1) / 2, 442 - 410 + 410 + 22, "час годинника →", size=12, color=MUTED))

    render(os.path.join(OUT, 'sink-decision.svg'), W, H, *f,
           title="Синхронізує тільки споживач: він порівнює sync_time з годинником")


# ── 3. Жива камера й latency ────────────────────────────────────────────────
def fig_live_latency():
    W, H = 980, 470
    f = []

    x0 = 190
    bw = 130                     # ширина кадру = 33 мс
    n = 4

    def row(y, shift, caption, note, col):
        out = []
        out.append(arrow(x0 - 30, y + 70, x0 + n * bw + 90, y + 70))
        out.append(text(x0 - 30, y + 92, "running_time →", size=12, color=MUTED, anchor="start"))
        for i in range(n):
            x = x0 + i * bw
            out.append(rect(x, y, bw - 8, 44, fill="#eef2f7", stroke=MUTED, sw=1.2))
            out.append(text(x + (bw - 8) / 2, y + 28, "кадр %d" % i, size=12, color=MUTED))
            # мить, коли кадр реально готовий
            out.append(line(x + bw - 8, y, x + bw - 8, y + 70, color=MUTED, sw=1, dash="3 3"))
            # точка показу
            out.append(circle(x + shift, y + 70, 8, fill="#ffffff", stroke=col, sw=2.6))
        out.append(text(30, y + 16, caption, size=13, anchor="start", bold=True))
        out.append(mtext(30, y + 40, note, size=12, color=col, anchor="start"))
        return "".join(out)

    f.append(text(x0 - 30, 62, "сірий блок — камера збирає кадр 33 мс; кружечок — мить показу",
                  size=12, color=MUTED, anchor="start"))
    f.append(row(90, 0, "без компенсації",
                 "показ призначено на\nпочаток збирання —\nкадр запізнився на 33 мс", POS))
    f.append(row(280, bw - 8, "з latency = 33 мс",
                 "показ зсунуто рівно на\nчас збирання — кадр\nвже готовий", FIELD))

    render(os.path.join(OUT, 'live-latency.svg'), W, H, *f,
           title="Живе джерело віддає кадр уже після його мітки часу")


# ── 4. Дві машини ───────────────────────────────────────────────────────────
def fig_two_machines():
    W, H = 900, 430
    f = []

    clock, cw, ch = textbox(W / 2, 90, ["спільний годинник",
                                        "GstNetClientClock або GstPtpClock"],
                            size=14, pad=14, fill="#eaf0fd", stroke=NEG, sw=2)
    f.append(clock)

    base, bw2, bh2 = textbox(W / 2, 200, "спільний base_time (роздали руками)",
                             size=13, pad=12, fill="#eafaf0", stroke=FIELD, sw=2)
    f.append(base)

    for cx, name in ((220, "машина A"), (680, "машина B")):
        box, w, h = textbox(cx, 330, [name,
                                      "власний конвеєр,",
                                      "власні буфери й caps"],
                            size=13, pad=14, min_w=250)
        f.append(box)
        f.append(arrow(W / 2 - (0 if cx < W / 2 else 0), 200 + bh2 / 2,
                       cx, 330 - h / 2 - 4, color=FIELD))
        f.append(line(W / 2, 90 + ch / 2, W / 2, 200 - bh2 / 2, color=NEG, sw=2))

    f.append(text(W / 2, 400, "однакові running_time ⇒ однакова мить показу; більше нічого спільного",
                  size=13, color=INK, bold=True))

    render(os.path.join(OUT, 'two-machines.svg'), W, H, *f,
           title="Синхронність між процесами: спільний годинник плюс спільний base_time")


# ── 5. Мапа контракту часу (до довідки інтерфейсів) ─────────────────────────
def fig_time_contract_map():
    W, H = 1000, 800
    f = []

    cx = 330
    boxes = [
        (115, ["GstBuffer", "PTS · DTS · DURATION", "GST_BUFFER_PTS(buf)"]),
        (275, ["GstSegment (подія SEGMENT)", "start · offset · base · rate", "gst_segment_to_running_time()"]),
        (435, ["base_time елемента", "gst_element_get_base_time()", "плюс latency з події LATENCY"]),
        (595, ["GstClock", "gst_clock_get_time()", "gst_clock_id_wait(id, &jitter)"]),
        (740, ["GstBaseSink", "sync · ts-offset · max-lateness", "показ · скидання · подія QoS"]),
    ]
    hs = []
    for cy, lines in boxes:
        box, w, h = textbox(cx, cy, lines, size=13, pad=12, min_w=260)
        f.append(box)
        hs.append((cy, h))

    labels = [
        "мітка у шкалі медіа",
        "running_time = (PTS − start) / |rate| + base",
        "sync_time = running_time + base_time + latency",
        "порівняння: рано · вчасно · пізно",
    ]
    for i in range(4):
        y1 = hs[i][0] + hs[i][1] / 2 + 4
        y2 = hs[i + 1][0] - hs[i + 1][1] / 2 - 6
        f.append(arrow(cx, y1, cx, y2, color=NEG))
        f.append(text(500, (y1 + y2) / 2 + 5, labels[i], size=13,
                      color=NEG if i in (1, 2) else MUTED, anchor="start"))

    render(os.path.join(OUT, 'time-contract-map.svg'), W, H, *f,
           title="Ланцюг чисел: від мітки буфера до рішення споживача")


# ── 6. Ланцюг сегментів: PTS як функція running_time ───────────────────────
def fig_segment_chain():
    W, H = 900, 540
    f = []

    X0, X1 = 90, 850          # running_time 0 … 28 с
    Y0, Y1 = 430, 90          # PTS 0 … 20 с (Y0 — низ)
    KX = (X1 - X0) / 28.0
    KY = (Y0 - Y1) / 20.0

    def px(rt):
        return X0 + rt * KX

    def py(pts):
        return Y0 - pts * KY

    # осі
    f.append(arrow(X0, Y0, X1 + 20, Y0))
    f.append(arrow(X0, Y0, X0, Y1 - 20))
    f.append(text(X0 + 6, Y1 - 30, "PTS, с", size=13, color=MUTED, anchor="start"))
    f.append(text(X1 + 20, Y0 + 46, "running_time, с", size=13, color=MUTED, anchor="end"))

    # позначки на осі PTS
    for v in (0, 5, 15, 20):
        f.append(line(X0 - 6, py(v), X0, py(v), color=INK, sw=1.5))
        f.append(text(X0 - 12, py(v) + 5, str(v), size=12, color=MUTED, anchor="end"))

    # шви — світлі вертикалі на всю висоту
    for rt in (10, 20):
        f.append(line(px(rt), Y1 - 10, px(rt), Y0, color=MUTED, sw=1.1, dash="5 5"))
        f.append(line(px(rt), Y0, px(rt), Y0 + 6, color=INK, sw=1.5))
        f.append(text(px(rt), Y0 + 24, str(rt), size=12, color=MUTED))
    f.append(text(X0, Y0 + 24, "0", size=12, color=MUTED))
    f.append(text(px(10), Y0 + 50, "base₂ = 10 с", size=12, color=FIELD, bold=True))
    f.append(text(px(20), Y0 + 50, "base₃ = 20 с", size=12, color=FIELD, bold=True))

    # три гілки
    f.append(line(px(0), py(0), px(10), py(20), color=POS, sw=2.6))
    f.append(line(px(10), py(15), px(20), py(5), color=NEG, sw=2.6))
    f.append(line(px(20), py(0), px(28), py(8), color=POS, sw=2.6))

    # розриви PTS на швах
    for rt, a, b in ((10, 20, 15), (20, 5, 0)):
        f.append(line(px(rt), py(a), px(rt), py(b), color=MUTED, sw=1.6, dash="3 4"))
        f.append(circle(px(rt), py(a), 4, fill=BG, stroke=INK, sw=1.6))
        f.append(circle(px(rt), py(b), 4, fill=INK, stroke=INK, sw=1.6))

    f.append(mtext(200, 348, ["сегмент 1 · rate = +2.0",
                              "нахил удвічі крутіший"], size=13, color=INK))
    f.append(mtext(510, 118, ["сегмент 2 · rate = −1.0",
                              "PTS спадає — running_time росте"], size=13, color=INK))
    f.append(mtext(755, 232, ["сегмент 3 · rate = +1.0",
                              "інший файл, PTS знову з нуля"], size=13, color=INK))

    f.append(text(X0, Y0 + 76, "по горизонталі рух лише вправо: жоден шов не повертає running_time назад",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'segment-chain.svg'), W, H, *f,
           title="PTS як функція running_time: три сегменти підряд")


# ── 7. rate проти applied_rate ─────────────────────────────────────────────
def fig_rate_vs_applied():
    W, H = 900, 420
    f = []

    a1, w1, h1 = textbox(190, 140, ["сегмент А",
                                    "rate = 2.0, applied_rate = 1.0",
                                    "буфер несе PTS = 12.000 с"],
                         size=13, pad=12, fill="#fdecea", stroke=POS, sw=2)
    a2, w2, h2 = textbox(530, 140, ["running_time = 12.000 / 2.0 = 6.000 с",
                                    "stream_time = 12.000 · 1.0 = 12.000 с"],
                         size=13, pad=12)
    b1, w3, h3 = textbox(190, 292, ["сегмент Б",
                                    "rate = 1.0, applied_rate = 2.0",
                                    "той самий кадр несе PTS = 6.000 с"],
                         size=13, pad=12, fill="#eaf0fd", stroke=NEG, sw=2)
    b2, w4, h4 = textbox(530, 292, ["running_time = 6.000 / 1.0 = 6.000 с",
                                    "stream_time = 6.000 · 2.0 = 12.000 с"],
                         size=13, pad=12)
    c, w5, h5 = textbox(790, 216, ["однакові", "6.000 с", "і 12.000 с"],
                        size=13, pad=12, fill="#eafaf0", stroke=FIELD, sw=2)
    f += [a1, a2, b1, b2, c]

    f.append(arrow(190 + w1 / 2 + 6, 140, 530 - w2 / 2 - 6, 140, color=POS))
    f.append(arrow(190 + w3 / 2 + 6, 292, 530 - w4 / 2 - 6, 292, color=NEG))
    f.append(arrow(530 + w2 / 2 + 6, 140, 790 - w5 / 2 - 6, 216 - 16, color=MUTED))
    f.append(arrow(530 + w4 / 2 + 6, 292, 790 - w5 / 2 - 6, 216 + 16, color=MUTED))

    f.append(text(W / 2, 380, "rate · applied_rate = 2.0 в обох рядках",
                  size=15, color=INK, bold=True))

    render(os.path.join(OUT, 'rate-vs-applied.svg'), W, H, *f,
           title="Одна швидкість, два розклади: хто саме прискорює дані")


# ── 7. Порядок старту двох машин (вставка proj-net-clock-sync) ──────────────
def fig_net_sync_startup():
    W, H = 1160, 560
    f = []

    yb1, yb2, bh = 150, 330, 76          # ряди рамок і їхня висота
    x1, w1 = 190, 260
    x2, w2 = 475, 260
    x3, w3 = 760, 220
    xT = 1050                            # вертикаль спільного base_time

    # майстер
    f.append(text(20, 186, "машина A — майстер", size=13, anchor="start", bold=True))
    f.append(text(20, 208, "роздає час і base_time", size=11, color=MUTED, anchor="start"))
    f.append(fitbox(x1, yb1, w1, bh,
                    ["gst_net_time_provider_new", "UDP :5637 — час назовні"], size=12))
    f.append(fitbox(x2, yb1, w2, bh,
                    ["дочекався всіх підлеглих,", "T = now + 1 с,", "роздає T по TCP"], size=12))
    f.append(fitbox(x3, yb1, w3, bh,
                    ["set_base_time(T)", "PAUSED → PLAYING"], size=12))
    f.append(arrow(x1 + w1 + 2, yb1 + bh / 2, x2 - 2, yb1 + bh / 2))
    f.append(arrow(x2 + w2 + 2, yb1 + bh / 2, x3 - 2, yb1 + bh / 2))

    # підлеглий
    f.append(text(20, 366, "машина B — підлеглий", size=13, anchor="start", bold=True))
    f.append(text(20, 388, "бере час і base_time", size=11, color=MUTED, anchor="start"))
    f.append(fitbox(x1, yb2, w1, bh,
                    ["gst_net_client_clock_new", "wait_for_sync — блокує,",
                     "поки годинник не зійшовся"], size=12))
    f.append(fitbox(x2, yb2, w2, bh,
                    ["з'єднується з майстром", "і читає T"], size=12))
    f.append(fitbox(x3, yb2, w3, bh,
                    ["set_base_time(T)", "PAUSED → PLAYING"], size=12))
    f.append(arrow(x1 + w1 + 2, yb2 + bh / 2, x2 - 2, yb2 + bh / 2))
    f.append(arrow(x2 + w2 + 2, yb2 + bh / 2, x3 - 2, yb2 + bh / 2))

    # «годинник зійшовся» — знизу вгору; T — згори вниз
    f.append(arrow(400, yb2 - 2, 500, yb1 + bh + 2, color=NEG))
    f.append(text(345, 300, "«годинник зійшовся»", size=11, color=NEG, anchor="end"))
    f.append(arrow(605, yb1 + bh + 2, 605, yb2 - 2, color=FIELD))
    f.append(text(622, 288, "T по TCP", size=11, color=FIELD, anchor="start"))

    # вісь часу
    f.append(arrow(190, 470, 1120, 470))
    f.append(text(190, 496, "час за спільним годинником →", size=12, color=MUTED, anchor="start"))
    f.append(line(870, 460, 870, 480, color=INK, sw=2))
    f.append(text(870, 450, "обидва в PLAYING", size=11, color=MUTED))
    f.append(line(xT, 122, xT, 470, color=NEG, sw=2, dash="6 5"))
    f.append(line(xT, 458, xT, 482, color=NEG, sw=2.5))
    f.append(text(xT - 12, 96, "T — спільний base_time", size=13, color=NEG,
                  anchor="end", bold=True))
    f.append(text(xT - 12, 118, "тут виходить перший кадр — на обох машинах",
                  size=12, color=MUTED, anchor="end"))

    # запас між PLAYING і T
    f.append(line(872, 505, 1048, 505, color=FIELD, sw=2))
    f.append(line(872, 498, 872, 512, color=FIELD, sw=2))
    f.append(line(1048, 498, 1048, 512, color=FIELD, sw=2))
    f.append(text(960, 526, "запас: споживач тримає перший кадр", size=11, color=FIELD))

    render(os.path.join(OUT, 'net-sync-startup.svg'), W, H, *f,
           title="Порядок старту: спершу годинник, потім спільний base_time")


# ── 8. Бюджет залишкової розбіжності ────────────────────────────────────────
def fig_sync_error_budget():
    W, H = 1180, 470
    f = []

    x0, k = 340, 40.0                    # 0 мс і масштаб: 40 px на мілісекунду
    rows = [
        (110, 0.2, 3.0,  "мережевий годинник у LAN", "0.2 … 3 мс",   "#eaf0fd", NEG),
        (185, 0.1, 1.5,  "планувальник і споживач",  "0.1 … 1.5 мс", "#f0f2f5", MUTED),
        (260, 0.0, 16.7, "кадрова розгортка 60 Гц",  "0 … 16.7 мс",  "#fdecea", POS),
    ]

    for y, a, b, name, val, fill, col in rows:
        f.append(rect(x0 + a * k, y, (b - a) * k, 40, fill=fill, stroke=col, sw=2))
        f.append(text(x0 - 18, y + 26, name, size=13, anchor="end"))
        f.append(text(x0 + b * k + 14, y + 26, val, size=12, color=col, anchor="start"))

    f.append(line(x0, 350, 1150, 350, color=INK, sw=1.5))
    for ms in (0, 5, 10, 15, 20):
        x = x0 + ms * k
        f.append(line(x, 350, x, 358, color=INK, sw=1.5))
        f.append(text(x, 376, str(ms), size=12, color=MUTED))
    f.append(text(745, 402, "розбіжність між двома машинами, мс", size=12, color=MUTED))

    box, bw, bh = textbox(590, 440,
                          "PTP ріже перший рядок до десятків мікросекунд;"
                          " третій не ріже ніщо — він у розгортці екрана",
                          size=12, pad=12)
    f.append(box)

    render(os.path.join(OUT, 'sync-error-budget.svg'), W, H, *f,
           title="Що лишається розбіжним, коли годинник і base_time уже спільні")


fig_three_axes()
fig_sink_decision()
fig_live_latency()
fig_two_machines()
fig_time_contract_map()
fig_segment_chain()
fig_rate_vs_applied()
fig_net_sync_startup()
fig_sync_error_budget()
print("ok")
