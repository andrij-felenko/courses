# -*- coding: utf-8 -*-
"""Фігури до статті «Первинне налаштування: калібрування давачів і радіо»
(guide/embedded/avtopilot/fc-setup-calibration).
Чистий Python, без залежностей; svgkit — зі scripts/ (не переписувати)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Порядок первинного налаштування: чому саме такий ланцюг.
#    Кожен крок спирається на попередній — переставиш і система не «зброїться».
# ─────────────────────────────────────────────────────────────────────────────
def fig_setup_order():
    W, H = 960, 300
    frags = [text(W / 2, 30, "Порядок первинного налаштування — не косметичний", size=15, bold=True)]

    steps = [
        ("1. Прошивка\nі рама", "FRAME_CLASS,\nтип апарата", FIELD),
        ("2. Акселе-\nрометр", "6 положень\n→ рівень", POS),
        ("3. Компас", "«танець»\n→ курс", NEG),
        ("4. Радіо\n(RC)", "краї стіків\n→ входи", INK),
        ("5. Режими\nй failsafe", "перемикач,\nповедінка", MUTED),
    ]
    n = len(steps)
    margin = 40
    gap = 22
    bw = (W - 2 * margin - (n - 1) * gap) / n
    y = 90
    bh = 120
    cxs = []
    for i, (title, sub, col) in enumerate(steps):
        x = margin + i * (bw + gap)
        cx = x + bw / 2
        cxs.append(cx)
        frags.append(rect(x, y, bw, bh, fill="#ffffff", stroke=col, sw=2.2))
        frags.append(mtext(cx, y + 30, title, size=14, bold=True, color=col))
        frags.append(mtext(cx, y + 74, sub, size=11.5, color=MUTED))
    # стрілки між кроками
    for i in range(n - 1):
        x1 = cxs[i] + bw / 2 + 2
        x2 = cxs[i + 1] - bw / 2 - 2
        frags.append(arrow(x1, y + bh / 2, x2, y + bh / 2))

    frags.append(text(W / 2, y + bh + 42,
                      "Спирається на попереднє: без рівня компас не має «низу», без входів немає що калібрувати; кінець — arming-перевірки",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'setup-order.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Калібрування акселерометра: гравітація як еталон на кожній грані.
#    Шість положень дають ±1g по кожній осі → з них однозначно зсув і масштаб.
# ─────────────────────────────────────────────────────────────────────────────
def fig_accel_six():
    W, H = 900, 480
    frags = [text(W / 2, 30, "Акселерометр: гравітація — безкоштовний еталон на кожній грані", size=15, bold=True)]

    # Зліва — куб у трьох положеннях зі стрілкою g; праворуч — три осі з двома точками кожна.
    def cube(cx, cy, s, label, gdir):
        f = []
        d = s * 0.42  # зсув для «третього виміру»
        # передня грань
        f.append(rect(cx - s / 2, cy - s / 2, s, s, fill="#eef2f7", stroke=INK, sw=1.8))
        # верхня грань
        f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="#dfe6ee" stroke="%s" stroke-width="1.8"/>'
                 % (cx - s / 2, cy - s / 2, cx - s / 2 + d, cy - s / 2 - d,
                    cx + s / 2 + d, cy - s / 2 - d, cx + s / 2, cy - s / 2, INK))
        # права грань
        f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="#d3dbe6" stroke="%s" stroke-width="1.8"/>'
                 % (cx + s / 2, cy - s / 2, cx + s / 2 + d, cy - s / 2 - d,
                    cx + s / 2 + d, cy + s / 2 - d, cx + s / 2, cy + s / 2, INK))
        # вектор g (завжди вниз)
        gx, gy0, gy1 = cx, cy + s / 2 + 8, cy + s / 2 + 46
        f.append(arrow(gx, gy0, gx, gy1, color=POS, sw=2.4))
        f.append(text(gx + 16, gy1 - 4, "g", size=13, color=POS, bold=True, anchor="start"))
        f.append(text(cx, cy - s / 2 - d - 12, label, size=12, bold=True))
        # яка вісь «бачить» g
        f.append(text(cx, cy + 5, gdir, size=12, color=NEG, bold=True))
        return f

    # cube #2 «на боці» опущено (cy=352), щоб стрілка g куба «рівень» (сягає y≈238)
    # не налазила на його підпис і на літеру «g» — раніше вони збігались коло y≈231
    frags += cube(150, 150, 84, "рівень", "Z:−g")
    frags += cube(150, 352, 84, "на боці", "Y:+g")
    frags += cube(300, 250, 84, "носом вниз", "X:+g")

    # праворуч — осі з двома опорними точками
    ax_x = 560
    ax_y0 = 90
    dy = 100
    axes = [("вісь X", "X:−g", "X:+g"), ("вісь Y", "Y:−g", "Y:+g"), ("вісь Z", "Z:−g", "Z:+g")]
    for i, (nm, lo, hi) in enumerate(axes):
        y = ax_y0 + i * dy
        frags.append(line(ax_x, y, ax_x + 250, y, color=INK, sw=1.6))
        frags.append(text(ax_x - 10, y + 5, nm, size=12, bold=True, anchor="end"))
        # дві точки: −1g і +1g
        frags.append(circle(ax_x + 20, y, 6, fill="#eaf0fd", stroke=NEG, sw=2))
        frags.append(text(ax_x + 20, y - 14, "−1g", size=11, color=NEG))
        frags.append(circle(ax_x + 230, y, 6, fill="#fdecea", stroke=POS, sw=2))
        frags.append(text(ax_x + 230, y - 14, "+1g", size=11, color=POS))
        frags.append(text(ax_x + 125, y + 22, "нуль між ними → зсув; розмах → масштаб", size=10.5, color=MUTED))

    frags.append(text(W / 2, H - 22,
                      "Шість граней дають по дві точки (±1g) на кожну вісь — рівно стільки, щоб знайти зсув і масштаб. Найважливіший — «рівень»",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'accel-six.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Калібрування RC: сирі мікросекунди → нормований вхід [-1..+1].
#    Крайні положення стіка задають min/max, центр — trim.
# ─────────────────────────────────────────────────────────────────────────────
def fig_rc_endpoints():
    W, H = 900, 340
    frags = [text(W / 2, 30, "Калібрування радіо: сирі мікросекунди стають нормованим входом", size=15, bold=True)]

    # горизонтальна шкала мікросекунд
    x0, x1 = 120, 780
    y = 130
    frags.append(line(x0, y, x1, y, color=INK, sw=2))
    # три вузли: MIN, TRIM, MAX
    def tick(px, top, lab, val, col):
        f = [line(px, y - 8, px, y + 8, color=col, sw=2.4)]
        f.append(text(px, y - 16, lab, size=12.5, bold=True, color=col))
        f.append(text(px, y + 28, val, size=12, color=MUTED))
        return f
    frags += tick(x0, y, "RCn_MIN", "≈ 1100 мкс", NEG)
    frags += tick((x0 + x1) / 2, y, "RCn_TRIM", "≈ 1500 мкс", INK)
    frags += tick(x1, y, "RCn_MAX", "≈ 1900 мкс", POS)
    # підпис що це — крайні положення стіка
    frags.append(text(x0, y + 52, "стік у краю", size=11, color=NEG))
    frags.append(text((x0 + x1) / 2, y + 52, "стік відпущено", size=11, color=INK))
    frags.append(text(x1, y + 52, "стік у краю", size=11, color=POS))

    # стрілка «нормування» вниз до діапазону [-1..+1]
    y2 = 250
    frags.append(arrow(W / 2, y + 66, W / 2, y2 - 26, sw=2))
    frags.append(text(W / 2 + 12, (y + 66 + y2 - 26) / 2, "нормування", size=11, color=MUTED, anchor="start"))
    frags.append(line(x0, y2, x1, y2, color=FIELD, sw=2.4))
    frags += [line(x0, y2 - 7, x0, y2 + 7, color=NEG, sw=2.4),
              line((x0 + x1) / 2, y2 - 7, (x0 + x1) / 2, y2 + 7, color=INK, sw=2.4),
              line(x1, y2 - 7, x1, y2 + 7, color=POS, sw=2.4)]
    frags.append(text(x0, y2 + 24, "−1", size=12.5, bold=True, color=NEG))
    frags.append(text((x0 + x1) / 2, y2 + 24, "0", size=12.5, bold=True))
    frags.append(text(x1, y2 + 24, "+1", size=12.5, bold=True, color=POS))
    frags.append(text(W / 2, H - 18,
                      "Крайні положення стіка записують RCn_MIN/MAX, центр — RCn_TRIM. Далі керування бачить не мкс, а частку відхилення",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'rc-endpoints.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 4. (вставка proj-accel-cal) Чому вісь, що не дивилась точно вниз, калібрується
#    найгірше. Дві осі бачать по два «упори» ±1g (густо → міцне рівняння).
#    Третя за всі шість положень лишалась близько нуля → її розмах не заміряно,
#    масштаб погано зумовлений (ділення майже на нуль).
# ─────────────────────────────────────────────────────────────────────────────
def fig_illcond_axis():
    W, H = 900, 420
    frags = [text(W / 2, 30, "Чому найгірше калібрується вісь, що не дивилась точно вниз", size=15, bold=True)]

    # Дві осі-«еталони»: точки біля −1g і +1g (широкий розмах).
    def good_axis(y, nm):
        x0, x1 = 120, 470
        f = [line(x0, y, x1, y, color=INK, sw=1.6),
             text(x0 - 12, y + 5, nm, size=12, bold=True, anchor="end")]
        # відлік «0g» орієнтир — тонка риска
        xm = (x0 + x1) / 2
        f.append(line(xm, y - 6, xm, y + 6, color=MUTED, sw=1.2, dash="3,3"))
        f.append(text(xm, y + 20, "0", size=10, color=MUTED))
        # два щільні згустки точок біля упорів
        for dx in (-3, 0, 3, 6):
            f.append(circle(x0 + 18 + dx, y, 3.2, fill="#eaf0fd", stroke=NEG, sw=1.4))
            f.append(circle(x1 - 18 + dx, y, 3.2, fill="#fdecea", stroke=POS, sw=1.4))
        f.append(text(x0 + 20, y - 16, "−1g", size=11, color=NEG))
        f.append(text(x1 - 20, y - 16, "+1g", size=11, color=POS))
        f.append(text(xm, y - 16, "широкий розмах → масштаб певний", size=10.5, color=FIELD))
        return f

    frags += good_axis(95, "вісь X")
    frags += good_axis(150, "вісь Y")

    # «Погана» вісь: за всі шість положень лишалась близько нуля.
    y = 240
    x0, x1 = 120, 470
    frags.append(line(x0, y, x1, y, color=INK, sw=1.6))
    frags.append(text(x0 - 12, y + 5, "вісь Z", size=12, bold=True, anchor="end"))
    xm = (x0 + x1) / 2
    frags.append(line(xm, y - 6, xm, y + 6, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(text(xm, y + 20, "0", size=10, color=MUTED))
    # усі точки збилися біля центру (мала проєкція g на цю вісь у всіх положеннях)
    import math as _m
    for k in range(8):
        dx = 14 * _m.cos(k) + (k - 4) * 3
        frags.append(circle(xm + dx, y, 3.2, fill="#f0f0f0", stroke=POS, sw=1.4))
    frags.append(text(xm, y - 16, "усі відліки збились коло нуля — упори ±1g так і не заміряно",
                      size=11, color=POS))
    frags.append(text(xm, y + 40, "розмах ≈ 0 → масштаб = (велике)/(майже нуль) → погано зумовлений",
                      size=10.5, color=MUTED))

    # Висновок унизу — рамка.
    body, bw, bh = textbox(W / 2, 350,
                           "Ліки: у кожному з шести положень справді клади апарат на грань,\n"
                           "щоб КОЖНА вісь хоч раз побачила точні −1g і +1g. Недбалі кути калічать саме масштаб.",
                           size=12, pad=12, fill="#f4f8f4", stroke=FIELD, sw=1.6)
    frags.append(body)
    render(os.path.join(IMG, 'illcond-axis.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_setup_order()
    fig_accel_six()
    fig_rc_endpoints()
    fig_illcond_axis()
    print("OK: setup-order.svg, accel-six.svg, rc-endpoints.svg, illcond-axis.svg")
