# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для компонентної вставки 2.11.9c
«Варистор і запобіжник: перший рубіж між мережею і платою».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

УНІКАЛЬНІ імена файлів (fig-r11-9c-*), щоб не зачіпати головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи — Рис. 2.11.9c.k.
Допоміжні функції скопійовано з figs-r11-s4-m-phase-power.py (єдиний вигляд).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMBER = "#fdf3e0"
AMBER = "#c9881e"
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


def _path(pts, col, wv=2.4, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
            f'fill="{fill}" stroke="{col}" stroke-width="{wv}"{d}/>\n')


def _area(pts, fill, stroke="none", wv=0):
    s = f' stroke="{stroke}" stroke-width="{wv}"' if stroke != "none" else ' stroke="none"'
    return (f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)} Z" '
            f'fill="{fill}"{s}/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 2.11.9c.1 — карта входу мережі: де сидять запобіжник, варистор і фільтр.
#  L/N → запобіжник (послідовно в L) → MOV (паралельно L-N) → далі схема.
#  Показуємо порядок, призначення кожного й куди йде енергія удару.
# ─────────────────────────────────────────────────────────────────────────────
def fig1_mains_entry():
    W, H = 780, 430
    s = header(W, H)
    s += text(W / 2, 30, "Вхід мережі: порядок першого рубежу захисту", 16, INK, "middle", "bold")

    # горизонтальні шини L (зверху) і N (знизу)
    yL = 110
    yN = 320
    x0 = 70          # вхід зліва (з мережі)
    xF = 210         # запобіжник
    xMOV = 380       # варистор
    xOut = 690       # вихід праворуч (до схеми)

    # підписи входу
    s += text(x0 - 8, yL - 14, "L (фаза)", 13, RED, "start", "bold")
    s += text(x0 - 8, yN + 26, "N (нуль)", 13, BLUE, "start", "bold")
    s += text(x0 - 8, (yL + yN) / 2 + 5, "З мережі", 12, GREY, "start", "italic")

    # шина N — суцільна синя
    s += line(x0, yN, xOut, yN, BLUE, 2.6)
    # шина L — до запобіжника червона, після — теж червона (через прилад)
    s += line(x0, yL, xF - 30, yL, RED, 2.6)

    # ── запобіжник (прямокутник у розрив L) ──
    s += rect(xF - 30, yL - 14, 60, 28, "#ffffff", INK, 2.2, 4)
    s += line(xF - 22, yL, xF + 22, yL, INK, 2.4)   # елемент усередині
    s += line(xF + 30, yL, xMOV - 10, yL, RED, 2.6)
    s += text(xF, yL - 26, "ЗАПОБІЖНИК", 12, INK, "middle", "bold")
    s += text(xF, yL - 40, "(послідовно в L)", 11, GREY, "middle")
    s += text(xF, yN - 24, "рве тривалий струм", 11, INK, "middle")
    s += text(xF, yN - 9, "перевантаження → розрив", 10, GREY, "middle", "italic")

    # ── варистор (MOV) — паралельно між L і N ──
    # символ: прямокутник із діагональною рискою (нелінійний резистор)
    mx = xMOV
    s += line(mx, yL, mx, yL + 40, INK, 2.4)
    s += rect(mx - 16, yL + 40, 32, 56, "#ffffff", INK, 2.2, 4)
    s += line(mx - 26, yL + 46, mx + 22, yL + 90, INK, 2.0)  # діагональ нелінійності
    s += line(mx, yL + 96, mx, yN, INK, 2.4)
    s += text(mx, yL + 32, "MOV", 12, INK, "middle", "bold")
    s += text(mx + 26, yL + 56, "варистор", 12, INK, "start", "bold")
    s += text(mx + 26, yL + 72, "(паралельно L–N)", 11, GREY, "start")
    s += text(mx + 26, yL + 90, "затискає сплеск напруги", 11, INK, "start")

    # стрілка «удар зливається в нуль через MOV»
    s += arrow(mx + 8, (yL + yN) / 2, mx + 8, yN - 6, GREEN, 2)
    s += text(mx + 14, (yL + yN) / 2 - 4, "сплеск", 10, GREEN, "start", "italic")

    # ── фільтр/далі (узагальнений блок) ──
    s += rect(xOut - 120, yL - 18, 120, yN - yL + 36, LBLUE, BLUE, 1.8, 6)
    s += text(xOut - 60, (yL + yN) / 2 - 8, "далі:", 12, BLUE, "middle", "bold")
    s += text(xOut - 60, (yL + yN) / 2 + 10, "EMI-фільтр,", 11, BLUE, "middle")
    s += text(xOut - 60, (yL + yN) / 2 + 26, "випрямляч, схема", 11, BLUE, "middle")
    s += line(xMOV + 10, yL, xOut - 120, yL, RED, 2.6)

    # земля під MOV-у трипровідних варіантах — натяк пунктиром (PE)
    s += text(W / 2, H - 18, "Порядок критичний: запобіжник СТОЇТЬ ПЕРЕД варистором, "
              "щоб згорілий MOV не лишився під струмом мережі.", 12, GREY, "middle", "italic")

    save("fig-r11-9c-1-mains-entry.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 2.11.9c.2 — нелінійна ВАХ варистора + поняття напруг
#  (робоча напруга, V_nom при 1 мА, затискання при великому струмі).
#  Лог-подібна крива I(V): майже не тече до коліна, далі різко.
# ─────────────────────────────────────────────────────────────────────────────
def fig2_mov_vi():
    W, H = 760, 440
    s = header(W, H)
    s += text(W / 2, 30, "Нелінійна ВАХ варистора: «стіна» біля напруги спрацювання", 15, INK, "middle", "bold")

    ox, oy = 110, 380
    plot_w = 560
    plot_h = 300

    # осі
    s += arrow(ox, oy, ox, oy - plot_h - 18, INK, 1.8)
    s += arrow(ox, oy, ox + plot_w + 18, oy, INK, 1.8)
    s += text(ox - 70, oy - plot_h - 4, "струм I", 13, INK, "start", "bold")
    s += text(ox + plot_w + 22, oy + 5, "напруга на MOV, V", 12, INK, "start", "bold")

    # модель: I = k * V^alpha (alpha велике). нормуємо так, щоб «коліно» було видно.
    # Беремо нормовану напругу u = V / V_nom; струм у логарифмічному масштабі по висоті.
    # Для наочності крива «майже горизонтальна» до u≈1, далі різко вгору.
    alpha = 30.0

    def curve_point(u):
        # відносний струм
        i_rel = u ** alpha
        return i_rel

    # масштаб: x від 0 до 1.45 u; y — нормуємо так, щоб у u=1.4 досягало верху
    u_max = 1.42
    i_top = curve_point(u_max)

    def X(u):
        return ox + plot_w * (u / u_max)

    def Y(i_rel):
        # лог-стиснення, щоб не вилазило: але лишаємо різкість коліна
        frac_ = (i_rel / i_top)
        return oy - plot_h * frac_

    pts = []
    u = 0.0
    while u <= u_max + 1e-9:
        pts.append((X(u), Y(curve_point(u))))
        u += 0.01
    s += _path(pts, RED, 3.0)

    # вертикалі-орієнтири: робоча напруга, V_nom (1 мА), затискання
    # робоча (u≈0.8): MOV мовчить
    uw = 0.8
    s += line(X(uw), oy, X(uw), oy - 40, GREEN, 2, dash="5,4")
    s += text(X(uw), oy + 20, "робоча", 11, GREEN, "middle", "bold")
    s += text(X(uw), oy + 35, "напруга", 11, GREEN, "middle")
    s += text(X(uw) - 6, oy - 48, "мовчить", 10, GREEN, "end", "italic")

    # V_nom при 1 мА (коліно, u=1.0)
    s += line(X(1.0), oy, X(1.0), Y(curve_point(1.0)), AMBER, 2, dash="5,4")
    s += circle(X(1.0), Y(curve_point(1.0)), 4.5, AMBER, INK, 1.6)
    s += text(X(1.0), oy + 20, "V_nom", 11, AMBER, "middle", "bold")
    s += text(X(1.0), oy + 35, "(1 мА)", 11, AMBER, "middle")

    # напруга затискання при великому струмі (u≈1.35)
    uc = 1.34
    s += line(X(uc), oy, X(uc), Y(curve_point(uc)), BLUE, 2, dash="5,4")
    s += circle(X(uc), Y(curve_point(uc)), 4.5, BLUE, INK, 1.6)
    s += text(X(uc) + 8, Y(curve_point(uc)) - 6, "V_clamp", 11, BLUE, "start", "bold")
    s += text(X(uc) + 8, Y(curve_point(uc)) + 10, "при сотнях А", 10, BLUE, "start")

    # горизонтальна стрілка робочого вікна
    s += text(ox + 12, oy - plot_h + 12, "до коліна струм мізерний — варистор «невидимий»",
              11, GREY, "start", "italic")
    s += text(X(1.1), oy - plot_h + 60, "за коліном:", 11, RED, "start", "italic")
    s += text(X(1.1), oy - plot_h + 76, "напруга майже не росте,", 11, RED, "start", "italic")
    s += text(X(1.1), oy - plot_h + 92, "а струм — лавиною", 11, RED, "start", "italic")

    save("fig-r11-9c-2-mov-vi.svg", s)


if __name__ == "__main__":
    fig1_mains_entry()
    fig2_mov_vi()
    print("done")
