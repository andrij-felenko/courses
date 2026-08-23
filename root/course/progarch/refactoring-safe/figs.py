# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GREEN_TINT = "#eaf7ef"
RED_TINT   = "#fdecea"


def _box(cx, cy, s, **kw):
    return textbox(cx, cy, s, **kw)[0]


# ── 1. Форма інша — поведінка та сама ────────────────────────────────────────
def fig_form_vs_behavior():
    W, H = 860, 430
    p = []

    # ── ліва панель: та сама зовнішня межа, заплутано всередині ──────────────
    p.append(rect(60, 80, 300, 240, fill="#f2fbf5", stroke=FIELD, sw=2.5, rx=10))
    p.append(text(210, 106, "видима поведінка", size=14, bold=True, color=FIELD))

    # заплутана внутрішня будова: кілька безіменних блоків + хаотичні звʼязки
    p.append(rect(96, 150, 78, 32, fill=FILL, stroke=LINE, sw=1.4))
    p.append(rect(250, 158, 74, 32, fill=FILL, stroke=LINE, sw=1.4))
    p.append(rect(150, 230, 96, 32, fill=FILL, stroke=LINE, sw=1.4))
    p.append(line(174, 158, 250, 182, color=MUTED, sw=1.4))   # box1→box2 (вниз)
    p.append(line(250, 166, 174, 176, color=MUTED, sw=1.4))   # box2→box1 (перехрест — «X»)
    p.append(line(287, 190, 205, 230, color=MUTED, sw=1.4))   # box2→box3
    p.append(line(160, 182, 212, 230, color=MUTED, sw=1.4))   # box1→box3
    p.append(text(210, 344, "до — заплутано", size=13, color=MUTED))

    # ── права панель: та сама межа, охайно й названо ─────────────────────────
    p.append(rect(500, 80, 300, 240, fill="#f2fbf5", stroke=FIELD, sw=2.5, rx=10))
    p.append(text(650, 106, "видима поведінка", size=14, bold=True, color=FIELD))
    p.append(_box(650, 158, "ціна рядка", size=13, fill=FILL))
    p.append(_box(650, 204, "знижка", size=13, fill=FILL))
    p.append(_box(650, 250, "сума", size=13, fill=FILL))
    p.append(text(650, 344, "після — названо й розкладено", size=13, color=MUTED))

    # ── стрілка перетворення між панелями ───────────────────────────────────
    p.append(text(430, 176, "рефакторинг", size=13, bold=True))
    p.append(arrow(370, 200, 490, 200))
    p.append(text(430, 224, "форма ≠, поведінка =", size=12, color=MUTED))

    # ── аналогія з математики (унизу, поза панелями) ────────────────────────
    p.append(text(430, 384, "у математиці:  x² + 5x + 6  =  (x + 2)(x + 3)", size=15))
    p.append(text(430, 408, "форма інша — значення те саме на будь-якому x", size=12, color=MUTED))

    return render(os.path.join(OUT, 'form-vs-behavior.svg'), W, H, *p,
                  title="Форма інша — поведінка та сама")


# ── 2. Ритм рефакторингу: зелено → крок → зелено; червоно → крок назад ───────
def _gnode(cx, cy, r=18):
    return circle(cx, cy, r, fill=GREEN_TINT, stroke=FIELD, sw=2) + \
           text(cx, cy + 6, "✓", size=19, color=FIELD, bold=True)


def _rnode(cx, cy, r=18):
    return circle(cx, cy, r, fill=RED_TINT, stroke=POS, sw=2) + \
           text(cx, cy + 6, "✗", size=19, color=POS, bold=True)


def fig_green_to_green():
    W, H = 880, 444
    p = []

    # ── верхня смуга: усе зелено, крок за кроком ─────────────────────────────
    p.append(text(54, 78, "усе зелено — крок за кроком", size=15, bold=True, anchor="start"))
    xs = [110, 320, 530, 740]
    for x in xs:
        p.append(_gnode(x, 150))
        p.append(text(x, 182, "зелено", size=12, color=MUTED))
    moves = [(215, "винести функцію"), (425, "винести знижку"), (635, "спростити цикл")]
    for mx, lab in moves:
        p.append(text(mx, 128, lab, size=12, color=INK))
    for a, b in zip(xs, xs[1:]):
        p.append(arrow(a + 20, 150, b - 20, 150))
    p.append(text(425, 214, "коміт на кожному зелено — точка збереження", size=12, color=MUTED))

    # розділювач
    p.append(line(40, 248, 840, 248, color=MUTED, sw=1, dash="4,6"))

    # ── нижня смуга: щось червоніє — крок назад ──────────────────────────────
    p.append(text(54, 284, "щось червоніє — крок назад", size=15, bold=True, anchor="start"))
    p.append(_gnode(160, 340))
    p.append(text(160, 372, "зелено", size=12, color=MUTED))
    p.append(text(275, 320, "крок", size=12, color=INK))
    p.append(arrow(180, 340, 350, 340))
    p.append(_rnode(370, 340))
    p.append(text(370, 372, "червоно", size=12, color=POS))
    # зворотна стрілка (нижче вузлів, підпис іще нижче)
    p.append(arrow(352, 398, 178, 398))
    p.append(text(265, 420, "відкотити один крок → знову зелено", size=12.5, color=INK))

    return render(os.path.join(OUT, 'green-to-green.svg'), W, H, *p,
                  title="Ритм рефакторингу: зелено → крихітний крок → зелено")


# ── 3. Драбина ходів walkthrough: зелено ×7 → червоний виступ → відкіт ────────
def fig_move_ladder():
    W, H = 900, 606
    p = []
    sx = 150                                   # вертикальна вісь (spine)

    rungs = [
        "Витягнути функцію  amountFor",
        "Перейменувати  ta → amount,  l → line",
        "Витягнути змінну  base,  surcharge",
        "Витягнути функцію  creditsFor",
        "Охоронні речення замість вкладеного if",
        "Розділити цикл на два",
        "Замінити temp запитом  total / credits",
    ]
    ys = [92, 153, 214, 275, 336, 397, 458]

    # стрілки між зеленими вузлами (крок → крок), потім до червоного
    for a, b in zip(ys, ys[1:]):
        p.append(arrow(sx, a + 18, sx, b - 18))
    p.append(arrow(sx, ys[-1] + 18, sx, 520 - 18))

    # зелені вузли й підписи праворуч
    for y, lab in zip(ys, rungs):
        p.append(_gnode(sx, y))
        p.append(text(sx + 34, y + 5, lab, size=13.5, anchor="start"))

    # ── червоний виступ: необачне «спрощення» змінило поведінку ──────────────
    ry = 520
    p.append(_rnode(sx, ry))
    p.append(text(sx + 34, ry - 3, "прибрав Math.max «для чистоти»", size=13, anchor="start", color=POS))
    p.append(text(sx + 34, ry + 16, "бонуси 120 → −50 — червоно", size=12.5, anchor="start", color=MUTED))

    # відкіт — вертикальна стрілка ліворуч від осі, назад до останнього зеленого
    p.append(arrow(124, ry - 6, 124, ys[-1] + 6, color=POS))
    p.append(text(116, (ry + ys[-1]) / 2 + 4, "відкіт", size=12.5, anchor="end", color=POS))

    # ── права колонка: функція тане, 24 → 6 рядків ──────────────────────────
    cx = 792
    p.append(text(cx, 84, "statement", size=13, bold=True))
    p.append(text(cx, 110, "24 рядки", size=13, color=MUTED))
    p.append(arrow(cx, 126, cx, 442, color=MUTED))
    p.append(text(cx, 462, "6 рядків", size=13, color=FIELD, bold=True))
    p.append(text(cx, 486, "тане з кожним ходом", size=11.5, color=MUTED))

    # ── нижній підпис ───────────────────────────────────────────────────────
    p.append(text(W / 2, 576,
                  "Сім дрібних ходів — щоразу зелено. Восьмий змінив поведінку — і винен останній крок: відкотити й переробити чисто.",
                  size=12.5, color=INK))

    return render(os.path.join(OUT, 'move-ladder.svg'), W, H, *p,
                  title="Драбина названих ходів: зелено щоразу, один червоний — і трос тримає")


# ── 4. Хроніка слова «рефакторинг»: дві колиски → наука → інструмент → книга ──
def fig_refactoring_timeline():
    W, H = 1080, 440
    AX = 250                                   # вісь часу
    x0, x1 = 60, 1000
    xs = [100 + i * (860.0 / 7) for i in range(8)]

    AMBER_F, AMBER_S = "#fdf1d6", "#c98a1e"    # мутні витоки: слово вже є, автора нема
    GREEN_F,  GREEN_S = "#eaf7ef", FIELD          # Фаулер виносить у широкий обіг

    ev = [
        dict(side="below", f=AMBER_F, s=AMBER_S, dash=False,
             lines=["1980-ті · Smalltalk", "слово вже в ужитку —", "хто вигадав, невідомо"]),
        dict(side="above", f=AMBER_F, s=AMBER_S, dash=False,
             lines=["1984 · Forth", "«Thinking Forth»", "перша друкована згадка"]),
        dict(side="below", f=FILL, s=LINE, dash=False,
             lines=["1990 · Опдайк, Джонсон", "перша згадка в науці"]),
        dict(side="above", f="#ffffff", s=MUTED, dash=True,
             lines=["1991 · Грізволд", "«restructuring» —", "слова ще нема"]),
        dict(side="below", f=FILL, s=LINE, dash=False,
             lines=["1992 · Опдайк", "дисертація:", "перше глибоке вивчення"]),
        dict(side="above", f=FILL, s=LINE, dash=False,
             lines=["1997 · автоінструмент", "Refactoring Browser", "Брант і Робертс"]),
        dict(side="below", f=GREEN_F, s=GREEN_S, dash=False,
             lines=["1999 · Фаулер", "«Refactoring» (Java)", "у широкий обіг"]),
        dict(side="above", f=GREEN_F, s=GREEN_S, dash=False,
             lines=["2018 · 2-ге видання", "(JavaScript)"]),
    ]

    p = [line(x0, AX, x1, AX, color=MUTED, sw=1.6)]
    dots = []
    for x, e in zip(xs, ev):
        cy = 150 if e["side"] == "above" else 350
        body, w, h = textbox(x, cy, "\n".join(e["lines"]), size=12, pad=9,
                             fill=e["f"], stroke=e["s"], sw=1.6)
        if e["side"] == "above":
            conn = line(x, AX - 8, x, cy + h / 2, color=MUTED, sw=1.3,
                        dash="3,4" if e["dash"] else None)
        else:
            conn = line(x, AX + 8, x, cy - h / 2, color=MUTED, sw=1.3,
                        dash="3,4" if e["dash"] else None)
        p.append(conn)
        p.append(body)
        dots.append(circle(x, AX, 7, fill=e["s"], stroke=e["s"], sw=1))
    p.extend(dots)

    return render(os.path.join(OUT, 'refactoring-timeline.svg'), W, H, *p,
                  title="Хроніка слова «рефакторинг»")


if __name__ == "__main__":
    fig_form_vs_behavior()
    fig_green_to_green()
    fig_move_ladder()
    fig_refactoring_timeline()
    print("ok")
