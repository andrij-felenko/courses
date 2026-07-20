# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── допоміжна пунктирна стрілка (для «прихованого» звʼязку) ──────────────────
def darrow(x1, y1, x2, y2, color=POS, sw=2.0):
    ang = math.atan2(y2 - y1, x2 - x1)
    hl = 12.0
    lx2 = x2 - hl * 0.75 * math.cos(ang)
    ly2 = y2 - hl * 0.75 * math.sin(ang)
    seg = line(x1, y1, lx2, ly2, color=color, sw=sw, dash="7 5")
    lx = x2 - hl * math.cos(ang) + hl * 0.5 * math.sin(ang)
    ly = y2 - hl * math.sin(ang) - hl * 0.5 * math.cos(ang)
    rx = x2 - hl * math.cos(ang) - hl * 0.5 * math.sin(ang)
    ry = y2 - hl * math.sin(ang) + hl * 0.5 * math.cos(ang)
    tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
           % (x2, y2, lx, ly, rx, ry, color))
    return seg + tri


# ── Фігура 1: приховане зчеплення через глобальний стан ──────────────────────
# Дві функції з чистими сигнатурами, які насправді таємно звʼязані спільним
# мутабельним глобалом. Жодна сигнатура про цей звʼязок не каже.
def fig_hidden_wire():
    W, H = 760, 430
    f = []

    # дві функції з «чесними» сигнатурами
    ax, ay, aw, ah = 60, 66, 280, 100
    f.append(rect(ax, ay, aw, ah, fill="#eef2ff", stroke=NEG, sw=2))
    f.append(text(ax + aw / 2, ay + 38, "checkout(order)", size=16, color=INK, bold=True))
    f.append(text(ax + aw / 2, ay + 66, "сигнатура обіцяє: лише order", size=13, color=MUTED))

    bx, by, bw, bh = 420, 66, 280, 100
    f.append(rect(bx, by, bw, bh, fill="#eef2ff", stroke=NEG, sw=2))
    f.append(text(bx + bw / 2, by + 38, "renderCart(cart)", size=16, color=INK, bold=True))
    f.append(text(bx + bw / 2, by + 66, "сигнатура обіцяє: лише cart", size=13, color=MUTED))

    # глобальний мутабельний стан унизу по центру
    gx, gy, gw, gh = 270, 302, 220, 86
    f.append(rect(gx, gy, gw, gh, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(text(gx + gw / 2, gy + 34, "session (глобальний)", size=15, color=INK, bold=True))
    f.append(text(gx + gw / 2, gy + 60, "мутабельний · видимий усім", size=12, color=POS))

    # приховані пунктирні звʼязки в глобал
    f.append(darrow(ax + 130, ay + ah, gx + 24, gy, POS))
    f.append(darrow(bx + 150, by + ah, gx + gw - 24, gy, POS))
    f.append(text(196, 250, "checkout пише", size=13, color=POS, anchor="middle"))
    f.append(text(566, 250, "renderCart читає", size=13, color=POS, anchor="middle"))

    # головна думка
    f.append(text(W / 2, 214, "жодна сигнатура про цей звʼязок не каже",
                  size=14, color=POS, bold=True))

    render(os.path.join(IMG, "hidden-wire.svg"), W, H, *f)


# ── Фігура 2: де саме криється небезпека — спільне × мутабельне ──────────────
# Квадрант «локальне↔спільне» на «незмінне↔мутабельне». Червона лише одна
# клітина: спільний І мутабельний стан. Решта — безпечні або майже безпечні.
def fig_quadrant():
    W, H = 720, 500
    f = []

    gx, gy, cw, ch, gap = 210, 96, 225, 150, 16
    col0, col1 = gx, gx + cw + gap
    row0, row1 = gy, gy + ch + gap

    # заголовки стовпців
    f.append(text(col0 + cw / 2, gy - 16, "локальний / переданий", size=14, color=INK, bold=True))
    f.append(text(col1 + cw / 2, gy - 16, "спільний (глобальний)", size=14, color=INK, bold=True))

    # мітки рядків ліворуч
    f.append(text(198, row0 + ch / 2, "мутабельний", size=14, color=INK, bold=True, anchor="end"))
    f.append(text(198, row1 + ch / 2, "незмінний", size=14, color=INK, bold=True, anchor="end"))

    # клітини
    f.append(fitbox(col0, row0, cw, ch,
                    "локальна змінна,\nполе обʼєкта —\nбезпечно",
                    size=15, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(fitbox(col1, row0, cw, ch,
                    "ГЛОБАЛЬНИЙ\nМУТАБЕЛЬНИЙ СТАН —\nось де весь біль",
                    size=15, fill="#fdecea", stroke=POS, sw=2.4, bold=True, color=POS))
    f.append(fitbox(col0, row1, cw, ch,
                    "константа,\nобʼєкт-значення —\nбезпечно",
                    size=15, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(fitbox(col1, row1, cw, ch,
                    "конфіг, прочитаний\nраз і незмінний —\nздебільшого безпечно",
                    size=15, fill="#fff7e6", stroke="#b8860b", sw=2))

    f.append(text(W / 2, row1 + ch + 44,
                  "небезпечна лише одна клітина: коли стан і спільний, і мутабельний",
                  size=14, color=INK, bold=True))

    render(os.path.join(IMG, "shared-mutable-quadrant.svg"), W, H, *f)


# ── Фігура 3: лізти в глобал проти передати згори ────────────────────────────
# Ліворуч: кожен модуль тягнеться в один глобал (невидимо, звідусіль).
# Праворуч: composition root створює залежність раз і передає її вниз —
# тепер вона у сигнатурі кожного модуля, і в тест можна підставити підробку.
def fig_reach_vs_inject():
    W, H = 920, 440
    f = []

    # роздільник
    f.append(line(462, 54, 462, 410, color=MUTED, sw=1.5, dash="6 6"))
    f.append(text(232, 40, "до: кожен лізе в глобал", size=15, color=INK, bold=True))
    f.append(text(700, 40, "після: залежність передають згори", size=15, color=INK, bold=True))

    # ── ліворуч ──
    mods = [("checkout()", 92), ("report()", 176), ("job()", 260)]
    for name, y in mods:
        f.append(rect(64, y, 156, 54, fill=FILL, stroke=LINE, sw=1.5))
        f.append(text(64 + 78, y + 32, name, size=15, color=INK))
    gx, gy, gw, gh = 300, 150, 120, 96
    f.append(rect(gx, gy, gw, gh, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(text(gx + gw / 2, gy + 42, "Db", size=17, color=INK, bold=True))
    f.append(text(gx + gw / 2, gy + 64, "(глобал)", size=12, color=POS))
    for name, y in mods:
        f.append(darrow(220, y + 27, gx, gy + gh / 2, POS))
    f.append(text(232, 330, "невидимо · звідусіль", size=13, color=POS, anchor="middle"))

    # ── праворуч ──
    rx, ry, rw, rh = 556, 78, 304, 54
    f.append(rect(rx, ry, rw, rh, fill="#eef2ff", stroke=NEG, sw=2))
    f.append(text(rx + rw / 2, ry + 26, "composition root", size=15, color=INK, bold=True))
    f.append(text(rx + rw / 2, ry + 46, "new Db() — один раз", size=13, color=NEG))

    rmods = [("checkout(db)", 172), ("report(db)", 250), ("job(db)", 328)]
    # вертикальна «шина» з кореня вниз і короткі відводи в лівий край кожного модуля,
    # щоб стрілки не перетинали проміжні рамки
    bus = 556
    f.append(line(bus, ry + rh, bus, rmods[-1][1] + 26, color=NEG, sw=2))
    for name, y in rmods:
        f.append(rect(566, y, 190, 52, fill="#eafaf1", stroke=FIELD, sw=1.8))
        f.append(text(566 + 95, y + 31, name, size=15, color=INK))
        f.append(arrow(bus, y + 26, 566, y + 26, color=NEG))
    f.append(('<text x="544.0" y="243.0" font-family="%s" font-size="12" fill="%s" '
              'text-anchor="middle" transform="rotate(-90 544 243)">%s</text>'
              % (FONT, NEG, "передає db")))
    f.append(text(661, 404, "залежність — у сигнатурі", size=13, color=FIELD, anchor="middle"))

    render(os.path.join(IMG, "reach-in-vs-inject.svg"), W, H, *f)


# ── Фігура 4 (вставка proj): живий годинник викреслює вісь входів ────────────
# Похибка бага «now + 30д» дорівнює рівно Δ — затримці платежу. Живий годинник
# змушує тест стояти в точці Δ = 0, де похибка тотожно нульова. Не «важко
# зловити» — а математично невидимо. FixedClock відкриває всю вісь.
def fig_blind_axis():
    W, H = 900, 540
    f = []
    f.append(text(W / 2, 32, "похибка «now + 30д» дорівнює рівно Δ — затримці платежу",
                  size=16, color=INK, bold=True))

    x0, x1 = 200, 790          # вісь Δ
    ybase, ytop = 350, 150     # низ (похибка 0) і верх (похибка 3 дні)

    # осі
    f.append(line(x0, ybase, x1 + 24, ybase, color=INK, sw=2))
    f.append(line(x0, ybase, x0, ytop - 24, color=INK, sw=2))
    f.append(text((x0 + x1) / 2, ybase + 52, "Δ — на скільки платіж спізнився",
                  size=14, color=INK, bold=True))
    # підпис осі похибки — вертикально, ліворуч від осі, повз усі написи
    f.append(('<text x="150.0" y="260.0" font-family="%s" font-size="13" fill="%s" '
              'text-anchor="middle" font-weight="700" transform="rotate(-90 150 260)">%s</text>'
              % (FONT, INK, "зсув дня списання")))

    # поділки
    for i in range(4):
        x = x0 + (x1 - x0) * i / 3.0
        f.append(line(x, ybase, x, ybase + 7, color=INK, sw=1.5))
        f.append(text(x, ybase + 26, "%dд" % i, size=13, color=MUTED))

    # пряма «похибка = Δ» (підпис — у порожньому трикутнику під нею)
    f.append(line(x0, ybase, x1, ytop, color=NEG, sw=2.6))
    f.append(text(660, 252, "похибка = Δ", size=15, color=NEG, bold=True))

    # єдина точка, доступна живому годиннику
    f.append(circle(x0, ybase, 8, fill=POS, stroke=POS, sw=2))
    f.append(line(x0, ybase, x0, 122, color=POS, sw=2, dash="6 5"))
    f.append(fitbox(x0 - 152, 62, 304, 56,
                    "живий годинник ставить тест рівно сюди:\nΔ = 0 — а тут похибка тотожно 0",
                    size=13, fill="#fdecea", stroke=POS, sw=2, color=POS, bold=True))

    # зелена смуга — що відкриває FixedClock
    f.append(rect(x0, ybase + 66, x1 - x0, 28, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text((x0 + x1) / 2, ybase + 85, "FixedClock: уся вісь доступна",
                  size=13, color=FIELD, bold=True))

    # висновок
    f.append(text(W / 2, 496,
                  "єдиний тест, який можна написати з живим годинником, —"
                  " єдиний, який цього бага не бачить",
                  size=14, color=INK, bold=True))

    render(os.path.join(IMG, "untangle-blind-axis.svg"), W, H, *f)


# ── Фігура 5 (вставка proj): критерій, який глобал витягувати ────────────────
# Небезпека глобала = чи його значення вертається в РІШЕННЯ логіки. Той самий
# критерій дає всі чотири вироки — включно з «логер лишаємо, і це не поблажка».
def fig_seam_ladder():
    W, H = 1010, 500
    f = []
    f.append(text(W / 2, 34, "один критерій: чи значення глобала вертається в рішення логіки?",
                  size=16, color=INK, bold=True))

    cols = [("глобал", 130), ("що це для логіки", 210), ("вертається в рішення?", 270),
            ("вирок", 320)]
    rows = [
        ("годинник", "вхід", "так — вирішує\nexpired чи ok", "витягти у шов:\nпорт Clock",
         "#fdecea", POS),
        ("конфіг", "вхід", "так — вирішує\nсуму", "витягти у шов:\nзаморожене значення",
         "#fdecea", POS),
        ("лічильник", "вхід і вихід\n(read-modify-write)", "у логіку — ні,\nу тест — так",
         "дати власника:\nMetrics із замком", "#fff7e6", "#b8860b"),
        ("логер", "лише вихід\n(чистий стік)", "ні — назад\nне вертається",
         "лишити фоновим —\nсвідомо", "#eafaf1", FIELD),
    ]

    x = 40
    xs = []
    for name, w in cols:
        xs.append((x, w))
        f.append(text(x + w / 2, 74, name, size=13, color=MUTED, bold=True))
        x += w + 12

    y = 90
    rh = 76
    for r in rows:
        vals = r[:4]
        fill, col = r[4], r[5]
        for i, (cx, cw) in enumerate(xs):
            bold = (i == 0 or i == 3)
            f.append(fitbox(cx, y, cw, rh, vals[i], size=13, fill=fill,
                            stroke=col, sw=1.8, color=(col if bold else INK), bold=bold))
        y += rh + 10

    f.append(text(W / 2, y + 26,
                  "порядок швів — згори вниз: спершу те, що логіка читає найглибше",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "untangle-seam-ladder.svg"), W, H, *f)


# ── Фігура 6 (вставка proj): храповик — сітка ніколи не буває червона двічі ──
# Шов — це рефакторинг: сітка МУСИТЬ лишитися зеленою. Зміна поведінки — окремий
# крок: там тест червоніє СВІДОМО. Змішаєш обидва в одному коміті — не знатимеш,
# що саме зламалося.
def fig_ratchet():
    W, H = 1000, 400
    f = []
    f.append(text(W / 2, 34, "храповик: шов і виправлення — ніколи в одному кроці",
                  size=16, color=INK, bold=True))

    steps = [
        ("1 · брудний шов", "monkeypatch ззовні,\nхарактеризаційний тест", "#fff7e6", "#b8860b",
         "зелена", FIELD),
        ("2 · чесний шов", "залежність у конструктор,\nповедінка та сама", "#eef2ff", NEG,
         "лишається зеленою", FIELD),
        ("3 · виправлення", "now+30д → paid_until+30д,\nповедінка міняється", "#fdecea", POS,
         "червоніє СВІДОМО", POS),
        ("4 · зняти риштування", "брудний шов видалено,\nтест бʼється в чесний", "#eafaf1", FIELD,
         "зелена назавжди", FIELD),
    ]

    bw, gap = 218, 26
    x = 34
    ytop = 76
    for title, body, fill, col, net, ncol in steps:
        f.append(fitbox(x, ytop, bw, 46, title, size=14, fill=fill, stroke=col,
                        sw=2, color=col, bold=True))
        f.append(fitbox(x, ytop + 54, bw, 62, body, size=12, fill="#ffffff",
                        stroke=col, sw=1.4))
        # стан сітки під кроком
        f.append(text(x + bw / 2, ytop + 158, "сітка:", size=12, color=MUTED))
        f.append(fitbox(x, ytop + 168, bw, 34, net, size=12,
                        fill=("#eafaf1" if ncol == FIELD else "#fdecea"),
                        stroke=ncol, sw=1.8, color=ncol, bold=True))
        x += bw + gap

    # стрілки між кроками — на висоті заголовків, повз написи
    for i in range(3):
        ax = 34 + bw + i * (bw + gap)
        f.append(arrow(ax + 4, ytop + 23, ax + gap - 4, ytop + 23, color=INK))

    f.append(text(W / 2, 352,
                  "крок 2 — рефакторинг: зелене мусить лишитися зеленим."
                  "  крок 3 — рішення: червоне ти обираєш сам",
                  size=13, color=INK, bold=True))

    render(os.path.join(IMG, "untangle-ratchet.svg"), W, H, *f)


# ── Фігура (вставка hist): маятник досяжності, 1958 → 2009 ───────────────────
# Висота коробки = наскільки стан досяжний ЗА ЗАМОВЧУВАННЯМ. Угорі — «звідусіль»,
# унизу — «лише за явною згодою». Видно і напрям руху, і зворотний хід 1994-го:
# Singleton підняв маятник назад майже до вихідної точки.
def fig_pendulum():
    W, H = 1190, 535
    f = []

    AMBER_F, AMBER_S = "#fff7e6", "#b8860b"

    # ── вісь ліворуч: що означає висота ──
    f.append(mtext(68, 34, ["стан досяжний", "звідусіль"], size=13, color=POS, bold=True))
    f.append(arrow(68, 250, 68, 72, color=MUTED, sw=1.6))
    f.append(arrow(68, 288, 68, 466, color=MUTED, sw=1.6))
    f.append(mtext(68, 496, ["досяжне лише за", "явною згодою"], size=13, color=FIELD, bold=True))

    # (cy, заливка, обвідка, колір тексту, рядки)
    pts = [
        (112, "#fdecea", POS, POS, ["1958", "FORTRAN II", "COMMON —", "спільна памʼять"]),
        (186, AMBER_F, AMBER_S, INK, ["1960", "ALGOL 60", "зʼявився блок", "і локальне імʼя"]),
        (280, AMBER_F, AMBER_S, INK, ["1973", "Вулф і Шоу", "«кандидат на", "скасування»"]),
        (400, "#eafaf1", FIELD, INK, ["1977–83", "Euclid, Ada,", "Modula-2", "імпорт — явно"]),
        (168, "#fdecea", POS, POS, ["1994", "GoF Singleton", "«глобальна точка", "доступу»"]),
        (352, "#eafaf1", FIELD, INK, ["2004–08", "DI, тести,", "багатоядерність"]),
        (424, "#eafaf1", FIELD, INK, ["2009", "Гамма: «викинути", "Singleton»"]),
    ]

    xs = [210 + i * 150 for i in range(len(pts))]

    # textbox шрифт НЕ зменшує (на відміну від fitbox) — коробка росте під текст,
    # тож 13 px лишається 13 px; повертає (фрагмент, ширина, висота).
    # Спершу порахуємо коробки, щоб знати ЇХНЮ СПРАВЖНЮ ширину.
    boxes = []
    for x, (cy, fill, stroke, col, lines) in zip(xs, pts):
        boxes.append(textbox(x, cy, "\n".join(lines), size=13, pad=9,
                             fill=fill, stroke=stroke, sw=2, color=col, min_w=128))

    # зʼєднувальні відрізки — від краю до краю СПРАВЖНІХ коробок, у проміжок між
    # ними; додаємо їх ПЕРШИМИ, щоб лягли під коробки й не черкали написи
    for i in range(len(pts) - 1):
        y1, y2 = pts[i][0], pts[i + 1][0]
        # круте піднесення 1994-го малюємо червоним: це і є зворотний хід маятника
        col = POS if y2 < y1 - 40 else MUTED
        f.append(line(xs[i] + boxes[i][1] / 2, y1,
                      xs[i + 1] - boxes[i + 1][1] / 2, y2, color=col, sw=2.2))

    for frag, bw, bh in boxes:
        f.append(frag)

    render(os.path.join(IMG, "globals-pendulum.svg"), W, H, *f)


if __name__ == "__main__":
    fig_hidden_wire()
    fig_quadrant()
    fig_reach_vs_inject()
    fig_blind_axis()
    fig_seam_ladder()
    fig_ratchet()
    fig_pendulum()
    print("figs done")
