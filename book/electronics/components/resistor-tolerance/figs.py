# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. e-series-log-spacing: логарифмічний крок та перекриття допусків ────────
def fig_e_series():
    W, H = 820, 440
    p = []
    
    # Заголовок і підзаголовок
    p.append(text(410, 26, "Логарифмічний розподіл номіналів та зон допуску (IEC 60063)", size=14, color=INK, bold=True))
    p.append(text(410, 48, "Геометрична прогресія q = 10^(1/n) забезпечує однакове відносне перекриття на всій декаді", size=10, color=MUTED))

    # Логарифмічна шкала від 1.0 до 10.0
    x_left = 130
    x_right = 770
    scale_w = x_right - x_left

    def log_pos(val):
        return x_left + (math.log10(val) / 1.0) * scale_w

    # Рядки шкали: E6, E12, E24
    rows = [
        ("E6 (±20%)", [1.0, 1.5, 2.2, 3.3, 4.7, 6.8], 0.20, 110, "#fdecec", POS),
        ("E12 (±10%)", [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2], 0.10, 200, "#fff4e5", "#d97706"),
        ("E24 (±5%)", [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1], 0.05, 290, "#eef6ef", FIELD)
    ]

    for name, vals, tol, y_base, bg_col, stroke_col in rows:
        # Фон для ряду
        p.append(rect(20, y_base - 32, 780, 72, fill="#fafafa", stroke="#e5e7eb", sw=1, rx=6))
        p.append(text(72, y_base + 6, name, size=11, color=INK, bold=True))
        
        # Вісь
        p.append(line(x_left, y_base + 10, x_right, y_base + 10, color="#9ca3af", sw=1))

        # Смуги допуску
        for i, v in enumerate(vals):
            v_min = v * (1.0 - tol)
            v_max = v * (1.0 + tol)
            x_min = max(x_left, log_pos(v_min))
            x_max = min(x_right, log_pos(v_max))
            w_band = max(3.0, x_max - x_min)
            
            # Для E24 розносимо по висоті в 2 яруси, щоб смуги допуску не перетиналися
            if len(vals) > 15:
                y_rect = (y_base - 20) if (i % 2 == 0) else (y_base - 7)
                h_rect = 13
            else:
                y_rect = y_base - 16
                h_rect = 22

            p.append(rect(x_min, y_rect, w_band, h_rect, fill=bg_col, stroke=stroke_col, sw=1, rx=2))
            
            # Центральна риска номіналу
            cx = log_pos(v)
            p.append(line(cx, y_base - 18, cx, y_base + 12, color=stroke_col, sw=1.5))
            
            # Підпис номіналів
            if len(vals) == 6:  # E6
                p.append(text(cx, y_base + 26, "%.1f" % v if v != 1.0 else "1.0", size=9, color=INK))
            elif len(vals) == 12:  # E12
                p.append(text(cx, y_base + 26, "%.1f" % v if v != 1.0 else "1.0", size=9, color=INK))
            elif v in [1.0, 1.5, 2.2, 3.3, 4.7, 6.8]:  # E24 ключові
                p.append(text(cx, y_base + 26, "%.1f" % v if v != 1.0 else "1.0", size=9, color=INK))

    # Нижнє пояснення
    p.append(rect(20, 370, 780, 50, fill=FILL, stroke=LINE, sw=1, rx=6))
    p.append(text(410, 391, "Крок ряду E(n):  q = 10^(1/n).  Умова стику:  (1 + tol) / (1 − tol) ≈ q", size=10, color=INK, bold=True))
    p.append(text(410, 408, "Сусідні смуги допусків стикаються без прогалин: верхня межа R[k] збігається з нижньою межею R[k+1]", size=9, color=MUTED))

    render(os.path.join(OUT, "e-series-log-spacing.svg"), W, H, *p)


# ── 2. binning-distribution-trap: пастка сортування (binned distribution) ─────
def fig_binning_trap():
    W, H = 780, 400
    p = []
    
    p.append(text(390, 26, "Пастка технологічного сортування (Binning)", size=14, color=INK, bold=True))
    p.append(text(390, 48, "Чому реальний розподіл дешевих резисторів ±5% має провал у центрі", size=10, color=MUTED))

    # Лівий графік: Початкова партія після напилення (Гаусів дзвін)
    p.append(rect(25, 65, 345, 255, fill="#fafafa", stroke="#d1d5db", sw=1.2, rx=6))
    p.append(text(197, 88, "Початкова партія після виробництва", size=11, color=INK, bold=True))
    p.append(text(197, 106, "Природний нормальний розподіл", size=9, color=MUTED))

    # Гаусова крива
    pts_bell = []
    for i in range(101):
        x = 55 + i * 2.8
        t = (i - 50) / 16.0
        y = 250 - 120 * math.exp(-0.5 * t * t)
        pts_bell.append("%.1f,%.1f" % (x, y))
    
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_bell), NEG))
    
    # Заливка кривої
    pts_fill = ["55,250"] + pts_bell + ["335,250"]
    p.append('<polygon points="%s" fill="#eaf0fd" opacity="0.6"/>' % (" ".join(pts_fill)))
    
    # Виділення центральної зони (±1%)
    p.append(rect(167, 130, 60, 120, fill="#fdecec", stroke=POS, sw=1.2))
    p.append(text(197, 175, "Відбір ±1%", size=9, color=POS, bold=True))
    p.append(text(197, 195, "(продаж дорожче)", size=9, color=POS))
    
    # Вісь
    p.append(line(45, 250, 350, 250, color=LINE, sw=1.5))
    p.append(text(197, 275, "Номінал R₀", size=10, color=INK, bold=True))
    p.append(text(80, 275, "−5%", size=9, color=MUTED))
    p.append(text(315, 275, "+5%", size=9, color=MUTED))

    # Стрілка переносу
    p.append(arrow(380, 185, 400, 185, color=POS, sw=2))

    # Правий графік: Залишок партії (продається як ±5%)
    p.append(rect(410, 65, 345, 255, fill="#fafafa", stroke="#d1d5db", sw=1.2, rx=6))
    p.append(text(582, 88, "Залишок у продажу як «±5%»", size=11, color=POS, bold=True))
    p.append(text(582, 106, "Двогорбий розподіл із «вирізаним серцем»", size=9, color=MUTED))

    # Двогорба крива (з вирізаним центром)
    pts_left = []
    for i in range(41):
        x = 440 + i * 2.7
        t = (i - 48) / 16.0
        y = 250 - 120 * math.exp(-0.5 * t * t)
        pts_left.append("%.1f,%.1f" % (x, y))
    
    pts_right = []
    for i in range(60, 101):
        x = 440 + i * 2.7
        t = (i - 52) / 16.0
        y = 250 - 120 * math.exp(-0.5 * t * t)
        pts_right.append("%.1f,%.1f" % (x, y))

    pts_l_poly = ["440,250"] + pts_left + ["548,250"]
    pts_r_poly = ["602,250"] + pts_right + ["710,250"]
    p.append('<polygon points="%s" fill="#fdecec" opacity="0.7"/>' % (" ".join(pts_l_poly)))
    p.append('<polygon points="%s" fill="#fdecec" opacity="0.7"/>' % (" ".join(pts_r_poly)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_left), POS))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_right), POS))

    # Вісь праворуч
    p.append(line(430, 250, 735, 250, color=LINE, sw=1.5))
    p.append(text(582, 275, "Номінал R₀ (порожньо)", size=10, color=POS, bold=True))
    p.append(text(465, 275, "−5% .. −1%", size=9, color=MUTED))
    p.append(text(695, 275, "+1% .. +5%", size=9, color=MUTED))
    p.append(text(582, 200, "Діра замість R₀", size=9, color=POS, italic=True))

    # Нижній висновок
    p.append(rect(25, 335, 730, 50, fill=FILL, stroke=LINE, sw=1, rx=6))
    p.append(text(390, 355, "Практичний наслідок: модель Гауса для дешевих компонентів не працює.", size=10, color=INK, bold=True))
    p.append(text(390, 372, "У партії ±5% ймовірність зустріти резистор з точним опором R₀ близька до нуля.", size=9, color=MUTED))

    render(os.path.join(OUT, "binning-distribution-trap.svg"), W, H, *p)


# ── 3. tcr-curves-tech: температурний коефіцієнт (TCR) за технологіями ────────
def fig_tcr_curves():
    W, H = 780, 420
    p = []
    
    p.append(text(390, 26, "Температурний дрейф опору (TCR) для різних технологій", size=14, color=INK, bold=True))
    p.append(text(390, 48, "Відносне відхилення ΔR/R (%) у діапазоні від −55 °C до +125 °C (базова точка 25 °C)", size=10, color=MUTED))

    # Сітка координат
    x0, y0 = 95, 230
    w_grid, h_grid = 420, 260
    
    p.append(rect(x0, y0 - 130, w_grid, h_grid, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))

    # Горизонтальні лінії (% відхилення)
    for dy, lbl in [(-100, "+5.0%"), (-60, "+3.0%"), (-20, "+1.0%"), (0, "0.0%"), (20, "−1.0%"), (60, "−3.0%"), (100, "−5.0%")]:
        y = y0 + dy
        p.append(line(x0, y, x0 + w_grid, y, color="#e5e7eb" if dy != 0 else "#9ca3af", sw=1 if dy != 0 else 1.5))
        p.append(text(x0 - 25, y + 4, lbl, size=9, color=MUTED, anchor="end"))

    # Вертикальні лінії (температура)
    for dx, lbl in [(0, "−55°C"), (70, "0°C"), (120, "+25°C"), (220, "+75°C"), (320, "+125°C"), (380, "+155°C")]:
        x = x0 + dx
        p.append(line(x, y0 - 130, x, y0 + 130, color="#e5e7eb" if lbl != "+25°C" else "#9ca3af", sw=1 if lbl != "+25°C" else 1.5))
        p.append(text(x, y0 + 145, lbl, size=9, color=MUTED))

    # 1. Carbon Composition / Film
    pts_carb = []
    for t_deg in range(-55, 156, 5):
        dx = 70 + t_deg * (200.0 / 100.0)
        dt = t_deg - 25
        dr_pct = -0.05 * dt - 0.00015 * dt * dt
        y = y0 - dr_pct * 20.0
        if y0 - 128 <= y <= y0 + 128 and x0 <= x0 + dx <= x0 + w_grid:
            pts_carb.append("%.1f,%.1f" % (x0 + dx, y))
    p.append('<polyline points="%s" fill="none" stroke="#9333ea" stroke-width="2.2"/>' % (" ".join(pts_carb)))

    # 2. Thick Film
    pts_thick = []
    for t_deg in range(-55, 156, 5):
        dx = 70 + t_deg * 2.0
        dt = t_deg - 25
        dr_pct = 0.015 * dt + 0.00005 * dt * dt
        y = y0 - dr_pct * 20.0
        pts_thick.append("%.1f,%.1f" % (x0 + dx, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_thick), POS))

    # 3. Thin Film NiCr
    pts_thin = []
    for t_deg in range(-55, 156, 5):
        dx = 70 + t_deg * 2.0
        dt = t_deg - 25
        dr_pct = 0.002 * dt
        y = y0 - dr_pct * 20.0
        pts_thin.append("%.1f,%.1f" % (x0 + dx, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_thin), NEG))

    # 4. Bulk Metal Foil
    pts_foil = []
    for t_deg in range(-55, 156, 5):
        dx = 70 + t_deg * 2.0
        dt = t_deg - 25
        dr_pct = -0.000015 * (dt ** 2)
        y = y0 - dr_pct * 20.0
        pts_foil.append("%.1f,%.1f" % (x0 + dx, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_foil), FIELD))

    # Легенда праворуч
    lx, ly = 535, 100
    p.append(rect(lx, ly, 220, 260, fill="#fafafa", stroke="#d1d5db", sw=1, rx=6))
    p.append(text(lx + 110, ly + 24, "Технології резисторів", size=11, color=INK, bold=True))

    leg_items = [
        ("Вуглецеві плівки", "TCR: −500..−1000 ppm/°C", "#9333ea"),
        ("Товстоплівкові (Thick)", "TCR: ±100..±200 ppm/°C", POS),
        ("Тонкоплівкові (Thin)", "TCR: ±10..±25 ppm/°C", NEG),
        ("Фольгові (Metal Foil)", "TCR: ±0.2..±2 ppm/°C", FIELD)
    ]
    
    y_leg = ly + 50
    for title_t, sub_t, col in leg_items:
        p.append(line(lx + 14, y_leg + 8, lx + 38, y_leg + 8, color=col, sw=3))
        p.append(text(lx + 46, y_leg + 6, title_t, size=10, color=INK, anchor="start", bold=True))
        p.append(text(lx + 46, y_leg + 24, sub_t, size=9, color=MUTED, anchor="start"))
        y_leg += 50

    # Нижній підпис
    p.append(rect(95, 375, 660, 32, fill=FILL, stroke=LINE, sw=1, rx=4))
    p.append(text(425, 395, "Формула дрейфу:  ΔR = R₀ · TCR · (T − 25 °C).  100 ppm/°C при ΔT = 50 °C дає похибку 0.5%", size=9, color=INK))

    render(os.path.join(OUT, "tcr-curves-tech.svg"), W, H, *p)


# ── 4. drift-budget-timeline: сукупний бюджет похибки ─────────────────────────
def fig_drift_budget():
    W, H = 800, 420
    p = []
    
    p.append(text(400, 26, "Сукупний бюджет похибки резистора (Total Life Drift)", size=14, color=INK, bold=True))
    p.append(text(400, 48, "Як початковий резистор ±1.0% перетворюється на ±3.7% у реальному виробі", size=10, color=MUTED))

    factors = [
        ("Початковий допуск", "Виробничий розкид 25°C", 1.0, "#3b82f6"),
        ("Монтажна пайка", "Термоудар 260°C", 0.5, "#8b5cf6"),
        ("Температурний дрейф", "TCR 100ppm, ΔT=50°C", 0.5, "#ec4899"),
        ("Старіння (1000 год)", "Load life @ 70°C", 1.0, "#f59e0b"),
        ("Вплив вологості", "85°C / 85% RH", 0.5, "#10b981"),
        ("Напруговий дрейф", "VCR коефіцієнт", 0.2, "#6b7280")
    ]

    x_start = 45
    y_base = 280
    bar_w = 88
    gap = 18

    total_drift = 0.0
    for i, (name, desc, val, col) in enumerate(factors):
        x = x_start + i * (bar_w + gap)
        h_bar = val * 55.0
        y = y_base - h_bar
        
        # Стовпчик фактора
        p.append(rect(x, y, bar_w, h_bar, fill=col, stroke=LINE, sw=1.2, rx=4))
        p.append(text(x + bar_w / 2, y - 8, "+%.1f%%" % val, size=11, color=INK, bold=True))
        
        # Назва під віссю (багаторядкова)
        p.append(fitbox(x - 4, y_base + 10, bar_w + 8, 50, name + "\n" + ("(±%.1f%%)" % val), size=9, bold=True, fill="#fafafa", stroke="#e5e7eb"))
        total_drift += val

    # Підсумковий стовпчик (Worst-case Total)
    x_tot = x_start + len(factors) * (bar_w + gap) + 12
    h_tot = total_drift * 55.0
    y_tot = y_base - h_tot
    p.append(rect(x_tot, y_tot, bar_w + 10, h_tot, fill="#fdecec", stroke=POS, sw=2, rx=4))
    p.append(text(x_tot + (bar_w + 10) / 2, y_tot - 8, "±%.1f%%" % total_drift, size=12, color=POS, bold=True))
    p.append(fitbox(x_tot - 2, y_base + 10, bar_w + 14, 50, "ПОВНИЙ ДРЕЙФ\nWorst-Case", size=9, color=POS, bold=True, fill="#fdecec", stroke=POS))

    # Вісь
    p.append(line(25, y_base, 775, y_base, color=LINE, sw=1.5))

    # Нижній висновок
    p.append(rect(25, 370, 750, 36, fill=FILL, stroke=LINE, sw=1, rx=6))
    p.append(text(400, 392, "Інженерне правило: Total Life Drift зазвичай у 3–4 рази перевищує початковий допуск.", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "drift-budget-timeline.svg"), W, H, *p)


# ── 5. wca-vs-rss-monte-carlo: методи аналізу розкиду ─────────────────────────
def fig_wca_vs_rss():
    W, H = 780, 400
    p = []
    
    p.append(text(390, 26, "Методи аналізу розкиду: Worst-Case проти RSS та Monte Carlo", size=14, color=INK, bold=True))
    p.append(text(390, 48, "Порівняння оцінки меж похибки для аналогових дільників напруги", size=10, color=MUTED))

    # 1. WCA (Worst-Case Analysis)
    p.append(rect(25, 68, 225, 245, fill="#fafafa", stroke="#d1d5db", sw=1.2, rx=6))
    p.append(text(137, 90, "1. Worst-Case (WCA)", size=11, color=POS, bold=True))
    p.append(text(137, 108, "Найгірший крайній випадок", size=9, color=MUTED))
    
    p.append(rect(45, 125, 185, 110, fill="#fdecec", stroke=POS, sw=1.5, rx=4))
    p.append(text(137, 155, "ΔV_wca = ∑ |∂f/∂Ri| · ΔRi", size=9, color=POS, bold=True))
    p.append(text(137, 180, "Гарантія: 100%", size=10, color=POS, bold=True))
    p.append(text(137, 200, "Ймовірність: ≈ 10⁻⁶", size=9, color=MUTED))
    p.append(text(137, 260, "Надто песимістично,", size=9, color=INK))
    p.append(text(137, 278, "здорожчує проект", size=9, color=INK, bold=True))

    # 2. RSS (Root-Sum-Square)
    p.append(rect(275, 68, 225, 245, fill="#fafafa", stroke="#d1d5db", sw=1.2, rx=6))
    p.append(text(387, 90, "2. Root-Sum-Square (RSS)", size=11, color=NEG, bold=True))
    p.append(text(387, 108, "Квадратична сума дисперсій", size=9, color=MUTED))
    
    p.append(circle(387, 180, 52, fill="#eaf0fd", stroke=NEG, sw=1.5))
    p.append(text(387, 155, "σ_tot = √(∑ (∂f/∂Ri)² σi²)", size=9, color=NEG, bold=True))
    p.append(text(387, 180, "Охоплення 3σ: 99.73%", size=10, color=NEG, bold=True))
    p.append(text(387, 200, "Припускає Гаусів розподіл", size=9, color=MUTED))
    p.append(text(387, 260, "Оптимально для", size=9, color=INK))
    p.append(text(387, 278, "серійного виробництва", size=9, color=INK, bold=True))

    # 3. Monte Carlo Simulation
    p.append(rect(525, 68, 225, 245, fill="#fafafa", stroke="#d1d5db", sw=1.2, rx=6))
    p.append(text(637, 90, "3. Monte Carlo (MC)", size=11, color=FIELD, bold=True))
    p.append(text(637, 108, "Числова симуляція (N=10⁴)", size=9, color=MUTED))
    
    # Заголовок гістограми вище стовпчиків
    p.append(text(637, 130, "Вихідний вихід (Yield)", size=10, color=FIELD, bold=True))

    # Гістограма
    bars = [(545, 15), (560, 35), (575, 60), (590, 80), (605, 90), (620, 95), (635, 95), (650, 90), (665, 80), (680, 60), (695, 35), (710, 15)]
    for bx, bh in bars:
        p.append(rect(bx, 235 - bh, 10, bh, fill="#eef6ef", stroke=FIELD, sw=1, rx=1))
    
    p.append(line(540, 235, 725, 235, color=LINE, sw=1))
    p.append(text(637, 260, "Враховує будь-яку", size=9, color=INK))
    p.append(text(637, 278, "форму розподілу (Binning)", size=9, color=INK, bold=True))

    # Нижній висновок
    p.append(rect(25, 330, 725, 50, fill=FILL, stroke=LINE, sw=1, rx=6))
    p.append(text(387, 350, "Правило вибору: WCA — для критичної авіації та медицини; RSS/MC — для масової електроніки.", size=10, color=INK, bold=True))
    p.append(text(387, 368, "Статистичний підхід дає змогу використовувати на порядок дешевшу елементну базу без втрати якості.", size=9, color=MUTED))

    render(os.path.join(OUT, "wca-vs-rss-monte-carlo.svg"), W, H, *p)


# ── 6. wheatstone-tolerance-bridge: похибка моста Вітстона ────────────────────
def fig_wheatstone_bridge():
    W, H = 780, 420
    p = []
    
    p.append(text(390, 26, "Вплив розкиду резисторів на міст Вітстона", size=14, color=INK, bold=True))
    p.append(text(390, 48, "Чому неузгодженість опорів створює паразитний зсув нуля (Offset Voltage)", size=10, color=MUTED))

    # Ліва частина: Схема моста Вітстона
    bx, by = 175, 210
    
    # Живлення V_in
    p.append(line(bx, by - 120, bx, by - 80, color=LINE, sw=1.8))
    p.append(circle(bx, by - 125, 4, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(bx, by - 138, "+V_in (Живлення)", size=10, color=POS, bold=True))

    # Земля
    p.append(line(bx, by + 80, bx, by + 120, color=LINE, sw=1.8))
    p.append(line(bx - 16, by + 120, bx + 16, by + 120, color=LINE, sw=2))
    p.append(line(bx - 10, by + 125, bx + 10, by + 125, color=LINE, sw=1.5))
    p.append(line(bx - 4, by + 130, bx + 4, by + 130, color=LINE, sw=1))

    # Ромб з'єднань
    p.append(line(bx, by - 80, bx - 70, by, color=LINE, sw=1.8))
    p.append(line(bx, by - 80, bx + 70, by, color=LINE, sw=1.8))
    p.append(line(bx - 70, by, bx, by + 80, color=LINE, sw=1.8))
    p.append(line(bx + 70, by, bx, by + 80, color=LINE, sw=1.8))

    # Резистори R1, R2, R3, R4
    p.append(fitbox(bx - 82, by - 52, 44, 24, "R₁", size=10, bold=True, fill="#ffffff", stroke=LINE))
    p.append(fitbox(bx + 38, by - 52, 44, 24, "R₂", size=10, bold=True, fill="#ffffff", stroke=LINE))
    p.append(fitbox(bx - 82, by + 28, 44, 24, "R₃", size=10, bold=True, fill="#ffffff", stroke=LINE))
    p.append(fitbox(bx + 38, by + 28, 44, 24, "R₄", size=10, bold=True, fill="#ffffff", stroke=LINE))

    # Вузли виходу A і B
    p.append(circle(bx - 70, by, 4, fill=NEG, stroke=LINE, sw=1.5))
    p.append(circle(bx + 70, by, 4, fill=NEG, stroke=LINE, sw=1.5))
    p.append(text(bx - 88, by - 6, "A", size=11, color=NEG, bold=True))
    p.append(text(bx + 88, by - 6, "B", size=11, color=NEG, bold=True))

    # Вихідний сигнал V_out
    p.append(line(bx - 60, by, bx + 60, by, color=POS, sw=1.5, dash="4,3"))
    p.append(fitbox(bx - 32, by - 12, 64, 24, "V_out", size=10, color=POS, bold=True, fill="#fdecec", stroke=POS))

    # Права частина: Порівняння окремих резисторів та інтегральної матриці
    p.append(rect(360, 68, 395, 135, fill="#fdecec", stroke=POS, sw=1.2, rx=6))
    p.append(text(557, 90, "Дискретні резистори (4 × ±0.1%)", size=11, color=POS, bold=True))
    p.append(text(375, 112, "• Розкид номіналів: до ±0.4% на V_out", size=9, color=INK, anchor="start"))
    p.append(text(375, 130, "• Різні TCR (±25 ppm/°C) → сильний дрейф нуля", size=9, color=INK, anchor="start"))
    p.append(text(375, 148, "• Різна температура на платі (градієнт ΔT)", size=9, color=INK, anchor="start"))
    p.append(text(375, 174, "Помилка нуля:  V_offset ≈ V_in · (ΔR / R)", size=9, color=POS, anchor="start", bold=True))

    p.append(rect(360, 218, 395, 135, fill="#eef6ef", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(557, 240, "Резистивна матриця (Matched Array)", size=11, color=FIELD, bold=True))
    p.append(text(375, 262, "• Узгодження опорів (Matching): до 0.01%", size=9, color=INK, anchor="start"))
    p.append(text(375, 280, "• Узгодження TCR (Tracking): до 1..2 ppm/°C", size=9, color=INK, anchor="start"))
    p.append(text(375, 298, "• Один кристал кремнію/кераміки (ізотермія)", size=9, color=INK, anchor="start"))
    p.append(text(375, 324, "Зсув нуля майже відсутній і стабільний у часі", size=9, color=FIELD, anchor="start", bold=True))

    # Нижній висновок
    p.append(rect(25, 368, 730, 36, fill=FILL, stroke=LINE, sw=1, rx=4))
    p.append(text(390, 390, "Метрологічний закон: точність моста залежить не від абсолютного опору, а від його співвідношення.", size=9, color=INK, bold=True))

    render(os.path.join(OUT, "wheatstone-tolerance-bridge.svg"), W, H, *p)


if __name__ == "__main__":
    fig_e_series()
    fig_binning_trap()
    fig_tcr_curves()
    fig_drift_budget()
    fig_wca_vs_rss()
    fig_wheatstone_bridge()
    print("All figures generated successfully.")
