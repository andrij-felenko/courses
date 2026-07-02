# -*- coding: utf-8 -*-
"""Фігури до статті «Коротке замикання»
(book/electronics/analog/short-circuit).

Кут статті: коротке замикання = поява шляху з майже нульовим опором навколо
навантаження чи впоперек джерела. Закон Ома I = V/R миттєво пояснює вибух струму
(R→0 ⇒ I→∞), а реальну межу задає внутрішній опір джерела й опір проводів.

Фігури:
  paths.svg   — нормальний шлях крізь навантаження ↔ короткий шлях в обхід (R≈0)
  iv.svg      — гіпербола I = V/R: опір падає до нуля — струм злітає до неба
  sources.svg — три реальні причини КЗ зводяться до «R≈0 впоперек джерела»,
                а справжню стелю струму ставить внутрішній опір джерела
  fuse-timeline.svg — родовід жертовної дротинки (вставка hist-fuse-lineage):
                Бреге 1847 → фольга/дротини 1864 → свинцева ланка Едісона 1880
                → патент-блок US438305 (подано 1885, видано 1890)
                → автомат Штоца 1924. Ідея старша за Едісона, винахід колективний.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ────────────────────────────────────────────────────────
def battery(x, y, h=44, label=None):
    """Батарея (джерело) вертикально: довга риска «+» згори, коротка «−» знизу."""
    out = [line(x, y - h / 2, x, y - 8, color=INK, sw=1.8),
           line(x - 15, y - 8, x + 15, y - 8, color=INK, sw=2.6),      # + (довга)
           line(x - 8, y + 2, x + 8, y + 2, color=INK, sw=1.6),        # − (коротка)
           line(x, y + 2, x, y + h / 2, color=INK, sw=1.8)]
    out.append(text(x + 22, y - 8, "+", size=14, color=POS, bold=True, anchor="middle"))
    out.append(text(x + 22, y + 8, "−", size=14, color=NEG, bold=True, anchor="middle"))
    if label:
        out.append(text(x - 22, y, label, size=12, color=INK, bold=True, anchor="end"))
    return "".join(out), {"top": (x, y - h / 2), "bot": (x, y + h / 2)}


def res_v(x, y1, y2, label=None, col=INK):
    """Вертикальний резистор-зигзаг (навантаження)."""
    out = []
    n, amp = 6, 6
    seg = (y2 - y1) / (n + 2)
    out.append(line(x, y1, x, y1 + seg, color=col, sw=1.8))
    yy = y1 + seg
    for i in range(n):
        nx = x + (amp if i % 2 == 0 else -amp)
        prevx = x if i == 0 else (x - amp if i % 2 == 1 else x + amp)
        out.append(line(prevx, yy, nx, yy + seg, color=col, sw=1.8))
        yy += seg
    lastx = x + (amp if (n - 1) % 2 == 0 else -amp)
    out.append(line(lastx, yy, x, yy + seg, color=col, sw=1.8))
    out.append(line(x, yy + seg, x, y2, color=col, sw=1.8))
    if label:
        out.append(text(x + 16, (y1 + y2) / 2 + 4, label, size=12, color=col, bold=True, anchor="start"))
    return "".join(out)


def spark(cx, cy, r=13, col=POS):
    """Зірочка-іскра — позначка місця замикання/перегріву."""
    out = []
    pts = []
    for k in range(16):
        ang = math.pi * k / 8
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts) + " Z"
    out.append('<path d="%s" fill="%s" fill-opacity="0.9" stroke="%s" stroke-width="1"/>' % (d, col, col))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. paths.svg — нормальний шлях крізь навантаження ↔ короткий шлях в обхід
# ════════════════════════════════════════════════════════════════════════════
def fig_paths():
    W, H = 700, 330
    f = []

    def stage(ox, title, shorted, col, note):
        sub = []
        bx = ox + 40
        by = 175
        bsvg, bn = battery(bx, by, h=64, label="V")
        top = ox + 40
        rightx = ox + 240
        yT = by - 74          # верхня шина
        yB = by + 74          # нижня шина
        # шини від батареї
        sub.append(line(bx, bn["top"][1], bx, yT, color=INK, sw=2))
        sub.append(line(bx, yT, rightx, yT, color=INK, sw=2))
        sub.append(line(bx, bn["bot"][1], bx, yB, color=INK, sw=2))
        sub.append(line(bx, yB, rightx, yB, color=INK, sw=2))
        # навантаження праворуч
        sub.append(res_v(rightx, yT, yB, label="R", col=(MUTED if shorted else INK)))
        sub.append(text(rightx + 18, yT - 6, "навантаження", size=10, color=MUTED, anchor="start"))
        sub.append(bsvg)
        # струм — стрілка на верхній шині
        if shorted:
            # коротка перемичка посередині
            sx = ox + 150
            sub.append(line(sx, yT, sx, yB, color=POS, sw=3.2))
            sub.append(spark(sx, by, r=15, col=POS))
            sub.append(text(sx, yT - 10, "R ≈ 0", size=12, color=POS, bold=True))
            sub.append(text(sx, yB + 20, "струм тече ТУТ", size=11, color=POS, bold=True))
            # жирна стрілка великого струму
            sub.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="5" marker-end="url(#arrow)"/>'
                       % (bx + 20, yT, sx - 6, yT, POS))
            sub.append(text((bx + sx) / 2, yT - 8, "величезний I", size=11, color=POS, bold=True))
        else:
            sub.append(arrow(bx + 24, yT, ox + 150, yT, color=FIELD, sw=2.4))
            sub.append(text(ox + 120, yT - 8, "робочий I = V/R", size=11, color=FIELD, bold=True))
            sub.append(text(ox + 150, by, "весь струм\nіде крізь R", size=10, color=MUTED))
            # багаторядковий підпис через два text
        sub.append(text(ox + 140, 44, title, size=14, color=col, bold=True))
        sub.append(text(ox + 140, 300, note, size=10.5, color=MUTED))
        return "".join(sub)

    f.append(stage(20, "НОРМА", False, FIELD, "струм обмежений опором R"))
    f.append(stage(370, "КОРОТКЕ ЗАМИКАННЯ", True, POS, "струм обмежений лише крихтою опору дротів і джерела"))

    # розділова риска
    f.append(line(355, 60, 355, 290, color=MUTED, sw=1, dash="4 5"))
    render(os.path.join(IMG, "paths.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. iv.svg — гіпербола I = V/R: R→0 ⇒ I→∞
# ════════════════════════════════════════════════════════════════════════════
def fig_iv():
    W, H = 680, 360
    f = []
    ox, oy = 90, 300           # початок осей
    aw, ah = 500, 250

    f.append(text(W / 2, 30, "Закон Ома при сталій напрузі: опір падає — струм злітає", size=14, bold=True))

    # осі
    f.append(arrow(ox, oy, ox + aw + 10, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ah - 10, color=INK, sw=1.8))
    f.append(text(ox + aw + 6, oy + 20, "опір R  →", size=12, color=INK, anchor="end"))
    f.append(text(ox - 10, oy - ah - 2, "струм I", size=12, color=INK, anchor="end"))

    # гіпербола I = V/R (V=12), масштаб підібрано під рамку
    V = 12.0
    Rmin, Rmax = 0.35, 12.0
    Imax_draw = 24.0          # стеля малюнка по струму (А)
    def X(R): return ox + (R / Rmax) * aw
    def Y(I): return oy - min(I, Imax_draw) / Imax_draw * ah
    pts = []
    R = Rmin
    while R <= Rmax + 1e-9:
        pts.append((X(R), Y(V / R)))
        R += 0.06
    f.append('<path d="M ' + " L ".join("%.1f %.1f" % p for p in pts) + '" fill="none" stroke="%s" stroke-width="2.6"/>' % POS)

    # робоча точка (нормальна): R=6 Ом
    Rn = 6.0
    f.append(line(X(Rn), oy, X(Rn), Y(V / Rn), color=FIELD, sw=1.2, dash="4 4"))
    f.append(line(ox, Y(V / Rn), X(Rn), Y(V / Rn), color=FIELD, sw=1.2, dash="4 4"))
    f.append(circle(X(Rn), Y(V / Rn), 4, fill=FIELD, stroke=FIELD))
    f.append(text(X(Rn) + 8, Y(V / Rn) - 8, "норма: R=6 Ω → I=2 A", size=11, color=FIELD, bold=True, anchor="start"))

    # зона КЗ — біля нуля опору
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.08" stroke="none"/>'
             % (ox, oy - ah - 10, X(1.2) - ox, ah + 10, POS))
    f.append(text(X(0.6), oy - ah + 14, "КЗ", size=15, color=POS, bold=True))
    f.append(text(X(0.6), oy - ah + 32, "R→0", size=11, color=POS))
    # вертикальна стрілка «струм у стелю»
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.4" stroke-dasharray="3 3" marker-end="url(#arrow)"/>'
             % (X(0.42), oy - 30, X(0.42), oy - ah + 40, POS))

    bb, _, _ = textbox(W / 2 + 60, oy - 34,
                       "гіпербола: половина опору — подвійний струм;\nбіля нуля — струм не має стелі, крім опору самих дротів",
                       size=10.5, color=INK, fill=FILL, stroke=MUTED)
    f.append(bb)
    render(os.path.join(IMG, "iv.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. sources.svg — три причини КЗ зводяться до R≈0; стелю ставить R_внутр
# ════════════════════════════════════════════════════════════════════════════
def fig_sources():
    W, H = 700, 360
    f = []
    f.append(text(W / 2, 30, "Різні причини — той самий підсумок: R ≈ 0 впоперек джерела", size=14, bold=True))

    causes = [
        ("місток припою", "дві доріжки плати\nз'єднав наплив олова"),
        ("продавлена ізоляція", "жила торкнулась\nсусідньої чи корпуса"),
        ("вихід у стіну", "транзистор відкрився\nнавстіж, опору майже нема"),
    ]
    xs = [140, 350, 560]
    yb = 120
    for (head, sub), x in zip(causes, xs):
        f.append(circle(x, yb, 30, fill="#fdecea", stroke=POS, sw=2))
        f.append(spark(x, yb, r=15, col=POS))
        f.append(text(x, yb + 52, head, size=12, color=POS, bold=True))
        f.append(text(x, yb + 70, sub.split("\n")[0], size=10, color=MUTED))
        f.append(text(x, yb + 84, sub.split("\n")[1], size=10, color=MUTED))
        # стрілка вниз до спільного вузла
        f.append(arrow(x, yb + 96, x, yb + 118, color=MUTED, sw=1.6))

    # спільний висновок-вузол
    yc = 262
    bb, w, h = textbox(W / 2, yc, "шлях з майже нульовим опором навколо/впоперек джерела",
                       size=12, color=POS, bold=True, fill="#fdecea", stroke=POS)
    f.append(bb)

    # що обмежує струм: внутрішній опір
    yr = 322
    bb2, _, _ = textbox(W / 2, yr,
                        "струм КЗ = V / (R_внутр + R_дротів)   — стелю ставить не КЗ, а опір самого джерела й провідників",
                        size=11, color=INK, fill=FILL, stroke=INK)
    f.append(bb2)
    render(os.path.join(IMG, "sources.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. fuse-timeline.svg — родовід жертовної дротинки (вставка hist-fuse-lineage)
# ════════════════════════════════════════════════════════════════════════════
def fig_fuse_timeline():
    W, H = 720, 340
    f = []
    f.append(text(W / 2, 30, "Родовід жертовної дротинки: ідея старша за Едісона",
                  size=15, bold=True))
    f.append(text(W / 2, 50, "жоден рік не «народження фактично» — це ланцюг рук",
                  size=10.5, color=MUTED))

    # горизонтальна вісь часу
    ax0, ax1 = 60, W - 40
    ay = 210
    f.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (ax1, ay, ax1 - 10, ay - 5, ax1 - 10, ay + 5, INK))

    # роки й підписи (рік, заголовок, підзаголовок, зверху/знизу, колір)
    marks = [
        (1847, "Бреге", "ідея: тонкий дріт\nяк заслін від блискавки", True,  FIELD),
        (1864, "фольга й дротини", "уже в ужитку на\nтелеграфі й освітленні", False, INK),
        (1880, "свинцева ланка", "патент Едісона,\nтравень 1880", True,  POS),
        (1890, "патент-блок", "US 438305:\nподано 1885 → видано 1890", False, POS),
        (1924, "автомат", "Штоц + Шахтнер:\nвимикач, що не згоряє", True,  NEG),
    ]
    y0, y1 = 1840, 1930
    def X(y): return ax0 + (y - y0) / (y1 - y0) * (ax1 - ax0 - 20)

    for yr, head, sub, up, col in marks:
        x = X(yr)
        f.append(circle(x, ay, 6, fill=col, stroke=col))
        f.append(text(x, ay + (24 if not up else -14), str(yr),
                      size=13, color=col, bold=True))
        if up:
            f.append(line(x, ay - 6, x, ay - 34, color=col, sw=1.2, dash="3 3"))
            ty = ay - 50
            f.append(text(x, ty, head, size=12, color=col, bold=True))
            f.append(text(x, ty + 16, sub.split("\n")[0], size=9.5, color=MUTED))
            f.append(text(x, ty + 29, sub.split("\n")[1], size=9.5, color=MUTED))
        else:
            f.append(line(x, ay + 6, x, ay + 34, color=col, sw=1.2, dash="3 3"))
            ty = ay + 52
            f.append(text(x, ty, head, size=12, color=col, bold=True))
            f.append(text(x, ty + 16, sub.split("\n")[0], size=9.5, color=MUTED))
            f.append(text(x, ty + 29, sub.split("\n")[1], size=9.5, color=MUTED))

    # підсумкова стрічка знизу
    bb, _, _ = textbox(W / 2, H - 22,
                       "заслін дозрів на телеграфі задовго до розетки; Едісон зробив "
                       "із нього придатний виріб, а не «вигадав уперше»",
                       size=10, color=INK, fill=FILL, stroke=MUTED)
    f.append(bb)
    render(os.path.join(IMG, "fuse-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_paths()
    fig_iv()
    fig_sources()
    fig_fuse_timeline()
    print("OK: 4 фігури у", IMG)
