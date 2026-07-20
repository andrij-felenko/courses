# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACC = "#caa24a"   # акцент «підпису» (контрольної суми) — теплий жовтий


# ── adler: дві біжучі суми A і B, тоді пакування B<<16 | A ─────────────────────
# Ідея: A починається з 1 і збирає байти; B на кожному кроці доливає поточне A;
# наприкінці A йде в молодші 16 біт, B — у старші, і виходить одне 32-бітне число.

def fig_adler():
    W, H = 760, 500
    p = []
    cols = [70, 250, 480]
    head = ["байт", "A += байт", "B += A"]
    for cx, h in zip(cols, head):
        p.append(text(cx, 92, h, size=13, color=INK, anchor="start", bold=True))
    p.append(line(70, 102, 700, 102, color=MUTED, sw=1.4))

    p.append(text(cols[0], 128, "старт", size=13, color=MUTED, anchor="start", italic=True))
    p.append(text(cols[1], 128, "A = 1", size=13.5, color=MUTED, anchor="start", italic=True))
    p.append(text(cols[2], 128, "B = 0", size=13.5, color=MUTED, anchor="start", italic=True))

    rows = [
        ("a  (97)", "1 + 97 = 98",    "0 + 98 = 98"),
        ("b  (98)", "98 + 98 = 196",  "98 + 196 = 294"),
        ("c  (99)", "196 + 99 = 295", "294 + 295 = 589"),
    ]
    y = 162
    for byte, a, b in rows:
        p.append(text(cols[0], y, byte, size=13.5, color=NEG, anchor="start", bold=True))
        p.append(text(cols[1], y, a, size=13.5, color=INK, anchor="start"))
        p.append(text(cols[2], y, b, size=13.5, color=ACC, anchor="start", bold=True))
        y += 34

    p.append(line(70, y - 4, 700, y - 4, color="#e4e4e4", sw=1.2))
    p.append(text(cols[0], y + 20, "разом:", size=13, color=INK, anchor="start", bold=True))
    p.append(text(cols[1], y + 20, "A = 295 = 0x0127", size=13.5, color=INK, anchor="start", bold=True))
    p.append(text(cols[2], y + 20, "B = 589 = 0x024D", size=13.5, color=ACC, anchor="start", bold=True))

    # ── пакування у 32-бітне слово ───────────────────────────────────────────
    py = 356
    p.append(line(50, py - 16, 710, py - 16, color="#e4e4e4", sw=1.4))
    bw, bh = 200, 46
    xB, xA = 150, 150 + bw + 10
    p.append(rect(xB, py, bw, bh, fill="#eef2fb", stroke=NEG, sw=1.8, rx=6))
    p.append(text(xB + bw / 2, py + bh / 2 + 5, "B = 0x024D", size=15, color=INK, bold=True))
    p.append(text(xB + bw / 2, py - 8, "старші 16 біт", size=11, color=MUTED))
    p.append(rect(xA, py, bw, bh, fill="#fff8e8", stroke=ACC, sw=2.2, rx=6))
    p.append(text(xA + bw / 2, py + bh / 2 + 5, "A = 0x0127", size=15, color=ACC, bold=True))
    p.append(text(xA + bw / 2, py - 8, "молодші 16 біт", size=11, color=MUTED))

    p.append(text(W / 2, py + bh + 34,
                  "Adler-32 = B·65536 + A = 0x024D0127",
                  size=15, color=INK, bold=True))
    p.append(text(W / 2, py + bh + 56,
                  "(перевірка: рядок «Wikipedia» дає 0x11E60398)",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "adler.svg"), W, H, *p,
           title="Adler-32: дві суми над потоком, тоді пакування в 32 біти")


# ── coverage: коротке повідомлення не «намотує» суму — і не заповнює діапазон ──
# Ідея: A може дійти щонайбільше до 1+255·n; поки це менше за 65521, верхні
# значення недосяжні, тож молодші 16 біт підпису «голодують» — звідси збіги.

def fig_coverage():
    W, H = 780, 465
    p = []
    p.append(text(W / 2, 58, "Яку частку діапазону A (0…65520) взагалі може дійти сума",
                  size=13, color=MUTED, italic=True))

    x0 = 210
    full = 470            # ширина, що відповідає 100 %
    bars = [
        ("n = 16 Б",   0.062, "6 %",     POS),
        ("n = 32 Б",   0.125, "12 %",    POS),
        ("n = 64 Б",   0.249, "25 %",    ACC),
        ("n = 128 Б",  0.498, "50 %",    ACC),
        ("n = 256 Б",  0.996, "≈ 100 %", FIELD),
    ]
    y = 96
    bh = 40
    gap = 20
    for label, frac, pct, col in bars:
        p.append(text(x0 - 16, y + bh / 2 + 5, label, size=13, color=INK, anchor="end", bold=True))
        p.append(rect(x0, y, full, bh, fill="#fafafa", stroke="#e4e4e4", sw=1.2, rx=5))
        w = max(6, frac * full)
        p.append(rect(x0, y, w, bh, fill=col, stroke=col, sw=1.2, rx=5))
        tx = x0 + w + 10 if frac < 0.85 else x0 + w - 10
        anc = "start" if frac < 0.85 else "end"
        tcol = INK if frac < 0.85 else "#ffffff"
        p.append(text(tx, y + bh / 2 + 5, pct, size=13, color=tcol, anchor=anc, bold=True))
        y += bh + gap

    # позначка «повний діапазон»
    p.append(line(x0 + full, 88, x0 + full, y - gap + bh + 6, color=INK, sw=1.4, dash="4 4"))
    p.append(text(x0 + full, 82, "повний діапазон (2¹⁶)", size=11, color=INK, bold=True))

    p.append(line(50, y + 8, 730, y + 8, color="#e4e4e4", sw=1.4))
    p.append(text(W / 2, y + 30,
                  "Поки повідомлення коротше за ~256 байтів, A не «намотує» модуль 65521:",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, y + 50,
                  "верхні значення недосяжні → молодші 16 біт підпису бідні → збіги ймовірніші, ніж 1/2³²",
                  size=12, color=POS, bold=True))

    render(os.path.join(OUT, "coverage.svg"), W, H, *p,
           title="Слабке місце Adler-32: короткі повідомлення")


# ── vs-fletcher: що саме Adler міняє у Флетчері ───────────────────────────────
# Ідея: два дрібні, але вирішальні кроки — просте 65521 замість складеного 65535
# і старт A=1 замість 0; праворуч — наслідок кожного.

def fig_vs_fletcher():
    W, H = 760, 380
    p = []
    cF, cA = 300, 560
    p.append(fitbox(cF - 95, 74, 190, 40, "Флетчер-32", size=15, fill="#f3f4f6", stroke=MUTED, sw=1.6, bold=True))
    p.append(fitbox(cA - 95, 74, 190, 40, "Adler-32", size=15, fill="#fff8e8", stroke=ACC, sw=2.0, bold=True, color=ACC))

    rows = [
        ("модуль (дільник)", "65535 = 3·5·17·257", "65521 — просте"),
        ("старт A", "0", "1"),
    ]
    y = 150
    for label, f, a in rows:
        p.append(text(60, y, label, size=13, color=INK, anchor="start", bold=True))
        p.append(text(cF, y, f, size=13, color=MUTED, anchor="middle"))
        p.append(text(cA, y, a, size=13.5, color=INK, anchor="middle", bold=True))
        p.append(line(50, y + 16, 710, y + 16, color="#eee", sw=1))
        y += 46

    b1, w1, h1 = textbox(cA, 262, ["просте 65521 → значення сум", "лягають рівномірніше, менше збігів"],
                         size=12, bold=True, fill="#eef7f0", stroke=FIELD, sw=1.6, color=FIELD)
    p.append(b1)
    b2, w2, h2 = textbox(cA, 322, ["старт 1 → сума бачить провідні нулі;", "порожнє «» ≠ «\\0»"],
                         size=12, bold=True, fill="#eef7f0", stroke=FIELD, sw=1.6, color=FIELD)
    p.append(b2)

    p.append(text(150, 262, "два дрібні,", size=13, color=INK, bold=True))
    p.append(text(150, 284, "але вирішальні", size=13, color=INK, bold=True))
    p.append(text(150, 322, "кроки", size=13, color=INK, bold=True))

    render(os.path.join(OUT, "vs-fletcher.svg"), W, H, *p,
           title="Що Adler-32 міняє у контрольній сумі Флетчера")


# ── hist-timeline: алгоритм поширювався швидше, ніж про нього збирали докази ───
# Ідея: два струмені подій. Ліворуч — поширення (Флетчер → zlib → RFC → SCTP),
# праворуч — вимір (Стоун, потім Максіно й Купман). Впадає в око, що SCTP узяв
# Adler-32 у пакети ВЖЕ ПІСЛЯ перших вимірів Стоуна.

def fig_hist_timeline():
    W, H = 940, 700
    p = []
    axis = 470
    lx, rx, bw, bh = 40, 540, 360, 52

    p.append(text(220, 76, "п о ш и р е н н я", size=13, color=NEG, bold=True))
    p.append(text(720, 76, "в и м і р", size=13, color=POS, bold=True))
    p.append(line(axis, 96, axis, 676, color=MUTED, sw=2))

    rows = [
        ("L", ["1982 · Джон Флетчер, Лівермор",
               "дві суми замість однієї"]),
        ("L", ["груд. 1994 · Unisys бере плату за GIF",
               "світові терміново потрібен вільний формат"]),
        ("L", ["~квіт. 1995 · zlib 0.4",
               "у списку змін: «added adler32 and crc32»"]),
        ("L", ["трав. 1996 · RFC 1950 (Дойч і Ґайї)",
               "«надзвичайно низька ймовірність похибки»"]),
        ("R", ["1998 · Стоун, Ґрінвальд, Г'юз, Партрідж",
               "збоїв у мережі більше, ніж обіцяє теорія"]),
        ("R", ["серп. 2000 · Стоун і Партрідж, SIGCOMM",
               "CRC і контрольна сума не сходяться"]),
        ("L", ["жовт. 2000 · RFC 2960",
               "SCTP кладе Adler-32 у короткі пакети"]),
        ("R", ["верес. 2002 · RFC 3309",
               "SCTP: Adler-32 → CRC-32C"]),
        ("R", ["2006 · Максіно й Купман",
               "Флетчер-32 кращий — і на 25 % дешевший"]),
    ]

    y = 118
    for side, lines in rows:
        col = NEG if side == "L" else POS
        fill = "#eef2fb" if side == "L" else "#fdecea"
        if side == "L":
            p.append(fitbox(lx, y - bh / 2, bw, bh, lines, size=12.5,
                            fill=fill, stroke=col, sw=1.6, color=INK))
            p.append(line(lx + bw, y, axis, y, color=col, sw=1.4))
        else:
            p.append(fitbox(rx, y - bh / 2, bw, bh, lines, size=12.5,
                            fill=fill, stroke=col, sw=1.6, color=INK))
            p.append(line(axis, y, rx, y, color=col, sw=1.4))
        p.append(circle(axis, y, 5.5, fill=col, stroke=col, sw=1.5))
        y += 66

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Adler-32: поширення випередило докази")


# ── hist-vs-whom: проти кого насправді змагався Adler-32 ──────────────────────
# Ідея: Адлер покращував Флетчер-16 (mod 255) — і сам це визнав у листуванні
# 2006 року. Світ прочитав RFC 1950 так, ніби Adler-32 побив Флетчер-32
# (mod 65535). Вимір показав: ні.

def fig_hist_vs_whom():
    W, H = 900, 470
    p = []

    p.append(fitbox(320, 72, 260, 64, ["Adler-32", "mod 65521 (просте)"],
                    size=15, fill="#fff8e8", stroke=ACC, sw=2.2, color=ACC, bold=True))

    p.append(arrow(370, 140, 205, 218, color=MUTED, sw=1.8))
    p.append(arrow(530, 140, 695, 218, color=MUTED, sw=1.8))

    p.append(mtext(120, 172, ["«я покращував", "ось це»"],
                   size=12.5, color=INK, bold=True))
    p.append(mtext(790, 172, ["«він побив", "ось це»?"],
                   size=12.5, color=INK, bold=True))

    p.append(fitbox(75, 222, 260, 60, ["Флетчер-16", "mod 255"],
                    size=14, fill="#f3f4f6", stroke=MUTED, sw=1.6, color=INK, bold=True))
    p.append(fitbox(565, 222, 260, 60, ["Флетчер-32", "mod 65535"],
                    size=14, fill="#f3f4f6", stroke=MUTED, sw=1.6, color=INK, bold=True))

    p.append(mtext(205, 310, ["✓ але це 32 біти проти 16 —", "перемога наперед відома"],
                   size=12, color=FIELD, bold=True))
    p.append(mtext(695, 310, ["✗ вимір 2006: у майже всіх", "випадках кращий Флетчер-32"],
                   size=12, color=POS, bold=True))

    p.append(line(50, 366, 850, 366, color="#e4e4e4", sw=1.4))
    p.append(text(W / 2, 396, "Просте 65521 перемішує біти краще — але лишає менше «кошиків» під підписи.",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, 420, "У більшості випадків утрата кошиків з'їдає виграш від перемішування.",
                  size=12.5, color=INK))
    p.append(text(W / 2, 446, "Сам Марк Адлер 2006 року визнав: Флетчера-32 він тоді просто не знав.",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "hist-vs-whom.svg"), W, H, *p,
           title="Проти кого насправді змагався Adler-32")


# ── nmax: скільки можна відкладати модуль, поки B не переповнить uint32 ───────
# Ідея: у найгіршому разі (усі байти 0xFF, обидві суми щойно зведені й дорівнюють
# 65520) B росте квадратично. Стеля — 2³²−1. Точка перетину і є NMAX = 5552.
# A росте лише лінійно й до стелі не дістає ніколи — вузьке місце тільки B.

def fig_nmax():
    W, H = 800, 480
    p = []
    BASE = 65521
    CEIL = 2 ** 32 - 1

    def worst_b(n):
        return (BASE - 1) + n * (BASE - 1) + 255 * n * (n + 1) // 2

    def worst_a(n):
        return (BASE - 1) + 255 * n

    x0, x1 = 130, 700
    ytop, ybot = 84, 344
    NX, VY = 6000, 5.2e9

    def X(n):
        return x0 + (n / NX) * (x1 - x0)

    def Y(v):
        return ybot - (v / VY) * (ybot - ytop)

    p.append(text(W / 2, 50, "Найгірший випадок: усі байти 0xFF, обидві суми стартують із 65520",
                  size=12.5, color=MUTED, italic=True))

    # смуга переповнення над стелею
    yc = Y(CEIL)
    p.append(rect(x0, ytop, x1 - x0, yc - ytop, fill="#fdf0ee", stroke="none", sw=0, rx=0))
    p.append(mtext(x0 + 12, ytop + 20, ["переповнення uint32", "2³² − 1 = 4 294 967 295"],
                   size=11.5, color=POS, anchor="start", lh=1.25, bold=True))
    p.append(line(x0, yc, x1, yc, color=POS, sw=1.6, dash="6 4"))

    # осі
    p.append(line(x0, ybot, x1, ybot, color=INK, sw=1.4))
    p.append(line(x0, ytop, x0, ybot, color=INK, sw=1.4))
    for v in range(0, 6):
        yy = Y(v * 1e9)
        lab = "0" if v == 0 else "%d·10⁹" % v
        p.append(text(x0 - 10, yy + 4, lab, size=10.5, color=MUTED, anchor="end"))
        if v:
            p.append(line(x0 - 4, yy, x0, yy, color=MUTED, sw=1.2))
    for n in range(0, NX + 1, 1000):
        p.append(line(X(n), ybot, X(n), ybot + 4, color=MUTED, sw=1.2))
        p.append(text(X(n), ybot + 18, str(n), size=11, color=MUTED))

    # криві
    ptsB = " ".join("%.1f,%.1f" % (X(n), Y(worst_b(n))) for n in range(0, NX + 1, 60))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (ptsB, ACC))
    ptsA = " ".join("%.1f,%.1f" % (X(n), Y(worst_a(n))) for n in range(0, NX + 1, 60))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (ptsA, NEG))

    # легенда — ліворуч під стелею, там крива ще далеко праворуч
    ly = yc + 26
    for col, lab in ((ACC, "найгірший B — росте як 255·n²/2"),
                     (NEG, "найгірший A — лише 255·n, стелі не бачить")):
        p.append(line(x0 + 16, ly - 4, x0 + 46, ly - 4, color=col, sw=2.6))
        p.append(text(x0 + 54, ly, lab, size=11.5, color=INK, anchor="start"))
        ly += 22

    # межа n = 5552
    xm = X(5552)
    p.append(line(xm, yc, xm, ybot, color=ACC, sw=1.6, dash="5 4"))
    p.append(circle(xm, Y(worst_b(5552)), 5, fill=ACC, stroke=ACC, sw=1.5))
    p.append(text(xm, ybot + 40, "n = 5552", size=12, color=ACC, bold=True))
    p.append(text(x0 + (x1 - x0) / 2 - 130, ybot + 40, "n — байтів від останнього зведення",
                  size=11.5, color=MUTED, italic=True))

    p.append(line(50, 400, 750, 400, color="#e4e4e4", sw=1.4))
    p.append(text(W / 2, 424, "255·n·(n+1)/2 + (n+1)·65520 ≤ 2³² − 1",
                  size=14, color=INK, bold=True))
    p.append(text(225, 450, "n = 5552 → 4 294 690 200 ✓ запас 277 095",
                  size=11.5, color=FIELD, bold=True))
    p.append(text(585, 450, "n = 5553 → 4 296 171 735 ✗ перебір 1 204 440",
                  size=11.5, color=POS, bold=True))

    render(os.path.join(OUT, "nmax.svg"), W, H, *p,
           title="Звідки береться NMAX = 5552")


# ── simd: чому наївний цикл не векторизується, а блок — векторизується ────────
# Ідея: у наївному циклі кожне A чекає на попереднє (ланцюг залежностей).
# Закрита формула на блок розриває ланцюг: усередині блоку байти незалежні,
# і дві горизонтальні згортки лягають на дві SIMD-інструкції.

def fig_simd():
    W, H = 820, 550
    p = []

    # ── верхня панель: сувора черга ──────────────────────────────────────────
    p.append(text(60, 78, "наївно — сувора черга", size=13.5, color=POS, anchor="start", bold=True))

    xs = [190, 300, 410, 520, 630]
    for i, cx in enumerate(xs):
        if i:
            p.append(rect(cx - 16, 88, 32, 24, fill="#eef2fb", stroke=NEG, sw=1.5, rx=4))
            p.append(text(cx, 105, "d%d" % i, size=11, color=NEG, bold=True))
            p.append(arrow(cx, 112, cx, 136, color=NEG, sw=1.4))
        p.append(rect(cx - 26, 136, 52, 32, fill=FILL, stroke=INK, sw=1.6, rx=5))
        p.append(text(cx, 157, "A%d" % i, size=12.5, color=INK, bold=True))
        p.append(rect(cx - 26, 192, 52, 32, fill="#fff8e8", stroke=ACC, sw=1.8, rx=5))
        p.append(text(cx, 213, "B%d" % i, size=12.5, color=ACC, bold=True))
        if i:
            p.append(arrow(cx, 168, cx, 192, color=MUTED, sw=1.3))
    for a, b in zip(xs, xs[1:]):
        p.append(arrow(a + 27, 152, b - 27, 152, color=POS, sw=2.4))
        p.append(arrow(a + 27, 208, b - 27, 208, color=MUTED, sw=1.4))

    p.append(text(W / 2, 250, "кожне A чекає на попереднє A — ланцюг завдовжки з усе повідомлення",
                  size=12.5, color=POS, bold=True))
    p.append(line(50, 272, 770, 272, color="#e4e4e4", sw=1.4))

    # ── нижня панель: блок ───────────────────────────────────────────────────
    p.append(text(60, 302, "блоком по 16 — ланцюг розірвано", size=13.5, color=FIELD,
                  anchor="start", bold=True))
    p.append(text(575, 302, "усередині блоку байти не чекають один одного",
                  size=12, color=FIELD, italic=True))

    p.append(text(120, 341, "байти:", size=11, color=INK, anchor="end", bold=True))
    p.append(text(120, 371, "ваги:", size=11, color=ACC, anchor="end", bold=True))
    for j in range(16):
        cx = 150 + j * 36
        p.append(rect(cx - 16, 324, 32, 24, fill="#eef2fb", stroke=NEG, sw=1.4, rx=4))
        p.append(text(cx, 341, "d%d" % (j + 1), size=10.5, color=NEG, bold=True))
        p.append(text(cx, 371, str(16 - j), size=10.5, color=ACC, bold=True))

    p.append(line(134, 384, 706, 384, color=MUTED, sw=1.4))
    p.append(arrow(300, 384, 300, 400, color=MUTED, sw=1.4))
    p.append(arrow(560, 384, 560, 400, color=MUTED, sw=1.4))

    b1, w1, h1 = textbox(300, 426, ["Σ dⱼ", "один _mm_sad_epu8"], size=11.5,
                         fill="#eef7f0", stroke=FIELD, sw=1.8, color=FIELD, bold=True)
    p.append(b1)
    b2, w2, h2 = textbox(560, 426, ["Σ (16−j)·dⱼ", "один _mm_maddubs_epi16"], size=11.5,
                         fill="#eef7f0", stroke=FIELD, sw=1.8, color=FIELD, bold=True)
    p.append(b2)

    p.append(arrow(300, 426 + h1 / 2, 300, 472, color=MUTED, sw=1.4))
    p.append(arrow(560, 426 + h2 / 2, 560, 472, color=MUTED, sw=1.4))

    b3, w3, h3 = textbox(W / 2, 498, ["A += Σ dⱼ", "B += 16·A + Σ (16−j)·dⱼ"], size=12.5,
                         fill=FILL, stroke=INK, sw=1.8, color=INK, bold=True)
    p.append(b3)

    render(os.path.join(OUT, "simd.svg"), W, H, *p,
           title="Ланцюг залежностей проти закритої формули на блок")


if __name__ == "__main__":
    fig_adler()
    fig_coverage()
    fig_vs_fletcher()
    fig_hist_timeline()
    fig_hist_vs_whom()
    fig_nmax()
    fig_simd()
    print("OK: figures written to", OUT)
