# -*- coding: utf-8 -*-
"""Фігури до ДЕТАЛЬНОЇ статті «Первинне налаштування зблизька»
(root/course/embedded/fc-setup-calibration/fc-setup-calibration-d.md).
Чистий Python, без залежностей; svgkit — зі scripts/ (не переписувати).
Ці фігури НЕ дублюють figs.py базової статті — вони про глибший шар:
поворот осей, розкладання компасної поправки, поріг failsafe."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Орієнтація плати — це ПОВОРОТ (множення на матрицю), а не поправка на вісь.
#    Ліворуч: осі давача й осі апарата суміщає матриця R.
#    Праворуч: що робить НЕПРАВИЛЬНА орієнтація — тангаж читається як крен.
# ─────────────────────────────────────────────────────────────────────────────
def fig_orientation_rotation():
    W, H = 940, 470
    frags = [text(W / 2, 30, "Орієнтація плати — це поворот осей, а не поправка на кожну вісь", size=15, bold=True)]

    # ── Ліва панель: осі давача → матриця R → осі апарата ──
    frags.append(text(235, 66, "Суміщення систем координат", size=13, bold=True))

    # осі апарата (body): X вперед(вгору на схемі), Y вправо, Z вниз — намалюємо як «еталон»
    bx, by = 150, 200
    frags.append(text(bx, by - 96, "осі апарата (body)", size=11.5, bold=True, color=FIELD))
    frags.append(arrow(bx, by, bx, by - 72, color=FIELD, sw=2.4))       # X вперед (вгору)
    frags.append(text(bx - 16, by - 76, "X↑", size=11, color=FIELD, bold=True, anchor="end"))
    frags.append(arrow(bx, by, bx + 72, by, color=FIELD, sw=2.4))        # Y вправо
    frags.append(text(bx + 76, by + 4, "Y", size=11, color=FIELD, bold=True, anchor="start"))
    frags.append(circle(bx, by, 3, fill=FIELD, stroke=FIELD, sw=1))

    # осі давача (sensor): повернуті на Yaw90 (нахилені)
    sx, sy = 150, 350
    frags.append(text(sx, sy + 74, "осі давача (як лежить мікросхема)", size=11.5, bold=True, color=NEG))
    # давач повернутий: його «X» дивиться вправо, «Y» вгору (Yaw90)
    frags.append(arrow(sx, sy, sx + 66, sy - 30, color=NEG, sw=2.2))
    frags.append(text(sx + 70, sy - 32, "xₛ", size=11, color=NEG, bold=True, anchor="start"))
    frags.append(arrow(sx, sy, sx + 30, sy + 60, color=NEG, sw=2.2))
    frags.append(text(sx + 34, sy + 64, "yₛ", size=11, color=NEG, bold=True, anchor="start"))
    frags.append(circle(sx, sy, 3, fill=NEG, stroke=NEG, sw=1))

    # стрілка «×R» від давача до апарата
    frags.append(arrow(sx + 4, sy - 24, bx + 4, by + 40, color=INK, sw=2))
    body, bw, bh = textbox(300, 275, "a_body = R · a_sensor\nR — матриця повороту\n(дискретна, кратна 45°)",
                           size=11.5, pad=9, fill="#eef2f7", stroke=INK, sw=1.4)
    frags.append(body)

    # роздільник
    frags.append(line(470, 60, 470, H - 40, color=MUTED, sw=1, dash="4,4"))

    # ── Права панель: неправильна орієнтація — тангаж стає креном ──
    frags.append(text(705, 66, "Неправильна орієнтація отруює політ", size=13, bold=True))

    # апарат нахиляється ВПЕРЕД (тангаж) — а прошивка «бачить» нахил УБІК (крен)
    # верх: фізичний рух
    fy = 150
    frags.append(text(560, fy - 18, "фізично: ніс униз (тангаж)", size=11, color=INK, anchor="start"))
    # простий силует апарата в профіль, нахилений уперед
    frags.append('<path d="M540 %d L640 %d" stroke="%s" stroke-width="3"/>' % (fy + 8, fy + 26, INK))
    frags.append(arrow(590, fy + 4, 590, fy + 40, color=INK, sw=2))
    frags.append(text(596, fy + 30, "ніс", size=10, color=MUTED, anchor="start"))

    # низ: як це «бачить» прошивка з переплутаною орієнтацією
    py = 300
    frags.append(text(560, py - 26, "прошивка (R=None при Yaw90): нахил УБІК (крен)", size=11, color=POS, anchor="start"))
    frags.append('<path d="M560 %d L680 %d" stroke="%s" stroke-width="3"/>' % (py + 26, py + 4, POS))
    frags.append(arrow(620, py + 15, 660, py - 3, color=POS, sw=2))

    # висновок-рамка
    body2, bw2, bh2 = textbox(705, 405,
                              "Стабілізатор «виправляє» неіснуючий крен —\n"
                              "і вганяє апарат у реальний. «Злетів і перекинувся»\n"
                              "часто = переплутана AHRS_ORIENTATION.",
                              size=11, pad=10, fill="#fdecea", stroke=POS, sw=1.5)
    frags.append(body2)

    frags.append(text(W / 2, H - 14,
                      "Поворот множить, калібрування додає й масштабує — вони не комутують: спершу поправ давач у його осях, тоді поверни в осі апарата",
                      size=11.5, color=MUTED))
    render(os.path.join(IMG, 'orientation-rotation.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Розкладання компасної поправки на три незалежні дії:
#    (а) тверде залізо ЗСУВАЄ коло вимірів з центру (вектор b → COMPASS_OFS);
#    (б) м'яке залізо РОЗТЯГУЄ+ПОВЕРТАЄ його в еліпс (матриця → DIA+ODI);
#    (в) схилення ПОВЕРТАЄ вже чистий курс з магнітної півночі на справжню.
# ─────────────────────────────────────────────────────────────────────────────
def fig_compass_decomposition():
    import math as m
    W, H = 960, 430
    frags = [text(W / 2, 30, "Три дії компасної поправки: зсув, форма, схилення", size=15, bold=True)]

    def axes(cx, cy, r):
        f = [line(cx - r - 14, cy, cx + r + 14, cy, color=MUTED, sw=1),
             line(cx, cy - r - 14, cx, cy + r + 14, color=MUTED, sw=1),
             circle(cx, cy, 2.5, fill=MUTED, stroke=MUTED, sw=1)]
        return f

    def circ_points(cx, cy, r, n=16, ox=0.0, oy=0.0, sx=1.0, sy=1.0, rot=0.0, col=POS):
        f = []
        for k in range(n):
            a = 2 * m.pi * k / n
            # точка на одиничному колі → масштаб → поворот → зсув центру
            px, py = m.cos(a) * r * sx, m.sin(a) * r * sy
            rx = px * m.cos(rot) - py * m.sin(rot)
            ry = px * m.sin(rot) + py * m.cos(rot)
            f.append(circle(cx + ox + rx, cy + oy + ry, 3.0, fill="#fdecea", stroke=col, sw=1.4))
        return f

    R = 58
    y0 = 150

    # (а) тверде залізо: коло, зсунуте від центру на вектор b
    cx = 150
    frags.append(text(cx, 70, "тверде залізо", size=12.5, bold=True, color=NEG))
    frags += axes(cx, y0, R)
    frags += circ_points(cx, y0, R, ox=26, oy=-16, col=NEG)
    # вектор зсуву від центру до центра хмари
    frags.append(arrow(cx, y0, cx + 26, y0 - 16, color=NEG, sw=2.2))
    frags.append(text(cx + 30, y0 - 20, "b", size=12, bold=True, color=NEG, anchor="start"))
    frags.append(text(cx, y0 + R + 46, "коло ЗСУНУТЕ з центру", size=11, color=MUTED))
    frags.append(text(cx, y0 + R + 64, "→ COMPASS_OFS_X/Y/Z", size=10.5, color=NEG))

    # стрілка між панелями
    frags.append(arrow(232, y0, 288, y0, color=INK, sw=2))

    # (б) м'яке залізо: той самий зсув + розтяг + поворот у еліпс
    cx = 370
    frags.append(text(cx, 70, "+ м'яке залізо", size=12.5, bold=True, color=FIELD))
    frags += axes(cx, y0, R)
    frags += circ_points(cx, y0, R, ox=26, oy=-16, sx=1.28, sy=0.72, rot=0.5, col=FIELD)
    frags.append(text(cx, y0 + R + 46, "коло РОЗТЯГНУТЕ+ПОВЕРНУТЕ", size=11, color=MUTED))
    frags.append(text(cx, y0 + R + 64, "→ DIA (розтяг) + ODI (перекіс)", size=10.5, color=FIELD))

    # стрілка «калібрування повертає до сфери»
    frags.append(arrow(452, y0, 512, y0, color=INK, sw=2))
    frags.append(text(482, y0 - 12, "калібрування", size=10, color=MUTED))

    # (в) чиста сфера в центрі + схилення повертає курс на справжню північ
    cx = 610
    frags.append(text(cx, 70, "чисто → схилення", size=12.5, bold=True, color=INK))
    frags += axes(cx, y0, R)
    frags += circ_points(cx, y0, R, col=POS)
    # магнітна північ (вимір) і справжня північ (після +D)
    frags.append(arrow(cx, y0, cx, y0 - R - 4, color=POS, sw=2.2))
    frags.append(text(cx - 6, y0 - R - 8, "магн. N", size=10, color=POS, anchor="end"))
    # справжня північ під кутом схилення D
    ang = -0.42
    tx, ty = cx + m.sin(-ang) * (R + 4), y0 - m.cos(ang) * (R + 4)
    frags.append(arrow(cx, y0, tx, ty, color=INK, sw=2.2))
    frags.append(text(tx + 6, ty - 2, "справж. N", size=10, color=INK, anchor="start"))
    # дуга кута D
    frags.append('<path d="M %.1f %.1f A 34 34 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
                 % (cx, y0 - 34, cx + m.sin(-ang) * 34, y0 - m.cos(ang) * 34, MUTED))
    frags.append(text(cx + 14, y0 - 40, "D", size=11, bold=True, color=MUTED, anchor="start"))
    frags.append(text(cx, y0 + R + 46, "сфера в центрі; +D до справжньої", size=11, color=MUTED))
    frags.append(text(cx, y0 + R + 64, "→ WMM / COMPASS_AUTODEC", size=10.5, color=INK))

    # права рамка-підсумок
    body, bw, bh = textbox(838, y0 + 6,
                           "Зсув — вектор.\nФорма — симетрична\nматриця 3×3.\n"
                           "Схилення — географія,\nне апарат.",
                           size=11, pad=10, fill="#f4f8f4", stroke=FIELD, sw=1.4)
    frags.append(body)

    frags.append(text(W / 2, H - 14,
                      "Дві дії прибирає калібрування «танцем» (зсув + форма), третю (схилення) додає магнітна модель за координатами GNSS",
                      size=11.5, color=MUTED))
    render(os.path.join(IMG, 'compass-decomposition.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Поріг failsafe: як апарат відрізняє «пілот прибрав газ» від «зв'язок зник».
#    Failsafe-значення приймача СВІДОМО нижче за RCn_MIN газу; THR_FS_VALUE між ними.
# ─────────────────────────────────────────────────────────────────────────────
def fig_rc_failsafe_threshold():
    W, H = 960, 360
    frags = [text(W / 2, 30, "Поріг failsafe: «прибрав газ» проти «зв'язок пропав»", size=15, bold=True)]

    x0, x1 = 130, 830          # шкала мкс
    y = 168
    # 900 і 950 навмисно розводимо ширше (нижня межа шкали 890), щоб їхні написи не злипались
    def pos(us):
        return x0 + (us - 890) / (1920 - 890) * (x1 - x0)

    xf = pos(950)
    # зона failsafe (ліворуч від порога) — блідо-червона
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="30" rx="5" fill="#fdecea" stroke="%s" stroke-width="1"/>'
                 % (x0 - 6, y - 15, (xf - (x0 - 6)), POS))
    # нормальний робочий діапазон (праворуч від порога) — блідо-зелений
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="30" rx="5" fill="#eef7f0" stroke="%s" stroke-width="1"/>'
                 % (xf, y - 15, (x1 + 6 - xf), FIELD))
    frags.append(line(x0 - 6, y, x1 + 6, y, color=INK, sw=2))

    # усі вузлові написи — НАД віссю, на двох висотах (парні вище), щоб сусіди не злипались
    def node(us, lab, sub, col, hi):
        px = pos(us)
        yl = y - 30 if hi else y - 66      # значення
        ys = y - 46 if hi else y - 82      # підпис
        f = [line(px, y - 9, px, y + 9, color=col, sw=2.6),
             text(px, yl, lab, size=12, bold=True, color=col),
             text(px, ys, sub, size=10.5, color=MUTED)]
        return f

    frags += node(905, "≈ 900", "приймач: втрата зв'язку", POS, hi=False)
    frags += node(950, "THR_FS_VALUE", "поріг (950)", INK, hi=True)
    frags += node(1100, "RCn_MIN", "газ 0 (пілот)", NEG, hi=False)
    frags += node(1900, "RCn_MAX", "газ повний", FIELD, hi=True)

    # назви зон — окремим рядком ПІД віссю (тут більше нічого немає → без накладань)
    frags.append(text((x0 + xf) / 2, y + 30, "FAILSAFE", size=12, bold=True, color=POS))
    frags.append(text((xf + x1) / 2, y + 30, "нормальний робочий діапазон газу", size=11.5, color=FIELD))

    # рамка-висновок
    body, bw, bh = textbox(W / 2, 300,
                           "Умова коректності: канал газу МУСИТЬ уміти впасти нижче за THR_FS_VALUE (зв'язок зник),\n"
                           "але при найнижчому газі пілота лишатися ВИЩЕ за нього. RCn_MIN газу занизько → хибний failsafe.",
                           size=11, pad=11, fill="#f7f7f9", stroke=MUTED, sw=1.4)
    frags.append(body)
    render(os.path.join(IMG, 'rc-failsafe-threshold.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_orientation_rotation()
    fig_compass_decomposition()
    fig_rc_failsafe_threshold()
    print("OK: orientation-rotation.svg, compass-decomposition.svg, rc-failsafe-threshold.svg")
