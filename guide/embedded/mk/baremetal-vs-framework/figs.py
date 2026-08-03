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
    W, H = 767, 300
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


# ════════════════ ФІГУРИ ДЕТАЛЬНОЇ СТАТТІ baremetal-vs-framework-d ════════════

# ── d1. two-ceilings: стеля обгортки й стеля шини ─────────────────────────────
def fig_two_ceilings():
    W, H = 760, 340
    p = []
    # вертикальна вісь швидкості: чим вище, тим швидше
    ax = 150
    ytop, ybot = 70, 280
    p.append(arrow(ax, ybot, ax, ytop - 8, color=INK, sw=2))
    p.append(text(ax, ytop - 16, "швидше →", size=10, color=MUTED, italic=True))

    # стеля APB (нижня, фізична) — суцільна товста лінія
    y_apb = 210
    p.append(line(ax, y_apb, W - 60, y_apb, color=POS, sw=3))
    p.append(text(W - 60, y_apb - 8, "стеля APB ≈ 3–4 МГц", size=11, color=POS, anchor="end", bold=True))
    p.append(text(ax + 14, y_apb + 18, "фізична: регістр GPIO на шині 80 МГц", size=10, color=MUTED, anchor="start"))

    # стеля обгортки (ще нижче) — пунктир
    y_fw = 250
    p.append(line(ax, y_fw, W - 60, y_fw, color=MUTED, sw=2, dash="6,5"))
    p.append(text(W - 60, y_fw + 16, "digitalWrite: ще ×3 накладних", size=11, color=MUTED, anchor="end"))

    # ядро 240 МГц — недосяжна мрія нагорі
    p.append(line(ax, ytop + 8, W - 60, ytop + 8, color=NEG, sw=1.6, dash="2,4"))
    p.append(text(W - 60, ytop + 2, "ядро 240 МГц (недосяжно для ніжки на APB)", size=10, color=NEG, anchor="end", italic=True))

    b, bw, bh = textbox((ax + W) / 2 - 20, 150,
                        "прибрати обгортку — здолати нижню стелю;\nверхню (шину) вона не рухає",
                        size=11, color=INK, fill="#f4f6f8", stroke=INK, sw=1.4, pad=12)
    p.append(b)
    render(os.path.join(OUT, "two-ceilings.svg"), W, H, *p,
           title="Дві стелі швидкості: обгортка знімається, шина лишається")


# ── d2. gpio-tiers: три поверхи доступу до ніжки ──────────────────────────────
def fig_gpio_tiers():
    W, H = 760, 320
    p = []
    rows = [
        ("digitalWrite(2, HIGH)", "обгортка над IDF · ~58 тактів на виклик", "#fdecea", POS, 0.28),
        ("REG_WRITE(W1TS, 1<<2)", "прямий запис у регістр APB · стеля ~3–4 МГц", "#fdf6e3", "#b8860b", 0.55),
        ("dedic_gpio (CSR, S2/S3)", "повз APB, прямо з ядра · десятки МГц", "#eafaf0", FIELD, 1.0),
    ]
    bx = 250
    barmax = 420
    y = 90
    for code, note, fill, col, frac in rows:
        p.append(('<text x="%.1f" y="%.1f" font-family="Consolas, monospace" font-size="12" '
                  'fill="%s" text-anchor="end">%s</text>' % (bx - 14, y + 24, INK, esc(code))))
        w = max(barmax * frac, 40)
        p.append(rect(bx, y + 6, w, 34, fill=fill, stroke=col, sw=1.8, rx=6))
        p.append(text(bx + 10, y + 27, note, size=10.5, color=col, anchor="start", bold=True))
        y += 66
    p.append(mtext(W / 2, H - 34,
                   "ключ не в «менше абстракцій», а в «інший механізм заліза»:\nшвидкість дає правильний шлях даних у чипі, а не відмова від обгортки",
                   size=11, color=INK))
    render(os.path.join(OUT, "gpio-tiers.svg"), W, H, *p,
           title="Три поверхи швидкості GPIO на ESP32")


# ── d3. rmw-race: гонитва read-modify-write ──────────────────────────────────
def fig_rmw_race():
    W, H = 780, 360
    p = []
    lx, rx = 210, 560          # колонки: основний код / переривання
    p.append(text(lx, 62, "основний код", size=13, color=NEG, bold=True))
    p.append(text(rx, 62, "переривання (ISR)", size=13, color=POS, bold=True))
    # вертикальна вісь часу
    p.append(arrow(W / 2, 78, W / 2, H - 60, color=MUTED, sw=1.4))
    p.append(text(W / 2 + 8, H - 46, "час", size=10, color=MUTED, anchor="start", italic=True))

    def step(cx, y, s, col, fill):
        b = fitbox(cx - 150, y, 300, 40, s, size=10.5, fill=fill, stroke=col, sw=1.5)
        return b

    p.append(step(lx, 84, "1. читає GPIO_OUT = 0x00", NEG, "#eaf0fd"))
    p.append(step(rx, 140, "читає GPIO_OUT = 0x00\nставить біт 5 → 0x20\nзаписує 0x20  ← ніжка 5 УВІМК", POS, "#fdecea"))
    p.append(step(lx, 226, "2. у СТАРІЙ копії ставить біт 2 → 0x04", NEG, "#eaf0fd"))
    p.append(step(lx, 278, "3. записує 0x04  ← біт 5 ЗАТЕРТО!", POS, "#fdecea"))

    # стрілка «влучило» від осі до ISR
    p.append(text(W / 2, 128, "◀ влучило між читанням і записом", size=10, color=POS, anchor="middle", italic=True))
    p.append(mtext(W / 2, H - 20,
                   "`|=` = прочитати-змінити-записати; переривання влучає в проміжок і його зміну затирають — збій плаваючий",
                   size=10.5, color=INK))
    render(os.path.join(OUT, "rmw-race.svg"), W, H, *p,
           title="Гонитва read-modify-write: чому GPIO_OUT |= (1<<2) буває неправильним")


# ── d4. startup-flow: від скидання до вашого коду ─────────────────────────────
def fig_startup_flow():
    W, H = 780, 360
    p = []
    # вертикальний ланцюг кроків стартового коду
    cx = 300
    steps = [
        ("подача живлення / скидання", "лічильник команд → фіксована адреса", "#efefef", MUTED),
        ("підняти годинники", "PLL, дільники, кеш → 240 МГц", "#fdf6e3", "#b8860b"),
        ("копіювати .data з Flash у RAM", "початкові значення глобальних", "#eef3ff", NEG),
        ("обнулити .bss у RAM", "неініціалізовані → нулі", "#eef3ff", NEG),
        ("привести периферію до відомого стану", "порти, шини, переривання", "#fdf6e3", "#b8860b"),
        ("викликати ВАШ код", "setup() / loop() / app_main", "#eafaf0", FIELD),
    ]
    bw, bh = 300, 40
    y = 62
    gap = 12
    centers = []
    for name, sub, fill, col in steps:
        b = rect(cx - bw / 2, y, bw, bh, fill=fill, stroke=col, sw=1.6, rx=8)
        b += text(cx, y + 16, name, size=11.5, color=col, bold=True)
        b += text(cx, y + 32, sub, size=9.5, color=MUTED)
        p.append(b)
        centers.append(y + bh)
        y += bh + gap
    for i in range(len(steps) - 1):
        p.append(arrow(cx, centers[i] + 1, cx, centers[i] + gap - 1, color=INK, sw=1.6))
    # права підпис-дужка: усе це — обов'язок голого заліза
    bx = cx + bw / 2 + 30
    p.append(line(bx, 62, bx, centers[-2], color=POS, sw=2))
    p.append(line(bx, 62, bx - 8, 62, color=POS, sw=2))
    p.append(line(bx, centers[-2], bx - 8, centers[-2], color=POS, sw=2))
    p.append(text(bx + 10, (62 + centers[-2]) / 2 - 10,
                  "на голому залізі —", size=10.5, color=POS, anchor="start", bold=True))
    p.append(text(bx + 10, (62 + centers[-2]) / 2 + 6,
                  "усе це ваш обов'язок;", size=10, color=POS, anchor="start"))
    p.append(text(bx + 10, (62 + centers[-2]) / 2 + 22,
                  "забути будь-що →", size=10, color=POS, anchor="start"))
    p.append(text(bx + 10, (62 + centers[-2]) / 2 + 38,
                  "«магічний» баг", size=10, color=POS, anchor="start", italic=True))
    render(os.path.join(OUT, "startup-flow.svg"), W, H, *p,
           title="Від скидання до вашого коду: що робить стартовий код")


# ── d5. weak-symbol: слабке гніздо, яке перекриває ваш код ────────────────────
def fig_weak_symbol():
    W, H = 760, 320
    p = []
    # ліворуч — фреймворк лишає слабку заглушку; праворуч — ваш сильний символ
    lx, rx = 200, 560
    p.append(text(lx, 58, "фреймворк лишає", size=12, color=MUTED, bold=True))
    a, aw, ah = textbox(lx, 118, "weak setup()\n{ /* порожньо */ }", size=11.5, bold=True,
                        color=MUTED, fill="#efefef", stroke=MUTED, sw=1.6, min_w=230)
    p.append(a)
    p.append(text(lx, 176, "слабкий символ = запасне гніздо", size=10, color=MUTED, italic=True))

    p.append(text(rx, 58, "ви пишете", size=12, color=FIELD, bold=True))
    b, bw, bh = textbox(rx, 118, "setup()\n{ ваша логіка }", size=11.5, bold=True,
                        color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.8, min_w=230)
    p.append(b)
    p.append(text(rx, 176, "сильний символ", size=10, color=FIELD, italic=True))

    # стрілка «перекриває»
    p.append(arrow(rx - bw / 2 - 4, 118, lx + aw / 2 + 4, 118, color=POS, sw=2))
    p.append(text((lx + rx) / 2, 104, "перекриває", size=11, color=POS, bold=True))

    # знизу — main() фреймворку кличе результат
    m, mw, mh = textbox((lx + rx) / 2, 236, "main() фреймворку кличе setup() — і бере ВАШ, сильний",
                        size=11.5, color=INK, fill="#eef3ff", stroke=NEG, sw=1.8, pad=12)
    p.append(m)
    p.append(mtext(W / 2, H - 22,
                   "ви не «під'єднуєтесь» до фреймворку — ви перекриваєте залишені для вас слабкі гнізда",
                   size=11, color=MUTED))
    render(os.path.join(OUT, "weak-symbol.svg"), W, H, *p,
           title="Слабкий символ: ваш setup() перекриває заглушку фреймворку")


# ── d6. leaky: закон дірявих абстракцій на нашому маршруті ────────────────────
def fig_leaky():
    W, H = 780, 330
    p = []
    p.append(text(W / 2, 54, "кожен шар тече під тиском — деталлю нижчого", size=13, color=INK, italic=True))
    rows = [
        ("digitalWrite", "гарячий цикл", "проступають такти + стеля APB"),
        ("«просто пиши C»", ".data / .bss", "змінна містить сміття на старті"),
        ("прямий запис у регістр", "переривання", "гонитва read-modify-write"),
        ("сам C (модель пам'яті)", "забутий volatile", "оптимізатор вивертає регістровий код"),
    ]
    y = 84
    for absn, press, leak in rows:
        p.append(fitbox(90, y, 200, 46, absn, size=11, fill="#eafaf0", stroke=FIELD, sw=1.5, bold=True))
        p.append(text(312, y + 20, "під тиском", size=9, color=MUTED, anchor="middle", italic=True))
        p.append(fitbox(300, y + 24, 150, 20, press, size=9.5, fill="#fdf6e3", stroke="#b8860b", sw=1.2, pad=4))
        p.append(arrow(300, y + 23, 292, y + 23, color=POS, sw=1.4))
        p.append(arrow(462, y + 23, 476, y + 23, color=POS, sw=1.6))
        p.append(fitbox(478, y, 224, 46, leak, size=10, fill="#fdecea", stroke=POS, sw=1.5))
        y += 58
    render(os.path.join(OUT, "leaky.svg"), W, H, *p,
           title="Закон дірявих абстракцій: течуть усі, кожна на своїй межі")


# ── d7. decide-flow: кількісний маршрут рішення ──────────────────────────────
def fig_decide_flow():
    W, H = 780, 330
    p = []
    cx = W / 2
    boxes = [
        ("1. ПОРАХУЙ БЮДЖЕТ", "ціна дії × частота проти часу ЦП", "#eef3ff", NEG),
        ("2. ВИМІРЯЙ РЕАЛЬНІСТЬ", "осцилограф / лічильник тактів — не вір оцінці", "#fdf6e3", "#b8860b"),
        ("3. ОПТИМІЗУЙ ВУЗЬКЕ МІСЦЕ", "саме ту стелю: обгортка? шина? механізм?", "#eafaf0", FIELD),
        ("4. СХОДЬ ДО РЕГІСТРІВ ПРАВИЛЬНО", "атомарно W1TS/W1TC · volatile · без гонитв", "#eafaf0", FIELD),
    ]
    bw, bh = 420, 48
    y = 62
    gap = 20
    centers = []
    for name, sub, fill, col in boxes:
        b = rect(cx - bw / 2, y, bw, bh, fill=fill, stroke=col, sw=1.8, rx=8)
        b += text(cx, y + 19, name, size=12.5, color=col, bold=True)
        b += text(cx, y + 36, sub, size=10, color=MUTED)
        p.append(b)
        centers.append(y + bh)
        y += bh + gap
    for i in range(len(boxes) - 1):
        p.append(arrow(cx, centers[i] + 1, cx, centers[i] + gap - 1, color=INK, sw=1.7))
    # бічна ремарка після кроку 1
    p.append(text(cx + bw / 2 + 16, centers[0] - 12,
                  "часто: оптимізувати\nнічого — стоп тут", size=9.5, color=MUTED, anchor="start", italic=True))
    render(os.path.join(OUT, "decide-flow.svg"), W, H, *p,
           title="Вирішувати числом: бюджет → вимір → вузьке місце → правильний спуск")


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
    fig_two_ceilings()
    fig_gpio_tiers()
    fig_rmw_race()
    fig_startup_flow()
    fig_weak_symbol()
    fig_leaky()
    fig_decide_flow()
    print("OK: figures written to", OUT)
