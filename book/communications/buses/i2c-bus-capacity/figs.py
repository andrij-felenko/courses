# -*- coding: utf-8 -*-
"""Фігури до теми «Ємність шини I²C і вибір підтяжок».
Запуск: python figs.py   → створює SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Часові діаграми: активний спад і пасивне RC-наростання ────────────────
def fig_rc_charging_envelope():
    W, H = 840, 420
    f = [text(W / 2, 26, "Формування фронтів I²C: активний спад проти пасивного RC-наростання", size=15, bold=True)]

    x0, y0, gw, gh = 90, 60, 680, 260
    f.append(rect(x0, y0, gw, gh, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=4))

    # Рівні напруги
    y_vdd = y0 + 20            # VDD (3.3V)
    y_vih = y0 + gh * 0.30     # VIH = 0.7 VDD (2.31V)
    y_vil = y0 + gh * 0.70     # VIL = 0.3 VDD (0.99V)
    y_vol = y0 + gh * 0.88     # VOL = 0.4V
    y_gnd = y0 + gh - 10       # GND (0V)

    # Горизонтальні лінії рівнів
    f.append(line(x0, y_vdd, x0 + gw, y_vdd, color="#c0392b", sw=1.2, dash="4,4"))
    f.append(text(x0 - 10, y_vdd + 4, "VDD (3.3 В)", size=11, color="#c0392b", anchor="end", bold=True))

    f.append(line(x0, y_vih, x0 + gw, y_vih, color="#27ae60", sw=1.2, dash="3,3"))
    f.append(text(x0 - 10, y_vih + 4, "VIH = 0.7 VDD", size=11, color="#27ae60", anchor="end", bold=True))

    f.append(line(x0, y_vil, x0 + gw, y_vil, color="#2457d6", sw=1.2, dash="3,3"))
    f.append(text(x0 - 10, y_vil + 4, "VIL = 0.3 VDD", size=11, color="#2457d6", anchor="end", bold=True))

    f.append(line(x0, y_vol, x0 + gw, y_vol, color="#d97706", sw=1.0, dash="2,2"))
    f.append(text(x0 - 10, y_vol + 4, "VOL ≤ 0.4 В", size=11, color="#d97706", anchor="end"))

    f.append(line(x0, y_gnd, x0 + gw, y_gnd, color="#6b7280", sw=1.0))
    f.append(text(x0 - 10, y_gnd + 4, "GND (0 В)", size=11, color="#6b7280", anchor="end"))

    # Початок: лінія у високому стані
    f.append(line(x0 + 20, y_vdd, x0 + 80, y_vdd, color="#1a1a1a", sw=2.5))

    # 1. Швидкий активний спад (N-MOSFET відкривається)
    f.append(line(x0 + 80, y_vdd, x0 + 95, y_vol, color="#d97706", sw=2.8))
    f.append(line(x0 + 95, y_vol, x0 + 170, y_vol, color="#1a1a1a", sw=2.5))

    # 2. Оптимальне RC-наростання (зелена крива)
    pts_opt = []
    t_start = x0 + 170
    t_span = 140
    for i in range(30):
        t = i / 29.0
        x = t_start + t * t_span
        v = 1.0 - math.exp(-3.5 * t)
        y = y_vol - v * (y_vol - y_vdd)
        pts_opt.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_opt)}" fill="none" stroke="#27ae60" stroke-width="2.6"/>')
    f.append(line(t_start + t_span, y_vdd, t_start + t_span + 50, y_vdd, color="#27ae60", sw=2.5))

    # 3. Заповільне наростання (надто великий Rp або велика ємність Cb) — червона пунктирна крива
    pts_slow = []
    for i in range(40):
        t = i / 39.0
        x = t_start + t * 290
        v = 1.0 - math.exp(-1.1 * t)
        y = y_vol - v * (y_vol - y_vdd)
        pts_slow.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_slow)}" fill="none" stroke="#c0392b" stroke-width="2.2" stroke-dasharray="4,4"/>')

    # 4. Занадто мала підтяжка (Rp < Rp,min) — піднятий рівень VOL
    y_bad_vol = y0 + gh * 0.65  # 1.15V > VIL !
    f.append(line(x0 + 510, y_vdd, x0 + 540, y_vdd, color="#8b5cf6", sw=2.0))
    f.append(line(x0 + 540, y_vdd, x0 + 555, y_bad_vol, color="#8b5cf6", sw=2.5))
    f.append(line(x0 + 555, y_bad_vol, x0 + 640, y_bad_vol, color="#8b5cf6", sw=2.5))

    # Маркери часу наростання tr
    x_t1 = t_start + 0.1019 * t_span
    x_t2 = t_start + 0.3440 * t_span

    f.append(line(x_t1, y_vil, x_t1, y0 + gh + 22, color="#2457d6", sw=1.2, dash="2,2"))
    f.append(line(x_t2, y_vih, x_t2, y0 + gh + 22, color="#27ae60", sw=1.2, dash="2,2"))
    f.append(arrow(x_t1, y0 + gh + 18, x_t2, y0 + gh + 18, color="#1a1a1a", sw=1.4))
    f.append(arrow(x_t2, y0 + gh + 18, x_t1, y0 + gh + 18, color="#1a1a1a", sw=1.4))
    f.append(text((x_t1 + x_t2) / 2, y0 + gh + 35, "tr = 0.8473·Rp·Cb", size=11, bold=True, color="#1a1a1a"))

    # Підписи зон і дефектів
    f.append(text(x0 + 115, y0 + 40, "Активний спад (tf < 20 нс)", size=11, color="#d97706", bold=True))
    f.append(text(t_start + 110, y_vih - 18, "Норма (tr ≤ tr,max)", size=11, color="#27ae60", bold=True))
    f.append(text(t_start + 230, y_vil - 20, "Затягнутий фронт (Rp > Rp,max)", size=11, color="#c0392b", bold=True))
    f.append(text(x0 + 580, y_bad_vol - 12, "Завищений VOL (Rp < Rp,min)", size=11, color="#8b5cf6", bold=True))

    # Легенда внизу
    ly = H - 35
    f.append(fitbox(x0 + 10, ly, 180, 26, "■ Оптимальна підтяжка", size=11, color="#27ae60", bold=True, fill="#eaf7ed", stroke="#27ae60"))
    f.append(fitbox(x0 + 210, ly, 210, 26, "■ Завелика Rp (завал фронту)", size=11, color="#c0392b", bold=True, fill="#fdecea", stroke="#c0392b"))
    f.append(fitbox(x0 + 440, ly, 230, 26, "■ Замала Rp (порушення VOL)", size=11, color="#8b5cf6", bold=True, fill="#f3e8ff", stroke="#8b5cf6"))

    return render(os.path.join(IMG, "rc-charging-envelope.svg"), W, H, *f)


# ── 2. Складові паразитної ємності шини ──────────────────────────────────────
def fig_capacitance_breakdown():
    W, H = 840, 360
    f = [text(W / 2, 26, "Складові сумарної паразитної ємності шини I²C (Cb)", size=15, bold=True)]

    # Загальна шина SDA/SCL
    y_bus = 80
    f.append(line(50, y_bus, 790, y_bus, color="#2457d6", sw=3.0))
    f.append(text(795, y_bus + 5, "SDA / SCL", size=12, color="#2457d6", bold=True, anchor="start"))

    # Земляна шина
    y_gnd = 250
    f.append(line(50, y_gnd, 790, y_gnd, color="#6b7280", sw=2.0))
    f.append(text(795, y_gnd + 5, "GND (земля)", size=12, color="#6b7280", bold=True, anchor="start"))

    # 1. Ведучий (MCU)
    x_mcu = 110
    f.append(fitbox(x_mcu - 50, y_bus - 45, 100, 35, "MCU (Ведучий)", size=11, bold=True, fill="#eaf0fd", stroke="#2457d6"))
    f.append(line(x_mcu, y_bus - 10, x_mcu, y_bus, color="#2457d6", sw=2.0))

    # Конденсатор C_pin MCU
    f.append(line(x_mcu, y_bus, x_mcu, y_bus + 50, color="#1a1a1a", sw=1.5))
    f.append(line(x_mcu - 14, y_bus + 50, x_mcu + 14, y_bus + 50, color="#1a1a1a", sw=2.5))
    f.append(line(x_mcu - 14, y_bus + 58, x_mcu + 14, y_bus + 58, color="#1a1a1a", sw=2.5))
    f.append(line(x_mcu, y_bus + 58, x_mcu, y_gnd, color="#1a1a1a", sw=1.5))
    f.append(text(x_mcu + 22, y_bus + 56, "Cpin1 ≈ 10 пФ", size=10, color="#1a1a1a", anchor="start"))

    # 2. Друкована плата (PCB trace)
    x_pcb = 260
    f.append(fitbox(x_pcb - 55, y_bus - 45, 110, 35, "Доріжка PCB (15 см)", size=10, bold=True, fill="#eaf7ed", stroke="#27ae60"))
    f.append(line(x_pcb, y_bus, x_pcb, y_bus + 50, color="#27ae60", sw=1.5))
    f.append(line(x_pcb - 14, y_bus + 50, x_pcb + 14, y_bus + 50, color="#27ae60", sw=2.5))
    f.append(line(x_pcb - 14, y_bus + 58, x_pcb + 14, y_bus + 58, color="#27ae60", sw=2.5))
    f.append(line(x_pcb, y_bus + 58, x_pcb, y_gnd, color="#27ae60", sw=1.5))
    f.append(text(x_pcb + 22, y_bus + 56, "Ctrace ≈ 20 пФ", size=10, color="#27ae60", anchor="start"))

    # 3. Ведений 1 (Давач)
    x_s1 = 410
    f.append(fitbox(x_s1 - 45, y_bus - 45, 90, 35, "Давач 1 (IMU)", size=11, bold=True, fill="#fef3c7", stroke="#d97706"))
    f.append(line(x_s1, y_bus - 10, x_s1, y_bus, color="#d97706", sw=2.0))
    f.append(line(x_s1, y_bus, x_s1, y_bus + 50, color="#1a1a1a", sw=1.5))
    f.append(line(x_s1 - 14, y_bus + 50, x_s1 + 14, y_bus + 50, color="#1a1a1a", sw=2.5))
    f.append(line(x_s1 - 14, y_bus + 58, x_s1 + 14, y_bus + 58, color="#1a1a1a", sw=2.5))
    f.append(line(x_s1, y_bus + 58, x_s1, y_gnd, color="#1a1a1a", sw=1.5))
    f.append(text(x_s1 + 22, y_bus + 56, "Cpin2 ≈ 10 пФ", size=10, color="#1a1a1a", anchor="start"))

    # 4. Кабель зв'язку (Шлейф 1 м)
    x_cab = 560
    f.append(fitbox(x_cab - 55, y_bus - 45, 110, 35, "Кабель зв'язку (1 м)", size=10, bold=True, fill="#fdecea", stroke="#c0392b"))
    f.append(line(x_cab, y_bus, x_cab, y_bus + 50, color="#c0392b", sw=1.5))
    f.append(line(x_cab - 14, y_bus + 50, x_cab + 14, y_bus + 50, color="#c0392b", sw=2.5))
    f.append(line(x_cab - 14, y_bus + 58, x_cab + 14, y_bus + 58, color="#c0392b", sw=2.5))
    f.append(line(x_cab, y_bus + 58, x_cab, y_gnd, color="#c0392b", sw=1.5))
    f.append(text(x_cab + 22, y_bus + 56, "Ccable ≈ 80 пФ", size=10, color="#c0392b", anchor="start"))

    # 5. Ведений 2 (Дисплей)
    x_s2 = 710
    f.append(fitbox(x_s2 - 45, y_bus - 45, 90, 35, "OLED Дисплей", size=11, bold=True, fill="#f3e8ff", stroke="#8b5cf6"))
    f.append(line(x_s2, y_bus - 10, x_s2, y_bus, color="#8b5cf6", sw=2.0))
    f.append(line(x_s2, y_bus, x_s2, y_bus + 50, color="#1a1a1a", sw=1.5))
    f.append(line(x_s2 - 14, y_bus + 50, x_s2 + 14, y_bus + 50, color="#1a1a1a", sw=2.5))
    f.append(line(x_s2 - 14, y_bus + 58, x_s2 + 14, y_bus + 58, color="#1a1a1a", sw=2.5))
    f.append(line(x_s2, y_bus + 58, x_s2, y_gnd, color="#1a1a1a", sw=1.5))
    f.append(text(x_s2 + 22, y_bus + 56, "Cpin3 ≈ 10 пФ", size=10, color="#1a1a1a", anchor="start"))

    # Резистор підтяжки Rp угорі
    x_rp = 60
    f.append(line(x_rp, y_bus - 35, x_rp, y_bus - 20, color="#c0392b", sw=2.0))
    f.append(rect(x_rp - 8, y_bus - 20, 16, 20, fill="#ffffff", stroke="#c0392b", sw=1.5))
    f.append(line(x_rp, y_bus, x_rp, y_bus, color="#c0392b", sw=2.0))
    f.append(text(x_rp, y_bus - 42, "VDD", size=10, bold=True, color="#c0392b"))
    f.append(text(x_rp - 12, y_bus - 10, "Rp", size=11, bold=True, color="#c0392b", anchor="end"))

    # Рамка формули суми внизу
    f.append(fitbox(120, 285, 600, 52,
                    "Сумарна ємність: Cb = ∑ Cpin + Ctrace + Ccable + Cconn = 10 + 20 + 10 + 80 + 10 = 130 пФ\n"
                    "Норма NXP UM10204: Cb ≤ 400 пФ (Standard/Fast mode), Cb ≤ 550 пФ (Fast-mode Plus)",
                    size=12, bold=True, fill="#f8fafc", stroke="#3b82f6"))

    return render(os.path.join(IMG, "capacitance-breakdown.svg"), W, H, *f)


# ── 3. Розрахункове вікно вибору підтяжки Rp vs Cb ───────────────────────────
def fig_pullup_design_window():
    W, H = 840, 440
    f = [text(W / 2, 26, "Вікно безпечного вибору підтяжки Rp від сумарної ємності Cb (VDD = 3.3 В)", size=15, bold=True)]

    x0, y0, gw, gh = 90, 60, 680, 310
    f.append(rect(x0, y0, gw, gh, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=4))

    def to_x(c): return x0 + (c / 500.0) * gw
    def to_y(r): return y0 + gh - (r / 12.0) * gh

    # Горизонтальні лінії сітки опору
    for r_val in [2, 4, 6, 8, 10, 12]:
        y = to_y(r_val)
        f.append(line(x0, y, x0 + gw, y, color="#e5e7eb", sw=1.0))
        f.append(text(x0 - 8, y + 4, f"{r_val} кОм", size=10, color="#6b7280", anchor="end"))

    # Вертикальні лінії сітки ємності
    for c_val in [100, 200, 300, 400, 500]:
        x = to_x(c_val)
        f.append(line(x, y0, x, y0 + gh, color="#e5e7eb", sw=1.0))
        f.append(text(x, y0 + gh + 18, f"{c_val} пФ", size=10, color="#6b7280"))

    f.append(text(x0 + gw / 2, y0 + gh + 36, "Сумарна ємність шини Cb (пФ)", size=12, bold=True))
    f.append(text(x0 - 55, y0 + gh / 2, "Опір Rp", size=12, bold=True, anchor="middle"))

    # 1. Нижня межа Rp,min = (3.3 - 0.4) / 3 mA = 0.967 kOm (горизонтальна лінія)
    y_min = to_y(0.967)
    f.append(line(x0, y_min, x0 + gw, y_min, color="#c0392b", sw=2.2))
    f.append(text(x0 + 80, y_min - 8, "Rp,min = 967 Ом (IOL ≤ 3 мА)", size=11, color="#c0392b", bold=True))

    # 2. Верхня межа Standard-mode: Rp,max = 1000 ns / (0.8473 * Cb) = 1180 / Cb (kOm при Cb в pF)
    pts_sm = []
    for c in range(100, 501, 10):
        r = 1180.2 / c
        pts_sm.append(f"{to_x(c):.1f},{to_y(r):.1f}")
    f.append(f'<polyline points="{" ".join(pts_sm)}" fill="none" stroke="#2457d6" stroke-width="2.5"/>')
    f.append(text(to_x(230), to_y(1180.2 / 230) - 10, "Rp,max (Standard-mode, 100 кГц, tr ≤ 1000 нс)", size=11, color="#2457d6", bold=True))

    # 3. Верхня межа Fast-mode: Rp,max = 300 ns / (0.8473 * Cb) = 354 / Cb
    pts_fm = []
    for c in range(40, 401, 10):
        r = 354.07 / c
        if r <= 12.0:
            pts_fm.append(f"{to_x(c):.1f},{to_y(r):.1f}")
    f.append(f'<polyline points="{" ".join(pts_fm)}" fill="none" stroke="#27ae60" stroke-width="2.5"/>')
    f.append(text(to_x(120), to_y(354.07 / 120) + 18, "Rp,max (Fast-mode, 400 кГц, tr ≤ 300 нс)", size=11, color="#27ae60", bold=True))

    # Зафарбована зона припустимих значень для Fast-mode
    poly_fm = [f"{to_x(50):.1f},{y_min:.1f}"]
    for c in range(50, 367, 10):
        r = 354.07 / c
        poly_fm.append(f"{to_x(c):.1f},{to_y(r):.1f}")
    poly_fm.append(f"{to_x(366):.1f},{y_min:.1f}")
    f.append(f'<polygon points="{" ".join(poly_fm)}" fill="#27ae60" fill-opacity="0.12"/>')
    f.append(text(to_x(160), to_y(1.7), "Робоче вікно Fast-mode", size=11, color="#1b7339", bold=True))

    # Критична межа 400 пФ
    x_400 = to_x(400)
    f.append(line(x_400, y0, x_400, y0 + gh, color="#c0392b", sw=1.5, dash="4,4"))
    f.append(text(x_400 - 6, y0 + 35, "Cb,max = 400 пФ (NXP ліміт)", size=10, color="#c0392b", bold=True, anchor="end"))

    # Пояснення точки звуження
    x_cross = to_x(366)
    f.append(circle(x_cross, y_min, 4, fill="#c0392b", stroke="#c0392b"))
    f.append(text(x_cross + 10, y_min + 18, "Вікно Fast-mode закривається при 366 пФ!", size=10, color="#c0392b", bold=True, anchor="start"))

    return render(os.path.join(IMG, "pullup-design-window.svg"), W, H, *f)


# ── 4. Схемотехнічні методи подолання ємнісного ліміту ───────────────────────
def fig_bus_extension_techniques():
    W, H = 840, 360
    f = [text(W / 2, 26, "Схемотехнічні рішення для роботи з підвищеною ємністю шини", size=15, bold=True)]

    bw, bh = 240, 270
    y_b = 60

    # Блок 1: Двоспрямований буфер (Ізоляція ємностей)
    x1 = 30
    f.append(rect(x1, y_b, bw, bh, fill="#f8fafc", stroke="#3b82f6", sw=1.5, rx=6))
    f.append(fitbox(x1 + 10, y_b + 12, bw - 20, 28, "1. Буфер/Повторювач (PCA9515)", size=11, bold=True, fill="#eaf0fd", stroke="#3b82f6"))
    f.append(line(x1 + 20, y_b + 80, x1 + 80, y_b + 80, color="#2457d6", sw=2.0))
    f.append(fitbox(x1 + 80, y_b + 65, 80, 30, "Буфер", size=11, bold=True, fill="#ffffff", stroke="#2457d6"))
    f.append(line(x1 + 160, y_b + 80, x1 + 220, y_b + 80, color="#2457d6", sw=2.0))
    f.append(text(x1 + 50, y_b + 115, "Сегмент A\n(Cb1 ≤ 400 пФ)", size=10, color="#1a1a1a"))
    f.append(text(x1 + 190, y_b + 115, "Сегмент B\n(Cb2 ≤ 400 пФ)", size=10, color="#1a1a1a"))
    f.append(fitbox(x1 + 10, y_b + 150, bw - 20, 105,
                    "• Розділяє шину на ізольовані\n  ємнісні домени.\n"
                    "• Кожен сегмент має власні\n  підтяжки Rp1 та Rp2.\n"
                    "• Сумарна ємність сегментів\n  не додається!",
                    size=10, fill="#ffffff", stroke="#d0d7de"))

    # Блок 2: Активний прискорювач фронтів (Rise-Time Accelerator)
    x2 = 300
    f.append(rect(x2, y_b, bw, bh, fill="#f8fafc", stroke="#27ae60", sw=1.5, rx=6))
    f.append(fitbox(x2 + 10, y_b + 12, bw - 20, 28, "2. Прискорювач RTA (LTC4311)", size=11, bold=True, fill="#eaf7ed", stroke="#27ae60"))
    f.append(line(x2 + 20, y_b + 80, x2 + 220, y_b + 80, color="#27ae60", sw=2.0))
    f.append(line(x2 + 120, y_b + 80, x2 + 120, y_b + 105, color="#27ae60", sw=2.0))
    f.append(fitbox(x2 + 70, y_b + 105, 100, 28, "Генератор струму", size=10, bold=True, fill="#ffffff", stroke="#27ae60"))
    f.append(fitbox(x2 + 10, y_b + 150, bw - 20, 105,
                    "• Відстежує наростання dV/dt.\n"
                    "• Тимчасово впорскує сильний\n  струм заряду (до 10-30 мА).\n"
                    "• Відключається біля VDD.\n"
                    "• Працює з Cb > 1000 пФ\n  при пасивних Rp = 10 кОм.",
                    size=10, fill="#ffffff", stroke="#d0d7de"))

    # Блок 3: Диференційний I²C (dI2C через PCA9615)
    x3 = 570
    f.append(rect(x3, y_b, bw, bh, fill="#f8fafc", stroke="#8b5cf6", sw=1.5, rx=6))
    f.append(fitbox(x3 + 10, y_b + 12, bw - 20, 28, "3. Диференційний I²C (PCA9615)", size=11, bold=True, fill="#f3e8ff", stroke="#8b5cf6"))
    f.append(fitbox(x3 + 15, y_b + 65, 60, 30, "dI2C Tx", size=10, bold=True, fill="#ffffff", stroke="#8b5cf6"))
    f.append(line(x3 + 75, y_b + 73, x3 + 165, y_b + 73, color="#8b5cf6", sw=1.5))
    f.append(line(x3 + 75, y_b + 87, x3 + 165, y_b + 87, color="#8b5cf6", sw=1.5))
    f.append(text(x3 + 120, y_b + 62, "Вита пара (DSDA+, DSDA−)", size=10, color="#8b5cf6"))
    f.append(fitbox(x3 + 165, y_b + 65, 60, 30, "dI2C Rx", size=10, bold=True, fill="#ffffff", stroke="#8b5cf6"))
    f.append(fitbox(x3 + 10, y_b + 150, bw - 20, 105,
                    "• Перетворює SDA/SCL на дві\n  диференційні пари.\n"
                    "• Нечутливий до синфазних\n  шумів та ємності кабелю.\n"
                    "• Дальність до 3-10 метрів\n  на швидкості 1 МГц (Fm+).",
                    size=10, fill="#ffffff", stroke="#d0d7de"))

    return render(os.path.join(IMG, "bus-extension-techniques.svg"), W, H, *f)


if __name__ == '__main__':
    fig_rc_charging_envelope()
    fig_capacitance_breakdown()
    fig_pullup_design_window()
    fig_bus_extension_techniques()
    print("Всі фігури успішно згенеровано.")
