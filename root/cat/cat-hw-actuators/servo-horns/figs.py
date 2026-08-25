# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def splined_circle(cx, cy, r_out, r_in, teeth, color=INK, sw=1.6):
    """Коло з трикутними зубцями назовні — модель шліцьового валу/маточини."""
    pts = []
    n = teeth * 2  # вершина + западина на зуб
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d = "M %.2f %.2f " % pts[0] + " ".join("L %.2f %.2f" % p for p in pts[1:]) + " Z"
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (
        d, "#eef2f7", color, sw)


def fig_splines():
    """Три поширені шліци: 21T (мікро), 24T (Hitec), 25T (Futaba) — і як роги
    сідають лише на свій. viewBox широкий, підписи стоять із запасом."""
    W, H = 760, 430
    frags = []
    frags.append(text(W / 2, 30, "Шліци валів: рахуй зубці — сідає лише свій ріг", size=17, bold=True))

    cols = [
        (150, "21 зуб", "мікросерво", "SG90 · MG90S · FS90R", 21, "≈ 4.8 мм"),
        (380, "24 зуби", "Hitec", "багато стандартних Hitec", 24, "≈ 5.9 мм"),
        (610, "25 зубів", "Futaba", "Futaba · Tamiya · Traxxas", 25, "≈ 5.9 мм"),
    ]
    cy = 175
    for (cx, cnt, brand, who, teeth, dia) in cols:
        frags.append(splined_circle(cx, cy, 62, 50, teeth))
        frags.append(circle(cx, cy, 16, fill=BG, stroke=MUTED, sw=1.3))  # отвір під гвинт
        frags.append(text(cx, cy + 5, "гвинт", size=11, color=MUTED))
        frags.append(text(cx, cy + 92, cnt, size=16, bold=True, color=POS))
        frags.append(text(cx, cy + 112, brand, size=13, color=INK))
        b, bw, bh = textbox(cx, cy + 146, who, size=11, color=MUTED, pad=8, min_w=200)
        frags.append(b)
        frags.append(text(cx, cy + 176, dia, size=12, color=NEG))

    # нижній рядок-висновок
    b, bw, bh = textbox(W / 2, 405, "однакова кількість зубців у різних брендів — ще не гарантія: діаметр шліца різнить на десяті міліметра",
                        size=12, color=INK, pad=10, min_w=W - 60, fill="#fff7ed", stroke="#d9822b")
    frags.append(b)
    render(os.path.join(OUT, 'splines.svg'), W, H, *frags)


def horn_arm(cx, cy, length, holes, angle_deg, label):
    """Один промінь рога: заокруглена «кістка» з рядком отворів під тяги."""
    a = math.radians(angle_deg)
    out = []
    # тіло променя як товста лінія з круглими торцями
    x2 = cx + length * math.cos(a)
    y2 = cy + length * math.sin(a)
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="16" stroke-linecap="round"/>' % (cx, cy, x2, y2, "#cfd8e3"))
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="16" stroke-linecap="round" fill="none"/>' % (cx, cy, x2, y2, "#cfd8e3"))
    # обвід
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2" stroke-linecap="round"/>' % (cx, cy, x2, y2, LINE))
    # отвори вздовж
    for k in range(holes):
        t = 0.42 + 0.5 * (k / max(1, holes - 1)) if holes > 1 else 0.7
        hx = cx + length * t * math.cos(a)
        hy = cy + length * t * math.sin(a)
        out.append(circle(hx, hy, 4.2, fill=BG, stroke=LINE, sw=1.2))
    return "".join(out)


def fig_types():
    """Родина форм рогів: одинарний, подвійний, хрест, круглий диск —
    і що кожна форма дає. Кожна панель зі своїм центром, підписи не тісняться."""
    W, H = 760, 470
    frags = []
    frags.append(text(W / 2, 30, "Форми рогів: скільки й куди тягти", size=17, bold=True))

    hub_r = 15

    def hub(cx, cy):
        f = splined_circle(cx, cy, hub_r, hub_r * 0.78, 21, sw=1.2)
        f += circle(cx, cy, 5.5, fill=BG, stroke=MUTED, sw=1.1)
        return f

    # 1 — одинарний
    c1 = (150, 150)
    frags.append(horn_arm(c1[0], c1[1], 78, 4, 0, ""))
    frags.append(hub(*c1))
    frags.append(text(c1[0], 250, "одинарний", size=14, bold=True))
    b, _, _ = textbox(c1[0], 285, "одна тяга;\nмаксимальний хід", size=11, color=MUTED, pad=8, min_w=180)
    frags.append(b)

    # 2 — подвійний (пряме коромисло)
    c2 = (400, 150)
    frags.append(horn_arm(c2[0], c2[1], 70, 3, 0, ""))
    frags.append(horn_arm(c2[0], c2[1], 70, 3, 180, ""))
    frags.append(hub(*c2))
    frags.append(text(c2[0], 250, "подвійний (коромисло)", size=14, bold=True))
    b, _, _ = textbox(c2[0], 285, "тяга на два боки;\nсиметрична сила", size=11, color=MUTED, pad=8, min_w=210)
    frags.append(b)

    # 3 — хрест
    c3 = (640, 150)
    for ang in (0, 90, 180, 270):
        frags.append(horn_arm(c3[0], c3[1], 58, 2, ang, ""))
    frags.append(hub(*c3))
    frags.append(text(c3[0], 250, "хрест (чотири промені)", size=14, bold=True))
    b, _, _ = textbox(c3[0], 285, "багато точок,\nвибір радіуса", size=11, color=MUTED, pad=8, min_w=200)
    frags.append(b)

    # 4 — круглий диск
    c4 = (275, 355)
    frags.append(circle(c4[0], c4[1], 55, fill="#cfd8e3", stroke=LINE, sw=1.2))
    for k in range(8):
        a = 2 * math.pi * k / 8
        frags.append(circle(c4[0] + 44 * math.cos(a), c4[1] + 44 * math.sin(a), 4, fill=BG, stroke=LINE, sw=1.1))
    frags.append(hub(*c4))
    frags.append(text(c4[0], 435, "круглий диск (колесо)", size=14, bold=True))

    # 5 — пояснення радіуса
    c5 = (560, 355)
    frags.append(horn_arm(c5[0], c5[1], 88, 4, 0, ""))
    frags.append(hub(*c5))
    frags.append(line(c5[0], c5[1] + 26, c5[0] + 88 * 0.7, c5[1] + 26, color=FIELD, sw=1.4, dash="4 3"))
    frags.append(text(c5[0] + 30, c5[1] + 42, "далі отвір → більший хід,", size=11, color=FIELD, anchor="start"))
    frags.append(text(c5[0] + 30, c5[1] + 58, "менша сила", size=11, color=FIELD, anchor="start"))
    frags.append(text(c5[0] + 44, 435, "радіус вирішує", size=13, bold=True))

    render(os.path.join(OUT, 'horn-types.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_splines()
    fig_types()
    print("figs done")
