# -*- coding: utf-8 -*-
"""
SVG-фігури для ⚙️-вставки §1.7.1a — «Синус у коді: таблиця відліків і фазовий акумулятор».
Окремий скрипт (за §9 не чіпаємо головний figs.py розділу). Чистий Python, без залежностей.
Вивід → ./img/ з УНІКАЛЬНИМИ іменами (префікс fig-7-1a-*).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Нумерація підписів — Рис. 1.7.1a.k.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
ORANGE = "#e08030"
PURPLE = "#7a3ea8"
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


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", ORANGE: "aOrange", PURPLE: "aPurple"}


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


def mono(x, y, s, size=14, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, monospace" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def write(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)


# ──────────────────────────────────────────────────────────────────────────
# Рис. 1.7.1a.1 — Таблиця відліків: коло слотів + сходинкова синусоїда на виході
# ──────────────────────────────────────────────────────────────────────────
def fig_lut():
    W, H = 760, 380
    s = header(W, H)
    s += text(W / 2, 26, "Таблиця відліків: один період синуса, нарізаний на N точок",
              size=16, anchor="middle", weight="bold")

    # --- ліворуч: кільце слотів таблиці (N = 16), кут індексує таблицю ---
    cx, cy, R = 195, 215, 120
    N = 16
    s += circle(cx, cy, R, fill="none", stroke=FAINT, w=14)
    s += text(cx, 70, "пам'ять = коло фаз", size=14, anchor="middle", color=GREY)

    # активний індекс (де зараз вказівник)
    k_active = 3
    for k in range(N):
        ang = -math.pi / 2 + 2 * math.pi * k / N  # 0 угорі, за годинниковою
        x = cx + R * math.cos(ang)
        y = cy + R * math.sin(ang)
        active = (k == k_active)
        s += circle(x, y, 8.5, fill=(ORANGE if active else "#ffffff"),
                    stroke=(ORANGE if active else INK), w=2)
        # підпис індексу зовні
        xl = cx + (R + 22) * math.cos(ang)
        yl = cy + (R + 22) * math.sin(ang) + 4
        s += text(xl, yl, str(k), size=11, anchor="middle",
                  color=(ORANGE if active else GREY))

    # вказівник-фаза (стрілка з центру на активний слот)
    ang_a = -math.pi / 2 + 2 * math.pi * k_active / N
    s += arrow(cx, cy, cx + (R - 12) * math.cos(ang_a), cy + (R - 12) * math.sin(ang_a),
               color=ORANGE, w=3)
    s += circle(cx, cy, 4, fill=INK, stroke=INK, w=1)
    s += text(cx, cy + 40, "фаза → індекс", size=13, anchor="middle", color=ORANGE, weight="bold")
    s += text(cx, cy - 28, "повний оберт", size=12, anchor="middle", color=GREY)
    s += text(cx, cy - 13, "= один період", size=12, anchor="middle", color=GREY)

    # --- праворуч: значення в комірках утворюють синус (сходинками) ---
    gx0, gy0 = 400, 110   # верх-лівий кут графіка
    gw, gh = 320, 210
    midy = gy0 + gh / 2
    s += line(gx0, midy, gx0 + gw, midy, color=GREY, w=1)        # вісь t
    s += line(gx0, gy0, gx0, gy0 + gh, color=GREY, w=1)          # вісь v
    s += text(gx0 + gw + 6, midy + 4, "k", size=13, color=GREY)
    s += text(gx0 - 6, gy0 + 2, "sin", size=13, color=GREY, anchor="end")

    amp = gh / 2 - 14
    # гладкий синус (орієнтир)
    smooth = [(gx0 + gw * t / 200.0, midy - amp * math.sin(2 * math.pi * t / 200.0))
              for t in range(201)]
    s += polyline(smooth, color=FAINT, w=2)

    # сходинки + точки-відліки
    step = gw / N
    prev = None
    for k in range(N + 1):
        kk = k % N
        v = math.sin(2 * math.pi * kk / N)
        x = gx0 + k * step
        y = midy - amp * v
        if prev is not None:
            # горизонтальна полиця тримається до наступного відліку (ZOH)
            s += line(prev[0], prev[1], x, prev[1], color=BLUE, w=2.4)
            s += line(x, prev[1], x, y, color=BLUE, w=2.4)
        prev = (x, y)
    for k in range(N):
        v = math.sin(2 * math.pi * k / N)
        x = gx0 + k * step
        y = midy - amp * v
        active = (k == k_active)
        s += circle(x, y, 4.5, fill=(ORANGE if active else BLUE),
                    stroke=(ORANGE if active else BLUE), w=1)
    s += text(gx0 + gw / 2, gy0 + gh + 26,
              "вихід ЦАП: значення з комірок, утримані сходинками",
              size=13, anchor="middle", color=BLUE)

    # активний відлік підсвічуємо до кола
    s += text(gx0 + 4, gy0 + gh + 46, "точка = один запис table[k]; гладка сіра — ідеал",
              size=11.5, color=GREY)

    # стрілка-зв'язок «коло → графік»
    s += arrow(cx + R + 30, cy - 70, gx0 - 14, gy0 + 30, color=GREY, w=1.6, dash="4,4")
    s += text((cx + R + gx0) / 2, cy - 92, "читаємо по колу", size=12, anchor="middle", color=GREY)

    s += footer()
    write("fig-7-1a-1-lut.svg", s)


# ──────────────────────────────────────────────────────────────────────────
# Рис. 1.7.1a.2 — Фазовий акумулятор: ФКС додається щотакту; старші біти індексують
# ──────────────────────────────────────────────────────────────────────────
def fig_accum():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 26, "Фазовий акумулятор: щотакту додаємо крок, старші біти індексують таблицю",
              size=15.5, anchor="middle", weight="bold")

    # --- верх: 32-бітний акумулятор як стрічка бітів, поділена на INDEX|FRACTION ---
    bx, by, bw, bh = 60, 64, 640, 46
    nbits = 32
    idx_bits = 8
    cellw = bw / nbits
    # фракційна частина (молодші) — світла; індексна (старші) — підсвічена
    s += rect(bx, by, cellw * idx_bits, bh, fill="#fdf0e2", stroke=ORANGE, sw=2)
    s += rect(bx + cellw * idx_bits, by, cellw * (nbits - idx_bits), bh,
              fill="#eef2fb", stroke=BLUE, sw=2)
    for i in range(1, nbits):
        col = ORANGE if i <= idx_bits else FAINT
        s += line(bx + cellw * i, by, bx + cellw * i, by + bh,
                  color=(ORANGE if i == idx_bits else FAINT), w=(2 if i == idx_bits else 1))
    s += text(bx + cellw * idx_bits / 2, by - 8, "INDEX (старші " + str(idx_bits) + " біт)",
              size=12.5, anchor="middle", color=ORANGE, weight="bold")
    s += text(bx + cellw * idx_bits + cellw * (nbits - idx_bits) / 2, by - 8,
              "FRACTION (молодші " + str(nbits - idx_bits) + " біт — відкидаємо)",
              size=12.5, anchor="middle", color=BLUE)
    s += text(bx - 8, by + bh / 2 + 5, "phase", size=13, anchor="end", weight="bold")
    s += text(bx, by + bh + 18, "MSB", size=11, color=GREY)
    s += text(bx + bw, by + bh + 18, "LSB", size=11, color=GREY, anchor="end")
    s += mono(bx + 6, by + bh - 14, "32-бітне беззнакове, переповнення = новий період (обгортка mod 2³²)",
              size=12, color=GREY)

    # стрілка «беремо старші біти як індекс»
    s += arrow(bx + cellw * idx_bits / 2, by + bh + 6, bx + cellw * idx_bits / 2, by + bh + 30,
               color=ORANGE, w=2)
    s += text(bx + cellw * idx_bits / 2 + 8, by + bh + 40,
              "index = phase >> 24   →   table[index]", size=13, color=ORANGE)

    # --- акумулятор: phase += tuning_word ---
    ay = 168
    s += rect(bx, ay, 250, 40, fill="#ffffff", stroke=INK, sw=2, rx=6)
    s += mono(bx + 12, ay + 26, "phase += step", size=16, weight="bold")
    s += text(bx + 125, ay - 8, "щотакту (на кожен відлік fₛ)", size=12.5, anchor="middle", color=GREY)
    s += arrow(bx + 260, ay + 20, bx + 320, ay + 20, color=INK, w=2)
    s += text(bx + 330, ay + 16, "крок step = ФКС (frequency control / tuning word)",
              size=13, color=INK)
    s += text(bx + 330, ay + 34, "fₒᵤₜ = step · fₛ / 2³²   (більший крок → вища частота)",
              size=13, color=PURPLE, weight="bold")

    # --- низ: дві швидкості обходу таблиці (малий крок vs великий) ---
    N = 16
    def ring(cx, cy, R, step_slots, color, title, sub):
        out = circle(cx, cy, R, fill="none", stroke=FAINT, w=10)
        for k in range(N):
            ang = -math.pi / 2 + 2 * math.pi * k / N
            x = cx + R * math.cos(ang)
            y = cy + R * math.sin(ang)
            out += circle(x, y, 4, fill="#ffffff", stroke=GREY, w=1.4)
        # стрибки вказівника
        pos = 0.0
        pts_idx = []
        for _ in range(7):
            pts_idx.append(int(round(pos)) % N)
            pos += step_slots
        for j, k in enumerate(pts_idx):
            ang = -math.pi / 2 + 2 * math.pi * k / N
            x = cx + R * math.cos(ang)
            y = cy + R * math.sin(ang)
            out += circle(x, y, 6, fill=color, stroke=color, w=1)
            out += text(x, y - 9, str(j), size=10, anchor="middle", color=color)
        out += text(cx, cy + 4, title, size=14, anchor="middle", color=color, weight="bold")
        out += text(cx, cy + R + 26, sub, size=12.5, anchor="middle", color=INK)
        return out

    s += ring(200, 320, 70, 1.0, GREEN, "малий крок", "повільний обхід → НИЗЬКА частота")
    s += ring(560, 320, 70, 3.0, RED, "великий крок", "пропускаємо точки → ВИСОКА частота")
    s += text(W / 2, 408, "Та сама таблиця, лише розмір кроку фази задає вихідну частоту (DDS).",
              size=12.5, anchor="middle", color=GREY)

    s += footer()
    write("fig-7-1a-2-accumulator.svg", s)


if __name__ == "__main__":
    fig_lut()
    fig_accum()
    print("OK ->", OUT)
