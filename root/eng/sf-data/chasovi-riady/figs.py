#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate SVG figures for chasovi-riady topic."""

import os
import sys

# Add scripts/ directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')

def make_regular_vs_irregular():
    path = os.path.join(IMG_DIR, 'regular-vs-irregular-series.svg')
    w, h = 820, 360
    frags = []

    # Section 1: Regular series
    frags.append(rect(20, 45, 780, 135, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(35, 70, "1. Регулярний часовий ряд (сталий інтервал Δt = 10s)", size=13, color=LINE, anchor="start", bold=True))
    frags.append(text(35, 88, "Передбачувана часова сітка: пряма адресація, ефективне дельта-стиснення", size=11, color=MUTED, anchor="start"))

    # Time axis 1
    frags.append(line(50, 140, 750, 140, color="#94a3b8", sw=1.5))
    frags.append(arrow(740, 140, 760, 140, color="#94a3b8", sw=1.5))
    frags.append(text(765, 144, "Час (t)", size=11, color=MUTED, anchor="start"))

    t_points = [
        (80, "t₀", 120, "24.1"),
        (160, "t₀+10s", 110, "25.3"),
        (240, "t₀+20s", 105, "26.0"),
        (320, "t₀+30s", None, "—"), # Missing
        (400, "t₀+40s", 115, "24.8"),
        (480, "t₀+50s", 125, "23.5"),
        (560, "t₀+60s", 130, "22.9"),
        (640, "t₀+70s", 120, "24.2"),
    ]

    for x, label, y_val, val_str in t_points:
        frags.append(line(x, 135, x, 145, color="#64748b", sw=1.5))
        frags.append(text(x, 160, label, size=10, color=MUTED, anchor="middle"))
        if y_val is not None:
            frags.append(circle(x, y_val, 4.5, fill="#2563eb", stroke="#1d4ed8", sw=1.5))
            frags.append(text(x, y_val - 10, val_str, size=10, color="#1e293b", anchor="middle", bold=True))
        else:
            # Missing sample marker
            frags.append(circle(x, 140, 4.5, fill="#ffffff", stroke="#ef4444", sw=1.5))
            frags.append(text(x, 120, "Пропуск (NaN)", size=10, color="#ef4444", anchor="middle", bold=True))

    # Connect regular points
    reg_coords = [(80, 120), (160, 110), (240, 105), (400, 115), (480, 125), (560, 130), (640, 120)]
    for i in range(len(reg_coords) - 1):
        x1, y1 = reg_coords[i]
        x2, y2 = reg_coords[i+1]
        if x2 - x1 <= 90:
            frags.append(line(x1, y1, x2, y2, color="#3b82f6", sw=1.5))
        else:
            frags.append(line(x1, y1, x2, y2, color="#94a3b8", sw=1.2, dash="4 4"))

    # Section 2: Irregular series
    frags.append(rect(20, 195, 780, 145, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(35, 220, "2. Нерегулярний / Подієвий ряд (довільний інтервал Δt)", size=13, color=LINE, anchor="start", bold=True))
    frags.append(text(35, 238, "Точки з'являються за подіями: обов'язковий явний timestamp, необхідна інтерполяція", size=11, color=MUTED, anchor="start"))

    # Time axis 2
    frags.append(line(50, 300, 750, 300, color="#94a3b8", sw=1.5))
    frags.append(arrow(740, 300, 760, 300, color="#94a3b8", sw=1.5))
    frags.append(text(765, 304, "Час (t)", size=11, color=MUTED, anchor="start"))

    irreg_points = [
        (70, "t=0.0s", 280, "1"),
        (130, "t=2.4s", 265, "3"),
        (280, "t=9.1s", 270, "2"),
        (350, "t=11.0s", 255, "5"),
        (510, "t=18.6s", 275, "1"),
        (670, "t=26.2s", 260, "4"),
    ]

    for x, label, y_val, val_str in irreg_points:
        frags.append(line(x, 295, x, 305, color="#64748b", sw=1.5))
        frags.append(text(x, 320, label, size=10, color=MUTED, anchor="middle"))
        frags.append(circle(x, y_val, 4.5, fill="#059669", stroke="#047857", sw=1.5))
        frags.append(text(x, y_val - 10, val_str, size=10, color="#1e293b", anchor="middle", bold=True))

    for i in range(len(irreg_points) - 1):
        x1, _, y1, _ = irreg_points[i]
        x2, _, y2, _ = irreg_points[i+1]
        frags.append(line(x1, y1, x2, y2, color="#10b981", sw=1.5))

    render(path, w, h, *frags, title="Регулярний проти нерегулярного часового ряду")


def make_metric_types_anatomy():
    path = os.path.join(IMG_DIR, 'metric-types-anatomy.svg')
    w, h = 840, 420
    frags = []

    # 4 columns for metric types
    col_w = 185
    gap = 15
    start_x = 25
    y_top = 50
    card_h = 345

    types_data = [
        {
            "name": "Gauge",
            "ukr": "Миттєвий рівень",
            "color": "#2563eb",
            "bg": "#eff6ff",
            "border": "#bfdbfe",
            "desc": "Значення вільно зростає і падає в часі.",
            "examples": ["Температура CPU", "Використана пам'ять", "Активні з'єднання"],
            "agg": "avg(), min(), max(), last()",
            "points": [(15, 45), (45, 20), (75, 55), (105, 30), (135, 40)]
        },
        {
            "name": "Counter",
            "ukr": "Монотонний лічильник",
            "color": "#059669",
            "bg": "#f0fdf4",
            "border": "#bbf7d0",
            "desc": "Тільки зростає; скидається до 0 при рестарті.",
            "examples": ["Оброблено запитів", "Передано байтів", "Кількість помилок"],
            "agg": "rate(), irate(), increase()",
            "points": [(15, 55), (45, 40), (75, 25), (85, 58), (115, 42), (135, 30)] # with reset
        },
        {
            "name": "Histogram",
            "ukr": "Бакетований розподіл",
            "color": "#d97706",
            "bg": "#fffbeb",
            "border": "#fde68a",
            "desc": "Кумулятивні лічильники за межами (le) + sum + count.",
            "examples": ["Затримка запитів (мс)", "Розмір payload", "Тривалість транзакцій"],
            "agg": "histogram_quantile(φ, ...)",
            "bars": [(15, 50, 20), (45, 40, 30), (75, 25, 45), (105, 15, 55)]
        },
        {
            "name": "Summary",
            "ukr": "Квантилі на клієнті",
            "color": "#7c3aed",
            "bg": "#faf5ff",
            "border": "#e9d5ff",
            "desc": "Обчислює p50/p90/p99 у процесі на ковзному вікні.",
            "examples": ["Точні квантилі інстансу", "Фіксований буфер пам'яті", "Висока точність p99"],
            "agg": "Не можна агрегувати між вузлами",
            "quantiles": [("p50", "42 ms"), ("p90", "118 ms"), ("p99", "340 ms")]
        }
    ]

    for i, t in enumerate(types_data):
        cx = start_x + i * (col_w + gap)
        # Card outline
        frags.append(rect(cx, y_top, col_w, card_h, fill=t["bg"], stroke=t["border"], rx=8))
        
        # Header
        frags.append(rect(cx, y_top, col_w, 42, fill=t["color"], stroke=t["color"], rx=8))
        # Mask lower corners of header rect
        frags.append(rect(cx, y_top + 30, col_w, 12, fill=t["color"], stroke=t["color"], rx=0))
        frags.append(text(cx + col_w/2, y_top + 20, t["name"], size=14, color="#ffffff", anchor="middle", bold=True))
        frags.append(text(cx + col_w/2, y_top + 34, t["ukr"], size=10, color="#ffffff", anchor="middle"))

        # Mini plot area
        plot_y = y_top + 52
        plot_h = 75
        frags.append(rect(cx + 10, plot_y, col_w - 20, plot_h, fill="#ffffff", stroke="#cbd5e1", rx=4))

        if "points" in t:
            # Draw axis
            frags.append(line(cx + 15, plot_y + plot_h - 10, cx + col_w - 15, plot_y + plot_h - 10, color="#cbd5e1", sw=1))
            pts = t["points"]
            for j in range(len(pts) - 1):
                x1 = cx + 15 + pts[j][0]
                y1 = plot_y + pts[j][1]
                x2 = cx + 15 + pts[j+1][0]
                y2 = plot_y + pts[j+1][1]
                if t["name"] == "Counter" and j == 2: # Reset line
                    frags.append(line(x1, y1, x2, y2, color="#ef4444", sw=1.2, dash="2 2"))
                else:
                    frags.append(line(x1, y1, x2, y2, color=t["color"], sw=1.8))
                frags.append(circle(x1, y1, 2.5, fill=t["color"], stroke=t["color"], sw=1))
            frags.append(circle(cx + 15 + pts[-1][0], plot_y + pts[-1][1], 2.5, fill=t["color"], stroke=t["color"], sw=1))
        elif "bars" in t:
            # Draw histogram bars
            for bx, by, bh in t["bars"]:
                frags.append(rect(cx + 10 + bx, plot_y + by, 22, bh, fill=t["color"], stroke=t["color"], rx=2))
        elif "quantiles" in t:
            # Draw quantile tags
            qy = plot_y + 15
            for qk, qv in t["quantiles"]:
                frags.append(rect(cx + 18, qy, 42, 16, fill="#7c3aed", stroke="#7c3aed", rx=3))
                frags.append(text(cx + 39, qy + 12, qk, size=10, color="#ffffff", anchor="middle", bold=True))
                frags.append(text(cx + 105, qy + 12, qv, size=11, color="#1e293b", anchor="middle", bold=True))
                qy += 18

        # Description
        frags.append(text(cx + col_w/2, y_top + 142, t["desc"], size=10, color="#334155", anchor="middle"))

        # Examples block
        frags.append(rect(cx + 8, y_top + 162, col_w - 16, 92, fill="#ffffff", stroke="#e2e8f0", rx=4))
        frags.append(text(cx + 14, y_top + 178, "Типові випадки:", size=10, color=MUTED, anchor="start", bold=True))
        for k, ex in enumerate(t["examples"]):
            frags.append(text(cx + 16, y_top + 196 + k * 18, "• " + ex, size=10, color="#1e293b", anchor="start"))

        # Aggregation block
        frags.append(rect(cx + 8, y_top + 264, col_w - 16, 70, fill="#ffffff", stroke="#e2e8f0", rx=4))
        frags.append(text(cx + 14, y_top + 280, "Агрегація / Запити:", size=10, color=MUTED, anchor="start", bold=True))
        frags.append(text(cx + 14, y_top + 302, t["agg"], size=10, color=t["color"], anchor="start", bold=True))

    render(path, w, h, *frags, title="Анатомія чотирьох фундаментальних типів метрик")


def make_timeseries_inverted_index():
    path = os.path.join(IMG_DIR, 'timeseries-inverted-index.svg')
    w, h = 820, 370
    frags = []

    # Left box: Incoming query / Metric Series identifier
    frags.append(rect(20, 50, 230, 290, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(135, 75, "Ідентифікатор ряду (Labels)", size=12, color=LINE, anchor="middle", bold=True))
    frags.append(text(135, 92, "Набір пар ключ=значення", size=10, color=MUTED, anchor="middle"))

    labels = [
        ('__name__', 'http_requests_total', "#2563eb"),
        ('method', 'POST', "#059669"),
        ('status', '200', "#d97706"),
        ('env', 'prod', "#7c3aed"),
    ]

    ly = 115
    for k, v, col in labels:
        frags.append(rect(30, ly, 210, 36, fill="#ffffff", stroke=col, rx=4))
        frags.append(text(40, ly + 22, f'{k}="{v}"', size=11, color="#1e293b", anchor="start", bold=True))
        ly += 45

    frags.append(text(135, 308, "Запит: SELECT series_id", size=10, color=MUTED, anchor="middle"))
    frags.append(text(135, 325, 'WHERE method="POST" AND env="prod"', size=10, color="#1e293b", anchor="middle", bold=True))

    # Center box: Inverted Index (Posting Lists)
    frags.append(rect(270, 50, 270, 290, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(405, 75, "Інвертований індекс (Posting Lists)", size=12, color=LINE, anchor="middle", bold=True))
    frags.append(text(405, 92, "Відображення: Мітка → Список ID рядів", size=10, color=MUTED, anchor="middle"))

    posting_lists = [
        ('method="POST"', "{101, 105, 114, 120}", "#059669"),
        ('status="200"', "{101, 102, 105, 114, 130}", "#d97706"),
        ('env="prod"', "{101, 105, 109, 114}", "#7c3aed"),
        ('env="dev"', "{102, 108, 120, 130}", "#94a3b8"),
    ]

    py = 115
    for term, ids, col in posting_lists:
        frags.append(rect(280, py, 250, 36, fill="#ffffff", stroke="#e2e8f0", rx=4))
        frags.append(text(290, py + 16, term, size=10, color=col, anchor="start", bold=True))
        frags.append(text(290, py + 29, ids, size=10, color="#334155", anchor="start"))
        py += 45

    # Intersect operation
    frags.append(rect(280, 298, 250, 32, fill="#eff6ff", stroke="#3b82f6", rx=4))
    frags.append(text(405, 318, "Перетин: {101, 105, 114} (AND)", size=10, color="#1d4ed8", anchor="middle", bold=True))

    # Connect Left to Center
    frags.append(arrow(250, 160, 270, 160, color="#64748b", sw=1.5))
    frags.append(arrow(250, 250, 270, 250, color="#64748b", sw=1.5))

    # Right box: Data Blocks & Series Time Lines
    frags.append(rect(560, 50, 240, 290, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(680, 75, "Блоки часових рядів на диску", size=12, color=LINE, anchor="middle", bold=True))
    frags.append(text(680, 92, "Дані відфільтрованих Series ID", size=10, color=MUTED, anchor="middle"))

    matched_series = [
        ("Series #101", "240 семплів (Gorilla 2.1 B/pt)", "#2563eb"),
        ("Series #105", "240 семплів (Gorilla 1.9 B/pt)", "#2563eb"),
        ("Series #114", "240 семплів (Gorilla 2.0 B/pt)", "#2563eb"),
    ]

    sy = 120
    for s_title, s_info, col in matched_series:
        frags.append(rect(575, sy, 210, 52, fill="#ffffff", stroke="#3b82f6", rx=4))
        frags.append(text(585, sy + 20, s_title, size=11, color=col, anchor="start", bold=True))
        frags.append(text(585, sy + 38, s_info, size=10, color="#64748b", anchor="start"))
        sy += 65

    # Connect Center to Right
    frags.append(arrow(530, 314, 560, 200, color="#2563eb", sw=1.8))

    render(path, w, h, *frags, title="Інвертований індекс тегів та ідентифікатори рядів (Series ID)")


def make_downsampling_retention_pipeline():
    path = os.path.join(IMG_DIR, 'downsampling-retention-pipeline.svg')
    w, h = 820, 370
    frags = []

    # Ingestion pipe to 3 tiers
    # Tier 1: Raw
    frags.append(rect(20, 55, 230, 285, fill="#f8fafc", stroke="#3b82f6", rx=8))
    frags.append(rect(20, 55, 230, 36, fill="#3b82f6", stroke="#3b82f6", rx=8))
    frags.append(rect(20, 79, 230, 12, fill="#3b82f6", stroke="#3b82f6", rx=0))
    frags.append(text(135, 78, "Tier 1: Сирі точки (Raw)", size=13, color="#ffffff", anchor="middle", bold=True))

    frags.append(text(135, 115, "Інтервал: 10 секунд (Δt = 10s)", size=10, color="#1e293b", anchor="middle", bold=True))
    frags.append(text(135, 135, "Точність: 100% (усі сплески та шуми)", size=10, color=MUTED, anchor="middle"))
    frags.append(text(135, 155, "Зберігання: RAM + NVMe SSD", size=10, color=MUTED, anchor="middle"))
    
    frags.append(rect(35, 175, 200, 60, fill="#ffffff", stroke="#cbd5e1", rx=4))
    frags.append(text(135, 195, "Строк зберігання (TTL):", size=10, color=MUTED, anchor="middle"))
    frags.append(text(135, 218, "7 – 14 днів", size=15, color="#2563eb", anchor="middle", bold=True))

    frags.append(text(135, 260, "Призначення:", size=10, color=MUTED, anchor="middle", bold=True))
    frags.append(text(135, 280, "Алерти в реальному часі,", size=10, color="#334155", anchor="middle"))
    frags.append(text(135, 298, "пошук аномалій та інцидентів", size=10, color="#334155", anchor="middle"))

    # Arrow 1 -> 2
    frags.append(arrow(250, 195, 285, 195, color="#64748b", sw=2))
    frags.append(text(267, 185, "5m Rollup", size=10, color=MUTED, anchor="middle"))

    # Tier 2: 5-minute rollup
    frags.append(rect(285, 55, 240, 285, fill="#f8fafc", stroke="#059669", rx=8))
    frags.append(rect(285, 55, 240, 36, fill="#059669", stroke="#059669", rx=8))
    frags.append(rect(285, 79, 240, 12, fill="#059669", stroke="#059669", rx=0))
    frags.append(text(405, 78, "Tier 2: Зріджені 5-хв агрегати", size=13, color="#ffffff", anchor="middle", bold=True))

    frags.append(text(405, 115, "Інтервал: 5 хвилин (30 точок → 1)", size=10, color="#1e293b", anchor="middle", bold=True))
    frags.append(text(405, 135, "Зберігає: min, max, sum, count", size=10, color=MUTED, anchor="middle"))
    frags.append(text(405, 155, "Стиснення обсягу: ~30×", size=10, color=MUTED, anchor="middle"))

    frags.append(rect(305, 175, 200, 60, fill="#ffffff", stroke="#cbd5e1", rx=4))
    frags.append(text(405, 195, "Строк зберігання (TTL):", size=10, color=MUTED, anchor="middle"))
    frags.append(text(405, 218, "30 – 90 днів", size=15, color="#059669", anchor="middle", bold=True))

    frags.append(text(405, 260, "Призначення:", size=10, color=MUTED, anchor="middle", bold=True))
    frags.append(text(405, 280, "Тижневі графіки дашбордів,", size=10, color="#334155", anchor="middle"))
    frags.append(text(405, 298, "аналіз навантаження та SLA", size=10, color="#334155", anchor="middle"))

    # Arrow 2 -> 3
    frags.append(arrow(525, 195, 560, 195, color="#64748b", sw=2))
    frags.append(text(542, 185, "1h Rollup", size=10, color=MUTED, anchor="middle"))

    # Tier 3: 1-hour rollup
    frags.append(rect(560, 55, 240, 285, fill="#f8fafc", stroke="#7c3aed", rx=8))
    frags.append(rect(560, 55, 240, 36, fill="#7c3aed", stroke="#7c3aed", rx=8))
    frags.append(rect(560, 79, 240, 12, fill="#7c3aed", stroke="#7c3aed", rx=0))
    frags.append(text(680, 78, "Tier 3: Годинні агрегати", size=13, color="#ffffff", anchor="middle", bold=True))

    frags.append(text(680, 115, "Інтервал: 1 година (360 точок → 1)", size=10, color="#1e293b", anchor="middle", bold=True))
    frags.append(text(680, 135, "Зберігає: min, max, sum, count", size=10, color=MUTED, anchor="middle"))
    frags.append(text(680, 155, "Стиснення обсягу: ~360×", size=10, color=MUTED, anchor="middle"))

    frags.append(rect(580, 175, 200, 60, fill="#ffffff", stroke="#cbd5e1", rx=4))
    frags.append(text(680, 195, "Строк зберігання (TTL):", size=10, color=MUTED, anchor="middle"))
    frags.append(text(680, 218, "1 – 3 роки", size=15, color="#7c3aed", anchor="middle", bold=True))

    frags.append(text(680, 260, "Призначення:", size=10, color=MUTED, anchor="middle", bold=True))
    frags.append(text(680, 280, "Річні бізнес-тренди,", size=10, color="#334155", anchor="middle"))
    frags.append(text(680, 298, "прогнозування ємності (capacity)", size=10, color="#334155", anchor="middle"))

    render(path, w, h, *frags, title="Конвеєр зріджування (Downsampling) та строки зберігання метрик")


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    make_regular_vs_irregular()
    make_metric_types_anatomy()
    make_timeseries_inverted_index()
    make_downsampling_retention_pipeline()
    print("All figures generated successfully in", IMG_DIR)

if __name__ == '__main__':
    main()
