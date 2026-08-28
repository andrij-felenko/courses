# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# ── 1. Канонічний 4-етапний конвеєр Bringup плати ─────────────────────────────
def fig_bringup_pipeline():
    W, H = 960, 570
    f = []

    # Заголовок фігури
    f.append(text(W / 2, 25, "Канонічний 4-етапний конвеєр оживлення плати (Bringup)", size=16, bold=True))

    # 4 колонки етапів
    stages = [
        {
            "num": "1",
            "title": "Шини живлення & POR",
            "color": POS,
            "bg": "#fef2f2",
            "border": "#fca5a5",
            "items": [
                "• LDO / Buck плавний пуск (Soft-start)",
                "• Монотонне наростання напруги dV/dt",
                "• Секвенсування: VCORE → VDD → VDDA",
                "• Спрацьовування Power-On Reset (POR)",
                "• Відсутність просідань та Brownout"
            ]
        },
        {
            "num": "2",
            "title": "Лінія скидання nRST",
            "color": "#d97706",
            "bg": "#fffbeb",
            "border": "#fcd34d",
            "items": [
                "• Затримка RC-ланцюга: 10–100 кОм + 100 нФ",
                "• nRST утримується в '0' під час підйому VDD",
                "• Відпускання в '1' після стабілізації",
                "• Фільтрація імпульсних завад (Glitch filter)",
                "• Робота зовнішнього супервізора / WDT"
            ]
        },
        {
            "num": "3",
            "title": "Тактове дерево & PLL",
            "color": "#2563eb",
            "bg": "#eff6ff",
            "border": "#93c5fd",
            "items": [
                "• Запуск внутрішнього RC-генератора HSI",
                "• Розгойдування кварцу HSE (Pierce OSC)",
                "• Баланс ємностей C_L та запас посилення gm",
                "• Захоплення частоти PLL (PLL Lock)",
                "• Активація захисту такту (CSS Failover)"
            ]
        },
        {
            "num": "4",
            "title": "SWD / JTAG Детект",
            "color": FIELD,
            "bg": "#f0fdf4",
            "border": "#86efac",
            "items": [
                "• Line Reset (≥ 50 тактів SWCLK при SWDIO=1)",
                "• Перемикання JTAG→SWD (послідовність 0x79E7)",
                "• Читання регістру DP-IDCODE через SWD",
                "• Активація живлення налагодження (CTRL/STAT)",
                "• Зупинка ядра (Core Halt) та доступ до пам'яті"
            ]
        }
    ]

    col_w = 215
    col_gap = 16
    start_x = 24
    top_y = 52
    card_h = 240

    for idx, st in enumerate(stages):
        cx = start_x + idx * (col_w + col_gap)
        # Рамка картки
        f.append(rect(cx, top_y, col_w, card_h, fill=st["bg"], stroke=st["border"], sw=1.5, rx=6))
        
        # Значок номера
        f.append(circle(cx + 22, top_y + 24, 13, fill=st["color"], stroke=st["color"], sw=1))
        f.append(text(cx + 22, top_y + 29, st["num"], size=12, color="#ffffff", bold=True))
        
        # Назва етапу
        f.append(text(cx + 42, top_y + 28, st["title"], size=11.5, color=INK, bold=True, anchor="start"))
        
        # Розділова лінія
        f.append(line(cx + 10, top_y + 46, cx + col_w - 10, top_y + 46, color=st["border"], sw=1))
        
        # Пункти вимог
        for i_idx, itm in enumerate(st["items"]):
            py = top_y + 68 + i_idx * 33
            f.append(text(cx + 10, py, itm, size=9.5, color=LINE, anchor="start"))

        # З'єднувальна стрілка між картками
        if idx < len(stages) - 1:
            arrow_x1 = cx + col_w + 2
            arrow_x2 = arrow_x1 + col_gap - 4
            arrow_y = top_y + card_h / 2
            f.append(arrow(arrow_x1, arrow_y, arrow_x2, arrow_y, color="#94a3b8", sw=2))

    # ── Нижня часова діаграма взаємодії сигналів ──────────────────────────────
    diag_y = top_y + card_h + 24
    diag_h = 225
    f.append(rect(start_x, diag_y, W - 2 * start_x, diag_h, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(start_x + 16, diag_y + 22, "Часова послідовність проходження фаз Bringup на живій платі:", size=12, bold=True, anchor="start"))

    # Осі сигналів
    sig_labels = [
        ("VDD (3.3V)", POS),
        ("POR / BOR", "#dc2626"),
        ("nRST лінія", "#d97706"),
        ("HSE Кварц", "#2563eb"),
        ("PLL Lock", "#0284c7"),
        ("SWD ACK", FIELD)
    ]

    t_start = start_x + 130
    t_end = start_x + W - 2 * start_x - 30
    t_w = t_end - t_start

    # Вертикальні пунктирні межі етапів
    t_stages = [
        (t_start + t_w * 0.22, "t1: VDD OK / POR", POS),
        (t_start + t_w * 0.44, "t2: nRST High", "#d97706"),
        (t_start + t_w * 0.72, "t3: PLL Locked", "#2563eb"),
        (t_start + t_w * 0.95, "t4: Target Halt", FIELD)
    ]

    for tx, tlab, tcol in t_stages:
        f.append(line(tx, diag_y + 36, tx, diag_y + diag_h - 10, color="#e2e8f0", sw=1.5, dash="4,4"))
        f.append(text(tx, diag_y + diag_h - 14, tlab, size=9.5, color=tcol, bold=True))

    sig_sy = diag_y + 50
    sig_row_h = 26

    for s_idx, (s_name, s_col) in enumerate(sig_labels):
        sy = sig_sy + s_idx * sig_row_h
        f.append(text(start_x + 16, sy + 4, s_name, size=10, color=s_col, bold=True, anchor="start"))
        f.append(line(t_start, sy, t_end, sy, color="#f1f5f9", sw=1))

    # Хвильові форми
    # 1. VDD: підйом від 0 до t1
    y1 = sig_sy
    f.append(line(t_start, y1 + 8, t_start + t_w * 0.18, y1 - 8, color=POS, sw=2))
    f.append(line(t_start + t_w * 0.18, y1 - 8, t_end, y1 - 8, color=POS, sw=2))

    # 2. POR: активний низький до перетину порогу, потім скидається у високий
    y2 = sig_sy + sig_row_h
    f.append(line(t_start, y2 + 8, t_start + t_w * 0.22, y2 + 8, color="#dc2626", sw=2))
    f.append(line(t_start + t_w * 0.22, y2 + 8, t_start + t_w * 0.22, y2 - 8, color="#dc2626", sw=2))
    f.append(line(t_start + t_w * 0.22, y2 - 8, t_end, y2 - 8, color="#dc2626", sw=2))

    # 3. nRST: зарядка RC, стрибок у '1' на t2
    y3 = sig_sy + 2 * sig_row_h
    f.append(line(t_start, y3 + 8, t_start + t_w * 0.44, y3 + 8, color="#d97706", sw=2))
    f.append(line(t_start + t_w * 0.44, y3 + 8, t_start + t_w * 0.44, y3 - 8, color="#d97706", sw=2))
    f.append(line(t_start + t_w * 0.44, y3 - 8, t_end, y3 - 8, color="#d97706", sw=2))

    # 4. HSE Кварц: тиша до nRST, розгойдування синусоїди, стабільна амплітуда
    y4 = sig_sy + 3 * sig_row_h
    f.append(line(t_start, y4, t_start + t_w * 0.46, y4, color="#94a3b8", sw=1.5))
    # Зростаюча синусоїда
    sin_x0 = t_start + t_w * 0.46
    sin_x1 = t_start + t_w * 0.65
    pts = []
    import math
    for step in range(60):
        px = sin_x0 + (sin_x1 - sin_x0) * (step / 59.0)
        amp = 2 + 6 * (step / 59.0)
        py = y4 + amp * math.sin(step * 0.8)
        pts.append((px, py))
    for p_idx in range(len(pts) - 1):
        f.append(line(pts[p_idx][0], pts[p_idx][1], pts[p_idx + 1][0], pts[p_idx + 1][1], color="#2563eb", sw=1.5))
    # Стабільна генерація
    pts2 = []
    for step in range(80):
        px = sin_x1 + (t_end - sin_x1) * (step / 79.0)
        py = y4 + 7 * math.sin((step + 60) * 0.8)
        pts2.append((px, py))
    for p_idx in range(len(pts2) - 1):
        f.append(line(pts2[p_idx][0], pts2[p_idx][1], pts2[p_idx + 1][0], pts2[p_idx + 1][1], color="#2563eb", sw=1.5))

    # 5. PLL Lock: низький до захоплення на t3
    y5 = sig_sy + 4 * sig_row_h
    f.append(line(t_start, y5 + 8, t_start + t_w * 0.72, y5 + 8, color="#0284c7", sw=2))
    f.append(line(t_start + t_w * 0.72, y5 + 8, t_start + t_w * 0.72, y5 - 8, color="#0284c7", sw=2))
    f.append(line(t_start + t_w * 0.72, y5 - 8, t_end, y5 - 8, color="#0284c7", sw=2))

    # 6. SWD ACK: детектування та передача пакетів на t4
    y6 = sig_sy + 5 * sig_row_h
    f.append(line(t_start, y6, t_start + t_w * 0.78, y6, color="#94a3b8", sw=1.5))
    # Пакети активності SWD
    f.append(rect(t_start + t_w * 0.79, y6 - 8, t_w * 0.08, 16, fill="#bbf7d0", stroke=FIELD, sw=1.2, rx=2))
    f.append(text(t_start + t_w * 0.83, y6 + 3.5, "Reset", size=9, color=FIELD, bold=True))
    f.append(rect(t_start + t_w * 0.88, y6 - 8, t_w * 0.07, 16, fill="#bbf7d0", stroke=FIELD, sw=1.2, rx=2))
    f.append(text(t_start + t_w * 0.915, y6 + 3.5, "0x79E7", size=9, color=FIELD, bold=True))
    f.append(rect(t_start + t_w * 0.96, y6 - 8, t_w * 0.035, 16, fill="#86efac", stroke=FIELD, sw=1.5, rx=2))
    f.append(text(t_start + t_w * 0.977, y6 + 3.5, "ID", size=9, color="#14532d", bold=True))

    return render(os.path.join(IMG, "bringup-four-stage-pipeline.svg"), W, H, *f)


# ── 2. Часова діаграма транзакції рукостискання SWD ───────────────────────────
def fig_swd_handshake():
    W, H = 980, 550
    f = []

    # Заголовок
    f.append(text(W / 2, 25, "Анатомія налагоджувального протоколу SWD: послідовність читання DP-IDCODE", size=15, bold=True))

    # ── Блок 1: Послідовність ініціалізації шини (Host Line Reset & JTAG-to-SWD) ─
    top_box_y = 50
    top_box_h = 135
    f.append(rect(25, top_box_y, W - 50, top_box_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(40, top_box_y + 20, "Фаза 1: Скидання шини та перемикання з JTAG на SWD", size=12, bold=True, anchor="start"))

    # Візуалізація 3 блоків ініціалізації
    b1_w = 270
    b2_w = 290
    b3_w = 270
    b_y = top_box_y + 36
    b_h = 76

    # Блок 1.1: Line Reset
    f.append(rect(45, b_y, b1_w, b_h, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=4))
    f.append(text(45 + b1_w / 2, b_y + 18, "1. SWD Line Reset", size=11, bold=True, color="#1e40af"))
    f.append(text(45 + b1_w / 2, b_y + 36, "≥ 50 тактів SWCLK при SWDIO = '1'", size=9.5, color=LINE))
    f.append(text(45 + b1_w / 2, b_y + 54, "Гарантоване скидання автомату DP", size=9.5, color=MUTED, italic=True))

    # Стрілка 1
    f.append(arrow(45 + b1_w + 4, b_y + b_h / 2, 45 + b1_w + 24, b_y + b_h / 2, color="#94a3b8", sw=2))

    # Блок 1.2: JTAG-to-SWD Sequence
    b2_x = 45 + b1_w + 30
    f.append(rect(b2_x, b_y, b2_w, b_h, fill="#fefce8", stroke="#fde047", sw=1.5, rx=4))
    f.append(text(b2_x + b2_w / 2, b_y + 18, "2. JTAG-to-SWD Switch (16 біт)", size=11, bold=True, color="#854d0e"))
    f.append(text(b2_x + b2_w / 2, b_y + 36, "0x79E7 (MSB-first: 0111_1001_1110_0111)", size=9.5, color=LINE))
    f.append(text(b2_x + b2_w / 2, b_y + 54, "Перемикання внутрішнього селектора", size=9.5, color=MUTED, italic=True))

    # Стрілка 2
    f.append(arrow(b2_x + b2_w + 4, b_y + b_h / 2, b2_x + b2_w + 24, b_y + b_h / 2, color="#94a3b8", sw=2))

    # Блок 1.3: Line Reset 2 & Idle
    b3_x = b2_x + b2_w + 30
    f.append(rect(b3_x, b_y, b3_w, b_h, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=4))
    f.append(text(b3_x + b3_w / 2, b_y + 18, "3. Line Reset + Idle Cycles", size=11, bold=True, color="#1e40af"))
    f.append(text(b3_x + b3_w / 2, b_y + 36, "≥ 50 тактів '1' + ≥ 2 тактів '0' (Idle)", size=9.5, color=LINE))
    f.append(text(b3_x + b3_w / 2, b_y + 54, "Шина готова до першого пакету", size=9.5, color=MUTED, italic=True))

    # ── Блок 2: Детальна діаграма читання DP-IDCODE (46 тактів) ─────────────────
    p_box_y = top_box_y + top_box_h + 18
    p_box_h = 215
    f.append(rect(25, p_box_y, W - 50, p_box_h, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(40, p_box_y + 22, "Фаза 2: Транзакція читання регістру DP-IDCODE (SWD Packet Timing)", size=12, bold=True, anchor="start"))

    pkt_sy = p_box_y + 44
    
    sec_host_w = 265
    sec_trn1_w = 55
    sec_ack_w = 110
    sec_data_w = 375
    sec_trn2_w = 55
    
    sx = 45
    # Host Request
    f.append(rect(sx, pkt_sy, sec_host_w, 44, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=4))
    f.append(text(sx + sec_host_w / 2, pkt_sy + 18, "HOST REQUEST (8 біт)", size=10.5, bold=True, color="#1d4ed8"))
    f.append(text(sx + sec_host_w / 2, pkt_sy + 34, "Start=1 | DP=0 | R=1 | A=00 | P=1 | Stop=0 | Park=1", size=9, color=LINE))
    
    # Trn 1
    sx_trn1 = sx + sec_host_w + 6
    f.append(rect(sx_trn1, pkt_sy, sec_trn1_w, 44, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(sx_trn1 + sec_trn1_w / 2, pkt_sy + 18, "Trn", size=10, bold=True, color=MUTED))
    f.append(text(sx_trn1 + sec_trn1_w / 2, pkt_sy + 34, "1 T (Hi-Z)", size=9, color=MUTED))
    
    # Target ACK
    sx_ack = sx_trn1 + sec_trn1_w + 6
    f.append(rect(sx_ack, pkt_sy, sec_ack_w, 44, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(sx_ack + sec_ack_w / 2, pkt_sy + 18, "ACK (3 біти)", size=10.5, bold=True, color="#15803d"))
    f.append(text(sx_ack + sec_ack_w / 2, pkt_sy + 34, "OK = 100b (001)", size=9, color="#15803d", bold=True))
    
    # Data Phase
    sx_data = sx_ack + sec_ack_w + 6
    f.append(rect(sx_data, pkt_sy, sec_data_w, 44, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    f.append(text(sx_data + sec_data_w / 2, pkt_sy + 18, "READ DATA (32 біти) + PARITY (1 біт)", size=10.5, bold=True, color="#b45309"))
    f.append(text(sx_data + sec_data_w / 2, pkt_sy + 34, "IDCODE: 0x0BC11477 (Cortex-M0+) / 0x6BA02147 (M4)", size=9, color=LINE))
    
    # Trn 2
    sx_trn2 = sx_data + sec_data_w + 6
    f.append(rect(sx_trn2, pkt_sy, sec_trn2_w, 44, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(sx_trn2 + sec_trn2_w / 2, pkt_sy + 18, "Trn", size=10, bold=True, color=MUTED))
    f.append(text(sx_trn2 + sec_trn2_w / 2, pkt_sy + 34, "1 T (Hi-Z)", size=9, color=MUTED))

    # Хвильові осцилограми SWCLK та SWDIO
    osc_y = pkt_sy + 58
    f.append(text(45, osc_y + 16, "SWCLK:", size=10, color=LINE, bold=True, anchor="start"))
    f.append(text(45, osc_y + 46, "SWDIO:", size=10, color=LINE, bold=True, anchor="start"))

    # Сітка тактів SWCLK
    clk_sx = 115
    clk_ex = W - 55
    num_cycles = 28
    cyc_w = (clk_ex - clk_sx) / float(num_cycles)

    for c in range(num_cycles):
        cx0 = clk_sx + c * cyc_w
        cx_mid = cx0 + cyc_w / 2.0
        cx1 = cx0 + cyc_w
        # Тактовий імпульс
        f.append(line(cx0, osc_y + 22, cx_mid, osc_y + 22, color="#2563eb", sw=1.5))
        f.append(line(cx_mid, osc_y + 22, cx_mid, osc_y + 8, color="#2563eb", sw=1.5))
        f.append(line(cx_mid, osc_y + 8, cx1, osc_y + 8, color="#2563eb", sw=1.5))
        f.append(line(cx1, osc_y + 8, cx1, osc_y + 22, color="#2563eb", sw=1.5))

    # Лінія SWDIO з напрямками шини
    # Host drive:
    f.append(line(clk_sx, osc_y + 40, clk_sx + cyc_w * 8, osc_y + 40, color="#1d4ed8", sw=2.5))
    f.append(text(clk_sx + cyc_w * 4, osc_y + 56, "Керує Host (Master)", size=9, color="#1d4ed8", bold=True))

    # Trn 1 (Hi-Z)
    f.append(line(clk_sx + cyc_w * 8, osc_y + 40, clk_sx + cyc_w * 9.5, osc_y + 40, color="#94a3b8", sw=1.5, dash="3,3"))
    f.append(text(clk_sx + cyc_w * 8.75, osc_y + 56, "Hi-Z", size=9, color=MUTED))

    # Target drive (ACK + Data)
    f.append(line(clk_sx + cyc_w * 9.5, osc_y + 40, clk_sx + cyc_w * 25.5, osc_y + 40, color=FIELD, sw=2.5))
    f.append(text(clk_sx + cyc_w * 17.5, osc_y + 56, "Керує Target MCU (CoreSight DP)", size=9, color=FIELD, bold=True))

    # Trn 2 (Hi-Z)
    f.append(line(clk_sx + cyc_w * 25.5, osc_y + 40, clk_sx + cyc_w * 27, osc_y + 40, color="#94a3b8", sw=1.5, dash="3,3"))
    f.append(text(clk_sx + cyc_w * 26.25, osc_y + 56, "Hi-Z", size=9, color=MUTED))

    # Пояснення допуску фаз
    f.append(rect(45, osc_y + 68, W - 90, 26, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=3))
    f.append(text(55, osc_y + 84, "Таймінги шини: Setup Time t_su ≥ 4 нс, Hold Time t_h ≥ 4 нс відносно зростаючого фронту SWCLK. Частота: 100 кГц–10 МГц.", size=9.5, color=LINE, anchor="start"))

    # ── Блок 3: Типові апаратні пастки та діагностичний вердикт ─────────────────
    bot_y = p_box_y + p_box_h + 16
    bot_h = 105
    f.append(rect(25, bot_y, W - 50, bot_h, fill="#fff7ed", stroke="#fed7aa", sw=1.2, rx=6))
    f.append(text(40, bot_y + 20, "Діагностика типових несправностей Bringup на етапі SWD:", size=11.5, bold=True, color="#9a3412", anchor="start"))

    traps = [
        ("Немає відповіді (ACK Timeout / 0x00 / 0xFF):", "Перевірити напругу VDD, наявність підтяжки SWDIO до VDD (10–100 кОм), підтяжки SWCLK до GND (10–100 кОм)"),
        ("Помилка FAULT / WAIT у полі ACK:", "Ядро заблоковано в глибокому сні (WFI/WFE) або PLL не залочений → Використати режим Connect-Under-Reset"),
        ("Помилка Parity Error під час читання:", "Занадто довгий шлейф, паразитна ємність лінії (>30 пФ) або дзвін → Знизити тактову частоту адаптера до 500 кГц")
    ]

    for t_idx, (t_title, t_body) in enumerate(traps):
        ty = bot_y + 40 + t_idx * 21
        f.append(text(45, ty, "• " + t_title, size=9.5, bold=True, color="#9a3412", anchor="start"))
        f.append(text(340, ty, t_body, size=9.5, color=LINE, anchor="start"))

    return render(os.path.join(IMG, "swd-debug-handshake-timing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bringup_pipeline()
    fig_swd_handshake()
    print("Figures generated successfully.")
