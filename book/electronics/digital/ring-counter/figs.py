# -*- coding: utf-8 -*-
"""Фігури до теми «Кільцевий і Johnson-лічильник».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def _ff(x, y, w, h, label, q):
    """Тригер: прямокутник, підпис, поточне значення Q (0/1), трикутник такту знизу-зліва."""
    on = (q == 1)
    out = rect(x, y, w, h, fill=("#eafaf0" if on else "#eef2f7"),
               stroke=(FIELD if on else LINE), sw=(2.0 if on else 1.5))
    out += text(x + w / 2, y + 20, label, size=13, bold=True)
    out += text(x + w / 2, y + h - 12, str(q), size=20, bold=True,
                color=(FIELD if on else MUTED))
    # трикутник «по фронту» на тактовому вході (ліва грань, низ)
    ty = y + h - 12
    out += ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" '
            'stroke="%s" stroke-width="1.3"/>' % (x, ty - 5, x + 9, ty, x, ty + 5, INK))
    return out


# ── 1. Кільцевий (straight): одна одиниця «крокує» по кільцю ─────────────────
def fig_ring_walk():
    W, H = 720, 430
    parts = []
    parts.append(text(W / 2, 26, "Кільцевий лічильник: одна одиниця крокує по кільцю", size=16, bold=True))

    ffw, ffh = 96, 66
    ys = 96
    xs = [60, 220, 380, 540]
    labels = ["Q0", "Q1", "Q2", "Q3"]
    bits = [1, 0, 0, 0]  # «гаряча» одиниця стоїть у Q0
    for x, lab, b in zip(xs, labels, bits):
        parts.append(_ff(x, ys, ffw, ffh, lab, b))

    # прямі зв'язки Q(n) → D(n+1)
    for i in range(3):
        x1 = xs[i] + ffw
        x2 = xs[i + 1]
        parts.append(arrow(x1, ys + ffh / 2, x2, ys + ffh / 2, color=INK, sw=1.8))

    # зворотний зв'язок: вихід останнього → вхід першого (пряме кільце)
    fy = ys + ffh + 46
    parts.append(line(xs[3] + ffw, ys + ffh / 2, xs[3] + ffw + 26, ys + ffh / 2, color=NEG, sw=2.0))
    parts.append(line(xs[3] + ffw + 26, ys + ffh / 2, xs[3] + ffw + 26, fy, color=NEG, sw=2.0))
    parts.append(line(xs[3] + ffw + 26, fy, xs[0] - 26, fy, color=NEG, sw=2.0))
    parts.append(line(xs[0] - 26, fy, xs[0] - 26, ys + ffh / 2, color=NEG, sw=2.0))
    parts.append(arrow(xs[0] - 26, ys + ffh / 2, xs[0], ys + ffh / 2, color=NEG, sw=2.0))
    parts.append(text(W / 2, fy + 16, "зворотний зв'язок: Q3 → D0 БЕЗ інверсії (пряме кільце)",
                      size=12, color=NEG, bold=True))

    # спільний такт
    clky = fy + 44
    parts.append(line(40, clky, W - 30, clky, color=POS, sw=2.4))
    parts.append(text(46, clky - 8, "ТАКТ — спільний для всіх", size=12, color=POS, anchor="start", bold=True))
    for x in xs:
        parts.append(line(x, ys + ffh - 10, x, clky, color=POS, sw=1.8))
        parts.append(circle(x, clky, 3.0, fill=POS, stroke=POS))

    # підсумок унизу: послідовність станів і скільки їх
    parts.append(text(W / 2, clky + 28,
                      "стани по такту:  1000 → 0100 → 0010 → 0001 → 1000 …   "
                      "(унітарний код: рівно одна одиниця; 4 тригери → лише 4 стани)",
                      size=11.5, color="#1e6b40"))
    return render(os.path.join(IMG, "ring-walk.svg"), W, H, *parts)


# ── 2. Johnson: одна інверсія у зв'язку → 2N станів, заповнення й спорожнення ─
def fig_johnson_cycle():
    W, H = 760, 470
    parts = []
    parts.append(text(W / 2, 26, "Johnson-лічильник: інвертований зв'язок дає 2N станів", size=16, bold=True))

    # схема зверху: 4 тригери, зворотний зв'язок з ІНВЕРСІЄЮ (Q̄3 → D0)
    ffw, ffh = 92, 58
    ys = 60
    xs = [60, 210, 360, 510]
    labels = ["Q0", "Q1", "Q2", "Q3"]
    bits = [1, 1, 0, 0]
    for x, lab, b in zip(xs, labels, bits):
        parts.append(_ff(x, ys, ffw, ffh, lab, b))
    for i in range(3):
        parts.append(arrow(xs[i] + ffw, ys + ffh / 2, xs[i + 1], ys + ffh / 2, color=INK, sw=1.8))
    # інвертор у зворотному зв'язку
    fy = ys + ffh + 34
    invx = xs[3] + ffw + 24
    parts.append(line(xs[3] + ffw, ys + ffh / 2, invx, ys + ffh / 2, color=POS, sw=2.0))
    # кружечок-інверсія
    parts.append(circle(invx + 8, ys + ffh / 2, 7, fill="#fdecea", stroke=POS, sw=2.0))
    parts.append(text(invx + 8, ys + ffh / 2 + 4, "¬", size=13, color=POS, bold=True))
    parts.append(line(invx + 15, ys + ffh / 2, invx + 30, ys + ffh / 2, color=POS, sw=2.0))
    parts.append(line(invx + 30, ys + ffh / 2, invx + 30, fy, color=POS, sw=2.0))
    parts.append(line(invx + 30, fy, xs[0] - 24, fy, color=POS, sw=2.0))
    parts.append(line(xs[0] - 24, fy, xs[0] - 24, ys + ffh / 2, color=POS, sw=2.0))
    parts.append(arrow(xs[0] - 24, ys + ffh / 2, xs[0], ys + ffh / 2, color=POS, sw=2.0))
    parts.append(text((invx + 30 + xs[0]) / 2, fy + 15,
                      "єдина відмінність від прямого кільця: Q3 повертається ІНВЕРТОВАНИМ  (Q̄3 → D0)",
                      size=11.5, color=POS, bold=True))

    # таблиця станів (заповнення нулями→одиницями, потім навпаки)
    tx, ty = 90, fy + 48
    parts.append(text(tx, ty - 6, "повний цикл 8 станів (4 тригери → 2·4 = 8):",
                      size=12.5, bold=True, anchor="start"))
    states = ["0000", "1000", "1100", "1110",
              "1111", "0111", "0011", "0001"]
    cell = 74
    y0 = ty + 16
    row_y = [y0, y0]
    # два рядки по 4 стани
    for k, s in enumerate(states):
        col = k % 4
        row = k // 4
        cx = tx + col * (cell + 24) + cell / 2
        cy = y0 + row * 70
        fill = "#eafaf0" if row == 0 else "#eef2f7"
        parts.append(rect(cx - cell / 2, cy, cell, 40, fill=fill, sw=1.4))
        # розфарбуємо кожен біт
        for j, ch in enumerate(s):
            bx = cx - cell / 2 + 10 + j * ((cell - 20) / 4) + ((cell - 20) / 8)
            parts.append(text(bx, cy + 26, ch, size=15, bold=True,
                              color=(FIELD if ch == "1" else MUTED)))
        if k < 7:
            # стрілка до наступного
            if col < 3:
                parts.append(arrow(cx + cell / 2, cy + 20, cx + cell / 2 + 22, cy + 20, color=INK, sw=1.5))
    # підписи фаз праворуч від двох рядків станів
    lx = tx + 4 * (cell + 24) + 4
    parts.append(mtext(lx, y0 + 12,
                       ["◀ заповнення", "одиницями"], size=10.5, color="#1e6b40", anchor="start"))
    parts.append(mtext(lx, y0 + 82,
                       ["◀ потім одиниці", "виходять"], size=10.5, color=MUTED, anchor="start"))

    parts.append(text(W / 2, H - 12,
                      "на КОЖНОМУ кроці міняється лише ОДИН біт — це код Грея, тому декодування без глітчів",
                      size=12, color="#1e6b40"))
    return render(os.path.join(IMG, "johnson-cycle.svg"), W, H, *parts)


# ── 3. Декодування Johnson: будь-який стан — одним 2-входовим вентилем ────────
def fig_johnson_decode():
    W, H = 720, 360
    parts = []
    parts.append(text(W / 2, 26, "Кожен стан Johnson декодується ОДНИМ вентилем на 2 входи", size=15.5, bold=True))

    # ліворуч — вихід лічильника (4 біти), праворуч — 8 декодованих виходів
    tx = 70
    parts.append(text(tx, 66, "виходи тригерів:", size=12.5, bold=True, anchor="start"))
    labels = ["Q0", "Q1", "Q2", "Q3"]
    ly0 = 90
    for i, lab in enumerate(labels):
        yy = ly0 + i * 34
        parts.append(circle(tx + 20, yy, 12, fill="#eef2f7", sw=1.4))
        parts.append(text(tx + 20, yy + 4, lab, size=11, bold=True))

    # приклад: стан «1100» декодується як Q1·Q̄2 → «крок №2»
    def andgate(cx, cy, r=16):
        s = ('<path d="M%.1f %.1f L%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f L%.1f %.1f z" '
             'fill="#fff" stroke="%s" stroke-width="1.6"/>'
             % (cx - r, cy - r, cx, cy - r, r, r, cx, cy + r, cx - r, cy + r, INK))
        s += text(cx - 3, cy + 5, "&", size=15, bold=True)
        return s

    gx = 360
    examples = [
        ("крок 1  (1000)", "Q0 · Q̄1", ly0 - 4),
        ("крок 2  (1100)", "Q1 · Q̄2", ly0 + 60),
        ("крок 4  (1111)", "Q3 · (усі 1)", ly0 + 120),
    ]
    for name, expr, gy in examples:
        parts.append(andgate(gx, gy))
        # два входи
        parts.append(line(gx - 40, gy - 8, gx - 16, gy - 8, color=NEG, sw=1.6))
        parts.append(line(gx - 40, gy + 8, gx - 16, gy + 8, color=NEG, sw=1.6))
        parts.append(text(gx - 44, gy - 4, expr, size=11.5, color=NEG, anchor="end", bold=True))
        # вихід
        parts.append(arrow(gx + 16, gy, gx + 120, gy, color=POS, sw=1.9))
        parts.append(text(gx + 126, gy + 4, name, size=11.5, color=POS, anchor="start", bold=True))

    # ключова рамка
    note, nw, nh = textbox(W / 2, H - 44,
                           "будь-який стан упізнають ДВА сусідні біти («межа» між зоною одиниць і зоною нулів)\n"
                           "→ вентиль на 2 входи, а не широке AND на всі розряди, як для двійкового лічильника",
                           size=11.5, fill="#eafaf0", stroke=FIELD, color="#1e6b40", pad=9)
    parts.append(note)
    return render(os.path.join(IMG, "johnson-decode.svg"), W, H, *parts)


# ── 4. Порівняння: пряме кільце vs Johnson vs двійковий ──────────────────────
def fig_compare():
    W, H = 760, 340
    parts = []
    parts.append(text(W / 2, 26, "Три способи лічити на N тригерах: чим платять і що виграють", size=15, bold=True))

    cols = [
        ("Пряме кільце", ["N станів", "унітарний код", "БЕЗ вентилів декоду",
                          "гріє N тригерів\nзаради N станів"], "#eef2f7", LINE),
        ("Johnson", ["2N станів", "код Грея (1 біт/крок)", "декод: 1 вентиль ×2 входи",
                     "удвічі щедріший\nза те саме залізо"], "#eafaf0", FIELD),
        ("Двійковий", ["2^N станів", "щільний двійковий код", "декод: широкі AND",
                       "максимум станів,\nале глітчі й ширші вентилі"], "#f7f0ea", "#c98a3a"),
    ]
    cw = 224
    gap = 14
    x0 = (W - (3 * cw + 2 * gap)) / 2
    y = 60
    ch = 240
    for i, (title, rows, fill, stroke) in enumerate(cols):
        cx = x0 + i * (cw + gap)
        parts.append(rect(cx, y, cw, ch, fill=fill, stroke=stroke, sw=1.8))
        parts.append(text(cx + cw / 2, y + 30, title, size=14.5, bold=True))
        parts.append(line(cx + 16, y + 44, cx + cw - 16, y + 44, color=stroke, sw=1.2))
        ry = y + 74
        for r in rows:
            parts.append(mtext(cx + cw / 2, ry, r, size=11.5, color=INK, lh=1.15))
            nlines = r.count("\n") + 1
            ry += 30 + (nlines - 1) * 16
    return render(os.path.join(IMG, "compare.svg"), W, H, *parts)


# ── 5. Історія: чому в добу ламп «перекрут» коштував удвічі дешевше ──────────
def fig_tubes_decade():
    """Декада (10 станів) на лампах: пряме кільце = 10 щаблів, Johnson = 5.
    Кожен щабель — це лампова комірка (≈2 тріоди). Отже вдвічі менше балонів."""
    W, H = 760, 400
    parts = []
    parts.append(text(W / 2, 26, "Декада (лічба до 10) у добу ламп: за що платив кожен щабель",
                      size=15, bold=True))

    def bank(x0, y0, n, fill, stroke, hot):
        """Ряд із n лампових комірок; hot — набір «увімкнених» (для наочності)."""
        s = ""
        cw, ch, gap = 40, 54, 8
        for i in range(n):
            cx = x0 + i * (cw + gap)
            on = i in hot
            s += rect(cx, y0, cw, ch, fill=(fill if on else "#eef2f7"),
                      stroke=(stroke if on else LINE), sw=(2.0 if on else 1.4))
            # дві «лампи» в комірці — два кружечки-балони
            s += circle(cx + cw / 2, y0 + 18, 6, fill=BG, stroke=(stroke if on else MUTED), sw=1.4)
            s += circle(cx + cw / 2, y0 + 36, 6, fill=BG, stroke=(stroke if on else MUTED), sw=1.4)
        return s, cw, gap

    # Пряме кільце: 10 щаблів
    parts.append(text(W / 2, 66, "Пряме кільце: 10 станів = 10 щаблів", size=13, bold=True, color=LINE))
    b, cw, gap = bank((W - (10 * 48 - 8)) / 2, 82, 10, "#eef2f7", LINE, set())
    parts.append(b)
    parts.append(mtext(W / 2, 158, ["10 комірок × ≈2 лампи = ≈20 ламп",
                                    "на ті самі 10 кроків"], size=12.5, color=INK, lh=1.2))

    # Johnson: 5 щаблів
    parts.append(text(W / 2, 218, "Johnson (перекручене кільце): 10 станів = 5 щаблів",
                      size=13, bold=True, color=FIELD))
    b2, _, _ = bank((W - (5 * 48 - 8)) / 2, 234, 5, "#eafaf0", FIELD, {0, 1, 2, 3, 4})
    parts.append(b2)
    parts.append(mtext(W / 2, 310, ["5 комірок × ≈2 лампи = ≈10 ламп",
                                    "— ті самі 10 кроків удвічі дешевше"], size=12.5,
                       color=INK, lh=1.2))

    body, bw, bh = textbox(W / 2, 358, "Один інвертор у петлі → удвічі менше балонів,\n"
                                       "менше тепла, менше того, що перегорить уночі",
                           size=12.5, pad=11, fill="#fbf6ea", stroke="#c98a3a", color=INK)
    parts.append(body)
    return render(os.path.join(IMG, "tubes-decade.svg"), W, H, *parts)


# ── 6. Що всередині корпусу: Johnson-ядро + вбудований дешифратор → 10 виходів ─
def fig_inside():
    W, H = 780, 440
    parts = []
    parts.append(text(W / 2, 26, "Що в корпусі: 5 тригерів у Johnson-кільці + вбудований дешифратор",
                      size=15, bold=True))

    # входи ліворуч
    ix = 44
    parts.append(text(ix, 78, "CLK", size=12, bold=True, color=POS, anchor="start"))
    parts.append(text(ix, 108, "CE", size=12, bold=True, color=NEG, anchor="start"))
    parts.append(text(ix, 138, "MR", size=12, bold=True, color=NEG, anchor="start"))

    # блок Johnson-ядра (5 тригерів)
    bx, by, bw, bh = 120, 66, 250, 96
    parts.append(rect(bx, by, bw, bh, fill="#eef2f7", stroke=LINE, sw=1.8))
    parts.append(text(bx + bw / 2, by + 22, "Johnson-кільце: 5 D-тригерів", size=12.5, bold=True))
    for k in range(5):
        cx = bx + 30 + k * 48
        parts.append(rect(cx - 15, by + 40, 30, 34, fill="#e6ecf5", sw=1.2))
        parts.append(text(cx, by + 62, "T%d" % k, size=11, bold=True))
        if k < 4:
            parts.append(arrow(cx + 15, by + 57, cx + 33, by + 57, color=INK, sw=1.4))
    # інвертор у зворотному зв'язку (дуга під блоком)
    fy = by + bh + 22
    parts.append(line(bx + bw - 18, by + bh, bx + bw - 18, fy, color=POS, sw=1.8))
    parts.append(line(bx + bw - 18, fy, bx + 30, fy, color=POS, sw=1.8))
    parts.append(circle(bx + 22, fy, 6, fill="#fdecea", stroke=POS, sw=1.8))
    parts.append(text(bx + 22, fy + 4, "¬", size=12, color=POS, bold=True))
    parts.append(line(bx + 16, fy, bx + 16, by + 57, color=POS, sw=1.8))
    parts.append(arrow(bx + 16, by + 57, bx + 30, by + 57, color=POS, sw=1.8))
    parts.append(text(bx + bw / 2, fy + 16, "інвертований зв'язок Q̄4 → T0 (перекручене кільце)",
                      size=10.5, color=POS))

    # входи заходять у блок
    parts.append(arrow(ix + 34, 74, bx, 74, color=POS, sw=1.6))
    parts.append(arrow(ix + 26, 104, bx, 104, color=NEG, sw=1.6))
    parts.append(arrow(ix + 30, 134, bx, 134, color=NEG, sw=1.6))

    # блок дешифратора
    dx, dy, dw, dh = 440, 66, 150, 96
    parts.append(rect(dx, dy, dw, dh, fill="#eafaf0", stroke=FIELD, sw=1.8))
    parts.append(mtext(dx + dw / 2, dy + 32,
                       ["вбудований", "дешифратор:", "10 вентилів AND", "по 2 входи"],
                       size=11, color="#1e6b40", lh=1.25, bold=True))
    # ядро → дешифратор (5 ліній)
    for k in range(5):
        yy = by + 30 + k * 12
        parts.append(line(bx + bw, yy, dx, yy, color=MUTED, sw=1.0))

    # 10 унітарних виходів праворуч від дешифратора
    ox = dx + dw
    for k in range(10):
        yy = dy + 8 + k * ((dh - 16) / 9.0)
        hot = (k == 3)
        col = FIELD if hot else MUTED
        parts.append(line(ox, yy, ox + 40, yy, color=col, sw=(2.2 if hot else 1.0)))
        parts.append(text(ox + 46, yy + 4, "Q%d" % k, size=10.5,
                          color=(FIELD if hot else INK), bold=hot, anchor="start"))
    parts.append(text(ox + 16, dy + dh + 22, "у високому — рівно ОДИН (тут Q3)", size=10.5,
                      color="#1e6b40", anchor="start"))

    # carry-out знизу з дешифратора
    parts.append(line(dx + dw / 2, dy + dh, dx + dw / 2, dy + dh + 42, color="#c98a3a", sw=1.8))
    parts.append(arrow(dx + dw / 2, dy + dh + 42, dx + dw + 24, dy + dh + 42, color="#c98a3a", sw=1.8))
    parts.append(text(dx + dw + 28, dy + dh + 46, "CO (÷10)", size=11, color="#c98a3a",
                      anchor="start", bold=True))

    # підсумкова рамка
    note, nw, nh = textbox(W / 2, H - 28,
                           "5 тригерів → 10 внутрішніх станів → вбудований 2-входовий дешифратор → 10 «крокових» виходів.\n"
                           "Зовні: даєш такт — по колу вмикається рівно один вихід, без жодної зовнішньої логіки.",
                           size=11, fill=FILL, stroke=LINE, color=INK, pad=9)
    parts.append(note)
    return render(os.path.join(IMG, "inside.svg"), W, H, *parts)


# ── 7. Типова розпіновка DIP-16: виходи Q ідуть НЕ по порядку ─────────────────
def fig_pinout():
    W, H = 640, 480
    parts = []
    parts.append(text(W / 2, 26, "Типова розпіновка DIP-16: виходи Q розкидані НЕ по порядку",
                      size=15, bold=True))

    # ліва (ніжки 1..8 згори вниз) і права (16..9 згори вниз) колонки
    left = [(1, "Q5"), (2, "Q1"), (3, "Q0"), (4, "Q2"),
            (5, "Q6"), (6, "Q7"), (7, "Q3"), (8, "GND")]
    right = [(16, "VDD"), (15, "MR"), (14, "CLK"), (13, "CE"),
             (12, "CO"), (11, "Q9"), (10, "Q4"), (9, "Q8")]

    bx, by, bw, bh = 230, 60, 180, 372
    parts.append(rect(bx, by, bw, bh, fill="#eef2f7", stroke=LINE, sw=1.8))
    # виїмка-ключ зверху
    parts.append(('<path d="M%.1f %.1f A14 14 0 0 1 %.1f %.1f" fill="#ffffff" '
                  'stroke="%s" stroke-width="1.8"/>' % (bx + bw / 2 - 14, by, bx + bw / 2 + 14, by, LINE)))
    parts.append(mtext(bx + bw / 2, by + 46,
                       ["десятковий", "Johnson-лічильник", "(клас «4017»)"],
                       size=12, bold=True, color=MUTED, lh=1.3))

    def color_of(name):
        if name in ("VDD", "GND"):
            return MUTED
        if name == "CLK":
            return POS
        if name in ("MR", "CE"):
            return NEG
        if name == "CO":
            return "#c98a3a"
        return FIELD  # виходи Q

    step = (bh - 44) / 7.0
    for i, (num, name) in enumerate(left):
        yy = by + 26 + i * step
        parts.append(line(bx - 26, yy, bx, yy, color=INK, sw=2.0))
        parts.append(circle(bx - 30, yy, 3, fill=INK, stroke=INK))
        parts.append(text(bx - 36, yy + 4, "%d" % num, size=10.5, color=MUTED, anchor="end"))
        parts.append(text(bx + 12, yy + 4, name, size=12.5, bold=True,
                          color=color_of(name), anchor="start"))
    for i, (num, name) in enumerate(right):
        yy = by + 26 + i * step
        parts.append(line(bx + bw, yy, bx + bw + 26, yy, color=INK, sw=2.0))
        parts.append(circle(bx + bw + 30, yy, 3, fill=INK, stroke=INK))
        parts.append(text(bx + bw + 36, yy + 4, "%d" % num, size=10.5, color=MUTED, anchor="start"))
        parts.append(text(bx + bw - 12, yy + 4, name, size=12.5, bold=True,
                          color=color_of(name), anchor="end"))

    # легенда ліворуч знизу
    lx = 34
    ly = H - 96
    parts.append(text(lx, ly - 8, "кольори:", size=11, bold=True, anchor="start"))
    legend = [("Q0..Q9 — десять декодованих виходів", FIELD),
              ("CLK — такт (рахунок по фронту 0→1)", POS),
              ("MR / CE — скид / стоп-такт", NEG),
              ("CO — перенос ÷10 для каскаду", "#c98a3a")]
    for i, (txt, col) in enumerate(legend):
        yy = ly + i * 18
        parts.append(rect(lx, yy - 9, 12, 12, fill=col, stroke=col, sw=1))
        parts.append(text(lx + 18, yy + 1, txt, size=10.5, color=INK, anchor="start"))

    parts.append(text(W - 26, ly + 24,
                      "Q0=3, Q1=2, Q2=4, Q3=7, Q4=10,", size=10, color=MUTED, anchor="end"))
    parts.append(text(W - 26, ly + 40,
                      "Q5=1, Q6=5, Q7=6, Q8=9, Q9=11", size=10, color=MUTED, anchor="end"))
    parts.append(text(W - 26, ly + 62,
                      "веди дроти за ПІДПИСОМ Qn, не за номером ніжки", size=10, color=POS,
                      anchor="end", bold=True))
    return render(os.path.join(IMG, "pinout.svg"), W, H, *parts)


# ── 8. Три типові ввімкнення: вогник, подільник ÷N через MR, каскад через CO ──
def fig_uses():
    W, H = 780, 470
    parts = []
    parts.append(text(W / 2, 26, "Три типові ввімкнення класу", size=15.5, bold=True))

    def chip(x, y, w=92, h=120, label="4017"):
        s = rect(x, y, w, h, fill="#eef2f7", stroke=LINE, sw=1.6)
        s += ('<path d="M%.1f %.1f A9 9 0 0 1 %.1f %.1f" fill="#fff" stroke="%s" '
              'stroke-width="1.5"/>' % (x + w / 2 - 9, y, x + w / 2 + 9, y, LINE))
        s += text(x + w / 2, y + h / 2 + 4, label, size=11.5, bold=True, color=MUTED)
        return s

    # --- (а) біжучий вогник ---
    ax = 44
    parts.append(text(ax + 46, 60, "а) біжучий вогник", size=12.5, bold=True, anchor="middle"))
    parts.append(chip(ax, 82))
    parts.append(text(ax - 6, 120, "CLK", size=9.5, color=POS, anchor="end", bold=True))
    parts.append(arrow(ax - 30, 120, ax, 120, color=POS, sw=1.6))
    parts.append(text(ax - 34, 150, "такт", size=9, color=POS, anchor="end"))
    # 10 світлодіодів праворуч
    for k in range(10):
        yy = 88 + k * 10.6
        col = FIELD if k == 2 else MUTED
        parts.append(line(ax + 92, yy, ax + 110, yy, color=col, sw=(2.0 if k == 2 else 1.0)))
        parts.append(('<path d="M%.1f %.1f l6 -4 l0 8 z" fill="%s"/>'
                      % (ax + 110, yy, col)))
    parts.append(mtext(ax + 120, 150, ["10 LED —", "вогник", "«біжить»"], size=10,
                       color="#1e6b40", anchor="start", lh=1.25))

    # --- (б) подільник ÷N: Q_N → MR ---
    bx = 320
    parts.append(text(bx + 46, 60, "б) подільник ÷N", size=12.5, bold=True, anchor="middle"))
    parts.append(chip(bx, 82))
    parts.append(text(bx - 6, 118, "CLK", size=9.5, color=POS, anchor="end", bold=True))
    parts.append(arrow(bx - 30, 118, bx, 118, color=POS, sw=1.6))
    parts.append(text(bx + 98, 104, "Q_N", size=9.5, color=FIELD, anchor="start", bold=True))
    parts.append(line(bx + 92, 104, bx + 132, 104, color=FIELD, sw=1.6))
    parts.append(line(bx + 132, 104, bx + 132, 258, color=FIELD, sw=1.6))
    parts.append(line(bx + 132, 258, bx - 42, 258, color=FIELD, sw=1.6))
    parts.append(line(bx - 42, 258, bx - 42, 150, color=FIELD, sw=1.6))
    parts.append(arrow(bx - 42, 150, bx, 150, color=FIELD, sw=1.6))
    parts.append(text(bx - 6, 150, "MR", size=9.5, color=NEG, anchor="end", bold=True))
    note, nw, nh = textbox(bx + 46, 320,
                           "вихід Q_N заведено в MR:\nдійшовши до N, лічильник\nсам скидається в 0 → ділить на N",
                           size=9.5, fill="#eafaf0", stroke=FIELD, color="#1e6b40", pad=7)
    parts.append(note)

    # --- (в) каскад через CO ---
    cx = 592
    parts.append(text(cx + 40, 60, "в) каскад через CO", size=12.5, bold=True, anchor="middle"))
    parts.append(chip(cx, 82, label="одиниці"))
    parts.append(chip(cx + 10, 258, label="десятки"))
    parts.append(text(cx - 6, 118, "CLK", size=9.5, color=POS, anchor="end", bold=True))
    parts.append(arrow(cx - 28, 118, cx, 118, color=POS, sw=1.6))
    parts.append(text(cx + 98, 150, "CO", size=9.5, color="#c98a3a", anchor="start", bold=True))
    parts.append(line(cx + 92, 150, cx + 124, 150, color="#c98a3a", sw=1.6))
    parts.append(line(cx + 124, 150, cx + 124, 300, color="#c98a3a", sw=1.6))
    parts.append(arrow(cx + 124, 300, cx + 10, 300, color="#c98a3a", sw=1.6))
    parts.append(text(cx + 4, 300, "CLK", size=9, color="#c98a3a", anchor="end", bold=True))
    note2, nw2, nh2 = textbox(cx + 40, 410,
                              "CO дає 1 імпульс\nна 10 тактів (÷10):\nдругий чип рахує десятки",
                              size=9.5, fill="#f7f0ea", stroke="#c98a3a", color="#8a5a20", pad=7)
    parts.append(note2)

    return render(os.path.join(IMG, "uses.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_ring_walk()
    fig_johnson_cycle()
    fig_johnson_decode()
    fig_compare()
    fig_tubes_decade()
    fig_inside()
    fig_pinout()
    fig_uses()
    print("OK: 8 SVG ->", IMG)
