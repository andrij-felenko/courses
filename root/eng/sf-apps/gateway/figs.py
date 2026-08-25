# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_scatter_vs_gateway():
    """Ліворуч: чужий API протікає в код скрізь. Праворуч: один шлюз затуляє його."""
    W, H = 940, 500
    frags = []
    frags.append(text(W / 2, 30,
                      "Чужий API розлитий по коду — або зібраний за одним шлюзом",
                      size=16, bold=True))

    # ── ЛІВОРУЧ: без шлюзу ──
    lx = 120
    callers = ["звіт", "картка\nклієнта", "розсилка"]
    for i, c in enumerate(callers):
        yy = 110 + i * 92
        b, _, _ = textbox(lx, yy, c, size=12, min_w=110, fill="#f4f6f8", stroke=LINE)
        frags.append(b)
        # кожен сам смикає чужий API з його дивною мовою
        frags.append(arrow(lx + 60, yy, 300, 202, color=POS, sw=1.8))
    api_l, _, _ = textbox(370, 202, "чужий HTTP-API\nseg=SEG_A & q=… & v=3\nкоди 200/406/419",
                          size=11, min_w=180, fill="#fdecea", stroke=POS)
    frags.append(api_l)
    frags.append(mtext(235, 424,
                       "дивна мова API вросла в три місця;\nзмінився — правиш усі три",
                       size=12, color=POS, bold=True))

    # роздільник
    frags.append(line(W / 2, 60, W / 2, 460, color=LINE, sw=1, dash="2 4"))

    # ── ПРАВОРУЧ: зі шлюзом ──
    rx = 560
    for i, c in enumerate(callers):
        yy = 110 + i * 92
        b, _, _ = textbox(rx, yy, c, size=12, min_w=110, fill="#f4f6f8", stroke=LINE)
        frags.append(b)
        frags.append(arrow(rx + 60, yy, 745, 202, color=MUTED, sw=1.6))
    gw, _, _ = textbox(800, 202, "Шлюз\ntariffFor(segment)",
                       size=13, bold=True, min_w=150, fill="#fff7e6", stroke="#d68910")
    frags.append(gw)
    frags.append(arrow(800, 236, 800, 306, color=INK, sw=2))
    api_r, _, _ = textbox(800, 340, "чужий HTTP-API\n(та сама дивина —\nале лише тут)",
                          size=11, min_w=170, fill="#fdecea", stroke=POS)
    frags.append(api_r)
    frags.append(mtext(720, 424,
                       "мова API замкнена в одному класі;\nкод кличе звичайний метод",
                       size=12, color="#b9770e", bold=True))

    render(os.path.join(IMG, "scatter-vs-gateway.svg"), W, H, *frags)


def fig_two_sides():
    """Шлюз — дволикий: зовні звичайний метод домену, всередині — чужа мова."""
    W, H = 860, 380
    frags = []
    frags.append(text(W / 2, 30,
                      "Шлюз дволикий: назовні — мова домену, всередині — мова чужини",
                      size=16, bold=True))

    # центральна рамка — шлюз
    gw = rect(300, 90, 260, 210, fill="#fff7e6", stroke="#d68910", sw=2, rx=10)
    frags.append(gw)
    frags.append(text(430, 116, "Шлюз", size=14, bold=True, color="#b9770e"))
    inb, _, _ = textbox(430, 165, "tariffFor(\n  segment)\n→ Tariff", size=12, min_w=170,
                        fill=BG, stroke="#d68910")
    frags.append(inb)
    frags.append(line(430, 210, 430, 235, color=MUTED, sw=1, dash="3 3"))
    outb, _, _ = textbox(430, 268, "склей URL, GET,\nрозбери 406,\nмапни JSON", size=11,
                         min_w=180, fill="#fdecea", stroke=POS)
    frags.append(outb)

    # ліворуч — домен, говорить із чистим боком
    dom, _, _ = textbox(140, 165, "домен\nзнає лише\nчистий бік", size=12, min_w=140,
                        fill="#eafaf1", stroke=FIELD)
    frags.append(dom)
    frags.append(arrow(212, 165, 344, 165, color=FIELD, sw=2))
    frags.append(text(278, 150, "проста\nмова", size=11, color=FIELD, bold=True))

    # праворуч — чужа система
    ext, _, _ = textbox(700, 268, "чужа\nсистема", size=12, min_w=120,
                        fill="#fdecea", stroke=POS)
    frags.append(ext)
    frags.append(arrow(522, 268, 638, 268, color=POS, sw=2))
    frags.append(text(600, 252, "дивна\nмова", size=11, color=POS, bold=True))

    frags.append(text(W / 2, 340,
                      "уся дивина замкнена всередині; назовні шлюз має вигляд звичайного об'єкта",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "two-sides.svg"), W, H, *frags)


def fig_intent_not_shape():
    """Три обгортки однакові на вигляд, різні за наміром: Адаптер, Фасад, Шлюз."""
    W, H = 900, 400
    frags = []
    frags.append(text(W / 2, 30,
                      "Однакова механіка — різний намір: що саме обгортка обіцяє",
                      size=16, bold=True))

    cards = [
        ("Адаптер", "чужий інтерфейс →\nпотрібна тобі форма",
         "намір: підігнати\nневідповідні роз'єми", "#eaf0fd", NEG),
        ("Фасад", "плутане нутро →\nодні прості двері",
         "намір: сховати\nскладність підсистеми", "#eafaf1", FIELD),
        ("Шлюз", "доступ до ЗОВНІШНЬОГО →\nметод у мові домену",
         "намір: стерегти межу\nіз чужою системою", "#fff7e6", "#d68910"),
    ]
    x0 = 155
    for i, (name, what, intent, fill, col) in enumerate(cards):
        cx = x0 + i * 300
        frags.append(rect(cx - 120, 80, 240, 250, fill=fill, stroke=col, sw=2, rx=10))
        frags.append(text(cx, 112, name, size=15, bold=True, color=col))
        w1, _, _ = textbox(cx, 165, what, size=11, min_w=200, fill=BG, stroke=col)
        frags.append(w1)
        w2, _, _ = textbox(cx, 260, intent, size=11, min_w=200, fill=BG, stroke=MUTED, color=MUTED)
        frags.append(w2)

    frags.append(text(W / 2, 375,
                      "код може виглядати однаково — назвою ти кажеш читачеві, ЧОМУ ця обгортка існує",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "intent-not-shape.svg"), W, H, *frags)


def fig_real_vs_stub():
    """Той самий інтерфейс шлюзу: у проді — справжній, у тесті — підробка."""
    W, H = 900, 400
    frags = []
    frags.append(text(W / 2, 30,
                      "Одна обіцянка шлюзу — дві реалізації: справжня і підробна",
                      size=16, bold=True))

    # інтерфейс угорі
    iface, _, _ = textbox(W / 2, 95, "інтерфейс  TariffGateway :  tariffFor(segment) → Tariff",
                          size=13, bold=True, min_w=560, fill="#fff7e6", stroke="#d68910")
    frags.append(iface)

    # дві реалізації внизу
    real, _, _ = textbox(255, 250, "HttpTariffGateway\nсклей URL, GET по мережі,\nрозбери коди, мапни JSON",
                         size=11, min_w=280, fill="#fdecea", stroke=POS)
    frags.append(real)
    frags.append(arrow(380, 120, 300, 205, color=POS, sw=1.8))
    frags.append(text(300, 165, "у проді", size=11, color=POS, bold=True))

    stub, _, _ = textbox(645, 250, "StubTariffGateway\nповерни Tariff(0.05)\nбез мережі, миттєво",
                         size=11, min_w=260, fill="#eaf0fd", stroke=NEG)
    frags.append(stub)
    frags.append(arrow(500, 120, 600, 205, color=NEG, sw=1.8))
    frags.append(text(600, 165, "у тесті", size=11, color=NEG, bold=True))

    frags.append(text(W / 2, 330,
                      "домен кличе tariffFor() і не знає, хто по той бік — тому тест іде без мережі",
                      size=12, color=MUTED, italic=True))
    frags.append(text(W / 2, 358,
                      "поміняли постачальника тарифів → новий клас збоку, домен не чіпаємо",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "real-vs-stub.svg"), W, H, *frags)


def fig_gateway_vs_gof():
    """Дві межі, якими Фаулер відрізнив шлюз від Фасада й Адаптера (для hist-вставки)."""
    W, H = 980, 430
    frags = []
    frags.append(text(W / 2, 30,
                      "Чим шлюз не Фасад і не Адаптер — межі, що виправдали нову назву",
                      size=16, bold=True))

    # ── Фасад ──
    cx = 180
    frags.append(rect(cx - 130, 80, 260, 250, fill="#eafaf1", stroke=FIELD, sw=2, rx=10))
    frags.append(text(cx, 112, "Фасад", size=15, bold=True, color=FIELD))
    frags.append(mtext(cx, 148, "двері будує АВТОР\nсистеми — для всіх",
                       size=11, color=INK))
    # стрілка зсередини системи назовні
    frags.append(rect(cx - 60, 200, 120, 48, fill=BG, stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(cx, 229, "нутро системи", size=11))
    frags.append(arrow(cx, 200, cx, 172, color=FIELD, sw=2))
    frags.append(text(cx, 300, "зсередини → назовні", size=11, color=MUTED, italic=True))

    # ── Адаптер ──
    cx = 490
    frags.append(rect(cx - 140, 80, 280, 250, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    frags.append(text(cx, 112, "Адаптер", size=15, bold=True, color=NEG))
    frags.append(mtext(cx, 148, "обидва роз'єми\nВЖЕ готові",
                       size=11, color=INK))
    frags.append(rect(cx - 118, 196, 84, 46, fill=BG, stroke=NEG, sw=1.5, rx=6))
    frags.append(text(cx - 76, 224, "роз'єм A", size=11))
    frags.append(rect(cx + 34, 196, 84, 46, fill=BG, stroke=NEG, sw=1.5, rx=6))
    frags.append(text(cx + 76, 224, "роз'єм Б", size=11))
    frags.append(arrow(cx - 34, 219, cx + 34, 219, color=NEG, sw=2))
    frags.append(text(cx, 300, "лише міст між готовими", size=11, color=MUTED, italic=True))

    # ── Шлюз ──
    cx = 810
    frags.append(rect(cx - 140, 80, 280, 250, fill="#fff7e6", stroke="#d68910", sw=2, rx=10))
    frags.append(text(cx, 112, "Шлюз", size=15, bold=True, color="#b9770e"))
    frags.append(mtext(cx, 148, "двері будує КЛІЄНТ\nпід себе",
                       size=11, color=INK))
    # ліворуч — вільний, самим-накреслений бік (пунктир); праворуч — готова чужина
    frags.append(rect(cx - 120, 196, 92, 46, fill=BG, stroke="#d68910", sw=1.5, rx=6, ))
    frags.append(mtext(cx - 74, 216, "мій бік —\nвигадую сам", size=10, color="#b9770e"))
    frags.append(rect(cx + 30, 196, 92, 46, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(mtext(cx + 76, 216, "чужина —\nготова", size=10, color=POS))
    frags.append(arrow(cx - 28, 219, cx + 30, 219, color="#d68910", sw=2))
    frags.append(text(cx, 300, "свій бік — з нуля, під потребу", size=11, color=MUTED, italic=True))

    frags.append(text(W / 2, 400,
                      "«різниці досить, аби виправдати нову назву» — М. Фаулер",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "gateway-vs-gof.svg"), W, H, *frags)


def fig_gateway_timeline():
    """Три віхи патерна: книга 2002, стаття-рефакторинг 2015, повна стаття 2021."""
    W, H = 1000, 340
    frags = []
    frags.append(text(W / 2, 30,
                      "Дев'ятнадцять років патерна «Шлюз» за трьома віхами",
                      size=16, bold=True))

    # горизонтальна вісь
    axis_y = 120
    frags.append(line(80, axis_y, 920, axis_y, color=LINE, sw=2))
    frags.append(arrow(900, axis_y, 924, axis_y, color=LINE, sw=2))

    milestones = [
        (200, "5 листопада 2002", "PoEAA",
         "короткий запис у каталозі,\nвводить назву Gateway,\nвагання проти Facade /\nAdapter / Mediator", "#d68910", "#fff7e6"),
        (500, "17 лютого 2015", "рефакторинг",
         "патерн у РУСІ:\nживий приклад із API\nYouTube, клас\nYoutubeGateway", NEG, "#eaf0fd"),
        (800, "10 серпня 2021", "стаття «Gateway»",
         "повне пояснення,\nприклад бронювання\nобладнання; визнання:\nназва не прижилася", FIELD, "#eafaf1"),
    ]
    for x, date, tag, body, col, fill in milestones:
        frags.append(circle(x, axis_y, 7, fill=col, stroke=col, sw=2))
        frags.append(text(x, axis_y - 18, date, size=12, bold=True, color=col))
        b, _, _ = textbox(x, 232, body, size=10.5, min_w=210, fill=fill, stroke=col)
        frags.append(b)
        frags.append(text(x, 168, tag, size=12, bold=True, color=INK))
        # конектор від осі до тега — обриваємо ВИЩЕ тега, щоб не перетнути напис
        frags.append(line(x, axis_y + 8, x, 154, color=col, sw=1.2, dash="2 3"))

    render(os.path.join(IMG, "gateway-timeline.svg"), W, H, *frags)


def fig_tariff_pipeline():
    """Усередині шлюзу: три переклади поспіль + захист мережі (повтор/таймаут)."""
    W, H = 1140, 470
    frags = []
    frags.append(text(W / 2, 30,
                      "Усередині шлюзу: три переклади поспіль, мережевий крок під захистом",
                      size=16, bold=True))

    # велика рамка воріт
    frags.append(rect(40, 150, 960, 205, fill="#fff7e6", stroke="#d68910", sw=2, rx=12))
    frags.append(text(158, 174, "HttpТарифШлюз", size=13, bold=True, color="#b9770e"))

    yc = 262  # спільна вісь ланцюга

    # 1) вхід: Напрямок (наш світ)
    b1, w1, _ = textbox(115, yc, "Напрямок", size=12, bold=True, min_w=105,
                        fill="#eafaf1", stroke=FIELD)
    frags.append(b1)
    frags.append(text(115, 328, "наш світ", size=11, color=FIELD, italic=True))

    # 2) складання URL (переклад 1)
    b2, w2, _ = textbox(315, yc, "складання\nURL", size=11, min_w=105,
                        fill="#eaf0fd", stroke=NEG)
    frags.append(b2)
    frags.append(arrow(115 + w1 / 2, yc, 315 - w2 / 2, yc, color=INK, sw=1.8))
    frags.append(mtext(215, 214, "переклад 1\nНапрямок → seg=…&v=3",
                       size=10, color=NEG, bold=True))

    # 3) мережевий запит (під захистом) + петля повтору над ним
    b3, w3, _ = textbox(545, yc, "мережевий\nзапит GET", size=11, min_w=118,
                        fill="#fdecea", stroke=POS)
    frags.append(b3)
    frags.append(arrow(315 + w2 / 2, yc, 545 - w3 / 2, yc, color=INK, sw=1.8))
    frags.append(mtext(430, 214, "захист:\nтаймаут + повтор",
                       size=10, color=MUTED, bold=True))
    # петля повтору — цілком над рамкою воріт, щоб не перетнути чужі написи
    lx = 545
    frags.append(line(lx - 24, 148, lx - 24, 108, color=POS, sw=1.6))
    frags.append(line(lx - 24, 108, lx + 24, 108, color=POS, sw=1.6))
    frags.append(arrow(lx + 24, 108, lx + 24, 148, color=POS, sw=1.6))
    frags.append(mtext(lx, 92, "обрив / таймаут / 5xx → повторити;   406 / 419 — НІ, остаточні",
                       size=10, color=POS, bold=True))

    # 4) розбір відповіді (переклад 2)
    b4, w4, _ = textbox(778, yc, "розбір\nвідповіді", size=11, min_w=105,
                        fill="#eaf0fd", stroke=NEG)
    frags.append(b4)
    frags.append(arrow(545 + w3 / 2, yc, 778 - w4 / 2, yc, color=INK, sw=1.8))
    frags.append(mtext(662, 214, "переклад 2\nкоди → винятки",
                       size=10, color=NEG, bold=True))
    frags.append(mtext(662, 320, "406 → ТарифНедоступний\n419 → ДоступПрострочено",
                       size=9, color=MUTED))

    # межа воріт (пунктир) — тут чужа мова закінчується
    frags.append(line(915, 150, 915, 355, color="#d68910", sw=1.5, dash="4 4"))
    frags.append(mtext(915, 373, "тут чужа мова закінчується",
                       size=10, color="#b9770e", bold=True))

    # 5) вихід: Тариф (наш світ), за межею
    b5, w5, _ = textbox(1055, yc, "Тариф", size=12, bold=True, min_w=105,
                        fill="#eafaf1", stroke=FIELD)
    frags.append(b5)
    frags.append(arrow(778 + w4 / 2, yc, 1055 - w5 / 2, yc, color=INK, sw=1.8))
    frags.append(mtext(962, 200, "переклад 3\nrate_bps/100\n→ Тариф",
                       size=10, color=FIELD, bold=True))
    frags.append(text(1055, 328, "наш світ", size=11, color=FIELD, italic=True))

    frags.append(text(W / 2, 440,
                      "домен бачить лише лівий вхід і правий вихід — три переклади й захист сховані у воротах",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "tariff-pipeline.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_scatter_vs_gateway()
    fig_two_sides()
    fig_intent_not_shape()
    fig_real_vs_stub()
    fig_gateway_vs_gof()
    fig_gateway_timeline()
    fig_tariff_pipeline()
    print("ok")
