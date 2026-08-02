# -*- coding: utf-8 -*-
"""Фігури до теми «Маршрутизація за sysid і compid» довідника QGroundControl."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

SOFT = "#ffffff"
BAND = "#eef2f6"
GREENFILL = "#e6f6ec"
REDFILL = "#fdecea"
GRAY = "#dfe5eb"


# ─────────────── 1. Дві пари адрес: у заголовку й у тілі ────────────────────
def fig_addresses():
    W, H = 1260, 640
    f = []

    # ── Панель A: заголовок ──────────────────────────────────────────────
    f.append(text(W / 2, 60, "Заголовок MAVLink v2 — 10 байтів, однакових у будь-якому повідомленні",
                  size=16, bold=True))

    cells = [("0xFD", 88), ("LEN", 88), ("IFLG", 88), ("CFLG", 88), ("SEQ", 88),
             ("SYSID", 88), ("COMPID", 88), ("MSGID", 264)]
    idx = ["0", "1", "2", "3", "4", "5", "6", "7–9"]
    x = 190
    cy_top, ch = 100, 64
    for i, (lbl, cw) in enumerate(cells):
        green = lbl in ("SYSID", "COMPID")
        f.append(fitbox(x, cy_top, cw, ch, lbl, size=14, bold=green,
                        fill=GREENFILL if green else SOFT,
                        stroke=FIELD if green else LINE, sw=2.4 if green else 1.4))
        f.append(text(x + cw / 2, cy_top + ch + 24, idx[i], size=12, color=MUTED))
        x += cw

    f.append(text(W / 2, 232,
                  "ці два байти лежать на своєму місці завжди — щоб зрозуміти, чий кадр, не треба знати, що це за повідомлення",
                  size=13, color=MUTED))

    # ── Панель B: тіло ───────────────────────────────────────────────────
    f.append(text(W / 2, 300, "Адреса одержувача — поле в тілі, і його зсув у кожного повідомлення свій",
                  size=16, bold=True))

    bar_x, bar_w = 300, 660

    # рядок 1 — COMMAND_LONG (33 байти)
    n1 = 33.0
    u1 = bar_w / n1
    y1 = 370
    f.append(fitbox(60, y1, 200, 52, "COMMAND_LONG\n33 байти тіла", size=13, fill=BAND))
    f.append(fitbox(bar_x, y1, u1 * 28, 52, "param1 … param7  (28 Б)", size=13, fill=SOFT))
    f.append(rect(bar_x + u1 * 28, y1, u1 * 2, 52, fill=GRAY, sw=1.2))
    f.append(rect(bar_x + u1 * 30, y1, u1 * 2, 52, fill=GREENFILL, stroke=FIELD, sw=2.4))
    f.append(rect(bar_x + u1 * 32, y1, u1 * 1, 52, fill=GRAY, sw=1.2))
    f.append(text(bar_x + u1 * 31, y1 - 16, "зсув 30–31", size=12, bold=True, color=FIELD))

    # рядок 2 — PARAM_SET (23 байти)
    n2 = 23.0
    u2 = bar_w / n2
    y2 = 510
    f.append(fitbox(60, y2, 200, 52, "PARAM_SET\n23 байти тіла", size=13, fill=BAND))
    f.append(fitbox(bar_x, y2, u2 * 4, 52, "param_value", size=12, fill=SOFT))
    f.append(rect(bar_x + u2 * 4, y2, u2 * 2, 52, fill=GREENFILL, stroke=FIELD, sw=2.4))
    f.append(fitbox(bar_x + u2 * 6, y2, u2 * 16, 52, "param_id  (16 Б)", size=13, fill=SOFT))
    f.append(rect(bar_x + u2 * 22, y2, u2 * 1, 52, fill=GRAY, sw=1.2))
    f.append(text(bar_x + u2 * 5, y2 - 16, "зсув 4–5", size=12, bold=True, color=FIELD))

    f.append(text(W / 2, 610,
                  "той самий сенс «кому» лежить у різних місцях: зсув маршрутизатор бере з таблиці, згенерованої з XML-опису",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "frame-addresses.svg"), W, H, *f)


# ─────────────── 2. Шлях кадру всередині станції ────────────────────────────
def fig_dispatch():
    W, H = 1200, 880
    f = []

    bx, bw = 70, 520          # головний ланцюг
    nx, nw = 660, 500         # колонка приміток
    bh = 74
    ys = [60, 178, 296, 414, 532, 650]

    boxes = [
        "MAVLinkProtocol::receiveBytes\nбайти → mavlink_parse_char(канал лінка, байт)",
        "кадр зібрано\nsysid і compid у заголовку — це ВІДПРАВНИК",
        "HEARTBEAT?  →  MultiVehicleManager",
        "emit messageReceived(link, message)\nкадр отримують УСІ об'єкти Vehicle",
        "Vehicle: message.sysid збігається з моїм?\nні → викинути",
        "розгалуження за compid усередині Vehicle",
    ]
    notes = [
        "у кожного з'єднання свій номер каналу розбору:\nнедозібрані кадри двох ліній не змішуються",
        "лічильник утрат ведеться по трійці\n(канал, sysid, compid) — у кожного компонента свій seq",
        "новий sysid, compid 1, тип не MAV_TYPE_GCS\n→ народжується новий Vehicle",
        "адресу ОДЕРЖУВАЧА тут не перевіряє ніхто",
        "виняток — RADIO_STATUS зі свого каналу:\nмодем має власний sysid, а доповідає про канал",
        None,
    ]

    for i, y in enumerate(ys):
        f.append(fitbox(bx, y, bw, bh, boxes[i], size=13, fill=SOFT))
        if notes[i]:
            f.append(fitbox(nx, y + 6, nw, bh - 12, notes[i], size=12, fill=BAND, sw=1.1))
            f.append(line(bx + bw, y + bh / 2, nx, y + bh / 2, color=MUTED, sw=1.1, dash="5 5"))
        if i:
            f.append(arrow(bx + bw / 2, ys[i - 1] + bh, bx + bw / 2, y))

    # віяло за compid
    fan_y = 780
    fan = [("compid 1\nавтопілот", 70, 200), ("compid 100–105\nкамери", 290, 200),
           ("compid 154\nпідвіс", 510, 200)]
    for lbl, fx, fw in fan:
        f.append(fitbox(fx, fan_y, fw, 66, lbl, size=13, fill=SOFT))
        f.append(arrow(fx + fw / 2, ys[5] + bh, fx + fw / 2, fan_y))
    f.append(fitbox(nx, fan_y, nw, 66,
                    "ParameterManager тримає окремий набір\nпараметрів на кожен compid", size=12, fill=BAND, sw=1.1))

    render(os.path.join(OUT, "dispatch-chain.svg"), W, H, *f)


# ─────────────── 3. Адреса не збігається з каналом ──────────────────────────
def fig_address_vs_link():
    W, H = 1220, 620
    f = []

    f.append(text(W / 2, 44, "Адреса живе в кадрі, а не в дроті", size=16, bold=True))

    # станція
    f.append(fitbox(60, 250, 250, 110, "QGroundControl\nsysid 255\ncompid 190", size=14, bold=True, fill=BAND))

    # канали
    f.append(fitbox(400, 170, 240, 60, "USB — серійний канал", size=13,
                    fill=GREENFILL, stroke=FIELD, sw=2.4))
    f.append(text(520, 156, "первинний", size=12, bold=True, color=FIELD))
    f.append(fitbox(400, 380, 240, 60, "UDP через модем", size=13, fill=SOFT))

    f.append(arrow(310, 288, 400, 205))
    f.append(arrow(310, 322, 400, 405))

    # апарат 1
    f.append(rect(730, 90, 430, 250, fill="#fbfcfd", sw=1.4))
    f.append(text(945, 122, "Апарат  sysid 1", size=14, bold=True))
    f.append(fitbox(760, 142, 370, 52, "compid 1 — автопілот", size=13, fill=SOFT))
    f.append(fitbox(760, 208, 370, 52, "compid 100 — камера", size=13, fill=SOFT))
    f.append(fitbox(760, 274, 370, 52, "compid 154 — підвіс", size=13, fill=SOFT))

    # апарат 2
    f.append(rect(730, 400, 430, 140, fill="#fbfcfd", sw=1.4))
    f.append(text(945, 432, "Апарат  sysid 2", size=14, bold=True))
    f.append(fitbox(760, 452, 370, 52, "compid 1 — автопілот", size=13, fill=SOFT))

    f.append(arrow(640, 200, 730, 200))
    f.append(arrow(640, 396, 730, 300))
    f.append(arrow(640, 414, 730, 470))

    f.append(text(W / 2, 592,
                  "той самий апарат приходить двома каналами: приймаємо з обох, шлемо — лише в первинний",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "address-vs-link.svg"), W, H, *f)


# ─────────────── 4. Таблиця досяжності маршрутизатора ───────────────────────
def fig_reach_table():
    W, H = 1320, 660
    f = []

    f.append(text(W / 2, 40, "Таблиця досяжності: її ніхто не налаштовує — вона намацується з трафіку",
                  size=16, bold=True))

    # кадр, про який ухвалюють рішення
    f.append(fitbox(390, 62, 540, 50,
                    "кадр COMMAND_LONG:  від 255/190,  адресовано 1/1",
                    size=14, bold=True, fill=GREENFILL, stroke=FIELD, sw=2.4))

    c1x, c1w = 60, 300
    c2x, c2w = 390, 490
    c3x, c3w = 910, 350

    f.append(text(c1x + c1w / 2, 152, "канал", size=13, bold=True, color=MUTED))
    f.append(text(c2x + c2w / 2, 152, "кого чули на цьому каналі (sysid/compid)",
                  size=13, bold=True, color=MUTED))
    f.append(text(c3x + c3w / 2, 152, "слати цей кадр сюди?", size=13, bold=True, color=MUTED))

    rows = [
        (176, "UART\nдо автопілота",
         "1/1 — автопілот\n1/100 — камера\n1/154 — підвіс",
         "ТАК", "систему 1 звідси чути", GREENFILL, FIELD),
        (316, "UDP\nдо наземної станції",
         "255/190 — QGroundControl",
         "НІ", "звідси кадр і прийшов", REDFILL, POS),
        (456, "TCP\nдо бортового логера",
         "порожньо: жодного кадру ще не було",
         "НІ", "системи 1 звідти не чули", REDFILL, POS),
    ]
    rh = 116
    for y, chan, seen, verdict, why, fill, stroke in rows:
        f.append(fitbox(c1x, y, c1w, rh, chan, size=14, fill=BAND))
        f.append(fitbox(c2x, y, c2w, rh, seen, size=14, fill=SOFT))
        f.append(fitbox(c3x, y, c3w, rh, verdict + "\n" + why, size=14, bold=True,
                        fill=fill, stroke=stroke, sw=2.2))

    f.append(text(W / 2, 616,
                  "жодних оголошень і жодного протоколу маршрутизації: рядок з'являється тоді, "
                  "коли на каналі почули цю пару чисел",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "router-reach-table.svg"), W, H, *f)


# ─────────────── 5. Рішення для одного вихідного каналу ─────────────────────
def fig_decision():
    W, H = 1300, 800
    f = []

    f.append(text(W / 2, 40, "Рішення ухвалюють окремо для КОЖНОГО вихідного каналу",
                  size=16, bold=True))

    qx, qw, qh = 70, 620, 78
    ox, ow, oh = 830, 400, 56
    ys = [80, 200, 320, 440, 560]

    steps = [
        ("це той самий канал, звідки кадр прийшов?",
         "ВИКИНУТИ\nназад у той самий дріт — ніколи", REDFILL, POS),
        ("джерело 'src_sys/src_comp' уже чули на цьому каналі?",
         "ВИКИНУТИ\nтам уже є цей кадр: інакше петля", REDFILL, POS),
        ("полів адресата немає або 'target_sys' дорівнює 0?",
         "НАДІСЛАТИ\nкадр широкомовний", GREENFILL, FIELD),
        ("'target_comp' ненульовий — цю пару чули на каналі?",
         "НАДІСЛАТИ\nадресат саме за цим каналом", GREENFILL, FIELD),
        ("'target_comp' нульовий — систему чули на каналі?",
         "НАДІСЛАТИ\nусім компонентам цієї системи", GREENFILL, FIELD),
    ]

    for i, (q, o, fill, stroke) in enumerate(steps):
        y = ys[i]
        f.append(fitbox(qx, y, qw, qh, q, size=14, fill=SOFT))
        f.append(fitbox(ox, y + (qh - oh) / 2, ow, oh, o, size=13, bold=True,
                        fill=fill, stroke=stroke, sw=2.2))
        f.append(arrow(qx + qw, y + qh / 2, ox, y + qh / 2, color=stroke))
        f.append(text((qx + qw + ox) / 2, y + qh / 2 - 14, "так", size=13, bold=True, color=stroke))
        if i:
            f.append(arrow(qx + qw / 2, ys[i - 1] + qh, qx + qw / 2, y))
            f.append(text(qx + qw / 2 - 34, (ys[i - 1] + qh + y) / 2 + 5, "ні", size=13, color=MUTED))

    fy = 680
    f.append(fitbox(qx, fy, qw, 62, "ВИКИНУТИ:  адресата з цього боку не чути",
                    size=14, bold=True, fill=REDFILL, stroke=POS, sw=2.2))
    f.append(arrow(qx + qw / 2, ys[4] + qh, qx + qw / 2, fy))
    f.append(text(qx + qw / 2 - 34, (ys[4] + qh + fy) / 2 + 5, "ні", size=13, color=MUTED))

    f.append(fitbox(ox, fy - 10, ow, 82,
                    "перші дві перевірки гасять петлю,\nтри наступні — лавину:\nбез них кадр летів би в усі канали",
                    size=13, fill=BAND, sw=1.1))

    render(os.path.join(OUT, "router-decision.svg"), W, H, *f)


# ─────────────── 6. Простір номерів систем (вставка api) ────────────────────
def fig_sysid_space():
    W, H = 1240, 440
    f = []
    BLUEFILL = "#e8eefc"

    f.append(text(W / 2, 44,
                  "Простір номерів систем: нуль недійсний, апарати ростуть від 1, станції — від 255 униз",
                  size=16, bold=True))

    x0, xw = 90, 1060
    u = xw / 255.0

    def X(v):
        return x0 + v * u

    f.append(rect(x0, 152, xw, 56, fill=BAND, sw=1.4))
    f.append(rect(X(0), 152, u * 1.8, 56, fill=REDFILL, stroke=POS, sw=2.0))

    f.append(arrow(X(1), 128, X(88), 128, color=FIELD, sw=2.2))
    f.append(text(X(44), 110, "апарати — від 1 вгору", size=13, bold=True, color=FIELD))
    f.append(arrow(X(255), 128, X(168), 128, color=NEG, sw=2.2))
    f.append(text(X(211), 110, "станції, SDK, скрипти — від 255 униз", size=13, bold=True, color=NEG))
    f.append(text(X(128), 110, "межу протокол не фіксує", size=12, color=MUTED))

    for v in (0, 1, 64, 128, 192, 255):
        f.append(line(X(v), 208, X(v), 222, color=MUTED, sw=1.2))
        f.append(text(X(v), 244, str(v), size=12, color=MUTED))

    cw, cy, ch = 356, 288, 112
    cards = [
        (70, X(0), REDFILL, POS,
         "0\nтільки як ЦІЛЬ — «усім».\nДжерелом бути не може: кадр\nіз sysid 0 станція відкидає"),
        (442, X(1), GREENFILL, FIELD,
         "1\nзаводське значення\nMAV_SYSID (ArduPilot)\nі MAV_SYS_ID (PX4)"),
        (814, X(255), BLUEFILL, NEG,
         "255\nзаводське значення\ngcsMavlinkSystemID у QGC\nі source_system у pymavlink"),
    ]
    for cx, tick, fill, stroke, label in cards:
        f.append(fitbox(cx, cy, cw, ch, label, size=13, fill=fill, stroke=stroke, sw=2.0))
        f.append(line(cx + cw / 2, cy, tick, 226, color=MUTED, sw=1.1, dash="5 5"))

    f.append(text(W / 2, 426,
                  "два діапазони ростуть назустріч один одному — і поки учасників мало, вони не зустрічаються",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "sysid-space.svg"), W, H, *f)


# ─────────────── 7. Карта зарезервованих номерів компонентів ────────────────
def fig_compid_map():
    W, H = 1240, 900
    f = []

    f.append(text(W / 2, 44, "Карта зарезервованих номерів компонентів (MAV_COMPONENT)",
                  size=16, bold=True))

    left = [
        (58, "norm", "0 — MAV_COMP_ID_ALL\nтільки як ціль: «усім компонентам»"),
        (58, "hi", "1 — MAV_COMP_ID_AUTOPILOT1\nлише з цим номером станція заводить апарат"),
        (34, "free", "2–24 — вільно"),
        (58, "norm", "25–99 — MAV_COMP_ID_USER1 … USER75\nприватні номери конкретної мережі"),
        (58, "hi", "68 — MAV_COMP_ID_TELEMETRY_RADIO\nєдиний зайнятий номер усередині USER-діапазону"),
        (58, "hi", "100–105 — MAV_COMP_ID_CAMERA … CAMERA6\nшість камер, кожна зі своїм номером"),
        (34, "free", "106–109 — вільно"),
        (46, "norm", "110–112 — MAV_COMP_ID_RADIO … RADIO3"),
        (34, "free", "113–139 — вільно"),
        (46, "norm", "140–153 — MAV_COMP_ID_SERVO1 … SERVO14"),
        (58, "norm", "154–158 — GIMBAL, LOG, ADSB,\nOSD, PERIPHERAL"),
    ]
    right = [
        (46, "norm", "160–161 — FLARM, PARACHUTE"),
        (46, "norm", "169 — WINCH — лебідка"),
        (46, "norm", "171–175 — GIMBAL2 … GIMBAL6"),
        (46, "norm", "180–181 — BATTERY, BATTERY2"),
        (46, "norm", "189 — MAVCAN — клієнт CAN поверх MAVLink"),
        (58, "hi", "190 — MAV_COMP_ID_MISSIONPLANNER\nтут сидить QGroundControl: стала коду, не налаштування"),
        (58, "norm", "191–194 — ONBOARD_COMPUTER1 … 4\nбортові комп'ютери"),
        (58, "norm", "195–198 — PATHPLANNER, OBSTACLE_AVOIDANCE,\nVISUAL_INERTIAL_ODOMETRY, PAIRING_MANAGER"),
        (46, "norm", "200–202 — IMU … IMU_3"),
        (46, "norm", "220–221 — GPS, GPS2"),
        (46, "norm", "236–238 — ODID_TXRX_1 … 3 — Open Drone ID"),
        (58, "norm", "240–243 — UDP_BRIDGE, UART_BRIDGE,\nTUNNEL_NODE, ILLUMINATOR"),
        (46, "free", "250 — SYSTEM_CONTROL — застаріле, замінене нулем"),
    ]

    def column(x, w, items):
        y = 84
        for h, kind, label in items:
            if kind == "hi":
                f.append(fitbox(x, y, w, h, label, size=13, bold=True,
                                fill=GREENFILL, stroke=FIELD, sw=2.2))
            elif kind == "free":
                f.append(fitbox(x, y, w, h, label, size=12, color=MUTED, fill=BAND, sw=1.1))
            else:
                f.append(fitbox(x, y, w, h, label, size=13, fill=SOFT))
            y += h + 10

    column(60, 540, left)
    column(640, 540, right)

    f.append(text(W / 2, 872,
                  "усе, що не зарезервоване, лишається вільним — але свої номери беруть із діапазону 25–99, "
                  "а не звідки заманеться",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "compid-map.svg"), W, H, *f)


fig_addresses()
fig_dispatch()
fig_address_vs_link()
fig_reach_table()
fig_decision()
fig_sysid_space()
fig_compid_map()
print("ok")
