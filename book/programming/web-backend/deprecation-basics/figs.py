# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

AMBER = "#caa23a"


# ── lifecycle-timeline: активне → застаріле → знято, з вікном міграції ─────────
# Ідея: деприкейшн — не подія, а проміжок. Між днем оголошення й днем зняття
# лежить вікно міграції (місяці). Унизу — контраст: тихе видалення без вікна.
def fig_lifecycle():
    W, H = 800, 380
    p = []

    start, depr, sunset, end = 70, 290, 590, 730
    by, bh = 150, 40           # смуга фаз
    bt, bb = by, by + bh       # верх і низ смуги

    # три фази
    p.append(rect(start, by, depr - start, bh, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(rect(depr, by, sunset - depr, bh, fill="#fbf3da", stroke=AMBER, sw=1.8))
    p.append(rect(sunset, by, end - sunset, bh, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text((start + depr) / 2, by + 25, "Активне", size=13, color=FIELD, bold=True))
    p.append(text((depr + sunset) / 2, by + 25, "Застаріле — ще працює", size=13, color="#9a7d1f", bold=True))
    p.append(text((sunset + end) / 2, by + 25, "Знято", size=13, color=POS, bold=True))

    # маркери-дати
    for mx in (depr, sunset):
        p.append(line(mx, bt - 12, mx, bb + 12, color=INK, sw=2))

    # виноски згори
    d1, w1, h1 = textbox(depr, 66, "Deprecation + Sunset\nchangelog · лист",
                         size=11, bold=True, fill="#f6f4ec", stroke=INK, sw=1.6)
    p.append(d1)
    p.append(arrow(depr, 66 + h1 / 2, depr, bt - 12, color=INK, sw=1.6))
    d2, w2, h2 = textbox(sunset, 66, "маршрут прибрано\n410 Gone",
                         size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.6)
    p.append(d2)
    p.append(arrow(sunset, 66 + h2 / 2, sunset, bt - 12, color=POS, sw=1.6))

    # вікно міграції — двобічна стрілка під смугою
    wy = 208
    p.append(line(depr, bb + 6, depr, wy, color=MUTED, sw=1))
    p.append(line(sunset, bb + 6, sunset, wy, color=MUTED, sw=1))
    p.append(line(depr, wy, sunset, wy, color=MUTED, sw=1.4))
    p.append(arrow(depr + 26, wy, depr, wy, color=MUTED, sw=1.4))
    p.append(arrow(sunset - 26, wy, sunset, wy, color=MUTED, sw=1.4))
    p.append(text((depr + sunset) / 2, wy + 20, "вікно міграції — місяці",
                  size=12, color=MUTED, bold=True))

    # контраст: тихе видалення
    p.append(text(start, 288, "тихе видалення (чого уникаємо):",
                  size=11, color=POS, bold=True, anchor="start"))
    cy = 322
    brk = 520
    p.append(line(start, cy, brk, cy, color=FIELD, sw=3))
    p.append(text((start + brk) / 2, cy - 8, "Активне", size=10, color=MUTED))
    # злам
    p.append(line(brk - 8, cy - 9, brk + 8, cy + 9, color=POS, sw=2.6))
    p.append(line(brk + 8, cy - 9, brk - 8, cy + 9, color=POS, sw=2.6))
    p.append(text(brk + 18, cy + 4, "раптовий 500 — зламаний клієнт",
                  size=11, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "lifecycle-timeline.svg"), W, H, *p,
           title="Життєвий цикл: активне → застаріле → знято")


# ── dual-channel: сигнал доходить і до машини, і до людини ─────────────────────
# Ідея: одне оголошення розходиться двома каналами. Машинний (заголовки) читає
# моніторинг клієнта; людський (changelog/лист/банер) читає розробник. Контракт
# тримається лише коли доходять обидва.
def fig_dual_channel():
    W, H = 780, 390
    p = []

    ev, ew, eh = textbox(390, 66, "Оголошення\nзастарілим", size=13, bold=True,
                         fill="#f6f4ec", stroke=INK, sw=2)
    p.append(ev)

    lx, rx = 185, 595
    # заголовки колонок
    p.append(text(lx, 124, "Машина читає", size=13, color=NEG, bold=True))
    p.append(text(rx, 124, "Людина читає", size=13, color=FIELD, bold=True))
    p.append(arrow(360, 66 + eh / 2, lx + 40, 112, color=NEG, sw=1.7))
    p.append(arrow(420, 66 + eh / 2, rx - 40, 112, color=FIELD, sw=1.7))

    # ліва колонка — заголовки
    lb = [
        "Deprecation: @1719705599",
        "Sunset: Wed, 31 Dec 2025",
        "Link: rel=deprecation",
    ]
    ys = [150, 198, 246]
    for i, s in enumerate(lb):
        p.append(fitbox(lx - 108, ys[i] - 18, 216, 36, s, size=11,
                        fill="#eaf0fd", stroke=NEG, sw=1.5, color=INK))
    # права колонка — люди
    rb = ["документація · changelog", "лист інтеграторам", "банер у дашборді"]
    for i, s in enumerate(rb):
        p.append(fitbox(rx - 108, ys[i] - 18, 216, 36, s, size=11,
                        fill="#eafaf0", stroke=FIELD, sw=1.5, color=INK))

    # підсумки
    p.append(arrow(lx, ys[2] + 18, lx, 296, color=NEG, sw=1.6))
    p.append(arrow(rx, ys[2] + 18, rx, 296, color=FIELD, sw=1.6))
    o1, ow1, oh1 = textbox(lx, 322, "моніторинг клієнта\nалертить сам",
                           size=11, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.6)
    p.append(o1)
    o2, ow2, oh2 = textbox(rx, 322, "розробник планує\nміграцію",
                           size=11, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.6)
    p.append(o2)

    p.append(text(390, 374, "контракт — коли сигнал доходить і до коду, і до людини",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "dual-channel.svg"), W, H, *p,
           title="Сигнал застарілості — двома каналами")


# ── usage-decay: зняття веде виміряне падіння, не календар ─────────────────────
# Ідея: після оголошення виклики застарілого маршрута спадають. Знімати безпечно
# біля нуля; знімати при високому трафіку — зламати живих; хвіст — добити особисто.
def fig_usage_decay():
    W, H = 780, 390
    p = []

    ox, oy = 95, 310            # початок осей
    tx, ty = 720, 70           # кінці осей
    p.append(arrow(ox, oy, tx, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, ty, color=INK, sw=1.6))
    p.append(text(ox + 60, 58, "виклики застарілого маршрута / день",
                  size=11, color=MUTED, anchor="start"))
    p.append(text(tx - 6, oy + 22, "час від оголошення →", size=11, color=MUTED, anchor="end"))

    # крива спаду
    pts = [(95, 100), (150, 150), (210, 196), (285, 235),
           (370, 262), (460, 280), (560, 293), (640, 300)]
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        p.append(line(x1, y1, x2, y2, color=NEG, sw=2.6))
    p.append(text(102, 92, "оголошення", size=10, color=MUTED, anchor="start"))

    # рано знімати — червоно
    ex, ey = 210, 196
    p.append(line(ex - 8, ey - 8, ex + 8, ey + 8, color=POS, sw=2.4))
    p.append(line(ex + 8, ey - 8, ex - 8, ey + 8, color=POS, sw=2.4))
    rb, rbw, rbh = textbox(175, 110, "рано:\nще залежать", size=11, bold=True,
                           color=POS, fill="#fdecea", stroke=POS, sw=1.6)
    p.append(rb)
    p.append(arrow(175, 110 + rbh / 2, ex - 6, ey - 6, color=POS, sw=1.4))

    # sunset — зелено, біля нуля
    sx = 600
    p.append(line(sx, oy, sx, 300, color=FIELD, sw=1.5, dash="4 4"))
    gb, gbw, gbh = textbox(632, 118, "Sunset:\nусе мігрувало", size=11, bold=True,
                           color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.6)
    p.append(gb)
    p.append(arrow(632, 118 + gbh / 2, sx, 294, color=FIELD, sw=1.4))

    # довгий хвіст — особисто
    tb, tbw, tbh = textbox(470, 228, "довгий хвіст —\nдостукатися особисто",
                           size=11, bold=True, color=MUTED, fill="#f3f4f6",
                           stroke=MUTED, sw=1.4)
    p.append(tb)
    p.append(arrow(470, 228 + tbh / 2, 545, 289, color=MUTED, sw=1.3))

    p.append(text(400, 366, "знімають за виміряним падінням, не лише за календарем",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "usage-decay.svg"), W, H, *p,
           title="Коли знімати: за кривою спаду викликів")


# ── retry-doublecount: ретрай без дедупу рахується двічі ──────────────────────
# Ідея: лічильник рахує ОТРИМАНІ запити, не логічні виклики. Загублена відповідь
# → клієнт повторює → сервер рахує двічі → крива спаду завищена. Idempotency-Key
# дає впізнати повтор і порахувати раз.
def fig_retry_doublecount():
    W, H = 840, 400
    p = []

    def panel(cy_c, cy_s, title, tcolor, msgs, verdict, vcolor):
        p.append(text(58, cy_c - 36, title, size=13, color=tcolor, bold=True, anchor="start"))
        cb, cw, ch = textbox(108, cy_c, "клієнт", size=12, bold=True,
                             fill="#f6f4ec", stroke=INK, sw=1.6, min_w=92)
        sb, sw2, sh = textbox(122, cy_s, "сервер · лічильник", size=12, bold=True,
                              fill="#fef7ec", stroke="#9a7d1f", sw=1.6)
        p.append(cb); p.append(sb)
        lx = 208
        p.append(line(lx, cy_c, 640, cy_c, color=MUTED, sw=1, dash="3 4"))
        p.append(line(lx, cy_s, 640, cy_s, color=MUTED, sw=1, dash="3 4"))
        mid = (cy_c + cy_s) / 2
        for (x, top, tally, color, lost) in msgs:
            if lost:
                p.append(line(x, cy_s, x, cy_c + 12, color=POS, sw=1.5, dash="4 4"))
                p.append(line(x - 7, mid - 7, x + 7, mid + 7, color=POS, sw=2.4))
                p.append(line(x + 7, mid - 7, x - 7, mid + 7, color=POS, sw=2.4))
                p.append(text(x, cy_c - 12, top, size=10, color=POS))
            else:
                p.append(arrow(x, cy_c + 8, x, cy_s - 8, color=color, sw=1.7))
                p.append(text(x, cy_c - 12, top, size=10, color=color, bold=True))
                p.append(text(x, cy_s + 21, tally, size=10, color=color, bold=True))
        vb, vw, vh = textbox(735, mid, verdict, size=11, bold=True,
                             color=vcolor, fill="#ffffff", stroke=vcolor, sw=1.8)
        p.append(vb)

    panel(92, 168, "без дедупу — ретрай рахується двічі", POS,
          [(280, "запит #1", "+1  (=1)", INK, False),
           (420, "відповідь загубилась", "", POS, True),
           (560, "ретрай — той самий", "+1  (=2)", POS, False)],
          "1 виклик →\nпораховано 2\nкрива завищена", POS)

    panel(288, 360, "з Idempotency-Key — повтор упізнано", FIELD,
          [(280, "запит · key=K", "+1  (=1)", INK, False),
           (420, "відповідь загубилась", "", POS, True),
           (560, "ретрай · key=K", "дедуп +0  (=1)", FIELD, False)],
          "1 виклик →\nпораховано 1\nкрива правдива", FIELD)

    render(os.path.join(OUT, "retry-doublecount.svg"), W, H, *p,
           title="Ретрай без дедупу рахується двічі")


# ── label-cardinality: кардинальність = добуток потужностей міток ─────────────
# Ідея: кожна комбінація значень міток — окремий часовий ряд. Обмежені мітки
# (route×client) дають десятки рядів; необмежені (path з id, api_key, UA) —
# мільйони, що кладуть систему метрик.
def fig_label_cardinality():
    W, H = 820, 410
    p = []

    def chip(cx, cy, name, card, color):
        b, w, h = textbox(cx, cy, "%s\n%s" % (name, card), size=11, bold=True,
                          fill="#ffffff", stroke=color, sw=1.6, color=INK, min_w=98)
        p.append(b)

    # панель А — обмежені мітки
    p.append(text(55, 66, "обмежені мітки — кардинальність під контролем",
                  size=13, color=FIELD, bold=True, anchor="start"))
    p.append(fitbox(55, 80, 470, 34, "deprecated_route_calls_total{route, client}",
                    size=12, fill="#eafaf0", stroke=FIELD, sw=1.5, color=INK))
    ay = 152
    chip(112, ay, "route", "3 значення", FIELD)
    p.append(text(206, ay + 6, "×", size=17, color=MUTED, bold=True))
    chip(300, ay, "client", "~20 назв", FIELD)
    p.append(text(408, ay + 6, "=", size=17, color=MUTED, bold=True))
    eb, ew, eh = textbox(505, ay, "≈ 60 рядів", size=13, bold=True,
                         color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(eb)
    p.append(text(600, ay + 5, "метрика спокійна", size=11, color=FIELD,
                  anchor="start", italic=True))

    # панель Б — необмежені мітки
    p.append(text(55, 250, "необмежені мітки — вибух кардинальності",
                  size=13, color=POS, bold=True, anchor="start"))
    p.append(fitbox(55, 264, 470, 34, "…{route, path, api_key, user_agent}",
                    size=12, fill="#fdecea", stroke=POS, sw=1.5, color=INK))
    by = 336
    chip(96, by, "route", "3", POS)
    p.append(text(166, by + 6, "×", size=15, color=MUTED, bold=True))
    chip(236, by, "path", "∞ (id)", POS)
    p.append(text(306, by + 6, "×", size=15, color=MUTED, bold=True))
    chip(376, by, "api_key", "∞", POS)
    p.append(text(452, by + 6, "×", size=15, color=MUTED, bold=True))
    chip(528, by, "user_agent", "тисячі", POS)
    p.append(text(626, by + 6, "=", size=17, color=MUTED, bold=True))
    xb, xw, xh = textbox(720, by, "мільйони\nрядів", size=13, bold=True,
                         color=POS, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(xb)

    p.append(text(410, 398, "ідентифікатори — у лог, не в мітку метрики",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "label-cardinality.svg"), W, H, *p,
           title="Кардинальність = добуток потужностей міток")


# ── machine-signal-timeline: десятирічна дуга машинного сигналу ────────────────
# Ідея: дві доріжки одного задуму. Угорі Sunset (чернетка 2015 → RFC 8594, 2019,
# HTTP-date); унизу Deprecation (чернетка 2019 → RFC 9745, 2025, @unix). Вони
# перетинаються ~2019 (естафета). Посередині — поява типу Date у структурованих
# полях (RFC 8941 без нього 2021 → RFC 9651 з ним 2024), що й уможливила @unix.
def fig_machine_signal_timeline():
    W, H = 980, 500
    p = []

    DARKGREEN = "#1d7a44"
    DARKAMBER = "#9a7d1f"

    def X(yf):                      # рік (дробовий) → x
        return 95 + (yf - 2015) * 74

    y_top, y_mid, y_bot = 130, 258, 382

    # ── вісь років унизу ──
    ax = 462
    p.append(line(95, ax, 862, ax, color=MUTED, sw=1.2))
    for yr in (2015, 2017, 2019, 2021, 2023, 2025):
        xt = X(yr)
        p.append(line(xt, ax - 5, xt, ax + 5, color=MUTED, sw=1.2))
        p.append(text(xt, ax + 20, str(yr), size=11, color=MUTED))

    # ── естафета 2019: вертикальний пунктир між доріжками ──
    xh = (X(2019.16) + X(2019.37)) / 2
    p.append(line(xh, y_top - 4, xh, y_bot + 4, color=MUTED, sw=1.1, dash="4 5"))
    p.append(text(xh, y_top - 30, "2019 — естафета", size=11, color=MUTED, bold=True))

    # ── ВЕРХНЯ доріжка: Sunset ──
    xs, xe = X(2015.58), X(2019.37)
    p.append(rect(xs, y_top - 6, xe - xs, 12, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6))
    p.append(circle(xs, y_top, 5, fill=FIELD, stroke=FIELD, sw=1.5))
    p.append(circle(xe, y_top, 5, fill=FIELD, stroke=FIELD, sw=1.5))
    # підписи вузлів — згори
    b1, w1, h1 = textbox(xs, 74, "чернетка Sunset\nВільде · серп. 2015",
                         size=11, bold=True, fill="#f6faf7", stroke=FIELD, sw=1.5)
    p.append(b1)
    p.append(line(xs, 74 + h1 / 2, xs, y_top - 6, color=FIELD, sw=1.2))
    b2, w2, h2 = textbox(xe, 74, "RFC 8594 · трав. 2019\nInformational",
                         size=11, bold=True, fill="#f6faf7", stroke=FIELD, sw=1.5)
    p.append(b2)
    p.append(line(xe, 74 + h2 / 2, xe, y_top - 6, color=FIELD, sw=1.2))
    # формат — під смугою
    p.append(text((xs + xe) / 2, y_top + 26, "формат: HTTP-date — людночитний",
                  size=11, color=DARKGREEN, bold=True))

    # ── СЕРЕДНЯ доріжка: тип Date у структурованих полях ──
    x41, x51 = X(2021.12), X(2024.70)
    p.append(circle(x41, y_mid, 5, fill=MUTED, stroke=MUTED, sw=1.5))
    p.append(circle(x51, y_mid, 5, fill=NEG, stroke=NEG, sw=1.5))
    m1, mw1, mh1 = textbox(x41, y_mid + 34, "RFC 8941 · лют. 2021\nструктуровані поля —\nбез типу Date",
                           size=11, bold=True, fill="#f3f4f6", stroke=MUTED, sw=1.4)
    p.append(m1)
    p.append(line(x41, y_mid + 6, x41, y_mid + 34 - mh1 / 2, color=MUTED, sw=1.2))
    m2, mw2, mh2 = textbox(x51, y_mid - 30, "RFC 9651 · вер. 2024\nтип Date з'явився",
                           size=11, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.5)
    p.append(m2)
    p.append(line(x51, y_mid - 30 + mh2 / 2, x51, y_mid - 6, color=NEG, sw=1.2))
    # стрілка «тип Date уможливив @unix» — від 9651 вниз до нижньої смуги
    p.append(arrow(x51, y_mid + 6, x51, y_bot - 8, color=NEG, sw=1.6))
    p.append(text(x51 + 12, (y_mid + y_bot) / 2, "тип Date\nуможливив @unix",
                  size=10, color=NEG, anchor="start"))

    # ── НИЖНЯ доріжка: Deprecation ──
    xd, xr = X(2019.16), X(2025.21)
    p.append(rect(xd, y_bot - 6, xr - xd, 12, fill="#fbf3da", stroke=AMBER, sw=1.8, rx=6))
    p.append(circle(xd, y_bot, 5, fill=AMBER, stroke=AMBER, sw=1.5))
    p.append(circle(xr, y_bot, 5, fill=AMBER, stroke=AMBER, sw=1.5))
    # формат — над смугою
    p.append(text((xd + xr) / 2, y_bot - 16, "формат: @unix — машинний (Structured Field Date)",
                  size=11, color=DARKAMBER, bold=True))
    # підписи вузлів — знизу
    d1, dw1, dh1 = textbox(xd, 430, "чернетка Deprecation\nДалал · лют. 2019",
                           size=11, bold=True, fill="#fdf8ea", stroke=AMBER, sw=1.5)
    p.append(d1)
    p.append(line(xd, y_bot + 6, xd, 430 - dh1 / 2, color=AMBER, sw=1.2))
    d2, dw2, dh2 = textbox(xr - 20, 430, "RFC 9745 · бер. 2025\nStandards Track",
                           size=11, bold=True, fill="#fdf8ea", stroke=AMBER, sw=1.5)
    p.append(d2)
    p.append(line(xr, y_bot + 6, xr - 20, 430 - dh2 / 2, color=AMBER, sw=1.2))

    p.append(text(W / 2, 490, "Ерік Вільде — співавтор обох доріжок: та сама рука пронесла ідею крізь десятиліття",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "machine-signal-timeline.svg"), W, H, *p,
           title="Десятиліття машинного сигналу застарілості")


# ── date-format-eras: два заголовки — дві доби формату ─────────────────────────
# Ідея: обидва несуть той самий різновид — мить у часі, — але записані двома
# діалектами. Sunset говорить старою людночитною HTTP-date (доба до структурованих
# полів); Deprecation — новою машинною @-міткою (тип Date, що з'явився лише 2024).
def fig_date_format_eras():
    W, H = 900, 360
    p = []

    DARKAMBER = "#9a7d1f"

    p.append(text(W / 2, 54, "той самий різновид — мить у часі — записаний двома різними діалектами",
                  size=12, color=MUTED, italic=True))

    # ── панель А: Sunset (стара доба) ──
    p.append(fitbox(55, 88, 470, 54, "Sunset: Wed, 31 Dec 2025 23:59:59 GMT",
                    size=15, fill="#eafaf0", stroke=FIELD, sw=1.8, color=INK, bold=True))
    ea, ewa, eha = textbox(710, 115, "людночитна HTTP-date\nдоба RFC 7231 · до структурованих полів\nформат заморожено 2019",
                           size=11, bold=True, fill="#f6faf7", stroke=FIELD, sw=1.5)
    p.append(ea)

    # ── панель Б: Deprecation (нова доба) ──
    p.append(fitbox(55, 196, 470, 54, "Deprecation: @1719705599",
                    size=15, fill="#fbf3da", stroke=AMBER, sw=1.8, color=INK, bold=True))
    eb, ewb, ehb = textbox(710, 223, "машинна @-мітка — Unix-секунди\nStructured Field Date · RFC 9651\nтип Date з'явився лише 2024",
                           size=11, bold=True, fill="#fef7ec", stroke=DARKAMBER, sw=1.5)
    p.append(eb)

    p.append(text(W / 2, 322, "формат кожного заголовка — скам'янілість доби, у яку його заморозили",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "date-format-eras.svg"), W, H, *p,
           title="Два заголовки — дві доби формату дати")


if __name__ == "__main__":
    fig_lifecycle()
    fig_dual_channel()
    fig_usage_decay()
    fig_retry_doublecount()
    fig_label_cardinality()
    fig_machine_signal_timeline()
    fig_date_format_eras()
    print("OK: figures written to", OUT)
