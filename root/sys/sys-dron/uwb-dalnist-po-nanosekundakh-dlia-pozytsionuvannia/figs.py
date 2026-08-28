# -*- coding: utf-8 -*-
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_uwb_pulse_vs_narrowband():
    """Порівняння вузькосмугового радіосигналу та надкороткого імпульсу UWB у часовій області та при багатопроменевості."""
    W, H = 840, 370
    p = []

    p.append(text(W / 2, 26, "Вузькосмуговий сигнал проти UWB: розділення прямого променя та відлуння", size=15, bold=True))

    # Ліва панель: Вузькосмуговий сигнал (Wi-Fi / BLE)
    p.append(rect(20, 50, 390, 305, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(215, 74, "Вузькосмуговий сигнал (Wi-Fi / BLE, Δf = 20 МГц)", size=12, bold=True, color=INK))
    p.append(text(215, 92, "Тривалість символу T ≈ 50 нс (довжина хвилі в просторі 15 м)", size=10, color=MUTED))

    cx1, cy1 = 60, 160
    # Прямий сигнал
    p.append(text(cx1, cy1 - 25, "Прямий промінь (LOS)", size=10, bold=True, color=FIELD))
    pts_los = []
    for i in range(120):
        t = i * 2.5
        y = cy1 - 20 * math.sin(i * 0.25) * math.exp(-((i - 40) ** 2) / 600.0)
        pts_los.append("%.1f,%.1f" % (cx1 + t, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(pts_los), FIELD))

    # Відбитий сигнал (Multipath)
    cy1_mp = 225
    p.append(text(cx1, cy1_mp - 25, "Відбитий промінь (затримка 10 нс = 3 м)", size=10, bold=True, color=POS))
    pts_mp = []
    for i in range(120):
        t = i * 2.5
        y = cy1_mp - 15 * math.sin((i - 15) * 0.25) * math.exp(-((i - 55) ** 2) / 600.0)
        pts_mp.append("%.1f,%.1f" % (cx1 + t, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,2"/>' % (" ".join(pts_mp), POS))

    # Результуючий сигнал на антені
    cy1_sum = 295
    p.append(text(cx1, cy1_sum - 20, "Сума на приймачі: інтерференція та фазовий зсув", size=10, bold=True, color=NEG))
    pts_sum = []
    for i in range(120):
        t = i * 2.5
        y1 = -20 * math.sin(i * 0.25) * math.exp(-((i - 40) ** 2) / 600.0)
        y2 = -15 * math.sin((i - 15) * 0.25) * math.exp(-((i - 55) ** 2) / 600.0)
        pts_sum.append("%.1f,%.1f" % (cx1 + t, cy1_sum + y1 + y2))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_sum), NEG))
    p.append(text(215, 342, "Помилка фіксації фронту: ±3–10 метрів", size=10, bold=True, color=NEG))

    # Права панель: Надширокосмуговий сигнал UWB
    p.append(rect(430, 50, 390, 305, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(625, 74, "Надширокосмуговий імпульс UWB (Δf ≥ 500 МГц)", size=12, bold=True, color=INK))
    p.append(text(625, 92, "Тривалість імпульсу T ≈ 2 нс (просторова довжина 60 см)", size=10, color=MUTED))

    cx2 = 470
    # Прямий імпульс
    p.append(text(cx2, cy1 - 25, "Прямий імпульс (LOS)", size=10, bold=True, color=FIELD))
    pts_uwb_los = []
    for i in range(120):
        t = i * 2.5
        x_val = (i - 30) / 4.0
        y = cy1 - 26 * math.exp(-(x_val ** 2)) * math.cos(x_val * 3.5)
        pts_uwb_los.append("%.1f,%.1f" % (cx2 + t, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(pts_uwb_los), FIELD))

    # Відбитий імпульс (чітко розділений у часі)
    p.append(text(cx2, cy1_mp - 25, "Відбитий імпульс (затримка 10 нс)", size=10, bold=True, color=POS))
    pts_uwb_mp = []
    for i in range(120):
        t = i * 2.5
        x_val = (i - 75) / 4.0
        y = cy1_mp - 18 * math.exp(-(x_val ** 2)) * math.cos(x_val * 3.5)
        pts_uwb_mp.append("%.1f,%.1f" % (cx2 + t, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,2"/>' % (" ".join(pts_uwb_mp), POS))

    # Результуючий профіль на приймачі
    p.append(text(cx2, cy1_sum - 20, "Розділені імпульси: перший фронт фіксується точно", size=10, bold=True, color=FIELD))
    pts_uwb_sum = []
    for i in range(120):
        t = i * 2.5
        x1 = (i - 30) / 4.0
        x2_val = (i - 75) / 4.0
        y1 = -26 * math.exp(-(x1 ** 2)) * math.cos(x1 * 3.5)
        y2 = -18 * math.exp(-(x2_val ** 2)) * math.cos(x2_val * 3.5)
        pts_uwb_sum.append("%.1f,%.1f" % (cx2 + t, cy1_sum + y1 + y2))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_uwb_sum), FIELD))

    # Маркер першого приходу
    p.append(arrow(cx2 + 75, cy1_sum + 20, cx2 + 75, cy1_sum - 15, color=POS, sw=1.5))
    p.append(text(cx2 + 80, cy1_sum + 28, "ToA (15.65 пс)", size=9, bold=True, color=POS))
    p.append(text(625, 342, "Похибка дальності: ±5–10 сантиметрів", size=10, bold=True, color=FIELD))

    render(os.path.join(OUT, "uwb-pulse-vs-narrowband.svg"), W, H, *p)


def fig_twr_ranging_protocols():
    """Часові діаграми одностороннього (SS-TWR) та симетричного двостороннього (DS-TWR) вимірювання дальності."""
    W, H = 840, 380
    p = []

    p.append(text(W / 2, 26, "Протоколи вимірювання дальності: односторонній (SS-TWR) та подвійний (DS-TWR)", size=15, bold=True))

    # Ліва панель: SS-TWR
    p.append(rect(20, 50, 390, 315, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(215, 74, "Single-Sided TWR (SS-TWR)", size=12, bold=True, color=INK))
    p.append(text(215, 92, "2 повідомлення: чутливий до дрейфу кварцу", size=10, color=MUTED))

    # Лінії вузлів
    p.append(line(80, 115, 80, 275, color="#64748b", sw=2.0))
    p.append(line(350, 115, 350, 275, color="#64748b", sw=2.0))
    p.append(text(80, 110, "Дрон (Tag)", size=11, bold=True, color=INK))
    p.append(text(350, 110, "Анкер (Anchor)", size=11, bold=True, color=INK))

    # Повідомлення Poll
    p.append(arrow(80, 135, 350, 175, color=FIELD, sw=2.0))
    p.append(text(215, 145, "1. Poll", size=10, bold=True, color=FIELD))
    p.append(circle(80, 135, 3.5, fill=FIELD, stroke=FIELD, sw=1.0))
    p.append(circle(350, 175, 3.5, fill=FIELD, stroke=FIELD, sw=1.0))
    p.append(text(65, 138, "t₁", size=10, bold=True, color=INK))
    p.append(text(365, 178, "t₂", size=10, bold=True, color=INK))

    # Повідомлення Response
    p.append(arrow(350, 215, 80, 255, color=POS, sw=2.0))
    p.append(text(215, 225, "2. Response (містить t₂, t₃)", size=10, bold=True, color=POS))
    p.append(circle(350, 215, 3.5, fill=POS, stroke=POS, sw=1.0))
    p.append(circle(80, 255, 3.5, fill=POS, stroke=POS, sw=1.0))
    p.append(text(365, 218, "t₃", size=10, bold=True, color=INK))
    p.append(text(65, 258, "t₄", size=10, bold=True, color=INK))

    # Часові інтервали
    p.append(line(45, 135, 45, 255, color=FIELD, sw=1.5))
    p.append(text(30, 198, "T_round", size=9, bold=True, color=FIELD))
    p.append(line(385, 175, 385, 215, color=POS, sw=1.5))
    p.append(text(398, 198, "T_reply", size=9, bold=True, color=POS))

    p.append(text(215, 298, "ToF = ½ (T_round − T_reply)", size=11, bold=True, color=INK))
    p.append(text(215, 320, "Похибка: Δf · T_reply (при 20 ppm і 1 мс → 6 метрів!)", size=9, bold=True, color=NEG))
    p.append(text(215, 345, "Використовується лише з підстроюванням несучої", size=9, color=MUTED))

    # Права панель: DS-TWR
    p.append(rect(430, 50, 390, 315, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(625, 74, "Double-Sided TWR (DS-TWR)", size=12, bold=True, color=INK))
    p.append(text(625, 92, "3 повідомлення: повна взаємна компенсація дрейфу", size=10, color=MUTED))

    # Лінії вузлів
    p.append(line(490, 115, 490, 280, color="#64748b", sw=2.0))
    p.append(line(760, 115, 760, 280, color="#64748b", sw=2.0))
    p.append(text(490, 110, "Дрон (Tag)", size=11, bold=True, color=INK))
    p.append(text(760, 110, "Анкер (Anchor)", size=11, bold=True, color=INK))

    # 1. Poll
    p.append(arrow(490, 130, 760, 160, color=FIELD, sw=1.8))
    p.append(text(625, 138, "1. Poll", size=9, bold=True, color=FIELD))
    p.append(circle(490, 130, 3.0, fill=FIELD, stroke=FIELD, sw=1.0))
    p.append(circle(760, 160, 3.0, fill=FIELD, stroke=FIELD, sw=1.0))
    p.append(text(475, 133, "t₁", size=9, bold=True, color=INK))
    p.append(text(775, 163, "t₂", size=9, bold=True, color=INK))

    # 2. Response
    p.append(arrow(760, 190, 490, 220, color=POS, sw=1.8))
    p.append(text(625, 198, "2. Response", size=9, bold=True, color=POS))
    p.append(circle(760, 190, 3.0, fill=POS, stroke=POS, sw=1.0))
    p.append(circle(490, 220, 3.0, fill=POS, stroke=POS, sw=1.0))
    p.append(text(775, 193, "t₃", size=9, bold=True, color=INK))
    p.append(text(475, 223, "t₄", size=9, bold=True, color=INK))

    # 3. Final
    p.append(arrow(490, 245, 760, 275, color=LINE, sw=1.8))
    p.append(text(625, 253, "3. Final (містить t₁, t₄, t₅)", size=9, bold=True, color=LINE))
    p.append(circle(490, 245, 3.0, fill=LINE, stroke=LINE, sw=1.0))
    p.append(circle(760, 275, 3.0, fill=LINE, stroke=LINE, sw=1.0))
    p.append(text(475, 248, "t₅", size=9, bold=True, color=INK))
    p.append(text(775, 278, "t₆", size=9, bold=True, color=INK))

    p.append(text(625, 305, "ToF = (T_r1 · T_r2 − T_p1 · T_p2) / (T_r1 + T_r2 + T_p1 + T_p2)", size=10, bold=True, color=INK))
    p.append(text(625, 325, "Залишкова похибка: ~0.4 пс (0.12 мм при 20 ppm)", size=9, bold=True, color=FIELD))
    p.append(text(625, 345, "Стандарт точного 3D-позиціонування дронів", size=9, color=MUTED))

    render(os.path.join(OUT, "twr-ranging-protocols.svg"), W, H, *p)


def fig_trilateration_vs_tdoa():
    """Порівняння трилатерації (TWR TOF) та гіперболічного позиціонування (TDoA)."""
    W, H = 840, 380
    p = []

    p.append(text(W / 2, 26, "Геометрія навігації: сферична трилатерація (ToF) проти гіперболічної (TDoA)", size=15, bold=True))

    # Ліва панель: Трилатерація ToF
    p.append(rect(20, 50, 390, 315, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(215, 74, "Трилатерація ToF (TWR: перетин сфер)", size=12, bold=True, color=INK))
    p.append(text(215, 92, "Кожен дрон опитує всі анкери: O(N_tags · N_anchors)", size=10, color=MUTED))

    # Анкери A1, A2, A3
    a1_x, a1_y = 140, 180
    a2_x, a2_y = 290, 180
    a3_x, a3_y = 215, 245

    # Дрон
    drone_x, drone_y = 215, 185

    # Кола відстаней (сфери)
    r1 = math.hypot(drone_x - a1_x, drone_y - a1_y)
    r2 = math.hypot(drone_x - a2_x, drone_y - a2_y)
    r3 = math.hypot(drone_x - a3_x, drone_y - a3_y)

    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#0284c7" stroke-width="1.4" stroke-dasharray="4,3"/>' % (a1_x, a1_y, r1))
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#0284c7" stroke-width="1.4" stroke-dasharray="4,3"/>' % (a2_x, a2_y, r2))
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#0284c7" stroke-width="1.4" stroke-dasharray="4,3"/>' % (a3_x, a3_y, r3))

    # Промені
    p.append(line(a1_x, a1_y, drone_x, drone_y, color="#0284c7", sw=1.2))
    p.append(line(a2_x, a2_y, drone_x, drone_y, color="#0284c7", sw=1.2))
    p.append(line(a3_x, a3_y, drone_x, drone_y, color="#0284c7", sw=1.2))

    # Вузли
    p.append(rect(a1_x - 12, a1_y - 12, 24, 24, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    p.append(text(a1_x, a1_y + 4, "A₁", size=10, bold=True, color="#0284c7"))

    p.append(rect(a2_x - 12, a2_y - 12, 24, 24, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    p.append(text(a2_x, a2_y + 4, "A₂", size=10, bold=True, color="#0284c7"))

    p.append(rect(a3_x - 12, a3_y - 12, 24, 24, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    p.append(text(a3_x, a3_y + 4, "A₃", size=10, bold=True, color="#0284c7"))

    # Дрон
    p.append(circle(drone_x, drone_y, 6.5, fill=POS, stroke=POS, sw=1.5))
    p.append(text(drone_x, drone_y - 11, "Дрон (Tag)", size=10, bold=True, color=POS))

    p.append(text(215, 325, "Перетин кіл: (x − xᵢ)² + (y − yᵢ)² = dᵢ²", size=10, bold=True, color=INK))
    p.append(text(215, 345, "Обмежена місткість (до 5–15 дронів одночасно)", size=9, color=NEG, bold=True))

    # Права панель: Гіперболічна навігація TDoA
    p.append(rect(430, 50, 390, 315, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(625, 74, "Гіперболічна навігація (TDoA)", size=12, bold=True, color=INK))
    p.append(text(625, 92, "Дрон лише блимає (Blink): необмежена кількість дронів", size=10, color=MUTED))

    ta1_x, ta1_y = 535, 180
    ta2_x, ta2_y = 715, 180
    ta3_x, ta3_y = 625, 245
    tdrone_x, tdrone_y = 620, 185

    # Гіперболи (множина точок з постійною різницею відстаней |d1 - d2| = const)
    pts_hyp1 = []
    pts_hyp2 = []
    # Пара A1-A2: фокусні точки
    d1_true = math.hypot(tdrone_x - ta1_x, tdrone_y - ta1_y)
    d2_true = math.hypot(tdrone_x - ta2_x, tdrone_y - ta2_y)
    diff12 = d1_true - d2_true

    for y_step in range(115, 295, 4):
        for x_test in range(450, 800, 2):
            val = math.hypot(x_test - ta1_x, y_step - ta1_y) - math.hypot(x_test - ta2_x, y_step - ta2_y)
            if abs(val - diff12) < 2.5:
                pts_hyp1.append("%.1f,%d" % (x_test, y_step))
                break

    if len(pts_hyp1) > 2:
        p.append('<polyline points="%s" fill="none" stroke="#d97706" stroke-width="1.8"/>' % " ".join(pts_hyp1))

    # Пара A1-A3
    d3_true = math.hypot(tdrone_x - ta3_x, tdrone_y - ta3_y)
    diff13 = d1_true - d3_true
    for y_step in range(115, 295, 4):
        for x_test in range(450, 800, 2):
            val = math.hypot(x_test - ta1_x, y_step - ta1_y) - math.hypot(x_test - ta3_x, y_step - ta3_y)
            if abs(val - diff13) < 2.5:
                pts_hyp2.append("%.1f,%d" % (x_test, y_step))
                break

    if len(pts_hyp2) > 2:
        p.append('<polyline points="%s" fill="none" stroke="#059669" stroke-width="1.8"/>' % " ".join(pts_hyp2))

    # Хвилі від дрона (Blink)
    p.append('<circle cx="%.1f" cy="%.1f" r="20" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' % (tdrone_x, tdrone_y, POS))
    p.append('<circle cx="%.1f" cy="%.1f" r="40" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' % (tdrone_x, tdrone_y, POS))
    p.append('<circle cx="%.1f" cy="%.1f" r="60" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' % (tdrone_x, tdrone_y, POS))

    # Вузли
    p.append(rect(ta1_x - 12, ta1_y - 12, 24, 24, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    p.append(text(ta1_x, ta1_y + 4, "A₁", size=10, bold=True, color="#d97706"))

    p.append(rect(ta2_x - 12, ta2_y - 12, 24, 24, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    p.append(text(ta2_x, ta2_y + 4, "A₂", size=10, bold=True, color="#d97706"))

    p.append(rect(ta3_x - 12, ta3_y - 12, 24, 24, fill="#dcfce7", stroke="#059669", sw=1.5, rx=4))
    p.append(text(ta3_x, ta3_y + 4, "A₃", size=10, bold=True, color="#059669"))

    # Дрон
    p.append(circle(tdrone_x, tdrone_y, 6.5, fill=POS, stroke=POS, sw=1.5))
    p.append(text(tdrone_x, tdrone_y - 11, "Дрон (Tag Blink)", size=10, bold=True, color=POS))

    p.append(text(625, 325, "Перетин гіпербол: dᵢ − dⱼ = c · (tᵢ − tⱼ)", size=10, bold=True, color=INK))
    p.append(text(625, 345, "Вимагає жорсткої наносекундної синхронізації анкерів", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "trilateration-vs-tdoa.svg"), W, H, *p)


def fig_cir_los_vs_nlos():
    """Профіль імпульсної характеристики каналу (CIR) в умовах прямої видимості (LOS) та перешкоди (NLOS)."""
    W, H = 840, 370
    p = []

    p.append(text(W / 2, 26, "Діагностика каналу CIR: детектування прямої видимості (LOS) та перешкод (NLOS)", size=15, bold=True))

    # Ліва панель: LOS (Line-of-Sight)
    p.append(rect(20, 50, 390, 305, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(215, 74, "1. Пряма видимість (LOS)", size=12, bold=True, color=FIELD))
    p.append(text(215, 92, "Перший імпульс — найпотужніший пік (FPP ≈ RXP)", size=10, color=MUTED))

    gx1, gy1 = 50, 270
    gw1, gh1 = 330, 160
    # Осі
    p.append(line(gx1, gy1, gx1 + gw1, gy1, color=INK, sw=1.5))
    p.append(line(gx1, gy1, gx1, gy1 - gh1, color=INK, sw=1.5))
    p.append(text(gx1 + gw1 - 10, gy1 + 18, "Час / Відліки CIR (нс)", size=9, bold=True, color=INK))
    p.append(text(gx1, gy1 - gh1 - 8, "Амплітуда |h(t)|", size=9, bold=True, color=INK))

    # Рівень шуму
    p.append(line(gx1, gy1 - 20, gx1 + gw1, gy1 - 20, color="#94a3b8", sw=1.0, dash="3,3"))
    p.append(text(gx1 + 65, gy1 - 24, "Поріг шуму (Noise Floor)", size=9, color=MUTED))

    # Крива CIR LOS
    pts_cir_los = []
    for i in range(gw1):
        noise = 5.0 + 3.0 * math.sin(i * 1.5) * math.cos(i * 0.7)
        fp = 135.0 * math.exp(-((i - 60) ** 2) / 18.0)
        mp1 = 45.0 * math.exp(-((i - 120) ** 2) / 35.0)
        mp2 = 25.0 * math.exp(-((i - 180) ** 2) / 50.0)
        mp3 = 15.0 * math.exp(-((i - 240) ** 2) / 70.0)
        y_val = gy1 - (noise + fp + mp1 + mp2 + mp3)
        pts_cir_los.append("%.1f,%.1f" % (gx1 + i, y_val))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(pts_cir_los), FIELD))

    # Маркер First Path
    p.append(circle(gx1 + 60, gy1 - 140, 4.0, fill=FIELD, stroke=FIELD, sw=1.0))
    p.append(arrow(gx1 + 60, gy1 - 160, gx1 + 60, gy1 - 144, color=FIELD, sw=1.5))
    p.append(text(gx1 + 60, gy1 - 165, "Перший промінь (FP)", size=9, bold=True, color=FIELD))

    p.append(text(215, 305, "Різниця потужностей: RXP − FPP < 6 дБ", size=10, bold=True, color=FIELD))
    p.append(text(215, 325, "Дальність валідна: похибка < 10 см", size=9, color=FIELD))

    # Права панель: NLOS (Non-Line-of-Sight)
    p.append(rect(430, 50, 390, 305, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(625, 74, "2. Перешкода (NLOS: стіна / перегородка)", size=12, bold=True, color=NEG))
    p.append(text(625, 92, "Перший промінь ослаблений, відлуння переважає", size=10, color=MUTED))

    gx2 = 460
    # Осі
    p.append(line(gx2, gy1, gx2 + gw1, gy1, color=INK, sw=1.5))
    p.append(line(gx2, gy1, gx2, gy1 - gh1, color=INK, sw=1.5))
    p.append(text(gx2 + gw1 - 10, gy1 + 18, "Час / Відліки CIR (нс)", size=9, bold=True, color=INK))
    p.append(text(gx2, gy1 - gh1 - 8, "Амплітуда |h(t)|", size=9, bold=True, color=INK))

    # Рівень шуму
    p.append(line(gx2, gy1 - 20, gx2 + gw1, gy1 - 20, color="#94a3b8", sw=1.0, dash="3,3"))
    p.append(text(gx2 + 65, gy1 - 24, "Поріг шуму (Noise Floor)", size=9, color=MUTED))

    # Крива CIR NLOS
    pts_cir_nlos = []
    for i in range(gw1):
        noise = 5.0 + 3.0 * math.sin(i * 1.5) * math.cos(i * 0.7)
        fp = 22.0 * math.exp(-((i - 60) ** 2) / 25.0)
        mp1 = 110.0 * math.exp(-((i - 130) ** 2) / 40.0)
        mp2 = 75.0 * math.exp(-((i - 175) ** 2) / 45.0)
        mp3 = 40.0 * math.exp(-((i - 230) ** 2) / 60.0)
        y_val = gy1 - (noise + fp + mp1 + mp2 + mp3)
        pts_cir_nlos.append("%.1f,%.1f" % (gx2 + i, y_val))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(pts_cir_nlos), NEG))

    # Маркери
    p.append(circle(gx2 + 60, gy1 - 27, 3.5, fill=MUTED, stroke=MUTED, sw=1.0))
    p.append(text(gx2 + 60, gy1 - 35, "Ослаблений FP", size=9, color=MUTED))

    p.append(circle(gx2 + 130, gy1 - 115, 4.0, fill=NEG, stroke=NEG, sw=1.0))
    p.append(arrow(gx2 + 130, gy1 - 138, gx2 + 130, gy1 - 120, color=NEG, sw=1.5))
    p.append(text(gx2 + 130, gy1 - 145, "Хибний пік (Multipath)", size=9, bold=True, color=NEG))

    p.append(text(625, 305, "Різниця потужностей: RXP − FPP > 10 дБ", size=10, bold=True, color=NEG))
    p.append(text(625, 325, "NLOS детектовано: дальність завищена на 0.5–2.0 м", size=9, bold=True, color=NEG))

    render(os.path.join(OUT, "cir-los-vs-nlos.svg"), W, H, *p)


if __name__ == "__main__":
    fig_uwb_pulse_vs_narrowband()
    fig_twr_ranging_protocols()
    fig_trilateration_vs_tdoa()
    fig_cir_los_vs_nlos()
    print("All 4 UWB figures generated successfully in img/")
