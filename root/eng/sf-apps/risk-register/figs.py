# -*- coding: utf-8 -*-
"""Фігури до статті «Ризик-реєстр як живий артефакт». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: сітка ризиків (ймовірність × вплив) з чотирма діями ────────────
def fig_grid():
    W, H = 720, 560
    # координати сітки
    gx, gy = 150, 90          # лівий-верхній кут сітки
    gw, gh = 470, 380         # розмір поля
    frags = []

    # осі-підписи
    frags.append(text(gx + gw / 2, gy + gh + 78, "Вплив, якщо станеться  →", size=15, bold=True))
    # вертикальний підпис осі ліворуч
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="15" fill="%s" '
                 'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">'
                 '↑  Імовірність</text>' % (gx - 82, gy + gh / 2, FONT, INK, gx - 82, gy + gh / 2))

    # чотири клітини 2×2
    cw, ch = gw / 2, gh / 2
    cells = [
        # (col, row, заливка, назва дії, колір рамки)
        (0, 0, "#fdecea", "СТЕЖ І ГОТУЙ ПЛАН\n(висока ймовірн. ×\nвеликий удар)", POS),
        (1, 0, "#fef6e7", "СТЕЖ БЛИЗЬКО\n(рідко, але\nбило б боляче)", "#b8860b"),
        (0, 1, "#eaf3ec", "ПОГЛИНЬ У РОБОТІ\n(часто, але\nдрібно)", FIELD),
        (1, 1, "#eef1f5", "ПРИЙМИ Й ЗАБУДЬ\n(навряд і\nне страшно)", MUTED),
    ]
    for col, row, fill, label, br in cells:
        x = gx + col * cw
        y = gy + row * ch
        frags.append(rect(x, y, cw, ch, fill=fill, stroke=br, sw=2, rx=8))
        frags.append(fitbox(x + 12, y + ch / 2 - 34, cw - 24, 68, label,
                            size=13, fill="none", stroke="none", bold=True, color=INK))

    # мітки країв осей
    frags.append(text(gx + cw / 2, gy + gh + 52, "малий", size=12, color=MUTED))
    frags.append(text(gx + cw + cw / 2, gy + gh + 52, "великий", size=12, color=MUTED))
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">низька</text>'
                 % (gx - 40, gy + gh - ch / 2, FONT, MUTED, gx - 40, gy + gh - ch / 2))
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">висока</text>'
                 % (gx - 40, gy + ch / 2, FONT, MUTED, gx - 40, gy + ch / 2))

    render(os.path.join(IMG, "grid.svg"), W, H, *frags,
           title="Куди тягнути увагу: ймовірність × вплив")


# ── Фігура 2: живий реєстр (петля станів) проти мертвого ─────────────────────
def fig_living():
    W, H = 760, 470
    frags = []

    # ── зверху: живий цикл ──
    frags.append(text(200, 58, "ЖИВИЙ реєстр — стани течуть", size=15, bold=True, color=FIELD))
    cy = 150
    xs = [110, 300, 490]
    labels = ["ВІДКРИТИЙ\nвиявили, оцінили", "У РОБОТІ\nдіємо, збиваємо", "ЗАКРИТИЙ\nминув або\nстався"]
    bw, bh = 150, 66
    boxes = []
    for x, lab in zip(xs, labels):
        frags.append(fitbox(x - bw / 2, cy - bh / 2, bw, bh, lab, size=12,
                            fill="#eaf3ec", stroke=FIELD, sw=2, bold=True))
        boxes.append((x, cy))
    # стрілки між ними
    frags.append(arrow(xs[0] + bw / 2, cy, xs[1] - bw / 2, cy, color=FIELD, sw=2))
    frags.append(arrow(xs[1] + bw / 2, cy, xs[2] - bw / 2, cy, color=FIELD, sw=2))
    # петля повернення (переоцінка) — дугою зверху
    frags.append('<path d="M %d %d C %d %d, %d %d, %d %d" fill="none" stroke="%s" '
                 'stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="5 4"/>'
                 % (xs[2], cy - bh / 2, xs[2], cy - 72, xs[0], cy - 72, xs[0], cy - bh / 2, FIELD))
    frags.append(text((xs[0] + xs[2]) / 2, cy - 78, "щотижня перечитуємо: оцінки зсунулись?",
                     size=12, color=FIELD, italic=True))
    # нові ризики вливаються
    frags.append(arrow(xs[0], cy + bh / 2 + 40, xs[0], cy + bh / 2 + 6, color=FIELD, sw=2))
    frags.append(text(xs[0], cy + bh / 2 + 58, "нові ризики", size=12, color=FIELD))
    # закриті йдуть у пам'ять
    frags.append(arrow(xs[2], cy + bh / 2 + 6, xs[2], cy + bh / 2 + 40, color=MUTED, sw=1.8))
    frags.append(text(xs[2], cy + bh / 2 + 58, "в архів, з уроком", size=12, color=MUTED))

    # роздільник
    frags.append(line(40, 300, W - 40, 300, color="#d0d0d0", sw=1.2, dash="4 4"))

    # ── знизу: мертвий реєстр ──
    frags.append(text(230, 348, "МЕРТВИЙ реєстр — таблиця пилюки", size=15, bold=True, color=MUTED))
    dcy = 410
    frags.append(fitbox(90, dcy - 30, 250, 60,
                        "написали раз на старті", size=13, fill=FILL, stroke=MUTED, sw=1.8))
    # перекреслена стрілка — нічого не тече
    frags.append(line(345, dcy, 430, dcy, color="#c0392b", sw=2))
    frags.append(text(388, dcy - 12, "×", size=22, color="#c0392b", bold=True))
    frags.append(fitbox(435, dcy - 30, 250, 60,
                        "більше не відкрили", size=13, fill=FILL, stroke=MUTED, sw=1.8))

    render(os.path.join(IMG, "living.svg"), W, H, *frags)


# ── Фігура 3: анатомія одного рядка реєстру ─────────────────────────────────
def fig_row():
    W, H = 720, 430
    frags = []
    # один рядок як картка з полями
    cols = [
        ("Опис ризику", "«Vendor-API\nвідмовить під\nпіковим навант.»", 172),
        ("Ймовір.", "середня", 92),
        ("Вплив", "великий", 92),
        ("Ознака-тригер", "p95 latency\n> 800 мс", 132),
        ("Хто веде", "Оля,\nдо 12 черв.", 110),
    ]
    x = 40
    top = 120
    rowh = 108
    frags.append(text(W / 2, 58, "Один рядок реєстру: не «страшно», а що робити",
                     size=16, bold=True))
    for head, body, w in cols:
        # шапка
        frags.append(rect(x, top, w, 34, fill="#eef1f5", stroke=LINE, sw=1.5, rx=6))
        frags.append(fitbox(x + 4, top + 3, w - 8, 28, head, size=12, fill="none",
                            stroke="none", bold=True))
        # тіло
        frags.append(fitbox(x, top + 40, w, rowh - 40, body, size=12,
                            fill=FILL, stroke=LINE, sw=1.4))
        x += w + 8

    # пояснення знизу — що робить рядок «живим»
    ey = top + rowh + 60
    frags.append(fitbox(40, ey, 320, 76,
                        "БЕЗ тригера й власника —\nце просто страшилка:\nніхто не знає, коли бити\nна сполох і хто діє",
                        size=13, fill="#fdecea", stroke=POS, sw=1.8, color=INK))
    frags.append(fitbox(390, ey, 290, 76,
                        "З тригером і власником —\nце план: ознака вмикає\nдію, людина відповідає",
                        size=13, fill="#eaf3ec", stroke=FIELD, sw=1.8, color=INK))

    render(os.path.join(IMG, "row.svg"), W, H, *frags)


# ── Фігура 4 (hist): три течії, що сходяться в практику реєстру ──────────────
def fig_timeline():
    W, H = 940, 560
    frags = []

    frags.append(text(W / 2, 32, "Три течії, з яких визрів реєстр ризиків",
                     size=17, bold=True))

    # спільна вісь часу знизу
    ax_y = 470
    x0, x1 = 70, 870
    frags.append(line(x0, ax_y, x1, ax_y, color=MUTED, sw=1.5))
    for yr, xx in [("1987", 150), ("1989", 300), ("1996", 470), ("2003", 640), ("2004", 720)]:
        frags.append(line(xx, ax_y - 5, xx, ax_y + 5, color=MUTED, sw=1.5))
        frags.append(text(xx, ax_y + 22, yr, size=12, color=MUTED, bold=True))
    frags.append(text(x1 - 6, ax_y + 22, "рік →", size=11, color=MUTED, anchor="end"))

    # ── смуга 1: PMBOK (американська методологія) ──
    y1 = 95
    frags.append(text(x0, y1 - 24, "PMBOK — американська методологія (ризик росте до центральної галузі)",
                     size=12, color=NEG, bold=True, anchor="start"))
    steps1 = [
        (150, "білий папір\n1987", "#eaf0fd"),
        (470, "Guide, 1-е вид.\n1996 · ризик — 1 з 9 галузей", "#eaf0fd"),
        (720, "3-є вид. 2004\nризик — центральна галузь", "#eaf0fd"),
    ]
    prev = None
    for xx, lab, fill in steps1:
        body, bw, bh = textbox(xx, y1, lab, size=11, fill=fill, stroke=NEG, sw=1.6)
        if prev is not None:
            frags.append(arrow(prev, y1, xx - bw / 2, y1, color=NEG, sw=1.6))
        frags.append(body)
        prev = xx + bw / 2

    # ── смуга 2: PROMPT → PRINCE → PRINCE2 (британський стандарт) ──
    y2 = 210
    frags.append(text(x0, y2 - 26, "PROMPT → PRINCE → PRINCE2 — британський урядовий стандарт (реєстр = обов'язковий продукт)",
                     size=12, color=POS, bold=True, anchor="start"))
    steps2 = [
        (150, "PROMPT II\n(Simpact)", "#fdecea"),
        (300, "PRINCE\nCCTA, 1989", "#fdecea"),
        (470, "PRINCE2, 1996\nреєстр ризиків —\nуправл. продукт", "#fdecea"),
    ]
    prev = None
    for xx, lab, fill in steps2:
        body, bw, bh = textbox(xx, y2, lab, size=11, fill=fill, stroke=POS, sw=1.6)
        if prev is not None:
            frags.append(arrow(prev, y2, xx - bw / 2, y2, color=POS, sw=1.6))
        frags.append(body)
        prev = xx + bw / 2

    # ── смуга 3: RAID (низова практика) ──
    y3 = 320
    frags.append(text(x0, y3 - 22, "RAID — низова практика без єдиного автора",
                     size=12, color=MUTED, bold=True, anchor="start"))
    body, bw, bh = textbox(150, y3,
                           "журнал R·A·I·D\nризики · припущення ·\nпроблеми · залежності",
                           size=11, fill=FILL, stroke=MUTED, sw=1.6)
    frags.append(body)
    frags.append(text(150 + bw / 2 + 150, y3, "склалося знизу, без дати й патенту",
                     size=11, color=MUTED, italic=True, anchor="middle"))

    # ── смуга 4: «Вальс із ведмедями» (програмна інженерія) ──
    y4 = 400
    body, bw, bh = textbox(640, y4,
                           "«Вальс із ведмедями»\nDeMarco & Lister · Dorset House · 2003\nпетля дій + 5 ядрових ризиків ПЗ",
                           size=11, fill="#eaf3ec", stroke=FIELD, sw=1.8, bold=False)
    frags.append(body)
    frags.append(text(640, y4 - bh / 2 - 10, "мова ризику для програмної інженерії",
                     size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "timeline.svg"), W, H, *frags)


# ── ДЕТАЛЬНА: Фігура 5 — експозиція як середнє (центр ваги) розподілу ────────
def fig_exposure_mean():
    W, H = 820, 440
    frags = []
    ax_y = 330
    x0, x1 = 100, 750
    frags.append(line(x0, ax_y, x1, ax_y, color=MUTED, sw=1.5))
    frags.append(text(x1, ax_y + 26, "збиток →", size=12, color=MUTED, anchor="end"))

    scale = 250.0           # px на одиницю ймовірності
    bx0, bx1 = 200, 660     # позиції: збиток 0 та збиток L
    p0, p = 0.8, 0.2
    bw = 60
    # «вага» шансу, що нічого не сталося (збиток 0)
    h0 = p0 * scale
    frags.append(rect(bx0 - bw / 2, ax_y - h0, bw, h0, fill="#eaf0fd", stroke=NEG, sw=2, rx=4))
    frags.append(text(bx0, ax_y - h0 - 30, "нічого не сталося", size=12, color=MUTED))
    frags.append(text(bx0, ax_y - h0 - 12, "шанс 1−p = 0.8", size=13, color=NEG, bold=True))
    frags.append(text(bx0, ax_y + 26, "збиток 0", size=12))
    # «вага» шансу удару (збиток L)
    hL = p * scale
    frags.append(rect(bx1 - bw / 2, ax_y - hL, bw, hL, fill="#fdecea", stroke=POS, sw=2, rx=4))
    frags.append(text(bx1, ax_y - hL - 30, "стався удар", size=12, color=MUTED))
    frags.append(text(bx1, ax_y - hL - 12, "шанс p = 0.2", size=13, color=POS, bold=True))
    frags.append(text(bx1, ax_y + 26, "збиток L", size=12))
    # точка рівноваги = очікуваний збиток p·L уздовж осі
    ex = bx0 + p * (bx1 - bx0)
    frags.append(line(ex, ax_y, ex, 165, color=FIELD, sw=2, dash="5 4"))
    frags.append(text(ex + 14, 158, "E[збиток] = p · L", size=14, color=FIELD, bold=True, anchor="start"))
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
                 % (ex, ax_y + 3, ex - 12, ax_y + 22, ex + 12, ax_y + 22, FIELD))
    frags.append(text(ex + 120, ax_y + 40, "центр ваги розподілу", size=12, color=FIELD, anchor="middle"))
    render(os.path.join(IMG, "exposure-mean.svg"), W, H, *frags,
           title="Експозиція — це центр ваги розподілу збитку")


# ── ДЕТАЛЬНА: Фігура 6 — теплова матриця бреше (діапазонне стиснення) ─────────
def fig_heatmap_lie():
    W, H = 900, 570
    frags = []
    gx, gy, cell, n = 150, 100, 60, 5

    def band(prod):
        if prod <= 4:  return "#eaf3ec", FIELD
        if prod <= 8:  return "#fef6e7", "#b8860b"
        if prod <= 14: return "#fce8d8", "#d35400"
        return "#fdecea", POS

    for ci in range(n):
        for ri in range(n):
            colrank = ci + 1        # вплив, зліва направо 1…5
            rowrank = n - ri        # ймовірність, знизу вгору 1…5
            fill, _ = band(colrank * rowrank)
            frags.append(rect(gx + ci * cell, gy + ri * cell, cell, cell,
                              fill=fill, stroke="#ffffff", sw=2, rx=0))
    frags.append(rect(gx, gy, n * cell, n * cell, fill="none", stroke=MUTED, sw=1.5, rx=0))

    frags.append(text(gx + n * cell / 2, gy + n * cell + 40, "Вплив (ранг 1…5)  →", size=13, bold=True))
    frags.append(text(gx + 4, gy + n * cell + 22, "дрібно", size=11, color=MUTED, anchor="start"))
    frags.append(text(gx + n * cell - 4, gy + n * cell + 22, "катастрофа", size=11, color=MUTED, anchor="end"))
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" text-anchor="middle" '
                 'font-weight="700" transform="rotate(-90 %.1f %.1f)">↑ Імовірність (ранг 1…5)</text>'
                 % (gx - 28, gy + n * cell / 2, FONT, INK, gx - 28, gy + n * cell / 2))

    def center(colrank, rowrank):
        return gx + (colrank - 0.5) * cell, gy + (n - rowrank + 0.5) * cell

    ax_, ay_ = center(3, 3)
    bx_, by_ = center(5, 1)
    cax = 660
    boxA, wA, hA = textbox(cax, 165,
                           "Ризик A — «оранжевий»\nсередня × середній\n0.3 × 100 тис. = 30 тис.\nранг: 3 × 3 = 9",
                           size=12, fill="#fce8d8", stroke="#d35400", sw=1.8)
    boxB, wB, hB = textbox(cax, 360,
                           "Ризик B — «жовтий», нижче\nрідкісний × катастрофа\n0.05 × 2 млн = 100 тис.\nранг: 1 × 5 = 5",
                           size=12, fill="#fef6e7", stroke="#b8860b", sw=1.8)
    frags.append(line(ax_ + 15, ay_, cax - wA / 2, 175, color="#d35400", sw=1.5))
    frags.append(line(bx_ + 15, by_, cax - wB / 2, 360, color="#b8860b", sw=1.5))
    frags.append(boxA)
    frags.append(boxB)
    frags.append(circle(ax_, ay_, 15, fill=INK, stroke="#ffffff", sw=2))
    frags.append(text(ax_, ay_ + 5, "A", size=15, color="#ffffff", bold=True))
    frags.append(circle(bx_, by_, 15, fill=INK, stroke="#ffffff", sw=2))
    frags.append(text(bx_, by_ + 5, "B", size=15, color="#ffffff", bold=True))

    frags.append(fitbox(130, 500, 640, 58,
                        "Матриця ставить A вище за B — хоча очікуваний збиток B утричі\n"
                        "більший. Це діапазонне стиснення: ранг 5 однаково накриває\n"
                        "і 1 млн, і 100 млн збитку.",
                        size=12, fill=FILL, stroke=POS, sw=1.8))
    render(os.path.join(IMG, "heatmap-lie.svg"), W, H, *frags,
           title="Чому теплова матриця бреше: однаковий колір ≠ однаковий збиток")


# ── ДЕТАЛЬНА: Фігура 7 — вигоряння ризику (експозиція в часі) ────────────────
def fig_burndown():
    W, H = 840, 470
    frags = []
    ox, oy, xr, yt = 100, 390, 770, 70
    frags.append(line(ox, oy, xr, oy, color=MUTED, sw=1.5))
    frags.append(line(ox, oy, ox, yt, color=MUTED, sw=1.5))
    frags.append(text(xr, oy + 26, "час, спринти →", size=12, color=MUTED, anchor="end"))
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" text-anchor="middle" '
                 'transform="rotate(-90 %.1f %.1f)">Сукупна експозиція  Σ p·L  →</text>'
                 % (ox - 26, (oy + yt) / 2, FONT, MUTED, ox - 26, (oy + yt) / 2))

    living = [(100, 110), (235, 110), (235, 175), (360, 175), (360, 255), (475, 255),
              (475, 238), (560, 238), (560, 305), (690, 305), (690, 338), (770, 338)]
    frags.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.5"/>'
                 % (" L ".join("%.0f %.0f" % pt for pt in living), FIELD))
    dead = [(100, 110), (320, 103), (540, 95), (770, 84)]
    frags.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6 5"/>'
                 % (" L ".join("%.0f %.0f" % pt for pt in dead), POS))
    frags.append(line(ox, 355, xr, 355, color=MUTED, sw=1.2, dash="3 4"))
    frags.append(text(xr, 350, "залишковий рівень (прийняті ризики)", size=11, color=MUTED, anchor="end"))

    # легенда у вільній смузі праворуч
    frags.append(rect(468, 138, 300, 74, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    frags.append(line(486, 162, 520, 162, color=FIELD, sw=3))
    frags.append(text(530, 166, "живий: щотижня ретирує → спадає", size=11, anchor="start"))
    frags.append(line(486, 190, 520, 190, color=POS, sw=3, dash="6 5"))
    frags.append(text(530, 194, "без ритуалу: копиться → росте", size=11, anchor="start"))

    frags.append(line(500, 232, 500, 250, color=MUTED, sw=1.2))
    frags.append(text(500, 226, "новий ризик влився", size=11, color=MUTED))
    frags.append(text(120, 100, "старт: Σ p·L усіх відкритих ризиків", size=11, color=INK, anchor="start"))
    render(os.path.join(IMG, "burndown.svg"), W, H, *frags,
           title="Вигоряння ризику: жива експозиція мусить спадати")


# ── ДЕТАЛЬНА: Фігура 8 — життєвий цикл ризику (стан-машина з RAID-переходом) ──
def _node(cx, cy, s, fill, stroke, sw=1.9, size=12):
    body, w, h = textbox(cx, cy, s, size=size, fill=fill, stroke=stroke, sw=sw, bold=True)
    return {"f": body, "x": cx, "y": cy, "w": w, "h": h}


def _edge(a, b, color=LINE, dash=None, gap=6):
    dx, dy = b["x"] - a["x"], b["y"] - a["y"]

    def clip(nd, ux, uy):
        if ux == 0 and uy == 0:
            return nd["x"], nd["y"]
        sx = (nd["w"] / 2 + gap) / abs(ux) if ux else 1e9
        sy = (nd["h"] / 2 + gap) / abs(uy) if uy else 1e9
        s = min(sx, sy)
        return nd["x"] + ux * s, nd["y"] + uy * s

    x1, y1 = clip(a, dx, dy)
    x2, y2 = clip(b, -dx, -dy)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" '
            'marker-end="url(#arrow)"%s/>' % (x1, y1, x2, y2, color, d))


def fig_states():
    W, H = 980, 560
    frags = []
    N1 = _node(120, 95,  "Виявлений", "#eef1f5", MUTED)
    N2 = _node(120, 250, "Оцінений\np · L, кут,\nвласник, тригер", "#eef1f5", INK)
    N3 = _node(375, 90,  "Прийнятий\n(і забутий)", "#eef1f5", MUTED)
    N4 = _node(375, 250, "Під наглядом\n(тригер зведено)", "#fef6e7", "#b8860b")
    N5 = _node(375, 425, "Пом'якшується\n(діємо наперед)", "#eaf3ec", FIELD)
    N7 = _node(660, 120, "Закритий\nминув / пом'якшено", "#eaf3ec", FIELD)
    N6 = _node(660, 435, "Матеріалізувався\n= ПРОБЛЕМА\n(у журнал проблем)", "#fdecea", POS)
    N8 = _node(870, 265, "В архіві\nз уроком", "#eef1f5", INK)

    # ребра (спершу лінії, потім вузли — щоб рамки лягли зверху)
    frags.append(_edge(N1, N2))
    frags.append(_edge(N2, N3))
    frags.append(_edge(N2, N4))
    frags.append(_edge(N2, N5))
    frags.append(_edge(N3, N7, color=MUTED))
    frags.append(_edge(N4, N7, color=FIELD))
    frags.append(_edge(N5, N7, color=FIELD))
    frags.append(_edge(N4, N6, color=POS))
    frags.append(_edge(N7, N8))
    frags.append(_edge(N6, N8, color=MUTED))
    # петля переоцінки — дугою під наглядом назад до оцінки
    frags.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" '
                 'stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#arrow)"/>'
                 % (N4["x"] - N4["w"] / 2, N4["y"] + 22, 250, 350, 150, 340,
                    N2["x"], N2["y"] + N2["h"] / 2 + 6, MUTED))
    frags.append(text(232, 360, "перегляд:", size=11, color=MUTED))
    frags.append(text(232, 376, "переоцінка кута", size=11, color=MUTED))

    for nd in (N1, N2, N3, N4, N5, N6, N7, N8):
        frags.append(nd["f"])

    # короткі підписи-переходи (осторонь від ліній)
    frags.append(text(548, 300, "тригер!", size=11, color=POS, bold=True))
    frags.append(text(520, 168, "минув", size=11, color=FIELD, bold=True))
    frags.append(text(800, 372, "розв'язано", size=11, color=MUTED))
    render(os.path.join(IMG, "states.svg"), W, H, *frags,
           title="Життєвий шлях ризику: гілки, тригер і межа «ризик → проблема»")


# ── MATH-вставка: Фігура 9 — однакове середнє, різний хвіст (кореляція) ───────
def fig_math_corr_tail():
    W, H = 860, 600
    frags = []
    X0, X1 = 190, 740          # loss 0 … 1 млн
    def xL(v): return X0 + (v / 1_000_000.0) * (X1 - X0)
    k = 175.0 / 0.8            # висота стовпця на одиницю ймовірності
    bw = 52

    def bar(cx, base, p, fill, stroke):
        h = p * k
        out = rect(cx - bw / 2, base - h, bw, h, fill=fill, stroke=stroke, sw=2, rx=4)
        out += text(cx, base - h - 9, ("%.2f" % p).lstrip("0"), size=13, color=stroke, bold=True)
        return out

    def up_tri(cx, apex, col):   # маркер-трикутник (path — svgcheck не чіпає)
        return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
                % (cx, apex, cx - 6, apex + 12, cx + 6, apex + 12, col))

    # ── панель А: незалежні ──
    base1 = 250
    frags.append(text(X0 - 20, 66, "НЕЗАЛЕЖНІ — удари не збігаються", size=14, bold=True,
                     color=NEG, anchor="start"))
    frags.append(line(X0 - 30, base1, X1 + 40, base1, color=MUTED, sw=1.5))
    frags.append(bar(xL(0),        base1, 0.64, "#eaf0fd", NEG))
    frags.append(bar(xL(500_000),  base1, 0.32, "#eaf0fd", NEG))
    frags.append(bar(xL(1_000_000),base1, 0.04, "#eaf0fd", NEG))
    frags.append(up_tri(xL(500_000), base1, FIELD))
    frags.append(text(xL(500_000), base1 + 27, "P₉₅ = 500 тис.", size=12, color=FIELD, bold=True))

    # ── панель B: зчеплені ──
    base2 = 520
    frags.append(text(X0 - 20, 322, "ЗЧЕПЛЕНІ — б'ють разом", size=14,
                     bold=True, color=POS, anchor="start"))
    frags.append(line(X0 - 30, base2, X1 + 40, base2, color=MUTED, sw=1.5))
    frags.append(bar(xL(0),         base2, 0.80, "#fdecea", POS))
    frags.append(bar(xL(1_000_000), base2, 0.20, "#fdecea", POS))
    frags.append(up_tri(xL(1_000_000), base2, FIELD))
    frags.append(text(xL(1_000_000), base2 + 22, "P₉₅ = 1 млн", size=12, color=FIELD, bold=True))

    # підписи осі під нижньою панеллю
    for v, lab in [(0, "0"), (500_000, "500 тис."), (1_000_000, "1 млн")]:
        frags.append(text(xL(v), base2 + 46, lab, size=12, color=MUTED))
    frags.append(text((X0 + X1) / 2, base2 + 68, "збиток за квартал →", size=12, color=MUTED))

    # маркер середнього 200 тис. — короткі стовпчики В МЕЖАХ панелей (не в коридорі)
    xm = xL(200_000)
    frags.append(line(xm, base1, xm, 110, color=INK, sw=1.6, dash="3 4"))
    frags.append(line(xm, base2, xm, 370, color=INK, sw=1.6, dash="3 4"))
    frags.append(text(xm, 284, "середнє = 200 тис.", size=13, bold=True))
    frags.append(text(xm, 300, "однакове в обох!", size=12, color=MUTED))

    render(os.path.join(IMG, "corr-tail.svg"), W, H, *frags,
           title="Однакове середнє, різний хвіст: резерв диктує кореляція")


# ── MATH-вставка: Фігура 10 — звідки (o+4m+p)/6: середнє скошеної бети ────────
def _beta_area(x0, x1, ybase, ypeak, alpha, betap, n=181):
    import math
    def f(t):
        if t <= 0 or t >= 1:
            return 0.0
        return math.exp((alpha - 1) * math.log(t) + (betap - 1) * math.log(1 - t))
    ts = [i / (n - 1.0) for i in range(n)]
    fs = [f(t) for t in ts]
    fmax = max(fs) or 1.0
    pts = [(x0 + t * (x1 - x0), ybase - (fv / fmax) * ypeak) for t, fv in zip(ts, fs)]
    d = "M %.1f %.1f " % (x0, ybase)
    d += " ".join("L %.1f %.1f" % p for p in pts)
    d += " L %.1f %.1f Z" % (x1, ybase)
    return d, pts


def fig_math_pert_beta():
    W, H = 860, 470
    frags = []
    o, m, p = 6.0, 10.0, 24.0
    X0, X1 = 120, 760
    def xD(v): return X0 + (v - o) / (p - o) * (X1 - X0)
    base = 360
    peak = 210
    alpha = 1 + 4 * (m - o) / (p - o)     # = 1.888…
    betap = 1 + 4 * (p - m) / (p - o)     # = 4.111… ; alpha+betap = 6

    d, _ = _beta_area(X0, X1, base, peak, alpha, betap)
    frags.append('<path d="%s" fill="#eef3ff" stroke="%s" stroke-width="2.5"/>' % (d, NEG))
    frags.append(line(X0 - 10, base, X1 + 20, base, color=MUTED, sw=1.5))

    # вертикалі: мода, середнє, середина розмаху
    def marker(v, col, lab, laby, dash="5 4"):
        x = xD(v)
        frags.append(line(x, base, x, base - peak - 6, color=col, sw=1.8, dash=dash))
        frags.append(text(x, base + 20, lab, size=12, color=col, bold=True))
        return x
    marker(m, "#b8860b", "мода m=10", 0)
    xmu = xD((o + 4 * m + p) / 6.0)
    frags.append(line(xmu, base, xmu, base - peak - 6, color=POS, sw=2, dash=None))
    frags.append(text(xmu, base + 40, "μ = 11.67", size=12, color=POS, bold=True))
    marker((o + p) / 2, MUTED, "середина 15", 0)

    # мітки кінців
    frags.append(text(X0, base + 40, "o = 6", size=12, color=NEG))
    frags.append(text(X1, base + 40, "p = 24", size=12, color=NEG))
    frags.append(text((X0 + X1) / 2, base + 60, "тривалість, днів →", size=12, color=MUTED))

    # легенда-виведення у порожньому правому-верхньому куті (пік — ліворуч)
    legend, lw, lh = textbox(
        628, 132,
        "Бета на [o, p], α+β = 6\n"
        "α = 1+4(m−o)/(p−o) = 1.89\n"
        "β = 1+4(p−m)/(p−o) = 4.11\n"
        "⇒ середнє = (o+4m+p)/6\n"
        "   = ⅔·мода + ⅓·середина",
        size=13, fill="#f4f6f8", stroke=INK, sw=1.6)
    frags.append(legend)

    # σ — окремий, ±3σ-евристичний «÷6»
    sig, sw_, sh_ = textbox(628, 300,
                            "розмах ≈ 6σ  ⇒  σ ≈ (p−o)/6 = 3.0\n(окрема евристика, не та сама бета)",
                            size=12, fill="#fff8ec", stroke="#b8860b", sw=1.6)
    frags.append(sig)

    render(os.path.join(IMG, "pert-beta.svg"), W, H, *frags,
           title="Звідки (o+4m+p)/6: середнє скошеної бети з α+β = 6")


# ── MATH-вставка: Фігура 11 — резерв як перцентиль між двома хибними межами ───
def fig_math_reserve_band():
    W, H = 860, 430
    frags = []
    X0, X1 = 90, 690
    base = 320
    peak = 190
    # скошений праворуч агрегат (бета α=2.4, β=5)
    d, pts = _beta_area(X0, X1, base, peak, 2.4, 5.0)
    frags.append('<path d="%s" fill="#eef7f0" stroke="%s" stroke-width="2.5"/>' % (d, FIELD))
    frags.append(line(X0 - 10, base, W - 20, base, color=MUTED, sw=1.5))
    frags.append(text((X0 + X1) / 2, base + 40, "сукупний строк / кошторис проєкту →",
                     size=12, color=MUTED))

    def pick(frac):   # x на кривій за часткою шляху зліва
        i = int(frac * (len(pts) - 1))
        return pts[i][0]

    xmean = pick(0.34)      # ≈ Σ середніх (близько піка-медіани)
    x80 = pick(0.52)        # P80 — правіше
    xpess = pick(0.93)      # Σ песимістичних — глибоко у хвості

    # затінити «у 80% світів вистачить» (від початку до P80)
    fillpts = [(X0, base)] + [pt for pt in pts if pt[0] <= x80] + [(x80, base)]
    dd = "M " + " L ".join("%.1f %.1f" % q for q in fillpts) + " Z"
    frags.append('<path d="%s" fill="#d6ebdd" stroke="none" opacity="0.7"/>' % dd)

    def stem(x, col, lab1, lab2, laby, sw=2, dash=None):
        frags.append(line(x, base, x, laby + 6, color=col, sw=sw,
                          **({"dash": dash} if dash else {})))
        frags.append(text(x, laby - 4, lab1, size=12, color=col, bold=True))
        if lab2:
            frags.append(text(x, laby - 20, lab2, size=11, color=col))

    stem(xmean, MUTED, "Σ середніх", "P₅₀ — замало", 150, sw=1.8, dash="4 4")
    stem(x80, FIELD, "резерв = P₈₀", "у 80% світів досить", 92)
    stem(xpess, POS, "Σ песимістичних", "≈ P₉₉ — забагато", 150, sw=1.8, dash="4 4")

    render(os.path.join(IMG, "reserve-band.svg"), W, H, *frags,
           title="Резерв — це перцентиль, а не сума середніх чи сума найгірших")


# ── MATH-вставка (mitigation-economics): Фігура 12 — черга пом'якшень за важелем ─
def fig_rrl_queue():
    W, H = 860, 460
    frags = []
    x0, xr = 300, 820
    rmax = 4.0

    def sx(v):
        return x0 + v / rmax * (xr - x0)

    top, rowh, bh = 118, 60, 30
    items = [
        ("Кеш-проксі перед вендором", 3.1, True),
        ("Резервний канал сповіщень", 2.2, True),
        ("Тестований бекап-відновлення", 1.5, True),
        ("Другий постачальник", 1.1, True),
        ("Повне дублювання регіону", 0.6, False),
    ]
    baseY = top + (len(items) - 1) * rowh + 34
    frags.append(line(x0, top - 40, x0, baseY, color=MUTED, sw=1.3))
    frags.append(line(x0, baseY, xr, baseY, color=MUTED, sw=1.3))
    for t in range(5):
        xt = sx(t)
        frags.append(line(xt, baseY, xt, baseY + 6, color=MUTED, sw=1))
        frags.append(text(xt, baseY + 22, str(t), size=11, color=MUTED))
    frags.append(text((x0 + xr) / 2, baseY + 44,
                     "Важіль RRL = знята експозиція / вартість пом'якшення  →", size=13, bold=True))
    xc = sx(1.0)
    frags.append(line(xc, top - 46, xc, baseY, color=POS, sw=2, dash="6 4"))
    frags.append(text(xc, top - 52, "поріг окупності  RRL = 1", size=12, color=POS, bold=True))
    for i, (name, rrl, buy) in enumerate(items):
        y = top + i * rowh
        col = FIELD if buy else MUTED
        fil = "#eaf3ec" if buy else "#eef1f5"
        frags.append(fitbox(24, y - bh / 2, 256, bh, name, size=12, fill="none", stroke="none", color=INK))
        frags.append(rect(x0, y - bh / 2, sx(rrl) - x0, bh, fill=fil, stroke=col, sw=1.8, rx=4))
        frags.append(text(sx(rrl) + 22, y + 4, "%.1f" % rrl, size=13, color=col, bold=True))
    render(os.path.join(IMG, "rrl-queue.svg"), W, H, *frags,
           title="Черга пом'якшень: посортуй за важелем, купуй згори вниз")


# ── MATH-вставка (mitigation-economics): Фігура 13 — наведений ризик з'їдає важіль ─
def fig_rrl_secondary():
    W, H = 820, 430
    frags = []
    x0 = 100
    scale = 600.0 / 92500.0

    def wv(v):
        return v * scale

    frags.append(text(W / 2, 56,
                     "Бекап за 60 000 зменшує збиток з 2 млн до 150 тис. (лишок після = 7 500)",
                     size=12, color=MUTED))
    y1 = 150
    frags.append(text(x0 + wv(92500) / 2, y1 - 26,
                     "нібито знято: 100 000 − 7 500 = 92 500", size=12, bold=True))
    frags.append(rect(x0, y1 - 18, wv(92500), 36, fill="#eaf3ec", stroke=FIELD, sw=1.8, rx=4))
    y2 = 250
    frags.append(text(x0 + 300, y2 - 26,
                     "…власний (наведений) ризик пом'якшення повертає частину назад:",
                     size=12, bold=True))
    frags.append(rect(x0, y2 - 18, wv(74000), 36, fill="#eaf3ec", stroke=FIELD, sw=1.8, rx=4))
    frags.append(rect(x0 + wv(74000), y2 - 18, wv(18500), 36, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    frags.append(text(x0 + wv(74000) / 2, y2 + 34, "чисто знято 74 000", size=12, color=FIELD, bold=True))
    frags.append(text(x0 + wv(74000) + wv(18500) / 2, y2 + 34, "наведено −18 500", size=12, color=POS, bold=True))
    y3 = 350
    frags.append(text(215, y3, "наївний RRL ≈ 1.54", size=14, bold=True, color=MUTED))
    frags.append(arrow(330, y3 - 4, 445, y3 - 4, color=INK, sw=2))
    frags.append(text(575, y3, "справжній RRL ≈ 1.23", size=14, bold=True, color=FIELD))
    frags.append(text(W / 2, y3 + 26,
                     "За менш надійного відновлення важіль легко падає під 1 — тому наведене рахують завжди.",
                     size=11, color=MUTED))
    render(os.path.join(IMG, "rrl-secondary.svg"), W, H, *frags,
           title="Пом'якшення несе власний ризик, і він з'їдає важіль")


# ── PROJ-вставка: Фігура 16 — два режими калькулятора (дешеве середнє / дорогий хвіст) ─
def fig_two_regimes():
    W, H = 900, 470
    frags = []
    # спільне джерело — реєстр
    src, sw_, sh_ = textbox(W / 2, 92,
                            "РЕЄСТР\nрядки: p · L  ·  задачі: o, m, p",
                            size=14, fill="#eef1f5", stroke=INK, sw=2, bold=True)
    frags.append(src)

    # ліва гілка — середнє (арифметика)
    lx = 240
    frags.append(arrow(W / 2 - 90, 128, lx + 40, 176, color=NEG, sw=2))
    la, law, lah = textbox(lx, 210, "СЕРЕДНЄ · РАНЖУВАННЯ", size=13,
                           fill="#eaf0fd", stroke=NEG, sw=2, bold=True)
    frags.append(la)
    frags.append(text(lx, 254, "Σ p·L — сума очікуваних", size=12))
    frags.append(fitbox(lx - 175, 276, 350, 96,
                        "• лінійне: сума середніх = середнє суми\n"
                        "• точне й дешеве — тривіальний цикл\n"
                        "• СЛІПЕ до хвоста й до кореляції\n"
                        "→ куди дивитися першими",
                        size=12, fill="#f4f6f8", stroke=NEG, sw=1.6, color=INK))

    # права гілка — хвіст (симуляція)
    rx = 660
    frags.append(arrow(W / 2 + 90, 128, rx - 40, 176, color=POS, sw=2))
    ra, raw, rah = textbox(rx, 210, "РЕЗЕРВ · ХВІСТ", size=13,
                           fill="#fdecea", stroke=POS, sw=2, bold=True)
    frags.append(ra)
    frags.append(text(rx, 254, "Монте-Карло → перцентиль P80", size=12))
    frags.append(fitbox(rx - 175, 276, 350, 96,
                        "• розігруємо реєстр тисячі разів\n"
                        "• БАЧИТЬ кореляцію (спільний корінь)\n"
                        "• дорожче, наближене, з seed\n"
                        "→ скільки закладати в резерв",
                        size=12, fill="#f4f6f8", stroke=POS, sw=1.6, color=INK))

    # застереження внизу
    frags.append(fitbox(150, 402, W - 300, 44,
                        "Не симулюй те, що дає лінійність, і не закладай резерв за середнім:\n"
                        "кореляція міняє лише правий шлях, а середнє — ніколи.",
                        size=12, fill="none", stroke="none", color=MUTED, bold=True))
    render(os.path.join(IMG, "two-regimes.svg"), W, H, *frags,
           title="Один реєстр — два обчислення: дешеве середнє, дорогий хвіст")


# ── PROJ-вставка: Фігура 17 — гістограма Монте-Карло: P80 між двома хибними межами ─
def fig_mc_reserve():
    import math
    W, H = 900, 470
    frags = []
    ox, oy = 70, 396
    x_lo, x_hi, plotw = 20.0, 88.0, 760.0

    def xmap(v):
        return ox + (v - x_lo) / (x_hi - x_lo) * plotw

    top = 168
    # вісь X
    frags.append(line(ox, oy, ox + plotw, oy, color=MUTED, sw=1.5))
    for t in (20, 30, 40, 50, 60, 70, 80):
        frags.append(line(xmap(t), oy, xmap(t), oy + 5, color=MUTED, sw=1.2))
        frags.append(text(xmap(t), oy + 20, str(t), size=11, color=MUTED))
    frags.append(text(ox + plotw, oy + 20, "днів →", size=11, color=MUTED, anchor="end"))

    # гістограма сукупної тривалості — скошене лог-нормальне ядро (детерміновано)
    b0, b1, step = 24, 56, 2
    centers = list(range(b0, b1, step))
    mu, s = math.log(12.0) + 0.10, 0.34
    hs = []
    for c in centers:
        sh = c - 21.0
        hs.append(math.exp(-((math.log(sh) - mu) ** 2) / (2 * s * s)) / sh if sh > 0 else 0.0)
    hmax = max(hs)
    barw = (xmap(b0 + step) - xmap(b0)) * 0.82
    for c, hv in zip(centers, hs):
        bh = hv / hmax * (oy - top)
        frags.append(rect(xmap(c) - barw / 2, oy - bh, barw, bh,
                          fill="#eaf0fd", stroke=NEG, sw=1.0, rx=1))

    def marker(v, ytop, color, dash="5 4", sw=2):
        frags.append(line(xmap(v), oy, xmap(v), ytop, color=color, sw=sw, dash=dash))

    # три маркери (рамки — зверху, лінії — знизу від них)
    marker(26, 100, MUTED)
    b, w, h = textbox(xmap(26), 80, "Σ мод = 26\nнаївний план", size=12,
                      fill="#eef1f5", stroke=MUTED, sw=1.8)
    frags.append(b)

    marker(41, 82, FIELD, dash=None)
    b, w, h = textbox(xmap(41), 62, "P80 = 41\nчесний резерв", size=12,
                      fill="#eaf3ec", stroke=FIELD, sw=2.2, bold=True)
    frags.append(b)

    marker(83, 100, POS)
    b, w, h = textbox(xmap(83), 80, "Σ песим. = 83\nусе лихо разом", size=12,
                      fill="#fdecea", stroke=POS, sw=1.8)
    frags.append(b)

    # дужка «резерв 15 днів» між планом і P80, під віссю
    by = oy + 46
    frags.append(line(xmap(26), by, xmap(41), by, color=INK, sw=1.4))
    frags.append(line(xmap(26), by - 4, xmap(26), by + 4, color=INK, sw=1.4))
    frags.append(line(xmap(41), by - 4, xmap(41), by + 4, color=INK, sw=1.4))
    frags.append(text((xmap(26) + xmap(41)) / 2, by + 16, "резерв 15 днів", size=11, color=INK))

    render(os.path.join(IMG, "mc-reserve.svg"), W, H, *frags,
           title="Монте-Карло кошторису: P80 — чесний резерв між двома хибними межами")


if __name__ == "__main__":
    fig_grid()
    fig_living()
    fig_row()
    fig_timeline()
    fig_exposure_mean()
    fig_heatmap_lie()
    fig_burndown()
    fig_states()
    fig_math_corr_tail()
    fig_math_pert_beta()
    fig_math_reserve_band()
    fig_rrl_queue()
    fig_rrl_secondary()
    fig_two_regimes()
    fig_mc_reserve()
    print("figs done")
