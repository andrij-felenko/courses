# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ORANGE = "#e67e22"   # OUT-напрям / control
PURPLE = "#8e44ad"   # службовий EP0


# ── endpoints: однонапрямні труби IN/OUT і службовий EP0 ──────────────────────
# Ідея: показати, що канал у пристрої — не «дріт у два боки», а набір окремих
# однонапрямних буферів; кожен має номер і напрям, а EP0 стоїть осібно.

def fig_endpoints():
    W, H = 760, 360
    p = []
    # пристрій праворуч — рамка з кінцевими точками
    dx, dy, dw, dh = 280, 60, 220, 260
    p.append(rect(dx, dy, dw, dh, fill="#fef9ec", stroke=ORANGE, sw=2.5, rx=10))
    p.append(text(dx + dw / 2, dy + 22, "Пристрій", size=14, color=ORANGE, bold=True))

    eps = [
        ("EP0 (control, двобічний)", "#f5eef8", PURPLE, False),
        ("EP1-IN (bulk →)", "#eafaf1", FIELD, False),
        ("EP1-OUT (bulk ←)", "#eafaf1", FIELD, False),
        ("EP2-IN (interrupt →)", "#eaf0fd", NEG, False),
    ]
    ey = dy + 47
    rowh = 36
    ep_centers = []
    for lab, fill, col, bold in eps:
        p.append(rect(dx + 30, ey, dw - 60, rowh, fill=fill, stroke=col, sw=2.0, rx=6))
        p.append(text(dx + dw / 2, ey + 23, lab, size=12, color=col, bold=bold))
        ep_centers.append(ey + rowh / 2)
        ey += rowh + 19

    # хост ліворуч
    hx, hy, hw, hh = 60, 120, 140, 140
    p.append(rect(hx, hy, hw, hh, fill="#eaf0fd", stroke=NEG, sw=2.0, rx=10))
    p.append(text(hx + hw / 2, hy + 40, "Хост", size=14, color=NEG, bold=True))
    p.append(text(hx + hw / 2, hy + 70, "(ПК)", size=12, color=MUTED))
    p.append(text(hx + hw / 2, hy + 92, "ініціює обмін", size=11, color=MUTED))

    hcx = hx + hw / 2
    # EP0 — двобічна стрілка
    p.append(line(hx + hw + 5, hy + 50, dx - 5, dy + 47 + rowh / 2,
                  color=PURPLE, sw=1.8))
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" '
             'marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
             % (hx + hw + 5, hy + 50, dx - 5, dy + 47 + rowh / 2, PURPLE))
    # IN — стрілка до хоста
    p.append(arrow(dx - 5, ep_centers[1], hx + hw + 5, hy + 60, color=FIELD, sw=1.8))
    p.append(arrow(dx - 5, ep_centers[3], hx + hw + 5, hy + 80, color=NEG, sw=1.8))
    # OUT — стрілка від хоста
    p.append(arrow(hx + hw + 5, hy + 100, dx - 5, ep_centers[2], color=ORANGE, sw=1.8))

    # легенда напрямів (з погляду хоста)
    p.append(text(W - 20, 84, "IN  = до хоста", size=12, color=FIELD, anchor="end", bold=True))
    p.append(text(W - 20, 104, "OUT = від хоста", size=12, color=ORANGE, anchor="end", bold=True))
    p.append(text(W - 20, 124, "напрям — завжди з погляду хоста", size=10, color=MUTED, anchor="end"))

    note = fitbox(143, 326, 474, 26, "EP0 є завжди: двобічний службовий канал, ним іде енумерація",
                  size=12, fill="#f5eef8", stroke=PURPLE, sw=1.5, bold=True)
    p.append(note)

    render(os.path.join(OUT, "endpoints.svg"), W, H, *p,
           title="Кінцеві точки пристрою: однонапрямні труби IN/OUT і службовий EP0")


# ── bus-tempo: хост диктує темп, кадри 1 мс ───────────────────────────────────
# Ідея: вісь часу поділена на кадри 1 мс; кожен відкриває SOF, далі хост сам
# опитує точки. Пристрій мовчить, доки його не спитали — звідси «реактивність».

def fig_bus_tempo():
    W, H = 820, 300
    p = []
    axis_y = 175
    p.append(arrow(60, axis_y, 760, axis_y, color=INK, sw=1.8))
    p.append(text(772, axis_y + 5, "час", size=13, color=MUTED, anchor="start"))

    frames = [
        ("Кадр 1", [("SOF", "#eaf0fd", NEG, True), ("IN EP1", "#eafaf1", FIELD, False),
                    ("OUT EP1", "#fef9ec", ORANGE, False), ("IN EP2", "#eafaf1", FIELD, False)]),
        ("Кадр 2", [("SOF", "#eaf0fd", NEG, True), ("IN EP1", "#eafaf1", FIELD, False),
                    ("OUT EP1", "#fef9ec", ORANGE, False)]),
        ("Кадр 3", [("SOF", "#eaf0fd", NEG, True), ("IN EP2", "#eafaf1", FIELD, False),
                    ("IN EP1", "#eafaf1", FIELD, False)]),
        ("Кадр 4", [("SOF", "#eaf0fd", NEG, True), ("OUT EP1", "#fef9ec", ORANGE, False),
                    ("IN EP2", "#eafaf1", FIELD, False)]),
    ]
    fx = 60
    fw = 168
    fy = 100
    fh = 52
    for label, slots in frames:
        p.append(rect(fx, fy, fw, fh, fill=BG, stroke=LINE, sw=1.5, rx=4))
        p.append(text(fx + fw / 2, fy - 12, label + " (1 мс)", size=11, color=MUTED))
        n = len(slots)
        sw_ = (fw - 8) / n
        sx = fx + 4
        for lab, fill, col, bold in slots:
            p.append(rect(sx, fy + 4, sw_ - 2, fh - 8, fill=fill, stroke=col, sw=1.0, rx=3))
            p.append(text(sx + sw_ / 2 - 1, fy + fh / 2 + 4, lab, size=9, color=col, bold=bold))
            sx += sw_
        fx += fw + 6

    p.append(text(W / 2, 225, "Пристрій мовчить, доки хост не надіслав запит; SOF (Start of Frame) відкриває кожен кадр",
                  size=12, color=MUTED))
    note = fitbox(W / 2 - 235, 250, 470, 30, "Тому пристрій лише відповідає й не може почати передачу сам",
                  size=12, fill=FILL, stroke=MUTED, sw=1.0)
    p.append(note)

    render(os.path.join(OUT, "bus-tempo.svg"), W, H, *p,
           title="Хост диктує темп: кадри 1 мс, у кожному — опитування точок")


# ── transfer-types: чотири типи, гарантія часу проти гарантії доставки ─────────
# Ідея: таблиця-матриця. Видно, що кожен тип жертвує чимось одним; тільки
# isochronous відмовляється від повтору заради сталого часу.

def fig_transfer_types():
    W, H = 820, 430
    p = []
    cols = [(80, "Тип"), (235, "Доставка"), (330, "Час"), (430, "Повтор"), (615, "Де застосовують")]
    for cx, lab in cols:
        p.append(text(cx, 58, lab, size=12, color=INK, bold=True))
    p.append(line(32, 73, 788, 73, color=LINE, sw=1.0))

    rows = [
        ("Control", PURPLE, "#f5eef8", "так", FIELD, "—", MUTED, "так", FIELD, "Енумерація, команди (EP0)"),
        ("Bulk", FIELD, BG, "так", FIELD, "—", MUTED, "так", FIELD, "Флешка, CDC-порт (велика смуга)"),
        ("Interrupt", ORANGE, "#fef9ec", "так", FIELD, "так", ORANGE, "так", FIELD, "Миша, клавіатура (макс. затримка)"),
        ("Isochronous", POS, BG, "—", MUTED, "так", ORANGE, "—", POS, "Аудіо, відео (смуга без повтору)"),
    ]
    ry = 81
    rh = 80
    for name, ncol, rfill, dlv, dcol, tm, tcol, rt, rtc, app in rows:
        if rfill != BG:
            p.append(rect(32, ry, 756, rh, fill=rfill, stroke="none", sw=0, rx=4))
        cy = ry + rh / 2 + 5
        p.append(text(80, cy, name, size=15, color=ncol, bold=True))
        p.append(text(235, cy, dlv, size=13, color=dcol, bold=True))
        p.append(text(330, cy, tm, size=13, color=tcol, bold=True))
        p.append(text(430, cy, rt, size=13, color=rtc, bold=True))
        p.append(text(615, cy, app, size=11, color=INK))
        ry += rh

    p.append(text(W / 2, 418, "Control і Bulk дають доставку; Interrupt і Isochronous дають час; повтору нема лише в Isochronous",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "transfer-types.svg"), W, H, *p,
           title="Чотири типи передач: гарантія часу проти гарантії доставки")


# ── polling-rate: bInterval interrupt-точки задає темп звітів ──────────────────
# Ідея: два ряди міток на осі часу. Менший bInterval → густіші опитування →
# менша затримка, але більше навантаження.

def fig_polling_rate():
    W, H = 760, 320
    p = []

    def ruler(y, n, color, head, sub):
        p.append(text(60, y - 12, head, size=13, color=color, anchor="start", bold=True))
        p.append(text(60, y + 8, sub, size=12, color=color, anchor="start"))
        x0, x1 = 260, 700
        p.append(line(x0, y, x1, y, color=MUTED, sw=1.0))
        p.append(text(x1 + 10, y + 5, "t", size=12, color=MUTED, anchor="start"))
        for i in range(n + 1):
            xx = x0 + (x1 - x0) * i / n
            p.append(line(xx, y - 16, xx, y + 6, color=color, sw=2.0))

    ruler(80, 8, ORANGE, "bInterval = 8 мс", "125 опитувань/с — звичайна миша")
    p.append(text(480, 116, "8 мс між опитуваннями → 125 Гц", size=11, color=MUTED))

    ruler(190, 16, NEG, "bInterval = 1 мс", "1000 опитувань/с — ігрова миша")
    p.append(text(480, 226, "1 мс між опитуваннями → 1000 Гц", size=11, color=MUTED))

    note = fitbox(90, 278, 580, 32,
                  "Частіше = менша затримка курсора, але більше навантаження на шину й хост",
                  size=12, fill=FILL, stroke=MUTED, sw=1.2)
    p.append(note)

    render(os.path.join(OUT, "polling-rate.svg"), W, H, *p,
           title="Чому миша «125 Гц» і «1000 Гц»: bInterval interrupt-точки")


# ── frame-schedule (для вставки proj-frames): порожні кадри між опитуваннями ───
# Ідея: точка з bInterval=8 дістає IN-токен лише в кадрах 0 і 8; між ними хост
# заповнює час іншим трафіком, а сама точка простоює.

def fig_frame_schedule():
    W, H = 860, 320
    p = []
    axis_y = 200
    p.append(arrow(50, axis_y, 810, axis_y, color=INK, sw=2.0))
    p.append(text(822, axis_y + 5, "t", size=15, color=INK, anchor="start", bold=True))

    n = 8
    fx0 = 70
    fw = 88
    fy = 110
    fh = 70
    for i in range(n + 1):
        xx = fx0 + i * fw
        p.append(line(xx, axis_y - 8, xx, axis_y + 8, color=INK, sw=1.8))
        p.append(text(xx, axis_y + 22, "%d мс" % i, size=11, color=MUTED))

    for i in range(n):
        bx = fx0 + i * fw
        p.append(rect(bx, fy, fw, fh, fill="#f0f4fa", stroke=LINE, sw=1.2, rx=4))
        # SOF на початку кожного кадру
        p.append(rect(bx + 2, fy + 4, 16, fh - 8, fill="#ffe9cc", stroke="#c8802a", sw=1.0, rx=3))
        p.append(text(bx + 10, fy + fh / 2 + 3, "SOF", size=9, color="#8a5000"))
        if i == 0:
            # IN-токен interrupt-точці
            p.append(rect(bx + 22, fy + 4, fw - 26, fh - 8, fill="#ddeeff", stroke=NEG, sw=1.5, rx=3))
            p.append(mtext(bx + 22 + (fw - 26) / 2, fy + fh / 2 - 2, ["IN", "→ DATA"], size=9, color=INK))
        else:
            p.append(rect(bx + 22, fy + 4, fw - 26, fh - 8, fill="#e8f4ec", stroke=FIELD, sw=1.0, rx=3))
            p.append(text(bx + 22 + (fw - 26) / 2, fy + fh / 2 + 3, "bulk", size=9, color=FIELD))
    # останній кадр (8 мс) знову дістає IN-токен — починаємо новий період
    bx = fx0 + n * fw
    # позначка наступного опитування стрілкою згори
    for cx in (fx0 + 0.5 * fw, fx0 + (n - 0.0) * fw):
        pass
    p.append(line(fx0 + fw / 2, 70, fx0 + fw / 2, 104, color=NEG, sw=2.0))
    p.append('<line x1="%.1f" y1="70" x2="%.1f" y2="104" stroke="%s" stroke-width="2.0" marker-end="url(#arrow)"/>'
             % (fx0 + fw / 2, fx0 + fw / 2, NEG))
    p.append(line(fx0 + n * fw + fw / 2 if False else fx0 + 7.5 * fw, 70,
                  fx0 + 7.5 * fw, 104, color=NEG, sw=2.0))
    note1 = fitbox(fx0 + 0.5 * fw - 60, 40, 120, 28, "IN-токен", size=10, fill="#ddeeff", stroke=NEG, sw=1.4)
    p.append(note1)

    p.append(text(W / 2, 270, "bInterval = 8: interrupt-точка дістає IN-токен раз на 8 кадрів (8 мс → 125 Гц)",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 292, "проміжні кадри хост заповнює bulk/control — сама точка простоює",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "frame-schedule.svg"), W, H, *p,
           title="Розклад кадрів Full-Speed: один IN-токен на bInterval")


if __name__ == "__main__":
    fig_endpoints()
    fig_bus_tempo()
    fig_transfer_types()
    fig_polling_rate()
    fig_frame_schedule()
    print("OK: figures written to", OUT)
