# -*- coding: utf-8 -*-
"""Фігури до теми «Топології лінійних регуляторів: NPN, PNP, PMOS».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

SOFT_G = "#e8f6ed"   # м'яке зелене тло рамки-висновку
SOFT_R = "#fdecea"   # м'яке червоне тло
GRID   = "#c9d2dc"


def poly(points, color=INK, sw=2.0, dash=None):
    """Ламана/крива як <path> (svgkit не має path-хелпера)."""
    d = "M %.2f %.2f " % points[0] + " ".join("L %.2f %.2f" % p for p in points[1:])
    ds = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linecap="round" stroke-linejoin="round"%s/>' % (d, color, sw, ds))


# ── 1. Три топології: куди дивиться керування й куди тече струм керування ─────
def fig_topologies():
    W, H = 1020, 450
    f = [text(W / 2, 30, "Одна петля, три прохідні елементи — розвилка в тому, до чого прив'язане керування",
              size=16, bold=True)]

    panels = [
        dict(px=180, title="NPN — повторювач", sub="керування прив'язане до ВИХОДУ",
             dev="NPN", top="колектор", bot="емітер",
             drive=["драйвер тягне", "ВГОРУ, вище Vвих"],
             note=["струм бази виходить емітером", "— у навантаження, не в землю"], nfill=SOFT_G,
             drop=["dropout = Vбе + Vнас", "≈ 1.1 В (2 В у дарлінгтона)"]),
        dict(px=510, title="PNP — інверсний", sub="керування прив'язане до ЗЕМЛІ",
             dev="PNP", top="емітер", bot="колектор",
             drive=["драйвер тягне", "ВНИЗ, до землі"],
             note=["струм бази стікає в землю", "Iзем ≈ Iвих / β"], nfill=SOFT_R,
             drop=["dropout = Vке(нас)", "≈ 0.3…0.5 В, без підлоги"]),
        dict(px=840, title="PMOS — інверсний", sub="керування прив'язане до ЗЕМЛІ",
             dev="PMOS", top="витік", bot="стік",
             drive=["драйвер тягне", "ВНИЗ, до землі"],
             note=["затвор постійного струму не бере", "Iзем ≈ лише вузол керування"], nfill=SOFT_G,
             drop=["dropout = Iвих · Rси(відкр)", "підлоги немає взагалі"]),
    ]

    for p in panels:
        px = p["px"]
        f.append(text(px, 62, p["title"], size=14, bold=True))
        f.append(text(px, 82, p["sub"], size=10, color=MUTED))

        # шина входу
        f.append(line(px - 130, 108, px + 130, 108, color=POS, sw=2.4))
        f.append(text(px - 138, 112, "Vвх", size=11, color=POS, anchor="end", bold=True))
        f.append(line(px, 108, px, 140, sw=1.8))
        f.append(text(px + 10, 130, p["top"], size=10, color=MUTED, anchor="start"))

        # прохідний елемент
        f.append(rect(px - 58, 140, 116, 62, fill="#eef2f7", stroke="#7f93a8", sw=2, rx=7))
        f.append(text(px, 178, p["dev"], size=17, bold=True))

        # керування збоку
        f.append(mtext(px - 92, 150, p["drive"], size=10, color=NEG))
        f.append(arrow(px - 126, 171, px - 62, 171, color=NEG, sw=1.8))

        # шина виходу
        f.append(line(px, 202, px, 250, sw=1.8))
        f.append(text(px + 10, 224, p["bot"], size=10, color=MUTED, anchor="start"))
        f.append(line(px - 130, 250, px + 130, 250, color=FIELD, sw=2.4))
        f.append(text(px + 138, 254, "Vвих", size=11, color=FIELD, anchor="start", bold=True))

        # наслідок: куди дівається струм керування
        f.append(textbox(px, 320, p["note"], size=11, fill=p["nfill"], stroke=MUTED, min_w=232)[0])
        f.append(textbox(px, 392, p["drop"], size=11, fill=FILL, stroke=MUTED, min_w=232)[0])

    return render(os.path.join(IMG, "topologies.svg"), W, H, *f)


# ── 2. Dropout проти струму: підлога чи опір ──────────────────────────────────
def fig_dropout():
    W, H = 880, 420
    X0, X1 = 90.0, 620.0      # 0 … 1 А
    Y0, Y1 = 350.0, 80.0      # 0 … 2.2 В

    def X(i):
        return X0 + (X1 - X0) * i

    def Y(v):
        return Y0 + (Y1 - Y0) * (v / 2.2)

    f = [text(W / 2, 30, "Dropout проти струму: у повторювача — підлога, в інверсних — опір",
              size=16, bold=True)]
    f.append(text(X0, 62, "падіння на регуляторі (dropout), В", size=11, color=MUTED, anchor="start"))

    # осі
    f.append(line(X0, 75, X0, 355, color=MUTED, sw=1.5))
    f.append(line(85, Y0, 625, Y0, color=MUTED, sw=1.5))
    for v in (0, 0.5, 1.0, 1.5, 2.0):
        f.append(line(X0 - 5, Y(v), X0, Y(v), color=MUTED, sw=1.2))
        f.append(text(82, Y(v) + 4, ("%g" % v), size=11, color=MUTED, anchor="end"))
    for i in (0, 0.25, 0.5, 0.75, 1.0):
        f.append(line(X(i), Y0, X(i), Y0 + 5, color=MUTED, sw=1.2))
        f.append(text(X(i), 372, ("%g" % i), size=11, color=MUTED))
    f.append(text((X0 + X1) / 2, 400, "струм навантаження Iвих, А", size=11, color=MUTED))

    N = 60
    # 78xx: дарлінгтон — рівна підлога 2 В
    f.append(poly([(X(k / N), Y(2.0)) for k in range(N + 1)], color=POS, sw=2.6))
    f.append(text(632, 100, "78xx: дарлінгтон, 2 В", size=12, color=POS, anchor="start"))
    # LM1117-клас: один NPN — підлога 1.05 В, ледь повзе
    f.append(poly([(X(k / N), Y(1.05 + 0.15 * (k / N))) for k in range(N + 1)], color="#e07b39", sw=2.6))
    f.append(text(632, 199, "LM1117-клас: один NPN", size=12, color="#e07b39", anchor="start"))
    # PNP: Vке(нас) — росте зі струмом, підлоги нема
    f.append(poly([(X(k / N), Y(0.5 * (k / N) ** 1.15)) for k in range(N + 1)], color=NEG, sw=2.6))
    f.append(text(632, 284, "PNP: Vке(нас)", size=12, color=NEG, anchor="start"))
    # PMOS: чистий опір
    f.append(poly([(X(k / N), Y(0.25 * (k / N))) for k in range(N + 1)], color=FIELD, sw=2.6))
    f.append(text(632, 330, "PMOS: Iвих · Rси", size=12, color=FIELD, anchor="start"))

    # легке навантаження — підлога нікуди не дівається
    f.append(line(X(0.05), 90, X(0.05), Y0, color=MUTED, sw=1.2, dash="5 4"))
    f.append(textbox(250, 150, ["за легкого струму підлога NPN", "нікуди не дівається, а в PNP",
                                "й PMOS dropout сходить до нуля"], size=11, fill=FILL, stroke=MUTED)[0])
    f.append(arrow(143, 150, 122, 150, sw=1.6))

    return render(os.path.join(IMG, "dropout-vs-current.svg"), W, H, *f)


# ── 3. Струм у землю: куди подівся струм керування ────────────────────────────
def fig_ground():
    W, H = 800, 420
    X0, X1 = 95.0, 620.0      # 0 … 1 А
    Y0, Y1 = 350.0, 80.0      # 0 … 60 мА

    def X(i):
        return X0 + (X1 - X0) * i

    def Y(ma):
        return Y0 + (Y1 - Y0) * (ma / 60.0)

    f = [text(W / 2, 30, "Струм, що йде в землю: ціна за спосіб керувати прохідним елементом",
              size=16, bold=True)]
    f.append(text(X0, 62, "власний струм у землю Iзем, мА", size=11, color=MUTED, anchor="start"))

    f.append(line(X0, 75, X0, 355, color=MUTED, sw=1.5))
    f.append(line(90, Y0, 625, Y0, color=MUTED, sw=1.5))
    for ma in (0, 10, 20, 30, 40, 50, 60):
        f.append(line(X0 - 5, Y(ma), X0, Y(ma), color=MUTED, sw=1.2))
        f.append(text(87, Y(ma) + 4, str(ma), size=11, color=MUTED, anchor="end"))
    for i in (0, 0.25, 0.5, 0.75, 1.0):
        f.append(line(X(i), Y0, X(i), Y0 + 5, color=MUTED, sw=1.2))
        f.append(text(X(i), 372, ("%g" % i), size=11, color=MUTED))
    f.append(text((X0 + X1) / 2, 400, "струм навантаження Iвих, А", size=11, color=MUTED))

    N = 40
    # PNP: Iq + Iвих/β, β ≈ 20
    f.append(poly([(X(k / N), Y(3 + 50 * (k / N))) for k in range(N + 1)], color=NEG, sw=2.6))
    f.append(text(632, 108, "PNP: Iзем ≈ Iвих / β", size=12, color=NEG, anchor="start"))
    # NPN-повторювач: струм бази йде у вихід, у землю — лише вузол керування
    f.append(poly([(X(k / N), Y(5)) for k in range(N + 1)], color=POS, sw=2.6))
    f.append(text(632, 323, "NPN: ~5 мА, стало", size=12, color=POS, anchor="start"))
    # PMOS: затвор струму не бере
    f.append(poly([(X(k / N), Y(0.05)) for k in range(N + 1)], color=FIELD, sw=3.0))
    f.append(text(632, 355, "PMOS: ~50 мкА", size=12, color=FIELD, anchor="start"))

    f.append(textbox(300, 150, ["у dropout транзистор насичується,",
                                "β падає — струм бази стрибає ще вище"],
                     size=11, fill=SOFT_R, stroke=MUTED)[0])
    f.append(arrow(432, 152, 553, 139, sw=1.6))

    return render(os.path.join(IMG, "ground-current.svg"), W, H, *f)


# ── 4. Вихідний полюс: повторювач ділить опір вузла на Vвих/Vт ────────────────
def fig_pole():
    W, H = 980, 400
    FX0 = 200.0
    DEC = 116.67   # px на декаду

    def F(f_hz):
        return FX0 + math.log10(f_hz) * DEC

    f = [text(W / 2, 30, "Де опиняється вихідний полюс: повторювач відсуває його на ті самі 2.1 декади",
              size=16, bold=True)]

    # вісь частоти
    f.append(line(FX0, 320, 935, 320, color=MUTED, sw=1.5))
    for hz, lbl in ((1, "1 Гц"), (10, "10 Гц"), (100, "100 Гц"), (1e3, "1 кГц"),
                    (1e4, "10 кГц"), (1e5, "100 кГц"), (1e6, "1 МГц")):
        f.append(line(F(hz), 320, F(hz), 328, color=MUTED, sw=1.2))
        f.append(text(F(hz), 344, lbl, size=11, color=MUTED))

    # ряд «інверсний»: Zвих ≈ Rнав = Vвих/Iвих
    f.append(textbox(102, 170, ["інверсний", "PNP / PMOS"], size=12, fill=SOFT_R, stroke=MUTED)[0])
    f.append(line(F(4.8), 170, F(4800), 170, color=NEG, sw=2.4))
    for hz, lbl in ((4.8, "1 мА → 4.8 Гц"), (4800, "1 А → 4.8 кГц")):
        f.append(circle(F(hz), 170, 6, fill=NEG, stroke=NEG))
        f.append(text(F(hz), 152, lbl, size=11, color=NEG))

    # ряд «повторювач»: Zвих ≈ 1/gm = Vт/Iвих
    f.append(textbox(102, 250, ["повторювач", "NPN / NMOS"], size=12, fill=SOFT_G, stroke=MUTED)[0])
    f.append(line(F(612), 250, F(612000), 250, color=FIELD, sw=2.4))
    for hz, lbl in ((612, "1 мА → 612 Гц"), (612000, "1 А → 612 кГц")):
        f.append(circle(F(hz), 250, 6, fill=FIELD, stroke=FIELD))
        f.append(text(F(hz), 272, lbl, size=11, color=FIELD))

    # той самий зсув за будь-якого струму
    f.append(arrow(F(4.8), 180, F(612), 240, color=MUTED, sw=1.6))
    f.append(arrow(F(4800), 180, F(612000), 240, color=MUTED, sw=1.6))

    # де петля перетинає одиничне підсилення
    f.append(line(F(3e4), 105, F(3e4), 305, color=POS, sw=1.4, dash="6 4"))
    f.append(text(F(3e4), 96, "петля перетинає одиницю", size=11, color=POS))

    f.append(text(W / 2, 374, "зсув однаковий за будь-якого струму:  Vвих / Vт = 3.3 / 0.026 ≈ 127  (≈ 2.1 декади)",
                  size=13, bold=True))

    return render(os.path.join(IMG, "output-pole.svg"), W, H, *f)


# ══ Фігури до вставки «Прохідний елемент, якого не обирали» (hist) ════════════

EPI  = "#e8f0fb"   # n-епітаксія
SUB  = "#e4e7ea"   # p-підкладка
PDIF = "#f8e3c0"   # p-дифузія
NDIF = "#cfe0f7"   # n+-дифузія
BASE = "#f6b8ae"   # база — те, крізь що мусять пройти носії


def fig_vertical_vs_lateral():
    """Чому в 1969-му прохідним міг бути лише NPN: чим задано ширину бази."""
    W, H = 1060, 575
    f = [text(W / 2, 34, "Ширину бази задають дві РІЗНІ машини — і точність у них різна на порядки",
              size=17, bold=True),
         text(W / 2, 60, "Червоним — база: те, крізь що носії мусять пройти. Обидва прилади зроблено тим самим процесом, на тому самому кристалі.",
              size=12, color=MUTED)]

    # ── Ряд 1: вертикальний NPN ───────────────────────────────────────────────
    f.append(rect(60, 150, 500, 90, fill=EPI, stroke=LINE, sw=1.5, rx=3))
    f.append(rect(60, 214, 500, 26, fill=SUB, stroke=LINE, sw=1.2, rx=0))
    f.append(text(68, 232, "p-підкладка", size=11, color=MUTED, anchor="start"))
    f.append(text(68, 205, "n-епі", size=11, color=MUTED, anchor="start"))

    f.append(rect(140, 150, 260, 36, fill=PDIF, stroke=LINE, sw=1.2, rx=2))     # p-база
    f.append(rect(190, 178, 140, 8, fill=BASE, stroke=POS, sw=1.2, rx=0))       # Wб
    f.append(rect(190, 150, 140, 28, fill=NDIF, stroke=LINE, sw=1.2, rx=2))     # n+ емітер
    f.append(rect(440, 150, 70, 64, fill=NDIF, stroke=LINE, sw=1.2, rx=2))      # n+ до колектора
    f.append(text(365, 171, "p-база", size=11))
    f.append(text(260, 168, "n+ емітер", size=11))
    f.append(text(475, 168, "n+", size=11))

    for cx, ln in ((260, "Е"), (365, "Б"), (475, "К")):
        f.append(rect(cx - 10, 142, 20, 8, fill=INK, stroke=INK, sw=0.8, rx=1))
        f.append(text(cx, 132, ln, size=13, bold=True))

    f.append(text(605, 168, "Вертикальний NPN", size=15, bold=True, anchor="start"))
    f.append(fitbox(600, 178, 430, 62,
                    ["Базу задає РІЗНИЦЯ ГЛИБИН двох дифузій,",
                     "а глибину тримає час і температура в печі:",
                     "Wб — частки мікрона.   β ≈ 200…500."], size=13))

    # ── Ряд 2: бічний PNP ─────────────────────────────────────────────────────
    f.append(rect(60, 330, 500, 90, fill=EPI, stroke=LINE, sw=1.5, rx=3))
    f.append(rect(60, 394, 500, 26, fill=SUB, stroke=LINE, sw=1.2, rx=0))
    f.append(text(68, 412, "p-підкладка", size=11, color=MUTED, anchor="start"))
    f.append(text(68, 385, "n-епі — і воно ж БАЗА", size=11, color=MUTED, anchor="start"))

    f.append(rect(250, 330, 80, 36, fill=BASE, stroke=POS, sw=1.2, rx=0))       # Wб — зазор
    f.append(rect(170, 330, 80, 36, fill=PDIF, stroke=LINE, sw=1.2, rx=2))      # p-емітер
    f.append(rect(330, 330, 120, 36, fill=PDIF, stroke=LINE, sw=1.2, rx=2))     # p-колектор
    f.append(rect(480, 330, 50, 28, fill=NDIF, stroke=LINE, sw=1.2, rx=2))      # n+ до бази
    f.append(text(210, 352, "p", size=11))
    f.append(text(390, 352, "p-колектор", size=11))
    f.append(text(505, 348, "n+", size=10))

    for cx, ln in ((210, "Е"), (390, "К"), (505, "Б")):
        f.append(rect(cx - 10, 322, 20, 8, fill=INK, stroke=INK, sw=0.8, rx=1))
        f.append(text(cx, 312, ln, size=13, bold=True))

    f.append(text(605, 348, "Бічний PNP", size=15, bold=True, anchor="start"))
    f.append(fitbox(600, 358, 430, 62,
                    ["Базу задає ЗАЗОР МІЖ ВІКНАМИ МАСКИ,",
                     "а зазор тримає роздільність фотолітографії:",
                     "у 1969-му — десятки мікронів.   β ≈ 10…50."], size=13))

    f.append(fitbox(60, 460, 970, 84,
                    ["Піч тримала глибину дифузії з точністю до часток мікрона; фотолітографія тих років різала вікна десятками мікронів.",
                     "Тож база бічного PNP виходила на один-два порядки ширша за базу вертикального NPN — а з нею падало і β, і швидкодія.",
                     "Прохідний елемент 1969 року не обирали: на кристалі був рівно один транзистор, здатний тягнути ампер."],
                    size=14, fill=SOFT_G, stroke=FIELD))

    return render(os.path.join(IMG, "pass-vertical-vs-lateral.svg"), W, H, *f)


def fig_pass_eras():
    """Топологію щоразу затискали з двох боків: технологія згори, вхід знизу."""
    W, H = 1300, 514
    f = [text(W / 2, 34, "Черга до прохідного елемента: жоден перехід не почався з нової ідеї",
              size=17, bold=True),
         text(W / 2, 60, "Згори тисне те, що кремній узагалі вміє зробити; знизу — те, що вхід готовий віддати. Топологія — це слід між двома тисками.",
              size=12, color=MUTED)]

    cols = [
        dict(era="1969 → 1976", chip="LM109 · 78xx · LM317",
             tech=["Ампер на кристалі тягне",
                   "лише вертикальний NPN.",
                   "У бічного PNP база",
                   "вдесятеро ширша, β 10…50."],
             pas=["NPN-повторювач", "(дарлінгтон)",
                  "dropout ≈ 2 В — і хоч як", "міняй струм, він стоїть"],
             dem=["Трансформатор, міст,",
                  "електроліт: 8–12 В на 5 В.",
                  "Запасу 3–7 В — за dropout",
                  "ніхто не платить."]),
        dict(era="1980-ті", chip="LM2930 · LM2940",
             tech=["Бічний PNP підріс і нарешті",
                   "тягне ампер — ціною площі.",
                   "β усе одно лишилося",
                   "в межах 10…50."],
             pas=["PNP, інверсний",
                  "dropout ≈ 0.5 В на 1 А,",
                  "зате струм у землю", "росте з навантаженням"],
             dem=["Машина. Стартер валить",
                  "бортову мережу до 6 В",
                  "і нижче (ISO 16750-2).",
                  "5 + 2 = 7 В не влазить."]),
        dict(era="1990-ті", chip="S-812-клас · MIC5205",
             tech=["CMOS: p-канал — рівно-",
                   "правний прилад. Літографія",
                   "дійшла до часток мікрона —",
                   "бічне більше не вирок."],
             pas=["PMOS, інверсний",
                  "Iспок ≈ 1 мкА;",
                  "dropout = Iвих · Rси(відкр)", "— підлоги немає"],
             dem=["Літієва банка (Sony, 1991):",
                  "4.2 → 3.0 В на 3.3 В.",
                  "Кожні 100 мВ dropout —",
                  "викинута ємність."]),
        dict(era="2000-ні →", chip="LTC3026-клас",
             tech=["Помпа й бустер на кристалі",
                   "коштують копійки —",
                   "затвор можна живити", "вище за вхід."],
             pas=["NMOS-повторювач",
                  "+ помпа на затвор",
                  "dropout ≈ 0.1 В на 1.5 А", "і полюс далеко"],
             dem=["Ампери від сусідньої шини",
                  "з різкими кидками.",
                  "Треба разом і малий",
                  "dropout, і стійкість петлі."]),
    ]

    f.append(text(32, 148, "ТЕХНОЛОГІЯ дала", size=12, bold=True, color=MUTED, anchor="start"))
    f.append(text(32, 248, "ПРОХІДНИЙ", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(text(32, 264, "ЕЛЕМЕНТ", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(text(32, 354, "ВХІД забрав", size=12, bold=True, color=MUTED, anchor="start"))

    for i, c in enumerate(cols):
        x = 190 + i * 275
        cx = x + 125
        f.append(text(cx, 88, c["era"], size=15, bold=True))
        f.append(text(cx, 104, c["chip"], size=11, color=MUTED))
        f.append(fitbox(x, 112, 250, 78, c["tech"], size=12))
        f.append(arrow(cx, 194, cx, 210, color=MUTED, sw=1.6))
        f.append(fitbox(x, 214, 250, 72, c["pas"], size=12, fill=SOFT_G, stroke=FIELD, sw=2.0))
        f.append(arrow(cx, 306, cx, 290, color=MUTED, sw=1.6))
        f.append(fitbox(x, 310, 250, 78, c["dem"], size=12))

    f.append(fitbox(30, 418, 1240, 76,
                    ["Кожну з цих чотирьох схем можна було намалювати ще в 1955-му — це підручникові вмикання, жодна не чекала на ідею.",
                     "Топологія мінялася рівно тоді, коли збігалися дві умови: технологія навчилася робити потрібний транзистор,",
                     "а вхід почав виставляти рахунок за старий. Спершу рахунок, потім кремній — і аж тоді нова топологія."],
                    size=14, fill=SOFT_G, stroke=FIELD))

    return render(os.path.join(IMG, "pass-element-eras.svg"), W, H, *f)


# ══ Фігури до вставки «NMOS-стабілізатор із шиною зміщення» (comp) ════════════

def gnd(x, y, color=MUTED):
    """Символ землі: вивід і три риски, що звужуються."""
    f = [line(x, y, x, y + 9, color=color, sw=1.6)]
    for k, half in enumerate((11, 7, 3)):
        f.append(line(x - half, y + 9 + k * 5, x + half, y + 9 + k * 5, color=color, sw=1.6))
    return "".join(f)


# ── comp-1. Два входи класу: м'яз і мозок ─────────────────────────────────────
def fig_nmos_block():
    W, H = 1080, 660
    f = [text(W / 2, 30, "Два входи одного чипа — і лише один із них несе струм навантаження",
              size=16, bold=True)]

    # дві шини живлення: фізично роз'єднані
    f.append(line(90, 95, 530, 95, color=NEG, sw=3.0))
    f.append(text(90, 82, "Vзм — шина зміщення, 2.7…5.5 В", size=12, color=NEG,
                  anchor="start", bold=True))
    f.append(line(650, 95, 1000, 95, color=POS, sw=3.0))
    f.append(text(650, 82, "Vвх — від 1.1 В", size=12, color=POS, anchor="start", bold=True))

    # два стовпці
    f.append(rect(90, 145, 440, 350, fill="#eef3fd", stroke=NEG, sw=1.6, rx=9))
    f.append(rect(650, 145, 370, 350, fill="#fdeeec", stroke=POS, sw=1.6, rx=9))
    f.append(text(305, 172, "МОЗОК — усе, що думає", size=13, bold=True, color=NEG))
    f.append(text(835, 172, "М'ЯЗ — усе, що гріється", size=13, bold=True, color=POS))

    # Vзм годує все, що всередині мозку
    for x in (160, 310, 460):
        f.append(arrow(x, 100, x, 143, color=NEG, sw=1.8))

    # нагляд — просто під шиною, куди приходить живлення
    f.append(textbox(310, 195, ["UVLO · обмеження струму · тепловий захист · PG"],
                     size=11, fill="#ffffff", stroke=MUTED)[0])

    # ланцюжок: м'який старт → еталон → підсилювач похибки → драйвер → затвор
    f.append(textbox(175, 265, ["м'який старт", "Cм.ст задає нахил"],
                     size=11, fill="#ffffff", stroke=MUTED)[0])
    f.append(arrow(175, 290, 175, 358, color=MUTED, sw=1.6))
    f.append(textbox(175, 390, ["еталон 0.8 В"], size=11, fill="#ffffff", stroke=MUTED)[0])
    f.append(arrow(221, 390, 327, 390, color=MUTED, sw=1.6))
    f.append(textbox(370, 390, ["підсилювач", "похибки"], size=11, fill="#ffffff", stroke=MUTED)[0])
    f.append(arrow(370, 365, 370, 305, color=MUTED, sw=1.6))
    f.append(textbox(370, 280, ["драйвер затвора"], size=11, fill="#ffffff", stroke=MUTED)[0])

    # затвор — єдина ниточка з мозку в м'яз
    f.append(arrow(423, 280, 753, 280, color=INK, sw=2.0))
    f.append(text(690, 268, "затвор", size=11, color=MUTED))

    # прохідний елемент: Vвх заходить лише сюди — обхід праворуч, повз заголовок "М'ЯЗ"
    f.append(line(950, 100, 950, 222, color=POS, sw=2.2))
    f.append(line(950, 222, 820, 222, color=POS, sw=2.2))
    f.append(arrow(820, 222, 820, 238, color=POS, sw=2.2))
    f.append(text(962, 165, "стік", size=11, color=MUTED, anchor="start"))
    f.append(rect(755, 240, 130, 85, fill="#ffffff", stroke=POS, sw=2.0, rx=7))
    f.append(text(820, 275, "NMOS", size=16, bold=True))
    f.append(text(820, 300, "прохідний", size=11, color=MUTED))
    f.append(line(820, 325, 820, 385, sw=1.8))
    f.append(text(832, 355, "витік", size=11, color=MUTED, anchor="start"))

    # вихід
    f.append(line(820, 385, 1010, 385, color=FIELD, sw=3.0))
    f.append(text(975, 373, "Vвих", size=12, color=FIELD, bold=True))

    # дільник на виході й дорога зворотного зв'язку назад у мозок
    f.append(line(900, 385, 900, 402, color=MUTED, sw=1.6))
    f.append(rect(890, 402, 20, 34, fill="#ffffff", stroke=MUTED, sw=1.4, rx=3))
    f.append(text(916, 424, "R1", size=10, color=MUTED, anchor="start"))
    f.append(line(900, 436, 900, 462, color=MUTED, sw=1.6))
    f.append(rect(890, 462, 20, 34, fill="#ffffff", stroke=MUTED, sw=1.4, rx=3))
    f.append(text(916, 484, "R2", size=10, color=MUTED, anchor="start"))
    f.append(line(900, 496, 900, 512, color=MUTED, sw=1.6))
    f.append(gnd(900, 512))
    f.append(line(900, 449, 700, 449, color=MUTED, sw=1.6))
    f.append(line(700, 449, 700, 545, color=MUTED, sw=1.6))
    f.append(line(700, 545, 370, 545, color=MUTED, sw=1.6))
    f.append(arrow(370, 545, 370, 417, color=MUTED, sw=1.6))
    f.append(text(535, 535, "FB — відвід дільника на виході", size=11, color=MUTED))

    f.append(textbox(555, 610,
                     ["Vвх заходить у ЄДИНЕ місце — у стік. Усе інше живиться від Vзм.",
                      "Саме тому Vвх вільний сісти до 1.1 В: еталонові й підсилювачеві вже не треба з нього жити."],
                     size=12, fill=SOFT_G, stroke=MUTED, min_w=920)[0])

    return render(os.path.join(IMG, "nmos-block.svg"), W, H, *f)


# ── comp-2. Два dropout під одним словом ──────────────────────────────────────
def fig_two_dropouts():
    W, H = 1020, 500
    Y0 = 390.0          # рівень Vвих
    PX = 150.0          # px на вольт

    f = [text(W / 2, 30, "Одне слово «dropout» — дві різні вимоги до двох різних шин",
              size=16, bold=True)]

    # спільна підлога — вихід
    f.append(line(90, Y0, 620, Y0, color=FIELD, sw=2.6))
    f.append(text(84, Y0 + 4, "Vвих = 1.0 В", size=12, color=FIELD, anchor="end", bold=True))

    # запас на вхідній шині — падіння на каналі
    hin = 0.115 * PX
    f.append(rect(150, Y0 - hin, 120, hin, fill="#f7c8c2", stroke=POS, sw=1.4, rx=2))
    f.append(line(130, Y0 - hin, 290, Y0 - hin, color=POS, sw=2.6))
    f.append(text(210, Y0 - hin - 15, "Vвх ≥ Vвих + 0.115 В", size=12, color=POS, bold=True))
    f.append(text(210, Y0 - hin - 33, "= Iвих · Rси(відкр) — падіння на каналі",
                  size=11, color=MUTED))
    f.append(text(300, Y0 - hin + 5, "115 мВ", size=11, color=POS, anchor="start", bold=True))

    # запас на шині зміщення — напруга, щоб тримати затвор
    hb = 1.62 * PX
    f.append(rect(430, Y0 - hb, 120, hb, fill="#cfdcf7", stroke=NEG, sw=1.4, rx=2))
    f.append(line(410, Y0 - hb, 570, Y0 - hb, color=NEG, sw=2.6))
    f.append(text(490, Y0 - hb - 15, "Vзм ≥ Vвих + 1.62 В", size=12, color=NEG, bold=True))
    f.append(text(490, Y0 - hb - 33, "= поріг + надлишок затвора + запас драйвера",
                  size=11, color=MUTED))
    f.append(text(490, 270, "1.62 В", size=15, color=NEG, bold=True))

    f.append(textbox(350, 250, ["той самий чип,", "той самий струм,", "×14 різниці"],
                     size=11, fill=FILL, stroke=MUTED)[0])

    # праворуч — чому запас на Vзм не стала
    f.append(line(660, 70, 660, 460, color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(840, 100, "Чому запас на Vзм росте зі струмом", size=13, bold=True))
    f.append(mtext(840, 126, ["більше струму → ширше треба відкрити",
                              "канал → вищий надлишок затвора →",
                              "вища шина зміщення"], size=11, color=MUTED))

    f.append(rect(700, 180, 280, 170, fill=FILL, stroke=MUTED, sw=1.4))
    f.append(text(790, 208, "Iвих", size=12, bold=True, anchor="end"))
    f.append(text(950, 208, "Vзм − Vвих", size=12, bold=True, anchor="end"))
    f.append(line(715, 220, 965, 220, color=MUTED, sw=1.2))
    for k, (a, b) in enumerate((("100 мА", "1.16 В"), ("500 мА", "1.27 В"),
                                ("1 А", "1.35 В"), ("3 А", "1.62 В"))):
        yy = 246 + k * 28
        f.append(text(790, yy, a, size=12, anchor="end"))
        f.append(text(950, yy, b, size=12, anchor="end", color=NEG, bold=(k == 3)))

    f.append(textbox(840, 405, ["30× струму коштують лише +0.46 В:",
                                "надлишок затвора росте як √Iвих"],
                     size=11, fill=SOFT_G, stroke=MUTED, min_w=280)[0])

    return render(os.path.join(IMG, "two-dropouts.svg"), W, H, *f)


# ── comp-3. Порядок увімкнення й доля м'якого старту ──────────────────────────
def fig_bias_sequence():
    W, H = 1240, 690
    X0, X1 = 200.0, 900.0
    AMP = 26.0

    def T(t):
        return X0 + (X1 - X0) * t

    def panel(ytop, title, tcolor, rows, note, nfill, arrow_to):
        g = [text(320, ytop - 8, title, size=13, bold=True, color=tcolor)]
        g.append(rect(60, ytop, 850, 230, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
        for k, (lbl, color, pts, amp) in enumerate(rows):
            yb = ytop + 40 + k * 38
            g.append(text(190, yb + 4, lbl, size=11, color=color, anchor="end", bold=True))
            g.append(line(X0, yb, X1, yb, color="#dfe4ea", sw=1.0))
            g.append(poly([(T(t), yb - amp * v) for t, v in pts], color=color, sw=2.2))
        g.append(textbox(1070, ytop + 115, note, size=11, fill=nfill,
                         stroke=MUTED, min_w=290)[0])
        g.append(arrow(925, ytop + 115, arrow_to[0], arrow_to[1], color=MUTED, sw=1.6))
        return g

    f = [text(W / 2, 30, "Порядок увімкнення: чому м'який старт може просто не відбутися",
              size=16, bold=True)]

    # ── правильно: обидві шини стоять, аж тоді EN
    rows_a = [
        ("Vзм", NEG, [(0, 0), (0.10, 0), (0.14, 1), (1, 1)], AMP),
        ("Vвх", POS, [(0, 0), (0.25, 0), (0.29, 1), (1, 1)], AMP),
        ("EN", INK, [(0, 0), (0.45, 0), (0.47, 1), (1, 1)], AMP),
        ("затвор", "#e07b39", [(0, 0), (0.47, 0), (0.80, 0.75), (1, 0.75)], AMP),
        ("Vвих", FIELD, [(0, 0), (0.47, 0), (0.80, 1), (1, 1)], AMP),
        ("Iвх", "#7b3fa0", [(0, 0), (0.47, 0), (0.50, 0.35), (0.80, 0.35),
                            (0.83, 0.25), (1, 0.25)], 30),
    ]
    f += panel(100, "Правильно: EN піднімають, коли обидві шини вже стоять", FIELD, rows_a,
               ["Рампу задає Cм.ст: затвор і вихід", "їдуть угору разом, а кидок у Cвих",
                "не перевищує C · dV/dt."],
               SOFT_G, (T(0.70), 100 + 40 + 5 * 38 - 14))
    f.append(line(T(0.47), 106, T(0.47), 324, color=MUTED, sw=1.2, dash="4 4"))

    # ── небезпечно: EN уже високий, Vвх приходить останнім
    rows_b = [
        ("Vзм", NEG, [(0, 0), (0.10, 0), (0.14, 1), (1, 1)], AMP),
        ("Vвх", POS, [(0, 0), (0.55, 0), (0.59, 1), (1, 1)], AMP),
        ("EN", INK, [(0, 0), (0.12, 0), (0.14, 1), (1, 1)], AMP),
        ("затвор", "#e07b39", [(0, 0), (0.14, 0), (0.22, 1), (1, 1)], AMP),
        ("Vвих", FIELD, [(0, 0), (0.55, 0), (0.60, 1.12), (0.66, 1), (1, 1)], AMP),
        ("Iвх", "#7b3fa0", [(0, 0), (0.55, 0), (0.575, 1.0), (0.63, 0.3),
                            (0.66, 0.25), (1, 0.25)], 30),
    ]
    f += panel(400, "Небезпечно: Vзм і EN є, а Vвх приходить останнім", POS, rows_b,
               ["Виходу немає — петля впирає затвор", "у шину, і рампа витрачається на",
                "мертвому виході. Vвх приходить на", "навстіж відкритий ключ."],
               SOFT_R, (T(0.60), 400 + 40 + 5 * 38 - 28))
    f.append(line(T(0.14), 406, T(0.14), 624, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(T(0.55), 406, T(0.55), 624, color=MUTED, sw=1.2, dash="4 4"))

    f.append(textbox(620, 655,
                     ["Кремнію байдуже — жоден порядок його не вб'є. Гине не чип, а м'який старт.",
                      "Тримай EN унизу, поки не піднялися ОБИДВІ шини, — і питання зникає."],
                     size=12, fill=FILL, stroke=MUTED, min_w=1000)[0])

    return render(os.path.join(IMG, "bias-sequence.svg"), W, H, *f)


# ══ Фігури до вставки «Числа прохідного елемента» (math) ══════════════════════

VT_    = 25.852e-3    # kT/q за 300 К
DEC_MV = VT_ * math.log(10)


def fig_vbe_floor():
    """Логарифм як підлога: пряма 59.5 мВ/декаду і ціна її зсуву."""
    W, H = 980, 470
    X0, X1 = 120.0, 690.0     # 1 мкА … 10 А  (7 декад)
    Y0, Y1 = 385.0, 95.0      # 0 … 0.9 В

    def X(i):
        return X0 + (X1 - X0) * (math.log10(i) + 6.0) / 7.0

    def Y(v):
        return Y0 + (Y1 - Y0) * (v / 0.9)

    IS_R = 2.5e-13            # реальний прохідний NPN на ампер
    IS_H = IS_R * 7.627e5     # уявний, щоб дати 0.4 В на ампері

    f = [text(W / 2, 32, "Vбе = Vт·ln(Iк/Is): пряма в логарифмі струму — і тому підлога",
              size=16, bold=True)]
    f.append(text(X0, 66, "напруга на переході Vбе, В", size=11, color=MUTED, anchor="start"))

    # сітка й осі
    for v in (0.2, 0.4, 0.6, 0.8):
        f.append(line(X0, Y(v), X1, Y(v), color=GRID, sw=1.0, dash="3 5"))
    f.append(line(X0, 82, X0, Y0, color=MUTED, sw=1.5))
    f.append(line(X0 - 6, Y0, X1 + 14, Y0, color=MUTED, sw=1.5))
    for v in (0, 0.2, 0.4, 0.6, 0.8):
        f.append(line(X0 - 5, Y(v), X0, Y(v), color=MUTED, sw=1.2))
        f.append(text(X0 - 10, Y(v) + 4, ("%g" % v), size=11, color=MUTED, anchor="end"))
    for i, lbl in ((1e-6, "1 мкА"), (1e-5, "10 мкА"), (1e-4, "100 мкА"), (1e-3, "1 мА"),
                   (1e-2, "10 мА"), (1e-1, "100 мА"), (1.0, "1 А"), (10.0, "10 А")):
        f.append(line(X(i), Y0, X(i), Y0 + 5, color=MUTED, sw=1.2))
        f.append(text(X(i), Y0 + 21, lbl, size=10, color=MUTED))
    f.append(text((X0 + X1) / 2, Y0 + 44, "струм колектора Iк (логарифмічна вісь)", size=11, color=MUTED))

    N = 70
    def curve(Is):
        return [(X(10 ** (-6 + 7.0 * k / N)), Y(VT_ * math.log(10 ** (-6 + 7.0 * k / N) / Is)))
                for k in range(N + 1)]

    f.append(poly(curve(IS_R), color=POS, sw=2.8))
    f.append(poly(curve(IS_H), color=MUTED, sw=2.2, dash="8 5"))

    # маркери на 1 А
    vr, vh = VT_ * math.log(1 / IS_R), VT_ * math.log(1 / IS_H)
    f.append(circle(X(1), Y(vr), 6, fill=POS, stroke=POS))
    f.append(circle(X(1), Y(vh), 6, fill=BG, stroke=MUTED, sw=2))

    # підпис до прямих — праворуч, поза полем
    f.append(textbox(830, Y(vr) - 26, ["реальний прохідний NPN", "Is = 2.5·10⁻¹³ А",
                                       "1 А → 0.750 В"], size=11, fill=SOFT_R, stroke=POS)[0])
    f.append(textbox(830, Y(vh) + 30, ["уявний «NPN на 0.4 В»", "Is = 1.9·10⁻⁷ А",
                                       "1 А → 0.400 В"], size=11, fill=FILL, stroke=MUTED)[0])
    f.append(line(X(10) + 4, Y(vr + DEC_MV), 700, Y(vr) - 26, color=POS, sw=1.2))
    f.append(line(X(10) + 4, Y(vh + DEC_MV), 700, Y(vh) + 30, color=MUTED, sw=1.2))

    # вертикальна відстань між прямими на 1 А
    f.append(line(X(1), Y(vr), X(1), Y(vh), color=NEG, sw=2.2))
    f.append(arrow(X(1), Y(vr) + 4, X(1), Y(vh) - 4, color=NEG, sw=2.0))
    f.append(arrow(X(1), Y(vh) - 4, X(1), Y(vr) + 4, color=NEG, sw=2.0))
    f.append(textbox(X(1) - 92, (Y(vr) + Y(vh)) / 2, ["350 мВ"], size=13,
                     fill=BG, stroke=NEG, bold=True, color=NEG)[0])

    # трикутник нахилу — на пологій ділянці, подалі від інших написів
    xa, xb = X(1e-4), X(1e-3)
    ya, yb = Y(VT_ * math.log(1e-4 / IS_R)), Y(VT_ * math.log(1e-3 / IS_R))
    f.append(line(xa, ya, xb, ya, color=NEG, sw=1.8))
    f.append(line(xb, ya, xb, yb, color=NEG, sw=1.8))
    f.append(text((xa + xb) / 2, ya + 17, "×10 струму", size=10, color=NEG))
    f.append(text(xb + 8, (ya + yb) / 2 + 4, "59.5 мВ", size=11, color=NEG, anchor="start", bold=True))

    f.append(fitbox(120, 428, 740, 30,
                    "Зсунути пряму вниз на 350 мВ = збільшити Is у 7.6·10⁵ разів = виростити емітер у 760 000 разів.",
                    size=13, fill=SOFT_G, stroke=FIELD))

    return render(os.path.join(IMG, "vbe-floor.svg"), W, H, *f)


def fig_saturation_wall():
    """Струм бази в насиченні має простий полюс — звідси стрибок у dropout."""
    W, H = 960, 480
    X0, X1 = 130.0, 660.0     # 0.40 … 0.62 В
    Y0, Y1 = 390.0, 100.0     # 10 мА … 10 А  (3 декади)

    BF, BR, RC = 30.0, 1.0, 0.39
    WALL = RC * 1.0 + VT_ * math.log(1 + 1 / BR)      # 0.4079 В

    def X(v):
        return X0 + (X1 - X0) * (v - 0.40) / 0.22

    def Y(ma):
        return Y0 + (Y1 - Y0) * (math.log10(ma) - 1.0) / 3.0

    def ib_ma(vtot):
        s = math.exp((vtot - RC) / VT_)
        bf = (s - 1 - 1 / BR) / (1 / BR + s / BF)
        return 1000.0 / bf if bf > 0 else 1e9

    f = [text(W / 2, 32, "Струм бази в насиченні: не крива, а полюс — стіна за 92 мВ від паспорта",
              size=16, bold=True)]
    f.append(text(X0, 68, "струм бази = струм у землю, Iб (логарифмічна вісь)",
                  size=11, color=MUTED, anchor="start"))

    for ma in (30, 100, 300, 1000, 3000):
        f.append(line(X0, Y(ma), X1, Y(ma), color=GRID, sw=1.0, dash="3 5"))
    f.append(line(X0, 86, X0, Y0, color=MUTED, sw=1.5))
    f.append(line(X0 - 6, Y0, X1 + 14, Y0, color=MUTED, sw=1.5))
    for ma, lbl in ((10, "10 мА"), (30, "30 мА"), (100, "100 мА"), (300, "300 мА"),
                    (1000, "1 А"), (3000, "3 А"), (10000, "10 А")):
        f.append(line(X0 - 5, Y(ma), X0, Y(ma), color=MUTED, sw=1.2))
        f.append(text(X0 - 10, Y(ma) + 4, lbl, size=10, color=MUTED, anchor="end"))
    for v in (0.40, 0.45, 0.50, 0.55, 0.60):
        f.append(line(X(v), Y0, X(v), Y0 + 5, color=MUTED, sw=1.2))
        f.append(text(X(v), Y0 + 21, "%.2f" % v, size=10, color=MUTED))
    f.append(text((X0 + X1) / 2, Y0 + 44, "падіння на прохідному PNP, Vке = Vвх − Vвих, В",
                  size=11, color=MUTED))

    # крива Iб(Vке)
    pts, N = [], 400
    for k in range(N + 1):
        v = 0.40 + 0.22 * k / N
        if v <= WALL + 0.0004:
            continue
        ma = ib_ma(v)
        if ma > 11000 or ma < 9:
            continue
        pts.append((X(v), Y(ma)))
    f.append(poly(pts, color=NEG, sw=2.8))

    # асимптота
    f.append(line(X(WALL), 92, X(WALL), Y0, color=POS, sw=2.0, dash="7 4"))
    f.append(textbox(X(WALL) + 118, 126,
                     ["стіна: Vке = Iвих·Rc + Vт·ln(1/αR)", "= 0.390 + 0.018 = 0.408 В",
                      "лівіше — жодного струму бази не досить"],
                     size=11, fill=SOFT_R, stroke=POS)[0])

    # паспортна точка
    f.append(circle(X(0.50), Y(ib_ma(0.50)), 6, fill=POS, stroke=POS))
    f.append(textbox(X(0.50) + 138, Y(ib_ma(0.50)) + 4,
                     ["паспортний dropout 0.5 В", "→ βforced = 20, Iб = 49 мА"],
                     size=11, fill=FILL, stroke=MUTED)[0])
    f.append(line(X(0.50) + 8, Y(ib_ma(0.50)), X(0.50) + 62, Y(ib_ma(0.50)) + 4, color=MUTED, sw=1.2))

    # активна ділянка
    f.append(circle(X(0.60), Y(ib_ma(0.60)), 5, fill=FIELD, stroke=FIELD))
    f.append(text(X(0.60) + 12, Y(ib_ma(0.60)) + 26, "тут ще активний режим: Iб = Iк/βF = 33 мА",
                  size=11, color=FIELD, anchor="start"))

    # смуга «92 мВ»
    yb = 358.0
    f.append(line(X(WALL), yb, X(0.50), yb, color=NEG, sw=2.0))
    f.append(arrow(X(WALL), yb, X(0.50), yb, color=NEG, sw=1.8))
    f.append(arrow(X(0.50), yb, X(WALL), yb, color=NEG, sw=1.8))
    f.append(text((X(WALL) + X(0.50)) / 2, yb - 9, "92 мВ", size=12, color=NEG, bold=True))

    f.append(fitbox(130, 438, 700, 30,
                    "Iб = Iк·(1/βR + s/βF) / (s − 1/αR),   s = exp(Vке(EM)/Vт)   —   простий полюс при s = 1/αR",
                    size=13, fill=SOFT_G, stroke=FIELD))

    return render(os.path.join(IMG, "saturation-wall.svg"), W, H, *f)


def fig_gm_ladder():
    """Опір вихідного вузла: межа Больцмана, MOSFET над нею, навантаження зверху."""
    W, H = 1000, 490
    X0, X1 = 140.0, 640.0     # 1 мА … 1 А (3 декади)
    Y0, Y1 = 395.0, 95.0      # 0.01 … 10 000 Ом (6 декад)

    VOUT, N_, KF = 3.3, 1.4, 22.2

    def X(i):
        return X0 + (X1 - X0) * (math.log10(i) + 3.0) / 3.0

    def Y(z):
        return Y0 + (Y1 - Y0) * (math.log10(z) + 2.0) / 6.0

    def z_nmos(i):
        return max(math.sqrt(1.0 / (2 * KF * i)), N_ * VT_ / i)

    f = [text(W / 2, 32, "Опір вихідного вузла: чому перевага повторювача стала лише в біполярного",
              size=16, bold=True)]
    f.append(text(X0, 66, "опір вузла Zвих, Ом (логарифмічна вісь)", size=11, color=MUTED, anchor="start"))

    f.append(line(X0, 82, X0, Y0, color=MUTED, sw=1.5))
    f.append(line(X0 - 6, Y0, X1 + 14, Y0, color=MUTED, sw=1.5))
    for z, lbl in ((0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"),
                   (100, "100"), (1000, "1 к"), (10000, "10 к")):
        f.append(line(X0 - 7, Y(z), X0, Y(z), color=MUTED, sw=1.2))
        f.append(text(X0 - 12, Y(z) + 4, lbl, size=11, color=MUTED, anchor="end"))
    for i, lbl in ((1e-3, "1 мА"), (1e-2, "10 мА"), (1e-1, "100 мА"), (1.0, "1 А")):
        f.append(line(X(i), Y0, X(i), Y0 + 5, color=MUTED, sw=1.2))
        f.append(text(X(i), Y0 + 21, lbl, size=11, color=MUTED))
    f.append(text((X0 + X1) / 2, Y0 + 44, "струм навантаження Iвих (логарифмічна вісь)",
                  size=11, color=MUTED))

    M = 60
    def cur(fn):
        return [(X(10 ** (-3 + 3.0 * k / M)), Y(fn(10 ** (-3 + 3.0 * k / M)))) for k in range(M + 1)]

    f.append(poly(cur(lambda i: VOUT / i), color=NEG, sw=2.8))            # інверсний
    f.append(poly(cur(z_nmos), color="#e07b39", sw=2.8))                  # NMOS-повторювач
    f.append(poly(cur(lambda i: VT_ / i), color=FIELD, sw=2.8))           # BJT-повторювач

    # підписи прямих — праворуч від поля
    f.append(textbox(806, Y(3.3) - 8, ["інверсний: Zвих = Rнав", "= Vвих / Iвих"],
                     size=11, fill=SOFT_R, stroke=NEG)[0])
    f.append(textbox(806, Y(0.15) - 34, ["NMOS-повторювач:", "Zвих = 1/gm = Vov / 2Iвих"],
                     size=11, fill=FILL, stroke="#e07b39")[0])
    f.append(textbox(806, Y(0.02585) + 14, ["BJT-повторювач:", "Zвих = 1/gm = Vт / Iвих"],
                     size=11, fill=SOFT_G, stroke=FIELD)[0])
    f.append(line(X(1) + 4, Y(3.3), 712, Y(3.3) - 8, color=NEG, sw=1.2))
    f.append(line(X(1) + 4, Y(0.15), 700, Y(0.15) - 34, color="#e07b39", sw=1.2))
    f.append(line(X(1) + 4, Y(0.02585), 700, Y(0.02585) + 14, color=FIELD, sw=1.2))

    # сталий розрив ×127 — на обох кінцях
    for i, lab in ((1e-3, "×127"), (1.0, "×127")):
        xa = X(i) + (26 if i < 1e-2 else -26)
        f.append(line(xa, Y(VOUT / i), xa, Y(VT_ / i), color=MUTED, sw=1.4, dash="4 3"))
        f.append(arrow(xa, Y(VOUT / i) + 3, xa, Y(VT_ / i) - 3, color=MUTED, sw=1.4))
        f.append(arrow(xa, Y(VT_ / i) - 3, xa, Y(VOUT / i) + 3, color=MUTED, sw=1.4))
        f.append(textbox(xa + (54 if i < 1e-2 else -50), (Y(VOUT / i) + Y(VT_ / i)) / 2,
                         [lab], size=12, fill=BG, stroke=MUTED, bold=True)[0])

    # злам NMOS
    f.append(circle(X(0.058), Y(z_nmos(0.058)), 5, fill=BG, stroke="#e07b39", sw=2))
    f.append(textbox(300, 140, ["злам при 58 мА: нижче NMOS іде в підпоріг,",
                                "де його крутість теж стає Iд/(n·Vт) —",
                                "і пряма лягає паралельно біполярній, ×1.4 вище"],
                     size=11, fill=FILL, stroke="#e07b39")[0])
    f.append(arrow(300, 176, X(0.058) - 4, Y(z_nmos(0.058)) - 6, color="#e07b39", sw=1.5))

    f.append(fitbox(140, 440, 720, 32,
                    "Розрив «навантаження ÷ біполярний» сталий (обидві прямі ∝ 1/I). Розрив до NMOS у сильній інверсії тане: ×91 на 1 мА → ×22 на 1 А.",
                    size=12, fill=SOFT_G, stroke=FIELD))

    return render(os.path.join(IMG, "gm-ladder.svg"), W, H, *f)


if __name__ == "__main__":
    fig_topologies()
    fig_dropout()
    fig_ground()
    fig_pole()
    fig_vertical_vs_lateral()
    fig_pass_eras()
    fig_nmos_block()
    fig_two_dropouts()
    fig_bias_sequence()
    fig_vbe_floor()
    fig_saturation_wall()
    fig_gm_ladder()
    print("ok:", os.listdir(IMG))
