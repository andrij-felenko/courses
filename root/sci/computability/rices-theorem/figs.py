# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми «Теорема Райса».
Всі фігури відповідають канону AUTHORING: білий фон, єдина палітра,
рамки з текстом через textbox/fitbox/fitwidth, без перетинів і налізань.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Синтаксис проти семантики ──────────────────────────────────────────
# Ідея: синтаксичний поділ (довжина коду, наявність токенів, розмір AST) — розв'язний,
# бо дивиться лише на текст програми. Семантичний поділ (що саме обчислює програма,
# множина partial functions) — нерозв'язний за теоремою Райса, бо програми з різним
# текстом обчислюють одну й ту саму функцію.
def fig_semantic_vs_syntactic():
    W, H = 880, 480
    p = []

    # Ліва колонка: Синтаксичні властивості (розв'язні)
    p.append(rect(40, 60, 380, 360, fill="#f4fbf6", stroke=FIELD, sw=2.0, rx=12))
    p.append(text(230, 92, "Синтаксичні властивості", size=15, color=FIELD, bold=True))
    p.append(text(230, 114, "Аналіз тексту програми (коду / AST)", size=12, color=MUTED))

    b1, _, _ = textbox(230, 160, "«Чи містить код цикл while?»\n(пошук токена в тексті)", size=12, pad=8, fill=BG, stroke=FIELD)
    p.append(b1)
    b2, _, _ = textbox(230, 230, "«Чи розмір AST менший за 50 вузлів?»\n(підрахунок вузлів дерева)", size=12, pad=8, fill=BG, stroke=FIELD)
    p.append(b2)
    b3, _, _ = textbox(230, 300, "«Чи є в тексті явна команда return?»\n(перевірка синтаксису)", size=12, pad=8, fill=BG, stroke=FIELD)
    p.append(b3)

    b_res1, _, _ = textbox(230, 375, "РОЗВ'ЯЗНІ ЗАВЖДИ ✓\n(алгоритм читає лише скінченний текст)", size=12.5, pad=8, fill="#eef7f0", stroke=FIELD, color=FIELD, bold=True)
    p.append(b_res1)

    # Права колонка: Семантичні властивості (нерозв'язні за Райсом)
    p.append(rect(460, 60, 380, 360, fill="#fdf5f5", stroke=POS, sw=2.0, rx=12))
    p.append(text(650, 92, "Семантичні властивості", size=15, color=POS, bold=True))
    p.append(text(650, 114, "Аналіз поведінки / обчислюваної функції φ_e", size=12, color=MUTED))

    b4, _, _ = textbox(650, 160, "«Чи обчислює код функцію f(x) = 0?»\n(значення для всіх входів x)", size=12, pad=8, fill=BG, stroke=POS)
    p.append(b4)
    b5, _, _ = textbox(650, 230, "«Чи завершується код на вході x = 42?»\n(проблема зупинки на точці)", size=12, pad=8, fill=BG, stroke=POS)
    p.append(b5)
    b6, _, _ = textbox(650, 300, "«Чи є дві програми еквівалентними?»\n(рівність функцій φ_a = φ_b)", size=12, pad=8, fill=BG, stroke=POS)
    p.append(b6)

    b_res2, _, _ = textbox(650, 375, "НЕРОЗВ'ЯЗНІ (Теорема Райса) ✗\n(жоден алгоритм не вирішить для всіх кодів)", size=12.5, pad=8, fill="#fdecea", stroke=POS, color=POS, bold=True)
    p.append(b_res2)

    p.append(text(440, 452, "Вододіл: синтаксис — про те, ЯК написаний код; семантика — про те, ЩО він обчислює.", size=12, color=INK))

    render(os.path.join(OUT, "rice-semantic-vs-syntactic.svg"), W, H, *p,
           title="Синтаксис проти семантики: де проходить межа обчислюваного")


# ── Фіг. 2: Ґаджет зведення теореми Райса ──────────────────────────────────────
# Ідея: Будуємо трансформер, який за парою (M, w) алгоритмічно генерує код програми
# Q_{M,w}(x): «виконай M(w); якщо спинилось, порахуй g(x)».
# Якщо M(w) спиняється -> Q обчислює g in P -> Q in I_P.
# Якщо M(w) зациклюється -> Q обчислює f_empty not in P -> Q not in I_P.
# Оракул для I_P розв'язав би проблему зупинки!
def fig_rice_gadget_reduction():
    W, H = 880, 520
    p = []
    cx = 440.0

    # Вхід: пара (M, w)
    b_in, _, _ = textbox(cx, 60, "Вхід проблеми зупинки: пара ⟨M, w⟩\n(програма M та її вхідні дані w)",
                         size=13, bold=True, fill="#eef2fb", stroke=NEG, color=NEG)
    p.append(b_in)
    p.append(arrow(cx, 86, cx, 126, color=INK, sw=1.7))

    # Трансформатор Кліні (s-m-n)
    b_trans, _, _ = textbox(cx, 160, "Алгоритмічний синтез коду (s-m-n теорема):\nСтворюємо нову програму Q_{M,w}(x)",
                            size=13, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK)
    p.append(b_trans)
    p.append(arrow(cx, 192, cx, 232, color=INK, sw=1.7))

    # Тіло згенерованої програми Q_{M,w}(x)
    b_code, _, _ = textbox(cx, 275, "Тіло програми Q_{M,w}(x):\n1. Запустити M на вході w (ігноруючи x)\n2. Якщо M(w) спинилась — обчислити й повернути g(x), де g ∈ P",
                           size=12, pad=10, fill=FILL, stroke=LINE, color=INK)
    p.append(b_code)

    # Дві гілки поведінки
    xL, xR = 230.0, 650.0
    p.append(arrow(cx - 60, 318, xL + 50, 355, color=INK, sw=1.6))
    p.append(arrow(cx + 60, 318, xR - 50, 355, color=INK, sw=1.6))

    # Ліва гілка: M(w) спиняється
    b_left1, _, _ = textbox(xL, 385, "M(w) СПИНЯЄТЬСЯ\nКрок 1 завершується ⟹\nQ_{M,w} обчислює функцію g ∈ P\n⟹ Q_{M,w} ∈ I_P",
                            size=11.5, bold=True, fill="#eef7f0", stroke=FIELD, color=FIELD)
    p.append(b_left1)

    # Права гілка: M(w) зависає
    b_right1, _, _ = textbox(xR, 385, "M(w) ЗАЦИКЛЮЄТЬСЯ\nКрок 1 крутиться вічно ⟹\nQ_{M,w} обчислює f_∅ ∉ P\n⟹ Q_{M,w} ∉ I_P",
                             size=11.5, bold=True, fill="#fdecea", stroke=POS, color=POS)
    p.append(b_right1)

    # Підсумковий висновок
    b_res, _, _ = textbox(cx, 475, "M(w) спиняється  ⟺  Q_{M,w} має властивість P  ⟹  I_P нерозв'язна",
                          size=13.5, bold=True, fill="#f4f6f8", stroke=LINE, color=INK)
    p.append(b_res)
    p.append(arrow(xL, 424, cx - 180, 460, color=MUTED, sw=1.4))
    p.append(arrow(xR, 424, cx + 180, 460, color=MUTED, sw=1.4))

    render(os.path.join(OUT, "rice-gadget-reduction.svg"), W, H, *p,
           title="Зведення проблеми зупинки до довільної семантичної властивості")


# ── Фіг. 3: Трикутник компромісів статичного аналізу ─────────────────────────
# Ідея: За теоремою Райса неможливо одночасно досягти трьох речей:
# 1. Надійність (Soundness) — жодних пропущених багів (false negatives = 0).
# 2. Повнота (Completeness) — жодних хибних тривог (false positives = 0).
# 3. Завершуваність (Termination) — гарантована зупинка алгоритму на будь-якому коді.
# Можна обрати щонайбільше дві з трьох.
def fig_soundness_completeness_triangle():
    W, H = 920, 520
    p = []

    # Вершини трикутника
    x_top, y_top = 460.0, 85.0
    x_left, y_left = 150.0, 380.0
    x_right, y_right = 770.0, 380.0

    # Сторони трикутника
    p.append(line(x_top, y_top, x_left, y_left, color=LINE, sw=2.0))
    p.append(line(x_top, y_top, x_right, y_right, color=LINE, sw=2.0))
    p.append(line(x_left, y_left, x_right, y_right, color=LINE, sw=2.0))

    # Вершина 1: Надійність (Soundness)
    b_top, _, _ = textbox(x_top, y_top - 20, "НАДІЙНІСТЬ (Soundness)\nЖодних пропусків помилок (0 false negatives)",
                          size=12, bold=True, fill="#eef7f0", stroke=FIELD, color=FIELD)
    p.append(b_top)

    # Вершина 2: Повнота (Completeness)
    b_left, _, _ = textbox(x_left - 10, y_left + 35, "ПОВНОТА (Completeness)\nЖодних хибних тривог (0 false positives)",
                           size=11.5, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG)
    p.append(b_left)

    # Вершина 3: Завершуваність (Termination)
    b_right, _, _ = textbox(x_right + 10, y_left + 35, "ЗАВЕРШУВАНІСТЬ (Termination)\nАналізатор спиняється на будь-якому коді",
                            size=11.5, bold=True, fill="#fff6e6", stroke="#e08a1e", color="#b9700f")
    p.append(b_right)

    # Реальні інструменти на ребрах
    # Ребро Soundness + Termination (Абстрактна інтерпретація, Linters): платять хибними тривогами
    b_edge1, _, _ = textbox(670, 210, "Статичні аналізатори\n(Abstract Interpretation)\n• Надійні (не пропускають)\n• Завжди завершуються\n✗ Є хибні тривоги",
                            size=11, pad=7, fill=FILL, stroke=LINE)
    p.append(b_edge1)

    # Ребро Completeness + Termination (Тестування, Fuzzing, Bounded Model Checking): платять пропусками
    b_edge2, _, _ = textbox(250, 210, "Динамічне тестування\n(Fuzzing / Testing)\n• Повні (якщо знайшов — є)\n• Завжди завершуються\n✗ Можуть пропустити баг",
                            size=11, pad=7, fill=FILL, stroke=LINE)
    p.append(b_edge2)

    # Ребро Soundness + Completeness (Повна верифікація): платять зависанням / ручною працею
    b_edge3, _, _ = textbox(460, 460, "Повна формальна верифікація (Interactive Provers)\n• Надійні + Повні ⟹ Не завершуються автоматично (потрібна допомога людини)",
                            size=11, pad=7, fill=FILL, stroke=LINE)
    p.append(b_edge3)

    # Центр: Теорема Райса забороняє всі три одночасно
    b_center, _, _ = textbox(460, 260, "ТЕОРЕМА РАЙСА:\nОдночасно всі три —\nНЕДОСЯЖНО",
                             size=13, bold=True, fill="#fdecea", stroke=POS, color=POS)
    p.append(b_center)

    render(os.path.join(OUT, "soundness-completeness-triangle.svg"), W, H, *p,
           title="Трикутник неможливості: чому ідеального верифікатора не існує")


# ── Фіг. 4: Теорема Райса–Шапіро — напіврозв'язність і скінченні підфункції ───
# Ідея: Теорема Райса–Шапіро стверджує, що індексна множина I_P є рекурсивно
# перелічуваною (напіврозв'язною) тоді й лише тоді, коли функція f належить P
# завдяки деякій своїй СКІНЧЕННІЙ підфункції theta subseteq f.
def fig_rice_shapiro_lattice():
    W, H = 880, 460
    p = []
    cx = 440.0

    # Верхній блок: нескінченна функція f
    b_f, _, _ = textbox(cx, 80, "Повна обчислювана функція f ∈ P\n(нескінченний графік: f(0), f(1), f(2), ...)",
                        size=13, bold=True, fill="#eef2fb", stroke=NEG, color=NEG)
    p.append(b_f)
    p.append(arrow(cx, 110, cx, 160, color=INK, sw=1.7))

    # Середній блок: скінченна підфункція theta
    b_theta, _, _ = textbox(cx, 200, "Скінченна підфункція θ ⊆ f\n(визначена лише на скінченній множині точок {x_1, ..., x_k})\nде θ ТАКОЖ має властивість P (θ ∈ P)",
                            size=12.5, bold=True, fill="#eef7f0", stroke=FIELD, color=FIELD)
    p.append(b_theta)

    # Дві умови теореми Райса–Шапіро
    xL, xR = 230.0, 650.0
    p.append(arrow(cx - 70, 240, xL + 40, 280, color=INK, sw=1.6))
    p.append(arrow(cx + 70, 240, xR - 40, 280, color=INK, sw=1.6))

    b_cond1, _, _ = textbox(xL, 335, "1. Компактність (Коректність):\nЯкщо f ∈ P, то існує скінченна θ ⊆ f,\nяка вже гарантує θ ∈ P.\n(Властивість проявляється за скінченний час)",
                            size=11.5, bold=True, fill=FILL, stroke=LINE)
    p.append(b_cond1)

    b_cond2, _, _ = textbox(xR, 335, "2. Монотонність:\nЯкщо скінченна θ ∈ P і θ ⊆ g,\nто будь-яке її розширення g ТАКОЖ g ∈ P.\n(Додавання значень не може зруйнувати P)",
                            size=11.5, bold=True, fill=FILL, stroke=LINE)
    p.append(b_cond2)

    # Висновок внизу
    b_bot, _, _ = textbox(cx, 425, "I_P є напіврозв'язною (Σ₁)  ⟺  P визначається перелічуваною сім'єю скінченних підфункцій",
                          size=12.5, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK)
    p.append(b_bot)

    render(os.path.join(OUT, "rice-shapiro-lattice.svg"), W, H, *p,
           title="Теорема Райса–Шапіро: напіврозв'язність через скінченні підфункції")


if __name__ == "__main__":
    fig_semantic_vs_syntactic()
    fig_rice_gadget_reduction()
    fig_soundness_completeness_triangle()
    fig_rice_shapiro_lattice()
    print("OK figs")
