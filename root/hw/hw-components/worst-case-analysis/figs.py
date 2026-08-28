# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. tolerance-stackup: структура сукупного допуску компонента ───────────────
def fig_tolerance_stackup():
    W, H = 840, 420
    p = []

    p.append(text(420, 28, "Анатомія сукупного допуску компонента (Tolerance Stackup)", size=15, color=INK, bold=True))
    p.append(text(420, 50, "Чотири незалежні фактори розширення смуги нестабільності резистора 10.0 кОм (±1%)", size=11, color=MUTED))

    # Візуальні блоки доданків допуску
    factors = [
        ("1. Заводський допуск", "Виготовлення при 25 °C", "±1.0 %", "±100 Ом", "#eef2ff", NEG, 75),
        ("2. Монтажна пайка", "Термоудар оплавлення припою", "±0.5 %", "±50 Ом", "#fff7ed", "#ea580c", 145),
        ("3. Температурний дрейф", "ΔT = 60 °C (TCR = ±100 ppm/°C)", "±0.6 %", "±60 Ом", "#fef2f2", POS, 215),
        ("4. Старіння та вологість", "10 000 год експлуатації", "±1.5 %", "±150 Ом", "#f0fdf4", FIELD, 285),
    ]

    for title, desc, pct, val, bg_col, stroke_col, y_pos in factors:
        p.append(rect(40, y_pos, 760, 56, fill=bg_col, stroke=stroke_col, sw=1.2, rx=6))
        p.append(text(60, y_pos + 24, title, size=12, color=INK, bold=True, anchor="start"))
        p.append(text(60, y_pos + 44, desc, size=10, color=MUTED, anchor="start"))
        p.append(text(560, y_pos + 33, pct, size=13, color=stroke_col, bold=True, anchor="end"))
        p.append(text(740, y_pos + 33, val, size=13, color=INK, bold=True, anchor="end"))

    # Підсумкова смуга
    p.append(rect(40, 355, 760, 52, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=6))
    p.append(text(60, 386, "Сукупний найгірший допуск (EVA найгірший випадок):", size=12, color="#ffffff", bold=True, anchor="start"))
    p.append(text(560, 386, "±3.6 %", size=15, color="#fca5a5", bold=True, anchor="end"))
    p.append(text(740, 386, "[9.64 кОм ... 10.36 кОм]", size=13, color="#38bdf8", bold=True, anchor="end"))

    render(os.path.join(OUT, "tolerance-stackup.svg"), W, H, *p)


# ── 2. eva-vs-rss-monte-carlo: порівняння трьох підходів WCCA ──────────────────
def fig_eva_rss_mc():
    W, H = 840, 460
    p = []

    p.append(text(420, 26, "Геометрія допусків: EVA vs RSS vs Monte Carlo", size=15, color=INK, bold=True))
    p.append(text(420, 48, "Двовимірний простір параметрів двох резисторів дільника напруги (R1 та R2)", size=11, color=MUTED))

    # Три панелі
    panels = [
        (40, "1. Метод EVA (Worst-Case)", "Прямокутник екстремумів", "#fef2f2", POS),
        (300, "2. Метод RSS (Statistical)", "Еліпс розсіювання 3σ (99.73%)", "#eef2ff", NEG),
        (560, "3. Монте-Карло (Simulation)", "Статистична хмара реальних плат", "#f0fdf4", FIELD),
    ]

    for x_base, p_title, p_sub, bg_col, stroke_col in panels:
        p.append(rect(x_base, 68, 240, 320, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6))
        p.append(rect(x_base, 68, 240, 48, fill=bg_col, stroke=stroke_col, sw=1, rx=6))
        p.append(text(x_base + 120, 88, p_title, size=11, color=INK, bold=True))
        p.append(text(x_base + 120, 106, p_sub, size=9, color=MUTED))

        # Координатні осі всередині панелі
        cx = x_base + 120
        cy = 240
        p.append(line(cx - 85, cy, cx + 85, cy, color="#cbd5e1", sw=1))
        p.append(line(cx, cy - 85, cx, cy + 85, color="#cbd5e1", sw=1))
        p.append(text(cx + 80, cy - 6, "ΔR1", size=9, color=MUTED, anchor="end"))
        p.append(text(cx + 6, cy - 75, "ΔR2", size=9, color=MUTED, anchor="start"))
        p.append(circle(cx, cy, 3, fill=INK))

    # Панель 1: EVA (Прямокутник допусків + кутові точки)
    cx1, cy1 = 160, 240
    p.append(rect(cx1 - 60, cy1 - 60, 120, 120, fill="#fee2e2", stroke=POS, sw=1.8, rx=2))
    # Кутові найгірші точки
    p.append(circle(cx1 - 60, cy1 + 60, 5, fill=POS))
    p.append(circle(cx1 + 60, cy1 - 60, 5, fill=POS))
    p.append(text(cx1 - 64, cy1 + 75, "Min Vout", size=9, color=POS, bold=True, anchor="end"))
    p.append(text(cx1 + 64, cy1 - 68, "Max Vout", size=9, color=POS, bold=True, anchor="start"))

    # Панель 2: RSS (Еліпс розсіювання 3σ всередині прямокутника)
    cx2, cy2 = 420, 240
    p.append(line(cx2 - 60, cy2 - 60, cx2 + 60, cy2 - 60, color="#94a3b8", sw=1, dash="3,3"))
    p.append(line(cx2 + 60, cy2 - 60, cx2 + 60, cy2 + 60, color="#94a3b8", sw=1, dash="3,3"))
    p.append(line(cx2 + 60, cy2 + 60, cx2 - 60, cy2 + 60, color="#94a3b8", sw=1, dash="3,3"))
    p.append(line(cx2 - 60, cy2 + 60, cx2 - 60, cy2 - 60, color="#94a3b8", sw=1, dash="3,3"))
    
    # Малюємо коло/еліпс 3σ
    p.append(circle(cx2, cy2, 54, fill="#dbeafe", stroke=NEG, sw=2))
    p.append(text(cx2, cy2 + 35, "Зона 3σ", size=10, color=NEG, bold=True))

    # Панель 3: Monte Carlo (Хмара точок)
    cx3, cy3 = 680, 240
    p.append(line(cx3 - 60, cy3 - 60, cx3 + 60, cy3 - 60, color="#94a3b8", sw=1, dash="3,3"))
    p.append(line(cx3 + 60, cy3 - 60, cx3 + 60, cy3 + 60, color="#94a3b8", sw=1, dash="3,3"))
    p.append(line(cx3 + 60, cy3 + 60, cx3 - 60, cy3 + 60, color="#94a3b8", sw=1, dash="3,3"))
    p.append(line(cx3 - 60, cy3 + 60, cx3 - 60, cy3 - 60, color="#94a3b8", sw=1, dash="3,3"))

    # Генеруємо хмару точок нормального розподілу
    for i in range(120):
        u1 = ((i * 37 + 13) % 100) / 100.0 + 0.001
        u2 = ((i * 59 + 41) % 100) / 100.0 + 0.001
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        z1 = math.sqrt(-2.0 * math.log(u1)) * math.sin(2.0 * math.pi * u2)
        px = cx3 + z0 * 18.0
        py = cy3 + z1 * 18.0
        if (px - cx3)**2 + (py - cy3)**2 < 58**2:
            p.append(circle(px, py, 1.8, fill=FIELD, stroke=FIELD))
        else:
            p.append(circle(px, py, 2.2, fill=POS, stroke=POS))

    # Нижнє порівняльне резюме
    p.append(rect(40, 400, 760, 48, fill=FILL, stroke=LINE, sw=1, rx=6))
    p.append(text(160, 429, "100% захист від браку, надлишковий запас", size=9.5, color=POS, bold=True))
    p.append(text(420, 429, "Ймовірність відмови < 0.27%, оптимальний баланс", size=9.5, color=NEG, bold=True))
    p.append(text(680, 429, "Точний розрахунок реального виходу придатних", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "eva-vs-rss-monte-carlo.svg"), W, H, *p)


# ── 3. sensitivity-divider: аналіз чутливості дільника напруги ─────────────────
def fig_sensitivity_divider():
    W, H = 840, 380
    p = []

    p.append(text(420, 26, "Аналіз чутливості (Sensitivity) резистивного дільника", size=15, color=INK, bold=True))
    p.append(text(420, 48, "Як парціальні похідні визначають напрямок найгіршого дрейфу вихідної напруги", size=11, color=MUTED))

    # Схема дільника зліва
    p.append(rect(40, 68, 320, 290, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6))
    p.append(text(200, 92, "Схема електрична принципова", size=12, color=INK, bold=True))

    # Провідники та компоненти дільника
    p.append(line(200, 115, 200, 140, color=LINE, sw=1.8))
    p.append(circle(200, 115, 3.5, fill=POS))
    p.append(text(200, 108, "Vin (номінал 5.0 В)", size=10, color=POS, bold=True))

    # Резистор R1
    p.append(rect(182, 140, 36, 48, fill="#f8fafc", stroke=LINE, sw=1.8, rx=2))
    p.append(text(200, 168, "R1", size=12, color=INK, bold=True))

    p.append(line(200, 188, 200, 232, color=LINE, sw=1.8))
    # Вузол Vout
    p.append(circle(200, 210, 4.5, fill=NEG))
    p.append(line(200, 210, 290, 210, color=NEG, sw=1.8))
    p.append(circle(290, 210, 3.5, fill=NEG))
    p.append(text(300, 214, "Vout", size=11, color=NEG, bold=True, anchor="start"))

    # Резистор R2
    p.append(rect(182, 232, 36, 48, fill="#f8fafc", stroke=LINE, sw=1.8, rx=2))
    p.append(text(200, 260, "R2", size=12, color=INK, bold=True))

    # Земля
    p.append(line(200, 280, 200, 310, color=LINE, sw=1.8))
    p.append(line(185, 310, 215, 310, color=LINE, sw=1.8))
    p.append(line(190, 316, 210, 316, color=LINE, sw=1.8))
    p.append(line(195, 322, 205, 322, color=LINE, sw=1.8))
    p.append(text(200, 338, "GND (0 В)", size=9, color=MUTED))

    # Права панель: Парціальні похідні та чутливість
    p.append(rect(380, 68, 420, 290, fill="#fafafa", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(590, 92, "Парціальні похідні та правила вибору меж", size=12, color=INK, bold=True))

    # Блок R1
    p.append(rect(395, 115, 390, 70, fill="#fef2f2", stroke=POS, sw=1, rx=4))
    p.append(text(410, 137, "Верхнє плече (R1): Від'ємна чутливість S(R1) < 0", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(410, 156, "∂Vout / ∂R1 = −Vin · R2 / (R1 + R2)² < 0", size=10, color=INK, anchor="start"))
    p.append(text(410, 173, "Збільшення R1 ЗМЕНШУЄ Vout  →  для Vout_min беремо R1_max", size=9.5, color=MUTED, anchor="start"))

    # Блок R2
    p.append(rect(395, 195, 390, 70, fill="#eef2ff", stroke=NEG, sw=1, rx=4))
    p.append(text(410, 217, "Нижнє плече (R2): Додатна чутливість S(R2) > 0", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(410, 236, "∂Vout / ∂R2 = +Vin · R1 / (R1 + R2)² > 0", size=10, color=INK, anchor="start"))
    p.append(text(410, 253, "Збільшення R2 ЗБІЛЬШУЄ Vout  →  для Vout_min беремо R2_min", size=9.5, color=MUTED, anchor="start"))

    # Правило EVA
    p.append(rect(395, 275, 390, 68, fill="#1e293b", stroke="#0f172a", sw=1, rx=4))
    p.append(text(410, 298, "Комбінація екстремумів для дільника:", size=11, color="#38bdf8", bold=True, anchor="start"))
    p.append(text(410, 317, "Vout_min  =  Vin_min · R2_min / (R1_max + R2_min)", size=10, color="#ffffff", anchor="start"))
    p.append(text(410, 334, "Vout_max  =  Vin_max · R2_max / (R1_min + R2_max)", size=10, color="#ffffff", anchor="start"))

    render(os.path.join(OUT, "sensitivity-divider.svg"), W, H, *p)


# ── 4. tracking-correlation: кореляція та узгоджені резисторні збірки ─────────
def fig_tracking_correlation():
    W, H = 840, 390
    p = []

    p.append(text(420, 26, "Вплив кореляції: дискретні резистори проти узгоджених збірок", size=15, color=INK, bold=True))
    p.append(text(420, 48, "Як спільний температурний коефіцієнт (TCR Tracking) знижує розкид дільника в 10 разів", size=11, color=MUTED))

    # Ліва колонка: Дискретні некорельовані резистори
    p.append(rect(40, 68, 365, 300, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(rect(40, 68, 365, 42, fill="#fef2f2", stroke=POS, sw=1, rx=6))
    p.append(text(222, 94, "Дискретні резистори (Некорельовані)", size=11, color=POS, bold=True))

    cx1, cy1 = 222, 215
    p.append(line(cx1 - 100, cy1, cx1 + 100, cy1, color="#cbd5e1", sw=1))
    p.append(line(cx1, cy1 - 85, cx1, cy1 + 85, color="#cbd5e1", sw=1))
    p.append(text(cx1 + 95, cy1 - 6, "ΔR1", size=9, color=MUTED, anchor="end"))
    p.append(text(cx1 + 6, cy1 - 75, "ΔR2", size=9, color=MUTED, anchor="start"))

    # Незалежний прямокутник / коло розсіювання
    p.append(line(cx1 - 65, cy1 - 65, cx1 + 65, cy1 - 65, color=POS, sw=1.2, dash="3,3"))
    p.append(line(cx1 + 65, cy1 - 65, cx1 + 65, cy1 + 65, color=POS, sw=1.2, dash="3,3"))
    p.append(line(cx1 + 65, cy1 + 65, cx1 - 65, cy1 + 65, color=POS, sw=1.2, dash="3,3"))
    p.append(line(cx1 - 65, cy1 + 65, cx1 - 65, cy1 - 65, color=POS, sw=1.2, dash="3,3"))

    p.append(circle(cx1, cy1, 58, fill="#fecaca", stroke=POS, sw=1.8))
    p.append(text(cx1, cy1 + 5, "Повний розкид дільника", size=10, color=POS, bold=True))
    p.append(text(cx1, 335, "TCR drift: Δ(R2/R1) до ±1.2 % (незалежні напрямки)", size=10, color=INK))
    p.append(text(cx1, 354, "R1 нагрівається на +600 ppm, R2 охолоджується на −600 ppm", size=10, color=MUTED))

    # Права колонка: Узгоджена резисторна збірка (Resistor Network)
    p.append(rect(435, 68, 365, 300, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(rect(435, 68, 365, 42, fill="#f0fdf4", stroke=FIELD, sw=1, rx=6))
    p.append(text(617, 94, "Монолітна збірка (TCR Tracking < 5 ppm/°C)", size=11, color=FIELD, bold=True))

    cx2, cy2 = 617, 215
    p.append(line(cx2 - 100, cy2, cx2 + 100, cy2, color="#cbd5e1", sw=1))
    p.append(line(cx2, cy2 - 85, cx2, cy2 + 85, color="#cbd5e1", sw=1))
    p.append(text(cx2 + 95, cy2 - 6, "ΔR1", size=9.5, color=MUTED, anchor="end"))
    p.append(text(cx2 + 6, cy2 - 75, "ΔR2", size=9.5, color=MUTED, anchor="start"))

    # Тонкий нахилений еліпс уздовж діагоналі y = x (корельований дрейф)
    p.append(line(cx2 - 75, cy2 - 75, cx2 + 75, cy2 + 75, color=FIELD, sw=1.2, dash="3,3"))
    
    # Контур кореляції
    pts_corr = []
    for deg in range(0, 365, 10):
        rad = math.radians(deg)
        x_rot = 72 * math.cos(rad) * math.cos(math.pi/4) - 14 * math.sin(rad) * math.sin(math.pi/4)
        y_rot = 72 * math.cos(rad) * math.sin(math.pi/4) + 14 * math.sin(rad) * math.cos(math.pi/4)
        pts_corr.append("%.1f,%.1f" % (cx2 + x_rot, cy2 + y_rot))
    
    p.append('<polygon points="%s" fill="#dcfce7" stroke="%s" stroke-width="2"/>' % (" ".join(pts_corr), FIELD))
    
    p.append(text(cx2 - 15, cy2 + 25, "Співвісний дрейф", size=10, color=FIELD, bold=True))
    p.append(text(cx2, 335, "TCR drift: Δ(R2/R1) < ±0.03 % (коефіцієнт стабільний)", size=10, color=FIELD, bold=True))
    p.append(text(cx2, 354, "Обидва резистори на одній підкладці дрейфують синхронно", size=10, color=MUTED))

    render(os.path.join(OUT, "tracking-correlation.svg"), W, H, *p)


if __name__ == "__main__":
    fig_tolerance_stackup()
    fig_eva_rss_mc()
    fig_sensitivity_divider()
    fig_tracking_correlation()
    print("All figures generated successfully.")
