# -*- coding: utf-8 -*-
"""
Фігури для вставки r12-s3-a-descriptors.md
Рис. 4.12.3a.1 — 18 байтів Device-дескриптора горизонтальною стрічкою
Рис. 4.12.3a.2 — Дерево конфігурації: Config→Interface→Endpoint у одному буфері

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.3a.1 — 18 байтів Device-дескриптора стрічкою
# ══════════════════════════════════════════════════════════════════════════════
def fig1_device_bytes():
    W, H = 900, 380
    frags = []

    # Розмір кожної клітинки стрічки
    cell_w = 36
    cell_h = 40
    strip_y = 140   # верхній край стрічки
    start_x = 30    # лівий край першого байта

    # Визначення полів Device Descriptor (зміщення, довжина, назва, колір заливки)
    fields = [
        (0,  1, "bLength\n(18)",          "#fdecea", POS),      # 0
        (1,  1, "bDescr\nType",           "#fdecea", POS),      # 1
        (2,  2, "bcdUSB\n0x0200 (LE)",    "#eaf0fd", NEG),      # 2-3
        (4,  1, "bDevice\nClass",         FILL,      INK),      # 4
        (5,  1, "bDevice\nSubClass",      FILL,      INK),      # 5
        (6,  1, "bDevice\nProtocol",      FILL,      INK),      # 6
        (7,  1, "bMaxPkt\nSize0=64",      "#e8f8ee", FIELD),    # 7
        (8,  2, "idVendor\n0x3003 (LE)",  "#fff8e8", "#c8a060"),# 8-9
        (10, 2, "idProduct\n0x0001 (LE)", "#fff8e8", "#c8a060"),# 10-11
        (12, 2, "bcdDevice\n0x0100 (LE)", FILL,      INK),      # 12-13
        (14, 1, "iMfr=0",                 FILL,      MUTED),    # 14
        (15, 1, "iProd=0",                FILL,      MUTED),    # 15
        (16, 1, "iSer=0",                 FILL,      MUTED),    # 16
        (17, 1, "bNum\nConf=1",           "#e8f8ee", FIELD),    # 17
    ]

    # 1. Намалювати 18 клітинок стрічки
    for byte_i in range(18):
        cx = start_x + byte_i * cell_w + cell_w / 2
        # знайдемо поле для цього байта
        f_fill, f_stroke = FILL, LINE
        for (off, ln, lbl, fill, stroke) in fields:
            if off <= byte_i < off + ln:
                f_fill = fill
                f_stroke = stroke
                break
        frags.append(rect(start_x + byte_i * cell_w, strip_y, cell_w, cell_h,
                          fill=f_fill, stroke=f_stroke, sw=1.8, rx=0))
        # Номер байта над клітинкою
        frags.append(text(cx, strip_y - 6, str(byte_i), size=9, color=MUTED, anchor="middle"))

    # 2. Фігурні дужки + підписи полів знизу
    label_y_base = strip_y + cell_h + 14  # початок дужок
    label_y_text = label_y_base + 52      # рядок підписів

    for (off, ln, lbl, fill, stroke) in fields:
        x_left  = start_x + off * cell_w
        x_right = start_x + (off + ln) * cell_w
        cx = (x_left + x_right) / 2

        # Вертикальна лінія вниз із центру групи клітинок
        frags.append(line(cx, strip_y + cell_h, cx, label_y_base, color=stroke, sw=1.2))

        # Горизонтальна дужка (якщо поле > 1 байт)
        if ln > 1:
            frags.append(line(x_left + 2,  label_y_base, x_right - 2, label_y_base,
                              color=stroke, sw=1.2))
            frags.append(line(x_left + 2,  strip_y + cell_h, x_left + 2,  label_y_base,
                              color=stroke, sw=1.0))
            frags.append(line(x_right - 2, strip_y + cell_h, x_right - 2, label_y_base,
                              color=stroke, sw=1.0))

        # Підпис поля (textbox авто-ширина, щоб текст не вилазив)
        max_field_w = ln * cell_w - 4
        lines_lbl = lbl.split("\n")
        fs = 9 if ln == 1 else 10
        tb, bw, bh = textbox(cx, label_y_text, lbl, size=fs, pad=4,
                             fill=fill, stroke=stroke, sw=1.2, min_w=max_field_w)
        frags.append(tb)

    # 3. Виноска little-endian для idVendor (байти 8-9)
    le_cx = start_x + 8 * cell_w + cell_w   # центр поля idVendor
    le_y  = strip_y + 20
    frags.append(line(le_cx, le_y, le_cx, strip_y - 28, color="#c8a060", sw=1.2, dash="4,3"))
    tb_le, _, _ = textbox(le_cx + 55, strip_y - 42,
                          "LE: 0x03 0x30\n→ 0x3003",
                          size=10, fill="#fff8e8", stroke="#c8a060", sw=1.5)
    frags.append(tb_le)
    frags.append(arrow(le_cx + 14, strip_y - 42, le_cx + 2, strip_y - 28,
                       color="#c8a060", sw=1.4))

    # 4. Підпис шапки (bLength+bDescriptorType)
    header_cx = start_x + cell_w   # центр між 0 і 1
    tb_h, _, _ = textbox(header_cx, strip_y - 60,
                         "Службова шапка\nbLength + bDescriptorType",
                         size=10, fill="#fdecea", stroke=POS, sw=1.4)
    frags.append(tb_h)
    frags.append(line(start_x + cell_w / 2, strip_y - 42,
                      start_x + cell_w / 2, strip_y, color=POS, sw=1.2))
    frags.append(line(start_x + 3 * cell_w / 2, strip_y - 42,
                      start_x + 3 * cell_w / 2, strip_y, color=POS, sw=1.2))
    frags.append(line(start_x + cell_w / 2, strip_y - 42,
                      start_x + 3 * cell_w / 2, strip_y - 42, color=POS, sw=1.2))

    # 5. Виноска bMaxPacketSize0 (байт 7)
    mp_cx = start_x + 7 * cell_w + cell_w / 2
    frags.append(line(mp_cx, strip_y - 6, mp_cx, strip_y - 24, color=FIELD, sw=1.2, dash="3,3"))
    tb_mp, _, _ = textbox(mp_cx - 90, strip_y - 38,
                          "Перший байт, який\nчитає хост!",
                          size=9, fill="#e8f8ee", stroke=FIELD, sw=1.4)
    frags.append(tb_mp)

    render(os.path.join(OUT, "fig-12-3a-1-device-bytes.svg"), W, H, *frags,
           title="Рис. 4.12.3a.1. 18 байтів Device-дескриптора стрічкою")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.3a.2 — Дерево конфігурації в одному буфері 25 байтів
# ══════════════════════════════════════════════════════════════════════════════
def fig2_config_tree():
    W, H = 820, 460
    frags = []

    # ─── Ліва частина: Device Descriptor (стисло, лише вказівник на конф.) ───
    dev_x, dev_y, dev_w, dev_h = 30, 80, 170, 120
    frags.append(rect(dev_x, dev_y, dev_w, dev_h, fill="#fdecea", stroke=POS, sw=2.0, rx=6))
    frags.append(text(dev_x + dev_w / 2, dev_y + 18, "Device Descriptor", size=12,
                      color=POS, anchor="middle", bold=True))
    frags.append(line(dev_x + 6, dev_y + 26, dev_x + dev_w - 6, dev_y + 26,
                      color=POS, sw=1.0))
    for i, lbl in enumerate(["bLength = 18", "bDescriptorType = 0x01",
                              "… (інші поля)", "bNumConfigurations = 1"]):
        color = FIELD if i == 3 else MUTED
        bold = (i == 3)
        frags.append(text(dev_x + dev_w / 2, dev_y + 40 + i * 16, lbl,
                          size=10, color=color, anchor="middle", bold=bold))

    # Стрілка «окремий GET_DESCRIPTOR(Config)» від Device до буфера
    arr_y = dev_y + dev_h / 2 + 20
    frags.append(arrow(dev_x + dev_w, arr_y, 260, arr_y, color=INK, sw=1.8))
    tb_req, _, _ = textbox((dev_x + dev_w + 260) / 2, arr_y - 18,
                           "GET_DESCRIPTOR\n(Configuration)",
                           size=10, fill=FILL, stroke=INK, sw=1.2)
    frags.append(tb_req)

    # ─── Центральна частина: склеєний буфер 25 байтів ──────────────────────
    buf_x = 270
    buf_top = 40
    segment_w = 200

    # Три сегменти буфера
    segments = [
        (9,  "Config Descriptor\n9 байтів",  "#e8f0ff", NEG),
        (9,  "Interface Descriptor\n9 байтів", "#e8f8ee", FIELD),
        (7,  "Endpoint Descriptor\n7 байтів",  "#fff8e8", "#c8a060"),
    ]

    seg_y = buf_top
    seg_centers = []
    seg_boundaries = []

    for (seg_len, seg_lbl, seg_fill, seg_stroke) in segments:
        # Висота пропорційна числу байтів (масштаб ~10px/байт)
        seg_h = seg_len * 12 + 20
        frags.append(rect(buf_x, seg_y, segment_w, seg_h,
                          fill=seg_fill, stroke=seg_stroke, sw=2.0, rx=0))
        cy = seg_y + seg_h / 2
        seg_centers.append((buf_x + segment_w / 2, cy, seg_fill, seg_stroke))
        seg_boundaries.append((seg_y, seg_y + seg_h, seg_len))

        # Підпис усередині сегмента
        lines_s = seg_lbl.split("\n")
        for li, ln in enumerate(lines_s):
            text_y = cy - 7 + li * 15
            color = seg_stroke if seg_stroke != "#c8a060" else "#7a5000"
            frags.append(text(buf_x + segment_w / 2, text_y, ln,
                              size=11, color=color, anchor="middle",
                              bold=(li == 0)))
        seg_y += seg_h

    buf_bot = seg_y
    total_h = buf_bot - buf_top

    # ─── Дужка wTotalLength охоплює все дерево ────────────────────────────
    brk_x = buf_x + segment_w + 16
    frags.append(line(brk_x, buf_top, brk_x, buf_bot, color=NEG, sw=2.5))
    frags.append(line(brk_x, buf_top, brk_x - 8, buf_top, color=NEG, sw=2.5))
    frags.append(line(brk_x, buf_bot, brk_x - 8, buf_bot, color=NEG, sw=2.5))
    mid_brk = (buf_top + buf_bot) / 2
    tb_wt, _, _ = textbox(brk_x + 80, mid_brk,
                          "wTotalLength = 25\n(9 + 9 + 7)",
                          size=11, fill="#eaf0fd", stroke=NEG, sw=1.8)
    frags.append(tb_wt)
    frags.append(arrow(brk_x + 16, mid_brk, brk_x + 2, mid_brk, color=NEG, sw=1.6))

    # ─── Праворуч: підписи полів кожного сегмента ──────────────────────────
    details = [
        # Config 9 байтів
        ["bLength=9, type=0x02 CONFIGURATION",
         "wTotalLength=25 (LE: 0x19, 0x00)",
         "bNumInterfaces=1",
         "bConfigurationValue=1",
         "bmAttributes=0x80 (bus-powered)",
         "bMaxPower=50 (×2 мА = 100 мА)"],
        # Interface 9 байтів
        ["bLength=9, type=0x04 INTERFACE",
         "bInterfaceNumber=0",
         "bNumEndpoints=1",
         "bInterfaceClass=0xFF (vendor)",
         "bAlternateSetting=0",
         "subclass=0, protocol=0, iInterface=0"],
        # Endpoint 7 байтів
        ["bLength=7, type=0x05 ENDPOINT",
         "bEndpointAddress=0x81 (IN, ep1)",
         "bmAttributes=0x03 (interrupt)",
         "wMaxPacketSize=8 (LE: 0x08, 0x00)",
         "bInterval=10"],
    ]
    detail_colors = [NEG, FIELD, "#7a5000"]

    for i, ((_, seg_top, seg_bot, _), dlns, dc) in enumerate(
            zip([(s[0], seg_boundaries[j][0], seg_boundaries[j][1], seg_boundaries[j][2])
                 for j, s in enumerate(segments)],
                details, detail_colors)):
        y0 = seg_boundaries[i][0]
        y1 = seg_boundaries[i][1]
        cy = (y0 + y1) / 2
        detail_x = buf_x - 14
        # Горизонтальна лінія до деталей
        frags.append(line(buf_x - 2, cy, detail_x - 100, cy, color=dc, sw=1.0, dash="4,3"))
        for li, dln in enumerate(details[i]):
            ty = cy - (len(details[i]) - 1) * 6 + li * 12
            frags.append(text(detail_x - 110, ty, dln,
                              size=8, color=dc, anchor="end"))

    # ─── Підпис «Device Descriptor лише вказує...» ─────────────────────────
    note_y = buf_bot + 28
    tb_note, _, _ = textbox(buf_x + segment_w / 2 + 60, note_y,
                            "Device вказує bNumConfigurations=1;\nвміст приходить окремим запитом",
                            size=10, fill="#fdecea", stroke=POS, sw=1.2)
    frags.append(tb_note)
    frags.append(arrow(dev_x + dev_w / 2, dev_y + dev_h + 4,
                       dev_x + dev_w / 2, note_y - 16, color=POS, sw=1.4))

    render(os.path.join(OUT, "fig-12-3a-2-config-tree.svg"), W, H, *frags,
           title="Рис. 4.12.3a.2. Дерево конфігурації в одному буфері (25 байтів)")


if __name__ == "__main__":
    fig1_device_bytes()
    print("OK: fig-12-3a-1-device-bytes.svg")
    fig2_config_tree()
    print("OK: fig-12-3a-2-config-tree.svg")
