# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── chain: ланцюг несправність → помилка → відмова, пройдений НАЗАД ───────────
# Ідея: у руках правий кінець (видима відмова), потрібен лівий (причина);
# наївний шлях стрибає до привида, метод веде ланцюгом назад.
def fig_chain():
    W, H = 720, 356
    p = []
    p.append(text(W / 2, 30, "Пошук несправності — ланцюг, пройдений назад", size=17, bold=True))

    # три ланки ланцюга
    links = [
        (110, "Несправність", "першопричина:\nбіт, дріт, рядок", POS),
        (360, "Помилка", "стан став\nхибним", "#b26a00"),
        (610, "Відмова", "видима\nдурня", FIELD),
    ]
    cy = 150
    bw, bh = 150, 78
    for cx, name, sub, col in links:
        p.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=FILL, stroke=col, sw=2))
        p.append(text(cx, cy - 12, name, size=14, bold=True, color=col))
        p.append(mtext(cx, cy + 8, sub, size=10.5, color=MUTED, lh=1.2))

    # штатний напрям ланцюга (тонкі сірі стрілки вперед)
    p.append(arrow(185, cy - 24, 285, cy - 24, color=MUTED, sw=1.4))
    p.append(arrow(435, cy - 24, 535, cy - 24, color=MUTED, sw=1.4))
    p.append(text(235, cy - 32, "визріває →", size=10, color=MUTED, italic=True))
    p.append(text(485, cy - 32, "визріває →", size=10, color=MUTED, italic=True))

    # напрям пошуку — назад, товстою лінією знизу (нижче рамок, без дотику)
    p.append(arrow(535, cy + 56, 185, cy + 56, color=INK, sw=2.4))
    p.append(text(360, cy + 74, "пошук іде назад: від видимого до схованого", size=12, bold=True, color=INK))

    # «на руках у тебе» — маркер над правою ланкою
    p.append(text(610, cy - bh / 2 - 12, "◀ це на руках", size=11, color=FIELD, italic=True))
    p.append(text(110, cy - bh / 2 - 12, "це шукаємо ▶", size=11, color=POS, italic=True))

    # наївний стрибок — пунктир від відмови просто до випадкової причини
    p.append(line(610, cy + bh / 2, 150, cy + bh / 2 + 78, color=POS, sw=1.6, dash="5 5"))
    p.append(text(400, cy + bh / 2 + 84, "наївний стрибок навмання → майже завжди в привида",
                  size=11, color=POS, italic=True))

    render(os.path.join(OUT, "chain.svg"), W, H, *p)


# ── bisect: ділення навпіл уздовж тракту сигналу ─────────────────────────────
# Ідея: щуп посередині одним виміром відкидає цілу половину підозрюваних.
def fig_bisect():
    W, H = 720, 360
    p = []
    p.append(text(W / 2, 30, "Ділити навпіл: один вимір відкидає половину", size=17, bold=True))

    stages = ["Давач", "Підсилю-\nвач", "АЦП", "Обчис-\nлення", "Вихід"]
    n = len(stages)
    bw, gap = 96, 26
    x0 = (W - (bw * n + gap * (n - 1))) / 2
    cy = 150
    bh = 62
    centers = []
    for i, s in enumerate(stages):
        x = x0 + i * (bw + gap)
        cx = x + bw / 2
        centers.append(cx)
        col = FIELD if i < 2 else (INK if i == 2 else POS)
        p.append(rect(x, cy - bh / 2, bw, bh, fill=FILL, stroke=col, sw=1.8))
        p.append(mtext(cx, cy - 2, s, size=11.5, color=INK, lh=1.05, bold=True))
        if i < n - 1:
            p.append(arrow(x + bw + 2, cy, x + bw + gap - 2, cy, color=MUTED, sw=1.6))

    # вихід — хиба
    p.append(text(centers[-1], cy - bh / 2 - 12, "тут хиба!", size=11.5, bold=True, color=POS))

    # щуп посередині (АЦП)
    mid = centers[2]
    p.append(line(mid, cy - bh / 2 - 46, mid, cy - bh / 2 - 2, color="#2457d6", sw=2.2))
    p.append(circle(mid, cy - bh / 2 - 52, 7, fill="#eaf0fd", stroke="#2457d6", sw=2))
    p.append(text(mid, cy - bh / 2 - 62, "щуп посередині", size=11.5, bold=True, color="#2457d6"))

    # дві гілки висновку
    yb = cy + bh / 2 + 34
    p.append(rect(x0, yb, bw * 2 + gap, 52, fill="#eef8f1", stroke=FIELD, sw=1.6))
    p.append(mtext(x0 + (bw * 2 + gap) / 2, yb + 20,
                   "число тут ПРАВИЛЬНЕ →\nліва половина здорова", size=11, color=INK, lh=1.25, bold=True))

    rx = x0 + (bw + gap) * 3
    p.append(rect(rx, yb, bw * 2 + gap, 52, fill="#fdeeec", stroke=POS, sw=1.6))
    p.append(mtext(rx + (bw * 2 + gap) / 2, yb + 20,
                   "число тут ХИБНЕ →\nправа половина здорова", size=11, color=INK, lh=1.25, bold=True))

    p.append(text(W / 2, 344, "кожен розріз ділить решту підозрюваних надвоє — простір тане вдвічі за крок",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "bisect.svg"), W, H, *p)


# ── suspects: список підозрюваних тане log₂(N) кроками (для proj-вставки) ─────
# Ідея: активне вікно [lo..hi] стискається вдвічі за крок; винуватець усередині.
def fig_suspects():
    W, H = 720, 452
    p = []
    p.append(text(W / 2, 30, "Половинний пошук над списком підозрюваних", size=17, bold=True))

    N = 16
    cell = 40
    x0 = (W - N * cell) / 2
    rows = [
        (66,  0,  15, "усі 16 підозрюваних", MUTED),
        (152, 8,  15, "збій є → винен у правій половині [8..15]", POS),
        (238, 8,  11, "збій зник → винен ліворуч [8..11]",        NEG),
        (324, 10, 11, "звузили до двох [10..11]",                 "#b26a00"),
    ]
    for cy, lo, hi, label, col in rows:
        for i in range(N):
            x = x0 + i * cell
            inside = lo <= i <= hi
            fill = "#fdeeec" if (inside and col is POS) else \
                   "#eaf0fd" if (inside and col is NEG) else \
                   "#fff6e6" if (inside and col == "#b26a00") else \
                   (FILL if inside else "#eef0f2")
            stroke = col if inside else "#c8ccd0"
            p.append(rect(x + 2, cy, cell - 4, 26, fill=fill, stroke=stroke, sw=1.6 if inside else 1.0))
            p.append(text(x + cell / 2, cy + 18, str(i), size=11,
                          color=(INK if inside else "#aab0b6"), bold=inside))
        # підпис — під рядком, по центру таблиці
        p.append(text(W / 2, cy + 44, label, size=12, color=col, bold=True))
    # винуватець — слот 10, позначка знизу від останнього рядка
    gx = x0 + 10 * cell + cell / 2
    p.append(line(gx, 324 + 30, gx, 406, color=INK, sw=1.4, dash="3 3"))
    p.append(text(gx, 422, "справжній винуватець — №10", size=12, bold=True, color=INK))

    p.append(text(W / 2, 444, "кожен дослід ділить активне вікно навпіл: 16 → 8 → 4 → 2 → 1 за 4 кроки, не 16",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "suspects.svg"), W, H, *p)


# ── flaky: недетермінований предикат заводить бісекцію не в ту половину ───────
# Ідея: одна хибна відповідь предиката — і півдерева пошуку викреслено помилково.
def fig_flaky():
    W, H = 720, 336
    p = []
    p.append(text(W / 2, 30, "Плавучий предикат ламає бісекцію", size=17, bold=True))

    # ліворуч: чесний предикат
    lx = 180
    p.append(text(lx, 66, "детермінований предикат", size=13, bold=True, color=FIELD))
    p.append(rect(lx - 120, 82, 240, 46, fill="#eef8f1", stroke=FIELD, sw=1.6))
    p.append(mtext(lx, 100, "увімкнув причину → впало ЩОРАЗУ\nвимкнув → не впало ЩОРАЗУ",
                   size=10.5, color=INK, lh=1.25))
    p.append(text(lx, 158, "«так/ні» чесне", size=11.5, bold=True, color=FIELD))
    p.append(arrow(lx, 168, lx, 206, color=FIELD, sw=1.8))
    p.append(rect(lx - 110, 210, 220, 44, fill=FILL, stroke=FIELD, sw=1.6))
    p.append(mtext(lx, 228, "вікно ділиться навпіл\nвірно щокроку → винуватець",
                   size=10.5, color=INK, lh=1.25))

    # праворуч: плавучий предикат
    rx = 540
    p.append(text(rx, 66, "плавучий предикат", size=13, bold=True, color=POS))
    p.append(rect(rx - 120, 82, 240, 46, fill="#fdeeec", stroke=POS, sw=1.6))
    p.append(mtext(rx, 100, "збій раз на годину «коли схоче»\nне впало за 5 хв — хибне чи не пощастило?",
                   size=10.5, color=INK, lh=1.25))
    p.append(text(rx, 158, "одна хибна «ні»", size=11.5, bold=True, color=POS))
    p.append(arrow(rx, 168, rx, 206, color=POS, sw=1.8))
    p.append(rect(rx - 118, 210, 236, 44, fill="#fdeeec", stroke=POS, sw=1.6))
    p.append(mtext(rx, 228, "відкинуто ЗДОРОВУ половину\n(з винуватцем) → пошук у пустелі",
                   size=10.5, color=INK, lh=1.25))

    # роздільник
    p.append(line(360, 60, 360, 264, color="#c8ccd0", sw=1.2, dash="4 4"))
    p.append(text(W / 2, 300, "спершу приборкай плавучість (зроби, щоб падало щоразу) — потім дели навпіл",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 322, "бісекція коректна рівно доти, доки кожна відповідь предиката однозначна",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "flaky.svg"), W, H, *p)


# ── heisenbug: журнал сам зрушує тайминг і ховає баг ──────────────────────────
# Ідея: важкий друк у журналі розтягує вікно й гасить гонку — треба легкий слід.
def fig_heisenbug():
    W, H = 720, 320
    p = []
    p.append(text(W / 2, 30, "Гейзенбаг від самого журналу", size=17, bold=True))

    # вісь часу — дві доріжки
    ax = 90
    aw = 540
    # верхня: без журналу — гонка спрацьовує
    y1 = 96
    p.append(text(ax - 6, y1 - 22, "без журналу", size=12, bold=True, color=POS, anchor="start"))
    p.append(line(ax, y1, ax + aw, y1, color=INK, sw=1.4))
    # вузьке вікно гонки
    p.append(rect(ax + 250, y1 - 12, 40, 24, fill="#fdeeec", stroke=POS, sw=1.6))
    p.append(text(ax + 270, y1 + 5, "гонка", size=9.5, color=POS, bold=True))
    p.append(text(ax + 270, y1 - 20, "вузьке вікно", size=9.5, color=POS))
    p.append(text(ax + aw + 8, y1 + 5, "БАГ Є", size=11.5, bold=True, color=POS, anchor="start"))

    # нижня: з важким друком у журналі — вікно розтягнулось, гонка не встигає
    y2 = 200
    p.append(text(ax - 6, y2 - 22, "з важким друком у журналі", size=12, bold=True, color=NEG, anchor="start"))
    p.append(line(ax, y2, ax + aw, y2, color=INK, sw=1.4))
    # друк вставляє затримку — зсув
    p.append(rect(ax + 150, y2 - 12, 150, 24, fill="#eaf0fd", stroke=NEG, sw=1.6))
    p.append(text(ax + 225, y2 + 5, "друк розтягнув крок", size=9.5, color=NEG, bold=True))
    p.append(text(ax + 470, y2 - 12, "×", size=20, color=NEG, bold=True))
    p.append(text(ax + aw + 8, y2 + 5, "баг зник", size=11.5, bold=True, color=NEG, anchor="start"))

    p.append(text(W / 2, 268, "спостереження змінило те, що спостерігали: важкий журнал зрушив тайминг",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 292, "лік — легкий слід (лічильник у RAM, зонд), а важкий друк лишай ПОЗА гарячим шляхом",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "heisenbug.svg"), W, H, *p)


# ── debug-timeline: дуга від слова до методу (для вставки hist-debugging) ─────
# Ідея: слово «bug» старе (Едісон→словник→міль), а передана ДИСЦИПЛІНА прийшла
# аж на ~130 років пізніше (Аганс, Целлер). Події тиснуться у два кластери з
# великою порожнечею між ними — тому шкала не лінійна: рівні слоти + злам осі.
def fig_timeline():
    W, H = 760, 340
    p = []
    p.append(text(W / 2, 30, "Півтора століття: від назви до дисципліни", size=17, bold=True))

    ax_y = 178
    # три слоти зліва (епоха слова) + злам + два слоти справа (епоха методу)
    left_x = [70, 210, 350]            # 1876, 1934, 1947
    brk = 455                          # позиція зламу осі
    right_x = [560, 690]               # 2002, 2005

    # вісь: суцільна ліворуч, суцільна праворуч, розрив посередині
    p.append(line(45, ax_y, brk - 22, ax_y, color=INK, sw=2.4))
    p.append(line(brk + 22, ax_y, W - 30, ax_y, color=INK, sw=2.4))
    p.append(arrow(W - 32, ax_y, W - 28, ax_y, color=INK, sw=2.4))
    # знак зламу осові (дві скісні риски)
    for dx in (-22, 22):
        p.append(line(brk + dx - 6, ax_y + 8, brk + dx + 6, ax_y - 8, color=INK, sw=1.6))
    p.append(text(brk, ax_y - 20, "≈130 років", size=11, bold=True, color=MUTED))
    p.append(text(brk, ax_y + 20, "порожнеча:", size=10.5, color=MUTED, italic=True))
    p.append(text(brk, ax_y + 33, "слово є,", size=10.5, color=MUTED, italic=True))
    p.append(text(brk, ax_y + 46, "методу нема", size=10.5, color=MUTED, italic=True))

    # смуги-епохи над віссю
    p.append(text((left_x[0] + left_x[-1]) / 2, 58, "епоха СЛОВА (жарт про міль)",
                  size=12.5, bold=True, color=MUTED))
    p.append(text((right_x[0] + right_x[-1]) / 2, 58, "епоха МЕТОДУ",
                  size=12.5, bold=True, color=FIELD))

    # події: (x, рік, підпис, над/під, колір)
    events = [
        (left_x[0],  "1876", "Едісон уживає\n«bug» у нотатках", "down", POS),
        (left_x[1],  "1934", "словник Вебстера:\n«bug» = вада апарата", "up", POS),
        (left_x[2],  "1947", "міль у реле 70 —\nкаламбур, не хрестини", "down", INK),
        (right_x[0], "2002", "Аганс: 9 правил\nремесла", "up", FIELD),
        (right_x[1], "2005", "Целлер: наук. метод\n+ дельта-дебагінг", "down", FIELD),
    ]
    for x, year, label, side, col in events:
        p.append(circle(x, ax_y, 6, fill="#ffffff", stroke=col, sw=2.4))
        lines = label.split("\n")
        if side == "down":
            p.append(text(x, ax_y + 24, year, size=12, bold=True, color=col))
            p.append(mtext(x, ax_y + 44, lines, size=10.5, color=INK, lh=1.2))
        else:
            p.append(text(x, ax_y - 14, year, size=12, bold=True, color=col))
            ly = ax_y - 34 - (len(lines) - 1) * 10.5 * 1.2
            p.append(mtext(x, ly, lines, size=10.5, color=INK, lh=1.2))

    p.append(text(W / 2, 328,
                  "слово старше за міль на 70 років; передану дисципліну дали аж у 2000-х",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "debug-timeline.svg"), W, H, *p)


# ══════════════════════════════════════════════════════════════════════════════
#  ФІГУРИ ДЕТАЛЬНОЇ СТАТТІ (-d): інформація на крок, вартісний розріз, довіра «ні»
# ══════════════════════════════════════════════════════════════════════════════

# ── info-per-cut: біти інформації на один дослід vs частка розрізу ────────────
# Ідея: дослід дає найбільше інформації (1 біт), коли ділить простір рівно навпіл;
# перекошений розріз дає менше — крива H(p) = −p·log₂p − (1−p)·log₂(1−p), пік у 0.5.
def fig_info_per_cut():
    import math
    W, H = 720, 400
    p = []
    p.append(text(W / 2, 30, "Скільки біт дає один дослід залежно від розрізу", size=17, bold=True))

    # осі
    ox, oy = 110, 320          # початок координат (лівий низ)
    aw, ah = 500, 230          # довжина осей
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))          # X
    p.append(line(ox, oy, ox, oy - ah - 8, color=INK, sw=1.8))       # Y
    p.append(arrow(ox + aw, oy, ox + aw + 6, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy - ah - 8, ox, oy - ah - 14, color=INK, sw=1.8))

    # підписи осей
    p.append(text(ox + aw / 2, oy + 52, "частка підозрюваних у ввімкненій половині p", size=12, color=INK))
    p.append(text(ox - 78, oy - ah / 2, "біт на дослід", size=12, color=INK, anchor="middle"))
    # вертикальний підпис через поворот важко — лишаємо горизонтально ліворуч над віссю
    # ділення X: 0, 0.25, 0.5, 0.75, 1
    for frac, lbl in [(0.0, "0"), (0.25, "¼"), (0.5, "½"), (0.75, "¾"), (1.0, "1")]:
        x = ox + frac * aw
        p.append(line(x, oy, x, oy + 5, color=INK, sw=1.4))
        p.append(text(x, oy + 20, lbl, size=11, color=MUTED))
    # ділення Y: 0, 0.5, 1.0 біт
    for val, lbl in [(0.0, "0"), (0.5, "0.5"), (1.0, "1.0")]:
        y = oy - val * ah
        p.append(line(ox - 5, y, ox, y, color=INK, sw=1.4))
        p.append(text(ox - 16, y + 4, lbl, size=11, color=MUTED, anchor="end"))

    # крива ентропії H(p)
    def Hbits(pp):
        if pp <= 0 or pp >= 1:
            return 0.0
        return -pp * math.log2(pp) - (1 - pp) * math.log2(1 - pp)
    pts = []
    steps = 100
    for i in range(steps + 1):
        pp = i / steps
        x = ox + pp * aw
        y = oy - Hbits(pp) * ah
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts), FIELD))

    # пік у 0.5 — 1 біт
    xm = ox + 0.5 * aw
    ym = oy - 1.0 * ah
    p.append(line(xm, oy, xm, ym, color=MUTED, sw=1.2, dash="4 4"))
    p.append(circle(xm, ym, 6, fill="#eef8f1", stroke=FIELD, sw=2.2))
    p.append(text(xm, ym - 14, "½ навпіл → 1 повний біт (максимум)", size=11.5, bold=True, color=FIELD))

    # перекіс — мало інформації: точка p=0.9
    xb = ox + 0.9 * aw
    yb = oy - Hbits(0.9) * ah
    p.append(circle(xb, yb, 5, fill="#fdeeec", stroke=POS, sw=2))
    p.append(text(xb + 4, yb - 10, "перекіс 9:1 → лише 0.47 біт", size=11, color=POS, anchor="middle"))

    p.append(text(W / 2, 388, "рівний розріз викачує максимум невизначеності за крок; косий — марнує дослід",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "info-per-cut.svg"), W, H, *p)


# ── cost-weighted: коли досліди різняться ціною, оптимальний розріз зсувається ─
# Ідея: якщо перевірити ЛІВУ половину дешево, а праву дорого — оптимум зсувається
# так, щоб дешевий бік ніс БІЛЬШЕ підозрюваних (кладемо ризик туди, де дешево ділити).
def fig_cost_weighted():
    W, H = 720, 356
    p = []
    p.append(text(W / 2, 30, "Розріз за вартістю: дешевий бік бере більше підозрюваних", size=16, bold=True))

    n = 12
    cell = 44
    x0 = (W - n * cell) / 2
    # два ряди: наївний рівний розріз проти вартісного
    def draw_row(cy, cut, label, note):
        for i in range(n):
            x = x0 + i * cell
            left = i < cut
            fill = "#eef8f1" if left else "#fdeeec"
            stroke = FIELD if left else POS
            p.append(rect(x + 2, cy, cell - 4, 30, fill=fill, stroke=stroke, sw=1.5))
        # межа розрізу
        bx = x0 + cut * cell
        p.append(line(bx, cy - 12, bx, cy + 42, color=INK, sw=2.4))
        p.append(text(x0 - 10, cy + 20, label, size=11.5, bold=True, color=INK, anchor="end"))
        p.append(text(W / 2, cy + 60, note, size=11, color=MUTED, italic=True))

    # рівний розріз (6|6) — коли ціни рівні
    draw_row(84, 6, "рівні ціни:",
             "6 | 6 — рівний розріз оптимальний, коли обидва досліди коштують однаково")
    # вартісний: лівий дослід дешевий → лівий бік бере більше (9|3)
    draw_row(190, 9, "лівий дослід\nдешевий:",
             "9 | 3 — дешевому боку віддаємо більше підозрюваних: за ту саму ціну ділимо глибше")

    # підписи «дешево / дорого» під нижнім рядом
    p.append(text(x0 + 4.5 * cell, 176, "дешевий дослід (напр. читання регістра)", size=10, color=FIELD))
    p.append(text(x0 + 10.5 * cell, 176, "дорогий (перепайка)", size=10, color=POS))

    p.append(text(W / 2, 300, "оптимум мінімізує не число кроків, а СУМАРНУ ціну: біти на гривню, не біти на крок",
                  size=12, bold=True, color=INK))
    p.append(text(W / 2, 324, "формально — зважуй розріз так, щоб приріст інформації на одиницю вартості був рівний з обох боків",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "cost-weighted.svg"), W, H, *p)


# ── flaky-trials: скільки дослідів треба, щоб довіряти «не відтворилось» ──────
# Ідея: якщо баг падає з імовірністю p за спробу, то N чистих спроб лишають шанс
# (1−p)^N, що він просто причаївся. Крива спаду + поріг довіри 5 %.
def fig_flaky_trials():
    import math
    W, H = 720, 400
    p = []
    p.append(text(W / 2, 30, "Скільки чистих спроб, щоб вірити «не відтворюється»", size=16, bold=True))

    ox, oy = 96, 320
    aw, ah = 520, 230
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(line(ox, oy, ox, oy - ah - 8, color=INK, sw=1.8))
    p.append(arrow(ox + aw, oy, ox + aw + 6, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy - ah - 8, ox, oy - ah - 14, color=INK, sw=1.8))
    p.append(text(ox + aw / 2, oy + 52, "число чистих спроб поспіль  N", size=12, color=INK))
    p.append(text(ox + 6, oy - ah - 22, "шанс, що баг просто причаївся  (1−p)ᴺ", size=12, color=INK, anchor="start"))

    Nmax = 60
    # X-мітки
    for nn in [0, 15, 30, 45, 60]:
        x = ox + nn / Nmax * aw
        p.append(line(x, oy, x, oy + 5, color=INK, sw=1.4))
        p.append(text(x, oy + 20, str(nn), size=11, color=MUTED))
    # Y-мітки (0..1)
    for val, lbl in [(0.0, "0"), (0.5, "50%"), (1.0, "100%")]:
        y = oy - val * ah
        p.append(line(ox - 5, y, ox, y, color=INK, sw=1.4))
        p.append(text(ox - 12, y + 4, lbl, size=11, color=MUTED, anchor="end"))

    # три криві для різних p
    curves = [(0.30, POS, "p = 0.3 (падає часто)"),
              (0.10, "#b26a00", "p = 0.1"),
              (0.03, NEG, "p = 0.03 (рідкісний)")]
    for pp, col, lbl in curves:
        pts = []
        for i in range(Nmax + 1):
            x = ox + i / Nmax * aw
            y = oy - (1 - pp) ** i * ah
            pts.append("%.1f,%.1f" % (x, y))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (" ".join(pts), col))

    # поріг довіри 5 %
    yth = oy - 0.05 * ah
    p.append(line(ox, yth, ox + aw, yth, color=FIELD, sw=1.6, dash="6 4"))
    p.append(text(ox + aw - 4, yth - 8, "поріг довіри 5%", size=11, bold=True, color=FIELD, anchor="end"))

    # легенда праворуч угорі
    lx, ly = ox + aw - 210, oy - ah + 6
    for k, (pp, col, lbl) in enumerate(curves):
        yy = ly + k * 20
        p.append(line(lx, yy, lx + 22, yy, color=col, sw=2.4))
        p.append(text(lx + 28, yy + 4, lbl, size=11, color=INK, anchor="start"))

    # приклад: p=0.03 → треба ~98 спроб; p=0.3 → ~9
    p.append(text(W / 2, 380, "p=0.3 → 5% вже за 9 спроб;  p=0.03 → аж ~98 спроб (ось чому спершу підсилюють p)",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "flaky-trials.svg"), W, H, *p)


if __name__ == "__main__":
    fig_chain()
    fig_bisect()
    fig_suspects()
    fig_flaky()
    fig_heisenbug()
    fig_timeline()
    fig_info_per_cut()
    fig_cost_weighted()
    fig_flaky_trials()
    print("ok: 9 figures ->", OUT)
