# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Кістяк стратегії: контекст → інтерфейс → взаємозамінні реалізації ─────────
def fig_strategy_structure():
    W, H = 1040, 600
    frags = []

    frags.append(text(W / 2, 40, "Кістяк стратегії", size=18, bold=True, color=INK))
    frags.append(text(W / 2, 62, "контекст делегує через інтерфейс, не знаючи реалізації",
                      size=12.5, color=MUTED))

    # ── Контекст (ліворуч) ───────────────────────────────────────────────────
    ctx_cx = W * 0.20
    ctx_cy = 210
    ctx, cw, ch = textbox(ctx_cx, ctx_cy,
                          ["Order  (контекст)",
                           "policy: DiscountPolicy",
                           "finalPrice():",
                           "  total − policy.discount(this)"],
                          size=12.5, bold=False, fill="#eaf0fd", stroke=NEG,
                          sw=1.8, min_w=290)
    frags.append(ctx)
    frags.append(text(ctx_cx, ctx_cy + ch / 2 + 26,
                      "тримає ОДНЕ поле-стратегію", size=12, color=INK))
    frags.append(text(ctx_cx, ctx_cy + ch / 2 + 46,
                      "і делегує йому роботу", size=12, color=INK))

    # ── Інтерфейс стратегії (центр угорі) ────────────────────────────────────
    iface_cx = W * 0.62
    iface_cy = 150
    iface, iw, ih = textbox(iface_cx, iface_cy,
                            ["«interface» DiscountPolicy",
                             "discount(order): number"],
                            size=12.5, bold=True, fill="#e8f6ee", stroke=FIELD,
                            sw=1.8, min_w=280)
    frags.append(iface)

    # контекст --залежить від--> інтерфейс (пунктир)
    frags.append(line(ctx_cx + cw / 2, ctx_cy - ch / 2 + 18,
                      iface_cx - iw / 2, iface_cy, color=NEG, sw=1.5, dash="5,5"))
    frags.append(text((ctx_cx + cw / 2 + iface_cx - iw / 2) / 2 - 4,
                      iface_cy - 28, "залежить лише", size=11, color=MUTED))
    frags.append(text((ctx_cx + cw / 2 + iface_cx - iw / 2) / 2 - 4,
                      iface_cy - 12, "від інтерфейсу", size=11, color=MUTED))

    # ── Три конкретні стратегії (праворуч, стовпчик) ─────────────────────────
    impls = [
        ("NoDiscount", "return 0", 300),
        ("VipDiscount", "total × 0.20", 400),
        ("SeasonalDiscount(rate)", "total × rate", 500),
    ]
    impl_cx = W * 0.62
    box_min_w = 280
    box_left = impl_cx - box_min_w / 2          # ліва грань стовпчика рамок
    rail_x = box_left - 30                       # вертикальна «рейка» реалізацій ліворуч
    top_iy = impls[0][2]                         # y верхньої рамки-реалізації
    bot_iy = impls[-1][2]                        # y нижньої рамки-реалізації
    for name, body, iy in impls:
        b, bw, bh = textbox(impl_cx, iy, [name, body],
                            size=12, bold=False, fill=FILL, stroke=LINE,
                            sw=1.4, min_w=box_min_w)
        frags.append(b)
        # горизонтальна поличка від лівого краю рамки до рейки
        frags.append(line(box_left, iy, rail_x, iy, color=FIELD, sw=1.3))
    # спільна рейка вздовж стовпчика й одна стрілка вгору до інтерфейсу
    frags.append(line(rail_x, bot_iy, rail_x, top_iy, color=FIELD, sw=1.3))
    frags.append(arrow(rail_x, top_iy, rail_x, iface_cy + ih / 2 + 2,
                       color=FIELD, sw=1.3))

    frags.append(text(impl_cx + 172, 400,
                      "взаємозамінні", size=12.5, bold=True, color=FIELD, anchor="start"))
    frags.append(text(impl_cx + 172, 420,
                      "реалізації", size=12.5, bold=True, color=FIELD, anchor="start"))
    frags.append(text(impl_cx + 172, 444,
                      "одна операція —", size=11, color=MUTED, anchor="start"))
    frags.append(text(impl_cx + 172, 460,
                      "кожна по-своєму", size=11, color=MUTED, anchor="start"))

    # ── Нижня плашка: підстановка ────────────────────────────────────────────
    band_y = H - 46
    frags.append(line(40, band_y - 20, W - 40, band_y - 20, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, band_y,
                      "setPolicy(інша) → контекст поводиться інакше, його код НЕ змінюється",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'strategy-structure.svg'), W, H, *frags)


# ── Спільне — вбік як інструмент, не вгору як предок ──────────────────────────
def fig_common_code_sideways():
    W, H = 1040, 560
    frags = []

    frags.append(text(W / 2, 38, "Спільне — вбік як інструмент, не вгору як предок",
                      size=18, bold=True, color=INK))
    frags.append(text(W / 2, 60, "стратегії рівні; помічник кличуть за потреби",
                      size=12.5, color=MUTED))

    # ── Чотири рівні стратегії (ліворуч, колонка) ────────────────────────────
    strat_cx = W * 0.26
    strat_w = 300
    calls = {"FlatRate": True, "ZonalRate": False,
             "FreeOverThreshold": True, "CourierRate": False}
    ys = [140, 240, 340, 440]
    right_edges = []
    for (name, cost), y in zip(
            [("FlatRate", "50 + вага·10"),
             ("ZonalRate", "40 + зона·25"),
             ("FreeOverThreshold", "поріг; 60 + вага·8"),
             ("CourierRate", "80 + віддаль·1.5")], ys):
        b, bw, bh = textbox(strat_cx, y, [name, cost],
                            size=12, bold=False, fill=FILL, stroke=LINE,
                            sw=1.4, min_w=strat_w)
        frags.append(b)
        right_edges.append((strat_cx + bw / 2, y))
    frags.append(text(strat_cx, ys[0] - 62,
                      "усі на одному рівні —", size=11.5, color=MUTED))
    frags.append(text(strat_cx, ys[0] - 46,
                      "жодна не предок жодній", size=11.5, color=MUTED))

    # ── Помічник (праворуч) ──────────────────────────────────────────────────
    help_cx = W * 0.74
    help_cy = 240
    hb, hw, hh = textbox(help_cx, help_cy,
                         ["weightFee(база, вага, ставка)",
                          "= база + вага · ставка"],
                         size=12.5, bold=True, fill="#e8f6ee", stroke=FIELD,
                         sw=1.8, min_w=300)
    frags.append(hb)
    frags.append(text(help_cx, help_cy - hh / 2 - 16,
                      "помічник ВБІК", size=12.5, bold=True, color=FIELD))

    # стрілки-виклики лише від тих, хто кличе (Flat, FreeOver)
    help_left = help_cx - hw / 2
    for (rx, ry), (name, does) in zip(right_edges, calls.items()):
        if does:
            frags.append(arrow(rx + 4, ry, help_left - 4, ry,
                               color=FIELD, sw=1.6))
    # підписи — у міжрядкові проміжки, де стрілок НЕ проходить (190, 290)
    frags.append(text((strat_cx + help_cx) / 2, 192,
                      "кличуть", size=11.5, bold=True, color=FIELD))
    frags.append(text((strat_cx + help_cx) / 2, 292,
                      "не кличуть — своя формула", size=11, color=MUTED))

    # ── Нижня плашка: вбік проти вгору (два рядки, без ліній крізь текст) ─────
    frags.append(line(40, H - 78, W - 40, H - 78, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 52,
                      "✓  вбік як інструмент — пропонує послугу", size=13.5,
                      bold=True, color=FIELD, anchor="middle"))
    frags.append(text(W / 2, H - 26,
                      "✗  вгору як предок — нав'язав би форму (тому відкинуте)",
                      size=13, color=POS, anchor="middle"))

    render(os.path.join(IMG, 'common-code-sideways.svg'), W, H, *frags)


# ── Додати варіант: switch (хірургія) проти стратегії (дописування) ──────────
def fig_add_variant_diff():
    W, H = 1040, 600
    frags = []

    frags.append(text(W / 2, 38, "Додати нову службу: два способи",
                      size=18, bold=True, color=INK))
    frags.append(text(W / 2, 60, "що доведеться чіпнути з наявного",
                      size=12.5, color=MUTED))

    # ── Ліва колонка: switch — усе червоне ───────────────────────────────────
    lx = W * 0.25
    frags.append(text(lx, 96, "switch", size=15, bold=True, color=POS))
    # великий блок методу, підсвічений увесь
    mb_w, mb_h = 340, 300
    mb_x, mb_y = lx - mb_w / 2, 118
    frags.append(rect(mb_x, mb_y, mb_w, mb_h, fill="#fdecea", stroke=POS, sw=2))
    frags.append(mtext(lx, mb_y + 34,
                       ["shippingCost() {",
                        "  switch (carrier) {",
                        "    case flat:      …",
                        "    case zonal:     …",
                        "    case free_over: …",
                        "    case courier:   …",
                        "    case postal:    …  ← новий",
                        "  }",
                        "}"],
                       size=12.5, color=INK, lh=1.32))
    frags.append(text(lx, mb_y + mb_h + 26,
                      "відкрити й перечитати ВЕСЬ метод", size=12, color=POS))
    frags.append(text(lx, mb_y + mb_h + 44,
                      "ризик зачепити сусідні гілки", size=11.5, color=MUTED))

    # ── Права колонка: стратегія — наявне сіре, нове зелене ───────────────────
    rx = W * 0.72
    frags.append(text(rx, 96, "стратегія + мапа", size=15, bold=True, color=FIELD))

    # наявні стратегії + метод — сірі, недоторкані
    grey = "#e9ecef"
    ex_y = 118
    exb, exw, exh = textbox(rx, ex_y + 44,
                            ["FlatRate · ZonalRate",
                             "FreeOverThreshold · CourierRate",
                             "shippingCost(): table[carrier].cost()"],
                            size=12, bold=False, fill=grey, stroke="#adb5bd",
                            sw=1.4, min_w=340)
    frags.append(exb)
    frags.append(text(rx, ex_y + 12, "наявне — НЕ чіпаємо", size=12,
                      color=MUTED, bold=True))

    # нове — два зелені шматки
    n1_y = ex_y + 150
    n1, n1w, n1h = textbox(rx - 78, n1_y, ["class PostalRate", "→ cost(s)"],
                           size=12, bold=False, fill="#e8f6ee", stroke=FIELD,
                           sw=1.8, min_w=180)
    frags.append(n1)
    n2, n2w, n2h = textbox(rx + 108, n1_y, ['мапа: postal →', 'new PostalRate()'],
                           size=12, bold=False, fill="#e8f6ee", stroke=FIELD,
                           sw=1.8, min_w=210)
    frags.append(n2)
    frags.append(text(rx, n1_y + 62, "нове — клас збоку + один рядок",
                      size=12, bold=True, color=FIELD))
    frags.append(text(rx, n1_y + 82, "наявне лишилось недоторканим",
                      size=11.5, color=MUTED))

    # ── Нижня плашка ─────────────────────────────────────────────────────────
    band_y = H - 40
    frags.append(line(40, band_y - 24, W - 40, band_y - 24, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, band_y,
                      "те саме додавання: хірургія в наявному  проти  дописування збоку",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'add-variant-diff.svg'), W, H, *frags)


# ── Історія: три доріжки сходяться в одну ідею, далі — два рівні підстановки ──
def fig_hist_convergence():
    W, H = 1120, 640
    frags = []

    frags.append(text(W / 2, 38, "Одна ідея — багато імен", size=18, bold=True, color=INK))
    frags.append(text(W / 2, 60,
                      "сталий контекст  +  взаємозамінний змінний алгоритм",
                      size=12.5, color=MUTED))

    # ── Три історичні доріжки ліворуч (стовпчик) ─────────────────────────────
    tracks = [
        ("Lisp / ML  (з 1958)", "функція — це значення;", "передай функцію-порівнювач", 150),
        ("C  qsort  (ANSI 1989)", "вказівник на функцію;", "стан — окремим аргументом", 270),
        ("GoF Strategy  (1994)", "поведінка — об'єкт;", "підстав іншу реалізацію", 390),
    ]
    tx = 215                       # центр доріжок по X
    tbw = 350                      # спільна ширина рамок доріжок
    hub_x = W * 0.60
    hub_y = 270
    for title, l1, l2, ty in tracks:
        b, bw, bh = textbox(tx, ty, [title, l1, l2],
                            size=12, bold=False, fill="#eaf0fd", stroke=NEG,
                            sw=1.6, min_w=tbw)
        # стрілку креслимо до вузла ПЕРЕД рамкою, щоб напис лежав поверх лінії
        frags.append(arrow(tx + tbw / 2 + 4, ty, hub_x - 156, hub_y,
                           color=MUTED, sw=1.6))
        frags.append(b)

    # ── Вузол «одна ідея» (центр) ────────────────────────────────────────────
    hub, hw, hh = textbox(hub_x, hub_y,
                          ["ОДНА ІДЕЯ:", "спосіб дії — окрема річ,",
                           "яку носять і підставляють"],
                          size=13, bold=True, fill="#e8f6ee", stroke=FIELD,
                          sw=2.0, min_w=300)
    frags.append(hub)

    # ── Два рівні підстановки (праворуч, під вузлом) ──────────────────────────
    lvl_x = W * 0.60
    top_b, tw2, th2 = textbox(lvl_x, 460,
                              ["РАНТАЙМ — стратегія", "поведінка = об'єкт у полі",
                               "вибір під час роботи · можна змінити"],
                              size=11.5, bold=False, fill=FILL, stroke=LINE,
                              sw=1.4, min_w=380)
    bot_b, bw2, bh2 = textbox(lvl_x, 575,
                              ["КОМПАЙЛ-ТАЙМ — політика", "поведінка = тип-параметр",
                               "вибір до запуску · нуль коштує в рантаймі"],
                              size=11.5, bold=False, fill=FILL, stroke=LINE,
                              sw=1.4, min_w=380)
    # від вузла вниз до верхнього рівня, далі рискою до нижнього
    frags.append(arrow(hub_x, hub_y + hh / 2, lvl_x, 460 - th2 / 2, color=FIELD, sw=1.5))
    frags.append(top_b)
    frags.append(line(lvl_x, 460 + th2 / 2, lvl_x, 575 - bh2 / 2, color=FIELD, sw=1.3))
    frags.append(bot_b)

    # підпис-місток праворуч від двох рівнів (поза рамками)
    note_x = lvl_x + tw2 / 2 + 22
    frags.append(text(note_x, 500, "різні лише", size=11.5, color=MUTED, anchor="start"))
    frags.append(text(note_x, 518, "механізм і час", size=11.5, color=MUTED, anchor="start"))
    frags.append(text(note_x, 542, "підстановки —", size=11.5, color=MUTED, anchor="start"))
    frags.append(text(note_x, 560, "суть та сама", size=11.5, bold=True, color=FIELD, anchor="start"))

    render(os.path.join(IMG, 'hist-convergence.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_strategy_structure()
    fig_common_code_sideways()
    fig_add_variant_diff()
    fig_hist_convergence()
    print("figs done")
