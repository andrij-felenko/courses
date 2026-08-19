# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN_COL = "#c0392b"
OK_COL   = "#27ae60"
BUS_COL  = "#2457d6"
WARN_BG  = "#fdecea"
OK_BG    = "#eef6ef"
ACCENT   = "#d97706"
ACCENT_BG = "#fef8ee"


def polyline(pts, color=LINE, sw=1.5, fill="none"):
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{points}" fill="{fill}" stroke="{color}" stroke-width="{sw:.1f}"/>'


def fig_single_wire_schematics():
    W, H = 900, 430
    p = []
    
    # 3 columns for 3 topologies
    cols = [
        ("1. Відкритий стік (Open-Drain)", 25, 270),
        ("2. Розв'язка діодом Шотткі", 315, 270),
        ("3. Внутрішній комутатор (HDSEL)", 605, 270)
    ]
    
    # Common header boxes
    for title, cx, cw in cols:
        p.append(rect(cx, 30, cw, 360, fill=FILL, stroke=LINE, sw=1.5, rx=8))
        p.append(fitbox(cx + 10, 40, cw - 20, 28, title, size=11, bold=True, fill=BG, stroke=BUS_COL))

    # --- TOPOLOGY 1: Open-Drain ---
    # MCU block
    p.append(rect(40, 85, 105, 160, fill=BG, stroke=LINE, sw=1.5))
    p.append(text(92, 108, "MCU 1", size=11, bold=True))
    p.append(text(92, 130, "TX (OD)", size=10, color=BUS_COL, bold=True))
    p.append(text(92, 152, "RX (Вхід)", size=10, color=MUTED))
    p.append(line(92, 178, 140, 178, color=LINE, sw=1.2))
    p.append(circle(140, 178, 2.5, fill=LINE, stroke=LINE))
    p.append(text(92, 215, "NMOS стік", size=9.5, color=MUTED))

    # MCU 2 block
    p.append(rect(175, 85, 105, 160, fill=BG, stroke=LINE, sw=1.5))
    p.append(text(228, 108, "MCU 2", size=11, bold=True))
    p.append(text(228, 130, "TX (OD)", size=10, color=BUS_COL, bold=True))
    p.append(text(228, 152, "RX (Вхід)", size=10, color=MUTED))
    p.append(line(180, 178, 228, 178, color=LINE, sw=1.2))
    p.append(circle(180, 178, 2.5, fill=LINE, stroke=LINE))
    
    # Shared wire & Pullup
    p.append(line(140, 178, 180, 178, color=BUS_COL, sw=2.5))
    p.append(circle(160, 178, 3.5, fill=BUS_COL, stroke=BUS_COL))
    p.append(line(160, 178, 160, 275, color=BUS_COL, sw=1.5))
    
    # Resistor
    p.append(rect(146, 275, 28, 48, fill=ACCENT_BG, stroke=ACCENT, sw=1.5))
    p.append(text(160, 303, "R_pu", size=10.5, bold=True, color=ACCENT))
    p.append(line(160, 323, 160, 345, color=LINE, sw=1.5))
    p.append(line(148, 345, 172, 345, color=LINE, sw=2))
    p.append(text(160, 362, "+3.3V", size=10, bold=True, color=POS))
    
    p.append(text(160, 262, "Спільна лінія", size=9.5, color=BUS_COL, bold=True))
    p.append(text(160, 405, "Монтажне «І», повільний спад RC", size=9.5, color=MUTED))

    # --- TOPOLOGY 2: Diode Mixing ---
    p.append(rect(330, 85, 100, 160, fill=BG, stroke=LINE, sw=1.5))
    p.append(text(380, 108, "MCU", size=11, bold=True))
    p.append(text(380, 138, "TX (Push-Pull)", size=9.5, color=WARN_COL, bold=True))
    p.append(text(380, 192, "RX (Вхід)", size=9.5, color=OK_COL, bold=True))
    
    # TX line through diode
    p.append(line(430, 138, 455, 138, color=LINE, sw=1.5))
    p.append(line(455, 138, 468, 138, color=LINE, sw=1.5))
    p.append(line(482, 126, 482, 150, color=LINE, sw=1.5))
    p.append(line(468, 126, 468, 150, color=LINE, sw=1.5))
    p.append(line(482, 126, 468, 138, color=LINE, sw=1.5))
    p.append(line(482, 150, 468, 138, color=LINE, sw=1.5))
    p.append(text(475, 118, "BAT54", size=9.5, color=ACCENT, bold=True))
    
    # RX line straight
    p.append(line(430, 192, 510, 192, color=LINE, sw=1.5))
    p.append(line(482, 138, 510, 138, color=LINE, sw=1.5))
    p.append(line(510, 138, 510, 192, color=BUS_COL, sw=2))
    p.append(circle(510, 165, 3.5, fill=BUS_COL, stroke=BUS_COL))
    
    # Bus line going out
    p.append(line(510, 165, 565, 165, color=BUS_COL, sw=2.5))
    p.append(arrow(510, 165, 560, 165, color=BUS_COL, sw=2))
    p.append(text(538, 154, "До шини", size=9.5, color=BUS_COL, bold=True))
    
    # Pullup resistor
    p.append(line(510, 165, 510, 275, color=BUS_COL, sw=1.5))
    p.append(rect(496, 275, 28, 48, fill=ACCENT_BG, stroke=ACCENT, sw=1.5))
    p.append(text(510, 303, "R_pu", size=10.5, bold=True, color=ACCENT))
    p.append(line(510, 323, 510, 345, color=LINE, sw=1.5))
    p.append(line(498, 345, 522, 345, color=LINE, sw=2))
    p.append(text(510, 362, "+3.3V", size=10, bold=True, color=POS))
    p.append(text(450, 405, "Захист виходу TX від зустрічного струму", size=9.5, color=MUTED))

    # --- TOPOLOGY 3: Internal Mux HDSEL ---
    p.append(rect(620, 85, 240, 255, fill=BG, stroke=BUS_COL, sw=1.8, rx=6))
    p.append(text(740, 108, "STM32 USART (HDSEL = 1)", size=10.5, color=BUS_COL, bold=True))
    
    p.append(rect(635, 128, 95, 52, fill=FILL, stroke=LINE, sw=1.2))
    p.append(text(682, 150, "TX Драйвер", size=10, bold=True))
    p.append(text(682, 168, "(Open-Drain)", size=9.5, color=MUTED))
    
    p.append(rect(635, 210, 95, 52, fill=FILL, stroke=LINE, sw=1.2))
    p.append(text(682, 232, "RX Приймач", size=10, bold=True))
    p.append(text(682, 250, "(Вхідний буфер)", size=9.5, color=MUTED))
    
    # Internal switch / tie
    p.append(line(730, 154, 775, 154, color=BUS_COL, sw=1.8))
    p.append(line(730, 236, 775, 236, color=BUS_COL, sw=1.8))
    p.append(line(775, 154, 775, 236, color=BUS_COL, sw=2))
    p.append(circle(775, 195, 3.5, fill=BUS_COL, stroke=BUS_COL))
    
    # Pin
    p.append(line(775, 195, 835, 195, color=BUS_COL, sw=2.5))
    p.append(circle(835, 195, 4, fill=BG, stroke=BUS_COL, sw=2))
    p.append(text(815, 184, "Пін TX", size=10, color=BUS_COL, bold=True))
    
    # Disconnected external RX note
    p.append(rect(640, 282, 200, 42, fill=OK_BG, stroke=OK_COL, sw=1.2, rx=4))
    p.append(text(740, 300, "Пін RX вільний для GPIO", size=9.5, color=OK_COL, bold=True))
    p.append(text(740, 315, "Внутрішній зворотний зв'язок", size=9, color=MUTED))
    p.append(text(740, 405, "Один пін на платі, без зовнішніх діодів", size=9.5, color=MUTED))

    render(os.path.join(OUT, "single-wire-schematics.svg"), W, H, *p, title="Три схемотехнічні підходи до однопровідного UART")


def fig_rs485_transceiver_timing():
    W, H = 900, 460
    p = []
    
    # Top Section: Transceiver Block Diagram
    p.append(rect(30, 20, 840, 155, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(170, 42, "Трансивер RS-485 (MAX485 / SN65HVD)", size=11, bold=True, color=BUS_COL))
    
    # MCU on left
    p.append(rect(50, 55, 140, 105, fill=BG, stroke=LINE, sw=1.5))
    p.append(text(120, 78, "Мікроконтролер", size=10.5, bold=True))
    p.append(text(120, 98, "TXD / UART_TX", size=9.5, color=MUTED))
    p.append(text(120, 118, "RXD / UART_RX", size=9.5, color=MUTED))
    p.append(text(120, 140, "DE_PIN (GPIO/DEM)", size=9.5, color=ACCENT, bold=True))
    
    # Transceiver IC in center
    p.append(rect(300, 50, 260, 112, fill=BG, stroke=BUS_COL, sw=1.8, rx=6))
    p.append(text(430, 70, "Диференційний трансивер", size=11, bold=True, color=BUS_COL))
    
    # Driver D
    p.append(rect(320, 85, 75, 32, fill=OK_BG, stroke=OK_COL, sw=1.2))
    p.append(text(357, 105, "Драйвер D", size=9.5, bold=True, color=OK_COL))
    
    # Receiver R
    p.append(rect(320, 122, 75, 30, fill=WARN_BG, stroke=WARN_COL, sw=1.2))
    p.append(text(357, 141, "Приймач R", size=9.5, bold=True, color=WARN_COL))
    
    # Lines between MCU and Transceiver
    p.append(line(190, 95, 320, 95, color=LINE, sw=1.5))
    p.append(arrow(190, 95, 315, 95, color=LINE, sw=1.5))
    p.append(text(255, 88, "DI (TX)", size=9.5, color=MUTED))
    
    p.append(line(320, 137, 190, 137, color=LINE, sw=1.5))
    p.append(arrow(320, 137, 195, 137, color=LINE, sw=1.5))
    p.append(text(255, 130, "RO (RX)", size=9.5, color=MUTED))
    
    # DE / RE Control line
    p.append(line(190, 140, 240, 140, color=ACCENT, sw=1.5))
    p.append(line(240, 140, 240, 60, color=ACCENT, sw=1.5))
    p.append(line(240, 60, 410, 60, color=ACCENT, sw=1.5))
    p.append(line(410, 60, 410, 85, color=ACCENT, sw=1.5))
    p.append(arrow(410, 60, 410, 82, color=ACCENT, sw=1.5))
    p.append(text(435, 95, "DE / /RE", size=9.5, bold=True, color=ACCENT))
    
    # Bus A / B outputs
    p.append(line(395, 100, 620, 100, color=POS, sw=2))
    p.append(line(395, 135, 620, 135, color=NEG, sw=2))
    p.append(circle(620, 100, 3.5, fill=POS, stroke=POS))
    p.append(circle(620, 135, 3.5, fill=NEG, stroke=NEG))
    p.append(text(640, 104, "Лінія A (D+)", size=10, bold=True, color=POS, anchor="start"))
    p.append(text(640, 139, "Лінія B (D−)", size=10, bold=True, color=NEG, anchor="start"))
    
    # Termination resistor
    p.append(line(590, 100, 590, 135, color=LINE, sw=1.5))
    p.append(rect(578, 110, 24, 18, fill=ACCENT_BG, stroke=ACCENT, sw=1.2))
    p.append(text(590, 123, "120Ω", size=9, color=ACCENT, bold=True))

    # Bottom Section: Timing Diagram
    p.append(rect(30, 190, 840, 250, fill=BG, stroke=LINE, sw=1.5, rx=8))
    p.append(text(190, 212, "Часова діаграма передачі та пастка переривання TXE vs TC", size=11, bold=True))
    
    t_labels = [
        (235, "Сигнал DE (Driver Enable)"),
        (275, "Дані TXD (Кадр UART)"),
        (320, "Прапорець TXE (TDR порожній)"),
        (360, "Прапорець TC (Передача завершена)"),
        (400, "Стан шини RS-485 (A/B)")
    ]
    for y, lbl in t_labels:
        p.append(text(45, y + 4, lbl, size=9.5, bold=True, anchor="start", color=INK))
        p.append(line(270, y, 850, y, color="#e5e7eb", sw=1))

    # Time markers (vertical dashed lines)
    p.append(line(320, 222, 320, 420, color=MUTED, sw=1, dash="2 2"))
    p.append(text(320, 220, "T_pre", size=9, color=MUTED))
    p.append(line(350, 222, 350, 420, color=MUTED, sw=1, dash="2 2"))
    p.append(text(350, 220, "Старт", size=9, color=MUTED))
    p.append(line(470, 222, 470, 420, color=WARN_COL, sw=1.2, dash="3 3"))
    p.append(text(470, 220, "TXE!", size=9.5, color=WARN_COL, bold=True))
    p.append(line(690, 222, 690, 420, color=OK_COL, sw=1.2, dash="3 3"))
    p.append(text(690, 220, "TC!", size=9.5, color=OK_COL, bold=True))
    p.append(line(730, 222, 730, 420, color=MUTED, sw=1, dash="2 2"))
    p.append(text(730, 220, "T_post", size=9, color=MUTED))

    # Waveform 1: DE signal
    de_pts = [(270, 245), (320, 245), (320, 230), (730, 230), (730, 245), (850, 245)]
    p.append(polyline(de_pts, color=ACCENT, sw=2))
    p.append(text(525, 226, "DE = 1 (Драйвер активний)", size=9.5, color=ACCENT, bold=True))

    # Waveform 2: TXD data
    txd_pts = [(270, 265), (350, 265), (350, 282), (390, 282), (390, 265), (430, 265),
               (430, 282), (510, 282), (510, 265), (590, 265), (590, 282), (630, 282),
               (630, 265), (850, 265)]
    p.append(polyline(txd_pts, color=BUS_COL, sw=1.8))
    p.append(text(370, 292, "Start", size=9, color=MUTED))
    p.append(text(510, 274, "Біти даних (D0..D7)", size=9.5, color=BUS_COL, bold=True))
    p.append(text(660, 260, "Stop", size=9, color=MUTED))

    # Waveform 3: TXE Flag
    txe_pts = [(270, 328), (470, 328), (470, 312), (550, 312), (550, 328), (850, 328)]
    p.append(polyline(txe_pts, color=WARN_COL, sw=1.8))
    p.append(text(615, 320, "Помилка: скидання DE тут обріже кадр!", size=9, color=WARN_COL, bold=True))

    # Waveform 4: TC Flag
    tc_pts = [(270, 368), (690, 368), (690, 352), (770, 352), (770, 368), (850, 368)]
    p.append(polyline(tc_pts, color=OK_COL, sw=2))
    p.append(text(745, 360, "Правильно: скидати DE по TC", size=9.5, color=OK_COL, bold=True))

    # Waveform 5: Bus State
    p.append(line(270, 400, 320, 400, color=MUTED, sw=1.5, dash="3 3"))
    p.append(text(295, 393, "Hi-Z", size=9, color=MUTED))
    p.append(rect(320, 390, 410, 22, fill="#eef3fc", stroke=BUS_COL, sw=1.2, rx=3))
    p.append(text(525, 405, "Диференційний сигнал на витій парі A / B", size=9.5, color=BUS_COL, bold=True))
    p.append(line(730, 400, 850, 400, color=MUTED, sw=1.5, dash="3 3"))
    p.append(text(780, 393, "Hi-Z (Слухаємо)", size=9, color=MUTED))

    render(os.path.join(OUT, "rs485-transceiver-timing.svg"), W, H, *p, title="Часова діаграма передачі кадру та керування DE")


def fig_local_echo_and_turnaround():
    W, H = 900, 410
    p = []
    
    # Left Block: Local Echo Mechanism
    p.append(rect(30, 30, 405, 355, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(fitbox(45, 42, 375, 28, "Локальне відлуння (Local Echo)", size=11, bold=True, fill=BG, stroke=BUS_COL))
    
    # MCU Node
    p.append(rect(50, 85, 115, 135, fill=BG, stroke=LINE, sw=1.5))
    p.append(text(107, 108, "MCU Вузол", size=11, bold=True))
    p.append(text(107, 138, "TX_OUT", size=9.5, color=BUS_COL, bold=True))
    p.append(text(107, 190, "RX_IN", size=9.5, color=WARN_COL, bold=True))
    
    # Shared line
    p.append(line(165, 138, 240, 138, color=BUS_COL, sw=2))
    p.append(line(240, 138, 240, 190, color=WARN_COL, sw=2, dash="3 3"))
    p.append(line(240, 190, 165, 190, color=WARN_COL, sw=2))
    p.append(arrow(240, 190, 170, 190, color=WARN_COL, sw=2))
    p.append(circle(240, 164, 4, fill=WARN_COL, stroke=WARN_COL))
    
    p.append(rect(260, 105, 160, 105, fill=WARN_BG, stroke=WARN_COL, sw=1.2, rx=4))
    p.append(text(340, 126, "Власна передача", size=10, bold=True, color=WARN_COL))
    p.append(text(340, 145, "повертається в RX FIFO!", size=9.5, color=WARN_COL))
    p.append(text(340, 172, "Потрібно фільтрувати", size=9, color=MUTED))
    p.append(text(340, 190, "або вимикати /RE", size=9, color=MUTED))
    
    # Echo applications box
    p.append(rect(50, 235, 365, 135, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(text(232, 255, "Діагностика: виявлення колізій", size=10.5, bold=True, color=OK_COL))
    p.append(text(65, 280, "1. Передано байт 0x55 (01010101b)", size=9.5, anchor="start", color=INK))
    p.append(text(65, 302, "2. Прийнято відлуння: 0x15 (00010101b)", size=9.5, anchor="start", color=WARN_COL, bold=True))
    p.append(text(65, 325, "3. Висновок: інший вузол притиснув лінію в 0!", size=9.5, anchor="start", color=POS, bold=True))
    p.append(text(65, 348, "   → Миттєва фіксація колізії на шині", size=9, anchor="start", color=MUTED))

    # Right Block: Turnaround Time & Collision Danger
    p.append(rect(455, 30, 415, 355, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(fitbox(470, 42, 385, 28, "Час перемикання (Turnaround Time)", size=11, bold=True, fill=BG, stroke=ACCENT))
    
    # Waveform: Master TX, Turnaround Guard Time, Slave TX
    p.append(text(475, 95, "Ведучий (TX)", size=10, bold=True, anchor="start", color=BUS_COL))
    p.append(text(475, 155, "Ведений (TX)", size=10, bold=True, anchor="start", color=OK_COL))
    p.append(text(475, 215, "Стан шини", size=10, bold=True, anchor="start", color=INK))
    
    # Master Frame
    p.append(rect(560, 80, 140, 26, fill="#eef3fc", stroke=BUS_COL, sw=1.5, rx=3))
    p.append(text(630, 97, "Запит ведучого", size=9.5, bold=True, color=BUS_COL))
    
    # Turnaround Guard interval
    p.append(rect(700, 80, 60, 100, fill=ACCENT_BG, stroke=ACCENT, sw=1.2))
    p.append(text(730, 126, "T_turnaround", size=9, bold=True, color=ACCENT))
    p.append(text(730, 142, "(Захисний час)", size=9, color=MUTED))
    
    # Slave Frame (Correct)
    p.append(rect(760, 140, 100, 26, fill=OK_BG, stroke=OK_COL, sw=1.5, rx=3))
    p.append(text(810, 157, "Відповідь", size=9.5, bold=True, color=OK_COL))
    
    # Collision scenario below
    p.append(rect(470, 235, 385, 135, fill=WARN_BG, stroke=WARN_COL, sw=1.2, rx=6))
    p.append(text(662, 255, "Небезпека: замалий захисний інтервал", size=10.5, bold=True, color=WARN_COL))
    p.append(text(485, 280, "• Ведучий ще вимикає драйвер (t_disable ~ 150 нс)", size=9.5, anchor="start", color=INK))
    p.append(text(485, 302, "• Ведений уже вмикає свій вихід на передачу", size=9.5, anchor="start", color=INK))
    p.append(text(485, 325, "• Результат: зустрічний струм, провал напруги,", size=9.5, anchor="start", color=POS, bold=True))
    p.append(text(485, 348, "  спотворення Start-біта відповіді веденого!", size=9.5, anchor="start", color=POS, bold=True))

    render(os.path.join(OUT, "local-echo-and-turnaround.svg"), W, H, *p, title="Локальне відлуння та захисний інтервал Turnaround")


def fig_master_slave_polling():
    W, H = 900, 380
    p = []
    
    p.append(rect(30, 20, 840, 345, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(fitbox(50, 32, 800, 28, "Цикл опитування «Господар — Підлеглий» (Master-Slave Polling)", size=11, bold=True, fill=BG, stroke=BUS_COL))
    
    # Timeline bar
    p.append(line(60, 110, 840, 110, color=LINE, sw=2))
    p.append(arrow(60, 110, 835, 110, color=LINE, sw=2))
    p.append(text(830, 95, "Час t", size=10.5, bold=True, color=MUTED))
    
    # Step 1: Master Polls Node #1
    p.append(rect(70, 75, 130, 30, fill="#eef3fc", stroke=BUS_COL, sw=1.5, rx=4))
    p.append(text(135, 94, "Запит [ID=1, CMD]", size=9, bold=True, color=BUS_COL))
    
    # Guard interval 1
    p.append(rect(200, 85, 35, 20, fill=ACCENT_BG, stroke=ACCENT, sw=1))
    p.append(text(217, 98, "T_grd", size=9, color=ACCENT))
    
    # Step 2: Node #1 Responds
    p.append(rect(235, 75, 135, 30, fill=OK_BG, stroke=OK_COL, sw=1.5, rx=4))
    p.append(text(302, 94, "Відповідь [ID=1, DATA]", size=9, bold=True, color=OK_COL))
    
    # Inter-frame silence
    p.append(rect(370, 85, 45, 20, fill=FILL, stroke=MUTED, sw=1))
    p.append(text(392, 98, "t_idle", size=9, color=MUTED))
    
    # Step 3: Master Polls Node #2 (Offline / Silent)
    p.append(rect(415, 75, 130, 30, fill="#eef3fc", stroke=BUS_COL, sw=1.5, rx=4))
    p.append(text(480, 94, "Запит [ID=2, CMD]", size=9, bold=True, color=BUS_COL))
    
    # Timeout window for Node #2
    p.append(rect(545, 68, 150, 42, fill=WARN_BG, stroke=WARN_COL, sw=1.5, rx=4))
    p.append(text(620, 86, "Вікно таймауту T_timeout", size=9, bold=True, color=WARN_COL))
    p.append(text(620, 102, "(Вузол 2 не відповідає)", size=9, color=WARN_COL))
    
    # Step 4: Master Polls Node #3
    p.append(rect(700, 75, 120, 30, fill="#eef3fc", stroke=BUS_COL, sw=1.5, rx=4))
    p.append(text(760, 94, "Запит [ID=3, CMD]", size=9, bold=True, color=BUS_COL))
    
    # Bottom explanation panels
    p.append(rect(60, 145, 365, 195, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(text(242, 168, "Дисципліна обміну «Запит — Відповідь»", size=10.5, bold=True, color=BUS_COL))
    p.append(text(75, 195, "• Ведений ніколи не передає без прямого запиту", size=9.5, anchor="start", color=INK))
    p.append(text(75, 218, "• Широкомовні команди (Broadcast) виконуються", size=9.5, anchor="start", color=INK))
    p.append(text(75, 235, "  всіма вузлами БЕЗ підтвердження (ACK)", size=9, anchor="start", color=MUTED))
    p.append(text(75, 258, "• Захисний інтервал T_grd унеможливлює колізію", size=9.5, anchor="start", color=OK_COL, bold=True))
    p.append(text(75, 280, "• Сувора адресація: кожен кадр містить унікальний ID", size=9.5, anchor="start", color=INK))
    p.append(text(75, 302, "• Контрольна сума (CRC16/CRC32) валідує цілісність", size=9.5, anchor="start", color=INK))

    p.append(rect(455, 145, 385, 195, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(text(647, 168, "Обробка помилок та захист від зависання", size=10.5, bold=True, color=WARN_COL))
    p.append(text(470, 195, "• Якщо ведений відключений або пошкоджений,", size=9.5, anchor="start", color=INK))
    p.append(text(470, 212, "  таймер T_timeout спрацьовує і звільняє шину", size=9.5, anchor="start", color=WARN_COL, bold=True))
    p.append(text(470, 235, "• T_timeout = T_turnaround + T_frame + T_margin", size=9.5, anchor="start", color=INK))
    p.append(text(470, 258, "• Лічильник повторних спроб (Retry Count, 1..3)", size=9.5, anchor="start", color=INK))
    p.append(text(470, 280, "• Після вичерпання спроб — фіксація збою вузла", size=9.5, anchor="start", color=POS, bold=True))
    p.append(text(470, 302, "  та перехід до опитування наступного ID", size=9, anchor="start", color=MUTED))

    render(os.path.join(OUT, "master-slave-polling.svg"), W, H, *p, title="Цикл опитування Master-Slave Polling")


if __name__ == "__main__":
    fig_single_wire_schematics()
    fig_rs485_transceiver_timing()
    fig_local_echo_and_turnaround()
    fig_master_slave_polling()
    print("All figures generated successfully.")
