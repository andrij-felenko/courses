# -*- coding: utf-8 -*-
"""Фігури до теми «Перерозподіл заряду між ємностями» (аналогова, кутом теорії кіл).
Фігури теми:
  share-levels.svg   — дві ємності як два «баки»: заряд перетікає, доки напруги зрівняються
  charge-vs-energy.svg— заряд зберігається, енергія падає (стовпчики до/після)
  r-independent.svg  — три різні R дають той самий ВТРАЧЕНИЙ джоуль (різна лише форма перехідного)
  redistribution-uses.svg— перерозподіл як рушій: вибірка ЦАП/АЦП, заряд-помпа, перекидні відра
Фігури вставки comp-switched-capacitor:
  sc-resistor.svg    — перемикуваний конденсатор ≈ резистор R = 1/(f·C): два такти, порція заряду
  sc-clocks.svg      — два неперекривні такти (Φ1/Φ2) з «мертвим часом» break-before-make
  sample-hold.svg    — вузол вибірки-зберігання: вибірка → утримання, граблі (інжекція, kT/C, витік)
Фігура вставки hist-two-capacitor-paradox:
  radiation-limit.svg— дві межі парадокса: кінцевий опір (тепло) vs нуль опору (LC-дзвін, випромінювання)
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _cap(x, y, w, h, fill_frac, col, top_lbl):
    """Намалювати «бак» (конденсатор як посудина) із рівнем заливки fill_frac∈[0,1]."""
    out = []
    out.append(rect(x, y, w, h, fill=BG, stroke=INK, sw=2))
    fh = h * fill_frac
    if fh > 1:
        fillc = {"#c0392b": "#fdecea", "#2457d6": "#eaf0fd", "#27ae60": "#eafaf0"}.get(col, "#eaf0fd")
        out.append(rect(x + 2, y + h - fh, w - 4, fh, fill=fillc, stroke="none", sw=0, rx=2))
        out.append(line(x + 2, y + h - fh, x + w - 2, y + h - fh, color=col, sw=2.4))
    out.append(text(x + w / 2, y - 8, top_lbl, size=13, bold=True))
    return out


def share_levels():
    """Дві ємності-баки: до замикання — повна й порожня; після — однаковий рівень."""
    W, H = 720, 400
    p = []
    boxh = 150
    boxw = 70

    # ── ліворуч: ДО замикання ──
    gx = 70
    p += _cap(gx, 110, boxw, boxh, 1.0, NEG, "C₁ = C")
    p += _cap(gx + 150, 110, boxw, boxh, 0.0, FIELD, "C₂ = C")
    p.append(text(gx + boxw / 2, 110 + boxh + 24, "V₁ = 10 В", size=12, color=NEG, bold=True))
    p.append(text(gx + 150 + boxw / 2, 110 + boxh + 24, "V₂ = 0 В", size=12, color=MUTED, bold=True))
    # розімкнений ключ між баками
    sk = gx + boxw + 18
    p.append(line(sk, 150, sk + 18, 150, color=INK, sw=2))
    p.append(line(sk + 34, 150, sk + 52, 150, color=INK, sw=2))
    p.append(line(sk + 18, 150, sk + 40, 136, color=INK, sw=2))   # розімкнений важіль
    p.append(text(sk + 26, 124, "розімкнено", size=10, color=MUTED))
    p.append(text(gx + 95, 92, "ДО", size=14, bold=True, color=INK))

    # ── стрілка переходу ──
    midx = gx + 150 + boxw + 40
    p.append(arrow(midx, 185, midx + 56, 185, color=INK, sw=2.4))
    p.append(text(midx + 28, 172, "замкнути", size=11, color=MUTED))

    # ── праворуч: ПІСЛЯ замикання ──
    rx = midx + 80
    p += _cap(rx, 110, boxw, boxh, 0.5, FIELD, "C₁")
    p += _cap(rx + 150, 110, boxw, boxh, 0.5, FIELD, "C₂")
    p.append(text(rx + boxw / 2, 110 + boxh + 24, "V = 5 В", size=12, color=FIELD, bold=True))
    p.append(text(rx + 150 + boxw / 2, 110 + boxh + 24, "V = 5 В", size=12, color=FIELD, bold=True))
    # замкнений ключ — пряма перемичка
    p.append(line(rx + boxw, 150, rx + 150, 150, color=FIELD, sw=2.6))
    p.append(text(rx + 110, 92, "ПІСЛЯ", size=14, bold=True, color=FIELD))
    # пунктир спільного рівня
    p.append(line(rx, 110 + boxh / 2, rx + 150 + boxw, 110 + boxh / 2, color=FIELD, sw=1, dash="4 3"))

    b, _, _ = textbox(W / 2, 372,
                      "Заряд перетікає з повної ємності в порожню, доки НАПРУГИ зрівняються — як вода між сполученими\n"
                      "баками. Сумарний заряд той самий (Q = C·10), але тепер ділиться на дві ємності: спільні 5 В.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'share-levels.svg'), W, H, *p,
           title="Перерозподіл заряду: рівні зрівнюються, як вода між баками")


def charge_vs_energy():
    """Стовпчики до/після: заряд незмінний, енергія падає вдвічі."""
    W, H = 700, 400
    p = []
    base_y = 300
    maxh = 200
    bw = 70

    # дві групи: ЗАРЯД (зберігається) і ЕНЕРГІЯ (втрачається)
    groups = [
        ("Сумарний заряд Q", [("до", 1.0, NEG), ("після", 1.0, FIELD)], "зберігся: 100%"),
        ("Енергія W", [("до", 1.0, NEG), ("після", 0.5, POS)], "лишилось: 50%"),
    ]
    gx0 = 130
    gap_in = 95
    gap_grp = 300
    for gi, (glbl, bars, note) in enumerate(groups):
        gx = gx0 + gi * gap_grp
        for bi, (lbl, frac, col) in enumerate(bars):
            cx = gx + bi * gap_in
            h = maxh * frac
            fillc = {"#c0392b": "#fdecea", "#2457d6": "#eaf0fd", "#27ae60": "#eafaf0"}[col]
            p.append(rect(cx - bw / 2, base_y - h, bw, h, fill=fillc, stroke=col, sw=2))
            p.append(text(cx, base_y + 18, lbl, size=12, bold=True, color=col))
            p.append(text(cx, base_y - h - 8, "%d%%" % (frac * 100), size=12, bold=True, color=col))
        # підпис групи й висновок
        p.append(text(gx + gap_in / 2, base_y + 44, glbl, size=13, bold=True))
        ncol = FIELD if "зберіг" in note else POS
        p.append(text(gx + gap_in / 2, base_y + 64, note, size=12, bold=True, color=ncol))
    p.append(line(70, base_y, W - 40, base_y, color=INK, sw=1.5))

    b, _, _ = textbox(W / 2, 374,
                      "Зберігається ЗАРЯД (його нема куди подіти), а не енергія. Половина джоулів зникає\n"
                      "у перехідному струмі — і це не залежить від того, який саме опір у ланцюзі.",
                      size=12, fill="#fdecea", stroke=POS)
    p.append(b)
    render(os.path.join(OUT, 'charge-vs-energy.svg'), W, H, *p,
           title="Заряд зберігається, енергія — ні: половина зникає")


def r_independent():
    """Три R: різні перехідні струми, та сама ВТРАЧЕНА енергія (площа під i²R однакова)."""
    W, H = 720, 420
    p = []
    # три осі i(t): малий R — високий короткий пік; великий R — низький довгий хвіст
    panels = [
        ("малий R", 1.0, 0.9, POS),
        ("середній R", 0.55, 1.8, NEG),
        ("великий R", 0.32, 3.2, FIELD),
    ]
    pw = (W - 60) / 3.0
    base_y = 250
    for i, (lbl, ipk, tau, col) in enumerate(panels):
        x0 = 30 + i * pw
        cx = x0 + pw / 2
        # рамка-панель
        p.append(rect(x0 + 10, 70, pw - 20, 200, fill=BG, stroke=MUTED, sw=1))
        # вісі
        ax0, ay0 = x0 + 28, base_y
        axw = pw - 58
        p.append(line(ax0, ay0, ax0 + axw, ay0, color=INK, sw=1.5))     # t
        p.append(line(ax0, ay0, ax0, ay0 - 160, color=INK, sw=1.5))     # i
        p.append(text(ax0 + axw, ay0 + 16, "час", size=10, color=MUTED, anchor="end"))
        p.append(text(ax0 - 6, ay0 - 160, "i", size=12, color=MUTED, anchor="end", italic=True))
        # крива i = ipk·e^(−t/tau)
        pts = []
        N = 60
        for k in range(N + 1):
            tt = k / N * 6.0
            ii = ipk * math.exp(-tt / tau)
            xx = ax0 + (axw) * (tt / 6.0)
            yy = ay0 - 150 * ii
            pts.append((xx, yy))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, col))
        # заливка під кривою — «енергія» (площа однакова між панелями)
        d_fill = d + " L%.1f %.1f L%.1f %.1f Z" % (pts[-1][0], ay0, ax0, ay0)
        fillc = {"#c0392b": "#fdecea", "#2457d6": "#eaf0fd", "#27ae60": "#eafaf0"}[col]
        p.append('<path d="%s" fill="%s" stroke="none" opacity="0.7"/>' % (d_fill, fillc))
        p.append(text(cx, 60, lbl, size=13, bold=True, color=col))
        p.append(text(cx, base_y + 34, "втрачено ½·W", size=12, bold=True, color=col))

    b, _, _ = textbox(W / 2, 392,
                      "Менший опір → вищий і коротший сплеск струму; більший опір → нижчий і довший хвіст.\n"
                      "Але ВТРАЧЕНА енергія (площа під i²·R) у всіх випадках одна — рівно половина початкової.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'r-independent.svg'), W, H, *p,
           title="Опір міняє форму перехідного струму, але не втрачену половину")


def redistribution_uses():
    """Перерозподіл заряду як спільний рушій кількох вузлів."""
    W, H = 720, 360
    p = []
    cards = [
        ("Вибірка АЦП/ЦАП", "вхід заряджає\nконденсатор вибірки;\nпотім порівнюють", NEG),
        ("Заряд-помпа", "конденсатор перекидають\nміж рівнями —\nпідіймає напругу", POS),
        ("Перекидні відра", "пакет заряду передають\nз ємності в ємність\nуздовж лінії", FIELD),
    ]
    cw = 210
    gap = 18
    x0 = (W - (3 * cw + 2 * gap)) / 2
    y0 = 80
    ch = 170
    for i, (title_c, body, col) in enumerate(cards):
        x = x0 + i * (cw + gap)
        p.append(rect(x, y0, cw, ch, fill="#f4f6f8", stroke=col, sw=2))
        p.append(text(x + cw / 2, y0 + 28, title_c, size=14, bold=True, color=col))
        p.append(line(x + 16, y0 + 40, x + cw - 16, y0 + 40, color=col, sw=1))
        p.append(mtext(x + cw / 2, y0 + 70, body, size=12, color=INK, lh=1.35))
    p.append(text(W / 2, y0 + ch + 34,
                  "У кожному — те саме: заряд перетікає між ємностями за законом збереження заряду.",
                  size=12, bold=True, color=MUTED))

    b, _, _ = textbox(W / 2, 332,
                      "Перерозподіл заряду — не лише «парадокс із підручника»: це робочий принцип вибірки сигналу,\n"
                      "помпування напруги й передавання заряду в аналогових і змішаних схемах.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'redistribution-uses.svg'), W, H, *p,
           title="Де працює перерозподіл заряду між ємностями")


def _switch(x, y, w, closed, lbl, col):
    """Маленький ключ: дві контактні точки + важіль (замкнено/розімкнено) з підписом такту."""
    out = []
    out.append(circle(x, y, 3.0, fill=INK, stroke=INK, sw=1))
    out.append(circle(x + w, y, 3.0, fill=INK, stroke=INK, sw=1))
    if closed:
        out.append(line(x, y, x + w, y, color=col, sw=2.6))
    else:
        out.append(line(x, y, x + w * 0.66, y - w * 0.34, color=col, sw=2.6))
    out.append(text(x + w / 2, y - 14, lbl, size=12, bold=True, color=col))
    return out


def sc_resistor():
    """Перемикуваний конденсатор ≈ резистор: за такт переноситься порція ΔQ = C·(V1−V2)."""
    W, H = 720, 380
    p = []

    # ── ліворуч: реальна схема — два ключі + конденсатор ──
    lx = 70
    yA = 150       # лінія вузла A (вхід)
    yB = 250       # лінія вузла B (вихід)
    # вузол A зліва, вузол B справа на одній горизонталі — зробимо горизонтальний тракт
    nodeAx = lx
    nodeBx = lx + 250
    ymid = 170
    p.append(text(nodeAx, ymid - 44, "V₁", size=14, bold=True, color=NEG))
    p.append(text(nodeBx + 8, ymid - 44, "V₂", size=14, bold=True, color=FIELD))
    # точки-вузли
    p.append(circle(nodeAx, ymid, 3.5, fill=INK, stroke=INK, sw=1))
    p.append(circle(nodeBx + 8, ymid, 3.5, fill=INK, stroke=INK, sw=1))
    # ключ Φ1 (ліворуч), пластина конденсатора, ключ Φ2 (праворуч)
    p += _switch(nodeAx + 10, ymid, 56, True, "Φ1", POS)
    capx = nodeAx + 10 + 56 + 18
    # конденсатор C (дві пластини вертикально)
    p.append(line(capx, ymid - 26, capx, ymid + 26, color=INK, sw=3))
    p.append(line(capx + 12, ymid - 26, capx + 12, ymid + 26, color=INK, sw=3))
    p.append(line(nodeAx + 10 + 56, ymid, capx, ymid, color=INK, sw=2))
    p.append(text(capx + 6, ymid + 44, "C", size=14, bold=True))
    p += _switch(capx + 12 + 6, ymid, 56, False, "Φ2", FIELD)
    p.append(line(capx + 12 + 6 + 56, ymid, nodeBx + 8, ymid, color=INK, sw=2))
    p.append(text(lx + 130, 92, "реальна схема", size=13, bold=True, color=MUTED))
    # підпис під схемою — що робить кожен такт
    p.append(mtext(lx + 130, ymid + 78,
                   "Φ1: C заряджається до V₁\n"
                   "Φ2: C віддає заряд у V₂\n"
                   "за такт переноситься ΔQ = C·(V₁−V₂)",
                   size=11, color=INK, lh=1.4))

    # ── праворуч: еквівалент — резистор ──
    rx = lx + 380
    rymid = ymid
    p.append(circle(rx, rymid, 3.5, fill=INK, stroke=INK, sw=1))
    p.append(text(rx, rymid - 44, "V₁", size=14, bold=True, color=NEG))
    # зигзаг-резистор
    zz = [(rx + 18, rymid)]
    for k in range(6):
        zz.append((rx + 18 + (k + 0.5) * 16, rymid + (-12 if k % 2 == 0 else 12)))
    zz.append((rx + 18 + 6 * 16, rymid))
    d = "M" + " L".join("%.1f %.1f" % q for q in zz)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, POS))
    p.append(line(rx, rymid, rx + 18, rymid, color=INK, sw=2))
    endx = rx + 18 + 6 * 16
    p.append(line(endx, rymid, endx + 18, rymid, color=INK, sw=2))
    p.append(circle(endx + 18, rymid, 3.5, fill=INK, stroke=INK, sw=1))
    p.append(text(endx + 18, rymid - 44, "V₂", size=14, bold=True, color=FIELD))
    p.append(text(rx + 60, 92, "еквівалент", size=13, bold=True, color=MUTED))
    p.append(text(rx + 60, rymid + 60, "R_екв = 1 / (f · C)", size=15, bold=True, color=POS))
    p.append(text(rx + 60, rymid + 82, "f — частота тактів", size=11, color=MUTED))

    # стрілка «≈»
    amx = lx + 330
    p.append(text(amx, ymid + 6, "≈", size=34, bold=True, color=INK))

    b, _, _ = textbox(W / 2, 352,
                      "Конденсатор, що тактами переносить порції заряду між двома вузлами, у СЕРЕДНЬОМУ\n"
                      "жене такий самий струм, як резистор R = 1/(f·C): швидше такти → менший опір.",
                      size=12, fill="#fdecea", stroke=POS)
    p.append(b)
    render(os.path.join(OUT, 'sc-resistor.svg'), W, H, *p,
           title="Перемикуваний конденсатор ≈ резистор R = 1/(f·C)")


def sc_clocks():
    """Два неперекривні такти Φ1/Φ2 з мертвим часом (break-before-make)."""
    W, H = 720, 360
    p = []
    ax0 = 90
    axw = W - 170
    # дві доріжки тактів
    rows = [("Φ1", 110, POS), ("Φ2", 200, FIELD)]
    period = axw / 4.0          # два повні періоди
    hi = 34                     # висота імпульсу
    dead = period * 0.10        # мертвий час
    for lbl, y0, col in rows:
        p.append(text(ax0 - 28, y0 + 6, lbl, size=14, bold=True, color=col))
        p.append(line(ax0, y0 + hi, ax0 + axw, y0 + hi, color=MUTED, sw=1))   # рівень 0
        # будуємо прямокутні імпульси; Φ2 зсунутий на півперіод
        shift = 0 if lbl == "Φ1" else period / 2
        x = ax0 + shift
        pts = [(ax0, y0 + hi)]
        # три імпульси
        for n in range(3):
            xs = x + n * period
            xe = xs + period / 2 - dead
            if xs < ax0:
                xs = ax0
            if xe > ax0 + axw:
                xe = ax0 + axw
            if xs >= ax0 + axw:
                break
            pts += [(xs, y0 + hi), (xs, y0), (xe, y0), (xe, y0 + hi)]
        pts.append((ax0 + axw, y0 + hi))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, col))

    # позначити «мертвий час» між фронтами
    gx = ax0 + period / 2 - dead
    p.append(line(gx, 96, gx, 250, color=INK, sw=1, dash="3 3"))
    p.append(line(ax0 + period / 2, 96, ax0 + period / 2, 250, color=INK, sw=1, dash="3 3"))
    p.append(text((gx + ax0 + period / 2) / 2, 86, "мертвий час", size=11, bold=True, color=INK))
    p.append(mtext((gx + ax0 + period / 2) / 2, 268, "обидва ключі\nрозімкнені", size=10, color=MUTED, lh=1.25))

    b, _, _ = textbox(W / 2, 330,
                      "Такти НЕ перекриваються: між ними — короткий «мертвий час», коли обидва ключі\n"
                      "розімкнені (break-before-make). Інакше вузли на мить замкнулись би й заряд потік би «навпростець».",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'sc-clocks.svg'), W, H, *p,
           title="Два неперекривні такти: Φ1, Φ2 і «мертвий час»")


def sample_hold():
    """Вузол вибірки-зберігання: вибірка → утримання, і три типові граблі."""
    W, H = 720, 420
    p = []

    # ── схема S/H угорі ──
    inx = 70
    y = 120
    p.append(text(inx, y - 24, "вхід", size=12, bold=True, color=NEG))
    p.append(circle(inx, y, 3.5, fill=INK, stroke=INK, sw=1))
    # буфер на вході (трикутник)
    bx = inx + 30
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (bx, y - 16, bx, y + 16, bx + 30, y, "#eef7f0", FIELD))
    p.append(line(inx, y, bx, y, color=INK, sw=2))
    # ключ вибірки
    sw_x = bx + 30 + 12
    p += _switch(sw_x, y, 56, True, "вибірка", POS)
    p.append(line(bx + 30, y, sw_x, y, color=INK, sw=2))
    # вузол утримання + конденсатор на землю
    nodex = sw_x + 56 + 14
    p.append(line(sw_x + 56, y, nodex, y, color=INK, sw=2))
    p.append(circle(nodex, y, 3.5, fill=INK, stroke=INK, sw=1))
    p.append(text(nodex, y - 24, "вузол утримання", size=11, bold=True, color=INK))
    # конденсатор Ch вниз на землю
    p.append(line(nodex, y, nodex, y + 34, color=INK, sw=2))
    p.append(line(nodex - 16, y + 34, nodex + 16, y + 34, color=INK, sw=3))
    p.append(line(nodex - 16, y + 42, nodex + 16, y + 42, color=INK, sw=3))
    p.append(text(nodex + 26, y + 40, "C_утр", size=13, bold=True))
    # земля
    gy = y + 42 + 12
    p.append(line(nodex, y + 42, nodex, gy, color=INK, sw=2))
    p.append(line(nodex - 12, gy, nodex + 12, gy, color=INK, sw=2))
    p.append(line(nodex - 7, gy + 5, nodex + 7, gy + 5, color=INK, sw=2))
    p.append(line(nodex - 3, gy + 10, nodex + 3, gy + 10, color=INK, sw=2))
    # вихідний буфер з високим імпедансом
    obx = nodex + 30
    p.append(line(nodex, y, obx, y, color=INK, sw=2))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (obx, y - 16, obx, y + 16, obx + 30, y, "#eef7f0", FIELD))
    p.append(line(obx + 30, y, obx + 60, y, color=INK, sw=2))
    p.append(circle(obx + 60, y, 3.5, fill=INK, stroke=INK, sw=1))
    p.append(text(obx + 60, y - 24, "до АЦП", size=12, bold=True, color=FIELD))

    # дві фази — короткий підпис
    p.append(text(W / 2, 198,
                  "Ключ замкнений → вузол стежить за входом (вибірка). Ключ розмикається → C_утр тримає «знімок» (утримання).",
                  size=11, color=MUTED))

    # ── три граблі картками ──
    cards = [
        ("Інжекція заряду", "у мить розмикання ключ\nскидає частину свого\nзаряду на C_утр →\nсходинка похибки", POS),
        ("kT/C-шум", "сам акт вибірки лишає\nна C_утр шумовий заряд\nσ² = kT/C — не залежить\nвід опору ключа", NEG),
        ("Витік під час утримання", "струми витоку ключа й\nбуфера повільно зміщують\nнапругу — «знімок»\nпливе з часом", FIELD),
    ]
    cw = 215
    gap = 16
    x0 = (W - (3 * cw + 2 * gap)) / 2
    yc = 232
    chh = 130
    for i, (t, body, col) in enumerate(cards):
        x = x0 + i * (cw + gap)
        p.append(rect(x, yc, cw, chh, fill="#f4f6f8", stroke=col, sw=2))
        p.append(text(x + cw / 2, yc + 24, t, size=13, bold=True, color=col))
        p.append(line(x + 14, yc + 34, x + cw - 14, yc + 34, color=col, sw=1))
        p.append(mtext(x + cw / 2, yc + 56, body, size=11, color=INK, lh=1.3))

    b, _, _ = textbox(W / 2, 392,
                      "Вузол вибірки-зберігання — це керований перерозподіл заряду в C_утр. Три граблі класу:\n"
                      "інжекція заряду ключа, kT/C-шум вибірки й витік під час утримання.",
                      size=12, fill="#fdecea", stroke=POS)
    p.append(b)
    render(os.path.join(OUT, 'sample-hold.svg'), W, H, *p,
           title="Вузол вибірки-зберігання та граблі класу")


def transient_curves():
    """Три R: крива потужності втрат P = i²R; пік ∝1/R, тривалість ∝R, ПЛОЩА однакова.
    Для math-rc-transient-loss: видно, як скорочення R лишає інтеграл незмінним."""
    W, H = 720, 430
    p = []
    # P(t) = (ΔV²/R)·e^(−2t/τ),  τ=R·C_екв.  Беремо ΔV²·C_екв ≡ 1 (нормування).
    # Тоді пік = ΔV²/R ∝ 1/R, а τ/2 = R·C_екв/2 ∝ R; площа = ½·C_екв·ΔV² = 0.5 (стала).
    # Параметр r — відносний опір; криві в СПІЛЬНИХ осях (не автомасштаб панелі),
    # щоб око бачило: вищий вузький пік ↔ нижчий ширший хвіст, площа та сама.
    panels = [
        ("малий R", 0.5, POS),
        ("середній R", 1.0, NEG),
        ("великий R", 2.0, FIELD),
    ]
    ax0, ay0 = 70, 300        # початок спільних осей
    axw, axh = W - 130, 210   # розмах осей
    Tmax = 6.0                # спільний горизонт часу (в одиницях базової τ)
    Pmax = 2.2                # спільна стеля потужності (щоб пік малого R уліз)
    # осі
    p.append(line(ax0, ay0, ax0 + axw, ay0, color=INK, sw=1.6))
    p.append(line(ax0, ay0, ax0, ay0 - axh, color=INK, sw=1.6))
    p.append(text(ax0 + axw, ay0 + 18, "час →", size=12, color=MUTED, anchor="end"))
    p.append(text(ax0 - 8, ay0 - axh + 4, "P = i²·R", size=13, color=MUTED, anchor="end", italic=True))
    for i, (lbl, r, col) in enumerate(panels):
        peak = 1.0 / r                 # ΔV²/R  (нормовано)
        tau_p = r / 2.0                # стала спаду потужності = τ/2 = R·C_екв/2
        pts = []
        N = 120
        for k in range(N + 1):
            tt = k / N * Tmax
            PP = peak * math.exp(-tt / tau_p)
            xx = ax0 + axw * (tt / Tmax)
            yy = ay0 - axh * (min(PP, Pmax) / Pmax)
            pts.append((xx, yy))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        # заливка під кривою — однакова ПЛОЩА (= ½·C_екв·ΔV²) у всіх трьох
        fillc = {"#c0392b": "#fdecea", "#2457d6": "#eaf0fd", "#27ae60": "#eafaf0"}[col]
        d_fill = d + " L%.1f %.1f L%.1f %.1f Z" % (pts[-1][0], ay0, ax0, ay0)
        p.append('<path d="%s" fill="%s" stroke="none" opacity="0.5"/>' % (d_fill, fillc))
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, col))
        # підпис кривої біля її піка
        pk_x = ax0 + 8 + i * 152
        pk_y = ay0 - axh * (min(peak, Pmax) / Pmax) - 10
        p.append(text(pk_x, max(pk_y, 62), lbl, size=12, bold=True, color=col, anchor="start"))
    # легенда-формула піка/хвоста
    p.append(text(ax0 + axw - 6, ay0 - axh + 30,
                  "пік = ΔV²/R   ·   спад ∝ R", size=12, color=MUTED, anchor="end"))
    # спільний підпис площі
    a, _, _ = textbox(ax0 + axw * 0.60, ay0 - 66,
                      "площа під усіма трьома\nоднакова:  ½·C_екв·ΔV²",
                      size=12, fill="#eef7f0", stroke=FIELD, bold=True, color=INK)
    p.append(a)

    b, _, _ = textbox(W / 2, 402,
                      "Менший опір → вищий і вужчий пік потужності; більший → нижчий і ширший хвіст.\n"
                      "Та інтеграл P = i²·R за весь час у всіх трьох однаковий: R скорочується, лишається ½·C_екв·ΔV².",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'transient-curves.svg'), W, H, *p,
           title="Опір кроїть форму перехідних втрат, але не їхній інтеграл")


def radiation_limit():
    """Кінцевий R (експонента → тепло) поряд із нулем R (LC-дзвін → випромінювання).
    Винесена частка ½ та сама, відмінний лише канал."""
    W, H = 762, 430
    p = []
    base_y = 250
    amp = 150
    pw = (W - 60) / 2.0
    panels = [
        ("Кінцевий опір R", "струм стікає за експонентою →\nполовина W йде в ТЕПЛО дроту", POS, False),
        ("Нуль опору (надпровідник)", "контур L·C дзвенить →\nта сама половина — у ВИПРОМІНЮВАННЯ", NEG, True),
    ]
    for i, (lbl, note, col, ring) in enumerate(panels):
        x0 = 30 + i * pw
        cx = x0 + pw / 2
        p.append(rect(x0 + 10, 72, pw - 20, 196, fill=BG, stroke=MUTED, sw=1))
        ax0, ay0 = x0 + 38, base_y
        axw = pw - 78
        p.append(line(ax0, ay0, ax0 + axw, ay0, color=INK, sw=1.5))       # вісь часу
        p.append(line(ax0, ay0, ax0, ay0 - amp, color=INK, sw=1.5))       # вісь струму
        p.append(text(ax0 + axw, ay0 + 16, "час", size=10, color=MUTED, anchor="end"))
        p.append(text(ax0 - 6, ay0 - amp + 6, "i", size=12, color=MUTED, anchor="end", italic=True))
        fillc = {"#c0392b": "#fdecea", "#2457d6": "#eaf0fd", "#27ae60": "#eafaf0"}[col]

        # крива струму
        pts = []
        N = 96
        for k in range(N + 1):
            tt = k / N * 6.0
            ii = math.exp(-tt / 3.2) * math.cos(tt * 2.4) if ring else math.exp(-tt / 1.3)
            xx = ax0 + axw * (tt / 6.0)
            yy = ay0 - (amp * 0.9) * ii
            pts.append((xx, yy))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)

        # заливка «винесеної енергії»: для дзвону беремо модуль струму
        if ring:
            pa = []
            for k in range(N + 1):
                tt = k / N * 6.0
                ii = abs(math.exp(-tt / 3.2) * math.cos(tt * 2.4))
                pa.append((ax0 + axw * (tt / 6.0), ay0 - (amp * 0.9) * ii))
            df = "M" + " L".join("%.1f %.1f" % q for q in pa)
            df += " L%.1f %.1f L%.1f %.1f Z" % (pa[-1][0], ay0, ax0, ay0)
        else:
            df = d + " L%.1f %.1f L%.1f %.1f Z" % (pts[-1][0], ay0, ax0, ay0)
        p.append('<path d="%s" fill="%s" stroke="none" opacity="0.6"/>' % (df, fillc))
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, col))

        # для нуль-R — дужки-радіохвилі, що відлітають
        if ring:
            ox, oy = cx + 6, 100
            for rr in (15, 27, 39):
                p.append('<path d="M %.1f %.1f A %d %d 0 0 1 %.1f %.1f" fill="none" '
                         'stroke="%s" stroke-width="1.6" opacity="0.85"/>'
                         % (ox + rr, oy, rr, rr, ox, oy - rr, NEG))
            p.append(text(cx + 66, 96, "радіохвилі", size=10, color=NEG, italic=True))

        p.append(text(cx, 62, lbl, size=13, bold=True, color=col))
        p.append(mtext(cx, base_y + 30, note, size=11, color=INK, lh=1.3))

    p.append(line(W / 2, 76, W / 2, 264, color=MUTED, sw=1, dash="3 4"))

    b, _, _ = textbox(W / 2, 400,
                      "Те саме явище у двох межах. Зникла половина (½·C·V²) виноситься різним КАНАЛОМ —\n"
                      "теплом на опорі або електромагнітним випромінюванням контуру — але ЧАСТКА завжди ½.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'radiation-limit.svg'), W, H, *p,
           title="Дві межі парадокса двох конденсаторів: тепло проти випромінювання, частка ½ незмінна")


if __name__ == '__main__':
    share_levels()
    charge_vs_energy()
    r_independent()
    redistribution_uses()
    sc_resistor()
    sc_clocks()
    sample_hold()
    transient_curves()
    radiation_limit()
    print("OK: 9 figures ->", OUT)
