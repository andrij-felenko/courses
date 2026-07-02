# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def flow():
    """Конвеєр синтезу: опис на HDL -> дерево логіки -> оптимізація -> прив'язка -> нетлист."""
    W, H = 760, 300
    y = 150
    stages = [
        ("Опис\nна HDL", "що робити", FILL),
        ("Родове\nдерево\nлогіки", "AND/OR/NOT", FILL),
        ("Оптимізація", "менше, коротше", "#eafaf0"),
        ("Прив'язка\nдо клітинок", "LUT / гейти", FILL),
        ("Нетлист", "готова схема", "#eafaf0"),
    ]
    n = len(stages)
    bw, bh = 118, 84
    gap = (W - 40 - n * bw) / (n - 1)
    frags = []
    xs = []
    for i, (label, sub, fill) in enumerate(stages):
        x = 20 + i * (bw + gap)
        xs.append(x + bw / 2)
        frags.append(fitbox(x, y - bh / 2, bw, bh, label, size=15, bold=True, fill=fill))
        frags.append(text(x + bw / 2, y + bh / 2 + 20, sub, size=12, color=MUTED, italic=True))
    for i in range(n - 1):
        frags.append(arrow(xs[i] + bw / 2 - 2, y, xs[i + 1] - bw / 2 + 2, y))
    frags.append(text(W / 2, y - bh / 2 - 48, "оптимізатор працює тут — між описом і залізом",
                      size=13, color=INK))
    frags.append(line(xs[1], y - bh / 2 - 34, xs[1], y - bh / 2 - 6, color=MUTED, sw=1, dash="3 3"))
    frags.append(line(xs[3], y - bh / 2 - 34, xs[3], y - bh / 2 - 6, color=MUTED, sw=1, dash="3 3"))
    frags.append(line(xs[1], y - bh / 2 - 34, xs[3], y - bh / 2 - 34, color=MUTED, sw=1, dash="3 3"))
    return render(os.path.join(IMG, "flow.svg"), W, H, *frags,
                  title="Синтез: від опису поведінки до реальних клітинок")


def simplify():
    """Та сама функція до й після спрощення: 3 гейти й 6 входів -> 1 гейт і 2 входи."""
    W, H = 720, 320
    frags = []
    # ліворуч — «сира» реалізація виразу a·b + a·b̄
    lx = 175
    frags.append(text(lx, 60, "як написано в коді", size=14, color=INK, bold=True))
    frags.append(text(lx, 82, "a·b + a·(НЕ b)", size=15, color=NEG))
    b1 = fitbox(lx - 130, 110, 74, 40, "AND", size=13, fill=FILL)
    b2 = fitbox(lx - 130, 170, 74, 40, "AND", size=13, fill=FILL)
    b3 = fitbox(lx - 20, 140, 74, 40, "OR", size=13, fill=FILL)
    frags += [b1, b2, b3]
    frags.append(arrow(lx - 56, 130, lx - 20, 150))
    frags.append(arrow(lx - 56, 190, lx - 20, 170))
    frags.append(text(lx, 240, "3 гейти · 6 входів", size=13, color=POS, bold=True))

    # стрілка спрощення
    frags.append(arrow(lx + 90, 175, lx + 200, 175, sw=2.4))
    frags.append(text(lx + 145, 158, "спрощення", size=13, color=FIELD, bold=True))
    frags.append(text(lx + 145, 196, "a·b + a·b̄ = a", size=12, color=MUTED, italic=True))

    # праворуч — те саме, зведене до самого «a»
    rx = 560
    frags.append(text(rx, 60, "що це насправді", size=14, color=INK, bold=True))
    frags.append(text(rx, 82, "a", size=16, color=FIELD, bold=True))
    frags.append(fitbox(rx - 40, 150, 80, 44, "буфер\n(a)", size=13, fill="#eafaf0"))
    frags.append(text(rx, 240, "1 елемент · 1 вхід", size=13, color=FIELD, bold=True))
    frags.append(text(W / 2, 292, "менше гейтів = менша площа, менше споживання, коротший шлях",
                      size=13, color=INK))
    return render(os.path.join(IMG, "simplify.svg"), W, H, *frags,
                  title="Оптимізація: та сама функція меншою ціною")


def tradeoff():
    """Один і той самий блок, зібраний під площу або під швидкість — три цілі тягнуть у різні боки."""
    W, H = 720, 340
    frags = []
    cx, cy, r = W / 2, 205, 110
    import math
    # вершини трикутника: площа, швидкість, споживання
    verts = []
    labels = ["ПЛОЩА\n(менше клітинок)", "ШВИДКІСТЬ\n(коротший шлях)", "СПОЖИВАННЯ\n(менше перемикань)"]
    cols = [NEG, POS, FIELD]
    for i in range(3):
        ang = -math.pi / 2 + i * 2 * math.pi / 3
        vx, vy = cx + r * math.cos(ang), cy + r * math.sin(ang)
        verts.append((vx, vy))
    # сторони трикутника
    for i in range(3):
        a = verts[i]
        b = verts[(i + 1) % 3]
        frags.append(line(a[0], a[1], b[0], b[1], color=MUTED, sw=1.5, dash="5 4"))
    # підписи-вершини
    offs = [(0, -18), (18, 22), (-18, 22)]
    for i, (vx, vy) in enumerate(verts):
        frags.append(fitbox(vx - 82 + offs[i][0], vy - 24 + offs[i][1], 164, 48,
                            labels[i], size=12.5, bold=True, fill="#ffffff", stroke=cols[i], sw=2))
    frags.append(text(cx, cy + 4, "тягнути можна", size=13, color=INK, bold=True))
    frags.append(text(cx, cy + 22, "лише до двох", size=13, color=INK, bold=True))
    frags.append(text(cx, cy + 40, "водночас", size=13, color=MUTED, italic=True))
    frags.append(text(W / 2, 322, "constraints кажуть, у який кут тягнути — решту оптимізатор пожертвує",
                      size=13, color=INK))
    return render(os.path.join(IMG, "tradeoff.svg"), W, H, *frags,
                  title="Три цілі синтезу тягнуть у різні боки")


def minimization_timeline():
    """Історія мінімізації: п'ять віх від ручних карт до промислових оптимізаторів; два переломи — руками→машиною, точно→евристично."""
    W, H = 860, 340
    frags = []
    yaxis = 250                # горизонтальна вісь-стрічка
    # п'ять віх рівномірно по ширині (не за лінійним часом — інакше 1956→1984 з'їдає екран)
    events = [
        ("1952", "Вейч", "діаграма", NEG),
        ("1953", "Карно", "карта", NEG),
        ("1956", "Квайн—\nМак-Класкі", "таблиця", FIELD),
        ("1984", "Espresso", "евристика", POS),
        ("2006", "ABC · AIG", "багато рівнів", INK),
    ]
    n = len(events)
    bw, bh = 132, 60
    margin = 24
    step = (W - 2 * margin - bw) / (n - 1)
    xs = [margin + bw / 2 + i * step for i in range(n)]

    for x, (yr, name, sub, col) in zip(xs, events):
        # засічка на осі + рік під нею
        frags.append(line(x, yaxis - 7, x, yaxis + 7, color=INK, sw=1.8))
        frags.append(text(x, yaxis + 26, yr, size=14, color=INK, bold=True))
        # картка над віссю
        top = yaxis - 7 - 34 - bh
        frags.append(line(x, yaxis - 7, x, top + bh, color=MUTED, sw=1, dash="3 3"))
        frags.append(fitbox(x - bw / 2, top, bw, bh, name, size=14, bold=True,
                            fill="#ffffff", stroke=col, sw=2))
        frags.append(text(x, top - 8, sub, size=12, color=col, italic=True))

    # вісь-стрілка «час»
    frags.append(line(margin, yaxis, W - margin, yaxis, color=INK, sw=2))
    frags.append(text(W - margin, yaxis - 12, "час", size=12, color=MUTED, italic=True, anchor="end"))

    # два переломи: підписи режимів під роками (три зони, поділені між віхами 2|3 і 3|4)
    b1 = (xs[1] + xs[2]) / 2      # межа руками | машиною
    b2 = (xs[2] + xs[3]) / 2      # межа точно | евристично
    yb = yaxis + 52
    frags.append(line(b1, yaxis + 34, b1, yb + 22, color=NEG, sw=1.2, dash="6 5"))
    frags.append(line(b2, yaxis + 34, b2, yb + 22, color=POS, sw=1.2, dash="6 5"))
    frags.append(text((margin + b1) / 2, yb, "руками", size=13, color=NEG, bold=True))
    frags.append(text((margin + b1) / 2, yb + 18, "видихаються по ~6 змінних", size=11, color=MUTED))
    frags.append(text((b1 + b2) / 2, yb, "машиною, точно", size=13, color=FIELD, bold=True))
    frags.append(text((b1 + b2) / 2, yb + 18, "але вибух на великому", size=11, color=MUTED))
    frags.append(text((b2 + W - margin) / 2, yb, "евристично", size=13, color=POS, bold=True))
    frags.append(text((b2 + W - margin) / 2, yb + 18, "~99% оптимуму, швидко", size=11, color=MUTED))

    return render(os.path.join(IMG, "minimization-timeline.svg"), W, H, *frags,
                  title="Історія мінімізації логіки: від олівця до промислового оптимізатора")


def cube():
    """Простір входів a,b,c як куб: вершини-мінтерми, куб-ребро 11– і куб-грань – –1."""
    W, H = 720, 400
    frags = []
    # ізометрична проєкція куба: вершина (a,b,c) з {0,1} → 2D
    ox, oy = 250, 250          # початок координат на полотні
    ux, uy = 150, 0            # вісь a (вправо)
    vx, vy = 0, -150           # вісь b (вгору)
    wx, wy = 80, -54           # вісь c (вглиб)

    def P(a, b, c):
        return (ox + a * ux + b * vx + c * wx,
                oy + a * uy + b * vy + c * wy)

    # грань c=1 (куб – –1): чотири вершини 001,011,111,101 — зелена заливка (малюємо першою, під ребрами)
    face = [P(0, 0, 1), P(0, 1, 1), P(1, 1, 1), P(1, 0, 1)]
    pts = " ".join("%.1f,%.1f" % pt for pt in face)
    frags.append('<polygon points="%s" fill="#27ae6022" stroke="%s" '
                 'stroke-width="2.5"/>' % (pts, FIELD))

    # ребра куба
    edges = [((0,0,0),(1,0,0)), ((0,0,0),(0,1,0)), ((0,0,0),(0,0,1)),
             ((1,1,1),(0,1,1)), ((1,1,1),(1,0,1)), ((1,1,1),(1,1,0)),
             ((1,0,0),(1,1,0)), ((1,0,0),(1,0,1)), ((0,1,0),(1,1,0)),
             ((0,1,0),(0,1,1)), ((0,0,1),(1,0,1)), ((0,0,1),(0,1,1))]
    for (aa, bb) in edges:
        p1, p2 = P(*aa), P(*bb)
        frags.append(line(p1[0], p1[1], p2[0], p2[1], color=MUTED, sw=1.2))

    # ребро 11– (між 110 та 111): червоне, товсте
    r1, r2 = P(1, 1, 0), P(1, 1, 1)
    frags.append(line(r1[0], r1[1], r2[0], r2[1], color=POS, sw=4))

    # вершини: одиниці функції заповнені, нулі — порожні
    ones = {(0,0,1), (0,1,1), (1,0,1), (1,1,0), (1,1,1)}
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                px, py = P(a, b, c)
                is1 = (a, b, c) in ones
                frags.append(circle(px, py, 8,
                             fill=(INK if is1 else BG), stroke=INK, sw=1.8))
                lbl = "%d%d%d" % (a, b, c)
                dx = 14 if a == 1 else -14
                dy = 4 if b == 0 else -13
                frags.append(text(px + dx, py + dy, lbl, size=11,
                             color=(INK if is1 else MUTED),
                             anchor=("start" if a == 1 else "end")))

    # підписи осей
    axa = P(1, 0, 0)
    frags.append(text(axa[0] + 18, axa[1] + 24, "вісь a", size=12, color=MUTED, italic=True, anchor="start"))
    axb = P(0, 1, 0)
    frags.append(text(axb[0] - 8, axb[1] - 12, "вісь b", size=12, color=MUTED, italic=True, anchor="end"))
    axc = P(0, 0, 1)
    frags.append(text(axc[0] + 8, axc[1] - 8, "вісь c", size=12, color=MUTED, italic=True, anchor="start"))

    # легенда праворуч
    lx = 500
    frags.append(fitbox(lx, 74, 204, 48,
                 "куб  1 1 –\nребро: 2 точки, 1 риска", size=12.5, fill="#fdecea", stroke=POS, sw=2))
    frags.append(fitbox(lx, 138, 204, 48,
                 "куб  – – 1\nгрань: 4 точки, 2 риски", size=12.5, fill="#eafaf0", stroke=FIELD, sw=2))
    frags.append(fitbox(lx, 208, 204, 72,
                 "● одиниця функції\n○ нуль\nриска = вісь, вздовж\nякої куб розтягнутий",
                 size=11.5, fill="#ffffff", stroke=MUTED, sw=1.5))

    return render(os.path.join(IMG, "cube.svg"), W, H, *frags,
                  title="Логіка як геометрія: куб входів, ребра й грані")


def kmap():
    """Карта Карно 4×4 функції y = d + a·b: групи-кубі й суттєва проста імпліканта."""
    W, H = 720, 430
    frags = []
    # y = d + a·b (перевірено): середні два стовпці cd=01,11 (там d=1) + рядок ab=11
    grid = [
        [0, 1, 1, 0],   # ab=00
        [0, 1, 1, 0],   # ab=01
        [1, 1, 1, 1],   # ab=11
        [0, 1, 1, 0],   # ab=10
    ]
    rows = ["00", "01", "11", "10"]   # ab у коді Ґрея
    cols = ["00", "01", "11", "10"]   # cd у коді Ґрея (стовпець = c d)
    cell = 60
    gx, gy = 210, 92                  # лівий верхній кут сітки

    frags.append(text(gx + 2 * cell, gy - 42, "cd  (код Ґрея →)", size=13, color=INK, bold=True))
    frags.append(text(gx - 60, gy + 2 * cell - 6, "ab", size=13, color=INK, bold=True))
    frags.append(text(gx - 60, gy + 2 * cell + 12, "(↓)", size=11, color=MUTED))
    for j, c in enumerate(cols):
        frags.append(text(gx + j * cell + cell / 2, gy - 12, c, size=12, color=MUTED))
    for i, r in enumerate(rows):
        frags.append(text(gx - 16, gy + i * cell + cell / 2 + 4, r, size=12, color=MUTED))

    for i in range(4):
        for j in range(4):
            x = gx + j * cell
            y = gy + i * cell
            v = grid[i][j]
            fill = "#eef4fb" if v == 1 else BG
            frags.append(rect(x, y, cell, cell, fill=fill, stroke=MUTED, sw=1, rx=0))
            frags.append(text(x + cell / 2, y + cell / 2 + 6, str(v),
                         size=17, color=(INK if v else MUTED), bold=bool(v)))

    def group(i0, j0, i1, j1, color):
        x = gx + j0 * cell + 4
        y = gy + i0 * cell + 4
        w = (j1 - j0 + 1) * cell - 8
        h = (i1 - i0 + 1) * cell - 8
        return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" '
                'fill="none" stroke="%s" stroke-width="3"/>' % (x, y, w, h, color))

    # куб «d» = – – –1 — два середні стовпці (cd=01,11), усі рядки: 8 клітинок, 3 риски
    frags.append(group(0, 1, 3, 2, FIELD))
    # куб «a·b» = 1 1 – – — увесь рядок ab=11: 4 клітинки, 2 риски
    frags.append(group(2, 0, 2, 3, NEG))
    # суттєвість a·b показуємо на клітинці (ab=11, cd=10): її не накриває «d» (там d=0)
    frags.append(group(2, 3, 2, 3, POS))

    frags.append(text(gx + 2 * cell, gy + 4 * cell + 30,
                 "зелена група (два середні стовпці, де d=1) — куб «d»: 8 клітинок, 3 риски",
                 size=11.5, color=FIELD, bold=True))
    frags.append(text(gx + 2 * cell, gy + 4 * cell + 50,
                 "синя група (рядок ab=11) — куб «a·b»: 4 клітинки, 2 риски → y = d + a·b",
                 size=11.5, color=NEG, bold=True))
    ex = gx + 4 * cell + 22
    frags.append(fitbox(ex, gy + 2.35 * cell, 158, 84,
                 "суттєва:\nцю клітинку (d=0)\nнакриває лише «a·b»,\nтож без неї не обійтись —\nбереться обов'язково",
                 size=11, fill="#fdecea", stroke=POS, sw=2))
    frags.append(fitbox(ex, gy + 0.35 * cell, 158, 66,
                 "а де одиницю накриває\nкілька груп — вибір;\nвін і робить точну\nмінімізацію дорогою",
                 size=11, fill="#ffffff", stroke=MUTED, sw=1.5))

    return render(os.path.join(IMG, "kmap.svg"), W, H, *frags,
                  title="Карта Карно: сусіди поруч, групи — це кубі")


if __name__ == "__main__":
    flow()
    simplify()
    tradeoff()
    minimization_timeline()
    cube()
    kmap()
    print("ok")
