# -*- coding: utf-8 -*-
"""Фігури до статті «Парадокс зарядки конденсатора»
(book/electronics/analog/rc-charging-energy-loss).
Чотири фігури:
  ledger.svg   — баланс: джерело платить C·V², половина в конденсатор, половина в тепло
  cancel.svg   — чому R випадає: малий R → крутіший струм, але коротший час (площа однакова)
  curves.svg   — наростання напруги (1−e^−t/τ) і спад струму; заштрихована теплова площа
  escape.svg   — три способи: пряма зарядка (50%), сходинками, сталим струмом (→0)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b8860b"   # тепло / втрата
COOL = "#2457d6"   # запасене


def cap_sym(cx, cy, label=None):
    """Простий символ конденсатора (дві горизонтальні пластини)."""
    out = [line(cx - 16, cy, cx + 16, cy, color=INK, sw=2.6),
           line(cx - 16, cy + 8, cx + 16, cy + 8, color=INK, sw=2.6)]
    if label:
        out.append(text(cx + 28, cy + 8, label, size=13, color=INK, anchor="start"))
    return "".join(out)


# ── 1. Баланс енергії ────────────────────────────────────────────────────────
def fig_ledger():
    W, H = 720, 300
    src = textbox(120, 150, "Джерело\nплатить\nC·V²", size=15, fill="#eef4ff",
                  stroke=COOL, bold=True, min_w=140)
    parts = [src[0]]
    # дві стрілки розгалуження
    parts.append(arrow(192, 120, 360, 78, color=COOL, sw=2.4))
    parts.append(arrow(192, 180, 360, 222, color=GOLD, sw=2.4))
    keep = textbox(470, 78, "½·C·V²  запасено\nу конденсаторі", size=14, fill="#eef4ff",
                   stroke=COOL, color=COOL, bold=True, min_w=240)
    heat = textbox(470, 222, "½·C·V²  у тепло\nна опорі R", size=14, fill="#fff7e6",
                   stroke=GOLD, color="#8a6500", bold=True, min_w=240)
    parts.append(keep[0])
    parts.append(heat[0])
    parts.append(text(W / 2, 150, "рівно", size=13, color=MUTED, italic=True))
    parts.append(text(W / 2, 167, "навпіл", size=13, color=MUTED, italic=True))
    return render(os.path.join(IMG, 'ledger.svg'), W, H, *parts,
                  title="Куди йде енергія при зарядці конденсатора через опір")


# ── 2. Чому R випадає з відповіді ────────────────────────────────────────────
def fig_cancel():
    W, H = 720, 330
    ox, oy = 90, 250          # початок осей
    aw, ah = 560, 190         # довжина осей
    parts = [line(ox, oy, ox + aw, oy, color=INK, sw=1.8),
             line(ox, oy, ox, oy - ah, color=INK, sw=1.8),
             text(ox + aw, oy + 22, "час", size=12, color=MUTED, anchor="end"),
             text(ox - 12, oy - ah + 4, "струм I", size=12, color=MUTED, anchor="end")]

    # дві експоненти спаду: малий R (крутий, високий старт, швидкий спад)
    # і великий R (пологий, низький старт, повільний спад). Площа однакова.
    def decay(I0, tau, color, dash=None):
        seg = []
        pts = []
        for k in range(0, 121):
            t = k / 120.0 * 1.0          # нормований час 0..1
            x = ox + t * aw
            y = oy - (I0 * math.exp(-t / tau)) * ah
            pts.append((x, y))
        for i in range(len(pts) - 1):
            seg.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                            color=color, sw=2.6, dash=dash))
        return "".join(seg)

    # малий R: I0=0.95, tau=0.16 ; великий R: I0=0.32, tau=0.5 — площі (I0*tau) ≈ рівні
    parts.append(decay(0.95, 0.155, POS))
    parts.append(decay(0.32, 0.46, NEG, dash="6 4"))

    lo = textbox(250, 70, "малий R: струм великий,\nале спадає швидко", size=12,
                 fill="#fdecea", stroke=POS, color="#8a2018", min_w=250)
    hi = textbox(500, 150, "великий R: струм малий,\nале тягнеться довго", size=12,
                 fill="#eaf0fd", stroke=NEG, color="#1a3a8a", min_w=250)
    parts.append(lo[0])
    parts.append(hi[0])
    note = textbox(W / 2, 300, "площа під кожною кривою однакова  →  однаковий заряд і однакове тепло ½·C·V²",
                   size=12.5, fill="#f0fff4", stroke=FIELD, color="#1d6b3a", min_w=560)
    parts.append(note[0])
    return render(os.path.join(IMG, 'cancel.svg'), W, H, *parts,
                  title="Чому опір зникає з відповіді")


# ── 3. Криві наростання напруги й спаду струму ──────────────────────────────
def fig_curves():
    W, H = 720, 320
    ox, oy = 80, 250
    aw, ah = 580, 190
    parts = [line(ox, oy, ox + aw, oy, color=INK, sw=1.8),
             line(ox, oy, ox, oy - ah, color=INK, sw=1.8),
             text(ox + aw, oy + 22, "час  (у сталих RC)", size=12, color=MUTED, anchor="end")]
    # позначки τ
    for k in (1, 2, 3, 4):
        x = ox + (k / 5.0) * aw
        parts.append(line(x, oy, x, oy + 5, color=MUTED, sw=1.4))
        parts.append(text(x, oy + 20, "%dτ" % k, size=11, color=MUTED))

    # струм i = e^-t/τ, заштрихована теплова зона під ним (мнемоніка: тепло ∝ ∫i·u_R)
    ip = []
    for k in range(0, 161):
        t = k / 160.0 * 5.0
        x = ox + (t / 5.0) * aw
        y = oy - math.exp(-t) * ah * 0.92
        ip.append((x, y))
    # заливка під струмом
    poly = "M %.1f %.1f " % (ip[0][0], oy)
    for (x, y) in ip:
        poly += "L %.1f %.1f " % (x, y)
    poly += "L %.1f %.1f Z" % (ip[-1][0], oy)
    parts.append('<path d="%s" fill="#fff2d6" stroke="none" opacity="0.9"/>' % poly)
    for i in range(len(ip) - 1):
        parts.append(line(ip[i][0], ip[i][1], ip[i + 1][0], ip[i + 1][1], color=GOLD, sw=2.6))

    # напруга u = 1 - e^-t/τ
    up = []
    for k in range(0, 161):
        t = k / 160.0 * 5.0
        x = ox + (t / 5.0) * aw
        y = oy - (1 - math.exp(-t)) * ah * 0.92
        up.append((x, y))
    for i in range(len(up) - 1):
        parts.append(line(up[i][0], up[i][1], up[i + 1][0], up[i + 1][1], color=COOL, sw=2.6))

    parts.append(line(ox, oy - ah * 0.92, ox + aw, oy - ah * 0.92, color=MUTED, sw=1.0, dash="3 4"))
    parts.append(text(ox + aw - 6, oy - ah * 0.92 - 6, "V", size=12, color=MUTED, anchor="end"))

    lu = textbox(470, 70, "напруга на C:  V·(1 − e^−t/RC)", size=12.5,
                 fill="#eef4ff", stroke=COOL, color="#1a3a8a", min_w=270)
    li = textbox(240, 150, "струм заряду:  (V/R)·e^−t/RC\nпід ним — енергія, що гріє R",
                 size=12, fill="#fff7e6", stroke=GOLD, color="#8a6500", min_w=290)
    parts.append(lu[0])
    parts.append(li[0])
    return render(os.path.join(IMG, 'curves.svg'), W, H, *parts,
                  title="Конденсатор наливається, струм згасає")


# ── 4. Три способи зарядки й їхні втрати ────────────────────────────────────
def fig_escape():
    W, H = 720, 300
    cards = [
        (130, "Прямо через R", ["крок V одразу", "втрата 50%"], "#fff7e6", GOLD, "#8a6500"),
        (360, "Сходинками (N кроків)", ["менші стрибки", "втрата ≈ 50%/N"], "#fffbe6", "#b89a00", "#7a6700"),
        (590, "Сталим струмом / котушкою", ["напруга на R мала", "втрата → 0"], "#f0fff4", FIELD, "#1d6b3a"),
    ]
    parts = []
    for (cx, title, lines, fill, stroke, txt) in cards:
        box, w, h = textbox(cx, 150, "\n".join([title, ""] + lines), size=13,
                            fill=fill, stroke=stroke, color=txt, bold=False, min_w=200)
        parts.append(box)
        # підкреслити заголовок жирним окремо
        parts.append(text(cx, 150 - h / 2 + 24, title, size=14, color=txt, bold=True))
    # стрілка «менше втрат →»
    parts.append(arrow(60, 255, 660, 255, color=INK, sw=2.0))
    parts.append(text(W / 2, 285, "що рівніше тримаєш напругу на опорі — то менше тепла", size=12.5,
                      color=MUTED, italic=True))
    return render(os.path.join(IMG, 'escape.svg'), W, H, *parts,
                  title="Як обійти втрату половини")


if __name__ == "__main__":
    fig_ledger()
    fig_cancel()
    fig_curves()
    fig_escape()
    print("OK: figures written to", IMG)
