# -*- coding: utf-8 -*-
"""Фігури теми «Аналіз кіл» (book/electronics/analog/circuit-analysis).
svgkit імпортуємо зі scripts/ — НЕ переписуємо (AUTHORING §5).

    python figs.py        # генерує всі SVG теми ТА її вставок у ./img/

Генерує і фігури самої статті, і фігури вставок (hist-maxwell-mesh,
proj-circuit-sim, proj-mna-spice) — усе з одного місця, як вимагає §5."""
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


# ════════════════════════════════════════════════════════════════════════════
#  ФІГУРИ ВСТАВОК — генеруємо тут-таки (§5: один figs.py у теці теми)
# ════════════════════════════════════════════════════════════════════════════

PURPLE = "#8e44ad"

# ── hist-maxwell-mesh: гілкові струми проти контурних ────────────────────────
def fig_branch_vs_mesh():
    W, H = 760, 360
    parts = []
    parts.append(line(W / 2, 64, W / 2, 320, color="#e4e4e4", sw=1.5))
    # ── ліворуч: гілкові струми ──
    parts.append(text(190, 86, "Гілкові струми", size=13, color=NEG, bold=True))
    parts.append(rect(70, 108, 240, 150, fill="none", stroke=INK, sw=2, rx=0))
    parts.append(line(190, 108, 190, 258, color=INK, sw=2))
    parts.append(text(66, 188, "V₁", size=11, color=POS, bold=True, anchor="end"))
    parts.append(text(314, 188, "V₂", size=11, color=POS, bold=True, anchor="start"))
    parts.append(text(130, 100, "i₁", size=12, color=NEG, bold=True))
    parts.append(text(250, 100, "i₂", size=12, color=NEG, bold=True))
    parts.append(text(200, 196, "i₃", size=12, color=NEG, bold=True))
    parts.append(rect(75, 272, 230, 56, fill="#eef2fb", stroke=NEG, sw=1.5, rx=8))
    parts.append(text(190, 294, "3 невідомі (i₁, i₂, i₃):", size=11, color=INK, bold=True))
    parts.append(text(190, 314, "1 струмів + 2 напруг = 3 рівняння", size=11, color=INK, bold=True))
    # ── праворуч: контурні струми ──
    parts.append(text(570, 86, "Контурні струми (Максвелл)", size=13, color=FIELD, bold=True))
    parts.append(rect(450, 108, 240, 150, fill="none", stroke=INK, sw=2, rx=0))
    parts.append(line(570, 108, 570, 258, color=INK, sw=2))
    parts.append(text(446, 188, "V₁", size=11, color=POS, bold=True, anchor="end"))
    parts.append(text(694, 188, "V₂", size=11, color=POS, bold=True, anchor="start"))
    parts.append(circle(510, 183, 24, fill="none", stroke=FIELD, sw=2))
    parts.append(text(510, 188, "Iₐ", size=12, color=FIELD, bold=True))
    parts.append(circle(630, 183, 24, fill="none", stroke=FIELD, sw=2))
    parts.append(text(630, 188, "I_b", size=12, color=FIELD, bold=True))
    parts.append(rect(455, 272, 230, 56, fill="#eef7f0", stroke=FIELD, sw=1.5, rx=8))
    parts.append(text(570, 294, "2 невідомі (Iₐ, I_b):", size=11, color=INK, bold=True))
    parts.append(text(570, 314, "струмів — сам собою; 2 напруг", size=11, color=INK, bold=True))
    parts.append(text(W / 2, 348, "Менше невідомих → менше рівнянь → швидший розв'язок руками",
                      size=12, color=FIELD, italic=True))
    render(out("branch-vs-mesh.svg"), W, H, *parts,
           title="Гілкові струми проти контурних: 3 рівняння проти 2")


# ── hist-maxwell-mesh: чому контурний струм сам задовольняє закон струмів ─────
def fig_cyclic_kcl():
    W, H = 760, 340
    parts = []
    parts.append(line(W / 2, 64, W / 2, 312, color="#e4e4e4", sw=1.5))
    # ліворуч — вузол, у який струм входить і виходить
    parts.append(text(195, 96, "Контурний струм крізь вузол", size=12, color=INK, bold=True))
    parts.append(node_dot(195, 180, r=8))
    parts.append(arrow(90, 180, 180, 180, color=FIELD, sw=2.6))
    parts.append(text(135, 168, "Iₐ входить", size=10, color=FIELD, bold=True))
    parts.append(arrow(210, 180, 300, 180, color=FIELD, sw=2.6))
    parts.append(text(265, 168, "Iₐ виходить", size=10, color=FIELD, bold=True))
    parts.append(text(195, 214, "те саме Iₐ → втікає = витікає", size=11, color=INK, bold=True))
    parts.append(text(195, 238, "→ закон струмів виконано сам собою", size=11, color=FIELD, bold=True))
    parts.append(text(195, 268, "тож пишемо лише закон напруг по контурах",
                      size=10, color=MUTED, italic=True))
    # праворуч — який метод обрати
    parts.append(text(575, 96, "Скільки рівнянь? Бери менше", size=12, color=INK, bold=True))
    parts.append(rect(440, 116, 290, 170, fill="#f7f7f7", stroke=MUTED, sw=1.5, rx=10))
    parts.append(text(458, 146, "• контурний метод: L = B−N+1 рівнянь",
                      size=11, color=FIELD, bold=True, anchor="start"))
    parts.append(text(458, 170, "• вузловий метод: N−1 рівнянь",
                      size=11, color=NEG, bold=True, anchor="start"))
    parts.append(mtext(458, 200, "Бери той, де менше — для різних\nкіл виграє різний метод.",
                       size=11, color=INK, anchor="start", lh=1.3))
    parts.append(mtext(458, 250, "Іронія: руками виграє контурний,\nа машини беруть вузловий / MNA —\nйого легше скласти з netlist.",
                       size=10, color=MUTED, anchor="start", lh=1.3))
    render(out("cyclic-kcl.svg"), W, H, *parts,
           title="Контурний струм автоматично задовольняє закон струмів")


# ── proj-mna-spice: резистор «штампує» хрест провідностей ────────────────────
def fig_mna_stamping():
    W, H = 760, 340
    parts = []
    parts.append(line(W / 2, 70, W / 2, 312, color="#e4e4e4", sw=1.5))
    # ліворуч — резистор між вузлами 1 і 2
    parts.append(text(190, 96, "Резистор R між вузлами 1 і 2", size=12, color=INK, bold=True))
    parts.append(circle(110, 160, 18, fill="#eef2fb", stroke=NEG, sw=2))
    parts.append(text(110, 165, "1", size=12, color=INK, bold=True))
    parts.append(circle(290, 160, 18, fill="#eef2fb", stroke=NEG, sw=2))
    parts.append(text(290, 165, "2", size=12, color=INK, bold=True))
    parts.append(line(128, 160, 165, 160, color=INK, sw=2))
    parts.append(line(235, 160, 272, 160, color=INK, sw=2))
    parts.append(rect(165, 148, 70, 24, fill="#fff", stroke=MUTED, sw=2, rx=4))
    parts.append(text(200, 165, "R", size=12, color=INK, bold=True))
    parts.append(text(200, 198, "провідність g = 1/R", size=10, color=MUTED))
    parts.append(text(190, 236, "додає у G чотири внески:", size=11, color=INK, bold=True))
    parts.append(text(190, 262, "(1,1) += g     (2,2) += g", size=12, color=FIELD, bold=True))
    parts.append(text(190, 284, "(1,2) −= g     (2,1) −= g", size=12, color=POS, bold=True))
    # праворуч — матриця G 2×2
    parts.append(text(600, 96, "Матриця провідностей G", size=12, color=INK, bold=True))
    parts.append(text(576, 124, "1", size=11, color=MUTED, bold=True))
    parts.append(text(648, 124, "2", size=11, color=MUTED, bold=True))
    parts.append(text(524, 168, "1", size=11, color=MUTED, bold=True))
    parts.append(text(524, 240, "2", size=11, color=MUTED, bold=True))
    cells = [(540, 132, "+g", FIELD), (612, 132, "−g", POS),
             (540, 204, "−g", POS), (612, 204, "+g", FIELD)]
    for cx, cy, lbl, col in cells:
        parts.append(rect(cx, cy, 72, 72, fill="#fafafa", stroke="#cccccc", sw=1.2, rx=0))
        parts.append(text(cx + 36, cy + 42, lbl, size=15, color=col, bold=True))
    parts.append(text(612, 300, "Кожен елемент штампує свій хрест незалежно",
                      size=10, color=INK, bold=True))
    parts.append(text(612, 318, "— уся матриця збирається з netlist сама",
                      size=10, color=MUTED, italic=True))
    render(out("mna-stamping.svg"), W, H, *parts,
           title="Резистор «штампує» хрест провідностей у матрицю G")


# ── proj-mna-spice: джерело напруги додає облямівковий рядок і стовпець ───────
def fig_mna_augment():
    W, H = 760, 340
    parts = []
    # матриця 3×3 з облямівкою
    x0, y0, c = 90, 90, 70
    labels = [["g₁", "−g₁", "1"], ["−g₁", "g₁+g₂", "0"], ["1", "0", "0"]]
    for i in range(3):
        for j in range(3):
            border = (i == 2 or j == 2)
            fill = "#eef2fb" if border else "#fafafa"
            parts.append(rect(x0 + j * c, y0 + i * c, c, c, fill=fill, stroke="#cccccc", sw=1.2, rx=0))
            parts.append(text(x0 + j * c + c / 2, y0 + i * c + c / 2 + 5,
                              labels[i][j], size=12, color=INK, bold=True))
    parts.append(line(x0 + 2 * c, y0 - 4, x0 + 2 * c, y0 + 3 * c + 4, color=NEG, sw=2))
    parts.append(line(x0 - 4, y0 + 2 * c, x0 + 3 * c + 4, y0 + 2 * c, color=NEG, sw=2))
    parts.append(text(x0 + c, y0 - 14, "вузлові рівняння", size=9.5, color=MUTED))
    parts.append(text(x0 + 2 * c + c / 2, y0 - 14, "джерело", size=9, color=NEG, bold=True))
    # вектор невідомих і права частина
    vx = x0 + 3 * c + 30
    for i, (v, col) in enumerate([("V₁", INK), ("V₂", INK), ("I_V", NEG)]):
        parts.append(text(vx, y0 + i * c + c / 2 + 5, v, size=13, color=col, bold=True))
    parts.append(text(vx + 34, y0 + c + c / 2 + 5, "=", size=16, color=INK, bold=True))
    for i, (v, col) in enumerate([("0", INK), ("0", INK), ("Vs", NEG)]):
        parts.append(text(vx + 70, y0 + i * c + c / 2 + 5, v, size=13, color=col, bold=True))
    # пояснення праворуч
    parts.append(rect(500, 116, 250, 150, fill="#eef7f0", stroke=FIELD, sw=1.5, rx=10))
    parts.append(text(625, 140, "Збірка → [ G  B ; C  D ]", size=11, color=INK, bold=True))
    parts.append(mtext(516, 164, "• G — вузлові провідності;\n• рядок/стовпець на кожне\n   джерело напруги (струм I_V).",
                       size=10, color=INK, anchor="start", lh=1.4))
    parts.append(mtext(516, 224, "• висячий вузол → матриця\n   вироджена; SPICE додає\n   gmin на землю.",
                       size=10, color=POS, anchor="start", lh=1.4))
    parts.append(text(W / 2, 322, "Далі облямівкову матрицю розв'язує метод Гаусса",
                      size=12, color=FIELD, italic=True))
    render(out("mna-augment.svg"), W, H, *parts,
           title="MNA: джерело напруги додає облямівковий рядок і стовпець")


# ── proj-circuit-sim: цикл «перевір до паяння» ───────────────────────────────
def fig_verify_loop():
    W, H = 720, 380
    parts = []
    cx, cy = W / 2, 210
    boxes = [
        (cx, 95, "1. Намалювати", "перенести схему\nз паперу у вікно", FIELD),
        (cx + 200, cy, "2. Запустити", "рушій розв'язує\nрівняння Кірхгофа", NEG),
        (cx, 325, "3. Зміряти", "клік на елемент:\nV, I, P миттєво", "#e08030"),
        (cx - 200, cy, "4. Звірити", "збігається з ручним\nрозрахунком?", POS),
    ]
    bw, bh = 168, 78
    for x, y, t, d, col in boxes:
        parts.append(rect(x - bw / 2, y - bh / 2, bw, bh, fill="#f4f6f9", stroke=col, sw=2.4, rx=11))
        parts.append(text(x, y - 12, t, size=15, color=col, bold=True))
        parts.append(mtext(x, y + 8, d, size=11.5, color=INK, lh=1.25))
    # стрілки по колу
    parts.append(arrow(cx + 90, 118, cx + 130, cy - 45, color=MUTED, sw=2.2))
    parts.append(arrow(cx + 130, cy + 45, cx + 90, 302, color=MUTED, sw=2.2))
    parts.append(arrow(cx - 90, 302, cx - 130, cy + 45, color=MUTED, sw=2.2))
    parts.append(arrow(cx - 130, cy - 45, cx - 90, 118, color=MUTED, sw=2.2))
    parts.append(text(cx, cy - 16, "ціна помилки", size=12, color=MUTED))
    parts.append(text(cx, cy + 8, "тут ≈ 0", size=18, color=INK, bold=True))
    parts.append(text(cx, cy + 28, "(а на платі — час і деталі)", size=11, color=MUTED))
    parts.append(text(cx, 364, "Цикл крутять, доки числа не зійдуться — і лише тоді беруться за паяльник",
                      size=12, color=MUTED, italic=True))
    render(out("verify-loop.svg"), W, H, *parts,
           title="Симулятор як «нульова ітерація»: спіймати помилку до паяння")


# ── proj-circuit-sim: що показує симулятор (полотно + панель замірів) ─────────
def fig_what_it_shows():
    W, H = 720, 440
    parts = []
    # полотно ліворуч
    parts.append(rect(28, 56, 392, 360, fill="#f4f6f9", stroke=MUTED, sw=1.6, rx=10))
    parts.append(text(40, 78, "полотно (перетягни-й-кинь)", size=12, color=MUTED, italic=True, anchor="start"))
    parts.append(rect(95, 120, 265, 220, fill="none", stroke=INK, sw=2.4, rx=0))
    # джерело (батарея) на лівій стороні
    parts.append(line(84, 225, 106, 225, color=INK, sw=3))
    parts.append(line(89, 233, 101, 233, color=INK, sw=2))
    parts.append(text(79, 234, "12 В", size=12, color=INK, anchor="end"))
    parts.append(text(118, 226, "+", size=14, color=POS, bold=True, anchor="start"))
    parts.append(text(118, 242, "−", size=14, color=NEG, bold=True, anchor="start"))
    # два резистори зверху
    parts.append(res_h(165, 120, "R₁ 100Ω", w=50, h=16))
    parts.append(res_h(285, 120, "R₂ 200Ω", w=50, h=16))
    parts.append(node_dot(225, 120, r=4))
    parts.append(text(225, 102, "вузол A", size=11, color=FIELD, bold=True))
    parts.append(text(225, 360, "рухомі точки = струм (густина ∝ I)", size=11, color="#e08030"))
    # панель замірів праворуч
    parts.append(rect(452, 56, 240, 360, fill="#ffffff", stroke=INK, sw=1.6, rx=10))
    parts.append(text(572, 78, "клік на елемент →", size=13, color=INK, bold=True))
    parts.append(text(572, 94, "панель замірів", size=11, color=MUTED))
    rows = [
        ("Напруга вузла A", "8.00 В", NEG, "= V·R₂/(R₁+R₂)"),
        ("Струм гілки", "40.0 мА", "#e08030", "однаковий усюди (закон струмів)"),
        ("Спад на R₁", "4.00 В", INK, "I·R₁ (закон Ома)"),
        ("Потужність R₂", "320 мВт", POS, "I²·R — гріється?"),
        ("Σ спадів у контурі", "12.00 В  ✓", FIELD, "= джерело (закон напруг)"),
    ]
    ry = 116
    for label, val, col, note in rows:
        parts.append(line(466, ry - 14, 678, ry - 14, color="#e4e4e4", sw=1.2))
        parts.append(text(468, ry, label, size=12, color=INK, anchor="start"))
        parts.append(text(468, ry + 19, val, size=15, color=col, bold=True, anchor="start"))
        parts.append(text(468, ry + 35, note, size=10, color=MUTED, italic=True, anchor="start"))
        ry += 60
    parts.append(text(W / 2, 432, "Симулятор не вигадує фізики — показує те, що ви порахували б руками",
                      size=12, color=MUTED, italic=True))
    render(out("what-it-shows.svg"), W, H, *parts,
           title="Що показує симулятор: величини Кірхгофа наживо")


def main():
    fig_toolkit()
    fig_reduction()
    fig_reduction_worked()
    fig_two_source()
    fig_systematic_worked()
    fig_recipe()
    # вставки
    fig_branch_vs_mesh()
    fig_cyclic_kcl()
    fig_mna_stamping()
    fig_mna_augment()
    fig_verify_loop()
    fig_what_it_shows()
    print("Згенеровано фігури статті та вставок у", IMG)


if __name__ == "__main__":
    main()
