# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра зносу ─────────────────────────────────────────────────────────────
GREENL = "#d9f0df"; GREENS = "#5fae78"   # свіжий блок
AMBER  = "#f4d97a"; AMBERS = "#c99a2e"   # трохи зношений
DEAD   = "#c0392b"; DEADS  = "#7e241a"   # мертвий (межа)
COLD   = "#cfd4db"; COLDS  = "#8b9099"   # холодний / заморожений
YOUNG  = "#d9f0df"; YOUNGS = "#27ae60"   # молодий, обрано
POOLF  = "#eaf0fd"; POOLS  = "#2457d6"   # вільний пул


def grid(x0, y0, cols, rows, cell, gap, fill_fn):
    out = []
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            x = x0 + c * (cell + gap)
            y = y0 + r * (cell + gap)
            f, s = fill_fn(i)
            out.append(rect(x, y, cell, cell, fill=f, stroke=s, sw=1.2, rx=3))
    return "".join(out)


def swatch(x, y, fill, stroke, label):
    s = rect(x, y, 20, 20, fill=fill, stroke=stroke, sw=1.4, rx=3)
    s += text(x + 28, y + 15, label, size=12, color=INK, anchor="start")
    return s


# ══════════════════════════════════════════════════════════════════════════════
# Фіг.1 — один зношений блок убиває чип; рівний знос — ні
# ══════════════════════════════════════════════════════════════════════════════
def fig_hotspot():
    W, H = 780, 400
    p = []
    cols, rows, cell, gap = 8, 5, 32, 6
    gw = cols * cell + (cols - 1) * gap        # ширина сітки
    lx, rx, gy = 46, 436, 80

    # заголовки панелей
    p.append(text(lx + gw / 2, 62, "Без вирівнювання", size=14, color=DEAD, bold=True))
    p.append(text(rx + gw / 2, 62, "З вирівнюванням", size=14, color=AMBERS, bold=True))

    # ліва сітка: один мертвий блок (кут), решта свіжа
    dead = rows * cols - 1
    p.append(grid(lx, gy, cols, rows, cell, gap,
                  lambda i: (DEAD, DEADS) if i == dead else (GREENL, GREENS)))
    # права сітка: усі трохи зношені, ~однаково
    p.append(grid(rx, gy, cols, rows, cell, gap, lambda i: (AMBER, AMBERS)))

    gy2 = gy + rows * cell + (rows - 1) * gap   # низ сітки

    # виноска на мертвий блок
    dcx = lx + (cols - 1) * (cell + gap) + cell / 2
    bb, bw, bh = textbox(lx + gw / 2 - 20, gy2 + 46,
                         "1 блок стерто до межі → чип непридатний",
                         size=11, bold=True, fill="#fdecea", stroke=DEAD, sw=1.5, color=INK)
    p.append(bb)
    p.append(arrow(lx + gw / 2 - 20 + bw / 2 - 30, gy2 + 34, dcx, gy2 + 4, color=DEAD, sw=1.6))

    bb, bw, bh = textbox(rx + gw / 2, gy2 + 46,
                         "усі блоки постаріли трішки — до межі далеко",
                         size=11, bold=True, fill="#fdf6e0", stroke=AMBERS, sw=1.5, color=INK)
    p.append(bb)

    # легенда
    ly = H - 40
    p.append(swatch(lx + 10, ly, GREENL, GREENS, "свіжий (0 стирань)"))
    p.append(swatch(lx + 210, ly, AMBER, AMBERS, "трохи зношений"))
    p.append(swatch(lx + 380, ly, DEAD, DEADS, "мертвий (межа стирань)"))

    render(os.path.join(OUT, "hotspot.svg"), W, H, *p,
           title="Той самий знос: зосереджений в одному блоці vs розкладений рівно")


# ══════════════════════════════════════════════════════════════════════════════
# Фіг.2 — таблиця трансляції спрямовує перезапис у свіжий блок
# ══════════════════════════════════════════════════════════════════════════════
def fig_mapping():
    W, H = 820, 400
    p = []
    ys = [104, 160, 216, 272]           # рядки, спільні для трьох колонок
    bh = 42

    # колонкові заголовки
    p.append(mtext(118, 66, ["Логічні", "адреси"], size=12, color=INK, bold=True))
    p.append(mtext(400, 66, ["Таблиця", "трансляції"], size=12, color=NEG, bold=True))
    p.append(mtext(636, 66, ["Фізичні блоки", "(лічильник стирань)"], size=12, color=INK, bold=True))

    # A — логічні адреси
    logical = ["LB 4", "LB 5", "LB 6", "LB 7"]
    ax, aw = 70, 96
    for i, lb in enumerate(logical):
        hi = (i == 1)
        p.append(rect(ax, ys[i], aw, bh, fill="#eef2f7" if not hi else "#fff3d6",
                      stroke=INK if not hi else AMBERS, sw=1.2 if not hi else 2, rx=6))
        p.append(text(ax + aw / 2, ys[i] + bh / 2 + 5, lb, size=13, color=INK, bold=hi))

    # B — таблиця (рядки лог → фіз)
    tx, tw = 300, 200
    rowsB = ["LB4  →  PB13", "LB5  →  PB40", "LB6  →  PB07", "LB7  →  PB22"]
    p.append(rect(tx, ys[0] - 8, tw, ys[-1] + bh + 8 - (ys[0] - 8), fill=BG, stroke=NEG, sw=1.6, rx=8))
    for i, row in enumerate(rowsB):
        hi = (i == 1)
        if hi:
            p.append(rect(tx + 6, ys[i] + 2, tw - 12, bh - 4, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=5))
        p.append(text(tx + tw / 2, ys[i] + bh / 2 + 5, row, size=13, color=NEG if hi else INK, bold=hi))

    # C — фізичні блоки з лічильниками
    cx, cw = 556, 150
    phys = [("PB13", "540", "#eef2f7", INK, 1.2),
            ("PB40", "0",   YOUNG,    YOUNGS, 2),      # свіжий, обрано
            ("PB07", "812", "#eef2f7", INK, 1.2),
            ("PB02", "1290", COLD,    COLDS, 1.4)]     # звільнено
    for i, (pb, cnt, fill, stroke, sw) in enumerate(phys):
        p.append(rect(cx, ys[i], cw, bh, fill=fill, stroke=stroke, sw=sw, rx=6))
        p.append(text(cx + 14, ys[i] + bh / 2 + 5, pb, size=13, color=INK, bold=(i == 1), anchor="start"))
        p.append(text(cx + cw - 14, ys[i] + bh / 2 + 5, cnt, size=13, color=stroke, bold=True, anchor="end"))

    # стрілки: LB5 → таблиця → PB40 (свіжий)
    yy = ys[1] + bh / 2
    p.append(arrow(ax + aw, yy, tx, yy, color=AMBERS, sw=2))
    p.append(arrow(tx + tw, yy, cx, yy, color=YOUNGS, sw=2.2))

    # бічні підписи
    p.append(mtext(cx + cw + 14, ys[1] + 12, ["обрано:", "мін. знос"], size=11, color=YOUNGS, anchor="start", bold=True))
    p.append(mtext(cx + cw + 14, ys[3] + 12, ["щойно", "звільнено"], size=11, color=COLDS, anchor="start"))

    render(os.path.join(OUT, "mapping.svg"), W, H, *p,
           title="Перезапис LB5 лягає у найменш зношений фізичний блок")


# ══════════════════════════════════════════════════════════════════════════════
# Фіг.3 — динамічне (лише пул) vs статичне (зрушує й холодні дані)
# ══════════════════════════════════════════════════════════════════════════════
def fig_dynstat():
    W, H = 820, 430
    p = []
    p.append(line(410, 52, 410, 372, color="#dddddd", sw=1.2, dash="5 5"))

    # ── ПАНЕЛЬ A: динамічне ──
    p.append(text(200, 64, "Динамічне", size=14, color=POOLS, bold=True))
    # вільний пул (4 блоки, крутяться)
    p.append(text(185, 96, "вільний пул", size=11, color=POOLS, bold=True))
    px, pw, pg, py = 66, 44, 24, 108
    for k in range(4):
        x = px + k * (pw + pg)
        p.append(rect(x, py, pw, pw, fill=POOLF, stroke=POOLS, sw=1.5, rx=4))
        if k < 3:
            p.append(arrow(x + pw, py + pw / 2, x + pw + pg, py + pw / 2, color=POOLS, sw=1.6))
    bb, bw, bh = textbox(185, py + pw + 34, "весь знос крутиться тут",
                         size=11, bold=True, fill=POOLF, stroke=POOLS, sw=1.4, color=INK)
    p.append(bb)
    # холодні блоки (заморожені)
    cg_y = 250
    p.append(grid(66, cg_y, 5, 2, 34, 8, lambda i: (COLD, COLDS)))
    p.append(mtext(185, cg_y + 2 * 34 + 8 + 26,
                   ["холодні блоки (статика):", "у вирівнюванні не беруть участі"],
                   size=11, color=COLDS))

    # ── ПАНЕЛЬ B: статичне ──
    p.append(text(614, 64, "Статичне", size=14, color=YOUNGS, bold=True))
    p.append(text(600, 96, "вільний пул", size=11, color=POOLS, bold=True))
    qx, qy = 476, 108
    for k in range(4):
        x = qx + k * (pw + pg)
        worn = (k == 0)                       # перший — зношений, приймає холодні дані
        p.append(rect(x, qy, pw, pw, fill="#fdecea" if worn else POOLF,
                      stroke=DEAD if worn else POOLS, sw=2 if worn else 1.5, rx=4))
        if k < 3 and not worn and k != 0:
            pass
    # холодні блоки, один молодий (обрано до переїзду) — під зношеним блоком пулу
    cg2_x, cg2_y = 476, 250
    young = 0
    p.append(grid(cg2_x, cg2_y, 5, 2, 34, 8,
                  lambda i: (YOUNG, YOUNGS) if i == young else (COLD, COLDS)))
    # вертикальна стрілка: молоді холодні дані → зношений блок пулу
    ux = cg2_x + 34 / 2
    p.append(arrow(ux, cg2_y - 4, qx + pw / 2, qy + pw + 6, color=YOUNGS, sw=2.4))
    p.append(mtext(ux + 60, (qy + pw + cg2_y) / 2 - 4,
                   ["переносимо", "холодні дані", "у зношений блок"],
                   size=11, color=YOUNGS, anchor="start", bold=True))
    p.append(mtext(600, cg2_y + 2 * 34 + 8 + 26,
                   ["звільнений молодий блок", "→ у пул: весь чип у роботі"],
                   size=11, color=YOUNGS))

    # легенда
    ly = H - 30
    p.append(swatch(70, ly, COLD, COLDS, "холодний / заморожений"))
    p.append(swatch(300, ly, YOUNG, YOUNGS, "молодий (обрано)"))
    p.append(swatch(500, ly, "#fdecea", DEAD, "зношений блок"))

    render(os.path.join(OUT, "dynamic-static.svg"), W, H, *p,
           title="Динамічне крутить лише пул; статичне зрушує й холодні дані")


# ══════════════════════════════════════════════════════════════════════════════
# Фіг.4 (вставка hist) — чотири незалежні лінії, що зійшлися за 27 місяців
# ══════════════════════════════════════════════════════════════════════════════
def lcard(x0, cy, lines, size=11, fill=FILL, stroke=LINE, sw=1.5, pad=10):
    """Картка з текстом, ЛІВИЙ край якої стоїть на x0 (ширина — під найдовший рядок).
    Ширину рахуємо тим самим правилом, що й textbox, і центруємо рамку під нього."""
    w = max(text_width(ln, size, False) for ln in lines) + 2 * pad
    body, w, h = textbox(x0 + w / 2, cy, lines, size=size, pad=pad,
                         fill=fill, stroke=stroke, sw=sw, color=INK)
    return body, w, h


def fig_hist_timeline():
    W, H = 940, 640
    p = []
    AX = 286                      # вісь
    X0 = 310                      # лівий край карток
    DX = 266                      # правий край колонки дат

    # групи: колір рамки / заливка / колір маркера
    IBMC   = (MUTED,  "#eef0f3")
    SDC    = (POOLS,  POOLF)
    MSC    = (YOUNGS, "#e6f6ec")
    CLC    = (DEAD,   "#fdecea")
    STDC   = (AMBERS, "#fdf6e0")

    rows = [
        (100, "28 груд. 1990", IBMC,
         ["IBM · Вілбур Прайсер — US 5,222,109",
          "лічильники залишку життя блоків"]),
        (178, "13 вер. 1991", SDC,
         ["SunDisk · Лофгрен, Норман, Телін, Ґупта",
          "US 6,230,233 — уперше «wear leveling» у назві"]),
        (256, "лип. 1992", MSC,
         ["M-Systems · TrueFFS на PC-Card Expo",
          "Санта-Клара — робочий продукт, не папір"]),
        (334, "8 бер. 1993", MSC,
         ["M-Systems · Амір Бан — US 5,404,485",
          "«Flash file system» — слів «wear leveling» нема"]),
        (412, "26 бер. 1993", CLC,
         ["Cirrus Logic · Ассар, Немазі, Естахрі",
          "US 5,479,638 — «wear leveling technique» у назві"]),
        (490, "бл. 1994", STDC,
         ["PCMCIA ухвалює FTL за взірцем TrueFFS",
          "трансляція стає галузевим стандартом"]),
        (568, "1 черв. 2001", MSC,
         ["M-Systems · Амір Бан — US 6,732,221",
          "статичне: мітла раз на 1000 стирань"]),
    ]

    # вісь: суцільна крізь щільний період, пунктирна на семирічній паузі
    p.append(line(AX, 78, AX, 508, color="#c8ccd2", sw=2))
    p.append(line(AX, 508, AX, 552, color="#c8ccd2", sw=2, dash="4 5"))
    p.append(line(AX, 552, AX, 596, color="#c8ccd2", sw=2))

    for y, date, (stroke, fill), lines in rows:
        p.append(text(DX, y + 4, date, size=12, color=INK, anchor="end", bold=True))
        body, w, h = lcard(X0, y, lines, fill=fill, stroke=stroke, sw=1.6)
        p.append(body)
        p.append(circle(AX, y, 8, fill=fill, stroke=stroke, sw=2.4))

    # ключова деталь: 18 днів між двома незалежними заявками
    p.append(text(DX, 377, "18 днів", size=11, color=DEAD, anchor="end", bold=True))
    # семирічна пауза
    p.append(text(DX, 533, "минає сім років", size=10, color=MUTED, anchor="end", italic=True))

    # дужка збіжності 1990–1993 + підпис праворуч від карток
    bx = 664
    p.append(line(bx, 100, bx, 412, color=MUTED, sw=1.6))
    p.append(line(bx - 6, 100, bx, 100, color=MUTED, sw=1.6))
    p.append(line(bx - 6, 412, bx, 412, color=MUTED, sw=1.6))
    bb, bw, bh = textbox(800, 256,
                         ["27 місяців:", "чотири команди,", "три країни —", "незалежно", "одна від одної"],
                         size=11, bold=True, fill=BG, stroke=MUTED, sw=1.4, color=INK)
    p.append(bb)

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Вирівнювання зносу винайшли чотири рази поспіль")


# ══════════════════════════════════════════════════════════════════════════════
# Фіг.5–7 (вставка proj) — розкладка блоку, шлях запису, тригер розкиду
# ══════════════════════════════════════════════════════════════════════════════
def badge(cx, cy, n, color, fill=BG):
    return (circle(cx, cy, 11, fill=fill, stroke=color, sw=1.8) +
            text(cx, cy + 4, n, size=12, color=color, bold=True))


def fig_proj_layout():
    W, H = 880, 390
    p = []

    p.append(text(440, 62, "порядок програмування — лише вперед за зсувом",
                  size=12, color=MUTED))
    p.append(arrow(60, 80, 820, 80, color=MUTED, sw=1.5))

    boxes = [(60, 150, POOLF, POOLS, 1.8, ["EC-заголовок", "сторінка 0"]),
             (210, 420, "#eef2f7", INK, 1.4, ["корисні дані", "сторінки 1…62"]),
             (630, 190, GREENL, YOUNGS, 2.0, ["COMMIT-заголовок", "сторінка 63"])]
    for i, (bx, bw, fill, stroke, sw, lab) in enumerate(boxes):
        p.append(badge(bx + bw / 2, 106, str(i + 1), stroke))
        p.append(rect(bx, 130, bw, 66, fill=fill, stroke=stroke, sw=sw, rx=5))
        p.append(mtext(bx + bw / 2, 157, lab, size=12, color=INK, bold=(i != 1)))

    for x, lab in [(60, "0"), (210, "2 КБ"), (630, "126 КБ"), (820, "128 КБ")]:
        p.append(line(x, 196, x, 206, color=MUTED, sw=1.2))
        p.append(text(x, 220, lab, size=11, color=MUTED))

    for cx, lines, fill, stroke in [
            (135, ["стирання щойно сталося —", "лічильник у флеші НЕГАЙНО"], POOLF, POOLS),
            (420, ["дані йдуть сторінка за", "сторінкою, зсув лише росте"], "#eef2f7", INK),
            (725, ["КОМІТ: LBA + seq + CRC.", "До цього рядка блок — сміття"], GREENL, YOUNGS)]:
        bb, bw, bh = textbox(cx, 272, lines, size=11, bold=True,
                             fill=fill, stroke=stroke, sw=1.4, color=INK)
        p.append(bb)

    bb, bw, bh = textbox(440, 340,
                         ["Заголовків два, і це не примха: лічильник стирань мусить лягти у флеш одразу після стирання,",
                          "а право на LBA — аж коли дані цілком записані. Одним заголовком ці два моменти не звести."],
                         size=11, fill="#fdf6e0", stroke=AMBERS, sw=1.5, color=INK)
    p.append(bb)

    render(os.path.join(OUT, "proj-block-layout.svg"), W, H, *p,
           title="Розкладка блоку: лічильник — на початку, коміт — у самому кінці")


def fig_proj_writepath():
    W, H = 1060, 540
    p = []

    steps = [(["беремо з пулу", "найменш зношений PB40"], POOLF, POOLS),
             (["пишемо дані,", "тоді КОМІТ, seq=8"], GREENL, YOUNGS),
             (["map[5] = PB40", "— лише в RAM"], "#eef2f7", MUTED),
             (["стираємо старий", "PB13 → у пул"], POOLF, POOLS)]
    xs = [56, 302, 548, 794]
    for i, (lab, fill, stroke) in enumerate(steps):
        x = xs[i]
        p.append(rect(x, 52, 210, 58, fill=fill, stroke=stroke, sw=1.5, rx=6))
        p.append(badge(x + 22, 81, str(i + 1), stroke))
        p.append(mtext(x + 42, 76, lab, size=11, color=INK, anchor="start"))
        if i < 3:
            p.append(arrow(x + 210, 81, x + 246, 81, color=MUTED, sw=1.6))

    cols = [(145, "зрив на кроці 2", "#fdf6e0", AMBERS),
            (447, "зрив між 2 і 4", GREENL, YOUNGS),
            (749, "зрив на кроці 4", POOLF, POOLS)]
    for cx, head, fill, stroke in cols:
        p.append(fitbox(cx, 146, 280, 40, head, size=13, bold=True,
                        fill=fill, stroke=stroke, sw=1.8, color=INK))

    rows = [
        (194, 82, "у флеші лишилось", [
            ["PB40: EC-заголовок є,", "КОМІТУ немає.", "PB13: цілий, seq=7"],
            ["PB40: коміт seq=8,", "PB13: коміт seq=7 —", "обидва звуться LBA 5"],
            ["PB13: стертий, але", "EC-заголовка немає —", "лічильник утрачено"]]),
        (284, 82, "скан при старті", [
            ["коміту нема → блок", "порожній → у пул;", "LBA 5 лишається за PB13"],
            ["seq 8 > 7 → map[5] = PB40;", "PB13 → стерти, у пул"],
            ["ставимо середній EC,", "стерти ще раз → у пул"]]),
        (374, 64, "наслідок", [
            ["утрачено лише новий запис,", "старі дані цілі"],
            ["новий запис уцілів"],
            ["дані цілі, лічильник", "трохи неточний"]]),
    ]
    for y, h, label, cells in rows:
        p.append(text(132, y + h / 2 + 4, label, size=11, color=MUTED,
                      anchor="end", bold=True))
        for j, (cx, _, _, stroke) in enumerate(cols):
            p.append(fitbox(cx, y, 280, h, cells[j], size=12,
                            fill=BG, stroke=stroke, sw=1.2, color=INK))

    bb, bw, bh = textbox(530, 480,
                         ["Таблиці у флеші немає — її щоразу відновлює скан.",
                          "Тому «атомарний запис таблиці» й не потрібен: суддя — seq у коміт-заголовку."],
                         size=12, bold=True, fill="#fdf6e0", stroke=AMBERS, sw=1.5, color=INK)
    p.append(bb)

    render(os.path.join(OUT, "proj-write-path.svg"), W, H, *p,
           title="Три місця, де живлення може зникнути, — і що вирішить скан")


def fig_proj_spread():
    W, H = 900, 500
    p = []
    ecs = [12, 3980, 4020, 3950, 4130, 3990, 18, 4005, 3970, 4100, 3960, 4040]
    SRC, DST, COLDB = 0, 4, 6
    base, top_h = 360.0, 200.0

    bb, bw, bh = textbox(300, 84,
                         ["розкид = max − min = 4130 − 12 = 4118",
                          "поріг T = 4096  →  4118 > T  →  час рухати холодні дані"],
                         size=12, bold=True, fill="#fdf6e0", stroke=AMBERS, sw=1.6, color=INK)
    p.append(bb)

    for i, e in enumerate(ecs):
        x = 98 + i * 60
        h = 20 + (e / 4130.0) * top_h
        if i == DST:
            fill, stroke = DEAD, DEADS
        elif i in (SRC, COLDB):
            fill, stroke = YOUNG, YOUNGS
        else:
            fill, stroke = AMBER, AMBERS
        sw = 2.4 if i in (SRC, DST) else 1.2
        p.append(rect(x, base - h, 44, h, fill=fill, stroke=stroke, sw=sw, rx=3))
        p.append(text(x + 22, base - h - 6, str(e), size=10, color=stroke, bold=True))
        p.append(text(x + 22, 378, "PB%d" % i, size=10, color=MUTED))

    p.append(line(98, base, 802, base, color=INK, sw=1.4))

    p.append(arrow(120, 404, 360, 404, color=YOUNGS, sw=2.4))
    p.append(text(240, 428, "холодні дані PB0 → PB4; PB0 звільняється в пул",
                  size=11, color=YOUNGS, bold=True))

    p.append(swatch(120, 456, YOUNG, YOUNGS, "молодий: тримає холодні дані"))
    p.append(swatch(380, 456, AMBER, AMBERS, "вільний пул (крутиться)"))
    p.append(swatch(620, 456, DEAD, DEADS, "найзношеніший — ціль"))

    render(os.path.join(OUT, "proj-ec-spread.svg"), W, H, *p,
           title="Тригер: поки розкид лічильників менший за поріг — не рухаємось")


# ══════════════════════════════════════════════════════════════════════════════
# Фіг.8–10 (вставка math) — розподіл лічильників, драбина TBW, оптимум мітли
# Числа — з симуляції моделі статті (N=4096…65536, P/E=3000, 80% статики).
# ══════════════════════════════════════════════════════════════════════════════

# гістограми лічильників стирань наприкінці життя, 20 бакетів по 150 стирань
H_DYN = [3276, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 820]
H_STA = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 138, 384, 429, 480, 535, 628, 1502]


def fig_math_histogram():
    W, H = 1020, 560
    p = []
    PW, PH = 384, 250                 # площа графіка
    PY = 118                          # верх площі
    BASE = PY + PH                    # вісь X
    YMAX = 3400.0                     # блоків — спільна шкала обох панелей

    panels = [
        (66, "Лише динамічне", H_DYN, 600.4, 1200.0, 1.999, 0.200, DEAD, DEADS),
        (566, "Зі статичним (K = 1000)", H_STA, 2662.1, 295.6, 0.111, 0.887, YOUNGS, GREENS),
    ]

    for x0, title, hist, mean, sd, cv, eta, hue, hues in panels:
        p.append(text(x0 + PW / 2, PY - 42, title, size=14, color=hue, bold=True))

        # осі
        p.append(line(x0, BASE, x0 + PW + 16, BASE, color=INK, sw=1.4))
        p.append(line(x0, PY - 12, x0, BASE, color=INK, sw=1.4))

        # стовпчики
        bw = PW / 20.0
        for i, n in enumerate(hist):
            if not n:
                continue
            h = n / YMAX * PH
            bx = x0 + i * bw
            p.append(rect(bx + 1.5, BASE - h, bw - 3, h,
                          fill=(DEAD if i == 19 and hist is H_DYN else
                                (COLD if i == 0 else AMBER)),
                          stroke=(DEADS if i == 19 and hist is H_DYN else
                                  (COLDS if i == 0 else AMBERS)), sw=1.1, rx=2))
            p.append(text(bx + bw / 2, BASE - h - 8, str(n), size=9,
                          color=MUTED, bold=True))

        # мітки осі X
        for e in (0, 1000, 2000, 3000):
            xx = x0 + e / 3000.0 * PW
            p.append(line(xx, BASE, xx, BASE + 7, color=MUTED, sw=1.2))
            p.append(text(xx, BASE + 24, str(e), size=11, color=MUTED))
        p.append(text(x0 + PW / 2, BASE + 46, "лічильник стирань блока",
                      size=11, color=MUTED, italic=True))

        # межа P/E
        xlim = x0 + PW
        p.append(line(xlim, PY - 12, xlim, BASE, color=DEAD, sw=1.8, dash="5 4"))
        p.append(text(xlim + 12, PY - 20, "P/E", size=11, color=DEAD, bold=True))

        # середнє
        xm = x0 + mean / 3000.0 * PW
        p.append(line(xm, PY - 12, xm, BASE, color=NEG, sw=1.8, dash="6 4"))
        p.append(text(xm, PY - 20, "ē = %.0f" % mean, size=11, color=NEG, bold=True))

        bb, bwd, bhd = textbox(x0 + PW / 2, BASE + 96,
                               ["σ = %.0f    CV = σ/ē = %.2f" % (sd, cv),
                                "η = ē / P/E = %.2f" % eta],
                               size=12, bold=True, fill=BG, stroke=hues, sw=1.5, color=INK)
        p.append(bb)

    p.append(text(W / 2, 84,
                  "той самий чип, той самий момент смерті (max = 3000) — різна тільки СЕРЕДНЯ",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "math-erase-histogram.svg"), W, H, *p,
           title="Розподіл зносу наприкінці життя: дві купки проти одного згустка")


def fig_math_tbw_ladder():
    import math as _m
    W, H = 980, 470
    p = []
    X0, XW = 300, 560                 # площа лог-шкали
    LO, HI = _m.log10(0.008), _m.log10(1000.0)   # ГіБ

    def xof(gib):
        return X0 + (_m.log10(gib) - LO) / (HI - LO) * XW

    rows = [
        (128, "без вирівнювання", 0.01144, "11.7 МіБ", DEAD, DEADS,
         "η = 1/65536 — усе б'є в один блок"),
        (198, "динамічне (f = 0.2)", 150.1, "150 ГіБ", AMBER, AMBERS,
         "η = f = 0.20 — грає лише вільний пул"),
        (268, "+ статичне, K = 1000", 664.9, "665 ГіБ", GREENL, GREENS,
         "η = 0.89, WAF = 1.001 — грає весь чип"),
        (338, "стеля (η = 1, WAF = 1)", 750.0, "750 ГіБ", "#eef2f7", MUTED,
         "C × P/E — фізика чипа, недосяжний ідеал"),
    ]

    # сітка декад
    for gib, lab in ((0.01, "10 МіБ"), (0.1, "100 МіБ"), (1, "1 ГіБ"),
                     (10, "10 ГіБ"), (100, "100 ГіБ"), (1000, "1 ТіБ")):
        xx = xof(gib)
        p.append(line(xx, 100, xx, 372, color="#e3e6ea", sw=1.0))
        p.append(text(xx, 394, lab, size=11, color=MUTED))
    p.append(text(X0 + XW / 2, 416, "TBW — скільки байтів прийме ХОСТ (лог. шкала)",
                  size=11, color=MUTED, italic=True))

    for y, name, gib, val, fill, stroke, note in rows:
        p.append(text(288, y + 5, name, size=12, color=INK, anchor="end", bold=True))
        w = xof(gib) - X0
        p.append(rect(X0, y - 15, w, 30, fill=fill, stroke=stroke, sw=1.6, rx=4))
        p.append(text(X0 + w + 12, y + 5, val, size=12, color=stroke,
                      anchor="start", bold=True))
        p.append(text(288, y + 22, note, size=10, color=MUTED, anchor="end", italic=True))

    # множники між сходинками
    for y1, y2, mult in ((128, 198, "× 13 115"), (198, 268, "× 4.43"), (268, 338, "× 1.128")):
        p.append(line(866, y1, 866, y2, color=NEG, sw=1.5))
        p.append(line(862, y1, 870, y1, color=NEG, sw=1.5))
        p.append(line(862, y2, 870, y2, color=NEG, sw=1.5))
        p.append(text(878, (y1 + y2) / 2 + 4, mult, size=11, color=NEG,
                      anchor="start", bold=True))

    bb, bw, bh = textbox(W / 2, 452,
                         "Чип 256 МіБ · блок 4 КіБ · N = 65536 · TLC, P/E = 3000 · 80% статики",
                         size=11, fill="#fdf6e0", stroke=AMBERS, sw=1.3, color=INK)
    p.append(bb)

    render(os.path.join(OUT, "math-tbw-ladder.svg"), W, H, *p,
           title="Драбина ресурсу: що саме додає кожен крок алгоритму")


def fig_math_sweep():
    import math as _m
    W, H = 940, 540
    p = []
    X0, XW = 110, 660
    PY, PH = 96, 300
    BASE = PY + PH

    # (ratio = P/E÷K, K при P/E=3000, η, WAF, merit) — з симуляції
    data = [(1.0, 3000, 0.8149, 1.0003, 0.8146),
            (3.0, 1000, 0.8874, 1.0010, 0.8865),
            (5.0, 600, 0.9329, 1.0017, 0.9313),
            (10.0, 300, 0.9657, 1.0033, 0.9625),
            (15.0, 200, 0.9770, 1.0050, 0.9722),
            (30.0, 100, 0.9881, 1.0100, 0.9783),
            (60.0, 50, 0.9940, 1.0200, 0.9745),
            (100.0, 30, 0.9962, 1.0333, 0.9641)]
    LO, HI = _m.log10(1.0), _m.log10(100.0)

    def xof(r):
        return X0 + (_m.log10(r) - LO) / (HI - LO) * XW

    def yof(v):                       # шкала 0.0…1.0
        return BASE - v * PH

    # осі
    p.append(line(X0, BASE, X0 + XW + 20, BASE, color=INK, sw=1.4))
    p.append(line(X0, PY - 10, X0, BASE, color=INK, sw=1.4))
    for v in (0.2, 0.4, 0.6, 0.8, 1.0):
        yy = yof(v)
        p.append(line(X0 - 6, yy, X0 + XW + 20, yy, color="#e3e6ea", sw=1.0))
        p.append(text(X0 - 14, yy + 4, "%.1f" % v, size=11, color=MUTED, anchor="end"))

    for r, K, _, _, _ in data:
        xx = xof(r)
        p.append(line(xx, BASE, xx, BASE + 7, color=MUTED, sw=1.2))
        p.append(text(xx, BASE + 24, ("%g" % r), size=11, color=MUTED))
        p.append(text(xx, BASE + 44, str(K), size=10, color=NEG))
    p.append(text(X0 + XW / 2, BASE + 70, "P/E ÷ K   (згори — відповідне K при P/E = 3000)",
                  size=11, color=MUTED, italic=True))

    # база: без статичного вирівнювання
    p.append(line(X0, yof(0.2001), X0 + XW + 20, yof(0.2001), color=DEAD, sw=1.8, dash="6 4"))
    p.append(text(X0 + XW - 100, yof(0.2001) - 12, "без статичного: η/WAF = 0.20",
                  size=11, color=DEAD, bold=True, anchor="start"))

    # криві η та η/WAF
    for key, color, lab in ((2, AMBERS, "η"), (4, GREENS, "η / WAF")):
        pts = [(xof(d[0]), yof(d[key])) for d in data]
        for i in range(len(pts) - 1):
            p.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                          color=color, sw=2.4))
        for xx, yy in pts:
            p.append(circle(xx, yy, 4, fill=BG, stroke=color, sw=2))
        p.append(text(pts[-1][0] + 14, pts[-1][1] + 4, lab, size=12,
                      color=color, anchor="start", bold=True))

    # оптимум
    xopt, yopt = xof(30.0), yof(0.9783)
    p.append(circle(xopt, yopt, 8, fill="none", stroke=NEG, sw=2.2))
    bb, bw, bh = textbox(xopt - 42, PY - 32, "оптимум 0.978", size=11, bold=True,
                         fill=BG, stroke=NEG, sw=1.4, color=NEG)
    p.append(bb)
    p.append(line(xopt, PY - 20, xopt, yopt - 10, color=NEG, sw=1.2, dash="3 3"))

    # точка M-Systems
    xms, yms = xof(3.0), yof(0.8865)
    p.append(circle(xms, yms, 8, fill="none", stroke=INK, sw=2.0))
    bb, bw, bh = textbox(xms + 66, yof(0.66), ["K ≈ 1000 —", "мітла M-Systems:", "0.89, тобто 91%", "від оптимуму"],
                         size=11, fill=BG, stroke=INK, sw=1.3, color=INK)
    p.append(bb)
    p.append(line(xms + 8, yms + 6, xms + 52, yof(0.72), color=INK, sw=1.1, dash="3 3"))

    bb, bw, bh = textbox(W / 2, 508,
                         ["Перша ж мітла коштує вчетверо більше за все подальше налаштування:",
                          "0.20 → 0.81 від самого факту статичного вирівнювання, і лише 0.81 → 0.98 від вибору K."],
                         size=11, bold=True, fill="#fdf6e0", stroke=AMBERS, sw=1.5, color=INK)
    p.append(bb)

    render(os.path.join(OUT, "math-sweep-optimum.svg"), W, H, *p,
           title="Як часто мести: η росте, WAF доплачує — і десь є максимум")


if __name__ == "__main__":
    fig_hotspot()
    fig_mapping()
    fig_dynstat()
    fig_hist_timeline()
    fig_proj_layout()
    fig_proj_writepath()
    fig_proj_spread()
    fig_math_histogram()
    fig_math_tbw_ladder()
    fig_math_sweep()
    print("OK: figures written to", OUT)
