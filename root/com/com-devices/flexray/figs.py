# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. Communication Cycle Structure ─────────────────────────────────────────
def fig_communication_cycle():
    W, H = 840, 360
    p = []

    # Title & Cycle Container
    p.append(rect(30, 45, 780, 240, fill="#fafbfc", stroke=MUTED, sw=1.5, rx=8))

    # Four Segments
    x_st = 50
    w_st = 290
    x_dy = x_st + w_st
    w_dy = 240
    x_sw = x_dy + w_dy
    w_sw = 95
    x_nit = x_sw + w_sw
    w_nit = 115
    y_seg = 65
    h_seg = 125

    # Static Segment (TDMA)
    p.append(rect(x_st, y_seg, w_st, h_seg, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    p.append(text(x_st + w_st/2, y_seg + 18, "1. Статичний сегмент (Static)", size=11, color=NEG, bold=True))
    p.append(text(x_st + w_st/2, y_seg + 34, "TDMA — Фіксовані слоти", size=9.5, color=MUTED))
    # Sub-slots in Static
    slot_w = (w_st - 20) / 3
    for i in range(3):
        sx = x_st + 10 + i * slot_w
        p.append(rect(sx + 2, y_seg + 46, slot_w - 4, 68, fill="#ffffff", stroke=NEG, sw=1.2, rx=3))
        p.append(text(sx + slot_w/2, y_seg + 68, f"Слот {i+1}", size=10, color=NEG, bold=True))
        p.append(text(sx + slot_w/2, y_seg + 92, "Детермін.", size=9, color=MUTED))

    # Dynamic Segment (FTDMA)
    p.append(rect(x_dy, y_seg, w_dy, h_seg, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    p.append(text(x_dy + w_dy/2, y_seg + 18, "2. Динамічний сегмент (Dynamic)", size=11, color=POS, bold=True))
    p.append(text(x_dy + w_dy/2, y_seg + 34, "FTDMA — Мініслоти", size=9.5, color=MUTED))
    # Minislots
    ms_w = (w_dy - 20) / 4
    for i in range(4):
        mx = x_dy + 10 + i * ms_w
        p.append(rect(mx + 1, y_seg + 46, ms_w - 2, 68, fill="#ffffff", stroke=POS, sw=1, rx=2))
        p.append(text(mx + ms_w/2, y_seg + 80, f"MS {i+1}", size=9.5, color=POS, bold=True))

    # Symbol Window
    p.append(rect(x_sw, y_seg, w_sw, h_seg, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(x_sw + w_sw/2, y_seg + 22, "3. Symbol Window", size=10, color=FIELD, bold=True))
    p.append(text(x_sw + w_sw/2, y_seg + 50, "Символи", size=9.5, color=MUTED))
    p.append(text(x_sw + w_sw/2, y_seg + 85, "MTS / CAS", size=9.5, color=FIELD, bold=True))

    # NIT (Network Idle Time)
    p.append(rect(x_nit, y_seg, w_nit, h_seg, fill="#fff3cd", stroke="#856404", sw=1.8, rx=4))
    p.append(text(x_nit + w_nit/2, y_seg + 22, "4. NIT", size=11, color="#856404", bold=True))
    p.append(text(x_nit + w_nit/2, y_seg + 50, "Пауза шини", size=9.5, color=MUTED))
    p.append(text(x_nit + w_nit/2, y_seg + 78, "Корекція часу", size=9.5, color="#856404", bold=True))
    p.append(text(x_nit + w_nit/2, y_seg + 102, "(Offset & Rate)", size=9, color=MUTED))

    # Bottom Cycle Arrow
    p.append(arrow(50, 215, 790, 215, color=INK, sw=1.8))
    p.append(text(420, 205, "Тривалість одного комунікаційного циклу T_cycle (наприклад, 5.0 мс)", size=10.5, color=INK, bold=True))

    # Explanatory Note Box
    box, _, _ = textbox(420, 310,
                        "Кожен цикли повторюється циклічно (Cycle Count 0..63). Статичний сегмент гарантує жорсткий детермінізм, а динамічний дає гнучкість для подій.",
                        size=11, bold=True, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=760)
    p.append(box)

    render(os.path.join(OUT, "flexray-communication-cycle.svg"), W, H, *p,
           title="Структура комунікаційного циклу FlexRay (Communication Cycle)")


# ── 2. FlexRay Frame Structure ───────────────────────────────────────────────
def fig_frame_structure():
    W, H = 840, 390
    p = []

    # Header Box (5 Bytes / 40 Bits)
    hx, hy, hw, hh = 40, 55, 280, 215
    p.append(rect(hx, hy, hw, hh, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(hx + hw/2, hy + 20, "Заголовок Кадру (Header)", size=11.5, color=NEG, bold=True))
    p.append(text(hx + hw/2, hy + 35, "5 байтів = 40 бітів", size=9.5, color=MUTED))

    header_fields = [
        ("Reserved bit", "1b", "Зарезервовано (0)"),
        ("Payload Preamble", "1b", "Наявність індикатора"),
        ("Null Frame Ind.", "1b", "1 = Норм, 0 = Порожній"),
        ("Sync Frame Ind.", "1b", "1 = Вузол синхронізації"),
        ("Startup Frame Ind.", "1b", "1 = Холодний старт"),
        ("Frame ID", "11b", "Номер слота (1..2047)"),
        ("Payload Length", "12b", "Довжина в 16-біт словах"),
        ("Header CRC", "11b", "CRC заголовка (0x385)"),
        ("Cycle Count", "6b", "Номер циклу (0..63)"),
    ]
    fy = hy + 50
    for title, bits, desc in header_fields:
        p.append(text(hx + 10, fy, f"• {title} ({bits}):", size=9, color=INK, anchor="start", bold=True))
        p.append(text(hx + 175, fy, desc, size=9, color=MUTED, anchor="start"))
        fy += 17

    # Payload Box (0..254 Bytes)
    px, py, pw, ph = 330, 55, 290, 215
    p.append(rect(px, py, pw, ph, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(px + pw/2, py + 20, "Корисне Навантаження (Payload)", size=11.5, color=FIELD, bold=True))
    p.append(text(px + pw/2, py + 35, "від 0 до 254 байтів (до 127 слів)", size=9.5, color=MUTED))

    p.append(rect(px + 15, py + 50, pw - 30, 50, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(px + pw/2, py + 70, "Слово 0 (16 біт) ... Слово N (16 біт)", size=10, color=FIELD, bold=True))
    p.append(text(px + pw/2, py + 86, "Сигнали датчиків та команд керування", size=9, color=MUTED))

    p.append(rect(px + 15, py + 115, pw - 30, 75, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(px + pw/2, py + 135, "Опціональний вектор керування", size=9.5, color=INK, bold=True))
    p.append(text(px + pw/2, py + 153, "Network Management Vector (у статичному)", size=9, color=MUTED))
    p.append(text(px + pw/2, py + 171, "або Message ID (у динамічному)", size=9, color=MUTED))

    # Trailer Box (3 Bytes / 24 Bits)
    tx, ty, tw, th = 630, 55, 170, 215
    p.append(rect(tx, ty, tw, th, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    p.append(text(tx + tw/2, ty + 20, "Трейлер (Trailer)", size=11.5, color=POS, bold=True))
    p.append(text(tx + tw/2, ty + 35, "3 байти = 24 біти", size=9.5, color=MUTED))

    p.append(rect(tx + 12, ty + 65, tw - 24, 85, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(tx + tw/2, ty + 90, "Frame CRC", size=11.5, color=POS, bold=True))
    p.append(text(tx + tw/2, ty + 112, "24-бітний контрольний", size=9.5, color=INK))
    p.append(text(tx + tw/2, ty + 130, "код кадру (0x5B2EC7)", size=9, color=MUTED))

    # Bottom Summary Line
    box, _, _ = textbox(420, 330,
                        "Загальна довжина кадру: 5 байтів заголовка + N байтів даних + 3 байти CRC. Усі значення передаються у форматі Big-Endian.",
                        size=11, bold=True, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=760)
    p.append(box)

    render(os.path.join(OUT, "flexray-frame-structure.svg"), W, H, *p,
           title="Анатомія кадру FlexRay: Заголовок, Дані та Трейлер")


# ── 3. FlexRay Bus Topologies ────────────────────────────────────────────────
def fig_bus_topologies():
    W, H = 840, 380
    p = []

    # Panel 1: Dual Channel Bus Topology
    p.append(rect(30, 50, 375, 230, fill="#fafbfc", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(217, 72, "1. Пасивна дубльована шина (Dual Bus)", size=11.5, color=NEG, bold=True))

    # Channel A and Channel B lines
    p.append(line(50, 110, 385, 110, color=NEG, sw=2))
    p.append(text(55, 100, "Канал A", size=9.5, color=NEG, bold=True, anchor="start"))

    p.append(line(50, 130, 385, 130, color=POS, sw=2))
    p.append(text(55, 142, "Канал B", size=9.5, color=POS, bold=True, anchor="start"))

    # Nodes on Bus
    nodes_bus = [("ECU 1", 110), ("ECU 2", 217), ("ECU 3", 325)]
    for name, nx in nodes_bus:
        p.append(rect(nx - 35, 170, 70, 50, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
        p.append(text(nx, 195, name, size=10.5, color=NEG, bold=True))
        # Taps
        p.append(line(nx - 10, 110, nx - 10, 170, color=NEG, sw=1.2))
        p.append(line(nx + 10, 130, nx + 10, 170, color=POS, sw=1.2))

    p.append(text(217, 255, "Передача даних дублюється або подвоює смугу", size=9.5, color=MUTED))

    # Panel 2: Active Star Topology
    p.append(rect(435, 50, 375, 230, fill="#fafbfc", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(622, 72, "2. Активна зірка (Active Star)", size=11.5, color=FIELD, bold=True))

    # Central Active Star Coupler
    p.append(rect(582, 130, 80, 50, fill="#eef6ef", stroke=FIELD, sw=2, rx=6))
    p.append(text(622, 150, "Active Star", size=10.5, color=FIELD, bold=True))
    p.append(text(622, 166, "Компенсатор", size=9, color=MUTED))

    # Star Nodes
    star_nodes = [
        ("ECU 1", 475, 95),
        ("ECU 2", 770, 95),
        ("ECU 3", 475, 220),
        ("ECU 4", 770, 220),
    ]
    for name, sx, sy in star_nodes:
        p.append(rect(sx - 30, sy - 20, 60, 40, fill="#ffffff", stroke=INK, sw=1.2, rx=4))
        p.append(text(sx, sy + 4, name, size=10, color=INK, bold=True))
        # Connection to Active Star
        p.append(line(sx, sy, 622, 155, color=FIELD, sw=1.4))

    p.append(text(622, 255, "Ізолює несправні гілки та усуває відбиття сигналу", size=9.5, color=MUTED))

    # Bottom Summary
    box, _, _ = textbox(420, 330,
                        "FlexRay підтримує комбіновані (гібридні) топології. Активна зірка посилює дифсигнал та запобігає відмовам всієї шини при обриві кабелю.",
                        size=11, bold=True, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=760)
    p.append(box)

    render(os.path.join(OUT, "flexray-bus-topologies.svg"), W, H, *p,
           title="Топології мережі FlexRay: Двоканальна Шина та Активна Зірка")


# ── 4. Clock Synchronization ────────────────────────────────────────────────
def fig_clock_sync():
    W, H = 840, 370
    p = []

    # Two Time Hierarchies: Microtick & Macrotick
    p.append(rect(40, 50, 760, 90, fill="#fafbfc", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(420, 70, "Двоуровнева часова ієрархія вузла", size=11, color=INK, bold=True))

    # Microtick bar
    p.append(rect(60, 85, 330, 40, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    p.append(text(225, 102, "Мікротакт (Microtick / µt)", size=10.5, color=NEG, bold=True))
    p.append(text(225, 116, "Прив'язаний до локального кварцу (напр. 12.5 або 25 нс)", size=9, color=MUTED))

    p.append(arrow(400, 105, 430, 105, color=INK, sw=1.5))

    # Macrotick bar
    p.append(rect(440, 85, 340, 40, fill="#eef6ef", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(610, 102, "Макротакт (Macrotick / MT)", size=10.5, color=FIELD, bold=True))
    p.append(text(610, 116, "Глобальна синхронізована одиниця часу мережі (напр. 1.0 мкс)", size=9, color=MUTED))

    # Correction Process Diagram
    p.append(rect(40, 155, 760, 135, fill="#ffffff", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(420, 175, "Процес вимірювання та коригування в кожному циклі", size=11, color=INK, bold=True))

    steps = [
        ("1. Вимірювання часу", "Зчитування часу приходу Sync-кадрів від Sync-вузлів у статичному сегменті.", "#eaf0fd", NEG, 60),
        ("2. FTM Алгоритм", "Обчислення відхилень фази (Offset) та частоти (Rate) за допомогою FTM.", "#fff3cd", "#856404", 310),
        ("3. Коригування в NIT", "Зміна кількості мікротактів у макротакті та зсув початку циклу в NIT.", "#eef6ef", FIELD, 560),
    ]

    for title, desc, bg_col, border_col, sx in steps:
        p.append(rect(sx, 190, 220, 85, fill=bg_col, stroke=border_col, sw=1.4, rx=4))
        p.append(text(sx + 110, 210, title, size=10.5, color=border_col, bold=True))
        # Text wrapping manually
        words = desc.split(" ")
        line1 = " ".join(words[:len(words)//2])
        line2 = " ".join(words[len(words)//2:])
        p.append(text(sx + 110, 235, line1, size=9, color=INK))
        p.append(text(sx + 110, 252, line2, size=9, color=INK))

    p.append(arrow(285, 232, 305, 232, color=INK, sw=1.5))
    p.append(arrow(535, 232, 555, 232, color=INK, sw=1.5))

    # Bottom Summary
    box, _, _ = textbox(420, 325,
                        "FlexRay не має єдиного Master-годинника. Синхронізація є розподіленою: щонайменше 2 Sync-вузли забезпечують стійкість до відмов окремих кварців.",
                        size=11, bold=True, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=760)
    p.append(box)

    render(os.path.join(OUT, "flexray-clock-sync.svg"), W, H, *p,
           title="Алгоритм розподіленої синхронізації годинників у FlexRay")


if __name__ == "__main__":
    fig_communication_cycle()
    fig_frame_structure()
    fig_bus_topologies()
    fig_clock_sync()
    print("FlexRay SVG figures generated successfully.")
