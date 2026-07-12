# -*- coding: utf-8 -*-
"""Фігури до кроку «Довга операція в DH: кліп, що переживає свій запит»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

RED_FILL = "#fdecea"
GREEN_FILL = "#eafaf0"
BLUE_FILL = "#e6eefb"
AMBER_FILL = "#fff4e0"
AMBER = "#c77800"
GRAY_FILL = "#f0f0f2"


def fig_sync_vs_async():
    """Синхронний шлях: з'єднання коротше за роботу. Асинхронний: відповідь одразу, робота у фоні."""
    W, H = 1200, 660
    frags = []

    X0, X45 = 360, 980           # часова вісь: 0 с → X0, 45 с → X45
    PPS = (X45 - X0) / 45.0       # пікселів на секунду

    def tx(s):
        return X0 + s * PPS

    LBLX = 110                    # ліва колонка підписів доріжок

    # ─────────── ВЕРХНЯ СМУГА: синхронно ───────────
    frags.append(text(W / 2, 66, "СИНХРОННО — з'єднання коротше за роботу",
                      size=16, bold=True, color=POS))

    # доріжка З'ЄДНАННЯ: живе тільки 0..30 с
    frags.append(text(LBLX, 128, "З'ЄДНАННЯ", size=12.5, bold=True, color=INK, anchor="start"))
    frags.append(rect(tx(0), 112, tx(30) - tx(0), 26, fill=AMBER_FILL, stroke=POS, sw=1.8))
    frags.append(text(tx(15), 129, "телефон чекає на дроті", size=11.5, color=AMBER))
    frags.append(text(tx(30) + 12, 118, "✗", size=20, bold=True, color=POS, anchor="start"))
    frags.append(text(tx(30) + 30, 122, "30 с · 504 — дріт убито", size=12, bold=True,
                      color=POS, anchor="start"))

    # доріжка РЕНДЕР: біжить усі 0..45 с
    frags.append(text(LBLX, 190, "РЕНДЕР", size=12.5, bold=True, color=INK, anchor="start"))
    frags.append(rect(tx(0), 174, tx(45) - tx(0), 26, fill=RED_FILL, stroke=POS, sw=1.8))
    frags.append(text(tx(22.5), 191, "перекодування · 45 с", size=11.5, color=POS))
    frags.append(text(tx(45) + 12, 191, "45 с · готово —", size=12, bold=True,
                      color=POS, anchor="start"))
    frags.append(text(tx(45) + 12, 207, "віддати нема кому", size=12, color=MUTED, anchor="start"))

    # вертикаль розриву: там, де дріт мертвий, робота ще йде
    frags.append(line(tx(30), 104, tx(30), 246, color=POS, sw=1.4, dash="4,5"))

    # повтор → другий рендер
    frags.append(rect(tx(0), 226, tx(45) - tx(0), 18, fill="#fadedb", stroke=MUTED, sw=1.3, rx=4))
    frags.append(text(tx(22.5), 239, "повтор телефона → ДРУГИЙ рендер тих самих 45 с",
                      size=11.5, bold=True, color=POS))

    # ─────────── роздільник ───────────
    frags.append(line(70, 288, W - 70, 288, color=MUTED, sw=1.2, dash="7,7"))

    # ─────────── НИЖНЯ СМУГА: асинхронно ───────────
    frags.append(text(W / 2, 328, "АСИНХРОННО — відповідь одразу, робота живе у фоні",
                      size=16, bold=True, color=FIELD))

    # доріжка З'ЄДНАННЯ: крихітне, віддало квитанцію й вільне
    frags.append(text(LBLX, 390, "З'ЄДНАННЯ", size=12.5, bold=True, color=INK, anchor="start"))
    frags.append(rect(tx(0), 374, max(tx(1.6) - tx(0), 10), 26, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    frags.append(text(tx(0) + 40, 391, "202 + /operations/abc123 · ≈20 мс — дріт одразу вільний",
                      size=11.5, bold=True, color=FIELD, anchor="start"))

    # доріжка РЕНДЕР (фон): ті самі 45 с, але вже НЕ на дроті
    frags.append(text(LBLX, 452, "РЕНДЕР · фон", size=12.5, bold=True, color=INK, anchor="start"))
    frags.append(rect(tx(0), 436, tx(45) - tx(0), 26, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    frags.append(text(tx(22.5), 453, "перекодування у фоні · 45 с", size=11.5, color=FIELD))
    frags.append(text(tx(45) + 12, 453, "45 с · кліп готовий", size=12, bold=True,
                      color=FIELD, anchor="start"))

    # доріжка ТЕЛЕФОН: полить поступ / дістає пуш
    frags.append(text(LBLX, 514, "ТЕЛЕФОН", size=12.5, bold=True, color=INK, anchor="start"))
    frags.append(text(tx(16), 514, "полить поступ: 45%… 70%…", size=11.5, color=MUTED))
    b, _, _ = textbox(tx(43), 514, "пуш / посилання", size=11.5, bold=True,
                      fill=GREEN_FILL, stroke=FIELD, sw=1.5, color=FIELD, min_w=150)
    frags.append(b)

    # часова вісь під нижньою смугою
    frags.append(line(X0, 560, X45, 560, color=INK, sw=1.4))
    for s in (0, 15, 30, 45):
        frags.append(line(tx(s), 556, tx(s), 564, color=INK, sw=1.2))
        frags.append(text(tx(s), 582, "%d с" % s, size=11.5, color=MUTED))

    frags.append(text(W / 2, 624,
                      "Та сама робота — 45 с. Угорі вона прив'язана до з'єднання, що вмирає на 30-й, і кожен розрив множить її. "
                      "Унизу її відв'язано від дроту — і тривалість роботи вже нікого не тримає.",
                      size=12.5, color=MUTED))

    render(os.path.join(IMG, "sync-vs-async.svg"), W, H, *frags,
           title="Сорок п'ять секунд роботи в тридцятисекундному з'єднанні")


def _statebox(cx, cy, head, sub, fill, stroke, color, min_w=230):
    return textbox(cx, cy, head + "\n" + sub, size=12.5, bold=True,
                   fill=fill, stroke=stroke, sw=2.2, color=color, min_w=min_w)


def fig_operation_lifecycle():
    """Життєвий цикл операції як скінченний автомат: черга → робота → один із трьох кінцевих станів."""
    W, H = 1200, 560
    frags = []

    XQ, XR, XT = 210, 590, 990          # queued / running / термінали
    YR = 300                             # рівень running і queued
    YS, YF, YC = 130, 300, 470           # succeeded / failed / canceled

    qb, qw, qh = _statebox(XQ, YR, "QUEUED", "у черзі задач", GRAY_FILL, MUTED, INK)
    rb, rw, rh = _statebox(XR, YR, "RUNNING", "рендерить · progress 0–100", BLUE_FILL, NEG, INK, min_w=260)
    sb, sw_, sh = _statebox(XT, YS, "SUCCEEDED", "кліп готовий · посилання", GREEN_FILL, FIELD, FIELD)
    fb, fw, fh = _statebox(XT, YF, "FAILED", "таймаут · смерть · N спроб", RED_FILL, POS, POS)
    cb, cw, ch = _statebox(XT, YC, "CANCELED", "користувач скасував", AMBER_FILL, AMBER, AMBER)

    # queued → running (робітник забрав)
    frags.append(arrow(XQ + qw / 2 + 6, YR, XR - rw / 2 - 6, YR, color=INK, sw=2))
    frags.append(text((XQ + XR) / 2, YR - 14, "робітник забрав задачу", size=12, bold=True, color=INK))

    # running → running (dashed back to queued): оренда згасла → назад у чергу
    frags.append(line(XR - rw / 2, YR + rh / 2 - 6, XR - rw / 2, YR + 96, color=MUTED, sw=1.6, dash="4,5"))
    frags.append(line(XR - rw / 2, YR + 96, XQ, YR + 96, color=MUTED, sw=1.6, dash="4,5"))
    frags.append(arrow(XQ, YR + 96, XQ, YR + qh / 2 + 6, color=MUTED, sw=1.6))
    frags.append(text((XQ + XR) / 2 - 20, YR + 112, "оренда згасла (серцебиття стихло) → назад у чергу",
                      size=11.5, bold=True, color=MUTED))

    # running → succeeded
    frags.append(arrow(XR + rw / 2 + 6, YR - rh / 2 + 6, XT - sw_ / 2 - 6, YS + sh / 2 - 4,
                       color=FIELD, sw=2))
    frags.append(text((XR + XT) / 2 + 10, YS + sh / 2 + 26, "рендер добіг", size=12, bold=True, color=FIELD))

    # running → failed
    frags.append(arrow(XR + rw / 2 + 6, YR, XT - fw / 2 - 6, YF, color=POS, sw=2))
    frags.append(text((XR + XT) / 2 + 6, YF - 12, "таймаут · смерть · вичерпані спроби",
                      size=11.5, bold=True, color=POS))

    # running → canceled
    frags.append(arrow(XR + rw / 2 + 6, YR + rh / 2 - 6, XT - cw / 2 - 6, YC - ch / 2 + 4,
                       color=AMBER, sw=2))
    frags.append(text((XR + XT) / 2 + 10, YC - ch / 2 - 12, "скасовано під час роботи",
                      size=11.5, bold=True, color=AMBER))

    # queued → canceled (скасовано до старту) — дуга низом
    frags.append(line(XQ, YR + qh / 2 + 6, XQ, 520, color=AMBER, sw=1.7))
    frags.append(line(XQ, 520, XT, 520, color=AMBER, sw=1.7))
    frags.append(arrow(XT, 520, XT, YC + ch / 2 + 6, color=AMBER, sw=1.7))
    frags.append(text((XQ + XT) / 2, 512, "скасовано ще до старту", size=11.5, bold=True, color=AMBER))

    frags += [qb, rb, sb, fb, cb]

    # позначка «кінцеві»
    frags.append(text(XT, 60, "кінцеві стани", size=12.5, bold=True, color=MUTED))
    frags.append(line(XT - 120, 68, XT + 120, 68, color=MUTED, sw=1, dash="3,4"))

    render(os.path.join(IMG, "operation-lifecycle.svg"), W, H, *frags,
           title="Життєвий цикл операції: жодної стрілки «зависнути назавжди»")


def fig_op_resource_timeline():
    """Родовід «операції-ресурсу»: 202 у 1996-му → дірка в стандарті на 26 років → однаковість у хмарі."""
    W, H = 1220, 560
    frags = []

    frags.append(text(W / 2, 52, "Зерно кинуто 1996-го — сходи зібрали за чверть століття",
                      size=13.5, color=MUTED))

    # ── лейбл лівої смуги ──
    frags.append(text(60, 96, "У СТАНДАРТІ", size=12, bold=True, color=INK, anchor="start"))
    frags.append(text(60, 112, "HTTP", size=12, bold=True, color=INK, anchor="start"))

    # ── вісь із роками (нелінійна, підписана) ──
    AY = 150
    X1996, X1999, X2014, X2022 = 250, 470, 660, 850
    frags.append(line(200, AY, 940, AY, color=INK, sw=1.4))
    for x, yr, hot in ((X1996, "1996", True), (X1999, "1999", False),
                       (X2014, "2014", False), (X2022, "2022", False)):
        frags.append(line(x, AY - 5, x, AY + 5, color=INK, sw=1.2))
        frags.append(text(x, AY + 22, yr, size=12, bold=hot, color=(FIELD if hot else MUTED)))

    # ── коробки RFC над віссю ──
    b, _, _ = textbox(X1996, 112, "RFC 1945\n202 Accepted", size=11.5, bold=True,
                      fill=GREEN_FILL, stroke=FIELD, sw=2, color=FIELD, min_w=118)
    frags.append(b)
    for x, s in ((X1999, "RFC 2616\nHTTP/1.1"), (X2014, "RFC 7231"), (X2022, "RFC 9110")):
        bb, _, _ = textbox(x, 112, s, size=11.5, fill=GRAY_FILL, stroke=MUTED, sw=1.4,
                           color=INK, min_w=96)
        frags.append(bb)

    # ── зерно 1996-го: власне текст коду 202 ──
    seed = ("«прийнято, роботу не завершено; з'єднання може не жити до кінця —\n"
            "а у відповідь клади ВКАЗІВНИК НА МОНІТОР СТАТУСУ»")
    sb, sw_, sh = textbox(455, 232, seed, size=12, bold=False, fill=GREEN_FILL,
                          stroke=FIELD, sw=1.8, color=FIELD, min_w=540)
    frags.append(line(X1996, AY + 30, 455, 232 - sh / 2, color=FIELD, sw=1.3, dash="3,4"))
    frags.append(sb)

    # ── дужка «дірка на 26 років» ──
    BY = 322
    frags.append(line(X1996, BY, X2022, BY, color=MUTED, sw=1.5, dash="5,5"))
    frags.append(line(X1996, BY, X1996, BY - 8, color=MUTED, sw=1.5))
    frags.append(line(X2022, BY, X2022, BY - 8, color=MUTED, sw=1.5))
    frags.append(text((X1996 + X2022) / 2, BY + 20,
                      "а ЯКИМ є той монітор — які поля, які дієслова — стандарт так і не сказав",
                      size=12, bold=True, color=MUTED))
    frags.append(text((X1996 + X2022) / 2, BY + 38,
                      "26 років кожен довгий виклик ліпив монітор по-своєму",
                      size=11.5, color=MUTED))

    # ── стрілка вниз до сходин ──
    frags.append(arrow(W / 2, BY + 52, W / 2, 424, color=INK, sw=2))

    # ── підсумковий вузол: одна форма ──
    node = ("операція — РЕСУРС, який опитуєш:\n"
            "прийми → ручка-адреса → GET-поллінг → кінцевий стан → результат за посиланням, зі старінням")
    nb, _, _ = textbox(W / 2, 462, node, size=12.5, bold=True, fill=BLUE_FILL,
                       stroke=NEG, sw=2, color=INK, min_w=880)
    frags.append(nb)
    frags.append(text(W / 2, 512, "≈2015–2019 · Google longrunning · Azure async · AWS job+poll — три словники, одна форма",
                      size=11.5, color=MUTED))

    render(os.path.join(IMG, "op-resource-timeline.svg"), W, H, *frags,
           title="Квитанція, якій уже тридцять років")


def _cell(x, y, w, h, s, fill, stroke, color=INK, bold=False, size=12):
    return fitbox(x, y, w, h, s, size=size, pad=8, fill=fill, stroke=stroke,
                  sw=1.4, color=color, bold=bold)


def fig_three_clouds_one_shape():
    """Три хмарні словники, зведені до однієї форми — і різна міра нав'язаної однаковості."""
    W, H = 1340, 660
    frags = []

    frags.append(text(W / 2, 52, "Один болт, три ключі: конвергентна еволюція довгих операцій",
                      size=13.5, color=MUTED))

    RX, RW = 30, 220
    C1, C2, C3, CW = 262, 620, 978, 348
    HY, HH = 84, 52

    # ── шапка колонок ──
    frags.append(_cell(RX, HY, RW, HH, "роль у формі", GRAY_FILL, MUTED, MUTED, True, 12))
    frags.append(_cell(C1, HY, CW, HH, "Google\nlongrunning.Operation · AIP-151",
                       GREEN_FILL, FIELD, FIELD, True, 12.5))
    frags.append(_cell(C2, HY, CW, HH, "Azure\nasync operations",
                       BLUE_FILL, NEG, NEG, True, 12.5))
    frags.append(_cell(C3, HY, CW, HH, "AWS\nStartX → JobId → GetX (на службу)",
                       AMBER_FILL, AMBER, AMBER, True, 12.5))

    rows = [
        ("Сигнал «прийнято»",
         "Operation\n(done: false)",
         "202 Accepted\n+ Retry-After",
         "StartX → JobId"),
        ("Ручка операції",
         "name:\n…/operations/{id}",
         "Azure-AsyncOperation\n(або Location) URL",
         "JobId"),
        ("Як опитуєш",
         "GetOperation",
         "GET на status-URL\n202 поки йде → 200",
         "GetX / DescribeX"),
        ("Кінець і результат",
         "done: true +\nresponse | error",
         "provisioningState:\nSucceeded/Failed/Canceled",
         "Status: SUCCEEDED /\nFAILED + сторінки"),
        ("Старіння",
         "≈ 30 днів",
         "за політикою ресурсу",
         "JobId живе 7 днів"),
    ]
    RY0, RH = HY + HH + 6, 74
    for i, (role, g, a, w) in enumerate(rows):
        y = RY0 + i * RH
        frags.append(_cell(RX, y, RW, RH - 6, role, GRAY_FILL, MUTED, INK, True, 12))
        frags.append(_cell(C1, y, CW, RH - 6, g, "#f3fbf6", FIELD, INK, False, 12))
        frags.append(_cell(C2, y, CW, RH - 6, a, "#f2f6fd", NEG, INK, False, 12))
        frags.append(_cell(C3, y, CW, RH - 6, w, "#fdf8ef", AMBER, INK, False, 12))

    # ── рядок-присуд: скільки однаковості нав'язано ──
    py = RY0 + len(rows) * RH + 6
    PH = 78
    frags.append(_cell(RX, py, RW, PH, "Скільки однаковості\nНАВ'ЯЗАНО", "#efe7f7", "#7c4dbc", "#5b2e94", True, 12))
    frags.append(_cell(C1, py, CW, PH, "ЖОРСТКО: один proto на всіх,\n«не винаходь свій інтерфейс»",
                       GREEN_FILL, FIELD, FIELD, True, 12.5))
    frags.append(_cell(C2, py, CW, PH, "єдине HTTP-рукостискання,\nстатус — на тип ресурсу",
                       BLUE_FILL, NEG, NEG, True, 12.5))
    frags.append(_cell(C3, py, CW, PH, "звичай-конвенція,\nбез єдиного інтерфейсу",
                       AMBER_FILL, AMBER, AMBER, True, 12.5))

    render(os.path.join(IMG, "three-clouds-one-shape.svg"), W, H, *frags,
           title="Три словники — одна форма")


def fig_idempotency_race():
    """Дві однакові POST-и з тим самим ключем: UNIQUE-індекс серіалізує їх — одна операція."""
    W, H = 1280, 520
    frags = []
    X1, X2, X3, X4 = 250, 575, 865, 1140
    YA, YB = 155, 375
    G = 10  # проміжок стрілки від краю коробки

    frags.append(text(W / 2, 56, "Дві однакові POST-и з ключем K — і рівно одна операція op-42",
                      size=17, bold=True, color=INK))

    def box(x, y, s, fill, stroke, color, mw, bold=False):
        b, w, _ = textbox(x, y, s, size=11.5, fill=fill, stroke=stroke, color=color,
                          min_w=mw, bold=bold)
        frags.append(b)
        return w

    def connect(x1, w1, x2, w2, y, color):
        frags.append(arrow(x1 + w1 / 2 + G, y, x2 - w2 / 2 - G, y, color=color, sw=1.8))

    # ── A: виграв ──
    frags.append(text(70, YA, "ЗАПИТ A", size=12.5, bold=True, color=INK, anchor="start"))
    wa1 = box(X1, YA, "POST /clips\nIdempotency-Key: K", GRAY_FILL, MUTED, INK, 155)
    wa2 = box(X2, YA, "INSERT … ON CONFLICT\nDO NOTHING RETURNING id", BLUE_FILL, NEG, INK, 230)
    wa3 = box(X3, YA, "1 рядок → op-42\nВИГРАВ · у чергу", GREEN_FILL, FIELD, FIELD, 175, True)
    wa4 = box(X4, YA, "202 · Location:\n…/operations/op-42", GREEN_FILL, FIELD, FIELD, 175, True)
    connect(X1, wa1, X2, wa2, YA, INK)
    connect(X2, wa2, X3, wa3, YA, FIELD)
    connect(X3, wa3, X4, wa4, YA, FIELD)

    # ── B: програв, читає ту саму ──
    frags.append(text(70, YB, "ЗАПИТ B", size=12.5, bold=True, color=INK, anchor="start"))
    wb1 = box(X1, YB, "POST /clips\nIdempotency-Key: K", GRAY_FILL, MUTED, INK, 155)
    wb2 = box(X2, YB, "INSERT … ON CONFLICT\n(блокується на індексі)", AMBER_FILL, AMBER, AMBER, 230)
    wb3 = box(X3, YB, "0 рядків → SELECT by key\nдістає op-42", BLUE_FILL, NEG, INK, 175)
    wb4 = box(X4, YB, "202 · Location:\n…/operations/op-42\n(ТА САМА)", GREEN_FILL, FIELD, FIELD, 175, True)
    connect(X1, wb1, X2, wb2, YB, INK)
    connect(X2, wb2, X3, wb3, YB, MUTED)
    connect(X3, wb3, X4, wb4, YB, FIELD)

    # серіалізація між лейнами
    xc = (X2 + X3) / 2
    frags.append(line(xc, YA + 48, xc, YB - 48, color=AMBER, sw=1.5, dash="5,5"))
    frags.append(text(xc, (YA + YB) / 2 - 6, "A комітить →", size=11, bold=True, color=AMBER))
    frags.append(text(xc, (YA + YB) / 2 + 12, "індекс відпускає B", size=11, color=AMBER))

    frags.append(text(W / 2, 478,
                      "UNIQUE(idempotency_key) пропускає першого й тримає другого, поки перший не закомітить; "
                      "тоді другий дістає 0 рядків і читає ту саму op-42. Один намір — одна операція — один рендер.",
                      size=12.5, color=MUTED))
    render(os.path.join(IMG, "idempotency-race.svg"), W, H, *frags, title=None)


def fig_lease_heartbeat():
    """Оренда, серцебиття, фенс: A замерзає — op-42 переходить до B, спізнілий A відсічений."""
    W, H = 1320, 580
    frags = []
    X0, XE = 140, 1200

    def tx(t):
        return X0 + (XE - X0) * t / 100.0

    YA, YL, YB, YAX = 155, 305, 435, 515

    frags.append(text(W / 2, 52,
                      "Оренда, серцебиття і фенс: A замерзає — op-42 переходить до B, спізнілий A відсічений",
                      size=16, bold=True, color=INK))

    # вісь часу
    frags.append(line(X0, YAX, XE, YAX, color=INK, sw=1.4))
    for t in range(0, 101, 10):
        frags.append(line(tx(t), YAX - 4, tx(t), YAX + 4, color=INK, sw=1))
        frags.append(text(tx(t), YAX + 20, "%d с" % t, size=10.5, color=MUTED))

    # лейн A
    frags.append(text(70, YA, "РОБІТНИК A", size=12.5, bold=True, color=INK, anchor="start"))
    frags.append(rect(tx(0), YA - 14, tx(32) - tx(0), 28, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    frags.append(text(tx(1.5), YA + 4, "claim(L1) · рендерить", size=11, color=FIELD, anchor="start"))
    for t in (10, 20, 30):
        frags.append(text(tx(t), YA - 20, "♥", size=13, bold=True, color=POS))
    frags.append(rect(tx(32), YA - 14, tx(70) - tx(32), 28, fill=AMBER_FILL, stroke=AMBER, sw=1.6))
    frags.append(text(tx(51), YA + 4, "заморозка (GC/stall) — серцебиття стихло", size=10.5, color=AMBER))
    frags.append(text(tx(70) + 10, YA - 5, "✗ hb/finish(L1) → 0 рядків", size=11, bold=True,
                      color=POS, anchor="start"))
    frags.append(text(tx(70) + 10, YA + 12, "ФЕНС · A спиняється", size=11, color=POS, anchor="start"))

    # оренда (середина)
    frags.append(text(70, YL, "ОРЕНДА op-42", size=12.5, bold=True, color=INK, anchor="start"))
    frags.append(rect(tx(0), YL - 12, tx(60) - tx(0), 24, fill=GRAY_FILL, stroke=MUTED, sw=1.5))
    for t in (30, 40, 50, 60):
        frags.append(line(tx(t), YL - 12, tx(t), YL + 12, color=FIELD, sw=1.2, dash="3,3"))
    frags.append(text(tx(28), YL - 22, "серцебиття що 10 с подовжує оренду (+30 с)", size=10.5,
                      color=FIELD, anchor="start"))
    frags.append(text(tx(60) + 10, YL + 4, "✗ оренда згасла на 60 с", size=11, bold=True,
                      color=POS, anchor="start"))

    # лейн B
    frags.append(text(70, YB, "РОБІТНИК B", size=12.5, bold=True, color=INK, anchor="start"))
    frags.append(rect(tx(62), YB - 14, tx(96) - tx(62), 28, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    frags.append(text(tx(63), YB + 4, "reclaim(L2): running & lease<now · рендерить", size=10.5,
                      color=FIELD, anchor="start"))
    for t in (72, 82, 92):
        frags.append(text(tx(t), YB - 20, "♥", size=13, bold=True, color=POS))

    frags.append(text(W / 2, YAX + 46,
                      "Серцебиття що 10 с подовжує 30-секундну оренду. Коли A замерзає, оренда не оновлюється й гасне на 60 с; "
                      "B забирає op-42 з новим жетоном L2. A прокидається — його запис із L1 відсіює фенс (0 рядків).",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "lease-heartbeat.svg"), W, H, *frags, title=None)


def fig_result_lifetimes():
    """Три вкладені строки: підписане посилання · файл у сховищі · запис операції."""
    W, H = 1200, 440
    frags = []
    frags.append(text(W / 2, 54, "Тлінний результат: три строки, і кожен заданий явно",
                      size=17, bold=True, color=INK))
    X0 = 400
    rows = [
        ("Підписане посилання", 470, GREEN_FILL, FIELD, "15 хв", "✗ підпис протух → 403"),
        ("Файл у сховищі", 580, BLUE_FILL, NEG, "7 днів · політика сховища", "✗ прибрано автоматично"),
        ("Запис операції у БД", 930, GRAY_FILL, MUTED, "≈30 днів", "✗ застарів → прибрано"),
    ]
    ys = [145, 240, 335]
    for (label, xend, fill, stroke, dur, gone), y in zip(rows, ys):
        frags.append(text(120, y + 4, label, size=12.5, bold=True, color=INK, anchor="start"))
        frags.append(rect(X0, y - 14, xend - X0, 28, fill=fill, stroke=stroke, sw=1.7))
        frags.append(text((X0 + xend) / 2, y + 4, dur, size=11.5, bold=True, color=stroke))
        frags.append(text(xend + 12, y + 4, gone, size=11, color=POS, anchor="start"))
    frags.append(line(X0, 115, X0, 360, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(X0, 104, "t = 0: кліп готовий", size=11.5, bold=True, color=MUTED))
    frags.append(text(W / 2, 408,
                      "Поки живий ФАЙЛ, за операцією можна щоразу взяти свіже 15-хвилинне посилання; коли політика сховища "
                      "прибирає файл, зникає й сенс запису. Нічого не задано «назавжди» — тому ніщо не тече в нескінченність.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "result-lifetimes.svg"), W, H, *frags, title=None)


if __name__ == "__main__":
    fig_sync_vs_async()
    fig_operation_lifecycle()
    fig_op_resource_timeline()
    fig_three_clouds_one_shape()
    fig_idempotency_race()
    fig_lease_heartbeat()
    fig_result_lifetimes()
    print("OK: sync-vs-async, operation-lifecycle, op-resource-timeline, three-clouds-one-shape, "
          "idempotency-race, lease-heartbeat, result-lifetimes")
