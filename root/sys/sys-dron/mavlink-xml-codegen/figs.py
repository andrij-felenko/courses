# -*- coding: utf-8 -*-
"""Фігури до теми «Генерація коду з XML-опису MAVLink».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

XMLC = "#2457d6"   # опис (XML) — холодне
GENC = "#7d3c98"   # генератор — фіолетове
OUTC = "#27ae60"   # згенерований код — зелене
WARN = "#c0392b"   # несумісність, розрив
CRCC = "#b9770e"   # контрольна сума


# ── 1. Ланцюг: дерево описів → генератор → кодеки різними мовами ────────────
def fig_pipeline():
    W, H = 920, 460
    f = [text(W / 2, 30, "Опис — джерело; код кожною мовою — похідний продукт", size=15, bold=True)]

    # ліва колонка: ланцюг включень
    lx = 150
    chain = ["minimal.xml", "standard.xml", "common.xml", "ardupilotmega.xml"]
    ys = [95, 160, 225, 290]
    for name, y in zip(chain, ys):
        b, bw, bh = textbox(lx, y, name, size=12, pad=12, stroke=XMLC, min_w=200)
        f.append(b)
    for i in range(len(ys) - 1):
        f.append(arrow(lx, ys[i + 1] - 18, lx, ys[i] + 18, color=XMLC, sw=1.6))
    f.append(text(lx, 60, "опис протоколу: XML", size=12, color=XMLC, bold=True))
    f.append(text(lx, 340, "діалект підключає ширший", size=10.5, color=MUTED, italic=True))
    f.append(text(lx, 360, "опис тегом <include>", size=10.5, color=MUTED, italic=True))

    # середина: генератор
    gx = 460
    gb, gw, gh = textbox(gx, 195, "mavgen\nрозбір XML\n+ шаблон мови",
                         size=12.5, pad=16, stroke=GENC, min_w=210)
    f.append(gb)
    f.append(arrow(lx + 108, 195, gx - gw / 2 - 12, 195, color=XMLC, sw=1.8))

    # права колонка: згенеровані кодеки
    rx = 770
    outs = ["C (прошивка)", "C++11", "Python (pymavlink)", "TypeScript"]
    oy = [100, 160, 220, 280]
    for name, y in zip(outs, oy):
        b, bw, bh = textbox(rx, y, name, size=11.5, pad=11, stroke=OUTC, min_w=250)
        f.append(b)
        f.append(arrow(gx + gw / 2 + 12, 195, rx - 130, y, color=GENC, sw=1.5))

    f.append(text(W / 2, 400,
                  "Розкладку полів, коди повідомлень і CRC_EXTRA обчислює генератор — однаково для всіх мов.",
                  size=11.5, color=MUTED, italic=True))
    f.append(text(W / 2, 424,
                  "Тому кодеки, зроблені з того самого опису, збігаються байт у байт.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "pipeline.svg"), W, H, *f)


# ── 2. Порядок у XML ≠ порядок на дроті ─────────────────────────────────────
def fig_field_order():
    W, H = 960, 480
    f = [text(W / 2, 30, "HEARTBEAT: генератор сам переставляє поля під розмір типу", size=15, bold=True)]

    xml_rows = [
        ("uint8_t · type", 1),
        ("uint8_t · autopilot", 1),
        ("uint8_t · base_mode", 1),
        ("uint32_t · custom_mode", 4),
        ("uint8_t · system_status", 1),
        ("uint8_t · mavlink_version", 1),
    ]
    wire_rows = [
        ("0–3", "uint32_t · custom_mode"),
        ("4", "uint8_t · type"),
        ("5", "uint8_t · autopilot"),
        ("6", "uint8_t · base_mode"),
        ("7", "uint8_t · system_status"),
        ("8", "uint8_t · mavlink_version"),
    ]

    colw = 330
    rh = 44
    gap = 10
    y0 = 100
    lx = 60
    rx = W - 60 - colw

    f.append(text(lx + colw / 2, 74, "порядок у XML", size=12.5, color=XMLC, bold=True))
    f.append(text(rx + colw / 2, 74, "порядок на дроті", size=12.5, color=OUTC, bold=True))

    for i, (label, sz) in enumerate(xml_rows):
        y = y0 + i * (rh + gap)
        col = CRCC if sz == 4 else XMLC
        f.append(fitbox(lx, y, colw, rh, label, size=12, stroke=col, sw=1.8))

    for i, (off, label) in enumerate(wire_rows):
        y = y0 + i * (rh + gap)
        col = CRCC if off == "0–3" else OUTC
        f.append(text(rx - 18, y + rh / 2 + 5, off, size=11, color=MUTED, anchor="end"))
        f.append(fitbox(rx, y, colw, rh, label, size=12, stroke=col, sw=1.8))

    # одна стрілка переставляння: 4-байтове поле йде вперед
    ymid = y0 + 2.5 * (rh + gap)
    f.append(arrow(lx + colw + 24, ymid, rx - 70, ymid, color=GENC, sw=2))
    f.append(text((lx + colw + rx) / 2 - 20, ymid - 14,
                  "сортування за розміром типу,", size=11, color=GENC))
    f.append(text((lx + colw + rx) / 2 - 20, ymid + 26,
                  "більші — попереду; рівні лишаються в порядку XML", size=11, color=GENC))

    f.append(text(W / 2, 424,
                  "Чотирибайтове поле опиняється на зміщенні 0 — воно вирівняне саме собою,",
                  size=11.5, color=MUTED, italic=True))
    f.append(text(W / 2, 448,
                  "і на дроті не треба жодного байта-заповнювача.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "field-order.svg"), W, H, *f)


# ── 3. Звідки береться CRC_EXTRA ────────────────────────────────────────────
def fig_crc_extra():
    W, H = 900, 470
    f = [text(W / 2, 30, "CRC_EXTRA: відбиток опису, зведений до одного байта", size=15, bold=True)]

    src = ("HEARTBEAT  uint32_t custom_mode  uint8_t type  uint8_t autopilot\n"
           "uint8_t base_mode  uint8_t system_status  uint8_t mavlink_version")
    b, bw, bh = textbox(W / 2, 105, src, size=11.5, pad=16, stroke=XMLC)
    f.append(b)
    f.append(text(W / 2, 62, "назва повідомлення, далі тип і назва кожного базового поля — у дротовому порядку",
                  size=11, color=MUTED, italic=True))

    steps = [
        ("CRC-16/MCRF4XX по цих символах", "початкове значення 0xFFFF"),
        ("отримали 0x2C1E", "два байти: 0x2C і 0x1E"),
        ("складаємо половинки: 0x1E ^ 0x2C", "CRC_EXTRA = 0x32 = 50"),
    ]
    y = 190
    for i, (title_, sub) in enumerate(steps):
        yy = y + i * 82
        col = CRCC if i == 2 else INK
        bb, bw2, bh2 = textbox(W / 2, yy, title_ + "\n" + sub, size=12, pad=13,
                               stroke=col, bold=(i == 2))
        f.append(bb)
        if i < len(steps) - 1:
            f.append(arrow(W / 2, yy + bh2 / 2 + 4, W / 2, yy + 82 - bh2 / 2 - 8, color=MUTED, sw=1.6))
    f.append(arrow(W / 2, 105 + bh / 2 + 4, W / 2, 190 - 30, color=MUTED, sw=1.6))

    f.append(text(W / 2, 430,
                  "Цей байт домішують у кінець контрольної суми кожного кадру HEARTBEAT —",
                  size=11.5, color=MUTED, italic=True))
    f.append(text(W / 2, 452,
                  "тож сторона з іншим описом просто не зійдеться в CRC.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "crc-extra-derivation.svg"), W, H, *f)


# ── 4. Розширення: що входить у відбиток, а що ні ───────────────────────────
def fig_extensions():
    W, H = 940, 450
    f = [text(W / 2, 30, "Тег <extensions/> ділить повідомлення на дві частини", size=15, bold=True)]

    # смуга корисних даних
    y = 96
    bh = 62
    x0 = 60
    basew = 500
    extw = 320
    f.append(rect(x0, y, basew, bh, fill=BG, stroke=XMLC, sw=2.2))
    f.append(text(x0 + basew / 2, y + 27, "базові поля", size=13, color=XMLC, bold=True))
    f.append(text(x0 + basew / 2, y + 47, "відсортовані за розміром · входять у CRC_EXTRA",
                  size=10.5, color=MUTED))
    f.append(rect(x0 + basew, y, extw, bh, fill=BG, stroke=OUTC, sw=2.2))
    f.append(text(x0 + basew + extw / 2, y + 27, "розширення", size=13, color=OUTC, bold=True))
    f.append(text(x0 + basew + extw / 2, y + 47, "порядок XML · поза CRC_EXTRA",
                  size=10.5, color=MUTED))
    f.append(line(x0 + basew, y - 14, x0 + basew, y + bh + 14, color=WARN, sw=2, dash="5 4"))
    f.append(text(x0 + basew, y - 24, "<extensions/>", size=11.5, color=WARN, bold=True))

    # два приймачі
    yy = 250
    lb, lw, lh = textbox(x0 + 190, yy,
                         "приймач зі старим описом\nчитає лише базову частину\nрешту байтів пропускає",
                         size=11.5, pad=14, stroke=INK)
    rb, rw, rh = textbox(x0 + 640, yy,
                         "приймач із новим описом\nчитає все; якщо кадр коротший —\nбракуючі байти вважає нулями",
                         size=11.5, pad=14, stroke=INK)
    f.append(lb)
    f.append(rb)
    f.append(arrow(x0 + 190, y + bh + 10, x0 + 190, yy - lh / 2 - 8, color=MUTED, sw=1.5))
    f.append(arrow(x0 + 640, y + bh + 10, x0 + 640, yy - rh / 2 - 8, color=MUTED, sw=1.5))

    f.append(text(W / 2, 370,
                  "Поле, дописане ПІСЛЯ тега, сумісності не ламає: відбиток опису не змінюється.",
                  size=12, color=OUTC, bold=True))
    f.append(text(W / 2, 400,
                  "Поле, вставлене ПЕРЕД тегом, змінює CRC_EXTRA — і старі кадри миттю відкидаються.",
                  size=12, color=WARN, bold=True))

    render(os.path.join(IMG, "extensions.svg"), W, H, *f)


# ── 5. Крок CRC-16/MCRF4XX: дзеркальний зсувний регістр (до proj-crc-extra) ──
def fig_crc_register():
    W, H = 990, 400
    f = [text(W / 2, 32,
              "Один крок CRC-16/MCRF4XX: зсув праворуч і умовне домішування 0x8408",
              size=15, bold=True)]
    f.append(text(W / 2, 60,
                  "Байт рядка спершу XOR-иться в молодші вісім бітів; далі — вісім таких кроків.",
                  size=11.5, color=MUTED, italic=True))

    x0, cw, ch, cy = 100, 44, 42, 132
    xend = x0 + 16 * cw            # правий край регістра
    taps = (15, 10, 3)

    f.append(text(520, 96, "напрям зсуву", size=11.5, color=MUTED))
    f.append(arrow(390, 112, 690, 112, color=MUTED, sw=1.5))

    for i in range(16):
        bit = 15 - i
        x = x0 + i * cw
        hot = bit in taps
        f.append(rect(x, cy, cw, ch, fill="#fdf3e3" if hot else FILL,
                      stroke=CRCC if hot else LINE, sw=2.2 if hot else 1.2, rx=3))
        f.append(text(x + cw / 2, cy + ch / 2 + 5, str(bit), size=12.5,
                      color=CRCC if hot else INK, bold=hot))

    # молодший біт вилітає праворуч і повертається на розгалуження
    f.append(text(880, 116, "вилітлий біт", size=11.5, color=CRCC, bold=True))
    f.append(arrow(xend + 6, cy + ch / 2, 900, cy + ch / 2, color=CRCC, sw=2))
    f.append(line(900, cy + ch / 2, 900, 258, color=CRCC, sw=2))
    tap_x = [x0 + (15 - b) * cw + cw / 2 for b in taps]
    f.append(line(900, 258, min(tap_x), 258, color=CRCC, sw=2))
    for tx in tap_x:
        f.append(arrow(tx, 252, tx, cy + ch + 6, color=CRCC, sw=1.8))

    f.append(text(500, 292,
                  "якщо вилітлий біт = 1 — перевернути біти 15, 10 і 3; якщо 0 — лишити як є",
                  size=12, color=CRCC, bold=True))

    f.append(text(W / 2, 336,
                  "0x8408 = 1000 0100 0000 1000₂ — одиниці стоять якраз на бітах 15, 10 і 3.",
                  size=11.5, color=MUTED))
    f.append(text(W / 2, 362,
                  "Це многочлен 0x1021 (x¹⁶ + x¹² + x⁵ + 1), записаний дзеркально: зсув іде до молодшого біта.",
                  size=11.5, color=MUTED))

    render(os.path.join(IMG, "crc-register.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pipeline()
    fig_field_order()
    fig_crc_extra()
    fig_extensions()
    fig_crc_register()
    print("OK: 5 figs ->", IMG)


# ── Що саме з'являється з ОДНОГО <message> (до довідника api-mavgen) ────────
def fig_artifacts():
    W, H = 1010, 570
    f = []

    # джерело — один елемент опису
    sx, sy = 160, 295
    sb, sw, sh = textbox(sx, sy,
                         "<message id=\"30\"\n         name=\"ATTITUDE\">\n   7 полів\n</message>",
                         size=12, pad=14, stroke=XMLC, min_w=235)
    f.append(text(sx, 105, "один елемент опису", size=12.5, color=XMLC, bold=True))
    f.append(sb)
    f.append(arrow(sx, 125, sx, sy - sh / 2 - 10, color=XMLC, sw=1.5))

    # генератор
    gx = 415
    gb, gw, gh = textbox(gx, sy, "mavgen\n--lang=C\n--lang=Python",
                         size=12, pad=14, stroke=GENC, min_w=175)
    f.append(gb)
    f.append(arrow(sx + sw / 2 + 10, sy, gx - gw / 2 - 10, sy, color=MUTED, sw=1.6))

    # три групи наслідків
    rx = 750
    groups = [
        (125, "mavlink_msg_attitude.h",
         "struct mavlink_attitude_t — у дротовому порядку\n"
         "MAVLINK_MSG_ID_ATTITUDE / _LEN / _MIN_LEN / _CRC\n"
         "_pack · _pack_chan · _pack_status · _encode\n"
         "_send · _get_<поле> · _decode", OUTC),
        (310, "common.h — заголовок діалекту",
         "#include \"./mavlink_msg_attitude.h\"\n"
         "рядок у MAVLINK_MESSAGE_CRCS: {30, 39, 28, 28, …}\n"
         "MAVLINK_MESSAGE_INFO_ATTITUDE — імена й зміщення", CRCC),
        (480, "common.py — кодек pymavlink",
         "MAVLINK_MSG_ID_ATTITUDE = 30\n"
         "class MAVLink_attitude_message: format, crc_extra\n"
         "запис у mavlink_map · метод attitude_send()", OUTC),
    ]
    for cy, head, bodytext, col in groups:
        b, bw, bh = textbox(rx, cy, bodytext, size=11, pad=13, stroke=col, min_w=440)
        f.append(text(rx, cy - bh / 2 - 13, head, size=12, color=col, bold=True))
        f.append(b)
        f.append(arrow(gx + gw / 2 + 10, sy, rx - bw / 2 - 12, cy, color=MUTED, sw=1.4))

    f.append(text(W / 2, 555,
                  "Жоден із цих символів не пишуть руками: усі до одного виведені з опису.",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "artifacts.svg"), W, H, *f,
           title="Один <message> — і все, що з нього народжується")


if __name__ == "__main__":
    fig_artifacts()
    print("OK: artifacts.svg ->", IMG)
