# -*- coding: utf-8 -*-
"""Фігури до теми «Пади і з'єднання елементів» (reference/media-vision/gstreamer)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def padbox(cx, cy, label, muted=False):
    """Маленька рамка пада збоку від елемента."""
    body, w, h = textbox(cx, cy, label, size=12, pad=9,
                         fill=("#eef2f7" if not muted else "#ffffff"),
                         stroke=(LINE if not muted else MUTED),
                         color=(INK if not muted else MUTED))
    return body, w, h


# ── 1. Напрямок падів ───────────────────────────────────────────────────────
def fig_direction():
    W, H = 900, 300
    f = []
    f.append(fitbox(110, 110, 230, 110, "videotestsrc\n(джерело)", size=15))
    f.append(fitbox(520, 110, 250, 110, "videoconvert\n(перетворювач)", size=15))

    f.append(padbox(370, 165, "src")[0])
    f.append(padbox(490, 165, "sink")[0])
    f.append(padbox(800, 165, "src")[0])

    f.append(arrow(396, 165, 460, 165))
    f.append(text(428, 145, "дані", size=12, color=MUTED))
    f.append(arrow(824, 165, 872, 165))

    f.append(text(225, 258, "src — віддає з елемента", size=13, color=MUTED))
    f.append(text(645, 258, "sink — приймає в елемент", size=13, color=MUTED))
    render(os.path.join(IMG, 'pad-direction.svg'), W, H, *f,
           title="Пади: напрямок називають від елемента")


# ── 2. Способи появи падів ──────────────────────────────────────────────────
def fig_presence():
    W, H = 1000, 370
    f = []
    cols = [
        (165, "videoconvert", [("sink", False)], [("src", False)],
         "ALWAYS\nпади є одразу після\nстворення елемента"),
        (500, "qtdemux", [("sink", False)], [("src_0", True), ("src_1", True)],
         "SOMETIMES\nз'являються, коли елемент\nрозбере вміст;\nсигнал pad-added"),
        (835, "tee", [("sink", False)], [("src_0", True), ("src_1", True)],
         "REQUEST\nстворюються на замовлення:\nrequest_pad_simple()"),
    ]
    for cx, name, sinks, srcs, caption in cols:
        f.append(fitbox(cx - 75, 70, 150, 100, name, size=15))
        for lbl, muted in sinks:
            f.append(padbox(cx - 112, 120, lbl, muted)[0])
            f.append(line(cx - 86, 120, cx - 76, 120, color=MUTED))
        ys = [120] if len(srcs) == 1 else [95, 145]
        for (lbl, muted), y in zip(srcs, ys):
            f.append(padbox(cx + 112, y, lbl, muted)[0])
            f.append(line(cx + 76, y, cx + 86, y, color=MUTED))
        f.append(fitbox(cx - 137, 205, 274, 118, caption, size=13,
                        fill="#ffffff", stroke=MUTED))
    render(os.path.join(IMG, 'pad-presence.svg'), W, H, *f,
           title="Три способи появи падів")


# ── 3. Штовхання: вкладені виклики chain-функцій ────────────────────────────
def fig_push():
    W, H = 980, 370
    f = []
    f.append(rect(40, 60, 900, 200, fill="#fbfcfd", stroke=MUTED, sw=1.2))
    f.append(text(60, 86, "один потік виконання", size=13,
                  color=MUTED, anchor="start"))

    f.append(fitbox(70, 110, 200, 80, "v4l2src\nштовхає", size=14))
    f.append(fitbox(390, 110, 200, 80, "x264enc\nchain()", size=14))
    f.append(fitbox(710, 110, 200, 80, "udpsink\nchain()", size=14))

    for x0, x1 in ((275, 385), (595, 705)):
        cx = (x0 + x1) / 2.0
        f.append(arrow(x0, 140, x1, 140))
        f.append(text(cx, 126, "gst_pad_push()", size=11, color=MUTED))
        f.append(arrow(x1, 172, x0, 172))
        f.append(text(cx, 196, "GST_FLOW_OK", size=11, color=MUTED))

    f.append(text(490, 300, "виклик не повертається, доки не відпрацює весь ланцюг", size=13))
    f.append(text(490, 330, "код повернення піднімається тим самим стеком назад", size=13, color=MUTED))
    render(os.path.join(IMG, 'push-chain.svg'), W, H, *f,
           title="Штовхання: src-пад кличе chain-функцію сусіда")


# ── 4. Привидний пад біна ───────────────────────────────────────────────────
def fig_ghost():
    W, H = 1000, 330
    f = []
    f.append(rect(250, 90, 500, 150, fill="#fbfcfd", stroke=LINE, sw=1.5))
    f.append(text(500, 116, "бін — сам є елементом, але власних падів не має",
                  size=13, color=MUTED))

    f.append(fitbox(290, 145, 170, 70, "h264parse", size=14))
    f.append(fitbox(540, 145, 180, 70, "avdec_h264", size=14))
    f.append(arrow(466, 180, 534, 180))

    f.append(padbox(215, 180, "ghost\nsink")[0])
    f.append(padbox(785, 180, "ghost\nsrc")[0])

    f.append(line(242, 180, 288, 180, color=MUTED, dash="4 3"))
    f.append(line(722, 180, 758, 180, color=MUTED, dash="4 3"))

    f.append(arrow(60, 180, 186, 180))
    f.append(text(123, 160, "дані ззовні", size=12, color=MUTED))
    f.append(arrow(814, 180, 940, 180))
    f.append(text(877, 160, "дані назовні", size=12, color=MUTED))

    f.append(text(500, 285, "привидний пад належить бінові, а роботу пересилає внутрішньому падові",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'ghost-pad.svg'), W, H, *f,
           title="Привидний пад: інтерфейс біна назовні")


# ── 5. Володіння посиланнями в API падів (до вставки api-pads.md) ───────────
def fig_ownership():
    W, H = 1020, 450
    f = []
    rows = [
        (70,
         "gst_pad_push(pad, buf)\ngst_pad_push_event(pad, ev)",
         "посилання ПЕРЕХОДИТЬ",
         "буфер уже не ваш —\nзвільнить той, хто прийняв"),
        (195,
         "gst_element_get_static_pad()\ngst_pad_get_peer()",
         "повертає ВАМ +1 посилання",
         "ваш обов'язок —\ngst_object_unref()"),
        (320,
         "GST_PAD_PROBE_INFO_DATA(info)\nу тілі проби",
         "лише ПОЗИЧЕНО на час виклику",
         "не звільняти; треба довше —\ngst_buffer_ref()"),
    ]
    for top, left, label, right in rows:
        f.append(fitbox(40, top, 340, 90, left, size=14))
        f.append(fitbox(650, top, 330, 90, right, size=14,
                        fill="#ffffff", stroke=MUTED))
        f.append(arrow(392, top + 45, 638, top + 45))
        f.append(text(515, top + 30, label, size=12, color=MUTED))
    render(os.path.join(IMG, 'pad-ownership.svg'), W, H, *f,
           title="Три режими володіння в API падів")


# ── 6. Дві фази динамічного з'єднання (до вставки proj-dynamic-linking.md) ──
def fig_dynlink_phases():
    W, H = 1040, 600
    f = []

    f.append(rect(30, 50, 980, 215, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(text(50, 78, "Фаза 1 · головний потік: складаємо статичну частину",
                  size=14, color=MUTED, anchor="start", bold=True))
    f.append(fitbox(70, 100, 180, 78, "filesrc", size=15))
    f.append(arrow(250, 139, 316, 139))
    f.append(fitbox(320, 100, 190, 78, "qtdemux", size=15))
    f.append(line(510, 139, 594, 139, color=MUTED, dash="5 4"))
    f.append(rect(600, 96, 380, 86, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(mtext(790, 130, ["src-падів ще немає:",
                              "заголовок MP4 не прочитано"], size=13, color=MUTED))
    f.append(text(520, 232, "gst_element_link(qtdemux, …) тут повертає FALSE",
                  size=13, color=POS))

    f.append(rect(30, 285, 980, 290, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(text(50, 313, "Фаза 2 · потік qtdemux: сигнал pad-added",
                  size=14, color=MUTED, anchor="start", bold=True))
    f.append(fitbox(70, 355, 190, 100, "qtdemux", size=15))
    for y, lbl in ((368, "src_0"), (444, "src_1")):
        f.append(line(260, y, 272, y, color=MUTED))
        f.append(padbox(300, y, lbl)[0])
        f.append(arrow(330, y, 414, y))
    f.append(fitbox(420, 336, 560, 64,
                    "гілка «відео»: queue → h264parse → avdec_h264 → videoconvert → autovideosink",
                    size=13))
    f.append(fitbox(420, 412, 560, 64,
                    "гілка «звук»: queue → aacparse → avdec_aac → audioconvert → autoaudiosink",
                    size=13))
    f.append(text(505, 522,
                  "гілку додають у конвеєр, з'єднують пади й лише тоді синхронізують стан",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'dynlink-phases.svg'), W, H, *f,
           title="Динамічне з'єднання: статична частина й гілки, що чіпляються потім")


# ── 7. Розрив гілки на ходу (до вставки proj-dynamic-linking.md) ────────────
def fig_dynlink_cut():
    W, H = 1040, 470
    f = []

    for y, name in ((60, "головний потік"),
                    (175, "потік qtdemux (streaming)"),
                    (290, "потік із пулу GStreamer")):
        f.append(rect(30, y, 980, 100, fill="#fbfcfd", stroke=MUTED, sw=1.2))
        f.append(text(46, y + 24, name, size=13, color=MUTED, anchor="start"))

    f.append(textbox(350, 122, "gst_pad_add_probe(src_0, IDLE, …)", size=13)[0])
    f.append(textbox(200, 237, "пад порожній → викликано пробу", size=13)[0])
    f.append(textbox(480, 237, "gst_pad_unlink(src_0, ghost)", size=13)[0])
    f.append(textbox(830, 237, "call_async(pipeline, teardown)", size=13)[0])
    f.append(textbox(400, 352, "set_state(гілка, NULL)", size=13)[0])
    f.append(textbox(760, 352, "gst_bin_remove(pipeline, гілка)", size=13)[0])

    f.append(arrow(300, 139, 300, 218))
    f.append(arrow(326, 237, 362, 237))
    f.append(arrow(596, 237, 703, 237))
    f.append(arrow(830, 256, 412, 332))
    f.append(arrow(492, 352, 623, 352))

    f.append(text(520, 430,
                  "різати можна лише там, де нічого не тече; стан міняти — лише в чужому потоці",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'dynlink-cut.svg'), W, H, *f,
           title="Від'єднання гілки на ходу: IDLE-проба й перенесення стану в інший потік")


if __name__ == '__main__':
    fig_direction()
    fig_presence()
    fig_push()
    fig_ghost()
    fig_ownership()
    fig_dynlink_phases()
    fig_dynlink_cut()
    print("ok")
