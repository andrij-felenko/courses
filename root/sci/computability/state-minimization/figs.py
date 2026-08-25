# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_R = "#2457d6"
ORANGE = "#e08a1e"
GREEN  = "#27ae60"
GREY   = "#9aa3af"
TINT = {BLUE_R: "#eaf0fd", ORANGE: "#fdf1e0", GREEN: "#eaf7ee", GREY: "#eef1f4"}


def state(cx, cy, name, r=28, fill=FILL, stroke=LINE, accept=False, sw=2.0):
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw)
    if accept:
        out += circle(cx, cy, r - 5, fill="none", stroke=stroke, sw=sw)
    out += text(cx, cy + 5, name, size=15, color=INK, bold=True)
    return out


def self_loop_left(cx, cy, r, label):
    """Петля з лівого боку вузла (виходить у порожнечу зліва), зі стрілкою назад."""
    x1, y1 = cx - r * 0.82, cy - r * 0.55
    x2, y2 = cx - r * 0.82, cy + r * 0.55
    c1x, c1y = cx - r - 48, cy - 34
    c2x, c2y = cx - r - 48, cy + 34
    path = ('<path d="M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
            % (x1, y1, c1x, c1y, c2x, c2y, x2, y2, LINE))
    path += text(cx - r - 56, cy + 4, label, size=13, color=INK, anchor="end")
    return path


# ── ФІГ.1  Нерозрізнюваність: однакова доля на кожному продовженні → один стан ──
# Ідея фігури: два стани p і q «однакові», якщо для БУДЬ-ЯКОГО дописаного w
# машина з обох закінчує однаково (прийняти/відкинути). Тоді їх можна злити.
def fig_indistinguishable():
    W, H = 880, 330
    p = []
    cols  = ["ε", "a", "ba", "aa", "aba"]
    fates = ["ні", "ні", "ні", "так", "так"]   # однакові для p і q
    xs = [330 + i * 82 for i in range(len(cols))]
    yhead, yp_row, yq_row = 132, 178, 250

    # рамка таблиці випробувань
    p.append(rect(272, 104, 428, 178, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=10))

    # два вихідні стани зліва
    p.append(state(150, yp_row, "p", r=28, stroke=BLUE_R))
    p.append(state(150, yq_row, "q", r=28, stroke=BLUE_R))
    p.append(line(178, yp_row, 272, yp_row, color=GREY, sw=1.0, dash="3 3"))
    p.append(line(178, yq_row, 272, yq_row, color=GREY, sw=1.0, dash="3 3"))

    # заголовок стовпців — дописані рядки w
    p.append(text(288, yhead - 26, "дописуємо w:", size=12, color=MUTED, anchor="start"))
    for x, c in zip(xs, cols):
        p.append(text(x, yhead, c, size=15, color=INK, bold=True))
    p.append(line(280, yhead + 12, 692, yhead + 12, color=MUTED, sw=1.0))

    # два рядки результатів — збігаються клітина в клітину
    for x, f in zip(xs, fates):
        col = GREEN if f == "так" else GREY
        p.append(text(x, yp_row + 5, f, size=14, color=col, bold=True))
        p.append(text(x, yq_row + 5, f, size=14, color=col, bold=True))

    p.append(text(486, 302, "рядки збігаються — та сама доля на кожному продовженні w",
                  size=12, color=MUTED))

    # злиття у один стан
    p.append(text(732, 168, "злити", size=11, color=MUTED))
    p.append(arrow(706, 189, 760, 189, color=INK, sw=2.0))
    p.append(state(812, 189, "{p, q}", r=40, stroke=BLUE_R, fill=TINT[BLUE_R]))
    p.append(text(812, 250, "один стан", size=12, color=MUTED))

    render(os.path.join(OUT, "dfa-indistinguishable.svg"), W, H, *p)


# ── ФІГ.2  Розбивка-уточнення: від поділу «приймальні/ні» до класів ────────────
def fig_partition_refine():
    W, H = 880, 380
    p = []

    def block(x, y, s, color, h=52):
        w = text_width(s, 15, True) + 34
        out = rect(x, y, w, h, fill=TINT[color], stroke=color, sw=2.2, rx=10)
        out += text(x + w / 2, y + h / 2 + 5, s, size=15, color=INK, bold=True)
        return out, w

    def row(y, blocks):
        x = 150
        for s, col in blocks:
            frag, w = block(x, y, s, col)
            p.append(frag)
            x += w + 22
        return x

    rows_y = [70, 190, 310]
    labels = ["P₀", "P₁", "P₂"]
    for ly, lab in zip(rows_y, labels):
        p.append(text(70, ly + 32, lab, size=18, color=INK, bold=True))

    row(rows_y[0], [("1, 2, 3, 4", GREY), ("5", GREEN)])
    row(rows_y[1], [("1, 2", BLUE_R), ("3, 4", ORANGE), ("5", GREEN)])
    row(rows_y[2], [("1, 2", BLUE_R), ("3, 4", ORANGE), ("5", GREEN)])

    # стрілки-переходи між раундами
    p.append(arrow(110, 128, 110, 186, color=MUTED, sw=1.6))
    p.append(arrow(110, 248, 110, 306, color=MUTED, sw=1.6))

    # пояснення праворуч
    p.append(mtext(560, rows_y[0] + 16, ["поділ за прийманням:",
                                          "стан 5 приймальний (F) ≠ решта"],
                   size=12, color=MUTED, anchor="start"))
    p.append(mtext(560, rows_y[1] + 16, ["по «a» стани 3,4 → у блок {5},",
                                          "а 1,2 → ні   ⇒  блок ділиться"],
                   size=12, color=MUTED, anchor="start"))
    p.append(mtext(560, rows_y[2] + 16, ["жоден блок більше не ділиться",
                                          "⇒ розбиття стабільне — це класи"],
                   size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "partition-refine.svg"), W, H, *p)


# ── ФІГ.3  До / після: п'ять станів згортаються у три (мінімальний DFA) ────────
def fig_before_after():
    W, H = 900, 410
    p = []

    # ── зліва: 5 станів у трьох групах (те, що зіллється) ──
    p.append(text(210, 40, "5 станів", size=15, color=INK, bold=True))
    # група A = {1,2}
    p.append(rect(60, 78, 130, 142, fill="none", stroke=BLUE_R, sw=1.8, rx=12))
    p.append(text(125, 70, "0 разів «a»", size=11, color=BLUE_R))
    p.append(state(125, 122, "1", r=24, stroke=BLUE_R))
    p.append(state(125, 180, "2", r=24, stroke=BLUE_R))
    # група B = {3,4}
    p.append(rect(250, 78, 130, 142, fill="none", stroke=ORANGE, sw=1.8, rx=12))
    p.append(text(315, 70, "1 раз «a»", size=11, color=ORANGE))
    p.append(state(315, 122, "3", r=24, stroke=ORANGE))
    p.append(state(315, 180, "4", r=24, stroke=ORANGE))
    # група C = {5}
    p.append(rect(120, 262, 130, 92, fill="none", stroke=GREEN, sw=1.8, rx=12))
    p.append(text(185, 254, "≥ 2 разів «a»", size=11, color=GREEN))
    p.append(state(185, 306, "5", r=24, stroke=GREEN, accept=True))

    # велика стрілка «мінімізація»
    p.append(text(468, 196, "мінімізація", size=13, color=INK, bold=True))
    p.append(arrow(420, 214, 512, 214, color=INK, sw=2.4))

    # ── справа: мінімальний автомат із 3 станів ──
    p.append(text(770, 40, "3 стани", size=15, color=INK, bold=True))
    cx = 612
    yA, yB, yC = 108, 232, 356
    p.append(text(612, 58, "старт", size=11, color=MUTED))
    p.append(arrow(612, 66, 612, 82, color=INK, sw=1.8))

    p.append(state(cx, yA, "{1,2}", r=30, stroke=BLUE_R, fill=TINT[BLUE_R]))
    p.append(state(cx, yB, "{3,4}", r=30, stroke=ORANGE, fill=TINT[ORANGE]))
    p.append(state(cx, yC, "{5}", r=30, stroke=GREEN, fill=TINT[GREEN], accept=True))

    # переходи по «a» (просування)
    p.append(arrow(cx, yA + 32, cx, yB - 32, color=INK, sw=2.0))
    p.append(text(cx + 16, (yA + yB) / 2 + 4, "a", size=14, color=INK, bold=True))
    p.append(arrow(cx, yB + 32, cx, yC - 32, color=INK, sw=2.0))
    p.append(text(cx + 16, (yB + yC) / 2 + 4, "a", size=14, color=INK, bold=True))

    # петлі по «b» (та «a,b» у пастці-прийманні)
    p.append(self_loop_left(cx, yA, 30, "b"))
    p.append(self_loop_left(cx, yB, 30, "b"))
    p.append(self_loop_left(cx, yC, 30, "a, b"))

    # семантичні підписи праворуч
    p.append(text(cx + 46, yA + 4, "0 разів «a»", size=11, color=MUTED, anchor="start"))
    p.append(text(cx + 46, yB + 4, "1 раз «a»", size=11, color=MUTED, anchor="start"))
    p.append(text(cx + 46, yC + 4, "≥ 2 разів «a»", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "minimize-before-after.svg"), W, H, *p)


# ── ФІГ.4  Гопкрофт: спліттер + обернені переходи розколюють блок ──────────────
# Ідея: узявши з черги блок A, дивимось ЛИШЕ на тих, хто по «a» веде в A
# (обернені переходи). Робота — по X, а не по всіх n станах.
def fig_hopcroft_splitter():
    W, H = 900, 420
    p = []

    p.append(text(410, 66, "переходи по символі «a»", size=13, color=MUTED))

    # ── блок Y ліворуч: кандидат на розкол ──
    p.append(rect(70, 85, 200, 190, fill="none", stroke=MUTED, sw=1.8, rx=12))
    p.append(text(170, 76, "блок Y", size=14, color=INK, bold=True))

    ys = [110, 145, 180, 215, 250]
    names = ["y₁", "y₂", "y₃", "y₄", "y₅"]
    # перші три ведуть у A (сині), решта — деінде (сірі)
    cols = [BLUE_R, BLUE_R, BLUE_R, GREY, GREY]
    for cy, nm, col in zip(ys, names, cols):
        p.append(state(170, cy, nm, r=16, stroke=col, fill=TINT[col], sw=1.8))

    # ── блоки-цілі праворуч ──
    p.append(rect(640, 85, 190, 85, fill=TINT[BLUE_R], stroke=BLUE_R, sw=2.2, rx=12))
    p.append(text(735, 76, "спліттер A", size=14, color=BLUE_R, bold=True))
    p.append(state(700, 127, "", r=15, stroke=BLUE_R, fill=BG, sw=1.6))
    p.append(state(770, 127, "", r=15, stroke=BLUE_R, fill=BG, sw=1.6))

    p.append(rect(640, 195, 190, 80, fill="none", stroke=GREY, sw=1.8, rx=12))
    p.append(text(735, 186, "решта блоків", size=13, color=MUTED))
    p.append(state(700, 235, "", r=15, stroke=GREY, fill=BG, sw=1.6))
    p.append(state(770, 235, "", r=15, stroke=GREY, fill=BG, sw=1.6))

    # ── стрілки переходів ──
    targets = [110, 125, 140, 225, 245]
    for cy, ty, col in zip(ys, targets, cols):
        p.append(arrow(188, cy, 635, ty, color=col, sw=1.6))

    # підпис-легенда під блоком Y
    p.append(text(170, 292, "сині ведуть у A — це і є X", size=11, color=BLUE_R))

    # ── роздільник ──
    p.append(line(60, 312, 840, 312, color=MUTED, sw=1.0, dash="4 4"))

    # ── нижній ряд: наслідок розколу ──
    p.append(text(70, 340, "після розколу:", size=13, color=INK,
                  anchor="start", bold=True))

    b1, w1, _ = textbox(268, 380, "Y ∩ X = {y₁, y₂, y₃}\nрозмір 3", size=13,
                        fill=TINT[BLUE_R], stroke=BLUE_R, sw=2.0, color=INK)
    p.append(b1)
    b2, w2, _ = textbox(505, 380, "Y ∖ X = {y₄, y₅}\nрозмір 2", size=13,
                        fill=TINT[GREY], stroke=GREY, sw=2.0, color=INK)
    p.append(b2)

    p.append(arrow(578, 380, 640, 380, color=INK, sw=1.8))
    p.append(mtext(760, 373, ["у чергу — МЕНША", "половина: {y₄, y₅}"],
                   size=12, color=INK, bold=True))

    render(os.path.join(OUT, "hopcroft-splitter.svg"), W, H, *p)


# ── ФІГ.5  Чому log n: блоки зі станом q щоразу вдвічі менші ───────────────────
def fig_hopcroft_halving():
    W, H = 880, 330
    p = []

    p.append(text(440, 42, "блоки зі станом q, які черга взяла на обробку (n = 32)",
                  size=13, color=INK, bold=True))

    # спадні за шириною блоки: 32 → 16 → 8 → 4
    boxes = [(80, 300, "A₁ — 32 стани"), (420, 150, "A₂ — 16"),
             (610, 75, "A₃ — 8"), (725, 38, "A₄ — 4")]
    ytop, bh, ymid = 92, 54, 119
    for x, w, lab in boxes:
        p.append(rect(x, ytop, w, bh, fill=TINT[BLUE_R], stroke=BLUE_R, sw=2.0, rx=8))
        p.append(text(x + w / 2, ytop - 10, lab, size=12, color=BLUE_R, bold=True))
        p.append(circle(x + w / 2, ymid, 6, fill=INK, stroke=INK, sw=1.0))
    p.append(text(230, 168, "q", size=13, color=INK, bold=True, italic=True))

    # стрілки між блоками
    for x1, x2 in ((380, 420), (570, 610), (685, 725)):
        p.append(arrow(x1, ymid, x2, ymid, color=MUTED, sw=1.6))

    p.append(mtext(440, 212,
                   ["коли блок зі станом q розколюється, у чергу йде МЕНША половина —",
                    "тож наступний блок зі станом q, що дійде до обробки, удвічі менший"],
                   size=12, color=MUTED))

    box, _, _ = textbox(440, 282, "⇒ кожен стан потрапляє у спліттер щонайбільше log₂n + 1 разів",
                        size=13, fill=TINT[GREEN], stroke=GREEN, sw=2.0, color=INK, bold=True)
    p.append(box)

    render(os.path.join(OUT, "hopcroft-halving.svg"), W, H, *p)


# ── ФІГ.6 (вставка hist-) Збіг незалежних відкриттів ──────────────────────────
# Ідея фігури: інженер, математик і двоє логіків ішли РІЗНИМИ дорогами й різними
# словами — і вперлися в одне й те саме відношення. Праворуч — те, що з ним
# зробили далі: інакше (Бжозовський) і швидше (Гопкрофт).
def fig_hist_confluence():
    W, H = 1110, 560
    p = []

    def card(x, y, w, h, head, body, color):
        out = rect(x, y, w, h, fill=TINT[color], stroke=color, sw=2.0, rx=10)
        cx = x + w / 2
        out += text(cx, y + 27, head, size=14, color=INK, bold=True)
        out += mtext(cx, y + 52, body, size=12, color=MUTED, lh=1.35)
        return out

    LX, LW, LH = 30, 290, 100
    RX, RW, RH = 780, 300, 120

    # заголовки колонок
    p.append(text(LX + LW / 2, 34, "витоки: незалежно, різними словами",
                  size=13, color=INK, bold=True))
    p.append(text(570, 34, "що саме вони знайшли", size=13, color=INK, bold=True))
    p.append(text(RX + RW / 2, 34, "далі: інакше й швидше", size=13, color=INK, bold=True))

    origins = [
        (60,  "Девід Гаффман · 1954",
         ["інженер, асинхронні схеми:", "злиття рядків таблиці потоків"], ORANGE),
        (180, "Едвард Мур · 1956",
         ["математик, «чорна скринька»:", "зведена форма машини"], BLUE_R),
        (300, "Джон Майгілл · 1957",
         ["логік: конгруенція", "скінченного індексу"], GREEN),
        (420, "Аніл Нероуд · 1958",
         ["математик: право-інваріантна", "рівноцінність"], GREY),
    ]
    for y, head, body, col in origins:
        p.append(card(LX, y, LW, LH, head, body, col))
        p.append(arrow(LX + LW + 6, y + LH / 2, 444, 290, color=MUTED, sw=1.5))

    # центр — те саме відношення
    p.append(rect(450, 220, 240, 140, fill="#fbfcfd", stroke=INK, sw=2.4, rx=12))
    p.append(text(570, 252, "одне відношення", size=14, color=INK, bold=True))
    p.append(mtext(570, 282, ["p ~ q  ⟺  жоден", "дописаний хвіст w", "не розрізняє",
                              "їхньої долі"], size=12, color=MUTED, lh=1.4))

    # праворуч — що з ним зробили далі
    p.append(card(RX, 150, RW, RH, "Януш Бжозовський · 1962",
                  ["а якщо зовсім інакше?", "подвійний реверс:",
                   "оберни · здетермінуй · двічі"], ORANGE))
    p.append(card(RX, 370, RW, RH, "Джон Гопкрофт · 1971",
                  ["а якщо швидше?", "O(n·log n) замість O(n²):",
                   "«обробляй меншу половину»"], BLUE_R))
    p.append(arrow(696, 268, 774, 212, color=MUTED, sw=1.5))
    p.append(arrow(696, 312, 774, 428, color=MUTED, sw=1.5))

    render(os.path.join(OUT, "hist-confluence.svg"), W, H, *p)


# ── ФІГ.7 (вставка math-) Майбутнє префікса: три різні майбутні → три класи ────
# Ідея: для мови «≥ 2 літери a» усе, що важить про прочитаний префікс, —
# множина продовжень, які доводять до приймання. Різних таких множин рівно три.
def fig_mn_futures():
    W, H = 1010, 392
    p = []
    xA, wA = 56, 236
    xC, wC = 352, 348
    xD, wD = 764, 190
    h = 64
    rows = [
        ("ε,  b,  bb,  bbb",     "{ z : у z ≥ 2 «a» }",        "[ε] — ще нема «a»",      BLUE_R),
        ("a,  ba,  ab,  abb",    "{ z : у z ≥ 1 «a» }",        "[a] — одна «a» вже є",   ORANGE),
        ("aa,  aab,  aba,  baa", "Σ*  — годиться будь-який z", "[aa] — дві «a», кінець", GREEN),
    ]
    ys = [128, 212, 296]

    p.append(text(xA + wA / 2, 58, "префікс x", size=13, color=MUTED))
    p.append(text(xC + wC / 2, 58, "майбутнє  x⁻¹L = { z : xz ∈ L }", size=13, color=MUTED))
    p.append(text(xD + wD / 2, 58, "клас", size=13, color=MUTED))
    p.append(line(xA, 72, xD + wD, 72, color=MUTED, sw=1.0))

    for (pre, fut, cls, col), y in zip(rows, ys):
        p.append(fitbox(xA, y - h / 2, wA, h, pre, size=15,
                        fill=TINT[col], stroke=col, sw=2.0, rx=10, bold=True))
        p.append(arrow(xA + wA + 8, y, xC - 8, y, color=MUTED, sw=1.6))
        p.append(fitbox(xC, y - h / 2, wC, h, fut, size=14,
                        fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=10))
        p.append(arrow(xC + wC + 8, y, xD - 8, y, color=MUTED, sw=1.6))
        p.append(fitbox(xD, y - h / 2, wD, h, cls, size=12,
                        fill=TINT[col], stroke=col, sw=2.0, rx=10))

    p.append(mtext(W / 2, 350, ["Три різні майбутні — рівно три класи.",
                                "Різні майбутні мусять сидіти в різних станах, однакові — в одному."],
                   size=12, color=MUTED))
    render(os.path.join(OUT, "mn-futures.svg"), W, H, *p)


# ── ФІГ.8 (вставка math-) Два відображення: рядки → стани → класи ──────────────
# Ідея: ψ веде рядок у стан, φ веде стан у клас; φ завжди сюр'єктивне, тому
# станів не буває менше, ніж класів. Дві марноти видно просто оком: недосяжний
# стан (у ψ нема образу) і пара, яку φ склеює в один клас (нерозрізнювані).
def fig_mn_two_maps():
    W, H = 1060, 500
    p = []
    z1x, z1w = 56, 200
    z2x, z2w = 400, 240
    z3x, z3w = 790, 214
    zy, zh = 120, 320

    for zx, zw in [(z1x, z1w), (z2x, z2w), (z3x, z3w)]:
        p.append(rect(zx, zy, zw, zh, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=12))

    for cx, t1, t2 in [(z1x + z1w / 2, "Σ* — усі рядки", "(нескінченно багато)"),
                       (z2x + z2w / 2, "Q — стани DFA", "(будь-якого для L)"),
                       (z3x + z3w / 2, "класи ≡ₗ", "(властивість МОВИ)")]:
        p.append(text(cx, 76, t1, size=14, color=INK, bold=True))
        p.append(text(cx, 96, t2, size=11, color=MUTED))

    strs = [("ε", BLUE_R), ("b", BLUE_R), ("bb", BLUE_R),
            ("a", ORANGE), ("ab", ORANGE), ("ba", ORANGE),
            ("aa", GREEN), ("aba", GREEN), ("…", MUTED)]
    for i, (s, col) in enumerate(strs):
        p.append(text(z1x + z1w / 2, 160 + i * 32, s, size=15, color=col, bold=True))

    qx = z2x + z2w / 2
    for y, name, col, acc in [(168, "q₁", BLUE_R, False), (228, "q₂", BLUE_R, False),
                              (290, "q₃", ORANGE, False), (350, "q₄", GREEN, True),
                              (410, "q₅", GREY, False)]:
        p.append(state(qx, y, name, r=24, stroke=col, fill=TINT[col], accept=acc, sw=2.0))
    p.append(text(qx - 32, 414, "недосяжний", size=11, color=GREY, anchor="end"))

    for cy, s, col in [(198, "[ε] — рядки без «a»", BLUE_R),
                       (290, "[a] — рядки з однією «a»", ORANGE),
                       (382, "[aa] — рядки з ≥ 2 «a»", GREEN)]:
        p.append(fitbox(z3x, cy - 28, z3w, 56, s, size=12,
                        fill=TINT[col], stroke=col, sw=2.0, rx=10))

    # ψ — рядок веде машину в стан
    p.append(mtext((z1x + z1w + z2x) / 2, 246,
                   ["ψ:  x ↦ δ*(q₀, x)", "куди рядок", "приводить машину"],
                   size=11, color=INK))
    p.append(arrow(z1x + z1w + 10, 300, z2x - 10, 300, color=INK, sw=2.4))

    # φ — стан веде у клас рядків, що в нього приводять
    for y1, y2 in [(172, 194), (224, 202), (290, 290), (356, 378)]:
        p.append(arrow(qx + 26, y1, z3x - 4, y2, color=MUTED, sw=1.6))
    gap = (z2x + z2w + z3x) / 2
    p.append(text(gap, 150, "два стани — один клас", size=11, color=MUTED))
    p.append(text(gap, 424, "φ:  стан ↦ його клас", size=11, color=INK))

    p.append(text(W / 2, 470,
                  "φ завжди НА: кожен клас хтось займає ⇒ станів не менше, ніж класів",
                  size=13, color=INK, bold=True))
    render(os.path.join(OUT, "mn-two-maps.svg"), W, H, *p)


# ── ФІГ.9 (вставка math-) Набір-обманка: 2ⁿ рядків попарно розрізнимі ──────────
# Ідея: дописування z = 0ⁱ⁻¹ підсовує ту саму позицію, де два рядки різняться,
# точно під приціл мови «n-й символ з кінця» — і тим їх розводить.
def fig_mn_fooling():
    W, H = 960, 500
    p = []

    def bitrow(x0, y, bits, hi=None, hi_col=GREEN, bw=42, gap=4):
        out = ""
        for i, b in enumerate(bits):
            x = x0 + i * (bw + gap)
            f = TINT[hi_col] if (hi is not None and i == hi) else FILL
            out += rect(x, y, bw, bw, fill=f, stroke=MUTED, sw=1.4, rx=5)
            out += text(x + bw / 2, y + bw / 2 + 6, b, size=17, color=INK, bold=True)
        return out

    p.append(text(W / 2, 46, "L₄ = { w : 4-й символ з кінця — це «1» }",
                  size=15, color=INK, bold=True))

    # ── два різні 4-бітові рядки ──
    p.append(text(150, 133, "u =", size=15, color=INK, bold=True, anchor="end"))
    p.append(bitrow(170, 106, "1011"))
    p.append(text(150, 195, "v =", size=15, color=INK, bold=True, anchor="end"))
    p.append(bitrow(170, 168, "1111"))
    p.append(rect(212, 98, 50, 116, fill="none", stroke=POS, sw=2.2, rx=6))
    p.append(text(237, 90, "різні тут — позиція 2", size=11, color=POS))
    p.append(mtext(560, 128, ["два різні 4-бітові рядки",
                              "десь мусять різнитися —",
                              "хай у позиції i = 2"], size=12, color=MUTED, anchor="start"))

    # ── дописуємо z ──
    p.append(arrow(237, 226, 237, 262, color=INK, sw=2.0))
    p.append(text(258, 250, "дописуємо z = 0ⁱ⁻¹ = 0", size=12, color=INK, anchor="start"))

    # ── позиція розходження заїхала точно у вікно «4-й з кінця» ──
    p.append(text(150, 325, "uz =", size=15, color=INK, bold=True, anchor="end"))
    p.append(bitrow(170, 298, "10110", hi=1))
    p.append(text(150, 387, "vz =", size=15, color=INK, bold=True, anchor="end"))
    p.append(bitrow(170, 360, "11110", hi=1))
    p.append(rect(212, 290, 50, 116, fill="none", stroke=GREEN, sw=2.2, rx=6))
    p.append(text(237, 282, "4-й з кінця", size=11, color=GREEN, bold=True))

    # лінійка «рахуємо з кінця»
    p.append(arrow(396, 420, 232, 420, color=MUTED, sw=1.2))
    for cx, lab in [(375, "1"), (329, "2"), (283, "3"), (237, "4")]:
        p.append(text(cx, 438, lab, size=10, color=MUTED))
    p.append(text(420, 424, "рахуємо з кінця", size=10, color=MUTED, anchor="start"))

    p.append(mtext(560, 308, ["uz: у вікні «0»  ⇒  uz ∉ L₄",
                              "vz: у вікні «1»  ⇒  vz ∈ L₄"],
                   size=12, color=INK, anchor="start"))
    p.append(text(560, 364, "отже z розрізняє u і v", size=12, color=POS,
                  bold=True, anchor="start"))

    p.append(text(W / 2, 478,
                  "усі 16 чотирибітових рядків попарно розрізнимі ⇒ будь-який DFA для L₄ має ≥ 16 станів",
                  size=12, color=MUTED))
    render(os.path.join(OUT, "mn-fooling.svg"), W, H, *p)


if __name__ == "__main__":
    fig_indistinguishable()
    fig_partition_refine()
    fig_before_after()
    fig_hopcroft_splitter()
    fig_hopcroft_halving()
    fig_hist_confluence()
    fig_mn_futures()
    fig_mn_two_maps()
    fig_mn_fooling()
    print("figs OK:", os.listdir(OUT))
