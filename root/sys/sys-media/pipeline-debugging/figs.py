# -*- coding: utf-8 -*-
"""Фігури до теми «Діагностика конвеєра»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

TINT_OK = "#eaf3ec"
TINT_HI = "#eaf0fd"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Як читати DOT-дамп конвеєра
# ─────────────────────────────────────────────────────────────────────────────
def element(x, y, w, h, name, state, sinks, srcs):
    """Прямокутник елемента з назвою, станом і падами-підрамками.
    Повертає (svg, anchors) — anchors['sink'][i] / anchors['src'][i] = (x, y)."""
    out = rect(x, y, w, h, fill="#ffffff", stroke=LINE, sw=1.8, rx=8)
    out += text(x + w / 2, y + 24, name, size=15, bold=True)
    out += text(x + w / 2, y + 44, state, size=11, color=MUTED)
    pw, ph = 68, 24
    anchors = {'sink': [], 'src': []}
    for i, s in enumerate(sinks):
        py = y + 64 + i * 40
        out += fitbox(x + 8, py, pw, ph, s, size=11, pad=4, fill=FILL)
        anchors['sink'].append((x, py + ph / 2))
    for i, s in enumerate(srcs):
        py = y + 64 + i * 40
        out += fitbox(x + w - pw - 8, py, pw, ph, s, size=11, pad=4, fill=FILL)
        anchors['src'].append((x + w, py + ph / 2))
    return out, anchors


def fig_dot():
    W, H = 1000, 400
    f = []
    f.append(text(W / 2, 32, "Те саме, що видно на DOT-графі конвеєра", size=16, bold=True))

    e1, a1 = element(58, 76, 180, 110, "filesrc", "PLAYING", [], ["src"])
    e2, a2 = element(390, 76, 180, 150, "qtdemux", "PLAYING", ["sink"], ["video_0", "audio_0"])
    e3, a3 = element(722, 76, 180, 110, "h264parse", "PLAYING", ["sink"], ["src"])
    f += [e1, e2, e3]

    # з'єднані пади: суцільна лінія + узгоджені caps над нею
    f.append(arrow(a1['src'][0][0], a1['src'][0][1], a2['sink'][0][0], a2['sink'][0][1]))
    f.append(text(314, 122, "video/quicktime", size=12, color=NEG))
    f.append(arrow(a2['src'][0][0], a2['src'][0][1], a3['sink'][0][0], a3['sink'][0][1]))
    f.append(text(646, 122, "video/x-h264", size=12, color=NEG))

    # динамічний пад, який нікуди не веде
    ax, ay = a2['src'][1]
    f.append(line(ax, ay, ax + 66, ay + 34, color=POS, sw=1.8, dash="6 5"))
    f.append(text(ax + 80, ay + 42, "пад створено, але не з'єднано", size=12,
                  color=POS, anchor="start"))

    f.append(text(58, 320, "суцільна стрілка — пади з'єднані; напис над нею — формат, "
                           "на якому вони домовилися", size=13, anchor="start"))
    f.append(text(58, 348, "пунктир — пад існує, але його ніхто не підхопив: дані з цієї "
                           "гілки нікуди не йдуть", size=13, anchor="start"))
    f.append(text(58, 376, "рядок під назвою — стан елемента, коли граф скидали на диск",
                  size=13, anchor="start"))
    render(os.path.join(OUT, 'dot-graph-read.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Анатомія рядка журналу
# ─────────────────────────────────────────────────────────────────────────────
def fields_row(fields, cy, cx, gap=22):
    """fields = [(значення, підпис, підсвітити?)]. Малює ряд рамок із підписами знизу."""
    bh = 50
    widths = []
    for val, lab, _ in fields:
        w = max(text_width(val, 14, True), text_width(lab, 11)) + 28
        widths.append(w)
    total = sum(widths) + gap * (len(fields) - 1)
    x = cx - total / 2
    out = []
    for (val, lab, hi), w in zip(fields, widths):
        out.append(rect(x, cy, w, bh, fill=TINT_HI if hi else "#ffffff",
                        stroke=NEG if hi else LINE, sw=1.8 if hi else 1.4, rx=6))
        out.append(text(x + w / 2, cy + 31, val, size=14, bold=True,
                        color=NEG if hi else INK))
        out.append(text(x + w / 2, cy + bh + 20, lab, size=11, color=MUTED))
        x += w + gap
    return out


def fig_logline():
    W, H = 1100, 420
    f = []
    f.append(text(W / 2, 34, "На що розкладається один рядок GST_DEBUG", size=16, bold=True))
    cx = W / 2
    f += fields_row([("0:00:01.234567890", "час від старту", False),
                     ("1234", "pid", False),
                     ("0x55f1c0", "нитка", True),
                     ("WARN", "рівень", False)], 66, cx)
    f += fields_row([("basesrc", "категорія", False),
                     ("gstbasesrc.c:3127", "файл:рядок", False),
                     ("gst_base_src_loop", "функція", False),
                     ("<v4l2src0>", "об'єкт", True)], 176, cx)
    f += fields_row([("error: Internal data stream error.", "текст повідомлення", False)],
                    286, cx)
    f.append(mtext(cx, 384,
                   ["дві підсвічені колонки роблять журнал придатним для читання:",
                    "«об'єкт» каже, ЯКИЙ саме елемент говорить, «нитка» — у якому потоці це сталося"],
                   size=12, color=NEG, lh=1.35))
    render(os.path.join(OUT, 'log-line-anatomy.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Бісекція конвеєра
# ─────────────────────────────────────────────────────────────────────────────
def chain(x, y, names, colors, bw=126, bh=46, gap=26):
    out = []
    for i, (n, c) in enumerate(zip(names, colors)):
        bx = x + i * (bw + gap)
        out.append(fitbox(bx, y, bw, bh, n, size=13, pad=6, fill=c,
                          stroke=POS if c == "#fdecea" else (NEG if c == TINT_HI else LINE),
                          sw=1.8 if c != "#ffffff" else 1.4))
        if i:
            out.append(arrow(bx - gap, y + bh / 2, bx, y + bh / 2))
    return out


def fig_bisect():
    W, H = 990, 400
    f = []
    f.append(text(W / 2, 32, "Бісекція: кожен крок ділить конвеєр навпіл", size=16, bold=True))
    wht = "#ffffff"

    f.append(text(48, 78, "повний конвеєр: чорний екран, помилки на шині нема", size=13,
                  anchor="start", color=MUTED))
    f += chain(48, 92, ["rtspsrc", "depay", "parse", "decode", "convert", "sink"],
               [wht] * 6)

    f.append(text(48, 192, "хвіст відрізано — чи доходять кадри хоча б сюди?", size=13,
                  anchor="start", color=MUTED))
    f += chain(48, 206, ["rtspsrc", "depay", "parse", "fakesink"],
               [wht, wht, wht, TINT_HI])

    f.append(text(48, 306, "голову замінено — чи показує хвіст завідомо справне джерело?",
                  size=13, anchor="start", color=MUTED))
    f += chain(48, 320, ["videotestsrc", "convert", "sink"], [TINT_HI, wht, wht])

    render(os.path.join(OUT, 'pipeline-bisect.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Сторожовий таймер: три різні вироки о N-й секунді (вставка proj-)
# ─────────────────────────────────────────────────────────────────────────────
def fig_watchdog():
    W, H = 1020, 430
    wht = "#ffffff"
    bad = "#fdecea"
    f = []
    f.append(text(510, 30, "Сторожовий таймер: що він застає о N-й секунді",
                  size=16, bold=True))
    f.append(mtext(884, 54, ["N-та секунда:", "сторож питає стан"],
                   size=11, color=POS, lh=1.3))
    f.append(line(884, 78, 884, 392, color=POS, sw=1.6, dash="6 5"))

    lanes = [
        ("пуск удався",
         [("NULL", 240, 306, wht), ("READY", 306, 378, wht),
          ("PAUSED", 378, 470, wht), ("PLAYING", 470, 868, TINT_OK)],
         "PLAYING настав раніше — сторожа знято, доповідати нема про що"),
        ("затик у PAUSED",
         [("NULL", 240, 306, wht), ("READY", 306, 378, wht),
          ("PAUSED", 378, 868, bad)],
         "стан PAUSED, у черзі PLAYING → перший буфер не дійшов до стоку"),
        ("затик у READY",
         [("NULL", 240, 306, wht), ("READY", 306, 868, bad)],
         "стан READY, у черзі PAUSED → джерело так і не відкрилося"),
    ]

    y = 90
    for label, boxes, verdict in lanes:
        f.append(text(44, y + 28, label, size=13, anchor="start", bold=True))
        for name, x0, x1, col in boxes:
            f.append(fitbox(x0, y, x1 - x0, 44, name, size=12, pad=6, fill=col,
                            stroke=POS if col == bad else LINE,
                            sw=1.8 if col == bad else 1.4))
        f.append(text(240, y + 68, verdict, size=12, anchor="start", color=MUTED))
        y += 110

    f.append(arrow(240, 396, 898, 396, color=MUTED, sw=1.4))
    f.append(text(240, 418, "час від виклику set_state", size=11,
                  anchor="start", color=MUTED))
    render(os.path.join(OUT, 'proj-watchdog-verdicts.svg'), W, H, *f)


fig_dot()
fig_logline()
fig_bisect()
fig_watchdog()
print("ok")
