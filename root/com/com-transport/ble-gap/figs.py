# -*- coding: utf-8 -*-
"""Генератор фігур для теми ble-gap (BLE GAP: рекламування, ролі та встановлення зв'язку)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. ble-gap-stack: положення GAP у стеку BLE ──────────────────────────────
def fig_ble_gap_stack():
    W, H = 760, 420
    p = []

    # Верхній рівень: Застосунок
    app_b, _, _ = textbox(380, 50, "Рівень застосунку (Application)\nПрофілі користувача, бізнес-логіка, датчики",
                          size=12, pad=8, fill="#f8fafc", stroke=MUTED, sw=1.5, bold=True, min_w=680)
    p.append(app_b)

    # Рівень хоста (Host)
    p.append(rect(40, 95, 680, 145, fill="#f0f4f8", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(60, 115, "Рівень хоста (Host)", size=11, color=MUTED, bold=True, anchor="start"))

    # GAP зліва (акцент)
    gap_b, _, _ = textbox(215, 175, "GAP (Generic Access Profile)\n• Ролі: Broadcaster, Observer, Peripheral, Central\n• Рекламування (Advertising) і сканування\n• Встановлення з'єднання та узгодження таймінгів\n• Приватність адрес і безпека зв'язку",
                          size=11, pad=10, fill="#eafaf0", stroke=FIELD, sw=2.0, bold=False, min_w=310)
    p.append(gap_b)
    p.append(text(215, 138, "GAP — поведінка та зв'язок", size=12, color=FIELD, bold=True))

    # GATT / ATT справа
    gatt_b, _, _ = textbox(545, 175, "GATT / ATT\n• Сервіси та характеристики\n• Операції Read, Write, Notify, Indicate\n• Модель даних клієнт / сервер\n• Структура бази атрибутів",
                           size=11, pad=10, fill="#eef4ff", stroke=NEG, sw=1.6, bold=False, min_w=310)
    p.append(gatt_b)
    p.append(text(545, 138, "GATT — структура даних", size=12, color=NEG, bold=True))

    # Інтерфейс HCI
    p.append(line(40, 255, 720, 255, color=LINE, sw=1.8, dash="6,4"))
    p.append(text(380, 250, "Інтерфейс контролера HCI (Host Controller Interface) — команди та події", size=11, color=MUTED, italic=True))

    # Рівень контролера (Controller)
    p.append(rect(40, 270, 680, 135, fill="#fbfaf6", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(60, 290, "Рівень контролера (Controller)", size=11, color=MUTED, bold=True, anchor="start"))

    # Link Layer
    ll_b, _, _ = textbox(380, 335, "Link Layer (LL)\n• Стан: Standby, Advertising, Scanning, Initiating, Connection\n• Керування радіопакетами, частотне стрибання (FHSS), таймінги зв'язку",
                         size=11, pad=8, fill="#fdf2e9", stroke=POS, sw=1.6, bold=False, min_w=640)
    p.append(ll_b)
    p.append(text(380, 308, "Link Layer — канальний рівень радіо", size=12, color=POS, bold=True))

    # Фізичний рівень (PHY)
    phy_b, _, _ = textbox(380, 385, "Фізичний рівень (PHY 2.4 ГГц): LE 1M, LE 2M, LE Coded (S=2, S=8)",
                          size=11, pad=6, fill="#f5eef8", stroke="#8e44ad", sw=1.4, bold=True, min_w=640)
    p.append(phy_b)

    render(os.path.join(OUT, "ble-gap-stack.svg"), W, H, *p,
           title="Положення GAP у стеку протоколів Bluetooth Low Energy")


# ── 2. gap-roles: чотири фундаментальні ролі GAP ─────────────────────────────
def fig_gap_roles():
    W, H = 760, 360
    p = []

    # Ліва колонка: Без з'єднання (Connectionless)
    p.append(rect(30, 45, 335, 295, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(197, 68, "Режим без з'єднання (Broadcasting)", size=12, color=MUTED, bold=True))

    # Broadcaster
    bc_b, _, _ = textbox(197, 125, "Broadcaster (Мовник)\n• Тільки передає (Tx)\n• Шле пакети ADV_NONCONN_IND\n• Приклади: iBeacon, маячок температури",
                         size=11, pad=8, fill="#eafaf0", stroke=FIELD, sw=1.8, min_w=300)
    p.append(bc_b)

    # Стрілка вниз
    p.append(arrow(197, 168, 197, 212, color=FIELD, sw=2.0))
    p.append(text(240, 192, "реклама (Adv)", size=10, color=FIELD, bold=True, anchor="start"))

    # Observer
    ob_b, _, _ = textbox(197, 260, "Observer (Спостерігач)\n• Тільки приймає (Rx)\n• Пасивне або активне сканування\n• Приклади: сканер міток, шлюз збору даних",
                         size=11, pad=8, fill="#eef4ff", stroke=NEG, sw=1.8, min_w=300)
    p.append(ob_b)

    # Права колонка: Зі з'єднанням (Connection-oriented)
    p.append(rect(395, 45, 335, 295, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(562, 68, "Режим зі з'єднанням (Connection)", size=12, color=MUTED, bold=True))

    # Peripheral
    per_b, _, _ = textbox(562, 125, "Peripheral (Периферія)\n• Рекламує себе (ADV_IND)\n• Приймає з'єднання → Link Layer Slave\n• Приклади: розумний годинник, пульсометр",
                          size=11, pad=8, fill="#fdf2e9", stroke=POS, sw=1.8, min_w=300)
    p.append(per_b)

    # Стрілки двосторонні
    p.append(arrow(540, 212, 540, 168, color=POS, sw=1.8))
    p.append(arrow(584, 168, 584, 212, color=NEG, sw=1.8))
    p.append(text(495, 185, "Adv / Дані", size=10, color=POS, bold=True, anchor="end"))
    p.append(text(628, 195, "Connect / Дані", size=10, color=NEG, bold=True, anchor="start"))

    # Central
    cen_b, _, _ = textbox(562, 260, "Central (Центральний)\n• Сканує ефір і надсилає CONNECT_IND\n• Керує розкладом → Link Layer Master\n• Приклади: смартфон, планшет, ПК",
                          size=11, pad=8, fill="#eef4ff", stroke=NEG, sw=1.8, min_w=300)
    p.append(cen_b)

    render(os.path.join(OUT, "gap-roles.svg"), W, H, *p,
           title="Фундаментальні ролі GAP у Bluetooth Low Energy")


# ── 3. adv-channels: розміщення каналів 37, 38, 39 між Wi-Fi ─────────────────
def fig_adv_channels():
    W, H = 760, 340
    p = []

    ox, oy = 50, 260
    aw = 660

    # Частотна вісь
    p.append(arrow(ox, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    p.append(text(ox + aw + 15, oy + 25, "Частота (МГц)", size=11, color=INK, bold=True, anchor="end"))

    # Позначки частот на осі
    freqs = [
        (2402, "2402"),
        (2412, "2412"),
        (2426, "2426"),
        (2437, "2437"),
        (2462, "2462"),
        (2480, "2480"),
    ]
    for f, lbl in freqs:
        fx = ox + (f - 2400) / 85.0 * aw
        p.append(line(fx, oy, fx, oy + 5, color=MUTED, sw=1.2))
        p.append(text(fx, oy + 18, lbl, size=10, color=MUTED, anchor="middle"))

    # Wi-Fi канали (широкі контурні блоки)
    wifi_ch = [
        (2412, "Wi-Fi Канал 1\n(2401..2423 МГц)", POS),
        (2437, "Wi-Fi Канал 6\n(2426..2448 МГц)", POS),
        (2462, "Wi-Fi Канал 11\n(2451..2473 МГц)", POS),
    ]
    for cf, name, stroke_col in wifi_ch:
        cx = ox + (cf - 2400) / 85.0 * aw
        bw = (22.0 / 85.0) * aw
        p.append(rect(cx - bw / 2, oy - 140, bw, 140, fill="none", stroke=stroke_col, sw=1.4, rx=6))
        p.append(mtext(cx, oy - 110, name.split("\n"), size=10, color=stroke_col, bold=True))

    # BLE рекламні канали 37, 38, 39 (зелені стовпчики)
    ble_ch = [
        (2402, 37, "Канал 37\n(2402 МГц)"),
        (2426, 38, "Канал 38\n(2426 МГц)"),
        (2480, 39, "Канал 39\n(2480 МГц)"),
    ]
    for f, ch_num, lbl in ble_ch:
        cx = ox + (f - 2400) / 85.0 * aw
        p.append(rect(cx - 12, oy - 195, 24, 195, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=4))
        p.append(text(cx, oy - 202, "BLE Ch %d" % ch_num, size=11, color=FIELD, bold=True, anchor="middle"))
        p.append(text(cx, oy - 165, "%d МГц" % f, size=9, color=FIELD, bold=True, anchor="middle"))

    # Пояснювальний підпис внизу
    p.append(text(W / 2, 45, "Канали 37, 38 і 39 розміщені в проміжках між основними неперекривними каналами Wi-Fi",
                  size=11, color=INK, bold=True, anchor="middle"))

    render(os.path.join(OUT, "adv-channels.svg"), W, H, *p,
           title="Первинні канали рекламування BLE у діапазоні 2.4 ГГц ISM")


# ── 4. adv-event-timing: подія рекламування та advDelay ──────────────────────
def fig_adv_event_timing():
    W, H = 760, 300
    p = []

    ox, oy = 50, 220
    aw = 660

    # Часова вісь
    p.append(arrow(ox, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    p.append(text(ox + aw + 15, oy + 22, "Час (t)", size=11, color=INK, bold=True, anchor="end"))

    # Перша подія рекламування (Event 1)
    ev1_x = ox + 40
    # Пакет Ch 37
    p.append(rect(ev1_x, oy - 70, 28, 70, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(ev1_x + 14, oy - 76, "Ch 37", size=9, color=FIELD, bold=True))
    # Пакет Ch 38
    p.append(rect(ev1_x + 36, oy - 70, 28, 70, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(ev1_x + 50, oy - 76, "Ch 38", size=9, color=FIELD, bold=True))
    # Пакет Ch 39
    p.append(rect(ev1_x + 72, oy - 70, 28, 70, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(ev1_x + 86, oy - 76, "Ch 39", size=9, color=FIELD, bold=True))

    # Фігурна дужка або рамка події
    p.append(rect(ev1_x - 4, oy - 105, 108, 105, fill="none", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(ev1_x + 50, oy - 112, "Advertising Event (~1.5 мс)", size=10, color=FIELD, bold=True))

    # Сон між подіями
    sleep_x0 = ev1_x + 100
    sleep_x1 = ev1_x + 380
    p.append(line(sleep_x0, oy - 2, sleep_x1, oy - 2, color=MUTED, sw=2.5))
    p.append(text((sleep_x0 + sleep_x1) / 2, oy - 12, "Сон контролера (мікроампери)", size=10, color=MUTED, italic=True))

    # Друга подія рекламування (Event 2)
    ev2_x = sleep_x1 + 60  # включно з advDelay
    # advInterval мітка
    interval_end = sleep_x1
    p.append(arrow(ev1_x, oy - 145, interval_end, oy - 145, color=NEG, sw=1.4))
    p.append(arrow(interval_end, oy - 145, ev1_x, oy - 145, color=NEG, sw=1.4))
    p.append(line(ev1_x, oy - 145, ev1_x, oy, color=NEG, sw=1.0, dash="3,3"))
    p.append(line(interval_end, oy - 145, interval_end, oy, color=NEG, sw=1.0, dash="3,3"))
    p.append(text((ev1_x + interval_end) / 2, oy - 152, "advInterval (фіксований, наприклад 100 мс)", size=11, color=NEG, bold=True))

    # advDelay мітка
    p.append(arrow(interval_end, oy - 145, ev2_x, oy - 145, color=POS, sw=1.4))
    p.append(arrow(ev2_x, oy - 145, interval_end, oy - 145, color=POS, sw=1.4))
    p.append(line(ev2_x, oy - 145, ev2_x, oy, color=POS, sw=1.0, dash="3,3"))
    p.append(text((interval_end + ev2_x) / 2, oy - 152, "advDelay (0..10 мс)", size=10, color=POS, bold=True))

    # Пакети Event 2
    p.append(rect(ev2_x, oy - 70, 28, 70, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(ev2_x + 14, oy - 76, "Ch 37", size=9, color=FIELD, bold=True))
    p.append(rect(ev2_x + 36, oy - 70, 28, 70, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(ev2_x + 50, oy - 76, "Ch 38", size=9, color=FIELD, bold=True))
    p.append(rect(ev2_x + 72, oy - 70, 28, 70, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(ev2_x + 86, oy - 76, "Ch 39", size=9, color=FIELD, bold=True))

    p.append(rect(ev2_x - 4, oy - 105, 108, 105, fill="none", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(ev2_x + 50, oy - 112, "Наступна подія", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, 40, "Псевдовипадковий зсув advDelay (0..10 мс) руйнує періодичні колізії між маячками",
                  size=11, color=INK, bold=True, anchor="middle"))

    render(os.path.join(OUT, "adv-event-timing.svg"), W, H, *p,
           title="Таймінги рекламної події (Advertising Event) та затримка advDelay")


# ── 5. active-scanning: діаграма послідовності Active Scanning ───────────────
def fig_active_scanning():
    W, H = 760, 380
    p = []

    # Вертикальні лінії життя (Lifelines)
    lx_per = 180
    lx_cen = 580
    top_y = 70
    bot_y = 340

    # Заголовки стовпчиків
    per_b, _, _ = textbox(lx_per, 45, "Периферія (Advertiser)", size=12, pad=6,
                          fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True)
    p.append(per_b)
    cen_b, _, _ = textbox(lx_cen, 45, "Центральний (Active Scanner)", size=12, pad=6,
                          fill="#eef4ff", stroke=NEG, sw=1.8, bold=True)
    p.append(cen_b)

    p.append(line(lx_per, top_y, lx_per, bot_y, color=MUTED, sw=1.5, dash="4,4"))
    p.append(line(lx_cen, top_y, lx_cen, bot_y, color=MUTED, sw=1.5, dash="4,4"))

    # 1. ADV_IND від периферії до центрального
    y1 = 110
    p.append(arrow(lx_per, y1, lx_cen, y1 + 30, color=FIELD, sw=2.0))
    p.append(fitbox(280, y1 - 5, 200, 30, "ADV_IND (до 31 Б даних)", size=11, fill="#f0fdf4", stroke=FIELD, sw=1.2, bold=True))

    # T_IFS пауза
    y_tifs1 = y1 + 30
    p.append(text(lx_cen + 12, y_tifs1 + 18, "T_IFS = 150 мкс", size=10, color=MUTED, anchor="start", italic=True))

    # 2. SCAN_REQ від центрального до периферії
    y2 = y_tifs1 + 35
    p.append(arrow(lx_cen, y2, lx_per, y2 + 30, color=NEG, sw=2.0))
    p.append(fitbox(280, y2 - 5, 200, 30, "SCAN_REQ (ScanA + AdvA)", size=11, fill="#eff6ff", stroke=NEG, sw=1.2, bold=True))

    # T_IFS пауза
    y_tifs2 = y2 + 30
    p.append(text(lx_per - 12, y_tifs2 + 18, "T_IFS = 150 мкс", size=10, color=MUTED, anchor="end", italic=True))

    # 3. SCAN_RSP від периферії до центрального
    y3 = y_tifs2 + 35
    p.append(arrow(lx_per, y3, lx_cen, y3 + 30, color=POS, sw=2.0))
    p.append(fitbox(280, y3 - 5, 200, 30, "SCAN_RSP (+31 Б даних)", size=11, fill="#fef2f2", stroke=POS, sw=1.2, bold=True))

    # Підсумок
    p.append(text(380, 320, "Активне сканування подвоює корисне навантаження (31 Б у ADV + 31 Б у SCAN_RSP = 62 Байти)",
                  size=11, color=INK, bold=True, anchor="middle"))

    render(os.path.join(OUT, "active-scanning.svg"), W, H, *p,
           title="Послідовність активного сканування (Active Scanning)")


# ── 6. connection-params: параметри з'єднання та Slave Latency ──────────────
def fig_connection_params():
    W, H = 760, 360
    p = []

    ox, oy = 60, 240
    aw = 640

    # Часова вісь
    p.append(arrow(ox, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    p.append(text(ox + aw + 15, oy + 22, "Час (t)", size=11, color=INK, bold=True, anchor="end"))

    # Події з'єднання (Connection Events)
    ce_w = 90
    events = [
        (0, "Event 0\n(Активна)", FIELD, True),
        (1, "Event 1\n(Пропуск)", MUTED, False),
        (2, "Event 2\n(Пропуск)", MUTED, False),
        (3, "Event 3\n(Пропуск)", MUTED, False),
        (4, "Event 4\n(Активна)", FIELD, True),
        (5, "Event 5\n(Активна)", FIELD, True),
    ]

    for idx, (ev_num, lbl, col, active) in enumerate(events):
        ex = ox + 30 + idx * ce_w
        # Master пакет (завжди передається)
        p.append(rect(ex, oy - 60, 18, 60, fill="#dbeafe", stroke=NEG, sw=1.4, rx=3))
        p.append(text(ex + 9, oy - 66, "M", size=9, color=NEG, bold=True))

        # Slave пакет (тільки коли активна)
        if active:
            p.append(rect(ex + 24, oy - 60, 18, 60, fill="#dcfce7", stroke=FIELD, sw=1.4, rx=3))
            p.append(text(ex + 33, oy - 66, "S", size=9, color=FIELD, bold=True))
        else:
            p.append(rect(ex + 24, oy - 15, 18, 15, fill="#f3f4f6", stroke=MUTED, sw=1.0, rx=2))
            p.append(text(ex + 33, oy - 22, "сон", size=9, color=MUTED))

        p.append(line(ex - 4, oy - 80, ex - 4, oy + 5, color="#cbd5e1", sw=1.0, dash="3,3"))

    # Connection Interval дужка між Event 0 і Event 1
    x0 = ox + 30
    x1 = ox + 30 + ce_w
    p.append(arrow(x0, oy - 110, x1, oy - 110, color=NEG, sw=1.4))
    p.append(arrow(x1, oy - 110, x0, oy - 110, color=NEG, sw=1.4))
    p.append(text((x0 + x1) / 2, oy - 118, "Connection Interval (7.5 мс .. 4 с)", size=10, color=NEG, bold=True))

    # Slave Latency дужка (Event 1 .. Event 3 = пропуск 3 подій)
    xs_start = ox + 30 + ce_w
    xs_end = ox + 30 + 4 * ce_w
    p.append(arrow(xs_start, oy - 150, xs_end, oy - 150, color=POS, sw=1.6))
    p.append(arrow(xs_end, oy - 150, xs_start, oy - 150, color=POS, sw=1.6))
    p.append(text((xs_start + xs_end) / 2, oy - 158, "Peripheral / Slave Latency = 3 (периферія спить 3 інтервали)", size=11, color=POS, bold=True))

    # Supervision Timeout лінія зверху
    p.append(arrow(x0, 60, ox + 30 + 5.5 * ce_w, 60, color="#8e44ad", sw=1.4))
    p.append(text((x0 + ox + 30 + 5.5 * ce_w) / 2, 50, "Supervision Timeout (100 мс .. 32.0 с) — ліміт очікування без пакетів", size=11, color="#8e44ad", bold=True))

    render(os.path.join(OUT, "connection-params.svg"), W, H, *p,
           title="Параметри з'єднання BLE: Connection Interval, Slave Latency та Supervision Timeout")


# ── 7. extended-advertising: архітектура Extended Advertising у BLE 5.0 ─────
def fig_extended_adv():
    W, H = 760, 360
    p = []

    # Первинні канали (Primary Channels: 37, 38, 39)
    p.append(rect(40, 50, 680, 115, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(60, 72, "Первинні канали рекламування (Primary Channels: 37, 38, 39) — LE 1M / LE Coded",
                  size=11, color=FIELD, bold=True, anchor="start"))

    adv_ext, _, _ = textbox(210, 115, "ADV_EXT_IND (Короткий заголовок)\n• Адреса передавача (AdvA)\n• AuxPointer: [Канал 14, Час Δt, PHY LE 2M]",
                            size=10, pad=8, fill="#ffffff", stroke=FIELD, sw=1.5, min_w=280)
    p.append(adv_ext)

    p.append(text(520, 115, "Мінімізує завантаження каналів 37-39,\nперенаправляючи слухача на канали даних",
                  size=10, color=MUTED, italic=True))

    # Стрілка покажчика AuxPointer
    p.append(arrow(210, 150, 210, 215, color=POS, sw=2.2))
    p.append(text(225, 185, "AuxPointer (вказівник на вторинний канал)", size=11, color=POS, bold=True, anchor="start"))

    # Вторинні канали даних (Secondary Data Channels: 0..36)
    p.append(rect(40, 215, 680, 120, fill="#eff6ff", stroke=NEG, sw=1.4, rx=8))
    p.append(text(60, 237, "Вторинні канали даних (Secondary Channels: 0..36) — LE 1M / LE 2M / LE Coded",
                  size=11, color=NEG, bold=True, anchor="start"))

    aux_adv, _, _ = textbox(210, 280, "AUX_ADV_IND (Великий пакет даних)\n• Корисне навантаження до 254 байтів\n• Швидкість LE 2M або дальність LE Coded",
                            size=10, pad=8, fill="#ffffff", stroke=NEG, sw=1.5, min_w=280)
    p.append(aux_adv)

    chain_adv, _, _ = textbox(530, 280, "AUX_CHAIN_IND (Ланцюгові пакети)\n• Об'єднання пакетів до 1650 байтів\n• Periodic Advertising (SyncInfo) для LE Audio",
                              size=10, pad=8, fill="#ffffff", stroke=NEG, sw=1.2, min_w=280)
    p.append(chain_adv)

    p.append(arrow(355, 280, 385, 280, color=NEG, sw=1.5))

    render(os.path.join(OUT, "extended-advertising.svg"), W, H, *p,
           title="Архітектура розширеного рекламування (Extended Advertising) у Bluetooth 5.0")


if __name__ == "__main__":
    fig_ble_gap_stack()
    fig_gap_roles()
    fig_adv_channels()
    fig_adv_event_timing()
    fig_active_scanning()
    fig_connection_params()
    fig_extended_adv()
    print("Всі 7 фігур успішно згенеровано у %s" % OUT)
