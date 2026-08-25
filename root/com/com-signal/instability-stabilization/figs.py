# -*- coding: utf-8 -*-
"""Фігури теми «Потреба стабілізації». Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: стійка рівновага проти нестійкої ───────────────────────────────
# Кулька на дні чаші сама вертається (стійко); кулька на вершині пагорба від
# найменшого поштовху скочується (нестійко). Багатороторний апарат — друге.
def fig_equilibrium():
    W, H = 700, 360
    parts = []

    # ── ліва панель: стійка рівновага (долина) ──
    lx = 175
    base = 250
    # чаша: парабола вниз
    pts = []
    for i in range(61):
        t = i / 60.0
        x = lx - 120 + t * 240
        y = base - 90 * (1 - 4 * (t - 0.5) ** 2)   # дно в центрі
        pts.append((x, y))
    pl = " ".join("%.1f,%.1f" % p for p in pts)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pl, INK))
    # кулька на дні
    bx, by = lx, base - 9
    parts.append(circle(bx, by, 13, fill="#eafaf1", stroke=FIELD, sw=2.5))
    # поштовх убік і повернення
    parts.append(arrow(bx + 16, by - 2, bx + 52, by - 2, color=MUTED, sw=1.6))
    parts.append(arrow(lx + 70, base - 52, lx + 30, base - 16, color=FIELD, sw=2.2))
    parts.append(text(lx, base + 44, "стійка рівновага", 13, INK, "middle", bold=True))
    parts.append(text(lx, base + 64, "поштовх → кулька сама вертається", 11, MUTED, "middle"))

    # ── права панель: нестійка рівновага (вершина) ──
    rx = 525
    # пагорб: парабола вгору (горб)
    pts = []
    for i in range(61):
        t = i / 60.0
        x = rx - 120 + t * 240
        y = base - 90 * (4 * (t - 0.5) ** 2)   # вершина в центрі (y менший = вище)
        pts.append((x, y))
    pr = " ".join("%.1f,%.1f" % p for p in pts)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pr, INK))
    # кулька на вершині
    tx, ty = rx, base - 90 - 9
    parts.append(circle(tx, ty, 13, fill="#fdecea", stroke=POS, sw=2.5))
    # найменший поштовх і зрив униз
    parts.append(arrow(tx + 15, ty, tx + 44, ty, color=MUTED, sw=1.6))
    parts.append(arrow(rx + 36, base - 78, rx + 96, base - 14, color=POS, sw=2.4))
    parts.append(text(rx, base + 44, "нестійка рівновага", 13, INK, "middle", bold=True))
    parts.append(text(rx, base + 64, "найменший поштовх → кулька скочується", 11, MUTED, "middle"))

    render(os.path.join(IMG, "equilibrium.svg"), W, H, *parts,
           title="Багатороторний апарат — кулька на вершині, а не в чаші")


# ── Фігура 2: збурення наростає, а контур його приборкує ──────────────────────
# Графік кута нахилу в часі. Без контуру: мале відхилення росте лавиною
# (експонента) до перекидання. З контуром: те саме збурення згасає назад до нуля.
def fig_growth():
    W, H = 700, 360
    ox, oy = 90, 300          # початок осей
    aw, ah = 540, 240         # розміри поля
    parts = []
    # осі
    parts.append(arrow(ox - 6, oy, ox + aw + 14, oy, color=MUTED, sw=1.3))      # час
    parts.append(arrow(ox, oy + 6, ox, oy - ah - 8, color=MUTED, sw=1.3))       # кут
    parts.append(text(ox + aw + 10, oy + 18, "час", 11, MUTED, "end"))
    parts.append(text(ox - 4, oy - ah - 14, "кут нахилу", 11, MUTED, "middle"))
    # лінія нуля (рівновага) і «перекидання»
    parts.append(line(ox, oy, ox + aw, oy, color=MUTED, sw=1.0, dash="3 4"))
    tip_y = oy - ah + 18
    parts.append(line(ox, tip_y, ox + aw, tip_y, color=POS, sw=1.0, dash="5 4"))
    parts.append(text(ox + aw - 2, tip_y - 6, "перекидання", 10, POS, "end"))

    # старт від малого збурення
    a0 = 14.0                  # початкове відхилення в px
    # БЕЗ контуру: експоненційне зростання до стелі
    grow = []
    for i in range(121):
        t = i / 120.0
        val = a0 * math.exp(3.2 * t)
        y = oy - val
        if y < tip_y:
            grow.append((ox + t * aw, tip_y))
            break
        grow.append((ox + t * aw, y))
    pg = " ".join("%.1f,%.1f" % p for p in grow)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pg, POS))
    parts.append(text(grow[-1][0] - 6, grow[-1][1] - 10, "без контуру: лавина", 11, POS, "end", bold=True))

    # З контуром: те саме збурення згасає назад
    damp = []
    for i in range(121):
        t = i / 120.0
        val = a0 * math.exp(-4.0 * t) * math.cos(7 * t)   # згасальне коливання
        damp.append((ox + t * aw, oy - val))
    pd = " ".join("%.1f,%.1f" % p for p in damp)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pd, FIELD))
    parts.append(text(ox + aw - 4, oy - 26, "з контуром: згасає до нуля", 11, FIELD, "end", bold=True))

    # позначка спільного старту
    parts.append(circle(ox, oy - a0, 4, fill=INK, stroke=INK, sw=1))
    parts.append(text(ox + 6, oy - a0 - 8, "мале збурення", 10, MUTED, "start"))

    render(os.path.join(IMG, "growth.svg"), W, H, *parts,
           title="Те саме збурення: само росте лавиною — або контур гасить його")


# ── Фігура 3: людина не встигає, автомат устигає ──────────────────────────────
# Часова шкала (мс). Час перекидання дрона — десятки мс. Реакція людини —
# сотні мс (запізно). Період автоконтуру — одиниці мс (встигає багато разів).
def fig_timescales():
    W, H = 700, 320
    ax0, ax1 = 90, 620
    axis_y = 150
    parts = []
    # вісь часу 0..400 мс
    tmax = 400.0
    parts.append(arrow(ax0 - 6, axis_y, ax1 + 14, axis_y, color=INK, sw=1.6))
    parts.append(text(ax1 + 12, axis_y + 20, "час, мс", 11, MUTED, "end"))
    # поділки
    for ms in (0, 50, 100, 200, 300, 400):
        x = ax0 + (ms / tmax) * (ax1 - ax0)
        parts.append(line(x, axis_y - 5, x, axis_y + 5, color=MUTED, sw=1.2))
        parts.append(text(x, axis_y + 22, str(ms), 10, MUTED, "middle"))

    def span(ms_a, ms_b, color, y, label, up=True):
        xa = ax0 + (ms_a / tmax) * (ax1 - ax0)
        xb = ax0 + (ms_b / tmax) * (ax1 - ax0)
        frag = line(xa, y, xb, y, color=color, sw=6)
        frag += line(xa, y - 7, xa, y + 7, color=color, sw=2)
        frag += line(xb, y - 7, xb, y + 7, color=color, sw=2)
        ly = y - 14 if up else y + 22
        frag += text((xa + xb) / 2, ly, label, 11, color, "middle", bold=True)
        return frag, xa, xb

    # перекидання: ~30..120 мс (червоний, над віссю)
    f, _, _ = span(30, 120, POS, axis_y - 46, "перекидання апарата: десятки мс")
    parts.append(f)
    # реакція людини: ~250 мс «помітив-зрозумів-рушив» (синій, над віссю далі)
    f, hxa, _ = span(180, 320, NEG, axis_y - 86, "реакція людини: помітити → зрозуміти → рушити")
    parts.append(f)
    parts.append(text(hxa + 6, axis_y - 100, "коли людина лише починає діяти —", 10, NEG, "start"))
    parts.append(text(hxa + 6, axis_y - 114, "апарат уже перекинувся", 10, NEG, "start"))

    # такт автоконтуру: ~2 мс, повторюваний (зелений, під віссю — частокіл)
    dt_ms = 2.0
    n = 18
    for k in range(n):
        x = ax0 + ((k * dt_ms) / tmax) * (ax1 - ax0)
        parts.append(line(x, axis_y + 36, x, axis_y + 56, color=FIELD, sw=2.4))
    xend = ax0 + ((n * dt_ms) / tmax) * (ax1 - ax0)
    parts.append(text(ax0 + 4, axis_y + 78, "такт автоконтуру кожні ~2 мс:", 11, FIELD, "start", bold=True))
    parts.append(text(ax0 + 4, axis_y + 94, "встигає вирівняти десятки разів, поки апарат лише починає падати",
                      10, FIELD, "start"))

    render(os.path.join(IMG, "timescales.svg"), W, H, *parts,
           title="Три часи: падіння — десятки мс, людина — сотні, автомат — одиниці")


# ── Фігура 4: контур керування (замкнена петля) ──────────────────────────────
# Бажаний кут → порівняння → обчислення → мотори → апарат → давач (IMU) →
# назад до порівняння. Петля замкнена; різниця (помилка) керує впливом.
def fig_loop():
    W, H = 720, 340
    parts = []
    cy = 130
    bh = 56

    # координати центрів блоків
    sp_x = 110     # завдання
    cmp_x = 255    # порівняння (різниця)
    ctrl_x = 410   # обчислення впливу
    plant_x = 580  # апарат + мотори

    # блоки
    b1 = textbox(sp_x, cy, "бажаний\nкут", size=12, fill="#eef2f7", stroke=MUTED, sw=1.4, min_w=92)[0]
    parts.append(b1)
    # суматор-порівняння (коло з + та −)
    parts.append(circle(cmp_x, cy, 22, fill="#fff8e1", stroke="#f0b429", sw=2))
    parts.append(text(cmp_x, cy + 5, "−", 18, INK, "middle", bold=True))
    parts.append(text(cmp_x - 20, cy - 22, "помилка", 10, INK, "middle"))
    b3 = textbox(ctrl_x, cy, "обчислити\nвплив", size=12, fill="#eafaf1", stroke=FIELD, sw=1.8, min_w=110)[0]
    parts.append(b3)
    b4 = textbox(plant_x, cy, "мотори →\nапарат", size=12, fill="#fdecea", stroke=POS, sw=1.8, min_w=118)[0]
    parts.append(b4)

    # стрілки прямого шляху
    parts.append(arrow(sp_x + 46, cy, cmp_x - 24, cy, color=INK, sw=1.8))
    parts.append(arrow(cmp_x + 24, cy, ctrl_x - 56, cy, color=INK, sw=1.8))
    parts.append(arrow(ctrl_x + 56, cy, plant_x - 60, cy, color=INK, sw=1.8))
    parts.append(text((ctrl_x + plant_x) / 2, cy - 8, "тяга", 10, MUTED, "middle"))

    # вихід (справжній кут) униз і назад до порівняння
    out_y = cy + 100
    parts.append(arrow(plant_x, cy + 28, plant_x, out_y, color=INK, sw=1.8))
    parts.append(text(plant_x + 6, cy + 64, "справжній кут", 10, MUTED, "start"))
    # давач у зворотному шляху
    sens = textbox((cmp_x + plant_x) / 2, out_y, "давач кута (IMU)",
                   size=12, fill="#eef2f7", stroke=NEG, sw=1.8)[0]
    parts.append(sens)
    sx_left = (cmp_x + plant_x) / 2 - 70
    parts.append(arrow(plant_x, out_y, (cmp_x + plant_x) / 2 + 70, out_y, color=INK, sw=1.8))
    parts.append(arrow(sx_left, out_y, cmp_x, out_y, color=INK, sw=1.8))
    parts.append(arrow(cmp_x, out_y, cmp_x, cy + 24, color=INK, sw=1.8))
    parts.append(text(cmp_x - 20, cy + 22, "+", 16, INK, "middle", bold=True))
    parts.append(text((cmp_x + sx_left) / 2, out_y - 8, "виміряний кут", 10, MUTED, "middle"))

    # підпис-висновок
    parts.append(text(W / 2, H - 22,
                      "петля замкнена: різниця «бажане − виміряне» керує тягою сто разів на секунду",
                      11, INK, "middle"))

    render(os.path.join(IMG, "control-loop.svg"), W, H, *parts,
           title="Контур керування: вимір → різниця → вплив → знову вимір")


fig_equilibrium()
fig_growth()
fig_timescales()
fig_loop()
print("Done. SVG in", IMG)
