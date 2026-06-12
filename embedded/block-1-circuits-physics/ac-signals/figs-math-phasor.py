# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🧮-вставки до теми 1.7.3 — «Фазор: синусоїда як вектор».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами (fig-7-3m-*).
НЕ чіпає головний figs.py розділу. Хелпери скопійовано з нього (за §9 — самодостатність).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; sans-serif.
Нумерація підписів у тексті — Рис. 1.7.3m.k.
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
PURPLE = "#7a3aa0"
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
        f'  <marker id="aGrey" markerWidth="10" markerHeight="10" refX="7.5" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,3 L0,6 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         ORANGE: "aOrange", PURPLE: "aPurple", GREY: "aGrey"}


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


def circle(cx, cy, r, fill="none", stroke=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}/>\n')


def dot(cx, cy, r, fill=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def _arc(cx, cy, r, a0_deg, a1_deg, color=INK, w=2.0, dash=None, arrowed=True):
    """Дуга кута від a0 до a1 (кути математичні, в екранній системі y вниз — беремо -sin)."""
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    sx, sy = cx + r * math.cos(a0), cy - r * math.sin(a0)
    ex, ey = cx + r * math.cos(a1), cy - r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    # у екранній системі (y вниз) додатний мат. напрям -> sweep=0
    sweep = 0 if a1_deg > a0_deg else 1
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    end = f' marker-end="url(#{m})"' if arrowed else ""
    return (f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large} {sweep} {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{d}{end}/>\n')


def _sine_pts(x0, y0, width, amp, cycles=1.0, phase=0.0, n=200):
    """Синусоїда: вісь по y0, амплітуда amp вгору, width пікселів на cycles періодів, фаза phase (рад)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * width
        y = y0 - amp * math.sin(2 * math.pi * cycles * t + phase)
        pts.append((x, y))
    return pts


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.7.3m.1 — фазор: обертова стрілка ліворуч, її проєкція малює синус праворуч
# ════════════════════════════════════════════════════════════════════════════
def fig_phasor_to_sine():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 28, "Фазор — обертова стрілка; її вертикальна тінь і є синусоїда",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "Зліва — миттєвий «знімок» о моменті t: стрілка довжини Vₘ під кутом (ωt+φ). "
                         "Справа — слід тіні в часі.",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВА панель: коло з обертовим фазором ──
    cx, cy, R = 175, 245, 120
    s += circle(cx, cy, R, "none", FAINT, 2)
    # осі
    s += arrow(cx - R - 24, cy, cx + R + 30, cy, GREY, 1.5)   # горизонт (Re)
    s += arrow(cx, cy + R + 30, cx, cy - R - 30, GREY, 1.5)   # вертикаль (Im)
    s += text(cx + R + 34, cy + 16, "Re", 12.5, GREY, "start", style="italic")
    s += text(cx + 8, cy - R - 22, "Im", 12.5, GREY, "start", style="italic")

    # фазор під кутом θ = 52°
    th = math.radians(52)
    px, py = cx + R * math.cos(th), cy - R * math.sin(th)
    # проєкція на вертикаль (тінь)
    s += line(px, py, cx, py, BLUE, 1.6, "5 4")          # горизонтальна пунктирна до Im
    s += line(cx, cy, cx, py, BLUE, 3.2)                  # сама тінь (відрізок на Im)
    s += text(cx - 12, (cy + py) / 2 + 4, "Vₘ·sin(ωt+φ)", 12.5, BLUE, "end", "bold")
    # дуга кута
    s += _arc(cx, cy, 40, 0, 52, RED, 2.0)
    s += text(cx + 50, cy - 18, "ωt+φ", 13, RED, "start", "bold", "italic")
    # сам фазор
    s += arrow(cx, cy, px, py, INK, 3.4)
    s += text((cx + px) / 2 - 6, (cy + py) / 2 - 8, "Vₘ", 14, INK, "end", "bold", "italic")
    # точка на колі
    s += dot(px, py, 4.5, INK)
    # стрілка обертання
    s += _arc(cx, cy, R + 14, 70, 120, GREEN, 2.2)
    s += text(cx - 70, cy - R - 6, "ω", 14, GREEN, "middle", "bold", "italic")
    s += text(cx, cy + R + 56, "обертається з кутовою швидкістю ω", 11.5, GREEN, "middle")

    # ── ПРАВА панель: синусоїда — слід тіні ──
    ax, ay = 360, 245           # початок осі часу (на рівні центра кола)
    aw, amp = 470, 120
    s += line(ax, ay - amp - 18, ax, ay + amp + 18, GREY, 1.4)   # вісь v
    s += arrow(ax, ay, ax + aw + 26, ay, GREY, 1.5)              # вісь часу
    s += text(ax + aw + 30, ay + 16, "t", 13, GREY, "start", style="italic")
    s += text(ax - 8, ay - amp - 22, "v", 13, GREY, "end", style="italic")
    # рівні ±Vm
    s += line(ax, ay - amp, ax + aw, ay - amp, FAINT, 1.4, "4 4")
    s += line(ax, ay + amp, ax + aw, ay + amp, FAINT, 1.4, "4 4")
    s += text(ax - 6, ay - amp + 4, "+Vₘ", 11, RED, "end")
    s += text(ax - 6, ay + amp + 4, "−Vₘ", 11, BLUE, "end")

    # синусоїда зі стартовою фазою phi так, щоб лівий край = поточна тінь (52°)
    phi = math.radians(52)
    pts = _sine_pts(ax, ay, aw, amp, cycles=1.35, phase=phi)
    s += polyline(pts, INK, 3.0)

    # з'єднати тінь зліва з початком синуса (та сама висота)
    y_start = ay - amp * math.sin(phi)
    s += line(cx, py, ax, y_start, BLUE, 1.4, "3 4")
    s += dot(ax, y_start, 4.0, BLUE)
    s += text(ax + 6, y_start - 8, "поточна висота", 10.5, BLUE, "start")

    # позначка періоду T (один повний оберт = 2π)
    # один цикл = aw/1.35 пікселів
    px_per_cycle = aw / 1.35
    t0 = ax + 60
    s += arrow(t0, ay + amp + 36, t0 + px_per_cycle, ay + amp + 36, GREY, 1.5)
    s += arrow(t0 + px_per_cycle, ay + amp + 36, t0, ay + amp + 36, GREY, 1.5)
    s += line(t0, ay + amp + 26, t0, ay + amp + 46, GREY, 1.2)
    s += line(t0 + px_per_cycle, ay + amp + 26, t0 + px_per_cycle, ay + amp + 46, GREY, 1.2)
    s += text(t0 + px_per_cycle / 2, ay + amp + 60, "T  —  один повний оберт (2π)", 11.5, GREY, "middle")

    save("fig-7-3m-1-phasor-to-sine.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.7.3m.2 — зсув фаз = сталий кут між фазорами; додавання = векторна сума
# ════════════════════════════════════════════════════════════════════════════
def fig_phase_as_angle():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 28, "Зсув фаз — це сталий кут між стрілками; додати синуси = додати вектори",
              17.5, INK, "middle", "bold")
    s += text(W / 2, 50, "Обидва фазори обертаються разом, тож кут φ між ними застиглий — "
                         "тригонометрія коливань стає геометрією трикутника.",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВА панель: два фазори під сталим кутом ──
    cx, cy, R1, R2 = 200, 250, 120, 92
    s += circle(cx, cy, R1, "none", FAINT, 1.8)
    s += arrow(cx - R1 - 22, cy, cx + R1 + 26, cy, GREY, 1.5)
    s += arrow(cx, cy + R1 + 26, cx, cy - R1 - 26, GREY, 1.5)
    s += text(cx + R1 + 30, cy + 16, "Re", 12, GREY, "start", style="italic")
    s += text(cx + 8, cy - R1 - 18, "Im", 12, GREY, "start", style="italic")

    a1 = math.radians(58)     # фазор A (випереджає)
    a2 = math.radians(20)     # фазор B (відстає) — різниця 38°
    ax1, ay1 = cx + R1 * math.cos(a1), cy - R1 * math.sin(a1)
    bx1, by1 = cx + R2 * math.cos(a2), cy - R2 * math.sin(a2)
    s += arrow(cx, cy, ax1, ay1, RED, 3.4)
    s += arrow(cx, cy, bx1, by1, BLUE, 3.4)
    s += text(ax1 + 6, ay1 - 6, "A", 14, RED, "start", "bold", "italic")
    s += text(bx1 + 8, by1 + 4, "B", 14, BLUE, "start", "bold", "italic")
    # кут φ між ними
    s += _arc(cx, cy, 56, 20, 58, PURPLE, 2.2)
    s += text(cx + 70, cy - 30, "φ", 15, PURPLE, "start", "bold", "italic")
    # спільне обертання
    s += _arc(cx, cy, R1 + 12, 80, 120, GREEN, 2.0)
    s += text(cx - 64, cy - R1 - 2, "ω (разом)", 11.5, GREEN, "middle", "bold")
    s += text(cx, cy + R1 + 50, "кут φ між A і B не міняється з часом", 11.5, INK, "middle")

    # ── ПРАВА панель: дві синусоїди зі зсувом φ + їхня сума ──
    ax, ay = 480, 235
    aw, amp = 380, 78
    s += line(ax, ay - amp - 60, ax, ay + amp + 18, GREY, 1.4)
    s += arrow(ax, ay, ax + aw + 24, ay, GREY, 1.5)
    s += text(ax + aw + 28, ay + 15, "t", 13, GREY, "start", style="italic")
    s += text(ax - 8, ay - amp - 56, "v", 13, GREY, "end", style="italic")

    phi = a1 - a2   # 38° зсув
    ptsA = _sine_pts(ax, ay, aw, amp, cycles=1.6, phase=a1)
    ptsB = _sine_pts(ax, ay, aw, amp * (R2 / R1), cycles=1.6, phase=a2)
    s += polyline(ptsA, RED, 2.6)
    s += polyline(ptsB, BLUE, 2.6)
    # сума (фазор C = A + B): амплітуда й фаза з векторної суми
    Ax, Ay = R1 * math.cos(a1), R1 * math.sin(a1)
    Bx, By = R2 * math.cos(a2), R2 * math.sin(a2)
    Cx, Cy = Ax + Bx, Ay + By
    Camp = math.hypot(Cx, Cy)
    Cphase = math.atan2(Cy, Cx)
    ptsC = _sine_pts(ax, ay, aw, amp * (Camp / R1), cycles=1.6, phase=Cphase)
    s += polyline(ptsC, GREEN, 3.0)

    s += text(ax + aw + 2, ptsA[-1][1] + 2, "A", 12, RED, "start", "bold", "italic")
    s += text(ax + aw + 2, ptsB[-1][1] + 14, "B", 12, BLUE, "start", "bold", "italic")
    s += text(ax + 8, ay - amp - 40, "A + B  (сума — знову синус)", 12, GREEN, "start", "bold")

    # ── мала вставка: векторний трикутник A+B=C ──
    tx, ty = 560, 360
    sc = 0.42
    s += text(tx + 40, ty - 70, "векторна сума:", 11.5, INK, "middle", "bold")
    ox, oy = tx, ty
    s += arrow(ox, oy, ox + Ax * sc, oy - Ay * sc, RED, 2.6)
    s += arrow(ox + Ax * sc, oy - Ay * sc, ox + Cx * sc, oy - Cy * sc, BLUE, 2.6)
    s += arrow(ox, oy, ox + Cx * sc, oy - Cy * sc, GREEN, 3.0)
    s += text(ox + Cx * sc + 8, oy - Cy * sc - 2, "C", 13, GREEN, "start", "bold", "italic")
    s += text(ox + Ax * sc * 0.5 - 6, oy - Ay * sc * 0.5 - 4, "A", 11.5, RED, "end", "bold", "italic")

    save("fig-7-3m-2-phase-as-angle.svg", s)


if __name__ == "__main__":
    fig_phasor_to_sine()
    fig_phase_as_angle()
    print("done")
