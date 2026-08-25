# -*- coding: utf-8 -*-
"""Фігури до теми «PNP-ключ і схема high-side».
Чотири фігури:
  1) level-problem.svg  — чому МК не може ЗАКРИТИ PNP (вузловий аналіз спокою)
  2) npn-translator.svg — повна схема: маленький NPN стягує базу PNP, три резистори
  3) current-paths.svg  — силовий шлях проти керувального; повернення в спокій
  4) turnoff-rc.svg     — швидкість вимикання: Rпідт заряджає паразитну Cбе
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні примітиви схем ─────────────────────────────────────────────────
def gnd(cx, y, label="GND"):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8)]
    out.append(line(cx - 14, y + 7, cx + 14, y + 7, color=INK, sw=2.4))
    out.append(line(cx - 8, y + 12, cx + 8, y + 12, color=INK, sw=2.0))
    out.append(line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8))
    if label:
        out.append(text(cx, y + 33, label, size=11, color=INK, bold=True))
    return "".join(out)


def res_v(cx, cy, h=40, label=None, lab_side="right"):
    w = 16
    yt, yb = cy - h / 2, cy + h / 2
    out = [rect(cx - w / 2, yt, w, h, fill="#ffffff", stroke=INK, sw=1.6, rx=2)]
    if label:
        if lab_side == "right":
            out.append(text(cx + w / 2 + 6, cy + 4, label, size=12, color=INK, anchor="start"))
        else:
            out.append(text(cx - w / 2 - 6, cy + 4, label, size=12, color=INK, anchor="end"))
    return "".join(out), yt, yb


def res_h(cx, cy, w=40, label=None, lab_above=True):
    h = 16
    xl, xr = cx - w / 2, cx + w / 2
    out = [rect(xl, cy - h / 2, w, h, fill="#ffffff", stroke=INK, sw=1.6, rx=2)]
    if label:
        if lab_above:
            out.append(text(cx, cy - h / 2 - 6, label, size=12, color=INK))
        else:
            out.append(text(cx, cy + h / 2 + 14, label, size=12, color=INK))
    return "".join(out), xl, xr


class Tr:
    __slots__ = ("svg", "xb", "xc", "yc", "ye", "yb")
    def __init__(self, svg, xb, xc, yc, ye, yb):
        self.svg, self.xb, self.xc, self.yc, self.ye, self.yb = svg, xb, xc, yc, ye, yb


def npn(cx, cy, label=None, lab_anchor="start", lab_dx=30):
    out = []
    bt, bb = cy - 28, cy + 28
    out.append(line(cx, bt, cx, bb, color=INK, sw=3))
    out.append(line(cx - 30, cy, cx, cy, color=INK, sw=2))
    cx2 = cx + 30
    out.append(line(cx, bt + 9, cx2, bt - 10, color=INK, sw=2))
    yC = bt - 34
    out.append(line(cx2, bt - 10, cx2, yC, color=INK, sw=2))
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
    """PNP: емітер угорі зі стрілкою всередину, колектор унизу.
    ye — кінець емітерного виводу (угорі), yc — колекторного (унизу)."""
    out = []
    bt, bb = cy - 28, cy + 28
    out.append(line(cx, bt, cx, bb, color=INK, sw=3))
    out.append(line(cx - 30, cy, cx, cy, color=INK, sw=2))
    cx2 = cx + 30
    out.append(line(cx, bt + 9, cx2, bt - 10, color=INK, sw=2))
    yE = bt - 34
    out.append(line(cx2, bt - 10, cx2, yE, color=INK, sw=2))
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        cx2 - 2, bt - 10, cx + 16, bt + 1, cx + 17, bt + 12, INK))
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


# ── Фігура 1: level-problem.svg ─────────────────────────────────────────────
def fig_level_problem():
    W, H = 860, 440
    f = [text(W / 2, 30, "Чому МК не може ЗАКРИТИ PNP у верхньому плечі", size=16, bold=True)]

    # схема: PNP, емітер на +12, база тягнеться до МК
    topY, botY = 80, 360
    Sx = 360
    f.append(rail(180, 540, topY, POS, "+12 В"))
    tp = pnp(Sx - 30, 170, "PNP")
    f.append(line(tp.xc, topY, tp.xc, tp.ye, color=INK, sw=2))
    f.append(dot(tp.xc, topY))
    f.append(tp.svg)
    f.append(line(tp.xc, tp.yc, tp.xc, tp.yc + 14, color=INK, sw=2))
    f.append(load_box(tp.xc, tp.yc + 38, label="навантаж."))
    f.append(line(tp.xc, tp.yc + 55, tp.xc, botY, color=INK, sw=2))
    f.append(gnd(tp.xc, botY))

    # позначки потенціалів
    f.append(text(tp.xc + 14, topY + 22, "емітер = +12 В", size=11, color=POS, bold=True, anchor="start"))

    # дріт бази до МК (через Rб)
    rs, rl, rr = res_h(tp.xb - 60, tp.yb, 38, "Rб")
    f.append(rs)
    f.append(line(rr, tp.yb, tp.xb, tp.yb, color=INK, sw=2))
    f.append(line(170, tp.yb, rl, tp.yb, color=FIELD, sw=2))
    f.append(text(166, tp.yb + 4, "МК", size=12, color=FIELD, bold=True, anchor="end"))
    f.append(text(tp.xb - 60, tp.yb + 30, "база PNP", size=11, color=INK, anchor="middle"))

    # права панель — розбір трьох спроб
    lx, ly, lw, lh = 560, 70, 280, 300
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
    f.append(text(lx + lw / 2, ly + 22, "PNP відкритий, поки база < +11.3 В", size=12, bold=True))
    f.append(fitbox(lx + 12, ly + 36, lw - 24, 50,
                    "МК = 3.3 В (високий):\nбаза ≈ 3.3 В << 12 В → перехід\nвідкритий → PNP ВВІМКНЕНО",
                    size=11, fill="#fdecea", stroke=POS, color="#9a2b22"))
    f.append(fitbox(lx + 12, ly + 94, lw - 24, 50,
                    "МК = 0 В (низький):\nбаза ще нижче → перехід\nвідкритий → PNP ВВІМКНЕНО",
                    size=11, fill="#fdecea", stroke=POS, color="#9a2b22"))
    f.append(fitbox(lx + 12, ly + 152, lw - 24, 50,
                    "вивід Hi-Z (відпущено):\nпідтягувань до 12 В нема →\nбаза «висить» внизу → ВВІМКНЕНО",
                    size=11, fill="#fdecea", stroke=POS, color="#9a2b22"))
    f.append(fitbox(lx + 12, ly + 210, lw - 24, 54,
                    "ЩОБ ЗАКРИТИ: базу треба підняти\nдо +12 В (зрівняти з емітером).\nМК туди не дістає → не може.",
                    size=11, fill="#eef6ef", stroke=FIELD, color="#1f6e33"))

    f.append(text(W / 2, 424,
                  "Логіка ходить 0…3.3 В, а закрити PNP можна лише підтягнувши базу до 12 В — звідси потрібен перекладач рівня.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "level-problem.svg"), W, H, *f)


# ── Фігура 2: npn-translator.svg ────────────────────────────────────────────
def fig_npn_translator():
    W, H = 880, 460
    f = [text(W / 2, 30, "Повна схема: маленький NPN перекладає рівень для силового PNP", size=16, bold=True)]

    topY, botY = 80, 370
    f.append(rail(150, 600, topY, POS, "+12 В"))
    f.append(line(150, botY, 600, botY, color=INK, sw=2))
    f.append(text(142, botY + 4, "GND", size=12, color=INK, bold=True, anchor="end"))

    # силовий PNP праворуч-угорі
    tp = pnp(480, 158, "PNP — силовий ключ")
    f.append(line(tp.xc, topY, tp.xc, tp.ye, color=INK, sw=2))
    f.append(dot(tp.xc, topY))
    f.append(tp.svg)
    f.append(line(tp.xc, tp.yc, tp.xc, tp.yc + 14, color=INK, sw=2))
    f.append(load_box(tp.xc, tp.yc + 38, label="навантаження"))
    f.append(line(tp.xc, tp.yc + 55, tp.xc, botY, color=INK, sw=2))
    f.append(dot(tp.xc, botY))

    baseY = tp.yb
    # підтягувальний резистор бази PNP до +12
    pull_x = tp.xb - 80
    rs, ryt, ryb = res_v(pull_x, (topY + baseY) / 2, 42, "R_pull", "left")
    f.append(rs)
    f.append(line(pull_x, topY, pull_x, ryt, color=INK, sw=2))
    f.append(dot(pull_x, topY))
    f.append(line(pull_x, ryb, pull_x, baseY, color=INK, sw=2))
    f.append(line(tp.xb, baseY, pull_x, baseY, color=INK, sw=2))
    f.append(dot(pull_x, baseY))

    # резистор бази PNP (між колектором NPN і базою PNP) — горизонтальний на baseY
    tn = npn(255, 250, "NPN — перекладач")
    rs2, r2l, r2r = res_h((pull_x + tn.xc) / 2, baseY, 44, "R_pb")
    f.append(rs2)
    f.append(line(pull_x, baseY, r2l, baseY, color=INK, sw=2))
    f.append(line(r2r, baseY, tn.xc, baseY, color=INK, sw=2))
    f.append(line(tn.xc, baseY, tn.xc, tn.yc, color=INK, sw=2))
    # емітер NPN → земля
    f.append(line(tn.xc, tn.ye, tn.xc, botY, color=INK, sw=2))
    f.append(dot(tn.xc, botY))
    # база NPN ← МК через Rб
    rs3, r3l, r3r = res_h(tn.xb - 50, tn.yb, 40, "R_b")
    f.append(rs3)
    f.append(line(r3r, tn.yb, tn.xb, tn.yb, color=INK, sw=2))
    f.append(line(165, tn.yb, r3l, tn.yb, color=FIELD, sw=2))
    f.append(text(160, tn.yb + 4, "МК", size=12, color=FIELD, bold=True, anchor="end"))

    # панель-легенда праворуч
    lx, ly, lw, lh = 630, 70, 240, 300
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
    f.append(text(lx + lw / 2, ly + 22, "як працює", size=13, bold=True))
    f.append(fitbox(lx + 12, ly + 34, lw - 24, 64,
                    "МК = 1:\nNPN насичений → стягує базу PNP\nкрізь R_pb униз → PNP ВВІМКНЕНО",
                    size=11, fill="#eef6ef", stroke=FIELD, color=INK))
    f.append(fitbox(lx + 12, ly + 104, lw - 24, 64,
                    "МК = 0:\nNPN закритий → R_pull тягне базу\nPNP до +12 → PNP ВИМКНЕНО",
                    size=11, fill="#f4f6f8", stroke=MUTED, color=INK))
    f.append(fitbox(lx + 12, ly + 174, lw - 24, 44,
                    "дві інверсії складаються →\nлогіка ПРЯМА: 1 вмикає",
                    size=11, fill="#f0ecf6", stroke="#7a4e8a", color=INK))
    f.append(fitbox(lx + 12, ly + 226, lw - 24, 56,
                    "R_b — струм бази NPN\nR_pb — струм бази PNP\nR_pull — тримає PNP закритим",
                    size=11, fill="#f4f6f8", stroke=MUTED, color=MUTED))

    f.append(text(W / 2, 444,
                  "NPN керується від землі (це МК уміє), а вже він стягує високовольтну базу PNP крізь R_pb.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "npn-translator.svg"), W, H, *f)


# ── Фігура 3: current-paths.svg ─────────────────────────────────────────────
def fig_current_paths():
    W, H = 860, 430
    f = [text(W / 2, 30, "Два струми: потужний силовий і кволий керувальний", size=16, bold=True)]

    topY, botY = 78, 360
    f.append(rail(150, 560, topY, POS, "+12 В"))
    f.append(line(150, botY, 560, botY, color=INK, sw=2))
    f.append(text(142, botY + 4, "GND", size=12, color=INK, bold=True, anchor="end"))

    tp = pnp(470, 156, "PNP")
    f.append(line(tp.xc, topY, tp.xc, tp.ye, color=POS, sw=3))  # силовий шлях — товсто, червоно
    f.append(dot(tp.xc, topY))
    f.append(tp.svg)
    f.append(line(tp.xc, tp.yc, tp.xc, tp.yc + 14, color=POS, sw=3))
    f.append(load_box(tp.xc, tp.yc + 38, label="навантаж."))
    f.append(line(tp.xc, tp.yc + 55, tp.xc, botY, color=POS, sw=3))
    f.append(dot(tp.xc, botY))
    f.append(text(tp.xc + 60, (tp.yc + botY) / 2, "силовий струм", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(tp.xc + 60, (tp.yc + botY) / 2 + 18, "(ампери)", size=11, color=POS, anchor="start"))

    baseY = tp.yb
    pull_x = tp.xb - 80
    rs, ryt, ryb = res_v(pull_x, (topY + baseY) / 2, 42, "R_pull", "left")
    f.append(rs)
    f.append(line(pull_x, topY, pull_x, ryt, color=INK, sw=2))
    f.append(dot(pull_x, topY))
    f.append(line(pull_x, ryb, pull_x, baseY, color=NEG, sw=2.4))
    f.append(line(tp.xb, baseY, pull_x, baseY, color=NEG, sw=2.4))
    f.append(dot(pull_x, baseY))

    tn = npn(255, 248, "NPN")
    rs2, r2l, r2r = res_h((pull_x + tn.xc) / 2, baseY, 44, "R_pb")
    f.append(rs2)
    f.append(line(pull_x, baseY, r2l, baseY, color=NEG, sw=2.4))
    f.append(line(r2r, baseY, tn.xc, baseY, color=NEG, sw=2.4))
    f.append(line(tn.xc, baseY, tn.xc, tn.yc, color=NEG, sw=2.4))
    f.append(line(tn.xc, tn.ye, tn.xc, botY, color=NEG, sw=2.4))
    f.append(dot(tn.xc, botY))
    f.append(text((pull_x + tn.xc) / 2, baseY - 30, "керувальний струм (міліампери)",
                  size=11, color=NEG, bold=True, anchor="middle"))

    rs3, r3l, r3r = res_h(tn.xb - 50, tn.yb, 40, "R_b")
    f.append(rs3)
    f.append(line(r3r, tn.yb, tn.xb, tn.yb, color=INK, sw=2))
    f.append(line(165, tn.yb, r3l, tn.yb, color=FIELD, sw=2))
    f.append(text(160, tn.yb + 4, "МК=1", size=12, color=FIELD, bold=True, anchor="end"))

    # пояснення внизу
    f.append(fitbox(600, 90, 250, 86,
                    "ВВІМКНЕНО (МК=1):\nсиловий струм — від +12 крізь\nемітер→колектор PNP у навантаж.\nкерувальний — база PNP крізь\nR_pb у відкритий NPN на землю",
                    size=11, fill="#ffffff", stroke="#c9d3dc", color=INK))
    f.append(fitbox(600, 186, 250, 74,
                    "ВИМКНЕНО (МК=0):\nNPN закрився → керувальний\nшлях обірвано → R_pull підтягує\nбазу до +12 → силовий згас",
                    size=11, fill="#f4f6f8", stroke=MUTED, color=INK))

    f.append(text(W / 2, 414,
                  "NPN несе лише струм бази PNP (міліампери) — силу тягне сам PNP; тому NPN досить найдешевшого сигнального.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "current-paths.svg"), W, H, *f)


# ── Фігура 4: turnoff-rc.svg ────────────────────────────────────────────────
def fig_turnoff_rc():
    W, H = 860, 380
    f = [text(W / 2, 30, "Швидкість вимикання: R_pull заряджає паразитну ємність бази", size=16, bold=True)]

    # ліворуч — фрагмент: база PNP, R_pull до +12, паразитна Cбе
    topY = 70
    Sx = 210
    baseY = 250
    f.append(rail(120, 320, topY, POS, "+12 В"))
    # емітер PNP (символ спрощено — планка)
    f.append(line(Sx + 40, topY, Sx + 40, baseY - 24, color=INK, sw=2))
    f.append(dot(Sx + 40, topY))
    f.append(line(Sx + 40, baseY - 24, Sx + 40, baseY + 24, color=INK, sw=3))  # планка бази
    f.append(text(Sx + 52, topY + 30, "емітер +12", size=10, color=POS, anchor="start"))
    f.append(text(Sx + 52, baseY + 4, "база PNP", size=11, color=INK, anchor="start"))
    # R_pull від +12 до бази
    rs, ryt, ryb = res_v(Sx - 30, (topY + baseY) / 2, 44, "R_pull", "left")
    f.append(rs)
    f.append(line(Sx - 30, topY, Sx - 30, ryt, color=INK, sw=2))
    f.append(dot(Sx - 30, topY))
    f.append(line(Sx - 30, ryb, Sx - 30, baseY, color=INK, sw=2))
    f.append(line(Sx - 30, baseY, Sx + 40, baseY, color=INK, sw=2))
    f.append(dot(Sx - 30, baseY))
    # Cбе — конденсатор від бази вниз (умовний символ)
    cap_y = baseY + 40
    f.append(line(Sx + 40, baseY, Sx + 40, cap_y, color=NEG, sw=2))
    f.append(line(Sx + 28, cap_y, Sx + 52, cap_y, color=NEG, sw=2.6))
    f.append(line(Sx + 28, cap_y + 6, Sx + 52, cap_y + 6, color=NEG, sw=2.6))
    f.append(text(Sx + 58, cap_y + 6, "C_be (паразитна)", size=10, color=NEG, anchor="start"))
    f.append(line(Sx + 40, cap_y + 6, Sx + 40, cap_y + 20, color=NEG, sw=2))
    f.append(gnd(Sx + 40, cap_y + 20))

    # праворуч — графік напруги бази в часі при вимиканні
    gx, gy = 470, 300        # початок осей
    gr, gt = 820, 90
    f.append(line(gx, gy, gr, gy, color=INK, sw=1.6))
    f.append(text(gr + 4, gy + 4, "t", size=12, color=INK, bold=True, anchor="start"))
    f.append(line(gx, gy, gx, gt, color=INK, sw=1.6))
    f.append(text(gx - 6, gt - 8, "U(база)", size=11, color=INK, anchor="middle"))
    # рівні
    v12 = gt + 14
    v_on = gy - 24
    f.append(line(gx, v12, gr, v12, color="#dddddd", sw=1, dash="4,3"))
    f.append(text(gx - 6, v12 + 4, "12 В", size=10, color=MUTED, anchor="end"))
    f.append(line(gx, v_on, gr, v_on, color="#dddddd", sw=1, dash="4,3"))
    f.append(text(gx - 6, v_on + 4, "≈11.3", size=10, color=MUTED, anchor="end"))
    # крива: до події — на v_on (ввімкнено), далі експоненційний підйом до v12
    tev = gx + 120
    pts = ["%.1f,%.1f" % (gx, v_on), "%.1f,%.1f" % (tev, v_on)]
    for i in range(0, 81):
        x = tev + i * 3.0
        tau = i / 18.0
        y = v_on - (v_on - v12) * (1 - math.exp(-tau))
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" L ".join(pts), POS))
    f.append(line(tev, gt, tev, gy, color=FIELD, sw=1.4, dash="5,3"))
    f.append(text(tev, gy + 18, "МК → 0 (вимикаємо)", size=10, color=FIELD, bold=True, anchor="middle"))
    f.append(text(tev + 130, v_on - 12, "τ = R_pull · C_be", size=12, color=POS, bold=True, anchor="middle"))
    f.append(text(tev + 130, v_on + 6, "вимикання затягується", size=10, color="#9a2b22", anchor="middle"))

    f.append(text(W / 2, 364,
                  "Замалий R_pull даремно гріє NPN; завеликий — повільно витягує базу до +12 (PNP «залипає» відкритим). Десятки кілоом — баланс.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "turnoff-rc.svg"), W, H, *f)


if __name__ == "__main__":
    fig_level_problem()
    fig_npn_translator()
    fig_current_paths()
    fig_turnoff_rc()
    print("OK: level-problem, npn-translator, current-paths, turnoff-rc -> img/")
