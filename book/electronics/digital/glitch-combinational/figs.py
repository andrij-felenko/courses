# -*- coding: utf-8 -*-
# Фігури теми «Глітчі в комбінаційних схемах». svgkit імпортуємо, не переписуємо (§5 AUTHORING).
# Вивід — у ./img/. Після запуску: python ../../../../scripts/svgcheck.py img --min-font 8
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def _poly(pts, color, sw):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (d, color, sw))


# ── 1. Звідки береться глітч: два шляхи з різними затримками ──────────────────
def fig_mechanism():
    W, H = 720, 470
    el = []
    el.append(text(W / 2, 26, "Глітч народжується з гонки двох шляхів", size=16, bold=True))

    # схема вгорі: A йде на AND напряму і через інвертор; вихід — OR
    ay = 70
    el.append(text(60, ay + 5, "A", size=15, bold=True, anchor="end"))
    el.append(line(64, ay, 130, ay, color=INK, sw=2))           # спільний вузол A
    el.append(circle(130, ay, 3, fill=INK, stroke=INK))
    # верхній шлях: напряму у верхній AND
    el.append(line(130, ay, 300, ay, color=INK, sw=2))
    # нижній шлях: через інвертор (затримка!)
    el.append(line(130, ay, 130, ay + 70, color=INK, sw=2))
    inv_x = 175
    el.append('<path d="M%d %d L%d %d L%d %d Z" fill="#eef2ff" stroke="%s" stroke-width="2"/>'
              % (inv_x, ay + 70 - 16, inv_x, ay + 70 + 16, inv_x + 30, ay + 70, NEG))
    el.append(circle(inv_x + 34, ay + 70, 4, fill=BG, stroke=NEG, sw=2))
    el.append(text(inv_x + 15, ay + 70 + 36, "інвертор", size=10.5, color=MUTED))
    el.append(text(inv_x + 15, ay + 70 + 49, "(затримка)", size=10.5, color=POS))
    el.append(line(inv_x + 38, ay + 70, 300, ay + 70, color=INK, sw=2))
    # вихідний вентиль OR
    orx, ory = 310, ay + 35
    el.append(rect(orx, ory - 28, 80, 56, fill="#fdecea", stroke=POS, sw=2))
    el.append(text(orx + 40, ory + 6, "OR", size=15, bold=True))
    el.append(line(390, ory, 470, ory, color=INK, sw=2))
    el.append(text(478, ory + 5, "вихід", size=12, color=MUTED, anchor="start"))

    # часові діаграми внизу
    L, R = 120, 660
    t0 = 200                     # момент перемикання A: 1 → 0
    d = 70                       # затримка нижнього (інвертованого) плеча
    def row(y, label, col):
        el.append(text(L - 14, y + 5, label, size=11.5, color=MUTED, anchor="end"))
        el.append(line(L - 6, y - 22, L - 6, y + 12, color=MUTED, sw=1))

    yA = 245
    yNA = 300
    yY = 360
    hi, lo = -20, 8              # відносні зсуви рівнів

    # A: 1 → 0 у момент t0
    row(yA, "A", NEG)
    el.append(_poly([(L, yA + hi), (t0, yA + hi), (t0, yA + lo), (R, yA + lo)], NEG, 2.4))
    # NOT A (із затримкою d): 0 → 1 пізніше на d
    row(yNA, "A (інв.)", NEG)
    el.append(_poly([(L, yNA + lo), (t0 + d, yNA + lo), (t0 + d, yNA + hi), (R, yNA + hi)], NEG, 2.4))
    # вихід: на коротку мить ОБА плеча в 0 → провал (для статичної 1) АБО сплеск.
    # Тут показуємо короткий хибний 0 між t0 і t0+d (вихід мав лишитися 1).
    row(yY, "вихід", POS)
    el.append(_poly([(L, yY + hi), (t0, yY + hi), (t0, yY + lo),
                     (t0 + d, yY + lo), (t0 + d, yY + hi), (R, yY + hi)], POS, 2.6))
    # підсвітити вікно глітча
    el.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff3cd" '
              'stroke="#d39e00" stroke-width="1.2" rx="3"/>' % (t0, yY - 26, d, 44))
    el.append(line(t0, yA + lo, t0, yY + 18, color=MUTED, sw=1, dash="3,3"))
    el.append(line(t0 + d, yNA + hi, t0 + d, yY + 18, color=MUTED, sw=1, dash="3,3"))
    # підпис «глітч» — винесений праворуч-униз із виноскою, щоб не накладатися
    glx, gly = t0 + d + 86, yY + 30
    b, w, h = textbox(glx, gly, "глітч", size=12.5, bold=True,
                      fill="#fff3cd", stroke="#d39e00")
    el.append(arrow(glx - w / 2 - 4, gly - 6, t0 + d / 2 + 4, yY + 14, color="#d39e00", sw=1.6))
    el.append(b)
    el.append(text(t0 + d + 70, yY - 30, "вихід мав лишитися 1", size=11, color=MUTED, anchor="start"))

    b, w, h = fitbox(L, H - 62, R - L, 42,
                     "Поки інвертоване плече «доганяє», обидва входи OR на мить нулі —\n"
                     "і вихід хибно провалюється, хоч усталено мав стояти на 1.",
                     size=12.5, fill=BG, stroke=MUTED), 0, 0
    el.append(b)
    render(os.path.join(OUT, "mechanism.svg"), W, H, *el)


# ── 2. Статична 1-небезпека на карті Карно: розрив між двома накривками ───────
def fig_kmap_hazard():
    W, H = 720, 420
    el = []
    el.append(text(W / 2, 26, "Небезпека — там, де перехід «випадає» між двома накривками", size=15, bold=True))

    # карта 4 клітинки по C (стовпці) × A (рядки) при B=1: f = A·B + B̄... спрощено покажемо
    # Класика: f = A·C̄ + B·C. Перехід C: 1→0 при A=B=1 «вислизає» між двома групами.
    # Намалюємо карту 2×2 за змінними (рядок=A, стовпець=C) при B=1.
    gx, gy = 150, 90
    cell = 90
    # підписи осей
    el.append(text(gx + cell, gy - 16, "C = 1        C = 0", size=12, color=MUTED))
    el.append(text(gx - 16, gy + cell / 2 + 4, "A=1", size=12, color=MUTED, anchor="end"))
    el.append(text(gx - 16, gy + cell + cell / 2 + 4, "A=0", size=12, color=MUTED, anchor="end"))
    el.append(text(gx + cell, gy - 36, "(при B = 1)", size=11.5, color=MUTED))

    # значення f у клітинках: рядок A=1: C=1 →1 (B·C), C=0 →1 (A·C̄)
    #                          рядок A=0: C=1 →1 (B·C), C=0 →0
    vals = [["1", "1"], ["1", "0"]]
    for r in range(2):
        for c in range(2):
            x = gx + c * cell
            y = gy + r * cell
            el.append(rect(x, y, cell, cell, fill=BG, stroke=LINE, sw=1.5, rx=4))
            el.append(text(x + cell / 2, y + cell / 2 + 7, vals[r][c], size=22, bold=True))

    # накривка B·C (лівий стовпець, обидва рядки) — синя
    el.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" fill="none" '
              'stroke="%s" stroke-width="3"/>' % (gx - 8, gy - 8, cell + 16, 2 * cell + 16, NEG))
    el.append(text(gx + cell / 2, gy + 2 * cell + 28, "група B·C", size=12, bold=True, color=NEG))
    # накривка A·C̄ (верхній рядок, правий стовпець) — зелена
    el.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" fill="none" '
              'stroke="%s" stroke-width="3" stroke-dasharray="6,4"/>'
              % (gx + cell - 8, gy - 4, cell + 16, cell + 8, FIELD))
    el.append(text(gx + cell + cell / 2, gy - 50, "група A·C̄", size=12, bold=True, color=FIELD))

    # стрілка переходу: верхня-права (A=1,C=0) ↔ верхня-ліва (A=1,C=1)
    ax1 = gx + cell + cell / 2
    ax2 = gx + cell / 2
    ayv = gy + cell / 2
    el.append(arrow(ax1, ayv, ax2, ayv, color=POS, sw=2.4))
    el.append(arrow(ax2, ayv, ax1, ayv, color=POS, sw=2.4))
    b, w, h = textbox(gx + cell, gy + cell + 6, "C: 1 ⇄ 0", size=12, bold=True,
                      fill="#fdecea", stroke=POS)
    el.append(b)

    b, w, h = fitbox(110, H - 116, W - 220, 80,
                     "Обидві клітинки переходу = 1, але вони в РІЗНИХ групах (B·C і A·C̄).\n"
                     "Жодна одна група не накриває обидві, тож під час перемикання C\n"
                     "одна група вже відпустила, а друга ще не схопила — на стику\n"
                     "виходить хибний 0. Це і є статична 1-небезпека.",
                     size=12.5, fill="#fff7e6", stroke="#d39e00"), 0, 0
    el.append(b)
    render(os.path.join(OUT, "kmap-hazard.svg"), W, H, *el)


# ── 3. Накривний (consensus) член зашиває розрив ─────────────────────────────
def fig_consensus():
    W, H = 720, 420
    el = []
    el.append(text(W / 2, 26, "Накривний член A·B накриває стик — глітч зникає", size=16, bold=True))

    gx, gy = 150, 90
    cell = 90
    el.append(text(gx + cell, gy - 16, "C = 1        C = 0", size=12, color=MUTED))
    el.append(text(gx - 16, gy + cell / 2 + 4, "A=1", size=12, color=MUTED, anchor="end"))
    el.append(text(gx - 16, gy + cell + cell / 2 + 4, "A=0", size=12, color=MUTED, anchor="end"))
    el.append(text(gx + cell, gy - 36, "(при B = 1)", size=11.5, color=MUTED))

    vals = [["1", "1"], ["1", "0"]]
    for r in range(2):
        for c in range(2):
            x = gx + c * cell
            y = gy + r * cell
            el.append(rect(x, y, cell, cell, fill=BG, stroke=LINE, sw=1.5, rx=4))
            el.append(text(x + cell / 2, y + cell / 2 + 7, vals[r][c], size=22, bold=True))

    # дві старі групи — блідо
    el.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" fill="none" '
              'stroke="%s" stroke-width="2" opacity="0.4"/>' % (gx - 6, gy - 6, cell + 12, 2 * cell + 12, NEG))
    el.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" fill="none" '
              'stroke="%s" stroke-width="2" stroke-dasharray="6,4" opacity="0.4"/>'
              % (gx + cell - 6, gy - 4, cell + 12, cell + 8, FIELD))
    # новий накривний член A·B — верхній рядок цілком, яскраво-червоний
    el.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="12" fill="#fdecea" '
              'fill-opacity="0.55" stroke="%s" stroke-width="3.5"/>'
              % (gx - 12, gy - 12, 2 * cell + 24, cell + 24, POS))
    el.append(text(gx + cell, gy - 50, "накривний член A·B", size=13, bold=True, color=POS))

    # формула
    b, w, h = textbox(W / 2, gy + 2 * cell + 36,
                      "f = B·C + A·C̄  +  A·B",
                      size=16, bold=True, fill="#f4f6f8", stroke=INK)
    el.append(b)
    el.append(text(W / 2, gy + 2 * cell + 62, "↑ зайвий за логікою, але тримає вихід під час переходу C",
                   size=11.5, color=MUTED))

    b, w, h = fitbox(110, H - 92, W - 220, 62,
                     "Член A·B дорівнює 1 на ВСЬОМУ верхньому рядку — і поки C перемикається,\n"
                     "саме він утримує вихід у 1. Перемикання C більше не залишає виходу\n"
                     "без жодної одиничної групи: розриву нема, глітча нема.",
                     size=12.5, fill="#eafaf0", stroke=FIELD), 0, 0
    el.append(b)
    render(os.path.join(OUT, "consensus.svg"), W, H, *el)


# ── 4. Кому глітч байдужий, а кому ні ─────────────────────────────────────────
def fig_who_cares():
    W, H = 720, 360
    el = []
    el.append(text(W / 2, 26, "Глітч на вході даних — пробачимо; глітч на такті чи дозволі — ні", size=14.5, bold=True))

    L, R = 70, 660
    t_glitch = 360
    gw = 26

    # рядок 1: вихід логіки з глітчем
    yL = 80
    el.append(text(L - 12, yL + 5, "логіка", size=11.5, color=MUTED, anchor="end"))
    el.append(_poly([(L, yL - 18), (t_glitch, yL - 18), (t_glitch, yL + 8),
                     (t_glitch + gw, yL + 8), (t_glitch + gw, yL - 18), (R, yL - 18)], POS, 2.4))
    b, w, h = textbox(t_glitch + gw / 2, yL + 30, "глітч", size=11, bold=True,
                      fill="#fff3cd", stroke="#d39e00")
    el.append(b)

    # рядок 2: такт — фронт ПІСЛЯ усталення
    yC = 175
    t_clk = R - 120
    el.append(text(L - 12, yC + 5, "такт", size=11.5, color=MUTED, anchor="end"))
    el.append(_poly([(L, yC + 8), (t_clk, yC + 8), (t_clk, yC - 18), (R, yC - 18)], NEG, 2.4))
    el.append(line(t_clk, yC - 26, t_clk, yC + 18, color=INK, sw=2))
    el.append(text(t_clk, yC - 32, "фронт", size=10.5, color=INK))
    # зона дозволеного глітча (до setup перед фронтом) — зелена
    el.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eafaf0" '
              'stroke="%s" stroke-width="1.2" rx="3"/>' % (L, yL - 40, t_clk - 40 - L, 70, FIELD))
    el.append(text(L + 10, yL - 46, "вікно, де глітч нікому не шкодить", size=11, color=FIELD, anchor="start"))
    el.append(line(t_clk - 40, yL - 40, t_clk - 40, yC + 22, color=FIELD, sw=1.2, dash="4,3"))
    el.append(text(t_clk - 40, yC + 38, "setup", size=10.5, color=FIELD, anchor="middle"))

    # рядок 3: а ось глітч НА такті/дозволі — хибний фронт
    yE = 270
    el.append(text(L - 12, yE + 5, "дозвіл / такт", size=11.5, color=MUTED, anchor="end"))
    el.append(_poly([(L, yE + 8), (t_glitch, yE + 8), (t_glitch, yE - 18),
                     (t_glitch + gw, yE - 18), (t_glitch + gw, yE + 8), (R, yE + 8)], POS, 2.6))
    el.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" '
              'stroke="%s" stroke-width="1.3" rx="3"/>' % (t_glitch - 4, yE - 26, gw + 8, 44, POS))
    el.append(text(t_glitch + gw + 60, yE + 5, "хибний фронт → залік сміття!", size=11.5,
                   color=POS, anchor="start", bold=True))

    b, w, h = fitbox(L, H - 40, R - L, 30,
                     "Защіпка читає вхід даних лише за фронтом такту, коли все вже усталилося — глітч до того часу зник. "
                     "Але глітч на самому такті чи на дозволі — це зайвий фронт: защіпнеться випадкове значення.",
                     size=12, fill=BG, stroke=MUTED), 0, 0
    el.append(b)
    render(os.path.join(OUT, "who-cares.svg"), W, H, *el)


# ── 5. Куб істинності: накривний член = грань, що містить ребро переходу ──────
#    (для вставки math-consensus.md)
def fig_cube():
    W, H = 720, 470
    el = []
    el.append(text(W / 2, 26, "Накривний член A·B — це ребро куба, натягнуте на перехід", size=15, bold=True))

    # 3-куб у координатах (A, B, C). Вершина = мінтерм; проєкція на площину.
    # Осі: A → праворуч, B → угору, C → «в глибину» (діагональ угору-праворуч).
    ox, oy = 150, 340                 # початок (A=0,B=0,C=0)
    ax, ay = 220, 0                   # напрям A
    bx, by = 0, -220                  # напрям B
    cx, cy = 120, -95                 # напрям C (перспектива)

    def V(a, b, c):
        return (ox + a * ax + b * bx + c * cx,
                oy + a * ay + b * by + c * cy)

    verts = {(a, b, c): V(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)}

    # ребра куба (сірі)
    edges = []
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                if a == 0: edges.append(((0, b, c), (1, b, c)))
                if b == 0: edges.append(((a, 0, c), (a, 1, c)))
                if c == 0: edges.append(((a, b, 0), (a, b, 1)))
    for p, q in edges:
        x1, y1 = verts[p]; x2, y2 = verts[q]
        el.append(line(x1, y1, x2, y2, color="#c8ccd2", sw=1.6))

    # накривний член A·B (A=1,B=1): з 3 змінних це ребро {A=1,B=1, C∈{0,1}} —
    # рівно те ребро, що з'єднує мінтерми 110 і 111. Підсвітимо його.
    p0 = verts[(1, 1, 0)]; p1 = verts[(1, 1, 1)]
    el.append(line(p0[0], p0[1], p1[0], p1[1], color=POS, sw=6))

    # значення функції f = B·C + A·C̄ у кожній вершині → колір вершини
    def f(a, b, c):
        return (b and c) or (a and (1 - c))
    for (a, b, c), (x, y) in verts.items():
        one = f(a, b, c)
        col = INK if one else BG
        el.append(circle(x, y, 8, fill=(POS if (a == 1 and b == 1) else col),
                         stroke=INK, sw=1.8))
        # мітка координат біля вершини — назовні від куба
        lbl = "%d%d%d" % (a, b, c)
        dx = -16 if x <= ox + 60 else 13
        el.append(text(x + dx, y + 4, lbl, size=10, color=MUTED,
                       anchor=("end" if dx < 0 else "start")))

    # осі-підказки
    el.append(text(ox + ax + 8, oy + ay + 5, "A →", size=12, color=MUTED, anchor="start"))
    el.append(text(ox + bx - 8, oy + by - 6, "B ↑", size=12, color=MUTED, anchor="end"))
    el.append(text(ox + cx + 42, oy + cy + 6, "C ↗", size=12, color=MUTED, anchor="start"))

    # виноска на ребро A·B — з вільного правого поля, стрілкою до середини ребра
    midx, midy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2   # ≈ (430, 72)
    b, w, h = textbox(588, 172, "ребро = член A·B\n(A=1, B=1, C будь-яке)", size=11.5, bold=True,
                      fill="#fdecea", stroke=POS)
    el.append(arrow(588, 172 - h / 2 - 4, midx + 18, midy + 8, color=POS, sw=1.7))
    el.append(b)

    # легенда — у вільному верхньому лівому куті, стовпчиком
    lx, ly = 60, 96
    el.append(circle(lx, ly, 7, fill=INK, stroke=INK))
    el.append(text(lx + 14, ly + 4, "f = 1", size=11.5, color=INK, anchor="start"))
    el.append(circle(lx, ly + 24, 7, fill=BG, stroke=INK))
    el.append(text(lx + 14, ly + 28, "f = 0", size=11.5, color=INK, anchor="start"))
    el.append(circle(lx, ly + 48, 7, fill=POS, stroke=INK))
    el.append(text(lx + 14, ly + 52, "ребро 110 ⇄ 111", size=11.5, color=POS, anchor="start"))

    b, w, h = fitbox(90, H - 74, W - 180, 54,
                     "Мінтерми 110 і 111 (A=B=1, C міняється) — сусідні вершини, з'єднані ребром.\n"
                     "Обидві = 1, але накриті РІЗНИМИ членами (B·C і A·C̄). Член A·B — це рівно те\n"
                     "ребро, натягнуте на обидва кінці переходу; воно тримає їх, поки C біжить.",
                     size=12.5, fill="#eafaf0", stroke=FIELD), 0, 0
    el.append(b)
    render(os.path.join(OUT, "cube-consensus.svg"), W, H, *el)


# ── 6. Функційна небезпека: діагональ між двома одиницями через нульовий кут ───
#    (для вставки math-consensus.md) — жоден накривний член не рятує
def fig_function_hazard():
    W, H = 720, 440
    el = []
    el.append(text(W / 2, 26, "Функційна небезпека: між двома одиницями лежить нульовий кут", size=15, bold=True))

    gx, gy = 210, 92
    cell = 96
    # f = A·B + Ā·B̄  (рівність A=B). Діагональні кути = 1, побічні = 0.
    el.append(text(gx + cell, gy - 16, "B = 0        B = 1", size=12, color=MUTED))
    el.append(text(gx - 16, gy + cell / 2 + 4, "A=0", size=12, color=MUTED, anchor="end"))
    el.append(text(gx - 16, gy + cell + cell / 2 + 4, "A=1", size=12, color=MUTED, anchor="end"))
    el.append(text(gx + cell, gy - 40, "f = A·B + Ā·B̄", size=12.5, bold=True, color=INK))

    #        B=0  B=1
    # A=0     1    0
    # A=1     0    1
    vals = [["1", "0"], ["0", "1"]]
    for r in range(2):
        for c in range(2):
            x = gx + c * cell
            y = gy + r * cell
            fill = "#eafaf0" if vals[r][c] == "1" else BG
            el.append(rect(x, y, cell, cell, fill=fill, stroke=LINE, sw=1.5, rx=4))
            el.append(text(x + cell / 2, y + cell / 2 + 7, vals[r][c], size=22, bold=True))

    # перехід 00 → 11 (обидва входи міняються). Обидва кінці = 1.
    start = (gx + 0.5 * cell, gy + 0.5 * cell)   # A=0,B=0  (=1)
    end   = (gx + 1.5 * cell, gy + 1.5 * cell)   # A=1,B=1  (=1)
    el.append(arrow(start[0], start[1], end[0], end[1], color=POS, sw=2.6))
    # два можливі проміжні кути — обидва НУЛІ (кільце-виноска)
    for (cc, rr) in ((1, 0), (0, 1)):
        px, py = gx + (cc + 0.5) * cell, gy + (rr + 0.5) * cell
        el.append(circle(px, py, 13, fill="none", stroke=POS, sw=2.2))
    b, w, h = textbox(gx + 2 * cell + 104, gy + cell,
                      "00 → 11\n(A і B разом)", size=11.5, bold=True,
                      fill="#fdecea", stroke=POS)
    el.append(arrow(gx + 2 * cell + 104 - w / 2 - 4, gy + cell, end[0] + 6, end[1] - 4,
                    color=POS, sw=1.6))
    el.append(b)

    b, w, h = fitbox(80, H - 122, W - 160, 92,
                     "Обидва кінці переходу = 1, отже вихід МАВ стояти на 1. Але A і B не перемкнуться\n"
                     "точно одночасно: хто випередить — і схема на мить осяде в куті 10 або 01, а там\n"
                     "f = 0. Вихід провалиться в 0, і це не вада реалізації, а сама функція: між двома\n"
                     "одиницями по діагоналі лежить нуль. Жоден накривний член цього не сховає — накрити\n"
                     "нульовий кут одиничною групою не можна. Рятує лише те, щоб A і B НЕ мінялися разом.",
                     size=12, fill="#fff7e6", stroke="#d39e00"), 0, 0
    el.append(b)
    render(os.path.join(OUT, "function-hazard.svg"), W, H, *el)


# ── 7. Хронологія приборкання небезпек (для вставки hist-huffman.md) ──────────
def fig_timeline():
    W, H = 730, 486
    el = []
    el.append(text(W / 2, 28, "Як приборкали небезпеки: ключові кроки", size=16, bold=True))

    axis_x = 128
    top, bot = 66, H - 34
    el.append(line(axis_x, top, axis_x, bot, color=MUTED, sw=2))

    rows = [
        ("1937", "Блейк", "поняття «згоди» (consensus) двох членів —\nще в чистій алгебрі логіки, без жодних схем", NEG),
        ("1952", "Гаффмен", "«код мінімальної надмірності» — студентська\nробота, що обійшла власного викладача Фано", MUTED),
        ("1957", "Гаффмен", "Design and Use of Hazard-Free Switching Networks:\nдовів, що безглітчеву схему можна побудувати ЗАВЖДИ", POS),
        ("1959", "Унґер", "переніс небезпеки на асинхронні автомати —\nде глітч не «метушня», а вже хибний стан", NEG),
        ("1962", "Мак-Класкі", "Transient behavior… — систематика перехідних\nпроцесів у комбінаційній логіці", MUTED),
        ("1964–65", "Йоелі·Рінон,\nАйхельберґер", "троїста (ternary) алгебра: небезпеку рахують\nмашинально, зокрема й при зміні кількох входів", FIELD),
    ]
    n = len(rows)
    for i, (yr, who, what, col) in enumerate(rows):
        y = top + (i + 0.5) * (bot - top) / n
        el.append(circle(axis_x, y, 6, fill=col, stroke=INK, sw=1.6))
        el.append(text(axis_x - 14, y + 4, yr, size=12, bold=True, color=INK, anchor="end"))
        cardx = axis_x + 30
        el.append(line(axis_x + 6, y, cardx, y, color=MUTED, sw=1.3))
        whoL = who.split("\n")
        nbw = max(text_width(ln, 12, True) for ln in whoL) + 20
        nby = y - (len(whoL) * 12 * 1.25) / 2 - 8
        nb, w2, h2 = textbox(cardx + nbw / 2, nby, who, size=12, bold=True,
                             fill="#f4f6f8", stroke=col)
        el.append(nb)
        el.append(mtext(cardx + 2, nby + h2 / 2 + 12, what, size=11.5, color=MUTED,
                        anchor="start", lh=1.25))

    render(os.path.join(OUT, "timeline.svg"), W, H, *el)


if __name__ == "__main__":
    fig_mechanism()
    fig_kmap_hazard()
    fig_consensus()
    fig_who_cares()
    fig_cube()
    fig_function_hazard()
    fig_timeline()
    print("OK: 7 figures ->", OUT)
