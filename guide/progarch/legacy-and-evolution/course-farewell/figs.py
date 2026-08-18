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
INK     = "#263238"


def fig_journey_scale_spirals():
    """Еволюційний шлях системи та сходження п'яти наскрізних спіралей якості."""
    W, H = 1020, 440
    f = []

    # 4 етапи розвитку системи (Масштаб турботи)
    f.append(fitbox(30, 40, 220, 100, "1. Одноплатник (DH v0)\n\n• Рядок коду & скрипт\n• Прямий доступ до I/O\n• Локальна пам'ять",
                    size=12, fill=NEUT, stroke=INK, color=INK))
    f.append(fitbox(280, 40, 220, 100, "2. Застосунок & Машина\n\n• Шар відмежування\n• Порти й адаптери\n• Потоки & Event Loop",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(fitbox(530, 40, 220, 100, "3. Розподілені Сервіси\n\n• Межі контекстів\n• Черги & Outbox / Saga\n• Спектр консистентності",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))
    f.append(fitbox(780, 40, 210, 100, "4. 3-Регіональна Хмара\n\n• Мультирегіональність\n• Team Topologies\n• FinOps & Strangler Fig",
                    size=12, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Стрілки масштабу
    f.append(arrow(250, 90, 280, 90, color=INK, sw=2))
    f.append(arrow(500, 90, 530, 90, color=BLUE, sw=2))
    f.append(arrow(750, 90, 780, 90, color=PURPLE, sw=2))

    # 5 Наскрізних спіралей якості
    f.append(fitbox(30, 160, 960, 48, "1. Контракт і помилки: Сигнатура функції  ──>  Schema Registry / gRPC  ──>  SLA/SLO сервісів",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(fitbox(30, 215, 960, 48, "2. Зворотність і ризик: Незмінність даних  ──>  Port/Adapter ізоляція  ──>  Strangler Fig міграція",
                    size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(fitbox(30, 270, 960, 48, "3. Ідемпотентність: Атомарна операція  ──>  HTTP Key Dedup  ──>  Ledger Reconciliation",
                    size=12, fill=AMBER_T, stroke=AMBER, color=AMBER))
    f.append(fitbox(30, 325, 960, 48, "4. Кеш і консистентність: L1/L3 кеш процесора  ──>  Redis Write-Through  ──>  CQRS Read-model lag",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))
    f.append(fitbox(30, 380, 960, 48, "5. Межі довіри й стійкість: Валідація аргументів  ──>  OAuth2 / mTLS Zero Trust  ──>  Adaptive Shedding",
                    size=12, fill=RED_T, stroke=RED, color=RED))

    render(os.path.join(OUT, 'journey-scale-spirals.svg'), W, H, *f,
           title="Еволюційний шлях системи та сходження спіралей якості")


def fig_architecture_decision_flow():
    """Потік прийняття значущих інженерних рішень під невизначеністю."""
    W, H = 1020, 420
    f = []

    # Крок 1: Pre-mortem & Ризик
    f.append(fitbox(30, 50, 210, 130, "1. Оцінка ризиків\n\n• Pre-mortem аналіз\n• Матриця ймовірності\n• Потенційний вплив",
                    size=12, fill=RED_T, stroke=RED, color=RED))

    # Крок 2: Класифікація Дверей
    f.append(fitbox(280, 50, 210, 130, "2. Класифікація дверей\n\n• One-way door (консенсус)\n• Two-way door (делегування)\n• Ціна зворотного відкату",
                    size=12, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # Крок 3: Спайк / Купівля інформації
    f.append(fitbox(530, 50, 210, 130, "3. Купівля інформації\n\n• Timeboxed Spike\n• Walking Skeleton\n• Зняття ключових плям",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))

    # Крок 4: Фіксація у ADR
    f.append(fitbox(780, 50, 210, 130, "4. Фіксація у ADR\n\n• Контекст і альтернативи\n• Вибране рішення\n• Явні наслідки й борг",
                    size=12, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Стрілки потоку
    f.append(arrow(240, 115, 280, 115, color=RED, sw=2))
    f.append(arrow(490, 115, 530, 115, color=AMBER, sw=2))
    f.append(arrow(740, 115, 780, 115, color=BLUE, sw=2))

    # Нижній шар контролю та еволюції
    f.append(fitbox(30, 230, 460, 140, "АВТОМАТИЗОВАНИЙ КОНТРОЛЬ (CI)\n\n• Архітектурні тести (ArchUnit / dependency-cruiser)\n• Перевірка меж шарів коду та заборона зациклень\n• Захист від невпинної архітектурної ерозії",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))
    f.append(fitbox(530, 230, 460, 140, "ОПЕРАЦІЙНА РЕТРОСПЕКТИВА\n\n• Перевірка припущень проти real-world метрик\n• Регулярний огляд ризик-реєстру та SLO\n• Вчасне проведення деприкейшину й рефакторингу",
                    size=12, fill=NEUT, stroke=INK, color=INK))

    # Стрілки зв'язку з нижнім шаром
    f.append(arrow(885, 180, 760, 230, color=GREEN, sw=2))
    f.append(arrow(135, 180, 260, 230, color=RED, sw=2))

    render(os.path.join(OUT, 'architecture-decision-flow.svg'), W, H, *f,
           title="Потік прийняття значущих інженерних рішень")


def fig_continuous_learning_loop():
    """Петля неперервного навчання та інженерної чесності архітектора."""
    W, H = 1020, 400
    f = []

    # 4 Вузли петлі
    f.append(fitbox(50, 40, 420, 130, "1. Спостереження продакшину (Observability)\n\n• Телеметрія (метрики, логи, трейси)\n• Вимірювання SLO та бюджету помилок\n• Реальний профіль навантаження й затримок",
                    size=12, bold=True, fill=BLUE_T, stroke=BLUE, color=BLUE))

    f.append(fitbox(550, 40, 420, 130, "2. Аналіз інцидентів та фактів (Honesty)\n\n• Беззаперечні факти замість припущень\n• Blameless Post-Mortem ретроспектива\n• Виявлення хибних початкових гіпотез",
                    size=12, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))

    f.append(fitbox(550, 230, 420, 130, "3. Адаптація та Рефакторинг (Evolution)\n\n• Виділення нових швів (Seams)\n• Покроковий Strangler Fig або BBA\n• Зменшення когнітивного навантаження",
                    size=12, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    f.append(fitbox(50, 230, 420, 130, "4. Оновлення драйверів і ADR (Feedback)\n\n• Коригування якісних атрибутів\n• Запис нових обмежень у журнал ADR\n• Перегляд соціотехнічної топології",
                    size=12, bold=True, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    # Направлені стрілки петлі (цикл за годинниковою стрілкою)
    f.append(arrow(470, 105, 550, 105, color=BLUE, sw=3))
    f.append(arrow(760, 170, 760, 230, color=AMBER, sw=3))
    f.append(arrow(550, 295, 470, 295, color=GREEN, sw=3))
    f.append(arrow(260, 230, 260, 170, color=PURPLE, sw=3))

    render(os.path.join(OUT, 'continuous-learning-loop.svg'), W, H, *f,
           title="Петля неперервного навчання та інженерної чесності")


if __name__ == '__main__':
    fig_journey_scale_spirals()
    fig_architecture_decision_flow()
    fig_continuous_learning_loop()
    print("Figures generated successfully!")
