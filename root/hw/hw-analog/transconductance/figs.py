# -*- coding: utf-8 -*-
"""Фігури до теми «Крутість (gm)».
Три фігури:
  vtoi.svg    — суть: напруга на вході керує струмом на виході (gm — «обмінний курс»)
  slope.svg   — gm як нахил кривої I(V) у робочій точці; крута vs полога
  devices.svg — одна роль, різні прилади: BJT / MOSFET / лампа дають струм від напруги
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Суть: напруга → струм, gm як коефіцієнт ──────────────────────────────
def fig_vtoi():
    W, H = 720, 320
    f = []
    # вхід: маленька синусоїда напруги ліворуч
    cx_in, cy_in = 120, 160
    f.append(text(cx_in, 48, "вхід: напруга", size=14, color=MUTED, bold=True))
    # вісь напруги
    f.append(line(cx_in - 70, cy_in, cx_in + 70, cy_in, color=MUTED, sw=1))
    pts = []
    for i in range(0, 141):
        x = cx_in - 70 + i
        ph = (i / 140.0) * 2 * math.pi * 2
        y = cy_in - 22 * math.sin(ph)
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), NEG))
    f.append(text(cx_in, cy_in + 56, "vᵢₙ  (мВ)", size=14, color=NEG, bold=True))

    # коробка-прилад у центрі
    bx, by, bw, bh = 290, 110, 150, 100
    f.append(rect(bx, by, bw, bh, fill="#eef7f0", stroke=FIELD, sw=2.2, rx=10))
    f.append(mtext(bx + bw / 2, by + 40, ["крутість", "gm"], size=18, color=FIELD, bold=True))
    f.append(text(bx + bw / 2, by + 80, "А на кожен В", size=12.5, color=MUTED))

    # стрілка вхід → коробка
    f.append(arrow(cx_in + 78, cy_in, bx - 8, by + bh / 2, color=INK, sw=2))
    # стрілка коробка → вихід
    f.append(arrow(bx + bw + 8, by + bh / 2, 560, 160, color=INK, sw=2))

    # вихід: синусоїда струму праворуч (та сама форма, більша)
    cx_out, cy_out = 630, 160
    f.append(text(cx_out, 48, "вихід: струм", size=14, color=MUTED, bold=True))
    f.append(line(cx_out - 70, cy_out, cx_out + 70, cy_out, color=MUTED, sw=1))
    pts = []
    for i in range(0, 141):
        x = cx_out - 70 + i
        ph = (i / 140.0) * 2 * math.pi * 2
        y = cy_out - 40 * math.sin(ph)
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), POS))
    f.append(text(cx_out, cy_out + 70, "iₒᵤₜ = gm · vᵢₙ  (мА)", size=14, color=POS, bold=True))

    render(os.path.join(IMG, "vtoi.svg"), W, H, *f,
           title="Крутість перетворює напругу на вході у струм на виході")


# ── 2. gm як нахил кривої I(V) ──────────────────────────────────────────────
def fig_slope():
    W, H = 720, 380
    f = []
    ox, oy = 90, 320          # початок осей
    ax_w, ax_h = 560, 250
    # осі
    f.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=1.6))
    f.append(text(ox + ax_w - 6, oy + 26, "напруга на вході  V", size=13, color=INK, anchor="end"))
    f.append(text(ox - 14, oy - ax_h + 4, "струм  I", size=13, color=INK, anchor="end"))

    # експонентна крива I(V)
    def curve_y(t):  # t у 0..1
        return oy - (ax_h - 20) * (math.exp(3.0 * t) - 1) / (math.exp(3.0) - 1)
    pts = []
    for i in range(0, 101):
        t = i / 100.0
        x = ox + 30 + t * (ax_w - 60)
        pts.append("%.1f,%.1f" % (x, curve_y(t)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), INK))

    # робоча точка Q на кривій
    tq = 0.62
    qx = ox + 30 + tq * (ax_w - 60)
    qy = curve_y(tq)
    # дотична в Q (числовий нахил)
    dt = 0.012
    x1 = ox + 30 + (tq - dt) * (ax_w - 60); y1 = curve_y(tq - dt)
    x2 = ox + 30 + (tq + dt) * (ax_w - 60); y2 = curve_y(tq + dt)
    slope = (y2 - y1) / (x2 - x1)
    # подовжити дотичну
    L = 150
    dx = L / math.sqrt(1 + slope * slope)
    f.append(line(qx - dx, qy - slope * dx, qx + dx, qy + slope * dx, color=FIELD, sw=2.6, dash="2,0"))
    f.append(circle(qx, qy, 6, fill=POS, stroke=POS, sw=1))
    f.append(text(qx + 12, qy - 12, "Q — робоча точка", size=13, color=POS, bold=True, anchor="start"))

    # трикутник нахилу ΔI / ΔV
    tri_dx = 70
    txq = qx - 20
    ty1 = qy - slope * (-20)        # на дотичній лівіше Q
    bx0 = txq
    by0 = qy - slope * (txq - qx)
    bx1 = txq + tri_dx
    by1 = qy - slope * (bx1 - qx)
    f.append(line(bx0, by0, bx1, by0, color=MUTED, sw=1.4))       # ΔV (горизонталь)
    f.append(line(bx1, by0, bx1, by1, color=MUTED, sw=1.4))       # ΔI (вертикаль)
    f.append(text((bx0 + bx1) / 2, by0 + 18, "ΔV", size=13, color=MUTED, bold=True))
    f.append(text(bx1 + 16, (by0 + by1) / 2, "ΔI", size=13, color=MUTED, bold=True, anchor="start"))

    # підпис нахилу
    b, w0, h0 = textbox(ox + ax_w - 150, oy - ax_h + 64, "gm = ΔI / ΔV\n(нахил у точці Q)",
                        size=14, color=FIELD, stroke=FIELD, fill="#eef7f0", bold=True)
    f.append(b)

    # натяк: полога ділянка = малий gm
    f.append(text(ox + 70, oy - 40, "полого → малий gm", size=12, color=MUTED, anchor="start"))
    f.append(text(qx + 30, qy - 70, "круто → великий gm", size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "slope.svg"), W, H, *f,
           title="Крутість — це нахил кривої «струм від напруги» в робочій точці")


# ── 3. Одна роль, різні прилади ─────────────────────────────────────────────
def fig_devices():
    W, H = 720, 300
    f = []
    cols = [
        ("BJT", "вхід: Vбаза", "gm = I_C / V_T", "≈ 38·I (мА/В)", NEG),
        ("MOSFET", "вхід: V_GS", "gm = 2·I_D / (V_GS−V_th)", "росте як √I", FIELD),
        ("лампа (тріод)", "вхід: V_сітка", "gm = ΔI_анод / ΔV_сітка", "1…10 мА/В", POS),
    ]
    bw, gap = 210, 18
    total = len(cols) * bw + (len(cols) - 1) * gap
    x0 = (W - total) / 2
    y0 = 70
    bh = 165
    for i, (name, vin, formula, note, col) in enumerate(cols):
        x = x0 + i * (bw + gap)
        f.append(rect(x, y0, bw, bh, fill=FILL, stroke=col, sw=2, rx=10))
        f.append(text(x + bw / 2, y0 + 30, name, size=16, color=col, bold=True))
        f.append(text(x + bw / 2, y0 + 58, vin + " керує струмом", size=12.5, color=MUTED))
        # формула у власній рамці, щоб не вилазила
        f.append(fitbox(x + 14, y0 + 74, bw - 28, 34, formula, size=13, color=INK, bold=True,
                        fill="#ffffff", stroke=MUTED, sw=1))
        f.append(text(x + bw / 2, y0 + 134, note, size=12.5, color=col, bold=True))

    f.append(text(W / 2, y0 + bh + 36,
                  "Прилади різні, формули різні — роль одна: напруга на вході задає струм на виході.",
                  size=13.5, color=INK))
    render(os.path.join(IMG, "devices.svg"), W, H, *f,
           title="Крутість — спільна мова трьох підсилювальних приладів")


if __name__ == "__main__":
    fig_vtoi()
    fig_slope()
    fig_devices()
    print("OK: figures written to", IMG)
