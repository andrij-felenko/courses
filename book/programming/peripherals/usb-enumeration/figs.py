# -*- coding: utf-8 -*-
"""Фігури до теми «Енумерація USB».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Послідовність енумерації: хост ↔ пристрій, крок за кроком ─────────────
def fig_enum_sequence():
    W, H = 820, 560
    f = [text(W / 2, 30, "Енумерація: кожен крок ініціює хост, усе через EP0", size=16, bold=True)]

    # дві вертикалі-доріжки
    hx, dx = 200, 620
    top, bot = 70, 525
    f.append(line(hx, top, hx, bot, color=MUTED, sw=2, dash="4,4"))
    f.append(line(dx, top, dx, bot, color=MUTED, sw=2, dash="4,4"))
    f.append(textbox(hx, top - 4, "ХОСТ", size=14, bold=True, fill="#eef2f7")[0])
    f.append(textbox(dx, top - 4, "ПРИСТРІЙ", size=14, bold=True, fill="#eef2f7")[0])

    # кроки: (y, текст, напрям) напрям: '>' хост→пристрій, '<' назад, '~' подія
    steps = [
        (108, "підключення: підтяжка D+ (Full-Speed)", "<"),
        (150, "USB reset", ">"),
        (192, "GET_DESCRIPTOR(Device, 8) → адреса 0", ">"),
        (234, "перші 8 байтів: дізнаюсь bMaxPacketSize0", "<"),
        (276, "USB reset", ">"),
        (318, "SET_ADDRESS(N)", ">"),
        (360, "тепер відповідаю на адресі N", "<"),
        (402, "GET_DESCRIPTOR(Device, 18) → адреса N", ">"),
        (444, "Configuration + Interface + Endpoint", "<"),
        (486, "SET_CONFIGURATION(1) → стан configured", ">"),
    ]
    for y, label, d in steps:
        if d == ">":
            f.append(arrow(hx + 8, y, dx - 8, y, color=POS, sw=2))
            f.append(text((hx + dx) / 2, y - 8, label, size=12, color=INK))
        else:
            f.append(arrow(dx - 8, y, hx + 8, y, color=NEG, sw=2))
            f.append(text((hx + dx) / 2, y - 8, label, size=12, color=INK))

    # підсумкова рамка
    f.append(fitbox(250, 505, 320, 34, "Готовий нести корисний трафік",
                    size=13, bold=True, fill="#e8f6ee", stroke=FIELD))
    return render(os.path.join(IMG, "enum-sequence.svg"), W, H, *f)


# ── 2. Дерево дескрипторів: Device → Configuration → Interface → Endpoint ────
def fig_descriptor_tree():
    W, H = 780, 470
    f = [text(W / 2, 30, "Дерево дескрипторів: хост читає зверху вниз", size=16, bold=True)]

    # вертикальний ланцюг
    cx = 300
    nodes = [
        (70,  "Device", "версія USB · клас · bMaxPacketSize0 · VID:PID · к-сть конфігурацій", "#fdecea", POS),
        (150, "Configuration", "к-сть інтерфейсів · живлення · макс. струм", FILL, LINE),
        (230, "Interface", "роль функції · клас · к-сть кінцевих точок", FILL, LINE),
        (310, "Endpoint", "номер · напрям · тип передачі · розмір пакета · інтервал", "#e8f6ee", FIELD),
    ]
    box_w = 420
    for i, (y, title_, sub, fill, stroke) in enumerate(nodes):
        f.append(rect(cx - box_w / 2, y, box_w, 56, fill=fill, stroke=stroke, sw=2))
        f.append(text(cx, y + 24, title_, size=15, bold=True))
        f.append(fitbox(cx - box_w / 2 + 6, y + 30, box_w - 12, 20, sub,
                        size=11, fill="none", stroke="none", color=MUTED))
        if i < len(nodes) - 1:
            ny = nodes[i + 1][0]
            f.append(arrow(cx, y + 56, cx, ny, color=LINE, sw=2))

    # збоку — String-дескриптори
    sx = 660
    f.append(rect(sx - 90, 150, 180, 56, fill="#eef2f7", stroke=MUTED, sw=1.5))
    f.append(text(sx, 174, "String (необов'язкові)", size=12, bold=True))
    f.append(text(sx, 194, "виробник · назва · серійник", size=10, color=MUTED))
    f.append(line(cx + box_w / 2, 178, sx - 90, 178, color=MUTED, sw=1.5, dash="4,4"))

    f.append(text(W / 2, 400, "VID:PID живуть у Device; код класу — у Device або Interface",
                  size=12, color=INK))
    f.append(text(W / 2, 422, "wTotalLength у Configuration охоплює все дерево в одному буфері",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, "descriptor-tree.svg"), W, H, *f)


# ── 3. 18 байтів Device-дескриптора: де VID і PID ───────────────────────────
def fig_device_descriptor_bytes():
    W, H = 860, 360
    f = [text(W / 2, 30, "Device-дескриптор: 18 байтів, VID:PID у little-endian", size=16, bold=True)]

    # 18 клітинок
    n = 18
    cw = 42
    x0 = (W - n * cw) / 2
    y = 110
    ch = 52
    # підсвічування VID (08-09) і PID (0A-0B)
    bytes_ = [
        ("12", "len", FILL), ("01", "type", FILL),
        ("00", "", FILL), ("02", "USB2.0", FILL),
        ("00", "cls", FILL), ("00", "", FILL), ("00", "", FILL),
        ("40", "EP0=64", FILL),
        ("83", "VID", "#fdecea"), ("04", "VID", "#fdecea"),
        ("11", "PID", "#eaf0fd"), ("57", "PID", "#eaf0fd"),
        ("00", "", FILL), ("02", "ver", FILL),
        ("01", "iM", FILL), ("02", "iP", FILL), ("03", "iS", FILL),
        ("01", "nCfg", FILL),
    ]
    for i, (hx, tag, fill) in enumerate(bytes_):
        x = x0 + i * cw
        f.append(rect(x, y, cw - 3, ch, fill=fill, stroke=LINE, sw=1.4, rx=4))
        f.append(text(x + (cw - 3) / 2, y - 8, "%02X" % i, size=10, color=MUTED))   # зсув
        f.append(text(x + (cw - 3) / 2, y + 24, hx, size=15, bold=True))            # hex
        if tag:
            f.append(text(x + (cw - 3) / 2, y + 44, tag, size=9, color=MUTED))

    # дужки під VID і PID
    vid_x = x0 + 8 * cw
    pid_x = x0 + 10 * cw
    f.append(line(vid_x, y + ch + 10, vid_x + 2 * cw - 3, y + ch + 10, color=POS, sw=2))
    f.append(text(vid_x + cw - 1.5, y + ch + 30, "idVendor = 0x0483", size=12, color=POS, bold=True))
    f.append(line(pid_x, y + ch + 10, pid_x + 2 * cw - 3, y + ch + 10, color=NEG, sw=2))
    f.append(text(pid_x + cw - 1.5, y + ch + 30, "idProduct = 0x5711", size=12, color=NEG, bold=True))

    f.append(text(W / 2, y + ch + 70,
                  "Байти йдуть молодшим уперед: 83 04 → 0x0483. За цією парою ОС обирає драйвер.",
                  size=12, color=INK))
    return render(os.path.join(IMG, "device-descriptor-bytes.svg"), W, H, *f)


# ── 4. Вставка proj: 18 байтів Device-дескриптора, рукотворні (VID 0x3003) ──
def fig_device_bytes():
    W, H = 880, 320
    f = [text(W / 2, 30, "Device-дескриптор рукотворно: 18 байтів і little-endian", size=16, bold=True)]
    bytes_ = [
        ("18", "len"), ("01", "type"), ("00", ""), ("02", "USB2.0"),
        ("00", "cls"), ("00", ""), ("00", ""), ("40", "EP0=64"),
        ("03", "VID"), ("30", "VID"), ("01", "PID"), ("00", "PID"),
        ("00", "ver"), ("01", "ver"), ("00", "iM"), ("00", "iP"),
        ("00", "iS"), ("01", "nCfg"),
    ]
    n = len(bytes_)
    cw = 44
    x0 = (W - n * cw) / 2
    y, ch = 110, 52
    for i, (hx, tag) in enumerate(bytes_):
        x = x0 + i * cw
        fill = "#fdecea" if 8 <= i <= 9 else ("#eaf0fd" if 10 <= i <= 11 else FILL)
        f.append(rect(x, y, cw - 3, ch, fill=fill, stroke=LINE, sw=1.4, rx=4))
        f.append(text(x + (cw - 3) / 2, y - 8, "%02X" % i, size=10, color=MUTED))
        f.append(text(x + (cw - 3) / 2, y + 24, hx, size=15, bold=True))
        if tag:
            f.append(text(x + (cw - 3) / 2, y + 44, tag, size=9, color=MUTED))
    vid_x = x0 + 8 * cw
    f.append(line(vid_x, y + ch + 10, vid_x + 2 * cw - 3, y + ch + 10, color=POS, sw=2))
    f.append(text(vid_x + cw - 1.5, y + ch + 30, "idVendor 0x3003 → 03 30", size=12, color=POS, bold=True))
    f.append(text(W / 2, y + ch + 62,
                  "Молодший байт першим: 03 30 у пам'яті означає 0x3003.",
                  size=12, color=INK))
    return render(os.path.join(IMG, "device-bytes.svg"), W, H, *f)


# ── 5. Вставка proj: Configuration-дерево 25 байтів і роль wTotalLength ──────
def fig_config_tree():
    W, H = 820, 470
    f = [text(W / 2, 30, "Configuration tree: три дескриптори в одному буфері (25 байтів)", size=16, bold=True)]
    cx = 250
    blocks = [
        (70,  "Config (9)", "wTotalLength = 25 · bNumInterfaces = 1 · bMaxPower", "#fdecea", POS),
        (170, "Interface (9)", "bInterfaceNumber 0 · bNumEndpoints 1 · клас", FILL, LINE),
        (270, "Endpoint (7)", "0x81 IN · interrupt · wMaxPacketSize 8 · bInterval", "#e8f6ee", FIELD),
    ]
    bw = 360
    for i, (y, title_, sub, fill, stroke) in enumerate(blocks):
        f.append(rect(cx - bw / 2, y, bw, 64, fill=fill, stroke=stroke, sw=2))
        f.append(text(cx, y + 26, title_, size=15, bold=True))
        f.append(fitbox(cx - bw / 2 + 6, y + 34, bw - 12, 22, sub,
                        size=11, fill="none", stroke="none", color=MUTED))
        if i < len(blocks) - 1:
            f.append(arrow(cx, y + 64, cx, blocks[i + 1][0], color=LINE, sw=2))

    # охоплювальна дужка wTotalLength
    bx = cx + bw / 2 + 30
    f.append(line(bx, 70, bx, 334, color=POS, sw=2.5))
    f.append(line(bx - 8, 70, bx, 70, color=POS, sw=2.5))
    f.append(line(bx - 8, 334, bx, 334, color=POS, sw=2.5))
    f.append(textbox(bx + 95, 202, "wTotalLength\nохоплює все\nдерево = 25",
                     size=12, bold=True, color=POS, fill="#fdecea", stroke=POS)[0])

    f.append(text(W / 2, 400, "Хост спершу читає 9 байтів Config, дізнається wTotalLength,",
                  size=12, color=INK))
    f.append(text(W / 2, 422, "потім забирає всі 25 одним запитом. Брехливий wTotalLength → дерево уривається.",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, "config-tree.svg"), W, H, *f)


# ── 6. (детальна) Три стадії контрольної передачі: setup → data → status ────
def fig_control_stages():
    W, H = 820, 420
    f = [text(W / 2, 30, "Контрольна передача: три стадії, кожна з квитуванням", size=16, bold=True)]

    stages = [
        (60,  "SETUP", "8-байтовий запит:\nщо хост хоче", "#fdecea", POS),
        (320, "DATA", "корисні байти\n(може бути 0 пакетів)", FILL, LINE),
        (580, "STATUS", "квитанція протилежним\nнапрямом: усе ок", "#e8f6ee", FIELD),
    ]
    bw, bh, by = 180, 120, 110
    for i, (x, title_, sub, fill, stroke) in enumerate(stages):
        f.append(rect(x, by, bw, bh, fill=fill, stroke=stroke, sw=2))
        f.append(text(x + bw / 2, by + 30, title_, size=16, bold=True))
        f.append(fitbox(x + 8, by + 44, bw - 16, 60, sub, size=12,
                        fill="none", stroke="none", color=INK))
        if i < len(stages) - 1:
            nx = stages[i + 1][0]
            f.append(arrow(x + bw, by + bh / 2, nx, by + bh / 2, color=LINE, sw=2))

    f.append(text(150, 285, "хост → пристрій", size=11, color=MUTED))
    f.append(text(410, 285, "напрям за bmRequestType", size=11, color=MUTED))
    f.append(text(670, 285, "пристрій → хост", size=11, color=MUTED))

    f.append(fitbox(110, 320, 600, 56,
                    "Для GET_DESCRIPTOR data-стадія несе байти дескриптора (IN); "
                    "для SET_ADDRESS data-стадії немає, одразу status.",
                    size=12, fill="#f4f6f8", stroke=MUTED))
    return render(os.path.join(IMG, "control-stages.svg"), W, H, *f)


# ── 7. (детальна) 8 байтів setup-пакета: bmRequestType…wLength ───────────────
def fig_setup_packet():
    W, H = 840, 360
    f = [text(W / 2, 30, "Setup-пакет: 8 байтів, що описують будь-який запит", size=16, bold=True)]

    fields = [
        ("bmReq\nType", "1", "напрям·тип", "#fdecea"),
        ("bReq", "1", "код запиту", "#eaf0fd"),
        ("wValue", "2", "тип+індекс дескриптора", FILL),
        ("wIndex", "2", "індекс / мова", FILL),
        ("wLength", "2", "скільки байтів даних", "#e8f6ee"),
    ]
    # ширина пропорційна к-сті байтів
    total_bytes = 8
    band_w = 720
    x = (W - band_w) / 2
    y, h = 115, 76
    for name, nb, desc, fill in fields:
        w = band_w * int(nb) / total_bytes
        f.append(rect(x, y, w, h, fill=fill, stroke=LINE, sw=1.6))
        f.append(fitbox(x + 3, y + 6, w - 6, 34, name, size=12, bold=True,
                        fill="none", stroke="none"))
        f.append(text(x + w / 2, y + 60, nb + " б", size=11, color=MUTED))
        f.append(fitbox(x + 2, y + h + 6, w - 4, 28, desc, size=10,
                        fill="none", stroke="none", color=MUTED))
        x += w

    f.append(fitbox(120, 250, 600, 80,
                    "Приклад GET_DESCRIPTOR(Device, 8):\n"
                    "bmRequestType=0x80 (IN, стандартний, до пристрою) · bRequest=0x06 (GET_DESCRIPTOR)\n"
                    "wValue=0x0100 (тип 0x01 DEVICE, індекс 0) · wIndex=0 · wLength=8",
                    size=12, fill="#f4f6f8", stroke=MUTED))
    return render(os.path.join(IMG, "setup-packet.svg"), W, H, *f)


if __name__ == "__main__":
    fig_enum_sequence()
    fig_descriptor_tree()
    fig_device_descriptor_bytes()
    fig_device_bytes()
    fig_config_tree()
    fig_control_stages()
    fig_setup_packet()
    print("figs.py: записано 7 SVG у", IMG)
