# -*- coding: utf-8 -*-
"""Фігури до теми «Система-на-кристалі (SoC)» та її вставок.
Запуск: python figs.py  → генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Спеціальна палітра для блоків SoC
C_CPU  = "#eaf0fd"   # синій для CPU
C_CPUK = "#2457d6"
C_GPU  = "#e8f7ec"   # зелений для GPU/NPU
C_GPUK = "#1e7e34"
C_MEM  = "#fdf3e7"   # помаранчевий для пам'яті/DDR
C_MEMK = "#d97706"
C_ANA  = "#fce8e6"   # червонуватий для аналогових блоків
C_ANAK = "#c0392b"
C_BUS  = "#ede9fe"   # фіолетовий для шин/NoC
C_BUSK = "#6d28d9"
C_SEC  = "#f3f4f6"   # сірий для безпеки/периферії
C_SECK = "#4b5563"


# ── d-фіг.1: Гетерогенна архітектура SoC на єдиному кристалі ─────────────────
def fig_soc_architecture():
    W, H = 760, 480
    f = [text(W / 2, 26, "Гетерогенна система-на-кристалі: ключові підсистеми на єдиному кремнії",
              size=15, bold=True)]

    # Зовнішній контур кристала (Die boundary)
    f.append(rect(30, 45, 700, 395, fill="#fafbfc", stroke=LINE, sw=2.2, rx=8))
    f.append(text(46, 64, "Кремнієвий кристал (Monolithic Die)", size=11, color=MUTED, bold=True, anchor="start"))

    # Центральна магістраль: Інтерконект / NoC
    f.append(rect(50, 205, 660, 52, fill=C_BUS, stroke=C_BUSK, sw=1.8, rx=4))
    f.append(text(380, 228, "Внутрішньокристальний інтерконект / Network-on-Chip (NoC)", size=12, color=C_BUSK, bold=True))
    f.append(text(380, 245, "Когерентна шинна матриця AMBA AXI / NoC-маршрутизатори", size=10, color=C_BUSK))

    # Верхній ярус обчислювачів: CPU, GPU, NPU, Secure Enclave
    # CPU Cluster
    f.append(rect(50, 75, 175, 115, fill=C_CPU, stroke=C_CPUK, sw=1.6, rx=4))
    f.append(text(137, 95, "CPU Кластер", size=12, color=C_CPUK, bold=True))
    f.append(rect(60, 106, 72, 36, fill="#ffffff", stroke=C_CPUK, sw=1.0, rx=3))
    f.append(text(96, 128, "Ядро 0 (Big)", size=9.5, color=INK))
    f.append(rect(142, 106, 72, 36, fill="#ffffff", stroke=C_CPUK, sw=1.0, rx=3))
    f.append(text(178, 128, "Ядро 1 (Big)", size=9.5, color=INK))
    f.append(rect(60, 146, 154, 34, fill="#ffffff", stroke=C_CPUK, sw=1.0, rx=3))
    f.append(text(137, 167, "L2 / L3 Кеш-пам'ять", size=10, color=C_CPUK))
    f.append(line(137, 190, 137, 205, color=C_BUSK, sw=2.0))

    # GPU Subsystem
    f.append(rect(235, 75, 155, 115, fill=C_GPU, stroke=C_GPUK, sw=1.6, rx=4))
    f.append(text(312, 95, "GPU Підсистема", size=12, color=C_GPUK, bold=True))
    f.append(rect(245, 106, 135, 45, fill="#ffffff", stroke=C_GPUK, sw=1.0, rx=3))
    f.append(text(312, 124, "Шейдерні ядра (SIMD)", size=9.5, color=INK))
    f.append(text(312, 141, "Растеризація та текстури", size=9, color=MUTED))
    f.append(rect(245, 155, 135, 25, fill="#ffffff", stroke=C_GPUK, sw=1.0, rx=3))
    f.append(text(312, 171, "GPU L2 Кеш", size=9.5, color=C_GPUK))
    f.append(line(312, 190, 312, 205, color=C_BUSK, sw=2.0))

    # NPU / DSP Accelerator
    f.append(rect(400, 75, 155, 115, fill=C_GPU, stroke=C_GPUK, sw=1.6, rx=4))
    f.append(text(477, 95, "Нейропроцесор (NPU)", size=12, color=C_GPUK, bold=True))
    f.append(rect(410, 106, 135, 45, fill="#ffffff", stroke=C_GPUK, sw=1.0, rx=3))
    f.append(text(477, 124, "Тензорний систолічний масив", size=9, color=INK))
    f.append(text(477, 141, "MAC-блоки (INT8/FP16)", size=9, color=MUTED))
    f.append(rect(410, 155, 135, 25, fill="#ffffff", stroke=C_GPUK, sw=1.0, rx=3))
    f.append(text(477, 171, "Локальна SRAM (TCM)", size=9, color=C_GPUK))
    f.append(line(477, 190, 477, 205, color=C_BUSK, sw=2.0))

    # Secure Enclave & Crypto
    f.append(rect(565, 75, 145, 115, fill=C_SEC, stroke=C_SECK, sw=1.6, rx=4))
    f.append(text(637, 95, "Безпечний анклав", size=11.5, color=C_SECK, bold=True))
    f.append(rect(575, 106, 125, 36, fill="#ffffff", stroke=C_SECK, sw=1.0, rx=3))
    f.append(text(637, 122, "Secure CPU", size=9.5, color=INK))
    f.append(text(637, 136, "+ Апаратний AES/SHA", size=9, color=MUTED))
    f.append(rect(575, 146, 125, 34, fill="#ffffff", stroke=C_SECK, sw=1.0, rx=3))
    f.append(text(637, 161, "Secure Boot ROM", size=9, color=INK))
    f.append(text(637, 174, "+ eFuse ключі", size=9, color=MUTED))
    f.append(line(637, 190, 637, 205, color=C_BUSK, sw=2.0))

    # Нижній ярус: Пам'ять, Аналог/PLL/PMIC, Швидкісні SerDes, Периферія
    # Системний кеш SLC та DDR Controller
    f.append(rect(50, 270, 200, 155, fill=C_MEM, stroke=C_MEMK, sw=1.6, rx=4))
    f.append(text(150, 290, "Підсистема пам'яті", size=12, color=C_MEMK, bold=True))
    f.append(rect(60, 300, 180, 34, fill="#ffffff", stroke=C_MEMK, sw=1.0, rx=3))
    f.append(text(150, 316, "Системний кеш (SLC)", size=9.5, color=INK))
    f.append(text(150, 329, "Загальний буфер (16–64 МБ)", size=9, color=MUTED))
    f.append(rect(60, 340, 180, 38, fill="#ffffff", stroke=C_MEMK, sw=1.0, rx=3))
    f.append(text(150, 356, "Контролер LPDDR5 / DDR5", size=9.5, color=INK))
    f.append(text(150, 371, "Планувальник запитів + черги", size=9, color=MUTED))
    f.append(rect(60, 384, 180, 32, fill="#faead6", stroke=C_MEMK, sw=1.2, rx=3))
    f.append(text(150, 404, "DDR PHY (Аналогові лінії IO)", size=9.5, color=C_MEMK, bold=True))
    f.append(line(150, 257, 150, 270, color=C_BUSK, sw=2.0))

    # Аналогові та радіочастотні блоки (Mixed-Signal)
    f.append(rect(260, 270, 175, 155, fill=C_ANA, stroke=C_ANAK, sw=1.6, rx=4))
    f.append(text(347, 290, "Аналог, PLL та живлення", size=11.5, color=C_ANAK, bold=True))
    f.append(rect(270, 300, 155, 34, fill="#ffffff", stroke=C_ANAK, sw=1.0, rx=3))
    f.append(text(347, 316, "Тактові генератори (PLL)", size=9.5, color=INK))
    f.append(text(347, 329, "Синтез частот для ядер", size=9, color=MUTED))
    f.append(rect(270, 340, 155, 34, fill="#ffffff", stroke=C_ANAK, sw=1.0, rx=3))
    f.append(text(347, 356, "АЦП / ЦАП (ADC / DAC)", size=9.5, color=INK))
    f.append(text(347, 369, "Сенсори температури й напруг", size=9, color=MUTED))
    f.append(rect(270, 380, 155, 36, fill="#ffffff", stroke=C_ANAK, sw=1.0, rx=3))
    f.append(text(347, 396, "Керування живленням", size=9.5, color=INK))
    f.append(text(347, 409, "PMIC інтерфейс, LDO", size=9, color=MUTED))
    f.append(line(347, 257, 347, 270, color=C_BUSK, sw=2.0))

    # Високошвидкісні інтерфейси (High-Speed IO)
    f.append(rect(445, 270, 130, 155, fill=C_SEC, stroke=C_SECK, sw=1.6, rx=4))
    f.append(text(510, 290, "Швидкісні IO", size=11.5, color=C_SECK, bold=True))
    f.append(rect(455, 304, 110, 32, fill="#ffffff", stroke=C_SECK, sw=1.0, rx=3))
    f.append(text(510, 324, "PCIe Gen4 / Gen5", size=9.5, color=INK))
    f.append(rect(455, 342, 110, 32, fill="#ffffff", stroke=C_SECK, sw=1.0, rx=3))
    f.append(text(510, 362, "USB4 / Thunderbolt", size=9.5, color=INK))
    f.append(rect(455, 380, 110, 35, fill="#e5e7eb", stroke=C_SECK, sw=1.0, rx=3))
    f.append(text(510, 396, "SerDes PHY", size=9.5, color=C_SECK, bold=True))
    f.append(text(510, 409, "Диференційні пари", size=9, color=MUTED))
    f.append(line(510, 257, 510, 270, color=C_BUSK, sw=2.0))

    # Низькошвидкісна периферія (Low-Speed IO)
    f.append(rect(585, 270, 125, 155, fill=C_SEC, stroke=C_SECK, sw=1.6, rx=4))
    f.append(text(647, 290, "Периферія", size=11.5, color=C_SECK, bold=True))
    f.append(rect(595, 304, 105, 26, fill="#ffffff", stroke=C_SECK, sw=1.0, rx=3))
    f.append(text(647, 321, "UART / SPI / I2C", size=9.5, color=INK))
    f.append(rect(595, 336, 105, 26, fill="#ffffff", stroke=C_SECK, sw=1.0, rx=3))
    f.append(text(647, 353, "GPIO / Таймери", size=9.5, color=INK))
    f.append(rect(595, 368, 105, 26, fill="#ffffff", stroke=C_SECK, sw=1.0, rx=3))
    f.append(text(647, 385, "SD / eMMC", size=9.5, color=INK))
    f.append(rect(595, 400, 105, 20, fill="#ffffff", stroke=C_SECK, sw=1.0, rx=3))
    f.append(text(647, 414, "JTAG / DFT", size=9, color=MUTED))
    f.append(line(647, 257, 647, 270, color=C_BUSK, sw=2.0))

    f.append(text(W / 2, H - 12, "Усі функціональні вузли інтегровано на єдиній кремнієвій підкладці та зв'язано швидкісною мережею NoC",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "soc-architecture.svg"), W, H, *f)


# ── d-фіг.2: Ієрархія інтерконекту: NoC / AXI crossbar → AHB → APB ───────────
def fig_interconnect_hierarchy():
    W, H = 760, 420
    f = [text(W / 2, 26, "Ієрархія з'єднань SoC: високошвидкісна NoC / AXI-матриця та периферійні мости",
              size=15, bold=True)]

    # Рівень 1: Високопродуктивні майстри (CPU, GPU, DMA)
    masters = [
        (90, 80, 120, 50, "CPU Кластер", "AMBA AXI Master", C_CPU, C_CPUK),
        (230, 80, 120, 50, "GPU / NPU", "AMBA AXI Master", C_GPU, C_GPUK),
        (370, 80, 120, 50, "DMA Контролер", "AMBA AXI Master", C_SEC, C_SECK),
        (510, 80, 120, 50, "PCIe Root Complex", "AMBA AXI Master", C_SEC, C_SECK),
    ]
    for x, y, w, h, t1, t2, col, ck in masters:
        f.append(rect(x, y, w, h, fill=col, stroke=ck, sw=1.5, rx=4))
        f.append(text(x + w / 2, y + 20, t1, size=11, color=ck, bold=True))
        f.append(text(x + w / 2, y + 38, t2, size=9.5, color=MUTED))
        f.append(line(x + w / 2, y + h, x + w / 2, 160, color=C_BUSK, sw=1.8))

    # Рівень 2: Високошвидкісний інтерконект (AXI Crossbar / NoC)
    f.append(rect(50, 160, 660, 60, fill=C_BUS, stroke=C_BUSK, sw=2.0, rx=6))
    f.append(text(380, 185, "AXI Crossbar Interconnect / 2D Mesh Network-on-Chip", size=13, color=C_BUSK, bold=True))
    f.append(text(380, 204, "Роздільні канали адрес, даних і відповідей · Позачергове виконання (AXI ID) · До 1 ТБ/с", size=10, color=INK))

    # Стрілки вниз до швидкісних слейвів і мостів
    # Швидкісний слейв 1: Пам'ять
    f.append(line(180, 220, 180, 255, color=C_BUSK, sw=2.0))
    f.append(rect(100, 255, 160, 50, fill=C_MEM, stroke=C_MEMK, sw=1.6, rx=4))
    f.append(text(180, 275, "Контролер пам'яті DDR", size=11, color=C_MEMK, bold=True))
    f.append(text(180, 293, "AXI Slave · Мульти-ранк", size=9.5, color=MUTED))

    # Швидкісний слейв 2: Вбудована SRAM
    f.append(line(360, 220, 360, 255, color=C_BUSK, sw=2.0))
    f.append(rect(280, 255, 160, 50, fill=C_MEM, stroke=C_MEMK, sw=1.6, rx=4))
    f.append(text(360, 275, "Внутрішня SRAM (TCM)", size=11, color=C_MEMK, bold=True))
    f.append(text(360, 293, "Низька латентність (1-2 такти)", size=9.5, color=MUTED))

    # Міст AXI-to-APB
    f.append(line(570, 220, 570, 255, color=C_BUSK, sw=2.0))
    f.append(rect(480, 255, 180, 50, fill="#fef3c7", stroke="#b45309", sw=1.6, rx=4))
    f.append(text(570, 275, "Міст AXI-to-APB", size=11.5, color="#b45309", bold=True))
    f.append(text(570, 293, "Узгодження частот і протоколів", size=9.5, color=MUTED))

    # Рівень 3: Периферійна шина APB
    f.append(line(570, 305, 570, 335, color="#b45309", sw=2.0))
    f.append(rect(400, 335, 320, 26, fill="#fef3c7", stroke="#b45309", sw=1.4, rx=4))
    f.append(text(560, 352, "Периферійна шина AMBA APB (Low Power / 2-phase)", size=10, color="#92400e", bold=True))

    # Периферійні слейви
    periphs = [
        (410, 375, 65, 30, "UART"),
        (490, 375, 65, 30, "I2C/SPI"),
        (570, 375, 65, 30, "Таймери"),
        (650, 375, 65, 30, "GPIO"),
    ]
    for px, py, pw, ph, plab in periphs:
        f.append(line(px + pw / 2, 361, px + pw / 2, py, color="#b45309", sw=1.4))
        f.append(rect(px, py, pw, ph, fill="#ffffff", stroke="#92400e", sw=1.0, rx=3))
        f.append(text(px + pw / 2, py + 19, plab, size=9.5, color=INK))

    f.append(text(W / 2, H - 6, "Швидкісні пристрої не блокують повільні: мости ізолюють трафік і транслюють транзакції",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "interconnect-hierarchy.svg"), W, H, *f)


# ── d-фіг.3: Мультидоменне живлення, Power Gating, DVFS та граничні комірки ──
def fig_power_domains_dvfs():
    W, H = 760, 430
    f = [text(W / 2, 26, "Мультидоменне живлення: ізоляція, перетворювачі рівнів та збереження стану",
              size=15, bold=True)]

    # ЛІВОРУЧ: Домен процесора (Switchable Power Domain / Voltage Island)
    f.append(rect(40, 60, 320, 290, fill="#f8fafc", stroke=C_CPUK, sw=1.8, rx=6))
    f.append(text(200, 82, "Комутований домен живлення (CPU Domain)", size=11.5, color=C_CPUK, bold=True))
    f.append(text(200, 98, "Напруга Vdd_cpu = 0.65 ... 1.05 В (DVFS)", size=10, color=MUTED))

    # Ключ живлення (Power Switch / Sleep PMOS Transistor)
    f.append(rect(60, 115, 280, 42, fill="#fee2e2", stroke=C_ANAK, sw=1.4, rx=4))
    f.append(text(200, 133, "Ключі живлення (Power Gating Header PMOS)", size=10.5, color=C_ANAK, bold=True))
    f.append(text(200, 149, "Послідовне ланцюжкове вмикання проти стрибка струму dI/dt", size=9, color=MUTED))

    # Логіка всередині домену
    f.append(rect(60, 170, 130, 90, fill="#ffffff", stroke=C_CPUK, sw=1.2, rx=4))
    f.append(text(125, 192, "Комбінаторна", size=10, color=INK, bold=True))
    f.append(text(125, 208, "логіка та АЛП", size=10, color=INK))
    f.append(text(125, 235, "Знеструмлюється", size=9, color=C_ANAK))
    f.append(text(125, 249, "при сні", size=9, color=C_ANAK))

    # Ретеншн-тригери (Retention Flip-Flops)
    f.append(rect(205, 170, 135, 90, fill="#eff6ff", stroke=C_CPUK, sw=1.2, rx=4))
    f.append(text(272, 192, "Retention Flip-Flops", size=10, color=C_CPUK, bold=True))
    f.append(text(272, 210, "Зберігають стан", size=9.5, color=INK))
    f.append(text(272, 225, "регістрів ядра", size=9.5, color=INK))
    f.append(rect(215, 238, 115, 16, fill="#dbeafe", stroke=C_CPUK, sw=0.8, rx=2))
    f.append(text(272, 250, "Резервна шина Vdd_ret", size=9, color=C_CPUK))

    # Граничні комірки на стику доменів
    f.append(rect(60, 275, 135, 60, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    f.append(text(127, 295, "Isolation Cells", size=10.5, color="#d97706", bold=True))
    f.append(text(127, 312, "Фіксація сигналів", size=9.5, color=INK))
    f.append(text(127, 326, "у «0» або «1» при сні", size=9, color=MUTED))

    f.append(rect(205, 275, 135, 60, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    f.append(text(272, 295, "Level Shifters", size=10.5, color="#d97706", bold=True))
    f.append(text(272, 312, "Узгодження напруг", size=9.5, color=INK))
    f.append(text(272, 326, "0.75 В ↔ 1.8 В / 0.9 В", size=9, color=MUTED))

    # Стрілка взаємодії між доменами
    f.append(arrow(360, 205, 410, 205, color=C_BUSK, sw=2.0))
    f.append(arrow(410, 225, 360, 225, color=C_BUSK, sw=2.0))

    # ПРАВОРУЧ: Постійно увімкнений домен (Always-On Domain / AON)
    f.append(rect(410, 60, 310, 290, fill="#f0fdf4", stroke=C_GPUK, sw=1.8, rx=6))
    f.append(text(565, 82, "Завжди увімкнений домен (Always-On / AON)", size=11.5, color=C_GPUK, bold=True))
    f.append(text(565, 98, "Незмінна напруга Vdd_aon = 0.9 В / 1.8 В", size=10, color=MUTED))

    f.append(rect(430, 115, 270, 50, fill="#ffffff", stroke=C_GPUK, sw=1.2, rx=4))
    f.append(text(565, 135, "Power Management Controller (PMC / PPU)", size=10.5, color=C_GPUK, bold=True))
    f.append(text(565, 152, "Скінченний автомат послідовності живлення", size=9, color=MUTED))

    f.append(rect(430, 175, 270, 48, fill="#ffffff", stroke=C_GPUK, sw=1.2, rx=4))
    f.append(text(565, 195, "Монітор подій пробудження (Wake-up Logic)", size=10.5, color=INK, bold=True))
    f.append(text(565, 211, "Обробка переривань таймера, RTC, переферії", size=9, color=MUTED))

    f.append(rect(430, 233, 270, 48, fill="#ffffff", stroke=C_GPUK, sw=1.2, rx=4))
    f.append(text(565, 253, "Інтерфейс регулятора напруг (I2C/PMBus/SPMI)", size=10, color=INK, bold=True))
    f.append(text(565, 269, "Команди на зовнішній або вбудований PMIC", size=9, color=MUTED))

    f.append(rect(430, 290, 270, 45, fill="#ffffff", stroke=C_GPUK, sw=1.2, rx=4))
    f.append(text(565, 308, "Годинник реального часу (RTC) + генератор (32 кГц)", size=9, color=INK))

    # Нижній висновок
    f.append(text(W / 2, 375, "Без ізоляційних комірок знеструмлений блок залишив би входи AON у «підвішеному» стані,",
                  size=11, color=INK))
    f.append(text(W / 2, 393, "що спричинило б наскрізні струми короткого замикання (shoot-through) і вихід мікросхеми з ладу.",
                  size=10.5, color=MUTED))
    render(os.path.join(IMG, "power-domains-dvfs.svg"), W, H, *f)


# ── d-фіг.4: Тактове дерево (CTS) та стробування такту (ICG) ─────────────────
def fig_clock_distribution_cts():
    W, H = 760, 410
    f = [text(W / 2, 26, "Синтез тактового дерева (CTS) та стробування такту (Clock Gating)",
              size=15, bold=True)]

    # ЛІВОРУЧ: Генератор PLL і корінь дерева
    f.append(rect(40, 70, 130, 65, fill=C_ANA, stroke=C_ANAK, sw=1.6, rx=4))
    f.append(text(105, 94, "PLL Синтезатор", size=11, color=C_ANAK, bold=True))
    f.append(text(105, 112, "f = 24 МГц → 3 ГГц", size=9.5, color=MUTED))
    f.append(text(105, 126, "Низький jitter", size=9, color=MUTED))

    # Стрілка до кореня H-дерева
    f.append(line(170, 102, 210, 102, color=INK, sw=2.0))
    f.append(circle(210, 102, 4, fill=INK, stroke=INK, sw=0))
    f.append(text(210, 88, "Root Clock", size=9.5, color=MUTED))

    # H-дерево (Симметричне розведення для мінімізації Clock Skew)
    # Перший рівень
    f.append(line(210, 102, 250, 102, color=INK, sw=2.0))
    f.append(line(250, 60, 250, 160, color=INK, sw=2.0))
    # Буфери на гілках
    f.append(rect(243, 95, 14, 14, fill="#ffffff", stroke=INK, sw=1.2))
    # Другий рівень (верх)
    f.append(line(250, 60, 310, 60, color=INK, sw=1.8))
    f.append(line(310, 42, 310, 82, color=INK, sw=1.8))
    # Другий рівень (низ)
    f.append(line(250, 160, 310, 160, color=INK, sw=1.8))
    f.append(line(310, 142, 310, 182, color=INK, sw=1.8))

    # Кінцеві точки дерева зі збалансованою затримкою
    f.append(arrow(310, 42, 350, 42, color=INK, sw=1.6))
    f.append(arrow(310, 82, 350, 82, color=INK, sw=1.6))
    f.append(arrow(310, 142, 350, 142, color=INK, sw=1.6))
    f.append(arrow(310, 182, 350, 182, color=INK, sw=1.6))

    f.append(text(280, 215, "Синтез H-дерева вирівнює затримки:", size=10.5, color=INK, bold=True))
    f.append(text(280, 232, "Clock Skew = t_clk2 − t_clk1 ≈ 0 пс", size=10, color=C_CPUK))

    # ПРАВОРУЧ: Комірка інтегрованого тактового стробування (ICG Cell)
    f.append(rect(370, 50, 350, 240, fill="#f8fafc", stroke=C_CPUK, sw=1.8, rx=6))
    f.append(text(545, 72, "Комірка тактового стробування (Integrated Clock Gating, ICG)", size=11, color=C_CPUK, bold=True))

    # Latch (засувка для уникнення глітчів)
    f.append(rect(390, 100, 100, 60, fill="#eff6ff", stroke=C_CPUK, sw=1.4, rx=4))
    f.append(text(440, 122, "Latch (Засувка)", size=10.5, color=C_CPUK, bold=True))
    f.append(text(440, 140, "Прозора при CLK=0", size=9, color=MUTED))
    f.append(text(440, 153, "Замикає при CLK=1", size=9, color=MUTED))

    # Сигнал Enable
    f.append(line(350, 120, 390, 120, color=C_GPUK, sw=1.8))
    f.append(text(345, 115, "Enable", size=9.5, color=C_GPUK, anchor="end", bold=True))

    # Тактовий сигнал на засувку
    f.append(line(350, 148, 390, 148, color=INK, sw=1.6))
    f.append(text(345, 152, "CLK_in", size=9.5, color=INK, anchor="end"))

    # Вентиль AND
    f.append(line(490, 120, 530, 120, color=INK, sw=1.8))
    f.append(line(370, 195, 510, 195, color=INK, sw=1.6))
    f.append(line(510, 195, 530, 140, color=INK, sw=1.6))

    # Полігон AND
    f.append('<polygon points="530,110 560,110 575,130 560,150 530,150" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % ("#dbeafe", C_CPUK))
    f.append(text(548, 134, "AND", size=10, color=C_CPUK, bold=True))

    # Вихід Gated CLK
    f.append(arrow(575, 130, 625, 130, color=C_CPUK, sw=2.0))
    f.append(text(630, 134, "Gated_CLK", size=10.5, color=C_CPUK, anchor="start", bold=True))

    # Ряд регістрів споживачів
    f.append(rect(630, 160, 80, 40, fill="#ffffff", stroke=INK, sw=1.2, rx=3))
    f.append(text(670, 184, "Регістри", size=9.5, color=INK))
    f.append(line(615, 130, 615, 180, color=C_CPUK, sw=1.6))
    f.append(arrow(615, 180, 630, 180, color=C_CPUK, sw=1.6))

    f.append(text(545, 260, "Засувка блокує перемикання сигналу Enable під час високого рівня CLK,",
                  size=9.5, color=INK))
    f.append(text(545, 276, "що повністю виключає появу небезпечних паразитних імпульсів (glitches).",
                  size=9.5, color=MUTED))

    # Загальний підпис унизу
    f.append(text(W / 2, 335, "Clock gating вимикає динамічне перезаряджання ємностей P = C·V²·f у простійних функціональних блоках,",
                  size=11, color=INK))
    f.append(text(W / 2, 355, "економлячи до 30–50% динамічної потужності кристала без втрати стану регістрів.",
                  size=10.5, color=MUTED))
    render(os.path.join(IMG, "clock-distribution-cts.svg"), W, H, *f)


# ── d-фіг.5: Методологія тестування (DFT): JTAG, IEEE 1500, Scan-ланцюги, BIST 
def fig_dft_bist_jtag():
    W, H = 760, 420
    f = [text(W / 2, 26, "Тестування складного кристала (DFT): JTAG, IEEE 1500 обгортки та BIST",
              size=15, bold=True)]

    # Контур чіпа з JTAG портами
    f.append(rect(40, 55, 680, 325, fill="#fbfcfd", stroke=LINE, sw=2.0, rx=8))
    f.append(text(55, 75, "SoC Die Boundary & Test Infrastructure", size=11, color=MUTED, bold=True, anchor="start"))

    # JTAG Контролер TAP (Test Access Port)
    f.append(rect(60, 95, 140, 130, fill=C_SEC, stroke=C_SECK, sw=1.6, rx=4))
    f.append(text(130, 118, "JTAG TAP", size=12, color=C_SECK, bold=True))
    f.append(text(130, 134, "IEEE 1149.1", size=10, color=MUTED))
    jtag_pins = ["TCK (Такт)", "TMS (Режим)", "TDI (Вхід)", "TDO (Вихід)"]
    for i, pin in enumerate(jtag_pins):
        f.append(text(72, 156 + i * 16, "• " + pin, size=9.5, color=INK, anchor="start"))

    # IEEE 1500 Wrapper навколо IP Core 1 (CPU / Logic)
    f.append(rect(230, 95, 230, 160, fill="#f0fdf4", stroke=C_GPUK, sw=1.6, rx=6))
    f.append(text(345, 115, "IP-блок (CPU) в IEEE 1500 Wrapper", size=11, color=C_GPUK, bold=True))
    # Scan Chain всередині
    f.append(rect(245, 130, 200, 50, fill="#ffffff", stroke=C_GPUK, sw=1.2, rx=4))
    f.append(text(345, 150, "Внутрішні Scan-ланцюги (ATPG)", size=10, color=INK, bold=True))
    f.append(text(345, 168, "Послідовний зсув векторів перевірки логіки", size=9, color=MUTED))
    # Logic BIST
    f.append(rect(245, 190, 200, 50, fill="#dcfce7", stroke=C_GPUK, sw=1.2, rx=4))
    f.append(text(345, 210, "Logic BIST (LBIST)", size=10, color=C_GPUK, bold=True))
    f.append(text(345, 228, "Автономний генератор LFSR + MISR сигнатура", size=9, color=MUTED))

    # IEEE 1500 Wrapper навколо IP Core 2 (SRAM / Пам'ять)
    f.append(rect(480, 95, 220, 160, fill="#eff6ff", stroke=C_CPUK, sw=1.6, rx=6))
    f.append(text(590, 115, "SRAM Кеш в IEEE 1500 Wrapper", size=11, color=C_CPUK, bold=True))
    # Memory BIST
    f.append(rect(495, 130, 190, 55, fill="#ffffff", stroke=C_CPUK, sw=1.2, rx=4))
    f.append(text(590, 150, "Memory BIST (MBIST)", size=10.5, color=C_CPUK, bold=True))
    f.append(text(590, 168, "Апаратний алгоритм March C−", size=9.5, color=INK))
    f.append(text(590, 180, "Тест на частоті пам'яті (At-Speed)", size=9, color=MUTED))
    # Redundancy & Repair
    f.append(rect(495, 195, 190, 45, fill="#dbeafe", stroke=C_CPUK, sw=1.2, rx=4))
    f.append(text(590, 213, "eFuse Repair / Заміна рядків", size=9.5, color=C_CPUK, bold=True))
    f.append(text(590, 228, "Підміна битих комірок резервними", size=9, color=MUTED))

    # Магістраль тестових інструкцій та даних від TAP до обгорток
    f.append(line(200, 160, 230, 160, color=C_SECK, sw=1.8))
    f.append(line(460, 160, 480, 160, color=C_SECK, sw=1.8))

    # Нижня частина: Boundary Scan на зовнішніх виводах чіпа
    f.append(rect(60, 275, 640, 85, fill="#fef3c7", stroke="#d97706", sw=1.6, rx=6))
    f.append(text(380, 295, "Граничне сканування (Boundary Scan Register / JTAG Cells на кожному виводі IO)",
                  size=11.5, color="#d97706", bold=True))
    f.append(text(380, 315, "Дозволяє перевірити цілісність пайки BGA-кульок та друкованої плати без фізичних зондів",
                  size=10, color=INK))
    f.append(text(380, 335, "Ізолює ядро від зовнішніх контактів під час внутрішніх тестів INTEST та зовнішніх EXTEST",
                  size=9.5, color=MUTED))

    f.append(text(W / 2, H - 10, "DFT перетворює мільярди закритих транзисторів на прозору та спостережувану систему",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "dft-bist-jtag.svg"), W, H, *f)


# ── comp-фіг.1: 5 незалежних каналів AXI4 та двостороннє рукостискання ────────
def fig_axi_channels():
    W, H = 760, 420
    f = [text(W / 2, 26, "5 незалежних каналів протоколу AXI4 та квитування VALID / READY",
              size=15, bold=True)]

    # ЛІВОРУЧ: 5 каналів AXI Master ↔ Slave
    f.append(rect(30, 60, 110, 240, fill=C_CPU, stroke=C_CPUK, sw=1.6, rx=4))
    f.append(text(85, 180, "AXI Master", size=12, color=C_CPUK, bold=True))

    f.append(rect(340, 60, 110, 240, fill=C_MEM, stroke=C_MEMK, sw=1.6, rx=4))
    f.append(text(395, 180, "AXI Slave", size=12, color=C_MEMK, bold=True))

    channels = [
        (80, "Read Address (AR)", "ARADDR, ARLEN, ARID", C_CPUK, True),
        (125, "Read Data (R)", "RDATA, RRESP, RID", C_MEMK, False),
        (170, "Write Address (AW)", "AWADDR, AWLEN, AWID", C_CPUK, True),
        (215, "Write Data (W)", "WDATA, WSTRB, WLAST", C_CPUK, True),
        (260, "Write Response (B)", "BRESP, BID", C_MEMK, False),
    ]
    for cy, cname, csig, col, is_fwd in channels:
        f.append(rect(150, cy - 14, 180, 28, fill="#ffffff", stroke=col, sw=1.2, rx=3))
        f.append(text(240, cy - 2, cname, size=9.5, color=col, bold=True))
        f.append(text(240, cy + 9, csig, size=9, color=MUTED))
        if is_fwd:
            f.append(arrow(140, cy, 150, cy, color=col, sw=1.4))
            f.append(arrow(330, cy, 340, cy, color=col, sw=1.4))
        else:
            f.append(arrow(340, cy, 330, cy, color=col, sw=1.4))
            f.append(arrow(150, cy, 140, cy, color=col, sw=1.4))

    # ПРАВОРУЧ: Часова діаграма рукостискання (Handshake VALID/READY)
    f.append(rect(470, 60, 260, 240, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    f.append(text(600, 80, "Двосторонній Handshake", size=11.5, color=INK, bold=True))

    # Такти T1, T2, T3, T4
    for i, tname in enumerate(["T1", "T2", "T3 (Transfer)", "T4"]):
        tx = 520 + i * 50
        f.append(text(tx, 102, tname, size=9, color=MUTED))
        f.append(line(tx, 110, tx, 260, color="#e2e8f0", sw=1.0, dash="2 2"))

    # CLK
    f.append(text(485, 125, "ACLK", size=9.5, color=INK, bold=True))
    f.append('<polyline points="505,130 520,130 520,118 545,118 545,130 570,130 570,118 595,118 595,130 620,130 620,118 645,118 645,130 670,130" fill="none" stroke="%s" stroke-width="1.4"/>' % INK)

    # VALID (піднімається джерелом на T2 і тримається)
    f.append(text(485, 160, "VALID", size=9.5, color=C_CPUK, bold=True))
    f.append('<polyline points="505,168 535,168 540,152 645,152 650,168 670,168" fill="none" stroke="%s" stroke-width="1.8"/>' % C_CPUK)

    # READY (піднімається приймачем на T3)
    f.append(text(485, 195, "READY", size=9.5, color=C_MEMK, bold=True))
    f.append('<polyline points="505,203 585,203 590,188 645,188 650,203 670,203" fill="none" stroke="%s" stroke-width="1.8"/>' % C_MEMK)

    # DATA
    f.append(text(485, 235, "DATA", size=9.5, color=INK, bold=True))
    f.append(rect(540, 225, 105, 20, fill="#dbeafe", stroke=C_CPUK, sw=1.2, rx=2))
    f.append(text(592, 239, "Дійсні дані", size=9.5, color=C_CPUK, bold=True))

    # Позначка транзакції
    f.append(circle(620, 130, 4, fill=POS, stroke=POS, sw=0))
    f.append(text(600, 275, "Передавання стається ТОЧНО в такт T3,", size=9, color=POS, bold=True))
    f.append(text(600, 288, "коли одночасно VALID=1 та READY=1", size=9, color=POS))

    # Нижній висновок
    f.append(text(W / 2, 335, "Роздільні канали читання й запису працюють повністю асинхронно та паралельно,",
                  size=11, color=INK))
    f.append(text(W / 2, 355, "а ідентифікатори транзакцій (AXI ID) дозволяють повертати дані без очікування попередніх запитів.",
                  size=10.5, color=MUTED))
    render(os.path.join(IMG, "axi-channels.svg"), W, H, *f)


# ── math-фіг.1: Топологія 2D Mesh NoC, маршрутизація XY та пакети/фліти ───────
def fig_noc_mesh_routing():
    W, H = 760, 420
    f = [text(W / 2, 26, "Топологія 2D Mesh Network-on-Chip: розбиття на фліти та маршрутизація XY",
              size=15, bold=True)]

    # ЛІВОРУЧ: 3x3 NoC Mesh
    f.append(rect(30, 55, 360, 310, fill="#f8fafc", stroke=LINE, sw=1.6, rx=6))
    f.append(text(210, 75, "2D Mesh NoC (3×3 Grid)", size=12, color=INK, bold=True))

    # Вузли сітки (Router + IP Core)
    nodes = [
        (0, 0, 70, 100, "Node (0,0)\n[Джерело]", True),
        (1, 0, 180, 100, "Node (1,0)", False),
        (2, 0, 290, 100, "Node (2,0)", False),
        (0, 1, 70, 190, "Node (0,1)", False),
        (1, 1, 180, 190, "Node (1,1)", False),
        (2, 1, 290, 190, "Node (2,1)", False),
        (0, 2, 70, 280, "Node (0,2)", False),
        (1, 2, 180, 280, "Node (1,2)", False),
        (2, 2, 290, 280, "Node (2,2)\n[Приймач]", True),
    ]

    # Горизонтальні та вертикальні зв'язки
    for r in range(3):
        f.append(line(125, 120 + r * 90, 180, 120 + r * 90, color=MUTED, sw=2.0))
        f.append(line(235, 120 + r * 90, 290, 120 + r * 90, color=MUTED, sw=2.0))
    for c in range(3):
        f.append(line(97 + c * 110, 142, 97 + c * 110, 190, color=MUTED, sw=2.0))
        f.append(line(97 + c * 110, 232, 97 + c * 110, 280, color=MUTED, sw=2.0))

    # Шлях маршрутизації XY: (0,0) → (1,0) → (2,0) → (2,1) → (2,2)
    path_pts = [(97, 120), (207, 120), (317, 120), (317, 210), (317, 300)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="4.0" stroke-linecap="round"/>'
             % (" ".join("%d,%d" % p for p in path_pts), POS))
    f.append(text(210, 110, "1. Спочатку по X", size=9.5, color=POS, bold=True))
    f.append(text(340, 250, "2. Потім по Y", size=9.5, color=POS, bold=True))

    for col_idx, row_idx, nx, ny, nlab, is_hl in nodes:
        bg_col = "#fee2e2" if is_hl else "#ffffff"
        bd_col = POS if is_hl else C_BUSK
        f.append(rect(nx - 27, ny - 20, 54, 42, fill=bg_col, stroke=bd_col, sw=1.4, rx=3))
        lines = nlab.split("\n")
        f.append(text(nx, ny - 2, lines[0], size=9, color=INK, bold=is_hl))
        if len(lines) > 1:
            f.append(text(nx, ny + 12, lines[1], size=9, color=POS, bold=True))

    # ПРАВОРУЧ: Структура Пакета та Флітів (Flits)
    f.append(rect(410, 55, 320, 310, fill="#f8fafc", stroke=LINE, sw=1.6, rx=6))
    f.append(text(570, 75, "Червоточинна комутація (Wormhole)", size=12, color=INK, bold=True))

    # Загальний пакет
    f.append(rect(430, 95, 280, 45, fill="#ede9fe", stroke=C_BUSK, sw=1.4, rx=4))
    f.append(text(570, 114, "Мережевий пакет (Packet: L_pkt біт)", size=10.5, color=C_BUSK, bold=True))
    f.append(text(570, 130, "Розбивається на F = ⌈L_pkt / W⌉ флітів", size=9.5, color=MUTED))

    # Фліти
    flits = [
        (430, 155, 280, 36, "Head Flit (Голова)", "Містить адресу призначення (x_d, y_d) · Резервує шлях", "#fee2e2", POS),
        (430, 198, 280, 36, "Body Flit 1..N (Тіло)", "Несе корисне навантаження · Рухається слідом без буферизації", "#eff6ff", C_CPUK),
        (430, 241, 280, 36, "Tail Flit (Хвіст)", "Замикає пакет · Звільняє віртуальний канал і ресурси маршрутизатора", "#f0fdf4", C_GPUK),
    ]
    for fx, fy, fw, fh, ftitle, fsub, fcol, fck in flits:
        f.append(rect(fx, fy, fw, fh, fill=fcol, stroke=fck, sw=1.2, rx=3))
        f.append(text(fx + fw / 2, fy + 15, ftitle, size=9.5, color=fck, bold=True))
        f.append(text(fx + fw / 2, fy + 29, fsub, size=9, color=MUTED))

    f.append(rect(430, 290, 280, 60, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    f.append(text(570, 308, "Латентність без завантаження:", size=9.5, color=INK, bold=True))
    f.append(text(570, 325, "T_zero = H · t_r + (H + F − 1) · t_w", size=10.5, color=C_BUSK, bold=True))
    f.append(text(570, 342, "H = хопи (Manhattan), t_r = такти роутера, F = кількість флітів", size=9, color=MUTED))

    f.append(text(W / 2, H - 12, "Маршрутизація XY детермінована й позбавлена тупиків (deadlock-free) завдяки суворому порядку осей",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "noc-mesh-routing.svg"), W, H, *f)


# ── proj-фіг.1: Скінченний автомат керування живленням та послідовність DVFS ──
def fig_dvfs_state_machine():
    W, H = 760, 410
    f = [text(W / 2, 26, "Скінченний автомат керування доменом живлення (PPU/PMC FSM) та DVFS",
              size=15, bold=True)]

    # Стан 1: OFF
    f.append(rect(40, 70, 140, 70, fill="#f1f5f9", stroke=MUTED, sw=1.6, rx=6))
    f.append(text(110, 95, "POWER_OFF", size=12, color=MUTED, bold=True))
    f.append(text(110, 114, "Ключі розімкнені", size=9.5, color=INK))
    f.append(text(110, 128, "Ізоляція активна", size=9, color=MUTED))

    # Перехід 1 -> 2
    f.append(arrow(180, 105, 230, 105, color=C_BUSK, sw=1.8))
    f.append(text(205, 95, "Power Up", size=9, color=C_BUSK, bold=True))

    # Стан 2: POWERING_ON (Послідовне ланцюжкове вмикання)
    f.append(rect(230, 70, 150, 70, fill="#fee2e2", stroke=C_ANAK, sw=1.6, rx=6))
    f.append(text(305, 95, "POWERING_ON", size=11.5, color=C_ANAK, bold=True))
    f.append(text(305, 114, "Ланцюгове ввімкнення", size=9, color=INK))
    f.append(text(305, 128, "PMOS-ключів (dI/dt)", size=9, color=MUTED))

    # Перехід 2 -> 3
    f.append(arrow(380, 105, 430, 105, color=C_BUSK, sw=1.8))
    f.append(text(405, 95, "Pwr Good", size=9, color=C_BUSK, bold=True))

    # Стан 3: RESTORING (Зняття ізоляції та відновлення ретеншн)
    f.append(rect(430, 70, 145, 70, fill="#fef3c7", stroke="#d97706", sw=1.6, rx=6))
    f.append(text(502, 95, "RESTORING", size=11.5, color="#d97706", bold=True))
    f.append(text(502, 114, "Деактивація ізоляції", size=9, color=INK))
    f.append(text(502, 128, "Відновлення Retention", size=9, color=MUTED))

    # Перехід 3 -> 4
    f.append(arrow(575, 105, 620, 105, color=C_BUSK, sw=1.8))
    f.append(text(597, 95, "Reset Off", size=9, color=C_BUSK, bold=True))

    # Стан 4: ACTIVE
    f.append(rect(620, 70, 100, 70, fill="#dcfce7", stroke=C_GPUK, sw=1.8, rx=6))
    f.append(text(670, 95, "ACTIVE", size=12, color=C_GPUK, bold=True))
    f.append(text(670, 114, "CLK увімкнено", size=9, color=INK))
    f.append(text(670, 128, "Ядро працює", size=9, color=C_GPUK))

    # Зворотний шлях (Power Down)
    f.append(line(670, 140, 670, 175, color=MUTED, sw=1.6))
    f.append(line(670, 175, 110, 175, color=MUTED, sw=1.6))
    f.append(arrow(110, 175, 110, 140, color=MUTED, sw=1.6))
    f.append(text(390, 168, "Power Down: Зупинка такту → Збереження Retention → Ізоляція → Розмикання ключів", size=9, color=MUTED))

    # НИЖНЯ ЧАСТИНА: Правило перемикання DVFS (Voltage & Frequency Scaling)
    f.append(rect(40, 205, 680, 160, fill="#f8fafc", stroke=LINE, sw=1.6, rx=6))
    f.append(text(380, 228, "Послідовність динамічного масштабування напруги та частоти (DVFS Ordering)", size=12.5, color=INK, bold=True))

    # Збільшення продуктивності (Scale UP)
    f.append(rect(60, 245, 300, 105, fill="#eff6ff", stroke=C_CPUK, sw=1.4, rx=4))
    f.append(text(210, 265, "Підвищення частоти (Scale UP)", size=11, color=C_CPUK, bold=True))
    f.append(text(75, 286, "1. Збільшити напругу Vdd (PMIC command)", size=9.5, color=INK, anchor="start"))
    f.append(text(75, 304, "2. Зачекати стабілізації живлення (t_settle)", size=9.5, color=INK, anchor="start"))
    f.append(text(75, 322, "3. Підвищити частоту тактового сигналу f_clk", size=9.5, color=INK, anchor="start"))
    f.append(text(210, 341, "Захист від timing violations на високій частоті", size=9, color=C_CPUK))

    # Зменшення продуктивності (Scale DOWN)
    f.append(rect(390, 245, 310, 105, fill="#f0fdf4", stroke=C_GPUK, sw=1.4, rx=4))
    f.append(text(545, 265, "Зниження енергоспоживання (Scale DOWN)", size=11, color=C_GPUK, bold=True))
    f.append(text(405, 286, "1. Знизити тактову частоту f_clk (Clock Mux)", size=9.5, color=INK, anchor="start"))
    f.append(text(405, 304, "2. Знизити напругу живлення Vdd (PMIC)", size=9.5, color=INK, anchor="start"))
    f.append(text(405, 322, "3. Заощадження енергії P = C · V² · f", size=9.5, color=INK, anchor="start"))
    f.append(text(545, 341, "Запобігає роботі швидкого такту на низькій напрузі", size=9, color=C_GPUK))

    f.append(text(W / 2, H - 12, "Порушення послідовності DVFS призводить до збоїв логіки через затримку поширення сигналів",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "dvfs-state-machine.svg"), W, H, *f)


# ── hist-фіг.1: Еволюція інтеграції: від дискретних плат до SoC ────────────────
def fig_pcb_to_soc_evolution():
    W, H = 760, 380
    f = [text(W / 2, 26, "Еволюція обчислювальних систем: від розсипу мікросхем до монолітного SoC",
              size=15, bold=True)]

    eras = [
        (40, 65, 210, 260, "1980-ті: Дискретна плата", "#f8fafc", MUTED, [
            ("Друкована плата (PCB)", True, INK),
            ("Окремий CPU (напр. Z80 / 8086)", False, C_CPUK),
            ("Окремий контролер ОЗП", False, C_MEMK),
            ("Окремий UART / периферія", False, C_SECK),
            ("Логіка узгодження 74-серії", False, MUTED),
            ("Десятки мікросхем на платі", True, POS),
            ("Шини: 10–20 пФ на доріжку", False, MUTED),
            ("Затримки: десятки наносекунд", False, MUTED),
        ]),
        (275, 65, 210, 260, "1990-ті: Мікроконтролери", "#f0fdf4", C_GPUK, [
            ("Перша інтеграція на кристалі", True, C_GPUK),
            ("CPU + Flash + SRAM разом", False, INK),
            ("Прості периферійні таймери/IO", False, INK),
            ("Загальна розділена шина", False, MUTED),
            ("Обмежена потужність (МГц)", False, MUTED),
            ("Прорив у вбудованих системах", True, C_GPUK),
            ("Низька собівартість", False, MUTED),
            ("Однорідний техпроцес", False, MUTED),
        ]),
        (510, 65, 210, 260, "2000-ні–2020-ті: Гетерогенний SoC", "#eff6ff", C_CPUK, [
            ("Повна гетерогенна система", True, C_CPUK),
            ("CPU + GPU + NPU + DDR PHY", False, C_CPUK),
            ("Аналогові PLL, RF-радіо, ADC", False, C_ANAK),
            ("Мережа NoC: терабайт/с", False, C_BUSK),
            ("Мультидоменне DVFS", False, C_GPUK),
            ("Мільярди транзисторів", True, C_CPUK),
            ("Шина на кристалі: <0.1 пФ", False, MUTED),
            ("Енергія: <1 пДж / біт", False, C_GPUK),
        ]),
    ]

    for bx, by, bw, bh, btitle, bcol, bck, items in eras:
        f.append(rect(bx, by, bw, bh, fill=bcol, stroke=bck, sw=1.8, rx=6))
        f.append(text(bx + bw / 2, by + 24, btitle, size=11.5, color=bck, bold=True))
        f.append(line(bx + 15, by + 36, bx + bw - 15, by + 36, color=bck, sw=1.0))
        yy = by + 56
        for itext, is_bold, icol in items:
            f.append(text(bx + bw / 2, yy, itext, size=9.5, color=icol, bold=is_bold))
            yy += 24

    # Стрілки між епохами
    f.append(arrow(252, 180, 273, 180, color=INK, sw=2.0))
    f.append(arrow(487, 180, 508, 180, color=INK, sw=2.0))

    f.append(text(W / 2, H - 16, "Інтеграція на єдиному кристалі скоротила енергію передавання біта у десятки разів і усунула «вузьке горло» виводів",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "pcb-to-soc-evolution.svg"), W, H, *f)


if __name__ == "__main__":
    fig_soc_architecture()
    fig_interconnect_hierarchy()
    fig_power_domains_dvfs()
    fig_clock_distribution_cts()
    fig_dft_bist_jtag()
    fig_axi_channels()
    fig_noc_mesh_routing()
    fig_dvfs_state_machine()
    fig_pcb_to_soc_evolution()
    print("OK: 9 SVG згенеровано у", IMG)
