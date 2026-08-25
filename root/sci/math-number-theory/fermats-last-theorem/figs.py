# -*- coding: utf-8 -*-
"""Фігури до статті «Велика теорема Ферма». Запуск із теки теми: python figs.py
Виводить SVG у ./img/. Розкладку тримаємо з запасом — текст не накладається."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: два режими рівняння (n=2 заселений ↔ n≥3 порожній) ─────────────
def fig_regimes():
    W, H = 760, 380
    f = []
    # панелі
    f.append(rect(25, 50, 330, 300, fill="#f2faf4", stroke=FIELD, sw=2))
    f.append(rect(405, 50, 330, 300, fill="#fdf4f3", stroke=POS, sw=2))
    # роздільник
    f.append(line(380, 60, 380, 340, color=MUTED, sw=1.5, dash="5,6"))

    # ── ліва панель: показник 2, безліч розв'язків ──
    f.append(text(190, 84, "a² + b² = c²", size=19, bold=True))
    f.append(text(190, 108, "показник 2 — безліч розв'язків", size=13, color=FIELD, bold=True))
    for i, eq in enumerate(["3² + 4² = 5²",
                            "5² + 12² = 13²",
                            "8² + 15² = 17²",
                            "20² + 21² = 29²"]):
        f.append(text(190, 150 + i * 30, eq, size=16, color=INK))
    f.append(text(190, 150 + 4 * 30 + 6, "…  трійок без кінця", size=14,
                  color=FIELD, italic=True))

    # ── права панель: показник ≥3, порожньо ──
    f.append(text(570, 84, "aⁿ + bⁿ = cⁿ,   n ≥ 3", size=19, bold=True))
    f.append(text(570, 108, "жодного розв'язку", size=13, color=POS, bold=True))
    f.append(text(570, 205, "∅", size=86, color="#e3b8b3", bold=True))
    b, bw, bh = textbox(570, 300, "6³ + 8³ = 728\n9³ = 729  —  бракує 1",
                        size=15, pad=12, fill="#ffffff", stroke=POS, sw=1.6)
    f.append(b)
    render(os.path.join(IMG, "regimes.svg"), W, H, *f)


# ── Фігура 2: 358-річна облога (вертикальна шкала подій) ─────────────────────
def fig_timeline():
    W, H = 780, 760
    axis_x = 388
    f = []
    f.append(line(axis_x, 55, axis_x, 705, color=LINE, sw=2.5))

    # (рік+підпис, сторона): справа = 'r', зліва = 'l'
    events = [
        (70,  "1637",   "Ферма — напис на полях «Арифметики»", 'r'),
        (134, "1770",   "Ойлер — показник 3", 'l'),
        (198, "1820-ті", "Жермен — перший випадок, клас простих", 'r'),
        (262, "1825",   "Діріхле, Лежандр — показник 5", 'l'),
        (326, "1839",   "Ламе — показник 7", 'r'),
        (390, "1847",   "Куммер — усі регулярні прості", 'l'),
    ]
    modern = [
        (500, "1984", "Фрай — крива з гаданого розв'язку", 'r'),
        (564, "1986", "Рібет — крива Фрая не модулярна", 'l'),
        (628, "1995", "Вайлз і Тейлор — доведено", 'r'),
    ]

    def place(y, year, desc, side, accent=INK):
        out = [circle(axis_x, y, 6, fill=accent, stroke=accent, sw=1)]
        b, bw, bh = textbox(0, 0, year + "\n" + desc, size=13.5, pad=10,
                            fill=FILL, stroke=accent, sw=1.6)
        # перерахувати позицію центру, знаючи ширину
        if side == 'r':
            cx = axis_x + 34 + bw / 2
            edge = axis_x + 34
        else:
            cx = axis_x - 34 - bw / 2
            edge = axis_x - 34
        b, bw, bh = textbox(cx, y, year + "\n" + desc, size=13.5, pad=10,
                            fill=FILL, stroke=accent, sw=1.6)
        out.append(line(axis_x, y, edge, y, color=MUTED, sw=1.4))
        out.append(b)
        return out

    for y, year, desc, side in events:
        f += place(y, year, desc, side)

    # смуга розриву — ≈137 років тиші
    f.append(line(axis_x - 16, 430, axis_x + 16, 418, color=MUTED, sw=2))
    f.append(line(axis_x - 16, 452, axis_x + 16, 440, color=MUTED, sw=2))
    f.append(text(axis_x, 480, "≈ 137 років — жодного нового показника",
                  size=13, color=MUTED, italic=True))

    for y, year, desc, side in modern:
        f += place(y, year, desc, side, accent=FIELD)

    f.append(text(axis_x, 735, "358 років облоги", size=15, bold=True, color=INK))
    render(os.path.join(IMG, "timeline.svg"), W, H, *f)


# ── Фігура 3: логічний ланцюг доведення Вайлза ──────────────────────────────
def fig_modern_proof():
    W, H = 820, 500
    f = []

    a, aw, ah = textbox(410, 66,
                        "Припущений розв'язок   aᵖ + bᵖ = cᵖ",
                        size=15, pad=13, fill="#fdf4f3", stroke=POS, sw=2, bold=True)
    b, bw, bh = textbox(410, 176,
                        "Крива Фрая:  y² = x (x − aᵖ)(x + bᵖ)",
                        size=15, pad=13, fill=FILL, stroke=INK, sw=1.8)
    c, cw, ch = textbox(210, 306,
                        "НЕ модулярна\n(Рібет, 1986)",
                        size=14, pad=12, fill=FILL, stroke=INK, sw=1.8)
    d, dw, dh = textbox(610, 306,
                        "мусить бути модулярною\n(модулярність — Вайлз)",
                        size=14, pad=12, fill=FILL, stroke=INK, sw=1.8)
    e, ew, eh = textbox(410, 436,
                        "Суперечність  ⇒  розв'язку немає",
                        size=15, pad=13, fill="#f2faf4", stroke=FIELD, sw=2, bold=True)
    f += [a, b, c, d, e]

    f.append(arrow(410, 66 + ah / 2, 410, 176 - bh / 2))
    f.append(text(430, 128, "Фрай", size=12.5, color=MUTED, anchor="start", italic=True))
    f.append(arrow(410 - 60, 176 + bh / 2, 210 + 40, 306 - ch / 2))
    f.append(arrow(410 + 60, 176 + bh / 2, 610 - 40, 306 - ch / 2))
    f.append(arrow(210, 306 + ch / 2, 410 - 70, 436 - eh / 2))
    f.append(arrow(610, 306 + ch / 2, 410 + 70, 436 - eh / 2))
    render(os.path.join(IMG, "modern-proof.svg"), W, H, *f)


# ── Фігура 4 (вставка math-descent-n4): рушій спуску для показника чотири ────
def fig_descent():
    W, H = 880, 662
    cx = 440
    f = []

    # верх — гаданий мінімальний розв'язок (червоний: припущення)
    t, tw, th = textbox(cx, 58,
                        "(x, y, z):   x⁴ + y⁴ = z²\nz — найменше,   gcd(x, y) = 1",
                        size=15, pad=13, fill="#fdf4f3", stroke=POS, sw=2, bold=True)
    # примітивна трійка Піфагора №1
    p, pw, ph = textbox(cx, 178,
                        "(x²)² + (y²)² = z²   —   примітивна трійка\n"
                        "x² = p² − q²,    y² = 2pq,    z = p² + q²",
                        size=14, pad=12, fill=FILL, stroke=INK, sw=1.8)
    # ліва гілка — непарний катет дає внутрішню трійку
    ax, ay = 235, 322
    a, aw, ah = textbox(ax, ay,
                        "x² + q² = p²   —   знову трійка\n"
                        "x = m² − n²,   q = 2mn,   p = m² + n²",
                        size=13, pad=11, fill=FILL, stroke=INK, sw=1.6)
    # права гілка — парний катет дає добуток-квадрат
    bx, by = 648, 322
    b, bw, bh = textbox(bx, by,
                        "y² = 4·m·n·p,   попарно прості\n"
                        "⇒   m = a²,   n = b²,   p = c²",
                        size=13, pad=11, fill=FILL, stroke=INK, sw=1.6)
    # злиття — новий розв'язок (зелений: висновок)
    e, ew, eh = textbox(cx, 478,
                        "p = m² + n²   ⇒   c² = a⁴ + b⁴\n"
                        "(a, b, c):   a⁴ + b⁴ = c²,   c < z",
                        size=15, pad=13, fill="#f2faf4", stroke=FIELD, sw=2, bold=True)
    # низ — ланцюг спуску
    ch, chw, chh = textbox(cx, 594,
                           "z > c > c′ > c″ > …   у додатних цілих неможливо",
                           size=13, pad=11, fill="#ffffff", stroke=MUTED, sw=1.4, color=MUTED)
    f += [t, p, a, b, e, ch]

    # стрілки потоку
    f.append(arrow(cx, 58 + th / 2, cx, 178 - ph / 2))
    f.append(arrow(cx - 78, 178 + ph / 2, ax + 44, ay - ah / 2))
    f.append(arrow(cx + 78, 178 + ph / 2, bx - 44, by - bh / 2))
    f.append(arrow(ax + 44, ay + ah / 2, cx - 78, 478 - eh / 2))
    f.append(arrow(bx - 44, by + bh / 2, cx + 78, 478 - eh / 2))
    f.append(arrow(cx, 478 + eh / 2, cx, 594 - chh / 2))

    render(os.path.join(IMG, "descent.svg"), W, H, *f)


# ── Фігура 5 (вставка hist-margin-to-wiles): останні два роки Вайлза ─────────
def fig_wiles_two_years():
    W, H = 960, 450
    ax_y = 225
    f = []
    # вісь часу
    f.append(line(60, ax_y, 890, ax_y, color=LINE, sw=2.5))
    f.append(text(66, ax_y - 12, "червень 1993", size=11, color=MUTED,
                  anchor="start", italic=True))
    f.append(text(884, ax_y - 12, "1995", size=11, color=MUTED,
                  anchor="end", italic=True))

    def node(x, above, txt, accent):
        cy = 120 if above else 330
        b, bw, bh = textbox(x, cy, txt, size=13, pad=11, fill=FILL,
                            stroke=accent, sw=1.8)
        edge = cy + bh / 2 if above else cy - bh / 2
        return [line(x, ax_y, x, edge, color=MUTED, sw=1.4),
                circle(x, ax_y, 6, fill=accent, stroke=accent, sw=1), b]

    f += node(175, True,  "23 червня 1993\nтри лекції в Кембриджі\n«гадаю, на цьому спинюся»", FIELD)
    f += node(435, False, "серпень 1993\nзвіряння виявляє прогалину\nметод Колівагіна–Флаха", POS)
    f += node(660, True,  "19 вересня 1994\nосяяння — разом із Тейлором\nпокинутий підхід рятує", FIELD)
    f += node(845, False, "травень 1995\nдві статті\nв Annals of Mathematics", INK)

    # смуга «рік у долині» між прогалиною і порятунком
    f.append(line(470, ax_y, 630, ax_y, color=POS, sw=5))
    f.append(text(550, ax_y - 13, "≈ рік у пошуках виходу", size=12,
                  color=MUTED, italic=True))
    render(os.path.join(IMG, "wiles-two-years.svg"), W, H, *f,
           title="Останні два роки теореми")


# ── Фігура 6 (вставка proj-search-and-near-misses): промахи, що дурять калькулятор ─
def fig_near_miss():
    W, H = 760, 320
    MONO = "'DejaVu Sans Mono','Consolas',monospace"
    x0 = 92
    f = []

    def drow(y, digits, k, pitch, size):
        out = []
        for i, ch in enumerate(digits):
            col = FIELD if i < k else (POS if i == k else MUTED)
            cx = x0 + i * pitch + pitch / 2
            out.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%.1f" '
                       'fill="%s" text-anchor="middle">%s</text>'
                       % (cx, y, MONO, size, col, esc(ch)))
        return "".join(out)

    f.append(text(W / 2, 26,
                  "Тісні промахи: калькулятор бачить лише зелений початок — і каже «рівно»",
                  size=13.5, bold=True))

    cases = [
        ("1782¹² + 1841¹²   проти   1922¹²",
         "2541210258614589176288669958142428526657",
         "2541210259314801410819278649643651567616", 9,
         "40 цифр — збігаються перші 9, далі 1922¹² трохи більше"),
        ("3987¹² + 4365¹²   проти   4472¹²",
         "63976656349698612616236230953154487896987106",
         "63976656348486725806862358322168575784124416", 10,
         "44 цифри — збігаються перші 10, далі сума трохи більша"),
    ]
    bases = [62, 196]
    for (label, L, Rr, k, note), base in zip(cases, bases):
        n = len(L)
        pitch = (W - x0 - 24) / n
        size = min(14.0, pitch * 0.95)
        f.append(text(W / 2, base, label, size=15, bold=True))
        yL, yR = base + 34, base + 60
        f.append(rect(x0 - 3, yL - 19, k * pitch + 6, 52, fill="#e9f8ef",
                      stroke=FIELD, sw=1.4, rx=4))
        sx = x0 + k * pitch
        f.append(line(sx, yL - 21, sx, yR + 11, color=POS, sw=1.4, dash="3,4"))
        f.append(drow(yL, L, k, pitch, size))
        f.append(drow(yR, Rr, k, pitch, size))
        f.append(text(x0 - 12, yL + 5, "aⁿ+bⁿ", size=12, color=MUTED, anchor="end"))
        f.append(text(x0 - 12, yR + 5, "= cⁿ", size=12, color=MUTED, anchor="end"))
        f.append(text(W / 2, base + 86, note, size=12.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "near-miss.svg"), W, H, *f)


if __name__ == "__main__":
    fig_regimes()
    fig_timeline()
    fig_modern_proof()
    fig_descent()
    fig_wiles_two_years()
    fig_near_miss()
    print("OK: regimes, timeline, modern-proof, descent, wiles-two-years, near-miss ->", IMG)
