# -*- coding: utf-8 -*-
"""Фігури для вставки proj-cooperative-scheduler.md (тема «Межі super-loop»).
Окремий генератор, щоб не чіпати наявний figs.py теми. Вивід — ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Круговий диспетчер: кроки добровільно повертають керування ────────────
def fig_roundrobin():
    W, H = 720, 320
    cx, cy, R = 360, 180, 96
    frags = []
    frags.append(text(W / 2, 26, "Круговий диспетчер: кожен крок сам віддає чергу", size=16, bold=True))

    # центральне коло-диспетчер
    frags.append(circle(cx, cy, 44, fill="#eef6ee", stroke=FIELD, sw=2))
    frags.append(mtext(cx, cy - 4, ["диспетчер", "for(;;) крок()"], size=12, bold=True))

    # три кроки по колу
    import math
    labels = [("blink", "перемкнув —\nвихід"),
              ("sensor", "зняв —\nвихід"),
              ("uart", "нема байта —\nвихід")]
    for i, (name, note) in enumerate(labels):
        ang = -math.pi / 2 + i * 2 * math.pi / 3
        bx = cx + R * math.cos(ang)
        by = cy + R * math.sin(ang)
        body, bw, bh = textbox(bx, by, name + "()", size=13, bold=True,
                               fill=FILL, stroke=LINE, min_w=92)
        frags.append(body)
        # стрілка від диспетчера до кроку і назад
        frags.append(arrow(cx + 40 * math.cos(ang), cy + 40 * math.sin(ang),
                           bx - (bw / 2 + 4) * math.cos(ang),
                           by - (bh / 2 + 4) * math.sin(ang), color=FIELD, sw=1.8))
        # підпис «повернув керування»
        nx = bx + (0 if abs(math.cos(ang)) < 0.2 else (70 if math.cos(ang) > 0 else -70))
        ny = by + (52 if math.sin(ang) > 0.2 else -40)
        frags.append(mtext(nx, ny, note.split("\n"), size=10, color=MUTED))

    frags.append(text(W / 2, H - 14,
                      "жоден крок не блокує: зробив своє — return; наступного оберту продовжить далі",
                      size=11, color=MUTED))
    render(os.path.join(IMG, "pt-roundrobin.svg"), W, H, *frags)


# ── 2. Як протопотік відновлюється: switch стрибає за останню паузу ──────────
def fig_resume():
    W, H = 720, 360
    frags = []
    frags.append(text(W / 2, 26, "Протопотік: switch стрибає рівно туди, де ми спинилися", size=16, bold=True))

    # ліворуч — лінійний код, який БАЧИТЬ програміст
    lx, ly, lw = 40, 56, 300
    frags.append(fitbox(lx, ly, lw, 250,
                        "PT_BEGIN\n\n  LED = 1;\n  WAIT 500 мс   ← пауза A\n\n  LED = 0;\n  WAIT 500 мс   ← пауза B\n\nPT_END",
                        size=13, fill="#eef6ee", stroke=FIELD))
    frags.append(text(lx + lw / 2, ly + 268, "як пишемо: згори вниз", size=11, color=MUTED))

    # праворуч — що робить switch щооберту
    rx, ry, rw = 400, 56, 280
    frags.append(fitbox(rx, ry, rw, 250,
                        "switch (pt.line) {\n case 0:      → старт\n case A: goto після A\n case B: goto після B\n}",
                        size=13, fill=FILL, stroke=LINE))
    frags.append(text(rx + rw / 2, ry + 268, "як виконує: стрибок за станом", size=11, color=MUTED))

    # стрілки відповідності пауз
    frags.append(arrow(lx + lw, ly + 96, rx, ry + 70, color=POS, sw=1.6))
    frags.append(arrow(lx + lw, ly + 150, rx, ry + 110, color=POS, sw=1.6))
    frags.append(text((lx + lw + rx) / 2, ly + 30, "pt.line = __LINE__", size=10, color=POS))

    frags.append(text(W / 2, H - 12,
                      "перед кожною паузою запам'ятали рядок; наступний вхід — switch по ньому — і ми одразу за паузою",
                      size=11, color=MUTED))
    render(os.path.join(IMG, "pt-resume.svg"), W, H, *frags)


# ── 3. Межа stackless: локальні зникають на паузі ────────────────────────────
def fig_stackless():
    W, H = 720, 300
    frags = []
    frags.append(text(W / 2, 26, "Межа stackless: локальні не переживають паузу", size=16, bold=True))

    # до паузи — стек із локальними
    bx, by, bw, bh = 60, 70, 240, 150
    frags.append(rect(bx, by, bw, bh, fill=FILL, stroke=LINE))
    frags.append(text(bx + bw / 2, by - 8, "перед WAIT: кадр стека живий", size=11, color=MUTED))
    frags.append(fitbox(bx + 18, by + 20, bw - 36, 34, "int sum = 0;", size=13, fill="#eef6ee", stroke=FIELD))
    frags.append(fitbox(bx + 18, by + 62, bw - 36, 34, "int i = 3;", size=13, fill="#eef6ee", stroke=FIELD))
    frags.append(fitbox(bx + 18, by + 104, bw - 36, 32, "адреса повернення", size=12, fill=FILL, stroke=MUTED))

    # стрілка «WAIT → return»
    frags.append(arrow(bx + bw + 8, by + bh / 2, bx + bw + 120, by + bh / 2, color=POS, sw=2))
    frags.append(mtext(bx + bw + 64, by + bh / 2 - 14, ["WAIT →", "return"], size=12, color=POS, bold=True))

    # після повернення — кадр здутий, локальні стерті
    ax = bx + bw + 132
    frags.append(rect(ax, by + 48, bw, bh - 96, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(text(ax + bw / 2, by - 8 + 48, "після return: кадр здувся", size=11, color=MUTED))
    frags.append(text(ax + bw / 2, by + bh / 2 + 6, "sum, i — ЗНИКЛИ", size=14, color=POS, bold=True))

    frags.append(text(W / 2, H - 14,
                      "переживає лише те, що поза кадром: static або поле структури-протопотоку",
                      size=11, color=MUTED))
    render(os.path.join(IMG, "pt-stackless.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_roundrobin()
    fig_resume()
    fig_stackless()
    print("OK: pt-roundrobin.svg, pt-resume.svg, pt-stackless.svg")
