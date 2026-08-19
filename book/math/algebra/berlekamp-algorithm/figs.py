# -*- coding: utf-8 -*-
"""Фігури до статті «Алгоритм Берлекампа»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Повний конвеєр алгоритму Берлекампа
# ─────────────────────────────────────────────────────────────────────────────
def fig_berlekamp_flow():
    W, H = 840, 520
    frby = []

    # Заголовок зверху
    frby.append(text(W / 2, 30, "Конвеєр факторизації многочлена f(x) над скінченним полем GF(q)", size=15, bold=True, color=INK))

    # Крок 1: Вхідний многочлен
    b1, w1, h1 = textbox(150, 95, "Вхід: многочлен f(x)\nстепеня n над GF(q)", size=13, pad=10, fill="#f8fafc", stroke=LINE, sw=1.5)
    frby.append(b1)

    # Крок 2: Безквадратний розклад
    b2, w2, h2 = textbox(470, 95, "1. Перевірка на кратні множники\nОбчислення похідної f'(x) та НСД(f, f')", size=13, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.5)
    frby.append(b2)

    frby.append(arrow(260, 95, 330, 95, color=INK, sw=1.8))
    frby.append(text(295, 83, "f(x)", size=11, color=MUTED))

    # Крок 3: Матриця Берлекампа Q
    b3, w3, h3 = textbox(470, 220, "2. Побудова матриці Q (n × n)\nРядок i: x^(i·q) mod f(x) для i = 0..n-1", size=13, pad=10, fill="#eff6ff", stroke=NEG, sw=1.5)
    frby.append(b3)

    frby.append(arrow(470, 135, 470, 185, color=INK, sw=1.8))
    frby.append(text(540, 160, "без квадратів", size=11, color=FIELD))

    # Крок 4: Ядро матриці (Q - I)
    b4, w4, h4 = textbox(470, 345, "3. Розв'язання системи: v · (Q - I) = 0\nЗнаходження ядра ker(Q - I) методом Гаусса\nРозмірність ядра k = dim ker(Q - I)", size=13, pad=10, fill="#fefce8", stroke="#ca8a04", sw=1.5)
    frby.append(b4)

    frby.append(arrow(470, 255, 470, 305, color=INK, sw=1.8))
    frby.append(text(535, 280, "матриця Q", size=11, color=NEG))

    # Розгалуження: k = 1 (незвідний) або k > 1 (розщеплення)
    # Ліва гілка: k = 1
    b5a, w5a, h5a = textbox(170, 445, "k = 1: Ядро одновимірне (константи)\nf(x) є незвідним многочленом", size=13, pad=10, fill="#fef2f2", stroke=POS, sw=1.5)
    frby.append(b5a)

    frby.append(arrow(340, 370, 220, 415, color=POS, sw=1.8))
    frby.append(text(250, 380, "k = 1", size=12, bold=True, color=POS))

    # Права гілка: k > 1
    b5b, w5b, h5b = textbox(630, 445, "k > 1: Взяти базисний v(x) ∉ GF(q)\nОбчислити НСД(f(x), v(x) - s) для s ∈ GF(q)\nРекурсивно розщепити на k множників", size=13, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.5)
    frby.append(b5b)

    frby.append(arrow(580, 370, 630, 410, color=FIELD, sw=1.8))
    frby.append(text(630, 380, "k > 1", size=12, bold=True, color=FIELD))

    render(os.path.join(OUT, "berlekamp-flow.svg"), W, H, *frby,
           title="Конвеєр факторизації многочлена f(x) за алгоритмом Берлекампа")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Алгебраїчна структура та ізоморфізм китайської теореми про остачі
# ─────────────────────────────────────────────────────────────────────────────
def fig_berlekamp_isomorphism():
    W, H = 840, 460
    frby = []

    frby.append(text(W / 2, 28, "Ізоморфізм Китайської теореми та підалгебра Берлекампа", size=15, bold=True, color=INK))

    # Ліва частина: Фактор-кільце R
    frby.append(rect(40, 60, 340, 360, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frby.append(text(210, 88, "Фактор-кільце R = GF(q)[x] / (f(x))", size=14, bold=True, color=INK))
    frby.append(line(50, 102, 370, 102, color=LINE, sw=1))

    frby.append(text(210, 130, "Многочлен f(x) = f₁(x) · f₂(x) · ... · f_k(x)", size=12, bold=True, color=INK))
    frby.append(text(210, 155, "Степінь многочлена n, розмірність R над GF(q) = n", size=11, color=MUTED))

    # Підалгебра всередині
    frby.append(rect(65, 185, 290, 210, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frby.append(text(210, 212, "Підалгебра Берлекампа B ⊂ R", size=13, bold=True, color=NEG))
    frby.append(text(210, 235, "{ v(x) ∈ R | v(x)^q ≡ v(x) mod f(x) }", size=12, bold=True, color=INK))
    frby.append(line(80, 248, 340, 248, color=NEG, sw=1, dash="3 3"))

    frby.append(text(210, 275, "Операція v ↦ v^q лінійна завдяки", size=11, color=INK))
    frby.append(text(210, 295, "автоморфізму Фробеніуса: (a + b)^q = a^q + b^q", size=11, color=INK))
    frby.append(text(210, 330, "Векторне рівняння: v · (Q - I) = 0", size=12, bold=True, color=NEG))
    frby.append(text(210, 365, "Розмірність: dim(B) = k (кількість множників)", size=12, bold=True, color=FIELD))

    # Центральна стрілка ізоморфізму
    frby.append(arrow(390, 240, 445, 240, color=FIELD, sw=2.5))
    frby.append(text(418, 225, "≅", size=20, bold=True, color=FIELD))
    frby.append(text(418, 260, "КТО", size=12, bold=True, color=FIELD))

    # Права частина: Прямий добуток полів
    frby.append(rect(455, 60, 345, 360, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frby.append(text(627, 88, "Прямий добуток фактор-полів", size=14, bold=True, color=INK))
    frby.append(line(465, 102, 790, 102, color=LINE, sw=1))

    frby.append(text(627, 130, "∏ (GF(q)[x] / (f_i(x))) для i = 1..k", size=13, bold=True, color=INK))
    frby.append(text(627, 155, "Кожен множник f_i(x) породжує своє поле", size=11, color=MUTED))

    # Відображення підалгебри
    frby.append(rect(480, 185, 295, 210, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frby.append(text(627, 212, "Образ підалгебри B в ізоморфізмі", size=13, bold=True, color=FIELD))
    frby.append(text(627, 235, "v(x) mod f_i(x) = s_i ∈ GF(q)", size=12, bold=True, color=INK))
    frby.append(line(495, 248, 760, 248, color=FIELD, sw=1, dash="3 3"))

    frby.append(text(627, 275, "Рівняння s^q = s у кожному полі GF(q^deg(f_i))", size=11, color=INK))
    frby.append(text(627, 295, "має рівно q розв'язків — константи базового GF(q)", size=11, color=INK))
    frby.append(text(627, 330, "Кортеж: (s₁, s₂, ..., s_k) ∈ GF(q)^k", size=12, bold=True, color=FIELD))
    frby.append(text(627, 365, "НСД(f, v - s_i) ділиться на f_i(x)!", size=12, bold=True, color=POS))

    render(os.path.join(OUT, "berlekamp-isomorphism.svg"), W, H, *frby,
           title="Ізоморфізм Китайської теореми та структура підалгебри Берлекампа")


if __name__ == '__main__':
    fig_berlekamp_flow()
    fig_berlekamp_isomorphism()
    print("Згенеровано фігури в img/")
