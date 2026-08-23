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


def fig_driver_to_slo_transformation():
    """Трансформація від бізнес-драйвера (SEI сценарій) до SLI, SLO та бюджету помилок."""
    W, H = 1040, 420
    f = []

    # Крок 1: Якісний драйвер (SEI сценарій)
    f.append(fitbox(40, 50, 210, 40, "1. Якісний драйвер", size=13, bold=True, fill=NEUT, stroke=INK))
    f.append(fitbox(40, 100, 210, 260, 
                    "Сценарій SEI:\n\n• Стимул: команда «відчинити»\n• Джерело: мобільний застосунок\n• Середовище: нормальне\n• Відповідь: замок відчинено\n• Міра: ≤ 500 мс у 99.9% спроб",
                    size=12, fill=BG, stroke=INK))

    f.append(arrow(260, 230, 290, 230))

    # Крок 2: Індикатор SLI
    f.append(fitbox(300, 50, 210, 40, "2. Індикатор (SLI)", size=13, bold=True, fill=NEUT, stroke=INK))
    f.append(fitbox(300, 100, 210, 260,
                    "Формула SLI:\n\nSLI = Good / Total\n\n• Good: HTTP 200 AND\n  latency ≤ 500 ms\n• Total: усі валідні\n  виклики lock_service\n• Точка виміру: API Gateway",
                    size=12, fill=BLUE_T, stroke=NEG))

    f.append(arrow(520, 230, 550, 230))

    # Крок 3: Ціль SLO
    f.append(fitbox(560, 50, 210, 40, "3. Ціль (SLO)", size=13, bold=True, fill=NEUT, stroke=INK))
    f.append(fitbox(560, 100, 210, 260,
                    "Угода SLO:\n\n• SLO = 99.9%\n• Вікно: 30 днів (скользяче)\n• Траєкторія: не менше\n  99.9% вдало виконаних\n  команд за місяць",
                    size=12, fill=GREEN_T, stroke=FIELD))

    f.append(arrow(780, 230, 810, 230))

    # Крок 4: Бюджет помилок
    f.append(fitbox(820, 50, 180, 40, "4. Бюджет помилок", size=13, bold=True, fill=NEUT, stroke=INK))
    f.append(fitbox(820, 100, 180, 260,
                    "Error Budget:\n\n• Бюджет = 100% − SLO\n  = 0.1%\n• Дозволений збій:\n  ~43.2 хвилини / місяць\n• Арбітр релізів:\n  Dev vs Ops",
                    size=12, fill=AMBER_T, stroke=AMBER))

    # Підпис знизу
    f.append(fitbox(40, 375, 960, 35, 
                    "Безперервний ланцюг: Бізнес-мета  →  Подієвий вимір  →  Статистична ціль  →  Ресурс ризику",
                    size=13, bold=True, fill=NEUT, stroke=INK))

    render(os.path.join(OUT, 'fig1-driver-to-slo-transformation.svg'), W, H, *f,
           title="Трансформація якісного драйвера у бюджет помилок")


def fig_error_budget_policy_lifecycle():
    """Динаміка вигорання бюджету помилок протягом місяця та реакція Error Budget Policy."""
    W, H = 1040, 460
    f = []

    # Осі графіка
    ox, oy, gw, gh = 80, 320, 920, 240
    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=2)) # Ось X (Час)
    f.append(line(ox, oy, ox, oy - gh, color=INK, sw=2)) # Ось Y (Бюджет %)

    # Засічки на осі Y (100%, 50%, 0%)
    f.append(text(65, oy - gh + 10, "100%", size=12, color=MUTED, anchor="end"))
    f.append(text(65, oy - gh/2, "50%", size=12, color=MUTED, anchor="end"))
    f.append(text(65, oy, "0%", size=12, color=POS, anchor="end"))
    f.append(line(ox - 5, oy - gh + 5, ox + gw, oy - gh + 5, color="#e2e8f0", sw=1, dash="4 4"))
    f.append(line(ox - 5, oy - gh/2, ox + gw, oy - gh/2, color="#e2e8f0", sw=1, dash="4 4"))

    # Пунктирна лінія порогу нуля
    f.append(line(ox, oy, ox + gw, oy, color=POS, sw=2, dash="6 4"))

    # Лінія спалювання бюджету (через сегменти line)
    path_points = [
        (ox, oy - gh + 5),
        (ox + 200, oy - gh + 50),  # День 10: 80%
        (ox + 260, oy - gh + 210), # День 12: 15% (аварія!)
        (ox + 500, oy - gh + 220), # День 20: 10% (заморозка релізів)
        (ox + 700, oy - gh + 230), # День 25: 5%
        (ox + 900, oy - gh + 5),   # День 30: скидання вікна (100%)
    ]

    for i in range(len(path_points) - 1):
        x1, y1 = path_points[i]
        x2, y2 = path_points[i+1]
        f.append(line(x1, y1, x2, y2, color=NEG, sw=3.5))

    # Зони станів релізів
    f.append(rect(ox + 10, 40, 180, 32, fill=GREEN_T, stroke=FIELD, rx=4))
    f.append(text(ox + 100, 61, "Зелена зона: релізи дозволено", size=11, bold=True, color=FIELD))

    f.append(rect(ox + 210, 40, 180, 32, fill=AMBER_T, stroke=AMBER, rx=4))
    f.append(text(ox + 300, 61, "Аварія: Fast Burn Alert (14.4x)", size=11, bold=True, color=AMBER))

    f.append(rect(ox + 400, 40, 280, 32, fill=RED_T, stroke=POS, rx=4))
    f.append(text(ox + 540, 61, "Бюджет вичерпано: Freeze Policy (лише хотфікси)", size=11, bold=True, color=POS))

    f.append(rect(ox + 710, 40, 200, 32, fill=BLUE_T, stroke=NEG, rx=4))
    f.append(text(ox + 810, 61, "Скидання 30-денного вікна", size=11, bold=True, color=NEG))

    # Позначки днів по осі X
    days = [("День 1", ox), ("День 10", ox + 200), ("День 12", ox + 260), ("День 20", ox + 500), ("День 30", ox + 900)]
    for dlabel, dx in days:
        f.append(line(dx, oy, dx, oy + 6, color=INK, sw=1.5))
        f.append(text(dx, oy + 22, dlabel, size=11, color=MUTED))

    # Пояснювальний бокс знизу
    f.append(fitbox(40, 385, 960, 55, 
                    "Error Budget Policy: Коли бюджет залишається > 0, Dev має право випускати фічі. "
                    "При вичерпанні (бюджет ≤ 0) автоматично вмикається Freeze — усі сили йдуть на надійність та усунення боргу.",
                    size=12, fill=NEUT, stroke=INK))

    render(os.path.join(OUT, 'fig2-error-budget-policy-lifecycle.svg'), W, H, *f,
           title="Життєвий цикл бюджету помилок та політика релізів")


def fig_multi_window_burn_rate():
    """Багатовіконна логіка детекції Burn Rate (коротке вікно + довге вікно)."""
    W, H = 1040, 440
    f = []

    # Блок ліворуч: Довге вікно (1 година)
    f.append(fitbox(40, 60, 430, 200, "", fill=BLUE_T, stroke=NEG))
    f.append(text(255, 90, "Довге вікно (1 година) — Точність (Precision)", size=14, bold=True, color=NEG))
    f.append(fitbox(60, 110, 390, 130,
                    "• Оцінює обсяг втраченого бюджету\n• Вимога: втрачено ≥ 2% бюджету за 1 годину\n• Захищає від хибних тривог на мікро-сп сплесках\n• Помилка: повільно реагує на початок інциденту",
                    size=12, fill=BG, stroke=NEG))

    # Блок праворуч: Коротке вікно (5 хвилин)
    f.append(fitbox(570, 60, 430, 200, "", fill=AMBER_T, stroke=AMBER))
    f.append(text(785, 90, "Коротке вікно (5 хвилин) — Свіжість (Recency)", size=14, bold=True, color=AMBER))
    f.append(fitbox(590, 110, 390, 130,
                    "• Оцінює поточний стан системи прямо зараз\n• Вимога: burn rate становить ≥ 14.4x за 5 хвилин\n• Гарантує, що аварія триває прямо зараз\n• Захищає від алертів після того, як збій вщух",
                    size=12, fill=BG, stroke=AMBER))

    # Логічне AND посередні
    f.append(circle(500, 160, 32, fill=NEUT, stroke=INK, sw=2))
    f.append(text(500, 166, "AND", size=14, bold=True, color=INK))

    f.append(arrow(470, 160, 468, 160))
    f.append(arrow(532, 160, 568, 160))

    # Вихідний результат вниз (PagerAlert)
    f.append(arrow(500, 192, 500, 280))

    f.append(fitbox(320, 285, 360, 75,
                    "Критичний алерт (PagerDuty / On-Call)\n\nBurn Rate = 14.4x (2% бюджету за годину + збій триває)",
                    size=13, bold=True, fill=RED_T, stroke=POS))

    # Підпис
    f.append(fitbox(40, 385, 960, 40,
                    "Багатовіконний аналіз (Multi-Window Multi-Burn-Rate) виключає хибні тривоги при коротких сплесках та мовчки згаслих інцидентах.",
                    size=12, fill=NEUT, stroke=INK))

    render(os.path.join(OUT, 'fig3-multi-window-burn-rate.svg'), W, H, *f,
           title="Багатовіконна логіка детекції Burn Rate")


if __name__ == '__main__':
    fig_driver_to_slo_transformation()
    fig_error_budget_policy_lifecycle()
    fig_multi_window_burn_rate()
    print("figures written successfully")
