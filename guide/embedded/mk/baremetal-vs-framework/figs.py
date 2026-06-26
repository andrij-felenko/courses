# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODEBG = "#0f1b14"   # темне тло код-плашки
CODEHW = "#7fe0a0"   # код голого заліза (зелений на темному)
CODEFW = "#9ec5ff"   # код фреймворку (блакитний на темному)


def codebox(cx, cy, code, sub, accent, w=300):
    """Плашка з рядком коду (моноширинно) і дрібним підписом під нею."""
    h = 46
    out = rect(cx - w / 2, cy - h / 2, w, h, fill=CODEBG, stroke="#0a120d", sw=1.4, rx=8)
    out += ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', monospace" '
            'font-size="13" fill="%s" text-anchor="middle" font-weight="700">%s</text>'
            % (cx, cy + 5, accent, esc(code)))
    out += text(cx, cy + h / 2 + 16, sub, size=10, color=MUTED)
    return out


# ── 1. two-ways: та сама дія — дві дороги до регістра ─────────────────────────
def fig_two_ways():
    W, H = 760, 300
    p = []
    # ліворуч — дві дороги
    yb, yf = 96, 220
    p.append(text(180, 70, "Голе залізо", size=14, color=POS, bold=True))
    p.append(codebox(180, yb, "GPIO_OUT |= (1 << 2);", "ви самі складаєте запис", CODEHW, w=290))
    p.append(text(180, 196, "Фреймворк", size=14, color=FIELD, bold=True))
    p.append(codebox(180, yf, "digitalWrite(2, HIGH);", "запис складе бібліотека", CODEFW, w=290))

    # праворуч — спільний підсумок: запис у регістр
    rx, ry = 600, 158
    box, bw, bh = textbox(rx, ry, "той самий\nЗАПИС У РЕГІСТР\n→ ніжка перемикається",
                          size=12, bold=True, color=NEG, fill="#eef3ff", stroke=NEG, sw=2, pad=14)
    p.append(line(180 + 145, yb, rx - bw / 2, ry - 16, color=INK, sw=2.0))
    p.append(line(180 + 145, yf, rx - bw / 2, ry + 16, color=INK, sw=2.0))
    p.append(box)

    render(os.path.join(OUT, "two-ways.svg"), W, H, *p,
           title="Та сама дія — дві дороги до регістра")


# ── 2. layers: шари абстракції ────────────────────────────────────────────────
def fig_layers():
    W, H = 720, 320
    p = []
    cx = W / 2
    layers = [
        ("ваш код", "digitalWrite(2, HIGH)", "#eafaf0", INK),
        ("фреймворк", "Arduino / ESP-IDF", "#eef3ff", NEG),
        ("регістри", "GPIO_OUT |= (1<<2)", "#f6f4ec", INK),
        ("залізо", "кремній, ніжка чипа", "#efefef", MUTED),
    ]
    bw, bh = 360, 50
    y = 64
    gap = 18
    centers = []
    for name, sub, fill, col in layers:
        b = rect(cx - bw / 2, y, bw, bh, fill=fill, stroke=INK, sw=1.6, rx=8)
        b += text(cx - bw / 2 + 14, y + bh / 2 + 5, name, size=13, color=col, anchor="start", bold=True)
        b += ('<text x="%.1f" y="%.1f" font-family="Consolas, monospace" font-size="11" '
              'fill="%s" text-anchor="end">%s</text>' % (cx + bw / 2 - 14, y + bh / 2 + 4, MUTED, esc(sub)))
        p.append(b)
        centers.append(y + bh)
        y += bh + gap
    # стрілки вниз між шарами
    for i in range(len(layers) - 1):
        ya = centers[i]
        p.append(arrow(cx, ya + 1, cx, ya + gap - 1, color=INK, sw=1.7))
    # підпис: голе залізо = прибрати середній шар
    p.append(text(cx + bw / 2 + 18, 64 + bh + gap + bh / 2,
                  "голе залізо =\nприбрати цей шар", size=10, color=POS, anchor="start"))
    render(os.path.join(OUT, "layers.svg"), W, H, *p,
           title="Шари абстракції: кожен ховає складність нижчого")


# ── 3. buys-costs: ваги абстракції ────────────────────────────────────────────
def fig_buys_costs():
    W, H = 720, 320
    p = []
    # коромисло
    cx = W / 2
    top = 70
    p.append(line(cx, top, cx, top + 26, color=INK, sw=3))          # стійка
    p.append(line(120, top, W - 120, top, color=INK, sw=3))         # балка
    p.append(circle(cx, top, 5, fill=INK, stroke=INK))

    def pan(px, title, items, col, fill):
        out = [line(px, top, px, top + 36, color=INK, sw=1.5)]
        lines = [title] + items
        b, bw, bh = textbox(px, top + 36 + 70, "\n".join(lines), size=11,
                            color=col, fill=fill, stroke=col, sw=1.6, pad=12, bold=False)
        out.append(b)
        return out

    p += pan(190, "ДАЄ", ["читабельність", "швидкість розробки", "переносність", "менше помилок"],
             FIELD, "#eafaf0")
    p += pan(W - 190, "БЕРЕ", ["накладні витрати", "більший розмір", "менше контролю", "віддаль від заліза"],
             POS, "#fdecea")

    p.append(text(cx, H - 22, "інженерія — свідомо зважувати цю торгівлю під кожну задачу",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "buys-costs.svg"), W, H, *p,
           title="Ваги абстракції: що дає і що бере")


# ── 4. when-which: фреймворк за замовчуванням, регістри точково ───────────────
def fig_when_which():
    W, H = 720, 290
    p = []
    # велика смуга «99 % коду — фреймворк», тонка вставка «гаряче місце — регістри»
    bx, by, bw, bh = 70, 110, 580, 70
    hot = 0.10
    wA = bw * (1 - hot)
    wB = bw * hot
    p.append(rect(bx, by, wA, bh, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=0))
    p.append(mtext(bx + wA / 2, by + bh / 2 - 4, "за замовчуванням — ФРЕЙМВОРК\n(швидко · надійно · переносно)",
                   size=12, color=INK))
    p.append(rect(bx + wA, by, wB, bh, fill="#fdecea", stroke=POS, sw=1.8, rx=0))
    p.append(text(bx + wA + wB / 2, by + bh + 18, "гаряче\nмісце", size=9, color=POS))

    p.append(text(bx, by - 16, "увесь код", size=11, color=MUTED, anchor="start", italic=True))
    p.append(text(bx + wA, by - 16, "регістри — точково", size=11, color=POS, anchor="middle", italic=True))

    p.append(mtext(W / 2, by + bh + 56,
                   "де треба гранична швидкість, тонкий контроль, мінімальний розмір\nчи глибоке розуміння — туди й сходимо до регістрів",
                   size=11, color=MUTED))
    render(os.path.join(OUT, "when-which.svg"), W, H, *p,
           title="Розумна стратегія: фреймворк за замовчуванням, регістри за потребою")


# ── 5. arduino-idf: спектр обгорток ──────────────────────────────────────────
def fig_arduino_idf():
    W, H = 720, 280
    p = []
    # шкала від тонкого до повносилого
    x0, x1, y = 110, W - 110, 130
    p.append(arrow(x0 - 20, y, x1 + 20, y, color=INK, sw=2))
    p.append(text(x0 - 24, y - 16, "тонше, дружніше", size=10, color=MUTED, anchor="start", italic=True))
    p.append(text(x1 + 24, y - 16, "повносиле, офіційне", size=10, color=MUTED, anchor="end", italic=True))

    a, aw, ah = textbox(x0 + 30, y, "Arduino", size=14, bold=True, color=FIELD,
                        fill="#eafaf0", stroke=FIELD, sw=1.8, min_w=130)
    p.append(a)
    p.append(text(x0 + 30, y + 50, "навчання, прототипи\nпросто, та зі «стелею»", size=10, color=MUTED))

    b, bw, bh = textbox(x1 - 30, y, "ESP-IDF", size=14, bold=True, color=NEG,
                        fill="#eef3ff", stroke=NEG, sw=1.8, min_w=130)
    p.append(b)
    p.append(text(x1 - 30, y + 50, "усі можливості, на ОСРЧ\nпотужно, та крутіше на вхід", size=10, color=MUTED))

    p.append(text(W / 2, H - 26, "Arduino збудовано ПОВЕРХ IDF — не суперники, а рівні тієї самої драбини",
                  size=11, color=INK, italic=True))
    render(os.path.join(OUT, "arduino-idf.svg"), W, H, *p,
           title="Фреймворки на шкалі: від тонкого Arduino до повносилого ESP-IDF")


# ── 6. cost-cycles: ціна виклику в тактах і часі ─────────────────────────────
def fig_cost_cycles():
    W, H = 720, 300
    p = []
    bx = 250
    barmax = 360
    # дві смуги тактів (логарифмічно «на око» — головне показати десятки разів)
    rows = [
        ("digitalWrite(2, HIGH)", 40, "≈ 40 тактів ≈ 0.17 мкс", POS, "#fdecea"),
        ("GPIO_OUT |= (1<<2)", 2, "≈ 2 такти ≈ 0.008 мкс", FIELD, "#eafaf0"),
    ]
    y = 96
    for lab, cyc, note, col, fill in rows:
        w = barmax * (cyc / 40.0)
        w = max(w, 22)
        p.append(('<text x="%.1f" y="%.1f" font-family="Consolas, monospace" font-size="12" '
                  'fill="%s" text-anchor="end">%s</text>' % (bx - 14, y + 26, INK, esc(lab))))
        p.append(rect(bx, y + 8, w, 36, fill=fill, stroke=col, sw=1.8, rx=6))
        p.append(text(bx + w + 10, y + 30, note, size=11, color=col, anchor="start", bold=True))
        y += 70

    p.append(text(bx, y + 6, "різниця ~10–50× — та на 240 МГц обидва тонуть у частках мкс",
                  size=11, color=MUTED, anchor="start", italic=True))
    p.append(mtext(W / 2, H - 34,
                   "для звичайної дії (блимнути раз на секунду) різниці не видно;\nвона важить лише в гарячому циклі на мільйони перемикань/с",
                   size=11, color=INK))
    render(os.path.join(OUT, "cost-cycles.svg"), W, H, *p,
           title="Ціна зручності: десятки тактів проти одного-трьох")


# ════════════════ ФІГУРИ ВСТАВКИ hist-arduino ════════════════

# ── i1. lineage: Processing → Wiring → Arduino ───────────────────────────────
def fig_lineage():
    W, H = 760, 240
    p = []
    y = 120
    stages = [
        ("Processing", "2001", "код — художникам", "#eef3ff", NEG),
        ("Wiring", "2003", "ідея — на залізо", "#eafaf0", FIELD),
        ("Arduino", "2005", "форк → масовий рух", "#fdf6e3", "#b8860b"),
    ]
    bw, bh = 180, 78
    gap = 70
    total = len(stages) * bw + (len(stages) - 1) * gap
    x = (W - total) / 2
    centers = []
    for name, yr, sub, fill, col in stages:
        b = rect(x, y - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.8, rx=10)
        b += text(x + bw / 2, y - 12, name, size=15, color=col, bold=True)
        b += text(x + bw / 2, y + 8, yr, size=11, color=INK)
        b += text(x + bw / 2, y + 26, sub, size=10, color=MUTED)
        p.append(b)
        centers.append((x, x + bw))
        x += bw + gap
    for i in range(len(stages) - 1):
        p.append(arrow(centers[i][1] + 4, y, centers[i + 1][0] - 4, y, color=INK, sw=2))
    p.append(text(W / 2, H - 20, "кожна ланка стоїть на попередній — Arduino не початок, а третя",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "hist-lineage.svg"), W, H, *p,
           title="Родовід: Processing → Wiring → Arduino")


# ── i2. wiring-vs-arduino: що змінилося, що лишилося ──────────────────────────
def fig_wiring_vs_arduino():
    W, H = 760, 300
    p = []
    colx = [220, 540]
    heads = [("Wiring (2003)", FIELD), ("Arduino (2005)", "#b8860b")]
    for cx, (h, col) in zip(colx, heads):
        p.append(text(cx, 64, h, size=14, color=col, bold=True))
    rows = [
        ("мова setup()/loop()", "та сама (форк)"),
        ("середовище (IDE)", "те саме (форк)"),
        ("мікроконтролер", "ATmega128 → ATmega8"),
        ("ціна плати", "~$100 → ~$30"),
    ]
    y = 100
    for left, right in rows:
        p.append(fitbox(colx[0] - 150, y, 300, 40, left, size=11, fill="#eafaf0", stroke=FIELD, sw=1.4))
        p.append(fitbox(colx[1] - 150, y, 300, 40, right, size=11, fill="#fdf6e3", stroke="#b8860b", sw=1.4))
        y += 50
    p.append(mtext(W / 2, H - 26,
                   "мова й IDE, відомі як «ардуїнівські», народилися у Wiring;\nArduino змінило передусім залізо — дешевше й відкрите",
                   size=11, color=MUTED))
    render(os.path.join(OUT, "hist-wiring-vs-arduino.svg"), W, H, *p,
           title="Wiring проти Arduino: що змінилося, що лишилося")


# ── i3. credit: дві версії історії ───────────────────────────────────────────
def fig_credit():
    W, H = 760, 300
    p = []
    # популярна версія — коротка
    p.append(text(200, 64, "популярний переказ", size=13, color=POS, bold=True))
    a, aw, ah = textbox(200, 130, "Arduino\n(команда, Іврея, бар)", size=12, bold=True,
                        color=INK, fill="#fdecea", stroke=POS, sw=1.8, min_w=220)
    p.append(a)
    p.append(text(200, 196, "Wiring і Барраґан зникають", size=10, color=POS))

    # чесніша версія — шарувата
    p.append(text(560, 64, "повніша картина", size=13, color=FIELD, bold=True))
    chain = ["Processing (Ріас, Фрай)", "Wiring (Барраґан)", "Arduino (команда)"]
    y = 100
    prev = None
    for c in chain:
        b, bw, bh = textbox(560, y + 18, c, size=11, color=INK, fill="#eafaf0", stroke=FIELD, sw=1.5, min_w=240)
        if prev is not None:
            p.append(arrow(560, prev, 560, y + 18 - bh / 2 - 2, color=INK, sw=1.6))
        p.append(b)
        prev = y + 18 + bh / 2
        y += 58
    p.append(mtext(W / 2, H - 24,
                   "Барраґан заклав фундамент, команда Arduino збудувала рух — обидва внески справжні",
                   size=11, color=MUTED))
    render(os.path.join(OUT, "hist-credit.svg"), W, H, *p,
           title="Дві версії історії: популярна й чесніша")


if __name__ == "__main__":
    fig_two_ways()
    fig_layers()
    fig_buys_costs()
    fig_when_which()
    fig_arduino_idf()
    fig_cost_cycles()
    fig_lineage()
    fig_wiring_vs_arduino()
    fig_credit()
    print("OK: figures written to", OUT)
