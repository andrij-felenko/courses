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


def fig_rollback_asymmetry():
    """Асиметрія між прямим розгортанням та відкатом системи."""
    W, H = 1040, 430
    f = []

    # Заголовок
    f.append(fitbox(300, 35, 440, 38, "Асиметрія стану при розгортанні та відкаті",
                    size=16, bold=True, fill=NEUT, stroke=INK))

    # Верхня панель — Пряме розгортання (v1 -> v2)
    f.append(fitbox(40, 85, 460, 320, "", fill=BG, stroke=INK, sw=1.5))
    f.append(fitbox(60, 100, 420, 32, "1. Прямий деплой та створення нового стану",
                    size=14, bold=True, fill=BLUE_T, stroke=INK))

    f.append(fitbox(80, 150, 160, 60, "Код v1 (Старий)\nСхема v1", size=13, fill=NEUT, stroke=INK))
    f.append(arrow(240, 180, 280, 180, color=INK, sw=2))
    f.append(fitbox(280, 150, 200, 60, "Деплой v2 + DDL\nДодано нову колонку", size=13, fill=BLUE_T, stroke=INK))

    f.append(arrow(380, 210, 380, 245, color=INK, sw=2))
    f.append(fitbox(180, 245, 300, 65, "Живий трафік v2 вносить дані\nу нову колонку tax_id (Новий стан)",
                    size=12, fill=AMBER_T, stroke=AMBER))

    f.append(fitbox(80, 325, 400, 55, "Результат: Система перейшла в стан S2,\nякого не існувало під час розробки v1.",
                    size=12, fill=NEUT, color=MUTED, stroke="#d0d7de"))

    # Нижня панель — Наївний відкат (Сліпий Revert)
    f.append(fitbox(540, 85, 460, 320, "", fill=BG, stroke=NEG, sw=1.5, dash="6 4"))
    f.append(fitbox(560, 100, 420, 32, "2. Наївний відкат коду (Сліпий Revert)",
                    size=14, bold=True, fill=RED_T, color=NEG, stroke=NEG))

    f.append(fitbox(580, 150, 180, 60, "Сліпий відкат коду\nдо версії v1", size=13, fill=RED_T, stroke=NEG))
    f.append(arrow(760, 180, 800, 180, color=NEG, sw=2))
    f.append(fitbox(800, 150, 180, 60, "База в стані S2\nабо DROP COLUMN", size=13, fill=RED_T, stroke=NEG))

    f.append(fitbox(580, 230, 400, 70, "❌ АВАРІЯ ТА ВТРАТА ДАНИХ:\n• Старий код v1 падає (не знає схеми S2)\n• Або DROP COLUMN нищить нові дані tax_id",
                    size=12, fill=RED_T, stroke=NEG))

    f.append(fitbox(580, 315, 400, 65, "Висновок: Сліпий відкат коду без плану сумісності\nперетворює збій на незворотну катастрофу.",
                    size=12, fill=NEUT, color=NEG, stroke=NEG))

    render(os.path.join(OUT, 'rollback-asymmetry.svg'), W, H, *f,
           title="Асиметрія стану при розгортанні та відкаті")


def fig_reversible_migration_lifecycle():
    """Трифазний життєвий цикл зворотної міграції Expand-Contract."""
    W, H = 1040, 440
    f = []

    # Заголовок
    f.append(fitbox(280, 35, 480, 38, "Життєвий цикл зворотної міграції Expand-Contract",
                    size=16, bold=True, fill=NEUT, stroke=INK))

    # Фаза 1: Expand
    f.append(fitbox(40, 90, 300, 330, "", fill=BG, stroke=POS, sw=2))
    f.append(fitbox(55, 105, 270, 32, "Фаза 1: Expand (Розширення)", size=14, bold=True, fill=GREEN_T, color=POS, stroke=POS))
    f.append(fitbox(60, 150, 260, 110, "• Схема: DDL додає nullable нове поле\n• Код v1: працює зі старим полем\n• Код v2: пише в обоє полів (Dual-write)\n• Стан сумісності: 100%",
                    size=12, fill=NEUT, stroke=INK))
    f.append(fitbox(60, 275, 260, 65, "✅ БЕЗПЕЧНИЙ ВІДКАТ\nПросто відкочуємо код v2 -> v1.\nБаза залишається повністю сумісною.",
                    size=12, fill=GREEN_T, color=POS, stroke=POS))
    f.append(fitbox(60, 355, 260, 45, "Статус: Зворотна зміна", size=12, bold=True, fill=BG, anchor="middle"))

    # Фаза 2: Migrate / Backfill
    f.append(fitbox(370, 90, 300, 330, "", fill=BG, stroke=AMBER, sw=2))
    f.append(fitbox(385, 105, 270, 32, "Фаза 2: Backfill (Фоновий перенос)", size=14, bold=True, fill=AMBER_T, color=AMBER, stroke=AMBER))
    f.append(fitbox(390, 150, 260, 110, "• Перенос історичних даних батчами\n• Тригер/View дублює нові записи\n• Обидва коди (v1 та v2) працездатні\n• Перевірка повноти переносу",
                    size=12, fill=NEUT, stroke=INK))
    f.append(fitbox(390, 275, 260, 65, "⚡ ВІДКАТ З КОМПЕНСАЦІЄЮ\nКод v1 читає старе поле.\nПотрібен компенсаційний тригер.",
                    size=12, fill=AMBER_T, color=AMBER, stroke=AMBER))
    f.append(fitbox(390, 355, 260, 45, "Статус: Контрольований відкат", size=12, bold=True, fill=BG, anchor="middle"))

    # Фаза 3: Contract
    f.append(fitbox(700, 90, 300, 330, "", fill=BG, stroke=NEG, sw=2, dash="5 4"))
    f.append(fitbox(715, 105, 270, 32, "Фаза 3: Contract (Згортання)", size=14, bold=True, fill=RED_T, color=NEG, stroke=NEG))
    f.append(fitbox(720, 150, 260, 110, "• Видалення старого поля / тригера\n• Виконується ЛИШЕ після 100% v2\n• Старий код v1 повністю виведено\n• Повна очистка legacy",
                    size=12, fill=NEUT, stroke=INK))
    f.append(fitbox(720, 275, 260, 65, "⛔ ТОЧКА НЕПОВЕРНЕННЯ\nВідкат схеми більше неможливий.\nТільки Forward-Fix або бекап.",
                    size=12, fill=RED_T, color=NEG, stroke=NEG))
    f.append(fitbox(720, 355, 260, 45, "Статус: Незворотний крок", size=12, bold=True, fill=BG, anchor="middle"))

    # Стрілки переходу
    f.append(arrow(340, 250, 370, 250, color=INK, sw=3))
    f.append(arrow(670, 250, 700, 250, color=INK, sw=3))

    render(os.path.join(OUT, 'reversible-migration-lifecycle.svg'), W, H, *f,
           title="Життєвий цикл зворотної міграції Expand-Contract")


def fig_automated_rollback_controller():
    """Схема роботи автоматизованого контролера відкату та health gates."""
    W, H = 1040, 440
    f = []

    # Заголовок
    f.append(fitbox(260, 35, 520, 38, "Автоматизований контролер відкату та Health Gates",
                    size=16, bold=True, fill=NEUT, stroke=INK))

    # Складові системи
    # 1. Canary Deployer
    f.append(fitbox(40, 95, 260, 120, "Canary Deployment\n(5% -> 25% -> 100%)\nВерсія v2", size=13, fill=BLUE_T, stroke=INK))

    # 2. Telemetry & Metrics
    f.append(fitbox(390, 95, 260, 120, "Телеметрія & Telemetry Gate\n• P99 Latency < 150ms\n• 5xx Error Rate < 0.1%\n• Business Conversion > 99%", size=12, fill=NEUT, stroke=INK))

    # 3. Rollback Orchestrator
    f.append(fitbox(740, 95, 260, 120, "Rollback Orchestrator\n• Автоматичний аналіз метрик\n• Вікно оцінки (5 хв)\n• Оцінка безпеки схеми", size=12, fill=BLUE_T, stroke=INK))

    f.append(arrow(300, 155, 390, 155, color=INK, sw=2))
    f.append(arrow(650, 155, 740, 155, color=INK, sw=2))

    # Зв'язок від Orchestrator до блоків рішень
    f.append(arrow(870, 215, 870, 265, color=INK, sw=2))

    # Ніжні блоки
    # Пояснювальна примітка ліворуч (з розбитими коротшими рядками)
    f.append(fitbox(40, 270, 410, 135, "Принцип контролера:\nЖодна міграція не переходить\nу фазу Contract доти, доки\nконтролер не підтвердить\nстабільність v2 у вікні перевірки.",
                    size=12, fill=AMBER_T, color=AMBER, stroke=AMBER))

    # Гілка А — Все добре (середина)
    f.append(fitbox(480, 270, 240, 135, "✅ Метрики в нормі (OK)\n\n• Продовжити розгортання v2\n• Затвердити Expand-фазу\n• Запланувати Contract",
                    size=12, fill=GREEN_T, color=POS, stroke=POS))

    # Гілка Б — Аварія / Деградація (праворуч)
    f.append(fitbox(750, 270, 250, 135, "🚨 Деградація (SLO Breach)\n\n• АВТОМАТИЧНИЙ ВІДКАТ\n• Traffic switch back -> v1\n• Feature-Flag -> Off\n• Schema remains in Expand",
                    size=12, fill=RED_T, color=NEG, stroke=NEG))

    render(os.path.join(OUT, 'automated-rollback-controller.svg'), W, H, *f,
           title="Автоматизований контролер відкату та Health Gates")


if __name__ == '__main__':
    fig_rollback_asymmetry()
    fig_reversible_migration_lifecycle()
    fig_automated_rollback_controller()
    print("All figures generated successfully.")
