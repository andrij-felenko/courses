# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── geometry: серце pure pursuit — дуга через апарат і ціль ────────────────────
# Ідея: апарат у початку, ціль на відстані L попереду на шляху; єдине коло,
# що проходить через обидві точки й дотикається курсу апарата, дає радіус
# повороту R = L²/(2x). Кут α між курсом і напрямом на ціль — те, чим кермуємо.

def fig_geometry():
    W, H = 720, 460
    p = []
    # апарат у (cx, cy), курс — угору екрана (дотична до дуги вертикальна).
    cx, cy = 250, 380

    # Задаємо дугу явно: центр праворуч на горизонталі апарата, радіус R.
    # Тоді курс (вертикаль) точно дотичний, а ціль лежить на самій дузі —
    # і бічний зсув x = gx-cx автоматично узгоджений із R = L²/(2x).
    R = 300.0
    ox, oy = cx + R, cy                 # центр дуги (праворуч, на горизонталі апарата)
    a_start = math.pi                   # апарат ліворуч від центра (курс угору = дотична)
    beta = 1.05                         # рад — гарний видимий поворот
    a_goal = math.pi + beta             # «+» → точка йде ВГОРУ екрана
    gx = ox + R * math.cos(a_goal)
    gy = oy + R * math.sin(a_goal)
    L = math.hypot(gx - cx, gy - cy)    # хорда апарат→ціль = випередження
    xoff = gx - cx                      # бічний зсув цілі (курс угору)

    # шлях (сірий пунктир) — трохи ширяє навколо дуги, не виходячи за неї далеко
    path = []
    for i in range(0, 201):
        a = a_start + (a_goal - a_start) * (i / 200.0) * 1.12
        rr = R + 24 * math.sin(i / 200.0 * 3.1)
        path.append("%.1f,%.1f" % (ox + rr * math.cos(a), oy + rr * math.sin(a)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
             'stroke-linejoin="round" stroke-dasharray="2 6"/>' % (" ".join(path), MUTED))
    p.append(text(gx - 6, gy - 26, "бажаний шлях", size=12, color=MUTED, anchor="start", italic=True))

    # дуга руху від апарата до цілі (зелена) — коротка, лишається на полотні
    arc = []
    for i in range(0, 121):
        a = a_start + (a_goal - a_start) * i / 120.0
        arc.append("%.1f,%.1f" % (ox + R * math.cos(a), oy + R * math.sin(a)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
             'stroke-linejoin="round"/>' % (" ".join(arc), FIELD))
    p.append(text(cx + 18, cy - 150, "дуга руху", size=12, color=FIELD, anchor="start", bold=True))

    # курс апарата (вертикальна стрілка вгору) — дотична до дуги
    p.append(arrow(cx, cy, cx, cy - 110, color=INK, sw=2.2))
    p.append(text(cx - 8, cy - 98, "курс", size=12, color=INK, anchor="end", italic=True))

    # хорда: від апарата до цілі (напрям погляду) — це L
    p.append(line(cx, cy, gx, gy, color=NEG, sw=2.0, dash="5 4"))
    mlx, mly = (cx + gx) / 2, (cy + gy) / 2
    p.append(text(mlx - 8, mly + 16, "L (випередження)", size=12, color=NEG, anchor="start", bold=True))

    # радіус: центр → апарат і центр → ціль
    p.append(line(ox, oy, cx, cy, color=POS, sw=1.6))
    p.append(line(ox, oy, gx, gy, color=POS, sw=1.6))
    p.append(circle(ox, oy, 4, fill=POS, stroke=POS, sw=1))
    p.append(text(ox - 6, oy + 20, "центр дуги", size=11, color=POS, anchor="end"))
    p.append(text((ox + cx) / 2, oy - 8, "R", size=13, color=POS, bold=True, italic=True))

    # кут α між курсом (вгору) і хордою — дужка біля апарата
    aa0 = -math.pi / 2                      # курс угору
    aa1 = math.atan2(gy - cy, gx - cx)      # напрям на ціль
    ar = 46
    barc = []
    steps = 24
    for i in range(steps + 1):
        a = aa0 + (aa1 - aa0) * i / steps
        barc.append("%.1f,%.1f" % (cx + ar * math.cos(a), cy + ar * math.sin(a)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (" ".join(barc), INK))
    amid = (aa0 + aa1) / 2
    p.append(text(cx + (ar + 14) * math.cos(amid), cy + (ar + 14) * math.sin(amid) + 4,
                  "α", size=14, color=INK, bold=True, italic=True))

    # бічний зсув x — горизонтальний пунктир від курсу до цілі
    p.append(line(cx, gy, gx, gy, color=POS, sw=1.3, dash="3 3"))
    p.append(text((cx + gx) / 2, gy - 6, "x", size=13, color=POS, anchor="middle", bold=True, italic=True))

    # точки апарата й цілі
    p.append(circle(cx, cy, 5.5, fill=INK, stroke=INK, sw=1))
    p.append(text(cx - 10, cy + 20, "апарат", size=12, color=INK, anchor="end"))
    p.append(circle(gx, gy, 6, fill="#fff", stroke=FIELD, sw=2.6))
    p.append(text(gx + 12, gy - 6, "ціль на шляху", size=12, color=FIELD, anchor="start", bold=True))

    # формула в кутку
    fb, fw, fh = textbox(575, 80, "R = L² / (2·x)\nкривина = 2·x / L²",
                         size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=1.6, pad=12)
    p.append(fb)
    p.append(text(575, 80 + fh / 2 + 16, "x — бічний зсув цілі", size=10, color=MUTED))

    render(os.path.join(OUT, "geometry.svg"), W, H, *p,
           title="Серце pure pursuit: одна дуга через апарат і ціль-точку")


# ── frame: як знайти зсув цілі в системі апарата ──────────────────────────────
# Ідея: ціль задано у світових координатах; переносимо її в систему апарата
# (початок — апарат, вісь вперед — курс), і бічна координата x — усе, що треба.

def fig_frame():
    W, H = 720, 340
    p = []
    cx, cy = 180, 250

    # світові осі (сірі, у кутку)
    p.append(arrow(50, 300, 50, 250, color=MUTED, sw=1.4))
    p.append(arrow(50, 300, 100, 300, color=MUTED, sw=1.4))
    p.append(text(104, 304, "світ", size=10, color=MUTED, anchor="start", italic=True))

    # апарат, повернутий на кут курсу (дивиться вправо-вгору)
    yaw = -0.55   # рад від горизонталі (екранні координати: вгору = мінус)
    fwx, fwy = math.cos(yaw), math.sin(yaw)         # вперед
    ltx, lty = math.cos(yaw - math.pi / 2), math.sin(yaw - math.pi / 2)  # ліворуч

    # осі системи апарата
    p.append(arrow(cx, cy, cx + fwx * 150, cy + fwy * 150, color=INK, sw=2.0))
    p.append(text(cx + fwx * 160, cy + fwy * 160, "вперед", size=12, color=INK, anchor="start", italic=True))
    p.append(arrow(cx, cy, cx + ltx * 90, cy + lty * 90, color=NEG, sw=1.8))
    p.append(text(cx + ltx * 100 - 4, cy + lty * 100, "вбік (x)", size=12, color=NEG, anchor="end", italic=True))

    p.append(circle(cx, cy, 5.5, fill=INK, stroke=INK, sw=1))
    p.append(text(cx - 8, cy + 20, "апарат", size=12, color=INK, anchor="end"))

    # ціль у світі
    gx, gy = cx + 250, cy - 40
    p.append(circle(gx, gy, 6, fill="#fff", stroke=FIELD, sw=2.6))
    p.append(text(gx + 12, gy - 4, "ціль", size=12, color=FIELD, anchor="start", bold=True))

    # вектор апарат→ціль
    p.append(line(cx, cy, gx, gy, color=FIELD, sw=1.6, dash="5 4"))

    # розклад: проєкція на «вперед» і на «вбік»
    dx, dy = gx - cx, gy - cy
    fproj = dx * fwx + dy * fwy      # уперед
    lproj = dx * ltx + dy * lty      # убік (x)
    # точка проєкції на вісь «вперед»
    fpx, fpy = cx + fwx * fproj, cy + fwy * fproj
    p.append(line(gx, gy, fpx, fpy, color=POS, sw=1.6, dash="3 3"))
    p.append(line(cx, cy, fpx, fpy, color=INK, sw=1.2, dash="2 4"))
    # підпис бічного зсуву
    mx, my = (gx + fpx) / 2, (gy + fpy) / 2
    p.append(text(mx + 8, my - 4, "x — бічний зсув", size=12, color=POS, anchor="start", bold=True))

    # формула переносу
    fb, fw, fh = textbox(560, 70, "у системі апарата:\nx = (ціль − апарат) · вісь-вбік",
                         size=12, bold=False, fill="#eef4ff", stroke=NEG, sw=1.4, pad=11)
    p.append(fb)

    render(os.path.join(OUT, "frame.svg"), W, H, *p,
           title="Спершу — ціль у системі апарата: важить лише зсув x")


# ── lookahead: короткий = зигзаг, довгий = зрізає кут ─────────────────────────
# Ідея: той самий шлях, різне випередження L. Мале L — нервовий зигзаг навколо
# шляху; велике L — гладко, але зрізає повороти; середнє — компроміс.

def fig_lookahead():
    W, H = 720, 340
    ox, oy = 70, 250
    aw, ah = 590, 200
    p = []

    # опорний шлях: сходинка-поворот (пряма, крутий поворот, пряма)
    def path_y(t):     # t у [0..1] → висота над віссю
        # спад-плато з «коліном» посередині
        if t < 0.35:
            return 0.15
        elif t < 0.55:
            return 0.15 + (t - 0.35) / 0.20 * 0.6
        else:
            return 0.75
    pts = []
    for i in range(0, 201):
        t = i / 200.0
        pts.append("%.1f,%.1f" % (ox + t * aw, oy - path_y(t) * ah))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
             'stroke-dasharray="2 6" stroke-linejoin="round"/>' % (" ".join(pts), MUTED))
    p.append(text(ox + aw, oy - path_y(1.0) * ah - 10, "шлях", size=11, color=MUTED, anchor="end", italic=True))

    # мале L — зигзаг навколо шляху (осциляція)
    zz = []
    for i in range(0, 201):
        t = i / 200.0
        base = path_y(t)
        wob = 0.11 * math.sin(t * 46) * math.exp(-abs(t - 0.5) * 1.2)
        zz.append("%.1f,%.1f" % (ox + t * aw, oy - (base + wob) * ah))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round"/>' % (" ".join(zz), POS))

    # велике L — зрізає кут (згладжений, «зрізаний» поворот)
    cut = []
    for i in range(0, 201):
        t = i / 200.0
        # згладжена версія коліна — розмиваємо перехід ширше й нижче піка
        if t < 0.25:
            y = 0.15
        elif t < 0.70:
            y = 0.15 + (t - 0.25) / 0.45 * 0.6
        else:
            y = 0.75
        cut.append("%.1f,%.1f" % (ox + t * aw, oy - y * ah))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round"/>' % (" ".join(cut), NEG))

    # осі-рамка (легка)
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.4))

    # легенда
    lx = ox + 8
    p.append(line(lx, oy - ah + 6, lx + 26, oy - ah + 6, color=MUTED, sw=3, dash="2 6"))
    p.append(text(lx + 32, oy - ah + 10, "заданий шлях", size=11, color=MUTED, anchor="start"))
    p.append(line(lx, oy - ah + 26, lx + 26, oy - ah + 26, color=POS, sw=2.2))
    p.append(text(lx + 32, oy - ah + 30, "мале L — нервовий зигзаг", size=11, color=POS, anchor="start", bold=True))
    p.append(line(lx, oy - ah + 46, lx + 26, oy - ah + 46, color=NEG, sw=2.2))
    p.append(text(lx + 32, oy - ah + 50, "велике L — гладко, та зрізає поворот", size=11, color=NEG, anchor="start", bold=True))

    render(os.path.join(OUT, "lookahead.svg"), W, H, *p,
           title="Упередження L вирішує характер: зигзаг ⇄ зрізаний кут")


# ── where: pure pursuit як зовнішній геометричний шар над керуванням ──────────
# Ідея: pure pursuit не крутить мотори — він видає кривину/курс, а нижчі контури
# (кермо/диференціал і швидкість) її втілюють. Шар над стабілізацією.

def fig_where():
    W, H = 720, 300
    p = []
    y = 150
    bw, bh = 132, 66
    gap = 40
    x = 40

    blocks = [
        ("шлях + позиція\n(де я, куди їхати)", "#eef4ff", INK),
        ("PURE PURSUIT\nвибір цілі →\nкривина / курс", "#eafaf0", FIELD),
        ("контур керма\n/ швидкості", "#fdf6e3", INK),
        ("привід\n(мотор, серво)", FILL, INK),
    ]
    centers = []
    for i, (lab, fill, col) in enumerate(blocks):
        b = fitbox(x, y - bh / 2, bw, bh, lab, size=11, fill=fill, stroke=(FIELD if i == 1 else INK),
                   sw=(2.2 if i == 1 else 1.5), bold=True, color=col)
        p.append(b)
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1], y, x - 2, y, color=INK, sw=1.8))
        x += bw + gap

    # зворотний зв'язок: позиція від приводу назад до першого блоку
    x_last = centers[-1][1]
    x_first = centers[0][0] + bw / 2
    p.append(line(x_last - bw / 2, y + bh / 2, x_last - bw / 2, y + 66, color=MUTED, sw=1.6))
    p.append(line(x_last - bw / 2, y + 66, x_first, y + 66, color=MUTED, sw=1.6))
    p.append(arrow(x_first, y + 66, x_first, y + bh / 2 + 2, color=MUTED, sw=1.6))
    p.append(text((x_first + x_last - bw / 2) / 2, y + 82, "нова позиція (одометрія / GNSS)",
                  size=11, color=MUTED, italic=True))

    p.append(text(W / 2, 44, "pure pursuit каже КУДИ гнути; нижчі контури — ЯК це зробити",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "where.svg"), W, H, *p,
           title="Місце pure pursuit: зовнішній геометричний шар над керуванням")


# ── segisect: коло випередження ∩ відрізок — квадратне рівняння й вибір кореня ─
# Ідея: ціль-точку шукаємо як перетин кола радіуса L навколо апарата з поточним
# відрізком шляху. Пряма-носій відрізка перетинає коло у ДВОХ точках (два корені
# t₁,t₂ квадратного рівняння); беремо той, що ПОПЕРЕДУ за рухом (більший t).

def fig_segisect():
    W, H = 792, 420
    p = []
    cx, cy = 250, 250            # апарат — центр кола випередження
    L = 150.0                    # радіус випередження (px)

    # коло випередження
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="4 5"/>' % (cx, cy, L, NEG))
    p.append(text(cx + L * 0.7, cy - L * 0.7 - 6, "коло радіуса L", size=12,
                  color=NEG, anchor="start", italic=True))

    # відрізок шляху A→B (напрям руху — від A до B), розсічений колом у двох точках
    ax, ay = 120, 360
    bx, by = 620, 150
    p.append(line(ax, ay, bx, by, color=MUTED, sw=3))
    p.append(circle(ax, ay, 4, fill=MUTED, stroke=MUTED, sw=1))
    p.append(circle(bx, by, 4, fill=MUTED, stroke=MUTED, sw=1))
    p.append(text(ax - 6, ay + 16, "A (початок відрізка)", size=11, color=MUTED, anchor="start"))
    p.append(text(bx + 8, by - 4, "B (кінець, напрям руху →)", size=11, color=MUTED, anchor="start", bold=True))

    # два перетини прямої-носія з колом: розв'язок |A + t·(B−A) − апарат|² = L²
    dx, dy = bx - ax, by - ay
    fx, fy = ax - cx, ay - cy
    aa = dx * dx + dy * dy
    bb = 2 * (fx * dx + fy * dy)
    ccq = fx * fx + fy * fy - L * L
    disc = math.sqrt(bb * bb - 4 * aa * ccq)
    t1 = (-bb - disc) / (2 * aa)      # менший корінь — ПОЗАДУ за рухом
    t2 = (-bb + disc) / (2 * aa)      # більший корінь — ПОПЕРЕДУ (беремо його)
    p1 = (ax + t1 * dx, ay + t1 * dy)
    p2 = (ax + t2 * dx, ay + t2 * dy)

    # корінь позаду (відкидаємо) — блідий
    p.append(circle(p1[0], p1[1], 6, fill="#fff", stroke=POS, sw=2))
    p.append(text(p1[0] - 10, p1[1] + 20, "корінь позаду —\nвідкинути", size=11,
                  color=POS, anchor="end"))
    # корінь попереду (ціль) — зелений, помітний
    p.append(circle(p2[0], p2[1], 7, fill="#fff", stroke=FIELD, sw=2.8))
    p.append(text(p2[0] + 12, p2[1] + 4, "ЦІЛЬ = корінь попереду\n(більший t)", size=12,
                  color=FIELD, anchor="start", bold=True))

    # апарат
    p.append(circle(cx, cy, 6, fill=INK, stroke=INK, sw=1))
    p.append(text(cx - 10, cy + 4, "апарат", size=12, color=INK, anchor="end"))

    # радіус до цілі
    p.append(line(cx, cy, p2[0], p2[1], color=FIELD, sw=1.4, dash="3 3"))

    fb, fw, fh = textbox(540, 350,
                         "|A + t·(B−A) − апарат|² = L²\n→ a·t² + b·t + c = 0\nбрати БІЛЬШИЙ корінь у [0,1]",
                         size=12, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.6, pad=12)
    p.append(fb)

    render(os.path.join(OUT, "segisect.svg"), W, H, *p,
           title="Ціль = перетин кола L з відрізком: квадратне рівняння, корінь попереду")


# ── hole: коло не дістає відрізка — дискримінант < 0, дірка в пошуку цілі ──────
# Ідея: якщо апарат відстав від лінії далі, ніж L, коло випередження взагалі не
# перетинає найближчий відрізок (disc<0). Наївний код лишається без цілі; лік —
# або тягтися до найближчої точки лінії, або нести межу з попереднього такту.

def fig_hole():
    W, H = 761, 340
    p = []
    cx, cy = 200, 250
    L = 95.0

    # коло випередження — МАЛЕ, не дістає лінії
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="4 5"/>' % (cx, cy, L, NEG))
    p.append(text(cx, cy - L - 8, "коло радіуса L", size=11, color=NEG, italic=True))

    # відрізок шляху — далеко зверху, поза колом
    ax, ay = 120, 90
    bx, by = 640, 130
    p.append(line(ax, ay, bx, by, color=MUTED, sw=3))
    p.append(text(bx + 6, by, "шлях (далі, ніж L)", size=11, color=MUTED, anchor="start"))

    # апарат
    p.append(circle(cx, cy, 6, fill=INK, stroke=INK, sw=1))
    p.append(text(cx - 10, cy + 18, "апарат відстав", size=12, color=INK, anchor="end"))

    # найближча точка лінії (проєкція) — запасна ціль
    dx, dy = bx - ax, by - ay
    tt = ((cx - ax) * dx + (cy - ay) * dy) / (dx * dx + dy * dy)
    tt = max(0.0, min(1.0, tt))
    npx, npy = ax + tt * dx, ay + tt * dy
    p.append(line(cx, cy, npx, npy, color=POS, sw=1.6, dash="4 4"))
    p.append(circle(npx, npy, 6, fill="#fff", stroke=POS, sw=2.4))
    p.append(text(npx + 8, npy - 6, "запасна ціль:\nнайближча точка лінії", size=11,
                  color=POS, anchor="start", bold=True))

    fb, fw, fh = textbox(500, 265,
                         "disc = b² − 4ac < 0\n→ коло НЕ перетинає відрізок\n→ дірка: цілі немає",
                         size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.6, pad=12)
    p.append(fb)

    render(os.path.join(OUT, "hole.svg"), W, H, *p,
           title="Пастка-дірка: апарат далі за L — коло не дістає відрізка")


# ── deriv: сама рівність двох радіусів як прямокутний трикутник ────────────────
# Ідея вставки-математики: центр C — на перпендикулярі до курсу, C→апарат = R.
# Ставимо C→ціль = R теж і опускаємо ноги трикутника: горизонтальна нога = R−x,
# вертикальна = y. Тоді (R−x)² + y² = R² — рівняння, з якого падає R = L²/(2x).

def fig_deriv():
    W, H = 720, 470
    p = []
    ax, ay = 250, 400                   # апарат; курс — угору екрана
    R = 260.0
    ox, oy = ax + R, ay                 # центр дуги C — праворуч на горизонталі апарата

    beta = 0.92                         # помірний видимий поворот
    a_goal = math.pi + beta
    gx = ox + R * math.cos(a_goal)
    gy = oy + R * math.sin(a_goal)

    # дуга руху апарат→ціль (зелена)
    arc = []
    for i in range(0, 121):
        a = math.pi + beta * i / 120.0
        arc.append("%.1f,%.1f" % (ox + R * math.cos(a), oy + R * math.sin(a)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
             'stroke-linejoin="round"/>' % (" ".join(arc), FIELD))
    p.append(text(ax + 14, ay - 150, "дуга руху", size=12, color=FIELD, anchor="start", bold=True))

    # курс — вертикальна стрілка вгору (дотична до дуги)
    p.append(arrow(ax, ay, ax, ay - 120, color=INK, sw=2.2))
    p.append(text(ax - 8, ay - 108, "курс", size=12, color=INK, anchor="end", italic=True))

    # перпендикуляр до курсу через апарат (на ньому лежить центр) — горизонталь
    p.append(line(ax - 30, ay, ox + 24, ay, color=MUTED, sw=1.3, dash="4 4"))
    p.append(text(ox + 20, ay + 18, "перпендикуляр до курсу", size=11, color=MUTED, anchor="end", italic=True))

    # два радіуси: C→апарат і C→ціль — обидва R
    p.append(line(ox, oy, ax, ay, color=POS, sw=2.0))
    p.append(line(ox, oy, gx, gy, color=POS, sw=2.0))
    p.append(text((ox + ax) / 2, ay - 8, "R", size=14, color=POS, bold=True, italic=True))
    mgx, mgy = (ox + gx) / 2, (oy + gy) / 2
    p.append(text(mgx + 8, mgy - 4, "R", size=14, color=POS, bold=True, italic=True))

    # прямокутний трикутник C–проекція цілі–ціль
    fx, fy = gx, oy                     # точка під ціллю на горизонталі центра
    p.append(line(ox, oy, fx, fy, color=NEG, sw=1.8))          # горизонтальна нога = R − x
    p.append(line(fx, fy, gx, gy, color=FIELD, sw=1.8))        # вертикальна нога = y
    s = 12                             # маркер прямого кута
    p.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="1.3"/>'
             % (fx - s, fy, fx - s, fy - s, fx, fy - s, INK))
    p.append(text((ox + fx) / 2, fy + 16, "R − x", size=12, color=NEG, anchor="middle", bold=True))
    p.append(text(gx + 8, (fy + gy) / 2, "y", size=13, color=FIELD, anchor="start", bold=True, italic=True))

    # бічний зсув x: від курсу до проекції цілі (угорі, на рівні цілі)
    p.append(line(ax, gy, gx, gy, color=INK, sw=1.3, dash="3 3"))
    p.append(text((ax + gx) / 2, gy - 6, "x", size=13, color=INK, anchor="middle", bold=True, italic=True))

    # точки
    p.append(circle(ax, ay, 5.5, fill=INK, stroke=INK, sw=1))
    p.append(text(ax - 10, ay + 20, "апарат", size=12, color=INK, anchor="end"))
    p.append(circle(ox, oy, 4.5, fill=POS, stroke=POS, sw=1))
    p.append(text(ox + 8, oy + 18, "центр C", size=11, color=POS, anchor="start"))
    p.append(circle(gx, gy, 6, fill="#fff", stroke=FIELD, sw=2.6))
    p.append(text(gx - 8, gy - 8, "ціль", size=12, color=FIELD, anchor="end", bold=True))

    fb, fw, fh = textbox(566, 96, "(R − x)² + y² = R²\n⇒ R = (x² + y²) / (2x) = L² / (2x)",
                         size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=1.6, pad=12)
    p.append(fb)
    p.append(text(566, 96 + fh / 2 + 16, "бо L² = x² + y²", size=10, color=MUTED))

    render(os.path.join(OUT, "deriv.svg"), W, H, *p,
           title="Рівність двох радіусів → прямокутний трикутник → R = L²/(2x)")


# ── sign: знак x = сторона повороту (дзеркальні дуги) ──────────────────────────
# Ідея: той самий |x|, той самий |R|, але ціль ліворуч (x>0) чи праворуч (x<0)
# дає дуги, зігнуті в протилежні боки. Кривина κ = 2x/L² міняє лише знак.

def fig_sign():
    W, H = 720, 360
    p = []
    ax, ay = 360, 300                   # апарат унизу по центру; курс угору
    R = 210.0

    # курс — угору
    p.append(arrow(ax, ay, ax, ay - 120, color=INK, sw=2.2))
    p.append(text(ax + 8, ay - 108, "курс", size=12, color=INK, anchor="start", italic=True))
    p.append(circle(ax, ay, 5.5, fill=INK, stroke=INK, sw=1))
    p.append(text(ax, ay + 22, "апарат", size=12, color=INK, anchor="middle"))

    beta = 0.95

    # права дуга: ціль праворуч (x>0 у осях виведення), центр праворуч
    oxR = ax + R
    arcR = []
    for i in range(0, 111):
        a = math.pi + beta * i / 110.0
        arcR.append("%.1f,%.1f" % (oxR + R * math.cos(a), ay + R * math.sin(a)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(arcR), POS))
    gxR = oxR + R * math.cos(math.pi + beta)
    gyR = ay + R * math.sin(math.pi + beta)
    p.append(circle(gxR, gyR, 5.5, fill="#fff", stroke=POS, sw=2.4))
    p.append(text(gxR + 8, gyR - 4, "ціль праворуч", size=11, color=POS, anchor="start", bold=True))
    p.append(mtext(ax + 78, ay - 158, "x > 0 → κ > 0\nповорот праворуч", size=11, color=POS, anchor="start", bold=True))

    # ліва дуга: ціль ліворуч (x<0), центр ліворуч — дзеркало
    oxL = ax - R
    arcL = []
    for i in range(0, 111):
        a = -beta * i / 110.0
        arcL.append("%.1f,%.1f" % (oxL + R * math.cos(a), ay + R * math.sin(a)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(arcL), NEG))
    gxL = oxL + R * math.cos(-beta)
    gyL = ay + R * math.sin(-beta)
    p.append(circle(gxL, gyL, 5.5, fill="#fff", stroke=NEG, sw=2.4))
    p.append(text(gxL - 8, gyL - 4, "ціль ліворуч", size=11, color=NEG, anchor="end", bold=True))
    p.append(mtext(ax - 78, ay - 158, "x < 0 → κ < 0\nповорот ліворуч", size=11, color=NEG, anchor="end", bold=True))

    # горизонтальні пунктири |x| з обох боків
    p.append(line(ax, gyL, gxL, gyL, color=NEG, sw=1.2, dash="3 3"))
    p.append(line(ax, gyR, gxR, gyR, color=POS, sw=1.2, dash="3 3"))

    render(os.path.join(OUT, "sign.svg"), W, H, *p,
           title="Знак x — це сторона повороту: дзеркальні дуги, |κ| той самий")


if __name__ == "__main__":
    fig_geometry()
    fig_frame()
    fig_lookahead()
    fig_where()
    fig_segisect()
    fig_hole()
    fig_deriv()
    fig_sign()
    print("OK: figures written to", OUT)
