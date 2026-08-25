# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BROKER = "#7c3aed"   # колір брокера (фіолетовий) — центр системи


# ── why-broker: плутанина прямих звʼязків проти зірки через брокера ────────────
# Ідея: ліворуч кожен з кожним (лавина ниток, усі мусять бути ввімкнені);
# праворуч одна нитка від кожного до центру — брокер розводить сам.
def fig_why_broker():
    W, H = 700, 360
    p = []

    # ── ліворуч: повний граф із 4 вузлів ──
    import math
    lcx, lcy, lr = 175, 200, 90
    nodes = []
    for i in range(4):
        a = -math.pi / 2 + i * math.pi / 2
        nodes.append((lcx + lr * math.cos(a), lcy + lr * math.sin(a)))
    # усі ребра між усіма
    for i in range(4):
        for j in range(i + 1, 4):
            p.append(line(nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1],
                          color=POS, sw=1.6))
    for x, y in nodes:
        p.append(circle(x, y, 18, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(lcx, 70, "кожен з кожним", size=13, color=POS, bold=True))
    p.append(text(lcx, lcy + lr + 50, "ниток — лавина; усі мусять", size=10, color=MUTED, italic=True))
    p.append(text(lcx, lcy + lr + 64, "бути ввімкнені водночас", size=10, color=MUTED, italic=True))

    # ── праворуч: зірка через брокер ──
    rcx, rcy, rr = 525, 200, 95
    leaves = []
    for i in range(4):
        a = -math.pi / 2 + i * math.pi / 2
        leaves.append((rcx + rr * math.cos(a), rcy + rr * math.sin(a)))
    for x, y in leaves:
        p.append(line(rcx, rcy, x, y, color=BROKER, sw=1.7))
    for x, y in leaves:
        p.append(circle(x, y, 18, fill="#eef4ff", stroke=NEG, sw=1.8))
    bb, bw, bh = textbox(rcx, rcy, "брокер", size=12, bold=True,
                         fill="#f3eafd", stroke=BROKER, sw=2.0)
    p.append(bb)
    p.append(text(rcx, 70, "усі — через брокера", size=13, color=BROKER, bold=True))
    p.append(text(rcx, rcy + rr + 50, "по одній нитці до центру;", size=10, color=MUTED, italic=True))
    p.append(text(rcx, rcy + rr + 64, "відправник і слухач не бачать одне одного", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "why-broker.svg"), W, H, *p,
           title="Чому посередник: зірка замість павутини прямих звʼязків")


# ── topic-tree: топіки як дерево назв змісту ──────────────────────────────────
# Ідея: корінь home → кімнати → величини; повний шлях від кореня до листка — топік.
def fig_topic_tree():
    W, H = 700, 350
    p = []

    # корінь
    rx, ry = 350, 56
    rb, rbw, rbh = textbox(rx, ry, "home", size=13, bold=True, fill=FILL, stroke=INK, sw=1.8)
    p.append(rb)

    # середній рівень — дві кімнати
    rooms = [(220, "room"), (480, "kitchen")]
    midy = 150
    midpos = {}
    for cx, name in rooms:
        b, bw, bh = textbox(cx, midy, name, size=12, bold=True,
                            fill="#fdf6e3", stroke="#b8901f", sw=1.6, min_w=120)
        p.append(line(rx, ry + rbh / 2, cx, midy - bh / 2, color=INK, sw=1.4))
        p.append(b)
        midpos[name] = (cx, midy, bh)

    # листки-величини
    leaves = [
        ("room", 150, "temp"), ("room", 290, "humidity"),
        ("kitchen", 480, "light"),
    ]
    ly = 250
    for parent, cx, name in leaves:
        px, py, pbh = midpos[parent]
        b, bw, bh = textbox(cx, ly, name, size=11, bold=True,
                            fill="#eef4ff", stroke=NEG, sw=1.5, min_w=110)
        p.append(line(px, py + pbh / 2, cx, ly - bh / 2, color="#b8901f", sw=1.3))
        p.append(b)

    p.append(text(W / 2, 312, "повний шлях від кореня до листка — окремий топік: home/room/temp",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, 332, "рівні розділяє «/»; структуру вигадує розробник",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "topic-tree.svg"), W, H, *p,
           title="Топіки — дерево назв змісту, а не адрес пристроїв")


# ── pub-sub: видавець → брокер → багато підписників ───────────────────────────
# Ідея: одна публікація на топік; брокер сам розмножує копії всім підписникам.
def fig_pub_sub():
    W, H = 700, 320
    p = []

    # видавець ліворуч
    pubx, puby = 120, 160
    pb, pbw, pbh = textbox(pubx, puby, "Видавець\n(давач)", size=12, bold=True,
                           fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(pb)

    # брокер у центрі
    brx, bry = 360, 160
    bb, bbw, bbh = textbox(brx, bry, "Брокер", size=13, bold=True,
                           fill="#f3eafd", stroke=BROKER, sw=2.0, min_w=130)
    p.append(bb)

    # публікація: видавець → брокер
    p.append(arrow(pubx + pbw / 2 + 6, puby, brx - bbw / 2 - 6, puby, color=FIELD, sw=2.0))
    p.append(text((pubx + brx) / 2, puby - 12, "PUBLISH", size=11, color=FIELD, bold=True))
    p.append(text((pubx + brx) / 2, puby + 18, "home/room/temp = 23.4", size=9.5, color=MUTED, italic=True))

    # два підписники праворуч
    subs = [(600, 95, "Телефон"), (600, 225, "База даних")]
    for sx, sy, name in subs:
        sb, sbw, sbh = textbox(sx, sy, name, size=11, bold=True,
                               fill="#eef4ff", stroke=NEG, sw=1.7, min_w=130)
        p.append(arrow(brx + bbw / 2 + 6, bry + (sy - bry) * 0.18,
                       sx - sbw / 2 - 6, sy, color=NEG, sw=1.8))
        p.append(b if False else sb)
    p.append(text((brx + 600) / 2 + 10, 120, "копія", size=10, color=NEG, italic=True))
    p.append(text((brx + 600) / 2 + 10, 210, "копія", size=10, color=NEG, italic=True))

    p.append(text(W / 2, H - 22, "видавець публікує ОДИН раз; розмноження на всіх підписників робить брокер",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "pub-sub.svg"), W, H, *p,
           title="Публікація/підписка: одна публікація — копії всім підписникам")


# ── wildcards: підписка + і # на дереві топіків ───────────────────────────────
# Ідея: одне дерево; + ловить один рівень (температуру всіх кімнат),
# # ловить усе піддерево.
def fig_wildcards():
    W, H = 700, 360
    p = []

    # корінь
    rx, ry = 350, 54
    rb, rbw, rbh = textbox(rx, ry, "home", size=12, bold=True, fill=FILL, stroke=INK, sw=1.7)
    p.append(rb)

    rooms = [(200, "room"), (500, "kitchen")]
    midy = 140
    midpos = {}
    for cx, name in rooms:
        b, bw, bh = textbox(cx, midy, name, size=11, bold=True,
                            fill="#fdf6e3", stroke="#b8901f", sw=1.5, min_w=110)
        p.append(line(rx, ry + rbh / 2, cx, midy - bh / 2, color=INK, sw=1.3))
        p.append(b)
        midpos[name] = (cx, midy, bh)

    # листки; temp-листки підсвічуємо зеленим (їх ловить +), решта — звичайні
    leaves = [
        ("room", 130, "temp", True), ("room", 270, "humidity", False),
        ("kitchen", 430, "temp", True), ("kitchen", 570, "light", False),
    ]
    ly = 235
    for parent, cx, name, hot in leaves:
        px, py, pbh = midpos[parent]
        col = FIELD if hot else NEG
        fill = "#eafaf0" if hot else "#eef4ff"
        b, bw, bh = textbox(cx, ly, name, size=10, bold=True,
                            fill=fill, stroke=col, sw=1.7 if hot else 1.3, min_w=100)
        p.append(line(px, py + pbh / 2, cx, ly - bh / 2, color="#b8901f", sw=1.2))
        p.append(b)

    # підписи двох вайлдкардів
    p.append(text(W / 2, 300,
                  "home/+/temp  →  температура в БУДЬ-ЯКІЙ кімнаті (зелені листки), один рівень",
                  size=11, color=FIELD, bold=True))
    p.append(text(W / 2, 322,
                  "home/#  →  УСЕ піддерево home на будь-якій глибині (# лише останнім)",
                  size=11, color=BROKER, bold=True))
    p.append(text(W / 2, 344,
                  "вайлдкарди дозволені лише в підписці, не в публікації",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "wildcards.svg"), W, H, *p,
           title="Вайлдкарди: підписка на цілу гілку дерева")


# ── qos-levels: три рівні гарантії як сходи від дешевого до надійного ──────────
# Ідея: QoS0 — один кидок без відповіді; QoS1 — кидок+ACK з повтором; QoS2 —
# чотирикроковий обмін. Що вище — більше гарантій і більше балачки.
def fig_qos_levels():
    W, H = 700, 360
    p = []
    pubx, brx = 180, 520

    def lane(y, h):
        for x, lab in ((pubx, "видавець"), (brx, "брокер")):
            p.append(line(x, y, x, y + h, color="#dddddd", sw=1.1, dash="3 4"))

    # QoS 0
    y0 = 70
    p.append(text(60, y0 + 4, "QoS 0", size=13, color=MUTED, anchor="start", bold=True))
    p.append(text(60, y0 + 20, "≤1 раз", size=9.5, color=MUTED, anchor="start"))
    lane(y0, 36)
    p.append(arrow(pubx, y0 + 14, brx, y0 + 14, color=MUTED, sw=1.8))
    p.append(text((pubx + brx) / 2, y0 + 6, "PUBLISH", size=10, color=MUTED, bold=True))
    p.append(text(brx + 70, y0 + 18, "кинув і забув — може зникнути", size=9.5, color=MUTED, italic=True, anchor="middle"))

    # QoS 1
    y1 = 140
    p.append(text(60, y1 + 4, "QoS 1", size=13, color=FIELD, anchor="start", bold=True))
    p.append(text(60, y1 + 20, "≥1 раз", size=9.5, color=FIELD, anchor="start"))
    lane(y1, 56)
    p.append(arrow(pubx, y1 + 12, brx, y1 + 12, color=FIELD, sw=1.8))
    p.append(text((pubx + brx) / 2, y1 + 4, "PUBLISH", size=10, color=FIELD, bold=True))
    p.append(arrow(brx, y1 + 40, pubx, y1 + 40, color=NEG, sw=1.8))
    p.append(text((pubx + brx) / 2, y1 + 56, "PUBACK", size=10, color=NEG, bold=True))
    p.append(text(brx + 70, y1 + 26, "дійде напевно, та може задвоїтись", size=9.5, color=FIELD, italic=True, anchor="middle"))

    # QoS 2
    y2 = 232
    p.append(text(60, y2 + 4, "QoS 2", size=13, color=POS, anchor="start", bold=True))
    p.append(text(60, y2 + 20, "рівно 1", size=9.5, color=POS, anchor="start"))
    lane(y2, 96)
    steps = [(12, "PUBLISH", FIELD, True), (36, "PUBREC", NEG, False),
             (60, "PUBREL", FIELD, True), (84, "PUBCOMP", NEG, False)]
    for dy, lab, col, fwd in steps:
        if fwd:
            p.append(arrow(pubx, y2 + dy, brx, y2 + dy, color=col, sw=1.7))
        else:
            p.append(arrow(brx, y2 + dy, pubx, y2 + dy, color=col, sw=1.7))
        p.append(text((pubx + brx) / 2, y2 + dy - 4, lab, size=9.5, color=col, bold=True))
    p.append(text(brx + 70, y2 + 48, "рівно раз — найдовше й найважче", size=9.5, color=POS, italic=True, anchor="middle"))

    render(os.path.join(OUT, "qos-levels.svg"), W, H, *p,
           title="Три рівні QoS: що більше гарантій — то більше балачки")


# ── retain: брокер зберігає останнє значення для нового підписника ────────────
# Ідея: давач публікує з retain; брокер відкладає значення; новий підписник
# одразу отримує його, не чекаючи нової публікації.
def fig_retain():
    W, H = 700, 320
    p = []

    pubx, puby = 110, 95
    pb, pbw, pbh = textbox(pubx, puby, "Давач", size=12, bold=True,
                           fill="#eafaf0", stroke=FIELD, sw=1.8, min_w=110)
    p.append(pb)

    brx, bry = 360, 130
    bb, bbw, bbh = textbox(brx, bry, "Брокер", size=13, bold=True,
                           fill="#f3eafd", stroke=BROKER, sw=2.0, min_w=130)
    p.append(bb)

    # публікація з retain
    p.append(arrow(pubx + pbw / 2 + 6, puby, brx - bbw / 2 - 6, bry - 16, color=FIELD, sw=2.0))
    p.append(text((pubx + brx) / 2 - 10, puby - 18, "PUBLISH 23.4", size=10, color=FIELD, bold=True))
    p.append(text((pubx + brx) / 2 - 10, puby - 4, "retain = 1", size=10, color=POS, bold=True))

    # збережене значення в брокері
    sb = fitbox(brx - 70, bry + bbh / 2 + 12, 140, 30, "відкладено: 23.4",
                size=10, fill="#fdf6e3", stroke="#b8901f", sw=1.5, bold=True, color="#8a6d00")
    p.append(sb)

    # новий підписник приходить пізніше
    subx, suby = 610, 130
    sbb, sbw, sbh = textbox(subx, suby, "Новий\nпідписник", size=11, bold=True,
                            fill="#eef4ff", stroke=NEG, sw=1.7, min_w=120)
    p.append(sbb)
    p.append(arrow(subx - sbw / 2 - 6, suby - 16, brx + bbw / 2 + 6, bry - 16, color=NEG, sw=1.6))
    p.append(text((brx + subx) / 2 + 6, suby - 24, "SUBSCRIBE (пізніше)", size=9.5, color=NEG, italic=True))
    p.append(arrow(brx + bbw / 2 + 6, bry + 10, subx - sbw / 2 - 6, suby + 10, color="#b8901f", sw=1.9))
    p.append(text((brx + subx) / 2 + 6, suby + 26, "одразу віддає 23.4", size=10, color="#8a6d00", bold=True))

    p.append(text(W / 2, H - 20, "нового слухача зустрічає поточний стан, а не порожнеча очікування",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "retain.svg"), W, H, *p,
           title="Retain: останнє значення чекає на нового підписника")


# ── lwt: заповіт — брокер оголошує раптову смерть клієнта ──────────────────────
# Ідея: клієнт лишає «волю» при під'єднанні; зв'язок рветься раптово; брокер сам
# публікує «offline» підписникам топіка статусу.
def fig_lwt():
    W, H = 700, 320
    p = []

    devx, devy = 120, 110
    db, dbw, dbh = textbox(devx, devy, "Давач", size=12, bold=True,
                           fill="#eafaf0", stroke=FIELD, sw=1.8, min_w=110)
    p.append(db)

    brx, bry = 360, 110
    bb, bbw, bbh = textbox(brx, bry, "Брокер", size=13, bold=True,
                           fill="#f3eafd", stroke=BROKER, sw=2.0, min_w=130)
    p.append(bb)

    # 1) лишає заповіт при під'єднанні
    p.append(arrow(devx + dbw / 2 + 6, devy - 12, brx - bbw / 2 - 6, bry - 12, color=NEG, sw=1.6))
    p.append(text((devx + brx) / 2, devy - 20, "CONNECT + воля:", size=9.5, color=NEG, bold=True))
    p.append(text((devx + brx) / 2, devy - 6, "«status = offline»", size=9.5, color=MUTED, italic=True))

    # відкладений заповіт у брокері
    wb = fitbox(brx - 75, bry + bbh / 2 + 10, 150, 28, "воля напоготові (мовчить)",
                size=9, fill="#f4f4f4", stroke=MUTED, sw=1.3, italic=False, color=MUTED)
    p.append(wb)

    # 2) зв'язок рветься раптово
    p.append(line(devx + dbw / 2 + 6, devy + 14, brx - bbw / 2 - 6, bry + 14,
                  color=POS, sw=2.0, dash="6 5"))
    p.append(text((devx + brx) / 2, devy + 30, "✗ зв'язок обірвано раптово", size=9.5, color=POS, bold=True))

    # 3) брокер сам публікує заповіт підписникам статусу
    subx, suby = 600, 110
    sbb, sbw, sbh = textbox(subx, suby, "Панель\nдиспетчера", size=10.5, bold=True,
                            fill="#eef4ff", stroke=NEG, sw=1.7, min_w=130)
    p.append(sbb)
    p.append(arrow(brx + bbw / 2 + 6, bry, subx - sbw / 2 - 6, suby, color=POS, sw=2.0))
    p.append(text((brx + subx) / 2, bry - 10, "PUBLISH «offline»", size=10, color=POS, bold=True))
    p.append(text((brx + subx) / 2, bry + 18, "(брокер — від імені давача)", size=9, color=MUTED, italic=True))

    p.append(text(W / 2, H - 18, "ввічливе прощання заповіт скасовує; оголошують лише раптову смерть",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "lwt.svg"), W, H, *p,
           title="Last Will & Testament: брокер оголосить, що пристрій помер")


# ── vs-http: поллінг HTTP проти відкритого зʼєднання MQTT ──────────────────────
# Ідея: ліворуч потік порожніх запитів «нема новин?»; праворуч одне відкрите
# зʼєднання, дані лише коли зʼявились.
def fig_vs_http():
    W, H = 720, 350
    p = []
    colw = 320
    lx, rx = 24, W - 24 - colw

    # ── HTTP-поллінг ──
    p.append(rect(lx, 56, colw, 258, fill="#fff5f5", stroke=POS, sw=1.5))
    p.append(text(lx + colw / 2, 80, "HTTP-поллінг", size=14, color=POS, bold=True))
    cx, sx = lx + 56, lx + colw - 56
    p.append(text(cx, 104, "пристрій", size=10, color=INK, bold=True))
    p.append(text(sx, 104, "сервер", size=10, color=INK, bold=True))
    y = 126
    for i in range(4):
        p.append(arrow(cx, y, sx, y, color=POS, sw=1.4))
        p.append(text((cx + sx) / 2, y - 5, "нема новин?", size=9, color=POS))
        p.append(arrow(sx, y + 18, cx, y + 18, color=MUTED, sw=1.3))
        p.append(text((cx + sx) / 2, y + 13, "ні" if i < 3 else "так: 23.4", size=9, color=MUTED))
        y += 42
    p.append(text(lx + colw / 2, 302, "купа важких запитів, більшість — порожні",
                  size=10, color=POS, italic=True))

    # ── MQTT ──
    p.append(rect(rx, 56, colw, 258, fill="#f6fbf7", stroke=FIELD, sw=1.5))
    p.append(text(rx + colw / 2, 80, "MQTT", size=14, color=FIELD, bold=True))
    cx2, bx2 = rx + 56, rx + colw - 56
    p.append(text(cx2, 104, "пристрій", size=10, color=INK, bold=True))
    p.append(text(bx2, 104, "брокер", size=10, color=BROKER, bold=True))
    # одне відкрите з'єднання — товста стала лінія
    p.append(line(cx2, 126, cx2, 280, color=MUTED, sw=1.1, dash="3 4"))
    p.append(line(bx2, 126, bx2, 280, color=MUTED, sw=1.1, dash="3 4"))
    p.append(line(cx2, 132, bx2, 132, color=FIELD, sw=2.6))
    p.append(text((cx2 + bx2) / 2, 124, "з'єднання відкрите весь час", size=10, color=FIELD, bold=True))
    # дані летять самі, лише коли є
    p.append(arrow(cx2, 196, bx2, 196, color=FIELD, sw=1.8))
    p.append(text((cx2 + bx2) / 2, 191, "23.4 — коли з'явилось", size=9, color=FIELD, bold=True))
    p.append(arrow(cx2, 248, bx2, 248, color=FIELD, sw=1.8))
    p.append(text((cx2 + bx2) / 2, 243, "24.1 — коли з'явилось", size=9, color=FIELD, bold=True))
    p.append(text(rx + colw / 2, 302, "дані самі, тієї ж миті; без «а чи є новини?»",
                  size=10, color=FIELD, italic=True))

    p.append(text(W / 2, H - 14, "для телеметрії MQTT — менше трафіку, менша затримка, довша робота від батареї",
                  size=11, color=INK, italic=True, bold=True))

    render(os.path.join(OUT, "vs-http.svg"), W, H, *p,
           title="Чому MQTT економніший за опитування HTTP")


# ════════ фігури для детальної версії (-d.md) ════════════════════════════════

# ── packet-anatomy: будова MQTT-пакета (для -d.md) ────────────────────────────
# Ідея: фіксований заголовок 2+ байти (тип+прапорці, потім Remaining Length зі
# змінною довжиною), далі необовʼязковий змінний заголовок і корисне навантаження.
def fig_packet_anatomy():
    W, H = 720, 330
    p = []
    x0, y = 40, 90
    bh = 64

    parts = [
        (150, "#fdecea", POS, "1-й байт", "тип пакета (4 біти)\n+ прапорці (4 біти)"),
        (175, "#fff3df", "#b8901f", "Remaining Length", "1–4 байти, змінна;\n7 біт + біт-продовження"),
        (180, "#eef4ff", NEG, "Змінний заголовок", "за типом: ід. пакета,\nтопік, прапорці…"),
        (155, "#eafaf0", FIELD, "Навантаження", "самі дані\n(може бути порожнім)"),
    ]
    x = x0
    for w, fill, col, name, desc in parts:
        p.append(rect(x, y, w, bh, fill=fill, stroke=col, sw=1.8))
        p.append(text(x + w / 2, y + 22, name, size=12, color=col, bold=True))
        for i, ln in enumerate(desc.split("\n")):
            p.append(text(x + w / 2, y + 40 + i * 14, ln, size=9, color=MUTED))
        x += w + 8

    # дужка над двома першими — фіксований заголовок
    fx2 = x0 + parts[0][0] + 8 + parts[1][0]
    p.append(line(x0, y - 14, fx2, y - 14, color=INK, sw=1.5))
    p.append(text((x0 + fx2) / 2, y - 20, "фіксований заголовок (мінімум 2 байти)", size=10, color=INK, bold=True))

    # дужка над двома останніми — необовʼязкові
    ox = x0 + parts[0][0] + 8 + parts[1][0] + 8
    p.append(line(ox, y + bh + 14, x - 8, y + bh + 14, color=MUTED, sw=1.4, dash="4 4"))
    p.append(text((ox + x - 8) / 2, y + bh + 28, "є не в кожному пакеті", size=10, color=MUTED, italic=True))

    p.append(text(W / 2, H - 24,
                  "найкоротший пакет (наприклад PINGREQ) — це лише 2 байти заголовка, і все",
                  size=11, color=INK, italic=True, bold=True))

    render(os.path.join(OUT, "packet-anatomy.svg"), W, H, *p,
           title="Будова MQTT-пакета: крихітний фіксований заголовок")


# ── qos2-flow: чотирикроковий обмін QoS 2 (для -d.md) ──────────────────────────
# Ідея: PUBLISH→PUBREC→PUBREL→PUBCOMP з одним ід. пакета; два «коліна» гарантують
# рівно-раз навіть при втраті будь-якого кроку (повтор за тим самим ід.).
def fig_qos2_flow():
    W, H = 700, 360
    p = []
    sx, rx = 180, 520
    top, bot = 80, 320
    for x, lab in ((sx, "видавець"), (rx, "брокер")):
        p.append(line(x, top, x, bot, color="#dddddd", sw=1.2, dash="4 4"))
        b, bw, bh = textbox(x, top - 16, lab, size=12, bold=True, fill=FILL, stroke=INK, sw=1.5, pad=8)
        p.append(b)

    def step(y, x1, x2, lab, col, note):
        p.append(arrow(x1, y, x2, y, color=col, sw=2.0))
        p.append(text((x1 + x2) / 2, y - 8, lab, size=12, color=col, bold=True))
        p.append(text((x1 + x2) / 2, y + 16, note, size=9.5, color=MUTED, italic=True))

    step(120, sx, rx, "PUBLISH (id=42)", FIELD, "ось дані; запамʼятай id")
    step(175, rx, sx, "PUBREC (id=42)", NEG, "отримав, відклав")
    step(230, sx, rx, "PUBREL (id=42)", FIELD, "тепер можеш віддавати")
    step(285, rx, sx, "PUBCOMP (id=42)", NEG, "віддав, забуваю id")

    p.append(text(W / 2, H - 18,
                  "однаковий id у всіх чотирьох кроках; загубиться будь-який — повтор за тим самим id, тож рівно раз",
                  size=10.5, color=POS, italic=True, bold=True))

    render(os.path.join(OUT, "qos2-flow.svg"), W, H, *p,
           title="QoS 2: чотири кроки гарантують доставку рівно раз")


# ── sessions: clean проти persistent (для -d.md) ───────────────────────────────
# Ідея: clean-сесія — брокер усе забуває при розриві; persistent — тримає
# підписки й чергу повідомлень QoS>0, доки клієнт повернеться.
def fig_sessions():
    W, H = 700, 320
    p = []
    colw = 300
    lx, rx = 30, W - 30 - colw

    def panel(x, title, col, fill, lines, foot):
        p.append(rect(x, 56, colw, 220, fill=fill, stroke=col, sw=1.6))
        p.append(text(x + colw / 2, 82, title, size=14, color=col, bold=True))
        y = 116
        for ln in lines:
            p.append(circle(x + 22, y - 4, 3, fill=col, stroke=col, sw=1))
            p.append(text(x + 36, y, ln, size=11, color=INK, anchor="start"))
            y += 30
        p.append(text(x + colw / 2, 262, foot, size=10, color=col, italic=True, bold=True))

    panel(lx, "Чиста сесія (clean)", POS, "#fff5f5",
          ["при розриві брокер", "  усе про клієнта забуває",
           "підписки зникають", "черга повідомлень — ні",
           "повернувся — починай з нуля"],
          "просто, та проспані повідомлення втрачено")

    panel(rx, "Тривала сесія (persistent)", FIELD, "#f6fbf7",
          ["брокер памʼятає клієнта", "  за його стійким id",
           "підписки лишаються", "копить повідомлення QoS>0",
           "повернувся — отримав усе проспане"],
          "переживає сон і обриви, але займає памʼять брокера")

    render(os.path.join(OUT, "sessions.svg"), W, H, *p,
           title="Дві моделі сесії: чиста проти тривалої")


# ── mqtt-sn: MQTT-SN через шлюз для не-TCP мереж (для -d.md) ───────────────────
# Ідея: крихітні вузли говорять MQTT-SN поверх UDP/Zigbee до шлюзу; шлюз
# перекладає це на звичайний MQTT/TCP до справжнього брокера.
def fig_mqtt_sn():
    W, H = 720, 300
    p = []

    # вузли ліворуч
    nodes_y = [100, 160, 220]
    for ny in nodes_y:
        b, bw, bh = textbox(110, ny, "вузол", size=10, bold=True,
                            fill="#eafaf0", stroke=FIELD, sw=1.5, min_w=90)
        p.append(b)

    # шлюз у центрі
    gwx = 380
    gb, gbw, gbh = textbox(gwx, 160, "MQTT-SN\nшлюз", size=12, bold=True,
                           fill="#fff3df", stroke="#b8901f", sw=1.9, min_w=130)
    p.append(gb)

    # брокер праворуч
    brx = 620
    bb, bbw, bbh = textbox(brx, 160, "Брокер\nMQTT", size=12, bold=True,
                           fill="#f3eafd", stroke=BROKER, sw=2.0, min_w=120)
    p.append(bb)

    # стрілки вузли → шлюз (UDP/Zigbee, без зʼєднання)
    for ny in nodes_y:
        p.append(arrow(110 + 50, ny, gwx - gbw / 2 - 6, 160 + (ny - 160) * 0.25,
                       color=FIELD, sw=1.6))
    p.append(text((110 + gwx) / 2, 250, "MQTT-SN поверх UDP / Zigbee / serial", size=10, color=FIELD, bold=True))
    p.append(text((110 + gwx) / 2, 266, "без зʼєднання, ще дрібніше; топіки — короткими id", size=9.5, color=MUTED, italic=True))

    # шлюз → брокер (звичайний MQTT/TCP)
    p.append(arrow(gwx + gbw / 2 + 6, 160, brx - bbw / 2 - 6, 160, color=BROKER, sw=2.0))
    p.append(text((gwx + brx) / 2, 150, "звичайний MQTT/TCP", size=10, color=BROKER, bold=True))

    p.append(text(W / 2, H - 18,
                  "шлюз перекладає світ без TCP на звичайний MQTT — решта системи різниці не бачить",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "mqtt-sn.svg"), W, H, *p,
           title="MQTT-SN: той самий принцип для мереж без TCP")


if __name__ == "__main__":
    # базова версія
    fig_why_broker()
    fig_topic_tree()
    fig_pub_sub()
    fig_wildcards()
    fig_qos_levels()
    fig_retain()
    fig_lwt()
    fig_vs_http()
    # детальна версія
    fig_packet_anatomy()
    fig_qos2_flow()
    fig_sessions()
    fig_mqtt_sn()
    print("OK: figures written to", OUT)
