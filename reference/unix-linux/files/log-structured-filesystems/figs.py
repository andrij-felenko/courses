# -*- coding: utf-8 -*-
"""Фігури до теми «Лог-структуровані файлові системи»."""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

LIVE = "#cfe6d6"
DEAD = "#eef0f2"
HEAD = "#fbe3df"


def inplace_vs_log():
    W, H = 1040, 400
    f = []

    # ── ліва панель: кожна структура на своєму місці ──────────────────────
    ax = 50
    f.append(text(ax + 220, 48, "кожна структура на своєму місці", size=15, bold=True))
    f.append(text(ax + 220, 76, "три переїзди голівки", size=13, color=MUTED))

    f.append(rect(ax, 190, 440, 46, fill=DEAD))
    cells = [(30, 74, "бітова\nкарта"), (180, 74, "дані"), (330, 84, "inode")]
    for dx, w, lab in cells:
        f.append(rect(ax + dx, 190, w, 46, fill=LIVE))
        f.append(mtext(ax + dx + w / 2, 208 if "\n" in lab else 219,
                       lab, size=12))

    centers = [ax + 30 + 37, ax + 180 + 37, ax + 330 + 42]
    f.append(arrow(centers[0], 168, centers[1], 168, color=POS))
    f.append(arrow(centers[1], 140, centers[2], 140, color=POS))
    f.append(text(ax + 220, 290, "12.7 мс позиціювання на кожен запис",
                  size=13, color=POS))
    f.append(text(ax + 220, 316, "корисно передано 12 КіБ за 38 мс", size=13, color=MUTED))

    # ── права панель: усе в голову лога ───────────────────────────────────
    bx = 560
    f.append(text(bx + 220, 48, "усе — в голову лога", size=15, bold=True))
    f.append(text(bx + 220, 76, "один послідовний запис", size=13, color=MUTED))

    f.append(rect(bx, 190, 440, 46, fill=DEAD))
    seg = [("дані", 96), ("дані", 96), ("inode", 84), ("підсумок", 104)]
    px = bx + 60
    for lab, w in seg:
        f.append(rect(px, 190, w, 46, fill=HEAD))
        f.append(text(px + w / 2, 219, lab, size=12))
        px += w

    f.append(arrow(bx + 60, 160, bx + 440, 160, color=FIELD))
    f.append(text(bx + 250, 140, "голова лога рухається в один бік",
                  size=12, color=FIELD))
    f.append(text(bx + 220, 290, "0 переїздів між сусідніми блоками", size=13, color=FIELD))
    f.append(text(bx + 220, 316, "той самий обсяг за частку мілісекунди", size=13, color=MUTED))

    render(os.path.join(OUT, 'inplace-vs-log.svg'), W, H, *f)


def imap_checkpoint():
    W, H = 980, 500
    f = []
    cx = 340
    ys = [70, 178, 286, 394]
    labels = [
        "каталог: «звіт.txt» → 17",
        "мапа inode: 17 → адреса 9042",
        "inode 17 за адресою 9042: карта блоків",
        "блок даних за адресою 15870",
    ]
    boxes = []
    for y, lab in zip(ys, labels):
        body, w, h = textbox(cx, y, lab, size=14, min_w=300)
        boxes.append((y, h))
        f.append(body)

    for i in range(3):
        y1 = boxes[i][0] + boxes[i][1] / 2
        y2 = boxes[i + 1][0] - boxes[i + 1][1] / 2
        f.append(arrow(cx, y1, cx, y2))

    # контрольна ділянка — єдина нерухома адреса
    body, w, h = textbox(760, 178,
                         "контрольна ділянка\nфіксована адреса\nдві копії по черзі",
                         size=13, fill=HEAD, stroke=POS)
    f.append(body)
    f.append(arrow(760 - w / 2, 178, cx + 150, 178, color=POS))
    f.append(text(760, 178 + h / 2 + 30, "єдине, що не рухається", size=12, color=POS))

    f.append(mtext(120, 300, ["усе нижче", "пливе в лозі:", "кожна нова", "версія лягає", "в голову"],
                   size=12, color=MUTED))

    render(os.path.join(OUT, 'imap-checkpoint.svg'), W, H, *f)


def segment_cleaning():
    W, H = 1020, 440
    f = []
    segw, segh, cellw = 156, 52, 26
    xs = [60, 300, 540, 780]
    live_counts = [2, 1, 5, 2]

    f.append(text(510, 44, "сегменти лога: темне — живі блоки, світле — перекриті",
                  size=14, bold=True))

    for x, live in zip(xs, live_counts):
        for i in range(6):
            fill = LIVE if i < live else DEAD
            f.append(rect(x + i * cellw, 74, cellw, segh, fill=fill, rx=2))
        u = live / 6.0
        f.append(text(x + segw / 2, 152, "u = %.2f" % u, size=13, color=MUTED))

    f.append(text(xs[2] + segw / 2, 180, "надто повний — не чіпаємо", size=12, color=POS))

    f.append(arrow(510, 208, 510, 262, color=FIELD, sw=2.2))
    f.append(text(760, 238, "прибирач бере три найпорожніші", size=13, color=FIELD))

    for i in range(5):
        f.append(rect(60 + i * cellw, 292, cellw, segh, fill=LIVE, rx=2))
    f.append(rect(60 + 5 * cellw, 292, cellw, segh, fill=HEAD, rx=2))
    f.append(text(60 + segw / 2, 372, "нова голова лога", size=13))
    f.append(text(60 + segw / 2, 396, "5 живих блоків переписано", size=12, color=MUTED))

    for x in (xs[1], xs[3]):
        f.append(rect(x, 292, segw, segh, fill=BG, rx=4))
        f.append(text(x + segw / 2, 324, "вільний", size=13, color=FIELD))
    for i in range(6):
        fill = LIVE if i < live_counts[2] else DEAD
        f.append(rect(xs[2] + i * cellw, 292, cellw, segh, fill=fill, rx=2))
    f.append(text(xs[2] + segw / 2, 372, "лишився повним", size=12, color=POS))
    f.append(text(510, 396, "звільнено два сегменти, третій став новою головою", size=13, color=FIELD))

    render(os.path.join(OUT, 'segment-cleaning.svg'), W, H, *f)


def log_on_log():
    W, H = 1020, 350
    f = []
    x0, x1 = 270, 960

    f.append(text(40, 108, "файлова система", size=14, anchor="start", bold=True))
    f.append(text(40, 262, "накопичувач (FTL)", size=14, anchor="start", bold=True))

    sw = (x1 - x0) / 3.0
    for i in range(3):
        f.append(rect(x0 + i * sw, 78, sw, 56, fill=LIVE))
        f.append(text(x0 + i * sw + sw / 2, 112, "сегмент", size=13))

    bw = (x1 - x0) / 4.0
    for i in range(4):
        f.append(rect(x0 + i * bw, 232, bw, 56, fill=HEAD))
        f.append(text(x0 + i * bw + bw / 2, 266, "блок стирання", size=12))

    for i in (1, 2):
        f.append(line(x0 + i * sw, 134, x0 + i * sw, 232, color=POS, sw=1.6, dash="5,4"))

    f.append(text(615, 190, "межі не збігаються", size=13, color=POS))
    f.append(text(510, 326,
                  "звільнений сегмент лишає живі сторінки в блоці стирання — прибирає ще й накопичувач",
                  size=13, color=MUTED))

    render(os.path.join(OUT, 'log-on-log.svg'), W, H, *f)


def argument_timeline():
    """Хроніка суперечки навколо LFS (вставка hist-lfs-argument)."""
    W, H = 1300, 440
    f = []
    axis_y = 220
    f.append(line(60, axis_y, W - 60, axis_y, color=MUTED, sw=2))

    events = [
        (1, "1989\nОстергаут і Дуґліс:\nдиск стане вузьким місцем"),
        (-1, "1991 SOSP · 1992 TOCS\nSprite LFS:\n70 % смуги на запис"),
        (1, "1993 USENIX\nBSD-LFS:\nреалізація поза Sprite"),
        (-1, "1995 USENIX\nлогування проти\nкластеризації"),
        (1, "1995–96\nкритика методики\nй відповідь на неї"),
        (-1, "1997\nстаріння ФС,\nадаптивне прибирання"),
    ]
    step = (W - 220) / (len(events) - 1)
    for i, (side, label) in enumerate(events):
        cx = 110 + i * step
        cy = axis_y - side * 130
        body, bw, bh = textbox(cx, cy, label, size=13, pad=11,
                               fill=FILL if side > 0 else HEAD)
        f.append(body)
        edge = cy + bh / 2 if side > 0 else cy - bh / 2
        f.append(line(cx, edge, cx, axis_y, color=MUTED, sw=1.4, dash="4,4"))
        f.append(circle(cx, axis_y, 6, fill=BG, stroke=MUTED, sw=2))

    f.append(text(W / 2, 40, "вісь часу: теза зверху, перевірка знизу",
                  size=13, color=MUTED))
    render(os.path.join(OUT, 'argument-timeline.svg'), W, H, *f)


def what_was_measured():
    """Дві лабораторії міряли різні речі (вставка hist-lfs-argument)."""
    W, H = 1180, 430
    f = []
    lx, cw = 60, 340
    ax, bx = 400, 780
    f.append(text(ax + cw / 2, 46, "Берклі, 1991: Sprite LFS", size=15, bold=True))
    f.append(text(bx + cw / 2, 46, "Гарвард, 1995: BSD-LFS", size=15, bold=True))

    rows = [
        ("том", "свіжий, близько 300 МБ", "заповнений, з історією"),
        ("навантаження", "10 000 файлів по 1 КіБ", "транзакції з fsync на кожну"),
        ("прибирання", "під час замірів не працює", "працює й входить у число"),
        ("з чим порівняно", "SunOS 4.0.3, класична FFS", "FFS із кластеризацією"),
        ("що вийшло", "близько 10× на дрібних записах", "прибирання з'їдає більшу\nчастину виграшу"),
    ]
    y = 78
    for lab, a, b in rows:
        h = 62
        f.append(fitbox(lx, y, 320, h, lab, size=13, fill=BG, stroke=BG, bold=True))
        f.append(fitbox(ax, y, cw, h, a, size=13, fill=FILL))
        f.append(fitbox(bx, y, cw, h, b, size=13, fill=HEAD))
        y += h + 8

    render(os.path.join(OUT, 'what-was-measured.svg'), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════
# Фігури до вставки math-cleaning-cost.md
# ══════════════════════════════════════════════════════════════════════════

BAND = "#fbeeeb"          # «дорога середина» кривої вартості
BARF = "#dbe5fb"


def _poly(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (s, color, sw, d))


def write_cost_curve():
    """Вартість запису 2/(1−u) і варіант із читанням лише живого."""
    W, H = 980, 470
    L, R, T, B0 = 100, 900, 60, 400
    UMAX, CMAX = 0.85, 12.5

    def xp(u):
        return L + u / UMAX * (R - L)

    def yp(c):
        return B0 - c / CMAX * (B0 - T)

    f = []
    f.append(line(L, B0, R + 10, B0, sw=1.6))
    f.append(line(L, B0, L, T - 5, sw=1.6))
    for u in (0.0, 0.2, 0.4, 0.6, 0.8):
        f.append(line(xp(u), B0, xp(u), B0 + 6, sw=1.2))
        f.append(text(xp(u), B0 + 26, "%.1f" % u, size=13, color=MUTED))
    for c in (0, 2, 4, 6, 8, 10, 12):
        f.append(line(L - 6, yp(c), L, yp(c), sw=1.2))
        f.append(text(L - 14, yp(c) + 5, str(c), size=13, color=MUTED,
                      anchor="end"))
    f.append(text(xp(0.42), B0 + 54, "заповненість сегмента-жертви  u",
                  size=14, color=MUTED))
    f.append(text(L - 52, T - 20, "вартість запису", size=14, color=MUTED,
                  anchor="start"))

    full, lean = [], []
    u = 0.0
    while u <= UMAX + 1e-9:
        c1 = 2.0 / (1.0 - u)
        c2 = (1.0 + u) / (1.0 - u)
        if c1 <= CMAX:
            full.append((xp(u), yp(c1)))
        if c2 <= CMAX:
            lean.append((xp(u), yp(c2)))
        u += 0.005
    f.append(_poly(full, color=POS, sw=2.4))
    f.append(_poly(lean, color=NEG, sw=2.0, dash="7,5"))

    f.append(line(120, 92, 170, 92, color=POS, sw=2.4))
    f.append(text(184, 97, "2/(1−u) — читаємо сегмент цілком",
                  size=13, anchor="start"))
    f.append(line(120, 126, 170, 126, color=NEG, sw=2.0, dash="7,5"))
    f.append(text(184, 131, "(1+u)/(1−u) — читаємо лише живі блоки",
                  size=13, anchor="start"))

    xg = xp(0.45)
    f.append(line(xg, yp(2.0 / 0.55), xg, yp(1.45 / 0.55), color=MUTED, sw=1.4))
    f.append(text(xg + 12, yp(2.9) + 5, "1", size=13, color=MUTED,
                  anchor="start"))

    for uu, cc, lab in ((0.5, 4.0, "u = 0.5 → вартість 4"),
                        (0.8, 10.0, "u = 0.8 → вартість 10")):
        f.append(circle(xp(uu), yp(cc), 5, fill=POS, stroke=POS))
        f.append(text(xp(uu) - 18, yp(cc) - 24, lab, size=13, anchor="end"))

    render(os.path.join(OUT, 'write-cost-curve.svg'), W, H, *f)


def cold_segment_lingers():
    """Гарячий устигає 21 цикл, поки холодний повзе крізь дорогу зону."""
    W, H = 980, 470
    L, R, T, B0 = 100, 900, 80, 380
    TMAX = 40.0

    def xp(t):
        return L + t / TMAX * (R - L)

    def yp(u):
        return B0 - u * (B0 - T)

    f = []
    f.append(rect(L, yp(0.9), R - L, yp(0.4) - yp(0.9), fill=BAND,
                  stroke="none", sw=0, rx=0))
    f.append(text(L + 16, yp(0.9) + 24,
                  "дорога середина: вартість 3.3 … 20", size=13, color=POS,
                  anchor="start"))

    f.append(line(L, B0, R + 10, B0, sw=1.6))
    f.append(line(L, B0, L, T - 5, sw=1.6))
    for t in (0, 10, 20, 30, 40):
        f.append(line(xp(t), B0, xp(t), B0 + 6, sw=1.2))
        f.append(text(xp(t), B0 + 24, str(t), size=13, color=MUTED))
    for u in (0.0, 0.25, 0.5, 0.75, 1.0):
        f.append(line(L - 6, yp(u), L, yp(u), sw=1.2))
        f.append(text(L - 14, yp(u) + 5, "%.2f" % u, size=13, color=MUTED,
                      anchor="end"))
    f.append(text(L - 14, T - 26, "заповненість сегмента  u", size=14,
                  color=MUTED, anchor="start"))
    f.append(text(xp(20), B0 + 52, "час у життях гарячого блока", size=14,
                  color=MUTED))

    hot, t = [], 0.0
    period = math.log(1 / 0.15)
    while t <= TMAX:
        hot.append((xp(t), yp(math.exp(-math.fmod(t, period)))))
        t += 0.05
    f.append(_poly(hot, color=POS, sw=1.6))

    cold, t = [], 0.0
    while t <= TMAX:
        cold.append((xp(t), yp(math.exp(-t / 81.0))))
        t += 0.2
    f.append(_poly(cold, color=NEG, sw=2.6))

    tc = 81 * math.log(1 / 0.762)
    tg = 81 * math.log(1 / 0.64)
    f.append(circle(xp(tc), yp(0.762), 5, fill=NEG, stroke=NEG))
    f.append(text(xp(tc) + 18, yp(0.762) - 6,
                  "0.76 — тут його бере вигода/витрати", size=13,
                  color=NEG, anchor="start"))
    f.append(circle(xp(tg), yp(0.64), 5, fill=MUTED, stroke=MUTED))
    f.append(text(xp(tg) - 20, yp(0.64) + 40,
                  "0.64 — лише тут його візьме жадібність", size=13,
                  color=MUTED, anchor="end"))

    f.append(text(xp(30.5), yp(0.95), "холодний сегмент", size=14, color=NEG,
                  anchor="start"))
    f.append(text(L + 8, yp(0.05), "гарячий сегмент: 21 цикл за той самий час",
                  size=13, color=POS, anchor="start"))

    render(os.path.join(OUT, 'cold-segment-lingers.svg'), W, H, *f)


def utilization_bimodality():
    """Розподіл заповненостей: жадібність — один горб, вигода/витрати — два."""
    W, H = 980, 460
    GREEDY = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
              0.004, 0.011, 0.019, 0.019, 0.047, 0.190, 0.169, 0.164,
              0.117, 0.111, 0.079, 0.068]
    COSTBEN = [0.000, 0.000, 0.005, 0.026, 0.031, 0.028, 0.018, 0.017,
               0.013, 0.012, 0.018, 0.018, 0.021, 0.024, 0.037, 0.071,
               0.134, 0.220, 0.160, 0.147]
    YMAX, BASE, TOPY = 0.24, 350, 100
    f = []

    def panel(x0, data, title, mean, note):
        w = 380.0
        bw = w / len(data)
        f.append(text(x0 + w / 2, 60, title, size=15, bold=True))
        f.append(line(x0, BASE, x0 + w + 8, BASE, sw=1.5))
        for i, v in enumerate(data):
            if v <= 0:
                continue
            h = v / YMAX * (BASE - TOPY)
            f.append(rect(x0 + i * bw + 1.5, BASE - h, bw - 3, h,
                          fill=BARF, stroke="none", sw=0, rx=2))
        for uu in (0.0, 0.5, 1.0):
            f.append(text(x0 + uu * w, BASE + 24, "%.1f" % uu, size=13,
                          color=MUTED))
        xm = x0 + mean * w
        f.append(line(xm, BASE, xm, TOPY + 6, color=INK, sw=1.6, dash="6,4"))
        f.append(text(xm + 10, TOPY + 24, "ū = %.3f" % mean, size=13,
                      anchor="start"))
        f.append(mtext(x0 + w / 2, BASE + 58, note, size=13, color=MUTED))

    panel(80, GREEDY, "жадібний вибір", 0.571,
          "один горб — усе скупчилося\nбіля спільного порога")
    panel(540, COSTBEN, "вигода на одиницю витрат", 0.435,
          "два горби — дешеві жертви ліворуч,\nнедоторкані холодні праворуч")
    f.append(text(496, BASE + 24, "u", size=13, color=MUTED))

    render(os.path.join(OUT, 'utilization-bimodality.svg'), W, H, *f)


inplace_vs_log()
imap_checkpoint()
segment_cleaning()
log_on_log()
argument_timeline()
what_was_measured()
write_cost_curve()
cold_segment_lingers()
utilization_bimodality()
print("ok")


def cleaner_liveness_walk():
    """Як прибирач із коду proj-segment-cleaner доводить, що блок живий:
    підсумковий блок → мапа блоків файлу → порівняння з власною адресою."""
    W, H = 1000, 560
    f = []
    cw, ch = 60, 60
    x0 = 90

    def strip(y, n, hi, hi_text, cells_text=None):
        for i in range(n):
            fill = HEAD if i == hi else DEAD
            f.append(rect(x0 + i * cw, y, cw, ch, fill=fill, rx=3))
            lab = hi_text if i == hi else (cells_text or "")
            if lab:
                f.append(text(x0 + i * cw + cw / 2, y + ch / 2 + 5, lab, size=11,
                              color=INK if i == hi else MUTED))

    f.append(text(430, 46, "перевірка живості блока в коді прибирача",
                  size=15, bold=True))

    # ── підсумковий блок сегмента-жертви ────────────────────────────────
    f.append(text(x0, 100, "сегмент-жертва v: підсумковий блок",
                  size=13, bold=True, anchor="start"))
    f.append(text(x0, 122, "для кожного слота — чий це блок",
                  size=12, color=MUTED, anchor="start"))
    strip(140, 8, 3, "17:5", "·")
    f.append(text(x0 + 3 * cw + cw / 2, 222, "слот 3", size=12, color=MUTED))

    # ── мапа блоків файлу ──────────────────────────────────────────────
    f.append(text(x0, 290, "inode[17]: адреса кожного зсуву файлу 17",
                  size=13, bold=True, anchor="start"))
    strip(310, 8, 5, "9027", "·")
    f.append(text(x0 + 5 * cw + cw / 2, 392, "зсув 5", size=12, color=MUTED))

    f.append(arrow(x0 + 3 * cw + cw / 2, 236, x0 + 5 * cw + cw / 2, 302,
                   color=FIELD, sw=2.0))
    f.append(text(x0 - 14, 272, "у слоті записано «файл 17, зсув 5» —",
                  size=12, color=FIELD, anchor="end"))
    f.append(text(x0 - 14, 292, "туди й дивимось", size=12, color=FIELD,
                  anchor="end"))

    # ── порівняння ─────────────────────────────────────────────────────
    body, bw, bh = textbox(700, 460,
                           "власна адреса слота\nv · 64 + 3 = 9027\n"
                           "у мапі теж 9027\nблок живий",
                           size=13, fill=LIVE, stroke=FIELD)
    f.append(body)
    f.append(arrow(x0 + 5 * cw + cw / 2, 406, 700 - bw / 2 - 12, 448,
                   color=FIELD, sw=2.0))

    f.append(mtext(x0 + 60, 470,
                   ["якби в мапі стояла інша адреса,",
                    "цей блок був би старою версією:",
                    "прибирач мовчки його викидає"],
                   size=12, color=MUTED, lh=1.45))

    render(os.path.join(OUT, 'cleaner-liveness-walk.svg'), W, H, *f)


cleaner_liveness_walk()
