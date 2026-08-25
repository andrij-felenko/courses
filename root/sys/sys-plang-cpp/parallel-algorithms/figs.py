# -*- coding: utf-8 -*-
"""Фігури до теми «Політики виконання й паралельні алгоритми»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Порівняння політик виконання за потоками й векторними лініями ──────────
def fig_execution_policies():
    W, H = 960, 520
    f = []

    f.append(text(480, 28, "Моделі виконання стандартних алгоритмів: потоки та чергування інструкцій", size=16, color=INK, anchor="middle", bold=True))

    # Стовпчик 1: seq
    f.append(fitbox(30, 60, 210, 50, "std::execution::seq\n(Послідовна політика)", size=13, fill="#f4f6f8", stroke=LINE, bold=True))
    f.append(fitbox(30, 120, 210, 260, "• 1 системний потік (T0)\n• Послідовний порядок\n• Немає чергування\n• Повна детермінованість\n• Дозволені будь-які блокування\n• Дозволене виділення пам'яті\n• Винятки розгортають стек", size=11, fill="#ffffff", stroke=MUTED))
    # Схематичний стек викликів
    f.append(fitbox(45, 395, 180, 28, "Крок 1: e[0] -> e[1] -> e[2]", size=10, fill="#e8f4fc", stroke=NEG))
    f.append(fitbox(45, 430, 180, 28, "Крок 2: e[3] -> e[4] -> e[5]", size=10, fill="#e8f4fc", stroke=NEG))
    f.append(fitbox(45, 465, 180, 28, "T0: строго послідовно", size=10, fill="#f4f6f8", stroke=MUTED, bold=True))

    # Стовпчик 2: par
    f.append(fitbox(260, 60, 210, 50, "std::execution::par\n(Багатопотокова паралельна)", size=13, fill="#e8f4fc", stroke=NEG, bold=True))
    f.append(fitbox(260, 120, 210, 260, "• N потоків (T0, T1, T2...)\n• Невизначений порядок між T[i]\n• У межах T[i] послідовно\n• Потрібен захист від Data Race\n• М'ютекси/lock_guard дозволені\n• Атоміки дозволені\n• Виняток -> std::terminate()", size=11, fill="#ffffff", stroke=NEG))
    f.append(fitbox(275, 395, 85, 28, "T0: e[0..k]", size=10, fill="#e8f4fc", stroke=NEG))
    f.append(fitbox(370, 395, 85, 28, "T1: e[k..2k]", size=10, fill="#e8f4fc", stroke=NEG))
    f.append(fitbox(275, 430, 85, 28, "T2: e[2k..3k]", size=10, fill="#e8f4fc", stroke=NEG))
    f.append(fitbox(370, 430, 85, 28, "T3: e[3k..N]", size=10, fill="#e8f4fc", stroke=NEG))
    f.append(fitbox(275, 465, 180, 28, "Паралельні потоки пулу", size=10, fill="#e8f4fc", stroke=NEG, bold=True))

    # Стовпчик 3: par_unseq
    f.append(fitbox(490, 60, 210, 50, "std::execution::par_unseq\n(Паралельна векторизована)", size=13, fill="#fff0f0", stroke=POS, bold=True))
    f.append(fitbox(490, 120, 210, 260, "• N потоків + SIMD-векторизація\n• Чергування між лініями SIMD\n• Заборона м'ютексів (дедлок!)\n• Заборона new/malloc\n• Заборона atomic::wait\n• Лише lock-free обчислення\n• Виняток -> std::terminate()", size=11, fill="#ffffff", stroke=POS))
    f.append(fitbox(505, 395, 85, 28, "T0 SIMD 0..3", size=10, fill="#fff0f0", stroke=POS))
    f.append(fitbox(600, 395, 85, 28, "T0 SIMD 4..7", size=10, fill="#fff0f0", stroke=POS))
    f.append(fitbox(505, 430, 85, 28, "T1 SIMD 0..3", size=10, fill="#fff0f0", stroke=POS))
    f.append(fitbox(600, 430, 85, 28, "T1 SIMD 4..7", size=10, fill="#fff0f0", stroke=POS))
    f.append(fitbox(505, 465, 180, 28, "Потоки + SIMD-регістри", size=10, fill="#fff0f0", stroke=POS, bold=True))

    # Стовпчик 4: unseq (C++20)
    f.append(fitbox(720, 60, 210, 50, "std::execution::unseq\n(Векторизована C++20)", size=13, fill="#e8f6ee", stroke=FIELD, bold=True))
    f.append(fitbox(720, 120, 210, 260, "• 1 потік + SIMD-векторизація\n• Без накладних витрат пулу\n• Чергування в 1 потоці\n• Заборона блокуючих викликів\n• Ідеально для чистої математики\n• Пряме відображення в AVX/NEON\n• Виняток -> std::terminate()", size=11, fill="#ffffff", stroke=FIELD))
    f.append(fitbox(735, 395, 180, 28, "T0 Вектор 1: e[0..3] (AVX)", size=10, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(735, 430, 180, 28, "T0 Вектор 2: e[4..7] (AVX)", size=10, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(735, 465, 180, 28, "1 потік + SIMD-векторизація", size=10, fill="#e8f6ee", stroke=FIELD, bold=True))

    render(os.path.join(OUT, 'execution-policies-interleaving.svg'), W, H, *f, title="Політики виконання та моделі чергування")


# ── 2. Дерево паралельної редукції: std::reduce vs std::accumulate ───────────
def fig_reduction_tree():
    W, H = 960, 480
    f = []

    f.append(text(480, 28, "Паралельна редукція std::reduce проти лінійного згортання std::accumulate", size=16, color=INK, anchor="middle", bold=True))

    # Ліва частина: std::accumulate (строго лінійне O(N))
    f.append(fitbox(40, 60, 380, 45, "std::accumulate (C++98): Лінійне згортання\nСтрогий лівий порядок: (((init + a) + b) + c)...", size=12, fill="#f4f6f8", stroke=LINE, bold=True))

    # Ланцюжок акумуляції
    elements = ["init", "x[0]", "x[1]", "x[2]", "x[3]"]
    for i, el in enumerate(elements):
        f.append(fitbox(50 + i * 70, 130, 60, 35, el, size=11, fill="#e8f4fc", stroke=NEG))

    f.append(arrow(80, 165, 115, 205, color=LINE, sw=1.5))
    f.append(arrow(150, 165, 115, 205, color=LINE, sw=1.5))
    f.append(fitbox(80, 205, 70, 35, "s1 = i+x0", size=10, fill="#f4f6f8", stroke=LINE))

    f.append(arrow(115, 240, 185, 275, color=LINE, sw=1.5))
    f.append(arrow(220, 165, 185, 275, color=LINE, sw=1.5))
    f.append(fitbox(150, 275, 70, 35, "s2 = s1+x1", size=10, fill="#f4f6f8", stroke=LINE))

    f.append(arrow(185, 310, 255, 345, color=LINE, sw=1.5))
    f.append(arrow(290, 165, 255, 345, color=LINE, sw=1.5))
    f.append(fitbox(220, 345, 70, 35, "s3 = s2+x2", size=10, fill="#f4f6f8", stroke=LINE))

    f.append(arrow(255, 380, 325, 415, color=LINE, sw=1.5))
    f.append(arrow(360, 165, 325, 415, color=LINE, sw=1.5))
    f.append(fitbox(290, 415, 80, 35, "Результат", size=11, fill="#fff0f0", stroke=POS, bold=True))

    f.append(fitbox(40, 415, 230, 45, "Глибина залежності: O(N)\nНеможливо розпаралелити!", size=11, fill="#fff0f0", stroke=POS))

    # Права частина: std::reduce (паралельне дерево O(log N))
    f.append(fitbox(480, 60, 440, 45, "std::reduce (C++17): Деревоподібна редукція\nВимагає асоціативності та комутативності операції", size=12, fill="#e8f6ee", stroke=FIELD, bold=True))

    # Рівень 0: Вхідні елементи
    leaves = ["x[0]", "x[1]", "x[2]", "x[3]", "x[4]", "x[5]", "x[6]", "x[7]"]
    for i, el in enumerate(leaves):
        f.append(fitbox(490 + i * 53, 130, 46, 35, el, size=11, fill="#e8f4fc", stroke=NEG))

    # Рівень 1: Попарні суми (4 потоки/SIMD)
    for i in range(4):
        x_left = 490 + (i * 2) * 53 + 23
        x_right = 490 + (i * 2 + 1) * 53 + 23
        cx = (x_left + x_right) / 2
        f.append(arrow(x_left, 165, cx, 205, color=FIELD, sw=1.5))
        f.append(arrow(x_right, 165, cx, 205, color=FIELD, sw=1.5))
        f.append(fitbox(cx - 35, 205, 70, 35, f"p[{i}]", size=10, fill="#e8f6ee", stroke=FIELD))

    # Рівень 2: 2 суми
    for i in range(2):
        x_left = 513 + (i * 2) * 106 + 30
        x_right = 513 + (i * 2 + 1) * 106 + 30
        cx = (x_left + x_right) / 2
        f.append(arrow(x_left, 240, cx, 280, color=FIELD, sw=1.5))
        f.append(arrow(x_right, 240, cx, 280, color=FIELD, sw=1.5))
        f.append(fitbox(cx - 40, 280, 80, 35, f"q[{i}]", size=10, fill="#e8f6ee", stroke=FIELD))

    # Рівень 3: Фінальна редукція
    f.append(arrow(596, 315, 702, 355, color=FIELD, sw=1.8))
    f.append(arrow(808, 315, 702, 355, color=FIELD, sw=1.8))
    f.append(fitbox(642, 355, 120, 35, "Загальна сума", size=11, fill="#e8f6ee", stroke=FIELD, bold=True))

    f.append(fitbox(480, 415, 440, 45, "Глибина обчислень: O(log₂ N) замість O(N)\nЕфективне завантаження всіх ядер CPU / потоків GPU", size=11, fill="#e8f6ee", stroke=FIELD))

    render(os.path.join(OUT, 'reduction-tree.svg'), W, H, *f, title="Деревоподібна паралельна редукція проти лінійного згортання")


# ── 3. Префіксне сканування: inclusive_scan vs exclusive_scan ─────────────────
def fig_inclusive_exclusive_scan():
    W, H = 960, 460
    f = []

    f.append(text(480, 28, "Паралельне префіксне сканування: inclusive_scan та exclusive_scan", size=16, color=INK, anchor="middle", bold=True))

    # Вхідний масив
    f.append(fitbox(40, 60, 160, 45, "Вхідний масив X\n(N елементів)", size=12, fill="#f4f6f8", stroke=LINE, bold=True))
    inp = ["3", "1", "7", "0", "4", "2"]
    for i, val in enumerate(inp):
        f.append(fitbox(230 + i * 115, 60, 85, 45, f"x[{i}] = {val}", size=12, fill="#e8f4fc", stroke=NEG))

    # std::inclusive_scan
    f.append(fitbox(40, 160, 160, 80, "std::inclusive_scan\n\nВключає поточний\nelem y[i] = Σ(0..i)", size=11, fill="#e8f6ee", stroke=FIELD, bold=True))
    inc_vals = ["3", "4", "11", "11", "15", "17"]
    inc_expr = ["3", "3+1", "4+7", "11+0", "11+4", "15+2"]
    for i, (val, expr) in enumerate(zip(inc_vals, inc_expr)):
        f.append(arrow(272 + i * 115, 105, 272 + i * 115, 160, color=FIELD, sw=1.5))
        f.append(fitbox(230 + i * 115, 160, 85, 80, f"y[{i}] = {val}\n\n({expr})", size=11, fill="#e8f6ee", stroke=FIELD))

    # std::exclusive_scan (з init = 0 або іншим значенням)
    f.append(fitbox(40, 290, 160, 80, "std::exclusive_scan\n(init = 0)\nВиключає поточний\ny[i] = init + Σ(0..i-1)", size=11, fill="#fff0f0", stroke=POS, bold=True))
    exc_vals = ["0", "3", "4", "11", "11", "15"]
    exc_expr = ["init", "0+3", "3+1", "4+7", "11+0", "11+4"]
    for i, (val, expr) in enumerate(zip(exc_vals, exc_expr)):
        f.append(arrow(272 + i * 115, 240, 272 + i * 115, 290, color=POS, sw=1.5))
        f.append(fitbox(230 + i * 115, 290, 85, 80, f"y[{i}] = {val}\n\n({expr})", size=11, fill="#fff0f0", stroke=POS))

    # Нижній пояснювальний блок
    f.append(fitbox(40, 395, 880, 45, "Алгоритм паралельного сканування (Blelloch / Kogge-Stone): 2 проходи (Up-Sweep редукція + Down-Sweep розподіл) за час O(log N)", size=11, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(OUT, 'inclusive-exclusive-scan.svg'), W, H, *f, title="Префіксне сканування: inclusive проти exclusive")


# ── 4. Небезпека блокувань у векторизованому коді (Vectorization Deadlock) ─────
def fig_vectorization_deadlock():
    W, H = 960, 440
    f = []

    f.append(text(480, 28, "Взаємне блокування (Deadlock) у векторизованому потоці par_unseq / unseq", size=16, color=INK, anchor="middle", bold=True))

    # Контекст
    f.append(fitbox(40, 60, 880, 45, "Один апаратний потік виконання CPU виконує векторну інструкцію над 4 лініями SIMD одночасно", size=12, fill="#f4f6f8", stroke=LINE))

    # 4 SIMD лінії в межах одного потоку
    lanes = [
        ("SIMD Лінія 0", "Захоплює std::mutex\n(успішно lock())", "#e8f6ee", FIELD),
        ("SIMD Лінія 1", "Намагається захопити\nтой самий mutex...", "#fff0f0", POS),
        ("SIMD Лінія 2", "Очікує завершення\nвекторного кроку", "#f4f6f8", MUTED),
        ("SIMD Лінія 3", "Очікує завершення\nвекторного кроку", "#f4f6f8", MUTED)
    ]

    for i, (title_text, desc, fill_c, stroke_c) in enumerate(lanes):
        f.append(fitbox(40 + i * 225, 125, 205, 90, f"{title_text}\n\n{desc}", size=11, fill=fill_c, stroke=stroke_c, bold=True))

    # Стрілка блокування
    f.append(arrow(367, 215, 367, 255, color=POS, sw=2))
    f.append(fitbox(150, 255, 660, 65, "КАТАСТРОФА: Потік призупиняється у mutex.lock() для Лінії 1!\n"
                                      "Оскільки це ТОЙ САМИЙ потік ОС, він не може продовжити виконання Лінії 0 і зробити unlock()!\n"
                                      "Потік назавжди блокує сам себе (Self-Deadlock)", size=12, fill="#fff0f0", stroke=POS, bold=True))

    # Висновок і правило
    f.append(fitbox(40, 345, 880, 70, "Золоте правило політик par_unseq та unseq:\n"
                                      "У тілі лямбди КАТЕГОРИЧНО ЗАБОРОНЕНО використовувати м'ютекси, блокуючі атоміки, динамічне виділення пам'яті (malloc/new) та виклики не-reentrant функцій. Код мусить бути строго Vectorization-Safe!", size=11, fill="#e8f6ee", stroke=FIELD))

    render(os.path.join(OUT, 'vectorization-deadlock.svg'), W, H, *f, title="Небезпека дедлоку при векторизації")


def main():
    fig_execution_policies()
    fig_reduction_tree()
    fig_inclusive_exclusive_scan()
    fig_vectorization_deadlock()
    print("Усі 4 фігури успішно згенеровано у", OUT)


if __name__ == '__main__':
    main()
