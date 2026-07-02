# -*- coding: utf-8 -*-
# Фігури для вставки math-bearing-frequencies.md (геометрія підшипника й кінематика
# кочення). Окремий генератор поруч із figs.py, бо файл теми спільний і пишеться
# паралельно; вивід — у той самий ./img/. Запуск:  python figs_bearing.py
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def axes(x0, y0, w, h, xlabel, ylabel):
    s  = line(x0, y0, x0 + w, y0, color=INK, sw=1.6)
    s += line(x0, y0, x0, y0 - h, color=INK, sw=1.6)
    s += text(x0 + w, y0 + 18, xlabel, size=11, color=MUTED, anchor="end")
    if ylabel:
        s += text(x0 - 6, y0 - h - 6, ylabel, size=11, color=MUTED, anchor="middle")
    return s


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — геометрія підшипника: Pd, Bd, β, доріжки, сепаратор
# ════════════════════════════════════════════════════════════════════════════
def fig_bearing_geometry():
    W, H = 760, 430
    cx, cy = 248, 220
    R_out = 160
    R_in  = 76
    R_pitch = (R_out + R_in) / 2
    r_ball = (R_out - R_in) / 2

    body = ""
    body += ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="3"/>'
             % (cx, cy, R_out, INK))
    body += ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (cx, cy, R_out - 13, MUTED))
    body += ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#eef2f7" stroke="%s" stroke-width="3"/>'
             % (cx, cy, R_in, INK))
    body += ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (cx, cy, R_in + 13, MUTED))
    body += text(cx, cy + 5, "вал", size=13, color=MUTED)
    body += ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.4" stroke-dasharray="5 5"/>' % (cx, cy, R_pitch, NEG))

    nb = 9
    for i in range(nb):
        a = 2 * math.pi * i / nb - math.pi / 2
        bx = cx + R_pitch * math.cos(a)
        by = cy + R_pitch * math.sin(a)
        hot = (i == 0)
        body += circle(bx, by, r_ball, fill=("#fdecea" if hot else "#eaf0fd"),
                       stroke=(POS if hot else NEG), sw=2)
    body += text(cx, cy - R_pitch - r_ball - 8, "тіло кочення (Nb штук)", size=11, color=POS, bold=True)

    ax = cx + R_pitch * math.cos(math.radians(38))
    ay = cy + R_pitch * math.sin(math.radians(38))
    body += arrow(cx, cy, ax, ay, color=NEG, sw=2)
    body += text((cx + ax) / 2 + 6, (cy + ay) / 2 - 6, "Pd/2", size=12, color=NEG, anchor="start")

    a2 = 2 * math.pi * 2 / nb - math.pi / 2
    b2x = cx + R_pitch * math.cos(a2)
    b2y = cy + R_pitch * math.sin(a2)
    body += line(b2x - r_ball, b2y, b2x + r_ball, b2y, color=INK, sw=2)
    body += text(b2x + r_ball + 6, b2y + 4, "Bd", size=12, color=INK, anchor="start", bold=True)

    body += text(cx - R_pitch - 6, cy - 6, "сепаратор", size=10.5, color=MUTED, anchor="end")
    body += text(cx - R_pitch - 6, cy + 10, "(тримає кут)", size=9.5, color=MUTED, anchor="end", italic=True)

    px = 562
    body += text(px, 70, "Кут контакту β", size=13, color=INK, bold=True)
    ox, oy = px, 232
    body += line(ox - 72, oy, ox + 72, oy, color=MUTED, sw=1.4, dash="4 4")
    body += text(ox + 76, oy + 4, "радіаль", size=10, color=MUTED, anchor="start")
    bdeg = 20
    ex = ox + 112 * math.cos(math.radians(bdeg))
    ey = oy - 112 * math.sin(math.radians(bdeg))
    body += arrow(ox, oy, ex, ey, color=POS, sw=2.2)
    body += text(ex + 4, ey - 2, "лінія тиску", size=10, color=POS, anchor="start")
    body += ('<path d="M %.1f %.1f A 34 34 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (ox + 34, oy, ox + 34 * math.cos(math.radians(bdeg)),
                oy - 34 * math.sin(math.radians(bdeg)), INK))
    body += text(ox + 44, oy - 12, "β", size=13, color=INK, bold=True)
    body += fitbox(px - 96, 300, 192, 100,
                   "Радіальний (6205):\nβ = 0° → cos β = 1.\nКутовий / упорний:\nβ > 0 → cos β < 1,\nчастоти трохи нижчі.",
                   size=11, fill=FILL, stroke=MUTED)

    render(os.path.join(OUT, "bearing-geometry.svg"), W, H, body,
           title="Чотири числа геометрії, з яких ростуть усі частоти")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — кочення без проковзування: швидкості контактів, чому сепаратор повільний
# ════════════════════════════════════════════════════════════════════════════
def fig_rolling_kinematics():
    W, H = 760, 360
    x0 = 110
    y_out = 250
    y_in = 132
    w = 520
    body = ""

    body += rect(x0, y_out, w, 22, fill="#eef2f7", stroke=INK, sw=2, rx=3)
    body += rect(x0, y_in - 22, w, 22, fill="#eef2f7", stroke=INK, sw=2, rx=3)
    body += text(x0 - 8, y_out + 16, "зовнішня", size=11, color=MUTED, anchor="end")
    body += text(x0 - 8, y_in - 6, "внутрішня", size=11, color=MUTED, anchor="end")

    bx = x0 + w * 0.46
    by = (y_out + y_in) / 2
    r = (y_out - y_in) / 2 - 2
    body += circle(bx, by, r, fill="#fdecea", stroke=POS, sw=2.4)
    body += text(bx, by + 4, "кулька", size=10.5, color=POS)

    body += circle(bx, y_out, 4, fill=INK, stroke=INK, sw=1)
    body += text(bx, y_out + 40, "v = 0", size=12, color=INK, bold=True)
    body += text(bx, y_out + 55, "(нерухомий контакт)", size=9.5, color=MUTED)

    body += circle(bx, y_in, 4, fill=POS, stroke=POS, sw=1)
    body += arrow(bx, y_in, bx + 92, y_in, color=POS, sw=2.4)
    body += text(bx + 97, y_in + 4, "v = vᵢ", size=12, color=POS, anchor="start", bold=True)

    body += arrow(bx, by, bx + 46, by, color=FIELD, sw=2.4)
    body += text(bx + 51, by - 8, "vᵢ/2", size=12, color=FIELD, anchor="start", bold=True)
    body += text(bx, by - r - 10, "центр = середнє двох контактів", size=10.5, color=FIELD)

    tri_x = bx - r - 64
    body += line(tri_x, y_out, tri_x, y_in, color=MUTED, sw=1.4)
    body += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (tri_x, y_out, tri_x - 44, y_in, tri_x, y_in, NEG))
    body += text(tri_x - 48, y_in - 4, "vᵢ", size=11, color=NEG, anchor="end", bold=True)
    body += text(tri_x + 5, y_out + 2, "0", size=11, color=MUTED, anchor="start")
    body += text(tri_x - 22, (y_out + y_in) / 2 + 36, "лінійний", size=9.5, color=MUTED)
    body += text(tri_x - 22, (y_out + y_in) / 2 + 49, "профіль", size=9.5, color=MUTED)

    body += fitbox(x0 + 30, 300, w - 60, 46,
                   "Нема проковзування → швидкість контакту = швидкість доріжки. Центр кульки (а з ним сепаратор) "
                   "рухається із СЕРЕДНЬОЮ двох контактів — тому сепаратор завжди повільніший за вал.",
                   size=11, fill="#f0f7f2", stroke=FIELD)

    render(os.path.join(OUT, "rolling-kinematics.svg"), W, H, body,
           title="Кочення без проковзування: звідки субсинхронний сепаратор")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — лінійка множників: де сідають чотири частоти відносно обертів
# ════════════════════════════════════════════════════════════════════════════
def fig_multiplier_ruler():
    W, H = 760, 300
    x0, y0 = 60, 175
    w_ax = 650
    mmax = 6.0
    body = axes(x0, y0, w_ax, 110, "× частоти обертання fr", "")

    def fx(m): return x0 + (m / mmax) * w_ax
    for m in range(0, 7):
        xc = fx(m)
        body += line(xc, y0, xc, y0 + 5, color=MUTED, sw=1)
        body += text(xc, y0 + 19, "%d×" % m, size=10, color=MUTED)

    marks = [
        (0.397, "FTF",   "0.40×", NEG,   72),
        (1.0,   "оберти","1×",    MUTED, 38),
        (2.322, "BSF",   "2.32×", FIELD, 72),
        (3.572, "BPFO",  "3.57×", POS,   46),
        (4.644, "2×BSF", "4.64×", FIELD, 98),
        (5.428, "BPFI",  "5.43×", POS,   46),
    ]
    for m, lbl, mul, col, up in marks:
        xc = fx(m)
        body += line(xc, y0, xc, y0 - 80, color=col, sw=(1.4 if col == MUTED else 2),
                     dash=("4 4" if col == MUTED else None))
        body += circle(xc, y0 - 80, 4, fill=col, stroke=col, sw=1)
        body += text(xc, y0 - up - 6, lbl, size=11, color=col, bold=(col != MUTED))
        body += text(xc, y0 - up + 8, mul, size=9.5, color=col)

    body += text(x0, 52, "Підшипник SKF 6205: Nb = 9, Bd = 7.938, Pd = 38.5, β = 0", size=12,
                 color=INK, bold=True, anchor="start")
    body += text(x0, 68, "усі чотири — НЕЦІЛІ множники обертів (на відміну від дисбалансу 1× і розцентрування 2×)",
                 size=10.5, color=MUTED, anchor="start")
    render(os.path.join(OUT, "multiplier-ruler.svg"), W, H, body,
           title="Чотири нецілі частоти на лінійці обертів")


if __name__ == "__main__":
    fig_bearing_geometry()
    fig_rolling_kinematics()
    fig_multiplier_ruler()
    print("OK: bearing figures written to", OUT)
