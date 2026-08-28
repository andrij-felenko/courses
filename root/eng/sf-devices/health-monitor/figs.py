# -*- coding: utf-8 -*-
"""Фігури до теми «Монітор здоров'я пристрою» (health-monitor).
Запуск: python figs.py  → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

BORDER = "#d1d5db"
ACCENT = "#2457d6"
GOLD = "#b78103"
WARN_BG = "#fff9e6"
ERR_BG = "#fdecea"
OK_BG = "#f3faf4"

# ── 1. Конвеєр збору, агрегації метрик здоров'я та ухвалення рішень ──────────
def fig_health_metrics_pipeline():
    W, H = 940, 520
    f = []

    # Заголовок / фонова панель конвеєра
    f.append(rect(15, 15, W - 30, H - 30, rx=8, fill="#fafbfc", stroke=BORDER, sw=1.2))
    f.append(text(W // 2, 42, "Конвеєр супервізора: від сирих апаратних подій до інтегрального індексу здоров'я",
                  size=14, bold=True, color=INK))

    # Стовпець 1: Джерела метрик (Physical & RTOS Signals)
    f.append(text(125, 78, "1. Джерела сигналів", size=12, bold=True, color=ACCENT))
    
    src_items = [
        ("Апаратний рівень\n(IWDG / WWDG / EWI)", "#eef6fc", NEG),
        ("Підсистема живлення\n(PVD / BOR / Ripple ADC)", WARN_BG, GOLD),
        ("Планувальник RTOS\n(Stack Watermark / Jitter)", OK_BG, FIELD),
        ("Периферійні шини\n(I2C lock / CAN Bus-off)", ERR_BG, POS),
        ("Фізичний знос\n(Flash cycles / Relay ESR)", "#f5f0fa", "#6c3483")
    ]
    
    y_start = 100
    box_h = 58
    gap = 22
    for i, (label, bg, stroke_col) in enumerate(src_items):
        y = y_start + i * (box_h + gap)
        b = fitbox(25, y, 200, box_h, label, size=10.5, fill=bg, stroke=stroke_col, sw=1.4)
        f.append(b)
        # Стрілка праворуч до блоку нормалізації
        f.append(arrow(225, y + box_h // 2, 285, y + box_h // 2, color=MUTED, sw=1.5))

    # Стовпець 2: Нормалізація та фільтрація (Normalization & EWMA)
    f.append(text(390, 78, "2. Нормалізація та згладжування", size=12, bold=True, color=ACCENT))

    norm_items = [
        ("Приведення до цілочисельного\nіндексу [0 ... 1000] (Fixed-Point)", "#ffffff", BORDER),
        ("Ковзне експоненційне вікно\nEWMA: H[k] = α·x[k] + (1-α)·H[k-1]", "#ffffff", BORDER),
        ("Виявлення спалахів та трендів\n(Burst / Drift Detection)", "#ffffff", BORDER),
        ("Динамічний дебаунсинг\n(Фільтрація завад N з M)", "#ffffff", BORDER)
    ]
    
    for i, (label, bg, stroke_col) in enumerate(norm_items):
        y = 115 + i * (box_h + 38)
        b = fitbox(285, y, 210, box_h, label, size=10.5, fill=bg, stroke=stroke_col, sw=1.3)
        f.append(b)
        # Стрілка праворуч до матриці вагових коефіцієнтів
        f.append(arrow(495, y + box_h // 2, 555, 270, color=MUTED, sw=1.4))

    # Стовпець 3: Матриця ваг та штрафна функція
    f.append(text(650, 78, "3. Розрахунок Health Score", size=12, bold=True, color=ACCENT))
    
    calc_box = fitbox(555, 140, 190, 260,
                      "Вагова матриця W_i\n"
                      "та нелінійний штраф:\n\n"
                      "Score = Σ (w_i · h_i)\n"
                      "× Penalty_critical\n\n"
                      "Критичний вузол = 0\n"
                      "→ Системний Score = 0\n\n"
                      "Детекція деградації\n"
                      "та оцінка залишку MTBF",
                      size=10.5, fill="#f8f9fa", stroke=ACCENT, sw=1.8)
    f.append(calc_box)

    # Стрілка від розрахунку до шару ескалації
    f.append(arrow(745, 270, 785, 270, color=ACCENT, sw=2.2))

    # Стовпець 4: Шар дій та ескалації
    f.append(text(855, 78, "4. Дії супервізора", size=12, bold=True, color=ACCENT))

    act_items = [
        ("Nominal (900-1000)\nГодівля Watchdog", OK_BG, FIELD),
        ("Degraded (700-899)\nЛог + Warning flags", WARN_BG, GOLD),
        ("Critical (400-699)\nFailover резерву / I2C reset", "#fff0ea", "#d35400"),
        ("Emergency (< 400)\nSafe State + NMI + Dump", ERR_BG, POS)
    ]
    
    for i, (label, bg, stroke_col) in enumerate(act_items):
        y = 100 + i * (box_h + gap)
        b = fitbox(785, y, 140, box_h, label, size=10, fill=bg, stroke=stroke_col, sw=1.5)
        f.append(b)

    return render(os.path.join(IMG, "health-metrics-pipeline.svg"), W, H, *f,
                  title="Конвеєр збору, агрегації метрик здоров'я та ухвалення рішень супервізором")


# ── 2. Діаграма ескалації аварійних реакцій супервізора ──────────────────────
def fig_emergency_escalation():
    W, H = 960, 530
    f = []

    # Фонова панель
    f.append(rect(15, 15, W - 30, H - 30, rx=8, fill="#ffffff", stroke=BORDER, sw=1.2))
    f.append(text(W // 2, 42, "Кінцевий автомат ескалації та захисні реакції при деградації пристрою",
                  size=14, bold=True, color=INK))

    # Чотири основні стани
    states = [
        ("HEALTH_NOMINAL\n(Score: 900 ... 1000)", 40, 100, 195, 90, OK_BG, FIELD,
         "Усі підсистеми в нормі.\nПеріодична годівля IWDG/WWDG.\nТелеметрія штатна."),
        
        ("HEALTH_DEGRADED\n(Score: 700 ... 899)", 270, 100, 195, 90, WARN_BG, GOLD,
         "Некритичні помилки шин, джиттер.\nПідняття Warning Flags.\nЗниження частоти оновлення."),
        
        ("HEALTH_CRITICAL\n(Score: 400 ... 699)", 500, 100, 195, 90, "#fff0ea", "#d35400",
         "Відмова сенсора чи шини.\nПеремикання на резервний канал.\nАпаратне розблокування шин."),
        
        ("HEALTH_EMERGENCY\n(Score: 0 ... 399)", 730, 100, 195, 90, ERR_BG, POS,
         "Критична відмова безпеки.\nЗнеструмлення силових ключів.\nЗапис Blackbox та NMI/Reset.")
    ]

    for title, x, y, w, h, bg, stroke_col, desc in states:
        box = fitbox(x, y, w, h, title, size=11, bold=True, fill=bg, stroke=stroke_col, sw=1.8)
        f.append(box)
        # Опис під блоком
        desc_box = fitbox(x, y + h + 15, w, 115, desc, size=10, fill="#fafbfc", stroke=BORDER, sw=1.0)
        f.append(desc_box)

    # Переходи між станами
    # NOMINAL -> DEGRADED
    f.append(arrow(235, 125, 270, 125, color=GOLD, sw=1.8))
    f.append(text(252, 115, "збій", size=9.5, color=GOLD, bold=True))

    # DEGRADED -> NOMINAL (відновлення)
    f.append(arrow(270, 165, 235, 165, color=FIELD, sw=1.6))
    f.append(text(252, 180, "відновлення", size=9.5, color=FIELD, bold=True))

    # DEGRADED -> CRITICAL
    f.append(arrow(465, 125, 500, 125, color="#d35400", sw=1.8))
    f.append(text(482, 115, "відмова", size=9.5, color="#d35400", bold=True))

    # CRITICAL -> DEGRADED (після відновлення)
    f.append(arrow(500, 165, 465, 165, color=GOLD, sw=1.6))
    f.append(text(482, 180, "failover OK", size=9.5, color=GOLD, bold=True))

    # CRITICAL -> EMERGENCY
    f.append(arrow(695, 125, 730, 125, color=POS, sw=2.0))
    f.append(text(712, 115, "колапс", size=9.5, color=POS, bold=True))

    # Нижня панель: аварійний бар'єр та ланцюжок захисних реакцій (Safety Interlocks)
    f.append(rect(35, 350, W - 70, 145, rx=6, fill="#fdfefe", stroke=ACCENT, sw=1.4))
    f.append(text(W // 2, 375, "Аварійний ланцюг реакцій при переході в стан EMERGENCY (Fail-Safe Action Plan)",
                  size=12, bold=True, color=ACCENT))

    chain_steps = [
        ("1. Апаратний Interlock\nВимкнення ШІМ / Реле", 50, 400, 190, 70, ERR_BG, POS),
        ("2. Фіксація Blackbox\nДамп стека, CFSR, ADC у FRAM", 275, 400, 195, 70, "#f8f9fa", INK),
        ("3. Ескалація на NMI\nВиклик обробника тривоги", 505, 400, 190, 70, "#fff0ea", "#d35400"),
        ("4. Контрольований скид\nПерезапуск через IWDG / NVIC", 730, 400, 190, 70, "#eef6fc", FIELD)
    ]

    for label, cx, cy, cw, ch, cbg, cstroke in chain_steps:
        box = fitbox(cx, cy, cw, ch, label, size=10, fill=cbg, stroke=cstroke, sw=1.3)
        f.append(box)

    f.append(arrow(240, 435, 275, 435, color=MUTED, sw=1.5))
    f.append(arrow(470, 435, 505, 435, color=MUTED, sw=1.5))
    f.append(arrow(695, 435, 730, 435, color=MUTED, sw=1.5))

    return render(os.path.join(IMG, "emergency-escalation.svg"), W, H, *f,
                  title="Ієрархія ескалації та кінцевий автомат аварійних реакцій супервізора")


if __name__ == "__main__":
    fig_health_metrics_pipeline()
    fig_emergency_escalation()
    print("OK: generated 2 SVGs in img/")
