# -*- coding: utf-8 -*-
"""Фігури до статті «Пряма цифрова синтеза (DDS)» (book/electronics/analog/dds-synthesis).
Чотири фігури:
  block.svg    — конвеєр DDS: акумулятор фази → ПЗП фаза→амплітуда → ЦАП → фільтр
  wheel.svg    — колесо фази: код настройки = крок по колу; більший крок = швидше = вища частота
  staircase.svg— сходинки ЦАП згладжуються фільтром у синусоїду; праворуч — образ на fclk−fout
  truncation.svg— зрізання фази: адресує ПЗП лише старша частина розрядів → періодична похибка → спури
  sawtooth-spectrum.svg — вставка math: пилка похибки e(n) з періодом T → лінійний спектр спурів довкола несучої
  sfdr-vs-bits.svg      — вставка math: найгірший спур vs P; точний tan-вираз ≈ пряма −6.02·P−3.92 (6 дБ/розряд)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

ACCENT = "#7a3fb0"   # фазовий шлях
CLK    = "#d68910"   # тактовий сигнал


def block(cx, cy, w, h, title, sub=None, fill=FILL, stroke=INK):
    """Прямокутний блок конвеєра з підписом (і дрібним підзаголовком під ним)."""
    out = [rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8)]
    if sub:
        out.append(text(cx, cy - 3, title, size=13, color=INK, bold=True))
        out.append(text(cx, cy + 15, sub, size=10.5, color=MUTED))
    else:
        out.append(text(cx, cy + 5, title, size=13, color=INK, bold=True))
    return "".join(out)


# ── 1. Конвеєр DDS ──────────────────────────────────────────────────────────
def fig_block():
    W, H = 950, 340
    f = []
    yb = 150
    bw, bh = 168, 78
    xs = [130, 330, 530, 730]
    labels = [
        ("Акумулятор фази", "додає M щотакту, N розрядів"),
        ("ПЗП фаза→амплітуда", "таблиця синуса"),
        ("ЦАП", "число → напруга"),
        ("Фільтр-згладжувач", "прибирає образи"),
    ]
    fills = ["#efe6f6", "#e8f0fb", "#fdf2e0", "#eaf7ee"]
    for x, (t, s), fl in zip(xs, labels, fills):
        f.append(block(x, yb, bw, bh, t, s, fill=fl))
    # стрілки між блоками
    for i in range(3):
        f.append(arrow(xs[i] + bw / 2, yb, xs[i + 1] - bw / 2, yb, color=INK, sw=2))
    # підписи сигналів на стрілках
    f.append(text((xs[0] + xs[1]) / 2, yb - 12, "фаза", size=10.5, color=ACCENT, bold=True))
    f.append(text((xs[1] + xs[2]) / 2, yb - 12, "число-відлік", size=10.5, color=MUTED))
    f.append(text((xs[2] + xs[3]) / 2, yb - 12, "сходинки", size=10.5, color=MUTED))
    # вхід: код настройки M
    f.append(arrow(xs[0], 66, xs[0], yb - bh / 2, color=ACCENT, sw=2.2))
    bb, _, _ = textbox(xs[0], 48, "код настройки M\n(бажана частота)", size=11, color=ACCENT,
                       bold=True, fill="#efe6f6", stroke=ACCENT)
    f.append(bb)
    # такт fclk знизу — спільний для перших трьох цифрових блоків
    ytk = yb + bh / 2 + 40
    f.append(line(xs[0], ytk, xs[2], ytk, color=CLK, sw=2, dash="2 4"))
    for x in xs[:3]:
        f.append(line(x, yb + bh / 2, x, ytk, color=CLK, sw=1.6, dash="2 4"))
        f.append(circle(x, ytk, 2.6, fill=CLK, stroke=CLK, sw=1))
    f.append(text((xs[0] + xs[2]) / 2, ytk + 20, "такт fclk — б'є одночасно по всій цифровій частині",
                  size=11, color=CLK, bold=True))
    # вихід: чиста синусоїда
    ox = xs[3] + bw / 2 + 8
    f.append(arrow(ox, yb, ox + 46, yb, color=INK, sw=2))
    px = []
    for k in range(41):
        xx = ox + 54 + k * 1.0
        yy = yb - 20 * math.sin(k / 40 * 2 * math.pi)
        px.append("%.1f,%.1f" % (xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' %
             (" ".join(px), POS))
    f.append(text(ox + 68, yb + 40, "чистий", size=11, color=POS, bold=True))
    f.append(text(ox + 68, yb + 56, "синус", size=11, color=POS, bold=True))
    render(os.path.join(IMG, "block.svg"), W, H, *f,
           title="DDS: від числа-настройки до синусоїди — чотири ланки")
    return W, H


# ── 2. Колесо фази ──────────────────────────────────────────────────────────
def fig_wheel():
    W, H = 780, 380
    f = []
    R = 118
    centers = [(210, 205), (570, 205)]
    steps = [8, 20]                      # кроків на оберт: маленький / великий
    caps = ["малий крок M → повільний оберт → низька частота",
            "великий крок M → швидкий оберт → висока частота"]
    for (cx, cy), n, cap in zip(centers, steps, caps):
        f.append(circle(cx, cy, R, fill="#ffffff", stroke=INK, sw=2))
        # позначки поділок по колу (це «місткість» акумулятора 2^N)
        for k in range(36):
            a = k / 36 * 2 * math.pi - math.pi / 2
            r1, r2 = R - 6, R
            f.append(line(cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                          cx + r2 * math.cos(a), cy + r2 * math.sin(a), color=MUTED, sw=1))
        # відлічувані точки — рівні кроки M навколо кола
        pts = []
        for k in range(n):
            a = k / n * 2 * math.pi - math.pi / 2
            pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
        for (px, py) in pts:
            f.append(circle(px, py, 3.4, fill=ACCENT, stroke=ACCENT, sw=1))
        # дуга-стрибок від першої до другої точки — і є «крок M»
        a0 = -math.pi / 2
        a1 = 1 / n * 2 * math.pi - math.pi / 2
        f.append(arrow(cx + (R + 22) * math.cos(a0), cy + (R + 22) * math.sin(a0),
                       cx + (R + 22) * math.cos(a1), cy + (R + 22) * math.sin(a1),
                       color=ACCENT, sw=2.4))
        f.append(line(cx, cy, cx + R * math.cos(a0), cy + R * math.sin(a0), color=INK, sw=1.4))
        f.append(line(cx, cy, cx + R * math.cos(a1), cy + R * math.sin(a1), color=ACCENT, sw=2))
        f.append(text(cx, cy - R - 30, "крок = M", size=12, color=ACCENT, bold=True))
        f.append(text(cx, cy + R + 34, cap, size=11, color=INK))
        f.append(text(cx, cy + R + 54, "поділок на колі — рівно 2ᴺ", size=10, color=MUTED))
    render(os.path.join(IMG, "wheel.svg"), W, H, *f,
           title="Акумулятор фази — це стрілка, що стрибає по колу кроком M")
    return W, H


# ── 3. Сходинки ЦАП → фільтр → синус, і образ ───────────────────────────────
def fig_staircase():
    W, H = 820, 400
    f = []
    # ліва панель: ступінчастий вихід ЦАП і згладжений синус поверх
    ax, ay, aw, ah = 70, 70, 320, 210
    f.append(rect(ax, ay, aw, ah, fill="#fbfbfc", stroke=MUTED, sw=1.2))
    mid = ay + ah / 2
    f.append(line(ax, mid, ax + aw, mid, color="#cbd0d6", sw=1))
    N = 16
    A = ah * 0.40
    # східчаста (утримання-нуль-порядку) форма
    stair = []
    for k in range(N):
        x0 = ax + k * aw / N
        x1 = ax + (k + 1) * aw / N
        yv = mid - A * math.sin((k + 0.5) / N * 2 * math.pi)
        stair.append("%.1f,%.1f" % (x0, yv))
        stair.append("%.1f,%.1f" % (x1, yv))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' %
             (" ".join(stair), NEG))
    # згладжений синус
    sm = []
    for k in range(161):
        xx = ax + k / 160 * aw
        yy = mid - A * math.sin(k / 160 * 2 * math.pi)
        sm.append("%.1f,%.1f" % (xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' %
             (" ".join(sm), POS))
    f.append(text(ax + aw / 2, ay - 12, "вихід ЦАП: сходинки → згладжений синус", size=12, color=INK, bold=True))
    f.append(text(ax + 6, ay + ah + 18, "сходинки (ЦАП)", size=10.5, color=NEG, anchor="start", bold=True))
    f.append(text(ax + aw - 6, ay + ah + 18, "після фільтра", size=10.5, color=POS, anchor="end", bold=True))

    # права панель: спектр — основна лінія fout і образ fclk−fout
    bx, by, bw, bh = 470, 70, 300, 210
    base = by + bh
    f.append(line(bx, base, bx + bw, base, color=INK, sw=1.5))       # вісь частоти
    f.append(arrow(bx, base, bx + bw + 8, base, color=INK, sw=1.5))
    # позначки: fout (низько), fclk/2, fclk−fout (високо), fclk
    def bar(xfrac, hfrac, color, lab, labcol=None, dash=None):
        x = bx + xfrac * bw
        f.append(line(x, base, x, base - hfrac * (bh - 20), color=color, sw=3 if not dash else 1.6,
                      dash=dash))
        f.append(text(x, base + 16, lab, size=10.5, color=labcol or color, bold=True))
    bar(0.16, 1.0, POS, "fout")
    bar(0.50, 0.0, MUTED, "fclk/2", labcol=MUTED, dash="3 4")
    f.append(line(bx + 0.50 * bw, base, bx + 0.50 * bw, by + 6, color=MUTED, sw=1, dash="3 4"))
    bar(0.84, 0.62, POS, "fclk−fout", labcol=NEG)
    bar(1.00, 0.0, INK, "fclk", labcol=INK)
    f.append(line(bx + 1.00 * bw, base, bx + 1.00 * bw, by + 6, color=INK, sw=1, dash="2 4"))
    # крива фільтра — гладко спадає до fclk/2
    fl = []
    for k in range(121):
        xf = k / 120
        xx = bx + xf * bw
        # плато до ~0.4, тоді спад
        g = 1.0 if xf < 0.40 else max(0.0, 1.0 - (xf - 0.40) / 0.22)
        yy = base - g * (bh - 20) * 0.92 - 4
        fl.append("%.1f,%.1f" % (xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="6 4"/>' %
             (" ".join(fl), CLK))
    f.append(text(bx + 0.20 * bw, by + 20, "смуга фільтра", size=10.5, color=CLK, bold=True, anchor="start"))
    f.append(text(bx + bw / 2, ay - 12, "спектр: корисне низько, образ під fclk", size=12, color=INK, bold=True))

    # підсумковий рядок
    bb, w0, h0 = textbox(W / 2, 340,
                         "Образ на fclk − fout лежить дзеркально до fout. Фільтр устигає його прибрати,\n"
                         "лише поки fout не піднялося занадто високо — тому робоча межа ≈ 0.4·fclk.",
                         size=11.5, color=INK, fill="#eaf7ee", stroke=FIELD)
    f.append(bb)
    render(os.path.join(IMG, "staircase.svg"), W, H, *f)
    return W, H


# ── 4. Зрізання фази → спури ────────────────────────────────────────────────
def fig_truncation():
    W, H = 800, 360
    f = []
    # розрядна лінійка акумулятора: старші P адресують ПЗП, молодші зрізаються
    x0, y0 = 90, 90
    cellw, cellh = 34, 46
    Ntot, P = 16, 6
    for i in range(Ntot):
        x = x0 + i * cellw
        used = i < P
        fill = "#e8f0fb" if used else "#f2f3f5"
        stroke = NEG if used else MUTED
        f.append(rect(x, y0, cellw, cellh, fill=fill, stroke=stroke, sw=1.6, rx=3))
    f.append(text(x0 + P * cellw / 2, y0 - 14, "старші P розрядів → адреса ПЗП", size=11.5,
                  color=NEG, bold=True))
    f.append(text(x0 + P * cellw + (Ntot - P) * cellw / 2, y0 - 14, "молодші розряди — зрізано",
                  size=11.5, color=MUTED, bold=True))
    f.append(text(x0, y0 + cellh + 20, "старший біт", size=9.5, color=MUTED, anchor="start"))
    f.append(text(x0 + Ntot * cellw, y0 + cellh + 20, "молодший біт", size=9.5, color=MUTED, anchor="end"))
    # дужка над зрізаною частиною
    xs2 = x0 + P * cellw
    xe2 = x0 + Ntot * cellw
    f.append(line(xs2, y0 + cellh + 6, xe2, y0 + cellh + 6, color=MUTED, sw=1.4))

    # нижче: пилчаста похибка фази (те, що викидаємо) — періодична, тому спектрально гостра
    ex, ey, ew, eh = 90, 210, 620, 90
    f.append(rect(ex, ey, ew, eh, fill="#fbfbfc", stroke=MUTED, sw=1.1))
    midy = ey + eh / 2
    f.append(line(ex, midy, ex + ew, midy, color="#cbd0d6", sw=1))
    saw = []
    period = ew / 6.0
    for k in range(int(ew) + 1):
        phase = (k % period) / period
        yy = midy + (eh / 2 - 8) * (phase - 0.5) * 2 * 0.85
        saw.append("%.1f,%.1f" % (ex + k, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' %
             (" ".join(saw), POS))
    f.append(text(ex + ew / 2, ey - 8, "викинута частина фази повторюється рівним «зубом» —",
                  size=11, color=INK, bold=True))
    f.append(text(ex + ew / 2, ey + eh + 18,
                  "рівна періодичність → у спектрі не рівний шум, а гострі паразитні лінії (спури)",
                  size=11, color=POS, bold=True))
    render(os.path.join(IMG, "truncation.svg"), W, H, *f,
           title="Зрізання фази: заощадили таблицю — заплатили спурами")
    return W, H


# ── 5. (math) Пилка похибки → лінійний спектр спурів ─────────────────────────
def fig_sawtooth_spectrum():
    """Вставка math-phase-truncation: періодична пилка e(n) з періодом T тактів,
    її гармоніки сідають рівними лініями обабіч несучої з кроком fclk/T."""
    W, H = 820, 430
    f = []
    # ── верхня панель: пилка похибки e(n) у часі ──
    ax, ay, aw, ah = 70, 66, 680, 130
    f.append(rect(ax, ay, aw, ah, fill="#fbfbfc", stroke=MUTED, sw=1.1))
    base = ay + ah - 16
    top = ay + 14
    f.append(line(ax, base, ax + aw, base, color="#cbd0d6", sw=1))
    # три повні зуби пилки — період T
    Tpx = aw / 3.4
    saw = []
    k = 0
    while k <= aw:
        ph = (k % Tpx) / Tpx
        yy = base - (base - top) * ph
        saw.append("%.1f,%.1f" % (ax + k, yy))
        # вертикальний скид на межі періоду
        if (k + 1) % Tpx < k % Tpx:
            saw.append("%.1f,%.1f" % (ax + k, base))
        k += 1
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' %
             (" ".join(saw), POS))
    # позначка періоду T між першим і другим зубом
    x1, x2 = ax, ax + Tpx
    f.append(line(x1, top - 6, x2, top - 6, color=INK, sw=1.2))
    f.append(line(x1, top - 10, x1, top - 2, color=INK, sw=1.2))
    f.append(line(x2, top - 10, x2, top - 2, color=INK, sw=1.2))
    f.append(text((x1 + x2) / 2, top - 12, "період T = 2ᴸ / GCD(M, 2ᴸ) тактів", size=11,
                  color=INK, bold=True))
    f.append(text(ax + 4, base + 13, "e(n) = (n·M) mod 2ᴸ — молодші L розрядів акумулятора",
                  size=10.5, color=MUTED, anchor="start"))
    f.append(text(ax - 6, top + 2, "2⁻ᴾ", size=10, color=POS, anchor="end", bold=True))
    f.append(text(ax + aw / 2, ay - 12, "похибка зрізання: рівна пилка, що повторюється",
                  size=12.5, color=INK, bold=True))

    # ── нижня панель: спектр — несуча + дзеркальні спури кроком fклк/T ──
    bx, by, bw, bh = 70, 250, 680, 130
    sb = by + bh - 16
    f.append(line(bx, sb, bx + bw, sb, color=INK, sw=1.5))
    f.append(arrow(bx, sb, bx + bw + 8, sb, color=INK, sw=1.5))
    f.append(text(bx + bw + 6, sb + 16, "частота", size=10, color=INK, anchor="end"))
    # несуча посередині
    xc = bx + bw * 0.5
    f.append(line(xc, sb, xc, by + 6, color=POS, sw=3))
    f.append(text(xc, sb + 16, "fout (несуча)", size=11, color=POS, bold=True))
    # спури обабіч рівним кроком, спадають за амплітудою
    dx = bw * 0.11
    heights = [0.52, 0.34, 0.24, 0.17]
    for i, hf in enumerate(heights, start=1):
        for sgn in (-1, +1):
            x = xc + sgn * i * dx
            if x <= bx + 4 or x >= bx + bw - 4:
                continue
            f.append(line(x, sb, x, sb - hf * (bh - 26), color=NEG, sw=2.4))
        # підпис кроку лише над першою парою
    # дужка кроку між несучою й першим спуром
    xs1 = xc + dx
    f.append(line(xc, by + 20, xs1, by + 20, color=INK, sw=1.1))
    f.append(line(xc, by + 16, xc, by + 24, color=INK, sw=1.1))
    f.append(line(xs1, by + 16, xs1, by + 24, color=INK, sw=1.1))
    f.append(text((xc + xs1) / 2, by + 14, "крок = fclk·GCD/2ᴸ", size=10.5, color=INK, bold=True))
    f.append(text(bx + bw * 0.14, sb - 0.40 * (bh - 26), "спури", size=10.5, color=NEG,
                  bold=True, anchor="middle"))
    f.append(text(bx + bw / 2, by - 12, "спектр: несуча й симетричні спури рівним кроком",
                  size=12.5, color=INK, bold=True))
    render(os.path.join(IMG, "sawtooth-spectrum.svg"), W, H, *f,
           title="Періодична пилка похибки → гострі спури довкола несучої")
    return W, H


# ── 6. (math) Найгірший спур vs розряди адреси таблиці ───────────────────────
def fig_sfdr_vs_bits():
    """Вставка math-phase-truncation: SFDR найгіршого спура зрізання vs P.
    Точний вираз 20·log10(tan(π/2^(P+1))) майже збігається з прямою −6.02·P−3.92."""
    W, H = 720, 440
    f = []
    px, py, pw, ph = 90, 70, 560, 300
    # осі
    f.append(line(px, py, px, py + ph, color=INK, sw=1.5))          # вісь Y (dBc)
    f.append(line(px, py + ph, px + pw, py + ph, color=INK, sw=1.5))  # вісь X (P)
    Pmin, Pmax = 8, 18
    ymin, ymax = -120.0, -40.0     # dBc
    def X(P): return px + (P - Pmin) / (Pmax - Pmin) * pw
    def Y(db): return py + ph - (db - ymin) / (ymax - ymin) * ph
    # сітка X: розряди
    for P in range(Pmin, Pmax + 1, 2):
        x = X(P)
        f.append(line(x, py + ph, x, py + ph + 5, color=INK, sw=1.2))
        f.append(text(x, py + ph + 20, str(P), size=11, color=INK))
    f.append(text(px + pw / 2, py + ph + 40, "P — розрядів адреси таблиці ПЗП", size=12,
                  color=INK, bold=True))
    # сітка Y: dBc
    for db in range(-120, -39, 20):
        y = Y(db)
        f.append(line(px - 5, y, px, y, color=INK, sw=1.2))
        f.append(text(px - 10, y + 4, "%d" % db, size=10.5, color=INK, anchor="end"))
        f.append(line(px, y, px + pw, y, color="#e5e8ec", sw=1))
    f.append(text(px - 44, py - 22, "рівень найгіршого", size=10.5, color=MUTED, anchor="start"))
    f.append(text(px - 44, py - 8, "спура, dBc", size=10.5, color=MUTED, anchor="start"))
    # пряма −6.02·P − 3.92
    ln = []
    for P in range(Pmin, Pmax + 1):
        ln.append("%.1f,%.1f" % (X(P), Y(-6.02 * P - 3.92)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' %
             (" ".join(ln), NEG))
    # точний tan-вираз — кружечки
    for P in range(Pmin, Pmax + 1):
        db = 20.0 * math.log10(math.tan(math.pi / (2 ** (P + 1))))
        f.append(circle(X(P), Y(db), 3.6, fill="#ffffff", stroke=POS, sw=1.8))
    # легенда
    lx, ly = px + pw - 250, py + 14
    f.append(line(lx, ly, lx + 26, ly, color=NEG, sw=2.4))
    f.append(text(lx + 32, ly + 4, "−6.02·P − 3.92 (оцінка)", size=10.5, color=NEG,
                  anchor="start", bold=True))
    f.append(circle(lx + 13, ly + 20, 3.6, fill="#ffffff", stroke=POS, sw=1.8))
    f.append(text(lx + 32, ly + 24, "20·log₁₀·tan(π/2^(P+1)) (точно)", size=10.5, color=POS,
                  anchor="start", bold=True))
    # робочі точки 12/14/16 — підписи рівнів
    for P, lab in ((12, "−72"), (14, "−84"), (16, "−96")):
        db = -6.02 * P - 3.92
        x, y = X(P), Y(db)
        f.append(circle(x, y, 5.4, fill="none", stroke=INK, sw=1.4))
        f.append(text(x + 8, y - 8, "P=%d ≈ %s dBc" % (P, lab), size=10, color=INK,
                      anchor="start", bold=True))
    # підпис нахилу
    bb, _, _ = textbox(px + 150, Y(-52), "нахил ≈ 6 дБ на кожен\nдоданий розряд адреси",
                       size=11, color=INK, fill="#eaf7ee", stroke=FIELD)
    f.append(bb)
    render(os.path.join(IMG, "sfdr-vs-bits.svg"), W, H, *f,
           title="Найгірший спур зрізання: 6 дБ на кожен розряд адреси таблиці")
    return W, H


if __name__ == "__main__":
    for fn in (fig_block, fig_wheel, fig_staircase, fig_truncation,
               fig_sawtooth_spectrum, fig_sfdr_vs_bits):
        w, h = fn()
        print("wrote", fn.__name__, w, h)
