# -*- coding: utf-8 -*-
"""Фігури до теми «Ліцензування IP-ядер» та її вставок.
Запуск: python figs.py  → генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Спеціальна палітра для IP-ядер
C_SOFT  = "#eaf0fd"   # синій для Soft IP
C_SOFTK = "#2457d6"
C_FIRM  = "#ede9fe"   # фіолетовий для Firm IP
C_FIRMK = "#6d28d9"
C_HARD  = "#fdf3e7"   # помаранчевий для Hard IP
C_HARDK = "#d97706"
C_BUS   = "#e8f7ec"   # зелений для шин і стандартних інтерфейсів
C_BUSK  = "#1e7e34"
C_WARN  = "#fce8e6"   # червонуватий для ризиків/витрат
C_WARNK = "#c0392b"
C_NEUT  = "#f3f4f6"   # сірий для нейтральних блоків
C_NEUTK = "#4b5563"


# ── d-фіг.1: Спектр трьох градацій IP-ядер ───────────────────────────────────
def fig_ip_hierarchy_spectrum():
    W, H = 760, 440
    f = [text(W / 2, 26, "Спектр трьох градацій напівпровідникової IP: Soft, Firm та Hard IP",
              size=15, bold=True)]

    # Загальний фон-шкала гнучкості та залежності
    f.append(rect(30, 48, 700, 365, fill="#fafbfc", stroke=LINE, sw=1.8, rx=8))

    # Стрілка вгорі: Переносимість між техпроцесами vs Оптимізація PPA
    f.append(line(50, 75, 710, 75, color=LINE, sw=1.5))
    f.append(text(60, 68, "◀ Максимальна гнучкість і переносимість (Portability)", size=10.5, color=C_SOFTK, bold=True, anchor="start"))
    f.append(text(700, 68, "Максимальний контроль PPA і кремнієва гарантія ▶", size=10.5, color=C_HARDK, bold=True, anchor="end"))

    col_w = 216
    col_gap = 18
    col_y = 90
    col_h = 305

    # 1. Soft IP
    x1 = 50
    f.append(rect(x1, col_y, col_w, col_h, fill=C_SOFT, stroke=C_SOFTK, sw=1.6, rx=6))
    f.append(text(x1 + col_w/2, col_y + 24, "Soft IP (Синтезований RTL)", size=12.5, color=C_SOFTK, bold=True))
    
    f.append(rect(x1 + 10, col_y + 36, col_w - 20, 52, fill="#ffffff", stroke=C_SOFTK, sw=1.0, rx=4))
    f.append(text(x1 + col_w/2, col_y + 54, "Формат представлення:", size=10, color=MUTED, bold=True))
    f.append(text(x1 + col_w/2, col_y + 72, "SystemVerilog / VHDL код", size=10.5, color=INK, bold=True))

    f.append(rect(x1 + 10, col_y + 96, col_w - 20, 88, fill="#ffffff", stroke=C_SOFTK, sw=1.0, rx=4))
    f.append(text(x1 + col_w/2, col_y + 114, "Ключові властивості:", size=10, color=MUTED, bold=True))
    f.append(text(x1 + col_w/2, col_y + 132, "• Повна конфігурованість", size=9.5, color=INK))
    f.append(text(x1 + col_w/2, col_y + 148, "• Незалежність від фабу", size=9.5, color=INK))
    f.append(text(x1 + col_w/2, col_y + 164, "• Синтез силами замовника", size=9.5, color=INK))

    f.append(rect(x1 + 10, col_y + 192, col_w - 20, 102, fill="#ffffff", stroke=C_SOFTK, sw=1.0, rx=4))
    f.append(text(x1 + col_w/2, col_y + 210, "Типові приклади:", size=10, color=MUTED, bold=True))
    f.append(text(x1 + col_w/2, col_y + 228, "• Процесорні ядра CPU", size=9.5, color=INK))
    f.append(text(x1 + col_w/2, col_y + 244, "• Контролери шин (AXI, AHB)", size=9.5, color=INK))
    f.append(text(x1 + col_w/2, col_y + 260, "• Цифрові MAC/DSP блоки", size=9.5, color=INK))
    f.append(text(x1 + col_w/2, col_y + 276, "• Контролери USB/PCIe MAC", size=9.5, color=INK))

    # 2. Firm IP
    x2 = x1 + col_w + col_gap
    f.append(rect(x2, col_y, col_w, col_h, fill=C_FIRM, stroke=C_FIRMK, sw=1.6, rx=6))
    f.append(text(x2 + col_w/2, col_y + 24, "Firm IP (Структурний нетліст)", size=12.5, color=C_FIRMK, bold=True))

    f.append(rect(x2 + 10, col_y + 36, col_w - 20, 52, fill="#ffffff", stroke=C_FIRMK, sw=1.0, rx=4))
    f.append(text(x2 + col_w/2, col_y + 54, "Формат представлення:", size=10, color=MUTED, bold=True))
    f.append(text(x2 + col_w/2, col_y + 72, "Gate-level Netlist + Floorplan", size=10.5, color=INK, bold=True))

    f.append(rect(x2 + 10, col_y + 96, col_w - 20, 88, fill="#ffffff", stroke=C_FIRMK, sw=1.0, rx=4))
    f.append(text(x2 + col_w/2, col_y + 114, "Ключові властивості:", size=10, color=MUTED, bold=True))
    f.append(text(x2 + col_w/2, col_y + 132, "• Синтезована логіка", size=9.5, color=INK))
    f.append(text(x2 + col_w/2, col_y + 148, "• Захист вихідного RTL", size=9.5, color=INK))
    f.append(text(x2 + col_w/2, col_y + 164, "• Фіксація критичних затримок", size=9.5, color=INK))

    f.append(rect(x2 + 10, col_y + 192, col_w - 20, 102, fill="#ffffff", stroke=C_FIRMK, sw=1.0, rx=4))
    f.append(text(x2 + col_w/2, col_y + 210, "Типові приклади:", size=10, color=MUTED, bold=True))
    f.append(text(x2 + col_w/2, col_y + 228, "• Спецпроцесори з захистом", size=9.5, color=INK))
    f.append(text(x2 + col_w/2, col_y + 244, "• Оптимізовані 3D-шейдери", size=9.5, color=INK))
    f.append(text(x2 + col_w/2, col_y + 260, "• Криптографічні акселератори", size=9.5, color=INK))
    f.append(text(x2 + col_w/2, col_y + 276, "• DSP під конкретні комірки", size=9.5, color=INK))

    # 3. Hard IP
    x3 = x2 + col_w + col_gap
    f.append(rect(x3, col_y, col_w, col_h, fill=C_HARD, stroke=C_HARDK, sw=1.6, rx=6))
    f.append(text(x3 + col_w/2, col_y + 24, "Hard IP (Фізичний GDSII)", size=12.5, color=C_HARDK, bold=True))

    f.append(rect(x3 + 10, col_y + 36, col_w - 20, 52, fill="#ffffff", stroke=C_HARDK, sw=1.0, rx=4))
    f.append(text(x3 + col_w/2, col_y + 54, "Формат представлення:", size=10, color=MUTED, bold=True))
    f.append(text(x3 + col_w/2, col_y + 72, "GDSII / OASIS + LEF + .lib", size=10.5, color=INK, bold=True))

    f.append(rect(x3 + 10, col_y + 96, col_w - 20, 88, fill="#ffffff", stroke=C_HARDK, sw=1.0, rx=4))
    f.append(text(x3 + col_w/2, col_y + 114, "Ключові властивості:", size=10, color=MUTED, bold=True))
    f.append(text(x3 + col_w/2, col_y + 132, "• Прив'язка до фабрики й PDK", size=9.5, color=INK))
    f.append(text(x3 + col_w/2, col_y + 148, "• Silicon-proven гарантія", size=9.5, color=INK))
    f.append(text(x3 + col_w/2, col_y + 164, "• Нульові зусилля розробки", size=9.5, color=INK))

    f.append(rect(x3 + 10, col_y + 192, col_w - 20, 102, fill="#ffffff", stroke=C_HARDK, sw=1.0, rx=4))
    f.append(text(x3 + col_w/2, col_y + 210, "Типові приклади:", size=10, color=MUTED, bold=True))
    f.append(text(x3 + col_w/2, col_y + 228, "• Аналогові PHY (PCIe, DDR5)", size=9.5, color=INK))
    f.append(text(x3 + col_w/2, col_y + 244, "• SerDes (112G / 224G PAM4)", size=9.5, color=INK))
    f.append(text(x3 + col_w/2, col_y + 260, "• Генератори такту (PLL, DLL)", size=9.5, color=INK))
    f.append(text(x3 + col_w/2, col_y + 276, "• SRAM-масиви, ADC, eFuse", size=9.5, color=INK))

    render(os.path.join(IMG, "ip-hierarchy-spectrum.svg"), W, H, *f)


# ── d-фіг.2: Економіка Build vs Buy ──────────────────────────────────────────
def fig_build_vs_buy_economics():
    W, H = 760, 420
    f = [text(W / 2, 26, "Економічна модель сукупних витрат: власна розробка (Build) проти ліцензування (Buy)",
              size=14, bold=True)]

    # Область графіку
    ox, oy = 80, 340
    gw, gh = 620, 270

    f.append(rect(30, 48, 700, 350, fill="#fafbfc", stroke=LINE, sw=1.6, rx=8))

    # Осі координат
    f.append(arrow(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - gh, color=LINE, sw=1.8))

    f.append(text(ox + gw - 20, oy + 25, "Тираж чіпів Q (обсяг випуску)", size=11, color=INK, bold=True, anchor="end"))
    f.append(text(ox - 15, oy - gh + 15, "Сукупні витрати TCO ($)", size=11, color=INK, bold=True, anchor="end"))

    # Лінія 1: Build from scratch (Високий стартовий NRE, нульові роялті, пологий нахил)
    f.append(line(ox, oy - 190, ox + 550, oy - 270, color=C_WARNK, sw=2.5))
    f.append(text(ox + 555, oy - 272, "Власна розробка (Build from Scratch)", size=11, color=C_WARNK, bold=True, anchor="start"))
    f.append(text(ox + 555, oy - 256, "Високий NRE R&D, 0% роялті", size=10, color=MUTED, anchor="start"))

    # Лінія 2: Buy / License IP (Низький стартовий NRE/Fee, поштучні роялті, крутіший нахил)
    f.append(line(ox, oy - 60, ox + 550, oy - 310, color=C_SOFTK, sw=2.5))
    f.append(text(ox + 555, oy - 312, "Ліцензування IP (Buy / License)", size=11, color=C_SOFTK, bold=True, anchor="start"))
    f.append(text(ox + 555, oy - 296, "Аванс (Fee) + Роялті за чіп", size=10, color=MUTED, anchor="start"))

    # Точка перетину (Break-even Point)
    bx, by = ox + 338, oy - 215
    f.append(circle(bx, by, 5, fill=C_HARDK, stroke="#ffffff", sw=2.0))
    f.append(line(bx, by, bx, oy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(bx, by, ox, by, color=MUTED, sw=1.2, dash="4,4"))

    f.append(text(bx, oy + 18, "Q_be (Точка беззбитковості)", size=10.5, color=C_HARDK, bold=True))
    f.append(text(ox - 10, by + 4, "TCO_be", size=10, color=MUTED, anchor="end"))

    # Позначення зон
    # Зона 1: До точки беззбитковості (Buy вигідніше)
    f.append(rect(ox + 30, oy - 150, 160, 48, fill=C_SOFT, stroke=C_SOFTK, sw=1.2, rx=4))
    f.append(text(ox + 110, oy - 134, "Зона вигоди ліцензування", size=10, color=C_SOFTK, bold=True))
    f.append(text(ox + 110, oy - 116, "Економія NRE та швидкий запуск", size=9.5, color=INK))

    # Зона 2: Після точки беззбитковості (Build вигідніше)
    f.append(rect(ox + 360, oy - 150, 160, 48, fill=C_WARN, stroke=C_WARNK, sw=1.2, rx=4))
    f.append(text(ox + 440, oy - 134, "Зона вигоди власного R&D", size=10, color=C_WARNK, bold=True))
    f.append(text(ox + 440, oy - 116, "Гігантські тиражі окупають R&D", size=9.5, color=INK))

    # Позначення авансових платежів на осі Y
    f.append(line(ox - 5, oy - 60, ox + 5, oy - 60, color=LINE, sw=1.5))
    f.append(text(ox - 10, oy - 56, "Upfront Fee", size=10, color=C_SOFTK, bold=True, anchor="end"))

    f.append(line(ox - 5, oy - 190, ox + 5, oy - 190, color=LINE, sw=1.5))
    f.append(text(ox - 10, oy - 186, "NRE R&D", size=10, color=C_WARNK, bold=True, anchor="end"))

    render(os.path.join(IMG, "build-vs-buy-economics.svg"), W, H, *f)


# ── d-фіг.3: Інтеграція IP-ядер через стандартні інтерфейси ──────────────────
def fig_ip_integration_interfaces():
    W, H = 760, 460
    f = [text(W / 2, 26, "Стандартизовані інтерфейси інтеграції різнорідних IP-блоків у SoC",
              size=15, bold=True)]

    # Контур SoC
    f.append(rect(30, 48, 700, 390, fill="#fafbfc", stroke=LINE, sw=2.0, rx=8))
    f.append(text(46, 68, "Кремнієвий кристал SoC (System-on-Chip)", size=11, color=MUTED, bold=True, anchor="start"))

    # Центральна магістраль: AMBA AXI4 / NoC Interconnect
    f.append(rect(50, 190, 660, 56, fill=C_BUS, stroke=C_BUSK, sw=1.8, rx=4))
    f.append(text(380, 213, "Центральний інтерконект: AMBA AXI4 / NoC Crossbar", size=13, color=C_BUSK, bold=True))
    f.append(text(380, 232, "Повнодуплексна матриця з 5 незалежними каналами (AW, W, B, AR, R)", size=10, color=C_BUSK))

    # Верхні цифрові Soft IP блоки: CPU Core, NPU Accelerator, DMA Controller
    # 1. CPU Cluster
    f.append(rect(50, 85, 175, 80, fill=C_SOFT, stroke=C_SOFTK, sw=1.5, rx=4))
    f.append(text(137, 107, "CPU Процесорний кластер", size=11, color=C_SOFTK, bold=True))
    f.append(text(137, 124, "Soft IP (SystemVerilog RTL)", size=9.5, color=MUTED))
    f.append(rect(65, 134, 145, 22, fill="#ffffff", stroke=C_SOFTK, sw=1.0, rx=3))
    f.append(text(137, 149, "AXI4 Master Interface", size=9.5, color=C_SOFTK, bold=True))
    f.append(line(137, 165, 137, 190, color=C_BUSK, sw=2.0))

    # 2. NPU / GPU Accelerator
    f.append(rect(245, 85, 175, 80, fill=C_SOFT, stroke=C_SOFTK, sw=1.5, rx=4))
    f.append(text(332, 107, "Нейроприскорювач NPU", size=11, color=C_SOFTK, bold=True))
    f.append(text(332, 124, "Soft IP / Firm IP модуль", size=9.5, color=MUTED))
    f.append(rect(260, 134, 145, 22, fill="#ffffff", stroke=C_SOFTK, sw=1.0, rx=3))
    f.append(text(332, 149, "AXI4 Master / Slave", size=9.5, color=C_SOFTK, bold=True))
    f.append(line(332, 165, 332, 190, color=C_BUSK, sw=2.0))

    # 3. Периферійний міст AMBA APB
    f.append(rect(440, 85, 270, 80, fill=C_NEUT, stroke=C_NEUTK, sw=1.5, rx=4))
    f.append(text(575, 105, "Міст APB Bridge + Периферія", size=11, color=C_NEUTK, bold=True))
    f.append(text(575, 121, "Шина керування регістрами APB", size=9.5, color=MUTED))
    f.append(rect(455, 132, 240, 24, fill="#ffffff", stroke=C_NEUTK, sw=1.0, rx=3))
    f.append(text(575, 148, "UART, I2C, SPI, Timers (Soft IP)", size=9.5, color=INK))
    f.append(line(575, 165, 575, 190, color=C_BUSK, sw=2.0))

    # Нижні блоки: Цифрові контролери + Hard IP PHY через DFI та PIPE
    # 1. Підсистема оперативної пам'яті DDR5
    f.append(rect(50, 270, 315, 150, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    f.append(text(207, 288, "Підсистема інтерфейсу пам'яті (LPDDR5 / DDR5)", size=11, color=INK, bold=True))

    # Цифровий контролер
    f.append(rect(60, 300, 135, 75, fill=C_SOFT, stroke=C_SOFTK, sw=1.4, rx=4))
    f.append(text(127, 318, "DDR Контролер", size=10.5, color=C_SOFTK, bold=True))
    f.append(text(127, 333, "Soft IP (RTL)", size=9.5, color=MUTED))
    f.append(text(127, 350, "AXI4 Slave", size=9.5, color=INK, bold=True))
    f.append(text(127, 365, "Черги й таймінги", size=9.5, color=MUTED))
    f.append(line(127, 246, 127, 270, color=C_BUSK, sw=2.0))

    # Інтерфейс DFI
    f.append(line(195, 337, 225, 337, color=C_BUSK, sw=2.5))
    f.append(text(210, 328, "DFI", size=10.5, color=C_BUSK, bold=True))
    f.append(text(210, 352, "Стандарт", size=9.5, color=MUTED))

    # Аналоговий Hard IP DDR PHY
    f.append(rect(225, 300, 130, 75, fill=C_HARD, stroke=C_HARDK, sw=1.4, rx=4))
    f.append(text(290, 318, "DDR PHY", size=10.5, color=C_HARDK, bold=True))
    f.append(text(290, 333, "Hard IP (GDSII)", size=9.5, color=MUTED))
    f.append(text(290, 350, "DLL, Driver, IO", size=9.5, color=INK))
    f.append(text(290, 365, "PDK Fab Specific", size=9.5, color=C_HARDK, bold=True))

    f.append(text(207, 405, "До зовнішніх мікросхем DRAM ──▶", size=9.5, color=MUTED))

    # 2. Підсистема PCIe Gen5 / Gen6
    f.append(rect(395, 270, 315, 150, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    f.append(text(552, 288, "Підсистема високошвидкісного PCIe / USB4", size=11, color=INK, bold=True))

    # Цифровий контролер MAC
    f.append(rect(405, 300, 135, 75, fill=C_SOFT, stroke=C_SOFTK, sw=1.4, rx=4))
    f.append(text(472, 318, "PCIe MAC / Link", size=10.5, color=C_SOFTK, bold=True))
    f.append(text(472, 333, "Soft IP (RTL)", size=9.5, color=MUTED))
    f.append(text(472, 350, "AXI4 Master/Slave", size=9.5, color=INK, bold=True))
    f.append(text(472, 365, "Рівні каналу й транзакцій", size=9.5, color=MUTED))
    f.append(line(472, 246, 472, 270, color=C_BUSK, sw=2.0))

    # Інтерфейс PIPE
    f.append(line(540, 337, 570, 337, color=C_BUSK, sw=2.5))
    f.append(text(555, 328, "PIPE", size=10.5, color=C_BUSK, bold=True))
    f.append(text(555, 352, "Стандарт", size=9.5, color=MUTED))

    # Аналоговий Hard IP SerDes PHY
    f.append(rect(570, 300, 130, 75, fill=C_HARD, stroke=C_HARDK, sw=1.4, rx=4))
    f.append(text(635, 318, "SerDes PHY", size=10.5, color=C_HARDK, bold=True))
    f.append(text(635, 333, "Hard IP (GDSII)", size=9.5, color=MUTED))
    f.append(text(635, 350, "32–112G PAM4 PLL", size=9.5, color=INK))
    f.append(text(635, 365, "PDK Fab Specific", size=9.5, color=C_HARDK, bold=True))

    f.append(text(552, 405, "До роз'єму PCIe / ліній зв'язку ──▶", size=9.5, color=MUTED))

    render(os.path.join(IMG, "ip-integration-interfaces.svg"), W, H, *f)


# ── comp-фіг.4: Матриця пакетів поставки (Deliverables) ──────────────────────
def fig_ip_deliverables_matrix():
    W, H = 760, 450
    f = [text(W / 2, 26, "Матриця пакетів поставки (Deliverables) для Soft, Firm та Hard IP",
              size=15, bold=True)]

    f.append(rect(30, 48, 700, 380, fill="#fafbfc", stroke=LINE, sw=1.8, rx=8))

    # Заголовок таблиці
    th_y = 60
    f.append(rect(45, th_y, 180, 32, fill=C_NEUT, stroke=LINE, sw=1.2, rx=4))
    f.append(text(135, th_y + 20, "Категорія файлів", size=11, color=INK, bold=True))

    f.append(rect(235, th_y, 150, 32, fill=C_SOFT, stroke=C_SOFTK, sw=1.2, rx=4))
    f.append(text(310, th_y + 20, "Soft IP", size=11, color=C_SOFTK, bold=True))

    f.append(rect(395, th_y, 150, 32, fill=C_FIRM, stroke=C_FIRMK, sw=1.2, rx=4))
    f.append(text(470, th_y + 20, "Firm IP", size=11, color=C_FIRMK, bold=True))

    f.append(rect(555, th_y, 160, 32, fill=C_HARD, stroke=C_HARDK, sw=1.2, rx=4))
    f.append(text(635, th_y + 20, "Hard IP", size=11, color=C_HARDK, bold=True))

    rows = [
        ("Логічний дизайн (RTL)", "RTL (SystemVerilog, VHDL)", "Gate Netlist (.v)", "Відсутній (Чорний ящик)"),
        ("Фізичний лейаут", "Відсутній (Синтез клієнта)", "DEF / RBM constraints", "GDSII / OASIS (Повна топологія)"),
        ("Абстракція для P&R", "Генерується замовником", "LEF (Опціонально)", "LEF (Піни + Obtsructions)"),
        ("Таймінгові моделі", "SDC (Timing constraints)", "SDC + .lib", "Liberty (.lib / .db) PVT corners"),
        ("Електрична схема", "Відсутня", "Gate-level Netlist", "CDL / SPICE transistor netlist"),
        ("Керування живленням", "UPF / CPF (Power intent)", "UPF / CPF", "Power pins + Internal PG"),
        ("Симуляційні моделі", "Поведінковий SystemVerilog", "Gate-level Verilog", "Verilog Shell / Fast SPICE"),
        ("Верифікація (VIP)", "UVM Testbench, Assertions", "Netlist Testbench", "Silicon proven тестові звіти")
    ]

    ry = 98
    rh = 38
    for i, (cat, soft, firm, hard) in enumerate(rows):
        bg_col = "#ffffff" if i % 2 == 0 else "#f8fafc"
        f.append(rect(45, ry, 670, rh, fill=bg_col, stroke=LINE, sw=0.8, rx=2))
        f.append(text(55, ry + 23, cat, size=9.5, color=INK, bold=True, anchor="start"))
        f.append(text(310, ry + 23, soft, size=9.5, color=C_SOFTK))
        f.append(text(470, ry + 23, firm, size=9.5, color=C_FIRMK))
        f.append(text(635, ry + 23, hard, size=9.5, color=C_HARDK))
        ry += rh + 2

    render(os.path.join(IMG, "ip-deliverables-matrix.svg"), W, H, *f)


# ── hist-фіг.5: Екосистема ліцензування ARM ──────────────────────────────────
def fig_arm_licensing_ecosystem():
    W, H = 760, 430
    f = [text(W / 2, 26, "Екосистема безфабричного ліцензування: рух технологій та фінансових потоків",
              size=14, bold=True)]

    f.append(rect(30, 48, 700, 360, fill="#fafbfc", stroke=LINE, sw=1.8, rx=8))

    # Центральний суб'єкт: IP Vendor (ARM / Synopsys)
    f.append(rect(50, 160, 180, 115, fill=C_SOFT, stroke=C_SOFTK, sw=1.8, rx=6))
    f.append(text(140, 184, "IP-Вендор (ARM)", size=13, color=C_SOFTK, bold=True))
    f.append(text(140, 202, "Розробка архітектури", size=9.5, color=INK))
    f.append(text(140, 218, "та процесорних ядер", size=9.5, color=INK))
    f.append(text(140, 238, "0 власних фабрик!", size=10, color=C_WARNK, bold=True))
    f.append(text(140, 256, "RTL & Hard IP дизайн", size=9.5, color=MUTED))

    # Fabless-клієнти (Apple, Qualcomm, MediaTek, NXP)
    f.append(rect(290, 68, 200, 95, fill=C_BUS, stroke=C_BUSK, sw=1.6, rx=6))
    f.append(text(390, 90, "Fabless-компанії", size=12, color=C_BUSK, bold=True))
    f.append(text(390, 107, "(Apple, Qualcomm, NXP)", size=9.5, color=MUTED))
    f.append(text(390, 126, "Інтеграція IP в SoC", size=10, color=INK))
    f.append(text(390, 144, "Створення файлу масок (GDSII)", size=9.5, color=INK))

    # Чиста фабрика: Pure-play Foundry (TSMC)
    f.append(rect(290, 210, 200, 95, fill=C_HARD, stroke=C_HARDK, sw=1.6, rx=6))
    f.append(text(390, 232, "Pure-play Foundry", size=12, color=C_HARDK, bold=True))
    f.append(text(390, 249, "(TSMC, Samsung, UMC)", size=9.5, color=MUTED))
    f.append(text(390, 268, "Виготовлення кремнію", size=10, color=INK))
    f.append(text(390, 286, "Мільярдні фабрики", size=9.5, color=INK))

    # OEM Виробники гаджетів (Смартфони, Авто, Сервери)
    f.append(rect(540, 160, 170, 115, fill=C_NEUT, stroke=C_NEUTK, sw=1.6, rx=6))
    f.append(text(625, 184, "OEM Виробники", size=12, color=C_NEUTK, bold=True))
    f.append(text(625, 202, "Кінцеві пристрої", size=9.5, color=INK))
    f.append(text(625, 220, "(Смартфони, Авто, ПК)", size=9.5, color=MUTED))
    f.append(text(625, 240, "Продаж мільярдів", size=9.5, color=INK))
    f.append(text(625, 256, "готових гаджетів", size=9.5, color=INK))

    # Стрілки взаємодії
    # 1. IP Vendor -> Fabless: Ліцензія IP (RTL, моделі)
    f.append(arrow(180, 160, 290, 115, color=C_SOFTK, sw=2.0))
    f.append(text(215, 125, "Ліцензія IP", size=9.5, color=C_SOFTK, bold=True, anchor="end"))

    # 2. Fabless -> IP Vendor: Upfront License Fee
    f.append(arrow(290, 135, 230, 175, color=C_WARNK, sw=1.6))
    f.append(text(285, 165, "Upfront Fee ($)", size=9.5, color=C_WARNK, bold=True, anchor="end"))

    # 3. Fabless -> Foundry: GDSII + Оплата пластин
    f.append(arrow(390, 163, 390, 210, color=LINE, sw=1.8))
    f.append(text(400, 188, "GDSII Маски", size=9.5, color=INK, bold=True, anchor="start"))

    # 4. Foundry -> OEM / Fabless: Готові чіпи
    f.append(arrow(490, 250, 560, 230, color=C_HARDK, sw=2.0))
    f.append(text(535, 260, "Кремнієві чіпи", size=9.5, color=C_HARDK, bold=True, anchor="start"))

    # 5. OEM -> Fabless: Оплата за чіпи
    f.append(arrow(580, 160, 490, 120, color=LINE, sw=1.6))
    f.append(text(565, 130, "Купівля чіпів", size=9.5, color=INK, anchor="start"))

    # 6. Зворотний потік: Per-chip Royalty від OEM до IP Vendor по нижньому контуру
    f.append(line(625, 275, 625, 345, color=C_WARNK, sw=2.0))
    f.append(line(625, 345, 520, 345, color=C_WARNK, sw=2.0))
    f.append(rect(260, 332, 260, 26, fill="#ffffff", stroke=C_WARNK, sw=1.2, rx=4))
    f.append(text(390, 349, "Поштучні роялті: 1–2% за чіп ($)", size=10, color=C_WARNK, bold=True))
    f.append(line(260, 345, 140, 345, color=C_WARNK, sw=2.0))
    f.append(arrow(140, 345, 140, 275, color=C_WARNK, sw=2.0))

    render(os.path.join(IMG, "arm-licensing-ecosystem.svg"), W, H, *f)


# ── math-фіг.6: Параметричні криві беззбитковості ────────────────────────────
def fig_break_even_analysis():
    W, H = 760, 420
    f = [text(W / 2, 26, "Вплив затримки виходу на ринок (Time-to-Market) на точку беззбитковості",
              size=14, bold=True)]

    ox, oy = 80, 340
    gw, gh = 620, 270

    f.append(rect(30, 48, 700, 350, fill="#fafbfc", stroke=LINE, sw=1.6, rx=8))

    # Осі координат
    f.append(arrow(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - gh, color=LINE, sw=1.8))

    f.append(text(ox + gw - 20, oy + 25, "Тираж чіпів Q (одиниць)", size=11, color=INK, bold=True, anchor="end"))
    f.append(text(ox - 15, oy - gh + 15, "Сукупні фінансові витрати та втрати ($)", size=11, color=INK, bold=True, anchor="end"))

    # 1. Buy IP (Швидкий вихід на ринок, 0 затримки)
    f.append(line(ox, oy - 60, ox + 550, oy - 290, color=C_SOFTK, sw=2.5))
    f.append(text(ox + 555, oy - 292, "Buy IP (Вчасний вихід на ринок)", size=10.5, color=C_SOFTK, bold=True, anchor="start"))

    # 2. Build Ідеальний (Без затримки)
    f.append(line(ox, oy - 150, ox + 550, oy - 230, color=MUTED, sw=1.8, dash="4,4"))
    f.append(text(ox + 555, oy - 232, "Build (Ідеальний: без затримки)", size=10, color=MUTED, anchor="start"))

    # 3. Build Реальний (+6 місяців затримки Time-to-Market + Penalty)
    f.append(line(ox, oy - 230, ox + 550, oy - 310, color=C_WARNK, sw=2.5))
    f.append(text(ox + 555, oy - 312, "Build з затримкою 6 міс (+Втрачена виручка)", size=10.5, color=C_WARNK, bold=True, anchor="start"))

    # Точки беззбитковості
    # Ідеальна точка Q1
    q1_x, q1_y = ox + 225, oy - 154
    f.append(circle(q1_x, q1_y, 4.5, fill=MUTED, stroke="#ffffff", sw=1.5))
    f.append(line(q1_x, q1_y, q1_x, oy, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(q1_x, oy + 18, "Q_be (Ідеальний)", size=9.5, color=MUTED))

    # Реальна точка Q2 (зсувається далеко вправо через затримку)
    q2_x, q2_y = ox + 425, oy - 238
    f.append(circle(q2_x, q2_y, 5.5, fill=C_WARNK, stroke="#ffffff", sw=2.0))
    f.append(line(q2_x, q2_y, q2_x, oy, color=C_WARNK, sw=1.2, dash="4,4"))
    f.append(text(q2_x, oy + 18, "Q_be (Реальний зі збитками затримки)", size=10, color=C_WARNK, bold=True))

    # Стрілка зсуву точки беззбитковості
    f.append(arrow(q1_x + 10, oy - 80, q2_x - 10, oy - 80, color=C_WARNK, sw=2.0))
    f.append(text((q1_x + q2_x)/2, oy - 92, "Зсув точки беззбитковості на мільйони чіпів!", size=10, color=C_WARNK, bold=True))

    render(os.path.join(IMG, "break-even-analysis.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ip_hierarchy_spectrum()
    fig_build_vs_buy_economics()
    fig_ip_integration_interfaces()
    fig_ip_deliverables_matrix()
    fig_arm_licensing_ecosystem()
    fig_break_even_analysis()
    print("Всі 6 фігур згенеровано у ./img/")
