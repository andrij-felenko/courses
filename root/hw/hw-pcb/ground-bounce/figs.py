# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: шлях струму крізь паразитну індуктивність ─────────────────────
def fig_path():
    W, H = 720, 380
    f = []
    f.append(text(W/2, 26, "Чому «земля» на кристалі стрибає", size=17, bold=True))

    # кристал (die)
    die_x, die_y, die_w, die_h = 60, 70, 250, 220
    f.append(rect(die_x, die_y, die_w, die_h, fill="#eef4ff", stroke=NEG, sw=2))
    f.append(text(die_x + die_w/2, die_y + 22, "Кристал (die)", size=14, bold=True, color=NEG))

    # вихідний драйвер, що тягне лінію в 0 — стік струму
    box, bw, bh = textbox(die_x + die_w/2, 160, "вихід\nтягне в 0", size=12, fill=FILL)
    f.append(box)
    # внутрішня «земля» кристала
    gnd_die_y = 258
    f.append(line(die_x + 30, gnd_die_y, die_x + die_w - 30, gnd_die_y, color=INK, sw=3))
    f.append(text(die_x + die_w/2, gnd_die_y + 20, "внутрішня GND кристала", size=11, color=MUTED))
    # струм із драйвера в цю землю
    f.append(arrow(die_x + die_w/2, 176, die_x + die_w/2, gnd_die_y - 4, color=POS, sw=2.4))
    f.append(text(die_x + die_w/2 + 46, 216, "i(t)", size=13, color=POS, italic=True, bold=True))

    # bond wire / вивід = котушка (індуктивність)
    coil_x0 = die_x + die_w/2
    pin_x = 470
    y = gnd_die_y
    # намалюємо «пружину» між кристалом і пластиною плати
    seg = ""
    n = 6
    step = (pin_x - coil_x0) / n
    px, py = coil_x0, y
    for i in range(n):
        nx = coil_x0 + step * (i + 1)
        my = y - 16 if i % 2 == 0 else y + 16
        seg += line(px, py, nx, my, color="#8a5a00", sw=2.6)
        px, py = nx, my
    seg += line(px, py, pin_x, y, color="#8a5a00", sw=2.6)
    f.append(seg)
    lbox, lw, lh = textbox(coil_x0 + (pin_x - coil_x0)/2, y - 52,
                           "вивід + bond wire\nL ≈ кілька нГн", size=12,
                           fill="#fff6e6", stroke="#8a5a00")
    f.append(lbox)

    # пластина землі плати
    gp_x, gp_w = pin_x - 6, 190
    f.append(rect(gp_x, y - 10, gp_w, 20, fill="#e8f7ee", stroke=FIELD, sw=2))
    f.append(text(gp_x + gp_w/2, y + 3, "GND-пластина плати", size=12, bold=True, color=FIELD))
    f.append(text(gp_x + gp_w/2, y + 34, "стабільний 0 В", size=11, color=MUTED))

    # напис із формулою
    fb = fitbox(60, 316, 600, 46,
                "різкий стрибок струму  →  на L падає напруга  V = L · (di/dt)  →  "
                "внутрішня земля кристала підскакує над 0 В плати",
                size=13, fill="#fdecea", stroke=POS)
    f.append(fb)

    render(os.path.join(IMG, 'bounce-path.svg'), W, H, *f)


# ── Фігура 2: тихий вихід глітчить у заборонену зону ─────────────────────────
def fig_wave():
    W, H = 720, 400
    f = []
    f.append(text(W/2, 26, "Тихий вихід підстрибує, бо земля під ним піднялася", size=16, bold=True))

    left = 70
    right = 680
    def X(t):  # t у 0..1
        return left + (right - left) * t

    # 1) багато виходів перемикаються одночасно (0→1)
    ax_a = 78
    f.append(text(left - 8, ax_a - 26, "N виходів  0 → 1", size=12, anchor="end", bold=True))
    hi_a, lo_a = ax_a, ax_a + 46
    # ступінь угору в момент t=0.35
    tt = 0.35
    f.append(line(X(0), lo_a, X(tt), lo_a, color=NEG, sw=3))
    f.append(line(X(tt), lo_a, X(tt+0.02), hi_a, color=NEG, sw=3))
    f.append(line(X(tt+0.02), hi_a, X(1), hi_a, color=NEG, sw=3))
    f.append(text(X(tt) + 8, hi_a - 6, "усі разом", size=11, color=NEG))

    # 2) внутрішня земля кристала — підскок і дзвін
    ax_g = 190
    f.append(text(left - 8, ax_g - 28, "GND кристала", size=12, anchor="end", bold=True))
    base_g = ax_g + 30
    f.append(line(X(0), base_g, X(tt), base_g, color=INK, sw=2.4))
    # затухаючий дзвін
    import math
    pts = []
    for k in range(0, 121):
        t = tt + (0.5) * (k / 120.0)
        env = math.exp(-6.0 * (t - tt))
        v = -46 * env * math.sin(2 * math.pi * 3.2 * (t - tt))
        pts.append((X(t), base_g + v))
    dpath = "M %.1f %.1f " % (X(tt), base_g) + " ".join("L %.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (dpath, POS))
    f.append(line(X(0), base_g, right, base_g, color=MUTED, sw=1, dash="4 4"))
    f.append(text(right - 4, base_g + 16, "0 В (ідеал)", size=10, anchor="end", color=MUTED))
    f.append(text(X(tt+0.05), base_g - 40, "підскок", size=11, color=POS, bold=True))

    # 3) тихий вихід, що мав би лежати в 0 — повторює підскок землі
    ax_q = 292
    f.append(text(left - 8, ax_q - 12, "тихий вихід", size=12, anchor="end", bold=True))
    f.append(text(left - 8, ax_q + 4, "(мав лежати в 0)", size=10, anchor="end", color=MUTED))
    base_q = ax_q + 44
    # заборонена зона (смуга)
    fz_y = base_q - 58
    fz_h = 30
    f.append(rect(left, fz_y, right - left, fz_h, fill="#fff3cd", stroke="#e0a800", sw=1, rx=3))
    f.append(text(right - 6, fz_y + 12, "заборонена зона / поріг «1»", size=10, anchor="end", color="#8a6d00"))
    # сам сигнал: лежить у 0, потім горб, що залазить у зону
    q = []
    for k in range(0, 121):
        t = tt + 0.5 * (k / 120.0)
        env = math.exp(-6.0 * (t - tt))
        v = -52 * env * math.sin(2 * math.pi * 3.2 * (t - tt))
        v = max(v, 0)  # угору вихід тягне вгору лише додатний підскок землі
        q.append((X(t), base_q + v))
    qpath = ("M %.1f %.1f L %.1f %.1f " % (X(0), base_q, X(tt), base_q)
             + " ".join("L %.1f %.1f" % p for p in q))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (qpath, POS))
    f.append(line(X(0), base_q, right, base_q, color=MUTED, sw=1, dash="4 4"))
    # стрілка-примітка на перший горб
    peak_t = tt + 1.0/(3.2)*0.25
    f.append(text(X(peak_t) + 70, base_q - 66, "фальшива «1»!", size=12, color=POS, bold=True))
    f.append(arrow(X(peak_t) + 60, base_q - 58, X(peak_t) + 4, base_q - fz_h + 4, color=POS, sw=2))

    # підпис часу
    f.append(line(X(tt), 60, X(tt), 350, color="#cccccc", sw=1, dash="3 5"))
    f.append(text(X(tt), 366, "момент одночасного перемикання", size=11, color=MUTED))

    render(os.path.join(IMG, 'bounce-wave.svg'), W, H, *f)


# ── Фігура 3: два важелі проти стрибка ───────────────────────────────────────
def fig_cures():
    W, H = 720, 300
    f = []
    f.append(text(W/2, 26, "V = L · (di/dt): бити можна по обох множниках", size=16, bold=True))

    # ліва колона — зменшити L
    lx = 40
    f.append(rect(lx, 56, 300, 200, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(lx + 150, 82, "менша L", size=15, bold=True, color=NEG))
    for i, s in enumerate([
        "кілька GND/VCC-пінів поряд",
        "живлення близько до кристала",
        "коротка широка земляна доріжка",
        "суцільна GND-пластина, не «павук»",
    ]):
        f.append(text(lx + 18, 116 + i*32, "•  " + s, size=13, anchor="start"))

    # права колона — зменшити di/dt
    rx = 380
    f.append(rect(rx, 56, 300, 200, fill="#e8f7ee", stroke=FIELD, sw=2))
    f.append(text(rx + 150, 82, "менший di/dt", size=15, bold=True, color=FIELD))
    for i, s in enumerate([
        "повільніший фронт (slew-rate)",
        "не перемикати все одночасно",
        "розвести фронти в часі",
        "конденсатор поряд живить пік",
    ]):
        f.append(text(rx + 18, 116 + i*32, "•  " + s, size=13, anchor="start"))

    f.append(text(W/2, 284, "будь-який із важелів зменшує підскок; разом — найкраще",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'bounce-cures.svg'), W, H, *f)


# ── Фігура 4 (вставка math): розклад формули + зростання з N ─────────────────
def fig_budget():
    import math
    W, H = 720, 420
    f = []
    f.append(text(W/2, 26, "Величина стрибка: чотири множники й зростання з N", size=16, bold=True))

    # ── ліва частина: розклад V ≈ N·L·C·V_swing / t² ────────────────────────
    lx = 34
    f.append(rect(lx, 52, 322, 232, fill="#f7f9ff", stroke=NEG, sw=2))
    f.append(fitbox(lx + 12, 66, 298, 34, "V ≈ N · L · C · V_swing / t²",
                    size=17, bold=True, fill="#eef4ff", stroke=NEG, color=NEG))
    rows = [
        ("N — виходів разом", "лінійно", NEG),
        ("L — індуктивність виводу", "лінійно", NEG),
        ("C — ємність лінії", "лінійно", NEG),
        ("t — час фронту", "у КВАДРАТІ", POS),
    ]
    for i, (name, law, col) in enumerate(rows):
        yy = 122 + i * 38
        f.append(text(lx + 16, yy, "•  " + name, size=13, anchor="start"))
        f.append(text(lx + 306, yy, law, size=12, anchor="end", color=col, bold=True))
    f.append(text(lx + 161, 276, "t б'є по стрибку сильніше за все", size=11, color=MUTED))

    # ── права частина: стовпчики росту з N ──────────────────────────────────
    rx = 388
    rw = 300
    f.append(rect(rx, 52, rw, 232, fill="#fbfefc", stroke=FIELD, sw=2))
    f.append(text(rx + rw/2, 72, "V росте прямо з числом виходів", size=13, bold=True, color=FIELD))

    base_y = 258                 # низ стовпчиків
    plot_x = rx + 30
    plot_w = rw - 56
    ns = [1, 2, 4, 8]
    v1 = 0.25                    # В на один вихід
    top_v = 2.0                  # верх шкали ≈ 8·v1
    max_h = 150
    bw = 34
    gap = (plot_w - len(ns) * bw) / (len(ns) + 1)

    # поріг «1» ≈ приблизно на рівні 0.8 В
    thr_v = 0.8
    thr_y = base_y - max_h * (thr_v / top_v)
    f.append(line(plot_x, thr_y, plot_x + plot_w, thr_y, color="#e0a800", sw=1.6, dash="5 4"))
    f.append(text(plot_x + plot_w, thr_y - 5, "поріг «1»", size=10, anchor="end", color="#8a6d00"))

    for i, n in enumerate(ns):
        v = n * v1
        bh = max_h * (v / top_v)
        bx = plot_x + gap + i * (bw + gap)
        col = POS if v > thr_v else NEG
        fillc = "#fdecea" if v > thr_v else "#eaf0fd"
        f.append(rect(bx, base_y - bh, bw, bh, fill=fillc, stroke=col, sw=1.8, rx=3))
        f.append(text(bx + bw/2, base_y - bh - 7, "%.2f В" % v, size=11, bold=True, color=col))
        f.append(text(bx + bw/2, base_y + 16, "N=%d" % n, size=11))
    f.append(line(plot_x, base_y, plot_x + plot_w, base_y, color=INK, sw=1.5))
    f.append(text(rx + rw/2, 278, "8 ліній разом → удвічі вище за поріг", size=11, color=MUTED))

    # ── нижній рядок: сам ланцюг виведення ──────────────────────────────────
    f.append(fitbox(34, 304, 654, 40,
                    "заряд лінії  Q = C·V   →   різкий струм  i = C·(dV/dt)   →   "
                    "на виводі  V = L·(di/dt)   →   ×N синхронних ліній",
                    size=13, fill="#f4f6f8", stroke=MUTED))
    f.append(text(W/2, 372, "стрибок = добуток чотирьох множників; ширша синхронна шина — вищий підскок",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'bounce-budget.svg'), W, H, *f)


# ── Фігура 5 (вставка hist): чому кутова ніжка — найгірша для живлення ───────
def fig_corner_pins():
    W, H = 720, 360
    f = []
    f.append(text(W/2, 26, "Індуктивність виводу залежить від того, де ніжка", size=16, bold=True))

    # корпус DIP згори, кристал у центрі
    pkg_x, pkg_y, pkg_w, pkg_h = 140, 74, 440, 150
    f.append(rect(pkg_x, pkg_y, pkg_w, pkg_h, fill="#f0f0f0", stroke=INK, sw=2))
    die_w, die_h = 120, 70
    die_x = pkg_x + (pkg_w - die_w) / 2
    die_y = pkg_y + (pkg_h - die_h) / 2
    f.append(rect(die_x, die_y, die_w, die_h, fill="#eef4ff", stroke=NEG, sw=2))
    f.append(text(die_x + die_w/2, die_y + die_h/2 + 5, "кристал", size=13, bold=True, color=NEG))

    # 10 ніжок по низу; значення нГн — 20-піновий DIP із даташита TI (кути 13.7 → центр 3.4)
    n = 10
    pin_gap = pkg_w / (n + 1)
    die_cx = die_x + die_w/2
    ind = [13.7, 11.1, 8.6, 6.0, 3.4, 3.4, 6.0, 8.6, 11.1, 13.7]
    for i in range(n):
        px = pkg_x + pin_gap * (i + 1)
        py = pkg_y + pkg_h
        f.append(line(px, py, px, py + 24, color=INK, sw=2.4))
        dxp = die_x if px < die_cx else die_x + die_w
        col = POS if ind[i] >= 11 else (FIELD if ind[i] <= 3.5 else "#8a5a00")
        f.append(line(dxp, die_y + die_h/2, px, py, color=col, sw=1.6, dash="2 3"))
        f.append(text(px, py + 40, "%.1f" % ind[i], size=11, color=col,
                      bold=(ind[i] >= 11 or ind[i] <= 3.5)))

    f.append(text(pkg_x - 6, pkg_y + pkg_h + 40, "нГн:", size=11, anchor="end", color=MUTED))
    f.append(text(pkg_x + pin_gap, pkg_y - 14, "кут", size=12, color=POS, bold=True))
    f.append(text(pkg_x + pin_gap*5.0, pkg_y - 14, "центр", size=12, color=FIELD, bold=True))

    fb = fitbox(90, 302, 540, 44,
                "кутова ніжка — найдовший шлях до кристала → найбільша L (≈13.7 нГн); "
                "центральна — найкоротший → найменша (≈3.4 нГн)",
                size=13, fill="#fdecea", stroke=POS)
    f.append(fb)
    render(os.path.join(IMG, 'corner-pins.svg'), W, H, *f)


# ── Фігура 6 (вставка hist): стара vs нова розпіновка живлення ──────────────
def fig_pinout_answer():
    W, H = 720, 344
    f = []
    f.append(text(W/2, 24, "Відповідь виробників: живлення з кутів — у центр", size=16, bold=True))

    def chip(cx, title, power_pins, note, ok):
        out = []
        w, h = 210, 190
        x, y = cx - w/2, 56
        out.append(rect(x, y, w, h, fill="#f7f8fa", stroke=INK, sw=2))
        out.append(text(cx, y - 8, title, size=13, bold=True))
        dw, dh = 66, 66
        out.append(rect(cx - dw/2, y + h/2 - dh/2, dw, dh, fill="#eef4ff", stroke=NEG, sw=1.8))
        out.append(text(cx, y + h/2 + 4, "die", size=11, color=NEG))
        for (frac, edge, lbl, col) in power_pins:
            px = x + w * frac
            py = (y + h) if edge == "b" else y
            dy = 20 if edge == "b" else -20
            out.append(line(px, py, px, py + dy, color=col, sw=4))
            ty = py + dy + (12 if edge == "b" else -6)
            out.append(text(px, ty, lbl, size=10, color=col, bold=True))
            dpx = cx - dw/2 if px < cx else cx + dw/2
            out.append(line(dpx, y + h/2, px, py, color=col, sw=1.3, dash="2 3"))
        bcol = FIELD if ok else POS
        out.append(text(cx, y + h + 40, note, size=11, color=bcol, bold=True))
        return out

    f += chip(190, "звична розпіновка",
              [(0.06, "t", "VCC", POS), (0.94, "b", "GND", NEG)],
              "довгі дротики • велика L", ok=False)
    f += chip(530, "родина 74AC11xxx",
              [(0.40, "t", "VCC", POS), (0.60, "t", "VCC", POS),
               (0.34, "b", "GND", NEG), (0.50, "b", "GND", NEG), (0.66, "b", "GND", NEG)],
              "короткі дротики • мала L", ok=True)

    f.append(arrow(300, 152, 415, 152, color=INK, sw=2.2))

    fb = fitbox(70, 296, 580, 40,
                "ціна: розпіновка більше не збігається зі стандартним 7400 — не drop-in, "
                "інше розведення, більше пінів",
                size=12, fill="#fff3cd", stroke="#e0a800")
    f.append(fb)
    render(os.path.join(IMG, 'pinout-answer.svg'), W, H, *f)


if __name__ == "__main__":
    fig_path()
    fig_wave()
    fig_cures()
    fig_budget()
    fig_corner_pins()
    fig_pinout_answer()
    print("ok: figures written to", IMG)
