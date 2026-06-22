# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURP = "#8a5fb0"   # колір ANS-родини (як у everywhere.svg сусідньої теми)


# ══════════════════════════════════════════════════════════════════════════════
# Базова стаття (asymmetric-numeral-systems.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── single-state: інтервал → одне число ───────────────────────────────────────
# Ідея: арифметичне тримає ДВА числа (low, high) — відрізок; ANS тримає ОДНЕ
# ціле x. Кодувати символ = наростити x; частий росте мало, рідкісний — сильно.

def fig_single_state():
    W, H = 720, 300
    p = []
    # ліворуч: арифметичне — відрізок [low,high)
    lx = 60
    p.append(text(lx + 130, 60, "арифметичне: два числа — відрізок", size=12,
                  color=NEG, bold=True, anchor="middle"))
    ax0, ax1, ay = lx, lx + 260, 110
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=1.4))
    a, b = 0.30, 0.62
    full = ax1 - ax0
    p.append(rect(ax0 + a * full, ay - 10, (b - a) * full, 20, fill="#eef4ff", stroke=NEG, sw=2))
    p.append(text(ax0 + a * full, ay - 18, "low", size=10, color=NEG, anchor="middle", bold=True))
    p.append(text(ax0 + b * full, ay - 18, "high", size=10, color=NEG, anchor="middle", bold=True))
    p.append(text(lx + 130, ay + 38, "звужуємо проміжок", size=11, color=MUTED, italic=True))

    # роздільник
    p.append(line(W / 2, 50, W / 2, H - 40, color="#dddddd", sw=1.2, dash="4 4"))

    # праворуч: ANS — одне ціле x
    rx = W / 2 + 40
    p.append(text(rx + 130, 60, "ANS: одне ціле число — стан x", size=12,
                  color=PURP, bold=True, anchor="middle"))
    bx, by, cell = rx + 60, 95, 38
    digits = ["1", "0", "1", "1", "0"]
    for i, d in enumerate(digits):
        p.append(rect(bx + i * (cell + 3), by, cell, cell, fill="#f2ecf8", stroke=PURP, sw=1.6))
        p.append(text(bx + i * (cell + 3) + cell / 2, by + cell / 2 + 6, d, size=15,
                      color=PURP, bold=True))
    p.append(text(rx + 130, by + cell + 24, "нарощуємо одне число", size=11, color=MUTED, italic=True))

    # спільний підсумок-стрічка
    bb, ww, hh = textbox(W / 2, 250, "частий символ нарощує x мало (мало бітів) · рідкісний — сильно (багато бітів)",
                         size=11, bold=True, fill="#f2ecf8", stroke=PURP, sw=1.5, color=INK)
    p.append(bb)
    render(os.path.join(OUT, "single-state.svg"), W, H, *p,
           title="Замість відрізка [low,high) — одне ціле число-стан")


# ── grow: worked-приклад — x росте символ за символом ─────────────────────────
# Ідея: показати числами, як один стан x збільшується при кожному кодованому
# символі; висота стовпчика ∝ log2(x) = накопичені біти.

def fig_grow():
    W, H = 720, 320
    p = []
    # сценарій (ілюстративні значення стану): старт 1, додаємо символи
    steps = [
        ("старт", 1, INK),
        ("+ A (частий)", 3, FIELD),
        ("+ A (частий)", 7, FIELD),
        ("+ B", 19, NEG),
        ("+ C (рідкісний)", 91, PURP),
    ]
    bx0, y0, bh = 90, 250, 180
    bw, gap = 96, 26
    maxbits = math.log(steps[-1][1] + 1, 2)
    for i, (lab, x, col) in enumerate(steps):
        x_px = bx0 + i * (bw + gap)
        bits = math.log(x, 2) if x > 1 else 0.0
        hh = max(8, bits / maxbits * bh)
        p.append(rect(x_px, y0 - hh, bw, hh, fill="#f2ecf8" if col == PURP else "#f4f6f8",
                      stroke=col, sw=1.8))
        p.append(text(x_px + bw / 2, y0 - hh - 10, "x=%d" % x, size=12, color=col, bold=True))
        p.append(text(x_px + bw / 2, y0 + 16, lab, size=10, color=col, anchor="middle"))
        if i > 0:
            p.append(arrow(x_px - gap + 4, y0 - 30, x_px - 4, y0 - 30, color=MUTED, sw=1.4))
    p.append(text(60, y0 - bh - 6, "біти", size=10, color=MUTED, anchor="end", bold=True))
    p.append(line(72, y0, 72, y0 - bh - 4, color=MUTED, sw=1))
    p.append(text(W / 2, y0 + 50,
                  "висота ∝ log₂(x) = накопичені біти; частий A додає мало, рідкісний C — стрибок",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "grow.svg"), W, H, *p,
           title="Один стан x росте: кожен символ додає рівно −log₂(p) біта")


# ── lifo: кодуємо push, декодуємо pop (стек, зворотний порядок) ────────────────
# Ідея: ANS — стек. Останній закодований символ виходить першим при декодуванні.
# Тому кодер зазвичай іде даними з кінця, щоб декодер видав їх по порядку.

def fig_lifo():
    W, H = 720, 300
    p = []
    syms = ["A", "B", "C"]
    cols = [FIELD, NEG, PURP]
    fills = ["#eafaf0", "#eef4ff", "#f2ecf8"]

    # ліворуч: кодування (push) — стек росте вгору
    sx = 150
    p.append(text(sx, 56, "кодування: push", size=12, color=INK, bold=True, anchor="middle"))
    cell = 44
    base = 230
    order_enc = [("A", 0), ("B", 1), ("C", 2)]   # кодуємо A, потім B, потім C
    for k, (s, ci) in enumerate(order_enc):
        y = base - k * (cell + 4)
        p.append(rect(sx - cell / 2, y - cell, cell, cell, fill=fills[ci], stroke=cols[ci], sw=1.8))
        p.append(text(sx, y - cell / 2 + 6, s, size=16, color=cols[ci], bold=True))
        p.append(text(sx + cell / 2 + 16, y - cell / 2 + 5, "%d-й" % (k + 1), size=10,
                      color=MUTED, anchor="start"))
    p.append(arrow(sx, base + 20, sx, base - 3 * (cell + 4) + 6, color=MUTED, sw=1.5))
    p.append(text(sx, base + 40, "кладемо згори", size=10, color=MUTED, italic=True))

    # стрілка-міст: один стан x
    p.append(arrow(sx + 90, 150, W / 2 + 30, 150, color=INK, sw=1.8))
    b, ww, hh = textbox(W / 2, 110, "стан x", size=13, bold=True, fill="#f2ecf8",
                        stroke=PURP, sw=1.8, color=PURP, pad=12)
    p.append(b)

    # праворуч: декодування (pop) — виходить C, B, A — ЗВОРОТНО
    dx = W - 170
    p.append(text(dx, 56, "декодування: pop", size=12, color=INK, bold=True, anchor="middle"))
    order_dec = [("C", 2), ("B", 1), ("A", 0)]   # виходить у зворотному порядку
    for k, (s, ci) in enumerate(order_dec):
        y = 90 + k * (cell + 4)
        p.append(rect(dx - cell / 2, y, cell, cell, fill=fills[ci], stroke=cols[ci], sw=1.8))
        p.append(text(dx, y + cell / 2 + 6, s, size=16, color=cols[ci], bold=True))
        p.append(text(dx + cell / 2 + 16, y + cell / 2 + 5, "%d-й" % (k + 1), size=10,
                      color=MUTED, anchor="start"))
    p.append(arrow(dx, 90 + 3 * (cell + 4) + 4, dx, 84, color=POS, sw=1.5))
    p.append(text(dx, 90 + 3 * (cell + 4) + 24, "знімаємо згори", size=10, color=POS, italic=True))

    p.append(text(W / 2, H - 16,
                  "останній закодований виходить першим — LIFO; тому кодер обробляє дані з кінця",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "lifo.svg"), W, H, *p,
           title="ANS — стек: декодування йде у зворотному порядку")


# ── rans-vs-tans: дві реалізації однієї ідеї ──────────────────────────────────
# Ідея: rANS — формула з множенням/діленням (гнучка, точна); tANS — заздалегідь
# порахована ТАБЛИЦЯ-автомат (без множень, дуже швидка). Та сама щільність.

def fig_rans_vs_tans():
    W, H = 720, 300
    p = []
    # rANS ліворуч
    lx, ly, lw, lh = 50, 70, 300, 190
    p.append(rect(lx, ly, lw, lh, fill="#fbfbfd", stroke=NEG, sw=1.8))
    p.append(text(lx + lw / 2, ly + 26, "rANS (range)", size=14, color=NEG, bold=True))
    p.append(fitbox(lx + 18, ly + 44, lw - 36, 46,
                    "x ← (x / freq)·total + (x mod freq) + cum",
                    size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.2, color=INK))
    for i, t in enumerate([
            "формула з множенням і діленням",
            "будь-які частоти, гнучко",
            "одне ділення в гарячому циклі"]):
        p.append(text(lx + 18, ly + 116 + i * 22, "• " + t, size=11, color=INK, anchor="start"))

    # tANS праворуч
    rx, ry = 370, 70
    p.append(rect(rx, ry, lw, lh, fill="#fbfbfd", stroke=PURP, sw=1.8))
    p.append(text(rx + lw / 2, ry + 26, "tANS (table)", size=14, color=PURP, bold=True))
    # маленька таблиця-автомат
    tx, ty, tc = rx + 26, ry + 42, 30
    p.append(text(tx + 2, ty - 4, "стан", size=9, color=MUTED, anchor="start"))
    p.append(text(tx + 110, ty - 4, "→ симв, новий стан", size=9, color=MUTED, anchor="start"))
    rows = [("0", "A · 4"), ("1", "A · 5"), ("2", "B · 2"), ("3", "C · 0")]
    for i, (s, r) in enumerate(rows):
        yy = ty + i * tc
        p.append(rect(tx, yy, tc, tc - 4, fill="#f2ecf8", stroke=PURP, sw=1.0))
        p.append(text(tx + tc / 2, yy + tc / 2 + 2, s, size=11, color=PURP, bold=True))
        p.append(text(tx + tc + 18, yy + tc / 2 + 2, r, size=11, color=INK, anchor="start"))
    p.append(text(rx + 200, ry + 150, "лише пошук —", size=11, color=PURP, anchor="start", bold=True))
    p.append(text(rx + 200, ry + 168, "без множень", size=11, color=PURP, anchor="start", bold=True))

    p.append(text(W / 2, H - 16,
                  "та сама ідея й та сама щільність; tANS міняє множення на заздалегідь пораховану таблицю",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "rans-vs-tans.svg"), W, H, *p,
           title="Два різновиди ANS: формула (rANS) і таблиця-автомат (tANS)")


# ── where: де живе ANS і кого витіснив ────────────────────────────────────────
# Ідея: ANS поєднав щільність арифметичного зі швидкістю Гаффмана — тому в
# нових кодеках витіснив обидва. Показати «батьків» і список продуктів.

def fig_where():
    W, H = 720, 320
    p = []
    # два «батьки» згори
    b1, w1, h1 = textbox(200, 70, "Гаффман\nшвидкий, але цілі біти", size=11, bold=True,
                         fill="#eafaf0", stroke=FIELD, sw=1.6, color=INK)
    b2, w2, h2 = textbox(520, 70, "арифметичне\nточне, але повільніше", size=11, bold=True,
                         fill="#eef4ff", stroke=NEG, sw=1.6, color=INK)
    p.append(b1); p.append(b2)
    # ANS посередині-нижче
    bc, wc, hc = textbox(W / 2, 168, "ANS\nщільність арифметичного + швидкість Гаффмана",
                         size=12, bold=True, fill="#f2ecf8", stroke=PURP, sw=2.2, color=INK, pad=14)
    p.append(line(200, 70 + h1 / 2, W / 2 - 60, 168 - hc / 2, color=FIELD, sw=1.5))
    p.append(line(520, 70 + h2 / 2, W / 2 + 60, 168 - hc / 2, color=NEG, sw=1.5))
    p.append(bc)
    # продукти знизу
    prods = ["Zstandard\n(FSE)", "JPEG XL", "LZFSE", "CRAM", "Draco"]
    n = len(prods)
    pw, pg = 110, 18
    x0 = (W - (n * pw + (n - 1) * pg)) / 2
    for i, pr in enumerate(prods):
        x = x0 + i * (pw + pg)
        b, bw, bh = textbox(x + pw / 2, 268, pr, size=10, bold=True,
                            fill="#fbfbfd", stroke=PURP, sw=1.4, color=PURP)
        p.append(line(W / 2, 168 + hc / 2, x + pw / 2, 268 - bh / 2, color="#cbb8de", sw=1.0))
        p.append(b)
    render(os.path.join(OUT, "where.svg"), W, H, *p,
           title="ANS витіснив обох батьків у нових кодеках")


# ══════════════════════════════════════════════════════════════════════════════
# Детальна стаття (asymmetric-numeral-systems-d.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── why-one-number: log2(x) як «лічильник бітів» ──────────────────────────────
# Ідея: одне натуральне x несе всю інформацію, бо log2(x) — це накопичені біти;
# додавання символу s робить log2(x) ← log2(x) + log2(1/p_s). Renorm зливає
# молодші біти в потік, тримаючи x у вікні регістра.

def fig_why_one_number():
    W, H = 720, 300
    p = []
    # вісь: log2(x) росте; позначки «+log2(1/p)» на сходинках
    ax0, ay = 90, 230
    aw, ah = 540, 160
    p.append(arrow(ax0, ay, ax0, ay - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ax0, ay, ax0 + aw, ay, color=INK, sw=1.6))
    p.append(text(ax0 - 10, ay - ah, "log₂(x)", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(ax0 - 10, ay - ah + 16, "(біти)", size=9, color=MUTED, anchor="end"))
    p.append(text(ax0 + aw, ay + 20, "символи →", size=11, color=INK, italic=True, anchor="end"))

    # сходинки накопичення бітів
    inc = [(1.0, "A", FIELD), (1.0, "A", FIELD), (2.3, "B", NEG), (3.6, "C", PURP)]
    x = ax0
    lvl = 0.0
    step_w = aw / (len(inc) + 1)
    total = sum(i[0] for i in inc)
    for di, lab, col in inc:
        y0 = ay - lvl / total * ah
        lvl += di
        y1 = ay - lvl / total * ah
        # горизонталь + вертикаль сходинки
        p.append(line(x, y0, x + step_w, y0, color=MUTED, sw=1.2))
        p.append(line(x + step_w, y0, x + step_w, y1, color=col, sw=2.4))
        p.append(text(x + step_w + 6, (y0 + y1) / 2 + 4, "+%.1f (%s)" % (di, lab),
                      size=10, color=col, anchor="start", bold=True))
        x += step_w
    p.append(text(ax0 + 8, ay - ah + 4,
                  "кожен символ додає −log₂(p) біта до log₂(x)", size=10,
                  color=MUTED, anchor="start", italic=True))

    # рамка про renorm
    bb, ww, hh = textbox(W / 2, H - 30, "x росте без меж → renormalization зливає молодші байти в потік, тримаючи x у вікні регістра",
                         size=10, bold=True, fill="#f2ecf8", stroke=PURP, sw=1.4, color=INK)
    p.append(bb)
    render(os.path.join(OUT, "why-one-number.svg"), W, H, *p,
           title="Чому одне число несе все: log₂(x) — це накопичені біти")


# ── rans-formula: C(s,x) і D(x) як обернені операції ──────────────────────────
# Ідея: кодер C і декодер D — точні взаємно-обернені функції над станом x.

def fig_rans_formula():
    W, H = 720, 300
    p = []
    # верх: кодування C
    p.append(text(W / 2, 56, "кодер C: додає символ s до стану", size=12, color=NEG, bold=True))
    p.append(fitbox(110, 74, 500, 40, "x' = (x / freq_s)·total + (x mod freq_s) + cum_s",
                    size=13, bold=True, fill="#eef4ff", stroke=NEG, sw=1.5, color=INK))
    # стан x  --C(s)-->  x'
    p.append(textbox(170, 160, "x", size=15, bold=True, fill="#fbfbfd", stroke=INK, sw=1.6, color=INK, pad=14)[0])
    p.append(textbox(W - 170, 160, "x'", size=15, bold=True, fill="#fbfbfd", stroke=INK, sw=1.6, color=INK, pad=14)[0])
    p.append(arrow(200, 150, W - 200, 150, color=NEG, sw=2))
    p.append(text(W / 2, 142, "C(s, x)", size=12, color=NEG, bold=True))
    p.append(arrow(W - 200, 178, 200, 178, color=POS, sw=2))
    p.append(text(W / 2, 200, "D(x') = (s, x)", size=12, color=POS, bold=True))

    # низ: декодування D
    p.append(text(W / 2, 244, "декодер D: дістає символ s і відновлює попередній стан", size=12,
                  color=POS, bold=True))
    p.append(fitbox(110, 258, 500, 34, "s = symbol(x' mod total);   x = freq_s·(x' / total) + (x' mod total) − cum_s",
                    size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.4, color=INK))
    render(os.path.join(OUT, "rans-formula.svg"), W, H, *p,
           title="rANS: кодер і декодер — точні взаємно-обернені дії над x")


# ── tans-fsm: скінченний автомат tANS ─────────────────────────────────────────
# Ідея: tANS — таблиця переходів. Поточний стан + прочитаний символ → видати
# біти renorm і перейти в новий стан. Жодного множення.

def fig_tans_fsm():
    W, H = 720, 310
    p = []
    # кілька станів як кружечки з переходами
    states = [("s0", 150, 120), ("s1", 360, 90), ("s2", 570, 130), ("s3", 360, 230)]
    pos = {n: (x, y) for n, x, y in states}
    for n, x, y in states:
        p.append(circle(x, y, 30, fill="#f2ecf8", stroke=PURP, sw=2))
        p.append(text(x, y + 5, n, size=13, color=PURP, bold=True))
    # переходи (символ / вихідні біти)
    edges = [("s0", "s1", "A"), ("s1", "s2", "A"), ("s2", "s3", "B / 01"),
             ("s3", "s0", "C / 1"), ("s1", "s3", "B")]
    for a, b, lab in edges:
        x1, y1 = pos[a]; x2, y2 = pos[b]
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        sx, sy = x1 + ux * 30, y1 + uy * 30
        ex, ey = x2 - ux * 30, y2 - uy * 30
        p.append(arrow(sx, sy, ex, ey, color=MUTED, sw=1.5))
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        p.append(text(mx, my - 6, lab, size=10, color=INK, bold=True))
    p.append(text(W / 2, H - 40,
                  "поточний стан + символ → видати біти renorm і перейти в новий стан",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, H - 20,
                  "увесь крок — пошук у таблиці; множень нема — тому tANS дуже швидкий",
                  size=11, color=PURP, italic=True, bold=True))
    render(os.path.join(OUT, "tans-fsm.svg"), W, H, *p,
           title="tANS — скінченний автомат: крок = пошук у таблиці")


# ── renorm-stream: x тримають у вікні [L, b·L) ────────────────────────────────
# Ідея: щоб x не переріс регістр, тримають його у вузькому вікні: переріс верх —
# злий молодший байт у потік (x велике вниз); присів під низ — підтягни байт.

def fig_renorm_stream():
    W, H = 720, 300
    p = []
    # вертикальна шкала-вікно
    cx = 200
    top, bot = 70, 250
    p.append(line(cx, top, cx, bot, color=INK, sw=1.6))
    p.append(line(cx - 60, top, cx + 60, top, color=POS, sw=2))
    p.append(line(cx - 60, bot, cx + 60, bot, color=NEG, sw=2))
    p.append(text(cx + 70, top + 4, "b·L  (стеля)", size=11, color=POS, anchor="start", bold=True))
    p.append(text(cx + 70, bot + 4, "L  (дно)", size=11, color=NEG, anchor="start", bold=True))
    p.append(rect(cx - 40, top + 8, 80, bot - top - 16, fill="#f2ecf8", stroke=PURP, sw=1.4))
    p.append(text(cx, (top + bot) / 2, "робоче", size=11, color=PURP, bold=True))
    p.append(text(cx, (top + bot) / 2 + 18, "вікно x", size=11, color=PURP, bold=True))

    # праворуч: дві дії
    rx = 430
    b1, w1, h1 = textbox(rx + 130, 110, "кодер: x перевалив стелю →\nзлий молодший байт у потік (x ÷ 256)",
                         size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.4, color=INK)
    p.append(b1)
    p.append(arrow(cx + 44, top + 30, rx, 110, color=POS, sw=1.5))
    b2, w2, h2 = textbox(rx + 130, 200, "декодер: x присів під дно →\nпідтягни байт із потоку (x · 256 + b)",
                         size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.4, color=INK)
    p.append(b2)
    p.append(arrow(cx + 44, bot - 30, rx, 200, color=NEG, sw=1.5))

    p.append(text(W / 2, H - 16,
                  "renormalization тримає x у вузькому вікні — скінченний регістр, нескінченний потік",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "renorm-stream.svg"), W, H, *p,
           title="Renormalization потоком байтів: x завжди у вікні [L, b·L)")


# ── patent: хронологія патентного спротиву ────────────────────────────────────
# Ідея: Дуда лишив ANS у відкритому доступі; Google спробував запатентувати
# (відкликано після відмови USPTO 2018); Microsoft дістав вужчий патент 2022.

def fig_patent():
    W, H = 720, 280
    p = []
    # горизонтальна вісь часу (відступ від країв, щоб крайні рамки не тиснулись)
    ax0, ax1, ay = 110, 610, 120
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=1.6))
    years = [(2009, "Дуда: ANS\nу відкритий доступ", FIELD, -1),
             (2015, "Google подає\nпатентну заявку", POS, 1),
             (2018, "USPTO відмовляє;\nGoogle відкликає", FIELD, -1),
             (2022, "Microsoft дістає\nвужчий патент на rANS", POS, 1)]
    span = years[-1][0] - years[0][0]
    for yr, lab, col, side in years:
        x = ax0 + (yr - years[0][0]) / span * (ax1 - ax0)
        p.append(circle(x, ay, 7, fill=col, stroke=col, sw=1))
        p.append(text(x, ay + (28 if side > 0 else -16), str(yr), size=12, color=INK, bold=True))
        by = ay + side * 64
        b, bw, bh = textbox(x, by, lab, size=10, bold=True,
                            fill="#fbfbfd", stroke=col, sw=1.4, color=INK)
        # притиснути до полотна по краях
        p.append(b)
    p.append(text(W / 2, H - 14,
                  "Дуда свідомо тримав ANS вільним; саме тому він розійшовся по кодеках, попри пізні патентні спроби",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "patent.svg"), W, H, *p,
           title="Патентний спротив: чому ANS лишився вільним")


if __name__ == "__main__":
    # базова
    fig_single_state()
    fig_grow()
    fig_lifo()
    fig_rans_vs_tans()
    fig_where()
    # детальна
    fig_why_one_number()
    fig_rans_formula()
    fig_tans_fsm()
    fig_renorm_stream()
    fig_patent()
    print("OK: figures written to", OUT)
