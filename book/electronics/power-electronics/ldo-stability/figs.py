# -*- coding: utf-8 -*-
"""Фігури для теми ldo-stability (стійкість LDO: полюси, ESR, компенсація).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5).
Підписи фігур живуть у Markdown, не в SVG — тут лише сама графіка."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8860b"   # проміжне / «на межі»


def fig_two_poles():
    """Механізм: дві полюси (вихід + підсилювач похибки) тягнуть фазу до −180°;
    нуль ESR, поставлений нижче зрізу, підіймає фазу назад → здоровий запас."""
    W, H = 900, 520
    xL, xR = 95, 840
    span = xR - xL
    # позиції особливостей уздовж осі частот (частка ширини)
    x_pout = xL + 0.16 * span
    x_pea  = xL + 0.40 * span
    x_fz   = xL + 0.585 * span
    x_fc   = xL + 0.66 * span
    frags = []

    # ── верхня смужка: підсилення петлі, зріз на 0 дБ ──
    gt, gb = 54, 118
    frags.append(text(xL - 6, gt + 4, "|A|", size=12, color=MUTED, anchor="end", bold=True))
    frags.append(line(xL, gb, xR, gb, color=MUTED, sw=1.2, dash="5,4"))
    frags.append(text(xR + 4, gb + 4, "0 дБ", size=11, color=MUTED, anchor="start"))
    # ламана підсилення: рівне → після p_out нахил → після p_ea крутіше → нуль ESR полегшує
    gpts = [(xL, gt + 4), (x_pout, gt + 8), (x_pea, gt + 30),
            (x_fz, gb - 4), (x_fc, gb + 2), (xR, gb + 20)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
                 'stroke-linejoin="round"/>'
                 % (" ".join("%.1f,%.1f" % p for p in gpts), INK))
    frags.append(circle(x_fc, gb, 4, fill=BG, stroke=INK, sw=2))
    frags.append(text(x_fc, gt + 2, "зріз", size=11, color=INK, bold=True))

    # ── фазова панель ──
    ptop, pbot = 176, 392            # 0° … −180°
    def yph(deg):                    # градуси (−) → піксель
        return ptop + (-deg / 180.0) * (pbot - ptop)
    frags.append(text(xL - 6, ptop + 4, "фаза", size=12, color=MUTED, anchor="end", bold=True))
    for deg, lab in [(0, "0°"), (-90, "−90°"), (-180, "−180° (зрив)")]:
        yy = yph(deg)
        col = POS if deg == -180 else MUTED
        frags.append(line(xL, yy, xR, yy, color=col, sw=1.2, dash="5,4"))
        frags.append(text(xR + 4, yy + 4, lab, size=11, color=col, anchor="start",
                          bold=(deg == -180)))

    # вертикальні маркери особливостей (крізь обидві панелі)
    for xx, col in [(x_pout, INK), (x_pea, INK), (x_fz, FIELD), (x_fc, MUTED)]:
        frags.append(line(xx, gt - 2, xx, pbot, color=col, sw=1.3, dash="3,4"))

    # фаза БЕЗ нуля ESR — валиться до −180° (нестійко)
    red = [(xL + 12, -6), (x_pout, -18), (218, -55), (300, -100), (x_pea, -132),
           (430, -152), (500, -166), (x_fc, -175), (700, -179), (xR, -180)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
                 'stroke-dasharray="7,5" stroke-linejoin="round"/>'
                 % (" ".join("%.1f,%.1f" % (x, yph(d)) for x, d in red), POS))

    # фаза З нулем ESR — нуль підіймає її назад коло зрізу (є запас)
    grn = [(xL + 12, -6), (x_pout, -18), (218, -55), (300, -100), (x_pea, -130),
           (430, -146), (x_fz, -150), (x_fc, -122), (700, -140), (xR, -158)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0" '
                 'stroke-linejoin="round"/>'
                 % (" ".join("%.1f,%.1f" % (x, yph(d)) for x, d in grn), FIELD))

    # позначка запасу фази на зрізі (від −180° до зеленої кривої)
    frags.append(line(x_fc, yph(-180), x_fc, yph(-122), color=FIELD, sw=2.4))
    frags.append(text(x_fc + 8, yph(-150), "запас", size=11, color=FIELD, anchor="start", bold=True))
    frags.append(text(x_fc + 8, yph(-150) + 15, "≈ 58°", size=11, color=FIELD, anchor="start", bold=True))

    # підписи маркерів під панеллю (рознесені, щоб не накладались)
    frags.append(text(x_pout, pbot + 22, "полюс виходу", size=12, color=INK, bold=True))
    frags.append(text(x_pout, pbot + 39, "1/(2π·Rвих·Cвих)", size=10, color=MUTED))
    frags.append(text(x_pea, pbot + 22, "полюс підсил.", size=12, color=INK, bold=True))
    frags.append(text(x_pea, pbot + 39, "похибки", size=10, color=MUTED))
    frags.append(text(x_fz - 30, pbot + 56, "нуль ESR", size=12, color=FIELD, bold=True, anchor="middle"))
    frags.append(text(x_fz - 30, pbot + 73, "1/(2π·ESR·Cвих)", size=10, color=FIELD, anchor="middle"))

    # легенда кривих
    frags.append(line(xR - 250, 150, xR - 218, 150, color=POS, sw=2.6, dash="7,5"))
    frags.append(text(xR - 210, 154, "без нуля ESR → −180° → зрив", size=11, color=POS, anchor="start"))
    frags.append(line(xR - 250, 168, xR - 218, 168, color=FIELD, sw=3))
    frags.append(text(xR - 210, 172, "з нулем ESR → фаза піднята → стійко", size=11, color=FIELD, anchor="start"))

    # вісь частот
    frags.append(arrow(xL, pbot + 92, xR, pbot + 92, color=INK))
    frags.append(text(xR, pbot + 108, "частота (лог)", size=12, color=INK, anchor="end", italic=True))
    render(os.path.join(OUT, "two-poles.svg"), W, H, *frags,
           title="Дві полюси тягнуть фазу вниз — нуль ESR її рятує")


def fig_load_pole():
    """Полюс виходу їде з навантаженням: легке → низька частота, важке → висока
    (Rвих = ro || Rнав спадає зі струмом). Полюс підсилювача майже сталий."""
    W, H = 900, 320
    xL, xR = 90, 840
    axy = 200
    frags = []
    frags.append(line(xL, axy, xR, axy, color=INK, sw=2))
    frags.append(text(xR, axy + 30, "частота (лог)", size=12, color=INK, anchor="end", italic=True))
    frags.append(arrow(xL + 40, axy - 92, xR - 90, axy - 92, color=MUTED))
    frags.append(text((xL + xR) / 2, axy - 100, "росте струм навантаження  →  полюс виходу їде вправо",
                      size=12, color=MUTED, italic=True))

    # три положення полюса виходу
    poles = [(0.14, "легке\n1 мА", "≈ 48 Гц", NEG),
             (0.40, "середнє\n50 мА", "≈ 2.4 кГц", GOLD),
             (0.66, "важке\n0.5 А", "≈ 24 кГц", POS)]
    for frac, load, val, col in poles:
        xx = xL + frac * (xR - xL)
        frags.append(line(xx, axy - 8, xx, axy + 8, color=col, sw=2))
        frags.append(circle(xx, axy, 6, fill=col, stroke=col))
        for i, ln in enumerate(load.split("\n")):
            frags.append(text(xx, axy + 34 + i * 16, ln, size=12, color=col, bold=(i == 0)))
        frags.append(text(xx, axy - 20, val, size=12, color=col, bold=True))

    # полюс підсилювача — майже сталий (правіше)
    xe = xL + 0.80 * (xR - xL)
    frags.append(line(xe, axy - 8, xe, axy + 8, color=FIELD, sw=2))
    frags.append(circle(xe, axy, 6, fill=BG, stroke=FIELD, sw=2))
    frags.append(text(xe, axy - 20, "полюс підсил.", size=12, color=FIELD, bold=True))
    frags.append(text(xe, axy + 34, "майже сталий", size=12, color=FIELD))

    # застереження
    box, bw, bh = textbox((xL + xR) / 2, 288,
                          "Стійкий на одному струмі — може дзвеніти на іншому: перевіряй увесь діапазон навантаження.",
                          size=12, fill="#fdf3e3", stroke=GOLD, bold=True)
    frags.append(box)
    render(os.path.join(OUT, "load-pole.svg"), W, H, *frags,
           title="Полюс виходу LDO їде з навантаженням")


def _esr_x(esr, x0, w):
    """ESR (Ом, лог 1 мОм…10 Ом) → піксель."""
    return x0 + (math.log10(esr) + 3.0) / 4.0 * w


def fig_esr_tunnel():
    """Тунель стійкості: смуга дозволених ESR (вужчає з навантаженням).
    Кераміка з ~0 ESR випадає ліворуч; сучасні ceramic-stable присувають
    ліву стіну до нуля."""
    W, H = 900, 400
    x0, w = 120, 700
    ytop, ybot = 74, 322            # top = важке навантаження, bottom = легке
    frags = []

    # осі
    frags.append(line(x0, ytop, x0, ybot, color=INK, sw=1.8))
    frags.append(line(x0, ybot, x0 + w, ybot, color=INK, sw=1.8))
    frags.append(arrow(x0, ybot, x0, ytop - 8, color=INK))
    frags.append(text(x0 - 12, ytop + 6, "важче", size=11, color=INK, anchor="end", bold=True))
    frags.append(text(x0 - 12, ybot - 2, "легше", size=11, color=INK, anchor="end"))
    frags.append(text(x0 - 40, (ytop + ybot) / 2, "струм", size=12, color=INK, anchor="middle", bold=True))
    for esr, lab in [(0.001, "1 мОм"), (0.01, "10 мОм"), (0.1, "0.1 Ом"),
                     (1.0, "1 Ом"), (10.0, "10 Ом")]:
        xx = _esr_x(esr, x0, w)
        frags.append(line(xx, ybot, xx, ybot + 6, color=INK, sw=1.4))
        frags.append(text(xx, ybot + 20, lab, size=11, color=INK))
    frags.append(text(x0 + w, ybot + 40, "ESR вихідного конденсатора (лог)", size=12,
                      color=INK, anchor="end", italic=True))

    # смуга стійкості (вужчає догори — до важчого навантаження)
    Lb = _esr_x(0.03, x0, w); Rb = _esr_x(3.0, x0, w)   # легке: широко
    Lt = _esr_x(0.12, x0, w); Rt = _esr_x(0.8, x0, w)   # важке: вузько
    band = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (Lb, ybot, Lt, ytop, Rt, ytop, Rb, ybot)
    frags.append('<polygon points="%s" fill="%s" fill-opacity="0.18" stroke="%s" '
                 'stroke-width="2"/>' % (band, FIELD, FIELD))
    frags.append(text((Lt + Rt) / 2, ytop + 40, "СТІЙКО", size=15, color="#1e7d45", bold=True))
    frags.append(text((Lb + Rb) / 2, ybot - 24, "вікно дозволених ESR", size=12, color="#1e7d45"))

    # ліва «нестійка» зона
    frags.append(text((x0 + Lb) / 2, 150, "нестійко:", size=12, color=POS, bold=True))
    frags.append(text((x0 + Lb) / 2, 168, "нуль ESR за зрізом", size=11, color=POS))
    # права «нестійка» зона
    frags.append(text((Rb + x0 + w) / 2 - 6, 150, "дзвін:", size=12, color=POS, bold=True))
    frags.append(text((Rb + x0 + w) / 2 - 6, 168, "зависокий ESR", size=11, color=POS))

    # точка кераміки (випадає ліворуч)
    cx = _esr_x(0.005, x0, w); cy = 250
    frags.append(line(cx - 7, cy - 7, cx + 7, cy + 7, color=POS, sw=2.6))
    frags.append(line(cx - 7, cy + 7, cx + 7, cy - 7, color=POS, sw=2.6))
    frags.append(text(cx, cy - 16, "кераміка", size=12, color=POS, bold=True))
    frags.append(text(cx, cy + 26, "ESR ≈ 5 мОм", size=11, color=POS))

    # точка тантала (в вікні)
    tx = _esr_x(0.5, x0, w); ty = 250
    frags.append(circle(tx, ty, 6, fill=NEG, stroke=NEG))
    frags.append(text(tx, ty - 14, "тантал", size=12, color=NEG, bold=True))
    frags.append(text(tx, ty + 26, "ESR ≈ 0.5 Ом", size=11, color=NEG))

    # присунення лівої стіни до нуля (ceramic-stable / cap-free)
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="2" stroke-dasharray="6,5" marker-end="url(#arrow)"/>'
                 % (Lb, ybot + 0, x0 + 6, ybot + 0, "#1e7d45"))
    frags.append(text(x0 + 8, ybot + 56, "сучасні ceramic-stable / cap-free LDO: внутрішня компенсація присуває ліву стіну до ~0",
                      size=11, color="#1e7d45", anchor="start", bold=True))
    render(os.path.join(OUT, "esr-tunnel.svg"), W, H, *frags,
           title="Тунель стійкості: вікно ESR вихідного конденсатора")


# ══════════════════════════════════════════════════════════════════════════
# Фігури вставки math-ldo-poles.md
# ══════════════════════════════════════════════════════════════════════════

def fig_math_loop_nodes():
    """Звідки беруться полюси: кожен вузол, що заряджає ємність через опір,
    дає рівно один множник 1/(1+s·RC). Вихідний вузол додає ще й нуль ESR."""
    W, H = 980, 500
    ych = 168            # рівень сигнального тракту
    ygnd = 366           # рівень землі
    frags = []

    # ── земляна шина ──
    frags.append(line(96, ygnd, 880, ygnd, color=MUTED, sw=1.8))
    for gx in (300, 700):
        frags.append(line(gx - 13, ygnd + 7, gx + 13, ygnd + 7, color=MUTED, sw=1.6))
        frags.append(line(gx - 8, ygnd + 12, gx + 8, ygnd + 12, color=MUTED, sw=1.6))
        frags.append(line(gx - 3, ygnd + 17, gx + 3, ygnd + 17, color=MUTED, sw=1.6))

    def rbox(cx, cy, lab):
        out = rect(cx - 21, cy - 12, 42, 24, fill=BG, stroke=INK, sw=1.6, rx=3)
        out += text(cx + 30, cy + 4, lab, size=12, color=INK, anchor="start")
        return out

    def cap(cx, cy, lab):
        out = line(cx - 17, cy, cx + 17, cy, color=INK, sw=2.4)
        out += line(cx - 17, cy + 9, cx + 17, cy + 9, color=INK, sw=2.4)
        out += text(cx + 26, cy + 9, lab, size=12, color=INK, anchor="start")
        return out

    # ── каскад 1: підсилювач похибки як джерело струму ──
    frags.append(circle(150, ych, 25, fill=BG, stroke=INK, sw=2))
    frags.append(text(150, ych + 5, "gm", size=13, color=INK, bold=True))
    frags.append(text(150, ych - 44, "підсилювач", size=12, color=INK, bold=True))
    frags.append(text(150, ych - 28, "похибки", size=12, color=INK, bold=True))
    frags.append(arrow(60, ych, 124, ych, color=INK))
    frags.append(text(58, ych - 12, "vзз", size=12, color=MUTED, anchor="start", italic=True))
    frags.append(arrow(176, ych, 300, ych, color=INK))

    # ── ВУЗОЛ A: Rпх ∥ Cз ──
    frags.append(circle(300, ych, 5, fill=INK, stroke=INK))
    frags.append(text(300, ych - 22, "вузол A", size=13, color=NEG, bold=True))
    frags.append(line(300, ych, 300, ych + 34, color=INK, sw=1.6))
    frags.append(line(232, ych + 34, 368, ych + 34, color=INK, sw=1.6))
    frags.append(line(232, ych + 34, 232, ygnd, color=INK, sw=1.6))
    frags.append(line(368, ych + 34, 368, ygnd, color=INK, sw=1.6))
    frags.append(line(232, ygnd, 368, ygnd, color=INK, sw=1.6))
    frags.append(rbox(232, ych + 96, "Rпх"))
    frags.append(cap(368, ych + 92, "Cз"))

    # ── каскад 2: прохідний транзистор як джерело струму ──
    frags.append(arrow(300, ych, 524, ych, color=INK))
    frags.append(circle(550, ych, 25, fill=BG, stroke=INK, sw=2))
    frags.append(text(550, ych + 5, "gmп", size=12, color=INK, bold=True))
    frags.append(text(550, ych - 44, "прохідний", size=12, color=INK, bold=True))
    frags.append(text(550, ych - 28, "транзистор", size=12, color=INK, bold=True))
    frags.append(arrow(576, ych, 700, ych, color=INK))

    # ── ВУЗОЛ ВИХІД: Rвих ∥ (ESR + Cвих) ──
    frags.append(circle(700, ych, 5, fill=INK, stroke=INK))
    frags.append(text(700, ych - 22, "вузол ВИХІД", size=13, color=POS, bold=True))
    frags.append(line(700, ych, 700, ych + 34, color=INK, sw=1.6))
    frags.append(line(632, ych + 34, 768, ych + 34, color=INK, sw=1.6))
    frags.append(line(632, ych + 34, 632, ygnd, color=INK, sw=1.6))
    frags.append(line(768, ych + 34, 768, ygnd, color=INK, sw=1.6))
    frags.append(line(632, ygnd, 768, ygnd, color=INK, sw=1.6))
    frags.append(rbox(632, ych + 96, "Rвих"))
    frags.append(rbox(768, ych + 62, "ESR"))
    frags.append(cap(768, ych + 124, "Cвих"))

    # ── дільник і зворотний шлях ──
    frags.append(arrow(700, ych, 852, ych, color=INK))
    frags.append(text(866, ych + 5, "β", size=14, color=INK, anchor="start", bold=True))
    frags.append(line(880, ych, 924, ych, color=MUTED, sw=1.6))
    frags.append(line(924, ych, 924, 92, color=MUTED, sw=1.6))
    frags.append(line(924, 92, 40, 92, color=MUTED, sw=1.6))
    frags.append('<line x1="40" y1="92" x2="40" y2="%.0f" stroke="%s" stroke-width="1.6" '
                 'marker-end="url(#arrow)"/>' % (ych - 6, MUTED))
    frags.append(text(482, 84, "зворотний шлях через дільник", size=12, color=MUTED, italic=True))

    # ── підписи «що дає цей вузол» ──
    box, bw, bh = textbox(232, 452,
                          "полюс A\nf_p2 = 1/(2π·Rпх·Cз)",
                          size=12, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    frags.append(box)
    box, bw, bh = textbox(700, 452,
                          "полюс виходу  f_p1 = 1/(2π·Rвих·Cвих)\nнуль ESR  f_z = 1/(2π·ESR·Cвих)",
                          size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)
    frags.append(box)
    render(os.path.join(OUT, "math-loop-nodes.svg"), W, H, *frags,
           title="Петля LDO по вузлах: один вузол R∥C — рівно один полюс")


def fig_math_zout():
    """Імпеданс вихідного вузла в лог-лог: полиця Rвих → спад 1/(2πfC) →
    полиця ESR. Полюс і нуль — це два злами, тобто дві точки перетину прямих."""
    W, H = 980, 520
    x0, x1 = 120, 830
    ytop, ybot = 96, 388
    fmin_d, fdec = 1.0, 7.0        # 10¹ Гц … 10⁸ Гц
    zmin_d, zdec = -3.0, 7.0       # 10⁻³ Ом … 10⁴ Ом
    frags = []

    def X(f):
        return x0 + (math.log10(f) - fmin_d) / fdec * (x1 - x0)

    def Y(z):
        return ybot - (math.log10(z) - zmin_d) / zdec * (ybot - ytop)

    # осі з засічками (без сітки — щоб жодна лінія не різала написів)
    frags.append(line(x0, ytop, x0, ybot, color=INK, sw=1.8))
    frags.append(line(x0, ybot, x1, ybot, color=INK, sw=1.8))
    for f, lab in [(1e1, "10 Гц"), (1e2, "100 Гц"), (1e3, "1 кГц"), (1e4, "10 кГц"),
                   (1e5, "100 кГц"), (1e6, "1 МГц"), (1e7, "10 МГц"), (1e8, "100 МГц")]:
        frags.append(line(X(f), ybot, X(f), ybot + 6, color=INK, sw=1.3))
        frags.append(text(X(f), ybot + 22, lab, size=11, color=MUTED))
    for z, lab in [(1e-3, "1 мОм"), (1e-2, "10 мОм"), (1e-1, "0.1 Ом"), (1e0, "1 Ом"),
                   (1e1, "10 Ом"), (1e2, "100 Ом"), (1e3, "1 кОм"), (1e4, "10 кОм")]:
        frags.append(line(x0 - 6, Y(z), x0, Y(z), color=INK, sw=1.3))
        frags.append(text(x0 - 12, Y(z) + 4, lab, size=11, color=MUTED, anchor="end"))
    frags.append(text(x1, ybot + 44, "частота (лог)", size=12, color=INK, anchor="end", italic=True))
    frags.append(text(x0 - 12, ytop - 14, "|Zвих|", size=13, color=INK, anchor="end", bold=True))

    Rout, Cout = 3300.0, 1e-6
    fp1 = 1 / (2 * math.pi * Rout * Cout)          # ≈ 48.2 Гц
    fzT, fzC = 159200.0, 31.83e6                   # нулі: тантал 1 Ом, кераміка 5 мОм

    # допоміжні прямі: полиця Rвих і схил самої ємності 1/(2πfC)
    frags.append(line(x0, Y(Rout), X(fp1), Y(Rout), color=MUTED, sw=1.4, dash="6,4"))
    frags.append(line(X(fp1), Y(Rout), X(1e8), Y(Rout * fp1 / 1e8),
                      color=MUTED, sw=1.4, dash="6,4"))

    # полиці ESR
    frags.append(line(X(fzT), Y(1.0), x1, Y(1.0), color=NEG, sw=2.2))
    frags.append(line(X(fzC), Y(0.005), x1, Y(0.005), color=POS, sw=2.2))

    # робочі криві |Zвих|
    tant = [(X(1e1), Y(Rout)), (X(fp1), Y(Rout)), (X(fzT), Y(1.0)), (X(1e8), Y(1.0))]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2" '
                 'stroke-linejoin="round"/>' % (" ".join("%.1f,%.1f" % p for p in tant), NEG))
    cer = [(X(fzT), Y(1.0)), (X(fzC), Y(0.005))]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2" '
                 'stroke-linejoin="round"/>' % (" ".join("%.1f,%.1f" % p for p in cer), POS))

    # злами — короткі теги в порожніх кутах
    frags.append(circle(X(fp1), Y(Rout), 6, fill=BG, stroke=INK, sw=2.4))
    frags.append(text(X(fp1) + 14, Y(Rout) - 10, "полюс 48 Гц", size=12, color=INK,
                      anchor="start", bold=True))
    frags.append(circle(X(fzT), Y(1.0), 6, fill=BG, stroke=NEG, sw=2.4))
    frags.append(text(X(fzT) + 12, Y(1.0) - 12, "нуль 159 кГц", size=12, color=NEG,
                      anchor="start", bold=True))
    frags.append(circle(X(fzC), Y(0.005), 6, fill=BG, stroke=POS, sw=2.4))
    frags.append(text(X(fzC) - 12, Y(0.005) + 18, "нуль 31.8 МГц", size=12, color=POS,
                      anchor="end", bold=True))

    # зріз петлі — підпис ВИЩЕ за верх поля, щоб лінія його не різала
    fc = 130000.0
    frags.append(line(X(fc), ytop, X(fc), ybot, color=FIELD, sw=2, dash="5,4"))
    frags.append(text(X(fc), ytop - 30, "зріз петлі", size=12, color=FIELD, bold=True))
    frags.append(text(X(fc), ytop - 14, "≈ 130 кГц", size=11, color=FIELD))

    # легенда — у порожньому лівому низу, під схилом
    lx, ly = 152, 292
    frags.append(rect(lx - 12, ly - 22, 348, 92, fill="#fbfcfd", stroke=MUTED, sw=1.2))
    for i, (col, sw_, lab) in enumerate([
            (MUTED, 1.4, "Rвих = 3.3 кОм і схил 1/(2πf·Cвих)"),
            (NEG, 3.2, "|Zвих| з танталом: ESR 1 Ом"),
            (POS, 3.2, "|Zвих| з керамікою: ESR 5 мОм")]):
        yy = ly + i * 24
        frags.append(line(lx, yy, lx + 30, yy, color=col, sw=sw_,
                          dash="6,4" if i == 0 else None))
        frags.append(text(lx + 40, yy + 4, lab, size=11, color=col, anchor="start"))

    # висновок — рамка ЗАДАНОЇ ширини, щоб не вилізти за viewBox
    frags.append(fitbox(120, 434, 740, 54,
                        "Нуль сидить там, де схил ємності впирається в ESR. Полиця тантала ріже схил коло\n"
                        "самого зрізу; полиця кераміки — аж на 31.8 МГц, за 2.4 декади від потрібного місця.",
                        size=12, fill="#f4f6f8", stroke=MUTED))
    render(os.path.join(OUT, "math-zout.svg"), W, H, *frags,
           title="Імпеданс вихідного вузла: полюс і нуль — це два перетини прямих")


def fig_math_phase_budget():
    """Запас фази — це арифметика трьох арктангенсів на частоті зрізу.
    Уся різниця тантала й кераміки — у третьому доданку."""
    W, H = 980, 470
    x0, x1 = 150, 850
    frags = []

    def X(deg):                       # 0° … −180° → піксель
        return x0 + (-deg / 180.0) * (x1 - x0)

    # шкала фази
    for deg in (0, -45, -90, -135, -180):
        xx = X(deg)
        col = POS if deg == -180 else MUTED
        frags.append(line(xx, 92, xx, 386, color=col, sw=1.6,
                          dash=None if deg == -180 else "4,5"))
        frags.append(text(xx, 82, "%d°" % deg, size=12, color=col, bold=(deg == -180)))
    frags.append(text(X(-180), 62, "межа зриву", size=12, color=POS, bold=True))

    rows = [("тантал, ESR = 1 Ом", 170, 90.0, 73.0, 39.3, 56.3, NEG),
            ("кераміка, ESR = 5 мОм", 300, 90.0, 70.7, 0.2, 19.5, POS)]
    for lab, y, a1, a2, a3, pm, col in rows:
        frags.append(text(x0 - 16, y - 14, lab, size=13, color=col, anchor="end", bold=True))
        frags.append(text(x0 - 16, y + 4, "запас фази %.1f°" % pm, size=12, color=col, anchor="end"))
        # відрізок полюса виходу
        xa, xb = X(0), X(-a1)
        frags.append(rect(xa, y - 16, xb - xa, 32, fill="#f0f1f3", stroke=INK, sw=1.4, rx=3))
        frags.append(text((xa + xb) / 2, y + 5, "−%.0f° полюс виходу" % a1, size=12, color=INK))
        # відрізок полюса підсилювача
        xc = X(-(a1 + a2))
        frags.append(rect(xb, y - 16, xc - xb, 32, fill="#f0f1f3", stroke=INK, sw=1.4, rx=3))
        frags.append(text((xb + xc) / 2, y + 5, "−%.0f° підсил." % a2, size=12, color=INK))
        # відрізок нуля — тягне НАЗАД
        xd = X(-(a1 + a2 - a3))
        if a3 > 3:
            frags.append(rect(xd, y - 16, xc - xd, 32, fill="#e7f7ee", stroke=FIELD, sw=1.8, rx=3))
            frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                         'stroke-width="2.2" marker-end="url(#arrow)"/>' % (xc, y + 30, xd, y + 30, FIELD))
            frags.append(text((xc + xd) / 2, y + 50, "+%.1f° нуль ESR" % a3, size=12,
                              color=FIELD, bold=True))
        else:
            frags.append(text(xc + 6, y + 44, "нуль ESR дає лише +%.1f°" % a3, size=12,
                              color=FIELD, anchor="start", bold=True))
        # підсумкова фаза й запас
        frags.append(circle(xd, y, 6, fill=col, stroke=col))
        frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="2.6"/>' % (xd, y - 32, X(-180), y - 32, col))
        frags.append(text((xd + X(-180)) / 2, y - 40, "запас %.1f°" % pm, size=12, color=col, bold=True))

    frags.append(text((x0 + x1) / 2, 420, "фаза петлі на частоті зрізу  =  −arctg(f_c/f_p1) − arctg(f_c/f_p2) + arctg(f_c/f_z)",
                      size=13, color=INK, bold=True))
    frags.append(text((x0 + x1) / 2, 442, "перші два доданки майже однакові в обох випадках — уся різниця сидить у третьому",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "math-phase-budget.svg"), W, H, *frags,
           title="Запас фази — арифметика трьох арктангенсів (легке навантаження, 1 мА)")


# ── Фігури історичної вставки (hist-ldo-esr.md) ────────────────────────────

def _card(x, y, w, h, year, lines, accent=INK):
    """Картка віхи: рік угорі жирним, під ним 1–2 короткі рядки.
    Рядки тримаємо короткими — ширина картки з запасом."""
    cx = x + w / 2
    out = rect(x, y, w, h, fill=FILL, stroke=LINE, sw=1.4, rx=7)
    out += text(cx, y + 24, year, size=15, color=accent, bold=True)
    fs = min(fit_font(ln, w - 18, 12) for ln in lines)
    out += mtext(cx, y + 46, lines, size=fs, color=INK, lh=1.35)
    return out


def fig_hist_eras():
    """Дві ери вихідного конденсатора LDO: у першій вимога до ESR народжується
    (тантал випадково пасує), у другій її скасовують (кераміка + внутрішній нуль).
    Це послідовність віх, а не вісь у масштабі — тому картки, не шкала."""
    W, H = 1080, 500
    frags = []
    CW, CH = 190, 98

    # ── ера I ──
    y1 = 74
    frags.append(rect(60, y1 - 44, W - 120, 32, fill="#fdf3e3", stroke=GOLD, sw=1.4, rx=6))
    frags.append(text(W / 2, y1 - 22, "ЕРА ТАНТАЛУ — вимога до ESR народжується",
                      size=15, color=GOLD, bold=True))
    era1 = [
        ("1952", ["Bell Labs: MnO₂", "як твердий електроліт"]),
        ("1954", ["Sprague, Preston Robinson:", "серійний тантал"]),
        ("1977", ["Dobkin, «Break Loose…»", "заявка на першість (хитка)"]),
        ("1980-ті", ["вікна ESR у даташитах —", "міряні на столі, не лічені"]),
    ]
    gap1 = (W - 120 - len(era1) * CW) / (len(era1) - 1)
    for i, (yr, lines) in enumerate(era1):
        x = 60 + i * (CW + gap1)
        frags.append(_card(x, y1, CW, CH, yr, lines, accent=GOLD))
        if i:
            frags.append(line(x - gap1, y1 + CH / 2, x, y1 + CH / 2, color=MUTED, sw=1.2))

    # ── злам ──
    ym = y1 + CH + 46
    frags.append(arrow(W / 2, y1 + CH + 8, W / 2, ym + 6, color=POS, sw=2.2))
    frags.append(text(W / 2 + 14, ym - 4,
                      "кераміка дешевшає, тантал дорожчає — вихідний конденсатор міняють НЕ схемотехніки",
                      size=12.5, color=POS, anchor="start", bold=True))
    frags.append(text(W / 2 - 14, ym - 4, "злам", size=12.5, color=POS, anchor="end", bold=True))

    # ── ера II ──
    y2 = ym + 60
    frags.append(rect(60, y2 - 44, W - 120, 32, fill="#eaf7ef", stroke=FIELD, sw=1.4, rx=6))
    frags.append(text(W / 2, y2 - 22, "ЕРА КЕРАМІКИ — вимогу скасовують",
                      size=15, color=FIELD, bold=True))
    era2 = [
        ("1998", ["Rincón-Mora & Allen, JSSC;", "Micrel: «ESR замалий» — вада"]),
        ("2000–01", ["цінова буря на тантал:", "закупівлі женуть у кераміку"]),
        ("2000", ["патент TI 6304131:", "внутрішня компенсація"]),
        ("2003", ["Leung & Mok, HKUST:", "LDO зовсім без конденсатора"]),
        ("2006", ["TI AN-1482: «ceramic-", "stable» стає нормою"]),
    ]
    gap2 = (W - 120 - len(era2) * CW) / (len(era2) - 1)
    for i, (yr, lines) in enumerate(era2):
        x = 60 + i * (CW + gap2)
        frags.append(_card(x, y2, CW, CH, yr, lines, accent=FIELD))
        if i:
            frags.append(line(x - gap2, y2 + CH / 2, x, y2 + CH / 2, color=MUTED, sw=1.2))

    frags.append(text(W / 2, y2 + CH + 34,
                      "Обидві ери починаються не з ідеї схемотехніка, а з того, що стало дешево лежати на складі.",
                      size=12.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "hist-eras.svg"), W, H, *frags,
           title="Дві ери вихідного конденсатора LDO (послідовність віх, не шкала часу)")


def _wx(esr, x0=125.0, dec=148.0):
    """X для ESR на логарифмічній осі, від 1 мОм (=x0) до 100 Ом."""
    return x0 + (math.log10(esr) + 3.0) * dec


def fig_hist_window_shift():
    """Головна нетривіальна розплата: внутрішній нуль НЕ розширює вікно ESR —
    він його ЗСУВАЄ. Ліва стіна падає до нуля, але й права опускається
    з ~10 Ом до ~0.5 Ом (числа з TI AN-1482)."""
    W, H = 980, 430
    x0, dec = 125.0, 148.0
    xEnd = _wx(100)
    frags = []

    # ── вісь ESR (лог) ──
    yax = 348
    frags.append(line(x0, yax, xEnd, yax, color=INK, sw=1.8))
    for esr, lab in [(0.001, "1 мОм"), (0.01, "10 мОм"), (0.1, "100 мОм"),
                     (1, "1 Ом"), (10, "10 Ом"), (100, "100 Ом")]:
        x = _wx(esr, x0, dec)
        frags.append(line(x, yax, x, yax + 7, color=INK, sw=1.5))
        frags.append(text(x, yax + 25, lab, size=12, color=MUTED))
    frags.append(text((x0 + xEnd) / 2, yax + 50, "ESR вихідного конденсатора (лог)",
                      size=13, color=INK, bold=True))

    rows = [
        (128, "LDO 1980-х · «electrolytic-stable»", 0.1, 10.0, GOLD, "#fdf3e3"),
        (238, "LDO сучасний · «ceramic-stable»", None, 0.5, FIELD, "#eaf7ef"),
    ]
    for y, name, lo, hi, col, fill in rows:
        xa = _wx(lo, x0, dec) if lo else x0
        xb = _wx(hi, x0, dec)
        frags.append(rect(xa, y, xb - xa, 44, fill=fill, stroke=col, sw=2, rx=5))
        frags.append(text((xa + xb) / 2, y + 28, "вікно стійкості", size=12.5, color=col, bold=True))
        frags.append(text(x0 - 14, y + 27, name, size=12.5, color=INK, anchor="end", bold=True))
        # стіни
        lotxt = "0 Ом" if lo is None else ("%g Ом" % lo)
        frags.append(text(xa + (4 if lo is None else 0), y - 9, lotxt,
                          size=12, color=col, bold=True, anchor="start" if lo is None else "middle"))
        frags.append(text(xb, y - 9, "%g Ом" % hi, size=12, color=col, bold=True))
        frags.append(line(xa, y, xa, yax, color=col, sw=1.2, dash="4,4"))
        frags.append(line(xb, y, xb, yax, color=col, sw=1.2, dash="4,4"))

    # ── реальні конденсатори ──
    for esr, lab, col in [(0.005, "кераміка\n5 мОм", NEG), (0.5, "тантал\n0.5 Ом", POS)]:
        x = _wx(esr, x0, dec)
        frags.append(line(x, 96, x, yax, color=col, sw=2, dash="6,4"))
        frags.append(circle(x, yax, 5, fill=col, stroke=col))
        b, _, _ = textbox(x, 78, lab, size=11.5, color=col, stroke=col, fill=BG, pad=7)
        frags.append(b)

    # ── висновки ──
    xc = _wx(0.005, x0, dec)
    frags.append(text(xc - 8, 172, "кераміка ЛІВІШЕ за вікно → старий чип співає",
                      size=12, color=NEG, anchor="end", bold=True))
    frags.append(text(_wx(1.6, x0, dec), 282, "→ права стіна впала з 10 Ом до 0.5 Ом",
                      size=12, color=POS, anchor="start", bold=True))
    frags.append(text((x0 + xEnd) / 2, H - 18,
                      "Вікно не розширилося — воно з'їхало вліво: внутрішній нуль уже сидить у петлі, "
                      "і зайвий нуль від великого ESR розганяє смугу.",
                      size=12.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "hist-window-shift.svg"), W, H, *frags,
           title="Що зробила внутрішня компенсація з вікном ESR (числа з TI AN-1482)")


# ══════════════════════════════════════════════════════════════════════════
# Фігури вставки proj-esr-map.md
# ══════════════════════════════════════════════════════════════════════════

def fig_proj_esr_walls():
    """Чому дві стіни вікна ESR мають РІЗНУ геометрію. Ліва: нуль мусить
    устигнути під зріз. Права: полиця A₀·ESR/(Rвих+ESR) ємності не бачить —
    зріз тікає вгору й вилітає за полюс прохідного транзистора."""
    W, H = 1000, 580
    x0, x1 = 130, 820
    ytop, ybot = 92, 386
    fdec0, fdecs = 2.0, 6.0        # 10² Гц … 10⁸ Гц
    gmin, gmax = -24.0, 72.0       # дБ
    frags = []

    def X(f):
        return x0 + (math.log10(f) - fdec0) / fdecs * (x1 - x0)

    def Y(db):
        return ybot - (db - gmin) / (gmax - gmin) * (ybot - ytop)

    for d in range(2, 9):
        frags.append(line(X(10.0 ** d), ytop, X(10.0 ** d), ybot, color="#e6e8eb", sw=1))
    for db in range(-20, 80, 20):
        frags.append(line(x0, Y(db), x1, Y(db), color="#e6e8eb", sw=1))
    frags.append(line(x0, ytop, x0, ybot, color=INK, sw=1.8))
    frags.append(line(x0, Y(0), x1, Y(0), color=INK, sw=2, dash="6,4"))
    frags.append(text(x1 + 8, Y(0) + 4, "0 дБ", size=11, color=INK, anchor="start", bold=True))
    for f, lab in [(1e2, "100 Гц"), (1e3, "1 кГц"), (1e4, "10 кГц"), (1e5, "100 кГц"),
                   (1e6, "1 МГц"), (1e7, "10 МГц"), (1e8, "100 МГц")]:
        frags.append(text(X(f), ybot + 20, lab, size=11, color=MUTED))
    for db in range(-20, 80, 20):
        frags.append(text(x0 - 10, Y(db) + 4, "%d" % db, size=11, color=MUTED, anchor="end"))
    frags.append(text(x0 - 10, ytop - 14, "|L|, дБ", size=12, color=INK, anchor="end", bold=True))
    frags.append(text(x1, ybot + 42, "частота (лог)", size=12, color=INK, anchor="end", italic=True))

    # дві сталі особливості петлі
    frags.append(line(X(6e6), ytop - 4, X(6e6), ybot, color=GOLD, sw=2.2, dash="5,4"))
    frags.append(text(X(6e6), ytop - 28, "полюс прохідного", size=11, color=GOLD, bold=True))
    frags.append(text(X(6e6), ytop - 12, "транзистора, 6 МГц", size=11, color=GOLD, bold=True))
    frags.append(line(X(6e4), ytop - 4, X(6e4), ybot, color=MUTED, sw=1.4, dash="3,4"))
    frags.append(text(X(6e4), ytop - 12, "полюс підсил., 60 кГц", size=11, color=MUTED))

    # три ламані (асимптоти) — злами й зрізи з прогону скрипта
    curves = [
        ("мало ESR: 5 мОм", POS, [(1e2, 66), (723, 66), (6e4, 27.6), (1.2e6, -20.2)],
         2.91e5, "зріз ловить −40 дБ/дек — фазі кінець"),
        ("у вікні: 0.5 Ом", FIELD, [(1e2, 66), (720, 66), (6e4, 27.6),
                                    (1.45e5, 12.3), (2.4e6, -12.1)],
         6.06e5, "нуль устиг: зріз на −20 дБ/дек"),
        ("забагато ESR: 50 Ом", NEG, [(1e2, 66), (482, 66), (1447, 56.5),
                                      (6e4, 56.5), (6e6, 16.5), (3.2e7, -12.5)],
         1.49e7, "зріз утік аж за полюс транзистора"),
    ]
    for lab, col, pts, fc, note in curves:
        poly = " ".join("%.1f,%.1f" % (X(f), Y(g)) for f, g in pts)
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
                     'stroke-linejoin="round"/>' % (poly, col))
        frags.append(circle(X(fc), Y(0), 5.5, fill=BG, stroke=col, sw=2.4))

    # полиця ESR — суть правої стіни
    frags.append(line(X(1447), Y(56.5), X(6e4), Y(56.5), color=NEG, sw=5))
    frags.append(text(X(3.2e3), Y(56.5) - 30, "полиця |L| = A₀·ESR/(Rвих + ESR):",
                      size=12, color=NEG, bold=True, anchor="start"))
    frags.append(text(X(3.2e3), Y(56.5) - 14, "ємність скоротилась — висота від Cвих не залежить",
                      size=11, color=NEG, italic=True, anchor="start"))

    # підписи зрізів, рознесені по вертикалі
    marks = [(2.91e5, POS, "зріз 291 кГц", "запас 10°", -1),
             (6.06e5, FIELD, "зріз 606 кГц", "запас 77°", 1),
             (1.49e7, NEG, "зріз 14.9 МГц", "запас 22°", 1)]
    for fc, col, l1, l2, side in marks:
        yy = Y(0) + (40 if side > 0 else -34)
        frags.append(line(X(fc), Y(0), X(fc), yy - (10 if side > 0 else -10), color=col, sw=1.4))
        frags.append(text(X(fc), yy, l1, size=11, color=col, bold=True))
        frags.append(text(X(fc), yy + 15, l2, size=11, color=col))

    ly = 458
    for i, (lab, col, _, _, note) in enumerate(curves):
        yy = ly + i * 24
        frags.append(line(x0, yy - 4, x0 + 32, yy - 4, color=col, sw=3))
        frags.append(text(x0 + 42, yy, lab, size=12, color=col, anchor="start", bold=True))
        frags.append(text(x0 + 230, yy, "→  " + note, size=12, color=INK, anchor="start"))

    box, bw, bh = textbox((x0 + x1) / 2, 548,
                          "Ліва стіна тримає нуль ПІД зрізом; права не пускає сам зріз "
                          "за полюс прохідного транзистора.",
                          size=12, fill="#f4f6f8", stroke=MUTED)
    frags.append(box)
    render(os.path.join(OUT, "proj-esr-walls.svg"), W, H, *frags,
           title="Дві стіни вікна ESR працюють різними механізмами")


def fig_proj_esr_map():
    """Порахована карта в площині (Cвих, ESR): ліва стіна коса й уривається,
    права — стрімка вертикаль. Пряма «стала ESR·C» лягає поряд лише коло
    мінімальної ємності."""
    W, H = 1020, 600
    x0, x1 = 160, 810
    ytop, ybot = 96, 410
    frags = []

    def X(esr):                     # 1 мОм … 100 Ом
        return x0 + (math.log10(esr) + 3.0) / 5.0 * (x1 - x0)

    def Y(cuf):                     # 0.47 … 220 мкФ
        lo, hi = math.log10(0.47), math.log10(220.0)
        return ybot - (math.log10(cuf) - lo) / (hi - lo) * (ybot - ytop)

    # порахована ліва стіна (запас 30°) — з прогону скрипта
    left = [(0.470, 0.29994), (0.661, 0.23552), (0.931, 0.18409), (1.310, 0.14273),
            (1.843, 0.10924), (2.593, 0.08197), (3.649, 0.05966), (5.135, 0.04134),
            (7.226, 0.02623), (10.169, 0.01375), (14.309, 0.00341)]
    RIGHT = 21.6

    poly = [(X(e), Y(c)) for c, e in left]
    poly += [(X(0.001), Y(14.309)), (X(0.001), Y(220.0)),
             (X(RIGHT), Y(220.0)), (X(RIGHT), Y(0.470))]
    frags.append('<polygon points="%s" fill="%s" fill-opacity="0.16" stroke="none"/>'
                 % (" ".join("%.1f,%.1f" % p for p in poly), FIELD))

    for e in (0.001, 0.01, 0.1, 1.0, 10.0, 100.0):
        frags.append(line(X(e), ytop, X(e), ybot, color="#e6e8eb", sw=1))
    for c in (0.47, 1.0, 2.2, 4.7, 10.0, 22.0, 47.0, 100.0, 220.0):
        frags.append(line(x0, Y(c), x1, Y(c), color="#e6e8eb", sw=1))
    frags.append(line(x0, ytop, x0, ybot, color=INK, sw=1.8))
    frags.append(line(x0, ybot, x1, ybot, color=INK, sw=1.8))
    for e, lab in [(0.001, "1 мОм"), (0.01, "10 мОм"), (0.1, "0.1 Ом"),
                   (1.0, "1 Ом"), (10.0, "10 Ом"), (100.0, "100 Ом")]:
        frags.append(text(X(e), ybot + 20, lab, size=11, color=MUTED))
    for c in (0.47, 1.0, 2.2, 4.7, 10.0, 22.0, 47.0, 100.0, 220.0):
        frags.append(text(x0 - 10, Y(c) + 4, "%g" % c, size=11, color=MUTED, anchor="end"))
    frags.append(text(x0 - 10, ytop - 30, "Cвих,", size=12, color=INK, anchor="end", bold=True))
    frags.append(text(x0 - 10, ytop - 14, "мкФ", size=12, color=INK, anchor="end", bold=True))
    frags.append(text(x1, ybot + 42, "ESR вихідного конденсатора (лог)", size=12,
                      color=INK, anchor="end", italic=True))

    # пряма «стала ESR·C = 2.2·10⁻⁷» — правило з даташита
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="2.2" stroke-dasharray="7,5"/>'
                 % (X(2.2e-7 / 0.47e-6), Y(0.47), X(2.2e-7 / 220e-6), Y(220.0), GOLD))
    frags.append(text(X(0.0042), Y(64.0), "правило «стала ESR·Cвих»", size=11,
                      color=GOLD, anchor="start", bold=True))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                 % (" ".join("%.1f,%.1f" % (X(e), Y(c)) for c, e in left), POS))
    frags.append(circle(X(0.00341), Y(14.309), 5, fill=BG, stroke=POS, sw=2.2))
    frags.append(text(X(0.022), Y(28.0), "тут ліва стіна уривається:", size=11,
                      color=POS, anchor="start", bold=True))
    frags.append(text(X(0.022), Y(19.0), "від ~20 мкФ нуль ESR узагалі не потрібен", size=11,
                      color=POS, anchor="start"))

    frags.append(line(X(RIGHT), ytop, X(RIGHT), ybot, color=NEG, sw=3))
    frags.append(text(X(RIGHT) + 9, ytop + 16, "права стіна:", size=11, color=NEG,
                      anchor="start", bold=True))
    frags.append(text(X(RIGHT) + 9, ytop + 32, "21.6 Ом за будь-якої", size=11,
                      color=NEG, anchor="start"))
    frags.append(text(X(RIGHT) + 9, ytop + 48, "ємності — вертикаль", size=11,
                      color=NEG, anchor="start"))

    frags.append(text(X(0.9), Y(6.0), "СТІЙКО", size=15, color="#1e7d45", bold=True))

    # вікно, надруковане в даташиті, при 2.2 мкФ
    frags.append(line(X(0.1), Y(2.2), X(20.0), Y(2.2), color=INK, sw=3.4))
    for e in (0.1, 20.0):
        frags.append(line(X(e), Y(2.2) - 7, X(e), Y(2.2) + 7, color=INK, sw=2.6))
    frags.append(text(X(1.4), Y(2.2) - 13, "даташит: 0.1 … 20 Ом при 2.2 мкФ", size=11,
                      color=INK, bold=True))

    cx, cy = X(0.005), Y(2.2)
    frags.append(line(cx - 7, cy - 7, cx + 7, cy + 7, color=POS, sw=2.6))
    frags.append(line(cx - 7, cy + 7, cx + 7, cy - 7, color=POS, sw=2.6))
    frags.append(text(cx, cy + 24, "кераміка 2.2 мкФ", size=11, color=POS, bold=True))
    frags.append(text(cx, cy + 51, "запас 10°", size=11, color=POS))

    box, bw, bh = textbox((x0 + x1) / 2, 508,
                          "Ліва стіна тримає добуток ESR·Cвих — тому коса.\n"
                          "Права тримає полицю A₀·ESR/(Rвих+ESR), яка ємності не бачить — тому вертикаль.",
                          size=12, fill="#f4f6f8", stroke=MUTED)
    frags.append(box)
    render(os.path.join(OUT, "proj-esr-map.svg"), W, H, *frags,
           title="Порахована карта стійкості в площині (Cвих, ESR)")


if __name__ == "__main__":
    fig_two_poles()
    fig_load_pole()
    fig_esr_tunnel()
    fig_math_loop_nodes()
    fig_math_zout()
    fig_math_phase_budget()
    fig_hist_eras()
    fig_hist_window_shift()
    fig_proj_esr_walls()
    fig_proj_esr_map()
    print("ok figs")
