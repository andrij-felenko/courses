# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

PHI = (1 + 5 ** 0.5) / 2
GOLD = "#d98a1e"   # акцент спіралі (не семантичний +/−, тому окремий теплий колір)


def fibs(n):
    f = [0, 1]
    while len(f) <= n:
        f.append(f[-1] + f[-2])
    return f


# ── Фігура 1: відношення сусідів завмирає на φ ───────────────────────────────
# Fₙ₊₁/Fₙ по черзі перескакує золоту межу згори (червоні точки) і знизу (сині),
# і розмах перескоку швидко тане — послідовність затискає φ у лещата.
def fig_ratio():
    W, H = 820, 452
    ox, x_right = 96, 772
    y_top, y_bot = 92, 388
    vlo, vhi = 0.9, 2.1
    F = fibs(14)
    ratios = [F[k + 1] / F[k] for k in range(1, 13)]   # k = 1..12

    def X(k):
        return ox + (k - 1) / 11.0 * (x_right - ox)

    def Y(v):
        return y_bot - (v - vlo) / (vhi - vlo) * (y_bot - y_top)

    parts = []
    # осі
    parts.append(arrow(ox, y_bot, x_right + 20, y_bot, color=INK, sw=1.8))
    parts.append(arrow(ox, y_bot, ox, y_top - 14, color=INK, sw=1.8))
    parts.append(text(x_right + 22, y_bot + 4, 'k', 13, INK, 'start', italic=True))
    parts.append(text(ox - 66, y_top - 18, 'Fₖ₊₁ / Fₖ', 12, INK, 'start', bold=True))

    # горизонтальні орієнтири по y
    for v in [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]:
        yy = Y(v)
        parts.append(line(ox, yy, x_right, yy, color="#eceef1", sw=1.0))
        parts.append(text(ox - 10, yy + 4, '%.1f' % v, 11, MUTED, 'end'))

    # золота межа φ
    yphi = Y(PHI)
    parts.append(line(ox, yphi, x_right, yphi, color=FIELD, sw=1.8, dash="7 5"))
    parts.append(text(ox + 6, yphi - 8, 'φ = (1+√5)/2 ≈ 1.618', 12, FIELD, 'start', bold=True))

    # позначки k на осі
    for k in range(1, 13):
        parts.append(text(X(k), y_bot + 20, str(k), 11, MUTED, 'middle'))

    # ламана через точки
    pts = ' '.join('%.1f,%.1f' % (X(k + 1), Y(ratios[k])) for k in range(12))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (pts, "#9aa2ad"))

    # точки: над φ — червоні, під φ — сині; підписи для перших шести (де є місце)
    lbl = {0: 'below', 1: 'above', 2: 'below', 3: 'above', 4: 'below', 5: 'above'}
    for k in range(12):
        v = ratios[k]
        col = POS if v > PHI else NEG
        parts.append(circle(X(k + 1), Y(v), 4.2, fill=col, stroke="#ffffff", sw=1.2))
        if k in lbl:
            dy = -12 if lbl[k] == 'above' else 16
            parts.append(text(X(k + 1), Y(v) + dy, '%.3f' % v, 10.5, col, 'middle'))

    # маркери «згори» / «знизу»
    parts.append(text(X(2), Y(ratios[1]) - 26, 'згори', 11, POS, 'middle', italic=True))
    parts.append(text(X(3), Y(ratios[2]) + 30, 'знизу', 11, NEG, 'middle', italic=True))

    render(os.path.join(IMG, 'ratio.svg'), W, H, *parts,
           title='Відношення сусідніх чисел Фібоначчі затискає золоту межу φ')


# ── Фігура 2: квадрати замощують прямокутник Fₙ×Fₙ₊₁, а дуги дають спіраль ────
# Квадрати зі сторонами 1,1,2,3,5,8 без зазорів заповнюють прямокутник 8×13:
# площа, порахована двічі, і є тотожністю Σ Fₖ² = Fₙ·Fₙ₊₁. Дуги в квадратах
# складаються у знайому спіраль.
def fig_squares():
    W, H = 730, 486
    u = 40
    RX, RY = 70, 66                      # лівий-верхній кут прямокутника
    right, bot = RX + 13 * u, RY + 8 * u

    def PX(gx):
        return RX + gx * u

    def PY(gy):
        return RY + gy * u

    parts = []

    # квадрати: (grid_x, grid_y, side, підпис, кегль)
    squares = [
        (0, 0, 8, '8', 30), (8, 0, 5, '5', 24), (10, 5, 3, '3', 18),
        (8, 6, 2, '2', 15), (9, 5, 1, '1', 12), (8, 5, 1, '1', 12),
    ]
    for gx, gy, s, lab, fs in squares:
        parts.append(rect(PX(gx), PY(gy), s * u, s * u, fill="#f6f8fa", stroke=LINE, sw=1.4, rx=0))
        parts.append(text(PX(gx) + s * u / 2, PY(gy) + s * u / 2 + fs * 0.35, lab, fs, MUTED, 'middle', bold=True))

    # зовнішній контур прямокутника
    parts.append(rect(RX, RY, 13 * u, 8 * u, fill="none", stroke=INK, sw=2.2, rx=0))

    # спіраль: чверть-кола (центр, старт, кінець у grid-координатах)
    arcs = [
        ((9, 6), (10, 6), (9, 5)),   # 1A
        ((9, 6), (9, 5), (8, 6)),    # 1B
        ((10, 6), (8, 6), (10, 8)),  # 2
        ((10, 5), (10, 8), (13, 5)), # 3
        ((8, 5), (13, 5), (8, 0)),   # 5
        ((8, 8), (8, 0), (0, 8)),    # 8
    ]
    poly = []
    for (cx, cy), (sx, sy), (ex, ey) in arcs:
        a0 = math.atan2(sy - cy, sx - cx)
        a1 = math.atan2(ey - cy, ex - cx)
        d = a1 - a0
        while d <= -math.pi:
            d += 2 * math.pi
        while d > math.pi:
            d -= 2 * math.pi
        r = math.hypot(sx - cx, sy - cy)
        N = 26
        for i in range(N + 1):
            a = a0 + d * i / N
            poly.append('%.1f,%.1f' % (PX(cx + r * math.cos(a)), PY(cy + r * math.sin(a))))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="4" '
                 'stroke-linecap="round" stroke-linejoin="round"/>' % (' '.join(poly), GOLD))

    # розміри сторін
    parts.append(text((RX + right) / 2, bot + 30, '13', 15, INK, 'middle', bold=True))
    parts.append(text(RX - 26, (RY + bot) / 2 + 5, '8', 15, INK, 'middle', bold=True))

    # права панель — сенс фігури
    px = right + 20
    parts.append(text(px, RY + 40, 'площа, порахована двічі:', 12, INK, 'start'))
    parts.append(text(px, RY + 66, '8 × 13 = 104', 13, INK, 'start', bold=True))
    parts.append(text(px, RY + 92, '1²+1²+2²', 12, MUTED, 'start'))
    parts.append(text(px, RY + 110, '+3²+5²+8²', 12, MUTED, 'start'))
    parts.append(text(px, RY + 128, '= 104', 12, MUTED, 'start'))
    b = fitbox(px - 4, RY + 150, 128, 52, 'Σ Fₖ² =\nFₙ · Fₙ₊₁',
               size=14, fill="#fff8e9", stroke=GOLD, sw=1.6, color=INK, bold=True)
    parts.append(b)

    render(os.path.join(IMG, 'squares.svg'), W, H, *parts,
           title='Квадрати Фібоначчі замощують прямокутник Fₙ × Fₙ₊₁')


# ── Фігура 3: періоди Пізано — остачі за модулем 4 ───────────────────────────
# Смуга остач за модулем 4: після шести клітинок пара (0,1) повертається, і
# візерунок починається спочатку. Скінченність можливих пар робить це неминучим.
def fig_pisano():
    W, H = 770, 286
    cw, ch = 50, 54
    RX, RY = 84, 116
    F = fibs(12)
    res = [f % 4 for f in F]              # 0,1,1,2,3,1,0,1,1,2,3,1,0
    N = len(F)                            # 13 клітинок: n = 0..12

    def CX(n):
        return RX + n * cw

    parts = []
    # підсвітка стартових пар (0,1) на початку кожного періоду
    for start in (0, 6, 12):
        for j in (0, 1):
            n = start + j
            if n < N:
                parts.append(rect(CX(n), RY, cw, ch, fill="#e7f7ee", stroke="none", sw=0, rx=0))

    # клітинки, справжнє Fₙ згори, остача всередині, n знизу
    for n in range(N):
        parts.append(rect(CX(n), RY, cw, ch, fill="none", stroke=LINE, sw=1.3, rx=0))
        col = FIELD if res[n] in (0,) and n in (0, 6, 12) else INK
        parts.append(text(CX(n) + cw / 2, RY - 12, str(F[n]), 11, MUTED, 'middle'))
        parts.append(text(CX(n) + cw / 2, RY + ch / 2 + 8, str(res[n]), 22, col, 'middle', bold=True))
        parts.append(text(CX(n) + cw / 2, RY + ch + 20, str(n), 11, MUTED, 'middle'))

    # межі періодів
    for n in (6, 12):
        parts.append(line(CX(n), RY - 6, CX(n), RY + ch + 6, color=NEG, sw=2.0, dash="5 4"))

    # підписи рядів
    parts.append(text(RX - 12, RY - 12, 'Fₙ:', 11, MUTED, 'end'))
    parts.append(text(RX - 12, RY + ch / 2 + 8, 'mod 4:', 12, INK, 'end', bold=True))

    # дужка над першим періодом
    by = RY - 40
    parts.append(line(CX(0), by, CX(6), by, color=INK, sw=1.6))
    parts.append(line(CX(0), by, CX(0), by + 8, color=INK, sw=1.6))
    parts.append(line(CX(6), by, CX(6), by + 8, color=INK, sw=1.6))
    parts.append(text((CX(0) + CX(6)) / 2, by - 8, 'π(4) = 6', 14, INK, 'middle', bold=True))

    # зворотна стрілка «та сама пара повертається»
    ay = RY + ch + 40
    parts.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
                 'stroke-width="1.8" stroke-dasharray="6 4" marker-end="url(#arrow)"/>'
                 % (CX(1) - 4, ay - 6, (CX(1) + CX(6)) / 2, ay + 30, CX(6) + 4, ay - 6, FIELD))
    parts.append(text((CX(1) + CX(6)) / 2 + 20, ay + 40, 'пара (0, 1) повертається — і візерунок повторюється',
                      12, FIELD, 'middle', italic=True))

    render(os.path.join(IMG, 'pisano.svg'), W, H, *parts,
           title='Остачі чисел Фібоначчі за модулем 4 замикаються в кільце')


# ── Фігура 4 (для вставки-історії): звідки в санскритській просодії те саме правило ─
# Ритм рядка на n мор: короткий склад — 1 мора, довгий — 2. Кожен ритм на 4 мори
# кінчається або коротким (спереду — будь-який ритм на 3 мори), або довгим (ритм
# на 2 мори). Звідси 5 = 3 + 2 — саме правило суми двох попередніх, задовго до кролів.
def fig_prosody():
    W, H = 800, 360
    u, ch = 28, 24                 # ширина однієї мори, висота клітинки складу
    SHORT = "#e7f7ee"              # короткий склад — зелений тон (1 мора)
    LONG = "#eaf0fd"               # довгий склад — синій тон (2 мори)

    def draw_pat(x, y, pat):
        out, cx, n = [], x, len(pat)
        for i, s in enumerate(pat):
            w = u if s == 'S' else 2 * u
            last = (i == n - 1)
            out.append(rect(cx, y, w, ch, fill=(SHORT if s == 'S' else LONG),
                            stroke=(GOLD if last else "#9aa2ad"),
                            sw=(2.6 if last else 1.2), rx=3))
            out.append(text(cx + w / 2, y + ch / 2 + 5, '1' if s == 'S' else '2',
                            12, MUTED, 'middle'))
            cx += w
        return out

    parts = []

    # легенда
    parts.append(rect(60, 44, u, ch, fill=SHORT, stroke="#9aa2ad", sw=1.2, rx=3))
    parts.append(text(60 + u + 10, 61, 'короткий склад = 1 мора', 13, INK, 'start'))
    parts.append(rect(330, 44, 2 * u, ch, fill=LONG, stroke="#9aa2ad", sw=1.2, rx=3))
    parts.append(text(330 + 2 * u + 10, 61, 'довгий склад = 2 мори', 13, INK, 'start'))

    # ЛІВА панель — ритми, що кінчаються коротким складом (3 шт.)
    parts.append(rect(52, 96, 160, 160, fill="#f2fbf5", stroke=FIELD, sw=1.4, rx=8))
    parts.append(text(132, 118, 'останній — КОРОТКИЙ', 12, FIELD, 'middle', bold=True))
    for i, pat in enumerate([['S', 'S', 'S', 'S'], ['S', 'L', 'S'], ['L', 'S', 'S']]):
        parts += draw_pat(76, 130 + i * 40, pat)

    # ПРАВА панель — ритми, що кінчаються довгим складом (2 шт.)
    parts.append(rect(270, 96, 160, 120, fill="#f0f4fe", stroke=NEG, sw=1.4, rx=8))
    parts.append(text(350, 118, 'останній — ДОВГИЙ', 12, NEG, 'middle', bold=True))
    for i, pat in enumerate([['S', 'S', 'L'], ['L', 'L']]):
        parts += draw_pat(294, 130 + i * 40, pat)

    # знаки «+» та «=»
    parts.append(text(240, 186, '+', 30, INK, 'middle', bold=True))
    parts.append(text(456, 166, '=', 30, INK, 'middle', bold=True))

    # результат
    parts.append(rect(486, 116, 286, 116, fill="#fff8e9", stroke=GOLD, sw=1.6, rx=8))
    parts.append(text(629, 152, '5 ритмів на 4 мори', 16, INK, 'middle', bold=True))
    parts.append(text(629, 186, 'C₄ = C₃ + C₂', 17, INK, 'middle', bold=True))
    parts.append(text(629, 212, '5  =  3  +  2', 14, MUTED, 'middle'))

    # нижній підпис
    parts.append(mtext(400, 298,
                       ['Кожен ритм на 4 мори кінчається або коротким складом (попереду — ритм на 3 мори),',
                        'або довгим (ритм на 2 мори): звідси 5 = 3 + 2 — правило суми двох попередніх.'],
                       12.5, INK, 'middle'))

    render(os.path.join(IMG, 'prosody.svg'), W, H, *parts,
           title='Звідки в санскритському віршуванні правило Фібоначчі')


# ── Фігура 5 (для вставки-проєкту): форма роботи — розгалуження проти сходження ─
# Ліворуч наївна рекурсія fib(5): кожен виклик породжує два, дерево росте як φⁿ
# (15 вузлів уже для F₅). Праворуч подвоєння: n щокроку ділиться навпіл, виходить
# одна коротка драбина завдовжки ≈ log₂n. Та сама відповідь — дві різні ціни.
def fig_costs():
    W, H = 880, 470
    parts = []

    # розділювач панелей
    parts.append(line(W / 2, 66, W / 2, H - 54, color="#e2e5ea", sw=1.4))

    # ── ЛІВА панель: дерево наївних викликів fib(5) ──────────────────────────
    parts.append(text(228, 62, 'наївна рекурсія: розгалуження', 15, POS, 'middle', bold=True))

    nleaves_box = [0]
    edges = []
    nodes2 = []

    def layout2(k, depth):
        if k < 2:
            x = nleaves_box[0]
            nleaves_box[0] += 1
            nodes2.append((k, depth, x, True))
            return (x, depth)
        cr = layout2(k - 1, depth + 1)
        cl = layout2(k - 2, depth + 1)
        x = (cr[0] + cl[0]) / 2.0
        nodes2.append((k, depth, x, False))
        edges.append(((x, depth), cr))
        edges.append(((x, depth), cl))
        return (x, depth)

    layout2(5, 0)
    nleaves = nleaves_box[0]                # 8 листків
    xL, xR = 44, 412
    yT, dy = 96, 50
    r = 14

    def NX(gx):
        return xL + gx / (nleaves - 1) * (xR - xL)

    def NY(depth):
        return yT + depth * dy

    for (x1, d1), (x2, d2) in edges:
        parts.append(line(NX(x1), NY(d1), NX(x2), NY(d2), color="#c3c8d0", sw=1.4))
    for k, depth, gx, leaf in nodes2:
        fill = "#eafaf0" if leaf else "#fdecea"
        stro = FIELD if leaf else POS
        parts.append(circle(NX(gx), NY(depth), r, fill=fill, stroke=stro, sw=1.6))
        parts.append(text(NX(gx), NY(depth) + 4, str(k), 12, INK, 'middle', bold=True))

    parts.append(text(228, NY(4) + 42, '15 викликів уже для F₅', 12.5, INK, 'middle', bold=True))
    parts.append(text(228, NY(4) + 62, 'загалом 2·Fₙ₊₁ − 1  —  росте як φⁿ', 11.5, MUTED, 'middle'))

    # ── ПРАВА панель: сходження вдвічі ───────────────────────────────────────
    parts.append(text(652, 62, 'подвоєння: сходження вдвічі', 15, FIELD, 'middle', bold=True))
    chain = [90, 45, 22, 11, 5, 2, 1, 0]
    cx = 652
    cyT, cdy = 100, 34
    bw, bh = 74, 24
    for i, v in enumerate(chain):
        cy = cyT + i * cdy
        parts.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
        parts.append(text(cx, cy + 4, str(v), 13, INK, 'middle', bold=True))
        if i < len(chain) - 1:
            parts.append(arrow(cx, cy + bh / 2, cx, cy + cdy - bh / 2, color="#7d8794", sw=1.6))
            parts.append(text(cx + bw / 2 + 22, cy + cdy / 2 + 5, '⌊n/2⌋', 11, MUTED, 'middle'))

    yb = cyT + (len(chain) - 1) * cdy
    parts.append(text(652, yb + 40, '7 кроків до F₉₀', 12.5, INK, 'middle', bold=True))
    parts.append(text(652, yb + 60, '≈ log₂n множень великих чисел', 11.5, MUTED, 'middle'))

    render(os.path.join(IMG, 'costs.svg'), W, H, *parts,
           title='Одна відповідь, дві ціни: дерево викликів проти драбини подвоєння')


# ── Фігура 6 (для вставки-Цекендорф): підпис 100 у фібоначчієвій системі ──────
# Смуга розрядів: кожна клітинка — число Фібоначчі (89, 55, …, 1); одиниці стоять
# там, де доданок увійшов у суму 100 = 89 + 8 + 3. Заповнені клітинки ніколи не
# сусідять — це і є визначальне правило запису Цекендорфа (заборона «11»).
def fig_zeckendorf():
    W, H = 820, 300
    cw, ch = 68, 62
    n = 10
    x0 = (W - n * cw) / 2.0
    RY = 96
    ks   = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    vals = [89, 55, 34, 21, 13, 8, 5, 3, 2, 1]
    bits = [1,  0,  0, 0, 0, 1, 0, 1, 0, 0]

    def CX(i):
        return x0 + i * cw

    parts = []
    # підписи рядів ліворуч (із запасом, щоб не налізали на клітинки)
    parts.append(text(x0 - 18, RY - 14, 'Fₖ:', 12, MUTED, 'end'))
    parts.append(text(x0 - 18, RY + ch / 2 + 8, 'біт:', 12, INK, 'end', bold=True))
    parts.append(text(x0 - 18, RY + ch + 22, 'k:', 12, MUTED, 'end'))

    for i in range(n):
        on = bits[i] == 1
        parts.append(rect(CX(i), RY, cw, ch,
                          fill=("#e7f7ee" if on else "#ffffff"),
                          stroke=(FIELD if on else LINE),
                          sw=(2.4 if on else 1.3), rx=6))
        parts.append(text(CX(i) + cw / 2, RY - 14, str(vals[i]), 12,
                          FIELD if on else MUTED, 'middle', bold=on))
        parts.append(text(CX(i) + cw / 2, RY + ch / 2 + 9, str(bits[i]), 26,
                          FIELD if on else "#c2c7cf", 'middle', bold=True))
        parts.append(text(CX(i) + cw / 2, RY + ch + 22, str(ks[i]), 12, MUTED, 'middle'))

    # рівняння й підпис-висновок під смугою
    parts.append(text(W / 2, RY + ch + 62, '100  =  89 + 8 + 3', 19, INK, 'middle', bold=True))
    parts.append(text(W / 2, RY + ch + 90,
                      'жодні дві заповнені клітинки не стоять поряд — у записі не буває «11»',
                      12.5, FIELD, 'middle', italic=True))

    render(os.path.join(IMG, 'zeckendorf.svg'), W, H, *parts,
           title='Підпис числа 100 у фібоначчієвій системі числення')


# ── Фігура 7 (для вставки-тотожностей): Кассіні як різниця площ ───────────────
# Прямокутник Fₙ₊₁×Fₙ₋₁ (13×5 = 65) має рівно на одну клітинку більше, ніж
# квадрат Fₙ×Fₙ (8×8 = 64): ця клітинка й є (−1)ⁿ у тотожності Кассіні при n=6,
# і вона ж — «зниклий квадрат» у славетній головоломці.
def fig_cassini_defect():
    W, H = 780, 384
    u = 25
    sx, sy = 64, 92                       # квадрат 8×8
    rx = 372                              # прямокутник 13×5
    ry = sy + (8 * u - 5 * u) // 2        # вирівняти по центру з квадратом
    parts = []

    # --- квадрат 8×8 = 64 ---
    for i in range(8):
        for j in range(8):
            parts.append(rect(sx + i * u, sy + j * u, u, u, fill="#eef1f4",
                              stroke="#c7ccd2", sw=0.8, rx=0))
    parts.append(rect(sx, sy, 8 * u, 8 * u, fill="none", stroke=NEG, sw=2.4, rx=0))
    parts.append(text(sx + 4 * u, sy - 16, 'F₆ · F₆ = 8 · 8', 14, INK, 'middle', bold=True))
    parts.append(text(sx + 4 * u, sy + 8 * u + 28, '64 клітинки', 13, NEG, 'middle', bold=True))

    # --- прямокутник 13×5 = 65 ---
    for i in range(13):
        for j in range(5):
            parts.append(rect(rx + i * u, ry + j * u, u, u, fill="#eef1f4",
                              stroke="#c7ccd2", sw=0.8, rx=0))
    # зайва (65-та) клітинка
    parts.append(rect(rx + 12 * u, ry + 4 * u, u, u, fill="#fde5c8", stroke=GOLD, sw=2.4, rx=0))
    parts.append(text(rx + 12 * u + u / 2, ry + 4 * u + u / 2 + 5, '+1', 13, POS, 'middle', bold=True))
    parts.append(rect(rx, ry, 13 * u, 5 * u, fill="none", stroke=POS, sw=2.4, rx=0))
    parts.append(text(rx + 6.5 * u, ry - 16, 'F₇ · F₅ = 13 · 5', 14, INK, 'middle', bold=True))
    parts.append(text(rx + 6.5 * u, ry + 5 * u + 28, '65 клітинок — на одну більше', 13, POS, 'middle', bold=True))

    # підсумкова рівність
    parts.append(text(W / 2, H - 22, 'Кассіні (n = 6):   F₇·F₅ − F₆²  =  65 − 64  =  +1  =  (−1)⁶',
                      14.5, INK, 'middle', bold=True))

    render(os.path.join(IMG, 'cassini-defect.svg'), W, H, *parts,
           title='Кассіні як різниця площ: 8×8 і 13×5 різняться на одну клітинку')


# ── Фігура 8 (для вставки-тотожностей): спуск НСД по номерах ↔ по числах ──────
# Алгоритм Евкліда на номерах (12,8)→(8,4)→(4,0) віддзеркалюється тим самим
# спуском у самих числах Фібоначчі й завершується на F₄ = 3 = F_gcd(12,8).
def fig_gcd_ladder():
    W, H = 760, 442
    bxL, wL = 118, 150                    # ліві боксики (номери)
    bxR, wR = 408, 256                    # праві боксики (числа Фібоначчі)
    cxL, cxR = bxL + wL / 2, bxR + wR / 2
    bh = 46
    tops = [92, 170, 248, 326]            # верхні краї чотирьох рядів

    left = ['gcd(12, 8)', 'gcd(8, 4)', 'gcd(4, 0)', '= 4']
    right = ['gcd(F₁₂, F₈) = gcd(144, 21)', 'gcd(F₈, F₄) = gcd(21, 3)',
             'gcd(F₄, F₀) = gcd(3, 0)', '= F₄ = 3']
    steps = ['12 = 1·8 + 4', '8 = 2·4 + 0']

    parts = []

    # заголовки колонок
    parts.append(text(cxL, 74, 'номери — крок Евкліда', 12.5, INK, 'middle', bold=True))
    parts.append(text(cxR, 74, 'числа Фібоначчі', 12.5, INK, 'middle', bold=True))

    def dashed_arrow(x1, y1, x2, y2, color, sw=1.4):
        return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                'stroke-width="%.1f" stroke-dasharray="6 4" marker-end="url(#arrow)"/>'
                % (x1, y1, x2, y2, color, sw))

    for i, top in enumerate(tops):
        cy = top + bh / 2
        answer = (i == len(tops) - 1)
        fillc = "#e7f7ee" if answer else "#f4f6f8"
        strokec = FIELD if answer else LINE
        col = FIELD if answer else INK
        parts.append(fitbox(bxL, top, wL, bh, left[i], size=15, fill=fillc,
                            stroke=strokec, sw=1.8 if answer else 1.4, color=col, bold=True))
        parts.append(fitbox(bxR, top, wR, bh, right[i], size=13, fill=fillc,
                            stroke=strokec, sw=1.8 if answer else 1.4, color=col, bold=answer))
        # дзеркальна стрілка «ті самі кроки»
        parts.append(dashed_arrow(bxL + wL, cy, bxR - 4, cy, MUTED))
        # вертикальні стрілки спуску між рядами
        if i < len(tops) - 1:
            parts.append(arrow(cxL, top + bh, cxL, tops[i + 1] - 2, color=INK, sw=1.8))
            parts.append(arrow(cxR, top + bh, cxR, tops[i + 1] - 2, color=INK, sw=1.8))
        if i < len(steps):
            parts.append(text(cxL + 12, (top + bh + tops[i + 1]) / 2 + 4, steps[i], 10.5, MUTED, 'start'))

    parts.append(text((bxL + wL + bxR) / 2, tops[0] - 6, 'ті самі кроки', 10.5, MUTED, 'middle', italic=True))

    parts.append(mtext(W / 2, 404,
                       ['Спуск у номерах і спуск у числах Фібоначчі йдуть у ногу й завершуються разом:',
                        'gcd(12, 8) = 4,   а   gcd(F₁₂, F₈) = F₄ = 3.'],
                       12.5, INK, 'middle'))

    render(os.path.join(IMG, 'gcd-ladder.svg'), W, H, *parts,
           title='НСД чисел Фібоначчі: спуск по номерах дзеркалить спуск по числах')


fig_ratio()
fig_squares()
fig_pisano()
fig_prosody()
fig_costs()
fig_zeckendorf()
fig_cassini_defect()
fig_gcd_ladder()
print('Done. SVG in', IMG)
