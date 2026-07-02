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


# ════════════════════════════════════════════════════════════════════════════
#  ФІГУРИ ДЕТАЛЬНОЇ СТАТТІ (circuit-analysis-d.md)
# ════════════════════════════════════════════════════════════════════════════

# ── tree-cotree.svg — дерево й хорди: звідки N−1 і B−N+1 ─────────────────────
def fig_tree_cotree():
    W, H = 760, 340
    parts = []
    parts.append(line(W / 2, 62, W / 2, 300, color="#e4e4e4", sw=1.5))
    # вузли — 4 штуки в обох панелях, гілки: 3 дерево + 2 хорди = 5, тож L=2
    def graph(ox, tree_only):
        pts = {1: (ox + 40, 110), 2: (ox + 200, 110),
               3: (ox + 200, 240), 4: (ox + 40, 240)}
        edges_tree = [(1, 2), (2, 3), (3, 4)]      # N−1 = 3 гілки дерева
        edges_cotree = [(1, 4), (1, 3)]            # хорди
        s = ""
        for a, b in edges_tree:
            s += line(pts[a][0], pts[a][1], pts[b][0], pts[b][1], color=FIELD, sw=3)
        if not tree_only:
            for a, b in edges_cotree:
                s += line(pts[a][0], pts[a][1], pts[b][0], pts[b][1],
                          color=NEG, sw=2.4, dash="6,5")
        for n, (x, y) in pts.items():
            s += circle(x, y, 13, fill="#fff", stroke=INK, sw=2)
            s += text(x, y + 5, str(n), size=12, color=INK, bold=True)
        return s
    # ліва панель — дерево
    parts.append(text(150, 88, "Кістякове дерево", size=13, color=FIELD, bold=True))
    parts.append(graph(70, True))
    parts.append(text(150, 288, "сполучає всі N вузлів, БЕЗ контурів",
                      size=11, color=MUTED, italic=True))
    parts.append(text(150, 310, "гілок дерева: завжди N − 1 = 3", size=12, color=INK, bold=True))
    # права панель — дерево + хорди
    parts.append(text(560, 88, "+ хорди (решта гілок)", size=13, color=NEG, bold=True))
    parts.append(graph(480, False))
    parts.append(text(560, 288, "кожна хорда замикає 1 контур",
                      size=11, color=MUTED, italic=True))
    parts.append(text(560, 310, "хорд: B − N + 1 = 2  →  стільки й контурів",
                      size=12, color=INK, bold=True))
    parts.append(text(W / 2, 332,
                      "N−1 незалежних балансів струмів  ·  B−N+1 незалежних контурів",
                      size=12, color=INK, italic=True))
    render(out("tree-cotree.svg"), W, H, *parts,
           title="Дерево й хорди: звідки беруться N−1 і B−N+1")


# ── bridge-reduce.svg — місток Вітстона через Y-Δ ───────────────────────────
def fig_bridge_reduce():
    W, H = 780, 360
    parts = []
    # ── крок 0: місток (ромб) ──
    def bridge(ox, oy):
        T = (ox + 80, oy)          # верх (джерело)
        A = (ox + 20, oy + 70)     # ліво
        B = (ox + 140, oy + 70)    # право
        D = (ox + 80, oy + 140)    # низ
        s = line(*T, *A, color=INK, sw=2) + line(*T, *B, color=INK, sw=2)
        s += line(*A, *D, color=INK, sw=2) + line(*B, *D, color=INK, sw=2)
        s += line(*A, *B, color=POS, sw=2.4)   # перемичка R5
        for p in (T, A, B, D):
            s += circle(*p, 4, fill=INK, stroke=INK, sw=1)
        s += text((T[0]+A[0])/2-14, (T[1]+A[1])/2, "R₁", size=11, bold=True, italic=True)
        s += text((T[0]+B[0])/2+14, (T[1]+B[1])/2, "R₂", size=11, bold=True, italic=True)
        s += text(ox + 80, oy + 62, "R₅", size=11, color=POS, bold=True, italic=True)
        s += text((A[0]+D[0])/2-14, (A[1]+D[1])/2+6, "R₃", size=11, bold=True, italic=True)
        s += text((B[0]+D[0])/2+14, (B[1]+D[1])/2+6, "R₄", size=11, bold=True, italic=True)
        s += text(T[0], oy - 10, "T", size=10, color=MUTED, bold=True)
        s += text(A[0]-12, A[1]+4, "A", size=10, color=MUTED, bold=True)
        s += text(B[0]+12, B[1]+4, "B", size=10, color=MUTED, bold=True)
        return s
    parts.append(text(120, 78, "1. Місток не згортається", size=12.5, color=INK, bold=True))
    parts.append(bridge(40, 110))
    # ── крок 1: верхній трикутник → зірка ──
    def star(ox, oy):
        T = (ox + 80, oy); A = (ox + 20, oy + 70); B = (ox + 140, oy + 70)
        D = (ox + 80, oy + 140); M = (ox + 80, oy + 55)
        s = line(*T, *M, color=FIELD, sw=2.6) + line(*A, *M, color=FIELD, sw=2.6)
        s += line(*B, *M, color=FIELD, sw=2.6)
        s += line(*A, *D, color=INK, sw=2) + line(*B, *D, color=INK, sw=2)
        for p in (T, A, B, D):
            s += circle(*p, 4, fill=INK, stroke=INK, sw=1)
        s += circle(*M, 4, fill=FIELD, stroke=FIELD, sw=1)
        s += text(M[0]+12, M[1]-2, "M", size=10, color=FIELD, bold=True)
        s += text(T[0]+10, (T[1]+M[1])/2, "R_T", size=10, color=FIELD, bold=True)
        s += text(A[0]+2, (A[1]+M[1])/2+4, "R_A", size=10, color=FIELD, bold=True)
        s += text(B[0]-2, (B[1]+M[1])/2+4, "R_B", size=10, color=FIELD, bold=True, anchor="end")
        s += text((A[0]+D[0])/2-14, (A[1]+D[1])/2+6, "R₃", size=11, bold=True, italic=True)
        s += text((B[0]+D[0])/2+14, (B[1]+D[1])/2+6, "R₄", size=11, bold=True, italic=True)
        return s
    parts.append(text(360, 78, "2. Трикутник (R₁,R₂,R₅) → зірка", size=12.5, color=FIELD, bold=True))
    parts.append(star(290, 110))
    parts.append(arrow(240, 180, 285, 180, color=MUTED, sw=2))
    # ── крок 2: підсумок згортання ──
    parts.append(text(640, 78, "3. Тепер згортається", size=12.5, color=POS, bold=True))
    parts.append(fitbox(560, 110, 190, 150,
                        "R_A+R₃ = 220 Ω\nR_B+R₄ = 220 Ω\n"
                        "220 ∥ 220 = 110 Ω\n"
                        "R_екв = R_T + 110\n     = 40 + 110 = 150 Ω\n"
                        "I = 10/150 = 66.7 мА",
                        size=13, fill="#fdecea", stroke=POS))
    parts.append(arrow(505, 180, 555, 180, color=MUTED, sw=2))
    parts.append(text(W / 2, 344,
                      "Y-Δ прибирає зчепленість → повертає послідовно-паралельні пари → згортання оживає",
                      size=11.5, color=INK, italic=True))
    render(out("bridge-reduce.svg"), W, H, *parts,
           title="Місток Вітстона: Y-Δ розчищає шлях згортанню")


# ── superposition.svg — накладання ──────────────────────────────────────────
def fig_superposition():
    W, H = 780, 320
    parts = []
    def cell(ox, title, e1, e2, col):
        # маленька рамкова схема: два джерела ліворуч/праворуч, R3 у центр вниз
        s = text(ox + 95, 78, title, size=12, color=col, bold=True)
        L, R, top, bot = ox + 30, ox + 160, 100, 210
        mid = (L + R) / 2
        s += line(L, top, R, top, color=INK, sw=1.8)
        s += line(L, bot, R, bot, color=INK, sw=1.8)
        s += line(mid, top, mid, 150, color=INK, sw=1.8)
        s += res_v(mid, 175, "R₃", side="right") if False else ""
        s += rect(mid - 8, 150, 16, 40, fill="#fff", stroke=INK, sw=1.8, rx=2)
        # ліве плече
        if e1 == "V":
            s += line(L, top, L, 135, color=INK, sw=1.8)
            s += line(L - 9, 138, L + 9, 138, color=INK, sw=3)
            s += line(L - 5, 146, L + 5, 146, color=INK, sw=2)
            s += line(L, 154, L, bot, color=INK, sw=1.8)
            s += text(L - 12, 150, "V₁", size=10, color=POS, bold=True, anchor="end")
        else:  # закорочено
            s += line(L, top, L, bot, color=NEG, sw=2.6)
            s += text(L - 12, 150, "0", size=11, color=NEG, bold=True, anchor="end")
        # праве плече
        if e2 == "V":
            s += line(R, top, R, 135, color=INK, sw=1.8)
            s += line(R - 9, 138, R + 9, 138, color=INK, sw=3)
            s += line(R - 5, 146, R + 5, 146, color=INK, sw=2)
            s += line(R, 154, R, bot, color=INK, sw=1.8)
            s += text(R + 12, 150, "V₂", size=10, color=POS, bold=True, anchor="start")
        else:
            s += line(R, top, R, bot, color=NEG, sw=2.6)
            s += text(R + 12, 150, "0", size=11, color=NEG, bold=True, anchor="start")
        s += text(mid, 172, "R₃", size=10, bold=True, italic=True)
        return s
    parts.append(cell(0, "живе лише V₁ (V₂ закорочено)", "V", "0", NEG))
    parts.append(cell(220, "живе лише V₂ (V₁ закорочено)", "0", "V", NEG))
    parts.append(text(305, 240, "Vₐ' = 4.0 В", size=12, color=INK, bold=True))
    parts.append(text(305, 258, "+  Vₐ'' = 2.4 В", size=12, color=INK, bold=True))
    # знак суми праворуч
    parts.append(fitbox(560, 100, 200, 130,
                        "повний відгук =\nсума часткових\n\n"
                        "Vₐ = 4.0 + 2.4\n    = 6.4 В  ✓",
                        size=14, fill="#eef7f0", stroke=FIELD))
    parts.append(text(490, 155, "→", size=26, color=FIELD, bold=True))
    parts.append(text(W / 2, 300,
                      "Лінійне коло: увімкни джерела по черзі й склади відгуки "
                      "(струми/напруги — можна, потужність — НІ)",
                      size=11.5, color=INK, italic=True))
    render(out("superposition.svg"), W, H, *parts,
           title="Накладання: розбити задачу з багатьма джерелами на прості")


# ── thevenin.svg — еквівалент Тевенена/Нортона ──────────────────────────────
def fig_thevenin():
    W, H = 780, 320
    parts = []
    # ── «хмара» складної схеми ──
    cx, cy = 130, 170
    parts.append('<ellipse cx="%d" cy="%d" rx="86" ry="60" fill="%s" stroke="%s" '
                 'stroke-width="2"/>' % (cx, cy, FILL, MUTED))
    parts.append(mtext(cx, cy - 8, "будь-яка\nлінійна схема",
                       size=13, color=INK, bold=True, lh=1.25))
    parts.append(text(cx, cy + 28, "(десятки елементів)", size=10, color=MUTED))
    parts.append(line(cx + 86, cy - 20, cx + 150, cy - 20, color=INK, sw=2))
    parts.append(line(cx + 86, cy + 20, cx + 150, cy + 20, color=INK, sw=2))
    parts.append(circle(cx + 150, cy - 20, 4, fill=INK, stroke=INK, sw=1))
    parts.append(circle(cx + 150, cy + 20, 4, fill=INK, stroke=INK, sw=1))
    parts.append(text(cx + 150, cy - 30, "затискачі", size=10, color=MUTED))
    parts.append(arrow(cx + 158, cy, cx + 210, cy, color=FIELD, sw=2.6))
    parts.append(text(cx + 184, cy - 8, "≡", size=18, color=FIELD, bold=True))
    # ── еквівалент Тевенена ──
    tx = 430
    parts.append(text(tx + 20, 92, "Тевенен", size=13, color=INK, bold=True))
    parts.append(line(tx + 20, 130, tx + 20, 150, color=INK, sw=2))
    parts.append(line(tx + 11, 130, tx + 29, 130, color=INK, sw=3))
    parts.append(line(tx + 15, 122, tx + 25, 122, color=INK, sw=2))
    parts.append(line(tx + 20, 108, tx + 20, 122, color=INK, sw=2))
    parts.append(text(tx - 4, 128, "V_th", size=11, color=POS, bold=True, anchor="end"))
    parts.append(rect(tx + 12, 150, 16, 44, fill="#fff", stroke=INK, sw=2, rx=2))
    parts.append(text(tx + 38, 176, "R_th", size=11, color=INK, bold=True, italic=True, anchor="start"))
    parts.append(line(tx + 20, 194, tx + 20, 214, color=INK, sw=2))
    parts.append(line(tx + 20, 108, tx + 60, 108, color=INK, sw=2))
    parts.append(line(tx + 20, 214, tx + 60, 214, color=INK, sw=2))
    parts.append(circle(tx + 60, 108, 4, fill=INK, stroke=INK, sw=1))
    parts.append(circle(tx + 60, 214, 4, fill=INK, stroke=INK, sw=1))
    # ── формули праворуч ──
    parts.append(fitbox(560, 92, 200, 150,
                        "V_th = напруга на\nРОЗІМКНЕНИХ\nзатискачах\n\n"
                        "R_th = опір із затискачів,\nусі джерела вимкнено\n"
                        "(V→дріт, I→розрив)",
                        size=12, fill="#f6f8fc", stroke=INK))
    parts.append(text(W / 2, 268,
                      "Нортон — дуально: I_n = V_th/R_th паралельно з тим самим R_th",
                      size=12, color=NEG, bold=True))
    parts.append(text(W / 2, 296,
                      "Максимум потужності в навантаженні — коли R_н = R_th (узгодження)",
                      size=11, color=MUTED, italic=True))
    render(out("thevenin.svg"), W, H, *parts,
           title="Тевенен: складну двополюсну схему — до V_th і R_th")


# ── method-map.svg — карта вибору методу ────────────────────────────────────
def fig_method_map():
    W, H = 780, 360
    parts = []
    rows = [
        ("Згортається (послід./парал.)?", "→ згортання + дільники", "найшвидше", FIELD),
        ("Місток / зчеплені трикутники?", "→ спершу Y-Δ, тоді згортання", "оживляє згортання", "#8e44ad"),
        ("Кілька джерел?", "→ накладання АБО система", "внесок кожного окремо", NEG),
        ("Одне навантаження, різні номінали?", "→ Тевенен / Нортон", "усе інше — 2 числа", POS),
        ("Багато вузлів і гілок?", "→ вузловий чи контурний", "бери, де менше невідомих", "#e08030"),
    ]
    x0, y0, rw, rh, gap = 60, 66, 660, 40, 8
    for i, (q, a, note, col) in enumerate(rows):
        y = y0 + i * (rh + gap)
        parts.append(rect(x0, y, rw, rh, fill=FILL, stroke=col, sw=2, rx=8))
        parts.append(rect(x0, y, 8, rh, fill=col, sw=0, rx=0))
        parts.append(text(x0 + 22, y + rh / 2 + 5, q, size=13, color=INK, bold=True, anchor="start"))
        parts.append(text(x0 + 350, y + rh / 2 + 5, a, size=13, color=col, bold=True, anchor="start"))
        parts.append(text(x0 + rw - 12, y + rh / 2 + 5, note, size=10.5, color=MUTED,
                          italic=True, anchor="end"))
    cy = y0 + 5 * (rh + gap) + 16
    parts.append(rect(x0, cy, rw, 40, fill="#eef7f0", stroke=FIELD, sw=2, rx=8))
    parts.append(text(W / 2, cy + 25,
                      "І ЗАВЖДИ наприкінці — три самоперевірки: одиниці · баланси Кірхгофа · порядок величин",
                      size=12.5, color=FIELD, bold=True))
    render(out("method-map.svg"), W, H, *parts,
           title="Карта вибору методу аналізу кіл")


# ── math-y-delta: фігури для вставки про виведення Y-Δ ───────────────────────
def _triangle(cx, cy, r, labels=("R₁₂", "R₂₃", "R₃₁"), nodes=("1", "2", "3"),
              hot=None, col=INK):
    """Трикутник: вузол 1 угорі, 2 — знизу-ліворуч, 3 — знизу-праворуч.
    Сторона R₁₂ (1–2) ліва, R₂₃ (2–3) низ, R₃₁ (3–1) права. hot — індекс
    сторони (0/1/2), яку підсвітити POS-кольором."""
    import math
    N1 = (cx, cy - r)
    N2 = (cx - r * 0.87, cy + r * 0.5)
    N3 = (cx + r * 0.87, cy + r * 0.5)
    P = (N1, N2, N3)
    sides = [(N1, N2), (N2, N3), (N3, N1)]   # 1–2, 2–3, 3–1
    s = ""
    for i, (a, b) in enumerate(sides):
        c = POS if hot == i else col
        sw = 3.0 if hot == i else 2.2
        s += line(*a, *b, color=c, sw=sw)
    # підписи сторін — трохи назовні від середини
    mids = [((N1[0]+N2[0])/2 - 16, (N1[1]+N2[1])/2),
            ((N2[0]+N3[0])/2, (N2[1]+N3[1])/2 + 16),
            ((N3[0]+N1[0])/2 + 16, (N3[1]+N1[1])/2)]
    for i, (mx, my) in enumerate(mids):
        c = POS if hot == i else INK
        s += text(mx, my, labels[i], size=13, color=c, bold=True, italic=True)
    for i, p in enumerate(P):
        s += circle(*p, 5, fill=INK, stroke=INK, sw=1)
        dx = 0 if i == 0 else (-14 if i == 1 else 14)
        dy = -12 if i == 0 else 6
        s += text(p[0] + dx, p[1] + dy, nodes[i], size=12, color=MUTED, bold=True)
    return s, P


def _star(cx, cy, r, labels=("Rₐ", "R_b", "R_c"), nodes=("1", "2", "3"),
          hot=(), col=FIELD):
    """Зірка: центр M, промені до вузлів 1 (угорі), 2 (низ-ліво), 3 (низ-право).
    hot — набір індексів променів (0/1/2), які підсвітити."""
    M = (cx, cy)
    N1 = (cx, cy - r)
    N2 = (cx - r * 0.87, cy + r * 0.5)
    N3 = (cx + r * 0.87, cy + r * 0.5)
    P = (N1, N2, N3)
    s = ""
    for i, p in enumerate(P):
        c = POS if i in hot else col
        sw = 3.2 if i in hot else 2.6
        s += line(*M, *p, color=c, sw=sw)
    labpos = [(N1[0] + 14, (N1[1] + M[1]) / 2),
              ((N2[0] + M[0]) / 2 - 4, (N2[1] + M[1]) / 2 + 12),
              ((N3[0] + M[0]) / 2 + 4, (N3[1] + M[1]) / 2 + 12)]
    for i, (lx, ly) in enumerate(labpos):
        c = POS if i in hot else FIELD
        s += text(lx, ly, labels[i], size=13, color=c, bold=True)
    for i, p in enumerate(P):
        s += circle(*p, 5, fill=INK, stroke=INK, sw=1)
        dx = 0 if i == 0 else (-14 if i == 1 else 14)
        dy = -12 if i == 0 else 6
        s += text(p[0] + dx, p[1] + dy, nodes[i], size=12, color=MUTED, bold=True)
    s += circle(*M, 5, fill=FIELD, stroke=FIELD, sw=1)
    s += text(M[0] + 12, M[1] - 2, "M", size=11, color=FIELD, bold=True)
    return s, P, M


# ── ydelta-pair.svg — що таке «опір між парою» в кожній фігурі ───────────────
def fig_ydelta_pair():
    W, H = 780, 380
    parts = []
    parts.append(text(W / 2, 52,
                      "Умова еквівалентності: опір між кожною парою зовнішніх вузлів — однаковий",
                      size=13, color=INK, bold=True))
    # ліворуч: трикутник, підсвічена «дорога» між вузлами 1 і 2
    tS, tP = _triangle(190, 175, 92, hot=0)
    parts.append(text(190, 92, "ТРИКУТНИК (Δ)", size=13, color=INK, bold=True))
    parts.append(tS)
    # праворуч: зірка, підсвічені промені a і b (шлях 1→M→2)
    sS, sP, sM = _star(590, 175, 92, hot=(0, 1))
    parts.append(text(590, 92, "ЗІРКА (Y)", size=13, color=FIELD, bold=True))
    parts.append(sS)
    # пояснення внизу — дві рамки з тим, що дає кожна фігура для пари 1–2
    parts.append(fitbox(60, 288, 300, 70,
                        "між 1 і 2: пряма сторона R₁₂\n"
                        "паралельно з обхідною R₂₃+R₃₁\n"
                        "R₁₂ ∥ (R₂₃ + R₃₁)",
                        size=12.5, fill="#fdecea", stroke=POS))
    parts.append(fitbox(420, 288, 300, 70,
                        "між 1 і 2: два промені підряд,\n"
                        "третій (R_c) висить у нікуди\n"
                        "Rₐ + R_b",
                        size=12.5, fill="#eef7f0", stroke=FIELD))
    parts.append(text(W / 2, 372,
                      "Прирівняй ці два вирази для кожної з трьох пар — і дістанеш систему на формули",
                      size=11.5, color=INK, italic=True))
    render(out("ydelta-pair.svg"), W, H, *parts,
           title="Зірка ↔ трикутник: що прирівнюємо")


# ── ydelta-equal.svg — симетричний випадок R_Y = R_Δ/3 ──────────────────────
def fig_ydelta_equal():
    W, H = 780, 330
    parts = []
    parts.append(text(W / 2, 52, "Рівні опори: звідки береться множник 3",
                      size=13, color=INK, bold=True))
    tS, tP = _triangle(190, 165, 88,
                       labels=("R", "R", "R"), col=INK)
    parts.append(text(190, 82, "Δ: усі сторони R", size=12.5, color=INK, bold=True))
    parts.append(tS)
    sS, sP, sM = _star(560, 165, 88,
                       labels=("R/3", "R/3", "R/3"), col=FIELD)
    parts.append(text(560, 82, "Y: усі промені R/3", size=12.5, color=FIELD, bold=True))
    parts.append(sS)
    parts.append(arrow(300, 165, 455, 165, color=MUTED, sw=2.2))
    parts.append(fitbox(300, 196, 155, 74,
                        "Δ→Y:\nR·R / (3R)\n= R/3",
                        size=13, fill="#eef7f0", stroke=FIELD))
    parts.append(text(W / 2, 300,
                      "Пара в Δ: R ∥ 2R = 2R/3.  Пара в Y: R/3 + R/3 = 2R/3.  Збігається ✓",
                      size=11.5, color=INK, italic=True))
    parts.append(text(W / 2, 320,
                      "Трикутник «жорсткіший» — щоб зірка була така сама, її промені втричі менші",
                      size=11, color=MUTED, italic=True))
    render(out("ydelta-equal.svg"), W, H, *parts,
           title="Симетрія: R_Y = R_Δ / 3")


# ── hist-network-theorems: часова смуга мережевих теорем ─────────────────────
def fig_theorems_timeline():
    """Хто, коли й що: Гельмгольц-першоджерело, дві незалежні перевідкриття
    (Тевенен; Нортон+Маєр) та окрема гілка Кеннеллі (Y-Δ)."""
    W, H = 900, 440
    parts = []
    # вісь часу
    x0, x1 = 150, 760
    axy = 360
    def X(year):
        return x0 + (x1 - x0) * (year - 1850) / (1930 - 1850)
    parts.append(line(x0 - 20, axy, x1 + 20, axy, color=INK, sw=2.4))
    for yr in (1850, 1870, 1890, 1910, 1930):
        parts.append(line(X(yr), axy - 5, X(yr), axy + 5, color=INK, sw=2))
        parts.append(text(X(yr), axy + 22, str(yr), size=12, color=MUTED, bold=True))

    # подія: кружок на осі + картка на висоті cy (центр bx для широких карток)
    def event(year, title, who, col, cy, bx=None):
        px = X(year)
        cx = px if bx is None else bx
        s = circle(px, axy, 6, fill=col, stroke=col, sw=1)
        s += line(px, axy, cx, cy + 30, color=col, sw=1.6, dash="3,3")
        box, bw, bh = textbox(cx, cy, "%d · %s\n%s" % (year, title, who),
                              size=12, pad=9, fill=FILL, stroke=col, sw=2,
                              color=INK, bold=False)
        return s + box, px

    # чотири картки на різних висотах, щоб не налазили; центри зсунуті всередину
    e1, x_h = event(1853, "Гельмгольц", "накладання + джерело напруги",
                    POS, 250, bx=250)
    e3, x_k = event(1899, "Кеннеллі", "зірка ⇄ трикутник (Y-Δ)",
                    "#8e44ad", 250, bx=560)
    e2, x_t = event(1883, "Тевенен", "джерело напруги, незалежно",
                    NEG, 165, bx=405)
    e4, x_n = event(1926, "Нортон + Маєр", "струмова форма, незалежно",
                    FIELD, 165, bx=690)
    for e in (e1, e3, e2, e4):
        parts.append(e)

    # дуги «перевідкрито незалежно» під осями подій: Гельмгольц→Тевенен→Нортон/Маєр
    def redisc(xa, xb, label):
        my = 78
        s = ('<path d="M %.1f 108 C %.1f %d, %.1f %d, %.1f 108" fill="none" '
             'stroke="%s" stroke-width="1.8" stroke-dasharray="5,4" '
             'marker-end="url(#arrow)"/>'
             % (xa, xa, my, xb, my, xb, MUTED))
        s += text((xa + xb) / 2, my - 6, label, size=11, color=MUTED, italic=True)
        return s
    parts.append(redisc(x_h, x_t, "перевідкрито незалежно"))
    parts.append(redisc(x_t, x_n, "і ще раз — двічі"))

    # легенда-висновок унизу
    parts.append(fitbox(80, 392, 740, 34,
                        "Одна ідея (двополюсник ⇄ джерело + опір) — тричі відкрита незалежно; "
                        "Y-Δ Кеннеллі — окремий інструмент, що ріже саме те з'єднання, яке не згортається",
                        size=11.5, fill="#f4f6f8", stroke=MUTED, sw=1.5))
    render(out("theorems-timeline.svg"), W, H, *parts,
           title="Мережеві теореми: хто, коли — і що перевідкрито незалежно")


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
    # детальна стаття
    fig_tree_cotree()
    fig_bridge_reduce()
    fig_superposition()
    fig_thevenin()
    fig_method_map()
    # вставка math-y-delta
    fig_ydelta_pair()
    fig_ydelta_equal()
    # вставка hist-network-theorems
    fig_theorems_timeline()
    print("Згенеровано фігури статті та вставок у", IMG)


if __name__ == "__main__":
    main()
