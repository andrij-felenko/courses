# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: розрив проти неподільності ────────────────────────────────────
def fig_torn_vs_atomic():
    W, H = 760, 400
    p = []
    p.append(text(W / 2, 30, "count++ як три кроки: без захисту рветься, atomic — ні", size=16, bold=True))

    # --- ліворуч: неатомарний RMW, перебитий іншим потоком ---
    lx = 40
    p.append(text(lx + 150, 66, "звичайне count++", size=13, bold=True, color=POS))
    # доріжка потоку A
    p.append(text(lx, 100, "потік A", size=11, color=MUTED, anchor="start"))
    p.append(text(lx, 250, "потік B", size=11, color=MUTED, anchor="start"))
    ax = lx + 20
    stepsA = [("read → 5", 92), ("+1 → 6", 140)]
    for s, yy in stepsA:
        b, w, h = textbox(ax + 70, yy, s, size=11, pad=6, min_w=110)
        p.append(b)
    # запис A відкладено вниз (після B)
    b, w, h = textbox(ax + 70, 200, "write 6", size=11, pad=6, min_w=110, stroke=POS)
    p.append(b)
    # потік B врізається посередині
    bx = lx + 165
    for s, yy in [("read → 5", 158), ("+1 → 6", 206), ("write 6", 254)]:
        b, w, h = textbox(bx + 70, yy, s, size=11, pad=6, min_w=110, fill="#eaf0fd", stroke=NEG)
        p.append(b)
    # підсумок
    b, w, h = textbox(lx + 150, 320, ["було два +1, а count = 6", "одне оновлення зникло"],
                      size=12, pad=8, stroke=POS, fill="#fdecea", bold=True)
    p.append(b)

    # роздільник
    p.append(line(W / 2, 55, W / 2, 300, color=MUTED, sw=1, dash="4,4"))

    # --- праворуч: atomic fetch_add неподільний ---
    rx = 415
    p.append(text(rx + 150, 66, "count.fetch_add(1)", size=13, bold=True, color=FIELD))
    p.append(text(rx, 100, "потік A", size=11, color=MUTED, anchor="start"))
    p.append(text(rx, 250, "потік B", size=11, color=MUTED, anchor="start"))
    # один неподільний блок A
    b, w, h = textbox(rx + 110, 128, ["fetch_add:", "read-modify-write", "5 → 6  (неподільно)"],
                      size=11, pad=8, min_w=170, fill="#eafaf1", stroke=FIELD, bold=True)
    p.append(b)
    # B чекає й бачить 6, робить 6→7
    b, w, h = textbox(rx + 110, 232, ["fetch_add:", "read-modify-write", "6 → 7  (неподільно)"],
                      size=11, pad=8, min_w=170, fill="#eafaf1", stroke=FIELD, bold=True)
    p.append(b)
    b, w, h = textbox(rx + 150, 320, ["два +1 → count = 7", "жодне не втрачено"],
                      size=12, pad=8, stroke=FIELD, fill="#eafaf1", bold=True)
    p.append(b)

    render(os.path.join(OUT, 'torn-vs-atomic.svg'), W, H, *p)


# ── Фігура 2: перестановка ламає передачу «дані + прапорець» ─────────────────
def fig_reordering():
    W, H = 760, 360
    p = []
    p.append(text(W / 2, 30, "Порядок важливий: перестановка ламає «дані, потім прапорець»", size=15, bold=True))

    # --- як написано (виробник) ---
    lx = 40
    p.append(text(lx + 130, 62, "як написано", size=13, bold=True))
    src = ["data = 42;", "ready = true;"]
    for i, s in enumerate(src):
        b, w, h = textbox(lx + 130, 92 + i * 42, s, size=13, pad=8, min_w=200)
        p.append(b)
    p.append(text(lx + 130, 180, "намір: дані готові", size=11, color=MUTED))
    p.append(text(lx + 130, 196, "ДО прапорця", size=11, color=MUTED))

    # стрілка «оптимізатор/процесор переставив»
    p.append(arrow(lx + 270, 130, lx + 330, 130, color=POS, sw=2))
    p.append(text(lx + 300, 116, "переставлено", size=10, color=POS))

    # --- як виконалось (переставлено) ---
    mx = 360
    p.append(text(mx + 110, 62, "як виконалось", size=13, bold=True, color=POS))
    src2 = ["ready = true;", "data = 42;"]
    for i, s in enumerate(src2):
        clr = POS if i == 0 else INK
        b, w, h = textbox(mx + 110, 92 + i * 42, s, size=13, pad=8, min_w=190,
                          stroke=(POS if i == 0 else LINE), fill=("#fdecea" if i == 0 else FILL))
        p.append(b)

    # --- споживач ловить діру ---
    cx = 590
    p.append(line(mx + 220, 55, mx + 220, 250, color=MUTED, sw=1, dash="4,4"))
    p.append(text(cx + 70, 62, "інший потік", size=13, bold=True, color=NEG))
    b, w, h = textbox(cx + 70, 100, "if (ready)", size=12, pad=7, min_w=150, fill="#eaf0fd", stroke=NEG)
    p.append(b)
    b, w, h = textbox(cx + 70, 150, ["читає data", "→ ще старе!"], size=11, pad=7, min_w=150,
                      fill="#fdecea", stroke=POS, bold=True)
    p.append(b)

    b, w, h = textbox(W / 2, 300, "neподільність не рятує: обидва записи атомарні окремо, а біда — у ПОРЯДКУ",
                      size=12, pad=9, stroke=POS, fill="#fdecea", bold=True)
    # fix typo in label
    render_note = None
    p[-1] = textbox(W / 2, 300, "неподільність не рятує: кожен запис атомарний окремо, а біда — у ПОРЯДКУ",
                    size=12, pad=9, stroke=POS, fill="#fdecea", bold=True)[0]

    render(os.path.join(OUT, 'reordering.svg'), W, H, *p)


# ── Фігура 3: release-store / acquire-load синхронізують ─────────────────────
def fig_release_acquire():
    W, H = 780, 380
    p = []
    p.append(text(W / 2, 30, "release + acquire: усе ДО релізу стає видно ПІСЛЯ захоплення", size=15, bold=True))

    # потік-виробник ліворуч
    lx = 60
    p.append(text(lx + 120, 66, "потік-виробник", size=13, bold=True, color=FIELD))
    prod = [
        ("data = 42;", 96, INK, FILL, LINE),
        ("buf[i] = x;", 132, INK, FILL, LINE),
        ("ready.store(true,", 178, FIELD, "#eafaf1", FIELD),
        ("  release);", 200, FIELD, "#eafaf1", FIELD),
    ]
    for s, yy, clr, fl, st in prod:
        b, w, h = textbox(lx + 120, yy, s, size=12, pad=6, min_w=210, color=clr, fill=fl, stroke=st,
                          bold=(clr == FIELD))
        p.append(b)
    # рамка «усе це» над релізом
    p.append(rect(lx + 5, 80, 230, 74, fill="none", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(lx + 120, 236, "усі ці записи —", size=11, color=MUTED))
    p.append(text(lx + 120, 252, "перед релізом", size=11, color=MUTED))

    # стрілка синхронізації (веду низько, а підпис — вище, щоб не перетиналися)
    p.append(text(W / 2 + 5, 116, "synchronizes-with", size=12, color=NEG, bold=True, italic=True))
    p.append(text(W / 2 + 5, 132, "(той самий прапорець)", size=10, color=MUTED))
    p.append(arrow(lx + 250, 200, W - 305, 150, color=NEG, sw=2.2))

    # потік-споживач праворуч
    rx = W - 300
    p.append(text(rx + 120, 66, "потік-споживач", size=13, bold=True, color=NEG))
    cons = [
        ("while(!ready.load(", 96, NEG, "#eaf0fd", NEG),
        ("      acquire)) {}", 118, NEG, "#eaf0fd", NEG),
        ("use(data);", 164, INK, FILL, LINE),
        ("read(buf[i]);", 200, INK, FILL, LINE),
    ]
    for s, yy, clr, fl, st in cons:
        b, w, h = textbox(rx + 120, yy, s, size=12, pad=6, min_w=210, color=clr, fill=fl, stroke=st,
                          bold=(clr == NEG))
        p.append(b)
    p.append(rect(rx + 5, 148, 230, 68, fill="none", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(rx + 120, 236, "тут гарантовано", size=11, color=MUTED))
    p.append(text(rx + 120, 252, "видно 42 і buf", size=11, color=MUTED))

    b, w, h = textbox(W / 2, 320, ["acquire-читання, що ПОБАЧИЛО release-запис,",
                                   "бачить і все, що виробник зробив до нього"],
                      size=12, pad=9, stroke=NEG, fill="#eaf0fd", bold=True)
    p.append(b)

    render(os.path.join(OUT, 'release-acquire.svg'), W, H, *p)


# ── Фігура 4: драбина сили порядків ─────────────────────────────────────────
def fig_order_ladder():
    W, H = 720, 380
    p = []
    p.append(text(W / 2, 30, "Три рівні порядку: сила гарантій ↔ ціна", size=16, bold=True))

    rows = [
        ("relaxed", "лише неподільність; порядок не обіцяно",
         "лічильники, статистика", "#eafaf1", FIELD, "найдешевший"),
        ("acquire / release", "пара «віддав → захопив» синхронізує один канал",
         "прапорець готовності, черга", "#eef4ff", NEG, "середина"),
        ("seq_cst (типовий)", "єдиний спільний порядок усіх seq_cst-дій",
         "коли не певен — бери це", "#fdecea", POS, "найдорожчий"),
    ]
    y = 70
    for name, what, use, fl, st, cost in rows:
        h = 82
        p.append(rect(60, y, W - 120, h, fill=fl, stroke=st, sw=2, rx=10))
        p.append(text(80, y + 30, name, size=15, bold=True, color=st, anchor="start"))
        p.append(text(80, y + 54, what, size=12, anchor="start"))
        p.append(text(80, y + 72, "приклад: " + use, size=11, color=MUTED, anchor="start"))
        p.append(text(W - 80, y + 30, cost, size=11, color=st, anchor="end", italic=True))
        y += h + 12

    # вісь сили ліворуч
    p.append(text(30, 100, "слабше", size=11, color=MUTED))
    p.append(text(30, 300, "сильніше", size=11, color=MUTED))
    p.append(arrow(30, 300, 30, 120, color=MUTED, sw=1.5))

    render(os.path.join(OUT, 'order-ladder.svg'), W, H, *p)


# ── HIST-фігура: лінія спадкоємності ідеї DRF-SC ────────────────────────────
def fig_hist_lineage():
    W, H = 900, 470
    p = []
    p.append(text(W / 2, 32, "Ідея йшла в C++ 30 років — і прийшла ззовні", size=17, bold=True))

    # горизонтальна вісь часу
    ax0, ax1, ay = 70, W - 40, 90
    p.append(line(ax0, ay, ax1, ay, color=MUTED, sw=2))
    for yr, xx in [(1979, ax0 + 20), (1990, 235), (1995, 360),
                   (2004, 560), (2008, 700), (2011, ax1 - 40)]:
        p.append(line(xx, ay - 6, xx, ay + 6, color=MUTED, sw=2))
        p.append(text(xx, ay - 14, str(yr), size=12, bold=True, color=MUTED))

    # віхи як картки під віссю, кожна зі своєю смугою «звідки»
    cards = [
        (ax0 + 20, 130, "Лемпорт", ["послідовна", "узгодженість", "(SC) — означення"], NEG),
        (235, 130, "Адве й Гілл", ["Weak Ordering:", "SC для програм", "без гонок"], FIELD),
        (360, 130, "Адве й", ["Ґарачорлу:", "туторіал —", "мова DRF"], FIELD),
        (560, 130, "Java JSR-133", ["DRF-SC уперше", "в живій мові", "(happens-before)"], POS),
        (700, 130, "Бем і Адве", ["PLDI'08:", "фундамент", "моделі C++"], POS),
        (ax1 - 40, 130, "C++11", ["std::atomic +", "6 memory_order", "у стандарті"], INK),
    ]
    for cx, cy, name, body, clr in cards:
        fl = "#eafaf1" if clr == FIELD else ("#eaf0fd" if clr == NEG else
             ("#fdecea" if clr == POS else FILL))
        # лінія від віхи на осі до картки
        p.append(line(cx, ay + 6, cx, cy - 34, color=MUTED, sw=1, dash="3,3"))
        p.append(text(cx, cy - 20, name, size=12, bold=True, color=clr))
        p.append(fitbox(cx - 78, cy - 8, 156, 74, "\n".join(body),
                        size=11, pad=7, fill=fl, stroke=clr))

    # три «річки», що зливаються: апаратна теорія + Java-досвід → C++
    p.append(text(W / 2, 320, "три струмені, що злилися в модель C++", size=12, italic=True, color=MUTED))
    b, w, h = textbox(200, 360, ["апаратна теорія узгодженості", "(Лемпорт · Адве · Ґарачорлу)"],
                      size=11, pad=8, fill="#eafaf1", stroke=FIELD)
    p.append(b)
    b, w, h = textbox(560, 360, ["перша обкатка DRF-SC", "у справжній мові — Java"],
                      size=11, pad=8, fill="#eaf0fd", stroke=NEG)
    p.append(b)
    b, w, h = textbox(W / 2, 430, ["C++11: та сама ідея DRF-SC,",
                                   "але з новими рівнями (relaxed, acquire/release, seq_cst)"],
                      size=12, pad=9, fill="#fdecea", stroke=POS, bold=True)
    p.append(b)
    p.append(arrow(200, 384, 400, 415, color=MUTED, sw=1.6))
    p.append(arrow(560, 384, 470, 415, color=MUTED, sw=1.6))

    render(os.path.join(OUT, 'hist-lineage.svg'), W, H, *p)


# ── HIST-фігура: чого стандарт не бачив до C++11 ─────────────────────────────
def fig_hist_before_after():
    W, H = 820, 430
    p = []
    p.append(text(W / 2, 32, "Що стандарт знав про потоки: до C++11 і після", size=17, bold=True))

    # ліворуч: до C++11 — порожнеча
    lx = 50
    p.append(text(lx + 160, 70, "до C++11 (C++03 і раніше)", size=14, bold=True, color=POS))
    p.append(rect(lx, 84, 320, 300, fill="#fdecea", stroke=POS, sw=2, rx=12))
    before = [
        "слова «потік» у стандарті НЕМА",
        "порядок пам'яті не визначено",
        "багатопотоковість — поза мовою:",
        "  • розширення компілятора",
        "  • бібліотека pthreads (POSIX)",
        "  • обіцянки, не гарантії мови",
        "компілятор вільний ламати код,",
        "бо про інші потоки «не знає»",
    ]
    yy = 118
    for i, s in enumerate(before):
        start = lx + 18
        clr = INK
        p.append(text(start, yy, s, size=12, anchor="start", color=clr,
                      bold=(i == 0)))
        yy += 33

    # праворуч: після C++11
    rx = 450
    p.append(text(rx + 160, 70, "C++11 і далі", size=14, bold=True, color=FIELD))
    p.append(rect(rx, 84, 320, 300, fill="#eafaf1", stroke=FIELD, sw=2, rx=12))
    after = [
        "потоки — В САМІЙ мові",
        "модель пам'яті визначена",
        "гонка даних → невизначеність",
        "std::thread, std::mutex",
        "std::atomic<T> — неподільність",
        "six memory_order:",
        "  relaxed · consume · acquire",
        "  release · acq_rel · seq_cst",
    ]
    yy = 118
    for i, s in enumerate(after):
        p.append(text(rx + 18, yy, s, size=12, anchor="start",
                      bold=(i == 0)))
        yy += 33

    # стрілка переходу
    p.append(arrow(lx + 322, 234, rx - 2, 234, color=INK, sw=2.4))
    p.append(text((lx + 322 + rx) / 2, 220, "2011", size=13, bold=True))

    b, w, h = textbox(W / 2, 410, "уперше мова САМА визнала, що код буває багатопотоковим",
                      size=13, pad=9, fill=FILL, stroke=INK, bold=True)
    p.append(b)

    render(os.path.join(OUT, 'hist-before-after.svg'), W, H, *p)


# ── MATH-фігура: повний порядок проти часткового ────────────────────────────
def fig_partial_order():
    W, H = 780, 400
    p = []
    p.append(text(W / 2, 30, "Повний порядок vs частковий: упорядковано все чи лише пов'язане", size=15, bold=True))

    p.append(line(W / 2, 55, W / 2, 372, color=MUTED, sw=1, dash="4,4"))

    # ліворуч: повний порядок — усі в ряд
    p.append(text(190, 66, "повний порядок", size=13, bold=True, color=NEG))
    p.append(text(190, 84, "будь-яку пару можна порівняти", size=10, color=MUTED))
    seq = ["e1", "e2", "e3", "e4", "e5"]
    ly = 122
    for i, s in enumerate(seq):
        cy = ly + i * 46
        p.append(circle(190, cy, 16, fill="#eaf0fd", stroke=NEG, sw=1.8))
        p.append(text(190, cy + 5, s, size=12, bold=True, color=NEG))
        if i < len(seq) - 1:
            p.append(arrow(190, cy + 17, 190, cy + 29, color=NEG, sw=1.6))

    # праворуч: частковий — дві гілки з одним містком
    p.append(text(585, 66, "частковий порядок", size=13, bold=True, color=FIELD))
    p.append(text(585, 84, "пов'язане впорядковано, решта — ні", size=10, color=MUTED))
    ax, ay = 500, 128
    p.append(text(ax, ay - 22, "потік A", size=10, color=MUTED))
    for i, s in enumerate(["a1", "a2", "a3"]):
        cy = ay + i * 66
        p.append(circle(ax, cy, 16, fill="#eafaf1", stroke=FIELD, sw=1.8))
        p.append(text(ax, cy + 5, s, size=12, bold=True, color=FIELD))
        if i < 2:
            p.append(arrow(ax, cy + 17, ax, cy + 49, color=FIELD, sw=1.6))
    bx, by = 670, 160
    p.append(text(bx, by - 22, "потік B", size=10, color=MUTED))
    for i, s in enumerate(["b1", "b2", "b3"]):
        cy = by + i * 66
        p.append(circle(bx, cy, 16, fill="#eafaf1", stroke=FIELD, sw=1.8))
        p.append(text(bx, cy + 5, s, size=12, bold=True, color=FIELD))
        if i < 2:
            p.append(arrow(bx, cy + 17, bx, cy + 49, color=FIELD, sw=1.6))
    # єдиний місток a2 → b1
    p.append(arrow(ax + 16, ay + 66, bx - 16, by, color=NEG, sw=2.2))
    p.append(text(585, 210, "місток", size=10, color=NEG, bold=True))
    b, w, h = textbox(585, 360, ["a3 і b3 — непорівнянні:", "жодне не «раніше», і це нормально"],
                      size=11, pad=8, stroke=FIELD, fill="#eafaf1")
    p.append(b)

    render(os.path.join(OUT, 'partial-order.svg'), W, H, *p)


# ── MATH-фігура: дві цеглини — sequenced-before + synchronizes-with ──────────
def fig_hb_edges():
    W, H = 800, 440
    p = []
    p.append(text(W / 2, 30, "Дві цеглини happens-before: порядок у потоці + місток між потоками", size=15, bold=True))

    lx = 155
    p.append(text(lx, 66, "потік-виробник", size=13, bold=True, color=FIELD))
    prod = ["data = 42;", "buf[i] = x;", "ready.store(release)"]
    py0 = 102
    for i, s in enumerate(prod):
        cy = py0 + i * 80
        st = FIELD if i == 2 else LINE
        fl = "#eafaf1" if i == 2 else FILL
        b, w, h = textbox(lx, cy, s, size=12, pad=8, min_w=200, stroke=st, fill=fl, bold=(i == 2))
        p.append(b)
        if i < 2:
            p.append(arrow(lx, cy + 20, lx, cy + 58, color=MUTED, sw=1.8))
            p.append(text(lx + 118, cy + 42, "seq-before", size=9, color=MUTED, anchor="start"))

    rx = 645
    p.append(text(rx, 66, "потік-споживач", size=13, bold=True, color=NEG))
    cons = ["ready.load(acquire)", "use(data);", "read(buf[i]);"]
    cy0 = 182
    for i, s in enumerate(cons):
        cy = cy0 + i * 80
        st = NEG if i == 0 else LINE
        fl = "#eaf0fd" if i == 0 else FILL
        b, w, h = textbox(rx, cy, s, size=12, pad=8, min_w=200, stroke=st, fill=fl, bold=(i == 0))
        p.append(b)
        if i < 2:
            p.append(arrow(rx, cy + 20, rx, cy + 58, color=MUTED, sw=1.8))
            p.append(text(rx - 118, cy + 42, "seq-before", size=9, color=MUTED, anchor="end"))

    # місток synchronizes-with: store → load
    p.append(arrow(lx + 100, py0 + 2 * 80, rx - 100, cy0, color=NEG, sw=2.4))
    p.append(text(W / 2, 252, "synchronizes-with", size=12, color=NEG, bold=True, italic=True))
    p.append(text(W / 2, 268, "(load побачив значення store)", size=10, color=MUTED))

    b, w, h = textbox(W / 2, 414, "Тільки діагональ перетинає межу потоків — без неї стовпчики не пов'язані",
                      size=12, pad=9, stroke=NEG, fill="#eaf0fd", bold=True)
    p.append(b)

    render(os.path.join(OUT, 'hb-edges.svg'), W, H, *p)


# ── MATH-фігура: happens-before визначає видимість; без ребра — UB ───────────
def fig_hb_defines_visibility():
    W, H = 760, 400
    p = []
    p.append(text(W / 2, 30, "«Видно» має сенс лише там, де є ребро happens-before", size=15, bold=True))

    # верх: є ребро → визначено
    p.append(text(120, 80, "є ребро", size=13, bold=True, color=FIELD))
    b, w, h = textbox(205, 120, "запис: data = 42", size=12, pad=8, min_w=180, stroke=FIELD, fill="#eafaf1")
    p.append(b)
    b, w, h = textbox(555, 120, "читання: use(data)", size=12, pad=8, min_w=180, stroke=NEG, fill="#eaf0fd")
    p.append(b)
    p.append(arrow(300, 120, 460, 120, color=INK, sw=2.4))
    p.append(text(380, 106, "happens-before", size=11, bold=True, italic=True))
    b, w, h = textbox(W / 2, 170, "читач ГАРАНТОВАНО бачить 42 — визначено, однаково для всіх",
                      size=12, pad=8, stroke=FIELD, fill="#eafaf1", bold=True)
    p.append(b)

    p.append(line(70, 212, W - 70, 212, color=MUTED, sw=1, dash="5,5"))

    # низ: нема ребра → UB
    p.append(text(120, 252, "нема ребра", size=13, bold=True, color=POS))
    b, w, h = textbox(205, 292, "запис: x = 1", size=12, pad=8, min_w=180, stroke=POS, fill="#fdecea")
    p.append(b)
    b, w, h = textbox(555, 292, "читання: r = x", size=12, pad=8, min_w=180, stroke=POS, fill="#fdecea")
    p.append(b)
    p.append(line(300, 292, 460, 292, color=MUTED, sw=1.6, dash="6,5"))
    p.append(text(380, 286, "?", size=20, bold=True, color=POS))
    b, w, h = textbox(W / 2, 358, ["конфліктні доступи без порядку → гонка даних",
                                   "об'єктивного «раніше» немає → НЕВИЗНАЧЕНА ПОВЕДІНКА"],
                      size=12, pad=9, stroke=POS, fill="#fdecea", bold=True)
    p.append(b)

    render(os.path.join(OUT, 'hb-defines-visibility.svg'), W, H, *p)


if __name__ == '__main__':
    fig_torn_vs_atomic()
    fig_reordering()
    fig_release_acquire()
    fig_order_ladder()
    fig_hist_lineage()
    fig_hist_before_after()
    fig_partial_order()
    fig_hb_edges()
    fig_hb_defines_visibility()
    print("figures written to", OUT)
