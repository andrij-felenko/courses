# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «28BYJ-48 — кроковий мотор (5V)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Розріз мотора: обмотки-статор + магнітний ротор + редуктор → вихідний вал ─
def fig_cutaway():
    W, H = 900, 470
    f = [text(W / 2, 30, "Що всередині 28BYJ-48: крокова частина обертає магнітний ротор, редуктор віддає силу",
              size=14, bold=True)]

    # ── ЛІВОРУЧ: крокова частина (статор + ротор) ──
    sx, sy = 205, 250
    f.append(circle(sx, sy, 108, fill="#eef2f8", stroke=INK, sw=2))
    f.append(text(sx, sy - 132, "крокова частина", size=12.5, bold=True, color=NEG, anchor="middle"))
    f.append(text(sx, sy - 116, "(4 котушки + магнітний ротор)", size=9.5, color=MUTED, anchor="middle"))

    # чотири котушки статора по колу (полюси)
    for i in range(4):
        ang = math.radians(i * 90 + 45)
        px = sx + 82 * math.cos(ang)
        py = sy + 82 * math.sin(ang)
        f.append(circle(px, py, 19, fill="#fdf0ec", stroke=POS, sw=1.8))
        f.append(text(px, py + 4, "L", size=12, bold=True, color=POS))

    # ротор — постійний магніт у центрі
    f.append(circle(sx, sy, 40, fill="#eafaf0", stroke=FIELD, sw=2))
    f.append(text(sx, sy - 6, "ротор:", size=10, bold=True, color=FIELD))
    f.append(text(sx, sy + 10, "магніт", size=10, bold=True, color=FIELD))
    f.append(circle(sx, sy, 7, fill="#f4f6f8", stroke=INK, sw=1.6))

    # стрілка вправо: вал ротора → у редуктор
    f.append(arrow(sx + 112, sy, sx + 168, sy, color=INK, sw=2.4))
    f.append(text(sx + 140, sy - 12, "вал ротора", size=10, color=INK, anchor="middle"))
    f.append(text(sx + 140, sy + 22, "швидко, кволо", size=9.5, color=MUTED, anchor="middle"))

    # ── ЦЕНТР: редуктор — блок із трьома шестернями ──
    gx, gy, gw, gh = sx + 172, sy - 52, 210, 104
    f.append(rect(gx, gy, gw, gh, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(gx + gw / 2, gy - 10, "редуктор  ~1/64", size=11.5, bold=True, color=FIELD, anchor="middle"))
    for i, r in enumerate([17, 22, 17]):
        cx = gx + 42 + i * 64
        f.append(circle(cx, gy + gh / 2, r, fill=BG, stroke=INK, sw=1.4))
        for t in range(10):
            a = math.radians(t * 36)
            f.append(line(cx + (r - 3) * math.cos(a), gy + gh / 2 + (r - 3) * math.sin(a),
                          cx + (r + 3) * math.cos(a), gy + gh / 2 + (r + 3) * math.sin(a),
                          color=INK, sw=1))
    f.append(text(gx + gw / 2, gy + gh + 18, "пластикові шестерні, 4 ступені", size=9.5, color=MUTED, anchor="middle"))

    # ── ПРАВОРУЧ: вихідний вал ──
    f.append(arrow(gx + gw + 4, gy + gh / 2, gx + gw + 54, gy + gh / 2, color=INK, sw=2.4))
    shx = gx + gw + 58
    f.append(rect(shx, gy + gh / 2 - 34, 132, 68, fill="#fdf3e6", stroke=POS, sw=1.8, rx=8))
    f.append(text(shx + 66, gy + gh / 2 - 12, "вихідний", size=11.5, bold=True, color=INK, anchor="middle"))
    f.append(text(shx + 66, gy + gh / 2 + 6, "вал", size=11.5, bold=True, color=INK, anchor="middle"))
    f.append(text(shx + 66, gy + gh / 2 + 26, "повільно, сильно", size=9.5, color=POS, anchor="middle"))

    b, _, _ = textbox(W / 2, 432,
                      "Ротор крокує дрібно, але кволо; редуктор ~вшістдесятеро сповільнює його, віддаючи на вихід куди більший момент.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "cutaway.svg"), W, H, *f)


# ── 2. Ланцюг редуктора: 4 ступені, чому ~1/64 некруглий і звідки 2038 ──────────
def fig_gears():
    W, H = 940, 470
    f = [text(W / 2, 30, "Ланцюг редуктора: чотири ступені зубчастих коліс, разом близько 1/64",
              size=15, bold=True)]

    # чотири ступені — блоки зі співвідношенням зубів
    stages = [
        ("вхід від ротора", "32 / 9", NEG),
        ("ступінь 2", "22 / 11", INK),
        ("ступінь 3", "26 / 9", INK),
        ("на вихідний вал", "22 / 10", POS),
    ]
    x0 = 70
    bw, bh = 165, 96
    gap = 42
    cy = 150
    for i, (lb, ratio, col) in enumerate(stages):
        bx = x0 + i * (bw + gap)
        f.append(rect(bx, cy - bh / 2, bw, bh, fill="#f4f6f8", stroke=col, sw=1.8, rx=10))
        f.append(text(bx + bw / 2, cy - 26, lb, size=10.5, bold=True, color=col))
        # дві шестерні (велика/мала) як дріб
        f.append(text(bx + bw / 2, cy + 6, ratio, size=20, bold=True, color=INK))
        f.append(text(bx + bw / 2, cy + 32, "зуб.: велике / мале", size=9.5, color=MUTED))
        if i < 3:
            f.append(arrow(bx + bw, cy, bx + bw + gap, cy, color=INK, sw=2.2))

    # обчислення добутку — код-блок-стиль (рамка)
    calc = ("(32·22·26·22) / (9·11·9·10)  =  402 688 / 8 910  ≈  63.684")
    b1, _, _ = textbox(W / 2, 262, calc, size=13, fill="#eef6ef", stroke=FIELD, color=INK, bold=True)
    f.append(b1)
    f.append(text(W / 2, 300, "точний передавальний коефіцієнт — НЕ рівно 64", size=11, bold=True, color=POS, anchor="middle"))

    # праворуч-унизу — наслідок для кроків
    b2, _, _ = textbox(300, 356,
                       "внутр. 32 повні кроки/оберт ротора\n× 63.684  ≈  2038 кроків на оберт ВАЛА\n(а не круглі 2048)",
                       size=11, fill=FILL, stroke=LINE, color=INK)
    f.append(b2)
    b3, _, _ = textbox(700, 356,
                       "у половинному режимі —\nудвічі більше:  ≈ 4076 кроків/оберт",
                       size=11, fill=FILL, stroke=LINE, color=INK)
    f.append(b3)

    b, _, _ = textbox(W / 2, 448,
                      "Некругле число — наслідок реальних зубів; тому «рівно 90°» ділять на 2038, і за багато обертів позиція трохи дрейфує.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "gears.svg"), W, H, *f)


# ── 3. П'ять дротів: дві котушки зі спільним відводом, червоний — центр ─────────
def fig_wires():
    W, H = 940, 490
    f = [text(W / 2, 30, "П'ять дротів мотора: дві обмотки зі спільним центром на +5 В",
              size=15, bold=True)]

    # спільна шина +5В зверху (червоний)
    vy = 96
    f.append(line(150, vy, W - 150, vy, color=POS, sw=3))
    f.append(plus(150, vy, 8))
    f.append(text(W / 2, vy - 14, "червоний дріт — спільний центр обох обмоток, на +5 В",
                  size=11.5, bold=True, color=POS, anchor="middle"))

    end_y = 300        # рівень кінців-виводів (кольорові кружечки)
    lbl_y = end_y + 24  # рівень підписів під ними

    def coil(cx, c_left, name_left, c_right, name_right, coil_label):
        branch = vy + 44                     # точка спільного відводу (центр обмотки)
        f.append(line(cx, vy, cx, branch, color=POS, sw=2.4))
        f.append(circle(cx, branch, 4, fill=POS, stroke=POS))
        # підпис обмотки — ЗБОКУ від вертикальної лінії (не на ній), anchor=start
        f.append(text(cx + 88, branch + 4, coil_label, size=10.5, bold=True, color=MUTED, anchor="middle"))
        for side, col, nm in [(-1, c_left, name_left), (1, c_right, name_right)]:
            bx = cx + side * 66
            f.append(line(cx, branch, bx, branch + 22, color=INK, sw=1.8))
            # дужки-виток обмотки
            for k in range(3):
                yy = branch + 30 + k * 17
                f.append('<path d="M%.0f %.0f q 13 8.5 0 17" fill="none" stroke="%s" stroke-width="2"/>'
                         % (bx, yy, INK))
            f.append(line(bx, branch + 30 + 3 * 17, bx, end_y, color=col, sw=3))
            f.append(circle(bx, end_y, 6.5, fill=col, stroke=INK, sw=1.2))
            f.append(text(bx, lbl_y, nm, size=10.5, bold=True, color=INK, anchor="middle"))

    coil(255, "#d35400", "помаранчевий", "#c9a227", "жовтий", "обмотка 1")
    coil(645, "#e84393", "рожевий", "#2457d6", "синій", "обмотка 2")

    # пояснення — чому 5, а не 4 (двома рядками, щоб рамка не вилазила)
    b1, _, _ = textbox(W / 2, 388,
                       "4 кінці фаз + 1 спільний центр = 5 дротів (уніполярна схема):\nдрайверу досить по черзі притягувати кінці до землі, центр — постійно на +5 В.",
                       size=11, fill="#eef6ef", stroke=FIELD, color=INK)
    f.append(b1)

    b, _, _ = textbox(W / 2, 456,
                      "Спільний відвід робить мотор УНІПОЛЯРНИМ: струм у кожній половині тече лише в один бік,\nтож ключі потрібні вчетверо простіші, ніж біполярному мотору.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "wires.svg"), W, H, *f)


# ── 4. Пастка порядку фаз: чому 1-3-2-4 крутить, а 1-2-3-4 лише тремтить ────────
def fig_phaseorder():
    W, H = 960, 560
    f = [text(W / 2, 30, "Головна пастка: у якому порядку перелічити піни в конструкторі",
              size=15, bold=True)]

    # ── легенда обмоток (яка фаза до якої котушки належить) ──
    ly = 66
    f.append(text(W / 2, ly, "Магнітно фази згруповані так (не за номером виводу, а за котушкою):",
                  size=11.5, color=MUTED, anchor="middle"))
    # обмотка A: помаранч + жовтий ; обмотка B: рожевий + синій
    ay = 92
    f.append(rect(230, ay, 210, 34, fill="#fdf3e6", stroke=POS, sw=1.6, rx=8))
    f.append(text(335, ay + 22, "обмотка A: помаранч. + жовтий", size=10.5, bold=True, color=INK, anchor="middle"))
    f.append(rect(520, ay, 210, 34, fill="#eef2f8", stroke=NEG, sw=1.6, rx=8))
    f.append(text(625, ay + 22, "обмотка B: рожевий + синій", size=10.5, bold=True, color=INK, anchor="middle"))

    # порядок кольорів у роз'ємі ULN2003 (IN1..IN4)
    conn_y = 158
    conn = [("IN1", "синій", "#2457d6", "B"),
            ("IN2", "рожевий", "#e84393", "B"),
            ("IN3", "жовтий", "#c9a227", "A"),
            ("IN4", "помаранч.", "#d35400", "A")]
    cx0 = 250
    step = 118
    f.append(text(W / 2, conn_y - 22, "піни драйвера в природному порядку роз'єму (IN1→IN4):",
                  size=11, color=MUTED, anchor="middle"))
    for i, (pin, nm, col, grp) in enumerate(conn):
        x = cx0 + i * step
        f.append(circle(x, conn_y, 20, fill=col, stroke=INK, sw=1.4))
        f.append(text(x, conn_y + 5, pin, size=10.5, bold=True, color=BG))
        f.append(text(x, conn_y + 40, nm, size=10, color=INK, anchor="middle"))
        f.append(text(x, conn_y + 56, "котушка " + grp, size=9.5, bold=True,
                      color=(POS if grp == "A" else NEG), anchor="middle"))

    # ── ЛІВОРУЧ-унизу: НЕПРАВИЛЬНО 1-2-3-4 ──
    def sequence_panel(px, title, order, groups, ok):
        pw, ph = 400, 168
        col = FIELD if ok else POS
        f.append(rect(px, 300, pw, ph, fill=("#eef6ef" if ok else "#fdecea"),
                      stroke=col, sw=2, rx=12))
        f.append(text(px + pw / 2, 326, title, size=12.5, bold=True, color=col, anchor="middle"))
        # рядок стрілочок порядку
        oy = 366
        box = 62
        ogap = 20
        ox0 = px + (pw - (4 * box + 3 * ogap)) / 2
        for j, (pin, grp) in enumerate(zip(order, groups)):
            bx = ox0 + j * (box + ogap)
            gcol = POS if grp == "A" else NEG
            f.append(rect(bx, oy, box, 46, fill=BG, stroke=gcol, sw=1.8, rx=8))
            f.append(text(bx + box / 2, oy + 20, pin, size=11, bold=True, color=INK))
            f.append(text(bx + box / 2, oy + 38, grp, size=11, bold=True, color=gcol))
            if j < 3:
                f.append(arrow(bx + box, oy + 23, bx + box + ogap, oy + 23, color=INK, sw=2))
        # рядок котушок як послідовність
        seq = " → ".join(groups)
        f.append(text(px + pw / 2, oy + 78, "котушки: " + seq, size=11, bold=True, color=INK, anchor="middle"))
        verdict = ("A і B чергуються — поле обертається, вал крокує"
                   if ok else "двічі та сама котушка поспіль — поле сіпається, вал тремтить")
        f.append(text(px + pw / 2, oy + 100, verdict, size=10, color=col, anchor="middle"))

    # 1-2-3-4 = IN1 IN2 IN3 IN4 = B B A A  → погано
    sequence_panel(60, "1-2-3-4  (як пишеться інтуїтивно)",
                   ["IN1", "IN2", "IN3", "IN4"], ["B", "B", "A", "A"], ok=False)
    # 1-3-2-4 = IN1 IN3 IN2 IN4 = B A B A  → добре
    sequence_panel(500, "1-3-2-4  (правильно!)",
                   ["IN1", "IN3", "IN2", "IN4"], ["B", "A", "B", "A"], ok=True)

    b, _, _ = textbox(W / 2, 522,
                      "У коді піни перелічують 8, 10, 9, 11 (IN1, IN3, IN2, IN4): так сусідні такти б'ють у РІЗНІ котушки й женуть поле по колу.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "phaseorder.svg"), W, H, *f)


# ── 5. Схема з'єднань: Arduino ↔ ULN2003 ↔ мотор, з окремим живленням ──────────
def fig_wiring():
    W, H = 940, 520
    f = [text(W / 2, 30, "Три блоки схеми: контролер дає сигнали, драйвер — струм, мотор — рух",
              size=15, bold=True)]

    # ── Arduino ──
    ax, ay, aw, ah = 60, 120, 190, 240
    f.append(rect(ax, ay, aw, ah, fill="#eef2f8", stroke=NEG, sw=2, rx=12))
    f.append(text(ax + aw / 2, ay + 26, "Arduino Uno", size=13, bold=True, color=NEG, anchor="middle"))
    pins = ["D8", "D10", "D9", "D11", "GND"]
    for i, p in enumerate(pins):
        yy = ay + 62 + i * 34
        f.append(text(ax + 40, yy, p, size=11.5, bold=True, color=INK, anchor="middle"))

    # ── ULN2003 ──
    ux, uy, uw, uh = 380, 120, 200, 300
    f.append(rect(ux, uy, uw, uh, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    f.append(text(ux + uw / 2, uy + 26, "плата ULN2003", size=13, bold=True, color=FIELD, anchor="middle"))
    ins = ["IN1", "IN2", "IN3", "IN4"]
    for i, p in enumerate(ins):
        yy = uy + 62 + i * 34
        f.append(text(ux + 34, yy, p, size=11.5, bold=True, color=INK, anchor="middle"))
        f.append(text(ux + uw - 40, yy, "OUT", size=10, color=MUTED, anchor="middle"))
    # живлення драйвера
    f.append(text(ux + uw / 2, uy + uh - 66, "+5 В (окреме)", size=11, bold=True, color=POS, anchor="middle"))
    f.append(text(ux + uw / 2, uy + uh - 44, "GND", size=11, bold=True, color=INK, anchor="middle"))
    f.append(text(ux + uw / 2, uy + uh - 20, "біла колодка → мотор", size=9.5, color=MUTED, anchor="middle"))

    # сигнальні лінії Arduino→ULN (перехрещені, бо 8,10,9,11)
    src = [ay + 62, ay + 62 + 34, ay + 62 + 2 * 34, ay + 62 + 3 * 34]  # D8 D10 D9 D11
    dst = [uy + 62, uy + 62 + 34, uy + 62 + 2 * 34, uy + 62 + 3 * 34]  # IN1 IN2 IN3 IN4
    # D8→IN1, D10→IN3, D9→IN2, D11→IN4  (тобто фізична відповідність)
    pairmap = [(0, 0), (1, 2), (2, 1), (3, 3)]
    for s, d in pairmap:
        f.append(line(ax + aw, src[s], ux, dst[d], color=NEG, sw=1.6))
    f.append(text((ax + aw + ux) / 2, ay + 44, "4 сигнали", size=9.5, color=MUTED, anchor="middle"))

    # спільна земля Arduino GND ↔ ULN GND (ЖИРНО, ключове)
    gnd_a_y = ay + 62 + 4 * 34
    f.append(line(ax + aw, gnd_a_y, ux, uy + uh - 44, color=INK, sw=2.6, dash="1 0"))
    f.append(text((ax + aw + ux) / 2, gnd_a_y + 16, "СПІЛЬНА земля", size=10, bold=True, color=POS, anchor="middle"))

    # ── Мотор ──
    mx, my = 760, 240
    f.append(circle(mx, my, 66, fill="#f4f6f8", stroke=INK, sw=2))
    f.append(text(mx, my - 6, "28BYJ-48", size=12, bold=True, color=INK))
    f.append(text(mx, my + 12, "5 дротів", size=10, color=MUTED))
    f.append(arrow(ux + uw, uy + uh / 2 - 10, mx - 70, my, color=INK, sw=2))
    f.append(text((ux + uw + mx) / 2, my - 34, "джгут", size=9.5, color=MUTED, anchor="middle"))

    # окреме джерело 5В
    px2, py2 = 380, 470
    f.append(rect(px2, py2 - 24, 200, 40, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    f.append(text(px2 + 100, py2, "БЖ 5 В  ·  ≥ 1 А (окремо, не з USB)", size=10.5, bold=True, color=POS, anchor="middle"))
    f.append(arrow(px2 + 100, py2 - 24, ux + uw / 2, uy + uh - 4, color=POS, sw=1.8))

    b, _, _ = textbox(W / 2, 502,
                      "Сигнали з D8,D10,D9,D11 → IN1..IN4; мотор живить окреме 5 В; землі контролера й драйвера ОБОВ'ЯЗКОВО з'єднані.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cutaway()
    fig_gears()
    fig_wires()
    fig_phaseorder()
    fig_wiring()
    print("OK: 5 figures ->", IMG)
