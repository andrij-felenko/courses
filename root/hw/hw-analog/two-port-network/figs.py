# -*- coding: utf-8 -*-
"""Фігури до статті «Двополюсні та чотириполюсні мережі»
(book/electronics/analog/two-port-network).
Чотири фігури:
  blackbox.svg  — ідея: довільне коло → «чорна скринька» з парою полюсів і умовою порту
  params.svg    — чотири описи (Z, Y, h, ABCD): що беремо за причину, що за наслідок
  cascade.svg   — навіщо ABCD: матриці послідовних ланок просто перемножуються
  model.svg     — підсилювач як чотириполюсник: вхідний опір, кероване джерело, вихідний опір
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ────────────────────────────────────────────────────────
def term(cx, cy, color=INK):
    """Полюс-затискач (кружечок-вузол)."""
    return circle(cx, cy, 4, fill="#ffffff", stroke=color, sw=2)


def resistor_h(x0, x1, y, label=None, color=POS):
    """Горизонтальний резистор-зигзаг між (x0,y) та (x1,y)."""
    out = []
    n = 6
    seg = (x1 - x0) / (n + 1)
    amp = 7
    out.append(line(x0, y, x0 + seg, y, color=INK, sw=1.6))
    xx = x0 + seg
    for i in range(n):
        ny = y + (amp if i % 2 == 0 else -amp)
        px = xx
        py = y if i == 0 else (y - amp if i % 2 == 1 else y + amp)
        out.append(line(px, py, xx + seg, ny, color=INK, sw=1.6))
        xx += seg
    out.append(line(xx, y + (amp if (n - 1) % 2 == 0 else -amp), x1, y, color=INK, sw=1.6))
    if label:
        out.append(text((x0 + x1) / 2, y - 12, label, size=12, color=color, bold=True))
    return "".join(out)


def vsrc(cx, cy, label=None, color=NEG):
    """Кероване джерело напруги — ромб зі знаками."""
    r = 18
    out = ['<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f L %.0f %.0f Z" '
           'fill="#ffffff" stroke="%s" stroke-width="1.8"/>'
           % (cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy, color)]
    out.append(text(cx, cy - r * 0.3, "+", size=12, color=POS, bold=True))
    out.append(text(cx, cy + r * 0.7, "−", size=12, color=NEG, bold=True))
    if label:
        out.append(text(cx, cy + r + 16, label, size=12, color=color, bold=True))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. blackbox.svg — будь-яке коло звертається до пари «полюсів» + умова порту
# ════════════════════════════════════════════════════════════════════════════
def fig_blackbox():
    W, H = 660, 360
    f = []

    # ── ліворуч: «начиння» — заплутане коло (резистори/джерела всередині) ──
    lx, ly, lw, lh = 40, 90, 150, 150
    f.append(rect(lx, ly, lw, lh, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=10))
    # натяк на «купу елементів» усередині
    f.append(resistor_h(lx + 22, lx + 78, ly + 40, color=MUTED))
    f.append(resistor_h(lx + 70, lx + 126, ly + 90, color=MUTED))
    f.append(line(lx + 100, ly + 30, lx + 100, ly + 70, color=MUTED, sw=1.6))
    f.append(circle(lx + 40, ly + 110, 10, fill="#ffffff", stroke=MUTED, sw=1.5))
    f.append(text(lx + lw / 2, ly - 10, "будь-яке коло", size=12, color=MUTED))
    f.append(text(lx + lw / 2, ly + lh + 18, "(хоч сотня елементів)", size=11, color=MUTED))

    # стрілка «згортаємо до»
    f.append(arrow(lx + lw + 8, H / 2 - 10, lx + lw + 56, H / 2 - 10, color=INK, sw=2.4))
    f.append(text(lx + lw + 34, H / 2 - 22, "ховаємо", size=11, color=MUTED))

    # ── праворуч: чорна скринька з двома портами ──
    bx, by, bw, bh = 270, 100, 200, 150
    f.append(rect(bx, by, bw, bh, fill="#1a1a1a", stroke=INK, sw=2, rx=12))
    f.append(text(bx + bw / 2, by + bh / 2 - 6, "ЧОРНА", size=16, color="#ffffff", bold=True))
    f.append(text(bx + bw / 2, by + bh / 2 + 16, "СКРИНЬКА", size=16, color="#ffffff", bold=True))

    yt, yb = by + 42, by + 108          # рівні верхнього/нижнього затискача
    # лівий порт (вхід)
    f.append(line(bx - 70, yt, bx, yt, color=INK, sw=1.8))
    f.append(line(bx - 70, yb, bx, yb, color=INK, sw=1.8))
    f.append(term(bx - 70, yt)); f.append(term(bx - 70, yb))
    f.append(arrow(bx - 60, yt - 16, bx - 30, yt - 16, color=POS, sw=2.0))
    f.append(text(bx - 45, yt - 22, "I₁", size=13, color=POS, bold=True))
    f.append(text(bx - 90, (yt + yb) / 2 + 4, "U₁", size=14, color=NEG, bold=True, anchor="middle"))
    f.append(line(bx - 90, yt + 6, bx - 90, yb - 6, color=NEG, sw=1.2, dash="3 3"))
    f.append(text(bx - 40, by + bh + 18, "ПОРТ 1 (вхід)", size=11, color=INK, bold=True, anchor="middle"))

    # правий порт (вихід)
    f.append(line(bx + bw, yt, bx + bw + 70, yt, color=INK, sw=1.8))
    f.append(line(bx + bw, yb, bx + bw + 70, yb, color=INK, sw=1.8))
    f.append(term(bx + bw + 70, yt)); f.append(term(bx + bw + 70, yb))
    f.append(arrow(bx + bw + 30, yt - 16, bx + bw + 60, yt - 16, color=POS, sw=2.0))
    f.append(text(bx + bw + 45, yt - 22, "I₂", size=13, color=POS, bold=True))
    f.append(text(bx + bw + 92, (yt + yb) / 2 + 4, "U₂", size=14, color=NEG, bold=True, anchor="middle"))
    f.append(line(bx + bw + 92, yt + 6, bx + bw + 92, yb - 6, color=NEG, sw=1.2, dash="3 3"))
    f.append(text(bx + bw + 40, by + bh + 18, "ПОРТ 2 (вихід)", size=11, color=INK, bold=True, anchor="middle"))

    # умова порту внизу
    body, w0, h0 = textbox(W / 2, H - 24,
                           "Умова порту: скільки струму ввійшло у верхній затискач —\nрівно стільки вийшло з нижнього (порт не «протікає» вбік)",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "blackbox.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. params.svg — чотири описи: що задаємо, що виходить
# ════════════════════════════════════════════════════════════════════════════
def fig_params():
    W, H = 700, 360
    f = []
    f.append(text(W / 2, 30, "Одна скринька — чотири способи її описати", size=16, bold=True))

    # чотири картки
    cards = [
        ("Z — опірні", "задаю струми I₁,I₂", "→  виходять напруги", "U = Z · I", POS, "#fdecea"),
        ("Y — провідні", "задаю напруги U₁,U₂", "→  виходять струми", "I = Y · U", NEG, "#eaf0fd"),
        ("h — гібридні", "задаю I₁ та U₂", "→  виходять U₁ та I₂", "мішанка — для транзистора", FIELD, "#eef7f0"),
        ("ABCD — передавальні", "задаю вихід U₂,I₂", "→  виходять вхід U₁,I₁", "для каскадів поспіль", "#8e44ad", "#f3ecf8"),
    ]
    cw, ch, gap = 150, 190, 24
    x0 = (W - (4 * cw + 3 * gap)) / 2
    y0 = 64
    for i, (title, give, get, note, col, fill) in enumerate(cards):
        x = x0 + i * (cw + gap)
        f.append(rect(x, y0, cw, ch, fill=fill, stroke=col, sw=2, rx=10))
        f.append(text(x + cw / 2, y0 + 26, title, size=13, color=col, bold=True))
        f.append(line(x + 14, y0 + 38, x + cw - 14, y0 + 38, color=col, sw=1.2))
        f.append(fitbox(x + 10, y0 + 50, cw - 20, 40, give, size=11, fill="#ffffff", stroke=col, rx=6))
        f.append(fitbox(x + 10, y0 + 98, cw - 20, 40, get, size=11, fill="#ffffff", stroke=col, rx=6))
        f.append(fitbox(x + 10, y0 + 146, cw - 20, 34, note, size=10, fill=fill, stroke=col, rx=6))

    f.append(text(W / 2, H - 14,
                  "Усі чотири описують ту саму скриньку — між ними переходять алгеброю; обирають той, що зручніший для задачі",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "params.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. cascade.svg — навіщо ABCD: послідовні ланки = добуток матриць
# ════════════════════════════════════════════════════════════════════════════
def fig_cascade():
    W, H = 700, 300
    f = []
    f.append(text(W / 2, 30, "Ланки поспіль: вихід однієї — вхід наступної", size=16, bold=True))

    yt, yb = 110, 180
    blocks = [(70, "ланка A", "#fdecea", POS), (300, "ланка B", "#eaf0fd", NEG), (530, "ланка C", "#eef7f0", FIELD)]
    bw = 110
    for bx, lab, fill, col in blocks:
        f.append(rect(bx, 90, bw, 100, fill=fill, stroke=col, sw=2, rx=8))
        f.append(text(bx + bw / 2, 130, lab, size=13, color=col, bold=True))
        f.append(text(bx + bw / 2, 152, "[A B; C D]", size=11, color=col))
        # верхній і нижній провід
        f.append(line(bx, yt, bx, yt, color=INK, sw=1.6))

    # сполучні дроти між ланками (верхній і нижній)
    f.append(line(20, yt, 70, yt, color=INK, sw=1.8)); f.append(line(20, yb, 70, yb, color=INK, sw=1.8))
    f.append(line(180, yt, 300, yt, color=INK, sw=1.8)); f.append(line(180, yb, 300, yb, color=INK, sw=1.8))
    f.append(line(410, yt, 530, yt, color=INK, sw=1.8)); f.append(line(410, yb, 530, yb, color=INK, sw=1.8))
    f.append(line(640, yt, 680, yt, color=INK, sw=1.8)); f.append(line(640, yb, 680, yb, color=INK, sw=1.8))
    for tx in (20, 680):
        f.append(term(tx, yt)); f.append(term(tx, yb))
    f.append(text(20, yt - 12, "вхід", size=11, color=MUTED, anchor="start"))
    f.append(text(680, yt - 12, "вихід", size=11, color=MUTED, anchor="end"))

    # підсумкова формула
    body, w0, h0 = textbox(W / 2, 250,
                           "Уся гірлянда = одна скринька з матрицею  [A B; C D]_заг = [A B; C D]_A · [A B; C D]_B · [A B; C D]_C\n"
                           "Саме тому в ABCD беруть вихідний струм зі знаком «−»: тоді матриці множаться підряд без поправок",
                           size=11, color=INK, fill="#f3ecf8", stroke="#8e44ad")
    f.append(body)
    render(os.path.join(IMG, "cascade.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. model.svg — підсилювач як чотириполюсник (вхід Zin, джерело, вихід Zout)
# ════════════════════════════════════════════════════════════════════════════
def fig_model():
    W, H = 680, 340
    f = []
    f.append(text(W / 2, 28, "Підсилювач, згорнутий до чотириполюсника", size=16, bold=True))

    yt, yb = 110, 230
    # рамка-скринька
    bx, by, bw, bh = 120, 80, 440, 180
    f.append(rect(bx, by, bw, bh, fill="#fbfbfc", stroke=INK, sw=1.8, rx=12))

    # лівий порт (вхід) + вхідний опір Z_in поперек порту
    f.append(line(40, yt, bx, yt, color=INK, sw=1.8))
    f.append(line(40, yb, bx, yb, color=INK, sw=1.8))
    f.append(term(40, yt)); f.append(term(40, yb))
    f.append(text(40, yt - 12, "U₁", size=13, color=NEG, bold=True, anchor="start"))
    # Z_in вертикально одразу за входом
    zinx = bx + 60
    f.append(line(bx, yt, zinx, yt, color=INK, sw=1.6))
    f.append(line(bx, yb, zinx, yb, color=INK, sw=1.6))
    # вертикальний резистор Z_in
    f.append('<rect x="%.0f" y="%.0f" width="22" height="70" rx="3" fill="#fdecea" stroke="%s" stroke-width="1.6"/>'
             % (zinx - 11, yt + 5, POS))
    f.append(line(zinx, yt, zinx, yt + 5, color=INK, sw=1.6))
    f.append(line(zinx, yt + 75, zinx, yb, color=INK, sw=1.6))
    f.append(text(zinx + 26, (yt + yb) / 2 + 4, "Z_вх", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(zinx + 26, (yt + yb) / 2 + 20, "(що бачить джерело)", size=9, color=MUTED, anchor="start"))

    # праворуч у скриньці: кероване джерело + вихідний опір
    # кероване джерело напруги «A·U₁» послідовно у верхній гілці виходу
    srcx = bx + 250
    f.append(vsrc(srcx, (yt + yb) / 2, label=None, color="#8e44ad"))
    f.append(text(srcx, (yt + yb) / 2 - 30, "A · U₁", size=12, color="#8e44ad", bold=True))
    f.append(text(srcx, (yt + yb) / 2 + 34, "копія входу, підсилена", size=9, color=MUTED))

    # від джерела через Z_out до правого верхнього затискача
    zoutx = bx + 350
    f.append(line(srcx, (yt + yb) / 2 - 18, srcx, yt, color=INK, sw=1.6))
    f.append(resistor_h(srcx + 16, zoutx, yt, label="Z_вих", color=NEG))
    f.append(line(srcx, (yt + yb) / 2 + 18, srcx, yb, color=INK, sw=1.6))

    # правий порт (вихід)
    f.append(line(zoutx, yt, 640, yt, color=INK, sw=1.8))
    f.append(line(bx + bw, yb, 640, yb, color=INK, sw=1.8))
    f.append(line(zoutx, yt, bx + bw, yt, color=INK, sw=1.6))
    f.append(term(640, yt)); f.append(term(640, yb))
    f.append(text(640, yt - 12, "U₂", size=13, color=NEG, bold=True, anchor="end"))

    body, w0, h0 = textbox(W / 2, H - 22,
                           "Три числа замість усієї схеми: вхідний опір Z_вх, підсилення A та вихідний опір Z_вих —\n"
                           "цього досить, щоб передбачити, як каскад поведеться з будь-яким джерелом і навантаженням",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "model.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. recipes.svg — як «зміряти» кожен коефіцієнт: холостий хід / коротке замикання
#     (для math-вставки: формальне означення Z, Y, h через ХХ/КЗ портів)
# ════════════════════════════════════════════════════════════════════════════
def fig_recipes():
    W, H = 700, 380
    f = []
    f.append(text(W / 2, 28, "Кожен коефіцієнт — це окремий дослід над скринькою", size=16, bold=True))

    # три колонки: Z (ХХ виходу), Y (КЗ виходу), h (мішанка)
    cols = [
        (60, "Z₁₁ — вхідний опір",
         "ХХ виходу:  I₂ = 0",
         "(вихід РОЗІМКНЕНО)",
         "подаю струм I₁, міряю U₁",
         "Z₁₁ = U₁ / I₁", POS, "#fdecea"),
        (260, "Y₁₁ — вхідна провідність",
         "КЗ виходу:  U₂ = 0",
         "(вихід ЗАКОРОЧЕНО)",
         "подаю напругу U₁, міряю I₁",
         "Y₁₁ = I₁ / U₁", NEG, "#eaf0fd"),
        (460, "h₂₁ — підсилення струму",
         "КЗ виходу:  U₂ = 0",
         "(вихід ЗАКОРОЧЕНО)",
         "подаю струм I₁, міряю I₂",
         "h₂₁ = I₂ / I₁", FIELD, "#eef7f0"),
    ]
    cw = 180
    y0 = 60
    for x, title, cond, cond2, how, formula, col, fill in cols:
        f.append(rect(x, y0, cw, 250, fill=fill, stroke=col, sw=2, rx=10))
        f.append(fitbox(x + 12, y0 + 14, cw - 24, 34, title, size=12, fill="#ffffff", stroke=col, rx=6, bold=True, color=col))
        # маленька скринька з портами
        bx, by, bw, bh = x + 40, y0 + 64, 100, 70
        f.append(rect(bx, by, bw, bh, fill="#1a1a1a", stroke=INK, sw=1.5, rx=6))
        # лівий порт — джерело-збудження
        f.append(line(bx - 26, by + 18, bx, by + 18, color=INK, sw=1.6))
        f.append(line(bx - 26, by + bh - 18, bx, by + bh - 18, color=INK, sw=1.6))
        f.append(term(bx - 26, by + 18, color=col)); f.append(term(bx - 26, by + bh - 18, color=col))
        # правий порт — стан: розімкнено (ХХ) чи закорочено (КЗ)
        f.append(line(bx + bw, by + 18, bx + bw + 26, by + 18, color=INK, sw=1.6))
        f.append(line(bx + bw, by + bh - 18, bx + bw + 26, by + bh - 18, color=INK, sw=1.6))
        if "ХХ" in cond:
            # розімкнено — два «висячі» затискачі з розривом
            f.append(term(bx + bw + 26, by + 18, color=MUTED)); f.append(term(bx + bw + 26, by + bh - 18, color=MUTED))
            f.append(text(bx + bw + 30, by + bh / 2 + 4, "⌀", size=14, color=MUTED, anchor="start"))
        else:
            # закорочено — перемичка між затискачами
            f.append(line(bx + bw + 26, by + 18, bx + bw + 26, by + bh - 18, color=POS, sw=2.4))
        f.append(fitbox(x + 12, y0 + 146, cw - 24, 26, cond, size=10, fill="#ffffff", stroke=col, rx=5))
        f.append(text(x + cw / 2, y0 + 184, cond2, size=9, color=MUTED))
        f.append(fitbox(x + 12, y0 + 192, cw - 24, 24, how, size=9, fill=fill, stroke=col, rx=5))
        f.append(fitbox(x + 12, y0 + 220, cw - 24, 24, formula, size=11, fill="#ffffff", stroke=col, rx=5, bold=True, color=col))

    f.append(text(W / 2, H - 12,
                  "Розімкнув вихід (I₂=0) → міряю опори Z. Закоротив вихід (U₂=0) → міряю провідності Y. Те саме для входу.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "recipes.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 6. blocks.svg — «цеглинки» з готовими ABCD: послідовний Z, паралельний Y, L, T
# ════════════════════════════════════════════════════════════════════════════
def fig_blocks():
    W, H = 700, 420
    f = []
    f.append(text(W / 2, 28, "Заготовки ланок та їхні ABCD-матриці", size=16, bold=True))

    yt, yb = 0, 0  # перевизначаються в кожній комірці

    def cell(cx, cy, label, matrix, draw):
        col = INK
        f.append(text(cx, cy - 58, label, size=12, color=POS, bold=True))
        draw(cx, cy)
        f.append(fitbox(cx - 78, cy + 30, 156, 34, matrix, size=11, fill="#f3ecf8", stroke="#8e44ad", rx=6, bold=True, color="#8e44ad"))

    # --- послідовний імпеданс Z ---
    def draw_series(cx, cy):
        f.append(line(cx - 90, cy, cx - 30, cy, color=INK, sw=1.8))
        f.append(resistor_h(cx - 30, cx + 30, cy, label="Z", color=POS))
        f.append(line(cx + 30, cy, cx + 90, cy, color=INK, sw=1.8))
        f.append(line(cx - 90, cy + 34, cx + 90, cy + 34, color=INK, sw=1.8))
        f.append(term(cx - 90, cy)); f.append(term(cx - 90, cy + 34))
        f.append(term(cx + 90, cy)); f.append(term(cx + 90, cy + 34))

    # --- паралельний адмітанс Y ---
    def draw_shunt(cx, cy):
        f.append(line(cx - 90, cy, cx + 90, cy, color=INK, sw=1.8))
        f.append(line(cx - 90, cy + 44, cx + 90, cy + 44, color=INK, sw=1.8))
        # вертикальний елемент Y посередині
        f.append('<rect x="%.0f" y="%.0f" width="20" height="30" rx="3" fill="#eaf0fd" stroke="%s" stroke-width="1.6"/>'
                 % (cx - 10, cy + 7, NEG))
        f.append(line(cx, cy, cx, cy + 7, color=INK, sw=1.6))
        f.append(line(cx, cy + 37, cx, cy + 44, color=INK, sw=1.6))
        f.append(text(cx + 26, cy + 26, "Y", size=12, color=NEG, bold=True, anchor="start"))
        f.append(term(cx - 90, cy)); f.append(term(cx - 90, cy + 44))
        f.append(term(cx + 90, cy)); f.append(term(cx + 90, cy + 44))

    # --- Г-ланка (L): послідовний Z, тоді паралельний Y ---
    def draw_L(cx, cy):
        f.append(line(cx - 90, cy, cx - 50, cy, color=INK, sw=1.8))
        f.append(resistor_h(cx - 50, cx + 4, cy, label="Z", color=POS))
        f.append(line(cx + 4, cy, cx + 90, cy, color=INK, sw=1.8))
        f.append(line(cx - 90, cy + 44, cx + 90, cy + 44, color=INK, sw=1.8))
        # шунт Y ближче до виходу
        sx = cx + 40
        f.append('<rect x="%.0f" y="%.0f" width="18" height="28" rx="3" fill="#eaf0fd" stroke="%s" stroke-width="1.6"/>'
                 % (sx - 9, cy + 8, NEG))
        f.append(line(sx, cy, sx, cy + 8, color=INK, sw=1.6))
        f.append(line(sx, cy + 36, sx, cy + 44, color=INK, sw=1.6))
        f.append(text(sx + 14, cy + 26, "Y", size=11, color=NEG, bold=True, anchor="start"))
        f.append(term(cx - 90, cy)); f.append(term(cx - 90, cy + 44))
        f.append(term(cx + 90, cy)); f.append(term(cx + 90, cy + 44))

    # --- T-ланка: Z1 послідовно, Y шунт, Z2 послідовно ---
    def draw_T(cx, cy):
        f.append(line(cx - 95, cy, cx - 70, cy, color=INK, sw=1.8))
        f.append(resistor_h(cx - 70, cx - 24, cy, label="Z₁", color=POS))
        f.append(line(cx - 24, cy, cx + 24, cy, color=INK, sw=1.8))
        f.append(resistor_h(cx + 24, cx + 70, cy, label="Z₂", color=POS))
        f.append(line(cx + 70, cy, cx + 95, cy, color=INK, sw=1.8))
        f.append(line(cx - 95, cy + 44, cx + 95, cy + 44, color=INK, sw=1.8))
        # шунт Y по центру
        f.append('<rect x="%.0f" y="%.0f" width="18" height="28" rx="3" fill="#eaf0fd" stroke="%s" stroke-width="1.6"/>'
                 % (cx - 9, cy + 8, NEG))
        f.append(line(cx, cy, cx, cy + 8, color=INK, sw=1.6))
        f.append(line(cx, cy + 36, cx, cy + 44, color=INK, sw=1.6))
        f.append(text(cx + 14, cy + 26, "Y", size=11, color=NEG, bold=True, anchor="start"))
        f.append(term(cx - 95, cy)); f.append(term(cx - 95, cy + 44))
        f.append(term(cx + 95, cy)); f.append(term(cx + 95, cy + 44))

    cell(190, 110, "послідовний імпеданс Z", "[A B; C D] = [1  Z;  0  1]", draw_series)
    cell(510, 110, "паралельний адмітанс Y", "[A B; C D] = [1  0;  Y  1]", draw_shunt)
    cell(190, 280, "Г-ланка (L): Z тоді Y", "[1+ZY  Z;  Y  1]", draw_L)
    cell(510, 280, "T-ланка: Z₁, шунт Y, Z₂", "[1+Y·Z₁  …;  Y  1+Y·Z₂]", draw_T)

    body, w0, h0 = textbox(W / 2, H - 26,
                           "Будь-яку пасивну ланку складають із цих цеглинок: перемнож їхні ABCD у порядку проходження сигналу —\n"
                           "і матимеш ABCD усієї ланки. У кожної з них AD − BC = 1: вони взаємні.",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "blocks.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 7. lineage.svg — історія портів: від реципрокності Лоренца до h-стандарту IRE
#     (для hist-вставки: одна нитка крізь десятиліття й країни)
# ════════════════════════════════════════════════════════════════════════════
def fig_lineage():
    W, H = 720, 440
    f = []
    f.append(text(W / 2, 28, "Як визрівала теорія портів: одна нитка крізь півстоліття", size=16, bold=True))

    # вертикальна вісь часу ліворуч
    ax = 150
    top, bot = 70, 388
    f.append(line(ax, top, ax, bot, color=MUTED, sw=2))
    f.append(arrow(ax, bot, ax, bot + 14, color=MUTED, sw=2))

    # віхи: (рік, заголовок, хто/де, колір, заливка)
    events = [
        ("1896", "Реципрокність поля", "Г. Лоренц (нідерландець): корінь взаємності пасивних мереж", FIELD, "#eef7f0"),
        ("1921", "«Vierpol» — чотириполюсник", "Ф. Брайзіг (німець): перша теорія двопортових мереж", POS, "#fdecea"),
        ("1945", "Матриця розсіяння", "В. Белевич (бельгієць рос. роду): n-порти, S-параметри", "#8e44ad", "#f3ecf8"),
        ("1953", "Слово «hybrid»", "Д. Алсберґ: h-параметри для метрології транзисторів", NEG, "#eaf0fd"),
        ("1956", "Стандарт 56 IRE 28.S2", "IRE+AIEE: h-опис — офіційний стандарт; звідси h_FE", INK, "#f4f6f8"),
    ]
    n = len(events)
    span = (bot - top) / (n - 1)
    for i, (yr, title, who, col, fill) in enumerate(events):
        cy = top + i * span
        # вузол на осі
        f.append(circle(ax, cy, 7, fill=fill, stroke=col, sw=2.4))
        # рік ліворуч від осі
        f.append(text(ax - 18, cy + 5, yr, size=13, color=col, bold=True, anchor="end"))
        # картка праворуч
        cardx, cardw = ax + 26, 520
        f.append(line(ax + 7, cy, cardx, cy, color=col, sw=1.6))
        f.append(rect(cardx, cy - 24, cardw, 48, fill=fill, stroke=col, sw=1.8, rx=8))
        f.append(text(cardx + 14, cy - 5, title, size=12, color=col, bold=True, anchor="start"))
        f.append(text(cardx + 14, cy + 15, who, size=10.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "lineage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_blackbox()
    fig_params()
    fig_cascade()
    fig_model()
    fig_recipes()
    fig_blocks()
    fig_lineage()
    print("OK: 7 фігур у", IMG)
