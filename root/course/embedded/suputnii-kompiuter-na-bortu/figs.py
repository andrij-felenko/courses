# -*- coding: utf-8 -*-
"""Фігури для статті suputnii-kompiuter-na-bortu
(«Супутній комп'ютер на борту: що рахує контролер, а що Linux»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. heterogeneous-architecture-split: Розподіл завдань між MCU та Linux ─────
def fig_heterogeneous_architecture_split():
    W, H = 840, 480
    p = []

    # Лівий блок — Польотний контролер (Hard Real-Time)
    p.append(rect(20, 20, 360, 440, fill="#f8fafc", stroke="#2563eb", sw=2.0, rx=8))
    p.append(rect(20, 20, 360, 44, fill="#dbeafe", stroke="#2563eb", sw=2.0, rx=8))
    p.append(text(200, 48, "ПОЛЬОТНИЙ КОНТРОЛЕР (Hard Real-Time)", size=13, color="#1e3a8a", bold=True))
    p.append(text(200, 80, "STM32H7 / NuttX / FreeRTOS (джиттер < 2 мкс)", size=11, color="#3b82f6", italic=True))

    # Складові контролера
    p.append(rect(35, 95, 330, 48, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=5))
    p.append(text(200, 115, "Опитування IMU (SPI @ 8 кГц)", size=12, color=INK, bold=True))
    p.append(text(200, 132, "Апаратне DMA, гіроскоп, акселерометр", size=10, color=MUTED))

    p.append(rect(35, 150, 330, 48, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=5))
    p.append(text(200, 170, "Оцінювач стану EKF3 (400 Гц)", size=12, color=INK, bold=True))
    p.append(text(200, 187, "Кватерніон орієнтації, позиція, швидкість", size=10, color=MUTED))

    p.append(rect(35, 205, 330, 48, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=5))
    p.append(text(200, 225, "Контури кутової швидкості PID (1–2 кГц)", size=12, color=INK, bold=True))
    p.append(text(200, 242, "Розрахунок моментів Roll, Pitch, Yaw", size=10, color=MUTED))

    p.append(rect(35, 260, 330, 48, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=5))
    p.append(text(200, 280, "Генерація DShot600 (1 кГц)", size=12, color=INK, bold=True))
    p.append(text(200, 297, "ШІМ/DShot імпульси безпосередньо на ESC", size=10, color=MUTED))

    p.append(rect(35, 315, 330, 48, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=5))
    p.append(text(200, 335, "Аварійний Failsafe & RC-приймач", size=12, color=INK, bold=True))
    p.append(text(200, 352, "Апаратний монітор зв'язку, автопосадка", size=10, color=MUTED))

    p.append(rect(35, 370, 330, 75, fill="#fef2f2", stroke="#f87171", sw=1.2, rx=5))
    p.append(text(200, 390, "КРИТИЧНІСТЬ: АБСОЛЮТНА", size=11, color="#991b1b", bold=True))
    p.append(text(200, 408, "Затримка > 5 мс → зрив контуру стабілізації", size=10, color="#b91c1c"))
    p.append(text(200, 426, "та миттєве падіння апарата", size=10, color="#b91c1c"))

    # Правий блок — Супутній комп'ютер (Soft Real-Time Linux)
    p.append(rect(460, 20, 360, 440, fill="#f8fafc", stroke="#059669", sw=2.0, rx=8))
    p.append(rect(460, 20, 360, 44, fill="#d1fae5", stroke="#059669", sw=2.0, rx=8))
    p.append(text(640, 48, "СУПУТНІЙ КОМП'ЮТЕР (Soft Real-Time)", size=13, color="#065f46", bold=True))
    p.append(text(640, 80, "Raspberry Pi CM4 / Jetson Orin / Linux OS", size=11, color="#059669", italic=True))

    # Складові комп'ютера
    p.append(rect(475, 95, 330, 48, fill="#ecfdf5", stroke="#a7f3d0", sw=1.2, rx=5))
    p.append(text(640, 115, "Візуальна одометрія / VIO (30–60 Гц)", size=12, color=INK, bold=True))
    p.append(text(640, 132, "Стереокамера, оптичний потік, SLAM", size=10, color=MUTED))

    p.append(rect(475, 150, 330, 48, fill="#ecfdf5", stroke="#a7f3d0", sw=1.2, rx=5))
    p.append(text(640, 170, "Нейромережі та Computer Vision (15–30 Гц)", size=12, color=INK, bold=True))
    p.append(text(640, 187, "YOLO, детекція об'єктів, трекінг цілі", size=10, color=MUTED))

    p.append(rect(475, 205, 330, 48, fill="#ecfdf5", stroke="#a7f3d0", sw=1.2, rx=5))
    p.append(text(640, 225, "Планування траєкторій (10–20 Гц)", size=12, color=INK, bold=True))
    p.append(text(640, 242, "Обхід перешкод, B-spline генерація шляху", size=10, color=MUTED))

    p.append(rect(475, 260, 330, 48, fill="#ecfdf5", stroke="#a7f3d0", sw=1.2, rx=5))
    p.append(text(640, 280, "Зв'язок 4G/5G, VPN, хмарна телеметрія", size=12, color=INK, bold=True))
    p.append(text(640, 297, "QMI/MBIM модеми, стрімінг H.264/H.265", size=10, color=MUTED))

    p.append(rect(475, 315, 330, 48, fill="#ecfdf5", stroke="#a7f3d0", sw=1.2, rx=5))
    p.append(text(640, 335, "Стек ROS 2 / DDS мікросервіси", size=12, color=INK, bold=True))
    p.append(text(640, 352, "Високорівнева логіка місії та ройова взаємодія", size=10, color=MUTED))

    p.append(rect(475, 370, 330, 75, fill="#fefce8", stroke="#fde047", sw=1.2, rx=5))
    p.append(text(640, 390, "КРИТИЧНІСТЬ: ВТОРИННА (ДОЗВОЛЕНО ЗБІЙ)", size=11, color="#854d0e", bold=True))
    p.append(text(640, 408, "Затримка > 50 мс через CFS/Swap не фатальна:", size=10, color="#713f12"))
    p.append(text(640, 426, "контролер переходить у Loiter / Return-to-Home", size=10, color="#713f12"))

    # Центральна шина зв'язку
    p.append(rect(388, 160, 64, 150, fill="#ffffff", stroke="#475569", sw=1.5, rx=4))
    p.append(text(420, 185, "МІСТОК", size=10, color="#334155", bold=True))
    p.append(text(420, 205, "UART", size=11, color="#0f172a", bold=True))
    p.append(text(420, 222, "921.6k / 3M", size=9, color=MUTED))
    p.append(text(420, 238, "CTS/RTS", size=9, color=MUTED))
    p.append(text(420, 258, "або", size=10, color=MUTED, italic=True))
    p.append(text(420, 275, "Ethernet", size=11, color="#0f172a", bold=True))
    p.append(text(420, 292, "MAVLink/ROS", size=9, color="#2563eb"))

    # Стрілки обміну
    p.append(arrow(380, 190, 390, 190, color="#2563eb", sw=2.0))
    p.append(arrow(450, 190, 460, 190, color="#2563eb", sw=2.0))
    p.append(arrow(460, 260, 450, 260, color="#059669", sw=2.0))
    p.append(arrow(390, 260, 380, 260, color="#059669", sw=2.0))

    render(os.path.join(OUT, "heterogeneous-architecture-split.svg"), W, H, *p)


# ── 2. uart-dma-flow-control: Апаратний UART з CTS/RTS та буферизацією DMA ──
def fig_uart_dma_flow_control():
    W, H = 820, 420
    p = []

    # Блок зліва: Польотний контролер (STM32)
    p.append(rect(20, 30, 280, 360, fill="#f0f9ff", stroke="#0284c7", sw=1.8, rx=6))
    p.append(text(160, 60, "ПОЛЬОТНИЙ КОНТРОЛЕР", size=13, color="#0369a1", bold=True))
    p.append(text(160, 80, "USART1 (з апаратним DMA)", size=11, color=MUTED))

    p.append(rect(35, 105, 250, 50, fill="#ffffff", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(160, 126, "Кільцевий буфер TX DMA", size=11, color=INK, bold=True))
    p.append(text(160, 144, "Пряма вичитка з SRAM без навантаження CPU", size=9, color=MUTED))

    p.append(rect(35, 175, 250, 50, fill="#ffffff", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(160, 196, "Кільцевий буфер RX DMA", size=11, color=INK, bold=True))
    p.append(text(160, 214, "Прийом пакетів по IDLE-перериванню", size=9, color=MUTED))

    p.append(rect(35, 245, 250, 65, fill="#e0f2fe", stroke="#38bdf8", sw=1.2, rx=4))
    p.append(text(160, 268, "Логіка Flow Control (Апаратно)", size=11, color="#0369a1", bold=True))
    p.append(text(160, 286, "CTS перевіряється перед кожним байтом", size=9, color=INK))
    p.append(text(160, 301, "RTS піднімається при заповненні FIFO", size=9, color=INK))

    p.append(text(160, 350, "Рівні напруг: 3.3V CMOS", size=11, color="#075985", bold=True))
    p.append(text(160, 370, "Швидкість: 921 600 … 3 000 000 бод", size=10, color=MUTED))

    # Блок справа: Бортовий комп'ютер (Linux SoC)
    p.append(rect(520, 30, 280, 360, fill="#f0fdf4", stroke="#16a34a", sw=1.8, rx=6))
    p.append(text(660, 60, "СУПУТНІЙ КОМП'ЮТЕР (Linux)", size=13, color="#15803d", bold=True))
    p.append(text(660, 80, "/dev/ttyAMA0 (termios + CRTSCTS)", size=11, color=MUTED))

    p.append(rect(535, 105, 250, 50, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=4))
    p.append(text(660, 126, "TTY RX Buffer (Ядро Linux)", size=11, color=INK, bold=True))
    p.append(text(660, 144, "Черга n_tty / DMA контролера SoC", size=9, color=MUTED))

    p.append(rect(535, 175, 250, 50, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=4))
    p.append(text(660, 196, "Користувацький процес (Bridge)", size=11, color=INK, bold=True))
    p.append(text(660, 214, "C++ / Python розбір MAVLink v2", size=9, color=MUTED))

    p.append(rect(535, 245, 250, 65, fill="#dcfce7", stroke="#4ade80", sw=1.2, rx=4))
    p.append(text(660, 268, "Захист від CPU Jitter", size=11, color="#15803d", bold=True))
    p.append(text(660, 286, "Якщо процес заблокований CFS/Swap,", size=9, color=INK))
    p.append(text(660, 301, "SoC виставляє RTS=HIGH (призупиняє FC)", size=9, color=INK))

    p.append(text(660, 350, "Рівні напруг: 3.3V LVTTL", size=11, color="#166534", bold=True))
    p.append(text(660, 370, "Вимкнено софтовий XON/XOFF", size=10, color=MUTED))

    # Лінії зв'язку між платами посередині
    # TX -> RX
    p.append(arrow(300, 120, 520, 120, color="#2563eb", sw=2.0))
    p.append(rect(365, 105, 90, 22, fill="#ffffff", stroke="#2563eb", sw=1.0, rx=3))
    p.append(text(410, 120, "TX → RX (Дані)", size=9, color="#2563eb", bold=True))

    # RX <- TX
    p.append(arrow(520, 160, 300, 160, color="#16a34a", sw=2.0))
    p.append(rect(365, 145, 90, 22, fill="#ffffff", stroke="#16a34a", sw=1.0, rx=3))
    p.append(text(410, 160, "RX ← TX (Уставки)", size=9, color="#16a34a", bold=True))

    # RTS -> CTS (з боку FC)
    p.append(arrow(300, 205, 520, 205, color="#d97706", sw=1.6))
    p.append(rect(360, 192, 100, 22, fill="#ffffff", stroke="#d97706", sw=1.0, rx=3))
    p.append(text(410, 207, "RTS → CTS (FC Flow)", size=9, color="#d97706", bold=True))

    # CTS <- RTS (з боку Linux)
    p.append(arrow(520, 245, 300, 245, color="#dc2626", sw=1.6))
    p.append(rect(350, 232, 120, 22, fill="#ffffff", stroke="#dc2626", sw=1.0, rx=3))
    p.append(text(410, 247, "CTS ← RTS (Linux Flow)", size=9, color="#dc2626", bold=True))

    # GND спільний
    p.append(line(300, 290, 520, 290, color="#1e293b", sw=2.5))
    p.append(rect(365, 278, 90, 22, fill="#ffffff", stroke="#1e293b", sw=1.0, rx=3))
    p.append(text(410, 293, "GND (Спільна)", size=9, color="#1e293b", bold=True))

    render(os.path.join(OUT, "uart-dma-flow-control.svg"), W, H, *p)


# ── 3. failsafe-timeout-fsm: Скінченний автомат безпеки при втраті зв'язку ────
def fig_failsafe_timeout_fsm():
    W, H = 840, 400
    p = []

    # Стан 1: OFFBOARD / GUIDED (Штатний режим)
    p.append(rect(30, 120, 210, 140, fill="#ecfdf5", stroke="#059669", sw=2.0, rx=8))
    p.append(text(135, 150, "OFFBOARD / GUIDED", size=13, color="#065f46", bold=True))
    p.append(text(135, 175, "Штатне виконання уставок", size=10, color=INK))
    p.append(text(135, 195, "Потік команд: > 2–5 Гц", size=10, color="#059669", bold=True))
    p.append(text(135, 215, "Таймер Watchdog = 0 мс", size=10, color=MUTED))
    p.append(text(135, 238, "Керування: Linux Companion", size=9, color="#047857", italic=True))

    # Петля оновлення watchdog
    p.append(arrow(70, 120, 70, 75, color="#059669", sw=1.4))
    p.append(line(70, 75, 200, 75, color="#059669", sw=1.4))
    p.append(arrow(200, 75, 200, 120, color="#059669", sw=1.4))
    p.append(text(135, 65, "Прийом уставки → Скидання таймера", size=9, color="#059669", bold=True))

    # Перехід 1: Тайм-аут 500 мс
    p.append(arrow(240, 170, 310, 170, color="#d97706", sw=2.0))
    p.append(rect(242, 130, 66, 32, fill="#fffbeb", stroke="#d97706", sw=1.0, rx=3))
    p.append(text(275, 144, "t > 500 мс", size=9, color="#b45309", bold=True))
    p.append(text(275, 157, "Нема уставки", size=9, color="#b45309"))

    # Стан 2: HOLD / LOITER (Безпечне зависання)
    p.append(rect(310, 120, 220, 140, fill="#fffbeb", stroke="#d97706", sw=2.0, rx=8))
    p.append(text(420, 150, "HOLD / LOITER", size=13, color="#b45309", bold=True))
    p.append(text(420, 175, "Утримання позиції на місці", size=10, color=INK))
    p.append(text(420, 195, "Очікування відновлення зв'язку", size=10, color=MUTED))
    p.append(text(420, 215, "Таймер Failsafe: 0.5 … 3.0 с", size=10, color="#d97706", bold=True))
    p.append(text(420, 238, "Керування: Автономний EKF FC", size=9, color="#92400e", italic=True))

    # Зворотний перехід при відновленні потоку
    p.append(arrow(310, 220, 240, 220, color="#059669", sw=1.4))
    p.append(text(275, 234, "Відновлення", size=9, color="#059669", bold=True))
    p.append(text(275, 247, "потоку команд", size=9, color="#059669"))

    # Перехід 2: Тайм-аут 3000 мс
    p.append(arrow(530, 170, 600, 170, color="#dc2626", sw=2.0))
    p.append(rect(534, 130, 62, 32, fill="#fef2f2", stroke="#dc2626", sw=1.0, rx=3))
    p.append(text(565, 144, "t > 3000 мс", size=9, color="#991b1b", bold=True))
    p.append(text(565, 157, "Повний збій", size=9, color="#991b1b"))

    # Стан 3: RETURN TO LAUNCH / LAND (Аварійне повернення або посадка)
    p.append(rect(600, 120, 210, 140, fill="#fef2f2", stroke="#dc2626", sw=2.0, rx=8))
    p.append(text(705, 150, "FAILSAFE: RTL / LAND", size=13, color="#991b1b", bold=True))
    p.append(text(705, 175, "Автономне повернення додому", size=10, color=INK))
    p.append(text(705, 195, "або негайна керована посадка", size=10, color=INK))
    p.append(text(705, 215, "Ігнорування команд Companion", size=10, color="#dc2626", bold=True))
    p.append(text(705, 238, "Керування: Бортовий навігатор FC", size=9, color="#7f1d1d", italic=True))

    # Нижній пояснювальний блок
    p.append(rect(30, 295, 780, 80, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=6))
    p.append(text(420, 318, "ЗОЛОТЕ ПРАВИЛО БЕЗПЕКИ АВІОНІКИ: «COMPANION IS UNTRUSTED»", size=11, color="#1e293b", bold=True))
    p.append(text(420, 338, "Польотний контролер ставиться до Linux як до джерела зовнішніх порад, а не до життєво необхідного вузла.", size=10, color=INK))
    p.append(text(420, 356, "Будь-яке зависання, Kernel Panic чи перевантаження Linux не призводить до втрати стійкості та падіння дрона.", size=10, color="#475569", italic=True))

    render(os.path.join(OUT, "failsafe-timeout-fsm.svg"), W, H, *p)


if __name__ == "__main__":
    fig_heterogeneous_architecture_split()
    fig_uart_dma_flow_control()
    fig_failsafe_timeout_fsm()
    print("All figures generated successfully in img/")
