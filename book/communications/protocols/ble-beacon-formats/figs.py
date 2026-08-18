# -*- coding: utf-8 -*-
"""Генератор фігур для теми ble-beacon-formats (Формати BLE-маячків: iBeacon, Eddystone та AltBeacon)."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. beacon-packet-comparison: побайтова структура маячків ───────────────────
def fig_beacon_packet_comparison():
    W, H = 820, 520
    p = []

    # Загальний контейнер Advertising Data (31 байт)
    hdr_b, _, _ = textbox(410, 48, "Структура корисного навантаження ADV_NONCONN_IND (максимум 31 байт Advertising Data)\nБудь-який маячок упаковується в послідовність структур AD (Length + AD Type + AD Data)",
                          size=11, pad=6, fill="#f8fafc", stroke=MUTED, sw=1.2, min_w=760)
    p.append(hdr_b)

    rows = [
        ("iBeacon (Apple, 30 байтів)", 125, [
            ("Flags (3B)\n02 01 06", 80, "#e2e8f0", MUTED),
            ("AD Hdr (2B)\n1A FF", 65, "#dbeafe", NEG),
            ("Company (2B)\n4C 00 (Apple)", 85, "#dbeafe", NEG),
            ("Type (2B)\n02 15", 60, "#ede9fe", "#7c3aed"),
            ("Proximity UUID (16 байтів)\n128-бітний ідентифікатор простору / мережі", 230, "#dcfce7", FIELD),
            ("Major (2B)\nБудівля", 65, "#fef3c7", "#d97706"),
            ("Minor (2B)\nТочка", 65, "#fef3c7", "#d97706"),
            ("TxPwr (1B)\n@1m", 50, "#fee2e2", POS),
        ]),
        ("Eddystone-UID (Google, 31 байт)", 210, [
            ("Flags (3B)\n02 01 06", 80, "#e2e8f0", MUTED),
            ("UUID List (4B)\n03 03 AA FE", 85, "#dbeafe", NEG),
            ("Service Data Hdr (4B)\n17 16 AA FE", 90, "#dbeafe", NEG),
            ("Frame (2B)\n00 + Tx@0m", 70, "#fee2e2", POS),
            ("Namespace ID (10 байтів)\nІдентифікатор домену / організації", 185, "#dcfce7", FIELD),
            ("Instance ID (6 байтів)\nІдентифікатор вузла", 125, "#fef3c7", "#d97706"),
            ("RFU (2B)\n00 00", 45, "#f1f5f9", MUTED),
        ]),
        ("Eddystone-URL (Google, до 31 байта)", 295, [
            ("Flags (3B)\n02 01 06", 80, "#e2e8f0", MUTED),
            ("UUID List (4B)\n03 03 AA FE", 85, "#dbeafe", NEG),
            ("Service Data Hdr (4B)\nLen 16 AA FE", 90, "#dbeafe", NEG),
            ("Frame (2B)\n10 + Tx@0m", 70, "#fee2e2", POS),
            ("Схема (1B)\nhttps://", 70, "#ede9fe", "#7c3aed"),
            ("Закодований URL (до 17 байтів)\nТекст + 1-байтні токени розширень (.com/, .org/, .ua/)", 285, "#dcfce7", FIELD),
        ]),
        ("Eddystone-TLM (Google, 25 байтів)", 380, [
            ("Flags (3B)\n02 01 06", 80, "#e2e8f0", MUTED),
            ("UUID List (4B)\n03 03 AA FE", 85, "#dbeafe", NEG),
            ("Service Data Hdr (4B)\n11 16 AA FE", 90, "#dbeafe", NEG),
            ("Type (2B)\n20 00", 60, "#ede9fe", "#7c3aed"),
            ("Vbatt (2B)\nмВ", 60, "#fef3c7", "#d97706"),
            ("Temp (2B)\n8.8 °C", 65, "#fef3c7", "#d97706"),
            ("ADV Count (4B)\nЛічильник пакетів", 120, "#e0f2fe", "#0284c7"),
            ("Uptime (4B)\nЧас роботи (0.1 с)", 120, "#e0f2fe", "#0284c7"),
        ]),
        ("AltBeacon (Radius Networks, 28 байтів)", 465, [
            ("Flags (3B)\n02 01 06", 80, "#e2e8f0", MUTED),
            ("AD Hdr (2B)\n1B FF", 65, "#dbeafe", NEG),
            ("Mfg ID (2B)\nКод виробника", 80, "#dbeafe", NEG),
            ("Code (2B)\nBE AC", 65, "#ede9fe", "#7c3aed"),
            ("Beacon ID (20 байтів)\n16B GUID + 2B Major + 2B Minor (або довільні 20B)", 255, "#dcfce7", FIELD),
            ("Ref RSSI (1B)\n@1m", 70, "#fee2e2", POS),
            ("RSV (1B)\n00", 45, "#f1f5f9", MUTED),
        ]),
    ]

    for title, y_top, cols in rows:
        p.append(text(40, y_top - 8, title, size=11, color=INK, bold=True, anchor="start"))
        cur_x = 40
        for label, w_col, fill_col, stroke_col in cols:
            p.append(fitbox(cur_x, y_top, w_col, 42, label, size=10, pad=3,
                            fill=fill_col, stroke=stroke_col, sw=1.2))
            cur_x += w_col + 2

    render(os.path.join(OUT, "beacon-packet-comparison.svg"), W, H, *p,
           title="Порівняння побайтової структури пакетів iBeacon, Eddystone та AltBeacon")


# ── 2. log-distance-path-loss: крива загасання RSSI ───────────────────────────
def fig_log_distance_path_loss():
    W, H = 780, 440
    p = []

    ox, oy = 90, 360
    gw, gh = 640, 270

    # Осі координат
    p.append(line(ox, oy, ox + gw + 15, oy, color=INK, sw=1.5))
    p.append(line(ox, oy, ox, oy - gh - 15, color=INK, sw=1.5))
    p.append(text(ox + gw + 10, oy + 25, "Відстань d (метри)", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(ox - 15, oy - gh - 8, "RSSI (дБм)", size=11, color=INK, bold=True, anchor="end"))

    # Сітка та мітки X (плавно від 0.2 до 12 м)
    d_ticks = [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 10.0, 12.0]
    for dt in d_ticks:
        tx = ox + (dt / 12.0) * gw
        p.append(line(tx, oy, tx, oy - gh, color="#e5e7eb", sw=1.0, dash="3,3"))
        p.append(line(tx, oy, tx, oy + 4, color=MUTED, sw=1.2))
        p.append(text(tx, oy + 18, "%.1f" % dt if dt < 1 else "%d" % int(dt), size=10, color=MUTED))

    # Сітка та мітки Y: RSSI від -30 до -95 дБм
    rssi_ticks = [-30, -40, -50, -60, -70, -80, -90]
    for rt in rssi_ticks:
        ty = oy - (rt - (-95)) / ((-30) - (-95)) * gh
        p.append(line(ox, ty, ox + gw, ty, color="#e5e7eb", sw=1.0, dash="3,3"))
        p.append(line(ox - 4, ty, ox, ty, color=MUTED, sw=1.2))
        p.append(text(ox - 8, ty + 4, "%d" % rt, size=10, color=MUTED, anchor="end"))

    def rssi_y(val):
        return oy - (val - (-95)) / ((-30) - (-95)) * gh

    def dist_x(d):
        return ox + (d / 12.0) * gw

    # Криві для різних показників загасання n при TxPower@1m = -59 дБм
    curves = [
        (2.0, "n = 2.0 (вільний простір / ідеальні умови)", FIELD),
        (2.7, "n = 2.7 (офісне приміщення, пряма видимість)", "#2563eb"),
        (3.8, "n = 3.8 (стіни, металеві шафи, перешкоди)", POS),
    ]

    for n_val, label, col in curves:
        pts = []
        d = 0.3
        while d <= 12.0:
            rssi = -59.0 - 10.0 * n_val * math.log10(d)
            if -95 <= rssi <= -30:
                pts.append((dist_x(d), rssi_y(rssi)))
            d += 0.15

        for i in range(len(pts) - 1):
            p.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=col, sw=2.2))

    # Точка калібрування 1 метр (iBeacon TxPower = -59 dBm)
    x1m = dist_x(1.0)
    y1m = rssi_y(-59.0)
    p.append(circle(x1m, y1m, 5, fill="#fee2e2", stroke=POS, sw=2))
    p.append(text(x1m + 12, y1m - 12, "Калібрована точка Measured Power @ 1m (-59 дБм)", size=10, color=POS, bold=True, anchor="start"))
    p.append(line(x1m, y1m, x1m, oy, color=POS, sw=1.2, dash="4,3"))

    # Зона 1: висока чутливість біля 1м
    p.append(rect(dist_x(0.3), rssi_y(-35), dist_x(2.0) - dist_x(0.3), 50, fill="#f0fdf4", stroke=FIELD, sw=1.0, rx=4))
    p.append(text((dist_x(0.3) + dist_x(2.0))/2, rssi_y(-35) + 18, "Крута зона (0.3..2 м):", size=10, color=FIELD, bold=True))
    p.append(text((dist_x(0.3) + dist_x(2.0))/2, rssi_y(-35) + 34, "Δ 6 дБм відповідає зміні на ~0.5 м", size=9, color=FIELD))

    # Зона 2: низька чутливість на відстані
    p.append(rect(dist_x(6.0), rssi_y(-45), dist_x(11.8) - dist_x(6.0), 50, fill="#fff1f2", stroke=POS, sw=1.0, rx=4))
    p.append(text((dist_x(6.0) + dist_x(11.8))/2, rssi_y(-45) + 18, "Полога зона (6..12 м):", size=10, color=POS, bold=True))
    p.append(text((dist_x(6.0) + dist_x(11.8))/2, rssi_y(-45) + 34, "Ті самі Δ 6 дБм дають похибку у 4..6 м!", size=9, color=POS))

    # Легенда
    leg_x = 420
    leg_y = 300
    p.append(rect(leg_x, leg_y, 310, 65, fill="#ffffff", stroke=MUTED, sw=1.0, rx=6))
    for i, (n_val, label, col) in enumerate(curves):
        ly = leg_y + 16 + i * 18
        p.append(line(leg_x + 10, ly, leg_x + 35, ly, color=col, sw=2.5))
        p.append(text(leg_x + 42, ly + 4, label, size=9, color=INK, anchor="start"))

    render(os.path.join(OUT, "log-distance-path-loss.svg"), W, H, *p,
           title="Модель загасання радіосигналу Log-Distance Path Loss та вплив перешкод")


# ── 3. channel-fading-rssi: частотно-селективне завмирання на 3 каналах ────────
def fig_channel_fading_rssi():
    W, H = 780, 400
    p = []

    ox, oy = 80, 330
    gw, gh = 660, 240

    # Осі
    p.append(line(ox, oy, ox + gw + 10, oy, color=INK, sw=1.5))
    p.append(line(ox, oy, ox, oy - gh - 15, color=INK, sw=1.5))
    p.append(text(ox + gw + 5, oy + 25, "Номер рекламного пакета (час)", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(ox - 10, oy - gh - 8, "RSSI (дБм)", size=11, color=INK, bold=True, anchor="end"))

    # Сітка Y (-55 .. -85 dBm)
    for rt in [-55, -60, -65, -70, -75, -80, -85]:
        ty = oy - (rt - (-85)) / ((-55) - (-85)) * gh
        p.append(line(ox, ty, ox + gw, ty, color="#f1f5f9", sw=1.0, dash="3,3"))
        p.append(line(ox - 4, ty, ox, ty, color=MUTED, sw=1.2))
        p.append(text(ox - 8, ty + 4, "%d" % rt, size=10, color=MUTED, anchor="end"))

    def ry(val):
        return oy - (val - (-85)) / ((-55) - (-85)) * gh

    import random
    rng = random.Random(42)

    ch_data = [
        (37, "Канал 37 (2402 МГц): середня потужність -62 дБм", "#2563eb", -62.0),
        (38, "Канал 38 (2426 МГц): деструктивне завмирання -75 дБм", POS, -75.0),
        (39, "Канал 39 (2480 МГц): проміжне значення -67 дБм", FIELD, -67.0),
    ]

    all_pts = []
    for ch_num, lbl, col, mean_val in ch_data:
        pts = []
        for i in range(30):
            x = ox + (i / 29.0) * gw
            noise = rng.gauss(0, 1.4)
            val = mean_val + noise
            pts.append((x, ry(val)))
            all_pts.append((x, val))
            p.append(circle(x, ry(val), 3.5, fill=col, stroke=col, sw=1))

        for j in range(len(pts) - 1):
            p.append(line(pts[j][0], pts[j][1], pts[j+1][0], pts[j+1][1], color=col, sw=1.2, dash="2,2"))

    true_mean_y = ry(-68.0)
    p.append(line(ox, true_mean_y, ox + gw, true_mean_y, color=INK, sw=2.2))
    p.append(text(ox + gw - 10, true_mean_y - 8, "Справжнє усереднене значення (-68 дБм)", size=10, color=INK, bold=True, anchor="end"))

    p.append(line(ox + 40, ry(-62), ox + 40, ry(-75), color="#7c3aed", sw=1.8))
    p.append(arrow(ox + 40, ry(-68), ox + 40, ry(-62), color="#7c3aed", sw=1.5))
    p.append(arrow(ox + 40, ry(-68), ox + 40, ry(-75), color="#7c3aed", sw=1.5))
    p.append(text(ox + 50, ry(-68.5) + 4, "Δ = 13 дБм між каналами\n(статичний маячок на 2 м!)", size=9, color="#7c3aed", bold=True, anchor="start"))

    p.append(rect(ox + 180, 52, 470, 48, fill="#ffffff", stroke=MUTED, sw=1.0, rx=6))
    for i, (ch_num, lbl, col, _) in enumerate(ch_data):
        lx = ox + 195 + (i % 2) * 230
        ly = 68 + (i // 2) * 20
        if i == 2:
            lx = ox + 195
            ly = 88
        p.append(circle(lx, ly, 4, fill=col, stroke=col, sw=1))
        p.append(text(lx + 10, ly + 3, lbl, size=9, color=INK, anchor="start"))

    render(os.path.join(OUT, "channel-fading-rssi.svg"), W, H, *p,
           title="Частотно-селективне багатопроменеве завмирання на каналах 37, 38 та 39")


# ── 4. kalman-rssi-filtering: конвеєр обробки сигналу ─────────────────────────
def fig_kalman_rssi_filtering():
    W, H = 800, 360
    p = []

    # Блок 1: Сирий потік
    b1, _, _ = textbox(110, 110, "Сирий потік RSSI\n• Пакети з Ch 37, 38, 39\n• Стрибки шуму до ±15 дБ\n• Випадкові випадіння",
                       size=10, pad=8, fill="#fee2e2", stroke=POS, sw=1.5, min_w=150)
    p.append(b1)

    p.append(arrow(190, 110, 240, 110, color=LINE, sw=1.8))
    p.append(text(215, 100, "z[k]", size=10, color=INK, bold=True))

    # Блок 2: Медіанний фільтр
    b2, _, _ = textbox(325, 110, "Медіанний фільтр\n(вікно W = 5..7)\n• Відкидає глибокі випади\n• Зберігає фронт зміни",
                       size=10, pad=8, fill="#fef3c7", stroke="#d97706", sw=1.5, min_w=150)
    p.append(b2)

    p.append(arrow(405, 110, 455, 110, color=LINE, sw=1.8))
    p.append(text(430, 100, "z_med", size=10, color=INK, bold=True))

    # Блок 3: 1D Фільтр Калмана
    b3, _, _ = textbox(575, 110, "1D Фільтр Калмана\nПрогноз: x̂ = x, P = P + Q\nПідсилення: K = P / (P + R)\nОновлення: x̂ = x̂ + K(z - x̂)\nP = (1 - K)P",
                       size=10, pad=8, fill="#dbeafe", stroke=NEG, sw=1.6, min_w=200)
    p.append(b3)

    p.append(arrow(680, 110, 720, 110, color=LINE, sw=1.8))
    p.append(text(700, 100, "RSSI_est", size=10, color=INK, bold=True))

    # Стрілка вниз до перетворення відстані
    p.append(arrow(575, 165, 575, 220, color=NEG, sw=2.0))

    # Блок 4: Log-Distance Path Loss
    b4, _, _ = textbox(575, 270, "Log-Distance Path Loss Model\nd = 10 ^ ((MeasuredPower - RSSI_est) / (10 · n))\nРозрахунок фізичної відстані (м)",
                       size=11, pad=8, fill="#dcfce7", stroke=FIELD, sw=1.8, min_w=340)
    p.append(b4)

    p.append(arrow(395, 270, 290, 270, color=FIELD, sw=2.0))

    # Блок 5: Зони близькості
    b5, _, _ = textbox(165, 270, "Зони наближення (Proximity Zones)\n• Immediate: d < 0.5 м\n• Near: 0.5 м ≤ d ≤ 3.0 м\n• Far: d > 3.0 м\n• Unknown: сигнал втрачено",
                       size=10, pad=8, fill="#f8fafc", stroke=MUTED, sw=1.5, min_w=210)
    p.append(b5)

    render(os.path.join(OUT, "kalman-rssi-filtering.svg"), W, H, *p,
           title="Конвеєр цифрової обробки сигналу та фільтрації шуму RSSI")


if __name__ == "__main__":
    fig_beacon_packet_comparison()
    fig_log_distance_path_loss()
    fig_channel_fading_rssi()
    fig_kalman_rssi_filtering()
    print("All figures rendered successfully.")
