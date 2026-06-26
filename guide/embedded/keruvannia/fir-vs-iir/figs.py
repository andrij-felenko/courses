# -*- coding: utf-8 -*-
"""Фігури до теми «КІХ проти БІХ».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math, random

# Локальні відтінки понад палітру svgkit
KIH = "#27ae60"      # КІХ — безпека, зелене
BIH = "#c0392b"      # БІХ — гострота/ризик, гаряче
GOLD = "#b9770e"     # затримка / тепле акцентування


# ── 1. Двобій критеріями: дзеркальна таблиця ─────────────────────────────────
def fig_comparison():
    W, H = 720, 430
    f = [text(W / 2, 26, "КІХ і БІХ: дзеркало переваг", size=15, bold=True)]

    cols = [("КІХ", 430, KIH), ("БІХ", 600, BIH)]
    for name, cx, col in cols:
        f.append(rect(cx - 70, 44, 140, 36, fill=FILL, stroke=col, sw=1.8))
        f.append(text(cx, 67, name, size=13, color=col, bold=True))

    rows = [
        ("Стійкість гарантована",   "++", "x"),
        ("Лінійна фаза (форма ціла)", "++", "x"),
        ("Гострий зріз дешево",      "x",  "++"),
        ("Малі обчислення",          "~",  "++"),
        ("Мала пам'ять",             "~",  "++"),
        ("Мала затримка",            "x",  "++"),
        ("Простота й передбачуваність", "++", "~"),
        ("Копіює аналоговий прототип", "x", "++"),
    ]
    glyph = {"++": ("сильно", KIH), "x": ("слабко", BIH), "~": ("так собі", GOLD)}

    y = 86
    for i, (label, a, b) in enumerate(rows):
        if i % 2 == 0:
            f.append(rect(16, y, 688, 36, fill="#f6f6f8", stroke="none", sw=0, rx=4))
        f.append(text(28, y + 24, label, size=12, anchor="start"))
        for v, cx in ((a, 430), (b, 600)):
            txt, col = glyph[v]
            f.append(text(cx, y + 24, txt, size=12, color=col, bold=True))
        y += 40

    f.append(text(W / 2, 418,
                  "усе, у чому сильний один, — слабке місце другого",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "comparison.svg"), W, H, *f)


# ── 2. Дерево рішення: два питання вирішують усе ──────────────────────────────
def fig_decision_tree():
    W, H = 760, 430
    f = [text(W / 2, 26, "Два питання вирішують вибір", size=15, bold=True)]

    # питання 1
    f.append(rect(40, 70, 230, 60, fill=FILL, stroke=INK, sw=2))
    f.append(text(155, 95, "Форма сигналу важлива?", size=12, bold=True))
    f.append(text(155, 114, "(фаза, фронти, точна хвиля)", size=9.5, color=MUTED, italic=True))

    # так → КІХ
    f.append(arrow(155, 130, 155, 178, color=KIH, sw=1.8))
    f.append(text(168, 158, "так", size=10.5, color=KIH, anchor="start", italic=True))
    f.append(rect(40, 180, 230, 58, fill=FILL, stroke=KIH, sw=1.8))
    f.append(text(155, 205, "КІХ", size=14, color=KIH, bold=True))
    f.append(text(155, 224, "лінійна фаза не псує форму", size=9.5, color=MUTED, italic=True))

    # ні → питання 2
    f.append(arrow(270, 100, 470, 100, color=MUTED, sw=1.8))
    f.append(text(360, 88, "ні", size=10.5, color=MUTED, anchor="middle", italic=True))
    f.append(rect(470, 70, 250, 60, fill=FILL, stroke=INK, sw=2))
    f.append(text(595, 92, "Гострий зріз", size=12, bold=True))
    f.append(text(595, 110, "за тісних ресурсів?", size=12, bold=True))

    # питання 2 → так → БІХ
    f.append(arrow(595, 130, 595, 178, color=BIH, sw=1.8))
    f.append(text(608, 158, "так", size=10.5, color=BIH, anchor="start", italic=True))
    f.append(rect(480, 180, 230, 58, fill=FILL, stroke=BIH, sw=1.8))
    f.append(text(595, 205, "БІХ", size=14, color=BIH, bold=True))
    f.append(text(595, 224, "крутість за кілька коефіцієнтів", size=9.5, color=MUTED, italic=True))

    # питання 2 → ні → байдуже
    f.append(arrow(595, 130, 595, 130, color=MUTED, sw=0.1))
    f.append(line(720, 100, 738, 100, color=MUTED, sw=1.6))
    f.append(text(729, 88, "ні", size=9, color=MUTED, italic=True))

    # нижній ряд: стабільність + проста задача
    f.append(rect(40, 300, 330, 60, fill=BG, stroke=KIH, sw=1.5))
    f.append(text(205, 324, "Критична безпека / стабільність?", size=11.5, bold=True))
    f.append(text(205, 344, "→ теж КІХ (не вибухне за визначенням)", size=10.5, color=KIH, italic=True))

    f.append(rect(400, 300, 320, 60, fill=BG, stroke=MUTED, sw=1.5))
    f.append(text(560, 324, "Жодне питання не «гостре»?", size=11.5, bold=True))
    f.append(text(560, 344, "→ найдешевше й найпростіше (EMA)", size=10.5, color=MUTED, italic=True))

    f.append(text(W / 2, 410,
                  "форма головніша за все: не можна псувати — БІХ відпадає одразу",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "decision-tree.svg"), W, H, *f)


# ── 3. Готові рецепти: задача → сімейство ─────────────────────────────────────
def fig_recipes():
    W, H = 820, 260
    f = [text(W / 2, 26, "Готові рецепти: задача підказує сімейство", size=15, bold=True)]

    cards = [
        (["ЕКГ,", "форма хвилі"], "КІХ", "діагноз — за QRS", KIH),
        (["Notch 50 Гц,", "дешевий чип"], "БІХ-біквад", "гостро за копійки", BIH),
        (["Просте", "згладжування"], "EMA", "найдешевший БІХ", GOLD),
        (["Безпека", "в керуванні"], "КІХ", "стійкість гарантовано", KIH),
        (["Копія", "аналогового"], "БІХ", "Баттерворт тощо", BIH),
    ]
    cw = 152
    x = 16
    for task, fam, note, col in cards:
        f.append(rect(x, 52, cw, 176, fill=FILL, stroke=col, sw=1.6))
        f.append(mtext(x + cw / 2, 76, task, size=12, color=INK, bold=True))
        f.append(line(x + 14, 108, x + cw - 14, 108, color="#dddddd", sw=1.2))
        f.append(text(x + cw / 2, 150, fam, size=14, color=col, bold=True))
        f.append(text(x + cw / 2, 204, note, size=9.5, color=MUTED, italic=True))
        x += cw + 8

    f.append(text(W / 2, 252,
                  "той самий тип задачі, протилежні рішення — бо протилежні пріоритети",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "recipes.svg"), W, H, *f)


# ── 4. Старі знайомі: ковзне середнє — КІХ, EMA — БІХ ─────────────────────────
def fig_already_know():
    W, H = 740, 300
    f = [text(W / 2, 26, "Ви вже знаєте обидва сімейства", size=15, bold=True)]

    # ліва панель: ковзне середнє = КІХ
    f.append(rect(30, 50, 330, 210, fill="#f3faf5", stroke=KIH, sw=1.8))
    f.append(text(195, 76, "Ковзне середнє = КІХ", size=13, color=KIH, bold=True))
    f.append(text(195, 100, "скінченна пам'ять · рівні відводи", size=10.5, color=MUTED, italic=True))
    f.append(text(195, 118, "лінійна фаза · завжди стійкий", size=10.5, color=MUTED, italic=True))
    # вікно зі скінченних відводів
    for i in range(5):
        bx = 70 + i * 46
        f.append(rect(bx, 150, 38, 60, fill="#d8f0e0", stroke=KIH, sw=1.4, rx=3))
        f.append(text(bx + 19, 186, "1/N", size=11, color=KIH, bold=True))
    f.append(text(195, 238, "пам'ять обривається рівно — скінченна", size=10, color=KIH, italic=True))

    # права панель: EMA = БІХ
    f.append(rect(380, 50, 330, 210, fill="#fdf2f1", stroke=BIH, sw=1.8))
    f.append(text(545, 76, "EMA = БІХ", size=13, color=BIH, bold=True))
    f.append(text(545, 100, "зворотний зв'язок · один коефіцієнт α", size=10.5, color=MUTED, italic=True))
    f.append(text(545, 118, "нескінченний хвіст · гранична ощадливість", size=10.5, color=MUTED, italic=True))
    # експоненційно спадний хвіст
    base = 210
    x0 = 410
    for i in range(11):
        h = 60 * (0.72 ** i)
        bx = x0 + i * 26
        f.append(rect(bx, base - h, 20, h, fill="#f6d4d1", stroke=BIH, sw=1.2, rx=2))
    f.append(text(545, 238, "хвіст згасає, але вічно — нескінченна", size=10, color=BIH, italic=True))

    f.append(text(W / 2, 286,
                  "прості часові фільтри — окремі випадки двох великих сімейств",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "already-know.svg"), W, H, *f)


# ── 5. Терези: фундаментальний розмін ─────────────────────────────────────────
def fig_tradeoff():
    W, H = 720, 320
    f = [text(W / 2, 26, "Безплатного фільтра не буває", size=15, bold=True)]

    fx, fy = W / 2, 110          # точка опори
    beam_w = 250
    tilt = 16                     # нахил коромисла

    # стійка й опора
    f.append(line(fx, fy, fx, 250, color=INK, sw=3))
    f.append('<polygon points="%.0f,250 %.0f,250 %.0f,236 %.0f,236" fill="%s"/>'
             % (fx - 26, fx + 26, fx + 14, fx - 14, INK))
    # коромисло (нахилене вліво — обидва однаково вагомі, символічно врівноважене)
    lx, ly = fx - beam_w, fy + tilt
    rx, ry = fx + beam_w, fy - tilt
    f.append(line(lx, ly, rx, ry, color=INK, sw=3))

    # ліва шалька — КІХ
    f.append(line(lx, ly, lx, ly + 24, color=MUTED, sw=1.4))
    box, bw, bh = textbox(lx, ly + 64, "КІХ\nбезпека + форма\n(дорожчий)",
                          size=11.5, color=KIH, stroke=KIH, sw=1.8, fill="#f3faf5", bold=True)
    f.append(box)

    # права шалька — БІХ
    f.append(line(rx, ry, rx, ry + 24, color=MUTED, sw=1.4))
    box2, bw2, bh2 = textbox(rx, ry + 64, "БІХ\nгострота + ощадливість\n(ризик + фаза)",
                             size=11.5, color=BIH, stroke=BIH, sw=1.8, fill="#fdf2f1", bold=True)
    f.append(box2)

    f.append(text(W / 2, 300,
                  "схиляючи терези в один бік, ви відмовляєтесь від переваг другого",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "tradeoff.svg"), W, H, *f)


# ── 6. Тракт: кожна ланка — свій фільтр ───────────────────────────────────────
def fig_pipeline():
    W, H = 780, 250
    f = [text(W / 2, 26, "Вибір — для кожної ланки тракту окремо", size=15, bold=True)]

    stages = [
        ("медіана", "проти викидів", "нелінійна", GOLD),
        ("БІХ-notch 50 Гц", "гострий зріз мережі", "ефективність", BIH),
        ("КІХ-згладжування", "чиста форма", "лінійна фаза", KIH),
    ]
    x = 24
    for title_, note, tag, col in stages:
        f.append(rect(x, 84, 220, 80, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + 110, 112, title_, size=13, color=col, bold=True))
        f.append(text(x + 110, 132, note, size=10, color=MUTED, italic=True))
        f.append(text(x + 110, 152, tag, size=9.5, color=col, italic=True))
        x += 245
    f.append(arrow(244, 124, 268, 124, color=INK, sw=2))
    f.append(arrow(489, 124, 513, 124, color=INK, sw=2))

    f.append(text(W / 2, 200,
                  "не «один фільтр на все» — ланцюжок, де кожна ланка найкраща у своїй ролі",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, 224,
                  "КІХ, БІХ і нелінійна медіана уживаються в одному тракті",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "pipeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_comparison()
    fig_decision_tree()
    fig_recipes()
    fig_already_know()
    fig_tradeoff()
    fig_pipeline()
    print("OK: 6 figures ->", IMG)
