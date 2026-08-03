# -*- coding: utf-8 -*-
"""Фігури до теми «Затримка й буферизація в конвеєрі» (reference/media-vision/gstreamer)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def bracket(x1, x2, y, down=False, color=MUTED, sw=1.3):
    """Горизонтальна дужка з засічками на кінцях."""
    d = 7 if down else -7
    return (line(x1, y, x2, y, color=color, sw=sw) +
            line(x1, y, x1, y + d, color=color, sw=sw) +
            line(x2, y, x2, y + d, color=color, sw=sw))


# ── 1. Чому кадр не можна показати «вчасно» ─────────────────────────────────
def fig_render_deadline():
    W, H = 920, 470
    X0, X1 = 210, 870
    TC, ARR, DL = 270, 560, 720          # захоплення, прибуття, зсунутий дедлайн
    f = []

    def row(y, cap, deadline_x, note, note_color):
        p = [text(24, y - 86, cap, size=14, bold=True, anchor="start", color=INK)]
        # вісь малюємо двома шматками, щоб лінія не перетинала напис у смузі
        p.append(line(X0, y, TC, y, color=MUTED, sw=1.2))
        p.append(line(ARR, y, X1, y, color=MUTED, sw=1.2))
        # смуга «шлях кадру конвеєром»
        p.append(fitbox(TC, y - 15, ARR - TC, 30, "шлях кадру конвеєром", size=12))
        # позначка захоплення
        p.append(line(TC, y - 22, TC, y + 22, color=INK, sw=1.6))
        p.append(text(TC, y + 42, "захоплено (t)", size=12, color=MUTED))
        # прибуття
        p.append(circle(ARR, y, 6, fill=POS, stroke=POS, sw=1.2))
        p.append(text(ARR, y + 42, "прибуло до споживача", size=12, color=MUTED))
        # дедлайн
        p.append(line(deadline_x, y - 40, deadline_x, y + 26, color=NEG, sw=1.6, dash="6,4"))
        p.append(text(deadline_x, y - 50, "дедлайн", size=12, color=NEG, bold=True))
        p.append(text(X0 + 4, y - 50, note, size=13, color=note_color, anchor="start"))
        return "".join(p)

    # рядок А: дедлайн = t
    yA = 150
    f.append(row(yA, "Дедлайн збігається з міткою часу", TC, "", INK))
    f.append(text(X1, yA - 50, "кадр завжди спізнюється — його викидають",
                  size=13, color=POS, anchor="end"))

    # рядок Б: дедлайн = t + L
    yB = 360
    f.append(row(yB, "Дедлайн зсунуто на узгоджену затримку L", DL, "", INK))
    f.append(bracket(TC, DL, yB - 62, down=True, color=FIELD))
    f.append(text((TC + DL) / 2, yB - 70, "затримка L", size=12, color=FIELD, bold=True))
    f.append(bracket(ARR, DL, yB + 62, down=False, color=FIELD))
    f.append(text((ARR + DL) / 2, yB + 78, "запас", size=12, color=FIELD))

    render(os.path.join(IMG, 'render-deadline.svg'), W, H, *f,
           title="Чому живий кадр не можна показати «точно за міткою»")


# ── 2. Вікна затримки гілок і їх перетин ───────────────────────────────────
def fig_latency_windows():
    W, H = 940, 520
    def X(ms):
        return 170 + ms * 1.8            # 0 мс → 170 px, 300 мс → 710 px

    def bar(y, lo, hi, color, fill):
        x1, x2 = X(lo), X(hi)
        return (rect(x1, y - 11, x2 - x1, 22, fill=fill, stroke=color, sw=1.6, rx=4) +
                text(x2 + 12, y + 5, "%d…%d мс" % (lo, hi), size=12,
                     color=MUTED, anchor="start"))

    def axis(y):
        p = [line(X(0), y, X(320), y, color=MUTED, sw=1.2)]
        for ms in (0, 100, 200, 300):
            p.append(line(X(ms), y - 5, X(ms), y + 5, color=MUTED, sw=1.2))
            p.append(text(X(ms), y + 22, str(ms), size=11, color=MUTED))
        p.append(text(X(320) + 16, y + 5, "мс", size=11, color=MUTED, anchor="start"))
        return "".join(p)

    f = []
    # панель А — перетин є
    f.append(text(24, 66, "Вікна гілок перетинаються — домовленість є",
                  size=14, bold=True, anchor="start"))
    f.append(text(24, 112, "гілка відео", size=12, anchor="start", color=INK))
    f.append(bar(108, 40, 250, NEG, "#eaf0fd"))
    f.append(text(24, 152, "гілка звуку", size=12, anchor="start", color=INK))
    f.append(bar(148, 10, 200, NEG, "#eaf0fd"))
    f.append(text(24, 192, "перетин", size=12, anchor="start", color=FIELD))
    f.append(bar(188, 40, 200, FIELD, "#e7f7ee"))
    f.append(axis(232))
    f.append(line(X(40), 200, X(40), 268, color=FIELD, sw=1.6, dash="5,4"))
    f.append(text(X(40) + 10, 288, "обрано 40 мс = MAX(мінімумів); стеля 200 мс = MIN(максимумів)",
                  size=12, color=FIELD, anchor="start"))

    # панель Б — перетину немає
    f.append(text(24, 356, "Та сама гілка звуку без черги — перетину немає",
                  size=14, bold=True, anchor="start"))
    f.append(text(24, 402, "гілка відео", size=12, anchor="start", color=INK))
    f.append(bar(398, 40, 250, NEG, "#eaf0fd"))
    f.append(text(24, 442, "гілка звуку", size=12, anchor="start", color=INK))
    f.append(bar(438, 10, 30, POS, "#fdecea"))
    f.append(axis(482))
    f.append(text(X(60), 402, "потрібно щонайменше 40 мс", size=12,
                  color=MUTED, anchor="start"))
    f.append(text(X(60), 442, "витримує щонайбільше 30 мс → неможливо", size=12,
                  color=POS, anchor="start"))

    render(os.path.join(IMG, 'latency-windows.svg'), W, H, *f,
           title="Домовленість — це перетин вікон [min, max] усіх гілок")


# ── 3. Затримка проти буферизації ──────────────────────────────────────────
def fig_latency_vs_buffering():
    W, H = 920, 470
    f = []

    # ── не-живий потік: пауза
    f.append(text(24, 68, "Не-живе джерело: можна зупинитися й дочекатися",
                  size=14, bold=True, anchor="start"))
    yt = 150
    f.append(line(120, yt, 410, yt, color=MUTED, sw=1.2))
    f.append(line(560, yt, 870, yt, color=MUTED, sw=1.2))
    for x in (140, 180, 220, 260, 300, 340):
        f.append(rect(x, yt - 9, 18, 18, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
    f.append(fitbox(410, yt - 26, 150, 52, "PAUSED\nдобираємо дані", size=12,
                    fill="#fff6e0", stroke="#b8860b"))
    for x in (600, 640, 680, 720, 760, 800):
        f.append(rect(x, yt - 9, 18, 18, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
    f.append(text(120, yt + 46, "потік не прив'язаний до реального часу — пауза нічого не коштує",
                  size=12, color=MUTED, anchor="start"))

    # ── живий потік: сталий зсув
    f.append(text(24, 262, "Живе джерело: зупинятися нікуди — лише сталий зсув",
                  size=14, bold=True, anchor="start"))
    yc, yr = 330, 410
    f.append(line(200, yc, 870, yc, color=MUTED, sw=1.2))
    f.append(line(200, yr, 870, yr, color=MUTED, sw=1.2))
    f.append(text(24, yc + 5, "захоплено", size=12, anchor="start", color=INK))
    f.append(text(24, yr + 5, "показано", size=12, anchor="start", color=INK))
    caps = [230, 300, 370, 440, 510, 580, 650, 720]
    for i, x in enumerate(caps):
        f.append(line(x, yc - 10, x, yc + 10, color=NEG, sw=2))
        if i == 4:                                   # кадр загубився
            f.append(text(x + 80, yr + 6, "×", size=22, color=POS, bold=True))
        else:
            f.append(line(x + 80, yr - 10, x + 80, yr + 10, color=NEG, sw=2))
            f.append(line(x + 4, yc + 12, x + 76, yr - 12, color=MUTED, sw=1))
    f.append(bracket(230, 310, yc - 34, down=True, color=FIELD))
    f.append(text(270, yc - 42, "сталий зсув L", size=12, color=FIELD, bold=True))
    f.append(text(870, yr + 42, "даних не було → пропуск, а не пауза",
                  size=12, color=POS, anchor="end"))

    render(os.path.join(IMG, 'latency-vs-buffering.svg'), W, H, *f,
           title="Дві різні відповіді на нестачу даних")


# ── 4. Наростання затримки в черзі ─────────────────────────────────────────
def fig_queue_creep():
    W, H = 960, 400
    XL, XR = 130, 660
    YT, YB = 110, 330
    f = []

    f.append(line(XL, YB, XR + 20, YB, color=MUTED, sw=1.2))
    f.append(line(XL, YT - 20, XL, YB, color=MUTED, sw=1.2))
    f.append(text(XR + 24, YB + 6, "час", size=12, color=MUTED, anchor="start"))
    f.append(text(XL, YT - 34, "заповнення черги", size=12, color=MUTED, anchor="start"))
    f.append(line(XL, YT, XR, YT, color=MUTED, sw=1, dash="5,5"))
    f.append(text(XL - 12, YT + 5, "повна", size=11, color=MUTED, anchor="end"))
    f.append(text(XL - 12, YB + 5, "0", size=11, color=MUTED, anchor="end"))

    # звичайна черга: наростає й лишається повною
    pts = [(150, YB), (200, 268), (250, 216), (310, 168), (380, YT), (XR, YT)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), POS))

    # черга, що скидає старе: пилка внизу
    saw = [(150, YB)]
    x = 150
    while x < XR - 30:
        saw.append((x + 45, 286)); saw.append((x + 52, YB - 6)); x += 52
    saw.append((XR, YB - 10))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join("%.1f,%.1f" % p for p in saw), NEG))

    f.append(mtext(700, YT + 4, ["звичайна черга:",
                                 "наповнилась і не спорожняється",
                                 "→ зайвий зсув назавжди"],
                   size=12, color=POS, anchor="start", lh=1.45))
    f.append(mtext(700, 276, ["leaky=downstream:",
                              "найстаріші кадри викидаються",
                              "→ черга лишається мілкою"],
                   size=12, color=NEG, anchor="start", lh=1.45))

    render(os.path.join(IMG, 'queue-creep.svg'), W, H, *f,
           title="Черга між живим джерелом і повільним споживачем")


# ── 5. Що показує зонд у кожній точці (до вставки proj-latency-probe) ───────
def fig_probe_points():
    W, H = 1000, 500
    f = []

    # ── верх: конвеєр із трьома точками вимірювання
    BW, GAP, BY, BH = 168, 15, 74, 46
    X0 = 34
    boxes = ["rtspsrc\nlatency=200", "rtph264depay", "avdec_h264",
             "videoconvert", "autovideosink"]
    xs = []
    for i, cap in enumerate(boxes):
        x = X0 + i * (BW + GAP)
        xs.append(x)
        f.append(fitbox(x, BY, BW, BH, cap, size=12))
        if i:
            f.append(line(x - GAP, BY + BH / 2, x, BY + BH / 2, color=MUTED, sw=1.4))

    # маркери точок: після депейлоадера, після декодувальника, на вході споживача
    marks = [(xs[1] + BW, "1"), (xs[2] + BW, "2"), (xs[4], "3")]
    for mx, num in marks:
        f.append(circle(mx, BY - 16, 12, fill="#e7f7ee", stroke=FIELD, sw=1.8))
        f.append(text(mx, BY - 11, num, size=12, color=FIELD, bold=True))

    # ── низ: виміряний вік буфера в кожній точці
    XA, SCALE = 300, 2.35                     # 0 мс → 300 px, 260 мс → 911 px
    def X(ms):
        return XA + ms * SCALE

    rows = [("1", "після депейлоадера", 201, 201),
            ("2", "після декодувальника", 209, 8),
            ("3", "на вході споживача", 212, 3)]

    f.append(text(34, 190, "виміряний вік буфера — скільки минуло від захоплення",
                  size=13, bold=True, anchor="start"))
    f.append(text(958, 190, "приріст", size=12, color=MUTED, anchor="end"))

    for i, (num, cap, val, delta) in enumerate(rows):
        y = 232 + i * 54
        f.append(circle(56, y + 11, 11, fill="#e7f7ee", stroke=FIELD, sw=1.6))
        f.append(text(56, y + 16, num, size=12, color=FIELD, bold=True))
        f.append(text(78, y + 16, cap, size=12, anchor="start", color=INK))
        f.append(rect(XA, y, X(val) - XA, 23, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
        f.append(text(X(val) - 12, y + 16, "%d мс" % val, size=12,
                      color=NEG, anchor="end", bold=True))
        f.append(text(958, y + 16, "+%d мс" % delta, size=12,
                      color=MUTED, anchor="end"))

    # вісь
    ya = 412
    f.append(line(XA, ya, X(268), ya, color=MUTED, sw=1.2))
    for ms in (0, 50, 100, 150, 200, 250):
        f.append(line(X(ms), ya - 5, X(ms), ya + 5, color=MUTED, sw=1.2))
        f.append(text(X(ms), ya + 22, str(ms), size=11, color=MUTED))
    f.append(text(X(268) + 14, ya + 5, "мс", size=11, color=MUTED, anchor="start"))

    # узгоджена затримка
    f.append(line(X(220), 214, X(220), ya, color=POS, sw=1.7, dash="6,4"))
    f.append(text(X(220), 206, "узгоджено 220 мс", size=12, color=POS, bold=True))

    f.append(text(34, 462, "Майже весь вік накопичено ще до депейлоадера — "
                           "важіль тут один: latency буфера джитера.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'probe-points.svg'), W, H, *f,
           title="Три зонди на конвеєрі: де саме накопичується вік буфера")


# ── 6. Чому середнє бреше: розкид проти дедлайну ───────────────────────────
def fig_probe_slack():
    W, H = 940, 450
    XA, BASE = 140, 356
    def X(ms):
        return XA + (ms - 178) * 6.15         # 178 мс → 140 px, 300 мс → 890 px

    # правостороннє скошення: підлога 200 мс і важкий хвіст
    bars = [(180, 2), (184, 3), (188, 5), (192, 10), (196, 26), (200, 62),
            (204, 108), (208, 150), (212, 138), (216, 104), (220, 74),
            (224, 52), (228, 38), (232, 28), (236, 22), (240, 17),
            (244, 13), (248, 10), (252, 8), (256, 7), (260, 6), (264, 5),
            (268, 4), (272, 4), (276, 3), (280, 3), (284, 2), (288, 2)]
    f = []
    for ms, hgt in bars:
        col, fill = (NEG, "#eaf0fd") if ms < 220 else (POS, "#fdecea")
        f.append(rect(X(ms), BASE - hgt, X(ms + 4) - X(ms) - 2, hgt,
                      fill=fill, stroke=col, sw=1.0, rx=2))

    # вісь
    f.append(line(XA, BASE, X(298), BASE, color=MUTED, sw=1.2))
    for ms in (180, 200, 220, 240, 260, 280):
        f.append(line(X(ms), BASE, X(ms), BASE + 6, color=MUTED, sw=1.2))
        f.append(text(X(ms), BASE + 26, str(ms), size=11, color=MUTED))
    f.append(text(XA, BASE + 54, "вік буфера на вході споживача, мс",
                  size=12, color=MUTED, anchor="start"))

    # дедлайн
    f.append(line(X(220), 62, X(220), BASE, color=POS, sw=1.8, dash="6,4"))
    f.append(text(X(220) + 12, 68, "дедлайн — узгоджена затримка 220 мс",
                  size=13, color=POS, bold=True, anchor="start"))
    # медіана
    f.append(line(X(212), 126, X(212), BASE, color=NEG, sw=1.8))
    f.append(text(X(212) - 12, 116, "медіана 212 мс — «запас 8 мс»",
                  size=12, color=NEG, bold=True, anchor="end"))
    # p95
    f.append(line(X(238), 168, X(238), BASE, color=INK, sw=1.6))
    f.append(text(X(238) + 12, 162, "p95 = 238 мс — на 18 мс запізно",
                  size=12, color=INK, bold=True, anchor="start"))

    # хвіст
    f.append(text(X(252), 250, "4% кадрів прибувають після дедлайну:",
                  size=12, color=POS, anchor="start"))
    f.append(text(X(252), 270, "споживач їх викидає, а середнє мовчить",
                  size=12, color=POS, anchor="start"))
    f.append(line(X(256), 282, X(252), BASE - 16, color=POS, sw=1.1, dash="4,3"))

    render(os.path.join(IMG, 'probe-slack.svg'), W, H, *f,
           title="Той самий вимір: середнє каже «встигаємо», хвіст каже інше")


# ── 7. Карта ручок уздовж конвеєра (до вставки api-latency-controls) ───────
def fig_knob_map():
    BW, GAP, X0 = 180, 22, 26
    W = X0 * 2 + 5 * BW + 4 * GAP
    H = 424
    BY, BH = 76, 52                       # рамка елемента
    KY = 160                              # перший рядок списку ручок
    EY, EH = 250, 54                      # плашка «що саме робить»
    f = []

    cols = [
        ("Джерело", "v4l2src · alsasrc · rtspsrc",
         ["do-timestamp", "buffer-time (мкс)", "latency-time (мкс)",
          "latency (rtspsrc, мс)"],
         "піднімає ПІДЛОГУ:\nданих раніше\nпросто не існує", POS, "#fdecea"),
        ("Буфер джитера", "rtpjitterbuffer",
         ["latency (мс)", "drop-on-latency", "mode", "do-retransmission",
          "rtx-delay (мс)"],
         "найбільша підлога\nв мережевому\nконвеєрі", POS, "#fdecea"),
        ("Черга", "queue · queue2 · multiqueue",
         ["max-size-time (нс)", "min-threshold-time", "leaky",
          "use-buffering", "high-watermark"],
         "піднімає СТЕЛЮ;\nпідлогу — лише\nmin-threshold-time", FIELD, "#e7f7ee"),
        ("Кодувальник", "x264enc · vah264enc",
         ["tune=zerolatency", "rc-lookahead", "bframes", "key-int-max"],
         "підлога = скільки\nмайбутнього треба\nбачити наперед", POS, "#fdecea"),
        ("Споживач", "GstBaseSink",
         ["sync", "processing-deadline", "max-lateness", "ts-offset",
          "render-delay"],
         "застосовує зсув\nі вирішує, що\nвикинути як пізнє", NEG, "#eaf0fd"),
    ]

    for i, (name, els, knobs, tag, col, fill) in enumerate(cols):
        x = X0 + i * (BW + GAP)
        f.append(rect(x, BY, BW, BH, fill="#f4f6f8", stroke=INK, sw=1.6))
        f.append(text(x + BW / 2, BY + 22, name, size=13, bold=True, color=INK))
        f.append(text(x + BW / 2, BY + 41, els, size=10, color=MUTED))
        f.append(mtext(x + 10, KY, knobs, size=11, color=INK,
                       anchor="start", lh=1.6))
        f.append(fitbox(x, EY, BW, EH, tag, size=11, color=col,
                        fill=fill, stroke=col, sw=1.3))
        if i < 4:
            f.append(arrow(x + BW + 3, BY + BH / 2, x + BW + GAP - 3, BY + BH / 2))

    f.append(rect(X0, 330, W - 2 * X0, 58, fill="#fff6e0", stroke="#b8860b", sw=1.4))
    f.append(mtext(W / 2, 354,
                   ["Рівень конвеєра: властивість latency (примусова підлога) ·",
                    "gst_bin_recalculate_latency() у відповідь на GST_MESSAGE_LATENCY"],
                   size=12, color=INK, lh=1.5))

    render(os.path.join(IMG, 'latency-knob-map.svg'), W, H, *f,
           title="Де в конвеєрі сидить кожна ручка затримки")


if __name__ == '__main__':
    fig_render_deadline()
    fig_latency_windows()
    fig_latency_vs_buffering()
    fig_queue_creep()
    fig_probe_points()
    fig_probe_slack()
    fig_knob_map()
    print("ok")
