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


def fig_migration_four_strategies():
    """Порівняння 4 стратегій міграції: Big Bang, Strangler Fig, Dark Launching, Branch by Abstraction."""
    W, H = 1000, 480
    f = []

    # 1. Big Bang
    f.append(fitbox(40, 40, 440, 190, 
                    "1. Big Bang (Одномоментна заміна)\n\n• Одномоментне перемикання всього трафіку\n• Високий ризик, точка неповернення\n• Придатний лише для простіших або некритичних систем",
                    size=12, fill=RED_T, stroke=RED, color=RED))

    # 2. Strangler Fig Pattern
    f.append(fitbox(520, 40, 440, 190, 
                    "2. Strangler Fig (Поступове витіснення)\n\n• Огородження legacy через API Gateway / Proxy\n• Інкрементальне винесення методів та доменів\n• Безперервний продаж і прозорий rollback",
                    size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # 3. Dark Launching / Shadowing
    f.append(fitbox(40, 250, 440, 190, 
                    "3. Dark Launching / Shadowing (Тіньовий запуск)\n\n• Дублювання реального трафіку без впливу на UX\n• Порівняння відповідей (Diff Engine) під навантаженням\n• Ізоляція побічних ефектів (Write Isolation)",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))

    # 4. Branch by Abstraction
    f.append(fitbox(520, 250, 440, 190, 
                    "4. Branch by Abstraction (Гілкування в коді)\n\n• Внутрішній шов: інтерфейс-абстракція всередині коду\n• Перемикання реалізацій через Feature Flags\n• Видалення legacy після стабілізації",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    render(os.path.join(OUT, 'migration-four-strategies.svg'), W, H, *f,
           title="Порівняння чотирьох фундаментальних стратегій міграції систем")


def fig_strangler_and_shadow_flow():
    """Архітектурний потік Strangler Fig + Shadowing Router з CDC синхронізацією даних."""
    W, H = 1020, 440
    f = []

    # Клієнт
    f.append(fitbox(40, 180, 140, 80, "Клієнти DH\n(Mobile / Web / IoT)", size=12, bold=True, fill=NEUT, stroke=INK))
    f.append(arrow(180, 220, 240, 220, color=INK, sw=2))

    # API Proxy / Shadow Router
    f.append(fitbox(240, 140, 200, 160, 
                    "API Gateway &\nShadow Router\n\n• Live Traffic (80%)\n• Shadow Clone (100%)\n• Feature Flags",
                    size=12, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # Канали з Proxy:
    # 1. Live -> Legacy Monolith
    f.append(arrow(440, 180, 520, 110, color=RED, sw=2))
    # 2. Live -> New Microservice
    f.append(arrow(440, 220, 520, 220, color=GREEN, sw=2))
    # 3. Asynchronous Shadow Clone -> Diff Engine
    f.append(arrow(440, 260, 520, 330, color=BLUE, sw=2))

    # Блоки сервісів
    f.append(fitbox(520, 70, 220, 80, "Legacy Monolith\n(Пряма відповідь користувачу)", size=12, fill=RED_T, stroke=RED, color=RED))
    f.append(fitbox(520, 180, 220, 80, "New Microservice\n(Постіпенно витісняє legacy)", size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(fitbox(520, 290, 220, 80, "Diff Engine & Validator\n(Тіньове порівняння метрик)", size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))

    # Зв'язки до БД
    f.append(arrow(740, 110, 800, 110, color=RED, sw=1.5))
    f.append(arrow(740, 220, 800, 220, color=GREEN, sw=1.5))

    f.append(fitbox(790, 70, 190, 60, "Monolith DB\n(Primary State)", size=11, fill=NEUT, stroke=INK))
    f.append(fitbox(790, 200, 190, 60, "Service DB\n(New State)", size=11, fill=NEUT, stroke=INK))

    # CDC / Dual Write pipe
    f.append(arrow(940, 130, 940, 200, color=PURPLE, sw=2))
    f.append(fitbox(805, 150, 120, 30, "CDC (Debezium)", size=10, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    render(os.path.join(OUT, 'strangler-and-shadow-flow.svg'), W, H, *f,
           title="Архітектурний потік Strangler Fig разом із тіньовим порівнянням трафіку")


def fig_branch_by_abstraction_lifecycle():
    """Життєвий цикл Branch by Abstraction: 4 послідовні фази."""
    W, H = 1000, 420
    f = []

    # Фаза 1: Створення інтерфейсу
    f.append(fitbox(40, 40, 440, 160, 
                    "Фаза 1: Огородження інтерфейсом\n\n• Клієнтський код переводиться на Abstraction Interface\n• Єдина реалізація: Legacy Implementation\n• Нульова зміна поведінки в продакшні",
                    size=12, fill=NEUT, stroke=INK))

    # Фаза 2: Нова реалізація в коді
    f.append(fitbox(520, 40, 440, 160, 
                    "Фаза 2: Нова реалізація та Feature Flag\n\n• Додається New Implementation поруч зі старою\n• Динамічний перемикач (Feature Flag / Config)\n• Можливість канарейкового перемикання або shadowing",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))

    # Фаза 3: Повне перемикання
    f.append(fitbox(40, 230, 440, 160, 
                    "Фаза 3: Перемикання на нову систему\n\n• 100% трафіку іде через New Implementation\n• Стара реалізація залишається як fallback\n• Спостереження за метриками й стабільністю",
                    size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Фаза 4: Видалення legacy
    f.append(fitbox(520, 230, 440, 160, 
                    "Фаза 4: Зачистка кодової бази\n\n• Остаточне видалення Legacy Implementation\n• Очищення Feature Flag та конфігураторів\n• Код знову чистий, без слідів міграції",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    render(os.path.join(OUT, 'branch-by-abstraction-lifecycle.svg'), W, H, *f,
           title="Чотири фази життєвого циклу Branch by Abstraction")


if __name__ == '__main__':
    fig_migration_four_strategies()
    fig_strangler_and_shadow_flow()
    fig_branch_by_abstraction_lifecycle()
    print("Figures generated successfully.")
