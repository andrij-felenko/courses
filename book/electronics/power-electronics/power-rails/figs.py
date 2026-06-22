# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ORANGE = "#d98a00"   # 12 В гілка / попередження-порядок


# ── power-tree: дерево живлення від батареї-кореня ─────────────────────────────
# Ідея: усе живлення росте з одного кореня (батарея); сильнострумова гілка йде
# «сирою» до моторів, а логіка — каскадом перетворювачів 5 В → 3.3 В.
def fig_power_tree():
    W, H = 760, 430
    p = []

    # корінь — батарея ліворуч по центру
    bx, by = 40, 195
    p.append(rect(bx, by, 120, 60, fill="#eafaef", stroke=FIELD, sw=1.9))
    p.append(text(bx + 60, by + 26, "Батарея", size=13, color=FIELD, bold=True))
    p.append(text(bx + 60, by + 46, "4S ~14.8 В", size=11))

    rootx = bx + 120

    # гілка 1 — сира до ESC/моторів (червона, товста)
    p.append(line(rootx, by + 12, 250, 70, color=POS, sw=2.8))
    b1 = fitbox(250, 52, 200, 50, "ESC ×4 → мотори\n(сира батарея, ~100 А)",
                size=11, fill="#fff0f0", stroke=POS, color=POS, bold=True)
    p.append(b1)

    # гілка 2 — buck 5 В (головна шина)
    p.append(line(rootx, by + 25, 250, by + 12, color=INK, sw=2.2))
    p.append(fitbox(250, by - 14, 150, 50, "Buck → 5 В\n(головна шина)",
                    size=11, fill="#eef2ff", stroke=NEG, color=NEG, bold=True))
    busx = 400
    # від 5 В — контролер/приймач і далі LDO 3.3 В
    p.append(line(busx, by, 470, by - 40, color=INK, sw=1.6))
    p.append(fitbox(470, by - 62, 200, 44, "Контролер, приймач",
                    size=11, fill=BG, stroke=INK, color=INK, bold=True))
    p.append(line(busx, by + 14, 470, by + 60, color=INK, sw=1.6))
    p.append(fitbox(470, by + 38, 130, 44, "LDO → 3.3 В\n(тихо)",
                    size=10, fill="#eafaef", stroke=FIELD, color=FIELD, bold=True))
    p.append(line(600, by + 60, 620, by + 60, color=INK, sw=1.6))
    p.append(fitbox(620, by + 38, 120, 44, "Давачі\n(чисто)",
                    size=10, fill=BG, stroke=FIELD, color=FIELD, bold=True))

    # гілка 3 — buck 12 В (камера/підвіс)
    p.append(line(rootx, by + 40, 250, 360, color=INK, sw=2.2))
    p.append(fitbox(250, 338, 150, 44, "Buck → 12 В",
                    size=11, fill="#fff5e6", stroke=ORANGE, color=ORANGE, bold=True))
    p.append(line(400, 360, 470, 360, color=INK, sw=1.6))
    p.append(fitbox(470, 338, 180, 44, "Камера / підвіс",
                    size=11, fill=BG, stroke=ORANGE, color=ORANGE, bold=True))

    return render(os.path.join(OUT, "power-tree.svg"), W, H, *p)


# ── inrush: кидок струму при під'єднанні (з захистом і без) ────────────────────
# Ідея: порожній конденсатор у першу мить = коротке; без опору — гострий пік
# (іскра), з резистором передзаряду — пологий заряд.
def fig_inrush():
    W, H = 720, 360
    ox, oy = 80, 290          # початок осей
    aw, ah = 480, 230
    p = []

    # осі
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.5))
    p.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.5))
    p.append(text(ox + aw, oy + 18, "час", size=12, italic=True))
    p.append(text(ox - 10, oy - ah + 6, "струм входу", size=12, bold=True, anchor="end"))
    p.append(text(ox - 10, oy + 4, "0", size=10, color=MUTED, anchor="end"))

    # без захисту — гострий пік (червоний)
    spike = "M%d,%d L%d,%d L%d,%d L%d,%d L%d,%d" % (
        ox + 4, oy, ox + 8, oy - ah + 8, ox + 40, oy - 40, ox + 110, oy - 10, ox + 240, oy - 6)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (spike, POS))
    p.append(text(ox + 36, oy - ah + 2, "без захисту: пік → ІСКРА", size=11, color=POS, bold=True, anchor="start"))

    # з анти-іскрою — пологий заряд (зелений)
    soft = "M%d,%d L%d,%d L%d,%d L%d,%d L%d,%d" % (
        ox + 4, oy, ox + 70, oy - 70, ox + 180, oy - 28, ox + 320, oy - 8, ox + 460, oy - 6)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (soft, FIELD))
    p.append(text(ox + 250, oy - 56, "з анти-іскрою: пологий заряд", size=11, color=FIELD, bold=True, anchor="start"))

    return render(os.path.join(OUT, "inrush.svg"), W, H, *p)


# ── sequencing: рейки піднімаються в порядку ядро → вв/в → периферія ──────────
# Ідея: деяким чіпам напруги треба строго по черзі; контролер послідовності
# вмикає рейки одна за одною з паузами (так само у зворотному при вимкненні).
def fig_sequencing():
    W, H = 720, 340
    ox, oy = 120, 280
    aw = 540
    p = []
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.5))
    p.append(text(ox + aw, oy + 18, "час", size=12, italic=True))

    rows = [("ядро 1.8 В", NEG, 110, 180), ("вв/в 3.3 В", FIELD, 190, 240),
            ("периферія 5 В", ORANGE, 270, 300)]
    for label, col, x_rise, y_top in rows:
        y_lo = oy - 18
        # сходинка: низько до x_rise, далі вгору й полицею
        step = "M%d,%d L%d,%d L%d,%d L%d,%d" % (ox, y_lo, x_rise, y_lo, x_rise + 28, y_top, ox + aw, y_top)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (step, col))
        p.append(text(ox - 8, y_top + 4, label, size=11, color=col, bold=True, anchor="end"))
        p.append(line(x_rise + 14, y_lo, x_rise + 14, oy, color=col, sw=1.0, dash="3,3"))

    p.append(text(124, oy + 18, "1-ша", size=9, color=NEG))
    p.append(text(204, oy + 18, "2-га", size=9, color=FIELD))
    p.append(text(284, oy + 18, "3-тя", size=9, color=ORANGE))

    box = fitbox(470, 70, 230, 96,
                 "Подаси не в тому порядку —\nі чіп може «защемити»\n(latch-up), перегрітись\nчи зависнути. Тому ставлять\nконтролер послідовності.",
                 size=10, fill="#fff5e6", stroke=ORANGE, color=INK)
    p.append(box)

    return render(os.path.join(OUT, "sequencing.svg"), W, H, *p)


# ── grounding: спільна земля vs зіркова ───────────────────────────────────────
# Ідея: спільний провід землі має опір; струм мотора × опір = напруга, яку
# давач бачить як шум. Зіркова земля розводить шляхи в одну точку.
def fig_grounding():
    W, H = 760, 360
    p = []

    # ── ліворуч: НЕПРАВИЛЬНО ──
    p.append(rect(30, 60, 340, 250, fill="#fff7f7", stroke=POS, sw=1.6))
    p.append(text(200, 86, "Неправильно: спільна земля", size=12, color=POS, bold=True))
    # спільний провід землі
    p.append(circle(70, 150, 5, fill=INK, stroke="none"))
    p.append(text(70, 138, "− батареї", size=9, color=MUTED))
    p.append(line(70, 150, 340, 150, color=INK, sw=4))
    p.append(text(205, 142, "спільний провід землі (має опір)", size=9, color=MUTED))
    # мотор тягне струм у землю
    p.append(fitbox(120, 185, 80, 38, "мотор", size=11, fill="#fde2e2", stroke=POS, color=INK, bold=True))
    p.append(arrow(160, 185, 160, 154, color=POS, sw=3))
    p.append(text(200, 178, "великий струм", size=9, color=POS, anchor="start"))
    p.append(fitbox(250, 185, 80, 38, "давач", size=11, fill=BG, stroke=NEG, color=NEG, bold=True))
    p.append(line(290, 185, 290, 154, color=NEG, sw=1.6))
    p.append(text(200, 270, "струм × опір проводу = напруга,", size=10, color=POS))
    p.append(text(200, 288, "яку давач бачить як шум", size=10, color=POS, bold=True))

    # ── праворуч: ПРАВИЛЬНО ──
    p.append(rect(390, 60, 340, 250, fill="#f4fbf6", stroke=FIELD, sw=1.6))
    p.append(text(560, 86, "Правильно: зіркова земля", size=12, color=FIELD, bold=True))
    star = (560, 235)
    p.append(circle(star[0], star[1], 6, fill=INK, stroke="none"))
    p.append(text(560, 258, "одна спільна точка («зірка»)", size=9, color=MUTED))
    p.append(fitbox(430, 130, 80, 38, "мотор", size=11, fill="#fde2e2", stroke=POS, color=INK, bold=True))
    p.append(line(470, 168, star[0] - 6, star[1] - 4, color=POS, sw=3))
    p.append(fitbox(610, 130, 80, 38, "давач", size=11, fill=BG, stroke=NEG, color=NEG, bold=True))
    p.append(line(650, 168, star[0] + 6, star[1] - 4, color=NEG, sw=1.6))
    p.append(text(560, 290, "струм мотора не тече", size=10, color=FIELD))
    p.append(text(560, 305, "через землю давача", size=10, color=FIELD, bold=True))

    return render(os.path.join(OUT, "grounding.svg"), W, H, *p)


if __name__ == "__main__":
    fig_power_tree()
    fig_inrush()
    fig_sequencing()
    fig_grounding()
    print("OK figs:", sorted(os.listdir(OUT)))
