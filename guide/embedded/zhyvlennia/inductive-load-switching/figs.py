# -*- coding: utf-8 -*-
"""Фігури для статті inductive-load-switching («Комутація індуктивного навантаження»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── kickback: чому розмикання котушки народжує сплеск ─────────────────────────
# Ідея: показати причинно-наслідковий ланцюг в одному кадрі — поки ключ
# замкнений, у полі сидить ½LI²; розімкнули за наносекунди → di/dt велике →
# V=L·di/dt підскакує вище живлення доти, доки не проб'є ключ.
def fig_kickback():
    W, H = 760, 360
    p = []

    # ── ліворуч: коло «джерело — котушка — ключ» ──
    Vx = 120
    p.append(text(Vx, 60, "+V", size=14, color=POS, bold=True))
    p.append(line(Vx, 70, Vx, 110, color=INK, sw=2))
    # котушка (символ — три дужки)
    cy0 = 110
    p.append(line(Vx, cy0, Vx, cy0 + 6, color=INK, sw=2))
    for i in range(3):
        p.append('<path d="M %.1f %.1f a 9 9 0 1 1 0 18" fill="none" stroke="%s" '
                 'stroke-width="2"/>' % (Vx, cy0 + 6 + i * 18, INK))
    p.append(text(Vx + 22, cy0 + 30, "L", size=15, color=INK, anchor="start", bold=True, italic=True))
    p.append(line(Vx, cy0 + 60, Vx, cy0 + 90, color=INK, sw=2))
    # вузол-ключ
    nodeY = cy0 + 90
    p.append(circle(Vx, nodeY, 4, fill=INK, stroke=INK, sw=1))
    # ключ — розімкнений (рисочка під кутом)
    p.append(line(Vx, nodeY, Vx, nodeY + 14, color=INK, sw=2))
    p.append(line(Vx, nodeY + 14, Vx + 20, nodeY - 2, color=POS, sw=2.4))
    p.append(line(Vx, nodeY + 34, Vx, nodeY + 52, color=INK, sw=2))
    p.append(text(Vx + 26, nodeY + 18, "ключ", size=11, color=POS, anchor="start", bold=True))
    p.append(text(Vx + 26, nodeY + 32, "розімкнувся", size=10, color=POS, anchor="start"))
    # земля
    gy = nodeY + 52
    p.append(line(Vx - 14, gy, Vx + 14, gy, color=INK, sw=2))
    p.append(line(Vx - 9, gy + 5, Vx + 9, gy + 5, color=INK, sw=1.6))
    p.append(line(Vx - 4, gy + 10, Vx + 4, gy + 10, color=INK, sw=1.2))

    # запасена енергія — плашка біля котушки
    eb, _, _ = textbox(Vx + 110, cy0 + 30, "у полі сидить\nW = ½·L·I²",
                       size=12, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.6)
    p.append(eb)
    p.append(arrow(Vx + 60, cy0 + 30, Vx + 40, cy0 + 30, color=FIELD, sw=1.6))

    # ── праворуч: ланцюг наслідків ──
    bx = 470
    steps = [
        ("струм мусить текти далі", "котушка не дає йому обірватися", POS, "#fdecea"),
        ("шлях обірвано за ~нс", "di/dt — величезне", "#b8860b", "#fdf6e3"),
        ("V = L · di/dt", "підскакує до сотень вольтів", POS, "#fdecea"),
        ("пробій ключа", "напруга шукає, де проскочити", NEG, "#eef4ff"),
    ]
    sy = 80
    sh = 64
    for i, (head, body, col, fill) in enumerate(steps):
        yy = sy + i * sh
        b, _, _ = textbox(bx, yy, head + "\n" + body, size=11, color=col,
                          fill=fill, stroke=col, sw=1.6, min_w=290)
        p.append(b)
        if i < len(steps) - 1:
            p.append(arrow(bx, yy + 22, bx, yy + sh - 22, color=MUTED, sw=1.8))

    p.append(text(W / 2, H - 16,
                  "що різкіше розмикання, то більше di/dt — і то вищий сплеск; "
                  "уся енергія поля мусить кудись піти",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "kickback.svg"), W, H, *p,
           title="Розмикання котушки: енергія поля вибиває сплеск напруги")


# ── clamp-zoo: чотири способи дати енергії безпечний шлях ─────────────────────
# Ідея: одна точка ввімкнення — і п'ять стандартних рішень, кожне зі своїм
# компромісом «напруга фіксації ↔ швидкість гасіння ↔ складність».
def fig_clamp_zoo():
    W, H = 940, 380
    p = []
    cards = [
        (140, "гасний діод", "Vкл ≈ V + 0.7",
         "найпростіше;\nале гасить ПОВІЛЬНО\n(струм тягнеться)", FIELD, "#eafaf0"),
        (370, "діод + Зенер / TVS", "Vкл = V + Vz",
         "швидке гасіння;\nфіксація вища, але\nкерована й безпечна", NEG, "#eef4ff"),
        (600, "RC / RCD-снабер", "поглинає dV/dt",
         "гасить дзвін і викид;\nтреба підібрати R, C\nпід саме це коло", "#b8860b", "#fdf6e3"),
        (820, "лавина MOSFET", "Vкл = BVdss",
         "без зовнішніх деталей;\nлише в межах E_AS\nданого транзистора", POS, "#fdecea"),
    ]
    for cx, title, formula, body, col, fill in cards:
        ht, _, _ = textbox(cx, 80, title, size=12, bold=True, color=col,
                           fill=fill, stroke=col, sw=1.8, min_w=200)
        p.append(ht)
        ft, _, _ = textbox(cx, 140, formula, size=12, bold=True, color=INK,
                           fill=BG, stroke="#c9d3dc", sw=1.2, min_w=200)
        p.append(ft)
        bt, _, _ = textbox(cx, 220, body, size=10, color=INK,
                           fill=BG, stroke="#dfe3e8", sw=1.0, min_w=200)
        p.append(bt)

    # вісь компромісу під картками
    ax0, ax1, ay = 80, 860, 300
    p.append(arrow(ax0, ay, ax1, ay, color=MUTED, sw=1.8))
    p.append(text(ax0 + 60, ay + 20, "повільне гасіння, низька Vкл", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(ax1 - 30, ay + 20, "швидке гасіння, вища Vкл", size=10, color=POS, anchor="end", bold=True))

    p.append(text(W / 2, H - 14,
                  "усі дають енергії поля безпечний шлях — різниця в тому, ЯК ШВИДКО її спалити "
                  "й ДО ЯКОЇ напруги пустити сплеск",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "clamp-zoo.svg"), W, H, *p,
           title="Чотири способи приборкати індуктивний сплеск")


# ── tradeoff: напруга на ключі в часі — діод проти Зенера ─────────────────────
# Ідея: показати головний компроміс наочно — площа під «полицею» однакова
# (та сама енергія), але висока полиця (Зенер) коротка, низька (діод) довга.
def fig_tradeoff():
    W, H = 760, 380
    ox, oy = 90, 290           # початок осей (нуль напруги внизу)
    aw, ah = 580, 220
    p = []

    # осі
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - ah - 10, color=INK, sw=1.8))
    p.append(text(ox + aw, oy + 20, "час після розмикання", size=12, color=INK, italic=True, anchor="end"))
    p.append(mtext(ox - 14, oy - ah - 4, "напруга\nна ключі", size=12, color=INK, anchor="end", bold=True))

    # рівень живлення V
    Vy = oy - 40
    p.append(line(ox, Vy, ox + aw, Vy, color=MUTED, sw=1.2, dash="5 4"))
    p.append(text(ox - 8, Vy + 4, "+V", size=11, color=MUTED, anchor="end", bold=True))

    # рівень голого сплеску (небезпека) — пунктир високо
    Sy = oy - ah + 6
    p.append(line(ox, Sy, ox + 70, Sy, color=POS, sw=1.2, dash="3 3"))
    p.append(text(ox + 74, Sy + 4, "куди б злетів сплеск без захисту → пробій", size=10, color=POS, anchor="start", bold=True))

    # ДІОД: низька довга полиця (V + 0.7), повільний спад
    Dy = Vy - 16
    t0 = ox + 30
    pts_d = ["%.1f,%.1f" % (t0, oy)]
    pts_d.append("%.1f,%.1f" % (t0, Dy))
    # повільне експоненційне згасання назад до V
    for i in range(0, 81):
        t = i / 80.0
        x = t0 + 30 + t * (aw - 120)
        y = Vy - 16 * math.exp(-t * 2.0)
        pts_d.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts_d), FIELD))
    p.append(text(ox + aw - 30, Dy - 26, "гасний діод: низька полиця V+0.7,", size=11, color=FIELD, anchor="end", bold=True))
    p.append(text(ox + aw - 30, Dy - 12, "але струм тягнеться ДОВГО", size=11, color=FIELD, anchor="end"))

    # ЗЕНЕР: висока коротка полиця (V + Vz), швидкий спад
    Zy = oy - ah + 40
    pts_z = ["%.1f,%.1f" % (t0, oy)]
    pts_z.append("%.1f,%.1f" % (t0, Zy))
    pts_z.append("%.1f,%.1f" % (t0 + 110, Zy))         # коротка полиця
    pts_z.append("%.1f,%.1f" % (t0 + 130, Vy))          # різкий спад до V
    pts_z.append("%.1f,%.1f" % (ox + aw - 30, Vy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts_z), NEG))
    p.append(text(t0 + 70, Zy - 12, "Зенер/TVS: висока полиця V+Vz,", size=11, color=NEG, anchor="middle", bold=True))
    p.append(text(t0 + 175, Zy + 18, "гасить ШВИДКО", size=11, color=NEG, anchor="start"))

    # підпис «площа = та сама енергія»
    eb, _, _ = textbox(ox + aw * 0.5, oy - 70, "площа під полицею = та сама енергія ½·L·I²\n(вибираємо лише її форму)",
                       size=11, color=INK, fill="#fffef0", stroke="#b8860b", sw=1.4)
    p.append(eb)

    render(os.path.join(OUT, "tradeoff.svg"), W, H, *p,
           title="Головний компроміс: висота полиці проти тривалості гасіння")


# ── recirc: куди тече струм після розмикання (low-side і міст) ────────────────
# Ідея: фіксація — це завжди ЗАМКНЕНА ПЕТЛЯ для струму котушки; показати дві
# типові: нижній ключ + діод і синхронну рециркуляцію через верхнє плече.
def fig_recirc():
    W, H = 800, 360
    p = []

    # ── ліворуч: нижній ключ + гасний діод ──
    Lx = 150
    topY, botY = 90, 290
    p.append(text(Lx, topY - 14, "+V", size=13, color=POS, bold=True))
    p.append(line(Lx, topY, Lx, topY + 30, color=INK, sw=2))
    # котушка
    cy0 = topY + 30
    for i in range(3):
        p.append('<path d="M %.1f %.1f a 9 9 0 1 1 0 18" fill="none" stroke="%s" '
                 'stroke-width="2"/>' % (Lx, cy0 + i * 18, INK))
    p.append(text(Lx + 22, cy0 + 28, "L", size=14, color=INK, anchor="start", bold=True, italic=True))
    nodeY = cy0 + 54
    p.append(line(Lx, cy0 + 54, Lx, nodeY + 10, color=INK, sw=2))
    p.append(circle(Lx, nodeY + 10, 4, fill=INK, stroke=INK, sw=1))
    # ключ (нижній)
    p.append(line(Lx, nodeY + 10, Lx, nodeY + 24, color=INK, sw=2))
    p.append(line(Lx, nodeY + 24, Lx + 18, nodeY + 8, color=POS, sw=2.2))
    p.append(text(Lx + 22, nodeY + 22, "ключ OFF", size=10, color=POS, anchor="start", bold=True))
    p.append(line(Lx, nodeY + 44, Lx, botY, color=INK, sw=2))
    # земля
    p.append(line(Lx - 14, botY, Lx + 14, botY, color=INK, sw=2))
    p.append(line(Lx - 9, botY + 5, Lx + 9, botY + 5, color=INK, sw=1.6))
    # гасний діод паралельно котушці: гілка праворуч від topY-рейки до вузла.
    # катод (риска) вгорі = до +V; анод (вістря) внизу = до вузла.
    dx = Lx + 70
    nY = nodeY + 10
    p.append(line(Lx, topY, dx, topY, color=INK, sw=2))            # +V-рейка → угору гілки
    p.append(line(dx, topY, dx, topY + 22, color=INK, sw=2))
    p.append(line(Lx, nY, dx, nY, color=INK, sw=2))                # вузол → низ гілки
    p.append(line(dx, nY - 22, dx, nY, color=INK, sw=2))
    # символ діода: трикутник вістрям УГОРУ (провідність вузол→+V), катод-риска вгорі
    dmy = (topY + 22 + nY - 22) / 2
    p.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (dx - 8, dmy + 8, dx + 8, dmy + 8, dx, dmy - 8, "#eafaf0", FIELD))
    p.append(line(dx - 9, dmy - 8, dx + 9, dmy - 8, color=FIELD, sw=2))   # катод-риска вгорі (до +V)
    p.append(mtext(dx + 14, dmy - 4, "гасний\nдіод", size=10, color=FIELD, anchor="start", bold=True))
    # петля струму — зелені стрілки «вузол → діод → +V → котушка»
    p.append(arrow(dx, nY - 4, dx, dmy + 14, color=FIELD, sw=2.2))
    p.append(arrow(dx, dmy - 14, dx, topY + 4, color=FIELD, sw=2.2))

    p.append(mtext(Lx + 30, botY + 40, "нижній ключ: енергія тече\nпо петлі «котушка → діод»",
                   size=11, color=INK, anchor="middle", bold=True))

    # ── праворуч: синхронна рециркуляція в півмості ──
    Rx = 560
    p.append(text(Rx, topY - 14, "+V", size=13, color=POS, bold=True))
    p.append(line(Rx - 40, topY, Rx + 40, topY, color=INK, sw=2))
    # верхнє плече (ключ Q1) і нижнє (Q2), між ними — вузол до котушки
    midY = (topY + botY) / 2
    p.append(line(Rx, topY, Rx, midY - 30, color=INK, sw=2))
    q1, _, _ = textbox(Rx, midY - 18, "Q1\n(OFF→ON)", size=10, color=NEG, fill="#eef4ff", stroke=NEG, sw=1.4, min_w=80)
    p.append(q1)
    p.append(line(Rx, midY + 6, Rx, midY + 24, color=INK, sw=2))
    p.append(circle(Rx, midY + 24, 4, fill=INK, stroke=INK, sw=1))
    p.append(line(Rx, midY + 24, Rx, midY + 42, color=INK, sw=2))
    q2, _, _ = textbox(Rx, midY + 54, "Q2 (OFF)", size=10, color=POS, fill="#fdecea", stroke=POS, sw=1.4, min_w=80)
    p.append(q2)
    p.append(line(Rx, midY + 66, Rx, botY, color=INK, sw=2))
    p.append(line(Rx - 14, botY, Rx + 14, botY, color=INK, sw=2))
    p.append(line(Rx - 9, botY + 5, Rx + 9, botY + 5, color=INK, sw=1.6))
    # котушка від вузла праворуч
    p.append(line(Rx, midY + 24, Rx + 60, midY + 24, color=INK, sw=2))
    for i in range(3):
        p.append('<path d="M %.1f %.1f a 9 9 0 1 1 18 0" fill="none" stroke="%s" '
                 'stroke-width="2"/>' % (Rx + 60 + i * 18, midY + 24, INK))
    p.append(text(Rx + 90, midY + 8, "L", size=14, color=INK, anchor="middle", bold=True, italic=True))
    p.append(line(Rx + 114, midY + 24, Rx + 114, botY, color=INK, sw=2))
    p.append(line(Rx + 114, botY, Rx, botY, color=INK, sw=2))
    # петля рециркуляції крізь Q1
    p.append(arrow(Rx + 60, midY + 18, Rx, midY + 6, color=NEG, sw=2.2))
    p.append(mtext(Rx + 70, midY - 40, "струм завертає\nкрізь верхнє плече\n(його й вмикають)",
                   size=10, color=NEG, anchor="start"))

    p.append(mtext(Rx + 30, botY + 40, "міст: струм рециркулює крізь\nпротилежне плече (синхронно)",
                   size=11, color=INK, anchor="middle", bold=True))

    p.append(text(W / 2, H - 12,
                  "фіксація — це завжди ЗАМКНЕНА ПЕТЛЯ для струму котушки; питання лише, крізь що саме він завертає",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "recirc.svg"), W, H, *p,
           title="Куди тече струм після розмикання: петля рециркуляції")


# ── fsm-safe: машина станів захисту котушки (для proj-вставки) ────────────────
# Ідея: робочий цикл IDLE→TURN_ON→ON→TURN_OFF по верху, кожен стан зі своїм
# вікном вимірювання й дедлайном; спільна нижня «червона шина» зводить будь-яку
# несправність у поглинальний FAULT із фіксацією (ключ закритий до явного clear).
def fig_fsm_safe():
    W, H = 900, 420
    p = []

    # верхній ряд — робочий цикл
    ty = 90
    boxes = [
        (130, "IDLE", "ключ закритий", FIELD, "#eafaf0"),
        (340, "TURN_ON", "вузол сів до землі?\n(навантаження є)", NEG, "#eef4ff"),
        (560, "ON", "вузол низький —\nштатне проведення", FIELD, "#eafaf0"),
        (780, "TURN_OFF", "полиця клампа;\nяк довго?", "#b8860b", "#fdf6e3"),
    ]
    cx_list = []
    for cx, name, sub, col, fill in boxes:
        b, bw, bh = textbox(cx, ty, name + "\n" + sub, size=11, bold=True,
                            color=col, fill=fill, stroke=col, sw=1.8, min_w=170)
        p.append(b)
        cx_list.append((cx, bw, bh))

    # стрілки вперед по верхньому ряду + підписи подій
    evs = ["request_on", "вузол < LOW", "request_off"]
    for i in range(3):
        x0 = cx_list[i][0] + cx_list[i][1] / 2
        x1 = cx_list[i + 1][0] - cx_list[i + 1][1] / 2
        p.append(arrow(x0 + 2, ty, x1 - 2, ty, color=MUTED, sw=1.9))
        p.append(text((x0 + x1) / 2, ty - 12, evs[i], size=9, color=MUTED, italic=True))

    # TURN_OFF → IDLE (замикання циклу) дугою згори
    cxoff = cx_list[3][0]
    cxidle = cx_list[0][0]
    p.append('<path d="M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.9" marker-end="url(#arrow)"/>'
             % (cxoff, ty - cx_list[3][2] / 2, cxoff, ty - 70,
                cxidle, ty - 70, cxidle, ty - cx_list[0][2] / 2, MUTED))
    p.append(text((cxoff + cxidle) / 2, ty - 76, "полиця скінчилась → IDLE",
                  size=9, color=MUTED, italic=True))

    # поглинальний FAULT унизу
    fy = 330
    fb, fbw, fbh = textbox(W / 2, fy, "FAULT  (зафіксовано)\nключ закритий · вихід лише через fault_clear()",
                           size=12, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=2.2, min_w=420)
    p.append(fb)

    # «червона шина» — від кожного робочого стану вниз у FAULT, з підписом причини
    causes = [
        (cx_list[1][0], "обрив котушки\n(вузол не сів)"),
        (cx_list[2][0], "навантаження\nзникло на ходу"),
        (cx_list[3][0], "застрягання /\nполиця задовга"),
    ]
    busY = 250
    p.append(line(causes[0][0], busY, causes[-1][0], busY, color=POS, sw=2.0, dash="6 4"))
    for cx, why in causes:
        p.append(line(cx, ty + cx_list[1][2] / 2, cx, busY, color=POS, sw=1.6, dash="4 3"))
        p.append(mtext(cx, ty + cx_list[1][2] / 2 + 22, why, size=9, color=POS))
    p.append(arrow(W / 2, busY, W / 2, fy - fbh / 2 - 2, color=POS, sw=2.2))
    # «ключ коротить» — окрема причина з TURN_OFF (вузол лишився низьким)
    p.append(text(cx_list[3][0], busY - 8, "+ ключ коротить", size=9, color=POS, anchor="middle", bold=True))

    p.append(text(W / 2, H - 14,
                  "кожен стан має своє ВІКНО вимірювання вузла й ДЕДЛАЙН; "
                  "будь-яка несправність → поглинальний FAULT, ключ закритий до явного скидання",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "fsm-safe.svg"), W, H, *p,
           title="Машина станів захисту котушки: робочий цикл і фіксація аварії")


if __name__ == "__main__":
    fig_kickback()
    fig_clamp_zoo()
    fig_tradeoff()
    fig_recirc()
    fig_fsm_safe()
    print("OK: figures written to", OUT)
