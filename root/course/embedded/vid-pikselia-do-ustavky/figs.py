# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Figure 1: camera-pinhole-angles ──────────────────────────────────────────
# Геометрія камери-обскури: оптичний центр, площина сенсора, фокусна відстань f,
# головна точка (cx, cy), координати цілі (u, v) та кутові похибки α_x і α_y.

def fig_camera_pinhole_angles():
    W, H = 940, 520
    p = []

    # Заголовок та підкладка
    p.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Координати центрів
    ox, oy = 180, 260          # Оптичний центр камери Oc (фокус)
    plane_x = 480              # Площина зображення (сенсор)
    target_x, target_y = 810, 120 # Реальний об'єкт у просторі

    # Промінь зору через площину камери до об'єкта
    p.append(line(ox, oy, target_x, target_y, color=POS, sw=2.2, dash="5,4"))

    # Оптична вісь Z_c (вперед)
    p.append(arrow(ox, oy, 860, oy, color=LINE, sw=1.8))
    p.append(text(875, oy + 5, "Zc (головна оптична вісь)", size=12, color=INK, anchor="start", bold=True))

    # Вісь X_c (вправо) та Y_c (вниз) біля оптичного центру
    p.append(arrow(ox, oy, ox, oy + 120, color=LINE, sw=1.8))
    p.append(text(ox - 10, oy + 125, "Yc (вниз)", size=11, color=INK, anchor="end"))
    p.append(arrow(ox, oy, ox - 70, oy - 60, color=LINE, sw=1.8))
    p.append(text(ox - 75, oy - 65, "Xc (вправо)", size=11, color=INK, anchor="end"))

    # Точка оптичного центру
    p.append(circle(ox, oy, 6, fill=NEG, stroke=LINE, sw=1.5))
    p.append(text(ox - 15, oy + 18, "Oc (оптичний центр камери)", size=12, color=NEG, anchor="end", bold=True))

    # Площина сенсора зображення (матриця пікселів)
    pw, ph = 180, 260
    py_top = oy - ph / 2
    p.append(rect(plane_x - 10, py_top, pw, ph, fill="#f8fafc", stroke=NEG, sw=2, rx=4))

    # Головна точка / оптичний центр матриці (cx, cy)
    cx_pix, cy_pix = plane_x + 80, oy
    p.append(circle(cx_pix, cy_pix, 4, fill=LINE, stroke=LINE, sw=1))
    p.append(line(cx_pix - 15, cy_pix, cx_pix + 15, cy_pix, color=MUTED, sw=1))
    p.append(line(cx_pix, cy_pix - 15, cx_pix, cy_pix + 15, color=MUTED, sw=1))
    p.append(text(cx_pix + 10, cy_pix + 18, "(cx, cy) оптичний центр", size=11, color=MUTED, anchor="start"))

    # Вісь координат сенсора u (вправо) та v (вниз)
    p.append(arrow(plane_x - 10, py_top, plane_x + 90, py_top, color=FIELD, sw=1.8))
    p.append(text(plane_x + 95, py_top + 14, "u (пікселі)", size=11, color=FIELD, anchor="start", bold=True))
    p.append(arrow(plane_x - 10, py_top, plane_x - 10, py_top + 90, color=FIELD, sw=1.8))
    p.append(text(plane_x - 18, py_top + 95, "v (пікселі)", size=11, color=FIELD, anchor="end", bold=True))
    p.append(circle(plane_x - 10, py_top, 4, fill=FIELD, stroke=LINE, sw=1))
    p.append(text(plane_x - 15, py_top - 8, "(0, 0)", size=11, color=MUTED, anchor="end"))

    # Точка проєкції на сенсорі (u, v)
    # З подібності трикутників: на площині plane_x проєкція променя
    frac = (plane_x - ox) / (target_x - ox)
    proj_y = oy + (target_y - oy) * frac
    proj_x = plane_x + 45

    p.append(circle(proj_x, proj_y, 5, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(proj_x + 12, proj_y - 8, "P(u, v) центр bounding box", size=11, color=POS, anchor="start", bold=True))

    # Зміщення від центру: Δu, Δv
    p.append(line(cx_pix, cy_pix, proj_x, cy_pix, color="#e67e22", sw=1.5, dash="3,3"))
    p.append(line(proj_x, cy_pix, proj_x, proj_y, color="#e67e22", sw=1.5, dash="3,3"))
    p.append(text((cx_pix + proj_x) / 2, cy_pix - 8, "Δu = u − cx", size=10, color="#d35400", anchor="middle"))
    p.append(text(proj_x + 8, (cy_pix + proj_y) / 2 + 3, "Δv = v − cy", size=10, color="#d35400", anchor="start"))

    # Фокусна відстань f
    p.append(line(ox, oy + 150, plane_x, oy + 150, color=LINE, sw=1.5))
    p.append(line(ox, oy + 140, ox, oy + 160, color=LINE, sw=1.5))
    p.append(line(plane_x, oy + 140, plane_x, oy + 160, color=LINE, sw=1.5))
    p.append(text((ox + plane_x) / 2, oy + 172, "f (фокусна відстань у метрах / пікселях fx)", size=11, color=INK, anchor="middle", bold=True))

    # Кут азимута α_x (bearing) та тангажу α_y (elevation)
    p.append(text(ox + 80, oy - 25, "α_x, α_y", size=12, color=POS, bold=True))
    p.append(line(ox, oy, plane_x, proj_y, color=POS, sw=1.8))

    # Об'єкт у просторі (Target)
    p.append(rect(target_x - 20, target_y - 25, 40, 50, fill="#fee2e2", stroke=POS, sw=2, rx=4))
    p.append(circle(target_x, target_y, 4, fill=POS, stroke=LINE, sw=1.2))
    p.append(text(target_x, target_y - 32, "Ціль у просторі (X, Y, Z)", size=12, color=POS, anchor="middle", bold=True))

    # Блок формул уніфікації
    fx_box = fitbox(480, 390, 420, 95,
                    "Розрахунок кутових похибок:\n"
                    "• x_n = (u − cx) / fx,   y_n = (v − cy) / fy\n"
                    "• Азимут: α_x = arctan(x_n) ≈ Δu / fx  (yaw)\n"
                    "• Тангаж: α_y = arctan(y_n) ≈ Δv / fy  (pitch)",
                    size=12, pad=10, fill="#f1f5f9", stroke="#94a3b8", color=INK, bold=False)
    p.append(fx_box)

    render(os.path.join(OUT, "camera-pinhole-angles.svg"), W, H, *p,
           title="Геометрія камери-обскури: від пікселя (u, v) до кутових похибок наведення")


# ── Figure 2: ibvs-control-loop ──────────────────────────────────────────────
# Архітектура контуру візуального наведення IBVS:
# Камера -> Детектор (затримка) -> Калман (екстраполяція) -> ПІД-регулятор -> Уставки швидкостей -> Автопілот

def fig_ibvs_control_loop():
    W, H = 940, 490
    p = []

    p.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Блоки верхнього ряду (прямий ланцюг обробки)
    # 1. Камера
    b1 = fitbox(35, 75, 130, 80, "Камера\n(сенсор IMX/MIPI)\n20–60 fps", size=11, fill="#eff6ff", stroke=NEG, bold=True)
    p.append(b1)

    # Стрілка Камера -> Детектор
    p.append(arrow(165, 115, 205, 115, color=LINE, sw=1.8))
    p.append(text(185, 105, "Кадр", size=10, color=MUTED))

    # 2. Нейродетектор / Трекер
    b2 = fitbox(205, 75, 155, 80, "Нейродетектор\n(YOLO/SORT на NPU)\nBounding Box [u,v,w,h]", size=11, fill="#fdf4ff", stroke="#a855f7", bold=True)
    p.append(b2)

    # Стрілка Детектор -> Калман
    p.append(arrow(360, 115, 400, 115, color=LINE, sw=1.8))
    p.append(mtext(380, 98, "Δu, Δv\n(запізнілі)", size=9.5, color=POS, bold=True))

    # 3. Фільтр Калмана / Екстраполятор
    b3 = fitbox(400, 75, 165, 80, "Фільтр Калмана\n+ компенсатор лагу\nПрогноз на t_now + T_lat", size=11, fill="#fefce8", stroke="#eab308", bold=True)
    p.append(b3)

    # Вхід гіроскопа IMU у фільтр Калмана (компенсація власного обертання)
    b_imu = fitbox(400, 195, 165, 55, "IMU автопілота\nКутові швидкості ω_gyro", size=10.5, fill="#f8fafc", stroke="#64748b")
    p.append(b_imu)
    p.append(arrow(482, 195, 482, 155, color="#64748b", sw=1.5))
    p.append(text(540, 178, "ego-motion feedforward", size=9, color="#64748b"))

    # Стрілка Калман -> IBVS Контролер
    p.append(arrow(565, 115, 605, 115, color=LINE, sw=1.8))
    p.append(mtext(585, 98, "α̂, α̂̇\n(актуальні)", size=9.5, color=FIELD, bold=True))

    # 4. IBVS Контролер
    b4 = fitbox(605, 75, 145, 80, "IBVS Контролер\nПІД-уставки + scale\nAnti-windup & deadband", size=11, fill="#ecfdf5", stroke=FIELD, bold=True)
    p.append(b4)

    # Стрілка Контролер -> Автопілот
    p.append(arrow(750, 115, 790, 115, color=LINE, sw=1.8))
    p.append(mtext(770, 98, "ω_sp, V_sp\n(MAVLink)", size=9.5, color=INK, bold=True))

    # 5. Автопілот / Приводи
    b5 = fitbox(790, 75, 120, 80, "Автопілот\n(PX4/ArduPilot)\nВнутрішній контур", size=11, fill="#eff6ff", stroke=NEG, bold=True)
    p.append(b5)

    # Нижня гілка: Динаміка дрона + Зміна положення цілі в полі зору
    p.append(line(850, 155, 850, 320, color=LINE, sw=1.8))
    p.append(line(850, 320, 730, 320, color=LINE, sw=1.8))

    b6 = fitbox(550, 280, 180, 80, "Динаміка апарата\nРух шасі, крен/рискання,\nзміна ракурсу камери", size=11, fill="#f1f5f9", stroke="#475569", bold=True)
    p.append(b6)

    p.append(arrow(550, 320, 390, 320, color=LINE, sw=1.8))

    b7 = fitbox(210, 280, 180, 80, "Ціль у кадрі\nЗміщення центра (u, v)\nта зміна площі (scale)", size=11, fill="#fee2e2", stroke=POS, bold=True)
    p.append(b7)

    p.append(line(210, 320, 100, 320, color=LINE, sw=1.8))
    p.append(arrow(100, 320, 100, 155, color=LINE, sw=1.8))
    p.append(text(100, 235, "Оптичний потік", size=10, color=MUTED, anchor="middle"))

    # Пояснювальний бейдж внизу
    note_box = fitbox(35, 390, 870, 75,
                      "Замкнений контур IBVS (Image-Based Visual Servoing):\n"
                      "Помилка формується безпосередньо у площині зображення. Детектор вносить транспортну затримку,\n"
                      "фільтр Калмана екстраполює стан цілі на поточний момент часу, а ПІД-регулятор формує уставки кутових швидкостей.",
                      size=11, pad=10, fill="#f8fafc", stroke="#cbd5e1", color=INK)
    p.append(note_box)

    render(os.path.join(OUT, "ibvs-control-loop.svg"), W, H, *p,
           title="Архітектура контуру візуального наведення IBVS із компенсацією затримки")


# ── Figure 3: latency-timeline-oscillation ───────────────────────────────────
# Два блоки:
# 1) Часова діаграма затримок: експозиція -> інференс -> шина -> контур
# 2) Відгук системи: розгойдування без компенсації проти стабільного захоплення з Калманом

def fig_latency_timeline_oscillation():
    W, H = 940, 520
    p = []

    p.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # ── Ліва половина: часова шкала латентності ─────────────────────────────
    p.append(text(240, 50, "Структура затримки кадру (Total Latency ~100 мс)", size=13, color=INK, bold=True))

    ty0 = 85
    stages = [
        ("Експозиція сенсора (середня точка t_exp/2)", "15 мс", "#dbeafe", NEG),
        ("Зчитування сенсора (Rolling Shutter readout)", "15 мс", "#e0e7ff", "#4338ca"),
        ("Передача кадру в пам'ять (DMA/ISP)", "5 мс", "#f1f5f9", "#475569"),
        ("Інференс нейромережі (YOLO на NPU)", "45 мс", "#fce7f3", "#be185d"),
        ("UART / MAVLink передача на автопілот", "10 мс", "#fef3c7", "#b45309"),
        ("Фільтрація та реакція приводу (ESC / Gimbal)", "20 мс", "#dcfce7", FIELD)
    ]

    cur_y = ty0
    for name, dur, fill, stroke in stages:
        p.append(rect(45, cur_y, 390, 42, fill=fill, stroke=stroke, sw=1.5, rx=5))
        p.append(text(60, cur_y + 25, name, size=10.5, color=INK, anchor="start", bold=False))
        p.append(text(420, cur_y + 25, dur, size=11, color=stroke, anchor="end", bold=True))
        cur_y += 50

    p.append(rect(45, cur_y + 5, 390, 45, fill="#fee2e2", stroke=POS, sw=2, rx=5))
    p.append(text(60, cur_y + 32, "Повна затримка T_total = t_act − t_capture", size=11, color=POS, anchor="start", bold=True))
    p.append(text(420, cur_y + 32, "≈ 110 мс", size=13, color=POS, anchor="end", bold=True))

    # ── Права половина: Порівняння перехідних процесів ───────────────────────
    p.append(text(700, 50, "Відгук контуру на зміщення цілі", size=13, color=INK, bold=True))

    # Графік: осі
    gx0, gy0 = 500, 240
    gw, gh = 380, 160

    p.append(line(gx0, gy0, gx0 + gw, gy0, color=MUTED, sw=1.2, dash="4,4")) # Нульова лінія (помилка = 0)
    p.append(text(gx0 + gw + 8, gy0 + 4, "Центр (0)", size=10, color=MUTED, anchor="start"))

    p.append(line(gx0, gy0 - gh/2 - 20, gx0, gy0 + gh/2 + 20, color=LINE, sw=1.8))
    p.append(line(gx0, gy0 + gh/2 + 20, gx0 + gw, gy0 + gh/2 + 20, color=LINE, sw=1.8))
    p.append(text(gx0 - 10, gy0 - gh/2 - 10, "Помилка (px)", size=10, color=MUTED, anchor="end"))
    p.append(text(gx0 + gw, gy0 + gh/2 + 38, "Час t (с) →", size=10, color=MUTED, anchor="end"))

    # Траєкторія 1: Без компенсації затримки (фазовий зсув, автоколивання, розгойдування)
    # Синусоїда зі зростанням амплітуди / граничний цикл
    pts_uncomp = []
    import math
    for i in range(120):
        t = i / 120.0
        x = gx0 + t * gw
        # Коливання з запізненням
        val = 70.0 * math.exp(-0.4 * t) * math.cos(2 * math.pi * 3.5 * t) + 25.0 * math.sin(2 * math.pi * 3.5 * t)
        y = gy0 - val
        pts_uncomp.append(f"{x:.1f},{y:.1f}")

    p.append(f'<polyline points="{" ".join(pts_uncomp)}" fill="none" stroke="{POS}" stroke-width="2.2"/>')
    p.append(text(gx0 + 230, gy0 - 68, "Без компенсації (лаг → автоколивання)", size=10.5, color=POS, bold=True))

    # Траєкторія 2: З фільтром Калмана та екстраполяцією (швидке аперіодичне згасання)
    pts_comp = []
    for i in range(120):
        t = i / 120.0
        x = gx0 + t * gw
        # Аперіодичний перехідний процес
        val = 70.0 * math.exp(-5.5 * t) * math.cos(2 * math.pi * 0.8 * t)
        y = gy0 - val
        pts_comp.append(f"{x:.1f},{y:.1f}")

    p.append(f'<polyline points="{" ".join(pts_comp)}" fill="none" stroke="{FIELD}" stroke-width="2.4"/>')
    p.append(text(gx0 + 130, gy0 + 45, "З фільтром Калмана (компенсовано)", size=10.5, color=FIELD, bold=True))

    # Пояснення фазового зсуву
    p.append(fitbox(500, 390, 390, 80,
                    "Фазове запізнення регулятора:\n"
                    "• При частоті супроводу f = 2.5 Гц і затримці T = 110 мс:\n"
                    "  Фазовий зсув: Δφ = 2π · f · T = 2π · 2.5 · 0.11 ≈ 99° (втрата запасу стійкості!)\n"
                    "• Екстраполяція повертає фазу, усуваючи зрив стеження.",
                    size=10.5, pad=8, fill="#f8fafc", stroke="#94a3b8", color=INK))

    render(os.path.join(OUT, "latency-timeline-oscillation.svg"), W, H, *p,
           title="Анатомія затримки кадру та її вплив на стійкість контуру візуального супроводу")


if __name__ == "__main__":
    fig_camera_pinhole_angles()
    fig_ibvs_control_loop()
    fig_latency_timeline_oscillation()
    print("All figures generated successfully.")
