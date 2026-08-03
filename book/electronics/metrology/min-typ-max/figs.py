# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#a9781a"   # «typ» — інформаційне, не гарантоване


def bell(ox, baseline, x0, x1, mu, sigma, peak, color, sw=2.4, fill=None, n=240):
    """Дзвін Гауса як polyline (за потреби — із заливкою-area).
    Координати в px: вісь по x від x0 до x1, висота вгору від baseline."""
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        z = (x - mu) / sigma
        y = baseline - peak * math.exp(-0.5 * z * z)
        pts.append((x, y))
    line_pts = " ".join("%.1f,%.1f" % p for p in pts)
    out = ""
    if fill:
        area = "M %.1f,%.1f " % (pts[0][0], baseline) + \
               " ".join("L %.1f,%.1f" % p for p in pts) + \
               " L %.1f,%.1f Z" % (pts[-1][0], baseline)
        out += '<path d="%s" fill="%s" stroke="none"/>' % (area, fill)
    out += ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (line_pts, color, sw))
    return out


# ── table: три колонки + умови ─────────────────────────────────────────────────
# Ідея: серце розділу — рядок параметра з min/typ/max і стовпцем умов; зелені краї
# гарантовані, жовтий «typ» — лише очікуваний, а умови роблять число дійсним.

def fig_table():
    W, H = 720, 320
    p = []
    x0, w = 40, 640
    cols = [56, 250, 404, 474, 544, 612]   # Параметр, Умови, Min, Typ, Max, Од.
    head_y = 70
    # шапка
    p.append(rect(x0, 50, w, 30, fill="#eef2f7", stroke="#7f93a8", sw=1.5))
    heads = [("Параметр", INK), ("Умови", INK), ("Min", FIELD), ("Typ", GOLD), ("Max", FIELD), ("Од.", INK)]
    for cx, (lab, col) in zip(cols, heads):
        p.append(text(cx, head_y, lab, size=12, color=col, anchor="start", bold=True))
    # рядки
    rows = [
        ("Напруга зсуву Vos", "Vcc=5 В, 25 °C", "—", "0.5", "3", "мВ", "max"),
        ("Струм спокою Iq", "без навантаж.", "—", "0.9", "1.5", "мА", "max"),
        ("Смуга GBW", "—", "8", "10", "—", "МГц", "min"),
        ("Rds(on)", "Vgs=10 В", "—", "18", "25", "мОм", "max"),
    ]
    ry = 80
    rh = 40
    for name, cond, vmin, vtyp, vmax, unit, hard in rows:
        p.append(rect(x0, ry, w, rh, fill=BG, stroke="#c9d3dc", sw=1.1, rx=0))
        ty = ry + 25
        p.append(text(cols[0], ty, name, size=11, anchor="start"))
        p.append(text(cols[1], ty, cond, size=11, anchor="start"))
        # min / max — зелені й жирні, коли це гарантований бік цього параметра
        p.append(text(cols[2], ty, vmin, size=11, anchor="start",
                      color=FIELD if hard == "min" and vmin != "—" else INK,
                      bold=(hard == "min" and vmin != "—")))
        p.append(text(cols[3], ty, vtyp, size=11, anchor="start", color=GOLD))
        p.append(text(cols[4], ty, vmax, size=11, anchor="start",
                      color=FIELD if hard == "max" and vmax != "—" else INK,
                      bold=(hard == "max" and vmax != "—")))
        p.append(text(cols[5], ty, unit, size=11, anchor="start", color=MUTED))
        ry += rh
    p.append(text(W / 2, ry + 24,
                  "зелене — гарантований край; жовте «typ» — лише очікуване; умови роблять число дійсним",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "table.svg"), W, H, *p,
           title="Кожен параметр: min · typ · max і — найважливіше — стовпець умов")


# ── distribution: «typ» — центр дзвона, гарантія — краї ────────────────────────
# Ідея: параметри партії лягають дзвоном; гарантують лише min/max на хвостах, а
# «typ» — лише вершина (найімовірніше), твій екземпляр — будь-де в проміжку.

def fig_distribution():
    W, H = 700, 330
    ox, oy = 90, 250
    span_x0, span_x1 = 90, 610
    mu = (span_x0 + span_x1) / 2
    sigma = (span_x1 - span_x0) / 6.4
    peak = 150
    p = []
    p.append(arrow(ox, oy, 630, oy, color=INK, sw=2))
    p.append(text(636, oy + 4, "параметр", size=11, color=INK, anchor="start", bold=True))
    p.append(bell(ox, oy, span_x0, span_x1, mu, sigma, peak, NEG, sw=2.6))
    # межі min / max на ~±3σ
    xmin, xmax = mu - 3 * sigma, mu + 3 * sigma
    for xx, lab in ((xmin, "min"), (xmax, "max")):
        p.append(line(xx, oy, xx, oy - 85, color=FIELD, sw=1.8, dash="5 4"))
        p.append(text(xx, oy + 18, lab, size=11, color=FIELD, bold=True))
    # typ — вершина
    p.append(line(mu, oy, mu, oy - peak + 3, color=GOLD, sw=1.8, dash="3 3"))
    p.append(text(mu, oy + 18, "typ", size=11, color=GOLD, bold=True))
    p.append(text(mu, oy - peak - 8, "усі випущені — між min і max (гарантовано)",
                  size=11, color=FIELD, bold=True))
    p.append(text(mu, oy - 72, "твій — будь-де тут", size=10, color=INK))
    render(os.path.join(OUT, "distribution.svg"), W, H, *p,
           title="«typ» — центр розкиду партії, а не обіцянка")


# ── design: розрахунок на typ підводить, на край — покриває всіх ───────────────
# Ідея: дві панелі з тим самим дзвоном. Зліва межа на typ — хвіст партії за нею
# (червоний), справа межа на гарантований край — уся крива з безпечного боку.

def fig_design():
    W, H = 700, 300
    p = []
    panel_w, panel_h = 320, 222
    oy = 252
    peak = 122

    def panel(px, title_lab, sub_lab, sub_col, cut_at_typ):
        out = [rect(px, 52, panel_w, panel_h, fill=BG, stroke="#c9d3dc", sw=1.4)]
        out.append(text(px + panel_w / 2, 46, title_lab, size=12, bold=True))
        out.append(text(px + panel_w / 2, 76, sub_lab, size=10, color=sub_col, bold=True))
        x0, x1 = px + 32, px + panel_w - 32
        mu = (x0 + x1) / 2 - 18
        sigma = (x1 - x0) / 6.4
        if cut_at_typ:
            out.append(bell(px, oy, x0, x1, mu, sigma, peak, NEG, sw=2.2))
            out.append(line(mu, oy, mu, oy - peak - 4, color=GOLD, sw=1.6, dash="3 3"))
            out.append(text(mu, oy + 16, "typ", size=9, color=GOLD, bold=True))
            cut = mu + 1.0 * sigma
            out.append(line(cut, oy - peak - 2, cut, oy, color=POS, sw=1.6))
            # хвіст за межею — червона area
            out.append(bell(px, oy, cut, x1, mu, sigma, peak, "none", sw=0.0,
                            fill="#fbe3e1"))
            out.append(bell(px, oy, x0, x1, mu, sigma, peak, NEG, sw=2.2))  # перемалювати лінію зверху
            out.append(text(cut + 30, oy - 40, "ці —", size=9, color=POS, bold=True))
            out.append(text(cut + 30, oy - 27, "за межу", size=9, color=POS))
        else:
            out.append(bell(px, oy, x0, x1, mu, sigma, peak, NEG, sw=2.2))
            edge = mu + 3 * sigma
            out.append(line(edge, oy - peak - 2, edge, oy, color=FIELD, sw=1.8))
            out.append(text(edge, oy + 16, "max", size=9, color=FIELD, bold=True))
            out.append(text(px + panel_w / 2, 94, "уся крива — лівіше межі",
                            size=9, color=FIELD, bold=True))
        return out

    p += panel(28, "розрахунок на «typ» — підведе", "а частина партії гірша", POS, True)
    p += panel(372, "розрахунок на гарантований край — надійно", "уся партія в безпеці", FIELD, False)
    p.append(text(W / 2, 290,
                  "на «typ» проектуєш під половину приладів; гарантований край покриває кожен",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "design.svg"), W, H, *p,
           title="Розраховуй на гарантований край, а не на «typ»")


# ── conditions: те саме число — лише для своїх умов ────────────────────────────
# Ідея: один параметр (Rds(on)) під двома температурами дає різні числа; стрілка
# «нагрів» між картками показує, що умови — половина числа.

def fig_conditions():
    W, H = 700, 290
    p = []
    bw, bh = 250, 130
    by = 80
    left = fitbox(70, by, bw, bh, "", fill="#eef6ef", stroke=FIELD, sw=1.6)
    p.append(left)
    p.append(text(195, by + 28, "Rds(on)", size=13, bold=True))
    p.append(text(195, by + 58, "20 мОм", size=22, color=FIELD, bold=True))
    p.append(text(195, by + 88, "@ Vgs=10 В, 25 °C", size=10))
    p.append(text(195, by + 110, "(умови з даташита)", size=9, color=MUTED))

    right = fitbox(390, by, bw, bh, "", fill="#fbecec", stroke=POS, sw=1.6)
    p.append(right)
    p.append(text(515, by + 28, "той самий Rds(on)", size=12, bold=True))
    p.append(text(515, by + 58, "≈ 40 мОм", size=22, color=POS, bold=True))
    p.append(text(515, by + 88, "@ Vgs=10 В, 125 °C", size=10))
    p.append(text(515, by + 110, "(у спеку — майже вдвічі)", size=9, color=POS))

    p.append(arrow(326, by + 65, 384, by + 65, color=MUTED, sw=2.2))
    p.append(text(355, by + 50, "нагрів", size=10, color=MUTED))
    p.append(text(W / 2, 270,
                  "той самий параметр під іншою температурою чи напругою — інше число; звіряй умови зі своїми",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "conditions.svg"), W, H, *p,
           title="Те саме число — лише для своїх умов")


# ── which-column: який край небезпечний ────────────────────────────────────────
# Ідея: таблиця «що боїшся → який край». Завеликого боїшся → max; замалого → min;
# поріг важить обома краями. «typ» при цьому осторонь.

def fig_which_column():
    W, H = 700, 300
    p = []
    rows = [
        ("Напруга зсуву, шум, струм спокою", "MAX", POS, "#fbecec", "менше — добре, боїшся великого"),
        ("Підсилення, вихідний струм, смуга", "MIN", NEG, "#e9eefb", "більше — добре, боїшся малого"),
        ("Dropout, вхідний струм, витік", "MAX", POS, "#fbecec", "хочеш якнайменше"),
        ("Поріг увімкнення (інколи)", "MIN і MAX", INK, "#f3f3f3", "важать обидва краї"),
    ]
    y = 64
    rh = 48
    for desc, badge, col, fill, note in rows:
        p.append(rect(50, y, 340, 38, fill=BG, stroke="#c9d3dc", sw=1.3))
        p.append(text(64, y + 24, desc, size=10, anchor="start"))
        bw = 110 if badge == "MIN і MAX" else 90
        p.append(rect(410, y, bw, 38, fill=fill, stroke=col, sw=1.4))
        p.append(text(410 + bw / 2, y + 24, badge, size=11, color=col, bold=True))
        p.append(text(410 + bw + 8, y + 24, note, size=9, color=MUTED, anchor="start"))
        y += rh
    p.append(text(W / 2, y + 16,
                  "дивись на той край, де ховається біда: для одних це max, для інших — min",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "which-column.svg"), W, H, *p,
           title="Який край небезпечний — залежить від параметра")


# ── recipe: три кроки читання рядка ────────────────────────────────────────────
# Ідея: рефлекс із трьох кроків — знайди параметр → знайди свої умови → читай
# гарантовану колонку (той бік, де біда).

def fig_recipe():
    W, H = 700, 220
    p = []
    steps = [
        (40, "#e9eefb", "Знайди параметр", "пошуком по назві"),
        (256, "#fff3e0", "Знайди свої умови", "потрібний рядок / інтерполяція"),
        (472, "#eef6ef", "Читай гарантовану колонку", "min або max — гірший бік"),
    ]
    sw_, sh = 188, 80
    y = 70
    centers = []
    for i, (x, fill, head, sub) in enumerate(steps):
        p.append(rect(x, y, sw_, sh, fill=fill, stroke="#9bb0c2", sw=1.5, rx=8))
        p.append(circle(x + 24, y + 26, 13, fill=BG, stroke=INK, sw=1.6))
        p.append(text(x + 24, y + 31, str(i + 1), size=13, bold=True))
        p.append(text(x + 44, y + 31, head, size=11, anchor="start", bold=True))
        p.append(text(x + 14, y + 58, sub, size=9, anchor="start"))
        centers.append((x, x + sw_))
        if i > 0:
            p.append(arrow(centers[i - 1][1] + 2, y + sh / 2, x - 4, y + sh / 2, color=INK, sw=2))
    p.append(text(W / 2, 200,
                  "параметр → свої умови → гарантований край: три кроки — і число, якому можна вірити",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "recipe.svg"), W, H, *p,
           title="Рецепт читання рядка таблиці")


# ── lot-spread (math): «typ» — центр, гарантія — краї на ±3σ ───────────────────
# Ідея: розкид параметра в партії — нормальний дзвін; min/max на хвостах ≈±3σ,
# typ = центр; запас typ→край — кілька сигм.

def fig_lot_spread():
    W, H = 840, 430
    ox, oy = 80, 320
    x0, x1 = 80, 670
    mu = (x0 + x1) / 2
    sigma = (x1 - x0) / 6.6
    peak = 215
    p = []
    p.append(arrow(ox, oy, 694, oy, color=INK, sw=2))
    p.append(text(698, oy + 5, "значення параметра", size=13, color=INK, anchor="start", bold=True))
    p.append(bell(ox, oy, x0, x1, mu, sigma, peak, NEG, sw=2.6, fill="#e9eefb"))
    xmin, xmax = mu - 3 * sigma, mu + 3 * sigma
    for xx, lab in ((xmin, "min"), (xmax, "max")):
        p.append(line(xx, oy, xx, oy - 2, color=FIELD, sw=2.4))
        p.append(text(xx, oy + 22, lab, size=14, color=FIELD, bold=True))
    # сигма-позначки
    for k in (-2, -1, 1, 2):
        xx = mu + k * sigma
        p.append(line(xx, oy, xx, oy + 6, color=MUTED, sw=1.6))
        p.append(text(xx, oy + 17, ("%+d" % k).replace("+", "+") + "σ", size=11, color=MUTED))
    # смуга «кожен прилад тут»
    p.append(rect(xmin, oy + 30, xmax - xmin, 16, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(mu, oy + 42, "гарантовано: КОЖЕН прилад тут", size=12, color=FIELD, bold=True))
    # typ
    p.append(line(mu, oy, mu, oy - peak, color=GOLD, sw=2.6))
    p.append(text(mu, oy - peak - 10, "typ", size=15, color=GOLD, bold=True))
    p.append(text(mu, oy - peak - 26, "(центр / найімовірніше)", size=11, color=GOLD))
    # запас typ→max ≈ 3σ
    p.append(line(mu, 59, xmax, 59, color=POS, sw=1.8))
    p.append(line(mu, 59, mu, 67, color=POS, sw=1.8))
    p.append(line(xmax, 59, xmax, 67, color=POS, sw=1.8))
    p.append(text((mu + xmax) / 2, 51, "запас typ→max ≈ 3σ", size=12, color=POS, bold=True))
    p.append(text(ox, 416,
                  "вужчі min/max = менша σ (точніший процес) АБО відбір кращих екземплярів = дорожче",
                  size=12, color=INK, anchor="start"))
    render(os.path.join(OUT, "lot-spread.svg"), W, H, *p,
           title="Розкид параметра в партії: «typ» — центр, гарантія — краї")


# ── binning (math): один процес — кілька сортів ───────────────────────────────
# Ідея: одна крива розкиду ріжеться тестом на сорти. Центр → дорогий прецизійний
# (вузькі краї), ширший шмат → дешевший стандартний, хвости — у брак. «typ» один.

def fig_binning():
    W, H = 843, 420
    ox, oy = 70, 300
    x0, x1 = 80, 680
    mu = (x0 + x1) / 2
    sigma = (x1 - x0) / 6.6
    peak = 190
    p = []
    p.append(arrow(ox, oy, 704, oy, color=INK, sw=2))
    p.append(text(708, oy + 5, "напруга зсуву Vos", size=13, color=INK, anchor="start", bold=True))

    prec_lo, prec_hi = mu - 1.0 * sigma, mu + 1.0 * sigma   # прецизійний сорт
    std_lo, std_hi = mu - 3.0 * sigma, mu + 3.0 * sigma     # стандартний сорт
    # заливки: хвости (брак) сірі, стандарт синюватий, прецизія зелена
    p.append(bell(ox, oy, x0, std_lo, mu, sigma, peak, "none", sw=0.0, fill="#e4e4e4"))
    p.append(bell(ox, oy, std_hi, x1, mu, sigma, peak, "none", sw=0.0, fill="#e4e4e4"))
    p.append(bell(ox, oy, std_lo, std_hi, mu, sigma, peak, "none", sw=0.0, fill="#e9eefb"))
    p.append(bell(ox, oy, prec_lo, prec_hi, mu, sigma, peak, "none", sw=0.0, fill="#eef6ef"))
    p.append(bell(ox, oy, x0, x1, mu, sigma, peak, INK, sw=2.4))   # контур зверху

    for xx in (std_lo, std_hi):
        p.append(line(xx, oy, xx, oy - peak * 0.62, color=MUTED, sw=1.6, dash="4 4"))
    for xx in (prec_lo, prec_hi):
        p.append(line(xx, oy, xx, oy - peak, color=MUTED, sw=1.6, dash="4 4"))

    # підписи сортів
    p.append(rect(prec_lo, oy + 12, prec_hi - prec_lo, 18, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(mu, oy + 25, "ПРЕЦИЗІЙНИЙ ±0.5 мВ", size=12, color=FIELD, bold=True))
    p.append(rect(std_lo, oy + 36, std_hi - std_lo, 18, fill="none", stroke=NEG, sw=1.4, rx=4))
    p.append(text(mu, oy + 49, "СТАНДАРТНИЙ ±3 мВ", size=12, color=NEG, bold=True))
    p.append(text(std_lo - 8, oy - 4, "відбраковано", size=11, color=MUTED, anchor="end"))
    p.append(text(std_hi + 8, oy - 4, "відбраковано", size=11, color=MUTED, anchor="start"))
    # typ один на всіх
    p.append(line(mu, oy, mu, oy - peak, color=GOLD, sw=2.2))
    p.append(text(mu, oy - peak - 8, "typ — однакове в усіх сортів", size=12, color=GOLD, bold=True))
    p.append(text(ox, 404,
                  "сортування коштує: «typ» однакове, а гарантований край (max) — різний, звідси й ціна",
                  size=12, color=INK, anchor="start"))
    render(os.path.join(OUT, "binning.svg"), W, H, *p,
           title="Біннінг: один процес — кілька сортів за тим самим номером")


if __name__ == "__main__":
    fig_table()
    fig_distribution()
    fig_design()
    fig_conditions()
    fig_which_column()
    fig_recipe()
    fig_lot_spread()
    fig_binning()
    print("OK: figures written to", OUT)
