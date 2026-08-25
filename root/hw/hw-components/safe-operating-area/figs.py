# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Струмова нитка: рівний розподіл vs стягування в точку ─────────────────
def fig_filament():
    W, H = 760, 380
    frags = []

    # дві панелі-кристали
    pad = 30
    pw = 300
    ph = 210
    top = 90
    gap = (W - 2 * pw - 2 * pad)
    x1 = pad
    x2 = W - pad - pw

    frags.append(text(W / 2, 34, "Той самий кристал — два режими розтікання струму",
                      size=17, bold=True))

    # сітка комірок усередині кристала
    cols, rows = 7, 5
    cwid = pw / cols
    chei = ph / rows

    def panel(x0, label, sublabel, hot_col, hot_row, hog):
        out = []
        out.append(rect(x0, top, pw, ph, fill="#fbfcfd", stroke=LINE, sw=2))
        # комірки із заливкою за «температурою»
        import math
        for r in range(rows):
            for c in range(cols):
                cx = x0 + c * cwid + cwid / 2
                cy = top + r * chei + chei / 2
                if hog:
                    d = math.hypot(c - hot_col, r - hot_row)
                    t = max(0.0, 1.0 - d / 3.2)      # 0..1, пік у гарячій комірці
                    t = t ** 1.7
                else:
                    t = 0.32                          # рівномірно тепло
                # колір від світло-сірого до гарячого червоного
                rr = int(244 + (192 - 244) * t)
                gg = int(246 + (57 - 246) * t)
                bb = int(248 + (43 - 248) * t)
                fill = "#%02x%02x%02x" % (rr, gg, bb)
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                           'fill="%s" stroke="#d4d9de" stroke-width="0.8"/>'
                           % (cx - cwid / 2 + 1, cy - chei / 2 + 1,
                              cwid - 2, chei - 2, fill))
        # підпис під панеллю
        out.append(text(x0 + pw / 2, top + ph + 30, label, size=15, bold=True))
        out.append(text(x0 + pw / 2, top + ph + 50, sublabel, size=12, color=MUTED))
        return out

    frags += panel(x1, "Рівний струм", "усі комірки несуть порівну — норма",
                   None, None, hog=False)
    frags += panel(x2, "Струмова нитка", "одна комірка перетягла майже все",
                   5, 2, hog=True)

    # стрілка переходу між панелями
    midy = top + ph / 2
    frags.append(arrow(x1 + pw + 8, midy, x2 - 8, midy, color=POS, sw=2.4))
    b, _, _ = textbox((x1 + pw + x2) / 2, midy - 26,
                      "локальний\nперегрів",
                      size=11, pad=6, fill="#fdecea", stroke=POS, sw=1.5)
    frags.append(b)

    render(os.path.join(IMG, "current-filament.svg"), W, H, *frags)


# ── 2. Чотири межі SOA в логарифмічних осях ─────────────────────────────────
def fig_soa():
    W, H = 720, 470
    frags = []
    frags.append(text(W / 2, 30, "Зона безпечної роботи в логарифмічних осях",
                      size=17, bold=True))

    # рамка-осі
    ox, oy = 95, 70          # лівий-верхній кут поля
    ow, oh = 540, 320        # розмір поля
    bx, by = ox, oy + oh     # початок осей (лівий-нижній)

    # осі
    frags.append(line(ox, oy, ox, by, color=INK, sw=2))         # вертикаль (Ic)
    frags.append(line(ox, by, ox + ow, by, color=INK, sw=2))    # горизонталь (Vce)
    frags.append(text(ox - 60, oy + 8, "Ic", size=15, bold=True, anchor="start"))
    frags.append(text(ox - 60, oy + 26, "(лог)", size=11, color=MUTED, anchor="start"))
    frags.append(text(ox + ow - 4, by + 34, "Vce (лог)", size=15, bold=True, anchor="end"))

    # координати ламаної межі SOA (всередині поля), зліва-вгорі → справа-вниз
    # точки в частках поля (0..1 по кожній осі), потім переводимо в пікселі
    def P(fx, fy):
        return (ox + fx * ow, by - fy * oh)

    # вершини контуру
    a = P(0.00, 0.86)   # верх лівий — стеля струму починається
    b1 = P(0.34, 0.86)  # кінець стелі струму (злам у похилу потужність)
    c = P(0.62, 0.50)   # лінія потужності (нахил −1) до зламу у вторинний пробій
    d = P(0.80, 0.20)   # лінія вторинного пробою (крутіше)
    e = P(0.80, 0.00)   # вертикаль пробою BVceo вниз до осі

    safe_fill = "#eaf6ee"
    # заливка безпечної області (полігон a-b1-c-d-e-низ-ліво)
    poly = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        ox, by, ox, a[1], a[0], a[1], b1[0], b1[1], c[0], c[1], d[0], d[1], e[0], e[1])
    frags.append('<polygon points="%s" fill="%s" stroke="none"/>' % (poly, safe_fill))

    # межі — кожну своїм кольором/підписом
    frags.append(line(a[0], a[1], b1[0], b1[1], color=NEG, sw=3))          # стеля струму
    frags.append(line(b1[0], b1[1], c[0], c[1], color=FIELD, sw=3))        # потужність
    frags.append(line(c[0], c[1], d[0], d[1], color=POS, sw=3))           # вторинний пробій
    frags.append(line(d[0], d[1], e[0], e[1], color=INK, sw=3, dash="6 4"))  # BVceo

    # підпис «БЕЗПЕЧНО» всередині
    frags.append(text(ox + 0.22 * ow, by - 0.42 * oh, "БЕЗПЕЧНО",
                      size=15, bold=True, color=FIELD))

    # виноски до кожної межі (textbox, аби напис не вилазив)
    def label(px, py, s, col, tx, ty):
        bb, _, _ = textbox(tx, ty, s, size=11, pad=6, fill="white",
                           stroke=col, sw=1.5, color=INK)
        return line(px, py, tx, ty, color=col, sw=1.0, dash="3 3") + bb

    midA = ((a[0] + b1[0]) / 2, a[1])
    frags.append(label(midA[0], midA[1], "стеля струму\nIc(max)", NEG,
                       ox + 0.17 * ow, oy - 8))
    midB = ((b1[0] + c[0]) / 2, (b1[1] + c[1]) / 2)
    frags.append(label(midB[0], midB[1], "стала потужність\nнахил −1", FIELD,
                       ox + 0.52 * ow, oy + 0.10 * oh))
    midC = ((c[0] + d[0]) / 2, (c[1] + d[1]) / 2)
    frags.append(label(midC[0], midC[1], "вторинний пробій\nнахил −α (крутіше)", POS,
                       ox + 0.97 * ow, by - 0.58 * oh))
    frags.append(label(e[0], (d[1] + e[1]) / 2, "пробій\nBVceo", INK,
                       ox + ow + 4, by - 0.12 * oh))

    render(os.path.join(IMG, "soa-boundaries.svg"), W, H, *frags)


# ── 3. Дослід Шафта–Френча: люмінофор робить гарячу нитку видимою ────────────
def fig_phosphor():
    import math
    W, H = 760, 380
    frags = []
    frags.append(text(W / 2, 34, "Дослід Шафта–Френча: невидиме тепло стало видимим",
                      size=17, bold=True))

    pad = 30
    pw = 300
    ph = 210
    top = 90
    x1 = pad
    x2 = W - pad - pw

    def panel(x0, label, sublabel, glow):
        out = []
        # «кристал» — темне тло, на ньому світиться люмінофор
        out.append(rect(x0, top, pw, ph, fill="#111418", stroke=LINE, sw=2))
        # люмінофорне світіння як сітка точок різної яскравості
        cols, rows = 26, 18
        cwid = pw / cols
        chei = ph / rows
        hc, hr = cols * 0.62, rows * 0.5     # положення гарячої плями
        for r in range(rows):
            for c in range(cols):
                cx = x0 + c * cwid + cwid / 2
                cy = top + r * chei + chei / 2
                if glow:
                    d = math.hypot((c - hc) / cols, (r - hr) / rows)
                    t = math.exp(-(d * 6.5) ** 2)      # яскравий вузький пік
                    base = 0.06
                    v = base + (1.0 - base) * t
                else:
                    v = 0.20                            # тьмяно й рівно
                # від тьмяно-зеленкуватого люмінофора до яскраво-жовто-білого піку
                rr = int(40 + (255 - 40) * v)
                gg = int(70 + (250 - 70) * v)
                bb = int(50 + (200 - 50) * (v ** 1.6))
                fill = "#%02x%02x%02x" % (rr, gg, bb)
                rad = 1.4 + 2.2 * (v if glow else 0.3)
                out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                           % (cx, cy, rad, fill))
        out.append(text(x0 + pw / 2, top + ph + 30, label, size=15, bold=True))
        out.append(text(x0 + pw / 2, top + ph + 50, sublabel, size=12, color=MUTED))
        return out

    frags += panel(x1, "Струм розтікається рівно",
                   "світіння тьмяне й однорідне", glow=False)
    frags += panel(x2, "Струм стягнувся в нитку",
                   "одна точка спалахує яскраво", glow=True)

    # стрілка-перехід
    midy = top + ph / 2
    frags.append(arrow(x1 + pw + 8, midy, x2 - 8, midy, color=POS, sw=2.4))
    b, _, _ = textbox((x1 + pw + x2) / 2, midy - 26,
                      "гаряча\nнитка",
                      size=11, pad=6, fill="#fdecea", stroke=POS, sw=1.5)
    frags.append(b)

    render(os.path.join(IMG, "phosphor-hotspot.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_filament()
    fig_soa()
    fig_phosphor()
    print("ok: current-filament.svg, soa-boundaries.svg, phosphor-hotspot.svg")
