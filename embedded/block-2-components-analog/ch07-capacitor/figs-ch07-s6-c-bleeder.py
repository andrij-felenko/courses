# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для вставки 2.1.6c «Чому блок живлення кусається
після вимкнення: bleeder-резистор» (Розділ 2.1, Модуль 2).

Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
fig-7-6cb-*.svg (b = bleeder), щоб не перетинатися з головним figs.py
розділу й вставкою про розв'язку (fig-7-6c-*).

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи в тексті — «Рис. 2.1.6c.k».
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (узгоджена з figs.py розділу) ────────────────────────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
METAL = "#9a9aa0"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fbf4e2"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


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
    r = f' rx="{rx}"' if rx else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{r}/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def polyline(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linecap="round" stroke-linejoin="round"/>\n')


def cap_symbol(cx, cy, s=""):
    """Конденсатор (дві пластини) вертикально, центр у (cx,cy)."""
    out = ""
    out += line(cx - 16, cy - 8, cx + 16, cy - 8, INK, 3)   # верхня пластина
    out += line(cx - 16, cy + 8, cx + 16, cy + 8, INK, 3)   # нижня пластина
    if s:
        out += text(cx + 24, cy + 5, s, 14, INK)
    return out


def res_symbol(cx, cy, label="", horiz=False):
    """Резистор-зигзаг. Вертикальний (за замовч.) або горизонтальний."""
    out = ""
    if horiz:
        out += rect(cx - 26, cy - 9, 52, 18, "#ffffff", INK, 2)
        if label:
            out += text(cx, cy + 30, label, 14, INK, "middle")
    else:
        out += rect(cx - 9, cy - 26, 18, 52, "#ffffff", INK, 2)
        if label:
            out += text(cx + 18, cy + 5, label, 14, INK)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.1.6c.1 — два сценарії: без bleeder заряд лишається, з bleeder стікає
# ─────────────────────────────────────────────────────────────────────────────
def fig_circuit():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 30, "Та сама вхідна ланка блока живлення — мережу щойно вимкнено",
              17, INK, "middle", "bold")

    def panel(x0, title, with_bleeder, sub, subcol):
        out = ""
        pw = 330
        out += rect(x0, 52, pw, 330, "#ffffff", GREY, 1.5, 10)
        out += text(x0 + pw / 2, 78, title, 15, INK, "middle", "bold")

        # координати кола всередині панелі
        lx = x0 + 60      # ліва шина (фаза, обірвана)
        rx = x0 + 250     # права шина (нейтраль/мінус)
        topy = 120
        boty = 320
        midy = (topy + boty) / 2

        # вилка / розрив мережі (вимкнено)
        out += line(lx, topy, lx, midy - 40, INK, 2)
        out += line(lx, midy + 40, lx, boty, INK, 2)
        # символ розриву (вимкнена вилка)
        out += circle(lx, midy - 26, 5, "#ffffff", GREY, 2)
        out += circle(lx, midy + 26, 5, "#ffffff", GREY, 2)
        out += line(lx - 14, midy - 14, lx + 14, midy + 14, RED, 2.5)
        out += line(lx - 14, midy + 14, lx + 14, midy - 14, RED, 2.5)
        out += text(lx - 16, midy + 4, "✂", 18, RED, "end")
        out += text(lx, boty + 22, "мережу вимкнено", 12, GREY, "middle")

        # верхня й нижня шини до конденсатора
        capx = (lx + rx) / 2
        out += line(lx, topy, rx, topy, INK, 2)
        out += line(lx, boty, rx, boty, INK, 2)

        # конденсатор (bulk) посередині
        out += line(capx, topy, capx, midy - 8, INK, 2)
        out += line(capx, midy + 8, capx, boty, INK, 2)
        out += cap_symbol(capx, midy)
        out += text(capx + 26, midy - 10, "C", 15, INK, "start", "bold")
        out += text(capx + 26, midy + 12, "330 мкФ", 12, INK)
        # позначки заряду на пластинах
        out += text(capx - 30, midy - 12, "+", 18, RED, "middle", "bold")
        out += text(capx - 30, midy + 22, "−", 18, BLUE, "middle", "bold")

        # права шина / навантаження-вузли (схематично)
        out += line(rx, topy, rx, boty, INK, 2)
        out += text(rx + 10, midy - 4, "до схеми", 12, GREY)
        out += text(rx + 10, midy + 12, "(вимкнена)", 12, GREY)

        if with_bleeder:
            # bleeder-резистор паралельно конденсатору, ближче до правого боку
            bx = capx + 70
            out += line(bx, topy, bx, midy - 26, INK, 2)
            out += line(bx, midy + 26, bx, boty, INK, 2)
            out += res_symbol(bx, midy, "")
            out += text(bx + 16, midy - 30, "R_bleed", 13, GREEN, "start", "bold")
            out += text(bx + 16, midy + 5, "100 кОм", 12, GREEN)
            # стрілка струму стікання
            out += arrow(bx, boty - 4, bx, boty - 36, GREEN, 2.2)
            out += text(bx + 14, boty - 18, "i", 13, GREEN, "start", "italic")

        # підпис-вердикт унизу панелі
        out += rect(x0 + 18, 344, pw - 36, 30, "#ffffff", subcol, 1.5, 6)
        out += text(x0 + pw / 2, 364, sub, 13, subcol, "middle", "bold")
        return out

    s += panel(28, "Без bleeder-резистора", False,
               "заряд лишається — небезпечно", RED)
    s += panel(402, "З bleeder-резистором", True,
               "стікає за секунди — безпечно", GREEN)

    s += footer()
    return W, H, s


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.1.6c.2 — крива розряду: V(t)=V0·e^(−t/τ), поріг 50 В, τ та 5τ
# ─────────────────────────────────────────────────────────────────────────────
def fig_discharge():
    W, H = 760, 440
    s = header(W, H)
    s += text(W / 2, 28, "Напруга на конденсаторі після вимкнення: V(t) = V₀ · e^(−t/τ)",
              16, INK, "middle", "bold")

    # система координат
    ox, oy = 90, 360         # початок осей
    pw, ph = 590, 290        # довжина осей
    V0 = 320.0               # початкова напруга, В
    tau = 1.0                # стала часу, с (умовні 1 с для наочності)
    tmax = 6.0               # вісь часу, с

    def X(t):
        return ox + (t / tmax) * pw

    def Y(v):
        return oy - (v / V0) * ph

    # сітка по напрузі
    for v in (0, 50, 100, 200, 300):
        yy = Y(v)
        s += line(ox, yy, ox + pw, yy, FAINT, 1)
        s += text(ox - 10, yy + 4, f"{v}", 12, GREY, "end")
    s += text(ox - 58, Y(160), "В", 13, GREY, "middle")
    # осі
    s += arrow(ox, oy, ox, oy - ph - 8, INK, 2)
    s += arrow(ox, oy, ox + pw + 8, oy, INK, 2)
    s += text(ox + pw + 6, oy + 22, "час", 13, INK, "end")

    # мітки часу в одиницях τ
    for k in range(0, 6):
        tt = k * tau
        xx = X(tt)
        s += line(xx, oy, xx, oy + 5, INK, 1.5)
        lab = "0" if k == 0 else f"{k}τ"
        s += text(xx, oy + 22, lab, 12, GREY, "middle")

    # небезпечна зона (вище 50 В) — бліде червоне тло
    yth = Y(50)
    s += rect(ox, oy - ph, pw, yth - (oy - ph), LRED, "none", 0)
    # безпечна зона нижче 50 В
    s += rect(ox, yth, pw, oy - yth, LGRN, "none", 0)
    s += line(ox, yth, ox + pw, yth, RED, 1.8, "6 4")
    s += text(ox + pw - 4, yth - 8, "50 В — поріг відчутного удару", 12, RED, "end", "bold")
    s += text(ox + pw - 4, yth + 18, "нижче — безпечно", 11, GREEN, "end")

    # крива розряду
    pts = []
    t = 0.0
    while t <= tmax + 1e-6:
        pts.append((X(t), Y(V0 * math.exp(-t / tau))))
        t += 0.04
    s += polyline(pts, BLUE, 3)

    # точка V0
    s += circle(X(0), Y(V0), 4, BLUE, BLUE, 1)
    s += text(X(0) + 8, Y(V0) - 8, "V₀ ≈ 320 В", 13, BLUE, "start", "bold")

    # позначка одного τ (37 %)
    v1 = V0 * math.exp(-1)
    s += line(X(1), oy, X(1), Y(v1), GREY, 1.3, "3 3")
    s += line(ox, Y(v1), X(1), Y(v1), GREY, 1.3, "3 3")
    s += circle(X(1), Y(v1), 3.5, GREY, GREY, 1)
    s += text(X(1) + 8, Y(v1) - 6, "1τ → 37 %", 12, GREY, "start")

    # точка, де крива перетинає 50 В:  t = τ·ln(V0/50)
    tcross = tau * math.log(V0 / 50.0)
    s += circle(X(tcross), yth, 4.5, RED, "#ffffff", 2)
    s += text(X(tcross) + 8, yth + 34, f"≈ {tcross:.1f}τ: впало до безпечного", 12, RED, "start", "bold")

    # 5τ — практично розряджено
    s += text(X(5) - 4, Y(V0 * math.exp(-5)) - 14, "5τ → < 1 %", 12, INK, "middle")

    # формула τ
    s += rect(ox + 250, oy - ph + 6, 322, 56, LAMB, AMBER, 1.5, 8)
    s += text(ox + 262, oy - ph + 28, "τ = R · C", 15, INK, "start", "bold")
    s += text(ox + 262, oy - ph + 48,
              "більший резистор → довше тримає заряд", 12, INK)

    s += footer()
    return W, H, s


def save(name, tup):
    w, h, body = tup
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print(f"  {name}  ({w}x{h})")


if __name__ == "__main__":
    print("Генерую фігури вставки 2.1.6c (bleeder):")
    save("fig-7-6cb-1-circuit.svg", fig_circuit())
    save("fig-7-6cb-2-discharge.svg", fig_discharge())
    print("Готово.")
