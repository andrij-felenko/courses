# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

import math


# ── 1. Дві цеглинки: інтегратор + поріг із двома станами ─────────────────────
def fig_blocks():
    W, H = 720, 300
    frags = []
    cy = 150

    # цеглинка 1 — RC-інтегратор
    b1, w1, h1 = textbox(150, cy, "Інтегратор\n(R заряджає C)\nнапруга повзе плавно",
                         size=13, pad=14, stroke=NEG, sw=2.2, color=INK)
    frags.append(b1)
    frags.append(text(150, cy - h1 / 2 - 14, "повільне", size=12, color=NEG, italic=True))

    # цеглинка 2 — поріг із двома станами
    b2, w2, h2 = textbox(560, cy, "Поріг із двома станами\n(коли дійшло — клац,\nстан перемикається)",
                         size=13, pad=14, stroke=POS, sw=2.2, color=INK)
    frags.append(b2)
    frags.append(text(560, cy - h2 / 2 - 14, "миттєве", size=12, color=POS, italic=True))

    # стрілка вперед: напруга дійшла до порога
    frags.append(arrow(150 + w1 / 2 + 8, cy - 14, 560 - w2 / 2 - 8, cy - 14, color=INK, sw=2.2))
    frags.append(text(355, cy - 26, "дійшла до порога", size=12, color=INK))

    # стрілка назад: перемикання скидає інтегратор
    frags.append(arrow(560 - w2 / 2 - 8, cy + 16, 150 + w1 / 2 + 8, cy + 16, color=POS, sw=2.4))
    frags.append(text(355, cy + 34, "клац скидає заряд → усе спочатку", size=12, color=POS))

    render(os.path.join(IMG, "blocks.svg"), W, H, *frags,
           title="Дві цеглинки релаксаційного генератора")


# ── 2. Форма коливання: пиляк заряду-розряду на конденсаторі ─────────────────
def fig_waveform():
    W, H = 720, 360
    ox, oy = 80, H - 70          # початок осей
    aw, ah = 580, 240            # поле
    frags = []
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))
    frags.append(text(ox + aw, oy + 26, "час", size=13, color=INK, anchor="end"))
    frags.append(text(ox - 10, oy - ah + 4, "U", size=15, color=INK, anchor="end", bold=True))

    # два пороги
    yhi = oy - ah * 0.78
    ylo = oy - ah * 0.30
    frags.append(line(ox, yhi, ox + aw, yhi, color=POS, sw=1.6, dash="6,5"))
    frags.append(line(ox, ylo, ox + aw, ylo, color=NEG, sw=1.6, dash="6,5"))
    frags.append(text(ox + aw + 4, yhi + 4, "верхній\nпоріг" if False else "верхній поріг", size=11, color=POS, anchor="start"))
    frags.append(text(ox + aw + 4, ylo + 4, "нижній поріг", size=11, color=NEG, anchor="start"))

    # напруга на C: експоненційний заряд до верхнього, тоді розряд до нижнього, повторити
    # будуємо як ламані-експоненти між порогами
    def seg_up(x0, x1, ystart, ytarget, asym):
        # заряд до асимптоти asym (вище ytarget); рух від ystart до ytarget по exp
        pts = []
        N = 40
        for k in range(N + 1):
            t = k / N
            # частка шляху ystart→ytarget за «опуклою» exp-кривою
            frac = 1 - math.exp(-2.0 * t)
            frac = frac / (1 - math.exp(-2.0))
            y = ystart + (ytarget - ystart) * frac
            x = x0 + (x1 - x0) * t
            pts.append((x, y))
        return pts

    def seg_dn(x0, x1, ystart, ytarget):
        pts = []
        N = 40
        for k in range(N + 1):
            t = k / N
            frac = 1 - math.exp(-2.0 * t)
            frac = frac / (1 - math.exp(-2.0))
            y = ystart + (ytarget - ystart) * frac
            x = x0 + (x1 - x0) * t
            pts.append((x, y))
        return pts

    allpts = []
    nseg = 6
    seglen = (aw - 12) / nseg
    x = ox + 6
    state_low = True   # стоїмо біля нижнього, їдемо вгору
    ystart = ylo
    for i in range(nseg):
        x1 = x + seglen
        seg = seg_up(x, x1, ystart, yhi, None) if state_low else seg_dn(x, x1, ystart, ylo)
        # уникнути дубля точки на стику
        if allpts:
            seg = seg[1:]
        allpts += seg
        ystart = yhi if state_low else ylo
        x = x1
        state_low = not state_low

    pts_str = " ".join("%.1f,%.1f" % (px, py) for (px, py) in allpts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (pts_str, INK))

    # підпис фаз під першими двома сегментами
    frags.append(text(ox + 6 + seglen * 0.5, oy + 20, "повільний заряд", size=11.5, color=NEG))
    frags.append(text(ox + 6 + seglen * 1.5, oy + 20, "розряд", size=11.5, color=POS))

    # позначка «клац» на верхньому порозі
    xc = ox + 6 + seglen
    frags.append(circle(xc, yhi, 5, fill=POS, stroke=POS))
    frags.append(text(xc + 6, yhi - 10, "клац", size=11, color=POS, anchor="start"))

    render(os.path.join(IMG, "waveform.svg"), W, H, *frags,
           title="Напруга на конденсаторі: повзе до порога, тоді скидається")


# ── 3. Канонічна схема: компаратор + RC + поріг від виходу ───────────────────
def fig_comparator():
    W, H = 740, 380
    frags = []

    def res(x, y, horiz, label, col):
        # резистор-прямокутник із центром (x,y); підпис над/ліворуч
        if horiz:
            frags.append(rect(x - 24, y - 9, 48, 18, fill=BG, stroke=col, sw=1.7, rx=3))
            frags.append(text(x, y - 14, label, size=12, color=col))
        else:
            frags.append(rect(x - 9, y - 24, 18, 48, fill=BG, stroke=col, sw=1.7, rx=3))
            frags.append(text(x + 15, y + 4, label, size=12, color=col, anchor="start"))

    def cap(x, y, col, label):
        frags.append(line(x - 17, y, x + 17, y, color=col, sw=2.6))
        frags.append(line(x - 17, y + 8, x + 17, y + 8, color=col, sw=2.6))
        frags.append(text(x + 22, y + 8, label, size=12, color=col, anchor="start"))

    def gnd(x, y, col=INK):
        frags.append(line(x, y, x, y + 12, color=col, sw=1.8))
        frags.append(line(x - 12, y + 12, x + 12, y + 12, color=col, sw=2))
        frags.append(line(x - 7, y + 17, x + 7, y + 17, color=col, sw=2))
        frags.append(line(x - 3, y + 22, x + 3, y + 22, color=col, sw=2))

    # компаратор (трикутник), вершина-вихід праворуч
    ax = 300                       # ліва грань
    ty = 180                       # вісь
    p1 = (ax, ty - 60); p2 = (ax, ty + 60); p3 = (ax + 130, ty)
    frags.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], FILL, INK))
    minus_y = ty - 28; plus_y = ty + 28
    frags.append(text(ax + 16, minus_y + 6, "−", size=20, color=NEG, bold=True))
    frags.append(text(ax + 16, plus_y + 6, "+", size=20, color=POS, bold=True))

    # вихід → вузол OUT, далі на ярлик «меандр»
    outx = p3[0] + 90
    frags.append(line(p3[0], ty, outx + 40, ty, color=INK, sw=2.2))
    frags.append(circle(outx, ty, 3.5, fill=INK, stroke=INK))
    b, bw, bh = textbox(outx + 110, ty, "вихід\nмеандр", size=12, pad=10, stroke=INK, sw=1.8)
    frags.append(b)

    # ── гілка ЧАСУ (синя): OUT → R → вузол «−» (ліва колонка), вниз C на землю ──
    nminus_x = ax - 150                # ліва колонка
    frags.append(line(outx, ty, outx, ty + 110, color=NEG, sw=1.9))
    frags.append(line(outx, ty + 110, nminus_x, ty + 110, color=NEG, sw=1.9))
    res((outx + nminus_x) / 2, ty + 110, True, "R", NEG)
    frags.append(line(nminus_x, ty + 110, nminus_x, minus_y, color=NEG, sw=1.9))
    frags.append(line(nminus_x, minus_y, ax, minus_y, color=NEG, sw=1.9))
    frags.append(circle(nminus_x, minus_y, 3.5, fill=NEG, stroke=NEG))
    # C від вузла «−» донизу на свою землю (ліворуч)
    frags.append(line(nminus_x, minus_y, nminus_x, minus_y + 34, color=NEG, sw=1.9))
    cap(nminus_x, minus_y + 34, NEG, "C")
    gnd(nminus_x, minus_y + 42, NEG)
    frags.append(text(nminus_x - 24, ty + 110, "час", size=11, color=NEG, anchor="end"))
    frags.append(text(nminus_x - 24, ty + 124, "заряду", size=11, color=NEG, anchor="end"))

    # ── гілка ПОРОГА (червона): OUT → R1 → вузол «+» (права колонка) → R2 → земля ──
    nplus_x = ax - 60                  # окрема колонка, правіше за синю
    frags.append(line(outx, ty, outx, ty - 110, color=POS, sw=1.9))
    frags.append(line(outx, ty - 110, nplus_x, ty - 110, color=POS, sw=1.9))
    res((outx + nplus_x) / 2, ty - 110, True, "R₁", POS)
    frags.append(line(nplus_x, ty - 110, nplus_x, plus_y, color=POS, sw=1.9))
    frags.append(line(nplus_x, plus_y, ax, plus_y, color=POS, sw=1.9))
    frags.append(circle(nplus_x, plus_y, 3.5, fill=POS, stroke=POS))
    # R2 від вузла «+» донизу на свою землю
    frags.append(line(nplus_x, plus_y, nplus_x, plus_y + 16, color=POS, sw=1.9))
    res(nplus_x, plus_y + 40, False, "R₂", POS)
    frags.append(line(nplus_x, plus_y + 64, nplus_x, plus_y + 80, color=POS, sw=1.9))
    gnd(nplus_x, plus_y + 80, POS)
    frags.append(text(nplus_x + 14, ty - 110, "поріг від виходу", size=11, color=POS, anchor="start"))

    render(os.path.join(IMG, "comparator.svg"), W, H, *frags,
           title="Компаратор + RC: синя гілка тримає час, червона — поріг")


# ── 4. Геометрія виведення: експонента тягнеться до U∞, рахуємо «лишок» ───────
def fig_gap():
    W, H = 720, 380
    ox, oy = 90, H - 70
    aw, ah = 560, 250
    frags = []
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))
    frags.append(text(ox + aw, oy + 26, "час t", size=13, color=INK, anchor="end"))
    frags.append(text(ox - 12, oy - ah + 4, "u", size=15, color=INK, anchor="end", bold=True))

    # рівні: U∞ (стеля, асимптота), VH, VL
    yinf = oy - ah * 0.92
    yhi = oy - ah * 0.66
    ylo = oy - ah * 0.30
    frags.append(line(ox, yinf, ox + aw, yinf, color=MUTED, sw=1.6, dash="7,5"))
    frags.append(line(ox, yhi, ox + aw, yhi, color=POS, sw=1.5, dash="5,4"))
    frags.append(line(ox, ylo, ox + aw, ylo, color=NEG, sw=1.5, dash="5,4"))
    frags.append(text(ox + aw + 6, yinf + 4, "U∞ (стеля)", size=12, color=MUTED, anchor="start"))
    frags.append(text(ox + aw + 6, yhi + 4, "VH", size=12, color=POS, anchor="start"))
    frags.append(text(ox + aw + 6, ylo + 4, "VL", size=12, color=NEG, anchor="start"))

    # експонента: стартує з VL, тягнеться ДО U∞, але ми ловимо її на VH
    # u(t) = U∞ + (VL − U∞)·e^(−t/τ)  → у пікселях y росте вниз
    import math as _m
    def yval(t, tau):
        # частка пройденого до стелі
        return yinf + (ylo - yinf) * _m.exp(-t / tau)
    # підберемо так, щоб крива досягла yhi приблизно на x = ox + aw*0.55
    tau = 1.0
    xcross = ox + aw * 0.55
    # знайдемо t*, коли yval == yhi
    # (ylo−yinf)·e^(−t/τ) = (yhi−yinf) → e^(−t/τ)=(yhi−yinf)/(ylo−yinf)
    ratio = (yhi - yinf) / (ylo - yinf)
    tstar = -tau * _m.log(ratio)
    # масштаб часу в пікселі: t=tstar → x=xcross
    xscale = (xcross - ox) / tstar
    pts = []
    N = 90
    tmax = tstar * 1.85
    for k in range(N + 1):
        t = tmax * k / N
        x = ox + t * xscale
        y = yval(t, tau)
        pts.append((x, y))
    # суцільна частина до перетину VH, пунктир — продовження «куди б дійшло»
    solid = [(x, y) for (x, y) in pts if x <= xcross + 0.1]
    ghost = [(x, y) for (x, y) in pts if x >= xcross - 0.1]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join("%.1f,%.1f" % p for p in solid), INK))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,5"/>'
                 % (" ".join("%.1f,%.1f" % p for p in ghost), MUTED))

    # вертикаль на старті: лишок (U∞ − VL)
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)" marker-start="url(#arrow)"/>'
                 % (ox + 30, yinf + 2, ox + 30, ylo - 2, NEG))
    bb, bw, bh = textbox(ox + 30 + 8 + 60, (yinf + ylo) / 2, "лишок старту\nU∞ − VL", size=11, pad=7,
                         stroke=NEG, sw=1.5, color=NEG)
    frags.append(bb)

    # вертикаль у момент перетину: лишок (U∞ − VH)
    frags.append(line(xcross, yinf, xcross, yhi, color=POS, sw=2.2))
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)" marker-start="url(#arrow)"/>'
                 % (xcross, yinf + 2, xcross, yhi - 2, POS))
    cc, cw, ch = textbox(xcross + 70, (yinf + yhi) / 2 - 6, "лишок у фіналі\nU∞ − VH", size=11, pad=7,
                         stroke=POS, sw=1.5, color=POS)
    frags.append(cc)

    # позначка часу t між стартом і перетином
    frags.append(line(ox, oy + 12, xcross, oy + 12, color=INK, sw=1.4))
    frags.append(text((ox + xcross) / 2, oy + 28, "час фази t = τ·ln[(U∞−VL)/(U∞−VH)]", size=12, color=INK))

    # точка «клац» на перетині
    frags.append(circle(xcross, yhi, 5, fill=POS, stroke=POS))

    render(os.path.join(IMG, "gap.svg"), W, H, *frags,
           title="Час фази — це логарифм відношення двох «лишків до стелі»")


# ── 5. Симетрія vs несиметрія: однакові R проти різних ───────────────────────
def fig_duty():
    W, H = 720, 330
    frags = []

    def panel(x0, title, rfill, frac_hi, sub):
        # рамка-заголовок
        frags.append(text(x0 + 150, 56, title, size=14, color=INK, bold=True))
        ox, oy = x0 + 30, 250
        aw, ah = 240, 130
        frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
        frags.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.8))
        # меандр виходу: частка frac_hi — високий рівень
        yhi = oy - ah * 0.82
        ylo = oy - ah * 0.12
        period = aw * 0.46
        x = ox + 4
        up = True
        segpts = []
        # старт унизу
        segpts.append((x, ylo))
        for _ in range(5):
            seglen = period * (frac_hi if up else (1 - frac_hi))
            y = yhi if up else ylo
            segpts.append((x, y))
            x2 = min(x + seglen, ox + aw)
            segpts.append((x2, y))
            x = x2
            up = not up
            if x >= ox + aw:
                break
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                     % (" ".join("%.1f,%.1f" % p for p in segpts), rfill))
        frags.append(text(ox - 6, yhi + 4, "H", size=11, color=INK, anchor="end"))
        frags.append(text(ox - 6, ylo + 4, "L", size=11, color=INK, anchor="end"))
        # підпис частки
        frags.append(text(x0 + 150, oy + 26, sub, size=12, color=rfill))

    panel(40, "симетрія: один R", POS, 0.5, "tᴴ = tᴸ = R·C·ln2  →  D = 50%")
    panel(390, "несиметрія: різні шляхи", NEG, 0.66, "tᴴ > tᴸ  →  D > 50%")

    # роздільник
    frags.append(line(370, 70, 370, 290, color=MUTED, sw=1.2, dash="4,5"))

    render(os.path.join(IMG, "duty.svg"), W, H, *frags,
           title="Однакові R дають симетричний меандр; різні — зміщену шпаруватість")


if __name__ == "__main__":
    fig_blocks()
    fig_waveform()
    fig_comparator()
    fig_gap()
    fig_duty()
    print("ok: figures written to", IMG)
