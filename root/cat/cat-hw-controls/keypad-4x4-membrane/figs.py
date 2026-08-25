# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Матрична клавіатура 4×4 (мембранна)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

KEYS = [["1", "2", "3", "A"],
        ["4", "5", "6", "B"],
        ["7", "8", "9", "C"],
        ["*", "0", "#", "D"]]


# ── 1. Матриця 4×4: 16 клавіш на 8 дротах ─────────────────────────────────────
def fig_matrix():
    W, H = 760, 640
    f = [text(W / 2, 34, "16 клавіш живуть на 8 дротах: 4 рядки × 4 стовпці",
              size=16, bold=True)]

    # координати ліній сітки
    x0, dx = 200, 120          # x перших стовпців і крок
    y0, dy = 130, 110          # y перших рядків і крок
    xs = [x0 + i * dx for i in range(4)]   # стовпці C1..C4
    ys = [y0 + i * dy for i in range(4)]   # рядки R1..R4
    x_left = 120               # де зліва починаються шини рядків
    x_right = xs[-1] + 60
    y_top = 90
    y_bot = ys[-1] + 60

    # рядкові шини (горизонталь) — сині
    for j, y in enumerate(ys):
        f.append(line(x_left, y, x_right, y, color=NEG, sw=2.4))
        f.append(text(x_left - 12, y + 5, "R%d" % (j + 1), size=14, bold=True,
                      color=NEG, anchor="end"))
    # стовпцеві шини (вертикаль) — червоні
    for i, x in enumerate(xs):
        f.append(line(x, y_top, x, y_bot, color=POS, sw=2.4))
        f.append(text(x, y_top - 12, "C%d" % (i + 1), size=14, bold=True, color=POS))

    # у кожному перехресті — клавіша (кружечок = кнопка, що замикає R на C)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            f.append(circle(x, y, 15, fill=BG, stroke=INK, sw=1.8))
            f.append(text(x, y + 5, KEYS[j][i], size=13, bold=True))

    # виноска: натиснута клавіша «5» замикає R2 з C2 (кільце-обвід поверх готового «5»)
    hx, hy = xs[1], ys[1]
    f.append(circle(hx, hy, 19, fill="none", stroke=POS, sw=2.6))
    f.append(text(hx + 155, hy - 40, "натиснули «5»:", size=12.5, bold=True,
                  color=POS, anchor="start"))
    f.append(text(hx + 155, hy - 22, "клавіша замикає", size=12, color=INK, anchor="start"))
    f.append(text(hx + 155, hy - 4, "R2 з C2 у цій точці", size=12, color=INK, anchor="start"))

    # 8 дротів до контролера — унизу підпис
    f.append(line(90, y_bot + 40, W - 60, y_bot + 40, color="#e5e7eb", sw=1))
    f.append(text(W / 2, y_bot + 66,
                  "4 рядки + 4 стовпці = 8 виводів гребінки (замість 16 окремих кнопок)",
                  size=12.5, bold=True))
    return W, H, f


# ── 2. Сканування: жену стовпець у 0, читаю рядки з підтяжкою ──────────────────
def fig_scan():
    W, H = 960, 600
    f = [text(W / 2, 34, "Опитування: жену один стовпець у «0», читаю чотири рядки",
              size=16, bold=True)]

    # сітку зсунуто праворуч — ліворуч лишаємо гутер під виноску-панель
    x0, dx = 430, 120
    y0, dy = 150, 90
    xs = [x0 + i * dx for i in range(4)]
    ys = [y0 + i * dy for i in range(4)]
    x_left = 380
    x_right = xs[-1] + 50
    y_top = 110
    y_bot = ys[-1] + 50

    active_col = 1             # C2 зараз ведений у 0
    pressed = (1, 1)          # натиснута «5» = (рядок 1, стовпець 1)

    # рядки — входи з підтяжкою: за замовчуванням «1»; читаний рівень — коротким «→1»/«→0» праворуч
    for j, y in enumerate(ys):
        col = POS if (j == pressed[0]) else NEG
        f.append(line(x_left, y, x_right, y, color=NEG, sw=2.2))
        f.append(text(x_left - 14, y + 5, "R%d" % (j + 1), size=13, bold=True,
                      color=NEG, anchor="end"))
        lvl = "0" if (j == pressed[0]) else "1"
        f.append(text(x_right + 16, y + 5, "→ %s" % lvl, size=13, bold=True,
                      color=col, anchor="start"))

    # стовпці: активний ведений у 0 (жирний), решта — Z (відпущені у вхід)
    for i, x in enumerate(xs):
        if i == active_col:
            f.append(line(x, y_top, x, y_bot, color=POS, sw=3.2))
            f.append(text(x, y_top - 28, "C%d" % (i + 1), size=13, bold=True, color=POS))
            f.append(text(x, y_top - 11, "жену 0", size=11, bold=True, color=POS))
        else:
            f.append(line(x, y_top, x, y_bot, color="#c9ced6", sw=1.6, dash="5 5"))
            f.append(text(x, y_top - 28, "C%d" % (i + 1), size=13, bold=True, color=MUTED))
            f.append(text(x, y_top - 11, "Z (вхід)", size=10.5, color=MUTED))

    # клавіші
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            hot = (j, i) == pressed
            f.append(circle(x, y, 13, fill=("#fdecea" if hot else BG),
                            stroke=(POS if hot else INK), sw=(2.4 if hot else 1.6)))
            f.append(text(x, y + 4, KEYS[j][i], size=12, bold=True,
                          color=(POS if hot else INK)))

    # обвід натиснутої «5»
    px, py = xs[pressed[1]], ys[pressed[0]]
    f.append(circle(px, py, 18, fill="none", stroke=POS, sw=2.4))

    # виноска-панель у лівому гутері (нічого поруч не стоїть)
    pnx, pny, pnw, pnh = 40, 180, 300, 150
    f.append(rect(pnx, pny, pnw, pnh, fill="#fdf0ee", stroke=POS, sw=1.6, rx=10))
    f.append(text(pnx + 18, pny + 32, "натиснули «5»", size=13.5, bold=True,
                  color=POS, anchor="start"))
    for k, ln in enumerate(["замкнула ведений C2 з R1;",
                            "«0» стікає з C2 у R1,",
                            "тож саме R1 читається «0».",
                            "решта рядків лишаються «1»."]):
        f.append(text(pnx + 18, pny + 58 + k * 22, ln, size=11.5, color=INK, anchor="start"))

    # підсумок унизу
    f.append(line(60, y_bot + 45, W - 50, y_bot + 45, color="#e5e7eb", sw=1))
    f.append(text(W / 2, y_bot + 70,
                  "Рядки з підтяжкою у спокої «1». Ведений стовпець + натиснута клавіша тягнуть свій рядок у «0».",
                  size=12, color=MUTED))
    f.append(text(W / 2, y_bot + 90,
                  "Стовпець із «0» + рядок з «0» = координата клавіші. Повтори для C1..C4 — і знаєш усі 16.",
                  size=12, bold=True))
    return W, H, f


# ── 3. Підключення гребінки до мікроконтролера (8 дротів) ─────────────────────
def fig_wiring():
    W, H = 940, 560
    f = [text(W / 2, 32, "Підключення: 8 виводів гребінки → 8 звичайних GPIO",
              size=16, bold=True)]

    # клавіатура ліворуч
    bx, by, bw, bh = 90, 90, 250, 400
    f.append(rect(bx, by, bw, bh, fill=BG, stroke=INK, sw=2.2, rx=14))
    f.append(text(bx + bw / 2, by + 34, "мембранна", size=15, bold=True))
    f.append(text(bx + bw / 2, by + 54, "клавіатура 4×4", size=13, color=MUTED))
    # намічена сітка 4×4 на панелі
    gx0, gy0, gs = bx + 55, by + 90, 46
    for r in range(4):
        for c in range(4):
            cxk = gx0 + c * gs
            cyk = gy0 + r * gs
            f.append(rect(cxk - 17, cyk - 17, 34, 34, fill="#f0f4fb", stroke=MUTED, sw=1, rx=6))
            f.append(text(cxk, cyk + 5, KEYS[r][c], size=12, bold=True, color=INK))

    # 8 виводів гребінки — праворуч від клавіатури, зверху вниз (нижче титрів блоків)
    order = [("R1", NEG), ("R2", NEG), ("R3", NEG), ("R4", NEG),
             ("C1", POS), ("C2", POS), ("C3", POS), ("C4", POS)]
    py0, pstep = by + 92, 40
    for k, (lab, col) in enumerate(order):
        y = py0 + k * pstep
        f.append(circle(bx + bw, y, 4.5, fill=col, stroke=col))
        f.append(text(bx + bw - 12, y + 4, lab, size=12, bold=True, color=col, anchor="end"))

    # мікроконтролер праворуч
    mx, my, mw, mh = 660, 90, 230, 400
    f.append(rect(mx, my, mw, mh, fill="#eef3fb", stroke=INK, sw=2.2, rx=14))
    f.append(text(mx + mw / 2, my + 34, "мікроконтролер", size=14, bold=True))
    f.append(text(mx + mw / 2, my + 54, "8 GPIO", size=12, color=MUTED))
    for k, (lab, col) in enumerate(order):
        y = py0 + k * pstep
        role = "OUTPUT" if lab.startswith("C") else "INPUT_PULLUP"
        f.append(circle(mx, y, 4.5, fill=col, stroke=col))
        f.append(text(mx + 12, y + 4, "%s → %s" % (lab, role), size=11, color=col, anchor="start"))
        # дріт від гребінки до GPIO (пряма горизонталь на одній висоті)
        f.append(line(bx + bw, y, mx, y, color=col, sw=1.6))

    f.append(text(W / 2, my + mh + 34,
                  "Порядок штирків на шлейфі гуляє між партіями — звіряй підписи або продзвони мультиметром.",
                  size=12, color=MUTED))
    return W, H, f


# ── 4. Привид (ghosting) і як його знімає діод ────────────────────────────────
def fig_ghost():
    W, H = 940, 470
    f = [text(W / 2, 32, "Привид: три клавіші розом малюють четверту, якої не торкались",
              size=15.5, bold=True)]

    def draw_grid(ox, oy, title, phantom, with_diode, subtitle):
        # мала матриця 2×2 (досить, щоб показати квадрат-привид)
        dx, dy = 120, 110
        xs = [ox, ox + dx]
        ys = [oy, oy + dy]
        y_top, y_bot = oy - 42, ys[-1] + 42
        x_left, x_right = ox - 60, xs[-1] + 42
        f.append(text(ox + dx / 2 - 30, oy - 78, title, size=13.5, bold=True))
        f.append(text(ox + dx / 2 - 30, oy - 60, subtitle, size=11, color=MUTED))
        # рядки/стовпці
        rlab = ["R1", "R2"]
        clab = ["C1", "C2"]
        gap = 22  # розрив вертикалі довкола вузла, щоб лінія не різала гліф клавіші
        for j, y in enumerate(ys):
            f.append(line(x_left, y, x_right, y, color=NEG, sw=2))
            f.append(text(x_left - 10, y + 5, rlab[j], size=12, bold=True, color=NEG, anchor="end"))
        for i, x in enumerate(xs):
            # вертикаль сегментами: згори до першого вузла, у проміжку між вузлами, після другого — донизу
            bounds = [y_top] + sum([[yy - gap, yy + gap] for yy in ys], []) + [y_bot]
            for a, b in zip(bounds[0::2], bounds[1::2]):
                if b > a:
                    f.append(line(x, a, x, b, color=POS, sw=2))
            f.append(text(x, y_top - 8, clab[i], size=12, bold=True, color=POS))
        # три реально натиснуті: (0,0),(0,1),(1,0); привид у (1,1)
        real = {(0, 0), (0, 1), (1, 0)}
        for j, y in enumerate(ys):
            for i, x in enumerate(xs):
                if (j, i) in real:
                    f.append(circle(x, y, 14, fill="#fdecea", stroke=POS, sw=2.4))
                    f.append(text(x, y + 4, "✓", size=13, bold=True, color=POS))
                elif (j, i) == (1, 1):
                    if phantom:
                        f.append(circle(x, y, 14, fill="#fff6d6", stroke="#b8860b", sw=2.4))
                        f.append(text(x, y + 4, "?", size=14, bold=True, color="#b8860b"))
                    else:
                        f.append(circle(x, y, 14, fill=BG, stroke=MUTED, sw=1.6))
                        f.append(text(x, y + 4, "–", size=13, bold=True, color=MUTED))
                    # діод у послідовність із клавішею (символ ▷|)
                    if with_diode:
                        f.append(text(x + 26, y + 5, "▷|", size=13, bold=True, color=FIELD))
                else:
                    f.append(circle(x, y, 14, fill=BG, stroke=INK, sw=1.6))

    # ліворуч: без діодів — з'являється привид
    draw_grid(160, 150, "Без діодів", phantom=True, with_diode=False,
              subtitle="струм обходить збоку")
    f.append(text(160 + 30, 150 + 110 + 78, "контролер «бачить» 4-ту клавішу —",
                  size=11.5, color="#b8860b", bold=True, anchor="middle"))
    f.append(text(160 + 30, 150 + 110 + 96, "хибне натискання (привид)",
                  size=11.5, color="#b8860b", bold=True, anchor="middle"))

    # роздільник
    f.append(line(W / 2, 90, W / 2, 400, color="#e5e7eb", sw=1))

    # праворуч: із діодами — привид зникає
    draw_grid(600, 150, "Діод у кожній клавіші", phantom=False, with_diode=True,
              subtitle="струм лише в один бік")
    f.append(text(600 + 30, 150 + 110 + 78, "обхідний шлях перекрито —",
                  size=11.5, color=FIELD, bold=True, anchor="middle"))
    f.append(text(600 + 30, 150 + 110 + 96, "привида нема (N-key rollover)",
                  size=11.5, color=FIELD, bold=True, anchor="middle"))

    f.append(text(W / 2, 452,
                  "Мембранна 4×4 діодів НЕ має. Тому одночасно тисни не більш як одну клавішу — так привид не виникає.",
                  size=12, bold=True))
    return W, H, f


# ── 5. Опитування vs переривання: дві осі часу процесора ──────────────────────
def fig_poll_vs_int():
    W, H = 940, 470
    f = [text(W / 2, 32, "Той самий натиск: опитування будить процесор без кінця — переривання лише раз",
              size=14.5, bold=True)]

    x0, x1 = 130, W - 60          # ліва/права межі осей часу
    span = x1 - x0
    # позначка «натиснули» — спільна для обох осей
    press_t = 0.62                # частка вздовж осі, де стався натиск
    px = x0 + span * press_t

    def axis(y, title, sub):
        f.append(text(70, y - 34, title, size=13.5, bold=True, anchor="start"))
        f.append(text(70, y - 17, sub, size=11, color=MUTED, anchor="start"))
        f.append(line(x0, y, x1, y, color=INK, sw=1.6))      # лінія «сон/спокій»
        f.append(text(x1 + 8, y + 4, "час →", size=11, color=MUTED, anchor="start"))
        # мітка натиску — коротка вертикаль лише в межах стрічки, напис ставимо ПРАВІШЕ
        f.append(line(px, y - 30, px, y + 30, color=FIELD, sw=1.4, dash="4 4"))
        f.append(text(px + 10, y + 46, "натиснули тут", size=11, bold=True,
                      color=FIELD, anchor="start"))

    # верхня вісь: ОПИТУВАННЯ — рівномірні сплески-пробудження щокілька мс
    yA = 135
    axis(yA, "Опитування (polling)", "прокидається кожні ~10 мс, тисни чи ні")
    for k in range(14):
        sx = x0 + 18 + k * (span - 30) / 13.0
        # кожен сплеск — коротке пробудження (стовпчик угору)
        f.append(rect(sx - 4, yA - 26, 8, 26, fill="#eef3fb", stroke=NEG, sw=1.4, rx=2))
    f.append(text(x1, yA - 44, "14 пробуджень — і лише одне корисне",
                  size=11, color=NEG, anchor="end", italic=True))

    # нижня вісь: ПЕРЕРИВАННЯ — рівна лінія сну, один високий сплеск у момент натиску
    yB = 330
    axis(yB, "Переривання (wake-on-press)", "спить, поки клавіша не притисне рядок у «0»")
    # «zzz» над лінією сну (у порожньому проміжку: правіше за підзаголовок, лівіше за мітку px)
    zmid = (355 + px) / 2.0               # десь між кінцем підзаголовка (~350) і міткою натиску (px)
    for k, sx in enumerate([zmid - 70, zmid, zmid + 70]):
        f.append(text(sx, yB - 12, "z", size=13 + k, color=MUTED, italic=True))
    # єдиний сплеск-пробудження у px (вищий — це реальна робота: скан+обробка)
    f.append(rect(px - 6, yB - 26, 12, 26, fill="#fdecea", stroke=POS, sw=2, rx=2))
    f.append(text(x1, yB - 44, "1 пробудження на 1 натиск",
                  size=11, color=POS, anchor="end", italic=True))

    f.append(text(W / 2, H - 22,
                  "Робота однакова — зчитати клавішу. Різниця в тому, скільки разів між натисками процесор дарма прокидався.",
                  size=12, color=MUTED))
    return W, H, f


# ── 6. Арм-стан для пробудження: усі стовпці ведені у «0», рядки чекають ───────
def fig_wake():
    W, H = 960, 600
    f = [text(W / 2, 30, "Стан «чекаю на натиск»: усі стовпці разом у «0», кожен рядок з підтяжкою — і на вартовому перериванні",
              size=13.5, bold=True)]

    x0, dx = 380, 130
    y0, dy = 150, 92
    xs = [x0 + i * dx for i in range(4)]
    ys = [y0 + i * dy for i in range(4)]
    x_left = 330
    x_right = xs[-1] + 55
    y_top = 108
    y_bot = ys[-1] + 55

    pressed = (2, 1)             # натиснута «8» = (рядок 2, стовпець 1) — будь-яка згодиться

    # усі стовпці ведені у «0» (усі однаково жирні-червоні) — не по одному, а РАЗОМ
    for i, x in enumerate(xs):
        f.append(line(x, y_top, x, y_bot, color=POS, sw=3))
        f.append(text(x, y_top - 26, "C%d" % (i + 1), size=12.5, bold=True, color=POS))
        f.append(text(x, y_top - 10, "OUTPUT 0", size=10, bold=True, color=POS))

    # рядки — входи з підтяжкою + позначка «вартове переривання» (PCINT) зліва
    for j, y in enumerate(ys):
        fell = (j == pressed[0])
        f.append(line(x_left, y, x_right, y, color=NEG, sw=2.2))
        f.append(text(x_left - 12, y + 5, "R%d" % (j + 1), size=12.5, bold=True,
                      color=NEG, anchor="end"))
        lvl = "0" if fell else "1"
        lcol = POS if fell else NEG
        f.append(text(x_right + 14, y + 5, "→ %s" % lvl, size=12.5, bold=True,
                      color=lcol, anchor="start"))

    # клавіші
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            hot = (j, i) == pressed
            f.append(circle(x, y, 13, fill=("#fdecea" if hot else BG),
                            stroke=(POS if hot else INK), sw=(2.4 if hot else 1.6)))
            f.append(text(x, y + 4, KEYS[j][i], size=12, bold=True,
                          color=(POS if hot else INK)))
    px, py = xs[pressed[1]], ys[pressed[0]]
    f.append(circle(px, py, 18, fill="none", stroke=POS, sw=2.4))

    # ліва панель-виноска: механізм пробудження
    pnx, pny, pnw, pnh = 30, 150, 280, 190
    f.append(rect(pnx, pny, pnw, pnh, fill="#fdf0ee", stroke=POS, sw=1.6, rx=10))
    f.append(text(pnx + 16, pny + 30, "будь-який натиск", size=13, bold=True,
                  color=POS, anchor="start"))
    for k, ln in enumerate(["з'єднує свій рядок з веденим",
                            "«0» стовпця → рядок падає в «0».",
                            "",
                            "Перепад на рядку ловить",
                            "вартове переривання (PCINT)",
                            "і будить процесор зі сну."]):
        if ln:
            f.append(text(pnx + 16, pny + 56 + k * 22, ln, size=11.5, color=INK, anchor="start"))

    # ліва нижня панель (під першою, у вільному гутері): різниця зі скануванням
    dnx, dny, dnw, dnh = 30, pny + pnh + 22, 280, 96
    f.append(rect(dnx, dny, dnw, dnh, fill="#eef3fb", stroke=NEG, sw=1.4, rx=10))
    f.append(text(dnx + 16, dny + 26, "Під час сканування — навпаки:", size=11.5, bold=True,
                  color=NEG, anchor="start"))
    f.append(text(dnx + 16, dny + 48, "стовпці ведуться по одному.", size=11.5, color=INK, anchor="start"))
    f.append(text(dnx + 16, dny + 70, "Тут же — усі разом, щоб зловити", size=11, color=MUTED, anchor="start"))
    f.append(text(dnx + 16, dny + 86, "будь-яку клавішу.", size=11, color=MUTED, anchor="start"))

    f.append(text(W / 2, H - 24,
                  "Прокинувшись, процесор перемикається у звичайне сканування — щоб дізнатися, ЯКА саме клавіша впала.",
                  size=12, bold=True))
    return W, H, f


for name, fn in [("matrix", fig_matrix),
                 ("scan", fig_scan),
                 ("wiring", fig_wiring),
                 ("ghost", fig_ghost),
                 ("poll-vs-int", fig_poll_vs_int),
                 ("wake", fig_wake)]:
    W, H, frags = fn()
    render(os.path.join(IMG, name + ".svg"), W, H, *frags)
    print("wrote", name + ".svg")
