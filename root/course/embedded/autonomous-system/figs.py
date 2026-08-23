# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорові стрілки-маркери (svgkit дає тільки нейтральну #arrow); тут потрібні
# сині/зелені/червоні наконечники, тож додаємо власні defs у кожну фігуру.
COL_MARKERS = (
    '<defs>'
    '<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '</defs>' % (NEG, FIELD, POS)
)


def carrow(x1, y1, x2, y2, color, mid, sw=2.0):
    """Лінія з кольоровим наконечником (mid ∈ B/G/R)."""
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arr%s)" stroke-linecap="round"/>'
            % (x1, y1, x2, y2, color, sw, mid))


def block(x, y, w, h, lines, fill, stroke, color=INK, size=12.5, bold=True):
    """Кольорова рамка-блок із центрованим багаторядковим написом."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.7, rx=10)
    n = len(lines)
    cy = y + h / 2 - (n - 1) * size * 1.25 / 2 + size * 0.35
    out += mtext(x + w / 2, cy, lines, size=size, color=color, bold=bold)
    return out


# ── loop: чотириланковий замкнений контур ─────────────────────────────────────
def fig_loop():
    W, H = 980, 470
    p = [COL_MARKERS]
    p.append(text(W / 2, 50, "давачі → оцінювач стану → керування → виконання → апарат → і знову давачі",
                  size=13, color=MUTED))
    y, h = 179, 72
    cells = [
        (36, 150, ["ДАВАЧІ", "вимірюють"], "#eef2ff", NEG),
        (222, 168, ["ОЦІНЮВАЧ", "СТАНУ"], "#f4f4f5", INK),
        (426, 152, ["КЕРУВАННЯ", "порівняти й виправити"], "#eafaef", FIELD),
        (614, 160, ["ВИКОНАВЧІ", "МЕХАНІЗМИ"], "#fff5e6", "#d98a00"),
        (810, 140, ["АПАРАТ", "+ фізика"], "#ececef", INK),
    ]
    cx = []
    for x, w, lines, fill, stroke in cells:
        p.append(block(x, y, w, h, lines, fill, stroke))
        cx.append((x, x + w))
    labels = ["сирі виміри", "оцінка стану", "команди", "сили / моменти"]
    for i in range(4):
        x1, x2 = cx[i][1], cx[i + 1][0]
        p.append(arrow(x1, y + h / 2, x2 - 3, y + h / 2, color=INK, sw=2.0))
        p.append(text((x1 + x2) / 2, y - 12, labels[i], size=11, color=MUTED))
    # уставка входить збоку, у блок керування
    kx = (cells[2][0] + cells[2][1] / 2)
    p.append(block(kx - 92, 64, 184, 50, ["ЗАВДАННЯ — бажаний стан", "(уставка)"],
                   "#eef6ff", NEG, color=NEG, size=11.5))
    p.append(carrow(kx, 114, kx, y - 2, NEG, "B", sw=2.0))
    p.append(text(kx + 54, 150, "уставка", size=10.5, color=NEG, anchor="start", italic=True))
    # замикання знизу
    ax = (cells[4][0] + cells[4][1] / 2)
    bx = (cells[0][0] + cells[0][1] / 2)
    p.append(line(ax, y + h, ax, 372, color=INK, sw=2.2))
    p.append(line(ax, 372, bx, 372, color=INK, sw=2.2))
    p.append(arrow(bx, 372, bx, y + h + 2, color=INK, sw=2.2))
    p.append(text(W / 2 + 5, 365, "апарат рухається → давачі міряють новий стан: контур замикається",
                  size=11.5, color=INK))
    p.append(text(W / 2, 450,
                  "Ключова ідея: керування спирається на оцінку стану, а не на сирі давачі, і безперервно порівнює її з уставкою.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "loop.svg"), W, H, *p,
           title="Автономний апарат — це замкнений контур, а не пряма лінія")


# ── open-vs-closed: розімкнений проти замкненого ──────────────────────────────
def fig_open_vs_closed():
    W, H = 880, 380
    p = [COL_MARKERS]
    p.append(text(W / 2, 50,
                  "однакове збурення; ліворуч — команда наосліп, праворуч — вимір, порівняння, корекція",
                  size=13, color=MUTED))

    def panel(x0, title_txt, poly, color, note):
        out = [rect(x0, 86, 360, 220, fill=BG, stroke=INK, sw=1.4, rx=10)]
        out.append(text(x0 + 180, 80, title_txt, size=12.5, color=INK, bold=True))
        out.append(arrow(x0 + 20, 296, x0 + 344, 296, color=MUTED, sw=1.2))
        out.append(text(x0 + 344, 290, "час", size=10, color=MUTED, anchor="end"))
        out.append(line(x0 + 20, 190, x0 + 348, 190, color=NEG, sw=1.3, dash="5 4"))
        out.append(text(x0 + 24, 184, "уставка 0°", size=10, color=NEG, anchor="start"))
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
                   'stroke-linejoin="round"/>' % (poly, color))
        out.append(text(x0 + 180, 116, note, size=11, color=color, bold=True))
        return out

    p += panel(60, "РОЗІМКНЕНО — без зворотного зв'язку",
               "84,190 140,186 185,178 228,166 270,148 312,122 350,106 398,98",
               POS, "кут утікає → апарат падає")
    p += panel(470, "ЗАМКНЕНО — зі зворотним зв'язком",
               "492,190 520,150 546,138 576,158 614,178 656,188 706,191 824,190",
               FIELD, "кут повертається до уставки")
    p.append(text(W / 2, 366,
                  "Той самий поштовх: без зворотного зв'язку похибка накопичується, із ним — гаситься. Уся автономність тримається на цій лінії.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "open-vs-closed.svg"), W, H, *p,
           title="Чому потрібен зворотний зв'язок: розімкнено проти замкнено")


# ── mapping: абстрактні блоки → реальні компоненти ────────────────────────────
def fig_mapping():
    W, H = 900, 470
    p = [COL_MARKERS]
    p.append(text(W / 2, 50, "кожна ланка контуру = конкретні компоненти апарата",
                  size=13, color=MUTED))
    rows = [
        (["ДАВАЧІ"], "#eef2ff", NEG,
         ["IMU (гіроскоп + акселерометр) · магнітометр · барометр",
          "GNSS-приймач · давач струму та напруги"]),
        (["ОЦІНЮВАЧ", "СТАНУ"], "#f4f4f5", INK,
         ["орієнтація: крен · тангаж · курс",
          "висота · положення · швидкість"]),
        (["КЕРУВАННЯ"], "#eafaef", FIELD,
         ["ПІД-контури й каскади:",
          "кутова швидкість → кут → положення → траєкторія"]),
        (["ВИКОНАВЧІ", "МЕХАНІЗМИ"], "#fff5e6", "#d98a00",
         ["ESC → безколекторні мотори (тяга)",
          "серворушії → керма / елерони"]),
    ]
    y = 72
    for left, fill, stroke, right in rows:
        p.append(block(44, y, 196, 72, left, fill, stroke, size=13))
        p.append(arrow(240, y + 36, 285, y + 36, color=INK, sw=2.0))
        p.append(rect(288, y, 576, 72, fill=BG, stroke=MUTED, sw=1.2, rx=9))
        p.append(text(304, y + 28, right[0], size=12.5, color=INK, anchor="start"))
        p.append(text(304, y + 48, right[1], size=12.5, color=INK, anchor="start"))
        y += 92
    p.append(text(W / 2, 456,
                  "Той самий контур — не метафора: за кожним блоком стоять відчутні мікросхеми, мотори й рядки коду.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "mapping.svg"), W, H, *p,
           title="Та сама абстракція — у реальному залізі й коді")


# ── nested: вкладені контури з різними темпами ────────────────────────────────
def fig_nested():
    W, H = 860, 510
    p = [COL_MARKERS]
    p.append(text(W / 2, 50,
                  "зовнішній контур веде апарат туди, куди треба; внутрішній не дає впасти",
                  size=13, color=MUTED))
    p.append(rect(70, 96, 720, 356, fill="#f6f7fb", stroke=MUTED, sw=1.8, rx=12))
    p.append(text(86, 116, "НАВІГАЦІЯ / МІСІЯ — куди летіти", size=12.5, color=MUTED, anchor="start", bold=True))
    p.append(rect(690, 100, 84, 22, fill=BG, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(732, 115, "~1–10 Гц", size=11, color=MUTED, bold=True))

    p.append(rect(140, 172, 580, 212, fill="#eef2ff", stroke=NEG, sw=1.8, rx=12))
    p.append(text(156, 192, "КОНТУР ПОЛОЖЕННЯ / ШВИДКОСТІ — тримати траєкторію",
                  size=12.5, color=NEG, anchor="start", bold=True))
    p.append(rect(612, 176, 84, 22, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(654, 191, "~20–50 Гц", size=11, color=NEG, bold=True))

    p.append(rect(220, 248, 420, 104, fill="#eafaef", stroke=FIELD, sw=1.8, rx=12))
    p.append(text(236, 274, "КОНТУР ОРІЄНТАЦІЇ (attitude) — не впасти",
                  size=12.5, color=FIELD, anchor="start", bold=True))
    p.append(rect(470, 258, 96, 22, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(518, 273, "~250–1000 Гц", size=11, color=FIELD, bold=True))
    p.append(text(228, 320, "вихід → команди на мотори та серво", size=11, color=FIELD, anchor="start"))

    p.append(text(96, 150, "↓ задає уставку", size=10.5, color=MUTED, anchor="start", italic=True))
    p.append(text(166, 226, "↓ задає уставку", size=10.5, color=MUTED, anchor="start", italic=True))
    p.append(text(W / 2, 494,
                  "Внутрішній контур — найшвидший і найкритичніший: не встигне — апарат перекинеться раніше, ніж зреагує навігація.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "nested.svg"), W, H, *p,
           title="Контур у контурі: різні задачі — різні темпи")


# ── estimator: чому окремий оцінювач ──────────────────────────────────────────
def fig_estimator():
    W, H = 900, 430
    p = [COL_MARKERS]
    p.append(text(W / 2, 50,
                  "сильне одного закриває слабке іншого; дещо не міряє ніхто — це оцінюють",
                  size=13, color=MUTED))
    sensors = [
        (81, NEG, "Гіроскоп — кутова швидкість", "✗ кут із нього дрейфує"),
        (156, POS, "Акселерометр — нахил (вниз)", "✗ трясеться від вібрації"),
        (231, FIELD, "Магнітометр — курс (північ)", "✗ плутає залізо й струми"),
        (306, "#d98a00", "GNSS — положення, швидкість", "✗ повільний, не всюди"),
    ]
    for y, col, t1, t2 in sensors:
        p.append(rect(40, y, 310, 58, fill=BG, stroke=col, sw=1.5, rx=9))
        p.append(text(56, y + 23, t1, size=12, color=col, anchor="start", bold=True))
        p.append(text(56, y + 42, t2, size=11, color=MUTED, anchor="start"))
        p.append(line(350, y + 29, 396, 240, color=MUTED, sw=1.6))
    p.append(rect(400, 120, 150, 240, fill="#f4f4f5", stroke=INK, sw=1.7, rx=11))
    p.append(mtext(475, 228, ["ОЦІНЮВАЧ", "СТАНУ", "(поєднання)"], size=13, color=INK, bold=True))
    p.append(arrow(550, 240, 596, 240, color=INK, sw=2.2))
    p.append(rect(600, 150, 280, 180, fill="#eafaef", stroke=FIELD, sw=1.7, rx=11))
    p.append(text(618, 178, "СТАН (чистий, надійний):", size=12.5, color=FIELD, anchor="start", bold=True))
    p.append(text(618, 202, "крен · тангаж · курс", size=11.5, color=INK, anchor="start"))
    p.append(text(618, 221, "висота · положення · швидкість", size=11.5, color=INK, anchor="start"))
    p.append(text(618, 256, "+ те, чого не міряє жоден давач", size=11.5, color=INK, anchor="start"))
    p.append(text(618, 275, "(напр. швидкість вітру) — оцінюється", size=11.5, color=INK, anchor="start"))
    p.append(text(W / 2, 418,
                  "Оцінювач — це не «згладжування»: він поєднує давачі й виводить навіть те, що напряму не вимірюється.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "estimator.svg"), W, H, *p,
           title="Навіщо окремий оцінювач: жоден давач сам не дає «стану»")


# ── setpoint: джерело уставки (пілот / місія) ─────────────────────────────────
def fig_setpoint():
    W, H = 900, 430
    p = [COL_MARKERS]
    p.append(text(W / 2, 50, "ручний і автономний режими різняться лише джерелом уставки",
                  size=13, color=MUTED))
    p.append(rect(46, 78, 250, 78, fill="#eef6ff", stroke=NEG, sw=1.7, rx=11))
    p.append(text(60, 102, "ПІЛОТ — RC-стіки", size=13, color=NEG, anchor="start", bold=True))
    p.append(text(60, 124, "ручна уставка просто зараз:", size=11.5, color=INK, anchor="start"))
    p.append(text(60, 139, "«нахили праворуч на 15°»", size=11.5, color=INK, anchor="start"))
    p.append(rect(46, 250, 250, 78, fill="#eafaef", stroke=FIELD, sw=1.7, rx=11))
    p.append(text(60, 274, "АВТОНОМНА МІСІЯ", size=13, color=FIELD, anchor="start", bold=True))
    p.append(text(60, 296, "точки маршруту → навігація", size=11.5, color=INK, anchor="start"))
    p.append(text(60, 311, "рахує уставку: «лети до точки B»", size=11.5, color=INK, anchor="start"))
    p.append(rect(346, 165, 128, 76, fill="#f4f4f5", stroke=INK, sw=1.6, rx=10))
    p.append(mtext(410, 200, ["ВИБІР", "РЕЖИМУ"], size=12.5, color=INK, bold=True))
    p.append(carrow(296, 117, 344, 188, NEG, "B", sw=2.0))
    p.append(carrow(296, 289, 344, 218, FIELD, "G", sw=2.0))
    p.append(rect(512, 165, 188, 76, fill="#eafaef", stroke=FIELD, sw=1.7, rx=11))
    p.append(mtext(606, 200, ["КЕРУВАННЯ", "(те саме ядро)"], size=12.5, color=INK, bold=True))
    p.append(arrow(474, 203, 510, 203, color=INK, sw=2.0))
    p.append(rect(728, 165, 140, 76, fill="#fff5e6", stroke="#d98a00", sw=1.7, rx=11))
    p.append(mtext(798, 200, ["ВИКОНАВЧІ", "МЕХАНІЗМИ"], size=12.5, color=INK, bold=True))
    p.append(arrow(700, 203, 726, 203, color=INK, sw=2.0))
    p.append(text(W / 2, 414,
                  "Те, що нижче «вибору режиму» (керування → виконання → апарат → давачі), однакове для ручного й автономного польоту.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "setpoint.svg"), W, H, *p,
           title="Звідки береться «бажаний стан»: пілот чи місія — ядро те саме")


# ════════════════ Фігури вставки hist-ardupilot ══════════════════════════════

# ── thermopile: ІЧ-термопари «бачать» горизонт ────────────────────────────────
def fig_thermopile():
    W, H = 940, 500
    p = [COL_MARKERS]
    p.append(text(W / 2, 50,
                  "земля тепла (ІЧ-яскрава), небо холодне (ІЧ-темне) — різниця дає крен і тангаж",
                  size=13, color=MUTED))
    # небо / земля
    p.append(rect(40, 70, 540, 200, fill="#dbeafe", stroke="none", sw=0, rx=0))
    p.append(rect(40, 270, 540, 160, fill="#dcfce7", stroke="none", sw=0, rx=0))
    p.append(line(40, 270, 580, 270, color=FIELD, sw=2.0))
    p.append(rect(40, 70, 540, 360, fill="none", stroke=INK, sw=1.4, rx=10))
    p.append(text(54, 96, "холодне небо  ≈ −40 °C", size=12.5, color=NEG, anchor="start", bold=True))
    p.append(text(54, 416, "тепла земля  ≈ +15 °C", size=12.5, color=POS, anchor="start", bold=True))
    # нахилений апарат із парою давачів
    cxp, cyp = 310.0, 242
    g = ['<g transform="rotate(22 %.1f %d)">' % (cxp, cyp)]
    g.append('<polygon points="224.0,242 396.0,242 388.0,251 232.0,251" fill="#ffffff" stroke="%s" stroke-width="1.6" stroke-linejoin="round"/>' % INK)
    g.append(circle(cxp, 240, 13, fill="#f4f4f5", stroke=INK, sw=1.6))
    g.append(circle(224.0, 246, 5, fill=POS, stroke=INK, sw=1.2))
    g.append(circle(396.0, 246, 5, fill=NEG, stroke=INK, sw=1.2))
    g.append("</g>")
    p.append("".join(g))
    p.append(carrow(230, 214, 202, 284, POS, "R", sw=2.0))
    p.append(carrow(390, 278, 418, 208, NEG, "B", sw=2.0))
    p.append(text(160, 306, "ІЧ-давач L", size=11.5, color=POS, anchor="start", bold=True))
    p.append(text(152, 320, "→ тепла земля", size=11, color=POS, anchor="start"))
    p.append(text(386, 202, "ІЧ-давач R", size=11.5, color=NEG, anchor="start", bold=True))
    p.append(text(378, 216, "→ холодне небо", size=11, color=NEG, anchor="start"))
    p.append(text(312, 198, "крен", size=11.5, color=INK, italic=True))
    # права колонка — що «чує» автопілот
    p.append(text(610, 78, "Що «чує» автопілот", size=13.5, color=INK, anchor="start", bold=True))
    p.append(rect(610, 92, 290, 86, fill=BG, stroke=INK, sw=1.3, rx=9))
    p.append(text(624, 114, "Рівний політ", size=12.5, color=INK, anchor="start", bold=True))
    p.append(circle(650, 144, 7, fill=POS, stroke=INK, sw=1.2))
    p.append(circle(860, 144, 7, fill=POS, stroke=INK, sw=1.2))
    p.append(text(650, 166, "T_L", size=11, color=MUTED))
    p.append(text(860, 166, "T_R", size=11, color=MUTED))
    p.append(text(755, 140, "T_L ≈ T_R", size=13, color=FIELD, bold=True))
    p.append(text(755, 158, "→ крен 0", size=11.5, color=FIELD))
    p.append(rect(610, 192, 290, 86, fill=BG, stroke=INK, sw=1.3, rx=9))
    p.append(text(624, 214, "Крен праворуч", size=12.5, color=INK, anchor="start", bold=True))
    p.append(circle(650, 244, 9, fill=POS, stroke=INK, sw=1.2))
    p.append(circle(860, 246, 5, fill=NEG, stroke=INK, sw=1.2))
    p.append(text(755, 240, "T_L > T_R", size=13, color="#d98a00", bold=True))
    p.append(text(755, 258, "→ виправити кермом", size=11.5, color="#d98a00"))
    p.append(rect(610, 292, 290, 56, fill="#f4f4f5", stroke=INK, sw=1.3, rx=9))
    p.append(text(755, 314, "крен ∝ T_L − T_R", size=13, color=INK, bold=True))
    p.append(text(755, 334, "тангаж ∝ T_перед − T_зад", size=12, color=INK))
    p.append(text(610, 372, "Чому відмовилися:", size=12, color="#d98a00", anchor="start", bold=True))
    p.append(text(610, 390, "хмари, захід сонця, гарячий дах і ліс", size=11.5, color=MUTED, anchor="start"))
    p.append(text(610, 406, "плутають «горизонт»; MEMS-IMU витіснили термопари.",
                  size=11.5, color=MUTED, anchor="start"))
    render(os.path.join(OUT, "thermopile.svg"), W, H, *p,
           title="Як перші автопілоти «бачили» горизонт без IMU: інфрачервоні термопари")


# ── timeline: дві лінії, спільне залізо, розкол ───────────────────────────────
def fig_timeline():
    W, H = 900, 668
    p = [COL_MARKERS]
    p.append(text(W / 2, 50,
                  "згори вниз — час; ліворуч від осі лінія ArduPilot, праворуч — лінія PX4/ETH",
                  size=13, color=MUTED))
    p.append(text(293, 78, "ArduPilot  (хобі → Arduino)", size=13, color=POS, bold=True))
    p.append(text(620, 78, "PX4 / Pixhawk  (ETH Zürich)", size=13, color=NEG, bold=True))
    p.append(line(450, 92, 450, 596, color=INK, sw=3.0))
    p.append(arrow(450, 596, 450, 600, color=INK, sw=3.0))
    p.append(text(450, 622, "час", size=12, color=MUTED, italic=True))

    def lcard(y, year, l1, l2):
        out = [rect(150, y, 286, 46, fill="#fff3f3", stroke=POS, sw=1.4, rx=8)]
        out.append(line(436, y + 23, 445, y + 23, color=POS, sw=1.4))
        out.append(circle(450, y + 23, 5, fill=POS, stroke=INK, sw=1.2))
        out.append(text(462, y + 27, year, size=11, color=MUTED, anchor="start", bold=True))
        out.append(text(164, y + 19, l1, size=11.5, color=INK, anchor="start"))
        out.append(text(164, y + 34, l2, size=11.5, color=INK, anchor="start"))
        return out

    def rcard(y, year, l1, l2):
        out = [rect(470, y, 300, 46, fill="#eff4ff", stroke=NEG, sw=1.4, rx=8)]
        out.append(line(455, y + 23, 470, y + 23, color=NEG, sw=1.4))
        out.append(circle(450, y + 23, 5, fill=NEG, stroke=INK, sw=1.2))
        out.append(text(438, y + 27, year, size=11, color=MUTED, anchor="end", bold=True))
        out.append(text(484, y + 19, l1, size=11.5, color=INK, anchor="start"))
        out.append(text(484, y + 34, l2, size=11.5, color=INK, anchor="start"))
        return out

    p += lcard(97, "2007", "DIY Drones — Кріс Андерсон:", "автопілот спершу на Lego Mindstorms")
    p += lcard(153, "2009", "ArduPilot на Arduino — Жорді Муньйос;", "засновано 3D Robotics (3DR)")
    p += rcard(209, "2009", "MAVLink — протокол телеметрії", "(Лоренц Маєр, ETH)")
    p += lcard(265, "2010–11", "ArduPilotMega (APM): 8-біт ATmega2560 + IMU;", "ArduCopter — підтримка мультироторів")
    # спільне залізо
    p.append(line(150, 348, 770, 348, color=FIELD, sw=1.4, dash="4 4"))
    p.append(rect(222, 318, 456, 60, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=11))
    p.append(text(240, 339, "2012–13 · Спільне 32-бітне залізо", size=12.5, color=FIELD, anchor="start", bold=True))
    p.append(text(240, 357, "8-біт уперся в стелю; PX4 і AP_HAL — 2012,", size=11.5, color=INK, anchor="start"))
    p.append(text(240, 372, "плата Pixhawk (STM32) — 2013; стеки → ARM + RTOS", size=11.5, color=INK, anchor="start"))
    p += rcard(391, "2014", "Dronecode — фундація під Linux Foundation", "(хостить PX4, MAVLink, QGroundControl)")
    # розкол
    p.append(line(150, 476, 770, 476, color="#d98a00", sw=1.4, dash="4 4"))
    p.append(rect(222, 446, 456, 60, fill="#fff5e6", stroke="#d98a00", sw=1.8, rx=11))
    p.append(text(240, 467, "2016 · Розкол через ліцензії", size=12.5, color="#d98a00", anchor="start", bold=True))
    p.append(text(240, 485, "ArduPilot виходить із Dronecode → незалежний (GPLv3);", size=11.5, color=INK, anchor="start"))
    p.append(text(240, 500, "PX4 лишається в Dronecode (ліцензія BSD)", size=11.5, color=INK, anchor="start"))
    p += lcard(525, "тепер", "ArduPilot.org: RTOS ChibiOS, STM32H7;", "Copter · Plane · Rover · Sub · Tracker")
    p += rcard(525, "тепер", "PX4 у Dronecode; спільний інструмент —", "наземна станція QGroundControl")
    p.append(text(W / 2, 652,
                  "Хобі-лінія (Arduino) і академічна лінія (ETH) зійшлися на залізі Pixhawk, а потім розійшлися через ліцензії — звідси два великі відкриті автопілоти.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Як народився ArduPilot: дві лінії, спільне залізо, розкол ліцензій")


# ── naming: три шари (залізо / прошивка / GCS) ────────────────────────────────
def fig_naming():
    W, H = 920, 520
    p = [COL_MARKERS]
    p.append(text(W / 2, 50,
                  "їх обирають майже незалежно; плутанина тягнеться ще з епохи «APM»",
                  size=13, color=MUTED))
    layers = [
        (80, "#fff5e6", "#d98a00", "НАЗЕМНА СТАНЦІЯ (GCS)",
         "на ноутбуці/планшеті: карта, параметри, місія, логи",
         "приклади:  Mission Planner · QGroundControl"),
        (206, "#eafaef", FIELD, "ПРОШИВКА — польотний стек",
         "заливається у плату; читає давачі й керує моторами",
         "приклади:  ArduPilot (GPLv3) · PX4 (BSD)"),
        (332, "#eef2ff", NEG, "ЗАЛІЗО — політний контролер (FMU)",
         "STM32 + IMU + барометр + роз'єми; «мозок» у залізі",
         "приклади:  Pixhawk · Cube · Matek · Holybro"),
    ]
    for y, fill, col, head, l1, l2 in layers:
        p.append(rect(70, y, 520, 96, fill=fill, stroke=col, sw=1.8, rx=12))
        p.append(text(88, y + 28, head, size=14, color=col, anchor="start", bold=True))
        p.append(text(88, y + 50, l1, size=12, color=INK, anchor="start"))
        p.append(text(88, y + 74, l2, size=12.5, color=INK, anchor="start", bold=True))
    # MAVLink між прошивкою й GCS
    p.append(arrow(620, 254, 620, 128, color=INK, sw=2.0))
    p.append(arrow(620, 136, 620, 246, color=INK, sw=2.0))
    p.append(rect(628, 163, 222, 56, fill="#f4f4f5", stroke=INK, sw=1.3, rx=9))
    p.append(text(640, 185, "MAVLink — протокол,", size=12, color=INK, anchor="start"))
    p.append(text(640, 201, "по радіо/USB", size=12, color=INK, anchor="start"))
    # прошити
    p.append(carrow(330, 302, 330, 332, FIELD, "G", sw=2.2))
    p.append(text(342, 321, "прошити (USB/UART)", size=11.5, color=FIELD, anchor="start", italic=True))
    p.append(text(W / 2, 498,
                  "Один FMU може нести або ArduPilot, або PX4; стара назва «APM» означала і плату, і прошивку — звідси вічна плутанина в чужих доках.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "naming.svg"), W, H, *p,
           title="Чому стільки назв: залізо, прошивка й наземна станція — три різні шари")


# ════════════════ Фігури детальної статті autonomous-system-d ═════════════════

# ── fusion-spectrum: доповняльний фільтр як поділ спектра ──────────────────────
def fig_fusion_spectrum():
    W, H = 900, 470
    p = [COL_MARKERS]
    p.append(text(W / 2, 50,
                  "низькі частоти тримає акселерометр (абсолют), високі — гіроскоп (динаміка)",
                  size=13, color=MUTED))
    # осі частотної смуги
    x0, x1 = 90.0, 810.0
    axy = 300.0
    p.append(arrow(x0, axy, x1 + 6, axy, color=MUTED, sw=1.4))
    p.append(text(x1 + 4, axy + 22, "частота", size=11.5, color=MUTED, anchor="end", italic=True))
    # частота поділу
    xc = 430.0
    p.append(line(xc, 96, xc, axy + 8, color=INK, sw=1.6, dash="6 4"))
    p.append(text(xc, 90, "частота поділу  f_поділу ≈ (1−α)/(2π·α·Δt)", size=12, color=INK, bold=True))
    # смуга акселерометра (низькі)
    p.append(rect(x0, 150, xc - x0, 60, fill="#fdecea", stroke=POS, sw=1.6, rx=9))
    p.append(text((x0 + xc) / 2, 176, "АКСЕЛЕРОМЕТР — низькі частоти", size=12.5, color=POS, bold=True))
    p.append(text((x0 + xc) / 2, 196, "абсолютний горизонт, не спливає", size=11, color=POS))
    # смуга гіроскопа (високі)
    p.append(rect(xc, 150, x1 - xc, 60, fill="#eef2ff", stroke=NEG, sw=1.6, rx=9))
    p.append(text((xc + x1) / 2, 176, "ГІРОСКОП — високі частоти", size=12.5, color=NEG, bold=True))
    p.append(text((xc + x1) / 2, 196, "чиста швидка динаміка маневру", size=11, color=NEG))
    # де кожен БРЕШЕ (під віссю)
    p.append(text((x0 + xc) / 2, axy + 40, "тут акселерометр брудний:", size=11, color=MUTED))
    p.append(text((x0 + xc) / 2, axy + 56, "вібрація, прискорення маневру", size=11, color=MUTED))
    p.append(text((xc + x1) / 2, axy + 40, "тут гіроскоп бреше:", size=11, color=MUTED))
    p.append(text((xc + x1) / 2, axy + 56, "дрейф інтеграла зміщення", size=11, color=MUTED))
    # формула зшивання
    p.append(rect(150, 366, 600, 58, fill="#eafaef", stroke=FIELD, sw=1.7, rx=11))
    p.append(text(W / 2, 390, "θ = α·(θ_попер + ω·Δt)  +  (1−α)·θ_акс", size=14, color=INK, bold=True))
    p.append(text(W / 2, 411, "гіро несе високі · акселерометр підрізає дрейф на низьких — сума без діри й задвоєння",
                  size=11, color=FIELD))
    p.append(text(W / 2, 452,
                  "α — не магічне число, а фізична межа довіри: зсунеш f_поділу — переділиш роботу між давачами.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "fusion-spectrum.svg"), W, H, *p,
           title="Оцінювач як частотний поділ праці між давачами")


# ── latency-budget: три внески в затримку → втрата запасу фази ─────────────────
def fig_latency_budget():
    W, H = 920, 470
    p = [COL_MARKERS]
    p.append(text(W / 2, 50,
                  "затримка від вибірки давача до дії команди з'їдає запас стійкості",
                  size=13, color=MUTED))
    # часова вісь одного такту
    x0, x1 = 80.0, 840.0
    ty = 150.0
    p.append(line(x0, ty, x1, ty, color=INK, sw=2.0))
    p.append(text(x0, ty - 14, "вибірка давача (t)", size=11.5, color=INK, anchor="start", bold=True))
    p.append(text(x1, ty - 14, "команда діє (t + τ_з)", size=11.5, color=INK, anchor="end", bold=True))
    p.append(line(x0, ty - 8, x0, ty + 8, color=INK, sw=2.0))
    p.append(line(x1, ty - 8, x1, ty + 8, color=INK, sw=2.0))
    # три сегменти затримки
    segs = [
        (x0, 300.0, "#eef2ff", NEG, "ОБЧИСЛЕННЯ", "читання шини + оцінювач + ПІД"),
        (300.0, 520.0, "#fdecea", POS, "ПІВ ТАКТУ  Δt/2", "команда тримається весь такт (ZOH)"),
        (520.0, x1, "#fff5e6", "#d98a00", "МЕХАНІКА", "інерція мотора / серво"),
    ]
    by = 176.0
    for xa, xb, fill, col, head, sub in segs:
        p.append(rect(xa + 3, by, xb - xa - 6, 66, fill=fill, stroke=col, sw=1.7, rx=10))
        p.append(text((xa + xb) / 2, by + 28, head, size=12.5, color=col, bold=True))
        p.append(text((xa + xb) / 2, by + 48, sub, size=10.5, color=INK))
    # дужка сумарної затримки
    p.append(line(x0, 262, x1, 262, color=MUTED, sw=1.3))
    p.append(text(W / 2, 282, "повна затримка  τ_з = τ_обч + Δt/2 + τ_мех", size=13, color=INK, bold=True))
    # наслідок: фазовий зсув
    p.append(rect(150, 306, 620, 92, fill="#f4f4f5", stroke=INK, sw=1.6, rx=11))
    p.append(text(W / 2, 332, "фазовий зсув від затримки:   Δφ = 2π · f · τ_з", size=14, color=INK, bold=True))
    p.append(text(W / 2, 356, "віднімається від запасу фази; коли Δφ дійде 180° — «гальмо» стає «газом»", size=11.5, color=POS))
    p.append(text(W / 2, 378, "гранична затримка:   τ_з ≈ запас_фази / (2π · f_зрізу)", size=12.5, color=FIELD, bold=True))
    p.append(text(W / 2, 452,
                  "Підняти частоту петлі — зменшити середній сегмент (Δt/2); будь-який сплеск обчислень роздуває лівий і краде стійкість.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "latency-budget.svg"), W, H, *p,
           title="Час як фізична сила: з чого складається затримка петлі")


# ── failsafe: сходи деградації як машина станів ───────────────────────────────
def fig_failsafe_ladder():
    W, H = 980, 560
    p = [COL_MARKERS]
    p.append(text(W / 2, 52,
                  "що глибше б'є відмова (ближче до внутрішнього контуру) — то радикальніша реакція",
                  size=13, color=MUTED, italic=True))

    # чотири режими стовпчиком: від найамбітнішого (AUTO) до найбезпечнішого (LAND)
    modes = [
        (96,  "AUTO",   "лети маршрутом",    "#eafaef", FIELD,     "усі давачі здорові"),
        (206, "LOITER", "висни на місці",    "#eef6ff", NEG,       "втрачено GNSS — сліпа навігація"),
        (316, "RTL",    "вертайся додому",   "#fff5e6", "#d98a00", "низька батарея / нема зв'язку"),
        (426, "LAND",   "сідай тут і зараз", "#fdecea", POS,       "критична батарея / RTL недосяжний"),
    ]
    bx, bw, bh = 96, 300, 74
    centers = []
    for y, name, sub, fill, col, why in modes:
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=col, sw=1.9, rx=12))
        p.append(text(bx + 120, y + 30, name, size=19, color=col, bold=True))
        p.append(text(bx + 120, y + 52, sub, size=12, color=INK))
        # причина переходу — праворуч від блока
        p.append(text(bx + bw + 20, y + bh / 2 - 6, "▲ причина:", size=10.5, color=MUTED, anchor="start"))
        p.append(text(bx + bw + 20, y + bh / 2 + 12, why, size=10.5, color=col, anchor="start"))
        centers.append((y, y + bh))

    # стрілки деградації вниз (тільки в бік безпеки)
    for i in range(3):
        yA = centers[i][1]
        yB = centers[i + 1][0]
        p.append(carrow(bx + 120, yA, bx + 120, yB - 3, POS, "R", sw=2.4))
    midy = (centers[0][1] + centers[3][0]) / 2
    p.append(text(bx - 16, midy, "деградація", size=12, color=POS, anchor="end", bold=True))
    p.append(text(bx - 16, midy + 18, "(вниз — до", size=10, color=MUTED, anchor="end"))
    p.append(text(bx - 16, midy + 32, "безпеки)", size=10, color=MUTED, anchor="end"))

    # аварійний зрив збоку: втрата орієнтації б'є з БУДЬ-ЯКОГО режиму одразу
    ex, ew = 690, 200
    ey, eh = 236, 108
    p.append(rect(ex, ey, ew, eh, fill="#fbe9e7", stroke=POS, sw=2.4, rx=12))
    p.append(text(ex + ew / 2, ey + 30, "АВАРІЯ", size=17, color=POS, bold=True))
    p.append(text(ex + ew / 2, ey + 54, "втрата орієнтації", size=12, color=INK))
    p.append(text(ex + ew / 2, ey + 76, "внутрішній контур", size=10.5, color=MUTED))
    p.append(text(ex + ew / 2, ey + 92, "осліп — гаси мотори", size=10.5, color=MUTED))
    # блискавки з кожного режиму в АВАРІЮ
    for y, *_ in modes:
        p.append(line(bx + bw + 150, y + bh / 2, ex - 4, ey + eh / 2, color=POS, sw=1.0, dash="4,4"))
    p.append(text(ex + ew / 2, ey - 16, "б'є з БУДЬ-ЯКОГО режиму", size=11, color=POS, bold=True))

    p.append(text(W / 2, 528,
                  "Ключове: переходи ведуть ЛИШЕ до безпечнішого. Втрата зовнішньої ланки коштує режим; втрата внутрішньої — політ.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "failsafe-ladder.svg"), W, H, *p,
           title="Сходи деградації failsafe як машина станів")


# ── failsafe: гістерезис на порозі (два рівні + затримка) ─────────────────────
def fig_hysteresis():
    W, H = 980, 470
    p = [COL_MARKERS]
    p.append(text(W / 2, 52, "один поріг тремтить на межі; два рівні + витримка часу — ні",
                  size=13, color=MUTED, italic=True))

    x0, x1 = 90, 890
    ymid = 250
    # осі
    p.append(arrow(x0, 400, x1, 400, color=INK, sw=1.6))       # час
    p.append(text(x1, 420, "час", size=12, color=INK, anchor="end"))
    p.append(arrow(x0, 400, x0, 90, color=INK, sw=1.6))        # напруга
    p.append(text(x0 - 8, 96, "напруга", size=12, color=INK, anchor="end"))

    # два пороги
    yLow = 190   # спрацювати (нижчий за напругою → вище на екрані? ні: менша напруга = нижче)
    yClr = 150
    # зробимо: більша напруга — вище. поріг спрацювання нижче, поріг відпуску вище.
    p.append(line(x0, yClr, x1, yClr, color=FIELD, sw=1.6, dash="7,5"))
    p.append(text(x1 + 4, yClr + 4, "поріг ВІДПУСКУ", size=10.5, color=FIELD, anchor="start"))
    p.append(text(x1 + 4, yClr + 18, "(вищий)", size=9.5, color=MUTED, anchor="start"))
    p.append(line(x0, yLow, x1, yLow, color=POS, sw=1.6, dash="7,5"))
    p.append(text(x1 + 4, yLow + 4, "поріг СПРАЦЮВАННЯ", size=10.5, color=POS, anchor="start"))
    p.append(text(x1 + 4, yLow + 18, "(нижчий)", size=9.5, color=MUTED, anchor="start"))
    # смуга гістерезису
    p.append(rect(x0, yClr, x1 - x0, yLow - yClr, fill="#fff7e6", stroke="none", sw=0))
    p.append(text((x0 + x1) / 2, (yClr + yLow) / 2 + 4, "мертва смуга (гістерезис)", size=10.5, color="#b8860b"))

    # шумний сигнал напруги, що просідає й тремтить рівно на порозі
    import math
    pts = []
    N = 160
    for i in range(N + 1):
        t = i / N
        vx = x0 + t * (x1 - x0)
        base = 230 - 70 * t                       # плавне просідання
        noise = 14 * math.sin(t * 34) * (0.4 + 0.6 * t)
        vy = base + noise
        pts.append((vx, vy))
    path = "M " + " L ".join("%.1f %.1f" % (a, b) for a, b in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (path, NEG))
    p.append(text(x0 + 150, 110, "напруга батареї (шумить)", size=11, color=NEG))

    # точка перетину порогу спрацювання + витримка часу
    # знайдемо перший стійкий перетин нижче yLow
    trig_x = None
    for a, b in pts:
        if b > yLow and a > x0 + 300:   # b>yLow бо менша напруга = більший y
            trig_x = a
            break
    if trig_x is None:
        trig_x = x0 + 520
    p.append(line(trig_x, yLow, trig_x + 90, yLow, color=POS, sw=3.0))
    p.append('<rect x="%.1f" y="%.1f" width="90" height="%.1f" fill="#fdecea" stroke="%s" stroke-width="1.4" rx="4"/>'
             % (trig_x, yLow + 6, 26, POS))
    p.append(text(trig_x + 45, yLow + 24, "витримка 10 с", size=10, color=POS))
    p.append(carrow(trig_x + 45, yLow + 40, trig_x + 45, 392, POS, "R", sw=1.8))
    p.append(text(trig_x + 45, 418, "СПРАЦЮВАЛО (стійко)", size=10.5, color=POS, bold=True))

    p.append(text(W / 2, 452,
                  "Одного порогу мало: сигнал перетне його туди-сюди десятки разів. Потрібні ДВА рівні й витримка часу — щоб рішення було одне.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "hysteresis.svg"), W, H, *p,
           title="Гістерезис на порозі: два рівні проти тремтіння")


# ════════════════ Фігура вставки math-loop-stability ═════════════════════════

# ── cascade-roots: корені зовнішнього контуру повзуть до одиничного кола ────────
def fig_cascade_roots():
    import cmath
    W, H = 900, 560
    p = [COL_MARKERS]
    p.append(text(W / 2, 52,
                  "менше λ (лінивіший внутрішній контур) → пара коренів ближче до кола |z|=1 → ближче до розносу",
                  size=13, color=MUTED))
    ox, oy = 300.0, 320.0          # початок координат (z=0)
    R = 210.0                       # радіус одиничного кола в пікселях (|z|=1)
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#eafaef" stroke="none"/>' % (ox, oy, R))
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="2.0"/>'
             % (ox, oy, R, FIELD))
    p.append(arrow(ox - R - 34, oy, ox + R + 34, oy, color=INK, sw=1.5))
    p.append(arrow(ox, oy + R + 34, ox, oy - R - 34, color=INK, sw=1.5))
    p.append(text(ox + R + 40, oy + 16, "Re z", size=12, color=INK, anchor="start", bold=True))
    p.append(text(ox + 12, oy - R - 30, "Im z", size=12, color=INK, anchor="start", bold=True))
    p.append(line(ox + R, oy - 5, ox + R, oy + 5, color=INK, sw=1.5))
    p.append(text(ox + R, oy + 22, "+1", size=11, color=INK))
    p.append(line(ox - R, oy - 5, ox - R, oy + 5, color=INK, sw=1.5))
    p.append(text(ox - R, oy + 22, "−1", size=11, color=INK))
    p.append(text(ox - 12, oy + 22, "0", size=11, color=MUTED))
    p.append(text(ox + R * 0.42, oy + R * 0.66, "стійка зона  |z| < 1",
                  size=12, color=FIELD, bold=True))

    def outer_root(lam, hKx):
        b = -(2 - lam); c = 1 - lam + lam * hKx
        s = cmath.sqrt(b * b - 4 * c)
        return (-b + s) / 2.0
    cases = [
        (0.9, 0.3, NEG, "λ=0.9  швидкий внутр."),
        (0.5, 0.3, FIELD, "λ=0.5"),
        (0.25, 0.3, "#d98a00", "λ=0.25"),
        (0.12, 0.4, POS, "λ=0.12  лінивий внутр."),
    ]

    def toxy(zc, up=True):
        im = zc.imag if up else -zc.imag
        return ox + zc.real * R, oy - im * R
    pts = [toxy(outer_root(l, h)) for l, h, _, _ in cases]
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        p.append(line(x1, y1, x2, y2, color=MUTED, sw=1.2, dash="4 4"))
    lx = ox + R + 74
    ly = oy - R + 4
    for i, (lam, hKx, col, lbl) in enumerate(cases):
        zc = outer_root(lam, hKx)
        xu, yu = toxy(zc, up=True)
        xd, yd = toxy(zc, up=False)
        p.append(circle(xu, yu, 6.5, fill=col, stroke=INK, sw=1.3))
        p.append(circle(xd, yd, 6.5, fill=col, stroke=INK, sw=1.3))
        yy = ly + i * 27
        p.append(circle(lx, yy, 6.0, fill=col, stroke=INK, sw=1.2))
        p.append(text(lx + 16, yy + 4, "%s   |z|=%.2f" % (lbl, abs(zc)),
                      size=11.5, color=INK, anchor="start"))
    yb = ly + 4 * 27 + 14
    p.append(text(lx, yb, "h·Kx фіксоване;", size=11, color=MUTED, anchor="start", italic=True))
    p.append(text(lx, yb + 17, "міняється лише швидкодія", size=11, color=MUTED, anchor="start", italic=True))
    p.append(text(lx, yb + 34, "внутрішнього контуру λ", size=11, color=MUTED, anchor="start", italic=True))
    p.append(text(W / 2, 544,
                  "Той самий зовнішній регулятор: його стійкість тане не від власних коефіцієнтів, а від повільності контуру, яким він керує.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "cascade-roots.svg"), W, H, *p,
           title="Каскад: динаміка внутрішнього контуру тягне корені зовнішнього")


if __name__ == "__main__":
    fig_loop()
    fig_open_vs_closed()
    fig_mapping()
    fig_nested()
    fig_estimator()
    fig_setpoint()
    fig_thermopile()
    fig_timeline()
    fig_naming()
    fig_fusion_spectrum()
    fig_latency_budget()
    fig_failsafe_ladder()
    fig_hysteresis()
    fig_cascade_roots()
    print("OK: figures written to", OUT)
