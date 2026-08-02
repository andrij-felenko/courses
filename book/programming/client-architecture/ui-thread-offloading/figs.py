# -*- coding: utf-8 -*-
"""Фігури до теми «Розвантаження потоку інтерфейсу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"
COOL = "#eaf0fd"
GOOD = "#e8f6ee"


# ── 1. Кадровий термін і довга задача ────────────────────────────────────────
def frame_timeline():
    W, H = 1060, 520
    f = []

    x0, x1 = 250.0, 1010.0
    span = x1 - x0

    # ── доріжка А: один нормальний кадр
    yA, hA = 100.0, 52.0
    f.append(fitbox(40, yA, 195, hA, "один кадр\n16.67 мс (60 Гц)", size=13, bold=True, fill=COOL))

    segs = [("події", 1.5), ("обробники", 3.0), ("розкладка", 3.2),
            ("малювання", 5.0), ("композиція", 2.0), ("запас", 2.0)]
    total = sum(s[1] for s in segs)
    px = span / total
    cur = x0
    for name, ms in segs:
        w = ms * px
        fill = GOOD if name == "запас" else FILL
        f.append(fitbox(cur, yA, w, hA, name, size=12, fill=fill))
        f.append(text(cur + w / 2, yA + hA + 20, "%.1f мс" % ms, size=11, color=MUTED))
        cur += w

    for x in (x0, x1):
        f.append(line(x, yA - 22, x, yA + hA + 30, color=NEG, sw=1.6, dash="4,4"))
    f.append(text(x0, yA - 28, "vsync", size=11, color=NEG))
    f.append(text(x1, yA - 28, "vsync", size=11, color=NEG))

    # ── доріжка Б: довга задача
    yB, hB = 250.0, 52.0
    f.append(fitbox(40, yB, 195, hB, "довга задача\nна тому самому потоці", size=12, bold=True, fill=WARM))

    step = span / 12.0
    f.append(text((x0 + x1) / 2, yB - 35, "vsync кожні 16.67 мс", size=11, color=MUTED))
    for i in range(13):
        x = x0 + step * i
        f.append(line(x, yB - 25, x, yB, color=NEG, sw=1.4, dash="4,4"))
    f.append(fitbox(x0, yB, span, hB, "розбір JSON — 200 мс", size=16, bold=True,
                    fill=WARM, stroke=POS, sw=2))
    for i in range(12):
        f.append(text(x0 + step * (i + 0.5), yB + hB + 24, "✗", size=14, color=POS, bold=True))
    f.append(text((x0 + x1) / 2, yB + hB + 52,
                  "12 кадрів не намальовано — на екрані стоїть той самий старий кадр",
                  size=12.5))

    # ── черга вводу
    yQ = 390.0
    f.append(text(250, yQ + 24, "черга вводу:", size=12.5, anchor="start", bold=True))
    qx = 380.0
    for lab in ("клік", "клік", "прокрутка"):
        b, w, h = textbox(0, 0, lab, size=12, fill=COOL, stroke=NEG)
        f.append(fitbox(qx, yQ, w + 14, 38, lab, size=12, fill=COOL, stroke=NEG))
        qx += w + 24
    f.append(text(qx + 16, yQ + 24, "жодна подія не вибрана з циклу", size=12.5, anchor="start", color=MUTED))

    f.append(text(W / 2, 478,
                  "після ~5 с без вибирання повідомлень ОС оголошує вікно таким, що не відповідає",
                  size=12, color=POS))

    render(os.path.join(OUT, "frame-timeline.svg"), W, H, *f,
           title="Кадр — це термін: що робить із ним одна довга задача")


# ── 2. Три способи перетнути межу даних ─────────────────────────────────────
def data_boundary():
    W, H = 1090, 480
    f = []

    panels = [
        (35.0, "копія", "час ∝ розміру даних",
         ["дані впаковуються в повідомлення",
          "й лягають у чергу другого потоку;",
          "спільної пам'яті немає, тож немає",
          "й гонок — але платиш за кожен байт"],
         "потік інтерфейсу не чекає", GOOD, "copy"),
        (385.0, "передача власності", "час сталий, розмір не важить",
         ["рухається лише покажчик;",
          "відправник утрачає доступ,",
          "тож у кожної одиниці даних",
          "будь-коли рівно один власник"],
         "потік інтерфейсу не чекає", GOOD, "move"),
        (735.0, "спільна пам'ять під замком", "копіювання немає, є очікування",
         ["доступ без копії, зате замок",
          "повертає в систему саме те,",
          "що ми виганяли, — право",
          "потоку інтерфейсу стояти"],
         "потік інтерфейсу може стояти", WARM, "share"),
    ]

    PW = 320.0
    for px, head, cost, desc, verdict, vfill, kind in panels:
        f.append(rect(px, 70, PW, 320, fill=BG, stroke=MUTED, sw=1.4))
        f.append(text(px + PW / 2, 100, head, size=15, bold=True))

        if kind in ("copy", "move"):
            f.append(fitbox(px + 30, 128, 110, 40, "інтерфейс", size=12, fill=COOL))
            f.append(fitbox(px + 180, 128, 110, 40, "фон", size=12, fill=FILL))
            f.append(arrow(px + 145, 148, px + 175, 148, color=NEG))
            if kind == "copy":
                f.append(fitbox(px + 30, 178, 110, 32, "дані", size=12, fill=FILL))
                f.append(fitbox(px + 180, 178, 110, 32, "копія даних", size=12, fill=FILL))
            else:
                f.append(fitbox(px + 30, 178, 110, 32, "порожньо", size=12,
                                fill=BG, stroke=MUTED))
                f.append(fitbox(px + 180, 178, 110, 32, "дані", size=12, fill=FILL))
        else:
            f.append(fitbox(px + 30, 128, 110, 40, "інтерфейс", size=12, fill=COOL))
            f.append(fitbox(px + 180, 128, 110, 40, "фон", size=12, fill=FILL))
            f.append(fitbox(px + 85, 178, 150, 32, "спільні дані", size=12,
                            fill=WARM, stroke=POS))
            f.append(arrow(px + 85, 168, px + 130, 178, color=POS))
            f.append(arrow(px + 235, 168, px + 190, 178, color=POS))

        f.append(text(px + PW / 2, 234, cost, size=12.5, color=MUTED, italic=True))
        f.append(mtext(px + PW / 2, 262, desc, size=12))
        f.append(fitbox(px + 20, 336, PW - 40, 40, verdict, size=13, bold=True,
                        fill=vfill, stroke=(POS if vfill == WARM else FIELD)))

    f.append(text(W / 2, 430,
                  "перші два різняться ціною, третій — природою: лише він повертає потоку інтерфейсу здатність чекати",
                  size=12.5))

    render(os.path.join(OUT, "data-boundary.svg"), W, H, *f,
           title="Межа даних: три способи перетнути її й що при цьому робить потік інтерфейсу")


# ── 3. Гонка зворотного шляху й лічильник поколінь ──────────────────────────
def stale_result():
    W, H = 1000, 580
    f = []

    XU, XB = 260.0, 740.0
    f.append(fitbox(XU - 110, 52, 220, 36, "потік інтерфейсу", size=13, bold=True, fill=COOL))
    f.append(fitbox(XB - 100, 52, 200, 36, "фоновий пул", size=13, bold=True, fill=FILL))

    boxes = [
        (130.0, 'запит "ab" · покоління 7', FILL, LINE),
        (220.0, 'запит "abc" · покоління 8', FILL, LINE),
        (365.0, "покоління 8 = поточне → малюємо", GOOD, FIELD),
        (475.0, "покоління 7 ≠ 8 → відкидаємо", WARM, POS),
    ]

    occupied = []
    for cy, label, fill, stroke in boxes:
        body, w, h = textbox(XU, cy, label, size=13, fill=fill, stroke=stroke)
        f.append(body)
        occupied.append((cy - h / 2 - 3, cy + h / 2 + 3))

    # лінії життя — сегментами, щоб не перетинати підписи
    top, bottom = 96.0, 508.0
    cur = top
    for a, b in occupied:
        if a > cur:
            f.append(line(XU, cur, XU, a, color=MUTED, sw=1.4, dash="5,5"))
        cur = max(cur, b)
    if cur < bottom:
        f.append(line(XU, cur, XU, bottom, color=MUTED, sw=1.4, dash="5,5"))
    f.append(line(XB, top, XB, bottom, color=MUTED, sw=1.4, dash="5,5"))

    msgs = [
        (175.0, "робота 7", True, NEG),
        (262.0, "робота 8", True, NEG),
        (320.0, "результат 8 (готовий раніше)", False, FIELD),
        (430.0, "результат 7 (спізнився)", False, POS),
    ]
    for y, label, to_bg, color in msgs:
        if to_bg:
            f.append(arrow(XU + 12, y, XB - 12, y, color=color))
        else:
            f.append(arrow(XB - 12, y, XU + 12, y, color=color))
        f.append(text((XU + XB) / 2, y - 11, label, size=12, color=color))

    f.append(text(W / 2, 548,
                  "без лічильника поколінь на екрані лишився б результат запиту, якого вже немає",
                  size=12.5))

    render(os.path.join(OUT, "stale-result.svg"), W, H, *f,
           title="Порядок відповідей не пов'язаний із порядком запитів")


# ── 4. Необмежена черга проти скрині на одне місце ──────────────────────────
def mailbox():
    W, H = 1020, 450
    f = []

    # ліва панель
    px = 35.0
    PW = 460.0
    f.append(rect(px, 70, PW, 320, fill=BG, stroke=MUTED, sw=1.4))
    f.append(text(px + PW / 2, 100, "необмежена черга", size=15, bold=True))

    sx = px + 55
    f.append(text(sx + 70, 124, "надходить 10 завдань/с", size=12, color=NEG))
    f.append(arrow(sx + 70, 132, sx + 70, 152, color=NEG))
    yy = 158.0
    for i in range(5):
        f.append(rect(sx, yy, 140, 26, fill=(FILL if i else COOL), stroke=LINE, sw=1.2))
        yy += 30
    f.append(rect(sx, yy, 140, 26, fill=GOOD, stroke=FIELD, sw=1.6))
    f.append(text(sx + 70, yy + 46, "встигаємо 3/с", size=12, color=FIELD))
    f.append(arrow(sx + 70, yy + 28, sx + 70, yy + 34, color=FIELD))
    f.append(mtext(sx + 165, 210, ["черга росте", "без межі, кожна", "відповідь усе", "старіша"],
                   size=12, anchor="start", color=POS))

    # права панель
    qx = 525.0
    f.append(rect(qx, 70, PW, 320, fill=BG, stroke=MUTED, sw=1.4))
    f.append(text(qx + PW / 2, 100, "скриня на одне місце", size=15, bold=True))

    mx = qx + 55
    f.append(text(mx + 75, 124, "надходить 10 завдань/с", size=12, color=NEG))
    f.append(arrow(mx + 75, 132, mx + 75, 216, color=NEG))
    f.append(rect(mx, 224, 150, 46, fill=GOOD, stroke=FIELD, sw=1.8))
    f.append(text(mx + 75, 252, "останнє завдання", size=12))
    f.append(arrow(mx + 158, 247, mx + 210, 247, color=MUTED))
    f.append(mtext(mx + 218, 240, ["старіші зникають", "ще до роботи"],
                   size=12, anchor="start", color=MUTED))
    f.append(arrow(mx + 75, 278, mx + 75, 306, color=FIELD))
    f.append(text(mx + 75, 326, "рахуємо лише останній", size=12, color=FIELD))

    f.append(text(W / 2, 424,
                  "коли надходження стабільно швидше за обслуговування, черга — це просто повільніше зависання",
                  size=12.5))

    render(os.path.join(OUT, "mailbox.svg"), W, H, *f,
           title="Куди дівати роботу, що приходить швидше, ніж робиться")


# ── 5. Драбина розвантаження: що виграєш і чим платиш ───────────────────────
def offload_ladder():
    W, H = 1090, 470
    f = []

    panels = [
        (30.0, "не робити\nроботи", GOOD,
         ["роботи немає зовсім —", "найдешевша перемога"],
         ["треба глибше зрозуміти", "саму задачу"]),
        (295.0, "порізати на шматки\nна тому самому потоці", COOL,
         ["межі даних немає,", "замків теж немає"],
         ["загальний час росте,", "світ міняється", "між шматками"]),
        (560.0, "винести\nв інший потік", COOL,
         ["справжня паралельність:", "рахує окреме ядро"],
         ["межа даних і зворотний", "шлях з усіма гонками"]),
        (825.0, "винести в інший\nпроцес або пристрій", WARM,
         ["збій не тягне", "за собою вікно"],
         ["протокол: серіалізація,", "таймаути, часткові", "відмови"]),
    ]

    PW = 235.0
    for px, head, hfill, gain, cost in panels:
        f.append(rect(px, 95, PW, 250, fill=BG, stroke=MUTED, sw=1.4))
        f.append(fitbox(px + 12, 108, PW - 24, 54, head, size=13, bold=True, fill=hfill))
        f.append(text(px + PW / 2, 192, "виграє", size=12, color=FIELD, bold=True))
        f.append(mtext(px + PW / 2, 214, gain, size=12))
        f.append(text(px + PW / 2, 276, "платить", size=12, color=POS, bold=True))
        f.append(mtext(px + PW / 2, 298, cost, size=12))

    f.append(arrow(60, 388, 1030, 388, color=MUTED, sw=2))
    f.append(text(W / 2, 425, "ціна межі, яку створюєш, росте зліва направо",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "offload-ladder.svg"), W, H, *f,
           title="Чотири щаблі розвантаження: від «не робити» до чужого процесу")


# ── 6. Чому замок не рятує: цикл через межу володіння (вставка hist) ─────────
def hist_lock_cycle():
    W, H = 1080, 470
    f = []

    f.append(fitbox(70, 150, 300, 100, "код застосунку\nвласний замок моделі",
                    size=14, bold=True, fill=COOL))
    f.append(fitbox(710, 150, 300, 100, "код оболонки\nзамок дерева елементів",
                    size=14, bold=True, fill=FILL))

    # напрямок 1: застосунок кличе оболонку
    f.append(arrow(380, 132, 700, 132, color=NEG, sw=2))
    f.append(mtext(540, 78, ["застосунок кличе оболонку",
                             "тримає замок моделі,",
                             "просить замок дерева"], size=12, color=NEG))

    # напрямок 2: оболонка кличе застосунок (зворотний виклик)
    f.append(arrow(700, 288, 380, 288, color=POS, sw=2))
    f.append(mtext(540, 314, ["оболонка кличе застосунок",
                              "тримає замок дерева,",
                              "просить замок моделі"], size=12, color=POS))

    body, w, h = textbox(540, 205, "два порядки захоплення\n= цикл очікування",
                         size=13, bold=True, fill=WARM, stroke=POS, sw=2)
    f.append(body)

    f.append(text(W / 2, 392,
                  "Жоден бік не володіє обома замками, і кожен напрямок — цілком нормальний код.",
                  size=13))
    f.append(text(W / 2, 418,
                  "Спільного порядку захоплення просто нема кому призначити.",
                  size=13))
    f.append(text(W / 2, 448,
                  "Ліки, що лишаються: замків не мати взагалі — дерево чіпає рівно один потік.",
                  size=13, color=FIELD, bold=True))

    render(os.path.join(OUT, "hist-lock-cycle.svg"), W, H, *f,
           title="Зворотні виклики роблять порядок захоплення замків неможливим")


# ── 7. Хроніка збігу: як усі прийшли до одного власника (вставка hist) ───────
def hist_convergence():
    W, H = 1180, 560
    f = []

    AX = 300.0
    x0, x1 = 95.0, 1085.0
    marks = [
        ("1985", "Windows 1.0", "потоків у системі\nнемає взагалі:\nодна черга подій", FILL),
        ("1987", "X11", "клієнт — одна\nнитка виконання\nз циклом подій", FILL),
        ("1993", "Win32 (NT 3.1)", "потоки з'явилися,\nа черга лишилася\nна кожен потік", COOL),
        ("1996", "AWT (JDK 1.0)", "спроба зробити\nпотокобезпечно:\nзамок на дереві", WARM),
        ("1997", "Swing", "правило одного\nпотоку замість\nзамків", GOOD),
        ("2004", "запис Гамільтона", "підсумок: винні\nпорядки захоплення\nзамків", GOOD),
        ("2006", "Goetz, розділ 9", "той самий дедлок\nрозібрано\nформально", GOOD),
        ("2008", "Android 1.0", "правило записане\nв документації\nз першого дня", GOOD),
    ]

    step = (x1 - x0) / (len(marks) - 1)
    BW, BH = 148.0, 130.0

    f.append(line(x0 - 45, AX, x1 + 45, AX, color=MUTED, sw=2))

    for i, (year, who, what, fill) in enumerate(marks):
        cx = x0 + step * i
        up = (i % 2 == 0)
        by = AX - 34 - BH if up else AX + 34
        f.append(line(cx, AX, cx, by + (BH if up else 0), color=MUTED, sw=1.4, dash="4,4"))
        f.append(circle(cx, AX, 7, fill=fill, stroke=LINE, sw=1.8))
        f.append(fitbox(cx - BW / 2, by, BW, 46, year + "\n" + who,
                        size=12.5, bold=True, fill=fill))
        f.append(fitbox(cx - BW / 2, by + 48, BW, BH - 48, what, size=11.5,
                        fill=BG, stroke=MUTED, sw=1.1))

    f.append(rect(95, 478, 990, 62, fill=GOOD, stroke=FIELD, sw=1.6))
    f.append(mtext(W / 2, 502,
                   ["Різні компанії, різні мови, різні десятиліття —",
                    "і той самий висновок: дерево елементів має рівно одного власника-потік"],
                   size=13, bold=True))

    render(os.path.join(OUT, "hist-convergence.svg"), W, H, *f,
           title="Вісім разів окремо — і щоразу той самий висновок")


# ── 8. Ймовірність чистої секунди (вставка math) ─────────────────────────────
def math_clean_second():
    W, H = 1040, 560
    f = []

    XL, XR = 150.0, 960.0        # p від 1e-4 до 1e-1 (три декади)
    YT, YB = 90.0, 430.0         # значення від 1 до 0

    def X(p):
        import math as m
        return XL + (XR - XL) * (m.log10(p) + 4.0) / 3.0

    def Y(v):
        return YB - (YB - YT) * v

    # ── осі
    f.append(line(XL, YT - 10, XL, YB, color=MUTED, sw=1.6))
    f.append(line(XL, YB, XR + 12, YB, color=MUTED, sw=1.6))

    for v, lab in ((1.0, "1.0"), (0.75, "0.75"), (0.5, "0.5"), (0.25, "0.25"), (0.0, "0")):
        y = Y(v)
        f.append(line(XL - 6, y, XL, y, color=MUTED, sw=1.4))
        f.append(text(XL - 12, y + 4, lab, size=12, color=MUTED, anchor="end"))
    f.append(text(XL - 12, YT - 26, "частка чистих секунд", size=12.5,
                  color=MUTED, anchor="start"))

    for p, lab in ((1e-4, "0.0001"), (1e-3, "0.001"), (1e-2, "0.01"), (1e-1, "0.1")):
        x = X(p)
        f.append(line(x, YB, x, YB + 6, color=MUTED, sw=1.4))
        f.append(text(x, YB + 24, lab, size=12, color=MUTED))
    f.append(text((XL + XR) / 2, YB + 54, "p — ймовірність, що окремий кадр не встиг", size=13))

    # ── крива (1−p)^60
    pts = []
    for i in range(0, 241):
        lp = -4.0 + 3.0 * i / 240.0
        p = 10.0 ** lp
        pts.append((X(p), Y((1.0 - p) ** 60)))
    f.append('<polyline fill="none" stroke="%s" stroke-width="2.8" points="%s"/>'
             % (POS, " ".join("%.1f,%.1f" % q for q in pts)))

    # ── рівень 95 %
    f.append(line(XL, Y(0.95), XR, Y(0.95), color=FIELD, sw=1.6, dash="6,5"))
    f.append(text(XR - 4, Y(0.95) - 10, "95 %", size=12.5, color=FIELD,
                  anchor="end", bold=True))

    xg = X(8.545e-4)
    f.append(circle(xg, Y(0.95), 5.5, fill=BG, stroke=FIELD, sw=2.2))
    f.append(line(xg, Y(0.95) + 8, xg, 268, color=FIELD, sw=1.4, dash="4,4"))
    body, bw, bh = textbox(310, 300, "щоб 95 % секунд були чисті,\n"
                                     "потрібно p ≈ 0.00085 —\n"
                                     "один поганий кадр із 1170",
                           size=13, fill=GOOD, stroke=FIELD, sw=1.6)
    f.append(body)

    # ── точка p = 0.01
    f.append(circle(X(0.01), Y(0.5472), 5.5, fill=BG, stroke=POS, sw=2.2))
    body, bw, bh = textbox(820, 175, "p = 0.01 → 55 %\n(p99 рівно на терміні)",
                           size=13, fill=WARM, stroke=POS, sw=1.6)
    f.append(body)
    f.append(line(750, 207, X(0.01) + 6, Y(0.5472) - 8, color=POS, sw=1.3))

    # ── точка p = 0.05
    f.append(circle(X(0.05), Y(0.0461), 5.5, fill=BG, stroke=POS, sw=2.2))
    body, bw, bh = textbox(640, 380, "p = 0.05 → 4.6 %:\nчистих секунд майже нема",
                           size=13, fill=WARM, stroke=POS, sw=1.6)
    f.append(body)
    f.append(line(743, 392, X(0.05) - 7, Y(0.0461) + 3, color=POS, sw=1.3))

    render(os.path.join(OUT, "math-clean-second.svg"), W, H, *f,
           title="Секунда без жодного пропущеного кадру при 60 Гц: (1 − p)⁶⁰")


# ── 9. Бюджет коду проти частоти оновлення (вставка math) ────────────────────
def math_budget_vs_hz():
    W, H = 1040, 580
    f = []

    E = 6.0                       # частка рушія, мс на кадр
    FL, FR = 50.0, 170.0
    XL, XR = 150.0, 960.0
    YT, YB = 90.0, 400.0
    BMAX = 14.0

    def X(fr):
        return XL + (XR - XL) * (fr - FL) / (FR - FL)

    def Y(b):
        return YB - (YB - YT) * b / BMAX

    f.append(line(XL, YT - 10, XL, YB, color=MUTED, sw=1.6))
    f.append(line(XL, YB, XR + 12, YB, color=MUTED, sw=1.6))

    for b in (0, 5, 10, 14):
        y = Y(b)
        f.append(line(XL - 6, y, XL, y, color=MUTED, sw=1.4))
        f.append(text(XL - 12, y + 4, str(b), size=12, color=MUTED, anchor="end"))
    f.append(text(XL - 12, YT - 26, "B — бюджет коду в кадрі, мс", size=12.5,
                  color=MUTED, anchor="start"))
    f.append(text(XL, YB + 22, "50 Гц", size=12, color=MUTED))
    f.append(text(XR, YB + 22, "170 Гц", size=12, color=MUTED))

    pts = []
    for i in range(0, 241):
        fr = FL + (1000.0 / E - FL) * i / 240.0
        pts.append((X(fr), Y(1000.0 / fr - E)))
    f.append('<polyline fill="none" stroke="%s" stroke-width="2.8" points="%s"/>'
             % (POS, " ".join("%.1f,%.1f" % q for q in pts)))

    # ── асимптота: бюджет обертається на нуль
    xa = X(1000.0 / E)
    f.append(line(xa, YT - 10, xa, YB + 8, color=NEG, sw=1.6, dash="6,5"))
    body, bw, bh = textbox(745, 152, "1/e ≈ 167 Гц —\nбюджет коду обертається на нуль",
                           size=13, fill=COOL, stroke=NEG, sw=1.6)
    f.append(body)
    f.append(line(881, 168, xa - 4, 210, color=NEG, sw=1.3))

    # ── чотири частоти: підписи окремим рядом під віссю
    marks = [(60.0, 217.5), (90.0, 420.0), (120.0, 622.5), (144.0, 800.0)]
    BW, BH = 142.0, 74.0
    for fr, bx in marks:
        b = 1000.0 / fr - E
        stretch = (1000.0 / fr) / b
        px, py = X(fr), Y(b)
        f.append(circle(px, py, 5.5, fill=BG, stroke=POS, sw=2.2))
        f.append(line(px, py + 8, bx, 448, color=MUTED, sw=1.3, dash="4,4"))
        f.append(fitbox(bx - BW / 2, 448, BW, BH,
                        "%d Гц\nB = %.1f мс\nрозтяг ×%.1f" % (int(fr), b, stretch),
                        size=12.5, fill=FILL))

    f.append(text(W / 2, 552,
                  "«розтяг» — у скільки разів довше йде та сама робота, "
                  "якщо різати її по бюджету кадру",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "math-budget-vs-hz.svg"), W, H, *f,
           title="B = 1/f − 6 мс: бюджет коду падає швидше за сам період кадру")


# ── 10. Черга без стелі проти скрині на одне місце (вставка math) ────────────
def math_queue_growth():
    W, H = 1000, 620
    f = []

    XL, XR = 150.0, 940.0
    LAM, MU = 10.0, 1.0 / 0.3

    # ── панель А: черга без стелі
    AT, AB = 90.0, 330.0
    LMAX = 70.0

    def XA(t):
        return XL + (XR - XL) * t / 10.0

    def YA(l):
        return AB - (AB - AT) * l / LMAX

    f.append(line(XL, AT - 10, XL, AB, color=MUTED, sw=1.6))
    f.append(line(XL, AB, XR + 12, AB, color=MUTED, sw=1.6))
    for l in (0, 35, 70):
        y = YA(l)
        f.append(line(XL - 6, y, XL, y, color=MUTED, sw=1.4))
        f.append(text(XL - 12, y + 4, str(l), size=12, color=MUTED, anchor="end"))
    f.append(text(XL - 12, AT - 26, "черга без стелі: L, завдань", size=12.5,
                  color=MUTED, anchor="start"))

    f.append(line(XA(0), YA(0), XA(10), YA((LAM - MU) * 10), color=POS, sw=2.8))

    body, bw, bh = textbox(330, 150, "нахил = λ − μ = 6.67 завдання/с", size=13,
                           fill=WARM, stroke=POS, sw=1.6)
    f.append(body)

    f.append(circle(XA(5), YA((LAM - MU) * 5), 5.5, fill=BG, stroke=POS, sw=2.2))
    body, bw, bh = textbox(750, 285, "t = 5 с: 33 завдання чекають,\n"
                                     "вік найсвіжішої відповіді — 10 с",
                           size=13, fill=WARM, stroke=POS, sw=1.6)
    f.append(body)
    f.append(line(629, 280, XA(5) + 7, YA((LAM - MU) * 5) + 6, color=POS, sw=1.3))

    # ── панель Б: скриня на одне місце
    BT, BB = 420.0, 530.0

    def YB2(l):
        return BB - (BB - BT) * l / 4.0

    f.append(line(XL, BT - 10, XL, BB, color=MUTED, sw=1.6))
    f.append(line(XL, BB, XR + 12, BB, color=MUTED, sw=1.6))
    for l in (0, 2, 4):
        y = YB2(l)
        f.append(line(XL - 6, y, XL, y, color=MUTED, sw=1.4))
        f.append(text(XL - 12, y + 4, str(l), size=12, color=MUTED, anchor="end"))
    f.append(text(XL - 12, BT - 26, "скриня на одне місце: L, завдань", size=12.5,
                  color=MUTED, anchor="start"))

    f.append(line(XA(0), YB2(2), XA(10), YB2(2), color=FIELD, sw=2.8))
    f.append(text((XL + XR) / 2, 448,
                  "L ≤ 2 за будь-якого λ: вік відповіді ≤ 0.6 с, "
                  "а зайві 6.67 завдання/с відкидаються одразу",
                  size=13, color=FIELD, bold=True))

    for t in (0, 2, 4, 6, 8, 10):
        x = XA(t)
        f.append(line(x, BB, x, BB + 6, color=MUTED, sw=1.4))
        f.append(text(x, BB + 24, str(t), size=12, color=MUTED))
    f.append(text((XL + XR) / 2, BB + 52, "час від початку напливу, с", size=13))

    render(os.path.join(OUT, "math-queue-growth.svg"), W, H, *f,
           title="λ = 10/с проти μ = 3.33/с: без стелі черга росте лінійно")


# ── proj-1. Повний шлях запиту: п'ять воріт і три виходи ────────────────────
def proj_search_pipeline():
    W, H = 1080, 830
    f = []

    XU, XB = 230.0, 830.0
    CW = 320.0
    UX, BX = 70.0, 670.0

    f.append(fitbox(UX, 52, CW, 36, "потік інтерфейсу", size=13, bold=True, fill=COOL))
    f.append(fitbox(BX, 52, CW, 36, "фоновий потік", size=13, bold=True, fill=FILL))

    # колонка інтерфейсу: ворота 1–3
    f.append(fitbox(UX, 108, CW, 42, "натиск клавіші", size=13, fill=COOL))
    f.append(arrow(XU, 152, XU, 178))
    f.append(fitbox(UX, 180, CW, 58,
                    "ворота 1 · тиша 150 мс\nновий знак переставляє таймер", size=12.5))
    f.append(arrow(XU, 240, XU, 266))
    f.append(fitbox(UX, 268, CW, 58,
                    "ворота 2 · скриня на одне місце\nнестартоване завдання витісняється",
                    size=12.5))
    f.append(arrow(XU, 328, XU, 354))
    f.append(fitbox(UX, 356, CW, 42, "ворота 3 · штамп покоління N", size=12.5))

    # перехід через межу туди
    f.append(mtext(640, 344, ["завдання: текст, покоління N,", "прапорець скасування"],
                   size=11, color=MUTED))
    f.append(line(UX + CW, 377, XB, 377, color=NEG, sw=1.6))
    f.append(arrow(XB, 379, XB, 416, color=NEG))

    # колонка фону: ворота 4
    f.append(fitbox(BX, 418, CW, 52,
                    "робітник бере зі скрині\nлише останнє — старіші зникли", size=12.5))
    f.append(arrow(XB, 472, XB, 496))
    f.append(fitbox(BX, 498, CW, 72,
                    "ворота 4 · робочий цикл\nкожні 512 записів — погляд у прапорець\n"
                    "побачив — виходить достроково", size=12.5))

    # перехід через межу назад
    f.append(mtext(640, 592, ["маршалінг: одне з трьох закінчень",
                              "лягає в чергу потоку інтерфейсу"], size=11, color=MUTED))
    f.append(line(XB, 572, XB, 622, color=FIELD, sw=1.6))
    f.append(line(XB, 622, XU, 622, color=FIELD, sw=1.6))
    f.append(arrow(XU, 624, XU, 648, color=FIELD))

    # ворота 5 і три виходи
    f.append(fitbox(UX, 650, CW, 58, "ворота 5 · адресат живий?\nпокоління = поточне?",
                    size=12.5, fill=WARM, stroke=POS, sw=1.8))

    ends = [(60.0, "показати результат", GOOD, FIELD),
            (390.0, "показати помилку", WARM, POS),
            (720.0, "тихо вийти: скасовано", FILL, MUTED)]
    for ex, label, fill, stroke in ends:
        f.append(fitbox(ex, 736, 300, 48, label, size=13, bold=True, fill=fill, stroke=stroke))
    f.append(arrow(224, 710, 210, 734, color=FIELD))
    f.append(arrow(238, 710, 540, 734, color=POS))
    f.append(arrow(250, 710, 870, 734, color=MUTED))

    f.append(text(W / 2, 808,
                  "ворота 1 і 2 бережуть процесор, ворота 3 і 5 — правильність, ворота 4 — і те, і те",
                  size=12.5))

    render(os.path.join(OUT, "proj-search-pipeline.svg"), W, H, *f,
           title="Шлях одного натиску: п'ять воріт і три виходи")


# ── proj-2. Гонка на скрині: чому предикат читають під замком ───────────────
def proj_mailbox_race():
    W, H = 1100, 500
    f = []

    panels = [
        (30.0, "наївно: перевірити, потім заснути",
         [("робітник", "перевіряє: скриня порожня", FILL),
          ("інтерфейс", "кладе завдання у скриню", COOL),
          ("інтерфейс", "notify_one() — спати ще ніхто не ліг", COOL),
          ("робітник", "аж тепер заходить у wait і засинає", WARM)],
         "завдання лежить у скрині, спінер крутиться вічно", WARM, POS),
        (560.0, "правильно: перевірити й заснути неподільно",
         [("робітник", "бере замок, предикат has_ хибний", FILL),
          ("робітник", "cv.wait відпускає замок і засинає", FILL),
          ("інтерфейс", "бере замок, has_ = true, notify_one()", COOL),
          ("робітник", "прокидається, предикат істинний — бере", GOOD)],
         "перевірка й засинання неподільні — прокол неможливий", GOOD, FIELD),
    ]

    PW = 510.0
    for px, head, rows, verdict, vfill, vstroke in panels:
        f.append(rect(px, 58, PW, 372, fill=BG, stroke=MUTED, sw=1.4))
        f.append(text(px + PW / 2, 90, head, size=14, bold=True))
        yy = 112.0
        for i, (who, what, fill) in enumerate(rows):
            f.append(fitbox(px + 16, yy, 112, 46, "%d · %s" % (i + 1, who), size=11,
                            fill=(COOL if who == "інтерфейс" else FILL)))
            f.append(fitbox(px + 140, yy, 354, 46, what, size=12, fill=fill))
            yy += 56
        f.append(fitbox(px + 16, 336, 478, 64, verdict, size=13, bold=True,
                        fill=vfill, stroke=vstroke, sw=1.8))

    f.append(text(W / 2, 468,
                  "різниця одна: праворуч стан скрині читають під тим самим замком, під яким його міняють",
                  size=12.5))

    render(os.path.join(OUT, "proj-mailbox-race.svg"), W, H, *f,
           title="Гонка на скрині: чому прапорець «є завдання» читають під замком")


frame_timeline()
data_boundary()
stale_result()
mailbox()
offload_ladder()
hist_lock_cycle()
hist_convergence()
math_clean_second()
math_budget_vs_hz()
math_queue_growth()
proj_search_pipeline()
proj_mailbox_race()
print("ok:", os.listdir(OUT))
