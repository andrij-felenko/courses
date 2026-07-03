# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: подвійне покриття — короткий і довгий шлях до тієї самої цілі ──
def fig_double_cover():
    W, H = 720, 380
    cx, cy, R = 300, 210, 130
    parts = []
    # коло орієнтацій (умовне «кільце» станів)
    parts.append(circle(cx, cy, R, fill=BG, stroke=MUTED, sw=2))
    # поточна орієнтація — угорі
    ax = math.radians(-90)
    px, py = cx + R * math.cos(ax), cy + R * math.sin(ax)
    # ціль — трохи праворуч-унизу
    bx_ang = math.radians(35)
    qx, qy = cx + R * math.cos(bx_ang), cy + R * math.sin(bx_ang)
    parts.append(dot_arc(cx, cy, R, -90, 35, FIELD, sw=6))          # короткий шлях
    parts.append(dot_arc(cx, cy, R, -90, 35, POS, sw=6, longway=True))  # довгий шлях
    parts.append(circle(px, py, 9, fill=INK, stroke=INK))
    parts.append(circle(qx, qy, 9, fill=FIELD, stroke=FIELD))
    parts.append(text(px, py - 18, "поточна q", size=14, bold=True))
    parts.append(text(qx + 12, qy + 26, "ціль q_d", size=14, bold=True, anchor="start"))
    parts.append(text(cx - 40, cy - 8, "короткий", size=13, color=FIELD, bold=True, anchor="end"))
    parts.append(text(cx + 8, cy + R - 30, "довгий (той самий поворот!)", size=12, color=POS, anchor="start"))
    # права колонка — правило вибору
    bx, by = 500, 90
    b1 = fitbox(bx, by, 200, 60,
                "q_err = q_d ⊗ q⁻¹\n(похибка як поворот)", size=13, fill=FILL)
    parts.append(b1)
    b2 = fitbox(bx, by + 90, 200, 70,
                "скалярна w < 0 ?\n→ узяти −q_err\n(коротша дуга)", size=13,
                fill="#eaf0fd", stroke=NEG)
    parts.append(b2)
    parts.append(arrow(bx + 100, by + 60, bx + 100, by + 90, color=LINE))
    return render(os.path.join(IMG, 'double-cover.svg'), W, H, *parts)


def dot_arc(cx, cy, R, a0_deg, a1_deg, color, sw=5, longway=False):
    """Дуга на колі від a0 до a1 (короткою або довгою стороною), пунктиром."""
    a0, a1 = a0_deg, a1_deg
    diff = (a1 - a0) % 360
    if longway:
        # взяти більшу дугу
        if diff < 180:
            a1 = a0 + (diff - 360)
    else:
        if diff > 180:
            a1 = a0 + (diff - 360)
    steps = 40
    pts = []
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append('%.1f,%.1f' % (cx + R * math.cos(a), cy + R * math.sin(a)))
    dash = '2,7' if longway else None
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linecap="round"%s/>' % (' '.join(pts), color, sw,
            ' stroke-dasharray="%s"' % dash if dash else ''))


# ── Фігура 2: контур керування орієнтацією на кватерніонах ──────────────────
def fig_control_loop():
    W, H = 760, 300
    parts = []
    y = 150
    boxes = [
        (95,  "ціль q_d", FILL, LINE),
        (250, "похибка\nq_err = q_d ⊗ q⁻¹", "#eaf0fd", NEG),
        (430, "закон PD\nτ = −Kₚ·qᵥ − K_d·ω", FILL, LINE),
        (610, "мотори\n(мікшер)", FILL, LINE),
    ]
    prev = None
    for x, label, fill, stroke in boxes:
        b = fitbox(x - 78, y - 34, 156, 68, label, size=13, fill=fill, stroke=stroke)
        parts.append(b)
        if prev is not None:
            parts.append(arrow(prev + 78, y, x - 78, y, color=LINE))
        prev = x
    # об'єкт (апарат) і зворотний зв'язок
    parts.append(arrow(610 + 78, y, 700, y, color=LINE))
    parts.append(text(715, y + 4, "тіло", size=13, anchor="start", bold=True))
    # зворотний зв'язок по орієнтації q та швидкості ω
    parts.append(line(715, y + 14, 715, 250, color=MUTED, sw=1.6))
    parts.append(line(715, 250, 250, 250, color=MUTED, sw=1.6))
    parts.append(arrow(250, 250, 250, y + 34, color=MUTED))
    parts.append(text(480, 268, "виміряні q (орієнтація) та ω (кутова швидкість) — зворотний зв'язок",
                      size=12, color=MUTED))
    return render(os.path.join(IMG, 'control-loop.svg'), W, H, *parts)


# ── Фігура 3: похибка = вісь + кут; векторна частина ≈ пів-кут × вісь ────────
def fig_axis_angle():
    W, H = 720, 340
    cx, cy = 250, 200
    parts = []
    # осі тіла
    parts.append(line(cx, cy, cx, cy - 120, color=MUTED, sw=1.6))
    parts.append(line(cx, cy, cx + 130, cy, color=MUTED, sw=1.6))
    parts.append(text(cx + 138, cy + 4, "де є", size=12, color=MUTED, anchor="start"))
    parts.append(text(cx + 4, cy - 126, "куди треба", size=12, color=MUTED, anchor="start"))
    # вісь повороту (нахилена) — те, що каже похибка
    ang = math.radians(-40)
    ex, ey = cx + 130 * math.cos(ang), cy + 130 * math.sin(ang)
    parts.append(arrow(cx, cy, ex, ey, color=FIELD, sw=3))
    parts.append(text(ex + 6, ey - 4, "вісь ê", size=14, color=FIELD, bold=True, anchor="start"))
    # дуга кута θ між «де є» і «куди треба»
    parts.append('<path d="M %.1f %.1f A 60 60 0 0 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2"/>' % (cx + 60, cy, cx, cy - 60, POS))
    parts.append(text(cx + 52, cy - 40, "θ", size=16, color=POS, bold=True))
    # права колонка — формула
    b = fitbox(470, 120, 220, 120,
               "q_err = (w, v)\n\nv = ê · sin(θ/2)\nw = cos(θ/2)\n\nмалий θ:  v ≈ (θ/2)·ê",
               size=14, fill=FILL)
    parts.append(b)
    parts.append(text(470 + 110, 260, "керуємо просто по v", size=13, color=FIELD, bold=True))
    return render(os.path.join(IMG, 'axis-angle.svg'), W, H, *parts)


# ── Фігура 4: сендвіч розкладає вектор на дві частини (вздовж осі й упоперек) ─
def fig_sandwich_split():
    W, H = 720, 360
    cx, cy = 250, 200
    parts = []
    # вісь ê (нахилена вгору-праворуч)
    aang = math.radians(-32)
    axx, axy = cx + 150 * math.cos(aang), cy + 150 * math.sin(aang)
    parts.append(arrow(cx, cy, axx, axy, color=FIELD, sw=3))
    parts.append(text(axx + 6, axy - 4, "вісь ê", size=14, color=FIELD, bold=True, anchor="start"))
    # вектор v (інший напрям)
    vang = math.radians(-78)
    vx, vy = cx + 135 * math.cos(vang), cy + 135 * math.sin(vang)
    parts.append(arrow(cx, cy, vx, vy, color=INK, sw=2.6))
    parts.append(text(vx - 2, vy - 8, "v", size=15, bold=True, anchor="middle"))
    # проєкція v‖ на вісь (нерухома частина)
    dot = ((vx - cx) * (axx - cx) + (vy - cy) * (axy - cy))
    alen2 = (axx - cx) ** 2 + (axy - cy) ** 2
    t = dot / alen2
    px, py = cx + t * (axx - cx), cy + t * (axy - cy)
    parts.append(line(cx, cy, px, py, color=POS, sw=4))
    parts.append(text((cx + px) / 2 + 6, (cy + py) / 2 - 6, "v‖", size=13, color=POS, bold=True, anchor="start"))
    # перпендикулярна частина v⊥ (та, що крутиться)
    parts.append(line(px, py, vx, vy, color=NEG, sw=2, dash="4,4"))
    parts.append(text((px + vx) / 2 - 8, (py + vy) / 2, "v⊥", size=13, color=NEG, bold=True, anchor="end"))
    # права колонка — що з ними робить сендвіч
    parts.append(fitbox(470, 110, 230, 66,
                        "v‖ (уздовж осі)\nсендвіч НЕ чіпає", size=13,
                        fill="#fdecea", stroke=POS))
    parts.append(fitbox(470, 200, 230, 66,
                        "v⊥ (упоперек осі)\nповертається на кут θ", size=13,
                        fill="#eaf0fd", stroke=NEG))
    return render(os.path.join(IMG, 'sandwich-split.svg'), W, H, *parts)


# ── Фігура 5: два піврухи складаються в повний кут (ліворуч θ/2, праворуч θ/2) ─
def fig_two_half_turns():
    W, H = 720, 380
    cx, cy, R = 360, 185, 120
    parts = []
    parts.append(circle(cx, cy, R, fill=BG, stroke=MUTED, sw=1.6))
    # старт вектора — праворуч
    def onring(deg):
        a = math.radians(deg)
        return cx + R * math.cos(a), cy + R * math.sin(a)
    x0, y0 = onring(0)
    xh, yh = onring(-55)      # після лівого множення: +θ/2
    x1, y1 = onring(-110)     # після правого: ще +θ/2 → повний θ
    parts.append(arrow(cx, cy, x0, y0, color=MUTED, sw=2.4))
    parts.append(text(x0 + 10, y0 + 4, "v", size=14, bold=True, anchor="start"))
    parts.append(arrow(cx, cy, xh, yh, color=NEG, sw=2.4))
    parts.append(text(xh + 10, yh - 2, "після q·(…)", size=12, color=NEG, anchor="start"))
    parts.append(arrow(cx, cy, x1, y1, color=POS, sw=2.8))
    parts.append(text(x1 - 6, y1 + 18, "після (…)·q⁻¹", size=12, color=POS, anchor="end"))
    # дуги θ/2 і θ/2
    parts.append('<path d="M %.1f %.1f A %d %d 0 0 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2"/>' % (
                     cx + (R + 22) * math.cos(0), cy + (R + 22) * math.sin(0),
                     R + 22, R + 22,
                     cx + (R + 22) * math.cos(math.radians(-55)),
                     cy + (R + 22) * math.sin(math.radians(-55)), NEG))
    parts.append('<path d="M %.1f %.1f A %d %d 0 0 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2"/>' % (
                     cx + (R + 22) * math.cos(math.radians(-55)),
                     cy + (R + 22) * math.sin(math.radians(-55)),
                     R + 22, R + 22,
                     cx + (R + 22) * math.cos(math.radians(-110)),
                     cy + (R + 22) * math.sin(math.radians(-110)), POS))
    mh = onring(-27); parts.append(text(cx + (R + 40) * math.cos(math.radians(-27)),
                                        cy + (R + 40) * math.sin(math.radians(-27)),
                                        "θ/2", size=14, color=NEG, bold=True))
    parts.append(text(cx + (R + 40) * math.cos(math.radians(-83)),
                      cy + (R + 40) * math.sin(math.radians(-83)),
                      "θ/2", size=14, color=POS, bold=True))
    # підпис унизу
    parts.append(text(cx, cy + R + 55, "кожне множення докладає θ/2  →  разом рівно θ",
                      size=14, bold=True))
    return render(os.path.join(IMG, 'two-half-turns.svg'), W, H, *parts)


# ── Фігура 6 (вставка proj): дрейф норми зі сфери, нормування повертає ───────
def fig_normalize_drift():
    W, H = 720, 360
    cx, cy, R = 250, 190, 130
    parts = []
    # одинична «сфера» (коло) станів чистого повороту
    parts.append(circle(cx, cy, R, fill=BG, stroke=FIELD, sw=2))
    parts.append(text(cx, cy - R - 12, "|q| = 1  (чистий поворот)", size=13,
                      color=FIELD, bold=True))
    # точка на сфері — чистий кватерніон
    a = math.radians(-58)
    px, py = cx + R * math.cos(a), cy + R * math.sin(a)
    # дрейф назовні (норма > 1) — округлення float штовхнуло за сферу
    dx, dy = cx + (R + 42) * math.cos(a), cy + (R + 42) * math.sin(a)
    parts.append(line(cx, cy, dx, dy, color=MUTED, sw=1.2, dash="3,4"))
    parts.append(circle(dx, dy, 8, fill="#fdecea", stroke=POS, sw=2))
    parts.append(text(dx + 12, dy - 4, "|q| = 1.02", size=12, color=POS,
                      bold=True, anchor="start"))
    parts.append(text(dx + 12, dy + 13, "дрейф від округлень", size=11,
                      color=MUTED, anchor="start"))
    # стрілка нормування — назад на сферу
    parts.append(arrow(dx, dy, px, py, color=NEG, sw=2.4))
    parts.append(circle(px, py, 8, fill=BG, stroke=FIELD, sw=2))
    parts.append(text(px - 10, py + 6, "q ← q/|q|", size=12, color=NEG,
                      bold=True, anchor="end"))
    # права колонка — суть
    parts.append(fitbox(470, 120, 226, 62,
                        "кожна float-операція\nтрохи зсуває з сфери", size=13,
                        fill="#fdecea", stroke=POS))
    parts.append(fitbox(470, 205, 226, 62,
                        "одне ділення на |q|\nщокроку — знову чисто", size=13,
                        fill="#eaf0fd", stroke=NEG))
    return render(os.path.join(IMG, 'normalize-drift.svg'), W, H, *parts)


# ── Фігура 7 (вставка proj): повний тракт модуля прошивки ────────────────────
def fig_module_pipeline():
    W, H = 780, 320
    parts = []
    y = 120
    boxes = [
        (100, "виміри\nq, q_d, ω", FILL, LINE),
        (270, "похибка +\nкороткий шлях", "#eaf0fd", NEG),
        (440, "PD-момент\nτ (3 осі)", FILL, LINE),
        (610, "розподіл A⁺\n→ актуатори", "#eafaf0", FIELD),
    ]
    prev = None
    for x, label, fill, stroke in boxes:
        b = fitbox(x - 80, y - 32, 160, 64, label, size=13, fill=fill, stroke=stroke)
        parts.append(b)
        if prev is not None:
            parts.append(arrow(prev + 80, y, x - 80, y, color=LINE))
        prev = x
    # хвіст — насичення й вихід на актуатори
    parts.append(arrow(610 + 80, y, 705, y, color=LINE))
    parts.append(fitbox(700, y - 30, 70, 60, "затиск\n(напрям!)", size=11,
                        fill="#fdecea", stroke=POS))
    # підписи-пастки під кожним боксом
    traps = [
        (100, "норму нормуй"),
        (270, "знак w<0 → −q"),
        (440, "знак осей!"),
        (610, "не обрізай нарізно"),
    ]
    for x, t in traps:
        parts.append(text(x, y + 52, t, size=11, color=MUTED))
    # зворотний зв'язок
    parts.append(line(735, y + 30, 735, 250, color=MUTED, sw=1.4))
    parts.append(line(735, 250, 100, 250, color=MUTED, sw=1.4))
    parts.append(arrow(100, 250, 100, y + 32, color=MUTED))
    parts.append(text(418, 268, "виміряні q та ω — зворотний зв'язок",
                      size=12, color=MUTED))
    return render(os.path.join(IMG, 'module-pipeline.svg'), W, H, *parts)


if __name__ == '__main__':
    print(fig_double_cover())
    print(fig_control_loop())
    print(fig_axis_angle())
    print(fig_sandwich_split())
    print(fig_two_half_turns())
    print(fig_normalize_drift())
    print(fig_module_pipeline())
