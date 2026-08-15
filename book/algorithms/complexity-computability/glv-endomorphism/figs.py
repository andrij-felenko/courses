# -*- coding: utf-8 -*-
"""
Генератор фігур для теми: Ендоморфізм GLV/GLS (book/algorithms/complexity-computability/glv-endomorphism)
"""

import sys
import os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_fig1():
    """Фігура 1: Геометрія ґратки GLV та пошук найближчого вектора (Babai Rounding)"""
    w, h = 800, 420
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % POS,
        '  </marker>',
        '  <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % NEG,
        '  </marker>',
        '  <marker id="arrow-dark" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % INK,
        '  </marker>',
        '</defs>',
        rect(0, 0, w, h, fill=BG, stroke="none")
    ]

    out.append(text(w / 2, 25, "Геометрія ґратки GLV: редукція вектора (k, 0) до малого вектора (k₁, k₂)", size=15, bold=True))

    # Оси координат з центром у O(180, 260)
    cx, cy = 180, 260
    out.append(line(40, cy, 760, cy, color=MUTED, sw=1.5))
    out.append(line(cx, 40, cx, 380, color=MUTED, sw=1.5))
    out.append(text(750, cy + 20, "x₁", size=12, bold=True, color=MUTED))
    out.append(text(cx - 20, 50, "x₂", size=12, bold=True, color=MUTED))
    out.append(text(cx - 15, cy + 18, "O", size=12, bold=True, color=MUTED))

    # Сетка ґратки (lattice points)
    # Базис v1 = (140, -40), v2 = (60, -110)
    v1x, v1y = 140, -40
    v2x, v2y = 60, -110

    # Малюємо паралелограм фундаментальної області в центрі
    p1 = (cx, cy)
    p2 = (cx + v1x, cy + v1y)
    p3 = (cx + v1x + v2x, cy + v1y + v2y)
    p4 = (cx + v2x, cy + v2y)
    out.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#e8f4fc" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4" />' % (
        p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1], POS))

    # Вузли ґратки (Lattice points L)
    for i in range(-1, 4):
        for j in range(-1, 3):
            lx = cx + i * v1x + j * v2x
            ly = cy + i * v1y + j * v2y
            if 30 <= lx <= 770 and 30 <= ly <= 390:
                out.append(circle(lx, ly, 4, fill=LINE, stroke="none"))

    # Базисні вектори v1 і v2
    out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.5" marker-end="url(#arrow-blue)" />' % (
        cx, cy, cx + v1x, cy + v1y, POS))
    out.append(text(cx + v1x / 2 + 10, cy + v1y / 2 + 20, "v¹ = (b₁₁, b₁₂)", size=12, bold=True, color=POS))

    out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.5" marker-end="url(#arrow-blue)" />' % (
        cx, cy, cx + v2x, cy + v2y, POS))
    out.append(text(cx + v2x - 70, cy + v2y / 2, "v² = (b₂₁, b₂₂)", size=12, bold=True, color=POS))

    # Цільовий вектор u = (k, 0)
    tx, ty = cx + 320, cy
    out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.5" marker-end="url(#arrow-dark)" />' % (
        cx, cy, tx, ty, INK))
    out.append(circle(tx, ty, 5, fill=INK, stroke="none"))
    out.append(text(tx - 30, ty + 25, "u = (k, 0)", size=13, bold=True, color=INK))

    # Знайдений вектор ґратки v = z1*v1 + z2*v2 = (340, -190)
    vx = cx + 2 * v1x + 1 * v2x
    vy = cy + 2 * v1y + 1 * v2y
    out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrow-blue)" />' % (
        cx, cy, vx, vy, POS))
    out.append(circle(vx, vy, 6, fill=POS, stroke="none"))
    out.append(text(vx + 12, vy - 10, "v = z₁v¹ + z₂v² ∈ L", size=12, bold=True, color=POS))

    # Вектор залишку (k1, k2) = u - v
    out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.5" marker-end="url(#arrow-red)" />' % (
        vx, vy, tx, ty, NEG))
    out.append(text(vx + (tx - vx) / 2 + 15, vy + (ty - vy) / 2 + 5, "(k₁, k₂) = u - v", size=13, bold=True, color=NEG))

    # Пояснювальний блок праворуч зверху
    tb, wtb, htb = textbox(620, 110, "Оцінка норми залишку:\n||(k₁, k₂)|| ≤ C · √r\n||k₁||, ||k₂|| ≈ 2¹²⁸\n(для 256-бітного r)", size=12, pad=10, fill="#fef3c7", stroke="#d97706")
    out.append(tb)

    out.append('</svg>')
    return "".join(out)


def build_fig2():
    """Фігура 2: Порівняння обчислювальних конвеєрів: стандартний vs 2D GLV vs 4D GLS"""
    w, h = 800, 380
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % LINE,
        '  </marker>',
        '</defs>',
        rect(0, 0, w, h, fill=BG, stroke="none")
    ]

    out.append(text(w / 2, 25, "Конвеєр скалярного множення: Класичний (256b) vs GLV 2D vs GLS 4D", size=15, bold=True))

    # Рядок 1: Класичний Double-and-Add (256 біт)
    y1 = 80
    out.append(rect(40, y1, 140, 60, fill="#f3f4f6", stroke=MUTED, rx=6))
    out.append(text(110, y1 + 35, "Скаляр k (256b)", size=12, bold=True))
    out.append(arrow(180, y1 + 30, 230, y1 + 30, color=LINE, sw=2))

    out.append(rect(230, y1, 310, 60, fill="#fee2e2", stroke=NEG, rx=6))
    out.append(text(385, y1 + 25, "Цикл скалярного множення NAF", size=12, bold=True, color=NEG))
    out.append(text(385, y1 + 45, "256 подвоєнь + ~85 додавань точок", size=11, color=INK))
    out.append(arrow(540, y1 + 30, 590, y1 + 30, color=LINE, sw=2))

    out.append(rect(590, y1, 170, 60, fill="#e8f4fc", stroke=POS, rx=6))
    out.append(text(675, y1 + 35, "Результат [k]P\n100% часу (база)", size=12, bold=True, color=POS))

    # Рядок 2: GLV 2D (secp256k1)
    y2 = 175
    out.append(rect(40, y2, 140, 60, fill="#f3f4f6", stroke=MUTED, rx=6))
    out.append(text(110, y2 + 35, "Скаляр k (256b)", size=12, bold=True))
    out.append(arrow(180, y2 + 30, 230, y2 + 30, color=LINE, sw=2))

    out.append(rect(230, y2, 150, 60, fill="#fef3c7", stroke="#d97706", rx=6))
    out.append(text(305, y2 + 25, "Розклад GLV", size=12, bold=True, color="#b45309"))
    out.append(text(305, y2 + 45, "k = k₁ + k₂λ (128b)", size=11, color=INK))
    out.append(arrow(380, y2 + 30, 420, y2 + 30, color=LINE, sw=2))

    out.append(rect(420, y2, 200, 60, fill="#e6f4ea", stroke=FIELD, rx=6))
    out.append(text(520, y2 + 25, "2D Straus/Shamir NAF", size=12, bold=True, color=FIELD))
    out.append(text(520, y2 + 45, "128 подвоєнь + 1 ендоморфізм", size=11, color=INK))
    out.append(arrow(620, y2 + 30, 650, y2 + 30, color=LINE, sw=2))

    out.append(rect(650, y2, 110, 60, fill="#e8f4fc", stroke=POS, rx=6))
    out.append(text(705, y2 + 28, "[k]P", size=13, bold=True, color=POS))
    out.append(text(705, y2 + 46, "Прискорення ~35%", size=10, bold=True, color=FIELD))

    # Рядок 3: GLS + GLV 4D (над F_{p^2})
    y3 = 270
    out.append(rect(40, y3, 140, 60, fill="#f3f4f6", stroke=MUTED, rx=6))
    out.append(text(110, y3 + 35, "Скаляр k (256b)", size=12, bold=True))
    out.append(arrow(180, y3 + 30, 230, y3 + 30, color=LINE, sw=2))

    out.append(rect(230, y3, 150, 60, fill="#fef3c7", stroke="#d97706", rx=6))
    out.append(text(305, y3 + 25, "4D Розклад GLS", size=12, bold=True, color="#b45309"))
    out.append(text(305, y3 + 45, "k = ∑ᵢ₌₁⁴ kᵢλᵢ (64b)", size=11, color=INK))
    out.append(arrow(380, y3 + 30, 420, y3 + 30, color=LINE, sw=2))

    out.append(rect(420, y3, 200, 60, fill="#e6f4ea", stroke=FIELD, rx=6))
    out.append(text(520, y3 + 25, "4D Interleaved NAF", size=12, bold=True, color=FIELD))
    out.append(text(520, y3 + 45, "64 подвоєння + 3 ендоморфізми", size=11, color=INK))
    out.append(arrow(620, y3 + 30, 650, y3 + 30, color=LINE, sw=2))

    out.append(rect(650, y3, 110, 60, fill="#e8f4fc", stroke=POS, rx=6))
    out.append(text(705, y3 + 28, "[k]P", size=13, bold=True, color=POS))
    out.append(text(705, y3 + 46, "Прискорення ~50%", size=10, bold=True, color=FIELD))

    out.append('</svg>')
    return "".join(out)


def build_fig3():
    """Фігура 3: Захист від атак по побічних каналах (Side-Channel Mitigation) у GLV-декомпозиції"""
    w, h = 800, 320
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % LINE,
        '  </marker>',
        '</defs>',
        rect(0, 0, w, h, fill=BG, stroke="none")
    ]

    out.append(text(w / 2, 25, "Захист від таймінг-атак у GLV: уразлива vs константна реалізація", size=15, bold=True))

    # Лева сторона: Уразлива декомпозиція (Variable-time)
    bx1 = 40
    out.append(rect(bx1, 60, 340, 230, fill="#fff5f5", stroke=NEG, rx=8))
    out.append(text(bx1 + 170, 85, "Уразлива декомпозиція (Вразливість)", size=13, bold=True, color=NEG))

    tb_v, wv, hv = textbox(bx1 + 170, 150, "• Ділення з округленням в розгалуженні if/else\n• РІЗНА довжина бітів k₁, k₂ залежно від k\n• Витік секретного скаляра через таймінг\n• Атаки за енергоспоживанням (SPA/DPA)", size=12, pad=10, fill="#ffffff", stroke=NEG)
    out.append(tb_v)

    out.append(rect(bx1 + 20, 220, 300, 50, fill="#fee2e2", stroke=NEG, rx=4))
    out.append(text(bx1 + 170, 248, "Час виконання залежить від значення k!", size=11, bold=True, color=NEG))

    # Права сторона: Захищена константна декомпозиція (Constant-time)
    bx2 = 420
    out.append(rect(bx2, 60, 340, 230, fill="#f0fdf4", stroke=FIELD, rx=8))
    out.append(text(bx2 + 170, 85, "Захищена константна декомпозиція", size=13, bold=True, color=FIELD))

    tb_c, wc, hc = textbox(bx2 + 170, 150, "• Фіксована точність (Fixed-point arithmetic)\n• Безрозгалужені маски та побітові зсуви\n• Нормалізація скалярів k₁, k₂ до 128 біт\n• Рівномірний профіль виконання й пам'яті", size=12, pad=10, fill="#ffffff", stroke=FIELD)
    out.append(tb_c)

    out.append(rect(bx2 + 20, 220, 300, 50, fill="#e6f4ea", stroke=FIELD, rx=4))
    out.append(text(bx2 + 170, 248, "Час виконання строгий і сталий T = const!", size=11, bold=True, color=FIELD))

    out.append('</svg>')
    return "".join(out)


def main():
    target_dir = os.path.dirname(__file__)
    img_dir = os.path.join(target_dir, "img")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir, exist_ok=True)

    figs = [
        ("glv-decomposition-lattice.svg", build_fig1()),
        ("glv-pipeline-flow.svg", build_fig2()),
        ("side-channel-mitigation.svg", build_fig3())
    ]

    for fname, svg_content in figs:
        fpath = os.path.join(img_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Згенеровано: {fpath}")

if __name__ == "__main__":
    main()
