# -*- coding: utf-8 -*-
"""Фігури до статті «Стратегії комутації BLDC-мотора».
  six-step.svg    — шість секторів по 60°, пара фаз у кожному, трапеція
  zero-cross.svg  — вільна фаза як генератор; перехід через нуль зворотної ЕРС
  strategies.svg  — трапеція → синус → FOC (вектор поля на 90°)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

A_COL = "#c0392b"   # фаза A / «+» гаряче
B_COL = "#2457d6"   # фаза B / «−»
C_COL = "#27ae60"   # фаза C / поле-зелене
GREY  = "#9aa4af"   # вільна фаза


def poly(pts, stroke, sw=2.4, fill="none"):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return '<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>' % (d, fill, stroke, sw)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Шість кроків: 6 секторів × (яка фаза +, −, вільна) + трапеція фази A
# ─────────────────────────────────────────────────────────────────────────────
def fig_six_step():
    W, H = 820, 470
    f = [text(W / 2, 30, "Шість кроків: 60° на сектор, дві фази ввімкнені, третя вільна", size=17, bold=True)]

    # таблиця секторів: підпис ролі кожної фази у 6 секторах
    # роль: '+', '-', '~' (вільна)
    roles = {
        'A': ['+', '+', '~', '-', '-', '~'],
        'B': ['~', '-', '-', '~', '+', '+'],
        'C': ['-', '~', '+', '+', '~', '-'],
    }
    colcol = {'A': A_COL, 'B': B_COL, 'C': C_COL}
    sym = {'+': '+', '-': '−', '~': 'вільна'}

    x0, y0 = 70, 66
    cw, ch = 118, 34
    # заголовки секторів
    for s in range(6):
        cx = x0 + cw / 2 + s * cw
        f.append(text(cx, y0 - 8, "сектор %d" % (s + 1), size=12, bold=True, color=MUTED))
        f.append(text(cx, y0 + 8, "%d°–%d°" % (s * 60, (s + 1) * 60), size=10, color=MUTED))
    # рядки фаз
    ry = y0 + 22
    for ph in ['A', 'B', 'C']:
        f.append(text(x0 - 18, ry + ch / 2 + 5, "фаза %s" % ph, size=12, bold=True, color=colcol[ph], anchor="end"))
        for s in range(6):
            x = x0 + s * cw
            r = roles[ph][s]
            if r == '+':
                fill, col, lab = "#fdecea", A_COL, "+"
            elif r == '-':
                fill, col, lab = "#eaf0fd", B_COL, "−"
            else:
                fill, col, lab = "#f0f2f4", GREY, "вільна"
            f.append(rect(x, ry, cw - 6, ch, fill=fill, stroke=col, sw=1.6))
            f.append(text(x + (cw - 6) / 2, ry + ch / 2 + 5, lab, size=13, bold=True, color=col))
        ry += ch + 6

    # трапеція фази A унизу, вирівняна під сектори
    gy = ry + 40
    gh = 70
    f.append(text(x0 - 18, gy - gh / 2 + 5, "напруга", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 18, gy - gh / 2 + 21, "фази A", size=11, color=A_COL, anchor="end", bold=True))
    # осі
    f.append(line(x0, gy, x0 + 6 * cw, gy, color=MUTED, sw=1.2, dash="4 4"))  # нуль
    # трапеція: A = + два сектори, спад, − два сектори, підйом
    top, bot = gy - gh / 2, gy + gh / 2
    pts = []
    # sector0: +top, sector1:+top, sector2: спад top->bot, sector3:-bot, sector4:-bot, sector5: підйом bot->top
    xs = [x0 + i * cw for i in range(7)]
    pts = [(xs[0], top), (xs[2], top), (xs[3], bot), (xs[5], bot), (xs[6], top)]
    f.append(poly(pts, A_COL, sw=2.6))
    # вертикальні розділювачі секторів
    for i in range(7):
        f.append(line(xs[i], y0 + 16, xs[i], gy + gh / 2 + 4, color="#dfe4ea", sw=1))
    f.append(text(x0 + 3 * cw, gy + gh / 2 + 24, "пласкі вершини трапеції → поле стрибає, а не крутиться плавно", size=11, color=MUTED))

    render(os.path.join(IMG, "six-step.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Zero-crossing: дві фази несуть струм, третя вільна = генератор; ЕРС у нулі
# ─────────────────────────────────────────────────────────────────────────────
def fig_zero_cross():
    W, H = 820, 430
    f = [text(W / 2, 30, "Безсенсорна комутація: вільна фаза генерує, її ЕРС перетинає нуль", size=16, bold=True)]

    # ліворуч: мотор із трьома фазами; A→+, B→−, C вільна (слухаємо)
    cx, cy, R = 175, 210, 78
    f.append(circle(cx, cy, R, fill="#eef2f7", stroke=LINE, sw=2))
    f.append(circle(cx, cy, 30, fill="#f7e9ea", stroke=A_COL, sw=1.6))
    f.append(text(cx, cy - 4, "ротор", size=11, bold=True))
    f.append(text(cx, cy + 12, "N–S", size=11, color=MUTED))
    # три виводи 120°
    outs = {'A': (-90, A_COL, "+"), 'B': (30, B_COL, "−"), 'C': (150, GREY, "вільна")}
    for ph, (ang, col, tag) in outs.items():
        a = math.radians(ang)
        ex, ey = cx + (R + 34) * math.cos(a), cy + (R + 34) * math.sin(a)
        wx, wy = cx + R * math.cos(a), cy + R * math.sin(a)
        f.append(line(wx, wy, ex, ey, color=col, sw=2.6))
        f.append(circle(ex, ey, 4, fill=col, stroke=col))
        f.append(text(ex + (16 if math.cos(a) >= 0 else -16), ey + 5,
                      "%s: %s" % (ph, tag), size=12, bold=True, color=col,
                      anchor="start" if math.cos(a) >= 0 else "end"))
    f.append(text(cx, cy + R + 42, "дві фази ведуть струм, третя висить вільна", size=11, color=MUTED))

    # праворуч: графік ЕРС вільної фази з переходом через нуль
    gx, gy, gw, gh = 430, 130, 330, 150
    f.append(text(gx + gw / 2, gy - 14, "зворотна ЕРС вільної фази (фаза C)", size=13, bold=True, color=C_COL))
    midy = gy + gh / 2
    f.append(line(gx, midy, gx + gw, midy, color=MUTED, sw=1.2, dash="5 4"))          # нуль
    f.append(text(gx - 8, midy + 4, "0", size=11, color=MUTED, anchor="end"))
    f.append(line(gx, gy, gx, gy + gh, color="#dfe4ea", sw=1))                          # вісь часу
    # синусоїдна ділянка ЕРС, що йде через нуль по центру
    pts = []
    for i in range(0, 101):
        t = i / 100.0
        xx = gx + t * gw
        # проста синусоїда, що перетинає нуль у центрі
        yy = midy - (gh / 2 - 8) * math.sin((t - 0.5) * math.pi)
        pts.append((xx, yy))
    f.append(poly(pts, C_COL, sw=2.6))
    # точка переходу через нуль
    zx = gx + 0.5 * gw
    f.append(circle(zx, midy, 5, fill="#ffffff", stroke=C_COL, sw=2.4))
    f.append(line(zx, gy + 4, zx, gy + gh - 4, color=C_COL, sw=1.2, dash="3 3"))
    box, bw, bh = textbox(zx, gy - 2, "перехід\nчерез нуль", size=11, color=C_COL, bold=True, fill="#eafaf0", stroke=C_COL)
    # box центрований — зсунемо у видиме місце над точкою
    f.append(box)

    # позначка «+30° → комутація» праворуч від нуля
    kx = gx + 0.5 * gw + 0.25 * gw
    f.append(line(kx, gy + 6, kx, gy + gh - 6, color=INK, sw=1.4))
    f.append(text(kx, gy + gh + 22, "+30° (пів сектора)", size=11, bold=True, color=INK))
    f.append(text(kx, gy + gh + 38, "→ мить перемкнути ключі", size=11, color=MUTED))
    f.append(arrow(zx + 4, gy + gh + 14, kx - 4, gy + gh + 14, color=INK, sw=1.6))
    f.append(text((zx + kx) / 2, gy + gh + 8, "чекаємо", size=10, color=MUTED))

    render(os.path.join(IMG, "zero-cross.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Три стратегії: трапеція → синус → FOC
# ─────────────────────────────────────────────────────────────────────────────
def fig_strategies():
    W, H = 840, 400
    f = [text(W / 2, 30, "Три стратегії комутації: від грубих сходинок до вектора поля", size=16, bold=True)]

    panels = [
        (60,  "Трапеція", "6 сходинок, 2 фази", "просто · гуде на малих", A_COL),
        (350, "Синус",    "3 плавні синусоїди", "тихо · рівне поле",       B_COL),
        (640, "FOC",      "вектор поля 90°",    "макс. момент · від 0 об", C_COL),
    ]
    pw, ph_ = 180, 150
    py = 70
    for px, title, sub, tag, col in panels:
        f.append(rect(px, py, pw, ph_, fill="#fbfcfd", stroke="#d5dbe1", sw=1.4))
        f.append(text(px + pw / 2, py + 24, title, size=15, bold=True, color=col))
        # зона малюнка
        ax, ay, aw, ah = px + 16, py + 40, pw - 32, ph_ - 60
        midy = ay + ah / 2

        if title == "Трапеція":
            # східчаста хвиля (грубе поле)
            f.append(line(ax, midy, ax + aw, midy, color="#e3e7eb", sw=1))
            steps = [1, 1, 0, -1, -1, 0]
            seg = aw / 6.0
            pts = []
            for i, s in enumerate(steps):
                yy = midy - s * (ah / 2 - 6)
                pts.append((ax + i * seg, yy))
                pts.append((ax + (i + 1) * seg, yy))
            f.append(poly(pts, A_COL, sw=2.4))
        elif title == "Синус":
            f.append(line(ax, midy, ax + aw, midy, color="#e3e7eb", sw=1))
            for k, cc in enumerate([A_COL, B_COL, C_COL]):
                pts = []
                for i in range(0, 61):
                    t = i / 60.0
                    xx = ax + t * aw
                    yy = midy - (ah / 2 - 6) * math.sin(2 * math.pi * t + k * 2 * math.pi / 3)
                    pts.append((xx, yy))
                f.append(poly(pts, cc, sw=1.8))
        else:  # FOC: ротор + вектор поля на 90°
            ccx, ccy, rr = ax + aw / 2, midy, ah / 2 - 6
            f.append(circle(ccx, ccy, rr, fill="#eef7f0", stroke="#cfe0d5", sw=1.4))
            # напрям ротора (вправо-вгору)
            ra = math.radians(-25)
            rx, ry = ccx + rr * 0.7 * math.cos(ra), ccy + rr * 0.7 * math.sin(ra)
            f.append(arrow(ccx, ccy, rx, ry, color=A_COL, sw=2.2))
            f.append(text(rx + 6, ry + 4, "ротор", size=10, bold=True, color=A_COL, anchor="start"))
            # поле статора на 90° уперед
            fa = ra - math.radians(90)
            fx, fy = ccx + rr * 0.9 * math.cos(fa), ccy + rr * 0.9 * math.sin(fa)
            f.append(arrow(ccx, ccy, fx, fy, color=C_COL, sw=2.4))
            f.append(text(fx - 4, fy - 6, "поле", size=10, bold=True, color=C_COL, anchor="middle"))
            f.append(text(ccx, ccy + rr + 14, "90°", size=11, bold=True, color=INK))

        f.append(text(px + pw / 2, py + ph_ + 22, sub, size=11, bold=True))
        f.append(text(px + pw / 2, py + ph_ + 40, tag, size=10, color=MUTED))

    # стрілка «складніше →» під панелями
    ay2 = py + ph_ + 66
    f.append(arrow(90, ay2, W - 90, ay2, color=MUTED, sw=1.6))
    f.append(text(W / 2, ay2 - 8, "дедалі більше обчислень і точнішого знання кута ротора →", size=11, color=MUTED))

    render(os.path.join(IMG, "strategies.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Таблиця шести кроків як коло: пара ключів у кожному секторі, вільна фаза,
#    напрям струму, «міняється рівно один ключ на крок» (для вставки proj-)
# ─────────────────────────────────────────────────────────────────────────────
def fig_step_table():
    W, H = 760, 620
    f = [text(W / 2, 30, "Таблиця шести кроків: пара ключів у кожному з 60°-секторів", size=16, bold=True)]

    cx, cy, R = W / 2, 320, 180

    # Дані шести секторів: (верхній ключ, нижній ключ, вільна фаза, напрям струму)
    steps = [
        ("AH", "CL", "B", "A→C"),
        ("AH", "BL", "C", "A→B"),
        ("CH", "BL", "A", "C→B"),
        ("CH", "AL", "B", "C→A"),
        ("BH", "AL", "C", "B→A"),
        ("BH", "CL", "A", "B→C"),
    ]
    col_of = {"A": A_COL, "B": B_COL, "C": C_COL}

    # межі секторів (радіальні лінії), сектор i займає [i*60, (i+1)*60)
    # кут малюємо від верху за годинниковою: 0° угорі
    def ang(a_deg):
        return math.radians(a_deg - 90.0)

    # заливка секторів світлим + радіальні межі
    for i in range(6):
        a0, a1 = ang(i * 60), ang((i + 1) * 60)
        x0o, y0o = cx + R * math.cos(a0), cy + R * math.sin(a0)
        x1o, y1o = cx + R * math.cos(a1), cy + R * math.sin(a1)
        f.append('<path d="M %.1f %.1f L %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f Z" '
                 'fill="%s" stroke="#dfe4ea" stroke-width="1.2"/>'
                 % (cx, cy, x0o, y0o, R, R, x1o, y1o,
                    "#fbfcfd" if i % 2 == 0 else "#f2f5f8"))

    # центральне коло-ротор + стрілка «вперед»
    f.append(circle(cx, cy, 30, fill="#eef2f7", stroke=LINE, sw=1.6))
    f.append(text(cx, cy - 2, "ротор", size=11, bold=True))
    f.append(text(cx, cy + 13, "→ вперед", size=9, color=MUTED))
    # дуга напряму обходу
    aa0, aa1 = ang(20), ang(40)
    f.append('<path d="M %.1f %.1f A 52 52 0 0 1 %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2" marker-end="url(#arrow)"/>'
             % (cx + 52 * math.cos(aa0), cy + 52 * math.sin(aa0),
                cx + 52 * math.cos(aa1), cy + 52 * math.sin(aa1), MUTED))

    # підписи в кожному секторі: пара ключів, вільна фаза, струм
    for i, (hi, lo, free, cur) in enumerate(steps):
        am = ang(i * 60 + 30)          # середина сектора
        # текст трохи ближче до обода
        tr = R * 0.66
        tx, ty = cx + tr * math.cos(am), cy + tr * math.sin(am)
        f.append(text(tx, ty - 20, "сектор %d" % (i + 1), size=11, bold=True, color=INK))
        # верхній ключ (гарячий колір фази) + нижній
        hcol = col_of[hi[0]]
        lcol = col_of[lo[0]]
        f.append(text(tx, ty - 3, "%s + %s" % (hi, lo), size=13, bold=True, color=INK))
        f.append(text(tx, ty + 14, "%s→%s" % (hi, "+"), size=9, color=hcol, anchor="end"))
        f.append(text(tx, ty + 14, "  %s→%s" % (lo, "−"), size=9, color=lcol, anchor="start"))
        f.append(text(tx, ty + 30, "вільна: %s" % free, size=10, color=GREY))
        # позначка переходу «міняється 1 ключ» на межі до наступного сектора
        ab = ang((i + 1) * 60)
        dot_x, dot_y = cx + R * math.cos(ab), cy + R * math.sin(ab)
        mx = cx + (R + 20) * math.cos(ab)
        my = cy + (R + 20) * math.sin(ab)
        # який ключ змінюється між i та i+1
        nxt = steps[(i + 1) % 6]
        changed = nxt[0] if nxt[0] != hi else nxt[1]
        f.append(circle(dot_x, dot_y, 3.2, fill=INK, stroke=INK))
        # горизонтальні межі — start/end від знака cos; майже вертикальні — по центру
        c = math.cos(ab)
        if abs(c) < 0.2:
            anc, off = "middle", (-8 if math.sin(ab) < 0 else 16)
            f.append(text(mx, my + off, "→%s" % changed, size=9, color=MUTED, anchor=anc))
        else:
            anc = "start" if c >= 0 else "end"
            f.append(text(mx, my + 4, "→%s" % changed, size=9, color=MUTED, anchor=anc))

    # легенда-нитка внизу (два рядки, читомий шрифт — не втискаємо в один)
    ly = cy + R + 58
    f.append(fitbox(70, ly, W - 140, 52,
                    "На межі кожного сектора змінюється рівно ОДИН ключ, чергуючись між\n"
                    "верхньою й нижньою половиною мосту — ознака правильної послідовності.",
                    size=12, fill="#f7fbff", stroke="#cfe0ee"))

    render(os.path.join(IMG, "step-table.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Часова лінія FOC (для вставки hist-): 1929 Парк → 1968 Гассе → 1971/73
#    Блашке → 1985 Леонгард; праворуч — ворота 1980-х: великі приводи → масові
# ─────────────────────────────────────────────────────────────────────────────
def fig_foc_timeline():
    W, H = 1000, 540
    ACC = "#8e44ad"   # акцент історії (фіолетовий — окремо від фаз)
    f = [text(W / 2, 30, "Півстоліття від ідеї до дешевого чипа: народження векторного керування",
              size=16, bold=True)]

    # ── горизонтальна вісь часу ──
    ax0, ax1 = 150, 650
    spine = 150
    f.append(line(ax0, spine, ax1 + 14, spine, color=INK, sw=2))
    f.append(arrow(ax1, spine, ax1 + 14, spine, color=INK, sw=2))
    f.append(text(ax1 + 20, spine + 5, "час", size=11, color=MUTED, anchor="start"))

    # чотири віхи: (частка по осі, рік, заголовок, підзаголовок, місце)
    nodes = [
        (0.04, "1929", "Перетворення Парка", "математика для\nрозрахунку, не керування", "США · GE"),
        (0.36, "1968", "Карл Гассе", "непрямий метод\n(через ковзання)", "Дармштадт"),
        (0.64, "1971", "Фелікс Блашке", "прямий метод; патент US,\nназва «Transvektor»", "Siemens · Ерланген"),
        (0.94, "1985", "Вернер Леонгард", "підручник; практична\nзрілість приводу", "Брауншвейг"),
    ]
    up = True
    for frac, year, title, sub, place in nodes:
        x = ax0 + frac * (ax1 - ax0)
        # вузол на осі + рік
        f.append(circle(x, spine, 6, fill=ACC, stroke=ACC))
        f.append(text(x, spine - 12 if not up else spine + 20, year, size=15, bold=True, color=ACC))
        # картка з підписом — над або під віссю по черзі
        lines = [title] + sub.split("\n") + [place]
        # ширина під найдовший рядок
        boxy = spine - 96 if up else spine + 44
        box, bw, bh = textbox(x, boxy + 34, "\n".join(lines), size=11,
                              fill="#f6effa", stroke=ACC, sw=1.4, min_w=150)
        f.append(box)
        # ніжка від осі до картки
        legy0 = spine - 6 if up else spine + 6
        legy1 = boxy + 34 + (bh / 2 if up else -bh / 2)
        f.append(line(x, legy0, x, legy1, color=ACC, sw=1.2, dash="3 3"))
        up = not up

    # підпис під смугою віх
    f.append(text((ax0 + ax1) / 2, spine + 150,
                  "ідея → застосування → зрілість: винахід шарами, а не спалахом",
                  size=11, color=MUTED, italic=True))

    # ── права частина: ворота мікропроцесора 1980-х ──
    gx = 740
    f.append(line(gx - 20, 70, gx - 20, H - 60, color="#dfe4ea", sw=1.4, dash="6 5"))

    # верх: до 1980-х — лише великі приводи
    b1, w1, h1 = textbox(gx + 108, 130,
                         "до 1980-х:\nобчислювач — ціла шафа\n→ лише ВЕЛИКІ промислові\nасинхронні приводи",
                         size=11, fill="#fbeeee", stroke=A_COL, sw=1.4)
    f.append(b1)

    # ворота — мікропроцесор
    gate, gw, gh = textbox(gx + 108, 268,
                          "злам 1970–80-х:\nдешевий мікропроцесор і DSP\nз апаратним множенням",
                          size=11, fill="#fff6e6", stroke="#d98c00", sw=1.8, bold=True)
    f.append(gate)

    # низ: після — масові дрібні мотори
    b2, w2, h2 = textbox(gx + 108, 410,
                        "після:\nПарк туди-назад — на ОДНОМУ чипі\n→ FOC сходить на МАСОВІ\nдрібні мотори (ESC)",
                        size=11, fill="#eafaf0", stroke=C_COL, sw=1.4)
    f.append(b2)

    # стрілки вниз крізь ворота
    f.append(arrow(gx + 108, 130 + h1 / 2 + 2, gx + 108, 268 - gh / 2 - 2, color=MUTED, sw=1.8))
    f.append(arrow(gx + 108, 268 + gh / 2 + 2, gx + 108, 410 - h2 / 2 - 2, color=MUTED, sw=1.8))

    render(os.path.join(IMG, "foc-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_six_step()
    fig_zero_cross()
    fig_strategies()
    fig_step_table()
    fig_foc_timeline()
    print("OK: six-step.svg, zero-cross.svg, strategies.svg, step-table.svg, foc-timeline.svg")
