# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Mission Planner і QGroundControl: порівняння GCS».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: чому станцій ДВІ — спільний MAVLink, дві родини стеку ───────────
# Ідея: посередині — один протокол MAVLink. Згори дві окремі лінії розвитку
# (ArduPilot → Mission Planner; PX4 → QGroundControl). Та оскільки ОБИДВІ
# станції говорять тим самим MAVLink, ArduPilot-апарат бачать обидві → вибір
# зручності, а не прив'язка.
def fig_two_lineages():
    W, H = 960, 470
    P = []
    P.append(text(W / 2, 30, "Чому станцій дві: один протокол, дві родини стеку",
                  size=17, bold=True))

    # центральна шина MAVLink
    busy = 250
    P.append(line(120, busy, W - 120, busy, color=INK, sw=3))
    fr, w, h = textbox(W / 2, busy, "MAVLink — спільна мова землі й борту",
                       size=13, bold=True, fill="#fff7e6", stroke="#b8860b", min_w=360)
    P.append(fr)

    # ліва родина: ArduPilot → Mission Planner
    lx = 250
    fr, w, h = textbox(lx, 90, "стек ArduPilot", size=12.5, bold=True,
                       fill="#eaf0fd", stroke=NEG, color=NEG, min_w=180)
    P.append(fr)
    fr, w, h = textbox(lx, 165, "Mission Planner\n(C#/.NET, Windows)",
                       size=12, bold=True, fill="#eef2f7", stroke=INK, min_w=180)
    P.append(fr)
    P.append(arrow(lx, 112, lx, 142, color=NEG))
    P.append(arrow(lx, 190, lx, busy - 16, color=NEG))

    # права родина: PX4 → QGroundControl
    rx = W - 250
    fr, w, h = textbox(rx, 90, "стек PX4", size=12.5, bold=True,
                       fill="#e9f7ef", stroke=FIELD, color=FIELD, min_w=180)
    P.append(fr)
    fr, w, h = textbox(rx, 165, "QGroundControl\n(Qt/QML, усі платформи)",
                       size=12, bold=True, fill="#eef2f7", stroke=INK, min_w=180)
    P.append(fr)
    P.append(arrow(rx, 112, rx, 142, color=FIELD))
    P.append(arrow(rx, 190, rx, busy - 16, color=FIELD))

    # апарат на ArduPilot під шиною — його бачать ОБИДВІ
    py = 360
    fr, w, h = textbox(W / 2, py, "апарат на ArduPilot", size=13, bold=True,
                       fill="#fdecea", stroke=POS, color=POS, min_w=220)
    P.append(fr)
    P.append(line(W / 2, busy + 18, W / 2, py - h / 2, color=MUTED, sw=1.4))

    # дуги «обидві дотягуються»
    P.append(arrow(lx, busy + 16, W / 2 - 120, py - 10, color=NEG, sw=1.6))
    P.append(arrow(rx, busy + 16, W / 2 + 120, py - 10, color=FIELD, sw=1.6))

    P.append(text(W / 2, H - 22,
                  "обидві станції говорять MAVLink → ArduPilot-борт працює з будь-якою; "
                  "це вибір зручності, не прив'язка",
                  size=12.5, color=MUTED))
    render("img/two-lineages.svg", W, H, *P)


# ── Фігура 2: де воно взагалі запускається ──────────────────────────────────
# Ідея: найрізкіша практична відмінність — охоплення платформ. Mission Planner
# рідний лише на Windows (деінде через Mono — з тертям); QGroundControl рідно
# скрізь, включно з планшетом і телефоном у полі. Хочеш у полі без ноутбука →
# вибору, по суті, нема.
def fig_platforms():
    W, H = 960, 430
    P = []
    P.append(text(W / 2, 30, "Де воно запускається: охоплення платформ",
                  size=17, bold=True))

    cols = ["Windows", "macOS", "Linux", "Android", "iOS"]
    n = len(cols)
    x0, x1 = 230, W - 60
    step = (x1 - x0) / (n - 1)
    colx = [x0 + i * step for i in range(n)]

    # заголовки колонок
    head_y = 95
    for cx, name in zip(colx, cols):
        P.append(text(cx, head_y, name, size=12.5, bold=True))
    # позначка «мобільне» над двома останніми
    P.append(line(colx[3] - 38, head_y - 26, colx[4] + 38, head_y - 26, color=MUTED, sw=1.2))
    P.append(text((colx[3] + colx[4]) / 2, head_y - 32, "у полі, без ноутбука",
                  size=11, color=MUTED, italic=True))

    def mark(cx, cy, kind):
        # kind: 'full' рідно, 'mono' через прошарок, 'no' нема
        if kind == "full":
            return (circle(cx, cy, 12, fill="#e9f7ef", stroke=FIELD, sw=2) +
                    text(cx, cy + 4.5, "✓", size=14, color=FIELD, bold=True))
        if kind == "mono":
            return (circle(cx, cy, 12, fill="#fff7e6", stroke="#b8860b", sw=2) +
                    text(cx, cy + 4.5, "~", size=15, color="#b8860b", bold=True))
        return (circle(cx, cy, 12, fill="#fdecea", stroke=POS, sw=2) +
                text(cx, cy + 4.5, "✕", size=13, color=POS, bold=True))

    rows = [
        ("Mission Planner", 175, ["full", "mono", "mono", "no", "no"]),
        ("QGroundControl", 255, ["full", "full", "full", "full", "full"]),
    ]
    for name, ry, kinds in rows:
        fr, w, h = textbox(120, ry, name, size=12.5, bold=True,
                           fill="#eef2f7", stroke=INK, min_w=180)
        P.append(fr)
        for cx, k in zip(colx, kinds):
            P.append(mark(cx, ry, k))

    # легенда
    ly = 330
    P.append(mark(250, ly, "full")); P.append(text(270, ly + 4, "рідно", size=11.5, anchor="start"))
    P.append(mark(400, ly, "mono")); P.append(text(420, ly + 4, "через Mono (з тертям)", size=11.5, anchor="start"))
    P.append(mark(640, ly, "no")); P.append(text(660, ly + 4, "нема", size=11.5, anchor="start"))

    P.append(text(W / 2, H - 22,
                  "потрібен планшет чи телефон у полі — практичного вибору, по суті, нема",
                  size=12.5, color=MUTED))
    render("img/platforms.svg", W, H, *P)


# ── Фігура 3: дві філософії екрана ──────────────────────────────────────────
# Ідея: Mission Planner — щільний кокпіт із вкладками, кожна крутилка назовні
# (сила для тюнінгу, поріг для новачка). QGroundControl — два режими (Plan/Fly),
# що самі підлаштовуються під екран; глибше сховане (легше старт, менше видно
# одразу). Та сама робота, протилежний підхід до показу.
def fig_two_uis():
    W, H = 960, 480
    P = []
    P.append(text(W / 2, 30, "Дві філософії екрана: усе назовні проти двох режимів",
                  size=17, bold=True))

    # ── ліворуч: Mission Planner — макет вікна з вкладками ──
    lx, ly, lw, lh = 70, 80, 360, 300
    P.append(rect(lx, ly, lw, lh, fill="#fbfcfe", stroke=INK, sw=1.6))
    P.append(text(lx + lw / 2, ly - 12, "Mission Planner", size=13.5, bold=True, color=NEG))
    # рядок вкладок
    tabs = ["Flight Data", "Plan", "Setup", "Config", "Tuning"]
    tw = lw / len(tabs)
    for i, t in enumerate(tabs):
        tx = lx + i * tw
        fill = "#eaf0fd" if i == 0 else "#eef2f7"
        P.append(rect(tx, ly, tw, 26, fill=fill, stroke=MUTED, sw=1, rx=3))
        P.append(text(tx + tw / 2, ly + 17, t, size=9.5, bold=(i == 0)))
    # «щільне поле крутилок»
    gy = ly + 44
    for r in range(5):
        for c in range(3):
            kx = lx + 26 + c * 115
            ky = gy + r * 40
            P.append(rect(kx, ky, 96, 26, fill="#ffffff", stroke="#c0c7d0", sw=1, rx=3))
            P.append(line(kx + 70, ky + 5, kx + 90, ky + 5, color=MUTED, sw=1))
            P.append(line(kx + 70, ky + 13, kx + 86, ky + 13, color=MUTED, sw=1))
            P.append(line(kx + 70, ky + 21, kx + 90, ky + 21, color=MUTED, sw=1))
    fr, w, h = textbox(lx + lw / 2, ly + lh + 36,
                       "усе назовні: глибокий тюнінг і аналіз\nпоруч — але новачок губиться",
                       size=11.5, fill="#eaf0fd", stroke=NEG, color=NEG)
    P.append(fr)

    # ── праворуч: QGroundControl — два великі режими ──
    rx, ry, rw, rh = W - 430, 80, 360, 300
    P.append(rect(rx, ry, rw, rh, fill="#fbfcfe", stroke=INK, sw=1.6))
    P.append(text(rx + rw / 2, ry - 12, "QGroundControl", size=13.5, bold=True, color=FIELD))
    # два великі режими Plan / Fly
    half = rw / 2
    P.append(rect(rx, ry, half, 30, fill="#e9f7ef", stroke=MUTED, sw=1, rx=3))
    P.append(text(rx + half / 2, ry + 20, "Plan", size=12, bold=True))
    P.append(rect(rx + half, ry, half, 30, fill="#eef2f7", stroke=MUTED, sw=1, rx=3))
    P.append(text(rx + half + half / 2, ry + 20, "Fly", size=12, bold=True))
    # велика «карта/HUD» — мінімум елементів
    P.append(rect(rx + 20, ry + 46, rw - 40, rh - 70, fill="#f1f5fb", stroke="#c0c7d0", sw=1.2, rx=4))
    P.append(circle(rx + rw / 2, ry + 46 + (rh - 70) / 2, 30, fill="#ffffff", stroke=FIELD, sw=2))
    P.append(line(rx + rw / 2 - 22, ry + 46 + (rh - 70) / 2, rx + rw / 2 + 22, ry + 46 + (rh - 70) / 2, color=FIELD, sw=2))
    P.append(text(rx + rw / 2, ry + rh - 18, "велика карта, небагато кнопок", size=10.5, color=MUTED))
    fr, w, h = textbox(rx + rw / 2, ry + rh + 36,
                       "два режими, що тягнуться під екран:\nлегший старт — глибше сховане",
                       size=11.5, fill="#e9f7ef", stroke=FIELD, color=FIELD)
    P.append(fr)

    render("img/two-uis.svg", W, H, *P)


# ── Фігура 4: роздавач MAVLink — один борт, дві станції ──────────────────────
# Ідея (для вставки proj): борт має ОДИН вихід (USB або один UDP-потік SITL),
# а станцій дві. Роздавач підключається до борту раз, забирає весь потік і
# КОПІЮЄ кожен кадр у дві станції; назад — ЗЛИВАЄ усе в єдиний потік до борту.
# Без нього друга станція впирається в «порт зайнято».
def fig_router_fanout():
    W, H = 980, 430
    P = []
    P.append(text(W / 2, 30, "Роздавач MAVLink: один борт — дві станції",
                  size=17, bold=True))

    # ── зліва: борт з ОДНИМ виходом ──
    bx, by = 150, 215
    fr, w, h = textbox(bx, by, "борт\n(один вихід:\nUSB або 1×UDP)",
                       size=12.5, bold=True, fill="#fdecea", stroke=POS,
                       color=POS, min_w=170)
    P.append(fr)
    bx_right = bx + w / 2

    # ── центр: роздавач ──
    cx, cy = W / 2, 215
    fr, w, h = textbox(cx, cy, "роздавач\n(router)", size=13.5, bold=True,
                       fill="#fff7e6", stroke="#b8860b", min_w=170)
    P.append(fr)
    cx_left = cx - w / 2
    cx_right = cx + w / 2

    # ── праворуч: дві станції на окремих портах ──
    sx = W - 165
    s1y, s2y = 120, 310
    fr1, w1, h1 = textbox(sx, s1y, "Mission Planner\n(порт 14550)",
                          size=12, bold=True, fill="#eaf0fd", stroke=NEG,
                          color=NEG, min_w=190)
    P.append(fr1)
    fr2, w2, h2 = textbox(sx, s2y, "QGroundControl\n(порт 14551)",
                          size=12, bold=True, fill="#e9f7ef", stroke=FIELD,
                          color=FIELD, min_w=190)
    P.append(fr2)
    s_left = sx - w1 / 2

    # борт → роздавач: «весь потік» (одна товста лінія праворуч)
    P.append(arrow(bx_right, by - 8, cx_left, cy - 8, color=POS, sw=2.4))
    # роздавач → борт: «усе злите назад» (нижче, ліворуч)
    P.append(arrow(cx_left, cy + 12, bx_right, by + 12, color=MUTED, sw=1.6))
    P.append(text((bx_right + cx_left) / 2, by - 22, "весь потік борту",
                  size=10.5, color=POS))
    P.append(text((bx_right + cx_left) / 2, by + 34, "усе назад — в один потік",
                  size=10.5, color=MUTED))

    # роздавач → станція 1 (копія потоку)
    P.append(arrow(cx_right, cy - 14, s_left, s1y + 6, color=NEG, sw=1.8))
    # роздавач → станція 2 (копія потоку)
    P.append(arrow(cx_right, cy + 14, s_left, s2y - 6, color=FIELD, sw=1.8))
    # станції → роздавач (їхні команди зливаються) — пунктир назад
    P.append(line(s_left, s1y + 18, cx_right, cy + 2, color=MUTED, sw=1.2, dash="4,3"))
    P.append(line(s_left, s2y - 18, cx_right, cy + 6, color=MUTED, sw=1.2, dash="4,3"))
    P.append(text((cx_right + s_left) / 2, s1y - 6, "копія кадрів",
                  size=10.5, color=NEG))
    P.append(text((cx_right + s_left) / 2, s2y + 22, "копія кадрів",
                  size=10.5, color=FIELD))

    P.append(text(W / 2, H - 20,
                  "одна точка виходу борту → дві станції; без роздавача друга "
                  "впирається в «порт зайнято»",
                  size=12.5, color=MUTED))
    render("img/router-fanout.svg", W, H, *P)


if __name__ == "__main__":
    fig_two_lineages()
    fig_platforms()
    fig_two_uis()
    fig_router_fanout()
    print("OK: 4 figures -> img/")
