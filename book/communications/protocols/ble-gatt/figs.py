# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── sleep: радіо майже весь час спить — звідси роки від батарейки ──────────────
# Ідея: Classic тримає струм високим увесь час; BLE лежить біля нуля й зрідка
# дає вузький сплеск на прокидання. Площа під кривою (заряд) — у рази менша.
def fig_sleep():
    W, H = 700, 320
    ox, oy = 70, 250
    aw, ah = 580, 196
    p = []

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час", size=12, color=INK, italic=True))
    p.append(text(ox - 12, oy - ah - 2, "струм", size=12, color=INK, anchor="end", italic=True))

    # Classic: висока майже стала лінія
    cl_y = oy - ah * 0.72
    p.append(line(ox, cl_y, ox + aw, cl_y, color=POS, sw=2.6))
    p.append(text(ox + 10, cl_y - 8, "Classic: радіо ввімкнене весь час (~десятки мА)",
                  size=11, color=POS, anchor="start", bold=True))

    # BLE: лежить біля нуля, кілька вузьких сплесків
    base = oy - ah * 0.06
    spikes = [0.18, 0.40, 0.62, 0.84]
    pts = [(ox, base)]
    for s in spikes:
        x = ox + s * aw
        pts += [(x - 7, base), (x, oy - ah * 0.52), (x + 7, base)]
    pts.append((ox + aw, base))
    poly = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (poly, FIELD))
    p.append(text(ox + aw * 0.40, base + 22, "BLE: майже весь час спить, зрідка короткий сплеск",
                  size=11, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "sleep.svg"), W, H, *p,
           title="Середній струм вирішує: BLE спить, Classic не вимикається")


# ── advertising: периферія мовить у ефір, центральний слухає ───────────────────
# Ідея: давач періодично шле короткі пакети «я тут»; телефон сканує і чує. Те
# саме — спосіб бути знайденим і найдешевший спосіб щось повідомити (маячок).
def fig_advertising():
    W, H = 700, 300
    p = []

    # периферія зліва
    perx, pery = 130, 150
    pb, pbw, pbh = textbox(perx, pery, "Периферія\n(давач)", size=12, bold=True,
                           fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(pb)

    # центральний справа
    cenx, ceny = 570, 150
    cb, cbw, cbh = textbox(cenx, ceny, "Центральний\n(телефон)", size=12, bold=True,
                           fill="#eef4ff", stroke=NEG, sw=1.8)
    p.append(cb)

    # три короткі пакети-сповіщення в ефір
    for i, dy in enumerate((-46, 0, 46)):
        x0 = perx + pbw / 2 + 6
        x1 = cenx - cbw / 2 - 6
        y = pery + dy
        p.append(arrow(x0, y, x1, y, color=MUTED, sw=1.6))
        pkt, kw, kh = textbox((x0 + x1) / 2, y, "«я тут»", size=10,
                              fill=BG, stroke=MUTED, sw=1.2, color=MUTED)
        p.append(pkt)

    p.append(text(perx, pery + pbh / 2 + 26, "періодично шле\nсповіщення (advertising)".split("\n")[0],
                  size=10, color=FIELD, bold=True))
    p.append(text(perx, pery + pbh / 2 + 40, "сповіщення (advertising)", size=10, color=FIELD, bold=True))
    p.append(text(cenx, ceny + cbh / 2 + 26, "сканує ефір", size=10, color=NEG, bold=True))
    p.append(text(cenx, ceny + cbh / 2 + 40, "і чує", size=10, color=NEG, bold=True))

    p.append(text(W / 2, H - 24,
                  "маячок мовить дані широкомовно; для двостороннього обміну — далі під'єднання",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "advertising.svg"), W, H, *p,
           title="Реклама: сповіщати про себе без з'єднання")


# ── roles: периферія = сервер даних, центральний = клієнт ──────────────────────
# Ідея: ролі BLE — не master/slave, а сервер (зберігає значення) і клієнт (читає
# й пише). ESP32 може бути будь-ким.
def fig_roles():
    W, H = 700, 300
    p = []

    # периферія / сервер
    perx, pery = 175, 130
    pb, pbw, pbh = textbox(perx, pery, "Периферія", size=13, bold=True,
                           fill="#eafaf0", stroke=FIELD, sw=1.9, min_w=170)
    p.append(pb)
    p.append(text(perx, pery + pbh / 2 + 22, "= сервер даних", size=12, color=FIELD, bold=True))
    p.append(text(perx, pery + pbh / 2 + 42, "зберігає значення; рекламує себе", size=10, color=MUTED))
    p.append(text(perx, pery + pbh / 2 + 58, "(давач, гаджет)", size=10, color=MUTED))

    # центральний / клієнт
    cenx, ceny = 525, 130
    cb, cbw, cbh = textbox(cenx, ceny, "Центральний", size=13, bold=True,
                           fill="#eef4ff", stroke=NEG, sw=1.9, min_w=170)
    p.append(cb)
    p.append(text(cenx, ceny + cbh / 2 + 22, "= клієнт", size=12, color=NEG, bold=True))
    p.append(text(cenx, ceny + cbh / 2 + 42, "сканує, під'єднується, читає/пише", size=10, color=MUTED))
    p.append(text(cenx, ceny + cbh / 2 + 58, "(телефон, ПК)", size=10, color=MUTED))

    # запит клієнта → сервер, відповідь назад
    y = pery
    p.append(arrow(cenx - cbw / 2 - 6, y - 10, perx + pbw / 2 + 6, y - 10, color=NEG, sw=1.7))
    p.append(text((perx + cenx) / 2, y - 16, "запит значення", size=10, color=NEG))
    p.append(arrow(perx + pbw / 2 + 6, y + 12, cenx - cbw / 2 - 6, y + 12, color=FIELD, sw=1.7))
    p.append(text((perx + cenx) / 2, y + 26, "значення у відповідь", size=10, color=FIELD))

    p.append(text(W / 2, H - 22, "ESP32 може бути будь-ким: периферією-давачем або центральним-збирачем",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "roles.svg"), W, H, *p,
           title="Дві ролі: сервер даних і клієнт (не master/slave)")


# ── gatt-tree: дані як дерево сервіс → характеристики ──────────────────────────
# Ідея: сервер містить сервіси (групи); у кожному — характеристики (іменовані
# значення з UUID, поточним значенням і властивостями).
def fig_gatt_tree():
    W, H = 700, 340
    p = []

    # корінь — сервер
    srvx, srvy = 350, 50
    sb, sbw, sbh = textbox(srvx, srvy, "Сервер (периферія)", size=12, bold=True,
                           fill=FILL, stroke=INK, sw=1.8)
    p.append(sb)

    # сервіс
    svcx, svcy = 350, 135
    vb, vbw, vbh = textbox(svcx, svcy, "Сервіс «Оточення»  ·  UUID", size=12, bold=True,
                           fill="#fdf6e3", stroke="#b8901f", sw=1.7)
    p.append(vb)
    p.append(line(srvx, srvy + sbh / 2, svcx, svcy - vbh / 2, color=INK, sw=1.5))

    # три характеристики
    chars = [
        (160, "Температура", "23.4 °C", "read · notify"),
        (350, "Вологість", "57 %", "read · notify"),
        (540, "Поріг", "30 °C", "read · write"),
    ]
    cy = 250
    for cx, name, val, props in chars:
        b, bw, bh = textbox(cx, cy, "%s\n%s" % (name, val), size=11, bold=True,
                            fill="#eef4ff", stroke=NEG, sw=1.6, min_w=150)
        p.append(line(svcx, svcy + vbh / 2, cx, cy - bh / 2, color="#b8901f", sw=1.4))
        p.append(b)
        p.append(text(cx, cy + bh / 2 + 18, "UUID · " + props, size=9.5, color=MUTED))

    p.append(text(W / 2, H - 16,
                  "характеристика = UUID + поточне значення + властивості (що з нею можна)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "gatt-tree.svg"), W, H, *p,
           title="GATT: дані як дерево сервісів і характеристик")


# ── operations: read / write / notify ─────────────────────────────────────────
# Ідея: три операції над характеристикою; notify — периферія сама штовхає нове
# значення без запиту, тож радіо прокидається лише за новиною.
def fig_operations():
    W, H = 700, 320
    p = []
    cenx = 150          # центральний
    perx = 550          # периферія (характеристика)
    rows = [
        (90, "READ", "центральний тягне значення, коли захоче", NEG, "cen->per", "per->cen"),
        (170, "WRITE", "центральний штовхає значення (поріг, команда)", POS, "cen->per", None),
        (250, "NOTIFY", "периферія САМА штовхає нове значення, без запиту", FIELD, None, "per->cen"),
    ]

    # стовпці-підписи
    p.append(text(cenx, 56, "Центральний", size=11, color=INK, bold=True))
    p.append(text(perx, 56, "Характеристика", size=11, color=INK, bold=True))
    p.append(line(cenx, 64, cenx, 290, color="#dddddd", sw=1.2, dash="3 4"))
    p.append(line(perx, 64, perx, 290, color="#dddddd", sw=1.2, dash="3 4"))

    for y, op, desc, col, req, resp in rows:
        p.append(text(cenx - 70, y, op, size=13, color=col, bold=True, anchor="start"))
        if req == "cen->per":
            p.append(arrow(cenx + 12, y, perx - 12, y, color=col, sw=1.8))
        if resp == "per->cen":
            yy = y + (14 if req else 0)
            p.append(arrow(perx - 12, yy, cenx + 12, yy, color=col, sw=1.8))
        p.append(text((cenx + perx) / 2, y - 10 if op != "NOTIFY" else y - 10, desc,
                      size=10, color=MUTED))

    p.append(text(W / 2, H - 22,
                  "notify економить енергію: радіо прокидається лише тоді, коли значення змінилось",
                  size=11, color=FIELD, italic=True, bold=True))

    render(os.path.join(OUT, "operations.svg"), W, H, *p,
           title="Три операції над характеристикою: read, write, notify")


# ── stream-vs-struct: потік (SPP) проти структури (GATT) ───────────────────────
# Ідея: SPP — труба сирих байтів, структуру вигадуєш сам; GATT — набір названих
# значень, до кожного звертаєшся за UUID.
def fig_stream_vs_struct():
    W, H = 700, 320
    p = []

    # ліворуч — SPP-труба
    lx = 70
    p.append(text(lx + 120, 64, "SPP (Classic): труба байтів", size=12, color=POS, bold=True))
    tube_y, tube_h = 110, 44
    p.append(rect(lx, tube_y, 260, tube_h, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    p.append(text(lx + 130, tube_y + tube_h / 2 + 5, "4A 12 FF 00 7E 4A 12 …",
                  size=12, color=INK))
    p.append(text(lx + 130, tube_y + tube_h + 24, "структуру (де що) вигадуєш сам",
                  size=10, color=MUTED))

    # праворуч — GATT названі значення
    rx = 400
    p.append(text(rx + 120, 64, "GATT (BLE): названі значення", size=12, color=FIELD, bold=True))
    named = [("Температура", "23.4"), ("Вологість", "57"), ("Заряд", "88 %")]
    yy = 100
    for name, val in named:
        b, bw, bh = textbox(rx + 120, yy + 22, "%s = %s" % (name, val), size=11, bold=True,
                            fill="#eafaf0", stroke=FIELD, sw=1.5, min_w=200)
        p.append(b)
        yy += 56
    p.append(text(rx + 120, yy + 14, "до кожного — за іменем (UUID)", size=10, color=MUTED))

    render(os.path.join(OUT, "stream-vs-struct.svg"), W, H, *p,
           title="Дві моделі даних: потік (SPP) проти структури (GATT)")


# ── choice: BLE / Classic / Wi-Fi — карта вибору ──────────────────────────────
# Ідея: три питання-розгалуження ведуть до трьох інструментів ESP32 за потребою:
# інтернет → Wi-Fi; довга автономність, рідкі дані → BLE; замінити дріт → SPP.
def fig_choice():
    W, H = 720, 330
    p = []

    qx, qy = 360, 56
    qb, qbw, qbh = textbox(qx, qy, "Що потрібно?", size=13, bold=True, fill=FILL, stroke=INK, sw=1.8)
    p.append(qb)

    leaves = [
        (140, "Wi-Fi", "вихід у мережу,\nінтернет, хмару", NEG, "#eef4ff"),
        (360, "BLE", "довга автономність,\nдані рідко й потроху", FIELD, "#eafaf0"),
        (580, "Classic / SPP", "замінити дріт\nпотоком байтів", POS, "#fdecea"),
    ]
    ly = 210
    for lx, name, desc, col, fill in leaves:
        b, bw, bh = textbox(lx, ly, name, size=13, bold=True, color=col, fill=fill, stroke=col, sw=1.9, min_w=150)
        p.append(line(qx, qy + qbh / 2, lx, ly - bh / 2, color=col, sw=1.6))
        p.append(b)
        p.append(mtext(lx, ly + bh / 2 + 20, desc, size=10, color=MUTED))

    p.append(text(W / 2, H - 18, "ESP32 вміє всі три — обмеження не залізо, а правильний добір під задачу",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "choice.svg"), W, H, *p,
           title="Карта вибору: BLE проти Classic проти Wi-Fi")


if __name__ == "__main__":
    fig_sleep()
    fig_advertising()
    fig_roles()
    fig_gatt_tree()
    fig_operations()
    fig_stream_vs_struct()
    fig_choice()
    print("OK: figures written to", OUT)
