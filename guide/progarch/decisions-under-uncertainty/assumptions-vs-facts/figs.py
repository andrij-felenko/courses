# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GREEN_TINT = "#eaf7ef"
RED_TINT   = "#fdecea"


def _box(cx, cy, s, **kw):
    return textbox(cx, cy, s, **kw)[0]


# ── 1. Класифікація переконання: факт чи припущення, і що робити ──────────────
def fig_classify():
    W, H = 820, 500
    p = []

    # рівень 0-1: переконання → питання
    p.append(_box(410, 72, "Переконання, на якому\nстоїть рішення", size=14))
    p.append(_box(410, 146, "Питання: як я це знаю?", size=14, bold=True,
                  fill="#eef2f7"))

    # гілка «факт» (ліворуч) і «припущення» (праворуч)
    p.append(_box(200, 250, "ФАКТ\nбудуй на ньому", size=14,
                  fill=GREEN_TINT, stroke=FIELD))
    p.append(_box(620, 250, "ПРИПУЩЕННЯ\nпознач як здогад", size=14,
                  fill=RED_TINT, stroke=POS))

    # зважування й дві дії
    p.append(_box(620, 340, "Зваж: P(хибне) × втрата", size=14))
    p.append(_box(470, 440, "Перевір зараз\n(купи інформацію)", size=13.5,
                  fill=GREEN_TINT, stroke=FIELD))
    p.append(_box(700, 440, "Прийми + знак\n(тригер на перегляд)", size=13.5))

    # стрілки
    p.append(arrow(410, 100, 410, 126))          # N0 → Q
    p.append(arrow(360, 164, 236, 222))          # Q → ФАКТ
    p.append(arrow(462, 164, 604, 222))          # Q → ПРИПУЩЕННЯ
    p.append(arrow(620, 278, 620, 321))          # ПРИПУЩЕННЯ → Зваж
    p.append(arrow(566, 358, 486, 412))          # Зваж → Перевір
    p.append(arrow(676, 358, 700, 412))          # Зваж → Прийми

    # підписи на гілках (осторонь від ліній)
    p.append(text(248, 182, "є доказ", size=12, color=MUTED))
    p.append(text(576, 182, "нема доказу", size=12, color=MUTED))

    return render(os.path.join(OUT, 'classify-belief.svg'), W, H, *p,
                  title="Як я це знаю? — розсортувати переконання й діяти")


# ── 2. Мапа припущень: впевненість × вплив → що робити ───────────────────────
def fig_map():
    W, H = 680, 560
    p = []

    gx, gy, gw, gh = 150, 80, 450, 400
    cw, ch = gw / 2, gh / 2

    # чотири клітини (fitbox — текст сам влазить у задану рамку)
    p.append(fitbox(gx,        gy,        cw, ch,
                    "ПЕРЕВІР ПЕРШИМ\n\nдорого помилитись,\nмало впевненості",
                    size=14, fill=RED_TINT, stroke=POS))
    p.append(fitbox(gx + cw,   gy,        cw, ch,
                    "Спирайся,\nале тримай знак\n\n(може змінитись)",
                    size=14, fill=FILL, stroke=LINE))
    p.append(fitbox(gx,        gy + ch,   cw, ch,
                    "Не марнуй перевірку\n\nприйми як є",
                    size=14, fill="#f7f8fa", stroke=LINE))
    p.append(fitbox(gx + cw,   gy + ch,   cw, ch,
                    "Це вже факт\n\nне стеж як за ризиком",
                    size=14, fill=GREEN_TINT, stroke=FIELD))

    # вісь X (впевненість) — стрілка й підпис під сіткою
    p.append(arrow(gx, gy + gh + 22, gx + gw, gy + gh + 22, color=MUTED))
    p.append(text((gx + gx + gw) / 2, gy + gh + 46,
                  "впевненість, що припущення істинне →", size=12.5, color=INK))

    # вісь Y (вплив) — стрілка ліворуч і підпис (три рядки, без повороту)
    p.append(arrow(gx - 22, gy + gh, gx - 22, gy, color=MUTED))
    p.append(mtext(78, gy + gh / 2 - 14, ["вплив,", "якщо", "хибне  ↑"],
                   size=12.5, color=INK))

    return render(os.path.join(OUT, 'assumption-map.svg'), W, H, *p,
                  title="Мапа припущень: що перевіряти першим")


# ── маленькі примітиви для дерева рішень ─────────────────────────────────────
def _sq(cx, cy, s=18, fill=FILL, stroke=INK):
    """Квадрат — вузол рішення."""
    return rect(cx - s / 2, cy - s / 2, s, s, fill=fill, stroke=stroke, sw=2, rx=0)


def _ch(cx, cy, r=16, fill="#eef2f7", stroke=INK):
    """Коло — вузол випадку."""
    return circle(cx, cy, r, fill=fill, stroke=stroke, sw=2)


# ── 3. Дерево рішень: EVPI (цінність ідеальної інформації) на кейсі замка ─────
def fig_voi_tree():
    W, H = 940, 620
    p = []

    # розділювач між двома деревами
    p.append(line(500, 96, 500, 500, color=MUTED, sw=1, dash="4,6"))
    p.append(text(250, 68, "Без перевірки — діємо на пріор", size=14.5, bold=True))
    p.append(text(720, 68, "З ясновидінням — правда наперед", size=14.5, bold=True))

    # ── ліве дерево (без інформації) ─────────────────────────────
    D1 = (95, 300)
    C1 = (285, 205)
    p.append(_sq(*D1))
    p.append(_ch(*C1))

    l0, _, _ = textbox(455, 150, "0", size=14, min_w=54, fill=GREEN_TINT, stroke=FIELD)
    l120, _, _ = textbox(455, 262, "120", size=14, min_w=54, fill=RED_TINT, stroke=POS)
    lb, _, _ = textbox(300, 442, "40", size=14, min_w=54, fill=FILL)
    p += [l0, l120, lb]

    # ребра
    p.append(line(D1[0] + 11, D1[1] - 9, C1[0] - 15, C1[1] + 9))     # D1 → C1 (купити)
    p.append(line(D1[0] + 9, D1[1] + 11, 273, 426))                 # D1 → будувати-leaf
    p.append(line(C1[0] + 14, C1[1] - 6, 428, 154))                # C1 → 0
    p.append(line(C1[0] + 14, C1[1] + 7, 428, 258))                # C1 → 120

    # підписи ребер (осторонь ліній)
    p.append(text(168, 232, "купити", size=12.5, color=MUTED))
    p.append(text(150, 392, "будувати", size=12.5, color=MUTED))
    p.append(text(360, 146, "тримає · 0.70", size=12, color=MUTED))
    p.append(text(378, 292, "падає · 0.30", size=12, color=MUTED))

    # згортки
    p.append(text(285, 176, "36", size=14, bold=True, color=POS))       # E у C1
    p.append(text(96, 348, "→ 36", size=12.5, color=INK))               # вибір у D1

    # ── праве дерево (ясновидіння) ───────────────────────────────
    C2 = (600, 232)
    p.append(_ch(*C2))
    r0, _, _ = textbox(800, 165, "0", size=14, min_w=54, fill=GREEN_TINT, stroke=FIELD)
    r40, _, _ = textbox(800, 322, "40", size=14, min_w=54, fill=FILL)
    p += [r0, r40]
    p.append(line(C2[0] + 14, C2[1] - 7, 772, 171))
    p.append(line(C2[0] + 14, C2[1] + 8, 772, 316))
    p.append(text(688, 176, "0.70 · купити", size=11.5, color=MUTED))
    p.append(text(700, 308, "0.30 · будувати", size=11.5, color=MUTED))
    p.append(text(600, 202, "12", size=14, bold=True, color=FIELD))     # E у C2

    # банер EVPI
    banner, _, _ = textbox(320, 556,
                           "EVPI = 36 − 12 = 24 люд-дні  ·  стеля ціни перевірки",
                           size=13.5, fill=GREEN_TINT, stroke=FIELD)
    p.append(banner)

    return render(os.path.join(OUT, 'voi-decision-tree.svg'), W, H, *p,
                  title="Дерево рішень: цінність ідеальної інформації (EVPI)")


# ── 4. Крива VoI(p): де перевірка цінна, а де марна ──────────────────────────
def fig_voi_curve():
    W, H = 780, 500
    p = []
    gx, gy, gw, gh = 120, 92, 560, 300
    base = gy + gh          # y осі X (VoI = 0)
    vmax = 30.0

    def X(pp):
        return gx + pp * gw

    def Y(v):
        return base - (v / vmax) * gh

    # осі
    p.append(arrow(gx, base, gx + gw + 18, base, color=MUTED))
    p.append(arrow(gx, base, gx, gy - 18, color=MUTED))
    p.append(text(gx + gw / 2, base + 42, "P(припущення хибне) →", size=13))
    p.append(mtext(48, gy + 46, ["цінність", "інфор-", "мації ↑"], size=12))

    # намет VoI(p): (0,0)–(1/3, 26.7)–(1,0)
    pk = 1.0 / 3.0
    vpk = 80 * pk           # 26.67
    p.append(line(X(0), Y(0), X(pk), Y(vpk), color=POS, sw=2.5))
    p.append(line(X(pk), Y(vpk), X(1), Y(0), color=POS, sw=2.5))

    # вертикаль байдужості
    p.append(line(X(pk), Y(vpk), X(pk), base, color=MUTED, sw=1, dash="4,6"))
    p.append(text(X(pk), base + 22, "p* = 1/3", size=12, color=MUTED))

    # наша точка p = 0.30 → 24
    p.append(circle(X(0.30), Y(24), 5, fill=INK, stroke=INK))
    p.append(text(X(0.30) - 12, Y(24) - 12, "наш кейс: 24", size=12, bold=True, anchor="end"))

    # пік і зони дій
    p.append(text(X(pk) + 4, Y(vpk) - 16, "пік — рішення на вістрі", size=12, bold=True, anchor="start"))
    p.append(text(X(0.15), Y(5.5), "обираємо: купити", size=11, color=MUTED))
    p.append(text(X(0.63), Y(5.5), "обираємо: будувати", size=11, color=MUTED))

    return render(os.path.join(OUT, 'voi-curve.svg'), W, H, *p,
                  title="Цінність інформації як функція непевності")


# ── 5. Лінія часу дисципліни: три світи + засторога (для hist-вставки) ────────
def fig_timeline():
    W, H = 780, 560
    PLAN, INTEL, START, CAUT = FIELD, NEG, "#8e44ad", POS
    rows = [
        (1987, PLAN,  "ABP розпочато в RAND (Army 21)"),
        (1993, PLAN,  "Звіт RAND MR-114"),
        (1999, INTEL, "Гоєр: «Psychology of Intelligence Analysis»"),
        (1999, CAUT,  "Mars Climate Orbiter втрачено"),
        (2002, PLAN,  "Дьюар: книга про несучі передумови"),
        (2005, START, "Бланк: «Four Steps to the Epiphany»"),
        (2009, INTEL, "Tradecraft Primer: Key Assumptions Check"),
        (2011, START, "Рис: «The Lean Startup» — стрибок віри"),
        (2016, START, "Гайем: Riskiest Assumption Test"),
    ]
    p = []
    x_spine = 250
    y0, dy = 84, 48
    y_last = y0 + (len(rows) - 1) * dy
    p.append(line(x_spine, y0 - 14, x_spine, y_last + 14, color=MUTED, sw=2))
    for i, (yr, col, lab) in enumerate(rows):
        y = y0 + i * dy
        p.append(text(214, y + 5, str(yr), size=13.5, color=INK, anchor="end", bold=True))
        p.append(circle(x_spine, y, 7, fill=col, stroke=col, sw=1.5))
        p.append(text(272, y + 5, lab, size=13.5, color=INK, anchor="start"))
    ly = 522
    leg = [(PLAN, "планування"), (INTEL, "розвідка"),
           (START, "стартапи"), (CAUT, "засторога")]
    lx = [60, 250, 440, 630]
    for (col, name), x in zip(leg, lx):
        p.append(circle(x, ly, 7, fill=col, stroke=col, sw=1.5))
        p.append(text(x + 16, ly + 5, name, size=12.5, color=INK, anchor="start"))
    return render(os.path.join(OUT, 'discipline-timeline.svg'), W, H, *p,
                  title="Три лінії розвитку, одна засторога")


# ── 6. Збіг словника: три племені — одне поняття (для hist-вставки) ───────────
def fig_converge():
    W, H = 880, 430
    p = []
    srcs = [
        (120, GREEN_TINT, FIELD,     ["Планування", "RAND, 1987", "несуча передумова"]),
        (225, "#eaf0fd",  NEG,       ["Розвідка", "ЦРУ, 2009", "ключове припущення"]),
        (330, "#f0e6f7",  "#8e44ad", ["Стартапи", "Lean, 2011", "стрибок віри"]),
    ]
    cx_src = 185
    for cy, fill, stroke, lines in srcs:
        p.append(_box(cx_src, cy, "\n".join(lines), size=14, fill=fill, stroke=stroke))
    p.append(_box(690, 225, "Те саме поняття —\nпереконання, на якому\nтримається весь план",
                  size=14, bold=True, fill="#eef2f7"))
    p.append(arrow(268, 120, 582, 212))
    p.append(arrow(268, 225, 582, 225))
    p.append(arrow(268, 330, 582, 238))
    return render(os.path.join(OUT, 'converge-names.svg'), W, H, *p,
                  title="Одна ідея, викувана тричі нарізно")


# ── 7. Ранг журналу припущень за очікуваною втратою (вихід інструмента) ───────
def fig_register_rank():
    W, H = 880, 440
    p = []
    x0 = 316          # ліва межа стовпчиків
    k = 10.5          # px на один людино-день

    rows = [
        ("Модуль замка тримає API ≥ 2р.",
         "P 0.30 · втрата 120 · перевірка 3", 36,
         "1 · гейт коміту", RED_TINT, POS),
        ("Брокер: 50 тис. на один вузол",
         "P 0.40 · втрата 60 · перевірка 4", 24,
         "2 · перевір", FILL, LINE),
        ("Відчиняють застосунком щодня",
         "P 0.30 · втрата 15 · перевірка 5", 4.5,
         "3 · прийми + знак", "#f7f8fa", LINE),
        ("Стабільний Wi-Fi без обривів",
         "P 0.50 · втрата 8 · перевірка 2", 4,
         "4 · прийми + знак", "#f7f8fa", LINE),
    ]
    ys = [120, 204, 288, 372]

    p.append(text(W / 2, 50, "очікувана втрата = P(хибне) × втрата, людино-дні",
                  size=13, color=MUTED))
    p.append(line(x0, 96, x0, 402, color=MUTED, sw=1))     # вісь стовпчиків

    for (claim, sub, v, tag, tf, ts), y in zip(rows, ys):
        bw = v * k
        top = v >= 30
        p.append(rect(x0, y - 16, bw, 32,
                      fill=RED_TINT if top else FILL,
                      stroke=POS if top else LINE, sw=1.5, rx=4))
        p.append(text(x0 + bw + 8, y + 5, ("%g" % v), size=14, bold=True, anchor="start"))
        p.append(text(24, y - 5, claim, size=13, anchor="start", bold=True))
        p.append(text(24, y + 14, sub, size=11, color=MUTED, anchor="start"))
        box, _, _ = textbox(806, y, tag, size=12.5, fill=tf, stroke=ts)
        p.append(box)

    return render(os.path.join(OUT, 'register-rank.svg'), W, H, *p,
                  title="Журнал припущень: ранг за очікуваною втратою")


if __name__ == "__main__":
    fig_classify()
    fig_map()
    fig_voi_tree()
    fig_voi_curve()
    fig_timeline()
    fig_converge()
    fig_register_rank()
    print("ok")
