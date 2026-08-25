# -*- coding: utf-8 -*-
"""Фігури до теми «Компоненти MAVLink: sysid, compid і адресація вузлів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def tb(cx, cy, s, **kw):
    body, _w, _h = textbox(cx, cy, s, **kw)
    return body


# ── 1. Двовимірний простір адрес ───────────────────────────────────────────
def fig_address_space():
    W, H = 1060, 600
    f = []

    rows = [
        ("compid 1 — автопілот",        (1, 1, 0)),
        ("compid 100 — камера",         (1, 1, 0)),
        ("compid 154 — підвіс",         (1, 0, 0)),
        ("compid 190 — станція",        (0, 0, 1)),
        ("compid 191 — борткомп'ютер",  (1, 0, 0)),
    ]
    cols = [
        (430, "sysid 1", "коптер"),
        (660, "sysid 2", "літак"),
        (900, "sysid 255", "земля"),
    ]

    # підписи стовпців
    for x, a, b in cols:
        f.append(tb(x, 105, a + "\n" + b, size=14, bold=False, min_w=170))

    # рядки
    for i, (label, marks) in enumerate(rows):
        y = 200 + i * 78
        f.append(text(300, y + 5, label, size=14, anchor="end"))
        for j, (x, _a, _b) in enumerate(cols):
            f.append(rect(x - 85, y - 30, 170, 60, fill="#ffffff",
                          stroke="#c9ced6", sw=1.2, rx=8))
            if marks[j]:
                f.append(circle(x, y, 13, fill="#d9f0e2", stroke=FIELD, sw=2.2))

    # вертикальні напрямні заголовків
    for x, _a, _b in cols:
        f.append(line(x, 140, x, 168, color=MUTED, sw=1.2, dash="4,4"))

    render(os.path.join(OUT, 'address-space.svg'), W, H, *f,
           title="Адреса MAVLink — точка у двовимірному просторі: апарат × вузол")


# ── 2. Відправник у заголовку, адресат — усередині даних ────────────────────
def fig_where_target():
    W, H = 1120, 560
    f = []

    def strip(y, title, cells, note, note_color=MUTED):
        out = [text(60, y - 46, title, size=15, bold=True, anchor="start")]
        x = 60
        for label, w, kind in cells:
            fill = {"hdr": "#eef2f7", "who": "#dfe9fb",
                    "tgt": "#fdeaea", "pay": "#f4f6f8"}[kind]
            stroke = {"hdr": "#c9ced6", "who": NEG,
                      "tgt": POS, "pay": "#c9ced6"}[kind]
            out.append(fitbox(x, y, w, 62, label, size=13,
                              fill=fill, stroke=stroke, sw=1.8))
            x += w + 6
        out.append(text(60, y + 96, note, size=13, color=note_color, anchor="start"))
        return out, x

    a, _ = strip(150, "ATTITUDE — оголошення про власний стан",
                 [("STX", 62, "hdr"), ("LEN", 62, "hdr"), ("SEQ", 62, "hdr"),
                  ("sysid\n1", 96, "who"), ("compid\n1", 104, "who"),
                  ("MSG ID\n30", 104, "hdr"),
                  ("roll  pitch  yaw  —  жодного поля адресата", 470, "pay"),
                  ("CRC", 62, "hdr")],
                 "Адресата немає взагалі: пакет читає кожен, хто його почув.")
    f += a

    b, _ = strip(370, "COMMAND_LONG — звернення до конкретного вузла",
                 [("STX", 62, "hdr"), ("LEN", 62, "hdr"), ("SEQ", 62, "hdr"),
                  ("sysid\n255", 96, "who"), ("compid\n190", 104, "who"),
                  ("MSG ID\n76", 104, "hdr"),
                  ("target_system 1  target_component 1  command …", 470, "tgt"),
                  ("CRC", 62, "hdr")],
                 "Адресат — звичайні поля корисних даних, і лише в тих типах, де він доречний.")
    f += b

    f.append(text(60, 300, "сині поля — хто надіслав;   червоні — кому призначено",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'where-target.svg'), W, H, *f,
           title="Заголовок каже, ХТО надіслав; адресата, якщо він є, шукають у даних")


# ── 3. Маршрутизація за вивченим ───────────────────────────────────────────
def fig_router():
    W, H = 1160, 620
    f = []

    f.append(tb(580, 300, "Маршрутизатор\nтри канали", size=15, bold=True, min_w=230))

    f.append(tb(180, 170, "Канал A — UART\nчув: 1/1,  1/100", size=13, min_w=250))
    f.append(tb(180, 440, "Канал B — USB\nчув: 1/191", size=13, min_w=250))
    f.append(tb(980, 300, "Канал C — UDP\nчув: 255/190", size=13, min_w=250))

    # вхід із каналу C
    f.append(arrow(852, 300, 700, 300, color=POS))
    f.append(text(776, 275, "вхід", size=13, color=POS))

    # вихід у канал A (ціль 1/100 бачено саме там)
    f.append(arrow(462, 272, 310, 190, color=FIELD))
    f.append(text(392, 210, "переслати", size=13, color=FIELD))

    # канал B — не пересилаємо
    f.append(line(462, 330, 310, 418, color=MUTED, sw=1.6, dash="7,6"))
    f.append(text(392, 400, "мовчимо", size=13, color=MUTED))

    f.append(text(580, 540, "Пакет із target 1/100. Цю пару чули лише на каналі A —",
                  size=14, anchor="middle"))
    f.append(text(580, 570, "туди його й віддають, решту каналів не турбують.",
                  size=14, anchor="middle"))

    render(os.path.join(OUT, 'router.svg'), W, H, *f,
           title="Маршрут будують не з таблиці мереж, а з того, кого де чули")


# ── 4. Закільцювання між двома мостами ─────────────────────────────────────
def fig_router_loop():
    W, H = 1020, 600
    f = []

    f.append(tb(140, 300, "Автопілот 1/1\nHEARTBEAT — оголошення", size=13, min_w=210))
    f.append(tb(420, 300, "Міст 1", size=15, bold=True, min_w=210))
    f.append(tb(830, 300, "Міст 2", size=15, bold=True, min_w=210))

    f.append(arrow(248, 300, 312, 300, color=MUTED))

    # верхня рейка: Міст 1 → Міст 2
    f.append(line(420, 272, 420, 180, color=POS, sw=2))
    f.append(arrow(420, 180, 830, 180, color=POS, sw=2))
    f.append(line(830, 180, 830, 272, color=POS, sw=2))
    f.append(text(625, 152, "канал USB", size=14, bold=True))
    f.append(text(625, 212, "оголошення — в усі канали, крім вхідного",
                 size=13, color=MUTED))

    # нижня рейка: Міст 2 → Міст 1
    f.append(line(830, 328, 830, 420, color=POS, sw=2))
    f.append(arrow(830, 420, 420, 420, color=POS, sw=2))
    f.append(line(420, 328, 420, 420, color=POS, sw=2))
    f.append(text(625, 392, "у Мості 2 те саме правило, дзеркально",
                 size=13, color=MUTED))
    f.append(text(625, 452, "канал Wi-Fi", size=14, bold=True))

    f.append(text(510, 520, "Один кадр обертається колом: 1 → 2 → 4 → 8 копій.",
                 size=14))
    f.append(text(510, 550,
                 "У заголовку MAVLink немає лічильника переходів — само це не згасне.",
                 size=14, color=POS))

    render(os.path.join(OUT, 'router-loop.svg'), W, H, *f,
           title="Два мости, з'єднані двома лініями: пакет ходить колом і множиться")


# ── 5. Карта зайнятого й вільного в діапазоні compid ───────────────────────
def fig_compid_map():
    W, H = 1260, 470
    f = []

    X0, K = 80.0, 4.2          # x(v) = X0 + v*K,  v ∈ 0…255
    BY, BH = 220, 52           # смуга: верх і висота

    def x(v):
        return X0 + v * K

    # підкладка на весь діапазон — «нічия земля», яку стандарт може забрати
    f.append(rect(x(0), BY, x(255) - x(0), BH,
                  fill="#ffffff", stroke="#c9ced6", sw=1.2, rx=4))

    taken = [(0, 0), (1, 1), (100, 105), (110, 112), (140, 161),
             (169, 169), (171, 175), (180, 181), (189, 198),
             (200, 202), (220, 221), (236, 238), (240, 243), (250, 250)]
    for a, b in taken:
        f.append(rect(x(a), BY, max(x(b + 1) - x(a), 3.0), BH,
                      fill="#dfe9fb", stroke=NEG, sw=1.4, rx=2))

    # вікно USER1…USER75 — єдине, що віддано інтеграторові
    f.append(rect(x(25), BY, x(100) - x(25), BH,
                  fill="#d9f0e2", stroke=FIELD, sw=2.2, rx=2))
    # у ньому вирізано 68 — телеметричне радіо
    f.append(rect(x(68), BY, max(x(69) - x(68), 3.0), BH,
                  fill="#dfe9fb", stroke=NEG, sw=1.4, rx=2))

    # ── підписи над смугою ──
    up = [(1, 118, "1 — автопілот"),
          (102, 510, "100–105 камери"),
          (150, 676, "140–161 приводи, підвіс, службові"),
          (195, 912, "189–202 борт, планування, IMU"),
          (240, 1090, "236–243 ODID і мости")]
    for v, lx, s in up:
        f.append(text(lx, 150, s, size=12, anchor="middle"))
        f.append(line(lx, 164, x(v), 214, color=MUTED, sw=1.0))

    # ── підписи під смугою ──
    dn = [(62, 340, "25–99 — вільні для ваших вузлів"),
          (111, 548, "110–112 радіо"),
          (175, 816, "169–181 лебідка, підвіси, батареї"),
          (220, 1004, "220–221 GPS"),
          (250, 1132, "250 — застаріле")]
    for v, lx, s in dn:
        f.append(line(x(v), BY + BH + 6, lx, 306, color=MUTED, sw=1.0))
        f.append(text(lx, 322, s, size=12, anchor="middle"))

    # шкала — лише два краї, щоб не тіснити підписи
    f.append(text(x(0), BY - 12, "0", size=11, color=MUTED))
    f.append(text(x(255), BY - 12, "255", size=11, color=MUTED))

    f.append(text(x(0), 400, "Зелене — вікно USER1…USER75, віддане інтеграторові; "
                             "у ньому вирізано 68 (телеметричне радіо).",
                  size=13, color=MUTED, anchor="start"))
    f.append(text(x(0), 428, "Біле — не «вільне», а ще не роздане: стандарт "
                             "займає ці числа новими редакціями.",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'compid-map.svg'), W, H, *f,
           title="Діапазон compid 0…255: що вже роздано, а що лишили інтеграторові")


if __name__ == '__main__':
    fig_address_space()
    fig_where_target()
    fig_router()
    fig_router_loop()
    fig_compid_map()
    print("ok")
