# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Схема інвертора: два ключі спина-до-спини ────────────────────────────
def fig_schematic():
    W, H = 560, 360
    e = []
    e.append(text(W / 2, 28, "Два комплементарні ключі між живленням і землею", size=16, bold=True))

    xmid = 300           # спільний стовп
    yvdd = 70
    ygnd = 300
    xin = 120

    # рейки
    e.append(line(xmid - 120, yvdd, xmid + 120, yvdd, color=POS, sw=2.5))
    e.append(text(xmid + 130, yvdd + 5, "+V_DD", size=14, color=POS, anchor="start", bold=True))
    e.append(line(xmid - 120, ygnd, xmid + 120, ygnd, color=NEG, sw=2.5))
    e.append(text(xmid + 130, ygnd + 5, "0 В (земля)", size=13, color=NEG, anchor="start"))

    # PMOS зверху
    b1 = fitbox(xmid - 55, yvdd + 25, 110, 55, "PMOS\n(верхній ключ)", size=13,
                fill="#fdecea", stroke=POS, bold=True)
    e.append(b1)
    # NMOS знизу
    b2 = fitbox(xmid - 55, ygnd - 80, 110, 55, "NMOS\n(нижній ключ)", size=13,
                fill="#eaf0fd", stroke=NEG, bold=True)
    e.append(b2)

    # з'єднання рейки-PMOS, PMOS-вихід, вихід-NMOS, NMOS-земля
    e.append(line(xmid, yvdd, xmid, yvdd + 25, color=LINE, sw=2))
    e.append(line(xmid, yvdd + 80, xmid, ygnd - 80, color=LINE, sw=2))
    e.append(line(xmid, ygnd - 25, xmid, ygnd, color=LINE, sw=2))

    # вузол виходу
    youtnode = (yvdd + 80 + ygnd - 80) / 2
    e.append(circle(xmid, youtnode, 4, fill=INK, stroke=INK))
    e.append(line(xmid, youtnode, xmid + 150, youtnode, color=LINE, sw=2))
    e.append(text(xmid + 155, youtnode - 8, "вихід", size=13, anchor="start", bold=True))
    e.append(text(xmid + 155, youtnode + 12, "V_out", size=13, anchor="start", color=MUTED))

    # вхід — на обидва затвори
    e.append(line(xin, youtnode, xin, youtnode, color=LINE))  # noop
    e.append(text(xin - 5, youtnode - 8, "вхід", size=13, anchor="end", bold=True))
    e.append(text(xin - 5, youtnode + 12, "V_in", size=13, anchor="end", color=MUTED))
    e.append(circle(xin, youtnode, 4, fill=INK, stroke=INK))
    e.append(line(xin, youtnode, xin, yvdd + 52, color=LINE, sw=2))
    e.append(line(xin, yvdd + 52, xmid - 55, yvdd + 52, color=LINE, sw=2))
    e.append(line(xin, youtnode, xin, ygnd - 52, color=LINE, sw=2))
    e.append(line(xin, ygnd - 52, xmid - 55, ygnd - 52, color=LINE, sw=2))

    # підпис-логіка
    e.append(text(W / 2, H - 14,
                  "вхід «0» → верхній відкритий → вихід тягне до +V_DD;   вхід «1» → нижній відкритий → вихід до 0",
                  size=11.5, color=MUTED))

    render(os.path.join(OUT, "schematic.svg"), W, H, *e)


# ── 2. Сама передавальна крива з п'ятьма ділянками ──────────────────────────
def fig_vtc():
    import math
    W, H = 620, 440
    e = []
    e.append(text(W / 2, 28, "Передавальна характеристика: вихід проти входу", size=16, bold=True))

    # рамка графіка
    x0, y0 = 90, 70          # лівий-верх осей
    gw, gh = 440, 300
    xr, yb = x0 + gw, y0 + gh
    VDD = 1.0

    def px(v):   # 0..VDD -> екран X
        return x0 + v / VDD * gw

    def py(v):   # 0..VDD -> екран Y (перевернуто)
        return yb - v / VDD * gh

    # осі
    e.append(line(x0, y0, x0, yb, color=INK, sw=1.8))
    e.append(line(x0, yb, xr, yb, color=INK, sw=1.8))
    e.append(text(x0 - 12, y0 + 4, "V_DD", size=12, anchor="end", color=MUTED))
    e.append(text(x0 - 12, yb + 4, "0", size=12, anchor="end", color=MUTED))
    e.append(text(px(VDD), yb + 20, "V_DD", size=12, color=MUTED))
    e.append(text(xr + 6, yb + 4, "V_in", size=13, anchor="start", bold=True))
    e.append(text(x0 - 40, y0 - 6, "V_out", size=13, anchor="start", bold=True))

    # крива: майже плоско — крутий обрив — майже плоско
    VM = 0.5
    steep = 26.0
    pts = []
    N = 240
    for i in range(N + 1):
        vin = i / N * VDD
        # логістичний перехід навколо VM (тільки для форми кривої)
        vout = VDD / (1.0 + math.exp(steep * (vin - VM)))
        pts.append((px(vin), py(vout)))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    e.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, FIELD))

    # діагональ V_out = V_in (для VM)
    e.append(line(px(0), py(0), px(VDD), py(VDD), color=MUTED, sw=1.2, dash="4 4"))
    e.append(text(px(0.86), py(0.94), "V_out = V_in", size=11, color=MUTED, anchor="start"))

    # точка VM
    e.append(circle(px(VM), py(VM), 5, fill=POS, stroke=POS))
    e.append(line(px(VM), yb, px(VM), py(VM), color=POS, sw=1, dash="3 3"))
    e.append(text(px(VM), yb + 20, "V_M", size=13, color=POS, bold=True))

    # вертикальні межі ділянок (умовні пороги)
    for vx, lab in [(0.20, ""), (0.42, ""), (0.58, ""), (0.80, "")]:
        e.append(line(px(vx), y0, px(vx), yb, color="#dddddd", sw=1))

    # підписи ділянок (I..V) над віссю
    zones = [(0.10, "I"), (0.31, "II"), (0.50, "III"), (0.69, "IV"), (0.90, "V")]
    for vx, lab in zones:
        e.append(text(px(vx), y0 - 6, lab, size=12, color=MUTED, bold=True))

    # плато VOH / VOL
    e.append(text(px(0.06), py(0.97), "V_OH", size=11, color=MUTED, anchor="start"))
    e.append(text(px(0.78), py(0.05), "V_OL", size=11, color=MUTED, anchor="start"))

    # пояснення внизу
    e.append(text(W / 2, H - 14,
                  "плоскі краї — чисті «0»/«1»; крута ділянка III (обидва в насиченні) — велике підсилення",
                  size=11.5, color=MUTED))

    render(os.path.join(OUT, "vtc.svg"), W, H, *e)


# ── 3. Наскрізний струм: пік рівно посередині переходу ──────────────────────
def fig_shoot_through():
    import math
    W, H = 600, 320
    e = []
    e.append(text(W / 2, 28, "Струм від живлення проти входу: пік лише в переході", size=15.5, bold=True))

    x0, y0 = 80, 70
    gw, gh = 460, 190
    xr, yb = x0 + gw, y0 + gh
    VDD = 1.0

    def px(v):
        return x0 + v / VDD * gw

    e.append(line(x0, y0, x0, yb, color=INK, sw=1.8))
    e.append(line(x0, yb, xr, yb, color=INK, sw=1.8))
    e.append(text(xr + 6, yb + 4, "V_in", size=13, anchor="start", bold=True))
    e.append(text(x0 - 8, y0 - 6, "I", size=13, anchor="end", bold=True))
    e.append(text(x0 - 8, y0 + 8, "струм", size=10, anchor="end", color=MUTED))

    # дзвіночок навколо VM
    VM = 0.5
    sig = 0.11
    pts = []
    N = 220
    for i in range(N + 1):
        vin = i / N * VDD
        y = math.exp(-((vin - VM) ** 2) / (2 * sig * sig))
        pts.append((px(vin), yb - y * (gh - 12)))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    e.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, POS))

    e.append(line(px(VM), yb, px(VM), yb - (gh - 12), color=POS, sw=1, dash="3 3"))
    e.append(text(px(VM), yb + 20, "V_M", size=13, color=POS, bold=True))
    e.append(text(px(0.10), yb + 20, "0", size=12, color=MUTED))
    e.append(text(px(0.90), yb + 20, "V_DD", size=12, color=MUTED))

    e.append(text(px(0.12), y0 + 30, "~0", size=12, color=MUTED, anchor="middle"))
    e.append(text(px(0.88), y0 + 30, "~0", size=12, color=MUTED, anchor="middle"))

    e.append(text(W / 2, H - 12,
                  "у станах «0» і «1» один ключ завжди закритий — струм майже нуль; енергія йде лише під час перемикання",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "shoot-through.svg"), W, H, *e)


# ── 4. Точка перемикання V_M на осі входу для різних r ──────────────────────
def fig_vm_vs_r():
    import math
    W, H = 620, 380
    e = []
    e.append(text(W / 2, 28, "Куди сідає точка перемикання V_M залежно від сили r", size=15.5, bold=True))

    # числа прикладу
    VDD = 3.3
    VTN = 0.6
    VTP = 0.7   # |V_Tp|

    def vm(r):
        s = math.sqrt(r)
        return (VDD - VTP + VTN * s) / (1.0 + s)

    x0, y0 = 90, 78
    gw, gh = 440, 210
    xr, yb = x0 + gw, y0 + gh

    def px(v):        # напруга 0..VDD -> екран X
        return x0 + v / VDD * gw

    # горизонтальна вісь входу (напруга)
    e.append(line(x0, yb, xr, yb, color=INK, sw=1.8))
    e.append(text(xr + 6, yb + 4, "V_in", size=13, anchor="start", bold=True))
    for v, lab in [(0.0, "0"), (VTN, "V_Tn"), (VDD / 2, "V_DD/2"), (VDD - VTP, "V_DD−|V_Tp|"), (VDD, "V_DD")]:
        e.append(line(px(v), yb - 4, px(v), yb + 4, color=INK, sw=1.4))
        e.append(text(px(v), yb + 20, lab, size=10.5, color=MUTED))

    # межі, між якими бігає V_M (пороги)
    e.append(line(px(VTN), y0 + 10, px(VTN), yb, color="#dddddd", sw=1, dash="4 4"))
    e.append(line(px(VDD - VTP), y0 + 10, px(VDD - VTP), yb, color="#dddddd", sw=1, dash="4 4"))
    # центр
    e.append(line(px(VDD / 2), y0 + 10, px(VDD / 2), yb, color=FIELD, sw=1, dash="3 3"))

    # маркери V_M для набору r; підпис r ліворуч, значення V_M над точкою
    rows = [
        (0.1, "r = 0.1  (PMOS набагато сильніший)"),
        (0.5, "r = 0.5"),
        (1.0, "r = 1     (баланс → V_DD/2)"),
        (2.8, "r ≈ 2.8  (однакова ширина: NMOS сильніший)"),
        (10.0, "r = 10   (NMOS набагато сильніший)"),
    ]
    n = len(rows)
    for i, (r, lab) in enumerate(rows):
        yy = y0 + 14 + i * (gh - 24) / (n - 1)
        v = vm(r)
        col = FIELD if abs(r - 1.0) < 1e-9 else POS
        e.append(circle(px(v), yy, 5, fill=col, stroke=col))
        e.append(text(px(v), yy - 10, "%.2f В" % v, size=10.5, color=col, bold=True))
        e.append(text(x0 - 8, yy + 4, lab, size=10.5, color=MUTED, anchor="end"))

    # стрілка напрямку руху
    e.append(text(px(VTN) + 4, y0 + 4, "↑ r росте → V_M сюди", size=10, color=MUTED, anchor="start"))
    e.append(text(px(VDD - VTP) - 4, y0 + 4, "r падає → V_M сюди ↑", size=10, color=MUTED, anchor="end"))

    e.append(text(W / 2, H - 12,
                  "V_M — зважене середнє двох порогових меж; вага √r монотонно рухає його між ними",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "vm-vs-r.svg"), W, H, *e)


if __name__ == "__main__":
    fig_schematic()
    fig_vtc()
    fig_shoot_through()
    fig_vm_vs_r()
    print("figures written to", OUT)
