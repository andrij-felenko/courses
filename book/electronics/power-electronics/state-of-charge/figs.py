# -*- coding: utf-8 -*-
"""Фігури до теми «Заряд, що лишився» (state of charge) та її вставки.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут, AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Чому це важко: батарея непрозора, видно лише V та I ───────────────────
def fig_problem():
    W, H = 820, 360
    f = [text(W / 2, 28, "Скільки лишилось? Батарея не показує сама", size=17, bold=True)]

    # «непрозора» комірка ліворуч з великим знаком питання
    f.append(rect(70, 100, 120, 170, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    f.append(rect(105, 88, 50, 14, fill="#eef6ef", stroke=FIELD, sw=2, rx=4))   # «пиптик» комірки
    f.append(text(130, 205, "?", size=66, color=MUTED, bold=True))
    f.append(text(130, 240, "скільки %", size=11, color=INK, bold=True))
    f.append(text(130, 286, "видно лише V та I", size=9.5, color=MUTED))
    f.append(text(130, 300, "на клемах", size=9.5, color=MUTED))

    f.append(arrow(196, 185, 246, 185, color=INK, sw=2))

    # три способи оцінки
    cards = [
        (270, POS,   "1. Напруга",     "глянь на V → SoC",   "швидко, та бреше"),
        (462, NEG,   "2. Кулонометрія", "лічи заряд (∫I·dt)", "точно, та дрейфує"),
        (654, FIELD, "3. Поєднання",   "поєднай обидва",     "найкраще на практиці"),
    ]
    for x, col, t1, t2, t3 in cards:
        f.append(rect(x, 110, 148, 130, fill=BG, stroke=col, sw=2, rx=10))
        f.append(text(x + 74, 138, t1, size=12, color=col, bold=True))
        f.append(text(x + 74, 174, t2, size=9.5, color=INK))
        f.append(text(x + 74, 208, t3, size=9.5, color=MUTED))

    # підсумкова смуга
    f.append(fitbox(70, 292, 732, 44,
                    "Усе, що видно ззовні, — напруга й струм на клемах.\n"
                    "«Паливомір» батареї доводиться рахувати з них, і кожен спосіб має свою ваду.",
                    size=11, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=8, color=INK))
    render(os.path.join(IMG, "problem.svg"), W, H, *f)


# ── 2. Напруга → SoC: похила Li-ion проти плато LiFePO4 ──────────────────────
def fig_voltage():
    W, H = 820, 410
    f = [text(W / 2, 28, "Напруга → SoC: читається на похилій, бреше на плато", size=16, bold=True)]
    L, R, T, B = 110, 720, 70, 320

    def px(s):  return L + s * (R - L)            # s — частка SoC 0..1
    # осі
    f.append(line(L, B, R, B, color=INK, sw=1.6))
    f.append(line(L, B, L, T, color=INK, sw=1.6))
    f.append(text(L - 10, T + 4, "V", size=11, color=INK, bold=True, anchor="end"))
    for frac, lab in [(0, "0%"), (.25, "25%"), (.5, "50%"), (.75, "75%"), (1, "100%")]:
        x = px(frac)
        f.append(line(x, B, x, B + 5, color=INK, sw=1))
        f.append(text(x, B + 18, lab, size=9.5, color=MUTED))
    f.append(text((L + R) / 2, B + 36, "SoC (заряд)", size=11, color=INK))

    # похила Li-ion (помітний нахил)
    li = [(0, B - 30), (.25, B - 108), (.5, B - 140), (.75, B - 188), (1, B - 218)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' %
             (" ".join("%.1f,%.1f" % (px(s), y) for s, y in li), POS))
    f.append(text(px(.62) + 8, B - 168, "Li-ion (похила)", size=10, color=POS, bold=True, anchor="start"))

    # пласка LiFePO4 (майже горизонтальне плато 20..80%)
    lfp = [(0, B), (.12, B - 56), (.2, B - 66), (.8, B - 74), (.88, B - 80), (1, B - 100)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' %
             (" ".join("%.1f,%.1f" % (px(s), y) for s, y in lfp), "#caa24a"))
    f.append(text(px(.22) + 6, B - 52, "LiFePO4 (плато)", size=10, color="#caa24a", bold=True, anchor="start"))

    # підсвітка плоскої зони
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="22" fill="#caa24a" fill-opacity="0.16"/>'
             % (px(.2), B - 77, px(.8) - px(.2)))
    f.append(text((px(.2) + px(.8)) / 2, B - 61, "тут 10 мВ ≈ десятки % SoC", size=9, color="#caa24a", bold=True))

    f.append(fitbox(70, 352, 680, 46,
                    "На похилій Li-ion напрузі SoC читається пристойно.\n"
                    "На пласкому плато LFP дрібна похибка напруги (чи просадка I·Rвн) дає велетенську похибку SoC.",
                    size=10.5, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=8))
    render(os.path.join(IMG, "voltage.svg"), W, H, *f)


# ── 3. Кулонометрія: лічба заряду й повільний дрейф ─────────────────────────
def fig_coulomb():
    W, H = 820, 400
    f = [text(W / 2, 28, "Кулонометрія: лічимо заряд — точно коротко, але дрейфує", size=16, bold=True)]
    L, R, T, B = 110, 720, 70, 300

    def px(t):  return L + t * (R - L)            # t — час 0..1
    f.append(line(L, B, R, B, color=INK, sw=1.6))
    f.append(line(L, B, L, T, color=INK, sw=1.6))
    f.append(text(L - 10, T + 4, "SoC", size=10.5, color=INK, bold=True, anchor="end"))
    f.append(text((L + R) / 2, B + 24, "час", size=11, color=INK))

    # справжній SoC — гладко спадає
    true_pts = [(t / 20, B - (218 - 150 * (t / 20))) for t in range(21)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-dasharray="6 5"/>' %
             (" ".join("%.1f,%.1f" % (px(t), y) for t, y in true_pts), MUTED))
    f.append(text(px(.5), B - 150, "справжній SoC", size=9.5, color=MUTED))

    # оцінка кулонометра — спершу збігається, далі повільно «з'їжджає» вгору (накопичений зсув)
    est_pts = [(t / 20, B - (218 - 150 * (t / 20)) - 46 * (t / 20) ** 2) for t in range(21)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' %
             (" ".join("%.1f,%.1f" % (px(t), y) for t, y in est_pts), NEG))
    f.append(text(px(.78), B - 150, "лічба заряду", size=10, color=NEG, bold=True))

    # стрілка-«дрейф» між кривими наприкінці
    xe = px(1.0)
    f.append(line(xe + 6, true_pts[-1][1], xe + 6, est_pts[-1][1], color=POS, sw=1.6))
    f.append(text(xe + 12, (true_pts[-1][1] + est_pts[-1][1]) / 2 + 4, "дрейф", size=9.5, color=POS, bold=True, anchor="start"))

    # формула
    f.append(textbox(W / 2, 338, "SoC = SoC(старт) − (∫ I·dt) / Ємність",
                     size=13, fill="#eef0fd", stroke=NEG, sw=1.5, bold=True)[0])
    f.append(text(W / 2, 372, "дрібний зсув давача струму інтегрується в дедалі більшу помилку",
                  size=10, color=MUTED))
    render(os.path.join(IMG, "coulomb.svg"), W, H, *f)


# ── 4. Поєднання: лічба дає гладкість, напруга прибиває дрейф ────────────────
def fig_fusion():
    W, H = 820, 340
    f = [text(W / 2, 28, "Поєднання: лічба тримає гладкість, напруга прибиває дрейф", size=16, bold=True)]

    # два джерела ліворуч
    f.append(rect(60, 80, 210, 70, fill="#eef0fd", stroke=NEG, sw=2, rx=10))
    f.append(text(165, 104, "Кулонометрія", size=11.5, color=NEG, bold=True))
    f.append(text(165, 124, "гладка, точна коротко", size=9.5, color=INK))
    f.append(text(165, 140, "але дрейфує", size=9.5, color=MUTED))

    f.append(rect(60, 190, 210, 70, fill="#fdecea", stroke=POS, sw=2, rx=10))
    f.append(text(165, 214, "Напруга", size=11.5, color=POS, bold=True))
    f.append(text(165, 234, "абсолютна прив'язка", size=9.5, color=INK))
    f.append(text(165, 250, "(спокій, край кривої)", size=9.5, color=MUTED))

    # суматор
    f.append(circle(370, 170, 26, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(text(370, 176, "+", size=24, color=FIELD, bold=True))
    f.append(arrow(270, 115, 348, 158, color=NEG, sw=2))
    f.append(arrow(270, 225, 348, 184, color=POS, sw=2))

    # результат праворуч
    f.append(arrow(396, 170, 470, 170, color=INK, sw=2))
    f.append(rect(470, 120, 290, 100, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    f.append(text(615, 148, "Оцінка SoC", size=12.5, color=FIELD, bold=True))
    f.append(text(615, 174, "точніша за кожен метод окремо", size=10, color=INK))
    f.append(text(615, 196, "так влаштовані мікросхеми-паливоміри", size=9.5, color=MUTED))

    f.append(fitbox(60, 280, 700, 46,
                    "Коротко довіряємо лічбі заряду; напругою (на краях кривої та у спокої)\n"
                    "повільно підправляємо її дрейф — м'яко, щоб відсотки не стрибали.",
                    size=10.5, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=8))
    render(os.path.join(IMG, "fusion.svg"), W, H, *f)


# ── 5. Перекалібрування на краях: краї круті, середина пласка ───────────────
def fig_recal():
    W, H = 820, 400
    f = [text(W / 2, 28, "Перекалібрування на краях: повний заряд = 100%, відсічка = 0%", size=15.5, bold=True)]
    L, R, T, B = 110, 720, 70, 300

    def px(s):  return L + s * (R - L)
    f.append(line(L, B, R, B, color=INK, sw=1.6))
    f.append(line(L, B, L, T, color=INK, sw=1.6))
    f.append(text(L - 10, T + 4, "V", size=11, color=INK, bold=True, anchor="end"))
    for frac, lab in [(0, "0%"), (.5, "50%"), (1, "100%")]:
        x = px(frac)
        f.append(line(x, B, x, B + 5, color=INK, sw=1))
        f.append(text(x, B + 18, lab, size=9.5, color=MUTED))
    f.append(text((L + R) / 2, B + 36, "SoC", size=11, color=INK))

    # крива з крутими краями і пласкою серединою
    cur = [(0, B - 14), (.08, B - 96), (.18, B - 128), (.82, B - 150), (.92, B - 182), (1, B - 226)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' %
             (" ".join("%.1f,%.1f" % (px(s), y) for s, y in cur), INK))

    # підсвітка країв (надійні) і середини (ненадійна)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.12"/>'
             % (px(0), T, px(.18) - px(0), B - T, FIELD))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.12"/>'
             % (px(.82), T, px(1) - px(.82), B - T, FIELD))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10"/>'
             % (px(.18), T, px(.82) - px(.18), B - T, "#caa24a"))
    f.append(text((px(.18) + px(.82)) / 2, T + 22, "пласко: напрузі не вірити", size=10, color="#caa24a", bold=True))

    # якорі
    f.append(text(px(.04), B - 240, "повний\nзаряд\n= 100%".replace("\n", " "), size=9, color=FIELD, bold=True, anchor="start"))
    f.append(circle(px(1), cur[-1][1], 5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(circle(px(0), cur[0][1], 5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(px(.0) + 8, cur[0][1] - 8, "відсічка = 0%", size=9, color=FIELD, bold=True, anchor="start"))

    f.append(fitbox(70, 346, 680, 46,
                    "На краях напруга крута й надійна — там «прибивають» SoC до відомих точок.\n"
                    "Кожен повний заряд скидає дрейф; у пласкій середині покладаються на лічбу.",
                    size=10, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=8))
    render(os.path.join(IMG, "recal.svg"), W, H, *f)


# ── 6. Який метод обрати + три залізні правила ──────────────────────────────
def fig_decision():
    W, H = 820, 380
    f = [text(W / 2, 28, "Який метод обрати — і три залізні правила", size=16, bold=True)]
    cards = [
        (55,  POS,   "Похила Li-ion,",  "треба дешево",       "напруга у спокої",      "проста оцінка, без чипа"),
        (305, "#caa24a", "Пласка LFP /", "потрібна точність", "кулонометрія + напруга", "паливомір (fuel gauge)"),
        (555, FIELD, "Складна система,", "телеметрія",        "паливомір з моделлю",   "+ здоров'я, прогноз часу"),
    ]
    for x, col, t1, t2, ans, sub in cards:
        f.append(rect(x, 60, 210, 130, fill=BG, stroke=col, sw=2, rx=12))
        f.append(text(x + 105, 86, t1, size=10.5, color=INK, bold=True))
        f.append(text(x + 105, 103, t2, size=10.5, color=INK, bold=True))
        f.append(line(x + 18, 120, x + 192, 120, color="#e4e4e4", sw=1))
        f.append(text(x + 105, 146, ans, size=10.5, color=col, bold=True))
        f.append(text(x + 105, 170, sub, size=9.5, color=MUTED))

    # три правила
    f.append(rect(55, 214, 710, 130, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(410, 240, "Три залізні правила паливоміра", size=12, color=FIELD, bold=True))
    rules = [
        "1) перекалібровуй на повному заряді (і на відсічці) — там напруга надійна;",
        "2) не вір останнім ~10% — там найбільша невизначеність;",
        "3) врахуй, що ємність тане з віком — інакше «100%» старої батареї бреше.",
    ]
    for i, r in enumerate(rules):
        f.append(text(410, 268 + i * 24, r, size=10, color=INK))
    render(os.path.join(IMG, "decision.svg"), W, H, *f)


# ── 7. Конвеєр кулонометрії у прошивці (для вставки proj-) ───────────────────
def fig_pipeline():
    W, H = 860, 380
    f = [text(W / 2, 28, "Лічба заряду в прошивці: конвеєр і дві підпорки проти дрейфу", size=15, bold=True)]

    # головний конвеєр
    stages = [
        (40,  "АЦП струму",     "read_adc()"),
        (210, "− зсув нуля",    "I − I_zero"),
        (380, "інтеграл ×Δt",   "Q += I·Δt"),
        (550, "накопичувач Q",  "А·с"),
        (700, "SoC",            "Q / Ємність"),
    ]
    y0 = 86
    for i, (x, t1, t2) in enumerate(stages):
        col = NEG if i == 4 else INK
        f.append(rect(x, y0, 130, 64, fill=BG, stroke=col, sw=2, rx=8))
        f.append(text(x + 65, y0 + 26, t1, size=10.5, color=col, bold=True))
        f.append(text(x + 65, y0 + 47, t2, size=9.5, color=MUTED))
        if i < len(stages) - 1:
            f.append(arrow(x + 130, y0 + 32, stages[i + 1][0], y0 + 32, color=INK, sw=1.8))

    # підпорка 1: якорі (повний/порожній) → скидають Q
    f.append(rect(120, 210, 300, 66, fill="#eef6ef", stroke=FIELD, sw=2, rx=10))
    f.append(text(270, 234, "Якорі на відомих точках", size=11, color=FIELD, bold=True))
    f.append(text(270, 256, "повний → Q=ємність, SoC=100%; відсічка → Q=0", size=9, color=INK))
    f.append(arrow(270, 210, 270, 152, color=FIELD, sw=2))

    # підпорка 2: напруга у спокої → м'яко тягне Q
    f.append(rect(470, 210, 300, 66, fill="#fdecea", stroke=POS, sw=2, rx=10))
    f.append(text(620, 234, "Напруга у спокої", size=11, color=POS, bold=True))
    f.append(text(620, 256, "Q += k·(SoC_v·ємність − Q), м'яка корекція", size=9, color=INK))
    f.append(arrow(620, 210, 620, 152, color=POS, sw=2))

    f.append(fitbox(110, 300, 660, 46,
                    "Без віднімання зсуву АЦП інтеграл повзе навіть без струму; без якорів дрейф росте вічно.\n"
                    "Ємність — вивчена (тане з віком), не паспортна.",
                    size=10, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=8))
    render(os.path.join(IMG, "pipeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_problem()
    fig_voltage()
    fig_coulomb()
    fig_fusion()
    fig_recal()
    fig_decision()
    fig_pipeline()
    print("OK: 7 SVG -> ./img/")
