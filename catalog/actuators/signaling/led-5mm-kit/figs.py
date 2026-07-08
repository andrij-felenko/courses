# -*- coding: utf-8 -*-
"""Фігури для статті «Набір 5мм світлодіодів» (catalog/actuators/signaling/led-5mm-kit).
Три фігури:
  (1) anatomy    — будова 5мм світлодіода: лінза, коваделко/стовпчик, зріз, дві ніжки;
  (2) vf-colors  — пряма напруга за кольором (чому в межах одного набору Vf різна);
  (3) drive      — правильне ввімкнення: LED + гасильний резистор, покроково.
Запуск: python figs.py  →  ./img/*.svg
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: анатомія 5мм світлодіода ───────────────────────────────────────
def fig_anatomy():
    W, H = 720, 490
    frags = []

    # центр лінзи
    cx, top = 300, 70
    body_w, body_h = 150, 190          # прямокутна частина корпусу
    bx = cx - body_w / 2

    # купол лінзи (півколо зверху) — малюємо як прямокутник із заокругленим верхом
    frags.append('<path d="M %.1f %.1f '
                 'L %.1f %.1f '
                 'A %.1f %.1f 0 0 1 %.1f %.1f '
                 'L %.1f %.1f Z" '
                 'fill="#dfeafc" stroke="#7a8aa8" stroke-width="2"/>'
                 % (bx, top + body_h,
                    bx, top + body_w / 2,
                    body_w / 2, body_w / 2, bx + body_w, top + body_w / 2,
                    bx + body_w, top + body_h))

    # обідок біля основи + ПЛОСКИЙ ЗРІЗ (з боку катода, ліворуч)
    rim_y = top + body_h
    frags.append(line(bx - 10, rim_y, bx + body_w + 10, rim_y, color="#7a8aa8", sw=3))
    # плоский зріз — зрізаний лівий бік обідка
    frags.append(line(bx - 10, rim_y - 26, bx - 10, rim_y, color=NEG, sw=5))
    frags.append(text(bx - 74, rim_y - 8, "плоский", size=12, color=NEG, bold=True))
    frags.append(text(bx - 74, rim_y + 9, "зріз", size=12, color=NEG, bold=True))
    frags.append(line(bx - 44, rim_y - 12, bx - 12, rim_y - 12, color=NEG, sw=1.2, dash="3,3"))

    # внутрішні деталі: коваделко (велике, катод) ліворуч, стовпчик (анод) праворуч
    # коваделко — чашка з кристалом
    anvil_x = cx - 30
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                 'fill="#c8d2e0" stroke="#5b6a82" stroke-width="1.6"/>'
                 % (anvil_x - 20, top + 150, anvil_x + 4, top + 150,
                    anvil_x + 12, top + 96, anvil_x - 28, top + 96))
    # кристал у чашці
    frags.append('<rect x="%.1f" y="%.1f" width="10" height="8" fill="#e8c400" '
                 'stroke="#a08a00" stroke-width="1"/>' % (anvil_x - 13, top + 92))
    # стовпчик — тонкий стрижень (анод)
    post_x = cx + 34
    frags.append('<rect x="%.1f" y="%.1f" width="8" height="56" fill="#c8d2e0" '
                 'stroke="#5b6a82" stroke-width="1.4"/>' % (post_x - 4, top + 96))
    # золотий провідничок від стовпчика до кристала
    frags.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" '
                 'fill="none" stroke="#c9a227" stroke-width="1.6"/>'
                 % (post_x, top + 100, cx, top + 70, anvil_x - 8, top + 92))

    # дві ніжки: катод (коротка, ліворуч) і анод (довга, праворуч)
    leg_top = rim_y
    frags.append(line(anvil_x - 8, leg_top, anvil_x - 8, leg_top + 90, color="#8a8a8a", sw=5))   # катод — коротший
    frags.append(line(post_x, leg_top, post_x, leg_top + 150, color="#8a8a8a", sw=5))            # анод — довший

    # підписи ніжок
    frags.append(minus(anvil_x - 8, leg_top + 108, r=13))
    frags.append(text(anvil_x - 8, leg_top + 132, "катод", size=13, color=NEG, bold=True))
    frags.append(text(anvil_x - 8, leg_top + 149, "коротка", size=11, color=MUTED))

    frags.append(plus(post_x, leg_top + 168, r=13))
    frags.append(text(post_x, leg_top + 192, "анод", size=13, color=POS, bold=True))
    frags.append(text(post_x, leg_top + 209, "довга", size=11, color=MUTED))

    # виноски до внутрішніх частин (праворуч, з запасом)
    lx = bx + body_w + 30
    frags.append(line(anvil_x - 6, top + 120, lx - 6, top + 120, color=MUTED, sw=1, dash="3,3"))
    b1, w1, h1 = textbox(lx + 96, top + 120, "коваделко (чашка):\nвеликий бік = катод",
                         size=12, fill="#eaf0fd", stroke=NEG, min_w=170)
    frags.append(b1)
    frags.append(line(post_x + 4, top + 124, lx - 6, top + 176, color=MUTED, sw=1, dash="3,3"))
    b2, w2, h2 = textbox(lx + 96, top + 176, "стовпчик:\nтонкий бік = анод",
                         size=12, fill="#fdecea", stroke=POS, min_w=170)
    frags.append(b2)

    render(os.path.join(OUT, "anatomy.svg"), W, H, *frags,
           title="Будова 5мм світлодіода: як упізнати полярність без приладу")


# ── Фігура 2: пряма напруга за кольором ──────────────────────────────────────
def fig_vf_colors():
    W, H = 760, 420
    frags = []
    # (назва, колір-заливка, Vf_low, Vf_high)
    rows = [
        ("інфрачервоний", "#8a1f1f", 1.2, 1.5),
        ("червоний",      "#c0392b", 1.8, 2.2),
        ("жовтий",        "#e8c400", 2.0, 2.2),
        ("зелений",       "#27ae60", 2.0, 3.5),
        ("синій",         "#2457d6", 2.8, 3.6),
        ("білий",         "#c9c9c9", 2.8, 3.6),
    ]

    # шкала напруги 0..4 В
    ax_x0, ax_x1 = 200, W - 40
    vmin, vmax = 0.0, 4.0
    def X(v):
        return ax_x0 + (v - vmin) / (vmax - vmin) * (ax_x1 - ax_x0)

    top = 66
    row_h = 46
    # сітка й підписи осі
    for gv in [0, 1, 2, 3, 4]:
        gx = X(gv)
        frags.append(line(gx, top - 6, gx, top + len(rows) * row_h - 8, color="#e5e7eb", sw=1))
        frags.append(text(gx, top - 14, "%d В" % gv, size=12, color=MUTED))

    for i, (name, col, lo, hi) in enumerate(rows):
        y = top + i * row_h + 12
        # назва кольору ліворуч
        frags.append(text(180, y + 5, name, size=13, color=INK, anchor="end", bold=True))
        # брусок діапазону Vf
        xL, xR = X(lo), X(hi)
        frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="22" rx="5" '
                     'fill="%s" stroke="#333" stroke-width="1"/>'
                     % (xL, y - 11, max(xR - xL, 6), col))
        # числа діапазону праворуч від бруска
        frags.append(text(xR + 8, y + 5, "%.1f–%.1f" % (lo, hi), size=12,
                          color=MUTED, anchor="start"))

    # висновок унизу власною рамкою
    note = ("що коротша хвиля світла (від червоного до синього) — то вищий бар'єр напівпровідника\n"
            "і то більша пряма напруга; тому в одному наборі червоний світить від ~1.8 В, а синій — від ~3 В")
    frags.append(fitbox(60, 336, W - 120, 56, note, size=13, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(OUT, "vf-colors.svg"), W, H, *frags,
           title="Пряма напруга Vf залежить від кольору світлодіода")


# ── Фігура 3: правильне ввімкнення — LED + гасильний резистор ─────────────────
def fig_drive():
    W, H = 720, 340
    frags = []

    y = 150
    x0 = 80
    # +5 В зліва
    frags.append(plus(x0, y, r=13))
    frags.append(text(x0, y - 26, "5 В", size=14, color=POS, bold=True))
    frags.append(line(x0 + 13, y, 170, y, color=INK, sw=2))

    # резистор (зигзаг)
    rx0 = 170
    zig = "M %.1f %.1f " % (rx0, y)
    step = 12
    for k in range(6):
        dy = -14 if k % 2 == 0 else 14
        zig += "l %d %d " % (step, dy)
    zig += "l %d %d" % (6, (14 if 6 % 2 else -14))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (zig, INK))
    rx1 = rx0 + 6 * step + 6
    frags.append(text((rx0 + rx1) / 2, y - 24, "R = 330 Ω", size=13, color=INK, bold=True))
    frags.append(line(rx1, y, rx1 + 60, y, color=INK, sw=2))

    # світлодіод — трикутник + риска + стрілки світла
    lx = rx1 + 60
    tri_w = 30
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                 'fill="#fdecea" stroke="%s" stroke-width="2"/>'
                 % (lx, y - 16, lx, y + 16, lx + tri_w, y, POS))
    frags.append(line(lx + tri_w, y - 16, lx + tri_w, y + 16, color=INK, sw=3))   # катодна риска
    # стрілочки випромінювання
    frags.append(arrow(lx + tri_w + 6, y - 8, lx + tri_w + 30, y - 26, color=POS))
    frags.append(arrow(lx + tri_w + 12, y - 2, lx + tri_w + 36, y - 20, color=POS))
    frags.append(text(lx + 6, y + 34, "анод", size=11, color=POS))
    frags.append(text(lx + tri_w, y + 34, "катод", size=11, color=NEG))
    frags.append(line(lx + tri_w, y, lx + tri_w + 40, y, color=INK, sw=2))

    # −/GND справа
    gx = lx + tri_w + 40
    frags.append(minus(gx, y, r=13))
    frags.append(text(gx, y - 26, "0 В", size=14, color=NEG, bold=True))

    # обчислення власною рамкою внизу
    calc = ("живлення 5 В, LED бере 10 мА і «з'їдає» 2 В\n"
            "R = (5 − 2) / 0.01 = 300 Ω  →  беремо 330 Ω з ряду")
    frags.append(fitbox(90, 236, W - 180, 56, calc, size=14, bold=True,
                        fill="#eef6ee", stroke=FIELD))

    render(os.path.join(OUT, "drive.svg"), W, H, *frags,
           title="Світлодіод НЕ вмикають без гасильного резистора")


# ── Фігура 4: стрічка часу кольорів світлодіода (для вставки hist) ────────────
def fig_color_timeline():
    W, H = 860, 470
    frags = []

    # горизонтальна вісь часу
    ax_y = 210
    x0, x1 = 70, W - 70
    ymin, ymax = 1960.0, 2020.0
    def X(yr):
        return x0 + (yr - ymin) / (ymax - ymin) * (x1 - x0)

    frags.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2.2))
    frags.append(arrow(x1 - 2, ax_y, x1 + 8, ax_y, color=INK))
    # десятиліття-мітки
    for yr in [1960, 1970, 1980, 1990, 2000, 2010, 2020]:
        gx = X(yr)
        frags.append(line(gx, ax_y - 5, gx, ax_y + 5, color=MUTED, sw=1.4))
        frags.append(text(gx, ax_y + 22, str(yr), size=12, color=MUTED))

    # події: (рік, підпис-колір, колір-заливка, зверху?, багаторядковий опис)
    def event(yr, dotcol, up, title_lines, cx_override=None):
        gx = X(yr)
        # крапка кольору на осі
        frags.append(circle(gx, ax_y, 8, fill=dotcol, stroke="#333", sw=1.4))
        cy = ax_y - 96 if up else ax_y + 96
        bx = cx_override if cx_override is not None else gx
        b, w, h = textbox(bx, cy, title_lines, size=12, fill="#f7f9fc",
                          stroke="#8a97ab", min_w=118)
        # стійка від осі до рамки (веду повз рамку, не крізь текст)
        edge = cy + h / 2 if up else cy - h / 2
        frags.append(line(gx, ax_y - 8 if up else ax_y + 8, bx, edge,
                          color=MUTED, sw=1.2, dash="3,3"))
        frags.append(b)

    # червоний 1962 — знизу
    event(1962, "#c0392b", False,
          "1962 · ЧЕРВОНИЙ\nГолоняк (GaAsP)\nперший видимий")
    # жовтий/зелений — зверху, зсунуто праворуч, щоб не налазити на червоний
    event(1971, "#e8c400", True,
          "к.1960-х–1970-ті\nЖОВТИЙ, ЗЕЛЕНИЙ\nродинні сплави",
          cx_override=X(1973))
    # синій 1993 — знизу
    event(1993, "#2457d6", False,
          "1990-ті · СИНІЙ\nАкасакі·Амано·Накамура\nнітрид галію (GaN)")
    # білий — зверху, праворуч від синього
    event(1996, "#c9c9c9", True,
          "з СИНЬОГО — БІЛИЙ\nсиній + люмінофор\nсучасне освітлення",
          cx_override=X(2004))
    # Нобель 2014 — окрема мітка знизу праворуч
    event(2014, "#2457d6", False,
          "2014\nНобель із фізики\nза ефективний синій",
          cx_override=X(2014))

    # «провалля» перед синім — дуга з підписом (над віссю, у вільній смузі)
    gap_l, gap_r = X(1971), X(1993)
    arc_y = ax_y - 30
    frags.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="1.6" stroke-dasharray="4,3"/>'
                 % (gap_l, ax_y - 10, (gap_l + gap_r) / 2, arc_y - 14,
                    gap_r, ax_y - 10, MUTED))
    frags.append(text((gap_l + gap_r) / 2, arc_y - 20,
                      "~30 років на впертий нітрид галію", size=12,
                      color=MUTED, italic=True))

    # висновок унизу
    note = ("кожен колір чекав, поки приборкають новий напівпровідник; "
            "синій дався останнім — і саме він відчинив двері до білого світла")
    frags.append(fitbox(60, 420, W - 120, 40, note, size=13,
                        fill="#f4f6f8", stroke=LINE))

    render(os.path.join(OUT, "color-timeline.svg"), W, H, *frags,
           title="Кольори світлодіода приходили ривками — від червоного до білого")


# ── Фігура 5 (math-вставка): навантажувальні прямі й крута крива діода ────────
def fig_load_line():
    W, H = 780, 470
    frags = []
    ox, oy = 120, H - 90          # початок координат
    ax_w, ax_h = W - 220, H - 170
    frags.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))     # вісь напруги
    frags.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))     # вісь струму
    frags.append(text(ox + ax_w, oy + 26, "напруга, В", size=12, color=MUTED, anchor="end"))
    frags.append(text(ox - 4, oy - ax_h - 8, "струм", size=12, color=MUTED, anchor="middle"))

    Vmax = 12.0
    def X(v): return ox + v / Vmax * ax_w
    Imax = 22.0
    def Y(i): return oy - i / Imax * ax_h

    for gv in [0, 3.3, 5, 12]:
        frags.append(line(X(gv), oy, X(gv), oy + 5, color=MUTED, sw=1))
        lab = ("%.1f" % gv).rstrip("0").rstrip(".")
        frags.append(text(X(gv), oy + 20, lab, size=11, color=MUTED))

    # крута крива діода
    Vf = 2.0
    pts = []
    for k in range(0, 300):
        v = Vf - 0.3 + k * 0.006
        i = 0.6 * math.exp((v - Vf) / 0.09)
        if i > Imax:
            pts.append("%.1f,%.1f" % (X(v), Y(Imax)))
            break
        pts.append("%.1f,%.1f" % (X(v), Y(i)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), POS))
    frags.append(text(X(Vf) - 4, Y(Imax) - 8, "крива діода", size=12, color=POS,
                      bold=True, anchor="start"))

    loads = [
        (3.3, "#8a5a00", "3.3 В"),
        (5.0, NEG,       "5 В"),
        (12.0, FIELD,    "12 В"),
    ]
    for Us, col, lab in loads:
        R = (Us - Vf) / 0.011
        i_axis = Us / R
        if i_axis > Imax:
            v_top = Us - Imax * R
            frags.append(line(X(v_top), Y(Imax), X(Us), Y(0), color=col, sw=2))
        else:
            frags.append(line(X(0), Y(i_axis), X(Us), Y(0), color=col, sw=2))
        i_op = (Us - Vf) / R
        frags.append(circle(X(Vf), Y(i_op), 4.5, fill=col, stroke="#ffffff", sw=1.5))
        frags.append(text(X(Us), oy - 9, lab, size=12, color=col, bold=True))

    note = ("більший запас U_жив − Vf →\nположистіша пряма, перетин упоперек →\nтремтіння Vf майже не зсуває струм")
    b, w, h = textbox(ox + ax_w - 168, oy - ax_h + 52, note, size=12,
                      fill="#f4f6f8", stroke=LINE, min_w=280)
    frags.append(b)

    render(os.path.join(OUT, "load-line.svg"), W, H, *frags,
           title="Робоча точка: перетин кривої діода й прямої резистора")


# ── Фігура 6 (math-вставка): послідовний ланцюжок і бюджет напруги ────────────
def fig_series_chain():
    W, H = 780, 380
    frags = []
    y = 128
    x0 = 66
    frags.append(plus(x0, y, r=13))
    frags.append(text(x0, y - 26, "12 В", size=14, color=POS, bold=True))
    frags.append(line(x0 + 13, y, 150, y, color=INK, sw=2))

    rx0 = 150
    step = 11
    zig = "M %.1f %.1f " % (rx0, y)
    for k in range(6):
        dy = -13 if k % 2 == 0 else 13
        zig += "l %d %d " % (step, dy)
    zig += "l 6 %d" % (-13)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (zig, INK))
    rx1 = rx0 + 6 * step + 6
    frags.append(text((rx0 + rx1) / 2, y - 22, "R 390 Ω", size=12, color=INK, bold=True))
    frags.append(text((rx0 + rx1) / 2, y + 28, "6 В", size=12, color=FIELD, bold=True))
    frags.append(line(rx1, y, rx1 + 22, y, color=INK, sw=2))

    lx = rx1 + 22
    tri_w = 26
    gap = 22
    for j in range(3):
        tx = lx + j * (tri_w + gap)
        frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                     'fill="#fdecea" stroke="%s" stroke-width="2"/>'
                     % (tx, y - 13, tx, y + 13, tx + tri_w, y, POS))
        frags.append(line(tx + tri_w, y - 13, tx + tri_w, y + 13, color=INK, sw=3))
        frags.append(arrow(tx + tri_w + 3, y - 7, tx + tri_w + 17, y - 19, color=POS))
        frags.append(text(tx + tri_w / 2, y + 30, "2 В", size=11, color=POS, bold=True))
        if j < 2:
            frags.append(line(tx + tri_w, y, tx + tri_w + gap, y, color=INK, sw=2))
    last = lx + 2 * (tri_w + gap) + tri_w
    frags.append(line(last, y, last + 28, y, color=INK, sw=2))
    gx = last + 28
    frags.append(minus(gx, y, r=13))
    frags.append(text(gx, y - 26, "0 В", size=14, color=NEG, bold=True))

    # стовпчик-бюджет напруги знизу ліворуч
    bx, by = 150, 232
    bw, seg_h = 58, 22
    frags.append(text(bx + bw / 2, by - 10, "бюджет 12 В", size=12, color=INK, bold=True))
    parts = [("2 В — LED", POS, "#fdecea", seg_h),
             ("2 В — LED", POS, "#fdecea", seg_h),
             ("2 В — LED", POS, "#fdecea", seg_h),
             ("6 В — резистор", FIELD, "#eaf6ea", seg_h * 2.0)]
    cy = by
    for lab, col, fill, h in parts:
        frags.append(rect(bx, cy, bw, h, fill=fill, stroke=col, sw=1.6, rx=3))
        frags.append(text(bx + bw + 10, cy + h / 2 + 4, lab, size=12, color=col,
                          anchor="start", bold=True))
        cy += h

    note = ("крізь усі три — ОДИН струм;\nсума Vf = 6 В мусить бути\nменша за живлення 12 В")
    b, w, h = textbox(W - 210, by + 66, note, size=12, fill="#f4f6f8",
                      stroke=LINE, min_w=280)
    frags.append(b)

    render(os.path.join(OUT, "series-chain.svg"), W, H, *frags,
           title="Послідовний ланцюжок: напруги Vf складаються")


# ── Фігура 7 (math-вставка): паралель на спільний резистор — струм-хог ────────
def fig_parallel_hog():
    W, H = 780, 430
    frags = []

    # ── ЛІВА половина: погана схема — спільний резистор ──
    L = 56
    frags.append(text(L + 130, 56, "✗ спільний резистор", size=14, color=POS, bold=True))
    topy = 92
    frags.append(plus(L, topy, r=12))
    frags.append(line(L + 12, topy, L + 56, topy, color=INK, sw=2))
    rx0 = L + 56
    step = 10
    zig = "M %.1f %.1f " % (rx0, topy)
    for k in range(5):
        dy = -11 if k % 2 == 0 else 11
        zig += "l %d %d " % (step, dy)
    zig += "l 5 11"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (zig, INK))
    rx1 = rx0 + 5 * step + 5
    frags.append(text((rx0 + rx1) / 2, topy - 16, "20 мА", size=12, color=INK, bold=True))
    busx = rx1 + 18
    frags.append(line(rx1, topy, busx, topy, color=INK, sw=2))
    frags.append(line(busx, topy, busx, topy + 132, color=INK, sw=2))

    gndy = topy + 176
    leds = [("17 мА", POS, 7.0, 18),
            ("2 мА", MUTED, 2.2, 62),
            ("1 мА", MUTED, 1.8, 106)]
    for cur, col, sw, off in leds:
        bxp = busx + 46
        yy = topy + off
        # branch runs to the right, then LED down
        bxp = busx + 46 + (0 if off == 18 else (36 if off == 62 else 72))
        frags.append(line(busx, yy, bxp, yy, color=INK, sw=1.6))
        cyl = yy + 26
        frags.append(line(bxp, yy, bxp, cyl, color=INK, sw=1.6))
        tw = 11
        frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                     'fill="#fdecea" stroke="%s" stroke-width="2"/>'
                     % (bxp - tw, cyl, bxp + tw, cyl, bxp, cyl + 20, POS))
        frags.append(line(bxp - tw, cyl + 20, bxp + tw, cyl + 20, color=INK, sw=3))
        frags.append(line(bxp, cyl + 20, bxp, gndy, color=INK, sw=1.6))
        frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="%.1f" marker-end="url(#arrow)"/>'
                     % (bxp, yy + 3, bxp, cyl - 3, col, sw))
        frags.append(text(bxp + 15, cyl + 4, cur, size=12, color=col, bold=True, anchor="start"))
    last_bx = busx + 46 + 72
    frags.append(line(busx, gndy, last_bx, gndy, color=INK, sw=2))
    frags.append(minus(busx, gndy, r=11))
    b, w, h = textbox(L + 150, gndy + 48,
                      "розкид Vf → діод із нижчою Vf\nхапає струм, гріється, Vf падає,\nхапає ще → теплова лавина",
                      size=11, fill="#fdecea", stroke=POS, min_w=270)
    frags.append(b)

    # ── ПРАВА половина: правильна схема — свій резистор кожному ──
    Rr = 468
    frags.append(text(Rr + 96, 56, "✓ свій резистор", size=14, color=FIELD, bold=True))
    frags.append(plus(Rr, topy, r=12))
    frags.append(line(Rr + 12, topy, Rr + 196, topy, color=INK, sw=2))
    rxs = [Rr + 44, Rr + 116, Rr + 188]
    for bxp in rxs:
        zy = topy
        zig = "M %.1f %.1f " % (bxp, zy)
        for m in range(4):
            dx = -9 if m % 2 == 0 else 9
            zig += "l %d 9 " % dx
        zig += "l 9 6"
        frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (zig, INK))
        zend = zy + 4 * 9 + 6
        frags.append(line(bxp, zend, bxp, zend + 6, color=INK, sw=1.6))
        cyl = zend + 6
        tw = 11
        frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                     'fill="#eaf6ea" stroke="%s" stroke-width="2"/>'
                     % (bxp - tw, cyl, bxp + tw, cyl, bxp, cyl + 20, FIELD))
        frags.append(line(bxp - tw, cyl + 20, bxp + tw, cyl + 20, color=INK, sw=3))
        frags.append(line(bxp, cyl + 20, bxp, gndy, color=INK, sw=1.6))
        frags.append(text(bxp + 14, cyl + 12, "9 мА", size=11, color=FIELD, bold=True, anchor="start"))
    frags.append(line(rxs[0], gndy, rxs[-1], gndy, color=INK, sw=2))
    frags.append(minus(rxs[0], gndy, r=11))
    b, w, h = textbox(Rr + 108, gndy + 48,
                      "струм кожної гілки тримає\nсвій резистор → розкид Vf\nдає лише ~3 % різниці",
                      size=11, fill="#eaf6ea", stroke=FIELD, min_w=250)
    frags.append(b)

    render(os.path.join(OUT, "parallel-hog.svg"), W, H, *frags,
           title="Паралель на спільний резистор губить світлодіоди")


if __name__ == "__main__":
    fig_anatomy()
    fig_vf_colors()
    fig_drive()
    fig_color_timeline()
    fig_load_line()
    fig_series_chain()
    fig_parallel_hog()
    print("done:", os.listdir(OUT))
