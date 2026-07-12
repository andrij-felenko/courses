# -*- coding: utf-8 -*-
"""Фігури до кроку «Фоновий вузол DH: де годинник зустрічає чергу»."""
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


def fig_background_node():
    """Три різні тригери входять одними дверима — в одну спільну машину черги й робітників."""
    W, H = 1240, 640
    frags = []

    # ── колонки ──
    XT = 175          # тригери (ліворуч)
    XQ = 560          # черга/робітники (центр)
    XR = 1000         # результати (праворуч)
    YS = [130, 250, 370]   # три рівні: годинник / подія / людина

    frags.append(text(XT, 78, "ТРИ ТРИГЕРИ", size=13.5, bold=True, color=MUTED))
    frags.append(text(XQ, 78, "ОДНА МАШИНА", size=13.5, bold=True, color=INK))
    frags.append(text(XR, 78, "ТРИ РЕЗУЛЬТАТИ", size=13.5, bold=True, color=MUTED))

    # ── тригери ──
    trigs = [
        ("ГОДИННИК", "cron-тік «02:00»", AMBER_FILL, AMBER),
        ("ПОДІЯ", "датчик «відчинено»", BLUE_FILL, NEG),
        ("ЛЮДИНА", "дотик «зроби кліп»", GREEN_FILL, FIELD),
    ]
    tboxes = []
    for (head, sub, fill, col), y in zip(trigs, YS):
        b, w, h = textbox(XT, y, head + "\n" + sub, size=13, bold=True,
                          fill=fill, stroke=col, sw=2, color=col, min_w=210)
        tboxes.append((b, w, h, y))
        frags.append(b)

    # ── центр: черга + робітники ──
    qb, qw, qh = textbox(XQ, 190, "ЧЕРГА ЗАДАЧ\nзадача = запис (аргументи, стан, спроби)",
                         size=13, bold=True, fill=GRAY_FILL, stroke=INK, sw=2.4,
                         color=INK, min_w=330)
    wb, ww, wh = textbox(XQ, 330, "РОБІТНИКИ\nокремі пули на класи роботи",
                         size=13, bold=True, fill=BLUE_FILL, stroke=NEG, sw=2.2,
                         color=INK, min_w=330)

    # тригери → черга (три стрілки, що сходяться в лівий бік черги)
    qx_left = XQ - qw / 2
    for _, w, h, y in tboxes:
        frags.append(arrow(XT + w / 2 + 8, y, qx_left - 8, 190, color=MUTED, sw=1.8))

    # черга → робітники
    frags.append(arrow(XQ, 190 + qh / 2 + 4, XQ, 330 - wh / 2 - 4, color=INK, sw=2))
    frags.append(qb)
    frags.append(wb)

    # ── результати ──
    res = [
        ("денний підсумок\nтелеметрії", GRAY_FILL, MUTED),
        ("пуш на телефон\nвласника", GRAY_FILL, MUTED),
        ("готовий кліп\nіз камери", GRAY_FILL, MUTED),
    ]
    wx_right = XQ + ww / 2
    for (label, fill, col), y in zip(res, YS):
        rb, rw, rh = textbox(XR, y, label, size=12.5, bold=True,
                            fill=fill, stroke=col, sw=1.6, color=INK, min_w=200)
        frags.append(arrow(wx_right + 8, 330, XR - rw / 2 - 8, y, color=MUTED, sw=1.8))
        frags.append(rb)

    # ── нижня смуга: спільний контракт вузла ──
    by = 500
    frags.append(rect(90, by, W - 180, 96, fill="#f7f9fb", stroke=FIELD, sw=2, rx=10))
    frags.append(text(W / 2, by + 30, "СПІЛЬНИЙ КОНТРАКТ ВУЗЛА — під усіма трьома роботами однаково",
                      size=14, bold=True, color=FIELD))
    parts = ["ідемпотентність", "чесний статус", "оренда + серцебиття", "тлінний строк життя"]
    n = len(parts)
    for i, p in enumerate(parts):
        cx = 90 + (W - 180) * (i + 0.5) / n
        frags.append(text(cx, by + 66, p, size=13, bold=True, color=INK))
        if i:
            xdiv = 90 + (W - 180) * i / n
            frags.append(line(xdiv, by + 46, xdiv, by + 82, color=MUTED, sw=1, dash="3,4"))

    render(os.path.join(IMG, "background-node.svg"), W, H, *frags,
           title="Фоновий вузол DH: троє дверей, одна кімната")


def _hatch(x, y, w, h, fill, stroke, color, label):
    out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=4)]
    # безпечна смуга посередині — без штрихування, щоб лінії не різали напис
    label_w = len(label) * 12 * 0.54 + 14
    cx = x + w / 2
    safe_l, safe_r = cx - label_w / 2, cx + label_w / 2
    step = 12
    xx = x + step
    while xx < x + w:
        x2 = max(x + 2, xx - h + 4)
        seg_l, seg_r = min(xx, x2), max(xx, x2)
        if seg_r < safe_l or seg_l > safe_r:
            out.append(line(xx, y + 2, x2, y + h - 2, color=stroke, sw=0.8))
        xx += step
    out.append(text(x + w / 2, y + h / 2 + 5, label, size=12, bold=True, color=color))
    return out


def fig_dst_seam():
    """Настінний годинник — не рівна вісь: навесні дірка, восени складка; доба ≠ 24 год."""
    W, H = 1240, 600
    frags = []

    X0 = 150
    HR = 148          # пікселів на годину
    def hx(h):        # h — годин від 01:00
        return X0 + h * HR

    AX_END = hx(4) + 40

    # ─────────── ВЕСНА (верхня половина) ───────────
    AXS = 190         # вісь весни
    frags.append(text(X0 - 40, 74, "ВЕСНА — переведення вперед", size=15, bold=True,
                      color=POS, anchor="start"))
    # cron-анотація й стрілка згори в дірку (добре відділені від заголовка)
    frags.append(text(hx(1.5), 112, "cron чекає на 02:00 → момент не настає", size=12,
                      bold=True, color=POS))
    frags.append(arrow(hx(1.5), 126, hx(1.5), AXS - 24, color=POS, sw=2))
    # вісь — з розривом рівно там, де година «не існує» (дірка на осі, не лише в штрихуванні)
    frags.append(line(X0, AXS, hx(1), AXS, color=INK, sw=1.6))
    frags.append(line(hx(2), AXS, AX_END, AXS, color=INK, sw=1.6))
    for h, lbl in [(0, "01:00"), (0.98, "01:59")]:
        frags.append(line(hx(h), AXS - 6, hx(h), AXS + 6, color=INK, sw=1.4))
        frags.append(text(hx(h), AXS + 28, lbl, size=12, color=INK))
    # дірка на місці 02:xx (між hx(1) і hx(2)), straddling вісь
    frags += _hatch(hx(1), AXS - 22, hx(2) - hx(1), 44, RED_FILL, POS, POS, "02:00 — НЕ існує")
    for h, lbl in [(2, "03:00"), (3, "04:00")]:
        frags.append(line(hx(h), AXS - 6, hx(h), AXS + 6, color=INK, sw=1.4))
        frags.append(text(hx(h), AXS + 28, lbl, size=12, color=INK))
    frags.append(text(hx(1.5), AXS + 54, "→ нічна агрегація НЕ запускається, графік із діркою",
                      size=12, color=MUTED))
    b, _, _ = textbox(hx(4) + 155, AXS, "локальна доба\n= 23 години", size=12.5, bold=True,
                      fill=RED_FILL, stroke=POS, color=POS, min_w=150)
    frags.append(b)

    # роздільник
    frags.append(line(70, 300, W - 70, 300, color=MUTED, sw=1.1, dash="7,7"))

    # ─────────── ОСІНЬ (нижня половина) ───────────
    AXF = 458         # вісь осені
    frags.append(text(X0 - 40, 344, "ОСІНЬ — переведення назад", size=15, bold=True,
                      color=NEG, anchor="start"))
    frags.append(text(hx(1.5), 382, "cron бачить 02:00 ДВІЧІ → запуск двічі → подвоєння",
                      size=12, bold=True, color=NEG))
    # дві cron-стрілки згори — обидві в 02:00
    frags.append(arrow(hx(1), 396, hx(1), AXF - 22, color=NEG, sw=2))
    frags.append(arrow(hx(2), 396, hx(2), AXF - 22, color=NEG, sw=2))
    # вісь
    frags.append(line(X0, AXF, AX_END, AXF, color=INK, sw=1.6))
    frags.append(line(hx(0), AXF - 6, hx(0), AXF + 6, color=INK, sw=1.4))
    frags.append(text(hx(0), AXF + 28, "01:00", size=12, color=INK))
    for h in (1, 2):
        frags.append(line(hx(h), AXF - 8, hx(h), AXF + 8, color=POS, sw=2.4))
        frags.append(text(hx(h), AXF + 29, "02:00", size=12.5, bold=True, color=POS))
    frags.append(line(hx(3), AXF - 6, hx(3), AXF + 6, color=INK, sw=1.4))
    frags.append(text(hx(3), AXF + 28, "03:00", size=12, color=INK))
    frags.append(text(hx(1.5), AXF + 54, "↩ переведено назад — та сама година знову",
                      size=12, bold=True, color=NEG))
    b2, _, _ = textbox(hx(4) + 155, AXF, "локальна доба\n= 25 годин", size=12.5, bold=True,
                       fill=BLUE_FILL, stroke=NEG, color=NEG, min_w=150)
    frags.append(b2)

    # ─────────── виноска-ліки ───────────
    fb, fw, fh = textbox(W / 2, 560,
                         "Ліки: вікно «вчора» = від локальної півночі до локальної півночі "
                         "(само дає 23/24/25 год), а не «зараз − 24 год»",
                         size=12.5, bold=True, fill=GREEN_FILL, stroke=FIELD, color=FIELD,
                         min_w=760)
    frags.append(fb)

    render(os.path.join(IMG, "dst-seam.svg"), W, H, *frags,
           title="Де годинник стає тригером: навесні дірка, восени складка")


def fig_three_nets():
    """Три сітки, що страхують «один запуск на кластер»: ліза · фенсинг · ключ (дім,доба)."""
    W, H = 1320, 700
    frags = []
    cols = [
        (240, "СІТКА 1 · ЛІЗА",
         "Двоє вузлів прокинулись\nо 02:00 — обидва хочуть\nпланувати ніч",
         "Лізу (право планувати)\nатомарно бере ЛИШЕ один.\nДругий бачить живу лізу\nй мовчить до її кінця",
         "рівно ОДИН планувальник\nна весь кластер", AMBER_FILL, AMBER, BLUE_FILL, NEG),
        (660, "СІТКА 2 · ФЕНСИНГ-ТОКЕН",
         "Власник ліг у GC-паузу,\nліза згасла, поки він спав, —\nа тоді ожив і пише",
         "Наступник узяв лізу з\nтокеном 34. Зомбі пише з\nтокеном 33 → сховище бачить\n33 < 34 і ВІДМОВЛЯЄ",
         "застарілий запис відкинуто,\nвказівник не зіпсовано", RED_FILL, POS, BLUE_FILL, NEG),
        (1080, "СІТКА 3 · КЛЮЧ (дім, доба)",
         "Черга «щонайменше раз»\nдоставила ту саму задачу\nагрегації двічі",
         "upsert за ключем (дім, доба):\nдругий запуск ПЕРЕПИШЕ\nтой самий рядок тими\nсамими числами",
         "той самий підсумок,\nбез подвоєння", GRAY_FILL, MUTED, GREEN_FILL, FIELD),
    ]
    for (cx, head, fail, net, out, ff, fc, nf, nc) in cols:
        frags.append(text(cx, 66, head, size=14, bold=True, color=INK))
        fb, fw, fh = textbox(cx, 152, fail, size=12.5, fill=ff, stroke=fc, sw=1.8,
                             color=INK, min_w=346)
        nb, nw, nh = textbox(cx, 352, net, size=12.5, fill=nf, stroke=nc, sw=2,
                             color=INK, min_w=356)
        ob, ow, oh = textbox(cx, 548, out, size=12.5, bold=True, fill=GREEN_FILL,
                             stroke=FIELD, sw=1.8, color=INK, min_w=326)
        frags.append(arrow(cx, 152 + fh / 2 + 4, cx, 352 - nh / 2 - 4, color=MUTED, sw=1.8))
        frags.append(arrow(cx, 352 + nh / 2 + 4, cx, 548 - oh / 2 - 4, color=FIELD, sw=1.9))
        frags += [fb, nb, ob]
    by = 622
    frags.append(rect(80, by, W - 160, 62, fill="#f7f9fb", stroke=FIELD, sw=2, rx=10))
    frags.append(text(W / 2, by + 25,
                      "Три сітки ПЕРЕКРИВАЮТЬСЯ — ніч стоїть на всіх трьох разом, не на одній",
                      size=13.5, bold=True, color=FIELD))
    frags.append(text(W / 2, by + 47,
                      "ліза ловить буденний випадок · фенсинг — зомбі після паузи · ключ — дубль від ретраю",
                      size=12, color=INK))
    render(os.path.join(IMG, "three-nets.svg"), W, H, *frags,
           title="Один нічний запуск на кластер: три сітки, що страхують одна одну")


def fig_catchup_mark():
    """High-water mark веде наздоганяння: провал у 3 доби (одна з них 23-годинна)."""
    W, H = 1280, 600
    frags = []
    X0, CW, YA = 120, 210, 178
    cells = [
        ("27 бер", "24 год", "✓ згорнуто", GREEN_FILL, FIELD),
        ("28 бер", "24 год", "пропущено", AMBER_FILL, AMBER),
        ("29 бер", "23 год", "весна · пропущено", RED_FILL, POS),
        ("30 бер", "24 год", "пропущено", AMBER_FILL, AMBER),
        ("31 бер", "—", "СЬОГОДНІ", GRAY_FILL, MUTED),
    ]
    cxs = []
    for i, (d, hh, st, fill, col) in enumerate(cells):
        cx = X0 + CW * i + CW / 2
        cxs.append(cx)
        b, _, _ = textbox(cx, YA, d + "\n" + hh + "\n" + st, size=12.5, bold=True,
                          fill=fill, stroke=col, sw=1.9, color=INK, min_w=CW - 22)
        frags.append(b)

    # дужка «кластер лежав» над клітинами 28..30
    lb, rb = X0 + CW * 1, X0 + CW * 4
    yb = 104
    frags.append(line(lb, yb, rb, yb, color=NEG, sw=2))
    frags.append(line(lb, yb, lb, yb + 16, color=NEG, sw=2))
    frags.append(line(rb, yb, rb, yb + 16, color=NEG, sw=2))
    frags.append(text((lb + rb) / 2, yb - 10, "кластер лежав — 3 доби пропущено",
                      size=13, bold=True, color=NEG))

    # mark повзе 27 → 30 (стрілка під віссю)
    ym = 268
    frags.append(text(cxs[0], ym - 14, "◀ mark був тут (27)", size=12, bold=True, color=FIELD))
    frags.append(arrow(cxs[0], ym + 6, cxs[3], ym + 6, color=FIELD, sw=2.2))
    frags.append(text((cxs[0] + cxs[3]) / 2, ym + 28,
                      "catch-up: enumerator видав [28, 29, 30] · mark повзе 27→28→29→30",
                      size=12.5, bold=True, color=FIELD))

    frags.append(line(80, 340, W - 80, 340, color=MUTED, sw=1.1, dash="7,7"))

    # наївна контр-доріжка
    frags.append(text(W / 2, 372,
                      "А наївне «вчора = сьогодні − 1» бачить лише одну добу — рештa провалу зникає:",
                      size=13, bold=True, color=POS))
    naive = [(cxs[1], "28 ✗ втрачено", RED_FILL, POS),
             (cxs[2], "29 ✗ втрачено", RED_FILL, POS),
             (cxs[3], "30 ✓ згорнуто", GREEN_FILL, FIELD)]
    for cx, lbl, fill, col in naive:
        b, _, _ = textbox(cx, 442, lbl, size=12.5, bold=True, fill=fill, stroke=col,
                          sw=1.8, color=INK, min_w=CW - 30)
        frags.append(b)
    frags.append(text(W / 2, 512,
                      "Наздоганяння — не окрема функція, а відсутність бага: воно випадає з "
                      "формули (mark, сьогодні, політика).",
                      size=12.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "catchup-mark.svg"), W, H, *frags,
           title="High-water mark веде наздоганяння через переведення стрілок")


def fig_miss_policies():
    """Три політики пропущеного запуску на провалі 28–30: skip · catch-up · coalesce."""
    W, H = 1300, 560
    frags = []
    X0, CW, YS = 350, 175, [140, 300, 460]
    cxs = [X0 + CW * i + CW / 2 for i in range(3)]  # 28, 29, 30

    frags.append(text(cxs[1], 66, "провал: доби 28 · 29 · 30 пропущено", size=13.5,
                      bold=True, color=INK))

    lanes = [
        ("SKIP", "Quartz DO_NOTHING", [
            ("28 ✗", RED_FILL, POS), ("29 ✗", RED_FILL, POS), ("30 ✓", GREEN_FILL, FIELD)],
         "лише найсвіжіша доба; 28–29\nлишаються порожні назавжди"),
        ("CATCH-UP", "Quartz ignore-misfire", [
            ("28 ✓", GREEN_FILL, FIELD), ("29 ✓", GREEN_FILL, FIELD), ("30 ✓", GREEN_FILL, FIELD)],
         "кожна доба — свій рядок\nза ключем (дім, доба)"),
    ]
    for (name, sub, cells, note), y in zip(lanes, YS):
        lb, _, _ = textbox(170, y, name + "\n" + sub, size=12.5, bold=True,
                           fill=GRAY_FILL, stroke=INK, sw=1.7, color=INK, min_w=210)
        frags.append(lb)
        for cx, (lbl, fill, col) in zip(cxs, cells):
            b, _, _ = textbox(cx, y, lbl, size=13, bold=True, fill=fill, stroke=col,
                              sw=1.8, color=INK, min_w=CW - 28)
            frags.append(b)
        frags.append(text(1010, y, note.split("\n")[0], size=12, color=INK, anchor="start"))
        frags.append(text(1010, y + 16, note.split("\n")[1], size=12, color=INK, anchor="start"))

    # COALESCE — один широкий блок
    y = YS[2]
    lb, _, _ = textbox(170, y, "COALESCE\nQuartz FIRE_NOW", size=12.5, bold=True,
                       fill=GRAY_FILL, stroke=INK, sw=1.7, color=INK, min_w=210)
    frags.append(lb)
    wide_l, wide_r = X0, X0 + CW * 3
    frags.append(rect(wide_l, y - 26, wide_r - wide_l, 52, fill=AMBER_FILL, stroke=AMBER,
                      sw=2, rx=6))
    frags.append(text((wide_l + wide_r) / 2, y + 5, "28–30 злиті в ОДНЕ вікно",
                      size=13, bold=True, color=AMBER))
    frags.append(text(1010, y, "⚠ ключ (дім, доба) НЕ тримає", size=12, bold=True,
                      color=POS, anchor="start"))
    frags.append(text(1010, y + 16, "діапазон — тільки для recompute", size=12, color=INK,
                      anchor="start"))

    by = 520
    frags.append(text(W / 2, by,
                      "Політику обираєш свідомо: skip дешевий і втрачає · catch-up точний і "
                      "дорогий · coalesce — лише де підсумок за діапазон має сенс",
                      size=12.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "miss-policies.svg"), W, H, *frags,
           title="Три відповіді на пропущений запуск: skip · catch-up · coalesce")


def fig_time_catches():
    """Ті самі граблі DST-часу на трьох масштабах: кишеня → світ → сервер."""
    W, H = 1260, 600
    frags = []

    X0, X1 = 330, 1200          # смуга чипів
    def chips(y, items, fill, stroke):
        n = len(items)
        for i, c in enumerate(items):
            cx = X0 + (X1 - X0) * (i + 0.5) / n
            b, _, _ = textbox(cx, y, c, size=12.5, bold=True,
                              fill=fill, stroke=stroke, sw=1.6, color=INK, min_w=0)
            frags.append(b)

    rows = [
        (122, "У КИШЕНІ\nбудильник iOS", AMBER_FILL, AMBER,
         ["Австралія 2010", "США · лист. 2010", "Новий рік 2011", "США · бер. 2011"],
         "щоразу на стрибку годинника (а Новий рік — на зміні дати)"),
        (286, "У СВІТІ\nдоба і держава", BLUE_FILL, NEG,
         ["Самоа 2011: доба зникла", "Росія 2014: постійний стандарт", "Бразилія 2019: без DST"],
         "локальні правила міняють згори — код про це не питали"),
        (450, "НА СЕРВЕРІ\ncron", RED_FILL, POS,
         ["навесні: 02:xx пропущено", "восени: 02:xx двічі", "різні cron — різна латка"],
         "той самий шов, рік за роком"),
    ]
    for y, label, fill, stroke, items, sub in rows:
        lb, _, _ = textbox(190, y, label, size=13, bold=True,
                           fill=fill, stroke=stroke, sw=2, color=INK, min_w=176)
        frags.append(lb)
        chips(y, items, fill, stroke)
        frags.append(text((X0 + X1) / 2, y + 52, sub, size=12, italic=True, color=MUTED))

    tb, _, _ = textbox(W / 2, 548,
                       "Один клас — рекурентний ЛОКАЛЬНИЙ час. UTC точно ловить минулу мить, "
                       "але не майбутній намір «о 02:00».",
                       size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2,
                       color=FIELD, min_w=940)
    frags.append(tb)

    render(os.path.join(IMG, "time-catches.svg"), W, H, *frags,
           title="Годинник ловить кожного: у кишені, у світі, на сервері")


if __name__ == "__main__":
    fig_background_node()
    fig_dst_seam()
    fig_three_nets()
    fig_catchup_mark()
    fig_miss_policies()
    fig_time_catches()
    print("OK: background-node, dst-seam, three-nets, catchup-mark, miss-policies, time-catches")
