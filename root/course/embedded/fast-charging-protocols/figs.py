# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: чому швидка зарядка важка — пляшкове горло на комірці + тепло ──
def fig_why_hard():
    W, H = 760, 380
    p = []
    p.append(text(W/2, 26, "Швидко взяти струм не можна: комірка диктує, а тепло карає", size=17, bold=True))

    # Ліва панель: крива CC/CV
    ax_x, ax_y, ax_w, ax_h = 70, 90, 290, 210
    p.append(rect(ax_x, ax_y, ax_w, ax_h, fill=BG, stroke=MUTED, sw=1.2))
    # осі
    p.append(line(ax_x, ax_y, ax_x, ax_y+ax_h, color=INK, sw=1.6))
    p.append(line(ax_x, ax_y+ax_h, ax_x+ax_w, ax_y+ax_h, color=INK, sw=1.6))
    p.append(text(ax_x-8, ax_y+12, "струм", size=11, color=MUTED, anchor="end"))
    p.append(text(ax_x+ax_w, ax_y+ax_h+18, "час", size=11, color=MUTED, anchor="end"))
    # фаза CC: горизонталь високого струму
    cc_x2 = ax_x + ax_w*0.45
    i_top = ax_y + 30
    p.append(line(ax_x, i_top, cc_x2, i_top, color=POS, sw=3))
    # фаза CV: спад струму (експонента)
    import math
    pts = []
    for k in range(0, 61):
        t = k/60.0
        xx = cc_x2 + t*(ax_x+ax_w - cc_x2)
        yy = i_top + (ax_y+ax_h-12 - i_top)*(1 - math.exp(-3.2*t))
        pts.append("%.1f,%.1f" % (xx, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), NEG))
    p.append(line(cc_x2, ax_y, cc_x2, ax_y+ax_h, color=MUTED, sw=1, dash="4,4"))
    p.append(text((ax_x+cc_x2)/2, i_top-10, "CC: повний струм", size=11, color=POS, bold=True))
    p.append(text(cc_x2+90, ax_y+60, "CV: струм спадає", size=11, color=NEG, bold=True))
    p.append(text(ax_x+ax_w/2, ax_y+ax_h+34, "комірка бере багато лише на початку", size=11, color=MUTED))

    # Права панель: три джерела тепла вздовж шляху струму
    bx = 410
    p.append(text(bx+165, 105, "Куди йде зайва потужність → у тепло", size=12, bold=True))
    # ланцюг адаптер → кабель → комірка
    spots = [
        (bx+55,  165, "в адаптері\n(перетворення)"),
        (bx+165, 165, "на кабелі\nI²·R"),
        (bx+285, 165, "у комірці\n(внутр. опір)"),
    ]
    boxes = []
    for sx, sy, lbl in spots:
        b, bw, _ = textbox(sx, sy, lbl, size=11, fill="#fdecea", stroke=POS, min_w=96)
        boxes.append((sx, bw))
        p.append(b)
    # стрілки потоку між осередками
    p.append(arrow(boxes[0][0]+boxes[0][1]/2, 165, boxes[1][0]-boxes[1][1]/2, 165, color=MUTED))
    p.append(arrow(boxes[1][0]+boxes[1][1]/2, 165, boxes[2][0]-boxes[2][1]/2, 165, color=MUTED))
    p.append(text(bx+165, 240, "удвічі більший струм → учетверо більше тепла", size=12, color=POS, bold=True))
    p.append(text(bx+165, 262, "одразу в усіх трьох місцях", size=11, color=POS))
    p.append(text(bx+165, 290, "а гаряча комірка швидко старіє", size=11, color=MUTED, italic=True))
    p.append(text(bx+165, 308, "і стає небезпечною", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, 'why-hard.svg'), W, H, *p)


# ── Фігура 2: де регулювати — підняти напругу vs низька-V/висока-I ──────────
def fig_where_regulate():
    W, H = 770, 380
    p = []
    p.append(text(W/2, 26, "Дві філософії: гнати високу напругу — чи понизити її в самому адаптері", size=16, bold=True))

    def cable(x1, x2, y, label, hot):
        col = POS if hot else FIELD
        out = line(x1, y, x2, y, color=col, sw=5)
        out += line(x1, y+18, x2, y+18, color=col, sw=5)
        out += text((x1+x2)/2, y-10, label, size=12, color=col, bold=True, anchor="middle")
        return out

    # Верх: «підняти напругу» (QC/PD)
    ytop = 95
    a1, _, _ = textbox(110, ytop, "Адаптер\n9–20 В", size=12, fill=FILL, stroke=LINE, min_w=110)
    p.append(a1)
    p.append(cable(175, 520, ytop, "малий струм → кабель ХОЛОДНИЙ", False))
    d1, _, _ = textbox(600, ytop, "Пристрій:\nперетворювач\n9–20 В → у комірку", size=11, fill=FILL, stroke=LINE, min_w=150)
    p.append(d1)
    p.append(text(W/2, ytop+48, "тепло перетворення — у ПРИСТРОЇ (де тісно й нема куди його дівати)",
                  size=11, color=POS))
    lab1, _, _ = textbox(110, ytop+78, "QC, PD", size=12, bold=True, fill="#eef7f0", stroke=FIELD, min_w=110)
    p.append(lab1)

    # роздільник
    p.append(line(40, 205, W-40, 205, color=MUTED, sw=1, dash="5,5"))

    # Низ: «низька напруга, високий струм» (VOOC)
    ybot = 270
    a2, _, _ = textbox(110, ybot, "Адаптер:\nперетворювач\nусередині", size=11, fill="#eef7f0", stroke=FIELD, min_w=130)
    p.append(a2)
    p.append(cable(185, 520, ybot, "великий струм → кабель ГРІЄТЬСЯ (товстий, з чипом)", True))
    d2, _, _ = textbox(610, ybot, "Пристрій:\nмайже прямо\nу комірку", size=11, fill=FILL, stroke=LINE, min_w=130)
    p.append(d2)
    p.append(text(W/2, ybot+48, "тепло перетворення — у АДАПТЕРІ (великому, з власним радіатором)",
                  size=11, color=FIELD))
    lab2, _, _ = textbox(110, ybot+78, "VOOC", size=12, bold=True, fill="#eef7f0", stroke=FIELD, min_w=130)
    p.append(lab2)

    render(os.path.join(IMG, 'where-regulate.svg'), W, H, *p)


# ── Фігура 3: дільник навпіл (charge pump) — кабель несе вдвічі менший струм ─
def fig_charge_pump():
    W, H = 770, 320
    p = []
    p.append(text(W/2, 26, "Дільник навпіл: висока напруга по кабелю, удвічі менший струм, учетверо менші втрати", size=15, bold=True))

    ymid = 170
    # Адаптер
    a, _, _ = textbox(95, ymid, "Адаптер\n(PPS)\n≈ 2·Vбат", size=12, fill=FILL, stroke=LINE, min_w=120)
    p.append(a)
    # кабель: малий струм I
    p.append(line(160, ymid, 360, ymid, color=FIELD, sw=5))
    p.append(line(160, ymid+16, 360, ymid+16, color=FIELD, sw=5))
    p.append(text(260, ymid-12, "струм  I", size=13, color=FIELD, bold=True))
    p.append(text(260, ymid+40, "втрати  I²·R", size=12, color=FIELD))
    # Дільник навпіл
    cp, _, _ = textbox(440, ymid, "Дільник\nнавпіл  2:1\n(charge pump)", size=12, fill="#eaf0fd", stroke=NEG, min_w=140)
    p.append(cp)
    # коротка шина: великий струм 2I
    p.append(line(515, ymid, 600, ymid, color=POS, sw=6))
    p.append(line(515, ymid+16, 600, ymid+16, color=POS, sw=6))
    p.append(text(557, ymid-12, "2·I", size=13, color=POS, bold=True))
    p.append(text(557, ymid+40, "коротко", size=11, color=MUTED))
    # Комірка
    b, _, _ = textbox(670, ymid, "Комірка\nVбат", size=12, fill="#eaf0fd", stroke=NEG, min_w=90)
    p.append(b)

    # Підсумкова рамка з рівнянням
    eq = ("Та сама потужність до комірки, але по кабелю йде I, а не 2·I.\n"
          "Половина струму → чверть втрат на кабелі (бо втрати ∝ струм²).")
    p.append(fitbox(150, 250, 470, 54, eq, size=12, fill="#eef7f0", stroke=FIELD))

    render(os.path.join(IMG, 'charge-pump.svg'), W, H, *p)


# ── Фігура 4: дільник 2:1 проти лінійного гасіння (для math-вставки) ─────────
def fig_divider_vs_linear():
    W, H = 770, 360
    p = []
    p.append(text(W/2, 26, "Та сама напруга 8 В → 4 В: дільник перекладає заряд, лінійник його спалює", size=15, bold=True))

    # роздільна вертикаль між панелями
    p.append(line(W/2, 56, W/2, H-20, color=MUTED, sw=1, dash="5,5"))

    # ── Ліва панель: ідеальний дільник 2:1 ──
    lx = W/4
    p.append(text(lx, 62, "Дільник навпіл 2:1", size=14, bold=True, color=NEG))
    # вхід
    inb, inw, _ = textbox(lx-110, 130, "Вхід\n8 В · I", size=12, fill=FILL, stroke=LINE, min_w=96)
    p.append(inb)
    # вузол із конденсатором (перекладання заряду)
    cpb, cpw, _ = textbox(lx+70, 130, "перекладає\nзаряд\nконденсатором", size=11, fill="#eaf0fd", stroke=NEG, min_w=120)
    p.append(cpb)
    p.append(arrow(lx-110+inw/2, 130, lx+70-cpw/2, 130, color=MUTED))
    # вихід
    outb, _, _ = textbox(lx, 210, "Вихід\n4 В · 2I", size=12, fill="#eaf0fd", stroke=NEG, min_w=110)
    p.append(outb)
    p.append(arrow(lx+70, 152, lx, 210-22, color=MUTED))
    # підсумок: потужність зберігається
    p.append(fitbox(lx-150, 260, 300, 56,
                    "Vвх·Iвх = (Vвх/2)·2Iвх\nуся потужність → у комірку, втрат майже нема",
                    size=12, fill="#eef7f0", stroke=FIELD))

    # ── Права панель: лінійний стабілізатор ──
    rx = 3*W/4
    p.append(text(rx, 62, "Лінійний стабілізатор", size=14, bold=True, color=POS))
    inb2, inw2, _ = textbox(rx-110, 130, "Вхід\n8 В · I", size=12, fill=FILL, stroke=LINE, min_w=96)
    p.append(inb2)
    # елемент, що гасить різницю
    rgb, rgw, _ = textbox(rx+70, 130, "гасить\n(8−4) В\nв собі", size=11, fill="#fdecea", stroke=POS, min_w=110)
    p.append(rgb)
    p.append(arrow(rx-110+inw2/2, 130, rx+70-rgw/2, 130, color=MUTED))
    outb2, _, _ = textbox(rx, 210, "Вихід\n4 В · I", size=12, fill=FILL, stroke=LINE, min_w=110)
    p.append(outb2)
    p.append(arrow(rx+70, 152, rx, 210-22, color=MUTED))
    p.append(fitbox(rx-150, 260, 300, 56,
                    "Pвтр = (Vвх−Vвих)·I = половина потужності\nу тепло; ККД = Vвих/Vвх = 50 %",
                    size=12, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, 'divider-vs-linear.svg'), W, H, *p)


if __name__ == '__main__':
    fig_why_hard()
    fig_where_regulate()
    fig_charge_pump()
    fig_divider_vs_linear()
    print("OK figures written to", IMG)
