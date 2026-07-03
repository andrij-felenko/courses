# -*- coding: utf-8 -*-
"""Фігури до теми «Тяга проти ваги».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

UP   = "#c0392b"   # тяга вгору — гаряча
DOWN = "#2457d6"   # вага вниз — холодна


def craft(cx, cy, w=64, h=16):
    """Простий силует апарата: корпус + дві «руки» з гвинтами."""
    out = rect(cx - w / 2, cy - h / 2, w, h, fill="#e8edf3", stroke=LINE, sw=1.6, rx=5)
    # лопаті-гвинти по краях
    for sx in (cx - w / 2, cx + w / 2):
        out += line(sx - 12, cy - h / 2 - 3, sx + 12, cy - h / 2 - 3, color=LINE, sw=3)
    return out


# ── Фігура 1: три режими за співвідношенням тяги й ваги ──────────────────────
def fig_three_regimes():
    W, H = 760, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Тяга проти ваги: три результати поєдинку", size=17, bold=True))

    col_w = W / 3
    cxs = [col_w * 0.5, col_w * 1.5, col_w * 2.5]
    titles = ["T = W", "T > W", "T < W"]
    subs   = ["рівновага — завис", "прискорення вгору", "тягне вниз"]
    # довжини стрілок (px) для тяги/ваги в кожній сцені
    tlens  = [70, 96, 52]
    wlens  = [70, 70, 70]
    acol   = [MUTED, UP, DOWN]     # колір підсумку
    averd  = ["a = 0", "a > 0", "a < 0"]

    yc = 180                        # рівень апарата
    for i, cx in enumerate(cxs):
        if i > 0:
            xs = col_w * i
            f.append(line(xs, 54, xs, H - 20, color="#dfe4ea", sw=1.2, dash="4,6"))
        f.append(text(cx, 62, titles[i], size=16, bold=True, color=acol[i]))
        # апарат
        f.append(craft(cx, yc))
        # стрілка тяги — вгору від апарата
        f.append(arrow(cx, yc - 10, cx, yc - 10 - tlens[i], color=UP, sw=3.2))
        f.append(text(cx + 12, yc - 10 - tlens[i] + 4, "T", size=15, bold=True,
                      color=UP, anchor="start"))
        # стрілка ваги — вниз від апарата
        f.append(arrow(cx, yc + 10, cx, yc + 10 + wlens[i], color=DOWN, sw=3.2))
        f.append(text(cx + 12, yc + 10 + wlens[i] - 2, "W", size=15, bold=True,
                      color=DOWN, anchor="start"))
        # підсумок унизу
        b, bw, bh = textbox(cx, H - 34, averd[i] + "\n" + subs[i], size=12, pad=8,
                            fill=FILL, stroke=acol[i], sw=1.4, bold=False)
        f.append(b)

    return render(os.path.join(IMG, "three-regimes.svg"), W, H, *f)


# ── Фігура 2: тяга як віддача відкинутого повітря ───────────────────────────
def fig_thrust_reaction():
    W, H = 560, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Тяга — віддача відкинутого повітря", size=17, bold=True))

    cx = W / 2
    yc = 150                         # рівень гвинта

    # стовп захопленого повітря (згори) — легкий блакитний прямокутник
    f.append(rect(cx - 52, 58, 104, yc - 70, fill="#eef4fb", stroke="#cdd8e6",
                  sw=1.2, rx=6))
    f.append(text(cx, 78, "повітря згори", size=12, color=MUTED))
    # маленькі стрілки входу повітря
    for dx in (-30, 0, 30):
        f.append(arrow(cx + dx, 92, cx + dx, yc - 34, color="#9fb2c8", sw=1.6))

    # апарат із гвинтом
    f.append(craft(cx, yc, w=120, h=18))
    f.append(text(cx, yc - 22, "гвинт", size=12, color=INK))

    # тяга вгору (віддача) — велика червона стрілка
    f.append(arrow(cx, yc - 30, cx, 92, color=UP, sw=3.4))
    f.append(text(cx + 14, 108, "T (тяга, вгору)", size=14, bold=True, color=UP,
                  anchor="start"))

    # струмінь униз — розганяється (стрілки довшають)
    ys = yc + 22
    for k, dx in enumerate((-34, 0, 34)):
        f.append(arrow(cx + dx, ys, cx + dx, ys + 150, color=DOWN, sw=2.6))
    f.append(text(cx, ys + 174, "повітря відкинуте вниз зі швидкістю v", size=13,
                  color=DOWN))

    # формула збоку
    b, bw, bh = textbox(cx, H - 26, "T = ṁ · v   (маса за секунду × швидкість)",
                        size=14, pad=9, fill="#fdecea", stroke=UP, sw=1.4, bold=True)
    f.append(b)
    f.append(mtext(cx, ys + 92, "3-й закон Ньютона:\nвниз штовхнув повітря —\nвгору штовхнуло гвинт",
                   size=11, color=MUTED))
    return render(os.path.join(IMG, "thrust-reaction.svg"), W, H, *f)


# ── Фігура 3: струмна трубка крізь ідеальний диск (v∞ = 2·v_i) ───────────────
def fig_streamtube():
    W, H = 780, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Струмна трубка крізь диск: далеко вниз швидкість удвічі більша",
                  size=16, bold=True))

    xd = 300                       # x диска
    ytop, ybot = 70, 360           # межі поля потоку
    ymid = (ytop + ybot) / 2

    # профіль трубки: широка вгорі (спокій), звужена внизу (розгін)
    # верхній контур
    r_far_up = 116                 # півширина далеко вгорі
    r_disk   = 92                  # півширина на диску
    r_far_dn = 66                  # півширина далеко вниз (звужена)
    xL, xR = 70, W - 40
    # верхня стінка трубки
    f.append('<path d="M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d" '
             'fill="none" stroke="%s" stroke-width="2"/>' % (
                 xL, ymid - r_far_up, xd - 90, ymid - r_far_up, xd - 40, ymid - r_disk, xd, ymid - r_disk,
                 xd + 60, ymid - r_disk, xR - 120, ymid - r_far_dn, xR, ymid - r_far_dn, LINE))
    # нижня стінка трубки (дзеркально)
    f.append('<path d="M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d" '
             'fill="none" stroke="%s" stroke-width="2"/>' % (
                 xL, ymid + r_far_up, xd - 90, ymid + r_far_up, xd - 40, ymid + r_disk, xd, ymid + r_disk,
                 xd + 60, ymid + r_disk, xR - 120, ymid + r_far_dn, xR, ymid + r_far_dn, LINE))

    # диск (товста вертикальна лінія на xd)
    f.append(line(xd, ymid - r_disk, xd, ymid + r_disk, color=POS, sw=5))
    f.append(text(xd, ymid - r_disk - 10, "диск A", size=13, bold=True, color=POS))

    # три перерізи зі стрілками швидкості (довжина = швидкість)
    # далеко вгорі: спокій (крихітна стрілка)
    f.append(text(xL + 46, ymid - r_far_up - 12, "далеко вгорі", size=12, color=MUTED))
    f.append(arrow(xL + 46, ymid - 8, xL + 46, ymid + 8, color=NEG, sw=2.2))
    f.append(text(xL + 46, ymid + 34, "v ≈ 0", size=12, bold=True, color=NEG))

    # на диску: v_i
    f.append(arrow(xd, ymid + 20, xd, ymid + 20 + 40, color=NEG, sw=3))
    f.append(text(xd + 40, ymid + 46, "v_i", size=14, bold=True, color=NEG, anchor="start"))

    # далеко вниз: 2·v_i (стрілка вдвічі довша)
    xdn = xR - 40
    f.append(text(xdn, ymid - r_far_dn - 12, "далеко вниз", size=12, color=MUTED))
    f.append(arrow(xdn, ymid - 40, xdn, ymid - 40 + 80, color=NEG, sw=3))
    f.append(text(xdn - 8, ymid + 4, "2·v_i", size=14, bold=True, color=NEG, anchor="end"))

    # підпис-висновок унизу
    b, bw, bh = textbox(W / 2, H - 22,
                        "маса стала (ρ·A·v) → швидкість ×2 ⟹ переріз ×½ : трубка звужується",
                        size=12, pad=8, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "streamtube.svg"), W, H, *f)


# ── Фігура 4: потужність зависання росте як T^1.5 і падає з площею диска ─────
def fig_power_law():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Ідеальна потужність зависання: P ∝ T^1.5 / √A", size=16, bold=True))

    # осі
    ox, oy = 90, 320               # початок координат
    ax, ay = 700, 70               # кінці осей
    f.append(arrow(ox, oy, ax, oy, color=INK, sw=1.8))       # вісь площі A →
    f.append(arrow(ox, oy, ox, ay, color=INK, sw=1.8))       # вісь потужності P ↑
    f.append(text(ax - 4, oy + 24, "площа диска A →", size=12, color=INK, anchor="end"))
    f.append(text(ox - 12, ay + 4, "P", size=13, bold=True, color=INK, anchor="end"))

    # крива P ∝ 1/√A для сталої тяги: спадна, крута зліва
    import math
    pts = []
    A0, span = 0.25, 6.0
    for i in range(0, 101):
        A = A0 + span * i / 100.0
        P = 1.0 / math.sqrt(A)
        px = ox + (ax - ox - 10) * (A - A0) / span
        py = oy - (oy - ay - 10) * (P - 1.0 / math.sqrt(A0 + span)) / (1.0 / math.sqrt(A0) - 1.0 / math.sqrt(A0 + span))
        pts.append((px, py))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, FIELD))
    f.append(text(pts[10][0] + 118, pts[10][1] + 6, "стала тяга T: P ∝ 1/√A", size=13,
                  bold=True, color=FIELD, anchor="start"))

    # дві точки: вузький диск (дорого) і широкий (дешево)
    xn, xw = pts[8], pts[70]
    f.append(circle(xn[0], xn[1], 5, fill=POS, stroke=POS, sw=1))
    f.append(mtext(xn[0] + 12, xn[1] - 12, ["вузький гвинт:", "мала A → велика P"],
                   size=11, color=POS, anchor="start"))
    f.append(circle(xw[0], xw[1], 5, fill=NEG, stroke=NEG, sw=1))
    f.append(mtext(xw[0] + 10, xw[1] - 26, ["широкий гвинт:", "велика A → мала P"],
                   size=11, color=NEG, anchor="start"))

    # формула-плашка
    b, bw, bh = textbox(W / 2, H - 20,
                        "P = √( T³ / (2·ρ·A) )   — удвічі ширший ротор → потужність ÷√2",
                        size=13, pad=9, fill="#eafaf1", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "power-law.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_three_regimes()
    p2 = fig_thrust_reaction()
    p3 = fig_streamtube()
    p4 = fig_power_law()
    print("written:")
    for p in (p1, p2, p3, p4):
        print("  ", p)
