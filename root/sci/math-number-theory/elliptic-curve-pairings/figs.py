# -*- coding: utf-8 -*-
"""
Генератор фігур для теми: Спарювання еліптичних кривих (Bilinear Pairings)
"""

import sys
import os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_fig1():
    """Фігура 1: Тригрупова структура білінійного спарювання e: G1 x G2 -> Gt"""
    w, h = 760, 320
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % LINE,
        '  </marker>',
        '</defs>',
        rect(0, 0, w, h, fill=BG, stroke="none")
    ]

    # Заголовок панелі
    out.append(text(w / 2, 25, "Тригрупова структура білінійного спарювання e: G1 × G2 → Gt", size=16, bold=True))

    # Блок G1
    tb1, w1, h1 = textbox(150, 110, "Група G1 = E(F_p)[r]\nАдитивна група точок над F_p\n[a]P ∈ G1 (48 байтів)", size=13, pad=12, fill="#e8f4fc", stroke=NEG)
    out.append(tb1)

    # Блок G2
    tb2, w2, h2 = textbox(150, 230, "Група G2 = E'(F_{p^2})[r]\nАдитивна група над F_{p^2}\n[b]Q ∈ G2 (96 байтів)", size=13, pad=12, fill="#fef3c7", stroke="#d97706")
    out.append(tb2)

    # Блок Gt
    tb_t, wt, ht = textbox(610, 170, "Група Gt = μ_r ⊂ F_{p^{12}}*\nМультиплікативна група\ne(P, Q)^(a·b) ∈ Gt (576 байтів)", size=13, pad=14, fill="#e6f4ea", stroke=FIELD)
    out.append(tb_t)

    # Стрілки відображення спарювання e(P, Q)
    out.append(arrow(280, 110, 460, 150, color=LINE, sw=2))
    out.append(arrow(280, 230, 460, 190, color=LINE, sw=2))

    # Вузол відображення e
    out.append(circle(460, 170, 24, fill="#ffffff", stroke=POS, sw=2))
    out.append(text(460, 175, "e", size=18, bold=True, color=POS))

    # Вихідна стрілка в Gt
    out.append(arrow(484, 170, 510, 170, color=LINE, sw=2))

    # Підпис білінійності у центрі
    out.append(rect(340, 40, 240, 36, fill="#f3f4f6", stroke=MUTED, rx=4))
    out.append(text(460, 63, "e([a]P, [b]Q) = e(P, Q)^(a·b)", size=13, bold=True, color=INK))

    out.append('</svg>')
    return "".join(out)


def build_fig2():
    """Фігура 2: Крок подвоєння та додавання в алгоритмі Міллера"""
    w, h = 760, 340
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % LINE,
        '  </marker>',
        '</defs>',
        rect(0, 0, w, h, fill=BG, stroke="none")
    ]

    out.append(text(w / 2, 25, "Геометричний крок алгоритму Міллера (Double & Add)", size=16, bold=True))

    # Два блоки: Подвоєння та Додавання
    # Блок 1: Подвоєння T -> [2]T
    out.append(rect(30, 50, 335, 260, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    out.append(text(197, 75, "Крок подвоєння (T ↦ [2]T)", size=14, bold=True, color=NEG))

    tb_d1, _, _ = textbox(197, 135, "Обчислення дотичної прямої l_{T,T}\nλ = (3·x_T² + a) / (2·y_T)", size=12, pad=8, fill="#ffffff", stroke=MUTED)
    out.append(tb_d1)

    tb_d2, _, _ = textbox(197, 215, "Оцінка прямої в точці Q ∈ G2\nl_{T,T}(Q) / v_{2T}(Q)", size=12, pad=8, fill="#ffffff", stroke=MUTED)
    out.append(tb_d2)

    tb_d3, _, _ = textbox(197, 280, "Накопичення: f := f² · l_{T,T}(Q)", size=12, pad=6, fill="#e8f4fc", stroke=NEG)
    out.append(tb_d3)

    out.append(arrow(197, 160, 197, 185, color=LINE, sw=1.5))
    out.append(arrow(197, 240, 197, 260, color=LINE, sw=1.5))

    # Блок 2: Додавання T + P
    out.append(rect(395, 50, 335, 260, fill="#fafaf9", stroke=LINE, sw=1.5, rx=8))
    out.append(text(562, 75, "Крок додавання (якщо біт = 1)", size=14, bold=True, color=POS))

    tb_a1, _, _ = textbox(562, 135, "Обчислення січної прямої l_{T,P}\nλ = (y_P - y_T) / (x_P - x_T)", size=12, pad=8, fill="#ffffff", stroke=MUTED)
    out.append(tb_a1)

    tb_a2, _, _ = textbox(562, 215, "Оцінка прямої в точці Q ∈ G2\nl_{T,P}(Q) / v_{T+P}(Q)", size=12, pad=8, fill="#ffffff", stroke=MUTED)
    out.append(tb_a2)

    tb_a3, _, _ = textbox(562, 280, "Накопичення: f := f · l_{T,P}(Q)", size=12, pad=6, fill="#fef2f2", stroke=POS)
    out.append(tb_a3)

    out.append(arrow(562, 160, 562, 185, color=LINE, sw=1.5))
    out.append(arrow(562, 240, 562, 260, color=LINE, sw=1.5))

    out.append('</svg>')
    return "".join(out)


def build_fig3():
    """Фігура 3: Конвеєр обчислення спарювання Ате"""
    w, h = 760, 260
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % LINE,
        '  </marker>',
        '</defs>',
        rect(0, 0, w, h, fill=BG, stroke="none")
    ]

    out.append(text(w / 2, 25, "Конвеєр спарювання Ате: Цикл Міллера + Фінальне піднесення", size=16, bold=True))

    # Вхідні точки
    tb_in, _, _ = textbox(90, 130, "Вхідні точки\nP ∈ G1\nQ ∈ G2", size=13, pad=10, fill="#f3f4f6", stroke=LINE)
    out.append(tb_in)

    out.append(arrow(150, 130, 190, 130, color=LINE, sw=2))

    # Цикл Міллера
    tb_m, _, _ = textbox(300, 130, "Фаза 1: Цикл Міллера\nОбчислення f_{T,Q}(P)\nітерацій s (64-bit NAF)\nf ∈ F_{p^{12}}*", size=13, pad=12, fill="#e8f4fc", stroke=NEG)
    out.append(tb_m)

    out.append(arrow(410, 130, 450, 130, color=LINE, sw=2))

    # Фінальне піднесення
    tb_f, _, _ = textbox(570, 130, "Фаза 2: Фінальне піднесення\nf_final = f^( (p^{12}-1)/r )\nПроста + Важка частина\nf_final ∈ Gt", size=13, pad=12, fill="#e6f4ea", stroke=FIELD)
    out.append(tb_f)

    out.append(arrow(690, 130, 725, 130, color=LINE, sw=2))

    # Пояснювальний підпис унизу
    out.append(text(w / 2, 230, "Фінальне піднесення усуває класи еквівалентності та зводить результат до канонічного кореня з 1", size=12, italic=True, color=MUTED))

    out.append('</svg>')
    return "".join(out)


def build_fig4():
    """Фігура 4: Агрегація підписів BLS та верифікація"""
    w, h = 760, 320
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % LINE,
        '  </marker>',
        '</defs>',
        rect(0, 0, w, h, fill=BG, stroke="none")
    ]

    out.append(text(w / 2, 25, "Схема агрегації підписів BLS та верифікація спарюванням", size=16, bold=True))

    # Валідатори 1..N
    tb_v1, _, _ = textbox(110, 80, "Валідатор 1\nσ_1 = [sk_1]H(m) ∈ G1", size=11, pad=6, fill="#f8fafc", stroke=MUTED)
    tb_v2, _, _ = textbox(110, 160, "Валідатор 2\nσ_2 = [sk_2]H(m) ∈ G1", size=11, pad=6, fill="#f8fafc", stroke=MUTED)
    tb_vn, _, _ = textbox(110, 240, "Валідатор N\nσ_N = [sk_N]H(m) ∈ G1", size=11, pad=6, fill="#f8fafc", stroke=MUTED)
    out.append(tb_v1)
    out.append(tb_v2)
    out.append(tb_vn)

    # Агрегатор
    out.append(arrow(210, 80, 260, 140, color=LINE, sw=1.5))
    out.append(arrow(210, 160, 260, 160, color=LINE, sw=1.5))
    out.append(arrow(210, 240, 260, 180, color=LINE, sw=1.5))

    tb_agg, _, _ = textbox(340, 160, "Неінтерактивний\nАгрегатор\nσ_agg = ∑ σ_i ∈ G1", size=12, pad=10, fill="#e8f4fc", stroke=NEG)
    out.append(tb_agg)

    out.append(arrow(420, 160, 460, 160, color=LINE, sw=2))

    # Верифікатор
    tb_ver, _, _ = textbox(590, 160, "Верифікатор спарювання\ne(σ_agg, P2) == e(H(m), PK_agg)\n2 операції спарювання!", size=12, pad=12, fill="#e6f4ea", stroke=FIELD)
    out.append(tb_ver)

    out.append(text(590, 260, "PK_agg = ∑ PK_i ∈ G2 обчислюється заздалегідь", size=12, bold=True, color=INK))

    out.append('</svg>')
    return "".join(out)


def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    figures = {
        "fig1-pairing-groups.svg": build_fig1(),
        "fig2-miller-step.svg": build_fig2(),
        "fig3-pairing-pipeline.svg": build_fig3(),
        "fig4-bls-aggregation.svg": build_fig4()
    }

    for filename, content in figures.items():
        filepath = os.path.join(img_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Згенеровано: {filepath}")

if __name__ == "__main__":
    main()
