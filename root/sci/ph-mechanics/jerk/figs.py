# -*- coding: utf-8 -*-
"""Фігури до теми «Ривок» (третя похідна положення).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

XC = "#c0392b"   # положення x — червоне
VC = "#2980b9"   # швидкість v — синє
AC = "#8e44ad"   # прискорення a — фіолетове
JC = "#d35400"   # ривок j — гарячий помаранчевий (герой теми)


# ── Фігура 1: драбина похідних x → v → a → j ─────────────────────────────────
def fig_deriv_ladder():
    W, H = 720, 862
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Драбина похідних: x → v → a → j", size=18, bold=True))

    PL, PW = 92, 300           # ліва межа й ширина графічної області
    PH = 150                   # висота панелі
    tops = (62, 250, 438, 626)
    tmax = 2.0

    def panel(top, fn, ymax, ylabel, formula, color, box_fill=FILL):
        out = []
        bottom = top + PH

        def Xx(t):
            return PL + t / tmax * PW

        def Yy(v):
            return bottom - v / ymax * (PH - 26)

        # осі панелі
        out.append(line(PL, bottom, PL + PW + 24, bottom, color=INK, sw=1.6))
        out.append(line(PL, bottom, PL, top + 4, color=INK, sw=1.6))
        out.append(text(PL - 12, top + 12, ylabel, size=14, italic=True, anchor="end", color=color, bold=True))
        # крива
        pts = []
        tt = 0.0
        while tt <= tmax + 1e-9:
            pts.append("%.1f,%.1f" % (Xx(tt), Yy(fn(tt))))
            tt += 0.04
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                    % (" ".join(pts), color))
        # формула у рамці справа (з великим запасом)
        out.append(textbox(PL + PW + 148, top + PH / 2, formula, size=13.5, pad=10,
                           fill=box_fill, stroke=color, sw=1.6, color=color, bold=True)[0])
        return "".join(out)

    f.append(panel(tops[0], lambda t: t ** 3, 8.4, "x", "x(t) = t³", XC))
    f.append(panel(tops[1], lambda t: 3 * t * t, 12.6, "v", "v = dx/dt\n= 3t²", VC))
    f.append(panel(tops[2], lambda t: 6 * t, 12.6, "a", "a = dv/dt\n= 6t", AC))
    f.append(panel(tops[3], lambda t: 6.0, 9.0, "j", "j = da/dt\n= 6  (стале)", JC, box_fill="#fdf0e6"))

    # стрілки «похідна = нахил» між панелями
    for i in range(3):
        y0 = tops[i] + PH + 3
        f.append(arrow(PL + 132, y0, PL + 132, y0 + 33, color=MUTED, sw=2.2))
        f.append(text(PL + 146, y0 + 23, "похідна = нахил", size=11.5, color=MUTED, anchor="start"))

    # спільна вісь часу
    f.append(text(PL + PW + 20, tops[3] + PH + 18, "t", size=13, italic=True, anchor="end"))

    b = textbox(W / 2, 828,
                "Кожна крива — нахил тієї, що над нею. Ривок стоїть на третьому щаблі:\n"
                "рівномірно висхідне прискорення (a = 6t) дає сталий додатний ривок",
                size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "deriv-ladder.svg"), W, H, *f)


# ── Фігура 2: трапеція vs S-крива (v, a, j) ──────────────────────────────────
def fig_profiles():
    W, H = 1020, 690
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Той самий переїзд: трапеція проти S-кривої", size=18, bold=True))

    # заголовки колонок
    f.append(textbox(300, 62, "Трапеція: ривок нескінченний", size=13.5, pad=8,
                     fill="#fbe9e4", stroke=XC, sw=1.5, color=XC, bold=True)[0])
    f.append(textbox(730, 62, "S-крива: ривок обмежений", size=13.5, pad=8,
                     fill="#e6f5ec", stroke="#1c7a43", sw=1.5, color="#1c7a43", bold=True)[0])
    f.append(line(515, 88, 515, 612, color="#dfe4ea", sw=1.3, dash="4,6"))

    # смуги рядків: (верх, низ) кожного графіка
    rows = {"v": (96, 210), "a": (250, 364), "j": (404, 518)}
    LX = (120, 470)     # ліва колонка: x-межі області
    RX = (560, 910)     # права колонка
    T = 4.0             # повний час переїзду
    A = 1.0             # рівень прискорення

    def cell_axes(out, xr, top, bottom, ylab, color, zero_mid=False):
        """Осі клітинки. zero_mid — нульова лінія посередині (для a, j зі знаком)."""
        x0, x1 = xr
        y_zero = (top + bottom) / 2 if zero_mid else bottom
        out.append(line(x0, y_zero, x1 + 16, y_zero, color=INK, sw=1.5))   # вісь t
        out.append(line(x0, bottom + 4, x0, top - 8, color=INK, sw=1.5))    # вісь значень
        out.append(text(x0 - 10, top + 4, ylab, size=13.5, italic=True, anchor="end", color=color, bold=True))
        out.append(text(x1 + 14, y_zero - 6, "t", size=12, italic=True, anchor="end", color=MUTED))
        return y_zero

    def X(xr, t):
        return xr[0] + t / T * (xr[1] - xr[0])

    # ── V (швидкість) ──
    top, bot = rows["v"]
    vtop = top + 14
    # ліва: трапеція
    yz = cell_axes(f, LX, top, bot, "v", VC)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (
        "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
            X(LX, 0), bot, X(LX, 1), vtop, X(LX, 3), vtop, X(LX, 4), bot), VC))
    # права: S-крива (згладжені кути)
    yz = cell_axes(f, RX, top, bot, "v", VC)
    spts = []
    tt = 0.0
    while tt <= T + 1e-9:
        # плавний профіль: smootherstep-розгін [0,1], поличка [1,3], спад [3,4]
        if tt <= 1:
            s = tt
            val = 6 * s ** 5 - 15 * s ** 4 + 10 * s ** 3
        elif tt <= 3:
            val = 1.0
        else:
            s = (4 - tt)
            val = 6 * s ** 5 - 15 * s ** 4 + 10 * s ** 3
        spts.append("%.1f,%.1f" % (X(RX, tt), bot - val * (bot - vtop)))
        tt += 0.03
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(spts), VC))

    # ── A (прискорення) ──
    top, bot = rows["a"]
    amp = (bot - top) / 2 - 12
    # ліва: прямокутні сходинки +A / 0 / −A
    yz = cell_axes(f, LX, top, bot, "a", AC, zero_mid=True)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (
        "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
            X(LX, 0), yz, X(LX, 0), yz - amp, X(LX, 1), yz - amp, X(LX, 1), yz,
            X(LX, 3), yz, X(LX, 3), yz + amp, X(LX, 4), yz + amp, X(LX, 4), yz), AC))
    f.append(text(X(LX, 0.5), yz - amp - 8, "+A", size=11.5, color=AC, bold=True))
    f.append(text(X(LX, 3.5), yz + amp + 16, "−A", size=11.5, color=AC, bold=True))
    # права: трикутні горби (без прямовисних зривів)
    yz = cell_axes(f, RX, top, bot, "a", AC, zero_mid=True)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (
        "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
            X(RX, 0), yz, X(RX, 0.5), yz - amp, X(RX, 1), yz, X(RX, 3), yz,
            X(RX, 3.5), yz + amp, X(RX, 4), yz, X(RX, 4), yz), AC))
    f.append(text(X(RX, 0.5), yz - amp - 8, "+A", size=11.5, color=AC, bold=True))
    f.append(text(X(RX, 3.5), yz + amp + 16, "−A", size=11.5, color=AC, bold=True))

    # ── J (ривок) ──
    top, bot = rows["j"]
    jamp = (bot - top) / 2 - 14
    # ліва: нескінченні піки (тонкі високі стрілки) на кутах
    yz = cell_axes(f, LX, top, bot, "j", JC, zero_mid=True)
    for tt, up in ((0, True), (1, False), (3, False), (4, True)):
        xx = X(LX, tt)
        y2 = yz - jamp - 6 if up else yz + jamp + 6
        f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="3.2" marker-end="url(#arrow)"/>' % (xx, yz, xx, y2, JC))
    f.append(text(X(LX, 0) + 8, yz - jamp + 2, "∞", size=17, color=JC, bold=True, anchor="start"))
    f.append(text(X(LX, 4) - 8, yz - jamp + 2, "∞", size=17, color=JC, bold=True, anchor="end"))

    # права: скінченні прямокутники ±J
    yz = cell_axes(f, RX, top, bot, "j", JC, zero_mid=True)
    jh = jamp * 0.7

    def jbar(t0, t1, sign):
        y = yz - sign * jh
        return (rect(X(RX, t0), min(y, yz), X(RX, t1) - X(RX, t0), abs(y - yz),
                     fill="#fdf0e6", stroke=JC, sw=1.8, rx=2))
    f.append(jbar(0, 0.5, +1))
    f.append(jbar(0.5, 1, -1))
    f.append(jbar(3, 3.5, -1))
    f.append(jbar(3.5, 4, +1))
    f.append(text(X(RX, 0.25), yz - jh - 8, "+J", size=11, color=JC, bold=True))
    f.append(text(X(RX, 0.75), yz + jh + 16, "−J", size=11, color=JC, bold=True))
    f.append(textbox(X(RX, 2.05), yz - jh - 20, "стеля ривка", size=10.5, pad=5,
                     fill="#fdf0e6", stroke=JC, sw=1.1, color=JC)[0])

    b = textbox(W / 2, 656,
                "Трапеція вмикає прискорення прямовисною сходинкою — ривок на кутах злітає в нескінченність (поштовх).\n"
                "S-крива нарощує прискорення по косій — ривок ніде не переступає заданої стелі, хід плавний",
                size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "profiles.svg"), W, H, *f)


# ── Фігура 3: раптова сила (удар) vs плавна сила ──────────────────────────────
def fig_force_onset():
    W, H = 940, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Та сама сила, різний ривок: удар проти лагідного розгону", size=17, bold=True))
    f.append(line(470, 58, 470, 400, color="#dfe4ea", sw=1.3, dash="4,6"))

    def person(cx, cy, thrown):
        """Сидяча постать; thrown — наскільки відкидає (px), пунктирна реакція."""
        out = []
        # крісло-спинка
        out.append(line(cx - 26, cy - 42, cx - 26, cy + 30, color="#9aa4b2", sw=4))
        out.append(line(cx - 26, cy + 30, cx + 20, cy + 30, color="#9aa4b2", sw=4))
        # тулуб (нахилений уперед на величину поштовху)
        lean = thrown * 0.5
        out.append(line(cx - 20, cy + 28, cx - 20 + lean, cy - 22, color="#5b6472", sw=7))
        # голова
        out.append(circle(cx - 20 + lean * 1.25, cy - 34, 11, fill="#fde9c8", stroke="#b98a5a", sw=1.8))
        # реакція (куди кидає тіло) — сірий пунктир
        if thrown > 0:
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                       'stroke-width="2.6" stroke-dasharray="5,3" marker-end="url(#arrow)"/>'
                       % (cx - 20 + lean * 1.25, cy - 40, cx - 20 + lean * 1.25 + thrown, cy - 40, MUTED))
        return "".join(out)

    def mini_Ft(cx, top, kind, color):
        """Малий графік F(t): kind='step' або 'ramp'."""
        out = []
        w, h = 250, 96
        x0, y0 = cx - w / 2, top
        yb = y0 + h            # низ (F=0)
        yt = y0 + 14           # рівень кінцевої сили
        out.append(line(x0, yb, x0 + w + 8, yb, color=INK, sw=1.5))
        out.append(line(x0, yb + 3, x0, y0 + 6, color=INK, sw=1.5))
        out.append(text(x0 - 8, y0 + 12, "F", size=12.5, italic=True, anchor="end", color=color, bold=True))
        out.append(text(x0 + w + 6, yb + 16, "t", size=12, italic=True, anchor="end", color=MUTED))
        if kind == "step":
            xj = x0 + w * 0.42
            out.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                       'fill="none" stroke="%s" stroke-width="3"/>'
                       % (x0, yb, xj, yb, xj, yt, x0 + w, yt, color))
            out.append(text(xj + 6, y0 + 40, "миттєво → ривок ∞", size=11, color=JC, anchor="start", bold=True))
        else:
            xa, xb = x0 + w * 0.18, x0 + w * 0.72
            out.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                       'fill="none" stroke="%s" stroke-width="3"/>'
                       % (x0, yb, xa, yb, xb, yt, x0 + w, yt, color))
            out.append(text(xa + 4, y0 + 6, "по косій → ривок скінченний", size=11, color="#1c7a43", anchor="start", bold=True))
        out.append(text(x0 + w + 4, yt, "F_к", size=11, color=color, anchor="start", italic=True))
        return "".join(out)

    # ── ліворуч: удар ──
    f.append(textbox(235, 86, "Раптова сила (крок)", size=14, pad=8,
                     fill="#fbe9e4", stroke=XC, sw=1.5, color=XC, bold=True)[0])
    f.append(person(200, 210, thrown=64))
    f.append(uarrow_note(f, 300, 196))         # велика стрілка сили
    f.append(mini_Ft(235, 300, "step", XC))
    f.append(text(235, 424, "тіло не встигає підібратися — кидає поштовхом", size=12, color=INK))

    # ── праворуч: плавно ──
    f.append(textbox(705, 86, "Плавна сила (розгін)", size=14, pad=8,
                     fill="#e6f5ec", stroke="#1c7a43", sw=1.5, color="#1c7a43", bold=True)[0])
    f.append(person(670, 210, thrown=16))
    f.append(uarrow_note(f, 770, 196, big=False))
    f.append(mini_Ft(705, 300, "ramp", "#1c7a43"))
    f.append(text(705, 424, "м'язи встигають напружитись — сила лягає м'яко", size=12, color=INK))

    return render(os.path.join(IMG, "force-onset.svg"), W, H, *f)


def uarrow_note(flist, x, y, big=True):
    """Горизонтальна стрілка сили F, що входить у постать (повертає рядок)."""
    L = 58 if big else 40
    sw = 4.2 if big else 3.0
    out = arrow(x, y, x - L, y, color=XC if big else "#1c7a43", sw=sw)
    out += text(x + 6, y + 5, "F", size=15, bold=True, italic=True,
                color=XC if big else "#1c7a43", anchor="start")
    return out


# ── Фігура 4 (до hist-вставки): вежа названих похідних 0..6 ──────────────────
def fig_names_tower():
    W, H = 940, 712
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Вежа похідних: де кінчаються описові імена й починаються власні",
                  size=17, bold=True))

    CX_NOT, CX_NAME, X_PROV = 108, 300, 476
    DIV1, DIV2 = 206, 456
    row_top0, rh = 74, 78

    PLAY = "#c2410c"      # тепла палена вохра — жартівливі імена
    tint = {"base": "#f4f6f8", "hero": "#fdeee2", "play": "#fff4e6"}
    ncol = {"base": INK, "hero": JC, "play": PLAY}

    # шапка стовпців
    f.append(text(CX_NOT, 62, "похідна", size=12.5, color=MUTED, bold=True))
    f.append(text(CX_NAME, 62, "ім'я", size=12.5, color=MUTED, bold=True))
    f.append(text(X_PROV, 62, "звідки взялося", size=12.5, color=MUTED, bold=True, anchor="start"))

    rows = [
        ("x",        "положення",     "base", ["де перебуває тіло"]),
        ("dx/dt",    "швидкість",     "base", ["як швидко тіло зсувається"]),
        ("d²x/dt²",  "прискорення",   "base", ["як швидко росте швидкість"]),
        ("d³x/dt³",  "jerk · ривок",  "hero", ["побутове слово (XVI ст.) — «різкий смик»;",
                                               "у техніку ввійшло у XX ст. (комфорт їзди),",
                                               "означене в ISO 2041 (1990)"]),
        ("d⁴x/dt⁴",  "snap",          "play", ["Ф. Ґіббс, Physics FAQ, вересень 1996;",
                                               "давніший суперник — jounce"]),
        ("d⁵x/dt⁵",  "crackle",       "play", ["Ґіббс 1996 — за трьома чоловічками",
                                               "з коробки пластівців Rice Krispies"]),
        ("d⁶x/dt⁶",  "pop",           "play", ["Ґіббс 1996"]),
    ]

    for i, (notn, name, cat, prov) in enumerate(rows):
        top = row_top0 + i * rh
        cy = top + rh / 2
        # смуга рядка
        f.append(rect(40, top + 4, 860, rh - 8, fill=tint[cat], stroke="#e2e6ea", sw=1.1, rx=7))
        # порядок n у кружечку зліва
        f.append(circle(60, cy, 12, fill=BG, stroke=ncol[cat], sw=1.8))
        f.append(text(60, cy + 4.5, str(i), size=12.5, color=ncol[cat], bold=True))
        # нотація похідної
        f.append(text(CX_NOT + 14, cy + 5, notn, size=14, color=MUTED, italic=True))
        # ім'я (рамка, що сама підганяється)
        f.append(textbox(CX_NAME, cy, name, size=14.5,
                         fill=BG, stroke=ncol[cat], sw=1.7, color=ncol[cat],
                         bold=(cat != "base"))[0])
        # провенанс — короткі рядки, лівопритиснуті
        ny = cy - (len(prov) - 1) * 8.5
        for ln in prov:
            f.append(text(X_PROV, ny + 4, ln, size=11.5, color=INK, anchor="start"))
            ny += 17
        # вертикальні роздільники стовпців
        f.append(line(DIV1, top + 6, DIV1, top + rh - 6, color="#e2e6ea", sw=1.0))
        f.append(line(DIV2, top + 6, DIV2, top + rh - 6, color="#e2e6ea", sw=1.0))

    b = textbox(W / 2, 690,
                "Перші три щаблі мають описові імена; від ривка починаються власні. jerk прийшов з інженерії комфорту їзди,\n"
                "а напівжартівливі snap · crackle · pop дав Філіп Ґіббс (1996) за трьома чоловічками з коробки пластівців.",
                size=12, pad=10, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "names-tower.svg"), W, H, *f)


# ═══ Фігури до вставки proj-scurve-profile ═══════════════════════════════════
def _scurve(dist, V, A, J):
    """Спланувати симетричний 7-фазний профіль спокій→спокій (той самий алгоритм,
    що в C-коді вставки): повернути межі фаз і стан (a,v,x) на початку кожної фази."""
    if V * J >= A * A:                       # плато прискорення є
        Tj, Ta, vpk = A / J, V / A - A / J, V
    else:                                    # трикутне прискорення (пік < A)
        Tj, Ta, vpk = math.sqrt(V / J), 0.0, V
    d_acc = vpk * (2 * Tj + Ta) / 2
    d_cru = dist - 2 * d_acc
    if d_cru >= 0:
        Tv = d_cru / vpk
    else:                                    # короткий хід — крейсера нема
        Tv = 0.0
        p = A * A / J
        vpk = (-p + math.sqrt(p * p + 4 * A * dist)) / 2
        if vpk >= A * A / J:                 # прискорення все ще дістає A
            Tj, Ta = A / J, vpk / A - A / J
        else:                                # навіть без плато — трикутник
            vpk = (dist * dist * J / 4) ** (1.0 / 3.0)
            Tj, Ta = math.sqrt(vpk / J), 0.0
    dur = [Tj, Ta, Tj, Tv, Tj, Ta, Tj]
    js = [+J, 0.0, -J, 0.0, -J, 0.0, +J]
    t = [0.0]; a0 = [0.0]; v0 = [0.0]; x0 = [0.0]
    for k in range(7):
        T = dur[k]; a = a0[k]; v = v0[k]; x = x0[k]; jk = js[k]
        t.append(t[k] + T)
        a0.append(a + jk * T)
        v0.append(v + a * T + 0.5 * jk * T * T)
        x0.append(x + v * T + 0.5 * a * T * T + jk * T ** 3 / 6)
    return {"t": t, "j": js, "a0": a0, "v0": v0, "x0": x0,
            "dur": dur, "total": t[-1]}


def _scurve_at(s, t):
    k = 0
    while k < 6 and t >= s["t"][k + 1]:
        k += 1
    tau = t - s["t"][k]; jk = s["j"][k]
    a = s["a0"][k] + jk * tau
    v = s["v0"][k] + s["a0"][k] * tau + 0.5 * jk * tau * tau
    x = s["x0"][k] + s["v0"][k] * tau + 0.5 * s["a0"][k] * tau * tau + jk * tau ** 3 / 6
    return a, v, x


def fig_scurve_anatomy():
    """Стос j → a → v → x для одного руху: кожен графік — інтеграл попереднього."""
    s = _scurve(10.0, 2.0, 1.0, 1.0)          # Tj=Ta=1, Tv=2, total=8, L=10
    T = s["total"]
    W, H = 900, 918
    PL, PW = 108, 660
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Анатомія S-профілю: ривок інтегрується в положення", size=18, bold=True))

    def Xt(t):
        return PL + t / T * PW

    PH = 150
    panels = [("j", 66, "j", JC, True, 1.2),
              ("a", 258, "a", AC, True, 1.2),
              ("v", 450, "v", VC, False, 2.25),
              ("x", 642, "x", XC, False, 10.6)]

    top0 = panels[0][1] - 6
    bot_last = panels[-1][1] + PH + 6
    # крейсерська смуга (T4) — блідо-зелена, ЗА графіками
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eef7f1"/>'
             % (Xt(s["t"][3]), top0, Xt(s["t"][4]) - Xt(s["t"][3]), bot_last - top0))
    for tb in s["t"]:
        f.append(line(Xt(tb), top0, Xt(tb), bot_last, color="#d0d7de", sw=1.0, dash="3,5"))

    def draw_panel(key, top, ylabel, color, signed, ymax):
        out = []
        bottom = top + PH
        yz = (top + bottom) / 2 if signed else bottom - 8
        span = (PH / 2 - 16) if signed else (PH - 22)

        def Yy(val):
            return yz - val / ymax * span

        out.append(line(PL - 6, yz, PL + PW + 30, yz, color=INK, sw=1.4))
        out.append(line(PL, bottom + 2, PL, top - 4, color=INK, sw=1.4))
        out.append(text(PL - 16, top + 14, ylabel, size=15, italic=True, anchor="end", color=color, bold=True))
        if key == "j":
            for k in range(7):
                jk = s["j"][k]
                if jk == 0:
                    continue
                x0p, x1p = Xt(s["t"][k]), Xt(s["t"][k + 1])
                yv = Yy(jk)
                out.append(rect(x0p, min(yv, yz), x1p - x0p, abs(yv - yz),
                                fill="#fdf0e6", stroke=JC, sw=1.8, rx=2))
            out.append(text(Xt(0.5), Yy(1.0) - 8, "+J", size=12, color=JC, bold=True))
            out.append(text(Xt(2.5), Yy(-1.0) + 18, "−J", size=12, color=JC, bold=True))
        else:
            pts = []
            n = 240
            for i in range(n + 1):
                tt = T * i / n
                a, v, x = _scurve_at(s, tt)
                val = {"a": a, "v": v, "x": x}[key]
                pts.append("%.1f,%.1f" % (Xt(tt), Yy(val)))
            out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                       % (" ".join(pts), color))
        if key == "a":
            out.append(line(PL, Yy(1.0), PL + PW, Yy(1.0), color=AC, sw=0.9, dash="2,4"))
            out.append(line(PL, Yy(-1.0), PL + PW, Yy(-1.0), color=AC, sw=0.9, dash="2,4"))
            out.append(text(PL + PW + 8, Yy(1.0) + 4, "+A", size=11.5, color=AC, anchor="start", bold=True))
            out.append(text(PL + PW + 8, Yy(-1.0) + 4, "−A", size=11.5, color=AC, anchor="start", bold=True))
        if key == "v":
            out.append(line(PL, Yy(2.0), PL + PW, Yy(2.0), color=VC, sw=0.9, dash="2,4"))
            out.append(text(PL + PW + 8, Yy(2.0) + 4, "V", size=11.5, color=VC, anchor="start", bold=True))
        if key == "x":
            out.append(text(PL + PW + 8, Yy(10.0) + 4, "L", size=11.5, color=XC, anchor="start", bold=True))
        return "".join(out)

    for key, top, ylabel, color, signed, ymax in panels:
        f.append(draw_panel(key, top, ylabel, color, signed, ymax))

    ylab = panels[-1][1] + PH + 28
    names = ["T₁", "T₂", "T₃", "T₄", "T₅", "T₆", "T₇"]
    subs = ["+J", "0", "−J", "0", "−J", "0", "+J"]
    for k in range(7):
        xc = (Xt(s["t"][k]) + Xt(s["t"][k + 1])) / 2
        f.append(text(xc, ylab, names[k], size=12.5, bold=True, color=INK))
        f.append(text(xc, ylab + 16, "j=" + subs[k], size=10, color=MUTED))
    f.append(text(PL + PW + 22, panels[-1][1] + PH + 2, "t", size=13, italic=True, anchor="end"))

    b = textbox(W / 2, 882,
                "Ривок — прямокутні сходинки ±J. Кожен наступний графік — інтеграл попереднього:\n"
                "трапеція прискорення → S-крива швидкості → плавне положення.\n"
                "Розгін T₁–T₃, крейсер T₄ (блідо-зелений), гальмування T₅–T₇.",
                size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "scurve-anatomy.svg"), W, H, *f)


def fig_scurve_regimes():
    """Три випадки форми a(t), які планувальник мусить розрізняти."""
    W, H = 960, 442
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Три випадки, які мусить розрізняти планувальник", size=18, bold=True))

    cases = [
        (_scurve(10.0, 2.0, 1.0, 1.0), "Довгий хід", "плато a + крейсер", "V·J ≥ A², хід довгий"),
        (_scurve(10.0, 0.5, 1.0, 1.0), "Мала швидкість", "трикутник a + крейсер", "V·J < A²"),
        (_scurve(3.0, 5.0, 1.0, 1.0), "Короткий хід", "плато a, без крейсера", "2·d_розг = L, Tv = 0"),
    ]
    colw = W / 3
    for i, (s, title, shape, cond) in enumerate(cases):
        cx = colw * (i + 0.5)
        PL = colw * i + 50
        PW = colw - 88
        top, bot = 100, 250
        yz = (top + bot) / 2
        T = s["total"]
        span = (bot - top) / 2 - 14

        def Xt(t, PL=PL, PW=PW, T=T):
            return PL + t / T * PW

        def Yy(val):
            return yz - val / 1.18 * span

        f.append(textbox(cx, 62, title, size=13.5, pad=7, fill=FILL, stroke=LINE, sw=1.4, bold=True)[0])
        f.append(line(PL, Yy(1.0), PL + PW, Yy(1.0), color=AC, sw=0.8, dash="2,4"))
        f.append(line(PL, Yy(-1.0), PL + PW, Yy(-1.0), color=AC, sw=0.8, dash="2,4"))
        f.append(text(PL - 2, Yy(1.0) - 5, "+A", size=10.5, color=AC, anchor="start", bold=True))
        f.append(text(PL - 2, Yy(-1.0) + 14, "−A", size=10.5, color=AC, anchor="start", bold=True))
        f.append(line(PL - 4, yz, PL + PW + 12, yz, color=INK, sw=1.3))
        f.append(line(PL, bot + 4, PL, top - 6, color=INK, sw=1.3))
        f.append(text(PL - 12, top + 4, "a", size=13, italic=True, anchor="end", color=AC, bold=True))
        f.append(text(PL + PW + 10, yz - 6, "t", size=11.5, italic=True, anchor="end", color=MUTED))
        pts = []
        n = 220
        for k in range(n + 1):
            tt = T * k / n
            a, v, x = _scurve_at(s, tt)
            pts.append("%.1f,%.1f" % (Xt(tt), Yy(a)))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), AC))
        f.append(textbox(cx, 300, shape, size=12, pad=7, fill="#f0eaf6", stroke=AC, sw=1.3, color=AC, bold=True)[0])
        f.append(textbox(cx, 340, cond, size=11.5, pad=6, fill=FILL, stroke=LINE, sw=1.1)[0])
        if i > 0:
            f.append(line(colw * i, 50, colw * i, 372, color="#e5e9ee", sw=1.1, dash="4,6"))

    b = textbox(W / 2, 410,
                "Один і той самий код дає всі три: зайві фази просто мають нульову тривалість\n"
                "(крейсер Tv=0 у короткому ході; плато Ta=0 у трикутному).",
                size=12, pad=10, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "scurve-regimes.svg"), W, H, *f)


# ═══ Фігури до вставки math-higher-derivatives ═══════════════════════════════
# ── Профілі мінімального ривка x, v, a, j (нормовано D=1, T=1) ────────────────
def fig_mj_profiles():
    W, H = 830, 936
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Траєкторія мінімального ривка: уся драбина", size=18, bold=True))
    f.append(text(W / 2, 52, "нормовано: відстань D = 1, час T = 1, τ = t/T", size=12.5, color=MUTED))

    PL, PW, PH = 96, 330, 150
    tops = (78, 274, 470, 666)

    def panel(top, fn, ymin, ymax, ylabel, formula, color, box_fill=FILL,
              zeroline=False, peak=None):
        out = []
        bottom = top + PH
        span = ymax - ymin

        def Xx(t):
            return PL + t * PW

        def Yy(v):
            return bottom - (v - ymin) / span * (PH - 20)

        out.append(line(PL, bottom, PL + PW + 24, bottom, color=INK, sw=1.6))
        out.append(line(PL, bottom, PL, top + 2, color=INK, sw=1.6))
        out.append(text(PL - 14, top + 12, ylabel, size=15, italic=True, anchor="end", color=color, bold=True))
        if zeroline and ymin < 0 < ymax:
            yz = Yy(0)
            out.append(line(PL, yz, PL + PW + 24, yz, color=MUTED, sw=1.0, dash="3,4"))
            out.append(text(PL - 6, yz + 4, "0", size=11, anchor="end", color=MUTED))
        pts = []
        tt = 0.0
        while tt <= 1.0 + 1e-9:
            pts.append("%.1f,%.1f" % (Xx(tt), Yy(fn(tt))))
            tt += 0.005
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                   % (" ".join(pts), color))
        if peak is not None:
            px, pv = peak
            out.append(line(Xx(px), Yy(pv), Xx(px), bottom, color=color, sw=1.0, dash="3,3"))
            out.append(circle(Xx(px), Yy(pv), 3.4, fill=color, stroke=color, sw=1))
        for tv, lbl in ((0, "0"), (0.5, "½"), (1.0, "1")):
            out.append(line(Xx(tv), bottom, Xx(tv), bottom + 5, color=INK, sw=1.2))
            out.append(text(Xx(tv), bottom + 18, lbl, size=11, color=MUTED))
        out.append(text(PL + PW + 18, bottom + 18, "τ", size=13, italic=True, color=MUTED))
        out.append(textbox(PL + PW + 172, top + PH / 2, formula, size=12.5, pad=10,
                           fill=box_fill, stroke=color, sw=1.5, color=color, bold=True)[0])
        return "".join(out)

    f.append(panel(tops[0], lambda t: 10 * t ** 3 - 15 * t ** 4 + 6 * t ** 5,
                   0, 1.08, "x", "x = D · (10τ³\n− 15τ⁴ + 6τ⁵)\nS-крива 0 → D", XC))
    f.append(panel(tops[1], lambda t: 30 * t * t * (1 - t) ** 2,
                   0, 2.05, "v", "v = (30D/T)\n· τ²(1−τ)²\nдзвін, пік 1.875·D/T", VC,
                   peak=(0.5, 1.875)))
    f.append(panel(tops[2], lambda t: 60 * t * (1 - t) * (1 - 2 * t),
                   -6.6, 6.6, "a", "a = (60D/T²)\n· τ(1−τ)(1−2τ)\nчерез нуль при ½", AC,
                   zeroline=True))
    f.append(panel(tops[3], lambda t: 60 * (6 * t * t - 6 * t + 1),
                   -42, 70, "j", "j = (60D/T³)\n· (6τ²−6τ+1)\n≠ 0 на кінцях", JC,
                   box_fill="#fdf0e6", zeroline=True))

    b = textbox(W / 2, 902,
                "Одна вимога — мінімум ∫j²dt — дає многочлен 5-го степеня: положення S-крива,\n"
                "швидкість дзвоноподібна (та сама, що в руху живої руки), а ривок скінченний, але на кінцях ненульовий",
                size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "mj-profiles.svg"), W, H, *f)


if __name__ == "__main__":
    fig_deriv_ladder()
    fig_profiles()
    fig_force_onset()
    fig_names_tower()
    fig_scurve_anatomy()
    fig_scurve_regimes()
    fig_mj_profiles()
    print("OK: фігури у", IMG)
