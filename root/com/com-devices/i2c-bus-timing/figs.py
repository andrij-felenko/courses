# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN_COL = "#d9534f"
OK_COL   = "#27ae60"
BUS_COL  = "#2457d6"
WARN_BG  = "#fdecea"
OK_BG    = "#eef6ef"
ACCENT   = "#d97706"
PURPLE   = "#8e44ad"
CYAN     = "#0284c7"
MUTED_GRID = "#e5e7eb"

def polyline(pts, color=LINE, sw=1.5, fill="none", dash=None):
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{points}" fill="{fill}" stroke="{color}" stroke-width="{sw:.1f}"{d}/>'

def draw_time_arrow(x1, x2, y, label, label_y=None, color=INK, size=10, bold=False):
    """Draw a double-headed timing interval dimension with vertical ticks."""
    p = []
    p.append(line(x1, y - 5, x1, y + 5, color=color, sw=1.2))
    p.append(line(x2, y - 5, x2, y + 5, color=color, sw=1.2))
    p.append(line(x1, y, x2, y, color=color, sw=1.2))
    # Arrowheads
    p.append(polyline([(x1 + 4, y - 2.5), (x1, y), (x1 + 4, y + 2.5)], color=color, sw=1.2))
    p.append(polyline([(x2 - 4, y - 2.5), (x2, y), (x2 - 4, y + 2.5)], color=color, sw=1.2))
    ly = label_y if label_y is not None else y - 6
    p.append(text((x1 + x2) / 2, ly, label, size=size, color=color, bold=bold))
    return "".join(p)


def fig_start_stop_timing():
    W, H = 880, 440
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))

    # Title / Mode banner
    p.append(text(W / 2, 35, "Часові параметри циклу I²C: START, передача біта, Repeated START, STOP", size=14, bold=True))

    # Grid / voltage levels
    y_scl_hi = 90
    y_scl_lo = 160
    y_sda_hi = 220
    y_sda_lo = 290

    # Labels for signals
    p.append(rect(25, y_scl_hi - 15, 60, 24, fill="#eff6ff", stroke=BUS_COL, sw=1.2, rx=4))
    p.append(text(55, y_scl_hi + 1, "SCL", size=11, color=BUS_COL, bold=True))

    p.append(rect(25, y_sda_hi - 15, 60, 24, fill="#fff7ed", stroke=ACCENT, sw=1.2, rx=4))
    p.append(text(55, y_sda_hi + 1, "SDA", size=11, color=ACCENT, bold=True))

    # Reference lines (0.7 VDD, 0.3 VDD)
    p.append(line(95, y_scl_hi, W - 30, y_scl_hi, color=MUTED_GRID, sw=1, dash="4,4"))
    p.append(line(95, y_scl_lo, W - 30, y_scl_lo, color=MUTED_GRID, sw=1, dash="4,4"))
    p.append(line(95, y_sda_hi, W - 30, y_sda_hi, color=MUTED_GRID, sw=1, dash="4,4"))
    p.append(line(95, y_sda_lo, W - 30, y_sda_lo, color=MUTED_GRID, sw=1, dash="4,4"))

    p.append(text(92, y_scl_hi + 3, "0.7 VDD", size=9.5, color=MUTED, anchor="end"))
    p.append(text(92, y_scl_lo + 3, "0.3 VDD", size=9.5, color=MUTED, anchor="end"))
    p.append(text(92, y_sda_hi + 3, "0.7 VDD", size=9.5, color=MUTED, anchor="end"))
    p.append(text(92, y_sda_lo + 3, "0.3 VDD", size=9.5, color=MUTED, anchor="end"))

    # Time marks
    t_start_sda_fall = 140
    t_start_scl_fall = 190

    t_bit_scl_rise = 260
    t_bit_scl_fall = 330
    t_bit_sda_trans = 220

    t_sr_scl_rise = 450
    t_sr_sda_rise = 420
    t_sr_sda_fall = 510
    t_sr_scl_fall = 560

    t_stop_scl_rise = 680
    t_stop_sda_rise = 740

    # SCL trace
    scl_pts = [
        (100, y_scl_hi),
        (t_start_scl_fall, y_scl_hi),
        (t_start_scl_fall + 10, y_scl_lo),
        (t_bit_scl_rise - 10, y_scl_lo),
        (t_bit_scl_rise, y_scl_hi),
        (t_bit_scl_fall, y_scl_hi),
        (t_bit_scl_fall + 10, y_scl_lo),
        (t_sr_scl_rise - 10, y_scl_lo),
        (t_sr_scl_rise, y_scl_hi),
        (t_sr_scl_fall, y_scl_hi),
        (t_sr_scl_fall + 10, y_scl_lo),
        (t_stop_scl_rise - 10, y_scl_lo),
        (t_stop_scl_rise, y_scl_hi),
        (W - 40, y_scl_hi)
    ]
    p.append(polyline(scl_pts, color=BUS_COL, sw=2.5))

    # SDA trace
    sda_pts = [
        (100, y_sda_hi),
        (t_start_sda_fall, y_sda_hi),
        (t_start_sda_fall + 10, y_sda_lo),
        (t_bit_sda_trans, y_sda_lo),
        (t_bit_sda_trans + 10, y_sda_hi),
        (t_sr_sda_rise - 10, y_sda_hi),
        (t_sr_sda_rise, y_sda_hi),
        (t_sr_sda_fall, y_sda_hi),
        (t_sr_sda_fall + 10, y_sda_lo),
        (t_stop_sda_rise, y_sda_lo),
        (t_stop_sda_rise + 10, y_sda_hi),
        (W - 40, y_sda_hi)
    ]
    p.append(polyline(sda_pts, color=ACCENT, sw=2.5))

    # Shaded phases
    # START banner
    p.append(rect(120, 315, 80, 22, fill="#eef2ff", stroke=BUS_COL, sw=1, rx=3))
    p.append(text(160, 330, "START (S)", size=9.5, color=BUS_COL, bold=True))

    # DATA valid banner
    p.append(rect(245, 315, 95, 22, fill="#ecfdf5", stroke=OK_COL, sw=1, rx=3))
    p.append(text(292, 330, "DATA VALID", size=9.5, color=OK_COL, bold=True))

    # REPEATED START banner
    p.append(rect(470, 315, 115, 22, fill="#fef3c7", stroke=ACCENT, sw=1, rx=3))
    p.append(text(527, 330, "Repeated START", size=9.5, color=ACCENT, bold=True))

    # STOP banner
    p.append(rect(700, 315, 80, 22, fill="#fef2f2", stroke=WARN_COL, sw=1, rx=3))
    p.append(text(740, 330, "STOP (P)", size=9.5, color=WARN_COL, bold=True))

    # Dimension arrows
    # t_HD;STA (between SDA fall and SCL fall at START)
    p.append(draw_time_arrow(t_start_sda_fall, t_start_scl_fall, 60, "t_HD;STA", 50, color="#b91c1c", size=9.5, bold=True))

    # t_LOW and t_HIGH for data bit
    p.append(draw_time_arrow(t_start_scl_fall + 10, t_bit_scl_rise, 185, "t_LOW", 175, color=BUS_COL, size=9.5))
    p.append(draw_time_arrow(t_bit_scl_rise, t_bit_scl_fall, 60, "t_HIGH", 50, color=BUS_COL, size=9.5))

    # t_SU;DAT and t_HD;DAT
    p.append(draw_time_arrow(t_bit_sda_trans + 10, t_bit_scl_rise, 245, "t_SU;DAT", 237, color=OK_COL, size=9.5))
    p.append(draw_time_arrow(t_bit_scl_fall, t_bit_scl_fall + 40, 245, "t_HD;DAT", 237, color=OK_COL, size=9.5))

    # t_SU;STA (between SCL rise and SDA fall at Sr)
    p.append(draw_time_arrow(t_sr_scl_rise, t_sr_sda_fall, 60, "t_SU;STA", 50, color="#b45309", size=9.5, bold=True))
    p.append(draw_time_arrow(t_sr_sda_fall, t_sr_scl_fall, 80, "t_HD;STA", 72, color="#b91c1c", size=9.5))

    # t_SU;STO (between SCL rise and SDA rise at STOP)
    p.append(draw_time_arrow(t_stop_scl_rise, t_stop_sda_rise, 60, "t_SU;STO", 50, color=WARN_COL, size=9.5, bold=True))

    # t_BUF (between STOP and next potential START)
    p.append(draw_time_arrow(t_stop_sda_rise + 10, W - 50, 245, "t_BUF (вільна шина)", 237, color=PURPLE, size=9.5, bold=True))

    # Explanatory bottom summary box
    p.append(rect(30, 360, W - 60, 60, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=5))
    p.append(text(W / 2, 380, "Ключове правило: зміна SDA при високому SCL кодує керуючі умови (START: спад SDA, STOP: наростання SDA).", size=10.5, color=INK, bold=True))
    p.append(text(W / 2, 400, "Під час передачі бітів даних SDA змінюється виключно в інтервалі t_LOW і залишається стабільною протягом t_HIGH.", size=10, color=MUTED))

    render(os.path.join(OUT, "start-stop-timing.svg"), W, H, *p)


def fig_data_validity_window():
    W, H = 840, 420
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))

    p.append(text(W / 2, 32, "Умова дійсності даних (Data Validity) та часові межі t_SU;DAT і t_HD;DAT", size=13.5, bold=True))

    # Levels
    y_scl_hi = 85
    y_scl_lo = 165
    y_sda_hi = 225
    y_sda_lo = 305

    # Signal badges
    p.append(rect(30, y_scl_hi - 12, 55, 22, fill="#eff6ff", stroke=BUS_COL, sw=1.2, rx=3))
    p.append(text(57, y_scl_hi + 3, "SCL", size=10.5, color=BUS_COL, bold=True))

    p.append(rect(30, y_sda_hi - 12, 55, 22, fill="#fff7ed", stroke=ACCENT, sw=1.2, rx=3))
    p.append(text(57, y_sda_hi + 3, "SDA", size=10.5, color=ACCENT, bold=True))

    # Threshold horizontal lines
    p.append(line(95, y_scl_hi, W - 35, y_scl_hi, color=MUTED_GRID, sw=1, dash="4,4"))
    p.append(line(95, y_scl_lo, W - 35, y_scl_lo, color=MUTED_GRID, sw=1, dash="4,4"))
    p.append(line(95, y_sda_hi, W - 35, y_sda_hi, color=MUTED_GRID, sw=1, dash="4,4"))
    p.append(line(95, y_sda_lo, W - 35, y_sda_lo, color=MUTED_GRID, sw=1, dash="4,4"))

    p.append(text(92, y_scl_hi + 3, "VIH = 0.7 VDD", size=9.5, color=MUTED, anchor="end"))
    p.append(text(92, y_scl_lo + 3, "VIL = 0.3 VDD", size=9.5, color=MUTED, anchor="end"))
    p.append(text(92, y_sda_hi + 3, "VIH = 0.7 VDD", size=9.5, color=MUTED, anchor="end"))
    p.append(text(92, y_sda_lo + 3, "VIL = 0.3 VDD", size=9.5, color=MUTED, anchor="end"))

    # Waveform positions
    t_rise_start = 320
    t_rise_end = 360
    t_fall_start = 580
    t_fall_end = 610

    t_sda_trans = 210

    # Zones background
    p.append(rect(t_rise_end, 60, t_fall_start - t_rise_end, 260, fill="#ecfdf5", stroke="none"))
    p.append(rect(100, 60, t_rise_start - 100, 260, fill="#f8fafc", stroke="none"))
    p.append(rect(t_fall_end, 60, W - 40 - t_fall_end, 260, fill="#f8fafc", stroke="none"))

    # SCL waveform
    scl_pts = [
        (100, y_scl_lo),
        (t_rise_start, y_scl_lo),
        (t_rise_end, y_scl_hi),
        (t_fall_start, y_scl_hi),
        (t_fall_end, y_scl_lo),
        (W - 40, y_scl_lo)
    ]
    p.append(polyline(scl_pts, color=BUS_COL, sw=2.5))

    # SDA waveform
    sda_high = [
        (100, y_sda_lo),
        (t_sda_trans, y_sda_lo),
        (t_sda_trans + 30, y_sda_hi),
        (W - 40, y_sda_hi)
    ]
    sda_low = [
        (100, y_sda_hi),
        (t_sda_trans, y_sda_hi),
        (t_sda_trans + 30, y_sda_lo),
        (W - 40, y_sda_lo)
    ]
    p.append(polyline(sda_high, color=ACCENT, sw=2.2))
    p.append(polyline(sda_low, color=ACCENT, sw=2.2, dash="3,3"))

    # Vertical boundary lines
    p.append(line(t_rise_end, 55, t_rise_end, 330, color=OK_COL, sw=1.2, dash="3,3"))
    p.append(line(t_fall_start, 55, t_fall_start, 330, color=OK_COL, sw=1.2, dash="3,3"))
    p.append(line(t_sda_trans + 30, 195, t_sda_trans + 30, 330, color=ACCENT, sw=1.2, dash="2,2"))

    # Timing dimension arrows
    p.append(draw_time_arrow(t_rise_start, t_rise_end, y_scl_lo + 22, "tr", y_scl_lo + 15, color=BUS_COL, size=9.5))
    p.append(draw_time_arrow(t_fall_start, t_fall_end, y_scl_lo + 22, "tf", y_scl_lo + 15, color=BUS_COL, size=9.5))

    # t_HIGH
    p.append(draw_time_arrow(t_rise_end, t_fall_start, 70, "t_HIGH (тривалість високого рівня SCL)", 58, color=OK_COL, size=10, bold=True))

    # t_SU;DAT
    p.append(draw_time_arrow(t_sda_trans + 30, t_rise_end, 205, "t_SU;DAT (час встановлення)", 195, color=ACCENT, size=9.5, bold=True))

    # t_HD;DAT
    p.append(draw_time_arrow(t_fall_end, t_fall_end + 70, 205, "t_HD;DAT (час утримання)", 195, color=PURPLE, size=9.5, bold=True))

    # Labels inside zones
    p.append(rect(120, 100, 175, 36, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    p.append(text(207, 115, "ДОЗВОЛЕНА ЗМІНА SDA", size=9.5, color="#334155", bold=True))
    p.append(text(207, 128, "(під час низького SCL t_LOW)", size=9.5, color="#64748b"))

    p.append(rect(395, 100, 155, 36, fill="#dcfce7", stroke=OK_COL, sw=1.2, rx=4))
    p.append(text(472, 115, "ДІЙСНІСТЬ ДАНИХ (VALID)", size=9.5, color=OK_COL, bold=True))
    p.append(text(472, 128, "SDA стабільна (заборона змін)", size=9.5, color="#166534"))

    # Bottom summary box
    p.append(rect(30, 345, W - 60, 60, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=5))
    p.append(text(W / 2, 365, "t_SU;DAT — мінімальний час, за який передавач повинен виставити стабільний біт до зростання SCL вище 0.7 VDD.", size=10, color=INK, bold=True))
    p.append(text(W / 2, 385, "t_HD;DAT — час, протягом якого стан SDA повинен утримуватися після спаду SCL нижче 0.3 VDD для надійного зчитування.", size=9.5, color=MUTED))

    render(os.path.join(OUT, "data-validity-window.svg"), W, H, *p)


def fig_ack_nack_phase():
    W, H = 860, 440
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))

    p.append(text(W / 2, 32, "Фаза 9-го такту: передача керування лінією SDA, стробування ACK (0) і NACK (1)", size=13.5, bold=True))

    # Horizontal coordinate guidelines
    y_scl_hi = 85
    y_scl_lo = 155
    y_sda_hi = 215
    y_sda_lo = 285

    # Badges
    p.append(rect(25, y_scl_hi - 12, 55, 22, fill="#eff6ff", stroke=BUS_COL, sw=1.2, rx=3))
    p.append(text(52, y_scl_hi + 3, "SCL", size=10.5, color=BUS_COL, bold=True))

    p.append(rect(25, y_sda_hi - 12, 55, 22, fill="#fff7ed", stroke=ACCENT, sw=1.2, rx=3))
    p.append(text(52, y_sda_hi + 3, "SDA", size=10.5, color=ACCENT, bold=True))

    # Reference lines
    p.append(line(90, y_scl_hi, W - 30, y_scl_hi, color=MUTED_GRID, sw=1, dash="4,4"))
    p.append(line(90, y_scl_lo, W - 30, y_scl_lo, color=MUTED_GRID, sw=1, dash="4,4"))
    p.append(line(90, y_sda_hi, W - 30, y_sda_hi, color=MUTED_GRID, sw=1, dash="4,4"))
    p.append(line(90, y_sda_lo, W - 30, y_sda_lo, color=MUTED_GRID, sw=1, dash="4,4"))

    # Clocks: 8th bit, handover gap, 9th bit (ACK/NACK), end of byte
    t_clk8_rise = 170
    t_clk8_fall = 250
    t_handover_tx_rel = 270
    t_handover_rx_drive = 320
    t_clk9_rise = 450
    t_clk9_fall = 550
    t_handover_rx_rel = 580

    # Shaded regions for ownership - adjusted height to 235 to avoid partial overlap with callout rect at y=300
    p.append(rect(95, 55, t_handover_tx_rel - 95, 235, fill="#f8fafc", stroke="none"))
    p.append(rect(t_handover_tx_rel, 55, t_handover_rx_rel - t_handover_tx_rel, 235, fill="#ecfdf5", stroke="none"))
    p.append(rect(t_handover_rx_rel, 55, W - 30 - t_handover_rx_rel, 235, fill="#f8fafc", stroke="none"))

    # SCL trace (8th clock pulse and 9th clock pulse)
    scl_pts = [
        (95, y_scl_lo),
        (t_clk8_rise - 15, y_scl_lo),
        (t_clk8_rise, y_scl_hi),
        (t_clk8_fall, y_scl_hi),
        (t_clk8_fall + 15, y_scl_lo),
        (t_clk9_rise - 15, y_scl_lo),
        (t_clk9_rise, y_scl_hi),
        (t_clk9_fall, y_scl_hi),
        (t_clk9_fall + 15, y_scl_lo),
        (W - 35, y_scl_lo)
    ]
    p.append(polyline(scl_pts, color=BUS_COL, sw=2.5))

    # SDA trace:
    # 8th bit: Transmitter drives data bit (e.g. HIGH)
    # At t_handover_tx_rel: TX releases SDA to Hi-Z (pulled HIGH)
    # At t_handover_rx_drive: RX pulls SDA LOW for ACK
    sda_ack_pts = [
        (95, y_sda_hi),
        (t_handover_tx_rel, y_sda_hi),
        (t_handover_rx_drive, y_sda_lo),
        (t_clk9_fall + 20, y_sda_lo),
        (t_handover_rx_rel, y_sda_hi),
        (W - 35, y_sda_hi)
    ]
    p.append(polyline(sda_ack_pts, color=OK_COL, sw=2.5))

    # NACK path (Red dashed): RX does not pull low, SDA remains HIGH
    sda_nack_pts = [
        (t_handover_tx_rel, y_sda_hi),
        (t_handover_rx_rel + 30, y_sda_hi)
    ]
    p.append(polyline(sda_nack_pts, color=WARN_COL, sw=2.2, dash="4,4"))

    # Sample strobe marks
    p.append(arrow(t_clk9_rise + 50, y_scl_hi - 18, t_clk9_rise + 50, y_sda_lo - 8, color=PURPLE, sw=1.8))
    p.append(circle(t_clk9_rise + 50, y_sda_lo, 4, fill=PURPLE, stroke=PURPLE))
    p.append(text(t_clk9_rise + 50, y_scl_hi - 22, "Зчитування квитанції (Sample ACK)", size=9.5, color=PURPLE, bold=True))

    # Ownership badges above
    p.append(rect(110, 58, 145, 22, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    p.append(text(182, 72, "8-й біт: Керує Передавач", size=9.5, color="#334155", bold=True))

    p.append(rect(310, 58, 230, 22, fill="#dcfce7", stroke=OK_COL, sw=1.2, rx=3))
    p.append(text(425, 72, "9-й такт: Керує Приймач (ACK/NACK)", size=9.5, color=OK_COL, bold=True))

    p.append(rect(610, 58, 165, 22, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    p.append(text(692, 72, "Повернення лінії Передавачу", size=9.5, color="#334155", bold=True))

    # Callout for ACK and NACK
    p.append(rect(380, y_sda_lo + 15, 140, 24, fill="#ecfdf5", stroke=OK_COL, sw=1.2, rx=3))
    p.append(text(450, y_sda_lo + 30, "ACK: SDA притягнуто до 0", size=9.5, color=OK_COL, bold=True))

    p.append(rect(380, y_sda_hi - 35, 140, 24, fill="#fef2f2", stroke=WARN_COL, sw=1.2, rx=3))
    p.append(text(450, y_sda_hi - 20, "NACK: SDA залишено на 1", size=9.5, color=WARN_COL, bold=True))

    # Handover annotations
    p.append(text(t_handover_tx_rel, 335, "TX відпускає SDA (Hi-Z)", size=9.5, color=MUTED, anchor="middle"))
    p.append(text(t_handover_rx_drive, 348, "RX притягує SDA до GND", size=9.5, color=OK_COL, bold=True, anchor="middle"))
    p.append(text(t_handover_rx_rel, 335, "RX відпускає SDA (Hi-Z)", size=9.5, color=MUTED, anchor="middle"))

    # Bottom summary box
    p.append(rect(30, 365, W - 60, 60, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=5))
    p.append(text(W / 2, 385, "Критичний момент: передавач зобов'язаний відпустити лінію SDA до початку 9-го такту SCL.", size=10, color=INK, bold=True))
    p.append(text(W / 2, 405, "Приймач виставляє ACK завчасно (t_SU;DAT) і утримує його до спаду 9-го такту (t_HD;DAT), після чого повертає лінію.", size=9.5, color=MUTED))

    render(os.path.join(OUT, "ack-nack-phase.svg"), W, H, *p)


def fig_clock_stretching_dynamics():
    W, H = 860, 440
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))

    p.append(text(W / 2, 32, "Динаміка розтягування такту (Clock Stretching) на фізичному рівні SCL", size=13.5, bold=True))

    # Waveform vertical positions
    y_m_hi = 75
    y_m_lo = 125

    y_s_hi = 165
    y_s_lo = 215

    y_bus_hi = 255
    y_bus_lo = 305

    # Labels
    p.append(rect(20, y_m_hi - 8, 125, 22, fill="#f1f5f9", stroke="#64748b", sw=1, rx=3))
    p.append(text(82, y_m_hi + 6, "Ведучий: Внутр. такт", size=9.5, color="#1e293b", bold=True))

    p.append(rect(20, y_s_hi - 8, 125, 22, fill="#fef2f2", stroke=WARN_COL, sw=1, rx=3))
    p.append(text(82, y_s_hi + 6, "Ведений: MOSFET SCL", size=9.5, color=WARN_COL, bold=True))

    p.append(rect(20, y_bus_hi - 8, 125, 22, fill="#eff6ff", stroke=BUS_COL, sw=1.2, rx=3))
    p.append(text(82, y_bus_hi + 6, "Фізична лінія SCL", size=9.5, color=BUS_COL, bold=True))

    # Timing coordinates
    t_clk1_fall = 180
    t_m_rel = 280            # Master finishes nominal t_LOW and releases MOSFET
    t_s_rel = 520            # Slave finishes processing and releases MOSFET
    t_bus_rise_end = 570     # RC rise time completes to 0.7 VDD
    t_m_high_end = 720       # Master finishes t_HIGH

    # Shaded stretch zone - height 270
    p.append(rect(t_m_rel, 55, t_bus_rise_end - t_m_rel, 270, fill="#fffbeb", stroke="none"))
    p.append(line(t_m_rel, 55, t_m_rel, 325, color="#f59e0b", sw=1.2, dash="3,3"))
    p.append(line(t_s_rel, 55, t_s_rel, 325, color=WARN_COL, sw=1.2, dash="3,3"))
    p.append(line(t_bus_rise_end, 55, t_bus_rise_end, 325, color=OK_COL, sw=1.2, dash="3,3"))

    # Trace 1: Master internal desired state (Hi-Z vs Drive LOW)
    m_pts = [
        (150, y_m_hi),
        (t_clk1_fall, y_m_lo),
        (t_m_rel, y_m_hi),
        (t_m_high_end, y_m_lo),
        (W - 40, y_m_lo)
    ]
    p.append(polyline(m_pts, color="#64748b", sw=2.2))
    p.append(text(230, y_m_lo + 15, "Номінальний t_LOW ведучого", size=9.5, color="#64748b"))
    p.append(text(380, y_m_hi - 6, "Ведучий відпустив свій MOSFET (Hi-Z)", size=9.5, color="#64748b"))

    # Trace 2: Slave MOSFET state (Closed Hi-Z vs Open Drive LOW)
    s_pts = [
        (150, y_s_hi),
        (t_clk1_fall + 20, y_s_lo),
        (t_s_rel, y_s_hi),
        (W - 40, y_s_hi)
    ]
    p.append(polyline(s_pts, color=WARN_COL, sw=2.2))
    p.append(text(350, y_s_lo + 15, "Ведений тримає SCL на GND (виконує операцію)", size=9.5, color=WARN_COL, bold=True))
    p.append(text(620, y_s_hi - 6, "Ведений відпустив SCL", size=9.5, color=OK_COL, bold=True))

    # Trace 3: Physical SCL line (Wired-AND result with exponential RC rise)
    bus_pts = [
        (150, y_bus_lo),
        (t_clk1_fall, y_bus_lo),
        (t_s_rel, y_bus_lo),
        (t_s_rel + 15, y_bus_lo - 12),
        (t_s_rel + 30, y_bus_lo - 32),
        (t_bus_rise_end, y_bus_hi),
        (t_m_high_end, y_bus_hi),
        (t_m_high_end + 10, y_bus_lo),
        (W - 40, y_bus_lo)
    ]
    p.append(polyline(bus_pts, color=BUS_COL, sw=2.5))

    # Timing dimension arrows
    p.append(draw_time_arrow(t_clk1_fall, t_m_rel, 340, "t_LOW (номінал)", 352, color="#64748b", size=9.5))
    p.append(draw_time_arrow(t_m_rel, t_s_rel, 340, "t_stretch (розтягування)", 352, color="#b45309", size=9.5, bold=True))
    p.append(draw_time_arrow(t_s_rel, t_bus_rise_end, 340, "tr (RC)", 352, color=BUS_COL, size=9.5))
    p.append(draw_time_arrow(t_bus_rise_end, t_m_high_end, 340, "t_HIGH (фактичний)", 352, color=OK_COL, size=9.5, bold=True))

    # Explanatory badge
    p.append(rect(t_m_rel + 15, y_bus_lo - 45, 175, 24, fill="#fffbeb", stroke="#f59e0b", sw=1.2, rx=3))
    p.append(text(t_m_rel + 102, y_bus_lo - 30, "Ведучий бачить 0В і чекає!", size=9.5, color="#92400e", bold=True))

    p.append(rect(t_bus_rise_end + 10, y_bus_hi - 30, 185, 24, fill="#ecfdf5", stroke=OK_COL, sw=1.2, rx=3))
    p.append(text(t_bus_rise_end + 102, y_bus_hi - 15, "SCL >= 0.7 VDD -> старт t_HIGH", size=9.5, color=OK_COL, bold=True))

    # Bottom summary box
    p.append(rect(30, 370, W - 60, 55, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=5))
    p.append(text(W / 2, 388, "Ведучий починає відлік фази t_HIGH лише після того, як лінія фізично перетне поріг 0.7 VDD.", size=10, color=INK, bold=True))
    p.append(text(W / 2, 406, "Монтажне «І» гарантує безпечне узгодження темпу без додаткових апаратних ліній переривань.", size=9.5, color=MUTED))

    render(os.path.join(OUT, "clock-stretching-dynamics.svg"), W, H, *p)


def fig_timing_violations_comparison():
    W, H = 880, 430
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))

    p.append(text(W / 2, 32, "Порушення часових інтервалів: спотворення даних та помилкові умови START/STOP", size=13.5, bold=True))

    # 3 comparison columns
    col_w = 265
    xs = [30, 310, 590]

    # Panel 1: False START/STOP caused by jitter/glitch during SCL HIGH
    p.append(rect(xs[0], 55, col_w, 290, fill="#fef2f2", stroke=WARN_COL, sw=1.2, rx=6))
    p.append(rect(xs[0], 55, col_w, 28, fill="#fee2e2", stroke=WARN_COL, sw=1, rx=6))
    p.append(text(xs[0] + col_w / 2, 73, "1. Фальшивий START/STOP", size=10.5, color=WARN_COL, bold=True))

    # Waveform 1: SCL high, SDA transitions
    y_p1_scl = 120
    y_p1_sda = 175
    p.append(text(xs[0] + 15, y_p1_scl + 4, "SCL", size=9.5, color=BUS_COL, bold=True))
    p.append(text(xs[0] + 15, y_p1_sda + 4, "SDA", size=9.5, color=ACCENT, bold=True))

    p.append(line(xs[0] + 45, y_p1_scl, xs[0] + col_w - 20, y_p1_scl, color=BUS_COL, sw=2.2))
    sda_glitch = [
        (xs[0] + 45, y_p1_sda - 20),
        (xs[0] + 110, y_p1_sda - 20),
        (xs[0] + 130, y_p1_sda + 20),
        (xs[0] + 170, y_p1_sda + 20),
        (xs[0] + 190, y_p1_sda - 20),
        (xs[0] + col_w - 20, y_p1_sda - 20)
    ]
    p.append(polyline(sda_glitch, color=WARN_COL, sw=2.2))
    p.append(circle(xs[0] + 130, y_p1_sda, 12, fill="none", stroke=WARN_COL, sw=1.5))
    p.append(text(xs[0] + 130, y_p1_sda + 35, "Фальш. START", size=9.5, color=WARN_COL, bold=True))
    p.append(text(xs[0] + 190, y_p1_sda - 28, "Фальш. STOP", size=9.5, color=WARN_COL, bold=True))

    p.append(rect(xs[0] + 10, 240, col_w - 20, 95, fill="#ffffff", stroke="#fca5a5", sw=1, rx=4))
    p.append(text(xs[0] + col_w / 2, 258, "Причина: перешкода на SDA", size=9.5, color=WARN_COL, bold=True))
    p.append(text(xs[0] + col_w / 2, 275, "при високому рівні SCL.", size=9.5, color="#475569"))
    p.append(text(xs[0] + col_w / 2, 295, "Наслідок: апаратне скидання", size=9.5, color=INK, bold=True))
    p.append(text(xs[0] + col_w / 2, 312, "скриньки станів кінцевого автомата.", size=9.5, color="#475569"))

    # Panel 2: Setup time violation (t_SU;DAT < t_SU;DAT_min)
    p.append(rect(xs[1], 55, col_w, 290, fill="#fffbeb", stroke="#d97706", sw=1.2, rx=6))
    p.append(rect(xs[1], 55, col_w, 28, fill="#fef3c7", stroke="#d97706", sw=1, rx=6))
    p.append(text(xs[1] + col_w / 2, 73, "2. Порушення t_SU;DAT", size=10.5, color="#b45309", bold=True))

    y_p2_scl = 120
    y_p2_sda = 175
    p.append(text(xs[1] + 15, y_p2_scl + 4, "SCL", size=9.5, color=BUS_COL, bold=True))
    p.append(text(xs[1] + 15, y_p2_sda + 4, "SDA", size=9.5, color=ACCENT, bold=True))

    scl_p2 = [
        (xs[1] + 45, y_p2_scl + 20),
        (xs[1] + 140, y_p2_scl + 20),
        (xs[1] + 160, y_p2_scl - 20),
        (xs[1] + col_w - 20, y_p2_scl - 20)
    ]
    p.append(polyline(scl_p2, color=BUS_COL, sw=2.2))

    sda_p2 = [
        (xs[1] + 45, y_p2_sda + 20),
        (xs[1] + 145, y_p2_sda + 20),
        (xs[1] + 165, y_p2_sda - 20),
        (xs[1] + col_w - 20, y_p2_sda - 20)
    ]
    p.append(polyline(sda_p2, color=WARN_COL, sw=2.2))

    p.append(line(xs[1] + 160, y_p2_scl - 25, xs[1] + 160, y_p2_sda + 25, color=WARN_COL, sw=1.2, dash="2,2"))
    p.append(text(xs[1] + col_w / 2, y_p2_sda + 38, "Δt < t_SU;DAT(min)", size=9.5, color=WARN_COL, bold=True))

    p.append(rect(xs[1] + 10, 240, col_w - 20, 95, fill="#ffffff", stroke="#fde68a", sw=1, rx=4))
    p.append(text(xs[1] + col_w / 2, 258, "Причина: запізніла зміна SDA", size=9.5, color="#b45309", bold=True))
    p.append(text(xs[1] + col_w / 2, 275, "перед наростанням SCL.", size=9.5, color="#475569"))
    p.append(text(xs[1] + col_w / 2, 295, "Наслідок: метастабільність або", size=9.5, color=INK, bold=True))
    p.append(text(xs[1] + col_w / 2, 312, "зчитування хибного значення біта.", size=9.5, color="#475569"))

    # Panel 3: Insufficient t_BUF (Bus Free Time)
    p.append(rect(xs[2], 55, col_w, 290, fill="#f5f3ff", stroke=PURPLE, sw=1.2, rx=6))
    p.append(rect(xs[2], 55, col_w, 28, fill="#ede9fe", stroke=PURPLE, sw=1, rx=6))
    p.append(text(xs[2] + col_w / 2, 73, "3. Недостатній t_BUF", size=10.5, color=PURPLE, bold=True))

    y_p3_scl = 120
    y_p3_sda = 175
    p.append(text(xs[2] + 15, y_p3_scl + 4, "SCL", size=9.5, color=BUS_COL, bold=True))
    p.append(text(xs[2] + 15, y_p3_sda + 4, "SDA", size=9.5, color=ACCENT, bold=True))

    # STOP followed immediately by START with no buffer
    p.append(line(xs[2] + 45, y_p3_scl, xs[2] + col_w - 20, y_p3_scl, color=BUS_COL, sw=2.2))
    sda_p3 = [
        (xs[2] + 45, y_p3_sda + 20),
        (xs[2] + 100, y_p3_sda - 20), # STOP rise
        (xs[2] + 130, y_p3_sda - 20),
        (xs[2] + 150, y_p3_sda + 20), # Next START fall
        (xs[2] + col_w - 20, y_p3_sda + 20)
    ]
    p.append(polyline(sda_p3, color=PURPLE, sw=2.2))
    p.append(text(xs[2] + 100, y_p3_sda - 26, "STOP", size=9.5, color=OK_COL, bold=True))
    p.append(text(xs[2] + 160, y_p3_sda + 32, "START", size=9.5, color=WARN_COL, bold=True))
    p.append(draw_time_arrow(xs[2] + 100, xs[2] + 150, y_p3_sda, "t_BUF закороткий", y_p3_sda - 8, color=PURPLE, size=9.5, bold=True))

    p.append(rect(xs[2] + 10, 240, col_w - 20, 95, fill="#ffffff", stroke="#ddd6fe", sw=1, rx=4))
    p.append(text(xs[2] + col_w / 2, 258, "Причина: ведучий почав обмін", size=9.5, color=PURPLE, bold=True))
    p.append(text(xs[2] + col_w / 2, 275, "одразу після STOP без паузи.", size=9.5, color="#475569"))
    p.append(text(xs[2] + col_w / 2, 295, "Наслідок: ведені не встигли", size=9.5, color=INK, bold=True))
    p.append(text(xs[2] + col_w / 2, 312, "скинути внутрішні логічні стани.", size=9.5, color="#475569"))

    # Bottom summary box
    p.append(rect(30, 360, W - 60, 55, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=5))
    p.append(text(W / 2, 380, "Суворе дотримання параметрів NXP UM10204 виключає збої та десинхронізацію пристроїв на спільній шині.", size=10, color=INK, bold=True))
    p.append(text(W / 2, 398, "Апаратні фільтри придушення імпульсних завад (t_SP <= 50 нс) відсікають випадкові шуми на фронтах сигналів.", size=9.5, color=MUTED))

    render(os.path.join(OUT, "timing-violations-comparison.svg"), W, H, *p)


if __name__ == "__main__":
    fig_start_stop_timing()
    fig_data_validity_window()
    fig_ack_nack_phase()
    fig_clock_stretching_dynamics()
    fig_timing_violations_comparison()
    print("All figures generated successfully.")
