# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def path(d, color=LINE, sw=1.5, fill="none"):
    return f'<path d="{d}" stroke="{color}" stroke-width="{sw}" fill="{fill}"/>'


# ── 1. CAN Physical Levels (Dominant vs Recessive) ──────────────────────────
def fig_physical_levels():
    W, H = 820, 340
    p = []
    
    # Background card
    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfdfd", stroke="#e0e0e0", sw=1, rx=8))
    
    # Title
    p.append(text(W / 2, 36, "Фізичний рівень CAN: диференційні напруги CAN_H та CAN_L", size=14, color=INK, bold=True))
    
    # Voltage scale positions
    y_35 = 105
    y_25 = 155
    y_15 = 205
    y_00 = 280
    
    # Horizontal voltage guidelines
    p.append(line(80, y_35, 750, y_35, color="#e0e0e0", sw=1, dash="4,4"))
    p.append(text(65, y_35 + 4, "3.5 В", size=10, color=MUTED, anchor="end"))
    
    p.append(line(80, y_25, 750, y_25, color="#c0c0c0", sw=1.2, dash="2,2"))
    p.append(text(65, y_25 + 4, "2.5 В", size=10.5, color=MUTED, bold=True, anchor="end"))
    
    p.append(line(80, y_15, 750, y_15, color="#e0e0e0", sw=1, dash="4,4"))
    p.append(text(65, y_15 + 4, "1.5 В", size=10, color=MUTED, anchor="end"))
    
    p.append(line(80, y_00, 750, y_00, color=INK, sw=1.5))
    p.append(text(65, y_00 + 4, "0.0 В", size=10, color=MUTED, anchor="end"))
    
    # Vertical phase dividers
    p.append(line(260, 55, 260, y_00, color="#d0d0d0", sw=1.2, dash="3,3"))
    p.append(line(480, 55, 480, y_00, color="#d0d0d0", sw=1.2, dash="3,3"))
    
    # CAN_H Signal (Red/NEG)
    path_h = f"M 80 {y_25} L 260 {y_25} L 275 {y_35} L 465 {y_35} L 480 {y_25} L 680 {y_25}"
    p.append(path(path_h, color=NEG, sw=2.5))
    
    # CAN_L Signal (Blue)
    path_l = f"M 80 {y_25} L 260 {y_25} L 275 {y_15} L 465 {y_15} L 480 {y_25} L 680 {y_25}"
    p.append(path(path_l, color="#0288d1", sw=2.5))
    
    # Labels for CAN_H and CAN_L
    p.append(text(710, y_35 - 5, "CAN_H (3.5 В)", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(710, y_15 + 12, "CAN_L (1.5 В)", size=11, color="#0288d1", bold=True, anchor="start"))
    
    # Phase Headers & Differential Voltage text
    p.append(rect(100, 55, 140, 30, fill="#f0f4f8", stroke="#d0d0d0", rx=4))
    p.append(text(170, 74, "Рецесивний («1»)", size=11, color=MUTED, bold=True))
    p.append(text(170, y_25 - 12, "Vdiff ≈ 0 В", size=10.5, color=MUTED, bold=True))
    
    p.append(rect(290, 55, 160, 30, fill="#feeef0", stroke=NEG, rx=4))
    p.append(text(370, 74, "Домінантний («0»)", size=11, color=NEG, bold=True))
    
    # Vdiff arrows pointing away from badge to lines, without crossing badge text
    p.append(rect(315, 143, 110, 24, fill="#ffffff", stroke=NEG, rx=3))
    p.append(text(370, 159, "Vdiff ≈ 2.0 В", size=10.5, color=NEG, bold=True))
    
    p.append(arrow(370, 143, 370, y_35 + 4, color=NEG, sw=1.5))
    p.append(arrow(370, 167, 370, y_15 - 4, color=NEG, sw=1.5))
    
    p.append(rect(510, 55, 140, 30, fill="#f0f4f8", stroke="#d0d0d0", rx=4))
    p.append(text(580, 74, "Рецесивний («1»)", size=11, color=MUTED, bold=True))
    p.append(text(580, y_25 - 12, "Vdiff ≈ 0 В", size=10.5, color=MUTED, bold=True))
    
    # Bus Termination Box on bottom right
    p.append(rect(530, 235, 210, 40, fill="#fff8e1", stroke="#ffa000", rx=4))
    p.append(text(635, 260, "Термінація: 120 Ом на кінцях", size=10.5, color="#b78103", bold=True))

    render(os.path.join(OUT, "can-physical-levels.svg"), W, H, *p)


# ── 2. CAN Bit Timing (Time Quanta Breakdown) ──────────────────────────────
def fig_bit_timing():
    W, H = 820, 330
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfdfd", stroke="#e0e0e0", sw=1, rx=8))
    p.append(text(W / 2, 36, "Структура номінального бітового інтервалу CAN (Bit Timing)", size=14, color=INK, bold=True))
    
    bx, by, bw, bh = 60, 80, 700, 90
    p.append(rect(bx, by, bw, bh, fill="#fafafa", stroke=INK, sw=2, rx=6))
    
    x_sync = 60
    x_prop = 130
    x_ps1 = 340
    x_sample = 550
    
    p.append(rect(x_sync, by, 70, bh, fill="#eef4fc", stroke=NEG, sw=1.5))
    p.append(text(x_sync + 35, by + 40, "Sync_Seg", size=11, color=NEG, bold=True))
    p.append(text(x_sync + 35, by + 62, "1 Tq", size=10, color=MUTED))
    
    p.append(rect(x_prop, by, 210, bh, fill="#fff8e1", stroke="#f57c00", sw=1.5))
    p.append(text(x_prop + 105, by + 40, "Prop_Seg (Затримка)", size=11, color="#e65100", bold=True))
    p.append(text(x_prop + 105, by + 62, "1..8 Tq", size=10, color=MUTED))
    
    p.append(rect(x_ps1, by, 210, bh, fill="#e8f5e9", stroke=FIELD, sw=1.5))
    p.append(text(x_ps1 + 105, by + 40, "Phase_Seg1", size=11, color=FIELD, bold=True))
    p.append(text(x_ps1 + 105, by + 62, "1..8 Tq (подовження SJW)", size=10, color=MUTED))
    
    p.append(rect(x_sample, by, 210, bh, fill="#f3e5f5", stroke="#8e24aa", sw=1.5))
    p.append(text(x_sample + 105, by + 40, "Phase_Seg2", size=11, color="#6a1b9a", bold=True))
    p.append(text(x_sample + 105, by + 62, "2..8 Tq (вкорочення SJW)", size=10, color=MUTED))
    
    p.append(line(x_sample, by - 15, x_sample, by + bh + 45, color=NEG, sw=2.5, dash="4,2"))
    p.append(circle(x_sample, by, 6, fill=NEG, stroke="#ffffff", sw=1.5))
    
    p.append(rect(x_sample - 95, by + bh + 15, 190, 30, fill=NEG, rx=4))
    p.append(text(x_sample, by + bh + 35, "Точка вибірки (Sample Point)", size=10.5, color="#ffffff", bold=True))
    p.append(text(x_sample, by + bh + 58, "Рекомендовано: 75% .. 87.5%", size=10, color=NEG, bold=True))
    
    p.append(text(W / 2, by + bh + 105, "Квант часу (Time Quantum, Tq) = BRP / f_sys", size=11, color=INK, bold=True))
    
    render(os.path.join(OUT, "can-bit-timing.svg"), W, H, *p)


# ── 3. CAN Frame Structure (Standard 2.0A vs Extended 2.0B) ────────────────
def fig_frame_structure():
    W, H = 820, 360
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfdfd", stroke="#e0e0e0", sw=1, rx=8))
    p.append(text(W / 2, 34, "Структура кадру даних CAN 2.0A (стандартний 11-біт ID)", size=13.5, color=INK, bold=True))
    
    y1 = 65
    h1 = 60
    
    fields = [
        ("SOF", "1 біт", 40, "#e3f2fd", NEG),
        ("ID (Ідентифікатор)", "11 біт", 150, "#fff3e0", "#e65100"),
        ("RTR", "1 біт", 42, "#ffe0b2", "#e65100"),
        ("IDE", "1 біт", 42, "#f1f8e9", FIELD),
        ("r0", "1 біт", 38, "#f1f8e9", FIELD),
        ("DLC", "4 біти", 55, "#e8f5e9", FIELD),
        ("Поле даних (Data Field)", "0 .. 8 байтів (0 .. 64 біти)", 210, "#e8eaf6", "#283593"),
        ("CRC", "15 біт", 75, "#f3e5f5", "#6a1b9a"),
        ("Del", "1b", 28, "#f3e5f5", "#6a1b9a"),
        ("ACK", "1 біт", 45, "#e0f2f1", "#00695c"),
        ("Del", "1b", 28, "#e0f2f1", "#00695c"),
        ("EOF", "7 бітів", 52, "#eceff1", MUTED),
    ]
    
    cur_x = 40
    for name, sz, w, bg, fg in fields:
        p.append(rect(cur_x, y1, w, h1, fill=bg, stroke=fg, sw=1.2, rx=3))
        p.append(text(cur_x + w / 2, y1 + 26, name, size=10, color=fg, bold=True))
        p.append(text(cur_x + w / 2, y1 + 46, sz, size=9.5, color=MUTED))
        cur_x += w
        
    p.append(line(80, y1 + h1 + 6, 272, y1 + h1 + 6, color="#e65100", sw=1.5))
    p.append(text(176, y1 + h1 + 20, "Арбітражне поле", size=10, color="#e65100", bold=True))
    
    p.append(line(274, y1 + h1 + 6, 407, y1 + h1 + 6, color=FIELD, sw=1.5))
    p.append(text(340, y1 + h1 + 20, "Поле керування", size=10, color=FIELD, bold=True))
    
    p.append(line(618, y1 + h1 + 6, 721, y1 + h1 + 6, color="#6a1b9a", sw=1.5))
    p.append(text(670, y1 + h1 + 20, "Перевірка CRC", size=10, color="#6a1b9a", bold=True))
    
    p.append(line(40, 185, 780, 185, color="#e0e0e0", sw=1, dash="4,4"))
    
    p.append(text(W / 2, 210, "Розширений кадр CAN 2.0B (29-біт ID): розбиття арбітражного поля", size=13, color=INK, bold=True))
    
    y2 = 230
    h2 = 55
    ext_fields = [
        ("Base ID", "11 біт", 130, "#fff3e0", "#e65100"),
        ("SRR", "1 біт (1)", 50, "#ffe0b2", "#e65100"),
        ("IDE", "1 біт (1)", 50, "#f1f8e9", FIELD),
        ("ID Extension", "18 бітів", 170, "#ffe0b2", "#e65100"),
        ("RTR", "1 біт", 50, "#ffe0b2", "#e65100"),
        ("r1 / r0 / DLC", "6 бітів", 120, "#e8f5e9", FIELD),
        ("Дані, CRC, ACK, EOF...", "без змін", 150, "#f5f5f5", MUTED),
    ]
    
    cur_x = 50
    for name, sz, w, bg, fg in ext_fields:
        p.append(rect(cur_x, y2, w, h2, fill=bg, stroke=fg, sw=1.2, rx=3))
        p.append(text(cur_x + w / 2, y2 + 24, name, size=10, color=fg, bold=True))
        p.append(text(cur_x + w / 2, y2 + 42, sz, size=9.5, color=MUTED))
        cur_x += w

    p.append(text(W / 2, 325, "Сумарний ідентифікатор 2.0B = [Base ID 11b] + [ID Extension 18b] = 29 бітів", size=10.5, color=NEG, bold=True))

    render(os.path.join(OUT, "can-frame-structure.svg"), W, H, *p)


# ── 4. CAN Fault Confinement State Machine ──────────────────────────────────
def fig_fault_confinement():
    W, H = 820, 340
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfdfd", stroke="#e0e0e0", sw=1, rx=8))
    p.append(text(W / 2, 34, "Автомат станів ізоляції помилок CAN (Fault Confinement)", size=14, color=INK, bold=True))
    
    p.append(rect(60, 95, 200, 150, fill="#e8f5e9", stroke=FIELD, sw=2, rx=8))
    p.append(text(160, 122, "Error Active", size=13, color=FIELD, bold=True))
    p.append(text(160, 142, "(Активний щодо помилок)", size=9.5, color=MUTED))
    p.append(line(75, 152, 245, 152, color="#c8e6c9", sw=1))
    p.append(text(160, 170, "TEC < 128  |  REC < 128", size=10.5, color=FIELD, bold=True))
    p.append(text(160, 195, "• Шле Active Error Flag", size=9.5, color=INK))
    p.append(text(160, 210, "(6 домінантних бітів)", size=9.5, color=MUTED))
    p.append(text(160, 228, "• Передає без затримок", size=9.5, color=INK))
    
    p.append(rect(310, 95, 200, 150, fill="#fff3e0", stroke="#f57c00", sw=2, rx=8))
    p.append(text(410, 122, "Error Passive", size=13, color="#e65100", bold=True))
    p.append(text(410, 142, "(Пасивний щодо помилок)", size=9.5, color=MUTED))
    p.append(line(325, 152, 495, 152, color="#ffe0b2", sw=1))
    p.append(text(410, 170, "TEC ≥ 128  або  REC ≥ 128", size=10.5, color="#e65100", bold=True))
    p.append(text(410, 195, "• Шле Passive Error Flag", size=9.5, color=INK))
    p.append(text(410, 210, "(6 рецесивних бітів)", size=9.5, color=MUTED))
    p.append(text(410, 228, "• Пауза Suspend TX (+8b)", size=9.5, color=INK))
    
    p.append(rect(560, 95, 200, 150, fill="#ffebee", stroke=NEG, sw=2, rx=8))
    p.append(text(660, 122, "Bus-Off", size=13, color=NEG, bold=True))
    p.append(text(660, 142, "(Відключений від шини)", size=9.5, color=MUTED))
    p.append(line(575, 152, 745, 152, color="#ffcdd2", sw=1))
    p.append(text(660, 170, "TEC > 255", size=11, color=NEG, bold=True))
    p.append(text(660, 195, "• Виходи PHY відключені", size=9.5, color=NEG, bold=True))
    p.append(text(660, 215, "• Передача заборонена", size=9.5, color=INK))
    p.append(text(660, 230, "• Відновлення: скид / 128×11b", size=9.5, color=MUTED))
    
    p.append(arrow(260, 130, 310, 130, color="#f57c00", sw=1.8))
    p.append(text(285, 120, "TEC/REC ≥ 128", size=9.5, color="#e65100", bold=True))
    
    p.append(arrow(310, 190, 260, 190, color=FIELD, sw=1.8))
    p.append(text(285, 203, "TEC, REC ≤ 127", size=9.5, color=FIELD, bold=True))
    
    p.append(arrow(510, 130, 560, 130, color=NEG, sw=1.8))
    p.append(text(535, 120, "TEC > 255", size=9.5, color=NEG, bold=True))
    
    p.append(path("M 660 245 L 660 285 L 160 285 L 160 245", color=FIELD, sw=1.5, fill="none"))
    p.append(arrow(160, 250, 160, 245, color=FIELD, sw=1.5))
    p.append(rect(300, 272, 220, 24, fill="#ffffff", stroke=FIELD, rx=3))
    p.append(text(410, 288, "Скидання ПЗ або 128 послідовностей 11b рецесивних", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "can-fault-confinement.svg"), W, H, *p)


if __name__ == "__main__":
    fig_physical_levels()
    fig_bit_timing()
    fig_frame_structure()
    fig_fault_confinement()
    print("All CAN Bus SVG figures generated successfully.")
