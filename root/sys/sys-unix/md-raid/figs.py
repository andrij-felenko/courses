# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
RED_FILL = "#fdecea"
GREY_FILL = "#eceff1"


# ── 1. Розкладка RAID5: смуги, обертання парності, відновлення ──────────────
def fig_stripe_and_parity():
    W, H = 1300, 730
    p = []

    disks = ["sdb", "sdc", "sdd", "sde", "sdf"]
    col_w, gap = 200, 12
    col_x = [210 + i * (col_w + gap) for i in range(5)]

    for x, d in zip(col_x, disks):
        p.append(text(x + col_w / 2, 82, d, size=14, bold=True))

    # left-symmetric: парність у смузі s стоїть на носії (4 − s), дані йдуть далі по колу
    rows = []
    d_no = 0
    for s in range(4):
        par = 4 - s
        cells = [None] * 5
        cells[par] = ("P%d" % s, WARM_FILL)
        for k in range(4):
            col = (par + 1 + k) % 5
            cells[col] = ("D%d" % d_no, BLUE_FILL)
            d_no += 1
        rows.append(cells)

    row_h, row_gap = 74, 16
    row_y = [104 + i * (row_h + row_gap) for i in range(4)]

    for s, y in enumerate(row_y):
        p.append(text(40, y + row_h / 2 + 5, "смуга %d" % s, size=13, bold=True,
                      anchor="start"))
        for x, (label, fill) in zip(col_x, rows[s]):
            p.append(fitbox(x, y, col_w, row_h, [label], size=17, pad=12,
                            fill=fill, stroke=LINE, sw=1.5, bold=True))

    # стан носіїв під сіткою
    state_y = row_y[-1] + row_h + 24
    states = [("цілий", GREEN_FILL), ("цілий", GREEN_FILL), ("зник", RED_FILL),
              ("цілий", GREEN_FILL), ("цілий", GREEN_FILL)]
    p.append(text(40, state_y + 26, "стан носія", size=13, bold=True, anchor="start"))
    for x, (lab, fill) in zip(col_x, states):
        p.append(fitbox(x, state_y, col_w, 44, [lab], size=14, pad=10,
                        fill=fill, stroke=LINE, sw=1.4))

    # два випадки відновлення
    frag, w1, h1 = textbox(400, state_y + 130,
                           ["у смузі 0 зник шматок даних D2",
                            "D2 = D0 ⊕ D1 ⊕ D3 ⊕ P0"],
                           size=14, pad=15, fill=BLUE_FILL, stroke=LINE, sw=1.5)
    p.append(frag)
    frag, w2, h2 = textbox(950, state_y + 130,
                           ["у смузі 2 зник шматок парності P2",
                            "P2 = D8 ⊕ D9 ⊕ D10 ⊕ D11"],
                           size=14, pad=15, fill=WARM_FILL, stroke=LINE, sw=1.5)
    p.append(frag)

    p.append(text(W / 2, state_y + 205,
                  "Обидва випадки — одна й та сама дія: скласти за модулем два все, що лишилося в смузі.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'stripe-and-parity.svg'), W, H, *p,
           title="RAID5 із п'яти носіїв: парність обертається по смугах")


# ── 2. Лічильник подій як арбітр свіжості ──────────────────────────────────
def fig_event_count():
    W, H = 1260, 660
    p = []

    members = [
        (250, ["суперблок на sdb",
               "UUID масиву: 3f9c…",
               "роль у масиві: 0",
               "лічильник подій: 4711"], GREEN_FILL),
        (630, ["суперблок на sdc",
               "UUID масиву: 3f9c…",
               "роль у масиві: 1",
               "лічильник подій: 4711"], GREEN_FILL),
        (1010, ["суперблок на sdd",
                "UUID масиву: 3f9c…",
                "роль у масиві: 2",
                "лічильник подій: 4390"], WARM_FILL),
    ]

    y_mem = 155
    heights = []
    for cx, lines, fill in members:
        frag, w, h = textbox(cx, y_mem, lines, size=13, pad=15, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)
        heights.append(h)

    y_dec = 350
    frag, wd, hd = textbox(630, y_dec,
                           ["збирання масиву звіряє три лічильники",
                            "найбільший — 4711 — і є станом, на якому масив спинився",
                            "sdd відстав на 321 подію: його вміст застарілий"],
                           size=14, pad=16, fill=BLUE_FILL, stroke=LINE, sw=1.6)
    p.append(frag)

    for (cx, _, _), h in zip(members, heights):
        p.append(arrow(cx, y_mem + h / 2, 630 + (cx - 630) * 0.28, y_dec - hd / 2))

    y_out = 500
    frag, wa, ha = textbox(390, y_out, ["sdb і sdc — повноцінні учасники,",
                                        "масив стартує на них"],
                           size=13, pad=14, fill=GREEN_FILL, stroke=LINE, sw=1.5)
    p.append(frag)
    frag, wb, hb = textbox(890, y_out, ["sdd приймається як той, що доганяє:",
                                        "для нього починають відбудову"],
                           size=13, pad=14, fill=WARM_FILL, stroke=LINE, sw=1.5)
    p.append(frag)

    p.append(arrow(500, y_dec + hd / 2, 390, y_out - ha / 2))
    p.append(arrow(760, y_dec + hd / 2, 890, y_out - hb / 2))

    p.append(text(W / 2, 600,
                  "Ім'я /dev/sdd тут ні до чого: учасника впізнають за UUID і роллю, а свіжість беруть із лічильника.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'event-count.svg'), W, H, *p,
           title="Хто в масиві свіжий: суперблоки вирішують це самі")


# ── 3. Дірка запису ────────────────────────────────────────────────────────
def fig_write_hole():
    W, H = 1340, 740
    p = []

    heads = ["1. усе узгоджено",
             "2. запис смуги в польоті",
             "3. живлення зникло",
             "4. гине носій із D2"]
    box_w, box_h = 300, 52
    col_x = [40, 380, 720, 1060]

    for x, hd in zip(col_x, heads):
        p.append(text(x + box_w / 2, 78, hd, size=14, bold=True))

    cells = [
        [("D0", BLUE_FILL), ("D1", BLUE_FILL), ("D2", BLUE_FILL),
         ("P = D0 ⊕ D1 ⊕ D2", GREEN_FILL)],
        [("D0", BLUE_FILL), ("D1′ уже записано", WARM_FILL), ("D2", BLUE_FILL),
         ("P — ще стара", RED_FILL)],
        [("D0", BLUE_FILL), ("D1′", WARM_FILL), ("D2", BLUE_FILL),
         ("P — стара", RED_FILL)],
        [("D0", BLUE_FILL), ("D1′", WARM_FILL), ("носій зник", GREY_FILL),
         ("P — стара", RED_FILL)],
    ]

    cell_y = [110 + i * (box_h + 12) for i in range(4)]

    for x, column in zip(col_x, cells):
        for y, (label, fill) in zip(cell_y, column):
            p.append(fitbox(x, y, box_w, box_h, [label], size=14, pad=12,
                            fill=fill, stroke=LINE, sw=1.4))

    verdicts = [
        (["будь-який шматок смуги", "відновлюється з решти"], GREEN_FILL),
        (["вікно неузгодженості:", "дані нові, парність стара"], WARM_FILL),
        (["суперечність лягла на носії,", "і ніхто про неї не знає"], RED_FILL),
        (["D0 ⊕ D1′ ⊕ P дає сміття", "замість утраченого D2"], RED_FILL),
    ]
    v_y = cell_y[-1] + box_h + 46
    for x, (lines, fill) in zip(col_x, verdicts):
        p.append(fitbox(x, v_y, box_w, 92, lines, size=14, pad=14,
                        fill=fill, stroke=LINE, sw=1.5))

    p.append(text(W / 2, v_y + 165,
                  "Карта намірів запису тут не рятує: вона підказує, ЯКУ смугу перевірити,",
                  size=13, color=MUTED))
    p.append(text(W / 2, v_y + 192,
                  "але не зберігає того, чим була парність до початку запису.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'write-hole.svg'), W, H, *p,
           title="Дірка запису: чому неповна смуга стає пасткою")


# ── 4. Чотири операції синхронізації ───────────────────────────────────────
def fig_sync_kinds():
    W, H = 1360, 600
    p = []

    label_x, label_w = 30, 200
    col_w, col_gap = 262, 12
    col_x = [250 + i * (col_w + col_gap) for i in range(4)]
    heads = ["що її запускає", "що читає", "що пише", "що з цього виходить"]

    for x, hd in zip(col_x, heads):
        p.append(text(x + col_w / 2, 82, hd, size=14, bold=True))

    rows = [
        ("resync",
         [(["масив спинили", "нечисто"], WARM_FILL),
          (["усіх учасників", "від початку до кінця"], BLUE_FILL),
          (["парність або", "другу копію"], WARM_FILL),
          (["знімає розбіжність,", "що лишилася після збою"], GREEN_FILL)]),
        ("recovery",
         [(["учасника замінили", "або додали запасного"], WARM_FILL),
          (["решту учасників"], BLUE_FILL),
          (["лише новий носій"], WARM_FILL),
          (["повертає масив", "до повного складу"], GREEN_FILL)]),
        ("check",
         [(["розклад або", "команда руками"], WARM_FILL),
          (["усіх учасників"], BLUE_FILL),
          (["нічого"], GREY_FILL),
          (["лише рахує незбіги", "в mismatch_cnt"], GREY_FILL)]),
        ("repair",
         [(["команда руками,", "зазвичай після check"], WARM_FILL),
          (["усіх учасників"], BLUE_FILL),
          (["парність або", "другу копію"], WARM_FILL),
          (["робить копії однаковими,", "не з'ясовуючи правди"], RED_FILL)]),
    ]

    row_h, row_gap = 92, 12
    row_y = [108 + i * (row_h + row_gap) for i in range(4)]

    for (name, cells), y in zip(rows, row_y):
        p.append(fitbox(label_x, y, label_w, row_h, [name], size=16, pad=12,
                        fill=GREY_FILL, stroke=LINE, sw=1.5, bold=True))
        for x, (lines, fill) in zip(col_x, cells):
            p.append(fitbox(x, y, col_w, row_h, lines, size=13, pad=12,
                            fill=fill, stroke=LINE, sw=1.4))

    p.append(text(W / 2, row_y[-1] + row_h + 46,
                  "check і repair читають те саме. Різниця лише в праві переписати те, що не збіглося,",
                  size=13, color=MUTED))
    p.append(text(W / 2, row_y[-1] + row_h + 72,
                  "а знання, котра зі сторін мала рацію, немає в жодної з чотирьох операцій.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'sync-kinds.svg'), W, H, *p,
           title="Чотири синхронізації md: однакова робота, різні підстави")


# ── 5. Де на учаснику лежать метадані: чотири версії суперблока ─────────────
def fig_metadata_layout():
    W, H = 1280, 640
    p = []

    x0, x1 = 190, 1230
    span = x1 - x0
    bar_h = 56
    rows = [
        ("0.90", 100, [(0.00, 0.74, "дані", GREEN_FILL),
                       (0.74, 1.00, "СБ + карта", WARM_FILL)]),
        ("1.0", 210, [(0.00, 0.68, "дані", GREEN_FILL),
                      (0.68, 0.84, "карта", BLUE_FILL),
                      (0.84, 1.00, "СБ", WARM_FILL)]),
        ("1.1", 320, [(0.00, 0.16, "СБ", WARM_FILL),
                      (0.16, 0.32, "карта", BLUE_FILL),
                      (0.32, 0.45, "ЖПБ", RED_FILL),
                      (0.45, 1.00, "дані", GREEN_FILL)]),
        ("1.2", 430, [(0.00, 0.13, "4 КіБ", GREY_FILL),
                      (0.13, 0.29, "СБ", WARM_FILL),
                      (0.29, 0.45, "карта", BLUE_FILL),
                      (0.45, 0.58, "ЖПБ", RED_FILL),
                      (0.58, 1.00, "дані", GREEN_FILL)]),
    ]

    p.append(text(W / 2, 44, "Порядок ділянок на учаснику масиву; ширини НЕ в масштабі",
                  size=14, color=MUTED))
    p.append(text(x0, 76, "початок носія", size=13, color=MUTED, anchor="start"))
    p.append(text(x1, 76, "кінець носія", size=13, color=MUTED, anchor="end"))

    data_x = None
    for name, y, segs in rows:
        p.append(text(96, y + bar_h / 2 + 6, name, size=17, bold=True))
        for a, b, label, fill in segs:
            sx = x0 + span * a
            sw_ = span * (b - a)
            p.append(fitbox(sx, y, sw_, bar_h, label, size=15, fill=fill))
            if name == "1.2" and label == "дані":
                data_x = sx

    # data_offset для 1.2 — від початку носія до першого сектора даних
    ay = 430 + bar_h + 26
    p.append(line(x0, ay, data_x, ay, color=MUTED, sw=1.5))
    p.append(line(x0, ay - 7, x0, ay + 7, color=MUTED, sw=1.5))
    p.append(line(data_x, ay - 7, data_x, ay + 7, color=MUTED, sw=1.5))
    p.append(text((x0 + data_x) / 2, ay + 24, "data_offset", size=14, color=MUTED))

    p.append(text(W / 2, 578,
                  "СБ — суперблок (4 КіБ) · карта — карта намірів запису · ЖПБ — журнал поганих блоків",
                  size=13, color=MUTED))
    p.append(text(W / 2, 602,
                  "0.90 і 1.0 лежать у хвості, тож дані лишаються на своєму місці; 1.1 і 1.2 — на початку.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'metadata-layout.svg'), W, H, *p,
           title="Розкладка метаданих md на учаснику: версії 0.90, 1.0, 1.1, 1.2")


if __name__ == '__main__':
    fig_stripe_and_parity()
    fig_event_count()
    fig_write_hole()
    fig_sync_kinds()
    fig_metadata_layout()
    print("ok")
