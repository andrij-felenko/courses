# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_mh_makeup_terminating():
    W, H = 760, 310
    p = []

    # Вхідний блок: Довжина серії L = 142 пікселі
    p.append(rect(40, 55, 680, 52, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(60, 85, "Серія L = 142 пікселі", size=12, bold=True, color=INK, anchor="start"))
    p.append(text(250, 85, "=  128 (Make-up)  +  14 (Terminating)", size=12, bold=False, color=NEG, anchor="start"))
    p.append(text(690, 85, "L = 64·M + T", size=12, bold=True, color=MUTED, anchor="end"))

    # Стрілки розгалуження
    p.append(arrow(260, 110, 190, 145, color=LINE, sw=1.5))
    p.append(arrow(500, 110, 570, 145, color=LINE, sw=1.5))

    # Ліва колонка: Make-up код
    box_l = fitbox(40, 150, 330, 120,
                   "Складений код нарощення (Make-up)\n"
                   "Кратно 64: {64, 128, 192, ..., 1728}\n"
                   "Для L=128 (біла серія):\n"
                   "Код префікса: 10010 (5 бітів)",
                   size=11, pad=10, fill="#eaf0fd", stroke=NEG, sw=1.5)
    p.append(box_l)

    # Права колонка: Terminating код
    box_r = fitbox(390, 150, 330, 120,
                   "Термінальний код (Terminating)\n"
                   "Залишок 0 <= T <= 63 пікселі\n"
                   "Для T=14 (біла серія):\n"
                   "Код префікса: 011001 (6 бітів)",
                   size=11, pad=10, fill="#eafaf0", stroke=FIELD, sw=1.5)
    p.append(box_r)

    # Підсумок внизу
    p.append(text(W / 2, 295, "Сумарний код довжини L=142:  10010 + 011001  (разом 11 бітів замість 142)", size=11, bold=True, color=INK))

    render(os.path.join(OUT, "mh-makeup-terminating.svg"), W, H, *p,
           title="Розбиття серії L у Modified Huffman (MH)")


def fig_mr_five_points():
    W, H = 760, 330
    p = []

    # Стрічка опорного рядка (Reference line)
    yr = 85
    cell = 24
    x0 = 50

    p.append(text(x0, yr - 35, "Опорний рядок (Reference line, рядок y-1):", size=11, bold=True, color=MUTED, anchor="start"))
    ref_pattern = "WWWWWWWWWWBBBBBBBBBBBBWWWWWW"
    for i, ch in enumerate(ref_pattern):
        col = "#ffffff" if ch == "W" else "#1e293b"
        p.append(rect(x0 + i * cell, yr, cell, cell, fill=col, stroke="#94a3b8", sw=1, rx=0))

    # Стрічка кодованого рядка (Coding line)
    yc = 195
    p.append(text(x0, yc - 15, "Кодований рядок (Coding line, рядок y):", size=11, bold=True, color=MUTED, anchor="start"))
    cod_pattern = "WWWWWWWWWWWBBBBBBBBBBBBWWWWW"
    for i, ch in enumerate(cod_pattern):
        col = "#ffffff" if ch == "W" else "#1e293b"
        p.append(rect(x0 + i * cell, yc, cell, cell, fill=col, stroke="#94a3b8", sw=1, rx=0))

    # a0 (поточна опорна точка)
    xa0 = x0 + 3 * cell + cell / 2
    p.append(circle(xa0, yc + cell / 2, 7, fill=POS, stroke=INK, sw=1.5))
    p.append(mtext(xa0, yc + cell + 18, ["a0", "(опорна)"], size=10, color=POS, bold=True))

    # a1 (наступна зміна на поточному рядку)
    xa1 = x0 + 11 * cell + cell / 2
    p.append(circle(xa1, yc + cell / 2, 7, fill="#f59e0b", stroke=INK, sw=1.5))
    p.append(mtext(xa1, yc + cell + 18, ["a1", "(W->B)"], size=10, color=INK, bold=True))

    # a2 (друга зміна на поточному рядку)
    xa2 = x0 + 23 * cell + cell / 2
    p.append(circle(xa2, yc + cell / 2, 7, fill="#f59e0b", stroke=INK, sw=1.5))
    p.append(mtext(xa2, yc + cell + 18, ["a2", "(B->W)"], size=10, color=INK, bold=True))

    # b1 (перша зміна на опорному рядку праворуч від a0 протилежного до a0 кольору)
    xb1 = x0 + 10 * cell + cell / 2
    p.append(circle(xb1, yr + cell / 2, 7, fill=NEG, stroke=INK, sw=1.5))
    p.append(mtext(xb1, yr - 22, ["b1", "(W->B)"], size=10, color=NEG, bold=True))

    # b2 (наступна зміна на опорному рядку)
    xb2 = x0 + 22 * cell + cell / 2
    p.append(circle(xb2, yr + cell / 2, 7, fill=NEG, stroke=INK, sw=1.5))
    p.append(mtext(xb2, yr - 22, ["b2", "(B->W)"], size=10, color=NEG, bold=True))

    # Вертикальна лінія кореляції між b1 та a1 (зсув +1 піксель)
    p.append(line(xb1, yr + cell + 4, xa1, yc - 4, color=FIELD, sw=2, dash="3 3"))
    p.append(text(xa1 + 75, (yr + yc) / 2 + 12, "Зсув +1 px: VR(1)", size=11, bold=True, color=FIELD))

    render(os.path.join(OUT, "mr-five-points.svg"), W, H, *p,
           title="Modified READ: геометрія точок a0, a1, a2, b1, b2")


def fig_mr_three_modes():
    W, H = 760, 320
    p = []

    # Блок 1: Pass Mode
    p.append(rect(30, 50, 220, 245, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(140, 75, "Режим пропуску (Pass)", size=11, bold=True, color=POS))
    p.append(line(45, 88, 235, 88, color="#fca5a5", sw=1))
    p.append(text(140, 115, "Умова: b2 < a1", size=11, bold=True, color=INK))
    p.append(mtext(140, 145, "Перехід на опорному\nрядку зник раніше, ніж\nпочався перехід у кодованому", size=10, color=MUTED, lh=1.3))
    p.append(text(140, 210, "Код: 0001 (4 біти)", size=11, bold=True, color=POS))
    p.append(text(140, 255, "Зсув: a0 := b2", size=11, bold=True, color=INK))

    # Блок 2: Vertical Mode
    p.append(rect(270, 50, 220, 245, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(380, 75, "Вертикальний (Vertical)", size=11, bold=True, color=FIELD))
    p.append(line(285, 88, 475, 88, color="#86efac", sw=1))
    p.append(text(380, 115, "Умова: |a1 - b1| <= 3", size=11, bold=True, color=INK))
    p.append(mtext(380, 145, "Точка a1 лежить поруч\nіз точкою b1 (зсув -3..+3)\nНайчастіший випадок у тексті", size=10, color=MUTED, lh=1.3))
    p.append(text(380, 210, "V(0)='1', VR(1)='011'...", size=10, bold=True, color=FIELD))
    p.append(text(380, 255, "Зсув: a0 := a1", size=11, bold=True, color=INK))

    # Блок 3: Horizontal Mode
    p.append(rect(510, 50, 220, 245, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(620, 75, "Горизонтальний (Horiz)", size=11, bold=True, color=NEG))
    p.append(line(525, 88, 715, 88, color="#93c5fd", sw=1))
    p.append(text(620, 115, "Умова: |a1 - b1| > 3", size=11, bold=True, color=INK))
    p.append(mtext(620, 145, "Новий елемент рядка,\nвертикальна кореляція\nвідсутня або завелика", size=10, color=MUTED, lh=1.3))
    p.append(text(620, 210, "Код: 001 + MH(a0a1) + MH(a1a2)", size=9, bold=True, color=NEG))
    p.append(text(620, 255, "Зсув: a0 := a2", size=11, bold=True, color=INK))

    render(os.path.join(OUT, "mr-three-modes.svg"), W, H, *p,
           title="Три режими Modified READ: Pass, Vertical, Horizontal")


def fig_g3_vs_g4_framing():
    W, H = 760, 310
    p = []

    # Group 3 1D
    y1 = 60
    p.append(text(40, y1 + 18, "CCITT T.4 (Group 3 1D):", size=11, bold=True, color=INK, anchor="start"))
    p.append(rect(230, y1, 100, 34, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(280, y1 + 22, "EOL (12 бітів)", size=10, bold=True, color=POS))
    p.append(rect(335, y1, 170, 34, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=4))
    p.append(text(420, y1 + 22, "1D Рядок (MH серії)", size=10, color=INK))
    p.append(rect(510, y1, 100, 34, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(560, y1 + 22, "EOL", size=10, bold=True, color=POS))
    p.append(rect(615, y1, 105, 34, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(667, y1 + 22, "RTC (6× EOL)", size=10, bold=True, color=POS))

    # Group 3 2D (K-фактор)
    y2 = 135
    p.append(text(40, y2 + 18, "CCITT T.4 (Group 3 2D, K=2):", size=11, bold=True, color=INK, anchor="start"))
    p.append(rect(230, y2, 80, 34, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(270, y2 + 22, "EOL + '1'", size=10, bold=True, color=POS))
    p.append(rect(315, y2, 130, 34, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=4))
    p.append(text(380, y2 + 22, "1D Рядок (Опорний)", size=10, color=INK))
    p.append(rect(450, y2, 80, 34, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(490, y2 + 22, "EOL + '0'", size=10, bold=True, color=NEG))
    p.append(rect(535, y2, 185, 34, fill="#e0f2fe", stroke=NEG, sw=1.2, rx=4))
    p.append(text(627, y2 + 22, "2D Рядок (Modified READ)", size=10, bold=True, color=NEG))

    # Group 4 (MMR)
    y3 = 210
    p.append(text(40, y3 + 18, "CCITT T.6 (Group 4 MMR):", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(rect(230, y3, 150, 34, fill="#dcfce7", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(305, y3 + 22, "2D Рядок 1 (від білого)", size=10, bold=True, color=FIELD))
    p.append(rect(385, y3, 130, 34, fill="#dcfce7", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(450, y3 + 22, "2D Рядок 2", size=10, bold=True, color=FIELD))
    p.append(rect(520, y3, 100, 34, fill="#dcfce7", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(570, y3 + 22, "2D Рядок N...", size=10, bold=True, color=FIELD))
    p.append(rect(625, y3, 95, 34, fill="#fef08a", stroke="#ca8a04", sw=1.4, rx=4))
    p.append(text(672, y3 + 22, "EOFB (2×Pass)", size=10, bold=True, color="#854d0e"))

    p.append(text(W / 2, 285, "MMR усуває EOL і 1D-бар'єри для надійних цифрових мереж та форматів (TIFF, PDF)", size=11, bold=False, color=MUTED))

    render(os.path.join(OUT, "g3-vs-g4-framing.svg"), W, H, *p,
           title="Структура потоку: Group 3 1D/2D та Group 4 (MMR)")


if __name__ == "__main__":
    fig_mh_makeup_terminating()
    fig_mr_five_points()
    fig_mr_three_modes()
    fig_g3_vs_g4_framing()
    print("All figures generated successfully.")
