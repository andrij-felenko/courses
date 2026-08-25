# -*- coding: utf-8 -*-
"""Фігури до теми «Зображення Галуа»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_galois_representation_concept():
    """Фігура 1: Концепція зображення Галуа: міст від нескінченної групи до лінійних операторів."""
    W, H = 880, 440
    frags = []

    # Заголовок
    frags.append(textbox(440, 30, "Концепція зображення Галуа: перехід від абстрактних симетрій до лінійної алгебри", size=13, bold=True, fill="#f8fafc")[0])

    # Лівий блок: Абсолютна група Галуа G_Q
    tb_gq, _, _ = textbox(180, 130, "Абсолютна група Галуа G_Q = Gal(Q̄/Q)\n\nНескінченна, неабелева,\nпроскінченна група симетрій\nвсіх алгебраїчних чисел", size=12, bold=True, fill="#eff6ff", stroke="#2563eb", sw=2)
    frags.append(tb_gq)

    frags.append(textbox(180, 240, "Топологія Крулля\n(компактна, тотально незв'язна)\nБазис околів: Gal(Q̄/K)\nдля скінченних K / Q", size=11, fill="#f1f5f9", stroke="#64748b")[0])

    frags.append(textbox(180, 345, "Елементи: автоморфізми σ\nСпряжені класи:\nелементи Фробеніуса Frob_p", size=11, fill="#f8fafc", stroke="#94a3b8")[0])

    # Центральна стрілка гомоморфізму
    frags.append(arrow(310, 130, 530, 130, color=POS, sw=2.5))
    frags.append(textbox(420, 105, "Неперервний гомоморфізм ρ\nρ(σ · τ) = ρ(σ) · ρ(τ)", size=11, bold=True, fill="#fff1f2", stroke=POS, sw=1.8)[0])

    frags.append(textbox(420, 240, "ЛІНЕАРИЗАЦІЯ ДІЇ\n\nНевідомі симетрії σ\nперетворюються на\nконкретні матриці M_σ", size=11, bold=True, fill="#fffbeb", stroke="#d97706", sw=1.8)[0])

    # Правий блок: Лінійна група GL_n(K)
    tb_gln, _, _ = textbox(680, 130, "Група лінійних операторів\nGL_n(Q_ℓ)  або  GL_n(C)\n\nОборотні матриці n × n\nнад ℓ-адичним полем Q_ℓ", size=12, bold=True, fill="#ecfdf5", stroke=FIELD, sw=2)
    frags.append(tb_gln)

    frags.append(textbox(680, 240, "Векторний простір V ≅ Q_ℓⁿ\n\n• n = 1: Круговий характер χ_ℓ\n• n = 2: Модуль Тейта V_ℓ(E)", size=11, fill="#f0fdf4", stroke=FIELD)[0])

    frags.append(textbox(680, 345, "Лінійні інваріанти оператора:\n• Слід Tr(ρ(σ))\n• Визначник det(ρ(σ))\n• Характеристичний многочлен", size=11, fill="#f8fafc", stroke="#94a3b8")[0])

    # Нижня стрілка зв'язку інваріантів
    frags.append(arrow(530, 345, 310, 345, color=FIELD, sw=2))
    frags.append(textbox(420, 385, "Сліди матриць Tr(ρ(Frob_p))\nоднозначно відновлюють зображення ρ\n(Теорема щільності Чеботарьова)", size=10, fill="#f8fafc", stroke="#94a3b8")[0])

    render(os.path.join(OUT, "galois-representation-concept.svg"), W, H, *frags)


def fig_tate_module_action():
    """Фігура 2: Вежа точок кручення еліптичної кривої та модуль Тейта."""
    W, H = 840, 460
    frags = []

    # Заголовок
    frags.append(textbox(420, 30, "Модуль Тейта T_ℓ(E): проєктивна границя точок кручення еліптичної кривої", size=13, bold=True, fill="#f8fafc")[0])

    # Рівні вежі (зліва направо або зверху вниз)
    # Зверху: T_ℓ(E)
    tb_top, _, _ = textbox(420, 90, "Модуль Тейта:  T_ℓ(E) = lim_inv E[ℓⁿ] ≅ Z_ℓ²\nРаціональний модуль:  V_ℓ(E) = T_ℓ(E) ⊗ Q_ℓ ≅ Q_ℓ²  (2-вимірний)", size=12, bold=True, fill="#eff6ff", stroke="#2563eb", sw=2)
    frags.append(tb_top)

    frags.append(arrow(420, 125, 420, 160, color=LINE, sw=1.8))

    # Рівень n = 3
    tb_n3, _, _ = textbox(420, 180, "Кручення порядку ℓ³:   E[ℓ³] ≅ (Z / ℓ³Z)²   [група з ℓ⁶ точок]", size=11, bold=True, fill="#f8fafc", stroke=LINE)
    frags.append(tb_n3)

    frags.append(arrow(420, 200, 420, 235, color=LINE, sw=1.8))
    frags.append(text(465, 218, "множення на ℓ", size=10, color=MUTED, italic=True))

    # Рівень n = 2
    tb_n2, _, _ = textbox(420, 255, "Кручення порядку ℓ²:   E[ℓ²] ≅ (Z / ℓ²Z)²   [група з ℓ⁴ точок]", size=11, bold=True, fill="#f8fafc", stroke=LINE)
    frags.append(tb_n2)

    frags.append(arrow(420, 275, 420, 310, color=LINE, sw=1.8))
    frags.append(text(465, 293, "множення на ℓ", size=10, color=MUTED, italic=True))

    # Рівень n = 1
    tb_n1, _, _ = textbox(420, 330, "Кручення порядку ℓ:    E[ℓ] ≅ (Z / ℓZ)²     [група з ℓ² точок над Q̄]", size=11, bold=True, fill="#ecfdf5", stroke=FIELD, sw=2)
    frags.append(tb_n1)

    # Дія групи Галуа (збоку)
    frags.append(rect(60, 170, 220, 170, fill="#fff1f2", stroke=POS, sw=1.8, rx=6))
    frags.append(textbox(170, 195, "Дія автоморфізму σ ∈ G_Q", size=11, bold=True, fill="#fee2e2", stroke=POS)[0])
    frags.append(mtext(170, 245, "σ зберігає закон додавання на E:\nσ(P + Q) = σ(P) + σ(Q)\n\nσ комутує з множенням на ℓ:\nσ(ℓ · P) = ℓ · σ(P)", size=10, color=INK))

    frags.append(arrow(280, 255, 330, 255, color=POS, sw=2))

    # Матричне зображення (справа)
    frags.append(rect(560, 170, 220, 170, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    frags.append(textbox(670, 195, "Матриця оператора ρ_{E,ℓ}(σ)", size=11, bold=True, fill="#dcfce7", stroke=FIELD)[0])
    frags.append(mtext(670, 245, "У базисі {P, Q} модуля T_ℓ(E):\n\nρ_{E,ℓ}(σ) = [ a  b ]\n             [ c  d ]\nде a, b, c, d ∈ Z_ℓ", size=10, color=INK))

    frags.append(arrow(510, 255, 560, 255, color=FIELD, sw=2))

    # Нижній висновок про спарювання Вейля
    frags.append(textbox(420, 415, "Спарювання Вейля: e_ℓ(σ P, σ Q) = e_ℓ(P, Q)^{χ_ℓ(σ)}   ==>   Визначник: det(ρ_{E,ℓ}(σ)) = χ_ℓ(σ) (круговий характер)", size=11, bold=True, fill="#fffbeb", stroke="#d97706", sw=1.8)[0])

    render(os.path.join(OUT, "tate-module-action.svg"), W, H, *frags)


def fig_modularity_bridge():
    """Фігура 3: Великий міст модулярності (Таніяма–Сімура–Вейль)."""
    W, H = 920, 460
    frags = []

    # Заголовок
    frags.append(textbox(460, 30, "Теорема модулярності: взаємно однозначна відповідність трьох математичних світів", size=13, bold=True, fill="#f8fafc")[0])

    # Лівий вузол: Геометрія (Еліптичні криві)
    tb_e, _, _ = textbox(170, 140, "АЛГЕБРАЇЧНА ГЕОМЕТРІЯ\n\nЕліптична крива E / Q\ny² = x³ + Ax + B\nКондуктор N", size=12, bold=True, fill="#eff6ff", stroke="#2563eb", sw=2)
    frags.append(tb_e)
    frags.append(textbox(170, 245, "Кількість точок редукції:\n#E(F_p) = p + 1 − a_p\n\nДефект точок:\na_p(E) = p + 1 − #E(F_p)\n(Нерівність Гассе: |a_p| ≤ 2√p)", size=11, fill="#f8fafc", stroke="#64748b")[0])

    # Центральний вузол: Арифметика (Зображення Галуа)
    tb_gal, _, _ = textbox(460, 140, "АРИФМЕТИКА ТА АЛГЕБРА\n\nЗображення Галуа\nρ_{E,ℓ}: G_Q → GL₂(Q_ℓ)\nНерозгалужене поза ℓ · N", size=12, bold=True, fill="#ecfdf5", stroke=FIELD, sw=2)
    frags.append(tb_gal)
    frags.append(textbox(460, 245, "Слід елемента Фробеніуса:\nTr(ρ_{E,ℓ}(Frob_p)) = a_p(E)\n\nХарактеристичний многочлен:\ndet(I − T · ρ(Frob_p)) =\n= 1 − a_p T + p T²", size=11, fill="#f8fafc", stroke=FIELD)[0])

    # Правий вузол: Комплексний аналіз (Модулярні форми)
    tb_mod, _, _ = textbox(750, 140, "КОМПЛЕКСНИЙ АНАЛІЗ\n\nПараболічна модулярна форма\nf(z) ∈ S₂(Γ₀(N))\nРівень N, вага 2", size=12, bold=True, fill="#fff1f2", stroke=POS, sw=2)
    frags.append(tb_mod)
    frags.append(textbox(750, 245, "Ряд Фур'є (q-розклад):\nf(z) = ∑_{n=1}^∞ a_n(f) qⁿ\nq = e^{2π i z}\n\nВласна форма операторів Гекке:\nT_p(f) = a_p(f) · f", size=11, fill="#f8fafc", stroke=POS)[0])

    # Горизонтальні двосторонні стрілки еквівалентності
    frags.append(arrow(275, 140, 345, 140, color=FIELD, sw=2.2))
    frags.append(arrow(345, 140, 275, 140, color=FIELD, sw=2.2))

    frags.append(arrow(575, 140, 645, 140, color=POS, sw=2.2))
    frags.append(arrow(645, 140, 575, 140, color=POS, sw=2.2))

    # Нижній об'єднавчий блок — Тотожність L-функцій
    frags.append(rect(140, 340, 640, 95, fill="#fffbeb", stroke="#d97706", sw=2, rx=8))
    frags.append(textbox(460, 365, "ГОЛОВНА ТОТОЖНІСТЬ МОДУЛЯРНОСТІ:  a_p(E) = Tr(ρ(Frob_p)) = a_p(f)", size=12, bold=True, fill="#fef3c7", stroke="#d97706")[0])
    frags.append(mtext(460, 405, "L-функція кривої E дорівнює L-функції модулярної форми f:\nL(E, s) = ∑ a_n(E) · n^{-s}  ≡  ∑ a_n(f) · n^{-s} = L(f, s)", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "modularity-bridge.svg"), W, H, *frags)


def fig_wiles_fermat_chain():
    """Фігура 4: Логічний ланцюг доведення Великої теореми Ферма Ендрю Вайлсом."""
    W, H = 960, 450
    frags = []

    # Заголовок
    frags.append(textbox(480, 30, "Логічний ланцюг доведення Великої теореми Ферма через зображення Галуа", size=13, bold=True, fill="#f8fafc")[0])

    # Крок 1: Гіпотетичний розв'язок Ферма
    tb1, _, _ = textbox(130, 110, "1. Припущення від супротивного\naᵖ + bᵖ = cᵖ\nдля простих p ≥ 5\n(a, b, c взаємно прості)", size=11, bold=True, fill="#fef2f2", stroke=POS, sw=1.8)
    frags.append(tb1)

    frags.append(arrow(220, 110, 270, 110, color=LINE, sw=2))

    # Крок 2: Крива Фрея
    tb2, _, _ = textbox(360, 110, "2. Крива Фрея E_{A,B,C}\ny² = x (x − aᵖ)(x + bᵖ)\nНапівстабільна еліптична крива\nΔ = (a · b · c)^{2p} / 2⁸", size=11, bold=True, fill="#eff6ff", stroke="#2563eb", sw=1.8)
    frags.append(tb2)

    frags.append(arrow(450, 110, 500, 110, color=LINE, sw=2))

    # Крок 3: Резидуальне зображення
    tb3, _, _ = textbox(600, 110, "3. Резидуальне зображення\nρ̄_{E,p}: G_Q → GL₂(F_p)\nНезвідне за Мазуром;\nрозгалужене лише в 2 і p", size=11, bold=True, fill="#ecfdf5", stroke=FIELD, sw=1.8)
    frags.append(tb3)

    frags.append(arrow(700, 110, 750, 110, color=LINE, sw=2))

    # Крок 4: Теорема Рібета (ε-гіпотеза Серра)
    tb4, _, _ = textbox(850, 110, "4. Зниження рівня (Рібет)\nЯкщо E модулярна, то\nρ̄_{E,p} походить від\nформи ваги 2 рівня N = 2", size=11, bold=True, fill="#fffbeb", stroke="#d97706", sw=1.8)
    frags.append(tb4)

    # Стрілка вниз до Вайлса
    frags.append(arrow(360, 175, 360, 240, color="#2563eb", sw=2.2))
    frags.append(text(435, 208, "Крива напівстабільна", size=10, color="#2563eb", bold=True))

    # Крок 5: Теорема Вайлса (R = T)
    tb5, _, _ = textbox(360, 310, "5. Теорема Вайлса та Тейлора–Вайлса (1995)\n\nУсі напівстабільні еліптичні криві над Q є МОДУЛЯРНИМИ!\nДоведено через ізоморфізм кілець деформацій:\nR ≅ T  (універсальне кільце деформацій = алгебра Гекке)", size=11, bold=True, fill="#dbeafe", stroke="#1d4ed8", sw=2)
    frags.append(tb5)

    frags.append(arrow(540, 310, 680, 310, color=POS, sw=2.5))
    frags.append(text(610, 290, "Крива Фрея модулярна!", size=11, color=POS, bold=True))

    # Крок 6: Фінальне протиріччя
    tb6, _, _ = textbox(810, 310, "6. ФАТАЛЬНЕ ПРОТИРІЧЧЯ\n\nПростір модулярних форм рівня 2:\nS₂(Γ₀(2)) = { 0 }  (порожній!)\nФорми f рівня N = 2 не існує!\n\n==> Розв'язку aᵖ + bᵖ = cᵖ НЕ ІСНУЄ!", size=11, bold=True, fill="#fee2e2", stroke=POS, sw=2.2)
    frags.append(tb6)

    # Замикання ланцюга
    frags.append(arrow(850, 175, 850, 240, color=POS, sw=2.2))

    render(os.path.join(OUT, "wiles-fermat-chain.svg"), W, H, *frags)


if __name__ == '__main__':
    fig_galois_representation_concept()
    fig_tate_module_action()
    fig_modularity_bridge()
    fig_wiles_fermat_chain()
    print("All figures generated successfully.")
