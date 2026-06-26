# -*- coding: utf-8 -*-
"""Фігури до теми «Розрахунок підтяжки» (guide/embedded/peryferiia).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def nmos(x, y, w=40, h=44, color=INK):
    """Спрощений n-канальний ключ нижнього плеча: прямокутник з підписом."""
    out = rect(x, y, w, h, fill="#e9edf2", stroke=color, sw=2, rx=4)
    out += text(x + w / 2, y + h / 2 + 5, "N", size=14, bold=True, color=color)
    return out


# ── 1. Навіщо підтяжка: відкритий стік уміє лише тягнути вниз ─────────────────
def fig_why_pullup():
    W, H = 760, 380
    f = [text(W / 2, 26, "Відкритий стік уміє лише тягнути вниз — «вгору» тягне резистор",
              size=16, bold=True)]

    def panel(x0, title, has_pullup, ok):
        col = FIELD if ok else POS
        f.append(rect(x0, 52, 348, 300, fill=BG, stroke=col, sw=2, rx=12))
        f.append(text(x0 + 174, 76, title, size=13.5, bold=True, color=INK))
        vcc_y, gnd_y = 104, 300
        vx = x0 + 56          # ліва вертикаль (живлення/земля)
        busx = x0 + 196       # вертикальна гілка лінії
        nodey = 196           # вузол лінії
        # рейка живлення
        f.append(plus(vx, vcc_y, 11))
        f.append(text(vx, vcc_y - 22, "VDD", size=11, bold=True, color=INK))
        # земля
        f.append(line(vx, gnd_y - 8, vx + 14, gnd_y - 8, color=LINE, sw=2.4))
        f.append(line(vx + 1, gnd_y - 4, vx + 11, gnd_y - 4, color=LINE, sw=2))
        f.append(line(vx + 3, gnd_y, vx + 9, gnd_y, color=LINE, sw=1.6))
        f.append(text(vx + 6, gnd_y + 18, "GND", size=10.5, color=MUTED))
        # підтяжка від VDD до вузла (або її відсутність)
        if has_pullup:
            f.append(line(vx, vcc_y, busx, vcc_y, color=LINE, sw=2))
            f.append(line(busx, vcc_y + 11, busx, nodey - 58, color=LINE, sw=2))
            f.append(rect(busx - 13, nodey - 58, 26, 40, fill=FILL, stroke=LINE, sw=1.8, rx=3))
            f.append(text(busx, nodey - 34, "Rp", size=12, bold=True, color=FIELD))
            f.append(line(busx, nodey - 18, busx, nodey, color=LINE, sw=2))
            f.append(arrow(busx + 8, nodey - 12, busx + 8, nodey + 2, color=FIELD, sw=2.2))
        else:
            f.append(text(busx, nodey - 42, "немає Rp", size=12, bold=True, color=POS))
            f.append(text(busx, nodey - 24, "(ніщо не тягне вгору)", size=10, color=POS))
        # вузол лінії (SDA/SCL)
        f.append(circle(busx, nodey, 3.4, fill=INK, stroke=INK))
        f.append(text(busx + 52, nodey - 6, "лінія", size=11, color=INK))
        f.append(text(busx + 52, nodey + 9, "SDA/SCL", size=10, color=MUTED))
        # відкритий стік: ключ від вузла до землі
        f.append(line(busx, nodey, busx, nodey + 28, color=LINE, sw=2))
        f.append(nmos(busx - 20, nodey + 28, color=(INK if ok else col)))
        f.append(text(busx + 50, nodey + 50, "вихід чіпа", size=10, color=MUTED))
        f.append(line(busx, nodey + 72, busx, gnd_y, color=LINE, sw=2))
        f.append(line(vx + 6, gnd_y - 8, busx, gnd_y - 8, color=LINE, sw=2))
        f.append(line(busx, gnd_y - 8, busx, gnd_y, color=LINE, sw=2))
        # стан лінії (підпис унизу)
        if has_pullup:
            f.append(text(x0 + 174, 332, "ключ відпущений → Rp підтягує до VDD (лог. 1)",
                          size=11, color=INK))
        else:
            f.append(text(busx + 50, nodey + 30, "?", size=22, bold=True, color=POS))
            f.append(text(x0 + 174, 332, "ключ відпущений → лінія «висить», рівень невідомий",
                          size=11, color=POS, bold=True))

    panel(18, "З підтяжкою", True, True)
    panel(394, "Без підтяжки", False, False)
    render(os.path.join(IMG, "why-pullup.svg"), W, H, *f)


# ── 2. Перетягування каната: вікно між двома обмеженнями ─────────────────────
def fig_window():
    W, H = 760, 360
    f = [text(W / 2, 26, "Опір підтяжки: вікно між «надто сильним» і «надто слабким»",
              size=16, bold=True)]

    ox = 70
    bar_y = 150
    bar_w = 620
    # вісь опору (логарифмічна за відчуттям, але рівномірна для наочності)
    f.append(line(ox, bar_y, ox + bar_w, bar_y, color=INK, sw=2))
    f.append(arrow(ox + bar_w, bar_y, ox + bar_w + 14, bar_y, color=INK, sw=2))
    f.append(text(ox + bar_w + 6, bar_y + 26, "більший Rp →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 4, bar_y + 26, "← менший Rp", size=11, color=MUTED, anchor="start"))
    # три зони
    lo = ox + 0.30 * bar_w          # межа Rp(min)
    hi = ox + 0.66 * bar_w          # межа Rp(max)
    f.append(rect(ox, bar_y - 26, lo - ox, 52, fill="#fbeee6", stroke=POS, sw=1.6, rx=6))
    f.append(rect(lo, bar_y - 26, hi - lo, 52, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=6))
    f.append(rect(hi, bar_y - 26, ox + bar_w - hi, 52, fill="#fbeee6", stroke=POS, sw=1.6, rx=6))
    f.append(text((ox + lo) / 2, bar_y + 5, "надто сильна", size=12.5, bold=True, color=POS))
    f.append(text((lo + hi) / 2, bar_y + 5, "робоче вікно", size=13, bold=True, color=FIELD))
    f.append(text((hi + ox + bar_w) / 2, bar_y + 5, "надто слабка", size=12.5, bold=True, color=POS))
    # межі з підписами
    f.append(line(lo, bar_y - 40, lo, bar_y + 40, color=INK, sw=1.4, dash="4 3"))
    f.append(line(hi, bar_y - 40, hi, bar_y + 40, color=INK, sw=1.4, dash="4 3"))
    b1, w1, _ = textbox(lo, bar_y - 64, "Rp(min)", size=12, fill=BG, stroke=INK, bold=True)
    f.append(b1)
    b2, w2, _ = textbox(hi, bar_y - 64, "Rp(max)", size=12, fill=BG, stroke=INK, bold=True)
    f.append(b2)
    # пояснення під кожною зоною
    f.append(mtext((ox + lo) / 2, bar_y + 78,
                   "ключу важко\nстягнути лінію в 0:\nбагато струму,\n«нуль» не дотискається",
                   size=10.5, color=POS, lh=1.25))
    f.append(mtext((lo + hi) / 2, bar_y + 78,
                   "і «нуль» чіткий,\nі фронт устигає\nдо порогу —\nобидві умови разом",
                   size=10.5, color=INK, lh=1.25))
    f.append(mtext((hi + ox + bar_w) / 2, bar_y + 78,
                   "фронт «вгору»\nрозтягується RC,\nне встигає за тактом:\nбіти змазуються",
                   size=10.5, color=POS, lh=1.25))
    render(os.path.join(IMG, "window.svg"), W, H, *f)


# ── 3. Фронт «вгору» — це зарядка RC; Rp і Cb розтягують його ────────────────
def fig_rise_time():
    W, H = 740, 410
    f = [text(W / 2, 26, "Фронт «вгору» — це зарядка ємності лінії крізь Rp (крива RC)",
              size=15.5, bold=True)]

    ox, oy = 86, 322
    ax_w, ax_h = 540, 250
    # осі
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(arrow(ox + ax_w, oy, ox + ax_w + 12, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 44, "час", size=12, color=INK))
    f.append(text(ox - 50, oy - ax_h + 6, "напруга", size=12, color=INK))
    f.append(text(ox - 50, oy - ax_h + 22, "на лінії", size=10.5, color=MUTED))

    Vдд = 1.0
    Tmax = 5.0   # у одиницях сталої τ = Rp·Cb
    def px(t, v):
        return ox + t / Tmax * ax_w, oy - v / 1.05 * ax_h

    # рівні VDD, 70%, 30%, 0
    for v, lab, c in [(1.0, "VDD", INK), (0.7, "0.7·VDD", MUTED), (0.3, "0.3·VDD", MUTED)]:
        x, y = px(0, v)
        f.append(line(ox, y, ox + ax_w, y, color="#cfd4da", sw=1, dash="5 4"))
        f.append(text(ox - 8, y + 4, lab, size=10.5, color=c, anchor="end"))

    # дві криві зарядки: швидка (малий Rp·Cb) і повільна (великий Rp·Cb)
    def charge(tau, color, sw=2.8, dash=None):
        pts = []
        t = 0.0
        while t <= Tmax + 0.001:
            v = Vдд * (1 - math.exp(-t / tau))
            pts.append(px(t, v))
            t += 0.05
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        s = " ".join("%.1f,%.1f" % p for p in pts)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                 % (s, color, sw, d))

    charge(0.55, FIELD)     # швидкий фронт — малий Rp або мала Cb
    charge(1.7, POS)        # повільний фронт — великий Rp або велика Cb

    # позначити час від 30% до 70% для кожної кривої
    def mark_tr(tau, color, yoff):
        t30 = -tau * math.log(1 - 0.3)
        t70 = -tau * math.log(1 - 0.7)
        x30, y30 = px(t30, 0.3)
        x70, y70 = px(t70, 0.7)
        ylev = oy + yoff
        f.append(line(x30, y30, x30, ylev, color=color, sw=1, dash="3 3"))
        f.append(line(x70, y70, x70, ylev, color=color, sw=1, dash="3 3"))
        f.append(line(x30, ylev, x70, ylev, color=color, sw=2.2))
        f.append(text((x30 + x70) / 2, ylev - 6, "t_r", size=11, color=color, bold=True))

    mark_tr(0.55, FIELD, -2)
    mark_tr(1.7, POS, 22)

    # підписи кривих
    xa, ya = px(Tmax, 1 - math.exp(-Tmax / 0.55))
    f.append(text(xa - 6, ya - 8, "малий Rp·Cb → фронт устигає", size=11.5, color=FIELD,
                  anchor="end", bold=True))
    xb, yb = px(Tmax, 1 - math.exp(-Tmax / 1.7))
    f.append(text(xb - 6, yb + 16, "великий Rp·Cb → фронт лінивий", size=11.5, color=POS,
                  anchor="end", bold=True))

    b, _, _ = textbox(ox + 210, oy - ax_h + 30,
                      "t_r вимірюють від 30% до 70% VDD\nt_r ≈ 0.85 · Rp · Cb",
                      size=11, fill="#eef2f8", stroke=INK)
    f.append(b)
    render(os.path.join(IMG, "rise-time.svg"), W, H, *f)


# ── 4. Той самий такт: сильна vs слабка підтяжка на осцилограмі ──────────────
def fig_strong_weak():
    W, H = 760, 360
    f = [text(W / 2, 26, "Та сама лінія, той самий такт: сильна підтяжка встигає, слабка — ні",
              size=15.5, bold=True)]

    ox, oy = 70, 250
    ax_w, ax_h = 620, 150
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.6))
    f.append(text(ox + ax_w / 2, oy + 78, "час →", size=11, color=MUTED))
    f.append(text(ox - 48, oy - ax_h + 6, "рівень", size=11, color=INK))
    f.append(text(ox - 48, oy - ax_h + 22, "лінії", size=10, color=MUTED))

    hi = oy - ax_h + 20      # рівень VDD
    lo = oy - 6              # рівень 0
    thr = oy - ax_h * 0.62   # поріг сприйняття «1»
    # поріг
    f.append(line(ox, thr, ox + ax_w, thr, color=MUTED, sw=1, dash="5 4"))
    f.append(text(ox + ax_w - 4, thr - 6, "поріг «1»", size=10.5, color=MUTED, anchor="end"))
    f.append(text(ox - 8, hi + 4, "VDD", size=10, color=INK, anchor="end"))
    f.append(text(ox - 8, lo + 4, "0", size=10, color=INK, anchor="end"))

    # три такти: ключ відпускає лінію (вгору) і знову тягне вниз
    # точки відпускання
    period = ax_w / 3.0
    SAMP = 0.46            # момент вибірки як частка періоду від фронту
    samples = []
    def edge_up_curve(x0, tau_frac, color, sw, dash=None):
        """крива зарядки від lo до hi, що стартує в x0; tau_frac — частка періоду."""
        tau = period * tau_frac
        pts = []
        x = x0
        while x <= x0 + period * 0.92:
            t = x - x0
            v = 1 - math.exp(-t / tau)
            y = lo + (hi - lo) * v
            pts.append((x, y))
            x += 3
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        s = " ".join("%.1f,%.1f" % p for p in pts)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                 % (s, color, sw, d))
        return tau

    # вертикальні «спади» (ключ стягує вниз) — спільні для обох
    for k in range(3):
        x0 = ox + k * period
        f.append(line(x0, hi, x0, lo, color=INK, sw=1.4))      # різкий спад (активне підтягання вниз)
        # момент вибірки приймачем — однаковий для обох підтяжок
        sx = x0 + period * SAMP
        samples.append(sx)

    # сильна підтяжка: крутий фронт (мала τ) — до вибірки вже біля VDD
    for k in range(3):
        edge_up_curve(ox + k * period, 0.10, FIELD, 2.8)
    # слабка підтяжка: лінивий фронт (велика τ) — до вибірки ще нижче порога — пунктир
    for k in range(3):
        edge_up_curve(ox + k * period, 0.62, POS, 2.6, dash="6 4")

    # моменти вибірки + вердикт: на кожному фронті ставимо точку на обох кривих
    def y_at(x0, tau_frac):
        tau = period * tau_frac
        v = 1 - math.exp(-(period * SAMP) / tau)
        return lo + (hi - lo) * v
    for k, sx in enumerate(samples):
        x0 = ox + k * period
        f.append(line(sx, oy - ax_h, sx, oy, color="#cfd4da", sw=1, dash="2 4"))
        ys = y_at(x0, 0.10)      # сильна — вище порога
        yw = y_at(x0, 0.62)      # слабка — нижче порога
        f.append(circle(sx, ys, 3.4, fill=FIELD, stroke=BG, sw=1.4))
        f.append(circle(sx, yw, 3.4, fill=POS, stroke=BG, sw=1.4))
    f.append(text(ox + 1.5 * period, oy - ax_h - 6,
                  "↑ моменти вибірки приймачем (однакові для обох)", size=10.5, color=MUTED))

    # легенда
    f.append(line(ox + 30, oy + 40, ox + 70, oy + 40, color=FIELD, sw=2.8))
    f.append(text(ox + 78, oy + 44, "сильна Rp: до вибірки лінія вже вище порога → «1»",
                  size=11, color=FIELD, anchor="start", bold=True))
    f.append(line(ox + 30, oy + 60, ox + 70, oy + 60, color=POS, sw=2.6, dash="6 4"))
    f.append(text(ox + 78, oy + 64, "слабка Rp: до вибірки не дотягла → приймач читає «0»",
                  size=11, color=POS, anchor="start", bold=True))
    render(os.path.join(IMG, "strong-weak.svg"), W, H, *f)


# ── 5. (вставка math) t_r між 30% і 70% = 0.847·τ на кривій зарядки ──────────
def fig_tr_levels():
    W, H = 740, 420
    f = [text(W / 2, 26, "Час фронту = проміжок, поки крива йде від 30% до 70% VDD",
              size=15.5, bold=True)]

    ox, oy = 92, 330
    ax_w, ax_h = 540, 258
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(arrow(ox + ax_w, oy, ox + ax_w + 12, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 50, "час (у сталих часу τ)", size=12, color=INK))
    f.append(text(ox - 56, oy - ax_h + 6, "напруга", size=12, color=INK))
    f.append(text(ox - 56, oy - ax_h + 22, "на лінії", size=10.5, color=MUTED))

    Tmax = 4.0   # у одиницях τ
    top = 1.06
    def px(t, v):
        return ox + t / Tmax * ax_w, oy - v / top * ax_h

    # горизонтальні рівні
    for v, lab, c in [(1.0, "VDD", INK), (0.7, "0.7·VDD", FIELD), (0.3, "0.3·VDD", FIELD)]:
        x, y = px(0, v)
        f.append(line(ox, y, ox + ax_w, y, color="#cfd4da", sw=1, dash="5 4"))
        f.append(text(ox - 8, y + 4, lab, size=10.5, color=c, anchor="end"))

    # крива зарядки v = 1 - e^-t (τ=1)
    pts = []
    t = 0.0
    while t <= Tmax + 0.001:
        pts.append(px(t, 1 - math.exp(-t)))
        t += 0.04
    s = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (s, INK))

    # моменти 30% і 70%
    t30 = -math.log(1 - 0.3)   # 0.357
    t70 = -math.log(1 - 0.7)   # 1.204
    x30, y30 = px(t30, 0.3)
    x70, y70 = px(t70, 0.7)
    for (xx, yy, lab) in [(x30, y30, "0.357·τ"), (x70, y70, "1.204·τ")]:
        f.append(line(xx, yy, xx, oy, color=FIELD, sw=1.3, dash="3 3"))
        f.append(circle(xx, yy, 4, fill=FIELD, stroke=BG, sw=1.4))
        f.append(text(xx, oy + 18, lab, size=10.5, color=FIELD, bold=True))

    # відрізок t_r на осі часу
    yb = oy - 0  # на осі
    f.append(line(x30, oy - 1, x70, oy - 1, color=POS, sw=3.2))
    f.append(arrow(x70, oy - 1, x70 + 0.1, oy - 1, color=POS, sw=3.2))
    f.append(text((x30 + x70) / 2, oy - 10, "t_r", size=13, color=POS, bold=True))

    b, _, _ = textbox(ox + ax_w - 150, oy - ax_h + 36,
                      "t_r = (1.204 − 0.357)·τ\n   = 0.847 · τ\n   = ln(7/3) · Rp·Cb",
                      size=11, fill="#eef2f8", stroke=INK)
    f.append(b)
    render(os.path.join(IMG, "tr-levels.svg"), W, H, *f)


# ── 6. (вставка math) різні пороги вирізають різний час фронту ───────────────
def fig_thresholds():
    W, H = 740, 430
    f = [text(W / 2, 26, "Інші пороги — інший коефіцієнт: ширший проміжок = довший фронт",
              size=15, bold=True)]

    ox, oy = 92, 338
    ax_w, ax_h = 540, 262
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(arrow(ox + ax_w, oy, ox + ax_w + 12, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 52, "час (у сталих часу τ)", size=12, color=INK))
    f.append(text(ox - 56, oy - ax_h + 6, "частка", size=12, color=INK))
    f.append(text(ox - 56, oy - ax_h + 22, "від VDD", size=10.5, color=MUTED))

    Tmax = 3.2
    top = 1.06
    def px(t, v):
        return ox + t / Tmax * ax_w, oy - v / top * ax_h

    for v, lab in [(1.0, "VDD"), (0.5, "0.5·VDD")]:
        x, y = px(0, v)
        f.append(line(ox, y, ox + ax_w, y, color="#e2e6ea", sw=1, dash="5 4"))
        f.append(text(ox - 8, y + 4, lab, size=10, color=MUTED, anchor="end"))

    # крива зарядки
    pts = []
    t = 0.0
    while t <= Tmax + 0.001:
        pts.append(px(t, 1 - math.exp(-t)))
        t += 0.03
    s = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (s, INK))

    def span(k1, k2, color, ylev, lab):
        t1 = -math.log(1 - k1)
        t2 = -math.log(1 - k2)
        x1, y1 = px(t1, k1)
        x2, y2 = px(t2, k2)
        # рівні
        for (kk, c) in [(k1, color), (k2, color)]:
            yy = px(0, kk)[1]
            f.append(line(ox, yy, ox + ax_w, yy, color=color, sw=0.9, dash="2 4"))
        f.append(circle(x1, y1, 3.6, fill=color, stroke=BG, sw=1.3))
        f.append(circle(x2, y2, 3.6, fill=color, stroke=BG, sw=1.3))
        f.append(line(x1, ylev, x2, ylev, color=color, sw=3))
        f.append(line(x1, y1, x1, ylev, color=color, sw=0.9, dash="3 3"))
        f.append(line(x2, y2, x2, ylev, color=color, sw=0.9, dash="3 3"))
        f.append(text((x1 + x2) / 2, ylev - 7, lab, size=11, color=color, bold=True))

    # 30-70: вузький (зелений), позначка ближче до осі
    span(0.30, 0.70, FIELD, oy - 6, "30→70%: 0.847·τ")
    # 10-90: широкий (червоний), позначка нижче
    span(0.10, 0.90, POS, oy + 26, "10→90%: 2.197·τ")

    b, _, _ = textbox(ox + ax_w - 138, oy - ax_h + 40,
                      "коеф. = ln((1−k₁)/(1−k₂))\n30/70 → ln(7/3)=0.847\n10/90 → ln(9)=2.197",
                      size=10.5, fill="#eef2f8", stroke=INK)
    f.append(b)
    render(os.path.join(IMG, "thresholds.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_pullup()
    fig_window()
    fig_rise_time()
    fig_strong_weak()
    fig_tr_levels()
    fig_thresholds()
    print("OK: 6 figures ->", IMG)
