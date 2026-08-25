# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def spectrum():
    W, H = 860, 380
    parts = []

    # Головна вісь
    ax_y = 120
    x0, x1 = 90, W - 90
    parts.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2.2))
    parts.append(arrow(x1 - 2, ax_y, x1 + 2, ax_y, color=INK, sw=2.2))
    parts.append(arrow(x0 + 2, ax_y, x0 - 2, ax_y, color=INK, sw=2.2))

    # Полюси осі — підписи стоять НАД віссю, по краях, поза рамками варіантів
    parts.append(text(x0 + 4, ax_y - 58, "чуже · швидко", size=13, color=MUTED, anchor="start", italic=True))
    parts.append(text(x1 - 4, ax_y - 58, "своє · під контролем", size=13, color=MUTED, anchor="end", italic=True))

    # Чотири варіанти як рамки на осі (від «чужого» ліворуч до «свого» праворуч)
    labels = [
        ("adopt\n(відкрите)", FIELD),
        ("SaaS\n(оренда)",    FIELD),
        ("buy\n(ліцензія)",   NEG),
        ("build\n(своє)",     POS),
    ]
    n = len(labels)
    span = x1 - x0
    xs = [x0 + span * (i + 0.5) / n for i in range(n)]
    for cx, (lab, col) in zip(xs, labels):
        # маркер на осі
        parts.append(circle(cx, ax_y, 5, fill=BG, stroke=col, sw=2.2))
        # рамка з підписом під маркером
        body, bw, bh = textbox(cx, ax_y + 46, lab, size=14, pad=9, stroke=col, sw=1.8, min_w=110)
        parts.append(body)

    # Дві протилежні стрілки-виміри під варіантами — обидві ростуть управо
    lane_y1 = 250
    lane_y2 = 300
    lx0, lx1 = xs[0], xs[-1]
    parts.append(arrow(lx0, lane_y1, lx1, lane_y1, color=POS, sw=2))
    parts.append(text((lx0 + lx1) / 2, lane_y1 - 12, "контроль над рішенням росте →",
                      size=13, color=POS, bold=True))
    parts.append(arrow(lx0, lane_y2, lx1, lane_y2, color=NEG, sw=2))
    parts.append(text((lx0 + lx1) / 2, lane_y2 - 12, "тягар супроводу й оновлень росте →",
                      size=13, color=NEG, bold=True))

    # Нижній підсумок-рядок
    parts.append(text(W / 2, 345, "більше свого = більше влади, але й більше зобов'язань",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'spectrum.svg'), W, H, *parts)


def timeline():
    # Дві нитки думки, що сходяться праворуч у точку «рішення build vs buy».
    W, H = 1040, 560
    parts = []

    x_left = 70
    x_join = 900          # x, де нитки сходяться
    y_top = 130           # нитка «оренда-як-послуга»
    y_bot = 400           # нитка «ядро / фон»

    # Заголовки ниток (ліворуч, поза вузлами)
    parts.append(text(x_left, y_top - 74, "оренда-як-послуга", size=15, color=POS,
                      anchor="start", bold=True))
    parts.append(text(x_left, y_bot - 74, "поділ на ядро та фон", size=15, color=FIELD,
                      anchor="start", bold=True))

    # ── Верхня нитка: вузли з роками ──
    top_nodes = [
        (0.02, "1961", "Маккарті:\nобчислення —\nкомунальна послуга"),
        (0.24, "1960-70-ті", "поділ часу:\nоренда\nмашинного часу"),
        (0.50, "кінець 1990-х", "хвиля ASP\n(«apps on tap»)"),
        (0.72, "лют. 2001", "SIIA-довідник:\nназва\n«software\nas a service»"),
        (0.93, "бер. 2005", "Кеніг:\nабревіатура\n«SaaS»"),
    ]
    # ── Нижня нитка: один вузол ──
    bot_nodes = [
        (0.50, "2000", "Мур, «Living on\nthe Fault Line»:\nядро vs фон"),
    ]

    span = x_join - x_left

    def draw_thread(nodes, y, col):
        # базова лінія нитки
        parts.append(line(x_left, y, x_join, y, color=col, sw=2.2))
        xs = []
        for frac, yr, lab in nodes:
            cx = x_left + span * frac
            xs.append(cx)
            # маркер року на лінії
            parts.append(circle(cx, y, 5.5, fill=BG, stroke=col, sw=2.2))
            # рік — над лінією, окремо, невеликим кеглем
            parts.append(text(cx, y - 16, yr, size=12, color=INK, bold=True))
            # підпис-рамка — під лінією, з запасом ширини
            body, bw, bh = textbox(cx, y + 58, lab, size=12, pad=8,
                                   stroke=col, sw=1.5, min_w=132)
            parts.append(body)
        return xs

    top_xs = draw_thread(top_nodes, y_top, POS)
    bot_xs = draw_thread(bot_nodes, y_bot, FIELD)

    # ── Точка сходження праворуч ──
    y_mid = (y_top + y_bot) / 2
    cx_join = x_join + 60
    # обидві нитки ведуть у спільний вузол
    parts.append(line(x_join, y_top, cx_join, y_mid, color=MUTED, sw=1.8))
    parts.append(line(x_join, y_bot, cx_join, y_mid, color=MUTED, sw=1.8))
    body, bw, bh = textbox(cx_join, y_mid, "рішення\nbuild vs buy", size=14, pad=11,
                           stroke=INK, sw=2, min_w=120, fill=FILL)
    parts.append(body)

    # Підсумок унизу
    parts.append(text(W / 2, H - 22,
                      "ядро (з 2000) каже ДЕ перевага · оренда (з 1961) робить ДЕШЕВИМ усе поза нею",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'timeline.svg'), W, H, *parts)


def plane():
    # Двовимірна площина: тягар експлуатації × контроль над напрямом.
    W, H = 900, 660
    parts = []
    left, right = 120, 860
    top, bottom = 80, 570
    aw, ah = right - left, bottom - top

    def px(fx): return left + aw * fx
    def py(fy): return bottom - ah * fy

    # Осі
    parts.append(line(left, bottom, right, bottom, color=INK, sw=2))
    parts.append(arrow(right - 2, bottom, right + 2, bottom, color=INK, sw=2))
    parts.append(line(left, bottom, left, top, color=INK, sw=2))
    parts.append(arrow(left, top + 2, left, top - 2, color=INK, sw=2))

    # Підписи осей (поза плотом)
    parts.append(text((left + right) / 2, bottom + 46, "тягар експлуатації →",
                      size=13, color=MUTED, italic=True))
    parts.append(text(left, bottom + 24, "нуль", size=12, color=MUTED))
    parts.append(text(right, bottom + 24, "повний", size=12, color=MUTED))
    parts.append(text(left, top - 22, "контроль над напрямом", size=13, color=MUTED,
                      anchor="start", italic=True))
    parts.append(text(left - 12, top + 10, "повний", size=12, color=MUTED, anchor="end"))
    parts.append(text(left - 12, bottom - 2, "низький", size=12, color=MUTED, anchor="end"))

    # Проста «пряма» — діагональ SaaS→build (обрізана, повз рамки варіантів)
    parts.append(line(px(0.12) + 74, py(0.15) - 30, px(0.90) - 70, py(0.90) + 30,
                      color=MUTED, sw=1.4, dash="6 5"))

    # Варіанти (fx = тягар, fy = контроль)
    opts = [
        (0.12, 0.15, "SaaS\n(оренда)",             NEG),
        (0.50, 0.22, "ліцензія\nна своєму залізі",  MUTED),
        (0.82, 0.62, "adopt\n(відкрите)",           POS),
        (0.90, 0.90, "build\n(своє)",               FIELD),
    ]
    for fx, fy, lab, col in opts:
        body, bw, bh = textbox(px(fx), py(fy), lab, size=14, pad=9,
                               stroke=col, sw=1.9, min_w=138)
        parts.append(body)

    parts.append(text(W / 2, H - 16,
                      "«adopt» вибивається вгору з простої діагоналі: повний тягар, та неповний контроль",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'plane.svg'), W, H, *parts)


def grid():
    # Сітка Мура: вирізняльність × критичність = чотири клітинки.
    W, H = 920, 660
    parts = []
    gl, gr = 210, 880
    gt, gb = 90, 560
    mx, my = (gl + gr) / 2, (gt + gb) / 2

    cells = [
        (gl + 6, gt + 6, (mx - gl) - 12, (my - gt) - 12,
         "КРИТИЧНИЙ ФОН — пастка\nне вирізняє, та критичне\n→ віддати спеціалістові,\nдля кого це ЯДРО\n(платежі · зарплатня · вхід)",
         "#fdecea", POS, 2.6),
        (mx + 6, gt + 6, (gr - mx) - 12, (my - gt) - 12,
         "ЯДРО й критичне\nвирізняє й не сміє впасти\n→ БУДУВАТИ своє\n(маршрут кур'єра)",
         "#eafaf1", FIELD, 2.0),
        (gl + 6, my + 6, (mx - gl) - 12, (gb - my) - 12,
         "ФОН допоміжний\nне вирізняє, збій не страшний\n→ брати найдешевше готове\n(розсилка · сховище)",
         "#eaf0fd", NEG, 1.8),
        (mx + 6, my + 6, (gr - mx) - 12, (gb - my) - 12,
         "ЯДРО допоміжне\nвирізняє, збій не фатальний\n→ радше своє, легко",
         "#f0faf4", FIELD, 1.6),
    ]
    for x, y, w, h, s, fl, st, sw in cells:
        parts.append(fitbox(x, y, w, h, s, size=14, pad=12, fill=fl, stroke=st, sw=sw))

    # Осі-підписи
    parts.append(text(mx, gb + 52, "вирізняльність →", size=14, color=INK, bold=True))
    parts.append(text((gl + mx) / 2, gb + 26, "фон — не вирізняє", size=12, color=MUTED))
    parts.append(text((mx + gr) / 2, gb + 26, "ядро — вирізняє", size=12, color=MUTED))
    parts.append(text(gl, gt - 16, "критичність ↑", size=13, color=INK, anchor="start", bold=True))
    parts.append(mtext(gl - 16, (gt + my) / 2 - 6, ["критичне", "не впасти"],
                       size=12, color=MUTED, anchor="end"))
    parts.append(text(gl - 16, (my + gb) / 2, "допоміжне", size=12, color=MUTED, anchor="end"))

    render(os.path.join(OUT, 'grid.svg'), W, H, *parts)


def crossover():
    # Накопичена вартість своє vs чуже; точка беззбитковості.
    W, H = 940, 560
    parts = []
    left, right = 90, 900
    top, bottom = 60, 480
    w, h = right - left, bottom - top
    MMAX, YMAX = 60.0, 260000.0

    def px(m): return left + w * (m / MMAX)
    def py(v): return bottom - h * (v / YMAX)

    # Осі
    parts.append(line(left, bottom, right, bottom, color=INK, sw=2))
    parts.append(arrow(right - 2, bottom, right + 2, bottom, color=INK, sw=2))
    parts.append(line(left, bottom, left, top, color=INK, sw=2))
    parts.append(arrow(left, top + 2, left, top - 2, color=INK, sw=2))

    # Тики X
    for m in (0, 12, 24, 36, 48, 60):
        x = px(m)
        parts.append(line(x, bottom, x, bottom + 5, color=INK, sw=1.4))
        parts.append(text(x, bottom + 20, str(m), size=11, color=MUTED))
    parts.append(text((left + right) / 2, bottom + 40, "місяці життя системи →",
                      size=13, color=MUTED, italic=True))
    # Тики Y
    parts.append(text(left, top - 18, "накопичені витрати, $", size=12, color=MUTED, anchor="start"))
    for v, lab in ((0, "0"), (60000, "60k"), (200000, "200k")):
        y = py(v)
        parts.append(line(left - 5, y, left, y, color=INK, sw=1.4))
        parts.append(text(left - 9, y + 4, lab, size=11, color=MUTED, anchor="end"))

    # Лінії витрат: своє 60000+2500m ; чуже 2500+4000m
    parts.append(line(px(0), py(60000), px(60), py(210000), color=FIELD, sw=2.6))
    parts.append(line(px(0), py(2500), px(60), py(242500), color=NEG, sw=2.6))

    # Перелом
    cx, cy = px(38.33), py(155750.0)
    parts.append(line(cx, cy, cx, bottom, color=MUTED, sw=1.3, dash="5 4"))
    parts.append(line(cx, cy, left, cy, color=MUTED, sw=1.3, dash="5 4"))
    parts.append(circle(cx, cy, 6, fill=BG, stroke=INK, sw=2.4))
    parts.append(text(cx + 20, bottom - 118, "перелом t* ≈ 38 міс",
                      size=12, color=INK, anchor="start", bold=True))

    # Легенда
    parts.append(line(118, 96, 150, 96, color=FIELD, sw=3))
    parts.append(text(156, 100, "своє: 60000 + 2500·міс", size=12, color=FIELD, anchor="start"))
    parts.append(line(118, 118, 150, 118, color=NEG, sw=3))
    parts.append(text(156, 122, "чуже: 2500 + 4000·міс", size=12, color=NEG, anchor="start"))

    # Області
    parts.append(mtext(250, 150, ["до перелому —", "дешевше ЧУЖЕ"], size=12, color=MUTED))
    parts.append(mtext(792, 300, ["після перелому —", "дешевше СВОЄ"], size=12, color=MUTED))

    render(os.path.join(OUT, 'crossover.svg'), W, H, *parts)


def seam():
    # Порти й адаптери проти розсипаних викликів чужого API.
    W, H = 940, 520
    parts = []

    parts.append(text(250, 34, "зі швом — постачальник за портом", size=14, color=INK, bold=True))
    parts.append(text(710, 34, "без шва — виклики розсипані", size=14, color=INK, bold=True))
    parts.append(line(485, 55, 485, 470, color=MUTED, sw=1.4, dash="6 5"))

    def box(cx, cy, s, col, mw=120, fill=FILL, sw=1.8):
        body, bw, bh = textbox(cx, cy, s, size=13, pad=9, stroke=col, sw=sw, min_w=mw, fill=fill)
        parts.append(body)

    # Ліва половина
    box(250, 78, "ваше ядро", INK, mw=130)
    box(250, 165, "порт (ваш інтерфейс):\nNotifier.notify(...)", FIELD, mw=190, sw=2.2)
    parts.append(arrow(250, 100, 250, 140, color=INK, sw=1.8))

    box(150, 290, "адаптер\nSendGrid", NEG, mw=110)
    box(360, 290, "адаптер\nSMTP", NEG, mw=110)
    parts.append(arrow(224, 190, 168, 262, color=INK, sw=1.8))
    parts.append(arrow(286, 190, 350, 262, color=INK, sw=1.8))

    box(150, 405, "SendGrid", MUTED, mw=110)
    box(360, 405, "поштовий\nсервер", MUTED, mw=110)
    parts.append(arrow(150, 318, 150, 378, color=MUTED, sw=1.6))
    parts.append(arrow(360, 318, 360, 378, color=MUTED, sw=1.6))

    parts.append(text(250, 462, "зміна постачальника — лише адаптер", size=12, color=FIELD, italic=True))

    # Права половина
    box(710, 130, "ваше ядро\n(виклики SendGrid\nрозсипані всередині)", POS, mw=200, sw=2.0)
    box(710, 405, "SendGrid", MUTED, mw=130)
    for sx, ex in ((650, 686), (690, 700), (730, 714), (770, 726)):
        parts.append(arrow(sx, 178, ex, 378, color=POS, sw=1.5))
    parts.append(mtext(560, 285, ["прямі виклики", "чужого API", "×багато місць"],
                       size=12, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, 'seam.svg'), W, H, *parts)


def _polyline(pts, color, sw, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (s, color, sw, d))


def discount():
    # Ціна часу гне прямі в угнуті криві й зсуває перелом ПІЗНІШЕ.
    # Числа з наскрізного прикладу: Sбуд=60000 m=2500 ; Sкуп=2500 f=4000 ; r=10%/рік.
    W, H = 960, 580
    parts = []
    left, right = 95, 915
    top, bottom = 70, 490
    w, h = right - left, bottom - top
    MMAX, YMAX = 72.0, 300000.0
    r = 0.10 / 12.0

    def px(m): return left + w * (m / MMAX)
    def py(v): return bottom - h * (v / YMAX)

    def a(t):
        return 0.0 if t <= 0 else (1 - (1 + r) ** (-t)) / r

    # Осі
    parts.append(line(left, bottom, right, bottom, color=INK, sw=2))
    parts.append(arrow(right - 2, bottom, right + 2, bottom, color=INK, sw=2))
    parts.append(line(left, bottom, left, top, color=INK, sw=2))
    parts.append(arrow(left, top + 2, left, top - 2, color=INK, sw=2))

    for m in (0, 12, 24, 36, 48, 60, 72):
        x = px(m)
        parts.append(line(x, bottom, x, bottom + 5, color=INK, sw=1.3))
        parts.append(text(x, bottom + 20, str(m), size=11, color=MUTED))
    parts.append(text((left + right) / 2, bottom + 42, "місяці життя системи →",
                      size=13, color=MUTED, italic=True))
    parts.append(text(left, top - 40, "теперішня вартість накопичених витрат, $",
                      size=12, color=MUTED, anchor="start"))
    for v, lab in ((0, "0"), (100000, "100k"), (200000, "200k"), (300000, "300k")):
        y = py(v)
        parts.append(line(left - 5, y, left, y, color=INK, sw=1.3))
        parts.append(text(left - 9, y + 4, lab, size=11, color=MUTED, anchor="end"))

    # Номінальні прямі (пунктир, тонко)
    parts.append(line(px(0), py(60000), px(72), py(60000 + 2500 * 72),
                      color=FIELD, sw=1.6, dash="6 5"))
    parts.append(line(px(0), py(2500), px(72), py(2500 + 4000 * 72),
                      color=NEG, sw=1.6, dash="6 5"))
    # Дисконтовані криві (суцільні, товсто)
    own = [(px(t), py(60000 + 2500 * a(t))) for t in range(0, 73)]
    frn = [(px(t), py(2500 + 4000 * a(t))) for t in range(0, 73)]
    parts.append(_polyline(own, FIELD, 3.0))
    parts.append(_polyline(frn, NEG, 3.0))

    # Номінальний перелом a=t → t=38.33
    tn, yn = 38.33, 60000 + 2500 * 38.33
    # Дисконтований перелом: a(t)=38.33 → знайти t
    td = 38.33
    for t in range(1, 400):
        if a(t) >= 38.33:
            td = (t - 1) + (38.33 - a(t - 1)) / (a(t) - a(t - 1))
            break
    yd = 60000 + 2500 * 38.33

    # Спільна висота перелому — тонка горизонталь
    parts.append(line(left, py(yn), px(td) + 40, py(yn), color=MUTED, sw=1.0, dash="4 4"))
    parts.append(text(px(66), py(yn) + 22, "перелам ≈ 156k $", size=11,
                      color=MUTED, anchor="middle"))

    # Маркери переломів
    parts.append(line(px(tn), py(yn), px(tn), bottom, color=FIELD, sw=1.1, dash="4 4"))
    parts.append(circle(px(tn), py(yn), 5.5, fill=BG, stroke=INK, sw=2.2))
    parts.append(line(px(td), py(yd), px(td), bottom, color=NEG, sw=1.1, dash="4 4"))
    parts.append(circle(px(td), py(yd), 5.5, fill=BG, stroke=INK, sw=2.2))

    # Стрілка зсуву + підпис (у чистій верхній зоні, ліворуч)
    parts.append(arrow(px(tn) + 4, py(240000), px(td) - 4, py(240000), color=INK, sw=1.8))
    body, bw, bh = textbox((px(tn) + px(td)) / 2, py(262000),
                           "дисконт зсуває перелам\nз 38 на 46 міс (+8)",
                           size=12, pad=8, stroke=INK, sw=1.5, min_w=210, fill=FILL)
    parts.append(body)

    # Легенда (правий верх, чиста зона)
    lx = px(6)
    parts.append(text(lx, py(298000), "суцільна — теперішня (дисконтована) вартість",
                      size=11, color=INK, anchor="start"))
    parts.append(text(lx, py(283000), "пунктир — номінальна сума без ціни часу",
                      size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'discount.svg'), W, H, *parts)


def seats():
    # Переворот рішення на МАСШТАБІ: опукла плата за місця vs великий вкладок свого.
    W, H = 940, 560
    parts = []
    left, right = 110, 900
    top, bottom = 70, 460
    w, h = right - left, bottom - top
    SMAX, YMAX = 14.0, 320.0

    def px(s): return left + w * (s / SMAX)
    def py(v): return bottom - h * (v / YMAX)

    def own(s): return 120 + 10 * s
    def rent(s): return 10 * (s ** 1.35)

    # Осі
    parts.append(line(left, bottom, right, bottom, color=INK, sw=2))
    parts.append(arrow(right - 2, bottom, right + 2, bottom, color=INK, sw=2))
    parts.append(line(left, bottom, left, top, color=INK, sw=2))
    parts.append(arrow(left, top + 2, left, top - 2, color=INK, sw=2))
    parts.append(text((left + right) / 2, bottom + 38,
                      "масштаб — кількість місць / обсяг даних →",
                      size=13, color=MUTED, italic=True))
    parts.append(text(left, top - 18, "річна вартість →", size=12, color=MUTED, anchor="start"))

    # Криві
    own_pts = [(px(s / 4.0), py(own(s / 4.0))) for s in range(0, 57)]
    rent_pts = [(px(s / 4.0), py(rent(s / 4.0))) for s in range(0, 57)]
    parts.append(_polyline(own_pts, FIELD, 3.0))
    parts.append(_polyline(rent_pts, NEG, 3.0))

    # Перелом на масштабі
    sc = 0.0
    for i in range(1, 561):
        s = i / 40.0
        if rent(s) >= own(s):
            sc = s
            break
    parts.append(line(px(sc), py(own(sc)), px(sc), bottom, color=MUTED, sw=1.1, dash="5 4"))
    parts.append(circle(px(sc), py(own(sc)), 5.5, fill=BG, stroke=INK, sw=2.4))
    parts.append(text(px(sc), bottom + 18, "N*", size=12, color=INK, bold=True))

    # Підписи кривих (кінці, чисті зони)
    parts.append(text(px(13.2), py(rent(13.2)) - 14, "оренда / SaaS:",
                      size=12, color=NEG, anchor="end", bold=True))
    parts.append(text(px(13.2), py(rent(13.2)) + 2, "плата за місце (опукла)",
                      size=12, color=NEG, anchor="end"))
    parts.append(text(px(13.4), py(own(13.4)) + 16, "своє: великий вкладок,",
                      size=12, color=FIELD, anchor="end", bold=True))
    parts.append(text(px(13.4), py(own(13.4)) + 32, "малий приріст за місце",
                      size=12, color=FIELD, anchor="end"))

    # Області рішення
    parts.append(mtext(px(3.4), py(250), ["малий масштаб:", "дешевша ОРЕНДА"],
                       size=12, color=MUTED))
    parts.append(mtext(px(11.6), py(70), ["великий масштаб:", "дешевше СВОЄ"],
                       size=12, color=MUTED))

    render(os.path.join(OUT, 'seats.svg'), W, H, *parts)


def option():
    # Цінність опціону шва як формула з рамок: p·уникнута − вартість шва.
    W, H = 1040, 300
    parts = []
    cy = 130

    def bx(cx, s, col, mw, fill=FILL, sw=2.0):
        body, bw, bh = textbox(cx, cy, s, size=13, pad=10, stroke=col, sw=sw,
                               min_w=mw, fill=fill)
        parts.append(body)
        return bw

    def op(cx, glyph):
        parts.append(text(cx, cy + 6, glyph, size=22, color=INK, bold=True))

    x1, x2, x3, x4, x5 = 140, 350, 565, 725, 905
    bx(x1, "уникнута\nвартість виходу\n$120k", NEG, 150)
    op((x1 + x2) / 2 - 6, "×")
    bx(x2, "імовірність\nзміни\n0.4", MUTED, 130)
    op((x2 + x3) / 2, "=")
    bx(x3, "очікувана\nекономія\n$48k", INK, 130)
    op((x3 + x4) / 2, "−")
    bx(x4, "вартість\nшва\n$8k", FIELD, 110)
    op((x4 + x5) / 2 + 4, "=")
    bx(x5, "цінність опціону\n+$40k\n→ ставити шов", POS, 160, fill="#eafaf1", sw=2.6)

    parts.append(text(W / 2, H - 26,
                      "опціон вартий додатного — право передумати окупає ціну шва; якби вийшло від'ємне, шов зайвий",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'option.svg'), W, H, *parts)


if __name__ == '__main__':
    spectrum()
    timeline()
    plane()
    grid()
    crossover()
    seam()
    discount()
    seats()
    option()
    print('done')
