# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

BLUE_T  = "#eaf0fd"
GREEN_T = "#e7f6ec"
AMBER_T = "#fdf0dd"
RED_T   = "#fdecea"
PURP_T  = "#f3e8ff"
NEUT    = "#eef2f6"

AMBER   = "#e08a1e"
GREEN   = "#2e7d32"
BLUE    = "#1565c0"
RED     = "#c62828"
PURPLE  = "#7b1fa2"


def fig_taste_triad():
    """Трипелюсткова мапа інженерного смаку архітектора: Елегантність, Прагматизм та Чесність."""
    W, H = 1020, 460
    f = []

    # Центральне ядро: Смак архітектора
    f.append(fitbox(380, 180, 260, 100, "СМАК АРХІТЕКТОРА\n\n• Натренована інтуїція компромісу\n• Збереження цілісності системи\n• Свідомий баланс trade-offs",
                    size=13, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # Певний 1: Елегантність
    f.append(fitbox(50, 40, 270, 110, "1. Елегантність & Простота\n\n• Максимальний важіль мінімумом дій\n• Боротьба з випадковою складністю\n• Simple vs Easy (Річ Гайкі)",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(arrow(320, 95, 410, 180, color=BLUE, sw=2))

    # Певний 2: Прагматизм
    f.append(fitbox(700, 40, 270, 110, "2. Контекстний Прагматизм\n\n• Рішення під реальні обмеження\n• One-way vs Two-way doors\n• YAGNI та швидкість зворотного зв'язку",
                    size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(arrow(700, 95, 610, 180, color=GREEN, sw=2))

    # Певний 3: Інженерна чесність
    f.append(fitbox(370, 320, 280, 110, "3. Інженерна Чесність\n\n• Визнання прихованої ціни складності\n• Прозорість операційних витрат\n• Запис неідеальних рішень у ADR",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))
    f.append(arrow(510, 320, 510, 280, color=PURPLE, sw=2))

    # Результат у бізнесі
    f.append(fitbox(50, 210, 260, 80, "Результат для системи:\n\nНизька вартість змін & стійкість",
                    size=12, bold=True, fill=NEUT, stroke=INK, color=INK))
    f.append(arrow(380, 230, 310, 230, color=INK, sw=2))

    render(os.path.join(OUT, 'taste-triad.svg'), W, H, *f,
           title="Трипелюсткова мапа інженерного смаку архітектора")


def fig_complexity_spectrum():
    """Спектр складності рішення: Примітив -> Смак (Елегантність) -> Over-engineering."""
    W, H = 1020, 380
    f = []

    # 3 Зони складності
    # Зона 1: Примітивна незрілість
    f.append(fitbox(40, 60, 290, 220, "ПРИМІТИВНА НЕЗРІЛІСТЬ\n\n• Хаотичний спагетті-код\n• Відсутність меж і контрактів\n• Неконтрольовані побічні ефекти\n• Змішування бізнес-логіки з I/O\n\nРизик: Аварії при зростанні",
                    size=12, fill=RED_T, stroke=RED, color=RED))

    # Зона 2: Зона смаку (Елегантна простота)
    f.append(fitbox(365, 40, 290, 260, "ЗОНА ІНЖЕНЕРНОГО СМАКУ\n(Елегантна простота)\n\n• Чіткі межі та ізольовані контексти\n• Мінімально необхідна абстракція\n• Прозора простежуваність викликів\n• Низьке зчеплення, висока зв'язність\n• YAGNI за замовчуванням\n\nПеревага: Керована еволюція",
                    size=12, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Зона 3: Надпроектування (Over-engineering)
    f.append(fitbox(690, 60, 290, 220, "НАДПРОЄКТУВАННЯ\n(Over-engineering Trap)\n\n• 7 шарів не потрібної індирекції\n• CQRS / Event Sourcing без потреби\n• Саморобні фреймворки й DSL\n• 15 DTO для передачі одного поля\n\nРизик: Когнітивний колапс",
                    size=12, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # Стрілка прогресу / пастки
    f.append(arrow(330, 170, 365, 170, color=GREEN, sw=2))
    f.append(arrow(655, 170, 690, 170, color=AMBER, sw=2))

    # Підпис знизу
    f.append(fitbox(40, 315, 940, 45, "Золота середина: Архітектурний смак утримує систему в зеленій зоні, запобігаючи хаосу та надлишку",
                    size=12, bold=True, fill=NEUT, stroke=INK, color=INK))

    render(os.path.join(OUT, 'complexity-spectrum.svg'), W, H, *f,
           title="Спектр складності програмних рішень")


def fig_rule_breaking_matrix():
    """Матриця прийняття рішень про контрольоване порушення правил."""
    W, H = 1020, 440
    f = []

    # Заголовок блоку порівняння
    f.append(fitbox(40, 30, 460, 45, "СЛІПИЙ ДОГМАТИЗМ (Правило ради правила)", size=13, bold=True, fill=RED_T, stroke=RED, color=RED))
    f.append(fitbox(520, 30, 460, 45, "КОНТРОЛЬОВАНЕ ПОРУШЕННЯ (Смак і прагматизм)", size=13, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Рядок 1: DRY
    f.append(fitbox(40, 95, 460, 90, "Сліпий DRY:\nШтучне об'єднання двох різних контекстів у єдиний клас ради усунення 5 одинакових рядків.\nНаслідок: Паразитне зчеплення (Coupling)", size=12, fill=NEUT, stroke=INK))
    f.append(fitbox(520, 95, 460, 90, "Дублювання замість невірної абстракції:\nСвідоме дублювання структури в двох сервісах.\nНаслідок: Повна автономія еволюції контекстів", size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Рядок 2: Шари (Layering)
    f.append(fitbox(40, 205, 460, 90, "Сліпа шаруватість:\nПрогонка транзакцій аналітики через Controller -> Service -> Domain -> DAO -> DTO.\nНаслідок: Затримка й когнітивний оверхед", size=12, fill=NEUT, stroke=INK))
    f.append(fitbox(520, 205, 460, 90, "Свідомий прокол шару (Direct Read):\nПрямий read-only SQL запит з контролера аналітики.\nНаслідок: p99 латентність < 5 мс, код у 20 рядків", size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Рядок 3: Топологія (Microservices)
    f.append(fitbox(40, 315, 460, 90, "Сліпі мікросервіси:\nВиділення 12 сервісів для команди з 3 розробників.\nНаслідок: Розподілений моноліт, мережеві каскади", size=12, fill=NEUT, stroke=INK))
    f.append(fitbox(520, 315, 460, 90, "Модульний моноліт на старті:\nОдин процес з чіткими межами модулів у git.\nНаслідок: Миттєвий деплой, проста реорганізація", size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))

    render(os.path.join(OUT, 'rule-breaking-matrix.svg'), W, H, *f,
           title="Матриця контрольованого порушення архітектурних правил")


if __name__ == "__main__":
    fig_taste_triad()
    fig_complexity_spectrum()
    fig_rule_breaking_matrix()
    print("Figures generated successfully.")
