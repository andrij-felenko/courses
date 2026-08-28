# -*- coding: utf-8 -*-
"""Фігури для детальної статті 'Правило чи модель: коли навчання виправдане'.
Запуск із цієї теки: python figs.py
Виводить SVG у ./img/. Імпортує спільний svgkit зі scripts/ (чотири рівні вгору)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# Палітра
DECISION_FILL = "#f0f4f8"
RULE_FILL     = "#e8f6ee"  # зелений — детермінізм
ML_FILL       = "#eaf0fd"  # синій — модель
HYBRID_FILL   = "#fef3d6"  # бурштиновий — гібрид
ALERT_FILL    = "#fdecea"  # червоний — загроза / блокування

# ── Фігура 1: Дерево прийняття інженерного рішення ──────────────────────────
def fig_decision_tree():
    W, H = 940, 560
    frags = []

    # Заголовок / Кореневий блок
    frags.append(fitbox(20, 20, 260, 60, "Вхідна інженерна задача:\nвибір архітектури керування",
                        size=14, bold=True, fill=FILL, stroke=LINE))

    # Стрілка від кореня до Q1
    frags.append(arrow(280, 50, 340, 50, color=LINE))

    # Q1: Фізична модель та розмірність
    frags.append(fitbox(340, 20, 280, 60, "1. Чи відома точна фізична модель\nабо аналітичні рівняння стану?",
                        size=13, fill=DECISION_FILL, stroke=LINE))

    # Q1 -> ТАК -> Правило / PID
    frags.append(arrow(480, 80, 480, 130, color=FIELD, sw=2))
    frags.append(text(495, 105, "Так", size=12, color=FIELD, bold=True, anchor="start"))
    frags.append(fitbox(340, 130, 280, 60, "Детерміноване правило / PID\n• Час O(1), доведена стійкість\n• Сертифікація DO-178C (DAL-A)",
                        size=12, fill=RULE_FILL, stroke=FIELD, sw=2))

    # Q1 -> НІ -> Q2
    frags.append(arrow(620, 50, 680, 50, color=POS, sw=2))
    frags.append(text(650, 40, "Ні", size=12, color=POS, bold=True, anchor="middle"))

    # Q2: Розмірність входу
    frags.append(fitbox(680, 20, 240, 60, "2. Яка розмірність входу?\nНизька (N ≤ 8) чи висока?",
                        size=13, fill=DECISION_FILL, stroke=LINE))

    # Q2 -> Низька -> Q3 (Таблиці / Евристики)
    frags.append(arrow(800, 80, 800, 130, color=LINE, sw=1.8))
    frags.append(text(810, 105, "Низька", size=12, color=INK, bold=True, anchor="start"))
    frags.append(fitbox(680, 130, 240, 60, "Таблиці пошуку (LUT) / FSM\n• Порогові дерева рішень\n• Нульовий дрейф у часі",
                        size=12, fill=RULE_FILL, stroke=FIELD, sw=1.8))

    # Q2 -> Висока -> Q4 (Датчики високої розмірності: камери, радар, спектр)
    frags.append(arrow(800, 190, 800, 240, color=LINE, sw=1.8))
    frags.append(text(810, 215, "Висока", size=12, color=INK, bold=True, anchor="start"))

    # Q4: Обчислювальний бюджет та дані
    frags.append(fitbox(660, 240, 260, 60, "3. Чи є бюджет пам'яті (NPU/FPU)\nта розмічений датасет?",
                        size=13, fill=DECISION_FILL, stroke=LINE))

    # Q4 -> НІ -> Спрощення датчиків
    frags.append(arrow(660, 270, 560, 270, color=POS, sw=1.8))
    frags.append(text(610, 260, "Ні", size=12, color=POS, bold=True, anchor="middle"))
    frags.append(fitbox(300, 240, 260, 60, "Спрощення сенсорики\n• Заміна камери на ToF/sonar\n• Перехід до простих правил",
                        size=12, fill=ALERT_FILL, stroke=POS, sw=1.8))

    # Q4 -> ТАК -> Q5
    frags.append(arrow(790, 300, 790, 350, color=FIELD, sw=2))
    frags.append(text(805, 325, "Так", size=12, color=FIELD, bold=True, anchor="start"))

    # Q5: Ціна помилки та безпека
    frags.append(fitbox(660, 350, 260, 60, "4. Чи є ризик для життя,\nобладнання або катастрофи?",
                        size=13, fill=DECISION_FILL, stroke=LINE))

    # Q5 -> НІ -> Чистий ML
    frags.append(arrow(660, 380, 560, 380, color=MUTED, sw=1.8))
    frags.append(text(610, 370, "Ні", size=12, color=MUTED, bold=True, anchor="middle"))
    frags.append(fitbox(280, 350, 280, 60, "Автономна модель (Чистий ML)\n• Ендпоінт без верифікатора\n• Фокус на середній точності",
                        size=12, fill=ML_FILL, stroke=NEG, sw=2))

    # Q5 -> ТАК -> Гібрид (ML + Детермінований бар'єр)
    frags.append(arrow(790, 410, 790, 460, color=POS, sw=2))
    frags.append(text(805, 435, "Так", size=12, color=POS, bold=True, anchor="start"))
    frags.append(fitbox(520, 460, 400, 75, "Гібридний Simplex-селектор (ML + Правило)\n• Нейромережа генерує пропозицію керування (Proposer)\n• Детермінований фільтр (Safety Barrier) блокує порушення меж\n• Миттєве перемикання на резервне правило (Fallback)",
                        size=12, fill=HYBRID_FILL, stroke="#d97706", sw=2, bold=True))

    render(os.path.join(IMG, 'decision-tree-rule-vs-ml.svg'), W, H, *frags,
           title="Дерево прийняття інженерного рішення: правило чи машинне навчання")


# ── Фігура 2: Архітектура гібридного селектора з бар'єром безпеки ───────────
def fig_hybrid_safety_barrier():
    W, H = 940, 540
    frags = []

    # Вхідний потік сенсорів (ліворуч)
    frags.append(fitbox(20, 180, 180, 100, "Сенсорна телеметрія\n(x_t ∈ R^N)\n• Камери, IMU, лідар\n• Струм, напруга, одометрія",
                        size=12, fill=FILL, stroke=LINE))

    # Розгалуження входу: лінії з кутовими переходами без накладання на текст
    # До верхньої гілки (ML)
    frags.append(line(200, 210, 225, 210, color=LINE, sw=1.8))
    frags.append(line(225, 210, 225, 110, color=LINE, sw=1.8))
    frags.append(arrow(225, 110, 260, 110, color=LINE, sw=1.8))
    frags.append(text(210, 95, "Кадри/хмари точок", size=11, color=MUTED, anchor="start"))

    # До нижньої гілки (Правила)
    frags.append(line(200, 250, 225, 250, color=LINE, sw=1.8))
    frags.append(line(225, 250, 225, 360, color=LINE, sw=1.8))
    frags.append(arrow(225, 360, 260, 360, color=LINE, sw=1.8))
    frags.append(text(210, 385, "Ознаки стану", size=11, color=MUTED, anchor="start"))

    # Верхня гілка: Нейромережевий оптимізатор (Proposer)
    frags.append(rect(260, 50, 300, 130, fill=ML_FILL, stroke=NEG, sw=2, rx=8))
    frags.append(text(410, 80, "Нейромережевий планувальник", size=14, bold=True, color=NEG))
    frags.append(text(410, 105, "• Квантована INT8 CNN / Transformer", size=12, color=INK))
    frags.append(text(410, 125, "• Оцінка оптимальної траєкторії u_ml", size=12, color=INK))
    frags.append(text(410, 145, "• Евристична генерація пропозиції", size=12, color=MUTED))

    # Нижня гілка: Резервне правило (Fail-safe Rule / Backup Controller)
    frags.append(rect(260, 300, 300, 130, fill=RULE_FILL, stroke=FIELD, sw=2, rx=8))
    frags.append(text(410, 330, "Резервний детермінований контролер", size=14, bold=True, color=FIELD))
    frags.append(text(410, 355, "• Фізичний PID / Гальмування / Зависання", size=12, color=INK))
    frags.append(text(410, 375, "• Розрахунок безпечної дії u_safe", size=12, color=INK))
    frags.append(text(410, 395, "• Доведена стабільність за Ляпуновим", size=12, color=MUTED))

    # З'єднання від блоків до Селектора / Бар'єра
    # Від ML
    frags.append(line(560, 115, 595, 115, color=NEG, sw=2))
    frags.append(line(595, 115, 595, 200, color=NEG, sw=2))
    frags.append(arrow(595, 200, 630, 200, color=NEG, sw=2))
    frags.append(text(575, 98, "Пропозиція u_ml", size=11, color=NEG, bold=True, anchor="start"))

    # Від Правила
    frags.append(line(560, 365, 595, 365, color=FIELD, sw=2))
    frags.append(line(595, 365, 595, 290, color=FIELD, sw=2))
    frags.append(arrow(595, 290, 630, 290, color=FIELD, sw=2))
    frags.append(text(575, 385, "Резерв u_safe", size=11, color=FIELD, bold=True, anchor="start"))

    # Центральний блок: Детермінований бар'єр безпеки (Safety Barrier / Simplex Arbiter)
    frags.append(rect(630, 140, 290, 210, fill=HYBRID_FILL, stroke="#d97706", sw=2.2, rx=10))
    frags.append(text(775, 170, "Детермінований бар'єр безпеки", size=14, bold=True, color="#92400e"))
    frags.append(line(645, 185, 905, 185, color="#d97706", sw=1.2))
    frags.append(text(775, 205, "1. Перевірка інваріантів стану (h(x) ≥ 0)", size=12, color=INK))
    frags.append(text(775, 225, "2. Контроль меж прискорень і струмів", size=12, color=INK))
    frags.append(text(775, 245, "3. Детекція дрейфу (Out-of-Distribution)", size=12, color=INK))
    frags.append(text(775, 265, "4. Тайм-аут інференсу (WCET < 5 мс)", size=12, color=INK))
    frags.append(text(775, 310, "Селектор: u_out = Safe(u_ml) ? u_ml : u_safe", size=11, color=POS, bold=True))

    # Вихід на актуатори (донизу)
    frags.append(arrow(775, 350, 775, 430, color=FIELD, sw=2.5))
    frags.append(fitbox(660, 430, 230, 60, "Верифікована дія u_out\nВидача на актуатори / ШІМ",
                        size=13, fill="#ffffff", stroke=FIELD, sw=2, bold=True))

    # Діагностична телеметрія (помилки, OOD, перехоплення керування)
    frags.append(arrow(920, 245, 935, 245, color=POS, sw=1.5))
    frags.append(text(925, 230, "Аварійний лог", size=10, color=POS, anchor="end"))

    render(os.path.join(IMG, 'hybrid-safety-barrier.svg'), W, H, *frags,
           title="Архітектура гібридного селектора з детермінованим бар'єром безпеки")


if __name__ == '__main__':
    fig_decision_tree()
    fig_hybrid_safety_barrier()
    print("Фігури успішно згенеровано у ./img/")
