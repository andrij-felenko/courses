# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки 🧮 «Формули астабільного 555» (тема 2.12.3, Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; стрілки
через marker; шрифт sans-serif. Допоміжні функції скопійовано з figs.py розділів
цього модуля (єдиний вигляд). Імена SVG — унікальні (префікс fig-12-3m-…),
щоб не зачіпати головний figs.py розділу.
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
SUN   = "#e0a32e"
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
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def path(d, color=INK, w=2, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da} '
            f'stroke-linejoin="round" stroke-linecap="round"/>\n')


def res(x, y, w, h, label=None, color=INK):
    """Резистор-зигзаг у вертикальній орієнтації (вивід зверху→вниз)."""
    s = ""
    n = 6
    step = h / n
    pts = [(x, y)]
    amp = w / 2
    for i in range(n):
        xx = x + (amp if i % 2 == 0 else -amp)
        pts.append((xx, y + step * (i + 0.5)))
    pts.append((x, y + h))
    s += polyline(pts, color=color, w=2)
    return s


# ---------------------------------------------------------------------------
# Фігура 1: астабільний 555 — шляхи заряду/розряду та осцилограма (duty > 50%)
# ---------------------------------------------------------------------------
def fig_astable():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 26, "Астабільний 555: заряд крізь R₁+R₂, розряд лише крізь R₂",
              size=17, anchor="middle", weight="bold")

    # --- ліва частина: схема ---
    # рейки
    Vtop, Vbot = 70, 360
    xrail_l = 70
    s += line(xrail_l, Vtop, 300, Vtop, color=RED, w=2)       # +V рейка
    s += line(xrail_l, Vbot, 320, Vbot, color=BLUE, w=2)      # GND рейка
    s += text(xrail_l - 8, Vtop - 8, "+V", size=14, color=RED, anchor="start", weight="bold")
    s += text(xrail_l - 8, Vbot + 18, "GND", size=13, color=BLUE, anchor="start")

    # колонка R1 (зверху від вузла A до +V)
    xR = 150
    yA = 175          # вузол A (між R1 і R2) = вивід 7 (DISCHARGE)
    yB = 270          # вузол B (між R2 і C) = виводи 2/6 (THR/TRIG)
    s += line(xR, Vtop, xR, 95, color=INK)
    s += res(xR, 95, 16, 55, color=INK)
    s += line(xR, 150, xR, yA, color=INK)
    s += text(xR + 16, 122, "R₁", size=15, weight="bold")

    # колонка R2 (від A до B)
    s += res(xR, yA + 5, 16, 55, color=INK)
    s += line(xR, yA + 60, xR, yB, color=INK)
    s += text(xR + 16, yA + 38, "R₂", size=15, weight="bold")

    # вузол A → вивід 7 чипа
    s += circle(xR, yA, 3.2, fill=INK, stroke=INK, w=1)
    # вузол B → конденсатор + виводи 2,6
    s += circle(xR, yB, 3.2, fill=INK, stroke=INK, w=1)

    # конденсатор C від B до GND
    s += line(xR, yB, xR, 318, color=INK)
    s += line(xR - 16, 318, xR + 16, 318, color=INK, w=3)
    s += line(xR - 16, 326, xR + 16, 326, color=INK, w=3)
    s += line(xR, 326, xR, Vbot, color=INK)
    s += text(xR + 16, 326, "C", size=15, weight="bold")

    # чип 555 (прямокутник праворуч від резисторної колонки)
    cx, cy, cw, ch = 230, 150, 70, 150
    s += rect(cx, cy, cw, ch, fill=LGRN, stroke=INK, sw=2, rx=4)
    s += text(cx + cw / 2, cy + 22, "555", size=16, anchor="middle", weight="bold")
    # виводи чипа
    # 7 DISCHARGE → вузол A
    s += line(xR, yA, cx, yA, color=INK)
    s += text(cx + 5, yA - 5, "7 DIS", size=11, anchor="start")
    # 6/2 THR+TRIG → вузол B
    s += line(xR, yB, cx, yB, color=INK)
    s += text(cx + 5, yB - 5, "6·2", size=11, anchor="start")
    # 3 OUT
    yout = cy + ch - 18
    s += line(cx + cw, yout, cx + cw + 24, yout, color=GREEN, w=2)
    s += text(cx + cw + 6, yout - 6, "3 OUT", size=11, anchor="start", color=GREEN)

    # стрілки шляхів струму
    # заряд (червоний): +V → R1 → R2 → C
    s += text(xrail_l - 4, 50, "заряд (charge): +V → R₁ → R₂ → C", size=12, color=RED, anchor="start", weight="bold")
    s += arrow(xR - 26, 110, xR - 26, 150, color=RED, w=2)
    s += arrow(xR - 26, 185, xR - 26, 250, color=RED, w=2)
    # розряд (синій): C → R2 → вивід 7
    s += text(xrail_l - 4, 392, "розряд (discharge): C → R₂ → вивід 7", size=12, color=BLUE, anchor="start", weight="bold")
    s += arrow(xR + 30, 250, xR + 30, 195, color=BLUE, w=2)
    s += text(xR + 30, 168, "→7", size=11, color=BLUE, anchor="middle")

    # --- права частина: осцилограма ---
    ox, oy = 400, 70          # лівий-верх осей
    ow, oh = 320, 250
    # осі
    s += arrow(ox, oy + oh, ox + ow + 10, oy + oh, color=INK, w=2)   # t
    s += arrow(ox, oy + oh, ox, oy - 10, color=INK, w=2)            # V
    s += text(ox + ow + 12, oy + oh + 4, "t", size=14, style="italic")
    s += text(ox - 8, oy - 12, "V", size=14, anchor="end", style="italic")

    # рівні ⅓ і ⅔ V
    y_full = oy + 20
    y_23 = oy + 70
    y_13 = oy + 150
    y_0 = oy + oh
    s += line(ox, y_23, ox + ow, y_23, color=GREY, w=1, dash="4 4")
    s += line(ox, y_13, ox + ow, y_13, color=GREY, w=1, dash="4 4")
    s += text(ox - 6, y_23 + 4, "⅔V", size=12, color=GREY, anchor="end")
    s += text(ox - 6, y_13 + 4, "⅓V", size=12, color=GREY, anchor="end")

    # напруга на C: експоненти між ⅓ і ⅔
    # один період: заряд (повільніше, R1+R2) від ⅓ до ⅔, потім розряд (R2) від ⅔ до ⅓
    def charge_seg(x0, x1, ylo, yhi, n=24):
        # від ylo(⅓) до yhi(⅔), наближення до стелі +V (y_full-ish) → опуклість угору
        pts = []
        target = y_full - 60   # уявна стеля (+V) вище ⅔
        for i in range(n + 1):
            f = i / n
            # експонента 1-e^{-k f}, нормована так, щоб старт=ylo, кінець=yhi
            k = 1.1
            a = (1 - math.exp(-k * f)) / (1 - math.exp(-k))
            y = ylo + (yhi - ylo) * a
            x = x0 + (x1 - x0) * f
            pts.append((x, y))
        return pts

    def disch_seg(x0, x1, yhi, ylo, n=24):
        pts = []
        for i in range(n + 1):
            f = i / n
            k = 1.6
            a = (1 - math.exp(-k * f)) / (1 - math.exp(-k))
            y = yhi + (ylo - yhi) * a
            x = x0 + (x1 - x0) * f
            pts.append((x, y))
        return pts

    # ширини: заряд ширший за розряд (t_H > t_L)
    tH = 78   # заряд
    tL = 46   # розряд
    x = ox + 6
    cappts = []
    # стартуємо знизу від ⅓ (перший заряд)
    cappts += charge_seg(x, x + tH, y_13, y_23)
    x += tH
    cappts += disch_seg(x, x + tL, y_23, y_13)
    x += tL
    cappts += charge_seg(x, x + tH, y_13, y_23)
    x += tH
    cappts += disch_seg(x, x + tL, y_23, y_13)
    x += tL
    cappts += charge_seg(x, x + tH * 0.5, y_13, y_13 + (y_23 - y_13) * 0.6)
    s += polyline(cappts, color=RED, w=2.4)
    s += text(ox + 150, oy + 8, "Vc(t) на конденсаторі", size=12, color=RED, anchor="middle")

    # вихід OUT: прямокутник, HIGH під час заряду (ширший), LOW під час розряду
    yo_hi = oy + 200
    yo_lo = oy + 235
    x = ox + 6
    outpts = [(x, yo_hi)]
    outpts += [(x + tH, yo_hi), (x + tH, yo_lo)]
    x += tH
    outpts += [(x + tL, yo_lo), (x + tL, yo_hi)]
    x += tL
    outpts += [(x + tH, yo_hi), (x + tH, yo_lo)]
    x += tH
    outpts += [(x + tL, yo_lo), (x + tL, yo_hi)]
    x += tL
    outpts += [(x + tH * 0.5, yo_hi)]
    s += polyline(outpts, color=GREEN, w=2.4)
    s += text(ox + 150, yo_lo + 22, "вихід (OUT)", size=12, color=GREEN, anchor="middle")

    # позначки tH / tL під першим періодом
    xb = ox + 6
    s += line(xb, yo_lo + 6, xb + tH, yo_lo + 6, color=GREEN, w=1)
    s += text(xb + tH / 2, yo_lo + 4 - 2, "", size=10)
    s += text(xb + tH / 2, yo_hi - 6, "tᴴ (заряд)", size=11, color=GREEN, anchor="middle")
    s += text(xb + tH + tL / 2, yo_hi - 6, "tᴸ", size=11, color=GREEN, anchor="middle")

    return W, H, s


# ---------------------------------------------------------------------------
# Фігура 2: чому duty > 50% та як діод дає 50% (розведення шляхів)
# ---------------------------------------------------------------------------
def fig_diode_fix():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 26, "Діод розводить шляхи: заряд лише крізь R₁, розряд лише крізь R₂",
              size=16, anchor="middle", weight="bold")

    # ---- ліва панель: класична схема (duty > 50%) ----
    def draw_block(x0, title, with_diode):
        ss = ""
        Vtop, Vbot = 80, 300
        xR = x0 + 70
        yA = 150
        yB = 230
        ss += line(x0 + 10, Vtop, xR + 40, Vtop, color=RED, w=2)
        ss += line(x0 + 10, Vbot, xR + 40, Vbot, color=BLUE, w=2)
        ss += text(x0 + 6, Vtop - 8, "+V", size=13, color=RED, weight="bold")
        ss += text(x0 + 6, Vbot + 18, "GND", size=12, color=BLUE)

        # R1
        ss += line(xR, Vtop, xR, 100, color=INK)
        ss += res(xR, 100, 14, 40, color=INK)
        ss += line(xR, 140, xR, yA, color=INK)
        ss += text(xR + 14, 118, "R₁", size=13, weight="bold")
        # R2
        ss += res(xR, yA + 4, 14, 40, color=INK)
        ss += line(xR, yA + 44, xR, yB, color=INK)
        ss += text(xR + 14, yA + 30, "R₂", size=13, weight="bold")
        # C
        ss += circle(xR, yB, 3, fill=INK, stroke=INK, w=1)
        ss += line(xR, yB, xR, 262, color=INK)
        ss += line(xR - 14, 262, xR + 14, 262, color=INK, w=3)
        ss += line(xR - 14, 270, xR + 14, 270, color=INK, w=3)
        ss += line(xR, 270, xR, Vbot, color=INK)
        ss += text(xR + 14, 270, "C", size=13, weight="bold")
        # вузол A → вивід 7
        ss += circle(xR, yA, 3, fill=INK, stroke=INK, w=1)
        ss += line(xR, yA, xR + 40, yA, color=INK)
        ss += text(xR + 42, yA + 4, "7", size=11)

        ss += text(x0 + 95, 50, title, size=13, anchor="middle", weight="bold")

        if with_diode:
            # діод паралельно R2: анод біля A(7), катод біля B → під час заряду
            # струм оминає R2 крізь діод (заряд лише R1), розряд крізь R2 (діод закритий)
            xd = xR - 34
            ss += line(xR, yA, xd, yA, color=GREEN, w=2)
            ss += line(xd, yA, xd, yB, color=GREEN, w=2)
            ss += line(xd, yB, xR, yB, color=GREEN, w=2)
            # символ діода (трикутник + риска) на вертикалі, спрямований униз (A→B = заряд)
            dy = (yA + yB) / 2
            ss += path(f"M {xd-8:.1f},{dy-8:.1f} L {xd+8:.1f},{dy-8:.1f} L {xd:.1f},{dy+8:.1f} Z",
                       color=GREEN, w=2, fill=LGRN)
            ss += line(xd - 9, dy + 8, xd + 9, dy + 8, color=GREEN, w=2)
            ss += text(xd - 12, dy + 2, "D", size=13, color=GREEN, anchor="end", weight="bold")
            # стрілка заряду крізь діод
            ss += arrow(xd - 14, yA + 18, xd - 14, yB - 18, color=RED, w=2)
            ss += text(xd - 18, dy + 2, "", size=10)
        return ss

    s += draw_block(40, "Класика: duty > 50%", with_diode=False)
    s += draw_block(380, "З діодом: duty ≈ 50%", with_diode=True)

    # формули внизу
    s += line(360, 60, 360, 320, color=FAINT, w=1)
    s += text(95 + 40, 340, "tᴴ = 0.693·(R₁+R₂)·C ;  tᴸ = 0.693·R₂·C", size=12.5, anchor="middle", color=INK)
    s += text(95 + 380, 340, "tᴴ ≈ 0.693·R₁·C ;  tᴸ ≈ 0.693·R₂·C", size=12.5, anchor="middle", color=GREEN)

    return W, H, s


def save(name, tup):
    W, H, body = tup
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name, f"({W}x{H})")


if __name__ == "__main__":
    save("fig-12-3m-1-astable-paths.svg", fig_astable())
    save("fig-12-3m-2-diode-fix.svg", fig_diode_fix())
    print("done")
