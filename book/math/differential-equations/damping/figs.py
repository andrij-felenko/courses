# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: три режими крокової відповіді ───────────────────────────────────
# Смикаємо систему ступінчастим входом і дивимось, як вона доповзає до цілі.
# Недогасована (ζ<1) перелітає й дзвенить; критична (ζ=1) — найшвидше без
# перельоту; перегасована (ζ>1) мляво повзе. Криві пораховані з точних формул
# крокової відповіді x¨+2ζω₀x˙+ω₀²x=ω₀²·1(t), нормовано ω₀=1.
def fig_three_regimes():
    W, H = 860, 452
    ox, oyb = 92, 388            # початок координат: t=0 при x=ox, значення 0 при y=oyb
    x_right, y_top = 812, 92
    tmax, ymax = 14.0, 1.62

    def X(t):
        return ox + (t / tmax) * (x_right - ox)

    def Y(v):
        return oyb - (v / ymax) * (oyb - y_top)

    parts = []
    parts.append(arrow(ox, oyb, x_right + 22, oyb, color=INK, sw=1.8))   # вісь часу
    parts.append(arrow(ox, oyb, ox, y_top - 12, color=INK, sw=1.8))      # вісь відгуку
    parts.append(text(x_right + 26, oyb + 4, 't', 13, INK, 'start', italic=True))
    parts.append(text(ox - 8, y_top - 16, 'відгук', 12, INK, 'end', bold=True))

    yt = Y(1.0)                                                          # рівень цілі
    parts.append(line(ox, yt, x_right, yt, color=MUTED, sw=1.3, dash="6 5"))
    parts.append(text(x_right + 4, yt + 4, 'ціль', 11, MUTED, 'start'))

    def curve(f, col, sw):
        pts = []
        N = 320
        for i in range(N + 1):
            t = tmax * i / N
            pts.append('%.1f,%.1f' % (X(t), Y(f(t))))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (' '.join(pts), col, sw))

    z = 0.2
    wd = math.sqrt(1 - z * z)
    under = lambda t: 1 - math.exp(-z * t) * (math.cos(wd * t) + (z / wd) * math.sin(wd * t))
    crit = lambda t: 1 - math.exp(-t) * (1 + t)
    zo = 2.0
    s1 = -zo + math.sqrt(zo * zo - 1)
    s2 = -zo - math.sqrt(zo * zo - 1)
    over = lambda t: 1 + (s2 * math.exp(s1 * t) - s1 * math.exp(s2 * t)) / (s1 - s2)

    parts.append(curve(over, FIELD, 2.6))
    parts.append(curve(under, POS, 2.6))
    parts.append(curve(crit, INK, 3.0))

    tp = math.pi / wd                                                   # мить першого піка
    parts.append(text(X(tp), Y(under(tp)) - 12, 'переліт', 11, POS, 'middle', italic=True))
    parts.append(text(X(11.3), Y(over(11.3)) + 18, 'повільно повзе', 11, FIELD, 'middle', italic=True))

    # легенда (верхня права зона — там криві вже осіли нижче)
    lx, ly, lw = 548, 104, 250
    parts.append(rect(lx, ly, lw, 80, fill="#ffffff", stroke="#e2e2e2", sw=1.3, rx=8))
    rows = [(POS, 2.6, 'ζ = 0.2  недогасований (дзвін)'),
            (INK, 3.0, 'ζ = 1  критичний (найшвидше)'),
            (FIELD, 2.6, 'ζ = 2  перегасований (мляво)')]
    for i, (col, sw, label) in enumerate(rows):
        yy = ly + 22 + i * 21
        parts.append(line(lx + 14, yy, lx + 40, yy, color=col, sw=sw))
        parts.append(text(lx + 48, yy + 4, label, 11, col, 'start'))

    render(os.path.join(IMG, 'three-regimes.svg'), W, H, *parts,
           title='Три режими відгуку на поштовх залежно від ζ')


# ── Фігура 2: одне рівняння, кілька втілень ──────────────────────────────────
# Абстрактна трійця «інерція · дисипація · пружність» дістає конкретне тіло в
# кожному домені: механіка (m,c,k) та електричний контур (L,R,1/C). Форма
# рівняння й коефіцієнт ζ ті самі — міняються лише підписи під ролями.
def fig_forms():
    W, H = 820, 470
    parts = []

    # канонічне рівняння + означення (банер угорі)
    b, bw, bh = textbox(W / 2, 80, 'x¨ + 2ζω₀·x˙ + ω₀²·x = 0',
                        size=18, bold=True, fill="#eef6ff", stroke=NEG, sw=1.8, pad=14)
    parts.append(b)
    parts.append(text(W / 2, 118, 'ω₀ = √(k/m) — власна частота     ·     ζ = c / (2√(mk)) — частка критичного демпфування',
                      12, MUTED, 'middle'))

    # колонки таблиці
    c0x, c0w = 60, 300     # роль
    c1x, c1w = 380, 180    # механіка
    c2x, c2w = 580, 180    # електрика

    # шапка
    hy = 150
    parts.append(text(c1x + c1w / 2, hy, 'МЕХАНІКА', 14, INK, 'middle', bold=True))
    parts.append(text(c2x + c2w / 2, hy, 'КОНТУР RLC', 14, INK, 'middle', bold=True))

    rowsY = [178, 244, 310]
    rowH = 58
    role = ['інерція\n(спротив прискоренню)',
            'дисипація\n(спротив швидкості)',
            'пружність\n(тягне до рівноваги)']
    mech = ['m\nмаса', 'c\nтертя', 'k\nжорсткість']
    elec = ['L\nіндуктивність', 'R\nопір', '1/C\n(з ємності C)']
    cols = [(POS, 0), (NEG, 1), (FIELD, 2)]   # колір рамки-ролі по рядках
    for r, ry in enumerate(rowsY):
        parts.append(fitbox(c0x, ry, c0w, rowH, role[r], size=13,
                            fill=FILL, stroke=cols[r][0], sw=1.6, color=INK))
        parts.append(fitbox(c1x, ry, c1w, rowH, mech[r], size=13,
                            fill="#ffffff", stroke=LINE, sw=1.3, color=INK))
        parts.append(fitbox(c2x, ry, c2w, rowH, elec[r], size=13,
                            fill="#ffffff", stroke=LINE, sw=1.3, color=INK))

    # спільний ζ (нижній банер): та сама формула, різні тіла
    fb = fitbox(60, 392, W - 120, 56,
                'той самий ζ = дисипація / (2·√(інерція · пружність))\n'
                'механіка:  ζ = c / (2√(mk))          електрика:  ζ = (R/2)·√(C/L)',
                size=13, fill="#fff8e1", stroke="#f0b429", sw=1.5, color=INK)
    parts.append(fb)

    render(os.path.join(IMG, 'second-order-forms.svg'), W, H, *parts,
           title='Одне рівняння другого порядку — кілька втілень')


# ── Фігура 3: вісь ζ і дзеркальна вісь Q ─────────────────────────────────────
# Число ζ на прямій ділить усі системи на недогасовані (ζ<1) й перегасовані
# (ζ>1) з межею ζ=1. Під кожним ζ — дзеркальне Q = 1/(2ζ). Особлива точка
# ζ=1/√2≈0.707 — «максимально пласка» межа частотної характеристики.
def fig_zeta_axis():
    W, H = 820, 340
    parts = []
    ay = 150
    x0 = 90
    sx = (770 - x0) / 2.2                  # масштаб: ζ=2.2 біля правого краю

    def X(z):
        return x0 + z * sx

    # осьова лінія
    parts.append(arrow(70, ay, 790, ay, color=INK, sw=2.0))
    parts.append(text(796, ay + 5, 'ζ', 15, INK, 'start', bold=True))

    # смуги режимів (над віссю)
    parts.append(rect(x0, 122, X(1) - x0, 26, fill="#fbecec", stroke="none", sw=0, rx=0))
    parts.append(rect(X(1), 122, 770 - X(1), 26, fill="#eef6ef", stroke="none", sw=0, rx=0))
    parts.append(text((x0 + X(1)) / 2, 112, 'ζ < 1  недогасований (дзвенить)', 11.5, POS, 'middle', bold=True))
    parts.append(text((X(1) + 770) / 2, 112, 'ζ > 1  перегасований', 11.5, FIELD, 'middle', bold=True))

    # легенда символів (порожня верхня права зона)
    parts.append(rect(548, 52, 250, 44, fill="#ffffff", stroke="#e2e2e2", sw=1.3, rx=8))
    parts.append(text(673, 71, 'ζ — коефіцієнт демпфування', 11, INK, 'middle'))
    parts.append(text(673, 89, 'Q — добротність = 1/(2ζ)', 11, INK, 'middle'))

    # позначки, підписи ζ і дзеркальні Q
    ticks = [(0, '0', '∞', INK, False),
             (0.2, '0.2', '2.5', POS, False),
             (0.5, '0.5', '1.0', POS, False),
             (0.707, '0.707', '0.71', NEG, True),
             (1, '1', '0.5', INK, True),
             (2, '2', '0.25', FIELD, False)]
    for z, zl, ql, col, strong in ticks:
        xx = X(z)
        parts.append(line(xx, ay - 6, xx, ay + 6, color=col, sw=2.2))
        parts.append(text(xx, ay + 22, zl, 12, col, 'middle', bold=strong))
        parts.append(text(xx, ay + 46, ql, 12, col, 'middle', bold=strong))
    parts.append(text(x0 - 4, ay + 46, 'Q:', 12, MUTED, 'end', italic=True))

    # межа ζ=1
    parts.append(circle(X(1), ay, 6, fill="#ffffff", stroke=INK, sw=2.4))
    parts.append(text(X(1), ay + 74, '↑ критичне: межа дзвону (ζ = 1, Q = 0.5)', 11.5, INK, 'middle', italic=True))
    parts.append(text(W / 2, ay + 100,
                      'ζ = 1/√2 ≈ 0.707  →  Q ≈ 0.71: «максимально пласка» межа частотної характеристики',
                      11.5, NEG, 'middle', italic=True))

    # формула-дзеркало (нижній банер)
    fb = fitbox(60, 288, W - 120, 40, 'ζ = 1 / (2Q)          Q = 1 / (2ζ)',
                size=16, fill="#ffffff", stroke="#e4e4e4", sw=1.4, color=INK, bold=True)
    parts.append(fb)

    render(os.path.join(IMG, 'zeta-axis.svg'), W, H, *parts,
           title='Вісь демпфування ζ і дзеркальна вісь добротності Q')


fig_three_regimes()
fig_forms()
fig_zeta_axis()
print('Done. SVG in', IMG)
