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
    fig_whisker()
    print("figs done")
