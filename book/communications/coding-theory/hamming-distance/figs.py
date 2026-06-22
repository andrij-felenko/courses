# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── cube: відстань Геммінга як кількість ребер на кубі 3-бітних слів ───────────
# Ідея: усі 3-бітні слова — вершини куба, ребро з'єднує слова на відстані 1.
# Геммінгова відстань = найменше число ребер між вершинами; праворуч — правило
# коду (за мінімальною d скільки помилок видно й скільки виправно).

def fig_cube():
    W, H = 880, 520
    p = []

    # вершини куба у проєкції: (мітка) → (x, y)
    front = {
        "000": (205, 340), "100": (325, 340),
        "110": (325, 220), "010": (205, 220),
    }
    back = {
        "001": (275, 380), "101": (395, 380),
        "111": (395, 260), "011": (275, 260),
    }
    pos = {}
    pos.update(front)
    pos.update(back)

    # ребра = пари слів, що різняться рівно одним бітом
    def diff1(a, b):
        return sum(1 for i in range(3) if a[i] != b[i]) == 1
    words = list(pos.keys())
    edges = []
    seen = set()
    for a in words:
        for b in words:
            if a != b and diff1(a, b) and (b, a) not in seen:
                seen.add((a, b))
                edges.append((a, b))

    # усі ребра — тонкі сірі
    for a, b in edges:
        ax, ay = pos[a]; bx, by = pos[b]
        p.append(line(ax, ay, bx, by, color="#e4e4e4", sw=2))

    # шлях 000 → 010 → 011 (червоний) показує d(000,011)=2
    path = ["000", "010", "011"]
    for i in range(len(path) - 1):
        ax, ay = pos[path[i]]; bx, by = pos[path[i + 1]]
        p.append(line(ax, ay, bx, by, color=POS, sw=3))

    # вершини: два кінці шляху червоні, решта чорні
    ends = {"000", "011"}
    for w, (x, y) in pos.items():
        col = POS if w in ends else INK
        sw = 2.4 if w in ends else 1.6
        p.append(circle(x, y, 17, fill="#fff", stroke=col, sw=sw))
        p.append(text(x, y + 5, w, size=12, color=col, bold=True))

    p.append(text(300, 500, "d(000, 011) = 2  (два ребра)", size=15, color=POS, bold=True))

    # права картка — правило коду (textbox самі підганяються під текст)
    bx, by, bw, bh = 600, 110, 250, 330
    p.append(rect(bx, by, bw, bh, fill="#fbfbfb", stroke="#e4e4e4", sw=1.4, rx=10))
    cx = bx + bw / 2
    p.append(text(cx, by + 28, "Правило коду", size=15, color=INK, bold=True))
    p.append(mtext(bx + 16, by + 62,
                   ["d — мінімальна відстань", "між БУДЬ-ЯКИМИ двома",
                    "дозволеними словами коду."],
                   size=12, color=INK, anchor="start", lh=1.35))
    p.append(line(bx + 16, by + 114, bx + bw - 16, by + 114, color="#e4e4e4", sw=1.2))
    p.append(text(bx + 16, by + 140, "виявити помилок:", size=12.5, color=FIELD, anchor="start", bold=True))
    p.append(text(bx + 16, by + 162, "до  d − 1", size=16, color=FIELD, anchor="start", bold=True))
    p.append(text(bx + 16, by + 196, "виправити помилок:", size=12.5, color=POS, anchor="start", bold=True))
    p.append(text(bx + 16, by + 218, "до  ⌊(d − 1) / 2⌋", size=16, color=POS, anchor="start", bold=True))
    p.append(line(bx + 16, by + 238, bx + bw - 16, by + 238, color="#e4e4e4", sw=1.2))
    p.append(mtext(bx + 16, by + 262,
                   ["Більша відстань —", "більше зайвих бітів,", "але й більша стійкість."],
                   size=12, color=MUTED, anchor="start", lh=1.45))

    render(os.path.join(OUT, "cube.svg"), W, H, *p,
           title="Відстань Геммінга = скільки бітів різнить два слова = скільки кроків по кубу")


# ── spheres: кулі навколо кодових слів — виявлення проти виправлення ───────────
# Ідея: навколо кожного кодового слова — куля радіуса t=⌊(d−1)/2⌋. Поки помилок
# ≤ t, точка лишається у своїй кулі (виправляємо); до d−1 — поза кулею, але не в
# чужій (виявляємо); ≥ d — можна впасти в чужу кулю (тиха помилка).

def fig_spheres():
    W, H = 880, 450
    p = []

    ay = 230
    ax, bx = 270, 610
    R = 70

    # пунктир «відстань d» між центрами
    p.append(line(ax, ay, bx, ay, color="#e4e4e4", sw=2, dash="6 5"))
    p.append(text((ax + bx) / 2, 150, "відстань d між словами", size=12.5, color=MUTED, italic=True))

    # дві кулі
    for cx in (ax, bx):
        p.append(circle(cx, ay, R, fill="#eef7ef", stroke=FIELD, sw=1.6))
    # центри-кодові слова
    p.append(circle(ax, ay, 15, fill="#fff", stroke=NEG, sw=2.6))
    p.append(text(ax, ay + 5, "A", size=14, color=NEG, bold=True))
    p.append(circle(bx, ay, 15, fill="#fff", stroke=NEG, sw=2.6))
    p.append(text(bx, ay + 5, "B", size=14, color=NEG, bold=True))
    p.append(text(ax, ay + R + 22, "куля A: радіус t", size=11.5, color=FIELD))
    p.append(text(bx, ay + R + 22, "куля B: радіус t", size=11.5, color=FIELD))

    # прийняте з помилкою — у межах кулі A
    ex, ey = 308, 202
    p.append(circle(ex, ey, 8, fill=POS, stroke=POS, sw=0))
    p.append(text(ex + 12, ey - 6, "прийнято з помилкою", size=11, color=POS, anchor="start", bold=True))
    p.append(line(ex, ey, 283, 220, color=POS, sw=1.8, dash="4 3"))
    p.append(text(300, 270, "ближче до A → вертаємо в A ✓", size=11, color=POS))

    # три рядки-висновки внизу
    y0 = 344
    p.append(line(60, y0, 820, y0, color="#e4e4e4", sw=1.4))
    p.append(text(60, y0 + 20, "Якщо помилок ≤ t = ⌊(d−1)/2⌋ — точка ще у «своїй» кулі → виправимо однозначно.",
                  size=13, color=FIELD, anchor="start", bold=True))
    p.append(text(60, y0 + 42, "Якщо помилок до d−1 — точка вийшла зі своєї кулі, але не дійшла чужої → бачимо, що щось не так.",
                  size=13, color="#caa24a", anchor="start"))
    p.append(text(60, y0 + 64, "Якщо помилок ≥ d — могли впасти в ЧУЖУ кулю → приймемо хибне слово за правильне (тиха помилка).",
                  size=13, color=POS, anchor="start"))

    render(os.path.join(OUT, "spheres.svg"), W, H, *p,
           title="Дозволені слова — острівці, помилка зсуває нас від берега")


if __name__ == "__main__":
    fig_cube()
    fig_spheres()
    print("OK: figures written to", OUT)
