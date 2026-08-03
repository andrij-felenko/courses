# -*- coding: utf-8 -*-
"""Фігури до теми «Конвеєр: елементи, зв'язки й потік даних»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def pad_square(cx, cy, color=INK):
    """Пад — маленький квадратик на межі елемента."""
    return rect(cx - 8, cy - 8, 16, 16, fill="#ffffff", stroke=color, sw=2, rx=2)


# ── 1. Елемент, пади й напрямок потоку ─────────────────────────────────────
def fig_elements_and_pads():
    W, H = 940, 320
    f = []
    bw, bh, top = 180, 64, 80
    mid = top + bh / 2
    gap = (W - 60 - 4 * bw) / 3.0
    xs = [30 + i * (bw + gap) for i in range(4)]
    labels = [["джерело", "rtspsrc"],
              ["декодер", "avdec_h264"],
              ["перетворювач", "videoconvert"],
              ["стік", "autovideosink"]]
    for i, x in enumerate(xs):
        f.append(fitbox(x, top, bw, bh, labels[i], size=14, pad=10))
    # пади: у джерела лише вихідний, у стоку лише вхідний
    for i, x in enumerate(xs):
        if i > 0:
            f.append(pad_square(x + 14, mid))
        if i < 3:
            f.append(pad_square(x + bw - 14, mid))
    # стрілки між сусідніми елементами
    for i in range(3):
        f.append(arrow(xs[i] + bw + 4, mid, xs[i + 1] - 4, mid))
    # виноска про формат стику між другим і третім елементами
    lx = (xs[1] + bw + xs[2]) / 2.0
    f.append(line(lx, mid + 14, lx, 200, color=MUTED, sw=1.2, dash="4,4"))
    body, _, _ = textbox(lx, 232,
                         ["формат, про який домовилися ці два пади:",
                          "video/x-raw, format=NV12, width=1920, height=1080, framerate=30/1"],
                         size=12, pad=10, stroke=FIELD)
    f.append(body)
    # легенда
    f.append(rect(30, 285, 14, 14, fill="#ffffff", stroke=INK, sw=2, rx=2))
    f.append(text(52, 296,
                  "пад — іменована точка стику; у джерела лише вихідний, у стоку лише вхідний",
                  size=12, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "elements-and-pads.svg"), W, H, *f,
           title="Елемент, пади й напрямок потоку")


# ── 2. Push-передача і межа ниток ──────────────────────────────────────────
def fig_push_flow_threads():
    W, H = 940, 430
    f = []

    # --- верхній ряд: лінійний ланцюг, одна нитка
    f.append(text(30, 56, "Лінійний ланцюг: одна нитка на весь стек викликів",
                  size=14, anchor="start", bold=True))
    bw, bh, top = 185, 54, 80
    mid = top + bh / 2
    gap = (W - 60 - 4 * bw) / 3.0
    xs = [30 + i * (bw + gap) for i in range(4)]
    names = ["rtspsrc", "avdec_h264", "videoconvert", "autovideosink"]
    for i, x in enumerate(xs):
        f.append(fitbox(x, top, bw, bh, names[i], size=14, pad=10))
    for i in range(3):
        f.append(arrow(xs[i] + bw + 4, mid, xs[i + 1] - 4, mid))
        f.append(text((xs[i] + bw + xs[i + 1]) / 2.0, mid - 12, "push()",
                      size=10, color=MUTED))
    f.append(rect(30, 155, W - 60, 5, fill=NEG, stroke=NEG, sw=0, rx=2))
    f.append(text(W / 2.0, 182,
                  "одна нитка виконання, створена джерелом: увесь ланцюг — один стек викликів",
                  size=13, color=NEG))

    # --- нижній ряд: той самий ланцюг із queue
    f.append(text(30, 235, "Той самий ланцюг із елементом queue: дві нитки",
                  size=14, anchor="start", bold=True))
    bw2, bh2, top2 = 150, 54, 260
    mid2 = top2 + bh2 / 2
    gap2 = (W - 60 - 5 * bw2) / 4.0
    xs2 = [30 + i * (bw2 + gap2) for i in range(5)]
    names2 = ["rtspsrc", "avdec_h264", "queue", "videoconvert", "autovideosink"]
    for i, x in enumerate(xs2):
        st = FIELD if i == 2 else LINE
        f.append(fitbox(x, top2, bw2, bh2, names2[i], size=13, pad=8, stroke=st,
                        sw=2.4 if i == 2 else 1.5))
    for i in range(4):
        f.append(arrow(xs2[i] + bw2 + 4, mid2, xs2[i + 1] - 4, mid2))

    qc = xs2[2] + bw2 / 2.0
    f.append(rect(30, 335, qc - 35, 5, fill=NEG, stroke=NEG, sw=0, rx=2))
    f.append(rect(qc + 5, 335, W - 30 - (qc + 5), 5, fill=POS, stroke=POS, sw=0, rx=2))
    f.append(text((30 + qc - 35) / 2.0, 368, "нитка №1: джерело → queue",
                  size=12, color=NEG))
    f.append(text((qc + 5 + W - 30) / 2.0, 368, "нитка №2: queue → стік",
                  size=12, color=POS))
    f.append(text(W / 2.0, 404,
                  "queue приймає дані чужою ниткою, а віддає власною — межа ниток проходить саме тут",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "push-flow-threads.svg"), W, H, *f,
           title="Передача прямим викликом і місце, де ланцюг розривають")


# ── 3. Конвеєр як власник стану, годинника й шини ──────────────────────────
def fig_pipeline_as_object():
    W, H = 940, 410
    f = []
    # зовнішня рамка конвеєра
    f.append(rect(30, 56, 540, 220, fill="#fbfcfd", stroke=INK, sw=2, rx=10))
    f.append(text(300, 82, "Конвеєр — бін найвищого рівня", size=13, bold=True))
    bw, bh, top = 145, 54, 110
    mid = top + bh / 2
    xs = [50, 222, 394]
    names = ["джерело", "декодер", "стік"]
    for i, x in enumerate(xs):
        f.append(fitbox(x, top, bw, bh, names[i], size=13, pad=8))
    for i in range(2):
        f.append(arrow(xs[i] + bw + 4, mid, xs[i + 1] - 4, mid))
    f.append(mtext(300, 190,
                   ["стан міняється для всієї групи разом,",
                    "знизу вгору: NULL → READY → PAUSED → PLAYING"],
                   size=12))
    f.append(text(300, 246,
                  "вкладений бін виглядає ззовні як один елемент",
                  size=12, color=MUTED))

    # права колонка: годинник, шина, нитка застосунку
    b1, w1, h1 = textbox(755, 105, ["Годинник", "один на весь конвеєр:",
                                    "стоки міряють час ним"], size=12, pad=10)
    b2, w2, h2 = textbox(755, 225, ["Шина", "черга повідомлень",
                                    "від ниток обробки"], size=12, pad=10)
    b3, w3, h3 = textbox(755, 350, ["Нитка застосунку", "читає шину тоді,",
                                    "коли їй зручно"], size=12, pad=10)
    f += [b1, b2, b3]
    f.append(arrow(755 - w1 / 2 - 6, 105, 578, 105))
    f.append(arrow(578, 225, 755 - w2 / 2 - 6, 225))
    f.append(arrow(755, 225 + h2 / 2 + 6, 755, 350 - h3 / 2 - 6))
    render(os.path.join(IMG, "pipeline-as-object.svg"), W, H, *f,
           title="Що належить конвеєрові, а не окремому елементу")


# ── 4. (вставка proj) Щілина в ланцюзі й момент, коли її замикають ─────────
def fig_manual_chain_gap():
    W, H = 960, 520
    f = []
    names = ["rtspsrc", "rtph264depay", "h264parse", "avdec_h264",
             "videoconvert", "queue", "autovideosink"]
    bw, x0, gap_big, gap_sm = 110, 35, 70, 10

    def row_xs():
        xs, x = [], x0
        for i in range(7):
            xs.append(x)
            x += bw + (gap_big if i == 0 else gap_sm)
        return xs

    xs = row_xs()
    gap_cx = xs[0] + bw + gap_big / 2.0

    # --- смуга 1: після складання
    f.append(text(x0, 62, "1 · Після складання: сім елементів у біні, зв'язано шість",
                  size=13, anchor="start", bold=True))
    top1, bh = 78, 50
    mid1 = top1 + bh / 2
    for i, x in enumerate(xs):
        f.append(fitbox(x, top1, bw, bh, names[i], size=12, pad=6))
    for i in range(1, 6):
        f.append(arrow(xs[i] + bw + 2, mid1, xs[i + 1] - 2, mid1))
    f.append(line(xs[0] + bw + 6, mid1, xs[1] - 6, mid1,
                  color=POS, sw=2, dash="6,5"))
    f.append(text(gap_cx, 148, "вихідного пада rtspsrc ще не існує",
                  size=11, color=POS))

    # --- смуга 2: після pad-added
    f.append(text(x0, 196, "2 · Коли надійшов SDP: обробник pad-added замикає щілину",
                  size=13, anchor="start", bold=True))
    top2 = 212
    mid2 = top2 + bh / 2
    for i, x in enumerate(xs):
        st = FIELD if i == 0 else LINE
        f.append(fitbox(x, top2, bw, bh, names[i], size=12, pad=6,
                        stroke=st, sw=2.2 if i == 0 else 1.5))
    for i in range(1, 6):
        f.append(arrow(xs[i] + bw + 2, mid2, xs[i + 1] - 2, mid2))
    f.append(arrow(xs[0] + bw + 6, mid2, xs[1] - 6, mid2, color=FIELD, sw=2.2))
    f.append(text(gap_cx, 282, "gst_pad_link(new_pad, sink_pad)",
                  size=11, color=FIELD))

    # --- смуга 3: порядок у часі
    f.append(text(x0, 334, "Порядок у часі", size=13, anchor="start", bold=True))
    ay = 382
    f.append(arrow(50, ay, 910, ay, color=MUTED, sw=1.6))
    ticks = [(95, ["gst_element_set_state", "(PLAYING)"]),
             (290, ["rtspsrc: DESCRIBE,", "SETUP, PLAY"]),
             (480, ["SDP розібрано,", "пади заведено"]),
             (670, ["спрацював pad-added,", "щілину замкнено"]),
             (860, ["перші кадри", "дійшли до вікна"])]
    for tx, lines in ticks:
        f.append(circle(tx, ay, 5, fill="#ffffff", stroke=MUTED, sw=2))
        f.append(mtext(tx, ay + 24, lines, size=11, color=INK))
    f.append(text(W / 2.0, 470,
                  "підписатися на pad-added треба ДО set_state: сигнал спрацьовує вже під час запуску",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "manual-chain-gap.svg"), W, H, *f,
           title="Щілина в ланцюзі й момент, коли її замикають")


# ── 5. (вставка proj) Хто кому винен посилання ─────────────────────────────
def fig_ref_ownership():
    W, H = 960, 476
    f = []
    cw = [280, 250, 350]
    cx0 = 35
    xs = [cx0, cx0 + cw[0], cx0 + cw[0] + cw[1]]
    hy, hh, rh = 58, 38, 44
    heads = ["виклик", "що ви отримали", "що зобов'язані зробити"]
    for i in range(3):
        f.append(fitbox(xs[i], hy, cw[i], hh, heads[i], size=12, pad=6,
                        fill="#e8ecf1", bold=True))
    rows = [
        ("gst_element_factory_make()", "плавуче посилання",
         "віддати самому, якщо не додали в бін"),
        ("gst_bin_add_many()", "власником став бін",
         "нічого: далі за все відповідає бін"),
        ("gst_element_get_bus()", "+1 посилання", "gst_object_unref(bus)"),
        ("gst_element_get_static_pad()", "+1 посилання", "gst_object_unref(pad)"),
        ("gst_bus_timed_pop_filtered()", "повідомлення ваше",
         "gst_message_unref(msg)"),
        ("gst_message_parse_error()", "GError і рядок подробиць",
         "g_clear_error(&err) і g_free(dbg)"),
        ("gst_object_unref(pipeline)", "бін звільняє все всередині",
         "перед цим — set_state(NULL)"),
    ]
    for r, (a, b, c) in enumerate(rows):
        y = hy + hh + r * rh
        fill = "#ffffff" if r % 2 == 0 else FILL
        for i, s in enumerate((a, b, c)):
            f.append(fitbox(xs[i], y, cw[i], rh, s, size=12, pad=6, fill=fill))
    yend = hy + hh + len(rows) * rh
    f.append(text(W / 2.0, yend + 30,
                  "у бін додано — бін і звільнить; узято окремо — віддавати вручну",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "ref-ownership.svg"), W, H, *f,
           title="Хто кому винен посилання в цій програмі")


if __name__ == "__main__":
    fig_elements_and_pads()
    fig_push_flow_threads()
    fig_pipeline_as_object()
    fig_manual_chain_gap()
    fig_ref_ownership()
    print("ok:", os.listdir(IMG))
