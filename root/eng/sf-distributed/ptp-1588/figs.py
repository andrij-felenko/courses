# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Чотириетапний обмін повідомленнями E2E (Delay Request-Response) ──
def fig_delay_req_resp():
    W, H = 840, 480
    parts = []
    parts.append(text(W/2, 28, "Чотириетапний обмін E2E: вимірювання зміщення та затримки лінії", size=16, bold=True))

    m_x = 220
    s_x = 620
    y_start = 70
    y_end = 430

    # Вертикальні часові осі
    parts.append(line(m_x, y_start, m_x, y_end, color=INK, sw=2))
    parts.append(line(s_x, y_start, s_x, y_end, color=INK, sw=2))

    # Заголовки стовпців
    bm, _, _ = textbox(m_x, y_start - 18, "Master (Головний годинник)", size=13.5,
                       fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    parts.append(bm)
    bs, _, _ = textbox(s_x, y_start - 18, "Slave (Підпорядкований)", size=13.5,
                       fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(bs)

    # Повідомлення 1: Sync
    t1_y = 100
    t2_y = 150
    parts.append(arrow(m_x, t1_y, s_x, t2_y, color=NEG, sw=2))
    parts.append(circle(m_x, t1_y, 4.5, fill=BG, stroke=NEG, sw=2))
    parts.append(circle(s_x, t2_y, 4.5, fill=BG, stroke=NEG, sw=2))
    parts.append(text(m_x - 12, t1_y + 4, "t1 (відправлено Sync)", size=12, color=NEG, anchor="end", bold=True))
    parts.append(text(s_x + 12, t2_y + 4, "t2 (отримано Sync)", size=12, color=NEG, anchor="start", bold=True))
    parts.append(text((m_x + s_x)/2, (t1_y + t2_y)/2 - 10, "1. Повідомлення Sync", size=12.5, color=NEG, bold=True))

    # Повідомлення 2: Follow_Up (Two-Step)
    fu_y1 = 175
    fu_y2 = 215
    parts.append(arrow(m_x, fu_y1, s_x, fu_y2, color=MUTED, sw=1.5))
    parts.append(text((m_x + s_x)/2, (fu_y1 + fu_y2)/2 - 8, "2. Follow_Up (передає точне значення t1)", size=12, color=MUTED, italic=True))

    # Повідомлення 3: Delay_Req
    t3_y = 260
    t4_y = 310
    parts.append(arrow(s_x, t3_y, m_x, t4_y, color=POS, sw=2))
    parts.append(circle(s_x, t3_y, 4.5, fill=BG, stroke=POS, sw=2))
    parts.append(circle(m_x, t4_y, 4.5, fill=BG, stroke=POS, sw=2))
    parts.append(text(s_x + 12, t3_y + 4, "t3 (відправлено Delay_Req)", size=12, color=POS, anchor="start", bold=True))
    parts.append(text(m_x - 12, t4_y + 4, "t4 (отримано Delay_Req)", size=12, color=POS, anchor="end", bold=True))
    parts.append(text((m_x + s_x)/2, (t3_y + t4_y)/2 - 10, "3. Повідомлення Delay_Req", size=12.5, color=POS, bold=True))

    # Повідомлення 4: Delay_Resp
    dr_y1 = 335
    dr_y2 = 375
    parts.append(arrow(m_x, dr_y1, s_x, dr_y2, color=MUTED, sw=1.5))
    parts.append(text((m_x + s_x)/2, (dr_y1 + dr_y2)/2 - 8, "4. Delay_Resp (передає точне значення t4)", size=12, color=MUTED, italic=True))

    # Формули внизу
    calc_str = (
        "Затримка лінії:   MeanPathDelay = ((t2 - t1) + (t4 - t3)) / 2\n"
        "Зміщення годинника:   Offset = ((t2 - t1) - (t4 - t3)) / 2 = (t2 - t1) - MeanPathDelay"
    )
    b_calc, _, _ = textbox(W/2, 435, calc_str, size=12.5, fill="#f8fafc", stroke=LINE, color=INK, bold=True, pad=10)
    parts.append(b_calc)

    render(os.path.join(IMG, "delay-req-resp.svg"), W, H, *parts)


# ── Фігура 2: Механізм Peer Delay (P2P) ──────────────────────────────────────
def fig_peer_delay():
    W, H = 840, 440
    parts = []
    parts.append(text(W/2, 28, "Механізм Peer Delay (P2P): вимірювання затримки сусіднього лінка", size=16, bold=True))

    p1_x = 220
    p2_x = 620
    y_start = 70
    y_end = 370

    parts.append(line(p1_x, y_start, p1_x, y_end, color=INK, sw=2))
    parts.append(line(p2_x, y_start, p2_x, y_end, color=INK, sw=2))

    bp1, _, _ = textbox(p1_x, y_start - 18, "Порт-ініціатор (Requester)", size=13.5,
                        fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(bp1)
    bp2, _, _ = textbox(p2_x, y_start - 18, "Сусідній порт (Responder)", size=13.5,
                        fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    parts.append(bp2)

    # 1. Pdelay_Req
    t1_y = 105
    t2_y = 155
    parts.append(arrow(p1_x, t1_y, p2_x, t2_y, color=POS, sw=2))
    parts.append(circle(p1_x, t1_y, 4.5, fill=BG, stroke=POS, sw=2))
    parts.append(circle(p2_x, t2_y, 4.5, fill=BG, stroke=POS, sw=2))
    parts.append(text(p1_x - 12, t1_y + 4, "t1 (вихід Pdelay_Req)", size=12, color=POS, anchor="end", bold=True))
    parts.append(text(p2_x + 12, t2_y + 4, "t2 (вхід Pdelay_Req)", size=12, color=POS, anchor="start", bold=True))
    parts.append(text((p1_x + p2_x)/2, (t1_y + t2_y)/2 - 10, "1. Pdelay_Req", size=12.5, color=POS, bold=True))

    # 2. Pdelay_Resp
    t3_y = 205
    t4_y = 255
    parts.append(arrow(p2_x, t3_y, p1_x, t4_y, color=NEG, sw=2))
    parts.append(circle(p2_x, t3_y, 4.5, fill=BG, stroke=NEG, sw=2))
    parts.append(circle(p1_x, t4_y, 4.5, fill=BG, stroke=NEG, sw=2))
    parts.append(text(p2_x + 12, t3_y + 4, "t3 (вихід Pdelay_Resp)", size=12, color=NEG, anchor="start", bold=True))
    parts.append(text(p1_x - 12, t4_y + 4, "t4 (вхід Pdelay_Resp)", size=12, color=NEG, anchor="end", bold=True))
    parts.append(text((p1_x + p2_x)/2, (t3_y + t4_y)/2 - 10, "2. Pdelay_Resp (несе мітку t2 або зсув)", size=12.5, color=NEG, bold=True))

    # 3. Pdelay_Resp_Follow_Up
    fu_y1 = 280
    fu_y2 = 320
    parts.append(arrow(p2_x, fu_y1, p1_x, fu_y2, color=MUTED, sw=1.5))
    parts.append(text((p1_x + p2_x)/2, (fu_y1 + fu_y2)/2 - 8, "3. Pdelay_Resp_Follow_Up (несе точну мітку t3)", size=12, color=MUTED, italic=True))

    calc_p2p = (
        "Затримка одного фізичного лінка:   PeerMeanPathDelay = ((t4 - t1) - (t3 - t2)) / 2\n"
        "Вимірюється локально між кожною парою сусідів, незалежно від наявності Grandmaster"
    )
    b_calc_p2p, _, _ = textbox(W/2, 395, calc_p2p, size=12.5, fill="#f8fafc", stroke=LINE, color=INK, bold=True, pad=9)
    parts.append(b_calc_p2p)

    render(os.path.join(IMG, "peer-delay.svg"), W, H, *parts)


# ── Фігура 3: Ієрархія та типи годинників у мережі PTP ───────────────────────
def fig_clock_hierarchy():
    W, H = 840, 480
    parts = []
    parts.append(text(W/2, 26, "Топологія та типи годинників PTP: GMC, BC, TC та Ordinary Clocks", size=16, bold=True))

    # Рівень 1: Grandmaster Clock
    gmc_box, _, _ = textbox(W/2, 75, "Grandmaster Clock (GMC)\nПервинний еталон часу (GNSS / Атомний годинник Cesium / Rubidium)",
                            size=13, fill="#fef3c7", stroke="#d97706", color="#92400e", bold=True, pad=8)
    parts.append(gmc_box)

    # Рівень 2: Boundary Clock та Transparent Clock
    # Boundary Clock (ліворуч)
    bc_x = 230
    bc_y = 210
    bc_box, _, _ = textbox(bc_x, bc_y,
                           "Boundary Clock (BC)\n"
                           "• Один Slave-порт синхронізується з GMC\n"
                           "• Власний генератор підлаштовується\n"
                           "• Master-порти роздають час далі\n"
                           "• Розвантажує GMC, створює новий домен",
                           size=11.5, fill="#eaf0fd", stroke=NEG, color=INK, pad=8)
    parts.append(bc_box)

    # Transparent Clock (праворуч)
    tc_x = 610
    tc_y = 210
    tc_box, _, _ = textbox(tc_x, tc_y,
                           "Transparent Clock (TC)\n"
                           "• Не має власної ролі Master/Slave\n"
                           "• Вимірює час перебування пакету (Residence Time)\n"
                           "• Додає затримку комутатора в correctionField\n"
                           "• Усуває джитер черг пакетного комутатора",
                           size=11.5, fill="#ecfdf5", stroke=FIELD, color=INK, pad=8)
    parts.append(tc_box)

    # З'єднання GMC -> BC та GMC -> TC
    parts.append(arrow(W/2 - 90, 105, bc_x, 150, color=LINE, sw=1.8))
    parts.append(text(W/2 - 140, 122, "Sync / Follow_Up", size=11, color=MUTED))

    parts.append(arrow(W/2 + 90, 105, tc_x, 150, color=LINE, sw=1.8))
    parts.append(text(W/2 + 140, 122, "Sync + correctionField", size=11, color=MUTED))

    # Рівень 3: Кінцеві вузли (Ordinary Clocks / Slaves)
    oc1_x, oc1_y = 120, 390
    oc2_x, oc2_y = 340, 390
    oc3_x, oc3_y = 510, 390
    oc4_x, oc4_y = 720, 390

    for x, lbl in [(oc1_x, "Slave Node 1\n(Industrial Drive)"),
                   (oc2_x, "Slave Node 2\n(Sensor Gateway)"),
                   (oc3_x, "Slave Node 3\n(5G Radio Unit)"),
                   (oc4_x, "Slave Node 4\n(Power Substation IED)")]:
        b, _, _ = textbox(x, oc3_y, "Ordinary Clock (OC)\n" + lbl, size=11, fill="#fdecea", stroke=POS, color=POS, bold=True, pad=6)
        parts.append(b)

    # З'єднання BC -> OC1, OC2
    parts.append(arrow(bc_x - 30, 270, oc1_x, 355, color=LINE, sw=1.5))
    parts.append(arrow(bc_x + 30, 270, oc2_x, 355, color=LINE, sw=1.5))

    # З'єднання TC -> OC3, OC4
    parts.append(arrow(tc_x - 30, 270, oc3_x, 355, color=LINE, sw=1.5))
    parts.append(arrow(tc_x + 30, 270, oc4_x, 355, color=LINE, sw=1.5))

    render(os.path.join(IMG, "clock-hierarchy.svg"), W, H, *parts)


# ── Фігура 4: Точки захоплення міток: софтові vs апаратні PHY/MAC ────────────
def fig_timestamping_layers():
    W, H = 840, 430
    parts = []
    parts.append(text(W/2, 26, "Точки фіксації міток часу в мережевому стеку: джерела похибок", size=16, bold=True))

    layers = [
        ("1. Програмний рівень застосунку (User Space)", "gettimeofday() / clock_gettime()", "Джитер: 10 мкс – 10 мс\n(перемикання контексту, планувальник ОС)", "#fee2e2", POS),
        ("2. Рівень ядра ОС (Kernel Socket Buffer)", "SO_TIMESTAMP (обробник мережевих пакетів ядра)", "Джитер: 1 – 100 мкс\n(обробка переривань, софт-IRQ, блокування)", "#fed7aa", "#c2410c"),
        ("3. Контролер Ethernet MAC (Network Adapter)", "Апаратний лічильник MAC під час старту кадру", "Джитер: 10 – 50 нс\n(затримка DMA-буфера та буфера дескрипторів)", "#fef08a", "#854d0e"),
        ("4. Фізичний трансивер Ethernet PHY (MII / GMII)", "Апаратне захоплення на делімітері початку кадру (SFD)", "Джитер: < 5 нс (субнаносекундна точність)\n(виключає всі затримки черг, DMA та софту)", "#dcfce7", FIELD),
    ]

    y_top = 65
    h_box = 72
    gap = 14

    for i, (title_text, sub_text, jitter_text, fill_c, stroke_c) in enumerate(layers):
        y = y_top + i * (h_box + gap)
        # ліва колонка: рівень стеку
        parts.append(rect(60, y, 440, h_box, fill=fill_c, stroke=stroke_c, sw=1.8, rx=6))
        parts.append(text(80, y + 26, title_text, size=13, color=INK, anchor="start", bold=True))
        parts.append(text(80, y + 50, sub_text, size=11.5, color=MUTED, anchor="start", italic=True))

        # права колонка: похибка
        parts.append(rect(520, y, 260, h_box, fill="#ffffff", stroke=stroke_c, sw=1.5, rx=6))
        lines = jitter_text.split("\n")
        parts.append(text(650, y + 26, lines[0], size=12.5, color=stroke_c, bold=True))
        parts.append(text(650, y + 50, lines[1], size=11, color=MUTED))

        # стрілка передачі пакету вниз
        if i < len(layers) - 1:
            parts.append(arrow(280, y + h_box, 280, y + h_box + gap, color=LINE, sw=1.5))

    render(os.path.join(IMG, "timestamping-layers.svg"), W, H, *parts)


# ── Фігура 5: Вектор пріоритетів алгоритму BMCA ──────────────────────────────
def fig_bmca_decision_tree():
    W, H = 840, 420
    parts = []
    parts.append(text(W/2, 26, "Алгоритм BMCA: послідовне порівняння якості джерел часу", size=16, bold=True))

    steps = [
        ("1. Priority 1", "Адміністративний пріоритет (0–255), ручне перевизначення вибору", "#eaf0fd", NEG),
        ("2. Clock Class", "Рівень простежуваності (Atomic/GNSS=6, Holdover=7, Free-running=248)", "#eaf0fd", NEG),
        ("3. Clock Accuracy", "Заявлена точність шкали часу (наприклад, <25 нс, <100 нс, <1 мкс)", "#eaf0fd", NEG),
        ("4. Offset Scaled Log Variance", "Стабільність / дисперсія Аллана внутрішнього генератора", "#eaf0fd", NEG),
        ("5. Priority 2", "Другорядний адміністративний пріоритет (тонке балансування)", "#eaf0fd", NEG),
        ("6. Clock Identity", "Унікальний 64-бітний ідентифікатор EUI-64 (розв'язання нічиєї)", "#f3e8ff", "#7e22ce"),
        ("7. Steps Removed", "Кількість мережевих переходів (BC) від GMC до поточного порту", "#ecfdf5", FIELD),
    ]

    col1_w = 340
    box_h = 36
    y_start = 65
    y_step = 46

    for i, (name, desc, f_col, s_col) in enumerate(steps):
        y = y_start + i * y_step
        # Лівий блок — критерій
        parts.append(rect(50, y, col1_w, box_h, fill=f_col, stroke=s_col, sw=1.5, rx=5))
        parts.append(text(65, y + 23, name, size=12.5, color=s_col, anchor="start", bold=True))

        # Стрілка "якщо рівні -> далі"
        parts.append(arrow(50 + col1_w, y + box_h/2, 50 + col1_w + 30, y + box_h/2, color=MUTED, sw=1.5))

        # Правий блок — пояснення
        parts.append(rect(50 + col1_w + 30, y, 370, box_h, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
        parts.append(text(50 + col1_w + 45, y + 23, desc, size=11.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "bmca-decision-tree.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_delay_req_resp()
    fig_peer_delay()
    fig_clock_hierarchy()
    fig_timestamping_layers()
    fig_bmca_decision_tree()
    print("All figures generated successfully.")
