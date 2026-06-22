# -*- coding: utf-8 -*-
"""Фігури до теми «Memory-mapped IO».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── спільний примітив: клітинка біта й рядок бітів ──────────────────────────
def bit_cell(x, y, val, w=26, h=26, hot=False):
    """Клітинка біта: 0 — бліда, 1 — виділена; hot — підсвітити змінюваний біт."""
    if hot:
        fill, col, sw = "#fdecea", POS, 1.8
    elif val:
        fill, col, sw = "#e9eefb", NEG, 1.4
    else:
        fill, col, sw = BG, MUTED, 1.4
    out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s" '
           'stroke="%s" stroke-width="%.1f"/>' % (x, y, w, h, fill, INK, sw))
    out += text(x + w / 2, y + h * 0.68, str(val), size=15, color=col, bold=True)
    return out


def bit_row(x, y, bits, w=26, h=26, labels=None, hot=None):
    """Рядок бітів (старший зліва). labels — номери під клітинками; hot — індекс гарячого."""
    out = ""
    for i, b in enumerate(bits):
        cx = x + i * w
        out += bit_cell(cx, y, b, w, h, hot=(hot is not None and i == hot))
        if labels is not None:
            out += text(cx + w / 2, y + h + 12, str(labels[i]), size=9, color=MUTED)
    return out


# ── 1. Єдиний адресний простір: Flash, SRAM, периферія ──────────────────────
def fig_address_map():
    W, H = 820, 545
    f = [text(W / 2, 30, "Єдиний адресний простір МК", size=17, bold=True)]
    f.append(text(W / 2, 52, "пам'ять і керування залізом — на одній карті адрес, на спільній шині",
                  size=12, color=MUTED, italic=True))

    # вертикальна карта адрес: низ — 0x0, верх — старші адреси
    bx, bw = 250, 320
    top, bot = 96, 470
    bands = [
        ("Flash — код",        "#eef6ef", FIELD, 0.30),
        ("SRAM — дані",        "#eaf0fd", NEG,   0.24),
        ("(діра)",             "#f4f6f8", MUTED, 0.06),
        ("Периферія — регістри", "#fdecea", POS, 0.40),
    ]
    # малюємо знизу вгору
    y = bot
    for name, fill, col, frac in bands:
        h = (bot - top) * frac
        yb = y - h
        f.append(rect(bx, yb, bw, h, fill=fill, stroke=col, sw=1.8, rx=4))
        f.append(text(bx + bw / 2, (yb + y) / 2 + 5,
                      name, size=12.5, color=col, bold=True))
        y = yb

    # вісь адрес зліва
    f.append(line(bx - 22, top, bx - 22, bot, color=INK, sw=1.4))
    f.append(arrow(bx - 22, top + 6, bx - 22, top - 4, color=INK))
    f.append(text(bx - 30, top - 10, "адреса", size=10, color=INK, anchor="end"))
    f.append(text(bx - 30, bot + 4, "0x0000…", size=10, color=MUTED, anchor="end"))
    f.append(text(bx - 30, top + 2, "0xFFFF…", size=10, color=MUTED, anchor="end"))

    # праворуч: периферійний діапазон розкладено на вузли
    px = bx + bw + 34
    f.append(text(px, top - 6, "периферійний діапазон:", size=11, bold=True, anchor="start"))
    nodes = ["GPIO", "Таймер", "АЦП", "UART", "SPI", "…"]
    ny, nh = top + 8, 30
    for i, nm in enumerate(nodes):
        yy = ny + i * (nh + 8)
        f.append(rect(px, yy, 150, nh, fill=BG, stroke=POS, sw=1.4, rx=6))
        f.append(text(px + 75, yy + 20, nm, size=11, bold=True))
        f.append(text(px + 160, yy + 20, "база + регістри", size=9.5,
                      color=MUTED, anchor="start"))
    # сполучна дужка від периферійної смуги до списку вузлів
    f.append(line(bx + bw, bot - (bot - top) * 0.20, px - 8, ny + 4,
                  color=POS, sw=1.2, dash="4 3"))
    f.append(line(bx + bw, bot - 4, px - 8, ny + 5 * (nh + 8) + 4,
                  color=POS, sw=1.2, dash="4 3"))

    f.append(text(W / 2, bot + 30,
                  "Звернення за адресою з периферійної ділянки керує ЗАЛІЗОМ, а не пам'яттю.",
                  size=12, bold=True))
    f.append(text(W / 2, bot + 52,
                  "Це і є відображений у пам'ять ввід-вивід (memory-mapped IO).",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "address-map.svg"), W, H, *f)


# ── 2. Регістр зблизька: кожен біт заведений на лінію заліза ─────────────────
def fig_register_bits():
    W, H = 900, 430
    f = [text(W / 2, 30, "Регістр периферії — це не пам'ять, а панель керування з адресою",
              size=16, bold=True)]
    f.append(text(W / 2, 52, "кожен біт дротом заведений на конкретну лінію вузла",
                  size=12, color=MUTED, italic=True))

    bits = [0, 1, 0, 0, 1, 0, 1, 0]            # довільний приклад
    labels = [7, 6, 5, 4, 3, 2, 1, 0]
    cw = 60
    x0 = (W - cw * len(bits)) / 2
    y0 = 110
    f.append(text(x0 - 14, y0 + 22, "біт:", size=11, anchor="end", bold=True))
    f.append(bit_row(x0, y0, bits, w=cw, h=44, labels=labels))
    f.append(text(W / 2, y0 - 16, "один регістр = один рядок тригерів за фіксованою адресою",
                  size=11, color=INK))

    # підписи ліній заліза під кожним бітом
    wires = ["enable", "dir", "—", "—", "mode", "—", "ready", "—"]
    wy = y0 + 44 + 30
    for i, wname in enumerate(wires):
        cx = x0 + i * cw + cw / 2
        if wname == "—":
            continue
        is_in = wname == "ready"        # ready — вхід (знімаємо стан), решта — виходи
        col = NEG if is_in else FIELD
        if is_in:
            f.append(arrow(cx, wy + 70, cx, wy + 4, color=col))      # від заліза вгору
        else:
            f.append(arrow(cx, wy + 4, cx, wy + 70, color=col))      # до заліза вниз
        f.append(text(cx, wy + 88, wname, size=10.5, color=col, bold=True))

    f.append(text(x0, wy + 116, "→ виходи бітів керують лінією (enable, dir, mode…)",
                  size=10.5, color=FIELD, anchor="start", bold=True))
    f.append(text(x0, wy + 136, "← входи бітів знімають стан заліза (ready…)",
                  size=10.5, color=NEG, anchor="start", bold=True))
    f.append(text(W / 2, H - 24,
                  "«Записати в регістр» = смикнути за важелі; «прочитати» = зняти показання.",
                  size=12, bold=True))
    render(os.path.join(IMG, "register-bits.svg"), W, H, *f)


# ── 3. Три види регістрів: керування, стану, даних ──────────────────────────
def fig_register_kinds():
    W, H = 880, 370
    f = [text(W / 2, 30, "Три ролі регістрів і напрям руху", size=17, bold=True)]
    f.append(text(W / 2, 52, "налаштував → дочекався стану → перекинув дані",
                  size=12, color=MUTED, italic=True))

    # центральна «ядрова» колонка зліва, залізо праворуч
    core_x, hw_x = 90, 700
    f.append(rect(core_x - 60, 110, 120, 150, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=10))
    f.append(mtext(core_x, 180, ["ЯДРО", "(код)"], size=13, bold=True))
    f.append(rect(hw_x, 110, 120, 150, fill="#fdecea", stroke=POS, sw=1.6, rx=10))
    f.append(mtext(hw_x + 60, 180, ["ЗАЛІЗО", "(вузол)"], size=13, bold=True))

    rows = [
        ("Керування / config", "ядро ПИШЕ команду", FIELD, "down"),
        ("Стану / status",      "ядро ЧИТАЄ показання", NEG, "up"),
        ("Даних / data",        "корисний вантаж туди-сюди", INK, "both"),
    ]
    midx0, midw = 320, 240
    for i, (name, sub, col, direction) in enumerate(rows):
        y = 130 + i * 60
        f.append(rect(midx0, y, midw, 44, fill="#fbfcff", stroke=col, sw=1.6, rx=8))
        f.append(text(midx0 + midw / 2, y + 19, name, size=12, color=col, bold=True))
        f.append(text(midx0 + midw / 2, y + 36, sub, size=9.5, color=MUTED))
        yc = y + 22
        # стрілка ядро→регістр
        if direction in ("down", "both"):
            f.append(arrow(core_x + 60, yc, midx0 - 4, yc, color=col))
        if direction == "up":
            f.append(arrow(midx0 - 4, yc, core_x + 60, yc, color=col))
        # стрілка регістр→залізо
        if direction in ("down",):
            f.append(arrow(midx0 + midw + 4, yc, hw_x - 4, yc, color=col))
        if direction in ("up", "both"):
            f.append(arrow(hw_x - 4, yc, midx0 + midw + 4, yc, color=col))
        if direction == "both":
            f.append(arrow(midx0 + midw + 4, yc, hw_x - 4, yc, color=col))
            f.append(arrow(midx0 - 4, yc, core_x + 60, yc, color=col))

    f.append(text(W / 2, H - 22,
                  "Майже будь-яка робота з периферією — танець саме цих трьох.",
                  size=12, bold=True))
    render(os.path.join(IMG, "register-kinds.svg"), W, H, *f)


# ── 4. Чотири побітові операції над тим самим словом ────────────────────────
def fig_bit_ops():
    W, H = 920, 540
    f = [text(W / 2, 30, "Маски в дії: set / clear / toggle / test над тим самим словом",
              size=16, bold=True)]
    f.append(text(W / 2, 52, "чіпаємо лише біт 3 — сусіди (інші ніжки) цілі",
                  size=12, color=MUTED, italic=True))

    before = [0, 0, 1, 0, 0, 1, 0, 0]   # біти 7..0; одиниці на 5 і 2
    rows = [
        ("set",    "reg |= (1<<3)",   FIELD, [0, 0, 1, 0, 1, 1, 0, 0], "біт 3 → 1, решта цілі"),
        ("clear",  "reg &= ~(1<<3)",  POS,   [0, 0, 1, 0, 0, 1, 0, 0], "біт 3 → 0, решта цілі"),
        ("toggle", "reg ^= (1<<3)",   NEG,   [0, 0, 1, 0, 1, 1, 0, 0], "біт 3 перевернувся"),
        ("test",   "reg & (1<<3)",    INK,   None,                     "дізнались стан біта 3"),
    ]
    cw = 30
    y = 92
    for name, code, col, after, note in rows:
        f.append(rect(40, y, 250, 80, fill="#fbfcff", stroke=col, sw=1.6, rx=8))
        f.append(text(56, y + 30, name, size=14, color=col, bold=True, anchor="start"))
        f.append(text(56, y + 56, code, size=13, bold=True, anchor="start"))
        bx = 320
        f.append(text(bx, y + 12, "до:", size=9, color=MUTED, anchor="start"))
        f.append(bit_row(bx, y + 18, before, w=cw, h=30, hot=4))   # hot=біт 3 (index 4 від старшого)
        if after is not None:
            ax = bx + 8 * cw + 24
            f.append(arrow(bx + 8 * cw + 4, y + 33, ax - 6, y + 33, color=col))
            f.append(text(ax, y + 12, "після:", size=9, color=MUTED, anchor="start"))
            f.append(bit_row(ax, y + 18, after, w=cw, h=30, hot=4))
            f.append(text(ax + 8 * cw + 14, y + 38, note, size=10.5, anchor="start"))
        else:
            ax = bx + 8 * cw + 24
            f.append(arrow(bx + 8 * cw + 4, y + 33, ax - 6, y + 33, color=col))
            f.append(text(ax, y + 38, "→ біт 3 =", size=12, bold=True, anchor="start"))
            f.append(text(ax + 78, y + 38, "1", size=17, color=FIELD, bold=True, anchor="start"))
            f.append(text(ax + 100, y + 38, note, size=10.5, anchor="start"))
        y += 100

    f.append(text(W / 2, H - 56, "Сіро — недоторкані біти; червоним — той, що ми змінюємо.",
                  size=11, color=MUTED))
    f.append(text(W / 2, H - 30, "Це і є «читай-зміни-запиши» над одним бітом.",
                  size=12, bold=True))
    render(os.path.join(IMG, "bit-ops.svg"), W, H, *f)


# ── 5. Шлях від коду до світла: DIR → OUT → ніжка ───────────────────────────
def fig_gpio_blink():
    W, H = 920, 440
    f = [text(W / 2, 30, "Шлях від коду до світла: три записи в регістри GPIO", size=16, bold=True)]
    f.append(text(W / 2, 52, "світлодіод на ніжці 2 — жодної «магії», лише біти за адресами",
                  size=12, color=MUTED, italic=True))

    # три кроки-картки коду
    steps = [
        ("1", "DIR |= (1<<2)",  "ніжку 2 — на вихід",   FIELD),
        ("2", "OUT |= (1<<2)",  "виставити високий рівень", NEG),
        ("3", "напруга на ніжці", "світлодіод спалахує",  POS),
    ]
    bx, by, bw, bh, gap = 60, 96, 230, 70, 30
    for i, (n, code, sub, col) in enumerate(steps):
        x = bx + i * (bw + gap)
        f.append(rect(x, by, bw, bh, fill="#fbfcff", stroke=col, sw=1.6, rx=10))
        f.append(text(x + 22, by + 30, n + ")", size=14, color=col, bold=True, anchor="start"))
        f.append(text(x + bw / 2 + 8, by + 30, code, size=12.5, bold=True))
        f.append(text(x + bw / 2 + 8, by + 52, sub, size=10, color=MUTED))
        if i < 2:
            f.append(arrow(x + bw, by + bh / 2, x + bw + gap, by + bh / 2, color=INK))

    # регістр OUT із засвіченим бітом 2
    bits = [0, 0, 0, 0, 0, 1, 0, 0]
    labels = [7, 6, 5, 4, 3, 2, 1, 0]
    cw = 50
    rx0 = (W - cw * 8) / 2
    ry = 220
    f.append(text(W / 2, ry - 14, "регістр OUT після кроку 2:", size=11, bold=True))
    f.append(bit_row(rx0, ry, bits, w=cw, h=44, labels=labels, hot=5))

    # ніжка й світлодіод
    pin_x = rx0 + 5 * cw + cw / 2
    led_y = ry + 120
    f.append(line(pin_x, ry + 44, pin_x, led_y - 22, color=POS, sw=2.4))
    f.append(text(pin_x + 10, (ry + 44 + led_y) / 2, "ніжка 2 = HIGH", size=10.5,
                  color=POS, anchor="start", bold=True))
    f.append(circle(pin_x, led_y, 18, fill="#fff3b0", stroke=POS, sw=2.2))
    # промінчики
    for ang in range(0, 360, 45):
        import math
        a = math.radians(ang)
        f.append(line(pin_x + 22 * math.cos(a), led_y + 22 * math.sin(a),
                      pin_x + 32 * math.cos(a), led_y + 32 * math.sin(a),
                      color=POS, sw=2))
    f.append(text(pin_x, led_y + 56, "світлодіод горить", size=11, color=POS, bold=True))

    f.append(text(W / 2, H - 22,
                  "Щоб згасити — OUT &= ~(1<<2). Саме це робить digitalWrite(2, HIGH) усередині.",
                  size=12, bold=True))
    render(os.path.join(IMG, "gpio-blink.svg"), W, H, *f)


# ── 6. Карта регістрів із даташита: база, зсуви, біти ───────────────────────
def fig_register_map():
    W, H = 920, 440
    f = [text(W / 2, 30, "Карта регістрів вузла GPIO з даташита", size=17, bold=True)]
    f.append(text(W / 2, 52, "адреса регістра = базова адреса + зсув; біти — за розшифровкою",
                  size=12, color=MUTED, italic=True))

    # ліворуч: таблиця база+зсув+назва
    tx, ty, tw = 50, 96, 360
    f.append(text(tx, ty - 8, "база вузла: 0x4000_8000", size=12, bold=True, anchor="start"))
    rows = [("0x00", "DIR",   "напрям ніжок", FIELD),
            ("0x04", "CTRL",  "керування",    FIELD),
            ("0x08", "OUT",   "вихідні рівні", NEG),
            ("0x0C", "IN",    "вхідні рівні",  NEG),
            ("0x10", "STATUS", "стан / прапорці", POS)]
    rh = 46
    # шапка
    f.append(rect(tx, ty, tw, 28, fill="#eef1f5", stroke=LINE, sw=1.2, rx=4))
    f.append(text(tx + 50, ty + 19, "зсув", size=10.5, bold=True))
    f.append(text(tx + 150, ty + 19, "регістр", size=10.5, bold=True))
    f.append(text(tx + 290, ty + 19, "роль", size=10.5, bold=True))
    for i, (off, name, role, col) in enumerate(rows):
        y = ty + 28 + i * rh
        f.append(rect(tx, y, tw, rh, fill=BG, stroke=MUTED, sw=1.0, rx=2))
        f.append(text(tx + 50, y + 28, off, size=12, bold=True))
        f.append(text(tx + 150, y + 28, name, size=12, color=col, bold=True))
        f.append(text(tx + 290, y + 28, role, size=10, color=MUTED))

    # праворуч: побітова розшифровка одного регістра (CTRL)
    dx = 520
    f.append(text(dx, ty - 8, "розшифровка CTRL (0x04):", size=12, bold=True, anchor="start"))
    cw = 44
    labels = [7, 6, 5, 4, 3, 2, 1, 0]
    meaning = ["—", "—", "EN", "—", "—", "—", "MODE", "—"]
    by = ty + 18
    f.append(bit_row(dx, by, [0] * 8, w=cw, h=40, labels=labels))
    for i, m in enumerate(meaning):
        if m == "—":
            continue
        cx = dx + i * cw + cw / 2
        f.append(text(cx, by + 66, m, size=10, color=INK, bold=True))
        f.append(line(cx, by + 40, cx, by + 54, color=INK, sw=1.2))
    f.append(text(dx, by + 100, "біт 5 EN — дозвіл вузла", size=10.5, anchor="start"))
    f.append(text(dx, by + 120, "біт 1 MODE — режим", size=10.5, anchor="start"))

    # приклад обчислення адреси
    f.append(rect(dx, by + 140, 350, 70, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=8))
    f.append(text(dx + 16, by + 166, "адреса CTRL = 0x4000_8000 + 0x04", size=11,
                  anchor="start", bold=True))
    f.append(text(dx + 16, by + 192, "            = 0x4000_8004", size=12,
                  color=FIELD, anchor="start", bold=True))

    f.append(text(W / 2, H - 20,
                  "Уміти читати таку таблицю — і є вся «таємниця» спілкування з периферією.",
                  size=12, bold=True))
    render(os.path.join(IMG, "register-map.svg"), W, H, *f)


# ── (вставка) RMW не атомарний, а SET-регістр — атомарний ───────────────────
def fig_rmw_race():
    W, H = 920, 430
    f = [text(W / 2, 30, "Чому read-modify-write небезпечний, а SET-регістр — ні",
              size=17, bold=True)]
    f.append(text(W / 2, 52, "переривання між читанням і записом — і твій запис затре його зміну",
                  size=12, color=MUTED, italic=True))

    labels = [3, 2, 1, 0]
    cw = 30

    # ── ліва панель: RMW (небезпечно) ──
    f.append(rect(40, 76, 420, 320, fill="#fffafa", stroke=POS, sw=2, rx=12))
    f.append(text(250, 102, "RMW:  reg |= (1<<0)  — НЕ атомарно", size=12, color=POS, bold=True))
    lx = 150
    f.append(text(60, 134, "1. main ЧИТАЄ reg → 0000", size=10.5, anchor="start", bold=True))
    f.append(bit_row(lx, 146, [0, 0, 0, 0], w=cw, h=26, labels=labels))
    f.append(text(60, 212, "2. ISR встряє: SET біт3", size=10.5, anchor="start", bold=True))
    f.append(bit_row(lx, 224, [1, 0, 0, 0], w=cw, h=26, labels=labels, hot=0))
    f.append(text(60, 290, "3. main ПИШЕ (старе | біт0)", size=10.5, anchor="start", bold=True))
    f.append(bit_row(lx, 302, [0, 0, 0, 1], w=cw, h=26, labels=labels, hot=3))
    f.append(text(250, 378, "біт3 від ISR — затерто", size=11, color=POS, bold=True))

    # ── права панель: SET-регістр (атомарно) ──
    f.append(rect(480, 76, 400, 320, fill="#fbfdfb", stroke=FIELD, sw=2, rx=12))
    f.append(text(680, 102, "SET-регістр:  SET = (1<<n)  — атомарно", size=11.5, color=FIELD, bold=True))
    rx = 580
    f.append(text(500, 148, "main: SET = біт0  → 0001", size=10.5, anchor="start", bold=True))
    f.append(bit_row(rx, 160, [0, 0, 0, 1], w=cw, h=26, labels=labels, hot=3))
    f.append(text(500, 240, "ISR:  SET = біт3  → 1001", size=10.5, anchor="start", bold=True))
    f.append(bit_row(rx, 252, [1, 0, 0, 1], w=cw, h=26, labels=labels, hot=0))
    f.append(text(680, 378, "обидва біти збережено", size=11, color=FIELD, bold=True))
    render(os.path.join(IMG, "rmw-race.svg"), W, H, *f)


# ── (вставка) Картка способів доступу до бітів регістра ──────────────────────
def fig_reg_access_methods():
    W, H = 900, 430
    f = [text(W / 2, 30, "Способи дотягтися до бітів регістра", size=17, bold=True)]
    f.append(text(W / 2, 52, "RMW зручний, але стережися гонки; SET/CLR-регістри атомарні",
                  size=12, color=MUTED, italic=True))

    # шапка таблиці
    f.append(text(70, 100, "дія", size=11, anchor="start", bold=True))
    f.append(text(330, 100, "ідіома C", size=11, anchor="start", bold=True))
    f.append(text(710, 100, "тип", size=11, anchor="start", bold=True))
    f.append(line(50, 110, 850, 110, color="#d8dde3", sw=1.4))

    rows = [
        ("встановити біт",          "reg |= (1<<n)",                    "RMW",            "#caa24a", "#fbf6ea"),
        ("скинути біт",             "reg &= ~(1<<n)",                   "RMW",            "#caa24a", "#fbf6ea"),
        ("перемкнути біт",          "reg ^= (1<<n)",                    "RMW",            "#caa24a", "#fbf6ea"),
        ("записати поле",           "reg = (reg & ~mask) | (val<<shift)", "RMW",          "#caa24a", "#fbf6ea"),
        ("атомарно встановити",     "SET_REG = (1<<n)",                 "без читання",    FIELD,     "#eef6ef"),
        ("атомарно скинути",        "CLR_REG = (1<<n)",                 "без читання",    FIELD,     "#eef6ef"),
        ("скинути прапорець статусу", "STATUS = (1<<n)",                "write-1-to-clear", NEG,     "#e9eefb"),
    ]
    y, rh = 122, 38
    for act, idiom, kind, col, fill in rows:
        f.append(rect(50, y, 800, rh - 4, fill=fill, stroke=col, sw=1.2, rx=6))
        f.append(text(70, y + 24, act, size=10.8, anchor="start"))
        f.append(text(330, y + 24, idiom, size=11, color=col, anchor="start", bold=True))
        f.append(text(710, y + 24, kind, size=10, color=col, anchor="start", bold=True))
        y += rh
    render(os.path.join(IMG, "reg-access-methods.svg"), W, H, *f)


if __name__ == "__main__":
    # фігури теми
    fig_address_map()
    fig_register_bits()
    fig_register_kinds()
    fig_bit_ops()
    fig_gpio_blink()
    fig_register_map()
    # фігури вставки proj-reg-access
    fig_rmw_race()
    fig_reg_access_methods()
    print("OK: figures written to", IMG)
