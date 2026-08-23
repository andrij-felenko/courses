# -*- coding: utf-8 -*-
# Фігури ДЕТАЛЬНОЇ статті ugv-platform-d.md.
# Тримаємо окремо від figs.py (базова), щоб не плутати вивід.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: перекидання як момент — багатокутник опори й критичний кут ──────
def f_tipover():
    W, H = 820, 470
    frags = []
    frags.append(text(W/2, 26, "Перекидання: вертикаль із центра мас і кут перекиду", size=17, bold=True))

    # ЛІВА панель: вид з торця, стійка машина на рівному
    # опорний слід — два колеса, відстань 2b; центр мас на висоті h
    gy = 210
    lx = 60
    trackL = 200
    wl = lx + 30
    wr = lx + 30 + trackL
    frags.append(line(lx, gy, lx + trackL + 60, gy, color=MUTED, sw=2))
    # колеса (перетин)
    for wx in (wl, wr):
        frags.append(circle(wx, gy-14, 14, fill="#e8ebef", stroke=INK, sw=2))
    # корпус
    frags.append(rect(wl-6, gy-96, (wr-wl)+12, 60, fill="#f4f6f8", stroke=INK, sw=2))
    # центр мас
    cmx = (wl+wr)/2
    cmy = gy-66
    frags.append(circle(cmx, cmy, 8, fill="#fff", stroke=INK, sw=2))
    frags.append(line(cmx-8, cmy, cmx+8, cmy, color=INK, sw=2))
    frags.append(line(cmx, cmy-8, cmx, cmy+8, color=INK, sw=2))
    # вертикаль униз від ЦМ
    frags.append(line(cmx, cmy, cmx, gy, color=NEG, sw=2, dash="5 4"))
    frags.append(text(cmx+8, gy-4, "всередині сліду → стійко", size=11, color=NEG, anchor="start"))
    # позначки b і h
    frags.append(line(cmx, gy+16, wr, gy+16, color=MUTED, sw=1.2))
    frags.append(text((cmx+wr)/2, gy+30, "b", size=13, italic=True, color=MUTED))
    frags.append(line(lx-4, cmy, lx-4, gy, color=MUTED, sw=1.2, dash="4 3"))
    frags.append(text(lx-12, (cmy+gy)/2, "h", size=13, italic=True, color=MUTED, anchor="end"))
    frags.append(text((wl+wr)/2, gy+52, "рівне: вертикаль падає між колесами", size=11, color=INK))

    # ПРАВА панель: нахил на кут α — вертикаль підходить до колеса
    ox = 430
    ang = 27 * math.pi/180
    # похилий ґрунт
    ax, ay = ox+10, gy+30
    Lg = 280
    bx2, by2 = ax + Lg*math.cos(ang), ay - Lg*math.sin(ang)
    frags.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#eef1f4" stroke="%s" stroke-width="2"/>' % (ax, ay, bx2, by2, bx2, ay, LINE))
    frags.append(text(ax+58, ay-8, "α", size=14, italic=True, bold=True))
    # колеса на схилі (нижнє й верхнє), корпус
    ux, uy = math.cos(ang), -math.sin(ang)   # уздовж, вгору
    nx, ny = math.sin(ang), math.cos(ang)    # нормаль, від поверхні
    base = (ax + 90*math.cos(ang), ay - 90*math.sin(ang))
    def pt(along, up):
        return (base[0] + along*ux + up*nx, base[1] + along*uy + up*ny)
    wlo = pt(0, 14); whi = pt(96, 14)
    frags.append(circle(wlo[0], wlo[1], 13, fill="#e8ebef", stroke=INK, sw=2))
    frags.append(circle(whi[0], whi[1], 13, fill="#e8ebef", stroke=INK, sw=2))
    c1 = pt(-4, 26); c2 = pt(100, 26); c3 = pt(100, 84); c4 = pt(-4, 84)
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#f4f6f8" stroke="%s" stroke-width="2"/>' % (
        c1[0], c1[1], c2[0], c2[1], c3[0], c3[1], c4[0], c4[1], INK))
    # центр мас
    cm = pt(48, 55)
    frags.append(circle(cm[0], cm[1], 8, fill="#fff", stroke=INK, sw=2))
    frags.append(line(cm[0]-8, cm[1], cm[0]+8, cm[1], color=INK, sw=2))
    frags.append(line(cm[0], cm[1]-8, cm[0], cm[1]+8, color=INK, sw=2))
    # вертикаль униз — падає майже на нижнє колесо
    frags.append(line(cm[0], cm[1], cm[0], ay+2, color=POS, sw=2.4, dash="5 4"))
    frags.append(text(cm[0]+10, ay-6, "край сліду → на межі", size=11, color=POS, anchor="start"))
    # нижнє колесо — вісь перекиду
    frags.append(circle(wlo[0], wlo[1], 4, fill=POS, stroke=POS))

    # формула критичного кута знизу
    body, bw, bh = textbox(W/2, 442,
        "перекид, коли вертикаль виходить за колесо:  tan α_кр = b / h   (широко й низько → великий α_кр)",
        size=13, bold=True, fill="#eafaf0", stroke=FIELD)
    frags.append(body)

    render(os.path.join(OUT, 'tipover.svg'), W, H, *frags)


# ── Фігура 2: геометрія наїзду на сходинку — звідки «третина радіуса» ─────────
def f_stepclimb():
    W, H = 760, 430
    frags = []
    frags.append(text(W/2, 26, "Колесо бере сходинку: геометрія точки дотику", size=17, bold=True))

    gy = 330
    # низький ґрунт зліва
    edge_x = 380
    frags.append(line(70, gy, edge_x, gy, color=MUTED, sw=2))
    # сходинка висотою s
    s = 78
    top_y = gy - s
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eef1f4" stroke="%s" stroke-width="2"/>' % (edge_x, top_y, W-70-edge_x, s+2, LINE))
    frags.append(line(edge_x, top_y, edge_x, gy, color=INK, sw=2))
    # висота сходинки s
    frags.append(line(edge_x-16, top_y, edge_x-16, gy, color=POS, sw=1.4, dash="4 3"))
    frags.append(text(edge_x-22, (top_y+gy)/2, "s", size=14, italic=True, bold=True, color=POS, anchor="end"))

    # колесо радіуса R, торкається кромки сходинки
    R = 118
    # центр колеса: торкаємось верхньої кромки (edge_x, top_y); колесо котиться по низу зліва.
    # центр на висоті R над низьким ґрунтом, x підібраний, щоб відстань до кромки = R
    cy = gy - R
    dx = math.sqrt(max(R*R - (gy - top_y - R)**2, 1))  # горизонталь від кромки до центра
    # кромка вище за центр? ні: top_y=gy-s, center_y=gy-R, R>s → центр вище кромки
    cx = edge_x - dx
    frags.append(circle(cx, cy, R, fill="none", stroke=INK, sw=2.5))
    frags.append(circle(cx, cy, 5, fill=INK, stroke=INK))
    # точка дотику = кромка
    tx, ty = edge_x, top_y
    frags.append(circle(tx, ty, 5, fill=POS, stroke=POS))
    # радіус до точки дотику
    frags.append(line(cx, cy, tx, ty, color=POS, sw=2))
    frags.append(text((cx+tx)/2-6, (cy+ty)/2-6, "R", size=14, italic=True, bold=True, color=POS, anchor="end"))
    # горизонталь від центра (рівень осі) до вертикалі кромки
    frags.append(line(cx, cy, tx, cy, color=MUTED, sw=1.4, dash="4 3"))
    # кут θ між радіусом-до-дотику й горизонталлю
    frags.append(text(cx+34, cy-8, "θ", size=14, italic=True, bold=True))
    # напрям реакції кромки (уздовж радіуса, від кромки до центра) та потрібна тяга
    frags.append(arrow(tx, ty, tx-46, ty-46*(cy-ty)/max(abs(cx-tx),1), color=FIELD, sw=2.2))

    # підпис геометрії праворуч унизу
    body, bw, bh = textbox(W/2, 402,
        "cos θ = (R − s)/R: що вище s, то крутіший підйом; ~R/3 бере котінням, вище R — глуха стіна",
        size=12, bold=True, fill="#f4f6f8", stroke=LINE)
    frags.append(body)

    render(os.path.join(OUT, 'stepclimb.svg'), W, H, *frags)


# ── Фігура 3: тиск на ґрунт — колесо проти гусениці, і зсув у повороті ────────
def f_groundpressure():
    W, H = 760, 400
    frags = []
    frags.append(text(W/2, 26, "Тиск на ґрунт: пляма контакту й зсув у повороті", size=17, bold=True))

    gy = 250
    frags.append(line(50, gy, W-50, gy, color=MUTED, sw=2))

    # ЛІВОРУЧ: колесо — маленька пляма, високий тиск
    cwx = 190
    frags.append(circle(cwx, gy-40, 40, fill="#f4f6f8", stroke=INK, sw=2))
    # пляма контакту (коротка) — червона потовщена
    frags.append(line(cwx-16, gy, cwx+16, gy, color=POS, sw=6))
    frags.append(text(cwx, gy-96, "колесо", size=14, bold=True))
    frags.append(text(cwx, gy+24, "мала пляма", size=12, color=POS, bold=True))
    frags.append(text(cwx, gy+42, "високий тиск p = W/A", size=11, color=INK))

    # ПРАВОРУЧ: гусениця — довга пляма, низький тиск
    tx0, tx1 = 430, 610
    ty = gy-42
    # обвід гусениці (спрощено — прямокутник із колесами)
    frags.append(rect(tx0, ty-18, tx1-tx0, 36, fill="#f4f6f8", stroke=INK, sw=2, rx=18))
    frags.append(circle(tx0+18, ty, 16, fill="#e8ebef", stroke=INK, sw=1.5))
    frags.append(circle(tx1-18, ty, 16, fill="#e8ebef", stroke=INK, sw=1.5))
    # довга пляма контакту
    frags.append(line(tx0+6, gy, tx1-6, gy, color=FIELD, sw=6))
    frags.append(text((tx0+tx1)/2, gy-70, "гусениця", size=14, bold=True))
    frags.append(text((tx0+tx1)/2, gy+24, "довга пляма", size=12, color=FIELD, bold=True))
    frags.append(text((tx0+tx1)/2, gy+42, "низький тиск — «пливе»", size=11, color=INK))

    # підпис-мораль про поворот
    body, bw, bh = textbox(W/2, 356,
        "та сама вага W на більшу площу A → менший тиск; зате поворот змушує пляму ШКРЕБТИ ґрунт боком",
        size=12, bold=True, fill="#eafaf0", stroke=FIELD)
    frags.append(body)

    render(os.path.join(OUT, 'groundpressure.svg'), W, H, *frags)


# ── Фігура 4: Пойкерт і просадка напруги під струмом ─────────────────────────
def f_peukert():
    W, H = 760, 420
    frags = []
    frags.append(text(W/2, 26, "Батарея під навантаженням: менше ємності, нижча напруга", size=16, bold=True))

    # ЛІВА панель: доступна ємність vs струм розряду (крива Пойкерта)
    ax0, ay0 = 90, 300   # початок осей
    axw, axh = 260, 210
    frags.append(line(ax0, ay0, ax0+axw, ay0, color=INK, sw=2))          # вісь X
    frags.append(line(ax0, ay0, ax0, ay0-axh, color=INK, sw=2))          # вісь Y
    frags.append(text(ax0+axw/2, ay0+30, "струм розряду (C)", size=12, color=MUTED))
    frags.append(text(ax0-18, ay0-axh-6, "доступна", size=11, color=MUTED, anchor="start"))
    frags.append(text(ax0-18, ay0-axh+10, "ємність", size=11, color=MUTED, anchor="start"))
    # крива: ємність спадає з ростом струму (сильніше для свинцю, м'якше для Li-ion)
    def cap(I, k):   # k — «жорсткість» спаду
        return 1.0 / (1.0 + k*(I-0.2))
    ptsPb = []
    ptsLi = []
    for j in range(0, 61):
        I = 0.2 + j/60.0*3.8
        x = ax0 + (I-0.2)/3.8*axw
        yPb = ay0 - cap(I, 0.35)*axh*0.95
        yLi = ay0 - cap(I, 0.10)*axh*0.95
        ptsPb.append("%.1f,%.1f" % (x, yPb))
        ptsLi.append("%.1f,%.1f" % (x, yLi))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(ptsLi), FIELD))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="6 4"/>' % (" ".join(ptsPb), POS))
    frags.append(text(ax0+axw-4, ay0-axh*0.86, "Li-ion (м'яко)", size=11, color=FIELD, anchor="end", bold=True))
    frags.append(text(ax0+axw-4, ay0-axh*0.30, "свинець (різко)", size=11, color=POS, anchor="end", bold=True))

    # ПРАВА панель: напруга під струмом — просадка на R_вн
    bx0, by0 = 470, 300
    bxw, bxh = 240, 210
    frags.append(line(bx0, by0, bx0+bxw, by0, color=INK, sw=2))
    frags.append(line(bx0, by0, bx0, by0-bxh, color=INK, sw=2))
    frags.append(text(bx0+bxw/2, by0+30, "струм навантаження", size=12, color=MUTED))
    frags.append(text(bx0-18, by0-bxh-6, "напруга", size=11, color=MUTED, anchor="start"))
    frags.append(text(bx0-18, by0-bxh+10, "на клемах", size=11, color=MUTED, anchor="start"))
    # пряма U = U0 − I·R_вн
    Voc_y = by0 - bxh*0.9
    end_y = by0 - bxh*0.35
    frags.append(line(bx0, Voc_y, bx0+bxw, end_y, color=NEG, sw=2.6))
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"/>' % (bx0, Voc_y, bx0+bxw, Voc_y, MUTED))
    frags.append(text(bx0+6, Voc_y-8, "U_хх (спокій)", size=11, color=MUTED, anchor="start"))
    frags.append(text(bx0+bxw-4, end_y+16, "U = U_хх − I·R_вн", size=11, color=NEG, anchor="end", bold=True))

    # підпис-мораль
    body, bw, bh = textbox(W/2, 392,
        "деруть сильно → ємність тане (Пойкерт), а напруга просідає на R_вн; обидва крадуть пробіг",
        size=12, bold=True, fill="#f4f6f8", stroke=LINE)
    frags.append(body)

    render(os.path.join(OUT, 'peukert.svg'), W, H, *frags)


if __name__ == '__main__':
    f_tipover()
    f_stepclimb()
    f_groundpressure()
    f_peukert()
    print("ok: tipover.svg, stepclimb.svg, groundpressure.svg, peukert.svg")
