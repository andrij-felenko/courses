# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_idea():
    """Спільна ідея: вузол, який сам себе піднімає, бо обидва його кінці їдуть разом."""
    W, H = 720, 360
    f = []
    f.append(text(W/2, 28, "Спільна ідея бутстрепа: обидва кінці їдуть разом", size=17, bold=True))

    # Ліворуч: звичайно — нижній кінець на місці, струм тече.
    f.append(text(180, 66, "Без бутстрепа", size=14, bold=True, color=MUTED))
    f.append(line(180, 90, 180, 150, color=INK, sw=2))           # верхній провід до елемента
    f.append(rect(150, 150, 60, 70, fill=FILL, stroke=LINE, sw=2))  # елемент (резистор/ємність)
    f.append(text(180, 190, "R", size=16, bold=True))
    f.append(line(180, 220, 180, 280, color=NEG, sw=2))          # нижній кінець стоїть
    f.append(line(140, 280, 220, 280, color=NEG, sw=3))          # «земля» — нерухомий низ
    f.append(text(180, 300, "низ нерухомий", size=12, color=NEG))
    f.append(text(300, 130, "сигнал", size=12, color=POS, anchor="start"))
    f.append(arrow(255, 150, 215, 175, color=POS, sw=2.0))
    f.append(text(300, 250, "крізь R тече\nповний струм", size=12, color=INK, anchor="start"))
    f.append(arrow(255, 235, 215, 210, color=INK, sw=1.8))

    # Праворуч: бутстреп — нижній кінець підняли копією верху.
    f.append(text(540, 66, "З бутстрепом", size=14, bold=True, color=FIELD))
    f.append(line(540, 90, 540, 150, color=INK, sw=2))
    f.append(rect(510, 150, 60, 70, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text(540, 190, "R", size=16, bold=True))
    f.append(line(540, 220, 540, 270, color=FIELD, sw=2))
    # стрілка вгору — низ піднімають
    f.append(arrow(600, 280, 600, 215, color=FIELD, sw=2.2))
    f.append(text(612, 250, "копія верху\nпіднімає низ", size=12, color=FIELD, anchor="start"))
    f.append(text(660, 130, "сигнал", size=12, color=POS, anchor="start"))
    f.append(arrow(615, 150, 575, 175, color=POS, sw=2.0))
    f.append(text(420, 240, "обидва кінці\nрівні → струму\nмайже нема", size=12, color=INK, anchor="end"))

    render(os.path.join(IMG, 'idea.svg'), W, H, *f)


def fig_follower():
    """Бутстреп резистора зміщення в повторювачі: апаратний опір зростає у 1/(1−A) раз."""
    W, H = 760, 400
    f = []
    f.append(text(W/2, 26, "Бутстреп зміщення в повторювачі піднімає вхідний опір", size=16, bold=True))

    top = 70; bot = 350
    railx = 120
    # Шина живлення
    f.append(line(60, top, 700, top, color=POS, sw=2))
    f.append(text(60, top-8, "+живлення", size=12, color=POS, anchor="start"))
    # Земля
    f.append(line(60, bot, 700, bot, color=NEG, sw=2))
    f.append(text(60, bot+18, "земля", size=12, color=NEG, anchor="start"))

    # Дільник зміщення R1 (верх) і R2 (низ); їхній спільний вузол — M (середина).
    basey = 210
    midy = basey
    f.append(rect(railx-18, 110, 36, 60, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(railx+26, 140, "R1", size=13, anchor="start"))
    f.append(line(railx, top, railx, 110, color=INK, sw=2))
    f.append(line(railx, 170, railx, midy, color=INK, sw=2))       # R1 → вузол M
    f.append(rect(railx-18, 250, 36, 60, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(railx+26, 280, "R2", size=13, anchor="start"))
    f.append(line(railx, midy, railx, 250, color=INK, sw=2))       # M → R2
    f.append(line(railx, 310, railx, bot, color=INK, sw=2))        # R2 → земля
    f.append(circle(railx, midy, 4, fill=INK, stroke=INK))
    f.append(text(railx-12, midy-8, "M", size=12, color=FIELD, anchor="end"))

    # Транзистор-повторювач (спрощено): база зліва, колектор вгору, емітер вниз.
    # R3 — послідовний резистор від вузла M до бази (через нього й діє бутстреп).
    tx = 340
    f.append(rect(railx+40, basey-15, 70, 30, fill=FILL, stroke=LINE, sw=1.8))  # R3
    f.append(text(railx+75, basey-22, "R3", size=12))
    f.append(line(railx, basey, railx+40, basey, color=INK, sw=2))
    f.append(circle(tx, basey, 34, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text(tx, basey-4, "Q", size=16, bold=True))
    f.append(line(railx+110, basey, tx-34, basey, color=INK, sw=2))  # R3 → база
    f.append(text((railx+110+tx)/2, basey-10, "база", size=11, color=MUTED))
    f.append(line(tx, basey-34, tx, top, color=INK, sw=2))         # колектор до живлення
    emy = 285
    f.append(line(tx, basey+34, tx, emy, color=INK, sw=2))         # емітер вниз
    f.append(circle(tx, emy, 4, fill=INK, stroke=INK))
    f.append(text(tx+12, emy-6, "вихід (емітер)", size=12, color=FIELD, anchor="start"))
    # Емітерний резистор до землі
    f.append(rect(tx-18, 310, 36, 30, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(tx+26, 330, "Re", size=12, anchor="start"))
    f.append(line(tx, emy, tx, 310, color=INK, sw=2))
    f.append(line(tx, 340, tx, bot, color=INK, sw=2))

    # Бутстреп-конденсатор Cb: переносить копію виходу (емітера) на вузол M дільника.
    # Маршрут: від M угору понад R1 і праворуч до вертикального конденсатора (x=cbx),
    # далі вниз у вузол емітера (вихід). Усе вище землі-шини, без помилкових з'єднань.
    topy = 92                      # горизонтальний відрізок над R1
    cbx = 420                      # колонка конденсатора, праворуч від транзистора
    f.append(line(railx, midy, 78, midy, color=FIELD, sw=2))      # M ліворуч
    f.append(line(78, midy, 78, topy, color=FIELD, sw=2))         # угору, обходимо R1
    f.append(line(78, topy, cbx, topy, color=FIELD, sw=2))        # понад усім до колонки
    f.append(line(cbx, topy, cbx, 150, color=FIELD, sw=2))        # вниз до верхньої пластини
    # пластини конденсатора (горизонтальні)
    f.append(line(cbx-14, 150, cbx+14, 150, color=FIELD, sw=3))
    f.append(line(cbx-14, 162, cbx+14, 162, color=FIELD, sw=3))
    f.append(text(cbx+22, 158, "Cb", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(cbx+22, 176, "(бутстреп)", size=11, color=FIELD, anchor="start"))
    f.append(line(cbx, 162, cbx, emy, color=FIELD, sw=2))         # нижня пластина вниз
    f.append(line(cbx, emy, tx, emy, color=FIELD, sw=2))          # у вузол емітера (вихід)

    # Підпис-висновок
    box = fitbox(470, 120, 250, 120,
                 "Вихід майже дорівнює входу (A≈1).\nCb переносить цю копію на низ\nдільника → на R1 та R2 падає\nмайже нуль сигналу → струму\nкрізь них майже нема → опір\nздається у 1/(1−A) раз більшим.",
                 size=12, fill="#f0fbf4", stroke=FIELD)
    f.append(box)

    render(os.path.join(IMG, 'follower.svg'), W, H, *f)


def fig_highside():
    """Бутстреп-конденсатор у драйвері верхнього ключа: заряджається внизу, їде над шиною."""
    W, H = 760, 420
    f = []
    f.append(text(W/2, 26, "Бутстреп-конденсатор живить керування верхнім ключем", size=16, bold=True))

    vp = 70; gnd = 380
    midx = 430                # півмостова точка SW (виток верхнього ключа)
    f.append(line(60, vp, 700, vp, color=POS, sw=2))
    f.append(text(60, vp-8, "+V (шина)", size=12, color=POS, anchor="start"))
    f.append(line(60, gnd, 700, gnd, color=NEG, sw=2))
    f.append(text(60, gnd+18, "земля", size=12, color=NEG, anchor="start"))

    # Верхній ключ (high-side)
    hs_y = 150
    f.append(rect(midx-22, hs_y-30, 44, 60, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(midx, hs_y, "верх", size=12, bold=True))
    f.append(line(midx, vp, midx, hs_y-30, color=INK, sw=2))
    # Нижній ключ (low-side)
    ls_y = 300
    f.append(rect(midx-22, ls_y-30, 44, 60, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(midx, ls_y, "низ", size=12, bold=True))
    f.append(line(midx, ls_y+30, midx, gnd, color=INK, sw=2))
    # Точка SW
    swy = (hs_y+30+ls_y-30)/2
    f.append(line(midx, hs_y+30, midx, ls_y-30, color=INK, sw=2))
    f.append(circle(midx, swy, 4, fill=INK, stroke=INK))
    f.append(text(midx+14, swy+4, "SW (виток верху)", size=12, color=INK, anchor="start"))
    f.append(text(midx+14, swy+24, "стрибає 0 → +V", size=11, color=MUTED, anchor="start"))

    # Діод бутстрепа Db: з вузла «живлення керування Vcc» у верх конденсатора
    vccx = 150
    f.append(text(vccx, vp-8, "Vcc керування", size=12, color=FIELD, anchor="middle") if False else "")
    f.append(line(vccx, vp, vccx, 110, color=FIELD, sw=2))
    f.append(text(vccx, vp-8, "Vcc", size=12, color=FIELD))
    # діод (трикутник + риска), вістрям праворуч
    dx = vccx; dy = 130
    f.append('<path d="M %d %d L %d %d L %d %d z" fill="#eafaf1" stroke="%s" stroke-width="1.8"/>' %
             (dx-10, dy-12, dx-10, dy+12, dx+10, dy, FIELD))
    f.append(line(dx+10, dy-12, dx+10, dy+12, color=FIELD, sw=3))
    f.append(text(dx-22, dy, "Db", size=12, color=FIELD, anchor="end"))
    f.append(line(vccx, 110, vccx, dy-12, color=FIELD, sw=2))
    topcb = 170
    f.append(line(vccx, dy+12, vccx, topcb, color=FIELD, sw=2))

    # Конденсатор бутстрепа Cb: між верхньою лінією керування і SW
    cbx = 280
    f.append(line(vccx, topcb, cbx, topcb, color=FIELD, sw=2))
    # верхня пластина (вузол VB — живлення верхнього драйвера)
    f.append(line(cbx, topcb-16, cbx, topcb+16, color=FIELD, sw=3))
    f.append(line(cbx+12, topcb-16, cbx+12, topcb+16, color=FIELD, sw=3))
    f.append(text(cbx+6, topcb-24, "Cb", size=13, color=FIELD, bold=True))
    # нижня пластина йде на SW
    f.append(line(cbx+12, topcb, cbx+12, swy, color=FIELD, sw=2))
    f.append(line(cbx+12, swy, midx, swy, color=FIELD, sw=2))

    # Верхній вузол VB живить драйвер верхнього ключа (стрілка до затвора)
    f.append(mtext(cbx-18, topcb+38, ["VB живить", "драйвер верху"], size=11, color=FIELD, anchor="end"))
    f.append(arrow(cbx, topcb+12, midx-26, hs_y-6, color=FIELD, sw=1.8))

    # Пояснення двох фаз праворуч
    f.append(fitbox(520, 90, 210, 110,
                    "Фаза 1: низ увімкнено,\nSW = 0. Db проводить,\nCb заряджається до Vcc\nзнизу (як батарейка).",
                    size=12, fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(520, 230, 210, 130,
                    "Фаза 2: верх увімкнено,\nSW злітає до +V. Cb їде\nразом, тож VB = +V + Vcc —\nкерування над шиною. Db\nзамкнено, Cb тримає заряд.",
                    size=12, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, 'highside.svg'), W, H, *f)


def fig_zin_node():
    """Серце виведення: на R3 падає лише u·(1−A), тож струм у (1−A) раз менший → Z = R/(1−A)."""
    W, H = 720, 360
    f = []
    f.append(text(W/2, 28, "Чому видимий опір = R/(1−A): рахуємо струм крізь R", size=16, bold=True))

    # Лівий вузол — вхід (база), напруга u. Правий вузол — M, напруга A·u.
    yb = 170
    xin = 150
    xm = 530
    # вхідний вузол
    f.append(circle(xin, yb, 5, fill=INK, stroke=INK))
    f.append(text(xin, yb-46, "вхід (база)", size=13, color=INK))
    f.append(text(xin, yb-26, "u", size=18, color=POS, bold=True))
    # стрілка-генератор сигналу знизу
    f.append(line(xin, yb, xin, yb+90, color=INK, sw=2))
    f.append(circle(xin, yb+118, 28, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(xin, yb+124, "~", size=26, color=INK, bold=True))
    f.append(text(xin, yb+162, "джерело сигналу", size=11, color=MUTED))

    # резистор R3 між вузлами
    f.append(line(xin, yb, xin+95, yb, color=INK, sw=2))
    f.append(rect(xin+95, yb-16, 90, 32, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(xin+140, yb+5, "R", size=16, bold=True))
    f.append(line(xin+185, yb, xm, yb, color=INK, sw=2))

    # вузол M, напруга A·u (копія виходу, привезена бутстрепом)
    f.append(circle(xm, yb, 5, fill=FIELD, stroke=FIELD))
    f.append(text(xm, yb-46, "вузол M (низ дільника)", size=13, color=FIELD))
    f.append(text(xm, yb-26, "A·u", size=18, color=FIELD, bold=True))
    # знизу — Cb привозить копію виходу
    f.append(line(xm, yb, xm, yb+70, color=FIELD, sw=2))
    f.append(line(xm-16, yb+70, xm+16, yb+70, color=FIELD, sw=3))
    f.append(line(xm-16, yb+82, xm+16, yb+82, color=FIELD, sw=3))
    f.append(text(xm+24, yb+80, "Cb", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(line(xm, yb+82, xm, yb+125, color=FIELD, sw=2))
    f.append(mtext(xm, yb+150, ["копія виходу", "≈ A·u"], size=11, color=FIELD))

    # Напруга на R: різниця кінців
    f.append(text((xin+xm)/2, yb-30, "на R падає лише", size=12, color=MUTED))
    f.append(text((xin+xm)/2, yb-50, "u − A·u = u·(1−A)", size=15, color=POS, bold=True))

    # Висновок-рамка
    f.append(fitbox(250, yb+62, 230, 78,
                    "i = u·(1−A) / R\nZ = u / i = R / (1−A)\nкінці майже рівні → i крихітний\n→ опір здається величезним",
                    size=12, fill="#f0fbf4", stroke=FIELD))

    render(os.path.join(IMG, 'zin_node.svg'), W, H, *f)


def fig_zin_freq():
    """Видимий опір — смугове явище: на басах Cb розриває бутстреп, на верхах паразити з'їдають A."""
    W, H = 760, 380
    f = []
    f.append(text(W/2, 26, "Видимий вхідний опір залежить від частоти (смуга бутстрепа)", size=15, bold=True))

    # осі
    x0, x1 = 90, 690
    y0, y1 = 320, 70          # y0 — низ (малий опір), y1 — верх (плато)
    f.append(line(x0, y0, x1, y0, color=INK, sw=2))        # вісь частоти
    f.append(line(x0, y0, x0, y1-6, color=INK, sw=2))      # вісь опору
    f.append(text(x1, y0+22, "частота (лог)", size=12, color=INK, anchor="end"))
    f.append(mtext(x0-12, (y0+y1)/2, ["видимий", "опір Z", "(лог)"], size=12, color=INK, anchor="end"))

    # рівні: низ = R∥(R1∥R2) без бутстрепа; плато = R/(1−A)
    ylow = y0 - 35
    yhi = y1 + 30
    f.append(line(x0, ylow, x1, ylow, color=MUTED, sw=1, dash="5 5"))
    f.append(text(x1, ylow-8, "без бутстрепа: ~R∥(R1∥R2)", size=11, color=MUTED, anchor="end"))
    f.append(line(x0, yhi, x1, yhi, color=FIELD, sw=1, dash="5 5"))
    f.append(text(x0+8, yhi-8, "плато бутстрепа: R/(1−A)", size=12, color=FIELD, anchor="start"))

    # крива: росте від ylow до плато (нижній злам fL), тримає плато, спадає на верхах (fH)
    xL = 230      # нижня гранична (заряд Cb)
    xH = 560      # верхня гранична (паразити, спад A)
    pts = [
        (x0, ylow), (xL-40, ylow),
        (xL+40, yhi), (xH-40, yhi),     # підйом і плато
        (xH+90, ylow+8), (x1, ylow+22)  # спад на верхах
    ]
    d = "M %.0f %.0f" % pts[0]
    # плавна полілінія через прості сегменти
    d += " L %.0f %.0f" % pts[1]
    d += " Q %.0f %.0f %.0f %.0f" % (xL, ylow, pts[2][0], pts[2][1])
    d += " L %.0f %.0f" % pts[3]
    d += " Q %.0f %.0f %.0f %.0f" % (xH, yhi, pts[4][0], pts[4][1])
    d += " L %.0f %.0f" % pts[5]
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, POS))

    # позначки граничних частот
    f.append(line(xL, y0, xL, y1+10, color=NEG, sw=1, dash="3 4"))
    f.append(mtext(xL, y0+20, ["fL — мала Cb", "«з'їдає баси»"], size=11, color=NEG))
    f.append(line(xH, y0, xH, y1+10, color=NEG, sw=1, dash="3 4"))
    f.append(mtext(xH, y0+20, ["fH — паразити", "тиснуть A вниз"], size=11, color=NEG))

    # пояснення зон
    f.append(mtext((xL+xH)/2, yhi-26, ["тут бутстреп працює:", "обидва кінці їдуть разом"], size=11, color=FIELD))

    render(os.path.join(IMG, 'zin_freq.svg'), W, H, *f)


if __name__ == '__main__':
    fig_idea()
    fig_follower()
    fig_highside()
    fig_zin_node()
    fig_zin_freq()
    print("ok: idea.svg, follower.svg, highside.svg, zin_node.svg, zin_freq.svg")
