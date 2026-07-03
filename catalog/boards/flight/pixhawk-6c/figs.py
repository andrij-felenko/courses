# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Pixhawk 6C — польотний контролер».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Архітектура: два процесори (FMU + IO) і давачі всередині ────────────────
def fig_architecture():
    W, H = 900, 560
    f = [text(W / 2, 30, "Усередині Pixhawk 6C: мозок (FMU) рахує, м'язи (IO) керують виходами",
              size=15.5, bold=True)]

    # межа плати
    bx, by, bw, bh = 40, 56, W - 80, 430
    f.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=MUTED, sw=1.6, rx=14))
    f.append(text(bx + 130, by + 22, "плата Pixhawk 6C", size=11.5, bold=True, color=MUTED))

    # ── блок давачів (ліворуч угорі) ──
    sx, sy, sw2, sh = bx + 30, by + 55, 220, 200
    f.append(rect(sx, sy, sw2, sh, fill="#eef6ef", stroke=FIELD, sw=1.7, rx=10))
    f.append(text(sx + sw2 / 2, sy + 24, "Давачі (на нагріві)", size=12, bold=True, color=FIELD))
    sensors = [
        "ICM-42688-P  — акселерометр+гіро",
        "BMI055/088   — другий акс.+гіро",
        "IST8310      — магнітометр",
        "MS5611       — барометр (тиск)",
    ]
    for i, s in enumerate(sensors):
        f.append(text(sx + 14, sy + 52 + i * 26, s, size=9.5, color=INK, anchor="start"))
    f.append(text(sx + sw2 / 2, sy + sh - 16, "два IMU — резервування",
                  size=9.5, italic=True, color=MUTED))

    # ── FMU (центр) ──
    fmx, fmy, fmw, fmh = bx + 300, by + 55, 240, 130
    f.append(rect(fmx, fmy, fmw, fmh, fill="#eaf0fd", stroke=NEG, sw=2.0, rx=10))
    f.append(text(fmx + fmw / 2, fmy + 26, "FMU  —  головний процесор", size=12, bold=True, color=NEG))
    f.append(text(fmx + fmw / 2, fmy + 50, "STM32H743", size=13, bold=True, color=INK))
    f.append(text(fmx + fmw / 2, fmy + 70, "Cortex-M7 · 480 МГц", size=10, color=INK))
    f.append(text(fmx + fmw / 2, fmy + 88, "2 МБ Flash · 1 МБ RAM", size=10, color=INK))
    f.append(text(fmx + fmw / 2, fmy + 112, "читає давачі, оцінює стан, рахує керування",
                  size=9, italic=True, color=MUTED))

    # ── IO (центр, нижче) ──
    iox, ioy, iow, ioh = bx + 300, by + 220, 240, 120
    f.append(rect(iox, ioy, iow, ioh, fill="#fdf0e6", stroke=POS, sw=2.0, rx=10))
    f.append(text(iox + iow / 2, ioy + 24, "IO  —  процесор виходів", size=12, bold=True, color=POS))
    f.append(text(iox + iow / 2, ioy + 47, "STM32F103", size=13, bold=True, color=INK))
    f.append(text(iox + iow / 2, ioy + 65, "Cortex-M3 · 72 МГц", size=10, color=INK))
    f.append(text(iox + iow / 2, ioy + 90, "жене PWM на мотори, ловить RC,",
                  size=9, italic=True, color=MUTED))
    f.append(text(iox + iow / 2, ioy + 104, "тримає керування при збої FMU",
                  size=9, italic=True, color=MUTED))

    # давачі → FMU
    f.append(arrow(sx + sw2, sy + 90, fmx, fmy + 60, color=FIELD, sw=2.2))
    f.append(text((sx + sw2 + fmx) / 2, sy + 66, "SPI / I²C", size=9.5, bold=True, color=FIELD))

    # FMU ↔ IO
    f.append(arrow(fmx + fmw / 2, fmy + fmh, iox + iow / 2, ioy, color=INK, sw=2.2))
    f.append(text(fmx + fmw / 2 + 44, (fmy + fmh + ioy) / 2 + 4, "команди", size=9.5, color=INK, anchor="start"))

    # ── виходи праворуч ──
    ox = bx + bw - 150
    # мотори від IO
    moty = ioy + ioh / 2
    f.append(rect(ox, moty - 34, 128, 68, fill=BG, stroke=INK, sw=1.6, rx=8))
    f.append(text(ox + 64, moty - 12, "16 × PWM", size=12, bold=True))
    f.append(text(ox + 64, moty + 8, "мотори (ESC)", size=10, color=INK))
    f.append(text(ox + 64, moty + 24, "серва", size=10, color=INK))
    f.append(arrow(iox + iow, moty, ox, moty, color=POS, sw=2.3))

    # RC вхід у IO
    rcy = ioy + ioh + 34
    f.append(rect(ox, rcy - 20, 128, 44, fill=BG, stroke=INK, sw=1.5, rx=8))
    f.append(text(ox + 64, rcy - 2, "RC-приймач", size=10.5, bold=True))
    f.append(text(ox + 64, rcy + 15, "SBUS / DSM / PPM", size=9, color=MUTED))
    f.append(arrow(ox, rcy, iox + iow, ioy + ioh - 18, color=INK, sw=1.8))

    # периферія від FMU
    fpy = fmy + fmh / 2
    f.append(rect(ox, fpy - 40, 128, 80, fill=BG, stroke=INK, sw=1.5, rx=8))
    f.append(text(ox + 64, fpy - 20, "GPS · телеметрія", size=10, bold=True))
    f.append(text(ox + 64, fpy - 3, "CAN · I²C · USB", size=10, bold=True))
    f.append(text(ox + 64, fpy + 16, "живлення (POWER)", size=9.5, color=MUTED))
    f.append(text(ox + 64, fpy + 32, "через JST-GH", size=9, italic=True, color=MUTED))
    f.append(arrow(fmx + fmw, fpy, ox, fpy, color=NEG, sw=2.0))

    b, _, _ = textbox(W / 2, H - 34,
                      "поділ праці: важкі обчислення — на швидкому FMU; примітивні, але критичні виходи — на окремому IO,\n"
                      "щоб мотори й ручне керування жили навіть коли головний процесор спіткнувся",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "architecture.svg"), W, H, *f)


# ── 2. Розводка портів: що куди підключати (пін-у-пін логіка) ──────────────────
def fig_wiring():
    W, H = 900, 600
    f = [text(W / 2, 30, "Розводка Pixhawk 6C: обов'язкове живлення й типова обв'язка дрона",
              size=15.5, bold=True)]

    # центральна плата
    bx, by, bw, bh = W / 2 - 130, 90, 260, 430
    f.append(rect(bx, by, bw, bh, fill="#eef2f8", stroke=INK, sw=2.0, rx=12))
    f.append(text(bx + bw / 2, by + 30, "Pixhawk 6C", size=15, bold=True))
    f.append(text(bx + bw / 2, by + 50, "84.8 × 44 × 12.4 мм", size=9.5, color=MUTED))

    # порти-мітки на платі (ліва й права колонки)
    left_ports = [
        ("POWER1", POS, "живлення + струм/напруга"),
        ("POWER2", POS, "резерв живлення"),
        ("GPS1", FIELD, "GPS + компас + кнопка"),
        ("I2C", FIELD, "зовн. компас / давачі"),
        ("CAN1/2", NEG, "розумна периферія"),
    ]
    right_ports = [
        ("PWM 1-8 (IO)", INK, "мотори / серва"),
        ("PWM 1-8 (FMU)", INK, "ще виходи"),
        ("TELEM1", NEG, "радіо-телеметрія"),
        ("TELEM2/3", NEG, "компаньйон-ПК"),
        ("USB-C", MUTED, "прошивка / налаштування"),
    ]

    ly0 = by + 80
    step = 62
    # ліві порти
    lx_label = bx - 24
    for i, (name, col, desc) in enumerate(left_ports):
        py = ly0 + i * step
        f.append(circle(bx, py, 5, fill=col, stroke=col))
        f.append(text(bx - 12, py - 8, name, size=11, bold=True, color=col, anchor="end"))
        # блок-адресат ліворуч
        tw = max(text_width(desc, 9.5), 150)
        box = rect(30, py - 17, tw + 16, 34, fill=BG, stroke=col, sw=1.4, rx=7)
        f.append(box)
        f.append(text(30 + (tw + 16) / 2, py + 4, desc, size=9.5, color=INK))
        f.append(line(30 + tw + 16, py, bx, py, color=col, sw=1.8))

    # праві порти
    for i, (name, col, desc) in enumerate(right_ports):
        py = ly0 + i * step
        f.append(circle(bx + bw, py, 5, fill=col, stroke=col))
        f.append(text(bx + bw + 12, py - 8, name, size=11, bold=True, color=col, anchor="start"))
        tw = max(text_width(desc, 9.5), 150)
        rxpos = W - 30 - (tw + 16)
        f.append(rect(rxpos, py - 17, tw + 16, 34, fill=BG, stroke=col, sw=1.4, rx=7))
        f.append(text(rxpos + (tw + 16) / 2, py + 4, desc, size=9.5, color=INK))
        f.append(line(bx + bw, py, rxpos, py, color=col, sw=1.8))

    b, _, _ = textbox(W / 2, H - 32,
                      "живлення — обов'язково через POWER1 (модуль міряє струм і напругу батареї); USB живить тільки\n"
                      "логіку, мотори від нього не крутяться. Усі роз'єми — JST-GH, переплутати важко",
                      size=10.5, fill="#fdf0e6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 3. Анатомія MAVLink-2-пакета (проти MAVLink 1) — до вставки proj-mavlink ────
def fig_mavlink_packet():
    W, H = 980, 470
    f = [text(W / 2, 30, "Кадр MAVLink 2: тонка обгортка навколо корисних байтів",
              size=15.5, bold=True)]

    fields = [
        ("STX", "0xFD", NEG, 66, "магія:\n1→0xFE, 2→0xFD"),
        ("LEN", "n", MUTED, 52, "довжина\nкорисних"),
        ("inc", "flags", "#8e44ad", 62, "несумісні\nпрапорці"),
        ("cmp", "flags", "#8e44ad", 62, "сумісні\nпрапорці"),
        ("SEQ", "0–255", MUTED, 64, "лічильник —\nловить утрату"),
        ("SYS", "sysid", POS, 64, "чий апарат\n(1 = автопілот)"),
        ("CMP", "compid", POS, 68, "який блок\n(1 = FMU)"),
        ("MSGID", "24 біт", FIELD, 74, "що це за\nповідомлення"),
        ("PAYLOAD", "0…255 Б", INK, 140, "самі дані:\nкоманда чи телеметрія"),
        ("CRC", "2 Б", MUTED, 56, "контроль\nцілості"),
        ("SIG", "13 Б?", "#c0392b", 62, "підпис —\nнеобов'язковий"),
    ]
    total = sum(w for *_, w, _ in fields)
    gap = 4
    x0 = (W - (total + gap * (len(fields) - 1))) / 2
    top = 100
    bh = 52
    x = x0
    for name, val, col, w, desc in fields:
        f.append(rect(x, top, w, bh, fill=BG, stroke=col, sw=2.0, rx=6))
        f.append(text(x + w / 2, top + 21, name, size=11, bold=True, color=col))
        f.append(text(x + w / 2, top + 39, val, size=10, color=INK))
        for i, ln in enumerate(desc.split("\n")):
            f.append(text(x + w / 2, top + bh + 26 + i * 15, ln, size=9, color=MUTED))
        x += w + gap

    hdr_w = sum(w for *_, w, _ in fields[:8]) + gap * 7
    hy = top - 18
    f.append(line(x0, hy, x0 + hdr_w, hy, color=INK, sw=1.4))
    f.append(line(x0, hy, x0, hy + 8, color=INK, sw=1.4))
    f.append(line(x0 + hdr_w, hy, x0 + hdr_w, hy + 8, color=INK, sw=1.4))
    f.append(text(x0 + hdr_w / 2, hy - 7, "заголовок (10 байтів) — маршрутизація й версія",
                  size=10, bold=True, color=INK))

    b, _, _ = textbox(W / 2, H - 44,
                      "уся «розмова» з дроном — потік таких кадрів. MAVLink 1 (0xFE) не має полів прапорців і підпису й шле весь\n"
                      "хвіст payload; MAVLink 2 (0xFD) додав їх і обрізає нульові байти з кінця. Бібліотека, що чекає іншу магію, кадру НЕ побачить.",
                      size=10, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "mavlink-packet.svg"), W, H, *f)


# ── 4. Послідовність керування: від порту до зльоту ────────────────────────────
def fig_mavlink_sequence():
    W, H = 640, 720
    f = [text(W / 2, 30, "Порядок керування Pixhawk по MAVLink: кроки не міняються місцями",
              size=14.5, bold=True)]

    steps = [
        ("1. Відкрити порт", NEG,
         "serial://COM3:921600   або   udp://:14540", "з'єднання ще німе"),
        ("2. Дочекатися heartbeat", FIELD,
         "wait_heartbeat() → знаємо sysid / compid", "лінія жива"),
        ("3. Задати режим", "#8e44ad",
         "GUIDED (ArduPilot)  /  SET_MODE+custom (PX4)", "апарат слухає команди"),
        ("4. Зброїти", POS,
         "MAV_CMD_COMPONENT_ARM_DISARM, param1 = 1", "мотори під напругою"),
        ("5. Злетіти / дати команду", POS,
         "MAV_CMD_NAV_TAKEOFF   або   action.takeoff()", "апарат у повітрі"),
        ("6. Читати стан", INK,
         "recv_match('ATTITUDE' / 'GLOBAL_POSITION_INT')", "телеметрія тече назад"),
    ]

    bx, bw = 70, W - 140
    y = 70
    bh = 78
    vgap = 26
    for i, (title, col, code, note) in enumerate(steps):
        f.append(rect(bx, y, bw, bh, fill=BG, stroke=col, sw=2.0, rx=10))
        f.append(text(bx + 18, y + 26, title, size=13, bold=True, color=col, anchor="start"))
        f.append(text(bx + 18, y + 48, code, size=10.5, color=INK, anchor="start"))
        f.append(text(bx + 18, y + 66, "→ " + note, size=9.5, italic=True, color=MUTED, anchor="start"))
        if i < len(steps) - 1:
            f.append(arrow(bx + bw / 2, y + bh, bx + bw / 2, y + bh + vgap, color=INK, sw=2.2))
        y += bh + vgap

    b, _, _ = textbox(W / 2, H - 34,
                      "кожен крок відкриває наступний: без heartbeat не знаєш адреси; поза потрібним режимом команду відкинуть;\n"
                      "не зброївши — не злетиш. А зброєння впаде, поки не знято кнопку-запобіжник.",
                      size=10, fill="#fdf0e6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "mavlink-sequence.svg"), W, H, *f)


# ── 5. Дві бібліотеки: рівень абстракції ───────────────────────────────────────
def fig_mavlink_libraries():
    W, H = 920, 470
    f = [text(W / 2, 30, "Два шляхи до тієї самої плати: готові дії проти сирих пакетів",
              size=15.5, bold=True)]

    lx, lw = 60, 370
    top = 66
    f.append(rect(lx, top, lw, 300, fill="#eaf0fd", stroke=NEG, sw=2.0, rx=12))
    f.append(text(lx + lw / 2, top + 28, "MAVSDK (C++)", size=14, bold=True, color=NEG))
    f.append(text(lx + lw / 2, top + 48, "високий рівень: думаєш діями", size=10, italic=True, color=MUTED))
    litems = [
        ("action.arm();", False),
        ("action.takeoff();", False),
        ("telemetry.subscribe_position(...)", False),
        ("— бібліотека сама шле пакети,", True),
        ("   чекає COMMAND_ACK, повторює", True),
    ]
    for i, (s, it) in enumerate(litems):
        f.append(text(lx + 22, top + 86 + i * 30, s, size=11,
                      color=MUTED if it else INK, italic=it, anchor="start"))
    f.append(text(lx + lw / 2, top + 300 - 16, "менше коду, менше контролю над байтами",
                  size=9.5, italic=True, color=NEG))

    rx, rw = 490, 370
    f.append(rect(rx, top, rw, 300, fill="#eef6ef", stroke=FIELD, sw=2.0, rx=12))
    f.append(text(rx + rw / 2, top + 28, "pymavlink (Python)", size=14, bold=True, color=FIELD))
    f.append(text(rx + rw / 2, top + 48, "низький рівень: думаєш пакетами", size=10, italic=True, color=MUTED))
    ritems = [
        ("m.mav.command_long_send(", False),
        ("     MAV_CMD_COMPONENT_ARM_DISARM, …)", False),
        ("m.recv_match('ATTITUDE', blocking=True)", False),
        ("— сам будуєш кожне повідомлення,", True),
        ("   сам ловиш і читаєш відповідь", True),
    ]
    for i, (s, it) in enumerate(ritems):
        f.append(text(rx + 22, top + 86 + i * 30, s, size=10.5,
                      color=MUTED if it else INK, italic=it, anchor="start"))
    f.append(text(rx + rw / 2, top + 300 - 16, "бачиш кожен байт, платиш ручною роботою",
                  size=9.5, italic=True, color=FIELD))

    b, _, _ = textbox(W / 2, H - 44,
                      "обидві говорять тим самим MAVLink і з тією самою платою. MAVSDK ховає пакети за готовими діями (arm/takeoff) —\n"
                      "швидко для звичайних сценаріїв; pymavlink віддає сирі повідомлення — коли треба нестандартне чи зазирнути в кожен байт.",
                      size=10, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "mavlink-libraries.svg"), W, H, *f)


if __name__ == "__main__":
    fig_architecture()
    fig_wiring()
    fig_mavlink_packet()
    fig_mavlink_sequence()
    fig_mavlink_libraries()
    print("OK: 5 figures ->", IMG)
