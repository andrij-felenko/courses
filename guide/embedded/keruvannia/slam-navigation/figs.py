# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «SLAM: одночасне картографування й локалізація».
Запуск:  python figs.py   → пише SVG у ./img/
Помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

import math

W, H = 760, 470


# ───────────────────── 1. Замкнене коло курки-яйця ───────────────────────────
def fig_chicken_egg():
    """Щоб скласти карту — треба знати, ДЕ ти; щоб знати, де ти, — треба карта.
    SLAM розриває коло, оцінюючи обидва водночас."""
    f = []
    f.append(text(W / 2, 32, "Карта й положення замкнені одне на одне", size=18, bold=True))

    # два бокси — «положення» і «карта», з'єднані циклом
    lx, rx, cy = 215, 545, 175
    bl, wl, hl = textbox(lx, cy, ["ПОЛОЖЕННЯ", "(де я зараз)"], size=15, bold=True,
                         fill="#eaf0fd", stroke=NEG, pad=14)
    br, wr, hr = textbox(rx, cy, ["КАРТА", "(де орієнтири)"], size=15, bold=True,
                         fill="#eafaf0", stroke=FIELD, pad=14)
    f.append(bl); f.append(br)

    # стрілка вгорі: карта → положення (маючи карту, локалізуюсь)
    f.append(arrow(rx - wr / 2 - 6, cy - 26, lx + wl / 2 + 6, cy - 26, color=INK, sw=2.2))
    f.append(text(W / 2, cy - 36, "маючи карту — знаю, де я", size=12.5, color=MUTED))
    # стрілка внизу: положення → карта (знаючи де я, наношу орієнтир)
    f.append(arrow(lx + wl / 2 + 6, cy + 26, rx - wr / 2 - 6, cy + 26, color=INK, sw=2.2))
    f.append(text(W / 2, cy + 40, "знаючи, де я — наношу орієнтир", size=12.5, color=MUTED))

    # знак безвиході по центру
    f.append(text(W / 2, cy + 2, "?", size=30, color=POS, bold=True))

    # знизу — розв'язка SLAM
    by = 300
    bs, ws, hs = textbox(W / 2, by, ["SLAM: оцінюй ОБИДВА водночас —", "одні дані правлять і карту, і положення"],
                         size=14, bold=True, fill="#fff8e1", stroke="#9a7d0a", pad=13)
    f.append(arrow(lx, cy + hl / 2 + 6, W / 2 - ws / 2 + 30, by - hs / 2 - 6, color=MUTED, sw=1.7))
    f.append(arrow(rx, cy + hr / 2 + 6, W / 2 + ws / 2 - 30, by - hs / 2 - 6, color=MUTED, sw=1.7))
    f.append(bs)

    f.append(fitbox(70, 372, W - 140, 80,
                    "Класична безвихідь: щоб скласти карту, треба точно знати своє положення;\n"
                    "щоб знати положення — треба вже мати карту з орієнтирами. Жодне не дано\n"
                    "першим. SLAM не розриває коло вибором «що раніше», а тримає обидві\n"
                    "невідомі в одній оцінці й уточнює їх спільно з кожним новим виміром.",
                    size=12, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "chicken-egg.svg"), W, H, *f)


# ───────────────────── 2. Замикання петлі виправляє дрейф ────────────────────
def fig_loop_closure():
    """Траєкторія дрейфує геть від істини; впізнавши вже бачений орієнтир,
    SLAM «стягує» весь контур назад — помилка розкидається по всьому шляху."""
    f = []
    f.append(text(W / 2, 30, "Замикання петлі: впізнав місце — виправив увесь шлях", size=17.5, bold=True))

    # справжній замкнений маршрут (коло) — зелений пунктир
    cx, cyr, R = 250, 250, 130
    truth = []
    N = 96
    for i in range(N + 1):
        a = -math.pi / 2 + 2 * math.pi * i / N
        truth.append((cx + R * math.cos(a), cyr + R * math.sin(a)))
    pts = " ".join("%.1f,%.1f" % p for p in truth)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" '
             'stroke-dasharray="5,4" opacity="0.8"/>' % (pts, FIELD))
    f.append(text(cx, cyr, "справжній", size=12, color=FIELD, bold=True))
    f.append(text(cx, cyr + 16, "маршрут", size=12, color=FIELD))

    # дрейфована оцінка одометрії: те саме коло, але радіус і кут поволі «повзуть»
    drift = []
    for i in range(N + 1):
        t = i / N
        a = -math.pi / 2 + 2 * math.pi * i / N + 0.55 * t          # кутовий дрейф
        rr = R * (1 + 0.16 * t)                                     # масштабний дрейф
        drift.append((cx + rr * math.cos(a), cyr + rr * math.sin(a)))
    dpts = " ".join("%.1f,%.1f" % p for p in drift)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (dpts, NEG))

    # старт (спільна точка) і кінець дрейфу (розійшовся)
    sx, sy = truth[0]
    ex, ey = drift[-1]
    f.append(circle(sx, sy, 6, fill=FIELD, stroke=BG, sw=2))
    f.append(text(sx, sy - 12, "старт", size=11, color=FIELD, bold=True))
    f.append(circle(ex, ey, 6, fill=NEG, stroke=BG, sw=2))
    f.append(text(ex + 8, ey + 4, "сюди завів", size=11, color=NEG, bold=True, anchor="start"))
    f.append(text(ex + 8, ey + 18, "голий рахунок", size=11, color=NEG, anchor="start"))

    # розрив замикання — червона дужка між справжнім стартом і дрейфованим кінцем
    f.append(line(sx, sy, ex, ey, color=POS, sw=1.6, dash="3,3"))
    mxp, myp = (sx + ex) / 2, (sy + ey) / 2
    f.append(text(mxp + 40, myp - 6, "те саме місце —", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(mxp + 40, myp + 8, "а оцінки розійшлись!", size=11, color=POS, anchor="start"))

    # права колонка — що дає впізнавання
    rx0 = 540
    b1, w1, h1 = textbox(rx0, 150, ["1. впізнав орієнтир,", "бачений на старті"], size=12.5,
                         bold=True, fill="#fdecea", stroke=POS, pad=11)
    b2, w2, h2 = textbox(rx0, 250, ["2. отже, старт і кінець —", "одна точка (зв'язок)"], size=12.5,
                         bold=True, fill="#fff8e1", stroke="#9a7d0a", pad=11)
    b3, w3, h3 = textbox(rx0, 350, ["3. помилку розкидай", "по всьому контуру"], size=12.5,
                         bold=True, fill="#eafaf0", stroke=FIELD, pad=11)
    f.append(b1); f.append(b2); f.append(b3)
    f.append(arrow(rx0, 150 + h1 / 2 + 3, rx0, 250 - h2 / 2 - 3, color=MUTED, sw=1.7))
    f.append(arrow(rx0, 250 + h2 / 2 + 3, rx0, 350 - h3 / 2 - 3, color=MUTED, sw=1.7))

    render(os.path.join(OUT, "loop-closure.svg"), W, H, *f)


# ───────────────────── 3. Карта корельована: спільна помилка пози ────────────
def fig_correlated_map():
    """Усі орієнтири нанесені З ТОЧКИ ЗОРУ робота, тож ділять спільну помилку
    його пози: точний вимір одного підтягує оцінку всіх інших."""
    f = []
    f.append(text(W / 2, 30, "Орієнтири корельовані: спільна помилка пози", size=18, bold=True))

    # робот
    rxp, ryp = 150, 300
    f.append(circle(rxp, ryp, 12, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(rxp, ryp + 4, "Я", size=13, color=NEG, bold=True))
    f.append(text(rxp, ryp + 28, "робот", size=11, color=MUTED))
    # хмара невизначеності самої пози
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="34" ry="22" fill="%s" opacity="0.16" '
             'stroke="%s" stroke-dasharray="3,3"/>' % (rxp, ryp, NEG, NEG))

    # три орієнтири, кожен зі своєю еліптичною хмарою — усі видовжені В ОДИН БІК
    # (бо ділять напрям помилки пози), і всі «дивляться» від робота
    lms = [(380, 130, 1), (520, 250, 2), (470, 400, 3)]
    for (lx, ly, idx) in lms:
        # промінь спостереження від робота до орієнтира
        f.append(line(rxp, ryp, lx, ly, color=MUTED, sw=1.2, dash="2,4"))
        # хмара орієнтира — нахилена вздовж напряму «робот→орієнтир» + спільний знос
        ang = math.degrees(math.atan2(ly - ryp, lx - rxp))
        f.append('<ellipse cx="%.1f" cy="%.1f" rx="40" ry="15" '
                 'transform="rotate(%.1f %.1f %.1f)" fill="%s" opacity="0.18" '
                 'stroke="%s" stroke-dasharray="3,3"/>'
                 % (lx, ly, ang, lx, ly, FIELD, FIELD))
        f.append(circle(lx, ly, 5, fill=FIELD, stroke=BG, sw=1.5))
        f.append(text(lx, ly - 22, "орієнтир %d" % idx, size=11, color=FIELD, bold=True))

    # стрілка: «точний вимір орієнтира 2» стискає не лише його
    tx, ty = 520, 250
    f.append(circle(tx, ty, 8, fill=POS, stroke=BG, sw=2))
    f.append(text(tx + 14, ty - 4, "цей виміряли точно", size=11.5, color=POS, bold=True, anchor="start"))
    f.append(text(tx + 14, ty + 12, "(GPS / прив'язка)", size=10.5, color=POS, anchor="start"))
    # пунктирні «стяжки» від точного до інших — спільна помилка зменшується в усіх
    for (lx, ly, idx) in lms:
        if (lx, ly) == (tx, ty):
            continue
        f.append(arrow((tx + lx) / 2 + (lx - tx) * 0.0, (ty + ly) / 2,
                       lx + (tx - lx) * 0.18, ly + (ty - ly) * 0.18,
                       color=POS, sw=1.4))
    # і пози робота теж
    f.append(arrow(tx - 30, ty + 10, rxp + 26, ryp - 8, color=POS, sw=1.4))

    f.append(fitbox(70, 392, W - 140, 64,
                    "Кожен орієнтир нанесено З ПОЛОЖЕННЯ робота — тож у всіх «зашита» одна\n"
                    "й та сама помилка його пози (зелені хмари знесені узгоджено, не врізнобій).\n"
                    "Виміряй один орієнтир точно — і ти оцінив спільну помилку: стискаються\n"
                    "хмари ВСІХ орієнтирів і самої пози. Це й робить карту єдиним цілим.",
                    size=11.5, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "correlated-map.svg"), W, H, *f)


# ───────────────────── 4. Розкладка спільного стану EKF-SLAM ─────────────────
def fig_ekf_state_layout():
    """Спільний вектор стану = поза (3) + пари координат орієнтирів; поряд —
    квадратна коваріація з блоками на діагоналі й кореляціями поза нею."""
    f = []
    f.append(text(W / 2, 30, "Спільний стан EKF-SLAM: один вектор, одна коваріація",
                  size=17.5, bold=True))

    # ── ліворуч: вектор стану як стовпчик клітинок ──────────────────────────
    cells = [("x", NEG), ("y", NEG), ("θ", NEG),
             ("mx¹", FIELD), ("my¹", FIELD), ("mx²", FIELD), ("my²", FIELD),
             ("mx³", FIELD), ("my³", FIELD)]
    cw, ch = 56, 30
    vx, vy = 70, 95
    f.append(text(vx + cw / 2, vy - 12, "вектор стану", size=12.5, bold=True, color=MUTED))
    for i, (lab, col) in enumerate(cells):
        y = vy + i * ch
        fill = "#eaf0fd" if col == NEG else "#eafaf0"
        f.append(rect(vx, y, cw, ch, fill=fill, stroke=col, sw=1.6, rx=4))
        f.append(text(vx + cw / 2, y + ch / 2 + 4, lab, size=12.5, color=col, bold=True))
    # дужки-підписи: поза / орієнтири
    f.append(line(vx - 8, vy, vx - 8, vy + 3 * ch, color=NEG, sw=2))
    f.append(text(vx - 14, vy + 1.5 * ch + 4, "поза", size=11.5, color=NEG,
                  bold=True, anchor="end"))
    f.append(line(vx - 8, vy + 3 * ch, vx - 8, vy + 9 * ch, color=FIELD, sw=2))
    f.append(text(vx - 14, vy + 6 * ch + 4, "орієн-", size=11.5, color=FIELD,
                  bold=True, anchor="end"))
    f.append(text(vx - 14, vy + 6 * ch + 18, "тири", size=11.5, color=FIELD,
                  bold=True, anchor="end"))

    # ── праворуч: матриця коваріації (3+2N)×(3+2N) ──────────────────────────
    n = len(cells)
    mx0, my0 = 300, 95
    gs = 30                                   # розмір клітинки матриці
    side = n * gs
    f.append(text(mx0 + side / 2, my0 - 12, "коваріація  P  (dim × dim)",
                  size=12.5, bold=True, color=MUTED))
    # рамка
    f.append(rect(mx0, my0, side, side, fill=BG, stroke=INK, sw=1.5, rx=3))
    for i in range(n):
        for j in range(n):
            x = mx0 + j * gs
            y = my0 + i * gs
            pose_i = i < 3
            pose_j = j < 3
            if i == j:
                # діагональні блоки невпевненості
                fill = "#dbe6fb" if pose_i else "#d8f2e2"
            elif pose_i and pose_j:
                fill = "#eef4fe"               # блок пози
            elif (not pose_i) and (not pose_j):
                # блок орієнтир-орієнтир: кореляція між РІЗНИМИ орієнтирами
                same = (i - 3) // 2 == (j - 3) // 2
                fill = "#cdeeda" if same else "#e7f7ee"
            else:
                fill = "#eafaf0"               # кроскореляція поза↔орієнтир
            f.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="%s" '
                     'stroke="#ffffff" stroke-width="0.8"/>' % (x, y, gs, gs, fill))
    # розділові лінії блоку пози
    f.append(line(mx0 + 3 * gs, my0, mx0 + 3 * gs, my0 + side, color=INK, sw=1.4))
    f.append(line(mx0, my0 + 3 * gs, mx0 + side, my0 + 3 * gs, color=INK, sw=1.4))
    # підписи блоків усередині матриці
    f.append(text(mx0 + 1.5 * gs, my0 + 1.5 * gs + 4, "поза", size=10.5,
                  color=NEG, bold=True))
    f.append(text(mx0 + 1.5 * gs, my0 + 6 * gs + 4, "коре-", size=10, color=FIELD, bold=True))
    f.append(text(mx0 + 1.5 * gs, my0 + 6 * gs + 17, "ляції", size=10, color=FIELD, bold=True))
    f.append(text(mx0 + 6 * gs, my0 + 1.5 * gs + 4, "кореляції", size=10,
                  color=FIELD, bold=True))

    # стрілка-зв'язок: рядок пози ↔ стовпці орієнтирів
    f.append(text(mx0 + side + 12, my0 + 1.5 * gs - 4, "← рядок пози несе", size=10.5,
                  color=FIELD, anchor="start"))
    f.append(text(mx0 + side + 12, my0 + 1.5 * gs + 11, "зв'язок з усіма", size=10.5,
                  color=FIELD, anchor="start"))
    f.append(text(mx0 + side + 12, my0 + 1.5 * gs + 26, "орієнтирами", size=10.5,
                  color=FIELD, anchor="start"))

    f.append(fitbox(70, 388, W - 140, 64,
                    "Один вектор: поза робота (3 числа, сині) і далі ПАРИ координат орієнтирів\n"
                    "(зелені). Поряд — квадратна коваріація того ж розміру: діагональні блоки —\n"
                    "невпевненість кожного, а позадіагональні (зелені) — КОРЕЛЯЦІЇ, через які\n"
                    "виправлення одного орієнтира торкається пози й усіх інших. Це й росте як dim².",
                    size=11.5, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "ekf-state-layout.svg"), W, H, *f)


# ──────────── 5. Розрідженість матриці системи (графовий SLAM) ───────────────
def fig_sparse_hessian():
    """Матриця системи H у блоках поз: одометрія дає щільну діагональну стрічку
    (сусід↔сусід), нечасті замикання петель — поодинокі блоки далеко від
    діагоналі. Решта — рівно нулі: саме це й робить великий SLAM швидким."""
    f = []
    f.append(text(W / 2, 30, "Матриця системи H: майже сама порожнеча", size=18, bold=True))

    # сітка n×n клітинок (клітинка = блок пари поз)
    n = 12
    gx, gy = 86, 78          # лівий-верхній кут сітки
    cell = 26
    G = n * cell

    # підписи осей
    f.append(text(gx + G / 2, gy - 12, "пози 1 … n  (стовпці)", size=12, color=MUTED))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">пози 1 … n  (рядки)</text>'
             % (gx - 22, gy + G / 2, FONT, MUTED, gx - 22, gy + G / 2))

    # ненульові клітинки
    diag = set((i, i) for i in range(n))                       # поза з собою
    odom = set()                                               # сусід ↔ сусід
    for i in range(n - 1):
        odom.add((i, i + 1)); odom.add((i + 1, i))
    loops = {(0, 9), (9, 0), (2, 11), (11, 2)}                 # замикання петель

    for r in range(n):
        for c in range(n):
            x = gx + c * cell
            y = gy + r * cell
            if (r, c) in diag:
                f.append(rect(x, y, cell, cell, fill="#d3def9", stroke=NEG, sw=1.1, rx=2))
            elif (r, c) in odom:
                f.append(rect(x, y, cell, cell, fill="#e6eefe", stroke=NEG, sw=0.8, rx=2))
            elif (r, c) in loops:
                f.append(rect(x, y, cell, cell, fill="#fdded9", stroke=POS, sw=1.5, rx=2))
            else:
                f.append(rect(x, y, cell, cell, fill=BG, stroke="#e5e7eb", sw=0.5, rx=0))

    # «0» у кількох порожніх клітинках — щоб одразу читалось «нулі»
    for (r, c) in [(1, 7), (7, 1), (4, 10), (10, 4), (0, 5), (5, 0)]:
        f.append(text(gx + c * cell + cell / 2, gy + r * cell + cell / 2 + 4,
                      "0", size=11, color="#c2c7cf"))

    # винесені підписи зі стрілками
    lx = gx + G + 22
    f.append(text(lx, gy + 30, "одометрія —", size=12.5, color=NEG, bold=True, anchor="start"))
    f.append(text(lx, gy + 46, "щільна стрічка", size=12, color=NEG, anchor="start"))
    f.append(text(lx, gy + 61, "(сусід ↔ сусід)", size=11, color=MUTED, anchor="start"))
    f.append(arrow(lx - 4, gy + 40, gx + 6 * cell + cell * 0.5, gy + 6 * cell - cell * 0.1,
                   color=NEG, sw=1.4))

    f.append(text(lx, gy + 116, "замикання петлі —", size=12.5, color=POS, bold=True, anchor="start"))
    f.append(text(lx, gy + 132, "поодинокі блоки", size=12, color=POS, anchor="start"))
    f.append(text(lx, gy + 147, "далеко від діагоналі", size=11, color=MUTED, anchor="start"))
    f.append(arrow(lx - 4, gy + 124, gx + 9 * cell + cell * 0.5, gy + cell * 0.6,
                   color=POS, sw=1.4))

    f.append(text(lx, gy + 200, "решта — нулі:", size=12.5, color=MUTED, bold=True, anchor="start"))
    f.append(text(lx, gy + 216, "не зберігаємо", size=12, color=MUTED, anchor="start"))
    f.append(text(lx, gy + 231, "й не множимо", size=12, color=MUTED, anchor="start"))

    by = gy + G + 22
    f.append(fitbox(70, by, W - 140, 74,
                    "Кожне ребро (i,j) заповнює лише блоки своїх двох поз. Одометрія в'яже\n"
                    "сусідів — звідси щільна діагональна стрічка; нечасті замикання петель\n"
                    "дають поодинокі блоки осторонь. Переважна більшість пар поз нічим не\n"
                    "зв'язані — ці клітинки рівно нуль. Розв'язувач працює лише з ненульовими\n"
                    "блоками, минаючи нулі: кубічна ціна щільної системи стає майже лінійною.",
                    size=11.5, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "sparse-hessian.svg"), W, by + 74 + 20, *f)


if __name__ == "__main__":
    fig_chicken_egg()
    fig_loop_closure()
    fig_correlated_map()
    fig_ekf_state_layout()
    fig_sparse_hessian()
    print("OK: 5 figures ->", OUT)
