# -*- coding: utf-8 -*-
"""Фігури до теми «Кадр UART».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Демонстраційний байт: 0xB5 = 1011 0101.
# LSB-first → на дроті D0..D7 = 1,0,1,0,1,1,0,1 (п'ять одиниць, непарно).
BYTE = 0xB5
BITS_LSB = [(BYTE >> i) & 1 for i in range(8)]   # D0..D7
ONES = sum(BITS_LSB)                              # 5
PAR_EVEN = ONES & 1                               # 1 (щоб разом стало парно)

HI = 150   # рівень «1» (мітка)
LO = 206   # рівень «0» (пропуск)


def _waveform(f, x0, cells, bw, baseline_lab=True):
    """Малює прямокутну хвилю за списком cells=[(label, value, color, sub)].
    Повертає список центрів кожної комірки."""
    centers = []
    x = x0
    prev = HI
    for i, (lab, val, col, sub) in enumerate(cells):
        y = HI if val == 1 else LO
        # вертикальний перепад на межі комірки
        if y != prev:
            f.append(line(x, prev, x, y, color=INK, sw=2.6))
        # горизонтальний рівень комірки
        f.append(line(x, y, x + bw, y, color=INK, sw=2.6))
        cx = x + bw / 2
        centers.append(cx)
        if lab:
            f.append(text(cx, LO + 26, lab, size=11, color=col, bold=True))
        if sub is not None:
            yy = HI - 10 if val == 1 else LO + 42
            f.append(text(cx, yy, str(sub), size=11, color=MUTED))
        prev = y
        x += bw
    # хвіст у спокій
    if prev != HI:
        f.append(line(x, prev, x, HI, color=INK, sw=2.6))
    f.append(line(x, HI, x + bw, HI, color=INK, sw=2.6))
    if baseline_lab:
        f.append(text(x0 - 12, HI + 4, "1", size=11, color=MUTED, anchor="end"))
        f.append(text(x0 - 12, LO + 4, "0", size=11, color=MUTED, anchor="end"))
    return centers, x + bw


# ── 1. Повний кадр 8N1 (even) для байта 0xB5: спокій → старт → дані → P → стоп ─
def fig_frame():
    W, H = 880, 380
    f = [text(W / 2, 30, "Один кадр UART: спокій, старт, вісім біт даних (молодший першим), парність, стоп",
              size=15, bold=True)]

    x0, bw = 130, 56
    cells = [("спокій", 1, MUTED, None), ("СТАРТ", 0, POS, None)]
    for i, b in enumerate(BITS_LSB):
        cells.append(("D%d" % i, b, INK, b))
    cells.append(("P", PAR_EVEN, NEG, PAR_EVEN))
    cells.append(("СТОП", 1, FIELD, None))
    centers, xend = _waveform(f, x0, cells, bw)

    # підпис рівнів праворуч від хвилі
    f.append(text(x0 - 12, HI - 14, "мітка", size=9.5, color=MUTED, anchor="end"))
    f.append(text(x0 - 12, LO + 20, "пропуск", size=9.5, color=MUTED, anchor="end"))

    # перепад «1→0» на старті
    sx = x0 + bw            # межа спокій|старт
    f.append(line(sx, HI - 34, sx, LO + 8, color=POS, sw=1.2, dash="3,3"))
    f.append(text(sx, HI - 40, "перепад 1→0 будить приймач", size=10, color=POS, bold=True))

    # дужка під полем даних
    d0c, d7c = centers[2], centers[9]
    by = 296
    f.append(line(d0c, by, d7c, by, color=MUTED, sw=1.4))
    f.append(line(d0c, by - 6, d0c, by, color=MUTED, sw=1.4))
    f.append(line(d7c, by - 6, d7c, by, color=MUTED, sw=1.4))
    f.append(text((d0c + d7c) / 2, by + 16, "8 біт даних — молодший (D0) першим", size=11.5, color=INK, bold=True))

    b, _, _ = textbox(W / 2, 350,
                      "байт 0xB5, формат 8E1 (8 даних, парна парність, 1 стоп); поза кадром лінія у «1»",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "frame.svg"), W, H, *f)


# ── 2. LSB-first: запис байта дзеркальний до порядку на дроті ─────────────────
def fig_lsb_first():
    W, H = 820, 360
    f = [text(W / 2, 30, "У пам'яті старший біт ліворуч — а в лінію байт іде молодшим уперед",
              size=15, bold=True)]

    bits_msb = [(BYTE >> i) & 1 for i in range(7, -1, -1)]   # D7..D0, як пишуть
    # ── рядок «як пишуть» ──
    ym = 110
    f.append(text(W / 2, ym - 30, "Як байт пишуть (0xB5)", size=12.5, bold=True, color=INK))
    bx, bw = 250, 40
    for i, b in enumerate(bits_msb):
        idx = 7 - i
        col = POS if b else NEG
        f.append(rect(bx + i * bw, ym, bw - 6, 40, fill="#f4f6f8", stroke=col, sw=1.6))
        f.append(text(bx + i * bw + (bw - 6) / 2, ym + 26, str(b), size=15, bold=True, color=col))
        f.append(text(bx + i * bw + (bw - 6) / 2, ym - 8, "D%d" % idx, size=9.5, color=MUTED))
    f.append(text(bx - 12, ym + 26, "MSB→", size=10, color=MUTED, anchor="end"))
    f.append(text(bx + 8 * bw + 4, ym + 26, "←LSB", size=10, color=MUTED, anchor="start"))

    # стрілка «перевертається»
    f.append(text(W / 2, 196, "на дроті порядок дзеркальний", size=11, color=FIELD, italic=True))
    f.append(arrow(W / 2 - 70, 206, W / 2 + 70, 206, color=FIELD, sw=1.8))

    # ── рядок «як іде на дроті» ──
    yw = 250
    f.append(text(W / 2, yw - 12, "Як байт іде в лінію (першим — D0)", size=12.5, bold=True, color=INK))
    for i, b in enumerate(BITS_LSB):
        col = POS if b else NEG
        f.append(rect(bx + i * bw, yw, bw - 6, 40, fill="#f4f6f8", stroke=col, sw=1.6))
        f.append(text(bx + i * bw + (bw - 6) / 2, yw + 26, str(b), size=15, bold=True, color=col))
        f.append(text(bx + i * bw + (bw - 6) / 2, yw + 56, "D%d" % i, size=9.5, color=MUTED))
    f.append(text(bx - 12, yw + 26, "перший", size=10, color=MUTED, anchor="end"))
    f.append(text(bx + 8 * bw + 4, yw + 26, "останній", size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "lsb-first.svg"), W, H, *f)


# ── 3. Запис «8N1» і споріднені формати ──────────────────────────────────────
def fig_format():
    W, H = 760, 360
    f = [text(W / 2, 30, "Код формату стискає три параметри кадру в кілька символів",
              size=15, bold=True)]

    # розкладка «8N1»
    cx = W / 2
    f.append(text(cx, 92, "8 N 1", size=40, bold=True, color=INK))
    # три виноски
    items = [
        (cx - 86, POS, "8", "біт даних"),
        (cx, NEG, "N", "парність: none (немає)"),
        (cx + 86, FIELD, "1", "стоп-біт"),
    ]
    for x, col, big, lab in items:
        f.append(line(x, 104, x, 134, color=col, sw=1.6))
        b, _, _ = textbox(x, 152, lab, size=10.5, fill="#f4f6f8", stroke=col)
        f.append(b)

    # таблиця споріднених форматів
    rows = [
        ("8N1", "8 даних · без парності · 1 стоп", "типовий за замовчуванням"),
        ("7E1", "7 даних · парна парність · 1 стоп", "класичний ASCII-текст"),
        ("8E1", "8 даних · парна парність · 1 стоп", "коли треба контроль помилок"),
        ("8N2", "8 даних · без парності · 2 стопи", "трохи більший запас між байтами"),
    ]
    ty = 206
    f.append(line(70, ty, W - 70, ty, color="#d6dde6", sw=1.2))
    for i, (code, expand, note) in enumerate(rows):
        y = ty + 24 + i * 30
        f.append(text(96, y, code, size=13, bold=True, color=INK, anchor="start"))
        f.append(text(190, y, expand, size=11, color=INK, anchor="start"))
        f.append(text(W - 96, y, note, size=10.5, color=MUTED, anchor="end"))

    b, _, _ = textbox(W / 2, 346,
                      "повний опис лінії — «швидкість + формат», як-от «115200 8N1»",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "format.svg"), W, H, *f)


# ── 4. Як добирають біт парності ──────────────────────────────────────────────
def fig_parity():
    W, H = 780, 330
    f = [text(W / 2, 30, "Біт парності добирають так, щоб загальна кількість одиниць стала рівною за правилом",
              size=14, bold=True)]

    # дані 0xB5 → 5 одиниць
    bx, bw = 150, 44
    yd = 96
    f.append(text(bx - 14, yd + 26, "дані", size=11, color=MUTED, anchor="end"))
    for i, b in enumerate(BITS_LSB):
        col = POS if b else NEG
        f.append(rect(bx + i * bw, yd, bw - 6, 40, fill="#f4f6f8", stroke=col, sw=1.6))
        f.append(text(bx + i * bw + (bw - 6) / 2, yd + 26, str(b), size=15, bold=True, color=col))
    f.append(text(bx + 8 * bw + 18, yd + 26, "→ одиниць: %d (непарно)" % ONES,
                  size=12, color=INK, anchor="start", bold=True))

    # дві гілки
    yb = 196
    # парна
    f.append(rect(90, yb, 300, 96, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(240, yb + 24, "Парна (even)", size=12.5, bold=True, color=FIELD))
    f.append(text(240, yb + 48, "P = 1  →  разом 6 одиниць (парно)", size=11.5, color=INK))
    f.append(text(240, yb + 72, "P = XOR усіх біт даних", size=10.5, color=MUTED, italic=True))
    # непарна
    f.append(rect(W - 390, yb, 300, 96, fill="#fbeee6", stroke=POS, sw=1.6, rx=8))
    f.append(text(W - 240, yb + 24, "Непарна (odd)", size=12.5, bold=True, color=POS))
    f.append(text(W - 240, yb + 48, "P = 0  →  лишилось 5 одиниць (непарно)", size=11.5, color=INK))
    f.append(text(W - 240, yb + 72, "доповнення до парної", size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "parity.svg"), W, H, *f)


# ── 5. Межа парності: ловить непарне число збоїв, пропускає парне ─────────────
def fig_parity_limits():
    W, H = 820, 340
    f = [text(W / 2, 30, "Один біт парності бачить непарне число перевернутих біт, але пропускає парне",
              size=14, bold=True)]

    cw = 240
    xs = [40, 290, 540]
    titles = ["Без помилок", "Перевернувся 1 біт", "Перевернулись 2 біти"]
    cols = [FIELD, FIELD, POS]
    verdict = ["звірка сходиться", "виявлено", "ПРОПУЩЕНО"]
    # стан: дані+P, скільки одиниць, чи парно
    states = [
        ("1·0·1·0·1·1·0·1  P=1", "одиниць 6 — парно", True),
        ("1·0·1·0·1·1·0·0  P=1", "одиниць 5 — непарно", True),
        ("1·0·1·0·1·1·1·0  P=1", "одиниць 6 — парно", False),
    ]
    for i, x in enumerate(xs):
        ok = (i != 2)
        col = cols[i]
        f.append(rect(x, 58, cw, 230, fill=("#eef6ef" if ok or i == 1 else "#fbeee6"),
                      stroke=col, sw=1.8, rx=10))
        f.append(text(x + cw / 2, 84, titles[i], size=12.5, bold=True, color=col))
        f.append(text(x + cw / 2, 130, states[i][0], size=12, color=INK))
        f.append(text(x + cw / 2, 158, states[i][1], size=11, color=MUTED))
        # вердикт
        mark = "✓" if states[i][2] == (i != 2) else "✗"
        # для випадку 2 (пропущено) сигнал помилки НЕ підняв, хоча біти биті
        if i == 2:
            f.append(text(x + cw / 2, 206, "перевірка каже «все добре»", size=11, color=POS, italic=True))
            f.append(text(x + cw / 2, 246, "помилку ПРОПУЩЕНО", size=13, bold=True, color=POS))
        elif i == 1:
            f.append(text(x + cw / 2, 206, "парність не та → прапорець", size=11, color=FIELD, italic=True))
            f.append(text(x + cw / 2, 246, "помилку виявлено", size=13, bold=True, color=FIELD))
        else:
            f.append(text(x + cw / 2, 206, "парність як домовлено", size=11, color=FIELD, italic=True))
            f.append(text(x + cw / 2, 246, "кадр чистий", size=13, bold=True, color=FIELD))

    render(os.path.join(IMG, "parity-limits.svg"), W, H, *f)


# ── 6. Стоп-біт між кадрами підряд ────────────────────────────────────────────
def fig_stop():
    W, H = 860, 360
    f = [text(W / 2, 28, "Стоп повертає лінію у «1», тож старт наступного кадру — знову чіткий перепад униз",
              size=14, bold=True)]

    # верх: два кадри з 1 стоп-бітом (спрощено: старт, кілька даних, стоп)
    def mini_frame(f, x0, bw, n_data, stop_cells, y_lab):
        cells = [("С", 0, POS, None)]
        pat = [1, 0, 1, 1, 0, 0, 1, 0][:n_data]
        for i in range(n_data):
            cells.append((None, pat[i], INK, None))
        for _ in range(stop_cells):
            cells.append(("Т", 1, FIELD, None))
        return cells

    bw = 30
    # рядок 1 — один стоп-біт між двома кадрами
    y1hi, y1lo = HI - 40, LO - 60   # підняти вище
    # намалюємо вручну спрощено через _waveform-подібний прохід на власних рівнях
    def wave(f, x0, cells, hi, lo):
        centers = []
        x = x0
        prev = hi
        for lab, val, col, sub in cells:
            y = hi if val == 1 else lo
            if y != prev:
                f.append(line(x, prev, x, y, color=INK, sw=2.4))
            f.append(line(x, y, x + bw, y, color=INK, sw=2.4))
            cx = x + bw / 2
            centers.append((cx, lab, col, val))
            prev = y
            x += bw
        if prev != hi:
            f.append(line(x, prev, x, hi, color=INK, sw=2.4))
        f.append(line(x, hi, x + bw, hi, color=INK, sw=2.4))
        return centers, x + bw

    # --- варіант з 1 стоп-бітом: кадр, кадр ---
    f.append(text(70, y1hi - 18, "Один стоп-біт", size=12, bold=True, color=INK, anchor="start"))
    cells = mini_frame(f, 0, bw, 8, 1, 0) + mini_frame(f, 0, bw, 8, 1, 0)
    cs, xend = wave(f, 120, cells, y1hi, y1lo)
    for cx, lab, col, val in cs:
        if lab == "С":
            f.append(text(cx, y1lo + 18, "ст", size=9.5, color=POS))
        elif lab == "Т":
            f.append(text(cx, y1hi - 6, "ст", size=9.5, color=FIELD))
    # позначити межу між кадрами
    boundary = cs[10][0]  # після першого кадру (1 старт+8 даних+1 стоп = 10), межа = початок наступного старту
    f.append(line(boundary, y1hi - 30, boundary, y1lo + 8, color=POS, sw=1.1, dash="3,3"))
    f.append(text(boundary, y1hi - 34, "новий старт видно", size=9.5, color=POS))

    # --- варіант з 2 стоп-бітами ---
    y2hi, y2lo = 280, 320
    f.append(text(70, y2hi - 18, "Два стоп-біти", size=12, bold=True, color=INK, anchor="start"))
    cells2 = mini_frame(f, 0, bw, 8, 2, 0)
    cs2, _ = wave(f, 120, cells2, y2hi, y2lo)
    # дужка над двома стопами
    stop_centers = [c for c in cs2 if c[1] == "Т"]
    if len(stop_centers) >= 2:
        a, b = stop_centers[-2][0], stop_centers[-1][0]
        f.append(line(a - bw / 2, y2hi - 12, b + bw / 2, y2hi - 12, color=MUTED, sw=1.3))
        f.append(text((a + b) / 2, y2hi - 18, "довший проміжок «1» = більший запас",
                      size=10, color=MUTED))

    render(os.path.join(IMG, "stop.svg"), W, H, *f)


# ── 7. Накладні витрати 8N1 і час байта ──────────────────────────────────────
def fig_overhead():
    W, H = 800, 360
    f = [text(W / 2, 30, "У 8N1 на 8 біт даних припадають 2 службові — корисні лише 80% часу лінії",
              size=14, bold=True)]

    # смуга кадру з 10 поділок
    bx, bw = 90, 60
    y = 80
    segs = [("СТАРТ", POS)] + [("D%d" % i, INK) for i in range(8)] + [("СТОП", FIELD)]
    for i, (lab, col) in enumerate(segs):
        fillc = "#fdecea" if col == POS else ("#eef6ef" if col == FIELD else "#f4f6f8")
        f.append(rect(bx + i * bw, y, bw - 4, 44, fill=fillc, stroke=col, sw=1.6))
        f.append(text(bx + i * bw + (bw - 4) / 2, y + 28, lab, size=10.5, bold=(col != INK), color=col))
    # дужки: службові 2, дані 8
    f.append(text(bx + bw / 2, y + 64, "службові: старт + стоп = 2 біти", size=10.5, color=MUTED, anchor="start"))
    f.append(text(bx + 5 * bw, y + 64, "корисні дані: 8 біт (80%)", size=11, color=INK, bold=True))

    # формула часу
    fy = 184
    f.append(rect(70, fy, W - 140, 130, fill=FILL, stroke=LINE, sw=1.4, rx=10))
    lines = [
        "час байта (8N1) = 10 біт / baud",
        "",
        "9600 8N1    : 10 / 9600   ≈ 1.042 мс  →  ≈ 960 байт/с",
        "115200 8N1  : 10 / 115200 ≈ 86.8 мкс  →  ≈ 11 520 байт/с",
    ]
    for i, ln in enumerate(lines):
        f.append(text(W / 2, fy + 30 + i * 26, ln, size=12.5 if i == 0 else 12,
                      color=INK, bold=(i == 0)))

    b, _, _ = textbox(W / 2, 340,
                      "«9600 бод» — це ≈960 байт/с, а не 9600: кожен байт тягне ще 2 службові біти",
                      size=11, fill="#fbeee6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "overhead.svg"), W, H, *f)


if __name__ == "__main__":
    fig_frame()
    fig_lsb_first()
    fig_format()
    fig_parity()
    fig_parity_limits()
    fig_stop()
    fig_overhead()
    print("OK: 7 figures ->", IMG)
