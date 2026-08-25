# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURPLE = "#8a4ea8"   # смуговий / третій колір характеристики


def polyline(pts, color, sw=2.4):
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>'
            % (" ".join("%.1f,%.1f" % (x, y) for x, y in pts), color, sw))


def axes(p, ox, oy, top, right, xlabel=None):
    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.4))
    p.append(arrow(ox, oy, right, oy, color=INK, sw=1.4))
    if xlabel:
        p.append(text(right - 2, oy + 16, xlabel, size=10, color=MUTED, anchor="end", italic=True))


# логістичні / гаусові форми характеристик у нормованих координатах [0..1] по f
def lp_shape(f, fc=0.42, k=14):   # низькі пропускає
    return 1.0 / (1.0 + math.exp(k * (f - fc)))

def hp_shape(f, fc=0.5, k=14):    # високі пропускає
    return 1.0 / (1.0 + math.exp(-k * (f - fc)))

def bp_shape(f, f0=0.5, bw=0.16): # смуга навколо f0
    return math.exp(-((f - f0) / bw) ** 2)

def bs_shape(f, f0=0.5, bw=0.06): # провал на f0
    return 1.0 - 0.97 * math.exp(-((f - f0) / bw) ** 2)


def shape_curve(ox, oy, w, h, fn, color, sw=2.4, n=240):
    pts = []
    for i in range(n + 1):
        f = i / n
        v = fn(f)
        pts.append((ox + f * w, oy - v * h))
    return polyline(pts, color, sw)


# ── four-shapes: чотири форми характеристики поруч ────────────────────────────
# Ідея: один малюнок — чотири канонічні форми |H(f)|, щоб одразу побачити, де в
# кожній пропускання, а де затримання.

def fig_four_shapes():
    W, H = 720, 360
    p = []
    pw, ph = 250, 96          # розмір одного панно осей
    pad_l = 60
    col2 = 400
    row1, row2 = 70 + ph, 210 + ph   # базові лінії (oy) двох рядів

    panels = [
        (pad_l, row1, "НЧ (ФНЧ)", "пропустити повільне", lp_shape, FIELD),
        (col2,  row1, "ВЧ (ФВЧ)", "прибрати повільне / DC", hp_shape, NEG),
        (pad_l, row2, "Смуговий", "лишити одну смугу", bp_shape, PURPLE),
        (col2,  row2, "Режекторний", "вирізати одну смугу", bs_shape, POS),
    ]
    for ox, oy, name, sub, fn, col in panels:
        top = oy - ph - 14
        axes(p, ox, oy, top, ox + pw + 8)
        p.append(shape_curve(ox, oy, pw, ph, fn, col, 2.4))
        p.append(text(ox, top + 2, name, size=12, color=col, anchor="start", bold=True))
        p.append(text(ox + pw, top + 2, sub, size=9, color=MUTED, anchor="end", italic=True))

    render(os.path.join(OUT, "four-shapes.svg"), W, H, *p,
           title="Чотири форми характеристики |H(f)|")


# ── lpf: ФНЧ у дії — сигнал зліва, характеристика справа ──────────────────────
# Ідея: ліворуч показати, що ФНЧ робить із сигналом (прибирає тремтіння),
# праворуч — форму характеристики, що це пояснює.

def fig_lpf():
    W, H = 720, 270
    p = []
    # ── ліва панель: сигнал у часі ──
    ox, oy, aw, ah = 50, 150, 360, 110
    axes(p, ox, oy - ah / 2 + ah, oy - ah / 2, ox + aw, "час")
    base_y = oy
    # повільна основа
    def base(t):
        return 22 * math.sin(2 * math.pi * t * 1.1)
    raw, sm = [], []
    for i in range(241):
        t = i / 240.0
        b = base(t)
        noise = 11 * math.sin(2 * math.pi * t * 17 + 1.0) + 7 * math.sin(2 * math.pi * t * 29)
        raw.append((ox + t * aw, base_y - (b + noise)))
        sm.append((ox + t * aw, base_y - b))
    p.append(polyline(raw, "#b9c4d6", 1.3))
    p.append(polyline(sm, FIELD, 2.4))
    p.append(text(ox, oy - ah / 2 - 6, "сирий шум → плавна основа", size=10, color=FIELD, anchor="start", bold=True))

    # ── права панель: характеристика ──
    bx, by, bw, bh = 470, 200, 210, 120
    axes(p, bx, by, by - bh - 8, bx + bw + 8, "частота")
    p.append(shape_curve(bx, by, bw, bh, lambda f: lp_shape(f, 0.4, 16), FIELD, 2.4))
    p.append(text(bx + 6, by - bh - 4, "пропускання внизу, спад угорі", size=9, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "lpf.svg"), W, H, *p,
           title="Низькочастотний: згладити, пропустити повільне")


# ── hpf: ФВЧ у дії — знімає повільний дрейф ───────────────────────────────────
# Ідея: сигнал їде на повзучій основі; ФВЧ повертає його на нуль, лишивши швидке.

def fig_hpf():
    W, H = 720, 270
    p = []
    ox, oy, aw, ah = 50, 150, 360, 110
    axes(p, ox, oy + ah / 2, oy - ah / 2 - 6, ox + aw, "час")
    zero = oy
    p.append(line(ox, zero, ox + aw, zero, color="#d8d8d8", sw=1.0, dash="4 3"))
    drift, out = [], []
    for i in range(241):
        t = i / 240.0
        d = 70 * t - 24                       # повільний дрейф угору
        fast = 16 * math.sin(2 * math.pi * t * 6.5)
        drift.append((ox + t * aw, zero - (d + fast)))
        out.append((ox + t * aw, zero - fast))
    p.append(polyline(drift, "#e08a3a", 2.0))
    p.append(polyline(out, NEG, 2.4))
    p.append(text(ox, oy - ah / 2 - 12, "сигнал на дрейфі → дрейф знято", size=10, color=NEG, anchor="start", bold=True))

    bx, by, bw, bh = 470, 200, 210, 120
    axes(p, bx, by, by - bh - 8, bx + bw + 8, "частота")
    p.append(shape_curve(bx, by, bw, bh, lambda f: hp_shape(f, 0.32, 16), NEG, 2.4))
    p.append(text(bx + 6, by - bh - 4, "нуль на 0 Гц, пропускання вгорі", size=9, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "hpf.svg"), W, H, *p,
           title="Високочастотний: зняти дрейф і постійне")


# ── bpf: смуговий — характеристика з f0, BW, Q ────────────────────────────────
# Ідея: одна крива-дзвін; підписати центр f0, ширину BW на рівні −3 дБ і звідки
# береться Q = f0/BW.

def fig_bpf():
    W, H = 720, 270
    p = []
    ox, oy, aw, ah = 70, 210, 580, 150
    axes(p, ox, oy, oy - ah - 8, ox + aw, "частота")

    f0, bw = 0.5, 0.14
    p.append(shape_curve(ox, oy, aw, ah, lambda f: bp_shape(f, f0, bw), PURPLE, 2.6))

    # рівень −3 дБ (0.707 від піку)
    lvl = 0.707
    y3 = oy - lvl * ah
    p.append(line(ox, y3, ox + aw - 30, y3, color="#caa24a", sw=1.0, dash="4 3"))
    p.append(text(ox - 6, y3 + 4, "−3 дБ", size=9, color="#9a7a1e", anchor="end"))

    # межі смуги на рівні −3 дБ: bp_shape = lvl → (f-f0)/bw = ±sqrt(-ln lvl)
    half = bw * math.sqrt(-math.log(lvl))
    xl = ox + (f0 - half) * aw
    xr = ox + (f0 + half) * aw
    xc = ox + f0 * aw
    for xx in (xl, xr):
        p.append(line(xx, oy, xx, y3, color="#cdbad6", sw=1.0, dash="3 3"))
    p.append(line(xc, oy, xc, oy - ah, color="#e0d3ea", sw=1.0, dash="3 3"))
    p.append(text(xc, oy + 16, "f₀", size=11, color=PURPLE, bold=True))
    # стрілка ширини BW
    p.append(arrow(xl, y3 - 14, xr, y3 - 14, color=PURPLE, sw=1.4))
    p.append(arrow(xr, y3 - 14, xl, y3 - 14, color=PURPLE, sw=1.4))
    p.append(text(xc, y3 - 20, "BW", size=10, color=PURPLE, bold=True))

    p.append(text(W / 2, H - 14, "вузька смуга = висока добротність Q = f₀/BW (гостріше, але дзвенить)",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "bpf.svg"), W, H, *p,
           title="Смуговий: лишити смугу навколо f₀")


# ── notch: режекторний — сигнал без гулу + характеристика з провалом ──────────
# Ідея: ліворуч сигнал із гулом 50 Гц очищається; праворуч характеристика —
# вузький провал точно на 50 Гц, решта проходить.

def fig_notch():
    W, H = 720, 270
    p = []
    # ── ліва панель: сигнал ──
    ox, oy, aw, ah = 50, 130, 360, 0
    p.append(line(ox, oy, ox + aw, oy, color="#e4e4e4", sw=1.0))
    raw, out = [], []
    for i in range(301):
        t = i / 300.0
        useful = 30 * math.sin(2 * math.pi * t * 2.0)
        hum = 16 * math.sin(2 * math.pi * t * 23)
        raw.append((ox + t * aw, oy - (useful + hum)))
        out.append((ox + t * aw, oy - useful))
    p.append(polyline(raw, "#e0b0b0", 1.3))
    p.append(polyline(out, FIELD, 2.2))
    p.append(text(ox + aw / 2, oy + 96, "з гулом → без гулу", size=10, color=FIELD, bold=True))

    # ── права панель: характеристика з провалом ──
    bx, by, bw, bh = 460, 200, 220, 120
    axes(p, bx, by, by - bh - 8, bx + bw + 8, "частота")
    f0 = 0.48
    p.append(shape_curve(bx, by, bw, bh, lambda f: bs_shape(f, f0, 0.045), POS, 2.4))
    xc = bx + f0 * bw
    p.append(line(xc, by, xc, by - bh, color="#e4e4e4", sw=1.0, dash="3 3"))
    p.append(text(xc, by + 16, "50 Гц", size=9, color=POS, bold=True))
    p.append(text(bx + 6, by - bh - 4, "вузький провал, решта ціла", size=9, color=POS, anchor="start", italic=True))

    render(os.path.join(OUT, "notch.svg"), W, H, *p,
           title="Режекторний (notch): вирізати гул 50 Гц")


# ── relations: усе виводиться з ФНЧ ───────────────────────────────────────────
# Ідея: три маленькі панно характеристик (ФВЧ, смуговий, режекторний) з підписом
# формули виведення з ФНЧ під кожним.

def fig_relations():
    W, H = 740, 280
    p = []
    pw, ph = 200, 110
    oy = 70 + ph
    cols = [40, 290, 540]
    items = [
        ("ФВЧ", "= 1 − ФНЧ", lambda f: hp_shape(f, 0.42, 14), NEG),
        ("смуговий", "= ФВЧ, тоді ФНЧ", lambda f: bp_shape(f, 0.5, 0.16), PURPLE),
        ("режекторний", "= 1 − смуговий", lambda f: bs_shape(f, 0.5, 0.06), POS),
    ]
    for ox, (name, formula, fn, col) in zip(cols, items):
        top = oy - ph - 14
        axes(p, ox, oy, top, ox + pw + 6)
        p.append(shape_curve(ox, oy, pw, ph, fn, col, 2.2))
        p.append(text(ox + pw / 2, top + 2, name, size=11, color=col, bold=True))
        p.append(text(ox + pw / 2, oy + 30, formula, size=10, color=MUTED, italic=True))

    p.append(text(W / 2, H - 14,
                  "опанувавши ФНЧ, маєте всі чотири типи — решта виводиться з нього",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "relations.svg"), W, H, *p,
           title="Усе виводиться з низькочастотного")


if __name__ == "__main__":
    fig_four_shapes()
    fig_lpf()
    fig_hpf()
    fig_bpf()
    fig_notch()
    fig_relations()
    print("OK: figures written to", OUT)
