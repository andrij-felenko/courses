# -*- coding: utf-8 -*-
"""Фігури для статті «Тертя кочення». Запуск із теки теми: python figs.py"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HOT = "#fdecea"   # тепла заливка (тиск / втрати)


def tick_span(x1, x2, y, label, size=13):
    """Горизонтальний вимірювальний відрізок b із засічками й підписом над ним."""
    s = line(x1, y - 6, x1, y + 6, color=INK, sw=1.4)
    s += line(x2, y - 6, x2, y + 6, color=INK, sw=1.4)
    s += line(x1, y, x2, y, color=INK, sw=1.4)
    s += text((x1 + x2) / 2, y - 10, label, size=size, color=INK, bold=True)
    return s


# ── Фігура 1: зсув реакції вперед, пара сил, тяга ───────────────────────────
def fig_force_shift():
    W, H = 740, 500
    ox, oy, r = 360, 260, 140
    yg = oy + r                     # рівень опори = 400
    bvis = 78                       # перебільшений зсув реакції
    xN = ox + bvis
    p = []
    # опора
    p.append(line(60, yg, 690, yg, color=INK, sw=2.5))
    for gx in range(70, 690, 26):   # штрихування ґрунту
        p.append(line(gx, yg, gx - 12, yg + 12, color=MUTED, sw=1))
    # колесо
    p.append(circle(ox, oy, r, fill=FILL, stroke=LINE, sw=2))
    p.append(circle(ox, oy, 6, fill=INK, stroke=INK, sw=1))
    # центральна вертикаль (через вісь)
    p.append(line(ox, oy, ox, yg, color=MUTED, sw=1.2, dash="5 5"))
    # напрямок руху
    p.append(arrow(300, 96, 440, 96, color=INK, sw=2))
    p.append(text(370, 86, "рух", size=13, color=INK))
    # обертання ω (дуга над центром, за годинниковою для руху вправо)
    a1, a2 = math.radians(132), math.radians(48)
    x1, y1 = ox + 78 * math.cos(a1), oy - 78 * math.sin(a1)
    x2, y2 = ox + 78 * math.cos(a2), oy - 78 * math.sin(a2)
    p.append('<path d="M%.1f %.1f A 78 78 0 0 0 %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (x1, y1, x2, y2, INK))
    p.append(text(300, 198, "ω", size=16, color=INK, anchor="end", italic=True))
    # вага W (вниз крізь вісь)
    p.append(arrow(ox, oy, ox, oy + 100, color=NEG, sw=2.4))
    p.append(text(ox - 12, oy + 70, "W (вага)", size=13, color=NEG, anchor="end"))
    # реакція N (вгору, зсунута вперед)
    p.append(arrow(xN, yg, xN, oy - 8, color=POS, sw=2.4))
    p.append(text(xN + 10, oy + 6, "N (реакція)", size=13, color=POS, anchor="start"))
    # тяга P (горизонтально на осі)
    p.append(arrow(ox, oy, ox + 150, oy, color=FIELD, sw=2.4))
    p.append(text(ox + 158, oy - 6, "P (тяга)", size=13, color=FIELD, anchor="start"))
    p.append(text(ox + 130, oy + 20, "плече R", size=12, color=MUTED))
    # позначка зсуву b під опорою
    p.append(tick_span(ox, xN, yg + 22, "b"))
    p.append(text((ox + xN) / 2, yg + 44, "(зсув перебільшено)", size=11, color=MUTED))
    render(os.path.join(OUT, 'wheel-force-shift.svg'), W, H, "\n".join(p),
           title="Зсув реакції вперед — момент, що гальмує кочення")


# ── Фігура 2: несиметричний тиск (ліворуч) + петля гістерезису (праворуч) ────
def fig_hysteresis():
    W, H = 840, 440
    p = []
    # ── ліва панель: розподіл тиску в плямі ──
    gy = 320
    p.append(text(215, 58, "Тиск у плямі несиметричний", size=14, bold=True))
    p.append(line(70, gy, 380, gy, color=INK, sw=2))
    # горб тиску (пік зсунутий уперед — праворуч)
    hump = "M110 320 L150 286 L192 258 L234 240 L262 232 L296 250 L330 286 L352 320 Z"
    p.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (hump, HOT, POS))
    p.append(text(196, 300, "тиск", size=12, color=POS))
    # вісь колеса (центр плями)
    p.append(line(224, gy, 224, 150, color=MUTED, sw=1.2, dash="5 5"))
    p.append(text(224, 142, "вісь колеса", size=11, color=MUTED))
    # рівнодійна N (у центроїді — попереду центра)
    p.append(arrow(263, gy, 263, 120, color=INK, sw=2.4))
    p.append(text(271, 132, "N — рівнодійна", size=12, color=INK, anchor="start"))
    # зсув b
    p.append(tick_span(224, 263, gy + 20, "b"))
    p.append(text(120, 338, "зад", size=11, color=MUTED))
    p.append(text(345, 338, "перед", size=11, color=MUTED))
    p.append(arrow(150, 96, 300, 96, color=MUTED, sw=1.6))
    p.append(text(225, 86, "рух", size=11, color=MUTED))
    # ── права панель: петля гістерезису ──
    ox, oy = 480, 320             # початок осей
    p.append(text(645, 58, "Петля гістерезису", size=14, bold=True))
    p.append(arrow(ox, oy, ox, 96, color=INK, sw=1.6))       # вісь напруження
    p.append(arrow(ox, oy, 800, oy, color=INK, sw=1.6))      # вісь деформації
    p.append(text(ox + 4, 90, "напруження σ", size=11, color=MUTED, anchor="start"))
    p.append(text(792, oy + 26, "деформація ε", size=11, color=MUTED, anchor="end"))
    # заливка петлі
    loop = ("M480 320 Q556 296 706 150 Q604 240 480 320 Z")
    p.append('<path d="%s" fill="%s" stroke="none"/>' % (loop, HOT))
    # крива навантаження (верхня)
    p.append('<path d="M480 320 Q556 296 706 150" fill="none" stroke="%s" '
             'stroke-width="2.4" marker-end="url(#arrow)"/>' % POS)
    # крива розвантаження (нижня)
    p.append('<path d="M706 150 Q604 240 480 320" fill="none" stroke="%s" '
             'stroke-width="2.4" marker-end="url(#arrow)"/>' % NEG)
    p.append(text(556, 188, "навантаження", size=11, color=POS, anchor="start"))
    p.append(text(600, 300, "розвантаження", size=11, color=NEG, anchor="start"))
    p.append(text(600, 258, "площа = тепло", size=11, color=INK))
    render(os.path.join(OUT, 'hysteresis.svg'), W, H, "\n".join(p),
           title="Звідки береться зсув b: гістерезис матеріалу")


# ── Фігура 3: спектр C_rr на логарифмічній шкалі ────────────────────────────
def fig_crr_spectrum():
    W, H = 780, 360
    x0, x1 = 270, 740             # межі осі в пікселях
    vmin, vmax = 3e-4, 4e-1
    lo, hi = math.log10(vmin), math.log10(vmax)

    def px(v):
        return x0 + (math.log10(v) - lo) / (hi - lo) * (x1 - x0)

    rows = [
        ("сталь по рейці", 0.0005, "0.0005", FIELD),
        ("велосипед (шосе)", 0.003, "0.003", FIELD),
        ("легкова шина, асфальт", 0.012, "0.012", "#e08a1e"),
        ("ґрунтова дорога", 0.05, "0.05", POS),
        ("шина на піску", 0.25, "0.25", POS),
    ]
    p = []
    # сітка декад
    for gv, lbl in [(0.001, "0.001"), (0.01, "0.01"), (0.1, "0.1")]:
        gx = px(gv)
        p.append(line(gx, 58, gx, 292, color="#d9dee3", sw=1, dash="4 4"))
        p.append(text(gx, 312, lbl, size=12, color=MUTED))
    p.append(line(x0, 58, x0, 292, color=INK, sw=1.5))
    y = 82
    for name, v, vlbl, col in rows:
        bx = px(v)
        p.append(rect(x0, y - 15, max(bx - x0, 3), 30, fill=col, stroke=col, sw=1, rx=4))
        p.append(text(x0 - 12, y + 5, name, size=12, color=INK, anchor="end"))
        p.append(text(bx + 8, y + 5, vlbl, size=12, color=INK, anchor="start", bold=True))
        y += 48
    p.append(text(x0 + 235, 336, "менше — ефективніше →", size=11, color=MUTED))
    render(os.path.join(OUT, 'crr-spectrum.svg'), W, H, "\n".join(p),
           title="Коефіцієнт опору коченню C_rr (логарифмічна шкала)")


# ── Фігура 4 (вставка hist): хронологія суперечки ───────────────────────────
def fig_hist_timeline():
    W, H = 900, 616
    spine = 176
    y0, pitch = 82, 68
    bx, bw = 206, 660
    rows = [
        ("1685", "Роберт Гук", "причина — опора вгинається, а частина деформації не повертається",
         FILL, LINE),
        ("1781", "Шарль-Оґюстен де Кулон", "циліндри по дубовій дошці: опір ∝ навантаженню й ∝ 1/діаметр",
         "#fdecea", POS),
        ("1831–1834", "Артюр Морен", "динамометр у Меці: закони тертя підтверджено, Кулон стає каноном",
         FILL, LINE),
        ("1837", "Жуль Дюпюї", "тяга возів на дорогах: опір ∝ 1/√діаметр, полеміка з Мореном",
         "#eaf0fd", NEG),
        ("1876", "Осборн Рейнольдс", "винне мікропроковзування всередині плями дотику",
         FILL, LINE),
        ("1882", "Генріх Герц", "теорія пружного контакту: розмір плями a ∝ √(N·R/E)",
         FILL, LINE),
        ("1955", "Девід Тейбор", "проковзування замало — губить енергію гістерезис у товщі",
         FILL, LINE),
        ("2021", "євромітка, ISO 28580", "C_rr не виводять із радіуса, а міряють шину на барабані",
         FILL, LINE),
    ]
    p = []
    p.append(line(spine, y0 - 30, spine, y0 + (len(rows) - 1) * pitch + 30,
                  color=MUTED, sw=2))
    for i, (yr, name, claim, fill, edge) in enumerate(rows):
        cy = y0 + i * pitch
        p.append(rect(bx, cy - 26, bw, 52, fill=fill, stroke=edge, sw=1.5))
        p.append(circle(spine, cy, 7, fill=edge, stroke=edge, sw=1.5))
        p.append(text(spine - 24, cy + 5, yr, size=13, color=INK, anchor="end", bold=True))
        p.append(text(bx + 16, cy - 4, name, size=14, color=INK, anchor="start", bold=True))
        fs = fit_font(claim, bw - 32, 12)
        p.append(text(bx + 16, cy + 17, claim, size=fs, color=MUTED, anchor="start"))
    render(os.path.join(OUT, 'hist-timeline.svg'), W, H, "\n".join(p),
           title="Двісті років навколо одного запитання: у якому степені радіус?")


# ── Фігура 5 (вставка hist): три степені радіуса на одній шкалі ─────────────
def fig_hist_exponents():
    W, H = 760, 470
    px0, px1 = 130, 700
    py0, py1 = 100, 400
    rmin, rmax = 0.1, 10.0
    vmin, vmax = 0.08, 12.0
    lx0, lx1 = math.log10(rmin), math.log10(rmax)
    ly0, ly1 = math.log10(vmin), math.log10(vmax)

    def X(r):
        return px0 + (math.log10(r) - lx0) / (lx1 - lx0) * (px1 - px0)

    def Y(v):
        return py1 - (math.log10(v) - ly0) / (ly1 - ly0) * (py1 - py0)

    p = []
    # смуга реальних радіусів коліс воза
    p.append(rect(X(0.45), py0, X(0.8) - X(0.45), py1 - py0,
                  fill="#eef1f4", stroke="none", sw=0, rx=0))
    p.append(mtext(X(0.6), 128, ["радіуси коліс", "одного воза"], size=11, color=MUTED))
    # сітка
    for r, lbl in [(0.1, "0.1"), (0.2, "0.2"), (0.5, "0.5"), (1, "1"), (2, "2"), (5, "5"), (10, "10")]:
        p.append(line(X(r), py0, X(r), py1, color="#d9dee3", sw=1, dash="4 4"))
        p.append(text(X(r), py1 + 22, lbl, size=12, color=MUTED))
    for v, lbl in [(0.1, "0.1"), (0.3, "0.3"), (1, "1"), (3, "3"), (10, "10")]:
        p.append(line(px0, Y(v), px1, Y(v), color="#eef0f2", sw=1))
        p.append(text(px0 - 12, Y(v) + 4, lbl, size=12, color=MUTED, anchor="end"))
    p.append(line(px0, py0, px0, py1, color=INK, sw=1.6))
    p.append(line(px0, py1, px1, py1, color=INK, sw=1.6))

    laws = [
        (lambda r: 1.0 / r, POS, "Кулон: 1/R"),
        (lambda r: r ** (-2.0 / 3), FIELD, "куля (Герц): 1/R²ᐟ³"),
        (lambda r: 1.0 / math.sqrt(r), NEG, "Дюпюї: 1/√R"),
    ]
    for fn, col, _ in laws:
        pts = []
        for k in range(0, 61):
            r = 10 ** (lx0 + (lx1 - lx0) * k / 60.0)
            pts.append("%.1f,%.1f" % (X(r), Y(fn(r))))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), col))
    p.append(circle(X(1), Y(1), 5, fill=BG, stroke=INK, sw=2))

    # легенда у вільному верхньому правому куті
    lx, ly, lw = 466, 112, 240
    p.append(rect(lx, ly, lw, 104, fill=BG, stroke="#d9dee3", sw=1.2))
    p.append(text(lx + 14, ly + 24, "залежність C_rr від R", size=12, color=INK,
                  anchor="start", bold=True))
    for i, (_, col, lbl) in enumerate(laws):
        yy = ly + 48 + i * 22
        p.append(line(lx + 14, yy - 4, lx + 44, yy - 4, color=col, sw=3))
        p.append(text(lx + 54, yy, lbl, size=12, color=INK, anchor="start"))

    p.append(text(px0, 82, "C_rr відносно значення при R = 1 м", size=12,
                  color=MUTED, anchor="start"))
    p.append(text((px0 + px1) / 2, py1 + 48, "радіус колеса R, м — логарифмічна шкала",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'hist-exponents.svg'), W, H, "\n".join(p),
           title="Три відповіді на одне запитання, зведені до R = 1 м")


# ── Фігура 6 (вставка proj): дві сили проти швидкості, точка перетину ───────
def fig_rolling_vs_drag():
    W, H = 820, 490
    X0, X1 = 90, 760           # межі поля по x
    Y0, Y1 = 60, 380           # верх і низ поля по y
    VMAX, FMAX = 150.0, 880.0  # км/год і Н
    M, CRR, CDA, RHO = 1200.0, 0.012, 0.66, 1.225
    F_ROLL = CRR * M * 9.81                     # 141.3 Н
    K = 0.5 * RHO * CDA                         # 0.4043 Н·с²/м²
    VSTAR = math.sqrt(F_ROLL / K) * 3.6         # 67.3 км/год

    def px(v):
        return X0 + v / VMAX * (X1 - X0)

    def py(f):
        return Y1 - f / FMAX * (Y1 - Y0)

    p = []
    # заливка двох царин
    p.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="#eaf0fd"/>'
             % (X0, Y0, px(VSTAR) - X0, Y1 - Y0))
    p.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="%s"/>'
             % (px(VSTAR), Y0, X1 - px(VSTAR), Y1 - Y0, HOT))
    # осі й засічки
    p.append(line(X0, 55, X0, Y1, color=INK, sw=1.8))
    p.append(line(X0, Y1, X1 + 12, Y1, color=INK, sw=1.8))
    p.append(text(58, 52, "сила, Н", size=12, color=MUTED, anchor="start"))
    for f in (0, 200, 400, 600, 800):
        p.append(line(X0 - 6, py(f), X0, py(f), color=INK, sw=1.4))
        p.append(text(X0 - 12, py(f) + 4, "%d" % f, size=12, color=MUTED, anchor="end"))
    for v in (0, 30, 60, 90, 120, 150):
        p.append(line(px(v), Y1, px(v), Y1 + 6, color=INK, sw=1.4))
        p.append(text(px(v), Y1 + 20, "%d" % v, size=12, color=MUTED))
    # крива опору повітря
    pts = []
    v = 0.0
    while v <= VMAX + 1e-9:
        pts.append("%.1f,%.1f" % (px(v), py(K * (v / 3.6) ** 2)))
        v += 2.5
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), POS))
    # пряма опору кочення
    p.append(line(X0, py(F_ROLL), X1, py(F_ROLL), color=NEG, sw=2.8))
    # вертикаль перетину й сама точка
    p.append(line(px(VSTAR), Y1, px(VSTAR), 200, color=MUTED, sw=1.4, dash="6 5"))
    p.append(circle(px(VSTAR), py(F_ROLL), 6, fill=BG, stroke=INK, sw=2.4))
    # підписи
    p.append(text(120, 310, "опір коченню C_rr·m·g = 141 Н", size=13, color=NEG, anchor="start"))
    p.append(text(742, 118, "опір повітря ½·ρ·C_d·A·v²", size=13, color=POS, anchor="end"))
    p.append(text(400, 190, "v* = 67 км/год", size=14, color=INK, anchor="start", bold=True))
    p.append(text(240, 426, "← панує кочення", size=13, color=NEG))
    p.append(text(575, 426, "панує повітря →", size=13, color=POS))
    p.append(text(425, 452, "швидкість, км/год", size=12, color=MUTED))
    render(os.path.join(OUT, 'rolling-vs-drag.svg'), W, H, "\n".join(p),
           title="Дві сили проти швидкості: де вони зрівнюються")


# ── Фігура 7 (вставка proj): швидкість перетину для різних машин ────────────
def fig_crossover_fleet():
    W, H = 820, 366
    X0, X1 = 300, 750          # 0…100 км/год
    VMAX = 100.0

    def px(v):
        return X0 + v / VMAX * (X1 - X0)

    rows = [
        ("велосипед із гонщиком", 15.3, FIELD),
        ("електросамокат",        23.8, FIELD),
        ("легковик-хетчбек",      67.3, "#e08a1e"),
        ("електроседан",          81.8, "#e08a1e"),
        ("фура, 40 т",            88.9, POS),
    ]
    p = []
    p.append(line(X0, 56, X0, 290, color=INK, sw=1.6))
    y = 78
    for name, v, col in rows:
        bx = px(v)
        p.append(rect(X0, y - 14, bx - X0, 28, fill=col, stroke=col, sw=1, rx=4))
        p.append(text(X0 - 12, y + 5, name, size=13, color=INK, anchor="end"))
        p.append(text(bx + 10, y + 5, "%.0f км/год" % v, size=13, color=INK,
                      anchor="start", bold=True))
        y += 46
    p.append(line(X0, 290, X1 + 12, 290, color=INK, sw=1.6))
    for v in (0, 25, 50, 75, 100):
        p.append(line(px(v), 290, px(v), 296, color=INK, sw=1.4))
        p.append(text(px(v), 314, "%d" % v, size=12, color=MUTED))
    p.append(text(750, 340, "км/год", size=12, color=MUTED, anchor="end"))
    render(os.path.join(OUT, 'crossover-fleet.svg'), W, H, "\n".join(p),
           title="Швидкість перетину v*: коли повітря дорожчає за колеса")


if __name__ == '__main__':
    fig_force_shift()
    fig_hysteresis()
    fig_crr_spectrum()
    fig_hist_timeline()
    fig_hist_exponents()
    fig_rolling_vs_drag()
    fig_crossover_fleet()
    print("OK:", os.listdir(OUT))


# ══ Фігури до вставки math-force-shift.md ═══════════════════════════════════
COLD = "#eaf0fd"   # холодна заливка (розвантаження)


def hatch(x1, x2, y, step=26, ln=12, color=MUTED):
    """Штрихування ґрунту під лінією опори."""
    out = []
    gx = x1
    while gx < x2:
        out.append(line(gx, y, gx - ln, y + ln, color=color, sw=1))
        gx += step
    return "\n".join(out)


# ── Схема: розподілені p(x) і q(x), а не зосереджена реакція ────────────────
def fig_fs_scheme():
    W, H = 900, 640
    yg = 470                       # рівень опори
    cx, cy, r = 410, 286, 200      # вісь колеса і радіус
    ap = 78                        # півдовжина плями в пікселях
    p = []
    # обід: коло, зрізане знизу рівнем опори (сплющення)
    pts = []
    for i in range(241):
        th = 2 * math.pi * i / 240
        pts.append("%.1f %.1f" % (cx + r * math.cos(th),
                                  min(cy + r * math.sin(th), yg)))
    p.append('<path d="M%s Z" fill="#fbfcfd" stroke="%s" stroke-width="2"/>'
             % (" L".join(pts), LINE))
    # опора
    p.append(line(70, yg, 830, yg, color=INK, sw=2.5))
    p.append(hatch(90, cx - ap - 10, yg))
    p.append(hatch(cx + ap + 30, 830, yg))
    # вісь
    p.append(circle(cx, cy, 6, fill=INK, stroke=INK, sw=1))
    p.append(text(cx - 14, cy - 12, "вісь O", size=13, color=INK, anchor="end"))
    # навантаження W і тяга P на осі
    p.append(arrow(cx, cy, cx, 396, color=NEG, sw=2.4))
    p.append(text(cx - 12, 366, "W (вага)", size=13, color=NEG, anchor="end"))
    p.append(arrow(cx, cy, 590, cy, color=FIELD, sw=2.4))
    p.append(text(500, 272, "P (тяга)", size=13, color=FIELD))
    # висота осі h
    p.append(line(600, cy, 742, cy, color=MUTED, sw=1, dash="5 5"))
    p.append(line(640, yg, 742, yg, color=MUTED, sw=1, dash="5 5"))
    p.append(arrow(750, cy, 750, yg, color=MUTED, sw=1.6))
    p.append(arrow(750, yg, 750, cy, color=MUTED, sw=1.6))
    p.append(text(762, 384, "h = R − δ", size=13, color=MUTED, anchor="start"))
    # розподілений тиск p(x): стрілки знизу вгору, спереду вищі
    for i in (-3, -2, -1, 0, 1, 2, 3):
        dx = i * ap / 4.0
        hgt = 52 * (1 - (dx / ap) ** 2)
        if dx < 0:
            hgt *= 0.4
        p.append(arrow(cx + dx, 473 + hgt, cx + dx, 473,
                       color=(POS if dx >= 0 else NEG), sw=2))
    p.append(text(318, 512, "p(x) — нормальний тиск", size=13, color=POS, anchor="end"))
    # дотична q(x) — назад
    p.append(arrow(470, 456, 350, 456, color=NEG, sw=2.2))
    p.append(text(410, 446, "q(x)", size=13, color=NEG))
    # півдовжини плями
    p.append(tick_span(cx - ap, cx, 552, "a"))
    p.append(tick_span(cx, cx + ap, 552, "a"))
    # вісь x
    p.append(arrow(300, 588, 560, 588, color=INK, sw=1.6))
    p.append(text(574, 582, "x", size=14, color=INK, anchor="start", italic=True))
    for xv, lbl in ((cx - ap, "−a"), (cx, "0"), (cx + ap, "+a")):
        p.append(line(xv, 582, xv, 594, color=INK, sw=1.4))
        p.append(text(xv, 614, lbl, size=13, color=INK))
    # напрямок руху
    p.append(arrow(140, 120, 280, 120, color=INK, sw=2))
    p.append(text(210, 108, "рух, швидкість v", size=13, color=INK))
    render(os.path.join(OUT, 'fs-scheme.svg'), W, H, "\n".join(p),
           title="Розрахункова схема: розподілені p(x) і q(x)")


# ── Кінематична лема: v_y = −v·x/R ─────────────────────────────────────────
def fig_fs_kinematics():
    W, H = 880, 570
    cx, y0, Rp, lev = 430, 400, 346.0, 340
    p = []

    def rim(x):
        return y0 - (x - cx) ** 2 / (2 * Rp)

    half = math.sqrt(2 * Rp * (y0 - lev))
    xa, xb = cx - half, cx + half
    # заливка вдавленого шару (між рівнем опори і ободом)
    arc = []
    xx = xa
    while xx <= xb:
        arc.append("%.1f %.1f" % (xx, rim(xx)))
        xx += 6
    p.append('<path d="M%.1f %.1f L%s L%.1f %.1f Z" fill="%s" stroke="none"/>'
             % (xa, lev, " L".join(arc), xb, lev, HOT))
    # обід
    rpts = []
    xx = 130
    while xx <= 730:
        rpts.append("%.1f %.1f" % (xx, rim(xx)))
        xx += 6
    p.append('<path d="M%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" L".join(rpts), LINE))
    # поверхня опори: рівна поза плямою, по ободу — в плямі
    p.append(line(70, lev, xa, lev, color=INK, sw=2.2))
    p.append(line(xb, lev, 810, lev, color=INK, sw=2.2))
    p.append('<path d="M%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" L".join(arc), INK))
    p.append(line(xa, lev, xb, lev, color=MUTED, sw=1, dash="5 5"))
    p.append(hatch(100, xa - 10, lev))
    p.append(hatch(xb + 30, 800, lev))
    # глибина δ
    p.append(line(cx, lev, cx, y0, color=INK, sw=1.4))
    p.append(line(cx - 6, lev, cx + 6, lev, color=INK, sw=1.4))
    p.append(line(cx - 6, y0, cx + 6, y0, color=INK, sw=1.4))
    p.append(text(442, 372, "δ", size=14, color=INK, anchor="start", italic=True))
    # товщина u(x)
    xu = 340
    p.append(line(xu, lev, xu, rim(xu), color=INK, sw=1.4))
    p.append(line(xu - 5, lev, xu + 5, lev, color=INK, sw=1.4))
    p.append(line(xu - 5, rim(xu), xu + 5, rim(xu), color=INK, sw=1.4))
    p.append(text(352, 367, "u(x)", size=13, color=INK, anchor="start"))
    # миттєвий центр
    p.append(circle(cx, y0, 6, fill=INK, stroke=INK, sw=1))
    p.append(text(404, 428, "C:  v = 0", size=13, color=INK, anchor="end"))
    # точка A на ободі попереду
    ax, ay = cx + 150, rim(cx + 150)
    p.append(line(cx, y0, ax, ay, color=MUTED, sw=1.4, dash="4 4"))
    p.append(circle(ax, ay, 6, fill=POS, stroke=POS, sw=1))
    p.append(text(ax + 12, ay - 14, "A", size=14, color=POS, anchor="start", bold=True))
    # швидкість точки A — перпендикуляр до CA
    dxv, dyv = ax - cx, ay - y0
    L = math.hypot(dxv, dyv)
    vx, vy = -dyv / L * 110, dxv / L * 110
    p.append(arrow(ax, ay, ax + vx, ay + vy, color=POS, sw=2.4))
    p.append(line(ax, ay, ax, ay + vy, color=MUTED, sw=1.2, dash="4 4"))
    p.append(line(ax, ay + vy, ax + vx, ay + vy, color=MUTED, sw=1.2, dash="4 4"))
    p.append(text(ax - 14, ay + vy * 0.62, "v·x/R", size=13, color=POS, anchor="end"))
    p.append(text(ax + vx + 14, ay + vy + 22, "≈ 0 (другого порядку)",
                  size=12, color=MUTED, anchor="start"))
    # підписи половин
    p.append(text(cx + 130, 296, "u̇ > 0: стиснення", size=13, color=POS))
    p.append(text(cx - 130, 296, "u̇ < 0: розправляння", size=13, color=NEG))
    # формула
    frag, _, _ = textbox(660, 128, "v_y(x) = − v·x / R\nu̇(x) = + v·x / R",
                         size=14, bold=True)
    p.append(frag)
    # рух
    p.append(arrow(140, 100, 280, 100, color=INK, sw=2))
    p.append(text(210, 88, "рух, швидкість v", size=13, color=INK))
    render(os.path.join(OUT, 'fs-kinematics.svg'), W, H, "\n".join(p),
           title="Кінематична лема: швидкість поверхні пропорційна зсуву x")


# ── Дві вітки тиску ↔ петля одного елемента ────────────────────────────────
def fig_fs_branches():
    W, H = 1000, 570
    beta = 0.35
    p = []
    # ── ліва панель: профіль тиску ──
    bx, ap, base, top = 280, 180, 380, 170
    p.append(text(280, 62, "тиск у плямі: дві вітки", size=14, bold=True))
    front = ["%.1f %.1f" % (bx, base)]
    xx = float(bx)
    while xx <= bx + ap:
        front.append("%.1f %.1f" % (xx, base - top * (1 - ((xx - bx) / ap) ** 2)))
        xx += 4
    front.append("%.1f %.1f" % (bx + ap, base))
    p.append('<path d="M%s Z" fill="%s" stroke="%s" stroke-width="2"/>'
             % (" L".join(front), HOT, POS))
    rear = ["%.1f %.1f" % (bx - ap, base)]
    xx = float(bx - ap)
    while xx <= bx:
        rear.append("%.1f %.1f" % (xx, base - beta * top * (1 - ((xx - bx) / ap) ** 2)))
        xx += 4
    rear.append("%.1f %.1f" % (bx, base))
    p.append('<path d="M%s Z" fill="%s" stroke="%s" stroke-width="2"/>'
             % (" L".join(rear), COLD, NEG))
    p.append(line(90, base, 470, base, color=INK, sw=2.2))
    frag, _, _ = textbox(392, 148, "навантаження\np = k·u(x)", size=13,
                         fill=HOT, stroke=POS)
    p.append(frag)
    frag, _, _ = textbox(160, 252, "розвантаження\np = β·k·u(x),  β < 1", size=13,
                         fill=COLD, stroke=NEG)
    p.append(frag)
    p.append(arrow(200, 100, 300, 100, color=INK, sw=1.8))
    p.append(text(250, 88, "рух", size=12, color=INK))
    p.append(text(bx - ap, 400, "−a", size=13, color=INK))
    p.append(text(bx - 10, 400, "0", size=13, color=INK, anchor="end"))
    p.append(text(bx + ap, 400, "+a", size=13, color=INK))
    p.append(line(bx, base, bx, 470, color=MUTED, sw=1.2, dash="5 5"))
    # рівнодійна N у центроїді
    bp = ap * 0.375 * (1 - beta) / (1 + beta)
    p.append(arrow(bx + bp, 500, bx + bp, 386, color=INK, sw=2.6))
    p.append(text(bx + bp + 12, 470, "N = ∫ p dx", size=13, color=INK, anchor="start"))
    p.append(tick_span(bx, bx + bp, 522, "b"))
    p.append(text(bx + 4, 552, "b = центр тиску", size=12, color=MUTED, anchor="start"))
    # ── права панель: петля одного елемента ──
    ox, oy, du, pk = 620, 420, 300, 260
    p.append(text(790, 62, "петля одного елемента", size=14, bold=True))
    p.append(arrow(ox, oy, ox, 130, color=INK, sw=1.6))
    p.append(arrow(ox, oy, 960, oy, color=INK, sw=1.6))
    p.append(text(ox - 10, 142, "p", size=14, color=INK, anchor="end", italic=True))
    p.append(text(790, 448, "u (деформація)", size=13, color=MUTED))
    p.append('<path d="M%d %d L%d %d L%d %d Z" fill="%s" stroke="none"/>'
             % (ox, oy, ox + du, oy - pk, ox + du, oy - beta * pk, HOT))
    p.append(arrow(ox, oy, ox + du, oy - pk, color=POS, sw=2.4))
    p.append(arrow(ox + du, oy - pk, ox + du, oy - beta * pk, color=INK, sw=1.8))
    p.append(arrow(ox + du, oy - beta * pk, ox, oy, color=NEG, sw=2.4))
    p.append(text(740, 262, "нахил k", size=13, color=POS, anchor="end"))
    p.append(text(800, 406, "нахил β·k", size=13, color=NEG))
    p.append(text(850, 300, "втрата за прохід", size=12, color=INK))
    p.append(line(ox + du, oy, ox + du, oy + 6, color=INK, sw=1.4))
    p.append(text(ox + du + 12, 442, "δ", size=13, color=INK, anchor="start", italic=True))
    frag, _, _ = textbox(790, 505, "площа петлі = ½·(1 − β)·k·δ² = ½·α·k·δ²",
                         size=13, bold=True)
    p.append(frag)
    render(os.path.join(OUT, 'fs-branches.svg'), W, H, "\n".join(p),
           title="Передня вітка навантажує, задня розвантажує — звідси і b, і втрати")


if __name__ == '__main__':
    fig_fs_scheme()
    fig_fs_kinematics()
    fig_fs_branches()
    print("OK math-force-shift figs")
