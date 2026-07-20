# -*- coding: utf-8 -*-
"""Фігури до теми «Тертя».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

PUSH = "#c0392b"   # зовнішня сила / натиск — гаряче червоне
FRIC = "#2457d6"   # сила тертя — холодне синє
WT   = "#27ae60"   # вага / складові — зелене
GRIP = "#c0392b"   # чіпко
SLIP = "#2457d6"   # ковзко


def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, fill, stroke, sw, da))


def poly(pts, fill="none", stroke=LINE, sw=1.5, dash=None, close=False):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    if close:
        d += " Z"
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, stroke, sw, da)


# ── Фігура 1: звідки береться тертя — виступи й реальна площа контакту ────────
def fig_friction_origin():
    W, H = 940, 470
    f = [text(W / 2, 30, "Поверхні торкаються лише вершечками виступів — там і живе тертя", size=16, bold=True)]

    x0, x1 = 130, 810
    contacts_x = [230, 445, 660]          # де вершечки зустрічаються
    ymeet = 258                            # рівень дотику

    # зубчастий верхній край нижнього блоку (вершини вгору — до ymeet)
    bottom_top = [
        (130, 296), (180, 274), (230, 258), (285, 280), (340, 296),
        (392, 274), (445, 258), (500, 280), (555, 296), (607, 274),
        (660, 258), (715, 280), (770, 293), (810, 296)]
    # зубчастий нижній край верхнього блоку (вершини вниз — до ymeet у тих самих x)
    top_bot = [
        (130, 230), (180, 224), (230, 258), (285, 214), (340, 208),
        (392, 224), (445, 258), (500, 214), (555, 208), (607, 224),
        (660, 258), (715, 214), (770, 216), (810, 222)]

    # нижній блок
    bpoly = bottom_top + [(810, 392), (130, 392)]
    f.append(poly(bpoly, fill="#eef1f4", stroke=INK, sw=2, close=True))
    # верхній блок
    tpoly = top_bot + [(810, 120), (130, 120)]
    f.append(poly(tpoly, fill="#f4f6f8", stroke=INK, sw=2, close=True))

    f.append(text(150, 360, "нижнє тіло", size=12.5, color=MUTED, anchor="start"))
    f.append(text(150, 150, "верхнє тіло", size=12.5, color=MUTED, anchor="start"))

    # притиск N — стрілки вниз на верхній блок
    for xx in (250, 470, 690):
        f.append(arrow(xx, 78, xx, 116, color=PUSH, sw=2.8))
    f.append(text(470, 66, "притиск N", size=13.5, bold=True, color=PUSH))

    # позначити три точки дотику
    for cx in contacts_x:
        f.append(circle(cx, ymeet, 7, fill="#fdecea", stroke=PUSH, sw=2.2))

    # виноска до одного дотику: зчеплення атомів
    box, bw, bh = textbox(690, 405,
                          "тут атоми зчіплюються —\nмістки холодного зварювання",
                          size=12.5, pad=10, fill="#fdf0ef", stroke=PUSH, sw=1.6)
    f.append(line(660, ymeet + 8, 690, 405 - bh / 2 - 4, color=PUSH, sw=1.4, dash="3,4"))
    f.append(box)

    # видима площа A — широка стрілка внизу
    f.append(arrow(130, 430, 810, 430, color=INK, sw=1.6))
    f.append(arrow(810, 430, 130, 430, color=INK, sw=1.6))
    f.append(text(300, 448, "видима площа дотику A — велика", size=12.5, color=INK, anchor="start"))

    # справжня площа — лише вершечки
    box2, bw2, bh2 = textbox(250, 405,
                             "справжня площа —\nлише вершечки\n(тисячні від A)",
                             size=12.5, pad=10, fill="#eef7f0", stroke=WT, sw=1.6)
    f.append(box2)

    render(os.path.join(IMG, "friction-origin.svg"), W, H, *f)


# ── Фігура 2: статичне й кінетичне тертя — відповідь на натиск ────────────────
def fig_static_kinetic():
    W, H = 900, 470
    f = [text(W / 2, 30, "Сила тертя у відповідь на натиск: поріг зриву й провал у ковзання", size=15.5, bold=True)]

    ox, oy = 120, 400          # початок осей
    ex, ey = 830, 90
    fx = lambda v: ox + v / 185.0 * (ex - ox)     # прикладена сила, 0..185 Н
    fy = lambda v: oy - v / 155.0 * (oy - ey)     # сила тертя, 0..155 Н

    # осі
    f.append(arrow(ox, oy, ox, ey - 6, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ex + 6, oy, color=INK, sw=1.8))
    f.append(text(ox - 10, ey - 4, "сила тертя", size=13, bold=True, anchor="end"))
    f.append(text(ex + 4, oy + 22, "прикладена зовнішня сила", size=13, bold=True, anchor="end"))

    Fs, Fk = 122.5, 98.0       # μ_s·N та μ_k·N із задачі в тексті

    # рівні μ_s·N та μ_k·N — пунктири до осі
    f.append(line(ox, fy(Fs), fx(Fs), fy(Fs), color=PUSH, sw=1.3, dash="5,5"))
    f.append(line(ox, fy(Fk), fx(185), fy(Fk), color=FRIC, sw=1.3, dash="5,5"))
    f.append(text(ox - 12, fy(Fs) + 4, "μ_s·N", size=13, bold=True, color=PUSH, anchor="end"))
    f.append(text(ox - 12, fy(Fk) + 4, "μ_k·N", size=13, bold=True, color=FRIC, anchor="end"))

    # діагональ спокою: тертя = натиск, до порога
    f.append(line(fx(0), fy(0), fx(Fs), fy(Fs), color=PUSH, sw=3.2))
    # провал на порозі
    f.append(line(fx(Fs), fy(Fs), fx(Fs), fy(Fk), color=INK, sw=2.0, dash="4,4"))
    # плато ковзання
    f.append(line(fx(Fs), fy(Fk), fx(185), fy(Fk), color=FRIC, sw=3.2))

    # маркери
    f.append(circle(fx(Fs), fy(Fs), 5.5, fill=PUSH, stroke=PUSH, sw=1))
    f.append(text(fx(Fs) + 12, fy(Fs) - 8, "поріг зриву", size=12.5, bold=True, color=PUSH, anchor="start"))

    # підписи режимів
    f.append(text(fx(48), fy(80), "тіло стоїть:", size=12.5, color=PUSH, anchor="start"))
    f.append(text(fx(48), fy(80) + 17, "тертя = натиск", size=12.5, color=PUSH, anchor="start"))
    f.append(text(fx(150), fy(Fk) - 16, "тіло ковзає: тертя стале", size=12.5, color=FRIC))

    render(os.path.join(IMG, "static-kinetic.svg"), W, H, *f)


# ── Фігура 3: похила площина — кут тертя й розклад ваги ───────────────────────
def fig_incline_repose():
    W, H = 920, 480
    f = [text(W / 2, 30, "Похилина як вимірювач тертя: зрив, коли tan θ = μ_s", size=16, bold=True)]

    A = (150, 385)             # нижній кут (вершина θ)
    B = (760, 385)             # низ, правий
    C = (760, 150)             # верх, правий (прямий кут унизу праворуч)

    # трикутник-клин
    f.append(poly([A, B, C], fill="#eef1f4", stroke=INK, sw=2, close=True))

    # орти вздовж схилу (u) і зовнішня нормаль (nOut)
    dx, dy = C[0] - A[0], C[1] - A[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L                  # угору по схилу
    nx, ny = -uy, ux                          # (−uy, ux) — угору-ліворуч від поверхні
    if ny > 0:                                # переконатися, що нормаль дивиться ВГОРУ
        nx, ny = -nx, -ny

    # брусок на схилі
    c = (440, 260)
    c = (c[0] + nx * 20, c[1] + ny * 20)      # трохи над поверхнею
    hh = 26
    P = [(c[0] + ux * hh + nx * hh, c[1] + uy * hh + ny * hh),
         (c[0] + ux * hh - nx * hh, c[1] + uy * hh - ny * hh),
         (c[0] - ux * hh - nx * hh, c[1] - uy * hh - ny * hh),
         (c[0] - ux * hh + nx * hh, c[1] - uy * hh + ny * hh)]
    f.append(poly(P, fill="#f4f6f8", stroke=INK, sw=2, close=True))

    th = math.atan2(-dy, dx)                   # кут схилу (dy<0)
    Lw = 128                                    # довжина вектора ваги (px)
    # вага прямовисно вниз
    wtip = (c[0], c[1] + Lw)
    f.append(arrow(c[0], c[1], wtip[0], wtip[1], color=WT, sw=3.2))
    f.append(text(wtip[0] + 13, wtip[1] - 2, "вага  mg", size=13, bold=True, color=WT, anchor="start"))

    # складова ваги вздовж схилу (притискальну показує N нижче)
    comp1 = Lw * math.sin(th)                   # mg·sinθ — скочувальна
    comp2 = Lw * math.cos(th)                   # mg·cosθ — притискальна (= N)
    d1 = (c[0] - ux * comp1, c[1] - uy * comp1)          # вниз по схилу
    f.append(arrow(c[0], c[1], d1[0], d1[1], color=WT, sw=2.0))
    f.append(line(d1[0], d1[1], wtip[0], wtip[1], color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(d1[0] - 10, d1[1] + 16, "mg·sinθ", size=12.5, color=WT, anchor="end"))
    f.append(text(d1[0] - 10, d1[1] + 33, "котить униз", size=11.5, color=MUTED, anchor="end"))

    # нормальна сила (проти притискальної складової)
    ntip = (c[0] + nx * comp2, c[1] + ny * comp2)
    f.append(arrow(c[0], c[1], ntip[0], ntip[1], color=INK, sw=2.6))
    f.append(text(ntip[0] - 6, ntip[1] - 6, "N = mg·cosθ", size=12.5, bold=True, anchor="end"))

    # тертя вгору по схилу
    ftip = (c[0] + ux * 92, c[1] + uy * 92)
    f.append(arrow(c[0], c[1], ftip[0], ftip[1], color=FRIC, sw=2.8))
    f.append(text(ftip[0] + 8, ftip[1] - 4, "тертя  μ_s·N", size=12.5, bold=True, color=FRIC, anchor="start"))

    # дуга кута θ біля A
    r = 66
    a1 = (A[0] + r, A[1])
    a2 = (A[0] + r * math.cos(th), A[1] - r * math.sin(th))
    f.append(path("M %.1f %.1f A %d %d 0 0 0 %.1f %.1f" % (a1[0], a1[1], r, r, a2[0], a2[1]),
                  stroke=INK, sw=1.6))
    f.append(text(A[0] + r + 8, A[1] - 6, "θ", size=16, bold=True, anchor="start"))

    # рамка з висновком
    box, bw, bh = textbox(W / 2, 452,
                          "зрив, коли mg·sinθ > μ_s·mg·cosθ   →   m і g скорочуються   →   μ_s = tan θ",
                          size=14, pad=12, fill="#eef7f0", stroke=WT, sw=1.5)
    f.append(box)

    render(os.path.join(IMG, "incline-repose.svg"), W, H, *f)


# ── Фігура 4: коефіцієнт тертя різних пар — смуги ─────────────────────────────
def fig_mu_values():
    W, H = 900, 380
    f = [text(W / 2, 30, "Коефіцієнт тертя μ: від чіпкого до ковзкого", size=16, bold=True)]

    rows = [
        ("гума по сухому бетону", 1.00),
        ("сталь по сталі (сухі)", 0.60),
        ("дерево по дереву",      0.30),
        ("лід по льоду",          0.10),
        ("тефлон по сталі",       0.04),
    ]
    x0 = 300                    # старт смуг
    xmax = 850                  # кінець найдовшої
    scale = (xmax - x0) / 1.05
    y = 92
    for name, mu in rows:
        f.append(text(280, y + 5, name, size=13, anchor="end"))
        bw = mu * scale
        col = GRIP if mu >= 0.5 else (MUTED if mu >= 0.15 else SLIP)
        f.append(rect(x0, y - 14, max(bw, 3), 28, fill=col, stroke="none", sw=0, rx=4))
        f.append(text(x0 + max(bw, 3) + 12, y + 5, "%.2f" % mu, size=13, bold=True, anchor="start"))
        y += 52
    f.append(line(x0, 74, x0, y - 34, color=MUTED, sw=1.2, dash="3,4"))
    f.append(text((x0 + xmax) / 2, 356,
                  "довша смуга — чіпкіше; суглоби людини (μ ≈ 0.003) лежать далеко за лівим краєм",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "mu-values.svg"), W, H, *f)


# ── Фігура 5 (hist): часова вісь відкриття законів тертя ──────────────────────
def fig_hist_timeline():
    W, H = 1060, 610
    f = [text(W / 2, 34, "Закони тертя: 450 років від виміру до пояснення", size=17, bold=True)]

    ax_y = 340
    x_left, x_right = 70, 1015
    f.append(arrow(x_left, ax_y, x_right, ax_y, color=INK, sw=2.2))
    f.append(text(x_right - 4, ax_y - 12, "час", size=12.5, color=MUTED, anchor="end"))

    box_w, box_top, box_h = 188, 92, 120
    nodes = [
        (145, "1493", "Леонардо да Вінчі",
         ["виміряв обидва закони", "— у таємних нотатниках", "(світ не дізнався)"], False),
        (345, "1699", "Ґійом Амонтон",
         ["оприлюднив закони", "Академії — і спершу", "йому не повірили"], False),
        (545, "1750", "Леонард Ойлер",
         ["дав математику:", "μ = tan α; спокій", "≠ ковзання"], False),
        (745, "1785", "Шарль Кулон",
         ["розділив статичне", "й кінетичне; майже", "незалежне від швидкості"], False),
        (945, "1950", "Боуден і Тейбор",
         ["ЧОМУ: справжня площа", "∝ навантаженню", "+ адгезія"], True),
    ]
    for x, yr, name, lines, is_why in nodes:
        fill = "#eef7f0" if is_why else "#f7f9fb"
        stroke = FIELD if is_why else MUTED
        bx = x - box_w / 2
        f.append(rect(bx, box_top, box_w, box_h, fill=fill, stroke=stroke,
                      sw=1.9 if is_why else 1.3, rx=8))
        f.append(text(x, box_top + 24, name, size=13.5, bold=True,
                      color=(FIELD if is_why else INK)))
        yy = box_top + 48
        for ln in lines:
            f.append(text(x, yy, ln, size=12, color=INK))
            yy += 18
        # конектор коробка → вузол на осі
        f.append(line(x, box_top + box_h, x, ax_y - 9, color=MUTED, sw=1.2, dash="3,4"))
        # вузол і рік
        f.append(circle(x, ax_y, 8, fill=(FIELD if is_why else INK),
                        stroke=(FIELD if is_why else INK), sw=1))
        f.append(text(x, ax_y + 28, yr, size=15, bold=True,
                      color=(FIELD if is_why else INK)))

    # Дезаґюльє — маленька віха під віссю (натяк, що лишився непочутим)
    dx = 445
    f.append(circle(dx, ax_y, 5, fill=MUTED, stroke=MUTED, sw=1))
    f.append(text(dx, ax_y + 50, "1734 · Дезаґюльє:", size=11.5, color=MUTED))
    f.append(text(dx, ax_y + 66, "натяк на адгезію — не почули", size=11.5, color=MUTED))

    # Теза: закон відомий, механізм — загадка (смуга під нодами 1493–1785)
    band_x0, band_x1 = 55, 745
    by0, by1 = 440, 494
    f.append(rect(band_x0, by0, band_x1 - band_x0, by1 - by0,
                  fill="#fdf1ee", stroke=PUSH, sw=1.5, rx=8))
    f.append(text((band_x0 + band_x1) / 2, by0 + 32,
                  "закон працює й тримає — а ЧОМУ він правдивий, не знав ніхто",
                  size=13.5, bold=True, color=PUSH))

    # стрілка від «загадки» до розгадки 1950 + зелена помітка
    f.append(arrow(band_x1 + 4, (by0 + by1) / 2, 852, (by0 + by1) / 2, color=INK, sw=1.8))
    gb0 = 856
    f.append(rect(gb0, by0, 1005 - gb0, by1 - by0, fill="#eef7f0", stroke=FIELD, sw=1.7, rx=8))
    f.append(text((gb0 + 1005) / 2, by0 + 32, "механізм пояснено", size=13, bold=True, color=FIELD))

    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


# ── Фігура 6 (hist): що знали — і чого не могли пояснити ──────────────────────
def fig_hist_known_vs_why():
    W, H = 1000, 520
    f = [text(W / 2, 34, "Що знали — і чого не могли пояснити", size=17, bold=True)]

    ly, lh = 72, 250
    # ліва панель — ЗНАЛИ
    lx, lw = 60, 400
    f.append(rect(lx, ly, lw, lh, fill="#eef7f0", stroke=FIELD, sw=1.9, rx=10))
    f.append(text(lx + lw / 2, ly + 28, "ЗНАЛИ  (да Вінчі 1493, Амонтон 1699)",
                  size=13, bold=True, color=FIELD))
    f.append(fitbox(lx + 24, ly + 46, lw - 48, 80,
                    "1.  Тертя ∝ навантаженню\nF = μ · N",
                    size=15, pad=10, fill=BG, stroke=INK, sw=1.3, bold=True))
    f.append(fitbox(lx + 24, ly + 142, lw - 48, 80,
                    "2.  Тертя НЕ залежить\nвід видимої площі",
                    size=15, pad=10, fill=BG, stroke=INK, sw=1.3, bold=True))

    # права панель — НЕ РОЗУМІЛИ
    rx, rw = 540, 400
    f.append(rect(rx, ly, rw, lh, fill="#fdf1ee", stroke=PUSH, sw=1.9, rx=10))
    f.append(text(rx + rw / 2, ly + 28, "НЕ РОЗУМІЛИ  (≈ 250 років)",
                  size=13, bold=True, color=PUSH))
    f.append(fitbox(rx + 24, ly + 46, rw - 48, 80,
                    "Чому важить навантаження,\nа не видима площа?",
                    size=15, pad=10, fill=BG, stroke=PUSH, sw=1.3))
    f.append(fitbox(rx + 24, ly + 142, rw - 48, 80,
                    "Що таке μ?\nзвідки береться це число?",
                    size=15, pad=10, fill=BG, stroke=PUSH, sw=1.3))

    # нижня смуга — розгадка
    byr = 372
    f.append(rect(60, byr, 880, 116, fill="#eef7f0", stroke=FIELD, sw=2, rx=10))
    f.append(text(500, byr + 28, "Боуден і Тейбор, 1950 — розгадка",
                  size=14.5, bold=True, color=FIELD))
    f.append(fitbox(84, byr + 40, 832, 62,
                    "справжня площа дотику крихітна й ∝ навантаженню (вершечки течуть, не пружинять)\n"
                    "→ обидва закони випливають;  μ ≈ міцність зчеплень ÷ твердість поверхні",
                    size=13.5, pad=8, fill=BG, stroke=FIELD, sw=1.2))

    f.append(arrow(lx + lw / 2, ly + lh, lx + lw / 2, byr, color=INK, sw=1.8))
    f.append(arrow(rx + rw / 2, ly + lh, rx + rw / 2, byr, color=INK, sw=1.8))

    render(os.path.join(IMG, "hist-known-vs-why.svg"), W, H, *f)


# ── Фігура 7 (math): справжня площа йде за навантаженням — A = N/H ─────────────
def fig_area_load():
    W, H = 960, 452
    f = [text(W / 2, 32, "Справжня площа контакту йде за навантаженням, а не за видимою: A = N/H",
              size=15.5, bold=True)]

    blkTop, baseY = 128, 250

    def panel(x0, x1, arrows, seg, area_lbl, vid_lbl):
        cx = (x0 + x1) / 2
        g = [rect(x0, blkTop, x1 - x0, baseY - blkTop, fill="#f4f6f8", stroke=INK, sw=2),
             text(cx, blkTop + (baseY - blkTop) / 2 + 5, "тіло", size=12.5, color=MUTED)]
        for ax in arrows:
            g.append(arrow(ax, 74, ax, blkTop - 4, color=PUSH, sw=3.4))
        # реальні плями контакту вздовж основи
        for a, b in seg:
            g.append(rect(a, baseY - 4, b - a, 9, fill=PUSH, stroke="none", sw=0, rx=2))
        g.append(text(cx, baseY + 28, area_lbl, size=13, bold=True, color=PUSH))
        # видима ширина (однакова в обох панелях)
        g.append(line(x0, baseY + 48, x1, baseY + 48, color=INK, sw=1.3))
        g.append(line(x0, baseY + 44, x0, baseY + 52, color=INK, sw=1.3))
        g.append(line(x1, baseY + 44, x1, baseY + 52, color=INK, sw=1.3))
        g.append(text(cx, baseY + 68, vid_lbl, size=12.5, color=INK))
        return g

    # ліва панель: навантаження N
    f += panel(140, 390, [265],
               [(176, 194), (250, 266), (330, 345)],
               "справжня площа A", "видима площа A_вид")
    f.append(text(265, 62, "навантаження N", size=13.5, bold=True, color=PUSH))
    # права панель: удвічі більше навантаження 2N → удвічі більша справжня площа
    f += panel(575, 825, [686, 734],
               [(600, 634), (672, 706), (752, 786)],
               "справжня площа 2A", "та сама A_вид")
    f.append(text(710, 62, "навантаження 2N", size=13.5, bold=True, color=PUSH))

    box, bw, bh = textbox(W / 2, baseY + 132,
                          "плями пластично плющаться, доки їхній тиск = H   →   A·H = N   →   A = N / H",
                          size=14, pad=12, fill="#eef7f0", stroke=WT, sw=1.6)
    f.append(box)
    render(os.path.join(IMG, "area-load.svg"), W, H, *f)


# ── Фігура 8 (math): μ = s/H — відношення двох міцностей, і як його зменшити ───
def fig_mu_ratio():
    W, H = 960, 470
    f = [text(W / 2, 32, "Коефіцієнт тертя — відношення міцності на зсув до твердості: μ = s / H",
              size=15.5, bold=True)]

    baseB = 340                      # спільна основа стовпчиків
    Hbar = 186                       # висота стовпчика H (= 3·σ_т у масштабі)

    def duo(cx, title, s_h, s_lbl, mu_txt, mu_col):
        g = [text(cx, 92, title, size=13.5, bold=True)]
        # стовпчик s (міцність на зсув) — синій, низький
        sx = cx - 66
        g.append(rect(sx - 26, baseB - s_h, 52, s_h, fill=FRIC, stroke=INK, sw=1.4))
        g.append(text(sx, baseB + 22, s_lbl, size=12.5, bold=True, color=FRIC))
        # стовпчик H (твердість) — темний, високий
        hx = cx + 66
        g.append(rect(hx - 26, baseB - Hbar, 52, Hbar, fill="#5b6470", stroke=INK, sw=1.4))
        g.append(text(hx, baseB + 22, "H ≈ 3·σ_т", size=12.5, bold=True, color="#5b6470"))
        # спільна лінія основи
        g.append(line(cx - 108, baseB, cx + 108, baseB, color=INK, sw=1.6))
        # підсумок μ
        box, bw, bh = textbox(cx, baseB + 66, mu_txt, size=13.5, pad=11,
                              fill="#eef7f0", stroke=mu_col, sw=1.6, bold=True, color=mu_col)
        g.append(box)
        return g

    f += duo(258, "гола пара метал–метал",
             56, "s ≈ σ_т/2", "μ = s/H ≈ 0.17", WT)
    f += duo(702, "тверда основа + м'яка плівка",
             16, "s плівки — мале", "μ = s/H ≈ 0.05", FRIC)

    f.append(line(480, 84, 480, 412, color=MUTED, sw=1.2, dash="4,5"))
    box, bw, bh = textbox(W / 2, 446,
                          "μ — не стала природи, а важіль: тримай H великим, s малим — і тертя мале "
                          "(тверді мастила: графіт, MoS₂, PTFE)",
                          size=13, pad=11, fill="#fdf7ee", stroke="#b8791f", sw=1.5)
    f.append(box)
    render(os.path.join(IMG, "mu-ratio.svg"), W, H, *f)


# ── Спільне для фігур stick-slip: пружина-зигзаг і сама симуляція ─────────────
def _spring(x1, y, x2, coils=9, amp=13):
    lead = 14
    xa, xb = x1 + lead, x2 - lead
    dx = (xb - xa) / (coils * 2)
    pts = [(x1, y), (xa, y)]
    for i in range(coils * 2):
        yy = y - amp if i % 2 == 0 else y + amp
        pts.append((xa + dx * (i + 0.5), yy))
    pts += [(xb, y), (x2, y)]
    return poly(pts, stroke=INK, sw=1.8)


def _simulate(m=1.0, k=100.0, g=9.8, mu_s=0.5, mu_k=0.3, V=0.02, dt=4e-4, T=7.2):
    """Подієво-перемикана модель stick-slip. Вертає (t, x, v, F)."""
    N = m * g; Fs = mu_s * N; Fk = mu_k * N
    x = v = t = 0.0; stuck = True
    ts = []; xs = []; vs = []; Fl = []
    while t < T:
        F = k * (V * t - x)
        if stuck:
            if F >= Fs:
                stuck = False
        else:
            a = (F - Fk * (1.0 if v >= 0 else -1.0)) / m
            v += a * dt; x += v * dt
            if v <= 0.0:
                v = 0.0; stuck = True
        ts.append(t); xs.append(x); vs.append(v); Fl.append(F)
        t += dt
    return ts, xs, vs, Fl


def _thin(seq, n=620):
    step = max(1, len(seq) // n)
    return seq[::step]


# ── Фігура 6 (proj): будова моделі — брусок, пружина, водій ───────────────────
def fig_stickslip_model():
    W, H = 960, 470
    f = [text(W / 2, 32, "Брусок на пружині, яку тягнуть зі сталою швидкістю V над шорсткою поверхнею",
              size=15.5, bold=True)]
    gy = 250
    # шорстка поверхня зі штрихуванням
    f.append(line(70, gy, 800, gy, color=INK, sw=2.4))
    for xx in range(80, 801, 26):
        f.append(line(xx, gy, xx - 15, gy + 19, color=MUTED, sw=1.2))
    # брусок
    bx, bw, bh = 210, 128, 82
    f.append(rect(bx, gy - bh, bw, bh, fill="#eef1f4", stroke=INK, sw=2))
    f.append(text(bx + bw / 2, gy - bh / 2 + 7, "m", size=22, bold=True))
    cy = gy - bh / 2
    # пружина до водія
    sx1, sx2 = bx + bw, 660
    f.append(_spring(sx1, cy, sx2, coils=9, amp=15))
    f.append(text((sx1 + sx2) / 2, cy - 26, "пружина  k", size=12.5, color=MUTED))
    # водій — планка й стала швидкість
    f.append(line(sx2, cy - 34, sx2, cy + 34, color=INK, sw=4))
    f.append(rect(sx2, cy - 34, 16, 68, fill="#e7ebef", stroke=INK, sw=1.6))
    f.append(arrow(sx2 + 20, cy - 50, sx2 + 108, cy - 50, color=PUSH, sw=3.2))
    f.append(text(sx2 + 116, cy - 46, "V = const", size=14, bold=True, color=PUSH, anchor="start"))
    f.append(text(sx2 + 116, cy - 28, "(сталий потяг)", size=11.5, color=MUTED, anchor="start"))
    # сила пружини на брусок
    f.append(arrow(bx + bw - 4, cy + 20, bx + bw + 66, cy + 20, color=PUSH, sw=2.6))
    f.append(text(bx + bw + 30, cy + 12, "F = k·(Vt − x)", size=12, color=PUSH))
    # тертя в основі
    f.append(arrow(bx + 20, gy - 7, bx - 48, gy - 7, color=FRIC, sw=2.6))
    f.append(text(bx - 12, gy - 15, "тертя", size=12.5, color=FRIC, anchor="end"))
    # нормальна сила / вага збоку
    f.append(text(bx + bw / 2, gy + 40, "N = m·g", size=12, color=MUTED))
    # два стани — рамки внизу
    boxA, wA, hA = textbox(275, 400,
                           "ПРИЛИПАННЯ (stick)\n|F| < μ_s·N — брусок стоїть,\nпружина напинається, сила росте",
                           size=12.5, pad=11, fill="#fdecea", stroke=PUSH, sw=1.6)
    f.append(boxA)
    boxB, wB, hB = textbox(690, 400,
                           "ЗРИВ І КОВЗАННЯ (slip)\nF = μ_s·N — брусок зривається й летить,\nтертя падає до μ_k·N, доки швидкість не впаде",
                           size=12.5, pad=11, fill="#eaf0fd", stroke=FRIC, sw=1.6)
    f.append(boxB)
    render(os.path.join(IMG, "stickslip-model.svg"), W, H, *f)


# ── Фігура 7 (proj): пилчаста крива — сила пружини й швидкість у часі ──────────
def fig_stickslip_sawtooth():
    ts, xs, vs, Fl = _simulate(V=0.02, T=7.2, dt=4e-4)
    ts, vs, Fl = _thin(ts), _thin(vs), _thin(Fl)
    W, H = 980, 600
    f = [text(W / 2, 30, "Пилчастий рух stick-slip: пружна сила й швидкість бруска в часі",
              size=15.5, bold=True)]
    N = 9.8; Fs, Fk, Fmin = 0.5 * N, 0.3 * N, (2 * 0.3 - 0.5) * N
    ox, ex = 170, 830
    t1 = 7.2
    tx = lambda t: ox + t / t1 * (ex - ox)

    # ── верхня панель: сила пружини (пилка) ──
    py0, py1, Fmax = 250, 70, 5.6
    fy = lambda v: py0 - v / Fmax * (py0 - py1)
    f.append(arrow(ox, py0, ox, py1 - 6, color=INK, sw=1.6))
    f.append(arrow(ox, py0, ex + 6, py0, color=INK, sw=1.6))
    f.append(text(ox - 2, py1 - 12, "сила пружини F, Н", size=12.5, bold=True, anchor="middle"))
    for lvl, col, lab in [(Fs, PUSH, "μ_s·N"), (Fk, FRIC, "μ_k·N"), (Fmin, WT, "мін")]:
        f.append(line(ox, fy(lvl), ex, fy(lvl), color=col, sw=1.1, dash="5,5"))
        f.append(text(ox - 10, fy(lvl) + 4, lab, size=12, bold=True, color=col, anchor="end"))
    f.append(poly([(tx(t), fy(v)) for t, v in zip(ts, Fl)], stroke=INK, sw=2.1))
    # позначки: поріг зриву, стрибок, час прилипання, час ковзання
    f.append(text(tx(0.5), fy(Fs) - 10, "лінійне вантаження ↗", size=11.5, color=MUTED, anchor="start"))
    # стрибок сили на першому зриві (t≈2.45)
    tb = 2.45
    f.append(arrow(tx(tb) + 46, fy(Fs), tx(tb) + 46, fy(Fmin), color=INK, sw=1.5))
    f.append(arrow(tx(tb) + 46, fy(Fmin), tx(tb) + 46, fy(Fs), color=INK, sw=1.5))
    dlab, dw, dh = textbox(tx(tb) + 150, fy((Fk + Fmin) / 2),
                           "стрибок Δ = 2(μ_s−μ_k)N", size=11.5, pad=7,
                           fill="#f4f6f8", stroke=MUTED, sw=1.2)
    f.append(dlab)
    # брекет часу прилипання під першим схилом
    f.append(line(tx(0.05), py0 + 16, tx(2.40), py0 + 16, color=PUSH, sw=1.4))
    f.append(text(tx(1.2), py0 + 31, "T_stick — довге прилипання ∝ 1/V", size=11.5, color=PUSH))

    # ── нижня панель: швидкість бруска (сплески) ──
    qy0, qy1, vmax = 470, 320, 0.26
    vy = lambda v: qy0 - v / vmax * (qy0 - qy1)
    f.append(arrow(ox, qy0, ox, qy1 - 6, color=INK, sw=1.6))
    f.append(arrow(ox, qy0, ex + 6, qy0, color=INK, sw=1.6))
    f.append(text(ox - 2, qy1 - 12, "швидкість бруска v, м/с", size=12.5, bold=True, anchor="middle"))
    f.append(line(ox, vy(0.02), ex, vy(0.02), color=MUTED, sw=1.0, dash="4,4"))
    f.append(text(ex + 4, vy(0.02) + 4, "V тяги", size=11, color=MUTED, anchor="start"))
    f.append(poly([(tx(t), vy(v)) for t, v in zip(ts, vs)], stroke=FRIC, sw=2.1))
    f.append(text(tx(2.62), vy(0.20), "різкий кидок:", size=11.5, color=FRIC, anchor="middle"))
    f.append(text(tx(2.62), vy(0.20) + 16, "v ≈ 10·V", size=11.5, color=FRIC, anchor="middle"))
    f.append(text(tx(1.2), vy(0.0) - 25, "стоїть (v = 0)", size=11.5, color=MUTED))
    f.append(text(ex + 6, qy0 + 20, "час t, с", size=12, bold=True, anchor="end"))
    render(os.path.join(IMG, "stickslip-sawtooth.svg"), W, H, *f)


# ── Фігура 8 (proj): від чого залежить пилка — швидкість тяги і розрив μ ───────
def fig_stickslip_depend():
    W, H = 1000, 470
    f = [text(W / 2, 30, "Від чого залежить stick-slip: швидкість тяги і розрив μ_s − μ_k",
              size=15.5, bold=True)]

    def strip(x0, y0, w, h, series, ymax, color, label, sub):
        f.append(rect(x0, y0, w, h, fill="#fbfcfd", stroke="#dfe3e8", sw=1.2))
        ts, Fl = series
        n = len(ts); t1 = ts[-1]
        px = lambda t: x0 + t / t1 * w
        py = lambda v: y0 + h - v / ymax * (h - 10)
        f.append(poly([(px(t), py(v)) for t, v in zip(ts, Fl)], stroke=color, sw=1.8))
        f.append(text(x0 + 8, y0 + 16, label, size=12, bold=True, color=color, anchor="start"))
        f.append(text(x0 + w - 8, y0 + 16, sub, size=11, color=MUTED, anchor="end"))

    # ── ліва колонка: швидкість тяги ──
    f.append(text(255, 66, "Швидше тягнеш → частіші зриви (зуб тієї ж висоти)", size=12.5, bold=True))
    LX, LW, hh = 70, 380, 78
    for i, (V, lab) in enumerate([(0.02, "V"), (0.05, "2.5·V"), (0.10, "5·V")]):
        ts, xs, vs, Fl = _simulate(V=V, T=6.0, dt=3e-4)
        strip(LX, 84 + i * (hh + 20), LW, hh, (_thin(ts, 500), _thin(Fl, 500)),
              5.6, INK, "тяга " + lab, "")
    f.append(text(LX + LW / 2, 84 + 3 * (hh + 20) - 6, "час →", size=11, color=MUTED))

    # ── права колонка: розрив коефіцієнтів ──
    f.append(text(745, 66, "Менший розрив μ_s−μ_k → нижчі зуби; розриву нема → гладко", size=12.5, bold=True))
    RX, RW = 560, 380
    cases = [(0.5, 0.3, "μ_s−μ_k = 0.2", GRIP), (0.37, 0.30, "μ_s−μ_k = 0.07", "#b8791f")]
    for i, (ms, mk, lab, col) in enumerate(cases):
        ts, xs, vs, Fl = _simulate(mu_s=ms, mu_k=mk, V=0.02, T=6.0, dt=3e-4)
        strip(RX, 84 + i * (hh + 20), RW, hh, (_thin(ts, 500), _thin(Fl, 500)),
              5.6, col, lab, "пилка")
    # розрив нема — гладке ковзання (ідеальна пряма на μ_k·N)
    y0 = 84 + 2 * (hh + 20)
    f.append(rect(RX, y0, RW, hh, fill="#fbfcfd", stroke="#dfe3e8", sw=1.2))
    Fk = 0.3 * 9.8; ymax = 5.6
    ry = lambda v: y0 + hh - v / ymax * (hh - 10)
    # коротке лінійне вантаження, тоді пласко на μ_k·N
    xr = RX + RW
    f.append(poly([(RX, ry(0)), (RX + 90, ry(Fk)), (xr, ry(Fk))], stroke=SLIP, sw=2.0))
    f.append(line(RX, ry(Fk), xr, ry(Fk), color=SLIP, sw=1.0, dash="4,4"))
    f.append(text(RX + 8, y0 + 16, "μ_s = μ_k", size=12, bold=True, color=SLIP, anchor="start"))
    f.append(text(xr - 8, y0 + 16, "гладко", size=11, color=MUTED, anchor="end"))
    f.append(text(RX + RW / 2, y0 + hh - 6, "час →", size=11, color=MUTED))
    render(os.path.join(IMG, "stickslip-depend.svg"), W, H, *f)


if __name__ == "__main__":
    fig_friction_origin()
    fig_static_kinetic()
    fig_incline_repose()
    fig_mu_values()
    fig_hist_timeline()
    fig_hist_known_vs_why()
    fig_area_load()
    fig_mu_ratio()
    fig_stickslip_model()
    fig_stickslip_sawtooth()
    fig_stickslip_depend()
    print("OK: figs written to", IMG)
