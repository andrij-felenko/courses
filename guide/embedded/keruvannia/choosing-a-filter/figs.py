# -*- coding: utf-8 -*-
"""Фігури до теми «Вибір фільтра».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math, random

# Локальні відтінки понад палітру svgkit (медіана — фіолетова лінія)
MED = "#8e44ad"      # медіана
GOLD = "#b9770e"     # калібрування / дрейф (тепле, але читабельне)


# ── 1. Дерево рішення: спершу діагноз, тоді фільтр ───────────────────────────
def fig_decision_tree():
    W, H = 760, 410
    f = [text(W / 2, 26, "Спершу діагноз, тоді фільтр", size=15, bold=True)]

    # корінь
    f.append(rect(24, 168, 156, 64, fill=FILL, stroke=INK, sw=2))
    f.append(text(102, 194, "сирий потік:", size=12, bold=True))
    f.append(text(102, 213, "який характер?", size=12, bold=True))

    # гілка 1: дрейф → калібрування
    f.append(line(180, 196, 250, 70, color=GOLD, sw=1.8))
    f.append(text(196, 110, "повзе?", size=10.5, color=MUTED, anchor="start", italic=True))
    f.append(rect(250, 46, 230, 50, fill=FILL, stroke=GOLD, sw=1.8))
    f.append(text(365, 68, "дрейф → калібрування", size=12.5, color=GOLD, bold=True))
    f.append(text(365, 85, "не фільтр!", size=10, color=MUTED, italic=True))

    # гілка 2: викиди → медіана
    f.append(line(180, 200, 250, 196, color=MED, sw=1.8))
    f.append(text(196, 182, "голки?", size=10.5, color=MUTED, anchor="start", italic=True))
    f.append(rect(250, 172, 230, 50, fill=FILL, stroke=MED, sw=1.8))
    f.append(text(365, 194, "викиди → медіана", size=12.5, color=MED, bold=True))
    f.append(text(365, 211, "вибиває голки", size=10, color=MUTED, italic=True))

    # гілка 3: шум → усереднення
    f.append(line(180, 204, 250, 322, color=NEG, sw=1.8))
    f.append(text(196, 300, "тремтить?", size=10.5, color=MUTED, anchor="start", italic=True))
    f.append(rect(250, 298, 230, 50, fill=FILL, stroke=NEG, sw=1.8))
    f.append(text(365, 320, "шум → усереднення", size=12.5, color=NEG, bold=True))
    f.append(text(365, 337, "EMA / ковзне середнє", size=10, color=MUTED, italic=True))

    # розгалуження усереднення на EMA / ковзне
    f.append(arrow(480, 318, 540, 290, color=NEG, sw=1.6))
    f.append(rect(540, 270, 208, 40, fill=BG, stroke=NEG, sw=1.5))
    f.append(text(644, 287, "EMA", size=12, color=NEG, bold=True))
    f.append(text(644, 302, "ресурси тиснуть · багато каналів", size=9, color=MUTED, italic=True))
    f.append(arrow(480, 326, 540, 354, color=FIELD, sw=1.6))
    f.append(rect(540, 334, 208, 40, fill=BG, stroke=FIELD, sw=1.5))
    f.append(text(644, 351, "ковзне середнє", size=12, color=FIELD, bold=True))
    f.append(text(644, 366, "лінійна фаза · нуль на 50 Гц", size=9, color=MUTED, italic=True))

    f.append(text(W / 2, 398,
                  "діагноз економить більше часу, ніж будь-який вибір алгоритму",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "decision-tree.svg"), W, H, *f)


# ── 2. Три фільтри за критеріями: таблиця ────────────────────────────────────
def fig_compare_table():
    W, H = 720, 432
    f = [text(W / 2, 26, "Три фільтри за критеріями вибору", size=15, bold=True)]

    cols = [("Ковзне\nсереднє", 365, FIELD), ("Медіана", 495, MED), ("EMA", 625, NEG)]
    for name, cx, col in cols:
        lines = name.split("\n")
        f.append(rect(cx - 58, 44, 116, 38, fill=FILL, stroke=col, sw=1.6))
        ty = 62 if len(lines) == 1 else 58
        f.append(mtext(cx, ty, lines, size=12, color=col, bold=True))

    rows = [
        ("Гладить дрібний шум",    "++", "~",  "++"),
        ("Вбиває викиди",          "x",  "++", "x"),
        ("Береже різкий край",     "x",  "+",  "~"),
        ("Лінійна фаза",           "+",  "x",  "x"),
        ("Прицільні нулі частот",  "+",  "x",  "x"),
        ("Мала пам'ять",           "x N", "x N", "++ 1"),
        ("Дешеві обчислення",      "+",  "x сорт", "++"),
        ("Передбачувана затримка", "+",  "~",  "+"),
    ]
    glyph = {"+": ("✓", FIELD), "++": ("✓✓", FIELD), "x": ("✗", POS), "~": ("~", GOLD)}

    def cell(v):
        # перша лексема — символ оцінки, решта (N, сорт, 1) — підпис тим же кольором
        head = v.split(" ")[0]
        sym, col = glyph.get(head, (v, INK))
        rest = v[len(head):]
        return (sym + rest), col

    y = 86
    for i, (label, a, b, c) in enumerate(rows):
        if i % 2 == 0:
            f.append(rect(16, y, 688, 34, fill="#f6f6f8", stroke="none", sw=0, rx=4))
        f.append(text(28, y + 22, label, size=12, anchor="start"))
        for v, cx in ((a, 365), (b, 495), (c, 625)):
            txt, col = cell(v)
            f.append(text(cx, y + 23, txt, size=13.5, color=col, bold=True))
        y += 38

    f.append(text(W / 2, 420,
                  "немає універсального переможця — кожен сильний у своєму",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "compare-table.svg"), W, H, *f)


# ── 3. Готові рецепти під ситуацію ───────────────────────────────────────────
def fig_recipes():
    W, H = 720, 250
    f = [text(W / 2, 26, "Готові рецепти під типову ситуацію", size=15, bold=True)]

    cards = [
        ("Повільне довкілля", "EMA, мала α", "темп., вологість, світло", FIELD),
        ("Далекомір із привидами", "медіана(3) → EMA", "ультразвук, лазер", MED),
        ("Вхід у керування", "легкий фільтр", "свіжість понад чистоту", NEG),
        ("Поріг / край", "медіана / гістерезис", "не згладжувати край!", GOLD),
    ]
    x = 14
    for title_, recipe, note, col in cards:
        f.append(rect(x, 52, 168, 170, fill=FILL, stroke=col, sw=1.6))
        f.append(fitbox(x + 8, 60, 152, 34, title_, size=12, color=col, bold=True,
                        fill=FILL, stroke="none", sw=0))
        f.append(line(x + 16, 100, x + 152, 100, color="#dddddd", sw=1.2))
        f.append(fitbox(x + 8, 132, 152, 28, recipe, size=12.5, color=INK, bold=True,
                        fill=BG, stroke="none", sw=0))
        f.append(text(x + 84, 196, note, size=9.5, color=MUTED, italic=True))
        x += 176

    f.append(text(W / 2, 244,
                  "діагноз → рецепт: більшість задач лягають у ці чотири шаблони",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "recipes.svg"), W, H, *f)


# ── 4. Зв'язка за замовчуванням: сирий → медіана(3) → EMA ────────────────────
def _stream_panel(f, x, y, w, h, color, label, note, pts):
    f.append(rect(x, y, w, h, fill="#fcfcfd", stroke="#e6e6ea", sw=1.4))
    f.append(text(x + w / 2, y + 22, label, size=12.5, color=color, bold=True))
    base = y + h - 24
    f.append(line(x + 12, base, x + w - 12, base, color="#e6e6ea", sw=1.4))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (poly, color))
    f.append(text(x + w / 2, y + h - 6, note, size=10, color=MUTED, italic=True))


def fig_robust_default():
    W, H = 780, 300
    f = [text(W / 2, 26, "Зв'язка за замовчуванням: медіана(3) → EMA", size=15, bold=True)]

    random.seed(7)
    n = 48
    px0, py0, pw, ph = 40, 44, 200, 204
    plot_lo, plot_hi = py0 + 36, py0 + ph - 40        # вертикальні межі лінії

    # справжній сигнал: сходинка посередині
    def truth(i):
        return 0.0 if i < n // 2 else 1.0

    # сирий = правда + дрібний шум + поодинокі спайки
    raw = []
    for i in range(n):
        v = truth(i) + random.uniform(-0.06, 0.06)
        if i in (10, 33):                              # спайки
            v += 1.6
        raw.append(v)

    # медіана(3)
    med = [raw[0]] + [sorted(raw[i - 1:i + 2])[1] for i in range(1, n - 1)] + [raw[-1]]

    # EMA по медіані
    ema, s = [], med[0]
    a = 0.3
    for v in med:
        s = a * v + (1 - a) * s
        ema.append(s)

    def to_pts(series, x):
        lo, hi = -0.1, 1.75
        out = []
        for i, v in enumerate(series):
            xx = x + 12 + (pw - 24) * i / (n - 1)
            yy = plot_hi - (v - lo) / (hi - lo) * (plot_hi - plot_lo)
            out.append((xx, yy))
        return out

    _stream_panel(f, px0, py0, pw, ph, POS, "сирий потік", "+спайки +шум", to_pts(raw, px0))
    _stream_panel(f, 290, py0, pw, ph, MED, "медіана(3)", "спайки геть", to_pts(med, 290))
    _stream_panel(f, 540, py0, pw, ph, FIELD, "EMA", "гладко", to_pts(ema, 540))

    f.append(arrow(244, 146, 286, 146, color=INK, sw=2))
    f.append(arrow(494, 146, 536, 146, color=INK, sw=2))

    f.append(text(W / 2, 288,
                  "дешева, надійна, покриває найчастіші біди — звідси й починають",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "robust-default.svg"), W, H, *f)


# ── 5. Чотири анти-патерни ───────────────────────────────────────────────────
def fig_antipatterns():
    W, H = 720, 250
    f = [text(W / 2, 26, "Чотири типові помилки фільтрації", size=15, bold=True)]

    cards = [
        ("Усереднити викид", "спайк розмажеться", "медіана"),
        ("Фільтрувати дрейф", "це не шум — систематика", "калібрування"),
        ("Перефільтрувати", "затримка розгойдує", "легший фільтр"),
        ("Вірити гладкому", "гладко ≠ правильно", "свіжо й правдиво"),
    ]
    x = 14
    for bad, why, fix in cards:
        f.append(rect(x, 52, 168, 170, fill="#fdf3f2", stroke=POS, sw=1.6))
        f.append(text(x + 84, 80, "✗", size=18, color=POS, bold=True))
        f.append(fitbox(x + 8, 92, 152, 26, bad, size=11.5, color=INK, bold=True,
                        fill="#fdf3f2", stroke="none", sw=0))
        f.append(text(x + 84, 150, why, size=10, color=MUTED, italic=True))
        f.append(line(x + 16, 168, x + 152, 168, color="#eccccc", sw=1.2))
        f.append(text(x + 84, 198, "→ " + fix, size=11.5, color=FIELD, bold=True))
        x += 176

    f.append(text(W / 2, 244,
                  "кожна має свій почерк у виході — знаючи його, причину видно за секунди",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "antipatterns.svg"), W, H, *f)


# ── 6. Місце фільтра в тракті ────────────────────────────────────────────────
def fig_pipeline():
    W, H = 780, 250
    f = [text(W / 2, 26, "Місце фільтра в тракті: одна ланка, не кінець", size=15, bold=True)]

    stages = [
        ("сирі відліки", "давач", MUTED),
        ("фільтр", "геть випадкове", NEG),
        ("калібрування", "геть систематичне", GOLD),
    ]
    x = 30
    for title_, note, col in stages:
        f.append(rect(x, 86, 170, 76, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + 85, 120, title_, size=13, color=col, bold=True))
        f.append(text(x + 85, 142, note, size=10, color=MUTED, italic=True))
        x += 205
    f.append(arrow(202, 124, 233, 124, color=INK, sw=2))
    f.append(arrow(407, 124, 438, 124, color=INK, sw=2))

    outs = [("рішення", 60), ("керування", 124), ("поєднання", 188)]
    for label, yy in outs:
        f.append(arrow(610, 124, 648, yy, color=FIELD, sw=1.6))
        f.append(rect(650, yy - 16, 120, 32, fill=BG, stroke=FIELD, sw=1.5))
        f.append(text(710, yy + 5, label, size=11, color=FIELD, bold=True))

    f.append(text(W / 2, 234,
                  "фільтр прибирає випадкове; систематику знімає калібрування; далі — рішення й поєднання",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "pipeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_decision_tree()
    fig_compare_table()
    fig_recipes()
    fig_robust_default()
    fig_antipatterns()
    fig_pipeline()
    print("OK: 6 figures ->", IMG)
