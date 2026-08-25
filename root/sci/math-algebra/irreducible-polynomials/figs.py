# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми «Непривідні многочлени»."""
import os
import sys

# Додаємо scripts до sys.path для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    text, mtext, rect, line, circle, arrow, textbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def fig_poly_factorization():
    """
    Ілюстрація факторизації многочленів: від складеного многочлена до непривідних
    будівельних блоків (аналог простих чисел) та фактор-кільця F[x]/(p(x)).
    Розмір: 800 x 420
    """
    w, h = 800, 420
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append(f'<rect width="100%" height="100%" fill="{BG}" />')

    # Заголовок
    svg.append(text(w / 2, 30, "Анатомія факторизації: від многочлена до нерозкладних атомів", size=16, bold=True))

    # Ліва колонка: Складений многочлен
    tb1, w1, h1 = textbox(160, 110, "Складений многочлен f(x)\nСтупінь deg(f) = n\nРозкладається на множники", size=13, pad=12, fill="#f8fafc", stroke=LINE)
    svg.append(tb1)

    # Стрілка розкладання
    svg.append(arrow(160, 155, 160, 210, color=LINE, sw=2))
    svg.append(text(175, 185, "Розклад на незвідні", size=11, color=MUTED, anchor="start"))

    # Середній рівень: Непривідні атоми
    tb_p1, wp1, hp1 = textbox(100, 270, "p₁(x)ᵉ¹\nНепривідний", size=12, pad=10, fill="#ecfdf5", stroke=FIELD, bold=True)
    tb_p2, wp2, hp2 = textbox(220, 270, "p₂(x)ᵉ²\nНепривідний", size=12, pad=10, fill="#ecfdf5", stroke=FIELD, bold=True)
    svg.append(tb_p1)
    svg.append(tb_p2)

    svg.append(arrow(140, 215, 100, 238, color=LINE, sw=1.5))
    svg.append(arrow(180, 215, 220, 238, color=LINE, sw=1.5))

    # Текст під атомами
    svg.append(text(160, 345, "Елементарні дільники (атоми кільця F[x])", size=12, color=INK, anchor="middle", italic=True))
    svg.append(text(160, 365, "Неможливо розкласти у добуток менших степенів над полем F", size=11, color=MUTED, anchor="middle"))

    # Розділювач колонок
    svg.append(line(340, 60, 340, 390, color="#e2e8f0", sw=1.5, dash="4,4"))

    # Права колонка: Побудова полів розширення
    tb2, w2, h2 = textbox(570, 100, "Фактор-кільце F[x] / (p(x))\nЗа модулем непривідного p(x)", size=13, pad=12, fill="#eff6ff", stroke=NEG)
    svg.append(tb2)

    # Дві гілки справа: якщо p(x) непривідний vs якщо p(x) складений
    svg.append(arrow(510, 145, 450, 205, color=FIELD, sw=2))
    svg.append(arrow(630, 145, 690, 205, color=POS, sw=2))

    tb_field, wf, hf = textbox(450, 260, "p(x) непривідний\n⬇\nІдеал (p(x)) максимальний\nФактор є ПОЛЕМ F[x]/(p(x))\nКожен елемент має обернений", size=12, pad=10, fill="#f0fdf4", stroke=FIELD)
    tb_ring, wr, hr = textbox(690, 260, "p(x) складений: a(x)·b(x)\n⬇\nІдеал НЕ максимальний\nЄ ДІЛЬНИКИ НУЛЯ\nНе є полем (лише кільце)", size=12, pad=10, fill="#fef2f2", stroke=POS)
    svg.append(tb_field)
    svg.append(tb_ring)

    svg.append(text(450, 360, "Основа скінченних полів Галуа GF(qⁿ)", size=12, color=FIELD, anchor="middle", bold=True))
    svg.append(text(690, 360, "Дільники нуля руйнують ділення", size=12, color=POS, anchor="middle"))

    svg.append("</svg>")
    return "\n".join(svg)

def fig_field_extension():
    """
    Ілюстрація побудови скінченного поля GF(2³) = F₂[x]/(x³ + x + 1).
    Показує представлення елементів: поліноміальне, векторне (3 біти) та степені кореня α.
    Розмір: 800 x 440
    """
    w, h = 800, 440
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append(f'<rect width="100%" height="100%" fill="{BG}" />')

    # Заголовок
    svg.append(text(w / 2, 28, "Побудова поля Галуа GF(2³) за модулем непривідного p(x) = x³ + x + 1", size=15, bold=True))

    # Верхній пояснювальний блок
    tb_intro, wi, hi = textbox(w / 2, 70, "Корінь многочлена α задовольняє рівність: α³ + α + 1 = 0 ⇒ α³ = α + 1 (над F₂)\nКожен елемент — многочлен ступеня ≤ 2 від α або 3-бітове двійкове слово (b₂, b₁, b₀)", size=12, pad=8, fill="#f8fafc", stroke="#cbd5e1")
    svg.append(tb_intro)

    # Таблиця елементів поля GF(8)
    headers = ["Степінь α", "Поліном (мод p)", "Векторний базис (b₂, b₁, b₀)", "Десятковий двійковий код"]
    col_x = [110, 290, 500, 690]
    y_start = 125
    row_h = 32

    # Заголовок таблиці
    svg.append(rect(40, y_start, 720, 30, fill="#e2e8f0", stroke=LINE, rx=4))
    for idx, h_text in enumerate(headers):
        svg.append(text(col_x[idx], y_start + 20, h_text, size=12, bold=True, anchor="middle"))

    rows = [
        ("0", "0", "(0, 0, 0)", "000₂ (0)"),
        ("α⁰ = 1", "1", "(0, 0, 1)", "001₂ (1)"),
        ("α¹", "α", "(0, 1, 0)", "010₂ (2)"),
        ("α²", "α²", "(1, 0, 0)", "100₂ (4)"),
        ("α³", "α + 1", "(0, 1, 1)", "011₂ (3)"),
        ("α⁴", "α² + α", "(1, 1, 0)", "110₂ (6)"),
        ("α⁵", "α² + α + 1", "(1, 1, 1)", "111₂ (7)"),
        ("α⁶", "α² + 1", "(1, 0, 1)", "101₂ (5)"),
    ]

    for r_idx, row in enumerate(rows):
        cur_y = y_start + 30 + r_idx * row_h
        bg_col = "#ffffff" if r_idx % 2 == 0 else "#f8fafc"
        if r_idx == 4: # виділити крок редукції
            bg_col = "#ecfdf5"
        svg.append(rect(40, cur_y, 720, row_h, fill=bg_col, stroke="#e2e8f0", rx=2))
        svg.append(text(col_x[0], cur_y + 21, row[0], size=12, color=INK, anchor="middle", bold=(r_idx>0)))
        svg.append(text(col_x[1], cur_y + 21, row[1], size=12, color=INK, anchor="middle"))
        svg.append(text(col_x[2], cur_y + 21, row[2], size=12, color=INK, anchor="middle"))
        svg.append(text(col_x[3], cur_y + 21, row[3], size=12, color=INK, anchor="middle"))

    # Нижній висновок
    svg.append(text(w / 2, 420, "Множення: α⁴ · α⁵ = α⁹ = α² (оскільки α⁷ = 1 у мультиплікативній групі порядку 7)", size=12, color=FIELD, anchor="middle", bold=True))

    svg.append("</svg>")
    return "\n".join(svg)

def fig_rabin_test():
    """
    Блок-схема алгоритму Рабіна для перевірки незвідності многочлена f(x) над полем F_q.
    Розмір: 860 x 430
    """
    w, h = 860, 430
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append(f'<rect width="100%" height="100%" fill="{BG}" />')

    # Заголовок
    svg.append(text(w / 2, 28, "Конвеєр перевірки незвідності Рабіна для f(x) степеня n над полем F_q", size=15, bold=True))

    # Крок 1: Вхід
    tb1, w1, h1 = textbox(135, 95, "Вхідні дані:\nf(x) ∈ F_q[x], deg(f) = n\nПрості дільники n: p₁, ..., p_k", size=12, pad=10, fill="#f8fafc", stroke=LINE)
    svg.append(tb1)

    # Крок 2: Перша умова (ділиться на x^(q^n) - x)
    tb2, w2, h2 = textbox(400, 95, "Крок 1: Перевірка періоду\nОбчислити x^(qⁿ) mod f(x)\nЧи дорівнює воно x?", size=12, pad=10, fill="#eff6ff", stroke=NEG)
    svg.append(tb2)

    svg.append(arrow(235, 95, 295, 95, color=LINE, sw=1.8))

    # Гілка НІ для кроку 1
    svg.append(arrow(400, 140, 400, 200, color=POS, sw=1.8))
    svg.append(text(410, 175, "НІ", size=11, color=POS, bold=True, anchor="start"))

    tb_comp1, _, _ = textbox(400, 245, "ЗВІДНИЙ (f має корені\nпоза F_(qⁿ) або ділиться\nна незвідні d ∤ n)", size=11, pad=8, fill="#fef2f2", stroke=POS)
    svg.append(tb_comp1)

    # Гілка ТАК для кроку 1
    svg.append(arrow(505, 95, 565, 95, color=FIELD, sw=1.8))
    svg.append(text(535, 85, "ТАК", size=11, color=FIELD, bold=True, anchor="middle"))

    # Крок 3: Друга умова (НСД для всіх n/p_i)
    tb3, w3, h3 = textbox(700, 95, "Крок 2: Відсутність дільників\nДля кожного p_i | n:\ng_i = НСД(f(x), x^(q^(n/p_i)) - x)\nЧи всі g_i = 1?", size=11, pad=10, fill="#eff6ff", stroke=NEG)
    svg.append(tb3)

    # Гілка НІ для кроку 2
    svg.append(arrow(700, 155, 700, 205, color=POS, sw=1.8))
    svg.append(text(710, 180, "НІ (g_i ≠ 1)", size=11, color=POS, bold=True, anchor="start"))

    tb_comp2, _, _ = textbox(700, 245, "ЗВІДНИЙ\nЗнайдено нетривіальний\nспільний дільник g_i(x)", size=11, pad=8, fill="#fef2f2", stroke=POS)
    svg.append(tb_comp2)

    # Гілка ТАК для кроку 2 -> Фінал
    svg.append(line(815, 95, 815, 350, color=FIELD, sw=1.8))
    svg.append(arrow(815, 350, 560, 350, color=FIELD, sw=1.8))
    svg.append(text(720, 340, "ТАК (усі g_i = 1)", size=11, color=FIELD, bold=True, anchor="middle"))

    tb_succ, _, _ = textbox(360, 350, "НЕПРИВІДНИЙ МНОГОЧЛЕН f(x)\nГарантовано не має дільників меншого ступеня над F_q", size=13, pad=12, fill="#ecfdf5", stroke=FIELD, bold=True)
    svg.append(tb_succ)

    svg.append("</svg>")
    return "\n".join(svg)

def fig_eisenstein_criterion():
    """
    Ілюстрація критерію Ейзенштейна для многочлена f(x) = a_n x^n + ... + a_1 x + a_0 nad Z.
    Розмір: 800 x 380
    """
    w, h = 800, 380
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append(f'<rect width="100%" height="100%" fill="{BG}" />')

    # Заголовок
    svg.append(text(w / 2, 28, "Критерій Шенемана — Ейзенштейна: умови незвідності над ℤ та ℚ", size=15, bold=True))

    # Формула многочлена
    svg.append(text(w / 2, 68, "f(x) = aₙ·xⁿ + aₙ₋₁·xⁿ⁻¹ + ... + a₁·x + a₀", size=14, color=INK, bold=True))

    # Три зони умов
    # Зона 1: a_n (старший коефіцієнт)
    tb_lead, _, _ = textbox(160, 155, "Старший коефіцієнт aₙ\n\np ∤ aₙ\n(p НЕ ділить aₙ)\n\nЗберігає ступінь n\nпри редукції за модулем p", size=12, pad=10, fill="#fef2f2", stroke=POS)
    svg.append(tb_lead)

    # Зона 2: проміжні коефіцієнти a_{n-1} ... a_1
    tb_mid, _, _ = textbox(400, 155, "Проміжні коефіцієнти\naₙ₋₁, aₙ₋₂, ..., a₁\n\np | aᵢ (для всіх 0 ≤ i < n)\n(p ділить усі проміжні)\n\nРедукція f(x) ≡ aₙ·xⁿ (mod p)", size=12, pad=10, fill="#eff6ff", stroke=NEG)
    svg.append(tb_mid)

    # Зона 3: вільний член a_0
    tb_const, _, _ = textbox(640, 155, "Вільний член a₀\n\np | a₀  ТА  p² ∤ a₀\n(p ділить a₀, але p² НЕ ділить)\n\nБлокує розклад\na₀ = b₀·c₀ за модулем p²", size=12, pad=10, fill="#fef9c3", stroke="#ca8a04")
    svg.append(tb_const)

    # Нижній синтез / Висновок
    svg.append(arrow(160, 245, 300, 295, color=FIELD, sw=2))
    svg.append(arrow(400, 245, 400, 295, color=FIELD, sw=2))
    svg.append(arrow(640, 245, 500, 295, color=FIELD, sw=2))

    tb_res, _, _ = textbox(w / 2, 325, "ВИСНОВОК: Многочлен f(x) є НЕПРИВІДНИМ над полем раціональних чисел ℚ (і кільцем ℤ)", size=13, pad=12, fill="#ecfdf5", stroke=FIELD, bold=True)
    svg.append(tb_res)

    svg.append("</svg>")
    return "\n".join(svg)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    ensure_dir(img_dir)

    figs = [
        ("poly-factorization-tree.svg", fig_poly_factorization()),
        ("field-extension-lattice.svg", fig_field_extension()),
        ("rabin-test-pipeline.svg", fig_rabin_test()),
        ("eisenstein-criterion-logic.svg", fig_eisenstein_criterion()),
    ]

    for fname, content in figs:
        fpath = os.path.join(img_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated: {fpath}")

if __name__ == "__main__":
    main()
