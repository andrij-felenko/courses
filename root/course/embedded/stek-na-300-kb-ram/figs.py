# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. lwip-memory-subsystems: розподіл 300 КБ SRAM мікроконтролера ─────────────
def fig_memory_subsystems():
    W, H = 940, 480
    p = []

    # Загальний контейнер SRAM 300 КБ
    p.append(rect(40, 60, 860, 390, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(470, 85, "Загальний бюджет оперативної пам'яті (SRAM 300 КБ, наприклад STM32F4/F7 або ESP32)",
                  size=14, color=INK, bold=True))

    # Секція 1: Додаток і RTOS (ліворуч)
    p.append(rect(60, 110, 240, 320, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    p.append(text(180, 135, "Додаток та RTOS", size=13, color=INK, bold=True))
    p.append(text(180, 155, "≈ 120–140 КБ", size=11, color=MUTED))

    p.append(rect(75, 175, 210, 50, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(180, 195, "Стек завдань FreeRTOS", size=11, color=INK, bold=True))
    p.append(text(180, 212, "Задачі давачів, логіки, UI", size=10, color=MUTED))

    p.append(rect(75, 235, 210, 50, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(180, 255, "Черги, м'ютекси, семафори", size=11, color=INK, bold=True))
    p.append(text(180, 272, "IPC ядра операційної системи", size=10, color=MUTED))

    p.append(rect(75, 295, 210, 50, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(180, 315, "Глобальні змінні й Heap", size=11, color=INK, bold=True))
    p.append(text(180, 332, ".data / .bss та malloc() додатку", size=10, color=MUTED))

    p.append(rect(75, 355, 210, 60, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(180, 375, "Буфери периферії", size=11, color=INK, bold=True))
    p.append(text(180, 392, "UART, SPI, дисплей, файли", size=10, color=MUTED))

    # Секція 2: lwIP Стек (посередині)
    p.append(rect(320, 110, 350, 320, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(495, 135, "lwIP Стек (Пул пам'яті й Купа)", size=13, color=NEG, bold=True))
    p.append(text(495, 155, "≈ 120–140 КБ (конфігурація мережі)", size=11, color=NEG))

    # Блок 2.1: MEMP Pools
    p.append(rect(335, 175, 320, 110, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
    p.append(text(495, 195, "Фіксовані пули пам'яті (memp)", size=12, color=NEG, bold=True))
    p.append(text(350, 218, "• PBUF_POOL: 16–32 буфери (по 512–1536 Б)", size=10.5, color=INK, anchor="start"))
    p.append(text(350, 238, "• TCP_PCB (TCB): 8–16 блоків (по 160 Б)", size=10.5, color=INK, anchor="start"))
    p.append(text(350, 258, "• TCP_SEG, UDP_PCB, NETCONN структури", size=10.5, color=INK, anchor="start"))
    p.append(text(350, 276, "• O(1) алокація без фрагментації пам'яті", size=9.5, color=FIELD, anchor="start", bold=True))

    # Блок 2.2: MEM Heap
    p.append(rect(335, 295, 320, 120, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
    p.append(text(495, 315, "Купа мережевого стека (MEM_SIZE Heap)", size=12, color=NEG, bold=True))
    p.append(text(350, 338, "• Динамічні буфери PBUF_RAM (TX черги)", size=10.5, color=INK, anchor="start"))
    p.append(text(350, 358, "• Збірка IP-фрагментів і TCP-сегментів", size=10.5, color=INK, anchor="start"))
    p.append(text(350, 378, "• Буфери сокетних структур та опцій", size=10.5, color=INK, anchor="start"))
    p.append(text(350, 398, "• Виділений статичний масив ram_heap[]", size=9.5, color=MUTED, anchor="start"))

    # Секція 3: Ethernet DMA (праворуч)
    p.append(rect(690, 110, 190, 320, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(785, 135, "Ethernet DMA", size=13, color=FIELD, bold=True))
    p.append(text(785, 155, "≈ 20–30 КБ", size=11, color=FIELD))

    p.append(rect(705, 175, 160, 70, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    p.append(text(785, 195, "RX Дільники DMA", size=11, color=FIELD, bold=True))
    p.append(text(785, 215, "4–8 дескрипторів", size=10, color=INK))
    p.append(text(785, 232, "Кільцевий список", size=9.5, color=MUTED))

    p.append(rect(705, 255, 160, 70, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    p.append(text(785, 275, "TX Дільники DMA", size=11, color=FIELD, bold=True))
    p.append(text(785, 295, "4–8 дескрипторів", size=10, color=INK))
    p.append(text(785, 312, "Кільцевий список", size=9.5, color=MUTED))

    p.append(rect(705, 335, 160, 80, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    p.append(text(785, 355, "DMA Буфери RAM", size=11, color=FIELD, bold=True))
    p.append(text(785, 375, "Zero-Copy прив'язка", size=10, color=INK))
    p.append(text(785, 395, "до pbuf_pool блоків", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "lwip-memory-subsystems.svg"), W, H, *p,
           title="Архітектура пам'яті вбудованого TCP/IP стека у ліміті 300 КБ RAM")


# ── 2. pbuf-types-and-chain: 4 типи pbuf та механізм pbuf_header ───────────────
def fig_pbuf_types():
    W, H = 940, 500
    p = []

    # 1. PBUF_RAM (один блок під заголовок + дані)
    p.append(rect(50, 70, 390, 80, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    p.append(text(65, 95, "1. PBUF_RAM (Купа mem_malloc)", size=12, color=INK, bold=True, anchor="start"))
    p.append(rect(70, 110, 110, 30, fill="#cbd5e1", stroke="#475569", sw=1, rx=3))
    p.append(text(125, 130, "struct pbuf", size=11, color=INK, bold=True))
    p.append(rect(185, 110, 240, 30, fill="#e2e8f0", stroke="#64748b", sw=1, rx=3))
    p.append(text(305, 130, "Payload (суцільний з pbuf блок)", size=10.5, color=INK))

    # 2. PBUF_POOL (ланцюжок фіксованих блоків)
    p.append(rect(50, 170, 840, 120, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(65, 195, "2. PBUF_POOL (Ланцюжок блоків фіксованого розміру для RX / TX)", size=12, color=NEG, bold=True, anchor="start"))

    # Вузол 1
    p.append(rect(70, 215, 90, 60, fill="#bfdbfe", stroke=NEG, sw=1.2, rx=4))
    p.append(text(115, 235, "struct pbuf 1", size=10.5, color=NEG, bold=True))
    p.append(text(115, 252, "tot_len: 1460", size=9.5, color=INK))
    p.append(text(115, 267, "len: 512", size=9.5, color=INK))

    p.append(rect(165, 215, 170, 60, fill="#dbeafe", stroke="#3b82f6", sw=1, rx=4))
    p.append(text(250, 240, "Payload блок 1 (512 Б)", size=10.5, color=INK, bold=True))
    p.append(text(250, 260, "Заголовки ETH/IP/TCP + дані", size=9.5, color=MUTED))

    # Стрілка next 1 -> 2
    p.append(arrow(340, 245, 385, 245, color=NEG, sw=2))
    p.append(text(362, 235, "next", size=9.5, color=NEG, bold=True))

    # Вузол 2
    p.append(rect(390, 215, 90, 60, fill="#bfdbfe", stroke=NEG, sw=1.2, rx=4))
    p.append(text(435, 235, "struct pbuf 2", size=10.5, color=NEG, bold=True))
    p.append(text(435, 252, "tot_len: 948", size=9.5, color=INK))
    p.append(text(435, 267, "len: 512", size=9.5, color=INK))

    p.append(rect(485, 215, 170, 60, fill="#dbeafe", stroke="#3b82f6", sw=1, rx=4))
    p.append(text(570, 240, "Payload блок 2 (512 Б)", size=10.5, color=INK, bold=True))
    p.append(text(570, 260, "Продовження корисних даних", size=9.5, color=MUTED))

    # Стрілка next 2 -> 3
    p.append(arrow(660, 245, 705, 245, color=NEG, sw=2))
    p.append(text(682, 235, "next", size=9.5, color=NEG, bold=True))

    # Вузол 3
    p.append(rect(710, 215, 90, 60, fill="#bfdbfe", stroke=NEG, sw=1.2, rx=4))
    p.append(text(755, 235, "struct pbuf 3", size=10.5, color=NEG, bold=True))
    p.append(text(755, 252, "tot_len: 436", size=9.5, color=INK))
    p.append(text(755, 267, "len: 436", size=9.5, color=INK))

    p.append(rect(805, 215, 70, 60, fill="#dbeafe", stroke="#3b82f6", sw=1, rx=4))
    p.append(text(840, 245, "Кінець", size=10, color=INK, bold=True))
    p.append(text(840, 262, "436 Б", size=9, color=MUTED))

    # 3. PBUF_ROM / PBUF_REF (нульове копіювання Flash/зовнішньої RAM)
    p.append(rect(50, 310, 840, 80, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(65, 335, "3. PBUF_ROM / PBUF_REF (Вказівник без дублювання даних)", size=12, color=FIELD, bold=True, anchor="start"))

    p.append(rect(70, 345, 120, 35, fill="#bbf7d0", stroke=FIELD, sw=1.2, rx=3))
    p.append(text(130, 367, "struct pbuf (RAM)", size=10.5, color=INK, bold=True))

    p.append(arrow(195, 362, 275, 362, color=FIELD, sw=2))
    p.append(text(235, 352, "payload *", size=9.5, color=FIELD, bold=True))

    p.append(rect(280, 345, 590, 35, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=3))
    p.append(text(575, 367, "Flash ROM / Статичний буфер RAM (HTML, CSS, JSON, сертифікати)", size=10.5, color=INK, bold=True))

    # 4. Демонстрація pbuf_header()
    p.append(rect(50, 410, 840, 75, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(65, 430, "Маніпуляція заголовками без memcpy: функція pbuf_header(p, +/- bytes)", size=12, color="#b45309", bold=True, anchor="start"))

    p.append(rect(70, 442, 120, 30, fill="#fef3c7", stroke="#f59e0b", sw=1, rx=3))
    p.append(text(130, 462, "ETH Header (14B)", size=10, color=INK))

    p.append(rect(195, 442, 120, 30, fill="#fed7aa", stroke="#f97316", sw=1, rx=3))
    p.append(text(255, 462, "IP Header (20B)", size=10, color=INK))

    p.append(rect(320, 442, 120, 30, fill="#fde68a", stroke="#eab308", sw=1, rx=3))
    p.append(text(380, 462, "TCP Header (20B)", size=10, color=INK))

    p.append(rect(445, 442, 435, 30, fill="#d9f99d", stroke="#84cc16", sw=1, rx=3))
    p.append(text(662, 462, "Корисні дані (Application Data Payload) — вказівник payload зсувається вправо", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "pbuf-types-and-chain.svg"), W, H, *p,
           title="Типи пакетних буферів pbuf та механізм обробки нульового копіювання")


# ── 3. api-triad-comparison: три API стека lwIP ────────────────────────────────
def fig_api_triad():
    W, H = 940, 460
    p = []

    # Колонка 1: Raw Callback API
    p.append(rect(40, 60, 270, 375, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(175, 90, "Raw Callback API", size=14, color=FIELD, bold=True))
    p.append(text(175, 110, "Подієва модель (Event-Driven)", size=11, color=MUTED))

    p.append(rect(55, 130, 240, 75, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    p.append(text(175, 150, "Один спільний потік", size=11.5, color=FIELD, bold=True))
    p.append(text(175, 170, "Головний цикл або один", size=10, color=INK))
    p.append(text(175, 188, "потік обробки переривань", size=10, color=INK))

    p.append(rect(55, 215, 240, 115, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    p.append(text(175, 235, "Зворотні виклики:", size=11, color=INK, bold=True))
    p.append(text(175, 255, "• tcp_recv() / tcp_sent()", size=10, color=INK))
    p.append(text(175, 275, "• tcp_accept() / tcp_err()", size=10, color=INK))
    p.append(text(175, 295, "• tcp_poll() за таймером", size=10, color=INK))
    p.append(text(175, 315, "0 копіювань, нуль RTOS задач", size=9.5, color=FIELD, bold=True))

    p.append(rect(55, 340, 240, 80, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    p.append(text(175, 360, "Витрати пам'яті:", size=11, color=INK, bold=True))
    p.append(text(175, 380, "Лише struct tcp_pcb (≈160 Б)", size=10, color=FIELD, bold=True))
    p.append(text(175, 400, "Найшвидший, 0 накладів RTOS", size=9.5, color=MUTED))

    # Колонка 2: Netconn API
    p.append(rect(335, 60, 270, 375, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(470, 90, "Netconn API", size=14, color=NEG, bold=True))
    p.append(text(470, 110, "Послідовна блокуюча модель", size=11, color=MUTED))

    p.append(rect(350, 130, 240, 75, fill="#ffffff", stroke="#93c5fd", sw=1, rx=4))
    p.append(text(470, 150, "Окремий tcpip_thread", size=11.5, color=NEG, bold=True))
    p.append(text(470, 170, "Взаємодія через черги RTOS", size=10, color=INK))
    p.append(text(470, 188, "(sys_mbox) та семафори", size=10, color=INK))

    p.append(rect(350, 215, 240, 115, fill="#ffffff", stroke="#93c5fd", sw=1, rx=4))
    p.append(text(470, 235, "Блокуючі виклики:", size=11, color=INK, bold=True))
    p.append(text(470, 255, "• netconn_new() / bind()", size=10, color=INK))
    p.append(text(470, 275, "• netconn_accept() [блок]", size=10, color=INK))
    p.append(text(470, 295, "• netconn_recv() / write()", size=10, color=INK))
    p.append(text(470, 315, "Зручний лінійний код у RTOS", size=9.5, color=NEG, bold=True))

    p.append(rect(350, 340, 240, 80, fill="#ffffff", stroke="#93c5fd", sw=1, rx=4))
    p.append(text(470, 360, "Витрати пам'яті:", size=11, color=INK, bold=True))
    p.append(text(470, 380, "Стек tcpip_thread + стеки задач", size=10, color=NEG, bold=True))
    p.append(text(470, 400, "≈ 2–4 КБ на кожне з'єднання", size=9.5, color=MUTED))

    # Колонка 3: BSD Sockets API
    p.append(rect(630, 60, 270, 375, fill="#fdf4ff", stroke="#a855f7", sw=1.8, rx=8))
    p.append(text(765, 90, "BSD Sockets API", size=14, color="#a855f7", bold=True))
    p.append(text(765, 110, "POSIX Стандартний шар", size=11, color=MUTED))

    p.append(rect(645, 130, 240, 75, fill="#ffffff", stroke="#d8b4fe", sw=1, rx=4))
    p.append(text(765, 150, "Обгортка над Netconn", size=11.5, color="#a855f7", bold=True))
    p.append(text(765, 170, "Таблиця сокетів sockets[]", size=10, color=INK))
    p.append(text(765, 188, "та дескрипторів файлів", size=10, color=INK))

    p.append(rect(645, 215, 240, 115, fill="#ffffff", stroke="#d8b4fe", sw=1, rx=4))
    p.append(text(765, 235, "POSIX функції:", size=11, color=INK, bold=True))
    p.append(text(765, 255, "• socket(), bind(), listen()", size=10, color=INK))
    p.append(text(765, 275, "• send(), recv(), select()", size=10, color=INK))
    p.append(text(765, 295, "• setsockopt(), poll()", size=10, color=INK))
    p.append(text(765, 315, "Максимальна сумісність коду", size=9.5, color="#a855f7", bold=True))

    p.append(rect(645, 340, 240, 80, fill="#ffffff", stroke="#d8b4fe", sw=1, rx=4))
    p.append(text(765, 360, "Витрати пам'яті:", size=11, color=INK, bold=True))
    p.append(text(765, 380, "Найважчий стек + копіювання", size=10, color=POS, bold=True))
    p.append(text(765, 400, "Копіювання з pbuf у буфер char*", size=9.5, color=MUTED))

    render(os.path.join(OUT, "api-triad-comparison.svg"), W, H, *p,
           title="Тріада API lwIP: вибір між мінімальним споживанням RAM та сумісністю POSIX")


# ── 4. zerocopy-dma-pipeline: конвеєр Zero-Copy RX/TX ─────────────────────────
def fig_zerocopy_pipeline():
    W, H = 940, 440
    p = []

    # Порівняння: Зверху — класичний Double-Copy, Знизу — Zero-Copy

    # 1. Класичний підхід (з подвійним копіюванням)
    p.append(rect(40, 60, 860, 160, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(60, 85, "Класична схема з копіюванням (Double Copy) — до 70% навантаження CPU на 100 Мбіт/с",
                  size=12, color=POS, bold=True, anchor="start"))

    p.append(rect(60, 105, 140, 90, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=4))
    p.append(text(130, 130, "Кабель Ethernet", size=11, color=INK, bold=True))
    p.append(text(130, 150, "Фізичний рівень", size=10, color=MUTED))
    p.append(text(130, 170, "PHY / RMII", size=10, color=MUTED))

    p.append(arrow(205, 150, 245, 150, color=POS, sw=1.8))

    p.append(rect(250, 105, 160, 90, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=4))
    p.append(text(330, 130, "DMA Буфер MAC", size=11, color=INK, bold=True))
    p.append(text(330, 150, "Статичний масив", size=10, color=MUTED))
    p.append(text(330, 170, "eth_rx_buff[1536]", size=9.5, color=MUTED))

    p.append(arrow(415, 150, 475, 150, color=POS, sw=2))
    p.append(text(445, 138, "memcpy #1", size=9.5, color=POS, bold=True))

    p.append(rect(480, 105, 160, 90, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=4))
    p.append(text(560, 130, "Пакетний pbuf", size=11, color=INK, bold=True))
    p.append(text(560, 150, "Стек lwIP", size=10, color=MUTED))
    p.append(text(560, 170, "Черга TCP/IP", size=9.5, color=MUTED))

    p.append(arrow(645, 150, 705, 150, color=POS, sw=2))
    p.append(text(675, 138, "memcpy #2", size=9.5, color=POS, bold=True))

    p.append(rect(710, 105, 170, 90, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=4))
    p.append(text(795, 130, "Буфер Додатку", size=11, color=INK, bold=True))
    p.append(text(795, 150, "app_buffer[]", size=10, color=MUTED))
    p.append(text(795, 170, "Виклик recv()", size=9.5, color=MUTED))

    # 2. Zero-Copy підхід
    p.append(rect(40, 240, 860, 170, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(60, 265, "Оптимізована схема Zero-Copy з прямим прив'язуванням PBUF_POOL до дескрипторів DMA",
                  size=12, color=FIELD, bold=True, anchor="start"))

    p.append(rect(60, 285, 140, 105, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    p.append(text(130, 310, "Кабель Ethernet", size=11, color=INK, bold=True))
    p.append(text(130, 330, "Кадр надходить", size=10, color=MUTED))
    p.append(text(130, 350, "на PHY трансивер", size=10, color=MUTED))

    p.append(arrow(205, 337, 265, 337, color=FIELD, sw=2.2))
    p.append(text(235, 322, "DMA запис", size=9.5, color=FIELD, bold=True))

    p.append(rect(270, 285, 360, 105, fill="#ffffff", stroke="#86efac", sw=1.5, rx=4))
    p.append(text(450, 305, "PBUF_POOL Payload (Адреса в DMA дескрипторі)", size=11.5, color=FIELD, bold=True))
    p.append(text(450, 328, "• Контролер DMA пише безпосередньо у виділений pbuf", size=10, color=INK))
    p.append(text(450, 348, "• SCB_InvalidateDCache_by_Addr() узгоджує D-Cache", size=9.5, color="#047857"))
    p.append(text(450, 368, "• pbuf передається у стек lwIP зміною вказівника", size=10, color=INK))

    p.append(arrow(635, 337, 705, 337, color=FIELD, sw=2.2))
    p.append(text(670, 322, "Вказівник", size=9.5, color=FIELD, bold=True))

    p.append(rect(710, 285, 170, 105, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    p.append(text(795, 310, "Прикладний код", size=11, color=INK, bold=True))
    p.append(text(795, 330, "Пряма робота", size=10, color=FIELD, bold=True))
    p.append(text(795, 350, "з p->payload", size=10, color=INK))
    p.append(text(795, 370, "0 копіювань!", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "zerocopy-dma-pipeline.svg"), W, H, *p,
           title="Апаратний конвеєр прямого доступу до пам'яті (DMA) без дублювання даних")


if __name__ == "__main__":
    fig_memory_subsystems()
    fig_pbuf_types()
    fig_api_triad()
    fig_zerocopy_pipeline()
    print("OK: figures generated in", OUT)
