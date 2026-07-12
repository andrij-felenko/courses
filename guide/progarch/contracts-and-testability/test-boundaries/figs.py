# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER = "#e08a1e"


def poly(points, fill=FILL, stroke=LINE, sw=1.5):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (pts, fill, stroke, sw))


def fig_boundary():
    """Три радіуси того самого кола: модульне ⊂ інтеграційне ⊂ наскрізне."""
    W, H = 1000, 540
    cx = 510
    frags = []

    # ── три концентричні рамки (радіуси кола тесту) ──────────────────
    # наскрізне (E2E) — найбільше
    frags.append(rect(250, 120, 520, 330, fill="#fdf3ea", stroke=POS, sw=2.4))
    frags.append(text(262, 142, "НАСКРІЗНИЙ (E2E)", size=12, bold=True,
                      color=POS, anchor="start"))
    # інтеграційне
    frags.append(rect(315, 178, 390, 214, fill="#eef2f6", stroke=NEG, sw=2.2))
    frags.append(text(327, 198, "ІНТЕГРАЦІЙНИЙ", size=12, bold=True,
                      color=NEG, anchor="start"))
    # модульне — найменше
    frags.append(rect(390, 232, 240, 104, fill="#eafaf1", stroke=FIELD, sw=2.2))
    frags.append(text(402, 252, "МОДУЛЬНИЙ", size=12, bold=True,
                      color=FIELD, anchor="start"))

    # вміст кіл — у вільних горизонтальних смугах
    frags.append(text(cx, 296, "decide()", size=17, bold=True))
    frags.append(text(cx, 367, "+ справжній адаптер давача, справжня БД",
                      size=12.5, color=INK))
    frags.append(text(cx, 424, "+ весь хаб, справжня розетка, реальний HTTP",
                      size=12.5, color=INK))

    # ── бічні пояснення торгу ─────────────────────────────────────────
    frags.append(mtext(28, 250, [
        "ближче до центра —",
        "менше справжнього коду:",
        "швидко, точно вказує",
        "на винуватця; але тест",
        "спирається на припущення",
        "про сусідів (дублери)"],
        size=11.5, color=MUTED, anchor="start", lh=1.35))

    frags.append(mtext(792, 258, [
        "далі від центра —",
        "більше справжнього коду:",
        "більше певності в системі;",
        "але повільніше, крихкіше",
        "й гірше локалізує збій"],
        size=11.5, color=MUTED, anchor="start", lh=1.35))

    # ── нижня двобічна стрілка: менше ↔ більше справжнього ────────────
    frags.append(arrow(510, 486, 330, 486, color=MUTED, sw=1.8))
    frags.append(arrow(510, 486, 690, 486, color=MUTED, sw=1.8))
    frags.append(text(322, 508, "менше справжнього", size=12, color=MUTED))
    frags.append(text(698, 508, "більше справжнього", size=12, color=MUTED))

    render(os.path.join(OUT, 'test-boundary.svg'), W, H, *frags,
           title="Рівень тесту — це радіус кола навколо справжнього коду")


def fig_shapes():
    """Піраміда тестів проти перевернутого «ріжка морозива»."""
    W, H = 940, 430
    frags = []

    # роздільник
    frags.append(line(470, 74, 470, 340, color=LINE, sw=1.0, dash="4 6"))

    # ── ЛІВОРУЧ: піраміда (широка основа) ─────────────────────────────
    px = 250
    # три яруси-трапеції знизу вгору
    frags.append(poly([(px - 33, 183), (px + 33, 183), (px + 66, 256),
                       (px - 66, 256)], fill="#eef2f6", stroke=NEG))   # інтегр.
    frags.append(poly([(px - 66, 256), (px + 66, 256), (px + 100, 330),
                       (px - 100, 330)], fill="#eafaf1", stroke=FIELD))  # модул.
    frags.append(poly([(px, 110), (px + 33, 183), (px - 33, 183)],
                      fill="#fdf3ea", stroke=POS))                       # E2E
    frags.append(text(px, 162, "E2E", size=12, bold=True, color=POS))
    frags.append(text(px, 224, "інтеграційні", size=11, color=NEG))
    frags.append(text(px, 300, "модульні", size=13, bold=True, color=FIELD))
    frags.append(text(px, 353, "піраміда (Cohn, 2009)", size=12.5, bold=True))
    frags.append(mtext(px, 376, [
        "маса тестів — унизу, де дешево",
        "й стабільно; вершина вузька"],
        size=10.5, color=MUTED, lh=1.35))

    # ── ПРАВОРУЧ: перевернутий «ріжок» ────────────────────────────────
    rx = 690
    # ложка морозива над широким верхом
    frags.append(circle(rx, 128, 22, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(text(rx, 96, "ручні / UI", size=10.5, color=POS))
    # перевернутий трикутник (вістря вниз): широкий верх → вузьке дно
    frags.append(poly([(rx - 90, 158), (rx + 90, 158), (rx + 62, 210),
                       (rx - 62, 210)], fill="#fdf3ea", stroke=POS))     # E2E/UI
    frags.append(poly([(rx - 62, 210), (rx + 62, 210), (rx + 34, 268),
                       (rx - 34, 268)], fill="#eef2f6", stroke=NEG))     # інтегр.
    frags.append(poly([(rx - 34, 268), (rx + 34, 268), (rx, 322)],
                      fill="#eafaf1", stroke=FIELD))                     # модул.
    frags.append(text(rx, 186, "E2E / UI", size=12, bold=True, color=POS))
    frags.append(text(rx, 242, "інтеграційні", size=11, color=NEG))
    frags.append(text(rx + 78, 300, "мало модульних", size=10, color=FIELD,
                      anchor="start"))
    frags.append(text(rx, 353, "«ріжок морозива» (антипатерн)", size=12.5,
                      bold=True, color=POS))
    frags.append(mtext(rx, 376, [
        "маса тестів — угорі, де повільно",
        "й крихко; регресія коштує дорого"],
        size=10.5, color=MUTED, lh=1.35))

    render(os.path.join(OUT, 'test-shapes.svg'), W, H, *frags,
           title="Дві форми: куди класти масу тестів")


def fig_bug_level_matrix():
    """Три баги × три рівні: кожен баг гине рівно на найдешевшому колі, що його містить."""
    W, H = 890, 380
    frags = []

    # координати колонок (рівнів)
    col_x = [310, 498, 686]      # ліві краї
    CW = 176
    col_c = [x + CW / 2 for x in col_x]        # центри: 398, 586, 774

    # ── заголовки колонок (рівні) + вміст кола ────────────────────────
    heads = [("МОДУЛЬНИЙ", FIELD, "коло: decide()"),
             ("ІНТЕГРАЦІЙНИЙ", NEG, "+ справжній адаптер"),
             ("НАСКРІЗНИЙ", POS, "+ зібраний хаб")]
    for cx, (name, col, sub) in zip(col_c, heads):
        frags.append(text(cx, 54, name, size=13, bold=True, color=col))
        frags.append(text(cx, 72, sub, size=10.5, color=MUTED))

    # ── рядки (баги) ──────────────────────────────────────────────────
    row_y = [88, 170, 252]       # верхні краї
    RH = 70
    row_c = [y + RH / 2 for y in row_y]        # центри: 123, 205, 287

    labels = [["1) decide плутає", "< і > (логіка)"],
              ["2) адаптер: °F", "віддано як °C (шов)"],
              ["3) buildHub губить", "поріг (проводка)"]]
    for cy, lab in zip(row_c, labels):
        frags.append(mtext(26, cy - 7, lab, size=11.5, color=INK,
                           anchor="start", lh=1.3))

    # типи клітин
    STAR = {FIELD: "#eafaf1", NEG: "#eaf0fd", POS: "#fdecea"}

    def cell(ci, ri, kind, col, txt):
        x, y = col_x[ci], row_y[ri]
        if kind == "star":
            return fitbox(x, y, CW, RH, "★ " + txt, size=12,
                          fill=STAR[col], stroke=col, color=INK, bold=True)
        if kind == "blind":
            return fitbox(x, y, CW, RH, txt, size=12,
                          fill="#eef0f2", stroke=MUTED, color=MUTED)
        return fitbox(x, y, CW, RH, txt, size=12,        # redundant
                      fill="#f5f7f8", stroke="#c9ced4", color=MUTED)

    # рядок 1 — баг логіки: ловить найдешевший (модульний), решта повторно
    frags.append(cell(0, 0, "star",  FIELD, "ловить\nколо на decide"))
    frags.append(cell(1, 0, "redun", NEG,   "ловить\n(повторно)"))
    frags.append(cell(2, 0, "redun", POS,   "ловить\n(найдорожче)"))
    # рядок 2 — баг одиниць: модульний сліпий, ловить інтеграційний
    frags.append(cell(0, 1, "blind", FIELD, "сліпий\nфейк дає 18 як факт"))
    frags.append(cell(1, 1, "star",  NEG,   "ловить\nсправжній адаптер"))
    frags.append(cell(2, 1, "redun", POS,   "ловить"))
    # рядок 3 — баг проводки: два сліпі, ловить лише наскрізний
    frags.append(cell(0, 2, "blind", FIELD, "сліпий\nминає buildHub"))
    frags.append(cell(1, 2, "blind", NEG,   "сліпий\nминає buildHub"))
    frags.append(cell(2, 2, "star",  POS,   "ловить\nзібраний хаб"))

    # ── легенда ───────────────────────────────────────────────────────
    frags.append(mtext(443, 350, [
        "★ — найдешевший рівень, що ловить цей клас помилок",
        "«сліпий» — дубль у колі замінив саме те місце, де живе баг"],
        size=10, color=MUTED, lh=1.35))

    render(os.path.join(OUT, 'bug-level-matrix.svg'), W, H, *frags,
           title="Той самий баг гине рівно на найдешевшому колі, що його містить")


def _tl_node(nx, side, year, l2, l3, color):
    """Один вузол таймлайна: рамка з текстом + сполучна лінія до осі (y=215)."""
    cy = 118 if side == "above" else 308
    body, w, h = textbox(nx, cy, [year, l2, l3], size=13, pad=9,
                         stroke=color, fill="#ffffff", color=color)
    edge = cy + h / 2 if side == "above" else cy - h / 2
    conn = line(nx, edge, nx, 215, color=color, sw=1.4)
    dot = circle(nx, 215, 6.5, fill=color, stroke=color, sw=1)
    return conn + body + dot


def fig_timeline():
    """Хронологія форм тестової стратегії — рік, автор, форма."""
    W, H = 1240, 430
    frags = []
    frags.append(text(W / 2, 48,
                      "кожна форма — відповідь на біль свого часу і свого роду систем",
                      size=12.5, color=MUTED))
    frags.append(arrow(80, 215, 1160, 215, color=MUTED, sw=2.0))

    nodes = [
        (130, "above", "2004", "Кон ескізує", "піраміду", NEG),
        (325, "below", "2009", "Кон друкує", "піраміду", NEG),
        (520, "above", "2012", "Скотт:", "ріжок морозива", POS),
        (715, "below", "2014", "Перейра:", "кекс", POS),
        (910, "above", "2016", "Раух: переважно", "інтеграційні", FIELD),
        (1105, "below", "2018", "Додс: трофей;", "Spotify: стільники", FIELD),
    ]
    for nx, side, yr, l2, l3, c in nodes:
        frags.append(_tl_node(nx, side, yr, l2, l3, c))

    def swatch(x, c, label):
        return (rect(x, 378, 15, 15, fill="#ffffff", stroke=c, sw=2.2, rx=3) +
                text(x + 23, 390, label, size=12, color=INK, anchor="start"))
    frags.append(swatch(250, NEG, "піраміда — канон"))
    frags.append(swatch(560, POS, "антипатерни — деформації"))
    frags.append(swatch(905, FIELD, "зсув до інтеграції"))

    render(os.path.join(OUT, 'test-shapes-timeline.svg'), W, H, *frags,
           title="Історія форм тестової стратегії")


def _hexagon(cx, cy, r, fill=FILL, stroke=LINE, sw=1.8):
    import math
    pts = [(cx + r * math.cos(math.radians(60 * i)),
            cy + r * math.sin(math.radians(60 * i))) for i in range(6)]
    return poly(pts, fill=fill, stroke=stroke, sw=sw)


def fig_family():
    """П'ять силуетів: куди кожна форма кладе масу тестів."""
    W, H = 1240, 470
    frags = []
    frags.append(text(W / 2, 48,
                      "ту саму купу тестів малювали по-різному — за тим, де живе ризик",
                      size=12.5, color=MUTED))
    cols = [150, 385, 620, 855, 1090]

    # ── 1. Піраміда (Кон) — маса внизу ────────────────────────────────
    cx = cols[0]
    frags.append(poly([(cx, 78), (cx - 85, 245), (cx + 85, 245)],
                      fill="#eef2f6", stroke=NEG, sw=2))
    frags.append(poly([(cx - 56.7, 190), (cx + 56.7, 190),
                       (cx + 85, 245), (cx - 85, 245)],
                      fill="#eafaf1", stroke=NEG, sw=2))
    frags.append(line(cx - 28.4, 135, cx + 28.4, 135, color=NEG, sw=1.2))

    # ── 2. Ріжок морозива (Скотт) — маса вгорі ────────────────────────
    cx = cols[1]
    frags.append(circle(cx, 100, 25, fill="#fdecea", stroke=POS, sw=2))
    frags.append(poly([(cx - 82, 120), (cx + 82, 120), (cx, 245)],
                      fill="#fdf3ea", stroke=POS, sw=2))
    frags.append(line(cx - 55, 162, cx + 55, 162, color=POS, sw=1.2))

    # ── 3. Стільники (Spotify) — маса в інтеграції ────────────────────
    cx = cols[2]
    frags.append(_hexagon(cx, 95, 22, fill="#eef2f6", stroke=FIELD, sw=1.8))
    frags.append(_hexagon(cx, 160, 54, fill="#eafaf1", stroke=FIELD, sw=2.2))
    frags.append(_hexagon(cx, 226, 22, fill="#eef2f6", stroke=FIELD, sw=1.8))

    # ── 4. Трофей (Додс) — маса в інтеграції ──────────────────────────
    cx = cols[3]
    frags.append(rect(cx - 30, 83, 60, 32, fill="#fdf3ea", stroke=FIELD, sw=1.8, rx=4))
    frags.append(rect(cx - 78, 117, 156, 48, fill="#eafaf1", stroke=FIELD, sw=2.4, rx=6))
    frags.append(rect(cx - 42, 167, 84, 38, fill="#eef2f6", stroke=FIELD, sw=1.8, rx=4))
    frags.append(rect(cx - 55, 207, 110, 38, fill="#f4f6f8", stroke=FIELD, sw=1.8, rx=4))

    # ── 5. Кекс (Перейра) — роздуто скрізь ────────────────────────────
    cx = cols[4]
    frags.append(poly([(cx - 62, 152), (cx - 40, 112), (cx, 96),
                       (cx + 40, 112), (cx + 62, 152)],
                      fill="#fdecea", stroke=POS, sw=2))
    frags.append(rect(cx - 60, 152, 120, 40, fill="#fdf3ea", stroke=POS, sw=1.8, rx=3))
    frags.append(poly([(cx - 55, 245), (cx + 55, 245),
                       (cx + 70, 192), (cx - 70, 192)],
                      fill="#fdecea", stroke=POS, sw=2))

    # ── підписи під кожним силуетом ────────────────────────────────────
    labels = [
        (cols[0], "Піраміда", "Кон, 2009", NEG, "маса — унизу"),
        (cols[1], "Ріжок морозива", "Скотт, 2012", POS, "маса — вгорі"),
        (cols[2], "Стільники", "Spotify, 2018", FIELD, "маса — інтеграція"),
        (cols[3], "Трофей", "Додс, 2018", FIELD, "маса — інтеграція"),
        (cols[4], "Кекс", "Перейра, 2014", POS, "роздуто скрізь"),
    ]
    for cx, name, who, c, cap in labels:
        body, w, h = textbox(cx, 305, [name, who], size=12.5, pad=8,
                             stroke=c, fill="#ffffff", color=c)
        frags.append(body)
        frags.append(text(cx, 350, cap, size=11.5, color=MUTED))

    render(os.path.join(OUT, 'test-shapes-family.svg'), W, H, *frags,
           title="Родина форм: де кожна кладе масу тестів")


if __name__ == '__main__':
    fig_boundary()
    fig_shapes()
    fig_bug_level_matrix()
    fig_timeline()
    fig_family()
    print("figures written to", OUT)
