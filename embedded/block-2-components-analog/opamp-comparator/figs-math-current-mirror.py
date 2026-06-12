#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Фігури для математичної вставки 2.8.10m «Струмове дзеркало: цеглинка всередині ОП».
Чистий Python без залежностей -> SVG у ./img/ (унікальні імена fig-13-10m-*).
НЕ чіпати головний figs.py розділу.
"""
import os

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(IMG, exist_ok=True)

# --- спільний стиль (копія допоміжних, як вимагає §9) ---
RED = "#c62828"      # "+"
BLUE = "#1565c0"     # "-"
GREEN = "#2e7d32"    # поле / струм
INK = "#202020"
GREY = "#777777"
LIGHT = "#f4f4f4"
FONT = "font-family='Segoe UI, Helvetica, Arial, sans-serif'"


def header(w, h):
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' "
        f"width='{w}' height='{h}'>\n"
        f"<defs>"
        f"<marker id='arr' markerWidth='9' markerHeight='9' refX='7' refY='4.5' "
        f"orient='auto' markerUnits='userSpaceOnUse'>"
        f"<path d='M0,0 L9,4.5 L0,9 z' fill='{GREEN}'/></marker>"
        f"<marker id='arrk' markerWidth='9' markerHeight='9' refX='7' refY='4.5' "
        f"orient='auto' markerUnits='userSpaceOnUse'>"
        f"<path d='M0,0 L9,4.5 L0,9 z' fill='{INK}'/></marker>"
        f"</defs>\n"
        f"<rect x='0' y='0' width='{w}' height='{h}' fill='white'/>\n"
    )


def txt(x, y, s, size=15, col=INK, anchor="middle", weight="normal", style="normal"):
    return (f"<text x='{x}' y='{y}' {FONT} font-size='{size}' fill='{col}' "
            f"text-anchor='{anchor}' font-weight='{weight}' "
            f"font-style='{style}'>{s}</text>\n")


def line(x1, y1, x2, y2, col=INK, w=2, dash=None, marker=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    m = f" marker-end='url(#{marker})'" if marker else ""
    return (f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{col}' "
            f"stroke-width='{w}'{d}{m}/>\n")


def rail(x1, x2, y, col, label, lx):
    s = line(x1, y, x2, y, col=col, w=3)
    s += txt(lx, y - 8, label, size=14, col=col, weight="bold")
    return s


def npn(cx, cy, scale=1.0, col=INK):
    """Малюємо спрощений NPN-символ; повертає (svg, точки C,B,E)."""
    r = 22 * scale
    s = f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{col}' stroke-width='2'/>\n"
    bx = cx - r
    # вертикальна база-лінія всередині
    s += line(cx - 6, cy - 12 * scale, cx - 6, cy + 12 * scale, col=col, w=2.5)
    # вивід бази
    s += line(bx, cy, cx - 6, cy, col=col, w=2)
    # колектор (вгору-праворуч)
    s += line(cx - 6, cy - 6 * scale, cx + 9, cy - 14 * scale, col=col, w=2)
    s += line(cx + 9, cy - 14 * scale, cx + 9, cy - r, col=col, w=2)
    # емітер (вниз-праворуч) зі стрілкою (NPN -> назовні)
    s += line(cx - 6, cy + 6 * scale, cx + 9, cy + 14 * scale, col=col, w=2, marker="arrk")
    s += line(cx + 9, cy + 14 * scale, cx + 9, cy + r, col=col, w=2)
    pts = {"C": (cx + 9, cy - r), "B": (bx, cy), "E": (cx + 9, cy + r)}
    return s, pts


# ---------------------------------------------------------------------------
# Рис. 2.8.10m.1 — базове дзеркало струму: задаємо ліворуч, копіюємо праворуч
# ---------------------------------------------------------------------------
def fig1():
    W, H = 680, 440
    s = header(W, H)
    s += txt(W / 2, 28, "Струмове дзеркало (current mirror)", size=18, weight="bold")

    top = 70
    bot = 360
    # шина живлення зверху і землі знизу
    s += rail(60, 620, top, RED, "+Vs", 78)
    s += rail(60, 620, bot, BLUE, "0 В (земля)", 120)

    # ----- ліва (опорна) гілка -----
    xL = 230
    # джерело опорного струму згори: коло з I_REF
    cyS = top + 55
    s += f"<circle cx='{xL}' cy='{cyS}' r='26' fill='{LIGHT}' stroke='{INK}' stroke-width='2'/>\n"
    s += line(xL, top, xL, cyS - 26, col=INK, w=2)
    s += txt(xL, cyS + 5, "I_REF", size=14, weight="bold")
    s += txt(xL, cyS + 50, "опорний струм", size=12, col=GREY)
    s += line(xL, cyS + 26, xL, cyS + 70, col=INK, w=2)

    # лівий транзистор (діодно-з'єднаний: база до колектора)
    tcyL = 250
    gL, pL = npn(xL, tcyL, scale=1.15, col=INK)
    s += gL
    # колектор від вузла зверху
    s += line(pL["C"][0], pL["C"][1], pL["C"][0], cyS + 70, col=INK, w=2)
    node_y = cyS + 70
    s += f"<circle cx='{xL}' cy='{node_y}' r='3.5' fill='{INK}'/>\n"
    # земля від емітера
    s += line(pL["E"][0], pL["E"][1], pL["E"][0], bot, col=INK, w=2)

    # ----- права (вихідна) гілка -----
    xR = 470
    tcyR = 250
    gR, pR = npn(xR, tcyR, scale=1.15, col=INK)
    s += gR
    # земля від емітера
    s += line(pR["E"][0], pR["E"][1], pR["E"][0], bot, col=INK, w=2)
    # вихід-копія: стрілка струму вгору від колектора
    s += line(pR["C"][0], pR["C"][1], pR["C"][0], top, col=GREEN, w=2.5, marker=None)
    s += txt(xR + 86, 150, "I_OUT ≈ I_REF", size=15, col=GREEN, weight="bold", anchor="middle")
    s += txt(xR + 86, 170, "(копія струму)", size=12, col=GREY, anchor="middle")
    s += line(xR + 86, 182, xR + 6, 182, col=GREEN, w=2, marker="arr")

    # спільна база: з'єднати бази обох + завести на вузол колектора лівого
    by = pL["B"][1]
    s += line(pL["B"][0], by, xL - 70, by, col=INK, w=2)         # ліво від бази L
    s += line(xL - 70, by, xL - 70, node_y, col=INK, w=2)        # вгору до вузла
    s += line(xL - 70, node_y, xL, node_y, col=INK, w=2)         # у вузол колектора
    s += f"<circle cx='{xL - 70}' cy='{by}' r='3.5' fill='{INK}'/>\n"
    # бази обох транзисторів спільні
    s += line(pL["B"][0], by, pR["B"][0], by, col=INK, w=2)
    s += f"<circle cx='{pR['B'][0]}' cy='{by}' r='3.5' fill='{INK}'/>\n"
    # підпис спільної бази / однакового Vbe
    s += txt((xL + xR) / 2, by - 12, "спільна база  →  однакова U_BE", size=14,
             col=INK, weight="bold")

    # підписи транзисторів
    s += txt(xL - 36, tcyL + 4, "Q1", size=14, weight="bold")
    s += txt(xR + 40, tcyR + 4, "Q2", size=14, weight="bold")
    s += txt(xL, 405, "задаємо струм тут…", size=13, col=GREY)
    s += txt(xR, 405, "…а копія тече тут", size=13, col=GREEN)

    s += "</svg>\n"
    with open(os.path.join(IMG, "fig-13-10m-1-mirror.svg"), "w", encoding="utf-8") as f:
        f.write(s)


# ---------------------------------------------------------------------------
# Рис. 2.8.10m.2 — дзеркало як активне навантаження: складає обидві гілки пари
# ---------------------------------------------------------------------------
def fig2():
    W, H = 680, 470
    s = header(W, H)
    s += txt(W / 2, 26, "Дзеркало як активне навантаження диференційної пари", size=17, weight="bold")

    top = 64
    s += rail(50, 630, top, RED, "+Vs", 70)

    # верх: PNP-дзеркало (намалюємо як два прямокутники-блоки для ясності)
    # лівий блок дзеркала
    mY = top + 22
    s += f"<rect x='180' y='{mY}' width='130' height='52' rx='6' fill='{LIGHT}' stroke='{INK}' stroke-width='2'/>\n"
    s += f"<rect x='370' y='{mY}' width='130' height='52' rx='6' fill='#eef6ee' stroke='{GREEN}' stroke-width='2'/>\n"
    s += txt(245, mY + 22, "дзеркало:", size=13, weight="bold")
    s += txt(245, mY + 40, "тут задається", size=12, col=GREY)
    s += txt(435, mY + 22, "дзеркало:", size=13, weight="bold", col=GREEN)
    s += txt(435, mY + 40, "тут копіюється", size=12, col=GREEN)
    # з'єднати блоки (спільна керівна лінія)
    s += line(310, mY + 26, 370, mY + 26, col=INK, w=2)
    s += f"<circle cx='340' cy='{mY + 26}' r='3.5' fill='{INK}'/>\n"
    s += line(340, top, 340, mY, col=INK, w=2)

    # колекторні лінії вниз від дзеркала до пари
    cTop = mY + 52
    xLc = 245
    xRc = 435
    s += line(xLc, cTop, xLc, 230, col=INK, w=2)
    s += line(xRc, cTop, xRc, 230, col=GREEN, w=2.5)

    # ----- диференційна пара -----
    tcy = 252
    gL, pL = npn(xLc - 6, tcy, scale=1.1, col=BLUE)   # лівий вх. транзистор
    gR, pR = npn(xRc - 6, tcy, scale=1.1, col=RED)
    s += gL + gR
    # колектори у дзеркало
    s += line(pL["C"][0], pL["C"][1], xLc, 230, col=INK, w=2)
    s += f"<circle cx='{xLc}' cy='230' r='3.5' fill='{INK}'/>\n"
    s += line(pR["C"][0], pR["C"][1], xRc, 230, col=GREEN, w=2.5)
    s += f"<circle cx='{xRc}' cy='230' r='3.5' fill='{GREEN}'/>\n"

    # бази = входи
    s += line(pL["B"][0], pL["B"][1], pL["B"][0] - 60, pL["B"][1], col=BLUE, w=2)
    s += txt(pL["B"][0] - 70, pL["B"][1] + 4, "−", size=22, col=BLUE, weight="bold", anchor="end")
    s += txt(pL["B"][0] - 64, pL["B"][1] + 24, "вхід", size=12, col=BLUE, anchor="middle")
    s += line(pR["B"][0], pR["B"][1], pR["B"][0] + 60, pR["B"][1], col=RED, w=2)
    s += txt(pR["B"][0] + 70, pR["B"][1] + 4, "+", size=22, col=RED, weight="bold", anchor="start")
    s += txt(pR["B"][0] + 64, pR["B"][1] + 24, "вхід", size=12, col=RED, anchor="middle")

    # хвіст: спільні емітери на джерело струму
    eY = pL["E"][1]
    tailY = 330
    s += line(pL["E"][0], eY, pL["E"][0], tailY, col=INK, w=2)
    s += line(pR["E"][0], eY, pR["E"][0], tailY, col=INK, w=2)
    s += line(pL["E"][0], tailY, pR["E"][0], tailY, col=INK, w=2)
    midx = (pL["E"][0] + pR["E"][0]) / 2
    s += f"<circle cx='{midx}' cy='{tailY}' r='3.5' fill='{INK}'/>\n"
    # джерело струму-хвіст
    cyT = 372
    s += f"<circle cx='{midx}' cy='{cyT}' r='24' fill='{LIGHT}' stroke='{INK}' stroke-width='2'/>\n"
    s += line(midx, tailY, midx, cyT - 24, col=INK, w=2)
    s += txt(midx, cyT + 5, "I_хвіст", size=13, weight="bold")
    s += line(midx, cyT + 24, midx, 425, col=INK, w=2)
    s += rail(50, 630, 425, BLUE, "0 В", 70)

    # вихідний вузол
    s += f"<circle cx='{xRc}' cy='190' r='4.5' fill='{GREEN}'/>\n"
    s += line(xRc, 190, 600, 190, col=GREEN, w=2.5, marker="arr")
    s += txt(600, 182, "вихід", size=14, col=GREEN, weight="bold", anchor="end")

    # пояснювальна виноска
    s += txt(W / 2, 452, "Дзеркало віддзеркалює струм лівої гілки у праву — половинки складаються, а не гасять одна одну.",
             size=12.5, col=GREY)

    s += "</svg>\n"
    with open(os.path.join(IMG, "fig-13-10m-2-active-load.svg"), "w", encoding="utf-8") as f:
        f.write(s)


if __name__ == "__main__":
    fig1()
    fig2()
    print("OK: fig-13-10m-1-mirror.svg, fig-13-10m-2-active-load.svg")
