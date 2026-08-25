# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Протокол CRSF».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Запуск:  python figs.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Анатомія кадру CRSF: базовий і розширений ─────────────────────────────
# Ідея: кадр — це рівно п'ять полів на дроті; поле «довжина» рахує ЛИШЕ те,
# що після нього (тип+дані+CRC), а CRC накриває тип+дані. Розширений кадр
# усуває дві адреси одразу після типу — і решта та сама.
def fig_frame():
    W, H = 940, 420
    P = [text(W / 2, 30, "Кадр CRSF: п'ять полів байтами на дроті", size=17, bold=True)]

    def cell(x, y, w, lab, sub, fill, col):
        P.append(rect(x, y, w, 54, fill=fill, stroke=col, sw=1.6, rx=6))
        P.append(text(x + w / 2, y + 24, lab, size=12, bold=True, color=col))
        if sub:
            P.append(text(x + w / 2, y + 42, sub, size=9.5, color=MUTED))

    # ── базовий кадр ──
    y1 = 90
    P.append(text(70, y1 - 14, "Базовий кадр (тип < 0x28):", size=12.5, bold=True, anchor="start"))
    xs = 70
    fields = [
        (70, "0xC8", "адреса/старт", "#eef6ef", FIELD),
        (100, "LEN", "довжина", "#f4f6f8", INK),
        (100, "TYPE", "тип кадру", "#eef2f7", NEG),
        (330, "PAYLOAD", "дані (0…60 Б)", "#f4f6f8", INK),
        (100, "CRC8", "контроль", "#fdecea", POS),
    ]
    x = xs
    span = []
    for w, lab, sub, fill, col in fields:
        cell(x, y1, w, lab, sub, fill, col)
        span.append((x, w))
        x += w + 4
    # дужка «LEN рахує це»: від початку TYPE до кінця CRC
    lx0 = span[2][0]
    lx1 = span[4][0] + span[4][1]
    by = y1 + 74
    P.append(line(lx0, by, lx1, by, color=NEG, sw=1.6))
    P.append(line(lx0, by, lx0, by - 8, color=NEG, sw=1.6))
    P.append(line(lx1, by, lx1, by - 8, color=NEG, sw=1.6))
    P.append(text((lx0 + lx1) / 2, by + 16, "LEN рахує саме це: тип + дані + CRC (2…62)", size=10.5, color=NEG))
    # дужка «CRC накриває це»: від початку TYPE до кінця PAYLOAD
    cx0 = span[2][0]
    cx1 = span[3][0] + span[3][1]
    cy = y1 - 10
    P.append(line(cx0, cy, cx1, cy, color=POS, sw=1.6))
    P.append(line(cx0, cy, cx0, cy + 8, color=POS, sw=1.6))
    P.append(line(cx1, cy, cx1, cy + 8, color=POS, sw=1.6))
    P.append(text((cx0 + cx1) / 2, cy - 6, "CRC8 накриває тип + дані", size=10.5, color=POS, bold=True))

    # ── розширений кадр ──
    y2 = 270
    P.append(text(70, y2 - 14, "Розширений кадр (тип ≥ 0x28): та сама рамка + дві адреси одразу після типу",
                  size=12.5, bold=True, anchor="start"))
    fields2 = [
        (70, "0xC8", "старт", "#eef6ef", FIELD),
        (90, "LEN", "довжина", "#f4f6f8", INK),
        (90, "TYPE", "тип", "#eef2f7", NEG),
        (95, "DEST", "кому", "#fef6e8", "#b8860b"),
        (95, "ORIG", "від кого", "#fef6e8", "#b8860b"),
        (260, "PAYLOAD", "дані", "#f4f6f8", INK),
        (90, "CRC8", "контроль", "#fdecea", POS),
    ]
    x = 70
    for w, lab, sub, fill, col in fields2:
        cell(x, y2, w, lab, sub, fill, col)
        x += w + 4
    P.append(text(W / 2, H - 22,
                  "адреса на початку — і старт кадру, і «хто говорить»: 0xC8 = польотний контролер, 0xEE = TX-модуль, 0xEC = приймач",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "frame.svg"), W, H, *P)


# ── 2. RC-канали: 16 × 11 бітів набиті впритул у 22 байти ────────────────────
# Ідея (важка словами): 11 біт на канал НЕ кратні 8, тож канали НЕ вирівняні
# по байтах — вони «переливаються» через межі байтів. Це видно як зсув.
def fig_packing():
    W, H = 940, 420
    P = [text(W / 2, 30, "RC-канали: 11 бітів × 16 набиті впритул у 22 байти", size=17, bold=True)]

    # верх: лінійка бітів 0..32, зверху — межі байтів, знизу — межі каналів
    x0, x1 = 60, W - 60
    bits_shown = 33  # показуємо перші ~3 канали / 4 байти
    step = (x1 - x0) / bits_shown
    yb = 120  # рядок байтів
    yc = 210  # рядок каналів

    # смуга бітів
    P.append(text(x0 - 4, yb - 34, "потік бітів →", size=11, color=MUTED, anchor="start"))
    for i in range(bits_shown):
        bx = x0 + i * step
        P.append(line(bx, yb - 22, bx, yc + 22, color="#eef0f3", sw=1))

    # межі байтів (кожні 8 бітів) — зверху, сірі рамки
    byte_cols = ["#e9eef5", "#f1f4f8"]
    for b in range(4):
        bx0 = x0 + b * 8 * step
        bx1 = x0 + min((b + 1) * 8, bits_shown) * step
        P.append(rect(bx0, yb - 22, bx1 - bx0, 24, fill=byte_cols[b % 2], stroke=INK, sw=1.2, rx=3))
        P.append(text((bx0 + bx1) / 2, yb - 6, "байт %d" % b, size=10.5, bold=True, color=INK))
    P.append(text(x1 + 4, yb - 6, "…", size=13, color=MUTED, anchor="start"))

    # межі каналів (кожні 11 бітів) — знизу, кольорові
    chan_cols = [NEG, FIELD, POS]
    for c in range(3):
        cx0 = x0 + c * 11 * step
        cx1 = x0 + min((c + 1) * 11, bits_shown) * step
        col = chan_cols[c % 3]
        P.append(rect(cx0, yc, cx1 - cx0, 26, fill="#ffffff", stroke=col, sw=1.8, rx=3))
        P.append(text((cx0 + cx1) / 2, yc + 17, "канал %d · 11 біт" % c, size=10.5, bold=True, color=col))

    # стрілки-виноски, що показують зсув межі каналу проти межі байта
    for c in range(1, 3):
        mx = x0 + c * 11 * step
        P.append(line(mx, yb + 2, mx, yc, color=chan_cols[c % 3], sw=1.4, dash="3,3"))
    P.append(text(W / 2, yc + 62,
                  "межа каналу (кожні 11) НЕ збігається з межею байта (кожні 8): канали «переливаються» через байти",
                  size=11.5, color=INK))

    # низ: порядок little-endian — молодший біт першим
    ye = 330
    P.append(rect(60, ye, W - 120, 60, fill="#f4f6f8", stroke=INK, sw=1.3, rx=6))
    P.append(text(W / 2, ye + 24,
                  "порядок little-endian: молодші біти каналу лягають у молодші біти байта",
                  size=11.5, bold=True))
    P.append(text(W / 2, ye + 44,
                  "16 × 11 = 176 біт = рівно 22 байти, жодного біта на вирівнювання не витрачено",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "packing.svg"), W, H, *P)


# ── 3. Один дріт, два напрями: напівдуплекс на одному UART ────────────────────
# Ідея: CRSF кладе керування (вниз, часто) І телеметрію (вгору, зрідка) на ОДНУ
# лінію по черзі. Економія: один UART замість двох, один дріт замість пучка.
def fig_halfduplex():
    W, H = 920, 380
    P = [text(W / 2, 30, "Один UART, два напрями: канали вниз, телеметрія вгору", size=17, bold=True)]

    rxx, fcx = 150, W - 150
    cy = 150
    P.append(textbox(rxx, cy, "ПРИЙМАЧ\n(RX)", size=13, bold=True, fill="#eef2f7", stroke=INK, min_w=130)[0])
    P.append(textbox(fcx, cy, "КОНТРОЛЕР\n(FC)", size=13, bold=True, fill="#eef2f7", stroke=INK, min_w=130)[0])

    # одна лінія між ними
    lx0, lx1 = rxx + 70, fcx - 70
    P.append(line(lx0, cy, lx1, cy, color=INK, sw=2.4))
    P.append(text((lx0 + lx1) / 2, cy - 12, "ОДИН дріт (один UART, 420 000 бод, 8N1)", size=11, bold=True))

    # канали вниз — часто (зелені імпульси зліва-направо)
    yd = 235
    P.append(text(rxx, yd - 10, "канали керування →  часто", size=11, color=FIELD, bold=True, anchor="start"))
    n = 9
    for i in range(n):
        px = lx0 + 10 + i * ((lx1 - lx0 - 20) / (n - 1))
        P.append(rect(px - 6, yd, 12, 16, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=2))
    P.append(text(lx1, yd + 13, "→", size=14, color=FIELD, anchor="start", bold=True))

    # телеметрія вгору — зрідка (сині імпульси справа-наліво), між керуванням
    yu = 285
    P.append(text(rxx, yu + 4, "← телеметрія  зрідка", size=11, color=NEG, bold=True, anchor="start"))
    for i in range(3):
        px = lx0 + 60 + i * ((lx1 - lx0 - 120) / 2)
        P.append(rect(px - 8, yu, 16, 16, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=2))
    P.append(text(lx0 - 4, yu + 13, "←", size=14, color=NEG, anchor="end", bold=True))

    P.append(rect(60, H - 52, W - 120, 36, fill="#f4f6f8", stroke=INK, sw=1.3, rx=6))
    P.append(text(W / 2, H - 29,
                  "напівдуплекс: у кожну мить лінією йде щось одне; телеметрія вставляється між пакетами керування — окремий дріт не потрібен",
                  size=11, color=INK))
    render(os.path.join(IMG, "halfduplex.svg"), W, H, *P)


# ── 4. LinkStatistics: борт сам звітує про якість свого ж каналу ──────────────
# Ідея: телеметрія вертає не лише «висоту й напругу», а й ЗДОРОВ'Я самого лінка
# (RSSI, LQ, SNR) — і контролер бачить, коли зв'язок «тане», ще до розриву.
def fig_linkstats():
    W, H = 900, 380
    P = [text(W / 2, 30, "LinkStatistics: лінк сам розповідає, наскільки він живий", size=17, bold=True)]

    # ліворуч — приймач, праворуч — контролер, стрілка телеметрії вгору
    P.append(textbox(120, 120, "приймач", size=12, bold=True, fill="#eef2f7", stroke=INK, min_w=110)[0])
    P.append(textbox(W - 120, 120, "контролер\n+ OSD", size=12, bold=True, fill="#eef2f7", stroke=INK, min_w=110)[0])
    P.append(arrow(180, 120, W - 180, 120, color=NEG, sw=2.4))
    P.append(text(W / 2, 104, "кадр 0x14 — 10 байтів здоров'я каналу", size=11.5, bold=True, color=NEG))

    # три ключові метрики як «датчики»
    def gauge(cx, lab, val_txt, frac, col):
        P.append(text(cx, 190, lab, size=12, bold=True))
        gw = 150
        gx = cx - gw / 2
        P.append(rect(gx, 205, gw, 16, fill="#f0f2f5", stroke=INK, sw=1.2, rx=8))
        P.append(rect(gx, 205, gw * frac, 16, fill=col, stroke=col, sw=0, rx=8))
        P.append(text(cx, 246, val_txt, size=11, color=col, bold=True))

    gauge(200, "RSSI", "−92 дБм · сила сигналу", 0.35, POS)
    gauge(W / 2, "LQ", "88 % · частка вцілілих пакетів", 0.88, FIELD)
    gauge(W - 200, "SNR", "+6 дБ · сигнал над шумом", 0.6, NEG)

    P.append(rect(60, 285, W - 120, 66, fill="#f4f6f8", stroke=INK, sw=1.3, rx=6))
    P.append(text(W / 2, 308,
                  "RSSI падає, LQ тане, SNR наближається до нуля → зв'язок «на межі»",
                  size=11.5, bold=True))
    P.append(text(W / 2, 330,
                  "контролер і пілот бачать деградацію ЗАЗДАЛЕГІДЬ і встигають розвернутись, поки лінк ще тримає керування",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "linkstats.svg"), W, H, *P)


# ── 5. Скінченний автомат парсера: чотири стани й ребро ресинку ───────────────
# Ідея (для proj-вставки): байти UART приходять довільними порціями, тож парсер
# живе МІЖ читаннями — це автомат. Чотири стани: шукаємо старт → читаємо
# довжину → добираємо тіло → перевіряємо CRC. Будь-яка невдача (чужий байт,
# погана довжина, битий CRC) не «зависає», а веде назад у пошук старту — ресинк.
def fig_parser_fsm():
    W, H = 940, 470
    P = [text(W / 2, 30, "Парсер CRSF — це автомат, що живе між читаннями UART", size=17, bold=True)]

    # чотири стани в ряд
    cy = 130
    xs = [140, 380, 610, 840]
    labels = [
        ("ПОШУК\nстарту 0xC8", "#eef6ef", FIELD),
        ("ДОВЖИНА\n2…62?", "#eef2f7", NEG),
        ("ТІЛО\nдобираємо байти", "#f4f6f8", INK),
        ("CRC8\nзбіглось?", "#fdecea", POS),
    ]
    boxes = []
    for x, (lab, fill, col) in zip(xs, labels):
        b, w, h = textbox(x, cy, lab, size=12, bold=True, fill=fill, stroke=col, sw=1.8, min_w=150)
        P.append(b)
        boxes.append((x, w, h))

    # прямі ребра «далі»
    for i in range(3):
        x0 = boxes[i][0] + boxes[i][1] / 2
        x1 = boxes[i + 1][0] - boxes[i + 1][1] / 2
        P.append(arrow(x0 + 4, cy, x1 - 4, cy, color=INK, sw=2.0))
    P.append(text((xs[0] + xs[1]) / 2, cy - 30, "є старт", size=10.5, color=FIELD, bold=True))
    P.append(text((xs[1] + xs[2]) / 2, cy - 30, "у діапазоні", size=10.5, color=NEG, bold=True))
    P.append(text((xs[2] + xs[3]) / 2, cy - 30, "кадр повний", size=10.5, color=INK, bold=True))

    # успіх з CRC → диспетчер
    dy = 300
    dbx, dbw, dbh = textbox(xs[3], dy, "ДИСПЕТЧЕР\nза типом", size=12, bold=True,
                            fill="#eef6ef", stroke=FIELD, sw=1.8, min_w=150)
    P.append(dbx)
    P.append(arrow(xs[3], cy + boxes[3][2] / 2, xs[3], dy - dbh / 2 - 2, color=FIELD, sw=2.0))
    P.append(text(xs[3] + 12, (cy + dy) / 2, "CRC ✓", size=10.5, color=FIELD, bold=True, anchor="start"))

    # ребро ресинку: будь-яка невдача → назад у ПОШУК (довга дуга знизу)
    ry = 400
    P.append(line(xs[3], dy + dbh / 2, xs[3], ry, color=POS, sw=1.8, dash="5,4"))
    P.append(line(xs[1], cy + boxes[1][2] / 2, xs[1], ry, color=POS, sw=1.8, dash="5,4"))
    P.append(line(xs[3], ry, xs[0], ry, color=POS, sw=1.8, dash="5,4"))
    P.append(line(xs[1], ry, xs[0], ry, color=POS, sw=1.8, dash="5,4"))
    P.append(arrow(xs[0], ry, xs[0], cy + boxes[0][2] / 2 + 2, color=POS, sw=1.8))
    P.append(text((xs[0] + xs[3]) / 2, ry + 20,
                  "будь-яка невдача — чужий байт, довжина поза 2…62, битий CRC — веде НАЗАД у пошук старту (ресинк)",
                  size=11, color=POS, bold=True))
    P.append(text(xs[1] + 10, (cy + ry) / 2 + 20, "погана\nдовжина", size=9.5, color=POS, anchor="start"))
    render(os.path.join(IMG, "parser-fsm.svg"), W, H, *P)


# ════════════════════════════════════════════════════════════════════════════
# ВСТАВКА 📜: історія CRSF — від фірмового формату TBS до спільної мови ELRS
# ════════════════════════════════════════════════════════════════════════════

# ── Дві епохи однієї мови: винахід TBS (2015) → стандарт через ELRS (~2020) ──
# Ідея: CRSF не «спроєктували як стандарт» — він НАРОДИВСЯ фірмовим форматом
# усередині одного продукту, а стандартом його зробив ЧУЖИЙ проєкт, що
# вирішив не винаходити свого, а взяти готове й перевірене.
def fig_two_eras():
    W, H = 940, 430
    P = [text(W / 2, 30, "Як CRSF став спільною мовою: винахід vs прийняття", size=17, bold=True)]

    # горизонтальна вісь часу
    axy = 118
    P.append(line(70, axy, W - 40, axy, color=MUTED, sw=2))
    for xx, yr in ((150, "2015"), (355, "2016"), (600, "~2020"), (820, "2021")):
        P.append(line(xx, axy - 6, xx, axy + 6, color=MUTED, sw=1.6))
        P.append(text(xx, axy - 14, yr, size=12, bold=True, color=MUTED))

    # ── ЕПОХА 1: фірмовий винахід TBS ──
    e1 = rect(95, 150, 330, 128, fill="#fdecea", stroke=POS, sw=1.8, rx=10)
    P.append(e1)
    P.append(text(260, 174, "Фірмовий винахід", size=13.5, bold=True, color=POS))
    P.append(text(260, 196, "TBS Crossfire, Team BlackSheep", size=11, color=INK))
    P.append(fitbox(112, 210, 296, 56,
                    "далекобійний лінк FPV; свій формат «приймач↔контролер»\n"
                    "поверх звичайного UART — рішення ПІД СВІЙ продукт",
                    size=10, fill="#fff5f4", stroke=POS, sw=1.2))

    # ── ЕПОХА 2: галузева стандартизація через ELRS ──
    e2 = rect(545, 150, 350, 128, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10)
    P.append(e2)
    P.append(text(720, 174, "Стандарт через прийняття", size=13.5, bold=True, color=FIELD))
    P.append(text(720, 196, "ExpressLRS (відкритий проєкт)", size=11, color=INK))
    P.append(fitbox(562, 210, 316, 56,
                    "не став вигадувати свій формат — узяв готовий CRSF\n"
                    "і зосередився на власне радіо. Так формат став спільним",
                    size=10, fill="#f4faf5", stroke=FIELD, sw=1.2))

    # стрілка «прийняття»: з епохи 1 у епоху 2
    P.append(arrow(425, 214, 545, 214, color=INK, sw=2.4))
    P.append(text(485, 202, "узяв", size=11, bold=True))
    P.append(text(485, 232, "готове", size=11, bold=True))

    # підсумковий рядок унизу
    P.append(text(W / 2, 330,
                  "Ключова різниця: TBS ВИНАЙШОВ формат для себе; ELRS зробив його ДЕ-ФАКТО стандартом,",
                  size=12, bold=True))
    P.append(text(W / 2, 352,
                  "прийнявши як є. Стандарт тут не спроєктований комітетом, а виріс із прийняття чужого рішення.",
                  size=12, bold=True))
    P.append(text(W / 2, 392,
                  "Дати веб-звірено: Crossfire — 2015; широке піднесення ELRS на 2.4 ГГц і прийняття CRSF — близько 2020.",
                  size=10.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "two-eras.svg"), W, H, *P)


# ── Чому одну мову вибрали обидва табори: спільний «роз'єм» на платі ─────────
# Ідея: контролер (Betaflight/ArduPilot) уже вміє CRSF. Тож будь-який приймач,
# що говорить CRSF, вставляється в ту саму «розетку» без переробок прошивки FC.
# Це і є механізм, яким прийняття однією стороною закріпило формат для всіх.
def fig_common_socket():
    W, H = 900, 360
    P = [text(W / 2, 30, "Чому прижилося: один «роз'єм» CRSF на боці контролера", size=17, bold=True)]

    # центр — польотний контролер, який РОЗУМІЄ CRSF
    fcx, fcy = W / 2, 200
    P.append(rect(fcx - 95, fcy - 46, 190, 92, fill="#eef2fb", stroke=NEG, sw=2, rx=10))
    P.append(text(fcx, fcy - 20, "Польотний контролер", size=12.5, bold=True))
    P.append(text(fcx, fcy + 2, "Betaflight / ArduPilot", size=11, color=INK))
    P.append(text(fcx, fcy + 26, "порт «розуміє CRSF»", size=11, bold=True, color=NEG))

    # два різні приймачі — обидва говорять CRSF — заходять в один порт
    def rx(cx, cy, title, sub, col):
        P.append(rect(cx - 92, cy - 34, 184, 68, fill="#f7f7f9", stroke=col, sw=1.8, rx=9))
        P.append(text(cx, cy - 10, title, size=12, bold=True, color=col))
        P.append(text(cx, cy + 12, sub, size=10, color=INK))

    rx(150, 200, "TBS Crossfire Rx", "рідний CRSF", POS)
    rx(750, 200, "ExpressLRS Rx", "той самий CRSF", FIELD)

    P.append(arrow(242, 200, fcx - 96, fcy - 8, color=POS, sw=2.2))
    P.append(arrow(658, 200, fcx + 96, fcy - 8, color=FIELD, sw=2.2))
    P.append(text(320, 176, "CRSF", size=11, bold=True, color=POS))
    P.append(text(578, 176, "CRSF", size=11, bold=True, color=FIELD))

    P.append(text(W / 2, 300,
                  "Контролер не переробляють під кожен лінк: він знає ОДНУ мову — CRSF.",
                  size=12, bold=True))
    P.append(text(W / 2, 322,
                  "Тож приймачу вигідно говорити нею — і кожен новий, що так робить, лише зміцнює спільний стандарт.",
                  size=11))
    render(os.path.join(IMG, "common-socket.svg"), W, H, *P)


if __name__ == "__main__":
    fig_frame()
    fig_packing()
    fig_halfduplex()
    fig_linkstats()
    fig_parser_fsm()
    fig_two_eras()
    fig_common_socket()
    print("OK: 7 фігур у", IMG)
