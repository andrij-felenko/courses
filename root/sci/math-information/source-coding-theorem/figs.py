# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Базова стаття (source-coding-theorem.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── squeeze: затиск H ≤ L < H+1 ───────────────────────────────────────────────
# Ідея ГОЛОВНА: середня довжина оптимального коду L затиснена між дном H (знизу,
# не можна нижче — обернена частина) і H+1 (згори, досяжно — пряма частина).
# Вісь біт/символ; смужка [H, H+1) — «коридор», де живе будь-який оптимальний код.

def fig_squeeze():
    W, H = 700, 280
    ax0, ay = 70, 188
    axw = 580
    p = []
    p.append(arrow(ax0, ay, ax0 + axw, ay, color=INK, sw=1.6))
    p.append(text(ax0 + axw, ay + 22, "біт на символ", size=11, color=INK, italic=True, anchor="end"))

    # масштаб: H у точці Hx, ширина одного «біта» = unit
    Hx = ax0 + 150
    unit = 200
    Hx1 = Hx + unit  # H+1

    # коридор [H, H+1)
    p.append(rect(Hx, 96, unit, ay - 96, fill="#eafaf0", stroke="none", sw=0))
    p.append(text((Hx + Hx1) / 2, 86, "коридор оптимального коду", size=11, color=FIELD, bold=True))

    # стіна H — дно
    p.append(line(Hx, 70, Hx, ay + 6, color=NEG, sw=2.6))
    p.append(text(Hx, 60, "H — дно (нижче не можна)", size=11, color=NEG, bold=True))
    # межа H+1 — досяжна стеля
    p.append(line(Hx1, 96, Hx1, ay + 6, color=POS, sw=2.4, dash="6 4"))
    p.append(text(Hx1, 86, "H + 1", size=11, color=POS, bold=True, anchor="start"))

    # заборонена зона ліворуч від H
    p.append(rect(ax0, 120, Hx - ax0, ay - 120, fill="#fdecea", stroke="none", sw=0))
    p.append(text((ax0 + Hx) / 2, 150, "неможливо", size=10, color=POS, bold=True))
    p.append(text((ax0 + Hx) / 2, 167, "(втрата)", size=9, color=POS))

    # точка L десь у коридорі
    Lx = Hx + 0.55 * unit
    p.append(circle(Lx, ay, 5, fill=FIELD, stroke=FIELD, sw=1))
    p.append(line(Lx, ay, Lx, 118, color=FIELD, sw=1.2, dash="3 3"))
    p.append(text(Lx, 112, "L — середня довжина", size=11, color=FIELD, bold=True))

    p.append(text(W / 2, ay + 56,
                  "будь-який оптимальний код: H ≤ L < H + 1   —   а блокуванням L/n тиснемо до самого H",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "squeeze.svg"), W, H, *p,
           title="Затиск середньої довжини: H ≤ L < H + 1")


# ── typical-set: типовий набір ділить простір послідовностей ───────────────────
# Ідея: серед усіх Nⁿ послідовностей майже вся ймовірність зосереджена у крихітній
# жмені «типових» (~2^{nH} штук, кожна ~рівноймовірна). Решта — практично не
# трапляється. Кодуємо коротко лише типові — звідси H біт на символ.

def fig_typical_set():
    W, H = 720, 320
    p = []
    cx, cy = 230, 175
    Rout, Rin = 120, 52
    # зовнішнє коло — усі послідовності
    p.append(circle(cx, cy, Rout, fill="#f4f6f8", stroke=MUTED, sw=1.6))
    p.append(text(cx, cy - Rout - 12, "усі Nⁿ послідовностей", size=12, color=MUTED, bold=True))
    # розкидані «нетипові» точки
    import random
    random.seed(7)
    for _ in range(70):
        a = random.uniform(0, 2 * math.pi)
        r = Rin + 14 + (Rout - Rin - 24) * math.sqrt(random.uniform(0, 1))
        x = cx + r * math.cos(a); y = cy + r * math.sin(a)
        p.append(circle(x, y, 1.6, fill=MUTED, stroke="none", sw=0))
    # внутрішнє коло — типовий набір
    p.append(circle(cx, cy, Rin, fill="#eafaf0", stroke=FIELD, sw=2.2))
    p.append(text(cx, cy - 6, "типовий", size=12, color=FIELD, bold=True))
    p.append(text(cx, cy + 12, "набір", size=12, color=FIELD, bold=True))

    # виноски
    b1, w1, h1 = textbox(cx, cy + Rin + 34, "≈ 2^{nH} штук · сумарна ймовірність ≈ 1",
                         size=11, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.6)
    p.append(b1)
    p.append(text(cx + Rout - 6, cy + Rout - 18, "майже не трапляються", size=10, color=MUTED,
                  italic=True, anchor="end"))

    # права панель — наслідок
    px = 470
    p.append(line(px - 20, 70, px - 20, 270, color="#e2e6ea", sw=1.4))
    p.append(text(px + 90, 92, "Наслідок для коду", size=12, color=INK, bold=True))
    rows = [
        ("типових ≈ 2^{nH}", FIELD),
        ("щоб занумерувати їх,", INK),
        ("треба ≈ nH біт", POS),
        ("→ H біт на символ", POS),
    ]
    for i, (t, c) in enumerate(rows):
        p.append(text(px, 128 + i * 30, t, size=12, color=c, anchor="start",
                      bold=(i >= 2)))
    p.append(text(px, 128 + 4 * 30 + 8, "нетиповим даємо довгий код —", size=10, color=MUTED, anchor="start", italic=True))
    p.append(text(px, 128 + 4 * 30 + 24, "вони майже не зринають", size=10, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "typical-set.svg"), W, H, *p,
           title="Типовий набір: уся ймовірність — у жмені послідовностей")


# ── two-parts: пряма і обернена частини теореми ───────────────────────────────
# Ідея: теорема = дві стіни до того самого дна H. Пряма (досяжність): існує код
# зі середньою довжиною як завгодно близькою до H зверху. Обернена: жоден код не
# опускається нижче H. Між ними дно H затиснуте з двох боків — це і є теорема.

def fig_two_parts():
    W, H = 720, 300
    p = []
    # центральна вісь-«дно»
    fx = W / 2
    p.append(line(fx, 70, fx, 250, color=FIELD, sw=2.6))
    b0, _, _ = textbox(fx, 60, "дно H", size=12, bold=True, color=FIELD,
                       fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(b0)

    # ліва стіна — пряма частина (зверху досягаємо)
    p.append(arrow(fx - 250, 150, fx - 14, 150, color=POS, sw=2.2))
    bl, wl, hl = textbox(fx - 250, 150, "ПРЯМА\n(досяжність)", size=12, bold=True, color=POS,
                         fill="#fdecea", stroke=POS, sw=1.8)
    p.append(bl)
    p.append(text(fx - 130, 134, "кодуємо типові", size=10, color=MUTED, italic=True))
    p.append(text(fx - 130, 174, "L → H зверху", size=10, color=POS, italic=True))

    # права стіна — обернена частина (знизу не можна)
    p.append(arrow(fx + 250, 150, fx + 14, 150, color=NEG, sw=2.2))
    br, wr, hr = textbox(fx + 250, 150, "ОБЕРНЕНА\n(межа знизу)", size=12, bold=True, color=NEG,
                         fill="#eef4ff", stroke=NEG, sw=1.8)
    p.append(br)
    p.append(text(fx + 130, 134, "місць бракує", size=10, color=MUTED, italic=True))
    p.append(text(fx + 130, 174, "L ≥ H завжди", size=10, color=NEG, italic=True))

    p.append(text(W / 2, 250 + 30,
                  "дві частини притискають L до того самого дна H з двох боків — у цьому й уся теорема",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "two-parts.svg"), W, H, *p,
           title="Дві частини теореми: пряма й обернена")


# ── blocking: блокування наближає L/n до H ────────────────────────────────────
# Ідея: посимвольно «зайвий» біт коштує до +1 на символ (H ≤ L < H+1). Кодуй блоки
# по n символів — той самий зайвий біт розмазується на n, тож L/n < H + 1/n → H.
# Стовпчики: середня довжина на символ для n=1,2,4,8 спадає до пунктиру H.

def fig_blocking():
    W, H = 700, 330
    p = []
    base_y = 250
    Hval = 1.75  # дно для прикладу
    ceil0 = Hval + 1.0
    scale = 90  # px на біт
    y_of = lambda v: base_y - (v - 1.0) * scale  # вісь починаємо трохи нижче H

    p.append(line(70, base_y, 660, base_y, color=INK, sw=1.6))
    # пунктир дна H
    yH = y_of(Hval)
    p.append(line(70, yH, 660, yH, color=FIELD, sw=2, dash="6 4"))
    p.append(text(664, yH + 4, "H", size=12, color=FIELD, bold=True, anchor="start"))

    blocks = [(1, ceil0 - 0.10), (2, Hval + 0.5), (4, Hval + 0.25), (8, Hval + 0.125)]
    bw, gap = 80, 56
    x0 = 120
    for i, (n, Ln) in enumerate(blocks):
        x = x0 + i * (bw + gap)
        yv = y_of(Ln)
        col = POS if i == 0 else (FIELD if i == len(blocks) - 1 else "#d98a00")
        fill = "#fdecea" if i == 0 else ("#eafaf0" if i == len(blocks) - 1 else "#fdf6e3")
        p.append(rect(x, yv, bw, base_y - yv, fill=fill, stroke=col, sw=2))
        p.append(text(x + bw / 2, yv - 10, "%.2f" % Ln, size=11, color=col, bold=True))
        p.append(text(x + bw / 2, base_y + 20, "n = %d" % n, size=12, color=INK, bold=True))
        p.append(text(x + bw / 2, base_y + 38, "біт/символ", size=9, color=MUTED))

    p.append(text(W / 2, base_y + 70,
                  "зайвий «до +1 біта» розмазується на n символів: L/n < H + 1/n → H",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "blocking.svg"), W, H, *p,
           title="Блокування: середня довжина на символ тисне до дна H")


# ── pair: пара теорем Шеннона ─────────────────────────────────────────────────
# Ідея: дві опори теорії інформації 1948 р. Кодування ДЖЕРЕЛА — стиск до H знизу
# (скільки мінімум). Кодування КАНАЛУ — передача до C зверху (скільки максимум).
# Дзеркальні межі: одна каже «не стиснеш тісніше», друга — «не передаси швидше».

def fig_pair():
    W, H = 720, 270
    p = []
    # ліва картка — джерело
    lx = 185
    p.append(rect(lx - 150, 70, 300, 150, fill="#eef4ff", stroke=NEG, sw=2, rx=10))
    p.append(text(lx, 98, "Кодування ДЖЕРЕЛА", size=13, color=NEG, bold=True))
    p.append(text(lx, 124, "стиск без втрат", size=11, color=INK))
    b1, _, _ = textbox(lx, 158, "L ≥ H", size=15, bold=True, color=NEG,
                       fill="#ffffff", stroke=NEG, sw=1.8)
    p.append(b1)
    p.append(text(lx, 200, "дно: тісніше за H не можна", size=10, color=MUTED, italic=True))

    # права картка — канал
    rx = 535
    p.append(rect(rx - 150, 70, 300, 150, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    p.append(text(rx, 98, "Кодування КАНАЛУ", size=13, color=FIELD, bold=True))
    p.append(text(rx, 124, "надійна передача", size=11, color=INK))
    b2, _, _ = textbox(rx, 158, "R ≤ C", size=15, bold=True, color=FIELD,
                       fill="#ffffff", stroke=FIELD, sw=1.8)
    p.append(b2)
    p.append(text(rx, 200, "стеля: швидше за C не можна", size=10, color=MUTED, italic=True))

    # місток
    p.append(text(W / 2, 145, "⇄", size=26, color=MUTED, bold=True))
    p.append(text(W / 2, 244, "дві опори теорії інформації Шеннона (1948): дно стиску й стеля передачі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "pair.svg"), W, H, *p,
           title="Пара теорем: джерело (дно H) і канал (стеля C)")


# ══════════════════════════════════════════════════════════════════════════════
# Детальна версія (source-coding-theorem-d.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── aep: концентрація −(1/n)·log p → H (закон великих чисел для інформації) ─────
# Ідея: випадкова величина −(1/n)·log p(X₁…Xₙ) — це середнє n незалежних
# «несподіванок». За ЗВЧ воно збігається до свого середнього H. Що більше n, то
# вужчий дзвін навколо H: майже всі послідовності мають ймовірність ≈ 2^{−nH}.

def fig_aep():
    W, H = 720, 320
    ox, oy = 80, 250
    aw, ah = 560, 190
    p = []
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - ah - 12, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 22, "−(1/n)·log₂ p(X₁…Xₙ)  — біт/символ", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 12, oy - ah - 2, "густина", size=10, color=INK, bold=True, anchor="end"))

    Hx = ox + 0.5 * aw  # положення H на осі
    # три дзвони дедалі вужчі (n росте)
    def bell(sigma, col, sw, dash=None, scale=1.0):
        pts = []
        nN = 200
        for i in range(nN + 1):
            xx = ox + aw * i / nN
            z = (xx - Hx) / (sigma * aw)
            yy = oy - ah * scale * math.exp(-0.5 * z * z)
            pts.append("%.1f,%.1f" % (xx, yy))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (" ".join(pts), col, sw, d))

    p.append(bell(0.20, MUTED, 1.8, dash="5 4", scale=0.42))
    p.append(bell(0.11, "#d98a00", 2.0, scale=0.66))
    p.append(bell(0.05, FIELD, 2.8, scale=1.0))

    # вісь H
    p.append(line(Hx, oy + 6, Hx, oy - ah - 6, color=NEG, sw=1.6, dash="4 4"))
    p.append(text(Hx, oy + 20, "H", size=12, color=NEG, bold=True))

    # підписи кривих
    p.append(text(Hx + 0.24 * aw, oy - 0.40 * ah, "мале n — широкий розкид", size=10, color=MUTED, anchor="start"))
    p.append(text(Hx + 0.07 * aw, oy - 0.96 * ah, "велике n — гострий пік на H", size=10, color=FIELD, anchor="start", bold=True))

    p.append(text(W / 2, oy + 52,
                  "−(1/n)·log p — середнє n несподіванок; за законом великих чисел воно стягується до H",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "aep.svg"), W, H, *p,
           title="AEP: ентропія на символ концентрується навколо H")


# ── counting: лічба типових ≈ 2^{nH} проти всіх Nⁿ ────────────────────────────
# Ідея: пряма частина спирається на лічбу. Усіх послідовностей Nⁿ = 2^{n·log N}.
# Типових лише ≈ 2^{nH}, а H ≤ log N. Тож типових експоненційно менше — і саме на
# них вистачає коротких кодів довжиною ≈ nH біт. Дві «полиці» довжин у бітах.

def fig_counting():
    W, H = 720, 300
    p = []
    ax0, ay = 90, 230
    p.append(arrow(ax0, ay, ax0, 70, color=INK, sw=1.6))
    p.append(text(ax0 - 6, 64, "довжина коду, біт", size=11, color=INK, anchor="middle", bold=True))
    p.append(line(ax0, ay, 640, ay, color=INK, sw=1.4))

    # дві стовпчасті «полиці»: всі (n·logN) і типові (nH)
    logN_h = 150   # px для n·log N
    nH_h = 96      # px для n·H (H < log N)
    bw = 150
    x1 = 210
    x2 = 460
    p.append(rect(x1 - bw / 2, ay - logN_h, bw, logN_h, fill="#f4f6f8", stroke=MUTED, sw=2))
    p.append(text(x1, ay - logN_h - 12, "усі: n·log₂N біт", size=12, color=MUTED, bold=True))
    p.append(text(x1, ay + 22, "2^{n·log N} штук", size=11, color=MUTED))

    p.append(rect(x2 - bw / 2, ay - nH_h, bw, nH_h, fill="#eafaf0", stroke=FIELD, sw=2.4))
    p.append(text(x2, ay - nH_h - 12, "типові: ≈ n·H біт", size=12, color=FIELD, bold=True))
    p.append(text(x2, ay + 22, "≈ 2^{nH} штук", size=11, color=FIELD, bold=True))

    # дужка економії
    p.append(line(x1 + bw / 2 + 10, ay - logN_h, x1 + bw / 2 + 10, ay - nH_h, color=POS, sw=1.6))
    p.append(line(x1 + bw / 2 + 6, ay - logN_h, x1 + bw / 2 + 14, ay - logN_h, color=POS, sw=1.6))
    p.append(line(x1 + bw / 2 + 6, ay - nH_h, x1 + bw / 2 + 14, ay - nH_h, color=POS, sw=1.6))
    p.append(text(x1 + bw / 2 + 20, ay - (logN_h + nH_h) / 2, "економія", size=10, color=POS,
                  anchor="start", bold=True))
    p.append(text(x1 + bw / 2 + 20, ay - (logN_h + nH_h) / 2 + 15, "n(log N − H)", size=9, color=POS,
                  anchor="start"))

    p.append(text(W / 2, 270,
                  "типових експоненційно менше за всі — нумеруємо лише їх, і код коштує ≈ H біт на символ",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "counting.svg"), W, H, *p,
           title="Лічба: типових ≈ 2^{nH}, а всіх — 2^{n·log N}")


# ── kraft-link: −log p як ідеальна довжина, і чому L ≥ H (обернена) ────────────
# Ідея: Крафт каже, що довжини lᵢ префіксного коду мусять задовольняти Σ2^{−lᵢ}≤1.
# Мінімум Σ pᵢlᵢ за цієї умови дає lᵢ = −log₂pᵢ (ідеальна довжина) і L = H. Цілість
# lᵢ лише піднімає L, ніколи не опускає → L ≥ H. Стовпчики: lᵢ поряд із −log₂pᵢ.

def fig_kraft_link():
    W, H = 720, 330
    p = []
    syms = [("A", 0.50), ("B", 0.25), ("C", 0.125), ("D", 0.125)]
    base_y = 232
    scale = 46
    bw, gap = 54, 40
    x0 = 150
    p.append(line(x0 - 30, base_y, 600, base_y, color=INK, sw=1.5))
    p.append(text(x0 - 34, 80, "довжина, біт", size=11, color=INK, anchor="start", bold=True))

    for i, (s, pr) in enumerate(syms):
        ideal = -math.log(pr, 2)
        x = x0 + i * (bw * 2 + gap)
        # ідеальна довжина −log p
        hi = ideal * scale
        p.append(rect(x, base_y - hi, bw, hi, fill="#eef4ff", stroke=NEG, sw=1.8))
        p.append(text(x + bw / 2, base_y - hi - 10, "%.0f" % ideal if ideal == int(ideal) else "%.2f" % ideal,
                      size=10, color=NEG, bold=True))
        # фактична ціла довжина lᵢ (тут збігається — степені ½)
        li = math.ceil(ideal)
        hl = li * scale
        p.append(rect(x + bw + 6, base_y - hl, bw, hl, fill="#eafaf0", stroke=FIELD, sw=1.8))
        p.append(text(x + bw + 6 + bw / 2, base_y - hl - 10, "%d" % li, size=10, color=FIELD, bold=True))
        p.append(text(x + bw + 3, base_y + 20, "%s, p=%g" % (s, pr), size=10, color=INK))

    # легенда
    p.append(rect(150, 270, 16, 12, fill="#eef4ff", stroke=NEG, sw=1.4))
    p.append(text(172, 280, "ідеальна −log₂p", size=10, color=NEG, anchor="start"))
    p.append(rect(330, 270, 16, 12, fill="#eafaf0", stroke=FIELD, sw=1.4))
    p.append(text(352, 280, "ціла lᵢ = ⌈−log₂p⌉", size=10, color=FIELD, anchor="start"))

    p.append(text(W / 2, 308,
                  "мінімум Σpᵢlᵢ за Крафтом дає lᵢ = −log₂pᵢ і L = H; округлення вгору лише піднімає L → L ≥ H",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "kraft-link.svg"), W, H, *p,
           title="Ідеальна довжина −log₂p, нерівність Крафта й чому L ≥ H")


if __name__ == "__main__":
    # базова
    fig_squeeze()
    fig_typical_set()
    fig_two_parts()
    fig_blocking()
    fig_pair()
    # детальна
    fig_aep()
    fig_counting()
    fig_kraft_link()
    print("OK: figures written to", OUT)
