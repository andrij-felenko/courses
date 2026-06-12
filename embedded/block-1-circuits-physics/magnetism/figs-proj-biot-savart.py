# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для ⚙️-вставки до теми 1.8.4 —
«Поле довільного контуру чисельно: складаємо внески за Біо—Саваром».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами (fig-r08-4a-*).
НЕ чіпає головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Нумерація підписів у тексті — Рис. 1.8.4a.k.
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


def dot(cx, cy, r, fill=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.8.4a.1 — внесок одного відрізка dL у точці P: Біо—Савар
# ════════════════════════════════════════════════════════════════════════════
def fig_segment():
    W, H = 940, 480
    s = header(W, H)
    s += text(W / 2, 30, "Внесок одного відрізка дроту за Біо—Саваром",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "контур ріжемо на маленькі шматочки dL; кожен дає крихітне поле dB у точці P — їх потім складемо",
              11, GREY, "middle", style="italic")

    # ── ліва половина: геометрія dB ──
    # контур — частина петлі (дуга), на ній виділений відрізок dL
    cx, cy, R = 250, 300, 150
    # дуга контуру (від ~200° до ~340°, нижня частина кола)
    arc = []
    for k in range(61):
        a = math.radians(150 + k * (260 - 150) / 60)
        arc.append((cx + R * math.cos(a), cy - R * 0.62 * math.sin(a)))
    s += polyline(arc, RED, 2.6)
    s += text(arc[2][0] - 6, arc[2][1] + 18, "контур зі струмом I", 11.5, RED, "start", "bold")

    # стрілки напрямку струму вздовж дуги
    for idx in (12, 30, 48):
        x1, y1 = arc[idx - 1]
        x2, y2 = arc[idx + 1]
        s += arrow(x1, y1, x2 + (x2 - x1) * 0.1, y2 + (y2 - y1) * 0.1, RED, 2.2)

    # виділений відрізок dL (короткий шматок дуги біля idx≈30)
    sa = arc[28]
    sb = arc[33]
    s += line(sa[0], sa[1], sb[0], sb[1], INK, 6)
    s += arrow(sa[0], sa[1], sb[0], sb[1], INK, 3)
    s += text((sa[0] + sb[0]) / 2 - 6, (sa[1] + sb[1]) / 2 + 22, "dL", 14, INK, "middle", "bold", "italic")
    s += text((sa[0] + sb[0]) / 2 - 6, (sa[1] + sb[1]) / 2 + 38, "(напрям = напрям струму)", 9, GREY, "middle")

    # точка P, де рахуємо поле
    Px, Py = 470, 175
    s += dot(Px, Py, 4.5, PURPLE)
    s += text(Px + 8, Py - 4, "P", 14, PURPLE, "start", "bold", "italic")
    s += text(Px + 8, Py + 12, "де шукаємо B", 9.5, PURPLE, "start")

    # вектор r від середини dL до P
    mx, my = (sa[0] + sb[0]) / 2, (sa[1] + sb[1]) / 2
    s += arrow(mx, my, Px, Py, BLUE, 2.2)
    s += text((mx + Px) / 2 + 6, (my + Py) / 2 - 6, "r", 14, BLUE, "start", "bold", "italic")
    rlen = math.hypot(Px - mx, Py - my)
    s += text((mx + Px) / 2 + 6, (my + Py) / 2 + 10, "відстань r", 9.5, BLUE, "start")

    # dB у точці P — перпендикулярний до площини (тут показуємо «з площини», кружком з крапкою)
    # позначка «поле виходить із площини» біля P: коло з крапкою
    s += circle(Px + 44, Py - 30, 11, "#eef7f0", GREEN, 2)
    s += dot(Px + 44, Py - 30, 2.6, GREEN)
    s += text(Px + 60, Py - 26, "dB", 13, GREEN, "start", "bold", "italic")
    s += text(Px + 44, Py - 48, "⊥ площині (dL × r)", 9.5, GREEN, "middle")

    # ── права половина: формула й розклад ──
    bx = 560
    s += rect(bx, 92, 360, 150, "#fbfbff", GREEN, 1.7, 12)
    s += text(bx + 180, 118, "Закон Біо—Савара (Biot–Savart)", 13, GREEN, "middle", "bold")
    s += text(bx + 180, 158, "dB = (μ₀ / 4π) · I · (dL × r̂) / r²", 16, INK, "middle", "bold", "italic")
    s += text(bx + 180, 188, "μ₀ = 4π·10⁻⁷  (магнітна стала)", 11, GREY, "middle")
    s += text(bx + 180, 210, "r̂ — одиничний вектор уздовж r,  r̂ = r / r", 10.5, GREY, "middle")
    s += text(bx + 180, 230, "× — векторний добуток (задає напрям і правило правої руки)", 9.5, PURPLE, "middle")

    s += rect(bx, 258, 360, 188, "#fff8f0", ORANGE, 1.6, 12)
    s += text(bx + 180, 284, "Три множники — три ідеї", 12.5, ORANGE, "middle", "bold")
    s += text(bx + 16, 312, "• I · dL — «скільки струму та як довго»:", 11, INK, "start")
    s += text(bx + 34, 330, "довший шматок чи більший струм — більше dB", 9.5, GREY, "start")
    s += text(bx + 16, 356, "• 1 / r² — спад із відстанню (як у §1.1.3):", 11, INK, "start")
    s += text(bx + 34, 374, "далекий шматок дає мізерний внесок", 9.5, GREY, "start")
    s += text(bx + 16, 400, "• dL × r̂ — напрям:", 11, INK, "start")
    s += text(bx + 34, 418, "dB ⊥ і до dL, і до r; найбільше, коли r ⊥ dL,", 9.5, GREY, "start")
    s += text(bx + 34, 433, "нуль — коли P лежить уздовж самого dL", 9.5, GREY, "start")
    save("fig-r08-4a-1-segment.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.8.4a.2 — складаємо внески: сума dB по всьому контуру = B(P)
# ════════════════════════════════════════════════════════════════════════════
def fig_sum():
    W, H = 940, 500
    s = header(W, H)
    s += text(W / 2, 30, "Складаємо внески всіх відрізків — дістаємо повне поле B",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "суперпозиція: B(P) = Σ dB по всіх шматочках контуру (та сама ідея, що й для E-поля в §1.1.3)",
              11, GREY, "middle", style="italic")

    # ── ліва половина: прямокутна петля, розбита на відрізки, поле в P (центр) ──
    # прямокутник
    L, T, Rr, Bm = 70, 120, 360, 360
    # розіб'ємо периметр на N точок
    N = 40
    perim = []
    # йдемо за годинниковою: верх→право→низ→ліво
    seg = []
    top = [(L + (Rr - L) * i / 10, T) for i in range(11)]
    rgt = [(Rr, T + (Bm - T) * i / 10) for i in range(11)]
    bot = [(Rr - (Rr - L) * i / 10, Bm) for i in range(11)]
    lft = [(L, Bm - (Bm - T) * i / 10) for i in range(11)]
    nodes = top + rgt[1:] + bot[1:] + lft[1:]
    s += polygon(nodes, "none", RED, 2.6)

    # вузли-точки (центри відрізків) + напрямок струму
    for i in range(0, len(nodes) - 1, 2):
        x1, y1 = nodes[i]
        s += dot(x1, y1, 2.6, RED)
    # стрілки струму на кожній стороні
    s += arrow((L + Rr) / 2 - 16, T, (L + Rr) / 2 + 20, T, RED, 2.2)
    s += arrow(Rr, (T + Bm) / 2 - 16, Rr, (T + Bm) / 2 + 20, RED, 2.2)
    s += arrow((L + Rr) / 2 + 16, Bm, (L + Rr) / 2 - 20, Bm, RED, 2.2)
    s += arrow(L, (T + Bm) / 2 + 16, L, (T + Bm) / 2 - 20, RED, 2.2)
    s += text((L + Rr) / 2, T - 12, "контур зі струмом I, розбитий на відрізки", 11, RED, "middle", "bold")

    # точка P у центрі
    Px, Py = (L + Rr) / 2, (T + Bm) / 2
    s += dot(Px, Py, 4.5, PURPLE)
    s += text(Px + 8, Py + 18, "P", 14, PURPLE, "start", "bold", "italic")

    # тонкі промені r від кількох вузлів до P + крихітні dB-стрілки (всі «з площини» — кружки)
    sample = [0, 5, 10, 15, 20, 25, 30, 35]
    for idx in sample:
        x1, y1 = nodes[idx]
        s += line(x1, y1, Px, Py, BLUE, 1.1, "3,3")
    # сумарне поле в P: «виходить із площини» (велике зелене коло з крапкою)
    s += circle(Px, Py, 14, "#eef7f0", GREEN, 2.4)
    s += dot(Px, Py, 3.2, GREEN)
    s += text(Px + 22, Py - 6, "B = Σ dB", 13, GREEN, "start", "bold", "italic")
    s += text(Px + 22, Py + 10, "(виходить із площини)", 9.5, GREEN, "start")

    s += text((L + Rr) / 2, Bm + 26, "кожен відрізок шле свій крихітний dB у P;",
              10.5, INK, "middle")
    s += text((L + Rr) / 2, Bm + 42, "векторна сума всіх — повне поле B у цій точці",
              10.5, INK, "middle")

    # ── права половина: збіжність — точність росте з числом відрізків ──
    gx, gy = 540, 120
    gw, gh = 360, 250
    s += rect(gx, gy, gw, gh, "#ffffff", GREY, 1.4, 8)
    s += text(gx + gw / 2, gy - 10, "Збіжність: більше відрізків — точніше",
              12.5, INK, "middle", "bold")
    # осі
    s += arrow(gx + 40, gy + gh - 30, gx + gw - 16, gy + gh - 30, INK, 1.8)  # X
    s += arrow(gx + 40, gy + gh - 30, gx + 40, gy + 24, INK, 1.8)            # Y
    s += text(gx + gw - 16, gy + gh - 10, "N відрізків", 10, GREY, "end")
    s += text(gx + 8, gy + 36, "похибка", 10, GREY, "start")

    # крива похибки ~ 1/N (спадає до нуля)
    pts = []
    x0, y0 = gx + 40, gy + gh - 30
    for i in range(1, 51):
        N = i
        err = 1.0 / N
        xx = x0 + (gw - 70) * (i / 50)
        yy = y0 - (gh - 70) * err
        pts.append((xx, yy))
    s += polyline(pts, PURPLE, 2.6)
    # точкові маркери для кількох N
    for Ni, lbl in [(4, "N=4"), (8, "N=8"), (16, "N=16"), (40, "N=40")]:
        xx = x0 + (gw - 70) * (Ni / 50)
        yy = y0 - (gh - 70) * (1.0 / Ni)
        s += dot(xx, yy, 3.2, PURPLE)
        s += text(xx, yy - 8, lbl, 9, PURPLE, "middle", "bold")
    s += line(x0, y0 - 4, gx + gw - 30, y0 - 4, GREEN, 1.6, "5,4")
    s += text(gx + gw - 30, y0 - 8, "точне значення", 9, GREEN, "end", "bold")

    # підпис-висновок під графіком
    s += rect(gx, gy + gh + 14, gw, 70, "#fbfbff", BLUE, 1.5, 10)
    s += text(gx + gw / 2, gy + gh + 38, "Грубий контур (мало відрізків) — груба відповідь.",
              10.5, INK, "middle")
    s += text(gx + gw / 2, gy + gh + 56, "Дрібніше ріжемо — ближче до істини, але довше рахуємо.",
              10.5, INK, "middle")
    s += text(gx + gw / 2, gy + gh + 74, "Класичний компроміс точність ↔ час.",
              10.5, BLUE, "middle", "bold")
    save("fig-r08-4a-2-sum.svg", s)


if __name__ == "__main__":
    fig_segment()
    fig_sum()
    print("OK")
