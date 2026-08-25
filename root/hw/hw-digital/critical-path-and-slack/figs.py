# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Анатомія перегону: два тригери, шлях даних = t_cq + t_логіки + t_setup ─
def fig_path():
    W, H = 720, 320
    frags = []

    # два тригери
    fw, fh = 96, 96
    y = 110
    x_src, x_dst = 70, 520
    frags.append(rect(x_src, y, fw, fh, fill=FILL, stroke=LINE, sw=1.8, rx=8))
    frags.append(mtext(x_src + fw / 2, y + 34, "тригер\nджерело", size=13, color=INK, bold=True))
    frags.append(text(x_src + fw / 2, y + 78, "Q →", size=13, color=NEG, bold=True))
    frags.append(rect(x_dst, y, fw, fh, fill=FILL, stroke=LINE, sw=1.8, rx=8))
    frags.append(mtext(x_dst + fw / 2, y + 34, "тригер\nприймач", size=13, color=INK, bold=True))
    frags.append(text(x_dst + fw / 2, y + 78, "→ D", size=13, color=NEG, bold=True))

    # хмара логіки посередині
    lx, lw = x_src + fw + 70, 190
    ly, lh = y + 16, 64
    frags.append(rect(lx, ly, lw, lh, fill="#eef2ff", stroke=NEG, sw=1.8, rx=30))
    frags.append(mtext(lx + lw / 2, ly + 26, "комбінаційна\nлогіка + дроти", size=13, color=NEG, bold=True))

    # шлях даних — стрілки
    ymid = y + fh / 2
    frags.append(arrow(x_src + fw, ymid, lx, ymid, color=LINE, sw=2.0))
    frags.append(arrow(lx + lw, ymid, x_dst, ymid, color=LINE, sw=2.0))

    # такт — спільна лінія знизу до обох
    cy = y + fh + 54
    frags.append(line(40, cy, W - 40, cy, color=FIELD, sw=2.0, dash="6,4"))
    frags.append(text(52, cy - 8, "спільний такт", size=12, color=FIELD, bold=True, anchor="start"))
    frags.append(arrow(x_src + fw / 2, cy, x_src + fw / 2, y + fh + 2, color=FIELD, sw=1.6))
    frags.append(arrow(x_dst + fw / 2, cy, x_dst + fw / 2, y + fh + 2, color=FIELD, sw=1.6))

    # підписи трьох доданків над стрілками
    frags.append(text(x_src + fw / 2, y - 16, "t_cq", size=13, color=POS, bold=True))
    frags.append(text(lx + lw / 2, ly - 12, "t_логіки", size=13, color=POS, bold=True))
    frags.append(text(x_dst + fw / 2, y - 16, "t_setup", size=13, color=POS, bold=True))

    # формула-підсумок
    b, w, h = textbox(W / 2, 40, "довжина перегону = t_cq + t_логіки + t_setup",
                      size=14, pad=10, fill="#fdecea", stroke=POS, color=POS, bold=True)
    frags.append(b)

    render(os.path.join(IMG, 'path.svg'), W, H, *frags,
           title="Анатомія перегону між двома тригерами")


# ── 2. Вікна заборони setup і hold навколо фронтів такту ─────────────────────
def fig_setup_hold():
    W, H = 720, 360
    frags = []

    ax0, ax1 = 70, 660          # вісь часу
    yb = 250                    # базова лінія даних
    # два фронти такту
    f0, f1 = 180, 540
    for fx, lab in [(f0, "фронт N"), (f1, "фронт N+1")]:
        frags.append(line(fx, 90, fx, yb + 30, color=FIELD, sw=2.4))
        frags.append(text(fx, 78, lab, size=12, color=FIELD, bold=True))

    # вісь часу
    frags.append(arrow(ax0, yb, ax1, yb, color=INK, sw=2))
    frags.append(text(ax1, yb + 22, "час →", size=12, color=MUTED, anchor="end"))

    # вікно hold після фронту N
    hw = 70
    frags.append(rect(f0, yb - 60, hw, 60, fill="#fdecea", stroke=POS, sw=1.6, rx=3))
    frags.append(text(f0 + hw / 2, yb - 72, "hold", size=12, color=POS, bold=True))
    frags.append(text(f0 + hw / 2, yb - 88, "заборона", size=11, color=POS))

    # вікно setup перед фронтом N+1
    sw_ = 90
    frags.append(rect(f1 - sw_, yb - 60, sw_, 60, fill="#fdecea", stroke=POS, sw=1.6, rx=3))
    frags.append(text(f1 - sw_ / 2, yb - 72, "setup", size=12, color=POS, bold=True))
    frags.append(text(f1 - sw_ / 2, yb - 88, "заборона", size=11, color=POS))

    # дозволене вікно між ними
    gx0, gx1 = f0 + hw, f1 - sw_
    frags.append(rect(gx0, yb - 46, gx1 - gx0, 46, fill="#eaf6ee", stroke=FIELD, sw=1.6, rx=3))
    frags.append(text((gx0 + gx1) / 2, yb - 22, "тут вхід приймача", size=13, color=FIELD, bold=True))
    frags.append(text((gx0 + gx1) / 2, yb - 6, "має право мінятися", size=12, color=FIELD))

    # підписи причин під віссю
    frags.append(mtext(f0 + hw / 2, yb + 40,
                       "прибіжиш зарано —\nзатреш старе, що ще\nзамикається\n(ламають ШВИДКІ шляхи)",
                       size=11, color=MUTED))
    frags.append(mtext(f1 - sw_ / 2, yb + 40,
                       "прибіжиш запізно —\nне встигне застигнути\nдо фронту\n(ламають ПОВІЛЬНІ шляхи)",
                       size=11, color=MUTED))

    render(os.path.join(IMG, 'setup-hold.svg'), W, H, *frags,
           title="Setup і hold — дві заборони навколо фронту")


# ── 3. Родовід поняття: від CPM/PERT великих робіт до STA цифрових схем ───────
def fig_lineage():
    W, H = 760, 380
    frags = []

    # спільна вісь часу
    ax0, ax1 = 60, 700
    ay = 320
    frags.append(arrow(ax0, ay, ax1, ay, color=INK, sw=2))
    frags.append(text(ax1, ay + 22, "час →", size=12, color=MUTED, anchor="end"))
    for yr, xx in [("1957", 150), ("1958", 210), ("1966", 400), ("1982", 610)]:
        frags.append(line(xx, ay - 6, xx, ay + 6, color=INK, sw=2))
        frags.append(text(xx, ay + 22, yr, size=12, color=MUTED, bold=True))

    # три віхи як картки, кожна над своєю позначкою року
    def milestone(cx, top, head_lines, body, accent):
        b, w, h = textbox(cx, top, head_lines, size=13, pad=9,
                          fill="#eef2ff", stroke=accent, color=accent, bold=True, min_w=150)
        frags.append(b)
        frags.append(mtext(cx, top + h / 2 + 16, body, size=11, color=MUTED))
        # ніжка до осі
        frags.append(line(cx, top + h / 2 + 16 + len(body.split("\n")) * 11 * 1.3,
                          cx, ay - 4, color=accent, sw=1.4, dash="4,3"))

    milestone(180, 70, "CPM / PERT\n(великі роботи)",
              "критичний шлях у\nмережі задач проєкту:\nDuPont, Polaris", NEG)
    milestone(400, 70, "Kirkpatrick &\nClark, IBM",
              "«PERT як помічник\nу логічному дизайні» —\nметод ліг на схему", FIELD)
    milestone(610, 70, "Hitchcock,\nSmith, Cheng",
              "arrival · required · slack;\nчас рахунку ∝ числу\nвентилів → STA", POS)

    # підпис-нитка знизу
    b, w, h = textbox(W / 2, 358, "той самий найдовший ланцюг залежностей — спершу в задачах, потім у вентилях",
                      size=12, pad=8, fill="#eaf6ee", stroke=FIELD, color=FIELD, bold=True)
    frags.append(b)

    render(os.path.join(IMG, 'lineage.svg'), W, H, *frags,
           title="Родовід критичного шляху: від планування робіт до аналізу схем")


# ── 4. Дві хвилі графом: arrival уперед (max+затримка), required назад (min−) ─
def fig_arrival_required():
    W, H = 720, 340
    frags = []

    r = 22
    xin = 120
    ins = [(xin, 92, "2.0"), (xin, 175, "2.7"), (xin, 258, "1.3")]
    xg = 380
    yg = 175
    xd = 620

    # ребра-затримки від входів до вентиля
    for (ix, iy, a) in ins:
        frags.append(arrow(ix + r, iy, xg - r - 6, yg, color=LINE, sw=1.8))
    # вузли-входи (arrival на них)
    for (ix, iy, a) in ins:
        frags.append(circle(ix, iy, r, fill="#eaf0fd", stroke=NEG, sw=2))
        frags.append(text(ix, iy + 5, a, size=14, color=NEG, bold=True))
    # вентиль
    frags.append(circle(xg, yg, r + 6, fill="#eef2ff", stroke=NEG, sw=2.2))
    frags.append(text(xg, yg + 5, "+2.3", size=13, color=INK, bold=True))
    frags.append(text(xg, yg - r - 18, "вентиль", size=12, color=MUTED))
    # ребро до приймача
    frags.append(arrow(xg + r + 6, yg, xd - r, yg, color=LINE, sw=1.8))
    frags.append(circle(xd, yg, r, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(xd, yg + 5, "5.0", size=14, color=NEG, bold=True))
    frags.append(text(xd, yg + r + 22, "далі →", size=12, color=MUTED))

    # позначити переможця max (середній вхід 2.7)
    frags.append(text(xin - r - 6, 175 + 5, "max", size=11, color=POS, bold=True, anchor="end"))

    # формула arrival згори
    b, w, h = textbox(xg, 40, "arrival = max(входи) + затримка = max(2.0, 2.7, 1.3) + 2.3 = 5.0",
                      size=13, pad=9, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    frags.append(b)

    # формула required знизу (дзеркальна)
    b2, w2, h2 = textbox(xg, H - 28, "required(вузла) = min(виходи) − затримка   —   хвиля назад від дедлайну",
                         size=13, pad=9, fill="#eaf6ee", stroke=FIELD, color=FIELD, bold=True)
    frags.append(b2)

    render(os.path.join(IMG, 'arrival-required.svg'), W, H, *frags,
           title="Дві хвилі: arrival уперед бере max, required назад бере min")


# ── 5. Робочий граф: кілька шляхів, критичний виділено, слек на приймачах ─────
def fig_worked_graph():
    import math
    W, H = 760, 400
    frags = []
    r = 24

    P = {
        "A":  (70, 96),  "B": (70, 250),
        "G1": (240, 96), "G2": (240, 250),
        "G3": (430, 170), "G4": (610, 170), "D1": (705, 170),
        "G5": (430, 330), "D2": (610, 330),
    }
    crit = {("B", "G2"), ("G2", "G3"), ("G3", "G4"), ("G4", "D1")}
    edges = [("A", "G1"), ("G1", "G3"), ("B", "G2"), ("G2", "G3"),
             ("G3", "G4"), ("G4", "D1"), ("G2", "G5"), ("G5", "D2")]
    for (u, v) in edges:
        ux, uy = P[u]; vx, vy = P[v]
        dx, dy = vx - ux, vy - uy
        L = math.hypot(dx, dy)
        ux2, uy2 = ux + dx / L * r, uy + dy / L * r
        vx2, vy2 = vx - dx / L * r, vy - dy / L * r
        if (u, v) in crit:
            frags.append(arrow(ux2, uy2, vx2, vy2, color=POS, sw=3.0))
        else:
            frags.append(arrow(ux2, uy2, vx2, vy2, color=MUTED, sw=1.6))

    NODE = {
        "A":  ("A", "0.6"), "B": ("B", "0.6"),
        "G1": ("G1\n+1.4", "2.0"), "G2": ("G2\n+2.1", "2.7"),
        "G3": ("G3\n+2.3", "5.0"), "G4": ("G4\n+1.8", "6.8"),
        "G5": ("G5\n+0.4", "3.1"),
        "D1": ("D1", "6.8"), "D2": ("D2", "3.1"),
    }
    oncrit_nodes = {"B", "G2", "G3", "G4", "D1"}
    for k, (ux, uy) in P.items():
        lab, arr = NODE[k]
        oncrit = k in oncrit_nodes
        if k in ("D1", "D2"):
            fill = "#fdecea" if oncrit else "#f4f6f8"
            stroke = POS if oncrit else LINE
            frags.append(rect(ux - r, uy - r, 2 * r, 2 * r, fill=fill, stroke=stroke, sw=2.2, rx=5))
            frags.append(text(ux, uy - 2, lab, size=13, color=INK, bold=True))
        else:
            fill = "#fdecea" if oncrit else "#eaf0fd"
            stroke = POS if oncrit else NEG
            frags.append(circle(ux, uy, r, fill=fill, stroke=stroke, sw=2.2))
            frags.append(mtext(ux, uy - 3, lab, size=11, color=INK, bold=True, lh=1.15))
        frags.append(text(ux, uy + r + 15, "a=" + arr, size=11, color=NEG, bold=True))

    frags.append(text(P["D1"][0], P["D1"][1] - r - 12, "слек +0.7", size=12, color=POS, bold=True))
    frags.append(text(P["D2"][0], P["D2"][1] - r - 12, "слек +4.4", size=12, color=FIELD, bold=True))

    b, w, h = textbox(W / 2, H - 24,
                      "required на входах приймачів = T − t_setup = 8.0 − 0.5 = 7.5 нс",
                      size=12, pad=8, fill="#eaf6ee", stroke=FIELD, color=FIELD, bold=True)
    frags.append(b)
    frags.append(text(24, H - 30, "червоне —", size=12, color=POS, bold=True, anchor="start"))
    frags.append(text(24, H - 14, "критичний шлях", size=12, color=POS, anchor="start"))

    render(os.path.join(IMG, 'worked-graph.svg'), W, H, *frags,
           title="Робочий граф: дві хвилі дали слек на кожному приймачі")


if __name__ == "__main__":
    fig_path()
    fig_setup_hold()
    fig_lineage()
    fig_arrival_required()
    fig_worked_graph()
    print("figures written to", IMG)
