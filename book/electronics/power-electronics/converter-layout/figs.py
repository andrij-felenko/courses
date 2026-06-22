# -*- coding: utf-8 -*-
"""Фігури для теми converter-layout (розведення перетворювача).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#b5763a"   # колір міді/котушки


def cap(x, y, w=30, gap=8, color=INK, sw=3.4):
    """Конденсатор — дві паралельні пластини горизонтально (на вертикальній шині)."""
    return (line(x - w / 2, y - gap / 2, x + w / 2, y - gap / 2, color=color, sw=sw) +
            line(x - w / 2, y + gap / 2, x + w / 2, y + gap / 2, color=color, sw=sw))


def coil(x1, y, x2, turns=4, color=COPPER, sw=2.6):
    """Котушка — низка дуг між x1 і x2 на висоті y."""
    seg = (x2 - x1) / turns
    d = "M %.1f %.1f " % (x1, y)
    for k in range(turns):
        cx = x1 + seg * (k + 0.5)
        d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (seg / 2, seg * 0.55, x1 + seg * (k + 1), y)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


# ── 1. Гаряча петля в buck ───────────────────────────────────────────────────
def fig_hotloop():
    W, H = 760, 430
    frags = []
    # вертикальна вхідна шина (Vвх) ліворуч
    xin, ytop, ybot = 150, 90, 330
    frags.append(text(xin, 74, "Vвх", size=13, color=NEG, bold=True))
    frags.append(line(xin, ytop, xin, ybot, color=INK, sw=2))
    frags.append(cap(xin, 210, color=COPPER))
    frags.append(text(xin - 28, 214, "Cвх", size=12, color=COPPER, bold=True, anchor="end"))

    # верхній ключ Q1 і вузол SW
    xsw = 360
    frags.append(line(xin, ytop, 250, ytop, color=POS, sw=3))
    q1 = rect(250, ytop - 17, 56, 34, fill="#eaf0fd", stroke=NEG, sw=2)
    frags.append(q1 + text(278, ytop + 5, "Q1", size=13, color=NEG, bold=True))
    frags.append(line(306, ytop, xsw, ytop, color=POS, sw=3))
    frags.append(circle(xsw, ytop, 4, fill=INK, stroke=INK))
    frags.append(text(xsw, ytop - 14, "SW", size=11, color="#caa24a", bold=True))

    # нижній ключ Q2
    frags.append(line(xsw, ytop, xsw, 200, color=POS, sw=3))
    q2 = rect(xsw - 28, 200, 56, 34, fill="#eaf0fd", stroke=FIELD, sw=2)
    frags.append(q2 + text(xsw, 222, "Q2", size=13, color=FIELD, bold=True))
    frags.append(line(xsw, 234, xsw, ybot, color=POS, sw=3))
    frags.append(line(xin, ybot, xsw, ybot, color=POS, sw=3))

    # котушка → вихід (холодна частина, тонше/темно)
    frags.append(coil(374, ytop, 470, turns=4))
    frags.append(line(470, ytop, 620, ytop, color=INK, sw=2))
    frags.append(line(620, ytop, 620, ybot, color=INK, sw=2))
    frags.append(cap(620, 210, color=INK, sw=3))
    frags.append(text(648, 104, "Vвих", size=12, color=INK, bold=True, anchor="start"))
    frags.append(line(xsw, ybot, 620, ybot, color=INK, sw=2))

    # підсвітити петлю
    frags.append('<rect x="138" y="84" width="234" height="252" rx="10" '
                 'fill="%s" fill-opacity="0.07"/>' % POS)
    frags.append(text(250, 268, "ГАРЯЧА ПЕТЛЯ", size=13, color=POS, bold=True))
    frags.append(text(250, 286, "Cвх → Q1 → Q2 → Cвх", size=11, color=POS, bold=True))
    frags.append(text(250, 304, "тут струм РІЖЕТЬСЯ (велике di/dt)", size=10, color=INK))

    # формула збоку
    bx, bbw, bbh = textbox(685, 175, ["V = L·di/dt", "L — паразитна", "котушка петлі",
                                      "→ викид, дзвін"], size=12, fill="#fbe9e7", stroke=POS)
    frags.append(bx)

    render(os.path.join(OUT, "hot-loop.svg"), W, H, *frags,
           title="Гаряча петля в buck: коло різаного струму")


# ── 2. Мала проти великої петлі ──────────────────────────────────────────────
def fig_loop_size():
    W, H = 760, 360
    frags = []

    def stage(x0, label, gap, hot):
        # вертикальна шина + конденсатор на відстані gap від ключів
        ytop, ybot = 90, 250
        xc = x0 + 20
        xq = x0 + 20 + gap
        col = POS if hot else FIELD
        frags.append(line(xc, ytop, xc, ybot, color=INK, sw=2))
        frags.append(cap(xc, 170, color=COPPER))
        frags.append(text(xc, ytop - 12, "Cвх", size=11, color=COPPER, bold=True))
        # ключі (стовпчик) праворуч
        frags.append(line(xc, ytop, xq, ytop, color=col, sw=3))
        frags.append(rect(xq, ytop - 14, 30, 28, fill="#eaf0fd", stroke=NEG, sw=1.8))
        frags.append(line(xq + 15, ytop + 14, xq + 15, 156, color=col, sw=3))
        frags.append(rect(xq, 156, 30, 28, fill="#eaf0fd", stroke=NEG, sw=1.8))
        frags.append(line(xq + 15, 184, xq + 15, ybot, color=col, sw=3))
        frags.append(line(xc, ybot, xq + 15, ybot, color=col, sw=3))
        # підсвітка площі
        frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" '
                     'fill="%s" fill-opacity="0.08"/>'
                     % (xc - 4, ytop - 4, (xq + 15) - xc + 8, ybot - ytop + 8, col))
        frags.append(text(x0 + 70, 290, label, size=13, color=col, bold=True))

    stage(70, "близько → крихітна L", 36, hot=False)
    stage(430, "далеко → велика L", 150, hot=True)

    # вертикальний роздільник
    frags.append(line(400, 70, 400, 310, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(225, 322, "чистий вузол, мало завад", size=11, color=FIELD))
    frags.append(text(575, 322, "викиди, дзвін, ЕМС", size=11, color=POS))

    render(os.path.join(OUT, "loop-size.svg"), W, H, *frags,
           title="Та сама схема: вхідний конденсатор близько чи далеко від ключів")


# ── 3. Яка петля гаряча ──────────────────────────────────────────────────────
def fig_which_loop():
    W, H = 760, 340
    frags = []
    # buck — ліворуч
    frags.append(text(190, 60, "buck", size=15, color=INK, bold=True))
    frags.append('<rect x="60" y="80" width="120" height="150" rx="10" '
                 'fill="%s" fill-opacity="0.10"/>' % POS)
    frags.append(text(120, 100, "ВХІД", size=12, color=POS, bold=True))
    frags.append(text(120, 118, "різаний струм", size=10, color=POS))
    frags.append(text(120, 134, "ГАРЯЧА", size=11, color=POS, bold=True))
    frags.append('<rect x="200" y="80" width="120" height="150" rx="10" '
                 'fill="%s" fill-opacity="0.10"/>' % NEG)
    frags.append(text(260, 100, "ВИХІД", size=12, color=NEG, bold=True))
    frags.append(text(260, 118, "струм котушки", size=10, color=NEG))
    frags.append(text(260, 134, "холодна", size=11, color=NEG, bold=True))

    # boost — праворуч (дзеркально)
    frags.append(text(570, 60, "boost", size=15, color=INK, bold=True))
    frags.append('<rect x="440" y="80" width="120" height="150" rx="10" '
                 'fill="%s" fill-opacity="0.10"/>' % NEG)
    frags.append(text(500, 100, "ВХІД", size=12, color=NEG, bold=True))
    frags.append(text(500, 118, "струм котушки", size=10, color=NEG))
    frags.append(text(500, 134, "холодний", size=11, color=NEG, bold=True))
    frags.append('<rect x="580" y="80" width="120" height="150" rx="10" '
                 'fill="%s" fill-opacity="0.10"/>' % POS)
    frags.append(text(640, 100, "ВИХІД", size=12, color=POS, bold=True))
    frags.append(text(640, 118, "різаний (діод)", size=10, color=POS))
    frags.append(text(640, 134, "ГАРЯЧА", size=11, color=POS, bold=True))

    bx, bw, bh = textbox(380, 280, ["Рецепт: знайди, ДЕ струм рветься,",
                                    "— ту петлю й зроби крихітною."],
                         size=12, fill="#fbf7ec", stroke="#caa24a")
    frags.append(bx)

    render(os.path.join(OUT, "which-loop.svg"), W, H, *frags,
           title="Гаряча — петля з різаним струмом; у boost усе дзеркально")


# ── 4. Вузол перемикання SW ──────────────────────────────────────────────────
def fig_sw_node():
    W, H = 760, 360
    frags = []
    # маленький SW
    frags.append(text(195, 70, "малий SW — добре", size=13, color=FIELD, bold=True))
    frags.append(rect(150, 100, 56, 30, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(178, 120, "Q1", size=12, color=NEG, bold=True))
    frags.append(line(206, 115, 250, 115, color="#caa24a", sw=6))   # коротка SW-мідь
    frags.append(coil(250, 115, 320, turns=3))
    frags.append(text(228, 100, "SW", size=11, color="#caa24a", bold=True))
    frags.append(text(195, 165, "тільки під струм і тепло", size=10, color=MUTED))

    # великий SW = антена
    frags.append(text(560, 70, "розлитий SW — антена", size=13, color=POS, bold=True))
    frags.append(rect(470, 100, 56, 30, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(498, 120, "Q1", size=12, color=NEG, bold=True))
    frags.append('<rect x="526" y="96" width="120" height="44" rx="6" '
                 'fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="1.6"/>' % (POS, POS))
    frags.append(text(586, 122, "велика мідь SW", size=10, color=POS, bold=True))
    frags.append(coil(646, 115, 700, turns=2))
    # хвилі випромінювання
    for r in (18, 32, 46):
        frags.append('<path d="M 586 150 A %d %d 0 0 0 %d 150" fill="none" '
                     'stroke="%s" stroke-width="1.4" stroke-dasharray="3,3"/>'
                     % (r, r, 586 + 2 * r, POS))
    frags.append(text(586, 215, "повний розмах Vвх за нс → світить в ефір", size=10, color=POS))

    bx, bw, bh = textbox(380, 285, ["SW — найшвидше змінна напруга на платі.",
                                    "Мідь тут ОБМЕЖУЮТЬ: рівно під струм і тепло."],
                         size=12, fill="#fbf7ec", stroke="#caa24a")
    frags.append(bx)

    render(os.path.join(OUT, "sw-node.svg"), W, H, *frags,
           title="Вузол перемикання: велика мідь = антена")


# ── 5. Kelvin до FB-дільника ─────────────────────────────────────────────────
def fig_kelvin():
    W, H = 760, 360
    frags = []
    ytrace = 130
    # силова доріжка з вихідним конденсатором
    frags.append(line(110, ytrace, 470, ytrace, color="#caa24a", sw=7))
    frags.append(text(110, ytrace - 16, "силова доріжка (тече струм I)", size=11,
                      color="#caa24a", bold=True, anchor="start"))
    frags.append(cap(470, ytrace, color=INK, sw=3))
    frags.append(text(470, ytrace - 16, "Cвих", size=11, color=INK, bold=True))
    frags.append(line(470, ytrace, 560, ytrace, color=INK, sw=2))
    frags.append(text(566, ytrace + 4, "→ навантаження", size=11, color=INK, anchor="start"))

    # ПОГАНО: відбір посеред доріжки
    frags.append(line(280, ytrace, 280, 235, color=POS, sw=2, dash="5,3"))
    frags.append(text(280, 252, "погано:", size=11, color=POS, bold=True))
    frags.append(text(280, 268, "ловить IR + шум SW", size=10, color=POS))

    # ДОБРЕ: Kelvin із виводів Cвих
    frags.append(line(470, ytrace + 4, 470, 300, color=FIELD, sw=2))
    frags.append(line(470, 300, 360, 300, color=FIELD, sw=2))
    frags.append(text(415, 290, "Kelvin: окрема тиха доріжка", size=10, color=FIELD, bold=True))
    frags.append(rect(300, 300, 60, 28, fill="#eef7f0", stroke=FIELD, sw=1.8))
    frags.append(text(330, 318, "FB", size=12, color=FIELD, bold=True))

    bx, bw, bh = textbox(620, 250, ["міряємо напругу", "там, де її бачить", "навантаження"],
                         size=11, fill="#eef7f0", stroke=FIELD)
    frags.append(bx)

    render(os.path.join(OUT, "kelvin-sense.svg"), W, H, *frags,
           title="Відбір FB: Kelvin просто з виводів вихідного конденсатора")


# ── 6. Карта доброго розведення ──────────────────────────────────────────────
def fig_map():
    W, H = 760, 420
    frags = []
    cards = [
        ("1. Гаряча петля", "Cвх упритул до ключів —\nкрихітна площа", POS),
        ("2. Вузол SW", "малий: рівно під\nструм і тепло", "#caa24a"),
        ("3. Земля", "суцільний полігон,\nкороткий зворот", INK),
        ("4. FB — Kelvin", "тиха доріжка просто\nз виводів Cвих", FIELD),
        ("5. Тепловідвід", "мідь + via під\nгарячі деталі", COPPER),
        ("6. Розділення", "силове осторонь\nсигнального", NEG),
    ]
    cw, ch, gx, gy = 210, 96, 30, 28
    x0, y0 = 40, 60
    for i, (head, body, col) in enumerate(cards):
        r, c = divmod(i, 3)
        x = x0 + c * (cw + gx)
        y = y0 + r * (ch + gy)
        frags.append(rect(x, y, cw, ch, fill="#f7faf8", stroke=col, sw=2))
        frags.append(text(x + cw / 2, y + 26, head, size=13, color=col, bold=True))
        frags.append(mtext(x + cw / 2, y + 50, body, size=11, color=INK))

    frags.append(text(W / 2, 392, "Дотримай шість — і навіть проста схема працюватиме чисто.",
                      size=12, color=INK, bold=True))

    render(os.path.join(OUT, "layout-map.svg"), W, H, *frags,
           title="Карта доброго розведення: шість правил")


if __name__ == "__main__":
    fig_hotloop()
    fig_loop_size()
    fig_which_loop()
    fig_sw_node()
    fig_kelvin()
    fig_map()
    print("ok figs")
