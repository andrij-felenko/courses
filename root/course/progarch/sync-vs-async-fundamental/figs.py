# -*- coding: utf-8 -*-
"""Фігури до кроку «Синхронно проти асинхронно як фундаментальний вибір зчеплення»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#dfe9fb"
GREEN_FILL = "#eafaf0"
GRAY_FILL = "#eceef1"
YELLOW_FILL = "#fff8e6"
RED_FILL = "#fdecea"


def _band(x, w, ycenter, h, label, fill, color=INK, size=12, bold=True):
    """Смуга-сегмент активності на доріжці; текст автоматично влазить (fitbox)."""
    return fitbox(x, ycenter - h / 2, w, h, label, size=size, bold=bold,
                  fill=fill, stroke=INK, color=color)


def fig_temporal_coupling():
    """Дві часові доріжки: синхронно — вікна перекриваються; асинхронно — розчеплені чергою."""
    W, H = 1200, 700
    frags = []
    BH = 38

    # ═══════════ ВЕРХНЯ ПАНЕЛЬ — СИНХРОННО ═══════════
    frags.append(text(W / 2, 54,
                      "СИНХРОННО — викликач тримає взаємодію відкритою, доки отримувач не відповість",
                      size=15, bold=True, color=INK))

    ayc, byc = 168, 268
    # доріжки-базиси: рядок A суцільно вкритий смугами (лінія б усе одно ховалась під ними) —
    # рядок B лише в проміжках ПОЗА смугою «обробляє запит» (330–540), щоб напис лишався поза лінією
    frags.append(line(150, byc, 330, byc, color=MUTED, sw=1, dash="3,4"))
    frags.append(line(540, byc, 720, byc, color=MUTED, sw=1, dash="3,4"))
    frags.append(text(96, ayc - 6, "A", size=13, bold=True, color=INK))
    frags.append(text(96, ayc + 12, "викликач", size=10, color=MUTED))
    frags.append(text(96, byc - 6, "B", size=13, bold=True, color=INK))
    frags.append(text(96, byc + 12, "отримувач", size=10, color=MUTED))

    # рамка перекриття (обидва живі)
    frags.append(rect(330, 132, 210, 172, fill="none", stroke=POS, sw=1.6, rx=8))
    frags.append(rect(330, 132, 210, 172, fill="none", stroke=POS, sw=1.6, rx=8))
    frags.append(text(435, 122, "обидва живі в той самий час", size=12, bold=True, color=POS))

    # доріжка A: працює → чекає → продовжує
    frags.append(_band(150, 100, ayc, BH, "працює", BLUE_FILL))
    frags.append(_band(250, 310, ayc, BH, "заблоковано — чекає на B", GRAY_FILL, color=MUTED))
    frags.append(_band(560, 160, ayc, BH, "продовжує", BLUE_FILL))
    # доріжка B: обробляє (в вікні перекриття)
    frags.append(_band(330, 210, byc, BH, "обробляє запит", GREEN_FILL))

    # стрілки запит/відповідь
    frags.append(arrow(252, ayc + BH / 2, 330, byc - BH / 2, color=INK, sw=1.7))
    frags.append(text(262, 222, "запит", size=11, color=INK, anchor="start"))
    frags.append(arrow(540, byc - BH / 2, 560, ayc + BH / 2, color=INK, sw=1.7))
    frags.append(text(566, 222, "відповідь", size=11, color=INK, anchor="start"))

    frags.append(text(W / 2, 340,
                      "Активні вікна A і B ПЕРЕКРИВАЮТЬСЯ — сторони мусять жити одночасно. Впаде B — стоїть і A.",
                      size=13, color=MUTED))

    # ═══════════ НИЖНЯ ПАНЕЛЬ — АСИНХРОННО ═══════════
    frags.append(line(70, 384, W - 70, 384, color=MUTED, sw=1, dash="6,6"))
    frags.append(text(W / 2, 420,
                      "АСИНХРОННО — викликач віддає повідомлення посередникові й одразу йде далі",
                      size=15, bold=True, color=INK))

    ayc2, byc2 = 500, 626
    # рядок A суцільно вкритий смугами — рядок B лише в проміжку ПОЗА смугою «обробляє…» (510–720)
    frags.append(line(150, byc2, 510, byc2, color=MUTED, sw=1, dash="3,4"))
    frags.append(text(96, ayc2 - 6, "A", size=13, bold=True, color=INK))
    frags.append(text(96, ayc2 + 12, "викликач", size=10, color=MUTED))
    frags.append(text(96, byc2 - 6, "B", size=13, bold=True, color=INK))
    frags.append(text(96, byc2 + 12, "отримувач", size=10, color=MUTED))

    # A: працює → продовжує одразу (не чекає)
    frags.append(_band(150, 100, ayc2, BH, "працює", BLUE_FILL))
    frags.append(_band(250, 470, ayc2, BH, "продовжує одразу — не чекає на B", BLUE_FILL))
    # B: обробляє пізніше
    frags.append(_band(510, 210, byc2, BH, "обробляє, коли доступна (пізніше)", GREEN_FILL))

    # черга-посередник між доріжками
    qb, qw, _ = textbox(400, 563, "черга\nтримає повідомлення", size=12, bold=True,
                        fill=YELLOW_FILL, stroke=MUTED, sw=1.6, min_w=210)
    frags.append(qb)
    # A кладе в чергу
    frags.append(arrow(252, ayc2 + BH / 2, 372, 548, color=INK, sw=1.7))
    frags.append(text(258, 536, "кладе", size=11, color=INK, anchor="start"))
    # B витягує пізніше
    frags.append(arrow(430, 578, 512, byc2 - BH / 2, color=INK, sw=1.7))
    frags.append(text(480, 598, "витягує пізніше", size=11, color=INK, anchor="start"))

    # позначки часу розриву
    frags.append(line(252, ayc2 + BH / 2, 252, byc2 + 30, color=POS, sw=1, dash="4,4"))
    frags.append(line(510, byc2 - BH / 2, 510, byc2 + 30, color=POS, sw=1, dash="4,4"))
    frags.append(text(381, byc2 + 46, "Δt — сторони не зустрічаються; черга перекриває розрив",
                      size=12, bold=True, color=POS))

    frags.append(text(W / 2, 690,
                      "Активні вікна НЕ перекриваються. A виживає, навіть якщо B лежить, — повідомлення чекає в черзі.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "temporal-coupling.svg"), W, H, *frags,
           title="Зчеплення в часі: синхронно проти асинхронно")


def fig_availability_chain():
    """Синхронний ланцюг перемножує доступність униз — простій росте з глибиною."""
    W, H = 1120, 470
    frags = []
    frags.append(text(W / 2, 54, "Синхронний ланцюг перемножує доступність УНИЗ",
                      size=16, bold=True, color=INK))

    xs = [175, 405, 635, 865]
    names = ["A", "B", "C", "D"]
    y = 150
    bw = 150
    for i, (x, nm) in enumerate(zip(xs, names)):
        frags.append(_band(x - bw / 2, bw, y, 56, nm + "\n99.9%", BLUE_FILL, size=14))
        if i > 0:
            frags.append(arrow(xs[i - 1] + bw / 2 + 6, y, x - bw / 2 - 6, y, color=INK, sw=1.8))

    # стовпчики добутку під кожною ланкою
    prod = [
        ("0.999", "99.9%", "8.8 год/рік"),
        ("0.999²", "99.8%", "17.5 год"),
        ("0.999³", "99.7%", "26 год"),
        ("0.999⁴", "99.6%", "35 год"),
    ]
    py = 250
    for x, (p, a, d) in zip(xs, prod):
        frags.append(line(x, 178, x, py - 6, color=MUTED, sw=1, dash="3,4"))
        frags.append(text(x, py + 8, p, size=14, bold=True, color=INK))
        frags.append(text(x, py + 30, a, size=13, color=NEG))
        frags.append(text(x, py + 52, d, size=12, color=POS))
    frags.append(text(xs[0] - bw / 2 - 18, py + 8, "добуток:", size=11, color=MUTED, anchor="end"))
    frags.append(text(xs[0] - bw / 2 - 18, py + 52, "простій:", size=11, color=MUTED, anchor="end"))

    box, _, _ = textbox(W / 2, 372,
                        "10 ланок поспіль → 0.999¹⁰ ≈ 99.0% → ≈ 87 год простою на рік — удесятеро більше за одну ланку.",
                        size=13, bold=True, fill=RED_FILL, stroke=POS, sw=1.7, min_w=880)
    frags.append(box)
    frags.append(text(W / 2, 430,
                      "Асинхронність розриває ланцюг: A залежить від черги, а не від того, чи живі B, C, D разом.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "availability-chain.svg"), W, H, *frags,
           title=None)


def fig_decision():
    """Евристика вибору: результат потрібен ЗАРАЗ → синхронно; робота може пізніше → асинхронно."""
    W, H = 1160, 540
    frags = []

    q, qw, qh = textbox(W / 2, 92,
                        "Чи потрібен викликачеві результат ЗАРАЗ, щоб рухатися далі?",
                        size=15, bold=True, fill=YELLOW_FILL, stroke=INK, sw=1.8, min_w=760)
    frags.append(q)

    LX, RX = 300, 860
    # стрілки-гілки
    frags.append(arrow(W / 2 - 120, 92 + qh / 2, LX + 40, 176, color=INK, sw=1.8))
    frags.append(arrow(W / 2 + 120, 92 + qh / 2, RX - 40, 176, color=INK, sw=1.8))
    frags.append(text(W / 2 - 210, 150, "так", size=13, bold=True, color=FIELD))
    frags.append(text(W / 2 + 220, 150, "ні / інше", size=13, bold=True, color=NEG))

    # заголовки колонок
    hl, hlw, _ = textbox(LX, 208, "СИНХРОННО\nзапит → відповідь", size=14, bold=True,
                         fill=GREEN_FILL, stroke=FIELD, sw=2, min_w=300)
    hr, hrw, _ = textbox(RX, 208, "АСИНХРОННО\nповідомлення / подія", size=14, bold=True,
                         fill=BLUE_FILL, stroke=NEG, sw=2, min_w=300)
    frags.append(hl)
    frags.append(hr)

    def bullets(cx, top, lines, stroke):
        w = 380
        h = 26 + len(lines) * 30
        x = cx - w / 2
        frags.append(rect(x, top, w, h, fill=BG, stroke=stroke, sw=1.5, rx=8))
        for i, ln in enumerate(lines):
            frags.append(text(x + 20, top + 34 + i * 30, "• " + ln, size=13,
                              color=INK, anchor="start"))

    bullets(LX, 268, [
        "людина чекає відповіді на екрані",
        "потрібне негайне «вийшло / ні»",
        "проста лінійна логіка, один стек",
        "повільний B сам гальмує A",
    ], FIELD)
    bullets(RX, 268, [
        "робота може статися пізніше",
        "має пережити падіння отримувача",
        "розходиться на багатьох (віяло)",
        "вирівняти сплески навантаження",
    ], NEG)

    frags.append(text(W / 2, 512,
                      "Вибір — на КОЖНУ взаємодію окремо, не на всю систему. Один продукт спокійно живе з обома.",
                      size=13, bold=True, color=MUTED))

    render(os.path.join(IMG, "sync-async-decision.svg"), W, H, *frags,
           title=None)


def fig_pendulum():
    """Маятник галузі: сховати мережу (синхронно) ⇄ явне повідомлення (асинхронно)."""
    W, H = 1440, 560
    frags = []

    Y_SYNC, Y_ASYNC = 160, 400
    X0, X1 = 250, 1380

    # напрямні полюсів
    frags.append(line(X0, Y_SYNC, X1, Y_SYNC, color=MUTED, sw=1, dash="4,5"))
    frags.append(line(X0, Y_ASYNC, X1, Y_ASYNC, color=MUTED, sw=1, dash="4,5"))

    # лівий підпис полюсів
    frags.append(text(28, Y_SYNC - 4, "СХОВАТИ МЕРЕЖУ", size=13, bold=True, color=POS, anchor="start"))
    frags.append(text(28, Y_SYNC + 15, "виклик «як локальний»", size=11, color=MUTED, anchor="start"))
    frags.append(text(28, Y_ASYNC - 4, "ЯВНЕ ПОВІДОМЛЕННЯ", size=13, bold=True, color=NEG, anchor="start"))
    frags.append(text(28, Y_ASYNC + 15, "розчеплення в часі", size=11, color=MUTED, anchor="start"))

    # вузли: (x, рік, назва, полюс)  полюс: 's' угорі (синхронно), 'a' унизу (асинхронно)
    nodes = [
        (300, "1948", ["телеграфне", "реле 55-A"], "a"),
        (445, "1966", ["спулінг", "HASP"], "a"),
        (615, "1984", ["мрія RPC", "Birrell–Nelson"], "s"),
        (745, "1991", ["CORBA,", "об'єкти"], "s"),
        (895, "1993", ["MQSeries", "+ TIB"], "a"),
        (1075, "2002", ["ESB / SOA"], "s"),
        (1225, "2011", ["Kafka", "(лог)"], "a"),
        (1350, "2014", ["мікросервіси", "dumb pipes"], "a"),
    ]

    def ny(p):
        return Y_SYNC if p == "s" else Y_ASYNC

    # хвиля-маятник крізь вузли (у хронологічному порядку)
    pts = " ".join("%.0f,%.0f" % (x, ny(p)) for (x, _, _, p) in nodes)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pts, INK))

    # застереження 1994 на схилі між CORBA і MOM
    xm, ym = (745 + 895) / 2, (Y_SYNC + Y_ASYNC) / 2
    frags.append(circle(xm, ym, 6, fill=RED_FILL, stroke=POS, sw=2))
    frags.append(text(xm + 16, ym - 6, "1994 «A Note…»", size=11, bold=True, color=POS, anchor="start"))
    frags.append(text(xm + 16, ym + 10, "дистанцію не сховати", size=10, color=MUTED, anchor="start"))

    # вузли й підписи
    for (x, yr, lbl, p) in nodes:
        y = ny(p)
        col = POS if p == "s" else NEG
        fillc = RED_FILL if p == "s" else BLUE_FILL
        frags.append(circle(x, y, 8, fill=fillc, stroke=col, sw=2.2))
        if p == "s":  # підпис угору
            frags.append(text(x, y - 40, yr, size=13, bold=True, color=INK))
            frags.append(mtext(x, y - 24, lbl, size=11, color=INK))
        else:         # підпис униз
            frags.append(text(x, y + 34, yr, size=13, bold=True, color=INK))
            frags.append(mtext(x, y + 50, lbl, size=11, color=INK))

    frags.append(text(W / 2, 512,
                      "Поле уваги галузі хитається туди-сюди — обидва зчеплення існують завжди, модним стає то одне, то інше.",
                      size=13, color=MUTED))
    frags.append(text(W / 2, 534,
                      "Щоразу маятник вертав, бо різницю локального й віддаленого сховати надовго не вдавалося.",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, "pendulum-lineage.svg"), W, H, *frags,
           title="Маятник: сховати мережу  ⇄  явне повідомлення")


def fig_store_and_forward():
    """Реле рваної стрічки = перша черга повідомлень; той самий силует у MQ і в лозі Kafka."""
    W, H = 1220, 560
    frags = []
    frags.append(text(W / 2, 40, "Store-and-forward: вузол тримає повідомлення, доки наступний готовий",
                      size=16, bold=True, color=INK))

    # ── верхній ряд: механізм телеграфного реле ──
    yc = 150
    # відправник
    frags.append(fitbox(50, yc - 35, 130, 70, "Відправник", size=13, bold=True, fill=BLUE_FILL, stroke=INK))
    # велика рамка реле
    frags.append(rect(240, 96, 620, 150, fill=GRAY_FILL, stroke=INK, sw=1.6, rx=10))
    frags.append(text(550, 116, "Реле-вузол (torn-tape) — оператор рве стрічку, читає адресу",
                      size=12, bold=True, color=INK))
    frags.append(fitbox(262, 150, 120, 56, "вхідний\nтелетайп", size=11, fill=BG, stroke=MUTED))
    frags.append(arrow(388, 178, 428, 178, color=INK, sw=1.7))
    # черга — стрічки на гачках
    qx, qtop = 442, 148
    frags.append(rect(qx, qtop, 260, 60, fill=YELLOW_FILL, stroke=MUTED, sw=1.4, rx=6))
    for i in range(4):
        hx = qx + 34 + i * 58
        frags.append(line(hx, qtop + 6, hx, qtop + 16, color=MUTED, sw=1.4))     # гачок
        frags.append(rect(hx - 8, qtop + 16, 16, 30, fill=BG, stroke=INK, sw=1)) # стрічка
    frags.append(text(qx + 130, qtop + 74, "черга — стрічки на гачках,", size=11, color=MUTED))
    frags.append(text(qx + 130, qtop + 90, "доки вихідна лінія зайнята", size=11, color=MUTED))
    frags.append(arrow(708, 178, 748, 178, color=INK, sw=1.7))
    frags.append(fitbox(748, 150, 100, 56, "вихідний\nтелетайп", size=11, fill=BG, stroke=MUTED))
    # отримувач
    frags.append(arrow(864, yc, 916, yc, color=INK, sw=1.8))
    frags.append(fitbox(918, yc - 35, 140, 70, "Отримувач\n(пізніше)", size=12, bold=True, fill=GREEN_FILL, stroke=INK))
    frags.append(arrow(186, yc, 238, yc, color=INK, sw=1.8))

    frags.append(text(W / 2, 292,
                      "Відправник уже пішов, отримувач іще спить — а повідомлення живе на гачку в черзі. Це і є розчеплення в часі, зроблене руками.",
                      size=13, color=MUTED))

    # ── нижній ряд: один силует, три епохи ──
    frags.append(line(70, 330, W - 70, 330, color=MUTED, sw=1, dash="6,6"))
    frags.append(text(W / 2, 366, "Один силует — буфер, що тримає повідомлення через розрив у часі — три епохи",
                      size=14, bold=True, color=INK))

    era = [
        (250, "телеграфне реле", "гачок зі стрічкою", "1948"),
        (610, "MQSeries", "менеджер черг", "1993"),
        (970, "Kafka", "журнал-лог", "2011"),
    ]
    ey = 452
    for i, (x, name, sub, yr) in enumerate(era):
        frags.append(fitbox(x - 130, ey - 34, 260, 68, name + "\n" + sub, size=13, bold=True,
                            fill=BLUE_FILL, stroke=NEG))
        frags.append(text(x, ey + 54, yr, size=12, bold=True, color=MUTED))
        if i < len(era) - 1:
            frags.append(arrow(x + 132, ey, era[i + 1][0] - 132, ey, color=INK, sw=1.8))
            frags.append(text((x + era[i + 1][0]) / 2, ey - 44, "той самий силует", size=11,
                              italic=True, color=MUTED))

    render(os.path.join(IMG, "store-and-forward.svg"), W, H, *frags, title=None)


def fig_async_lifecycle():
    """Життя асинхронної команди: 202 зараз — стан згодом; дедуп, твін, мертва черга."""
    W, H = 1360, 660
    frags = []
    frags.append(text(W / 2, 32,
                      "Життя асинхронної команди «зачинити»: 202 зараз — кінцевий стан згодом",
                      size=17, bold=True, color=INK))

    spine = 300

    # ── три стани на хребті ──
    s1, _, _ = textbox(230, spine, "ACCEPTED\nприйнято · лежить у черзі",
                       size=13, bold=True, fill=BLUE_FILL, stroke=NEG, sw=2, min_w=250)
    s2, _, _ = textbox(680, spine, "PROCESSING\nспоживач узяв команду",
                       size=13, bold=True, fill=YELLOW_FILL, stroke=INK, sw=2, min_w=250)
    s3, _, _ = textbox(1140, spine, "DONE\nзачинено ✓ · твін оновлено",
                       size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2, min_w=250)
    frags += [s1, s2, s3]
    frags.append(arrow(360, spine, 550, spine, color=INK, sw=1.9))
    frags.append(arrow(810, spine, 1010, spine, color=INK, sw=1.9))

    # ── над хребтом: що спричиняє переходи ──
    ent, _, eh = textbox(230, 110,
                         "POST /homes/:id/lock\nхмара кладе в чергу → 202 {commandId}",
                         size=11, fill=GRAY_FILL, stroke=MUTED, sw=1.4, min_w=250)
    frags.append(ent)
    frags.append(arrow(230, 110 + eh / 2, 230, spine - 26, color=MUTED, sw=1.5))

    t1, _, t1h = textbox(455, 182,
                         "споживач тягне з черги\n⚠ at-least-once: той самий id\n"
                         "може прийти двічі → дедуп-ворота",
                         size=11, fill=RED_FILL, stroke=POS, sw=1.4, min_w=300)
    frags.append(t1)
    frags.append(arrow(455, 182 + t1h / 2, 455, spine - 12, color=MUTED, sw=1.5))

    t2, _, t2h = textbox(910, 128,
                         "hub.send(lock) → «locked»\nкінцевий стан → у ТВІН",
                         size=11, fill=GREEN_FILL, stroke=FIELD, sw=1.4, min_w=280)
    frags.append(t2)
    frags.append(arrow(910, 128 + t2h / 2, 910, spine - 12, color=MUTED, sw=1.5))

    # ── гілка невдачі: у мертву чергу ──
    frags.append(arrow(680, spine + 26, 680, 428, color=POS, sw=1.7))
    frags.append(mtext(720, 372,
                       ["не позначили «done» →", "повтор; після N спроб —",
                        "у мертву чергу"],
                       size=11, color=MUTED, anchor="start"))
    fb, _, _ = textbox(680, 462,
                       "FAILED\nпомилка N разів → МЕРТВА ЧЕРГА\n(людина розбере згодом)",
                       size=12, bold=True, fill=RED_FILL, stroke=POS, sw=1.8, min_w=340)
    frags.append(fb)

    # ── знизу: що бачить застосунок (кінцева узгодженість) ──
    note, _, _ = textbox(W / 2, 596,
                         "Застосунок одразу після 202 показує «в обробці», опитує GET /commands/{id} "
                         "(або слухає твін)\nі міняє на «зачинено» ЛИШЕ коли стан = done — доти "
                         "дім у кінцевій узгодженості.",
                         size=12, bold=True, fill=GRAY_FILL, stroke=INK, sw=1.6, min_w=1180)
    frags.append(note)

    render(os.path.join(IMG, "dh-async-lifecycle.svg"), W, H, *frags, title=None)


def fig_error_timing():
    """Де й коли зринає помилка: синхронно — зараз і у викликача; асинхронно — згодом і збоку."""
    W, H = 1200, 590
    frags = []
    frags.append(text(W / 2, 30, "Де й коли зринає помилка", size=17, bold=True, color=INK))

    # ═══ ВЕРХ — СИНХРОННО ═══
    frags.append(text(W / 2, 66,
                      "СИНХРОННО — помилка приходить у ТІЙ САМІЙ відповіді, поки викликач чекає",
                      size=14, bold=True, color=INK))
    ay = 168
    a1, _, _ = textbox(130, ay, "App\nPOST /lock", size=12, bold=True,
                       fill=BLUE_FILL, stroke=NEG, sw=1.8, min_w=110)
    frags.append(a1)
    frags.append(_band(205, 405, ay, 34, "заблоковано — чекає на весь ланцюг (хмара→хаб→замок)",
                       GRAY_FILL, color=MUTED, size=12, bold=False))
    frags.append(arrow(610, ay, 668, ay, color=INK, sw=1.8))
    r1, _, _ = textbox(770, ay, "504 timeout · 502 offline\nstate: unknown",
                       size=12, bold=True, fill=RED_FILL, stroke=POS, sw=1.8, min_w=230)
    frags.append(r1)
    frags.append(mtext(W / 2, 232,
                       ["Помилка — НЕГАЙНА і в обличчя викликачеві.",
                        "Але хаб офлайн → команду нема куди подіти → ВОНА ВТРАЧЕНА."],
                       size=12, color=MUTED))

    # ═══ НИЗ — АСИНХРОННО ═══
    frags.append(line(60, 288, W - 60, 288, color=MUTED, sw=1, dash="6,6"))
    frags.append(text(W / 2, 326,
                      "АСИНХРОННО — 202 одразу; збій осідає збоку й спливає ПІЗНІШЕ",
                      size=14, bold=True, color=INK))
    by = 408
    a2, _, _ = textbox(120, by, "App\nPOST /lock", size=12, bold=True,
                       fill=BLUE_FILL, stroke=NEG, sw=1.8, min_w=110)
    frags.append(a2)
    frags.append(arrow(178, by, 250, by, color=INK, sw=1.8))
    g2, _, _ = textbox(330, by, "202 {commandId}", size=12, bold=True,
                       fill=GREEN_FILL, stroke=FIELD, sw=1.8, min_w=150)
    frags.append(g2)
    frags.append(text(330, by - 40, "негайно — App вільний", size=11, color=FIELD, bold=True))
    frags.append(arrow(408, by, 486, by, color=MUTED, sw=1.6))
    frags.append(text(560, by - 40, "згодом, окремим шляхом", size=11, color=MUTED))
    f2, _, _ = textbox(620, by, "черга → споживач → hub.send", size=12,
                       fill=YELLOW_FILL, stroke=INK, sw=1.6, min_w=250)
    frags.append(f2)
    frags.append(arrow(748, by, 812, by, color=POS, sw=1.7))
    r2, _, _ = textbox(940, by, "МЕРТВА ЧЕРГА\n(після N невдач)", size=12, bold=True,
                       fill=RED_FILL, stroke=POS, sw=1.8, min_w=210)
    frags.append(r2)
    frags.append(arrow(620, by + 26, 620, 486, color=MUTED, sw=1.4))
    p2, _, _ = textbox(620, 512, "App: GET /commands/{id}\nбачить «failed» лише коли спитає",
                       size=11, fill=GRAY_FILL, stroke=MUTED, sw=1.4, min_w=300)
    frags.append(p2)
    frags.append(text(W / 2, 566,
                      "Ніхто не заблокований — але про збій мусить спитати хтось: "
                      "поллінг, монітор або людина біля мертвої черги.",
                      size=12, bold=True, color=MUTED))

    render(os.path.join(IMG, "dh-error-timing.svg"), W, H, *frags, title=None)


if __name__ == "__main__":
    fig_temporal_coupling()
    fig_availability_chain()
    fig_decision()
    fig_pendulum()
    fig_store_and_forward()
    fig_async_lifecycle()
    fig_error_timing()
    print("OK: temporal-coupling, availability-chain, sync-async-decision, pendulum-lineage, "
          "store-and-forward, dh-async-lifecycle, dh-error-timing")
