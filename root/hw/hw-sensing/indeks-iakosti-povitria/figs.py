# -*- coding: utf-8 -*-
"""Фігури до теми «Індекс якості повітря».
Запуск:  python figs.py   → генерує SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_GOOD      = "#27ae60"  # Добре (0-50)
COLOR_MODERATE  = "#d4ac0d"  # Помірне (51-100)
COLOR_USG       = "#d35400"  # Шкідливе для чутливих (101-150)
COLOR_UNHEALTHY = "#c0392b"  # Шкідливе (151-200)
COLOR_VERY_UNH  = "#7d3c98"  # Дуже шкідливе (201-300)
COLOR_HAZARD    = "#641e16"  # Небезпечне (301-500)
COLOR_BLUE      = "#2457d6"


# ── Фігура 1: Кусково-лінійна інтерполяція суб-індексу AQI ─────────────────
def fig_piecewise_interpolation():
    W, H = 760, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, "Кусково-лінійна інтерполяція суб-індексу AQI (на прикладі PM2.5)", size=15, bold=True))

    ox, oy = 80, 370
    gw, gh = 630, 310
    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))

    f.append(text(ox + gw - 30, oy + 32, "Концентрація C (мкг/м³)", size=11, bold=True, color=INK))
    f.append(text(ox - 40, oy - gh + 15, "Індекс I", size=11, bold=True, color=INK))

    y_tiers = [
        (0, COLOR_GOOD, "0 — Добре"),
        (50, COLOR_MODERATE, "50 — Помірне"),
        (100, COLOR_USG, "100 — Чутливі"),
        (150, COLOR_UNHEALTHY, "150 — Шкідливе"),
        (200, COLOR_VERY_UNH, "200 — Дуже шкідливе"),
        (300, COLOR_HAZARD, "300 — Небезпечне"),
        (500, COLOR_HAZARD, "500")
    ]

    pts = [
        (0.0, 0),
        (9.0, 50),
        (35.4, 100),
        (55.4, 150),
        (125.4, 200),
        (225.4, 300),
        (325.4, 500)
    ]

    def map_x(c):
        return ox + (c / 350.0) * (gw - 40)

    def map_y(aqi):
        if aqi <= 50:
            return oy - (aqi / 50.0) * 44
        elif aqi <= 100:
            return oy - 44 - ((aqi - 50) / 50.0) * 44
        elif aqi <= 150:
            return oy - 88 - ((aqi - 100) / 50.0) * 44
        elif aqi <= 200:
            return oy - 132 - ((aqi - 150) / 50.0) * 44
        elif aqi <= 300:
            return oy - 176 - ((aqi - 200) / 100.0) * 50
        else:
            return oy - 226 - ((aqi - 300) / 200.0) * 54

    for aqi, col, lbl in y_tiers:
        y_pos = map_y(aqi)
        f.append(line(ox, y_pos, ox + gw, y_pos, color="#e5e8eb", sw=1, dash="4,4"))
        f.append(text(ox - 8, y_pos + 4, str(aqi), size=11, color=col, bold=True, anchor="end"))

    for i in range(len(pts) - 1):
        c1, a1 = pts[i]
        c2, a2 = pts[i + 1]
        x1, y1 = map_x(c1), map_y(a1)
        x2, y2 = map_x(c2), map_y(a2)
        seg_col = y_tiers[i + 1][1]
        f.append(line(x1, y1, x2, y2, color=seg_col, sw=3))
        f.append(line(x2, oy, x2, y2, color="#d0d4dc", sw=1, dash="3,3"))
        dx_offset = -6 if i == 0 else (4 if i == 1 else 0)
        f.append(text(x2 + dx_offset, oy + 16, str(c2), size=10, color=INK, anchor="middle"))

    f.append(text(ox, oy + 16, "0.0", size=10, color=INK, anchor="middle"))

    for c, a in pts:
        x, y = map_x(c), map_y(a)
        f.append(circle(x, y, 4, fill=BG, stroke=LINE, sw=1.8))

    # Точка прикладу C = 45.4 -> AQI = 125
    sample_c = 45.4
    sample_aqi = 125
    sx, sy = map_x(sample_c), map_y(sample_aqi)
    f.append(circle(sx, sy, 5, fill=COLOR_BLUE, stroke=LINE, sw=1.5))

    # Розміщення формульного блоку вгорі праворуч
    box_cx, box_cy = 480, 110
    box, bw, bh = textbox(box_cx, box_cy,
                          "I = ((I_hi − I_lo) / (BP_hi − BP_lo)) · (C − BP_lo) + I_lo\n"
                          "C = 45.4  →  I = ((150 − 101) / (55.4 − 35.5)) · (45.4 − 35.5) + 101 = 125",
                          size=11, pad=10, fill="#eef6ff", stroke=COLOR_BLUE, sw=1.2)
    f.append(box)

    # Стрілка від точки до нижнього лівого кута рамки
    f.append(arrow(sx, sy, box_cx - bw / 2 + 20, box_cy + bh / 2 + 2, color=COLOR_BLUE, sw=1.3))

    return render(os.path.join(IMG, "aqi-piecewise-interpolation.svg"), W, H, *f)


# ── Фігура 2: Конвеєр мультисенсорного злиття та обчислення AQI ───────────
def fig_multisensor_pipeline():
    W, H = 760, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, "Архітектура конвеєра обробки мультисенсорних даних та розрахунку AQI", size=14, bold=True))

    y_start = 55
    row_h = 44
    gap_y = 10

    sensors = [
        ("Оптичний лічильник\n(PM2.5 / PM10)", "#e8f8f5", "#16a085"),
        ("Електрохімічні комірки\n(CO, NO2, SO2, O3)", "#fef9e7", "#f39c12"),
        ("NDIR давач\n(CO2)", "#ebf5fb", "#2980b9"),
        ("MOX давач\n(VOC / IAQ)", "#f4ecf7", "#8e44ad"),
        ("T / RH давач\n(SHT3x / BME280)", "#fdedec", "#e74c3c")
    ]

    # 1. Давачі
    f.append(text(90, y_start - 10, "1. Сирі сигнали", size=12, bold=True, color=INK))
    for i, (title, fcol, scol) in enumerate(sensors):
        cy = y_start + i * (row_h + gap_y) + row_h / 2
        f.append(rect(20, y_start + i * (row_h + gap_y), 140, row_h, fill=fcol, stroke=scol, sw=1.4, rx=4))
        lines = title.split("\n")
        f.append(text(90, cy - 6, lines[0], size=10, bold=True, color=INK))
        f.append(text(90, cy + 8, lines[1], size=9, color=MUTED))

    # 2. Фізична корекція
    f.append(text(275, y_start - 10, "2. Фізична корекція", size=12, bold=True, color=INK))
    corrs = [
        "Гігроскопічна поправка\n(здуття аерозолю за RH)",
        "Температурний дрейф нуля\n+ крос-чутливість NO2/O3",
        "Температурна лінеаризація\nта тиск",
        "Відстеження базової лінії\nта вологості",
        "Опорні канали T (°C)\nта RH (%)"
    ]
    for i, text_corr in enumerate(corrs):
        cy = y_start + i * (row_h + gap_y) + row_h / 2
        f.append(rect(195, y_start + i * (row_h + gap_y), 160, row_h, fill='#ffffff', stroke=LINE, sw=1.2, rx=4))
        lines = text_corr.split("\n")
        f.append(text(275, cy - 6, lines[0], size=10, bold=True, color=INK))
        f.append(text(275, cy + 8, lines[1], size=9, color=MUTED))
        f.append(arrow(160, cy, 195, cy, color=LINE, sw=1.2))

    rh_cy = y_start + 4 * (row_h + gap_y) + row_h / 2
    f.append(line(195, rh_cy, 180, rh_cy, color="#e74c3c", sw=1.2, dash="2,2"))
    f.append(line(180, rh_cy, 180, y_start + row_h / 2, color="#e74c3c", sw=1.2, dash="2,2"))
    f.append(arrow(180, y_start + row_h / 2, 195, y_start + row_h / 2, color="#e74c3c", sw=1.2))

    # 3. Адаптивні фільтри
    f.append(text(450, y_start - 10, "3. Адаптивні фільтри", size=12, bold=True, color=INK))
    filters = [
        "EPA NowCast (12 год)\nдинамічне зважування",
        "Ковзне вікно (1 год / 8 год)\nінтерполяція пропусків",
        "Ковзне вікно (8 год)\nусереднення CO",
        "Відносний індекс IAQ\n(алгоритм сенсора)",
        "Метео-параметри\n(фільтрація шумів)"
    ]
    for i, filt in enumerate(filters):
        cy = y_start + i * (row_h + gap_y) + row_h / 2
        f.append(rect(375, y_start + i * (row_h + gap_y), 150, row_h, fill='#f4f6f8', stroke=LINE, sw=1.2, rx=4))
        lines = filt.split("\n")
        f.append(text(450, cy - 6, lines[0], size=10, bold=True, color=INK))
        f.append(text(450, cy + 8, lines[1], size=9, color=MUTED))
        f.append(arrow(355, cy, 375, cy, color=LINE, sw=1.2))

    # 4. Суб-індекси
    f.append(text(600, y_start - 10, "4. Суб-індекси I_p", size=12, bold=True, color=INK))
    sub_indices = [
        ("I_PM2.5", "125", COLOR_USG),
        ("I_NO2 / I_O3", "42", COLOR_GOOD),
        ("I_CO", "18", COLOR_GOOD),
        ("I_SO2", "12", COLOR_GOOD),
        ("I_PM10", "65", COLOR_MODERATE)
    ]
    for i, (name, val, col) in enumerate(sub_indices):
        cy = y_start + i * (row_h + gap_y) + row_h / 2
        f.append(rect(555, y_start + i * (row_h + gap_y), 90, row_h, fill='#ffffff', stroke=col, sw=1.5, rx=4))
        f.append(text(600, cy - 6, name, size=10, bold=True, color=INK))
        f.append(text(600, cy + 9, "I = " + val, size=11, bold=True, color=col))
        f.append(arrow(525, cy, 555, cy, color=LINE, sw=1.2))

    # 5. Агрегація
    f.append(text(700, y_start - 10, "5. Агрегація", size=12, bold=True, color=INK))
    f.append(rect(665, y_start + 40, 75, 160, fill='#fff0f0', stroke=COLOR_UNHEALTHY, sw=1.8, rx=6))
    f.append(text(702, y_start + 65, "AQI", size=14, bold=True, color=COLOR_UNHEALTHY))
    f.append(text(702, y_start + 85, "= max(I_p)", size=11, bold=True, color=INK))
    f.append(text(702, y_start + 115, "125", size=22, bold=True, color=COLOR_USG))
    f.append(text(702, y_start + 138, "Чутливі", size=10, bold=True, color=COLOR_USG))
    f.append(text(702, y_start + 155, "Домінанта:", size=9, color=MUTED))
    f.append(text(702, y_start + 170, "PM2.5", size=10, bold=True, color=INK))

    for i in range(5):
        cy = y_start + i * (row_h + gap_y) + row_h / 2
        f.append(line(645, cy, 665, y_start + 120, color=MUTED, sw=1.1))

    box, bw, bh = textbox(W / 2, 355,
                          "Токсикологічний принцип некомпенсованості: агрегація через max() запобігає маскуванню небезпеки.\n"
                          "Чисте повітря за іншими газами не може зменшити токсичний вплив домінуючого забруднювача!",
                          size=11, pad=6, fill="#fef9e7", stroke="#f39c12", sw=1.2)
    f.append(box)

    return render(os.path.join(IMG, "aqi-multisensor-pipeline.svg"), W, H, *f)


# ── Фігура 3: Адаптивне зважування NowCast проти ковзного середнього ────────
def fig_nowcast_weighting():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, "Динамічний відгук EPA NowCast проти 24-годинного ковзного середнього", size=14, bold=True))

    ox, oy = 80, 310
    gw, gh = 620, 240
    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))

    f.append(text(ox + gw - 20, oy + 30, "Час (години доби)", size=12, bold=True, color=INK))
    f.append(text(ox - 45, oy - gh + 15, "PM2.5 (мкг/м³)", size=11, bold=True, color=INK))

    for h_val in range(0, 25, 4):
        hx = ox + (h_val / 24.0) * (gw - 20)
        f.append(line(hx, oy, hx, oy + 5, color=LINE, sw=1.2))
        f.append(text(hx, oy + 18, f"{h_val:02d}:00", size=10, color=MUTED, anchor="middle"))

    for c_val in range(0, 250, 50):
        cy = oy - (c_val / 200.0) * (gh - 30)
        f.append(line(ox - 5, cy, ox, cy, color=LINE, sw=1.2))
        f.append(line(ox, cy, ox + gw, cy, color="#efefef", sw=1, dash="3,3"))
        f.append(text(ox - 10, cy + 4, str(c_val), size=10, color=MUTED, anchor="end"))

    raw_profile = [
        (0, 12), (4, 15), (7, 18), (8, 65), (9, 145), (10, 180), (11, 195),
        (12, 170), (13, 110), (14, 45), (16, 25), (20, 15), (24, 12)
    ]

    sma_profile = [
        (0, 14), (4, 14), (7, 15), (8, 18), (9, 24), (10, 32), (11, 41),
        (12, 49), (13, 54), (14, 56), (16, 55), (20, 48), (24, 40)
    ]

    nowcast_profile = [
        (0, 13), (4, 14), (7, 17), (8, 48), (9, 118), (10, 162), (11, 184),
        (12, 168), (13, 122), (14, 62), (16, 32), (20, 18), (24, 13)
    ]

    def to_coords(prof):
        return [(ox + (h / 24.0) * (gw - 20), oy - (c / 200.0) * (gh - 30)) for h, c in prof]

    pts_sma = to_coords(sma_profile)
    for i in range(len(pts_sma) - 1):
        f.append(line(pts_sma[i][0], pts_sma[i][1], pts_sma[i+1][0], pts_sma[i+1][1], color=COLOR_BLUE, sw=2.5, dash="6,3"))

    pts_nc = to_coords(nowcast_profile)
    for i in range(len(pts_nc) - 1):
        f.append(line(pts_nc[i][0], pts_nc[i][1], pts_nc[i+1][0], pts_nc[i+1][1], color=COLOR_UNHEALTHY, sw=3))

    pts_raw = to_coords(raw_profile)
    for i in range(len(pts_raw) - 1):
        f.append(line(pts_raw[i][0], pts_raw[i][1], pts_raw[i+1][0], pts_raw[i+1][1], color=INK, sw=1.5))
        f.append(circle(pts_raw[i][0], pts_raw[i][1], 3, fill=BG, stroke=INK, sw=1.2))
    f.append(circle(pts_raw[-1][0], pts_raw[-1][1], 3, fill=BG, stroke=INK, sw=1.2))

    leg_x = 420
    leg_y = 55
    f.append(rect(leg_x, leg_y, 260, 85, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=4))
    f.append(line(leg_x + 15, leg_y + 18, leg_x + 45, leg_y + 18, color=INK, sw=1.8))
    f.append(circle(leg_x + 30, leg_y + 18, 3, fill=BG, stroke=INK, sw=1.2))
    f.append(text(leg_x + 55, leg_y + 22, "Реальна погодинна PM2.5", size=10, bold=True, color=INK, anchor="start"))

    f.append(line(leg_x + 15, leg_y + 42, leg_x + 45, leg_y + 42, color=COLOR_UNHEALTHY, sw=3))
    f.append(text(leg_x + 55, leg_y + 46, "EPA NowCast (швидкий відгук)", size=10, bold=True, color=COLOR_UNHEALTHY, anchor="start"))

    f.append(line(leg_x + 15, leg_y + 66, leg_x + 45, leg_y + 66, color=COLOR_BLUE, sw=2.5, dash="6,3"))
    f.append(text(leg_x + 55, leg_y + 70, "24-год ковзне середнє (запізнення)", size=10, bold=True, color=COLOR_BLUE, anchor="start"))

    f.append(arrow(ox + (11 / 24.0) * (gw - 20), oy - (184 / 200.0) * (gh - 30),
                   ox + (11 / 24.0) * (gw - 20), oy - (41 / 200.0) * (gh - 30) - 5,
                   color=COLOR_UNHEALTHY, sw=1.5))
    f.append(text(ox + (11 / 24.0) * (gw - 20) + 10, oy - (120 / 200.0) * (gh - 30),
                  "Запізнення 24h SMA", size=10, bold=True, color=COLOR_UNHEALTHY, anchor="start"))

    box, bw, bh = textbox(W / 2, 365,
                          "Коефіцієнт зважування: w = max(C_min / C_max, 0.5). При різкому стрибку w = 0.5 (ваги: 1, 0.5, 0.25...),\n"
                          "що надає 50% ваги останній годині. При стабільному повітрі w = 1.0 (звичайне 12-годинне середнє).",
                          size=11, pad=6, fill="#eef6ff", stroke=COLOR_BLUE, sw=1.2)
    f.append(box)

    return render(os.path.join(IMG, "nowcast-weighting.svg"), W, H, *f)


# ── Фігура 4: Порівняння шкал US EPA AQI та європейського CAQI / EEA ───────
def fig_epa_vs_caqi():
    W, H = 760, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, "Порівняльна структура шкал US EPA AQI та європейського CAQI / EEA", size=14, bold=True))

    midx = W / 2
    f.append(line(midx, 45, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # ЛІВА ЧАСТИНА: US EPA AQI (0-500)
    f.append(text(midx / 2, 50, "US EPA AQI (Шкала 0–500)", size=13, bold=True, color=INK))

    epa_tiers = [
        ("0–50: Добре (Good)", "PM2.5: 0.0–9.0 мкг/м³", COLOR_GOOD, "#eafaf1"),
        ("51–100: Помірне (Moderate)", "PM2.5: 9.1–35.4 мкг/м³", COLOR_MODERATE, "#fefde8"),
        ("101–150: Чутливі групи (USG)", "PM2.5: 35.5–55.4 мкг/м³", COLOR_USG, "#fdf2e9"),
        ("151–200: Шкідливе (Unhealthy)", "PM2.5: 55.5–125.4 мкг/м³", COLOR_UNHEALTHY, "#fdedec"),
        ("201–300: Дуже шкідливе (Very Unhealthy)", "PM2.5: 125.5–225.4 мкг/м³", COLOR_VERY_UNH, "#f4ecf7"),
        ("301–500: Небезпечне (Hazardous)", "PM2.5: 225.5–325.4+ мкг/м³", COLOR_HAZARD, "#f9ebea")
    ]

    y_s = 70
    b_h = 34
    g_y = 6
    for i, (title, sub, col, fcol) in enumerate(epa_tiers):
        cy = y_s + i * (b_h + g_y)
        f.append(rect(25, cy, midx - 50, b_h, fill=fcol, stroke=col, sw=1.5, rx=4))
        f.append(text(35, cy + 14, title, size=10, bold=True, color=col, anchor="start"))
        f.append(text(35, cy + 26, sub, size=9, color=MUTED, anchor="start"))

    b_epa, bw_epa, bh_epa = textbox(midx / 2, 340,
                                    "Особливості EPA:\n• Погодинний NowCast / 24h PM, 8h CO/O3\n• Одиниці: мкг/м³, ppm, ppb",
                                    size=10, pad=6, fill="#f8f9fa", stroke="#ced4da", sw=1.1)
    f.append(b_epa)

    # ПРАВА ЧАСТИНА: European CAQI / EEA (0-100 / 5-6 рівнів)
    f.append(text(midx + midx / 2, 50, "European CAQI / EEA (Шкала 0–100)", size=13, bold=True, color=INK))

    caqi_tiers = [
        ("0–25: Дуже низький (Very Low)", "PM2.5: 0–10 мкг/м³", COLOR_GOOD, "#eafaf1"),
        ("25–50: Низький (Low)", "PM2.5: 10–20 мкг/м³", "#2ecc71", "#eafaf1"),
        ("50–75: Середній (Medium)", "PM2.5: 20–25 мкг/м³", COLOR_MODERATE, "#fefde8"),
        ("75–100: Високий (High)", "PM2.5: 25–50 мкг/м³", COLOR_UNHEALTHY, "#fdedec"),
        ("> 100: Дуже високий (Very High)", "PM2.5: 50–75+ мкг/м³", COLOR_VERY_UNH, "#f4ecf7")
    ]

    for i, (title, sub, col, fcol) in enumerate(caqi_tiers):
        cy = y_s + i * (b_h + 8)
        f.append(rect(midx + 25, cy, midx - 50, b_h + 2, fill=fcol, stroke=col, sw=1.5, rx=4))
        f.append(text(midx + 35, cy + 15, title, size=10, bold=True, color=col, anchor="start"))
        f.append(text(midx + 35, cy + 28, sub, size=9, color=MUTED, anchor="start"))

    b_caqi, bw_caqi, bh_caqi = textbox(midx + midx / 2, 340,
                                      "Особливості CAQI / EEA:\n• Окремі сітки: City Background та Roadside\n• Всі гази уніфіковано в мкг/м³ (CO в мг/м³)",
                                      size=10, pad=6, fill="#f8f9fa", stroke="#ced4da", sw=1.1)
    f.append(b_caqi)

    return render(os.path.join(IMG, "epa-vs-caqi-comparison.svg"), W, H, *f)


if __name__ == '__main__':
    fig_piecewise_interpolation()
    fig_multisensor_pipeline()
    fig_nowcast_weighting()
    fig_epa_vs_caqi()
    print("Всі 4 фігури згенеровано успішно у ./img/")
