# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── power-sums-triangle: трикутник сум степенів та коефіцієнти Бернуллі
def fig_power_sums_triangle():
    W, H = 820, 520
    p = []

    p.append(text(W / 2, 45, "Структура сум степенів S_m(n) = 1ᵐ + 2ᵐ + … + (n−1)ᵐ", size=15, bold=True))
    p.append(text(W / 2, 72, "Коефіцієнти поліномів виражаються через числа Бернуллі Bₖ", size=13, color=MUTED))

    # Таблиця формул сум для m = 1, 2, 3, 4
    rows = [
        ("m = 1", "S₁(n) = ½·n² − ½·n", "B₀ = 1, B₁ = −½"),
        ("m = 2", "S₂(n) = ⅓·n³ − ½·n² + ⅙·n", "B₂ = ⅙"),
        ("m = 3", "S₃(n) = ¼·n⁴ − ½·n³ + ¼·n²", "B₃ = 0"),
        ("m = 4", "S₄(n) = ⅕·n⁵ − ½·n⁴ + ⅓·n³ − ⅓₀·n", "B₄ = −⅓₀"),
    ]

    Y0 = 120
    DY = 75
    CW1, CW2, CW3 = 110, 410, 210
    X1 = 50
    X2 = X1 + CW1 + 15
    X3 = X2 + CW2 + 15

    # Заголовки колонок
    p.append(rect(X1, Y0 - 30, CW1, 28, fill="#eef2ff", stroke="#c7d2fe", sw=1.2))
    p.append(text(X1 + CW1 / 2, Y0 - 11, "Степінь", size=13, bold=True, color=NEG))

    p.append(rect(X2, Y0 - 30, CW2, 28, fill="#eef2ff", stroke="#c7d2fe", sw=1.2))
    p.append(text(X2 + CW2 / 2, Y0 - 11, "Формула суми S_m(n)", size=13, bold=True, color=NEG))

    p.append(rect(X3, Y0 - 30, CW3, 28, fill="#eef2ff", stroke="#c7d2fe", sw=1.2))
    p.append(text(X3 + CW3 / 2, Y0 - 11, "Нове число Бернуллі", size=13, bold=True, color=NEG))

    for i, (m_str, sum_str, b_str) in enumerate(rows):
        y = Y0 + i * DY
        p.append(rect(X1, y, CW1, 58, fill=FILL, stroke=LINE, sw=1.2))
        p.append(text(X1 + CW1 / 2, y + 33, m_str, size=14, bold=True))

        p.append(rect(X2, y, CW2, 58, fill="#f8fafc", stroke=LINE, sw=1.2))
        p.append(text(X2 + CW2 / 2, y + 33, sum_str, size=14))

        p.append(rect(X3, y, CW3, 58, fill="#f0fdf4", stroke=FIELD, sw=1.4))
        p.append(text(X3 + CW3 / 2, y + 33, b_str, size=14, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, Y0 + 4 * DY + 25,
                      ["Загальна формула Фаульгабера: S_m(n) = (1 / (m+1)) · ∑ C(m+1, k) · B_k · n^(m+1-k)",
                       "Числа Бернуллі B_k задають універсальні коефіцієнти для будь-якого степеня m"],
                      size=13, pad=12, fill="#fbfbfc", stroke=LINE)
    p.append(b)

    render(os.path.join(OUT, "power-sums-triangle.svg"), W, H, *p,
           title="Структура сум степенів та числа Бернуллі")


# ── generating-function-symmetry: симетрія x/(e^x - 1) + x/2
def fig_generating_function_symmetry():
    W, H = 800, 520
    p = []

    p.append(text(W / 2, 45, "Симетрія твірної функції та непарні числа Бернуллі", size=15, bold=True))
    p.append(text(W / 2, 72, "Функція g(x) = x/(eˣ − 1) + x/2 є парною: g(−x) = g(x)", size=13, color=MUTED))

    # Дві панелі зі співвідношеннями
    BX1, BY1, BW1, BH1 = 60, 110, 320, 280
    p.append(rect(BX1, BY1, BW1, BH1, fill="#f8fafc", stroke=LINE, sw=1.3, rx=8))
    p.append(text(BX1 + BW1 / 2, BY1 + 35, "Розклад у степеневий ряд", size=14, bold=True, color=NEG))

    lines1 = [
        "x / (eˣ − 1) = ∑ Bₙ · xⁿ / n!",
        "",
        "= B₀ + B₁·x + B₂·x²/2! + B₃·x³/3! + …",
        "",
        "Оскільки B₀ = 1 та B₁ = −½:",
        "x / (eˣ − 1) = 1 − x/2 + ∑ (n≥2) Bₙ·xⁿ/n!"
    ]
    for i, line in enumerate(lines1):
        if line:
            p.append(text(BX1 + 20, BY1 + 75 + i * 32, line, size=13.5, anchor="start"))

    BX2, BY2, BW2, BH2 = 420, 110, 320, 280
    p.append(rect(BX2, BY2, BW2, BH2, fill="#f0fdf4", stroke=FIELD, sw=1.3, rx=8))
    p.append(text(BX2 + BW2 / 2, BY2 + 35, "Парність компенсованої функції", size=14, bold=True, color=FIELD))

    lines2 = [
        "Додамо x/2 до обох частин:",
        "g(x) = x / (eˣ − 1) + x/2",
        "",
        "= 1 + ∑ (n≥2) Bₙ · xⁿ / n!",
        "",
        "Перевірка парності: g(−x) = g(x)",
        "⇒ усі коефіцієнти при непарних xⁿ",
        "дорівнюють нулю: B₃ = B₅ = B₇ = … = 0"
    ]
    for i, line in enumerate(lines2):
        if line:
            p.append(text(BX2 + 20, BY2 + 75 + i * 28, line, size=13.5, anchor="start"))

    # Стрілка між панелями
    p.append(arrow(BX1 + BW1 + 10, BY1 + BH1 / 2, BX2 - 10, BY2 + BH2 / 2, color=NEG, sw=2))
    p.append(text((BX1 + BW1 + BX2) / 2, BY1 + BH1 / 2 - 15, "+ x/2", size=13, bold=True, color=NEG))

    b, _, _ = textbox(W / 2, 440,
                      ["Єдине ненульове непарне число Бернуллі — це B₁ = −½ (або +½ залежно від угоди).",
                       "Усі подальші непарні числа B₃, B₅, B₇, B₉, … тотожно дорівнюють нулю."],
                      size=13, pad=12, fill="#fffbe6", stroke="#ffe58f")
    p.append(b)

    render(os.path.join(OUT, "generating-function-symmetry.svg"), W, H, *p,
           title="Симетрія твірної функції чисел Бернуллі")


# ── staudt-clausen-denominators: будова знаменників за теоремою фон Штаудта — Клаузена
def fig_staudt_clausen_denominators():
    W, H = 820, 540
    p = []

    p.append(text(W / 2, 45, "Теорема фон Штаудта — Клаузена: будова знаменників B₂ₖ", size=15, bold=True))
    p.append(text(W / 2, 72, "Знаменник B₂ₖ дорівнює добутку простих p, для яких (p − 1) ділить 2k", size=13, color=MUTED))

    cases = [
        ("B₂ = ⅙", "2k = 2", "p − 1 | 2 ⇒ p = 2, 3", "2 · 3 = 6"),
        ("B₄ = −⅓₀", "2k = 4", "p − 1 | 4 ⇒ p = 2, 3, 5", "2 · 3 · 5 = 30"),
        ("B₆ = 1/42", "2k = 6", "p − 1 | 6 ⇒ p = 2, 3, 7", "2 · 3 · 7 = 42"),
        ("B₈ = −1/30", "2k = 8", "p − 1 | 8 ⇒ p = 2, 3, 5", "2 · 3 · 5 = 30"),
        ("B₁₂ = −691/2730", "2k = 12", "p − 1 | 12 ⇒ p = 2, 3, 5, 7, 13", "2 · 3 · 5 · 7 · 13 = 2730")
    ]

    Y0 = 125
    DY = 62
    CW1, CW2, CW3, CW4 = 140, 110, 280, 180
    X1 = 40
    X2 = X1 + CW1 + 10
    X3 = X2 + CW2 + 10
    X4 = X3 + CW3 + 10

    headers = [
        (X1, CW1, "Число Бернуллі B₂ₖ"),
        (X2, CW2, "Показник 2k"),
        (X3, CW3, "Прості p з умовою (p−1) | 2k"),
        (X4, CW4, "Знаменник den(B₂ₖ)")
    ]
    for x, cw, title in headers:
        p.append(rect(x, Y0 - 30, cw, 28, fill="#eef2ff", stroke="#c7d2fe", sw=1.2))
        p.append(text(x + cw / 2, Y0 - 11, title, size=13, bold=True, color=NEG))

    for i, (b_val, k_val, p_cond, den_val) in enumerate(cases):
        y = Y0 + i * DY
        p.append(rect(X1, y, CW1, 50, fill=FILL, stroke=LINE, sw=1.2))
        p.append(text(X1 + CW1 / 2, y + 29, b_val, size=14, bold=True))

        p.append(rect(X2, y, CW2, 50, fill="#f8fafc", stroke=LINE, sw=1.2))
        p.append(text(X2 + CW2 / 2, y + 29, k_val, size=13.5))

        p.append(rect(X3, y, CW3, 50, fill="#f8fafc", stroke=LINE, sw=1.2))
        p.append(text(X3 + CW3 / 2, y + 29, p_cond, size=13.5))

        p.append(rect(X4, y, CW4, 50, fill="#f0fdf4", stroke=FIELD, sw=1.4))
        p.append(text(X4 + CW4 / 2, y + 29, den_val, size=14, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, Y0 + 5 * DY + 20,
                      ["Формула Штаудта — Клаузена: B₂ₖ + ∑_{(p−1)|2k} (1/p) є цілим числом.",
                       "Знаменник завжди вільний від квадратів (без повторів простих множників) і містить 2 та 3 для всіх k ≥ 1."],
                      size=13, pad=12, fill="#fbfbfc", stroke=LINE)
    p.append(b)

    render(os.path.join(OUT, "staudt-clausen-denominators.svg"), W, H, *p,
           title="Знаменники чисел Бернуллі за теоремою фон Штаудта — Клаузена")


# ── akiyama-tanigawa-grid: трикутна сітка алгоритму Акіями — Таніґави
def fig_akiyama_tanigawa_grid():
    W, H = 820, 520
    p = []

    p.append(text(W / 2, 45, "Схема алгоритму Акіями — Таніґави для чисел Бернуллі", size=15, bold=True))
    p.append(text(W / 2, 72, "Перетворення початкового рядка A₀,ₘ = 1/(m+1) за правилом A_{i,j} = (j+1)·(A_{i-1,j} − A_{i-1,j+1})", size=13, color=MUTED))

    grid_data = [
        ["i=0", "1", "1/2", "1/3", "1/4", "1/5"],
        ["i=1", "1/2", "1/3", "1/4", "1/5", "—"],
        ["i=2", "1/6", "1/6", "3/20", "—", "—"],
        ["i=3", "0", "1/15", "—", "—", "—"],
        ["i=4", "-1/30", "—", "—", "—", "—"]
    ]

    Y0 = 125
    DY = 58
    CW = 100
    X0 = 60

    p.append(rect(X0, Y0 - 30, 80, 28, fill="#eef2ff", stroke="#c7d2fe", sw=1.2))
    p.append(text(X0 + 40, Y0 - 11, "Крок i", size=13, bold=True, color=NEG))

    for j in range(5):
        xj = X0 + 90 + j * (CW + 10)
        p.append(rect(xj, Y0 - 30, CW, 28, fill="#eef2ff", stroke="#c7d2fe", sw=1.2))
        p.append(text(xj + CW / 2, Y0 - 11, f"j = {j}", size=13, bold=True, color=NEG))

    for i, row in enumerate(grid_data):
        y = Y0 + i * DY
        p.append(rect(X0, y, 80, 48, fill="#f8fafc", stroke=LINE, sw=1.2))
        p.append(text(X0 + 40, y + 28, row[0], size=13.5, bold=True))

        for j in range(5):
            xj = X0 + 90 + j * (CW + 10)
            val = row[j + 1]
            if val == "—":
                continue
            is_bernoulli = (j == 0)
            fill_clr = "#f0fdf4" if is_bernoulli else FILL
            strk_clr = FIELD if is_bernoulli else LINE
            txt_clr = FIELD if is_bernoulli else "black"

            p.append(rect(xj, y, CW, 48, fill=fill_clr, stroke=strk_clr, sw=1.4 if is_bernoulli else 1.2))
            p.append(text(xj + CW / 2, y + 28, val, size=14, bold=is_bernoulli, color=txt_clr))

    b, _, _ = textbox(W / 2, Y0 + 5 * DY + 15,
                      ["Ліва колонка j = 0 дає числа Бернуллі B₀, B₁, B₂, B₃, B₄, … у позиції A_{i,0}.",
                       "Алгоритм потребує лише O(n²) раціональних операцій без обчислення біноміальних коефіцієнтів."],
                      size=13, pad=12, fill="#fbfbfc", stroke=LINE)
    p.append(b)

    render(os.path.join(OUT, "akiyama-tanigawa-grid.svg"), W, H, *p,
           title="Сітка алгоритму Акіями — Таніґави для чисел Бернуллі")


def main():
    fig_power_sums_triangle()
    fig_generating_function_symmetry()
    fig_staudt_clausen_denominators()
    fig_akiyama_tanigawa_grid()
    print("Figures generated successfully in img/")

if __name__ == "__main__":
    main()
