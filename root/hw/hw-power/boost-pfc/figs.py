# -*- coding: utf-8 -*-
"""Фігури до статті «Boost у корекції коефіцієнта потужності (PFC)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

COIL = "#b5763a"   # мідь котушки


# ── дрібні символи схеми ─────────────────────────────────────────────────────
def coil(x1, x2, y, color=COIL, sw=2.8):
    n = 4
    step = (x2 - x1) / n
    r = step / 2
    d = "M %.1f %.1f " % (x1, y)
    for i in range(n):
        cx0 = x1 + step * i
        d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (r, 9.0, cx0 + step, y)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def diode(x, y, color=INK, sw=2.0, w=20):
    out = ['<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="none" '
           'stroke="%s" stroke-width="%.1f"/>' % (x, y - 10, x, y + 10, x + w, y, color, sw)]
    out.append(line(x + w, y - 10, x + w, y + 10, color=color, sw=sw + 0.6))
    return "".join(out), x + w


def cap(cx, y_top, y_bot, color=INK, sw=2.0):
    midhi, midlo = (y_top + y_bot) / 2 - 5, (y_top + y_bot) / 2 + 5
    out = [line(cx, y_top, cx, midhi, color=color, sw=sw)]
    out.append(line(cx - 13, midhi, cx + 13, midhi, color=color, sw=sw + 0.6))
    out.append(line(cx - 13, midlo, cx + 13, midlo, color=color, sw=sw + 0.6))
    out.append(line(cx, midlo, cx, y_bot, color=color, sw=sw))
    return "".join(out)


def load(x, y_top, y_bot, color=INK, sw=1.8):
    out = [line(x, y_top, x, y_top + 10, color=color, sw=sw)]
    out.append(rect(x - 10, y_top + 10, 20, 44, fill="none", stroke=color, sw=sw, rx=0))
    out.append(line(x, y_top + 54, x, y_bot, color=color, sw=sw))
    return "".join(out)


def sw_symbol(cx, y_top, y_bot, color=NEG, sw=2.2):
    """Транзистор-ключ як розімкнена планка на вертикальній гілці."""
    ymid = (y_top + y_bot) / 2
    out = [line(cx, y_top, cx, ymid - 12, color=color, sw=sw)]
    out.append(line(cx, ymid - 12, cx + 15, ymid - 1, color=color, sw=sw + 0.4))
    out.append(line(cx, ymid + 12, cx, y_bot, color=color, sw=sw))
    return "".join(out)


def sine_pts(x0, x1, ymid, amp, n=240, rect_wave=False, phase=0.0, cycles=1.0):
    pts = []
    for i in range(n + 1):
        t = i / n
        xx = x0 + t * (x1 - x0)
        s = math.sin(2 * math.pi * cycles * t + phase)
        if rect_wave:
            s = abs(s)
        pts.append("%.1f,%.1f" % (xx, ymid - amp * s))
    return " ".join(pts)


def poly(pts, color, sw=2.6, dash=None, fill="none"):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (pts, fill, color, sw, d))


# ── Фіг.1 — пастка vs корекція: піки проти синусоїдного струму ───────────────
def fig_problem_fix():
    W, H = 940, 470
    f = [text(W / 2, 30, "Що робить PFC: замість піків — струм у формі синусоїди", size=17, bold=True)]

    def panel(x0, title_txt, tcolor, good):
        out = [rect(x0, 60, 410, 330, fill="none", stroke="#d8dde3", sw=2, rx=10)]
        out.append(text(x0 + 205, 84, title_txt, size=13, color=tcolor, bold=True))
        gx0, gx1 = x0 + 40, x0 + 385
        ymid = 235
        out.append(line(gx0, ymid, gx1, ymid, color="#cfcfcf", sw=1.2))
        # напруга мережі — синій, дві півхвилі випрямленої (огинальна)
        vpts = sine_pts(gx0, gx1, ymid, 78, rect_wave=True, cycles=2.0)
        out.append(poly(vpts, NEG, sw=2.0, dash="5,4"))
        out.append(text(gx1 - 4, 128, "|Vмережі|", size=10.5, color=NEG, anchor="end"))
        if good:
            # струм повторює огинальну — помаранчевий
            ipts = sine_pts(gx0, gx1, ymid, 60, rect_wave=True, cycles=2.0)
            out.append(poly(ipts, "#e8820c", sw=3.0))
            out.append(text(x0 + 205, 300, "струм тягнеться слідом за напругою", size=11, color="#b5660a"))
            out.append(text(x0 + 205, 320, "PF ≈ 0.99 · гармоніки малі", size=12, color=FIELD, bold=True))
        else:
            # вузькі піки на вершинах — помаранчевий
            for c in (0.5, 1.5):
                cxp = gx0 + (c / 2.0) * (gx1 - gx0)
                out.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                           'fill="none" stroke="#e8820c" stroke-width="3.0" stroke-linejoin="round"/>'
                           % (cxp - 16, ymid, cxp - 6, ymid - 96, cxp, ymid - 108,
                              cxp + 6, ymid - 96, cxp + 16, ymid))
            out.append(text(x0 + 205, 300, "струм — вузькі високі піки на вершинах", size=11, color="#b5660a"))
            out.append(text(x0 + 205, 320, "PF ≈ 0.5–0.65 · багато гармонік", size=12, color=POS, bold=True))
        return "".join(out)

    f.append(panel(20, "БЕЗ КОРЕКЦІЇ: випрямляч + конденсатор", POS, False))
    f.append(panel(510, "З PFC: вхідний струм — синусоїда", FIELD, True))
    f.append(fitbox(70, 410, 800, 44,
                    ["Мета PFC — примусити вхідний струм ПОВТОРЮВАТИ форму й фазу напруги мережі: тоді PF ≈ 1, а гармоніки нижче норм.",
                     "Це не косинус-компенсація конденсатором — тут лікують саму ФОРМУ струму, а не зсув фаз."],
                    size=11.5, fill="#eef8ef", stroke=FIELD))
    render(os.path.join(IMG, "problem-fix.svg"), W, H, *f)


# ── Фіг.2 — силовий каскад boost-PFC із контуром струму ─────────────────────
def fig_stage():
    W, H = 960, 500
    f = [text(W / 2, 28, "Каскад boost-PFC: міст → boost, а контролер веде струм за формою напруги", size=16, bold=True)]
    out = []
    ytop, ygnd = 150, 330

    # мережа + міст (блок)
    out.append(text(70, 120, "~ мережа", size=12, bold=True))
    out.append(rect(40, 132, 64, 66, fill="#f6f9fc", stroke=INK, sw=1.8, rx=6))
    out.append(text(72, 162, "діод.", size=11))
    out.append(text(72, 178, "міст", size=11))
    # шина після мосту: |Vмережі| огинальна
    out.append(line(104, ytop, 150, ytop, color=INK, sw=2))
    out.append(line(104, ygnd, 150, ygnd, color=INK, sw=2))
    out.append(line(104, 165, 104, ytop, color=INK, sw=2))
    out.append(line(104, 180, 104, ygnd, color=INK, sw=2))
    out.append(text(150, 138, "|Vмережі| (0…375 В)", size=10.5, color=MUTED, anchor="start"))

    # котушка
    out.append(coil(158, 258, ytop))
    out.append(text(208, 133, "L", size=12, color=COIL, bold=True, anchor="middle"))
    node_sw = 300
    out.append(line(258, ytop, node_sw, ytop, color=INK, sw=2))
    out.append(circle(node_sw, ytop, 3.5, fill=INK, stroke=INK, sw=0))

    # ключ униз
    out.append(sw_symbol(node_sw, ytop, ygnd))
    out.append(text(node_sw - 14, 250, "ключ", size=11, color=NEG, anchor="end", bold=True))
    out.append(circle(node_sw, ygnd, 3.5, fill=INK, stroke=INK, sw=0))

    # діод у вихід
    out.append(line(node_sw, ytop, 336, ytop, color=INK, sw=2))
    dfrag, dend = diode(336, ytop, color=INK)
    out.append(dfrag)
    out.append(text(347, 133, "D", size=12, bold=True))
    node_out = 430
    out.append(line(dend, ytop, node_out, ytop, color=INK, sw=2))
    out.append(circle(node_out, ytop, 3.5, fill=INK, stroke=INK, sw=0))

    # бульк-конденсатор і навантаження
    out.append(cap(node_out, ytop, ygnd))
    out.append(text(node_out - 18, 245, "C_шини", size=10.5, color=MUTED, anchor="end"))
    out.append(line(node_out, ytop, 500, ytop, color=INK, sw=2))
    out.append(load(500, ytop, ygnd))
    out.append(text(502, 142, "≈ 400 В=", size=12, color=POS, anchor="start", bold=True))
    out.append(text(502, 320, "далі DC-DC", size=10, color=MUTED, anchor="start"))
    out.append(line(104, ygnd, 500, ygnd, color=INK, sw=2))

    # ── контролер (блок під схемою) ──
    cx0, cy0 = 150, 400
    out.append(rect(cx0, cy0, 360, 74, fill="#eef2fb", stroke=NEG, sw=1.8, rx=10))
    out.append(text(cx0 + 180, cy0 + 20, "КОНТРОЛЕР", size=12, color=NEG, bold=True))
    out.append(text(cx0 + 180, cy0 + 40,
                    "еталон струму = (форма |Vмережі|) × (похибка Vшини)", size=11))
    out.append(text(cx0 + 180, cy0 + 58,
                    "жене iL слідом за еталоном, керуючи шпаруватістю", size=10.5, color=MUTED))
    # сигнальні лінії: вимір струму, вимір напруги, привід затвора
    out.append(line(node_sw, ygnd + 4, node_sw, cy0, color=NEG, sw=1.4, dash="4,3"))
    out.append(text(node_sw + 4, 372, "iL", size=10, color=NEG, anchor="start"))
    out.append(line(cx0, cy0 + 20, 128, cy0 + 20, color=NEG, sw=1.4, dash="4,3"))
    out.append(line(128, cy0 + 20, 128, 200, color=NEG, sw=1.4, dash="4,3"))
    out.append(line(128, 200, 150, 200, color=NEG, sw=1.4, dash="4,3"))
    out.append(text(120, 214, "форма |Vмережі|", size=9.5, color=NEG, anchor="end"))
    out.append(line(node_out, ygnd - 0, node_out, 366, color=NEG, sw=1.4, dash="4,3"))
    out.append(line(node_out, 366, cx0 + 360, 366, color=NEG, sw=1.4, dash="4,3"))
    out.append(line(cx0 + 360, 366, cx0 + 360, cy0, color=NEG, sw=1.4, dash="4,3"))
    out.append(text(node_out + 4, 360, "Vшини", size=9.5, color=NEG, anchor="start"))
    # привід на затвор
    out.append(line(node_sw + 15, 268, node_sw + 15, 300, color="#e8820c", sw=1.6))
    out.append(text(node_sw + 20, 288, "привід", size=9.5, color="#b5660a", anchor="start"))

    out.append(fitbox(560, 150, 372, 180,
                      ["Чому саме boost:",
                       "• котушка стоїть на ВХОДІ →",
                       "   вхідний струм безперервний,",
                       "   його легко тримати синусоїдним;",
                       "• шина 400 В вища за пік мережі",
                       "   (~375 В), а boost тільки й уміє,",
                       "   що ПІДВИЩУВАТИ — це якраз те;",
                       "• buck не дотягне до 400 В,",
                       "   buck-boost рве вхідний струм",
                       "   і напружує ключ на Vвх+Vвих."],
                      size=11.5, fill="#f6f9fc", stroke=INK))
    f.extend(out)
    render(os.path.join(IMG, "stage.svg"), W, H, *f)


# ── Фіг.3 — чому не buck: огинальна мережі проти шини ────────────────────────
def fig_why_boost():
    W, H = 900, 430
    f = [text(W / 2, 30, "Boost — єдиний, хто дотягує: шина стоїть ВИЩЕ піка мережі", size=16, bold=True)]
    out = []
    ox, oy, rx, ty = 90, 330, 720, 80
    out.append(arrow(ox, oy, ox, ty, color=INK))
    out.append(arrow(ox, oy, rx + 20, oy, color=INK))
    out.append(text(ox - 8, ty + 6, "В", size=12, anchor="end", bold=True))
    out.append(text(rx + 24, oy + 4, "час", size=11, anchor="start"))

    vmax = 420.0
    def Y(v):
        return oy - v / vmax * (oy - ty)

    for v in (100, 200, 300, 400):
        yy = Y(v)
        out.append(line(ox, yy, rx, yy, color="#ececec", sw=1))
        out.append(text(ox - 8, yy + 4, "%d" % v, size=10, color=MUTED, anchor="end"))

    # огинальна |Vмережі|, пік 375 (265 В rms · √2)
    peak = 375.0
    pts = []
    n = 300
    for i in range(n + 1):
        t = i / n
        xx = ox + t * (rx - ox)
        s = abs(math.sin(2 * math.pi * 2.0 * t))
        pts.append("%.1f,%.1f" % (xx, Y(peak * s)))
    out.append(poly(" ".join(pts), NEG, sw=2.6))
    out.append(text(ox + 120, Y(peak) - 8, "|Vмережі|, пік ≈ 375 В", size=11.5, color=NEG, bold=True))

    # шина 400 В
    out.append(line(ox, Y(400), rx, Y(400), color=POS, sw=3))
    out.append(text(rx - 4, Y(400) - 8, "шина ≈ 400 В (стала)", size=12, color=POS, anchor="end", bold=True))

    # стрілки-«підняти» від огинальної до шини у кількох точках
    for c in (0.25, 0.75, 1.25, 1.75):
        xx = ox + (c / 2.0) * (rx - ox)
        vv = peak * abs(math.sin(2 * math.pi * 2.0 * (c / 2.0)))
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                   'stroke-width="1.6" marker-end="url(#arrow)" stroke-dasharray="3,3"/>'
                   % (xx, Y(vv), xx, Y(400) + 4, FIELD))

    out.append(fitbox(70, 372, 760, 44,
                      ["Миттєва |Vмережі| гуляє від 0 до ~375 В, а шину тримають сталою на ~400 В — вище за миттєвий вхід.",
                       "Підняти напругу вміє лише boost; buck принципово знижує, тож для першого каскаду PFC не годиться."],
                      size=11, fill="#eef8ef", stroke=FIELD))
    f.extend(out)
    render(os.path.join(IMG, "why-boost.svg"), W, H, *f)


# ── Фіг.4 — пульсація 2× частоти й повільний контур напруги ─────────────────
def fig_ripple():
    W, H = 940, 460
    f = [text(W / 2, 30, "Потужність входу пульсує на подвоєній частоті — шина «дихає»", size=16, bold=True)]
    out = []
    x0, x1 = 90, 720

    # верх: миттєва потужність p(t) = синус² → пульсує 2× частоти
    ymid1 = 130
    out.append(text(x0 - 14, 95, "p_вх(t)", size=11, anchor="end", bold=True))
    base1 = 175
    out.append(line(x0, base1, x1, base1, color="#cfcfcf", sw=1.2))
    pts = []
    n = 300
    for i in range(n + 1):
        t = i / n
        xx = x0 + t * (x1 - x0)
        s = math.sin(2 * math.pi * 2.0 * t) ** 2   # sin² — дві горби на період мережі
        pts.append("%.1f,%.1f" % (xx, base1 - 78 * s))
    out.append(poly(" ".join(pts), "#e8820c", sw=2.6))
    # середня лінія (стала віддавана потужність)
    out.append(line(x0, base1 - 39, x1, base1 - 39, color=FIELD, sw=2.0, dash="6,4"))
    out.append(text(x1 + 6, base1 - 39, "середнє = P_вих", size=10.5, color=FIELD, anchor="start", bold=True))
    out.append(text(x1 + 6, base1 - 76, "p_вх ~ sin²", size=10.5, color="#b5660a", anchor="start"))
    out.append(text(x1 + 6, base1 - 62, "(двічі за період)", size=9.5, color=MUTED, anchor="start"))

    # низ: напруга шини — маленька пульсація 100/120 Гц навколо 400 В
    base2 = 330
    out.append(text(x0 - 14, base2 - 30, "Vшини", size=11, anchor="end", bold=True))
    out.append(line(x0, base2, x1, base2, color="#cfcfcf", sw=1.2))
    out.append(line(x0, base2 - 30, x1, base2 - 30, color="#d0d0d0", sw=1, dash="3,3"))
    pts2 = []
    for i in range(n + 1):
        t = i / n
        xx = x0 + t * (x1 - x0)
        # пульсація зсунута по фазі відносно потужності (інтеграл)
        s = math.cos(2 * math.pi * 2.0 * t)
        pts2.append("%.1f,%.1f" % (xx, base2 - 30 - 16 * s))
    out.append(poly(" ".join(pts2), POS, sw=2.6))
    out.append(text(x1 + 6, base2 - 30, "≈ 400 В", size=10.5, color=POS, anchor="start", bold=True))
    out.append(text(x1 + 6, base2 - 14, "пульс. 100/120 Гц", size=9.5, color=MUTED, anchor="start"))

    out.append(text((x0 + x1) / 2, base2 + 34,
                    "Різницю «горб потужності мінус середнє» ковтає C_шини — тому й потрібен великий бульк-конденсатор",
                    size=11))
    out.append(fitbox(70, 400, 800, 44,
                      ["Контур НАПРУГИ мусить бути ПОВІЛЬНИЙ (смуга ~10–20 Гц): якби він швидко «виправляв» цю 100/120-Гц пульсацію,",
                       "то спотворив би сам еталон струму й зіпсував PF. Тож напругу тримає повільна петля, а форму струму — швидка."],
                      size=11.5, fill="#fbe9e7", stroke=POS))
    f.extend(out)
    render(os.path.join(IMG, "ripple.svg"), W, H, *f)


# ── Фіг.5 — нутрощі PFC-контролера: два входи виміру, помножувач, дві петлі ──
def fig_controller_block():
    W, H = 960, 520
    f = [text(W / 2, 30, "Нутрощі PFC-контролера: два виміри → помножувач → дві петлі → драйвер",
              size=15.5, bold=True)]
    out = []

    def blk(x, y, w, h, title_lines, fill="#eef2fb", stroke=NEG, ts=11.5):
        o = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8)]
        lines = title_lines if isinstance(title_lines, list) else [title_lines]
        cy = y + h / 2 - (len(lines) - 1) * (ts + 2) / 2 + ts * 0.35
        for i, ln in enumerate(lines):
            o.append(text(x + w / 2, cy + i * (ts + 2), ln, size=ts, color=INK))
        return "".join(o)

    # ── три входи ліворуч ──
    xin = 40
    out.append(text(xin, 92, "ВХОДИ", size=11, color=MUTED, anchor="start", bold=True))
    out.append(blk(xin, 108, 150, 42, ["форма |Vмережі|", "(після мосту)"], fill="#eafaf0", stroke=FIELD))
    out.append(blk(xin, 232, 150, 42, ["струм котушки iL", "(шунт / трансф.)"], fill="#fff3e6", stroke="#b5660a"))
    out.append(blk(xin, 360, 150, 42, ["Vшини", "(дільник з виходу)"], fill="#fdecea", stroke=POS))

    # ── помножувач/дільник ──
    mx, my, mw, mh = 300, 118, 150, 108
    out.append(rect(mx, my, mw, mh, fill="#eef2fb", stroke=NEG, sw=2, rx=10))
    out.append(text(mx + mw / 2, my + 22, "ПОМНОЖУВАЧ", size=12, color=NEG, bold=True))
    out.append(text(mx + mw / 2, my + 44, "× ÷", size=18, color=NEG, bold=True))
    out.append(text(mx + mw / 2, my + 68, "форма × похибка", size=10, color=INK))
    out.append(text(mx + mw / 2, my + 84, "÷ Vмережі²", size=10, color=MUTED))
    out.append(text(mx + mw / 2, my + 100, "= еталон iL", size=10.5, color=FIELD, bold=True))

    # ── повільний контур напруги (згори до помножувача) ──
    vex, vey, vew, veh = 300, 360, 150, 44
    out.append(blk(vex, vey, vew, veh, ["похибка напруги", "ПОВІЛЬНА (десятки Гц)"],
                   fill="#fdecea", stroke=POS, ts=10.5))

    # ── струмова петля (швидка) ──
    cex, cey, cew, ceh = 540, 226, 168, 60
    out.append(rect(cex, cey, cew, ceh, fill="#fff3e6", stroke="#b5660a", sw=2, rx=10))
    out.append(text(cex + cew / 2, cey + 22, "СТРУМОВА ПЕТЛЯ", size=11.5, color="#b5660a", bold=True))
    out.append(text(cex + cew / 2, cey + 40, "iL слідом за еталоном", size=10, color=INK))
    out.append(text(cex + cew / 2, cey + 54, "ШВИДКА (кожен такт)", size=10, color=MUTED))

    # ── ШІМ-компаратор + драйвер ──
    px, py, pw, ph = 748, 226, 92, 60
    out.append(blk(px, py, pw, ph, ["ШІМ", "компар."], fill="#f6f9fc", stroke=INK, ts=11))
    dx, dy, dw, dh = 748, 118, 92, 60
    out.append(blk(dx, dy, dw, dh, ["ДРАЙВЕР", "затвора"], fill="#eef2fb", stroke=NEG, ts=11))
    out.append(text(dx + dw / 2, dy - 12, "→ на ключ", size=11, color="#b5660a", bold=True))

    # ── стрілки сигналів ──
    def a(x1, y1, x2, y2, color=INK, sw=1.8):
        out.append(arrow(x1, y1, x2, y2, color=color, sw=sw))

    a(190, 129, mx, 150, FIELD)            # форма → помножувач
    a(190, 253, cex, 246, "#b5660a")       # струм → струмова петля
    a(190, 381, vex, 382, POS)             # Vшини → похибка напруги
    a(vex + vew / 2, vey, mx + mw / 2, my + mh, POS)   # похибка → помножувач (знизу)
    a(mx + mw, 172, cex, 250, NEG)         # еталон iL → струмова петля
    a(cex + cew, cey + ceh / 2, px, py + ph / 2, "#b5660a")  # петля → ШІМ
    a(px + pw / 2, py, dx + dw / 2, dy + dh)                 # ШІМ → драйвер

    # м'який старт (окремим блоком під драйвером)
    ssx, ssy, ssw, ssh = 620, 118, 110, 44
    out.append(blk(ssx, ssy, ssw, ssh, ["м'який старт /", "обмеж. пуску"], fill="#eafaf0", stroke=FIELD, ts=10))
    a(ssx + ssw, ssy + ssh / 2, dx, dy + 20, FIELD)

    out.append(fitbox(70, 430, 820, 66,
                      ["Форма напруги задає струму ОБРИС синусоїди, похибка шини — МАСШТАБ; помножувач зводить їх в еталон струму.",
                       "Швидка струмова петля жене iL за еталоном кожен такт; повільна напругова лише неквапно рухає масштаб — інакше зіпсує PF.",
                       "Поділ на Vмережі² тримає підсилення петлі сталим, коли мережа гуляє 85–265 В; м'який старт стримує пусковий кидок."],
                      size=11, fill="#eef2fb", stroke=NEG))
    f.extend(out)
    render(os.path.join(IMG, "controller-block.svg"), W, H, *f)


# ── Фіг.6 — CrM проти CCM: форма струму котушки за такт ──────────────────────
def fig_crm_vs_ccm():
    W, H = 960, 470
    f = [text(W / 2, 30, "Дві родини керування: межа провідності (CrM) проти неперервного (CCM)",
              size=15.5, bold=True)]

    def panel(x0, title_txt, tcolor, mode):
        out = [rect(x0, 58, 420, 300, fill="none", stroke="#d8dde3", sw=2, rx=10)]
        out.append(text(x0 + 210, 82, title_txt, size=12.5, color=tcolor, bold=True))
        gx0, gx1 = x0 + 40, x0 + 400
        base = 300           # нульова лінія струму
        top = 120
        out.append(line(gx0, base, gx1, base, color="#cfcfcf", sw=1.3))
        out.append(text(gx0 - 6, base + 4, "0", size=10, color=MUTED, anchor="end"))
        out.append(text(gx0 - 6, base - 4, "iL", size=10.5, color=INK, anchor="end", bold=True))

        # огинальна середнього струму (пів-синус) — спільна пунктирна для обох
        env = []
        n = 200
        for i in range(n + 1):
            t = i / n
            xx = gx0 + t * (gx1 - gx0)
            s = math.sin(math.pi * t)          # один горб — чверть періоду мережі
            env.append("%.1f,%.1f" % (xx, base - (base - top) * 0.5 * s))
        out.append(poly(" ".join(env), FIELD, sw=2.0, dash="6,4"))
        out.append(text(gx1 - 4, top + 10, "середнє ~ |Vмережі|", size=10, color=FIELD, anchor="end", bold=True))

        # пилка струму: багато трикутників/трапецій під огинальною
        ncy = 13
        col = "#e8820c"
        for k in range(ncy):
            tc = (k + 0.5) / ncy
            xc = gx0 + tc * (gx1 - gx0)
            wtri = (gx1 - gx0) / ncy * 0.92
            avg = (base - top) * 0.5 * math.sin(math.pi * tc)   # висота середнього тут
            if mode == "crm":
                # трикутник від нуля до 2×середнього (пік = 2× avg)
                pk = 2 * avg
                out.append(poly("%.1f,%.1f %.1f,%.1f %.1f,%.1f"
                                % (xc - wtri / 2, base, xc, base - pk, xc + wtri / 2, base),
                                col, sw=1.7))
            else:
                # трапеція: невелика пульсація навколо середнього (не торкається нуля)
                ripp = (base - top) * 0.09
                lo = base - (avg - ripp / 2)
                hi = base - (avg + ripp / 2)
                out.append(poly("%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f"
                                % (xc - wtri / 2, lo, xc - wtri / 6, hi,
                                   xc + wtri / 6, hi, xc + wtri / 2, lo),
                                col, sw=1.7))

        if mode == "crm":
            out.append(text(x0 + 210, base + 26, "пік = 2 × середнє · струм торкається нуля щотакту",
                            size=10, color="#b5660a"))
            out.append(text(x0 + 210, base + 44, "частота ГУЛЯЄ · високі пік/RMS · просто й дешево",
                            size=10.5, color=POS, bold=True))
        else:
            out.append(text(x0 + 210, base + 26, "лише мала пульсація навколо середнього",
                            size=10, color="#b5660a"))
            out.append(text(x0 + 210, base + 44, "частота СТАЛА · низькі пік/RMS · треба вести струм",
                            size=10.5, color=FIELD, bold=True))
        return "".join(out)

    f.append(panel(20, "CrM / BCM — на межі провідності", POS, "crm"))
    f.append(panel(510, "CCM — неперервний струм", FIELD, "ccm"))
    f.append(fitbox(70, 396, 820, 58,
                    ["CrM: кожен такт стартує, щойно струм спав до нуля; середнє саме лягає на синусоїду — контролер простий, окремо мірити струм не конче.",
                     "Але трикутник удвічі вищий за своє середнє (пік = 2× avg), тож пікові й діючі струми високі, а частота гуляє в такт мережі — важче фільтрувати завади.",
                     "CCM: струм лише злегка колишеться, пік/RMS низькі, частота стала — але середнє САМО на синусоїду не ляже, тож потрібна активна струмова петля."],
                    size=10.5, fill="#eef8ef", stroke=FIELD))
    render(os.path.join(IMG, "crm-vs-ccm.svg"), W, H, *f)


# ── Фіг.7 (вставка math) — розклад sin² на сталу + косинус 2ω ────────────────
def fig_power_decomp():
    W, H = 940, 470
    f = [text(W / 2, 30, "Миттєва потужність p = V·I·sin² = стала + хвиля на 2ω", size=16, bold=True)]
    out = []
    x0, x1 = 90, 720
    n = 300

    def curve(base, amp, fn, color, sw=2.6, dash=None):
        pts = []
        for i in range(n + 1):
            t = i / n
            xx = x0 + t * (x1 - x0)
            pts.append("%.1f,%.1f" % (xx, base - amp * fn(t)))
        return poly(" ".join(pts), color, sw=sw, dash=dash)

    # верх: p(t) = sin² (жовтогаряча), пік 2A, середнє A
    b1 = 150
    A = 70.0
    out.append(text(x0 - 14, b1 - 2 * A + 40, "p(t)", size=11, anchor="end", bold=True))
    out.append(line(x0, b1, x1, b1, color="#cfcfcf", sw=1.2))  # нуль
    out.append(curve(b1, 2 * A, lambda t: math.sin(2 * math.pi * 2.0 * t) ** 2, "#e8820c", sw=2.8))
    out.append(line(x0, b1 - A, x1, b1 - A, color=FIELD, sw=2.0, dash="6,4"))  # середнє
    out.append(text(x1 + 6, b1 - A, "P_сер", size=10.5, color=FIELD, anchor="start", bold=True))
    out.append(text(x1 + 6, b1 - 2 * A + 6, "p = sin²", size=10, color="#b5660a", anchor="start"))
    out.append(text(x1 + 6, b1 - 2 * A + 20, "(2 горби)", size=9, color=MUTED, anchor="start"))

    out.append(text((x0 + x1) / 2, 232, "=", size=22, bold=True))

    # низ: сталий рівень P_сер + мінус косинус 2ω навколо нуля
    b2 = 360
    out.append(text(x0 - 14, b2 - A - 4, "P_сер", size=10.5, anchor="end", color=FIELD, bold=True))
    out.append(text(x0 - 14, b2 + 4, "0", size=10.5, anchor="end", color=MUTED))
    out.append(line(x0, b2, x1, b2, color="#cfcfcf", sw=1.2))  # нуль
    out.append(line(x0, b2 - A, x1, b2 - A, color=FIELD, sw=2.4, dash="6,4"))  # стала
    out.append(text(x1 + 6, b2 - A, "стала = P_сер", size=10, color=FIELD, anchor="start", bold=True))
    out.append(curve(b2, A, lambda t: -math.cos(2 * math.pi * 2.0 * t), NEG, sw=2.6))
    out.append(text(x1 + 6, b2 + 4, "−P_сер·cos2ωt", size=10, color=NEG, anchor="start", bold=True))
    out.append(text(x1 + 6, b2 + 18, "(на 2ω → конденсатор)", size=9, color=MUTED, anchor="start"))

    out.append(fitbox(70, 408, 800, 46,
                      ["sin²(ωt) = ½·(1 − cos2ωt): миттєва потужність = СТАЛИЙ рівень P_сер (його бере навантаження, = V_rms·I_rms)",
                       "ПЛЮС косинус на ПОДВОЄНІЙ частоті амплітудою P_сер — цю пульсацію поперемінно ковтає й віддає конденсатор шини."],
                      size=11.5, fill="#eef8ef", stroke=FIELD))
    f.extend(out)
    render(os.path.join(IMG, "power-decomp.svg"), W, H, *f)


# ── Фіг.8 (вставка math) — розмах пульсації шини vs ємність ──────────────────
def fig_ripple_vs_c():
    W, H = 940, 440
    f = [text(W / 2, 30, "Розмах пульсації шини ΔV = P/(ω·C·V): більший C — вужче «дихання»", size=15.5, bold=True)]
    out = []
    x0, x1 = 90, 700
    mid = 250          # рівень ~400 В
    n = 300
    out.append(line(x0, mid, x1, mid, color="#d0d0d0", sw=1.2, dash="4,4"))
    out.append(text(x0 - 12, mid + 4, "400 В", size=10.5, anchor="end", color=MUTED))

    def ripple(amp, color, sw=2.6):
        pts = []
        for i in range(n + 1):
            t = i / n
            xx = x0 + t * (x1 - x0)
            s = math.sin(2 * math.pi * 2.0 * t)
            pts.append("%.1f,%.1f" % (xx, mid - amp * s))
        return poly(" ".join(pts), color, sw=sw)

    out.append(ripple(70, "#e8820c"))     # мала C → велика пульсація
    out.append(ripple(40, POS))           # середня C
    out.append(ripple(22, NEG))           # велика C → мала пульсація

    out.append(text(x1 + 8, mid - 70, "C мала → ΔV велика", size=10.5, color="#b5660a", anchor="start", bold=True))
    out.append(text(x1 + 8, mid - 40, "C середня", size=10.5, color=POS, anchor="start", bold=True))
    out.append(text(x1 + 8, mid - 20, "C велика → ΔV мала", size=10.5, color=NEG, anchor="start", bold=True))

    # двобічна стрілка розмаху для найбільшої пульсації, на вершині синуса (чверть періоду)
    xa = x0 + 0.125 * (x1 - x0)
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" '
               'marker-start="url(#arrow)" marker-end="url(#arrow)"/>' % (xa, mid - 70, xa, mid + 70, INK))
    out.append(text(xa - 8, mid, "ΔV", size=11, anchor="end", bold=True))

    out.append(fitbox(70, 372, 780, 46,
                      ["ΔV (розмах) = P_вих/(ω·C·V_шини): обернено пропорційний ємності — подвоїш C, удвічі менша пульсація.",
                       "Завжди на подвоєній частоті мережі й зсунута на чверть періоду відносно пульсації потужності (напруга — інтеграл струму)."],
                      size=11.5, fill="#eef8ef", stroke=FIELD))
    f.extend(out)
    render(os.path.join(IMG, "ripple-vs-c.svg"), W, H, *f)


if __name__ == "__main__":
    fig_problem_fix()
    fig_stage()
    fig_why_boost()
    fig_ripple()
    fig_controller_block()
    fig_crm_vs_ccm()
    fig_power_decomp()
    fig_ripple_vs_c()
    print("OK: 8 фігур у", IMG)
