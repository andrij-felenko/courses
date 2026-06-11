# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §1.8.6m — «Петля B–H кількісно: площа петлі = втрати за цикл».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена fig-8-6m-*).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація підписів: Рис. 1.8.6m.k.
НЕ чіпає головний figs.py розділу.
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey", PURPLE: "aPurple"}


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


def circle(cx, cy, r, fill=INK, stroke="none", sw=0):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>\n')


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, color=INK, w=2.4, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
#  Модель петлі B–H (безрозмірна, лише для рисунків — НЕ фізично точна крива,
#  але якісно правильна: насичення, залишок Br, коерцитивна сила Hc, опуклість).
#  Будуємо параметрично двома вітками за H(t) = sin.
# ─────────────────────────────────────────────────────────────────────────────
def _loop_points(Hmax=1.0, Bsat=1.0, Hc=0.30, n=200):
    """Повертає (verkhnia, nyzhnia) — два списки (H, B) для верхньої й нижньої віток."""
    upper = []  # йде зліва направо (H зростає): нижня крива насправді
    lower = []
    # верхня вітка: B(H) при зростанні H — зсунута вліво на Hc tanh
    for i in range(n + 1):
        H = -Hmax + 2 * Hmax * i / n
        Bup = Bsat * math.tanh((H + Hc) * 2.2)   # вітка при зростанні H
        Bdn = Bsat * math.tanh((H - Hc) * 2.2)   # вітка при спаданні H
        upper.append((H, Bup))
        lower.append((H, Bdn))
    return upper, lower


def fig_loop_area():
    """Рис. 1.8.6m.1 — петля B–H, заштрихована площа = втрати; Br, Hc, насичення."""
    W, H = 760, 560
    s = header(W, H)
    s += text(W / 2, 30, "Площа всередині петлі B–H = енергія втрат за один цикл",
              17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "Кожен оберт по петлі лишає на осерді тепло пропорційно затемненій площі",
              11.5, GREY, "middle", style="italic")

    # координати: центр осей
    cx, cy = W / 2, 300
    sx = 200   # px на одиницю H
    sy = 165   # px на одиницю B
    Hmax, Bsat = 1.25, 1.0

    def X(Hv):
        return cx + sx * Hv

    def Y(Bv):
        return cy - sy * Bv

    # сітка осей
    s += line(cx - sx * Hmax - 20, cy, cx + sx * Hmax + 20, cy, GREY, 1.2)   # вісь H
    s += line(cx, cy - sy * 1.35, cx, cy + sy * 1.35, GREY, 1.2)             # вісь B
    s += arrow(cx + sx * Hmax + 5, cy, cx + sx * Hmax + 35, cy, GREY, 1.6)
    s += arrow(cx, cy - sy * 1.30, cx, cy - sy * 1.50, GREY, 1.6)
    s += text(cx + sx * Hmax + 40, cy + 5, "H", 16, GREY, "start", "bold", "italic")
    s += text(cx + sx * Hmax + 40, cy + 22, "(А/м)", 10.5, GREY, "start")
    s += text(cx + 10, cy - sy * 1.50, "B", 16, GREY, "start", "bold", "italic")
    s += text(cx + 10, cy - sy * 1.50 + 17, "(Тл)", 10.5, GREY, "start")
    s += text(cx - 8, cy + 18, "0", 12, GREY, "end")

    upper, lower = _loop_points(Hmax=Hmax * 0.85, Bsat=Bsat, Hc=0.32, n=200)

    # заливка площі петлі: контур = верхня вітка зліва→направо, далі нижня направо→зліва
    poly = []
    for Hv, Bv in lower:           # B при зростанні H (нижня з двох на лівому боці)
        poly.append((X(Hv), Y(Bv)))
    for Hv, Bv in reversed(upper):  # B при спаданні H
        poly.append((X(Hv), Y(Bv)))
    s += polygon(poly, "#fbe3df")   # світло-червона заливка площі

    # дві вітки петлі
    s += polyline([(X(h), Y(b)) for h, b in lower], RED, 3.0)
    s += polyline([(X(h), Y(b)) for h, b in upper], RED, 3.0)

    # стрілки напрямку обходу петлі (за годинниковою стрілкою у звичних осях):
    # верхня вітка (спадання H) йде справа наліво у верхній частині графіка
    s += arrow(X(-0.05), Y(0.62), X(-0.30), Y(0.40), RED, 2.4)
    # нижня вітка (зростання H) йде зліва направо у нижній частині
    s += arrow(X(0.05), Y(-0.62), X(0.30), Y(-0.40), RED, 2.4)

    # ── характерні точки ──
    # насичення Bs
    Bs = Bsat * math.tanh((Hmax * 0.85 - 0.32) * 2.2)
    s += line(cx, Y(Bs), X(Hmax * 0.85), Y(Bs), BLUE, 1.2, "4,3")
    s += text(cx - 8, Y(Bs) - 4, "Bₛ", 13, BLUE, "end", "bold")
    s += text(cx - 8, Y(Bs) + 12, "насичення", 9.5, BLUE, "end")

    # залишкова індукція Br (H=0 на верхній вітці — точка перетину з віссю B)
    Br = Bsat * math.tanh((0 + 0.32) * 2.2)
    s += circle(X(0), Y(Br), 4.5, GREEN)
    s += text(X(0) + 10, Y(Br) - 6, "Bᵣ", 14, GREEN, "start", "bold")
    s += text(X(0) + 10, Y(Br) + 9, "залишок", 9.5, GREEN, "start")

    # коерцитивна сила Hc (B=0 на нижній вітці)
    # розв'яжемо tanh((H-Hc)*2.2)=0 → H=Hc=0.32
    Hc = 0.32
    s += circle(X(Hc), Y(0), 4.5, PURPLE)
    s += text(X(Hc) + 6, Y(0) + 20, "H_c", 13, PURPLE, "start", "bold")
    s += text(X(Hc) + 6, Y(0) + 35, "коерцитивна", 9.5, PURPLE, "start")
    s += text(X(Hc) + 6, Y(0) + 48, "сила", 9.5, PURPLE, "start")

    # підпис заштрихованої площі
    s += text(cx + sx * 0.02, cy - 2, "площа = втрати", 13, RED, "middle", "bold")
    s += text(cx + sx * 0.02, cy + 15, "за цикл  (Дж/м³)", 11, RED, "middle")

    # формула внизу
    s += rect(40, H - 58, W - 80, 40, "#fafafa", FAINT, 1.2, 8)
    s += text(W / 2, H - 32, "w_цикл  =  ∮ H dB     [ Дж/м³ ]     — площа, охоплена петлею",
              14, INK, "middle", "bold")

    save("fig-8-6m-1-loop-area.svg", s)


def fig_loop_width():
    """Рис. 1.8.6m.2 — порівняння: тонка петля (м'який ферит) vs широка (сталь);
    площа ∝ частота → нагрів. Дві петлі поруч + стовпчики втрат."""
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 30, "Вузька петля гріє мало, широка — багато: чому осердя бувають «м'які» й «тверді»",
              16, INK, "middle", "bold")
    s += text(W / 2, 50, "Однакова амплітуда B, та площа (а отже й тепло за цикл) різниться в рази",
              11.5, GREY, "middle", style="italic")

    def draw_loop(ox, oy, Hc, title, subtitle, fill, n=160, sx=95, sy=95, Bsat=1.0, Hmax=1.05):
        # локальні осі
        s_local = ""
        s_local += line(ox - sx * Hmax - 10, oy, ox + sx * Hmax + 10, oy, GREY, 1.1)
        s_local += line(ox, oy - sy * 1.25, ox, oy + sy * 1.25, GREY, 1.1)
        s_local += text(ox + sx * Hmax + 14, oy + 4, "H", 12, GREY, "start", "bold", "italic")
        s_local += text(ox + 8, oy - sy * 1.25 + 4, "B", 12, GREY, "start", "bold", "italic")

        def X(Hv):
            return ox + sx * Hv

        def Y(Bv):
            return oy - sy * Bv

        pts_up, pts_dn = [], []
        for i in range(n + 1):
            Hv = -Hmax + 2 * Hmax * i / n
            pts_up.append((Hv, Bsat * math.tanh((Hv + Hc) * 2.4)))
            pts_dn.append((Hv, Bsat * math.tanh((Hv - Hc) * 2.4)))
        poly = [(X(h), Y(b)) for h, b in pts_dn] + [(X(h), Y(b)) for h, b in reversed(pts_up)]
        s_local += polygon(poly, fill)
        s_local += polyline([(X(h), Y(b)) for h, b in pts_dn], RED, 2.6)
        s_local += polyline([(X(h), Y(b)) for h, b in pts_up], RED, 2.6)
        # Hc мітка
        s_local += circle(X(Hc), Y(0), 3.6, PURPLE)
        s_local += text(ox, oy + sy * 1.25 + 22, title, 13.5, INK, "middle", "bold")
        s_local += text(ox, oy + sy * 1.25 + 40, subtitle, 10.5, GREY, "middle")
        # площа-оцінка для стовпчика
        return s_local

    s += draw_loop(195, 175, 0.18, "М'яке осердя (ферит, кремниста сталь)",
                   "мала H_c → вузька петля → мало тепла", "#dbeede")
    s += draw_loop(615, 175, 0.62, "Тверде осердя (звичайна сталь)",
                   "велика H_c → широка петля → багато тепла", "#fbdcd6")

    # ── нижній блок: масштабування з частотою ──
    by = 350
    s += rect(40, by, W - 80, 95, "#fafafa", FAINT, 1.2, 10)
    s += text(60, by + 26, "Потужність нагріву = площа петлі × частота перемагнічування:",
              13.5, INK, "start", "bold")
    s += text(60, by + 52, "P_гіст / V  =  f · ∮ H dB        [ Вт/м³ ]",
              14.5, RED, "start", "bold")
    s += text(60, by + 76, "Подвоїш частоту f — подвоїться й тепло від гістерезису. Тому в перетворювачах на десятках кГц",
              11, GREY, "start")
    s += text(60, by + 90, "беруть ферити з тонкою петлею, а не звичайну сталь.",
              11, GREY, "start")

    save("fig-8-6m-2-loop-width.svg", s)


if __name__ == "__main__":
    fig_loop_area()
    fig_loop_width()
    print("done")
