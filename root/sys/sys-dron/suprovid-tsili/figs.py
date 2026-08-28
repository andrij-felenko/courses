# -*- coding: utf-8 -*-
"""Фігури до статті «Супровід цілі: follow-me й утримання в кадрі» (sys-dron/suprovid-tsili).
Запуск: python figs.py  ->  ./img/*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Двоконтурна архітектура керування ──────────────────────────────────────
def fig_two_loop_tracking_architecture():
    W, H = 900, 550
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Двоконтурна архітектура візуального супроводу та Follow-Me", size=16, bold=True))

    # 1. Верхній блок: Оптичне сприйняття та трекер
    f.append(rect(30, 55, 840, 90, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(450, 75, "ПЕРЦЕПТИВНИЙ СТЕК (БОРТОВИЙ КОМП'ЮТЕР / COMPANION COMPUTER)", size=12, bold=True, color=INK))

    b_cam = fitbox(45, 88, 180, 45, "Оптична камера\n(MIPI-CSI / RTSP, 60 FPS)", size=10, fill="#ffffff", stroke=MUTED, sw=1.2)
    b_trk = fitbox(245, 88, 200, 45, "Візуальний трекер\n(SiamRPN / KCF / YOLO)", size=10, fill="#ffffff", stroke=NEG, sw=1.4)
    b_pin = fitbox(465, 88, 200, 45, "Пінхол-модель & геометрія\n(u, v, bbox -> кути, дальність)", size=10, fill="#ffffff", stroke=MUTED, sw=1.2)
    b_lrf = fitbox(685, 88, 170, 45, "Лазерний далекомір / IMU\n(дистанція, висота AGL)", size=10, fill="#ffffff", stroke=MUTED, sw=1.2)
    f.extend([b_cam, b_trk, b_pin, b_lrf])

    # Зв'язки у верхньому блоці
    f.append(arrow(225, 110, 245, 110, color=MUTED, sw=1.4))
    f.append(arrow(445, 110, 465, 110, color=MUTED, sw=1.4))

    # Стрілки вниз до контурів
    f.append(arrow(345, 133, 235, 175, color=NEG, sw=1.6))
    f.append(arrow(565, 133, 665, 175, color=FIELD, sw=1.6))
    f.append(arrow(770, 133, 730, 175, color=FIELD, sw=1.4))

    # 2. Лівий блок: Швидкий внутрішній контур підвісу (IBVS)
    f.append(rect(30, 175, 410, 260, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    f.append(text(235, 198, "ВНУТРІШНІЙ КОНТУР: ПІДВІС (IBVS, 50–100 Гц)", size=11, bold=True, color=NEG))

    b_err = fitbox(45, 215, 380, 44, "Кутові помилки відхилення від оптичної осі\ne_yaw = arctan(Δu / fx),  e_pitch = arctan(Δv / fy)", size=10, fill="#ffffff", stroke=NEG, sw=1.2)
    b_pid = fitbox(45, 270, 380, 48, "ПД-серворегулятор з гірокомпенсацією\nω_cmd = Kp·e + Kd·ė + ω_tgt_pred − ω_drone_gyro", size=10, fill="#ffffff", stroke=NEG, sw=1.4)
    b_gim = fitbox(45, 330, 380, 46, "Контролер підвісу (FOC / SimpleBGC / Mount)\nВекторне керування BLDC-моторами осей Roll/Pitch/Yaw", size=10, fill="#ffffff", stroke=NEG, sw=1.2)
    b_gact = fitbox(45, 388, 380, 36, "Триосьовий стабілізований підвіс (Gimbal)", size=10, fill="#ffffff", stroke=MUTED, sw=1.2)
    f.extend([b_err, b_pid, b_gim, b_gact])

    f.append(arrow(235, 259, 235, 270, color=NEG, sw=1.4))
    f.append(arrow(235, 318, 235, 330, color=NEG, sw=1.4))
    f.append(arrow(235, 376, 235, 388, color=NEG, sw=1.4))

    # 3. Правий блок: Зовнішній траєкторний контур (Follow-Me / Orbit)
    f.append(rect(460, 175, 410, 260, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(665, 198, "ЗОВНІШНІЙ КОНТУР: НАВІГАЦІЯ ДРОНА (10–20 Гц)", size=11, bold=True, color=FIELD))

    b_ekf = fitbox(475, 215, 380, 44, "Фільтр Калмана оцінки стану цілі (CV/CA)\nВектор стану: позиція (x, y, z), швидкість (vx, vy, vz)", size=10, fill="#ffffff", stroke=FIELD, sw=1.2)
    b_traj = fitbox(475, 270, 380, 48, "Генератор траєкторії Follow-Me / Orbit\nРозрахунок уставки позиції P_sp, швидкості V_sp та курсу Yaw_sp", size=10, fill="#ffffff", stroke=FIELD, sw=1.4)
    b_fc = fitbox(475, 330, 380, 46, "Польотний контролер (PX4 / ArduPilot)\nКаскадні ПІД-контури швидкості, положення та орієнтації", size=10, fill="#ffffff", stroke=FIELD, sw=1.2)
    b_act = fitbox(475, 388, 380, 36, "Силова установка (ESC, мотори, пропелери)", size=10, fill="#ffffff", stroke=MUTED, sw=1.2)
    f.extend([b_ekf, b_traj, b_fc, b_act])

    f.append(arrow(665, 259, 665, 270, color=FIELD, sw=1.4))
    f.append(arrow(665, 318, 665, 330, color=FIELD, sw=1.4))
    f.append(arrow(665, 376, 665, 388, color=FIELD, sw=1.4))

    # Зв'язок між фільтром Калмана та ПД-підвісу
    f.append(arrow(475, 240, 425, 290, color=NEG, sw=1.4))
    f.append(text(450, 260, "ω_tgt", size=10, bold=True, color=NEG))

    # 4. Нижній блок: MAVLink міст
    f.append(rect(30, 455, 840, 75, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    f.append(text(450, 474, "ПРОТОКОЛЬНИЙ ІНТЕРФЕЙС MAVLINK (UART 921600 / UDP 14550)", size=11, bold=True, color=LINE))
    b_m1 = fitbox(45, 485, 380, 34, "MAV_CMD_DO_MOUNT_CONTROL / GIMBAL_MANAGER", size=9, fill="#f8fafc", stroke=NEG, sw=1.0)
    b_m2 = fitbox(475, 485, 380, 34, "SET_POSITION_TARGET_LOCAL_NED / TARGET_RELATIVE", size=9, fill="#f8fafc", stroke=FIELD, sw=1.0)
    f.extend([b_m1, b_m2])

    render(os.path.join(IMG, "two-loop-tracking-architecture.svg"), W, H, *f)


# ── 2. Часова діаграма та оклюзія ───────────────────────────────────────────
def fig_tracking_timing_occlusion_timeline():
    W, H = 920, 520
    f = []

    # Заголовок
    f.append(text(W / 2, 26, "Часова діаграма обробки кадрів, затримок та екстраполяції при оклюзії", size=15, bold=True))

    # 1. Часова вісь зверху
    f.append(line(80, 60, 850, 60, color=LINE, sw=1.8))
    f.append(arrow(840, 60, 860, 60, color=LINE, sw=1.8))
    f.append(text(880, 64, "Час t", size=11, bold=True, color=LINE))

    # Фази часу
    f.append(rect(80, 75, 240, 375, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(200, 95, "ФАЗА 1: НОРМАЛЬНИЙ ТРЕКІНГ", size=10, bold=True, color=FIELD))

    f.append(rect(340, 75, 270, 375, fill="#fef2f2", stroke=POS, sw=1.4, rx=4))
    f.append(text(475, 95, "ФАЗА 2: ОКЛЮЗІЯ ЦІЛІ (0.5–2.0 с)", size=10, bold=True, color=POS))

    f.append(rect(630, 75, 240, 375, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    f.append(text(750, 95, "ФАЗА 3: ПОВТОРНЕ ЗАХОПЛЕННЯ", size=10, bold=True, color=NEG))

    # 2. Рядок 1: Відеопотік і кадри
    f.append(text(70, 135, "Відео\nкадри", size=9, bold=True, anchor="end"))
    for i, x in enumerate([90, 145, 200, 255]):
        f.append(fitbox(x, 120, 48, 28, "t%d" % i, size=9, fill="#ffffff", stroke=FIELD, sw=1.0))
    for i, x in enumerate([355, 415, 475, 535]):
        f.append(fitbox(x, 120, 54, 28, "t%d (блок)" % (i+4), size=8, fill="#ffffff", stroke=POS, sw=1.0))
    for i, x in enumerate([645, 700, 755, 810]):
        f.append(fitbox(x, 120, 50, 28, "t%d (знай)" % (i+8), size=8, fill="#ffffff", stroke=NEG, sw=1.0))

    # 3. Рядок 2: Затримка нейромережі / детектора (Latency Pipeline)
    f.append(text(70, 195, "Детекція\nі трекер", size=9, bold=True, anchor="end"))
    f.append(fitbox(90, 175, 220, 42, "Детекція успішна (conf > 0.85)\nОбчислювальний лаг Δt = 35 мс", size=9, fill="#ffffff", stroke=FIELD, sw=1.2))
    f.append(fitbox(350, 175, 250, 42, "Втрата детекції (оклюзія)\nТрекер повідомляє: TRACK_LOST", size=9, fill="#ffffff", stroke=POS, sw=1.4))
    f.append(fitbox(640, 175, 220, 42, "Повторне виявлення в зоні очікування\nRe-identification (conf > 0.80)", size=9, fill="#ffffff", stroke=NEG, sw=1.2))

    # 4. Рядок 3: Фільтр Калмана (Оцінка стану та коваріація P)
    f.append(text(70, 262, "Фільтр\nКалмана", size=9, bold=True, anchor="end"))
    f.append(fitbox(90, 235, 220, 52, "Режим корекції (Predict + Update)\nКоваріація P мінімальна (σ ≈ 0.3 м)\nОцінка швидкості V_target стійка", size=9, fill="#ffffff", stroke=FIELD, sw=1.2))
    f.append(fitbox(350, 235, 250, 52, "Режим екстраполяції (Dead-Reckoning)\nТільки Predict: X[k+1] = F·X[k]\nКоваріація P зростає: σ -> 2.5 м", size=9, fill="#ffffff", stroke=POS, sw=1.4))
    f.append(fitbox(640, 235, 220, 52, "Корекція за новим вимірюванням\nСтрибок нев'язки (Innovation)\nШвидка збіжність за 2–3 кроки", size=9, fill="#ffffff", stroke=NEG, sw=1.2))

    # 5. Рядок 4: Дії підвісу та автопілота
    f.append(text(70, 330, "Керування\nпідвісом", size=9, bold=True, anchor="end"))
    f.append(fitbox(90, 305, 220, 48, "Плавне утримання в центрі кадру\nПомилка Δu, Δv ≈ 0 пікселів", size=9, fill="#ffffff", stroke=FIELD, sw=1.2))
    f.append(fitbox(350, 305, 250, 48, "Рух за екстрапольованим вектором\nПошукове сканування навколо прогнозу", size=9, fill="#ffffff", stroke=POS, sw=1.4))
    f.append(fitbox(640, 305, 220, 48, "Компенсація стрибка позиції\nПлавне повернення цілі в центр кадру", size=9, fill="#ffffff", stroke=NEG, sw=1.2))

    # 6. Рядок 5: Траєкторія дрона
    f.append(text(70, 395, "Траєкторія\nдрона", size=9, bold=True, anchor="end"))
    f.append(fitbox(90, 370, 220, 46, "Слідування на заданій дистанції D_set\nКурс узгоджено з вектором руху цілі", size=9, fill="#ffffff", stroke=FIELD, sw=1.2))
    f.append(fitbox(350, 370, 250, 46, "Збереження швидкості та напрямку польоту\nЗапобігання різкому гальмуванню дрона", size=9, fill="#ffffff", stroke=POS, sw=1.4))
    f.append(fitbox(640, 370, 220, 46, "Відновлення відносного позиціонування\nПідтримання безпечного ешелону висоти", size=9, fill="#ffffff", stroke=NEG, sw=1.2))

    # Нижній висновок
    f.append(rect(30, 465, 860, 35, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    f.append(text(460, 487, "Фільтр Калмана забезпечує нерозривність контуру керування: підвіс і дрон не втрачають орієнтації під час короткочасних завад.", size=10, color=INK))

    render(os.path.join(IMG, "tracking-timing-occlusion-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_loop_tracking_architecture()
    fig_tracking_timing_occlusion_timeline()
    print("Фігури успішно скомпільовано в img/")
