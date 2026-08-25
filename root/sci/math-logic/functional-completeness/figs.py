# -*- coding: utf-8 -*-
"""Фігури до статті «Функціональна повнота».
Запуск:  python figs.py   → пише SVG у ./img/  (nand-builds, post-classes)
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#e7f6ec"   # клітина «виходить з класу»
GREYFILL  = "#eef0f2"   # клітина «застрягла в класі»
GATEFILL  = "#eef3fb"   # заливка вентиля
BAND      = "#f4f6f8"   # смуга парного рядка


# ── 1. Як NAND будує ¬, ∧, ∨ ─────────────────────────────────────────────────
def fig_nand_builds():
    W, H = 860, 520
    f = [text(W / 2, 32, "Як з одного NAND зібрати ¬, ∧ і ∨", size=18, bold=True),
         text(W / 2, 54, "NAND(a, b) = ¬(a ∧ b);  усі три схеми складено ЛИШЕ з таких вентилів",
              size=12.5, color=MUTED, italic=True)]

    def gate(cx, cy):
        # вентиль як підписана рамка (fitbox — безпечний текст-у-рамці)
        return fitbox(cx - 48, cy - 24, 96, 48, "NAND", size=15,
                      fill=GATEFILL, stroke=INK, sw=1.6, bold=True)

    # -- Рядок 1: ¬a = a | a --------------------------------------------------
    cy = 130
    f.append(text(64, cy + 5, "a", size=16, bold=True))
    f.append(line(80, cy, 150, cy))                 # головний дріт від a
    f.append(line(150, cy, 226, cy - 12))           # роздвоєння на два входи
    f.append(line(150, cy, 226, cy + 12))
    f.append(circle(150, cy, 3.2, fill=INK, stroke=INK))
    f.append(gate(274, cy))
    f.append(line(322, cy, 400, cy))
    f.append(text(420, cy + 5, "¬a", size=16, bold=True, color=FIELD, anchor="start"))
    f.append(text(560, cy + 5, "обидва входи = a", size=12.5, color=MUTED, anchor="start", italic=True))

    # -- Рядок 2: a ∧ b = (a|b) | (a|b) ---------------------------------------
    cy = 275
    f.append(text(64, cy - 13, "a", size=16, bold=True))
    f.append(text(64, cy + 19, "b", size=16, bold=True))
    f.append(line(80, cy - 15, 174, cy - 12))
    f.append(line(80, cy + 17, 174, cy + 12))
    f.append(gate(222, cy))                          # перший NAND → ¬(a∧b)
    f.append(line(270, cy, 344, cy))                 # спільний дріт t
    f.append(circle(344, cy, 3.2, fill=INK, stroke=INK))
    f.append(line(344, cy, 400, cy - 12))            # роздвоєння t на два входи
    f.append(line(344, cy, 400, cy + 12))
    f.append(gate(448, cy))                          # другий NAND як інвертор
    f.append(line(496, cy, 566, cy))
    f.append(text(586, cy + 5, "a ∧ b", size=16, bold=True, color=FIELD, anchor="start"))
    f.append(text(300, cy - 20, "¬(a∧b)", size=11.5, color=MUTED, italic=True))

    # -- Рядок 3: a ∨ b = (a|a) | (b|b) ---------------------------------------
    cyA, cyB, cyO = 388, 452, 420
    f.append(text(64, cyA + 5, "a", size=16, bold=True))
    f.append(text(64, cyB + 5, "b", size=16, bold=True))
    # a → перший NAND (обидва входи a)
    f.append(line(80, cyA, 128, cyA))
    f.append(circle(128, cyA, 3.2, fill=INK, stroke=INK))
    f.append(line(128, cyA, 176, cyA - 11))
    f.append(line(128, cyA, 176, cyA + 11))
    f.append(gate(224, cyA))
    # b → другий NAND (обидва входи b)
    f.append(line(80, cyB, 128, cyB))
    f.append(circle(128, cyB, 3.2, fill=INK, stroke=INK))
    f.append(line(128, cyB, 176, cyB - 11))
    f.append(line(128, cyB, 176, cyB + 11))
    f.append(gate(224, cyB))
    # обидва інверсні входи → третій NAND
    f.append(line(272, cyA, 400, cyO - 12))
    f.append(line(272, cyB, 400, cyO + 12))
    f.append(gate(448, cyO))
    f.append(line(496, cyO, 566, cyO))
    f.append(text(586, cyO + 5, "a ∨ b", size=16, bold=True, color=FIELD, anchor="start"))
    f.append(text(300, cyA - 16, "¬a", size=11.5, color=MUTED, italic=True))
    f.append(text(300, cyB + 20, "¬b", size=11.5, color=MUTED, italic=True))

    # підсумкова плашка
    by = 486
    f.append(rect(60, by, 740, 26, fill="#f1f8f3", stroke=FIELD, sw=1.4, rx=8))
    f.append(text(W / 2 - 10, by + 18,
                  "Маючи ¬, ∧ і ∨ — уже можна зібрати БУДЬ-ЯКУ логіку.",
                  size=12.5, bold=True))
    render(os.path.join(IMG, "nand-builds.svg"), W, H, *f)


# ── 2. Критерій Поста: матриця членства ──────────────────────────────────────
def fig_post_classes():
    W, H = 860, 588
    f = [text(W / 2, 30, "Критерій Поста: п'ять класів і хто до якого належить", size=18, bold=True),
         text(W / 2, 52, "зелене ∉ — операція ВИХОДИТЬ із класу (пробиває стіну);  сіре ∈ — застрягла в ньому",
              size=12, color=MUTED, italic=True)]

    cols = [(250, "T₀", "зберігає 0"),
            (350, "T₁", "зберігає 1"),
            (450, "M",  "монотонна"),
            (550, "S",  "самодвоїста"),
            (650, "L",  "лінійна"),
            (762, "сам?", "повний")]
    for cx, name, sub in cols:
        f.append(text(cx, 96, name, size=15, bold=True))
        f.append(text(cx, 114, sub, size=10, color=MUTED))
    f.append(line(50, 122, 812, 122, color=MUTED, sw=1.2))
    # роздільники
    f.append(line(212, 126, 212, 512, color="#e4e4e4", sw=1.2))
    f.append(line(708, 126, 708, 512, color="#e4e4e4", sw=1.2))

    # member[i] = True якщо операція В класі (застрягла); escape = not member
    rows = [
        ("0",        [True,  False, True,  False, True ], False),
        ("1",        [False, True,  True,  False, True ], False),
        ("¬",        [False, False, False, True,  True ], False),
        ("∧",        [True,  True,  True,  False, False], False),
        ("∨",        [True,  True,  True,  False, False], False),
        ("⊕",        [True,  False, False, False, True ], False),
        ("→",        [False, True,  False, False, False], False),
        ("|  (NAND)",[False, False, False, False, False], True),
        ("↓  (NOR)", [False, False, False, False, False], True),
    ]
    top, rh = 132, 42
    classx = [c[0] for c in cols[:5]]
    for i, (label, member, full) in enumerate(rows):
        y = top + i * rh
        cy = y + rh / 2
        if full:
            f.append(rect(50, y, 762, rh, fill="#eef8f0", stroke="none", sw=0, rx=0))
        elif i % 2 == 0:
            f.append(rect(50, y, 762, rh, fill=BAND, stroke="none", sw=0, rx=0))
        # підпис операції
        lc = FIELD if full else INK
        f.append(text(64, cy + 5, label, size=14.5, bold=True, color=lc, anchor="start"))
        # клітини-чіпи
        for k, cx in enumerate(classx):
            esc = not member[k]
            fill = GREENFILL if esc else GREYFILL
            f.append(rect(cx - 22, cy - 13, 44, 26, fill=fill, stroke="#d5dbe0", sw=1.0, rx=5))
            sym = "∉" if esc else "∈"
            f.append(text(cx, cy + 5, sym, size=15,
                          color=(FIELD if esc else MUTED), bold=esc))
        # вердикт «повний сам?»
        f.append(text(762, cy + 5, "так" if full else "—", size=14,
                      color=(FIELD if full else MUTED), bold=full, anchor="middle"))

    # плашка з правилом
    by = top + len(rows) * rh + 8
    f.append(rect(50, by, 762, 46, fill="#f1f8f3", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(W / 2, by + 20,
                  "Набір повний  ⟺  у КОЖНОМУ стовпці є хоч одна зелена клітина (хтось виходить із класу).",
                  size=12.5, bold=True))
    f.append(text(W / 2, by + 38,
                  "NAND і NOR зелені в усіх п'яти — тому кожен повний сам; у {∧, ∨} стовпці T₀, T₁, M геть сірі — тому неповний.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "post-classes.svg"), W, H, *f)


# ── 3. Історія: чотири відкриття — чотири долі ───────────────────────────────
def fig_hist_timeline():
    W, H = 1000, 610
    f = [text(W / 2, 32, "Одну й ту саму річ відкрили чотири рази — і кожен раз по-своєму загубили",
              size=17, bold=True),
         text(W / 2, 54, "рік · хто · що зробив · що з того вийшло",
              size=12, color=MUTED, italic=True)]

    LOST = ("#fdecea", POS)      # знахідка не дійшла до людей
    NEUT = ("#eef0f2", MUTED)    # дійшла, та скалічена
    PASS = ("#e7f6ec", FIELD)    # знахідка таки пішла далі

    # заголовки стовпців
    f.append(text(80, 92, "рік", size=11, color=MUTED))
    f.append(text(140, 92, "хто", size=11, color=MUTED, anchor="start"))
    f.append(text(365, 92, "що зробив", size=11, color=MUTED, anchor="start"))
    f.append(text(845, 92, "доля знахідки", size=11, color=MUTED))
    f.append(line(40, 100, 960, 100, color=MUTED, sw=1.2))

    rows = [
        ("1880", "Ч. С. Пірс",        "знайшов: NAND і NOR повні поодинці",   "написав — і поховав",       LOST),
        ("1911", "Е. Б. Стамм",       "перший НАДРУКУВАВ доведення повноти",  "надруковано — не почуто",   LOST),
        ("1913", "Г. М. Шеффер",      "штрих = «ні p, ні q», тобто NOR",      "прославлено не за те",      NEUT),
        ("1917", "Ж. Нікод",          "перечитав штрих як NAND; одна аксіома", "дав робочу нотацію",       PASS),
        ("1925", "Б. Расселл",        "штрих у 2-му виданні Principia",       "увімкнув мережу слави",     PASS),
        ("1926", "Гарвард",           "MS 378 Пірса з биркою «на викид»",     "врятовано випадково",       LOST),
        ("1933", "Collected Papers",  "рукопис Пірса нарешті надруковано",    "запізно на 53 роки",        NEUT),
        ("1941", "Е. Л. Пост",        "класифікував УСІ замкнені класи",      "видано — нечитабельно",     NEUT),
        ("1990", "Мартін і Пеллетьє", "переписали доведення сучасно",         "прочитано через 49 років",  PASS),
    ]
    top, rh = 108, 52
    for i, (year, who, deed, fate, (cfill, cstroke)) in enumerate(rows):
        y = top + i * rh
        cy = y + rh / 2
        if i % 2 == 1:
            f.append(rect(40, y, 920, rh, fill=BAND, stroke="none", sw=0, rx=0))
        f.append(text(80, cy + 5, year, size=14, bold=True, color=INK))
        f.append(text(140, cy + 5, who, size=13, bold=True, anchor="start"))
        f.append(text(365, cy + 5, deed, size=12, color=INK, anchor="start"))
        f.append(fitbox(720, cy - 16, 250, 32, fate, size=11.5,
                        fill=cfill, stroke=cstroke, sw=1.4, rx=8,
                        color=cstroke, bold=True))

    by = top + len(rows) * rh + 8
    f.append(rect(40, by, 920, 26, fill="#f1f8f3", stroke=FIELD, sw=1.4, rx=8))
    f.append(text(W / 2, by + 18,
                  "Знахідку робить надбанням не першість, а те, чи є їй кому передатися.",
                  size=12.5, bold=True))
    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


# ── 4. Підміна імен: чий штрих і чия стрілка ─────────────────────────────────
def fig_hist_name_swap():
    W, H = 940, 540
    f = [text(W / 2, 30, "«Штрих Шеффера» — не те, що означив Шеффер", size=18, bold=True),
         text(W / 2, 52, "ліворуч — головний текст його статті 1913 року; праворуч — те, що ми звемо його іменем",
              size=12, color=MUTED, italic=True)]

    def panel(x, head, quote, op, today, accent):
        g = rect(x, 80, 420, 344, fill="#ffffff", stroke=accent, sw=1.8, rx=12)
        g += fitbox(x + 12, 92, 396, 34, head, size=12.5,
                    fill="#f4f6f8", stroke="none", sw=0, rx=7, color=MUTED, bold=True)
        g += fitbox(x + 12, 140, 396, 58, quote, size=12.5,
                    fill=FILL, stroke="#d5dbe0", sw=1.2, rx=8)
        g += arrow(x + 210, 206, x + 210, 242)
        g += fitbox(x + 12, 250, 396, 48, op, size=15,
                    fill="#eef3fb", stroke=INK, sw=1.6, rx=8, bold=True)
        g += arrow(x + 210, 304, x + 210, 340)
        g += fitbox(x + 12, 348, 396, 62, today, size=13,
                    fill=("#e7f6ec" if accent == FIELD else "#fdecea"),
                    stroke=accent, sw=1.6, rx=8, color=accent, bold=True)
        return g

    f.append(panel(30,
                   "Що Шеффер СПРАВДІ означив (§2 статті)",
                   "«p | q можна тлумачити як\nсудження ні p, ні q»",
                   "¬(a ∨ b)   —   це NOR",
                   "сьогодні цю дію звуть\nСТРІЛКА ПІРСА   ↓",
                   POS))
    f.append(panel(490,
                   "Що вжив Нікод (1917), читаючи зноску",
                   "«не обидва» — дія, на яку\nШеффер лише натякнув у зносці",
                   "¬(a ∧ b)   —   це NAND",
                   "сьогодні цю дію звуть\nШТРИХ ШЕФФЕРА   |",
                   FIELD))

    f.append(rect(30, 444, 880, 66, fill="#f1f8f3", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(W / 2, 468,
                  "Те, що Шеффер означив, носить ім'я Пірса. Те, що зветься його штрихом, вжив Нікод.",
                  size=13, bold=True))
    f.append(text(W / 2, 492,
                  "А обидві дії знайшов Пірс іще 1880-го (мовчки), і першим надрукував Стамм 1911-го (непочутим).",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "hist-name-swap.svg"), W, H, *f)


# ── 5. П'ять стін — лише верхній ярус мапи Поста ─────────────────────────────
def fig_hist_post_lattice():
    W, H = 980, 540
    f = [text(W / 2, 30, "П'ять стін — це лише верхівка того, що зробив Пост", size=18, bold=True),
         text(W / 2, 52, "він описав УСІ замкнені класи булевих функцій; критерій повноти — наслідок",
              size=12, color=MUTED, italic=True)]

    TOPY, CLSY, BOTY = 108, 196, 452
    cx = 330

    # верхній вузол — усе
    f.append(fitbox(cx - 120, TOPY, 240, 40, "УСІ булеві функції", size=13.5,
                    fill="#eef3fb", stroke=INK, sw=1.8, rx=9, bold=True))

    # п'ять максимальних класів
    classes = [(110, "T₀", "зберігає 0"), (225, "T₁", "зберігає 1"), (340, "M", "монотонні"),
               (455, "S", "самодвоїсті"), (570, "L", "лінійні")]
    for x, name, sub in classes:
        f.append(line(cx, TOPY + 40, x, CLSY, color=MUTED, sw=1.2))
        f.append(fitbox(x - 52, CLSY, 104, 42, name + "\n" + sub, size=11,
                        fill="#e7f6ec", stroke=FIELD, sw=1.6, rx=8, bold=True))

    # нижче — зліченна безодня перетинів (без підписів, щоб не заважати)
    tiers = [(268, [150, 240, 330, 420, 510]),
             (322, [195, 275, 355, 435]),
             (376, [255, 330, 405])]
    prev = [x for x, _, _ in classes]
    for ty, xs in tiers:
        for x in xs:
            for px in prev:
                if abs(px - x) < 95:
                    f.append(line(px, ty - 12, x, ty - 4, color="#d5dbe0", sw=1.0))
            f.append(circle(x, ty, 7, fill=FILL, stroke=MUTED, sw=1.3))
        prev = xs
    f.append(text(cx, 414, "⋮", size=22, color=MUTED))

    f.append(fitbox(cx - 130, BOTY, 260, 40, "проєкції (нічого не будують)", size=11.5,
                    fill="#eef0f2", stroke=MUTED, sw=1.4, rx=9, color=MUTED))
    f.append(line(cx, 424, cx, BOTY, color="#d5dbe0", sw=1.0))

    # пояснювальна панель праворуч
    px0 = 660
    f.append(rect(px0, 100, 290, 300, fill="#ffffff", stroke=FIELD, sw=1.8, rx=12))
    f.append(fitbox(px0 + 12, 112, 266, 32, "Що насправді довів Пост", size=13,
                    fill="#f1f8f3", stroke="none", sw=0, rx=7, color=FIELD, bold=True))
    f.append(mtext(px0 + 16, 172,
                   ["Він перелічив УСІ класи функцій,",
                    "замкнені відносно сполучення —",
                    "їх зліченно багато, і кожен має",
                    "скінченний базис. Ця мапа зветься",
                    "решіткою Поста."],
                   size=11.5, color=INK, anchor="start", lh=1.45))
    f.append(line(px0 + 16, 268, px0 + 274, 268, color="#e4e4e4", sw=1.2))
    f.append(mtext(px0 + 16, 292,
                   ["Критерій повноти — просто наслідок:",
                    "п'ять зелених вузлів — це рівно всі",
                    "МАКСИМАЛЬНІ класи. Не влізти в",
                    "жоден із них = збудувати все."],
                   size=11.5, color=INK, anchor="start", lh=1.45))

    f.append(rect(px0, 416, 290, 76, fill=FILL, stroke="#d5dbe0", sw=1.2, rx=10))
    f.append(mtext(px0 + 16, 440,
                   ["Annals of Mathematics Studies № 5,",
                    "Princeton, 1941, 122 с. — літографія",
                    "з машинопису, у власній нотації."],
                   size=10.5, color=MUTED, anchor="start", lh=1.5))

    render(os.path.join(IMG, "hist-post-lattice.svg"), W, H, *f)


# ── 6. Матем.: конвеєр доведення достатності ─────────────────────────────────
def fig_math_proof_map():
    W, H = 900, 730
    BOXFILL = "#eef3fb"
    OKFILL  = "#eef8f0"
    f = [text(W / 2, 32, "Як із п'яти «утікачів» механічно скласти ¬ і ∧", size=18, bold=True),
         text(W / 2, 54, "доведення достатності — конвеєр із чотирьох лем: що дано → що з цього збирається",
              size=12.5, color=MUTED, italic=True)]

    # Дано
    f.append(fitbox(150, 78, 600, 40, "Дано: f₀ ∉ T₀,   f₁ ∉ T₁,   f_M ∉ M,   f_S ∉ S,   f_L ∉ L",
                    size=14, bold=True, fill=FILL, stroke="#c9ced4", sw=1.4, rx=10))
    f.append(arrow(450, 118, 450, 142))

    # Лема 1
    f.append(fitbox(280, 144, 340, 76,
                    ["Лема 1 · діагональ  f(x, x, …, x)",
                     "вхід:  f₀ ∉ T₀  і  f₁ ∉ T₁",
                     "вихід:  ¬   АБО   обидві константи 0 і 1"],
                    size=13, fill=BOXFILL, stroke="#9fb4d4", sw=1.6, rx=10))

    # Розгалуження
    f.append(arrow(450, 220, 260, 250))
    f.append(arrow(450, 220, 640, 250))
    f.append(fitbox(60, 252, 300, 48, ["випадок A", "маємо 0 і 1, ¬ ще нема"],
                    size=12.5, fill=FILL, stroke="#c9ced4", sw=1.4, rx=10))
    f.append(fitbox(540, 252, 300, 48, ["випадок Б", "маємо ¬, констант ще нема"],
                    size=12.5, fill=FILL, stroke="#c9ced4", sw=1.4, rx=10))
    f.append(arrow(210, 300, 210, 336))
    f.append(arrow(690, 300, 690, 336))

    # Леми 2 і 3
    f.append(fitbox(60, 338, 300, 76,
                    ["Лема 2 · ланцюг у кубі",
                     "вхід:  f_M ∉ M  +  константи",
                     "вихід:  ¬"],
                    size=12.5, fill=BOXFILL, stroke="#9fb4d4", sw=1.6, rx=10))
    f.append(fitbox(540, 338, 300, 76,
                    ["Лема 3 · підстановка за вектором",
                     "вхід:  f_S ∉ S  +  ¬",
                     "вихід:  константа (а з ¬ — обидві)"],
                    size=12.5, fill=BOXFILL, stroke="#9fb4d4", sw=1.6, rx=10))

    # Злиття
    f.append(arrow(210, 414, 370, 452))
    f.append(arrow(690, 414, 530, 452))
    f.append(fitbox(280, 454, 340, 46, "У БУДЬ-ЯКОМУ разі маємо   ¬,   0,   1",
                    size=14, bold=True, color=FIELD, fill=OKFILL, stroke=FIELD, sw=1.8, rx=10))
    f.append(arrow(450, 500, 450, 538))

    # Лема 4
    f.append(fitbox(280, 540, 340, 76,
                    ["Лема 4 · розчеплення полінома",
                     "вхід:  f_L ∉ L  +  ¬  +  константи",
                     "вихід:  ∧"],
                    size=12.5, fill=BOXFILL, stroke="#9fb4d4", sw=1.6, rx=10))
    f.append(arrow(450, 616, 450, 648))

    # Результат
    f.append(fitbox(210, 650, 480, 58,
                    ["{¬, ∧} — а це вже все: сума добутків",
                     "дає БУДЬ-ЯКУ булеву функцію.   [F] = P₂"],
                    size=13.5, bold=True, color=FIELD, fill=OKFILL, stroke=FIELD, sw=1.8, rx=10))
    render(os.path.join(IMG, "math-proof-map.svg"), W, H, *f)


# ── 7. Матем.: ланцюг у кубі (лема про немонотонність) ───────────────────────
def fig_math_monotone_chain():
    W, H = 900, 570
    R = 28
    TBL = {(0, 0, 0): 1, (0, 0, 1): 1, (0, 1, 0): 0, (0, 1, 1): 1,
           (1, 0, 0): 1, (1, 0, 1): 0, (1, 1, 0): 0, (1, 1, 1): 0}
    P = {(0, 0, 0): (300, 440),
         (1, 0, 0): (170, 350), (0, 1, 0): (300, 350), (0, 0, 1): (430, 350),
         (1, 1, 0): (170, 250), (1, 0, 1): (300, 250), (0, 1, 1): (430, 250),
         (1, 1, 1): (300, 160)}
    EDGES = [((0,0,0),(1,0,0)), ((0,0,0),(0,1,0)), ((0,0,0),(0,0,1)),
             ((1,0,0),(1,1,0)), ((1,0,0),(1,0,1)),
             ((0,1,0),(1,1,0)), ((0,1,0),(0,1,1)),
             ((0,0,1),(1,0,1)), ((0,0,1),(0,1,1)),
             ((1,1,0),(1,1,1)), ((1,0,1),(1,1,1)), ((0,1,1),(1,1,1))]

    def seg(a, b, color="#ccd2d8", sw=1.6):
        (x1, y1), (x2, y2) = P[a], P[b]
        dx, dy = x2 - x1, y2 - y1
        d = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / d, dy / d
        return line(x1 + ux * (R + 2), y1 + uy * (R + 2),
                    x2 - ux * (R + 2), y2 - uy * (R + 2), color=color, sw=sw)

    f = [text(W / 2, 30, "Лема 2: як немонотонність перетворюється на ¬", size=18, bold=True),
         text(W / 2, 52, "куб усіх входів; ребро вгору = підняти один біт з 0 на 1; f задано таблицею",
              size=12.5, color=MUTED, italic=True)]

    chain = [((0,0,0),(1,0,0)), ((1,1,0),(1,1,1))]
    drop  = ((1,0,0), (1,1,0))
    for a, b in EDGES:
        if (a, b) in chain or (a, b) == drop:
            continue
        f.append(seg(a, b))
    for a, b in chain:
        f.append(seg(a, b, color=NEG, sw=3.4))
    f.append(seg(*drop, color=POS, sw=4))

    for v, pos in P.items():
        val = TBL[v]
        f.append(circle(pos[0], pos[1], R,
                        fill=("#e7f6ec" if val else "#eef0f2"),
                        stroke=(FIELD if val else "#9aa3ab"), sw=1.8))
        f.append(text(pos[0], pos[1] - 3, "".join(str(x) for x in v), size=12, bold=True))
        f.append(text(pos[0], pos[1] + 14, "f=%d" % val, size=10, color=MUTED))

    f.append(text(300, 118, "β = (1,1,1),   f(β) = 0", size=12.5, bold=True))
    f.append(text(300, 500, "α = (0,0,0),   f(α) = 1", size=12.5, bold=True))
    f.append(text(126, 302, "1 падає на 0", size=11.5, color=POS, bold=True, anchor="end"))

    # Панель праворуч
    f.append(rect(566, 150, 312, 300, fill=FILL, stroke="#d5dbe0", sw=1.4, rx=10))
    f.append(mtext(584, 180,
                   ["α ≤ β, а f(α) = 1 > 0 = f(β):",
                    "монотонність порушено — але",
                    "α і β різняться аж у трьох бітах."],
                   size=11.5, color=INK, anchor="start", lh=1.5))
    f.append(line(584, 240, 860, 240, color="#e4e4e4", sw=1.2))
    f.append(mtext(584, 266,
                   ["Ідемо ланцюгом, по одному біту:",
                    "000 → 100 → 110 → 111",
                    "f :    1  →  1  →  0  →  0",
                    "Десь 1 мусить упасти на 0 —",
                    "тут на ребрі 100 → 110.",
                    "Ці сусіди різняться ЛИШЕ в b."],
                   size=11.5, color=INK, anchor="start", lh=1.5))
    f.append(line(584, 376, 860, 376, color="#e4e4e4", sw=1.2))
    f.append(mtext(584, 400,
                   ["Заморозимо решту константами:",
                    "φ(x) = f(1, x, 0)",
                    "φ(0) = 1,   φ(1) = 0   ⟹   φ = ¬"],
                   size=11.5, color=FIELD, anchor="start", lh=1.6, bold=True))

    f.append(text(W / 2, 540,
                  "Будь-який інший ланцюг від α до β теж дав би ¬: падіння мусить статися десь, бо кінці різні.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "math-monotone-chain.svg"), W, H, *f)


# ── 8. Матем.: жодну стіну не викинеш ────────────────────────────────────────
def fig_math_no_wall_drops():
    W, H = 880, 448
    REDFILL = "#fdecea"
    f = [text(W / 2, 30, "Жодну з п'яти перевірок не викинеш", size=18, bold=True),
         text(W / 2, 52, "кожен набір проходить ЧОТИРИ стіни з п'яти — і все одно неповний; червона клітина і є причина",
              size=12, color=MUTED, italic=True)]

    cols = [(330, "T₀", "зберігає 0"),
            (420, "T₁", "зберігає 1"),
            (510, "M",  "монотонні"),
            (600, "S",  "самодвоїсті"),
            (690, "L",  "лінійні")]
    for cx, name, sub in cols:
        f.append(text(cx, 96, name, size=15, bold=True))
        f.append(text(cx, 114, sub, size=9.5, color=MUTED))
    f.append(text(790, 96, "повний?", size=13, bold=True))
    f.append(line(46, 124, 834, 124, color=MUTED, sw=1.2))
    f.append(line(300, 128, 300, 356, color="#e4e4e4", sw=1.2))
    f.append(line(740, 128, 740, 356, color="#e4e4e4", sw=1.2))

    rows = [
        ("{¬a ∧ b}",  "«b, і не a»",          0),
        ("{a → b}",   "імплікація",           1),
        ("{0, 1, ∧}", "константи + «і»",      2),
        ("{¬, maj}",  "«не» + більшість трьох", 3),
        ("{¬, ⊕}",    "«не» + XOR",           4),
    ]
    top, rh = 130, 45
    for i, (label, hint, trapped) in enumerate(rows):
        y = top + i * rh
        cy = y + rh / 2
        if i % 2 == 0:
            f.append(rect(46, y, 788, rh, fill=BAND, stroke="none", sw=0, rx=0))
        f.append(text(60, cy - 3, label, size=14, bold=True, anchor="start"))
        f.append(text(60, cy + 14, hint, size=10, color=MUTED, anchor="start", italic=True))
        for k, (cx, _, _) in enumerate(cols):
            stuck = (k == trapped)
            f.append(rect(cx - 22, cy - 13, 44, 26,
                          fill=(REDFILL if stuck else GREENFILL),
                          stroke=("#e8b4ae" if stuck else "#c6e3d0"), sw=1.0, rx=5))
            f.append(text(cx, cy + 5, "∈" if stuck else "∉", size=15,
                          color=(POS if stuck else FIELD), bold=True))
        f.append(text(790, cy + 5, "НІ", size=13.5, color=POS, bold=True))

    by = top + len(rows) * rh + 10
    f.append(rect(46, by, 788, 52, fill="#f1f8f3", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(W / 2, by + 21,
                  "Кожен рядок — набір, що застряг РІВНО в одній стіні: чотири перевірки він проходить, п'яту — ні.",
                  size=12, bold=True))
    f.append(text(W / 2, by + 40,
                  "Викинь із критерію будь-яку стіну — і саме цей набір він оголосить повним. Помилково.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "math-no-wall-drops.svg"), W, H, *f)


# ── 9. proj: метелик Мебіуса — поліном Жегалкіна за O(n·2ⁿ) ──────────────────
def fig_proj_mobius_butterfly():
    W, H = 940, 616
    f = [text(W / 2, 32, "Метелик Мебіуса: з таблиці — поліном Жегалкіна", size=18, bold=True),
         text(W / 2, 54, "f = a ∨ (b ∧ c);  на кожному кроці ВЕРХНЯ клітина пари приймає ⊕ нижньої",
              size=12.5, color=MUTED, italic=True)]

    CW, GAP, CH, X0 = 48, 8, 40, 150
    ROWS = [(122, "таблиця", [0, 1, 0, 1, 0, 1, 1, 1], None),
            (222, "крок 1",  [0, 1, 0, 1, 0, 1, 1, 0], 1),
            (322, "крок 2",  [0, 1, 0, 0, 0, 1, 1, 1], 2),
            (422, "крок 4",  [0, 1, 0, 0, 0, 0, 1, 1], 4)]
    cx = lambda i: X0 + i * (CW + GAP)

    for i in range(8):
        f.append(text(cx(i) + CW / 2, 108, "x=" + str(i), size=11, color=MUTED))

    # стрілки-метелики — у проміжках між рядками, повз усі написи
    for r in range(1, 4):
        y_from, step = ROWS[r - 1][0] + CH + 6, ROWS[r][3]
        y_to = ROWS[r][0] - 8
        for base in range(0, 8, 2 * step):
            for j in range(base, base + step):
                f.append(arrow(cx(j) + CW / 2, y_from, cx(j + step) + CW / 2, y_to,
                               color="#9aa4ae", sw=1.3))

    prev = None
    for y, label, vals, step in ROWS:
        if step:
            f.append(text(132, y + 17, label, size=12.5, bold=True, color=MUTED, anchor="end"))
            f.append(text(132, y + 35, "a[j+%d] ^= a[j]" % step, size=10.5,
                          color=MUTED, anchor="end", italic=True))
        else:
            f.append(text(132, y + CH / 2 + 5, label, size=12.5, bold=True, color=MUTED, anchor="end"))
        for i, v in enumerate(vals):
            changed = prev is not None and prev[i] != v
            f.append(rect(cx(i), y, CW, CH, fill=("#fdecea" if changed else GREYFILL),
                          stroke=(POS if changed else "#d5dbe0"), sw=(1.8 if changed else 1.0), rx=5))
            f.append(text(cx(i) + CW / 2, y + CH / 2 + 6, str(v), size=16, bold=True,
                          color=(POS if changed else INK)))
        prev = vals

    # який одночлен стоїть у кожній клітині
    MONO = ["1", "a", "b", "ab", "c", "ac", "bc", "abc"]
    anf = ROWS[-1][2]
    for i, m in enumerate(MONO):
        f.append(text(cx(i) + CW / 2, 486, m, size=13, bold=bool(anf[i]),
                      color=(FIELD if anf[i] else MUTED)))
    f.append(text(132, 486, "одночлен", size=12, color=MUTED, anchor="end", italic=True))

    f.append(rect(150, 508, 430, 34, fill="#eef8f0", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(365, 530, "лишилися одиниці при  a,  bc,  abc", size=13, bold=True, color=FIELD))
    f.append(rect(150, 552, 660, 34, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    f.append(text(480, 574, "f = a ⊕ bc ⊕ abc  —  є одночлени з ДОБУТКОМ змінних → функція НЕ лінійна",
                  size=13, bold=True, color=POS))

    px = 640
    f.append(rect(px, 122, 280, 216, fill="#ffffff", stroke=FIELD, sw=1.8, rx=12))
    f.append(fitbox(px + 12, 134, 256, 30, "Чому це швидко", size=12.5,
                    fill="#f1f8f3", stroke="none", sw=0, rx=7, color=FIELD, bold=True))
    f.append(mtext(px + 16, 190,
                   ["Кроки 1, 2, 4 — це log₂8 = 3",
                    "проходи по 8 клітинах.",
                    "Разом n · 2ⁿ дій, на місці,",
                    "без краплі зайвої памʼяті.",
                    "Наївне розкриття дужок",
                    "коштувало б 2ⁿ доданків",
                    "на КОЖЕН одиничний рядок."],
                   size=11.5, color=INK, anchor="start", lh=1.5))
    f.append(rect(px, 354, 280, 116, fill=FILL, stroke="#d5dbe0", sw=1.2, rx=10))
    f.append(text(px + 16, 380, "Клітина ↔ одночлен", size=12, color=MUTED,
                  anchor="start", bold=True))
    f.append(mtext(px + 16, 410,
                   ["Номер клітини, читаний як",
                    "набір бітів, І Є набором",
                    "змінних одночлена:",
                    "6 = 110₂ = {b, c} → bc."],
                   size=11.5, color=INK, anchor="start", lh=1.5))

    render(os.path.join(IMG, "proj-mobius-butterfly.svg"), W, H, *f)


# ── 10. proj: самодвоїстість — таблиця проти свого дзеркала ──────────────────
def fig_proj_selfdual_mirror():
    W, H = 980, 452
    f = [text(W / 2, 32, "Самодвоїстість: таблицю звіряють із власним дзеркалом", size=18, bold=True),
         text(W / 2, 54, "дзеркало — та сама таблиця, читана з кінця: клітина x проти клітини ¬x",
              size=12.5, color=MUTED, italic=True)]

    CW, GAP, CH = 38, 5, 32

    def panel(px, head, vals, verdict, ok):
        g = rect(px, 78, 460, 300, fill="#ffffff", stroke=(FIELD if ok else POS), sw=1.8, rx=12)
        g += fitbox(px + 14, 90, 432, 30, head, size=12.5,
                    fill=("#f1f8f3" if ok else "#fdecea"), stroke="none", sw=0, rx=7,
                    color=(FIELD if ok else POS), bold=True)
        x0 = px + 118
        cx = lambda i: x0 + i * (CW + GAP)
        for i in range(8):
            g += text(cx(i) + CW / 2, 146, str(i), size=10.5, color=MUTED)
        rev = vals[::-1]
        for j, (lab, row) in enumerate((("f(x)", vals), ("f(¬x)", rev))):
            y = 156 + j * 44
            g += text(px + 106, y + CH / 2 + 5, lab, size=12, bold=True, color=INK, anchor="end")
            for i, v in enumerate(row):
                g += rect(cx(i), y, CW, CH, fill=GREYFILL, stroke="#d5dbe0", sw=1.0, rx=4)
                g += text(cx(i) + CW / 2, y + CH / 2 + 5, str(v), size=14, bold=True)
        g += text(px + 106, 262, "різні?", size=12, color=MUTED, anchor="end", italic=True)
        for i in range(8):
            diff = vals[i] != rev[i]
            g += text(cx(i) + CW / 2, 262, "так" if diff else "ні", size=11.5, bold=True,
                      color=(FIELD if diff else POS))
        g += text(px + 240, 296, "одиниць — рівно 4 з 8", size=12, color=MUTED, italic=True)
        g += fitbox(px + 14, 314, 432, 50, verdict, size=12.5,
                    fill=("#eef8f0" if ok else "#fdecea"), stroke=(FIELD if ok else POS),
                    sw=1.6, rx=8, color=(FIELD if ok else POS), bold=True)
        return g

    f.append(panel(20, "MAJ(a, b, c) — більшість голосів",
                   [0, 0, 0, 1, 0, 1, 1, 1],
                   "усі вісім стовпців різні\nсамодвоїста — застрягла в класі S", True))
    f.append(panel(500, "a ⊕ b   (вхід c — фіктивний)",
                   [0, 1, 1, 0, 0, 1, 1, 0],
                   "дзеркало збіглося саме з собою\nне самодвоїста — виходить із класу S", False))

    by = 396
    f.append(rect(20, by, 940, 40, fill="#f1f8f3", stroke=FIELD, sw=1.4, rx=9))
    f.append(text(W / 2, by + 25,
                  "Обидві збалансовані порівну — та лише в лівої дзеркало ВСЮДИ інше. Баланс необхідний, але його не досить.",
                  size=12.5, bold=True))
    render(os.path.join(IMG, "proj-selfdual-mirror.svg"), W, H, *f)


if __name__ == "__main__":
    fig_nand_builds()
    fig_post_classes()
    fig_hist_timeline()
    fig_hist_name_swap()
    fig_hist_post_lattice()
    fig_math_proof_map()
    fig_math_monotone_chain()
    fig_math_no_wall_drops()
    fig_proj_mobius_butterfly()
    fig_proj_selfdual_mirror()
    print("OK: 10 figures ->", IMG)
