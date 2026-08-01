# -*- coding: utf-8 -*-
"""Фігури для статті «Драбинковий ЦАП R-2R». Запуск із теки теми:  python figs.py
Виводить SVG у ./img/. Фігури про ПЕРЕТВОРЮВАЧ (не про саму мережу):
блок-схема, струмовий режим, передавальна характеристика з немонотонністю."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=15, pad=13, min_w=132, **kw):
    body, w, h = textbox(cx, cy, s, size=size, pad=pad, min_w=min_w, **kw)
    return body


def res_h(cx, cy, label, w=42, h=20):
    """Горизонтальний резистор-прямокутник із підписом над ним."""
    return (rect(cx - w / 2, cy - h / 2, w, h, fill="#eef2f7", rx=3) +
            text(cx, cy - h / 2 - 6, label, size=13, color=MUTED))


def res_v(cx, cy, label, w=20, h=42):
    """Вертикальний резистор-прямокутник із підписом праворуч."""
    return (rect(cx - w / 2, cy - h / 2, w, h, fill="#eef2f7", rx=3) +
            text(cx + w / 2 + 16, cy + 4, label, size=13, color=MUTED))


def gnd(cx, cy, s=9):
    """Символ землі."""
    return (line(cx, cy, cx, cy + s) +
            line(cx - 12, cy + s, cx + 12, cy + s, sw=2) +
            line(cx - 7, cy + s + 5, cx + 7, cy + s + 5, sw=2) +
            line(cx - 3, cy + s + 10, cx + 3, cy + s + 10, sw=2))


# ── Фігура 1: блок-схема перетворювача ──────────────────────────────────────
def fig_block():
    W, H = 960, 300
    cy = 128
    cxs = [200, 380, 560, 740]
    labels = ["Засувка\nкоду", "Ключі\nбітів", "Драбина\nR-2R", "Вихідний\nпідсилювач"]
    frags = []
    # вхід
    frags.append(mtext(64, cy - 6, ["цифровий", "код bₙ₋₁…b₀"], size=13, color=INK))
    frags.append(arrow(96, cy + 12, 132, cy + 12))
    # блоки + стрілки між ними
    edges = []
    for cx, lab in zip(cxs, labels):
        frags.append(box(cx, cy, lab, size=15, min_w=132))
        edges.append((cx - 66, cx + 66))
    for i in range(3):
        frags.append(arrow(edges[i][1] + 2, cy, edges[i + 1][0] - 2, cy))
    # вихід
    frags.append(arrow(edges[3][1] + 2, cy, edges[3][1] + 44, cy))
    frags.append(text(edges[3][1] + 78, cy + 5, "Vout", size=16, bold=True, color=FIELD))
    frags.append(text(edges[3][1] + 78, cy + 25, "(аналог)", size=12, color=MUTED))
    # Vref знизу в драбину
    vref_cy = 236
    frags.append(box(560, vref_cy, "Vref  (опора)", size=14, min_w=118, fill="#fdf6ec"))
    frags.append(arrow(560, vref_cy - 22, 560, cy + 30))
    frags.append(text(560, 288, "задає повну шкалу", size=12, color=MUTED))
    render(os.path.join(IMG, 'block.svg'), W, H, *frags)


# ── Фігура 2: струмовий (множильний) режим ──────────────────────────────────
def fig_current():
    W, H = 1040, 520
    rail = 118           # верхня шина
    sw_y = 250           # рівень ключів
    sum_y = 336          # підсумовувальна шина (віртуальна земля)
    gnd_y = 424          # шина землі
    nodes = [170, 360, 550]
    names = ["старший", "…", "молодший"]
    frags = []

    # Vref і верхня шина з резисторами R
    frags.append(text(60, rail - 26, "Vref", size=15, bold=True, color=INK))
    frags.append(circle(60, rail, 5, fill=INK, stroke=INK))
    frags.append(line(60, rail, nodes[0], rail, sw=2))
    seg_mid = [(60 + nodes[0]) / 2, (nodes[0] + nodes[1]) / 2, (nodes[1] + nodes[2]) / 2]
    frags.append(res_h(seg_mid[0], rail, "R"))
    frags.append(line(nodes[0], rail, nodes[1], rail, sw=2))
    frags.append(res_h(seg_mid[1], rail, "R"))
    frags.append(line(nodes[1], rail, nodes[2], rail, sw=2))
    frags.append(res_h(seg_mid[2], rail, "R"))
    # кінцевий термінатор
    term_x = nodes[2] + 120
    frags.append(line(nodes[2], rail, term_x, rail, sw=2))
    frags.append(res_v(term_x, (rail + gnd_y) / 2, "2R"))
    frags.append(line(term_x, rail, term_x, (rail + gnd_y) / 2 - 21, sw=2))
    frags.append(line(term_x, (rail + gnd_y) / 2 + 21, term_x, gnd_y, sw=2))

    # щаблі 2R + ключі
    for nx, nm in zip(nodes, names):
        frags.append(circle(nx, rail, 4, fill=INK, stroke=INK))
        frags.append(text(nx, rail - 24, nm, size=12, color=MUTED))
        frags.append(res_v(nx, (rail + sw_y) / 2, "2R"))
        frags.append(line(nx, rail, nx, (rail + sw_y) / 2 - 21, sw=2))
        frags.append(line(nx, (rail + sw_y) / 2 + 21, nx, sw_y, sw=2))
        # ключ: спільний вузол, два контакти (Σ ліворуч-вниз, земля праворуч-вниз)
        frags.append(circle(nx, sw_y, 4, fill=INK, stroke=INK))
        sigx, gx = nx - 18, nx + 18
        frags.append(circle(sigx, sw_y + 30, 3, fill=FILL, stroke=LINE))
        frags.append(circle(gx, sw_y + 30, 3, fill=FILL, stroke=LINE))
        # лезо на Σ (біт = 1)
        frags.append(line(nx, sw_y, sigx, sw_y + 27, color=FIELD, sw=2.4))
        # опускання Σ-контакту на підсумовувальну шину
        frags.append(line(sigx, sw_y + 30, sigx, sum_y, sw=1.6))
        # опускання земляного контакту на шину землі
        frags.append(line(gx, sw_y + 30, gx, gnd_y, sw=1.6, color=MUTED))

    # підсумовувальна шина → інвертувальний вхід ОП
    op_x, op_cy = 760, sum_y
    frags.append(line(nodes[0] - 18, sum_y, op_x, sum_y, sw=2, color=FIELD))
    frags.append(text(247, sum_y - 10, "Iout", size=13, bold=True, color=FIELD))
    # шина землі
    frags.append(line(nodes[0] + 18, gnd_y, term_x, gnd_y, sw=2, color=MUTED))
    frags.append(gnd(term_x, gnd_y))
    frags.append(text((nodes[0] + nodes[2]) / 2 + 18, gnd_y + 22, "шина землі", size=12, color=MUTED))

    # операційний підсилювач (трикутник)
    ax, ay = op_x, op_cy - 40
    frags.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f Z" fill="#f4f6f8" stroke="%s" stroke-width="1.6"/>'
                 % (ax, ay, ax, ay + 100, ax + 96, ay + 50, LINE))
    frags.append(text(ax + 14, sum_y - 6, "−", size=18, bold=True, color=NEG))
    frags.append(line(op_x, sum_y + 44, op_x - 26, sum_y + 44, sw=1.6))
    frags.append(text(ax + 14, sum_y + 50, "+", size=16, bold=True, color=POS))
    frags.append(gnd(op_x - 26, sum_y + 44))
    # вихід
    outx = ax + 96
    frags.append(line(outx, sum_y + 10, outx + 96, sum_y + 10, sw=2))
    frags.append(text(outx + 128, sum_y + 15, "Vout", size=16, bold=True, color=FIELD))
    frags.append(text(outx + 128, sum_y + 34, "= −Iout·Rfb", size=12, color=MUTED))
    # зворотний зв'язок Rfb: від − входу вгору-над-вниз до виходу
    fb_top = ay - 18
    frags.append(line(op_x - 4, sum_y, op_x - 4, fb_top, sw=1.6))
    frags.append(line(op_x - 4, fb_top, outx + 30, fb_top, sw=1.6))
    frags.append(res_h((op_x + outx + 26) / 2, fb_top, "Rfb"))
    frags.append(line(outx + 30, fb_top, outx + 30, sum_y + 10, sw=1.6))
    render(os.path.join(IMG, 'current-mode.svg'), W, H, *frags)


# ── Фігура 3: передавальна характеристика з немонотонністю ───────────────────
def fig_transfer():
    W, H = 780, 560
    x0, y0 = 96, 468      # початок координат
    xr, yt = 690, 92      # праворуч / вгору
    frags = []
    # осі
    frags.append(arrow(x0, y0, xr + 8, y0))
    frags.append(arrow(x0, y0, x0, yt - 8))
    frags.append(text(xr - 4, y0 + 30, "код", size=14, color=INK))
    frags.append(text(x0 - 6, yt - 18, "Vout", size=14, bold=True, color=INK))
    # позначки шкали
    frags.append(line(x0 + (xr - x0) / 2, y0, x0 + (xr - x0) / 2, y0 + 6, sw=1.5))
    frags.append(text(x0 + (xr - x0) / 2, y0 + 26, "½ шкали", size=12, color=MUTED))
    frags.append(text(x0 - 20, y0 + 5, "0", size=12, color=MUTED))
    frags.append(line(x0 - 6, yt + 6, x0, yt + 6, sw=1.5))
    frags.append(text(x0 - 26, yt + 11, "Vref", size=12, color=MUTED))

    # ідеальна пряма
    frags.append(line(x0, y0, xr, yt + 6, color=NEG, sw=1.4, dash="6 5"))
    frags.append(text(xr - 96, yt + 40, "ідеал: Vref·код/2ᴺ", size=12, color=NEG))

    # сходинки: 8 видимих; одна посеред шкали йде ВНИЗ (немонотонність)
    N = 8
    sw_w = (xr - x0) / N
    full = y0 - (yt + 6)
    treads = [y0 - full * k / N for k in range(N)]
    treads[4] = treads[3] + 26           # провал: код 4 нижчий за код 3
    px, py = x0, treads[0]
    for k in range(N):
        tx0 = x0 + sw_w * k
        tx1 = tx0 + sw_w
        ty = treads[k]
        # підйомник від попереднього рівня
        frags.append(line(tx0, py, tx0, ty, color=INK, sw=2.2))
        # площадка
        frags.append(line(tx0, ty, tx1, ty, color=INK, sw=2.2))
        py = ty
    # виділити провал
    dip_x = x0 + sw_w * 4 + sw_w / 2
    dip_y = treads[4]
    frags.append('<circle cx="%.0f" cy="%.0f" r="30" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4 4"/>'
                 % (x0 + sw_w * 4, (treads[3] + treads[4]) / 2, POS))
    # підпис із виноскою праворуч, з відступом
    lx, ly = x0 + sw_w * 4 + 70, 150
    frags.append(box(lx + 96, ly, "код зріс —\nнапруга впала:\nнемонотонність", size=13,
                     min_w=176, fill="#fdecea", stroke=POS))
    frags.append(line(x0 + sw_w * 4 + 30, (treads[3] + treads[4]) / 2, lx + 20, ly + 20, color=POS, sw=1.4))
    render(os.path.join(IMG, 'transfer.svg'), W, H, *frags)


# ── Точний розв'язок драбини (для фігур вставки math-inl-dnl-mismatch) ──────
def _solve(N, legs, ser, term):
    """Струмовий режим: жорстка Vref=1 у вузлі 1 (старший), низи плечей на 0 В.
    Повертає ваги бітів w[0..N-1] (w[0] — молодший)."""
    Z = [0.0] * (N + 1)
    Z[N] = legs[N - 1] * term / (legs[N - 1] + term)
    for j in range(N - 1, 0, -1):
        r = ser[j - 1] + Z[j + 1]
        Z[j] = legs[j - 1] * r / (legs[j - 1] + r)
    V = [0.0] * (N + 1)
    V[1] = 1.0
    for j in range(1, N):
        V[j + 1] = V[j] * Z[j + 1] / (ser[j - 1] + Z[j + 1])
    w = [0.0] * N
    for j in range(1, N + 1):
        w[N - j] = V[j] / legs[j - 1]
    return w


def _dnl(N, w):
    out = [sum(w[k] for k in range(N) if (D >> k) & 1) for D in range(2 ** N)]
    lsb = (out[-1] - out[0]) / (2 ** N - 1)
    inl = [(out[D] - out[0]) / lsb - D for D in range(2 ** N)]
    return [inl[D + 1] - inl[D] for D in range(2 ** N - 1)]


# ── Фігура 4: плече очима Тевеніна — звідки береться чутливість ──────────────
def fig_leg_thevenin():
    W, H = 1020, 500
    frags = []
    rail, legy, gy = 128, 226, 300

    # ── ліворуч: шматок драбини з виділеним плечем
    frags.append(text(232, 56, "плече біта m у драбині", size=15, bold=True))
    nx = 232
    frags.append(line(76, rail, 388, rail, sw=2))
    frags.append(res_h(148, rail, "R"))
    frags.append(res_h(316, rail, "R"))
    frags.append(circle(nx, rail, 4.5, fill=INK, stroke=INK))
    frags.append(text(76, rail - 34, "до Vref", size=13, color=MUTED, anchor="start"))
    frags.append(text(388, rail - 34, "далі вниз", size=13, color=MUTED, anchor="end"))
    frags.append(line(nx, rail, nx, legy - 21, sw=2))
    frags.append(res_v(nx, legy, "2R(1+δ)"))
    frags.append(line(nx, legy + 21, nx, gy, sw=2))
    frags.append(gnd(nx, gy))
    frags.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="none" '
                 'stroke="%s" stroke-width="1.8" stroke-dasharray="6 5"/>'
                 % (nx - 62, legy - 44, 124, 88, POS))

    # ── стрілка переходу
    frags.append(arrow(430, legy - 10, 512, legy - 10))
    frags.append(text(471, legy - 24, "Тевенін", size=13, color=MUTED))

    # ── праворуч: еквівалентний контур
    frags.append(text(760, 56, "усе інше — джерело Vₜ і опір Rₜ", size=15, bold=True))
    lx, rx2 = 596, 848
    frags.append(circle(lx, legy, 22, fill="#fdf6ec", stroke=LINE))
    frags.append(text(lx, legy + 5, "Vₜ", size=15, bold=True))
    frags.append(line(lx, legy - 22, lx, rail, sw=2))
    frags.append(line(lx, rail, rx2, rail, sw=2))
    frags.append(res_h((lx + rx2) / 2, rail, "Rₜ"))
    frags.append(line(rx2, rail, rx2, legy - 21, sw=2))
    frags.append(res_v(rx2, legy, "2R(1+δ)"))
    frags.append(line(rx2, legy + 21, rx2, gy, sw=2))
    frags.append(line(lx, legy + 22, lx, gy, sw=2))
    frags.append(line(lx, gy, rx2, gy, sw=2))
    frags.append(gnd((lx + rx2) / 2, gy))
    frags.append(text((lx + rx2) / 2, legy - 44, "I = Vₜ / (Rₜ + 2R(1+δ))", size=15, bold=True, color=FIELD))

    # ── низ: як Rₜ і чутливість залежать від глибини щабля
    rows = [("щабель 1\n(старший)", "Rₜ = 0", "S = −1"),
            ("щабель 2", "Rₜ = 2R/3", "S = −3/4"),
            ("щабель 3", "Rₜ = 10R/11", "S = −11/16"),
            ("глибокі", "Rₜ → R", "S → −2/3")]
    cx0, step = 168, 228
    frags.append(text(W / 2, 384, "S = ∂(відносна зміна струму плеча) / ∂δ  =  −2R / (Rₜ + 2R)",
                      size=14, color=MUTED))
    for i, (a, b, c) in enumerate(rows):
        cx = cx0 + i * step
        frags.append(textbox(cx, 442, [a.replace("\n", " "), b + "   →   " + c],
                             size=13, min_w=196, fill="#f4f6f8")[0])
    render(os.path.join(IMG, 'math-leg-thevenin.svg'), W, H, *frags)


# ── Фігура 5: вплив кожного елемента на DNL середини шкали ───────────────────
def fig_influence():
    W, H = 1040, 430
    rail, legy, gy = 150, 244, 312
    frags = []
    nodes = [214, 366, 518, 670]
    frags.append(text(120, rail - 44, "Vref", size=15, bold=True))
    frags.append(circle(120, rail, 5, fill=INK, stroke=INK))
    frags.append(line(120, rail, 822, rail, sw=2))
    # послідовні R і їхній вплив (над шиною)
    ser_infl = ["+2ᴺ⁻²", "+2ᴺ⁻⁴", "+2ᴺ⁻⁶"]
    for i in range(3):
        mid = (nodes[i] + nodes[i + 1]) / 2
        frags.append(res_h(mid, rail, "R"))
        frags.append(text(mid, rail - 40, ser_infl[i], size=14, bold=True, color=NEG))
    # плечі і їхній вплив (під землею)
    leg_infl = ["−2ᴺ⁻¹", "+2ᴺ⁻³", "+2ᴺ⁻⁵", "+2ᴺ⁻⁷"]
    leg_col = [POS, NEG, NEG, NEG]
    for nx, lab, col in zip(nodes, leg_infl, leg_col):
        frags.append(circle(nx, rail, 4.5, fill=INK, stroke=INK))
        frags.append(line(nx, rail, nx, legy - 21, sw=2))
        frags.append(res_v(nx, legy, "2R"))
        frags.append(line(nx, legy + 21, nx, gy, sw=2))
        frags.append(text(nx, gy + 30, lab, size=14, bold=True, color=col))
    frags.append(line(nodes[0], gy, 822, gy, sw=2, color=MUTED))
    frags.append(gnd((nodes[0] + 822) / 2, gy))
    # хвіст драбини
    frags.append(text(760, rail - 40, "…", size=20, color=MUTED))
    frags.append(line(822, rail, 822, legy - 21, sw=2))
    frags.append(res_v(822, legy, "2R"))
    frags.append(line(822, legy + 21, 822, gy, sw=2))
    frags.append(text(822, gy + 30, "≈0", size=14, bold=True, color=MUTED))
    frags.append(text(214, rail - 74, "старший біт", size=13, color=MUTED))
    frags.append(text(822, rail - 40, "кінцевий", size=13, color=MUTED))
    # підсумок
    frags.append(textbox(W / 2, 396,
                         ["сума модулів усіх впливів ≈ 2ᴺ   ⇒   кожен опір мусить тримати відношення краще за 2⁻ᴺ"],
                         size=15, bold=True, fill="#eafaf1", stroke=FIELD, min_w=880)[0])
    frags.append(text(W / 2, 46, "у скільки разів похибка елемента множиться в DNL середини шкали",
                      size=15, bold=True))
    render(os.path.join(IMG, 'math-influence.svg'), W, H, *frags)


# ── Фігура 6: DNL по кодах — сплески сидять на переносах ─────────────────────
def fig_dnl_spikes():
    N = 8
    # фіксований набір розбіжностей (у відсотках), σ ≈ 0.6 %
    dl = [0.732, 0.581, -0.823, -1.163, -0.061, 0.457, -0.088, -0.875]
    ds = [-0.298, 0.861, -0.829, 0.629, 0.314, 0.289, 0.460]
    dt = -0.328
    legs = [2.0 * (1 + x / 100.0) for x in dl]
    ser = [1.0 * (1 + x / 100.0) for x in ds]
    term = 2.0 * (1 + dt / 100.0)
    dn = _dnl(N, _solve(N, legs, ser, term))

    W, H = 1020, 560
    x0, x1 = 108, 962
    ytop, ybot = 176, 466          # +0.35 ... -1.15 LSB
    vmax, vmin = 0.35, -1.15
    def px(code): return x0 + (x1 - x0) * code / 255.0
    def py(v): return ytop + (ybot - ytop) * (vmax - v) / (vmax - vmin)
    frags = []
    # осі
    frags.append(line(x0, ytop - 8, x0, ybot + 8, color=LINE, sw=1.5))
    frags.append(line(x0 - 8, py(0), x1 + 10, py(0), color=LINE, sw=1.5))
    frags.append(text(x1 + 10, py(0) - 12, "код", size=14, anchor="end"))
    frags.append(text(x0 - 14, ytop - 18, "DNL, LSB", size=14, bold=True, anchor="start"))
    for v in [0.25, 0.0, -0.25, -0.5, -0.75, -1.0]:
        frags.append(line(x0 - 6, py(v), x0, py(v), sw=1.4))
        frags.append(text(x0 - 14, py(v) + 5, ("%+.2f" % v) if v else "0", size=12,
                          color=MUTED, anchor="end"))
    for c in [0, 64, 128, 192, 255]:          # мітки кодів — під полем, щоб їх не перетинали стовпчики
        frags.append(line(px(c), ybot, px(c), ybot + 7, sw=1.4))
        frags.append(text(px(c), ybot + 24, str(c), size=12, color=MUTED))
    # межа монотонності
    frags.append(line(x0, py(-1), x1, py(-1), color=POS, sw=1.6, dash="7 5"))
    frags.append(text(x1, py(-1) + 24, "DNL = −1: крок обертається назад", size=13,
                      color=POS, anchor="end"))
    # стовпчики DNL
    for c, v in enumerate(dn):
        if abs(v) < 1e-4:
            continue
        col = POS if v < -0.02 else (NEG if v > 0.02 else MUTED)
        frags.append(line(px(c + 0.5), py(0), px(c + 0.5), py(v), color=col, sw=2.0))
    # виноски у верхній смузі; короткі виводи в порожній простір
    frags.append(textbox(px(128), 96, ["перенос через середину шкали:", "проти старшого щабля вимикається",
                                       "вся молодша половина"],
                         size=13, min_w=336, fill="#fdecea", stroke=POS)[0])
    frags.append(line(px(128), 136, px(128), py(0) - 16, color=POS, sw=1.4))
    frags.append(textbox(858, 350, ["той самий перенос —", "той самий сплеск"],
                         size=13, min_w=268, fill="#eaf0fd", stroke=NEG)[0])
    frags.append(line(790, 342, px(192) + 5, py(-0.30), color=NEG, sw=1.4))
    frags.append(text(W / 2, 528,
                      "восьмибітна драбина, розбіжність плечей σ ≈ 0.6 %: поза переносами DNL майже нульова",
                      size=13, color=MUTED))
    render(os.path.join(IMG, 'math-dnl-spikes.svg'), W, H, *frags)


# ── Фігура: драбина на ніжках GPIO (вставка proj-gpio-r2r) ──────────────────
def fig_gpio_ladder():
    W, H = 1220, 610
    rail = 356           # горизонтальна шина драбини
    pin_y = 168          # нижній край корпусу — рівень ніжок
    gnd_y = 500
    nodes = [268, 442, 616, 790]
    names = ["b0 (мол.)", "b1", "…", "b7 (стар.)"]
    pins = ["PA0", "PA1", "…", "PA7"]
    term_x = 128
    frags = []

    # корпус мікроконтролера
    frags.append(rect(96, 66, 760, 96, fill="#eef2f7"))
    frags.append(mtext(476, 104, ["Мікроконтролер: вісім ніжок ОДНІЄЇ групи порту,",
                                  "усі перемикаються одним записом у регістр"], size=15))

    # вертикальні плечі 2R = R + R
    for nx, nm, pn in zip(nodes, names, pins):
        frags.append(line(nx, pin_y, nx, pin_y + 26, sw=2))
        frags.append(text(nx - 42, pin_y + 22, pn, size=13, color=MUTED))
        frags.append(res_v(nx, pin_y + 54, "R"))
        frags.append(line(nx, pin_y + 75, nx, pin_y + 118, sw=2))
        frags.append(res_v(nx, pin_y + 139, "R"))
        frags.append(line(nx, pin_y + 160, nx, rail, sw=2))
        frags.append(circle(nx, rail, 4, fill=INK, stroke=INK))
        frags.append(text(nx, rail + 34, nm, size=13, color=MUTED))

    # дужка «2R = R + R» ліворуч від першого плеча
    bx = nodes[0] - 92
    frags.append(line(bx, pin_y + 32, bx, pin_y + 182, color=FIELD, sw=1.6))
    frags.append(line(bx, pin_y + 32, bx + 14, pin_y + 32, color=FIELD, sw=1.6))
    frags.append(line(bx, pin_y + 182, bx + 14, pin_y + 182, color=FIELD, sw=1.6))
    frags.append(mtext(bx - 54, pin_y + 84, ["2R — це", "два R того", "самого", "номіналу"],
                       size=13, color=FIELD))

    # горизонтальна шина R між вузлами
    frags.append(line(term_x, rail, nodes[0], rail, sw=2))
    frags.append(res_h((term_x + nodes[0]) / 2, rail, "R"))
    for a, b in zip(nodes, nodes[1:]):
        frags.append(line(a, rail, b, rail, sw=2))
        frags.append(res_h((a + b) / 2, rail, "R"))

    # термінатор 2R на землю
    frags.append(line(term_x, rail, term_x, rail + 32, sw=2))
    frags.append(res_v(term_x, rail + 53, "2R"))
    frags.append(line(term_x, rail + 74, term_x, gnd_y, sw=2))
    frags.append(gnd(term_x, gnd_y))
    frags.append(mtext(term_x - 6, rail + 138, ["термінатор:", "цей 2R —", "просто на землю"],
                       size=12, color=MUTED))

    # вихід драбини → повторювач
    ox = nodes[-1]
    ax = 930
    frags.append(line(ox, rail, ax, rail, sw=2, color=FIELD))
    frags.append(text((ox + ax) / 2, rail - 16, "Zвих = R", size=13, color=FIELD))
    frags.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f Z" fill="#f4f6f8" stroke="%s" stroke-width="1.6"/>'
                 % (ax, rail - 52, ax, rail + 52, ax + 92, rail, LINE))
    frags.append(text(ax + 16, rail + 5, "+", size=17, bold=True, color=POS))
    frags.append(text(ax + 16, rail + 46, "−", size=17, bold=True, color=NEG))
    frags.append(line(ax, rail + 40, ax - 32, rail + 40, sw=1.6))
    frags.append(line(ax - 32, rail + 40, ax - 32, rail + 104, sw=1.6))
    outx = ax + 92
    frags.append(line(outx, rail, outx + 130, rail, sw=2))
    frags.append(line(ax - 32, rail + 104, outx + 40, rail + 104, sw=1.6))
    frags.append(line(outx + 40, rail + 104, outx + 40, rail, sw=1.6))
    frags.append(text(outx + 158, rail + 6, "Vout", size=16, bold=True, color=FIELD))
    frags.append(mtext(ax + 40, rail + 148, ["повторювач: віддає", "струм навантаженню"],
                       size=13, color=MUTED))
    render(os.path.join(IMG, 'gpio-ladder.svg'), W, H, *frags)


# ── Фігура: ланцюг драйвера (таблиця + накопичувач фази) ────────────────────
def fig_dds_chain():
    W, H = 1260, 470
    y1, y2 = 122, 314
    frags = []
    top = [("Таймер\nперервання рівно\nкожні 1/fs", 190),
           ("Накопичувач фази\nacc += M\n(32 біти)", 560),
           ("Індекс таблиці\ni = acc >> 24\n(старші 8 бітів)", 930)]
    bot = [("Таблиця 256 слів\nготове слово BSRR", 930),
           ("Один 32-бітний запис\nGPIOA→BSRR = tab[i]", 560),
           ("Драбина R-2R\nаналоговий рівень", 190)]
    halfs = {}
    for txt, cx in top:
        b, w, h = textbox(cx, y1, txt, size=14, pad=14, min_w=290)
        frags.append(b); halfs[(cx, y1)] = w / 2
    for txt, cx in bot:
        b, w, h = textbox(cx, y2, txt, size=14, pad=14, min_w=290,
                          fill="#eef7f0", stroke=FIELD)
        frags.append(b); halfs[(cx, y2)] = w / 2
    for (t1, x1), (t2, x2) in zip(top, top[1:]):
        frags.append(arrow(x1 + halfs[(x1, y1)] + 4, y1, x2 - halfs[(x2, y1)] - 4, y1))
    for (t1, x1), (t2, x2) in zip(bot, bot[1:]):
        frags.append(arrow(x1 - halfs[(x1, y2)] - 4, y2, x2 + halfs[(x2, y2)] + 4, y2))
    frags.append(arrow(930, y1 + 52, 930, y2 - 46))          # перехід у нижній ряд
    frags.append(arrow(190 - halfs[(190, y2)] - 4, y2, 76, y2))
    frags.append(text(62, y2 + 32, "Vout", size=15, bold=True, color=FIELD))
    frags.append(text(560, 206, "крок сітки частот Δf = fs / 2³²", size=13, color=MUTED))
    frags.append(mtext(956, 214, ["решта 24 бітів фази", "не гине — копиться далі"],
                       size=13, color=MUTED, anchor="start"))
    frags.append(text(560, y2 + 76, "усі вісім бітів міняються разом — проміжних комбінацій немає",
                      size=13, color=MUTED))
    frags.append(text(W / 2, 428,
                      "у перериванні лишається три дії: додати, зсунути, записати",
                      size=14, bold=True, color=INK))
    render(os.path.join(IMG, 'dds-chain.svg'), W, H, *frags)


# ── Фігура: скільки розрядів витримує Ron ніжки ─────────────────────────────
def fig_ron_ceiling():
    import math
    W, H = 900, 580
    x0, y0, xr, yt = 150, 462, 812, 96
    frags = []
    Ns = list(range(6, 15))
    d20 = [0.0472, 0.0996, 0.2054, 0.4177, 0.8432, 1.6949, 3.3993, 6.8090, 13.6291]
    d94 = [0.0100, 0.0212, 0.0437, 0.0889, 0.1795, 0.3609, 0.7237, 1.4497, 2.9017]
    lo, hi = -2.25, 1.4                       # межі log10(DNL)

    def X(n):
        return x0 + (xr - x0) * (n - Ns[0]) / (Ns[-1] - Ns[0])

    def Y(v):
        return y0 - (y0 - yt) * (math.log10(v) - lo) / (hi - lo)

    for dec, lab in ((0.01, "0.01"), (0.1, "0.1"), (1.0, "1"), (10.0, "10")):
        frags.append(line(x0, Y(dec), xr, Y(dec), color="#dfe4ea", sw=1))
        frags.append(text(x0 - 28, Y(dec) + 5, lab, size=12, color=MUTED))
    frags.append(arrow(x0, y0, xr + 14, y0))
    frags.append(arrow(x0, y0, x0, yt - 14))
    frags.append(text(xr - 30, y0 + 36, "розрядів N", size=14))
    frags.append(mtext(x0 + 4, yt - 46, ["|DNL| на середині шкали, LSB"], size=13))
    for n in Ns:
        frags.append(line(X(n), y0, X(n), y0 + 6, sw=1.4))
        frags.append(text(X(n), y0 + 24, str(n), size=12, color=MUTED))

    frags.append(line(x0, Y(1.0), xr, Y(1.0), color=POS, sw=1.8, dash="7 5"))
    frags.append(text(x0 + 172, Y(1.0) - 12, "1 LSB — межа монотонності", size=13, color=POS))

    def poly(vals, color):
        out = []
        pts = list(zip(Ns, vals))
        for a, b in zip(pts, pts[1:]):
            out.append(line(X(a[0]), Y(a[1]), X(b[0]), Y(b[1]), color=color, sw=2.4))
        for n, v in pts:
            out.append(circle(X(n), Y(v), 4, fill=color, stroke=color))
        return out
    frags += poly(d20, NEG)
    frags += poly(d94, FIELD)
    frags.append(text(X(8) + 4, Y(d20[2]) - 22, "2R = 20 кΩ", size=14, bold=True, color=NEG))
    frags.append(text(X(12) - 20, Y(d94[6]) + 34, "2R = 94 кΩ", size=14, bold=True, color=FIELD))
    frags.append(text((x0 + xr) / 2, H - 22,
                      "Ron ніжки = 50 Ω, резистори драбини ідеальні", size=13, color=MUTED))
    render(os.path.join(IMG, 'ron-ceiling.svg'), W, H, *frags)


# ── Фігури вставки comp-multiplying-dac ─────────────────────────────────────
def c_amp(x_left, y_top, y_bot, apex_x, label="", inv_y=None, ni_y=None):
    """Трикутник ОП вістрям праворуч + позначки входів."""
    cy = (y_top + y_bot) / 2
    f = ['<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f Z" fill="#f4f6f8" '
         'stroke="%s" stroke-width="1.6"/>' % (x_left, y_top, x_left, y_bot, apex_x, cy, LINE)]
    if inv_y is not None:
        f.append(text(x_left + 16, inv_y + 6, "−", size=18, bold=True, color=NEG))
    if ni_y is not None:
        f.append(text(x_left + 16, ni_y + 5, "+", size=16, bold=True, color=POS))
    if label:
        f.append(text(x_left + 48, cy + 5, label, size=14, bold=True, color=MUTED))
    return "".join(f)


def c_cap(cx, cy, gap=9, half=13):
    """Конденсатор у горизонтальному проводі (дві вертикальні пластини)."""
    return (line(cx - gap, cy - half, cx - gap, cy + half, sw=2.2, color=NEG) +
            line(cx + gap, cy - half, cx + gap, cy + half, sw=2.2, color=NEG))


def c_res_v(cx, cy, label, w=20, h=42, lab_dx=-26):
    """Вертикальний резистор із підписом ЛІВОРУЧ (щоб не лізти на край корпусу)."""
    return (rect(cx - w / 2, cy - h / 2, w, h, fill="#eef2f7", rx=3) +
            text(cx + lab_dx, cy + 5, label, size=13, color=MUTED, anchor="end"))


# ── Фігура: що всередині корпусу множильного ЦАП і що на виводах ────────────
def fig_comp_inside():
    W, H = 1200, 570
    cx0, cy0, cw, ch = 320, 100, 440, 380
    frags = [text(540, 62, "що всередині корпусу — і чого в ньому немає", size=15, bold=True)]
    frags.append(rect(cx0, cy0, cw, ch, fill="#fbfcfd", stroke=LINE, sw=2, rx=10))

    # внутрішні блоки
    frags.append(box(540, 180, "Драбина R-2R", size=15, min_w=320))
    frags.append(box(540, 300, "Ключі бітів (двонапрямні)", size=15, min_w=320))
    frags.append(box(540, 415, "Інтерфейс, засувка коду\nі подвійна буферизація", size=14, min_w=320))
    frags.append(arrow(540, 202, 540, 277))
    frags.append(arrow(540, 386, 540, 325))

    # праві (аналогові) виводи
    def pin_r(y, name, x_from):
        return (line(x_from, y, 820, y, sw=1.8) +
                text(832, y + 5, name, size=13, anchor="start", color=INK))
    frags.append(pin_r(180, "VREF", 700))
    frags.append(pin_r(284, "IOUT1", 700))
    frags.append(pin_r(316, "IOUT2", 700))
    frags.append(pin_r(452, "AGND", 700))
    # Rfb: від вузла IOUT1 всередині корпусу до виводу RFB
    frags.append(circle(740, 284, 4, fill=INK, stroke=INK))
    frags.append(line(740, 284, 740, 329, sw=1.8))
    frags.append(c_res_v(740, 350, "Rfb ≈ R"))
    frags.append(line(740, 371, 740, 396, sw=1.8))
    frags.append(line(740, 396, 820, 396, sw=1.8))
    frags.append(text(832, 401, "RFB", size=13, anchor="start", color=INK))

    # ліві (цифрові) виводи
    frags.append(line(220, 140, 320, 140, sw=1.8))
    frags.append(text(208, 145, "VDD", size=13, anchor="end", color=INK))
    frags.append(line(220, 180, 320, 180, sw=1.8))
    frags.append(text(208, 185, "DGND", size=13, anchor="end", color=INK))
    for yy in (400, 415, 430):
        frags.append(line(220, yy, 380, yy, sw=1.6))
    frags.append(mtext(208, 400, ["SCLK", "SDI", "SYNC"], size=13, anchor="end", color=INK))
    frags.append(line(220, 462, 380, 462, sw=1.8))
    frags.append(text(208, 467, "LDAC", size=13, anchor="end", color=INK))

    # чого немає
    frags.append(box(1040, 290, "у корпусі НЕМА\nпідсилювача:\nструмовий вихід\nперетворюєте ви",
                     size=13, min_w=250, fill="#fdecea", stroke=POS))
    render(os.path.join(IMG, 'comp-mdac-inside.svg'), W, H, *frags)


# ── Фігура: двоквадрантна обв'язка ──────────────────────────────────────────
def fig_comp_wiring():
    W, H = 1100, 500
    frags = [text(550, 44, "двоквадрантна обв'язка: усе, що треба зовні", size=15, bold=True)]
    # корпус
    frags.append(rect(160, 130, 290, 250, fill="#fbfcfd", stroke=LINE, sw=2, rx=10))
    frags.append(mtext(305, 240, ["множильний ЦАП", "(драбина + ключі + Rfb)"], size=14, color=INK))
    # Vref ліворуч
    frags.append(circle(60, 190, 5, fill=INK, stroke=INK))
    frags.append(line(60, 190, 160, 190, sw=2))
    frags.append(text(60, 174, "Vref", size=14, bold=True))
    frags.append(mtext(72, 218, ["стала напруга", "або сигнал"], size=12, color=MUTED))
    frags.append(text(175, 180, "VREF", size=12, anchor="start", color=MUTED))
    # праві виводи
    frags.append(line(450, 175, 800, 175, sw=1.8))
    frags.append(text(462, 165, "RFB", size=12, anchor="start", color=MUTED))
    frags.append(line(450, 220, 620, 220, sw=1.8, color=FIELD))
    frags.append(text(462, 210, "IOUT1", size=12, anchor="start", color=MUTED))
    frags.append(line(450, 300, 540, 300, sw=1.8))
    frags.append(text(462, 290, "IOUT2", size=12, anchor="start", color=MUTED))
    frags.append(gnd(540, 300))
    frags.append(line(450, 350, 540, 350, sw=1.8))
    frags.append(text(462, 340, "AGND", size=12, anchor="start", color=MUTED))
    frags.append(gnd(540, 350))
    # підсилювач
    frags.append(c_amp(620, 160, 340, 716, inv_y=220, ni_y=280))
    frags.append(line(620, 280, 590, 280, sw=1.8))
    frags.append(gnd(590, 280))
    # вихід і зворотний зв'язок через внутрішній Rfb
    frags.append(line(716, 250, 900, 250, sw=2))
    frags.append(circle(800, 250, 4, fill=INK, stroke=INK))
    frags.append(line(800, 175, 800, 250, sw=1.8))
    frags.append(circle(800, 175, 4, fill=INK, stroke=INK))
    frags.append(text(940, 246, "Vout", size=16, bold=True, color=FIELD))
    frags.append(text(940, 272, "= −Vref·D/2ᴺ", size=13, color=MUTED))
    # Cf зовні
    frags.append(circle(560, 220, 4, fill=INK, stroke=INK))
    frags.append(line(560, 220, 560, 110, sw=1.6, color=NEG))
    frags.append(line(560, 110, 671, 110, sw=1.6, color=NEG))
    frags.append(c_cap(680, 110))
    frags.append(line(689, 110, 800, 110, sw=1.6, color=NEG))
    frags.append(line(800, 110, 800, 175, sw=1.6, color=NEG))
    frags.append(text(680, 86, "Cf", size=14, bold=True, color=NEG))
    # примітки
    frags.append(box(280, 450, "IOUT2 і AGND — на землю опори, однією точкою",
                     size=13, min_w=400, fill="#f4f6f8"))
    frags.append(box(830, 450, "резистора зв'язку зовні немає:\nце внутрішній Rfb",
                     size=13, min_w=330, fill="#eafaf1", stroke=FIELD))
    render(os.path.join(IMG, 'comp-mdac-wiring.svg'), W, H, *frags)


# ── Фігура: чотири квадранти другим підсилювачем ────────────────────────────
def fig_comp_4q():
    W, H = 1060, 440
    frags = [text(530, 40, "чотири квадранти: другий підсилювач подвоює і віднімає Vref",
                  size=15, bold=True)]
    # джерело V1
    frags.append(box(180, 170, "ЦАП + A1\nV₁ = −Vref·D/2ᴺ", size=14, min_w=220))
    frags.append(line(290, 170, 390, 170, sw=1.8))
    frags.append(res_h(340, 170, "R"))
    # гілка Vref
    frags.append(circle(215, 290, 5, fill=INK, stroke=INK))
    frags.append(text(178, 295, "Vref", size=14, bold=True, anchor="end"))
    frags.append(line(215, 290, 390, 290, sw=1.8))
    frags.append(res_h(300, 290, "2R"))
    frags.append(line(390, 290, 390, 170, sw=1.8))
    frags.append(circle(390, 170, 4, fill=INK, stroke=INK))
    frags.append(line(390, 170, 470, 170, sw=1.8))
    # A2
    frags.append(c_amp(470, 130, 290, 566, label="A2", inv_y=170, ni_y=250))
    frags.append(line(470, 250, 430, 250, sw=1.8))
    frags.append(gnd(430, 250))
    # зворотний зв'язок 2R
    frags.append(circle(455, 170, 4, fill=INK, stroke=INK))
    frags.append(line(455, 170, 455, 95, sw=1.8))
    frags.append(line(455, 95, 700, 95, sw=1.8))
    frags.append(res_h(577, 95, "2R"))
    frags.append(line(700, 95, 700, 210, sw=1.8))
    # вихід
    frags.append(line(566, 210, 820, 210, sw=2))
    frags.append(circle(700, 210, 4, fill=INK, stroke=INK))
    frags.append(mtext(900, 196, ["Vout =", "Vref·(2D/2ᴺ − 1)"], size=14, color=FIELD))
    # примітки
    frags.append(box(190, 82, "зовнішні R і 2R:\nвідношення тримати\nкраще за 1/2ᴺ⁻¹",
                     size=13, min_w=230, fill="#fdecea", stroke=POS))
    frags.append(box(530, 390, "код 0 → −Vref     ·     півшкали → 0     ·     повний код → +Vref",
                     size=14, min_w=580, fill="#eafaf1", stroke=FIELD))
    render(os.path.join(IMG, 'comp-mdac-4q.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_block()
    fig_current()
    fig_transfer()
    fig_gpio_ladder()
    fig_dds_chain()
    fig_ron_ceiling()
    fig_leg_thevenin()
    fig_influence()
    fig_dnl_spikes()
    fig_comp_inside()
    fig_comp_wiring()
    fig_comp_4q()
    print("OK: + gpio-ladder.svg, dds-chain.svg, ron-ceiling.svg,",
          "comp-mdac-inside.svg, comp-mdac-wiring.svg, comp-mdac-4q.svg ->", IMG)
