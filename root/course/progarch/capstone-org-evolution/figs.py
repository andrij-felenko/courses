# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED     = "#d9534f"
GREEN   = "#2e7d32"
BLUE    = "#1565c0"
PURPLE  = "#6a1b9a"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
PURPLE_T= "#f3e5f5"
NEUT    = "#eef2f6"
INK     = "#1a202c"


def fig_conway_inverse_topologies():
    """Візуалізація Реверсивного маневру Конвея: узгодження топології команд (Stream, Platform, Enabling)
    із межами контекстів системи для усунення орг-зчеплення."""
    W, H = 1000, 480
    f = []

    # ── Заголовок колонок ──
    f.append(fitbox(40, 30, 440, 36, "А. Традиційна організація (Орг-зчеплення)", size=13, bold=True, fill=RED_T, stroke=RED))
    f.append(fitbox(520, 30, 440, 36, "Б. Соціотехнічний дизайн (Team Topologies)", size=13, bold=True, fill=GREEN_T, stroke=GREEN))

    # ── Колонка А: Хаотичне орг-зчеплення ──
    f.append(fitbox(55, 85, 410, 45, "Frontend Team (React/Mobile)", size=11, fill=NEUT, stroke="#90a4ae"))
    f.append(fitbox(55, 140, 410, 45, "Backend Monolith Team (15 розробників)", size=11, fill=RED_T, stroke=RED))
    f.append(fitbox(55, 195, 410, 45, "DBA & Ops Team (Ручні розгортання)", size=11, fill=NEUT, stroke="#90a4ae"))

    # Сервісна сітка знизу
    f.append(fitbox(55, 270, 125, 55, "Payments\nService", size=10, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(197, 270, 125, 55, "Telemetry\nService", size=10, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(340, 270, 125, 55, "Devices\nRegistry", size=10, fill=AMBER_T, stroke=AMBER))

    # Вертикальні лінії зв'язку між блоками (у чистому проміжку від Y=242 до Y=268)
    f.append(line(117, 242, 117, 268, color=RED, sw=1.5, dash="3,3"))
    f.append(line(260, 242, 260, 268, color=RED, sw=1.5, dash="3,3"))
    f.append(line(402, 242, 402, 268, color=RED, sw=1.5, dash="3,3"))

    f.append(fitbox(40, 340, 440, 110, "Наслідки:\n• Перехресні блокування (Wait States) на кожному релізі\n• Немає чіткого власника доменної цілісності\n• Розмита відповідальність між шарами коду", size=11, fill="#fff3e0", stroke=AMBER))

    # ── Розділювач ──
    f.append(line(490, 40, 490, 450, color="#cfd8dc", sw=1.5, dash="4,4"))

    # ── Колонка Б: Реверсивний маневр Конвея ──
    f.append(fitbox(535, 85, 200, 125, "Stream-Aligned: Payments\n\n[ Context: Ledger & Billing ]\n• Власний репозиторій\n• Повний цикл релізу", size=11, bold=True, fill=GREEN_T, stroke=GREEN))
    f.append(fitbox(745, 85, 200, 125, "Stream-Aligned: Devices\n\n[ Context: Telemetry & IoT ]\n• Власний репозиторій\n• Повний цикл релізу", size=11, bold=True, fill=BLUE_T, stroke=BLUE))

    # Enabling team
    f.append(fitbox(535, 225, 410, 40, "Enabling Team: Architecture & Security (Консультації та стандарти)", size=11, fill=PURPLE_T, stroke=PURPLE))

    # Platform team
    f.append(fitbox(535, 280, 410, 45, "Platform Team: Developer Platform (IDP / Self-Service Infrastructure)", size=11, bold=True, fill="#e1f5fe", stroke="#0288d1"))

    # Стрілки X-as-a-Service
    f.append(arrow(635, 280, 635, 267, color=BLUE, sw=2))
    f.append(arrow(845, 280, 845, 267, color=BLUE, sw=2))

    f.append(fitbox(520, 340, 440, 110, "Результат:\n• Повна автономність релізів без очікування інших команд\n• Extraneous Load знято через Self-service Platform\n• Архітектура коду збігається з орг-топологією", size=11, fill=GREEN_T, stroke=GREEN))

    render(os.path.join(OUT, 'conway-inverse-topologies.svg'), W, H, *f,
           title="Реверсивний маневр Конвея та орг-топології систем")


def fig_tco_lockin_matrix():
    """Діаграма оцінки TCO та Vendor Lock-in Exit Cost: співвідношення операційної швидкості та ціни виходу."""
    W, H = 1000, 450
    f = []

    # Вісі координат
    f.append(arrow(80, 390, 940, 390, color=INK, sw=2))  # Х: Операційна швидкість / Managed-глибина
    f.append(arrow(80, 390, 80, 40, color=INK, sw=2))   # Y: Lock-in Exit Cost (ціна виходу)

    f.append(text(920, 420, "Managed-глибина →", size=12, bold=True, color=INK, anchor="end"))
    f.append(text(30, 50, "Exit Cost ↑", size=12, bold=True, color=INK))

    # Пунктирні лінії розділення квадрантів
    f.append(line(490, 50, 490, 385, color="#cfd8dc", sw=1.5, dash="3,3"))
    f.append(line(85, 225, 930, 225, color="#cfd8dc", sw=1.5, dash="3,3"))

    # Квадрант 1: Open Source Self-Hosted (низький Y, низький X)
    f.append(fitbox(110, 240, 360, 120, "1. Self-Hosted (Vanilla Postgres, K8s)\n\n• Lock-in Exit Cost: Низька (0–10%)\n• TCO: Висока операційна складність\n• Швидкість старту: Повільна", size=11, fill=GREEN_T, stroke=GREEN))

    # Квадрант 2: Managed Standard (поміркований Y, високий X)
    f.append(fitbox(520, 240, 380, 120, "2. Managed Open Standard (AWS RDS, MSK)\n\n• Lock-in Exit Cost: Поміркована (10–25%)\n• TCO: Оптимальний баланс\n• Швидкість старту: Висока (Golden Path)", size=11, bold=True, fill=BLUE_T, stroke=BLUE))

    # Квадрант 3: Proprietary Cloud Native (високий Y, високий X)
    f.append(fitbox(520, 80, 380, 130, "3. Deep Cloud Native (DynamoDB, Lambda, AppSync)\n\n• Lock-in Exit Cost: Критично висока (60–90%)\n• TCO: Низький старт, дорого у масштабі\n• Швидкість: Максимальна на старті", size=11, fill=RED_T, stroke=RED))

    # Квадрант 4: Abstraction Trap (Cloud Agnostic) (високий Y, низький X)
    f.append(fitbox(110, 80, 360, 130, "4. Cloud Agnostic Trap (Власні обгортки)\n\n• Lock-in Exit Cost: Теоретично низька\n• TCO: Катастрофічно висока (Extraneous Load)\n• Швидкість: Постійний підпис абстракцій", size=11, fill=AMBER_T, stroke=AMBER))

    # Лінія оптимального зваженого вибору - у чистому між-квадрантному проміжку (X=475..515)
    f.append(arrow(475, 235, 515, 215, color=PURPLE, sw=2))

    f.append(fitbox(350, 15, 300, 30, "Зона свідомого архітектурного компромісу", size=11, bold=True, fill=PURPLE_T, stroke=PURPLE))

    render(os.path.join(OUT, 'tco-lockin-matrix.svg'), W, H, *f,
           title="Матриця оцінки TCO та Vendor Lock-in Exit Cost")


def fig_deprecation_lifecycle_pipeline():
    """Еволюційний пайплайн зняття сервісів з експлуатації (Deprecation & Migration Pipeline)."""
    W, H = 1000, 420
    f = []

    # 4 фази еволюційного виведення
    f.append(fitbox(40, 60, 210, 140, "Фаза 1: Notice\n\n• Додавання Sunset HTTP-заголовків\n• Фіксація контрактів у CI\n• Оповіщення споживачів", size=11, fill=BLUE_T, stroke=BLUE))

    # Стрілка 1->2
    f.append(arrow(250, 130, 280, 130, color=INK, sw=2))

    # Фаза 2
    f.append(fitbox(280, 60, 210, 140, "Фаза 2: Shadowing\n\n• Трафіковий дубляж (Traffic Shadowing)\n• Порівняння відповідей\n• Нульовий вплив на prod", size=11, fill=PURPLE_T, stroke=PURPLE))

    # Стрілка 2->3
    f.append(arrow(490, 130, 520, 130, color=INK, sw=2))

    # Фаза 3
    f.append(fitbox(520, 60, 210, 140, "Фаза 3: Dual Write\n\n• Подвійний запис у стару й нову БД\n• Перемикання читання (Canary)\n• Можливість відкату", size=11, fill=AMBER_T, stroke=AMBER))

    # Стрілка 3->4
    f.append(arrow(730, 130, 760, 130, color=INK, sw=2))

    # Фаза 4
    f.append(fitbox(760, 60, 200, 140, "Фаза 4: Tombstone\n\n• Відключення старого шлюзу\n• Архівація даних і коду\n• Звільнення ресурсів", size=11, bold=True, fill=GREEN_T, stroke=GREEN))

    # Нижня панель: Контроль через Fitness Functions
    f.append(fitbox(40, 240, 920, 130, "Автоматизований контроль ерозії (Architecture Fitness Functions у CI/CD):\n\n1. Static AST Linter: Заборона нових викликів Deprecated-ендпоінтів у код-базі\n2. Metrics Alert: Авто-сповіщення при виявленні трафіку на розкладених версіях за 14 днів до Sunset\n3. ArchUnit Contract Gate: Автоматичне блокування PR, що порушують нові межі команд", size=11, fill=NEUT, stroke="#78909c"))

    render(os.path.join(OUT, 'deprecation-lifecycle-pipeline.svg'), W, H, *f,
           title="Еволюційний конвеєр Deprecation та автоматизований контроль ерозії")


if __name__ == '__main__':
    fig_conway_inverse_topologies()
    fig_tco_lockin_matrix()
    fig_deprecation_lifecycle_pipeline()
    print("All figures generated successfully!")
