# -*- coding: utf-8 -*-
"""Фігури до теми «JFET» та вставки math-shockley-law.
Фігури теми:
  structure.svg  — будова: n-канал між S і D, збоку p-затвор; перехід затвор–канал
  squeeze.svg    — звуження каналу: при від'ємнішому Vgs збіднені області з боків ростуть
  transfer.svg   — передавальна крива Шоклі: IDSS при Vgs=0 → 0 при Vgs=Vp (квадрат)
  output.svg     — вихідна ВАХ ID(Vds): омічна ділянка → насичення, верхня крива на IDSS
Фігури вставки math-shockley-law:
  cross-section.svg — поперечний переріз: два збіднені шари d з боків, просвіт 2(a−d)
  wedge.svg         — канал-клин: V(x) росте до стоку, збіднені шари товщають; координата x
  saturate.svg      — повний ID(Vds) виходить на поличку точно в точці защемлення
  gm-slope.svg      — крутість як нахил передавальної кривої: max при Vgs=0, →0 при Vp
Запуск швидкий, без зациклень.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DEPL = "#d7dbe0"   # збіднена область (сіра, не проводить)
CHAN = "#cdeedd"   # провідний канал (зелений, як «поле»)
PCOL = "#f6e0e6"   # p-затвор (легкий рожевий)


# ── 1. Будова JFET ───────────────────────────────────────────────────────────
def fig_structure():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 28, "Будова JFET: канал проводить сам, затвор — перехід збоку",
                  size=16, bold=True))
    bx, by, bw, bh = 130, 120, 460, 110
    # n-канал (сам брусок)
    f.append(rect(bx, by, bw, bh, fill=CHAN, stroke=FIELD, sw=1.6))
    f.append(text(W / 2, by + bh / 2 + 5, "n-канал (проводить)", size=14, bold=True, color=FIELD))
    # витік / стік
    f.append(rect(bx - 44, by + 18, 44, bh - 36, fill="#dfe7f5", stroke=NEG, sw=1.5))
    f.append(text(bx - 22, by + bh / 2 + 5, "S", size=15, bold=True, color=NEG))
    f.append(text(bx - 22, by + bh + 22, "витік", size=11, color=MUTED))
    f.append(rect(bx + bw, by + 18, 44, bh - 36, fill="#dfe7f5", stroke=NEG, sw=1.5))
    f.append(text(bx + bw + 22, by + bh / 2 + 5, "D", size=15, bold=True, color=NEG))
    f.append(text(bx + bw + 22, by + bh + 22, "стік", size=11, color=MUTED))
    # p-затвори зверху і знизу (дві симетричні області)
    gx, gw = bx + 150, 160
    f.append(rect(gx, by - 40, gw, 38, fill=PCOL, stroke=POS, sw=1.5))
    f.append(text(gx + gw / 2, by - 16, "p-затвор", size=12, bold=True, color=POS))
    f.append(rect(gx, by + bh + 2, gw, 38, fill=PCOL, stroke=POS, sw=1.5))
    f.append(text(gx + gw / 2, by + bh + 26, "p-затвор", size=12, bold=True, color=POS))
    # межі-переходи (пунктир уздовж стику p і n)
    f.append(line(gx, by, gx + gw, by, color=POS, sw=1.4, dash="4 3"))
    f.append(line(gx, by + bh, gx + gw, by + bh, color=POS, sw=1.4, dash="4 3"))
    f.append(text(gx + gw + 86, by - 4, "перехід", size=11, color=POS, anchor="start"))
    f.append(text(gx + gw + 86, by + 11, "затвор–канал", size=11, color=POS, anchor="start"))
    f.append(line(gx + gw, by, gx + gw + 80, by - 2, color=POS, sw=1.0))
    # висновок-рамка
    b, w, h = textbox(W / 2, 322,
                      "Vgs = 0: канал суцільний → JFET проводить (нормально відкритий)",
                      size=12, fill="#f7fbf8", stroke=FIELD, pad=9)
    f.append(b)
    render(os.path.join(IMG, "structure.svg"), W, H, *f)


# ── 2. Звуження каналу зворотним зміщенням затвора ───────────────────────────
def fig_squeeze():
    W, H = 840, 380
    f = []
    f.append(text(W / 2, 26, "Затвор душить канал: збіднені області з'їдають переріз",
                  size=16, bold=True))

    def panel(x0, title, vgs, depl_frac, accent, pinched=False):
        out = []
        cx = x0 + 140
        out.append(text(cx, 62, title, size=14, bold=True, color=accent))
        out.append(text(cx, 80, vgs, size=12, color=MUTED))
        bx, by, bw, bh = x0 + 36, 110, 208, 130
        # повний канал-брусок (зелений)
        out.append(rect(bx, by, bw, bh, fill=CHAN, stroke=FIELD, sw=1.4))
        # p-затвори зверху/знизу
        out.append(rect(bx + 70, by - 22, bw - 140, 20, fill=PCOL, stroke=POS, sw=1.2))
        out.append(rect(bx + 70, by + bh + 2, bw - 140, 20, fill=PCOL, stroke=POS, sw=1.2))
        # збіднені області з боків (сірі), ростуть усередину з depl_frac
        d = (bh / 2 - 8) * depl_frac
        out.append(rect(bx + 70, by, bw - 140, d, fill=DEPL, stroke=MUTED, sw=1.0))
        out.append(rect(bx + 70, by + bh - d, bw - 140, d, fill=DEPL, stroke=MUTED, sw=1.0))
        # S / D
        out.append(rect(bx - 26, by + 14, 26, bh - 28, fill="#dfe7f5", stroke=NEG, sw=1.3))
        out.append(text(bx - 13, by + bh / 2 + 4, "S", size=12, bold=True, color=NEG))
        out.append(rect(bx + bw, by + 14, 26, bh - 28, fill="#dfe7f5", stroke=NEG, sw=1.3))
        out.append(text(bx + bw + 13, by + bh / 2 + 4, "D", size=12, bold=True, color=NEG))
        # просвіт каналу посередині
        if pinched:
            out.append(line(bx + bw / 2, by + bh / 2 - 6, bx + bw / 2, by + bh / 2 + 6,
                            color=POS, sw=2.2))
            out.append(text(cx, by + bh + 44, "канал перекрито: струму нема",
                            size=11, bold=True, color=POS))
        else:
            out.append(text(bx + bw / 2, by + bh / 2 + 4, "просвіт", size=10, color=FIELD))
            out.append(arrow(bx - 4, by + bh / 2, bx + bw + 4, by + bh / 2,
                             color=accent, sw=2.0))
            out.append(text(cx, by + bh + 44, "струм тече", size=11, bold=True, color=accent))
        return out

    f += panel(10, "Vgs = 0", "канал найширший", 0.18, FIELD)
    f += panel(290, "Vgs помірно −", "канал звузився", 0.55, "#b8860b")
    f += panel(570, "Vgs = Vp", "збіднені шари зімкнулись", 1.0, POS, pinched=True)
    render(os.path.join(IMG, "squeeze.svg"), W, H, *f)


# ── 3. Передавальна крива Шоклі ID(Vgs) ──────────────────────────────────────
def fig_transfer():
    W, H = 720, 420
    ox, oy = 130, 330
    axw, axh = 520, 250
    f = []
    f.append(text(W / 2, 28, "Передавальна крива JFET: від IDSS до нуля (квадрат)",
                  size=16, bold=True))
    # осі
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))
    f.append(text(ox + axw, oy + 24, "Vgs", size=13, italic=True))
    f.append(text(ox - 6, oy - axh + 4, "ID", size=13, anchor="end", italic=True))
    # вісь Vgs = 0 праворуч (бо робоча ділянка — від'ємна)
    zx = ox + axw - 40
    f.append(line(zx, oy, zx, oy - axh + 10, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(zx, oy + 20, "0", size=12, color=MUTED))
    # Vp ліворуч
    vpx = ox + 40
    f.append(line(vpx, oy, vpx, oy + 8, color=POS, sw=1.4))
    f.append(text(vpx, oy + 24, "Vp", size=12, bold=True, color=POS))
    f.append(text(vpx, oy + 40, "(відсічка)", size=10, color=POS))
    # парабола: ID = IDSS*(1 - Vgs/Vp)^2; при Vgs=0 -> IDSS (у zx), при Vgs=Vp -> 0 (у vpx)
    idss_y = oy - (axh - 24)
    pts = []
    n = 80
    for i in range(0, n + 1):
        t = i / n                      # t: 0 у Vp -> 1 у нулі
        x = vpx + t * (zx - vpx)
        d = t * t                      # (1 - Vgs/Vp)^2 росте як t^2 від Vp до 0
        y = oy - d * (oy - idss_y)
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), FIELD))
    # IDSS-рівень
    f.append(circle(zx, idss_y, 4.5, fill="#fff", stroke=FIELD, sw=2))
    f.append(line(ox, idss_y, zx, idss_y, color=FIELD, sw=1.0, dash="3 4"))
    f.append(text(ox - 6, idss_y + 4, "IDSS", size=12, bold=True, color=FIELD, anchor="end"))
    # точка відсічки
    f.append(circle(vpx, oy, 4.5, fill="#fff", stroke=POS, sw=2))
    # підпис робочої зони
    f.append(text(ox + axw / 2, oy - axh + 30, "робоча ділянка: Vgs від Vp до 0 (від'ємна)",
                  size=12, bold=True, color=INK))
    f.append(text(ox + axw / 2 + 40, idss_y + 40, "ID = IDSS·(1 − Vgs/Vp)²",
                  size=13, bold=True, color=FIELD))
    render(os.path.join(IMG, "transfer.svg"), W, H, *f)


# ── 4. Вихідна характеристика ID(Vds): омічний → насичення ───────────────────
def fig_output():
    W, H = 720, 430
    ox, oy = 100, 340
    axw, axh = 560, 270
    f = []
    f.append(text(W / 2, 26, "Вихідна ВАХ: омічна ділянка (резистор) → насичення (струм)",
                  size=15, bold=True))
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))
    f.append(text(ox + axw, oy + 24, "Vds", size=13, italic=True))
    f.append(text(ox - 56, oy - axh + 6, "ID", size=13, anchor="start", italic=True))

    # криві для кількох Vgs (0 — найвища, далі від'ємніші — нижчі)
    curves = [(0.40, "#16307a", 1.00, "Vgs = 0  → IDSS"),
              (0.34, NEG, 0.64, "Vgs < 0"),
              (0.26, "#9bb7ef", 0.34, "ще −")]
    for vp_frac, col, plat, lab in curves:
        vp = ox + vp_frac * axw       # точка переходу в насичення (Vds = Vgs - Vp)
        ipl = oy - plat * (axh - 36)  # рівень плато
        pts = []
        n = 60
        for i in range(0, n + 1):
            t = i / n
            x = ox + t * (vp - ox)
            d = (2 * t - t * t)        # омічна: росте, нахил→0 на защемленні
            y = oy - d * (oy - ipl)
            pts.append("%.1f,%.1f" % (x, y))
        for i in range(1, 56):
            x = vp + i * ((ox + axw - 14 - vp) / 56.0)
            y = ipl - i * 0.08
            pts.append("%.1f,%.1f" % (x, y))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), col))
        f.append(circle(vp, ipl, 3.5, fill="#fff", stroke=col, sw=1.8))
    # позначити IDSS на верхній кривій
    top_ipl = oy - 1.00 * (axh - 36)
    f.append(line(ox, top_ipl, ox + 0.40 * axw, top_ipl, color="#16307a", sw=1.0, dash="3 4"))
    f.append(text(ox - 6, top_ipl + 4, "IDSS", size=11, bold=True, color="#16307a", anchor="end"))
    f.append(text(ox + 0.40 * axw + 6, top_ipl - 8, "Vgs = 0", size=11, bold=True, color="#16307a", anchor="start"))
    f.append(text(ox + axw - 14, oy - 0.34 * (axh - 36) + 18, "Vgs < 0", size=11, color=NEG, anchor="end"))

    # межа защемлення (пунктир крізь точки переходу)
    f.append(line(ox + 0.26 * axw, oy - 0.34 * (axh - 36),
                  ox + 0.40 * axw + 6, oy - 1.00 * (axh - 36) - 6,
                  color=POS, sw=1.6, dash="6 4"))
    f.append(text(ox + 175, oy - 60, "межа: Vds = Vgs − Vp", size=12, bold=True, color=POS))

    # підписи зон
    f.append(text(ox + 60, oy - 16, "ОМІЧНИЙ", size=12, bold=True, color=MUTED))
    f.append(text(ox + 60, oy - 3, "(резистор)", size=10, color=MUTED))
    f.append(text(ox + 410, oy - 16, "НАСИЧЕННЯ", size=12, bold=True, color=MUTED))
    f.append(text(ox + 410, oy - 3, "(джерело струму)", size=10, color=MUTED))
    render(os.path.join(IMG, "output.svg"), W, H, *f)


# ── 5. Історія: теорія випередила залізо (для hist-вставки) ──────────────────
def fig_history_timeline():
    W, H = 880, 470
    f = []
    f.append(text(W / 2, 28, "Польове керування: ідея, теорія й залізо розійшлися в часі",
                  size=16, bold=True))

    ax = 70                       # ліва межа осі часу
    axw = W - 140                 # довжина осі
    y_idea = 110                  # доріжка «ідея / патент»
    y_real = 360                  # доріжка «робоче залізо»
    # роки → x
    Y0, Y1 = 1925, 1955
    def X(year):
        return ax + (year - Y0) / (Y1 - Y0) * axw

    # дві доріжки-осі
    for yy, lab, col in [(y_idea, "ІДЕЯ / ТЕОРІЯ (папір)", NEG),
                         (y_real, "РОБОЧЕ ЗАЛІЗО", FIELD)]:
        f.append(line(ax, yy, ax + axw, yy, color=col, sw=1.6))
        f.append(text(ax, yy - 14, lab, size=12, bold=True, color=col, anchor="start"))
    # роки-засічки
    for yr in (1925, 1930, 1935, 1940, 1945, 1950, 1955):
        x = X(yr)
        f.append(line(x, y_idea, x, y_real, color="#e3e6ea", sw=1.0))
        f.append(text(x, y_real + 30, str(yr), size=11, color=MUTED))

    def node(x, y, col):
        return circle(x, y, 5.5, fill="#fff", stroke=col, sw=2.2)

    # ── доріжка ідеї/теорії ──
    # Лілієнфельд 1925–1930 (патент)
    f.append(node(X(1927.5), y_idea, NEG))
    b, w, h = textbox(X(1927.5), y_idea + 54, "Лілієнфельд\nпатент 1925–30\n(лише ідея)",
                      size=10, fill="#eef3fd", stroke=NEG, pad=7)
    f.append(b)
    f.append(line(X(1927.5), y_idea, X(1927.5), y_idea + 54 - h / 2, color=NEG, sw=1.0))
    # Гайль 1935 (патент)
    f.append(node(X(1935), y_idea, NEG))
    b, w, h = textbox(X(1935), y_idea + 54, "Гайль\nпатент 1935\n(лише ідея)",
                      size=10, fill="#eef3fd", stroke=NEG, pad=7)
    f.append(b)
    f.append(line(X(1935), y_idea, X(1935), y_idea + 54 - h / 2, color=NEG, sw=1.0))
    # Шоклі 1952 — теорія уніполярного
    f.append(node(X(1952), y_idea, NEG))
    b, w, h = textbox(X(1952), y_idea + 58, "Шоклі 1952\n«уніполярний»\nТЕОРІЯ JFET",
                      size=11, fill="#dfe7f5", stroke=NEG, pad=8, bold=True)
    f.append(b)
    f.append(line(X(1952), y_idea, X(1952), y_idea + 58 - h / 2, color=NEG, sw=1.4))

    # ── доріжка заліза ──
    # Шоклі 1945: польовий не вийшов (поверхневі стани)
    f.append(node(X(1945), y_real, POS))
    b, w, h = textbox(X(1945), y_real - 50, "1945: польовий\nне вийшов\n(поверхневі стани)",
                      size=10, fill="#fdecea", stroke=POS, pad=7)
    f.append(b)
    f.append(line(X(1945), y_real, X(1945), y_real - 50 + h / 2, color=POS, sw=1.0))
    # 1947 точковий, 1948 біполярний — «не той прилад»
    f.append(node(X(1947.5), y_real, "#b8860b"))
    b, w, h = textbox(X(1947.5), y_real - 50, "1947–48:\nвийшов БІПОЛЯРНИЙ\n(не польовий)",
                      size=10, fill="#fff6e6", stroke="#b8860b", pad=7)
    f.append(b)
    f.append(line(X(1947.5), y_real, X(1947.5), y_real - 50 + h / 2, color="#b8860b", sw=1.0))
    # Дейсі & Росс 1953 — перший робочий JFET
    f.append(node(X(1953), y_real, FIELD))
    b, w, h = textbox(X(1953), y_real - 56, "Дейсі & Росс 1953\nПЕРШИЙ РОБОЧИЙ\nJFET",
                      size=11, fill="#d6f0e2", stroke=FIELD, pad=8, bold=True)
    f.append(b)
    f.append(line(X(1953), y_real, X(1953), y_real - 56 + h / 2, color=FIELD, sw=1.4))

    # стрілка «теорія → залізо» (1952 → 1953): рік розриву
    f.append(arrow(X(1952), y_idea + 70, X(1953) - 4, y_real - 72, color=INK, sw=1.8))
    f.append(mtext((X(1952) + X(1953)) / 2 + 64, (y_idea + y_real) / 2 - 4,
                   ["теорія випередила", "залізо на рік"], size=11, bold=True,
                   color=INK, anchor="start"))

    # нижня рамка-висновок
    b, w, h = textbox(W / 2, 440,
                      "Папір ішов попереду: ідею патентували за 27 років до приладу; "
                      "Шоклі ж, ідучи до польового, першим зробив біполярний",
                      size=11, fill="#f7fbf8", stroke=FIELD, pad=9)
    f.append(b)
    render(os.path.join(IMG, "history-timeline.svg"), W, H, *f)


# ── 6. Поперечний переріз каналу (для math-вставки) ──────────────────────────
def fig_cross_section():
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 28, "Поперечний переріз: збіднені шари з'їдають по d, просвіт 2(a−d)",
                  size=15, bold=True))
    cx = W / 2
    bx, by, bw, bh = cx - 230, 90, 460, 200
    a_half = bh / 2                       # півтовщина a (від осі до краю)
    d = a_half * 0.42                     # з'їдено по d з кожного боку
    # повний канал (зелений)
    f.append(rect(bx, by, bw, bh, fill=CHAN, stroke=FIELD, sw=1.6))
    # p-затвори зовні (згори/знизу)
    f.append(rect(bx, by - 30, bw, 26, fill=PCOL, stroke=POS, sw=1.4))
    f.append(text(cx, by - 11, "p-затвор", size=12, bold=True, color=POS))
    f.append(rect(bx, by + bh + 4, bw, 26, fill=PCOL, stroke=POS, sw=1.4))
    f.append(text(cx, by + bh + 23, "p-затвор", size=12, bold=True, color=POS))
    # збіднені шари з боків (сірі) завтовшки d
    f.append(rect(bx, by, bw, d, fill=DEPL, stroke=MUTED, sw=1.0))
    f.append(rect(bx, by + bh - d, bw, d, fill=DEPL, stroke=MUTED, sw=1.0))
    f.append(text(bx + 70, by + d / 2 + 4, "збіднено (не проводить)", size=11, color=MUTED))
    f.append(text(bx + 70, by + bh - d / 2 + 4, "збіднено", size=11, color=MUTED))
    # просвіт посередині
    f.append(text(cx, by + bh / 2 + 5, "провідний просвіт", size=13, bold=True, color=FIELD))
    # вісь симетрії (пунктир)
    f.append(line(bx, by + bh / 2, bx + bw, by + bh / 2, color=MUTED, sw=1.0, dash="3 4"))
    # розмірні стрілки праворуч: a (півтовщина) і d
    rx = bx + bw + 26
    f.append(line(rx, by, rx, by + bh / 2, color=NEG, sw=1.2))
    f.append(arrow(rx, by + bh / 2, rx, by + 2, color=NEG, sw=1.4))
    f.append(arrow(rx, by + bh / 2, rx, by + bh / 2 - 2, color=NEG, sw=1.4))
    f.append(text(rx + 14, by + bh / 4 + 4, "a", size=13, bold=True, color=NEG, anchor="start", italic=True))
    f.append(line(rx + 40, by, rx + 40, by + d, color=POS, sw=1.2))
    f.append(arrow(rx + 40, by + d, rx + 40, by + 2, color=POS, sw=1.4))
    f.append(text(rx + 54, by + d / 2 + 4, "d", size=13, bold=True, color=POS, anchor="start", italic=True))
    # просвіт 2(a−d) — стрілка ліворуч
    lx = bx - 24
    f.append(line(lx, by + d, lx, by + bh - d, color=FIELD, sw=1.4))
    f.append(arrow(lx, by + bh / 2, lx, by + d + 2, color=FIELD, sw=1.4))
    f.append(arrow(lx, by + bh / 2, lx, by + bh - d - 2, color=FIELD, sw=1.4))
    f.append(mtext(lx - 40, by + bh / 2 - 6, ["2(a−d)", "просвіт"], size=11, bold=True,
                   color=FIELD, anchor="middle"))
    # висновок
    b, w, h = textbox(W / 2, 352, "d росте як корінь зі зміщення; d = a → канал зачинено",
                      size=12, fill="#f7fbf8", stroke=FIELD, pad=9)
    f.append(b)
    render(os.path.join(IMG, "cross-section.svg"), W, H, *f)


# ── 7. Канал-клин: V(x) росте до стоку, координата x (для math-вставки) ───────
def fig_wedge():
    import math
    W, H = 760, 462
    f = []
    f.append(text(W / 2, 26, "Канал-клин: до стоку V(x) і зміщення більші → збіднені шари товщі",
                  size=15, bold=True))
    ox, oy = 110, 250                 # лівий край каналу, вісь симетрії
    L = 520                           # довжина каналу на малюнку
    a_half = 78                       # півтовщина a
    Vp = 1.0                          # нормоване защемлення
    Vgs = -0.20                       # від'ємний затвор
    Vds = 0.65                        # стік нижче насичення

    def Vx(t):                        # потенціал уздовж каналу (приблизно лінійний)
        return Vds * t
    def dfrac(t):                     # d/a = корінь з місцевого зміщення / Vp
        return math.sqrt((Vx(t) - Vgs) / Vp)

    n = 60
    top = []                          # верхня межа просвіту
    bot = []                          # нижня межа просвіту
    for i in range(n + 1):
        t = i / n
        x = ox + t * L
        dd = a_half * dfrac(t)
        top.append((x, oy - (a_half - dd)))
        bot.append((x, oy + (a_half - dd)))
    # повний канал-брусок (зелений фон)
    f.append(rect(ox, oy - a_half, L, 2 * a_half, fill=CHAN, stroke=FIELD, sw=1.3))
    # p-затвори
    f.append(rect(ox, oy - a_half - 26, L, 22, fill=PCOL, stroke=POS, sw=1.2))
    f.append(text(ox + L / 2, oy - a_half - 10, "p-затвор (потенціал Vgs усюди)", size=11, bold=True, color=POS))
    f.append(rect(ox, oy + a_half + 4, L, 22, fill=PCOL, stroke=POS, sw=1.2))
    f.append(text(ox + L / 2, oy + a_half + 20, "p-затвор", size=11, bold=True, color=POS))
    # збіднені області (сірі) — між затвором і просвітом
    top_path = " ".join("%.1f,%.1f" % p for p in top)
    bot_path = " ".join("%.1f,%.1f" % p for p in bot)
    f.append('<polygon points="%s %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.0"/>'
             % (top_path, ox + L, oy - a_half, ox, oy - a_half, DEPL, MUTED))
    f.append('<polygon points="%s %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.0"/>'
             % (bot_path, ox + L, oy + a_half, ox, oy + a_half, DEPL, MUTED))
    # провідний просвіт (видно як зелений клин між сірими)
    f.append(text(ox + L * 0.32, oy + 4, "провідний просвіт (клин)", size=12, bold=True, color=FIELD))
    # S / D
    f.append(rect(ox - 30, oy - a_half + 14, 28, 2 * a_half - 28, fill="#dfe7f5", stroke=NEG, sw=1.3))
    f.append(text(ox - 16, oy + 4, "S", size=13, bold=True, color=NEG))
    f.append(text(ox - 16, oy + a_half + 40, "x=0", size=11, color=MUTED))
    f.append(text(ox - 16, oy + a_half + 54, "V=0", size=11, color=MUTED))
    f.append(rect(ox + L + 2, oy - a_half + 14, 28, 2 * a_half - 28, fill="#dfe7f5", stroke=NEG, sw=1.3))
    f.append(text(ox + L + 16, oy + 4, "D", size=13, bold=True, color=NEG))
    f.append(text(ox + L + 16, oy + a_half + 40, "x=L", size=11, color=MUTED))
    f.append(text(ox + L + 16, oy + a_half + 54, "V=Vds", size=11, color=MUTED))
    # координата x (під каналом, над висновком)
    xaxy = oy + a_half + 62
    f.append(arrow(ox, xaxy, ox + L, xaxy, color=INK, sw=1.4))
    f.append(text(ox + L + 8, xaxy + 4, "x", size=13, italic=True, anchor="start"))
    # профіль V(x) угорі — окрема міні-вісь
    py = 96
    f.append(text(ox - 4, py - 30, "V(x)", size=12, italic=True, anchor="end"))
    f.append(arrow(ox, py + 4, ox, py - 34, color=MUTED, sw=1.1))
    f.append(arrow(ox, py + 4, ox + L, py + 4, color=MUTED, sw=1.1))
    vpts = []
    for i in range(n + 1):
        t = i / n
        vpts.append("%.1f,%.1f" % (ox + t * L, py + 4 - Vx(t) / Vds * 32))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(vpts), NEG))
    f.append(text(ox + L + 8, py - 26, "Vds", size=11, color=NEG, anchor="start"))
    # висновок
    b, w, h = textbox(W / 2, 436,
                      "Місцеве зміщення V(x)−Vgs росте до стоку → d товщає → просвіт звужується",
                      size=11, fill="#f7fbf8", stroke=FIELD, pad=9)
    f.append(b)
    render(os.path.join(IMG, "wedge.svg"), W, H, *f)


# ── 8. Згортка в насичення: повний ID(Vds) → поличка (для math-вставки) ───────
def fig_saturate():
    import math
    W, H = 720, 420
    ox, oy = 110, 330
    axw, axh = 540, 260
    f = []
    f.append(text(W / 2, 26, "Повний ID(Vds) виходить на поличку точно в точці защемлення",
                  size=15, bold=True))
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))
    f.append(text(ox + axw, oy + 24, "Vds", size=13, italic=True))
    f.append(text(ox - 6, oy - axh + 4, "ID", size=13, anchor="end", italic=True))

    # омічна частина: повний кубічно-кореневий вираз, нормований так, що піку = 1 у Vsat
    Vp = 1.0
    Vgs = -0.30
    Vsat = Vp + Vgs                    # = 0.70 (точка защемлення, нормовано)
    G0 = 1.0
    # ID(Vds) = G0*[ Vds - (2/3)*((Vds-Vgs)^1.5 - (-Vgs)^1.5)/sqrt(Vp) ]
    def idfull(v):
        return G0 * (v - (2.0 / 3.0) * ((v - Vgs) ** 1.5 - (-Vgs) ** 1.5) / math.sqrt(Vp))
    Ipeak = idfull(Vsat)
    # масштаб на екран
    xsc = (axw - 40) / 1.4             # Vds-діапазон 0..1.4 нормованих
    ysc = (axh - 40) / (Ipeak * 1.15)

    pts = []
    n = 70
    for i in range(n + 1):
        v = Vsat * i / n
        x = ox + v * xsc
        y = oy - idfull(v) * ysc
        pts.append("%.1f,%.1f" % (x, y))
    # полиця насичення (горизонталь від Vsat)
    xs = ox + Vsat * xsc
    ys = oy - Ipeak * ysc
    for i in range(1, 56):
        v = Vsat + i * (1.4 - Vsat) / 56.0
        pts.append("%.1f,%.1f" % (ox + v * xsc, ys))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), FIELD))
    # точка защемлення
    f.append(circle(xs, ys, 5, fill="#fff", stroke=POS, sw=2.2))
    f.append(line(xs, oy, xs, ys, color=POS, sw=1.0, dash="4 4"))
    f.append(mtext(xs, oy + 20, ["Vds(sat)", "= Vp + Vgs"], size=11, bold=True, color=POS))
    f.append(line(ox, ys, xs, ys, color=FIELD, sw=1.0, dash="3 4"))
    f.append(text(ox - 6, ys + 4, "ID(sat)", size=11, bold=True, color=FIELD, anchor="end"))
    # підписи зон
    f.append(mtext(ox + Vsat * xsc * 0.45, oy - axh + 40, ["омічний:", "кубічний вираз росте"],
                   size=11, bold=True, color=MUTED))
    f.append(mtext(xs + (axw - 40 - Vsat * xsc) * 0.5, ys - 26, ["насичення:", "струм сталий"],
                   size=11, bold=True, color=MUTED))
    # нахил→0 у точці защемлення
    f.append(text(xs + 6, ys - 6, "нахил → 0", size=10, color=POS, anchor="start"))
    render(os.path.join(IMG, "saturate.svg"), W, H, *f)


# ── 9. Крутість як нахил передавальної кривої (для math-вставки) ─────────────
def fig_gm_slope():
    W, H = 740, 420
    ox, oy = 120, 330
    axw, axh = 540, 250
    f = []
    f.append(text(W / 2, 26, "Крутість gm — нахил кривої ID(Vgs): max при Vgs=0, →0 при Vp",
                  size=15, bold=True))
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))
    f.append(text(ox + axw, oy + 24, "Vgs", size=13, italic=True))
    f.append(text(ox - 6, oy - axh + 4, "ID", size=13, anchor="end", italic=True))

    zx = ox + axw - 36                # Vgs = 0 праворуч
    vpx = ox + 36                     # Vp ліворуч
    f.append(line(zx, oy, zx, oy - axh + 10, color=MUTED, sw=1.1, dash="4 4"))
    f.append(text(zx, oy + 20, "0", size=12, color=MUTED))
    f.append(line(vpx, oy, vpx, oy + 8, color=POS, sw=1.4))
    f.append(text(vpx, oy + 22, "Vp", size=12, bold=True, color=POS))

    idss_y = oy - (axh - 26)
    # парабола ID = IDSS*(1-Vgs/Vp)^2; t: 0 у Vp → 1 у нулі; ID ∝ t^2
    pts = []
    n = 80
    for i in range(n + 1):
        t = i / n
        x = vpx + t * (zx - vpx)
        y = oy - t * t * (oy - idss_y)
        pts.append((x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), FIELD))
    f.append(circle(zx, idss_y, 4.5, fill="#fff", stroke=FIELD, sw=2))
    f.append(text(ox - 6, idss_y + 4, "IDSS", size=12, bold=True, color=FIELD, anchor="end"))
    f.append(line(ox, idss_y, zx, idss_y, color=FIELD, sw=0.9, dash="3 4"))

    # дотичні (нахил=gm) у трьох точках: біля 0 (крута), посередині, біля Vp (полога)
    def tangent_at(t, col, lab):
        x0 = vpx + t * (zx - vpx)
        y0 = oy - t * t * (oy - idss_y)
        # нахил параболи dID/dVgs ∝ 2t (у екранних координатах, з урахуванням напрямів)
        span = (zx - vpx)
        slope = (2 * t) * (oy - idss_y) / span     # |dy/dx| екранний
        seg = 64
        x1, y1 = x0 - seg, y0 + slope * seg
        x2, y2 = x0 + seg, y0 - slope * seg
        out = [line(x1, y1, x2, y2, color=col, sw=2.0),
               circle(x0, y0, 4, fill=col, stroke=col, sw=1.0)]
        out.append(text(x0, y0 - 12, lab, size=10, bold=True, color=col,
                        anchor="middle" if t > 0.2 else "start"))
        return out

    f += tangent_at(0.92, POS, "крута → gm велика")
    f += tangent_at(0.55, "#b8860b", "")
    f += tangent_at(0.20, NEG, "полога → gm мала")

    # рамки-формули
    f.append(fitbox(ox + 70, oy - axh + 12, 250, 42,
                    "gm = −(2·IDSS/Vp)·(1 − Vgs/Vp)", size=12, fill="#f7fbf8",
                    stroke=FIELD, bold=True))
    f.append(fitbox(ox + 70, oy - axh + 60, 250, 36,
                    "gm ∝ √ID", size=13, fill="#fef7e6", stroke="#b8860b", bold=True))
    render(os.path.join(IMG, "gm-slope.svg"), W, H, *f)


if __name__ == "__main__":
    fig_structure()
    fig_squeeze()
    fig_transfer()
    fig_output()
    fig_history_timeline()
    fig_cross_section()
    fig_wedge()
    fig_saturate()
    fig_gm_slope()
    print("OK: 9 figures ->", IMG)
