# -*- coding: utf-8 -*-
"""Фігури до кроку «Дедуп, злиття й throttling сповіщень».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
У самих SVG уникаємо кольорових емодзі (не всюди рендеряться): лише ✓ · ! ①②③ і фігури."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREENBG = "#eafaf0"
REDBG   = "#fdecea"
BLUEBG  = "#eaf0fd"
GREY    = "#e5e7eb"


# ───────── Фіг. 1: три фільтри + пріоритетний обхід ─────────
def fig_three_filters():
    W, H = 1200, 560
    f = []

    # пріоритетна смуга зверху — оминає все
    f.append(fitbox(60, 50, 1080, 46,
                    "Критичний клас (дим · злом · протікання) — оминає всі три фільтри, доставляємо негайно",
                    size=14, fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=2))

    # вхід
    f.append(fitbox(50, 180, 250, 156,
                    "Вхід: 43 події / 3 с\n40× пристрій офлайн\n(Wi-Fi моргнув)\n2 дублі «двері»\n1 критична: дим",
                    size=13, fill=FILL, stroke=INK, color=INK, sw=1.6))

    # три фільтри в ряд
    f.append(arrow(302, 258, 350, 258, color=MUTED, sw=1.8))
    f.append(fitbox(355, 202, 200, 112, "① ДЕДУП\nтой самий ключ — раз",
                    size=14, fill=FILL, stroke=NEG, color=NEG, bold=True, sw=1.8))

    f.append(arrow(557, 258, 605, 258, color=MUTED, sw=1.8))
    f.append(text(581, 240, "−2 дублі", size=11, color=MUTED))
    f.append(fitbox(610, 202, 200, 112, "② ЗЛИТТЯ\nспільна тема —\nдайджест",
                    size=14, fill=FILL, stroke=FIELD, color=FIELD, bold=True, sw=1.8))

    f.append(arrow(812, 258, 860, 258, color=MUTED, sw=1.8))
    f.append(text(836, 240, "буря → 1", size=11, color=MUTED))
    f.append(fitbox(865, 202, 210, 112, "③ THROTTLING\nне частіше\nза бюджет",
                    size=14, fill=FILL, stroke=POS, color=POS, bold=True, sw=1.8))

    # вниз до виходу
    f.append(arrow(970, 314, 970, 384, color=MUTED, sw=1.8))
    f.append(text(992, 356, "2 ✓", size=12, color=FIELD, anchor="start", bold=True))

    # вихід
    f.append(fitbox(300, 392, 800, 100,
                    "Вихід:\n✓ 1 дайджест: «40 пристроїв офлайн»\n"
                    "✓ критична (дим) — негайно, в обхід\n→ телефон дзинькнув 2 рази замість 82",
                    size=14, fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=2))

    render(os.path.join(IMG, "three-filters.svg"), W, H, *f,
           title="Три сита, одне питання — чи вартий сигнал уваги зараз")


# ───────── Фіг. 2: трейд-оф вікна злиття ─────────
def fig_coalesce_window():
    W, H = 1080, 478
    f = []

    ticks = [160, 235, 315, 435, 605, 790]

    # ── панель А: без вікна ──
    f.append(text(120, 74, "Без вікна (W = 0): кожна подія — окреме сповіщення",
                  size=14, bold=True, color=POS, anchor="start"))
    f.append(line(120, 162, 820, 162, color=MUTED, sw=1.4))
    for x in ticks:
        f.append(circle(x, 162, 5, fill=INK, stroke=INK, sw=1))
        f.append(circle(x, 126, 8, fill=REDBG, stroke=POS, sw=2))     # «пінг» = переривання
        f.append(line(x, 134, x, 157, color=POS, sw=1, dash="3,3"))
    f.append(fitbox(852, 110, 196, 46, "6 переривань\nзатримка 0",
                    size=12, fill=REDBG, stroke=POS, color=POS, bold=True, sw=1.8))
    f.append(text(470, 190, "6 подій «пристрій офлайн» за 58 с", size=12, color=MUTED))

    # ── панель Б: вікно 60 с ──
    f.append(text(120, 256, "Вікно W = 60 с: усе за вікно — один дайджест",
                  size=14, bold=True, color=FIELD, anchor="start"))
    f.append(line(120, 344, 820, 344, color=MUTED, sw=1.4))
    for x in ticks:
        f.append(circle(x, 344, 5, fill=FIELD, stroke=FIELD, sw=1))
    # дужка-вікно над подіями
    f.append(line(150, 308, 800, 308, color=FIELD, sw=2))
    f.append(line(150, 308, 150, 326, color=FIELD, sw=2))
    f.append(line(800, 308, 800, 326, color=FIELD, sw=2))
    f.append(text(410, 300, "вікно 60 с — збираємо", size=12, color=FIELD))
    f.append(fitbox(852, 320, 196, 48, "1 дайджест:\n«40 офлайн»",
                    size=12, fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=1.8))
    f.append(text(410, 372, "1 переривання · затримка до 60 с", size=12, color=MUTED))

    # банер-теза
    f.append(fitbox(90, 420, 900, 42,
                    "Довше вікно — менше переривань, пізніша новина. Критичне не чекає: W = 0.",
                    size=14, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))

    render(os.path.join(IMG, "coalesce-window.svg"), W, H, *f,
           title="Вікно злиття: прямий обмін затримки на спокій")


# ───────── Фіг. 3: token bucket ─────────
def fig_token_bucket():
    W, H = 1060, 500
    f = []

    # відро
    f.append(rect(400, 150, 200, 230, fill=FILL, stroke=INK, sw=2, rx=8))

    # приплив зверху
    f.append(arrow(500, 82, 500, 148, color=NEG, sw=2.4))
    f.append(text(500, 68, "r жетонів/хв — усталений темп доливання", size=13, color=NEG))

    # межа місткості
    f.append(line(400, 176, 600, 176, color=MUTED, sw=1.4, dash="6,4"))
    f.append(text(620, 181, "b — місткість (сплеск до b поспіль)",
                  size=12, color=MUTED, anchor="start"))

    # жетони на дні
    for cx, cy in [(442, 352), (478, 358), (512, 350), (548, 358), (578, 351)]:
        f.append(circle(cx, cy, 10, fill=GREENBG, stroke=FIELD, sw=2))
    f.append(text(500, 326, "жетони", size=12, color=FIELD, bold=True))

    # вхідне сповіщення ліворуч
    f.append(fitbox(60, 250, 176, 46, "сповіщення\nприходить",
                    size=13, fill=FILL, stroke=MUTED, color=INK, sw=1.4))
    f.append(arrow(240, 273, 396, 300, color=MUTED, sw=1.8))

    # два наслідки праворуч
    f.append(arrow(602, 250, 700, 250, color=FIELD, sw=1.8))
    f.append(fitbox(704, 226, 300, 48, "є жетон → пропустити\n(списати 1)",
                    size=13, fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=1.8))
    f.append(arrow(602, 340, 700, 340, color=POS, sw=1.8))
    f.append(fitbox(704, 314, 300, 62, "порожньо → притримати /\nзлити в дайджест / відкинути",
                    size=13, fill=REDBG, stroke=POS, color=POS, bold=True, sw=1.8))

    # банер
    f.append(fitbox(60, 440, 940, 46,
                    "Сплеск до b поспіль дозволено; надовго темп не більший за r. "
                    "Leaky bucket — рідший брат: випускає рівно по краплі, згладжуючи навіть сплеск.",
                    size=13, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))

    render(os.path.join(IMG, "token-bucket.svg"), W, H, *f,
           title="Відро жетонів: сплеск до b, усталено — не швидше за r")


# ───────── Фіг. 4 (вставка hist): один урок, три домени ─────────
def fig_alarm_lineage():
    W, H = 1240, 620
    f = []

    # спинний хребет часу
    f.append(line(90, 308, 1150, 308, color=MUTED, sw=2))
    nodes = [280, 620, 960]
    for x in nodes:
        f.append(circle(x, 308, 13, fill=BG, stroke=INK, sw=2.4))

    # стрілки «урок їде вперед» по хребту
    f.append(arrow(300, 308, 598, 308, color=INK, sw=2))
    f.append(arrow(642, 308, 938, 308, color=INK, sw=2))
    f.append(text(450, 299, "той самий урок", size=12, color=MUTED))
    f.append(text(790, 299, "той самий урок", size=12, color=MUTED))

    # ── над хребтом: домен + що сталося ──
    f.append(fitbox(130, 72, 300, 168,
                    "1979 · Ядерна енергетика\nТРИ-МАЙЛ-АЙЛЕНД\nпонад 100 однакових тривог\n"
                    "за перші хвилини — і жодного\nспособу приглушити дрібні",
                    size=14, fill=FILL, stroke=POS, color=INK, sw=1.8))
    f.append(fitbox(470, 72, 300, 168,
                    "2000-2013 · Лікарняні монітори\nALARM FATIGUE\n72-99% сигналів — хибні;\n"
                    "персонал звикає й перестає\nреагувати на писк",
                    size=14, fill=FILL, stroke=NEG, color=INK, sw=1.8))
    f.append(fitbox(810, 72, 300, 168,
                    "2016+ · Софт\nALERT / NOTIFICATION FATIGUE\nчергування (SRE) і застосунки:\n"
                    "недиференційований потік\nглушать цілком",
                    size=14, fill=FILL, stroke=MUTED, color=INK, sw=1.8))

    # від бокса до вузла
    for x in nodes:
        f.append(arrow(x, 240, x, 294, color=MUTED, sw=1.6))

    # ── під хребтом: ціна ──
    f.append(fitbox(130, 336, 300, 150,
                    "Оператори не вирізнили\nголовного сигналу, вручну\nзменшили аварійне охолодження\n"
                    "→ розплавлено ~45% зони",
                    size=13, fill=REDBG, stroke=POS, color=POS, bold=True, sw=1.8))
    f.append(fitbox(470, 336, 300, 150,
                    "Boston Globe (2011): >200 смертей\nза 5 років; Joint Commission —\n"
                    "80 смертей; ECRI — загроза №1",
                    size=13, fill=REDBG, stroke=POS, color=POS, bold=True, sw=1.8))
    f.append(fitbox(810, 336, 300, 150,
                    "Сповіщення вимикають геть —\nі повз проходить та єдина\nтривога, заради якої\n"
                    "все будувалось",
                    size=13, fill=REDBG, stroke=POS, color=POS, bold=True, sw=1.8))

    # від вузла до нижнього бокса
    for x in nodes:
        f.append(line(x, 321, x, 336, color=MUTED, sw=1.4))

    # банер-теза + відповідь
    f.append(fitbox(100, 508, 1040, 46,
                    "Один урок, три домени: потік недиференційованих тривог — це відсутність тривоги.",
                    size=15, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))
    f.append(fitbox(250, 562, 740, 42,
                    "Відповідь скрізь та сама — пріоритезувати сигнал: критичне в обхід шуму.",
                    size=14, fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=2))

    render(os.path.join(IMG, "alarm-lineage.svg"), W, H, *f,
           title="Тривожна втома: та сама помилка в ядерній, клінічній і софтверній царинах")


# ───────── Фіг. 5 (вставка proj): де живе стан ─────────
def fig_gate_state():
    W, H = 1240, 690
    f = []

    # два інстанси зверху
    f.append(fitbox(90, 66, 470, 98,
                    "Інстанс A (Gate)\nу пам'яті процесу — ЛИШЕ таймер\nозброєної групи (time.AfterFunc);\nусе інше — у спільному сховищі",
                    size=13, fill=FILL, stroke=INK, color=INK, sw=1.6))
    f.append(fitbox(680, 66, 470, 98,
                    "Інстанс B (Gate)\nтой самий код, той самий стан;\nчитає й пише ТЕ САМЕ сховище —\nбо фільтрує СПІЛЬНИЙ потік",
                    size=13, fill=FILL, stroke=INK, color=INK, sw=1.6))

    # стрілки вниз у сховище
    f.append(arrow(325, 166, 400, 250, color=MUTED, sw=1.8))
    f.append(arrow(915, 166, 840, 250, color=MUTED, sw=1.8))
    f.append(text(620, 210, "читають і пишуть спільний стан", size=12, color=MUTED))

    # рамка спільного сховища
    f.append(rect(90, 250, 1060, 320, fill="#f9fafb", stroke=NEG, sw=2, rx=10))
    f.append(text(620, 282, "Спільне сховище (Redis) — єдине джерело правди для стану фільтрів",
                  size=15, bold=True, color=NEG))

    rows = [
        ("Дедуп — SET dk NX EX ttl · dk = hash(отримувач + подія + канал) · nil ⇒ дубль, тихо кинути", GREENBG, FIELD),
        ("Буфер злиття — RPUSH group item (TTL ≈ 2·W) · відповідь «1» ⇒ ти власник → лише ти озброюєш таймер", BLUEBG, NEG),
        ("Відро жетонів — tb:user:channel = {tokens, last} · дозрів рахуємо через TIME сховища (спільний годинник)", GREENBG, FIELD),
        ("Тихі години — часовий пояс КОРИСТУВАЧА (настінний місцевий), не UTC сервера", "#fff7e6", "#b7791f"),
    ]
    ry = 302
    for s, bg, col in rows:
        f.append(fitbox(112, ry, 1016, 56, s, size=13, fill=bg, stroke=col, color=col, bold=True, sw=1.6))
        ry += 66

    # банер-застереження
    f.append(fitbox(120, 600, 1000, 62,
                    "Тримати цей стан у пам'яті процесу — кожен інстанс фільтрує НАОСЛІП лише свій шматок трафіку: "
                    "бурі й дублі просочуються між інстансами.",
                    size=14, fill=REDBG, stroke=POS, color=POS, bold=True, sw=2))

    render(os.path.join(IMG, "gate-state.svg"), W, H, *f,
           title="Стан фільтрів живе у спільному сховищі, не в пам'яті інстанса")


# ───────── Фіг. 6 (вставка proj): гонка власника таймера ─────────
def fig_coalesce_race():
    W, H = 1220, 560
    f = []

    # ── панель А: наївно ──
    f.append(text(110, 70, "Наївно: «перевір, тоді дій» — гонка між інстансами",
                  size=15, bold=True, color=POS, anchor="start"))
    f.append(fitbox(110, 92, 300, 44, "A: EXISTS(group)? → нема", size=13,
                    fill=FILL, stroke=MUTED, color=INK, sw=1.4))
    f.append(fitbox(110, 146, 300, 44, "B: EXISTS(group)? → нема", size=13,
                    fill=FILL, stroke=MUTED, color=INK, sw=1.4))
    f.append(text(258, 210, "(обидва читають t₀ — ще порожньо)", size=11, color=MUTED))
    f.append(arrow(414, 114, 470, 114, color=MUTED, sw=1.6))
    f.append(arrow(414, 168, 470, 168, color=MUTED, sw=1.6))
    f.append(fitbox(474, 92, 360, 44, "A: створює буфер + озброює таймер", size=13,
                    fill=REDBG, stroke=POS, color=POS, sw=1.6))
    f.append(fitbox(474, 146, 360, 44, "B: створює буфер + озброює таймер", size=13,
                    fill=REDBG, stroke=POS, color=POS, sw=1.6))
    f.append(arrow(838, 114, 894, 130, color=POS, sw=1.8))
    f.append(arrow(838, 168, 894, 152, color=POS, sw=1.8))
    f.append(fitbox(898, 108, 300, 52, "2 таймери → 2 дайджести\nна ту саму групу", size=13,
                    fill=REDBG, stroke=POS, color=POS, bold=True, sw=1.8))

    # роздільник
    f.append(line(90, 250, 1130, 250, color=GREY, sw=1.4, dash="6,5"))

    # ── панель Б: атомарно ──
    f.append(text(110, 296, "Атомарно: RPUSH повертає нову довжину — власник обирається сам",
                  size=15, bold=True, color=FIELD, anchor="start"))
    f.append(fitbox(110, 318, 300, 44, "A: RPUSH group → 1", size=13,
                    fill=FILL, stroke=MUTED, color=INK, sw=1.4))
    f.append(fitbox(110, 372, 300, 44, "B: RPUSH group → 2", size=13,
                    fill=FILL, stroke=MUTED, color=INK, sw=1.4))
    f.append(arrow(414, 340, 470, 340, color=MUTED, sw=1.6))
    f.append(arrow(414, 394, 470, 394, color=MUTED, sw=1.6))
    f.append(fitbox(474, 318, 360, 44, "A: «1» → ВЛАСНИК, озброює таймер", size=13,
                    fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=1.6))
    f.append(fitbox(474, 372, 360, 44, "B: «2» → лише додав у буфер", size=13,
                    fill=FILL, stroke=FIELD, color=FIELD, sw=1.4))
    f.append(arrow(838, 340, 894, 356, color=FIELD, sw=1.8))
    f.append(arrow(838, 394, 894, 378, color=FIELD, sw=1.8))
    f.append(fitbox(898, 344, 300, 44, "1 таймер → 1 дайджест", size=13,
                    fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=1.8))

    # банер
    f.append(fitbox(120, 452, 980, 62,
                    "Вибір власника таймера має бути АТОМАРНИМ у спільному сховищі — "
                    "інакше N інстансів дадуть N дайджестів на ту саму групу.",
                    size=14, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))

    render(os.path.join(IMG, "coalesce-race.svg"), W, H, *f,
           title="Гонка «обидва бачать новий ключ» і атомарний вибір власника")


# ───────── Фіг. 7 (вставка math): конверт token bucket N(w) ≤ b + r·w ─────────
def fig_throttle_envelope():
    W, H = 1140, 560
    f = []

    # межі поля графіка
    LX, RX, TY, BY = 155, 1010, 110, 470
    b, r = 5.0, 0.1                  # місткість, темп (жетон/хв)
    sx = (RX - LX) / 60.0
    sy = (BY - TY) / 11.0
    X = lambda t: LX + t * sx
    Y = lambda v: BY - v * sy

    # осі
    f.append(line(LX, BY, RX, BY, color=INK, sw=1.8))
    f.append(line(LX, BY, LX, TY, color=INK, sw=1.8))
    # мітки осі часу
    for t in (0, 10, 20, 30, 40, 50, 60):
        f.append(line(X(t), BY, X(t), BY + 6, color=MUTED, sw=1.4))
        f.append(text(X(t), BY + 24, str(t), size=12, color=MUTED))
    f.append(text((LX + RX) / 2, BY + 48, "час, хв", size=13, color=INK))
    # мітки осі значень
    for v in (0, 5, 10):
        f.append(line(LX - 6, Y(v), LX, Y(v), color=MUTED, sw=1.4))
        f.append(text(LX - 14, Y(v) + 4, str(v), size=12, color=MUTED, anchor="end"))
    f.append(text(LX + 4, TY - 18, "накопичено пропущено сповіщень", size=13, color=INK, anchor="start"))

    # конверт N(w) ≤ b + r·w
    f.append(line(X(0), Y(b), X(60), Y(b + r * 60), color=NEG, sw=2.6))
    f.append(text(770, 148, "конверт  N(w) ≤ b + r·w", size=15, color=NEG, bold=True))
    f.append(line(770, 156, X(47), Y(b + r * 47) - 4, color=NEG, sw=1.2, dash="4,3"))

    # нахил r — у відкритій зоні над конвертом
    f.append(text(380, 206, "нахил = r = 0.1/хв (усталений темп)", size=12.5, color=MUTED))

    # східчаста лінія фактичних пропусків: сплеск ×5, тоді +1 щодесять хвилин
    bx = X(0) + 3
    f.append(line(bx, Y(0), bx, Y(5), color=INK, sw=2.6))                  # сплеск ×5
    prev, lastx, lasty = 5, bx, Y(5)
    for t in (10, 20, 30, 40, 50, 60):
        nx = X(t)
        f.append(line(lastx, lasty, nx, lasty, color=INK, sw=2.4))         # тримаємо
        f.append(line(nx, lasty, nx, Y(prev + 1), color=INK, sw=2.4))      # сходинка +1
        f.append(circle(nx, Y(prev + 1), 4, fill=BG, stroke=INK, sw=1.6))
        lastx, lasty, prev = nx, Y(prev + 1), prev + 1

    # вільний член b — миттєвий сплеск: підпис у порожній зоні під першою сходинкою
    f.append(text(216, 402, "b = 5 — миттєвий сплеск", size=12.5, color=POS, anchor="start"))
    f.append(arrow(210, 396, bx + 2, Y(2.4), color=POS, sw=1.8))

    # фактичні пропуски — у порожній нижній зоні праворуч
    f.append(text(640, 434, "фактичні пропуски тримаються під конвертом",
                  size=12.5, color=INK))

    # банер-теза
    f.append(fitbox(150, 502, 840, 42,
                    "Вільний член = сплеск b; нахил = темп r. Повне відро випускає b поспіль, далі — по жетону за 1/r.",
                    size=13, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))

    render(os.path.join(IMG, "throttle-envelope.svg"), W, H, *f,
           title="Конверт відра: b + r·w обмежує пропуски в будь-якому вікні")


# ───────── Фіг. 8 (вставка math): фіксоване вікно проти debounce на миготінні ─────────
def fig_window_vs_debounce():
    W, H = 1180, 540
    f = []

    LX, RX = 130, 1030
    X = lambda t: LX + t * (RX - LX) / 660.0     # секунди на осі (запас на debounce-хвіст)

    # ── доріжка 1: миготливий сигнал ──
    y1 = 150
    f.append(text(LX, 108, "Пристрій миготить: 30 перемикань кожні 20 с (10 хв поспіль)",
                  size=14, bold=True, color=INK, anchor="start"))
    f.append(line(LX, y1, X(600), y1, color=MUTED, sw=1.6))
    for i in range(30):
        f.append(line(X(i * 20), y1 - 11, X(i * 20), y1 + 11, color=INK, sw=1.5))

    # ── доріжка 2: фіксоване вікно ──
    y2 = 275
    f.append(text(LX, 233, "Фіксоване вікно W = 60 с", size=14, bold=True, color=NEG, anchor="start"))
    f.append(text(RX, 233, "⌈600 / 60⌉ = 10 дайджестів", size=13.5, color=POS, anchor="end", bold=True))
    f.append(line(LX, y2, X(600), y2, color=MUTED, sw=1.6))
    for k in range(1, 11):
        t = k * 60
        f.append(line(X(t), y2 - 22, X(t), y2 + 22, color=MUTED, sw=1.2, dash="5,4"))
        f.append(rect(X(t) - 8, y2 - 8, 16, 16, fill=REDBG, stroke=POS, sw=1.8, rx=3))
    f.append(text(X(300), y2 + 46, "кожен дайджест — знімок посеред миготіння (може брехати про стан)",
                  size=12.5, color=MUTED))

    # ── доріжка 3: debounce ──
    y3 = 400
    f.append(text(LX, 358, "Debounce W = 60 с (таймер скидається на кожному перемиканні)",
                  size=14, bold=True, color=FIELD, anchor="start"))
    f.append(line(LX, y3, X(640), y3, color=MUTED, sw=1.6))
    f.append(arrow(X(580), y3, X(640), y3, color=FIELD, sw=1.8))
    f.append(text(X(610), y3 - 14, "60 с тиші", size=12, color=FIELD))
    f.append(rect(X(640) - 9, y3 - 9, 18, 18, fill=GREENBG, stroke=FIELD, sw=2, rx=3))
    f.append(text(X(300), y3 + 42, "1 дайджест — через тишу після того, як пристрій визначився: фінальний стан",
                  size=12.5, color=FIELD))

    # банер
    f.append(fitbox(120, 468, 940, 44,
                    "Фіксоване: затримка ≤ W, передбачувано — але ріже бурю на межах скиб. "
                    "Debounce: 30 перемикань → 1 підсумок фінального стану, ціною очікування спокою (зі стелею).",
                    size=12.5, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))

    render(os.path.join(IMG, "window-vs-debounce.svg"), W, H, *f,
           title="Фіксоване вікно проти debounce: ⌈T/W⌉ знімків чи один фінальний")


if __name__ == "__main__":
    fig_three_filters()
    fig_coalesce_window()
    fig_token_bucket()
    fig_alarm_lineage()
    fig_gate_state()
    fig_coalesce_race()
    fig_throttle_envelope()
    fig_window_vs_debounce()
    print("OK: three-filters.svg, coalesce-window.svg, token-bucket.svg, "
          "alarm-lineage.svg, gate-state.svg, coalesce-race.svg, "
          "throttle-envelope.svg, window-vs-debounce.svg")
