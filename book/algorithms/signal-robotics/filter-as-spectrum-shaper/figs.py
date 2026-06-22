# -*- coding: utf-8 -*-
"""Фігури до теми «Фільтр як формувач спектра».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
PASS_C = FIELD       # смуга пропускання — зелене
STOP_C = POS         # смуга затримання — гаряче
RESP_C = NEG         # сама характеристика — холодна лінія
SHADE  = "#eef4ff"   # легка заливка під кривою


def _polyline(pts, color, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (s, color, sw, d))


def _axes(f, ox, oy, aw, ah, xlab="частота", ylab="підсилення"):
    f.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.5))
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.5))
    f.append(text(ox + aw, oy + 19, xlab, size=11, color=MUTED, italic=True, anchor="end"))
    f.append(text(ox - 8, oy - ah - 2, ylab, size=11, color=MUTED, italic=True, anchor="end"))


# ── 1. Формувач спектра: вхід × характеристика = вихід ───────────────────────
def fig_shaper():
    W, H = 760, 300
    f = [text(W / 2, 26, "Фільтр множить спектр сигналу на свою характеристику",
              size=15, bold=True)]

    base = 210
    top = 70

    def bars(x0, heights, color):
        out = []
        n = len(heights)
        bw = 150
        for i, hfrac in enumerate(heights):
            bx = x0 + 8 + (bw - 16) * i / (n - 1)
            bh = (base - top) * hfrac
            out.append(line(bx, base, bx, base - bh, color=color, sw=6))
        return out

    def panel(x0, label, color):
        _axes(f, x0, base, 170, base - top, xlab="f", ylab="")
        f.append(text(x0 + 85, base + 38, label, size=12, color=color, bold=True))

    # вхід — спадні стовпчики (широкий спектр)
    panel(30, "спектр входу", NEG)
    f += bars(30, [0.85, 0.92, 0.6, 0.5, 0.4], NEG)

    f.append(text(232, 145, "×", size=24, color=INK, bold=True))

    # характеристика — ФНЧ-крива
    panel(264, "характеристика", RESP_C)
    pts = []
    for i in range(81):
        t = i / 80.0
        g = 1.0 / (1.0 + (t / 0.42) ** 4) ** 0.5      # м'який ФНЧ
        pts.append((264 + 8 + (170 - 16) * t, base - (base - top) * g))
    f.append(_polyline(pts, RESP_C, 2.6))

    f.append(text(466, 145, "=", size=24, color=INK, bold=True))

    # вихід — низькі пройшли, високі прибиті
    panel(498, "спектр виходу", PASS_C)
    f += bars(498, [0.84, 0.88, 0.42, 0.18, 0.06], PASS_C)

    f.append(text(W / 2, 286,
                  "уся дія фільтра — поточкове множення спектра на цю криву",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "shaper.svg"), W, H, *f)


# ── 2. Анатомія характеристики: смуги пропускання / переходу / затримання ────
def fig_response_anatomy():
    W, H = 720, 360
    f = [text(W / 2, 26, "Паспорт фільтра низьких частот", size=15, bold=True)]

    ox, oy, aw, ah = 70, 280, 580, 210
    _axes(f, ox, oy, aw, ah)

    # сітка рівнів 1.0 та 0.707
    one_y = oy - ah * 0.9
    half_y = oy - ah * 0.9 * 0.707
    f.append(line(ox, one_y, ox + aw, one_y, color="#dddddd", sw=1.1, dash="4 4"))
    f.append(text(ox - 8, one_y + 4, "1.0", size=10, color=MUTED, anchor="end"))
    f.append(line(ox, half_y, ox + aw, half_y, color="#dddddd", sw=1.1, dash="4 4"))
    f.append(text(ox - 8, half_y + 4, "0.707", size=10, color=MUTED, anchor="end"))

    # крива ФНЧ
    def g(t):
        return 1.0 / (1.0 + (t / 0.5) ** 6) ** 0.5
    pts = []
    for i in range(241):
        t = i / 240.0
        pts.append((ox + aw * t, oy - ah * 0.9 * g(t)))
    f.append(_polyline(pts, RESP_C, 2.8))

    # частота зрізу: де крива перетинає 0.707
    fc_t = 0.5
    fc_x = ox + aw * fc_t
    f.append(line(fc_x, oy, fc_x, half_y, color=INK, sw=1.3, dash="3 3"))
    f.append(circle(fc_x, half_y, 4, fill=BG, stroke=INK, sw=1.6))
    f.append(text(fc_x, oy + 19, "fc", size=11, color=INK, bold=True, italic=True))
    f.append(text(fc_x + 6, half_y - 8, "−3 дБ", size=10, color=MUTED, anchor="start"))

    # зони
    pass_x = ox + aw * 0.18
    trans_x = ox + aw * 0.5
    stop_x = ox + aw * 0.82
    f.append(rect(ox, top_zone := oy - ah, aw * 0.40, ah, fill="#eafaf0", stroke="none", sw=0, rx=0))
    f.append(rect(ox + aw * 0.40, top_zone, aw * 0.20, ah, fill="#fff7e6", stroke="none", sw=0, rx=0))
    f.append(rect(ox + aw * 0.60, top_zone, aw * 0.40, ah, fill="#fdecea", stroke="none", sw=0, rx=0))
    # повторно крива поверх заливок
    f.append(_polyline(pts, RESP_C, 2.8))
    f.append(line(fc_x, oy, fc_x, half_y, color=INK, sw=1.3, dash="3 3"))

    f.append(text(pass_x, oy - ah + 22, "смуга", size=12, color=PASS_C, bold=True))
    f.append(text(pass_x, oy - ah + 40, "пропускання", size=12, color=PASS_C, bold=True))
    f.append(text(pass_x, oy - ah + 56, "passband ≈ 1", size=9.5, color=MUTED, italic=True))
    f.append(text(trans_x, oy - ah + 22, "смуга", size=11, color="#b9770e", bold=True))
    f.append(text(trans_x, oy - ah + 39, "переходу", size=11, color="#b9770e", bold=True))
    f.append(text(stop_x, oy - ah + 22, "смуга", size=12, color=STOP_C, bold=True))
    f.append(text(stop_x, oy - ah + 40, "затримання", size=12, color=STOP_C, bold=True))
    f.append(text(stop_x, oy - ah + 56, "stopband ≈ 0", size=9.5, color=MUTED, italic=True))

    f.append(text(W / 2, oy + 40,
                  "зріз fc — там, де підсилення падає до 0.707 (половина потужності)",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "response-anatomy.svg"), W, H, *f)


# ── 3. Характеристика ковзного середнього: ФНЧ із нулями ─────────────────────
def fig_movavg_response():
    W, H = 720, 320
    f = [text(W / 2, 26, "Ковзне середнє очима частот: ФНЧ із нулями", size=15, bold=True)]

    ox, oy, aw, ah = 70, 250, 580, 190
    _axes(f, ox, oy, aw, ah)

    # |sin(N x /2) / (N sin(x/2))| — характеристика ковзного середнього, N=8
    N = 8
    pts = []
    for i in range(601):
        t = i / 600.0                     # 0..1 = 0..Найквіст (тут до 4 нулів)
        x = t * 4 * math.pi / N * N       # розгорнемо так, щоб було ~4 нулі у вікні
        x = t * math.pi * 4               # частота
        if abs(math.sin(x / 2)) < 1e-6:
            val = 1.0
        else:
            val = abs(math.sin(N * x / 2) / (N * math.sin(x / 2)))
        pts.append((ox + aw * t, oy - ah * 0.92 * val))
    f.append(_polyline(pts, RESP_C, 2.4))

    # позначити нулі
    for k in range(1, 4):
        zt = k / 4.0
        zx = ox + aw * zt
        f.append(circle(zx, oy, 3.5, fill=POS, stroke=POS, sw=1))
        if k == 1:
            f.append(text(zx, oy + 19, "нуль", size=10, color=POS, italic=True))

    f.append(text(ox + 6, oy - ah * 0.92 + 4, "1.0", size=10, color=MUTED, anchor="start"))
    f.append(text(ox + aw * 0.62, oy - ah * 0.30,
                  "«горбики» між нулями", size=10.5, color=MUTED, italic=True, anchor="start"))

    f.append(text(W / 2, oy + 44,
                  "нулі сідають на частоти, що вкладаються у вікно цілим числом періодів",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "movavg-response.svg"), W, H, *f)


# ── 4. Характеристика EMA: гладкий ФНЧ, кероване α ────────────────────────────
def fig_ema_response():
    W, H = 720, 320
    f = [text(W / 2, 26, "EMA очима частот: гладкий ФНЧ, зріз керує α", size=15, bold=True)]

    ox, oy, aw, ah = 70, 250, 580, 190
    _axes(f, ox, oy, aw, ah)

    # |H(w)| EMA = a / sqrt(1 - 2(1-a)cos w + (1-a)^2)
    def ema_mag(a, t):
        w = t * math.pi
        b = 1 - a
        den = math.sqrt(1 - 2 * b * math.cos(w) + b * b)
        return a / den

    curves = [(0.1, "#1c6fb0", "мала α — зріз низько"),
              (0.3, NEG, "середня α"),
              (0.6, "#7aa9e0", "велика α — зріз високо")]
    for a, col, _ in curves:
        pts = []
        for i in range(401):
            t = i / 400.0
            pts.append((ox + aw * t, oy - ah * 0.92 * ema_mag(a, t)))
        f.append(_polyline(pts, col, 2.4))

    # легенда
    ly = oy - ah + 6
    for a, col, lab in curves:
        f.append(line(ox + aw - 196, ly, ox + aw - 168, ly, color=col, sw=2.6))
        f.append(text(ox + aw - 162, ly + 4, "α=%.1f · %s" % (a, lab.split('—')[-1].strip() if '—' in lab else lab),
                      size=9.5, color=col, anchor="start"))
        ly += 17

    f.append(text(ox + 6, oy - ah * 0.92 + 4, "1.0", size=10, color=MUTED, anchor="start"))
    f.append(text(W / 2, oy + 44,
                  "без нулів і горбиків — гладкий спад; менша α звужує смугу пропускання",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "ema-response.svg"), W, H, *f)


# ── 5. Ідеал проти реальності: «цегляна стіна» vs поступовий спад ─────────────
def fig_ideal_real():
    W, H = 720, 320
    f = [text(W / 2, 26, "Мрія й дійсність: ідеальний зріз недосяжний", size=15, bold=True)]

    ox, oy, aw, ah = 70, 250, 580, 190
    _axes(f, ox, oy, aw, ah)

    one = ah * 0.9
    fc_t = 0.5
    fc_x = ox + aw * fc_t

    # ідеал — «цегляна стіна»
    brick = [(ox, oy - one), (fc_x, oy - one), (fc_x, oy), (ox + aw, oy)]
    f.append(_polyline(brick, MUTED, 2.0, dash="7 4"))
    f.append(text(fc_x - 8, oy - one - 8, "ідеал: цегляна стіна", size=10.5,
                  color=MUTED, italic=True, anchor="end"))

    # реальність — поступовий спад із пульсаціями в смузі пропускання
    def real(t):
        ripple = 1.0 + 0.04 * math.sin(t * 22) * (t < 0.42)
        roll = 1.0 / (1.0 + (t / 0.5) ** 5) ** 0.5
        floor = 0.02
        return max(floor, roll * ripple)
    pts = []
    for i in range(401):
        t = i / 400.0
        pts.append((ox + aw * t, oy - one * real(t)))
    f.append(_polyline(pts, RESP_C, 2.8))

    f.append(line(fc_x, oy, fc_x, oy - one, color="#cccccc", sw=1.1, dash="3 3"))
    f.append(text(fc_x, oy + 19, "fc", size=11, color=INK, bold=True, italic=True))
    f.append(text(ox + aw * 0.66, oy - one * 0.5,
                  "реальність: поступово,", size=10.5, color=RESP_C, italic=True, anchor="start"))
    f.append(text(ox + aw * 0.66, oy - one * 0.5 + 15,
                  "зі смугою переходу", size=10.5, color=RESP_C, italic=True, anchor="start"))
    f.append(text(ox + aw * 0.16, oy - one - 6,
                  "пульсації", size=9.5, color="#b9770e", italic=True))

    f.append(text(W / 2, oy + 44,
                  "різкіший обрив коштує довшого фільтра й більшої затримки",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "ideal-real.svg"), W, H, *f)


# ── 6. Задум фільтра: форма → коефіцієнти → зважена сума в часі ───────────────
def fig_design_flow():
    W, H = 760, 250
    f = [text(W / 2, 26, "Як народжується фільтр", size=15, bold=True)]

    y = 130
    # (1) бажана форма
    x1 = 40
    f.append(rect(x1, y - 56, 200, 112, fill=FILL, stroke=RESP_C, sw=1.8))
    f.append(text(x1 + 100, y - 38, "1. бажана форма", size=12, color=RESP_C, bold=True))
    # мініатюра ФНЧ усередині
    mx, my, mw, mh = x1 + 24, y + 30, 152, 56
    f.append(line(mx, my, mx + mw, my, color="#cccccc", sw=1))
    mp = []
    for i in range(61):
        t = i / 60.0
        g = 1.0 / (1.0 + (t / 0.45) ** 6) ** 0.5
        mp.append((mx + mw * t, my - mh * g))
    f.append(_polyline(mp, RESP_C, 2.0))
    f.append(text(x1 + 100, y + 46, "що пропускати / гасити", size=9, color=MUTED, italic=True))

    # (2) коефіцієнти
    x2 = 290
    f.append(rect(x2, y - 56, 180, 112, fill=FILL, stroke="#b9770e", sw=1.8))
    f.append(text(x2 + 90, y - 38, "2. коефіцієнти", size=12, color="#b9770e", bold=True))
    f.append(text(x2 + 90, y - 6, "b₀ b₁ b₂ b₃ …", size=14, color=INK, bold=True))
    f.append(text(x2 + 90, y + 30, "процедура", size=10, color=MUTED, italic=True))
    f.append(text(x2 + 90, y + 45, "проєктування", size=10, color=MUTED, italic=True))

    # (3) зважена сума в часі
    x3 = 520
    f.append(rect(x3, y - 56, 200, 112, fill=FILL, stroke=PASS_C, sw=1.8))
    f.append(text(x3 + 100, y - 38, "3. зважена сума", size=12, color=PASS_C, bold=True))
    f.append(text(x3 + 100, y - 4, "y = Σ bₖ·xₖ", size=14, color=INK, bold=True))
    f.append(text(x3 + 100, y + 30, "кілька множень", size=10, color=MUTED, italic=True))
    f.append(text(x3 + 100, y + 45, "на відлік — миттєво", size=10, color=MUTED, italic=True))

    f.append(arrow(242, y, 288, y, color=INK, sw=2))
    f.append(arrow(472, y, 518, y, color=INK, sw=2))

    f.append(text(W / 2, H - 16,
                  "мислимо в частоті, рахуємо в часі — частотний задум стає копійчаною операцією",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "design-flow.svg"), W, H, *f)


if __name__ == "__main__":
    fig_shaper()
    fig_response_anatomy()
    fig_movavg_response()
    fig_ema_response()
    fig_ideal_real()
    fig_design_flow()
    print("OK: 6 figures ->", IMG)
