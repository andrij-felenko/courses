# -*- coding: utf-8 -*-
"""Фігури теми «Проєктування місії (вейпойнти)». Чистий Python + svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
def out(name): return os.path.join(IMG, name)


# ── 1) item.svg — анатомія MISSION_ITEM_INT ─────────────────────────────────
def fig_item():
    W, H = 760, 360
    frags = []
    top = 64
    rows = [
        ("seq",          "номер пункту в списку",            MUTED),
        ("frame",        "система відліку висоти",           FIELD),
        ("command",      "ЩО робити (MAV_CMD) — задає сенс решти", POS),
        ("current / autocontinue", "поточний? і йти далі сам?", MUTED),
        ("param1 … param4", "аргументи; зміст залежить від command", INK),
        ("param5 = широта × 10⁷", "ціле — без втрати метрів", NEG),
        ("param6 = довгота × 10⁷", "ціле — без втрати метрів", NEG),
        ("param7 = висота",  "метри (від чого — каже frame)", FIELD),
    ]
    rh = 34
    x = 40
    w = W - 2 * x
    frags.append(text(W / 2, 32, "MISSION_ITEM_INT — анатомія елемента місії", size=17, bold=True))
    for i, (name, desc, col) in enumerate(rows):
        y = top + i * rh
        frags.append(rect(x, y, w, rh - 6, fill=FILL, stroke=LINE, sw=1.2))
        frags.append(text(x + 14, y + (rh - 6) / 2 + 5, name, size=14, color=col, anchor="start", bold=True))
        frags.append(text(x + w - 14, y + (rh - 6) / 2 + 5, desc, size=12.5, color=MUTED, anchor="end"))
    # підкреслення: три «координатні» поля
    yb = top + 5 * rh
    frags.append(line(x - 8, yb, x - 8, yb + 3 * rh - 6, color=NEG, sw=3))
    frags.append(text(x - 14, yb + (3 * rh - 6) / 2, "позиція", size=11.5, color=NEG, anchor="end"))
    render(out("item.svg"), W, H, *frags)


# ── 2) frames.svg — три системи відліку висоти ──────────────────────────────
def fig_frames():
    W, H = 760, 380
    frags = []
    frags.append(text(W / 2, 30, "«50 метрів» — від чого? Три системи відліку (frame)", size=16, bold=True))

    ground = 318          # лінія рельєфу (базова)
    sea = 348             # рівень моря
    # рівень моря
    frags.append(line(40, sea, W - 40, sea, color=NEG, sw=2, dash="6 5"))
    frags.append(text(W - 44, sea + 16, "рівень моря (MSL)", size=11.5, color=NEG, anchor="end"))

    # рельєф: рівнина ліворуч, пагорб праворуч
    pts = [(40, ground), (300, ground), (430, ground - 70), (560, ground - 70),
           (650, ground - 30), (W - 40, ground - 30)]
    d = "M %.0f %.0f " % pts[0] + " ".join("L %.0f %.0f" % p for p in pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d, "#8a6d3b"))
    frags.append('<path d="%s L %d %d L 40 %d Z" fill="#efe6d6" stroke="none" opacity="0.7"/>'
                 % (d, W - 40, ground + 30, ground + 30))

    def drone(cx, cy, label, lab_col):
        s = circle(cx, cy, 9, fill="#eaf0fd", stroke=NEG, sw=2)
        s += line(cx - 14, cy, cx + 14, cy, color=NEG, sw=2)
        s += text(cx, cy - 16, label, size=12, color=lab_col, anchor="middle", bold=True)
        return s

    # GLOBAL: 50 м над рівнем моря (ліворуч, над рівниною) — низько
    gx = 150
    gy = sea - 50  # умовний масштаб: 50м ≈ 50px
    frags.append(drone(gx, gy, "GLOBAL", POS))
    frags.append(line(gx, gy + 9, gx, sea, color=POS, sw=1.4, dash="3 3"))
    frags.append(text(gx + 8, (gy + sea) / 2, "50 м", size=11, color=POS, anchor="start"))

    # RELATIVE_ALT: 50 м над домівкою (над рівниною, де злетів)
    hx = 235
    home_y = ground
    rel_y = home_y - 50
    frags.append(text(hx, home_y + 16, "домівка", size=10.5, color=FIELD, anchor="middle"))
    frags.append(circle(hx, home_y, 4, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(drone(hx, rel_y, "RELATIVE_ALT", FIELD))
    frags.append(line(hx, rel_y + 9, hx, home_y, color=FIELD, sw=1.4, dash="3 3"))
    frags.append(text(hx + 8, (rel_y + home_y) / 2, "50 м", size=11, color=FIELD, anchor="start"))

    # TERRAIN_ALT: 50 м над рельєфом — над пагорбом
    tx = 495
    ter_ground = ground - 70
    ter_y = ter_ground - 50
    frags.append(drone(tx, ter_y, "TERRAIN_ALT", INK))
    frags.append(line(tx, ter_y + 9, tx, ter_ground, color=INK, sw=1.4, dash="3 3"))
    frags.append(text(tx + 8, (ter_y + ter_ground) / 2, "50 м", size=11, color=INK, anchor="start"))

    render(out("frames.svg"), W, H, *frags)


# ── 3) commands.svg — палітра команд місії ──────────────────────────────────
def fig_commands():
    W, H = 760, 340
    frags = []
    frags.append(text(W / 2, 30, "Палітра команд місії: NAV_* рухають, DO_* налаштовують", size=16, bold=True))

    nav = [
        ("NAV_TAKEOFF", "22", "зліт на висоту"),
        ("NAV_WAYPOINT", "16", "летіти до точки"),
        ("NAV_LOITER_TIME", "19", "кружляти над точкою"),
        ("NAV_LAND", "21", "сісти в точці"),
        ("NAV_RETURN_TO_LAUNCH", "20", "повернутися додому"),
    ]
    do = [
        ("DO_CHANGE_SPEED", "—", "задати швидкість"),
        ("DO_JUMP", "—", "стрибок → цикл у місії"),
    ]
    bx, by = 40, 70
    bw, bh, gap = 218, 50, 14

    def card(x, y, name, idn, desc, col, fill):
        s = rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.6)
        s += text(x + 12, y + 20, name, size=13, color=col, anchor="start", bold=True)
        s += text(x + bw - 12, y + 20, "ID " + idn, size=11, color=MUTED, anchor="end")
        s += text(x + 12, y + 39, desc, size=12, color=INK, anchor="start")
        return s

    frags.append(text(bx, by - 8, "NAV_* — переміщення (по черзі):", size=12.5, color=NEG, anchor="start", bold=True))
    for i, (n, idn, dsc) in enumerate(nav):
        col = i % 2
        x = bx + col * (bw + gap)
        y = by + (i // 2) * (bh + gap)
        frags.append(card(x, y, n, idn, dsc, NEG, "#eef3fe"))

    rx = bx + 2 * (bw + gap)
    frags.append(text(rx, by - 8, "DO_* — дії та переходи:", size=12.5, color=POS, anchor="start", bold=True))
    for i, (n, idn, dsc) in enumerate(do):
        y = by + i * (bh + gap)
        frags.append(card(rx, y, n, idn, dsc, POS, "#fdecea"))

    # стрілка циклу від DO_JUMP назад
    jy = by + 1 * (bh + gap) + bh / 2
    frags.append(text(rx, by + 2 * (bh + gap) + 6, "DO_JUMP → пункт N, K разів", size=11.5, color=POS, anchor="start"))
    frags.append('<path d="M %d %d q -40 40 0 80" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 3" marker-end="url(#arrow)"/>'
                 % (rx, jy + 16, POS))

    render(out("commands.svg"), W, H, *frags)


# ── 4) radius.svg — радіус прийняття й форма повороту ───────────────────────
def fig_radius():
    W, H = 760, 360
    frags = []
    frags.append(text(W / 2, 30, "Радіус прийняття ліпить форму повороту", size=16, bold=True))

    def scene(ox, title, R, cut):
        f = [text(ox + 150, 64, title, size=13.5, bold=True)]
        # три точки кутом
        A = (ox + 30, 300)
        B = (ox + 150, 110)   # вершина кута
        C = (ox + 270, 300)
        for p, lab in ((A, "A"), (B, "B"), (C, "C")):
            f.append(circle(p[0], p[1], 5, fill=INK, stroke=INK, sw=1))
            f.append(text(p[0], p[1] - 12 if p is B else p[1] + 20, lab, size=13, bold=True))
        # ідеальні ланки (пунктир)
        f.append(line(A[0], A[1], B[0], B[1], color=MUTED, sw=1.2, dash="4 4"))
        f.append(line(B[0], B[1], C[0], C[1], color=MUTED, sw=1.2, dash="4 4"))
        # сфера прийняття навколо B
        f.append(circle(B[0], B[1], R, fill="none", stroke=FIELD, sw=1.6))
        f.append(text(B[0] + R + 4, B[1], "R", size=12, color=FIELD, anchor="start", bold=True))
        # фактична траєкторія: квадратична крива, що зрізає кут на величину cut
        mid = (B[0], B[1] + cut)   # контрольна точка нижче вершини = зріз
        f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (A[0], A[1], mid[0], mid[1], C[0], C[1], POS))
        return f

    frags += scene(20, "малий радіус — точно, але смикано", 20, 20)
    frags += scene(400, "великий радіус — плавно, але повз точку", 64, 95)
    frags.append(text(W / 2, H - 14, "червона лінія — фактичний політ; зелене коло — сфера, вхід у яку зараховує точку",
                      size=11.5, color=MUTED))
    render(out("radius.svg"), W, H, *frags)


# ── 5) waypoint-history.svg — чотири кроки ідеї «машина пройде маршрут сама» ─
def fig_waypoint_history():
    W, H = 820, 380
    frags = []
    frags.append(text(W / 2, 30, "Дорога до вейпойнта: чотири способи «знати, де я» без людини", size=16, bold=True))

    axis_y = 250
    frags.append(line(40, axis_y, W - 40, axis_y, color=MUTED, sw=1.5))

    steps = [
        ("1914", "Гіроавтопілот\nСперрі", "тримає РІВЕНЬ,\nале не знає, ДЕ він", NEG),
        ("1940-50-ті", "Інерціальна\nнавігація (INS)", "числить шлях сама —\nале ДРЕЙФ росте з часом", POS),
        ("1950-ті →", "TERCOM:\nприв'язка до рельєфу", "звіряє висоту з картою —\nгасить дрейф над землею", FIELD),
        ("2000 →", "GNSS\n(GPS і сузір'я)", "точка на кулі стала\nВИМІРНОЮ — метри будь-де", INK),
    ]
    n = len(steps)
    x0, x1 = 110, W - 110
    for i, (yr, name, note, col) in enumerate(steps):
        cx = x0 + (x1 - x0) * i / (n - 1)
        # вузол на осі
        frags.append(circle(cx, axis_y, 7, fill="#ffffff", stroke=col, sw=2.5))
        frags.append(text(cx, axis_y + 26, yr, size=12.5, color=col, bold=True))
        # назва над віссю
        frags.append(mtext(cx, 86, name, size=13, color=col, bold=True, lh=1.25))
        # стрілка від назви до вузла
        frags.append(line(cx, 118, cx, axis_y - 9, color=col, sw=1.2, dash="3 3"))
        # нотатка нижче року
        frags.append(mtext(cx, axis_y + 52, note, size=11, color=MUTED, lh=1.3))

    # підпис «наростання якості плану» стрілкою вздовж осі
    frags.append('<path d="M %d %d L %d %d" fill="none" stroke="%s" stroke-width="1.6" '
                 'marker-end="url(#arrow)"/>' % (x0 - 30, axis_y - 150, x1 + 18, axis_y - 150, INK))
    frags.append(text(W / 2, axis_y - 158, "план із координат стає дедалі надійніше «літати»",
                      size=11.5, color=INK, italic=True))
    render(out("waypoint-history.svg"), W, H, *frags)


# ── builder.svg — масив структур годує рукостискання завантаження ───────────
def fig_builder():
    W, H = 760, 380
    frags = []
    frags.append(text(W / 2, 28, "Конструктор: масив структур → протокол завантаження", size=16, bold=True))

    # ліворуч — масив зібраних елементів
    ax, ay = 36, 78
    aw, rh = 250, 40
    items = [
        ("0", "NAV_TAKEOFF", NEG),
        ("1", "NAV_WAYPOINT", INK),
        ("2", "NAV_WAYPOINT", INK),
        ("3", "NAV_RETURN_TO_LAUNCH", NEG),
    ]
    frags.append(text(ax + aw / 2, ay - 14, "масив mavlink_mission_item_int_t[]", size=12, color=MUTED, bold=True))
    for i, (seq, cmd, col) in enumerate(items):
        y = ay + i * rh
        frags.append(rect(ax, y, aw, rh - 6, fill=FILL, stroke=LINE, sw=1.2))
        frags.append(text(ax + 16, y + (rh - 6) / 2 + 5, "i = " + seq, size=12.5, color=col, anchor="start", bold=True))
        frags.append(text(ax + aw - 14, y + (rh - 6) / 2 + 5, cmd, size=12, color=INK, anchor="end"))

    # праворуч — діалог завантаження (борт ↔ код)
    lane_l = 470          # код (станція)
    lane_r = 660          # апарат
    top = 70
    frags.append(text(lane_l, top - 10, "твій код", size=12.5, color=NEG, anchor="middle", bold=True))
    frags.append(text(lane_r, top - 10, "апарат", size=12.5, color=POS, anchor="middle", bold=True))
    frags.append(line(lane_l, top, lane_l, H - 30, color=MUTED, sw=1.2, dash="3 4"))
    frags.append(line(lane_r, top, lane_r, H - 30, color=MUTED, sw=1.2, dash="3 4"))

    def msg(y, x1, x2, label, col):
        f = arrow(x1, y, x2, y, color=col, sw=1.8)
        f += text((x1 + x2) / 2, y - 7, label, size=11, color=col, anchor="middle", bold=True)
        return f

    y = top + 24
    frags.append(msg(y, lane_l, lane_r, "MISSION_COUNT = 4", NEG)); y += 38
    frags.append(msg(y, lane_r, lane_l, "REQUEST_INT 0", POS)); y += 30
    frags.append(msg(y, lane_l, lane_r, "ITEM_INT 0", NEG)); y += 34
    frags.append(text((lane_l + lane_r) / 2, y - 2, "… 1, 2, 3 по черзі …", size=11, color=MUTED, anchor="middle")); y += 30
    frags.append(msg(y, lane_r, lane_l, "REQUEST_INT 3", POS)); y += 30
    frags.append(msg(y, lane_l, lane_r, "ITEM_INT 3", NEG)); y += 36
    frags.append(msg(y, lane_r, lane_l, "MISSION_ACK ✓", FIELD))

    # зв'язок: масив живить діалог
    frags.append('<path d="M %d %d C %d %d, %d %d, %d %d" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 3" marker-end="url(#arrow)"/>'
                 % (ax + aw, ay + rh / 2, 360, ay, 410, top + 10, lane_l - 6, top + 18, FIELD))
    render(out("builder.svg"), W, H, *frags)


# ── seqmap.svg — нульовий пункт-домівка й off-by-one у DO_JUMP ───────────────
def fig_seqmap():
    W, H = 760, 350
    frags = []
    frags.append(text(W / 2, 28, "Нульовий пункт — домівка: зсув номерів і ціль DO_JUMP", size=16, bold=True))

    rows = [
        ("0", "HOME (домівка)", "ставить автопілот сам", FIELD, "#eafaf1"),
        ("1", "NAV_TAKEOFF", "перша ТВОЯ команда", NEG, "#eef3fe"),
        ("2", "NAV_WAYPOINT", "початок ланки ← ціль DO_JUMP", INK, FILL),
        ("3", "NAV_WAYPOINT", "", INK, FILL),
        ("4", "DO_JUMP → 2", "стрибок на seq 2, не на 1!", POS, "#fdecea"),
        ("5", "NAV_RETURN_TO_LAUNCH", "додому", NEG, "#eef3fe"),
    ]
    x = 150
    w = 470
    rh = 40
    top = 60
    for i, (seq, cmd, note, col, fill) in enumerate(rows):
        y = top + i * rh
        frags.append(rect(x, y, w, rh - 6, fill=fill, stroke=col, sw=1.5))
        frags.append(text(x + 16, y + (rh - 6) / 2 + 5, "seq " + seq, size=13, color=col, anchor="start", bold=True))
        frags.append(text(x + 92, y + (rh - 6) / 2 + 5, cmd, size=12.5, color=INK, anchor="start", bold=True))
        if note:
            frags.append(text(x + w - 12, y + (rh - 6) / 2 + 5, note, size=11, color=MUTED, anchor="end"))

    # дуга DO_JUMP від seq 4 назад до seq 2
    y_jump = top + 4 * rh + (rh - 6) / 2
    y_targ = top + 2 * rh + (rh - 6) / 2
    frags.append('<path d="M %d %d C %d %d, %d %d, %d %d" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5 3" marker-end="url(#arrow)"/>'
                 % (x, y_jump, x - 80, y_jump, x - 80, y_targ, x - 4, y_targ, POS))

    frags.append(text(W / 2, H - 14, "масив, що ти шлеш, нумерується з 0; але seq 0 на борту — це home, тож твоя перша команда стає seq 1",
                      size=11, color=MUTED))
    render(out("seqmap.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_item()
    fig_frames()
    fig_commands()
    fig_radius()
    fig_waypoint_history()
    fig_builder()
    fig_seqmap()
    print("OK: item, frames, commands, radius, waypoint-history, builder, seqmap")
