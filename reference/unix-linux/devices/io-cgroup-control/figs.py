# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"


# ── 1. Де на шляху запиту ще відомо, чия це група ───────────────────────────
def fig_decision_points():
    W, H = 1340, 1030
    p = []

    p.append(text(W / 2, 46, "Шлях запиту: три брами, і межа, за якою груп немає",
                  size=18, bold=True))

    # ── ліва гілка: буферизований запис ────────────────────────────────────
    lx = 330
    f, w1, h1 = textbox(lx, 130, ["буферизований запис", "write() повертається одразу"],
                        size=14, pad=14, fill=WARM, stroke=LINE)
    p.append(f)
    f, w2, h2 = textbox(lx, 265, ["сторінковий кеш", "брудну сторінку записано за групою"],
                        size=14, pad=14, fill=WARM, stroke=LINE)
    p.append(f)
    f, w3, h3 = textbox(lx, 400, ["потік фонового запису", "подає чужу роботу, не свою"],
                        size=14, pad=14, fill=WARM, stroke=LINE)
    p.append(f)
    p.append(arrow(lx, 130 + h1 / 2 + 6, lx, 265 - h2 / 2 - 6))
    p.append(arrow(lx, 265 + h2 / 2 + 6, lx, 400 - h3 / 2 - 6))

    # ── права гілка: пряме подання ─────────────────────────────────────────
    rx = 1010
    f, w4, h4 = textbox(rx, 130, ["читання і O_DIRECT", "подає сам процес"],
                        size=14, pad=14, fill=BLUE, stroke=LINE)
    p.append(f)

    # ── злиття ─────────────────────────────────────────────────────────────
    cx = 670
    f, wb, hb = textbox(cx, 520, "bio з міткою cgroup", size=16, bold=True,
                        pad=16, fill=GREEN, stroke=FIELD, sw=2)
    p.append(f)
    p.append(arrow(lx, 400 + h3 / 2 + 6, cx - wb / 2 - 14, 520 - hb / 2 - 4))
    p.append(arrow(rx, 130 + h4 / 2 + 6, cx + wb / 2 + 14, 520 - hb / 2 - 4))

    # ── три брами ──────────────────────────────────────────────────────────
    gates = [
        (645, RED, "io.max — чи вкладається група в стелю байтів і операцій"),
        (755, BLUE, "io.weight (iocost) — чи лишився в групи віртуальний час"),
        (865, GREEN, "io.latency — чи не страждає через це захищена група"),
    ]
    prev_bottom = 520 + hb / 2
    for y, fill, label in gates:
        f, wg, hg = textbox(cx, y, label, size=14, pad=14, fill=fill, stroke=LINE)
        p.append(f)
        p.append(arrow(cx, prev_bottom + 6, cx, y - hg / 2 - 6))
        prev_bottom = y + hg / 2

    f, wd, hd = textbox(cx, 975, "планувальник → тег → пристрій",
                        size=15, pad=14, fill=GREY, stroke=MUTED)
    p.append(f)
    p.append(arrow(cx, prev_bottom + 6, cx, 975 - hd / 2 - 6))
    p.append(text(cx, 975 + hd / 2 + 30,
                  "нижче цієї межі поняття «чия це група» в інтерфейсі вже немає",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, 'decision-points.svg'), W, H, *p)


# ── 2. Віртуальні годинники iocost ──────────────────────────────────────────
def fig_iocost_clocks():
    W, H = 1420, 780
    p = []

    p.append(text(W / 2, 44, "Однаковий запит зсуває власний час групи по-різному",
                  size=18, bold=True))

    X0, X1 = 430, 1360          # доріжка власного часу групи
    DEV = 1010                  # де стоїть годинник пристрою

    p.append(line(DEV, 110, DEV, 690, color=POS, sw=2, dash="8 6"))
    p.append(text(DEV, 96, "годинник пристрою", size=14, color=POS, bold=True))

    rows = [
        (215, "A · вага 600", 50, GREEN, "запас власного часу ще великий"),
        (395, "B · вага 300", 100, BLUE, "запасу лишилося менше"),
        (575, "C · вага 100", 300, RED,
         "вибігла поперед годинника пристрою — подання чекає"),
    ]

    for y, label, step, fill, note in rows:
        f, wl, hl = textbox(225, y, label, size=15, pad=14, fill=fill, stroke=LINE)
        p.append(f)

        p.append(rect(X0, y - 26, X1 - X0, 52, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=5))
        for i in range(3):
            p.append(rect(X0 + i * step + 3, y - 22, step - 6, 44,
                          fill=fill, stroke=LINE, sw=1.2, rx=4))
        end = X0 + 3 * step
        p.append(line(end, y - 40, end, y + 40, color=INK, sw=3))

        p.append(text(X0, y + 66, note, size=13, color=MUTED, anchor="start"))

    p.append(text(X0, 152, "три однакові запити, зліва направо", size=13,
                  color=MUTED, anchor="start"))

    return render(os.path.join(IMG, 'iocost-clocks.svg'), W, H, *p)


# ── 3. Що робить кожен контролер у момент події ─────────────────────────────
def fig_when_things_change():
    W, H = 1420, 620
    p = []

    p.append(text(W / 2, 44, "Частка носія, яку бачить група, до події і після неї",
                  size=18, bold=True))

    PW, PH = 400, 250           # рамка графіка
    PY = 150
    gap = 55
    x0 = (W - (3 * PW + 2 * gap)) / 2

    panels = [
        ("io.max", GREEN, [(0.0, 0.40), (0.5, 0.40), (0.5, 0.40), (1.0, 0.40)],
         "сусід замовк", "стеля лишилася на місці:", "носій простоює, група — ні швидше"),
        ("io.weight (iocost)", BLUE, [(0.0, 0.40), (0.5, 0.40), (0.56, 0.95), (1.0, 0.95)],
         "сусід замовк", "донор віддав невикористану частку:", "група розганяється на весь носій"),
        ("io.latency", RED, [(0.0, 0.95), (0.5, 0.95), (0.56, 0.45), (0.66, 0.12),
                             (0.82, 0.12), (0.9, 0.6), (1.0, 0.95)],
         "захищена група промахнулася", "крива — це СУСІД захищеної групи:",
         "глибину подання тиснуть, потім відпускають"),
    ]

    for i, (name, fill, pts, ev, cap1, cap2) in enumerate(panels):
        px = x0 + i * (PW + gap)

        p.append(text(px + PW / 2, PY - 24, name, size=16, bold=True))
        p.append(rect(px, PY, PW, PH, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))

        ex = px + PW * 0.5
        p.append(line(ex, PY + 6, ex, PY + PH - 6, color=MUTED, sw=1.2, dash="6 6"))

        poly = " ".join("%g,%g" % (px + fx * PW, PY + PH - fy * PH) for fx, fy in pts)
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.5"/>'
                 % (poly, INK))

        p.append(text(px + PW / 2, PY + PH + 34, ev, size=13, color=MUTED))
        p.append(mtext(px + PW / 2, PY + PH + 68, [cap1, cap2], size=13, color=INK))

    return render(os.path.join(IMG, 'when-things-change.svg'), W, H, *p)


if __name__ == '__main__':
    for f in (fig_decision_points, fig_iocost_clocks, fig_when_things_change):
        print(f())
