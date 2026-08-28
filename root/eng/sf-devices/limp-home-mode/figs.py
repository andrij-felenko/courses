#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор діаграм для теми limp-home-mode (Кульгавий режим)."""

import os
import sys

def build_subsystem_matrix_svg(out_path):
    """Генерує матрицю деградації підсистем у різних режимах роботи."""
    w, h = 960, 560
    
    modes = [
        {"name": "NORMAL", "sub": "Повний", "color": "#2e7d32", "bg": "#e8f5e9"},
        {"name": "THROTTLED", "sub": "Термо-спад", "color": "#f57f17", "bg": "#fffde7"},
        {"name": "LIMP L1", "sub": "Тяга 50%", "color": "#e65100", "bg": "#fff3e0"},
        {"name": "LIMP L2", "sub": "Доліт 35%", "color": "#c62828", "bg": "#ffebee"},
        {"name": "SAFE STATE", "sub": "Стоп/Посадка", "color": "#37474f", "bg": "#eceff1"}
    ]
    
    subsystems = [
        {"name": "Силові приводи (ESC/Мотори)", "detail": "ШІМ, струм фаз, динаміка"},
        {"name": "Критична навігація (IMU/FCU)", "detail": "Оцінка кута, стабілізація"},
        {"name": "Канал зв'язку / Телеметрія", "detail": "Радіолінк, резервний CAN"},
        {"name": "Оптичний потік та лідар", "detail": "Висотомір, сенсори землі"},
        {"name": "Супутній комп'ютер (SBC/AI)", "detail": "Нейромережі, трекінг цілей"},
        {"name": "Підвіс камери та корисне", "detail": "Сервоприводи, живлення камери"},
        {"name": "Підсвітка та нагрівачі", "detail": "Фари, обігрів трубки Піто"}
    ]
    
    matrix = [
        [("100% тяга / 25кГц", 0), ("80% струм / 16кГц", 1), ("50% струм / 10кГц", 2), ("35% тяга (спуск)", 2), ("0% (Вимкнено)", 3)],
        [("1000Гц FOC / Повна", 0), ("1000Гц FOC / Повна", 0), ("500Гц / Стабільний", 1), ("250Гц / Базовий кут", 1), ("Стоп-лог в NVS", 3)],
        [("50Гц Телеметрія", 0), ("20Гц Телеметрія", 0), ("5Гц Стан + DTC", 1), ("1Гц SOS-координати", 2), ("0.2Гц Маяк пошуку", 3)],
        [("Повна (50Гц)", 0), ("Повна (50Гц)", 0), ("Знижена (20Гц)", 1), ("Висотомір (10Гц)", 2), ("Вимкнено", 3)],
        [("Повна (15 Вт)", 0), ("Еко CPU (8 Вт)", 1), ("Вимкнено (0 Вт)", 3), ("Вимкнено (0 Вт)", 3), ("Вимкнено (0 Вт)", 3)],
        [("Стабілізація ON", 0), ("Стабілізація ON", 0), ("Парк / Вимкнено", 3), ("Знеструмлено", 3), ("Знеструмлено", 3)],
        [("100% Фари / Нагрів", 0), ("Вимкнено (Еко)", 3), ("Знеструмлено", 3), ("Знеструмлено", 3), ("Знеструмлено", 3)]
    ]
    
    status_styles = {
        0: {"bg": "#e8f5e9", "border": "#4caf50", "text": "#1b5e20"},
        1: {"bg": "#fffde7", "border": "#fbc02d", "text": "#f57f17"},
        2: {"bg": "#fff3e0", "border": "#ff9800", "text": "#e65100"},
        3: {"bg": "#f5f5f5", "border": "#bdbdbd", "text": "#757575"}
    }

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append('  <defs>')
    svg.append('    <style>')
    svg.append('      .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 15px; font-weight: 700; fill: #212121; }')
    svg.append('      .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; fill: #616161; }')
    svg.append('      .row-name { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; font-weight: 700; fill: #212121; }')
    svg.append('      .row-detail { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 9px; fill: #757575; }')
    svg.append('      .legend-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 10px; fill: #424242; }')
    svg.append('    </style>')
    svg.append('  </defs>')
    
    # Background
    svg.append(f'  <rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff" rx="8" />')
    
    # Title & Subtitle
    svg.append('  <text x="25" y="32" class="title" font-size="15">Матриця каскадної деградації функцій при переході в Limp-Home</text>')
    svg.append('  <text x="25" y="48" class="subtitle" font-size="11">Розподіл пріоритетів та бюджету потужності між критичними й допоміжними підсистемами</text>')
    
    start_x = 240
    start_y = 64
    col_w = 136
    row_h = 56
    
    # Mode Headers
    for c_idx, mode in enumerate(modes):
        cx = start_x + c_idx * (col_w + 6)
        svg.append(f'  <rect x="{cx}" y="{start_y}" width="{col_w}" height="40" fill="{mode["bg"]}" stroke="{mode["color"]}" stroke-width="1.5" rx="4" />')
        svg.append(f'  <text x="{cx + col_w/2}" y="{start_y + 16}" font-size="11" font-weight="700" text-anchor="middle" fill="{mode["color"]}">{mode["name"]}</text>')
        svg.append(f'  <text x="{cx + col_w/2}" y="{start_y + 30}" font-size="10" text-anchor="middle" fill="#424242">{mode["sub"]}</text>')
        
    # Rows
    for r_idx, sub in enumerate(subsystems):
        ry = start_y + 46 + r_idx * (row_h + 4)
        
        # Row Header
        svg.append(f'  <rect x="25" y="{ry}" width="208" height="{row_h}" fill="#fcfcfc" stroke="#e0e0e0" rx="4" />')
        svg.append(f'  <text x="33" y="{ry + 22}" class="row-name" font-size="11">{sub["name"]}</text>')
        svg.append(f'  <text x="33" y="{ry + 40}" class="row-detail" font-size="9">{sub["detail"]}</text>')
        
        # Cells
        for c_idx in range(len(modes)):
            cx = start_x + c_idx * (col_w + 6)
            text, stype = matrix[r_idx][c_idx]
            style = status_styles[stype]
            
            svg.append(f'  <rect x="{cx}" y="{ry}" width="{col_w}" height="{row_h}" fill="{style["bg"]}" stroke="{style["border"]}" stroke-width="1" rx="4" />')
            
            parts = text.split(" / ")
            if len(parts) == 2:
                svg.append(f'  <text x="{cx + col_w/2}" y="{ry + 23}" font-size="10" font-weight="600" text-anchor="middle" fill="{style["text"]}">{parts[0]}</text>')
                svg.append(f'  <text x="{cx + col_w/2}" y="{ry + 41}" font-size="10" font-weight="600" text-anchor="middle" fill="{style["text"]}">{parts[1]}</text>')
            else:
                svg.append(f'  <text x="{cx + col_w/2}" y="{ry + 32}" font-size="10" font-weight="600" text-anchor="middle" fill="{style["text"]}">{text}</text>')
                
    # Legend at bottom
    leg_y = h - 25
    legends = [
        ("Повна функція (100%)", 0),
        ("Знижена потужність / частота", 1),
        ("Мінімальний аварійний профіль", 2),
        ("Скинуте навантаження (Off)", 3)
    ]
    
    leg_x = 25
    for ltext, lstype in legends:
        lstyle = status_styles[lstype]
        svg.append(f'  <rect x="{leg_x}" y="{leg_y - 10}" width="12" height="12" fill="{lstyle["bg"]}" stroke="{lstyle["border"]}" stroke-width="1.2" rx="2" />')
        svg.append(f'  <text x="{leg_x + 18}" y="{leg_y}" class="legend-text" font-size="10">{ltext}</text>')
        leg_x += 230

    svg.append('</svg>')
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated: {out_path}")


def build_timing_diagram_svg(out_path):
    """Генерує часову діаграму аварійного скидання навантаження та переходу в Limp-Home."""
    w, h = 960, 500
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append('  <defs>')
    svg.append('    <style>')
    svg.append('      .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 15px; font-weight: 700; fill: #212121; }')
    svg.append('      .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; fill: #616161; }')
    svg.append('      .axis-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; font-weight: 700; fill: #424242; }')
    svg.append('      .row-detail { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 9px; fill: #757575; }')
    svg.append('      .trace-val { font-family: "SFMono-Regular", Consolas, monospace; font-size: 9px; font-weight: 600; }')
    svg.append('    </style>')
    svg.append('    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    svg.append('      <path d="M 0 1 L 10 5 L 0 9 z" fill="#9e9e9e" />')
    svg.append('    </marker>')
    svg.append('  </defs>')
    
    # Background
    svg.append(f'  <rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff" rx="8" />')
    
    # Title
    svg.append('  <text x="25" y="32" class="title" font-size="15">Часова діаграма реакції контролера на тепловий пробій та просідання батареї</text>')
    svg.append('  <text x="25" y="48" class="subtitle" font-size="11">Послідовність аварійного скидання навантаження (Load Shedding), струмового тротлінгу та стабілізації</text>')
    
    t_start = 175
    t_end = 870
    
    # Vertical phase bands
    phases = [
        {"x": 175, "w": 145, "bg": "#e8f5e9", "name": "NORMAL", "color": "#2e7d32"},
        {"x": 320, "w": 160, "bg": "#fffde7", "name": "THERMAL SPIKE", "color": "#f57f17"},
        {"x": 480, "w": 180, "bg": "#fff3e0", "name": "LIMP L1 (SHED 1)", "color": "#e65100"},
        {"x": 660, "w": 210, "bg": "#ffebee", "name": "LIMP L2 (GLIDE)", "color": "#c62828"}
    ]
    
    chart_top = 65
    chart_bot = 430
    
    for ph in phases:
        svg.append(f'  <rect x="{ph["x"]}" y="{chart_top}" width="{ph["w"]}" height="{chart_bot - chart_top}" fill="{ph["bg"]}" opacity="0.35" />')
        # Tag at top
        svg.append(f'  <rect x="{ph["x"] + 6}" y="{chart_top + 2}" width="{ph["w"] - 12}" height="18" fill="#ffffff" stroke="{ph["color"]}" stroke-width="1" rx="3" />')
        svg.append(f'  <text x="{ph["x"] + ph["w"]/2}" y="{chart_top + 15}" font-size="10" font-weight="700" text-anchor="middle" fill="{ph["color"]}">{ph["name"]}</text>')
        # Vertical dashed line below tag
        svg.append(f'  <line x1="{ph["x"]}" y1="{chart_top + 22}" x2="{ph["x"]}" y2="{chart_bot}" stroke="#d0d0d0" stroke-dasharray="3,3" />')
        
    svg.append(f'  <line x1="{t_end}" y1="{chart_top + 22}" x2="{t_end}" y2="{chart_bot}" stroke="#d0d0d0" stroke-dasharray="3,3" />')
    
    # 1. Temperature T MOSFET
    svg.append('  <text x="25" y="120" class="axis-label" font-size="11">T MOSFET (°C)</text>')
    svg.append('  <text x="25" y="134" class="row-detail" font-size="9">Поріг 95°C / 115°C</text>')
    svg.append(f'  <line x1="{t_start}" y1="150" x2="{t_end}" y2="150" stroke="#e0e0e0" />')
    
    # Thresholds
    svg.append(f'  <line x1="{t_start}" y1="125" x2="{t_end}" y2="125" stroke="#fbc02d" stroke-dasharray="2,2" stroke-width="1" />')
    svg.append(f'  <text x="{t_end + 6}" y="128" class="trace-val" font-size="9" fill="#f57f17">95°C</text>')
    svg.append(f'  <line x1="{t_start}" y1="102" x2="{t_end}" y2="102" stroke="#e53935" stroke-dasharray="2,2" stroke-width="1" />')
    svg.append(f'  <text x="{t_end + 6}" y="105" class="trace-val" font-size="9" fill="#c62828">115°C</text>')
    
    temp_path = f"M {t_start} 142 L 320 142 C 370 138 430 108 480 105 C 540 102 600 130 660 133 L {t_end} 135"
    svg.append(f'  <path d="{temp_path}" fill="none" stroke="#d32f2f" stroke-width="2.2" />')
    svg.append('  <circle cx="480" cy="105" r="3.5" fill="#d32f2f" />')
    svg.append('  <text x="480" y="96" class="trace-val" font-size="9" text-anchor="middle" fill="#d32f2f">112°C</text>')

    # 2. Battery Current
    svg.append('  <text x="25" y="190" class="axis-label" font-size="11">Струм батареї I (A)</text>')
    svg.append('  <text x="25" y="204" class="row-detail" font-size="9">Піковий: 80A → 30A</text>')
    svg.append(f'  <line x1="{t_start}" y1="220" x2="{t_end}" y2="220" stroke="#e0e0e0" />')
    
    current_path = f"M {t_start} 190 L 320 190 L 325 170 L 480 172 L 485 194 L 660 196 L 665 210 L {t_end} 210"
    svg.append(f'  <path d="{current_path}" fill="none" stroke="#1976d2" stroke-width="2.2" />')
    svg.append('  <text x="340" y="165" class="trace-val" font-size="9" fill="#1976d2">78A (Пік)</text>')
    svg.append('  <text x="500" y="190" class="trace-val" font-size="9" fill="#1976d2">45A (-42%)</text>')
    svg.append('  <text x="680" y="206" class="trace-val" font-size="9" fill="#1976d2">30A (Глайд)</text>')

    # 3. Battery Voltage
    svg.append('  <text x="25" y="260" class="axis-label" font-size="11">Напруга шини V (В)</text>')
    svg.append('  <text x="25" y="274" class="row-detail" font-size="9">6S LiPo: Sag 20.8V</text>')
    svg.append(f'  <line x1="{t_start}" y1="290" x2="{t_end}" y2="290" stroke="#e0e0e0" />')
    
    volt_path = f"M {t_start} 248 L 320 248 L 325 278 L 480 276 L 485 260 L 660 258 L 665 252 L {t_end} 252"
    svg.append(f'  <path d="{volt_path}" fill="none" stroke="#7b1fa2" stroke-width="2" />')
    svg.append('  <text x="340" y="286" class="trace-val" font-size="9" fill="#7b1fa2">20.8V (Sag)</text>')
    svg.append('  <text x="680" y="248" class="trace-val" font-size="9" fill="#7b1fa2">23.1V (Norm)</text>')

    # 4. Digital Load Shedding Enables
    svg.append('  <text x="25" y="330" class="axis-label" font-size="11">Скидання ліній</text>')
    
    # Sub-track A: Gimbal & Aux Lights (Tier 1) - Off at x=480
    svg.append('  <text x="25" y="350" class="row-detail" font-size="9">Tier 1: Підвіс + Фари</text>')
    tier1_path = f"M {t_start} 345 L 480 345 L 480 365 L {t_end} 365"
    svg.append(f'  <path d="{tier1_path}" fill="none" stroke="#e65100" stroke-width="2" />')
    svg.append('  <text x="435" y="341" class="trace-val" font-size="9" fill="#e65100">ON</text>')
    svg.append('  <text x="500" y="361" class="trace-val" font-size="9" fill="#757575">OFF (t=4.2s)</text>')

    # Sub-track B: Companion Computer (Tier 2) - Off at x=660
    svg.append('  <text x="25" y="390" class="row-detail" font-size="9">Tier 2: SBC / AI Модуль</text>')
    tier2_path = f"M {t_start} 385 L 660 385 L 660 405 L {t_end} 405"
    svg.append(f'  <path d="{tier2_path}" fill="none" stroke="#c62828" stroke-width="2" />')
    svg.append('  <text x="615" y="381" class="trace-val" font-size="9" fill="#c62828">ON</text>')
    svg.append('  <text x="680" y="401" class="trace-val" font-size="9" fill="#757575">OFF (t=7.8s)</text>')

    # Time Axis at bottom
    axis_y = 445
    svg.append(f'  <line x1="{t_start}" y1="{axis_y}" x2="{t_end}" y2="{axis_y}" stroke="#616161" stroke-width="1.5" marker-end="url(#arrow)" />')
    svg.append(f'  <text x="{t_end + 6}" y="{axis_y + 4}" class="axis-label" font-size="11">t (с)</text>')
    
    time_marks = [
        (175, "0.0с"),
        (320, "2.5с (Аномалія)"),
        (480, "4.2с (Скид 1)"),
        (660, "7.8с (Скид 2)"),
        (850, "15.0с (Доліт)")
    ]
    for tx, tlabel in time_marks:
        svg.append(f'  <line x1="{tx}" y1="{axis_y - 4}" x2="{tx}" y2="{axis_y + 4}" stroke="#616161" stroke-width="1.2" />')
        svg.append(f'  <text x="{tx}" y="{axis_y + 16}" font-size="9" text-anchor="middle" fill="#757575">{tlabel}</text>')

    svg.append('</svg>')
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated: {out_path}")


def main():
    topic_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(topic_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    
    mat_svg = os.path.join(img_dir, "subsystem-degradation-matrix.svg")
    timing_svg = os.path.join(img_dir, "emergency-load-shedding-timing.svg")
    
    build_subsystem_matrix_svg(mat_svg)
    build_timing_diagram_svg(timing_svg)


if __name__ == "__main__":
    main()
