# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── spof: де єдині точки відмови проти дубльованого ────────────────────────────
# Ідея: дві колонки. Ліворуч — вузли, чия одна поломка валить усе (SPOF);
# праворуч — те, що зазвичай дублюють. Око одразу бачить, де апарат крихкий.

def fig_spof():
    W, H = 760, 360
    p = []
    # дві рамки-колонки
    lx, rx, top, cw, ch = 40, 400, 70, 320, 250
    p.append(rect(lx, top, cw, ch, fill="#fdecea", stroke=POS, sw=1.8, rx=12))
    p.append(rect(rx, top, cw, ch, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=12))
    p.append(text(lx + cw / 2, top + 26, "Єдині точки відмови", size=14, color=POS, bold=True))
    p.append(text(lx + cw / 2, top + 44, "одна поломка — падає все", size=10, color=MUTED))
    p.append(text(rx + cw / 2, top + 26, "Зазвичай дублюють", size=14, color=FIELD, bold=True))
    p.append(text(rx + cw / 2, top + 44, "одна відмова — апарат живий", size=10, color=MUTED))

    spof = ["одна батарея", "один контролер", "регулятор логіки", "головний джгут / роз'єм"]
    dup = ["IMU ×2–3 (голосування)", "компас, GNSS", "мотори 6–8 замість 4", "два живлення / контролери"]
    rh, gap = 38, 12
    y = top + 64
    for i in range(4):
        ry = y + i * (rh + gap)
        p.append(rect(lx + 18, ry, cw - 36, rh, fill=BG, stroke=POS, sw=1.1, rx=8))
        p.append(text(lx + 30, ry + rh / 2 + 4, "✗  " + spof[i], size=11, color=INK, anchor="start"))
        p.append(rect(rx + 18, ry, cw - 36, rh, fill=BG, stroke=FIELD, sw=1.1, rx=8))
        p.append(text(rx + 30, ry + rh / 2 + 4, "✓  " + dup[i], size=11, color=INK, anchor="start"))

    p.append(text(W / 2, H - 14,
                  "дублюють не все підряд, а вузькі місця — під ставки місії",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "spof.svg"), W, H, *p,
           title="Перше питання: де поодинока відмова валить усе")


# ── motor-loss: квадро не переживає втрати мотора, гекса/окто — переживає ───────
# Ідея: дві рами зверху; на кожній один мотор «вибитий» хрестиком. Квадро лишає
# 3 мотори на 4 величини (керованість зникає); гекса має запас.

def fig_motor_loss():
    W, H = 760, 380
    p = []
    lx, rx, top, cw, ch = 40, 400, 70, 320, 230
    p.append(rect(lx, top, cw, ch, fill="#fdf3f2", stroke=POS, sw=1.4, rx=12))
    p.append(rect(rx, top, cw, ch, fill="#f3fbf6", stroke=FIELD, sw=1.4, rx=12))
    p.append(text(lx + cw / 2, top + 24, "Квадрокоптер (4 мотори)", size=13, color=POS, bold=True))
    p.append(text(rx + cw / 2, top + 24, "Гекса / окто (6–8 моторів)", size=13, color=FIELD, bold=True))

    def frame(cx, cy, n, dead_idx, r=18, arm=72):
        out = [circle(cx, cy, 14, fill="#f4f4f5", stroke=INK, sw=1.6)]
        for i in range(n):
            ang = -math.pi / 2 + 2 * math.pi * i / n
            mx, my = cx + arm * math.cos(ang), cy + arm * math.sin(ang)
            if i == dead_idx:
                out.append(line(cx, cy, mx, my, color=POS, sw=2.4, dash="4 3"))
                out.append(circle(mx, my, r, fill="#fde0e0", stroke=POS, sw=1.8))
                out.append(line(mx - 9, my - 9, mx + 9, my + 9, color=POS, sw=2.2))
                out.append(line(mx - 9, my + 9, mx + 9, my - 9, color=POS, sw=2.2))
            else:
                out.append(line(cx, cy, mx, my, color=INK, sw=2.4))
                out.append(circle(mx, my, r, fill="#eafaf0", stroke=FIELD, sw=1.8))
        return out

    p += frame(lx + cw / 2, top + 130, 4, 1)
    p += frame(rx + cw / 2, top + 130, 6, 1)
    p.append(text(lx + cw / 2, top + 206, "4 мотори = 4 керовані величини — запасу немає",
                  size=10.5, color=INK))
    p.append(text(rx + cw / 2, top + 206, "зайві мотори дають запас тяги й керування",
                  size=10.5, color=INK))

    p.append(text(lx + cw / 2, H - 42, "втратив один → падіння", size=12, color=POS, bold=True))
    p.append(text(rx + cw / 2, H - 42, "втратив один → летить, сідає контрольовано",
                  size=11, color=FIELD, bold=True))
    p.append(text(W / 2, H - 14,
                  "за достатнього запасу тяги, геометрії й налаштованої реакції на втрату мотора",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "motor-loss.svg"), W, H, *p,
           title="Те саме резервування, лише для виконавців")


# ── voting: мажоритарне голосування 2 з 3 давачів ─────────────────────────────
# Ідея: три давачі дають значення; один «збрехав». Медіана/голос викидає
# відхилене й бере згоду двох. Це ядро worked-прикладу в тексті.

def fig_voting():
    W, H = 740, 330
    p = []
    # три давачі ліворуч
    sx, sw_box, sh = 60, 150, 56
    ys = [70, 150, 230]
    vals = [("давач A", "10.1", FIELD, False),
            ("давач B", "10.2", FIELD, False),
            ("давач C", "47.3", POS, True)]   # C збрехав
    cx_v = sx + sw_box + 120          # вузол-голосувач
    cy_v = 150
    for (lab, val, col, bad), y in zip(vals, ys):
        fill = "#fdecea" if bad else "#eafaf0"
        p.append(rect(sx, y, sw_box, sh, fill=fill, stroke=col, sw=1.6, rx=8))
        p.append(text(sx + 14, y + 22, lab, size=11, color=INK, anchor="start"))
        p.append(text(sx + sw_box - 14, y + 40, val, size=15, color=col, anchor="end", bold=True))
        # стрілка до голосувача
        p.append(arrow(sx + sw_box + 4, y + sh / 2, cx_v - 46, cy_v + (y - cy_v) * 0.18,
                       color=(POS if bad else MUTED), sw=1.7))
    p.append(text(vals[2][0] and sx + sw_box / 2, ys[2] + sh + 16,
                  "відхилений", size=10, color=POS))

    # вузол голосування
    b, bw, bh = textbox(cx_v, cy_v, "голос / медіана\n2 з 3", size=12, bold=True,
                        fill="#eef4ff", stroke=NEG, sw=2, pad=14)
    p.append(b)

    # вихід праворуч
    out_x = cx_v + bw / 2 + 70
    p.append(arrow(cx_v + bw / 2 + 4, cy_v, out_x - 46, cy_v, color=INK, sw=2.0))
    ob, obw, obh = textbox(out_x + 8, cy_v, "вихід 10.15", size=13, bold=True,
                           fill="#eafaf0", stroke=FIELD, sw=2, pad=12)
    p.append(ob)

    p.append(text(W / 2, H - 16,
                  "дві згодні копії важать більше за одну відхилену — брехуна викинуто, не повіривши йому",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "voting.svg"), W, H, *p,
           title="Мажоритарне голосування: двоє правлять третього")


# ── pipeline: виявити → вирішити → деградувати ────────────────────────────────
# Ідея: три блоки конвеєра; перший (виявити) найширший — бо без нього решта марна.

def fig_pipeline():
    W, H = 780, 330
    p = []
    top, ch = 70, 220
    cols = [
        ("1. Виявити", NEG, "#eef4ff",
         ["звірка давачів", "(не згодні?)", "телеметрія ESC", "watchdog (завис?)", "струм і температура"]),
        ("2. Вирішити", "#b8860b", "#fdf6e3",
         ["який failsafe доречний:", "• на резерв", "• повернутись додому", "• сісти / планувати", "• роззброїти на землі"]),
        ("3. Деградувати", FIELD, "#eafaf0",
         ["виконати реакцію:", "втратити трохи,", "а не все одразу;", "реакція зашита", "заздалегідь"]),
    ]
    cw, gap = 220, 40
    x = 30
    centers = []
    for title_, col, fill, lines in cols:
        p.append(rect(x, top, cw, ch, fill=fill, stroke=col, sw=1.8, rx=12))
        p.append(text(x + cw / 2, top + 28, title_, size=13.5, color=col, bold=True))
        for i, ln in enumerate(lines):
            p.append(text(x + 18, top + 58 + i * 26, ln, size=11, color=INK, anchor="start"))
        centers.append((x, x + cw))
        x += cw + gap
    # стрілки між блоками
    ay = top + ch / 2
    for i in range(2):
        p.append(arrow(centers[i][1] + 4, ay, centers[i + 1][0] - 4, ay, color=INK, sw=2.2))

    p.append(text(W / 2, H - 14,
                  "не можна зреагувати на відмову, якої не помітив — тому виявлення найважливіше",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "pipeline.svg"), W, H, *p,
           title="Поведінка за відмови — це конвеєр")


# ── ladder: драбина деградації проти обриву ───────────────────────────────────
# Ідея: ліворуч сходинки вниз (кожна відмова — крок), праворуч прямовисний обрив
# від справності одразу до краху.

def fig_ladder():
    W, H = 760, 380
    p = []
    p.append(text(W * 0.27, 60, "Добра система: драбина", size=13, color=FIELD, bold=True))
    p.append(text(W * 0.76, 60, "Крихка система: обрив", size=13, color=POS, bold=True))

    steps = ["повна справність", "втратив давач → резерв",
             "зник GNSS → безпечний режим", "втратив мотор → сісти", "безпечна зупинка"]
    bx, by, bw, bh = 40, 86, 230, 26
    dx, dy = 34, 50
    prev = None
    for i, lab in enumerate(steps):
        x = bx + i * dx
        y = by + i * dy
        p.append(rect(x, y, bw, bh, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
        p.append(text(x + 10, y + bh / 2 + 4, lab, size=9.5, color=INK, anchor="start"))
        if prev:
            p.append(line(prev[0] + bw / 2, prev[1] + bh, x, y, color=FIELD, sw=2.0))
        prev = (x, y)
    p.append(text(bx + 110, by + 4 * dy + bh + 26, "кожна відмова — лише крок униз, апарат живий",
                  size=10, color=FIELD))

    # обрив праворуч
    cx = W * 0.76
    p.append(rect(cx - 100, 86, 200, 30, fill="#fdecea", stroke=POS, sw=1.6, rx=7))
    p.append(text(cx, 106, "повна справність", size=11, color=INK))
    p.append(arrow(cx, 120, cx, 300, color=POS, sw=3.0))
    p.append(text(cx + 16, 215, "одна відмова", size=11, color=POS, anchor="start", bold=True))
    p.append(rect(cx - 80, 304, 160, 40, fill=POS, stroke=POS, sw=1.6, rx=8))
    p.append(text(cx, 329, "КРАХ", size=15, color="#ffffff", bold=True))

    render(os.path.join(OUT, "ladder.svg"), W, H, *p,
           title="Мета — драбина деградації, а не обрив")


if __name__ == "__main__":
    fig_spof()
    fig_motor_loss()
    fig_voting()
    fig_pipeline()
    fig_ladder()
    print("OK: figures written to", OUT)
