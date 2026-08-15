# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F  = "#e8eefc"
RED_F   = "#fdecea"
GREEN_F = "#e6f7ee"
QUAD_F  = "#eef4ff"

# ── 1. diophantine-classification: Класифікація діофантових рівнянь ────────────
def fig_classification():
    W, H = 1060, 560
    p = []
    
    p.append(text(W / 2, 36, "Класифікація діофантових рівнянь за степенем та геометрією",
                  size=16, color=INK, bold=True))
    
    categories = [
        ("Лінійні", "Степінь 1", "ax + by = c", "НСД(a, b) ділить c", GREEN_F, FIELD, 70),
        ("Квадратичні", "Степінь 2", "x² - dy² = 1 (Пелль)\nx² + y² = z² (Піфагор)", "Коніки, дискримінант,\nпринцип Гассе", BLUE_F, NEG, 310),
        ("Кубічні / Еліптичні", "Степінь 3", "y² = x³ + ax + b", "Група раціональних точок,\nтеорема Морделла-Вейля", QUAD_F, "#7b1fa2", 550),
        ("Вищі степені", "Степінь n ≥ 3", "xⁿ + yⁿ = zⁿ (Ферма)", "Теорема Фальтінгса (g ≥ 2),\nскінченність розв'язків", RED_F, POS, 790)
    ]
    
    for title, deg, eq, desc, fill_c, stroke_c, x_pos in categories:
        box_w = 200
        p.append(rect(x_pos, 80, box_w, 40, fill=stroke_c, stroke=stroke_c, sw=1.5, rx=6))
        p.append(text(x_pos + box_w / 2, 105, title, size=14, color=BG, bold=True))
        
        p.append(rect(x_pos, 125, box_w, 30, fill=fill_c, stroke=stroke_c, sw=1, rx=4))
        p.append(text(x_pos + box_w / 2, 145, deg, size=12.5, color=stroke_c, bold=True))
        
        p.append(rect(x_pos, 160, box_w, 80, fill=FILL, stroke=LINE, sw=1.5, rx=6))
        p.append(mtext(x_pos + box_w / 2, 195, eq, size=13, color=INK, bold=True, lh=1.4))
        
        p.append(rect(x_pos, 245, box_w, 90, fill=BG, stroke=LINE, sw=1, rx=6))
        p.append(mtext(x_pos + box_w / 2, 280, desc, size=12, color=MUTED, lh=1.4))

    p.append(rect(70, 375, 920, 140, fill=RED_F, stroke=POS, sw=2, rx=8))
    p.append(text(W / 2, 405, "10-та проблема Гільберта та теорема Матіясевича (MRDP, 1970)",
                  size=15, color=POS, bold=True))
    p.append(mtext(W / 2, 440,
                   "Не існує єдиного алгоритму, який визначає наявність цілих розв'язків для довільного діофантового рівняння.\n"
                   "Загальна задача алгоритмічно нерозв'язна (еквівалентна здатності емулювати будь-яку обчислювану функцію).",
                   size=13, color=INK, lh=1.5))

    return render(os.path.join(OUT, "diophantine-classification.svg"), W, H, *p)


# ── 2. modular-obstruction: Модульні перешкоди (неіснування розв'язків) ───────
def fig_modular_obstruction():
    W, H = 1040, 520
    p = []
    
    p.append(text(W / 2, 36, "Метод модульних перешкод: чому рівняння x² - 3y² = 2 не має цілих розв'язків",
                  size=16, color=INK, bold=True))

    xL = 60
    p.append(rect(xL, 75, 430, 390, fill=QUAD_F, stroke=NEG, sw=1.8, rx=8))
    p.append(text(xL + 215, 105, "Аналіз за модулем 3 (mod 3)", size=15, color=NEG, bold=True))
    
    p.append(mtext(xL + 20, 140,
                   "Розглянемо рівняння  x² − 3y² = 2  за модулем 3:\n"
                   "Оскільки 3y² ≡ 0 (mod 3), рівняння спрощується до:",
                   size=13, color=INK, anchor="start", lh=1.4))
    
    p.append(rect(xL + 80, 190, 270, 45, fill=RED_F, stroke=POS, sw=2, rx=6))
    p.append(text(xL + 215, 218, "x² ≡ 2 (mod 3)", size=16, color=POS, bold=True))

    p.append(text(xL + 20, 265, "Таблиця можливих квадратів modulo 3:", size=13, color=INK, anchor="start", bold=True))

    table_y = 285
    p.append(rect(xL + 50, table_y, 330, 90, fill=BG, stroke=LINE, sw=1.5, rx=4))
    p.append(line(xL + 50, table_y + 30, xL + 380, table_y + 30, color=LINE, sw=1.2))
    p.append(line(xL + 160, table_y, xL + 160, table_y + 90, color=LINE, sw=1.2))
    
    p.append(text(xL + 105, table_y + 20, "x (mod 3)", size=12.5, color=MUTED, bold=True))
    p.append(text(xL + 270, table_y + 20, "x² (mod 3)", size=12.5, color=MUTED, bold=True))
    
    for i, (val_x, val_x2) in enumerate([("0", "0"), ("1", "1"), ("2 (≡ −1)", "1")]):
        ty = table_y + 48 + i * 18
        p.append(text(xL + 105, ty, val_x, size=12, color=INK))
        p.append(text(xL + 270, ty, val_x2, size=12, color=NEG, bold=True))

    p.append(text(xL + 215, 410, "Квадрат цілого числа за mod 3 дає ЛИШЕ 0 або 1!", size=13, color=POS, bold=True))
    p.append(text(xL + 215, 435, "Остача 2 є модульною перешкодою → розв'язків немає.", size=12.5, color=INK))

    xR = 530
    p.append(rect(xR, 75, 450, 390, fill=GREEN_F, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(xR + 225, 105, "Локально-глобальний принцип (Гассе)", size=15, color=FIELD, bold=True))

    p.append(mtext(xR + 20, 145,
                   "Глобальний розв'язок (у цілих числах ℤ або раціональних ℚ)\n"
                   "вимагає наявності локальних розв'язків усюди:",
                   size=13, color=INK, anchor="start", lh=1.5))

    p.append(rect(xR + 40, 210, 370, 50, fill=BG, stroke=FIELD, sw=1.5, rx=6))
    p.append(text(xR + 225, 240, "Розв'язок у ℤ  ⇒  Розв'язок у ℤ / mℤ  для ВСІХ m ≥ 2", size=13.5, color=FIELD, bold=True))

    p.append(mtext(xR + 20, 290,
                   "Якщо знайдено ХОЧ ОДИН модуль m, для якого\n"
                   "порівняння не має розв'язку — цілочисельний розв'язок\n"
                   "НЕМОЖЛИВИЙ В ПРИНЦИПІ (локальна перешкода).",
                   size=13, color=INK, anchor="start", lh=1.5))

    p.append(rect(xR + 40, 370, 370, 65, fill=RED_F, stroke=POS, sw=1.5, rx=6))
    p.append(mtext(xR + 225, 398,
                   "Застереження: для рівнянь вищих степеней (n ≥ 3)\n"
                   "відсутність модульних перешкод НЕ гарантує наявності розв'язку!",
                   size=12, color=POS, bold=True, lh=1.4))

    return render(os.path.join(OUT, "modular-obstruction.svg"), W, H, *p)


# ── 3. fermat-descent: Нескінченний спуск Ферма ───────────────────────────────
def fig_fermat_descent():
    W, H = 1040, 500
    p = []

    p.append(text(W / 2, 36, "Метод нескінченного спуску Ферма: доведення відсутності розв'язків",
                  size=16, color=INK, bold=True))

    steps = [
        ("1. Припущення", "(x₀, y₀, z₀)", "Припускаємо існування\nнайменшого натурального\nрозв'язку з z₀ > 0", BLUE_F, NEG, 60),
        ("2. Алгебра", "z₁ < z₀", "Шляхом подільності\nта перетворень будуємо\nновий розв'язок (x₁, y₁, z₁)", QUAD_F, "#7b1fa2", 300),
        ("3. Ітерація", "z₀ > z₁ > z₂ > ...", "Повторення процедури дає\nнескінченний спадний ланцюг\nпозитивних цілих чисел", RED_F, POS, 540),
        ("4. Суперечність", "∄ нескінченного спуску", "Множина ℕ цілком впорядкована:\nне існує нескінченного спадного\nланцюга натуральних чисел!", GREEN_F, FIELD, 780)
    ]

    for i, (title, formula, desc, fill_c, stroke_c, x_pos) in enumerate(steps):
        w_box = 200
        p.append(rect(x_pos, 80, w_box, 35, fill=stroke_c, stroke=stroke_c, sw=1.5, rx=6))
        p.append(text(x_pos + w_box / 2, 102, title, size=13.5, color=BG, bold=True))
        
        p.append(rect(x_pos, 120, w_box, 45, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        p.append(text(x_pos + w_box / 2, 148, formula, size=14, color=stroke_c, bold=True))
        
        p.append(rect(x_pos, 175, w_box, 90, fill=FILL, stroke=LINE, sw=1, rx=6))
        p.append(mtext(x_pos + w_box / 2, 210, desc, size=12, color=INK, lh=1.4))

        if i < len(steps) - 1:
            arrow_start_x = x_pos + w_box + 5
            arrow_end_x = x_pos + w_box + 35
            p.append(arrow(arrow_start_x, 142, arrow_end_x, 142, color=LINE, sw=2))

    p.append(rect(60, 290, 920, 180, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(W / 2, 315, "Геометрично: нескінченний спуск по ступенях натурального ряду", size=14, color=INK, bold=True))

    st_x = 120
    st_y = 350
    step_w = 160
    step_h = 25
    
    for k in range(4):
        cx = st_x + k * step_w
        cy = st_y + k * step_h
        p.append(rect(cx, cy, step_w, 20, fill=QUAD_F if k < 3 else RED_F, stroke=NEG if k < 3 else POS, sw=1.5, rx=4))
        lbl = f"z_{k} = {100 - k*28}" if k < 3 else "z_k → ... ⚡"
        p.append(text(cx + step_w / 2, cy + 14, lbl, size=12, color=INK, bold=True))
        if k < 3:
            p.append(arrow(cx + step_w - 20, cy + 20, cx + step_w + 10, cy + step_h + 10, color=POS, sw=1.8))

    p.append(text(780, 410, "Зупинка у 0!", size=14, color=POS, bold=True))
    p.append(text(780, 435, "Розв'язку у ℕ > 0 не існує.", size=13, color=FIELD, bold=True))

    return render(os.path.join(OUT, "fermat-descent.svg"), W, H, *p)


# ── 4. solver-flow: керуючий потік розв'язника ───────────────────────────────
def fig_solver_flow():
    W, H = 880, 690
    p = []
    p.append(text(W / 2, 32, "Розв'язник  a·x + b·y = c:  від входу до переліку",
                  size=16.5, color=INK, bold=True))

    MX, MW = 60, 380
    EX, EW = 530, 330
    cxm = MX + MW / 2

    def box(y, h, s, fill=FILL, stroke=MUTED, x=MX, w=MW, bold=False, size=13.5):
        p.append(rect(x, y - h/2, w, h, fill=fill, stroke=stroke, sw=1.8, rx=6))
        lines = s.split("\n")
        ty = y - (len(lines)-1)*size*1.3/2 + size*0.35
        p.append(mtext(x + w/2, ty, lines, size=size, color=INK, bold=bold))

    def down(y1, y2):
        p.append(arrow(cxm, y1, cxm, y2, color=INK, sw=1.9))

    def right(ymid, label):
        p.append(arrow(MX + MW, ymid, EX, ymid, color=MUTED, sw=1.8))
        p.append(text((MX + MW + EX) / 2, ymid - 8, label, size=12, color=MUTED, italic=True))

    box(62, 44, "вхід:  цілі  a, b, c")
    box(128, 44, "a = 0  і  b = 0 ?", fill=BLUE_F, stroke=NEG, bold=True)
    box(196, 52, "d = НСД(a, b),  розшир. Евклід:\nx₀, y₀ :  a·x₀ + b·y₀ = d")
    box(284, 44, "d  ділить  c ?", fill=BLUE_F, stroke=NEG, bold=True)
    box(356, 52, "один розв'язок:\nx₁ = x₀·(c/d),   y₁ = y₀·(c/d)")
    box(444, 52, "уся родина:\nx = x₁ + (b/d)·t,   y = y₁ − (a/d)·t")
    box(530, 44, "зведення:   t  →  найменший  | x |")
    box(598, 52, "вікно t:  x ≥ 0  і  y ≥ 0\n→  перелік невід'ємних",
        fill=GREEN_F, stroke=FIELD, bold=True)

    box(124, 52, "так, c = 0  →  уся площина\nтак, c ≠ 0  →  немає розв'язку",
        x=EX, w=EW, fill=FILL, stroke=MUTED, size=12.5)
    box(284, 44, "ні   →   немає розв'язку",
        x=EX, w=EW, fill=RED_F, stroke=POS, bold=True)
    box(598, 52, "a чи b = 0, або різні знаки\n→  нескінченно багато",
        x=EX, w=EW, fill=FILL, stroke=MUTED, size=12.5)

    for y1, y2 in ((84, 106), (150, 170), (222, 262), (306, 330),
                   (382, 418), (470, 508), (552, 572)):
        down(y1, y2)

    right(128, "так")
    right(284, "ні")
    right(598, "інакше")

    return render(os.path.join(OUT, "solver-flow.svg"), W, H, *p)


for f in (fig_classification, fig_modular_obstruction, fig_fermat_descent, fig_solver_flow):
    print("написано:", f())
