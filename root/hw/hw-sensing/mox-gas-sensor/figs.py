# -*- coding: utf-8 -*-
"""Фігури до теми «Напівпровідниковий давач газу й що таке eCO2».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Додаткові відтінки палітри
WARM  = "#d35400"     # помаранчевий / тепло
COLD  = "#2980b9"     # синій / чисте повітря
PURP  = "#8e44ad"     # фіолетовий / VOC
OXY   = "#e74c3c"     # червоний / кисень
GAS   = "#16a085"     # бірюзовий / CO, етанол
GREY  = "#7f8c8d"     # сірий
LGREY = "#bdc3c7"     # світло-сірий


# ── 1. Хімічний механізм та вигин зон у SnO2 ────────────────────────────────
def fig_mox_surface_chemistry():
    W, H = 840, 440
    f = []

    # Заголовок панелей
    f.append(text(220, 26, "1. Чисте повітря: хемосорбція кисню", size=14, bold=True, color=COLD))
    f.append(text(620, 26, "2. Повітря з газом (VOC / CO): окиснення", size=14, bold=True, color=POS))

    # Розділювач панелей
    f.append(line(420, 15, 420, 420, color=LGREY, sw=1.2, dash="4,4"))

    # === ЛІВА ПАНЕЛЬ: Чисте повітря ===
    # Поверхня кристалітів SnO2
    f.append(rect(40, 50, 340, 160, fill="#fdfefe", stroke=COLD, sw=1.5, rx=8))
    f.append(text(210, 72, "Поверхня нанокристалітів SnO₂ (300 °C)", size=12, bold=True, color=INK))

    # Зерна кристалітів
    f.append(circle(130, 140, 45, fill="#ebf5fb", stroke=COLD, sw=1.8))
    f.append(circle(210, 140, 45, fill="#ebf5fb", stroke=COLD, sw=1.8))
    f.append(circle(290, 140, 45, fill="#ebf5fb", stroke=COLD, sw=1.8))
    f.append(text(130, 145, "Зерно SnO₂", size=10, color=COLD, bold=True))
    f.append(text(210, 145, "Зерно SnO₂", size=10, color=COLD, bold=True))
    f.append(text(290, 145, "Зерно SnO₂", size=10, color=COLD, bold=True))

    # Шар збіднення електронами (пунктирне кільце)
    f.append('<circle cx="130" cy="140" r="35" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' % POS)
    f.append('<circle cx="210" cy="140" r="35" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' % POS)
    f.append('<circle cx="290" cy="140" r="35" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' % POS)

    # Іони кисню O^- на поверхні
    for ox, oy in [(100, 105), (130, 92), (160, 102), (180, 95), (210, 92), (240, 98), (265, 102), (290, 92), (318, 105)]:
        f.append(circle(ox, oy, 8, fill="#fadbd8", stroke=OXY, sw=1.2))
        f.append(text(ox, oy + 3, "O⁻", size=10, bold=True, color=OXY))

    # Електрони захоплені на поверхню
    f.append(text(210, 196, "Кисень зв'язує e⁻ → Шар збіднення W", size=10.5, color=POS, bold=True))

    # Енергетична діаграма зон (Вигин зон Ec, Ev)
    f.append(rect(40, 225, 340, 185, fill="#fcfcfc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(210, 246, "Зонна діаграма: високий бар'єр qVs", size=11.5, bold=True, color=INK))

    # Вісь енергії та координати
    f.append(arrow(60, 385, 60, 260, color=LINE, sw=1.3))
    f.append(text(55, 270, "Енергія E", size=10, color=MUTED, anchor="end"))
    f.append(arrow(60, 385, 360, 385, color=LINE, sw=1.3))
    f.append(text(355, 400, "x (глибина зерна)", size=10, color=MUTED, anchor="end"))

    # Зона провідності Ec з вигином вгору на межах зерен
    pts_ec1 = [(70, 320), (100, 320), (140, 280), (170, 280), (200, 320), (240, 320), (270, 280), (300, 280), (330, 320), (355, 320)]
    poly_ec1 = " ".join("%.1f,%.1f" % p for p in pts_ec1)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (poly_ec1, COLD))
    f.append(text(85, 312, "E_c", size=10.5, bold=True, color=COLD))

    # Рівень Фермі Ef
    f.append(line(70, 335, 355, 335, color=GREY, sw=1.2, dash="4,3"))
    f.append(text(85, 348, "E_F", size=10, color=GREY))

    # Бар'єр qVs
    f.append(line(170, 280, 170, 320, color=POS, sw=1.4))
    f.append(text(178, 305, "q·V_s (0.8 еВ)", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(210, 370, "Опір R_0 ВИСОКИЙ (сотні кОм — МОм)", size=10.5, bold=True, color=POS))


    # === ПРАВА ПАНЕЛЬ: Повітря з газом ===
    f.append(rect(460, 50, 340, 160, fill="#fdfefe", stroke=POS, sw=1.5, rx=8))
    f.append(text(630, 72, "Каталітичне окиснення VOC / CO / Спирту", size=12, bold=True, color=INK))

    # Зерна кристалітів
    f.append(circle(550, 140, 45, fill="#fef9e7", stroke=WARM, sw=1.8))
    f.append(circle(630, 140, 45, fill="#fef9e7", stroke=WARM, sw=1.8))
    f.append(circle(710, 140, 45, fill="#fef9e7", stroke=WARM, sw=1.8))
    f.append(text(550, 145, "Зерно SnO₂", size=10, color=WARM, bold=True))
    f.append(text(630, 145, "Зерно SnO₂", size=10, color=WARM, bold=True))
    f.append(text(710, 145, "Зерно SnO₂", size=10, color=WARM, bold=True))

    # Тонший шар збіднення (звузився)
    f.append('<circle cx="550" cy="140" r="41" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' % FIELD)
    f.append('<circle cx="630" cy="140" r="41" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' % FIELD)
    f.append('<circle cx="710" cy="140" r="41" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' % FIELD)

    # Молекули відновлювального газу реагують
    f.append(rect(520, 86, 42, 18, fill="#e8f8f5", stroke=GAS, sw=1.2, rx=4))
    f.append(text(541, 99, "CO", size=10, bold=True, color=GAS))
    f.append(arrow(541, 105, 545, 116, color=GAS, sw=1.2))

    f.append(rect(605, 86, 66, 18, fill="#f4ecf7", stroke=PURP, sw=1.2, rx=4))
    f.append(text(638, 99, "VOC (спирт)", size=10, bold=True, color=PURP))
    f.append(arrow(638, 105, 634, 116, color=PURP, sw=1.2))

    f.append(rect(690, 86, 65, 18, fill="#fef5e7", stroke=WARM, sw=1.2, rx=4))
    f.append(text(722, 99, "CO₂ + H₂O", size=10, bold=True, color=WARM))

    f.append(text(630, 196, "CO + O⁻ → CO₂ + e⁻ (скидання e⁻ в зону E_c)", size=10, color=FIELD, bold=True))

    # Зонна діаграма при появі газу
    f.append(rect(460, 225, 340, 185, fill="#fcfcfc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(630, 246, "Зонна діаграма: колапс бар'єра Шотткі", size=11.5, bold=True, color=INK))

    f.append(arrow(480, 385, 480, 260, color=LINE, sw=1.3))
    f.append(text(475, 270, "Енергія E", size=9.5, color=MUTED, anchor="end"))
    f.append(arrow(480, 385, 780, 385, color=LINE, sw=1.3))
    f.append(text(775, 400, "x (глибина зерна)", size=9.5, color=MUTED, anchor="end"))

    # Зона провідності Ec з набагато меншим вигином
    pts_ec2 = [(490, 320), (520, 320), (560, 305), (590, 305), (620, 320), (660, 320), (690, 305), (720, 305), (750, 320), (775, 320)]
    poly_ec2 = " ".join("%.1f,%.1f" % p for p in pts_ec2)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (poly_ec2, FIELD))
    f.append(text(505, 312, "E_c", size=10.5, bold=True, color=FIELD))

    f.append(line(490, 335, 775, 335, color=GREY, sw=1.2, dash="4,3"))
    f.append(text(505, 348, "E_F", size=10, color=GREY))

    # Знижений бар'єр
    f.append(line(590, 305, 590, 320, color=FIELD, sw=1.4))
    f.append(text(598, 313, "q·V_s' (0.15 еВ)", size=9.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(630, 370, "Опір R_s різко ПАДАЄ (струм вільно тече)", size=10.5, bold=True, color=FIELD))

    render(os.path.join(IMG, "mox-surface-chemistry.svg"), W, H, *f)


# ── 2. Конструкція MEMS Micro-hotplate ──────────────────────────────────────
def fig_mems_micro_hotplate():
    W, H = 800, 380
    f = []

    f.append(text(W / 2, 24, "Конструкція кремнієвого мікронагрівача (MEMS Micro-hotplate)", size=15, bold=True))

    # Витравлений кремній (Si підкладка)
    # Зліва кристал
    f.append(rect(60, 160, 160, 120, fill="#eaeded", stroke=LINE, sw=1.5, rx=3))
    f.append(text(140, 225, "Кремнієва підкладка\n(Si Substrate)", size=10.5, color=INK, bold=True))

    # Справа кристал
    f.append(rect(580, 160, 160, 120, fill="#eaeded", stroke=LINE, sw=1.5, rx=3))
    f.append(text(660, 225, "Кремнієва підкладка\n(Si Substrate)", size=10.5, color=INK, bold=True))

    # Витравлена порожнина (Cavity) під мембраною
    f.append('<polygon points="220,160 300,280 500,280 580,160" fill="#f4f6f7" stroke="%s" stroke-width="1.5"/>' % LINE)
    f.append(text(400, 240, "Витравлена порожнина (Micro-cavity)\nТеплоізоляція від кристала", size=10, color=MUTED, bold=True))

    # Тонка діелектрична мембрана (Si3N4 / SiO2 товщиною 1-2 мкм)
    f.append(rect(180, 150, 440, 12, fill="#aed6f1", stroke=COLD, sw=1.5, rx=2))
    f.append(text(230, 136, "Мембрана Si₃N₄ / SiO₂ (1–2 мкм)", size=10, bold=True, color=COLD))

    # Платиновий нагрівач (Pt Heater) всередині мембрани
    for hx in [310, 340, 370, 400, 430, 460, 490]:
        f.append(circle(hx, 156, 4, fill="#f9e79f", stroke=WARM, sw=1.2))
    f.append(text(400, 180, "Платиновий змійовик нагрівача (Pt Heater / RTD)", size=9.5, bold=True, color=WARM))

    # Зустрічно-штирьові електроди (Interdigitated electrodes)
    f.append(rect(300, 142, 200, 8, fill="#d5d8dc", stroke=LINE, sw=1.2))
    f.append(text(510, 136, "Електроди вимірювання", size=9.5, bold=True, color=LINE, anchor="start"))

    # Чутливий шар SnO2 (Nanocrystalline film)
    f.append(rect(320, 120, 160, 22, fill="#fdebd0", stroke=POS, sw=1.8, rx=4))
    f.append(text(400, 134, "Газочутливий шар SnO₂ / WO₃", size=11, bold=True, color=POS))
    f.append(text(400, 105, "Гаряча робоча зона (300–380 °C)", size=10.5, bold=True, color=OXY))

    # Теплові потоки
    f.append(arrow(340, 110, 340, 85, color=OXY, sw=1.3))
    f.append(arrow(400, 100, 400, 75, color=OXY, sw=1.3))
    f.append(arrow(460, 110, 460, 85, color=OXY, sw=1.3))

    # Нижня панель: порівняння параметрів
    f.append(rect(60, 305, 680, 60, fill="#fdfefe", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(180, 328, "Класичний давач (MQ)", size=11, bold=True, color=POS))
    f.append(text(180, 348, "Потужність: 800–1000 мВт (5 В, 180 мА)\nЧас розігріву: 30–60 секунд", size=9.5, color=MUTED))

    f.append(line(390, 312, 390, 358, color=LGREY, sw=1.2))

    f.append(text(550, 328, "Сучасний MEMS-давач (SGP40 / BME680)", size=11, bold=True, color=FIELD))
    f.append(text(550, 348, "Потужність: 15–25 мВт (імпульсно < 0.1 мВт)\nЧас розігріву: 10–30 мілісекунд (Duty cycling)", size=9.5, color=MUTED))

    render(os.path.join(IMG, "mems-micro-hotplate.svg"), W, H, *f)


# ── 3. Розбіжність eCO2 та NDIR при появі VOC ────────────────────────────────
def fig_eco2_vs_ndir_divergence():
    W, H = 820, 400
    f = []

    f.append(text(W / 2, 25, "Порівняння eCO₂ (напівпровідник MOX) та фізичного NDIR CO₂", size=15, bold=True))

    # Осі графіка
    x0, y0 = 80, 330
    x_max, y_max = 760, 70
    f.append(arrow(x0, y0, x_max, y0, color=LINE, sw=1.5))
    f.append(arrow(x0, y0, x0, y_max, color=LINE, sw=1.5))
    f.append(text(x_max - 20, y0 + 25, "Час (години) →", size=11, bold=True, color=INK))
    f.append(text(x0 - 10, y_max + 10, "Концентрація CO₂ / eCO₂ (ppm)", size=11, bold=True, color=INK, anchor="end"))

    # Горизонтальні позначки ppm
    for ppm, y_pos in [(400, 305), (1000, 250), (2000, 180), (5000, 120)]:
        f.append(line(x0 - 5, y_pos, x_max - 40, y_pos, color=LGREY, sw=1, dash="3,3"))
        f.append(text(x0 - 10, y_pos + 4, str(ppm), size=9.5, color=MUTED, anchor="end"))

    # Фази експерименту (вертикальні зони)
    f.append('<rect x="80" y="60" width="220" height="270" rx="0" fill="#ebf5fb" stroke="none" opacity="0.6"/>')
    f.append(text(190, 80, "Фаза 1: Дихання людей", size=10.5, bold=True, color=COLD))
    f.append(text(190, 96, "CO₂ і біо-VOC ростуть разом", size=10, color=MUTED))

    f.append('<rect x="300" y="60" width="220" height="270" rx="0" fill="#fdebd0" stroke="none" opacity="0.6"/>')
    f.append(text(410, 80, "Фаза 2: Антисептик / Спирт", size=10.5, bold=True, color=POS))
    f.append(text(410, 96, "Сплеск етанолу (VOC)", size=10, color=MUTED))

    f.append('<rect x="520" y="60" width="200" height="270" rx="0" fill="#eaeded" stroke="none" opacity="0.6"/>')
    f.append(text(620, 80, "Фаза 3: Чистий CO₂ (без VOC)", size=10.5, bold=True, color=PURP))
    f.append(text(620, 96, "Провітрено + сухий лід", size=10, color=MUTED))

    # Крива NDIR (справжній оптичний CO2) — Зелена лінія
    pts_ndir = []
    for x in range(80, 301, 10):
        t = (x - 80) / 220.0
        y = 300 - 95 * t
        pts_ndir.append((x, y))
    for x in range(310, 521, 10):
        t = (x - 300) / 220.0
        y = 205 + 30 * t
        pts_ndir.append((x, y))
    for x in range(530, 721, 10):
        t = (x - 520) / 200.0
        y = 235 - 80 * math.sin(t * math.pi)
        pts_ndir.append((x, y))

    poly_ndir = " ".join("%.1f,%.1f" % p for p in pts_ndir)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round"/>' % (poly_ndir, FIELD))

    # Крива eCO2 (MOX оцінка) — Червона пунктирна лінія
    pts_eco2 = []
    for x in range(80, 301, 10):
        t = (x - 80) / 220.0
        y = 302 - 102 * t + math.sin(x) * 3
        pts_eco2.append((x, y))
    for x in range(310, 521, 10):
        t = (x - 300) / 220.0
        if t < 0.2:
            y = 200 - (125 * (t / 0.2))
        else:
            y = 75 + 110 * ((t - 0.2) / 0.8)
        pts_eco2.append((x, y))
    for x in range(530, 721, 10):
        t = (x - 520) / 200.0
        y = 300 - 5 * math.sin(t)
        pts_eco2.append((x, y))

    poly_eco2 = " ".join("%.1f,%.1f" % p for p in pts_eco2)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,4" stroke-linejoin="round"/>' % (poly_eco2, POS))

    # Легенда
    f.append(rect(180, 345, 460, 45, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(line(200, 368, 240, 368, color=FIELD, sw=3))
    f.append(text(250, 372, "Справжній NDIR CO₂ (оптичне поглинання 4.26 мкм)", size=10.5, bold=True, color=FIELD, anchor="start"))

    f.append(line(460, 368, 500, 368, color=POS, sw=2.5, dash="6,4"))
    f.append(text(510, 372, "eCO₂ (напівпровідник MOX)", size=10.5, bold=True, color=POS, anchor="start"))

    # Анотації на графіку
    f.append(text(410, 130, "ПОМИЛКА +5000%:\nспирт маскується під CO₂", size=10, bold=True, color=POS))
    f.append(text(620, 240, "СЛІПА ЗОНА:\nчистий CO₂ не реагує з MOX", size=10, bold=True, color=PURP))

    render(os.path.join(IMG, "eco2-vs-ndir-divergence.svg"), W, H, *f)


# ── 4. Алгоритм відстеження базової лінії та VOC Index ──────────────────────
def fig_baseline_tracking_algorithm():
    W, H = 820, 390
    f = []

    f.append(text(W / 2, 24, "Алгоритм динамічної базової лінії (Baseline Tracking) та VOC Index", size=15, bold=True))

    # Верхній графік: Опір сенсора Rs і Базова лінія R_base
    x0, y0 = 80, 180
    x_max = 760
    f.append(arrow(x0, y0, x_max, y0, color=LINE, sw=1.4))
    f.append(arrow(x0, y0, x0, 50, color=LINE, sw=1.4))
    f.append(text(x_max - 20, y0 + 18, "Час t (24–72 години) →", size=10.5, bold=True, color=INK))
    f.append(text(x0 - 10, 60, "Опір шару R (кОм)", size=10.5, bold=True, color=INK, anchor="end"))

    pts_rs = []
    pts_base = []
    for x in range(80, 741, 10):
        t = (x - 80) / 660.0
        base_val = 150 - 20 * t
        pollution = 0
        if 180 <= x <= 260:
            pollution = 60 * math.sin((x - 180) / 80.0 * math.pi)
        elif 360 <= x <= 460:
            pollution = 85 * math.sin((x - 360) / 100.0 * math.pi)
        elif 560 <= x <= 680:
            pollution = 70 * math.sin((x - 560) / 120.0 * math.pi)

        noise = math.sin(x * 1.5) * 2
        y_rs = 180 - (base_val - pollution + noise)
        y_base = 180 - base_val
        pts_rs.append((x, y_rs))
        pts_base.append((x, y_base))

    poly_rs = " ".join("%.1f,%.1f" % p for p in pts_rs)
    poly_base = " ".join("%.1f,%.1f" % p for p in pts_base)

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-linejoin="round"/>' % (poly_rs, COLD))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5,4"/>' % (poly_base, POS))

    f.append(text(280, 65, "Базова лінія R_base(t) (асиметричний LP-фільтр)", size=10, bold=True, color=POS))
    f.append(text(500, 160, "Сирий опір сенсора R_s(t)", size=10, bold=True, color=COLD))

    # Нижній графік: Вихідний VOC Index (Sensirion / Bosch алгоритм)
    y2_0 = 340
    f.append(arrow(x0, y2_0, x_max, y2_0, color=LINE, sw=1.4))
    f.append(arrow(x0, y2_0, x0, 215, color=LINE, sw=1.4))
    f.append(text(x_max - 20, y2_0 + 18, "Час t →", size=10.5, bold=True, color=INK))
    f.append(text(x0 - 10, 225, "VOC Index (0..500)", size=10.5, bold=True, color=INK, anchor="end"))

    f.append(line(x0, 310, x_max - 20, 310, color=FIELD, sw=1.2, dash="4,3"))
    f.append(text(x0 - 8, 314, "100", size=10, bold=True, color=FIELD, anchor="end"))
    f.append(text(720, 303, "Індекс 100 = нормальний фон", size=10, bold=True, color=FIELD))

    f.append(line(x0, 275, x_max - 20, 275, color=LGREY, sw=1, dash="3,3"))
    f.append(text(x0 - 8, 279, "250", size=10, color=MUTED, anchor="end"))
    f.append(line(x0, 235, x_max - 20, 235, color=LGREY, sw=1, dash="3,3"))
    f.append(text(x0 - 8, 239, "500", size=10, color=MUTED, anchor="end"))

    pts_voc = []
    for x in range(80, 741, 10):
        idx = 100
        if 180 <= x <= 260:
            idx += 180 * math.sin((x - 180) / 80.0 * math.pi)
        elif 360 <= x <= 460:
            idx += 350 * math.sin((x - 360) / 100.0 * math.pi)
        elif 560 <= x <= 680:
            idx += 260 * math.sin((x - 560) / 120.0 * math.pi)
        idx += math.sin(x) * 4
        y_voc = y2_0 - (idx / 500.0) * 115
        pts_voc.append((x, y_voc))

    poly_voc = " ".join("%.1f,%.1f" % p for p in pts_voc)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-linejoin="round"/>' % (poly_voc, PURP))

    f.append(text(220, 235, "Вентиляція відчинена", size=9.5, bold=True, color=PURP))
    f.append(text(410, 220, "Приготування їжі / Спирт", size=9.5, bold=True, color=POS))
    f.append(text(620, 235, "Забруднення VOC", size=9.5, bold=True, color=PURP))

    render(os.path.join(IMG, "baseline-tracking-algorithm.svg"), W, H, *f)


if __name__ == '__main__':
    fig_mox_surface_chemistry()
    fig_mems_micro_hotplate()
    fig_eco2_vs_ndir_divergence()
    fig_baseline_tracking_algorithm()
    print("Усі 4 фігури згенеровано успішно.")
