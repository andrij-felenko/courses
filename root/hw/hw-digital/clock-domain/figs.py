# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def sq_wave(x0, y0, w, high, period_px, n, color=INK, sw=2.2):
    """Прямокутна хвиля: старт (x0,y0) — рівень 0; high — висота над 0."""
    top = y0 - high
    pts = []
    x = x0
    lvl = y0  # починаємо з низу
    pts.append((x, lvl))
    half = period_px / 2.0
    for _ in range(n * 2):
        # вертикальний фронт
        nlvl = top if lvl == y0 else y0
        pts.append((x, nlvl))
        lvl = nlvl
        x += half
        pts.append((x, lvl))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


# ── Фігура 1: частота ⇄ період ─────────────────────────────────────────────
def fig_freq_period():
    W, H = 720, 300
    x0, y0 = 70, 175
    high = 70
    period = 130
    frags = [sq_wave(x0, y0, 560, high, period, 4, color=INK)]
    # осьова лінія рівня 0
    frags.append(line(x0 - 10, y0, x0 + 540, y0, color=MUTED, sw=1, dash="4 4"))
    frags.append(text(x0 - 16, y0 + 4, "0", size=13, color=MUTED, anchor="end"))
    frags.append(text(x0 - 16, y0 - high + 4, "1", size=13, color=MUTED, anchor="end"))
    # позначка періоду T — між двома однаковими фронтами (наростання)
    xa = x0
    xb = x0 + period
    yT = y0 - high - 28
    frags.append(line(xa, y0 - high - 6, xa, yT - 6, color=FIELD, sw=1, dash="3 3"))
    frags.append(line(xb, y0 - high - 6, xb, yT - 6, color=FIELD, sw=1, dash="3 3"))
    frags.append(arrow(xa, yT, xb, yT, color=FIELD))
    frags.append(arrow(xb, yT, xa, yT, color=FIELD))
    frags.append(text((xa + xb) / 2, yT - 8, "період T", size=14, color=FIELD, bold=True))
    # підпис частоти
    b, bw, bh = textbox(600, 150, "частота\nf = 1 / T", size=15, bold=True,
                        fill="#eef7f0", stroke=FIELD, color=INK)
    frags.append(b)
    frags.append(text(W / 2, H - 18,
                      "Один повний цикл триває T секунд; за секунду їх f = 1/T штук.",
                      size=13, color=MUTED))
    render(os.path.join(IMG, 'freq-period.svg'), W, H, *frags,
           title="Частота — це скільки однакових тактів вкладається в секунду")


# ── Фігура 2: один кристал — три тактові домени ─────────────────────────────
def fig_domains_on_chip():
    W, H = 760, 380
    frags = [rect(30, 46, W - 60, H - 76, fill="#fbfbfd", stroke=INK, sw=2, rx=14)]
    frags.append(text(W / 2, 68, "кристал (один корпус)", size=13, color=MUTED))

    doms = [
        (60, 100, 200, 150, "ЯДРО", "600 МГц", NEG, "#eaf0fd"),
        (300, 100, 200, 150, "USB", "60 МГц", FIELD, "#eef7f0"),
        (540, 100, 170, 150, "РАДІО", "80 МГц", POS, "#fdecea"),
    ]
    centers = []
    for (x, y, w, h, name, rate, col, fillc) in doms:
        frags.append(rect(x, y, w, h, fill=fillc, stroke=col, sw=2.2, rx=10))
        frags.append(text(x + w / 2, y + 30, name, size=16, color=col, bold=True))
        frags.append(text(x + w / 2, y + 54, rate, size=15, color=INK, bold=True))
        # символ окремого джерела такту
        frags.append(circle(x + w / 2, y + 95, 20, fill=BG, stroke=col, sw=2))
        frags.append(sq_wave(x + w / 2 - 13, y + 100, 26, 12,
                             13 if col == NEG else (20 if col == FIELD else 16),
                             2, color=col, sw=1.6))
        frags.append(text(x + w / 2, y + 132, "свій такт", size=11, color=MUTED))
        centers.append((x + w / 2, y + h))

    # межі між доменами — стрілки «перетин» через синхронізатор
    y_line = 300
    for (cx, cy), (nx, _) in zip(centers[:-1], centers[1:]):
        midx = (cx + nx) / 2
        frags.append(line(cx, cy, cx, y_line, color=MUTED, sw=1.4, dash="4 4"))
    # підпис межі
    b, bw, bh = textbox(W / 2, 330,
                        "межа доменів — сигнал тут не «псується», а РОЗ'ЇЖДЖАЄТЬСЯ в часі",
                        size=13, fill="#fff6e6", stroke="#c98a00", color=INK)
    frags.append(b)
    render(os.path.join(IMG, 'domains-on-chip.svg'), W, H, *frags,
           title="Один кристал — кілька тактових доменів, у кожного свій ритм")


# ── Фігура 3: два такти розходяться (тому 100 і 59 МГц — різні домени) ───────
def fig_drift():
    W, H = 720, 320
    xa, yb = 80, 130
    frags = []
    frags.append(text(60, yb - 62, "A: 100 МГц", size=14, color=NEG, bold=True, anchor="start"))
    frags.append(text(60, yb + 78, "B: 59 МГц", size=14, color=POS, bold=True, anchor="start"))
    # хвиля A — коротший період
    frags.append(sq_wave(xa, yb, 580, 46, 58, 10, color=NEG, sw=2))
    # хвиля B — довший період, старт синхронно
    frags.append(sq_wave(xa, yb + 140, 580, 46, 98, 6, color=POS, sw=2))
    # вертикальна лінія «спочатку разом»
    frags.append(line(xa, yb - 52, xa, yb + 150, color=FIELD, sw=1.4, dash="5 4"))
    frags.append(text(xa, yb - 60, "старт разом", size=12, color=FIELD, anchor="middle"))
    # де вони «розійшлися»
    xd = xa + 470
    frags.append(line(xd, yb - 52, xd, yb + 150, color="#c98a00", sw=1.4, dash="5 4"))
    frags.append(text(xd, yb - 60, "фронти вже врозбіг", size=12, color="#c98a00"))
    frags.append(text(W / 2, H - 16,
                      "Фаза між ними повзе весь час — спільної миті «оба стабільні» немає. Це два домени.",
                      size=13, color=MUTED))
    render(os.path.join(IMG, 'drift.svg'), W, H, *frags,
           title="Два такти без спільного кратного розходяться в часі")


# ── Фігура 4 (hist): cycling unit роздає такт усім акумуляторам ──────────────
def fig_eniac_fanout():
    W, H = 760, 420
    frags = []
    # джерело: кварцовий генератор 100 кГц
    ox, oy = 90, 120
    frags.append(rect(ox, oy, 150, 74, fill="#eef7f0", stroke=FIELD, sw=2.2, rx=10))
    frags.append(text(ox + 75, oy + 26, "генератор", size=14, color=INK, bold=True))
    frags.append(text(ox + 75, oy + 50, "100 кГц", size=15, color=FIELD, bold=True))
    # cycling unit
    cx, cy = 300, 108
    frags.append(rect(cx, cy, 170, 98, fill="#eef2ff", stroke=NEG, sw=2.4, rx=12))
    frags.append(text(cx + 85, cy + 28, "cycling unit", size=15, color=NEG, bold=True))
    frags.append(text(cx + 85, cy + 50, "«циклувальний", size=12, color=MUTED))
    frags.append(text(cx + 85, cy + 66, "вузол»", size=12, color=MUTED))
    frags.append(text(cx + 85, cy + 88, "10P 9P 4P 2P 1P …", size=12, color=INK, bold=True))
    frags.append(arrow(ox + 150, oy + 37, cx, cy + 49, color=INK))

    # шина такту вниз і віяло до акумуляторів
    busx = cx + 85
    busy = cy + 98
    frags.append(line(busx, busy, busx, 250, color=NEG, sw=2.4))
    frags.append(text(busx + 8, 232, "спільна шина імпульсів", size=12, color=NEG, anchor="start"))

    accs = [(90, 300), (230, 300), (370, 300), (510, 300), (650, 300)]
    labels = ["акум. 1", "акум. 2", "акум. 3", "…", "акум. 20"]
    for (ax, ay), lb in zip(accs, labels):
        col = MUTED if lb == "…" else INK
        if lb != "…":
            frags.append(rect(ax, ay, 90, 66, fill=FILL, stroke=col, sw=1.8, rx=8))
            frags.append(text(ax + 45, ay + 24, lb, size=12, color=INK, bold=True))
            frags.append(text(ax + 45, ay + 46, "10 кілець", size=11, color=MUTED))
            # маленька хвиля-«клац»
            frags.append(sq_wave(ax + 18, ay + 60, 54, 8, 18, 2, color=FIELD, sw=1.3))
        else:
            frags.append(text(ax + 45, ay + 40, "…", size=22, color=MUTED, bold=True))
        # відгалуження від шини
        frags.append(line(busx, 250, ax + 45, 250, color=NEG, sw=1.3))
        frags.append(arrow(ax + 45, 250, ax + 45, ay, color=NEG, sw=1.6))

    b, bw, bh = textbox(W / 2, 400,
                        "один ритм на всіх — акумулятори клацають РАЗОМ, а не хто коли",
                        size=13, fill="#fff6e6", stroke="#c98a00", color=INK)
    frags.append(b)
    render(os.path.join(IMG, 'eniac-fanout.svg'), W, H, *frags,
           title="ENIAC: cycling unit роздає єдиний такт усім 20 акумуляторам")


# ── Фігура 5 (hist): багатофазний потік у межах однієї addition time ─────────
def fig_eniac_pulsetrain():
    W, H = 760, 360
    frags = []
    x0 = 150
    span = 560          # 20 позицій такту
    n = 20
    step = span / n
    y_top = 70

    # рамка «одна addition time = 20 тактів = 200 мкс»
    frags.append(line(x0, y_top - 14, x0 + span, y_top - 14, color="#c98a00", sw=1.4))
    frags.append(line(x0, y_top - 20, x0, y_top - 8, color="#c98a00", sw=1.4))
    frags.append(line(x0 + span, y_top - 20, x0 + span, y_top - 8, color="#c98a00", sw=1.4))
    frags.append(text(x0 + span / 2, y_top - 22,
                      "одна addition time = 20 тактів по 10 мкс = 200 мкс",
                      size=13, color="#c98a00", bold=True))

    # сітка позицій такту
    for i in range(n + 1):
        gx = x0 + i * step
        frags.append(line(gx, y_top, gx, 300, color="#e3e6ea", sw=1))

    def pulses(y, positions, color, label):
        frags.append(text(x0 - 12, y + 4, label, size=13, color=color, bold=True, anchor="end"))
        frags.append(line(x0, y, x0 + span, y, color=MUTED, sw=1))
        for p in positions:
            gx = x0 + p * step + step / 2
            frags.append(line(gx, y, gx, y - 22, color=color, sw=2.4))
            frags.append(line(gx, y - 22, gx + step * 0.45, y - 22, color=color, sw=2.4))
            frags.append(line(gx + step * 0.45, y - 22, gx + step * 0.45, y, color=color, sw=2.4))

    # 10P — десять поспіль (жене кільце на 9 кроків + скид)
    pulses(120, list(range(0, 10)), NEG, "10P")
    # 1P — один імпульс (одиничний крок)
    pulses(180, [1], FIELD, "1P")
    # 4P — чотири (додати 4)
    pulses(240, [1, 2, 3, 4], POS, "4P")
    # CPP — керівний, наприкінці циклу
    pulses(300, [19], INK, "CPP")

    frags.append(text(W / 2, H - 20,
                      "Різні лінії — різні «фази» одного ритму: скільки саме імпульсів прийшло, стільки крокнуло кільце.",
                      size=13, color=MUTED))
    render(os.path.join(IMG, 'eniac-pulsetrain.svg'), W, H, *frags,
           title="Багатофазний потік cycling unit за один машинний цикл")


if __name__ == "__main__":
    fig_freq_period()
    fig_domains_on_chip()
    fig_drift()
    fig_eniac_fanout()
    fig_eniac_pulsetrain()
    print("figs done")
