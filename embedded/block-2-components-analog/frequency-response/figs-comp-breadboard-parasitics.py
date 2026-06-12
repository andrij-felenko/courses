# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для КОМПОНЕНТНОЇ вставки 2.4.1c (макетка на ВЧ):
"Чому макетка бреше: пікофаради рядів і наногенрі перемичок на ВЧ".
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(fig-r04-1c-bb-*), щоб не конфліктувати з головним figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif.
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
COPP  = "#b5732e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
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


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
            f'fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n')


def _frame(x, y, w, h, title=""):
    s = rect(x, y, w, h, "#ffffff", "#c9d3dc", 1.4, 6)
    if title:
        s += text(x + w / 2, y - 6, title, 12, INK, "middle", "bold")
    return s


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 2.4.1c.1 — анатомія паразитів макетки: де живуть пФ рядів і нГн перемичок
# ─────────────────────────────────────────────────────────────────────────────
def fig_bb_anatomy():
    W, H = 860, 470
    s = header(W, H)
    s += text(W / 2, 30, "Де в макетці ховаються паразити", 19, INK, "middle", "bold")
    s += text(W / 2, 51, "ідеальний провід — це міф: кожен ряд має ємність, кожна перемичка — індуктивність",
              12.5, GREY, "middle", style="italic")

    # --- ліва панель: фізична макетка (вид зверху, кілька рядів) ---
    bx, by, bw, bh = 40, 78, 360, 350
    s += _frame(bx, by, bw, bh, "Фрагмент макетки (вид зверху)")

    # металеві контактні смуги-ряди (горизонтальні шини під отворами)
    rows_y = [by + 70 + i * 56 for i in range(4)]
    for i, ry in enumerate(rows_y):
        # металева смуга
        s += rect(bx + 40, ry - 12, 280, 24, "#f1d9bf", COPP, 1.4, 5)
        # отвори в ряду
        for k in range(10):
            s += circle(bx + 58 + k * 28, ry, 4.5, "#ffffff", COPP, 1.2)
        s += text(bx + 30, ry + 4, "ряд", 11, GREY, "end")

    # ємність між сусідніми рядами (паразитний конденсатор)
    for i in range(3):
        ya = rows_y[i] + 12
        yb = rows_y[i + 1] - 12
        ymid = (ya + yb) / 2
        # дві обкладки = краї смуг, поле між ними
        s += rect(bx + 70, ya + 2, 220, (yb - ya) - 4, LGRN, "none")
        # символ конденсатора збоку
        cx = bx + 305
        s += line(cx, ya + 2, cx, ya + 8, GREEN, 2)
        s += line(cx - 9, ya + 8, cx + 9, ya + 8, GREEN, 3)
        s += line(cx - 9, ya + 14, cx + 9, ya + 14, GREEN, 3)
        s += line(cx, ya + 14, cx, yb - 2, GREEN, 2)
        if i == 0:
            s += text(cx + 14, ymid - 2, "C_ряд", 12.5, GREEN, "start", "bold")
            s += text(cx + 14, ymid + 14, "~2–5 пФ", 11, GREEN, "start")

    s += text(bx + bw / 2, by + bh - 14,
              "сусідні ряди — дві пластини → конденсатор", 11.5, GREEN, "middle", style="italic")

    # --- перемичка-дріт зверху з індуктивністю ---
    jx0, jx1 = bx + 58, bx + 58 + 6 * 28
    jy = rows_y[0]
    # дугоподібний дріт між двома отворами різних рядів
    s += (f'<path d="M {jx0:.1f},{jy:.1f} C {jx0+20:.1f},{by+34:.1f} '
          f'{jx1-20:.1f},{by+34:.1f} {jx1:.1f},{rows_y[1]:.1f}" '
          f'fill="none" stroke="{BLUE}" stroke-width="3.4"/>\n')
    s += circle(jx0, jy, 4.5, BLUE, BLUE, 1)
    s += circle(jx1, rows_y[1], 4.5, BLUE, BLUE, 1)
    s += text(bx + 150, by + 30, "перемичка ≈ 5 см", 12, BLUE, "middle", "bold")
    s += text(bx + 150, by + 46, "L ≈ 50 нГн", 11.5, BLUE, "middle")

    # --- права панель: еквівалентна схема одного з'єднання ---
    ex, ey, ew, eh = 430, 78, 392, 350
    s += _frame(ex, ey, ew, eh, "Що насправді стоїть на шляху сигналу")

    # верхня шина "вузол A"
    nax = ex + 60
    nay = ey + 70
    s += circle(nax, nay, 5, INK, INK, 1)
    s += text(nax - 12, nay + 4, "A", 13, INK, "end", "bold")
    s += text(nax - 12, nay + 20, "(джерело)", 10.5, GREY, "end")

    # послідовна індуктивність перемички (зигзаг-котушка)
    lx0 = nax
    lx1 = nax + 150
    coil_y = nay
    # котушка як серія дуг
    n = 5
    seg = (lx1 - lx0) / n
    path = f'M {lx0:.1f},{coil_y:.1f} '
    for k in range(n):
        x = lx0 + k * seg
        path += f'q {seg/2:.1f},-16 {seg:.1f},0 '
    s += f'<path d="{path}" fill="none" stroke="{BLUE}" stroke-width="2.8"/>\n'
    s += text((lx0 + lx1) / 2, coil_y - 24, "L_перемички ≈ 50 нГн", 12, BLUE, "middle", "bold")

    # вузол B
    nbx = lx1 + 60
    nby = nay
    s += line(lx1, coil_y, nbx, nby, INK, 2)
    s += circle(nbx, nby, 5, INK, INK, 1)
    s += text(nbx + 12, nby + 4, "B", 13, INK, "start", "bold")
    s += text(nbx + 12, nby + 20, "(до чипа)", 10.5, GREY, "start")

    # паразитна ємність вузла B на сусідній ряд (вниз на землю)
    gy = ey + eh - 56
    s += line(nbx, nby, nbx, gy - 36, GREEN, 2)
    s += line(nbx - 12, gy - 36, nbx + 12, gy - 36, GREEN, 3)
    s += line(nbx - 12, gy - 28, nbx + 12, gy - 28, GREEN, 3)
    s += line(nbx, gy - 28, nbx, gy, GREEN, 2)
    s += text(nbx + 18, gy - 36, "C_ряд", 12.5, GREEN, "start", "bold")
    s += text(nbx + 18, gy - 20, "~2–5 пФ", 11, GREEN, "start")
    # земля
    s += line(nbx - 16, gy, nbx + 16, gy, INK, 2.4)
    s += line(nbx - 10, gy + 6, nbx + 10, gy + 6, INK, 2)
    s += line(nbx - 5, gy + 12, nbx + 5, gy + 12, INK, 2)
    s += text(nbx, gy + 30, "сусідній ряд", 10.5, GREY, "middle")

    # підсумок-формула резонансу — у вільній смузі ліворуч від ємності
    fx = ex + 24
    fy = ey + 168
    s += rect(fx - 8, fy - 22, 300, 86, "#fff6f5", "#e7c3c0", 1.2, 6)
    s += text(fx, fy, "L та C утворюють РЕЗОНАНСНИЙ контур", 13, RED, "start", "bold")
    s += text(fx, fy + 22,
              "f₀ = 1/(2π·√(L·C)) ≈", 11.5, RED, "start")
    s += text(fx, fy + 40,
              "1/(2π·√(50нГн·4пФ)) ≈ 350 МГц", 11.5, RED, "start")
    s += text(fx, fy + 58,
              "нижче f₀ — ще «дріт», вище — дзвенить", 11, GREY, "start", style="italic")

    save("fig-r04-1c-bb-1-anatomy.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 2.4.1c.2 — наслідок: той самий фронт на платі й на макетці (дзвін)
# ─────────────────────────────────────────────────────────────────────────────
def fig_bb_consequence():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Той самий швидкий фронт: на платі й на макетці", 18.5, INK, "middle", "bold")
    s += text(W / 2, 51, "паразитний LC-контур перетворює чисту сходинку на дзвін",
              12.5, GREY, "middle", style="italic")

    def panel(px, title, ring):
        pw, ph = 360, 248
        py = 78
        s = _frame(px, py, pw, ph, title)
        ox, oy = px + 50, py + ph - 46
        axw, axh = pw - 90, ph - 86
        # осі
        s += arrow(ox, oy, ox, oy - axh - 10, INK, 1.8)
        s += arrow(ox, oy, ox + axw + 10, oy, INK, 1.8)
        s += text(ox + axw + 12, oy + 4, "t", 12, INK, "start", "bold")
        s += text(ox - 6, oy - axh - 16, "V", 12, INK, "middle", "bold")
        # рівні
        ylo = oy - 14
        yhi = oy - axh + 18
        s += line(ox, ylo, ox + axw, ylo, FAINT, 1.2, "3,3")
        s += line(ox, yhi, ox + axw, yhi, FAINT, 1.2, "3,3")
        s += text(ox - 8, yhi + 4, "1", 11, GREY, "end")
        s += text(ox - 8, ylo + 4, "0", 11, GREY, "end")
        # форма сходинки
        x_edge = ox + axw * 0.34
        pts = [(ox, ylo)]
        N = 160
        for k in range(N + 1):
            xx = ox + axw * k / N
            if xx < x_edge:
                yy = ylo
            else:
                tt = (xx - x_edge) / (axw * 0.62)
                if ring:
                    # затухлий дзвін навколо 1
                    env = math.exp(-3.2 * tt)
                    val = 1 - env * math.cos(13.0 * tt)
                else:
                    # чистий швидкий фронт із легким згладжуванням
                    val = 1 - math.exp(-9.0 * tt)
                val = max(0.0, min(1.32, val))
                yy = ylo + (yhi - ylo) * val
            pts.append((xx, yy))
        col = RED if ring else GREEN
        s += _poly(pts, col, 2.8)
        # ідеальний фронт пунктиром для порівняння
        s += line(x_edge, ylo, x_edge, yhi, INK, 1.4, "4,3")
        s += line(x_edge, yhi, ox + axw, yhi, INK, 1.2, "4,3")
        return s, py, ph

    sL, py, ph = panel(40, "На друкованій платі (короткі доріжки)", False)
    s += sL
    s += text(40 + 180, py + ph + 24, "чистий фронт: смуга — гігагерци", 12, GREEN, "middle", "bold")

    sR, _, _ = panel(460, "На макетці (5-см перемички, ряди-пФ)", True)
    s += sR
    s += text(460 + 180, py + ph + 24, "дзвін і викид: контур ~350 МГц збуджено", 12, RED, "middle", "bold")

    # стрілка-висновок між панелями
    s += text(W / 2, py + ph + 50,
              "те, що на платі працює, на макетці «бреше»: вище ~10–20 МГц макетці вже не вірять",
              12, INK, "middle", style="italic")

    save("fig-r04-1c-bb-2-consequence.svg", s)


if __name__ == "__main__":
    fig_bb_anatomy()
    fig_bb_consequence()
    print("done")
