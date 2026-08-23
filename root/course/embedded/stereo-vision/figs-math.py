# -*- coding: utf-8 -*-
"""Фігури для вставки «Виведення формули диспаритету» (math-disparity-derivation).
Окремий генератор, щоб не чіпати figs.py теми. Запуск: python figs-math.py → ./img/*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: подібні трикутники однієї камери — звідки Z = f·X/x′ ────────────
def fig_similar_triangles():
    W, H = 760, 470
    f = []
    f.append(text(W/2, 26, "Два подібні трикутники в одній камері", size=17, bold=True))

    # Оптична вісь — горизонталь. Центр проєкції O ліворуч, сцена праворуч.
    # Малюємо «розгорнуту» камеру: матриця ПЕРЕД центром (модель тонкого отвору
    # без перевороту), щоб трикутники читалися без зайвого мінуса.
    Ox, Oy = 120, 300          # центр проєкції O (вершина обох трикутників)
    axis_x2 = 700
    f.append(arrow(Ox, Oy, axis_x2, Oy, color=INK, sw=1.6))
    f.append(text(axis_x2-4, Oy+22, "оптична вісь  Z →", size=12, anchor="end"))
    f.append(circle(Ox, Oy, 6, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(Ox-10, Oy+4, "O", size=14, bold=True, color=NEG, anchor="end"))
    f.append(text(Ox-10, Oy+22, "центр", size=10, color=MUTED, anchor="end"))

    # Площина матриці на відстані фокуса f від O (вертикальна риска)
    xImg = Ox + 90
    f.append(line(xImg, Oy-120, xImg, Oy+70, color=POS, sw=3))
    f.append(text(xImg, Oy+90, "матриця", size=12, color=POS, bold=True))
    # фокус f — відрізок O→матриця вздовж осі
    f.append(line(Ox, Oy+44, xImg, Oy+44, color=MUTED, sw=1.4))
    f.append(line(Ox, Oy, Ox, Oy+48, color=MUTED, sw=1, dash="3,3"))
    f.append(line(xImg, Oy, xImg, Oy+48, color=MUTED, sw=1, dash="3,3"))
    f.append(text((Ox+xImg)/2, Oy+62, "f", size=13, bold=True, color=INK))

    # Реальна точка P: на глибині Z (вздовж осі) і на висоті X над віссю
    Pz = 600                    # x-координата P на полотні = глибина
    Px_h = 150                  # висота X над віссю
    Py = Oy - Px_h
    f.append(circle(Pz, Py, 7, fill=FIELD, stroke=INK, sw=1.8))
    f.append(text(Pz+14, Py-4, "P", size=14, bold=True, anchor="start"))

    # Промінь P→O; перетин із матрицею на висоті x′ над віссю
    # подібність: x′/f = X/Z  →  на матриці висота = f * X / Z
    xp_h = f_focal = (xImg - Ox)            # f у пікселях полотна
    Zlen = (Pz - Ox)
    img_h = f_focal * Px_h / Zlen           # висота точки-зображення над віссю
    yimg = Oy - img_h
    f.append(line(Ox, Oy, Pz, Py, color=FIELD, sw=1.8))      # промінь через центр
    f.append(circle(xImg, yimg, 5, fill=POS, stroke=POS, sw=1))
    f.append(text(xImg+10, yimg-2, "x′", size=13, bold=True, color=POS, anchor="start"))

    # ВЕЛИКИЙ трикутник: O — (вісь під P) — P
    f.append(line(Pz, Oy, Pz, Py, color=INK, sw=1.4, dash="4,3"))   # катет X (далеко)
    f.append(text(Pz+14, (Oy+Py)/2, "X", size=13, bold=True, anchor="start"))
    f.append(text((Ox+Pz)/2, Oy-8, "Z", size=13, bold=True, color=MUTED))

    # МАЛИЙ трикутник: O — (вісь під x′) — x′
    f.append(line(xImg, Oy, xImg, yimg, color=POS, sw=2))           # катет x′ (близько)
    f.append(text(xImg-8, (Oy+yimg)/2, "x′", size=12, bold=True, color=POS, anchor="end"))

    # Прямі кути біля основ — маленькі квадратики
    f.append('<path d="M %.1f %.1f h 9 v -9" fill="none" stroke="%s" stroke-width="1"/>'
             % (xImg-9, Oy, MUTED))
    f.append('<path d="M %.1f %.1f h 9 v -9" fill="none" stroke="%s" stroke-width="1"/>'
             % (Pz-9, Oy, MUTED))

    # Рамка-висновок із пропорцією
    box, bw, bh = textbox(560, 150,
                          "подібні трикутники:\nx′ / f  =  X / Z\n⇒  Z = f · X / x′",
                          size=13, fill="#eafaf1", stroke=FIELD)
    f.append(box)

    render(os.path.join(OUT, "derivation-triangles.svg"), W, H, *f)


# ── Фігура 2: дві камери разом — диспаритет як різниця двох x′ ────────────────
def fig_two_cameras():
    W, H = 760, 460
    f = []
    f.append(text(W/2, 26, "Дві камери: один X, дві висоти на матрицях", size=17, bold=True))

    # Два центри на одній горизонталі (оптичні осі паралельні), рознесені на b.
    OLx, ORx = 180, 470
    Oy = 330
    f.append(circle(OLx, Oy, 6, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(circle(ORx, Oy, 6, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(OLx, Oy+24, "Oл (ліва)", size=11, color=NEG))
    f.append(text(ORx, Oy+24, "Oп (права)", size=11, color=POS))
    # база
    f.append(line(OLx, Oy+40, ORx, Oy+40, color=MUTED, sw=1.4))
    f.append(line(OLx, Oy, OLx, Oy+44, color=MUTED, sw=1, dash="3,3"))
    f.append(line(ORx, Oy, ORx, Oy+44, color=MUTED, sw=1, dash="3,3"))
    f.append(text((OLx+ORx)/2, Oy+58, "база  b", size=13, bold=True))

    # матриці перед центрами на висоті фокуса
    fpx = 70
    yImg = Oy - fpx
    halfw = 70
    for cx, col in ((OLx, NEG), (ORx, POS)):
        f.append(line(cx-halfw, yImg, cx+halfw, yImg, color=col, sw=3))
        f.append(line(cx, yImg, cx, Oy, color=MUTED, sw=1, dash="2,3"))  # оптична вісь
    f.append(line(OLx-halfw-16, yImg, OLx-halfw-16, Oy, color=MUTED, sw=1.2))
    f.append(text(OLx-halfw-26, (yImg+Oy)/2, "f", size=13, bold=True, anchor="end"))

    # точка P попереду, ближче до лівої камери для наочної різниці зсувів
    Px, Py = 360, 90
    f.append(circle(Px, Py, 7, fill=FIELD, stroke=INK, sw=1.8))
    f.append(text(Px+14, Py-4, "P (на Z)", size=12, bold=True, anchor="start"))

    # промені й точки попадання
    def hit(cx):
        t = (yImg - Py) / (Oy - Py)
        return Px + t * (cx - Px)
    hL, hR = hit(OLx), hit(ORx)
    f.append(line(Px, Py, OLx, Oy, color=NEG, sw=1.6))
    f.append(line(Px, Py, ORx, Oy, color=POS, sw=1.6))
    f.append(circle(hL, yImg, 5, fill=NEG, stroke=NEG))
    f.append(circle(hR, yImg, 5, fill=POS, stroke=POS))

    # координати x′ відносно власних оптичних осей (від осі камери до точки)
    f.append(line(OLx, yImg-14, hL, yImg-14, color=NEG, sw=2))
    f.append(text((OLx+hL)/2, yImg-20, "x′л", size=12, color=NEG, bold=True))
    f.append(line(ORx, yImg-30, hR, yImg-30, color=POS, sw=2))
    f.append(text((ORx+hR)/2, yImg-36, "x′п", size=12, color=POS, bold=True))

    box, bw, bh = textbox(610, 150,
                          "x′л = f·(X+b/2)/Z\nx′п = f·(X−b/2)/Z\n──────────\nd = x′л − x′п = f·b/Z\n⇒  Z = f·b / d",
                          size=12, fill="#eafaf1", stroke=FIELD)
    f.append(box)

    render(os.path.join(OUT, "derivation-two-cameras.svg"), W, H, *f)


# ── Фігура 3: епіполярна площина — чому пара точки лежить на одному рядку ─────
def fig_epipolar():
    W, H = 760, 430
    f = []
    f.append(text(W/2, 26, "Епіполярна площина зрізає обидві матриці одним рядком", size=16, bold=True))

    OLx, ORx, Oy = 180, 470, 300
    f.append(circle(OLx, Oy, 6, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(circle(ORx, Oy, 6, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(OLx, Oy+22, "Oл", size=12, color=NEG, bold=True))
    f.append(text(ORx, Oy+22, "Oп", size=12, color=POS, bold=True))
    f.append(line(OLx, Oy, ORx, Oy, color=MUTED, sw=1.4))
    f.append(text((OLx+ORx)/2, Oy+18, "база (вісь центрів)", size=11, color=MUTED))

    P = (340, 80)
    f.append(circle(P[0], P[1], 7, fill=FIELD, stroke=INK, sw=1.8))
    f.append(text(P[0]+14, P[1]-2, "P", size=14, bold=True, anchor="start"))

    # епіполярна площина = трикутник Oл–Oп–P (заштрихований)
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#eafaf1" '
             'fill-opacity="0.6" stroke="%s" stroke-width="1.4"/>'
             % (OLx, Oy, ORx, Oy, P[0], P[1], FIELD))
    f.append(text((OLx+ORx+P[0])/3, (Oy+Oy+P[1])/3 + 6, "епіполярна площина",
                  size=12, color=FIELD, bold=True))

    # промені до P
    f.append(line(OLx, Oy, P[0], P[1], color=NEG, sw=1.5))
    f.append(line(ORx, Oy, P[0], P[1], color=POS, sw=1.5))

    # матриці як вертикальні риски; перетин площини з матрицею — ОДИН рядок
    fpx = 64
    yImg = Oy - fpx
    halfw = 64
    for cx, col, nm in ((OLx, NEG, "рядок л"), (ORx, POS, "рядок п")):
        f.append(line(cx-halfw, yImg, cx+halfw, yImg, color=col, sw=3))
        # точка-перетин променя з матрицею
        t = (yImg - P[1]) / (Oy - P[1])
        hx = P[0] + t * (cx - P[0])
        f.append(circle(hx, yImg, 5, fill=col, stroke=col))
    f.append(text(OLx, yImg-12, "та сама горизонталь", size=11, color=INK))
    f.append(text(ORx, yImg-12, "та сама горизонталь", size=11, color=INK))

    box, bw, bh = textbox(380, 392,
                          "пара точки шукається не по всьому кадру, а вздовж ОДНОГО рядка",
                          size=12, fill="#fff8e6", stroke="#d39e00")
    f.append(box)

    render(os.path.join(OUT, "epipolar-plane.svg"), W, H, *f)


if __name__ == "__main__":
    fig_similar_triangles()
    fig_two_cameras()
    fig_epipolar()
    print("OK: figures written to", OUT)
