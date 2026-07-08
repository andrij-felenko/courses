# -*- coding: utf-8 -*-
"""Фігури для теми «Штирьові зʼєднувачі (male)». Чистий Python, svgkit зі scripts/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BRASS = "#b8860b"   # латунний штир
BRASSF = "#f3e2b3"  # світла заливка металу
PLAST = "#2b2b3a"   # чорний пластик-ізолятор
PLASTF = "#40404f"


# ── Фігура 1: анатомія одного штиря (квадрат у перетині) ────────────────────
def fig_anatomy():
    W, H = 760, 520
    frags = []
    # горизонталь пластику (планка-ізолятор) по центру
    px, pw, ph = 250, 260, 74
    py = H / 2 - ph / 2
    frags.append(rect(px, py, pw, ph, fill=PLASTF, stroke=PLAST, sw=2, rx=4))
    frags.append(text(px + pw / 2, py + ph / 2 + 5, "пластиковий ізолятор", size=13,
                      color="#ffffff", bold=True))

    # один штир: вертикальна латунна смуга крізь планку
    cx = px + pw / 2
    pin_w = 18
    top_y = 70          # верх штиря (частина під розʼєм)
    bot_y = H - 70      # низ штиря (хвіст під пайку)
    frags.append(rect(cx - pin_w / 2, top_y, pin_w, bot_y - top_y, fill=BRASSF,
                      stroke=BRASS, sw=2, rx=2))
    # позначка квадратного перетину — маленький квадрат-виноска праворуч угорі
    qx, qy, qs = 640, 96, 40
    frags.append(rect(qx, qy, qs, qs, fill=BRASSF, stroke=BRASS, sw=2, rx=2))
    frags.append(line(qx, qy + qs + 4, qx, qy + qs + 20, color=MUTED, sw=1))
    frags.append(line(qx + qs, qy + qs + 4, qx + qs, qy + qs + 20, color=MUTED, sw=1))
    frags.append(text(qx + qs / 2, qy + qs + 34, "0.64 мм", size=11, color=MUTED))
    frags.append(text(qx + qs / 2, qy - 8, "перетин —", size=11, color=MUTED))
    frags.append(text(qx + qs / 2, qy - 22, "квадрат", size=11, color=MUTED, bold=True))

    # мітки трьох ділянок штиря (виноски ліворуч, з запасом)
    def label_left(y, s):
        bx = 40
        b, bw, bh = textbox(bx + 78, y, s, size=12, pad=7)
        frags.append(b)
        frags.append(line(bx + 78 + bw / 2, y, cx - pin_w / 2, y, color=MUTED, sw=1, dash="4 3"))

    label_left((top_y + py) / 2, "частина під\nрозʼєм (mating)")
    label_left((py + ph + bot_y) / 2, "хвіст під\nпайку (tail)")

    # розмір pitch: два сусідні штирі-привиди й розмірна лінія 2.54
    ghost_dx = 70
    for gx in (cx - ghost_dx, cx + ghost_dx):
        frags.append(rect(gx - pin_w / 2, py - 4, pin_w, ph + 8, fill="#eceff4",
                          stroke=MUTED, sw=1.2, rx=2))
    dim_y = py + ph + 34
    frags.append(line(cx - ghost_dx, dim_y, cx + ghost_dx, dim_y, color=INK, sw=1.4))
    for gx in (cx - ghost_dx, cx + ghost_dx):
        frags.append(line(gx, dim_y - 6, gx, dim_y + 6, color=INK, sw=1.4))
    b, bw, bh = textbox(cx, dim_y + 26, "крок 2.54 мм (0.1″)", size=13, pad=7, bold=True)
    frags.append(b)

    # горизонтальна пунктирна лінія — рівень плати
    board_y = py + ph + 2
    frags.append(line(120, board_y, W - 40, board_y, color=FIELD, sw=1.4, dash="7 5"))
    frags.append(text(150, board_y + 16, "поверхня плати", size=11, color=FIELD, bold=True,
                      anchor="start"))

    render(os.path.join(IMG, "anatomy.svg"), W, H,
           text(W / 2, 30, "Будова одного штиря: метал крізь пластик", size=16, bold=True),
           *frags)


# ── Фігура 2: прямий проти кутового корпусу ─────────────────────────────────
def fig_straight_vs_angle():
    W, H = 720, 430
    frags = []
    pinw = 16

    # ── лівий блок: прямий (вертикальний) ──
    lx = 175
    board_y = 300
    frags.append(rect(lx - 90, board_y, 180, 26, fill="#d9e6cf", stroke=FIELD, sw=1.6, rx=3))
    frags.append(text(lx, board_y + 46, "плата", size=12, color=FIELD, bold=True))
    # планка на платі
    bh = 30
    frags.append(rect(lx - 70, board_y - bh, 140, bh, fill=PLASTF, stroke=PLAST, sw=1.8, rx=3))
    # 4 штирі вгору
    for i in range(4):
        xx = lx - 45 + i * 30
        frags.append(rect(xx - pinw / 2, board_y - bh - 66, pinw, 66, fill=BRASSF,
                          stroke=BRASS, sw=1.6, rx=2))
        # хвіст крізь плату вниз
        frags.append(rect(xx - pinw / 2, board_y, pinw, 22, fill=BRASSF,
                          stroke=BRASS, sw=1.4, rx=2))
    frags.append(text(lx, 70, "прямий", size=15, bold=True))
    frags.append(text(lx, 90, "(вертикальний)", size=12, color=MUTED))
    frags.append(text(lx, 118, "розʼєм заходить згори", size=11, color=INK))

    # ── правий блок: кутовий (right-angle) ──
    rx = 545
    frags.append(rect(rx - 90, board_y, 180, 26, fill="#d9e6cf", stroke=FIELD, sw=1.6, rx=3))
    frags.append(text(rx, board_y + 46, "плата", size=12, color=FIELD, bold=True))
    # планка на платі
    frags.append(rect(rx - 70, board_y - bh, 60, bh, fill=PLASTF, stroke=PLAST, sw=1.8, rx=3))
    # штирі: коротко вгору, згин, довго вбік (горизонтально)
    for i in range(4):
        yy = board_y - bh + 6 + i * 6.0
        # вертикальний огризок у планці
    # намалюємо L-подібні штирі
    for i in range(4):
        col_x = rx - 55 + i * 12
        bend_y = board_y - bh - 8 - i * 12
        # вертикаль від плати вгору до згину
        frags.append(line(col_x, board_y + 20, col_x, bend_y, color=BRASS, sw=3.2))
        # горизонталь від згину вправо
        frags.append(line(col_x, bend_y, rx + 78, bend_y, color=BRASS, sw=3.2))
    frags.append(text(rx, 70, "кутовий", size=15, bold=True))
    frags.append(text(rx, 90, "(right-angle)", size=12, color=MUTED))
    frags.append(text(rx, 118, "розʼєм заходить збоку", size=11, color=INK))

    render(os.path.join(IMG, "straight-vs-angle.svg"), W, H,
           text(W / 2, 32, "Два корпуси: звідки заходить відповідник", size=16, bold=True),
           *frags)


# ── Фігура 3: планка, яку ламають на потрібну довжину ───────────────────────
def fig_breakaway():
    W, H = 720, 300
    frags = []
    pinw = 14
    n = 12
    x0 = 90
    step = 34
    top = 120
    ph = 30
    # довга планка
    frags.append(rect(x0 - 12, top, (n - 1) * step + 24, ph, fill=PLASTF,
                      stroke=PLAST, sw=1.8, rx=4))
    for i in range(n):
        xx = x0 + i * step
        frags.append(rect(xx - pinw / 2, top - 40, pinw, 40, fill=BRASSF,
                          stroke=BRASS, sw=1.5, rx=2))
    # місце злому після 4-го штиря
    br = x0 + 3 * step + step / 2
    frags.append(line(br, top - 52, br, top + ph + 20, color=POS, sw=2.2, dash="6 5"))
    b, bw, bh = textbox(br, top + ph + 42, "ламаємо тут: рівно 4 штирі", size=12, pad=7,
                        color=POS, stroke=POS)
    frags.append(b)
    # ножиці-піктограма (простий трикутник-стрілка вниз до лінії)
    frags.append(text(br, top - 62, "злам руками / кусачками", size=11, color=MUTED))

    frags.append(text(W / 2, 40, "Планка 40 штирів → відламуємо скільки треба", size=16, bold=True))
    frags.append(text(W / 2, 62, "одна довга гребінка = запас на десятки дрібних розʼємів",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "breakaway.svg"), W, H, *frags)


# ── Фігура 4 (hist): ланцюг власників контакту Mini-PV ──────────────────────
def fig_owners_timeline():
    W, H = 920, 430
    frags = []
    # горизонтальна вісь часу
    ax0, ax1 = 70, W - 60
    ay = 215
    frags.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    frags.append(text(ax1 + 6, ay + 4, "час →", size=12, color=MUTED, anchor="start"))

    # роки й підписи: (рік, назва+подія в рамці, вгору/вниз)
    events = [
        (1950, "Berg Electronics", "заснування · Гаррісбург, PA", +1),
        (1972, "du Pont", "поглинання ≈ $25 млн", -1),
        (1993, "Hicks-Muse", "du Pont продає підрозділ", +1),
        (1998, "FCI", "Framatome Connectors Int.", -1),
        (2016, "Amphenol", "власник по сьогодні", -1),
    ]
    y0, y1 = 1947, 2019
    def X(yr):
        return ax0 + 20 + (yr - y0) / (y1 - y0) * (ax1 - ax0 - 40)

    # два рівні по кожен бік, щоб рамки НЕ налазили одна на одну по горизонталі
    up_far, up_near = 150, 92
    dn_near, dn_far = 92, 150
    for i, (yr, name, cap, side) in enumerate(events):
        x = X(yr)
        # вузол
        frags.append(circle(x, ay, 6, fill=BRASSF, stroke=BRASS, sw=2))
        # рік — трохи вбік від вузла вздовж осі, поза самою лінією (над/під нею)
        frags.append(text(x, ay - 14 if side > 0 else ay + 22, str(yr),
                          size=13, color=INK, bold=True))
        # рамка: назва (жирна) + подія (дрібним) — двома рядками в ОДНІЙ рамці,
        # тож окремих плаваючих написів, що могли б налазити, немає
        label = name + "\n" + cap
        off = (up_far if i in (0, 2) else up_near) if side > 0 else \
              (dn_far if i == 4 else dn_near)
        by = ay - off if side > 0 else ay + off
        b, bw, bh = textbox(x, by, label, size=12, pad=8, bold=False,
                            fill="#fbf6e9", stroke=BRASS)
        frags.append(b)
        # виноска від вузла до краю рамки — веде повз рік (рік зсунуто вбік осі)
        y_from = ay - 26 if side > 0 else ay + 34
        y_to = by + bh / 2 if side > 0 else by - bh / 2
        frags.append(line(x, y_from, x, y_to, color=MUTED, sw=1.2, dash="4 3"))

    render(os.path.join(IMG, "owners-timeline.svg"), W, H,
           text(W / 2, 30, "Хто володів контактом Mini-PV: 1950 → сьогодні", size=16, bold=True),
           text(W / 2, 52, "деталь та сама — мінявся лише напис на оснащенні", size=12, color=MUTED),
           *frags)


if __name__ == "__main__":
    fig_anatomy()
    fig_straight_vs_angle()
    fig_breakaway()
    fig_owners_timeline()
    print("figures written to", IMG)
