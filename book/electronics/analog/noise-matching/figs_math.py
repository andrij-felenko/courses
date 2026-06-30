# -*- coding: utf-8 -*-
"""Фігури до вставки «math-noise-parameters.md» (виведення F(Ys) = Fmin + (Rn/Gs)|Ys−Yopt|²).
Дві фігури (окремо від figs.py статті, щоб не чіпати спільний генератор):
  two-sources.svg  — модель двох вхідних джерел шуму: en послідовно, in паралельно, перед тихим двопортом;
                     джерело сигналу з провідністю Ys теж шумить струмом is.
  why-minimum.svg  — ЧОМУ існує мінімум: внесок струму (Gu+RnGc²)/Gs падає, внесок напруги Rn·Gs росте,
                     сума має єдине дно Fmin при Gopt.
Запуск:  python figs_math.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def two_sources():
    """Модель Роте — Дальке: увесь шум двопорту винесено в два вхідні джерела.
    Ліворуч — джерело сигналу (провідність Ys + його тепловий струм is);
    посередині — en (послідовно) та in (паралельно); праворуч — ідеально ТИХИЙ двопорт."""
    W, H = 720, 380
    p = []
    yb = 165                       # рівень нижньої шини (земля-вузол)
    yt = 95                        # рівень верхньої (сигнальної) лінії

    # ── земляна шина ──
    p.append(line(70, yb, 650, yb, color=INK, sw=2))
    for gx in (95, 640):
        p.append(line(gx, yb, gx, yb + 12, color=INK, sw=2))
        p.append(line(gx - 11, yb + 12, gx + 11, yb + 12, color=INK, sw=2.4))

    # ── джерело сигналу: провідність Ys (квадрат) + його шумовий струм is ──
    sx = 130
    p.append(rect(sx - 22, (yt + yb) / 2 - 18, 44, 36, fill="#eef2ff", stroke=NEG, sw=2, rx=4))
    p.append(text(sx, (yt + yb) / 2 + 5, "Ys", size=14, bold=True, color=NEG))
    p.append(line(sx, yt, sx, (yt + yb) / 2 - 18, color=INK, sw=2))
    p.append(line(sx, (yt + yb) / 2 + 18, sx, yb, color=INK, sw=2))
    p.append(text(sx, yt - 28, "джерело сигналу", size=12, bold=True, color=NEG))
    p.append(text(sx, yt - 13, "провідність Ys = Gs + jBs", size=10, color=MUTED))
    # шумовий струм джерела is — стрілка вгору біля Ys
    p.append(arrow(sx + 40, yb - 6, sx + 40, (yt + yb) / 2 + 10, color=NEG, sw=1.6))
    p.append(text(sx + 46, (yt + yb) / 2 + 2, "is", size=12, bold=True, color=NEG, anchor="start"))
    p.append(text(sx + 46, (yt + yb) / 2 + 18, "⟨is²⟩=4kT₀Gs", size=9, color=MUTED, anchor="start"))

    # верхня лінія до вузла входу
    p.append(line(sx, yt, 360, yt, color=INK, sw=2))

    # ── en: шумова напруга ПОСЛІДОВНО у верхній лінії (кружок-джерело) ──
    ex = 270
    p.append(circle(ex, yt, 14, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(ex, yt + 5, "en", size=12, bold=True, color=POS))
    p.append(text(ex, yt - 24, "шумова напруга", size=11, bold=True, color=POS))
    p.append(text(ex, yt - 10, "(послідовно)", size=10, color=MUTED))
    # розрив лінії під кружок en
    p.append(line(sx + 100, yt, ex - 14, yt, color=INK, sw=2))
    p.append(line(ex + 14, yt, 360, yt, color=INK, sw=2))

    # ── in: шумовий струм ПАРАЛЕЛЬНО (вузол входу → земля), стрілка вгору ──
    ix = 360
    p.append(line(ix, yt, ix, yb, color=INK, sw=2))         # вузол входу до землі
    p.append(arrow(ix, yb - 6, ix, yt + 18, color=POS, sw=1.8))
    p.append(circle(ix, (yt + yb) / 2, 13, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(ix, (yt + yb) / 2 + 5, "in", size=12, bold=True, color=POS))
    p.append(text(ix + 18, (yt + yb) / 2 - 10, "шумовий струм", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(ix + 18, (yt + yb) / 2 + 6, "(паралельно)", size=10, color=MUTED, anchor="start"))

    # ── вузол входу → ідеально тихий двопорт ──
    p.append(line(ix, yt, 470, yt, color=INK, sw=2))
    p.append(circle(ix, yt, 3.2, fill=INK, stroke=INK))     # вузол
    # тихий двопорт — рамка
    p.append(rect(470, yt - 40, 150, 110, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    p.append(text(545, yt + 6, "ідеально", size=13, bold=True, color=FIELD))
    p.append(text(545, yt + 24, "ТИХИЙ", size=14, bold=True, color=FIELD))
    p.append(text(545, yt + 42, "двопорт", size=13, bold=True, color=FIELD))
    p.append(line(470, yb, 620, yb, color=INK, sw=2))       # нижній вивід двопорту до шини

    # підпис-висновок
    b, _, _ = textbox(W / 2, 300,
                      "Весь внутрішній шум підсилювача винесено у два вхідні джерела: напругу en (послідовно)\n"
                      "і струм in (паралельно). Сам двопорт — тихий. Сумарний шумовий струм на вході: in + Ys·en.",
                      size=11, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    b2, _, _ = textbox(W / 2, 348,
                       "F = 1 + ⟨|in + Ys·en|²⟩ / ⟨|is|²⟩  — у скільки разів повний вхідний шум більший за шум джерела.",
                       size=11, fill=FILL, stroke=LINE)
    p.append(b2)
    render(os.path.join(OUT, 'two-sources.svg'), W, H, *p,
           title="Модель двох вхідних джерел шуму (Роте — Дальке)")


def why_minimum():
    """ЧОМУ існує оптимум за Gs: внесок струму (Gu+RnGc²)/Gs падає як 1/Gs,
    внесок напруги Rn·Gs росте лінійно; сума F(Gs) має єдине дно Fmin при Gopt."""
    W, H = 720, 420
    p = []
    ox, oy = 95, 300              # початок осей
    axw, axh = 540, 250

    # осі
    p.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=2))
    p.append(text(ox + axw - 4, oy + 26, "провідність джерела Gs = Re(Ys)", size=12, color=MUTED, anchor="end"))
    p.append(text(ox - 18, oy - axh + 8, "F", size=14, bold=True, anchor="end"))

    # моделі (умовні масштабовані величини для форми кривих)
    a = 6.0     # внесок струму ~ a/Gs
    b = 4.0     # внесок напруги ~ b·Gs
    base = 0.9  # умовна «1» (внесок джерела)
    gmin = math.sqrt(a / b)                       # точка дна
    # відображення Gs∈(0.25..3.2) у піксельні x
    g0, g1 = 0.28, 3.2
    def X(g):  return ox + 18 + (axw - 40) * (g - g0) / (g1 - g0)
    # масштаб по Y: підберемо так, щоб усе влізло
    fmax = base + a / g0 if (base + a/g0) < 20 else 18
    ytop = oy - axh + 30
    def Y(val):
        val = min(val, 13.0)
        return oy - (oy - ytop) * (val / 13.0)

    def curve(fn, col, sw=2.2, dash=None):
        pts = []
        N = 220
        for i in range(N + 1):
            g = g0 + (g1 - g0) * i / N
            v = fn(g)
            if v > 13.5:   # за межами поля — не малюємо
                pts = []
                continue
            pts.append((X(g), Y(v)))
        if not pts:
            return
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        ds = ' stroke-dasharray="%s"' % dash if dash else ''
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, col, sw, ds))

    # внесок струму: падає як a/Gs
    curve(lambda g: a / g, NEG, sw=2.0, dash="6 4")
    # внесок напруги: росте b·Gs (+base, щоб не з нуля для читабельності — лишаємо чистим b·g)
    curve(lambda g: b * g, POS, sw=2.0, dash="6 4")
    # сума F(Gs) = base + a/g + b·g
    curve(lambda g: base + a / g + b * g, FIELD, sw=2.8)

    # дно мінімуму
    fmin_val = base + a / gmin + b * gmin
    mx, my = X(gmin), Y(fmin_val)
    p.append(circle(mx, my, 5.5, fill=BG, stroke=FIELD, sw=2.4))
    p.append(line(mx, my, mx, oy, color=INK, sw=1, dash="3 3"))
    p.append(text(mx, oy + 20, "Gopt", size=12, bold=True, color=INK))
    p.append(line(ox, my, mx, my, color=MUTED, sw=1, dash="3 3"))
    p.append(text(ox - 8, my + 4, "Fmin", size=11, bold=True, color=FIELD, anchor="end"))

    # підписи кривих (біля їх «активних» кінців)
    p.append(text(X(0.42) + 4, Y(a / 0.42) - 6, "внесок струму in:  (Gu + Rn·Gc²)/Gs", size=11, bold=True, color=NEG, anchor="start"))
    p.append(text(X(2.95), Y(b * 2.95) - 8, "внесок напруги en:  Rn·Gs", size=11, bold=True, color=POS, anchor="end"))
    p.append(text(X(2.2), Y(base + a / 2.2 + b * 2.2) - 10, "сума F(Gs)", size=12, bold=True, color=FIELD, anchor="middle"))

    # підпис-висновок
    b1, _, _ = textbox(W / 2, 388,
                       "Внесок шумового струму падає як 1/Gs, внесок шумової напруги росте лінійно.\n"
                       "Жоден кінець не виграє → сума має ЄДИНЕ дно: оптимальна провідність Gopt, де F = Fmin.",
                       size=11, fill="#eef7f0", stroke=FIELD)
    p.append(b1)
    render(os.path.join(OUT, 'why-minimum.svg'), W, H, *p,
           title="Чому існує оптимум: перетягування каната за провідність джерела")


if __name__ == '__main__':
    two_sources()
    why_minimum()
    print("OK: 2 figures ->", OUT)
