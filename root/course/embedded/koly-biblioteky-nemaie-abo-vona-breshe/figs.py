# -*- coding: utf-8 -*-
"""Фігури для статті koly-biblioteky-nemaie-abo-vona-breshe.
Згенеровані через svgkit зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_bad_lib_vs_robust_driver():
    """Порівняння типової аматорської бібліотеки та промислового драйвера."""
    W, H = 840, 430
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Ліва колонка — Наївна бібліотека
    p.append(rect(20, 20, 385, 390, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(212, 50, "Аматорська бібліотека з мережі", size=15, color=POS, bold=True))

    bad_points = [
        ("delay(20) блокує процесор під час заміру", "#fee2e2", POS),
        ("malloc() на кожен пакет → фрагментація купи", "#fee2e2", POS),
        ("while (!ready) без таймауту → вічний завис", "#fee2e2", POS),
        ("Ігнорування NACK / помилок шини I2C/SPI", "#fee2e2", POS),
        ("Жорстка прив'язка до Arduino Wire / HAL", "#fee2e2", POS),
        ("Припущення про Little-Endian і UB при зсувах", "#fee2e2", POS),
    ]
    y = 80
    for title, fcol, tcol in bad_points:
        p.append(rect(35, y, 355, 38, fill=fcol, stroke=POS, sw=1.0, rx=4))
        p.append(text(212, y + 24, title, size=11, color=tcol, bold=True))
        y += 46

    p.append(rect(35, 360, 355, 40, fill="#ffffff", stroke=POS, sw=1.0, rx=4))
    p.append(text(212, 385, "Наслідок: збій під час вібрацій, завад або перезапуску", size=11, color=POS, bold=True))

    # Права колонка — Надійний драйвер
    p.append(rect(435, 20, 385, 390, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(627, 50, "Промисловий надійний драйвер", size=15, color=FIELD, bold=True))

    good_points = [
        ("Неблокуючий автомат станів (FSM / DMA)", "#dcfce7", FIELD),
        ("Статична пам'ять (нуль динамічних виділень)", "#dcfce7", FIELD),
        ("Суворі таймаути на кожну транзакцію", "#dcfce7", FIELD),
        ("Типізовані коди помилок (CRC, Bus, Timeout)", "#dcfce7", FIELD),
        ("Абстракція транспорту (легкі тести на ПК)", "#dcfce7", FIELD),
        ("Апаратне відновлення шини (Bus Recovery 9-clock)", "#dcfce7", FIELD),
    ]
    y = 80
    for title, fcol, tcol in good_points:
        p.append(rect(450, y, 355, 38, fill=fcol, stroke=FIELD, sw=1.0, rx=4))
        p.append(text(627, y + 24, title, size=11, color=tcol, bold=True))
        y += 46

    p.append(rect(450, 360, 355, 40, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(627, 385, "Результат: 100% передбачуваність у реальному часі", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "bad-lib-vs-robust-driver.svg"), W, H, *p)


def fig_driver_layer_architecture():
    """Трьохрівнева архітектура драйвера з абстракцією транспорту."""
    W, H = 840, 380
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Рівень 1: Застосунок
    p.append(rect(40, 20, 500, 55, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(290, 44, "Рівень застосунку (Application Layer)", size=14, color=NEG, bold=True))
    p.append(text(290, 62, "Отримує готові фізичні значення (SI: Па, °C, м/с²) без деталей регістрів", size=11, color=MUTED))

    # Стрілка вниз 1
    p.append(arrow(290, 75, 290, 95, color=INK, sw=1.5))

    # Рівень 2: Логіка чипа
    p.append(rect(40, 95, 500, 85, fill="#f8fafc", stroke=INK, sw=1.5, rx=6))
    p.append(text(290, 120, "Логіка чипа та автомат станів (Sensor Driver Core)", size=14, color=INK, bold=True))
    p.append(text(290, 142, "• Карта регістрів, бітові маски, послідовність ініціалізації", size=11, color=INK))
    p.append(text(290, 162, "• Неблокуючий FSM, калібрувальні формули, перевірка CRC-8", size=11, color=INK))

    # Стрілка вниз 2
    p.append(arrow(290, 180, 290, 200, color=INK, sw=1.5))

    # Рівень 3: Абстракція транспорту
    p.append(rect(40, 200, 500, 65, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(290, 226, "Транспортний інтерфейс (Bus Interface)", size=13, color="#d97706", bold=True))
    p.append(text(290, 248, "Контракт I/O: read_reg(dev, reg, buf, len), write_reg(dev, reg, buf, len)", size=11, color=INK))

    # Стрілка вниз 3 (розгалуження на залізо та хост-тести)
    p.append(arrow(165, 265, 165, 290, color=FIELD, sw=1.5))
    p.append(arrow(415, 265, 415, 290, color=NEG, sw=1.5))

    # Рівень 4а: Апаратна периферія МК
    p.append(rect(40, 290, 240, 70, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(160, 315, "Реальне залізо (Target MCU)", size=12, color=FIELD, bold=True))
    p.append(text(160, 335, "I2C/SPI HAL, DMA, переривання,", size=10, color=INK))
    p.append(text(160, 349, "апаратні регістри мікроконтролера", size=10, color=MUTED))

    # Рівень 4б: Хостові Unit-тести
    p.append(rect(300, 290, 240, 70, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(420, 315, "Тестове середовище (Host Mock)", size=12, color=NEG, bold=True))
    p.append(text(420, 335, "Програмний емулятор шини, ін'єкція", size=10, color=INK))
    p.append(text(420, 349, "помилок шини та збійних відліків", size=10, color=MUTED))

    # Права панель: Переваги архітектури
    p.append(rect(560, 20, 250, 340, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(685, 48, "Чому саме так:", size=13, color=INK, bold=True))

    benefits = [
        ("1. Нуль залежностей", "Чистий C/C++ без CMSIS чи Arduino"),
        ("2. Тести на ПК за 1 мс", "Unit-тести всієї математики на хості"),
        ("3. Легка заміна шини", "Перехід з I2C на SPI без зміни коду"),
        ("4. Чіткі межі помилок", "Розмежування апаратних і софтових збоїв"),
    ]
    y = 75
    for title, desc in benefits:
        p.append(text(575, y + 16, title, size=11, color=INK, bold=True, anchor="start"))
        p.append(text(575, y + 34, desc, size=10, color=MUTED, anchor="start"))
        p.append(line(575, y + 48, 795, y + 48, color="#e5e7eb", sw=1.0))
        y += 65

    render(os.path.join(OUT, "driver-layer-architecture.svg"), W, H, *p)


def fig_sensor_fsm_timeline():
    """Часова діаграма неблокуючого автомата опитування сенсора."""
    W, H = 840, 360
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(420, 30, "Часова діаграма неблокуючого опитування (FSM + DRDY / Таймер)", size=15, color=INK, bold=True))

    # Стан 1: TRIGGER
    p.append(rect(30, 60, 150, 70, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(105, 85, "STATE_TRIGGER", size=12, color=NEG, bold=True))
    p.append(text(105, 105, "I2C: Start Measure", size=10, color=INK))
    p.append(text(105, 119, "CPU: 4 мкс", size=10, color=MUTED))

    p.append(arrow(180, 95, 220, 95, color=INK, sw=1.5))

    # Стан 2: AWAIT_CONVERSION
    p.append(rect(220, 60, 220, 70, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(330, 85, "STATE_AWAIT_CONVERSION", size=12, color="#d97706", bold=True))
    p.append(text(330, 105, "Очікування 20 мс (DRDY або таймер)", size=10, color=INK))
    p.append(text(330, 119, "CPU: 0% (вільний для інших задач)", size=10, color=FIELD, bold=True))

    p.append(arrow(440, 95, 480, 95, color=INK, sw=1.5))

    # Стан 3: READ_RAW
    p.append(rect(480, 60, 160, 70, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(560, 85, "STATE_READ_RAW", size=12, color=NEG, bold=True))
    p.append(text(560, 105, "I2C Read / DMA Burst", size=10, color=INK))
    p.append(text(560, 119, "CPU: 6 мкс (старт DMA)", size=10, color=MUTED))

    p.append(arrow(640, 95, 680, 95, color=INK, sw=1.5))

    # Стан 4: PROCESS_DATA
    p.append(rect(680, 60, 130, 70, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(745, 85, "STATE_PROCESS", size=12, color=FIELD, bold=True))
    p.append(text(745, 105, "CRC + Math SI", size=10, color=INK))
    p.append(text(745, 119, "CPU: 12 мкс", size=10, color=FIELD))

    # Зворотна стрілка до IDLE
    p.append(line(745, 130, 745, 155, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(745, 155, 105, 155, color=MUTED, sw=1.2, dash="4,3"))
    p.append(arrow(105, 155, 105, 130, color=MUTED, sw=1.2))
    p.append(text(425, 150, "Повернення в IDLE або наступний цикл опитування", size=10, color=MUTED))

    # Графік завантаження CPU
    p.append(rect(30, 185, 780, 150, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=6))
    p.append(text(120, 210, "Завантаження процесора (CPU Time)", size=12, color=INK, bold=True))

    # Вісь часу
    p.append(arrow(60, 300, 780, 300, color=LINE, sw=1.5))
    p.append(text(770, 318, "Час t", size=11, color=MUTED))

    # Вісь завантаження
    p.append(arrow(60, 300, 60, 220, color=LINE, sw=1.5))
    p.append(text(50, 215, "100%", size=10, color=MUTED, anchor="end"))
    p.append(text(50, 300, "0%", size=10, color=MUTED, anchor="end"))

    # Імпульси завантаження
    p.append(rect(95, 235, 20, 65, fill=POS, stroke="none"))
    p.append(text(105, 228, "4 мкс", size=10, color=POS, bold=True))

    # Нульова зона (20 мс)
    p.append(line(115, 300, 550, 300, color=FIELD, sw=3.0))
    p.append(text(330, 275, "Інтервал перетворення сенсора (20 мс) — CPU вільний на 100%", size=11, color=FIELD, bold=True))

    p.append(rect(550, 235, 20, 65, fill=POS, stroke="none"))
    p.append(text(560, 228, "6 мкс", size=10, color=POS, bold=True))

    p.append(rect(735, 230, 20, 70, fill=FIELD, stroke="none"))
    p.append(text(745, 222, "12 мкс", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "sensor-fsm-timeline.svg"), W, H, *p)


def fig_i2c_bus_lockup_recovery():
    """Сценарій зависання лінії SDA в нулі та процедура 9-тактового відновлення."""
    W, H = 840, 420
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(420, 30, "Зависання шини I2C (SDA Lockup) та алгоритм відновлення 9 тактами", size=15, color=INK, bold=True))

    # Верхній блок: Як виникає зависання
    p.append(rect(30, 55, 780, 130, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(210, 80, "1. Причина: Скидання MCU під час читання байта", size=13, color=POS, bold=True))

    p.append(text(50, 110, "1. MCU зчитує 8 біт даних від веденого сенсора (Slave).", size=11, color=INK, anchor="start"))
    p.append(text(50, 130, "2. Сенсор передає біт '0' і притискає лінію SDA до землі (LOW).", size=11, color=INK, anchor="start"))
    p.append(text(50, 150, "3. У цю мить стається Reset / Watchdog MCU. Тактування SCL припиняється.", size=11, color=INK, anchor="start"))
    p.append(text(50, 170, "4. Сенсор лишається чекати наступного такту SCL і вічно тримає SDA=0 (шина заблокована!).", size=11, color=POS, anchor="start", bold=True))

    # Стрілка переходу до відновлення
    p.append(arrow(420, 185, 420, 210, color=INK, sw=2.0))

    # Нижній блок: Процедура відновлення
    p.append(rect(30, 210, 780, 190, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(220, 235, "2. Алгоритм апаратного розблокування (Bus Clear)", size=13, color=FIELD, bold=True))

    steps = [
        ("Крок 1: Відключити периферію I2C, перевести піни SCL і SDA в режим GPIO Open-Drain.", 262),
        ("Крок 2: Згенерувати до 9 тактових імпульсів на SCL (частота 50-100 кГц).", 284),
        ("Крок 3: Після кожного такту перевіряти стан SDA: щойно SDA відпущено (HIGH) — вихід із циклу.", 306),
        ("Крок 4: Сформувати коректну умову STOP (SCL=HIGH, потім SDA перехід LOW → HIGH).", 328),
        ("Крок 5: Повторно увімкнути та налаштувати апаратний блок I2C мікроконтролера.", 350),
    ]
    for st, y_pos in steps:
        p.append(text(50, y_pos, st, size=11, color=INK, anchor="start"))

    p.append(rect(50, 365, 740, 26, fill="#dcfce7", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(420, 382, "Результат: сенсор допередає байт, бачить NACK/STOP і звільняє шину без зняття живлення", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "i2c-bus-lockup-recovery.svg"), W, H, *p)


def fig_logic_analyzer_verification():
    """Верифікація транзакції I2C на екрані логічного аналізатора."""
    W, H = 840, 380
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(420, 30, "Верифікація I2C транзакції логічним аналізатором (PulseView / Sigrok)", size=15, color=INK, bold=True))

    # Канали аналізатора
    p.append(rect(30, 60, 780, 290, fill="#1e1e1e", stroke=LINE, sw=1.5, rx=8))

    # Канал D0: SCL
    p.append(rect(40, 75, 90, 45, fill="#333333", stroke="none", rx=4))
    p.append(text(85, 102, "D0: SCL", size=13, color="#fbbf24", bold=True))

    # Канал D1: SDA
    p.append(rect(40, 140, 90, 45, fill="#333333", stroke="none", rx=4))
    p.append(text(85, 167, "D1: SDA", size=13, color="#38bdf8", bold=True))

    # Канал декодера
    p.append(rect(40, 205, 90, 45, fill="#333333", stroke="none", rx=4))
    p.append(text(85, 232, "I2C Decode", size=12, color="#4ade80", bold=True))

    # Спрощене креслення імпульсів SCL
    x = 150
    scl_pts = []
    for _ in range(12):
        scl_pts.extend([(x, 115), (x + 10, 80), (x + 30, 80), (x + 40, 115), (x + 50, 115)])
        x += 50
    p.append(line(140, 80, 150, 80, color="#fbbf24", sw=2.0))
    for i in range(len(scl_pts) - 1):
        p.append(line(scl_pts[i][0], scl_pts[i][1], scl_pts[i+1][0], scl_pts[i+1][1], color="#fbbf24", sw=2.0))

    # SDA лінія з перепадами
    p.append(line(140, 145, 160, 145, color="#38bdf8", sw=2.0))
    p.append(line(160, 145, 170, 180, color="#38bdf8", sw=2.0))  # START
    p.append(line(170, 180, 280, 180, color="#38bdf8", sw=2.0))
    p.append(line(280, 180, 290, 145, color="#38bdf8", sw=2.0))
    p.append(line(290, 145, 450, 145, color="#38bdf8", sw=2.0))
    p.append(line(450, 145, 460, 180, color="#38bdf8", sw=2.0))
    p.append(line(460, 180, 680, 180, color="#38bdf8", sw=2.0))
    p.append(line(680, 180, 700, 145, color="#38bdf8", sw=2.0))  # STOP
    p.append(line(700, 145, 780, 145, color="#38bdf8", sw=2.0))

    # Блоки протокольного декодера PulseView
    dec_blocks = [
        ("S", 150, 35, "#ef4444"),
        ("Addr: 0x76 + W", 190, 120, "#3b82f6"),
        ("ACK", 315, 45, "#22c55e"),
        ("Reg: 0xF7 (DATA)", 365, 130, "#a855f7"),
        ("ACK", 500, 45, "#22c55e"),
        ("Val: 0x5A", 550, 85, "#eab308"),
        ("ACK", 640, 45, "#22c55e"),
        ("P", 690, 35, "#ef4444"),
    ]
    for lbl, bx, bw, bcol in dec_blocks:
        p.append(rect(bx, 212, bw, 32, fill=bcol, stroke="#ffffff", sw=1.0, rx=4))
        p.append(text(bx + bw / 2, 233, lbl, size=11, color="#ffffff", bold=True))

    # Нижня довідкова смужка
    p.append(rect(40, 275, 760, 60, fill="#262626", stroke=MUTED, sw=1.0, rx=4))
    p.append(text(420, 298, "Критичні точки контролю: 1. Setup/Hold таймінги даних SDA відносно фронтів SCL;", size=11, color="#e5e5e5"))
    p.append(text(420, 318, "2. Рівень перешкод під час спаду (Ground Bounce); 3. Чіткий ACK (0) від веденого чипа.", size=11, color="#4ade80"))

    render(os.path.join(OUT, "logic-analyzer-verification.svg"), W, H, *p)


if __name__ == "__main__":
    fig_bad_lib_vs_robust_driver()
    fig_driver_layer_architecture()
    fig_sensor_fsm_timeline()
    fig_i2c_bus_lockup_recovery()
    fig_logic_analyzer_verification()
    print("All figures generated successfully!")
