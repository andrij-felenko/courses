# -*- coding: utf-8 -*-
"""Фігури до теми «Пристрій на шині USB: хост, енумерація, кінцеві точки, класи».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def spark(cx, cy, r=18, color=POS, n=10):
    """Зірка-спалах (колізія): промені з центру + маленьке ядро."""
    out = []
    for i in range(n):
        a = math.pi * 2 * i / n
        rr = r if i % 2 == 0 else r * 0.5
        out.append(line(cx, cy, cx + rr * math.cos(a), cy + rr * math.sin(a),
                        color=color, sw=2.2))
    out.append(circle(cx, cy, 5, fill=color, stroke=color, sw=1))
    return "".join(out)


# ── 1. Дві моделі шини: єдиний господар (USB) проти рівних (I²C/CAN) ──────────
def fig_bus_contrast():
    W, H = 880, 470
    f = [text(W / 2, 30, "Дві моделі шини: єдиний господар проти рівних учасників",
              size=15.5, bold=True)]

    # ── ліва панель: USB ──
    f.append(rect(30, 52, 400, 384, fill=BG, stroke=NEG, sw=2, rx=12))
    f.append(text(230, 82, "USB: господар опитує — пристрій відповідає",
                  size=12.5, bold=True, color=NEG))
    # хост
    f.append(rect(155, 100, 150, 46, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    f.append(text(230, 130, "ХОСТ", size=15, bold=True, color=NEG))
    # легенда стрілок (у чистому куті)
    f.append(text(46, 176, "↓ хост опитує (токен)", size=10, color=INK, anchor="start"))
    f.append(text(46, 194, "↑ пристрій відповідає (дані)", size=10, color=MUTED, anchor="start"))
    # пристрої
    devs = [(105, "клавіатура"), (230, "флешка"), (355, "камера")]
    for cx, name in devs:
        f.append(rect(cx - 48, 340, 96, 46, fill=FILL, stroke=LINE, sw=1.5, rx=8))
        f.append(text(cx, 368, name, size=10.5, color=INK))
        # опитування (вниз) і відповідь (вгору) — рознесено по x, щоб не злипались
        f.append(arrow(215, 148, cx - 12, 338, color=INK, sw=1.8))
        f.append(arrow(cx + 12, 338, 245, 148, color=MUTED, sw=1.4))
    b, _, _ = textbox(230, 414, "говорить лише опитаний → колізій немає",
                      size=10.8, fill="#eafaf1", stroke=FIELD)
    f.append(b)

    # ── права панель: I²C / CAN ──
    f.append(rect(450, 52, 400, 384, fill=BG, stroke=POS, sw=2, rx=12))
    f.append(text(650, 82, "I²C / CAN: кожен може почати сам",
                  size=12.5, bold=True, color=POS))
    f.append(text(650, 108, "обидва почали разом", size=10.8, bold=True, color=POS))
    # два рівні вузли
    for cx, name in [(560, "вузол A"), (740, "вузол B")]:
        f.append(rect(cx - 55, 124, 110, 46, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
        f.append(text(cx, 153, name, size=12, bold=True, color=INK))
    # спільна шина
    f.append(line(480, 250, 820, 250, color=INK, sw=3))
    f.append(text(492, 244, "спільна шина", size=10, color=MUTED, anchor="start"))
    # обидва «тягнуть» шину, сигнали сходяться в центрі
    f.append(arrow(560, 170, 622, 246, color=POS, sw=2.2))
    f.append(arrow(740, 170, 678, 246, color=POS, sw=2.2))
    f.append(spark(650, 250, r=20, color=POS))
    f.append(text(650, 288, "колізія!", size=12.5, bold=True, color=POS))
    f.append(text(650, 306, "→ потрібен арбітраж у кожному вузлі", size=10.5, color=MUTED))
    b, _, _ = textbox(650, 414, "рівні учасники → колізії → арбітраж, якого USB не має",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "bus-contrast.svg"), W, H, *f)


# ── 2. Транзакція = три пакети поспіль: токен → дані → підтвердження ──────────
def fig_transaction():
    W, H = 900, 445
    f = [text(W / 2, 30, "Транзакція USB — три пакети поспіль", size=15.5, bold=True)]

    sx = [45, 330, 615]        # ліві краї трьох боксів
    sw_ = 240
    cxs = [x + sw_ / 2 for x in sx]
    topY, boxH = 96, 206

    senders = ["шле ХОСТ", "шле хост АБО пристрій", "шле приймач"]
    titles = ["1 · ТОКЕН", "2 · ДАНІ", "3 · ПІДТВЕРДЖЕННЯ"]
    tcols = [NEG, FIELD, POS]

    for i in range(3):
        # плашка «хто шле» над боксом
        b, _, _ = textbox(cxs[i], 66, senders[i], size=10.3, pad=7,
                          fill="#f0f2f5", stroke=MUTED, color=INK)
        f.append(b)
        # сам бокс
        f.append(rect(sx[i], topY, sw_, boxH, fill=BG, stroke=tcols[i], sw=1.8, rx=10))
        f.append(text(cxs[i], topY + 28, titles[i], size=13.5, bold=True, color=tcols[i]))

    # стрілки між кроками
    midY = topY + boxH / 2
    f.append(arrow(sx[0] + sw_, midY, sx[1], midY, color=INK, sw=2.2))
    f.append(arrow(sx[1] + sw_, midY, sx[2], midY, color=INK, sw=2.2))

    # ── вміст боксу 1: три поля токена ──
    for j, lab in enumerate(["адреса N", "кінцева точка M", "напрям (IN / OUT)"]):
        b, _, _ = textbox(cxs[0], 150 + j * 42, lab, size=11, pad=8,
                          fill=FILL, stroke=LINE)
        f.append(b)
    f.append(text(cxs[0], 288, "кого й куди опитують", size=9.8, italic=True, color=MUTED))

    # ── вміст боксу 2: потік у названий бік ──
    f.append(text(cxs[1], 150, "вміст названої точки", size=11, color=INK))
    f.append(arrow(sx[1] + 40, 185, sx[1] + sw_ - 40, 185, color=FIELD, sw=3.2))
    f.append(text(cxs[1], 178, "тече у названий бік", size=9.8, italic=True, color=FIELD))
    f.append(text(cxs[1], 228, "напрям OUT → шле хост", size=10, color=MUTED))
    f.append(text(cxs[1], 248, "напрям IN → шле пристрій", size=10, color=MUTED))
    f.append(text(cxs[1], 288, "самі дані обміну", size=9.8, italic=True, color=MUTED))

    # ── вміст боксу 3: три можливі відповіді ──
    chips = [("ACK — прийнято", FIELD, "#eafaf1"),
             ("NAK — ще не готовий", NEG, "#eaf0fd"),
             ("STALL — помилка точки", POS, "#fdecea")]
    for j, (lab, col, fill) in enumerate(chips):
        yy = 148 + j * 48
        f.append(rect(sx[2] + 16, yy, sw_ - 32, 40, fill=fill, stroke=col, sw=1.6, rx=7))
        f.append(text(cxs[2], yy + 25, lab, size=11, bold=True, color=col))

    b, _, _ = textbox(W / 2, 418,
                      "Пристрій віддає дані лише у відповідь на адресований йому токен; підтвердження закриває транзакцію.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "transaction.svg"), W, H, *f)


# ── 3. Енумерація: шість кроків від «воткнули» до «працює» ────────────────────
def fig_enumeration():
    W, H = 800, 652
    f = [text(W / 2, 32, "Енумерація: від «воткнули» до «працює»", size=15.5, bold=True)]

    steps = [
        ("Поява", "підтяжка на D+ або D− → «я тут» і швидкість", "n"),
        ("Скидання порту", "обидві лінії низькі понад 10 мс → відомий стан", "n"),
        ("Перше знайомство", "хост читає розмір нульової точки — на адресі 0", "n"),
        ("SET_ADDRESS(n)", "пристрій дістає власну постійну адресу N", "pivot"),
        ("Повний розпит", "віддає все дерево дескрипторів на своїй адресі", "n"),
        ("SET_CONFIGURATION", "оживають усі кінцеві точки — пристрій ГОТОВИЙ", "ready"),
    ]

    x0, x1 = 120, 680
    topY, boxH, gap = 62, 76, 20
    for i, (title, detail, kind) in enumerate(steps):
        y = topY + i * (boxH + gap)
        if kind == "ready":
            bf, bs, bc = "#eafaf1", FIELD, FIELD
        elif kind == "pivot":
            bf, bs, bc = "#eaf0fd", NEG, NEG
        else:
            bf, bs, bc = FILL, LINE, INK
        f.append(rect(x0, y, x1 - x0, boxH, fill=bf, stroke=bs, sw=1.8, rx=10))
        # значок-номер
        f.append(circle(152, y + boxH / 2, 18, fill=bc, stroke=bc, sw=1))
        f.append(text(152, y + boxH / 2 + 6, str(i + 1), size=16, bold=True, color=BG))
        # текст кроку
        f.append(text(188, y + 33, title, size=14.5, bold=True, color=INK, anchor="start"))
        f.append(text(188, y + 57, detail, size=11.5, color=MUTED, anchor="start"))
        # стрілка вниз до наступного
        if i < len(steps) - 1:
            f.append(arrow(W / 2, y + boxH + 2, W / 2, y + boxH + gap - 2, color=INK, sw=2))

    render(os.path.join(IMG, "enumeration.svg"), W, H, *f)


# ── 4. Setup-пакет: 8 байтів + розгортання байта bmRequestType по бітах ───────
def fig_setup_packet():
    W, H = 900, 470
    f = [text(W / 2, 30, "Setup-пакет: 8 байтів кожного керівного запиту",
              size=15.5, bold=True)]

    # ── Зона A: вісім байтів пакета ──
    x0, cellW, cellH, yb = 66, 96, 52, 108
    groups = [(0, 1, "bmRequestType"), (1, 1, "bRequest"), (2, 2, "wValue"),
              (4, 2, "wIndex"), (6, 2, "wLength")]
    for start, span, name in groups:
        gx, gw = x0 + start * cellW, span * cellW
        hot = (name == "bmRequestType")
        f.append(fitbox(gx + 3, 70, gw - 6, 26, name, size=11, bold=True,
                        fill=("#eaf0fd" if hot else FILL),
                        stroke=(NEG if hot else LINE),
                        color=(NEG if hot else INK)))
    for i in range(8):
        left = x0 + i * cellW
        hot = (i == 0)
        f.append(rect(left + 2, yb, cellW - 4, cellH, fill=("#eaf0fd" if hot else BG),
                      stroke=(NEG if hot else LINE), sw=(2 if hot else 1.4)))
        f.append(text(left + cellW / 2, yb + 33, str(i), size=19, bold=True,
                      color=(NEG if hot else INK)))
    f.append(text(x0 - 8, yb + 33, "зсув:", size=10, color=MUTED, anchor="end"))
    b, _, _ = textbox(x0 + 5 * cellW, yb + cellH + 26,
                      "16-бітові wValue / wIndex / wLength — молодшим байтом уперед (little-endian)",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)

    # ── стрілка «байт 0 по бітах» ──
    f.append(text(66, 210, "байт 0 — по бітах:", size=11, italic=True,
                  color=NEG, anchor="start"))
    f.append(arrow(114, yb + cellH, 178, 234, color=NEG, sw=1.8))

    # ── Зона B: вісім бітів bmRequestType ──
    bx0, bcw, byb, bch = 178, 67, 230, 46
    for i in range(8):
        bit = 7 - i
        if i == 0:
            tint, col = "#eaf0fd", NEG
        elif i in (1, 2):
            tint, col = "#eafaf1", FIELD
        else:
            tint, col = "#fdecea", POS
        left = bx0 + i * bcw
        f.append(rect(left + 2, byb, bcw - 4, bch, fill=tint, stroke=col, sw=1.6))
        f.append(text(left + bcw / 2, byb + 29, "D%d" % bit, size=14, bold=True, color=col))

    # ── брекети груп + легенди ──
    ybr = byb + bch + 8
    def bracket(cf, ct, col):
        f.append(line(cf, ybr, ct, ybr, color=col, sw=2))
        f.append(line(cf, ybr - 6, cf, ybr, color=col, sw=2))
        f.append(line(ct, ybr - 6, ct, ybr, color=col, sw=2))
    d7_l, d7_r = bx0 + 2, bx0 + bcw - 2
    ty_l, ty_r = bx0 + bcw + 2, bx0 + 3 * bcw - 2
    rc_l, rc_r = bx0 + 3 * bcw + 2, bx0 + 8 * bcw - 2
    bracket(d7_l, d7_r, NEG)
    bracket(ty_l, ty_r, FIELD)
    bracket(rc_l, rc_r, POS)

    legends = [
        ((d7_l + d7_r) / 2, 165, NEG, "Напрям (D7)",
         ["0 = OUT: хост → пристрій", "1 = IN: пристрій → хост"]),
        ((ty_l + ty_r) / 2, 428, FIELD, "Тип (D6–D5)",
         ["0 стандартний · 1 класовий", "2 вендорний · 3 резерв"]),
        ((rc_l + rc_r) / 2, 715, POS, "Отримувач (D4–D0)",
         ["0 пристрій · 1 інтерфейс", "2 точка · 3 інше"]),
    ]
    for br_cx, box_cx, col, title, lines in legends:
        body, w, h = textbox(box_cx, 404, [title] + lines, size=10.5,
                             fill=BG, stroke=col, color=INK)
        f.append(line(br_cx, ybr, box_cx, 404 - h / 2, color=col, sw=1.1, dash="3,3"))
        f.append(body)

    render(os.path.join(IMG, "setup-packet.svg"), W, H, *f)


# ── 5. Плаский буфер дескрипторів → дерево: крок за bLength ───────────────────
def fig_descriptor_walk():
    W, H = 940, 576
    f = [text(W / 2, 30, "Плаский буфер дескрипторів → дерево: крок за bLength",
              size=15.5, bold=True)]

    # ── верхня панель: сирий буфер як низка блоків ──
    f.append(text(40, 60,
                  "Сирий буфер: дескриптори склеєні підряд — кожен починається з bLength і bDescriptorType",
                  size=10.8, color=MUTED, anchor="start"))

    blocks = [
        ("Config", 9, NEG), ("Інтф 0", 9, FIELD),
        ("cs", 5, MUTED), ("cs", 5, MUTED), ("cs", 4, MUTED), ("cs", 5, MUTED),
        ("EP·81", 7, POS), ("Інтф 1", 9, FIELD),
        ("EP·02", 7, POS), ("EP·82", 7, POS),
    ]
    x0, bw, gap, top, bh = 40, 82, 6, 74, 58
    for i, (lab, blen, col) in enumerate(blocks):
        x = x0 + i * (bw + gap)
        cx = x + bw / 2
        f.append(rect(x, top, bw, bh, fill=col, stroke=col, sw=1, rx=7))
        f.append(text(cx, top + 25, lab, size=11.5, bold=True, color=BG))
        f.append(text(cx, top + 44, "bLen %d" % blen, size=10, color=BG))

    # стрілка проходу під блоками
    ay = top + bh + 20                       # 152
    f.append(arrow(40, ay, x0 + 10 * (bw + gap) - gap, ay, color=INK, sw=1.8))
    f.append(text(W / 2, ay + 18,
                  "курсор off += bLength — щоразу стрибок на довжину поточного дескриптора",
                  size=10.5, italic=True, color=INK))

    # перехід до дерева
    f.append(arrow(W / 2, ay + 30, W / 2, ay + 54, color=INK, sw=2))
    f.append(text(W / 2 + 16, ay + 48, "switch за bDescriptorType",
                  size=10.5, italic=True, color=MUTED, anchor="start"))

    # ── нижня панель: відновлене дерево ──
    def node(cx, cy, w, h, l1, l2, col):
        out = rect(cx - w / 2, cy - h / 2, w, h, fill=col, stroke=col, sw=1, rx=9)
        if l2:
            out += text(cx, cy - 4, l1, size=11.5, bold=True, color=BG)
            out += text(cx, cy + 14, l2, size=9.8, color=BG)
        else:
            out += text(cx, cy + 5, l1, size=11.5, bold=True, color=BG)
        return out

    cfg = (470, 250)
    if0, if1 = (268, 338), (672, 338)
    ep81, ep02, ep82 = (268, 432), (582, 432), (772, 432)

    # зв'язки (лінії ПЕРЕД вузлами, щоб ховались під ними)
    f.append(line(cfg[0], cfg[1] + 27, if0[0], if0[1] - 25, color=INK, sw=1.6))
    f.append(line(cfg[0], cfg[1] + 27, if1[0], if1[1] - 25, color=INK, sw=1.6))
    f.append(line(if0[0], if0[1] + 25, ep81[0], ep81[1] - 22, color=INK, sw=1.6))
    f.append(line(if1[0], if1[1] + 25, ep02[0], ep02[1] - 22, color=INK, sw=1.6))
    f.append(line(if1[0], if1[1] + 25, ep82[0], ep82[1] - 22, color=INK, sw=1.6))

    f.append(node(cfg[0], cfg[1], 186, 54, "Конфігурація", "тип 2 · wTotalLength=67", NEG))
    f.append(node(if0[0], if0[1], 192, 50, "Інтерфейс 0", "клас 0x02 · CDC-Comm", FIELD))
    f.append(node(if1[0], if1[1], 192, 50, "Інтерфейс 1", "клас 0x0A · CDC-Data", FIELD))
    f.append(node(ep81[0], ep81[1], 176, 44, "0x81 · IN", "переривна", POS))
    f.append(node(ep02[0], ep02[1], 176, 44, "0x02 · OUT", "масова", POS))
    f.append(node(ep82[0], ep82[1], 176, 44, "0x82 · IN", "масова", POS))

    b, _, _ = textbox(W / 2, 522,
                      "Класоспецифічні дескриптори (тип 0x24, сірі блоки) не мають вузла — їх пропущено кроком за bLength",
                      size=10.6, fill=FILL, stroke=MUTED)
    f.append(b)

    render(os.path.join(IMG, "descriptor-walk.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bus_contrast()
    fig_transaction()
    fig_enumeration()
    fig_setup_packet()
    fig_descriptor_walk()
    print("OK: 5 figures ->", IMG)
