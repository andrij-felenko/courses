# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

PHI = (1 + 5 ** 0.5) / 2
PSI = (1 - 5 ** 0.5) / 2

# ── Фігура 1: Порівняння росту послідовностей Фібоначчі та Люка ────────────────
def fig_ladder():
    W, H = 820, 440
    ox, x_right = 100, 760
    y_top, y_bot = 80, 370
    
    indices = list(range(9))
    F = [0, 1, 1, 2, 3, 5, 8, 13, 21]
    L = [2, 1, 3, 4, 7, 11, 18, 29, 47]

    def X(i):
        return ox + i / 8.0 * (x_right - ox)

    def Y(val):
        return y_bot - (math.log2(val + 1) / math.log2(50)) * (y_bot - y_top)

    parts = []
    parts.append(arrow(ox, y_bot, x_right + 25, y_bot, color=INK, sw=1.8))
    parts.append(arrow(ox, y_bot, ox, y_top - 20, color=INK, sw=1.8))
    parts.append(text(x_right + 28, y_bot + 4, 'n', 14, INK, 'start', bold=True))
    parts.append(text(ox - 70, y_top - 24, 'Значення', 12, INK, 'start', bold=True))

    for i in indices:
        parts.append(line(X(i), y_bot, X(i), y_bot + 5, color=INK, sw=1.2))
        parts.append(text(X(i), y_bot + 22, str(i), 12, MUTED, 'middle'))

    pts_F = ' '.join(f'{X(i):.1f},{Y(F[i]):.1f}' for i in indices)
    parts.append(f'<polyline points="{pts_F}" fill="none" stroke="{NEG}" stroke-width="2.4"/>')

    pts_L = ' '.join(f'{X(i):.1f},{Y(L[i]):.1f}' for i in indices)
    parts.append(f'<polyline points="{pts_L}" fill="none" stroke="{POS}" stroke-width="2.4"/>')

    for i in indices:
        parts.append(circle(X(i), Y(F[i]), 4.5, fill=NEG, stroke="#ffffff", sw=1.5))
        parts.append(text(X(i), Y(F[i]) + 18, f'F={F[i]}', 10.5, NEG, 'middle', bold=True))

        parts.append(circle(X(i), Y(L[i]), 4.5, fill=POS, stroke="#ffffff", sw=1.5))
        parts.append(text(X(i), Y(L[i]) - 12, f'L={L[i]}', 10.5, POS, 'middle', bold=True))

    parts.append(rect(500, 35, 260, 45, fill="#ffffff", stroke="#d0d5dd", rx=6))
    parts.append(line(515, 50, 545, 50, color=POS, sw=2.5))
    parts.append(circle(530, 50, 4, fill=POS))
    parts.append(text(555, 54, 'Числа Люка Lₙ (старт: 2, 1)', 11.5, INK, 'start'))

    parts.append(line(515, 68, 545, 68, color=NEG, sw=2.5))
    parts.append(circle(530, 68, 4, fill=NEG))
    parts.append(text(555, 72, 'Числа Фібоначчі Fₙ (старт: 0, 1)', 11.5, INK, 'start'))

    render(os.path.join(IMG, 'lucas-fibonacci-ladder.svg'), W, H, *parts,
           title='Порівняння послідовностей Фібоначчі та Люка')


# ── Фігура 2: Збіжність φⁿ та ψⁿ ──────────────────────────────────────────────
def fig_conjugates():
    W, H = 800, 420
    ox, x_right = 90, 740
    cy = 240

    parts = []
    parts.append(arrow(ox, cy, x_right + 20, cy, color=INK, sw=1.8))
    parts.append(text(x_right + 25, cy + 4, 'n', 14, INK, 'start', bold=True))
    parts.append(text(ox - 60, 60, 'Складові Lₙ', 12, INK, 'start', bold=True))

    indices = list(range(8))
    def X(i):
        return ox + i / 7.0 * (x_right - ox)

    def Y_phi(i):
        val = PHI ** i
        return cy - (val / 30.0) * 160.0

    def Y_psi(i):
        val = PSI ** i
        return cy - val * 60.0

    parts.append(line(ox, cy, x_right, cy, color=MUTED, dash="4 4"))

    pts_psi = ' '.join(f'{X(i):.1f},{Y_psi(i):.1f}' for i in indices)
    parts.append(f'<polyline points="{pts_psi}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="5 4"/>')

    pts_phi = ' '.join(f'{X(i):.1f},{Y_phi(i):.1f}' for i in indices)
    parts.append(f'<polyline points="{pts_phi}" fill="none" stroke="{POS}" stroke-width="2.2"/>')

    for i in indices:
        parts.append(line(X(i), cy - 6, X(i), cy + 6, color=INK))
        parts.append(text(X(i), cy + 22, f'n={i}', 11, MUTED, 'middle'))

        y_p = Y_psi(i)
        parts.append(circle(X(i), y_p, 4, fill=NEG))
        
        y_ph = Y_phi(i)
        parts.append(circle(X(i), y_ph, 4, fill=POS))

    box1, _, _ = textbox(220, 95, "Головний доданок φⁿ\n(зростає експоненційно)", size=11, fill="#f0f9ff", stroke=POS)
    box2, _, _ = textbox(580, 305, "Спряжений доданок ψⁿ = (−1/φ)ⁿ\n(коливається і прямує до 0)", size=11, fill="#fff5f5", stroke=NEG)
    parts.extend([box1, box2])

    render(os.path.join(IMG, 'golden-conjugates.svg'), W, H, *parts,
           title='Збіжність степенів золотого перерізу до чисел Люка')


# ── Фігура 3: Гіпербола Люка-Пелля ────────────────────────────────────────────
def fig_hyperbola():
    W, H = 760, 460
    cx, cy = 380, 230
    scale_x, scale_y = 10.5, 36.0

    parts = []
    parts.append(arrow(60, cy, W - 40, cy, color=INK, sw=1.8))
    parts.append(arrow(cx, H - 40, cx, 40, color=INK, sw=1.8))
    parts.append(text(W - 30, cy + 18, 'x = Lₙ', 13, INK, 'middle', bold=True))
    parts.append(text(cx + 25, 30, 'y = Fₙ', 13, INK, 'middle', bold=True))

    points = [
        (2, 0, 'n=0 (2,0)'),
        (1, 1, 'n=1 (1,1)'),
        (3, 1, 'n=2 (3,1)'),
        (4, 2, 'n=3 (4,2)'),
        (7, 3, 'n=4 (7,3)'),
        (11, 5, 'n=5 (11,5)'),
        (18, 8, 'n=6 (18,8)'),
        (29, 13, 'n=7 (29,13)')
    ]

    for x_val, y_val, lbl in points:
        px = cx + x_val * scale_x
        py = cy - y_val * scale_y
        if px < W - 50 and py > 50:
            col = POS if (x_val**2 - 5*y_val**2 == 4) else NEG
            parts.append(circle(px, py, 5, fill=col, stroke="#ffffff", sw=1.5))
            parts.append(text(px + 8, py - 8, lbl, 10.5, col, 'start', bold=True))

    box1, _, _ = textbox(185, 100, "Гіпербола x² − 5y² = 4\n(парні індекси n)", size=11, fill="#f0f9ff", stroke=POS)
    box2, _, _ = textbox(185, 180, "Гіпербола x² − 5y² = −4\n(непарні індекси n)", size=11, fill="#fff5f5", stroke=NEG)
    parts.extend([box1, box2])

    render(os.path.join(IMG, 'hyperbola-pell.svg'), W, H, *parts,
           title='Цілочисельні точки Люка-Фібоначчі на гіперболах Пелля')


# ── Фігура 4: Схема тесту Люка-Лемера ─────────────────────────────────────────
def fig_primality_tree():
    W, H = 780, 400
    parts = []

    box1, _, _ = textbox(150, 200, "Крок 0:\ns₀ = 4\n(базовий елемент V₂)", size=12, fill="#f8fafc", stroke=INK)
    box2, _, _ = textbox(400, 200, "Рекурентний крок:\nsₖ = sₖ₋₁² − 2 (mod Mₚ)\n(k = 1 ... p−2)", size=12, fill="#eff6ff", stroke=FIELD)
    box3, _, _ = textbox(650, 135, "Якщо sₚ₋₂ ≡ 0:\nMₚ — ПРОСТЕ!\n(Детерміновано)", size=12, fill="#f0fdf4", stroke=POS)
    box4, _, _ = textbox(650, 265, "Якщо sₚ₋₂ ≢ 0:\nMₚ — СКЛАДЕНЕ", size=12, fill="#fef2f2", stroke=NEG)

    parts.extend([box1, box2, box3, box4])

    parts.append(arrow(240, 200, 290, 200, color=INK, sw=2))
    parts.append(arrow(510, 180, 560, 140, color=POS, sw=2))
    parts.append(arrow(510, 220, 560, 260, color=NEG, sw=2))

    parts.append(text(W // 2, 45, 'Тест простоти Люка–Лемера для чисел Мерсенна Mₚ = 2ᵖ − 1', 14, INK, 'middle', bold=True))

    render(os.path.join(IMG, 'lucas-primality-tree.svg'), W, H, *parts,
           title='Схема роботи тесту простоти Люка-Лемера')


if __name__ == '__main__':
    fig_ladder()
    fig_conjugates()
    fig_hyperbola()
    fig_primality_tree()
    print("Всі фігури згенеровано успішно.")
