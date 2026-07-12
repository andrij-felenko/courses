# -*- coding: utf-8 -*-
"""Фігури до кроку «Як зберігати час»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER = "#e08a00"
AMBER_F = "#fdf3e7"; AMBER_S = "#e08a3c"
RED_F = "#fdecea"
GREEN_F = "#eafaf1"


def cbox(cx, cy, w, h, s, **kw):
    """Рамка з центром (cx,cy) — текст автоматично влазить (fitbox)."""
    return fitbox(cx - w / 2.0, cy - h / 2.0, w, h, s, **kw)


def fig_instant_vs_civil():
    """Мить — точка на фізичній осі; цивільний намір лягає в неї через змінне правило."""
    W, H = 1020, 480
    frags = []

    # ── Верхня вісь: фізичний час (мить) ──
    ay = 165
    frags.append(text(110, ay - 44, "фізична вісь часу", size=14, bold=True, anchor="start"))
    frags.append(arrow(110, ay, 950, ay, color=INK, sw=2.2))

    # тверда точка-мить (ліворуч, окремо від цивільних)
    dotx = 265
    frags.append(circle(dotx, ay, 8, fill=INK, stroke=INK))
    frags.append(text(dotx, ay - 18, "мить · 21 °C", size=13, bold=True))
    frags.append(text(dotx, ay + 30, "вже сталася — фіксована", size=12, color=MUTED))

    # дві цільові точки того самого наміру за різних правил (праворуч, рознесені)
    px_winter, px_summer = 645, 815
    frags.append(text(730, ay - 42, "«07:00 Київ» за чинним правилом", size=12,
                      bold=True, color=MUTED))
    frags.append(circle(px_winter, ay, 7, fill=NEG, stroke=NEG))
    frags.append(circle(px_summer, ay, 7, fill=POS, stroke=POS))
    frags.append(text(px_winter, ay - 16, "+02:00", size=12, color=NEG, bold=True))
    frags.append(text(px_summer, ay - 16, "+03:00", size=12, color=POS, bold=True))
    frags.append(text(px_winter, ay + 28, "узимку", size=11, color=NEG))
    frags.append(text(px_summer, ay + 28, "улітку", size=11, color=POS))

    # ── Нижня вісь: громадянський календар (намір) ──
    cy = 375
    frags.append(text(110, cy + 46, "громадянський календар", size=14, bold=True, anchor="start"))
    frags.append(arrow(110, cy, 950, cy, color=INK, sw=2.2))
    intent_x = 730
    frags.append(circle(intent_x, cy, 8, fill=FIELD, stroke=FIELD))
    frags.append(text(intent_x, cy - 16, "людський намір", size=12, color=MUTED))
    frags.append(text(intent_x, cy + 32, "07:00 · Europe/Kyiv", size=13, bold=True))

    # два відображення намір → фізична вісь (обидва в правій частині, ліва вільна)
    frags.append(arrow(intent_x, cy - 10, px_winter, ay + 12, color=NEG, sw=1.8))
    frags.append(arrow(intent_x, cy - 10, px_summer, ay + 12, color=POS, sw=1.8))

    # пояснення правила — у вільному лівому просторі, осторонь стрілок
    b, _, _ = textbox(320, 285, "зсув зони — політичне\nправило, що змінюється (tzdata)",
                      size=12, fill="#fffaf0", stroke=AMBER)
    frags.append(b)

    frags.append(text(W / 2, 460,
                      "Той самий намір «07:00» лягає в РІЗНІ фізичні миті — залежно від чинного правила зони.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "instant-vs-civil.svg"), W, H, *frags,
           title="Мить проти наміру")


def fig_schedule_drift():
    """Майбутній розклад: заморожена UTC-мить з'їжджає, локальний+зона тримає 07:00."""
    W, H = 1020, 400
    frags = []

    # ── Ліва колонка підписів рядів (окремо від поля-графіка) ──
    frags.append(text(40, 165, "А · UTC-мить 05:00Z", size=13, anchor="start", bold=True))
    frags.append(text(40, 186, "(порахована взимку)", size=11, anchor="start", color=MUTED))
    frags.append(text(40, 255, "Б · локальний + зона", size=13, anchor="start", bold=True))

    # ── Поле-графік праворуч від підписів ──
    plot_l = 360
    axy = 330
    frags.append(arrow(plot_l, axy, 985, axy, color=MUTED, sw=1.6))
    frags.append(text(690, axy + 40, "настінний час у Києві  →", size=12, color=MUTED))

    hours = [(470, "06:00"), (620, "07:00"), (770, "08:00")]
    for hx, hl in hours:
        frags.append(line(hx, axy - 6, hx, axy + 6, color=MUTED, sw=1.4))
        frags.append(text(hx, axy + 22, hl, size=11, color=MUTED))

    # ціль 07:00 — вертикаль у полі
    goalx = 620
    frags.append(line(goalx, 150, goalx, axy, color=FIELD, sw=1.6, dash="5,4"))
    frags.append(text(goalx, 138, "ціль: 07:00", size=13, bold=True, color=FIELD))

    # подія переведення стрілок — у полі, у вільному просторі
    evx = 410
    frags.append(line(evx, 172, evx, axy, color=AMBER, sw=1.4, dash="4,4"))
    b, _, _ = textbox(evx, 130, "переведення\nстрілок (+1 год)", size=11,
                      fill="#fffaf0", stroke=AMBER)
    frags.append(b)

    # Ряд А: дот з'їхав на 08:00
    ya = 160
    driftx = 770
    frags.append(line(goalx, ya, driftx, ya, color=POS, sw=1.4, dash="3,3"))
    frags.append(circle(driftx, ya, 9, fill="#f7d9d5", stroke=POS, sw=2))
    frags.append(text(driftx + 22, ya + 5, "на годину пізніше (08:00)",
                      size=12, color=POS, anchor="start"))

    # Ряд Б: дот точно на цілі
    yb = 250
    frags.append(circle(goalx, yb, 9, fill="#d9f2e4", stroke=FIELD, sw=2))
    frags.append(text(goalx + 22, yb + 5, "тримає 07:00 — перерозв'язано за чинним правилом",
                      size=12, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "schedule-drift.svg"), W, H, *frags,
           title="Що робить зміна правила з майбутнім розкладом")


def fig_store_three_ways():
    """Три способи записати той самий час: мить / намір / обидва."""
    W, H = 1040, 430
    frags = []
    for sx in (347, 693):
        frags.append(line(sx, 46, sx, 400, color=MUTED, sw=1, dash="4,5"))

    panels = [
        (173, "А · UTC-мить", "2026-03-30\nT05:00:00Z", FILL, LINE,
         "подій, що вже сталися",
         "майбутній локальний час,\nколи зміняться правила"),
        (520, "Б · локальний + зона", "2026-03-30 07:00\n+ Europe/Kyiv", "#eafaf1", FIELD,
         "майбутніх і повторюваних\nцивільних подій",
         "неоднозначна година переходу;\nтреба розв'язувати"),
        (867, "В · обидва", "мить (кеш) +\nлокальний+зона (джерело)", "#fffaf0", AMBER,
         "розкладу, що треба\nі сортувати, і пережити зміну",
         "якщо кеш\nне перерозв'язувати"),
    ]
    for cx, title, store, fill, stroke, good, bad in panels:
        frags.append(text(cx, 66, title, size=14, bold=True))
        b, _, _ = textbox(cx, 120, store, size=12, fill=fill, stroke=stroke, min_w=250)
        frags.append(b)
        # + добре для
        frags.append(text(cx, 208, "＋ добре для", size=12, bold=True, color=FIELD))
        frags.append(mtext(cx, 230, good.split("\n"), size=12, color=INK))
        # − ламається
        frags.append(text(cx, 306, "－ ламається", size=12, bold=True, color=POS))
        frags.append(mtext(cx, 328, bad.split("\n"), size=12, color=INK))

    frags.append(text(W / 2, 410,
                      "Один час — три записи: точка на осі · людський намір · обидва з перекуванням миті.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "store-three-ways.svg"), W, H, *frags,
           title="Три способи записати той самий час")


def fig_tz_timeline():
    """Життя бази tzdata 1986→2023: заснування, суд, вервечка політичних правок часу."""
    W, H = 1260, 470
    f = []
    axy = 250
    f.append(arrow(58, axy, 1205, axy, color=MUTED, sw=1.8))

    # (x, рік, «above»/«below», заливка, обвід, підпис, жирний)
    events = [
        (120,  "1986",       "below", FILL,    MUTED,
         "Олсон заводить базу\nу NIH (США)", False),
        (290,  "1993",       "above", FILL,    MUTED,
         "Еґґерт: імена\nКонтинент/Місто", False),
        (460,  "2011",       "below", RED_F,   POS,
         "позов Astrolabe:\nбаза гасне, ICANN рятує", True),
        (630,  "груд. 2011", "above", AMBER_F, AMBER_S,
         "Самоа стрибає\nчерез лінію дат", True),
        (800,  "2019",       "below", AMBER_F, AMBER_S,
         "Європарламент 410–192:\nскасувати — застрягло", True),
        (970,  "2022",       "above", GREEN_F, FIELD,
         "Kiev → Kyiv:\nнавіть ім'я — рішення", True),
        (1140, "2023",       "below", AMBER_F, AMBER_S,
         "Ліван: два\nодночасні годинники", True),
    ]
    for x, year, side, fill, stroke, label, bold in events:
        f.append(circle(x, axy, 7, fill=fill, stroke=stroke, sw=2.5))
        if side == "above":
            bcy = 120
            f.append(line(x, axy - 7, x, bcy + 30, color=MUTED, dash="3 3"))
            f.append(text(x, axy + 24, year, size=15, bold=True))
        else:
            bcy = 380
            f.append(line(x, axy + 7, x, bcy - 30, color=MUTED, dash="3 3"))
            f.append(text(x, axy - 13, year, size=15, bold=True))
        f.append(cbox(x, bcy, 232, 60, label, size=12, fill=fill, stroke=stroke,
                      bold=bold))

    f.append(text(W / 2.0, 448,
                  "файл оновлюють кілька разів на рік — щоразу, як черговий уряд перепише правило часу",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(IMG, "tz-timeline.svg"), W, H, *f,
           title="tzdata: тридцять сім років політичного часу")


def fig_dst_edges():
    """Межа переходу: навесні година зникає, восени — повторюється двічі."""
    W, H = 1100, 560
    frags = []

    # ── Верхня стрічка: ВЕСНА, щілина ──
    frags.append(text(W / 2, 68, "Навесні · 2026-03-29 · стрілки 03:00 → 04:00",
                      size=16, bold=True))
    frags.append(text(W / 2, 92, "година «03:30» не існує — жодної миті на осі",
                      size=13, color=MUTED))

    y, ch = 150, 62
    spring = [  # (x, ширина, підпис, заливка, обвід, колір тексту)
        (90, 120, "02:00", FILL, LINE, INK),
        (218, 120, "02:30", FILL, LINE, INK),
        (346, 300, "03:00–03:59\n×  НЕ ІСНУЄ", RED_F, POS, POS),
        (654, 120, "04:00", FILL, LINE, INK),
        (782, 120, "04:30", FILL, LINE, INK),
    ]
    for x, cw, lbl, fill, stroke, color in spring:
        frags.append(fitbox(x, y, cw, ch, lbl, size=14, fill=fill,
                            stroke=stroke, color=color, bold=True))
    # анотація під щілиною — стрілка вниз повз клітини, текст у вільному просторі
    frags.append(line(496, y + ch, 496, 252, color=POS, sw=1.4, dash="4,4"))
    b, _, _ = textbox(560, 278,
                      "заплановане 03:30 → політика:\n"
                      "зсунути на 04:00 · відкотити на 02:59 · пропустити",
                      size=12.5, fill=AMBER_F, stroke=AMBER, min_w=560)
    frags.append(b)

    # ── Нижня стрічка: ОСІНЬ, повтор ──
    frags.append(text(W / 2, 384, "Восени · 2026-10-25 · стрілки 04:00 → 03:00",
                      size=16, bold=True))
    frags.append(text(W / 2, 408, "година «03:30» буває двічі — дві різні миті на осі",
                      size=13, color=MUTED))

    y2 = 450
    fall = [
        (90, 120, "02:30", FILL, LINE, INK),
        (270, 230, "03:00–03:59\nперше · EEST +03 · fold=0", GREEN_F, FIELD, FIELD),
        (516, 230, "03:00–03:59\nдруге · EET +02 · fold=1", GREEN_F, FIELD, FIELD),
        (762, 120, "04:30", FILL, LINE, INK),
    ]
    for x, cw, lbl, fill, stroke, color in fall:
        frags.append(fitbox(x, y2, cw, ch, lbl, size=12, fill=fill,
                            stroke=stroke, color=color, bold=True))
    b, _, _ = textbox(992, y2 + ch / 2, "fold=0 чи\nfold=1 —\nсвідомо",
                      size=12.5, fill=AMBER_F, stroke=AMBER, min_w=170)
    frags.append(b)

    render(os.path.join(IMG, "dst-edges.svg"), W, H, *frags,
           title="Дві межові години переходу")


def fig_reresolve_loop():
    """Варіант В: кеш-мить живе, лише поки джоб перекуває її після оновлення tzdata."""
    W, H = 1100, 470
    frags = []

    # ── Верхній ряд: джерело → кеш → планувальник ──
    a, aw, _ = textbox(172, 150, "ДЖЕРЕЛО ПРАВДИ\n07:00 · Europe/Kyiv",
                       size=13, fill=GREEN_F, stroke=FIELD, bold=True, min_w=224)
    b, bw, _ = textbox(560, 150, "КЕШ (похідне)\nnext_fire =\n2026-03-30 04:00:00Z",
                       size=13, fill=FILL, stroke=LINE, bold=True, min_w=250)
    c, cw, _ = textbox(948, 150, "ПЛАНУВАЛЬНИК\nвибирає за міттю",
                       size=13, fill=FILL, stroke=LINE, bold=True, min_w=210)
    frags += [a, b, c]
    frags.append(arrow(172 + aw / 2, 150, 560 - bw / 2, 150, color=INK, sw=2))
    frags.append(text((172 + aw / 2 + 560 - bw / 2) / 2, 132,
                      "розв'язати за tzdata", size=12, color=MUTED))
    frags.append(arrow(560 + bw / 2, 150, 948 - cw / 2, 150, color=INK, sw=2))
    frags.append(text((560 + bw / 2 + 948 - cw / 2) / 2, 132,
                      "дешевий індекс", size=12, color=MUTED))

    # ── Нижній ряд: подія оновлення → джоб → назад у кеш ──
    e, ew, _ = textbox(172, 355, "ОНОВЛЕННЯ tzdata\nЛіван 2023 · 2023a→2023c",
                       size=13, fill=AMBER_F, stroke=AMBER, bold=True, min_w=224)
    j, jw, jh = textbox(560, 355, "ДЖОБ ПЕРЕРОЗВ'ЯЗАННЯ\nпісля кожного апдейту",
                        size=13, fill=AMBER_F, stroke=AMBER, bold=True, min_w=250)
    frags += [e, j]
    frags.append(arrow(172 + ew / 2, 355, 560 - jw / 2, 355, color=AMBER, sw=2))
    frags.append(text((172 + ew / 2 + 560 - jw / 2) / 2, 337,
                      "тригер", size=12, color=MUTED))
    # джоб перекуває кеш (вертикальна стрілка вгору до КЕШу)
    frags.append(arrow(560, 355 - jh / 2, 560, 188, color=FIELD, sw=2))
    frags.append(text(600, 268, "перекувати кеш", size=12, color=FIELD, anchor="start"))

    # застереження про забутий джоб — праворуч, осторонь стрілок
    b2, _, _ = textbox(948, 355, "нема джоба →\nкеш протухає →\nВ вироджується в А",
                       size=12.5, fill=RED_F, stroke=POS, color=POS, bold=True, min_w=240)
    frags.append(b2)

    render(os.path.join(IMG, "reresolve-loop.svg"), W, H, *frags,
           title="Варіант В: кеш живе, поки його перекуває джоб")


if __name__ == "__main__":
    fig_instant_vs_civil()
    fig_schedule_drift()
    fig_store_three_ways()
    fig_tz_timeline()
    fig_dst_edges()
    fig_reresolve_loop()
    print("OK: instant-vs-civil.svg, schedule-drift.svg, store-three-ways.svg, "
          "tz-timeline.svg, dst-edges.svg, reresolve-loop.svg")
