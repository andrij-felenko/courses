# -*- coding: utf-8 -*-
"""Фігури до кроку «Дублі й переупорядкування як норма»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

A_FILL = "#dfe9fb"      # оновлення A — старіше (21°)
B_FILL = "#eafaf0"      # оновлення B — новіше (23°)
GRAY_FILL = "#f0f0f2"
RED_FILL = "#fdecea"
GREEN_FILL = "#eafaf0"
AMBER = "#fff8e6"


def fig_reorder_normal():
    """Відправлено A→B, прибуло B→A: перехрестя ліній як образ переставлення."""
    W, H = 1080, 560
    frags = []

    TOPY, BOTY = 175, 430
    AX_T, BX_T = 330, 700          # верхній ряд (відправлено): A ліворуч, B праворуч
    BX_B, AX_B = 330, 700          # нижній ряд (прибуло): B ліворуч, A праворуч

    # ── ряд «Відправлено джерелом» ──
    frags.append(text(150, TOPY - 44, "Відправлено", size=14, bold=True, color=MUTED, anchor="middle"))
    frags.append(text(150, TOPY - 26, "джерелом", size=14, bold=True, color=MUTED, anchor="middle"))
    frags.append(text(W / 2, TOPY - 52, "спершу A, потім B", size=13, color=MUTED))
    a_t, aw, ah = textbox(AX_T, TOPY, "A · v5\n21°", size=14, bold=True, fill=A_FILL, stroke=NEG, min_w=120)
    b_t, bw, bh = textbox(BX_T, TOPY, "B · v6\n23°", size=14, bold=True, fill=B_FILL, stroke=FIELD, min_w=120)

    # ── ряд «Прибуло в хмару» ──
    frags.append(text(150, BOTY + 40, "Прибуло", size=14, bold=True, color=MUTED, anchor="middle"))
    frags.append(text(150, BOTY + 58, "в хмару", size=14, bold=True, color=MUTED, anchor="middle"))
    frags.append(text(W / 2, BOTY + 66, "спершу B, потім A", size=13, color=MUTED))
    b_b, _, _ = textbox(BX_B, BOTY, "B · v6\n23°", size=14, bold=True, fill=B_FILL, stroke=FIELD, min_w=120)
    a_b, _, _ = textbox(AX_B, BOTY, "A · v5\n21°", size=14, bold=True, fill=A_FILL, stroke=NEG, min_w=120)

    # ── лінії однакового повідомлення згори вниз (перехрещуються) ──
    yb1, yb2 = TOPY + ah / 2 + 4, BOTY - ah / 2 - 4
    # A: довга дорога (повтор), штрихована червона — з лівого верху в правий низ
    frags.append(line(AX_T, yb1, AX_B, yb2, color=POS, sw=2.2, dash="8,6"))
    # B: пряма, суцільна — з правого верху в лівий низ
    frags.append(line(BX_T, yb1, BX_B, yb2, color=INK, sw=2.0))

    # позначка в проміжку між лініями (праворуч від перехрестя, у чистій зоні)
    frags.append(text(560, 300, "переставлено", size=12, bold=True, color=MUTED))

    for f in (a_t, b_t, b_b, a_b):
        frags.append(f)

    # ── легенда внизу ──
    frags.append(line(70, 512, 110, 512, color=INK, sw=2.0))
    frags.append(text(118, 517, "B: пряма дорога", size=12, color=INK, anchor="start"))
    frags.append(line(360, 512, 400, 512, color=POS, sw=2.2, dash="8,6"))
    frags.append(text(408, 517, "A: повтор, довга дорога — наздогнав пізніше за нове B",
                      size=12, color=POS, anchor="start"))

    render(os.path.join(IMG, "reorder-normal.svg"), W, H, *frags,
           title="Відправлено A→B, прибуло B→A")


def fig_two_keys():
    """Дубль і переупорядкування — дві хвороби, два різні ключі впізнавання."""
    W, H = 1060, 540
    frags = []

    LX, RX = 235, 635              # ліві межі колонок
    CW = 380                       # ширина колонки
    LCX, RCX = LX + CW / 2, RX + CW / 2

    # заголовки колонок
    frags.append(fitbox(LX, 74, CW, 46, "ДУБЛЬ", size=17, bold=True, fill=RED_FILL, stroke=POS))
    frags.append(fitbox(RX, 74, CW, 46, "ПЕРЕУПОРЯДКУВАННЯ", size=17, bold=True, fill=A_FILL, stroke=NEG))

    rows = [
        (146, 62, "що це",
         "те саме оновлення двічі",
         "два різні оновлення не по черзі"),
        (226, 96, "чим упізнати",
         "ідентифікатор (тотожність):\n«чи бачив я це?»",
         "номер версії (старшинство):\n«котре з двох новіше?»"),
        (340, 62, "приклад шкоди",
         "дію виконано двічі",
         "свіже значення затерто старим"),
    ]
    for y, h, label, lcell, rcell in rows:
        frags.append(text(210, y + h / 2 + 4, label, size=13, bold=True, color=MUTED, anchor="end"))
        frags.append(fitbox(LX, y, CW, h, lcell, size=13, fill=BG, stroke=LINE))
        frags.append(fitbox(RX, y, CW, h, rcell, size=13, fill=BG, stroke=LINE))

    # спільна смуга внизу — вартовий версії
    frags.append(fitbox(LX, 428, RX + CW - LX, 58,
                        "Вартовий версії закриває ОБИДВІ — якщо застосування ідемпотентне за версією",
                        size=14, bold=True, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, "two-keys.svg"), W, H, *frags,
           title="Дві болячки — два різні ключі")


def fig_by_arrival_vs_version():
    """Ті самі прибуття, різне правило: за прибуттям → брехня; за версією → правда."""
    W, H = 1140, 560
    frags = []

    S1X, S2X, RX = 300, 640, 970
    S1W, S2W, RW = 300, 300, 210

    def lane(y, header, hcolor, step1, step2, result, res_fill, res_stroke, res_color):
        frags.append(text(70, y - 66, header, size=15, bold=True, color=hcolor, anchor="start"))
        s1, _, _ = textbox(S1X, y, step1, size=13, fill=BG, stroke=LINE, min_w=S1W)
        s2, _, _ = textbox(S2X, y, step2, size=13, fill=BG, stroke=LINE, min_w=S2W)
        rb, _, _ = textbox(RX, y, result, size=14, bold=True, fill=res_fill,
                           stroke=res_stroke, color=res_color, sw=2, min_w=RW)
        frags.append(arrow(S1X + S1W / 2 + 6, y, S2X - S2W / 2 - 6, y, color=INK, sw=1.7))
        frags.append(arrow(S2X + S2W / 2 + 6, y, RX - RW / 2 - 6, y, color=res_stroke, sw=1.8))
        for f in (s1, s2, rb):
            frags.append(f)

    # вхід — однаковий для обох доріжок
    frags.append(text(W / 2, 78, "Прибуло однаково в обидві доріжки:  спершу B (v6, 23°),  тоді A (v5, 21°)",
                      size=14, bold=True, color=INK))

    lane(190, "Трактує за ПРИБУТТЯМ",  POS,
         "прийшов B v6\n→ став 23°",
         "прийшов A v5\n→ став 21°  (останній!)",
         "кінець: 21°\nБРЕХНЯ", RED_FILL, POS, POS)

    frags.append(line(60, 300, 1080, 300, color=MUTED, sw=1, dash="6,6"))

    lane(410, "Вартовий ВЕРСІЇ",  FIELD,
         "прийшов B v6\n→ став 23°,  межа = 6",
         "прийшов A v5:\n5 ≤ 6 → відкинуто",
         "кінець: 23°\nПРАВДА", GREEN_FILL, FIELD, FIELD)

    frags.append(text(W / 2, 522,
                      "Прибуття однакові — різне лише правило рішення. Номер версії відкидає відсталий пакет; мить прибуття — ні.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "by-arrival-vs-version.svg"), W, H, *frags,
           title="За прибуттям → брехня;  за версією → правда")


def fig_exactly_once_timeline():
    """Вставка hist-exactly-once: п'ятдесят років думки про «рівно раз» на осі часу."""
    W, H = 1240, 350
    frags = []
    y = 140                                   # рівень осі часу
    xs = [130, 375, 620, 865, 1110]
    colors = [POS, INK, NEG, MUTED, FIELD]
    nodes = [
        ("1975", ["Дві банди, не генерали", "Аккоюнлу · Еканадгам", "· Губер (SOSP):", "«рівно раз» довести", "НЕМОЖЛИВО"]),
        ("1978", ["Два генерали", "Джим Ґрей дає образ", "і назву «парадокс»"]),
        ("1985", ["FLP: глибша стіна —", "консенсусу в асинхронній", "системі з 1 збоєм нема"]),
        ("2015", ["«You Cannot Have", "Exactly-Once Delivery»", "спільнота ставить крапку"]),
        ("2017", ["Kafka 0.11: «exactly-once»", "чесно й У МЕЖАХ", "(дедуп + транзакції)"]),
    ]

    frags.append(line(90, y, W - 90, y, color=MUTED, sw=2.4))
    for x, (yr, lines), c in zip(xs, nodes, colors):
        frags.append(circle(x, y, 9, fill=c, stroke=c))
        frags.append(text(x, y - 22, yr, size=20, bold=True, color=c))
        box, _, _ = textbox(x, y + 118, "\n".join(lines), size=12,
                            min_w=214, fill=BG, stroke=c)
        frags.append(box)

    render(os.path.join(IMG, "exactly-once-timeline.svg"), W, H, *frags,
           title="«Рівно раз»: півстоліття однієї думки")


def fig_kafka_boundary():
    """Вставка hist-exactly-once: що «exactly-once» у Kafka покриває, а що ні."""
    W, H = 1080, 540
    frags = []

    # ── зовнішня червона зона: світ поза Kafka ──
    frags.append(rect(40, 62, 1000, 452, fill=RED_FILL, stroke=POS, sw=2, rx=12))
    frags.append(text(W / 2, 96, "ЗОВНІ СВІТУ KAFKA — гарантія не діє, два генерали повертаються",
                      size=15, bold=True, color=POS))

    # ── внутрішня зелена зона: замкнене коло Kafka ──
    GX, GY, GW, GH = 90, 122, 900, 208
    CX = GX + GW / 2
    frags.append(rect(GX, GY, GW, GH, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=10))
    frags.append(text(CX, GY + 28, "У СВІТІ KAFKA: exactly-once PROCESSING",
                      size=15, bold=True, color=FIELD))
    # підпис-механізм — НАД рядом ланок, щоб вертикальна стрілка його не перетнула
    frags.append(text(CX, GY + 58,
                      "дедуп: PID + порядковий номер на партицію · атомарність: транзакція",
                      size=12, color=MUTED))

    # три ланки замкненого циклу
    rowy = GY + 128
    tin, _, _ = textbox(230, rowy, "вхідний\ntopic", size=13, fill=BG, stroke=LINE, min_w=140)
    proc, _, _ = textbox(CX, rowy, "обробка\n(Kafka Streams)", size=13, bold=True,
                         fill=AMBER, stroke=FIELD, min_w=180)
    tout, _, _ = textbox(760, rowy, "вихідний\ntopic", size=13, fill=BG, stroke=LINE, min_w=140)
    frags.append(arrow(300, rowy, 448, rowy, color=INK, sw=1.8))
    frags.append(arrow(632, rowy, 690, rowy, color=INK, sw=1.8))
    for f in (tin, proc, tout):
        frags.append(f)

    # ── стрілка з «обробки» вниз, ЗА зелену межу, у червону зону ──
    frags.append(arrow(CX, rowy + 30, CX, 392, color=POS, sw=2.4))
    frags.append(text(CX + 24, 356, "перетнув межу — гарантія Kafka вже не діє",
                      size=12, bold=True, color=POS, anchor="start"))

    ext, _, _ = textbox(CX, 440, "e-mail · оплата · чужий API · зовнішня БД\n— свій ключ ідемпотентності ТУТ",
                        size=13, bold=True, fill=BG, stroke=POS, sw=2, color=POS, min_w=520)
    frags.append(ext)

    render(os.path.join(IMG, "kafka-eos-boundary.svg"), W, H, *frags,
           title="Що «exactly-once» у Kafka покриває — і де закінчується")


def fig_version_ladder():
    """Вставка math-convergence: стани одного господаря — ланцюг; злиття = вищий."""
    W, H = 1140, 620
    frags = []

    # ── вертикальний ланцюг станів (ліворуч) ──
    LCX = 260
    nodes = [
        (540, "⊥ · нічого", GRAY_FILL, LINE, "seen = −1"),
        (430, "v5 · 21°", A_FILL, NEG, None),
        (320, "v6 · 23°", B_FILL, FIELD, None),
        (210, "v7 · 22°", B_FILL, FIELD, None),
    ]
    # напрям порядку ⊑ — стрілка знизу вгору, ліворуч від вузлів
    frags.append(arrow(110, 560, 110, 180, color=MUTED, sw=2.2))
    frags.append(text(96, 372, "⊑", size=18, bold=True, color=MUTED, anchor="middle"))
    frags.append(text(150, 588, "вище = новіша версія", size=11, color=MUTED, anchor="middle"))

    boxes = []
    for y, label, fill, stroke, sub in nodes:
        b, _, _ = textbox(LCX, y, label, size=15, bold=True, fill=fill, stroke=stroke, min_w=160)
        boxes.append(b)
        if sub:
            frags.append(text(LCX, y + 32, sub, size=11, color=MUTED))
    # з'єднувачі ⊏ між сусідніми вузлами
    for i in range(len(nodes) - 1):
        y_low = nodes[i][0] - 23
        y_high = nodes[i + 1][0] + 23
        frags.append(line(LCX, y_low, LCX, y_high, color=LINE, sw=1.4))
        frags.append(text(LCX + 20, (y_low + y_high) / 2 + 5, "⊏", size=16,
                          bold=True, color=MUTED, anchor="start"))
    frags.extend(boxes)
    frags.append(text(LCX, 165, "…лічильник росте далі", size=12, italic=True, color=MUTED))

    # ── панель прикладів злиття (праворуч) ──
    PX = 700
    frags.append(rect(PX - 40, 190, 460, 265, fill=BG, stroke=LINE, sw=1.2, rx=10))
    frags.append(text(PX + 190, 168, "злиття = піднятися до вищого", size=15, bold=True, color=INK))
    examples = [
        (240, "merge( v5 , v6 )", "= v6", "новіша перемагає"),
        (330, "merge( v6 , v6 )", "= v6", "дубль → те саме (ідемпотентно)"),
        (420, "merge( v7 , v5 )", "= v7", "порядок байдужий (комутативно)"),
    ]
    for y, lhs, rhs, note in examples:
        lb, _, _ = textbox(PX + 90, y, lhs, size=13, fill=FILL, stroke=LINE, min_w=200)
        frags.append(lb)
        frags.append(text(PX + 210, y + 5, rhs, size=16, bold=True, color=FIELD, anchor="start"))
        frags.append(text(PX + 90, y + 32, note, size=11, color=MUTED))

    render(os.path.join(IMG, "version-ladder.svg"), W, H, *frags,
           title="Один господар → стани шикуються в ланцюг")


def fig_fold_convergence():
    """Вставка math-convergence: той самий набір, різний порядок і дублі — та сама вершина."""
    W, H = 1180, 560
    frags = []

    frags.append(text(W / 2, 66,
                      "Той самий набір  {A = v5 · 21°,   B = v6 · 23°}  —  різний порядок, різні дублі",
                      size=15, bold=True, color=INK))

    TOK = {"5": (A_FILL, NEG, "v5"), "6": (B_FILL, FIELD, "v6")}
    lanes = [
        (150, ["6", "5", "6"],           "⊥ ⊔ 6 ⊔ 5 ⊔ 6  =  6"),
        (290, ["5", "5", "6", "5"],      "⊥ ⊔ 5 ⊔ 5 ⊔ 6 ⊔ 5  =  6"),
        (430, ["6", "6", "5", "6", "5"], "⊥ ⊔ 6 ⊔ 6 ⊔ 5 ⊔ 6 ⊔ 5  =  6"),
    ]
    x0, step = 180, 96
    FINALX = 1000
    for y, seq, trace in lanes:
        frags.append(text(x0 - 96, y + 5, "⊥", size=17, bold=True, color=MUTED))
        frags.append(arrow(x0 - 82, y, x0 - 34, y, color=MUTED, sw=1.6))
        for i, t in enumerate(seq):
            fill, stroke, lbl = TOK[t]
            x = x0 + i * step
            b, _, _ = textbox(x, y, lbl, size=14, bold=True, fill=fill, stroke=stroke, min_w=66)
            frags.append(b)
            if i < len(seq) - 1:
                frags.append(arrow(x + 33, y, x + step - 33, y, color=MUTED, sw=1.5))
        lastx = x0 + (len(seq) - 1) * step
        frags.append(arrow(lastx + 33, y, FINALX - 60, y, color=FIELD, sw=2.2))
        fb, _, _ = textbox(FINALX, y, "23°", size=16, bold=True, fill=GREEN_FILL,
                           stroke=FIELD, sw=2, min_w=96)
        frags.append(fb)
        frags.append(text(x0 - 96, y + 42, trace, size=12, color=MUTED, anchor="start"))

    frags.append(line(FINALX - 62, 168, FINALX - 62, 448, color=FIELD, sw=1.4, dash="5,5"))
    frags.append(text(FINALX, 505, "усі доріжки → 23°", size=14, bold=True, color=FIELD))
    frags.append(text(FINALX, 525, "(вершина = найбільша версія)", size=11, color=MUTED))

    render(os.path.join(IMG, "fold-convergence.svg"), W, H, *frags,
           title="Будь-який порядок, будь-які дублі — та сама вершина")


def fig_one_vs_two_owners():
    """Вставка math-convergence: один господар → ланцюг; двоє → часткова впорядкованість, LWW втрачає."""
    W, H = 1200, 640
    frags = []

    frags.append(line(W / 2, 66, W / 2, 604, color=MUTED, sw=1.2, dash="6,6"))

    # ── ЛІВОРУЧ: один господар — ланцюг ──
    frags.append(text(300, 96, "ОДИН ГОСПОДАР → ланцюг", size=16, bold=True, color=FIELD))
    frags.append(text(300, 118, "повний порядок: будь-які два порівнянні", size=12, color=MUTED))
    LCX = 300
    chain = [(520, "⊥"), (432, "v5 · 21°"), (344, "v6 · 23°"), (256, "v7 · 22°")]
    for i in range(len(chain) - 1):
        frags.append(line(LCX, chain[i][0] - 22, LCX, chain[i + 1][0] + 22, color=LINE, sw=1.4))
    cboxes = []
    for j, (y, lbl) in enumerate(chain):
        fill = GRAY_FILL if j == 0 else (A_FILL if "v5" in lbl else B_FILL)
        stroke = LINE if j == 0 else (NEG if "v5" in lbl else FIELD)
        b, _, _ = textbox(LCX, y, lbl, size=14, bold=True, fill=fill, stroke=stroke, min_w=150)
        cboxes.append(b)
    frags.extend(cboxes)
    frags.append(circle(LCX + 118, 256, 14, fill="none", stroke=FIELD, sw=2.2))
    frags.append(text(LCX + 118, 262, "✓", size=16, bold=True, color=FIELD))
    frags.append(text(300, 566, "єдина вершина = найновіший СПРАВЖНІЙ стан",
                      size=12, bold=True, color=FIELD))

    # ── ПРАВОРУЧ: двоє господарів — часткова впорядкованість ──
    RCX = 900
    frags.append(text(RCX, 96, "ДВОЄ ГОСПОДАРІВ → лише частковий порядок", size=15, bold=True, color=POS))
    frags.append(text(RCX, 118, "a7 і b7 несумірні — «більшого» немає", size=12, color=MUTED))

    base, _, _ = textbox(RCX, 500, "спільний стан  v6", size=13, bold=True,
                         fill=GRAY_FILL, stroke=LINE, min_w=180)
    ax, bx, midy = RCX - 150, RCX + 150, 372
    ab, _, _ = textbox(ax, midy, "A: a7\nяскраво", size=13, bold=True, fill=A_FILL, stroke=NEG, min_w=140)
    bb, _, _ = textbox(bx, midy, "B: b7\nтьмяно", size=13, bold=True, fill=B_FILL, stroke=FIELD, min_w=140)
    # ребра від спільного низу до обох конкурентних гілок
    frags.append(line(RCX, 478, ax, midy + 28, color=LINE, sw=1.4))
    frags.append(line(RCX, 478, bx, midy + 28, color=LINE, sw=1.4))
    # позначка несумірності
    frags.append(text(RCX, midy - 2, "∦", size=24, bold=True, color=POS))
    frags.append(text(RCX, midy + 22, "несумірні", size=11, color=POS))
    # істинне з'єднання вгорі
    joinb, _, _ = textbox(RCX, 214, "a7 ⊔ b7 = ОБИДВА", size=13, bold=True,
                          fill=GREEN_FILL, stroke=FIELD, min_w=250)
    frags.append(text(RCX, 182, "справжнє з'єднання — над обома", size=11, color=MUTED))
    frags.append(line(ax, midy - 28, RCX - 60, 232, color=FIELD, sw=1.4))
    frags.append(line(bx, midy - 28, RCX + 60, 232, color=FIELD, sw=1.4))
    for f in (base, ab, bb, joinb):
        frags.append(f)
    frags.append(text(RCX, 584, "LWW бере одного за tiebreak → другий тихо ЗНИКАЄ",
                      size=12, bold=True, color=POS))

    render(os.path.join(IMG, "one-vs-two-owners.svg"), W, H, *frags,
           title="Де правило тримається — і де ламається")


def fig_harness_pipeline():
    """Вставка proj-reorder-harness: стенд — незалежний оракул (max версія) проти вартового,
    якого годують перемішаним і задубльованим потоком; підсумок звіряють з оракулом."""
    W, H = 1200, 540
    frags = []

    # ── нижня «доріжка під випробуванням» ──
    src, _, _   = textbox(140, 300, "ДЖЕРЕЛО\nштампує версію\nна пристрій",
                          size=13, bold=True, fill=BG, stroke=LINE, min_w=170)
    true_, _, _ = textbox(400, 300, "істинний потік\nliving: v1 v2 v3\nhall: v1 v2",
                          size=13, fill=BG, stroke=LINE, min_w=200)
    net, _, _   = textbox(660, 410, "ЗЛОВОРОЖА МЕРЕЖА\n× 1..3 копії\n+ перемішати",
                          size=13, bold=True, fill=RED_FILL, stroke=POS, color=POS, min_w=210)
    guard, _, _ = textbox(895, 410, "ВАРТОВИЙ\napplyUpdate\nмежа / пристрій",
                          size=13, bold=True, fill=AMBER, stroke=FIELD, min_w=190)
    final, _, _ = textbox(1090, 410, "кінцевий\nстан",
                          size=13, bold=True, fill=BG, stroke=LINE, min_w=130)

    # ── верхня «істина» ──
    oracle, _, _ = textbox(660, 150, "ОРАКУЛ\nmax версія / пристрій\nliving → v3 · hall → v2",
                           size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, min_w=250)
    assr, _, _   = textbox(1035, 150, "ЗБІГ?\nстан == оракул\nдля КОЖНОГО пристрою",
                           size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, color=FIELD, min_w=250)

    frags.append(arrow(226, 300, 296, 300))                       # джерело → істинний потік
    frags.append(arrow(472, 268, 556, 180, color=FIELD, sw=2))    # істинний → оракул
    frags.append(text(452, 236, "істина", size=12, color=FIELD, anchor="end"))
    frags.append(arrow(472, 332, 560, 392, color=POS, sw=2))      # істинний → мережа
    frags.append(arrow(766, 410, 800, 410))                       # мережа → вартовий
    frags.append(arrow(991, 410, 1025, 410))                      # вартовий → кінець
    frags.append(arrow(786, 150, 908, 150, color=FIELD, sw=2))    # оракул → збіг
    frags.append(arrow(1090, 376, 1090, 192, color=INK, sw=2))    # кінець → збіг (вгору)

    for f in (src, true_, net, guard, final, oracle, assr):
        frags.append(f)

    frags.append(text(W / 2, 512,
                      "Ціль стенд знає напряму — оракулом. Хоч як мережа перемішає й задублює, "
                      "підсумок вартового мусить збігтися з оракулом.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "harness-pipeline.svg"), W, H, *frags,
           title="Стенд: незалежний оракул проти вартового під обстрілом")


def fig_perkey_vs_global():
    """Вставка proj-reorder-harness: глобальна межа плутає версії різних пристроїв;
    межа на пристрій — ні. Тому стенд і тримає кілька пристроїв."""
    W, H = 1160, 560
    frags = []
    CX = W / 2

    frags.append(fitbox(120, 70, 260, 50, "ГЛОБАЛЬНА межа — БАГ",
                        size=15, bold=True, fill=RED_FILL, stroke=POS, color=POS))
    frags.append(fitbox(450, 70, 260, 50, "ПРИБУЛО (те саме)",
                        size=15, bold=True, fill=BG, stroke=LINE))
    frags.append(fitbox(780, 70, 260, 50, "МЕЖА НА ПРИСТРІЙ",
                        size=15, bold=True, fill=GREEN_FILL, stroke=FIELD, color=FIELD))

    rows = [
        ("living · v2 → 22°", "−1 → 2:  взяв",     FIELD, "L: −1 → 2:  взяв",    FIELD),
        ("hall · v1 → 70%",   "1 ≤ 2 → ВІДКИНУВ",  POS,   "H: −1 → 1:  взяв",    FIELD),
        ("living · v1 → 21°", "1 ≤ 2 → відкинув",  MUTED, "L: 1 ≤ 2 → відкинув", MUTED),
        ("hall · v2 → 72%",   "2 ≤ 2 → ВІДКИНУВ",  POS,   "H: 1 → 2:  взяв",     FIELD),
    ]
    y0, dy, h = 150, 70, 54
    for i, (arr, ldec, lcol, rdec, rcol) in enumerate(rows):
        y = y0 + i * dy
        frags.append(fitbox(120, y, 260, h, ldec, size=13, bold=(lcol == POS),
                            fill=BG, stroke=(POS if lcol == POS else LINE), color=lcol))
        frags.append(fitbox(450, y, 260, h, arr, size=13, fill=FILL, stroke=LINE))
        frags.append(fitbox(780, y, 260, h, rdec, size=13, bold=(rcol == FIELD),
                            fill=BG, stroke=(FIELD if rcol == FIELD else LINE), color=rcol))

    frags.append(fitbox(120, 438, 260, 62,
                        "hall лишився ПОРОЖНІЙ:\nверсії living зараховано проти hall",
                        size=12, bold=True, fill=RED_FILL, stroke=POS, color=POS))
    frags.append(fitbox(780, 438, 260, 62, "living = 22° · hall = 72%:\nобидва праві",
                        size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, color=FIELD))

    frags.append(text(CX, 528,
                      "Версії кожного пристрою починаються з 1 → номери різних пристроїв збігаються. "
                      "Стенд ловить баг ЛИШЕ з кількома пристроями.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "perkey-vs-global.svg"), W, H, *frags,
           title="Межа має бути на пристрій, а не глобальна")


def fig_race_check_then_act():
    """Вставка proj-reorder-harness: read-compare-write не атомарний — без замка межа
    відкочується; замок на пристрій серіалізує."""
    W, H = 1120, 610
    frags = []

    def step(cx, cy, s, fill, stroke, color=INK):
        b, _, _ = textbox(cx, cy, s, size=13, fill=fill, stroke=stroke, color=color, min_w=196)
        return b

    # ── верхній панель: без замка ──
    frags.append(text(W / 2, 66,
                      "БЕЗ замка — read-compare-write переплітається (той самий пристрій, межа = 5, дві копії)",
                      size=13, bold=True, color=POS))
    y1, y2 = 132, 214
    frags.append(text(66, y1 + 5, "W1", size=14, bold=True, color=NEG, anchor="start"))
    frags.append(text(66, y2 + 5, "W2", size=14, bold=True, color=NEG, anchor="start"))
    xs = [250, 490, 730, 970]
    frags.append(step(xs[0], y1, "читає межу = 5\n(бачить v7)", BG, LINE))
    frags.append(step(xs[1], y2, "читає межу = 5\n(бачить v6)", BG, LINE))
    frags.append(step(xs[2], y1, "v7 > 5 → пише\nзначення = v7, межа = 7", B_FILL, FIELD))
    frags.append(step(xs[3], y2, "v6 > 5 → пише\nзначення = v6, межа = 6", RED_FILL, POS, color=POS))

    frags.append(arrow(120, 272, 1030, 272, color=MUTED, sw=1.5))
    frags.append(text(1038, 276, "час", size=12, color=MUTED, anchor="start"))
    for i, x in enumerate(xs):
        frags.append(line(x, 252, x, 264, color=MUTED, sw=1))
        frags.append(text(x, 248, "t%d" % (i + 1), size=11, color=MUTED))
    frags.append(fitbox(290, 296, 540, 40,
                        "межа відкотилася 7 → 6 · свіже v7 ЗАТЕРТО старим v6",
                        size=13, bold=True, fill=RED_FILL, stroke=POS, color=POS))

    # ── нижній панель: із замком ──
    frags.append(line(60, 370, W - 60, 370, color=MUTED, sw=1, dash="6,6"))
    frags.append(text(W / 2, 406,
                      "ЗАМОК на пристрій — read-compare-write неподільний (серіалізовано на цей пристрій)",
                      size=13, bold=True, color=FIELD))
    y3, y4 = 466, 548
    frags.append(text(66, y3 + 5, "W1", size=14, bold=True, color=NEG, anchor="start"))
    frags.append(text(66, y4 + 5, "W2", size=14, bold=True, color=NEG, anchor="start"))
    frags.append(step(300, y3, "бере замок · читає 5\nv7 > 5 → межа = 7 · віддає", B_FILL, FIELD))
    frags.append(step(770, y4, "бере замок · читає 7\nv6 ≤ 7 → відкидає", GREEN_FILL, FIELD, color=FIELD))
    frags.append(arrow(410, 508, 636, 528, color=MUTED, sw=1.5))
    frags.append(fitbox(280, 578, 560, 30, "значення = v7 · межа = 7 — правду збережено",
                        size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, color=FIELD))

    render(os.path.join(IMG, "race-check-then-act.svg"), W, H, *frags,
           title="Одночасні повтори: чому read-compare-write треба замикати")


if __name__ == "__main__":
    fig_reorder_normal()
    fig_two_keys()
    fig_by_arrival_vs_version()
    fig_exactly_once_timeline()
    fig_kafka_boundary()
    fig_version_ladder()
    fig_fold_convergence()
    fig_one_vs_two_owners()
    fig_harness_pipeline()
    fig_perkey_vs_global()
    fig_race_check_then_act()
    print("OK: reorder-normal.svg, two-keys.svg, by-arrival-vs-version.svg, "
          "exactly-once-timeline.svg, kafka-eos-boundary.svg, "
          "version-ladder.svg, fold-convergence.svg, one-vs-two-owners.svg, "
          "harness-pipeline.svg, perkey-vs-global.svg, race-check-then-act.svg")
