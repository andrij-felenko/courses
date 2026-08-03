# -*- coding: utf-8 -*-
"""Фігури до теми «GPIO-регістри».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── спільний примітив: рядок бітів регістра ─────────────────────────────────
def bit_cell(x, y, val, w=26, h=26, hot=False):
    """Клітинка біта: 0 — сіра, 1 — синя (виділена)."""
    fill = "#e9eefb" if val else BG
    col = NEG if val else MUTED
    out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s" '
           'stroke="%s" stroke-width="1.4"/>' % (x, y, w, h, fill, INK))
    out += text(x + w / 2, y + h * 0.68, str(val), size=15, color=col, bold=True)
    return out


def bit_row(x, y, bits, w=26, h=26, labels=None):
    """Рядок бітів (старший зліва). labels — список номерів під клітинками."""
    out = ""
    for i, b in enumerate(bits):
        cx = x + i * w
        out += bit_cell(cx, y, b, w, h)
        if labels is not None:
            out += text(cx + w / 2, y + h + 12, str(labels[i]), size=9, color=MUTED)
    return out


# ── 1. Регістр GPIO_OUT: один біт — одна ніжка ──────────────────────────────
def fig_out_register_bits():
    W, H = 760, 320
    f = [text(W / 2, 30, "GPIO_OUT: біт n керує ніжкою GPIOn", size=17, bold=True)]
    f.append(text(W / 2, 52, "стан усіх ніжок порту лежить в одній комірці пам'яті",
                  size=12, color=MUTED, italic=True))

    bits = [0, 0, 1, 0, 0, 1, 0, 0]   # біти 7..0; 1 на бітах 5 і 2
    labels = [7, 6, 5, 4, 3, 2, 1, 0]
    cw = 48
    x0 = (W - cw * len(bits)) / 2
    y0 = 92
    f.append(text(x0 - 14, y0 + 18, "біт:", size=11, color=INK, anchor="end", bold=True))
    f.append(bit_row(x0, y0, bits, w=cw, h=48, labels=labels))

    # стрілки вниз від «1»-бітів
    for idx, name in ((2, "GPIO5"), (5, "GPIO2")):
        cx = x0 + idx * cw + cw / 2
        f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.8" marker-end="url(#arrow)"/>' % (cx, y0 + 62, cx, y0 + 100, NEG))
        f.append(text(cx, y0 + 124, name + " = HIGH", size=11, color=NEG, bold=True))

    f.append(text(W / 2, 258, "Записати «1» у біт n → GPIOn стає HIGH; «0» → LOW.",
                  size=12, bold=True))
    f.append(text(W / 2, 282, "Рівні входів читають із дзеркального регістра GPIO_IN — так само побітно.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "out-register-bits.svg"), W, H, *f)


# ── 2. digitalWrite (кілька кроків) проти прямого запису (один крок) ─────────
def fig_digitalwrite_vs_register():
    W, H = 849, 360
    f = [text(W / 2, 30, "digitalWrite — виклик функції; прямий запис — одна дія", size=16, bold=True)]
    f.append(text(W / 2, 52, "за зручність обгортки платять часом", size=12, color=MUTED, italic=True))

    # верхній ряд: digitalWrite — 4 кроки
    f.append(text(60, 96, "digitalWrite(2, HIGH):", size=12, bold=True, anchor="start"))
    steps = [("виклик", "функції"), ("знайти регістр", "і біт за № піна"),
             ("перевірки", "безпеки"), ("запис у", "регістр")]
    bx, by, bw, bh, gap = 60, 112, 160, 54, 26
    for i, (a, b) in enumerate(steps):
        x = bx + i * (bw + gap)
        stroke = FIELD if i == 3 else MUTED
        fill = "#eef6ef" if i == 3 else "#f2f2f2"
        f.append(rect(x, by, bw, bh, fill=fill, stroke=stroke, sw=1.6, rx=8))
        f.append(text(x + bw / 2, by + 24, a, size=11, bold=True))
        f.append(text(x + bw / 2, by + 42, b, size=9, color=MUTED))
        if i < 3:
            f.append(arrow(x + bw, by + bh / 2, x + bw + gap, by + bh / 2, color=INK))
    f.append(text(bx + 4 * (bw + gap) - gap + 6, by + bh / 2 + 4, "≈ 1 мкс",
                  size=13, color=POS, bold=True, anchor="start"))

    # нижній ряд: прямий запис — один крок
    f.append(text(60, 232, "GPIO.out_w1ts = (1 << 2):", size=12, bold=True, anchor="start"))
    f.append(rect(60, 248, bw, bh, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(60 + bw / 2, 248 + 24, "запис у", size=11, bold=True))
    f.append(text(60 + bw / 2, 248 + 42, "регістр", size=9, color=MUTED))
    f.append(text(60 + bw + 16, 248 + bh / 2 + 4,
                  "≈ одиниці–десятки нс  (у десятки разів швидше)",
                  size=12, color=FIELD, bold=True, anchor="start"))

    f.append(rect(60, 322, W - 120, 30, fill="#fff6e0", stroke="#caa24a", sw=1.4, rx=8))
    f.append(text(W / 2, 341,
                  "Рідкі перемикання — digitalWrite зручний; «гарячі» — прямий регістр.",
                  size=11, bold=True))
    render(os.path.join(IMG, "digitalwrite-vs-register.svg"), W, H, *f)


# ── 3. Чотири бітові операції з маскою (1<<3) ───────────────────────────────
def fig_bit_operations():
    W, H = 940, 410
    f = [text(W / 2, 30, "set / clear / toggle / read на масці (1 << 3)", size=17, bold=True)]
    f.append(text(W / 2, 52, "чіпаємо лише біт 3 — сусіди (інші ніжки) без змін",
                  size=12, color=MUTED, italic=True))

    before = [0, 0, 1, 0, 0, 1, 0, 0]   # біти 7..0; одиниці на 5 і 2
    rows = [
        ("set",    "REG |= (1<<3)",   FIELD, [0, 0, 1, 0, 1, 1, 0, 0], "біт 3 → 1, решта без змін"),
        ("clear",  "REG &= ~(1<<3)",  POS,   [0, 0, 1, 0, 0, 1, 0, 0], "біт 3 → 0, решта без змін"),
        ("toggle", "REG ^= (1<<3)",   NEG,   [0, 0, 1, 0, 1, 1, 0, 0], "біт 3 перевернувся"),
        ("read",   "(GPIO_IN>>3)&1",  INK,   None,                     "лишається лише потрібний біт"),
    ]
    cw = 22
    y = 86
    for name, code, col, after, note in rows:
        # картка операції
        f.append(rect(50, y, 250, 60, fill="#fbfcff", stroke=col, sw=1.6, rx=8))
        f.append(text(64, y + 24, name, size=13, color=col, bold=True, anchor="start"))
        f.append(text(64, y + 46, code, size=12, bold=True, anchor="start"))
        # «до»
        bx = 330
        f.append(bit_row(bx, y + 10, before, w=cw, h=22))
        if after is not None:
            f.append(text(bx + 8 * cw + 14, y + 26, "→", size=15, bold=True, anchor="start"))
            f.append(bit_row(bx + 8 * cw + 30, y + 10, after, w=cw, h=22))
            f.append(text(bx + 16 * cw + 44, y + 26, note, size=10, anchor="start"))
        else:
            # read: видобули біт 3 = 1
            f.append(text(bx + 8 * cw + 14, y + 26, "→ біт 3 =", size=12, bold=True, anchor="start"))
            f.append(text(bx + 8 * cw + 92, y + 26, "1", size=16, color=FIELD, bold=True, anchor="start"))
            f.append(text(bx + 16 * cw + 44, y + 26, note, size=10, anchor="start"))
        y += 78
    render(os.path.join(IMG, "bit-operations.svg"), W, H, *f)


# ── 4. W1TS / W1TC проти read-modify-write ──────────────────────────────────
def fig_w1ts_w1tc():
    W, H = 860, 410
    f = [text(W / 2, 30, "Атомарні W1TS / W1TC: без «прочитав-змінив-записав»", size=16, bold=True)]
    f.append(text(W / 2, 52, "запис маски прямо ставить або скидає лише потрібні біти — одним рухом",
                  size=12, color=MUTED, italic=True))

    # небезпека
    f.append(rect(40, 76, W - 80, 138, fill="none", stroke=POS, sw=1.6, rx=12))
    f.append(text(60, 100, "Небезпека: REG |= mask — це три дії (read-modify-write)",
                  size=12, color=POS, bold=True, anchor="start"))
    steps = ["1) прочитати REG", "2) АБО з маскою", "3) записати назад"]
    bx, by, bw, bh, gap = 100, 116, 180, 44, 60
    for i, s in enumerate(steps):
        x = bx + i * (bw + gap)
        f.append(rect(x, by, bw, bh, fill=BG, stroke=MUTED, sw=1.4, rx=8))
        f.append(text(x + bw / 2, by + 28, s, size=11, bold=True))
        if i < 2:
            f.append(arrow(x + bw, by + bh / 2, x + bw + gap, by + bh / 2, color=INK))
    f.append(text(W / 2, 200,
                  "Втрутиться переривання між 1 і 3 — твій запис ЗАТРЕ його зміну (гонка).",
                  size=11, color=POS, bold=True))

    # безпека
    f.append(rect(40, 234, W - 80, 150, fill="none", stroke=FIELD, sw=1.6, rx=12))
    f.append(text(60, 258, "Безпечно: GPIO.out_w1ts = mask — одна атомарна дія",
                  size=12, color=FIELD, bold=True, anchor="start"))
    f.append(text(80, 290, "W1TS (write-1-to-set):", size=11, bold=True, anchor="start"))
    f.append(text(100, 312, "де в масці 1 — той біт стає 1; де 0 — біт без змін.",
                  size=10.5, anchor="start"))
    f.append(text(80, 344, "W1TC (write-1-to-clear):", size=11, bold=True, anchor="start"))
    f.append(text(100, 366, "де в масці 1 — той біт стає 0; де 0 — біт без змін.",
                  size=10.5, anchor="start"))
    b, w0, h0 = textbox(700, 326, "Залізо саме чіпає\nлише потрібні біти —\nчитати нічого не треба.",
                        size=10.5, color=FIELD, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "w1ts-w1tc.svg"), W, H, *f)


# ── 5. Кілька ніжок одним записом синхронно проти послідовних digitalWrite ──
def fig_multipin_sync():
    W, H = 820, 420
    f = [text(W / 2, 30, "Один масковий запис підіймає кілька ніжок СИНХРОННО", size=16, bold=True)]
    f.append(text(W / 2, 52, "послідовні digitalWrite зсувають фронти на мікросекунди",
                  size=12, color=MUTED, italic=True))

    pins = ["GPIO2", "GPIO3", "GPIO4", "GPIO5"]
    x0, span = 150, 560
    lo, hi = 24, 20   # рівні відносно базової лінії

    # ── ліворуч/угорі: 4 digitalWrite — східчасто зсунуті фронти ──
    f.append(text(60, 94, "4× digitalWrite — врозкид:", size=12, bold=True, anchor="start"))
    top = 110
    for i, p in enumerate(pins):
        base = top + i * 36
        edge = x0 + (i + 1) * 70    # кожна ніжка піднімається пізніше
        f.append(text(x0 - 12, base + 4, p, size=10, anchor="end", color=INK))
        pts = "%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" % (
            x0, base, edge, base, edge, base - hi, x0 + span, base - hi)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (pts, NEG))
        f.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="1" '
                 'stroke-dasharray="3 3"/>' % (edge, base - hi, edge, top - 6, MUTED))
    f.append(text(x0 + 70, top - 14, "фронти розповзаються →", size=10, color=POS,
                  bold=True, anchor="start"))

    # ── праворуч/унизу: один масковий запис — спільний фронт ──
    f.append(text(60, 290, "1× масковий запис — разом:", size=12, bold=True, anchor="start"))
    bot = 306
    edge = x0 + 150
    for i, p in enumerate(pins):
        base = bot + i * 26
        f.append(text(x0 - 12, base + 4, p, size=10, anchor="end", color=INK))
        pts = "%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" % (
            x0, base, edge, base, edge, base - hi, x0 + span, base - hi)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (pts, FIELD))
    f.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="1.4" '
             'stroke-dasharray="4 3"/>' % (edge, bot - 14, edge, bot + 3 * 26 + 6, POS))
    f.append(text(edge + 10, bot - 6, "спільний фронт", size=10, color=FIELD, bold=True, anchor="start"))
    f.append(text(x0, 412, "GPIO.out_w1ts = (1<<2)|(1<<3)|(1<<4)|(1<<5);",
                  size=11, bold=True, anchor="start"))
    render(os.path.join(IMG, "multipin-sync.svg"), W, H, *f)


# ── 6. Карта GPIO-регістрів ESP32 ───────────────────────────────────────────
def fig_esp32_gpio_registers():
    W, H = 820, 360
    f = [text(W / 2, 30, "Карта GPIO-регістрів ESP32", size=17, bold=True)]
    f.append(text(W / 2, 52, "ніжок більше за 32 → дві групи: 0–31 і 32–39 (регістри з «1» у назві)",
                  size=12, color=MUTED, italic=True))

    cols = [("Вихід (стан)", ["GPIO_OUT", "GPIO_OUT1"], NEG),
            ("Атомарний set/скид", ["GPIO_OUT_W1TS", "GPIO_OUT_W1TC"], FIELD),
            ("Напрям", ["GPIO_ENABLE", "GPIO_ENABLE1"], "#8a5a00"),
            ("Вхід (рівень)", ["GPIO_IN", "GPIO_IN1"], INK)]
    cw, gap = 180, 16
    total = len(cols) * cw + (len(cols) - 1) * gap
    x0 = (W - total) / 2
    y = 92
    for i, (head, regs, col) in enumerate(cols):
        x = x0 + i * (cw + gap)
        f.append(rect(x, y, cw, 150, fill="#fbfcff", stroke=col, sw=1.6, rx=10))
        f.append(text(x + cw / 2, y + 26, head, size=11.5, color=col, bold=True))
        for j, r in enumerate(regs):
            f.append(rect(x + 14, y + 44 + j * 44, cw - 28, 34, fill=BG, stroke=MUTED, sw=1.2, rx=6))
            f.append(text(x + cw / 2, y + 44 + j * 44 + 22, r, size=11, bold=True))
    f.append(text(x0 + total / 2, y + 178, "Усі мають фіксовані адреси в пам'яті (memory-mapped).",
                  size=11, color=MUTED))
    f.append(text(x0 + total / 2, y + 200,
                  "pinMode → ENABLE · digitalWrite → OUT (W1TS/W1TC) · digitalRead → IN",
                  size=11, bold=True))
    render(os.path.join(IMG, "esp32-gpio-registers.svg"), W, H, *f)


# ── 7. (вставка) Біт-бенгінг: код сам формує хвилі DATA і CLK ────────────────
def fig_bitbang_idea():
    W, H = 780, 340
    f = [text(W / 2, 30, "Біт-бенгінг: протокол — це послідовність станів ніжок у часі", size=15, bold=True)]
    f.append(text(W / 2, 52, "на кожен біт: постав DATA, дай імпульс CLK (↑ потім ↓)",
                  size=12, color=MUTED, italic=True))

    x0, span = 120, 600
    bits = [1, 0, 1, 1, 0]
    n = len(bits)
    step = span / n
    hi = 26

    # DATA
    dy = 120
    f.append(text(x0 - 14, dy + 4, "DATA", size=11, anchor="end", bold=True, color=NEG))
    pts = []
    for i, b in enumerate(bits):
        x = x0 + i * step
        lvl = dy - hi if b else dy
        pts.append("%.0f,%.0f" % (x, lvl))
        pts.append("%.0f,%.0f" % (x + step, lvl))
        f.append(text(x + step / 2, dy - hi - 8, str(b), size=11, color=NEG, bold=True))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), NEG))

    # CLK — імпульс усередині кожного біта
    cy = 220
    f.append(text(x0 - 14, cy + 4, "CLK", size=11, anchor="end", bold=True, color=POS))
    pts = []
    for i in range(n):
        x = x0 + i * step
        q = step / 4
        pts += ["%.0f,%.0f" % (x, cy), "%.0f,%.0f" % (x + q, cy),
                "%.0f,%.0f" % (x + q, cy - hi), "%.0f,%.0f" % (x + 3 * q, cy - hi),
                "%.0f,%.0f" % (x + 3 * q, cy), "%.0f,%.0f" % (x + step, cy)]
        # фронт читання
        f.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="1" '
                 'stroke-dasharray="3 3"/>' % (x + q, cy - hi, x + q, dy, MUTED))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), POS))

    f.append(text(W / 2, 288, "Приймач читає DATA по фронту CLK (↑).", size=11, bold=True))
    f.append(text(W / 2, 310, "Відтвори цю послідовність кодом — і ти реалізував протокол.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "bitbang-idea.svg"), W, H, *f)


# ── 8. (вставка) Дві ціни біт-бенгінгу: швидкість і зайнятість ядра ──────────
def fig_bitbang_cost():
    W, H = 780, 340
    f = [text(W / 2, 30, "Дві ціни біт-бенгінгу", size=17, bold=True)]
    f.append(text(W / 2, 52, "швидкість виклику й зайнятість ядра", size=12, color=MUTED, italic=True))

    # ліва панель: швидкість
    f.append(rect(40, 76, 350, 240, fill="#fbfcff", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(40 + 175, 102, "Швидкість одного перемикання", size=12.5, bold=True))
    # дві смуги
    f.append(text(70, 150, "digitalWrite", size=11, anchor="start", bold=True, color=POS))
    f.append(rect(70, 158, 280, 28, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    f.append(text(70 + 140, 177, "≈ 2 мкс  (ледача шина)", size=11, color=POS, bold=True))
    f.append(text(70, 224, "прямий регістр", size=11, anchor="start", bold=True, color=FIELD))
    f.append(rect(70, 232, 56, 28, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(70 + 150, 251, "наносекунди  (швидка)", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(40 + 175, 296, "швидкість шини = темп вашого циклу", size=10.5, color=MUTED))

    # права панель: зайнятість ядра
    f.append(rect(410, 76, 330, 240, fill="#fbfcff", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(410 + 165, 102, "Хто жене дані", size=12.5, bold=True))
    f.append(text(575, 140, "біт-бенгінг", size=11, bold=True, color=POS))
    b1, _, _ = textbox(575, 178, "ядро зайняте\nцілком — більше\nнічого не робить",
                       size=10.5, color=POS, fill="#fdecea", stroke=POS, min_w=210)
    f.append(b1)
    f.append(text(575, 238, "апаратний блок", size=11, bold=True, color=FIELD))
    b2, _, _ = textbox(575, 276, "жене дані у фоні —\nядро вільне",
                       size=10.5, color=FIELD, fill="#eef6ef", stroke=FIELD, min_w=210)
    f.append(b2)
    render(os.path.join(IMG, "bitbang-cost.svg"), W, H, *f)


if __name__ == "__main__":
    fig_out_register_bits()
    fig_digitalwrite_vs_register()
    fig_bit_operations()
    fig_w1ts_w1tc()
    fig_multipin_sync()
    fig_esp32_gpio_registers()
    fig_bitbang_idea()
    fig_bitbang_cost()
    print("OK: figures written to", IMG)
