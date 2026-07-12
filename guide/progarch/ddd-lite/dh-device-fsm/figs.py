# -*- coding: utf-8 -*-
"""Фігури до кроку «Життєвий цикл пристрою як автомат станів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER = "#c07d1a"          # offline — притлумлений бурштин
AMBER_FILL = "#fdf6ec"
GREEN_FILL = "#eafaf0"
GRAY_FILL = "#f0f0f2"


def fig_boolean_explosion():
    """Чотири прапорці = 16 комбінацій, сенс мають 4 → один стан-перелік."""
    W, H = 1020, 560
    frags = [line(510, 70, 510, 500, color=MUTED, sw=1, dash="5,6")]

    # ── ЛІВОРУЧ: чотири прапорці ──
    frags.append(text(255, 92, "Чотири прапорці", size=17, bold=True, color=POS))
    flags = ["commissioned: bool", "online: bool", "retired: bool", "home_id: id?"]
    fy = 130
    for f in flags:
        b, _, _ = textbox(255, fy, f, size=13, fill="#fdecea", stroke=POS, sw=1.4, min_w=230)
        frags.append(b)
        fy += 40
    frags.append(text(255, fy + 18, "2⁴ = 16 комбінацій, сенс мають 4",
                      size=14, bold=True, color=INK))

    # три приклади-маячні
    combos = [
        (330, "retired=так, online=так", "списаний — і досі на звʼязку?"),
        (400, "commissioned=ні, home_id=є", "нічий — а вже в чиємусь домі?"),
        (470, "retired=так, commissioned=ні", "списали те, чого не вводили?"),
    ]
    for cy, top, bot in combos:
        frags.append(minus(70, cy))
        frags.append(text(92, cy - 3, top, size=13, anchor="start", bold=True))
        frags.append(text(92, cy + 15, bot, size=12, anchor="start", color=MUTED))

    # ── ПРАВОРУЧ: один стан ──
    frags.append(text(765, 92, "Один стан", size=17, bold=True, color=FIELD))
    states = [
        ("new", "щойно з коробки, ще нічий"),
        ("online", "у домі й на звʼязку"),
        ("offline", "у домі, але зараз мовчить"),
        ("retired", "списаний назавжди"),
    ]
    sy = 145
    prev = None
    for name, desc in states:
        b, bw, bh = textbox(690, sy, name, size=14, bold=True,
                            fill=GREEN_FILL, stroke=FIELD, sw=1.8, min_w=120)
        frags.append(b)
        frags.append(text(690 + bw / 2 + 12, sy + 4, desc, size=12,
                          anchor="start", color=MUTED))
        if prev is not None:
            frags.append(arrow(690, prev + 16, 690, sy - 16, color=MUTED, sw=1.6))
        prev = sy
        sy += 78
    frags.append(text(765, sy + 4, "рівно чотири — інших нема звідки взяти",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, "boolean-explosion.svg"), W, H, *frags,
           title="Чому не чотири прапорці")


def _node(cx, cy, name, sub, fill, stroke, terminal=False):
    """Вузол-стан: назва + підпис, за потреби — подвійна рамка (кінцевий)."""
    body, w, h = textbox(cx, cy, name + "\n" + sub, size=13, bold=False,
                         fill=fill, stroke=stroke, sw=2, min_w=170)
    out = ""
    if terminal:
        out += rect(cx - w / 2 - 6, cy - h / 2 - 6, w + 12, h + 12,
                    fill="none", stroke=stroke, sw=1.4)
    out += body
    return out, w, h


def fig_lifecycle_fsm():
    """Автомат життєвого циклу: new → online ⇄ offline → retired (кінцевий)."""
    W, H = 960, 540
    frags = []

    # координати центрів
    NX, NY = 155, 210
    OX, OY = 460, 210
    FX, FY = 795, 210
    BX, BY = 460, 400        # offline

    n_new, wn, hn = _node(NX, NY, "new", "щойно з коробки", GREEN_FILL, FIELD)
    n_on, wo, ho = _node(OX, OY, "online", "у домі, на звʼязку", GREEN_FILL, FIELD)
    n_off, wb, hb = _node(BX, BY, "offline", "у домі, мовчить", AMBER_FILL, AMBER)
    n_ret, wr, hr = _node(FX, FY, "retired", "списаний назавжди", GRAY_FILL, MUTED, terminal=True)

    # старт-заглушка → new
    frags.append(arrow(28, NY, NX - wn / 2 - 6, NY, color=MUTED, sw=1.8))
    frags.append(text(45, NY - 12, "старт", size=12, color=MUTED, anchor="middle"))

    # new → online
    frags.append(arrow(NX + wn / 2 + 6, NY, OX - wo / 2 - 6, NY, color=INK, sw=1.8))
    frags.append(text((NX + OX) / 2, NY - 12, "commission()", size=13, bold=True))

    # online → offline (вниз, ліворуч від центру); підпис — ліворуч від вузлів
    frags.append(arrow(OX - 30, OY + ho / 2 + 4, BX - 30, BY - hb / 2 - 4,
                       color=INK, sw=1.8))
    frags.append(text(320, 298, "markOffline()", size=13, anchor="middle", bold=True))
    frags.append(text(320, 315, "втратив звʼязок", size=11, color=MUTED, anchor="middle"))

    # offline → online (вгору, праворуч від центру); підпис — праворуч, вище діагоналі
    frags.append(arrow(BX + 30, BY - hb / 2 - 4, OX + 30, OY + ho / 2 + 4,
                       color=INK, sw=1.8))
    frags.append(text(610, 298, "markOnline()", size=13, anchor="middle", bold=True))
    frags.append(text(610, 315, "звʼязок вернувся", size=11, color=MUTED, anchor="middle"))

    # online → retired
    frags.append(arrow(OX + wo / 2 + 6, OY, FX - wr / 2 - 8, FY, color=INK, sw=1.8))
    frags.append(text((OX + FX) / 2, NY - 12, "retire()", size=13, bold=True))

    # offline → retired: у ДНИЩЕ retired, низько праворуч — щоб не чіпати підписів
    frags.append(arrow(BX + wb / 2 + 4, BY, FX, FY + hr / 2 + 8, color=INK, sw=1.8))
    frags.append(text(690, 392, "retire()", size=13, bold=True))

    for f in (n_new, n_on, n_off, n_ret):
        frags.append(f)

    frags.append(text(W / 2, 512,
                      "один початок (new), один незворотний кінець (retired), між ними — лише дозволені стрілки",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "lifecycle-fsm.svg"), W, H, *frags,
           title="Життєвий цикл пристрою як автомат")


def fig_state_dimensions():
    """Дві незалежні осі стану: життєвий цикл (повільний) і робочий (швидкий)."""
    W, H = 940, 470
    frags = []

    frags.append(text(W / 2, 66, "Життєвий цикл — ОДНА нитка, спільна для будь-якого пристрою",
                      size=14, bold=True, color=INK))

    # верхній ряд — чотири стани життєвого циклу
    xs = [150, 375, 600, 825]
    names = ["new", "online", "offline", "retired"]
    fills = [GREEN_FILL, GREEN_FILL, AMBER_FILL, GRAY_FILL]
    strokes = [FIELD, FIELD, AMBER, MUTED]
    LY = 120
    centers = []
    for x, nm, fl, st in zip(xs, names, fills, strokes):
        b, w, h = textbox(x, LY, nm, size=14, bold=True, fill=fl, stroke=st,
                          sw=1.8, min_w=140)
        frags.append(b)
        centers.append((x, w))
    for i in range(3):
        x1 = centers[i][0] + centers[i][1] / 2 + 6
        x2 = centers[i + 1][0] - centers[i + 1][1] / 2 - 6
        frags.append(arrow(x1, LY, x2, LY, color=MUTED, sw=1.6))

    # робочий стан — під online, за пунктирною дужкою
    onx = xs[1]
    frags.append(line(onx, LY + 22, onx, 240, color=AMBER, sw=1.4, dash="5,5"))
    frags.append(rect(230, 240, 300, 150, fill="#fbfbfc", stroke=MUTED, sw=1.5))
    frags.append(text(380, 266, "робочий стан замка", size=13, bold=True))
    ops = [("Locked", 300), ("Unlocked", 380), ("Jammed", 460)]
    for label, ox in ops:
        b, _, _ = textbox(ox, 320, label, size=12, fill=BG, stroke=INK, sw=1.2, min_w=76)
        frags.append(b)
    frags.append(text(380, 372, "свій у кожного виду; живий лише поки online",
                      size=12, color=MUTED))

    frags.append(text(W / 2, 430,
                      "осі ортогональні: у списаного робочого стану нема, у offline — лише останній відомий",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "state-dimensions.svg"), W, H, *frags,
           title="Дві незалежні осі стану одного пристрою")


def fig_transition_matrix():
    """Ґратка (стан × команда): законний перехід + подія / no-op / кидає."""
    W, H = 1040, 560
    frags = []
    states = [("new", GREEN_FILL, FIELD), ("online", GREEN_FILL, FIELD),
              ("offline", AMBER_FILL, AMBER), ("retired", GRAY_FILL, MUTED)]
    cmds = ["commission", "markOffline", "markOnline", "retire"]
    # kind: 'go' законний | 'noop' ідемпотентний | 'bad' кидає
    G = {
        (0, 0): ("go", "→ online", "Commissioned"),
        (0, 1): ("bad", "✗ кидає", ""), (0, 2): ("bad", "✗ кидає", ""),
        (0, 3): ("bad", "✗ кидає", ""),
        (1, 0): ("bad", "✗ кидає", ""),
        (1, 1): ("go", "→ offline", "WentOffline"),
        (1, 2): ("noop", "no-op", "без події"),
        (1, 3): ("go", "→ retired", "Retired"),
        (2, 0): ("bad", "✗ кидає", ""),
        (2, 1): ("noop", "no-op", "без події"),
        (2, 2): ("go", "→ online", "Reconnected"),
        (2, 3): ("go", "→ retired", "Retired"),
        (3, 0): ("bad", "✗ кидає", ""), (3, 1): ("bad", "✗ кидає", ""),
        (3, 2): ("bad", "✗ кидає", ""),
        (3, 3): ("noop", "no-op", "без події"),
    }
    x0, y0 = 178, 96
    cw, rh = 196, 90
    for j, c in enumerate(cmds):
        frags.append(text(x0 + cw * j + cw / 2, y0 - 20, c, size=13, bold=True))
    frags.append(text(x0 - 88, y0 - 20, "стан ↓  команда →", size=11, color=MUTED))
    for i, (sname, fl, st) in enumerate(states):
        cy = y0 + rh * i + rh / 2
        b, _, _ = textbox(x0 - 88, cy, sname, size=13, bold=True, fill=fl,
                          stroke=st, sw=1.6, min_w=120)
        frags.append(b)
        for j in range(4):
            kind, top, sub = G[(i, j)]
            cx = x0 + cw * j + cw / 2
            if kind == "go":
                cf, cs, tc = GREEN_FILL, FIELD, INK
            elif kind == "noop":
                cf, cs, tc = GRAY_FILL, MUTED, MUTED
            else:
                cf, cs, tc = "#fdecea", POS, POS
            frags.append(rect(x0 + cw * j + 5, y0 + rh * i + 5, cw - 10, rh - 10,
                              fill=cf, stroke=cs, sw=1.5))
            frags.append(text(cx, cy - 6, top, size=14, bold=True, color=tc))
            if sub:
                frags.append(text(cx, cy + 16, sub, size=11, color=MUTED))
    ly = y0 + rh * 4 + 34
    items = [(GREEN_FILL, FIELD, "законний перехід — емітить подію"),
             (GRAY_FILL, MUTED, "ідемпотентний no-op — без події"),
             ("#fdecea", POS, "незаконний — кидає DomainError")]
    lx = 180
    for cf, cs, label in items:
        frags.append(rect(lx, ly - 13, 17, 17, fill=cf, stroke=cs, sw=1.4))
        frags.append(text(lx + 25, ly + 1, label, size=12, anchor="start", color=INK))
        lx += 25 + text_width(label, 12) + 34
    render(os.path.join(IMG, "transition-matrix.svg"), W, H, *frags,
           title="Уся ґратка (стан × команда) — одне джерело правди й міра покриття")


def fig_events_fanout():
    """Подія на кожному переході; інші контексти реагують, не лізучи в пристрій."""
    W, H = 1000, 430
    frags = []
    dbox, dwid, _ = textbox(140, 210, "Пристрій\n(агрегат стану)", size=14,
                            bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2, min_w=160)
    bx, by, bw, bh = 380, 118, 210, 184
    frags.append(rect(bx, by, bw, bh, fill="#fbfbfc", stroke=INK, sw=1.6))
    frags.append(text(bx + bw / 2, by + 26, "шина подій", size=14, bold=True))
    evs = ["DeviceCommissioned", "DeviceWentOffline",
           "DeviceReconnected", "DeviceRetired"]
    ey = by + 58
    for e in evs:
        frags.append(text(bx + bw / 2, ey, e, size=12, color=MUTED))
        ey += 30
    bill, bwd, _ = textbox(852, 132, "Білінг\nрахує від Commissioned", size=13,
                           fill=FILL, stroke=INK, sw=1.6, min_w=210)
    tele, twd, _ = textbox(852, 300, "Телеметрія\nспиняє прийом від Retired",
                           size=13, fill=FILL, stroke=INK, sw=1.6, min_w=210)
    frags.append(arrow(140 + dwid / 2 + 6, 210, bx - 6, 210, color=INK, sw=1.9))
    frags.append(text((140 + dwid / 2 + bx) / 2, 196, "записує й публікує",
                      size=11, color=MUTED))
    frags.append(arrow(bx + bw + 6, 190, 852 - bwd / 2 - 6, 140, color=INK, sw=1.8))
    frags.append(text(686, 142, "Commissioned", size=11, color=MUTED))
    frags.append(arrow(bx + bw + 6, 236, 852 - twd / 2 - 6, 300, color=INK, sw=1.8))
    frags.append(text(686, 270, "Retired", size=11, color=MUTED))
    for f in (dbox, bill, tele):
        frags.append(f)
    frags.append(text(W / 2, 402,
                      "інші контексти РЕАГУЮТЬ на події; стрілки лише від пристрою — досередини не веде жодна",
                      size=13, color=MUTED))
    render(os.path.join(IMG, "events-fanout.svg"), W, H, *frags,
           title="Подія на кожному переході — контексти реагують, не лізучи в пристрій")


def fig_state_explosion():
    """Пласко кожен вимір МНОЖИТЬ стани: online × робочий стан × живлення (для hist-вставки)."""
    W, H = 1040, 600
    frags = []

    # ── ЛІВОРУЧ: один online + два внутрішні виміри ──
    b, wo, ho = textbox(150, 210, "online", size=16, bold=True,
                        fill=GREEN_FILL, stroke=FIELD, sw=2, min_w=140)
    frags.append(b)
    frags.append(text(150, 300, "робочий стан замка", size=13, bold=True))
    frags.append(text(150, 322, "Locked · Unlocked · Jammed  (3)", size=12, color=MUTED))
    frags.append(text(150, 372, "живлення", size=13, bold=True))
    frags.append(text(150, 394, "Full · Low  (2)", size=12, color=MUTED))

    # стрілка «пласко»
    frags.append(arrow(240, 210, 600, 210, color=INK, sw=1.8))
    frags.append(text(420, 190, "пласко: перемножуємо", size=13, bold=True))
    frags.append(text(420, 236, "3 × 2 = 6", size=16, bold=True, color=POS))

    # ── ПРАВОРУЧ: 6 станів-добуток, стрілки в клубок ──
    cols = [720, 910]
    rows = [130, 300, 470]
    works = ["Locked", "Unlocked", "Jammed"]
    powers = ["Full", "Low"]
    cells = {}
    for r, wy in enumerate(rows):
        for c, cx in enumerate(cols):
            lbl = works[r] + "\n" + powers[c]
            box, bw, bh = textbox(cx, wy, lbl, size=12, fill=BG, stroke=INK,
                                  sw=1.3, min_w=104)
            cells[(r, c)] = (cx, wy)
            frags.append(box)

    # клубок перехресних стрілок — лише кілька, щоб проступило плетиво
    tangle = [((0, 0), (2, 1)), ((0, 1), (2, 0)), ((0, 0), (1, 1)),
              ((1, 0), (2, 1)), ((1, 1), (0, 0)), ((2, 0), (0, 1))]
    for a, b2 in tangle:
        x1, y1 = cells[a]
        x2, y2 = cells[b2]
        frags.append(arrow(x1, y1 + 22, x2, y2 - 22, color=AMBER, sw=1.2))
    frags.append(text(815, 545, "…і кожна пара станів — свій перехід", size=12, color=MUTED))

    frags.append(text(W / 2, 578,
                      "Стани ростуть як ДОБУТОК вимірів, переходи — як його квадрат; третій вимір множить знову.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "state-explosion.svg"), W, H, *frags,
           title="Пласко: кожен вимір МНОЖИТЬ стани")


def fig_statechart_cure():
    """Ліки Гареля: online як над-стан (ієрархія) з двома ортогональними регіонами (для hist-вставки)."""
    W, H = 1080, 610
    frags = []

    # new — ліворуч
    b_new, wn, hn = textbox(95, 300, "new", size=14, bold=True,
                            fill=GREEN_FILL, stroke=FIELD, sw=1.8, min_w=90)

    # online — великий над-стан (блоб)
    OX0, OY0, OW, OH = 235, 108, 545, 432
    frags.append(rect(OX0, OY0, OW, OH, fill="#f4fbf6", stroke=FIELD, sw=2.2, rx=16))
    frags.append(text(OX0 + 26, OY0 + 34, "online — над-стан", size=15, bold=True,
                      color=FIELD, anchor="start"))
    # пунктирний поділ на два ортогональні регіони
    DIVX = OX0 + OW / 2
    frags.append(line(DIVX, OY0 + 58, DIVX, OY0 + OH - 26, color=MUTED, sw=1.6, dash="7,6"))

    # лівий регіон — робочий стан замка
    frags.append(text(OX0 + OW / 4 + 10, OY0 + 78, "робочий стан замка", size=13, bold=True))
    wl_y = [250, 340, 428]
    wl_lbl = ["Locked", "Unlocked", "Jammed"]
    wcx = OX0 + OW / 4 + 10
    prev = None
    for y, lbl in zip(wl_y, wl_lbl):
        box, bw, bh = textbox(wcx, y, lbl, size=12, fill=BG, stroke=INK, sw=1.3, min_w=118)
        frags.append(box)
        if prev is not None:
            frags.append(arrow(wcx - 34, prev + 16, wcx - 34, y - 16, color=MUTED, sw=1.4))
            frags.append(arrow(wcx + 34, y - 16, wcx + 34, prev + 16, color=MUTED, sw=1.4))
        prev = y

    # правий регіон — живлення
    frags.append(text(OX0 + 3 * OW / 4 - 10, OY0 + 78, "живлення", size=13, bold=True))
    pcx = OX0 + 3 * OW / 4 - 10
    frags.append(textbox(pcx, 268, "Full", size=12, fill=BG, stroke=INK, sw=1.3, min_w=104)[0])
    frags.append(textbox(pcx, 392, "Low", size=12, fill=BG, stroke=INK, sw=1.3, min_w=104)[0])
    frags.append(arrow(pcx - 30, 292, pcx - 30, 368, color=MUTED, sw=1.4))
    frags.append(arrow(pcx + 30, 368, pcx + 30, 292, color=MUTED, sw=1.4))

    # offline / retired — праворуч, поза блобом
    b_off, wf, hf = textbox(960, 250, "offline", size=14, bold=True,
                            fill=AMBER_FILL, stroke=AMBER, sw=1.8, min_w=120)
    b_ret, wr, hr = textbox(960, 445, "retired", size=14, bold=True,
                            fill=GRAY_FILL, stroke=MUTED, sw=1.8, min_w=120)
    ret_border = rect(960 - wr / 2 - 6, 445 - hr / 2 - 6, wr + 12, hr + 12,
                      fill="none", stroke=MUTED, sw=1.3)

    # стрілки життєвого циклу — по МЕЖІ над-стану, не по під-станах
    frags.append(arrow(95 + wn / 2 + 6, 300, OX0 - 6, 300, color=INK, sw=1.9))
    frags.append(text(182, 285, "commission()", size=12, bold=True))

    frags.append(arrow(OX0 + OW + 6, 244, 960 - wf / 2 - 6, 244, color=INK, sw=1.9))
    frags.append(text(872, 229, "markOffline()", size=11, bold=True))
    frags.append(arrow(960 - wf / 2 - 6, 286, OX0 + OW + 6, 322, color=INK, sw=1.6))
    frags.append(text(874, 356, "markOnline()", size=11))

    frags.append(arrow(OX0 + OW + 6, 452, 960 - wr / 2 - 6, 452, color=INK, sw=1.9))
    frags.append(text(880, 437, "retire()", size=11, bold=True))
    frags.append(arrow(960, 250 + hf / 2 + 6, 960, 445 - hr / 2 - 12, color=INK, sw=1.6))
    frags.append(text(1006, 352, "retire()", size=11, anchor="start"))

    for f in (b_new, ret_border, b_ret, b_off):
        frags.append(f)

    frags.append(text(W / 2, 582,
                      "online — один над-стан; усередині дві незалежні нитки за пунктиром: 3 + 2 = 5 станів замість 3 × 2 = 6, вхід і вихід — одні на весь блок.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "statechart-cure.svg"), W, H, *frags,
           title="Ліки Гареля: над-стан (ієрархія) + регіони (ортогональність)")


if __name__ == "__main__":
    fig_boolean_explosion()
    fig_lifecycle_fsm()
    fig_state_dimensions()
    fig_transition_matrix()
    fig_events_fanout()
    fig_state_explosion()
    fig_statechart_cure()
    print("OK: boolean-explosion.svg, lifecycle-fsm.svg, state-dimensions.svg, "
          "transition-matrix.svg, events-fanout.svg, state-explosion.svg, statechart-cure.svg")
