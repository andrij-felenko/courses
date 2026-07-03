# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#c9971e"     # припій
COPPER = "#b26b3a"   # мідь площадки
LEAD = "#8a8f98"     # вивід/нога компонента
IMC = "#7a5230"      # інтерметалевий шар


# ── Фігура 1: добрий шов проти холодного ─────────────────────────────────────
def fig_joint():
    W, H = 720, 400
    frags = []

    # спільний рівень плати
    board_y = 300
    # ── Ліворуч: ДОБРИЙ шов (увігнута галтель, малий кут змочування) ──
    cx = 200
    # площадка (мідь) на платі
    frags.append(rect(cx - 95, board_y, 190, 22, fill=COPPER, stroke=INK, sw=1.2, rx=2))
    # вивід компонента (вертикальна нога крізь отвір)
    frags.append(rect(cx - 8, 120, 16, board_y - 120 + 22, fill=LEAD, stroke=INK, sw=1.2, rx=2))
    # припій — увігнута галтель: два трикутні схили від ноги до країв площадки
    frags.append('<path d="M %d %d L %d %d Q %d %d %d %d Z" fill="%s" stroke="%s" stroke-width="1.4"/>'
                 % (cx - 8, 220, cx - 8, board_y, cx - 80, board_y - 8, cx - 80, board_y, GOLD, INK))
    frags.append('<path d="M %d %d L %d %d Q %d %d %d %d Z" fill="%s" stroke="%s" stroke-width="1.4"/>'
                 % (cx + 8, 220, cx + 8, board_y, cx + 80, board_y - 8, cx + 80, board_y, GOLD, INK))
    # тонкий інтерметалевий прошарок на межі припій-мідь
    frags.append(line(cx - 80, board_y, cx + 80, board_y, color=IMC, sw=3))
    # кут змочування — гострий, позначка
    frags.append(text(cx - 70, board_y - 20, "θ мале", size=13, color=FIELD, bold=True))
    frags.append(text(cx, 105, "вивід", size=13, color=MUTED))
    b, bw, bh = textbox(cx, 360, "ДОБРИЙ ШОВ\nувігнута галтель, блиск", size=13, bold=True,
                        fill="#eafaf0", stroke=FIELD)
    frags.append(b)

    # ── Праворуч: ХОЛОДНИЙ шов (кулька, припій не змочив) ──
    dx = 520
    frags.append(rect(dx - 95, board_y, 190, 22, fill=COPPER, stroke=INK, sw=1.2, rx=2))
    frags.append(rect(dx - 8, 120, 16, board_y - 120 + 22, fill=LEAD, stroke=INK, sw=1.2, rx=2))
    # припій — кулька, що облягає ногу, але НЕ розтеклась по площадці (опуклий, тупий кут)
    frags.append('<ellipse cx="%d" cy="%d" rx="46" ry="40" fill="%s" stroke="%s" stroke-width="1.4"/>'
                 % (dx, board_y - 18, GOLD, INK))
    # видима щілина між кулькою і міддю — немає інтерметалевого зчеплення
    frags.append(line(dx - 46, board_y + 6, dx + 46, board_y + 6, color=POS, sw=2.5, dash="4,3"))
    frags.append(text(dx + 96, board_y + 8, "щілина", size=12, color=POS, bold=True, anchor="start"))
    frags.append(text(dx + 62, board_y - 34, "θ велике", size=13, color=POS, bold=True, anchor="start"))
    frags.append(text(dx, 105, "вивід", size=13, color=MUTED))
    b, bw, bh = textbox(dx, 360, "ХОЛОДНИЙ ШОВ\nкулька, тьмяний, не зчепився", size=13, bold=True,
                        fill="#fdecea", stroke=POS)
    frags.append(b)

    # легенда інтерметалу
    frags.append(line(300, 70, 340, 70, color=IMC, sw=3))
    frags.append(text(348, 74, "інтерметалевий шар — метал зрісся з міддю", size=12,
                      color=INK, anchor="start"))

    render(os.path.join(IMG, 'joint.svg'), W, H, *frags,
           title="Що таке паяний шов: змочування проти кульки")


# ── Фігура 2: теплове рукостискання ─────────────────────────────────────────
def fig_heat():
    W, H = 720, 380
    frags = []
    board_y = 260

    # площадка + вивід
    frags.append(rect(250, board_y, 200, 22, fill=COPPER, stroke=INK, sw=1.2, rx=2))
    frags.append(rect(342, 150, 16, board_y - 150 + 22, fill=LEAD, stroke=INK, sw=1.2, rx=2))
    frags.append(text(350, 140, "вивід + площадка", size=13, color=MUTED))

    # жало паяльника торкається ОБОХ одночасно — з одного боку
    tip = ('<path d="M 120 %d L 300 %d L 300 %d L 150 %d Z" fill="#d8dde3" '
           'stroke="%s" stroke-width="1.4"/>' % (board_y - 60, board_y - 6, board_y + 14, board_y - 40, INK))
    frags.append(tip)
    frags.append(text(175, board_y - 60, "жало", size=14, color=INK, bold=True))
    # точка контакту жала одразу з ногою і площадкою
    frags.append(circle(320, board_y, 7, fill=POS, stroke=POS))
    frags.append(text(300, board_y + 40, "жало гріє ногу Й площадку разом", size=12,
                      color=POS, anchor="middle"))

    # припій підводять з ПРОТИЛЕЖНОГО боку, до з'єднання (не до жала)
    frags.append(line(560, board_y - 70, 400, board_y - 6, color=GOLD, sw=6))
    frags.append(text(575, board_y - 74, "припій —", size=13, color=INK, bold=True, anchor="start"))
    frags.append(text(575, board_y - 56, "у шов, не на жало", size=13, color=INK, anchor="start"))
    frags.append(circle(398, board_y - 4, 6, fill=GOLD, stroke=INK))

    # стрілки тепла в обидві деталі
    frags.append(arrow(325, board_y - 4, 345, board_y - 40, color=POS))
    frags.append(arrow(330, board_y + 6, 410, board_y + 10, color=POS))
    frags.append(text(430, board_y + 12, "тепло", size=12, color=POS, anchor="start"))

    b, bw, bh = textbox(360, 340,
                        "Порядок: спершу нагріти деталі ~1 с, тоді торкнути припоєм ШВА — він сам затече",
                        size=13, bold=True, fill="#fff7e6", stroke=GOLD, min_w=560)
    frags.append(b)

    render(os.path.join(IMG, 'heat.svg'), W, H, *frags,
           title="Теплове рукостискання: гріємо деталі, не припій")


# ── Фігура 3: фазова діаграма Sn-Pb (для вставки math-eutectic) ──────────────
def fig_phase():
    W, H = 760, 470
    frags = []

    # осі: X — % олова (0..100), Y — температура (°C, 130..340)
    x0, x1 = 90, 690          # ліва/права межа поля даних
    y0, y1 = 410, 70          # низ/верх поля (y росте вниз, тому y0>y1)
    Tmin, Tmax = 130, 340
    Smin, Smax = 0, 100       # % Sn

    def X(sn):  # % олова -> піксель X
        return x0 + (sn - Smin) / (Smax - Smin) * (x1 - x0)
    def Y(T):   # °C -> піксель Y
        return y0 + (T - Tmin) / (Tmax - Tmin) * (y1 - y0)

    # рамка поля
    frags.append(rect(x0, y1, x1 - x0, y0 - y1, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=2))

    # горизонтальні сітки-температури з підписами
    for T in (150, 183, 200, 250, 300):
        yy = Y(T)
        col = POS if T == 183 else "#e6e9ee"
        sw = 1.6 if T == 183 else 1.0
        dash = "5,4" if T == 183 else None
        frags.append(line(x0, yy, x1, yy, color=col, sw=sw, dash=dash))
        frags.append(text(x0 - 8, yy + 4, "%d" % T, size=12, color=(POS if T == 183 else MUTED), anchor="end"))
    # вісь X — підписи складу
    for sn in (0, 20, 40, 60, 63, 80, 100):
        xx = X(sn)
        frags.append(line(xx, y0, xx, y0 + 5, color=MUTED, sw=1.0))
        lbl = "63" if sn == 63 else "%d" % sn
        frags.append(text(xx, y0 + 20, lbl, size=11, color=(FIELD if sn == 63 else MUTED)))
    frags.append(text((x0 + x1) / 2, y0 + 42, "% олова (решта — свинець) →", size=13, color=INK))
    frags.append(text(x0 - 60, (y0 + y1) / 2, "T, °C", size=13, color=INK))

    # координати ключових точок
    Pb_mp, Sn_mp, eut_T, eut_sn = 327.0, 232.0, 183.0, 63.0

    # ЛІКВІДУС: від т.пл. свинцю (0% Sn) вниз до евтектики, тоді вгору до т.пл. олова
    liq = [(0, Pb_mp), (20, 280), (40, 238), (eut_sn, eut_T), (80, 205), (100, Sn_mp)]
    pts = " ".join("%.1f,%.1f" % (X(s), Y(T)) for s, T in liq)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (pts, NEG))

    # СОЛІДУС: горизонталь евтектики на 183 між гілками розчинності + скошені краї
    # ліва межа розчинності Pb(Sn) ~ 19% Sn при евт., права Sn(Pb) ~ 97% Sn
    sol_left, sol_right = 19.0, 97.0
    frags.append(line(X(0), Y(Pb_mp), X(sol_left), Y(eut_T), color=INK, sw=2.0))
    frags.append(line(X(sol_left), Y(eut_T), X(sol_right), Y(eut_T), color=INK, sw=2.0))
    frags.append(line(X(sol_right), Y(eut_T), X(100), Y(Sn_mp), color=INK, sw=2.0))

    # евтектична точка
    ex, ey = X(eut_sn), Y(eut_T)
    frags.append(circle(ex, ey, 6, fill=FIELD, stroke=INK, sw=1.4))
    b, bw, bh = textbox(ex + 8, ey - 42, "евтектика\n63/37 · 183 °C", size=12, bold=True,
                        fill="#eafaf0", stroke=FIELD)
    frags.append(b)

    # позначки чистих металів
    frags.append(circle(X(0), Y(Pb_mp), 4, fill=NEG, stroke=INK, sw=1.0))
    frags.append(text(X(0) + 6, Y(Pb_mp) - 8, "Pb 327 °C", size=11, color=INK, anchor="start"))
    frags.append(circle(X(100), Y(Sn_mp), 4, fill=NEG, stroke=INK, sw=1.0))
    frags.append(text(X(100) - 6, Y(Sn_mp) - 8, "Sn 232 °C", size=11, color=INK, anchor="end"))

    # підписи областей фаз (кашоподібні — ЛІВОРУЧ від демо-лінії x=40%, щоб та не різала напис)
    frags.append(text(X(50), Y(320), "РІДИНА (розплав)", size=13, color=NEG, bold=True))
    frags.append(text(X(26), Y(206), "рідина + кристали", size=11, color=MUTED, anchor="end"))
    frags.append(text(X(26), Y(193), "(кашоподібна зона)", size=11, color=MUTED, anchor="end"))
    frags.append(text(X(50), Y(158), "ТВЕРДА суміш", size=13, color=INK, bold=True))

    # позначити «діапазон плавлення» для 40% Sn: вертикальний відрізок від солідуса(183) до лідуса
    sn_demo = 40.0
    yliq_demo = Y(238)   # лідус при 40% (з масиву вище)
    ysol_demo = Y(eut_T)
    frags.append(line(X(sn_demo), ysol_demo, X(sn_demo), yliq_demo, color=POS, sw=2.4, dash="3,3"))
    frags.append(circle(X(sn_demo), yliq_demo, 4, fill=POS, stroke=INK, sw=1.0))
    frags.append(circle(X(sn_demo), ysol_demo, 4, fill=POS, stroke=INK, sw=1.0))

    # легенда ліній
    frags.append(line(x0 + 470, y1 + 18, x0 + 500, y1 + 18, color=NEG, sw=2.4))
    frags.append(text(x0 + 506, y1 + 22, "лідус", size=11, color=INK, anchor="start"))
    frags.append(line(x0 + 470, y1 + 36, x0 + 500, y1 + 36, color=INK, sw=2.0))
    frags.append(text(x0 + 506, y1 + 40, "солідус", size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, 'phase.svg'), W, H, *frags,
           title="Фазова діаграма олово-свинець")


# ── Фігура 4: криві застигання — евтектика проти суміші ─────────────────────
def fig_cooling():
    W, H = 720, 380
    frags = []
    x0, x1 = 90, 660
    y0, y1 = 320, 70
    Tmin, Tmax = 150, 320
    tmin, tmax = 0, 100  # умовний час

    def X(t): return x0 + (t - tmin) / (tmax - tmin) * (x1 - x0)
    def Y(T): return y0 + (T - Tmin) / (Tmax - Tmin) * (y1 - y0)

    frags.append(rect(x0, y1, x1 - x0, y0 - y1, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=2))
    for T in (183, 200, 250, 300):
        yy = Y(T)
        col = POS if T == 183 else "#e6e9ee"
        frags.append(line(x0, yy, x1, yy, color=col, sw=(1.4 if T == 183 else 1.0),
                          dash=("5,4" if T == 183 else None)))
        frags.append(text(x0 - 8, yy + 4, "%d" % T, size=11,
                          color=(POS if T == 183 else MUTED), anchor="end"))
    frags.append(text((x0 + x1) / 2, y0 + 34, "час охолодження →", size=12, color=INK))
    frags.append(text(x0 - 58, (y0 + y1) / 2, "T, °C", size=12, color=INK))

    # ЕВТЕКТИКА: спад до 183, різка ПЛОЩАДКА, далі спад — як чистий метал
    eut = [(0, 300), (32, 183), (60, 183), (100, 165)]
    pts = " ".join("%.1f,%.1f" % (X(t), Y(T)) for t, T in eut)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, FIELD))
    frags.append(text(X(46), Y(183) - 10, "площадка — застигає ОДРАЗУ", size=11, color=FIELD, bold=True))
    # ідентифікатор кривої — у порожній смузі між 250 і 200 °C ліворуч (жодна гілка/сітка не ріже)
    b, bw, bh = textbox(X(11), Y(222), "63/37\nевтектика", size=12, bold=True,
                        fill="#eafaf0", stroke=FIELD)
    frags.append(b)

    # НЕЕВТЕКТИКА (напр. 40/60): злам на лідусі, ПОХИЛА ділянка (каша), тоді площадка на 183
    non = [(0, 300), (24, 238), (58, 183), (72, 183), (100, 165)]
    pts2 = " ".join("%.1f,%.1f" % (X(t), Y(T)) for t, T in non)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6,4"/>' % (pts2, POS))
    # позначити похилу кашоподібну ділянку
    frags.append(circle(X(24), Y(238), 4, fill=POS, stroke=INK, sw=1.0))
    frags.append(text(X(24) + 6, Y(238) - 6, "лідус: почалась каша", size=11, color=POS, anchor="start"))
    frags.append(circle(X(58), Y(183), 4, fill=POS, stroke=INK, sw=1.0))
    frags.append(text(X(58) + 8, Y(183) + 26, "солідус: тільки тут тверда", size=11, color=POS, anchor="start"))
    b2, bw2, bh2 = textbox(X(89), Y(222), "неевтектика\nдіапазон", size=12, bold=True,
                           fill="#fdecea", stroke=POS)
    frags.append(b2)

    render(os.path.join(IMG, 'cooling.svg'), W, H, *frags,
           title="Криві застигання: евтектика проти суміші")


# ── Фігура (вставка comp-tin-whiskers): механізм росту вуса ───────────────────
def fig_whisker():
    """Розріз покриття: мідь → інтерметалева кірка (качає стиск) → шар олова
    під окисною шкіркою → вус як клапан скидання тиску, що росте З КОРЕНЯ."""
    SN = "#c8ccd2"       # шар олова
    OXIDE = "#8f6fb0"    # окисна плівка на олові
    WHISK = "#dfe4ea"    # сам вус (світлий метал)
    W, H = 760, 470
    frags = []

    base_x, base_w = 120, 520
    cu_top = 360          # верх міді
    imc_top = 340         # верх інтерметалу (кірка між міддю й оловом)
    sn_top = 250          # верх олова
    ox_y = sn_top         # окисна плівка по верху олова

    # мідь (основа виводу)
    frags.append(rect(base_x, cu_top, base_w, 74, fill=COPPER, stroke=INK, sw=1.2, rx=2))
    frags.append(text(base_x + base_w - 10, cu_top + 44, "мідь виводу", size=13,
                      color="#3a2a1e", anchor="end", bold=True))

    # інтерметалева кірка Cu6Sn5 — зубчастий верх, росте від міді в олово
    imc = ['M %d %d' % (base_x, imc_top)]
    n = 13
    for i in range(1, n + 1):
        x = base_x + base_w * i / n
        y = imc_top - (9 if i % 2 else 2)
        imc.append('L %.1f %.1f' % (x, y))
    imc.append('L %d %d' % (base_x + base_w, cu_top + 2))
    imc.append('L %d %d Z' % (base_x, cu_top + 2))
    frags.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.1"/>'
                 % (' '.join(imc), IMC, INK))
    frags.append(text(base_x + 12, imc_top + 22, "інтерметал Cu₆Sn₅", size=12,
                      color="#f0e6da", anchor="start", bold=True))

    # шар олова
    frags.append(rect(base_x, sn_top, base_w, imc_top - sn_top, fill=SN,
                      stroke=INK, sw=1.2, rx=0))
    frags.append(text(base_x + base_w - 10, sn_top + 58, "шар олова", size=13,
                      color="#40454c", anchor="end", bold=True))

    # окисна плівка по верху олова, з РОЗРИВОМ під вусом
    wx = base_x + 190
    frags.append(line(base_x, ox_y, wx - 14, ox_y, color=OXIDE, sw=5))
    frags.append(line(wx + 14, ox_y, base_x + base_w, ox_y, color=OXIDE, sw=5))
    frags.append(text(base_x + base_w, ox_y - 12, "окисна плівка (тримає зверху)",
                      size=12, color=OXIDE, anchor="end", bold=True))

    # стрілки стиску всередині олова — назустріч
    for sx in (base_x + 360, base_x + 475):
        frags.append(arrow(sx - 28, sn_top + 40, sx - 5, sn_top + 40, color=POS))
        frags.append(arrow(sx + 28, sn_top + 40, sx + 5, sn_top + 40, color=POS))
    frags.append(text(base_x + 418, sn_top + 74, "стиск усередині шару", size=12,
                      color=POS, anchor="middle", bold=True))

    # дифузія міді вгору — джерело тиску
    frags.append(arrow(base_x + 300, cu_top + 32, base_x + 300, imc_top - 3, color=NEG))
    frags.append(text(base_x + 300, cu_top + 58, "мідь дифундує в олово → кірка пухне",
                      size=11, color=NEG, anchor="middle"))

    # ── ВУС: голка з кореня в розриві плівки ──
    root_y = ox_y
    tip_y = 72
    frags.append('<path d="M %d %d L %d %d L %d %d L %d %d Z" fill="%s" stroke="%s" '
                 'stroke-width="1.3"/>'
                 % (wx - 6, root_y, wx - 3, tip_y, wx + 3, tip_y, wx + 6, root_y,
                    WHISK, INK))
    frags.append(line(wx - 1, tip_y + 6, wx - 1, root_y - 4, color=MUTED, sw=0.8))
    frags.append(line(wx + 2, tip_y + 10, wx + 2, root_y - 4, color=MUTED, sw=0.8))
    frags.append(circle(wx, root_y, 6, fill=POS, stroke=POS))
    frags.append(arrow(wx - 44, root_y + 30, wx - 8, root_y + 4, color=POS))
    frags.append(text(wx - 50, root_y + 30, "росте З КОРЕНЯ:", size=12, color=POS,
                      anchor="end", bold=True))
    frags.append(text(wx - 50, root_y + 46, "олово підтікає знизу", size=12,
                      color=POS, anchor="end"))
    frags.append(arrow(wx, tip_y + 4, wx, tip_y - 22, color=INK))
    frags.append(text(wx, tip_y - 30, "вус (монокристал олова)", size=13,
                      color=INK, anchor="middle", bold=True))

    render(os.path.join(IMG, 'whisker.svg'), W, H, *frags,
           title="Олов'яний вус як клапан скидання внутрішнього тиску")


if __name__ == "__main__":
    fig_joint()
    fig_heat()
    fig_phase()
    fig_cooling()
    fig_whisker()
    print("figs done")
