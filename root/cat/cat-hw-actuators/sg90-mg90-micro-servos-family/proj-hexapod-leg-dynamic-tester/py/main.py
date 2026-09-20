"""
Головна точка входу стендової утиліти та модуль візуалізації результатів випробувань.

Забезпечує:
- Координацію циклічних сценаріїв випробувань мікросервоприводів SG90, SG92R, MG90S та MG90D.
- Цифрову фільтрацію та обчислення інженерних метрик перехідних процесів.
- Псевдографічну ASCII-візуалізацію траєкторій руху, струмових сплесків та спрацьовування захисту в терміналі.
- Генерацію та експорт векторного SVG-звіту високої роздільної здатності.
- Порівняльний аналіз впливу матеріалів зубчастих коліс (нейлон, карбон, метал) на динаміку та ресурс привода.
"""

import math
import os
import sys
from typing import Dict, List, Optional, Tuple

from servo_bench import ServoTestbenchClient, TelemetryRecord, SERVO_CONFIGS
from dynamics_analyzer import DynamicsAnalyzer, DynamicsMetrics


class BenchmarkVisualizer:
    """
    Модуль візуалізації результатів випробувань та побудови порівняльних графіків.
    """

    # Символи маркування кривих для термінального виводу
    MODEL_SYMBOLS = {
        "SG90": "*",
        "SG92R": "+",
        "MG90S": "#",
        "MG90D": "@",
    }

    # Кольорова палітра для векторної SVG-графіки
    MODEL_COLORS = {
        "SG90": "#38bdf8",   # Світло-блакитний (Нейлон)
        "SG92R": "#fbbf24",  # Бурштиновий / Карбон
        "MG90S": "#f87171",  # Кораловий / Метал аналоговий
        "MG90D": "#4ade80",  # Яскраво-зелений / Метал цифровий
    }

    @classmethod
    def render_ascii_step_response(
        cls,
        records_by_model: Dict[str, List[TelemetryRecord]],
        target_angle: float = 90.0,
        width: int = 74,
        height: int = 15,
    ) -> str:
        """
        Формує псевдографічний ASCII-графік порівняння перехідних процесів кута вала.
        """
        all_recs = [r for sublist in records_by_model.values() for r in sublist]
        if not all_recs:
            return "Немає даних для побудови графіка."

        t_min = min(r.timestamp_s for r in all_recs)
        t_max = max(r.timestamp_s for r in all_recs)
        y_min = 0.0
        y_max = max(target_angle * 1.18, max(r.actual_angle_deg for r in all_recs) + 2.0)

        grid = [[" " for _ in range(width)] for _ in range(height)]

        # Горизонтальна лінія цільового кута
        target_row = int((y_max - target_angle) / (y_max - y_min) * (height - 1))
        target_row = max(0, min(height - 1, target_row))
        for x in range(width):
            grid[target_row][x] = "-"

        tag = f" ЦІЛЬ {target_angle:.1f}° "
        start_tag = max(0, (width - len(tag)) // 2)
        for i, ch in enumerate(tag):
            if start_tag + i < width:
                grid[target_row][start_tag + i] = ch

        # Нанесення точок траєкторій моделей
        for model_name, records in records_by_model.items():
            symbol = cls.MODEL_SYMBOLS.get(model_name, "•")
            for r in records:
                x = int((r.timestamp_s - t_min) / (t_max - t_min) * (width - 1))
                y = int((y_max - r.actual_angle_deg) / (y_max - y_min) * (height - 1))
                x = max(0, min(width - 1, x))
                y = max(0, min(height - 1, y))
                # Не затираємо цільову мітку, якщо там немає інших точок
                grid[y][x] = symbol

        lines = [
            "  Кут (°) | ДИНАМІЧНИЙ ВІДГУК ВАЛА НА СХОДИНКУ 0° -> 90°",
            "  --------+" + "-" * width,
        ]
        for row in range(height):
            y_val = y_max - (row / (height - 1)) * (y_max - y_min)
            row_str = "".join(grid[row])
            lines.append(f"  {y_val:6.1f}° |{row_str}")

        lines.append("  --------+" + "-" * width)
        t_min_ms = int(t_min * 1000)
        t_max_ms = int(t_max * 1000)
        spacing = width - len(f"{t_min_ms} мс") - len(f"{t_max_ms} мс") - 2
        lines.append(f"           {t_min_ms} мс" + " " * max(0, spacing) + f"{t_max_ms} мс (Час)")

        # Легенда
        lines.append("  Легенда: " + " | ".join(
            f"[{cls.MODEL_SYMBOLS[m]}] {m} ({SERVO_CONFIGS[m].gear_material})"
            for m in records_by_model.keys()
        ))
        return "\n".join(lines)

    @classmethod
    def render_ascii_current_profile(
        cls,
        records_by_model: Dict[str, List[TelemetryRecord]],
        width: int = 74,
        height: int = 11,
    ) -> str:
        """
        Формує псевдографічний ASCII-графік струму споживання під час робочого переміщення.
        """
        all_recs = [r for sublist in records_by_model.values() for r in sublist]
        if not all_recs:
            return "Немає даних."

        t_min = min(r.timestamp_s for r in all_recs)
        t_max = max(r.timestamp_s for r in all_recs)
        i_min = 0.0
        i_max = max(260.0, max(r.current_ma for r in all_recs) * 1.1)

        grid = [[" " for _ in range(width)] for _ in range(height)]

        for model_name, records in records_by_model.items():
            symbol = cls.MODEL_SYMBOLS.get(model_name, "•")
            for r in records:
                x = int((r.timestamp_s - t_min) / (t_max - t_min) * (width - 1))
                y = int((i_max - r.current_ma) / (i_max - i_min) * (height - 1))
                x = max(0, min(width - 1, x))
                y = max(0, min(height - 1, y))
                grid[y][x] = symbol

        lines = [
            "  Струм(мА)| ДИНАМІКА СПОЖИВАННЯ СТРУМУ ПРИ РОЗГОНІ ТА ГАЛЬМУВАННІ",
            "  ---------+" + "-" * width,
        ]
        for row in range(height):
            i_val = i_max - (row / (height - 1)) * (i_max - i_min)
            row_str = "".join(grid[row])
            lines.append(f"   {i_val:6.1f} |{row_str}")

        lines.append("  ---------+" + "-" * width)
        t_min_ms = int(t_min * 1000)
        t_max_ms = int(t_max * 1000)
        spacing = width - len(f"{t_min_ms} мс") - len(f"{t_max_ms} мс") - 2
        lines.append(f"            {t_min_ms} мс" + " " * max(0, spacing) + f"{t_max_ms} мс")
        return "\n".join(lines)

    @classmethod
    def render_ascii_stall_response(
        cls,
        stall_records_by_model: Dict[str, List[TelemetryRecord]],
        width: int = 74,
        height: int = 11,
    ) -> str:
        """
        Формує графік струмового сплеску блокування вала та спрацьовування захисту стенда.
        """
        all_recs = [r for sublist in stall_records_by_model.values() for r in sublist]
        if not all_recs:
            return "Немає даних стопору."

        t_min = min(r.timestamp_s for r in all_recs)
        t_max = max(r.timestamp_s for r in all_recs)
        i_min = 0.0
        i_max = max(1150.0, max(r.current_ma for r in all_recs) * 1.08)

        grid = [[" " for _ in range(width)] for _ in range(height)]

        # Поріг фіксації аварійного струму (400 мА)
        thr_row = int((i_max - 400.0) / (i_max - i_min) * (height - 1))
        thr_row = max(0, min(height - 1, thr_row))
        for x in range(width):
            grid[thr_row][x] = "."

        for model_name, records in stall_records_by_model.items():
            symbol = cls.MODEL_SYMBOLS.get(model_name, "•")
            for r in records:
                x = int((r.timestamp_s - t_min) / (t_max - t_min) * (width - 1))
                y = int((i_max - r.current_ma) / (i_max - i_min) * (height - 1))
                x = max(0, min(width - 1, x))
                y = max(0, min(height - 1, y))
                grid[y][x] = symbol

        lines = [
            "  Струм(мА)| АВАРІЙНИЙ СТРУМ СТОПОРУ ТА СПРАЦЬОВУВАННЯ ЗАХИСТУ СТЕНДА",
            "  ---------+" + "-" * width,
        ]
        for row in range(height):
            i_val = i_max - (row / (height - 1)) * (i_max - i_min)
            row_str = "".join(grid[row])
            lines.append(f"   {i_val:6.1f} |{row_str}")

        lines.append("  ---------+" + "-" * width)
        lines.append("           Лінія (...) позначає поріг спрацьовування компаратора струму стенда (400 мА)")
        return "\n".join(lines)

    @classmethod
    def render_metrics_table(cls, metrics_list: List[DynamicsMetrics]) -> str:
        """
        Формує структуровану зведену таблицю інженерних метрик перехідних процесів.
        """
        header = (
            f"| {'Модель':<7} | {'Редуктор':<20} | {'Маса':<6} | {'Контур':<17} "
            f"| {'Час нар.':<9} | {'Овершут':<8} | {'Заспок.':<8} | {'Демпф. ζ':<8} "
            f"| {'Струм пік':<9} | {'Струм стоп':<10} | {'Захист':<8} |"
        )
        divider = "|" + "-" * (len(header) - 2) + "|"
        rows = [divider, header, divider]

        for m in metrics_list:
            row = (
                f"| {m.model_name:<7} | {m.gear_material:<20} | {m.mass_g:>4.1f} г | {m.controller_type:<17} "
                f"| {m.rise_time_ms:>6.1f} мс | {m.overshoot_percent:>6.1f}% | {m.settling_time_ms:>6.1f} мс "
                f"| {m.damping_ratio:>8.2f} | {m.peak_motion_current_ma:>6.1f} мА | {m.stall_current_peak_ma:>7.1f} мА "
                f"| {m.protection_trip_delay_ms:>5.1f} мс |"
            )
            rows.append(row)

        rows.append(divider)
        return "\n".join(rows)

    @classmethod
    def export_svg_report(
        cls,
        step_records: Dict[str, List[TelemetryRecord]],
        stall_records: Dict[str, List[TelemetryRecord]],
        metrics_list: List[DynamicsMetrics],
        filename: str = "servo_benchmark_dynamics.svg",
    ) -> str:
        """
        Експортує комплексний векторний SVG-звіт із двома графіками та карточками метрик.
        Працює без зовнішніх бібліотек, формуючи валідну векторну графіку.
        """
        width = 1000
        height = 760

        svg: List[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
            "<defs>",
            '  <linearGradient id="panelGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
            '    <stop offset="0%" stop-color="#1e293b"/>',
            '    <stop offset="100%" stop-color="#0f172a"/>',
            "  </linearGradient>",
            "</defs>",
            "<style>",
            '  text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }',
            "  .title { font-size: 20px; font-weight: 700; fill: #f8fafc; }",
            "  .subtitle { font-size: 13px; fill: #94a3b8; }",
            "  .panel-title { font-size: 14px; font-weight: 600; fill: #e2e8f0; }",
            "  .axis-text { font-size: 11px; fill: #64748b; }",
            "  .legend-text { font-size: 12px; font-weight: 500; fill: #cbd5e1; }",
            "  .grid-line { stroke: #334155; stroke-dasharray: 3,4; stroke-width: 1; }",
            "  .target-line { stroke: #e2e8f0; stroke-dasharray: 6,4; stroke-width: 1.5; stroke-opacity: 0.7; }",
            "  .card-val { font-size: 15px; font-weight: 700; }",
            "  .card-lbl { font-size: 11px; fill: #94a3b8; }",
            "</style>",
            f'<rect width="{width}" height="{height}" fill="#0b0f19"/>',
            '<!-- Заголовок -->',
            '<text x="40" y="42" class="title">СТЕНДОВЕ ПОРІВНЯННЯ ДИНАМІКИ 9-ГРАМОВИХ МІКРОСЕРВОПРИВОДІВ</text>',
            '<text x="40" y="64" class="subtitle">Порівняльний аналіз TowerPro SG90, SG92R, MG90S та MG90D (перехідні процеси та захист блокування)</text>',
        ]

        # -------------------------------------------------------------
        # 1. ПАНЕЛЬ ГРАФІКА 1: Кут вала (Step Response 0 -> 90°)
        # -------------------------------------------------------------
        p1_x, p1_y, p1_w, p1_h = 40, 95, 440, 300
        svg.append(f'<rect x="{p1_x}" y="{p1_y}" width="{p1_w}" height="{p1_h}" rx="8" fill="url(#panelGrad)" stroke="#334155"/>')
        svg.append(f'<text x="{p1_x + 16}" y="{p1_y + 26}" class="panel-title">Перехідний процес кута вала (0° → 90°)</text>')

        # Вісь Y: 0° .. 110°, Вісь X: 0 .. 450 мс
        y1_max = 110.0
        x1_max_s = 0.45

        # Горизонтальні лінії сітки та цільова лінія
        for deg in (0, 30, 60, 90, 100):
            y_pos = p1_y + p1_h - 35 - (deg / y1_max) * (p1_h - 75)
            line_style = 'class="target-line"' if deg == 90 else 'class="grid-line"'
            svg.append(f'<line x1="{p1_x + 45}" y1="{y_pos}" x2="{p1_x + p1_w - 20}" y2="{y_pos}" {line_style}/>')
            svg.append(f'<text x="{p1_x + 38}" y="{y_pos + 4}" class="axis-text" text-anchor="end">{deg}°</text>')

        svg.append(f'<text x="{p1_x + p1_w - 25}" y="{p1_y + p1_h - 40 - (90.0 / y1_max) * (p1_h - 75)}" class="axis-text" fill="#e2e8f0">Ціль 90°</text>')

        # Побудова ліній кута для кожної моделі
        for name, records in step_records.items():
            color = cls.MODEL_COLORS.get(name, "#ffffff")
            points = []
            for r in records:
                px = p1_x + 45 + (min(r.timestamp_s, x1_max_s) / x1_max_s) * (p1_w - 65)
                py = p1_y + p1_h - 35 - (r.actual_angle_deg / y1_max) * (p1_h - 75)
                points.append(f"{px:.1f},{py:.1f}")
            svg.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round"/>')

        svg.append(f'<text x="{p1_x + 45}" y="{p1_y + p1_h - 14}" class="axis-text">0 мс</text>')
        svg.append(f'<text x="{p1_x + p1_w - 20}" y="{p1_y + p1_h - 14}" class="axis-text" text-anchor="end">450 мс</text>')

        # -------------------------------------------------------------
        # 2. ПАНЕЛЬ ГРАФІКА 2: Аварійний струм та відсічка захисту
        # -------------------------------------------------------------
        p2_x, p2_y, p2_w, p2_h = 520, 95, 440, 300
        svg.append(f'<rect x="{p2_x}" y="{p2_y}" width="{p2_w}" height="{p2_h}" rx="8" fill="url(#panelGrad)" stroke="#334155"/>')
        svg.append(f'<text x="{p2_x + 16}" y="{p2_y + 26}" class="panel-title">Струм аварійного блокування та відсічка стенда</text>')

        i2_max = 1200.0
        for cur_ma in (0, 300, 600, 900, 1100):
            y_pos = p2_y + p2_h - 35 - (cur_ma / i2_max) * (p2_h - 75)
            svg.append(f'<line x1="{p2_x + 48}" y1="{y_pos}" x2="{p2_x + p2_w - 20}" y2="{y_pos}" class="grid-line"/>')
            svg.append(f'<text x="{p2_x + 42}" y="{y_pos + 4}" class="axis-text" text-anchor="end">{cur_ma}</text>')

        # Побудова ліній струму блокування
        for name, records in stall_records.items():
            color = cls.MODEL_COLORS.get(name, "#ffffff")
            points = []
            for r in records:
                px = p2_x + 48 + (min(r.timestamp_s, x1_max_s) / x1_max_s) * (p2_w - 68)
                py = p2_y + p2_h - 35 - (r.current_ma / i2_max) * (p2_h - 75)
                points.append(f"{px:.1f},{py:.1f}")
            svg.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round"/>')

        svg.append(f'<text x="{p2_x + 48}" y="{p2_y + p2_h - 14}" class="axis-text">0 мс</text>')
        svg.append(f'<text x="{p2_x + p2_w - 20}" y="{p2_y + p2_h - 14}" class="axis-text" text-anchor="end">450 мс</text>')

        # -------------------------------------------------------------
        # 3. ЛЕГЕНДА СЕРВОПРИВОДІВ
        # -------------------------------------------------------------
        leg_y = 415
        svg.append(f'<rect x="40" y="{leg_y}" width="920" height="42" rx="6" fill="#1e293b" stroke="#334155"/>')
        leg_items = [
            ("SG90", "Нейлонові шестерні (POM), 9г, Аналоговий 50 Гц"),
            ("SG92R", "Вуглепластик (CF-POM), 9г, Аналоговий 50 Гц"),
            ("MG90S", "Металеві шестерні + підшипник, 13.4г, Аналоговий 50 Гц"),
            ("MG90D", "Металеві шестерні + підшипник, 13.4г, Цифровий 300 Гц"),
        ]
        col_w = 920 // len(leg_items)
        for idx, (m_name, desc) in enumerate(leg_items):
            lx = 55 + idx * col_w
            c = cls.MODEL_COLORS[m_name]
            svg.append(f'<circle cx="{lx}" cy="{leg_y + 21}" r="6" fill="{c}"/>')
            svg.append(f'<text x="{lx + 12}" y="{leg_y + 25}" class="legend-text" fill="{c}">{m_name}</text>')
            short_desc = desc.split(",")[0]
            svg.append(f'<text x="{lx + 62}" y="{leg_y + 25}" class="axis-text">{short_desc}</text>')

        # -------------------------------------------------------------
        # 4. КАРТКИ ПОРІВНЯЛЬНИХ ІНЖЕНЕРНИХ МЕТРИК
        # -------------------------------------------------------------
        cards_y = 475
        card_w = 218
        card_h = 245
        for idx, m in enumerate(metrics_list):
            cx = 40 + idx * (card_w + 16)
            c = cls.MODEL_COLORS[m.model_name]
            svg.append(f'<rect x="{cx}" y="{cards_y}" width="{card_w}" height="{card_h}" rx="8" fill="url(#panelGrad)" stroke="{c}" stroke-width="1.5"/>')
            svg.append(f'<text x="{cx + 16}" y="{cards_y + 30}" class="panel-title" fill="{c}">{m.model_name}</text>')
            svg.append(f'<text x="{cx + 16}" y="{cards_y + 48}" class="axis-text">{m.gear_material}</text>')

            # Рядки параметрів
            params = [
                ("Маса привода:", f"{m.mass_g:.1f} г"),
                ("Час наростання:", f"{m.rise_time_ms:.1f} мс"),
                ("Час заспокоєння:", f"{m.settling_time_ms:.1f} мс"),
                ("Перерегулювання:", f"{m.overshoot_percent:.1f}% ({m.overshoot_deg:.1f}°)"),
                ("Коефіцієнт ζ:", f"{m.damping_ratio:.2f}"),
                ("Пік струму руху:", f"{m.peak_motion_current_ma:.0f} мА"),
                ("Струм блокування:", f"{m.stall_current_peak_ma:.0f} мА"),
                ("Відсічка захисту:", f"{m.protection_trip_delay_ms:.1f} мс"),
            ]
            for p_idx, (p_name, p_val) in enumerate(params):
                py = cards_y + 72 + p_idx * 21
                svg.append(f'<text x="{cx + 16}" y="{py}" class="card-lbl">{p_name}</text>')
                svg.append(f'<text x="{cx + card_w - 16}" y="{py}" class="card-val" fill="#f1f5f9" text-anchor="end">{p_val}</text>')

        svg.append("</svg>")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(svg))

        return os.path.abspath(filename)


def main() -> None:
    """
    Головний сценарій стендового тестування лінійки сервоприводів.
    """
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 80)
    print(" АВТОМАТИЗОВАНЕ СТЕНДОВЕ ТЕСТУВАННЯ МІКРОСЕРВОПРИВОДІВ СЕРІЇ SG90 ТА MG90")
    print(" Двостороння телеметрія, аналіз динаміки демпфування та захист від блокування")
    print("=" * 80)

    target_models = ["SG90", "SG92R", "MG90S", "MG90D"]
    step_records_by_model: Dict[str, List[TelemetryRecord]] = {}
    stall_records_by_model: Dict[str, List[TelemetryRecord]] = {}
    metrics_by_model: Dict[str, DynamicsMetrics] = {}

    # 1. Виконання тестових програм для кожної моделі
    for model_name in target_models:
        print(f"\n[ТЕСТУВАННЯ] Ініціалізація стендового клієнта для {model_name}...")
        client = ServoTestbenchClient(model_name=model_name, use_simulator=True)
        client.connect()

        # Тест 1: Сходинкове збурення 0° -> 90°
        print(f"  -> Запуск Step Response Test (0.0° -> 90.0°)...")
        raw_step = client.run_step_test(from_angle=0.0, to_angle=90.0, duration_s=0.45)
        filtered_step = DynamicsAnalyzer.filter_telemetry(raw_step, window_size=5)
        step_records_by_model[model_name] = filtered_step

        # Розрахунок метрик перехідного процесу
        step_metrics = DynamicsAnalyzer.analyze_step_response(
            records=filtered_step,
            target_angle=90.0,
            model_name=model_name,
            tolerance_pct=2.0,
        )

        # Тест 2: Швидкісний циклічний реверс вала (30° <-> 150°)
        print(f"  -> Запуск Fast Reversal Test (30° <-> 150° @ 500°/с)...")
        client.run_reversal_sweep(angle_a=30.0, angle_b=150.0, speed_deg_s=500.0, cycles=1)

        # Тест 3: Аварійне блокування ротора на перешкоді 45°
        print(f"  -> Запуск Stall Protection Test (команда 90°, перешкода на 45°)...")
        raw_stall = client.run_stall_test(target_angle=90.0, obstacle_angle=45.0, duration_s=0.45)
        filtered_stall = DynamicsAnalyzer.filter_telemetry(raw_stall, window_size=3)
        stall_records_by_model[model_name] = filtered_stall

        # Вимірювання параметрів захисту блокування
        stall_peak, trip_delay = DynamicsAnalyzer.analyze_stall_protection(
            records=filtered_stall,
            stall_threshold_ma=400.0,
            cut_off_threshold_ma=120.0,
        )

        # Оновлення підсумкових метрик моделі
        final_metrics = DynamicsMetrics(
            model_name=step_metrics.model_name,
            gear_material=step_metrics.gear_material,
            controller_type=step_metrics.controller_type,
            mass_g=step_metrics.mass_g,
            step_amplitude_deg=step_metrics.step_amplitude_deg,
            rise_time_ms=step_metrics.rise_time_ms,
            settling_time_ms=step_metrics.settling_time_ms,
            overshoot_deg=step_metrics.overshoot_deg,
            overshoot_percent=step_metrics.overshoot_percent,
            damping_ratio=step_metrics.damping_ratio,
            peak_motion_current_ma=step_metrics.peak_motion_current_ma,
            steady_current_ma=step_metrics.steady_current_ma,
            stall_current_peak_ma=stall_peak,
            protection_trip_delay_ms=trip_delay,
        )
        metrics_by_model[model_name] = final_metrics
        client.disconnect()

    # 2. Виведення результатів у термінал
    metrics_list = [metrics_by_model[m] for m in target_models]

    print("\n" + "=" * 80)
    print(" ЗВЕДЕНА ТАБЛИЦЯ ІНЖЕНЕРНИХ ХАРАКТЕРИСТИК МІКРОСЕРВОПРИВОДІВ")
    print("=" * 80)
    print(BenchmarkVisualizer.render_metrics_table(metrics_list))

    print("\n" + "=" * 80)
    print(" ГРАФІК 1: ПОРІВНЯЛЬНИЙ ДИНАМІЧНИЙ ВІДГУК ВАЛА НА СХОДИНКУ (ASCII)")
    print("=" * 80)
    print(BenchmarkVisualizer.render_ascii_step_response(step_records_by_model, target_angle=90.0))

    print("\n" + "=" * 80)
    print(" ГРАФІК 2: ДИНАМІКА СПОЖИВАННЯ СТРУМУ ПІД ЧАС МАНЕВРУ (ASCII)")
    print("=" * 80)
    print(BenchmarkVisualizer.render_ascii_current_profile(step_records_by_model))

    print("\n" + "=" * 80)
    print(" ГРАФІК 3: СТРУМ БЛОКУВАННЯ ТА СПРАЦЬОВУВАННЯ ЗАХИСТУ СТЕНДА (ASCII)")
    print("=" * 80)
    print(BenchmarkVisualizer.render_ascii_stall_response(stall_records_by_model))

    # 3. Експорт SVG звіту
    svg_path = BenchmarkVisualizer.export_svg_report(
        step_records=step_records_by_model,
        stall_records=stall_records_by_model,
        metrics_list=metrics_list,
        filename="servo_benchmark_dynamics.svg",
    )
    print(f"\n[ВЕКТОРНИЙ ЗВІТ] Графіки високої роздільної здатності збережено у файл:")
    print(f"  -> {svg_path}")

    # 4. Формування підсумкового інженерного звіту
    print("\n" + DynamicsAnalyzer.generate_comparative_summary(metrics_list))


if __name__ == "__main__":
    main()
