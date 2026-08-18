# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"
BG      = "#ffffff"
INK     = "#111827"
POS     = "#15803d"
NEG     = "#b91c1c"
FIELD   = "#1e40af"


def fig_four_price_tags():
    """Чотири цінники кожного архітектурного вибору: CapEx, OpEx, Change Cost, Exit Cost."""
    W, H = 960, 420
    f = []

    # Блок 1: CapEx (Вартість побудови)
    f.append(fitbox(40, 60, 410, 140, "1. CapEx — Вартість побудови (Build Cost)\n• Проєктування та прототипування\n• Написання первинного коду й тестів\n• Навчання команди та первинне налаштування\n• Час до виходу на ринок (Time-to-Market)", size=13, fill=BLUE_T, stroke=FIELD))

    # Блок 2: OpEx (Вартість експлуатації)
    f.append(fitbox(510, 60, 410, 140, "2. OpEx — Вартість володіння (Run Cost)\n• Рахунки за хмару (vCPU, RAM, Storage, Egress)\n• Ліцензії SaaS/PaaS сервісів\n• Оперативне навантаження на чергових (On-call)\n• Технічне обслуговування й інциденти", size=13, fill=AMBER_T, stroke=AMBER))

    # Блок 3: Change Cost (Вартість зміни)
    f.append(fitbox(40, 245, 410, 140, "3. Change Cost — Вартість зміни (Evolution Cost)\n• Когнітивне навантаження кодової бази\n• Складність безпечного рефакторингу\n• Ризик ламання суміжних систем при змінах\n• Вартість додавання нових вимог", size=13, fill=GREEN_T, stroke=POS))

    # Блок 4: Exit Cost (Вартість виходу)
    f.append(fitbox(510, 245, 410, 140, "4. Exit Cost — Вартість виходу (Lock-in Cost)\n• Переписування протекших абстракцій\n• Egress-мито за виведення даних із хмари\n• Заміна пропрацевих API й інфраструктури\n• Ризик банкрутства або зміни умов вендора", size=13, fill=RED_T, stroke=NEG))

    # Стрілки зв'язку між блоками (Trade-off компенсації)
    f.append(arrow(450, 130, 510, 130, color=INK, sw=2))
    f.append(arrow(240, 200, 240, 245, color=INK, sw=2))
    f.append(arrow(715, 200, 715, 245, color=INK, sw=2))
    f.append(arrow(510, 315, 450, 315, color=INK, sw=2))

    render(os.path.join(OUT, 'four-price-tags.svg'), W, H, *f,
           title="Життєвий цикл та чотири цінники архітектурного рішення")


def fig_tradeoff_tree():
    """Дерево економічних компенсацій: прив'язка архітектури до бізнес-моделі."""
    W, H = 980, 440
    f = []

    # Корінь: Бізнес-модель
    f.append(fitbox(340, 50, 300, 45, "Бізнес-модель проєкту\n(Економічний двигун)", size=14, bold=True, fill=NEUT, stroke=INK))

    # Гілка 1: High-Volume Low-ARPU (B2C)
    f.append(arrow(400, 95, 220, 120, color=INK, sw=2))
    f.append(fitbox(70, 120, 300, 60, "High-Volume / Low-ARPU\n(B2C, IoT, Масовий SaaS)\nНизький чек · Мільйони користувачів", size=12, bold=True, fill=AMBER_T, stroke=AMBER))

    f.append(arrow(220, 180, 220, 210, color=INK, sw=2))
    f.append(fitbox(50, 210, 340, 85, "Головний пріоритет: Мінімальний Unit Cost\n• Високий початковий CapEx виправданий\n• Свої протоколи, Bare Metal / hybrid, кеш\n• Асинхронний Fan-out, zero-copy", size=12, fill=GREEN_T, stroke=POS))

    f.append(arrow(220, 295, 220, 330, color=INK, sw=2))
    f.append(fitbox(50, 330, 340, 80, "Результат:\nДорого розробити (CapEx ↑),\nале низький OpEx тримає високий Gross Margin", size=12, bold=True, fill=BLUE_T, stroke=FIELD))

    # Гілка 2: Low-Volume High-ARPU (B2B Enterprise)
    f.append(arrow(580, 95, 760, 120, color=INK, sw=2))
    f.append(fitbox(610, 120, 300, 60, "Low-Volume / High-ARPU\n(B2B Enterprise, Fintech Core)\nВисокий чек ($50k+) · Мало клієнтів", size=12, bold=True, fill=BLUE_T, stroke=FIELD))

    f.append(arrow(760, 180, 760, 210, color=INK, sw=2))
    f.append(fitbox(590, 210, 340, 85, "Головний пріоритет: Time-to-Market & SLA\n• Керовані хмарні сервіси (SaaS/PaaS)\n• Мінімальний початковий CapEx\n• Синхронні контракти, ізольовані тенанти", size=12, fill=AMBER_T, stroke=AMBER))

    f.append(arrow(760, 295, 760, 330, color=INK, sw=2))
    f.append(fitbox(590, 330, 340, 80, "Результат:\nШвидкий старт (CapEx ↓),\nвисокий OpEx легко покривається маржею чеку", size=12, bold=True, fill=GREEN_T, stroke=POS))

    render(os.path.join(OUT, 'economic-tradeoff-tree.svg'), W, H, *f,
           title="Дерево економічних компенсацій")


def fig_unit_cost_scaling_trap():
    """Динаміка Unit Cost проти ARPU при зростанні масштабу."""
    W, H = 960, 440
    f = []

    # Осі
    f.append(arrow(80, 370, 900, 370, color=INK, sw=2)) # X
    f.append(arrow(80, 370, 80, 60, color=INK, sw=2))   # Y

    f.append(text(890, 395, "Кількість активних користувачів / трафік (N)", size=12, color=INK, anchor="end"))
    f.append(text(90, 50, "Вартість інфраструктури на 1 користувача ($ / Unit)", size=12, color=INK, anchor="start"))

    # Пунктирна лінія ARPU (дохід на користувача)
    f.append(line(80, 180, 880, 180, color=POS, sw=2.5, dash="6 4"))
    f.append(text(860, 165, "Дохід на користувача (ARPU = $1.50)", size=12, bold=True, color=POS, anchor="end"))

    # Крива 1: Сублінійна O(1) / O(log N) — ефективна архітектура (чорнила/синій)
    f.append('<path d="M 80 320 Q 400 310 880 300" fill="none" stroke="%s" stroke-width="3"/>' % FIELD)
    f.append(text(860, 285, "Ефективний Unit Cost: O(1) / O(log N)", size=12, bold=True, color=FIELD, anchor="end"))

    # Крива 2: Суперлінійна O(N) Unit Cost — Пастка архітектурного дрейфу (червоний)
    f.append('<path d="M 80 350 Q 500 310 830 70" fill="none" stroke="%s" stroke-width="3.5"/>' % NEG)
    f.append(text(810, 60, "Пастка архітектури: Unit Cost O(N)", size=12, bold=True, color=NEG, anchor="end"))

    # Точка перетину (Crossover point) з ARPU на X=675, Y=180
    f.append(circle(675, 180, 7, fill=AMBER, stroke=INK, sw=1.5))
    f.append(line(675, 180, 675, 370, color=AMBER, sw=1.5, dash="4 4"))

    f.append(fitbox(530, 90, 220, 65, "Точка банкрутства:\nUnit Cost перевищує ARPU!\nЗбиток на кожному юзері", size=11, bold=True, fill=RED_T, stroke=NEG))

    # Зони
    f.append(fitbox(150, 220, 240, 55, "Зона прибутку (Gross Margin > 0):\nARPU перевищує витрати", size=11, fill=GREEN_T, stroke=POS))
    f.append(fitbox(710, 220, 160, 55, "Зона збитків:\nВід'ємна маржа", size=11, fill=RED_T, stroke=NEG))

    render(os.path.join(OUT, 'unit-cost-scaling-trap.svg'), W, H, *f,
           title="Динаміка Unit Cost та пастка недосяжного масштабу")


if __name__ == '__main__':
    fig_four_price_tags()
    fig_tradeoff_tree()
    fig_unit_cost_scaling_trap()
    print("Figures generated successfully.")
