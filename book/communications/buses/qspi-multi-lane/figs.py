# -*- coding: utf-8 -*-
"""Генератор векторних фігур SVG для теми «QSPI та багатолінійний SPI».
Використовує спільний модуль svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра сигналів та елементів
CLK_COL  = NEG          # Тактовий сигнал SCK (синій #2457d6)
CS_COL   = POS          # Вибір кристала CS# (червоний #c0392b)
DAT_COL  = "#7a5fb0"    # Лінії даних IO0..IO3 (фіолетовий)
DQS_COL  = FIELD        # Строб даних DQS (зелений #27ae60)
HI_Z_COL = MUTED        # Високоімпедансний стан Hi-Z (сірий)
BOX_BG   = FILL         # Фонова заливка блоків (#f4f6f8)
HL_BG    = "#eef2ff"    # Підсвітка активних фаз (блакитний)
ALT_BG   = "#fdf8e2"    # Підсвітка службових фаз (жовтуватий)
WARN_BG  = "#fef2f2"    # Затримки / Dummy (червонуватий)


# ── 1. Еволюція ліній: Standard SPI -> Dual -> Quad -> Octal ────────────────
def fig_pin_transition():
    W, H = 840, 480
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    # Секція 1: Класичний SPI (1-бітний повний дуплекс)
    p.append(rect(30, 40, 360, 190, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(210, 65, "Класичний SPI (1 біт, повний дуплекс)", size=13, color=INK, bold=True))
    
    # Контролер і Flash
    p.append(rect(50, 85, 90, 130, fill=BOX_BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(95, 155, "MCU SPI", size=12, color=INK, bold=True))
    p.append(rect(280, 85, 90, 130, fill=BOX_BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(325, 155, "Flash", size=12, color=INK, bold=True))

    # Лінії Standard SPI
    lines_std = [
        (105, "CS#", CS_COL, "→"),
        (135, "SCK", CLK_COL, "→"),
        (165, "MOSI (IO0)", DAT_COL, "→"),
        (195, "MISO (IO1)", DAT_COL, "←"),
    ]
    for y, label, col, direction in lines_std:
        if direction == "→":
            p.append(arrow(140, y, 280, y, color=col, sw=1.6))
        else:
            p.append(arrow(280, y, 140, y, color=col, sw=1.6))
        p.append(text(210, y - 5, label, size=10, color=col, bold=True))

    # Секція 2: Quad-SPI (4 біти, напівдуплекс, мультиплексовані ніжки)
    p.append(rect(430, 40, 380, 190, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(620, 65, "Quad-SPI / QSPI (4 біти, напівдуплекс)", size=13, color=INK, bold=True))
    
    p.append(rect(450, 85, 90, 130, fill=BOX_BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(495, 155, "QSPI Ctrl", size=12, color=INK, bold=True))
    p.append(rect(700, 85, 90, 130, fill=BOX_BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(745, 155, "Quad Flash", size=12, color=INK, bold=True))

    lines_qspi = [
        (100, "CS#", CS_COL, "→"),
        (125, "SCK", CLK_COL, "→"),
        (150, "IO0 (MOSI / Data0)", DAT_COL, "⇄"),
        (170, "IO1 (MISO / Data1)", DAT_COL, "⇄"),
        (190, "IO2 (WP# / Data2)", DAT_COL, "⇄"),
        (210, "IO3 (HOLD# / Data3)", DAT_COL, "⇄"),
    ]
    for y, label, col, direction in lines_qspi:
        if direction == "→":
            p.append(arrow(540, y, 700, y, color=col, sw=1.5))
        else:
            p.append(line(540, y, 700, y, color=col, sw=1.5))
            p.append(circle(540, y, 2.5, fill=col, stroke=col))
            p.append(circle(700, y, 2.5, fill=col, stroke=col))
        p.append(text(620, y - 4, label, size=10, color=col, bold=True))

    # Секція 3: Порівняльна таблиця пропускної здатності шин
    p.append(rect(30, 250, 780, 205, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(420, 275, "Порівняння інтерфейсів послідовної та паралельної Flash-пам'яті", size=13, color=INK, bold=True))

    headers = ["Інтерфейс", "Кількість ліній IO", "Тактова частота", "Режим даних", "Швидкість передачі", "Кількість ніжок"]
    col_x = [45, 160, 285, 410, 545, 680, 800]
    
    # Заголовок таблиці
    p.append(rect(45, 290, 750, 26, fill=BOX_BG, stroke=LINE, sw=1.0, rx=2))
    for i in range(len(headers)):
        cx = (col_x[i] + col_x[i+1]) / 2
        p.append(text(cx, 307, headers[i], size=10, color=INK, bold=True))

    rows_data = [
        ("Standard SPI", "1 (MOSI/MISO)", "до 50 МГц", "SDR (1 біт/такт)", "6.25 МБ/с", "4 ніжки"),
        ("Dual-SPI", "2 (IO0..IO1)", "до 104 МГц", "SDR (2 біти/такт)", "26.0 МБ/с", "4 ніжки"),
        ("Quad-SPI (QSPI)", "4 (IO0..IO3)", "до 133 МГц", "SDR (4 біти/такт)", "66.5 МБ/с", "6 ніжок"),
        ("Quad-DDR / QPI", "4 (IO0..IO3)", "до 100 МГц DDR", "DDR (8 бітів/такт)", "100.0 МБ/с", "6 ніжок"),
        ("Octal-SPI / xSPI", "8 (IO0..IO7 + DQS)", "до 200 МГц DDR", "DDR (16 бітів/такт)", "400.0 МБ/с", "11–12 ніжок"),
    ]

    y_row = 320
    for r_idx, row in enumerate(rows_data):
        bg = "#ffffff" if r_idx % 2 == 0 else "#f9fafb"
        p.append(rect(45, y_row, 750, 24, fill=bg, stroke="#e5e7eb", sw=0.8, rx=0))
        for i in range(len(row)):
            cx = (col_x[i] + col_x[i+1]) / 2
            col_t = POS if i == 4 and r_idx >= 2 else INK
            bld = True if i == 0 or (i == 4 and r_idx >= 2) else False
            p.append(text(cx, y_row + 16, row[i], size=10, color=col_t, bold=bld))
        y_row += 24

    return render(os.path.join(OUT, "pin-transition.svg"), W, H, *p)


# ── 2. Фази транзакції QSPI (1-1-1 проти 1-1-4, 1-4-4 та 4-4-4) ────────────
def fig_transaction_phases():
    W, H = 860, 520
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    p.append(text(430, 35, "Анатомія транзакції швидкого читання (Fast Read Quad I/O, 1-4-4)", size=14, color=INK, bold=True))

    # Візуалізація 5 фаз транзакції 1-4-4
    phases = [
        (40, 130, "1. Instruction Phase", "Команда 0xEB", "1 лінія (IO0)", "8 тактів SCLK", HL_BG, POS),
        (170, 200, "2. Address Phase", "Адреса A23..A0", "4 лінії (IO0..IO3)", "6 тактів (24 біти)", HL_BG, CLK_COL),
        (370, 130, "3. Mode / Alternate", "Mode Bits (M7..M0)", "4 лінії (IO0..IO3)", "2 такти (XIP)", ALT_BG, DAT_COL),
        (500, 150, "4. Dummy Clocks", "Затримка вибірки", "Hi-Z (немає даних)", "4–10 тактів", WARN_BG, POS),
        (650, 170, "5. Data Phase", "Потік даних D7..D0", "4 лінії (IO0..IO3)", "2 такти на байт", "#dcfce7", FIELD),
    ]

    for x, w, title, desc, lines_cnt, clocks, bg, stroke_col in phases:
        p.append(rect(x, 55, w, 110, fill=bg, stroke=stroke_col, sw=1.5, rx=4))
        p.append(text(x + w / 2, 75, title, size=11, color=stroke_col, bold=True))
        p.append(text(x + w / 2, 95, desc, size=10, color=INK, bold=True))
        p.append(text(x + w / 2, 115, lines_cnt, size=10, color=MUTED))
        p.append(text(x + w / 2, 135, clocks, size=10, color=INK))

    # Сигнальні діаграми на лініях CS, SCK, IO0..IO3
    y_sig_base = 185
    p.append(rect(30, y_sig_base, 800, 175, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))

    # Лінія CS
    p.append(text(75, y_sig_base + 25, "CS#", size=11, color=CS_COL, bold=True, anchor="end"))
    p.append(line(85, y_sig_base + 15, 110, y_sig_base + 15, color=CS_COL, sw=2.0))
    p.append(line(110, y_sig_base + 15, 115, y_sig_base + 35, color=CS_COL, sw=2.0))
    p.append(line(115, y_sig_base + 35, 780, y_sig_base + 35, color=CS_COL, sw=2.0))
    p.append(line(780, y_sig_base + 35, 785, y_sig_base + 15, color=CS_COL, sw=2.0))
    p.append(line(785, y_sig_base + 15, 810, y_sig_base + 15, color=CS_COL, sw=2.0))

    # Лінія SCK
    p.append(text(75, y_sig_base + 60, "SCK", size=11, color=CLK_COL, bold=True, anchor="end"))
    clk_x = 120
    p.append(line(85, y_sig_base + 65, clk_x, y_sig_base + 65, color=CLK_COL, sw=1.5))
    for i in range(26):
        p.append(line(clk_x + i * 25, y_sig_base + 65, clk_x + i * 25 + 6, y_sig_base + 50, color=CLK_COL, sw=1.5))
        p.append(line(clk_x + i * 25 + 6, y_sig_base + 50, clk_x + i * 25 + 13, y_sig_base + 50, color=CLK_COL, sw=1.5))
        p.append(line(clk_x + i * 25 + 13, y_sig_base + 50, clk_x + i * 25 + 19, y_sig_base + 65, color=CLK_COL, sw=1.5))
        p.append(line(clk_x + i * 25 + 19, y_sig_base + 65, clk_x + i * 25 + 25, y_sig_base + 65, color=CLK_COL, sw=1.5))

    # Лінії IO0..IO3
    # IO0
    p.append(text(75, y_sig_base + 95, "IO0", size=10, color=DAT_COL, bold=True, anchor="end"))
    p.append(rect(120, y_sig_base + 85, 120, 20, fill="#f3f4f6", stroke=POS, sw=1.2, rx=2))
    p.append(text(180, y_sig_base + 98, "Cmd 0xEB (1-біт)", size=10, color=POS, bold=True))
    p.append(rect(240, y_sig_base + 85, 140, 20, fill="#f3f4f6", stroke=CLK_COL, sw=1.2, rx=2))
    p.append(text(310, y_sig_base + 98, "A20, A16... A0", size=10, color=CLK_COL, bold=True))
    p.append(rect(380, y_sig_base + 85, 70, 20, fill=ALT_BG, stroke=DAT_COL, sw=1.2, rx=2))
    p.append(text(415, y_sig_base + 98, "M4, M0", size=10, color=DAT_COL, bold=True))
    p.append(line(450, y_sig_base + 95, 590, y_sig_base + 95, color=HI_Z_COL, sw=1.5, dash="3,3"))
    p.append(text(520, y_sig_base + 92, "Hi-Z (Dummy)", size=10, color=MUTED))
    p.append(rect(590, y_sig_base + 85, 190, 20, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=2))
    p.append(text(685, y_sig_base + 98, "Data: D0, D4, D0, D4...", size=10, color=FIELD, bold=True))

    # IO1..IO3
    p.append(text(75, y_sig_base + 130, "IO1..IO3", size=10, color=DAT_COL, bold=True, anchor="end"))
    p.append(line(85, y_sig_base + 130, 240, y_sig_base + 130, color=HI_Z_COL, sw=1.5, dash="3,3"))
    p.append(text(160, y_sig_base + 125, "Hi-Z / WP# / HOLD#", size=10, color=MUTED))
    p.append(rect(240, y_sig_base + 120, 140, 20, fill="#f3f4f6", stroke=CLK_COL, sw=1.2, rx=2))
    p.append(text(310, y_sig_base + 133, "A23..A1, A22..A2...", size=10, color=CLK_COL, bold=True))
    p.append(rect(380, y_sig_base + 120, 70, 20, fill=ALT_BG, stroke=DAT_COL, sw=1.2, rx=2))
    p.append(text(415, y_sig_base + 133, "M7..M1", size=10, color=DAT_COL, bold=True))
    p.append(line(450, y_sig_base + 130, 590, y_sig_base + 130, color=HI_Z_COL, sw=1.5, dash="3,3"))
    p.append(text(520, y_sig_base + 125, "Hi-Z (Dummy)", size=10, color=MUTED))
    p.append(rect(590, y_sig_base + 120, 190, 20, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=2))
    p.append(text(685, y_sig_base + 133, "Data: D1..D3, D5..D7...", size=10, color=FIELD, bold=True))

    # Порівняння режимів протоколу
    p.append(rect(30, 380, 800, 120, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(430, 400, "Нотація режимів X-Y-Z (Instruction - Address - Data)", size=12, color=INK, bold=True))

    modes = [
        ("1-1-1 (Standard SPI)", "1 лінія", "1 лінія", "1 лінія", "0x03 / 0x0B (Fast Read)", "Базовий сумісний режим"),
        ("1-1-4 (Quad Output / QREAD)", "1 лінія", "1 лінія", "4 лінії", "0x6B (QREAD)", "Швидкий вивід даних"),
        ("1-4-4 (Quad I/O / 4READ)", "1 лінія", "4 лінії", "4 лінії", "0xEB (4READ / QIO)", "Адреса і дані по 4 лінії"),
        ("4-4-4 (QPI Mode)", "4 лінії", "4 лінії", "4 лінії", "0xEB / 0x0B у режимі QPI", "Максимальна швидкість XIP"),
    ]
    m_y = 422
    for name, ins, addr, dat, opc, note in modes:
        p.append(text(45, m_y, name, size=10, color=POS if "4-4-4" in name else INK, bold=True, anchor="start"))
        p.append(text(280, m_y, f"Команда: {ins} | Адреса: {addr} | Дані: {dat}", size=10, color=MUTED, anchor="start"))
        p.append(text(620, m_y, f"{opc} ({note})", size=10, color=FIELD if "4-4-4" in name else INK, anchor="start"))
        m_y += 20

    return render(os.path.join(OUT, "transaction-phases.svg"), W, H, *p)


# ── 3. SDR проти DDR і строб даних DQS в Octal-SPI ─────────────────────────
def fig_sdr_vs_ddr():
    W, H = 840, 440
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    p.append(text(420, 35, "Режими передачі даних: SDR (Single Data Rate) проти DDR (Double Data Rate)", size=14, color=INK, bold=True))

    # Ліва колонка: SDR (1 передача на період такту)
    p.append(rect(30, 60, 370, 355, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(215, 85, "SDR (Single Data Rate)", size=13, color=CLK_COL, bold=True))
    p.append(text(215, 105, "Вибірка лише на наростаючому фронті", size=10, color=MUTED))

    # SCK SDR
    p.append(text(45, 145, "SCK", size=11, color=CLK_COL, bold=True, anchor="start"))
    for i in range(4):
        x = 90 + i * 65
        p.append(rect(x + 32, 125, 2, 40, fill=POS, stroke="none")) # позначка вибірки
        p.append(line(x, 155, x + 32, 155, color=CLK_COL, sw=1.8))
        p.append(line(x + 32, 155, x + 32, 125, color=CLK_COL, sw=1.8))
        p.append(line(x + 32, 125, x + 65, 125, color=CLK_COL, sw=1.8))
        p.append(line(x + 65, 125, x + 65, 155, color=CLK_COL, sw=1.8))
        p.append(arrow(x + 32, 170, x + 32, 157, color=POS, sw=1.5))
        p.append(text(x + 32, 184, "Sample", size=10, color=POS, bold=True))

    # Data SDR (IO0..IO3)
    p.append(text(45, 220, "IO[3:0]", size=11, color=DAT_COL, bold=True, anchor="start"))
    for i in range(4):
        x = 90 + i * 65
        p.append(rect(x + 5, 205, 55, 30, fill=HL_BG, stroke=DAT_COL, sw=1.4, rx=3))
        p.append(text(x + 32, 224, f"Nibble {i}", size=10, color=INK, bold=True))

    # Підсумок SDR
    p.append(rect(45, 270, 340, 130, fill=BOX_BG, stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(215, 290, "Характеристики SDR:", size=11, color=INK, bold=True))
    p.append(text(60, 312, "• 1 передача (нібл) за 1 повний такт SCK", size=10, color=INK, anchor="start"))
    p.append(text(60, 332, "• При частоті 133 МГц: 133 млн ніблів/с", size=10, color=INK, anchor="start"))
    p.append(text(60, 352, "• Пропускна здатність: 66.5 МБайт/с", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(60, 372, "• Простий таймінг, фіксація затримки на платі", size=10, color=MUTED, anchor="start"))

    # Права колонка: DDR + DQS (2 передачі на такт + синхронізація стробом)
    p.append(rect(430, 60, 380, 355, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(620, 85, "DDR (Double Data Rate) + DQS", size=13, color=FIELD, bold=True))
    p.append(text(620, 105, "Вибірка на обох фронтах (наростаючий + спадний)", size=10, color=MUTED))

    # SCK DDR
    p.append(text(445, 140, "SCK", size=11, color=CLK_COL, bold=True, anchor="start"))
    for i in range(4):
        x = 490 + i * 70
        p.append(line(x, 150, x + 35, 150, color=CLK_COL, sw=1.8))
        p.append(line(x + 35, 150, x + 35, 125, color=CLK_COL, sw=1.8))
        p.append(line(x + 35, 125, x + 70, 125, color=CLK_COL, sw=1.8))
        p.append(line(x + 70, 125, x + 70, 150, color=CLK_COL, sw=1.8))

    # DQS (Data Strobe від Flash)
    p.append(text(445, 185, "DQS", size=11, color=DQS_COL, bold=True, anchor="start"))
    for i in range(4):
        x = 490 + i * 70
        p.append(line(x + 10, 195, x + 45, 195, color=DQS_COL, sw=1.8))
        p.append(line(x + 45, 195, x + 45, 170, color=DQS_COL, sw=1.8))
        p.append(line(x + 45, 170, x + 80, 170, color=DQS_COL, sw=1.8))
        p.append(line(x + 80, 170, x + 80, 195, color=DQS_COL, sw=1.8))
        # стрілки вибірки на обох фронтах DQS
        p.append(arrow(x + 45, 210, x + 45, 198, color=POS, sw=1.2))
        p.append(arrow(x + 80, 210, x + 80, 173, color=POS, sw=1.2))

    # Data DDR (IO0..IO7 / IO0..IO3)
    p.append(text(445, 235, "IO[7:0]", size=11, color=DAT_COL, bold=True, anchor="start"))
    for i in range(8):
        x = 495 + i * 35
        p.append(rect(x + 2, 220, 31, 28, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=2))
        p.append(text(x + 17, 238, f"B{i}", size=10, color=INK, bold=True))

    # Підсумок DDR
    p.append(rect(445, 270, 350, 130, fill=BOX_BG, stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(620, 290, "Характеристики DDR / xSPI:", size=11, color=INK, bold=True))
    p.append(text(460, 312, "• 2 передачі за 1 такт тактового сигналу SCK", size=10, color=INK, anchor="start"))
    p.append(text(460, 332, "• В Octal DDR (8 ліній): 2 байти за 1 такт", size=10, color=INK, anchor="start"))
    p.append(text(460, 352, "• При частоті 200 МГц: 400 МБайт/с", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(460, 372, "• DQS нівелює фазові зсуви та температурний дрейф", size=10, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, "sdr-vs-ddr.svg"), W, H, *p)


# ── 4. Апаратний режим Memory-Mapped XIP у мікроконтролері ────────────────
def fig_xip_memory_mapped():
    W, H = 860, 460
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    p.append(text(430, 35, "Архітектура прямого виконання коду з Flash-пам'яті (Execute-in-Place / XIP)", size=14, color=INK, bold=True))

    # 1. CPU Core
    p.append(rect(30, 70, 140, 180, fill="#e0e7ff", stroke=CLK_COL, sw=1.6, rx=6))
    p.append(text(100, 95, "CPU Ядро", size=13, color=CLK_COL, bold=True))
    p.append(text(100, 115, "(ARM Cortex-M7", size=10, color=INK))
    p.append(text(100, 130, "/ RISC-V)", size=10, color=INK))
    p.append(rect(40, 150, 120, 45, fill="#ffffff", stroke=CLK_COL, sw=1.0, rx=4))
    p.append(text(100, 168, "PC: 0x9000_1240", size=10, color=POS, bold=True))
    p.append(text(100, 184, "Fetch 32-bit Inst", size=10, color=MUTED))

    # Стрілка CPU -> System Bus Matrix
    p.append(arrow(170, 160, 220, 160, color=INK, sw=2.0))
    p.append(text(195, 150, "AXI / AHB", size=10, color=INK, bold=True))

    # 2. Bus Matrix & Cache / Prefetch Controller
    p.append(rect(220, 70, 180, 180, fill="#fef3c7", stroke="#d97706", sw=1.6, rx=6))
    p.append(text(310, 95, "Кеш / Prefetch Буфер", size=12, color="#b45309", bold=True))
    p.append(text(310, 115, "(L1 I-Cache / ART)", size=10, color=MUTED))
    
    p.append(rect(230, 135, 160, 45, fill="#ffffff", stroke="#d97706", sw=1.0, rx=4))
    p.append(text(310, 152, "Cache Hit → 0 тактів", size=10, color=FIELD, bold=True))
    p.append(text(310, 168, "Cache Miss → Burst Read", size=10, color=POS))
    p.append(text(310, 210, "Line Fill (32 байти)", size=10, color=INK, bold=True))

    # Стрілка Cache -> QSPI Controller
    p.append(arrow(400, 160, 450, 160, color=INK, sw=2.0))
    p.append(text(425, 150, "32B Burst", size=10, color=INK, bold=True))

    # 3. Апаратний контролер QSPI / OCTOSPI
    p.append(rect(450, 70, 190, 180, fill="#f1f5f9", stroke=DAT_COL, sw=1.6, rx=6))
    p.append(text(545, 95, "Апаратний QSPI Блок", size=12, color=DAT_COL, bold=True))
    p.append(text(545, 115, "Memory-Mapped Engine", size=10, color=MUTED))

    p.append(rect(460, 130, 170, 50, fill="#ffffff", stroke=DAT_COL, sw=1.0, rx=4))
    p.append(text(545, 148, "Автомат транзакцій:", size=10, color=INK, bold=True))
    p.append(text(545, 165, "Fast Read Quad I/O (0xEB)", size=10, color=POS, bold=True))

    p.append(text(545, 205, "Режим Continuous Read", size=10, color=FIELD, bold=True))
    p.append(text(545, 222, "(без повтору коду 0xEB)", size=10, color=MUTED))

    # Стрілка QSPI Controller -> Зовнішня Flash
    p.append(arrow(640, 160, 690, 160, color=DAT_COL, sw=2.0))
    p.append(text(665, 150, "6 ліній", size=10, color=DAT_COL, bold=True))

    # 4. Зовнішня Flash-пам'ять
    p.append(rect(690, 70, 140, 180, fill="#dcfce7", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(760, 95, "NOR Flash", size=13, color=FIELD, bold=True))
    p.append(text(760, 115, "(W25Q / IS25LP)", size=10, color=MUTED))
    p.append(rect(700, 135, 120, 45, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(760, 152, "Адресний простір:", size=10, color=INK))
    p.append(text(760, 168, "0x9000_0000...", size=10, color=POS, bold=True))
    p.append(text(760, 215, "133 МГц Quad QIO", size=10, color=DAT_COL, bold=True))

    # Нижня секція: Покроковий цикл виконання команди з Flash
    p.append(rect(30, 275, 800, 165, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(430, 298, "Послідовність подій при зверненні процесора до зовнішньої Flash-пам'яті", size=12, color=INK, bold=True))

    steps = [
        ("1. Fetch за адресою", "Ядро запитує інструкцію за адресою 0x90001240 через шину AHB/AXI.", CLK_COL),
        ("2. Перевірка L1 Cache", "Якщо рядок кешу є (Cache Hit) — інструкція видається за 0 тактів очікування.", "#d97706"),
        ("3. Апаратний Burst", "При Cache Miss контролер QSPI самостійно формує транзакцію 0xEB на шині.", DAT_COL),
        ("4. Вибірка 32 байтів", "Flash передає 32 байти по 4 лініях IO0..IO3 за 64 такти тактового сигналу.", FIELD),
        ("5. Заповнення рядка", "Рядок кешу заповнюється, конвеєр CPU продовжує виконання без участі ПЗ.", POS),
    ]

    y_st = 320
    for idx, (head_st, desc_st, col_st) in enumerate(steps):
        p.append(text(45, y_st, head_st, size=10, color=col_st, bold=True, anchor="start"))
        p.append(text(210, y_st, desc_st, size=10, color=INK, anchor="start"))
        y_st += 22

    return render(os.path.join(OUT, "xip-memory-mapped.svg"), W, H, *p)


# ── 5. Затримка вибірки Dummy Cycles та залежність від частоти ──────────────
def fig_dummy_cycles_lookup():
    W, H = 840, 420
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    p.append(text(420, 35, "Фізична природа та розрахунок холостих тактів (Dummy Cycles)", size=14, color=INK, bold=True))

    # Лівий блок: Фізика матриці Flash
    p.append(rect(30, 60, 370, 335, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(215, 85, "Чому потрібні такти затримки?", size=12, color=POS, bold=True))

    p.append(rect(45, 105, 340, 75, fill=WARN_BG, stroke=POS, sw=1.0, rx=4))
    p.append(text(215, 125, "Час доступу матриці Flash: t_ACC ≈ 30–50 нс", size=10, color=POS, bold=True))
    p.append(text(215, 145, "Внутрішній підсилювач зчитування (Sense Amp)", size=10, color=INK))
    p.append(text(215, 162, "потребує фіксованого часу на перезаряд ємностей комірок", size=10, color=MUTED))

    p.append(text(215, 200, "Формула розрахунку Dummy тактів:", size=11, color=INK, bold=True))
    p.append(rect(45, 215, 340, 45, fill=HL_BG, stroke=CLK_COL, sw=1.2, rx=4))
    p.append(text(215, 235, "N_dummy ≥ ⌈ t_ACC × f_SCK ⌉", size=12, color=CLK_COL, bold=True))
    p.append(text(215, 250, "+ такти перемикання напрямку шини (Bus Turnaround)", size=10, color=MUTED))

    p.append(text(60, 285, "• При 20 МГц (T = 50 нс): вистачає 1 такту", size=10, color=INK, anchor="start"))
    p.append(text(60, 310, "• При 104 МГц (T = 9.6 нс): потрібно 4–6 тактів", size=10, color=INK, anchor="start"))
    p.append(text(60, 335, "• При 133 МГц (T = 7.5 нс): потрібно 8 тактів", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(60, 360, "• При 200 МГц DDR: потрібно 10–16 тактів", size=10, color=POS, bold=True, anchor="start"))

    # Правий блок: Таблиця конфігурації Dummy Cycles у регістрі стану Flash
    p.append(rect(430, 60, 380, 335, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(620, 85, "Таблиця конфігурації (Winbond W25Q / Micron)", size=12, color=DAT_COL, bold=True))

    col_w = [445, 535, 625, 715, 795]
    p.append(rect(445, 105, 350, 26, fill=BOX_BG, stroke=LINE, sw=1.0, rx=2))
    p.append(text(490, 122, "Команда", size=10, color=INK, bold=True))
    p.append(text(580, 122, "Dummy біти", size=10, color=INK, bold=True))
    p.append(text(670, 122, "Макс. f_SCK", size=10, color=INK, bold=True))
    p.append(text(755, 122, "t_Dummy", size=10, color=INK, bold=True))

    dummy_table = [
        ("0x03 (READ)", "0 тактів", "до 33 МГц", "0 нс"),
        ("0x0B (Fast Read)", "8 тактів", "до 133 МГц", "60.1 нс"),
        ("0x3B (Dual Output)", "8 тактів", "до 133 МГц", "60.1 нс"),
        ("0xBB (Dual I/O)", "4 такти", "до 104 МГц", "38.5 нс"),
        ("0x6B (Quad Output)", "8 тактів", "до 133 МГц", "60.1 нс"),
        ("0xEB (Quad I/O)", "6 тактів", "до 104 МГц", "57.7 нс"),
        ("0xEB (Quad I/O)", "8 тактів", "до 133 МГц", "60.1 нс"),
        ("0xEB (Quad DDR)", "8 тактів (DDR)", "до 100 МГц", "40.0 нс"),
    ]

    y_dt = 135
    for r_idx, (cmd, d_cnt, f_max, t_d) in enumerate(dummy_table):
        bg = "#ffffff" if r_idx % 2 == 0 else "#f9fafb"
        p.append(rect(445, y_dt, 350, 22, fill=bg, stroke="#e5e7eb", sw=0.8, rx=0))
        p.append(text(490, y_dt + 15, cmd, size=10, color=POS if "0xEB" in cmd else INK, bold=True))
        p.append(text(580, y_dt + 15, d_cnt, size=10, color=INK))
        p.append(text(670, y_dt + 15, f_max, size=10, color=CLK_COL, bold=True))
        p.append(text(755, y_dt + 15, t_d, size=10, color=MUTED))
        y_dt += 22

    p.append(rect(445, 325, 350, 55, fill=HL_BG, stroke=CLK_COL, sw=1.0, rx=4))
    p.append(text(620, 345, "Критичне правило для мікроконтролера:", size=10, color=POS, bold=True))
    p.append(text(620, 362, "Кількість dummy тактів у контролері QSPI МК МУСИТЬ", size=10, color=INK))
    p.append(text(620, 376, "точно збігатися з конфігурацією Flash-пам'яті!", size=10, color=INK, bold=True))

    return render(os.path.join(OUT, "dummy-cycles-lookup.svg"), W, H, *p)


if __name__ == "__main__":
    fig_pin_transition()
    fig_transaction_phases()
    fig_sdr_vs_ddr()
    fig_xip_memory_mapped()
    fig_dummy_cycles_lookup()
    print("Всі 5 SVG-фігур згенеровано успішно.")
