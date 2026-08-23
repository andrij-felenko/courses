# -*- coding: utf-8 -*-
"""Фігури до кроку «Останній квиток» (модуль storage-as-decision, курс progarch).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

A_COL, B_COL = NEG, FIELD          # Покупець А — синій, Покупець Б — зелений
TINT_A, TINT_B = "#eaf0fd", "#eafaf0"
TINT_RED, TINT_GRAY = "#fdecea", "#f0f2f4"


# ───────── Фіг. 1: перегони «останнього квитка» (втрачене оновлення) ─────────
def fig_race_timeline():
    W, H = 1040, 470
    f = []

    yA, yB = 150, 300               # центри доріжок
    ch = 66
    x_left = 168
    # ── доріжки-фони на весь час ──
    f.append(rect(x_left, yA - ch / 2, 820, ch, fill="#f7f9fb", stroke="#e2e6ea", sw=1))
    f.append(rect(x_left, yB - ch / 2, 820, ch, fill="#f7f9fb", stroke="#e2e6ea", sw=1))
    f.append(text(96, yA + 5, "Покупець А", size=13, bold=True, color=A_COL))
    f.append(text(96, yB + 5, "Покупець Б", size=13, bold=True, color=B_COL))

    # центри чотирьох подій у часі
    t1, t2, t3, t4 = 268, 470, 672, 892
    cw = 176

    def card(cx, yc, s, accent, tint):
        return fitbox(cx - cw / 2, yc - ch / 2, cw, ch, s, size=12, bold=True,
                      fill=tint, stroke=accent, color=INK, sw=1.8)

    # А читає (t1), Б читає (t2) — обидва бачать 1, ще до будь-якого запису
    f.append(card(t1, yA, "A: SELECT seats_left\n→ бачить 1", A_COL, TINT_A))
    f.append(card(t2, yB, "Б: SELECT seats_left\n→ бачить 1", B_COL, TINT_B))
    # А пише 0 (t3), Б пише 0 поверх (t4)
    f.append(card(t3, yA, "A: UPDATE = 0\nCOMMIT", A_COL, TINT_A))
    f.append(card(t4, yB, "Б: UPDATE = 0 · COMMIT\n(стерло запис A)", POS, TINT_RED))

    # червона стрілка «Б вирішує на застарілому 1» — від читання Б до запису Б
    f.append(line(t2, yB + ch / 2 + 6, t2, 372, color=POS, sw=1.4, dash="3,4"))
    f.append(line(t4, yB + ch / 2 + 6, t4, 372, color=POS, sw=1.4, dash="3,4"))
    f.append(arrow(t2, 372, t4, 372, color=POS, sw=1.8))
    f.append(text((t2 + t4) / 2, 364,
                  "Б вирішує на застарілому 1 — хоча A вже записав 0",
                  size=11.5, bold=True, color=POS))

    # часова вісь із порядком подій
    ax = 420
    f.append(line(x_left, ax, 988, ax, color=INK, sw=1.6))
    for x, lab in ((t1, "① A читає 1"), (t2, "② Б читає 1"),
                   (t3, "③ A пише 0"), (t4, "④ Б пише 0")):
        f.append(line(x, ax - 5, x, ax + 5, color=INK, sw=1.4))
        f.append(text(x, ax + 22, lab, size=11.5, color=MUTED))
    f.append(text(x_left - 8, ax - 10, "час →", size=11, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "race-timeline.svg"), W, H, *f,
           title="Останній квиток: обидва прочитали 1 — оновлення A загублене, продано 2 місця")


# ───────── Фіг. 2: атомний guard закриває проміжок ─────────
def fig_guard_closes_gap():
    W, H = 1040, 460
    f = []

    yA, yB = 148, 300
    ch = 74
    x_left = 168
    f.append(rect(x_left, yA - ch / 2, 820, ch, fill="#f7f9fb", stroke="#e2e6ea", sw=1))
    f.append(rect(x_left, yB - ch / 2, 820, ch, fill="#f7f9fb", stroke="#e2e6ea", sw=1))
    f.append(text(96, yA + 5, "Покупець А", size=13, bold=True, color=A_COL))
    f.append(text(96, yB + 5, "Покупець Б", size=13, bold=True, color=B_COL))

    # А: один атомний оператор — бере замок рядка, 1→0, COMMIT
    f.append(fitbox(x_left + 20, yA - ch / 2 + 6, 300, ch - 12,
                    "A: UPDATE seats_left = seats_left − 1\nWHERE seats_left > 0\n→ 1 рядок · лишилось 0 · COMMIT",
                    size=12, bold=True, fill=TINT_B, stroke=FIELD, color=INK, sw=1.8))

    # Б: спершу чекає на замок (сіра смуга), тоді перечитує guard на свіжому 0
    f.append(fitbox(x_left + 20, yB - ch / 2 + 6, 300, ch - 12,
                    "Б: той самий UPDATE\n⛔ чекає на замок рядка A",
                    size=12, bold=True, fill=TINT_GRAY, stroke=MUTED, color=INK, sw=1.6))
    f.append(fitbox(560, yB - ch / 2 + 6, 380, ch - 12,
                    "замок вільний → guard на свіжому рядку:\n0 > 0 хибно → 0 рядків змінено\n→ застосунок: «продано»",
                    size=12, bold=True, fill=TINT_A, stroke=A_COL, color=INK, sw=1.8))

    # стрілка «А комітить → Б прокидається»
    f.append(arrow(340, yB, 552, yB, color=INK, sw=1.6))
    f.append(text(446, yB - 12, "A закомітив", size=11, color=MUTED))

    # підсумок-банер
    f.append(fitbox(x_left, 372, 820, 46,
                    "seats_left = 0   ·   продано РІВНО 1   ·   інваріант цілий — проміжку для Б немає",
                    size=13.5, bold=True, fill="#eafaf0", stroke=FIELD, color=INK, sw=2))

    render(os.path.join(IMG, "guard-closes-gap.svg"), W, H, *f,
           title="Один атомний UPDATE … WHERE: замок серіалізує, guard перечитує свіже значення")


# ───────── Фіг. 3: форма задачі → інструмент у сховищі ─────────
def fig_decision_map():
    W, H = 1060, 588
    f = []

    L, R = 30, 1030
    c1x, c1w = L, 300
    c2x, c2w = 340, 340
    c3x, c3w = 690, 340

    # заголовок таблиці
    hy, hh = 48, 40
    f.append(fitbox(c1x, hy, c1w, hh, "Форма задачі", size=13.5, bold=True,
                    fill="#eef1f6", stroke=MUTED, color=INK))
    f.append(fitbox(c2x, hy, c2w, hh, "Інструмент у сховищі", size=13.5, bold=True,
                    fill="#eef1f6", stroke=MUTED, color=INK))
    f.append(fitbox(c3x, hy, c3w, hh, "Ціна / коли брати", size=13.5, bold=True,
                    fill="#eef1f6", stroke=MUTED, color=INK))

    rows = [
        ("Лічильник із межею\n(−1 до нуля, +1 до стелі)",
         "Атомний UPDATE … WHERE guard\n(перевірка й зміна — один оператор)",
         "Дефолт. Найпростіше —\nбери це першим", FIELD, "#eafaf0"),
        ("Заявка на унікальне\n(місце, імʼя, пристрій)",
         "UNIQUE-обмеження + INSERT\n(індекс стає суддею)",
         "БД сама відхиляє дубль\nпомилкою унікальності", FIELD, "#eafaf0"),
        ("Прочитати → складна\nлогіка → записати, ексклюзивно",
         "SELECT … FOR UPDATE\n(песимістичний замок рядка)",
         "Один писар за раз;\nстережись дедлоку", NEG, "#eaf0fd"),
        ("Довге редагування,\nрідкі конфлікти",
         "Колонка version\n(оптимістичне блокування)",
         "Без замків; зайва\nробота при повторі", NEG, "#eaf0fd"),
        ("Інваріант на кілька рядків;\nзловити будь-яку аномалію",
         "SERIALIZABLE + повтор\n(БД ловить конфлікт сама)",
         "Повтори під\nнавантаженням (40001)", POS, "#fdecea"),
    ]

    ry, rh, gap = 96, 78, 6
    for i, (shape, tool, price, accent, tint) in enumerate(rows):
        y = ry + i * (rh + gap)
        f.append(fitbox(c1x, y, c1w, rh, shape, size=12.5, fill=FILL, stroke="#d7dbe0", color=INK))
        f.append(fitbox(c2x, y, c2w, rh, tool, size=12.5, bold=True, fill=tint, stroke=accent, color=INK, sw=1.8))
        f.append(fitbox(c3x, y, c3w, rh, price, size=12.5, fill=FILL, stroke="#d7dbe0", color=MUTED))

    # нижній висновок на всю ширину
    ny = ry + 5 * (rh + gap) + 6
    f.append(fitbox(L, ny, R - L, 48,
                    "Спільне в усіх рядках: рішення переносять У СХОВИЩЕ — воно, а не застосунок, стає суддею інваріанта в мить запису.",
                    size=13, bold=True, fill="#fbfbe8", stroke="#c9b458", color=INK, sw=1.8))

    render(os.path.join(IMG, "decision-map.svg"), W, H, *f,
           title="Форма задачі диктує інструмент — але всі вони віддають рішення сховищу")


# ───────── Фіг. 4 (вставка hist): дві лінії — механізм і словник ─────────
def fig_history_timeline():
    W, H = 1120, 600
    f = []
    axis_y = 300

    # легенда двох ліній (під заголовком)
    f.append(fitbox(298, 40, 246, 30, "▲ механізм — як стримати конкуренцію",
                    size=12, bold=True, fill=TINT_A, stroke=NEG, color=INK, sw=1.6))
    f.append(fitbox(576, 40, 246, 30, "▼ словник — як назвати аномалію",
                    size=12, bold=True, fill=TINT_B, stroke=FIELD, color=INK, sw=1.6))

    # часова вісь зі стрілкою
    f.append(arrow(66, axis_y, 1052, axis_y, color=INK, sw=2))
    f.append(text(1052, axis_y + 22, "час →", size=11.5, color=MUTED, anchor="end"))

    ticks = [180, 440, 700, 960]
    years = ["1976", "1981", "1992", "1995"]
    for x, yr in zip(ticks, years):
        f.append(fitbox(x - 36, axis_y - 19, 72, 38, yr, size=15, bold=True,
                        fill="#eef1f6", stroke=MUTED, color=INK, sw=1.5))

    cw, chh = 250, 92

    def top_card(x, s, tint, accent):
        cy = 150
        f.append(line(x, axis_y - 22, x, cy + chh / 2, color=accent, sw=1.3, dash="3,4"))
        f.append(fitbox(x - cw / 2, cy - chh / 2, cw, chh, s, size=12.5,
                        bold=False, fill=tint, stroke=accent, color=INK, sw=1.8))

    def bot_card(x, s, tint, accent):
        cy = 452
        f.append(line(x, axis_y + 22, x, cy - chh / 2, color=accent, sw=1.3, dash="3,4"))
        f.append(fitbox(x - cw / 2, cy - chh / 2, cw, chh, s, size=12.5,
                        bold=False, fill=tint, stroke=accent, color=INK, sw=1.8))

    # верхня лінія — механізм (синій)
    top_card(180, "Двофазний замок (2PL)\nЕсваран · Ґрей · Лорі · Трейґер\nдефолт епохи: блокуй наперед", TINT_A, NEG)
    top_card(440, "Kung & Robinson\nоптимізм: виконуй й перевіряй\nна валідації — відкат, не замок", TINT_A, NEG)
    top_card(960, "оптимізм визрів:\nversion-стовпець · snapshot\nisolation · MVCC-рушії", TINT_A, NEG)

    # нижня лінія — словник (зелений; критика 1995 — червона, це кульмінація)
    bot_card(180, "Ступені узгодженості\nlost update уже названо\n(Ґрей, Лорі, Пуцолу, Трейґер)", TINT_B, FIELD)
    bot_card(700, "SQL-92 (ANSI / ISO)\nрівні через 3 явища:\ndirty · non-repeatable · phantom", TINT_B, FIELD)
    bot_card(960, "Критика ANSI (SIGMOD)\nявищ замало → +dirty write,\n+lost update, +WRITE SKEW", TINT_RED, POS)

    # дужка «майже 20 років» під нижньою лінією
    by = 524
    f.append(line(180, by, 960, by, color=MUTED, sw=1.4))
    f.append(line(180, by - 6, 180, by, color=MUTED, sw=1.4))
    f.append(line(960, by - 6, 960, by, color=MUTED, sw=1.4))
    f.append(text(570, by + 22,
                  "майже 20 років — щоб дорахувати всі способи зіпсувати один рядок",
                  size=12.5, bold=True, color=MUTED))

    render(os.path.join(IMG, "history-timeline.svg"), W, H, *f,
           title="Дві лінії, що сходяться у статті: як стримати конкуренцію і як назвати зіпсоване")


# ───────── Фіг. 5 (вставка proj): бар'єр — одночасний наліт на квиток ─────────
def fig_stampede_barrier():
    W, H = 1100, 540
    f = []

    f.append(text(40, 90, "Покупці ×50 · своє з'єднання", size=13.5, bold=True,
                  color=INK, anchor="start"))

    bx, bw, bh = 40, 244, 46
    ys = [118, 176, 234, 292]
    labels = ["покупець 1 · conn #1", "покупець 2 · conn #2",
              "покупець 3 · conn #3", "покупець 4 · conn #4"]
    for y, lab in zip(ys, labels):
        f.append(fitbox(bx, y, bw, bh, lab, size=12.5, bold=True,
                        fill=TINT_A, stroke=NEG, color=INK, sw=1.6))
    f.append(fitbox(bx, 350, bw, bh, "…  ще 46   ( × 50 )", size=12.5, bold=True,
                    fill="#eef1f6", stroke=MUTED, color=MUTED, sw=1.4))

    allys = ys + [350]

    # бар'єр — вертикальна стіна
    gx = 352
    f.append(line(gx, 104, gx, 410, color=INK, sw=5))
    f.append(fitbox(gx - 62, 60, 124, 32, "⏸ БАР'ЄР", size=13.5, bold=True,
                    fill="#fbfbe8", stroke="#c9b458", color=INK, sw=1.8))

    # покупець → бар'єр (стають у чергу на старт)
    for y in allys:
        f.append(arrow(bx + bw + 4, y + bh / 2, gx - 6, y + bh / 2, color=MUTED, sw=1.4))

    # БД — висока коробка, ловить усі лінії
    dbx, dby, dbw, dbh = 744, 104, 318, 306
    f.append(fitbox(dbx, dby, dbw, dbh, "таблиця events\n\nseats_left = 1", size=19,
                    bold=True, fill="#f7f9fb", stroke=INK, color=INK, sw=2))

    # бар'єр → БД: усі паралельно, в одну мить
    for y in allys:
        f.append(arrow(gx + 8, y + bh / 2, dbx - 6, y + bh / 2, color=NEG, sw=1.5))

    f.append(text((gx + dbx) / 2, 88, "постріл → усі 50 ОДНОЧАСНО", size=12.5,
                  bold=True, color=NEG))
    f.append(text((gx + dbx) / 2, 438, "кожен: SELECT seats_left → усі бачать 1",
                  size=12, bold=True, color=NEG))

    f.append(fitbox(40, 462, 1020, 60,
                    "Наслідок: наївний продає ~40 квитків за ОДНЕ місце — і так ЩОРАЗУ, бо старт одночасний.\n"
                    "Без бар'єра читання розсипалися б у часі, перекриття було б рідким — і перегони «не відтворювались» би.",
                    size=12.5, fill=TINT_RED, stroke=POS, color=INK, sw=1.6))

    render(os.path.join(IMG, "stampede-barrier.svg"), W, H, *f,
           title="Стенд-наліт: бар'єр змушує 50 покупців ударити по квитку в одну мить")


# ───────── Фіг. 6 (вставка proj): вимір — 711 зайвих проти 0 ─────────
def fig_bench_results():
    W, H = 1080, 430
    f = []

    x0 = 250                    # старт смуг
    k = 560.0 / 731.0           # шкала: 731 продано → 560 px

    # заголовки колонок
    f.append(text(40, 92, "стратегія", size=13, bold=True, color=MUTED, anchor="start"))
    f.append(text(530, 92, "продано за 20 нальотів", size=13, bold=True, color=MUTED))
    f.append(text(965, 92, "зайвих квитків", size=13, bold=True, color=MUTED))

    # спільна базова лінія «0»
    f.append(line(x0, 138, x0, 330, color=MUTED, sw=1.2))
    f.append(text(x0, 348, "0", size=11, color=MUTED))

    # ── наївно (червона, довга) ──
    cy = 176
    w_naive = 731 * k
    f.append(rect(x0, cy - 24, w_naive, 48, fill=TINT_RED, stroke=POS, sw=1.8))
    f.append(text(x0 + w_naive / 2, cy + 5, "продано 731", size=14, bold=True, color=INK))
    f.append(text(40, cy - 2, "наївно", size=15, bold=True, color=POS, anchor="start"))
    f.append(text(40, cy + 20, "лічильник → 0 (чисто!)", size=11, color=MUTED, anchor="start"))
    f.append(text(965, cy + 9, "711", size=30, bold=True, color=POS))

    # ── вартовий (зелений, крихітний) ──
    cy = 290
    w_guard = 20 * k
    f.append(rect(x0, cy - 24, w_guard, 48, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(x0 + w_guard + 12, cy + 5, "продано 20", size=13, bold=True,
                  color=INK, anchor="start"))
    f.append(text(40, cy - 2, "вартовий", size=15, bold=True, color=FIELD, anchor="start"))
    f.append(text(40, cy + 20, "лічильник → 0 (чесно)", size=11, color=MUTED, anchor="start"))
    f.append(text(965, cy + 9, "0 ✓", size=30, bold=True, color=FIELD))

    f.append(fitbox(40, 360, 1000, 52,
                    "Той самий N = 50, той самий стенд. Різниця лише в тому, ХТО ухвалює рішення: "
                    "застосунок — сотні зайвих квитків; сховище — рівно нуль.",
                    size=13, fill="#fbfbe8", stroke="#c9b458", color=INK, sw=1.8))

    render(os.path.join(IMG, "bench-results.svg"), W, H, *f,
           title="Той самий наліт, дві стратегії: 711 зайвих квитків проти нуля")


if __name__ == "__main__":
    fig_race_timeline()
    fig_guard_closes_gap()
    fig_decision_map()
    fig_history_timeline()
    fig_stampede_barrier()
    fig_bench_results()
    print("OK: race-timeline.svg, guard-closes-gap.svg, decision-map.svg, "
          "history-timeline.svg, stampede-barrier.svg, bench-results.svg")
