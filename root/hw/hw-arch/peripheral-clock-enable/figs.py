# -*- coding: utf-8 -*-
import sys, os

# Reach scripts/ at repository root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Fig 1: MCU Clock Tree and Bus Domains with Clock Gating ──────────────────────
def fig_mcu_clock_tree_bus_domains():
    W, H = 960, 640
    p = []

    # Canvas Background
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=0))

    # Top Header
    header, hw, hh = textbox(480, 30, "Дерево тактування мікроконтролера та стробування такту (Clock Gating) шинних доменів",
                             size=13, bold=True, fill="#f6f8fa", stroke="#0969da", sw=1.5, pad=10)
    p.append(header)

    # ── Left Column: Primary Clock Sources ──
    p.append(rect(20, 65, 175, 550, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    p.append(text(107, 90, "Джерела такту", size=12, color="#0f172a", bold=True))

    src_boxes = [
        (107, 130, "HSI RC\n16 МГц (внутр.)", "#e2e8f0", "#475569"),
        (107, 205, "HSE Кварц\n8–25 МГц (зовн.)", "#e0f2fe", "#0284c7"),
        (107, 290, "PLL Множник\nдо 168–480 МГц", "#fef3c7", "#d97706"),
        (107, 400, "LSI RC\n32 кГц (Watchdog)", "#f1f5f9", "#64748b"),
        (107, 490, "LSE Кварц\n32.768 кГц (RTC)", "#f0fdf4", "#16a34a"),
    ]
    for cx, cy, lab, fill_c, str_c in src_boxes:
        b, bw, bh = textbox(cx, cy, lab, size=10, bold=True, fill=fill_c, stroke=str_c, sw=1.2, pad=8)
        p.append(b)

    # Connect HSE to PLL
    p.append(arrow(107, 230, 107, 265, color="#0284c7", sw=1.5))
    p.append(text(128, 248, "×N/M", size=9.5, color="#0284c7", italic=True))

    # SYSCLK MUX
    p.append(arrow(185, 130, 230, 210, color="#475569", sw=1.5))
    p.append(arrow(185, 205, 230, 210, color="#0284c7", sw=1.5))
    p.append(arrow(185, 290, 230, 220, color="#d97706", sw=1.5))

    mux_box, mw, mh = textbox(260, 215, "Селектор\nSYSCLK\nMUX", size=10, bold=True, fill="#fff7ed", stroke="#ea580c", sw=1.5, pad=8)
    p.append(mux_box)

    # Central Distribution Line
    p.append(arrow(260 + mw/2, 215, 335, 215, color="#ea580c", sw=2.0))
    p.append(text(298, 203, "SYSCLK", size=10, color="#ea580c", bold=True))

    # ── AHB Prescaler ──
    ahb_pre, apw, aph = textbox(380, 215, "AHB Дільник\n(/1, /2.. /512)", size=10, bold=True, fill="#eff6ff", stroke="#2563eb", sw=1.5, pad=8)
    p.append(ahb_pre)

    p.append(arrow(380 + apw/2, 215, 450, 215, color="#2563eb", sw=2.2))
    p.append(text(415, 203, "HCLK", size=10.5, color="#2563eb", bold=True))

    # ── AHB Domain ──
    p.append(rect(450, 65, 490, 180, fill="#f0fdf4", stroke="#16a34a", sw=1.6, rx=6))
    p.append(text(695, 86, "Шинний домен AHB (HCLK — висока швидкість, системна матриця)", size=11, color="#15803d", bold=True))

    # AHB Peripherals with Clock Gating
    ahb_nodes = [
        (505, 145, "Cortex-M Ядро\n& SysTick", "#dcfce7", "#16a34a", "Постійний такт"),
        (620, 145, "DMA1 / DMA2\nКонтролери", "#dcfce7", "#16a34a", "RCC_AHB1ENR"),
        (735, 145, "Flash & SRAM\nПам'ять", "#dcfce7", "#16a34a", "Автостробування"),
        (855, 145, "USB OTG / ETH\nМережеві блоки", "#dcfce7", "#16a34a", "RCC_AHB2ENR"),
    ]
    for cx, cy, lab, fill_c, str_c, gate_lbl in ahb_nodes:
        icg_b, iw, ih = textbox(cx, cy - 28, "ICG Gate", size=9, bold=True, fill="#fef9c3", stroke="#ca8a04", sw=1.0, pad=4)
        p.append(icg_b)
        b, bw, bh = textbox(cx, cy + 20, lab, size=9.5, bold=True, fill=fill_c, stroke=str_c, sw=1.2, pad=6)
        p.append(b)
        p.append(line(cx, cy - 28 + ih/2, cx, cy + 20 - bh/2, color=str_c, sw=1.4))
        p.append(text(cx, cy + 54, gate_lbl, size=9, color="#4b5563", italic=True))

    # AHB bus main trace
    p.append(line(450, 104, 915, 104, color="#16a34a", sw=2.5))
    for cx, cy, lab, fill_c, str_c, gate_lbl in ahb_nodes:
        p.append(arrow(cx, 104, cx, cy - 28 - 9, color="#16a34a", sw=1.4))

    # ── Downward Split from AHB to APB Bridges ──
    p.append(circle(475, 215, 3.5, fill="#2563eb", stroke="#2563eb", sw=1))
    p.append(line(475, 215, 475, 320, color="#2563eb", sw=1.8))
    p.append(line(475, 320, 475, 500, color="#2563eb", sw=1.8))

    # ── APB1 Bridge & Prescaler ──
    p.append(arrow(475, 320, 505, 320, color="#2563eb", sw=1.6))
    apb1_bridge, b1w, b1h = textbox(565, 320, "Міст AHB→APB1\n& Дільник PCLK1 (/2, /4..)", size=9.5, bold=True, fill="#fff1f2", stroke="#e11d48", sw=1.4, pad=7)
    p.append(apb1_bridge)

    # ── APB1 Domain (Low Speed) ──
    p.append(rect(655, 265, 285, 165, fill="#fff5f5", stroke="#e11d48", sw=1.5, rx=6))
    p.append(text(797, 286, "Домен APB1 (PCLK1 ≤ 42–45 МГц)", size=10.5, color="#be123c", bold=True))

    p.append(arrow(565 + b1w/2, 320, 675, 320, color="#e11d48", sw=1.8))
    p.append(line(675, 305, 915, 305, color="#e11d48", sw=2.0))

    apb1_periphs = [
        (710, 355, "USART2/3\nI2C1/2", "RCC_APB1ENR"),
        (795, 355, "SPI2/3\nCAN1/2", "RCC_APB1ENR"),
        (880, 355, "TIM2–TIM5\nDAC1/2", "RCC_APB1ENR"),
    ]
    for cx, cy, lab, gate_lbl in apb1_periphs:
        icg_b, iw, ih = textbox(cx, cy - 20, "ICG Gate", size=9, bold=True, fill="#fef9c3", stroke="#ca8a04", sw=1.0, pad=3)
        p.append(icg_b)
        b, bw, bh = textbox(cx, cy + 18, lab, size=9, bold=True, fill="#ffe4e6", stroke="#e11d48", sw=1.2, pad=5)
        p.append(b)
        p.append(arrow(cx, 305, cx, cy - 20 - 8, color="#e11d48", sw=1.2))
        p.append(line(cx, cy - 20 + ih/2, cx, cy + 18 - bh/2, color="#e11d48", sw=1.2))
        p.append(text(cx, cy + 46, gate_lbl, size=9, color="#6b7280", italic=True))

    # ── APB2 Bridge & Prescaler ──
    p.append(arrow(475, 500, 505, 500, color="#2563eb", sw=1.6))
    apb2_bridge, b2w, b2h = textbox(565, 500, "Міст AHB→APB2\n& Дільник PCLK2 (/1, /2..)", size=9.5, bold=True, fill="#faf5ff", stroke="#9333ea", sw=1.4, pad=7)
    p.append(apb2_bridge)

    # ── APB2 Domain (High Speed) ──
    p.append(rect(655, 445, 285, 165, fill="#faf5ff", stroke="#9333ea", sw=1.5, rx=6))
    p.append(text(797, 466, "Домен APB2 (PCLK2 ≤ 84–90 МГц)", size=10.5, color="#7e22ce", bold=True))

    p.append(arrow(565 + b2w/2, 500, 675, 500, color="#9333ea", sw=1.8))
    p.append(line(675, 485, 915, 485, color="#9333ea", sw=2.0))

    apb2_periphs = [
        (710, 535, "USART1/6\nUART9/10", "RCC_APB2ENR"),
        (795, 535, "SPI1/4/5/6\nEXTI", "RCC_APB2ENR"),
        (880, 535, "TIM1/8/9..\nADC1/2/3", "RCC_APB2ENR"),
    ]
    for cx, cy, lab, gate_lbl in apb2_periphs:
        icg_b, iw, ih = textbox(cx, cy - 20, "ICG Gate", size=9, bold=True, fill="#fef9c3", stroke="#ca8a04", sw=1.0, pad=3)
        p.append(icg_b)
        b, bw, bh = textbox(cx, cy + 18, lab, size=9, bold=True, fill="#f3e8ff", stroke="#9333ea", sw=1.2, pad=5)
        p.append(b)
        p.append(arrow(cx, 485, cx, cy - 20 - 8, color="#9333ea", sw=1.2))
        p.append(line(cx, cy - 20 + ih/2, cx, cy + 18 - bh/2, color="#9333ea", sw=1.2))
        p.append(text(cx, cy + 46, gate_lbl, size=9, color="#6b7280", italic=True))

    # Independent Kernel Clock Trace
    p.append('<path d="M 185 130 C 240 100, 290 595, 655 595" fill="none" stroke="#ea580c" stroke-width="1.5" stroke-dasharray="4 3"/>')
    p.append(text(370, 606, "Незалежне тактування ядра периферії (Kernel Clock Mux)", size=9.5, color="#ea580c", italic=True))

    render(os.path.join(OUT, "mcu-clock-tree-bus-domains.svg"), W, H, *p,
           title="Дерево тактування мікроконтролера та стробування такту шинних доменів")


# ── Fig 2: Peripheral Clock Gating & Timing Propagation ──────────────────────────
def fig_peripheral_clock_gating_timing():
    W, H = 900, 540
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=0))

    header, hw, hh = textbox(450, 28, "Схема клітини ICG та часова діаграма ввімкнення тактування з бар'єром",
                             size=12.5, bold=True, fill="#f6f8fa", stroke="#0969da", sw=1.5, pad=9)
    p.append(header)

    # ── Top Block: Schematic of Integrated Clock Gating (ICG) Cell ──
    p.append(rect(30, 60, 840, 145, fill="#f8fafc", stroke="#64748b", sw=1.4, rx=6))
    p.append(text(450, 82, "Апаратна комірка стробування такту (Integrated Clock Gating — ICG на базі Latch + AND)", size=11, color="#0f172a", bold=True))

    # CLK Input
    p.append(text(75, 128, "CLK_IN", size=10, color="#1e293b", bold=True))
    p.append(line(120, 128, 235, 128, color="#1e293b", sw=1.8))
    p.append(circle(235, 128, 3, fill="#1e293b", stroke="#1e293b", sw=1))

    # Inverter bubble before latch clock
    p.append(line(235, 128, 235, 148, color="#1e293b", sw=1.5))
    p.append(circle(235, 151, 3, fill="#ffffff", stroke="#1e293b", sw=1.5))
    p.append(line(235, 154, 265, 154, color="#1e293b", sw=1.5))

    # EN Input from RCC Register
    p.append(text(75, 172, "EN (RCC)", size=10, color="#0284c7", bold=True))
    p.append(arrow(120, 172, 265, 172, color="#0284c7", sw=1.8))

    # Transparent Low Latch
    latch_box, lw, lh = textbox(315, 163, "Negative-edge\nLatch\n(D-Latch, активна 0)", size=9.5, bold=True, fill="#e0f2fe", stroke="#0284c7", sw=1.3, pad=6)
    p.append(latch_box)

    # Latch Output EN_LAT
    p.append(arrow(315 + lw/2, 163, 455, 163, color="#0284c7", sw=1.8))
    p.append(text(398, 152, "EN_LAT (без глітчів)", size=9.5, color="#0284c7", italic=True))

    # AND Gate
    p.append(line(235, 128, 455, 128, color="#1e293b", sw=1.8))
    and_box, aw, ah = textbox(490, 145, "AND\nGate", size=10, bold=True, fill="#fef3c7", stroke="#d97706", sw=1.4, pad=7)
    p.append(and_box)

    # Gated Clock Output
    p.append(arrow(490 + aw/2, 145, 605, 145, color="#16a34a", sw=2.2))
    p.append(text(675, 145, "GCLK (Периферія)", size=10, color="#16a34a", bold=True))

    # Glitch Warning Note
    p.append(rect(615, 75, 245, 48, fill="#fff1f2", stroke="#e11d48", sw=1.2, rx=4))
    p.append(text(737, 93, "Запобігання Runt-імпульсам:", size=9.5, color="#be123c", bold=True))
    p.append(text(737, 110, "Latch блокує переходи EN при CLK=1", size=9, color="#be123c"))

    # ── Bottom Block: Timing Waveforms with Race Condition & Barrier ──
    p.append(rect(30, 220, 840, 300, fill="#f8fafc", stroke="#64748b", sw=1.4, rx=6))
    p.append(text(450, 242, "Часова діаграма затримки поширення такту та захист бар'єром читання", size=11, color="#0f172a", bold=True))

    # Time Axis & Cycles
    t_start = 180
    t_step = 68
    cycles = ["T0 (STR)", "T1 (Bridge)", "T2 (Latch)", "T3 (GCLK ON)", "T4 (Valid)"]
    for i, c_name in enumerate(cycles):
        cx = t_start + i * t_step * 1.8
        p.append(line(cx, 258, cx, 505, color="#e2e8f0", sw=1.0, dash="3 3"))
        p.append(text(cx, 268, c_name, size=9.5, color="#64748b", bold=True))

    # Signal Labels on Left
    sig_y = [
        (298, "1. HCLK (Ядро)", "#1e293b"),
        (340, "2. RCC_ENR Запис", "#0284c7"),
        (382, "3. EN_LAT (ICG)", "#0284c7"),
        (424, "4. GCLK Периферії", "#16a34a"),
        (470, "5. Доступ до регістра", "#9333ea"),
    ]
    for y_pos, s_label, s_col in sig_y:
        p.append(text(100, y_pos + 4, s_label, size=10, color=s_col, bold=True, anchor="middle"))

    # 1. HCLK Clock pulses
    _clock_wave_timing(p, t_start - 20, 298, t_start + 4.8 * t_step * 1.8, n=9, col="#1e293b")

    # 2. RCC Write Signal (goes high at T0)
    p.append('<path d="M %d 350 L %d 350 L %d 330 L %d 330" fill="none" stroke="#0284c7" stroke-width="2.0"/>'
             % (t_start - 20, t_start, t_start + 10, t_start + 4.8 * t_step * 1.8))

    # 3. EN_LAT Signal (propagates at falling edge in T2)
    t_latch_edge = t_start + 1.6 * t_step * 1.8
    p.append('<path d="M %d 392 L %d 392 L %d 372 L %d 372" fill="none" stroke="#0284c7" stroke-width="2.0"/>'
             % (t_start - 20, t_latch_edge, t_latch_edge + 10, t_start + 4.8 * t_step * 1.8))

    # 4. GCLK (Clock only active after T3)
    p.append('<line x1="%d" y1="434" x2="%d" y2="434" stroke="#94a3b8" stroke-width="2.0"/>' % (t_start - 20, t_start + 2.2 * t_step * 1.8))
    _clock_wave_timing(p, t_start + 2.2 * t_step * 1.8, 434, t_start + 4.8 * t_step * 1.8, n=5, col="#16a34a")

    # 5. Register Access scenarios
    # Scenario A: Immediate write without delay (HardFault / Bus Error)
    err_x = t_start + 0.9 * t_step * 1.8
    p.append(rect(err_x - 35, 452, 70, 24, fill="#ffe4e6", stroke="#e11d48", sw=1.3, rx=3))
    p.append(text(err_x, 468, "Прямий запис", size=9, color="#be123c", bold=True))
    p.append(text(err_x, 494, "BusFault / Зависання!", size=9.5, color="#e11d48", bold=True))
    p.append(line(err_x, 452, err_x, 436, color="#e11d48", sw=1.5, dash="2 2"))

    # Scenario B: Access with Dummy Read / Barrier (Safe)
    safe_x = t_start + 3.8 * t_step * 1.8
    p.append(rect(safe_x - 55, 452, 110, 24, fill="#dcfce7", stroke="#16a34a", sw=1.3, rx=3))
    p.append(text(safe_x, 468, "Після Dummy Read", size=9, color="#15803d", bold=True))
    p.append(text(safe_x, 494, "Успішна транзакція", size=9.5, color="#16a34a", bold=True))
    p.append(line(safe_x, 452, safe_x, 436, color="#16a34a", sw=1.5, dash="2 2"))

    render(os.path.join(OUT, "peripheral-clock-gating-timing.svg"), W, H, *p,
           title="Схема комірки ICG та часова діаграма стробування тактування з бар'єром")


def _clock_wave_timing(p, x0, y, x1, n, col):
    step = (x1 - x0) / (2 * n)
    hi, lo = y - 10, y + 10
    pts = [(x0, lo)]
    x = x0
    for i in range(n):
        pts.append((x, hi)); x += step
        pts.append((x, hi)); pts.append((x, lo)); x += step
        pts.append((x, lo))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % pt for pt in pts[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, col))


if __name__ == "__main__":
    fig_mcu_clock_tree_bus_domains()
    fig_peripheral_clock_gating_timing()
    print("OK: Figures generated in", OUT)
