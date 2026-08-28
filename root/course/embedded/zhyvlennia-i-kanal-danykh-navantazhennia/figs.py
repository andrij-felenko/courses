# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми «Живлення й канал даних навантаження»."""

import os
import sys

# Підключаємо svgkit з кореневої теки scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_power_filtering_topology():
    """1. Топологія живлення навантаження: батарейна шина, захист, LC π-фільтр, BEC та LDO."""
    W, H = 940, 480
    f = []
    
    # Заголовок блоків
    f.append(fitbox(20, 20, 260, 40, "Силова шина батареї (4S–12S)\nКомутаційний шум ESC", size=13, bold=True, fill="#fdecea", stroke=POS))
    f.append(fitbox(310, 20, 320, 40, "Каскад захисту та фільтрації\nTVS + Демпфований π-фільтр + CMC", size=13, bold=True, fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(660, 20, 260, 40, "Стабілізація та навантаження\nDedicated BEC + LDO + Сенсор", size=13, bold=True, fill="#eafaf1", stroke=FIELD))
    
    # ── Блок 1: Силове джерело та завади ESC
    f.append(rect(20, 80, 260, 360, fill="#fffaf9", stroke=POS, sw=1.5))
    f.append(textbox(150, 110, "LiPo Батарея 14.8–50.4 В\n(Низький внутрішній опір R_int)", size=12, bold=True, fill="#ffffff", stroke=POS)[0])
    
    f.append(fitbox(35, 160, 230, 80, "Комутація MOSFET ESC:\n• dI/dt > 100 А/мкс при 24–48 кГц\n• Індуктивні голки: ΔV = L·(dI/dt)\n• Амплітуда сплесків до 60–80 В", size=11, fill="#fdecea", stroke=POS))
    
    f.append(fitbox(35, 260, 230, 80, "Паразитна індуктивність джгутів:\n• L_wire ≈ 1 нГн/мм (~200 нГн)\n• Спільний імпеданс шини\n• Зворотна ЕРС моторів", size=11, fill="#fbf2ef", stroke=LINE))
    
    f.append(textbox(150, 380, "Пульсації на шині: 1–3 В p-p\nВисокочастотний дзвін >10 МГц", size=11, bold=True, color=POS, fill="#ffffff", stroke=POS)[0])

    # Стрілка 1 -> 2
    f.append(arrow(280, 220, 310, 220, color=POS, sw=2))

    # ── Блок 2: Фільтрація
    f.append(rect(310, 80, 320, 360, fill="#f6f9fe", stroke=NEG, sw=1.5))
    
    f.append(fitbox(325, 100, 290, 65, "1. Захист від перенапруги (TVS):\n• Діод SMBJ33A / SMAJ40CA\n• Зрізання гострих викидів > 33–40 В", size=11, fill="#ffffff", stroke=NEG))
    
    f.append(fitbox(325, 180, 290, 85, "2. Демпфований LC π-фільтр:\n• C_in: 2×10 мкФ X7R (кераміка)\n• L_choke: 10–22 мкГн (низький DCR)\n• R_damp + C_damp (гасіння резонансу)\n• f_c = 1 / (2π√(LC)) ≈ 2–5 кГц", size=11, fill="#ffffff", stroke=NEG))

    f.append(fitbox(325, 280, 290, 75, "3. Синфазний дросель (CMC):\n• Придушення синфазних завад\n• Захист вимірювальних трактів\n• C_bulk: Полімер 220 мкФ Low-ESR", size=11, fill="#ffffff", stroke=NEG))

    f.append(textbox(470, 395, "Придушення шуму ESC: > 45 дБ\nАмплітуда залишку: < 20 мВ", size=11, bold=True, color=NEG, fill="#ffffff", stroke=NEG)[0])

    # Стрілка 2 -> 3
    f.append(arrow(630, 220, 660, 220, color=FIELD, sw=2))

    # ── Блок 3: Регуляція та навантаження
    f.append(rect(660, 80, 260, 360, fill="#f4fbf7", stroke=FIELD, sw=1.5))
    
    f.append(fitbox(675, 100, 230, 70, "Dedicated Buck BEC (12V / 5A):\n• Синхронне випрямлення\n• Живлення моторів підвісу\n• ККД > 92%, високий запас", size=11, fill="#ffffff", stroke=FIELD))
    
    f.append(fitbox(675, 185, 230, 70, "Ultra-Low-Noise LDO (5V / 3.3V):\n• PSRR > 65 дБ на 100 кГц\n• Живлення матриці камери й АЦП\n• Залишковий шум < 5 мкВ RMS", size=11, fill="#ffffff", stroke=FIELD))

    f.append(fitbox(675, 270, 230, 90, "Корисне навантаження:\n• Камера 4K / Тепловізор\n• 3-осьовий підвіс (Gimbal)\n• LiDAR / Бортовий комп'ютер\n• Чисте зображення без смуг", size=11, fill="#ffffff", stroke=FIELD))

    f.append(textbox(790, 395, "Чиста шина: Ripple < 3 мВ\nВідсутність артефактів смуг", size=11, bold=True, color=FIELD, fill="#ffffff", stroke=FIELD)[0])

    render(os.path.join(IMG, "power-filtering-topology.svg"), W, H, *f)


def fig_ground_loop_isolation():
    """2. Земляні петлі від струму ESC та гальванічна розв'язка."""
    W, H = 940, 440
    f = []
    
    # ── Ліва колонка: Неізольована система та земляна петля
    f.append(rect(20, 20, 435, 400, fill="#fffaf9", stroke=POS, sw=1.5))
    f.append(textbox(237, 45, "Неізольована схема: Земляна петля (Ground Loop)", size=13, bold=True, color=POS, fill="#ffffff", stroke=POS)[0])
    
    f.append(fitbox(35, 75, 180, 60, "Батарея & ESC\nСтрум мотора:\nI_ESC = 40–100 А", size=11, bold=True, fill="#fdecea", stroke=POS))
    f.append(fitbox(260, 75, 180, 60, "Польотний контролер (FC)\nСигнал UART 3.3V LVCMOS\nV_IL(max) = 0.8 В", size=11, bold=True, fill="#f4f6f8", stroke=LINE))
    
    f.append(fitbox(35, 175, 180, 70, "Опір силової землі:\nR_gnd = 10–15 мОм\nПадіння напруги:\nΔV = I_ESC · R_gnd = 0.6–1.2 В", size=11, fill="#ffffff", stroke=POS))
    f.append(fitbox(260, 175, 180, 70, "Камера / Сенсор\nЗемля зміщена на +ΔV\nПомилки розпізнавання бітів\nЗрив синхронізації UART", size=11, fill="#ffffff", stroke=POS))

    # Стрілки циркуляції петлі
    f.append(arrow(125, 135, 125, 175, color=POS, sw=2))
    f.append(arrow(350, 135, 350, 175, color=POS, sw=2))
    f.append(line(215, 210, 260, 210, color=POS, sw=2, dash="4,3"))
    f.append(arrow(260, 105, 215, 105, color=POS, sw=2))
    f.append(text(237, 125, "Зрівнювальний струм через екран", size=10, color=POS, bold=True))

    f.append(fitbox(35, 275, 405, 125, "Наслідки для апарата:\n• Силовий струм мотора затікає в сигнальний екран UART/USB\n• Зсув опорного рівня землі сенсора перевищує поріг логічного нуля (0.8 В)\n• Поява шумів на АЦП, збої передачі MAVLink, нагрів сигнальних проводів\n• Небезпека вигорання вхідних каскадів мікроконтролера", size=11, fill="#fdecea", stroke=POS))

    # ── Права колонка: Гальванічна розв'язка
    f.append(rect(485, 20, 435, 400, fill="#f4fbf7", stroke=FIELD, sw=1.5))
    f.append(textbox(702, 45, "Гальванічна розв'язка: Повний захист від петель", size=13, bold=True, color=FIELD, fill="#ffffff", stroke=FIELD)[0])

    f.append(fitbox(500, 75, 180, 60, "Силова земля дрона (GND)\nПольотний контролер\nШумні кола ESC & Motor", size=11, bold=True, fill="#f4f6f8", stroke=LINE))
    f.append(fitbox(725, 75, 180, 60, "Ізольована земля (GND_ISO)\nКамера, Підвіс, Радіоканал\nЧутливі аналогові сенсори", size=11, bold=True, fill="#eafaf1", stroke=FIELD))

    # Бар'єр ізоляції посередині
    f.append(line(692, 145, 692, 270, color=NEG, sw=2, dash="6,4"))
    f.append(text(692, 140, "Ізоляційний бар'єр 1.5–3 кВ", size=10, color=NEG, bold=True))

    f.append(fitbox(500, 160, 175, 50, "Ізольований DC-DC:\nТрансформаторна розв'язка\n(Flyback / Push-Pull)", size=10, fill="#ffffff", stroke=FIELD))
    f.append(arrow(675, 185, 725, 185, color=FIELD, sw=2))

    f.append(fitbox(500, 220, 175, 50, "Цифровий ізолятор:\nTI ISO7741 / ADuM1400\nЄмнісна / Магнітна розв'язка", size=10, fill="#ffffff", stroke=FIELD))
    f.append(arrow(675, 245, 725, 245, color=FIELD, sw=2))

    f.append(fitbox(500, 285, 405, 115, "Переваги архітектури:\n• Повна відсутність провідного шляху для силового струму ESC\n• Висока стійкість до синфазних перешкод: CMTI > 100 кВ/мкс\n• Затримка поширення сигналів < 11 нс, швидкість до 150 Мбіт/с\n• Безпечне підключення сервісного USB та відсутність зсуву потенціалів", size=11, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG, "ground-loop-isolation.svg"), W, H, *f)


def fig_data_interfaces_comparison():
    """3. Порівняння каналів передачі даних та пастка випромінювання USB 3.0 на GNSS."""
    W, H = 940, 460
    f = []

    f.append(fitbox(20, 20, 280, 40, "UART та RS-422\nНизька швидкість, довгі лінії", size=12, bold=True, fill="#f4f6f8", stroke=LINE))
    f.append(fitbox(320, 20, 300, 40, "USB 2.0 проти USB 3.0\nПастка інтерференції з GNSS L1", size=12, bold=True, fill="#fdecea", stroke=POS))
    f.append(fitbox(640, 20, 280, 40, "Single-Pair Ethernet (100BASE-T1)\nВисокошвидкісний відеопотік", size=12, bold=True, fill="#eafaf1", stroke=FIELD))

    # Блок 1: UART / RS-422
    f.append(rect(20, 75, 280, 365, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(fitbox(35, 90, 250, 80, "Single-Ended UART (3.3V):\n• Довжина: < 20–30 см\n• Чутливий до шуму dV/dt\n• Для внутрішньоплатних зв'язків", size=11, fill="#fbf2ef", stroke=POS))
    f.append(fitbox(35, 185, 250, 110, "Диференційний RS-422 / RS-485:\n• Довжина: до 50–100 метрів\n• Лінії TX+/TX-, RX+/RX- (вита пара)\n• Швидкість: 1–10 Мбод\n• Придушення синфазної завади\n• Для виносних антен і підвісів", size=11, fill="#f4fbf7", stroke=FIELD))
    f.append(fitbox(35, 310, 250, 110, "Застосування в дронах:\n• Передача команд MAVLink v2\n• Керування сервопідвісом\n• Отримання телеметрії сенсорів\n• Захист від перешкод моторів", size=11, fill="#f4f6f8", stroke=LINE))

    # Блок 2: USB 2.0 vs USB 3.0 & GNSS
    f.append(rect(320, 75, 300, 365, fill="#fffaf9", stroke=POS, sw=1.5))
    f.append(fitbox(335, 90, 270, 75, "USB 2.0 High-Speed (480 Мбіт/с):\n• Диференційний імпеданс: 90 Ом\n• Спектр сигналу зосереджений < 500 МГц\n• Безпечний для GPS-приймачів", size=11, fill="#f4fbf7", stroke=FIELD))
    f.append(fitbox(335, 175, 270, 115, "USB 3.0 SuperSpeed (5 Гбіт/с):\n• Spread Spectrum Clocking (SSC)\n• Широкосмуговий шум у смузі 1.2–1.6 ГГц\n• Рівень випромінювання: -110..-120 dBm\n• Чутливість GPS L1: -160 dBm\n• Результат: Втрата 3D GPS-фіксації!", size=11, fill="#fdecea", stroke=POS))
    f.append(fitbox(335, 300, 270, 120, "Методи ліквідації EMI:\n• Подвійний екран кабелю (STP, 360° GND)\n• Віддалення USB-кабелю від антени GPS > 15 см\n• Феритові фільтри на обох кінцях\n• Металеві екрануючі кожухи портів", size=11, fill="#ffffff", stroke=POS))

    # Блок 3: Ethernet & BroadR-Reach
    f.append(rect(640, 75, 280, 365, fill="#f4fbf7", stroke=FIELD, sw=1.5))
    f.append(fitbox(655, 90, 250, 95, "Автомобільний Ethernet (100BASE-T1):\n• BroadR-Reach / IEEE 802.3bw\n• 100 Мбіт/с по 1 витій парі (2 дроти)\n• Вага проводки в 4 рази менша за RJ-45\n• Повнодуплексна ехокомпенсація", size=11, fill="#ffffff", stroke=FIELD))
    f.append(fitbox(655, 195, 250, 95, "Стандартний Ethernet (1000BASE-T):\n• 1 Гбіт/с для важких потоків даних\n• Промислові роз'єми JST-GH / Molex\n• Трансформаторна розв'язка 1.5 кВ\n• Передача Raw point clouds LiDAR", size=11, fill="#ffffff", stroke=FIELD))
    f.append(fitbox(655, 300, 250, 120, "Застосування:\n• Стримінг 4K H.264/H.265 RTSP відео\n• Передача даних 3D LiDAR на Jetson\n• Машинний зір та SLAM-навігація\n• Нульовий вплив на радіоканали", size=11, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG, "data-interfaces-comparison.svg"), W, H, *f)


def fig_mavlink_camera_protocol_fsm():
    """4. Стан кінцевого автомата та послідовність повідомлень MAVLink Camera Protocol v2."""
    W, H = 940, 480
    f = []

    # Заголовок
    f.append(textbox(470, 30, "MAVLink Camera Protocol v2: Послідовність обміну та FSM захоплення", size=14, bold=True, fill="#eaf0fd", stroke=NEG)[0])

    # 3 вертикальні осі: Ground Control Station (QGC), Autopilot (FC), Camera Payload
    f.append(textbox(150, 75, "Ground Station (QGC)\n(sysid=255, compid=190)", size=12, bold=True, fill="#f4f6f8", stroke=LINE)[0])
    f.append(textbox(470, 75, "Flight Controller (FC)\n(sysid=1, compid=1)", size=12, bold=True, fill="#f4f6f8", stroke=LINE)[0])
    f.append(textbox(790, 75, "Camera Payload Driver\n(sysid=1, compid=100)", size=12, bold=True, fill="#eafaf1", stroke=FIELD)[0])

    # Вертикальні лінії
    f.append(line(150, 100, 150, 450, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(470, 100, 470, 450, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(790, 100, 790, 450, color=FIELD, sw=1.8))

    # 1. Heartbeat
    f.append(arrow(790, 125, 470, 125, color=FIELD, sw=1.5))
    f.append(arrow(470, 125, 150, 125, color=FIELD, sw=1.5))
    f.append(textbox(470, 115, "HEARTBEAT (1 Гц, type=MAV_TYPE_CAMERA, state=ACTIVE)", size=10, fill="#ffffff", stroke=FIELD)[0])

    # 2. Discovery: Request CAMERA_INFORMATION
    f.append(arrow(150, 160, 790, 160, color=NEG, sw=1.5))
    f.append(textbox(470, 150, "COMMAND_LONG(MAV_CMD_REQUEST_MESSAGE, param1=259)", size=10, fill="#ffffff", stroke=NEG)[0])

    f.append(arrow(790, 195, 150, 195, color=FIELD, sw=1.5))
    f.append(textbox(470, 185, "CAMERA_INFORMATION (Vendor, Model, CapFlags, URI def.xml)", size=10, fill="#ffffff", stroke=FIELD)[0])

    # 3. Settings & Zoom
    f.append(arrow(150, 230, 790, 230, color=LINE, sw=1.5))
    f.append(textbox(470, 220, "COMMAND_LONG(MAV_CMD_SET_CAMERA_ZOOM, type=ABSOLUTE, zoom=2.5x)", size=10, fill="#ffffff", stroke=LINE)[0])

    f.append(arrow(790, 255, 150, 255, color=FIELD, sw=1.5))
    f.append(textbox(470, 245, "COMMAND_ACK(command=SET_CAMERA_ZOOM, result=MAV_RESULT_ACCEPTED)", size=10, fill="#ffffff", stroke=FIELD)[0])

    # 4. Trigger Image Capture
    f.append(arrow(150, 295, 790, 295, color=POS, sw=2))
    f.append(textbox(470, 285, "COMMAND_LONG(MAV_CMD_IMAGE_START_CAPTURE, interval=0, count=1)", size=10, bold=True, fill="#ffffff", stroke=POS)[0])

    f.append(arrow(790, 325, 150, 325, color=FIELD, sw=1.5))
    f.append(textbox(470, 315, "COMMAND_ACK(command=IMAGE_START_CAPTURE, result=ACCEPTED)", size=10, fill="#ffffff", stroke=FIELD)[0])

    # 5. Local FSM: Hardware Shutter & Optical Exposure
    f.append(rect(710, 345, 160, 45, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(mtext(790, 360, "FSM: Hardware Sensor Exposure\nSensor Flash Sync Triggered", size=9, bold=True, color=POS))

    # 6. Geotagging Feedback: CAMERA_IMAGE_CAPTURED
    f.append(arrow(790, 410, 470, 410, color=FIELD, sw=2))
    f.append(arrow(470, 410, 150, 410, color=FIELD, sw=2))
    f.append(textbox(470, 400, "CAMERA_IMAGE_CAPTURED (time_utc, img_idx=42, lat, lon, alt, q[4], success=1)", size=10, bold=True, fill="#ffffff", stroke=FIELD)[0])

    f.append(fitbox(470, 428, 260, 28, "Автопілот записує геомітку в .ulog для RTK/PPK", size=9, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG, "mavlink-camera-protocol-fsm.svg"), W, H, *f)


def main():
    fig_power_filtering_topology()
    fig_ground_loop_isolation()
    fig_data_interfaces_comparison()
    fig_mavlink_camera_protocol_fsm()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
