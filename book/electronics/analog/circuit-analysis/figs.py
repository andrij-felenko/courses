# -*- coding: utf-8 -*-
"""Фігури теми «Аналіз кіл» (book/electronics/analog/circuit-analysis).
svgkit імпортуємо зі scripts/ — НЕ переписуємо (AUTHORING §5).

    python figs.py        # генерує всі SVG теми у ./img/

Вставки (hist-/proj-) мають власні, складніші схематичні SVG у ./img/, зроблені
окремо; цей генератор відповідає за фігури САМОЇ статті."""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (render, text, mtext, rect, line, arrow, circle, textbox,
                    fitbox, INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── допоміжне: резистор-прямокутник із підписом ─────────────────────────────
def res_h(cx, cy, label, w=54, h=18):
    """Горизонтальний резистор, підпис над ним."""
    s = rect(cx - w / 2, cy - h / 2, w, h, fill="#fff", stroke=INK, sw=2, rx=3)
    s += text(cx, cy - h / 2 - 6, label, size=13, bold=True, italic=True)
    return s

def res_v(cx, cy, label, w=20, h=70, side="right"):
    """Вертикальний резистор, підпис збоку."""
    s = rect(cx - w / 2, cy - h / 2, w, h, fill="#fff", stroke=INK, sw=2, rx=3)
    tx = cx + w / 2 + 8 if side == "right" else cx - w / 2 - 8
    anchor = "start" if side == "right" else "end"
    s += ('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
          'text-anchor="%s" font-weight="700" font-style="italic">%s</text>'
          % (tx, cy + 4, "'Segoe UI','DejaVu Sans',Arial,sans-serif", INK, anchor, label))
    return s

def battery(cx, cy, label):
    """Джерело (батарея) вертикально, підпис ліворуч червоним."""
    s = line(cx, cy - 30, cx, cy + 30, color=INK, sw=2.4)
    s += line(cx - 16, cy - 8, cx + 16, cy - 8, color=INK, sw=3)   # довга пластина
    s += line(cx - 9, cy + 8, cx + 9, cy + 8, color=INK, sw=5)     # коротка
    s += text(cx - 22, cy - 3, label, size=12, color=POS, bold=True, anchor="end")
    return s

def node_dot(cx, cy, r=4):
    return circle(cx, cy, r, fill=INK, stroke=INK, sw=1)


# ── 1. toolkit.svg — чотири знаряддя ────────────────────────────────────────
def fig_toolkit():
    W, H = 720, 300
    parts = []
    cells = [
        ("Закон Ома", "V = I·R", "зв'язок струму й\nнапруги на елементі", POS),
        ("Зведення", "R_екв", "послідовні / паралельні\nгрупи → один опір", FIELD),
        ("Закон струмів", "Σ I = 0", "у кожному вузлі:\nскільки втікає — стільки витікає", NEG),
        ("Закон напруг", "Σ V = 0", "по кожному контуру:\nспади врівноважують джерело", "#8e44ad"),
    ]
    bw, bh, gap = 158, 150, 14
    x0 = (W - (bw * 4 + gap * 3)) / 2
    top = 70
    for i, (name, formula, desc, col) in enumerate(cells):
        x = x0 + i * (bw + gap)
        parts.append(rect(x, top, bw, bh, fill=FILL, stroke=col, sw=2.2, rx=10))
        parts.append(rect(x, top, bw, 30, fill=col, sw=0, rx=10))
        parts.append(rect(x, top + 18, bw, 12, fill=col, sw=0, rx=0))
        parts.append(text(x + bw / 2, top + 21, name, size=14, color="#fff", bold=True))
        parts.append(text(x + bw / 2, top + 70, formula, size=22, color=col, bold=True))
        parts.append(mtext(x + bw / 2, top + 100, desc, size=11.5, color=MUTED, lh=1.25))
    parts.append(text(W / 2, H - 18,
                      "Будь-яке коло розв'язують комбінацією цих чотирьох — у правильному порядку",
                      size=12.5, color=INK, italic=True))
    render(out("toolkit.svg"), W, H, *parts,
           title="Чотири знаряддя аналізу кіл")


# ── 2. reduction.svg — згортання крок за кроком ─────────────────────────────
def fig_reduction():
    W, H = 760, 300
    parts = []
    y = 165
    stages = [
        (95,  "повна\nсхема",        "R₁, R₂∥R₃, …"),
        (300, "згорнули\nпаралель",  "R₂∥R₃ → 1 опір"),
        (505, "згорнули\nпослідовно", "усе → R_екв"),
        (665, "повний\nструм",       "I = V/R_екв"),
    ]
    for i, (x, cap, sub) in enumerate(stages):
        col = FIELD if i < 3 else POS
        parts.append(circle(x, y, 46, fill=FILL, stroke=col, sw=2.4))
        parts.append(mtext(x, y - 6, cap, size=12.5, color=INK, bold=True, lh=1.2))
        parts.append(text(x, y + 26, sub, size=10, color=MUTED))
        if i < len(stages) - 1:
            parts.append(arrow(x + 50, y, stages[i + 1][0] - 50, y, color=INK, sw=2))
    # зворотний хід
    parts.append(arrow(665, y + 70, 95, y + 70, color=NEG, sw=2))
    parts.append(text(380, y + 62, "«розгортаємо» назад: дільниками — спади й гілкові струми",
                      size=12, color=NEG, italic=True))
    render(out("reduction.svg"), W, H, *parts,
           title="Стратегія 1: згортання (вперед — до R_екв, назад — до всіх величин)")


# ── 3. reduction-worked.svg — числовий приклад ──────────────────────────────
def fig_reduction_worked():
    W, H = 760, 330
    parts = []
    # схема ліворуч
    bx, by = 60, 90
    parts.append(battery(bx, by + 80, "12 В"))
    parts.append(line(bx, by + 50, bx, by, color=INK, sw=2))
    parts.append(line(bx, by, bx + 70, by, color=INK, sw=2))
    parts.append(res_h(bx + 110, by, "R₁=100"))
    parts.append(line(bx + 137, by, bx + 200, by, color=INK, sw=2))
    parts.append(node_dot(bx + 200, by))
    # дві паралельні гілки
    parts.append(res_v(bx + 200, by + 80, "R₂=200", side="left"))
    parts.append(res_v(bx + 280, by + 80, "R₃=200", side="right"))
    parts.append(line(bx + 200, by, bx + 280, by, color=INK, sw=2))
    parts.append(line(bx + 280, by, bx + 280, by + 45, color=INK, sw=2))
    parts.append(line(bx + 200, by + 115, bx + 280, by + 115, color=INK, sw=2))
    parts.append(node_dot(bx + 200, by + 115))
    parts.append(line(bx + 200, by + 115, bx + 200, by + 160, color=INK, sw=2))
    parts.append(line(bx, by + 160, bx + 200, by + 160, color=INK, sw=2))
    parts.append(line(bx, by + 110, bx, by + 160, color=INK, sw=2))
    parts.append(text(bx + 150, by + 178, "30 мА", size=10, color=NEG))
    parts.append(text(bx + 235, by - 60, "по 30 мА у гілці", size=10, color=MUTED))
    # обчислення праворуч
    box = fitbox(420, 70, 300, 200,
                 "R₂∥R₃ = 200·200/400 = 100 Ω\n"
                 "R_екв = 100 + 100 = 200 Ω\n"
                 "I = 12/200 = 60 мА\n"
                 "V₁ = 0.06·100 = 6 В\n"
                 "V_пара = 12 − 6 = 6 В\n"
                 "I₂ = I₃ = 6/200 = 30 мА\n"
                 "KCL: 30 + 30 = 60 мА  ✓",
                 size=15, fill="#f6f8fc", stroke=INK)
    parts.append(box)
    render(out("reduction-worked.svg"), W, H, *parts,
           title="Приклад згортанням: R₁ послідовно з R₂∥R₃")


# ── 4. two-source.svg — коли не згортається ─────────────────────────────────
def fig_two_source():
    W, H = 760, 320
    parts = []
    L, R, top, bot = 110, 430, 110, 250
    mid = (L + R) / 2
    # рамка кола
    parts.append(line(L, top, R, top, color="#cf8b5e", sw=2.2))
    parts.append(line(L, bot, R, bot, color="#cf8b5e", sw=2.2))
    parts.append(battery(L, (top + bot) / 2, "V₁"))
    parts.append(line(L, top, L, (top + bot) / 2 - 30, color=INK, sw=2.2))
    parts.append(line(L, (top + bot) / 2 + 30, L, bot, color=INK, sw=2.2))
    parts.append(battery(R, (top + bot) / 2, "V₂"))
    parts.append(line(R, top, R, (top + bot) / 2 - 30, color=INK, sw=2.2))
    parts.append(line(R, (top + bot) / 2 + 30, R, bot, color=INK, sw=2.2))
    parts.append(res_h(L + 70, top, "R₁"))
    parts.append(res_h(R - 70, top, "R₂"))
    parts.append(res_v(mid, (top + bot) / 2, "R₃", side="right"))
    parts.append(line(mid, top, mid, (top + bot) / 2 - 35, color="#cf8b5e", sw=2))
    parts.append(line(mid, (top + bot) / 2 + 35, mid, bot, color="#cf8b5e", sw=2))
    parts.append(text(L + 60, (top + bot) / 2 + 10, "Iₐ", size=12, bold=True, italic=True))
    parts.append(text(R - 60, (top + bot) / 2 + 10, "I_b", size=12, bold=True, italic=True))
    # рівняння праворуч
    parts.append(fitbox(480, 105, 250, 130,
                        "контур A:\n  V₁ = Iₐ·R₁ + (Iₐ−I_b)·R₃\n\n"
                        "контур B:\n  V₂ = I_b·R₂ + (I_b−Iₐ)·R₃",
                        size=13, fill="#f6f8fc", stroke=INK))
    parts.append(text(605, 255, "дві рівності — дві невідомі", size=11, color=MUTED, italic=True))
    render(out("two-source.svg"), W, H, *parts,
           title="Коли коло не згортається: два джерела → система рівнянь")


# ── 5. systematic-worked.svg — числовий приклад системою ────────────────────
def fig_systematic_worked():
    W, H = 760, 300
    parts = []
    parts.append(fitbox(50, 60, 330, 200,
                        "Дано: V₁=10, V₂=6 В;\n"
                        "R₁=R₂=10 Ω, R₃=20 Ω\n\n"
                        "A:  10 = 30·Iₐ − 20·I_b\n"
                        "B:   6 = 30·I_b − 20·Iₐ\n\n"
                        "розв'язок системи:\n"
                        "Iₐ = 0.36 А,  I_b = 0.44 А",
                        size=14, fill="#f6f8fc", stroke=INK))
    parts.append(fitbox(410, 60, 300, 200,
                        "струм у R₃ (спільна гілка):\n"
                        "I₃ = Iₐ − I_b = −0.08 А\n"
                        "(тече знизу вгору)\n\n"
                        "перевірка KVL, контур A:\n"
                        "30·0.36 − 20·0.44\n"
                        "= 10.8 − 8.8 = 10 В = V₁  ✓",
                        size=13, fill="#eef7f0", stroke=FIELD))
    render(out("systematic-worked.svg"), W, H, *parts,
           title="Приклад системою: два контури, дві невідомі")


# ── 6. recipe.svg — рецепт і перевірки ──────────────────────────────────────
def fig_recipe():
    W, H = 740, 330
    parts = []
    steps = [
        ("1", "спрости", "послідовні й\nпаралельні групи", FIELD),
        ("2", "повний струм", "I = V/R_екв", POS),
        ("3", "розгорни назад", "дільниками — спади\nй гілкові струми", NEG),
        ("4", "не згорнулось?", "система\nKCL + KVL + Ом", "#8e44ad"),
    ]
    bw, gap = 160, 14
    x0 = (W - (bw * 4 + gap * 3)) / 2
    top = 70
    for i, (n, name, desc, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        parts.append(rect(x, top, bw, 110, fill=FILL, stroke=col, sw=2.2, rx=10))
        parts.append(circle(x + 24, top + 26, 15, fill=col, stroke=col, sw=1))
        parts.append(text(x + 24, top + 31, n, size=15, color="#fff", bold=True))
        parts.append(text(x + bw / 2 + 14, top + 31, name, size=13.5, color=INK, bold=True))
        parts.append(mtext(x + bw / 2, top + 68, desc, size=11, color=MUTED, lh=1.25))
        if i < 3:
            parts.append(arrow(x + bw + 1, top + 55, x + bw + gap - 1, top + 55, color=INK, sw=1.8))
    # три самоперевірки
    cy = top + 175
    checks = [("одиниці", "В з В, А з А —\nне загубити множник"),
              ("KCL / KVL", "Σ струмів = повному,\nΣ спадів = джерелу"),
              ("порядок величин", "міліампери,\nа не кілоампери?")]
    cw = 220
    cx0 = (W - (cw * 3 + 20 * 2)) / 2
    parts.append(text(W / 2, cy - 14, "і завжди — три самоперевірки:", size=13, color=INK, bold=True))
    for i, (name, desc) in enumerate(checks):
        x = cx0 + i * (cw + 20)
        parts.append(rect(x, cy, cw, 64, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=8))
        parts.append(text(x + cw / 2, cy + 20, name, size=12.5, color=FIELD, bold=True))
        parts.append(mtext(x + cw / 2, cy + 38, desc, size=10.5, color=MUTED, lh=1.2))
    render(out("recipe.svg"), W, H, *parts,
           title="Рецепт: 4 кроки + 3 перевірки")


def main():
    fig_toolkit()
    fig_reduction()
    fig_reduction_worked()
    fig_two_source()
    fig_systematic_worked()
    fig_recipe()
    print("Згенеровано фігури статті у", IMG)


if __name__ == "__main__":
    main()
