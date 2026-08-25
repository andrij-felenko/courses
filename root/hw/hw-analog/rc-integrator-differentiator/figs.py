# -*- coding: utf-8 -*-
"""Фігури до теми «RC-інтегратор і диференціатор» (аналогова, кутом теорії кіл).
Чотири фігури:
  two-circuits.svg   — ті самі R і C, два знімання виходу: на C → інтегратор, на R → диференціатор
  integrator-wave.svg— прямокутник на вході → трикутна (нахилена) напруга на C; умова τ ≫ T
  differentiator-wave.svg — фронт на вході → сплеск на R, що спадає; умова τ ≪ T
  freq-domain.svg    — спад/підйом 6 дБ/окт; смуга, де нахил справді = інтеграл / похідна
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _res(x, y, w=44, h=14):
    """Резистор-прямокутник із виводами; повертає (svg, лівий_вивід_x, правий_вивід_x)."""
    return rect(x, y - h / 2, w, h, fill=BG, stroke=LINE, sw=1.6, rx=2), x, x + w


def _cap_v(cx, cy, gap=8, plate=24):
    """Конденсатор вертикальний (дві пластини), центр (cx,cy). Виводи зверху й знизу."""
    out = []
    out.append(line(cx - plate / 2, cy - gap / 2, cx + plate / 2, cy - gap / 2, color=LINE, sw=2.4))
    out.append(line(cx - plate / 2, cy + gap / 2, cx + plate / 2, cy + gap / 2, color=LINE, sw=2.4))
    return "".join(out)


def two_circuits():
    """Один RC-дільник, два варіанти виходу: на C — інтегратор, на R — диференціатор."""
    W, H = 720, 380
    p = []

    def integrator(ox, oy):
        out = []
        # вхід (ліворуч) -> R -> вузол -> C -> земля; вихід на C
        rsvg, rl, rr = _res(ox + 30, oy)
        out.append(line(ox, oy, ox + 30, oy, color=LINE, sw=1.6))      # вхід до R
        out.append(rsvg)
        out.append(text(ox + 52, oy - 14, "R", size=14, bold=True))
        nx = rr + 36                                                   # вузол виходу
        out.append(line(rr, oy, nx, oy, color=LINE, sw=1.6))
        out.append(circle(nx, oy, 2.6, fill=INK, stroke=INK))
        # C вниз до землі
        out.append(line(nx, oy, nx, oy + 26, color=LINE, sw=1.6))
        out.append(_cap_v(nx, oy + 34))
        out.append(text(nx + 16, oy + 36, "C", size=14, bold=True, anchor="start"))
        out.append(line(nx, oy + 42, nx, oy + 60, color=LINE, sw=1.6))
        # земля
        for i, ww in enumerate((18, 11, 5)):
            out.append(line(nx - ww, oy + 60 + i * 5, nx + ww, oy + 60 + i * 5, color=LINE, sw=1.6))
        # вихід праворуч від вузла
        out.append(line(nx, oy, nx + 60, oy, color=LINE, sw=1.6))
        out.append(circle(nx + 60, oy, 3, fill=BG, stroke=LINE, sw=1.6))
        out.append(text(nx + 70, oy + 4, "вихід", size=12, color=MUTED, anchor="start"))
        out.append(text(ox - 6, oy + 4, "вхід", size=12, color=MUTED, anchor="end"))
        out.append(text(ox + 70, oy - 70, "ВИХІД НА C", size=14, bold=True, color=NEG))
        out.append(text(ox + 70, oy - 52, "→ інтегратор", size=13, bold=True, color=NEG))
        return out

    def differentiator(ox, oy):
        out = []
        # вхід -> C -> вузол -> R -> земля; вихід на R
        out.append(line(ox, oy, ox + 24, oy, color=LINE, sw=1.6))
        # C горизонтальний
        out.append(line(ox + 24, oy - 12, ox + 24, oy + 12, color=LINE, sw=2.4))
        out.append(line(ox + 32, oy - 12, ox + 32, oy + 12, color=LINE, sw=2.4))
        out.append(text(ox + 28, oy - 20, "C", size=14, bold=True))
        nx = ox + 32 + 34
        out.append(line(ox + 32, oy, nx, oy, color=LINE, sw=1.6))
        out.append(circle(nx, oy, 2.6, fill=INK, stroke=INK))
        # R вниз до землі
        out.append(line(nx, oy, nx, oy + 22, color=LINE, sw=1.6))
        out.append(rect(nx - 7, oy + 22, 14, 40, fill=BG, stroke=LINE, sw=1.6, rx=2))
        out.append(text(nx + 18, oy + 44, "R", size=14, bold=True, anchor="start"))
        out.append(line(nx, oy + 62, nx, oy + 78, color=LINE, sw=1.6))
        for i, ww in enumerate((18, 11, 5)):
            out.append(line(nx - ww, oy + 78 + i * 5, nx + ww, oy + 78 + i * 5, color=LINE, sw=1.6))
        out.append(line(nx, oy, nx + 60, oy, color=LINE, sw=1.6))
        out.append(circle(nx + 60, oy, 3, fill=BG, stroke=LINE, sw=1.6))
        out.append(text(nx + 70, oy + 4, "вихід", size=12, color=MUTED, anchor="start"))
        out.append(text(ox - 6, oy + 4, "вхід", size=12, color=MUTED, anchor="end"))
        out.append(text(ox + 70, oy - 70, "ВИХІД НА R", size=14, bold=True, color=POS))
        out.append(text(ox + 70, oy - 52, "→ диференціатор", size=13, bold=True, color=POS))
        return out

    p += integrator(70, 150)
    p += differentiator(430, 150)
    # роздільна вертикаль
    p.append(line(360, 70, 360, 250, color=MUTED, sw=1, dash="4 4"))

    b, _, _ = textbox(W / 2, 320,
                      "Ті самі два елементи, R і C. Знімаємо напругу з C — повільний бік, що накопичує: інтеграл.\n"
                      "Знімаємо з R — швидкий бік, що відгукується лише на зміну: похідна.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'two-circuits.svg'), W, H, *p,
           title="Один RC, два виходи: на C — інтегратор, на R — диференціатор")


def integrator_wave():
    """Прямокутник на вході; на C — повільна зарядка/розрядка ≈ трикутник (нахил)."""
    W, H = 720, 360
    p = []
    ox, oy = 80, 70
    plot_w, plot_h = 560, 110
    # вісь часу
    midy_in = oy + plot_h / 2
    p.append(line(ox, midy_in, ox + plot_w, midy_in, color=MUTED, sw=1))
    p.append(text(ox - 10, oy + 6, "вхід", size=12, bold=True, anchor="end", color=NEG))

    # прямокутна хвиля (2 періоди)
    T = plot_w / 2.0
    hi = midy_in - 40
    lo = midy_in + 40
    pts = []
    seq = [(0, hi), (T / 2, hi), (T / 2, lo), (T, lo),
           (T, hi), (T * 1.5, hi), (T * 1.5, lo), (2 * T, lo)]
    d = "M%.1f %.1f" % (ox + seq[0][0], seq[0][1])
    for x, y in seq[1:]:
        d += " L%.1f %.1f" % (ox + x, y)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, NEG))

    # вихід: трикутна хвиля (заряд лінійно, бо τ ≫ T → ділянка експоненти майже пряма)
    oy2 = oy + plot_h + 50
    midy_out = oy2 + plot_h / 2
    p.append(line(ox, midy_out, ox + plot_w, midy_out, color=MUTED, sw=1))
    p.append(text(ox - 10, oy2 + 6, "вихід", size=12, bold=True, anchor="end", color=FIELD))
    amp = 26
    tr = [(0, midy_out + amp)]
    # піднімається коли вхід високий, спадає коли низький
    tr += [(T / 2, midy_out - amp), (T, midy_out + amp),
           (T * 1.5, midy_out - amp), (2 * T, midy_out + amp)]
    d2 = "M%.1f %.1f" % (ox + tr[0][0], tr[0][1])
    for x, y in tr[1:]:
        d2 += " L%.1f %.1f" % (ox + x, y)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d2, FIELD))
    p.append(text(ox + plot_w + 6, midy_out + 4, "≈ трикутник", size=12, color=FIELD, anchor="start"))
    p.append(text(ox + T / 4, midy_out - amp - 8, "інтеграл сталої = нахил", size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 322,
                      "Поки вхід тримає стале значення, конденсатор заряджається майже рівно — пряма лінія.\n"
                      "Прямокутник інтегрується в трикутник. Працює, ЛИШЕ коли τ = RC ≫ період входу.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'integrator-wave.svg'), W, H, *p,
           title="Інтегратор: прямокутник на вході → трикутник на C (τ ≫ T)")


def differentiator_wave():
    """Фронти прямокутника → короткі сплески на R, що швидко спадають."""
    W, H = 720, 360
    p = []
    ox, oy = 80, 70
    plot_w, plot_h = 560, 110
    midy_in = oy + plot_h / 2
    p.append(line(ox, midy_in, ox + plot_w, midy_in, color=MUTED, sw=1))
    p.append(text(ox - 10, oy + 6, "вхід", size=12, bold=True, anchor="end", color=NEG))

    T = plot_w / 2.0
    hi = midy_in - 40
    lo = midy_in + 40
    seq = [(0, lo), (T / 2, lo), (T / 2, hi), (T, hi),
           (T, lo), (T * 1.5, lo), (T * 1.5, hi), (2 * T, hi)]
    d = "M%.1f %.1f" % (ox + seq[0][0], seq[0][1])
    for x, y in seq[1:]:
        d += " L%.1f %.1f" % (ox + x, y)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, NEG))

    # вихід: сплеск угору на висхідному фронті, вниз — на спадному; між фронтами ≈ 0
    oy2 = oy + plot_h + 50
    midy_out = oy2 + plot_h / 2
    p.append(line(ox, midy_out, ox + plot_w, midy_out, color=MUTED, sw=1))
    p.append(text(ox - 10, oy2 + 6, "вихід", size=12, bold=True, anchor="end", color=POS))

    def spike(x0, up=True, A=42, tau=18):
        """Експоненційний сплеск від x0; up=True → угору."""
        pts = []
        sign = -1 if up else 1
        for k in range(0, 60):
            xx = x0 + k * 1.0
            if xx > ox + plot_w:
                break
            yy = midy_out + sign * A * math.exp(-(k) / tau)
            pts.append((xx, yy))
        if not pts:
            return ""
        d = "M%.1f %.1f" % (pts[0][0], midy_out)
        d += " L%.1f %.1f" % (pts[0][0], pts[0][1])
        for xx, yy in pts[1:]:
            d += " L%.1f %.1f" % (xx, yy)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, POS)

    # фронти входу: вгору при T/2 і 1.5T; вниз при T
    p.append(spike(ox + T / 2, up=True))
    p.append(spike(ox + T, up=False))
    p.append(spike(ox + T * 1.5, up=True))
    p.append(text(ox + T / 2 + 6, midy_out - 50, "+сплеск", size=11, color=POS, anchor="start"))
    p.append(text(ox + T + 6, midy_out + 56, "−сплеск", size=11, color=POS, anchor="start"))
    p.append(text(ox + T * 0.78, midy_out - 12, "між фронтами ≈ 0", size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 322,
                      "Стрибок входу дає різкий сплеск на R, що відразу спадає; стале значення дає нуль —\n"
                      "це й є похідна. Працює, ЛИШЕ коли τ = RC ≪ період входу (інакше виходить просто копія).",
                      size=12, fill="#fdecea", stroke=POS)
    p.append(b)
    render(os.path.join(OUT, 'differentiator-wave.svg'), W, H, *p,
           title="Диференціатор: фронти на вході → сплески на R (τ ≪ T)")


def freq_domain():
    """Дві АЧХ у log-log: інтегратор (спад −6 дБ/окт) і диференціатор (підйом +6 дБ/окт);
    позначено смугу, де нахил справді відповідає інтегруванню / диференціюванню."""
    W, H = 720, 400
    p = []
    ox, oy = 90, 320
    aw, ah = 540, 250
    # осі
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))           # частота →
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.8))           # підсилення ↑
    p.append(text(ox + aw / 2, oy + 34, "частота (log)", size=13, bold=True))
    p.append(text(ox - 60, oy - ah / 2, "|вихід|", size=13, bold=True))
    p.append(text(ox - 60, oy - ah / 2 + 18, "(log)", size=13, bold=True))

    fc = ox + aw * 0.45                                              # злам f = 1/(2πRC)
    p.append(line(fc, oy, fc, oy - ah, color=MUTED, sw=1, dash="4 4"))
    p.append(text(fc, oy - ah - 6, "f꜀ = 1/(2πRC)", size=12, bold=True, color=MUTED))

    # ── інтегратор: плато до fc, далі спад ──
    yflat = oy - ah * 0.78
    p.append(line(ox, yflat, fc, yflat, color=NEG, sw=2.6))
    p.append(line(fc, yflat, ox + aw, yflat + ah * 0.62, color=NEG, sw=2.6))
    p.append(text(ox + 10, yflat - 8, "інтегратор (вихід на C)", size=12, bold=True, color=NEG, anchor="start"))
    p.append(text(fc + 90, yflat + ah * 0.36, "−6 дБ/окт", size=12, bold=True, color=NEG))

    # зона дійсного інтегрування — праворуч від fc
    p.append(rect(fc, oy - ah, ox + aw - fc, ah, fill="rgba(0,0,0,0)", stroke="none"))
    p.append(text((fc + ox + aw) / 2, oy - 12, "тут вихід ≈ ∫ входу", size=12, bold=True, color=NEG))

    # ── диференціатор: підйом до fc, далі плато ──
    ylow = oy - ah * 0.16
    p.append(line(ox, ylow, fc, ylow - ah * 0.55, color=POS, sw=2.6))
    p.append(line(fc, ylow - ah * 0.55, ox + aw, ylow - ah * 0.55, color=POS, sw=2.6))
    p.append(text(ox + 10, ylow + 16, "диференціатор (вихід на R)", size=12, bold=True, color=POS, anchor="start"))
    p.append(text(ox + 60, ylow - ah * 0.30, "+6 дБ/окт", size=12, bold=True, color=POS))
    p.append(text((ox + fc) / 2, oy - 12, "тут вихід ≈ d/dt входу", size=12, bold=True, color=POS))

    b, _, _ = textbox(W / 2, 372,
                      "Інтегрування = нахил −6 дБ/окт (ділення на ω): працює ВИЩЕ зламу, де C коротить.\n"
                      "Диференціювання = +6 дБ/окт (множення на ω): працює НИЖЧЕ зламу, де C ще тримає.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'freq-domain.svg'), W, H, *p,
           title="Частотний бік: де нахил АЧХ справді = інтеграл або похідна")


def transfer_complex():
    """Комплексна площина: знаменник 1+jωτ як вектор; інтегратор бере його обернений,
    диференціатор домножує на jωτ. Показано модуль і кут для одного ωτ."""
    W, H = 720, 420
    p = []
    cx, cy = 250, 250          # початок координат
    sc = 95.0                  # масштаб одиниці
    r = 1.4                    # приклад ωτ
    # осі
    p.append(line(cx - 60, cy, cx + 320, cy, color=INK, sw=1.6))
    p.append(line(cx, cy + 70, cx, cy - 230, color=INK, sw=1.6))
    p.append(text(cx + 322, cy + 18, "Re", size=12, bold=True, anchor="end"))
    p.append(text(cx - 10, cy - 228, "Im", size=12, bold=True, anchor="start"))
    # одиничні позначки
    p.append(line(cx + sc, cy - 4, cx + sc, cy + 4, color=MUTED, sw=1))
    p.append(text(cx + sc, cy + 18, "1", size=11, color=MUTED))

    # вектор знаменника 1 + jωτ (Re=1, Im=ωτ); екран: вгору = +Im
    dx, dy = cx + sc, cy - r * sc
    p.append(line(cx, cy, dx, dy, color=INK, sw=2.6))
    p.append(circle(dx, dy, 3, fill=INK, stroke=INK))
    p.append(text(dx + 8, dy - 6, "1 + jωτ", size=13, bold=True, anchor="start"))
    # проєкції
    p.append(line(dx, dy, dx, cy, color=MUTED, sw=1, dash="3 3"))
    p.append(line(cx, dy, dx, dy, color=MUTED, sw=1, dash="3 3"))
    p.append(text(cx + sc / 2, cy + 18, "Re = 1", size=11, color=MUTED))
    p.append(text(cx - 8, (cy + dy) / 2, "Im = ωτ", size=11, color=MUTED, anchor="end"))
    # кут φ = arctan(ωτ)
    p.append(text(cx + 30, cy - 14, "φ", size=13, bold=True, color=MUTED))

    # довжина = √(1+(ωτ)²)
    L = math.hypot(1, r)
    p.append(text((cx + dx) / 2 - 6, (cy + dy) / 2 - 10,
                  "|1+jωτ| = √(1+(ωτ)²)", size=11, color=INK, anchor="end"))

    # підписи: як кожна машина користується цим вектором
    bx = 470
    bi, _, _ = textbox(bx + 95, 150,
                       "ІНТЕГРАТОР  H = 1/(1+jωτ)\n"
                       "модуль = 1 / довжина\n"
                       "кут = −φ  (поворот назад)\n"
                       "велике ωτ → |H|→0, спад",
                       size=12, fill="#eaf0fd", stroke=NEG, color=INK)
    p.append(bi)
    bd, _, _ = textbox(bx + 95, 300,
                       "ДИФЕРЕНЦІАТОР  H = jωτ/(1+jωτ)\n"
                       "домножити ще на jωτ:\n"
                       "+довжина ωτ, +90° поворот\n"
                       "мале ωτ → |H|≈ωτ, підйом",
                       size=12, fill="#fdecea", stroke=POS, color=INK)
    p.append(bd)

    b, _, _ = textbox(W / 2, 392,
                      "Обидві передавальні функції — це дії над ОДНИМ вектором 1 + jωτ (сторони 1 і ωτ).\n"
                      "Інтегратор бере його обернений; диференціатор домножує на jωτ. Уся різниця — у фазі.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'transfer-complex.svg'), W, H, *p,
           title="Комплексний бік: один вектор 1 + jωτ задає обидві машини")


def error_curve():
    """Похибка наближення ε проти ωτ (log-x): інтегратор точний за великого ωτ,
    диференціатор — за малого; на зламі ωτ=1 обидва дають ε≈0.293."""
    W, H = 720, 420
    p = []
    ox, oy = 90, 320
    aw, ah = 540, 250
    # осі
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    p.append(text(ox + aw / 2, oy + 34, "ωτ  (log)", size=13, bold=True))
    p.append(text(ox - 56, oy - ah / 2, "похибка ε", size=13, bold=True))
    p.append(text(ox - 56, oy - ah / 2 + 18, "(частка)", size=12, color=MUTED))

    # log-вісь від ωτ=0.1 до 10 ; x(r) = ox + (log10(r)+1)/2 * aw
    def X(r):
        return ox + (math.log10(r) + 1.0) / 2.0 * aw
    # y: ε від 0 (внизу, oy) до 1 (вгорі)
    def Y(e):
        return oy - e * ah

    # сітка по ωτ
    for rr, lab in [(0.1, "0.1"), (1.0, "1"), (10.0, "10")]:
        gx = X(rr)
        p.append(line(gx, oy, gx, oy - ah, color=MUTED, sw=1, dash="3 3"))
        p.append(text(gx, oy + 16, lab, size=11, color=MUTED))
    # горизонталі ε
    for ee, lab in [(0.293, "0.293"), (0.5, "0.5"), (1.0, "1")]:
        gy = Y(ee)
        p.append(line(ox, gy, ox + 6, gy, color=MUTED, sw=1))
        p.append(text(ox - 8, gy + 4, lab, size=10, color=MUTED, anchor="end"))

    # точна похибка інтегратора: ε = 1 - r/√(1+r²)  (мала за великого r)
    di = []
    rr = 0.1
    while rr <= 10.001:
        e = 1 - rr / math.sqrt(1 + rr * rr)
        di.append((X(rr), Y(e)))
        rr *= 1.06
    d = "M%.1f %.1f" % di[0]
    for x, y in di[1:]:
        d += " L%.1f %.1f" % (x, y)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, NEG))
    p.append(text(X(6.5), Y(0.02) - 8, "інтегратор", size=12, bold=True, color=NEG, anchor="middle"))
    p.append(text(X(6.5), Y(0.02) + 8, "ε≈1/(2(ωτ)²)", size=11, color=NEG, anchor="middle"))

    # точна похибка диференціатора: ε = 1 - 1/√(1+r²)  (мала за малого r)
    dd = []
    rr = 0.1
    while rr <= 10.001:
        e = 1 - 1 / math.sqrt(1 + rr * rr)
        dd.append((X(rr), Y(e)))
        rr *= 1.06
    d2 = "M%.1f %.1f" % dd[0]
    for x, y in dd[1:]:
        d2 += " L%.1f %.1f" % (x, y)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d2, POS))
    p.append(text(X(0.16), Y(0.02) - 8, "диференціатор", size=12, bold=True, color=POS, anchor="middle"))
    p.append(text(X(0.16), Y(0.02) + 8, "ε≈(ωτ)²/2", size=11, color=POS, anchor="middle"))

    # точка зламу: обидві ε = 0.293
    p.append(circle(X(1), Y(0.293), 4, fill=BG, stroke=INK, sw=2))
    p.append(text(X(1) + 8, Y(0.293) - 8, "ωτ=1: ε≈0.29", size=11, bold=True, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, 392,
                      "Інтегратор точний ПРАВОРУЧ (велике ωτ, далеко над зламом); диференціатор — ЛІВОРУЧ\n"
                      "(мале ωτ, далеко під зламом). На самому зламі ωτ=1 кожен має ~29% похибки.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'error-curve.svg'), W, H, *p,
           title="Залишкова похибка наближення проти ωτ")


if __name__ == '__main__':
    two_circuits()
    integrator_wave()
    differentiator_wave()
    freq_domain()
    transfer_complex()
    error_curve()
    print("OK: 6 figures ->", OUT)
