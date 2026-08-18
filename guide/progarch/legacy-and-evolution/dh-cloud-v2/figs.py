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
INK     = "#1e293b"
BG      = "#ffffff"


def fig_v1_monolith_to_v2_geo():
    """Порівняння архітектури v1 Моноліт (Single DC) та v2 Гео-розподілена хмара з Strangler Gateway."""
    W, H = 1040, 520
    f = []

    # Фон лівий (v1)
    f.append(rect(20, 20, 480, 480, fill="#f8fafc", stroke="#cbd5e1", rx=8, sw=1.5))
    f.append(fitbox(40, 35, 440, 30, "v1: Монолітна спадщина (Single DC Frankfurt)", size=14, bold=True, fill=RED_T, stroke=RED, color=RED))

    # Компоненти v1
    f.append(fitbox(50, 85, 440, 60, "Клієнти (1.2M хабів / 4.5M застосунків)\nMQTT / REST безпосередньо в DC", size=11, fill=NEUT, stroke=INK, color=INK))
    f.append(arrow(270, 145, 270, 175, color=INK, sw=2))

    f.append(fitbox(50, 175, 440, 70, "Платформений моноліт v1\n(Twin B + Auth + Automation + Notif)\nСинхронний доступ до єдиної БД", size=11, fill=RED_T, stroke=RED, color=RED))
    f.append(arrow(270, 245, 270, 285, color=RED, sw=2))

    f.append(fitbox(50, 285, 210, 80, "PostgreSQL Monolith\n(P99 > 850 мс)\nСпільні таблиці стану", size=11, fill=AMBER_T, stroke=AMBER, color=AMBER))
    f.append(fitbox(280, 285, 210, 80, "Shared Redis Cluster\n(Каскадна інвалідація)\nThundering Herd ризик", size=11, fill=AMBER_T, stroke=AMBER, color=AMBER))

    f.append(fitbox(50, 395, 440, 85, "Проблеми v1:\n• Single Point of Failure (один DC)\n• Неможливість технічного вікна (SLO 99.99%)\n• Висока затримка запису під вечірнім піком", size=11, fill=RED_T, stroke=RED, color=RED))

    # Фон правий (v2)
    f.append(rect(540, 20, 480, 480, fill="#f8fafc", stroke="#cbd5e1", rx=8, sw=1.5))
    f.append(fitbox(560, 35, 440, 30, "v2: Гео-розподілена хмара (Strangler Pattern)", size=14, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Компоненти v2
    f.append(fitbox(570, 85, 420, 55, "Edge Fleet Routers (Multi-Region)\nБлизькі регіональні кінцеві точки", size=11, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(arrow(780, 140, 780, 165, color=BLUE, sw=2))

    f.append(fitbox(570, 165, 420, 55, "Strangler API Gateway & Feature Flags\nМаршрутизація трафіку (v1 ↔ v2)", size=11, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    # Стрілки маршрутизації
    f.append(arrow(680, 220, 680, 255, color=PURPLE, sw=2))
    f.append(arrow(880, 220, 880, 255, color=PURPLE, sw=2))

    f.append(fitbox(570, 255, 200, 75, "Device Twin v2 (CQRS)\nKafka Outbox +\nSharded Event Store", size=11, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(fitbox(790, 255, 200, 75, "Доменні мікросервіси\n(Notif / Analytics /\nAutomation Engine)", size=11, fill=GREEN_T, stroke=GREEN, color=GREEN))

    f.append(fitbox(570, 350, 420, 60, "CI/CD Fitness Guard & ArchUnit\nАвтоматичний контроль ерозії шарів і схем", size=11, fill=BLUE_T, stroke=BLUE, color=BLUE))

    f.append(fitbox(570, 425, 420, 55, "Переваги v2: Zero-downtime, ізоляція збоїв,\nгео-локальна латентність P99 < 45 мс", size=11, fill=GREEN_T, stroke=GREEN, color=GREEN))

    render(os.path.join(OUT, 'v1-monolith-to-v2-geo.svg'), W, H, *f,
           title="Порівняння архітектури v1 Моноліт та v2 Гео-розподілена хмара Digital Homes")


def fig_migration_phases_reversibility():
    """Етапи 4-фазної zero-downtime міграції з позначенням зворотності та Точки Неповернення."""
    W, H = 1040, 460
    f = []

    # Вісь часу
    f.append(line(60, 390, 980, 390, color=INK, sw=3))
    f.append(arrow(960, 390, 990, 390, color=INK, sw=3))

    # Фаза 0
    f.append(rect(60, 50, 200, 270, fill="#f1f5f9", stroke="#94a3b8", rx=6, sw=1.5))
    f.append(fitbox(70, 65, 180, 45, "Фаза 0: Baseline\n(Dark Launch)", size=12, bold=True, fill=NEUT, stroke=INK, color=INK))
    f.append(fitbox(70, 120, 180, 110, "• 100% читання/запису в v1\n• v2 деплоїться в режимі тень\n• Перевірка баз і Kafka", size=11, fill=BG, stroke="#cbd5e1", color=INK))
    f.append(fitbox(70, 240, 180, 65, "Зворотність: 100%\n(Two-Way Door)", size=11, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(line(160, 320, 160, 390, color=GREEN, sw=2, dash="4,4"))
    f.append(fitbox(100, 405, 120, 30, "Тиждень 1–2", size=11, color=INK))

    # Фаза 1
    f.append(rect(290, 50, 210, 270, fill="#eff6ff", stroke="#3b82f6", rx=6, sw=1.5))
    f.append(fitbox(300, 65, 190, 45, "Фаза 1: Expand &\nDual-Write", size=12, bold=True, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(fitbox(300, 120, 190, 110, "• Запис у v1 + Outbox у v2\n• Parallel Run verification (1%)\n• mismatch_total < 0.001%", size=11, fill=BG, stroke="#cbd5e1", color=INK))
    f.append(fitbox(300, 240, 190, 65, "Зворотність: Повна\n(Вимкнення прапорця)", size=11, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(line(395, 320, 395, 390, color=BLUE, sw=2, dash="4,4"))
    f.append(fitbox(335, 405, 120, 30, "Тиждень 3–4", size=11, color=INK))

    # Точка неповернення (Розділювач)
    f.append(line(525, 30, 525, 430, color=RED, sw=2.5, dash="6,4"))
    f.append(fitbox(465, 5, 120, 24, "ТОЧКА НЕПОВЕРНЕННЯ", size=10, bold=True, fill=RED_T, stroke=RED, color=RED))

    # Фаза 2
    f.append(rect(550, 50, 210, 270, fill="#fff7ed", stroke="#f97316", rx=6, sw=1.5))
    f.append(fitbox(560, 65, 190, 45, "Фаза 2: Read Switch &\nToken Backfill", size=12, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))
    f.append(fitbox(560, 120, 190, 110, "• Читання з v2 (з Fallback)\n• Backfill 500 req/s з v1\n• Первинні записи телеметрії v2", size=11, fill=BG, stroke="#cbd5e1", color=INK))
    f.append(fitbox(560, 240, 190, 65, "Зворотність: Обмежена\n(Потрібен реверсний backfill)", size=11, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))
    f.append(line(655, 320, 655, 390, color=AMBER, sw=2, dash="4,4"))
    f.append(fitbox(595, 405, 120, 30, "Тиждень 5–7", size=11, color=INK))

    # Фаза 3
    f.append(rect(780, 50, 200, 270, fill="#f0fdf4", stroke="#22c55e", rx=6, sw=1.5))
    f.append(fitbox(790, 65, 180, 45, "Фаза 3: Contract &\nDeprecate v1", size=12, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(fitbox(790, 120, 180, 110, "• 100% читання/запису v2\n• v1 Postgres у Read-Only (72h)\n• Архівування легасі-коду", size=11, fill=BG, stroke="#cbd5e1", color=INK))
    f.append(fitbox(790, 240, 180, 65, "Одностороння дверка\n(One-Way Door)", size=11, bold=True, fill=RED_T, stroke=RED, color=RED))
    f.append(line(880, 320, 880, 390, color=GREEN, sw=2, dash="4,4"))
    f.append(fitbox(820, 405, 120, 30, "Тиждень 8+", size=11, color=INK))

    render(os.path.join(OUT, 'migration-phases-reversibility.svg'), W, H, *f,
           title="Етапи 4-фазної zero-downtime міграції з позначенням зворотності")


def fig_fitness_guard_pipeline():
    """Контур автоматизованого fitness-контролю ерозії архітектури в CI/CD та runtime."""
    W, H = 1040, 440
    f = []

    # Блок 1: Коміт розробника
    f.append(fitbox(40, 60, 230, 100, "1. Git Commit / PR\n\nНовий код мікросервісу v2\nабо зміна схеми події", size=12, bold=True, fill=NEUT, stroke=INK, color=INK))
    f.append(arrow(270, 110, 320, 110, color=INK, sw=2))

    # Блок 2: CI/CD Fitness Guard Gateway
    f.append(rect(320, 40, 380, 360, fill="#f8fafc", stroke="#64748b", rx=8, sw=1.5))
    f.append(fitbox(340, 50, 340, 35, "2. CI/CD Fitness Guard Pipeline", size=13, bold=True, fill=BLUE_T, stroke=BLUE, color=BLUE))

    f.append(fitbox(340, 100, 340, 70, "Перевірка залежностей коду (AST / ArchUnit)\nЗаборона прямих викликів v1 DB з v2 сервісів\nЗаборона обходу DeviceTwinRepository", size=11, fill=BG, stroke="#cbd5e1", color=INK))

    f.append(fitbox(340, 185, 340, 70, "Валідація схем подій Kafka Outbox\nПеревірка монотонності versionSeq\nПеревірка обов'язкових метрик SLO", size=11, fill=BG, stroke="#cbd5e1", color=INK))

    f.append(fitbox(340, 270, 340, 60, "Автоматичний результат:\nPASS -> Merge / FAIL -> Блокування PR", size=11, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Гілки результату
    f.append(arrow(700, 300, 760, 300, color=GREEN, sw=2))

    # Блок 3: Runtime Monitoring & Drift Alerting
    f.append(rect(760, 60, 240, 320, fill="#fefce8", stroke="#eab308", rx=8, sw=1.5))
    f.append(fitbox(775, 75, 210, 45, "3. Runtime Drift Control\n(Prometheus / Grafana)", size=12, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))
    f.append(fitbox(775, 135, 210, 225, "Метрики в реальному часі:\n\n• twin_mismatch_total\n  (розбіжність v1 vs v2)\n\n• outbox_lag_seconds\n  (затримка інвалідації)\n\n• fitness_violations_total\n  (зафіксований дрейф)\n\nАвто-алерт при виході\nза межі SLO!", size=11, fill=BG, stroke="#fde047", color=INK))

    render(os.path.join(OUT, 'fitness-guard-pipeline.svg'), W, H, *f,
           title="Контур автоматизованого fitness-контролю ерозії архітектури")


if __name__ == '__main__':
    fig_v1_monolith_to_v2_geo()
    fig_migration_phases_reversibility()
    fig_fitness_guard_pipeline()
    print("All figures generated successfully.")
