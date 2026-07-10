# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Життя об'єкта: без пулу (створити-знищити щоразу) проти з пулом (коло) ─────
def fig_borrow_return():
    W, H = 1120, 760
    frags = []

    # роздільна лінія між верхом і низом
    frags.append(line(60, 300, W - 60, 300, color="#d0d5db", sw=1.2, dash="7,7"))

    # ═══════════ ВЕРХ: БЕЗ ПУЛУ ═══════════
    frags.append(text(W / 2, 42, "Без пулу — кожне використання платить за народження",
                      size=16, bold=True, color=POS))

    # три однакові цикли створити→попрацювати→знищити, поряд
    cyc_cx = [W * 0.22, W * 0.5, W * 0.78]
    cy_top = 96
    step_labels = ["створити", "попрацювати", "знищити"]
    step_notes = ["ДОРОГО", "", "викинути"]
    step_cols = [POS, INK, MUTED]
    for k, ccx in enumerate(cyc_cx):
        frags.append(text(ccx, cy_top - 8, "використання %d" % (k + 1),
                          size=11.5, color=MUTED))
        prev_bottom = None
        for i, (lab, note, col) in enumerate(zip(step_labels, step_notes, step_cols)):
            by = cy_top + 18 + i * 62
            label = lab if not note else "%s (%s)" % (lab, note)
            b, bw, bh = textbox(ccx, by, label, size=12, bold=(i == 0),
                                fill=("#fdecea" if i == 0 else FILL),
                                stroke=col, sw=1.5, min_w=176)
            frags.append(b)
            if prev_bottom is not None:
                frags.append(arrow(ccx, prev_bottom, ccx, by - bh / 2 - 2,
                                   color=LINE, sw=1.4))
            prev_bottom = by + bh / 2
    frags.append(text(W / 2, 288, "…і так знову, і знову — кожен цикл оплачує дороге створення",
                      size=12, color=INK))

    # ═══════════ НИЗ: З ПУЛОМ ═══════════
    frags.append(text(W / 2, 342, "З пулом — народження раз, далі об'єкт кружляє між станами",
                      size=16, bold=True, color=FIELD))

    # пул-контейнер ліворуч із трьома об'єктами (стан: вільний/зайнятий)
    pool_x, pool_y, pool_w, pool_h = 90, 396, 300, 250
    frags.append(rect(pool_x, pool_y, pool_w, pool_h, fill="#f4fbf7",
                      stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(pool_x + pool_w / 2, pool_y + 26, "ПУЛ",
                      size=14, bold=True, color=FIELD))
    frags.append(text(pool_x + pool_w / 2, pool_y + 46,
                      "створені раз, на старті", size=11, color=MUTED))
    slots = [("об'єкт A — вільний", FIELD, "#e8f6ee"),
             ("об'єкт B — зайнятий", POS, "#fdecea"),
             ("об'єкт C — вільний", FIELD, "#e8f6ee")]
    for i, (lab, col, fill) in enumerate(slots):
        sy = pool_y + 92 + i * 50
        b, _, _ = textbox(pool_x + pool_w / 2, sy, lab, size=12,
                          fill=fill, stroke=col, sw=1.4, min_w=250)
        frags.append(b)

    # праворуч — клієнт, і коло позичити→працювати→повернути
    cli_x = W * 0.72
    ring_top = 402
    # три стани клієнта
    steps = [("acquire()  ← позичив", NEG, "#eaf0fd"),
             ("працює з об'єктом", INK, FILL),
             ("release()  ← повернув", FIELD, "#e8f6ee")]
    ys = []
    for i, (lab, col, fill) in enumerate(steps):
        sy = ring_top + i * 74
        ys.append(sy)
        b, bw, bh = textbox(cli_x, sy, lab, size=12.5, bold=True,
                            fill=fill, stroke=col, sw=1.6, min_w=250)
        frags.append(b)
        if i > 0:
            frags.append(arrow(cli_x, ys[i - 1] + bh / 2 + 2, cli_x, sy - bh / 2 - 2,
                               color=LINE, sw=1.5))

    # стрілка "acquire" від пулу до клієнта і "release" назад — по краях, повз написи
    ax_out = pool_x + pool_w
    frags.append(arrow(ax_out + 4, ring_top, cli_x - 132, ring_top,
                       color=NEG, sw=1.7))
    frags.append(text((ax_out + cli_x - 132) / 2, ring_top - 12,
                      "дай вільний", size=11, color=NEG))
    frags.append(arrow(cli_x - 132, ys[2], ax_out + 4, ys[2],
                       color=FIELD, sw=1.7))
    frags.append(text((ax_out + cli_x - 132) / 2, ys[2] + 20,
                      "поклади назад", size=11, color=FIELD))

    # замикання кола: від release угору до acquire (наступний користувач)
    loop_x = cli_x + 172
    frags.append(line(cli_x + 132, ys[2], loop_x, ys[2], color=MUTED, sw=1.4))
    frags.append(line(loop_x, ys[2], loop_x, ring_top, color=MUTED, sw=1.4))
    frags.append(arrow(loop_x, ring_top, cli_x + 132, ring_top, color=MUTED, sw=1.4))
    frags.append(text(loop_x + 8, (ring_top + ys[2]) / 2, "той самий",
                      size=10.5, color=MUTED, anchor="start"))
    frags.append(text(loop_x + 8, (ring_top + ys[2]) / 2 + 15, "об'єкт —",
                      size=10.5, color=MUTED, anchor="start"))
    frags.append(text(loop_x + 8, (ring_top + ys[2]) / 2 + 30, "наступному",
                      size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'borrow-return.svg'), W, H, *frags)


# ── Часова смуга: як пул із практики визрів у названий патерн і назад ─────────
def fig_timeline():
    W, H = 1180, 560
    frags = []

    # горизонтальна вісь часу
    axis_y = 300
    x0, x1 = 90, W - 60
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2))
    frags.append(arrow(x1 - 2, axis_y, x1 + 2, axis_y, color=INK, sw=2))
    frags.append(text(x1 + 6, axis_y + 26, "час", size=12, color=MUTED, anchor="end"))

    # роки й позиції на осі (рівномірно розкидані з запасом між написами)
    marks = [
        (1994, 0.10, "up",
         ["«Банда чотирьох»", "23 патерни —", "пулу серед них НЕМА"],
         POS, "#fdecea"),
        (1999, 0.34, "down",
         ["JDBC 2.0 Optional Package:", "пул з'єднань —", "у стандарті мови"],
         FIELD, "#e8f6ee"),
        (2002, 0.58, "up",
         ["Kircher і Jain, «Pooling»", "(EuroPLoP, с. 497–510):", "пул описано як патерн"],
         NEG, "#eaf0fd"),
        (2005, 0.86, "down",
         ["Goetz і Bloch:", "«пулити все» — міф;", "лише важкі ресурси"],
         "#8e44ad", "#f3e9f7"),
    ]

    for year, t, side, lines, col, fill in marks:
        cx = x0 + t * (x1 - x0)
        # вузол на осі
        frags.append(circle(cx, axis_y, 8, fill=fill, stroke=col, sw=2.4))
        # рік — біля осі, з протилежного боку від картки
        yr_dy = 40 if side == "up" else -28
        frags.append(text(cx, axis_y + yr_dy, str(year), size=17, bold=True, color=col))
        # картка-опис — вгору або вниз, повз вісь (висоту знаємо з рядків)
        nlines = len(lines)
        bh = nlines * 12.5 * 1.3 + 2 * 10 - 12.5 * 0.3
        if side == "up":
            box_cy = axis_y - 78 - bh / 2
            conn_y2 = box_cy + bh / 2
        else:
            box_cy = axis_y + 88 + bh / 2
            conn_y2 = box_cy - bh / 2
        b, _, _ = textbox(cx, box_cy, "\n".join(lines), size=12.5, bold=False,
                          fill=fill, stroke=col, sw=1.6, min_w=246)
        frags.append(b)
        # тонка ніжка від вузла до картки
        stem_y1 = axis_y - 8 if side == "up" else axis_y + 8
        frags.append(line(cx, stem_y1, cx, conn_y2, color=col, sw=1.3, dash="4,4"))

    # підпис-дуга: практика → назва → розворот поради
    frags.append(text(W / 2, 40,
                      "Пул жив у практиці задовго до назви — і назву дістав уже після сумнівів",
                      size=15, bold=True, color=INK))
    frags.append(text(W / 2, H - 26,
                      "з інженерії продуктивності (бази, сервери) → у каталог патернів → назад до «міряй, не вір»",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'timeline.svg'), W, H, *frags)


# ── Двобічний оптимум розміру пулу: замалий і завеликий однаково шкодять ──────
def fig_size_optimum():
    W, H = 1180, 620
    frags = []
    x0, x1 = 120, 1080
    ybase, ytop = 520, 110

    # осі
    frags.append(line(x0, ybase, x1 + 6, ybase, color=INK, sw=2))
    frags.append(arrow(x1, ybase, x1 + 8, ybase, color=INK, sw=2))
    frags.append(line(x0, ybase, x0, ytop - 6, color=INK, sw=2))
    frags.append(arrow(x0, ytop, x0, ytop - 8, color=INK, sw=2))
    frags.append(text(x1 - 4, ybase + 30, "розмір пулу →", size=13, color=MUTED, anchor="end"))
    frags.append(text(x0 - 6, ytop + 2, "корисний потік", size=13, color=MUTED, anchor="end"))

    def px(fx): return x0 + fx * (x1 - x0)
    def py(fy): return ybase - fy * (ybase - ytop)

    # крива потоку: круто вгору → пік → повільний спад
    pts = [(0.02, 0.05), (0.07, 0.28), (0.13, 0.52), (0.20, 0.73),
           (0.29, 0.90), (0.40, 0.99), (0.50, 0.97), (0.61, 0.88),
           (0.72, 0.75), (0.84, 0.58), (0.97, 0.42)]
    poly = " ".join("%.1f,%.1f" % (px(fx), py(fy)) for fx, fy in pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                 % (poly, NEG))

    # межі трьох зон (тонкі пунктири; лінія-крізь-лінію — норма)
    b1, b2 = 0.235, 0.555
    frags.append(line(px(b1), ybase, px(b1), ytop + 30, color="#c0c6cf", sw=1.2, dash="6,6"))
    frags.append(line(px(b2), ybase, px(b2), ytop + 30, color="#c0c6cf", sw=1.2, dash="6,6"))

    # пік — маркер і підпис над ним
    pk = (0.40, 0.99)
    frags.append(circle(px(pk[0]), py(pk[1]), 6, fill="#eaf0fd", stroke=NEG, sw=2.4))
    frags.append(text(px(pk[0]), py(pk[1]) - 20, "оптимум ≈ (ядра·2) + диски",
                      size=13.5, bold=True, color=NEG))

    # зона «замалий» — картка ліворуч, під висхідною гілкою
    bL, _, _ = textbox(px(0.10), 350, "ЗАМАЛИЙ\nусі зайняті — черга\nна вході (закон Літтла)",
                       size=12.5, fill="#fdf0ea", stroke=POS, sw=1.5, min_w=232)
    frags.append(bL)
    # зона «завеликий» — картка праворуч, над спадною гілкою
    bR, _, _ = textbox(px(0.86), 200, "ЗАВЕЛИКИЙ\nтиск на базу: контекст-\nсвітчі, боротьба за замки",
                       size=12.5, fill="#fdf0ea", stroke=POS, sw=1.5, min_w=248)
    frags.append(bR)

    frags.append(text(W / 2, 42, "У пулу — двобічний оптимум: і замалий, і завеликий гальмують",
                      size=16, bold=True, color=INK))
    render(os.path.join(IMG, 'pool-size-optimum.svg'), W, H, *frags)


# ── Справжній життєвий цикл об'єкта пулу: старіння, валідація, оновлення ───────
def fig_lifecycle():
    W, H = 1140, 660
    frags = []

    born = (235, 135)
    free = (665, 135)
    busy = (665, 480)
    dead = (235, 480)

    b1, w1, h1 = textbox(*born, "СТВОРЮЄТЬСЯ\n(дороге народження)",
                         size=12.5, fill="#eef2fb", stroke=NEG, sw=1.7, min_w=210)
    b2, w2, h2 = textbox(*free, "ВІЛЬНИЙ\n(на полиці, чистий)",
                         size=12.5, fill="#e9f7ef", stroke=FIELD, sw=1.7, min_w=210)
    b3, w3, h3 = textbox(*busy, "ЗАЙНЯТИЙ\n(виданий назовні)",
                         size=12.5, fill="#fdf0ea", stroke=POS, sw=1.7, min_w=210)
    b4, w4, h4 = textbox(*dead, "НА ЗЛАМ\n(знищується)",
                         size=12.5, fill=FILL, stroke=MUTED, sw=1.7, min_w=210)
    frags += [b1, b2, b3, b4]

    # створюється → вільний (верх)
    frags.append(arrow(born[0] + w1 / 2 + 4, born[1], free[0] - w2 / 2 - 4, free[1],
                       color=INK, sw=1.6))
    frags.append(text((born[0] + free[0]) / 2, born[1] - 14, "готовий до видачі",
                      size=11.5, color=MUTED))

    # вільний → зайнятий (права гілка вниз): acquire + валідація
    ax = 720
    frags.append(line(free[0], free[1] + h2 / 2 + 2, ax, free[1] + h2 / 2 + 2, color=NEG, sw=1.6))
    frags.append(line(ax, free[1] + h2 / 2 + 2, ax, busy[1] - h3 / 2 - 2, color=NEG, sw=1.6))
    frags.append(arrow(ax, busy[1] - h3 / 2 - 2, busy[0] + w3 / 2 + 2, busy[1] - h3 / 2 - 2,
                       color=NEG, sw=1.6))
    frags.append(text(ax + 12, (free[1] + busy[1]) / 2 - 8, "acquire", size=11.5, color=NEG, anchor="start"))
    frags.append(text(ax + 12, (free[1] + busy[1]) / 2 + 8, "+ валідація", size=11.5, color=NEG, anchor="start"))

    # зайнятий → вільний (ліва гілка вгору): release + reset
    rx = 605
    frags.append(line(busy[0], busy[1] - h3 / 2 - 2, rx, busy[1] - h3 / 2 - 2, color=FIELD, sw=1.6))
    frags.append(line(rx, busy[1] - h3 / 2 - 2, rx, free[1] + h2 / 2 + 2, color=FIELD, sw=1.6))
    frags.append(arrow(rx, free[1] + h2 / 2 + 2, free[0] - w2 / 2 - 2, free[1] + h2 / 2 + 2,
                       color=FIELD, sw=1.6))
    frags.append(text(rx - 12, (free[1] + busy[1]) / 2 - 8, "release", size=11.5, color=FIELD, anchor="end"))
    frags.append(text(rx - 12, (free[1] + busy[1]) / 2 + 8, "+ reset", size=11.5, color=FIELD, anchor="end"))

    # вільний → на злам (діагональ): простій / не пройшов валідацію
    frags.append(arrow(free[0] - w2 / 2 - 2, free[1] + h2 / 2, dead[0] + w4 / 2 + 6, dead[1] - h4 / 2 - 2,
                       color=MUTED, sw=1.5))
    frags.append(text(455, 270, "простій > idle-timeout", size=11.5, color=MUTED))
    frags.append(text(455, 286, "або не пройшов валідацію", size=11.5, color=MUTED))

    # зайнятий → на злам (низ): вік > max-lifetime
    frags.append(arrow(busy[0] - w3 / 2 - 2, busy[1], dead[0] + w4 / 2 + 2, dead[1],
                       color=MUTED, sw=1.5))
    frags.append(text((born[0] + free[0]) / 2 + 10, busy[1] + 26,
                      "release, але вік > max-lifetime → на злам", size=11.5, color=MUTED))

    # на злам → створюється (ліва колона вгору): поповнити до min-idle
    lx = 145
    frags.append(line(dead[0] - w4 / 2 - 2, dead[1], lx, dead[1], color=NEG, sw=1.5, dash="5,5"))
    frags.append(line(lx, dead[1], lx, born[1], color=NEG, sw=1.5, dash="5,5"))
    frags.append(arrow(lx, born[1], born[0] - w1 / 2 - 2, born[1], color=NEG, sw=1.5))
    frags.append(text(lx - 6, (born[1] + dead[1]) / 2 - 8, "поповнити", size=11, color=NEG, anchor="end"))
    frags.append(text(lx - 6, (born[1] + dead[1]) / 2 + 8, "до min-idle", size=11, color=NEG, anchor="end"))

    frags.append(text(W / 2, 42, "Живі стани — лише «вільний» і «зайнятий»; решта — старіння й оновлення",
                      size=15.5, bold=True, color=INK))
    render(os.path.join(IMG, 'lifecycle-states.svg'), W, H, *frags)


# ── Чому пул дрібних об'єктів у GC-мові стріляє в ногу (покоління) ─────────────
def fig_gc_generations():
    W, H = 1180, 560
    frags = []

    # роздільник між доріжками
    frags.append(line(70, 258, W - 70, 258, color="#d0d5db", sw=1.2, dash="7,7"))

    # ── доріжка А: короткоживучий, без пулу ──
    frags.append(text(W / 2, 44, "Короткоживучий об'єкт — без пулу: GC саме на це заточений",
                      size=15.5, bold=True, color=FIELD))
    ya = 150
    a = [
        ((200, ya), "народження\nу молодшому поколінні\n(зсув вказівника —\nмайже дарма)", "#e9f7ef"),
        ((560, ya), "швидко вмирає\n(гіпотеза поколінь:\nмолоде гине рано)", "#e9f7ef"),
        ((900, ya), "малий GC копіює\nлише ЖИВЕ;\nмертве молоде — 0 роботи", "#e9f7ef"),
    ]
    prev = None
    for (cx, cy), s, fill in a:
        b, w, h = textbox(cx, cy, s, size=12, fill=fill, stroke=FIELD, sw=1.6, min_w=196)
        frags.append(b)
        if prev is not None:
            frags.append(arrow(prev[0] + prev[1] / 2 + 3, ya, cx - w / 2 - 3, ya, color=INK, sw=1.5))
        prev = (cx, w)

    # ── доріжка Б: пульований, тримаємо живим ──
    frags.append(text(W / 2, 300, "Пульований об'єкт — тримаємо живим: годуємо GC найважчим",
                      size=15.5, bold=True, color=POS))
    yb = 400
    b_ = [
        ((165, yb), "народження\n(теж у молодшому)", "#fdf0ea"),
        ((410, yb), "пул тримає\nживим довго", "#fdf0ea"),
        ((690, yb), "підвищення (promotion)\nу старше покоління", "#fdf0ea"),
        ((985, yb), "кожен GC СКАНУЄ\nзнову; запис →\nбар'єр old→young", "#fdf0ea"),
    ]
    prev = None
    for (cx, cy), s, fill in b_:
        b, w, h = textbox(cx, cy, s, size=12, fill=fill, stroke=POS, sw=1.6, min_w=170)
        frags.append(b)
        if prev is not None:
            frags.append(arrow(prev[0] + prev[1] / 2 + 3, yb, cx - w / 2 - 3, yb, color=INK, sw=1.5))
        prev = (cx, w)

    frags.append(text(W / 2, H - 26,
                      "Пул робить дешеве народження обліком, дешеву смерть — підвищенням, і вимикає escape-аналіз",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, 'gc-generations.svg'), W, H, *frags)


# ── (proj-concurrent) Три шари координації: локальний кеш → шард → стек Трейбера ─
def fig_concurrent_layers():
    W, H = 1240, 720
    frags = []
    frags.append(text(W / 2, 40,
                      "Три шари: що менше спільного чіпає гарячий шлях, то краще масштаб",
                      size=16, bold=True, color=INK))

    ys = [180, 300, 420, 540]                       # чотири «доріжки» потоків
    # заголовки колонок (над усіма рядками — лінії арок горизонтальні, тексту не чіпають)
    frags.append(text(180, 96, "ШАР 1", size=13.5, bold=True, color=FIELD))
    frags.append(text(180, 116, "потік + локальний кеш", size=11.5, color=MUTED))
    frags.append(text(590, 96, "ШАР 2", size=13.5, bold=True, color=NEG))
    frags.append(text(590, 116, "шард за ядром", size=11.5, color=MUTED))
    frags.append(text(1010, 96, "ШАР 3", size=13.5, bold=True, color=POS))
    frags.append(text(1010, 116, "стек Трейбера в шарді", size=11.5, color=MUTED))

    # ── Колонка 1: потоки з власними кешами ──
    for i, y in enumerate(ys):
        b, w, h = textbox(180, y, "Потік %d\nлокальний масив" % (i + 1),
                          size=12, bold=True, fill="#e9f7ef", stroke=FIELD, sw=1.7, min_w=214)
        frags.append(b)
    frags.append(text(180, 620, "гарячий шлях — тут:", size=11.5, color=FIELD, bold=True))
    frags.append(text(180, 638, "pop/push у свій масив,", size=11, color=MUTED))
    frags.append(text(180, 654, "0 атоміків, 0 замків", size=11, color=MUTED))

    # ── Колонка 2: шарди ──
    shard_edges = []
    for i, y in enumerate(ys):
        b, w, h = textbox(590, y, "Шард %d\nстек вільних" % (i + 1),
                          size=12, bold=True, fill="#eef2fb", stroke=NEG, sw=1.7, min_w=190)
        frags.append(b)
        shard_edges.append((590 - w / 2, 590 + w / 2, w, h))

    # стрілки кеш → шард (рідкісний БАТЧ), пунктир; горизонтальні, повз заголовки
    for i, y in enumerate(ys):
        frags.append(arrow(180 + 214 / 2 + 4, y, shard_edges[i][0] - 4, y,
                           color=MUTED, sw=1.4))
    frags.append(text((180 + 214 / 2 + 590 - 95) / 2, 150,
                      "лише БАТЧ по 32", size=11, color=MUTED))
    frags.append(text((180 + 214 / 2 + 590 - 95) / 2, 166,
                      "(кеш спорожнів / повний)", size=10.5, color=MUTED))

    # ── Колонка 3: зум одного шарду у стек Трейбера ──
    # ланцюг head → □ → □ → ∅ вертикально
    chain_x = 1010
    node_ys = [200, 300, 400]
    frags.append(text(chain_x, 168, "head", size=12, bold=True, color=POS))
    prev = (chain_x, 178)
    for k, ny in enumerate(node_ys):
        b, w, h = textbox(chain_x, ny, "вільний\nвузол", size=11,
                          fill="#fdecea", stroke=POS, sw=1.5, min_w=110)
        frags.append(b)
        frags.append(arrow(prev[0], prev[1], chain_x, ny - h / 2 - 3, color=POS, sw=1.5))
        prev = (chain_x, ny + h / 2 + 1)
    frags.append(arrow(prev[0], prev[1], chain_x, 470, color=POS, sw=1.5))
    frags.append(text(chain_x, 486, "∅", size=15, bold=True, color=MUTED))
    # підпис механізму — праворуч від ланцюга, у чистій смузі
    frags.append(text(chain_x + 82, 250, "pop/push —", size=11, color=POS, anchor="start"))
    frags.append(text(chain_x + 82, 266, "CAS-цикл на head;", size=11, color=MUTED, anchor="start"))
    frags.append(text(chain_x + 82, 282, "ніхто нікого", size=11, color=MUTED, anchor="start"))
    frags.append(text(chain_x + 82, 298, "не блокує", size=11, color=MUTED, anchor="start"))

    # зум-лінія від шарду 2 до ланцюга
    frags.append(line(shard_edges[1][1] + 4, 300, chain_x - 70, 300,
                      color="#c0c6cf", sw=1.2, dash="5,5"))
    frags.append(text(590, 620, "1 з 32 операцій", size=11.5, color=NEG, bold=True))
    frags.append(text(590, 638, "доходить до шарду —", size=11, color=MUTED))
    frags.append(text(590, 654, "замок або CAS лише тут", size=11, color=MUTED))

    render(os.path.join(IMG, 'concurrent-layers.svg'), W, H, *frags)


# ── (proj-concurrent) Проблема ABA на стеку Трейбера і лагодження лічильником ──
def fig_aba():
    W, H = 1240, 760
    frags = []
    frags.append(text(W / 2, 40, "Проблема ABA: CAS бачить те саме A — та стек уже інший",
                      size=16, bold=True, color=INK))

    def chain(x0, y, labels, hot=None):
        """Маленький ланцюг вузлів зліва направо; hot — індекс, який підсвітити."""
        out = []
        x = x0
        for i, lab in enumerate(labels):
            fill = "#fdecea" if (hot is not None and i == hot) else "#eef2fb"
            stroke = POS if (hot is not None and i == hot) else NEG
            b, w, h = textbox(x + 24, y, lab, size=12, bold=True,
                              fill=fill, stroke=stroke, sw=1.6, min_w=44)
            if i > 0:
                out.append(arrow(x - 6, y, x + 24 - w / 2 - 3, y, color=INK, sw=1.4))
            out.append(b)
            x = x + 24 + w / 2 + 40
        return out, x

    rows = [
        ("Старт. Стек:  head →", ["A", "B", "C"], None, INK, FILL),
        ("Потік 1: прочитав head=A, next=B;\nготує CAS(A→B)… витіснений", ["A", "B", "C"], 0, NEG, "#eef2fb"),
        ("Потік 2: pop A, потім pop B", ["C"], None, POS, "#fdecea"),
        ("Потік 2: reset A, push A назад\n(тепер A.next = C)", ["A", "C"], 0, POS, "#fdecea"),
        ("Потік 1 прокинувся: CAS(head:A→B)\nУСПІХ — head досі ==A!", ["B", "?"], 0, POS, "#fdecea"),
    ]
    ry = [120, 216, 312, 408, 504]
    for (lab, st, hot, col, fill), y in zip(rows, ry):
        b, w, h = textbox(300, y, lab, size=12, bold=False, fill=fill,
                          stroke=col, sw=1.6, min_w=440)
        frags.append(b)
        ch, _ = chain(600, y, st, hot=hot)
        frags += ch
    frags.append(text(870, 504, "→ head→B→(вилучений B) — стек зруйновано",
                      size=11.5, color=POS, anchor="start"))

    # роздільник і панель лагодження
    frags.append(line(90, 560, W - 90, 560, color="#d0d5db", sw=1.2, dash="7,7"))
    fix = ("Лагодження — мічений покажчик (tagged pointer): head = {вказівник, лічильник}.\n"
           "Кожен успішний CAS додає +1 до лічильника. Потік 1 тримає {A, v1}, а зараз уже {A, v3}\n"
           "→ подвійний CAS не збігається за лічильником → безпечний повтор. Інший шлях — hazard pointers.")
    b, w, h = textbox(W / 2, 630, fix, size=12.5, bold=False,
                      fill="#e9f7ef", stroke=FIELD, sw=1.7, min_w=980)
    frags.append(b)

    render(os.path.join(IMG, 'aba-problem.svg'), W, H, *frags)


# ── (proj-concurrent) Хибне сусідство: один рядок кеша vs padding до рядка ─────
def fig_false_sharing():
    W, H = 1180, 560
    frags = []
    frags.append(text(W / 2, 40, "Хибне сусідство: різні змінні на одному рядку кеша труться",
                      size=16, bold=True, color=INK))
    frags.append(line(W / 2, 80, W / 2, H - 60, color="#d0d5db", sw=1.2, dash="7,7"))

    # ── Ліва панель: спільний рядок ──
    frags.append(text(300, 108, "БЕЗ padding — один рядок на двох", size=14, bold=True, color=POS))
    # рядок кеша з двома клітинами
    ln_y = 300
    frags.append(rect(150, ln_y - 34, 300, 68, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    frags.append(text(300, ln_y - 46, "рядок кеша, 64 байти", size=11, color=MUTED))
    b, _, _ = textbox(228, ln_y, "head[0]", size=12, bold=True, fill=BG, stroke=INK, sw=1.3, min_w=110)
    frags.append(b)
    b, _, _ = textbox(372, ln_y, "head[1]", size=12, bold=True, fill=BG, stroke=INK, sw=1.3, min_w=110)
    frags.append(b)
    # два ядра
    b, _, _ = textbox(210, 178, "Ядро 0", size=12, bold=True, fill="#eef2fb", stroke=NEG, sw=1.5, min_w=110)
    frags.append(b)
    b, _, _ = textbox(390, 178, "Ядро 1", size=12, bold=True, fill="#eef2fb", stroke=NEG, sw=1.5, min_w=110)
    frags.append(b)
    frags.append(arrow(210, 198, 228, ln_y - 40, color=NEG, sw=1.5))
    frags.append(arrow(390, 198, 372, ln_y - 40, color=NEG, sw=1.5))
    # пінг-понг рядка між ядрами
    frags.append(arrow(250, 430, 350, 430, color=POS, sw=1.7))
    frags.append(arrow(350, 452, 250, 452, color=POS, sw=1.7))
    frags.append(text(300, 486, "запис у head[0] викидає рядок", size=11.5, color=POS))
    frags.append(text(300, 502, "з кеша Ядра 1 — хоч воно чіпає head[1]", size=11.5, color=POS))

    # ── Права панель: padding ──
    frags.append(text(880, 108, "З padding — кожен head на своєму рядку", size=14, bold=True, color=FIELD))
    for k, cx in enumerate([760, 1000]):
        frags.append(rect(cx - 96, ln_y - 34, 192, 68, fill="#e9f7ef", stroke=FIELD, sw=1.8, rx=8))
        b, _, _ = textbox(cx - 26, ln_y, "head[%d]" % k, size=12, bold=True, fill=BG, stroke=INK, sw=1.3, min_w=104)
        frags.append(b)
        frags.append(text(cx + 58, ln_y, "pad", size=10.5, color=MUTED))
        b, _, _ = textbox(cx, 178, "Ядро %d" % k, size=12, bold=True, fill="#eef2fb", stroke=NEG, sw=1.5, min_w=104)
        frags.append(b)
        frags.append(arrow(cx, 198, cx, ln_y - 40, color=NEG, sw=1.5))
    frags.append(text(880, 486, "різні рядки → запис одного ядра", size=11.5, color=FIELD))
    frags.append(text(880, 502, "не чіпає кеш іншого: 0 хибних інвалідацій", size=11.5, color=FIELD))

    render(os.path.join(IMG, 'false-sharing.svg'), W, H, *frags)


# ── (math) Закон Літтла: доказ «порахуй площу двома способами» (sample-path) ───
def fig_little_area():
    W, H = 1120, 640
    frags = []
    x0, x1 = 150, 980
    axis_y = 520
    top = 150

    # осі
    frags.append(arrow(x0, axis_y, x1 + 12, axis_y, color=INK, sw=2))
    frags.append(text(x1 + 8, axis_y + 26, "час t", size=12, color=MUTED, anchor="end"))

    def tx(t):  # час 0..10 → піксель
        return x0 + (t / 10.0) * (x1 - x0)

    # шість запитів як горизонтальні смуги (кожна тримає об'єкт Wᵢ секунд)
    cust = [(0.5, 3.0), (1.4, 4.2), (2.3, 5.2), (3.5, 6.1), (4.6, 7.5), (5.9, 8.7)]
    rows = [455, 403, 351, 299, 247, 195]   # знизу вгору
    bh = 26
    for i, ((a, d), yc) in enumerate(zip(cust, rows)):
        frags.append(rect(tx(a), yc - bh / 2, tx(d) - tx(a), bh,
                          fill="#eaf0fd", stroke=NEG, sw=1.5, rx=5))
        frags.append(text(x0 - 14, yc + 4, "запит %d" % (i + 1),
                          size=11, color=MUTED, anchor="end"))

    # вертикаль у мить t* — скільки смуг вона перетинає, стільки об'єктів зайнято
    tstar = 3.8
    frags.append(line(tx(tstar), top + 6, tx(tstar), axis_y - 2,
                      color=POS, sw=1.7, dash="5,5"))
    frags.append(text(tx(tstar), 176, "t*", size=13, bold=True, color=POS))
    frags.append(text(tx(tstar), axis_y + 22, "мить t*", size=11, color=POS))
    # підпис «N(t*)=3» — праворуч від вертикалі, у порожнечі над смугами
    frags.append(text(tx(tstar) + 152, 300, "у мить t* зайнято",
                      size=12, color=POS))
    frags.append(text(tx(tstar) + 152, 318, "3 об'єкти → N(t*) = 3",
                      size=12, bold=True, color=POS))

    # ширину однієї смуги (запит 1) підписати як Wᵢ — знизу, у вільній смузі
    a1, d1 = cust[0]
    frags.append(line(tx(a1), 486, tx(d1), 486, color=FIELD, sw=1.5))
    frags.append(line(tx(a1), 482, tx(a1), 490, color=FIELD, sw=1.5))
    frags.append(line(tx(d1), 482, tx(d1), 490, color=FIELD, sw=1.5))
    frags.append(text((tx(a1) + tx(d1)) / 2, 504, "Wᵢ — час утримання",
                      size=11, color=FIELD))

    # два тлумачення площі + висновок
    bV, _, _ = textbox(322, 96, "рахуємо ВВИСЬ (по вертикалях):\n∫ N(t) dt = L · T",
                       size=12.5, fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=300)
    frags.append(bV)
    bH, _, _ = textbox(802, 96, "рахуємо ВШИР (по смугах):\nΣ Wᵢ = сума часів утримання",
                       size=12.5, fill="#e8f6ee", stroke=FIELD, sw=1.6, min_w=320)
    frags.append(bH)
    bC, _, _ = textbox(W / 2, 582,
                       "та сама площа:  Σ Wᵢ = L · T,  а Σ Wᵢ = (λT) · W   ⟹   L = λ · W",
                       size=13.5, bold=True, fill=FILL, stroke=INK, sw=1.8, min_w=300)
    frags.append(bC)

    frags.append(text(W / 2, 40,
                      "Одну площу рахуємо двома способами — і випадає L = λW",
                      size=16, bold=True, color=INK))
    render(os.path.join(IMG, 'little-area.svg'), W, H, *frags)


# ── (math) Чутливість break-even до вартості скидання: N* = 1/(1−f) ───────────
def fig_break_even():
    W, H = 1100, 600
    frags = []
    x0, x1 = 170, 970
    ybase, ytop = 520, 110
    NMAX = 16.0

    # осі
    frags.append(arrow(x0, ybase, x1 + 30, ybase, color=INK, sw=2))
    frags.append(arrow(x0, ybase, x0, ytop - 8, color=INK, sw=2))
    frags.append(text(x1 + 26, ybase + 30, "f = C_reset ⁄ C_new →", size=12.5, color=MUTED, anchor="end"))
    frags.append(text(x0 - 6, ytop - 4, "N* — використань до окупності", size=12.5, color=MUTED, anchor="start"))

    def px(f): return x0 + f * (x1 - x0)
    def py(n): return ybase - (min(n, NMAX) / NMAX) * (ybase - ytop)

    # крива N* = 1/(1−f)
    pts = []
    f = 0.0
    while f <= 0.941:
        pts.append((px(f), py(1.0 / (1.0 - f))))
        f += 0.015
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, NEG))

    # вертикальна асимптота f→1
    frags.append(line(px(0.9375), ybase, px(0.9375), ytop + 16, color=POS, sw=1.4, dash="6,6"))
    frags.append(text(px(0.9375) - 12, 150, "f → 1:", size=12.5, bold=True, color=POS, anchor="end"))
    frags.append(text(px(0.9375) - 12, 168, "C_reset → C_new,", size=12, color=POS, anchor="end"))
    frags.append(text(px(0.9375) - 12, 186, "N* → ∞", size=12.5, bold=True, color=POS, anchor="end"))

    # позначені точки з винесеними підписами (у чистих зонах)
    def dot(f):
        n = 1.0 / (1.0 - f)
        frags.append(circle(px(f), py(n), 6, fill="#eaf0fd", stroke=NEG, sw=2.4))
    dot(0.0); dot(0.5); dot(0.9)
    b, _, _ = textbox(360, 250, "f = 0.5: скидання = ½ народження\n→ окупність за 2 використання",
                      size=11.5, fill=FILL, stroke=MUTED, sw=1.3, min_w=300)
    frags.append(b)
    b, _, _ = textbox(690, 200, "f = 0.9: скидання = 0.9 народження\n→ аж 10 використань",
                      size=11.5, fill=FILL, stroke=MUTED, sw=1.3, min_w=300)
    frags.append(b)
    frags.append(text(px(0.5), py(2.0) + 26, "2", size=11.5, bold=True, color=NEG))
    frags.append(text(px(0.9) - 12, py(10.0), "10", size=11.5, bold=True, color=NEG, anchor="end"))

    # приклад із з'єднанням — біля лівого краю
    frags.append(text(px(0.02) + 6, py(1.0) + 34, "з'єднання: f ≈ 0.02 → N* ≈ 1 (пул виграє миттєво)",
                      size=11.5, color=FIELD, anchor="start"))

    frags.append(text(W / 2, 42,
                      "Що дорожче скидання (f), то довше об'єкт має служити, щоб пул окупив дороге народження",
                      size=14, bold=True, color=INK))
    render(os.path.join(IMG, 'break-even.svg'), W, H, *frags)


# ── (math) Ерланг C: розмір пулу збиває ймовірність очікування (a = λW = 5) ────
def fig_erlang_c():
    W, H = 1100, 600
    frags = []
    x0, x1 = 185, 950
    ybase, ytop = 505, 120
    cmin, cmax = 4, 12

    def erlang_c(c, a):
        B = 1.0
        for k in range(1, c + 1):
            B = a * B / (k + a * B)
        if a / c >= 1:
            return 1.0
        return c * B / (c - a + a * B)

    def px(c): return x0 + (c - cmin) / float(cmax - cmin) * (x1 - x0)
    def py(p): return ybase - p * (ybase - ytop)

    # осі
    frags.append(arrow(x0, ybase, x1 + 20, ybase, color=INK, sw=2))
    frags.append(arrow(x0, ybase, x0, ytop - 8, color=INK, sw=2))
    frags.append(text(x1 + 4, ybase + 32, "розмір пулу c →", size=12.5, color=MUTED, anchor="end"))
    frags.append(text(x0 - 8, ytop - 4, "P(очікування)", size=12.5, color=MUTED, anchor="start"))

    # підлога a = λW = 5 (при c ≤ 5 система нестабільна)
    frags.append(line(px(5), ybase, px(5), ytop + 8, color=POS, sw=1.5, dash="6,6"))
    frags.append(text(px(5) - 10, 168, "підлога a = λW = 5", size=12, bold=True, color=POS, anchor="end"))
    frags.append(text(px(5) - 10, 186, "c ≤ 5 → ρ ≥ 1: нестабільно", size=11, color=POS, anchor="end"))

    # ціль ≤ 10%
    frags.append(line(px(6), py(0.1), x1, py(0.1), color=FIELD, sw=1.4, dash="5,5"))
    frags.append(text(x1 - 4, py(0.1) - 9, "ціль: P(очікування) ≤ 10%", size=11.5, color=FIELD, anchor="end"))

    # крива P_wait по цілих c
    a = 5.0
    vals = [(c, erlang_c(c, a)) for c in range(5, cmax + 1)]
    poly = " ".join("%.1f,%.1f" % (px(c), py(p)) for c, p in vals)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, NEG))
    for c, p in vals:
        hot = (c == 9)
        frags.append(circle(px(c), py(p), 6 if hot else 4.5,
                            fill=("#e8f6ee" if hot else "#eaf0fd"),
                            stroke=(FIELD if hot else NEG), sw=2.2))
        lab = ("%.0f%%" % (p * 100)) if p >= 0.095 else ("%.1f%%" % (p * 100))
        frags.append(text(px(c) + (14 if c == 5 else 0), py(p) - 15, lab,
                          size=11.5, color=(FIELD if hot else INK), bold=hot,
                          anchor="middle"))
        frags.append(text(px(c), ybase + 22, "%d" % c, size=11.5, color=MUTED))

    # виноска на c=9 — перший під ціллю (у чистій зоні вгорі-праворуч)
    b, _, _ = textbox(812, 300, "c = 9 → 8%: перший розмір\nпід ціллю. Запас c − a = 4",
                      size=11.5, fill="#e8f6ee", stroke=FIELD, sw=1.4, min_w=250)
    frags.append(b)

    frags.append(text(W / 2, 46,
                      "Ерланг C: кожен доданий об'єкт понад підлогу різко збиває ймовірність очікування",
                      size=14, bold=True, color=INK))
    render(os.path.join(IMG, 'erlang-c.svg'), W, H, *frags)


# ── Слаб: суміжні сторінки, поділені на однакові клітини ──────────────────────
def fig_slab_anatomy():
    W, H = 1200, 560
    frags = []

    # три суміжні сторінки згори
    frags.append(text(W / 2, 54, "три суміжні сторінки з кеша сторінок ядра",
                      size=13, color=MUTED))
    px0, px1 = 110, 1090
    pw = (px1 - px0) / 3.0
    for i in range(3):
        x = px0 + i * pw
        frags.append(rect(x, 66, pw, 46, fill="#eef4fd", stroke=NEG, sw=1.4, rx=4))
        frags.append(text(x + pw / 2, 94, "сторінка", size=13, color=NEG))

    # стрілка «поділені на клітини»
    frags.append(arrow(600, 118, 600, 168, color=LINE, sw=1.6))
    frags.append(text(618, 146, "та сама памʼять, порізана на однакові клітини",
                      size=12.5, color=INK, anchor="start"))

    # слаб
    sx, sy, sw_, sh = 110, 178, 980, 150
    frags.append(rect(sx, sy, sw_, sh, fill="#fbfbfd", stroke=INK, sw=2, rx=8))

    # смуга «фарби» на початку
    col_w = 40
    frags.append(rect(sx, sy, col_w, sh, fill="#efe9f6", stroke="#8e44ad", sw=1.2, rx=0))
    frags.append(text(sx + col_w / 2, sy + sh + 20, "фарба", size=11.5, color="#8e44ad"))

    # 6 клітин
    cells_x0 = sx + col_w
    n = 6
    cw = 140
    states = [("готовий", FIELD, "#e8f6ee"),
              ("готовий", FIELD, "#e8f6ee"),
              ("виданий", POS, "#fdecea"),
              ("готовий", FIELD, "#e8f6ee"),
              ("виданий", POS, "#fdecea"),
              ("готовий", FIELD, "#e8f6ee")]
    for i, (st, col, fill) in enumerate(states):
        cx = cells_x0 + i * cw
        frags.append(fitbox(cx + 6, sy + 18, cw - 14, sh - 36,
                            "обʼєкт №%d\n%s" % (i, st),
                            size=13, fill=fill, stroke=col, sw=1.5, color=INK))

    # решта наприкінці
    rest_x = cells_x0 + n * cw
    rest_w = (sx + sw_) - rest_x
    if rest_w > 6:
        frags.append(rect(rest_x, sy, rest_w, sh, fill="#f1f1f4", stroke=MUTED, sw=1.1, rx=0))
        frags.append(text(rest_x + rest_w / 2, sy + sh + 20, "решта", size=11.5, color=MUTED))

    # підписи-суть
    frags.append(text(W / 2, sy + sh + 48,
                      "Вільні клітини зчеплені у вбудований список — окремих таблиць обліку нема.",
                      size=12.5, color=INK))
    frags.append(text(W / 2, sy + sh + 72,
                      "Кожна готова клітина вже містить сконструйований обʼєкт: стан збережено між використаннями.",
                      size=12.5, color=FIELD, italic=True))

    render(os.path.join(IMG, 'slab-anatomy.svg'), W, H, *frags,
           title="Слаб: суміжні сторінки, поділені на однакові клітини")


# ── Розфарбування слабів: дрібний зсув розкидає обʼєкти по рядках кеша ─────────
def fig_slab_coloring():
    W, H = 1200, 600
    frags = []

    frags.append(text(300, 84, "три слаби одного кеша", size=13.5, bold=True, color=INK))
    frags.append(text(930, 84, "рядки кеша процесора", size=13.5, bold=True, color=INK))

    # рядки кеша (лінійка) праворуч
    ruler_x, ruler_w = 780, 300
    line_h, line_gap, line_y0 = 56, 24, 108
    line_centers = []
    for L in range(5):
        y = line_y0 + L * (line_h + line_gap)
        line_centers.append(y + line_h / 2)
        used = L < 3
        fill = "#eef4fd" if used else "#f6f6f8"
        frags.append(rect(ruler_x, y, ruler_w, line_h,
                          fill=fill, stroke=NEG if used else MUTED, sw=1.4, rx=5))
        frags.append(text(ruler_x + ruler_w / 2, y + line_h / 2 + 5, "рядок кеша %d" % L,
                          size=13, color=INK if used else MUTED))

    # три слаби ліворуч зі зростаючим зсувом
    slab_x0, off_unit = 150, 46
    for i in range(3):
        rc = line_centers[i]
        oi = i * off_unit
        strip_y = rc - 34
        frags.append(text(70, rc + 4, "слаб %d" % (i + 1), size=12.5, color=MUTED, anchor="start"))
        if oi > 0:
            frags.append(rect(slab_x0, strip_y, oi, 68, fill="#efe9f6", stroke="#8e44ad", sw=1.1, rx=3))
        c0x = slab_x0 + oi
        frags.append(rect(c0x, strip_y, 120, 68, fill="#fdf0e6", stroke=POS, sw=1.6, rx=5))
        frags.append(text(c0x + 60, rc + 5, "обʼєкт №0", size=12.5, color=POS))
        for k in range(2):
            cx = c0x + 120 + k * 70
            frags.append(rect(cx, strip_y, 66, 68, fill="#f4f6f8", stroke=MUTED, sw=1.1, rx=4))
        ax = c0x + 120 + 2 * 70
        frags.append(arrow(ax + 6, rc, ruler_x - 4, line_centers[i], color="#8e44ad", sw=1.7))

    frags.append(text(300, 522, "нульовий зсув · +1 рядок · +2 рядки — «фарба» з решти слаба",
                      size=12, color="#8e44ad"))
    frags.append(text(W / 2, 558,
                      "Без фарбування кожен слаб почався б із нуля — і обʼєкт №0 усіх слабів бив би в ОДИН рядок; дрібний зсув їх розкидає.",
                      size=12.5, color=INK, italic=True))

    render(os.path.join(IMG, 'slab-coloring.svg'), W, H, *frags,
           title="Розфарбування: дрібний зсув розкидає обʼєкти по рядках кеша")


# ── Родовід слаба: у Linux, FreeBSD, illumos ─────────────────────────────────
def fig_slab_lineage():
    W, H = 1200, 620
    frags = []

    root_cx, root_cy = 620, 96
    rb, rw, rh = textbox(root_cx, root_cy,
                         "Слаб-розподільник Джефа Бонвіка\n"
                         "SunOS 5.4 (Solaris 2.4) · USENIX Summer 1994",
                         size=13.5, bold=True, fill="#fff7e6", stroke="#b8860b", sw=2, min_w=520)
    frags.append(rb)

    # рейка-розподільник
    rail_y = 210
    child_cx = [180, 470, 780, 1055]
    frags.append(line(root_cx, root_cy + rh / 2, root_cx, rail_y, color=LINE, sw=1.6))
    frags.append(line(child_cx[0], rail_y, child_cx[-1], rail_y, color=LINE, sw=1.6))
    for cx in child_cx:
        frags.append(arrow(cx, rail_y, cx, 250, color=LINE, sw=1.6))

    # 1) illumos — живий прямий нащадок (зелений)
    b, _, _ = textbox(child_cx[0], 286,
                      "illumos\nkmem — прямий нащадок\nOpenSolaris, живий досі",
                      size=12.5, fill="#e8f6ee", stroke=FIELD, sw=1.7, min_w=210)
    frags.append(b)

    # 2) Linux — субланцюг SLAB → SLUB → 2024
    lx = child_cx[1]
    b, _, h1 = textbox(lx, 282, "Linux: SLAB\nМарк Гемент, 1996",
                       size=12.5, fill="#eef4fd", stroke=NEG, sw=1.6, min_w=210)
    frags.append(b)
    b, _, h2 = textbox(lx, 372, "SLUB\nКрістоф Ламетер, 2007",
                       size=12.5, fill="#eef4fd", stroke=NEG, sw=1.6, min_w=210)
    frags.append(b)
    b, _, h3 = textbox(lx, 462, "2024: SLAB прибрано,\nлишився SLUB",
                       size=12, fill="#f4f6f8", stroke=MUTED, sw=1.4, min_w=210)
    frags.append(b)
    frags.append(arrow(lx, 282 + h1 / 2 + 2, lx, 372 - h2 / 2 - 2, color=NEG, sw=1.5))
    frags.append(arrow(lx, 372 + h2 / 2 + 2, lx, 462 - h3 / 2 - 2, color=NEG, sw=1.5))

    # 3) FreeBSD — UMA (синій)
    b, _, _ = textbox(child_cx[2], 286,
                      "FreeBSD: UMA\n(universal memory allocator)\nДжефф Роберсон, ~2002",
                      size=12.5, fill="#eef4fd", stroke=NEG, sw=1.7, min_w=210)
    frags.append(b)

    # 4) Magazines & Vmem — розвиток самого автора (фіолетовий)
    b, _, _ = textbox(child_cx[3], 286,
                      "Magazines & Vmem\nБонвік і Адамс, 2001\nмасштаб на багато CPU",
                      size=12.5, fill="#efe9f6", stroke="#8e44ad", sw=1.7, min_w=210)
    frags.append(b)

    # легенда
    ly = 556
    frags.append(rect(150, ly - 12, 16, 16, fill="#e8f6ee", stroke=FIELD, sw=1.4, rx=3))
    frags.append(text(174, ly + 1, "живий прямий нащадок", size=12, color=INK, anchor="start"))
    frags.append(rect(470, ly - 12, 16, 16, fill="#eef4fd", stroke=NEG, sw=1.4, rx=3))
    frags.append(text(494, ly + 1, "перенесено в інше ядро", size=12, color=INK, anchor="start"))
    frags.append(rect(800, ly - 12, 16, 16, fill="#efe9f6", stroke="#8e44ad", sw=1.4, rx=3))
    frags.append(text(824, ly + 1, "продовження самого Бонвіка", size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, 'slab-lineage.svg'), W, H, *frags,
           title="Родовід слаба: з ядра SunOS — у Linux, FreeBSD, illumos")


if __name__ == '__main__':
    fig_borrow_return()
    fig_timeline()
    fig_size_optimum()
    fig_lifecycle()
    fig_gc_generations()
    fig_concurrent_layers()
    fig_aba()
    fig_false_sharing()
    fig_little_area()
    fig_break_even()
    fig_erlang_c()
    fig_slab_anatomy()
    fig_slab_coloring()
    fig_slab_lineage()
    print("figs done")
