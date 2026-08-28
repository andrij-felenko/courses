# -*- coding: utf-8 -*-
"""Фігури для теми vidtvorennia-intsydentu-z-trokh-dzherel.
Генерує SVG-ілюстрації для статті про відтворення інцидентів з трьох джерел:
1. three-sources-truth.svg — три модальності спостереження (борт, станція, відео).
2. timeline-alignment-anchors.svg — вирівнювання часових шкал за опорними подіями.
3. clock-drift-cross-correlation.svg — двоступеневе усунення зміщення та дрейфу годинників.
4. power-loss-signature.svg — мультимодальна сигнатура раптового знеструмлення.
5. ekf-divergence-toilet-bowl.svg — автограф зриву давача та розбіжності інновацій EKF.
6. pilot-vs-autopilot-collision.svg — зіставлення команд пілота проти реакції автопілота.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. three-sources-truth: порівняння трьох модальностей даних ──────────────
def fig_three_sources_truth():
    W, H = 860, 420
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 28, "Три джерела правди в розслідуванні інциденту", size=16, color=INK, bold=True))

    # Три колонки
    cols = [
        {
            "x": 40, "w": 240, "title": "Бортовий лог (.bin / .ulg)",
            "color": POS, "bg": "#fdf3f2",
            "items": [
                "Частота: 50–400 Гц",
                "Шкала: монотонна (boot_us)",
                "Джерело: SPI Flash / SD-карта",
                "Дані: IMU, EKF, PID, ESC, струм",
                "Перевага: мікросекундна глибина",
                "Вразливість: втрата буфера при аварії"
            ]
        },
        {
            "x": 310, "w": 240, "title": "Лог станції (.tlog)",
            "color": NEG, "bg": "#f0f4fd",
            "items": [
                "Частота: 2–10 Гц",
                "Шкала: стінний час (UTC epoch)",
                "Джерело: накопичувач GCS ноутбука",
                "Дані: команди пілота, RSSI, пакети",
                "Перевага: виживає при загибелі дрона",
                "Вразливість: латентність і втрати радіо"
            ]
        },
        {
            "x": 580, "w": 240, "title": "Відеозапис камери (MP4)",
            "color": FIELD, "bg": "#f0faf3",
            "items": [
                "Частота: 30–60 fps + аудіо",
                "Шкала: кадри / таймкоди PTS",
                "Джерело: незалежна Flash-карта",
                "Дані: візуальний простір, OSD, звук",
                "Перевага: об'єктивна фізична дійсність",
                "Вразливість: немає внутрішніх станів"
            ]
        }
    ]

    for col in cols:
        cx = col["x"] + col["w"] / 2
        p.append(rect(col["x"], 55, col["w"], 270, fill=col["bg"], stroke=col["color"], sw=1.8, rx=8))
        p.append(rect(col["x"], 55, col["w"], 38, fill=col["color"], stroke=col["color"], sw=1.8, rx=8))
        # зрізати нижні кути шапки прямокутником
        p.append(rect(col["x"], 75, col["w"], 18, fill=col["color"], stroke=col["color"], sw=0, rx=0))
        p.append(text(cx, 79, col["title"], size=13, color="#ffffff", bold=True))

        for i, itm in enumerate(col["items"]):
            iy = 116 + i * 32
            p.append(circle(col["x"] + 16, iy - 4, 3, fill=col["color"], stroke=col["color"], sw=1))
            p.append(text(col["x"] + 28, iy, itm, size=11, color=INK, anchor="start"))

    # Центральний блок злиття знизу
    b_fuse, _, _ = textbox(W / 2, 375,
                           "Алгоритмічне злиття: відновлення єдиного детермінованого ланцюга подій\n"
                           "компенсація латентності, зшивання шкал та локалізація першопричини",
                           size=12, color=INK, bold=True, fill=FILL, stroke=LINE, sw=1.6, pad=12)
    p.append(b_fuse)

    # Стрілки від колонок до блоку злиття
    p.append(arrow(160, 325, 290, 355, color=POS, sw=1.6))
    p.append(arrow(430, 325, 430, 350, color=NEG, sw=1.6))
    p.append(arrow(700, 325, 570, 355, color=FIELD, sw=1.6))

    render(os.path.join(OUT, "three-sources-truth.svg"), W, H, *p)


# ── 2. timeline-alignment-anchors: вирівнювання за опорними подіями ──────────
def fig_timeline_alignment_anchors():
    W, H = 880, 430
    p = []

    p.append(text(W / 2, 26, "Вирівнювання часових шкал за дискретними опорними подіями", size=16, color=INK, bold=True))

    # Три несинхронізовані осі
    y_boot = 90
    y_gcs = 190
    y_vid = 290
    ax_start, ax_end = 120, 820

    p.append(text(50, y_boot + 4, "Борт (t_boot)\n[μs від старту]", size=11, color=POS, bold=True, anchor="middle"))
    p.append(arrow(ax_start, y_boot, ax_end, y_boot, color=POS, sw=2))

    p.append(text(50, y_gcs + 4, "Станція (t_gcs)\n[UTC epoch ms]", size=11, color=NEG, bold=True, anchor="middle"))
    p.append(arrow(ax_start, y_gcs, ax_end, y_gcs, color=NEG, sw=2))

    p.append(text(50, y_vid + 4, "Відео (t_pts)\n[кадри / секунди]", size=11, color=FIELD, bold=True, anchor="middle"))
    p.append(arrow(ax_start, y_vid, ax_end, y_vid, color=FIELD, sw=2))

    # Опорні події (Anchors): X-позиції на різних шкалах через зміщення
    # Подія 1: Arming (Армінг моторів)
    x_b1, x_g1, x_v1 = 200, 245, 175
    # Подія 2: Перемикання режиму (Mode Switch)
    x_b2, x_g2, x_v2 = 420, 467, 396
    # Подія 3: Втрата зв'язку (Link Loss / Failsafe)
    x_b3, x_g3, x_v3 = 600, 649, 577
    # Подія 4: Фізичний удар / краш (Impact / Shock)
    x_b4, x_g4, x_v4 = 750, 799, 728

    anchors = [
        {"title": "Подія 1: Армінг", "sub": "STATUSTEXT vs звук обертів", "xb": x_b1, "xg": x_g1, "xv": x_v1, "col": "#d35400"},
        {"title": "Подія 2: Зміна режиму", "sub": "MAV_CMD vs регістр режиму", "xb": x_b2, "xg": x_g2, "xv": x_v2, "col": "#8e44ad"},
        {"title": "Подія 3: Failsafe зв'язку", "sub": "Таймаут Heartbeat vs RC-втрата", "xb": x_b3, "xg": x_g3, "xv": x_v3, "col": "#c0392b"},
        {"title": "Подія 4: Удар (Impact)", "sub": "Пік 16g IMU vs струс камери", "xb": x_b4, "xg": x_g4, "xv": x_v4, "col": "#2c3e50"},
    ]

    for anc in anchors:
        col = anc["col"]
        # Точки на осях
        p.append(circle(anc["xb"], y_boot, 5, fill=col, stroke="#ffffff", sw=1.5))
        p.append(circle(anc["xg"], y_gcs, 5, fill=col, stroke="#ffffff", sw=1.5))
        p.append(circle(anc["xv"], y_vid, 5, fill=col, stroke="#ffffff", sw=1.5))

        # Сполучні пунктирні лінії між осями
        p.append(line(anc["xb"], y_boot, anc["xg"], y_gcs, color=col, sw=1.6, dash="4 3"))
        p.append(line(anc["xg"], y_gcs, anc["xv"], y_vid, color=col, sw=1.6, dash="4 3"))

    # Позначення розриву/зсуву шкал
    p.append(line(x_b1, y_boot - 15, x_b1, y_boot + 15, color=POS, sw=1.5))
    p.append(line(x_g1, y_gcs - 15, x_g1, y_gcs + 15, color=NEG, sw=1.5))
    b_shift, _, _ = textbox(300, 140, "Δt_gcs ≈ +45 с\n(зсув епохи)", size=9, color=NEG, bold=True,
                            fill="#f0f4fd", stroke=NEG, sw=1.2, pad=4)
    p.append(b_shift)

    # Нижній пояснювальний блок
    by = 360
    for i, anc in enumerate(anchors):
        bx = 130 + i * 195
        b_box, _, _ = textbox(bx, by, anc["title"] + "\n" + anc["sub"], size=10, color=INK,
                              bold=True, fill="#fafafa", stroke=anc["col"], sw=1.4, pad=6)
        p.append(b_box)
        p.append(arrow(bx, by - 24, anc["xv"], y_vid + 8, color=anc["col"], sw=1.2))

    render(os.path.join(OUT, "timeline-alignment-anchors.svg"), W, H, *p)


# ── 3. clock-drift-cross-correlation: взаємна кореляція та лінійна регресія ─
def fig_clock_drift_cross_correlation():
    W, H = 860, 420
    p = []

    p.append(text(W / 2, 26, "Двоступенева синхронізація: взаємна кореляція та усунення дрейфу", size=16, color=INK, bold=True))

    # Ліва половина: Взаємна кореляція безперервних сигналів R_xy(tau)
    p.append(rect(30, 55, 380, 340, fill="#fdfdfd", stroke=LINE, sw=1.4, rx=8))
    p.append(text(220, 80, "Етап 1. Взаємна кореляція сигналів", size=13, color=INK, bold=True))
    p.append(text(220, 98, "R_xy(τ) = ∑ x[n] · y[n + τ]  (пошук піка суміщення)", size=11, color=MUTED))

    # Графік двох зміщених сигналів
    gx, gy, gw, gh = 60, 120, 320, 110
    p.append(line(gx, gy + gh / 2, gx + gw, gy + gh / 2, color="#e0e0e0", sw=1))
    p.append(arrow(gx, gy + gh, gx, gy - 10, color=LINE, sw=1.2))
    p.append(arrow(gx, gy + gh / 2, gx + gw + 10, gy + gh / 2, color=LINE, sw=1.2))
    p.append(text(gx + gw, gy + gh / 2 + 16, "час t", size=10, color=INK, italic=True))

    # Хвиля 1 (борт)
    pts1 = []
    pts2 = []
    for i in range(0, 101):
        t = i / 100.0
        # сигнал кута нахилу (roll/pitch)
        val = math.sin(t * 12.0) * math.exp(-((t - 0.45) ** 2) / 0.08)
        pts1.append("%.1f,%.1f" % (gx + t * 240, gy + gh / 2 - val * 38))
        # зміщений сигнал станції (із затримкою та дрейфом)
        pts2.append("%.1f,%.1f" % (gx + 40 + t * 240, gy + gh / 2 - val * 35))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts1), POS))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="4 3"/>' % (" ".join(pts2), NEG))

    p.append(text(gx + 40, gy + 20, "Бортовий гіроскоп (x[n])", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(gx + 120, gy + gh - 6, "Телеметрія GCS (y[n])", size=10, color=NEG, bold=True, anchor="start"))

    # Графік кореляційної функції R_xy(tau) знизу
    cy = 280
    p.append(line(gx, cy + 45, gx + gw, cy + 45, color=LINE, sw=1.2))
    p.append(arrow(gx + gw / 2, cy + 55, gx + gw / 2, cy - 5, color=LINE, sw=1.2))
    p.append(text(gx + gw / 2 + 6, cy + 8, "R_xy(τ)", size=10, color=INK, bold=True))

    cpts = []
    for i in range(0, 101):
        tau = (i - 50) / 50.0  # -1..1
        # функція кореляції з чітким піком на tau_opt = 0.25
        cval = math.exp(-((tau - 0.25) ** 2) / 0.03) * 40
        cpts.append("%.1f,%.1f" % (gx + gw / 2 + tau * 120, cy + 45 - cval))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(cpts), FIELD))
    # пік кореляції
    pk_x = gx + gw / 2 + 0.25 * 120
    p.append(line(pk_x, cy + 45, pk_x, cy + 5, color=FIELD, sw=1.5, dash="2 2"))
    p.append(circle(pk_x, cy + 5, 4, fill=FIELD, stroke="#ffffff", sw=1))
    p.append(text(pk_x, cy + 62, "τ_opt = зміщення", size=10, color=FIELD, bold=True))

    # Права половина: Лінійна регресія дрейфу t_gcs = alpha * t_boot + beta
    p.append(rect(440, 55, 390, 340, fill="#fdfdfd", stroke=LINE, sw=1.4, rx=8))
    p.append(text(635, 80, "Етап 2. Лінійна регресія дрейфу кварцу", size=13, color=INK, bold=True))
    p.append(text(635, 98, "t_gcs = α · t_boot + β   (α ≈ 1 + ppm · 10⁻⁶)", size=11, color=MUTED))

    rx, ry, rw, rh = 490, 130, 300, 180
    p.append(arrow(rx, ry + rh, rx + rw + 15, ry + rh, color=LINE, sw=1.4))
    p.append(arrow(rx, ry + rh, rx, ry - 10, color=LINE, sw=1.4))
    p.append(text(rx + rw + 10, ry + rh + 18, "t_boot [с]", size=11, color=POS, bold=True))
    p.append(text(rx - 12, ry - 5, "t_gcs [с]", size=11, color=NEG, bold=True, anchor="end"))

    # Лінія регресії
    p.append(line(rx + 20, ry + rh - 25, rx + rw - 20, ry + 25, color=FIELD, sw=2.2))

    # Точки вимірів опорних подій з відхиленням
    sample_pts = [
        (rx + 35, ry + rh - 40, "Армінг"),
        (rx + 105, ry + rh - 95, "Зліт"),
        (rx + 175, ry + rh - 150, "Пункт 5"),
        (rx + 245, ry + rh - 205, "Аварія")
    ]
    for px, py_val, lbl in sample_pts:
        p.append(circle(px, py_val, 5, fill=POS, stroke=LINE, sw=1.2))
        p.append(text(px + 8, py_val - 8, lbl, size=9, color=INK, bold=True, anchor="start"))

    # Підписи параметрів регресії
    p.append(text(rx + 150, ry + rh - 60, "Нахил α = (1 + Δf/f)\nДрейф генератора: 18 ppm", size=10, color=FIELD, bold=True))
    p.append(text(rx + 30, ry + rh + 16, "β = початковий зсув епохи", size=10, color=MUTED))

    # Результат
    b_res, _, _ = textbox(635, 360, "Залишкова фазова похибка після регресії: < 1.2 мс\nПовний збіг мілісекундних фронтів перемикання ключів",
                          size=10, color=INK, bold=True, fill="#f4fbf6", stroke=FIELD, sw=1.2, pad=6)
    p.append(b_res)

    render(os.path.join(OUT, "clock-drift-cross-correlation.svg"), W, H, *p)


# ── 4. power-loss-signature: мультимодальний автограф раптового знеструмлення ─
def fig_power_loss_signature():
    W, H = 860, 410
    p = []

    p.append(text(W / 2, 26, "Мультимодальна сигнатура раптового обриву живлення", size=16, color=INK, bold=True))

    # Часова вісь спільна
    ox, oy, aw = 120, 70, 680
    t_fail = ox + 430  # момент аварії

    # Вертикальна червона смуга моменту аварії (T_crash)
    p.append(rect(t_fail - 3, 48, 6, 290, fill="#fdecea", stroke=POS, sw=1.2, rx=2))
    p.append(line(t_fail, 48, t_fail, 340, color=POS, sw=1.5, dash="4 2"))
    p.append(text(t_fail, 42, "T_crash (обрив силового роз'єму)", size=11, color=POS, bold=True))

    # Секція 1: Бортовий лог (SPI Flash)
    p.append(text(60, oy + 25, "Борт\n(Flash)", size=11, color=POS, bold=True, anchor="middle"))
    p.append(line(ox, oy + 40, ox + aw, oy + 40, color="#e5e7eb", sw=1))
    # Напруга живлення (падіння)
    pts_v = []
    for x in range(ox, t_fail):
        pts_v.append("%.1f,%.1f" % (x, oy + 15 + math.sin(x * 0.2) * 1.5))
    pts_v.append("%.1f,%.1f" % (t_fail, oy + 38))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_v), POS))
    # Обрив запису (незакритий сектор)
    p.append(rect(t_fail, oy + 5, 80, 30, fill="#fff1f0", stroke=POS, sw=1.5, rx=4))
    p.append(text(t_fail + 40, oy + 23, "ОБРИВ ЗАПИСУ\n(без EOF / CRC)", size=9, color=POS, bold=True))

    # Секція 2: Лог станції (GCS Telemetry)
    gy = oy + 90
    p.append(text(60, gy + 25, "Станція\n(GCS)", size=11, color=NEG, bold=True, anchor="middle"))
    p.append(line(ox, gy + 40, ox + aw, gy + 40, color="#e5e7eb", sw=1))
    # Пакети телеметрії (крапки)
    for x in range(ox + 10, t_fail, 35):
        p.append(circle(x, gy + 20, 3.5, fill=NEG, stroke=LINE, sw=1))
    p.append(circle(t_fail - 15, gy + 20, 3.5, fill=NEG, stroke=LINE, sw=1))
    # Тиша після аварії
    p.append(line(t_fail, gy + 20, ox + aw, gy + 20, color="#d1d5db", sw=1.5, dash="4 4"))
    p.append(text(t_fail + 120, gy + 15, "ТЕЛЕМЕТРИЧНА ТИША (Heartbeat Timeout)", size=10, color=NEG, bold=True))
    p.append(text(t_fail + 120, gy + 32, "RSSI = 0%, латентність буфера GCS", size=9, color=MUTED))

    # Секція 3: Відеозапис (Камера з автономним акумулятором)
    vy = gy + 90
    p.append(text(60, vy + 25, "Відео\n(FPV/Action)", size=11, color=FIELD, bold=True, anchor="middle"))
    p.append(line(ox, vy + 40, ox + aw, vy + 40, color="#e5e7eb", sw=1))
    # Нормальний політ до t_fail
    p.append(rect(ox, vy + 5, t_fail - ox, 30, fill="#f0faf3", stroke=FIELD, sw=1.4, rx=4))
    p.append(text((ox + t_fail) / 2, vy + 24, "Нормальний політ (гул моторів 240 Гц, OSD активне)", size=10, color=FIELD, bold=True))
    # Падіння після t_fail (камера продовжує писати!)
    p.append(rect(t_fail, vy + 5, ox + aw - t_fail, 30, fill="#fff9db", stroke="#f59f00", sw=1.4, rx=4))
    p.append(text(t_fail + (ox + aw - t_fail) / 2, vy + 24, "Перекидання без тяги (тиша моторів, OSD зникло, удар об землю)", size=10, color="#b05200", bold=True))

    # Висновок розслідування знизу
    b_diag, _, _ = textbox(W / 2, 370,
                           "Діагностичний висновок мультимодального розбору:\n"
                           "Раптове механічне розімкнення живлення (не зависання CPU, не відмова мотора, не помилка пілота)",
                           size=11, color=INK, bold=True, fill="#fdfbf7", stroke="#d97706", sw=1.5, pad=8)
    p.append(b_diag)

    render(os.path.join(OUT, "power-loss-signature.svg"), W, H, *p)


# ── 5. ekf-divergence-toilet-bowl: зрив давача та розбіжність EKF ────────────
def fig_ekf_divergence_toilet_bowl():
    W, H = 860, 440
    p = []

    p.append(text(W / 2, 26, "Сигнатура EKF-розбіжності: зрив магнітометра та спіраль «унітазингу»", size=16, color=INK, bold=True))

    # Лівий блок: Траєкторія в просторі (відеозапис зверху)
    p.append(rect(30, 55, 380, 295, fill="#fcfcfc", stroke=LINE, sw=1.4, rx=8))
    p.append(text(220, 78, "Візуальна траєкторія (з камери спостереження)", size=12, color=INK, bold=True))

    # Спіраль унітазингу (toilet-bowl effect)
    sp_cx, sp_cy = 220, 200
    sp_pts = []
    for a in range(0, 720, 10):
        rad = math.radians(a)
        r = 8 + (a / 720.0) * 95
        sx = sp_cx + r * math.cos(rad)
        sy = sp_cy + r * math.sin(rad)
        sp_pts.append("%.1f,%.1f" % (sx, sy))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(sp_pts), POS))
    p.append(circle(sp_cx, sp_cy, 5, fill=FIELD, stroke=LINE, sw=1.2))
    p.append(text(sp_cx + 12, sp_cy - 8, "Точка зависання (PosHold)", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(arrow(sp_cx + 95, sp_cy, sp_cx + 95, sp_cy + 22, color=POS, sw=2))
    p.append(text(sp_cx, sp_cy + 120, "Розбіжна спіраль (позитивний зворотний зв'язок)", size=10, color=POS, bold=True))

    # Правий блок: Сигнали в логу (Інновації EKF та розбіжність курсу)
    p.append(rect(440, 55, 390, 295, fill="#fcfcfc", stroke=LINE, sw=1.4, rx=8))
    p.append(text(635, 78, "Бортовий лог: EKF інновації та розбіжність кутів", size=12, color=INK, bold=True))

    # Верхній підграфік: Курс компаса vs Курс за вектором GPS
    gy1 = 100
    p.append(line(460, gy1 + 50, 790, gy1 + 50, color="#e0e0e0", sw=1))
    p.append(text(460, gy1, "Курс Yaw: Магнітометр проти GPS Velocity", size=10, color=INK, bold=True, anchor="start"))

    # Сигнал 1 (GPS Yaw) - прямий
    p.append(line(460, gy1 + 30, 790, gy1 + 30, color=FIELD, sw=2))
    p.append(text(795, gy1 + 32, "GPS Yaw (факт)", size=9, color=FIELD, bold=True, anchor="start"))

    # Сигнал 2 (Mag Yaw) - дрейфує через наведення силового кабелю
    mpts = []
    for i in range(0, 101):
        t = i / 100.0
        my = gy1 + 30 + (t ** 1.8) * 30
        mpts.append("%.1f,%.1f" % (460 + t * 330, my))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4 2"/>' % (" ".join(mpts), POS))
    p.append(text(795, gy1 + 62, "Mag Yaw (дрейф)", size=9, color=POS, bold=True, anchor="start"))

    # Нижній підграфік: Невпевненість / Інновації EKF (XKF4.SM / XKF4.SV)
    gy2 = 210
    p.append(line(460, gy2 + 60, 790, gy2 + 60, color=LINE, sw=1.2))
    p.append(line(460, gy2 + 30, 790, gy2 + 30, color="#c0392b", sw=1.2, dash="3 3"))
    p.append(text(460, gy2 + 10, "Інноваційний індекс EKF (XKF4.SM / SM_Ratio)", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(795, gy2 + 32, "Поріг (1.0)", size=9, color="#c0392b", bold=True, anchor="start"))

    ipts = []
    for i in range(0, 101):
        t = i / 100.0
        # експоненційне зростання інновацій
        ival = 0.15 + (t ** 3) * 0.95
        ipts.append("%.1f,%.1f" % (460 + t * 330, gy2 + 60 - ival * 30))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(ipts), POS))

    # Висновок знизу
    b_ekf, _, _ = textbox(W / 2, 385,
                          "Діагностичний висновок мультимодального розбору:\n"
                          "Магнітна аномалія спотворила курс EKF, автопілот намагався скомпенсувати уявний дрейф і розкрутив спіраль",
                          size=11, color=INK, bold=True, fill="#fff5f5", stroke=POS, sw=1.3, pad=8)
    p.append(b_ekf)

    render(os.path.join(OUT, "ekf-divergence-toilet-bowl.svg"), W, H, *p)


# ── 6. pilot-vs-autopilot-collision: команда пілота проти збою автопілота ────
def fig_pilot_vs_autopilot_collision():
    W, H = 860, 420
    p = []

    p.append(text(W / 2, 26, "Диференціація провини: команда пілота проти збою автопілота", size=16, color=INK, bold=True))

    # Ліва половина: Випадок А — Помилка пілота (CFIT / Pilot Error)
    p.append(rect(30, 55, 380, 340, fill="#fdfdfd", stroke=LINE, sw=1.4, rx=8))
    p.append(text(220, 80, "Сценарій А: Помилка пілота (CFIT)", size=13, color=POS, bold=True))

    ay = 110
    p.append(line(50, ay + 30, 390, ay + 30, color="#e5e7eb", sw=1))
    p.append(line(50, ay + 90, 390, ay + 90, color="#e5e7eb", sw=1))
    p.append(line(50, ay + 150, 390, ay + 150, color="#e5e7eb", sw=1))

    # Сигнали: Стік пілота (RCIN)
    p.append(text(50, ay + 15, "1. Стік Roll (RCIN.C1)", size=10, color=NEG, bold=True, anchor="start"))
    p.append(line(60, ay + 30, 180, ay + 30, color=NEG, sw=2))
    p.append(line(180, ay + 30, 220, ay + 10, color=NEG, sw=2))
    p.append(line(220, ay + 10, 380, ay + 10, color=NEG, sw=2))
    p.append(text(300, ay + 24, "Команда вліво", size=9, color=NEG, italic=True))

    # Ціль автопілота (RATE.RDes)
    p.append(text(50, ay + 75, "2. Ціль кутової швидкості (RDes)", size=10, color="#8e44ad", bold=True, anchor="start"))
    p.append(line(60, ay + 90, 185, ay + 90, color="#8e44ad", sw=2))
    p.append(line(185, ay + 90, 225, ay + 70, color="#8e44ad", sw=2))
    p.append(line(225, ay + 70, 380, ay + 70, color="#8e44ad", sw=2))

    # Факт гіроскопа (RATE.R)
    p.append(text(50, ay + 135, "3. Факт кутової швидкості (GyrX)", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(line(60, ay + 150, 190, ay + 150, color=FIELD, sw=2))
    p.append(line(190, ay + 150, 230, ay + 130, color=FIELD, sw=2))
    p.append(line(230, ay + 130, 380, ay + 130, color=FIELD, sw=2))

    # Висновок А
    b_res_a, _, _ = textbox(220, 340, "Факт точно повторює команду пілота:\nАвтопілот справний, пілот скерував апарат у перешкоду",
                            size=10, color=POS, bold=True, fill="#fff5f5", stroke=POS, sw=1.2, pad=6)
    p.append(b_res_a)

    # Права половина: Випадок Б — Відмова приводу / Зрив автопілота
    p.append(rect(440, 55, 390, 340, fill="#fdfdfd", stroke=LINE, sw=1.4, rx=8))
    p.append(text(635, 80, "Сценарій Б: Відмова приводу / Апаратури", size=13, color=POS, bold=True))

    by = 110
    p.append(line(460, by + 30, 810, by + 30, color="#e5e7eb", sw=1))
    p.append(line(460, by + 90, 810, by + 90, color="#e5e7eb", sw=1))
    p.append(line(460, by + 150, 810, by + 150, color="#e5e7eb", sw=1))

    # Стік пілота (нейтраль)
    p.append(text(460, by + 15, "1. Стік Roll (RCIN.C1) = нейтраль 1500 μs", size=10, color=NEG, bold=True, anchor="start"))
    p.append(line(470, by + 30, 800, by + 30, color=NEG, sw=2))
    p.append(text(650, by + 24, "Пілот тримає центр", size=9, color=NEG, italic=True))

    # Факт гіроскопа (раптовий неконтрольований зрив)
    p.append(text(460, by + 75, "2. Факт гіроскопа (GyrX) = зрив обертання", size=10, color=POS, bold=True, anchor="start"))
    p.append(line(470, by + 90, 580, by + 90, color=POS, sw=2))
    p.append(line(580, by + 90, 610, by + 60, color=POS, sw=2))
    p.append(line(610, by + 60, 800, by + 60, color=POS, sw=2))

    # Реакція моторів (MOT.Mot1 на максимумі 100%, але апарат не реагує)
    p.append(text(460, by + 135, "3. Вихід мікшера: Мотор 1 на 100% (насичення)", size=10, color="#8e44ad", bold=True, anchor="start"))
    p.append(line(470, by + 160, 585, by + 160, color="#8e44ad", sw=2))
    p.append(line(585, by + 160, 600, by + 130, color="#8e44ad", sw=2))
    p.append(line(600, by + 130, 800, by + 130, color="#8e44ad", sw=2))

    # Висновок Б
    b_res_b, _, _ = textbox(635, 340, "Автопілот бореться, але мотор не дає тяги:\nВідмова ESC/мотора або зрив гвинта (пілот не винен)",
                            size=10, color=FIELD, bold=True, fill="#f4fbf6", stroke=FIELD, sw=1.2, pad=6)
    p.append(b_res_b)

    render(os.path.join(OUT, "pilot-vs-autopilot-collision.svg"), W, H, *p)


def main():
    fig_three_sources_truth()
    fig_timeline_alignment_anchors()
    fig_clock_drift_cross_correlation()
    fig_power_loss_signature()
    fig_ekf_divergence_toilet_bowl()
    fig_pilot_vs_autopilot_collision()
    print("Всі 6 фігур згенеровано успішно у %s" % OUT)


if __name__ == "__main__":
    main()
