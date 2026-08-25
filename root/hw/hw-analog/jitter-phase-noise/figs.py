# -*- coding: utf-8 -*-
"""Фігури до теми «Джиттер і фазовий шум» (аналогова електроніка, кутом теорії кіл).
Чотири фігури:
  jitter-edges.svg    — ідеальний такт vs реальний: фронти «дихають» у часі (джиттер)
  two-faces.svg       — одне явище, два погляди: тремтіння в часі ⇄ спідниця в спектрі
  leeson-regions.svg  — спектр фазового шуму L(f): три ділянки (1/f³, 1/f², полиця)
  jitter-snr.svg      — джиттер ставить стелю SNR: −20·log(2π·f·tj), −20 дБ/декаду частоти
  leeson-corner.svg   — [вставка hist] резонатор як ФНЧ для фази: кут на f₀/2Q
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _wiggle(seed):
    """Детермінований псевдошум у [-1,1] — без залежностей."""
    x = math.sin(seed * 12.9898) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


def jitter_edges():
    """Ідеальний меандр і реальний: краї зсунуті туди-сюди від такту до такту."""
    W, H = 720, 360
    p = []
    x0, x1 = 80, 660
    period = (x1 - x0) / 6.0
    top, bot = 90, 150       # ідеальний рівень
    top2, bot2 = 210, 270    # реальний рівень

    # ── сітка ідеальних моментів (пунктир) ──
    for k in range(7):
        gx = x0 + k * period
        p.append(line(gx, 78, gx, 285, color=MUTED, sw=1, dash="3 4"))

    # ── ідеальний такт ──
    p.append(text(x0 - 14, (top + bot) / 2 + 5, "ідеал", size=12, color=MUTED, anchor="end"))
    d = "M%.1f %.1f" % (x0, bot)
    for k in range(6):
        ex = x0 + k * period
        hi = (k % 2 == 0)
        y = top if hi else bot
        d += " L%.1f %.1f" % (ex, y)
        d += " L%.1f %.1f" % (ex + period, y)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, NEG))

    # ── реальний такт: кожен край зсунутий на дрібний джиттер ──
    p.append(text(x0 - 14, (top2 + bot2) / 2 + 5, "реал", size=12, color=MUTED, anchor="end"))
    jit = period * 0.16
    d2 = "M%.1f %.1f" % (x0, bot2)
    prev = x0
    for k in range(6):
        ex = x0 + k * period + (_wiggle(k * 3.1 + 7) * jit if k > 0 else 0)
        hi = (k % 2 == 0)
        y = top2 if hi else bot2
        d2 += " L%.1f %.1f" % (ex, y)
        # позначка зсуву краю
        ideal_ex = x0 + k * period
        if k > 0:
            p.append(line(ideal_ex, top2 - 8, ex, top2 - 8, color=POS, sw=2.2))
        d2 += " L%.1f %.1f" % (ex + period, y)
        prev = ex
    # домалювати до кінця
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d2, POS))

    p.append(text((x0 + x1) / 2, 304, "червоні відрізки — зсув краю від ідеального моменту: це і є джиттер",
                  size=12, color=POS))

    b, _, _ = textbox(W / 2, 338,
                      "Ідеальний такт перемикається рівно по сітці. Реальний — щоразу трохи раніше\n"
                      "чи пізніше. Це тремтіння моментів у часі й називають джиттером.",
                      size=12, fill="#fdecea", stroke=POS)
    p.append(b)
    render(os.path.join(OUT, 'jitter-edges.svg'), W, H, *p,
           title="Джиттер: краї такту «дихають» навколо ідеальних моментів")


def two_faces():
    """Одне явище — два погляди: тремтіння в часі (зліва) ⇄ спідниця коло несучої (справа)."""
    W, H = 740, 360
    p = []
    # ── ліва панель: осцилограма — фронт «розмазаний» у часі ──
    lx, ly = 60, 80
    lw, lh = 280, 200
    p.append(rect(lx, ly, lw, lh, fill=BG, stroke=MUTED, sw=1))
    p.append(text(lx + lw / 2, ly - 8, "погляд у часі (осцилограф)", size=13, bold=True))
    midx = lx + lw / 2
    # «хмара» можливих моментів фронту
    for j in range(7):
        off = _wiggle(j * 2.3) * 26
        p.append(line(midx + off, ly + 24, midx + off, ly + lh - 40,
                      color=POS if j != 3 else NEG, sw=1.6 if j != 3 else 2.6,
                      dash=None if j == 3 else "2 3"))
    p.append(text(midx, ly + lh - 22, "момент фронту «гуляє»", size=11, color=POS))
    p.append(text(midx, ly + lh - 8, "Δt — джиттер (нс, пс)", size=11, bold=True, color=INK))

    # ── права панель: спектр — гострий пік + спідниця ──
    rx, ry = 410, 80
    rw, rh = 280, 200
    p.append(rect(rx, ry, rw, rh, fill=BG, stroke=MUTED, sw=1))
    p.append(text(rx + rw / 2, ry - 8, "погляд у спектрі (аналізатор)", size=13, bold=True))
    cx = rx + rw / 2
    base = ry + rh - 26
    # несуча — гострий пік
    p.append(line(cx, base, cx, ry + 20, color=NEG, sw=3))
    p.append(text(cx, ry + 14, "f₀", size=12, bold=True, color=NEG))
    # спідниця фазового шуму — спадні «горбики» обабіч
    pts = []
    for s in range(-58, 59):
        xx = cx + s * (rw / 2 - 16) / 58.0
        d = abs(s) / 58.0
        h = (rh - 60) * math.exp(-d * 4.2) * 0.9 if abs(s) > 2 else 0
        pts.append((xx, base - h))
    dpath = "M" + " L".join("%.1f %.1f" % q for q in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (dpath, POS))
    p.append(text(cx + 78, base - 30, "спідниця", size=11, color=POS))
    p.append(text(cx + 78, base - 16, "фазового шуму", size=11, color=POS))

    # ── міст між панелями ──
    p.append(arrow(lx + lw + 4, ly + lh / 2, rx - 4, ry + rh / 2, color=FIELD, sw=2.4))
    p.append(arrow(rx - 4, ry + rh / 2 + 16, lx + lw + 4, ly + lh / 2 + 16, color=FIELD, sw=2.4))
    p.append(text((lx + lw + rx) / 2, ly + lh / 2 - 10, "те саме", size=12, bold=True, color=FIELD))
    p.append(text((lx + lw + rx) / 2, ly + lh / 2 + 40, "явище", size=12, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, 338,
                      "Джиттер — тремтіння моментів у ЧАСІ; фазовий шум — те саме тремтіння,\n"
                      "побачене як розмиття піку в СПЕКТРІ. Одна суть, дві мови опису.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'two-faces.svg'), W, H, *p,
           title="Дві грані одного: джиттер у часі ⇄ фазовий шум у спектрі")


def leeson_regions():
    """Спектр L(f) у лог-лог осях: три нахили — 1/f³, 1/f², полиця."""
    W, H = 720, 420
    p = []
    ox, oy = 90, 330          # початок осей
    aw, ah = 560, 250
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))      # вісь X (offset, лог)
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))      # вісь Y (L(f), дБ)
    p.append(text(ox + aw / 2, oy + 44, "відступ від несучої f  (лог-шкала) →", size=12, bold=True))
    p.append(text(ox - 60, oy - ah / 2, "L(f)", size=13, bold=True))
    p.append(text(ox - 60, oy - ah / 2 + 17, "дБн/Гц", size=12, bold=True))

    # декади по X
    decades = ["1 Гц", "10", "100", "1к", "10к", "100к", "1М"]
    for i, lbl in enumerate(decades):
        gx = ox + aw * i / (len(decades) - 1)
        p.append(line(gx, oy, gx, oy - ah, color="#eef0f3", sw=1))
        p.append(text(gx, oy + 18, lbl, size=10, color=MUTED))

    # три ділянки: задаємо точки зламів і малюємо ламану
    # лівий край (близько несучої) — найвище; до полиці справа
    x_a = ox + aw * 0.0      # старт 1/f^3
    x_b = ox + aw * 0.33     # злам у 1/f^2
    x_c = ox + aw * 0.70     # вихід на полицю
    x_d = ox + aw
    y_a = oy - ah * 0.96
    y_b = oy - ah * 0.60
    y_c = oy - ah * 0.20
    y_d = oy - ah * 0.16
    seg = "M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f" % (x_a, y_a, x_b, y_b, x_c, y_c, x_d, y_d)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (seg, POS))

    # підписи нахилів
    p.append(text((x_a + x_b) / 2, (y_a + y_b) / 2 - 14, "−30 дБ/дек", size=11, bold=True, color=NEG))
    p.append(text((x_a + x_b) / 2, (y_a + y_b) / 2 + 2, "(1/f³, флікер)", size=10, color=MUTED))
    p.append(text((x_b + x_c) / 2, (y_b + y_c) / 2 - 14, "−20 дБ/дек", size=11, bold=True, color=NEG))
    p.append(text((x_b + x_c) / 2, (y_b + y_c) / 2 + 2, "(1/f², білий)", size=10, color=MUTED))
    p.append(text((x_c + x_d) / 2 + 6, y_c - 16, "полиця (флор)", size=11, bold=True, color=FIELD))

    # позначки зламів
    for (xx, yy, lbl) in [(x_b, y_b, "куток флікера"), (x_c, y_c, "f₀ / 2Q")]:
        p.append(circle(xx, yy, 4, fill=BG, stroke=INK, sw=1.6))
        p.append(text(xx, yy - 12, lbl, size=10, color=INK))

    b, _, _ = textbox(W / 2, 398,
                      "Чим ближче до несучої — тим вищий шум. Висока добротність Q відсуває весь\n"
                      "графік униз і праворуч: ось чому за чистий такт відповідає резонатор.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'leeson-regions.svg'), W, H, *p,
           title="Спектр фазового шуму генератора: три ділянки за моделлю Лісона")


def jitter_snr():
    """Стеля SNR від джиттера: спадає на 20 дБ за декаду вхідної частоти; родина прямих по tj."""
    W, H = 720, 420
    p = []
    ox, oy = 95, 330
    aw, ah = 545, 250
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))
    p.append(text(ox + aw / 2, oy + 44, "частота сигналу f  (лог-шкала) →", size=12, bold=True))
    p.append(text(ox - 66, oy - ah / 2, "стеля", size=13, bold=True))
    p.append(text(ox - 66, oy - ah / 2 + 17, "SNR, дБ", size=12, bold=True))

    decades = ["100 кГц", "1 МГц", "10М", "100М"]
    for i, lbl in enumerate(decades):
        gx = ox + aw * i / (len(decades) - 1)
        p.append(line(gx, oy, gx, oy - ah, color="#eef0f3", sw=1))
        p.append(text(gx, oy + 18, lbl, size=10, color=MUTED))

    # SNR = -20 log(2 pi f tj). Прямі для трьох tj — спадні з нахилом -20 дБ/дек.
    def snr_db(f, tj):
        return -20.0 * math.log10(2 * math.pi * f * tj)
    fs = [1e5, 1e6, 1e7, 1e8]
    def fx(f):
        return ox + aw * (math.log10(f) - 5) / 3.0   # 100к..100М → 3 декади
    snr_lo, snr_hi = 20.0, 130.0
    def fy(s):
        return oy - ah * (s - snr_lo) / (snr_hi - snr_lo)
    # горизонтальні орієнтири дБ
    for snr_val in (40, 60, 80, 100, 120):
        gy = fy(snr_val)
        p.append(line(ox, gy, ox + aw, gy, color="#eef0f3", sw=1))
        p.append(text(ox - 10, gy + 4, "%d дБ" % snr_val, size=10, color=MUTED, anchor="end"))

    for tj, col, lbl in [(1e-12, FIELD, "tⱼ = 1 пс"), (1e-11, NEG, "tⱼ = 10 пс"), (1e-10, POS, "tⱼ = 100 пс")]:
        pts = [(fx(f), fy(snr_db(f, tj))) for f in fs]
        dp = "M" + " L".join("%.1f %.1f" % q for q in pts)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (dp, col))
        # підпис біля правого кінця, трохи вище лінії
        x_r, y_r = pts[-1]
        p.append(text(x_r - 4, y_r - 9, lbl, size=11, bold=True, color=col, anchor="end"))

    p.append(text(fx(3e5), fy(snr_db(3e5, 1e-12)) - 12, "−20 дБ/дек", size=11, bold=True,
                  color=MUTED, anchor="start"))

    b, _, _ = textbox(W / 2, 398,
                      "Той самий джиттер ставить тим нижчу стелю SNR, чим вища частота сигналу.\n"
                      "Для швидкого АЦП тиша такту важить більше, ніж зайвий розряд.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'jitter-snr.svg'), W, H, *p,
           title="Джиттер ставить стелю SNR: −20·log(2π·f·tⱼ)")


def leeson_corner():
    """[вставка hist] Резонатор як ФНЧ для фазового шуму: підсилення фази проти відступу.
    Плоско поза смугою (давиться), круто росте в смузі (накопичується); кут на f₀/2Q."""
    W, H = 720, 432
    p = []
    ox, oy = 95, 320          # початок осей
    aw, ah = 545, 240
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))      # вісь X (offset, лог) ←росте до несучої вліво
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))      # вісь Y (підсилення фази)
    p.append(text(ox + aw / 2, oy + 44, "← ближче до несучої    відступ f (лог-шкала)    далі →",
                  size=12, bold=True))
    p.append(text(ox - 70, oy - ah / 2 - 6, "наскільки", size=12, bold=True, color=MUTED))
    p.append(text(ox - 70, oy - ah / 2 + 10, "резонатор", size=12, bold=True, color=MUTED))
    p.append(text(ox - 70, oy - ah / 2 + 26, "підсилює фазу", size=12, bold=True, color=MUTED))

    # кут на f₀/2Q — приблизно на третині осі зліва
    x_corner = ox + aw * 0.42
    y_floor = oy - ah * 0.18      # плоска полиця поза смугою
    # крива: плоско справа від кута, далі круто вгору вліво (1/f² → +20 дБ/дек у бік несучої)
    pts = []
    n = 90
    for i in range(n + 1):
        xx = ox + aw * i / n
        if xx >= x_corner:
            yy = y_floor
        else:
            # ліворуч від кута росте лінійно в лог-лог (нахил), обмежимо вершиною
            dec = (x_corner - xx) / (aw / 6.0)   # скільки «декад» лівіше кута
            rise = dec * (ah * 0.30)             # +нахил
            yy = max(oy - ah * 0.97, y_floor - rise)
        pts.append((xx, yy))
    dp = "M" + " L".join("%.1f %.1f" % q for q in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (dp, POS))

    # вертикаль кута + підпис f₀/2Q
    p.append(line(x_corner, oy, x_corner, oy - ah, color=FIELD, sw=1.8, dash="5 5"))
    p.append(circle(x_corner, y_floor, 4.5, fill=BG, stroke=INK, sw=1.8))
    p.append(text(x_corner, oy - ah - 6, "частота Лісона  f₀ / 2Q", size=13, bold=True, color=FIELD))
    p.append(text(x_corner, oy - ah + 12, "= півширина смуги резонатора", size=11, color=MUTED))

    # дві зони: ліворуч (у смузі, накопичується) і праворуч (поза смугою, давиться)
    p.append(text((ox + x_corner) / 2, oy - ah * 0.78, "у СМУЗІ резонатора", size=12, bold=True, color=POS))
    p.append(text((ox + x_corner) / 2, oy - ah * 0.78 + 16, "повільний шум накопичується", size=11, color=POS))
    p.append(text((ox + x_corner) / 2, oy - ah * 0.78 + 31, "→ спідниця круто росте", size=11, color=POS))

    p.append(text((x_corner + ox + aw) / 2, y_floor - 40, "ПОЗА смугою", size=12, bold=True, color=NEG))
    p.append(text((x_corner + ox + aw) / 2, y_floor - 24, "швидкий шум давиться", size=11, color=NEG))
    p.append(text((x_corner + ox + aw) / 2, y_floor - 9, "→ плоска полиця", size=11, color=NEG))

    # підпис нахилу
    p.append(text(ox + aw * 0.12, oy - ah * 0.60, "+20 дБ/дек", size=11, bold=True, color=MUTED,
                  anchor="start"))

    b, _, _ = textbox(W / 2, 404,
                      "Резонатор для фази — низькочастотний фільтр. Те, що повільніше за півсмугу f₀/2Q,\n"
                      "він пропускає й дає накопичитися; швидше — глушить. Звідси й злам спектра.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'leeson-corner.svg'), W, H, *p,
           title="Чому кут спектра стоїть на f₀/2Q: резонатор як ФНЧ для фази")


if __name__ == '__main__':
    jitter_edges()
    two_faces()
    leeson_regions()
    jitter_snr()
    leeson_corner()
    print("OK: 5 figures ->", OUT)
