# -*- coding: utf-8 -*-
"""Фігури до теми «MIPI CSI-2: послідовний інтерфейс камери».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Допоміжне: згладжений перепад сигналу ──────────────────────────────────
def smooth_step(x0, x1, y0, y1, n=16):
    pts = []
    for i in range(n + 1):
        t = i / n
        s = 0.5 * (1 - math.cos(math.pi * t))
        pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * s))
    return pts


def polyline_d(pts, color=LINE, sw=1.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pd = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (pd, color, sw, d))


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 1 — Паралельний інтерфейс камери (DVP) проти MIPI CSI-2
# ════════════════════════════════════════════════════════════════════════════
def fig_parallel_vs_mipi():
    W, H = 880, 420
    els = [
        text(W / 2, 25, "Еволюція інтерфейсу камери: від паралельного DVP до диференційного MIPI CSI-2", size=15, bold=True)
    ]

    # ── Ліва панель: Паралельна шина DVP (Digital Video Port) ──
    p1_x, p1_y, p1_w, p1_h = 30, 55, 390, 340
    els.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    els.append(text(p1_x + p1_w / 2, p1_y + 24, "Паралельна шина (DVP / Parallel CPI)", size=13.5, bold=True, color=POS))

    # Сенсор і SoC блок ліворуч
    b1_w, b1_h = 74, 180
    s_y = p1_y + 50
    els.append(rect(p1_x + 18, s_y, b1_w, b1_h, fill=FILL, stroke=LINE, sw=1.4, rx=4))
    els.append(mtext(p1_x + 18 + b1_w / 2, s_y + 80, ["Сенсор", "камери", "(DVP TX)"], size=11, bold=True))

    els.append(rect(p1_x + p1_w - 18 - b1_w, s_y, b1_w, b1_h, fill=FILL, stroke=LINE, sw=1.4, rx=4))
    els.append(mtext(p1_x + p1_w - 18 + b1_w / 2, s_y + 80, ["Процесор", "(SoC / ISP", "RX)"], size=11, bold=True))

    # Лінії зв'язку
    lines_y = [s_y + 25, s_y + 50, s_y + 75, s_y + 100, s_y + 125, s_y + 155]
    labels = ["PCLK (піксельний такт, до 150 МГц)", "D[0..7/11] (8–12 ліній даних)", "HSYNC (рядкова синхронізація)", "VSYNC (кадрова синхронізація)", "I2C / SCCB (керування)", "GND / Живлення (множинні виводи)"]
    
    lx_start = p1_x + 18 + b1_w
    lx_end = p1_x + p1_w - 18 - b1_w
    for y, lbl in zip(lines_y, labels):
        els.append(arrow(lx_start, y, lx_end, y, color=POS, sw=1.4))
    
    els.append(text(p1_x + p1_w / 2, s_y + 15, "12–18 однофазних ліній 1.8V / 3.3V CMOS", size=10.5, color=POS, bold=True))
    els.append(text(p1_x + p1_w / 2, s_y + 40, "D[0..11] паралельні дані", size=10, color=MUTED))
    els.append(text(p1_x + p1_w / 2, s_y + 65, "PCLK спільний такт", size=10, color=MUTED))
    els.append(text(p1_x + p1_w / 2, s_y + 115, "HSYNC / VSYNC строби", size=10, color=MUTED))

    # Підсумок проблем паралельної шини
    pr_box_y = p1_y + 242
    els.append(rect(p1_x + 14, pr_box_y, p1_w - 28, 85, fill="#fff2f0", stroke=POS, sw=1.2, rx=4))
    dvp_problems = [
        "• Невиправний часовий перекіс (skew) ліній > 100 МГц",
        "• Високі паразитні наводки (EMI) та шум перемикань",
        "• Громіздкий шлейф (20–30 контактів) і зайві виводи чипа",
        "• Нездатність пропустити 1080p60 / 4K відеопотоки"
    ]
    for i, line_txt in enumerate(dvp_problems):
        els.append(text(p1_x + 22, pr_box_y + 18 + i * 18, line_txt, size=10.5, color=POS, anchor="start"))

    # ── Права панель: MIPI CSI-2 (D-PHY) ──
    p2_x, p2_y, p2_w, p2_h = 460, 55, 390, 340
    els.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f9fdfa", stroke=FIELD, sw=1.5, rx=8))
    els.append(text(p2_x + p2_w / 2, p2_y + 24, "Послідовний інтерфейс MIPI CSI-2 (D-PHY)", size=13.5, bold=True, color=FIELD))

    # Сенсор і SoC блок праворуч
    els.append(rect(p2_x + 18, s_y, b1_w, b1_h, fill=FILL, stroke=LINE, sw=1.4, rx=4))
    els.append(mtext(p2_x + 18 + b1_w / 2, s_y + 80, ["Сенсор", "камери", "(CSI-2 TX)"], size=11, bold=True))

    els.append(rect(p2_x + p2_w - 18 - b1_w, s_y, b1_w, b1_h, fill=FILL, stroke=LINE, sw=1.4, rx=4))
    els.append(mtext(p2_x + p2_w - 18 + b1_w / 2, s_y + 80, ["Процесор", "(SoC / ISP", "CSI-2 RX)"], size=11, bold=True))

    lx2_start = p2_x + 18 + b1_w
    lx2_end = p2_x + p2_w - 18 - b1_w

    # Диференційні пари MIPI
    mipi_lines_y = [s_y + 30, s_y + 65, s_y + 100, s_y + 145]
    for y in mipi_lines_y[:3]:
        # Малюємо пару дротів
        els.append(line(lx2_start, y - 4, lx2_end - 6, y - 4, color=NEG, sw=1.6))
        els.append(line(lx2_start, y + 4, lx2_end - 6, y + 4, color=NEG, sw=1.6))
        els.append(arrow(lx2_end - 6, y, lx2_end, y, color=NEG, sw=1.6))
    
    # I2C/CCI шина керування
    els.append(arrow(lx2_start, mipi_lines_y[3], lx2_end, mipi_lines_y[3], color=LINE, sw=1.3))

    els.append(text(p2_x + p2_w / 2, s_y + 20, "Clock Lane (диф. пара такту)", size=10, color=NEG, bold=True))
    els.append(text(p2_x + p2_w / 2, s_y + 55, "Data Lane 0 (диф. пара даних)", size=10, color=NEG, bold=True))
    els.append(text(p2_x + p2_w / 2, s_y + 90, "Data Lane 1..3 (додаткові лінії)", size=10, color=NEG, bold=True))
    els.append(text(p2_x + p2_w / 2, s_y + 135, "CCI (I2C / I3C — конфігурація сенсора)", size=10, color=MUTED))

    # Переваги MIPI CSI-2
    mipi_box_y = p2_y + 242
    els.append(rect(p2_x + 14, mipi_box_y, p2_w - 28, 85, fill="#edf8f1", stroke=FIELD, sw=1.2, rx=4))
    mipi_advantages = [
        "• Диференційні пари SLVS (200 мВ) — захист від завад",
        "• Швидкість до 2.5–4.5 Гбіт/с на лінію (4K60 / HDR легко)",
        "• Мінімум пінів: лише 4–10 провідників у тонкому шлейфі",
        "• Гнучке енергозбереження: динамічний перехід LP ↔ HS"
    ]
    for i, line_txt in enumerate(mipi_advantages):
        els.append(text(p2_x + 22, mipi_box_y + 18 + i * 18, line_txt, size=10.5, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "parallel-vs-mipi.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 2 — Фізичні рівні D-PHY: динамічний перехід LP (1.2V) ↔ HS (200mV)
# ════════════════════════════════════════════════════════════════════════════
def fig_dphy_signaling():
    W, H = 920, 440
    els = [
        text(W / 2, 24, "Фізичний рівень MIPI D-PHY: динамічний перехід Low-Power (LP) ↔ High-Speed (HS)", size=15, bold=True)
    ]

    # Вісь напруги ліворуч
    ax_x = 75
    y_top, y_bot = 65, 340
    els.append(line(ax_x, y_bot, ax_x, y_top, color=MUTED, sw=1.5))
    els.append(arrow(ax_x, y_top + 10, ax_x, y_top - 5, color=MUTED, sw=1.5))
    els.append(text(ax_x - 10, y_top, "U (В)", size=11, color=MUTED, bold=True, anchor="end"))

    # Рівні напруги
    # 1.2V (LP High)
    y_1v2 = 90
    els.append(line(ax_x - 4, y_1v2, W - 40, y_1v2, color=MUTED, sw=1, dash="3,4"))
    els.append(text(ax_x - 8, y_1v2 + 4, "1.2 В", size=10.5, color=MUTED, anchor="end"))
    els.append(text(W - 45, y_1v2 - 8, "Рівень LP (Low-Power)", size=10.5, color=POS, bold=True, anchor="end"))

    # HS діапазон (100 мВ .. 300 мВ, центр 200 мВ)
    y_hs_hi = 265  # 300 мВ
    y_hs_mid = 285 # 200 мВ (V_CM)
    y_hs_lo = 305  # 100 мВ
    y_0v = 330     # 0 В (GND)

    els.append(line(ax_x - 4, y_hs_mid, W - 40, y_hs_mid, color=MUTED, sw=1, dash="2,4"))
    els.append(text(ax_x - 8, y_hs_mid + 4, "200 мВ", size=10, color=MUTED, anchor="end"))

    els.append(line(ax_x - 4, y_0v, W - 40, y_0v, color=MUTED, sw=1))
    els.append(text(ax_x - 8, y_0v + 4, "0 В", size=10.5, color=MUTED, anchor="end"))
    els.append(text(W - 45, y_hs_hi - 8, "Рівень HS (High-Speed SLVS, ΔV=200 мВ)", size=10.5, color=NEG, bold=True, anchor="end"))

    # ── Часові ділянки сигналу ──
    t_start = 95
    t_lp01 = 205
    t_lp00 = 295
    t_hs_zero = 385
    t_sot = 475
    t_payload = 575
    t_eot = 735
    t_end = 860

    # Фон фаз
    phases = [
        (t_start, t_lp01, "LP-11\n(Stop)", "#fcfdfe", MUTED),
        (t_lp01, t_lp00, "LP-01\n(HS-Req)", "#fffbf0", POS),
        (t_lp00, t_hs_zero, "LP-00\n(Prepare)", "#fff5f5", POS),
        (t_hs_zero, t_sot, "HS-Zero\n(Драйвер ON)", "#edf2fc", NEG),
        (t_sot, t_payload, "SoT Sync\n(0xB8)", "#e8f5e9", FIELD),
        (t_payload, t_eot, "HS Payload (Пакети пікселів)\n1.5–2.5 Гбіт/с", "#f0f4fd", NEG),
        (t_eot, t_end, "EoT → LP-11\n(Stop State)", "#fcfdfe", MUTED)
    ]

    for x1, x2, lbl, bg, stroke in phases:
        els.append(rect(x1, y_1v2 - 20, x2 - x1, y_0v - y_1v2 + 35, fill=bg, stroke=stroke, sw=1, rx=3))
        els.append(mtext((x1 + x2) / 2, y_1v2 - 5, lbl.split("\n"), size=9.5, color=stroke, bold=True))

    # Хвилі сигналів
    # D_P (червона лінія)
    dp_pts = [
        (t_start, y_1v2), (t_lp01 - 10, y_1v2),
        (t_lp01, y_0v), (t_lp00 - 10, y_0v),
        (t_lp00, y_0v), (t_hs_zero - 15, y_0v),
        (t_hs_zero, y_hs_lo), (t_sot, y_hs_lo)
    ]
    sot_bits_dp = [0, 0, 0, 1, 1, 1, 0, 1]
    sot_w = (t_payload - t_sot) / len(sot_bits_dp)
    for i, b in enumerate(sot_bits_dp):
        bx = t_sot + i * sot_w
        by = y_hs_hi if b else y_hs_lo
        dp_pts.append((bx, by))
        dp_pts.append((bx + sot_w, by))

    pay_w = 12
    n_pay = int((t_eot - t_payload) / pay_w)
    for i in range(n_pay):
        bx = t_payload + i * pay_w
        by = y_hs_hi if (i % 2 == 1) else y_hs_lo
        dp_pts.append((bx, by))
        dp_pts.append((bx + pay_w, by))

    dp_pts.append((t_eot, y_hs_lo))
    dp_pts.append((t_eot + 15, y_1v2))
    dp_pts.append((t_end, y_1v2))

    # D_N (синя лінія)
    dn_pts = [
        (t_start, y_1v2), (t_lp01 - 10, y_1v2),
        (t_lp01, y_1v2), (t_lp00 - 10, y_1v2),
        (t_lp00, y_0v), (t_hs_zero - 15, y_0v),
        (t_hs_zero, y_hs_hi), (t_sot, y_hs_hi)
    ]
    for i, b in enumerate(sot_bits_dp):
        bx = t_sot + i * sot_w
        by = y_hs_lo if b else y_hs_hi
        dn_pts.append((bx, by))
        dn_pts.append((bx + sot_w, by))

    for i in range(n_pay):
        bx = t_payload + i * pay_w
        by = y_hs_lo if (i % 2 == 1) else y_hs_hi
        dn_pts.append((bx, by))
        dn_pts.append((bx + pay_w, by))

    dn_pts.append((t_eot, y_hs_hi))
    dn_pts.append((t_eot + 15, y_1v2))
    dn_pts.append((t_end, y_1v2))

    els.append(polyline_d(dp_pts, color=POS, sw=2))
    els.append(polyline_d(dn_pts, color=NEG, sw=2))

    leg_y = 390
    els.append(line(120, leg_y, 160, leg_y, color=POS, sw=2.5))
    els.append(text(170, leg_y + 4, "Data Positive (D_P / D+)", size=11, color=POS, bold=True, anchor="start"))

    els.append(line(360, leg_y, 400, leg_y, color=NEG, sw=2.5))
    els.append(text(410, leg_y + 4, "Data Negative (D_N / D−)", size=11, color=NEG, bold=True, anchor="start"))

    els.append(fitbox(640, leg_y - 14, 230, 28, "Термінація 100 Ом увімкнена лише в HS", size=10, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "dphy-signaling-modes.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 3 — Структура пакетів MIPI CSI-2 та розподіл по лініях (Multi-Lane)
# ════════════════════════════════════════════════════════════════════════════
def fig_csi2_packet():
    W, H = 920, 430
    els = [
        text(W / 2, 24, "Структура пакетів MIPI CSI-2 та розподіл байтів по кількох лініях даних (Multi-Lane)", size=15, bold=True)
    ]

    # Короткий пакет (Short Packet)
    sp_x, sp_y = 40, 55
    els.append(text(sp_x + 160, sp_y + 16, "Короткий пакет (Short Packet — 4 байти: синхронізація)", size=11.5, bold=True, color=POS))
    
    els.append(rect(sp_x, sp_y + 26, 90, 42, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    els.append(mtext(sp_x + 45, sp_y + 43, ["Data ID (DI)", "VC[1:0] + DT[5:0]"], size=9.5, color=POS, bold=True))

    els.append(rect(sp_x + 95, sp_y + 26, 140, 42, fill="#fff7e6", stroke="#d48806", sw=1.4, rx=4))
    els.append(mtext(sp_x + 165, sp_y + 43, ["Data Field (16 біт)", "Номер кадру / рядка"], size=9.5, color="#d48806", bold=True))

    els.append(rect(sp_x + 240, sp_y + 26, 80, 42, fill="#e6f7ff", stroke=NEG, sw=1.4, rx=4))
    els.append(mtext(sp_x + 280, sp_y + 43, ["ECC (8 біт)", "Хеммінг (1b/2b)"], size=9.5, color=NEG, bold=True))

    # Довгий пакет (Long Packet)
    lp_x, lp_y = 380, 55
    els.append(text(lp_x + 250, lp_y + 16, "Довгий пакет (Long Packet — піксельні дані рядка кадру)", size=11.5, bold=True, color=FIELD))

    # Packet Header (4 байти)
    els.append(rect(lp_x, lp_y + 26, 75, 42, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    els.append(mtext(lp_x + 37.5, lp_y + 43, ["Data ID", "VC + DT"], size=9.5, color=POS, bold=True))

    els.append(rect(lp_x + 80, lp_y + 26, 85, 42, fill="#fff7e6", stroke="#d48806", sw=1.4, rx=4))
    els.append(mtext(lp_x + 122.5, lp_y + 43, ["Word Count", "WC (16 біт)"], size=9.5, color="#d48806", bold=True))

    els.append(rect(lp_x + 170, lp_y + 26, 65, 42, fill="#e6f7ff", stroke=NEG, sw=1.4, rx=4))
    els.append(mtext(lp_x + 202.5, lp_y + 43, ["ECC", "8 біт"], size=9.5, color=NEG, bold=True))

    els.append(text(lp_x + 117.5, lp_y + 82, "Заголовок (PH, 4 байти)", size=9.5, color=MUTED, bold=True))

    # Payload (N байтів)
    els.append(rect(lp_x + 242, lp_y + 26, 200, 42, fill="#edf8f1", stroke=FIELD, sw=1.6, rx=4))
    els.append(mtext(lp_x + 342, lp_y + 43, ["Корисне навантаження (Payload)", "WC байтів пікселів (RAW8/10/12/YUV/RGB)"], size=9.5, color=FIELD, bold=True))

    # Packet Footer (2 байти CRC)
    els.append(rect(lp_x + 448, lp_y + 26, 60, 42, fill="#f9f0ff", stroke="#722ed1", sw=1.4, rx=4))
    els.append(mtext(lp_x + 478, lp_y + 43, ["CRC-16", "2 байти"], size=9.5, color="#722ed1", bold=True))
    els.append(text(lp_x + 478, lp_y + 82, "Кінцевик (PF)", size=9.5, color=MUTED, bold=True))

    # Розподіл байтів по 4 лініях даних
    ml_y = 150
    els.append(line(40, ml_y - 15, W - 40, ml_y - 15, color=MUTED, sw=1, dash="3,4"))
    els.append(text(W / 2, ml_y + 8, "Розподіл байтів пакета по 4 лініях MIPI D-PHY (Multi-Lane Byte Striping)", size=13, bold=True))

    lane_h = 32
    lane_y_start = ml_y + 35
    lanes = ["Lane 0", "Lane 1", "Lane 2", "Lane 3"]
    lane_colors = [POS, FIELD, NEG, "#722ed1"]

    col_titles = ["SoT", "Такт 1 (PH)", "Такт 2 (Data)", "Такт 3 (Data)", "Такт 4 (Data)", "Такт 5 (PF)", "EoT"]
    col_widths = [55, 90, 95, 95, 95, 90, 55]

    cur_x = 170
    col_x_positions = []
    for ct, cw in zip(col_titles, col_widths):
        col_x_positions.append(cur_x)
        els.append(text(cur_x + cw / 2, lane_y_start - 10, ct, size=10, color=MUTED, bold=True))
        cur_x += cw + 8

    for i, (lname, lcol) in enumerate(zip(lanes, lane_colors)):
        ly = lane_y_start + i * (lane_h + 10)
        els.append(fitbox(50, ly, 100, lane_h, lname, size=11, fill="#fdfdfd", stroke=lcol, color=lcol, bold=True))

        # SoT
        els.append(rect(col_x_positions[0], ly, col_widths[0], lane_h, fill="#f6ffed", stroke=FIELD, sw=1.2, rx=3))
        els.append(text(col_x_positions[0] + col_widths[0] / 2, ly + lane_h * 0.65, "SoT", size=10, color=FIELD, bold=True))

        # PH
        ph_labels = ["DI (B0)", "WC_L (B1)", "WC_H (B2)", "ECC (B3)"]
        els.append(rect(col_x_positions[1], ly, col_widths[1], lane_h, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
        els.append(text(col_x_positions[1] + col_widths[1] / 2, ly + lane_h * 0.65, ph_labels[i], size=10, color=POS, bold=True))

        # Data 1
        d1_labels = ["Data B4", "Data B5", "Data B6", "Data B7"]
        els.append(rect(col_x_positions[2], ly, col_widths[2], lane_h, fill="#edf8f1", stroke=FIELD, sw=1.2, rx=3))
        els.append(text(col_x_positions[2] + col_widths[2] / 2, ly + lane_h * 0.65, d1_labels[i], size=10, color=FIELD))

        # Data 2
        d2_labels = ["Data B8", "Data B9", "Data B10", "Data B11"]
        els.append(rect(col_x_positions[3], ly, col_widths[3], lane_h, fill="#edf8f1", stroke=FIELD, sw=1.2, rx=3))
        els.append(text(col_x_positions[3] + col_widths[3] / 2, ly + lane_h * 0.65, d2_labels[i], size=10, color=FIELD))

        # Data 3
        d3_labels = ["Data B12", "Data B13", "...", "Data B_N-2"]
        els.append(rect(col_x_positions[4], ly, col_widths[4], lane_h, fill="#edf8f1", stroke=FIELD, sw=1.2, rx=3))
        els.append(text(col_x_positions[4] + col_widths[4] / 2, ly + lane_h * 0.65, d3_labels[i], size=10, color=FIELD))

        # PF
        pf_labels = ["CRC_L", "CRC_H", "Заповн.", "Заповн."]
        els.append(rect(col_x_positions[5], ly, col_widths[5], lane_h, fill="#f9f0ff", stroke="#722ed1", sw=1.2, rx=3))
        els.append(text(col_x_positions[5] + col_widths[5] / 2, ly + lane_h * 0.65, pf_labels[i], size=9.5, color="#722ed1", bold=True))

        # EoT
        els.append(rect(col_x_positions[6], ly, col_widths[6], lane_h, fill="#fff2f0", stroke=POS, sw=1.2, rx=3))
        els.append(text(col_x_positions[6] + col_widths[6] / 2, ly + lane_h * 0.65, "EoT", size=10, color=POS, bold=True))

    els.append(text(W / 2, H - 20, "Байти чергуються циклічно: кожен такт внутрішнього Byte Clock паралельно передає 4 байти", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "csi2-packet-structure.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 4 — Тракт апаратного приймача MIPI CSI-2 в SoC / FPGA
# ════════════════════════════════════════════════════════════════════════════
def fig_rx_pipeline():
    W, H = 940, 360
    els = [
        text(W / 2, 24, "Конвеєр апаратного приймача MIPI CSI-2 в SoC або FPGA: від фізичних ліній до пам'яті", size=15, bold=True)
    ]

    cy = 150
    bh = 72
    bw = 110
    gap = 20

    pipeline_blocks = [
        ("D-PHY RX\n(Фізичний шар)", "Диф. компаратори,\nдетектор SoT,\nдесеріалізація", "#eaf0fd", NEG),
        ("Lane Deskew\n& Alignment", "Вирівнювання ліній,\nкомпенсація перекосу,\nзбирання слів", "#fdf4e8", "#d48806"),
        ("Packet Decoder\n(Протокол)", "Перевірка ECC,\nвиділення VC та DT,\nконтроль CRC-16", "#fdecea", POS),
        ("Pixel Unpacker\n(Розпакування)", "RAW10 → 16-біт,\nRAW12 → 16-біт,\nвилучення хвостів", "#eafaf0", FIELD),
        ("CDC FIFO\n(Асинхр. черга)", "Перехід Byte Clock\n→ Pixel / AXI Clock\nбез збоїв", "#f9f0ff", "#722ed1"),
        ("DMA / ISP Bridge\n(Інтерфейс)", "Запис у DDR RAM\n(Frame Buffer) або\nпотік в ISP", "#f4f6f8", LINE)
    ]

    total_w = len(pipeline_blocks) * bw + (len(pipeline_blocks) - 1) * gap
    start_x = (W - total_w) / 2

    cur_x = start_x
    for i, (title, desc, fill_col, stroke_col) in enumerate(pipeline_blocks):
        els.append(rect(cur_x, cy - bh / 2, bw, bh, fill=fill_col, stroke=stroke_col, sw=1.6, rx=6))
        els.append(mtext(cur_x + bw / 2, cy - 14, title.split("\n"), size=11, color=stroke_col, bold=True))
        els.append(mtext(cur_x + bw / 2, cy + 14, desc.split("\n"), size=9, color=INK))

        if i < len(pipeline_blocks) - 1:
            els.append(arrow(cur_x + bw, cy, cur_x + bw + gap, cy, color=LINE, sw=1.8))
        cur_x += bw + gap

    els.append(arrow(start_x - 45, cy, start_x, cy, color=NEG, sw=2))
    els.append(mtext(start_x - 50, cy - 12, ["Диф. пари", "MIPI D-PHY"], size=10, color=NEG, bold=True, anchor="end"))
    els.append(text(start_x - 50, cy + 18, "(Clock + 1..4 Data)", size=9, color=MUTED, anchor="end"))

    last_x = start_x + total_w
    els.append(arrow(last_x, cy, last_x + 45, cy, color=FIELD, sw=2))
    els.append(mtext(last_x + 50, cy - 12, ["AXI4-Stream", "відеопотік"], size=10, color=FIELD, bold=True, anchor="start"))
    els.append(text(last_x + 50, cy + 18, "у DDR / ISP", size=9, color=MUTED, anchor="start"))

    dom_y = cy + bh / 2 + 40
    w_d1 = bw * 4 + gap * 3 + 10
    els.append(rect(start_x - 5, dom_y, w_d1, 45, fill="#f0f5ff", stroke=NEG, sw=1.2, rx=4))
    els.append(text(start_x - 5 + w_d1 / 2, dom_y + 18, "Тактовий домен MIPI (Byte Clock = D-PHY Bit Rate / 8)", size=10.5, color=NEG, bold=True))
    els.append(text(start_x - 5 + w_d1 / 2, dom_y + 34, "Синхронізований із тактовою парою передавача камери", size=9.5, color=MUTED))

    w_d2 = bw * 2 + gap * 1 + 10
    d2_x = start_x - 5 + w_d1 + gap - 10
    els.append(rect(d2_x, dom_y, w_d2, 45, fill="#fdf6ec", stroke="#d48806", sw=1.2, rx=4))
    els.append(text(d2_x + w_d2 / 2, dom_y + 18, "Тактовий домен SoC / AXI (System Clock)", size=10.5, color="#d48806", bold=True))
    els.append(text(d2_x + w_d2 / 2, dom_y + 34, "Незалежний локальний генератор SoC / FPGA", size=9.5, color=MUTED))

    els.append(text(start_x + total_w * 0.72, dom_y - 10, "Безпечний бар'єр тактових доменів", size=9.5, color="#722ed1", bold=True))

    render(os.path.join(IMG, "rx-pipeline.svg"), W, H, *els)


if __name__ == "__main__":
    fig_parallel_vs_mipi()
    fig_dphy_signaling()
    fig_csi2_packet()
    fig_rx_pipeline()
    print("OK: figures written to", IMG)
