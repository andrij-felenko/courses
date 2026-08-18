# -*- coding: utf-8 -*-
"""Фігури до кроку «Від модульного моноліта до сервісів без розриву»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_migration_phases():
    """Чотири фази міграції від модульного моноліта до автоновного сервісу:
    1) Модульний моноліт → 2) Виділення шва та даних → 3) Strangler Fig & Dual Write → 4) Окремий сервіс."""
    W, H = 1200, 520
    frags = []

    # Заголовок / вісь
    y_box = 100
    w_box, h_box = 240, 320
    gap = 40
    x_starts = [60 + i * (w_box + gap) for i in range(4)]

    phases = [
        ("1. Модульний моноліт", "#eafaf0", FIELD, [
            "• Дев'ять модулів в 1 деплої",
            "• Прямі виклики в пам'яті",
            "• Спільна реляційна БД",
            "• Межі модулів зафіксовані"
        ]),
        ("2. Шви та ізоляція", "#eef2fb", NEG, [
            "• Branch by Abstraction в коді",
            "• Логічні схеми в БД (PostgreSQL)",
            "• Прибрано cross-domain JOINs",
            "• Доступ лише через інтерфейси"
        ]),
        ("3. Strangler & Canary", "#fff8e6", "#d97706", [
            "• API Gateway рутить 5% → 100%",
            "• Dual Write / CDC синхронізація",
            "• Shadow Reads для звірки",
            "• Старий модуль слугує fallback"
        ]),
        ("4. Автономний сервіс", "#fdecea", POS, [
            "• Сервіс розгорнуто автономно",
            "• Власна ізольована БД",
            "• Старий код вирізано з моноліта",
            "• Нуль прямих зв'язків"
        ]),
    ]

    for i, (title, fillc, strokec, bullets) in enumerate(phases):
        x = x_starts[i]
        # Картка фази
        frags.append(rect(x, y_box, w_box, h_box, fill=fillc, stroke=strokec, sw=2.0, rx=8))
        frags.append(text(x + w_box / 2, y_box + 30, title, size=13, color=INK, bold=True))
        frags.append(line(x + 15, y_box + 48, x + w_box - 15, y_box + 48, color=strokec, sw=1.2))

        # Кулі/текст всередині
        by = y_box + 75
        for btext in bullets:
            frags.append(text(x + 16, by, btext, size=11, color=INK, anchor="start"))
            by += 44

        # Стрілка переходу до наступної фази
        if i < 3:
            ax1 = x + w_box + 5
            ax2 = ax1 + gap - 10
            ay = y_box + h_box / 2
            frags.append(arrow(ax1, ay, ax2, ay, color=INK, sw=2.0))

    # Нижня рамка з висновком
    b, _, _ = textbox(600, 470,
                      "Ключовий принцип: кожна фаза зворотна, а перехід між ними відбувається без зупинки системи (Zero Downtime)",
                      size=12, fill=FILL, stroke=LINE, min_w=850)
    frags.append(b)

    render(os.path.join(IMG, "migration-phases.svg"), W, H, *frags,
           title="Чотири фази покрокової міграції від моноліта до мікросервісу")


def fig_data_decoupling_stages():
    """Етапи розділення даних:
    А) Спільна БД з JOINs → Б) Логічні схеми без FK → В) Подвійний запис/CDC → Г) Автономна БД per service."""
    W, H = 1240, 560
    frags = []

    # 4 блоки етапів
    stages = [
        ("А. Спільні таблиці", [
            "Модуль А  ──  Модуль Б",
            "       │      │",
            "       ▼      ▼",
            "   [Спільні JOIN / FK]",
            "   [ Таблиця Order/User ]"
        ], POS),
        ("Б. Логічні схеми", [
            "Схема А  │  Схема Б",
            " (User)  │  (Order)",
            "─────────┼─────────",
            "Прибрано FK та JOINs",
            "Доступ лише своєму коду"
        ], NEG),
        ("В. Dual Write / CDC", [
            "Модуль А ──CDC──► Сервіс Б",
            "  │                │",
            "  ▼                ▼",
            "  БД-Моноліт      БД-Сервісу",
            "Подвійне оновлення стану"
        ], "#d97706"),
        ("Г. Database-per-Service", [
            "Моноліт          Сервіс Б",
            "   │                │",
            "   ▼                ▼",
            " БД-Моноліт      БД-Сервіс Б",
            "Повна фізична ізоляція"
        ], FIELD)
    ]

    w_card = 265
    h_card = 340
    gap = 30
    x0 = 40

    for i, (stitle, slines, scolor) in enumerate(stages):
        x = x0 + i * (w_card + gap)
        y = 90

        frags.append(rect(x, y, w_card, h_card, fill="#ffffff", stroke=scolor, sw=2.0, rx=8))
        frags.append(rect(x, y, w_card, 42, fill=scolor, stroke=scolor, rx=0))
        frags.append(text(x + w_card / 2, y + 26, stitle, size=13, color="#ffffff", bold=True))

        ly = y + 75
        for line_txt in slines:
            frags.append(text(x + w_card / 2, ly, line_txt, size=11.5, color=INK))
            ly += 42

        if i < 3:
            frags.append(arrow(x + w_card + 4, y + h_card / 2, x + w_card + gap - 4, y + h_card / 2, color=MUTED, sw=1.8))

    b, _, _ = textbox(620, 490,
                      "Ізоляція даних є передумовою мережевого розколу: без розділення БД сервіси лишаються зв'язаними на рівні сховища",
                      size=12, fill="#f7f9fc", stroke=MUTED, min_w=900)
    frags.append(b)

    render(os.path.join(IMG, "data-decoupling-stages.svg"), W, H, *frags,
           title="Етапи безпечної ізоляції даних під час розпилу моноліта")


def fig_contract_test_gate():
    """Петля перевірки контрактних тестів (Consumer-Driven Contracts) між Споживачем і Провайдером в CI/CD."""
    W, H = 1180, 520
    frags = []

    # Клієнт / Споживач (Consumer)
    b, _, _ = textbox(250, 120, "Споживач (Consumer)\n(Застосунок / Сервіс A)", size=13,
                      fill="#eef2fb", stroke=NEG, bold=True, min_w=300)
    frags.append(b)

    # Провайдер (Provider)
    b, _, _ = textbox(930, 120, "Провайдер (Provider)\n(Новий мікросервіс B)", size=13,
                      fill="#fdecea", stroke=POS, bold=True, min_w=300)
    frags.append(b)

    # Крок 1: Генерація контракту
    frags.append(arrow(250, 170, 250, 250, color=NEG, sw=1.8))
    b, _, _ = textbox(250, 290, "1. Запуск unit-тестів Споживача\nГенерація файлу контракту (pact.json)",
                      size=11.5, fill=FILL, stroke=NEG, min_w=280)
    frags.append(b)

    # Крок 2: Публікація в Broker
    frags.append(arrow(390, 290, 520, 290, color=INK, sw=1.8))
    b, _, _ = textbox(590, 290, "Pact Broker / Registry\n(Збереження версій контрактів)",
                      size=12, fill="#fff8e6", stroke="#d97706", bold=True, min_w=240)
    frags.append(b)

    # Крок 3: Перевірка Провайдером
    frags.append(arrow(660, 290, 790, 290, color=INK, sw=1.8))
    b, _, _ = textbox(930, 290, "3. Провайдер відтворює запити\nі звіряє реальні відповіді з контрактом",
                      size=11.5, fill=FILL, stroke=POS, min_w=280)
    frags.append(b)

    # Крок 4: Фідбек у CI/CD
    frags.append(arrow(930, 340, 930, 420, color=POS, sw=1.8))
    b, _, _ = textbox(590, 440, "4. CI/CD Gate: зелене світло деплою лише при 100% сумісності контрактів",
                      size=12, fill="#eafaf0", stroke=FIELD, bold=True, min_w=620)
    frags.append(b)
    frags.append(arrow(790, 440, 680, 440, color=FIELD, sw=1.8))

    render(os.path.join(IMG, "contract-test-gate.svg"), W, H, *frags,
           title="Контрактні тести (CDC): перевірка сумісності API в CI/CD до виходу на прод")


if __name__ == "__main__":
    fig_migration_phases()
    fig_data_decoupling_stages()
    fig_contract_test_gate()
    print("OK: generated migration-phases.svg, data-decoupling-stages.svg, contract-test-gate.svg")
