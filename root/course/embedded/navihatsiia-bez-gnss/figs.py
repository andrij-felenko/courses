# -*- coding: utf-8 -*-
"""Фігури теми «Навігація без GNSS: що лишається». Запуск: python figs.py → ./img/*.svg"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: накопичення похибки координати з часом (дрейф) ──────────────────
def fig_drift_comparison():
    W, H = 760, 440
    L, R = 80, 420          # графік ліворуч (X: 80..420)
    T, B = 60, 370          # графік Y: 60..370
    parts = []

    # Сітка та осі графіка
    parts.append(line(L, B, R, B, color=MUTED, sw=1.5))
    parts.append(line(L, T, L, B, color=MUTED, sw=1.5))
    parts.append(text((L + R) / 2, B + 34, "Час руху t (секунди) →", size=12, color=INK, bold=True))
    parts.append(text(L - 10, T - 12, "Похибка Δp", size=12, color=INK, anchor="start", bold=True))

    # Позначки осі X (0, 30, 60, 90, 120 с)
    for sec in [0, 30, 60, 90, 120]:
        x = L + (R - L) * (sec / 120.0)
        parts.append(line(x, B, x, B + 5, color=MUTED, sw=1.2))
        parts.append(text(x, B + 18, "%d с" % sec, size=10, color=MUTED))
        if sec > 0:
            parts.append(line(x, T, x, B, color="#e5e7eb", sw=1.0, dash="3 3"))

    # Позначки осі Y (0, 50 м, 200 м, 500 м, 1000 м, 2000 м)
    y_marks = [
        (0, B, "0 м"),
        (50, B - 60, "50 м"),
        (200, B - 120, "200 м"),
        (500, B - 180, "500 м"),
        (1000, B - 240, "1000 м"),
        (2000, B - 295, "2000+ м")
    ]
    for val, y, lbl in y_marks:
        parts.append(line(L - 5, y, L, y, color=MUTED, sw=1.2))
        parts.append(text(L - 10, y + 4, lbl, size=10, color=MUTED, anchor="end"))
        if val > 0:
            parts.append(line(L, y, R, y, color="#e5e7eb", sw=1.0, dash="3 3"))

    # Крива 1: Чистий IMU (Кубічний розгін похибки t³)
    imu_pts = []
    for i in range(0, 101):
        t_sec = 120.0 * (i / 100.0)
        err_m = 0.015 * (t_sec ** 3)
        if err_m <= 50:
            y = B - (err_m / 50.0) * 60
        elif err_m <= 200:
            y = (B - 60) - ((err_m - 50) / 150.0) * 60
        elif err_m <= 500:
            y = (B - 120) - ((err_m - 200) / 300.0) * 60
        elif err_m <= 1000:
            y = (B - 180) - ((err_m - 500) / 500.0) * 60
        else:
            y = (B - 240) - min(1.0, (err_m - 1000) / 1500.0) * 55
        x = L + (R - L) * (i / 100.0)
        imu_pts.append((x, y))
        if err_m >= 2500:
            break

    imu_path = "M " + " L ".join("%.1f %.1f" % p for p in imu_pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (imu_path, POS))

    # Крива 2: Колісна одометрія (Лінійний ріст t)
    odo_pts = []
    for i in range(0, 101):
        t_sec = 120.0 * (i / 100.0)
        err_m = 0.8 * t_sec
        y = B - (err_m / 50.0) * 60 if err_m <= 50 else (B - 60) - ((err_m - 50) / 150.0) * 60
        x = L + (R - L) * (i / 100.0)
        odo_pts.append((x, y))
    odo_path = "M " + " L ".join("%.1f %.1f" % p for p in odo_pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6 3"/>' % (odo_path, NEG))

    # Крива 3: Оптичний потік + ToF + EKF
    flow_pts = []
    for i in range(0, 101):
        t_sec = 120.0 * (i / 100.0)
        err_m = 0.15 * math.sqrt(t_sec) + 0.02 * t_sec
        y = B - (err_m / 50.0) * 60
        x = L + (R - L) * (i / 100.0)
        flow_pts.append((x, y))
    flow_path = "M " + " L ".join("%.1f %.1f" % p for p in flow_pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (flow_path, FIELD))

    # Права частина: 3 інформаційні плашки
    tb_cx = 585
    tb1, _, _ = textbox(tb_cx, 105, "Чистий MEMS IMU (~ t³)\nКубічний дрейф від гіроскопа\n(зсув нахиляє гравітацію g):\nпохибка > 1000 м вже за 60 с",
                        size=11, fill="#fdf2f2", stroke=POS, sw=1.5, color=POS, bold=True)
    parts.append(tb1)

    tb2, _, _ = textbox(tb_cx, 225, "Колісна одометрія (~ t)\nЛінійний ріст похибки:\nпроковзування коліс (1–5%)\nта неточність діаметра шин",
                        size=11, fill="#f0f4ff", stroke=NEG, sw=1.5, color=NEG, bold=True)
    parts.append(tb2)

    tb3, _, _ = textbox(tb_cx, 345, "Оптичний потік + ToF + EKF\nОбмежений дрейф швидкості:\nпохибка швидкості скидається\nдо нуля (~1–3 м на хвилину)",
                        size=11, fill="#f0fff4", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    parts.append(tb3)

    render(os.path.join(IMG, "drift-comparison.svg"), W, H, *parts,
           title="Порівняння дрейфу координат у різних методах без GNSS")


# ── Фігура 2: геометрія вимірювання оптичного потоку та деротація ──────────────
def fig_optical_flow_geometry():
    W, H = 760, 440
    parts = []

    # Верхня частина: корпус апарата з сенсором і гіроскопом
    cx, cy = 250, 75
    body_w, body_h = 170, 42
    parts.append(rect(cx - body_w/2, cy - body_h/2, body_w, body_h, fill="#eef2f7", stroke=LINE, sw=2, rx=6))
    parts.append(text(cx, cy - 4, "Бортовий контролер + IMU", size=11, color=INK, bold=True))
    parts.append(text(cx, cy + 12, "Гіроскоп міряє швидкість ω", size=10, color=MUTED))

    # Сенсор PMW3901 знизу корпусу
    s_w, s_h = 66, 20
    s_y = cy + body_h/2 + s_h/2
    parts.append(rect(cx - s_w/2, s_y - s_h/2, s_w, s_h, fill="#dbeafe", stroke=NEG, sw=1.5, rx=4))
    parts.append(text(cx, s_y + 4, "PMW3901", size=10, color=NEG, bold=True))

    # Лазерний далекомір ToF поруч
    tof_x = cx + body_w/2 - 22
    parts.append(rect(tof_x - 18, s_y - s_h/2, 36, s_h, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    parts.append(text(tof_x, s_y + 4, "ToF", size=10, color="#d97706", bold=True))

    # Лінії променя оптичного зору (конус) до підстильної поверхні
    ground_y = 350
    fov_left_x = 90
    fov_right_x = 410

    # Промінь зору
    parts.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#eff6ff" opacity="0.6" stroke="%s" stroke-width="1.2" stroke-dasharray="4 3"/>' %
                 (cx, s_y + s_h/2, fov_left_x, ground_y, fov_right_x, ground_y, NEG))

    # Лазерний промінь далекоміра (вертикальний пунктир)
    parts.append(line(tof_x, s_y + s_h/2, tof_x, ground_y, color="#d97706", sw=1.8, dash="4 3"))

    # Лінія підстильної поверхні (землі)
    parts.append(line(60, ground_y, 450, ground_y, color=LINE, sw=2.5))
    parts.append(text(70, ground_y + 22, "Підстильна поверхня (текстура ґрунту)", size=11, color=INK, anchor="start", bold=True))

    # Штрихування ґрунту
    for gx in range(70, 440, 20):
        parts.append(line(gx, ground_y, gx - 10, ground_y + 10, color=MUTED, sw=1.0))

    # Вектор лінійної швидкості Vx
    parts.append(arrow(cx - 20, cy - 32, cx + 45, cy - 32, color=FIELD, sw=2.2))
    parts.append(text(cx + 12, cy - 40, "Швидкість Vx", size=11, color=FIELD, bold=True))

    # Обертання ω (паразитний нахил)
    parts.append(text(cx - 120, cy - 8, "Хитання ω_y", size=10, color=POS, bold=True))
    parts.append('<path d="M 170 58 A 20 20 0 0 1 170 92" fill="none" stroke="%s" stroke-width="1.8"/>' % POS)
    parts.append(arrow(172, 90, 170, 94, color=POS, sw=1.8))

    # Права частина: велика пояснювальна картка з математикою деротації
    card_cx = 585
    t_lines = [
        "Математика оптичного потоку",
        "───────────────────────────",
        "1. Зсув пікселів у кадрі (Δu):",
        "   Δu = (Vx/h)·f·Δt + ω_y·f·Δt",
        "   де f — фокусна відстань сенсора,",
        "   h — поточна висота від ToF.",
        "",
        "2. Деротація (віднімання обертання):",
        "   Δu_чистий = Δu - ω_y · f · Δt",
        "",
        "3. Відновлена лінійна швидкість:",
        "   Vx = (Δu_чистий / f) · (h / Δt)",
        "",
        "Висновок: знаючи висоту h та",
        "кутову швидкість ω_y, потік дає",
        "чесну лінійну швидкість апарата."
    ]
    tb_math, _, _ = textbox(card_cx, 215, "\n".join(t_lines), size=10.5, fill="#f8fafc", stroke=LINE, sw=1.5, color=INK)
    parts.append(tb_math)

    render(os.path.join(IMG, "optical-flow-geometry.svg"), W, H, *parts,
           title="Геометрія вимірювання швидкості оптичним потоком та деротація")


# ── Фігура 3: замкнений контур EKF Sensor Fusion без GNSS ─────────────────────
def fig_ekf_fusion_loop():
    W, H = 760, 440
    parts = []

    # 1. Блок IMU (Predict) ліворуч зверху
    b1_x, b1_y = 135, 90
    tb1, _, _ = textbox(b1_x, b1_y, "IMU (200–500 Гц)\nАкселерометр + Гіроскоп\n(прискорення a, кут ω)",
                        size=10.5, fill="#fee2e2", stroke=POS, sw=1.8, color=POS, bold=True)
    parts.append(tb1)

    # 2. Блок EKF Predict (Центр зверху)
    b2_x, b2_y = 415, 90
    tb2, _, _ = textbox(b2_x, b2_y, "Крок передбачення (Predict)\nІнтегрування кінематики: x = f(x, a, ω)\nЕкстраполяція коваріації: P = F·P·Fᵀ + Q",
                        size=10.5, fill="#f3f4f6", stroke=LINE, sw=1.8, color=INK, bold=True)
    parts.append(tb2)

    # Стрілка від IMU до Predict
    parts.append(arrow(225, b1_y, 285, b1_y, color=POS, sw=2.0))
    parts.append(text(255, b1_y - 10, "dt ~ 2–5 мс", size=9.5, color=MUTED))

    # 3. Блок Вектора Стану праворуч
    b3_x, b3_y = 650, 90
    tb3, _, _ = textbox(b3_x, b3_y, "Оцінка стану x\n[px, py, pz] (позиція)\n[vx, vy, vz] (швидкість)\n[b_a] (зсув нуля)",
                        size=10, fill="#ecfdf5", stroke=FIELD, sw=1.8, color=FIELD, bold=True)
    parts.append(tb3)

    # Стрілка від Predict до Вектора Стану
    parts.append(arrow(545, b2_y, 580, b2_y, color=LINE, sw=2.0))

    # 4. Давачі корекції (Update) знизу
    u_y = 330
    tb_flow, _, _ = textbox(115, u_y, "Оптичний потік\n(PMW3901, 50–100 Гц)\nШвидкість Vx, Vy",
                            size=10, fill="#eff6ff", stroke=NEG, sw=1.5, color=NEG, bold=True)
    parts.append(tb_flow)

    tb_tof, _, _ = textbox(270, u_y, "Далекомір ToF / Baro\n(VL53L1X, 20–50 Гц)\nВисота Pz",
                           size=10, fill="#fef3c7", stroke="#d97706", sw=1.5, color="#d97706", bold=True)
    parts.append(tb_tof)

    tb_odo, _, _ = textbox(435, u_y, "Енкодери / ZUPT\n(Одометрія / зупинка)\nШвидкість V = 0",
                           size=10, fill="#f5f3ff", stroke="#7c3aed", sw=1.5, color="#7c3aed", bold=True)
    parts.append(tb_odo)

    # 5. Блок EKF Update (Центр знизу-справа)
    b4_x, b4_y = 635, 330
    tb4, _, _ = textbox(b4_x, b4_y, "Крок оновлення (Update)\nІнновація: y = z - h(x)\nКоефіцієнт: K = P·Hᵀ·S⁻¹\nКорекція: x = x + K·y",
                        size=10, fill="#f3f4f6", stroke=LINE, sw=1.8, color=INK, bold=True)
    parts.append(tb4)

    # Стрілки від сенсорів корекції до EKF Update
    parts.append(arrow(180, u_y, 210, u_y, color=NEG, sw=1.5))
    parts.append(arrow(335, u_y, 365, u_y, color="#d97706", sw=1.5))
    parts.append(arrow(510, u_y, 545, u_y, color=LINE, sw=1.5))

    # Зворотний зв'язок: від EKF Update вгору до Вектора стану
    parts.append(arrow(b4_x, b4_y - 45, b3_x, b3_y + 45, color=FIELD, sw=2.2))
    parts.append(text(b4_x + 35, 210, "Корекція стану та зсувів IMU", size=10, color=FIELD, bold=True, anchor="end"))

    # Пояснювальний підпис посередині
    tb_gate, _, _ = textbox(370, 215, "Інноваційний фільтр (Gate Testing)\nВідкидання хибних відблисків ToF та змазаних кадрів потоку",
                            size=10, fill="#ffffff", stroke=MUTED, sw=1.0, color=MUTED)
    parts.append(tb_gate)

    render(os.path.join(IMG, "ekf-fusion-loop.svg"), W, H, *parts,
           title="Контур розширеного фільтра Калмана (EKF Dead Reckoning)")


if __name__ == "__main__":
    fig_drift_comparison()
    fig_optical_flow_geometry()
    fig_ekf_fusion_loop()
    print("Фігури успішно згенеровано.")
