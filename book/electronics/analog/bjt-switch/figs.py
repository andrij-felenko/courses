# -*- coding: utf-8 -*-
"""Фігури до вставок теми «BJT як ключ».
Покриває п'ять фігур, на які посилаються вставки:
  comp-high-side-pnp.md →  low-vs-high.svg, pnp-driver.svg
  math-base-resistor.md →  two-points.svg, forced-beta.svg, derive.svg
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні примітиви схем (символи елементів) ─────────────────────────────
def gnd(cx, y, label="GND"):
    """Символ землі: три горизонтальні штрихи, що звужуються."""
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8)]
    out.append(line(cx - 14, y + 7, cx + 14, y + 7, color=INK, sw=2.4))
    out.append(line(cx - 8, y + 12, cx + 8, y + 12, color=INK, sw=2.0))
    out.append(line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8))
    if label:
        out.append(text(cx, y + 33, label, size=11, color=INK, bold=True))
    return "".join(out)


def res_v(cx, cy, h=40, label=None, lab_side="right"):
    """Вертикальний резистор-прямокутник із центром (cx,cy); повертає (svg, y_top, y_bot)."""
    w = 16
    yt, yb = cy - h / 2, cy + h / 2
    out = [rect(cx - w / 2, yt, w, h, fill="#ffffff", stroke=INK, sw=1.6, rx=2)]
    if label:
        if lab_side == "right":
            out.append(text(cx + w / 2 + 6, cy + 4, label, size=12, color=INK, anchor="start"))
        else:
            out.append(text(cx - w / 2 - 6, cy + 4, label, size=12, color=INK, anchor="end"))
    return "".join(out), yt, yb


def res_h(cx, cy, w=40, label=None):
    """Горизонтальний резистор; повертає (svg, x_left, x_right)."""
    h = 16
    xl, xr = cx - w / 2, cx + w / 2
    out = [rect(xl, cy - h / 2, w, h, fill="#ffffff", stroke=INK, sw=1.6, rx=2)]
    if label:
        out.append(text(cx, cy - h / 2 - 6, label, size=12, color=INK))
    return "".join(out), xl, xr


class Tr:
    """Координати виводів намальованого транзистора (для приєднання дротів)."""
    __slots__ = ("svg", "xb", "xc", "yc", "ye", "yb")
    def __init__(self, svg, xb, xc, yc, ye, yb):
        self.svg, self.xb, self.xc, self.yc, self.ye, self.yb = svg, xb, xc, yc, ye, yb


def npn(cx, cy, label=None, lab_anchor="start", lab_dx=30):
    """Символ NPN: вертикальна планка бази (зліва вивід), колектор угору-праворуч,
    емітер униз-праворуч зі стрілкою назовні. Повертає Tr(svg, xb, xc, yc, ye, yb):
    xb — x виводу бази (ліворуч), xc — x спільної колектор/емітер-осі,
    yc/ye — кінці колекторного/емітерного виводів, yb — y виводу бази."""
    out = []
    bt, bb = cy - 28, cy + 28           # планка бази
    out.append(line(cx, bt, cx, bb, color=INK, sw=3))
    out.append(line(cx - 30, cy, cx, cy, color=INK, sw=2))      # вивід бази
    cx2 = cx + 30
    # колектор (угору-праворуч)
    out.append(line(cx, bt + 9, cx2, bt - 10, color=INK, sw=2))
    yC = bt - 34
    out.append(line(cx2, bt - 10, cx2, yC, color=INK, sw=2))
    # емітер зі стрілкою назовні (вниз-праворуч)
    out.append(line(cx, bb - 9, cx2, bb + 10, color=INK, sw=2))
    yE = bb + 34
    out.append(line(cx2, bb + 10, cx2, yE, color=INK, sw=2))
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        cx + 18, bb + 3, cx2, bb + 11, cx + 16, bb + 12, INK))
    if label:
        ax = cx2 + lab_dx if lab_anchor == "start" else cx - 36
        out.append(text(ax, cy + 4, label, size=12, color=INK, bold=True, anchor=lab_anchor))
    return Tr("".join(out), cx - 30, cx2, yC, yE, cy)


def pnp(cx, cy, label=None, lab_anchor="start", lab_dx=30):
    """Символ PNP: планка бази, емітер угору-праворуч зі стрілкою ВСЕРЕДИНУ (до бази),
    колектор униз-праворуч. Повертає Tr(svg, xb, xc, yc, ye, yb), де yc — кінець
    КОЛЕКТОРНОГО виводу (унизу), ye — кінець ЕМІТЕРНОГО (угорі)."""
    out = []
    bt, bb = cy - 28, cy + 28
    out.append(line(cx, bt, cx, bb, color=INK, sw=3))
    out.append(line(cx - 30, cy, cx, cy, color=INK, sw=2))      # вивід бази
    cx2 = cx + 30
    # емітер угорі зі стрілкою ВСЕРЕДИНУ (вказує на планку бази)
    out.append(line(cx, bt + 9, cx2, bt - 10, color=INK, sw=2))
    yE = bt - 34
    out.append(line(cx2, bt - 10, cx2, yE, color=INK, sw=2))
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        cx2 - 2, bt - 10, cx + 16, bt + 1, cx + 17, bt + 12, INK))
    # колектор унизу
    out.append(line(cx, bb - 9, cx2, bb + 10, color=INK, sw=2))
    yC = bb + 34
    out.append(line(cx2, bb + 10, cx2, yC, color=INK, sw=2))
    if label:
        ax = cx2 + lab_dx if lab_anchor == "start" else cx - 36
        out.append(text(ax, cy + 4, label, size=12, color=INK, bold=True, anchor=lab_anchor))
    return Tr("".join(out), cx - 30, cx2, yC, yE, cy)


def load_box(cx, cy, w=46, h=34, label="навант."):
    out = [rect(cx - w / 2, cy - h / 2, w, h, fill="#ffffff", stroke=INK, sw=1.8, rx=3)]
    out.append(text(cx, cy + 4, label, size=11, color=INK))
    return "".join(out)


def dot(cx, cy):
    return '<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s"/>' % (cx, cy, INK)


def rail(x1, x2, y, color, label, lab_side="start"):
    out = [line(x1, y, x2, y, color=color, sw=2.4)]
    if lab_side == "start":
        out.append(text(x1 - 8, y + 4, label, size=12, color=color, bold=True, anchor="end"))
    else:
        out.append(text(x2 + 8, y + 4, label, size=12, color=color, bold=True, anchor="start"))
    return "".join(out)


# ── Фігура 1: low-vs-high.svg (нижнє плече NPN ↔ верхнє плече PNP) ───────────
def fig_low_vs_high():
    W, H = 860, 430
    f = [text(W / 2, 30, "Нижнє плече проти верхнього — і чому PNP не слухає МК прямо",
              size=16, bold=True)]

    # ── ліва панель: low-side NPN ──
    pL_x, pL_y, pL_w, pL_h = 30, 56, 390, 344
    f.append(rect(pL_x, pL_y, pL_w, pL_h, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
    f.append(text(pL_x + pL_w / 2, pL_y + 24, "low-side (NPN): розриває «мінус»", size=13, bold=True))

    topY, botY = pL_y + 50, pL_y + pL_h - 30
    t = npn(pL_x + pL_w / 2, pL_y + 230, "NPN")     # спершу транзистор → знаємо вісь xc
    Sx = t.xc                                        # вертикальна спина (колектор/емітер)
    f.append(rail(pL_x + 40, pL_x + pL_w - 40, topY, POS, "+V"))
    # навантаження на спині, між +V і колектором
    f.append(line(Sx, topY, Sx, topY + 17, color=INK, sw=2))
    f.append(load_box(Sx, topY + 34))
    f.append(line(Sx, topY + 51, Sx, t.yc, color=INK, sw=2))     # навантаж → колектор
    f.append(t.svg)
    # емітер → земля
    f.append(line(Sx, t.ye, Sx, botY, color=INK, sw=2))
    f.append(gnd(Sx, botY))
    # база ← МК через резистор (на висоті виводу бази)
    rs, rl, rr = res_h(t.xb - 44, t.yb, 38, "Rб")
    f.append(rs)
    f.append(line(rr, t.yb, t.xb, t.yb, color=INK, sw=2))
    f.append(line(pL_x + 34, t.yb, rl, t.yb, color=FIELD, sw=2))
    f.append(text(pL_x + 30, t.yb + 4, "МК", size=12, color=FIELD, bold=True, anchor="end"))
    # підпис проблеми
    f.append(text(pL_x + pL_w / 2, botY + 2, "вимкнене навантаження ще під +V!",
                  size=11, color=POS, bold=True))

    # ── права панель: high-side PNP ──
    pR_x = 440
    f.append(rect(pR_x, pL_y, pL_w, pL_h, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
    f.append(text(pR_x + pL_w / 2, pL_y + 24, "high-side (PNP): розриває «плюс»", size=13, bold=True))

    tp = pnp(pR_x + pL_w / 2 + 20, topY + 70, "PNP")    # емітер угорі (ye), колектор унизу (yc)
    Sx = tp.xc
    f.append(rail(pR_x + 40, pR_x + pL_w - 40, topY, POS, "+12 В"))
    f.append(line(Sx, topY, Sx, tp.ye, color=INK, sw=2))     # емітер → +V
    f.append(dot(Sx, topY))
    f.append(tp.svg)
    # колектор → навантаження → земля
    f.append(line(Sx, tp.yc, Sx, tp.yc + 17, color=INK, sw=2))
    f.append(load_box(Sx, tp.yc + 34))
    f.append(line(Sx, tp.yc + 51, Sx, botY, color=INK, sw=2))
    f.append(gnd(Sx, botY))
    # база «?» ліворуч пунктиром
    f.append(line(tp.xb, tp.yb, pR_x + 40, tp.yb, color=NEG, sw=2, dash="5,3"))
    f.append(text(pR_x + 36, tp.yb + 4, "база?", size=12, color=NEG, bold=True, anchor="end"))
    # підпис проблеми (двома рядками через fitbox у нижній смузі панелі)
    f.append(fitbox(pR_x + 30, botY - 36, pL_w - 60, 32,
                    "щоб ЗАКРИТИ PNP, базу треба підняти до +12 В,\nа МК дає лише 0–3.3 В → прямо не може",
                    size=11, fill="#fdecea", stroke=POS, color="#9a2b22"))

    render(os.path.join(IMG, "low-vs-high.svg"), W, H, *f)


# ── Фігура 2: pnp-driver.svg (NPN-перекладач для PNP) ───────────────────────
def fig_pnp_driver():
    W, H = 860, 440
    f = [text(W / 2, 30, "Розв'язок: маленький NPN «перекладає рівень» для PNP",
              size=16, bold=True)]

    topY, botY = 78, 360
    f.append(rail(140, 600, topY, POS, "+12 В"))
    f.append(line(140, botY, 600, botY, color=INK, sw=2))
    f.append(text(132, botY + 4, "GND", size=12, color=INK, bold=True, anchor="end"))

    # ── силовий PNP праворуч-угорі (емітер ye угорі, колектор yc унизу) ──
    tp = pnp(470, 150, "PNP (силовий ключ)")
    f.append(line(tp.xc, topY, tp.xc, tp.ye, color=INK, sw=2))   # емітер → +12
    f.append(dot(tp.xc, topY))
    f.append(tp.svg)
    # колектор → навантаження → земля
    f.append(line(tp.xc, tp.yc, tp.xc, tp.yc + 14, color=INK, sw=2))
    f.append(load_box(tp.xc, tp.yc + 38, label="навантаження"))
    f.append(line(tp.xc, tp.yc + 55, tp.xc, botY, color=INK, sw=2))
    f.append(dot(tp.xc, botY))

    baseY = tp.yb                              # рівень бази PNP — спільний дріт перекладача
    # ── підтягувальний резистор бази PNP до +12 ──
    pull_x = tp.xb - 70
    rs, ryt, ryb = res_v(pull_x, (topY + baseY) / 2, 40, "Rпідт", "left")
    f.append(rs)
    f.append(line(pull_x, topY, pull_x, ryt, color=INK, sw=2))
    f.append(dot(pull_x, topY))
    f.append(line(pull_x, ryb, pull_x, baseY, color=INK, sw=2))
    f.append(line(tp.xb, baseY, pull_x, baseY, color=INK, sw=2))
    f.append(dot(pull_x, baseY))

    # ── маленький NPN, що стягує базу PNP ──
    tn = npn(250, 240, "NPN (керує МК)")
    # колектор NPN ↔ база PNP: спільний горизонтальний дріт на рівні baseY
    f.append(line(pull_x, baseY, tn.xc, baseY, color=INK, sw=2))
    f.append(line(tn.xc, baseY, tn.xc, tn.yc, color=INK, sw=2))
    # емітер NPN → земля
    f.append(line(tn.xc, tn.ye, tn.xc, botY, color=INK, sw=2))
    f.append(dot(tn.xc, botY))
    # база NPN ← МК через Rб
    rs, rl, rr = res_h(tn.xb - 48, tn.yb, 40, "Rб")
    f.append(rs)
    f.append(line(rr, tn.yb, tn.xb, tn.yb, color=INK, sw=2))
    f.append(line(162, tn.yb, rl, tn.yb, color=FIELD, sw=2))
    f.append(text(158, tn.yb + 4, "МК", size=12, color=FIELD, bold=True, anchor="end"))

    # ── панель-легенда праворуч ──
    lx, ly, lw, lh = 620, 78, 220, 282
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
    f.append(text(lx + lw / 2, ly + 22, "логіка", size=13, bold=True))
    f.append(fitbox(lx + 12, ly + 34, lw - 24, 56,
                    "МК = 1:\nNPN відкритий → стягує базу PNP\nвниз → PNP ВВІМКНЕНО",
                    size=11, fill="#eef6ef", stroke=FIELD, color=INK))
    f.append(fitbox(lx + 12, ly + 98, lw - 24, 56,
                    "МК = 0:\nNPN закритий → Rпідт тримає базу\nPNP на +12 → PNP ВИМКНЕНО",
                    size=11, fill="#f4f6f8", stroke=MUTED, color=INK))
    f.append(fitbox(lx + 12, ly + 162, lw - 24, 40,
                    "логіка НЕ інвертована:\n1 вмикає, 0 вимикає",
                    size=11, fill="#f0ecf6", stroke="#7a4e8a", color=INK))
    f.append(fitbox(lx + 12, ly + 210, lw - 24, 40,
                    "два транзистори — бо рівні\nнапруг не збігаються",
                    size=11, fill="#f4f6f8", stroke=MUTED, color=MUTED))

    f.append(text(W / 2, 422, "NPN керується від землі (МК уміє), а вже він стягує високовольтну базу PNP.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "pnp-driver.svg"), W, H, *f)


# ── Фігура 3: two-points.svg (дві робочі точки на лінії навантаження) ───────
def fig_two_points():
    W, H = 860, 410
    f = [text(W / 2, 30, "Чому в ключі НЕ беруть паспортне β: дві робочі точки", size=16, bold=True)]

    # осі
    ox, oy = 100, 330           # початок координат
    ax_r, ax_t = 700, 80
    f.append(line(ox, oy, ax_r, oy, color=INK, sw=1.6))
    f.append(text(ax_r + 18, oy + 4, "Vce", size=12, color=INK, bold=True, anchor="middle"))
    f.append(line(ox, oy, ox, ax_t, color=INK, sw=1.6))
    f.append(text(ox - 8, ax_t - 8, "Ic", size=12, color=INK, bold=True))

    # три криві Ib (вихідні характеристики): різке коліно + майже плаский рівень
    def curve(plateau_y, col, sw=1.8):
        pts = []
        for i in range(0, 121):
            x = ox + i * 5
            t = i / 12.0
            # експоненційне наближення до плато (коліно насичення)
            y = oy - (oy - plateau_y) * (1 - math.exp(-t))
            pts.append("%.1f,%.1f" % (x, y))
        return '<path d="M %s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (
            " L ".join(pts), col, sw)

    f.append(curve(236, "#e0e0e0"))      # малий Ib
    f.append(curve(176, "#cccccc"))      # середній Ib
    f.append(curve(120, "#bdbdbd"))      # великий Ib (Ib=Ic/10)

    # лінія навантаження: від (Vce=0, Ic_max) до (Vce=Vcc, 0)
    lx1, ly1 = ox, 128
    lx2, ly2 = 650, oy
    f.append(line(lx1, ly1, lx2, ly2, color="#b5732e", sw=2, dash="6,4"))
    f.append(text(470, 280, "лінія навантаження", size=12, color="#b5732e", bold=True, anchor="start"))

    # точка A: на межі (перетин лінії навантаження з «паспортною» кривою, високо/праворуч)
    ax_, ay_ = 300, 168
    f.append('<circle cx="%.1f" cy="%.1f" r="6.5" fill="none" stroke="%s" stroke-width="2.6"/>' % (ax_, ay_, POS))
    f.append(text(ax_ + 12, ay_ - 6, "A: Ib = Ic/β(паспорт)", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(ax_ + 12, ay_ + 11, "Vce велике → гріється", size=11, color="#9a2b22", anchor="start"))

    # точка B: глибоко в насиченні (коліно, ліворуч біля осі Ic)
    bx_, by_ = 132, 134
    f.append('<circle cx="%.1f" cy="%.1f" r="6.5" fill="%s" stroke="%s" stroke-width="0"/>' % (bx_, by_, FIELD, FIELD))
    f.append(text(bx_ + 14, by_ - 4, "B: Ib = Ic/10", size=12, color="#1f6e33", bold=True, anchor="start"))
    f.append(text(bx_ + 14, by_ + 13, "Vce(sat) ≈ 0.2 В → насичено", size=11, color="#1f6e33", anchor="start"))

    f.append(text(W / 2, 392, "Паспортне β виводить транзистор лише НА МЕЖУ насичення; для надійного «ввімкнено» базі дають надлишок.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "two-points.svg"), W, H, *f)


# ── Фігура 4: forced-beta.svg (компроміс вибору β_forced) ───────────────────
def fig_forced_beta():
    W, H = 840, 360
    f = [text(W / 2, 30, "Примусове β: компроміс між теплом і швидкістю", size=16, bold=True)]
    f.append(text(W / 2, 52, "β_forced = Ic / Ib — навмисно беруть набагато меншим за паспортне β",
                  size=12, color=MUTED, italic=True))

    # вісь β_forced
    ax_l, ax_r, ay = 110, 730, 250
    f.append(line(ax_l, ay, ax_r, ay, color=INK, sw=2))
    ticks = [("30", 110), ("20", 264), ("10", 420), ("5", 560), ("2", 700)]
    for lab, x in ticks:
        f.append(line(x, ay - 6, x, ay + 6, color=INK, sw=1.6))
        f.append(text(x, ay + 24, "β_forced=" + lab, size=11, color=INK, bold=True))

    # ліва зона: замало запасу (велике β_forced)
    f.append(fitbox(95, 178, 190, 50,
                    "замало запасу:\nнедонасичення, гріється",
                    size=11, fill="#fdecea", stroke=POS, color="#9a2b22", bold=False))
    f.append(fitbox(95, 300, 190, 44,
                    "база не дотискає — Vce велике,\nпотужність Vce·Ic гріє ключ",
                    size=10, fill="#ffffff", stroke="#e7c9c5", color=MUTED))

    # центр: оптимум ≈10
    f.append(fitbox(330, 168, 180, 64,
                    "оптимум ≈ 10\nнадійне насичення,\nпомірний струм бази",
                    size=11, fill="#eef6ef", stroke=FIELD, color="#1f6e33", bold=False))

    # права зона: забагато бази (мале β_forced)
    f.append(fitbox(525, 178, 200, 50,
                    "забагато бази:\nмарний струм + повільне вимикання",
                    size=11, fill="#fbf0e0", stroke="#b5732e", color="#7a4e1d"))
    f.append(fitbox(525, 300, 200, 44,
                    "глибоке насичення копить заряд\nбази — його довго «вимітати»",
                    size=10, fill="#ffffff", stroke="#e6d2b0", color=MUTED))

    render(os.path.join(IMG, "forced-beta.svg"), W, H, *f)


# ── Фігура 5: derive.svg (формула, приклад, перевірки) ──────────────────────
def fig_derive():
    W, H = 840, 380
    f = [text(W / 2, 30, "Формула, приклад і перевірка", size=16, bold=True)]

    # ── міні-схема ключа ліворуч ──
    topY, botY = 78, 300
    t = npn(168, topY + 120, "")
    Sx = t.xc
    f.append(rail(Sx - 46, Sx + 56, topY, POS, "+5 В"))
    f.append(line(Sx, topY, Sx, topY + 17, color=INK, sw=2))
    f.append(load_box(Sx, topY + 34, label="навант. (Ic)"))
    f.append(line(Sx, topY + 51, Sx, t.yc, color=INK, sw=2))   # навантаж → колектор
    f.append(t.svg)
    f.append(line(Sx, t.ye, Sx, botY, color=INK, sw=2))        # емітер → GND
    f.append(gnd(Sx, botY))
    rs, rl, rr = res_h(t.xb - 44, t.yb, 38, "Rб")
    f.append(rs)
    f.append(line(rr, t.yb, t.xb, t.yb, color=INK, sw=2))
    f.append(line(60, t.yb, rl, t.yb, color=FIELD, sw=2))
    f.append(text(56, t.yb + 4, "Vlog", size=12, color=FIELD, bold=True, anchor="end"))

    # ── формула й приклад праворуч ──
    tx = 300
    f.append(text(tx, 86, "1)  обери β_forced ≈ 10", size=13, color=INK, bold=True, anchor="start"))
    f.append(text(tx, 114, "2)  Ib = Ic / β_forced", size=13, color=INK, bold=True, anchor="start"))
    f.append(text(tx, 144, "3)  Rб = (Vlog − Vbe) / Ib", size=13, color=POS, bold=True, anchor="start"))
    f.append(text(tx + 14, 164, "= β_forced·(Vlog − 0.7)/Ic", size=11, color=MUTED, anchor="start"))
    f.append(line(tx, 180, 800, 180, color="#dddddd", sw=1))

    f.append(text(tx, 206, "Приклад: Ic = 100 мА, Vlog = 5 В", size=12, color=INK, bold=True, anchor="start"))
    f.append(text(tx, 230, "Ib = 100/10 = 10 мА", size=12, color="#1f6e33", bold=True, anchor="start"))
    f.append(text(tx, 252, "Rб = (5 − 0.7)/10мА = 430 Ом → 390 Ом", size=12, color="#1f6e33", bold=True, anchor="start"))

    f.append(text(tx, 282, "перевір: Ib ≤ Iвиводу МК (≈20–40 мА)?  так", size=11, color="#9c6a16", bold=True, anchor="start"))
    f.append(text(tx, 304, "перевір: Vce(sat) < 0.3 В у даташиті?  так", size=11, color="#9c6a16", bold=True, anchor="start"))
    f.append(text(tx, 326, "не лізе → потрібен Дарлінгтон або MOSFET", size=11, color=MUTED, italic=True, anchor="start"))

    f.append(text(W / 2, 366, "Округляй Rб ВНИЗ (більше бази — безпечніше), та стеж, щоб струм бази не перевищив дозволений для виводу.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "derive.svg"), W, H, *f)


if __name__ == "__main__":
    fig_low_vs_high()
    fig_pnp_driver()
    fig_two_points()
    fig_forced_beta()
    fig_derive()
    print("OK: low-vs-high, pnp-driver, two-points, forced-beta, derive -> img/")
