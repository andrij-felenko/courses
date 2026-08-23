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


def fig_dh_evolution_epochs():
    """Чотири епохи системної архітектури Digital Homes (2019–2024)."""
    W, H = 1040, 480
    f = []

    # Епохи - 4 блоки
    # Ep 1: 2019 Monolith
    f.append(fitbox(40, 50, 220, 320,
                    "Епоха 1: 2019\nМоноліт v1.0\n\n• Python/Django MVP\n• Єдина PostgreSQL БД\n• Прямі сокети хабів\n• 1,000 будинків\n\nОбмеження:\nВузьке місце запису\nНемає офлайн-автономії",
                    size=12, fill=NEUT, stroke=INK, color=INK))

    # Ep 2: 2020-2021 Microservices
    f.append(fitbox(290, 50, 220, 320,
                    "Епоха 2: 2020–2021\nМікросервіси v2.0\n\n• Сервіси Go/Java\n• MQTT + Kafka брокери\n• Redis Device Shadow\n• 15,000 будинків\n\nОбмеження:\nСкладні саги й 2PC\nДрейф стану shadows",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))

    # Ep 3: 2022-2023 Edge & Video
    f.append(fitbox(540, 50, 220, 320,
                    "Епоха 3: 2022–2023\nEdge & WebRTC v3.0\n\n• C++ двигун на хабі\n• WebRTC P2P для відео\n• Офлайн-автономія <100ms\n• TimescaleDB телеметрія\n\nОбмеження:\nСкладність OTA флоту",
                    size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Ep 4: 2024 Multi-region Scale
    f.append(fitbox(790, 50, 220, 320,
                    "Епоха 4: 2024\nМультирегіон v4.0\n\n• ScyllaDB + VictoriaMetrics\n• Envoy API Gateway\n• Fitness Functions у CI\n• 50,000+ хабів\n\nПеремога:\nСтійкість до штормів",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    # Стрілки між епохами
    f.append(arrow(260, 210, 290, 210, color=INK, sw=2))
    f.append(arrow(510, 210, 540, 210, color=BLUE, sw=2))
    f.append(arrow(760, 210, 790, 210, color=GREEN, sw=2))

    # Нижній часовий проміжок
    f.append(fitbox(40, 395, 970, 55,
                    "Головний системний вектор: Від централізованого хмарного моноліту → до автономного edge-обчислення та розподіленого мультирегіону",
                    size=13, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))

    render(os.path.join(OUT, 'dh-evolution-epochs.svg'), W, H, *f,
           title="Чотири епохи системної архітектури Digital Homes")


def fig_dh_utility_verification():
    """Звірка архітектурних результатів проти Дерева корисності."""
    W, H = 1000, 460
    f = []

    # Заголовок матриці
    f.append(fitbox(40, 30, 920, 45, "Матриця відповідності атрибутів корисності (Utility Tree) реальним результатам",
                    size=14, bold=True, fill=NEUT, stroke=INK, color=INK))

    # 4 квадранти / категорії підсумків
    # 1. Повні перемоги (Win)
    f.append(fitbox(40, 95, 445, 155,
                    "🟢 Повні перемоги (Achieved Drivers)\n\n• Офлайн-автономність замка (<100мс на хабі)\n• Затримка відео дзвінка (<1.6с через WebRTC)\n• Зворотна сумісність контракту (4 покоління датчиків)",
                    size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # 2. Необхідні компроміси (Partial Trade-offs)
    f.append(fitbox(515, 95, 445, 155,
                    "🟡 Контрольовані компроміси (Trade-offs)\n\n• Пропускна здатність телеметрії (TimescaleDB замість Kafka)\n• Бюджет сховища (Edge-буфер + Cloud Object Lifecycle)\n• Багатокомпонентний API Gateway (Envoy gRPC/REST)",
                    size=12, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # 3. Больові точки та дрейф (Pain Points)
    f.append(fitbox(40, 270, 445, 155,
                    "🔴 Виправлені больові точки (Resolved Friction)\n\n• Дрейф стану Device Shadow → Event Sourcing в v3.2\n• Передчасна мікросервісна декомпозиція → консолідація\n• Спільна база даних → ізольовані схемні межі",
                    size=12, fill=RED_T, stroke=RED, color=RED))

    # 4. Засвоєні уроки (Hard Lessons)
    f.append(fitbox(515, 270, 445, 155,
                    "🟣 Засвоєні уроки штормів (Outage Lessons)\n\n• Відновлення після блекауту 50k хабів → Backoff + Jitter\n• Захист архітектурних меж → Fitness Functions у CI\n• Односторонній вибір безпеки → mTLS з заводу",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    render(os.path.join(OUT, 'dh-utility-verification.svg'), W, H, *f,
           title="Звірка результатів Digital Homes проти Дерева корисності")


def fig_dh_oneway_twoway_doors():
    """Категоризація 19 рішень Digital Homes за незворотністю (One-Way vs Two-Way Doors)."""
    W, H = 1000, 460
    f = []

    # Ліва колонка: One-Way Doors
    f.append(fitbox(40, 40, 445, 380,
                    "🚪 Незворотні рішення (One-Way Doors / Type 1)\nЦіна зміни: висока (місяці роботи, заміна заліза)\n\n1. Edge-First парадигма автономії хаба (C++ Engine)\n2. Схема бінарного протоколу Protobuf над MQTT\n3. mTLS криптографічна ідентичність пристроїв\n4. Доменна ізоляція контекстів і меж агрегатів\n5. Append-only модель зберігання часових рядів\n\nСтратегія: 80% часу аналізу, прототипування, ADR",
                    size=12, fill=RED_T, stroke=RED, color=RED))

    # Права колонка: Two-Way Doors
    f.append(fitbox(515, 40, 445, 380,
                    "🔄 Двосторонні рішення (Two-Way Doors / Type 2)\nЦіна зміни: низька (дні/тижні, рефакторинг)\n\n1. Вибір СУБД телеметрії (TimescaleDB ↔ VictoriaMetrics)\n2. Конкретна реалізація MQTT-брокера (Mosquitto ↔ EMQX)\n3. Фреймворк API Gateway (Nginx ↔ Envoy)\n4. Протокол live-оновлень UI (WebSockets ↔ SSE)\n5. Вибір мови високорівневих сервісів (Go ↔ Java)\n\nСтратегія: Швидкі експерименти, ізоляція за швами",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))

    render(os.path.join(OUT, 'dh-oneway-twoway-doors.svg'), W, H, *f,
           title="Класифікація рішений Digital Homes за незворотністю")


def fig_dh_architectural_guardrails():
    """Контур автоматичного захисту архітектури через фітнес-функції."""
    W, H = 1020, 440
    f = []

    # Схема конвеєра CI/CD із фітнес-функціями
    f.append(fitbox(40, 50, 200, 110, "1. Git Push / PR\n\nЗміна коду або контрактів", size=12, fill=NEUT, stroke=INK, color=INK))
    f.append(fitbox(290, 50, 210, 110, "2. Статичні фітнес-функції\n\nПеревірка залежностей контекстів (tree-sitter)", size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(fitbox(550, 50, 210, 110, "3. Контрактні фітнес-функції\n\nЗворотна сумісність Proto/OpenAPI", size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))
    f.append(fitbox(800, 50, 180, 110, "4. Динамічний load-test\n\nПеревірка latencies p99 < 100ms", size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Стрілки
    f.append(arrow(240, 105, 290, 105, color=INK, sw=2))
    f.append(arrow(500, 105, 550, 105, color=BLUE, sw=2))
    f.append(arrow(760, 105, 800, 105, color=PURPLE, sw=2))

    # Нижня частина: Блокування PR при дрейфі
    f.append(fitbox(290, 220, 690, 160,
                    "Результат роботи заслонів CI/CD:\n\n• Блокування незаконних зв'язків між сервісами (наприклад: Telemetry → Billing DB)\n• Попередження про злам зворотної сумісності бінарного протоколу\n• Автоматичний відкат деплою при виявленні витоку пам'яті чи перевищенні латентності\n\nРезультат: Нуль архітектурної ерозії протягом 2 років після впровадження",
                    size=12, fill=AMBER_T, stroke=AMBER, color=AMBER))

    f.append(arrow(890, 160, 890, 220, color=GREEN, sw=2))

    render(os.path.join(OUT, 'dh-architectural-guardrails.svg'), W, H, *f,
           title="Система захисту від ерозії через фітнес-функції")


if __name__ == '__main__':
    fig_dh_evolution_epochs()
    fig_dh_utility_verification()
    fig_dh_oneway_twoway_doors()
    fig_dh_architectural_guardrails()
    print("All figures rendered successfully!")
