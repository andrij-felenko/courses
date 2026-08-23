# -*- coding: utf-8 -*-
"""Фігури теми «Обхід перешкод». Чистий Python + svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
def out(name): return os.path.join(IMG, name)


def vec(x1, y1, x2, y2, color, sw=2.4):
    """Кольорова стрілка (лінія + власна голівка того ж кольору)."""
    ang = math.atan2(y2 - y1, x2 - x1)
    hl = 10.0
    hw = 5.0
    bx = x2 - hl * math.cos(ang)
    by = y2 - hl * math.sin(ang)
    px, py = -math.sin(ang), math.cos(ang)
    p1 = (bx + hw * px, by + hw * py)
    p2 = (bx - hw * px, by - hw * py)
    s = line(x1, y1, bx, by, color=color, sw=sw)
    s += ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
          % (x2, y2, p1[0], p1[1], p2[0], p2[1], color))
    return s


# ── 1) two-layers.svg — розважливий план і рефлекс ──────────────────────────
def fig_two_layers():
    W, H = 760, 400
    frags = [text(W / 2, 30, "Два поверхи навігації: розважливий план і швидкий рефлекс", size=16, bold=True)]

    # ── верхній поверх: карта з маршрутом ──
    tx, ty, tw, th = 40, 58, W - 80, 138
    frags.append(rect(tx, ty, tw, th, fill="#f7f9fc", stroke=NEG, sw=1.6))
    frags.append(text(tx + 14, ty + 22, "РОЗВАЖЛИВИЙ ПОВЕРХ — план по карті (повільно, наперед)",
                      size=12.5, color=NEG, anchor="start", bold=True))
    # клітинкова карта з парою «стін» і ламаним маршрутом
    gx, gy, cell = tx + 24, ty + 40, 22
    cols, rows = 24, 3
    for c in range(cols + 1):
        frags.append(line(gx + c * cell, gy, gx + c * cell, gy + rows * cell, color="#dfe4ea", sw=0.7))
    for r in range(rows + 1):
        frags.append(line(gx, gy + r * cell, gx + cols * cell, gy + r * cell, color="#dfe4ea", sw=0.7))
    for (c, r) in [(7, 0), (7, 1), (14, 1), (14, 2)]:
        frags.append(rect(gx + c * cell, gy + r * cell, cell, cell, fill="#d9dde3", stroke="#c2c7ce", sw=0.8, rx=2))
    # проміжні точки маршруту
    pts = [(gx + 1 * cell, gy + 2 * cell + cell / 2),
           (gx + 6 * cell, gy + 2 * cell + cell / 2),
           (gx + 10 * cell, gy + 0 * cell + cell / 2),
           (gx + 17 * cell, gy + 0 * cell + cell / 2),
           (gx + 22 * cell, gy + 1 * cell + cell / 2)]
    for i in range(len(pts) - 1):
        frags.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=NEG, sw=2, dash="5 3"))
    for i, p in enumerate(pts):
        frags.append(circle(p[0], p[1], 4.5, fill="#ffffff", stroke=NEG, sw=2))
    # підпис «ціль» — НАД сіткою, щоб лінії сітки його не перетинали
    frags.append(text(pts[-1][0], gy - 8, "ціль", size=11, color=NEG, anchor="middle"))
    frags.append(text(gx + 24 * cell + 8, gy + rows * cell / 2, "ланцюг проміжних\nточок ↓", size=10.5,
                      color=MUTED, anchor="start"))

    # стрілка «намір» вниз
    my = ty + th
    frags.append(vec(W / 2, my + 2, W / 2, my + 34, FIELD, sw=2.2))
    frags.append(text(W / 2 + 74, my + 24, "напрям наміру", size=11, color=FIELD, anchor="middle", italic=True))

    # ── нижній поверх: апарат із давачем ──
    bx, by, bw, bh = 40, my + 44, W - 80, 118
    frags.append(rect(bx, by, bw, bh, fill="#fff7f6", stroke=POS, sw=1.6))
    frags.append(text(bx + 14, by + 22, "РЕФЛЕКСИВНИЙ ПОВЕРХ — обхід за свіжими давачами (швидко, зараз)",
                      size=12.5, color=POS, anchor="start", bold=True))
    # апарат
    rcx, rcy = bx + 150, by + 74
    frags.append(circle(rcx, rcy, 12, fill="#eaf0fd", stroke=NEG, sw=2))
    # підпис ЛІВОРУЧ від апарата — там немає променів давача (усі йдуть праворуч)
    frags.append(text(rcx - 18, rcy + 4, "апарат", size=11, color=INK, anchor="end"))
    # промені давача (вінець дальностей)
    import math as _m
    for k in range(-4, 5):
        a = _m.radians(k * 20)
        d = 46 if k not in (1, 2) else 22  # праворуч ближче — «перешкода»
        ex = rcx + d * _m.cos(a)
        ey = rcy - d * _m.sin(a)
        col = POS if d < 30 else "#9fb3d6"
        frags.append(line(rcx, rcy, ex, ey, color=col, sw=1.3, dash="2 2"))
        frags.append(circle(ex, ey, 2.2, fill=col, stroke=col, sw=0.8))
    # перешкода праворуч-угорі
    obx, oby = rcx + 30, rcy - 18
    frags.append(rect(obx, oby - 8, 26, 22, fill="#f2d7d3", stroke=POS, sw=1.4, rx=3))
    frags.append(text(obx + 13, oby - 12, "нове!", size=10, color=POS))
    # обраний курс (ухиляння ліворуч від наміру)
    frags.append(vec(rcx, rcy, rcx + 70, rcy - 40, FIELD, sw=2.6))
    frags.append(text(rcx + 96, rcy - 44, "куди повернути\nзараз", size=10.5, color=FIELD, anchor="middle"))

    render(out("two-layers.svg"), W, H, *frags)


# ── 2) potential-field.svg — тяга цілі й поштовхи перешкод ───────────────────
def fig_potential_field():
    W, H = 760, 380
    frags = [text(W / 2, 30, "Потенційні поля: ціль тягне, перешкоди штовхають, апарат іде за сумою",
                  size=16, bold=True)]

    rcx, rcy = 210, 250          # апарат
    goal = (640, 110)            # ціль

    # ── обчислимо реальні вектори, щоб сума була чесною ──
    att_k = 1.0
    gx, gy = goal[0] - rcx, goal[1] - rcy
    gl = math.hypot(gx, gy)
    ax, ay = att_k * gx / gl, att_k * gy / gl   # одинична тяга

    obstacles = [(330, 150, 1.0), (300, 300, 0.75)]  # x, y, вага
    rx, ry = 0.0, 0.0
    for (ox, oy, wgt) in obstacles:
        dx, dy = rcx - ox, rcy - oy             # від перешкоди до апарата
        dl = math.hypot(dx, dy)
        s = wgt * (60.0 / dl)                   # ближче — сильніше (умовно)
        rx += s * dx / dl
        ry += s * dy / dl

    sx, sy = ax + rx, ay + ry                   # сума
    sl = math.hypot(sx, sy)

    SC = 70.0  # масштаб векторів у px

    # ціль
    frags.append(circle(goal[0], goal[1], 12, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(goal[0], goal[1] + 4, "★", size=15, color=FIELD))
    frags.append(text(goal[0], goal[1] - 20, "ціль", size=12, color=FIELD, bold=True))

    # перешкоди
    for (ox, oy, wgt) in obstacles:
        frags.append(circle(ox, oy, 15, fill="#f2d7d3", stroke=POS, sw=1.8))
        frags.append(text(ox, oy + 4, "✕", size=13, color=POS))
        # вектор поштовху від перешкоди
        dx, dy = rcx - ox, rcy - oy
        dl = math.hypot(dx, dy)
        s = wgt * (60.0 / dl)
        frags.append(vec(rcx, rcy, rcx + s * dx / dl * (SC / 60.0) * 1.0,
                         rcy + s * dy / dl * (SC / 60.0) * 1.0, POS, sw=2.0))
    frags.append(text((obstacles[0][0] + rcx) / 2, obstacles[0][1] - 6, "поштовх", size=11, color=POS, italic=True))

    # тяга цілі (пунктирна лінія до цілі + вектор)
    frags.append(line(rcx, rcy, goal[0], goal[1], color="#bcd6c6", sw=1.2, dash="4 4"))
    frags.append(vec(rcx, rcy, rcx + ax * SC, rcy + ay * SC, NEG, sw=2.2))
    frags.append(text(rcx + ax * SC + 30, rcy + ay * SC - 4, "тяга цілі", size=11, color=NEG, italic=True))

    # апарат
    frags.append(circle(rcx, rcy, 13, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(rcx, rcy + 32, "апарат", size=12, color=INK))

    # СУМА — товстий зелений
    frags.append(vec(rcx, rcy, rcx + sx / sl * SC * 1.35, rcy + sy / sl * SC * 1.35, FIELD, sw=3.4))
    frags.append(text(rcx + sx / sl * SC * 1.35 + 16, rcy + sy / sl * SC * 1.35 + 16,
                      "СУМА → рух", size=12.5, color=FIELD, bold=True))

    render(out("potential-field.svg"), W, H, *frags)


# ── 3) local-minimum.svg — пастка в підкові ─────────────────────────────────
def fig_local_minimum():
    W, H = 760, 380
    frags = [text(W / 2, 30, "Пастка локального мінімуму: апарат застигає в підкові", size=16, bold=True)]

    # підкова (U), відкрита ліворуч, до апарата; ціль праворуч за нею
    ux0, uy0 = 360, 90            # верхній лівий кут U
    uw, uh, tk = 250, 200, 34     # ширина, висота, товщина стінки
    # три стінки U (права + верх + низ), відкрита зліва
    frags.append(rect(ux0 + uw - tk, uy0, tk, uh, fill="#d9dde3", stroke="#b7bcc4", sw=1.4))   # права
    frags.append(rect(ux0, uy0, uw, tk, fill="#d9dde3", stroke="#b7bcc4", sw=1.4))             # верх
    frags.append(rect(ux0, uy0 + uh - tk, uw, tk, fill="#d9dde3", stroke="#b7bcc4", sw=1.4))   # низ
    frags.append(text(ux0 + uw / 2, uy0 - 10, "перешкода-підкова", size=12, color=MUTED))

    # ціль — праворуч за підковою
    goal = (690, uy0 + uh / 2)
    frags.append(circle(goal[0], goal[1], 12, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(goal[0], goal[1] + 4, "★", size=15, color=FIELD))
    frags.append(text(goal[0], goal[1] - 20, "ціль", size=12, color=FIELD, bold=True))

    # апарат застряг усередині підкови (там, де сили гасяться)
    rcx, rcy = ux0 + uw - tk - 60, uy0 + uh / 2
    # тяга цілі — праворуч (до цілі)
    frags.append(vec(rcx, rcy, rcx + 56, rcy, NEG, sw=2.2))
    frags.append(text(rcx + 30, rcy - 12, "тяга →", size=11, color=NEG, italic=True))
    # поштовх стіни — ліворуч (від правої стінки)
    frags.append(vec(rcx, rcy, rcx - 56, rcy, POS, sw=2.2))
    frags.append(text(rcx - 30, rcy + 20, "← поштовх", size=11, color=POS, italic=True))
    frags.append(circle(rcx, rcy, 13, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(rcx, rcy - 26, "СИЛА = 0", size=12, color=INK, bold=True))
    frags.append(text(rcx, rcy + 34, "апарат застиг", size=11.5, color=POS))

    # шлях, яким апарат зайшов (пунктир зліва всередину)
    frags.append(line(200, rcy, rcx - 14, rcy, color=MUTED, sw=1.4, dash="4 4"))
    frags.append(vec(230, rcy, 262, rcy, MUTED, sw=1.6))
    frags.append(text(200, rcy - 12, "зайшов сюди…", size=11, color=MUTED, anchor="start"))

    # правильний вихід — назад і в обхід (сірий пунктир)
    frags.append(text(W / 2, H - 16,
                      "вибратися можна лише ПРОТИ тяги цілі — а поле рухає тільки ЗА нею",
                      size=11.5, color=MUTED))

    render(out("local-minimum.svg"), W, H, *frags)


# ── 4) vfh-histogram.svg — полярна гістограма й вибір долини ─────────────────
def fig_vfh():
    W, H = 760, 400
    frags = [text(W / 2, 30, "VFH: звести дальності в полярну гістограму й вибрати вільну долину",
                  size=16, bold=True)]

    cx, cy = 250, 220            # центр — апарат
    R0 = 40                      # базовий радіус стовпчиків
    # щільність перешкод по 24 секторах (0 = вільно, 1 = стіна). Долина ліворуч-угору до цілі.
    dens = []
    for i in range(24):
        a = i * 15.0
        # стіна праворуч (біля 0°) і знизу (біля 270°); долина коло 120°
        v = 0.0
        v += 0.9 * math.exp(-((a - 0) % 360 if (a % 360) < 180 else (360 - a)) ** 2 / (2 * 35 ** 2))
        v += 0.85 * math.exp(-((a - 270)) ** 2 / (2 * 40 ** 2))
        v += 0.4 * math.exp(-((a - 200)) ** 2 / (2 * 25 ** 2))
        dens.append(min(1.0, v))

    thr = 0.35                    # поріг «долини»
    # намалюємо радіальні стовпчики
    for i, v in enumerate(dens):
        a = math.radians(i * 15.0)
        length = R0 + v * 70
        ex = cx + length * math.cos(a)
        ey = cy - length * math.sin(a)
        col = POS if v >= thr else FIELD
        sw = 8 if v >= thr else 6
        frags.append(line(cx + R0 * math.cos(a), cy - R0 * math.sin(a), ex, ey, color=col, sw=sw))

    # базове коло (апарат)
    frags.append(circle(cx, cy, R0, fill="#ffffff", stroke=MUTED, sw=1.2))
    frags.append(circle(cx, cy, 11, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(cx, cy + 4, "▲", size=12, color=NEG))
    frags.append(text(cx, cy + 30, "апарат", size=11, color=INK))

    # обрана долина — стрілка в бік ~120°
    ga = math.radians(120)
    frags.append(vec(cx, cy, cx + 128 * math.cos(ga), cy - 128 * math.sin(ga), FIELD, sw=3.2))
    frags.append(text(cx + 150 * math.cos(ga) - 6, cy - 150 * math.sin(ga),
                      "обрана долина\n→ до цілі", size=11.5, color=FIELD, bold=True))

    # напрям на ціль (тонкий пунктир, поряд із долиною)
    ta = math.radians(135)
    tex, tey = cx + 150 * math.cos(ta), cy - 150 * math.sin(ta)
    frags.append(line(cx, cy, tex, tey, color="#bcd6c6", sw=1.3, dash="4 4"))
    # підпис — на вільному лівому полі, ВБІК від променів і пунктиру; веде коротка ніжка
    lbx, lby = 92, 150
    frags.append(line(lbx + 30, lby - 4, tex - 6, tey + 4, color="#bcd6c6", sw=1.0, dash="3 3"))
    frags.append(text(lbx, lby, "напрям на ціль", size=10.5, color=MUTED))

    # ── легенда праворуч ──
    lx, ly = 540, 120
    frags.append(rect(lx, ly, 190, 150, fill="#fbfcfd", stroke=LINE, sw=1.2))
    frags.append(text(lx + 12, ly + 24, "стовпчик = щільність", size=12, color=INK, anchor="start", bold=True))
    frags.append(text(lx + 12, ly + 42, "перешкод у цей бік", size=12, color=INK, anchor="start"))
    frags.append(line(lx + 16, ly + 68, lx + 56, ly + 68, color=POS, sw=8))
    frags.append(text(lx + 66, ly + 72, "тісно (стіна)", size=11.5, color=POS, anchor="start"))
    frags.append(line(lx + 16, ly + 96, lx + 56, ly + 96, color=FIELD, sw=6))
    frags.append(text(lx + 66, ly + 100, "вільно (долина)", size=11.5, color=FIELD, anchor="start"))
    frags.append(text(lx + 12, ly + 128, "вибрати долину, що", size=11, color=MUTED, anchor="start"))
    frags.append(text(lx + 12, ly + 143, "найближча до цілі", size=11, color=MUTED, anchor="start"))

    render(out("vfh-histogram.svg"), W, H, *frags)


# ── 5) pf-landscape.svg — рельєф потенціалу й локальний мінімум ──────────────
def fig_pf_landscape():
    """Профіль U(x) уздовж прямої крізь підкову: чаша до цілі + паразитна
    ямка всередині підкови, де ∇U=0. Кулька котиться за −∇U (униз)."""
    W, H = 760, 380
    frags = [text(W / 2, 30, "Рельєф сумарного потенціалу: чому виникає зайва ямка", size=16, bold=True)]

    # осі
    x0, x1 = 70, 690            # ліворуч старт, праворуч ціль
    ybase = 300                 # рівень «нуль сили» (візуальна база графіка)
    frags.append(line(x0, ybase, x1, ybase, color=MUTED, sw=1.0, dash="3 3"))
    frags.append(text(x0 - 4, 70, "U — сумарний потенціал", size=12, color=INK, anchor="start", bold=True))
    frags.append(text(x1, ybase + 22, "ціль", size=12, color=FIELD, anchor="middle", bold=True))
    frags.append(text(x0, ybase + 22, "старт", size=12, color=NEG, anchor="middle"))

    # U(x): параболічна чаша до цілі (спадає праворуч) + горб-стінка підкови
    # + локальна ямка ПЕРЕД горбом. Складаємо як реальну суму двох доданків.
    import math as _m
    xs = [x0 + i * (x1 - x0) / 240.0 for i in range(241)]
    def U(px):
        t = (px - x0) / (x1 - x0)              # 0..1 уздовж лінії
        att = 120 * (1 - t)                    # чаша притягання: нижче біля цілі
        # стінка підкови ~ біля t=0.72: високий вузький горб (відштовхування 1/ρ²)
        wall_c, wall_w = 0.72, 0.05
        rep = 150 * _m.exp(-((t - wall_c) / wall_w) ** 2)
        return att + rep
    # у px: більший U → вище (менший y)
    Umin = min(U(px) for px in xs)
    Umax = max(U(px) for px in xs)
    def y_of(px):
        u = U(px)
        return 250 - (u - Umin) / (Umax - Umin) * 170  # 250 (низ) .. 80 (верх)
    # крива
    d = "M %.1f %.1f" % (xs[0], y_of(xs[0]))
    for px in xs[1:]:
        d += " L %.1f %.1f" % (px, y_of(px))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, INK))

    # позначити локальний мінімум: найнижча точка ЛІВОРУЧ від стінки
    left = [px for px in xs if (px - x0) / (x1 - x0) < 0.66]
    lm = min(left, key=U)
    lmy = y_of(lm)
    frags.append(circle(lm, lmy, 9, fill="#eaf0fd", stroke=NEG, sw=2.2))
    frags.append(text(lm, lmy - 18, "∇U = 0", size=12, color=NEG, bold=True))
    frags.append(text(lm, lmy + 26, "локальний\nмінімум", size=11, color=NEG))
    # кулька-апарат котиться сюди й застигає
    frags.append(vec(lm - 70, lmy - 34, lm - 14, lmy - 12, MUTED, sw=1.8))
    frags.append(text(lm - 96, lmy - 40, "апарат\nскочується", size=10.5, color=MUTED, anchor="middle"))

    # глобальний мінімум — біля цілі
    gm = xs[-1]
    frags.append(circle(gm, y_of(gm), 8, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(gm, y_of(gm) - 16, "глобальний\nмінімум", size=10.5, color=FIELD))

    # стінка підкови — підпис на горбі
    wall_px = x0 + 0.72 * (x1 - x0)
    frags.append(text(wall_px, y_of(wall_px) - 12, "стінка підкови (відштовхування ↑)",
                      size=11, color=POS, bold=True))

    # барʼєр між ямкою й ціллю
    frags.append(text(W / 2, H - 14,
                      "щоб дійти до цілі, треба перелізти горб — тобто піти ВГОРУ по U (проти сили)",
                      size=11.5, color=MUTED))
    render(out("pf-landscape.svg"), W, H, *frags)


# ── 6) pf-oscillation.svg — коливання у вузькому проході ─────────────────────
def fig_pf_oscillation():
    """Бічна віддільна сила в коридорі: різка (1/d²) проти гладшої;
    крива сили по ширині проходу + зигзаг траєкторії від різкої."""
    W, H = 760, 400
    frags = [text(W / 2, 30, "Коливання в проході: різкий градієнт кидає апарат зиґзаґом",
                  size=16, bold=True)]

    # ── ліворуч: графік бічної сили F_y(y) поперек проходу ──
    gx0, gx1 = 70, 380        # межі графіка по x (px)
    gy_mid = 210              # центр проходу (F=0)
    axh = 120                # піврозмах по вертикалі
    # стіни проходу
    wall_top, wall_bot = gy_mid - 150, gy_mid + 150
    frags.append(rect(gx0, wall_top - 14, gx1 - gx0, 14, fill="#d9dde3", stroke="#b7bcc4", sw=1.2))
    frags.append(rect(gx0, wall_bot, gx1 - gx0, 14, fill="#d9dde3", stroke="#b7bcc4", sw=1.2))
    frags.append(text((gx0 + gx1) / 2, wall_top - 20, "стіна", size=11, color=MUTED))
    frags.append(text((gx0 + gx1) / 2, wall_bot + 26, "стіна", size=11, color=MUTED))
    # вісь центру
    frags.append(line(gx0, gy_mid, gx1, gy_mid, color=MUTED, sw=1.0, dash="3 3"))
    frags.append(text(gx1 + 4, gy_mid + 4, "центр", size=10.5, color=MUTED, anchor="start"))

    import math as _m
    half = 150.0             # півширина проходу в px
    axc = (gx0 + gx1) / 2    # де F=0 на осі x графіка
    # F(y): різниця двох 1/d² від верхньої й нижньої стін. y в px від центру.
    def F_sharp(dy):
        eps = 18.0
        du = half - dy       # відстань до верхньої стіни (dy<0 => ближче до верху)
        dd = half + dy
        return (1.0 / (dd + eps) ** 2 - 1.0 / (du + eps) ** 2)
    def F_soft(dy):
        # гладша: обмежена похідна (лінійна близько центру, насичення)
        return 0.0000090 * dy  # мʼяка пружина з малим нахилом
    # нормування під однаковий візуальний масштаб
    Sm = max(abs(F_sharp(dy)) for dy in range(-140, 141))
    # крива різкої сили (червона): x = axc + F*scale
    scaleX = 150.0
    pts_sharp = []
    for dy in range(-145, 146, 2):
        fx = axc + F_sharp(dy) / Sm * scaleX
        pts_sharp.append((fx, gy_mid + dy))
    d = "M %.1f %.1f" % pts_sharp[0]
    for p in pts_sharp[1:]:
        d += " L %.1f %.1f" % p
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))
    # крива гладкої сили (зелена)
    Ss = max(abs(F_soft(dy)) for dy in range(-140, 141)) or 1.0
    pts_soft = []
    for dy in range(-140, 141, 4):
        fx = axc + F_soft(dy) / Ss * scaleX * 0.9
        pts_soft.append((fx, gy_mid + dy))
    d2 = "M %.1f %.1f" % pts_soft[0]
    for p in pts_soft[1:]:
        d2 += " L %.1f %.1f" % p
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6 4"/>' % (d2, FIELD))

    frags.append(text(gx0 + 6, wall_top + 24, "різка 1/d² →", size=11, color=POS, anchor="start", bold=True))
    frags.append(text(gx0 + 6, wall_bot - 14, "← гладша (обмежена похідна)", size=11, color=FIELD, anchor="start"))
    frags.append(text((gx0 + gx1) / 2, gy_mid + axh + 66,
                      "бічна сила F поперек проходу", size=11.5, color=INK))

    # ── праворуч: зигзаг траєкторії від різкого поля ──
    cx0 = 440
    cw = 270
    ctop, cbot = 90, 330
    ccy = (ctop + cbot) / 2
    # коридор
    frags.append(rect(cx0, ctop - 12, cw, 12, fill="#d9dde3", stroke="#b7bcc4", sw=1.2))
    frags.append(rect(cx0, cbot, cw, 12, fill="#d9dde3", stroke="#b7bcc4", sw=1.2))
    frags.append(line(cx0, ccy, cx0 + cw, ccy, color=MUTED, sw=1.0, dash="3 3"))
    # зигзаг: різка сила перекидає з боку на бік
    zx = [cx0 + 6 + i * (cw - 12) / 6.0 for i in range(7)]
    zy = [ccy, ctop + 26, cbot - 26, ctop + 30, cbot - 30, ctop + 34, ccy]
    dz = "M %.1f %.1f" % (zx[0], zy[0])
    for i in range(1, len(zx)):
        dz += " L %.1f %.1f" % (zx[i], zy[i])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (dz, POS))
    for i in range(len(zx)):
        frags.append(circle(zx[i], zy[i], 3.2, fill="#ffffff", stroke=POS, sw=1.6))
    # гладша траєкторія — майже пряма посередині
    frags.append(line(cx0 + 6, ccy, cx0 + cw - 6, ccy, color=FIELD, sw=2.4, dash="6 4"))
    frags.append(circle(cx0 + 6, ccy, 4, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(cx0 + cw / 2, ctop - 18, "рух уздовж проходу →", size=11, color=MUTED))
    frags.append(text(cx0 + cw / 2, cbot + 28, "різке поле: зиґзаґ (—)   гладке: рівно (- -)",
                      size=11, color=INK))

    render(out("pf-oscillation.svg"), W, H, *frags)


# ── 7) hist-timeline.svg — три повороти думки (для вставки hist) ─────────────
def fig_hist_timeline():
    W, H = 780, 350
    frags = [text(W / 2, 30, "Три повороти думки в реактивному обході перешкод",
                  size=16, bold=True)]

    # горизонтальна вісь часу
    ax0, ax1, ay = 70, W - 40, 150
    frags.append(line(ax0, ay, ax1, ay, color=INK, sw=2.2))
    frags.append(vec(ax1 - 24, ay, ax1, ay, INK, sw=2.2))
    frags.append(text(ax1 - 6, ay + 26, "час", size=11, color=MUTED, anchor="end", italic=True))

    def px(year):
        return ax0 + (year - 1984) / (1998 - 1984) * (ax1 - 40 - ax0)

    # ── верхні події (головна лінія методів) ──
    top = [
        (1985, "Хатіб", "потенційні\nполя", NEG),
        (1991, "Боренштайн\n+ Корен", "VFH\n(відмова\nвід полів)", FIELD),
        (1997, "Фокс · Бургард\n· Трун", "динамічне\nвікно (DWA)", POS),
    ]
    for (yr, who, what, col) in top:
        x = px(yr)
        frags.append(circle(x, ay, 6, fill=col, stroke=col, sw=1.5))
        frags.append(text(x, ay + 24, str(yr), size=12.5, color=INK, bold=True))
        bx, w, h = textbox(x, ay - 92, what, size=11.5, pad=8, fill="#ffffff",
                           stroke=col, sw=1.6, color=col, bold=True)
        frags.append(bx)
        who_y = ay - 92 + h / 2 + 15
        # ніжка донизу СТОПАЄ під підписом-автором, щоб не різати його
        frags.append(line(x, ay, x, who_y + 6, color=col, sw=1.6, dash="3 3"))
        frags.append(text(x, who_y, who, size=10.5, color=MUTED))

    # ── нижня подія (тактильна гілка — Bug) ──
    xb = px(1987)
    frags.append(line(xb, ay, xb, ay + 50, color=MUTED, sw=1.4, dash="3 3"))
    frags.append(circle(xb, ay, 5, fill="#ffffff", stroke=MUTED, sw=1.6))
    bb, wb, hb = textbox(xb + 46, ay + 88, "Bug-алгоритм\n(дотик, не далекомір)",
                         size=11, pad=8, fill="#fbfcfd", stroke=MUTED, sw=1.4, color=INK)
    frags.append(bb)
    frags.append(text(xb + 46, ay + 88 + hb / 2 + 14, "Лумельський + Степанов, 1987",
                      size=10, color=MUTED))

    frags.append(text(W / 2, H - 14,
                      "кожен наступний метод лікує ваду попереднього: сили → напрямки → фізика апарата",
                      size=11.5, color=MUTED))
    render(out("hist-timeline.svg"), W, H, *frags)


# ── 8) hist-four-flaws.svg — чотири вроджені вади полів ──────────────────────
def fig_four_flaws():
    W, H = 760, 330
    frags = [text(W / 2, 30, "Чому Корен і Боренштайн відреклися від власного улюбленого методу",
                  size=15, bold=True)]
    frags.append(text(W / 2, 52, "Чотири вади, що випливають із самої ідеї «складати сили» (ICRA 1991)",
                      size=12, color=MUTED))

    flaws = [
        ("1", "пастка в куті", "у ввігнутій перешкоді сили\nгасяться — апарат застигає"),
        ("2", "тремтіння", "у вузькому проході кермо\nсіпається зиґзаґом"),
        ("3", "не проходить\nу щілину", "між близькими перешкодами\nпоштовх відкидає геть"),
        ("4", "коливання", "перед перешкодою в лоб сила\nрізко вмикається й гасне"),
    ]
    cw, gap = 168, 18
    total = 4 * cw + 3 * gap
    x0 = (W - total) / 2
    cy = 180
    for i, (n, title, body) in enumerate(flaws):
        x = x0 + i * (cw + gap)
        frags.append(rect(x, cy - 62, cw, 134, fill="#fff7f6", stroke=POS, sw=1.5, rx=8))
        frags.append(circle(x + 24, cy - 40, 13, fill=POS, stroke=POS, sw=1))
        frags.append(text(x + 24, cy - 35, n, size=14, color="#ffffff", bold=True))
        frags.append(mtext(x + cw / 2 + 10, cy - 36, title, size=12.5, color=POS, bold=True))
        frags.append(mtext(x + cw / 2, cy + 6, body, size=10.5, color=INK))

    frags.append(text(W / 2, H - 16,
                      "жодна — не помилка коду; усі — прямий наслідок принципу. Тому знадобився інший принцип.",
                      size=11.5, color=MUTED))
    render(out("hist-four-flaws.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_two_layers()
    fig_potential_field()
    fig_local_minimum()
    fig_vfh()
    fig_pf_landscape()
    fig_pf_oscillation()
    fig_hist_timeline()
    fig_four_flaws()
    print("OK: two-layers, potential-field, local-minimum, vfh-histogram, pf-landscape, pf-oscillation, hist-timeline, hist-four-flaws")
