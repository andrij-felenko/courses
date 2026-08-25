# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: задумана vs реальна архітектура — розрив, що зветься ерозією ──
def fig_prescriptive_vs_descriptive():
    W, H = 860, 430
    frags = []
    frags.append(text(W/2, 30, "Задумана структура та реальна — і зазор між ними", size=17, bold=True))

    # ЛІВОРУЧ: задумана (prescriptive) — чисті шари, стрілки лише вниз
    lx = 60
    frags.append(text(lx + 150, 66, "ЗАДУМАНА (як має бути)", size=13, bold=True, color=FIELD))
    layers = ["UI", "Логіка", "Доступ до даних", "База"]
    ly0, lh, lw = 88, 58, 300
    ys = []
    for i, name in enumerate(layers):
        y = ly0 + i * (lh + 22)
        ys.append(y)
        frags.append(fitbox(lx, y, lw, lh, name, size=14, bold=True,
                            fill="#eafaf1", stroke=FIELD, sw=1.8))
    # дозволені стрілки — тільки сусідній шар униз
    for i in range(len(layers) - 1):
        frags.append(arrow(lx + lw/2, ys[i] + lh, lx + lw/2, ys[i+1], color=FIELD, sw=2))
    frags.append(text(lx + lw/2, ys[-1] + lh + 26, "кожен шар знає лише сусіда нижче", size=11, color=MUTED))

    # ПРАВОРУЧ: реальна (descriptive) — ті самі шари, але заборонені перемички
    rx = 420
    frags.append(text(rx + 150, 66, "РЕАЛЬНА (як стало)", size=13, bold=True, color=POS))
    rys = []
    for i, name in enumerate(layers):
        y = ly0 + i * (lh + 22)
        rys.append(y)
        frags.append(fitbox(rx, y, lw, lh, name, size=14, bold=True,
                            fill="#fdeeec", stroke=POS, sw=1.8))
    # дозволені (сірі, вниз по сусідах)
    for i in range(len(layers) - 1):
        frags.append(arrow(rx + lw*0.30, rys[i] + lh, rx + lw*0.30, rys[i+1], color=MUTED, sw=1.5))
    # ПОРУШЕННЯ: UI -> База напряму (в обхід), збоку справа, щоб не лягти на текст
    frags.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="6 4" marker-end="url(#arrow)"/>' % (
        rx + lw, rys[0] + lh/2, rx + lw + 70, rys[0] + lh/2, rx + lw + 70, rys[3] + lh/2, rx + lw, rys[3] + lh/2, POS))
    frags.append(text(rx + lw + 74, (rys[0] + rys[3])/2 + lh/2, "в обхід", size=11, color=POS, anchor="start", bold=True))
    # порушення: Логіка -> База (перескок шару)
    frags.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="6 4" marker-end="url(#arrow)"/>' % (
        rx + lw*0.72, rys[1] + lh, rx + lw*0.95, rys[1] + lh + 30, rx + lw*0.95, rys[3] - 8, rx + lw*0.72, rys[3], POS))

    return render(os.path.join(IMG, 'prescriptive-vs-descriptive.svg'), W, H, *frags)


# ── Фігура 2: механізм ерозії — самопідсильна петля дрібних поступок ──
def fig_erosion_loop():
    W, H = 720, 400
    frags = []
    frags.append(text(W/2, 30, "Чому ерозія розкручується сама", size=17, bold=True))

    # чотири вузли по колу
    cx, cy, R = 360, 225, 128
    nodes = [
        ("Тиск дедлайну:\nполагодь зараз", cx, cy - R),
        ("Поступка в обхід\nструктури", cx + R + 20, cy),
        ("Структуру важче\nчитати й тримати", cx, cy + R),
        ("Наступна поступка\nще дешевша", cx - R - 20, cy),
    ]
    pts = []
    for label, x, y in nodes:
        frag, w, h = textbox(x, y, label, size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.6)
        frags.append(frag)
        pts.append((x, y, w, h))

    # стрілки по колу (за годинниковою), від краю рамки до краю наступної
    order = [0, 1, 2, 3, 0]
    import math
    for a in range(4):
        x1, y1, w1, h1 = pts[order[a]]
        x2, y2, w2, h2 = pts[order[a+1]]
        # напрям
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx/d, dy/d
        # відступ від рамок (приблизно піврозмір по більшій осі)
        off1 = (w1/2 + 12) if abs(ux) > abs(uy) else (h1/2 + 12)
        off2 = (w2/2 + 12) if abs(ux) > abs(uy) else (h2/2 + 12)
        sx, sy = x1 + ux*off1, y1 + uy*off1
        ex, ey = x2 - ux*off2, y2 - uy*off2
        frags.append(arrow(sx, sy, ex, ey, color=POS, sw=2))

    frags.append(text(cx, cy - 4, "петля", size=13, bold=True, color=POS))
    frags.append(text(cx, cy + 16, "з додатним", size=12, color=POS))
    frags.append(text(cx, cy + 34, "зворотним зв'язком", size=12, color=POS))

    return render(os.path.join(IMG, 'erosion-loop.svg'), W, H, *frags)


# ── Фігура 3: дрейф vs ерозія — дві різні хвороби структури ──
def fig_drift_vs_erosion():
    W, H = 760, 340
    frags = []
    frags.append(text(W/2, 30, "Дві різні хвороби: дрейф і ерозія", size=17, bold=True))

    colw = 330
    # ДРЕЙФ
    dx = 50
    frags.append(fitbox(dx, 58, colw, 46, "ДРЕЙФ", size=16, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.8))
    drift_lines = [
        "Правил ніхто не порушував —",
        "їх просто перестали помічати.",
        "Структура розмивається від",
        "неуважності: рішення додають,",
        "не звіряючись із задумом.",
    ]
    frags.append(fitbox(dx, 116, colw, 150, "\n".join(drift_lines), size=13,
                        fill=BG, stroke=NEG, sw=1.4))
    frags.append(text(dx + colw/2, 290, "причина: нечутливість до архітектури", size=11.5, color=NEG))

    # ЕРОЗІЯ
    ex = 420
    frags.append(fitbox(ex, 58, colw, 46, "ЕРОЗІЯ", size=16, bold=True,
                        fill="#fdeeec", stroke=POS, sw=1.8))
    ero_lines = [
        "Правило знали — і свідомо",
        "переступили заради швидкого",
        "виграшу. Кожне порушення",
        "лишає рубець, і наступне",
        "переступити вже легше.",
    ]
    frags.append(fitbox(ex, 116, colw, 150, "\n".join(ero_lines), size=13,
                        fill=BG, stroke=POS, sw=1.4))
    frags.append(text(ex + colw/2, 290, "причина: порушення архітектури", size=11.5, color=POS))

    return render(os.path.join(IMG, 'drift-vs-erosion.svg'), W, H, *frags)


# ── Фігура 4: DFS трьома кольорами — зворотне ребро в сіру вершину = цикл ──
def fig_dfs_colors_cycle():
    W, H = 820, 430
    frags = []
    frags.append(text(W/2, 30, "Обхід у глибину трьома кольорами: цикл = ребро в сіру вершину", size=15.5, bold=True))

    WH  = "#ffffff"   # біла вершина
    GR  = "#cfd4da"   # сіра вершина (у поточному ланцюжку)
    BK  = "#333333"   # чорна вершина (вийдена)

    R = 26

    # ── Легенда ліворуч (окрема колонка, щоб не лягти на граф) ──
    lx, ly = 60, 92
    frags.append(text(lx, ly - 22, "Стан вершини:", size=12.5, bold=True, anchor="start"))
    legend = [
        (WH, INK,  "білий — ще не заходили"),
        (GR, INK,  "сірий — у ланцюжку зараз"),
        (BK, "#ffffff", "чорний — вийдено остаточно"),
    ]
    for i, (fill, tcol, lab) in enumerate(legend):
        cy = ly + i * 40
        frags.append(circle(lx + 12, cy, 12, fill=fill, stroke=LINE, sw=1.6))
        frags.append(text(lx + 34, cy + 4, lab, size=11.5, anchor="start"))

    # ── Граф праворуч: ланцюжок A→B→C→D, і зворотне ребро D→B (цикл) ──
    # A(чорна, збоку — вже вийдена гілка сходиться), головний ланцюжок B→C→D сірий.
    gx = 470
    nodes = {
        "A": (gx,        110, WH, INK),   # біла: ще не ходили
        "B": (gx,        210, GR, INK),   # сіра: у ланцюжку
        "C": (gx + 150,  210, GR, INK),   # сіра: у ланцюжку
        "D": (gx + 150,  330, GR, INK),   # сіра: у ланцюжку — звідси зворотне ребро
        "E": (gx - 140,  330, BK, "#ffffff"),  # чорна: вийдена гілка
    }
    def cxy(n): return nodes[n][0], nodes[n][1]

    # прямі ребра (крок углиб) — від краю кола до краю кола
    import math
    def edge(a, b, color=LINE, sw=2.0, dash=None):
        x1, y1 = cxy(a); x2, y2 = cxy(b)
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy); ux, uy = dx/d, dy/d
        sx, sy = x1 + ux*R, y1 + uy*R
        ex, ey = x2 - ux*(R+3), y2 - uy*(R+3)
        dd = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                'stroke-width="%.1f"%s marker-end="url(#arrow)"/>' % (sx, sy, ex, ey, color, sw, dd))

    frags.append(edge("A", "B"))               # крок углиб
    frags.append(edge("B", "C"))
    frags.append(edge("C", "D"))
    frags.append(edge("B", "E"))               # інша гілка з B, уже вийдена (E чорна)

    # ЗВОРОТНЕ РЕБРО D → B (у сіру!) — дугою праворуч, повз вузли
    dxx, dyy = cxy("D"); bxx, byy = cxy("B")
    frags.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2.6" stroke-dasharray="7 4" '
                 'marker-end="url(#arrow)"/>' % (
                     dxx + R, dyy - 6, dxx + 120, dyy - 40, bxx + 120, byy + 30,
                     bxx + R, byy + 8, POS))
    frags.append(text(dxx + 128, (dyy + byy)/2 + 4, "зворотне", size=11.5, color=POS, bold=True, anchor="start"))
    frags.append(text(dxx + 128, (dyy + byy)/2 + 20, "ребро → цикл", size=11.5, color=POS, bold=True, anchor="start"))

    # вершини поверх ребер
    for n, (x, y, fill, tcol) in nodes.items():
        frags.append(circle(x, y, R, fill=fill, stroke=LINE, sw=2))
        frags.append(text(x, y + 6, n, size=17, bold=True, color=tcol))

    return render(os.path.join(IMG, 'dfs-colors-cycle.svg'), W, H, *frags)


# ── Фігура 5 (вставка math-coupling-metrics): головна послідовність A+I=1 і відстань D ──
def fig_main_sequence():
    W, H = 640, 560
    frags = []
    frags.append(text(W/2, 30, "Головна послідовність: A + I = 1", size=17, bold=True))

    # система координат: I по горизонталі (0..1), A по вертикалі (0..1)
    ox, oy = 140, 470          # початок осей (екранний кут 0,0)
    L = 340                    # довжина осі в px (одиниця = L)
    def px(i, a):              # (I,A) -> екранні координати
        return ox + i * L, oy - a * L

    # осі
    frags.append(arrow(ox, oy, ox + L + 26, oy, color=INK, sw=1.6))          # вісь I →
    frags.append(arrow(ox, oy, ox, oy - L - 26, color=INK, sw=1.6))          # вісь A ↑
    frags.append(text(ox + L + 22, oy + 24, "I (нестабільність)", size=12, color=INK, anchor="end"))
    frags.append(text(ox - 44, oy - L/2, "A", size=13, color=INK, bold=True, anchor="middle"))
    frags.append(text(ox - 44, oy - L/2 + 18, "абстр.", size=10.5, color=MUTED, anchor="middle"))
    # позначки 0 і 1 на осях
    frags.append(text(ox, oy + 24, "0", size=11, color=MUTED))
    frags.append(text(ox + L, oy + 24, "1", size=11, color=MUTED))
    frags.append(text(ox - 18, oy + 4, "0", size=11, color=MUTED))
    frags.append(text(ox - 18, oy - L + 4, "1", size=11, color=MUTED))

    # головна послідовність: пряма від (I=0,A=1) до (I=1,A=0)
    x0, y0 = px(0, 1)
    x1, y1 = px(1, 0)
    frags.append(line(x0, y0, x1, y1, color=FIELD, sw=3))
    # підпис прямої — праворуч від верхнього кінця, щоб не лягти на саму лінію
    frags.append(text(x0 + 96, y0 + 8, "A + I = 1", size=12.5, color=FIELD, bold=True, anchor="start"))
    frags.append(text(x0 + 96, y0 + 26, "(здорова смуга)", size=11, color=FIELD, anchor="start"))

    # зона болю — нижній лівий кут (I=0, A=0)
    bx, by = px(0, 0)
    frags.append(circle(bx, by, 7, fill="#fdeeec", stroke=POS, sw=2))
    fb, wb, hb = textbox(bx + 120, by - 34,
                         "ЗОНА БОЛЮ (I=0, A=0)\nстабільне й конкретне:\nтреба міняти — а не можна",
                         size=11, pad=8, fill="#fdeeec", stroke=POS, sw=1.4, color=INK)
    frags.append(line(bx + 7, by - 5, bx + 120 - wb/2, by - 34 + hb/2, color=POS, sw=1.2, dash="4 3"))
    frags.append(fb)

    # зона марності — верхній правий кут (I=1, A=1)
    ux, uy = px(1, 1)
    frags.append(circle(ux, uy, 7, fill="#eaf0fd", stroke=NEG, sw=2))
    fu, wu, hu = textbox(ux - 108, uy + 34,
                         "ЗОНА МАРНОСТІ (I=1, A=1)\nабстрактне без клієнтів",
                         size=11, pad=8, fill="#eaf0fd", stroke=NEG, sw=1.4, color=INK)
    frags.append(line(ux - 7, uy + 5, ux - 108 + wu/2, uy + 34 - hu/2, color=NEG, sw=1.2, dash="4 3"))
    frags.append(fu)

    # приклад-пакет осторонь прямої + перпендикуляр D до неї
    pi, pa = 0.28, 0.28                 # точка (I,A) під прямою
    ppx, ppy = px(pi, pa)
    # нога перпендикуляра на пряму I+A=1: I'=(1+pi−pa)/2, A'=(1−pi+pa)/2
    fi, fa = (1 + pi - pa) / 2, (1 - pi + pa) / 2
    fpx, fpy = px(fi, fa)
    frags.append(line(ppx, ppy, fpx, fpy, color=INK, sw=1.8, dash="5 3"))
    frags.append(circle(ppx, ppy, 6, fill=INK, stroke=INK, sw=1))
    frags.append(text(ppx - 12, ppy + 22, "пакет", size=11, color=INK, anchor="end"))
    # підпис D — праворуч від перпендикуляра, у просвіті між лінією й прямою
    mxp, myp = (ppx + fpx) / 2, (ppy + fpy) / 2
    frags.append(text(mxp + 16, myp - 2, "D = |A+I−1|", size=12, color=INK, bold=True, anchor="start"))

    return render(os.path.join(IMG, 'main-sequence.svg'), W, H, *frags)


if __name__ == '__main__':
    p1 = fig_prescriptive_vs_descriptive()
    p2 = fig_erosion_loop()
    p3 = fig_drift_vs_erosion()
    p4 = fig_dfs_colors_cycle()
    p5 = fig_main_sequence()
    print("OK", p1, p2, p3, p4, p5)
