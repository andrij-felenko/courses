# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#b87333"   # мідь майданчиків/виводів
SOLDER = "#9aa3ad"   # припій
BOARD  = "#cfe3cf"   # тіло плати (склотекстоліт)
BODY   = "#3a3f44"   # корпус деталі


# ── joint-anatomy: розріз THT- і SMD-з'єднання поруч ───────────────────────────
# Ідея: показати, ЧОМУ дві родини монтажу різні. THT прошиває плату й паяється
# знизу галтеллю (струм + механіка); SMD лежить на майданчику й тримається лише
# припоєм згори, того самого боку. Звідси дрібність SMD і його залежність від
# однієї тонкої зони припою.
def fig_joint_anatomy():
    W, H = 760, 400
    p = []

    def board_slab(x0, x1, ytop, h):
        return rect(x0, ytop, x1 - x0, h, fill=BOARD, stroke="#7fae7f", sw=1.5, rx=3)

    # ----- ліва половина: THT -----
    cx = 195
    bx0, bx1 = 60, 330
    btop, bh = 200, 46
    p.append(text(cx, 56, "THT — наскрізний монтаж", size=15, bold=True))
    p.append(board_slab(bx0, bx1, btop, bh))
    # металізований отвір (стінки)
    holex = cx
    hw = 16
    p.append(rect(holex - hw/2, btop, hw, bh, fill=BG, stroke=COPPER, sw=2.4, rx=0))
    # вивід деталі крізь отвір
    leadw = 7
    p.append(rect(holex - leadw/2, 110, leadw, btop + bh + 30 - 110, fill=COPPER, stroke="#8a561f", sw=1.2, rx=2))
    # тіло деталі зверху
    p.append(rect(cx - 70, 84, 140, 30, fill=BODY, stroke="#1f2225", sw=1.5, rx=5))
    p.append(text(cx, 104, "деталь", size=12, color="#ffffff"))
    # галтель припою з обох боків (низ — більша)
    p.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f L %.1f %.1f Q %.1f %.1f %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.2"/>' % (
        holex - hw/2 - 22, btop + bh, holex - 3, btop + bh + 28, holex - leadw/2, btop + bh + 30,
        holex + leadw/2, btop + bh + 30, holex + 3, btop + bh + 28, holex + hw/2 + 22, btop + bh, SOLDER, "#6b7280"))
    # верхня галтель (менша)
    p.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f L %.1f %.1f Q %.1f %.1f %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.0"/>' % (
        holex - hw/2 - 12, btop, holex - 3, btop - 10, holex - leadw/2, btop - 11,
        holex + leadw/2, btop - 11, holex + 3, btop - 10, holex + hw/2 + 12, btop, SOLDER, "#6b7280"))
    # підписи
    p.append(line(holex + hw/2 + 22, btop + bh + 20, bx1 + 26, btop + bh + 20, color=MUTED, sw=1.0))
    b, _, _ = textbox(bx1 + 70, btop + bh + 20, "галтель\nзнизу", size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.0, pad=5)
    p.append(b)
    p.append(line(holex + hw/2, btop + bh/2, bx1 + 26, btop + bh/2, color=MUTED, sw=1.0, dash="3 3"))
    b, _, _ = textbox(bx1 + 78, btop + bh/2, "металіз.\nотвір", size=10, color="#8a561f", fill="#ffffff", stroke=COPPER, sw=1.0, pad=5)
    p.append(b)
    p.append(text(cx, btop + bh + 64, "паяють із ЗВОРОТНОГО боку", size=11, color=MUTED))
    p.append(text(cx, btop + bh + 80, "припій тримає + проводить", size=11, color=FIELD, bold=True))

    # роздільник
    p.append(line(W/2, 70, W/2, H - 30, color="#d0d4d8", sw=1.4, dash="6 5"))

    # ----- права половина: SMD -----
    cx2 = 565
    bx0b, bx1b = 430, 700
    p.append(text(cx2, 56, "SMD — поверхневий монтаж", size=15, bold=True))
    p.append(board_slab(bx0b, bx1b, btop, bh))
    # два мідні майданчики згори
    padw, padg = 56, 70
    padL = cx2 - padg/2 - padw
    padR = cx2 + padg/2
    pady = btop - 8
    for px in (padL, padR):
        p.append(rect(px, pady, padw, 8, fill=COPPER, stroke="#8a561f", sw=1.0, rx=1))
    # корпус деталі лежить на майданчиках
    p.append(rect(cx2 - 64, pady - 34, 128, 30, fill=BODY, stroke="#1f2225", sw=1.5, rx=5))
    p.append(text(cx2, pady - 14, "деталь", size=12, color="#ffffff"))
    # виводи-торці (end caps) і галтель припою лише згори
    for px, sgn in ((padL, -1), (padR, +1)):
        cap_x = cx2 + sgn * 64
        # галтель припою між торцем корпусу й майданчиком
        if sgn < 0:
            x_in, x_out = px + 6, cap_x
        else:
            x_in, x_out = cap_x, px + padw - 6
        p.append('<path d="M%.1f %.1f L %.1f %.1f Q %.1f %.1f %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.0"/>' % (
            (cap_x), pady - 30, (cap_x), pady,
            (px + padw/2 + sgn*8), pady, (px + padw/2 + sgn*padw/2), pady, SOLDER, "#6b7280"))
    # підпис: усе з ОДНОГО боку
    p.append(line(padR + padw/2, pady + 2, bx1b + 4, pady + 2, color=MUTED, sw=1.0))
    b, _, _ = textbox(bx1b + 38, pady - 6, "припій\nлише\nзгори", size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.0, pad=5)
    p.append(b)
    p.append(text(cx2, btop + bh + 30, "немає отворів — лежить на майданчиках", size=11, color=MUTED))
    p.append(text(cx2, btop + bh + 48, "уся надійність — у тонкій зоні припою", size=11, color=POS, bold=True))
    p.append(text(cx2, btop + bh + 66, "дрібніше · щільніше · краще на ВЧ", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "joint-anatomy.svg"), W, H, *p)


# ── mixed-flow: маршрут змішаного монтажу (SMD оплавленням → THT окремо) ───────
# Ідея: показати ПОРЯДОК і його причину. Гаряча піч для всього SMD проходить
# РАНІШЕ, поки на платі ще немає чутливих до тепла THT-деталей; THT додають
# після — хвилею у серії або руками, коли їх одиниці. Порядок диктує температура.
def fig_mixed_flow():
    W, H = 780, 360
    p = []
    p.append(text(W/2, 30, "Маршрут плати: спершу все SMD, потім THT", size=15, bold=True))

    # верхній ряд: ланцюг SMD-оплавлення
    y1 = 110
    boxw, boxh = 132, 66
    gap = 28
    smd = [
        ("1. Паста", "трафарет\nна всі майданчики"),
        ("2. Установка", "деталі на пасту\n(pick-and-place)"),
        ("3. Піч", "оплавлення —\nуся плата за раз"),
    ]
    x = 40
    centers = []
    for i, (t, s) in enumerate(smd):
        fill = "#fdecea" if i == 2 else "#eaf0fd"
        stroke = POS if i == 2 else NEG
        p.append(rect(x, y1, boxw, boxh, fill=fill, stroke=stroke, sw=1.8, rx=8))
        p.append(text(x + boxw/2, y1 + 22, t, size=12, bold=True, color=INK))
        p.append(mtext(x + boxw/2, y1 + 40, s, size=9.5, color=MUTED))
        centers.append((x + boxw/2, x + boxw, y1 + boxh/2))
        if i < len(smd) - 1:
            p.append(arrow(x + boxw + 4, y1 + boxh/2, x + boxw + gap - 4, y1 + boxh/2, color=LINE, sw=1.8))
        x += boxw + gap
    # дужка над рядом SMD
    p.append(text(40 + (3*boxw + 2*gap)/2, y1 - 16, "ВСЕ SMD — оплавленням (гаряча піч)", size=11, color=NEG, bold=True))

    # стрілка вниз із приміткою «порядок диктує температура»
    midx = x - boxw - gap + boxw/2  # центр останнього SMD-блока (піч)
    downx = midx
    p.append(arrow(downx, y1 + boxh + 6, downx, y1 + boxh + 52, color=LINE, sw=2.0))
    b, _, _ = textbox(downx + 150, y1 + boxh + 30, "THT заходять ПІСЛЯ печі:\nте, що не любить жар, —\nне в духовку", size=10, color=INK, fill=FILL, stroke="#e0a800", sw=1.4, pad=8)
    p.append(b)

    # нижній ряд: дві гілки THT
    y2 = y1 + boxh + 64
    # блок THT
    tx = downx - boxw/2
    p.append(rect(tx, y2, boxw, boxh, fill="#fef9e7", stroke="#caa700", sw=1.8, rx=8))
    p.append(text(tx + boxw/2, y2 + 22, "4. THT", size=12, bold=True, color=INK))
    p.append(mtext(tx + boxw/2, y2 + 40, "роз'єми, клеми,\nелектроліти", size=9.5, color=MUTED))

    # дві гілки виходу
    by = y2 + boxh/2
    # хвиля (серія)
    p.append(arrow(tx + boxw + 4, by, tx + boxw + 60, by - 26, color=LINE, sw=1.6))
    b, _, _ = textbox(tx + boxw + 150, by - 30, "хвилею —\nвелика серія", size=10, color=INK, fill="#ffffff", stroke=FIELD, sw=1.3, pad=6)
    p.append(b)
    # руками (мало)
    p.append(arrow(tx + boxw + 4, by, tx + boxw + 60, by + 26, color=LINE, sw=1.6))
    b, _, _ = textbox(tx + boxw + 150, by + 30, "руками —\nколи їх одиниці", size=10, color=INK, fill="#ffffff", stroke=FIELD, sw=1.3, pad=6)
    p.append(b)

    render(os.path.join(OUT, "mixed-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_joint_anatomy()
    fig_mixed_flow()
    print("figs done:", os.listdir(OUT))
