# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(points, color=INK, sw=2.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (pts, color, sw, d))


# ── Фігура 1: два полюси й чому один роблять домінантним ─────────────────────
def fig_two_poles():
    W, H = 720, 430
    f = []
    f.append(text(W/2, 26, "Два полюси підсилювача: до корекції і після", size=17, bold=True))

    # дві координатні панелі: ліворуч «без корекції», праворуч «з корекцією»
    def panel(ox, label, p1x, p2x, fc_x, crossed):
        g = []
        x0, y0 = ox + 18, 250          # початок осей
        ax_w, ax_h = 250, 170
        # осі
        g.append(line(x0, y0, x0 + ax_w, y0, color=INK, sw=1.8))         # частота →
        g.append(line(x0, y0, x0, y0 - ax_h, color=INK, sw=1.8))         # |A|, дБ ↑
        g.append(text(x0 + ax_w, y0 + 18, "частота (log)", size=11, color=MUTED, anchor="end"))
        g.append(text(x0 - 6, y0 - ax_h + 4, "|A|", size=12, color=MUTED, anchor="end"))
        g.append(text(ox + 18 + ax_w/2, 78, label, size=13, bold=True))

        ytop = y0 - ax_h + 16          # рівень DC-підсилення
        # ламана АЧХ: пласко до p1, −20 дБ/дек до p2, далі −40 дБ/дек
        seg = []
        seg.append((x0, ytop))
        seg.append((p1x, ytop))
        # нахил −20: від p1 до p2
        slope1 = 1.0
        y_at_p2 = ytop + (p2x - p1x) * slope1
        seg.append((p2x, y_at_p2))
        # нахил −40 далі до краю
        y_edge = y_at_p2 + (x0 + ax_w - p2x) * 2.0
        y_edge = min(y_edge, y0 - 4)
        seg.append((x0 + ax_w - 4, y_edge))
        g.append(polyline(seg, color=NEG, sw=3))

        # лінія 0 дБ (де |A|=1)
        zero_y = y0 - 14
        g.append(line(x0, zero_y, x0 + ax_w, zero_y, color=MUTED, sw=1.2, dash="5 4"))
        g.append(text(x0 + 4, zero_y - 4, "0 дБ", size=10, color=MUTED, anchor="start"))

        # позначки полюсів
        for px, lab in ((p1x, "p₁"), (p2x, "p₂")):
            g.append(line(px, y0, px, y0 - ax_h, color=MUTED, sw=1.0, dash="3 4"))
            g.append(circle(px, y0, 4, fill=POS, stroke=POS, sw=1))
            g.append(text(px, y0 + 16, lab, size=12, color=POS, bold=True))

        # частота зрізу контуру (де крива перетинає 0 дБ) — позначимо
        g.append(circle(fc_x, zero_y, 5, fill=FIELD, stroke=FIELD, sw=1))
        return g

    # БЕЗ корекції: p1 і p2 близько → крива перетинає 0 дБ вже на крутому −40
    f += panel(20, "без корекції", p1x=20+18+70, p2x=20+18+120, fc_x=20+18+185, crossed=True)
    # вердикт під лівою панеллю
    f.append(fitbox(38, 282, 250, 56,
                    "на 0 дБ нахил уже −40 дБ/дек\n→ фаза ~−180° → дзвенить",
                    size=12, fill="#fdecea", stroke=POS, color=POS))

    # З корекцією: p1 «відтягнуто» далеко вліво (низька частота) → 0 дБ задовго до p2
    f += panel(390, "з корекцією (полюс зсунуто)", p1x=390+18+22, p2x=390+18+150, fc_x=390+18+120, crossed=False)
    f.append(fitbox(408, 282, 250, 56,
                    "p₁ зсунуто вниз: 0 дБ настає\nдо p₂, нахил −20 → запас фази є",
                    size=12, fill="#eafaf1", stroke=FIELD, color="#1e7a45"))

    render(os.path.join(IMG, 'two-poles.svg'), W, H, *f)


# ── Фігура 2: rate of closure — |A| і лінія 1/β ─────────────────────────────
def fig_rate_of_closure():
    W, H = 720, 470
    f = []
    f.append(text(W/2, 26, "Швидкість зближення: |A| проти лінії 1/β", size=17, bold=True))

    x0, y0 = 70, 380
    ax_w, ax_h = 580, 300
    f.append(line(x0, y0, x0 + ax_w, y0, color=INK, sw=1.8))
    f.append(line(x0, y0, x0, y0 - ax_h, color=INK, sw=1.8))
    f.append(text(x0 + ax_w, y0 + 20, "частота (log)", size=12, color=MUTED, anchor="end"))
    f.append(text(x0 - 8, y0 - ax_h + 6, "дБ", size=12, color=MUTED, anchor="end"))

    ytop = y0 - ax_h + 24
    # крива розімкненого |A|: пласко, потім −20, потім −40 (другий полюс)
    p1x = x0 + 60
    p2x = x0 + 330
    y_p2 = ytop + (p2x - p1x) * 0.62          # нахил −20 (помірний, щоб лишити місце)
    y_end = min(y_p2 + (x0 + ax_w - p2x) * 1.24, y0 - 8)   # −40 далі
    seg = [(x0, ytop), (p1x, ytop), (p2x, y_p2), (x0 + ax_w - 4, y_end)]
    f.append(polyline(seg, color=NEG, sw=3))
    f.append(text(p1x + 8, ytop - 8, "розімкнене |A|", size=12, color=NEG, anchor="start", bold=True))
    f.append(text(p2x + 8, y_p2 - 4, "p₂", size=12, color=POS, anchor="start", bold=True))
    f.append(circle(p2x, y_p2, 4, fill=POS, stroke=POS, sw=1))

    # висока полиця 1/β (G=100) — перетинає на −20 ділянці → стійко
    yA = ytop + 70
    f.append(line(x0, yA, x0 + ax_w, yA, color=FIELD, sw=2.2, dash="7 5"))
    f.append(text(x0 + 8, yA - 7, "1/β високе (G=100)", size=11, color="#1e7a45", anchor="start", bold=True))
    cxA = p1x + (yA - ytop) / 0.62        # перетин на нахилі 0.62
    f.append(circle(cxA, yA, 6, fill=FIELD, stroke="#1e7a45", sw=1.5))
    f.append(text(cxA, yA - 16, "перетин на −20: розбіжність\n20 дБ/дек → стійко",
                  size=10, color="#1e7a45", anchor="middle"))

    # низька полиця 1/β (G=1) — перетинає вже на −40 ділянці → ризик
    yB = y_p2 + (y_end - y_p2) * 0.42
    f.append(line(x0, yB, x0 + ax_w, yB, color=POS, sw=2.2, dash="7 5"))
    f.append(text(x0 + 8, yB - 7, "1/β низьке (G=1)", size=11, color=POS, anchor="start", bold=True))
    cxB = p2x + (yB - y_p2) / 1.24        # перетин на нахилі 1.24
    f.append(circle(cxB, yB, 6, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(cxB + 10, yB + 18, "перетин на −40: розбіжність\n40 дБ/дек → дзвін, генерація",
                  size=10, color=POS, anchor="middle"))

    render(os.path.join(IMG, 'rate-of-closure.svg'), W, H, *f)


# ── Фігура 3: ємнісне навантаження додає полюс; лік — резистор у вихід ───────
def fig_cap_load():
    W, H = 720, 360
    f = []
    f.append(text(W/2, 26, "Ємнісне навантаження краде запас фази", size=17, bold=True))

    # ліва схема: ОП з Cload — Rout + CL утворюють зайвий полюс
    def opamp(cx, cy, label):
        g = []
        # трикутник
        g.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (cx-30, cy-26, cx-30, cy+26, cx+34, cy, FILL, LINE))
        g.append(minus(cx-22, cy-13, r=7))
        g.append(plus(cx-22, cy+13, r=7))
        g.append(text(cx, cy+44, label, size=11, color=MUTED))
        return g, cx+34, cy   # вихідна точка

    # ── ліворуч: без резистора ──
    gx, ox, oy = opamp(140, 150, "вихідний опір Rout")
    f += gx
    # лінія виходу до вузла
    nodex = 250
    f.append(line(ox, oy, nodex, oy, color=INK, sw=1.8))
    # Rout як символ (зигзаг спрощено прямокутником)
    f.append(rect(ox+14, oy-9, 34, 18, fill="#fff", stroke=INK, sw=1.4, rx=3))
    f.append(text(ox+31, oy-14, "Rout", size=10, color=MUTED))
    # конденсатор навантаження на землю
    f.append(line(nodex, oy, nodex, oy+34, color=INK, sw=1.8))
    f.append(line(nodex-14, oy+34, nodex+14, oy+34, color=INK, sw=2.2))
    f.append(line(nodex-14, oy+42, nodex+14, oy+42, color=INK, sw=2.2))
    f.append(text(nodex+22, oy+40, "C_L", size=11, color=POS, bold=True))
    # земля
    f.append(line(nodex, oy+42, nodex, oy+58, color=INK, sw=1.6))
    f.append(line(nodex-10, oy+58, nodex+10, oy+58, color=INK, sw=1.6))
    f.append(line(nodex-6, oy+62, nodex+6, oy+62, color=INK, sw=1.6))
    f.append(fitbox(70, 232, 220, 48,
                    "Rout · C_L → зайвий полюс\n+(−90°) фази → запас падає",
                    size=12, fill="#fdecea", stroke=POS, color=POS))

    # ── праворуч: з розв'язувальним резистором Riso ──
    gx2, ox2, oy2 = opamp(470, 150, "той самий ОП")
    f += gx2
    nodex2 = 560
    # Riso послідовно у вихід
    f.append(line(ox2, oy2, ox2+14, oy2, color=INK, sw=1.8))
    f.append(rect(ox2+14, oy2-9, 34, 18, fill="#eafaf1", stroke=FIELD, sw=1.6, rx=3))
    f.append(text(ox2+31, oy2-14, "Riso", size=10, color="#1e7a45", bold=True))
    f.append(line(ox2+48, oy2, nodex2, oy2, color=INK, sw=1.8))
    # навантаження
    f.append(line(nodex2, oy2, nodex2, oy2+34, color=INK, sw=1.8))
    f.append(line(nodex2-14, oy2+34, nodex2+14, oy2+34, color=INK, sw=2.2))
    f.append(line(nodex2-14, oy2+42, nodex2+14, oy2+42, color=INK, sw=2.2))
    f.append(text(nodex2+22, oy2+40, "C_L", size=11, color=MUTED))
    f.append(line(nodex2, oy2+42, nodex2, oy2+58, color=INK, sw=1.6))
    f.append(line(nodex2-10, oy2+58, nodex2+10, oy2+58, color=INK, sw=1.6))
    f.append(line(nodex2-6, oy2+62, nodex2+6, oy2+62, color=INK, sw=1.6))
    f.append(fitbox(400, 232, 240, 48,
                    "Riso ізолює C_L від петлі →\nполюс іде вгору, запас фази назад",
                    size=12, fill="#eafaf1", stroke=FIELD, color="#1e7a45"))

    render(os.path.join(IMG, 'cap-load.svg'), W, H, *f)


# ── Фігура 4: розщеплення полюсів на дійсній осі ─────────────────────────────
def fig_pole_split():
    W, H = 720, 430
    f = []
    f.append(text(W/2, 26, "Розщеплення полюсів: Cc розводить їх у різні боки", size=17, bold=True))

    # одна горизонтальна вісь σ (дійсна частина s), полюси — хрестики на ній.
    x0, xr = 90, 640          # від лівого до правого краю осі
    y_un, y_cm = 150, 300     # рядок «без Cc» і рядок «з Cc»
    sigma0 = x0 + 12          # точка σ = 0 (уявна вісь / початок)

    def axis(yc, label):
        g = []
        g.append(line(x0, yc, xr, yc, color=INK, sw=1.8))
        # стрілка вліво — у бік зростання |полюса| (швидше згасання)
        g.append(text(xr - 4, yc - 10, "−σ  (далі від нуля = вищий полюс) →", size=11,
                      color=MUTED, anchor="end"))
        # позначка осі jω (σ=0)
        g.append(line(sigma0, yc - 26, sigma0, yc + 26, color=MUTED, sw=1.2, dash="3 4"))
        g.append(text(sigma0, yc + 40, "σ = 0", size=10, color=MUTED))
        g.append(text(x0 - 8, yc - 30, label, size=13, bold=True, anchor="start"))
        return g

    def pole(px, yc, color):
        s = 7
        return (line(px - s, yc - s, px + s, yc + s, color=color, sw=3) +
                line(px - s, yc + s, px + s, yc - s, color=color, sw=3))

    # БЕЗ Cc: два полюси близько одне до одного, обидва помірно далеко від нуля
    f += axis(y_un, "без Cc")
    un_p1 = sigma0 + 150       # 1/(R1·C1)
    un_p2 = sigma0 + 250       # 1/(R2·C2) — поруч
    f.append(pole(un_p1, y_un, NEG))
    f.append(pole(un_p2, y_un, NEG))
    f.append(text(un_p1, y_un - 30, "p₁ = 1/(R₁C₁)", size=11, color=NEG, bold=True))
    f.append(text(un_p2, y_un - 14, "p₂ = 1/(R₂C₂)", size=11, color=NEG, bold=True))
    f.append(fitbox(sigma0 + 110, y_un + 18, 210, 26, "два полюси поруч → дзвін",
                    size=11, fill="#fdecea", stroke=POS, color=POS))

    # З Cc: p1 сунеться ДО нуля (вліво по модулю), p2 — ГЕТЬ від нуля (вправо)
    f += axis(y_cm, "з Cc")
    cm_p1 = sigma0 + 36        # 1/(gm2·R1·R2·Cc) — близько до нуля
    cm_p2 = sigma0 + 470       # gm2·Cc/(C1·C2) — далеко
    f.append(pole(cm_p1, y_cm, FIELD))
    f.append(pole(cm_p2, y_cm, FIELD))
    f.append(text(cm_p1 + 4, y_cm - 14, "p₁↓  1/(gm₂R₁R₂Cc)", size=11, color="#1e7a45",
                  bold=True, anchor="start"))
    f.append(text(cm_p2, y_cm - 14, "p₂↑  gm₂Cc/(C₁C₂)", size=11, color="#1e7a45", bold=True))

    # стрілки, що показують рознесення (від «без Cc» рівня вниз до «з Cc»)
    f.append(arrow(un_p1, y_un + 30, cm_p1 + 8, y_cm - 18, color=FIELD, sw=2))
    f.append(arrow(un_p2, y_un + 30, cm_p2 - 8, y_cm - 18, color=FIELD, sw=2))
    f.append(text((un_p1 + cm_p1)/2 - 40, (y_un + y_cm)/2, "вниз", size=10,
                  color="#1e7a45", anchor="end", italic=True))
    f.append(text((un_p2 + cm_p2)/2 + 40, (y_un + y_cm)/2, "вгору", size=10,
                  color="#1e7a45", anchor="start", italic=True))
    f.append(fitbox(sigma0 + 70, y_cm + 18, 360, 26,
                    "один пішов до нуля, другий — геть: пологий −20 дБ/дек став широким",
                    size=11, fill="#eafaf1", stroke=FIELD, color="#1e7a45"))

    render(os.path.join(IMG, 'pole-split.svg'), W, H, *f)


# ── Фігура 5: міллерів місток — звідки беруться обидва зсуви ──────────────────
def fig_miller_bridge():
    W, H = 720, 380
    f = []
    f.append(text(W/2, 26, "Один конденсатор Cc — два протилежні наслідки", size=17, bold=True))

    # два інвертуючі каскади підряд; Cc перекинуто через другий.
    def stage(cx, cy, label, gainlab):
        g = []
        g.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (cx-28, cy-30, cx-28, cy+30, cx+32, cy, FILL, LINE))
        g.append(text(cx-4, cy+5, gainlab, size=13, bold=True))
        g.append(text(cx, cy+50, label, size=11, color=MUTED))
        return g, cx-28, cx+32

    cy = 180
    # вузол A (вхід 2-го каскаду = вихід 1-го), вузол OUT
    g1, _, a_in = stage(170, cy, "1-й каскад", "−gm₁")
    g2, a_node, out_node = stage(420, cy, "2-й каскад", "−gm₂")
    f += g1
    f += g2
    # з'єднання: вихід 1-го → вузол A → вхід 2-го
    f.append(line(a_in, cy, a_node, cy, color=INK, sw=1.8))
    f.append(circle((a_in+a_node)/2, cy, 4, fill=INK, stroke=INK, sw=1))
    nodeAx = (a_in + a_node)/2
    f.append(text(nodeAx, cy - 12, "вузол A (C₁)", size=11, color=NEG, bold=True))
    # вихід 2-го → OUT
    outx = out_node + 70
    f.append(line(out_node, cy, outx, cy, color=INK, sw=1.8))
    f.append(circle(outx, cy, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(outx + 6, cy + 4, "OUT (C₂)", size=11, color=POS, bold=True, anchor="start"))

    # Cc — дуга з OUT назад на вузол A
    ccy = cy - 90
    f.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (outx, cy - 6, (nodeAx+outx)/2, ccy, nodeAx, cy - 6, FIELD))
    # символ конденсатора посередині дуги
    midx = (nodeAx + outx)/2
    f.append(line(midx-3, ccy-12, midx-3, ccy+12, color=FIELD, sw=3))
    f.append(line(midx+5, ccy-12, midx+5, ccy+12, color=FIELD, sw=3))
    f.append(text(midx, ccy - 18, "Cc", size=13, color="#1e7a45", bold=True))

    # ліва виноска: на вході 2-го Cc виглядає у (1+gm2·Rout) разів більшим → p1 ВНИЗ
    f.append(fitbox(40, 250, 300, 70,
                    "На вузлі A:  Cc·(1 + gm₂·Rout)\nефект Міллера роздуває ємність →\nдомінантний полюс p₁ падає ВНИЗ",
                    size=12, fill="#eaf0fd", stroke=NEG, color=NEG))
    # права виноска: на виході Cc підпирає вузол струмом → p2 ВГОРУ
    f.append(fitbox(388, 250, 300, 70,
                    "На вузлі OUT:  Cc подає струм gm₂·v\nу протифазі — вузол «жорсткішає» →\nвихідний полюс p₂ йде ВГОРУ",
                    size=12, fill="#fdecea", stroke=POS, color=POS))

    # вхід
    f.append(line(a_in - 40, cy, a_in, cy, color=INK, sw=1.8))
    f.append(text(a_in - 44, cy + 4, "вхід", size=11, color=MUTED, anchor="end"))

    render(os.path.join(IMG, 'miller-bridge.svg'), W, H, *f)


# ── Фігура 6: декомпенсований проти повністю компенсованого ───────────────────
def fig_decomp_vs_comp():
    W, H = 720, 430
    f = []
    f.append(text(W/2, 26, "Те саме ядро, дві корекції: великий Cc vs малий Cc", size=16, bold=True))

    def panel(ox, label, p1x, p2x, verdict, vfill, vstroke, vcolor):
        g = []
        x0, y0 = ox + 18, 250
        ax_w, ax_h = 250, 170
        g.append(line(x0, y0, x0 + ax_w, y0, color=INK, sw=1.8))
        g.append(line(x0, y0, x0, y0 - ax_h, color=INK, sw=1.8))
        g.append(text(x0 + ax_w, y0 + 18, "частота (log)", size=11, color=MUTED, anchor="end"))
        g.append(text(x0 - 6, y0 - ax_h + 4, "|A|", size=12, color=MUTED, anchor="end"))
        g.append(text(ox + 18 + ax_w/2, 70, label, size=12, bold=True))

        ytop = y0 - ax_h + 16
        zero_y = y0 - 14
        # ідеальна ламана: пласко → −20 до p₂ → −40 далі
        ideal = [(x0, ytop), (p1x, ytop)]
        y_at_p2 = ytop + (p2x - p1x) * 1.0          # нахил −20 (1 px/px)
        ideal.append((p2x, y_at_p2))
        x_right = x0 + ax_w - 4
        ideal.append((x_right, y_at_p2 + (x_right - p2x) * 2.0))   # нахил −40

        # ведемо криву рівно до першого перетину з 0 дБ і там спиняємо
        seg = [ideal[0]]
        fc_x = None
        for (xa, ya), (xb, yb) in zip(ideal, ideal[1:]):
            if fc_x is None and (ya - zero_y) * (yb - zero_y) <= 0 and ya != yb:
                fc_x = xa + (zero_y - ya) * (xb - xa) / (yb - ya)
                seg.append((fc_x, zero_y))
                break
            seg.append((xb, yb))
        g.append(polyline(seg, color=NEG, sw=3))

        g.append(line(x0, zero_y, x0 + ax_w, zero_y, color=MUTED, sw=1.2, dash="5 4"))
        g.append(text(x0 + 4, zero_y - 4, "0 дБ", size=10, color=MUTED, anchor="start"))

        for px, lab in ((p1x, "p₁"), (p2x, "p₂")):
            g.append(line(px, y0, px, y0 - ax_h, color=MUTED, sw=1.0, dash="3 4"))
            g.append(circle(px, y0, 4, fill=POS, stroke=POS, sw=1))
            g.append(text(px, y0 + 16, lab, size=12, color=POS, bold=True))

        if fc_x is not None:
            g.append(circle(fc_x, zero_y, 5, fill=FIELD, stroke=FIELD, sw=1))
        g.append(fitbox(ox + 20, 286, 246, 52, verdict, size=11,
                        fill=vfill, stroke=vstroke, color=vcolor))
        return g

    # компенсований: p₁ далеко вліво, −20 довгий, 0 дБ задовго до p₂
    f += panel(20, "повністю компенсований (Cc великий)",
               p1x=20+18+24, p2x=20+18+200,
               verdict="0 дБ задовго до p₂, нахил −20\n→ стійко аж до ×1, смуга вузька",
               vfill="#eafaf1", vstroke=FIELD, vcolor="#1e7a45")
    # декомпенсований: p₁ ближче, −20 короткий, 0 дБ уже за p₂ на −40
    f += panel(390, "декомпенсований (Cc малий)",
               p1x=390+18+86, p2x=390+18+140,
               verdict="0 дБ аж за p₂ (на −40) → смуга\nв рази ширша, стійко лише ≥ Gmin",
               vfill="#fdecea", vstroke=POS, vcolor=POS)

    render(os.path.join(IMG, 'decomp-vs-comp.svg'), W, H, *f)


# ── Фігура 7: носик шумового підсилення (NG1 → NG2) ───────────────────────────
def fig_noise_gain():
    W, H = 720, 460
    f = []
    f.append(text(W/2, 26, "Носик шумового підсилення: NG1 для сигналу, NG2 для стійкості", size=15, bold=True))

    x0, y0 = 70, 370
    ax_w, ax_h = 580, 300
    f.append(line(x0, y0, x0 + ax_w, y0, color=INK, sw=1.8))
    f.append(line(x0, y0, x0, y0 - ax_h, color=INK, sw=1.8))
    f.append(text(x0 + ax_w, y0 + 20, "частота (log)", size=12, color=MUTED, anchor="end"))
    f.append(text(x0 - 8, y0 - ax_h + 6, "дБ", size=12, color=MUTED, anchor="end"))

    ytop = y0 - ax_h + 24
    p1x = x0 + 55
    p2x = x0 + 360
    y_p2 = ytop + (p2x - p1x) * 0.60
    y_end = min(y_p2 + (x0 + ax_w - p2x) * 1.20, y0 - 8)
    seg = [(x0, ytop), (p1x, ytop), (p2x, y_p2), (x0 + ax_w - 4, y_end)]
    f.append(polyline(seg, color=NEG, sw=3))
    f.append(text(p1x + 8, ytop - 8, "розімкнене |A|", size=12, color=NEG, anchor="start", bold=True))
    f.append(circle(p2x, y_p2, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(p2x + 6, y_p2 - 6, "p₂", size=12, color=POS, anchor="start", bold=True))

    yNG1 = y0 - 50                       # низьке плато (сигнал)
    yNG2 = ytop + 86                      # високе плато (стійкість)
    slopeA = 0.60                        # нахил −20 ділянки |A| (px/px)
    cx = p1x + (yNG2 - ytop) / slopeA    # справжня точка перетину плато NG2 з |A|
    xstep = cx - 70                      # носик мусить піднятися ДО перетину
    ng = [(x0, yNG1), (xstep, yNG1), (xstep + 24, yNG2), (x0 + ax_w - 4, yNG2)]
    f.append(polyline(ng, color=FIELD, sw=2.6, dash="7 5"))
    f.append(text(x0 + 10, yNG1 + 22, "NG1 = 1 + Rf/Rg (сигнал, низьке)",
                  size=11, color="#1e7a45", anchor="start", bold=True))
    f.append(text(cx + 70, yNG2 - 10, "NG2 = 1 + Cs/Cf ≥ Gmin",
                  size=11, color="#1e7a45", anchor="start", bold=True))

    f.append(circle(cx, yNG2, 6, fill="#eafaf1", stroke="#1e7a45", sw=1.6))
    f.append(text(cx, yNG2 - 14, "перетин на −20 → стійко",
                  size=10, color="#1e7a45", anchor="middle", bold=True))

    ymid = (yNG1 + yNG2) / 2
    f.append(line(xstep + 12, yNG1 + 6, xstep + 12, yNG2 + 6, color=POS, sw=1.2, dash="2 3"))
    f.append(text(xstep - 4, ymid, "носик", size=11, color=POS, anchor="end", bold=True))

    render(os.path.join(IMG, 'noise-gain.svg'), W, H, *f)


if __name__ == "__main__":
    fig_two_poles()
    fig_rate_of_closure()
    fig_cap_load()
    fig_pole_split()
    fig_miller_bridge()
    fig_decomp_vs_comp()
    fig_noise_gain()
    print("figs done")
