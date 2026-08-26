# -*- coding: utf-8 -*-
"""Фігури до теми «Серцебиття й виявлення розриву».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

HOT = "#c0392b"
COLD = "#2457d6"
WARN = "#d97706"
FIELD = "#27ae60"
MUTED = "#6b7280"


# ── 1. Сценарії «мовчазного» обриву ──────────────────────────────────────────
def fig_silent_disconnect():
    W, H = 960, 560
    f = [text(W / 2, 28, "Чому апаратний лінк не гарантує життя вузла", size=16, bold=True)]

    card_w, card_h = 276, 440
    y0 = 60

    # Картка 1: Зависання процесу при живому PHY
    x1 = 44
    f.append(rect(x1, y0, card_w, card_h, fill="#fffaf0", stroke=WARN, sw=1.8, rx=10))
    f.append(text(x1 + card_w / 2, y0 + 26, "1. Завис процесор / ОС", size=13, bold=True, color="#9a5b00"))
    
    # Блок вузла А (Керуючий)
    f.append(rect(x1 + 20, y0 + 50, 105, 70, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    f.append(text(x1 + 72, y0 + 78, "Хост A", size=11, bold=True))
    f.append(text(x1 + 72, y0 + 98, "Чекає дані", size=10, color=MUTED))

    # Блок вузла Б (Завис)
    f.append(rect(x1 + 150, y0 + 50, 105, 70, fill="#fdecea", stroke=HOT, sw=1.5, rx=6))
    f.append(text(x1 + 202, y0 + 78, "Вузол B", size=11, bold=True, color=HOT))
    f.append(text(x1 + 202, y0 + 98, "HardFault / Lock", size=10, color=HOT))

    # Лінія PHY Link
    f.append(line(x1 + 125, y0 + 85, x1 + 150, y0 + 85, color=FIELD, sw=3))
    f.append(circle(x1 + 137, y0 + 72, 4, fill=FIELD, stroke="none", sw=0))
    f.append(text(x1 + 137, y0 + 64, "PHY UP", size=10, bold=True, color=FIELD))

    b1, _, _ = textbox(x1 + card_w / 2, y0 + 220,
                       "Апаратний трансивер\n(Ethernet PHY, CAN-чіп,\nRS-485 драйвер) живиться\nі тримає несучу частоту\nабо рівень шини.\n\nПроцесор ядра завис\nу мертвому циклі й не шле\nжодних корисних команд.",
                       size=10.5, fill="#ffffff", stroke="#e0caa0", min_w=246)
    f.append(b1)
    
    b1_bot, _, _ = textbox(x1 + card_w / 2, y0 + 380,
                           "Наслідок:\nПін LINK світиться зеленим,\nале зв'язку немає взагалі.",
                           size=10.5, bold=True, fill="#fdecea", stroke=HOT, min_w=246)
    f.append(b1_bot)

    # Картка 2: Асиметричний радіообрив
    x2 = 342
    f.append(rect(x2, y0, card_w, card_h, fill="#eef2f8", stroke=COLD, sw=1.8, rx=10))
    f.append(text(x2 + card_w / 2, y0 + 26, "2. Асиметричний канал", size=13, bold=True, color=COLD))

    f.append(rect(x2 + 20, y0 + 50, 105, 70, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    f.append(text(x2 + 72, y0 + 78, "Пульт TX", size=11, bold=True))
    f.append(text(x2 + 72, y0 + 98, "Шле 100 мВт", size=10, color=MUTED))

    f.append(rect(x2 + 150, y0 + 50, 105, 70, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    f.append(text(x2 + 202, y0 + 78, "Дрон RX", size=11, bold=True))
    f.append(text(x2 + 202, y0 + 98, "Шле 10 мВт", size=10, color=MUTED))

    # Стрілка вниз (йде), стрілка назад (перебита)
    f.append(arrow(x2 + 125, y0 + 75, x2 + 150, y0 + 75, color=FIELD, sw=2))
    f.append(line(x2 + 150, y0 + 95, x2 + 138, y0 + 95, color=HOT, sw=2))
    f.append(text(x2 + 137, y0 + 98, "✕", size=12, bold=True, color=HOT))

    b2, _, _ = textbox(x2 + card_w / 2, y0 + 220,
                       "Прямий лінк (TX хоста)\nпотужний і доходить,\nале зворотний лінк (RX)\nзаглушений завадою або\nмає слабкий передавач.\n\nХост думає, що дрон пропав,\nа дрон усе ще виконує\nстарі команди з ефіру.",
                       size=10.5, fill="#ffffff", stroke="#c8d6e8", min_w=246)
    f.append(b2)

    b2_bot, _, _ = textbox(x2 + card_w / 2, y0 + 380,
                           "Наслідок:\nОдносторонній політ у стіну\nчерез хибний стан зв'язку.",
                           size=10.5, bold=True, fill="#fdecea", stroke=HOT, min_w=246)
    f.append(b2_bot)

    # Картка 3: Мертвий TCP сокет / дроп у NAT
    x3 = 640
    f.append(rect(x3, y0, card_w, card_h, fill="#f4f6f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(x3 + card_w / 2, y0 + 26, "3. Напіввідкритий сокет", size=13, bold=True, color=INK))

    f.append(rect(x3 + 20, y0 + 50, 75, 70, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    f.append(text(x3 + 57, y0 + 78, "Клієнт", size=11, bold=True))
    f.append(text(x3 + 57, y0 + 98, "ESTABL.", size=10, color=FIELD))

    # Роутер посередині
    f.append(rect(x3 + 102, y0 + 58, 72, 54, fill="#fdecea", stroke=HOT, sw=1.2, rx=4))
    f.append(text(x3 + 138, y0 + 78, "NAT / AP", size=10, bold=True))
    f.append(text(x3 + 138, y0 + 96, "Drop state", size=9.5, color=HOT))

    f.append(rect(x3 + 180, y0 + 50, 75, 70, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    f.append(text(x3 + 217, y0 + 78, "Сервер", size=11, bold=True))
    f.append(text(x3 + 217, y0 + 98, "Вимкнено", size=10, color=MUTED))

    b3, _, _ = textbox(x3 + card_w / 2, y0 + 220,
                       "Кабель живлення висмикнули,\nале жоден TCP FIN або RST\nне було надіслано в мережу.\n\nПроміжний роутер тихо\nвитер трансляцію з пам'яті.\n\nСтандартний TCP Keepalive\nза замовчуванням чекає\n2 години до першої проби!",
                       size=10.5, fill="#ffffff", stroke="#d0d6dd", min_w=246)
    f.append(b3)

    b3_bot, _, _ = textbox(x3 + card_w / 2, y0 + 380,
                           "Наслідок:\nСокет висить годинами,\nпам'ять і дескриптори течуть.",
                           size=10.5, bold=True, fill="#fdecea", stroke=HOT, min_w=246)
    f.append(b3_bot)

    render(os.path.join(IMG, "silent-disconnect-scenarios.svg"), W, H, *f)


# ── 2. Часовий бюджет Heartbeat та джитер ────────────────────────────────────
def fig_heartbeat_timing():
    W, H = 960, 480
    f = [text(W / 2, 28, "Часовий бюджет Heartbeat: період, пропуски та джитер", size=16, bold=True)]

    t0 = 80
    tW = 800
    y_top = 80

    f.append(text(t0, y_top, "1. Регулярний пульс і лічильник втрат N = 3", size=13, bold=True, color=INK, anchor="start"))

    # Вісь часу
    axis_y = y_top + 50
    f.append(line(t0, axis_y, t0 + tW, axis_y, color=INK, sw=2))
    f.append(text(t0 + tW + 10, axis_y + 4, "Час (t)", size=10, color=MUTED, anchor="start"))

    # Імпульси пульсу
    hb_times = [0.08, 0.22, 0.36]
    for idx, ht in enumerate(hb_times):
        hx = t0 + ht * tW
        f.append(line(hx, axis_y - 28, hx, axis_y, color=FIELD, sw=2.5))
        f.append(circle(hx, axis_y - 28, 4, fill=FIELD, stroke="none", sw=0))
        f.append(text(hx, axis_y - 36, "HB #%d" % (idx + 1), size=10, bold=True, color=FIELD))
        f.append(text(hx, axis_y + 18, "ACK ✓", size=10, color=FIELD))

    # Інтервал T_hb
    f.append(line(t0 + 0.08 * tW, axis_y - 12, t0 + 0.22 * tW, axis_y - 12, color=COLD, sw=1.5))
    f.append(text(t0 + 0.15 * tW, axis_y - 18, "T_hb (період)", size=10, bold=True, color=COLD))

    # Точка аварії / обриву
    x_fault = t0 + 0.44 * tW
    f.append(line(x_fault, axis_y - 45, x_fault, axis_y + 45, color=HOT, sw=2, dash="4 3"))
    f.append(text(x_fault, axis_y - 52, "ОБРИВ ЛІНІЇ", size=10.5, bold=True, color=HOT))

    # Пропущені HB (1, 2, 3)
    missed_times = [0.50, 0.64, 0.78]
    for idx, mt in enumerate(missed_times):
        mx = t0 + mt * tW
        f.append(line(mx, axis_y - 28, mx, axis_y, color=HOT, sw=2, dash="3 3"))
        f.append(text(mx, axis_y - 34, "✕", size=12, bold=True, color=HOT))
        f.append(text(mx, axis_y + 18, "Пропуск %d" % (idx + 1), size=10, color=HOT))

    # Момент Failsafe
    x_fail = t0 + 0.78 * tW + 25
    f.append(rect(x_fail - 40, axis_y - 30, 95, 42, fill="#fdecea", stroke=HOT, sw=2, rx=5))
    f.append(text(x_fail + 7, axis_y - 14, "FAILSAFE!", size=10.5, bold=True, color=HOT))
    f.append(text(x_fail + 7, axis_y + 4, "Аварійний стоп", size=9.5, color=HOT))

    # Інтервал T_fail
    f.append(line(x_fault, axis_y + 40, x_fail, axis_y + 40, color=HOT, sw=1.8))
    f.append(text((x_fault + x_fail) / 2, axis_y + 56, "Час реакції T_fail = N × T_hb + запас", size=10.5, bold=True, color=HOT))

    # Нижня частина: Джитер (розмиття фази)
    y_bot = 270
    f.append(text(t0, y_bot, "2. Захист від резонансу пакетів (Heartbeat Jitter)", size=13, bold=True, color=INK, anchor="start"))

    bx1, _, _ = textbox(t0 + 190, y_bot + 95,
                        "БЕЗ ДЖИТЕРА (жорсткий таймер):\n100 датчиків увімкнулися одночасно\n→ шлють HB кожні строго 1000 мс\n→ шторм колізій в ефірі щосекунди.",
                        size=10, fill="#fdecea", stroke=HOT, min_w=370)
    f.append(bx1)

    bx2, _, _ = textbox(t0 + 600, y_bot + 95,
                        "З ДЖИТЕРОМ (рандомізація ±15%):\nПеріод = T_hb ± rand(-0.15, +0.15) × T_hb\n→ фази імпульсів розмазуються в часі\n→ навантаження на канал рівномірне.",
                        size=10, fill="#eef6ef", stroke=FIELD, min_w=390)
    f.append(bx2)

    render(os.path.join(IMG, "heartbeat-timing-budget.svg"), W, H, *f)


# ── 3. Dead Peer Detection проти постійного Heartbeat ────────────────────────
def fig_dpd_vs_heartbeat():
    W, H = 960, 500
    f = [text(W / 2, 28, "Heartbeat за розкладом чи Dead Peer Detection за простоєм", size=16, bold=True)]

    t0 = 80
    tW = 800

    # 1. Постійний Heartbeat
    y1 = 65
    f.append(rect(t0 - 20, y1, tW + 40, 185, fill="#fffaf0", stroke=WARN, sw=1.5, rx=8))
    f.append(text(t0, y1 + 24, "А. Класичний безумовний Heartbeat (періодичний)", size=12.5, bold=True, color="#9a5b00", anchor="start"))

    ay1 = y1 + 75
    f.append(line(t0, ay1, t0 + tW, ay1, color=INK, sw=1.8))
    f.append(text(t0 + tW + 10, ay1 + 4, "t", size=10, color=MUTED, anchor="start"))

    # Потік даних
    f.append(rect(t0 + 40, ay1 - 25, 260, 20, fill="#eef2f8", stroke=COLD, sw=1.2, rx=4))
    f.append(text(t0 + 170, ay1 - 11, "Корисний трафік телеметрії (50 Гц)", size=10, color=COLD))

    # Серцебиття лізе поверх трафіку
    hb_pts = [0.1, 0.25, 0.4, 0.55, 0.7, 0.85]
    for hp in hb_pts:
        hx = t0 + hp * tW
        f.append(line(hx, ay1, hx, ay1 + 25, color=WARN, sw=2))
        f.append(circle(hx, ay1 + 25, 3.5, fill=WARN, stroke="none", sw=0))
        f.append(text(hx, ay1 + 40, "HB ping", size=9.5, color="#9a5b00"))

    f.append(text(t0 + tW / 2, y1 + 165,
                  "Мінус: шле пінг-понг навіть коли канал на 100% забитий даними. Марнує батарею й радіоефір.",
                  size=10.5, color=HOT, bold=True))

    # 2. Dead Peer Detection
    y2 = 275
    f.append(rect(t0 - 20, y2, tW + 40, 195, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(t0, y2 + 24, "Б. Dead Peer Detection (DPD — перевірка лише під час тиші)", size=12.5, bold=True, color=FIELD, anchor="start"))

    ay2 = y2 + 75
    f.append(line(t0, ay2, t0 + tW, ay2, color=INK, sw=1.8))
    f.append(text(t0 + tW + 10, ay2 + 4, "t", size=10, color=MUTED, anchor="start"))

    # Корисний потік
    f.append(rect(t0 + 40, ay2 - 25, 280, 20, fill="#eef2f8", stroke=COLD, sw=1.2, rx=4))
    f.append(text(t0 + 180, ay2 - 11, "Корисний трафік (таймер DPD скидається в 0)", size=10, color=COLD))

    # Зона тиші
    f.append(text(t0 + 400, ay2 - 11, "Тиша в каналі...", size=10.5, italic=True, color=MUTED))

    # Спрацювання DPD проби
    x_probe = t0 + 0.62 * tW
    f.append(line(x_probe, ay2 - 25, x_probe, ay2 + 25, color=FIELD, sw=2.5))
    f.append(circle(x_probe, ay2 - 25, 4, fill=FIELD, stroke="none", sw=0))
    f.append(text(x_probe, ay2 - 33, "DPD Probe?", size=10, bold=True, color=FIELD))

    # Відповідь ACK
    x_ack = t0 + 0.72 * tW
    f.append(line(x_ack, ay2 - 20, x_ack, ay2 + 20, color=COLD, sw=2))
    f.append(text(x_ack, ay2 + 34, "DPD Ack ✓", size=10, bold=True, color=COLD))

    f.append(text(t0 + tW / 2, y2 + 175,
                  "Плюс: 0% оверхеду за наявності даних. Контрольний запит надсилається лише після таймауту тиші.",
                  size=10.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "dpd-vs-heartbeat.svg"), W, H, *f)


# ── 4. Адаптація таймаутів за алгоритмом Якобсона/Карна ───────────────────────
def fig_rtt_jacobson():
    W, H = 960, 500
    f = [text(W / 2, 28, "Адаптивний таймаут (RTO): фільтрація спалахів за Якобсоном", size=16, bold=True)]

    t0 = 80
    tW = 800
    base_y = 400

    # Осі
    f.append(line(t0, base_y, t0 + tW, base_y, color=INK, sw=2))
    f.append(line(t0, base_y, t0, 70, color=INK, sw=2))
    f.append(text(t0 + tW + 10, base_y + 4, "Вибірки RTT", size=10, color=MUTED, anchor="start"))
    f.append(text(t0 - 10, 64, "Час (мс)", size=10, color=MUTED, anchor="end"))

    # Дані RTT з викидом
    raw_rtt = [
        (0.05, 30), (0.10, 25), (0.15, 35), (0.20, 28), (0.25, 32),
        (0.35, 190), (0.40, 160), (0.45, 90), (0.50, 40),
        (0.60, 30), (0.70, 28), (0.80, 32), (0.90, 26)
    ]

    pts_raw = ["%.1f,%.1f" % (t0 + px * tW, base_y - py * 1.5) for px, py in raw_rtt]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3 3"/>' % (" ".join(pts_raw), MUTED))
    for px, py in raw_rtt:
        f.append(circle(t0 + px * tW, base_y - py * 1.5, 3.5, fill=MUTED, stroke="none", sw=0))

    # Згладжений SRTT (EWMA)
    srtt_data = [
        (0.05, 30), (0.10, 29), (0.15, 30), (0.20, 29), (0.25, 30),
        (0.35, 50), (0.40, 65), (0.45, 68), (0.50, 62),
        (0.60, 52), (0.70, 44), (0.80, 38), (0.90, 34)
    ]
    pts_srtt = ["%.1f,%.1f" % (t0 + px * tW, base_y - py * 1.5) for px, py in srtt_data]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts_srtt), COLD))

    # Динамічний поріг RTO = SRTT + 4 * RTTVAR
    rto_data = [
        (0.05, 75), (0.10, 72), (0.15, 76), (0.20, 74), (0.25, 75),
        (0.35, 230), (0.40, 240), (0.45, 210), (0.50, 170),
        (0.60, 130), (0.70, 100), (0.80, 85), (0.90, 78)
    ]
    pts_rto = ["%.1f,%.1f" % (t0 + px * tW, base_y - py * 1.5) for px, py in rto_data]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts_rto), HOT))

    # Статичний фіксований таймаут (показано як хибу)
    f.append(line(t0, base_y - 80 * 1.5, t0 + tW, base_y - 80 * 1.5, color=WARN, sw=2, dash="5 4"))
    f.append(text(t0 + tW - 10, base_y - 80 * 1.5 - 8, "Жорсткий таймаут (80 мс)", size=10, bold=True, color="#9a5b00", anchor="end"))

    # Позначка хибного спрацювання
    f.append(text(t0 + 0.37 * tW, base_y - 80 * 1.5 + 20, "Хибний обрив!", size=10.5, bold=True, color=HOT))
    f.append(arrow(t0 + 0.37 * tW, base_y - 80 * 1.5 + 8, t0 + 0.37 * tW, base_y - 120 * 1.5, color=HOT, sw=1.8))

    # Легенда
    lx, ly = t0 + 50, 90
    f.append(rect(lx, ly, 380, 95, fill="#ffffff", stroke=INK, sw=1.2, rx=6))
    f.append(line(lx + 15, ly + 22, lx + 45, ly + 22, color=MUTED, sw=1.8, dash="3 3"))
    f.append(text(lx + 55, ly + 26, "Сирі заміри RTT (зі спалахами)", size=10, anchor="start"))

    f.append(line(lx + 15, ly + 46, lx + 45, ly + 46, color=COLD, sw=2.6))
    f.append(text(lx + 55, ly + 50, "SRTT (експоненційне середнє)", size=10, bold=True, color=COLD, anchor="start"))

    f.append(line(lx + 15, ly + 70, lx + 45, ly + 70, color=HOT, sw=2.6))
    f.append(text(lx + 55, ly + 74, "RTO = SRTT + 4 × RTTVAR (адаптивний поріг)", size=10, bold=True, color=HOT, anchor="start"))

    render(os.path.join(IMG, "rtt-jacobson-timeout.svg"), W, H, *f)


# ── 5. Автомат станів моніторингу зв'язку та Failsafe ────────────────────────
def fig_fsm_failsafe():
    W, H = 960, 540
    f = [text(W / 2, 28, "Скінченний автомат моніторингу каналу та входу у Failsafe", size=16, bold=True)]

    # Координати станів
    # 1. DISCONNECTED
    x_disc, y_disc = 80, 160
    w_box, h_box = 180, 90

    f.append(rect(x_disc, y_disc, w_box, h_box, fill="#f4f6f8", stroke=INK, sw=2, rx=8))
    f.append(text(x_disc + w_box / 2, y_disc + 30, "DISCONNECTED", size=12, bold=True))
    f.append(text(x_disc + w_box / 2, y_disc + 52, "Канал не відкрито", size=10, color=MUTED))
    f.append(text(x_disc + w_box / 2, y_disc + 72, "Приводи знеструмлені", size=10, color=HOT))

    # 2. CONNECTING
    x_conn, y_conn = 390, 160
    f.append(rect(x_conn, y_conn, w_box, h_box, fill="#eef2f8", stroke=COLD, sw=2, rx=8))
    f.append(text(x_conn + w_box / 2, y_conn + 30, "CONNECTING", size=12, bold=True, color=COLD))
    f.append(text(x_conn + w_box / 2, y_conn + 52, "Рукостискання / SYN", size=10, color=MUTED))
    f.append(text(x_conn + w_box / 2, y_conn + 72, "Очікування 1-го кадру", size=10, color=COLD))

    # 3. CONNECTED (ОК)
    x_ok, y_ok = 700, 160
    f.append(rect(x_ok, y_ok, w_box, h_box, fill="#eef6ef", stroke=FIELD, sw=2.2, rx=8))
    f.append(text(x_ok + w_box / 2, y_ok + 30, "CONNECTED_OK", size=12, bold=True, color=FIELD))
    f.append(text(x_ok + w_box / 2, y_ok + 52, "Пульс регулярний", size=10, color=MUTED))
    f.append(text(x_ok + w_box / 2, y_ok + 72, "Повне керування", size=10, bold=True, color=FIELD))

    # 4. SUSPECT (Деградація)
    x_susp, y_susp = 700, 360
    f.append(rect(x_susp, y_susp, w_box, h_box, fill="#fffaf0", stroke=WARN, sw=2, rx=8))
    f.append(text(x_susp + w_box / 2, y_susp + 30, "LINK_SUSPECT", size=12, bold=True, color="#9a5b00"))
    f.append(text(x_susp + w_box / 2, y_susp + 52, "Пропущено 1..N-1 кадрів", size=10, color=MUTED))
    f.append(text(x_susp + w_box / 2, y_susp + 72, "DPD Probe активний", size=10, color="#9a5b00"))

    # 5. FAILSAFE
    x_fail, y_fail = 390, 360
    f.append(rect(x_fail, y_fail, w_box, h_box, fill="#fdecea", stroke=HOT, sw=2.5, rx=8))
    f.append(text(x_fail + w_box / 2, y_fail + 30, "FAILSAFE_ACTIVE", size=12, bold=True, color=HOT))
    f.append(text(x_fail + w_box / 2, y_fail + 52, "T_fail вичерпано", size=10, color=MUTED))
    f.append(text(x_fail + w_box / 2, y_fail + 72, "АВАРІЙНИЙ СТОП", size=10, bold=True, color=HOT))

    # Стрілки переходів
    # DISCONNECTED -> CONNECTING
    f.append(arrow(x_disc + w_box, y_disc + 45, x_conn, y_conn + 45, color=INK, sw=1.8))
    f.append(text((x_disc + w_box + x_conn) / 2, y_disc + 35, "Open / Link UP", size=9.5, color=MUTED))

    # CONNECTING -> CONNECTED
    f.append(arrow(x_conn + w_box, y_conn + 45, x_ok, y_ok + 45, color=FIELD, sw=2))
    f.append(text((x_conn + w_box + x_ok) / 2, y_conn + 35, "1-й HB отримано", size=9.5, bold=True, color=FIELD))

    # CONNECTED -> SUSPECT
    f.append(arrow(x_ok + 60, y_ok + h_box, x_susp + 60, y_susp, color=WARN, sw=2))
    f.append(text(x_ok + 115, (y_ok + h_box + y_susp) / 2, "Пропуск кадру", size=9.5, bold=True, color="#9a5b00"))

    # SUSPECT -> CONNECTED (Відновлення)
    f.append(arrow(x_susp + 140, y_susp, x_ok + 140, y_ok + h_box, color=FIELD, sw=2))
    f.append(text(x_susp + 155, (y_ok + h_box + y_susp) / 2, "HB / ACK", size=9.5, bold=True, color=FIELD, anchor="start"))

    # SUSPECT -> FAILSAFE
    f.append(arrow(x_susp, y_susp + 45, x_fail + w_box, y_fail + 45, color=HOT, sw=2.5))
    f.append(text((x_susp + x_fail + w_box) / 2, y_susp + 35, "Таймаут T_fail", size=9.5, bold=True, color=HOT))

    # FAILSAFE -> CONNECTING (Скидання / перепідключення)
    f.append(arrow(x_fail + w_box / 2, y_fail, x_conn + w_box / 2, y_conn + h_box, color=MUTED, sw=1.8))
    f.append(text(x_fail + w_box / 2 + 10, (y_fail + y_conn + h_box) / 2, "Рестарт сесії", size=9.5, color=MUTED, anchor="start"))

    # CONNECTING -> DISCONNECTED (Таймаут з'єднання)
    f.append(arrow(x_conn, y_conn + 70, x_disc + w_box, y_disc + 70, color=HOT, sw=1.5))
    f.append(text((x_disc + w_box + x_conn) / 2, y_conn + 88, "Помилка зв'язку", size=9.5, color=HOT))

    render(os.path.join(IMG, "connection-fsm-failsafe.svg"), W, H, *f)


if __name__ == "__main__":
    fig_silent_disconnect()
    fig_heartbeat_timing()
    fig_dpd_vs_heartbeat()
    fig_rtt_jacobson()
    fig_fsm_failsafe()
    print("OK: 5 figures ->", IMG)
