# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: базове правило — лічильник = число посилань ────────────────────
def fig_count():
    W, H = 820, 380
    f = []

    # тримачі посилань зліва
    hx, hw, hh = 70, 160, 54
    holders = [("посилання a", 100), ("посилання b", 200), ("посилання c", 300)]
    for name, cy in holders:
        f.append(fitbox(hx, cy - hh / 2, hw, hh, name, size=15,
                        fill="#eaf0fd", stroke=NEG, sw=1.6))

    # об'єкт у купі
    ox, ow, oh, ocy = 320, 180, 130, 200
    f.append(fitbox(ox, ocy - oh / 2, ow, oh,
                    "об'єкт у купі\n\nлічильник: 3", size=16,
                    fill="#eafaf1", stroke=FIELD, sw=2.2, bold=True))

    # стрілки: правий край тримача → лівий край об'єкта (віялом)
    targets = [ocy - 42, ocy, ocy + 42]
    for (name, cy), ty in zip(holders, targets):
        f.append(arrow(hx + hw, cy, ox, ty, color=NEG, sw=1.8))

    # правила праворуч
    rlx = 560
    f.append(plus(rlx, 96, r=13))
    f.append(mtext(rlx + 26, 90, ["з'явилось посилання", "→ +1  (retain)"],
                   size=14, anchor="start"))
    f.append(minus(rlx, 176, r=13))
    f.append(mtext(rlx + 26, 170, ["посилання зникло", "→ −1  (release)"],
                   size=14, anchor="start"))
    f.append(fitbox(rlx - 20, 240, 250, 80,
                    "лічильник = 0\nніхто не дивиться\n→ звільнити негайно",
                    size=14, fill="#fdecea", stroke=POS, sw=1.8, bold=True))

    render(os.path.join(IMG, "count-rule.svg"), W, H, *f,
           title="Правило: лічильник дорівнює числу живих посилань")


# ── Фігура 2: каскад звільнення ──────────────────────────────────────────────
def fig_cascade():
    W, H = 860, 400
    f = []

    bw, bh = 170, 66

    def node(cx, cy, s, stroke, fill):
        f.append(fitbox(cx - bw / 2, cy - bh / 2, bw, bh, s, size=14,
                        fill=fill, stroke=stroke, sw=1.8, bold=True))
        return cx, cy

    # A щойно впав до нуля
    ax, ay = node(130, 110, "A\nлічильник 1→0\nзвільнити", POS, "#fdecea")
    # діти A
    bx, by = node(430, 90, "B\nлічильник 2→1\nвиживає", FIELD, "#eafaf1")
    cx, cy = node(430, 260, "C\nлічильник 1→0\nзвільнити", POS, "#fdecea")
    dx, dy = node(720, 260, "D\nлічильник 1→0\nзвільнити", POS, "#fdecea")

    # ребра власності A→B, A→C, C→D зі знаком «−» на кожному
    def edge(x1, y1, x2, y2, sign):
        f.append(arrow(x1, y1, x2, y2, color=INK, sw=1.8))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if sign == "-":
            f.append(minus(mx, my - 16, r=11))

    edge(ax + bw / 2, ay - 8, bx - bw / 2, by + 6, "-")
    edge(ax + bw / 2, ay + 8, cx - bw / 2, cy - 6, "-")
    edge(cx + bw / 2, cy, dx - bw / 2, dy, "-")

    f.append(mtext(W / 2, 350,
                   ["Один release на A запускає release на всьому, що A тримав,",
                    "а звільнення C — ще один на D: три звільнення однією хвилею."],
                   size=14, color=MUTED))

    render(os.path.join(IMG, "cascade.svg"), W, H, *f,
           title="Звільнення тягне звільнення: каскад однією хвилею")


# ── Фігура 3: цикл, який підрахунок не бачить ────────────────────────────────
def fig_cycle():
    W, H = 800, 400
    f = []

    # корінь (стек), що щойно відпустив
    rx, rw, rh = 300, 200, 56
    f.append(fitbox(rx - rw / 2, 60 - rh / 2, rw, rh,
                    "корінь на стеку", size=15, fill=FILL, stroke=MUTED, sw=1.6))
    # перерізане посилання кореня → A
    f.append(line(rx, 88, 320, 165, color=MUTED, sw=1.8, dash="6,6"))
    f.append(text(250, 130, "× посилання зникло", size=13, color=POS, bold=True))

    # цикл A ⇄ B
    aw, ah = 150, 90
    axc, ayc = 300, 250
    bxc, byc = 560, 250
    f.append(fitbox(axc - aw / 2, ayc - ah / 2, aw, ah,
                    "A\nлічильник: 1", size=15, fill="#eafaf1", stroke=FIELD, sw=2, bold=True))
    f.append(fitbox(bxc - aw / 2, byc - ah / 2, aw, ah,
                    "B\nлічильник: 1", size=15, fill="#eafaf1", stroke=FIELD, sw=2, bold=True))
    # A→B (верхня дуга) і B→A (нижня дуга)
    f.append(arrow(axc + aw / 2, ayc - 18, bxc - aw / 2, byc - 18, color=INK, sw=1.9))
    f.append(text((axc + bxc) / 2, ayc - 28, "тримає (+1)", size=12, color=INK))
    f.append(arrow(bxc - aw / 2, byc + 18, axc + aw / 2, ayc + 18, color=INK, sw=1.9))
    f.append(text((axc + bxc) / 2, byc + 40, "тримає (+1)", size=12, color=INK))

    # рамка «недосяжно, але живе»
    f.append(rect(axc - aw / 2 - 24, ayc - ah / 2 - 30, (bxc - axc) + aw + 48, ah + 70,
                  fill="none", stroke=POS, sw=1.6, rx=12))
    f.append(text((axc + bxc) / 2, byc + 78,
                  "недосяжно ззовні — та лічильники не падають до 0 → витік", size=13,
                  color=POS, bold=True))

    render(os.path.join(IMG, "cycle-leak.svg"), W, H, *f,
           title="Цикл: недосяжний ззовні, але звільнити нікому")


# ── Фігура 4: сильні й слабкі — контрольний блок ─────────────────────────────
def fig_control_block():
    W, H = 860, 420
    f = []

    # власники
    ow, oh = 150, 56
    f.append(fitbox(50, 100 - oh / 2, ow, oh, "shared_ptr", size=15,
                    fill="#eafaf1", stroke=FIELD, sw=1.8, bold=True))
    f.append(fitbox(50, 300 - oh / 2, ow, oh, "weak_ptr", size=15,
                    fill="#eaf0fd", stroke=NEG, sw=1.8, bold=True))

    # контрольний блок у центрі
    cbx, cbw, cbh, cby = 330, 200, 130, 200
    f.append(fitbox(cbx, cby - cbh / 2, cbw, cbh,
                    "керівний блок\n\nсильних: 1\nслабких: 1", size=15,
                    fill=FILL, stroke=INK, sw=2, bold=True))

    # керований об'єкт праворуч
    obx, obw, obh, oby = 640, 170, 90, 100
    f.append(fitbox(obx, oby - obh / 2, obw, obh, "керований\nоб'єкт", size=15,
                    fill="#eafaf1", stroke=FIELD, sw=2, bold=True))

    # shared_ptr → блок (суцільна), weak_ptr → блок (пунктир)
    f.append(arrow(200, 100, cbx, 150, color=FIELD, sw=2))
    f.append(arrow(200, 300, cbx, 250, color=NEG, sw=2, ))
    f.append(text(250, 300, "не тримає життя", size=12, color=NEG))
    # блок → об'єкт (власність, тільки поки сильних > 0)
    f.append(arrow(cbx + cbw, 175, obx, oby, color=FIELD, sw=2))
    f.append(text((cbx + cbw + obx) / 2, 160, "власність", size=12, color=FIELD))

    # правила знизу
    f.append(fitbox(50, 350, 360, 56,
                    "сильних = 0  →  звільнити ОБ'ЄКТ", size=14,
                    fill="#fdecea", stroke=POS, sw=1.6, bold=True))
    f.append(fitbox(440, 350, 380, 56,
                    "сильних = 0 і слабких = 0  →  звільнити БЛОК", size=14,
                    fill=FILL, stroke=MUTED, sw=1.6, bold=True))

    render(os.path.join(IMG, "control-block.svg"), W, H, *f,
           title="Сильні тримають об'єкт, слабкі тільки спостерігають")


# ── Фігура 5 (для вставки-історії): хронологія підрахунку посилань ────────────
def fig_timeline():
    # (рік, подія, колір-акцент, заливка) — червоні рядки = наскрізна тема циклів
    rows = [
        ("1960", "Джон Маккарті: LISP і трасувальний збирач (mark-sweep) —\n"
                 "суперник підрахунку, що лишиться поруч назавжди", MUTED, "#f1f3f5"),
        ("груд. 1960", "Джордж Коллінз, CACM: перший опис підрахунку —\n"
                       "лічильник, щоб безпечно стирати спільні списки", FIELD, "#eafaf1"),
        ("1963", "Дж. Макбет: підрахунок не бачить циклів —\n"
                 "сліпу пляму помічено вже за три роки", POS, "#fdecea"),
        ("1990", "Мартінес · Ваченчаузер · Лінс:\n"
                 "перший загальний збирач циклів для підрахунку", POS, "#fdecea"),
        ("1993", "Microsoft COM: IUnknown.AddRef / Release —\n"
                 "облік клієнтів через межі мов і процесів", NEG, "#eaf0fd"),
        ("1994", "OpenStep (NeXTSTEP): retain / release / autorelease —\n"
                 "ручний облік; звідси й самі назви операцій", NEG, "#eaf0fd"),
        ("жовт. 2000", "Python 2.0: до підрахунку (ob_refcnt) додано\n"
                       "окремий збирач циклів — гібрид у мейнстрімі", FIELD, "#eafaf1"),
        ("2007 → 2011", "C++: shared_ptr з Boost → звіт TR1 → стандарт C++11\n"
                        "(сильні й слабкі посилання, керівний блок)", NEG, "#eaf0fd"),
        ("2011", "Objective-C ARC: компілятор Clang сам розставляє\n"
                 "retain / release; згодом — основа пам'яті Swift", NEG, "#eaf0fd"),
        ("Rust", "Rc і Arc: ціну атомарного лічильника винесено\n"
                 "прямо в тип, і компілятор її пильнує", NEG, "#eaf0fd"),
    ]
    W = 960
    top = 70
    rh = 70
    H = top + len(rows) * rh + 24
    spine_x = 232
    f = []
    first_cy = top + rh / 2
    last_cy = top + (len(rows) - 1) * rh + rh / 2
    f.append(line(spine_x, first_cy - 26, spine_x, last_cy + 26, color=MUTED, sw=2.2))
    for i, (year, txt, col, fill) in enumerate(rows):
        cy = top + i * rh + rh / 2
        f.append(text(spine_x - 52, cy + 5, year, size=14, color=INK, anchor="end", bold=True))
        f.append(circle(spine_x, cy, 8, fill=fill, stroke=col, sw=2.6))
        f.append(fitbox(spine_x + 36, cy - 27, 640, 54, txt, size=14,
                        fill=fill, stroke=col, sw=1.7))
    render(os.path.join(IMG, "timeline.svg"), W, H, *f,
           title="Одне число крізь шість десятиліть")


# ── Фігура 6 (проєкт): розкладка нашого типу (Shared/Weak → блок → об'єкт) ────
def fig_layout():
    W, H = 940, 440
    f = []

    # власники
    f.append(fitbox(50, 72, 200, 96, "Shared<T>\n\nptr_\nblock_", size=15,
                    fill="#eafaf1", stroke=FIELD, sw=2, bold=True))
    f.append(fitbox(50, 300, 200, 96, "Weak<T>\n\nptr_\nblock_", size=15,
                    fill="#eaf0fd", stroke=NEG, sw=2, bold=True))

    # керівний блок
    f.append(fitbox(400, 150, 230, 170,
                    "керівний блок\n\nstrong = 1\nweak = 1\ndeleter", size=15,
                    fill=FILL, stroke=INK, sw=2.2, bold=True))

    # керований об'єкт
    f.append(fitbox(770, 175, 120, 110, "T\nкерований\nоб'єкт", size=15,
                    fill="#eafaf1", stroke=FIELD, sw=2, bold=True))

    # ребра володіння / спостереження
    f.append(arrow(250, 150, 400, 205, color=FIELD, sw=2))
    f.append(text(305, 148, "володіє", size=12, color=FIELD))
    f.append(arrow(250, 320, 400, 275, color=NEG, sw=2))
    f.append(text(305, 330, "спостерігає", size=12, color=NEG))
    f.append(arrow(630, 232, 770, 228, color=FIELD, sw=2))
    f.append(text(700, 214, "знищує (strong→0)", size=11, color=FIELD))

    # правила знизу
    f.append(fitbox(120, 372, 340, 52,
                    "strong = 0  →  ~T(), звільнити об'єкт", size=13,
                    fill="#fdecea", stroke=POS, sw=1.6, bold=True))
    f.append(fitbox(500, 372, 370, 52,
                    "strong = 0 і weak = 0  →  звільнити блок", size=13,
                    fill=FILL, stroke=MUTED, sw=1.6, bold=True))

    render(os.path.join(IMG, "layout.svg"), W, H, *f,
           title="Розкладка типу: власники → керівний блок → об'єкт")


# ── Фігура 7 (проєкт): захопити ДО звільнити (самоприсвоєння p = p) ───────────
def fig_assign():
    W, H = 940, 380
    f = []
    bw, bh = 132, 50

    def box(cx, cy, s, stroke, fill):
        f.append(fitbox(cx - bw / 2, cy - bh / 2, bw, bh, s, size=14,
                        fill=fill, stroke=stroke, sw=1.8, bold=True))

    def link(x1, x2, cy, badge=None):
        f.append(arrow(x1, cy, x2, cy, color=INK, sw=1.7))
        if badge == "+":
            f.append(plus((x1 + x2) / 2, cy - 26, r=12))
        elif badge == "-":
            f.append(minus((x1 + x2) / 2, cy - 26, r=12))

    f.append(text(W / 2, 60, "p = q,  коли p і q — той самий об'єкт (strong = 1)",
                  size=15, bold=True))

    cs = [120, 366, 612, 838]  # центри чотирьох колонок

    # трек A — правильний порядок
    yA = 152
    f.append(text(60, yA - 48, "захопити, потім звільнити:", size=13,
                  color=FIELD, anchor="start", bold=True))
    box(cs[0], yA, "strong = 1", INK, FILL)
    link(cs[0] + bw / 2, cs[1] - bw / 2, yA, "+")
    box(cs[1], yA, "strong = 2", NEG, "#eaf0fd")
    link(cs[1] + bw / 2, cs[2] - bw / 2, yA, "-")
    box(cs[2], yA, "strong = 1", INK, FILL)
    link(cs[2] + bw / 2, cs[3] - bw / 2, yA)
    box(cs[3], yA, "об'єкт живий", FIELD, "#eafaf1")

    # трек B — хибний порядок
    yB = 292
    f.append(text(60, yB - 48, "звільнити спершу:", size=13,
                  color=POS, anchor="start", bold=True))
    box(cs[0], yB, "strong = 1", INK, FILL)
    link(cs[0] + bw / 2, cs[1] - bw / 2, yB, "-")
    box(cs[1], yB, "strong = 0", POS, "#fdecea")
    f.append(text(cs[1], yB + bh / 2 + 16, "звільнено", size=11, color=POS))
    link(cs[1] + bw / 2, cs[2] - bw / 2, yB, "+")
    box(cs[2], yB, "+1 на трупі", POS, "#fdecea")
    link(cs[2] + bw / 2, cs[3] - bw / 2, yB)
    box(cs[3], yB, "крах", POS, "#fdecea")

    render(os.path.join(IMG, "assign-order.svg"), W, H, *f,
           title="Оператор присвоєння: +1 до −1 рятує самоприсвоєння")


# ── Фігура 8 (проєкт): подвійне звільнення блока (наївні незалежні лічильники) ─
def fig_race():
    W, H = 900, 470
    f = []

    # вісь часу
    f.append(arrow(58, 96, 58, 430, color=MUTED, sw=1.6))
    f.append(text(58, 82, "час", size=12, color=MUTED))

    # заголовки смуг
    f.append(fitbox(148, 66, 244, 46, "Потік 1: останній shared release",
                    size=13, fill="#eaf0fd", stroke=NEG, sw=1.6, bold=True))
    f.append(fitbox(518, 66, 244, 46, "Потік 2: останній weak release",
                    size=13, fill="#eaf0fd", stroke=NEG, sw=1.6, bold=True))

    L1, L2 = 270, 640
    ew, eh = 252, 46

    def ev(cx, cy, s, danger=False):
        f.append(fitbox(cx - ew / 2, cy - eh / 2, ew, eh, s, size=13,
                        fill="#fdecea" if danger else FILL,
                        stroke=POS if danger else INK, sw=1.6, bold=danger))

    ev(L1, 152, "--strong  →  0")
    ev(L2, 152, "--weak  →  0")
    ev(L1, 222, "знищити об'єкт ~T()")
    ev(L2, 222, "читає strong  →  бачить 0")
    ev(L1, 292, "читає weak  →  бачить 0")
    ev(L2, 292, "delete блок", danger=True)
    ev(L1, 372, "delete блок", danger=True)

    f.append(text(W / 2, 442, "обидва бачать нуль сусіда  →  блок звільнено ДВІЧІ",
                  size=14, color=POS, bold=True))

    render(os.path.join(IMG, "block-double-free.svg"), W, H, *f,
           title="Гонка: наївна перевірка обох лічильників звільняє блок двічі")


if __name__ == "__main__":
    fig_count()
    fig_cascade()
    fig_cycle()
    fig_control_block()
    fig_timeline()
    fig_layout()
    fig_assign()
    fig_race()
    print("OK: figures written to", IMG)
