# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# ── 1. Пошарове перерізання друкованого провідника та вибірка V-подібного паза ──
def fig_trace_cutting():
    W, H = 940, 500
    f = []

    f.append(text(W / 2, 25, "Технологія перерізання друкованих провідників: ризики та стандарт IPC-7721", size=15, bold=True))

    # ── Ліва панель: Небезпечний прямий різ ───────────────────────────────────
    lx, ly = 25, 50
    lw, lh = 435, 430
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(lx + lw / 2, ly + 22, "Небезпечно: прямий різ під кутом 90°", size=13, bold=True, color=POS))

    # Схема шарів (зріз) ліворуч
    bx, by = lx + 30, ly + 50
    bw, bh = 375, 175

    # L1 Маска + Мідь
    f.append(rect(bx, by, bw, 20, fill="#2e7d32", stroke="#1b5e20", sw=1.2, rx=0))
    f.append(text(bx + 60, by + 14, "Паяльна маска (20 мкм)", size=10.5, color="#ffffff", bold=True))

    f.append(rect(bx, by + 20, bw, 28, fill="#d97706", stroke="#b45309", sw=1.2, rx=0))
    f.append(text(bx + 60, by + 38, "Шар L1: Мідний провідник (35 мкм / 1 oz)", size=10.5, color="#ffffff", bold=True))

    # Препрег / Діелектрик FR-4
    f.append(rect(bx, by + 48, bw, 70, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=0))
    f.append(text(bx + 75, by + 85, "Препрег / Діелектрик FR-4 (100–150 мкм)", size=10.5, color="#92400e", bold=True))

    # L2 Внутрішня площина GND
    f.append(rect(bx, by + 118, bw, 28, fill="#2563eb", stroke="#1d4ed8", sw=1.2, rx=0))
    f.append(text(bx + 75, by + 136, "Шар L2: Внутрішня площина GND (35 мкм)", size=10.5, color="#ffffff", bold=True))

    # Основний текстоліт Core
    f.append(rect(bx, by + 146, bw, 25, fill="#e2e8f0", stroke="#94a3b8", sw=1.0, rx=0))
    f.append(text(bx + 75, by + 162, "Основа FR-4 Core", size=10, color="#475569"))

    # Скальпель що глибоко прорізав
    cx_cut = bx + bw / 2 + 50
    # Лезо скальпеля (трикутник/полігон)
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#64748b" stroke="#334155" stroke-width="1.5"/>' %
             (cx_cut - 14, by - 35, cx_cut + 14, by - 35, cx_cut, by + 120))
    f.append(text(cx_cut, by - 42, "Скальпель №11", size=11, color="#334155", bold=True))

    # Місце пробою L2
    f.append(circle(cx_cut, by + 120, 10, fill="none", stroke=POS, sw=2.2))
    f.append(text(cx_cut, by + 124, "⚡", size=12, color=POS))

    # Опис дефектів під малюнком
    f.append(fitbox(lx + 15, ly + 235, lw - 30, 52,
                    "1. Задирки міді (Burrs) на краях розрізу\n"
                    "Під вібрацією або термоциклами змикаються назад",
                    size=11, fill="#fef2f2", stroke="#fecaca", color="#991b1b"))

    f.append(fitbox(lx + 15, ly + 295, lw - 30, 58,
                    "2. Прорізання тонкого препрегу L1–L2\n"
                    "Лезо скальпеля закорочує сигнальний провідник L1\n"
                    "на суцільний внутрішній шар заземлення L2",
                    size=11, fill="#fef2f2", stroke="#fecaca", color="#991b1b"))

    f.append(fitbox(lx + 15, ly + 360, lw - 30, 56,
                    "3. Капілярне затікання вологи та флюсу\n"
                    "Негерметизований мікророзріз утворює струмопровідні\n"
                    "дендрити міді під дією постійної напруги",
                    size=11, fill="#fef2f2", stroke="#fecaca", color="#991b1b"))

    # ── Права панель: Стандарт IPC-7721 ───────────────────────────────────────
    rx_p, ry_p = 480, 50
    rw, rh = 435, 430
    f.append(rect(rx_p, ry_p, rw, rh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(rx_p + rw / 2, ry_p + 22, "Правильно: вибірка сегмента за IPC-7721", size=13, bold=True, color=FIELD))

    # Схема шарів справа
    rx_b, ry_b = rx_p + 30, ry_p + 50

    # L1 Маска з обох боків
    gap_w = 40
    gx_mid = rx_b + bw / 2 + 50
    gx1 = gx_mid - gap_w / 2
    gx2 = gx_mid + gap_w / 2

    # L1 Мідь ліворуч і праворуч
    f.append(rect(rx_b, ry_b + 20, gx1 - rx_b, 28, fill="#d97706", stroke="#b45309", sw=1.2, rx=0))
    f.append(rect(gx2, ry_b + 20, (rx_b + bw) - gx2, 28, fill="#d97706", stroke="#b45309", sw=1.2, rx=0))

    # Маска L1 ліворуч і праворуч
    f.append(rect(rx_b, ry_b, gx1 - 10 - rx_b, 20, fill="#2e7d32", stroke="#1b5e20", sw=1.2, rx=0))
    f.append(rect(gx2 + 10, ry_b, (rx_b + bw) - (gx2 + 10), 20, fill="#2e7d32", stroke="#1b5e20", sw=1.2, rx=0))

    # Препрег / FR-4 суцільний без пошкодження!
    f.append(rect(rx_b, ry_b + 48, bw, 70, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=0))
    f.append(text(rx_b + 75, ry_b + 85, "Препрег не пошкоджено (глибина різу ≤ 35 мкм)", size=10.5, color="#92400e", bold=True))

    # Шар L2 цілий
    f.append(rect(rx_b, ry_b + 118, bw, 28, fill="#2563eb", stroke="#1d4ed8", sw=1.2, rx=0))
    f.append(text(rx_b + 75, ry_b + 136, "Шар L2: Внутрішня площина GND (цілісна)", size=10.5, color="#ffffff", bold=True))

    # Core
    f.append(rect(rx_b, ry_b + 146, bw, 25, fill="#e2e8f0", stroke="#94a3b8", sw=1.0, rx=0))

    # Заповнення паза УФ-маскою
    f.append(rect(gx1 - 5, ry_b + 5, gap_w + 10, 43, fill="#86efac", stroke="#16a34a", sw=1.5, rx=3))
    f.append(text(gx_mid, ry_b + 30, "УФ-маска", size=10, color="#14532d", bold=True))

    # Розмір проміжку
    f.append(line(gx1, ry_b - 12, gx2, ry_b - 12, color=INK, sw=1.2))
    f.append(line(gx1, ry_b - 16, gx1, ry_b - 8, color=INK, sw=1.2))
    f.append(line(gx2, ry_b - 16, gx2, ry_b - 8, color=INK, sw=1.2))
    f.append(text(gx_mid, ry_b - 18, "Зазор 0.8–1.5 мм", size=10, color=INK, bold=True))

    # Опис процесу праворуч
    f.append(fitbox(rx_p + 15, ry_p + 235, rw - 30, 52,
                    "Крок 1. Два надрізи під кутом 30–45°\n"
                    "Виконувати з контролем тиску, не прорізаючи діелектрик",
                    size=11, fill="#f0fdf4", stroke="#bbf7d0", color="#166534"))

    f.append(fitbox(rx_p + 15, ry_p + 295, rw - 30, 58,
                    "Крок 2. Відлущування мідного сегмента\n"
                    "Пінцетом видаляється острівець міді довжиною ~1 мм;\n"
                    "оголений чистий склотекстоліт перевіряється мікроскопом",
                    size=11, fill="#f0fdf4", stroke="#bbf7d0", color="#166534"))

    f.append(fitbox(rx_p + 15, ry_p + 360, rw - 30, 56,
                    "Крок 3. Герметизація УФ-затверджуваною маскою\n"
                    "Паз заливається акриловою маскою й полімеризується УФ;\n"
                    "виключає корозію, міграцію міді та випадкове замикання",
                    size=11, fill="#f0fdf4", stroke="#bbf7d0", color="#166534"))

    return render(os.path.join(IMG, "trace-cutting-technique.svg"), W, H, *f)


# ── 2. Вплив геометрії прокладання синього дроту на контур струму ──────────────
def fig_bodge_wire_routing():
    W, H = 940, 480
    f = []

    f.append(text(W / 2, 24, "Вплив геометрії прокладання бодж-дроту на паразитну індуктивність та контур струму", size=15, bold=True))

    # ── Ліва частина: Помилкове прокладання по повітрю ────────────────────────
    lx, ly = 25, 48
    lw, lh = 435, 415
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(lx + lw / 2, ly + 22, "Помилка: вільна петля над платою", size=13, bold=True, color=POS))

    # Поверхня плати ліворуч
    px, py = lx + 30, ly + 210
    pw, ph = 375, 30
    f.append(rect(px, py, pw, ph, fill="#2e7d32", stroke="#1b5e20", sw=1.2, rx=0))
    f.append(text(px + 45, py + 18, "FR-4 PCB", size=10, color="#ffffff", bold=True))

    # Площина GND
    f.append(rect(px, py + 30, pw, 18, fill="#2563eb", stroke="#1d4ed8", sw=1.2, rx=0))
    f.append(text(px + 100, py + 43, "Внутрішня площина заземлення (GND Plane)", size=9.5, color="#ffffff"))

    # Компоненти IC1 та IC2
    f.append(rect(px + 30, py - 25, 45, 25, fill="#1e293b", stroke="#0f172a", sw=1.2, rx=2))
    f.append(text(px + 52.5, py - 10, "IC 1", size=10, color="#ffffff", bold=True))

    f.append(rect(px + pw - 75, py - 25, 45, 25, fill="#1e293b", stroke="#0f172a", sw=1.2, rx=2))
    f.append(text(px + pw - 52.5, py - 10, "IC 2", size=10, color="#ffffff", bold=True))

    # Дріт у повітрі (велика дуга)
    wire_start_x, wire_start_y = px + 52.5, py - 25
    wire_end_x, wire_end_y = px + pw - 52.5, py - 25
    f.append('<path d="M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (wire_start_x, wire_start_y, px + pw / 2, py - 130, wire_end_x, wire_end_y, POS))
    f.append(text(px + pw / 2, py - 135, "Синій дріт (висота h = 15–20 мм)", size=11, color=POS, bold=True))

    # Шлях зворотного струму у площині GND
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.0" stroke-dasharray="4,3"/>' %
             (wire_start_x, py + 39, wire_end_x, py + 39, NEG))
    f.append(text(px + pw / 2, py + 65, "Зворотний струм тече в площині GND під дротом", size=10, color=NEG))

    # Площа контуру заливка (контур розриву)
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fecaca" fill-opacity="0.35"/>' %
             (wire_start_x, wire_start_y, px + pw / 2, py - 110, wire_end_x, wire_end_y, wire_start_x, wire_end_y))
    f.append(text(px + pw / 2, py - 45, "Величезна площа контуру A_loop", size=12, color="#991b1b", bold=True))

    # Метрики та проблеми
    f.append(fitbox(lx + 15, ly + 280, lw - 30, 56,
                    "• Паразитна індуктивність L_loop ≈ 20–50 нГн\n"
                    "• Стрибки напруги (L·di/dt) спотворюють фронти імпульсів\n"
                    "• Працює як антена: високий рівень випромінювання EMI",
                    size=10.5, fill="#fef2f2", stroke="#fecaca", color="#991b1b"))

    f.append(fitbox(lx + 15, ly + 344, lw - 30, 56,
                    "• Висока взаємна індукція: наводить завади на сусідні кола\n"
                    "• Сприйнятливість до зовнішніх магнітних полів\n"
                    "• Швидкісні інтерфейси (SPI > 10 MHz, QSPI) дають збої",
                    size=10.5, fill="#fef2f2", stroke="#fecaca", color="#991b1b"))

    # ── Права частина: Правильне прокладання впритул до GND ───────────────────
    rx_p, ry_p = 480, 48
    rw, rh = 435, 415
    f.append(rect(rx_p, ry_p, rw, rh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(rx_p + rw / 2, ry_p + 22, "Правильно: щільне прилягання до плати", size=13, bold=True, color=FIELD))

    # Поверхня плати справа
    r_px, r_py = rx_p + 30, ry_p + 210
    f.append(rect(r_px, r_py, pw, ph, fill="#2e7d32", stroke="#1b5e20", sw=1.2, rx=0))
    f.append(text(r_px + 45, r_py + 18, "FR-4 PCB", size=10, color="#ffffff", bold=True))

    # Площина GND
    f.append(rect(r_px, r_py + 30, pw, 18, fill="#2563eb", stroke="#1d4ed8", sw=1.2, rx=0))
    f.append(text(r_px + 100, r_py + 43, "Внутрішня площина заземлення (GND Plane)", size=9.5, color="#ffffff"))

    # Компоненти IC1 та IC2
    f.append(rect(r_px + 30, r_py - 25, 45, 25, fill="#1e293b", stroke="#0f172a", sw=1.2, rx=2))
    f.append(text(r_px + 52.5, r_py - 10, "IC 1", size=10, color="#ffffff", bold=True))

    f.append(rect(r_px + pw - 75, r_py - 25, 45, 25, fill="#1e293b", stroke="#0f172a", sw=1.2, rx=2))
    f.append(text(r_px + pw - 52.5, r_py - 10, "IC 2", size=10, color="#ffffff", bold=True))

    # Дріт щільно притиснутий до поверхні плати
    r_wire_sx, r_wire_sy = r_px + 52.5, r_py - 25
    r_wire_ex, r_wire_ey = r_px + pw - 52.5, r_py - 25
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (r_wire_sx, r_wire_sy, r_wire_sx, r_py - 2, r_wire_ex, r_py - 2, r_wire_ex, r_wire_ey, "#2563eb"))

    # Краплі УФ-клею
    drop_x1 = r_px + 120
    drop_x2 = r_px + pw / 2
    drop_x3 = r_px + pw - 120
    for dx in [drop_x1, drop_x2, drop_x3]:
        f.append(circle(dx, r_py - 2, 7, fill="#86efac", stroke="#16a34a", sw=1.2))
    f.append(text(drop_x2, r_py - 16, "Фіксація УФ-маскою / клеєм що 15–20 мм", size=10, color="#15803d", bold=True))

    # Шлях зворотного струму
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.0" stroke-dasharray="4,3"/>' %
             (r_wire_sx, r_py + 39, r_wire_ex, r_py + 39, NEG))

    # Вказівка на мінімальну площу контуру
    f.append(text(r_px + pw / 2, r_py - 40, "Мінімальний проміжок h ≈ 0.2 мм (товщина маски)", size=10.5, color="#15803d", bold=True))
    f.append(text(r_px + pw / 2, r_py - 60, "Мінімальна площа контуру A_min", size=12, color=FIELD, bold=True))

    # Переваги
    f.append(fitbox(rx_p + 15, ry_p + 280, rw - 30, 56,
                    "• Паразитна індуктивність мінімізована: L_loop < 3–5 нГн\n"
                    "• Зворотний струм у GND тече безпосередньо під дротом\n"
                    "• Хвильовий опір наближається до мікросмужкової лінії (~80–110 Ом)",
                    size=10.5, fill="#f0fdf4", stroke="#bbf7d0", color="#166534"))

    f.append(fitbox(rx_p + 15, ry_p + 344, rw - 30, 56,
                    "• Стійкість до вібрацій: дріт не відриває контакти компонентів\n"
                    "• Для ліній > 25 МГц застосовують виту пару (Signal + GND)\n"
                    "• Відсутність перехресних наведень на сусідні сигнальні шини",
                    size=10.5, fill="#f0fdf4", stroke="#bbf7d0", color="#166534"))

    return render(os.path.join(IMG, "bodge-wire-routing-ground-plane.svg"), W, H, *f)


if __name__ == "__main__":
    fig_trace_cutting()
    fig_bodge_wire_routing()
    print("Figures generated successfully in img/")
