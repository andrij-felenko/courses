# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: компонування — де що стоїть і чому низько й по центру ──────────
def f_layout():
    W, H = 720, 400
    frags = []
    frags.append(text(W/2, 26, "Компонування ровера: вид збоку", size=17, bold=True))

    # рівень землі
    ground_y = 330
    frags.append(line(40, ground_y, W-40, ground_y, color=MUTED, sw=2))
    frags.append(text(W-44, ground_y+18, "ґрунт", size=11, color=MUTED, anchor="end"))

    # рама (корпус)
    fx, fy, fw, fh = 150, 150, 420, 150
    frags.append(rect(fx, fy, fw, fh, fill="#f4f6f8", stroke=LINE, sw=2))

    # колеса
    wheel_r = 30
    wy = ground_y - wheel_r
    for wx in (fx+40, fx+fw-40):
        frags.append(circle(wx, wy, wheel_r, fill="#e8ebef", stroke=INK, sw=2))
        frags.append(circle(wx, wy, 6, fill=INK, stroke=INK, sw=1))
    # опори колесо-рама
    frags.append(line(fx+40, wy-wheel_r, fx+40, fy+fh, color=LINE, sw=2))
    frags.append(line(fx+fw-40, wy-wheel_r, fx+fw-40, fy+fh, color=LINE, sw=2))

    # батарея — важка, низько й по центру
    bx, bw, bh = fx+fw/2-70, 140, 46
    by = fy+fh-bh-14
    frags.append(rect(bx, by, bw, bh, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(bx+bw/2, by+bh/2+5, "батарея", size=14, color=NEG, bold=True))

    # плата керування — легка, вище
    frags.append(rect(fx+30, fy+18, 150, 34, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(text(fx+105, fy+40, "плата + давачі", size=12, color=POS))

    # корисне навантаження
    frags.append(rect(fx+fw-190, fy+18, 160, 34, fill="#eafaf0", stroke=FIELD, sw=1.5))
    frags.append(text(fx+fw-110, fy+40, "навантаження", size=12, color=FIELD))

    # центр мас — низько
    cmx, cmy = fx+fw/2, by+bh/2+4
    frags.append(circle(cmx, cmy, 9, fill="#fff", stroke=INK, sw=2))
    frags.append(line(cmx-9, cmy, cmx+9, cmy, color=INK, sw=2))
    frags.append(line(cmx, cmy-9, cmx, cmy+9, color=INK, sw=2))
    frags.append(text(cmx, cmy+30, "центр мас — низько й між осями", size=12, bold=True))

    # висота ЦМ
    frags.append(line(fx-24, cmy, fx-24, ground_y, color=MUTED, sw=1.2, dash="4 3"))
    frags.append(text(fx-30, (cmy+ground_y)/2, "h", size=13, color=MUTED, anchor="end", italic=True))

    render(os.path.join(OUT, 'layout.svg'), W, H, *frags)


# ── Фігура 2: сили на схилі — звідки береться попит на момент ────────────────
def f_slope():
    import math
    W, H = 720, 420
    frags = []
    frags.append(text(W/2, 26, "Ровер на схилі: що тягне його назад", size=17, bold=True))

    # схил
    ax, ay = 90, 360          # нижня точка схилу
    ang = 26 * math.pi/180
    L = 500
    bx, by = ax + L*math.cos(ang), ay - L*math.sin(ang)
    # трикутник схилу
    frags.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#eef1f4" stroke="%s" stroke-width="2"/>' % (ax, ay, bx, by, bx, ay, LINE))
    # кут
    frags.append(text(ax+70, ay-10, "α", size=15, italic=True, bold=True))

    # ровер (прямокутник на схилі) — абсолютні точки, без transform/негативів
    cx, cy = ax + 250*math.cos(ang), ay - 250*math.sin(ang)
    rw, rh = 96, 50
    ux, uy = math.cos(ang), -math.sin(ang)      # уздовж схилу (вгору)
    nx, ny = math.sin(ang), math.cos(ang)       # нормаль до схилу (вгору від поверхні)
    # чотири кути корпусу над поверхнею
    def pt(along, up):
        return (cx + along*ux + up*nx, cy + along*uy + up*ny)
    p1 = pt(-rw/2, 8);  p2 = pt(rw/2, 8)
    p3 = pt(rw/2, 8+rh); p4 = pt(-rw/2, 8+rh)
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#f4f6f8" stroke="%s" stroke-width="2"/>' % (
        p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1], INK))
    w1 = pt(-rw/2+18, 6); w2 = pt(rw/2-18, 6)
    frags.append(circle(w1[0], w1[1], 14, fill="#e8ebef", stroke=INK, sw=2))
    frags.append(circle(w2[0], w2[1], 14, fill="#e8ebef", stroke=INK, sw=2))

    # вектори сили від центра мас ровера (середина корпусу)
    mid = pt(0, 8+rh/2)
    ox, oy = mid[0], mid[1]
    frags.append(circle(ox, oy, 4, fill=INK, stroke=INK))
    # повна вага вниз
    gy = oy + 120
    frags.append(arrow(ox, oy, ox, gy, color=INK, sw=2.4))
    frags.append(text(ox+14, gy-6, "m·g", size=13, italic=True))
    # складова вздовж схилу (тягне назад-вниз)
    comp = 120*math.sin(ang)
    sx = ox - comp*math.cos(ang)
    sy = oy + comp*math.sin(ang)
    frags.append(arrow(ox, oy, sx, sy, color=POS, sw=2.6))
    frags.append(text(sx-8, sy+18, "m·g·sin α", size=13, color=POS, bold=True, anchor="end"))

    # потрібна тяга коліс — угору вздовж схилу
    tx = ox + 130*math.cos(ang)
    ty = oy - 130*math.sin(ang)
    frags.append(arrow(ox, oy, tx, ty, color=FIELD, sw=2.6))
    frags.append(text(tx+6, ty-4, "тяга коліс", size=13, color=FIELD, bold=True))

    # формула-висновок унизу
    body, bw, bh = textbox(W/2, 398, "щоб їхати вгору: тяга ≥ m·g·sin α  +  опір кочення",
                           size=13, bold=True, fill="#eafaf0", stroke=FIELD)
    frags.append(body)

    render(os.path.join(OUT, 'slope.svg'), W, H, *frags)


# ── Фігура 3: куди дівається енергія батареї ────────────────────────────────
def f_energy():
    W, H = 720, 400
    frags = []
    frags.append(text(W/2, 26, "Куди йдуть ват-години батареї", size=17, bold=True))

    # труба енергії зліва направо
    x0 = 70
    ytop = 66
    total_h = 210
    bar_w = 90
    # вхід
    frags.append(rect(x0, ytop, bar_w, total_h, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(x0+bar_w/2, ytop-10, "батарея", size=13, color=NEG, bold=True))
    frags.append(text(x0+bar_w/2, ytop+total_h+20, "100 %", size=12, color=NEG))

    # відгалуження (частки — приблизні, ілюстративні)
    segs = [
        ("рух (корисне)", 0.55, FIELD, "#eafaf0"),
        ("опір кочення", 0.20, MUTED, "#f0f1f3"),
        ("втрати приводу", 0.15, POS, "#fdecea"),
        ("плата й давачі", 0.10, INK, "#eef1f4"),
    ]
    bx = x0 + bar_w + 120
    y = ytop
    for name, frac, col, fill in segs:
        h = total_h * frac
        seg_h = h - 6 if h > 30 else h
        cy_lbl = y + seg_h/2 + 4
        frags.append(arrow(x0+bar_w+8, y+h/2, bx-6, y+h/2, color=col, sw=2.2))
        frags.append(rect(bx, y, 190, seg_h, fill=fill, stroke=col, sw=1.8))
        frags.append(text(bx+95, cy_lbl, "%s  %d%%" % (name, int(frac*100)),
                          size=12, color=col, bold=True))
        y += h

    # підпис-мораль
    body, bw, bh = textbox(x0+bar_w/2+55, ytop+total_h+62,
                           "тільки зелене рушить ровер —\nрешта гріє мотори, ґрунт і повітря",
                           size=12, fill="#f4f6f8", stroke=LINE)
    frags.append(body)

    render(os.path.join(OUT, 'energy.svg'), W, H, *frags)


# ── Фігура 4 (вставка proj): танкове змішування + стиснення ─────────────────
def f_mix():
    W, H = 720, 380
    frags = []
    frags.append(text(W/2, 26, "Танкове змішування: газ і поворот у два борти", size=16, bold=True))

    # входи ліворуч
    ix = 60
    body, bw, bh = textbox(ix+50, 90, "газ", size=14, bold=True, fill="#eef1f4", stroke=LINE, min_w=90)
    frags.append(body)
    body, bw, bh = textbox(ix+50, 150, "поворот", size=14, bold=True, fill="#eef1f4", stroke=LINE, min_w=90)
    frags.append(body)

    # вузли суматорів
    sx = 300
    ly, ry = 90, 210
    # лівий борт = газ + поворот
    frags.append(circle(sx, ly, 22, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(sx, ly+6, "+", size=26, color=POS, bold=True))
    # правий борт = газ − поворот
    frags.append(circle(sx, ry, 22, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(sx, ry+2, "−", size=26, color=NEG, bold=True))

    # стрілки газ → обидва (з плюсом)
    frags.append(arrow(ix+96, 90, sx-24, ly, color=INK, sw=2))
    frags.append(arrow(ix+96, 96, sx-24, ry-6, color=INK, sw=2))
    # поворот → лівий (+), правий (−)
    frags.append(arrow(ix+96, 150, sx-24, ly+14, color=POS, sw=2))
    frags.append(arrow(ix+96, 156, sx-24, ry-16, color=NEG, sw=2))

    # виходи бортів
    frags.append(text(sx+34, ly-26, "left = газ + поворот", size=12, color=INK, anchor="start"))
    frags.append(text(sx+34, ry+34, "right = газ − поворот", size=12, color=INK, anchor="start"))

    # блок стиснення праворуч
    cx = 560
    frags.append(rect(cx-72, 70, 150, 190, fill="#eafaf0", stroke=FIELD, sw=2))
    frags.append(text(cx, 92, "стиснути", size=13, color=FIELD, bold=True))
    frags.append(text(cx, 110, "обидва разом,", size=12, color=INK))
    frags.append(text(cx, 128, "якщо пік > MAX", size=12, color=INK))
    frags.append(line(cx-56, 142, cx+62, 142, color=MUTED, sw=1))
    frags.append(text(cx, 164, "курс = різниця", size=12, color=INK, bold=True))
    frags.append(text(cx, 182, "бортів →", size=12, color=INK))
    frags.append(text(cx, 200, "її бережемо,", size=12, color=INK))
    frags.append(text(cx, 218, "гучність тиснемо", size=12, color=INK))

    frags.append(arrow(sx+24, ly, cx-74, 120, color=INK, sw=2))
    frags.append(arrow(sx+24, ry, cx-74, 210, color=INK, sw=2))

    body, bw, bh = textbox(W/2, 348,
                           "обрізати ОДИН борт = змінити курс; тиснути ОБИДВА = зберегти курс, збавити хід",
                           size=12, bold=True, fill="#f4f6f8", stroke=LINE)
    frags.append(body)

    render(os.path.join(OUT, 'mix.svg'), W, H, *frags)


# ── Фігура 5 (вставка proj): failsafe — газ у нуль за тишею heartbeat ────────
def f_failsafe():
    W, H = 720, 360
    frags = []
    frags.append(text(W/2, 26, "Failsafe: тиша в каналі глушить газ", size=16, bold=True))

    x0, x1 = 70, 660
    axis_y = 250
    # вісь часу
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2))
    frags.append(text(x1, axis_y+20, "час", size=12, color=MUTED, anchor="end"))

    # позначки серцебиття (пакети команди) — регулярні, тоді обрив
    import math
    last_pkt_x = x0 + 300
    pkt_xs = [x0 + 30 + i*54 for i in range(6)]     # до обриву
    for px in pkt_xs:
        frags.append(line(px, axis_y-8, px, axis_y+8, color=NEG, sw=2))
    last = pkt_xs[-1]
    frags.append(text(pkt_xs[0], axis_y+26, "пакети команди", size=11, color=NEG, anchor="start"))

    # мить обриву
    frags.append(line(last, 70, last, axis_y, color=POS, sw=1.4, dash="5 4"))
    frags.append(text(last, 62, "останній пакет", size=11, color=POS))

    # вікно таймауту
    to_end = last + 150
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" stroke="none"/>' % (last, 80, to_end-last, axis_y-80))
    frags.append(line(to_end, 70, to_end, axis_y, color=POS, sw=1.6))
    frags.append(text((last+to_end)/2, 96, "таймаут", size=12, color=POS, bold=True))
    frags.append(text((last+to_end)/2, 114, "тиші", size=12, color=POS, bold=True))

    # крива газу: тримається, тоді за таймаутом — у нуль
    gy_hi = 150      # рівень «газ тримається на останній команді»
    gy_zero = axis_y # нуль газу = вісь
    pts = "%d,%d %d,%d %d,%d %d,%d" % (x0+20, gy_hi, last, gy_hi, to_end, gy_hi, to_end+2, gy_zero)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pts, FIELD))
    frags.append(text(x0+22, gy_hi-10, "газ", size=13, color=FIELD, bold=True, anchor="start"))
    frags.append(text(to_end+10, gy_hi+4, "останнє відоме", size=11, color=FIELD, anchor="start"))
    frags.append(text(to_end+10, gy_zero-6, "газ = 0 (стоп)", size=12, color=FIELD, bold=True, anchor="start"))

    # підпис-мораль
    body, bw, bh = textbox(W/2, 332,
                           "нема свіжих пакетів довше за таймаут → команда не «застигає», а падає в нуль",
                           size=12, bold=True, fill="#f4f6f8", stroke=LINE)
    frags.append(body)

    render(os.path.join(OUT, 'failsafe.svg'), W, H, *frags)


# ── Фігура (вставка hist): родовід rocker-bogie від Rocky до польоту ─────────
def f_lineage():
    W, H = 760, 440
    frags = []
    frags.append(text(W/2, 26, "Родовід rocker-bogie: від гаража до Марса й Місяця", size=17, bold=True))

    # вертикальна вісь часу
    axis_x = 168
    y0, y1 = 66, 388
    frags.append(line(axis_x, y0, axis_x, y1, color=MUTED, sw=2))

    # вузли: (рік, назва, коротка нотатка, колір крапки)
    nodes = [
        ("1988",       "патент Біклера",        "коромисло-візок, без пружин",     POS),
        ("Rocky 3–7",  "стенди JPL",            "«пантограф», відпрацювання схеми", MUTED),
        ("1997",       "Sojourner",             "Pathfinder — перший на Марсі",     FIELD),
        ("2004",       "Spirit / Opportunity",  "роки замість трьох місяців",       FIELD),
        ("2012",       "Curiosity",             "899 кг, диференціальний брус",     FIELD),
        ("2021",       "Perseverance",          "1025 кг, та сама схема",           FIELD),
        ("2023",       "Pragyan",               "Місяць, ISRO — вже не лише NASA",  NEG),
    ]
    n = len(nodes)
    for i, (yr, name, note, col) in enumerate(nodes):
        y = y0 + (y1 - y0) * i / (n - 1)
        frags.append(circle(axis_x, y, 8, fill="#ffffff", stroke=col, sw=3))
        frags.append(text(axis_x - 20, y + 5, yr, size=13, color=col, bold=True, anchor="end"))
        frags.append(text(axis_x + 24, y + 1, name, size=14, bold=True, anchor="start"))
        frags.append(text(axis_x + 24, y + 18, note, size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'lineage.svg'), W, H, *frags)


if __name__ == '__main__':
    f_layout()
    f_slope()
    f_energy()
    f_mix()
    f_failsafe()
    f_lineage()
    print("ok: layout.svg, slope.svg, energy.svg, mix.svg, failsafe.svg, lineage.svg")
