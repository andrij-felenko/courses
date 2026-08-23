# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Спільні відтінки для цих фігур (поверх палітри svgkit)
RX_FILL = "#eef4ff"   # «приймаємо» — холодне
RX_STK  = "#c9d6f0"
TX_FILL = "#fdecea"   # «шлемо» — гаряче
TX_STK  = "#e7b6b0"
OK_FILL = "#eafaf1"   # підтвердження
OK_STK  = "#bfe6cf"


# ── receive: байти → парсер → готові повідомлення з полями ────────────────────
# Ідея: код не торкається байтів — парсер віддає об'єкт із полями. Спершу
# дочекатися HEARTBEAT (адреса апарата), далі брати потрібні повідомлення.
def fig_receive():
    W, H = 760, 300
    p = []
    p.append(text(W/2, 30, "Приймання: байти стають готовими повідомленнями", size=16, bold=True))

    # потік байтів
    bx, by = 40, 95
    p.append(text(bx, by - 16, "лінк (UART / USB / UDP)", size=12, color=MUTED, anchor="start"))
    raw = "FD 1C 00 ... 1E 5C"
    for i, ch in enumerate(["FD", "1C", "00", "07", "..", "5C"]):
        cx = bx + i * 30
        p.append(rect(cx, by, 26, 26, fill="#f0f0f0", stroke=MUTED, sw=1.0, rx=3))
        p.append(text(cx + 13, by + 18, ch, size=11, color=INK))
    p.append(arrow(bx + 6*30 + 4, by + 13, bx + 6*30 + 44, by + 13, color=INK))

    # парсер
    pb, _, _ = textbox(bx + 6*30 + 44 + 95, by + 13, "парсер\nMAVLink", size=14, bold=True,
                       fill=FILL, stroke=LINE, min_w=130)
    p.append(pb)
    px2 = bx + 6*30 + 44 + 95 + 65
    p.append(text(px2 - 65, by + 52, "збирає кадр, звіряє CRC", size=11, color=MUTED))
    p.append(arrow(px2 + 6, by + 13, px2 + 46, by + 13, color=INK))

    # готовий об'єкт із полями
    ox = px2 + 52
    msg_lines = ["msg = ATTITUDE", "  msg.roll  = 0.03", "  msg.pitch = -0.11", "  msg.yaw   = 1.57"]
    ob = fitbox(ox, by - 26, 235, 92, "\n".join(msg_lines), size=12, fill=RX_FILL, stroke=RX_STK)
    p.append(ob)
    p.append(text(ox + 117, by + 86, "поля вже розкладені — байти не чіпаємо", size=11, color=MUTED))

    # нижче: послідовність дій
    sy = 215
    steps = ["1. дочекатися HEARTBEAT", "2. у циклі брати потрібний тип", "3. читати готові поля"]
    sx = 40
    for i, s in enumerate(steps):
        b = fitbox(sx, sy, 215, 44, s, size=12, fill=OK_FILL if i == 0 else FILL,
                   stroke=OK_STK if i == 0 else LINE)
        p.append(b)
        if i < 2:
            p.append(arrow(sx + 219, sy + 22, sx + 233, sy + 22, color=INK))
        sx += 233
    render(os.path.join(OUT, "receive.svg"), W, H, *p)


# ── request: апарат мовчить, поки потік не замовлено ──────────────────────────
# Ідея: канал вузький, тож апарат не шле все підряд; SET_MESSAGE_INTERVAL вмикає
# конкретне повідомлення з потрібною частотою (стара дорога — REQUEST_DATA_STREAM).
def fig_request():
    W, H = 760, 290
    p = []
    p.append(text(W/2, 30, "Спершу замов: апарат не транслює все підряд", size=16, bold=True))

    gcs_x, veh_x, midy = 150, 610, 150
    gb, _, _ = textbox(gcs_x, midy, "твій код", size=14, bold=True, min_w=150)
    vb, _, _ = textbox(veh_x, midy, "апарат", size=14, bold=True, min_w=150)
    p.append(gb); p.append(vb)

    # запит праворуч
    p.append(arrow(gcs_x + 80, midy - 22, veh_x - 80, midy - 22, color=POS, sw=2.0))
    p.append(text(W/2, midy - 30, "SET_MESSAGE_INTERVAL  (ATTITUDE, 100 ms)", size=12.5, color=POS, bold=True))

    # потік ліворуч
    p.append(arrow(veh_x - 80, midy + 26, gcs_x + 80, midy + 26, color=FIELD, sw=2.0))
    p.append(text(W/2, midy + 44, "ATTITUDE  · ATTITUDE · ATTITUDE …  (10 раз/с)", size=12.5, color=FIELD, bold=True))

    # підпис-наслідок
    note = "Не замовив — повідомлення «немає». Критичне — частіше, фонове — рідше,\nщоб не перевантажити вузький канал телеметрії."
    p.append(mtext(W/2, 235, note, size=12, color=MUTED))
    render(os.path.join(OUT, "request.svg"), W, H, *p)


# ── command-ack: COMMAND_LONG → виконання → COMMAND_ACK з результатом ──────────
# Ідея: команда — це повідомлення з ID і 7 параметрами; апарат мусить відповісти
# ACK із кодом результату. Без перевірки ACK не знаєш, чи команда дійшла.
def fig_command_ack():
    W, H = 760, 330
    p = []
    p.append(text(W/2, 30, "Команда → обов'язкове підтвердження", size=16, bold=True))

    gcs_x, veh_x, midy = 150, 610, 140
    gb, _, _ = textbox(gcs_x, midy, "твій код", size=14, bold=True, min_w=150)
    vb, _, _ = textbox(veh_x, midy, "апарат", size=14, bold=True, min_w=150)
    p.append(gb); p.append(vb)

    p.append(arrow(gcs_x + 80, midy - 18, veh_x - 80, midy - 18, color=POS, sw=2.0))
    p.append(text(W/2, midy - 26, "COMMAND_LONG: command=MAV_CMD_…, param1..7", size=12, color=POS, bold=True))

    p.append(arrow(veh_x - 80, midy + 22, gcs_x + 80, midy + 22, color=FIELD, sw=2.0))
    p.append(text(W/2, midy + 40, "COMMAND_ACK: result = ?", size=12, color=FIELD, bold=True))

    # три можливі результати
    ry = 235
    res = [("ACCEPTED", "виконано", OK_FILL, OK_STK),
           ("DENIED / TEMPORARILY_REJECTED", "відмовлено — апарат не готовий", "#fef6e7", "#e9d8a6"),
           ("FAILED", "почав, але не вдалося", TX_FILL, TX_STK)]
    rx = 40
    for name, desc, fl, st in res:
        b = fitbox(rx, ry, 225, 56, name + "\n" + desc, size=11.5, fill=fl, stroke=st)
        p.append(b)
        rx += 235
    p.append(text(W/2, 315, "ACK не прийшов → збільш confirmation і повтори ту саму команду", size=11.5, color=MUTED))
    render(os.path.join(OUT, "command-ack.svg"), W, H, *p)


# ── commands: чотири щоденні команди, усі через COMMAND_LONG + ACK ─────────────
def fig_commands():
    W, H = 760, 300
    p = []
    p.append(text(W/2, 30, "Чотири щоденні команди (усі — COMMAND_LONG з ACK)", size=16, bold=True))

    cards = [
        ("ARM / DISARM", "MAV_CMD_COMPONENT_ARM_DISARM", "param1 = 1 / 0 — мотори", TX_FILL, TX_STK),
        ("Режим", "MAV_CMD_DO_SET_MODE", "STABILIZE · LOITER · AUTO · RTL", FILL, LINE),
        ("Зліт", "MAV_CMD_NAV_TAKEOFF", "param7 = висота, м", FILL, LINE),
        ("Додому (RTL)", "MAV_CMD_NAV_RETURN_TO_LAUNCH", "повернутися й сісти", OK_FILL, OK_STK),
    ]
    cw, ch, gap = 340, 92, 24
    x0 = (W - (2*cw + gap)) / 2
    for i, (ttl, cmd, sub, fl, st) in enumerate(cards):
        col, row = i % 2, i // 2
        x = x0 + col * (cw + gap)
        y = 60 + row * (ch + gap)
        p.append(rect(x, y, cw, ch, fill=fl, stroke=st, sw=1.5))
        p.append(text(x + 16, y + 26, ttl, size=14, bold=True, anchor="start"))
        p.append(text(x + 16, y + 50, cmd, size=12, color=NEG, anchor="start"))
        p.append(text(x + 16, y + 72, sub, size=11.5, color=MUTED, anchor="start"))
    p.append(text(W/2, 292, "Кожна реально рухає апарат — спершу симулятор чи стенд", size=11.5, color=MUTED))
    render(os.path.join(OUT, "commands.svg"), W, H, *p)


# ── params: read/write параметрів, обидва — з підтвердженням PARAM_VALUE ───────
def fig_params():
    W, H = 760, 300
    p = []
    p.append(text(W/2, 30, "Параметри: читання й запис — теж із підтвердженням", size=16, bold=True))

    gcs_x, veh_x = 150, 610
    # читання
    ry = 110
    p.append(text(gcs_x, ry - 34, "ПРОЧИТАТИ", size=12, color=NEG, bold=True, anchor="start"))
    gb, _, _ = textbox(gcs_x, ry, "твій код", size=13, bold=True, min_w=150)
    vb, _, _ = textbox(veh_x, ry, "апарат", size=13, bold=True, min_w=150)
    p.append(gb); p.append(vb)
    p.append(arrow(gcs_x + 80, ry - 16, veh_x - 80, ry - 16, color=POS, sw=1.8))
    p.append(text(W/2, ry - 24, "PARAM_REQUEST_READ (WPNAV_SPEED)", size=11.5, color=POS, bold=True))
    p.append(arrow(veh_x - 80, ry + 18, gcs_x + 80, ry + 18, color=FIELD, sw=1.8))
    p.append(text(W/2, ry + 34, "PARAM_VALUE = 500", size=11.5, color=FIELD, bold=True))

    # запис
    wy = 220
    p.append(text(gcs_x, wy - 30, "ЗАПИСАТИ", size=12, color=NEG, bold=True, anchor="start"))
    gb2, _, _ = textbox(gcs_x, wy, "твій код", size=13, bold=True, min_w=150)
    vb2, _, _ = textbox(veh_x, wy, "апарат", size=13, bold=True, min_w=150)
    p.append(gb2); p.append(vb2)
    p.append(arrow(gcs_x + 80, wy - 16, veh_x - 80, wy - 16, color=POS, sw=1.8))
    p.append(text(W/2, wy - 24, "PARAM_SET (WPNAV_SPEED = 700)", size=11.5, color=POS, bold=True))
    p.append(arrow(veh_x - 80, wy + 18, gcs_x + 80, wy + 18, color=FIELD, sw=1.8))
    p.append(text(W/2, wy + 34, "PARAM_VALUE = 700  ← підтвердив новим значенням", size=11.5, color=FIELD, bold=True))
    render(os.path.join(OUT, "params.svg"), W, H, *p)


# ── mission: завантаження маршруту як рукостискання пункт за пунктом ───────────
def fig_mission():
    W, H = 760, 320
    p = []
    p.append(text(W/2, 30, "Завантаження місії: рукостискання пункт за пунктом", size=16, bold=True))

    gcs_x, veh_x = 150, 610
    rows = [
        ("MISSION_COUNT = N", POS, "→"),
        ("MISSION_REQUEST_INT  0", FIELD, "←"),
        ("MISSION_ITEM_INT  0", POS, "→"),
        ("MISSION_REQUEST_INT  1", FIELD, "←"),
        ("MISSION_ITEM_INT  1", POS, "→"),
        ("MISSION_ACK  (усе прийнято)", FIELD, "←"),
    ]
    gb, _, _ = textbox(gcs_x, 70, "станція", size=13, bold=True, min_w=150)
    vb, _, _ = textbox(veh_x, 70, "апарат", size=13, bold=True, min_w=150)
    p.append(gb); p.append(vb)
    y = 120
    for label, color, direction in rows:
        if direction == "→":
            p.append(arrow(gcs_x + 80, y, veh_x - 80, y, color=color, sw=1.8))
        else:
            p.append(arrow(veh_x - 80, y, gcs_x + 80, y, color=color, sw=1.8))
        p.append(text(W/2, y - 7, label, size=11.5, color=color, bold=True))
        y += 30
    p.append(text(W/2, y + 6, "Кожна точка підтверджена — жодна не загубиться", size=11.5, color=MUTED))
    render(os.path.join(OUT, "mission.svg"), W, H, *p)


# ── sitl: трирівневий шлях навчання — симулятор → стенд → політ ────────────────
def fig_sitl():
    W, H = 760, 300
    p = []
    p.append(text(W/2, 30, "Безпечний шлях: симулятор → стенд → політ", size=16, bold=True))

    stages = [
        ("SITL", "віртуальний апарат у комп'ютері;\nMAVLink справжній, збити нічого", OK_FILL, OK_STK),
        ("Стенд", "реальна плата, гвинти зняті;\nмотори крутяться, не злетить", "#fef6e7", "#e9d8a6"),
        ("Політ", "відкрите безпечне місце,\nдалеко від людей", TX_FILL, TX_STK),
    ]
    cw, ch, gap = 210, 110, 30
    x0 = (W - (3*cw + 2*gap)) / 2
    y = 90
    for i, (ttl, sub, fl, st) in enumerate(stages):
        x = x0 + i * (cw + gap)
        p.append(rect(x, y, cw, ch, fill=fl, stroke=st, sw=1.6))
        p.append(text(x + cw/2, y + 30, ttl, size=15, bold=True))
        p.append(mtext(x + cw/2, y + 56, sub, size=11.5, color=INK))
        if i < 2:
            p.append(arrow(x + cw + 4, y + ch/2, x + cw + gap - 4, y + ch/2, color=INK, sw=2.0))
    p.append(text(W/2, 250, "Кожна команда реально рухає апарат — гвинти востаннє", size=12, color=MUTED))
    render(os.path.join(OUT, "sitl.svg"), W, H, *p)


if __name__ == "__main__":
    fig_receive()
    fig_request()
    fig_command_ack()
    fig_commands()
    fig_params()
    fig_mission()
    fig_sitl()
    print("OK figs ->", OUT)
