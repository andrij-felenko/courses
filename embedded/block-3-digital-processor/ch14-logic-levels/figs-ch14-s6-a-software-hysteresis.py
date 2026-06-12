# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для ⚙️-вставки до теми 3.1.6 — «Гістерезис у коді:
програмний тригер Шмітта для зашумленого АЦП-сигналу».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(fig-14-6a-*). НЕ чіпає головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Нумерація підписів у тексті — Рис. 3.1.6a.k.
"""
import os
import math
import random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
ORANGE = "#e08030"
PURPLE = "#7a3fb0"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         ORANGE: "aOrange", PURPLE: "aPurple"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def polygon(points, fill=INK, stroke="none", sw=0, opacity=1.0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" fill-opacity="{opacity}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
#  Спільний «брудний» сигнал: повільний підйом-спад + шум.
#  Один і той самий ряд відліків живить обидві перші фігури — щоб порівняння
#  «один поріг» проти «два пороги» було чесним (та сама хвиля, той самий шум).
# ─────────────────────────────────────────────────────────────────────────────
def _noisy_signal(n=240, lo=0.6, hi=2.7, noise=0.16, seed=7):
    """Повільний трикутний хід (вгору, тоді вниз) із доданим шумом.
    Повертає список значень у вольтах."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        t = i / (n - 1)
        # трикутна обвідна: 0→1→0
        base = (2 * t) if t < 0.5 else (2 * (1 - t))
        v = lo + (hi - lo) * base
        v += rnd.uniform(-noise, noise)
        out.append(v)
    return out


def _simulate(sig, vt_lo, vt_hi):
    """Прогнати ряд через ДВОПОРОГОВИЙ автомат; повернути список станів 0/1
    і кількість перемикань."""
    state = 0
    states = []
    edges = 0
    for v in sig:
        prev = state
        if state == 0 and v > vt_hi:
            state = 1
        elif state == 1 and v < vt_lo:
            state = 0
        if state != prev:
            edges += 1
        states.append(state)
    return states, edges


def _simulate_single(sig, vt):
    """Один поріг (наївне порівняння) — рахуємо хибні перемикання."""
    state = 0
    states = []
    edges = 0
    for v in sig:
        prev = state
        state = 1 if v > vt else 0
        if state != prev:
            edges += 1
        states.append(state)
    return states, edges


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.1.6a.1 — один поріг + шум у коді → дребезг (наївний if)
# ════════════════════════════════════════════════════════════════════════════
def fig_single_threshold():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 30, "Наївне порівняння в коді: один поріг + шум = дребезг",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "повільний зашумлений відлік АЦП біля єдиного порога перемикає вихід багато разів замість одного",
              11, GREY, "middle", style="italic")

    sig = _noisy_signal()
    n = len(sig)
    vt = 1.65                       # єдиний поріг посередині
    states, edges = _simulate_single(sig, vt)

    # ── верхня панель: сигнал і поріг ──
    ax, aw = 70, 560
    ytop, ybot = 90, 250            # 0.0 В ↔ ybot, 3.3 В ↔ ytop
    vmin, vmax = 0.0, 3.3

    def vy(v):
        return ybot - (v - vmin) / (vmax - vmin) * (ybot - ytop)

    def tx(i):
        return ax + i / (n - 1) * aw

    # сітка по напрузі
    for v in (0.0, 1.0, 2.0, 3.0):
        s += line(ax, vy(v), ax + aw, vy(v), FAINT, 1.2)
        s += text(ax - 8, vy(v) + 4, f"{v:.0f}", 10, GREY, "end")
    s += text(ax - 28, (ytop + ybot) / 2, "В", 11, GREY, "middle", style="italic")

    # поріг
    s += line(ax, vy(vt), ax + aw, vy(vt), RED, 2.0, "7,4")
    s += text(ax + aw + 8, vy(vt) + 4, "поріг VT", 11, RED, "start", "bold")

    # сигнал
    pts = [(tx(i), vy(v)) for i, v in enumerate(sig)]
    s += polyline(pts, BLUE, 2.0)
    s += text(ax + 6, ytop - 8, "відлік АЦП  v[n]  (повільний, зашумлений)",
              11.5, BLUE, "start", "bold")

    # підсвітити зону перетину (де хвиля «сидить» на порозі)
    # знайдемо діапазон індексів, де сигнал близько до порога
    near = [i for i, v in enumerate(sig) if abs(v - vt) < 0.45]
    if near:
        i0, i1 = min(near), max(near)
        s += rect(tx(i0), ytop, tx(i1) - tx(i0), ybot - ytop, ORANGE, "none", 0)
        s += polygon([(tx(i0), ytop), (tx(i1), ytop), (tx(i1), ybot), (tx(i0), ybot)],
                     ORANGE, "none", 0, 0.10)
        s += text((tx(i0) + tx(i1)) / 2, ytop + 16, "тут шум скаче через поріг",
                  10, ORANGE, "middle", "bold")

    # ── нижня панель: вихід state (0/1) ──
    oy1, oy0 = 300, 360             # рівень «1» ↔ oy1, «0» ↔ oy0
    s += line(ax, oy0, ax + aw, oy0, GREY, 1.3)
    s += line(ax, oy1, ax + aw, oy1, FAINT, 1.2)
    s += text(ax - 8, oy0 + 4, "0", 10, GREY, "end")
    s += text(ax - 8, oy1 + 4, "1", 10, GREY, "end")
    s += text(ax - 28, (oy0 + oy1) / 2, "state", 10, GREY, "middle", style="italic")

    opts = []
    for i, st in enumerate(states):
        y = oy1 if st else oy0
        if i > 0:
            opts.append((tx(i), oy1 if states[i - 1] else oy0))
        opts.append((tx(i), y))
    s += polyline(opts, RED, 2.4)
    s += text(ax + 6, oy1 - 10, "state = (v > VT)   — голий if", 11.5, RED, "start", "bold")
    s += text(ax + aw / 2, oy0 + 26,
              f"{edges} перемикань на ОДИН перехід сигналу — пачка хибних подій",
              11.5, RED, "middle", "bold")

    # ── права колонка: пояснення коду ──
    bx = 670
    s += rect(bx, 86, 250, 150, "#fff6f3", RED, 1.6, 12)
    s += text(bx + 125, 110, "Що сталося", 12.5, RED, "middle", "bold")
    s += text(bx + 16, 136, "Біля порога корисний", 10.5, INK, "start")
    s += text(bx + 16, 154, "сигнал майже не росте,", 10.5, INK, "start")
    s += text(bx + 16, 172, "а шум ±0.16 В кидає", 10.5, INK, "start")
    s += text(bx + 16, 190, "v[n] то вище, то нижче.", 10.5, INK, "start")
    s += text(bx + 16, 212, "Кожен перетин → нова", 10.5, INK, "start")
    s += text(bx + 16, 230, "хибна подія в коді.", 10.5, INK, "start")

    s += rect(bx, 250, 250, 110, "#f7f7f7", GREY, 1.4, 12)
    s += text(bx + 125, 274, "Наслідок для логіки", 11.5, INK, "middle", "bold")
    s += text(bx + 16, 298, "• одне натискання → 10", 10.5, INK, "start")
    s += text(bx + 16, 316, "• один перехід давача →", 10.5, INK, "start")
    s += text(bx + 28, 332, "серія фантомних спрацювань", 9.5, GREY, "start")
    s += text(bx + 16, 352, "• лічильники брешуть", 10.5, INK, "start")

    save("fig-14-6a-1-single-threshold.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.1.6a.2 — два пороги в коді → одне чисте перемикання
# ════════════════════════════════════════════════════════════════════════════
def fig_two_thresholds():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 30, "Два пороги в коді: мертва смуга вбиває дребезг",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "той самий відлік, той самий шум — але вихід тримає стан, поки сигнал не пробив ПРОТИЛЕЖНИЙ поріг",
              11, GREY, "middle", style="italic")

    sig = _noisy_signal()           # ТОЙ САМИЙ ряд, що й на Рис. 3.1.6a.1
    n = len(sig)
    vt_hi, vt_lo = 2.0, 1.2         # верхній / нижній пороги
    states, edges = _simulate(sig, vt_lo, vt_hi)

    ax, aw = 70, 560
    ytop, ybot = 90, 250
    vmin, vmax = 0.0, 3.3

    def vy(v):
        return ybot - (v - vmin) / (vmax - vmin) * (ybot - ytop)

    def tx(i):
        return ax + i / (n - 1) * aw

    for v in (0.0, 1.0, 2.0, 3.0):
        s += line(ax, vy(v), ax + aw, vy(v), FAINT, 1.2)
        s += text(ax - 8, vy(v) + 4, f"{v:.0f}", 10, GREY, "end")
    s += text(ax - 28, (ytop + ybot) / 2, "В", 11, GREY, "middle", style="italic")

    # мертва смуга між порогами (зелена)
    s += polygon([(ax, vy(vt_hi)), (ax + aw, vy(vt_hi)),
                  (ax + aw, vy(vt_lo)), (ax, vy(vt_lo))], GREEN, "none", 0, 0.12)
    s += line(ax, vy(vt_hi), ax + aw, vy(vt_hi), GREEN, 2.0, "7,4")
    s += line(ax, vy(vt_lo), ax + aw, vy(vt_lo), GREEN, 2.0, "7,4")
    s += text(ax + aw + 8, vy(vt_hi) + 4, "VT+ = 2.0", 11, GREEN, "start", "bold")
    s += text(ax + aw + 8, vy(vt_lo) + 4, "VT− = 1.2", 11, GREEN, "start", "bold")
    s += text(ax + aw - 6, vy((vt_hi + vt_lo) / 2) + 4, "мертва смуга  VH = 0.8 В",
              10.5, GREEN, "end", "bold")

    # сигнал
    pts = [(tx(i), vy(v)) for i, v in enumerate(sig)]
    s += polyline(pts, BLUE, 2.0)
    s += text(ax + 6, ytop - 8, "той самий відлік АЦП  v[n]",
              11.5, BLUE, "start", "bold")

    # ── нижня панель: вихід ──
    oy1, oy0 = 300, 360
    s += line(ax, oy0, ax + aw, oy0, GREY, 1.3)
    s += line(ax, oy1, ax + aw, oy1, FAINT, 1.2)
    s += text(ax - 8, oy0 + 4, "0", 10, GREY, "end")
    s += text(ax - 8, oy1 + 4, "1", 10, GREY, "end")
    s += text(ax - 28, (oy0 + oy1) / 2, "state", 10, GREY, "middle", style="italic")

    opts = []
    for i, st in enumerate(states):
        y = oy1 if st else oy0
        if i > 0:
            opts.append((tx(i), oy1 if states[i - 1] else oy0))
        opts.append((tx(i), y))
    s += polyline(opts, GREEN, 2.6)

    # позначити дві справжні події
    rises = [i for i in range(1, n) if states[i] == 1 and states[i - 1] == 0]
    falls = [i for i in range(1, n) if states[i] == 0 and states[i - 1] == 1]
    for i in rises:
        s += arrow(tx(i), oy0 + 28, tx(i), oy1 + 4, GREEN, 1.8)
        s += text(tx(i), oy0 + 44, "0→1", 10, GREEN, "middle", "bold")
    for i in falls:
        s += arrow(tx(i), oy1 - 4, tx(i), oy0 - 4, GREEN, 1.8)
        s += text(tx(i), oy0 - 12, "1→0", 10, GREEN, "middle", "bold")

    s += text(ax + 6, oy1 - 10, "state із гістерезисом", 11.5, GREEN, "start", "bold")
    s += text(ax + aw / 2, oy0 + 70,
              f"{edges} перемикання — рівно стільки, скільки разів сигнал реально перетнув смугу",
              11.5, GREEN, "middle", "bold")

    # ── права колонка: правило ──
    bx = 670
    s += rect(bx, 86, 250, 200, "#eef7f0", GREEN, 1.6, 12)
    s += text(bx + 125, 110, "Правило двох порогів", 12.5, GREEN, "middle", "bold")
    s += text(bx + 16, 138, "якщо state == 0:", 11, INK, "start", "bold")
    s += text(bx + 28, 158, "перейти в 1 лише коли", 10, INK, "start")
    s += text(bx + 28, 175, "v > VT+  (2.0 В)", 11, GREEN, "start", "bold")
    s += text(bx + 16, 202, "якщо state == 1:", 11, INK, "start", "bold")
    s += text(bx + 28, 222, "перейти в 0 лише коли", 10, INK, "start")
    s += text(bx + 28, 239, "v < VT−  (1.2 В)", 11, GREEN, "start", "bold")
    s += text(bx + 16, 266, "інакше — НЕ чіпати state", 10.5, INK, "start", "bold")

    s += rect(bx, 300, 250, 86, "#fffaf2", ORANGE, 1.4, 12)
    s += text(bx + 125, 322, "Чому працює", 11.5, ORANGE, "middle", "bold")
    s += text(bx + 16, 344, "шум ±0.16 В « смуга 0.8 В,", 10, INK, "start")
    s += text(bx + 16, 361, "тож, перемкнувшись, сигнал", 10, INK, "start")
    s += text(bx + 16, 377, "не дістає до іншого порога", 10, INK, "start")

    save("fig-14-6a-2-two-thresholds.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.1.6a.3 — автомат із двох станів (псевдокод як діаграма)
# ════════════════════════════════════════════════════════════════════════════
def fig_state_machine():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 30, "Програмний тригер Шмітта — це автомат із двох станів",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "один біт пам'яті (state) + дві умови переходу; на кожен відлік виконуємо лише кілька порівнянь",
              11, GREY, "middle", style="italic")

    # два стани-кружальця
    cx0, cx1 = 280, 660
    cyc = 175
    r = 64
    s += circle(cx0, cyc, r, "#fdeeec", RED, 2.4)
    s += text(cx0, cyc - 8, "state = 0", 15, RED, "middle", "bold")
    s += text(cx0, cyc + 14, "(низько)", 11.5, INK, "middle")
    s += circle(cx1, cyc, r, "#eef7f0", GREEN, 2.4)
    s += text(cx1, cyc - 8, "state = 1", 15, GREEN, "middle", "bold")
    s += text(cx1, cyc + 14, "(високо)", 11.5, INK, "middle")

    # перехід 0→1 (верхня дуга)
    s += f'<path d="M {cx0 + r - 6} {cyc - 30} C {cx0 + 130} {cyc - 95}, {cx1 - 130} {cyc - 95}, {cx1 - r + 6} {cyc - 30}" fill="none" stroke="{GREEN}" stroke-width="2.4" marker-end="url(#aGreen)"/>\n'
    s += text((cx0 + cx1) / 2, cyc - 86, "v > VT+", 13, GREEN, "middle", "bold")
    s += text((cx0 + cx1) / 2, cyc - 68, "(сигнал упевнено пробив верхній поріг)",
              10, GREY, "middle")

    # перехід 1→0 (нижня дуга)
    s += f'<path d="M {cx1 - r + 6} {cyc + 30} C {cx1 - 130} {cyc + 95}, {cx0 + 130} {cyc + 95}, {cx0 + r - 6} {cyc + 30}" fill="none" stroke="{BLUE}" stroke-width="2.4" marker-end="url(#aBlue)"/>\n'
    s += text((cx0 + cx1) / 2, cyc + 92, "v < VT−", 13, BLUE, "middle", "bold")
    s += text((cx0 + cx1) / 2, cyc + 110, "(сигнал упав аж нижче нижнього порога)",
              10, GREY, "middle")

    # петлі «лишитися» (self-loop) на кожному стані
    s += f'<path d="M {cx0 - r + 14} {cyc + 22} C {cx0 - 96} {cyc + 80}, {cx0 - 96} {cyc - 80}, {cx0 - r + 14} {cyc - 22}" fill="none" stroke="{GREY}" stroke-width="1.8" marker-end="url(#aInk)"/>\n'
    s += text(cx0 - 104, cyc + 4, "v ≤ VT+", 11, GREY, "end", "bold")
    s += text(cx0 - 104, cyc + 20, "лишитись 0", 9.5, GREY, "end")
    s += f'<path d="M {cx1 + r - 14} {cyc - 22} C {cx1 + 96} {cyc - 80}, {cx1 + 96} {cyc + 80}, {cx1 + r - 14} {cyc + 22}" fill="none" stroke="{GREY}" stroke-width="1.8" marker-end="url(#aInk)"/>\n'
    s += text(cx1 + 104, cyc + 4, "v ≥ VT−", 11, GREY, "start", "bold")
    s += text(cx1 + 104, cyc + 20, "лишитись 1", 9.5, GREY, "start")

    # підпис під діаграмою: зв'язок із залізом
    s += rect(150, 286, 640, 52, "#f7f7f7", PURPLE, 1.5, 12)
    s += text(470, 308,
              "«state» — це той самий один біт, що пам'ятає апаратний тригер Шмітта (§2.8.8):",
              11.5, INK, "middle", "bold")
    s += text(470, 326,
              "усередині мертвої смуги вихід залежить не від поточного v, а від того, ЗВІДКИ ми прийшли.",
              10.5, PURPLE, "middle")

    save("fig-14-6a-3-state-machine.svg", s)


if __name__ == "__main__":
    fig_single_threshold()
    fig_two_thresholds()
    fig_state_machine()
    print("OK")
