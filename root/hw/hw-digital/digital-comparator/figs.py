# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_three_outputs():
    """Компаратор як чорна скринька: два числа -> три взаємовиключні виходи."""
    W, H = 800, 330
    parts = []
    # вхідні числа
    parts.append(fitbox(40, 80, 130, 56, "A\n4 біти", size=15, fill="#eaf0fd", stroke=NEG, bold=True))
    parts.append(fitbox(40, 200, 130, 56, "B\n4 біти", size=15, fill="#eaf0fd", stroke=NEG, bold=True))
    # тіло компаратора
    body, bw, bh = textbox(360, 168, "Цифровий\nкомпаратор", size=17, pad=22,
                           fill=FILL, stroke=LINE, bold=True, min_w=210)
    parts.append(body)
    # дроти всередину
    parts.append(arrow(170, 108, 254, 140))
    parts.append(arrow(170, 228, 254, 196))
    bx = 360 + bw / 2
    # три виходи
    rows = [(96, "A > B", "більше", POS),
            (168, "A = B", "рівні", FIELD),
            (240, "A < B", "менше", NEG)]
    for y, lab, sub, col in rows:
        parts.append(arrow(bx, 168, bx + 120, y))
        parts.append(fitbox(bx + 120, y - 22, 168, 44, lab + "   (" + sub + ")",
                            size=14, fill="#ffffff", stroke=col, bold=True, color=col))
    parts.append(text(W / 2, 300, "будь-якої миті рівно один вихід = 1", size=13, color=MUTED, italic=True))
    return render(os.path.join(OUT, 'three-outputs.svg'), W, H, *parts)


def fig_one_bit():
    """Однобітовий компаратор: таблиця істинності + три рівняння."""
    W, H = 720, 340
    parts = []
    parts.append(text(W / 2, 30, "Однобітовий компаратор: a проти b", size=17, bold=True))
    # таблиця істинності
    tx, ty, cw, rh = 70, 60, 70, 34
    hdr = ["a", "b", "a>b", "a=b", "a<b"]
    for i, h in enumerate(hdr):
        col = INK if i < 2 else (POS if i == 2 else (FIELD if i == 3 else NEG))
        parts.append(rect(tx + i * cw, ty, cw, rh, fill="#eef2f7", stroke=LINE))
        parts.append(text(tx + i * cw + cw / 2, ty + 23, h, size=14, bold=True, color=col))
    data = [("0", "0", "0", "1", "0"),
            ("0", "1", "0", "0", "1"),
            ("1", "0", "1", "0", "0"),
            ("1", "1", "0", "1", "0")]
    for r, row in enumerate(data):
        yy = ty + (r + 1) * rh
        for i, v in enumerate(row):
            hot = (i >= 2 and v == "1")
            col = (POS if i == 2 else FIELD if i == 3 else NEG) if hot else INK
            parts.append(rect(tx + i * cw, yy, cw, rh, fill="#ffffff" if not hot else "#f3faf5", stroke=LINE, sw=1))
            parts.append(text(tx + i * cw + cw / 2, yy + 22, v, size=14, bold=hot, color=col))
    # рівняння праворуч
    ex = 470
    parts.append(fitbox(ex, 75, 220, 50, "a>b = a · b̅", size=16, fill="#fdecea", stroke=POS, bold=True, color=POS))
    parts.append(fitbox(ex, 145, 220, 50, "a=b = a ⊙ b", size=16, fill="#f3faf5", stroke=FIELD, bold=True, color=FIELD))
    parts.append(fitbox(ex, 215, 220, 50, "a<b = a̅ · b", size=16, fill="#eaf0fd", stroke=NEG, bold=True, color=NEG))
    parts.append(text(ex + 110, 300, "⊙ — XNOR (рівність)", size=12, color=MUTED, italic=True))
    return render(os.path.join(OUT, 'one-bit.svg'), W, H, *parts)


def fig_msb_scan():
    """Порівняння чисел: скан від старшого біта, перша відмінність вирішує."""
    W, H = 720, 300
    parts = []
    parts.append(text(W / 2, 30, "A = 1011  проти  B = 1001 — скан від старшого біта", size=16, bold=True))
    bits_a = "1011"
    bits_b = "1001"
    x0, y_a, y_b, cw = 130, 90, 150, 90
    labels = ["біт 3", "біт 2", "біт 1", "біт 0"]
    parts.append(text(70, y_a + 6, "A:", size=15, bold=True, anchor="middle"))
    parts.append(text(70, y_b + 6, "B:", size=15, bold=True, anchor="middle"))
    decide = 1  # індекс першої відмінності (зліва направо): біт1
    for i in range(4):
        cx = x0 + i * cw
        same = bits_a[i] == bits_b[i]
        if i < decide:
            colbox = "#eef2f7"; note = "рівні →\nдивимось далі"; ncol = MUTED
        elif i == decide:
            colbox = "#fdecea"; note = "перша різниця:\n1 > 0 ⇒ A > B"; ncol = POS
        else:
            colbox = "#f4f6f8"; note = "(уже неважливо)"; ncol = MUTED
        parts.append(rect(cx - 28, y_a - 24, 56, 44, fill=colbox, stroke=LINE))
        parts.append(text(cx, y_a + 6, bits_a[i], size=20, bold=True))
        parts.append(rect(cx - 28, y_b - 24, 56, 44, fill=colbox, stroke=LINE))
        parts.append(text(cx, y_b + 6, bits_b[i], size=20, bold=True))
        parts.append(text(cx, y_a - 34, labels[i], size=11, color=MUTED))
        if i == decide:
            parts.append(fitbox(cx - 70, 200, 140, 56, note, size=12, fill="#ffffff", stroke=POS, bold=True, color=POS))
        else:
            parts.append(fitbox(cx - 60, 205, 120, 46, note, size=11, fill="#ffffff", stroke=LINE, color=ncol))
    parts.append(arrow(x0 - 40, 70, x0 + 3 * cw + 40, 70, color=MUTED))
    parts.append(text(x0 + 3 * cw + 40, 60, "напрям сканування", size=11, color=MUTED, anchor="end", italic=True))
    return render(os.path.join(OUT, 'msb-scan.svg'), W, H, *parts)


def fig_cascade():
    """Каскад: ланцюг однобітових ступенів від старшого до молодшого."""
    W, H = 810, 270
    parts = []
    parts.append(text(W / 2, 28, "Каскад: рішення тече від старшого біта до молодшого", size=16, bold=True))
    sx, sw_box, gap, y = 70, 120, 35, 120
    stages = ["біт 3\n(старший)", "біт 2", "біт 1", "біт 0\n(молодший)"]
    cx_prev = None
    for i, lab in enumerate(stages):
        x = sx + i * (sw_box + gap)
        parts.append(fitbox(x, y, sw_box, 60, lab, size=12, fill=FILL, stroke=LINE, bold=True))
        # вертикальні входи aᵢ,bᵢ зверху
        parts.append(text(x + sw_box / 2, y - 12, "aᵢ  bᵢ", size=12, color=NEG))
        parts.append(arrow(x + sw_box / 2, y - 6, x + sw_box / 2, y, color=NEG, sw=1.5))
        if cx_prev is not None:
            parts.append(arrow(cx_prev, y + 30, x, y + 30))
        cx_prev = x + sw_box
    # підпис зв'язку
    parts.append(text(W / 2, y + 78, "кожен ступінь: «якщо старші рівні — вирішую я; інакше пропускаю готове рішення далі»",
                      size=12, color=MUTED, italic=True))
    # фінальний вихід
    parts.append(arrow(cx_prev, y + 30, cx_prev + 30, y + 30))
    parts.append(fitbox(cx_prev + 30, y, 90, 60, "A>B\nA=B\nA<B", size=12, fill="#ffffff", stroke=FIELD, bold=True, color=FIELD))
    return render(os.path.join(OUT, 'cascade.svg'), W, H, *parts)


def fig_window():
    """Застосування в ОЦС: віконний компаратор над відліком АЦП."""
    W, H = 720, 320
    parts = []
    parts.append(text(W / 2, 28, "Віконний компаратор над відліком (код АЦП x)", size=16, bold=True))
    # вісь значень
    ax0, ax1, ayy = 90, 630, 150
    parts.append(line(ax0, ayy, ax1, ayy, color=INK, sw=2))
    lo, hi = 250, 470  # позиції меж на осі
    # зони
    parts.append(rect(ax0, ayy - 26, lo - ax0, 26, fill="#eaf0fd", stroke="none", rx=0))
    parts.append(rect(lo, ayy - 26, hi - lo, 26, fill="#eafaf0", stroke="none", rx=0))
    parts.append(rect(hi, ayy - 26, ax1 - hi, 26, fill="#fdecea", stroke="none", rx=0))
    parts.append(line(lo, ayy - 34, lo, ayy + 10, color=NEG, sw=2, dash="4 3"))
    parts.append(line(hi, ayy - 34, hi, ayy + 10, color=POS, sw=2, dash="4 3"))
    parts.append(text(lo, ayy - 42, "нижня межа L", size=12, color=NEG, bold=True))
    parts.append(text(hi, ayy - 42, "верхня межа H", size=12, color=POS, bold=True))
    parts.append(text((ax0 + lo) / 2, ayy - 8, "x < L", size=13, color=NEG, bold=True))
    parts.append(text((lo + hi) / 2, ayy - 8, "L ≤ x ≤ H : у вікні", size=13, color=FIELD, bold=True))
    parts.append(text((hi + ax1) / 2, ayy - 8, "x > H", size=13, color=POS, bold=True))
    # відлік-точка
    px = 360
    parts.append(circle(px, ayy, 6, fill=FIELD, stroke=INK, sw=1.5))
    parts.append(arrow(px, ayy + 60, px, ayy + 12, color=INK))
    parts.append(text(px, ayy + 78, "поточний відлік x", size=12, bold=True))
    parts.append(fitbox(ax0, ayy + 110, ax1 - ax0, 56,
                        "два магнітудні порівняння (x≥L  і  x≤H) + AND  →  один біт «у межах»",
                        size=13, fill=FILL, stroke=LINE, bold=True))
    return render(os.path.join(OUT, 'window.svg'), W, H, *parts)


# ── Фігури для вставки comp-magnitude-comparator.md ──────────────────────────

def fig_ic_block():
    """Блок-схема мікросхеми-компаратора: дані + каскадні входи -> три виходи."""
    W, H = 820, 380
    parts = []
    parts.append(text(W / 2, 28, "Магнітудний компаратор-мікросхема: що заходить і що виходить", size=16, bold=True))
    # тіло чипа
    bx, by, bw, bh = 300, 70, 220, 250
    parts.append(rect(bx, by, bw, bh, fill=FILL, stroke=LINE, sw=2))
    parts.append(text(bx + bw / 2, by + 34, "4-бітовий", size=15, bold=True))
    parts.append(text(bx + bw / 2, by + 56, "магнітудний", size=15, bold=True))
    parts.append(text(bx + bw / 2, by + 78, "компаратор", size=15, bold=True))
    # дані A, B зліва
    parts.append(fitbox(70, 100, 150, 42, "A  (a₃a₂a₁a₀)", size=14, fill="#eaf0fd", stroke=NEG, bold=True, color=NEG))
    parts.append(fitbox(70, 158, 150, 42, "B  (b₃b₂b₁b₀)", size=14, fill="#eaf0fd", stroke=NEG, bold=True, color=NEG))
    parts.append(arrow(220, 121, bx, 121, color=NEG))
    parts.append(arrow(220, 179, bx, 179, color=NEG))
    # каскадні входи знизу зліва
    parts.append(fitbox(60, 250, 176, 60, "каскадні входи\nIₐ﹥ᵦ  Iₐ₌ᵦ  Iₐ﹤ᵦ\n(від молодшого чипа)", size=11, fill="#fff7e6", stroke="#b8860b", bold=True, color="#8a6d00"))
    parts.append(arrow(230, 280, bx, 255, color="#b8860b"))
    # три виходи справа
    outs = [(120, "Qₐ﹥ᵦ", "A > B", POS),
            (179, "Qₐ₌ᵦ", "A = B", FIELD),
            (238, "Qₐ﹤ᵦ", "A < B", NEG)]
    for yy, lab, sub, col in outs:
        parts.append(arrow(bx + bw, yy, bx + bw + 60, yy, color=col))
        parts.append(fitbox(bx + bw + 60, yy - 20, 150, 40, lab + "  " + sub, size=13, fill="#ffffff", stroke=col, bold=True, color=col))
    # каскадний вихід теж є — це ті самі три виходи, підпис
    parts.append(text(W / 2, by + bh + 34, "три виходи = і результат, і «каскадний вихід» у старший чип",
                      size=12, color=MUTED, italic=True))
    return render(os.path.join(OUT, 'ic-block.svg'), W, H, *parts)


def fig_pinout():
    """Типова розпіновка DIP-16 (сімейство 74x85)."""
    W, H = 720, 540
    parts = []
    parts.append(text(W / 2, 28, "Типова розпіновка DIP-16 (клас 74x85)", size=16, bold=True))
    # корпус
    cx, top, cw, rowh = 360, 56, 150, 44
    n = 8
    ch = n * rowh
    parts.append(rect(cx - cw / 2, top, cw, ch, fill="#f0f0f0", stroke=INK, sw=2))
    # виїмка зверху
    parts.append(path_notch(cx, top))
    parts.append(text(cx, top + 24, "74x85", size=14, bold=True, color=MUTED))
    # ліві піни 1..8, праві 16..9
    left = [("1", "B3", NEG), ("2", "Iₐ﹤ᵦ", "#8a6d00"), ("3", "Iₐ₌ᵦ", "#8a6d00"),
            ("4", "Iₐ﹥ᵦ", "#8a6d00"), ("5", "Qₐ﹥ᵦ", POS), ("6", "Qₐ₌ᵦ", FIELD),
            ("7", "Qₐ﹤ᵦ", NEG), ("8", "GND", INK)]
    right = [("16", "VCC", POS), ("15", "A3", NEG), ("14", "B2", NEG),
             ("13", "A2", NEG), ("12", "A1", NEG), ("11", "B1", NEG),
             ("10", "A0", NEG), ("9", "B0", NEG)]
    for i, (pn, nm, col) in enumerate(left):
        yy = top + rowh * i + rowh / 2
        parts.append(line(cx - cw / 2 - 26, yy, cx - cw / 2, yy, color=INK, sw=2))
        parts.append(circle(cx - cw / 2 - 34, yy, 3, fill=INK, stroke=INK))
        parts.append(text(cx - cw / 2 - 44, yy + 5, pn, size=12, color=MUTED, anchor="end"))
        parts.append(text(cx - cw / 2 + 12, yy + 5, nm, size=13, bold=True, color=col, anchor="start"))
    for i, (pn, nm, col) in enumerate(right):
        yy = top + rowh * i + rowh / 2
        parts.append(line(cx + cw / 2, yy, cx + cw / 2 + 26, yy, color=INK, sw=2))
        parts.append(circle(cx + cw / 2 + 34, yy, 3, fill=INK, stroke=INK))
        parts.append(text(cx + cw / 2 + 44, yy + 5, pn, size=12, color=MUTED, anchor="start"))
        parts.append(text(cx + cw / 2 - 12, yy + 5, nm, size=13, bold=True, color=col, anchor="end"))
    # легенда
    ly = top + ch + 40
    parts.append(fitbox(70, ly, 175, 34, "A, B — дані (сині)", size=12, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))
    parts.append(fitbox(265, ly, 175, 34, "I — каскадні входи", size=12, fill="#fff7e6", stroke="#b8860b", color="#8a6d00", bold=True))
    parts.append(fitbox(460, ly, 190, 34, "Q — виходи A>B/=/<", size=12, fill="#ffffff", stroke=FIELD, color=FIELD, bold=True))
    parts.append(text(W / 2, ly + 60, "нумерація проти годинникової від крапки-виїмки; VCC=16, GND=8",
                      size=11, color=MUTED, italic=True))
    return render(os.path.join(OUT, 'pinout.svg'), W, H, *parts)


def path_notch(cx, top):
    """Півколо-виїмка зверху корпусу."""
    return ('<path d="M %.1f %.1f a 12 12 0 0 0 24 0" fill="#ffffff" stroke="%s" stroke-width="2"/>'
            % (cx - 12, top, INK))


def fig_chain():
    """Каскад двох чипів у 8-бітове порівняння: виходи молодшого -> входи старшого."""
    W, H = 840, 340
    parts = []
    parts.append(text(W / 2, 28, "Два 4-бітові чипи → одне 8-бітове порівняння", size=16, bold=True))
    # старший чип (ліворуч) — біти 7..4
    hx, hy, bw, bh = 90, 80, 210, 150
    parts.append(rect(hx, hy, bw, bh, fill=FILL, stroke=LINE, sw=2))
    parts.append(text(hx + bw / 2, hy + 26, "СТАРШИЙ чип", size=13, bold=True))
    parts.append(text(hx + bw / 2, hy + 46, "біти 7…4", size=12, color=MUTED))
    parts.append(text(hx + bw / 2, hy + 92, "Iₐ₌ᵦ ← вихід", size=12, color="#8a6d00", bold=True))
    parts.append(text(hx + bw / 2, hy + 110, "молодшого", size=12, color="#8a6d00"))
    # молодший чип (праворуч) — біти 3..0
    lx = 540
    parts.append(rect(lx, hy, bw, bh, fill=FILL, stroke=LINE, sw=2))
    parts.append(text(lx + bw / 2, hy + 26, "МОЛОДШИЙ чип", size=13, bold=True))
    parts.append(text(lx + bw / 2, hy + 46, "біти 3…0", size=12, color=MUTED))
    parts.append(text(lx + bw / 2, hy + 92, "Iₐ₌ᵦ = 1 (старт)", size=12, color=FIELD, bold=True))
    parts.append(text(lx + bw / 2, hy + 110, "Iₐ﹥ᵦ = Iₐ﹤ᵦ = 0", size=12, color=MUTED))
    # зв'язок: виходи молодшого -> каскадні входи старшого
    parts.append(arrow(lx, hy + bh - 20, hx + bw, hy + bh - 20, color="#b8860b", sw=2.2))
    parts.append(text((hx + bw + lx) / 2, hy + bh + 6, "3 виходи молодшого →", size=12, color="#8a6d00", bold=True))
    parts.append(text((hx + bw + lx) / 2, hy + bh + 24, "3 каскадні входи старшого", size=12, color="#8a6d00"))
    # спільний вихід зі старшого
    parts.append(arrow(hx, hy + bh / 2, hx - 40, hy + bh / 2, color=FIELD))
    parts.append(text(hx - 44, hy + bh / 2 - 26, "результат", size=12, color=FIELD, bold=True, anchor="end"))
    parts.append(text(hx - 44, hy + bh / 2 - 8, "усіх 8 біт", size=12, color=FIELD, anchor="end"))
    parts.append(text(W / 2, hy + bh + 60, "старший чип має останнє слово; за рівних старших біт віддає голос ланцюга молодшого",
                      size=12, color=MUTED, italic=True))
    return render(os.path.join(OUT, 'chain.svg'), W, H, *parts)


def fig_tie_rule():
    """Правило каскадних входів у поодинокого/наймолодшого чипа."""
    W, H = 720, 320
    parts = []
    parts.append(text(W / 2, 28, "Один чип: каскадні входи треба виставити правильно", size=16, bold=True))
    # три входи
    rows = [("Iₐ₌ᵦ", "1  (HIGH)", FIELD, "старт «поки що рівні»"),
            ("Iₐ﹥ᵦ", "0  (LOW)", MUTED, "нема попереднього «більше»"),
            ("Iₐ﹤ᵦ", "0  (LOW)", MUTED, "нема попереднього «менше»")]
    y0 = 80
    for i, (nm, val, col, note) in enumerate(rows):
        yy = y0 + i * 60
        parts.append(fitbox(90, yy, 130, 44, nm, size=16, fill="#fff7e6", stroke="#b8860b", bold=True, color="#8a6d00"))
        parts.append(fitbox(250, yy, 150, 44, val, size=15, fill="#ffffff", stroke=col, bold=True, color=col))
        parts.append(text(430, yy + 28, note, size=12, color=MUTED, anchor="start"))
    parts.append(fitbox(90, y0 + 3 * 60 + 6, 540, 42,
                        "«усі три в нуль» — ПАСТКА: тоді за рівних A і B вихід A=B лишається 0",
                        size=12.5, fill="#fdecea", stroke=POS, bold=True, color=POS))
    return render(os.path.join(OUT, 'tie-rule.svg'), W, H, *parts)


# ── Фігури для вставки proj-comparator-patterns.md ───────────────────────────

def fig_signedness():
    """Пастка знаку: ті самі біти — різне відношення до порогу."""
    W, H = 760, 300
    parts = []
    parts.append(text(W / 2, 30, "Ті самі 16 бітів — знакове чи беззнакове?", size=16, bold=True))
    bits = "1111111111111011"
    x0, cw, yb = 90, 36, 96
    parts.append(text(70, yb + 6, "біти:", size=13, bold=True, anchor="end"))
    for i, ch in enumerate(bits):
        cx = x0 + i * cw
        parts.append(rect(cx - 15, yb - 20, 30, 40, fill="#eef2f7", stroke=LINE, sw=1))
        parts.append(text(cx, yb + 6, ch, size=15, bold=True))
    xr = x0 + len(bits) * cw / 2
    parts.append(fitbox(120, 165, 240, 62,
                        "int16_t  →  −5\nменше за поріг 10",
                        size=14, fill="#eaf0fd", stroke=NEG, bold=True, color=NEG))
    parts.append(fitbox(420, 165, 240, 62,
                        "uint16_t →  65531\nбільше за поріг 10",
                        size=14, fill="#fdecea", stroke=POS, bold=True, color=POS))
    parts.append(arrow(xr - 120, yb + 22, 240, 163, color=NEG, sw=1.5))
    parts.append(arrow(xr + 120, yb + 22, 540, 163, color=POS, sw=1.5))
    parts.append(text(W / 2, 262, "змішав знакове й беззнакове — компілятор мовчки бере беззнакове",
                      size=12, color=MUTED, italic=True))
    return render(os.path.join(OUT, 'signedness.svg'), W, H, *parts)


def fig_endian_memcmp():
    """Чому memcmp бреше на little-endian: перший байт у памʼяті — не старший."""
    W, H = 780, 330
    parts = []
    parts.append(text(W / 2, 30, "memcmp над little-endian числами: молодший байт першим", size=15, bold=True))
    parts.append(text(310, 78, "байт 0 (молодший)", size=10, color=MUTED))
    parts.append(text(440, 78, "байт 1 (старший)", size=10, color=MUTED))

    def row(y, name, val, b0, b1, col):
        parts.append(text(70, y + 6, name, size=14, bold=True, anchor="end", color=col))
        parts.append(text(160, y + 6, "= " + val, size=13, color=INK, anchor="middle"))
        for k, bb in enumerate((b0, b1)):
            bx = 250 + k * 130
            hot = (k == 0)
            parts.append(rect(bx, y - 20, 120, 40,
                              fill="#fdecea" if hot else "#eef2f7",
                              stroke=col if hot else LINE, sw=2 if hot else 1))
            parts.append(text(bx + 60, y + 6, bb, size=14, bold=True))

    row(110, "A", "0x0100 = 256", "0x00", "0x01", NEG)
    row(175, "B", "0x0002 = 2", "0x02", "0x00", POS)
    parts.append(arrow(310, 200, 310, 232, color=INK))
    parts.append(fitbox(110, 238, 400, 46,
                        "memcmp: 0x00 < 0x02  ⇒  «A менше»",
                        size=14, fill="#fff4f4", stroke=POS, bold=True, color=POS))
    parts.append(fitbox(540, 238, 200, 46,
                        "а насправді\n256 > 2 !",
                        size=13, fill="#f4f6f8", stroke=LINE, bold=True))
    parts.append(text(W / 2, 312, "магнітудно чесний лише для big-endian (старший байт першим)",
                      size=12, color=MUTED, italic=True))
    return render(os.path.join(OUT, 'endian-memcmp.svg'), W, H, *parts)


def fig_hysteresis():
    """Брязкіт на одному порозі проти чистого перемикання з гістерезисом."""
    import math
    W, H = 780, 430
    parts = []
    parts.append(text(W / 2, 26, "Один поріг брязкає — два пороги (гістерезис) не брязкають", size=15, bold=True))
    x0, x1 = 100, 700
    N = 120

    def sig(i):
        base = 0.5 + 0.28 * math.sin(math.pi * i / N)
        noise = 0.055 * math.sin(i * 1.9) * math.cos(i * 0.7)
        return base + noise

    def X(i):
        return x0 + (x1 - x0) * i / (N - 1)

    def Y(v, ay, ah):
        return ay + ah * (1 - v)

    # верхня панель: один поріг
    ay, ah = 66, 118
    th = 0.62
    parts.append(line(x0, Y(th, ay, ah), x1, Y(th, ay, ah), color=POS, sw=1.5, dash="5 3"))
    parts.append(text(x1 + 6, Y(th, ay, ah) + 4, "TH", size=12, color=POS, bold=True, anchor="start"))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' %
                 (" ".join("%.1f,%.1f" % (X(i), Y(sig(i), ay, ah)) for i in range(N)), INK))
    oy = ay + ah + 24
    seg = [(X(i), oy - 22 * (1 if sig(i) > th else 0)) for i in range(N)]
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.9"/>' %
                 (" ".join("%.1f,%.1f" % p for p in seg), POS))
    parts.append(text(x0 - 8, oy - 10, "вихід", size=11, color=MUTED, anchor="end"))
    parts.append(text(W / 2, oy + 8, "деренчить: багато перемикань на одну подію",
                      size=12, color=POS, italic=True))

    # нижня панель: два пороги
    by = 254
    thi, tlo = 0.66, 0.58
    parts.append(rect(x0, Y(thi, by, ah), x1 - x0, Y(tlo, by, ah) - Y(thi, by, ah),
                      fill="#eafaf0", stroke="none", rx=0))
    parts.append(line(x0, Y(thi, by, ah), x1, Y(thi, by, ah), color=POS, sw=1.5, dash="5 3"))
    parts.append(line(x0, Y(tlo, by, ah), x1, Y(tlo, by, ah), color=NEG, sw=1.5, dash="5 3"))
    parts.append(text(x1 + 6, Y(thi, by, ah) + 4, "TH_HI", size=11, color=POS, bold=True, anchor="start"))
    parts.append(text(x1 + 6, Y(tlo, by, ah) + 4, "TH_LO", size=11, color=NEG, bold=True, anchor="start"))
    parts.append(text((x0 + x1) / 2, Y((thi + tlo) / 2, by, ah) + 4, "мертва зона",
                      size=11, color=FIELD, bold=True))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' %
                 (" ".join("%.1f,%.1f" % (X(i), Y(sig(i), by, ah)) for i in range(N)), INK))
    oy2 = by + ah + 24
    state = 0
    seg2 = []
    for i in range(N):
        v = sig(i)
        if state == 0 and v > thi:
            state = 1
        elif state == 1 and v < tlo:
            state = 0
        seg2.append((X(i), oy2 - 22 * state))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.9"/>' %
                 (" ".join("%.1f,%.1f" % p for p in seg2), FIELD))
    parts.append(text(x0 - 8, oy2 - 10, "вихід", size=11, color=MUTED, anchor="end"))
    parts.append(text(W / 2, oy2 + 8, "одне чисте перемикання на подію",
                      size=12, color=FIELD, italic=True))
    return render(os.path.join(OUT, 'hysteresis.svg'), W, H, *parts)


if __name__ == "__main__":
    fig_three_outputs()
    fig_one_bit()
    fig_msb_scan()
    fig_cascade()
    fig_window()
    fig_ic_block()
    fig_pinout()
    fig_chain()
    fig_tie_rule()
    fig_signedness()
    fig_endian_memcmp()
    fig_hysteresis()
    print("ok")
