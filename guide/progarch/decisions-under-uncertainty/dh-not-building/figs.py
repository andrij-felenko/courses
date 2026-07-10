# -*- coding: utf-8 -*-
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_T = "#eafaf0"   # зона «будувати»
RED_T   = "#fdecea"   # зона «найгірше будувати самим»
BLUE_T  = "#eef3fd"   # зона «купити / орендувати»


# ── Спільна модель вартості брокера (та сама, що в proj-broker-cost-model) ───
def _managed_month(n):
    """Рахунок за керований брокер, $/міс — лінійний із трафіком."""
    return n * 86400 / 1e6 * 1.00 + n * 43200 / 1e6 * 0.08

def _ops_fte(n):
    """Інженери на 24/7-хвіст; підлога 2 (щедро занижено проти SRE-шних ~8)."""
    return max(2.0, 2.0 + 2.0 * math.log10(n / 10000.0))

def _own_month(n):
    """Своє БЕЗ разової побудови, $/міс: люди + залізо + безпека."""
    return _ops_fte(n) * 12500.0 + 0.01 * n + 2500.0

def _poly(points, color, sw=2.4):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (d, color, sw))


# ── Мапа рішень: дві осі (ядро↔контекст, ціна помилки) з трьома «не будувати» ──
# Ідея: єдине, що лягає в «будувати» — це наше ядро з обмеженою ціною помилки
# (локальний рушій дому). Брокер і аналітика — контекст із обмеженою ціною → купити.
# Біометрія — контекст, але ціна помилки безмежна → тим паче не будувати наосліп.
def fig_decision_map():
    W, H = 760, 520
    ox, oy = 110.0, 70.0          # лівий верх поля
    pw, ph = 560.0, 386.0
    bottom = oy + ph              # 456
    right = ox + pw               # 670
    midx = ox + pw / 2            # 390
    midy = oy + ph / 2            # 263
    p = []

    # зони-квадранти (тільки заливка, без ліній)
    p.append(rect(midx, midy, right - midx, bottom - midy, fill=GREEN_T, stroke="none", sw=0, rx=0))
    p.append(rect(ox, oy, midx - ox, midy - oy, fill=RED_T, stroke="none", sw=0, rx=0))
    p.append(rect(ox, midy, midx - ox, bottom - midy, fill=BLUE_T, stroke="none", sw=0, rx=0))
    # рамка поля поверх заливок
    p.append(rect(ox, oy, pw, ph, fill="none", stroke=INK, sw=1.6, rx=10))

    def X(nx):
        return ox + pw * nx

    def Y(ny):
        return bottom - ph * ny

    def dot(nx, ny, col, label, dy):
        gx, gy = X(nx), Y(ny)
        out = circle(gx, gy, 7, fill=col, stroke=BG, sw=2)
        out += text(gx, gy + dy, label, size=12, color=INK)
        return out

    p.append(dot(0.26, 0.34, NEG,   "власний брокер",       -16))
    p.append(dot(0.40, 0.20, NEG,   "власна аналітика",      22))
    p.append(dot(0.24, 0.78, POS,   "власна біометрія",      22))
    p.append(dot(0.80, 0.34, FIELD, "локальний рушій — ядро", -16))

    # підписи зон
    p.append(text(200, 345, "КУПИТИ / ОРЕНДА", size=12, color=NEG, bold=True))
    p.append(text(250, 92, "будувати самим — найгірше", size=12, color=POS, bold=True))
    p.append(text(530, 435, "БУДУВАТИ САМІ", size=13, color=FIELD, bold=True))

    # осі-напрямки
    p.append(text(158, 480, "← контекст (товар)", size=11, color=MUTED))
    p.append(text(600, 480, "ядро (відмінність) →", size=11, color=MUTED))
    p.append('<text x="34" y="263" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 34 263)">ціна помилки зростає вгору</text>'
             % (FONT, MUTED))

    render(os.path.join(OUT, "decision-map.svg"), W, H, *p,
           title="Будувати чи купувати: мапа рішень DH")


# ── Критерії достатності: сходи-ворота, де «так» веде вниз до «будувати» ───────
# Ідея: чотири питання по черзі; будь-яке «ні» відводить убік (відкласти / купити).
# До «будувати самим» доходить лише те, що потрібне вже, є ядром, має обмежену
# ціну помилки і не покривається готовим товаром.
def fig_sufficiency_gates():
    W, H = 780, 560
    gx, gw = 150.0, 330.0
    px, pw = 548.0, 210.0
    spine = gx + gw / 2           # 315
    gate_right = gx + gw          # 480
    rows = [78.0, 170.0, 262.0, 354.0]
    gh = 58.0
    p = []

    gates = [
        "Це нам потрібно\nвже зараз?",
        "Це наша відмінність\n— ядро?",
        "Ціна помилки обмежена?\n(безпека, право, життя)",
        "Готовий товар НЕ\nдотягує до ядра?",
    ]
    exits = [
        ("Відкласти\n(YAGNI)", NEG, BLUE_T),
        ("Купити / орендувати", NEG, BLUE_T),
        ("Узяти перевірене,\nне наосліп", POS, RED_T),
        ("Купити — товар\nвирішує дешевше", NEG, BLUE_T),
    ]

    for i, ytop in enumerate(rows):
        cy = ytop + gh / 2
        p.append(fitbox(gx, ytop, gw, gh, gates[i], size=13, fill=FILL, stroke=INK))
        # бічна стрілка «ні» → відхід
        lbl, col, tint = exits[i]
        p.append(arrow(gate_right, cy, px - 2, cy, color=MUTED, sw=1.6))
        p.append(text((gate_right + px) / 2, cy - 8, "ні", size=11, color=POS))
        p.append(fitbox(px, cy - 24, pw, 48, lbl, size=12, fill=tint, stroke=col, color=col))
        # спинна стрілка «так» → униз
        if i < len(rows) - 1:
            p.append(arrow(spine, ytop + gh, spine, rows[i + 1], color=INK, sw=1.8))
            p.append(text(spine + 14, (ytop + gh + rows[i + 1]) / 2 + 4, "так", size=10, color=FIELD))

    # хвіст до «будувати»
    p.append(arrow(spine, rows[-1] + gh, spine, 452, color=INK, sw=1.8))
    p.append(fitbox(spine - 105, 452, 210, 64, "БУДУВАТИ САМІ\nі лише це",
                    size=14, fill=GREEN_T, stroke=FIELD, color=FIELD, bold=True))

    render(os.path.join(OUT, "sufficiency-gates.svg"), W, H, *p,
           title="Критерії достатності: коли будувати самим")


# ── Хроніка біометричної приватності: спинний таймлайн подій ────────────────
# Ідея: показати ескалацію одним поглядом — від банкрутства, що налякало
# законодавця, до мільярдних рахунків. Сірий = іскра, синій = закон/суд,
# червоний = виплати. Роки ліворуч спини, картки-події праворуч.
def fig_biometric_timeline():
    W, H = 780, 600
    spine_x = 210.0
    card_x, card_w, card_h = 236.0, 512.0, 64.0
    centers = [92.0, 184.0, 276.0, 368.0, 460.0, 552.0]
    events = [
        ("2007", MUTED, ["Pay By Touch банкрутує — мільйони",
                         "відбитків зависають без господаря"]),
        ("2008", NEG,   ["Іллінойс ухвалює BIPA: перший у США",
                         "закон, із правом особистого позову"]),
        ("2019", NEG,   ["Rosenbach v. Six Flags — порушення",
                         "саме по собі вже вважають шкодою"]),
        ("2021", POS,   ["Facebook: $650 млн за Tag Suggestions",
                         "(~1.6 млн користувачів з Іллінойсу)"]),
        ("2023", NEG,   ["Cothron v. White Castle — КОЖНЕ",
                         "сканування окреме порушення"]),
        ("2024", POS,   ["Техас: рекордні $1.4 млрд",
                         "за законом CUBI (ухвалений 2009)"]),
    ]
    p = [line(spine_x, centers[0] - 24, spine_x, centers[-1] + 24, color=MUTED, sw=2)]
    for cy, (yr, col, lines) in zip(centers, events):
        p.append(fitbox(card_x, cy - card_h / 2, card_w, card_h, "\n".join(lines),
                        size=13, fill=FILL, stroke=INK, sw=1.2))
        p.append(line(spine_x + 9, cy, card_x, cy, color=MUTED, sw=1.4))
        p.append(circle(spine_x, cy, 8, fill=col, stroke=BG, sw=2))
        p.append(text(spine_x - 24, cy + 5, yr, size=15, color=col, anchor="end", bold=True))
    render(os.path.join(OUT, "biometric-timeline.svg"), W, H, *p,
           title="Як біометрична приватність стала радіоактивною")


# ── Пароль ↺ vs біометрія ✕: зворотне проти незворотного ────────────────────
# Ідея: обидві таємниці можуть витекти, але пароль повертається в безпеку
# скиданням (цикл), а біометрію перевидати нічим — тупик. Дві колонки-потоки.
def fig_reset_vs_forever():
    W, H = 760, 400
    cx1, cx2 = 200.0, 560.0
    bw, bh = 250.0, 52.0
    hcy, hh = 62.0, 32.0
    rows = [126.0, 200.0, 274.0]
    fcy, fh = 344.0, 44.0

    def column(cx, header, hcol, boxes, footer, fcol, ftint):
        out = [fitbox(cx - bw / 2, hcy - hh / 2, bw, hh, header, size=15, bold=True,
                      fill=BG, stroke=hcol, color=hcol)]
        out.append(arrow(cx, hcy + hh / 2, cx, rows[0] - bh / 2, color=MUTED, sw=1.6))
        for i, (txt, tint) in enumerate(boxes):
            cy = rows[i]
            out.append(fitbox(cx - bw / 2, cy - bh / 2, bw, bh, txt, size=13,
                              fill=tint, stroke=INK, sw=1.2))
            nxt = rows[i + 1] - bh / 2 if i + 1 < len(rows) else fcy - fh / 2
            out.append(arrow(cx, cy + bh / 2, cx, nxt, color=MUTED, sw=1.6))
        out.append(fitbox(cx - bw / 2, fcy - fh / 2, bw, fh, footer, size=13, bold=True,
                          fill=ftint, stroke=fcol, color=fcol))
        return out

    p = []
    p += column(cx1, "ПАРОЛЬ", NEG,
                [("хтось викрав таємницю", FILL),
                 ("скинути за хвилину", FILL),
                 ("нова таємниця — знову захист", GREEN_T)],
                "↺  можна повторювати без кінця", FIELD, GREEN_T)
    p += column(cx2, "БІОМЕТРІЯ", POS,
                [("хтось викрав шаблон", FILL),
                 ("скинути… нема чим", FILL),
                 ("скомпрометовано назавжди", RED_T)],
                "✕  перевидати НЕ можна", POS, RED_T)
    render(os.path.join(OUT, "reset-vs-forever.svg"), W, H, *p,
           title="Пароль можна скинути, біометрію — ні")


# ── Перетин вартості: свій брокер проти купленого через масштаб ─────────────
# Ідея: куплене — пряма з майже-нуля (лінійна з трафіком), своє — висока людська
# підлога з пологим підйомом. Криві перетинаються раз, коло мільйона домів;
# теперішні 5 000 домів DH — далеко в зоні «купувати».
def fig_broker_crossover():
    W, H = 860, 520
    x0, x1 = 100.0, 800.0          # поле по X (пікселі)
    yt, yb = 74.0, 452.0           # поле по Y (верх — дороге, низ — дешеве)
    xdps = (x1 - x0) / 4.0         # 4 декади домів: 1e3 … 1e7
    ydps = (yb - yt) / 5.0         # 5 декад $/міс: 1e1 … 1e6

    def X(n): return x0 + (math.log10(n) - 3.0) * xdps
    def Y(v): return yb - (math.log10(v) - 1.0) * ydps

    p = [rect(x0, yt, x1 - x0, yb - yt, fill=BG, stroke=INK, sw=1.6, rx=8)]
    xlab = ["1 тис", "10 тис", "100 тис", "1 млн", "10 млн"]
    for i, d in enumerate(range(3, 8)):
        gx = X(10 ** d)
        p.append(line(gx, yt, gx, yb, color="#e6e8ec", sw=1.0))
        p.append(text(gx, yb + 20, xlab[i], size=11, color=MUTED))
    ylab = ["$10", "$100", "$1 тис", "$10 тис", "$100 тис", "$1 млн"]
    for i, d in enumerate(range(1, 7)):
        gy = Y(10 ** d)
        p.append(line(x0, gy, x1, gy, color="#e6e8ec", sw=1.0))
        p.append(text(x0 - 8, gy + 4, ylab[i], size=11, color=MUTED, anchor="end"))
    p.append(text((x0 + x1) / 2, yb + 42, "кількість домів (логарифм)", size=12, color=INK))
    p.append('<text x="26" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 26 %.1f)">вартість, $/місяць (логарифм)</text>'
             % ((yt + yb) / 2, FONT, INK, (yt + yb) / 2))

    ns = [10 ** (3 + 4 * k / 80.0) for k in range(81)]
    p.append(_poly([(X(n), Y(_managed_month(n))) for n in ns], NEG, 2.6))
    p.append(_poly([(X(n), Y(_own_month(n))) for n in ns], POS, 2.6))

    lo, hi = 1e3, 1e8                      # точка перетину — двійковим пошуком
    for _ in range(60):
        m = math.sqrt(lo * hi)
        lo, hi = (m, hi) if _own_month(m) > _managed_month(m) else (lo, m)
    xc = math.sqrt(lo * hi)
    cx, cy = X(xc), Y(_managed_month(xc))
    p.append(line(cx, cy, cx, yb, color=MUTED, sw=1.2, dash="4 4"))
    p.append(circle(cx, cy, 6, fill=FIELD, stroke=BG, sw=2))
    p.append(line(cx + 5, cy + 4, 648.0, 232.0, color=MUTED, sw=1.0))
    p.append(fitbox(642.0, 232.0, 150, 52,
                    "перетин ≈ %.0f тис домів\n(своє нарешті дешевше)" % (xc / 1000.0),
                    size=11, fill=GREEN_T, stroke=FIELD, color=INK))

    dn = 5000.0
    dx, dy = X(dn), Y(_managed_month(dn))
    p.append(circle(dx, dy, 5, fill=NEG, stroke=BG, sw=2))
    p.append(line(dx + 4, dy + 4, 300.0, 362.0, color=MUTED, sw=1.0))
    p.append(fitbox(264.0, 356.0, 156, 32, "DH сьогодні — 5 000 домів",
                    size=11, fill=FILL, stroke=NEG, color=INK))

    p.append(text((x0 + cx) / 2, yb - 14, "← тут дешевше КУПИТИ", size=11, color=NEG, bold=True))
    p.append(text((cx + x1) / 2, yb - 14, "будувати дешевше →", size=11, color=FIELD, bold=True))

    lgx, lgy = 118.0, 92.0
    p.append(line(lgx, lgy, lgx + 26, lgy, color=NEG, sw=3))
    p.append(text(lgx + 34, lgy + 4, "куплене — лінійно з трафіком", size=11, color=INK, anchor="start"))
    p.append(line(lgx, lgy + 22, lgx + 26, lgy + 22, color=POS, sw=3))
    p.append(text(lgx + 34, lgy + 26, "своє — великий фікс + пологий ріст", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "broker-crossover.svg"), W, H, *p,
           title="Місячна вартість брокера: свій проти купленого")


# ── На масштабі DH своє не окупається ніколи: накопичена вартість у часі ─────
# Ідея: на 5 000 домів куплене повзе по дну ($449/міс), а своє стартує з боргу
# $150 тис і росте вчетверо-вп'ятеро швидше — розрив лише ширшає, не сходиться.
def fig_broker_never_pays():
    W, H = 820, 480
    x0, x1 = 96.0, 780.0
    yt, yb = 70.0, 400.0
    MONTHS = 60
    ymax = 1_900_000.0
    n = 5000.0

    def X(m): return x0 + (x1 - x0) * m / MONTHS
    def Y(v): return yb - (yb - yt) * v / ymax

    buy = lambda m: _managed_month(n) * m                 # $449/міс
    own = lambda m: 150_000.0 + _own_month(n) * m         # $150к + $27.5к/міс

    p = [rect(x0, yt, x1 - x0, yb - yt, fill=BG, stroke=INK, sw=1.6, rx=8)]
    for v in [0, 500_000, 1_000_000, 1_500_000]:
        gy = Y(v)
        p.append(line(x0, gy, x1, gy, color="#e6e8ec", sw=1.0))
        p.append(text(x0 - 8, gy + 4, ("$%.1f млн" % (v / 1e6)) if v else "$0",
                      size=11, color=MUTED, anchor="end"))
    for yr in range(0, 6):
        gx = X(yr * 12)
        p.append(line(gx, yt, gx, yb, color="#eef0f3", sw=1.0))
        p.append(text(gx, yb + 20, ("%d р" % yr) if yr else "старт", size=11, color=MUTED))
    p.append(text((x0 + x1) / 2, yb + 42, "час експлуатації", size=12, color=INK))

    gap = ([(X(m), Y(own(m))) for m in range(0, MONTHS + 1, 2)] +
           [(X(m), Y(buy(m))) for m in range(MONTHS, -1, -2)])
    p.append('<polygon points="%s" fill="%s" stroke="none" opacity="0.55"/>'
             % (" ".join("%.1f,%.1f" % (x, y) for x, y in gap), RED_T))
    p.append(_poly([(X(m), Y(buy(m))) for m in range(0, MONTHS + 1)], NEG, 2.6))
    p.append(_poly([(X(m), Y(own(m))) for m in range(0, MONTHS + 1)], POS, 2.6))

    p.append(circle(X(0), Y(own(0)), 4, fill=POS, stroke=BG, sw=2))
    p.append(fitbox(150.0, 120.0, 258, 30, "свій: старт $150 тис + $27.5 тис/міс",
                    size=11, fill=RED_T, stroke=POS, color=INK))
    p.append(fitbox(470.0, 348.0, 226, 30, "куплений: лише $449/міс",
                    size=11, fill=BLUE_T, stroke=NEG, color=INK))
    p.append(fitbox(432.0, 100.0, 300, 52,
                    "на 5 000 домів свій не окупається\nніколи — розрив лише росте",
                    size=12, fill=FILL, stroke=INK, color=INK, bold=True))

    render(os.path.join(OUT, "broker-never-pays.svg"), W, H, *p,
           title="На теперішньому масштабі DH свій брокер не окупається")


if __name__ == "__main__":
    fig_decision_map()
    fig_sufficiency_gates()
    fig_biometric_timeline()
    fig_reset_vs_forever()
    fig_broker_crossover()
    fig_broker_never_pays()
    print("OK figs")
