# -*- coding: utf-8 -*-
"""Фігури до теми «Алгоритми підвищеної точності на базі FMA».
Запуск: python figs.py  -> створює SVG у теці ./img/
Стиль і помічники — зі спільного svgkit."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки
GOLD   = "#b9770e"
PALE_R = "#fdecea"
PALE_B = "#eaf0fd"
PALE_G = "#eaf7ee"
PALE_Y = "#fbf4e6"
PALE_V = "#f3e8fd"
PURPLE = "#7b2cbf"
CYAN   = "#0288d1"
PALE_C = "#e1f5fe"


# ── 1. Механізм Fast2Mult: видобування точного залишку множення ───────────────
def fig_fast2mult_mechanism():
    W, H = 840, 480
    f = []

    f.append(text(W / 2, 28, "Механізм точного розкладання добутку: алгоритм Fast2Mult на базі FMA", size=15, color=INK, bold=True))

    # Крок 1: Обчислення x = round(a * b)
    f.append(rect(40, 55, 360, 180, fill=PALE_B, stroke=NEG, rx=8))
    f.append(text(220, 78, "Крок 1: Старша частина x = round(a × b)", size=13, color=NEG, bold=True))
    f.append(rect(60, 95, 140, 32, fill=FILL, stroke=LINE, rx=4))
    f.append(text(130, 115, "Мантиса a (53 біти)", size=11, color=INK))
    f.append(rect(240, 95, 140, 32, fill=FILL, stroke=LINE, rx=4))
    f.append(text(310, 115, "Мантиса b (53 біти)", size=11, color=INK))

    f.append(arrow(130, 127, 190, 145, color=LINE))
    f.append(arrow(310, 127, 250, 145, color=LINE))

    f.append(rect(100, 145, 240, 32, fill=FILL, stroke=LINE, rx=4))
    f.append(text(220, 165, "Множення: 106 бітів у конвеєрі", size=11, color=INK, bold=True))

    f.append(arrow(220, 177, 220, 195, color=LINE))
    f.append(rect(80, 195, 280, 30, fill=PALE_R, stroke=POS, rx=4))
    f.append(text(220, 214, "Округлення IEEE 754 -> x (старші 53 біти)", size=11, color=POS, bold=True))

    # Крок 2: Обчислення y = fma(a, b, -x)
    f.append(rect(440, 55, 360, 180, fill=PALE_G, stroke=FIELD, rx=8))
    f.append(text(620, 78, "Крок 2: Точний залишок y = fma(a, b, -x)", size=13, color=FIELD, bold=True))

    f.append(rect(460, 95, 150, 32, fill=FILL, stroke=LINE, rx=4))
    f.append(text(535, 115, "Добуток a × b (106 бітів)", size=11, color=INK))
    f.append(rect(630, 95, 150, 32, fill=PALE_R, stroke=POS, rx=4))
    f.append(text(705, 115, "Віднімання -x (53 біти)", size=11, color=POS))

    f.append(arrow(535, 127, 590, 145, color=LINE))
    f.append(arrow(705, 127, 650, 145, color=LINE))

    f.append(rect(480, 145, 280, 32, fill=FILL, stroke=LINE, rx=4))
    f.append(text(620, 165, "Акумулятор FMA: точне скасування старших бітів", size=10, color=INK, bold=True))

    f.append(arrow(620, 177, 620, 195, color=LINE))
    f.append(rect(480, 195, 280, 30, fill=PALE_G, stroke=FIELD, rx=4))
    f.append(text(620, 214, "Результат y: рівно молодші 53 біти (без похибки!)", size=11, color=FIELD, bold=True))

    # Нижня частина: Бітова розкладка
    f.append(rect(40, 255, 760, 200, fill=FILL, stroke=LINE, rx=8))
    f.append(text(W / 2, 280, "Анатомія розрядної сітки: точний зв'язок a × b = x + y", size=13, color=INK, bold=True))

    # Лінійка розрядів 106 бітів
    f.append(rect(70, 305, 340, 38, fill=PALE_R, stroke=POS, rx=4))
    f.append(text(240, 328, "Старша частина: число x (53 біти)", size=11, color=POS, bold=True))

    f.append(rect(410, 305, 350, 38, fill=PALE_G, stroke=FIELD, rx=4))
    f.append(text(585, 328, "Молодший хвіст: залишок y (≤ 53 біти)", size=11, color=FIELD, bold=True))

    # Стрілки та підписи розрядів
    f.append(line(70, 350, 760, 350, color=LINE, sw=1.2))
    f.append(text(70, 368, "Біт 106 (MSB)", size=10, color=MUTED, anchor="start"))
    f.append(text(410, 368, "Біт 53 (Межа ULP(x))", size=10, color=MUTED, anchor="middle"))
    f.append(text(760, 368, "Біт 1 (LSB)", size=10, color=MUTED, anchor="end"))

    # Пояснення безпомилковості
    f.append(rect(70, 390, 690, 50, fill=PALE_Y, stroke=GOLD, rx=6))
    f.append(text(W / 2, 412, "Чому FMA не створює другої похибки: віднімання -x відбувається всередині широкого акумулятора FMA.", size=10, color=INK))
    f.append(text(W / 2, 428, "Старші 53 біти взаємно знищуються, а залишок y займає не більше 53 бітів, тому вкладається у double абсолютно точно.", size=10, color=INK, bold=True))

    render(os.path.join(IMG, "fast2mult-mechanism.svg"), W, H, *f)


# ── 2. Структура представлення Double-Double ─────────────────────────────────
def fig_double_double_layout():
    W, H = 840, 420
    f = []

    f.append(text(W / 2, 28, "Формат подвійної точності Double-Double: пара (hi, lo)", size=15, color=INK, bold=True))

    # Контейнер для числа hi
    f.append(rect(50, 60, 740, 110, fill=PALE_B, stroke=NEG, rx=8))
    f.append(text(120, 85, "Старше число: x.hi", size=13, color=NEG, bold=True))
    f.append(text(480, 85, "Стандартне число IEEE 754 binary64 (53 біти значущості)", size=11, color=MUTED))

    # Складові x.hi: знак, порядок, мантиса
    f.append(rect(70, 105, 45, 45, fill=PALE_R, stroke=POS, rx=4))
    f.append(text(92, 132, "s", size=12, color=POS, bold=True))
    f.append(rect(120, 105, 130, 45, fill=PALE_Y, stroke=GOLD, rx=4))
    f.append(text(185, 132, "Порядок (11 бітів)", size=11, color=GOLD, bold=True))
    f.append(rect(255, 105, 510, 45, fill=PALE_G, stroke=FIELD, rx=4))
    f.append(text(510, 132, "Старша мантиса hi: 53 біти точності (включно з неявною 1)", size=11, color=FIELD, bold=True))

    # Стрілка неперекриття
    f.append(line(420, 180, 420, 220, color=LINE, sw=1.5, dash="4,4"))
    f.append(rect(270, 190, 300, 26, fill=PALE_Y, stroke=GOLD, rx=4))
    f.append(text(420, 207, "Умова неперекриття: |x.lo| ≤ 0.5 × ULP(x.hi)", size=11, color=INK, bold=True))

    # Контейнер для числа lo
    f.append(rect(50, 230, 740, 110, fill=PALE_C, stroke=CYAN, rx=8))
    f.append(text(120, 255, "Молодше число: x.lo", size=13, color=CYAN, bold=True))
    f.append(text(480, 255, "Зміщене за порядком коригувальне число IEEE 754 binary64", size=11, color=MUTED))

    # Складові x.lo
    f.append(rect(70, 275, 45, 45, fill=PALE_R, stroke=POS, rx=4))
    f.append(text(92, 302, "s", size=12, color=POS, bold=True))
    f.append(rect(120, 275, 130, 45, fill=PALE_Y, stroke=GOLD, rx=4))
    f.append(text(185, 302, "Порядок (≤ exp_hi − 53)", size=10, color=GOLD, bold=True))
    f.append(rect(255, 275, 510, 45, fill=PALE_G, stroke=FIELD, rx=4))
    f.append(text(510, 302, "Молодша мантиса lo: додаткові 53 біти точності", size=11, color=FIELD, bold=True))

    # Підсумок
    f.append(rect(50, 355, 740, 45, fill=FILL, stroke=LINE, rx=6))
    f.append(text(W / 2, 382, "Сумарна ефективна мантиса: 106 бітів (~31-32 десяткові знаки) при апаратному динамічному діапазоні double", size=11, color=INK, bold=True))

    render(os.path.join(IMG, "double-double-layout.svg"), W, H, *f)


# ── 3. Компенсована схема Горнера ────────────────────────────────────────────
def fig_compensated_horner_flow():
    W, H = 840, 480
    f = []

    f.append(text(W / 2, 28, "Компенсована схема Горнера: паралельне відстеження полінома та похибок", size=15, color=INK, bold=True))

    # Класична гілка (вгорі)
    f.append(rect(40, 55, 760, 115, fill=PALE_B, stroke=NEG, rx=8))
    f.append(text(210, 78, "Основна обчислювальна лінія: sᵢ = sᵢ₋₁ × x + aᵢ", size=13, color=NEG, bold=True))

    f.append(rect(60, 95, 140, 36, fill=FILL, stroke=LINE, rx=4))
    f.append(text(130, 117, "Попереднє sᵢ₋₁", size=11, color=INK))

    f.append(arrow(200, 113, 240, 113, color=LINE))
    f.append(rect(240, 95, 170, 36, fill=PALE_Y, stroke=GOLD, rx=4))
    f.append(text(325, 117, "TwoProductFMA(sᵢ₋₁, x)", size=11, color=GOLD, bold=True))

    f.append(arrow(410, 113, 450, 113, color=LINE))
    f.append(rect(450, 95, 160, 36, fill=PALE_Y, stroke=GOLD, rx=4))
    f.append(text(530, 117, "TwoSum(pᵢ, aᵢ)", size=11, color=GOLD, bold=True))

    f.append(arrow(610, 113, 650, 113, color=LINE))
    f.append(rect(650, 95, 130, 36, fill=PALE_B, stroke=NEG, rx=4))
    f.append(text(715, 117, "Нове значення sᵢ", size=11, color=NEG, bold=True))

    # Стрілки похибок у проміжку
    f.append(arrow(325, 131, 325, 230, color=POS))
    f.append(arrow(530, 131, 530, 230, color=POS))
    f.append(rect(335, 170, 140, 26, fill=PALE_R, stroke=POS, rx=4))
    f.append(text(405, 187, "Похибка множення πᵢ", size=10, color=POS, bold=True))
    f.append(rect(540, 170, 140, 26, fill=PALE_R, stroke=POS, rx=4))
    f.append(text(610, 187, "Похибка додавання σᵢ", size=10, color=POS, bold=True))

    # Компенсаційна гілка (внизу)
    f.append(rect(40, 230, 760, 135, fill=PALE_G, stroke=FIELD, rx=8))
    f.append(text(230, 253, "Лінія компенсації: P_err(x) = ∑ (πᵢ + σᵢ) × xⁿ⁻ⁱ", size=13, color=FIELD, bold=True))

    f.append(rect(60, 275, 170, 36, fill=FILL, stroke=LINE, rx=4))
    f.append(text(145, 297, "Поточна похибка eᵢ₋₁", size=11, color=INK))

    f.append(arrow(230, 293, 270, 293, color=LINE))
    f.append(rect(270, 275, 310, 36, fill=PALE_G, stroke=FIELD, rx=4))
    f.append(text(425, 297, "Акумуляція похибки: eᵢ = fma(eᵢ₋₁, x, πᵢ + σᵢ)", size=11, color=FIELD, bold=True))

    f.append(arrow(580, 293, 620, 293, color=LINE))
    f.append(rect(620, 275, 160, 36, fill=PALE_G, stroke=FIELD, rx=4))
    f.append(text(700, 297, "Акумульована eᵢ", size=11, color=FIELD, bold=True))

    f.append(text(420, 345, "Оновлення полінома похибок виконується однією інструкцією FMA без розширених типів", size=11, color=MUTED))

    # Фінальне об'єднання
    f.append(rect(40, 385, 760, 65, fill=PALE_Y, stroke=GOLD, rx=6))
    f.append(text(W / 2, 410, "Фінальний результат: res = s_n + e_n (додавання накопиченого виправлення)", size=12, color=INK, bold=True))
    f.append(text(W / 2, 432, "Точність подвоюється: результат еквівалентний обчисленню в quad precision з подальшим округленням до double", size=10, color=GOLD, bold=True))

    render(os.path.join(IMG, "compensated-horner-flow.svg"), W, H, *f)


# ── 4. Скорочення похибки в детермінанті Кахана ───────────────────────────────
def fig_kahan_det_cancellation():
    W, H = 840, 440
    f = []

    f.append(text(W / 2, 28, "Катастрофічне скасування та алгоритм Вільяма Кахана для det = ad − bc", size=15, color=INK, bold=True))

    # Ліва колонка: Наївне обчислення
    f.append(rect(40, 55, 360, 320, fill=PALE_R, stroke=POS, rx=8))
    f.append(text(220, 80, "Наївний підхід: (a × d) − (b × c)", size=13, color=POS, bold=True))

    f.append(rect(60, 100, 320, 32, fill=FILL, stroke=LINE, rx=4))
    f.append(text(220, 120, "p = round(a × d) [округлення 1]", size=11, color=INK))

    f.append(rect(60, 145, 320, 32, fill=FILL, stroke=LINE, rx=4))
    f.append(text(220, 165, "q = round(b × c) [округлення 2]", size=11, color=INK))

    f.append(arrow(220, 177, 220, 200, color=LINE))

    f.append(rect(60, 200, 320, 55, fill=PALE_R, stroke=POS, rx=4))
    f.append(text(220, 222, "Віднімання p − q при p ≈ q", size=11, color=POS, bold=True))
    f.append(text(220, 242, "Катастрофічне скасування розрядів!", size=10, color=POS))

    f.append(arrow(220, 255, 220, 280, color=LINE))

    f.append(rect(60, 280, 320, 75, fill=FILL, stroke=LINE, rx=4))
    f.append(text(220, 302, "Старші 50 бітів збігаються і зникають.", size=10, color=INK))
    f.append(text(220, 322, "У результаті лишається 3 біти шуму.", size=10, color=POS, bold=True))
    f.append(text(220, 342, "Відносна похибка: до 100% (або хибний знак)", size=10, color=POS, bold=True))

    # Права колонка: Алгоритм Кахана з FMA
    f.append(rect(440, 55, 360, 320, fill=PALE_G, stroke=FIELD, rx=8))
    f.append(text(620, 80, "Алгоритм Кахана на базі FMA", size=13, color=FIELD, bold=True))

    f.append(rect(460, 100, 320, 32, fill=FILL, stroke=LINE, rx=4))
    f.append(text(620, 120, "1. w = b × c", size=11, color=INK))

    f.append(rect(460, 145, 320, 32, fill=PALE_Y, stroke=GOLD, rx=4))
    f.append(text(620, 165, "2. e = fma(-b, c, w)  [точна похибка w]", size=11, color=GOLD, bold=True))

    f.append(arrow(620, 177, 620, 200, color=LINE))

    f.append(rect(460, 200, 320, 55, fill=PALE_G, stroke=FIELD, rx=4))
    f.append(text(620, 222, "3. d = fma(a, d, -w)  [різниця у 106 бітах]", size=11, color=FIELD, bold=True))
    f.append(text(620, 242, "4. det = d + e        [додавання похибки]", size=11, color=FIELD, bold=True))

    f.append(arrow(620, 255, 620, 280, color=LINE))

    f.append(rect(460, 280, 320, 75, fill=FILL, stroke=LINE, rx=4))
    f.append(text(620, 302, "FMA утримує 106 бітів різниці a·d − w.", size=10, color=INK))
    f.append(text(620, 322, "Похибка e компенсує залишок округлення w.", size=10, color=FIELD, bold=True))
    f.append(text(620, 342, "Гарантована похибка: ≤ 1.5 ULP!", size=11, color=FIELD, bold=True))

    # Нижній підсумок
    f.append(rect(40, 385, 760, 42, fill=FILL, stroke=LINE, rx=6))
    f.append(text(W / 2, 410, "Алгоритм Кахана гарантує високу відносну точність навіть при майже повному збігу добутків", size=11, color=INK, bold=True))

    render(os.path.join(IMG, "kahan-det-cancellation.svg"), W, H, *f)


# ── 5. Пропускна здатність конвеєра FMA та розгортання циклів ────────────────
def fig_fma_pipeline_throughput():
    W, H = 840, 450
    f = []

    f.append(text(W / 2, 28, "Мікроархітектура FMA: затримка (Latency) проти пропускної здатності (Throughput)", size=15, color=INK, bold=True))

    # Ліва колонка: Послідовна залежність
    f.append(rect(40, 55, 360, 260, fill=PALE_R, stroke=POS, rx=8))
    f.append(text(220, 80, "Послідовний ланцюг (1 акумулятор)", size=13, color=POS, bold=True))
    f.append(text(220, 100, "acc = fma(x[i], y[i], acc)", size=11, color=MUTED))

    # Таблиця тактів
    y0 = 115
    for t in range(4):
        f.append(rect(60, y0 + t * 34, 60, 28, fill=FILL, stroke=LINE, rx=3))
        f.append(text(90, y0 + t * 34 + 18, "Такт %d" % (t + 1), size=10, color=MUTED))
        f.append(rect(125, y0 + t * 34, 255, 28, fill=PALE_R if t > 0 else PALE_Y, stroke=POS if t > 0 else GOLD, rx=3))
        f.append(text(252, y0 + t * 34 + 18, "FMA 1 (стадія %d/4, конвеєр зайнято)" % (t + 1) if t == 0 else "Очікування результату FMA 1 (простій!)", size=10, color=POS if t > 0 else GOLD))

    f.append(rect(60, 260, 320, 42, fill=FILL, stroke=LINE, rx=4))
    f.append(text(220, 278, "Затримка: 4 такти на ітерацію", size=10, color=POS, bold=True))
    f.append(text(220, 294, "Утилізація FPU: лише 25% від максимуму!", size=10, color=POS))

    # Права колонка: 4 паралельні акумулятори
    f.append(rect(440, 55, 360, 260, fill=PALE_G, stroke=FIELD, rx=8))
    f.append(text(620, 80, "Розгорнутий конвеєр (4 акумулятори)", size=13, color=FIELD, bold=True))
    f.append(text(620, 100, "acc0..acc3 = fma(x[i+k], y[i+k], accK)", size=11, color=MUTED))

    # Таблиця тактів
    y0 = 115
    labels = ["FMA(acc0)", "FMA(acc1)", "FMA(acc2)", "FMA(acc3)"]
    for t in range(4):
        f.append(rect(460, y0 + t * 34, 60, 28, fill=FILL, stroke=LINE, rx=3))
        f.append(text(490, y0 + t * 34 + 18, "Такт %d" % (t + 1), size=10, color=MUTED))
        f.append(rect(525, y0 + t * 34, 255, 28, fill=PALE_G, stroke=FIELD, rx=3))
        f.append(text(652, y0 + t * 34 + 18, "%s запускається на порту 0/1" % labels[t], size=10, color=FIELD, bold=True))

    f.append(rect(460, 260, 320, 42, fill=FILL, stroke=LINE, rx=4))
    f.append(text(620, 278, "Пропускна здатність: 1 FMA кожен такт (або 2 на Zen/Skylake)", size=10, color=FIELD, bold=True))
    f.append(text(620, 294, "Утилізація FPU: 100% (повне насичення конвеєра)", size=10, color=FIELD))

    # Нижня діаграма: Виконавчі порти сучасного процесора
    f.append(rect(40, 325, 760, 110, fill=FILL, stroke=LINE, rx=8))
    f.append(text(W / 2, 348, "Архітектура портів виконання x86-64 / ARM (Intel Golden Cove, AMD Zen 4/5, Apple M-серія)", size=12, color=INK, bold=True))

    f.append(rect(60, 365, 340, 55, fill=PALE_C, stroke=CYAN, rx=6))
    f.append(text(230, 388, "Порт виконання 0: 512-бітний FMA конвеєр", size=11, color=CYAN, bold=True))
    f.append(text(230, 406, "Здатність: 8 × double або 16 × float за такт", size=10, color=MUTED))

    f.append(rect(440, 365, 340, 55, fill=PALE_C, stroke=CYAN, rx=6))
    f.append(text(610, 388, "Порт виконання 1: 512-бітний FMA конвеєр", size=11, color=CYAN, bold=True))
    f.append(text(610, 406, "Здатність: 8 × double або 16 × float за такт", size=10, color=MUTED))

    render(os.path.join(IMG, "fma-pipeline-throughput.svg"), W, H, *f)


def main():
    fig_fast2mult_mechanism()
    fig_double_double_layout()
    fig_compensated_horner_flow()
    fig_kahan_det_cancellation()
    fig_fma_pipeline_throughput()
    print("Фігури успішно згенеровано у %s" % IMG)


if __name__ == "__main__":
    main()
