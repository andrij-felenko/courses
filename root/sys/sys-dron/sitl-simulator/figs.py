# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра під стиль курсу
AMBER   = "#c28200"
AMBERBG = "#fef8e7"
AMBERTXT= "#855800"
BLUEBG  = "#eff5ff"
GREENBG = "#eaf8ed"
REDBG   = "#fdeeed"
GRAYBG  = "#f4f6f8"


def fig_sitl_pipeline():
    W, H = 860, 440
    p = []
    
    # Загальний контейнер Host PC
    p.append(rect(20, 20, 820, 395, fill=GRAYBG, stroke=MUTED, sw=1.5, rx=12))
    p.append(text(40, 45, "Хостовий комп'ютер x86 / Linux (робоча станція або CI-сервер)", size=13, color=MUTED, anchor="start", bold=True))

    # Лівий блок: Процес автопілота
    fw_x, fw_y, fw_w, fw_h = 45, 65, 340, 260
    p.append(rect(fw_x, fw_y, fw_w, fw_h, fill=GREENBG, stroke=FIELD, sw=2, rx=10))
    p.append(text(fw_x + fw_w / 2, fw_y + 28, "ПРОЦЕС АВТОПІЛОТА (SITL)", size=13, color=FIELD, bold=True))
    p.append(text(fw_x + fw_w / 2, fw_y + 48, "Незмінний польотний код C++ (ArduPilot / PX4)", size=10, color=INK))
    
    # Шари всередині автопілота
    p.append(rect(fw_x + 15, fw_y + 65, fw_w - 30, 42, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(fw_x + fw_w / 2, fw_y + 83, "Навігація, фільтр EKF, автомати місій", size=10, color=INK, bold=True))
    p.append(text(fw_x + fw_w / 2, fw_y + 98, "Контури кутового положення і позиції (PID)", size=9, color=MUTED))

    p.append(rect(fw_x + 15, fw_y + 115, fw_w - 30, 42, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(fw_x + fw_w / 2, fw_y + 133, "Мікшер та розподіл тяги (Allocation)", size=10, color=INK, bold=True))
    p.append(text(fw_x + fw_w / 2, fw_y + 148, "Розрахунок обертів гвинтів та кутів сервоприводів", size=9, color=MUTED))

    p.append(rect(fw_x + 15, fw_y + 165, fw_w - 30, 80, fill=AMBERBG, stroke=AMBER, sw=1.4, rx=6))
    p.append(text(fw_x + fw_w / 2, fw_y + 185, "Апаратна абстракція: HAL_SITL", size=11, color=AMBERTXT, bold=True))
    p.append(text(fw_x + fw_w / 2, fw_y + 203, "Віртуальні шини: SPI, I2C, UART замінено на сокети", size=9.5, color=INK))
    p.append(text(fw_x + fw_w / 2, fw_y + 220, "Синхронізація монотонного часу (Lockstep Clock)", size=9.5, color=AMBERTXT))

    # Правий блок: Симулятор фізики
    sim_x, sim_y, sim_w, sim_h = 475, 65, 340, 260
    p.append(rect(sim_x, sim_y, sim_w, sim_h, fill=BLUEBG, stroke=NEG, sw=2, rx=10))
    p.append(text(sim_x + sim_w / 2, sim_y + 28, "СИМУЛЯТОР ФІЗИКИ (FDM)", size=13, color=NEG, bold=True))
    p.append(text(sim_x + sim_w / 2, sim_y + 48, "JSBSim / Gazebo / AirSim / Власний FDM-міст", size=10, color=INK))

    # Шари всередині симулятора
    p.append(rect(sim_x + 15, sim_y + 65, sim_w - 30, 55, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(sim_x + sim_w / 2, sim_y + 85, "Динаміка твердого тіла (6 DOF)", size=10.5, color=INK, bold=True))
    p.append(text(sim_x + sim_w / 2, sim_y + 102, "Рівняння Ньютона-Ейлера, тяга гвинтів, вітер, гравітація", size=9, color=MUTED))

    p.append(rect(sim_x + 15, sim_y + 128, sim_w - 30, 55, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(sim_x + sim_w / 2, sim_y + 148, "Синтез сигналів сенсорів", size=10.5, color=INK, bold=True))
    p.append(text(sim_x + sim_w / 2, sim_y + 165, "Істинний стан + гаусів шум + дрейф зміщення Гаусса-Маркова", size=9, color=MUTED))

    p.append(rect(sim_x + 15, sim_y + 191, sim_w - 30, 54, fill=AMBERBG, stroke=AMBER, sw=1.2, rx=6))
    p.append(text(sim_x + sim_w / 2, sim_y + 211, "Мережевий міст (IPC / UDP-сокет)", size=10.5, color=AMBERTXT, bold=True))
    p.append(text(sim_x + sim_w / 2, sim_y + 228, "JSON / HIL_SENSOR / Protobuf протокол lockstep", size=9, color=INK))

    # Стрілки між Автопілотом та Симулятором
    # 1. Тяга моторів -> FDM
    p.append(arrow(fw_x + fw_w, fw_y + 185, sim_x, sim_y + 185, color=POS, sw=2.2))
    p.append(rect(390, fw_y + 168, 80, 20, fill=REDBG, stroke=POS, sw=1, rx=4))
    p.append(text(430, fw_y + 182, "ШІМ / Тяга", size=9, color=POS, bold=True))

    # 2. Сенсори -> Автопілот
    p.append(arrow(sim_x, sim_y + 225, fw_x + fw_w, fw_y + 225, color=NEG, sw=2.2))
    p.append(rect(390, sim_y + 208, 80, 20, fill=BLUEBG, stroke=NEG, sw=1, rx=4))
    p.append(text(430, sim_y + 222, "Дані сенсорів", size=9, color=NEG, bold=True))

    # Зовнішні з'єднання MAVLink (вниз)
    p.append(arrow(fw_x + 80, fw_y + fw_h, fw_x + 80, 360, color=FIELD, sw=2))
    p.append(rect(45, 360, 240, 42, fill=BG, stroke=FIELD, sw=1.4, rx=6))
    p.append(text(165, 377, "Наземна станція (GCS)", size=10.5, color=FIELD, bold=True))
    p.append(text(165, 393, "QGroundControl / UDP 14550", size=9, color=MUTED))

    p.append(arrow(fw_x + fw_w - 80, fw_y + fw_h, fw_x + fw_w - 80, 360, color=INK, sw=2))
    p.append(rect(195 + 110, 360, 240, 42, fill=BG, stroke=LINE, sw=1.4, rx=6))
    p.append(text(425, 377, "Зовнішній супутній комп'ютер", size=10.5, color=INK, bold=True))
    p.append(text(425, 393, "MAVSDK / ROS2 / UDP 14540", size=9, color=MUTED))

    # Візуалізація симулятора (3D сцена)
    p.append(arrow(sim_x + sim_w / 2, sim_y + sim_h, sim_x + sim_w / 2, 360, color=NEG, sw=2))
    p.append(rect(585, 360, 220, 42, fill=BG, stroke=NEG, sw=1.4, rx=6))
    p.append(text(695, 377, "3D-візуалізація світу", size=10.5, color=NEG, bold=True))
    p.append(text(695, 393, "Рендеринг мешів, камер, лідарів", size=9, color=MUTED))

    render(os.path.join(OUT, "sitl-architecture-pipeline.svg"), W, H, *p,
           title="Архітектура симуляції SITL: замкнений контур автопілота й фізичного рушія")


def fig_lockstep_cycle():
    W, H = 860, 420
    p = []

    # Тло діаграми
    p.append(rect(20, 20, 820, 380, fill=BG, stroke=LINE, sw=1.2, rx=10))
    p.append(text(W / 2, 45, "Синхронізація часу Lockstep (узгоджений крок) проти вільного ходу", size=13, color=INK, bold=True))

    # Ліва колонка: Симулятор фізики FDM
    col1_x = 180
    p.append(rect(col1_x - 110, 70, 220, 38, fill=BLUEBG, stroke=NEG, sw=1.6, rx=6))
    p.append(text(col1_x, 94, "Симулятор фізики (FDM)", size=11.5, color=NEG, bold=True))

    # Права колонка: Польотний стек автопілота
    col2_x = 680
    p.append(rect(col2_x - 110, 70, 220, 38, fill=GREENBG, stroke=FIELD, sw=1.6, rx=6))
    p.append(text(col2_x, 94, "Автопілот (ArduPilot / PX4)", size=11.5, color=FIELD, bold=True))

    # Вертикальні лінії життя
    p.append(line(col1_x, 115, col1_x, 375, color=MUTED, sw=1.5, dash="4 4"))
    p.append(line(col2_x, 115, col2_x, 375, color=MUTED, sw=1.5, dash="4 4"))

    # Крок 1: FDM генерує сенсори на час t0
    p.append(rect(col1_x - 12, 130, 24, 40, fill=BLUEBG, stroke=NEG, sw=1.2))
    p.append(arrow(col1_x + 12, 145, col2_x - 12, 165, color=NEG, sw=2))
    p.append(text(430, 145, "1. Пакет сенсорів [ t = t₀, IMU, Baro, GPS ]", size=10, color=NEG, bold=True))

    # FDM стає на паузу
    p.append(rect(col1_x - 65, 178, 130, 75, fill=AMBERBG, stroke=AMBER, sw=1.2, rx=4))
    p.append(text(col1_x, 198, "ПАУЗА ЧАСУ", size=10, color=AMBERTXT, bold=True))
    p.append(text(col1_x, 216, "Фізика зупинена,", size=9, color=INK))
    p.append(text(col1_x, 234, "очікування команд u(t₀)", size=9, color=INK))

    # Крок 2: Автопілот обробляє дані
    p.append(rect(col2_x - 12, 165, 24, 60, fill=GREENBG, stroke=FIELD, sw=1.2))
    p.append(text(col2_x + 25, 185, "Оновлення годинника автопілота: t_sim = t₀", size=9, color=INK, anchor="start"))
    p.append(text(col2_x + 25, 203, "Такт фільтрації EKF та обчислення PID", size=9, color=INK, anchor="start"))
    p.append(text(col2_x + 25, 221, "Розрахунок вихідних сигналів мікшера", size=9, color=INK, anchor="start"))

    # Крок 3: Автопілот надсилає актуатори назад
    p.append(arrow(col2_x - 12, 225, col1_x + 12, 255, color=POS, sw=2))
    p.append(text(430, 235, "2. Команди актуаторів [ u(t₀) = {PWM₁, PWM₂, ...} ]", size=10, color=POS, bold=True))

    # Крок 4: FDM просуває фізику на dt
    p.append(rect(col1_x - 12, 255, 24, 65, fill=BLUEBG, stroke=NEG, sw=1.2))
    p.append(text(col1_x - 25, 275, "Інтегрування 6 DOF на крок Δt", size=9, color=INK, anchor="end"))
    p.append(text(col1_x - 25, 293, "Новий час: t₁ = t₀ + Δt", size=9, color=AMBERTXT, anchor="end", bold=True))
    p.append(text(col1_x - 25, 311, "Генерація шуму нових сенсорів", size=9, color=INK, anchor="end"))

    # Крок 5: Новий цикл
    p.append(arrow(col1_x + 12, 320, col2_x - 12, 340, color=NEG, sw=2))
    p.append(text(430, 320, "3. Пакет сенсорів [ t = t₁ = t₀ + Δt ]", size=10, color=NEG, bold=True))

    # Висновок знизу
    p.append(rect(40, 368, 780, 24, fill=GRAYBG, stroke=MUTED, sw=1, rx=4))
    p.append(text(W / 2, 384, "Повна детермінованість: навантаження процесора змінює реальну швидкість, але не математичний результат польоту", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "lockstep-sync-cycle.svg"), W, H, *p,
           title="Покрокова синхронізація lockstep: гарантія точного відтворення польоту")


def fig_fdm_frames():
    W, H = 860, 400
    p = []

    p.append(rect(20, 20, 820, 360, fill=BG, stroke=LINE, sw=1.2, rx=10))
    p.append(text(W / 2, 45, "Системи координат і динаміка 6 DOF: перетворення сил і моментів", size=13, color=INK, bold=True))

    # Лівий блок: Навігаційна система NED
    p.append(rect(40, 70, 360, 285, fill=GRAYBG, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(220, 95, "Навігаційна система NED (Earth Frame)", size=11.5, color=INK, bold=True))
    p.append(text(220, 113, "Нерухома система відліку відносно точки старту", size=9.5, color=MUTED))

    # Осі NED
    p.append(arrow(120, 180, 220, 180, color=POS, sw=2))
    p.append(text(230, 184, "X (Північ, North)", size=10, color=POS, anchor="start", bold=True))

    p.append(arrow(120, 180, 120, 260, color=FIELD, sw=2))
    p.append(text(120, 276, "Z (Вниз до центру Землі, Down)", size=10, color=FIELD, bold=True))

    p.append(arrow(120, 180, 60, 220, color=NEG, sw=2))
    p.append(text(50, 235, "Y (Схід, East)", size=10, color=NEG, anchor="end", bold=True))

    p.append(rect(60, 290, 320, 50, fill=BG, stroke=MUTED, sw=1, rx=4))
    p.append(text(220, 308, "Гравітаційне прискорення: g_ned = [0, 0, +9.81] м/с²", size=9.5, color=INK))
    p.append(text(220, 326, "Траєкторія: r_ned = [x, y, z], швидкість: v_ned = [u, v, w]", size=9.5, color=MUTED))

    # Центральний міст: Орієнтація через кватерніон
    p.append(arrow(405, 180, 455, 180, color=AMBER, sw=2.5))
    p.append(arrow(455, 230, 405, 230, color=AMBER, sw=2.5))
    p.append(rect(390, 192, 80, 26, fill=AMBERBG, stroke=AMBER, sw=1.2, rx=4))
    p.append(text(430, 209, "q (Кватерніон)", size=9.5, color=AMBERTXT, bold=True))

    # Правий блок: Зв'язана система координат Body Frame
    p.append(rect(460, 70, 360, 285, fill=BLUEBG, stroke=NEG, sw=1.5, rx=8))
    p.append(text(640, 95, "Зв'язана система Body Frame (X-Fwd, Y-Right, Z-Down)", size=11, color=NEG, bold=True))
    p.append(text(640, 113, "Закріплена на центрі мас літального апарата", size=9.5, color=MUTED))

    # Осі Body
    p.append(arrow(580, 180, 680, 160, color=POS, sw=2))
    p.append(text(690, 160, "X_b (Ніс / Roll p)", size=10, color=POS, anchor="start", bold=True))

    p.append(arrow(580, 180, 660, 230, color=FIELD, sw=2))
    p.append(text(670, 238, "Y_b (Праве крило / Pitch q)", size=10, color=FIELD, anchor="start", bold=True))

    p.append(arrow(580, 180, 580, 260, color=NEG, sw=2))
    p.append(text(580, 276, "Z_b (Днище / Yaw r)", size=10, color=NEG, bold=True))

    p.append(rect(480, 290, 320, 50, fill=BG, stroke=NEG, sw=1, rx=4))
    p.append(text(640, 308, "Сили двигунів: F_thrust = [0, 0, -Σ T_i] (спрямована вгору)", size=9.5, color=POS, bold=True))
    p.append(text(640, 326, "Обертальні моменти: M_total = M_thrust + M_gyro + M_aero", size=9.5, color=INK))

    render(os.path.join(OUT, "fdm-coordinate-frames.svg"), W, H, *p,
           title="Перетворення координат між навігаційним базисом NED та зв'язаним базисом Body")


def fig_sensor_noise():
    W, H = 860, 380
    p = []

    p.append(rect(20, 20, 820, 340, fill=BG, stroke=LINE, sw=1.2, rx=10))
    p.append(text(W / 2, 45, "Синтез сигналів сенсорів: перетворення істинного стану в зашумлені виміри", size=13, color=INK, bold=True))

    # Вхід: Істинний стан
    p.append(rect(40, 75, 170, 260, fill=GREENBG, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(125, 100, "ІСТИННИЙ СТАН", size=12, color=FIELD, bold=True))
    p.append(text(125, 118, "Ground Truth FDM", size=9.5, color=MUTED))
    p.append(line(55, 130, 195, 130, color=FIELD, sw=1))

    p.append(text(60, 155, "• Положення: r_ned", size=10, color=INK, anchor="start"))
    p.append(text(60, 185, "• Швидкість: v_ned", size=10, color=INK, anchor="start"))
    p.append(text(60, 215, "• Прискорення: a_ned", size=10, color=INK, anchor="start"))
    p.append(text(60, 245, "• Кутова шв.: ω_body", size=10, color=INK, anchor="start"))
    p.append(text(60, 275, "• Орієнтація: q_nb", size=10, color=INK, anchor="start"))
    p.append(text(60, 305, "• Атмосфера: P(h), T(h)", size=10, color=INK, anchor="start"))

    # Центральний блок: Моделі шумів і похибок
    p.append(rect(250, 75, 360, 260, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=8))
    p.append(text(430, 100, "ШУМОВІ МОДЕЛІ ДАВАЧІВ", size=12, color=AMBERTXT, bold=True))
    p.append(text(430, 118, "Фізичні спотворення реального світу", size=9.5, color=MUTED))
    p.append(line(265, 130, 595, 130, color=AMBER, sw=1))

    # Сенсорні моделі
    p.append(rect(265, 140, 330, 38, fill=BG, stroke=AMBER, sw=1, rx=4))
    p.append(text(275, 157, "Акселерометр:", size=10, color=AMBERTXT, anchor="start", bold=True))
    p.append(text(370, 157, "a_meas = R(a - g) + bias + w_acc", size=9.5, color=INK, anchor="start"))
    p.append(text(275, 171, "Дрейф зміщення 1-го порядку Гаусса-Маркова", size=9.2, color=MUTED, anchor="start"))

    p.append(rect(265, 185, 330, 38, fill=BG, stroke=AMBER, sw=1, rx=4))
    p.append(text(275, 202, "Гіроскоп:", size=10, color=AMBERTXT, anchor="start", bold=True))
    p.append(text(340, 202, "ω_meas = ω + bias_gyro + w_gyro", size=9.5, color=INK, anchor="start"))
    p.append(text(275, 216, "Вібраційний шум від обертів двигунів", size=9.2, color=MUTED, anchor="start"))

    p.append(rect(265, 230, 330, 44, fill=BG, stroke=AMBER, sw=1, rx=4))
    p.append(text(275, 247, "Барометр / GNSS:", size=10, color=AMBERTXT, anchor="start", bold=True))
    p.append(text(390, 247, "P_baro = P₀ · (1 - L·h/T₀)^(gM/RL)", size=9.2, color=INK, anchor="start"))
    p.append(text(275, 265, "GNSS: затримка 200 мс, джиттер HDOP/VDOP, 5-10 Гц", size=9.2, color=MUTED, anchor="start"))

    p.append(rect(265, 280, 330, 44, fill=BG, stroke=AMBER, sw=1, rx=4))
    p.append(text(275, 297, "Магнітометр:", size=10, color=AMBERTXT, anchor="start", bold=True))
    p.append(text(370, 297, "B_meas = A_soft · R · B_earth + V_hard", size=9.2, color=INK, anchor="start"))
    p.append(text(275, 315, "Модель геомагнітного поля WMM + наведення струму", size=9.2, color=MUTED, anchor="start"))

    # Вихідний блок: Сирі пакети
    p.append(rect(650, 75, 170, 260, fill=BLUEBG, stroke=NEG, sw=1.8, rx=8))
    p.append(text(735, 100, "СИНТЕТИЧНІ ДАНІ", size=11.5, color=NEG, bold=True))
    p.append(text(735, 118, "Сирі виміри для HAL", size=9.5, color=MUTED))
    p.append(line(665, 130, 805, 130, color=NEG, sw=1))

    p.append(text(670, 160, "• IMU (1000 Гц)", size=10, color=INK, anchor="start", bold=True))
    p.append(text(670, 195, "• Baro (50-100 Гц)", size=10, color=INK, anchor="start", bold=True))
    p.append(text(670, 235, "• Mag (50-100 Гц)", size=10, color=INK, anchor="start", bold=True))
    p.append(text(670, 275, "• GNSS (5-10 Гц)", size=10, color=INK, anchor="start", bold=True))
    p.append(text(670, 310, "• Квантування АЦП", size=9.5, color=MUTED, anchor="start"))

    # Стрілки передачі
    p.append(arrow(210, 205, 250, 205, color=FIELD, sw=2.5))
    p.append(arrow(610, 205, 650, 205, color=AMBER, sw=2.5))

    render(os.path.join(OUT, "sensor-noise-models.svg"), W, H, *p,
           title="Генерація шумів сенсорів: моделювання похибок акселерометра, гіроскопа, барометра та GNSS")


def fig_hitl_loop():
    W, H = 860, 420
    p = []

    p.append(rect(20, 20, 820, 380, fill=BG, stroke=LINE, sw=1.2, rx=10))
    p.append(text(W / 2, 45, "Апаратне моделювання в контурі (Hardware-In-The-Loop — HITL)", size=13, color=INK, bold=True))

    # Лівий бік: Робоча станція симуляції
    pc_x, pc_y, pc_w, pc_h = 40, 75, 340, 270
    p.append(rect(pc_x, pc_y, pc_w, pc_h, fill=BLUEBG, stroke=NEG, sw=2, rx=10))
    p.append(text(pc_x + pc_w / 2, pc_y + 28, "ХОСТОВИЙ ПК (СИМУЛЯТОР ФІЗИКИ)", size=12, color=NEG, bold=True))
    p.append(text(pc_x + pc_w / 2, pc_y + 48, "JSBSim / Gazebo / X-Plane у реальному часі", size=9.5, color=INK))

    p.append(rect(pc_x + 15, pc_y + 65, pc_w - 30, 60, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(pc_x + pc_w / 2, pc_y + 88, "Математична модель 6 DOF", size=10.5, color=INK, bold=True))
    p.append(text(pc_x + pc_w / 2, pc_y + 106, "Розрахунок динаміки середовища й аеродинаміки", size=9.2, color=MUTED))

    p.append(rect(pc_x + 15, pc_y + 135, pc_w - 30, 55, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(pc_x + pc_w / 2, pc_y + 157, "Генератор сирих пакетів сенсорів", size=10.5, color=INK, bold=True))
    p.append(text(pc_x + pc_w / 2, pc_y + 174, "Формування повідомлень HIL_SENSOR / MAVLink", size=9.2, color=MUTED))

    p.append(rect(pc_x + 15, pc_y + 200, pc_w - 30, 55, fill=AMBERBG, stroke=AMBER, sw=1.2, rx=6))
    p.append(text(pc_x + pc_w / 2, pc_y + 222, "Апаратний міст USB-UART / CAN", size=10.5, color=AMBERTXT, bold=True))
    p.append(text(pc_x + pc_w / 2, pc_y + 240, "FTDI 3–12 Мбіт/с або CAN-адаптер", size=9.2, color=INK))

    # Правий бік: Справжній польотний контролер
    mcu_x, mcu_y, mcu_w, mcu_h = 480, 75, 340, 270
    p.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill=GREENBG, stroke=FIELD, sw=2, rx=10))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 28, "ФІЗИЧНИЙ ПОЛЬОТНИЙ КОНТРОЛЕР", size=12, color=FIELD, bold=True))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 48, "Реальна плата: STM32H7 / RTOS NuttX / ChibiOS", size=9.5, color=INK))

    p.append(rect(mcu_x + 15, mcu_y + 65, mcu_w - 30, 55, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 87, "HIL-драйвери замість фізичних давачів", size=10.5, color=INK, bold=True))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 104, "Прийом пакетів через UART/USB DMA-буфери", size=9.2, color=MUTED))

    p.append(rect(mcu_x + 15, mcu_y + 130, mcu_w - 30, 60, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 152, "Реальний процесор і пам'ять MCU", size=10.5, color=INK, bold=True))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 170, "Перевірка таймінгів, переривань, завантаження CPU", size=9.2, color=MUTED))

    p.append(rect(mcu_x + 15, mcu_y + 200, mcu_w - 30, 55, fill=REDBG, stroke=POS, sw=1.2, rx=6))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 222, "Вихідні таймери ШІМ / DShot", size=10.5, color=POS, bold=True))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 240, "Апаратне формування сигналів керування моторами", size=9.2, color=INK))

    # Фізичний кабель між ними
    p.append(arrow(pc_x + pc_w, pc_y + 160, mcu_x, mcu_y + 160, color=NEG, sw=2.5))
    p.append(rect(385, pc_y + 145, 90, 26, fill=BLUEBG, stroke=NEG, sw=1.2, rx=4))
    p.append(text(430, pc_y + 162, "Сенсори (UART)", size=9.5, color=NEG, bold=True))

    p.append(arrow(mcu_x, mcu_y + 225, pc_x + pc_w, pc_y + 225, color=POS, sw=2.5))
    p.append(rect(385, mcu_y + 210, 90, 26, fill=REDBG, stroke=POS, sw=1.2, rx=4))
    p.append(text(430, mcu_y + 227, "Команди ШІМ", size=9.5, color=POS, bold=True))

    # Підсумок знизу
    p.append(rect(40, 365, 780, 26, fill=GRAYBG, stroke=MUTED, sw=1, rx=4))
    p.append(text(W / 2, 382, "HITL виявляє апаратні вузькі місця: переповнення стека, переривання DMA, затримки шини та реальні таймінги ОС", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "hitl-hardware-loop.svg"), W, H, *p,
           title="Стенд апаратного моделювання в контурі (HITL): фізичний контролер у віртуальному середовищі")


if __name__ == "__main__":
    fig_sitl_pipeline()
    fig_lockstep_cycle()
    fig_fdm_frames()
    fig_sensor_noise()
    fig_hitl_loop()
    print("Всі фігури згенеровано успішно!")
