# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. LIN Physical Layer Diagram ──────────────────────────────────────────────
def fig_physical_layer():
    W, H = 820, 360
    frags = []
    
    # Title
    frags.append(text(410, 24, "Фізична топологія LIN: однопровідна шина 12V з відкритим колектором", size=14, bold=True))

    # Power Rail VBAT (12V)
    vbat_y = 60
    frags.append(line(80, vbat_y, 740, vbat_y, color=POS, sw=2, dash="6,3"))
    frags.append(text(755, vbat_y + 4, "VBAT (+12V)", size=11, color=POS, bold=True, anchor="start"))

    # LIN Bus Line
    bus_y = 170
    frags.append(line(80, bus_y, 740, bus_y, color=NEG, sw=2.5))
    frags.append(text(410, bus_y - 12, "Однопровідна шина LIN (Recessive = 12V, Dominant = 0V)", size=11, color=NEG, bold=True))

    # Master Node
    mx, my = 120, 220
    frags.append(rect(mx, my, 180, 110, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    frags.append(text(mx + 90, my + 24, "Master Node", size=13, color=NEG, bold=True))
    frags.append(text(mx + 90, my + 44, "ПЛК / Дверний модуль ECU", size=10, color=MUTED))
    frags.append(rect(mx + 20, my + 56, 140, 40, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    frags.append(text(mx + 90, my + 80, "Pull-Up 1 kΩ + Діод", size=11, color=INK, bold=True))

    # Master connection to VBAT and LIN
    frags.append(line(mx + 90, vbat_y, mx + 90, my, color=POS, sw=1.5))
    frags.append(circle(mx + 90, vbat_y, 3.5, fill=POS, stroke=POS))
    frags.append(line(mx + 90, bus_y, mx + 90, my, color=NEG, sw=1.5))
    frags.append(circle(mx + 90, bus_y, 4, fill=NEG, stroke=NEG))

    # Slave 1 Node
    s1x, s1y = 380, 220
    frags.append(rect(s1x, s1y, 170, 110, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(s1x + 85, s1y + 24, "Slave Node 1", size=13, color=FIELD, bold=True))
    frags.append(text(s1x + 85, s1y + 44, "Модуль склопідйомника", size=10, color=MUTED))
    frags.append(rect(s1x + 15, s1y + 56, 140, 40, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    frags.append(text(s1x + 85, s1y + 80, "Pull-Up 30 kΩ + Діод", size=11, color=INK, bold=True))

    # Slave 1 connection
    frags.append(line(s1x + 85, vbat_y, s1x + 85, s1y, color=POS, sw=1.5))
    frags.append(circle(s1x + 85, vbat_y, 3.5, fill=POS, stroke=POS))
    frags.append(line(s1x + 85, bus_y, s1x + 85, s1y, color=NEG, sw=1.5))
    frags.append(circle(s1x + 85, bus_y, 4, fill=FIELD, stroke=FIELD))

    # Slave N Node
    snx, sny = 600, 220
    frags.append(rect(snx, sny, 170, 110, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(snx + 85, sny + 24, "Slave Node N (≤16)", size=13, color=FIELD, bold=True))
    frags.append(text(snx + 85, sny + 44, "Привід дзеркала / LED", size=10, color=MUTED))
    frags.append(rect(snx + 15, sny + 56, 140, 40, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    frags.append(text(snx + 85, sny + 80, "Pull-Up 30 kΩ + Діод", size=11, color=INK, bold=True))

    # Slave N connection
    frags.append(line(snx + 85, vbat_y, snx + 85, sny, color=POS, sw=1.5))
    frags.append(circle(snx + 85, vbat_y, 3.5, fill=POS, stroke=POS))
    frags.append(line(snx + 85, bus_y, snx + 85, sny, color=NEG, sw=1.5))
    frags.append(circle(snx + 85, bus_y, 4, fill=FIELD, stroke=FIELD))

    render(os.path.join(OUT, "lin-physical-layer.svg"), W, H, *frags)


# ── 2. LIN Frame Structure Diagram ────────────────────────────────────────────
def fig_frame_structure():
    W, H = 840, 280
    frags = []

    frags.append(text(420, 24, "Формат кадру LIN (Header передає Master, Response — Slave/Master)", size=14, bold=True))

    # Header Box (Master)
    hx, hy, hw, hh = 40, 60, 360, 160
    frags.append(rect(hx, hy, hw, hh, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    frags.append(text(hx + hw / 2, hy + 24, "HEADER (Заголовок від Master)", size=13, color=NEG, bold=True))

    # Header components: Break, Sync, PID
    b1_x = hx + 15
    frags.append(rect(b1_x, hy + 45, 100, 85, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(b1_x + 50, hy + 70, "Break Field", size=11, color=NEG, bold=True))
    frags.append(text(b1_x + 50, hy + 92, "≥13 біт Low", size=10, color=MUTED))
    frags.append(text(b1_x + 50, hy + 112, "+ Delimiter ≥1b", size=9.5, color=MUTED))

    b2_x = b1_x + 110
    frags.append(rect(b2_x, hy + 45, 100, 85, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(b2_x + 50, hy + 70, "Sync Byte", size=11, color=NEG, bold=True))
    frags.append(text(b2_x + 50, hy + 92, "0x55", size=12, color=INK, bold=True))
    frags.append(text(b2_x + 50, hy + 112, "01010101b", size=9.5, color=MUTED))

    b3_x = b2_x + 110
    frags.append(rect(b3_x, hy + 45, 110, 85, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(b3_x + 55, hy + 70, "PID Byte", size=11, color=NEG, bold=True))
    frags.append(text(b3_x + 55, hy + 92, "ID (6b) + P0,P1", size=10, color=INK, bold=True))
    frags.append(text(b3_x + 55, hy + 112, "0x00 .. 0x3F", size=9.5, color=MUTED))

    # Response Box (Slave or Master)
    rx, ry, rw, rh = 430, 60, 370, 160
    frags.append(rect(rx, ry, rw, rh, fill="#eef6ef", stroke=FIELD, sw=2, rx=8))
    frags.append(text(rx + rw / 2, ry + 24, "RESPONSE (Відповідь від адресованого вузла)", size=13, color=FIELD, bold=True))

    # Response components: Data 1..N, Checksum
    d1_x = rx + 20
    frags.append(rect(d1_x, ry + 45, 200, 85, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(d1_x + 100, ry + 70, "Data Bytes (1 .. 8 байт)", size=11, color=FIELD, bold=True))
    frags.append(text(d1_x + 100, ry + 92, "Байт 1 ... Байт N", size=10.5, color=INK))
    frags.append(text(d1_x + 100, ry + 112, "Корисне навантаження", size=9.5, color=MUTED))

    c1_x = d1_x + 215
    frags.append(rect(c1_x, ry + 45, 115, 85, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(c1_x + 57, ry + 70, "Checksum", size=11, color=FIELD, bold=True))
    frags.append(text(c1_x + 57, ry + 90, "Classic / Enhanced", size=9.5, color=INK, bold=True))
    frags.append(text(c1_x + 57, ry + 112, "1 байт CRC", size=9.5, color=MUTED))

    # Inter-frame response space note below
    frags.append(text(420, 250, "Між Header і Response допускається пауза (Response Space) для перемикання напрямку шини", size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "lin-frame-structure.svg"), W, H, *frags)


# ── 3. LIN Sync Mechanism Diagram ──────────────────────────────────────────────
def fig_sync_mechanism():
    W, H = 820, 300
    frags = []

    frags.append(text(410, 24, "Механізм автосинхронізації за Sync-байтом 0x55 (UART Baud Rate Adjust)", size=14, bold=True))

    # Oscillogram timeline
    ox, oy = 60, 70
    timeline_w = 700
    
    # Recessive level line (12V / High)
    # Dominant level line (0V / Low)
    y_high = oy + 20
    y_low = oy + 100

    frags.append(line(ox - 20, y_high, ox + timeline_w + 20, y_high, color="#d0d0d0", sw=1, dash="4,4"))
    frags.append(text(ox - 30, y_high + 4, "High (1)", size=10, color=MUTED, anchor="end"))
    
    frags.append(line(ox - 20, y_low, ox + timeline_w + 20, y_low, color="#d0d0d0", sw=1, dash="4,4"))
    frags.append(text(ox - 30, y_low + 4, "Low (0)", size=10, color=MUTED, anchor="end"))

    # Square wave for 0x55:
    # 0x55 over LSB-first UART is: Start(0), D0(1), D1(0), D2(1), D3(0), D4(1), D5(0), D6(1), D7(0), Stop(1)
    # Bit slots: 10 bit periods.
    bit_w = 64
    bits = [
        ("Start", 0), ("D0", 1), ("D1", 0), ("D2", 1), ("D3", 0),
        ("D4", 1), ("D5", 0), ("D6", 1), ("D7", 0), ("Stop", 1)
    ]

    path_pts = []
    curr_x = ox
    curr_level = 1 # Start from High before Start bit
    path_pts.append((curr_x, y_high))

    falling_edges = []

    for i, (bname, bval) in enumerate(bits):
        target_y = y_low if bval == 0 else y_high
        if target_y != (y_low if curr_level == 0 else y_high):
            # Edge transition
            path_pts.append((curr_x, target_y))
            if bval == 0:
                falling_edges.append(curr_x)
        curr_level = bval
        curr_x += bit_w
        path_pts.append((curr_x, target_y))

    # Draw waveform path
    d_str = "M %f %f" % path_pts[0]
    for px, py in path_pts[1:]:
        d_str += " L %f %f" % (px, py)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_str, NEG))

    # Bit labels below bits
    for i, (bname, bval) in enumerate(bits):
        bx = ox + i * bit_w + bit_w / 2
        frags.append(text(bx, y_low + 22, bname, size=10.5, color=INK, bold=True))

    # Show falling edges measurement arrows
    fe_y = y_low + 45
    if len(falling_edges) >= 5:
        # Measure 8 bit periods between 1st falling edge (Start bit) and 5th falling edge (D7 bit)
        x_start = falling_edges[0]
        x_end = falling_edges[4]
        frags.append(line(x_start, y_low + 5, x_start, fe_y + 15, color=POS, sw=1.2, dash="3,3"))
        frags.append(line(x_end, y_low + 5, x_end, fe_y + 15, color=POS, sw=1.2, dash="3,3"))
        frags.append(arrow(x_start, fe_y, x_end, fe_y, color=POS, sw=1.8))
        frags.append(arrow(x_end, fe_y, x_start, fe_y, color=POS, sw=1.8))
        frags.append(text((x_start + x_end) / 2, fe_y - 6, "Виміряний інтервал = 8 × T_bit (5 спадних фронтів)", size=11, color=POS, bold=True))

    # Equation note at bottom
    frags.append(rect(150, 235, 520, 45, fill="#fff8e7", stroke="#d97706", sw=1.2, rx=6))
    frags.append(text(410, 255, "T_bit = (Час між 1-м та 5-м спадним фронтом) / 8", size=11.5, color="#b45309", bold=True))
    frags.append(text(410, 271, "Slave підганяє дільник частоти таймера RC-генератора під виміряне значення T_bit", size=10, color=MUTED))

    render(os.path.join(OUT, "lin-sync-mechanism.svg"), W, H, *frags)


# ── 4. LIN Schedule Cycle Diagram ──────────────────────────────────────────────
def fig_schedule_cycle():
    W, H = 820, 310
    frags = []

    frags.append(text(410, 24, "Циклічний розклад шини (LIN Schedule Table) та часові слоти", size=14, bold=True))

    # Schedule Table Container
    sx, sy, sw, sh = 40, 55, 740, 180
    frags.append(rect(sx, sy, sw, sh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))

    # Time slots
    slots = [
        ("Слот 1 (10 ms)", "Unconditional Frame", "PID 0x10 (Двері: кнопка)", "#eaf0fd", NEG),
        ("Слот 2 (10 ms)", "Unconditional Frame", "PID 0x22 (Дзеркало: кут)", "#eaf0fd", NEG),
        ("Слот 3 (15 ms)", "Event-Triggered Frame", "PID 0x30 (Подія кнопка)", "#fef3c7", "#d97706"),
        ("Слот 4 (20 ms)", "Diagnostic Master Req", "PID 0x3C (Запит UDS)", "#fce7f3", "#db2777"),
    ]

    slot_w = 170
    gap = 12
    start_x = sx + 15

    for i, (stitle, stype, spid, sbg, scolor) in enumerate(slots):
        x = start_x + i * (slot_w + gap)
        y = sy + 35
        frags.append(rect(x, y, slot_w, 120, fill=sbg, stroke=scolor, sw=1.5, rx=6))
        frags.append(text(x + slot_w / 2, y + 22, stitle, size=11, color=scolor, bold=True))
        frags.append(line(x + 10, y + 32, x + slot_w - 10, y + 32, color=scolor, sw=1, dash="2,2"))
        frags.append(text(x + slot_w / 2, y + 54, stype, size=10.5, color=INK, bold=True))
        frags.append(text(x + slot_w / 2, y + 78, spid, size=10, color=MUTED))
        frags.append(text(x + slot_w / 2, y + 100, "Header + Response", size=9.5, color=MUTED, italic=True))

    # Time axis arrow at bottom
    ax_y = sy + sh + 30
    frags.append(line(sx, ax_y, sx + sw, ax_y, color=INK, sw=1.5))
    frags.append(arrow(sx + sw - 20, ax_y, sx + sw, ax_y, color=INK, sw=1.8))
    frags.append(text(sx + sw / 2, ax_y + 20, "Час циклу розкладу (Schedule Cycle Time = 55 ms)", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "lin-schedule-cycle.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_physical_layer()
    fig_frame_structure()
    fig_sync_mechanism()
    fig_schedule_cycle()
    print("Generated 4 SVG diagrams successfully.")
