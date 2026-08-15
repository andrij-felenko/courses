# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


# ── 1. Три долі сторінки, яку вирішили забрати ────────────────────────────────
def fig_three_fates():
    W, H = 1205, 660
    p = []

    cols = [
        (85, "Чиста файлова", NEG, COOL,
         "вміст є у файлі\nна диску, і копія\nсвіжа",
         "відв'язати від\nтаблиць сторінок —\nі фрейм вільний",
         "нічого", "читання з файлу"),
        (370, "Брудна файлова", "#b7791f", "#fdf6e3",
         "вміст є у файлі,\nале копія на диску\nвідстала",
         "спершу скинути\nна диск, тоді\nзвільняти",
         "один запис", "читання з файлу"),
        (655, "Анонімна", POS, WARM,
         "вмісту немає\nніде, крім самої\nпам'яті",
         "записати у своп —\nінакше забрати\nне можна взагалі",
         "один запис", "читання зі свопу"),
        (940, "Незабирана", MUTED, PALE,
         "mlock, буфери DMA,\nтаблиці сторінок,\nстеки ядра",
         "нічого: фрейм\nлишається за\nвласником",
         "—", "—"),
    ]

    for x, name, accent, fillc, where, how, now, later in cols:
        p.append(fitbox(x, 62, 225, 44, name, size=14,
                        fill=fillc, stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(fitbox(x, 124, 225, 84, where, size=12,
                        fill=SOFT, stroke=MUTED, sw=1.2, color=INK))
        p.append(fitbox(x, 224, 225, 84, how, size=12,
                        fill=SOFT, stroke=accent, sw=1.5, color=INK))
        p.append(fitbox(x, 336, 225, 44, now, size=13,
                        fill="#fff", stroke=accent, sw=1.4, color=accent, bold=True))
        p.append(fitbox(x, 396, 225, 44, later, size=12,
                        fill="#fff", stroke=MUTED, sw=1.2, color=MUTED))

    p.append(text(79, 154, "де копія", size=11, color=MUTED, anchor="end"))
    p.append(text(79, 358, "ціна зараз", size=11, color=MUTED, anchor="end"))
    p.append(text(79, 418, "ціна потім", size=11, color=MUTED, anchor="end"))

    p.append(fitbox(85, 470, 1080, 90,
                    "правило одне: сторінку можна забрати лише тоді, коли її вміст можна відтворити на вимогу\n"
                    "своп — це і є дім, який будують анонімній сторінці, щоб її взагалі стало можна забрати",
                    size=13, fill=GREENF, stroke=FIELD, sw=1.6, color=INK))
    p.append(text(W / 2, 604,
                  "без свопу третя колонка стає четвертою: анонімна пам'ять перестає бути забиральною",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "three-fates.svg"), W, H, *p,
           title="Що можна зробити зі сторінкою, коли треба звільнити фрейм")


# ── 2. Запис у таблиці сторінок до й після витіснення ─────────────────────────
def fig_swap_pte():
    W, H = 1120, 600
    p = []

    # présent
    p.append(text(60, 84, "сторінка в пам'яті", size=13, color=NEG, anchor="start", bold=True))
    p.append(fitbox(60, 100, 520, 56, "номер фрейму (PFN)", size=13,
                    fill=COOL, stroke=NEG, sw=1.8, color=INK, bold=True))
    p.append(fitbox(596, 100, 100, 56, "A", size=13, fill=SOFT, stroke=NEG, sw=1.4, color=INK))
    p.append(fitbox(712, 100, 100, 56, "D", size=13, fill=SOFT, stroke=NEG, sw=1.4, color=INK))
    p.append(fitbox(828, 100, 130, 56, "права", size=12, fill=SOFT, stroke=NEG, sw=1.4, color=INK))
    p.append(fitbox(974, 100, 86, 56, "P=1", size=13, fill="#fff", stroke=NEG, sw=2.0, color=NEG, bold=True))
    p.append(text(646, 180, "біт звернення", size=10, color=MUTED))
    p.append(text(762, 180, "біт запису", size=10, color=MUTED))

    # стрілки посередині
    p.append(arrow(300, 210, 300, 330, color=POS, sw=2.0))
    p.append(fitbox(330, 224, 420, 92,
                    "витіснення: вміст переписано у слот свопу,\n"
                    "а в сам запис ядро кладе адресу цього слота",
                    size=12, fill=WARM, stroke=POS, sw=1.4, color=INK))
    p.append(arrow(880, 330, 880, 210, color=FIELD, sw=2.0))
    p.append(fitbox(790, 224, 300, 92,
                    "великий збій: слот прочитано\nу новий фрейм, запис відновлено",
                    size=12, fill=GREENF, stroke=FIELD, sw=1.4, color=INK))

    # відсутній
    p.append(text(60, 356, "сторінки в пам'яті немає", size=13, color=POS, anchor="start", bold=True))
    p.append(fitbox(60, 372, 300, 56, "тип області свопу", size=13,
                    fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))
    p.append(fitbox(376, 372, 584, 56, "номер слота в цій області", size=13,
                    fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))
    p.append(fitbox(974, 372, 86, 56, "P=0", size=13, fill="#fff", stroke=POS, sw=2.0, color=POS, bold=True))

    p.append(fitbox(60, 466, 1000, 86,
                    "апаратура дивиться лише на P; коли він нуль, решта бітів для неї — сміття\n"
                    "ядро зберігає там те, що потрібне саме йому: адресу слота, позначку міграції чи збійної пам'яті",
                    size=13, fill=PALE, stroke=MUTED, sw=1.3, color=INK))

    render(os.path.join(OUT, "swap-pte.svg"), W, H, *p,
           title="Той самий запис у таблиці сторінок: до витіснення і після")


# ── 3. Карусель двох черг і тінь, що дає зворотний зв'язок ────────────────────
def fig_lru_lists():
    W, H = 1160, 700
    p = []

    p.append(fitbox(400, 74, 360, 82,
                    "АКТИВНІ\nдо них зверталися недавно",
                    size=14, fill=GREENF, stroke=FIELD, sw=1.9, color=INK, bold=True))
    p.append(fitbox(400, 250, 360, 82,
                    "НЕАКТИВНІ\nвипробувальна смуга",
                    size=14, fill="#fdf6e3", stroke="#b7791f", sw=1.9, color=INK, bold=True))
    p.append(fitbox(400, 424, 360, 82,
                    "ЗАБРАНО\nфрейм вільний",
                    size=14, fill=WARM, stroke=POS, sw=1.9, color=INK, bold=True))

    p.append(arrow(490, 160, 490, 246, color=MUTED, sw=1.9))
    p.append(arrow(670, 246, 670, 160, color=FIELD, sw=1.9))
    p.append(arrow(580, 336, 580, 420, color=POS, sw=1.9))

    p.append(fitbox(40, 96, 320, 100,
                    "старіння: сканування зсуває\nхвіст активних у неактивні\nй гасить біт звернення",
                    size=12, fill=SOFT, stroke=MUTED, sw=1.3, color=INK))
    p.append(fitbox(800, 96, 320, 100,
                    "друга нагода: звернулися,\nпоки лежала внизу, —\nі вона повертається нагору",
                    size=12, fill=SOFT, stroke=FIELD, sw=1.3, color=INK))
    p.append(fitbox(800, 400, 320, 130,
                    "тінь: на місці викинутої\nсторінки в кеші лишається\nпозначка з номером\nпокоління витіснення",
                    size=12, fill=COOL, stroke=NEG, sw=1.5, color=INK))
    p.append(arrow(770, 466, 796, 466, color=NEG, sw=1.8))

    p.append(fitbox(40, 570, 1080, 90,
                    "повернулася скоро після витіснення — черга була замала: сторінку одразу в АКТИВНІ,\n"
                    "а межу між чергами зсувають на її користь; це й є те, що лічильники звуть refault",
                    size=13, fill=PALE, stroke=NEG, sw=1.5, color=INK))
    p.append(line(370, 614, 370, 116, color=NEG, sw=1.6, dash="6 6"))
    p.append(arrow(370, 116, 396, 116, color=NEG, sw=1.8))

    p.append(text(W / 2, 686,
                  "таких пар дві — окремо для файлових сторінок і окремо для анонімних",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "lru-lists.svg"), W, H, *p,
           title="Карусель черг: старіння, друга нагода і слід від викинутої сторінки")


# ── 4. Рівневі позначки: хто платить за прибирання ────────────────────────────
def fig_watermarks():
    W, H = 1140, 620
    p = []

    zones = [
        (80, 260, WARM, POS, "нижче min"),
        (260, 480, "#fdf6e3", "#b7791f", "min … low"),
        (480, 700, "#eef7ff", NEG, "low … high"),
        (700, 1060, GREENF, FIELD, "вище high"),
    ]
    for x1, x2, fillc, accent, name in zones:
        p.append(rect(x1, 150, x2 - x1, 62, fill=fillc, stroke=accent, sw=1.7, rx=4))
        p.append(text((x1 + x2) / 2, 188, name, size=13, color=accent, bold=True))

    for x, lab in ((260, "min"), (480, "low"), (700, "high")):
        p.append(line(x, 132, x, 236, color=INK, sw=1.4, dash="4 4"))
        p.append(text(x, 124, lab, size=12, color=INK, bold=True))

    p.append(text(80, 116, "вільної пам'яті обмаль", size=12, color=MUTED, anchor="start"))
    p.append(text(1060, 116, "вільної пам'яті вдосталь", size=12, color=MUTED, anchor="end"))

    acts = [
        (40, 260, WARM, POS,
         "прохач витісняє сам —\nпрямий відбір його коштом;\nне вийшло — OOM-вбивця"),
        (300, 260, "#fdf6e3", "#b7791f",
         "kswapd вивільняє у фоні;\nпрохачі беруть із пулу\nй нічого не помічають"),
        (580, 260, "#eef7ff", NEG,
         "розбуджений на low,\nkswapd дотягує рівень\nназад до high"),
        (860, 240, GREENF, FIELD,
         "ніхто нічого не робить"),
    ]
    for x, w, fillc, accent, s in acts:
        p.append(fitbox(x, 268, w, 116, s, size=12,
                        fill=fillc, stroke=accent, sw=1.5, color=INK))

    p.append(fitbox(40, 424, 1060, 96,
                    "kswapd прокидається на low і працює, доки не дотягне рівень до high\n"
                    "коли виділення випереджають його, рівень провалюється до min — і кожне наступне виділення саме йде в диск",
                    size=13, fill=PALE, stroke=MUTED, sw=1.3, color=INK))
    p.append(text(W / 2, 566,
                  "машина «встає» не тому, що диск повільний, а тому, що затримку диска приписали кожному, хто просить пам'ять",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "watermarks.svg"), W, H, *p,
           title="Рівневі позначки вільної пам'яті й хто платить за прибирання")


# ── 5. Що означало слово «свопінг» у різні епохи (вставка hist-) ──────────────
def fig_swap_eras():
    rows = [
        ("1975 · Unix V6, PDP-11", "образ процесу\nцілком",
         "нульовий процес перекачує образи через диск;\nжертва — та, що найдовше просиділа в пам'яті", WARM),
        ("1979 · 3BSD, VAX-11/780", "сторінка",
         "посторінкова підкачка (Джой, Бабаоглу);\nбіти звернення довелося імітувати програмно", GREENF),
        ("2001 · Linux 2.4.10", "сторінка",
         "заміна підсистеми пам'яті посеред стабільної\nгілки (Арканджелі замість ван Ріла)", COOL),
        ("2001–2004 · Linux 2.5–2.6", "сторінка",
         "зворотні відображення: rmap, далі об'єктні для\nфайлових (Маккракен) і anon_vma (Арканджелі)", COOL),
        ("2008 · Linux 2.6.28", "сторінка\n+ клас",
         "окремі черги анонімних і файлових сторінок\n(ван Ріл); незабирані — геть зі сканування", COOL),
        ("2014 · Linux 3.15", "сторінка\n+ історія",
         "тінь у кеші й відстань повернення (Вайнер):\nвидно, що викинуто помилково", COOL),
        ("2022 · Linux 6.1", "сторінка\n+ покоління",
         "багатопоколінна черга: замість двох черг —\nпокоління, а таблиці сторінок скануються прямо", COOL),
    ]

    X1, W1 = 40, 300
    X2, W2 = 364, 236
    X3, W3 = 624, 512
    RH, GAP = 84, 10
    TOP = 34
    W = X3 + W3 + 40
    H = TOP + 46 + GAP + len(rows) * (RH + GAP) + 44

    p = []
    p.append(fitbox(X1, TOP, W1, 46, "епоха", size=14, fill=PALE, stroke=MUTED,
                    sw=1.3, color=MUTED, bold=True))
    p.append(fitbox(X2, TOP, W2, 46, "одиниця витіснення", size=14, fill=PALE,
                    stroke=MUTED, sw=1.3, color=MUTED, bold=True))
    p.append(fitbox(X3, TOP, W3, 46, "що з'явилося", size=14, fill=PALE,
                    stroke=MUTED, sw=1.3, color=MUTED, bold=True))

    y = TOP + 46 + GAP
    for era, unit, what, tone in rows:
        p.append(fitbox(X1, y, W1, RH, era, size=14, fill=SOFT, stroke=MUTED,
                        sw=1.3, color=INK, bold=True))
        p.append(fitbox(X2, y, W2, RH, unit, size=14, fill=tone, stroke=MUTED,
                        sw=1.3, color=INK, bold=True))
        p.append(fitbox(X3, y, W3, RH, what, size=13, fill=SOFT, stroke=MUTED,
                        sw=1.3, color=INK))
        y += RH + GAP

    p.append(text(W / 2, y + 24,
                  "одиниця змінилася один раз — 1979 року; далі поглиблювався лише спосіб вибору",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "swap-eras.svg"), W, H, *p,
           title="Що означало слово «свопінг» у різні епохи лінії Unix")


# ── 6. Чотири контрольні точки досліду й що показує кожен прилад ─────────────
def fig_probe_checkpoints():
    W, H = 1180, 600
    p = []
    LX, LW = 26, 200
    colw, gap = 216, 18
    x0 = LX + LW + gap
    xs = [x0 + i * (colw + gap) for i in range(4)]

    heads = [
        ("1 щойно виділено", "mmap(), жодного доступу", MUTED, PALE),
        ("2 після торкання", "запис у кожну сторінку", FIELD, GREENF),
        ("3 після MADV_PAGEOUT", "ядро витіснило ділянку", POS, WARM),
        ("4 після повернення", "читання кожної сторінки", NEG, COOL),
    ]
    for x, (t1, t2, accent, fillc) in zip(xs, heads):
        p.append(fitbox(x, 52, colw, 58, t1 + "\n" + t2, size=13,
                        fill=fillc, stroke=accent, sw=1.8, color=INK))

    rows = [
        ("mincore()", "біт резидентності",
         ["0 з 65536", "65536 з 65536", "0 з 65536", "65536 з 65536"]),
        ("RssAnon", "скільки в пам'яті",
         ["2 108 кБ", "264 252 кБ", "2 216 кБ", "264 260 кБ"]),
        ("VmSwap", "скільки у свопі",
         ["0 кБ", "0 кБ", "262 144 кБ", "0 кБ"]),
        ("ru_majflt", "великих збоїв",
         ["0", "0", "0", "8 213"]),
    ]
    for i, (name, sub, vals) in enumerate(rows):
        y = 126 + i * 68
        p.append(fitbox(LX, y, LW, 56, name + "\n" + sub, size=13,
                        fill=SOFT, stroke=MUTED, sw=1.3, color=INK))
        for j, (x, v) in enumerate(zip(xs, vals)):
            p.append(fitbox(x, y, colw, 56, v, size=14,
                            fill="#fff", stroke=heads[j][2], sw=1.3, color=INK))

    p.append(fitbox(LX, 406, W - 2 * LX, 92,
                    "для mincore() стовпці 1 і 3 однакові: нуль резидентних сторінок\n"
                    "але в першому їх ще ніколи не було, а в третьому вони у свопі — розрізняє це лише VmSwap",
                    size=13, fill=GREENF, stroke=FIELD, sw=1.6, color=INK))

    p.append(text(W / 2, 540,
                  "великих збоїв у стовпці 4 увосьмеро менше за сторінки: сусідів підтягує "
                  "випереджальне читання свопу (vm.page-cluster = 3)",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "probe-checkpoints.svg"), W, H, *p,
           title="Чотири контрольні точки досліду і що показує кожен прилад")


def _poly(pts, color, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


# ── 7. Обрив: сповільнення як функція нестачі пам'яті (вставка math) ─────────
def fig_cliff():
    import math
    W, H = 1160, 730
    p = []
    x0, x1 = 170, 1000
    yb, yt = 480, 100
    dmax = 0.20
    th = math.log(0.8) / math.log(0.2)

    def X(d):
        return x0 + (d / dmax) * (x1 - x0)

    def Y(S):
        return yb - (math.log10(S) / 4.0) * (yb - yt)

    p.append(rect(x0, yt, x1 - x0, yb - yt, fill="#fcfdff", stroke=MUTED, sw=1.2, rx=4))
    for S, lab in ((1, "×1"), (10, "×10"), (100, "×100"),
                   (1000, "×1000"), (10000, "×10000")):
        y = Y(S)
        if S > 1:
            p.append(line(x0, y, x1, y, color="#dfe4ec", sw=1.0))
        p.append(text(x0 - 16, y + 4, lab, size=12, color=MUTED, anchor="end"))

    for d in (0.0, 0.05, 0.10, 0.15, 0.20):
        x = X(d)
        p.append(line(x, yb, x, yb + 8, color=MUTED, sw=1.2))
        p.append(text(x, yb + 28, ("%g %%" % (d * 100)) if d else "0",
                      size=12, color=MUTED))

    curves = [("NVMe", 1250.0, NEG),
              ("SATA SSD", 3750.0, "#b7791f"),
              ("обертовий диск", 125000.0, POS)]
    for name, R, col in curves:
        pts = []
        n = 500
        for i in range(n + 1):
            d = dmax * i / n
            S = 1.0 + R * (1.0 - (1.0 - d) ** th)
            pts.append((X(d), Y(min(max(S, 1.0), 10000.0))))
        p.append(_poly(pts, col))
        Send = min(1.0 + R * (1.0 - (1.0 - dmax) ** th), 10000.0)
        p.append(text(x1 + 14, Y(Send) + 4, name, size=13,
                      color=col, bold=True, anchor="start"))

    y2 = Y(2.0)
    p.append(line(x0, y2, x1, y2, color=INK, sw=1.3, dash="6 5"))
    p.append(text(x1 - 12, y2 - 14, "×2 — удвічі повільніше",
                  size=12, color=INK, anchor="end"))

    p.append(text(x0, yt - 24, "у скільки разів повільніший середній доступ до пам'яті",
                  size=12, color=MUTED, anchor="start"))
    p.append(text(W / 2, yb + 56,
                  "нестача d — частка живого робочого набору, що не вміщається в пам'ять",
                  size=13, color=INK))

    rows = [("NVMe", NEG, "0.58 %"),
            ("SATA SSD", "#b7791f", "0.19 %"),
            ("обертовий диск", POS, "0.0058 %")]
    for i, (name, col, val) in enumerate(rows):
        p.append(fitbox(170 + i * 285, 566, 265, 92,
                        name + "\nвистачає нестачі " + val + ",\nщоб стати вдвічі повільнішим",
                        size=12, fill=SOFT, stroke=col, sw=1.7, color=INK))

    p.append(text(W / 2, 700,
                  "межа ×2 стоїть при d* = 1 / (R·θ): стократно швидший пристрій "
                  "зсуває її стократно — і вона лишається часткою відсотка",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "thrashing-cliff.svg"), W, H, *p,
           title="Втрата швидкодії від нестачі пам'яті при законі звернень 80/20")


# ── 8. Черга як вікно в часі: τmax = L / v (вставка math) ────────────────────
def fig_refault_window():
    W, H = 1160, 600
    p = []
    ax, bx, ay = 150, 1030, 300
    tmax = 60.0

    def X(t):
        return ax + (t / tmax) * (bx - ax)

    p.append(rect(X(0), 270, X(21.0) - X(0), 30,
                  fill=GREENF, stroke=FIELD, sw=1.6, rx=4))
    p.append(rect(X(21.0), 270, bx - X(21.0), 30,
                  fill=WARM, stroke=POS, sw=1.4, rx=4))
    p.append(line(ax, ay, bx, ay, color=INK, sw=2.0))

    for t in (0, 10, 20, 30, 40, 50, 60):
        x = X(t)
        p.append(line(x, ay, x, ay + 8, color=MUTED, sw=1.2))
        p.append(text(x, ay + 28, ("%d с" % t) if t else "0", size=12, color=MUTED))

    marks = [(3.0, FIELD, "3 с — вижила"),
             (15.0, FIELD, "15 с — вижила"),
             (45.0, POS, "45 с — загинула")]
    for t, col, lab in marks:
        x = X(t)
        p.append(line(x, 212, x, 264, color=col, sw=1.4, dash="4 4"))
        p.append(circle(x, 202, 8, fill="#fff", stroke=col, sw=2.2))
        p.append(text(x, 176, lab, size=12, color=col, bold=True))

    p.append(line(X(0), 346, X(21.0), 346, color=FIELD, sw=1.8))
    p.append(line(X(0), 338, X(0), 346, color=FIELD, sw=1.8))
    p.append(line(X(21.0), 338, X(21.0), 346, color=FIELD, sw=1.8))
    p.append(text((X(0) + X(21.0)) / 2, 370,
                  "вікно пам'яті τmax = L / v ≈ 21 с", size=13,
                  color=FIELD, bold=True))

    p.append(text(W / 2, 148, "як давно до сторінки востаннє зверталися",
                  size=12, color=MUTED))

    p.append(fitbox(150, 400, 880, 118,
                    "сторінка вижила б  ⟺  D ≤ L        D — відстань повернення, L — довжина черг\n"
                    "за час відсутності сталося D = v·τ витіснень        v — темп витіснень, τ — проміжок повторного звернення\n"
                    "звідси  L ≥ v·τ,  тобто черга рятує лише те, до чого повертаються частіше, ніж кожні L / v секунд",
                    size=13, fill=SOFT, stroke=MUTED, sw=1.4, color=INK))

    p.append(text(W / 2, 556,
                  "L = 4 ГіБ і v = 50 000 сторінок/с дають вікно у 21 секунду: "
                  "менша черга й більший темп ріжуть його добутком",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "refault-window.svg"), W, H, *p,
           title="Довжина черг — це не обсяг, а проміжок часу")


# ── 9. Беззбитковість стиснення (вставка math) ──────────────────────────────
def fig_zram_breakeven():
    W, H = 1160, 700
    p = []

    p.append(fitbox(60, 74, 480, 150,
                    "справжній своп\n\n"
                    "щоб вивільнити ΔM — викинути рівно ΔM\n"
                    "ціна повернення сторінки — t_dev\n"
                    "втрата ∝ θ · (ΔM / W) · t_dev",
                    size=13, fill=COOL, stroke=NEG, sw=1.7, color=INK))
    p.append(fitbox(620, 74, 480, 150,
                    "zram\n\n"
                    "щоб вивільнити ΔM — стиснути ΔM · c/(c−1)\n"
                    "ціна повернення сторінки — t_dec\n"
                    "втрата ∝ θ · (ΔM / W) · c/(c−1) · t_dec",
                    size=13, fill=GREENF, stroke=FIELD, sw=1.7, color=INK))

    p.append(fitbox(160, 252, 840, 78,
                    "zram дешевший  ⟺  t_dec / t_dev  <  (c − 1) / c",
                    size=17, fill="#fff", stroke=INK, sw=2.0, color=INK, bold=True))

    p.append(text(W / 2, 372,
                  "скільки стиснути, щоб вивільнити один мегабайт: коефіцієнт c/(c−1)",
                  size=13, color=INK))

    bars = [(1.1, 11.0), (1.2, 6.0), (1.5, 3.0), (2.0, 2.0), (3.0, 1.5), (4.0, 1.33)]
    base, top = 620, 420
    for i, (c, k) in enumerate(bars):
        x = 170 + i * 140
        h = (k / 11.0) * (base - top)
        col = POS if k > 2.5 else (FIELD if k < 1.8 else "#b7791f")
        p.append(rect(x, base - h, 92, h, fill="#fff", stroke=col, sw=2.0, rx=3))
        p.append(text(x + 46, base - h - 12, "×%.2f" % k, size=13, color=col, bold=True))
        p.append(text(x + 46, base + 26, "c = %g" % c, size=13, color=INK))

    p.append(line(150, base, 1010, base, color=INK, sw=1.6))

    p.append(text(W / 2, 672,
                  "при c → 1 множник c/(c−1) росте без міри: стиснення програє не тоді, "
                  "коли повільне, а тоді, коли даних більше не стискає",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "zram-breakeven.svg"), W, H, *p,
           title="Точка беззбитковості стиснення в пам'яті")


# ── 6. Карта чисел: де рівень, де потік, де затримка (вставка api-) ───────────
def fig_counter_map():
    X1, W1 = 40, 190
    X2, W2 = 240, 340
    X3, W3 = 590, 350
    X4, W4 = 950, 270
    RH, GAP, TOP = 100, 10, 34
    HH = 62
    W = X4 + W4 + 40

    heads = [
        (X2, W2, "РІВЕНЬ\nскільки просто зараз", NEG, COOL),
        (X3, W3, "ПОТІК\nскільки відтоді — потрібна різниця", POS, WARM),
        (X4, W4, "ЗАТРИМКА\nскільки часу втрачено", "#b7791f", "#fdf6e3"),
    ]

    rows = [
        ("МАШИНА",
         "/proc/meminfo\nSwapTotal · SwapFree · SwapCached\nActive(anon) … Inactive(file)\nDirty · Writeback · Mlocked",
         "/proc/vmstat\npswpin · pswpout · pgmajfault\npgscan_* · pgsteal_* · allocstall_*\nworkingset_refault_* · _activate_*",
         "/proc/pressure/memory\nsome · full\navg10 / avg60 / avg300\ntotal у мікросекундах"),
        ("ГРУПА\ncgroup v2",
         "memory.stat: anon · file ·\nswapcached · active_anon …\nmemory.swap.current",
         "memory.stat: pgscan · pgsteal ·\npgmajfault · workingset_*\nmemory.swap.events",
         "memory.pressure\nтой самий формат,\nтільки про цю групу"),
        ("ПРОЦЕС",
         "status: VmSwap\nsmaps_rollup: Swap · SwapPss",
         "stat: majflt — дванадцяте поле",
         "—"),
        ("ОБЛАСТЬ\nСВОПУ",
         "swapon --show: SIZE · USED · PRIO\nzram mm_stat: orig_data_size ·\ncompr_data_size · mem_used_total",
         "vmstat 1: si · so у КіБ/с\nzram io_stat",
         "—"),
    ]

    H = TOP + HH + GAP + len(rows) * (RH + GAP) + 46
    p = []

    p.append(fitbox(X1, TOP, W1, HH, "обсяг\nспостереження", size=13,
                    fill=PALE, stroke=MUTED, sw=1.3, color=MUTED, bold=True))
    for x, w, s, accent, fillc in heads:
        p.append(fitbox(x, TOP, w, HH, s, size=13, fill=fillc,
                        stroke=accent, sw=1.7, color=accent, bold=True))

    y = TOP + HH + GAP
    for name, lvl, flow, lat in rows:
        p.append(fitbox(X1, y, W1, RH, name, size=13, fill=SOFT,
                        stroke=MUTED, sw=1.3, color=INK, bold=True))
        p.append(fitbox(X2, y, W2, RH, lvl, size=12, fill=COOL,
                        stroke=NEG, sw=1.3, color=INK))
        p.append(fitbox(X3, y, W3, RH, flow, size=12, fill=WARM,
                        stroke=POS, sw=1.3, color=INK))
        p.append(fitbox(X4, y, W4, RH, lat, size=12, fill="#fdf6e3",
                        stroke="#b7791f", sw=1.3, color=INK))
        y += RH + GAP

    p.append(text(W / 2, y + 26,
                  "рівень читають один раз; потік має сенс лише як різниця двох читань, поділена на час",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "counter-map.svg"), W, H, *p,
           title="Де лежать числа про своп: обсяг спостереження проти сорту числа")


fig_counter_map()
fig_three_fates()
fig_swap_pte()
fig_lru_lists()
fig_watermarks()
fig_swap_eras()
fig_probe_checkpoints()
fig_cliff()
fig_refault_window()
fig_zram_breakeven()
print("ok")
