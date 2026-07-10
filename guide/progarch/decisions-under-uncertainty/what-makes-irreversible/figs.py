# -*- coding: utf-8 -*-
"""Фігури до кроку «Що робить рішення незворотним» (guide/progarch)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")


def fig_decay():
    """Спад зворотності: те саме рішення дешеве на день 1 і руйнівне на рік 2."""
    W, H = 760, 430
    x0, y_ax = 92, 352          # початок осей
    parts = []

    # осі
    parts.append(arrow(x0, y_ax, 726, y_ax))         # X →
    parts.append(arrow(x0, y_ax, x0, 58))            # Y ↑
    parts.append(text(96, 50, "вартість відкату", size=12, color=MUTED, anchor="start"))
    parts.append(text(720, 343, "час · обсяг накопиченого →", size=12, color=MUTED, anchor="end"))

    # крива-спад (пласка → крута): відкат довго дешевий, тоді різко дорожчає
    pts = [(100, 348), (270, 336), (430, 300), (545, 222), (662, 92)]
    poly = " ".join("%.0f,%.0f" % p for p in pts)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, NEG))

    # день 1 — двобічні двері (зелене), горішній лівий кут, з виноскою до низу кривої
    parts.append(line(196, 150, 118, 340, color=MUTED, sw=1))
    b, w, h = textbox(196, 118, "день 1: порожньо\nвідкат — години\n(двобічні двері)",
                      size=12, color=FIELD, stroke=FIELD, fill="#eafaf0", pad=9)
    parts.append(b)

    # рік 2 — однобічні двері (червоне), над пласкою частиною кривої, виноска до вершини
    parts.append(line(452, 150, 648, 104, color=MUTED, sw=1))
    b, w, h = textbox(392, 128, "рік 2: 8 ТБ, 30 сервісів\nвідкат — місяці\n(однобічні двері)",
                      size=12, color=POS, stroke=POS, fill="#fdecea", pad=9)
    parts.append(b)

    # маркер останнього відповідального моменту — на «коліні» перед крутим підйомом
    parts.append(line(548, 214, 548, y_ax, color=INK, sw=1.4, dash="5 4"))
    parts.append(text(548, 384, "останній відповідальний момент", size=12, color=INK, bold=True))
    parts.append(text(548, 402, "далі двері швидко зачиняються", size=11, color=MUTED))

    render(os.path.join(IMG, "decay.svg"), W, H, *parts,
           title="Зворотність — не мітка, а показник, що спадає з часом")


def fig_reach():
    """Кільця досяжності: що далі від твоєї одноосібної влади — то важче відкотити."""
    W, H = 760, 500
    cx = 384
    parts = []

    # стрілка «важче» ліворуч
    parts.append(arrow(40, 432, 40, 66))
    parts.append(text(40, 56, "важче", size=11, color=MUTED))

    # вкладені рамки: спільний низ, дедалі вищий верх — підписи стають ярусами
    rings = [
        # (top, width, label, fill, stroke, color, label_y, bold)
        (60, 660, "розгорнуте у світ, видалене — вороття вже нема",
         "#fdecea", POS, POS, 82, True),
        (104, 548, "публічні контракти — вже поза твоєю владою",
         "#fef3e2", "#d98324", "#a8631a", 126, False),
        (148, 442, "інші команди — потрібне узгодження, не коміт",
         "#fbf6e0", "#b8a51e", "#8a7b12", 170, False),
        (192, 338, "накопичені дані — тяжіння, жива міграція",
         "#eef2fb", NEG, NEG, 214, False),
    ]
    bottom = 436
    for top, wd, label, fill, stroke, color, ly, bold in rings:
        parts.append(rect(cx - wd / 2, top, wd, bottom - top, fill=fill, stroke=stroke, sw=1.8, rx=10))
        parts.append(text(cx, ly, label, size=13, color=color, bold=bold))

    # осереддя — твій код (найдешевше)
    b, w, h = textbox(cx, 348, "твій код\n(рефактор)", size=13, color=FIELD,
                      stroke=FIELD, fill="#eafaf0", pad=11, bold=True)
    parts.append(b)

    parts.append(text(cx, 470,
                      "від осереддя назовні: більше накопичено й далі від одноосібної влади — дорожчий відкат",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "reach.svg"), W, H, *parts,
           title="Незворотність = наскільки далеко сягнуло рішення")


def fig_ratchet():
    """Одні однобічні двері даних → п'ять кроків, кожен (крім останнього) зі своїм відкатом."""
    W, H = 980, 372
    parts = []

    n = 5
    bx0, bw, step = 40, 166, 184
    by, bh = 118, 94
    xs = [bx0 + i * step for i in range(n)]

    phases = [
        ("1 · expand", "додати колонку\nпоруч зі старою", FIELD),
        ("2 · подвійний запис", "писати і в старе,\nі в нове", FIELD),
        ("3 · переливання", "історію — порціями,\nз тротлінгом", FIELD),
        ("4 · перемкнути читачів", "після звірки —\nчитати з нового", FIELD),
        ("5 · contract", "прибрати старе", POS),
    ]
    rollbacks = [
        "відкат:\nDROP порожньої\nколонки",
        "відкат:\nне писати\nв нове",
        "відкат:\nспинити\nбекфіл",
        "відкат:\nтумблер назад\nна старе",
    ]

    # фазові рамки + стрілки між ними
    for i, (head, body, col) in enumerate(phases):
        x = xs[i]
        fill = "#eafaf0" if col is FIELD else "#fdecea"
        parts.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=1.8, rx=9))
        parts.append(text(x + bw / 2, by + 26, head, size=13, color=col, bold=True))
        parts.append(mtext(x + bw / 2, by + 50, body, size=12, color=INK))
        if i < n - 1:
            parts.append(arrow(x + bw + 3, by + bh / 2, xs[i + 1] - 3, by + bh / 2))

    # відкати під фазами 1-4 (зелені) — стрілка від фази вниз до свого відкату
    ry = 300
    for i in range(4):
        cx = xs[i] + bw / 2
        b, w, h = textbox(cx, ry, rollbacks[i], size=11, color=FIELD,
                          stroke=FIELD, fill="#eafaf0", pad=8)
        parts.append(arrow(cx, by + bh + 4, cx, ry - h / 2 - 3, color=FIELD, sw=1.4))
        parts.append(b)

    # під фазою 5 — червоний глухий кут
    cx5 = xs[4] + bw / 2
    b, w, h = textbox(cx5, ry, "назад\nдороги нема", size=12, color=POS,
                      stroke=POS, fill="#fdecea", pad=9, bold=True)
    parts.append(b)

    # гейт звірки — вертикальна пунктирна межа між фазами 3 і 4
    gx = (xs[2] + bw + xs[3]) / 2
    parts.append(line(gx, by - 30, gx, by + bh + 28, color=INK, sw=1.5, dash="5 4"))
    b, w, h = textbox(gx, by - 48, "гейт звірки: нове не вмикається, поки не збіглося",
                      size=11, color=INK, fill=FILL, stroke=INK, pad=7)
    parts.append(b)

    render(os.path.join(IMG, "ratchet.svg"), W, H, *parts,
           title="Одні однобічні двері даних → п'ять двобічних")


def fig_timeline():
    """Дві колонки в часі: старе й нове співіснують, поки не звірили; відкат є до contract."""
    W, H = 980, 300
    parts = []

    n = 5
    cx0, cw, step = 84, 172, 178
    xs = [cx0 + i * step for i in range(n)]
    heads = ["1 · expand", "2 · dual-write", "3 · backfill",
             "4 · звірка + switch", "5 · contract"]

    for i, hd in enumerate(heads):
        parts.append(text(xs[i] + cw / 2, 64, hd, size=12, color=INK, bold=True))

    # ряд «нове» (temp_mc)
    ny, rh = 88, 52
    parts.append(mtext(74, 110, ["temp_mc", "(нове)"], size=11, color=FIELD, anchor="end"))
    new_cells = [
        ("#ffffff", "порожнє (NULL)", MUTED),
        ("#eafaf0", "нові рядки", FIELD),
        ("#d3f0df", "+ історія", FIELD),
        ("#b6e9c9", "повне", FIELD),
        ("#9ce0b6", "єдине джерело", "#15703b"),
    ]
    for i, (fill, lab, col) in enumerate(new_cells):
        parts.append(fitbox(xs[i], ny, cw, rh, lab, size=12, fill=fill,
                            stroke=FIELD, sw=1.6, color=col))

    # ряд «старе» (temp_c)
    oy = 164
    parts.append(mtext(74, 186, ["temp_c", "(старе)"], size=11, color=NEG, anchor="end"))
    old_cells = [
        ("#dce6fb", "джерело правди", NEG),
        ("#dce6fb", "джерело правди", NEG),
        ("#dce6fb", "ще джерело", NEG),
        ("#eef2fb", "лише страховка", MUTED),
        ("#fdecea", "прибрано", POS),
    ]
    for i, (fill, lab, col) in enumerate(old_cells):
        st = POS if i == 4 else NEG
        parts.append(fitbox(xs[i], oy, cw, rh, lab, size=12, fill=fill,
                            stroke=st, sw=1.6, color=col))

    # дужка співіснування під фазами 1-4
    bl, br = xs[0], xs[3] + cw
    byk = oy + rh + 22
    parts.append(line(bl, byk, br, byk, color=FIELD, sw=2))
    parts.append(line(bl, byk, bl, byk - 8, color=FIELD, sw=2))
    parts.append(line(br, byk, br, byk - 8, color=FIELD, sw=2))
    b, w, h = textbox((bl + br) / 2, byk + 19,
                      "обидві колонки живі — дорога назад є будь-якої миті",
                      size=12, color="#15703b", stroke=FIELD, fill="#eafaf0", pad=8)
    parts.append(b)

    # позначка «однобічний крок» під фазою 5
    parts.append(mtext(xs[4] + cw / 2, byk + 6, ["тут зникає", "дорога назад"],
                       size=11, color=POS, bold=True))

    render(os.path.join(IMG, "timeline.svg"), W, H, *parts,
           title="Старе й нове живуть поряд, поки нове не довело себе")


def fig_decompose():
    """Вартість відкату по вимірах; шов стискає лише вимір майбутніх звертань (код)."""
    W, H = 880, 430
    parts = []
    xlab = 236          # правий край підписів виміру
    xb0 = 250           # старт смуг
    bmax = 452          # макс. ширина смуги
    xbadge = 800        # центр бейджа «шов»

    parts.append(text(xlab, 62, "вимір залежності", size=12, color=MUTED, anchor="end"))
    parts.append(text(xb0, 62, "внесок у вартість відкату  ·  колір = досяжність",
                      size=12, color=MUTED, anchor="start"))
    parts.append(text(xbadge, 62, "шов", size=12, color=MUTED))

    rows = [
        ("місця коду", 0.16, FIELD, True),
        ("рядки даних", 1.00, NEG, False),
        ("зовнішні споживачі", 0.58, "#d98324", False),
        ("сусідні команди", 0.44, "#b8a51e", False),
        ("відвантажені пристрої", 0.82, POS, False),
    ]
    y, dy, bh = 92, 60, 30
    for lab, frac, col, seam in rows:
        cy = y + bh / 2
        parts.append(text(xlab, cy + 5, lab, size=13, color=INK, anchor="end"))
        parts.append(rect(xb0, y, bmax * frac, bh, fill=col, stroke=col, sw=1.4, rx=5))
        if seam:
            b, _, _ = textbox(xbadge, cy, "✓ O(1)", size=12, color=FIELD,
                              stroke=FIELD, fill="#eafaf0", pad=7, bold=True)
        else:
            b, _, _ = textbox(xbadge, cy, "✗ O(N)", size=12, color=POS,
                              stroke=POS, fill="#fdecea", pad=7, bold=True)
        parts.append(b)
        y += dy

    parts.append(text(W / 2, y + 14,
                      "шов стискає лише майбутні звертання (код); уречевлене минуле — байти, обіцянки, залізо — крізь шов не тече",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "decompose.svg"), W, H, *parts,
           title="Вартість відкату — сума по вимірах, і що з кожним робить шов")


def fig_decay_steps():
    """Спад зворотності сходинками: гладкий підйом + різкі стрибки на межах досяжності."""
    W, H = 820, 430
    x0, y_ax = 90, 360
    parts = []

    parts.append(arrow(x0, y_ax, 800, y_ax))
    parts.append(arrow(x0, y_ax, x0, 60))
    parts.append(text(96, 52, "вартість відкату", size=12, color=MUTED, anchor="start"))
    parts.append(text(794, 351, "час · накопичене →", size=12, color=MUTED, anchor="end"))

    # крива: гладкий опуклий підйом + три вертикальні сходинки
    pts = [(100, 350), (200, 340), (300, 318), (300, 250), (400, 238),
           (470, 224), (470, 162), (560, 150), (620, 140), (620, 86),
           (700, 78), (760, 72)]
    poly = " ".join("%.0f,%.0f" % p for p in pts)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, NEG))

    # легенда-стек угорі ліворуч (порожня зона над пласким початком)
    parts.append(text(112, 80, "сходинки — переступи межі досяжності:",
                      size=12, color=INK, anchor="start", bold=True))
    stack = ["① перший зовнішній споживач",
             "② перша сусідня команда",
             "③ перший відвантажений пристрій"]
    for i, s in enumerate(stack):
        parts.append(text(112, 104 + i * 22, s, size=12, color=MUTED, anchor="start"))

    # маркери ①②③ біля основи кожної сходинки (ліворуч від стовпчика, над кривою)
    for cx, cy, lb in [(283, 284, "①"), (452, 193, "②"), (602, 113, "③")]:
        parts.append(circle(cx, cy, 10, fill=BG, stroke=INK, sw=1.2))
        parts.append(text(cx, cy + 4, lb, size=12, color=INK, bold=True))

    # останній відповідальний момент — пунктир перед першою сходинкою
    parts.append(line(268, 322, 268, y_ax, color=INK, sw=1.4, dash="5 4"))
    parts.append(text(268, 382, "останній відповідальний момент", size=12, color=INK, bold=True))
    parts.append(text(268, 400, "далі двері грюкають сходинками", size=11, color=MUTED))

    # кути-присуди
    parts.append(text(190, 258, "двобічні — дешево", size=12, color="#15703b"))
    parts.append(text(690, 258, "однобічні — за сходинками", size=12, color=POS))

    render(os.path.join(IMG, "decay_steps.svg"), W, H, *parts,
           title="Зворотність спадає не рівно, а сходинками")


def fig_floor():
    """Три роди відкату; за межею стирання/випуску вартість не висока, а невизначена."""
    W, H = 900, 440
    parts = []
    xb = 670            # межа Ландауера

    # межа й підпис
    parts.append(line(xb, 74, xb, 350, color=POS, sw=1.6, dash="6 4"))
    b, _, _ = textbox(xb, 60, "межа Ландауера: стирання / випуск",
                      size=12, color=POS, stroke=POS, fill="#fdecea", pad=7)
    parts.append(b)

    # рід 1 — оборотне заплативши (зелена смуга, скінченна)
    parts.append(rect(120, 100, 520, 50, fill="#eafaf0", stroke=FIELD, sw=1.7, rx=8))
    parts.append(text(380, 122, "рід 1 · оборотне — заплативши", size=13, color=FIELD, bold=True))
    parts.append(text(380, 140, "рефактор · міграція · передеплой — дорого, але скінченно",
                      size=12, color=INK))

    # рід 2 — оборотне заміщенням (синя смуга, скінченна)
    parts.append(rect(120, 170, 520, 50, fill="#eef2fb", stroke=NEG, sw=1.7, rx=8))
    parts.append(text(380, 192, "рід 2 · оборотне — заміщенням", size=13, color=NEG, bold=True))
    parts.append(text(380, 210, "розширення-звуження · ротація ключів · v2 біля v1",
                      size=12, color=INK))

    # рід 3 — дороги нема (за межею, зона ∞)
    parts.append(text(120, 272, "рід 3 · дороги нема", size=13, color=POS, anchor="start", bold=True))
    parts.append(text(120, 292, "за жодну ціну", size=12, color=MUTED, anchor="start"))
    for i, s in enumerate(["видалене без копії", "витеклий секрет", "відвантажене без каналу"]):
        b, _, _ = textbox(768, 250 + i * 40, s, size=12, color=POS,
                          stroke=POS, fill="#fdecea", pad=8)
        parts.append(b)

    # вісь вартості внизу
    parts.append(arrow(90, 360, 850, 360))
    parts.append(text(96, 353, "вартість відкату →", size=12, color=MUTED, anchor="start"))
    for tx, s, col in [(160, "копійки", MUTED), (340, "дорого", MUTED),
                       (520, "дуже дорого", MUTED), (800, "∞ невизначено", POS)]:
        parts.append(text(tx, 382, s, size=12, color=col))

    render(os.path.join(IMG, "floor.svg"), W, H, *parts,
           title="Дорога-костильна проти дороги-нема: справжня межа")


def fig_key_overlap():
    """Ротація ключів як храповик: старий і новий ключ чинні поряд, поки не відкликали старий."""
    W, H = 1020, 316
    parts = []

    n = 5
    cx0, cw, step = 108, 176, 182
    xs = [cx0 + i * step for i in range(n)]
    heads = ["1 · закладка", "2 · додати #2", "3 · рознести полем",
             "4 · перемкнути підпис", "5 · відкликати #1"]

    for i, hd in enumerate(heads):
        parts.append(text(xs[i] + cw / 2, 64, hd, size=12, color=INK, bold=True))

    # ряд «ключ #1» (старий) — джерело довіри, поки живий
    ny, rh = 82, 52
    parts.append(mtext(96, 104, ["ключ #1", "(старий)"], size=11, color=NEG, anchor="end"))
    old_cells = [
        ("#dce6fb", "чинний, підписує", NEG),
        ("#dce6fb", "чинний", NEG),
        ("#dce6fb", "чинний", NEG),
        ("#eef2fb", "чинний, у резерві", MUTED),
        ("#fdecea", "відкликаний", POS),
    ]
    for i, (fill, lab, col) in enumerate(old_cells):
        st = POS if i == 4 else NEG
        parts.append(fitbox(xs[i], ny, cw, rh, lab, size=12, fill=fill,
                            stroke=st, sw=1.6, color=col))

    # ряд «ключ #2» (новий)
    oy = 158
    parts.append(mtext(96, 180, ["ключ #2", "(новий)"], size=11, color=FIELD, anchor="end"))
    new_cells = [
        ("#ffffff", "— ще нема", MUTED),
        ("#eafaf0", "доданий, чинний", FIELD),
        ("#d3f0df", "чинний, наздоганяє", FIELD),
        ("#b6e9c9", "підписує", FIELD),
        ("#9ce0b6", "єдиний", "#15703b"),
    ]
    for i, (fill, lab, col) in enumerate(new_cells):
        st = FIELD
        parts.append(fitbox(xs[i], oy, cw, rh, lab, size=12, fill=fill,
                            stroke=st, sw=1.6, color=col))

    # дужка співіснування під фазами 1-4 (поки ключ #1 живий — є дорога назад)
    bl, br = xs[0], xs[3] + cw
    byk = oy + rh + 22
    parts.append(line(bl, byk, br, byk, color=FIELD, sw=2))
    parts.append(line(bl, byk, bl, byk - 8, color=FIELD, sw=2))
    parts.append(line(br, byk, br, byk - 8, color=FIELD, sw=2))
    b, w, h = textbox((bl + br) / 2, byk + 19,
                      "ключ #1 ще чинний — можна вернутися на нього будь-якої миті",
                      size=12, color="#15703b", stroke=FIELD, fill="#eafaf0", pad=8)
    parts.append(b)

    # під фазою 5 — червоний глухий кут
    parts.append(mtext(xs[4] + cw / 2, byk + 6, ["тут зникає", "старий ключ"],
                       size=11, color=POS, bold=True))

    render(os.path.join(IMG, "key_overlap.svg"), W, H, *parts,
           title="Старий і новий ключ живуть поряд, поки новий не довів себе")


def fig_two_tier():
    """Два яруси довіри: корінь (офлайн) підписує оновлення ключів, операційний — щоденні дозволи."""
    W, H = 960, 470
    parts = []
    xl, xr = 258, 702          # осі двох ярусів
    xdev = 480                 # центр пристрою

    # ── ярус 1: два ключі за роллю ──
    b, w, h = textbox(xl, 96,
                      "КОРІНЬ (root)\nофлайн, в HSM\nпідписує лише оновлення ключів\nротація — рідко",
                      size=12, color=NEG, stroke=NEG, fill="#eef2fb", pad=11, bold=False)
    parts.append(b)
    b, w, h = textbox(xr, 96,
                      "ОПЕРАЦІЙНИЙ (hot)\nу мережі, підписує щодня\nдозволи на відкриття\nротація — часто",
                      size=12, color=FIELD, stroke=FIELD, fill="#eafaf0", pad=11, bold=False)
    parts.append(b)

    # ── те, що кожен підписує ──
    b1, w1, h1 = textbox(xl, 224, "оновлення ключа\n(add · revoke)",
                         size=12, color=INK, stroke=NEG, fill=FILL, pad=10)
    b2, w2, h2 = textbox(xr, 224, "дозвіл на відкриття\n(нонс + термін)",
                         size=12, color=INK, stroke=FIELD, fill=FILL, pad=10)
    parts.append(arrow(xl, 148, xl, 224 - h1 / 2 - 3, color=NEG, sw=1.6))
    parts.append(arrow(xr, 148, xr, 224 - h2 / 2 - 3, color=FIELD, sw=1.6))
    parts.append(text(xl - 8, 190, "підписує", size=11, color=MUTED, anchor="end"))
    parts.append(text(xr + 8, 190, "підписує", size=11, color=MUTED, anchor="start"))
    parts.append(b1)
    parts.append(b2)

    # ── пристрій у полі ──
    bd, wd, hd = textbox(xdev, 342, "замок у полі\nзвʼязка ключів: kid + вікно чинності",
                         size=12, color=INK, stroke=INK, fill="#fbfbfb", pad=12, bold=True)
    parts.append(arrow(xl, 224 + h1 / 2 + 3, xdev - wd / 2 - 4, 342 - hd / 2, color=NEG, sw=1.6))
    parts.append(arrow(xr, 224 + h2 / 2 + 3, xdev + wd / 2 + 4, 342 - hd / 2, color=FIELD, sw=1.6))
    parts.append(bd)

    # ── підпис-сценарій унизу ──
    parts.append(text(xdev, 404,
                      "Операційний ключ витік? Корінь недоторканий, бо офлайн — підписує «відкликати #1, додати #2».",
                      size=12, color=INK))
    parts.append(text(xdev, 428,
                      "Гарячий ключ міняють часто й дешево; корінь тримають офлайн саме щоб він завжди міг підписати порятунок.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "two_tier.svg"), W, H, *parts,
           title="Два яруси довіри: рідкісний корінь наглядає за частим операційним")


def fig_hyrum_saturation():
    """P(хтось залежить)=1-(1-p)^N по лог-осі N для кількох p: будь-яка p>0 → 1."""
    import math
    W, H = 820, 470
    x0, y_ax, ytop, xr = 96, 384, 74, 776
    lw, hh, LMAX = xr - x0, y_ax - 74, 6.0
    parts = []

    def X(N): return x0 + (math.log10(N) / LMAX) * lw
    def Y(P): return y_ax - P * hh

    # осі
    parts.append(arrow(x0, y_ax, xr + 8, y_ax))
    parts.append(arrow(x0, y_ax, x0, ytop - 8))
    parts.append(text(x0 - 4, ytop - 16, "P(хтось залежить)", size=12, color=MUTED, anchor="start"))
    parts.append(text(xr + 6, y_ax + 42, "N — користувачів (лог)", size=12, color=MUTED, anchor="end"))

    dec = ["1", "10", "100", "10³", "10⁴", "10⁵", "10⁶"]
    for k, lab in enumerate(dec):
        x = x0 + (k / LMAX) * lw
        parts.append(line(x, y_ax, x, y_ax + 5, color=MUTED, sw=1))
        parts.append(text(x, y_ax + 20, lab, size=11, color=MUTED))
    for P, lab in [(0.0, "0"), (0.5, "½"), (1.0, "1")]:
        y = Y(P)
        parts.append(line(x0 - 5, y, x0, y, color=MUTED, sw=1))
        parts.append(text(x0 - 12, y + 4, lab, size=11, color=MUTED, anchor="end"))

    # стеля P=1 і лінія половини
    parts.append(line(x0, Y(1.0), xr, Y(1.0), color=MUTED, sw=1, dash="2 4"))
    parts.append(line(x0, Y(0.5), xr, Y(0.5), color=INK, sw=1, dash="5 4"))

    curves = [
        (0.1,    POS,       "p = 0.1  —  N* ≈ 7"),
        (0.01,   "#d98324", "p = 0.01  —  N* ≈ 69"),
        (0.001,  FIELD,     "p = 0.001  —  N* ≈ 690"),
        (0.0001, NEG,       "p = 0.0001  —  N* ≈ 6900"),
    ]
    Ns = [10 ** (i / 12.0) for i in range(int(LMAX * 12) + 1)]
    for p, col, _ in curves:
        pts = [(X(N), Y(1.0 - (1.0 - p) ** N)) for N in Ns]
        poly = " ".join("%.1f,%.1f" % q for q in pts)
        parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (poly, col))

    # легенда в порожній нижньо-правій зоні (під усіма кривими)
    bx, by, bw, bh = 556, 240, 218, 138
    parts.append(rect(bx, by, bw, bh, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(bx + bw / 2, by + 20, "N*(½) = ln2 / p · стеля завжди 1", size=11, color=INK, bold=True))
    ys = [by + 42, by + 64, by + 86, by + 108]
    for (p, col, lab), ry in zip(curves, ys):
        parts.append(line(bx + 14, ry, bx + 42, ry, color=col, sw=3))
        parts.append(text(bx + 50, ry + 4, lab, size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, "hyrum_saturation.svg"), W, H, *parts,
           title="Насичення: будь-яка помітна поведінка доростає до контракту")


def fig_hyrum_lambda():
    """Універсальна крива P=1-e^(-λ), λ=Np: тиск користувачів праворуч, важіль ентропії ліворуч."""
    import math
    W, H = 820, 460
    x0, y_ax, ytop, xr = 96, 356, 74, 720
    lw, hh, LMAX = xr - x0, y_ax - 74, 6.0
    parts = []

    def X(l): return x0 + (l / LMAX) * lw
    def Y(P): return y_ax - P * hh

    parts.append(arrow(x0, y_ax, xr + 8, y_ax))
    parts.append(arrow(x0, y_ax, x0, ytop - 8))
    parts.append(text(x0 - 4, ytop - 16, "P = 1 − e^(−λ)", size=12, color=MUTED, anchor="start"))
    parts.append(text(xr + 6, y_ax + 42, "λ = N · p", size=13, color=INK, anchor="end"))

    for l in range(7):
        x = X(l)
        parts.append(line(x, y_ax, x, y_ax + 5, color=MUTED, sw=1))
        parts.append(text(x, y_ax + 20, str(l), size=11, color=MUTED))
    for P, lab in [(0.0, "0"), (0.5, "½"), (1.0, "1")]:
        y = Y(P)
        parts.append(line(x0 - 5, y, x0, y, color=MUTED, sw=1))
        parts.append(text(x0 - 12, y + 4, lab, size=11, color=MUTED, anchor="end"))

    parts.append(line(x0, Y(1.0), xr, Y(1.0), color=MUTED, sw=1, dash="2 4"))

    pts, l = [], 0.0
    while l <= 6.0001:
        pts.append((X(l), Y(1 - math.exp(-l))))
        l += 0.1
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
                 % (" ".join("%.1f,%.1f" % q for q in pts), NEG))

    for l in (1, 3, 5):
        parts.append(circle(X(l), Y(1 - math.exp(-l)), 4, fill=BG, stroke=INK, sw=1.4))
    parts.append(text(X(1) + 10, Y(1 - math.exp(-1)) + 24, "λ=1 · P≈0.63", size=11, color=INK, anchor="start"))
    parts.append(text(X(3) + 10, Y(1 - math.exp(-3)) + 24, "λ=3 · P≈0.95", size=11, color=INK, anchor="start"))
    parts.append(text(X(5) + 8, Y(1 - math.exp(-5)) + 26, "λ=5 · P≈0.99", size=11, color=INK, anchor="start"))

    # важіль ентропії — ліворуч, над кривою (порожня зона)
    parts.append(text(186, 104, "впорскування ентропії:  p ↓  ⇒  λ ↓", size=12, color=FIELD, bold=True))
    parts.append(arrow(250, 120, 112, 120, color=FIELD, sw=1.8))
    parts.append(text(168, 276, "поведінка ще вільна", size=12, color=MUTED, anchor="start"))

    # тиск користувачів — праворуч, під кривою (порожня зона)
    parts.append(text(600, 152, "контракт майже певний", size=12, color=POS))
    parts.append(arrow(470, 300, 690, 300, color=POS, sw=1.8))
    parts.append(text(580, 320, "більше користувачів N  ⇒  λ = Np росте", size=12, color=POS))

    b, w, h = textbox(410, 416,
                      "рандомізація мапи в Go тримає p ≈ 0  ⇒  λ ≈ 0: залежності нема на що впертися",
                      size=12, color=INK, stroke=FIELD, fill="#eafaf0", pad=9)
    parts.append(b)

    render(os.path.join(IMG, "hyrum_lambda.svg"), W, H, *parts,
           title="Тиск контракту λ=Np і єдиний важіль проти нього — ентропія")


if __name__ == "__main__":
    fig_decay()
    fig_reach()
    fig_ratchet()
    fig_timeline()
    fig_decompose()
    fig_decay_steps()
    fig_floor()
    fig_key_overlap()
    fig_two_tier()
    fig_hyrum_saturation()
    fig_hyrum_lambda()
    print("ok")
