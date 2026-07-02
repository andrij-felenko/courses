# -*- coding: utf-8 -*-
"""Фігури теми «Перетворення зірка–трикутник». Запуск: python figs.py → ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)
P = lambda name: os.path.join(OUT, name)


def resistor(x1, y1, x2, y2, label=None, lab_dx=0, lab_dy=0, lab_color=INK):
    """Резистор-прямокутник на відрізку (x1,y1)-(x2,y2), з короткими виводами."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L          # напрямок
    nx, ny = -uy, ux                 # нормаль
    body = 30.0                      # довжина тіла
    lead = (L - body) / 2.0
    ax, ay = x1 + ux * lead, y1 + uy * lead        # початок тіла
    bx, by = x2 - ux * lead, y2 - uy * lead        # кінець тіла
    w = 9.0                          # піврозмах тіла
    out  = line(x1, y1, ax, ay, color=INK, sw=2)
    out += line(bx, by, x2, y2, color=INK, sw=2)
    # чотири кути прямокутника
    c1 = (ax + nx * w, ay + ny * w)
    c2 = (bx + nx * w, by + ny * w)
    c3 = (bx - nx * w, by - ny * w)
    c4 = (ax - nx * w, ay - ny * w)
    out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
            'fill="#fff" stroke="%s" stroke-width="2"/>'
            % (c1[0], c1[1], c2[0], c2[1], c3[0], c3[1], c4[0], c4[1], INK))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        out += text(mx + lab_dx, my + lab_dy, label, size=14, bold=True, color=lab_color)
    return out


def node(cx, cy, name=None, name_dx=0, name_dy=0, big=False):
    out = circle(cx, cy, 5 if big else 4, fill=INK, stroke=INK)
    if name:
        out += text(cx + name_dx, cy + name_dy, name, size=14, bold=True, color=INK)
    return out


# ── 1. Дві форми між трьома клемами: зірка (Y) і трикутник (Δ) ───────────────
def fig_two_shapes():
    W, H = 720, 340
    f = [text(W/2, 26, "Три клеми, дві форми між ними", size=17, bold=True)]

    # клеми — вершини рівнобічного трикутника, спільні для обох панелей
    # ЛІВА панель: зірка
    ax, ay = 60, 300      # A ліворуч знизу
    bx, by = 300, 300     # B праворуч знизу
    cx, cy = 180, 90      # C угорі
    ox, oy = 180, 210     # центр зірки

    f.append(text(180, 58, "Зірка (Y, «трипроменева»)", size=14, bold=True, color=NEG))
    f.append(resistor(ax, ay, ox, oy, label="Rₐ", lab_dx=-16, lab_dy=6, lab_color=NEG))
    f.append(resistor(bx, by, ox, oy, label="R_b", lab_dx=16, lab_dy=6, lab_color=NEG))
    f.append(resistor(cx, cy, ox, oy, label="R_c", lab_dx=16, lab_dy=0, lab_color=NEG))
    f.append(node(ox, oy))
    f.append(text(ox + 4, oy + 20, "спільна", size=11, color=MUTED))
    f.append(text(ox + 4, oy + 34, "точка N", size=11, color=MUTED))
    f.append(node(ax, ay, "A", -14, 6))
    f.append(node(bx, by, "B", 12, 6))
    f.append(node(cx, cy, "C", 0, -12))

    # роздільник
    f.append(line(W/2, 46, W/2, H - 20, color=MUTED, sw=1, dash="5,5"))

    # ПРАВА панель: трикутник
    Ax, Ay = 420, 300
    Bx, By = 660, 300
    Cx, Cy = 540, 90
    f.append(text(540, 58, "Трикутник (Δ, «замкнене кільце»)", size=14, bold=True, color=POS))
    # плече проти клеми: R_A навпроти A -> сторона B-C; R_B навпроти B -> A-C; R_C навпроти C -> A-B
    f.append(resistor(Bx, By, Cx, Cy, label="R_A", lab_dx=22, lab_dy=-2, lab_color=POS))
    f.append(resistor(Ax, Ay, Cx, Cy, label="R_B", lab_dx=-22, lab_dy=-2, lab_color=POS))
    f.append(resistor(Ax, Ay, Bx, By, label="R_C", lab_dx=0, lab_dy=20, lab_color=POS))
    f.append(node(Ax, Ay, "A", -14, 6))
    f.append(node(Bx, By, "B", 12, 6))
    f.append(node(Cx, Cy, "C", 0, -12))

    f.append(text(W/2, H - 6, "Ззовні — на клемах A, B, C — обидві схеми поводяться однаково.",
                  size=12, color=INK))
    render(P("two-shapes.svg"), W, H, *f)


# ── 2. Міст: чому послідовно-паралельно не бере, і як один Δ→Y розв'язує ──────
def fig_bridge_unlock():
    W, H = 720, 360
    f = [text(W/2, 26, "Місток: жодна пара плечей не послідовна й не паралельна", size=16, bold=True)]

    # ЛІВА: класичний місток-діамант
    # вузли: T (верх), Bt (низ), Lm (ліворуч, вузол D), Rm (праворуч)
    Tx, Ty = 170, 70
    Btx, Bty = 170, 300
    Lx, Ly = 70, 185
    Rx, Ry = 270, 185
    f.append(resistor(Tx, Ty, Lx, Ly, label="R₁", lab_dx=-14, lab_dy=-6))
    f.append(resistor(Tx, Ty, Rx, Ry, label="R₂", lab_dx=14, lab_dy=-6))
    f.append(resistor(Lx, Ly, Btx, Bty, label="R₃", lab_dx=-14, lab_dy=6))
    f.append(resistor(Rx, Ry, Btx, Bty, label="R₄", lab_dx=14, lab_dy=6))
    f.append(resistor(Lx, Ly, Rx, Ry, label="R₅", lab_dx=0, lab_dy=-10, lab_color=POS))
    f.append(node(Tx, Ty, "1", 0, -10))
    f.append(node(Btx, Bty, "2", 0, 20))
    f.append(node(Lx, Ly, "D", -14, 4, big=True))
    f.append(node(Rx, Ry, "3", 14, 4))
    # виводи джерела
    f.append(line(Tx, Ty, Tx, Ty - 24, color=INK, sw=2))
    f.append(line(Btx, Bty, Btx, Bty + 24, color=INK, sw=2))
    f.append(text(170, 335, "вхід між 1 і 2", size=11, color=MUTED))
    f.append(text(Lx - 26, Ly - 18, "R₅ — перемичка", size=11, color=POS, anchor="start"))

    # стрілка переходу
    f.append(arrow(315, 185, 385, 185, color=FIELD, sw=2.4))
    f.append(text(350, 172, "Δ→Y", size=13, bold=True, color=FIELD))
    f.append(text(350, 205, "у вузлі D", size=11, color=MUTED))

    # ПРАВА: після заміни трикутника (D,1,3) на зірку — усе стало послідовно-паралельним
    Tx2, Ty2 = 560, 70
    Btx2, Bty2 = 560, 300
    Nx, Ny = 560, 165        # нова спільна точка зірки
    L2x, L2y = 470, 130      # плече до 1 (верх-ліворуч уявно) — намалюємо як три промені у N
    # клеми 1,3 та D навколо N
    n1x, n1y = 560, 95       # клема 1 (верх)
    n3x, n3y = 645, 150      # клема 3
    nDx, nDy = 475, 150      # клема D
    f.append(resistor(n1x, n1y, Nx, Ny, label="Rₐ", lab_dx=14, lab_dy=0, lab_color=NEG))
    f.append(resistor(n3x, n3y, Nx, Ny, label="R_b", lab_dx=6, lab_dy=-8, lab_color=NEG))
    f.append(resistor(nDx, nDy, Nx, Ny, label="R_c", lab_dx=-6, lab_dy=-8, lab_color=NEG))
    f.append(node(Nx, Ny))
    f.append(node(n1x, n1y, "1", 0, -10))
    f.append(node(n3x, n3y, "3", 12, 4))
    f.append(node(nDx, nDy, "D", -12, 4))
    # від D і 3 донизу до вузла 2 через R₃, R₄
    f.append(resistor(nDx, nDy, Btx2, Bty2, label="R₃", lab_dx=-14, lab_dy=0))
    f.append(resistor(n3x, n3y, Btx2, Bty2, label="R₄", lab_dx=14, lab_dy=0))
    f.append(node(Btx2, Bty2, "2", 0, 20))
    f.append(text(560, 335, "тепер: Rₐ послідовно, далі дві гілки паралельно",
                  size=11, color=FIELD))

    render(P("bridge-unlock.svg"), W, H, *f)


# ── 3. Візерунок формул: Δ→Y (добуток/сума) і Y→Δ (сума пар/протилежний) ─────
def fig_formula_pattern():
    W, H = 720, 400
    f = [text(W/2, 26, "Візерунок формул: що куди множити й ділити", size=17, bold=True)]

    # ── верх: Δ → Y ──
    f.append(text(W/2, 62, "Трикутник → Зірка:  плече зірки = добуток двох суміжних сторін ÷ сума всіх трьох",
                  size=13, bold=True, color=NEG))
    # маленький Δ ліворуч із підписаними сторонами
    ax, ay = 70, 190
    bx, by = 250, 190
    cx, cy = 160, 90
    f.append(line(bx, by, cx, cy, color=POS, sw=2.4))   # R_A (проти A)
    f.append(line(ax, ay, cx, cy, color=POS, sw=2.4))   # R_B (проти B)
    f.append(line(ax, ay, bx, by, color=POS, sw=2.4))   # R_C (проти C)
    f.append(text((bx+cx)/2 + 20, (by+cy)/2, "R_A", size=13, bold=True, color=POS))
    f.append(text((ax+cx)/2 - 22, (ay+cy)/2, "R_B", size=13, bold=True, color=POS))
    f.append(text((ax+bx)/2, by + 18, "R_C", size=13, bold=True, color=POS))
    f.append(node(ax, ay, "A", -14, 6))
    f.append(node(bx, by, "B", 12, 6))
    f.append(node(cx, cy, "C", 0, -12))

    # формула Rₐ (плече до A): дві сторони, що торкаються A, це R_B і R_C
    b1 = fitbox(360, 110, 330, 74,
                "Rₐ = (R_B · R_C) / (R_A + R_B + R_C)",
                size=15, bold=True, fill="#eaf0fd", stroke=NEG)
    f.append(b1)
    f.append(text(525, 200, "«суміжні до A» = R_B і R_C (обидва впираються у A)",
                  size=11, color=MUTED))

    # роздільна лінія
    f.append(line(50, 235, W - 50, 235, color=MUTED, sw=1, dash="5,5"))

    # ── низ: Y → Δ ──
    f.append(text(W/2, 268, "Зірка → Трикутник:  сторона = сума попарних добутків ÷ протилежне плече",
                  size=13, bold=True, color=POS))
    # мала зірка ліворуч
    ox, oy = 160, 355
    aX, aY = 70, 385
    bX, bY = 250, 385
    cX, cY = 160, 300
    f.append(line(aX, aY, ox, oy, color=NEG, sw=2.4))
    f.append(line(bX, bY, ox, oy, color=NEG, sw=2.4))
    f.append(line(cX, cY, ox, oy, color=NEG, sw=2.4))
    f.append(text((aX+ox)/2 - 16, (aY+oy)/2 + 4, "Rₐ", size=13, bold=True, color=NEG))
    f.append(text((bX+ox)/2 + 16, (bY+oy)/2 + 4, "R_b", size=13, bold=True, color=NEG))
    f.append(text((cX+ox)/2 + 14, (cY+oy)/2, "R_c", size=13, bold=True, color=NEG))
    f.append(node(ox, oy))
    f.append(node(aX, aY, "A", -14, 6))
    f.append(node(bX, bY, "B", 12, 6))
    f.append(node(cX, cY, "C", 0, -12))

    b2 = fitbox(360, 300, 330, 46, "S = Rₐ·R_b + R_b·R_c + R_c·Rₐ",
                size=14, bold=True, fill="#f4f6f8", stroke=INK)
    f.append(b2)
    b3 = fitbox(360, 356, 330, 44, "R_A = S / Rₐ   (Rₐ — плече до A)",
                size=14, bold=True, fill="#fdecea", stroke=POS)
    f.append(b3)
    f.append(text(525, 392, "чисельник S — той самий для всіх трьох сторін",
                  size=11, color=MUTED))

    render(P("formula-pattern.svg"), W, H, *f)


# ── 4. Три рівняння еквівалентності: зірка (сума двох) = трикутник (паралель) ─
def fig_three_equations():
    W, H = 720, 340
    f = [text(W/2, 26, "Три пари клем → три рівняння еквівалентності", size=17, bold=True)]

    rows = [
        ("Пара A–B", "Rₐ + R_b", "R_C ∥ (R_A + R_B)", NEG),
        ("Пара B–C", "R_b + R_c", "R_A ∥ (R_B + R_C)", POS),
        ("Пара C–A", "R_c + Rₐ", "R_B ∥ (R_C + R_A)", FIELD),
    ]
    y0 = 78
    dy = 74
    # заголовки колонок
    f.append(text(150, 60, "поміж клемами", size=12, bold=True, color=MUTED))
    f.append(text(360, 60, "зірка: два промені", size=12, bold=True, color=INK))
    f.append(text(585, 60, "трикутник: сторона ∥ обхід", size=12, bold=True, color=INK))

    for i, (pair, ystar, ytri, col) in enumerate(rows):
        yc = y0 + i * dy
        f.append(fitbox(60, yc, 180, 46, pair, size=14, bold=True,
                        fill="#f4f6f8", stroke=col))
        f.append(fitbox(268, yc, 185, 46, ystar, size=15, bold=True,
                        fill="#eaf0fd", stroke=NEG))
        f.append(text(468, yc + 28, "=", size=20, bold=True, color=INK))
        f.append(fitbox(486, yc, 200, 46, ytri, size=14, bold=True,
                        fill="#fdecea", stroke=POS))

    f.append(text(W/2, H - 14,
                  "Ліворуч — послідовні промені; праворуч — пряма сторона в паралелі з обхідними двома. "
                  "∥ = «паралельно».",
                  size=11, color=MUTED))
    render(P("three-equations.svg"), W, H, *f)


# ── 5. Ланцюжок Δ→Y: скласти три, поділити на два, відняти рівняння без променя ─
def fig_delta_to_y_steps():
    W, H = 720, 400
    f = [text(W/2, 26, "Δ→Y: як три рівняння дають один промінь", size=17, bold=True)]

    steps = [
        ("1. Скласти всі три рівняння",
         "2·(Rₐ + R_b + R_c) = 2P / Σ",
         "кожен промінь увійшов двічі → зліва подвоєна сума",
         NEG),
        ("2. Поділити на два",
         "Rₐ + R_b + R_c = P / Σ",
         "P = R_A·R_B + R_B·R_C + R_C·R_A   (попарні добутки)",
         INK),
        ("3. Відняти рівняння без Rₐ",
         "Rₐ = P/Σ − R_A·(R_B + R_C)/Σ",
         "доданки з R_A гасяться → лишається R_B·R_C",
         FIELD),
        ("Результат",
         "Rₐ = (R_B · R_C) / (R_A + R_B + R_C)",
         "суміжні до A сторони над сумою всіх трьох",
         POS),
    ]
    y0 = 66
    dy = 84
    for i, (title_s, formula, note, col) in enumerate(steps):
        yc = y0 + i * dy
        f.append(text(58, yc + 6, title_s, size=13, bold=True, color=col, anchor="start"))
        f.append(fitbox(58, yc + 16, 604, 40, formula, size=15, bold=True,
                        fill="#f7f9fc" if i < 3 else "#fdecea",
                        stroke=col))
        f.append(text(58, yc + 72, note, size=11, color=MUTED, anchor="start"))

    render(P("delta-to-y-steps.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_shapes()
    fig_bridge_unlock()
    fig_formula_pattern()
    fig_three_equations()
    fig_delta_to_y_steps()
    print("OK: figures written to", OUT)
