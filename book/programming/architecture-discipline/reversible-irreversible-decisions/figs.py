# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Спектр за вартістю відкату: не «велике/мале», а «дешево/дорого вернути» ──
# Головна ідея статті: рішення класифікують не за розміром наслідків, а за тим,
# скільки коштує його СКАСУВАТИ. Ліворуч — двобічні двері (відкат майже дармовий),
# праворуч — однобічні (відкат руйнівний). Розмір наслідків тут ні до чого.
def fig_spectrum():
    W, H = 780, 300
    p = []
    p.append(text(W / 2, 26, "Рішення сортують не за розміром наслідків, а за вартістю відкату", size=14, bold=True))

    ax_y = 120
    x0, x1 = 70, 710
    # градієнтна вісь: від зеленого (дешево) до червоного (руйнівно)
    p.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2))
    p.append(arrow(x1 - 2, ax_y, x1 + 8, ax_y, color=INK, sw=2))
    p.append(text(x0, ax_y - 30, "двобічні двері", size=13, color=FIELD, bold=True, anchor="start"))
    p.append(text(x0, ax_y - 14, "вернувся — і майже нічого не втратив", size=10, color=MUTED, anchor="start"))
    p.append(text(x1, ax_y - 30, "однобічні двері", size=13, color=POS, bold=True, anchor="end"))
    p.append(text(x1, ax_y - 14, "назад — тільки з великою кровʼю", size=10, color=MUTED, anchor="end"))
    p.append(text(x1 + 6, ax_y + 20, "вартість відкату росте →", size=10, color=INK, anchor="end"))

    # приклади-вузли на осі (frac, підпис, колір, зверху/знизу)
    def X(f):
        return x0 + f * (x1 - x0 - 20)
    nodes = [
        (0.05, "назва змінної", FIELD, True),
        (0.22, "внутрішній модуль\nпереписати", FIELD, False),
        (0.46, "REST-ендпойнт,\nяким користуються", MUTED, True),
        (0.68, "формат даних\nу базі", POS, False),
        (0.90, "вибір хмари\nна весь стек", POS, True),
    ]
    for f, lbl, col, above in nodes:
        x = X(f)
        p.append(circle(x, ax_y, 6, fill=col, stroke=col, sw=2))
        yoff = -34 if above else 34
        p.append(line(x, ax_y, x, ax_y + (yoff * 0.55), color=col, sw=1.3, dash="3,3"))
        lines = lbl.split("\n")
        base = ax_y + (yoff + (-14 if above else 14))
        for i, ln in enumerate(lines):
            p.append(text(x, base + i * 14, ln, size=10, color=INK if col == MUTED else col,
                          bold=(col != MUTED)))

    p.append(text(W / 2, H - 18, "Дрібна зміна може бути однобічними дверима, а велика перебудова — двобічними: важить лише зворотність",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(OUT, "spectrum.svg"), W, H, *p)


# ── 2. Як шов перетворює однобічні двері на двобічні ───────────────────────────
# Прямий виклик бази з усього коду = однобічні двері (зміна бази чіпає всюди).
# Той самий вибір за інтерфейсом (порт/адаптер) = двобічні: міняється лише адаптер.
def fig_seam():
    W, H = 780, 380
    p = []
    p.append(text(W / 2, 26, "Той самий незворотний вибір, загорнутий у шов, стає зворотним", size=14, bold=True))

    # ── ЛІВОРУЧ: без шва — прямі виклики, однобічні двері ──
    lcx = 195
    p.append(text(lcx, 58, "без шва", size=13, bold=True, color=POS))
    p.append(text(lcx, 74, "кожен виклик знає конкретну базу", size=9.5, color=MUTED))
    callers = ["замовлення", "звіти", "профіль", "пошук"]
    cy0 = 100
    for i, c in enumerate(callers):
        cy = cy0 + i * 44
        p.append(rect(70, cy, 110, 32, fill="#fdf2f0", stroke=POS, sw=1.5))
        p.append(text(125, cy + 20, c, size=11, color=INK))
        p.append(arrow(180, cy + 16, 290, 178, color=POS, sw=1.6))
    # база
    p.append(rect(285, 160, 130, 40, fill="#fadbd6", stroke=POS, sw=2))
    p.append(text(350, 178, "PostgreSQL", size=12, bold=True, color=POS))
    p.append(text(350, 194, "жорстко скрізь", size=9, color=MUTED))
    p.append(text(lcx, 300, "змінити базу →", size=10.5, color=POS, bold=True))
    p.append(text(lcx, 316, "правити всі чотири виклики", size=10, color=INK))
    p.append(text(lcx, 332, "(і ще ті, що забули)", size=9.5, color=MUTED))

    # роздільник
    p.append(line(415, 60, 415, 350, color=MUTED, sw=1, dash="4,4"))

    # ── ПРАВОРУЧ: зі швом — інтерфейс, двобічні двері ──
    rcx = 600
    p.append(text(rcx, 58, "зі швом", size=13, bold=True, color=FIELD))
    p.append(text(rcx, 74, "виклики знають лише інтерфейс", size=9.5, color=MUTED))
    for i, c in enumerate(callers):
        cy = cy0 + i * 44
        p.append(rect(455, cy, 110, 32, fill="#e7f7ee", stroke=FIELD, sw=1.5))
        p.append(text(510, cy + 20, c, size=11, color=INK))
        p.append(arrow(565, cy + 16, 618, 168, color=FIELD, sw=1.6))
    # порт (інтерфейс)
    p.append(rect(615, 160, 120, 38, fill="#eef6ff", stroke=NEG, sw=2))
    p.append(text(675, 177, "Repository", size=12, bold=True, color=NEG))
    p.append(text(675, 192, "інтерфейс (порт)", size=9, color=MUTED))
    # адаптер під портом
    p.append(arrow(675, 198, 675, 232, color=NEG, sw=1.6))
    p.append(rect(615, 234, 120, 38, fill="#f4f6f8", stroke=INK, sw=1.6))
    p.append(text(675, 251, "адаптер до бази", size=11, bold=True))
    p.append(text(675, 266, "лише тут — конкретика", size=9, color=MUTED))
    p.append(text(rcx, 300, "змінити базу →", size=10.5, color=FIELD, bold=True))
    p.append(text(rcx, 316, "переписати один адаптер,", size=10, color=INK))
    p.append(text(rcx, 332, "виклики не чіпати", size=10, color=INK))

    render(os.path.join(OUT, "seam.svg"), W, H, *p)


# ── 3. Дві протилежні помилки класифікації ────────────────────────────────────
# Плутанина коштує в обидва боки: важкий процес на двобічні двері = параліч;
# легкий процес на однобічні = тихе замкнення. Ціль — по діагоналі.
def fig_mistakes():
    W, H = 760, 400
    p = []
    p.append(text(W / 2, 26, "Дві дзеркальні помилки: не тільки поспіх коштує, а й зайва обережність", size=14, bold=True))

    # сітка 2×2: рядки — який процес; стовпці — які насправді двері
    gx, gy = 210, 70
    cw, ch = 240, 130
    # заголовки стовпців
    p.append(text(gx + cw / 2, gy - 12, "насправді ДВОБІЧНІ", size=12, bold=True, color=FIELD))
    p.append(text(gx + cw + cw / 2, gy - 12, "насправді ОДНОБІЧНІ", size=12, bold=True, color=POS))
    # заголовки рядків (ліворуч від сітки, вертикально по центру рядка)
    p.append(text(gx - 12, gy + ch / 2 - 8, "легкий,", size=11, bold=True, anchor="end"))
    p.append(text(gx - 12, gy + ch / 2 + 8, "швидкий процес", size=11, bold=True, anchor="end"))
    p.append(text(gx - 12, gy + ch + ch / 2 - 8, "важкий процес,", size=11, bold=True, anchor="end"))
    p.append(text(gx - 12, gy + ch + ch / 2 + 8, "довгі узгодження", size=11, bold=True, anchor="end"))

    cells = [
        (0, 0, "#e7f7ee", FIELD, "ВІРНО", "дешеве рішення —\nзважитися й іти далі"),
        (1, 0, "#fdf2f0", POS, "ПАРАЛІЧ", "місяць нарад заради того,\nщо відкотиш за годину"),
        (0, 1, "#fdf2f0", POS, "ТИХЕ ЗАМКНЕННЯ", "продавили за мить те,\nз чого потім не вийти"),
        (1, 1, "#e7f7ee", FIELD, "ВІРНО", "серйозна перевірка перед\nдверима без вороття"),
    ]
    for col, row, fill, col_c, verdict, sub in cells:
        x = gx + col * cw
        y = gy + row * ch
        p.append(rect(x, y, cw - 12, ch - 12, fill=fill, stroke=col_c, sw=1.8))
        p.append(text(x + (cw - 12) / 2, y + 34, verdict, size=14, bold=True, color=col_c))
        for i, ln in enumerate(sub.split("\n")):
            p.append(text(x + (cw - 12) / 2, y + 62 + i * 16, ln, size=10.5, color=INK))

    p.append(text(W / 2, H - 20, "Мета — по зеленій діагоналі: важкий процес лише на однобічні двері, решту — легко й швидко",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(OUT, "mistakes.svg"), W, H, *p)


# ── 4. Родовід ідеї: одна думка, три перевтілення за 14 років ──────────────────
# Для вставки hist-one-way-doors.md. Вертикальний ланцюжок 2002→2003→2015→2016.
# Ліворуч — рік і автор; праворуч від осі — у що ідея щоразу оберталася.
def fig_lineage():
    W, H = 820, 560
    p = []
    p.append(text(W / 2, 30, "Одна думка — «незворотність народжує складність» — і три її перевтілення",
                  size=14, bold=True))

    axx = 250                      # вертикальна вісь часу
    y0, y1 = 90, 500
    p.append(line(axx, y0, axx, y1, color=INK, sw=2))
    p.append(arrow(axx, y1 - 2, axx, y1 + 10, color=INK, sw=2))

    # (y-вузол, рік, автор+місце, короткий зміст[рядки], колір рамки, форма-збоку)
    nodes = [
        (130, "2002", ["Енріко Заніното", "XP 2002, Альгеро"],
         ["незворотність — одне з чотирьох", "джерел складності; Тойота", "приборкує складність, зменшуючи", "незворотність"],
         NEG, "економічна теорема про виробництво"),
        (250, "2003", ["Мартін Фаулер", "«Who Needs an Architect?»"],
         ["задача архітектора —", "прибирати незворотність, дати", "команді право передумати згодом"],
         FIELD, "порада ремесла проєктувальникові"),
        (370, "2015", ["Джеф Безос", "лист акціонерам Amazon"],
         ["однобічні / двобічні двері", "= Тип 1 / Тип 2; велика фірма", "душить себе важким процесом"],
         POS, "простий образ для будь-кого"),
        (470, "2016", ["Джеф Безос", "лист акціонерам Amazon"],
         ["70% інформації досить;", "повільність дорожча за помилку;", "«не згоден, але берусь»"],
         POS, "готове правило швидкості"),
    ]

    lblx = axx - 22                # праворуч закінчуються підписи року/автора (anchor=end)
    boxx = axx + 24                # ліворуч починається рамка зі змістом
    boxw = 330
    for y, year, who, body, col, form in nodes:
        # вузол на осі
        p.append(circle(axx, y, 8, fill=col, stroke=col, sw=2))
        # ліворуч від осі: рік (великий) + автор/місце
        p.append(text(lblx, y - 6, year, size=17, bold=True, color=col, anchor="end"))
        p.append(text(lblx, y + 10, who[0], size=11, bold=True, anchor="end"))
        p.append(text(lblx, y + 24, who[1], size=9.5, color=MUTED, anchor="end"))
        # праворуч: рамка зі змістом
        bh = len(body) * 15 + 16
        by = y - bh / 2
        p.append(rect(boxx, by, boxw, bh, fill="#f7f9fb", stroke=col, sw=1.5))
        p.append(line(axx + 8, y, boxx, y, color=col, sw=1.4))
        ty = by + 18
        for i, ln in enumerate(body):
            p.append(text(boxx + 12, ty + i * 15, ln, size=10.5, color=INK, anchor="start"))
        # курсивом під рамкою — у яку форму обернулася ідея
        p.append(text(boxx + boxw / 2, by + bh + 13, "→ " + form, size=10, color=col, italic=True))

    p.append(text(W / 2, H - 16,
                  "Ідея не належить одному: Заніното її вимовив, Фаулер приклав до архітектури, Безос дав образ і поширив",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(OUT, "lineage.svg"), W, H, *p)


def poly(pts, color=INK, sw=2.0, dash=None, fill="none"):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pstr = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (pstr, fill, color, sw, d))


# ── 5. Анатомія вартості відкату: добуток осей, розмір серед них немає ──────────
# Три рішення як профілі з пʼятьох осей. «Переписати модуль» велике, та відкат
# малий; «формат даних» дрібне, та відкат величезний — бо важить не розмір, а осі.
def fig_anatomy():
    W, H = 900, 470
    p = []
    p.append(text(W / 2, 24, "Вартість відкату — добуток кількох осей; розміру рішення серед них немає",
                  size=14, bold=True))

    # легенда: три рішення
    leg = [(60, "A · перейменувати змінну", FIELD),
           (340, "B · переписати цілий модуль", NEG),
           (650, "C · формат даних у проді", POS)]
    for lx, lbl, col in leg:
        p.append(circle(lx, 50, 6, fill=col, stroke=col, sw=2))
        p.append(text(lx + 12, 54, lbl, size=11, color=INK, anchor="start"))

    rows = [
        ("радіус вибуху — скільки залежить",      0.06, 0.85, 0.45),
        ("жорсткість — чи є шов",                 0.05, 0.20, 0.35),
        ("гравітація даних — накопичений стан",   0.02, 0.05, 0.95),
        ("зовнішня обіцянка — видно чужим",       0.03, 0.05, 0.30),
        ("затримка звороту — коли помітиш",       0.08, 0.22, 0.85),
    ]
    ys = [120, 175, 230, 285, 340]
    tx0, tx1 = 270, 760

    def X(f):
        return tx0 + f * (tx1 - tx0)

    for (lbl, a, b, c), y in zip(rows, ys):
        p.append(text(250, y + 4, lbl, size=10.5, color=INK, anchor="end"))
        p.append(line(tx0, y, tx1, y, color=MUTED, sw=1.2))
        p.append(circle(X(a), y - 8, 5, fill=FIELD, stroke=FIELD, sw=1.5))
        p.append(circle(X(b), y,     5, fill=NEG,   stroke=NEG,   sw=1.5))
        p.append(circle(X(c), y + 8, 5, fill=POS,   stroke=POS,   sw=1.5))

    p.append(text((tx0 + tx1) / 2, 372, "низька  ←  вартість осі  →  висока",
                  size=10, color=MUTED))

    # Σ смуга: сумарна вартість відкату (добуток), розмір ні до чого
    p.append(text(60, 412, "сумарна вартість відкату:", size=11, bold=True, anchor="start"))
    p.append(rect(270, 400, 16, 12, fill=FIELD, stroke=FIELD, sw=1, rx=2))
    p.append(text(294, 410, "≈ 0 — двобічні", size=10, color=INK, anchor="start"))
    p.append(rect(270, 420, 64, 12, fill=NEG, stroke=NEG, sw=1, rx=2))
    p.append(text(342, 430, "мала — двобічні (хоча рішення велике)", size=10, color=INK, anchor="start"))
    p.append(rect(270, 440, 300, 12, fill=POS, stroke=POS, sw=1, rx=2))
    p.append(text(578, 450, "величезна — однобічні", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "anatomy.svg"), W, H, *p)


# ── 6. Цінність зворотності: обрати ПІСЛЯ того, як дізнався ─────────────────────
# Два рівноймовірні майбутні. Жорсткий вибір усереднено дає 6; гнучкий бере
# найкраще в кожному світі — 9. Різниця 3 — грошова цінність зворотності.
def fig_option():
    W, H = 820, 440
    p = []
    p.append(text(W / 2, 24, "Чому зворотність коштує грошей: обрати ПІСЛЯ того, як дізнався — цінніше",
                  size=13.5, bold=True))
    p.append(text(W / 2, 44, "Два рівноймовірні майбутні (по ½); цінність рішення — умовні бали",
                  size=10.5, color=MUTED))

    base = 330
    sc = 22  # px на бал

    def bar(xc, v, col):
        h = v * sc
        return rect(xc - 27, base - h, 54, h, fill=col, stroke=col, sw=1, rx=3)

    def outline(xc, v):
        h = v * sc
        return rect(xc - 27, base - h, 54, h, fill="none", stroke=INK, sw=3, rx=3)

    # Панель L: попит низький — просте 9, масштабоване 3
    p.append(text(210, 78, "майбутнє L: попит низький", size=11.5, bold=True))
    p.append(bar(177, 9, NEG)); p.append(bar(241, 3, FIELD))
    p.append(outline(177, 9))
    p.append(text(177, base - 9 * sc - 8, "9", size=12, bold=True, color=NEG))
    p.append(text(241, base - 3 * sc - 8, "3", size=12, bold=True, color=FIELD))
    p.append(line(140, base, 282, base, color=INK, sw=1.5))
    p.append(text(177, 348, "просте", size=9.5, color=INK))
    p.append(text(241, 348, "масштаб.", size=9.5, color=INK))

    # Панель H: попит зростає — просте 3, масштабоване 9
    p.append(text(520, 78, "майбутнє H: попит зростає", size=11.5, bold=True))
    p.append(bar(487, 3, NEG)); p.append(bar(551, 9, FIELD))
    p.append(outline(551, 9))
    p.append(text(487, base - 3 * sc - 8, "3", size=12, bold=True, color=NEG))
    p.append(text(551, base - 9 * sc - 8, "9", size=12, bold=True, color=FIELD))
    p.append(line(450, base, 590, base, color=INK, sw=1.5))
    p.append(text(487, 348, "просте", size=9.5, color=INK))
    p.append(text(551, 348, "масштаб.", size=9.5, color=INK))

    # Панель підсумку
    p.append(rect(620, 84, 190, 210, fill=FILL, stroke=MUTED, sw=1.4))
    p.append(text(715, 108, "усереднено:", size=11, bold=True))
    p.append(text(632, 136, "жорстко A:  (9+3)/2 = 6", size=10.5, color=INK, anchor="start"))
    p.append(text(632, 162, "жорстко B:  (3+9)/2 = 6", size=10.5, color=INK, anchor="start"))
    p.append(text(632, 188, "гнучко:     (9+9)/2 = 9", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(line(632, 206, 798, 206, color=MUTED, sw=1))
    p.append(text(715, 232, "цінність зворотності", size=10.5, bold=True))
    p.append(text(715, 256, "= 9 − 6 = 3", size=13, bold=True, color=FIELD))

    p.append(text(W / 2, 380,
                  "Жорсткий вибір мусить угадати наперед; гнучкий вирішує, коли туман розвіявся — різниця і є ціна зворотності.",
                  size=10.5, italic=True, color=INK))
    p.append(text(W / 2, 400, "Гнучкий бере вищий стовпчик у кожному майбутньому (обведено).",
                  size=10, italic=True, color=MUTED))
    render(os.path.join(OUT, "option-value.svg"), W, H, *p)


# ── 7. Зворотність тане: двобічні двері тихо стають однобічними ─────────────────
# Без нагляду зворотність спадає й перетинає поріг (тихе замкнення). Fitness-
# функція ловить кожен витік на білді (храповик) і тримає двері широкими.
def fig_erosion():
    W, H = 820, 430
    p = []
    p.append(text(W / 2, 24, "Зворотність — актив, що тане: двобічні двері тихо стають однобічними",
                  size=13.5, bold=True))

    x0, x1 = 90, 710
    thr = 210
    # зони
    p.append(rect(x0, 70, x1 - x0, thr - 70, fill="#eafaf1", stroke="#d5efe0", sw=1, rx=0))
    p.append(rect(x0, thr, x1 - x0, 350 - thr, fill="#fdecea", stroke="#f6d7d2", sw=1, rx=0))
    p.append(line(x0, thr, x1, thr, color=INK, sw=1.4, dash="6,4"))
    p.append(text(716, 150, "двобічні", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(text(716, 285, "однобічні", size=11, bold=True, color=POS, anchor="start"))

    # осі
    p.append(line(x0, 350, x1, 350, color=INK, sw=1.5))
    p.append(arrow(x1 - 4, 350, x1 + 8, 350, color=INK, sw=1.5))
    p.append(line(x0, 350, x0, 70, color=INK, sw=1.5))
    p.append(arrow(x0, 82, x0, 66, color=INK, sw=1.5))
    p.append(text(706, 368, "час →", size=10.5, color=INK, anchor="end"))
    p.append(text(96, 62, "зворотність", size=10.5, color=INK, anchor="start"))

    # крива 1: тане
    c1 = [(x0 + (x1 - x0) * (i / 24.0), 95 + 225 * (i / 24.0) ** 1.3) for i in range(25)]
    p.append(poly(c1, color=POS, sw=2.6))
    p.append(circle(460, thr, 5, fill=POS, stroke=POS, sw=1.5))
    p.append(text(150, 300, "тихе замкнення", size=11, bold=True, color=POS, anchor="start"))
    p.append(arrow(252, 294, 453, 216, color=INK, sw=1.5))

    # крива 2: тримається (храповик)
    c2 = [(90, 100), (175, 150), (175, 112), (300, 150), (300, 118),
          (430, 152), (430, 120), (560, 154), (560, 122), (690, 150), (710, 132)]
    p.append(poly(c2, color=FIELD, sw=2.4))

    # легенда знизу
    p.append(line(110, 392, 140, 392, color=POS, sw=3))
    p.append(text(148, 396, "без нагляду — залежності наростають, шов протікає",
                  size=10, color=INK, anchor="start"))
    p.append(line(110, 412, 140, 412, color=FIELD, sw=3))
    p.append(text(148, 416, "з fitness-функцією — витік ловить білд, двері тримаються",
                  size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "erosion.svg"), W, H, *p)


# ── 8. Паралельна зміна: одна незворотна зміна = ланцюг зворотних кроків ──────
# Для вставки proj-expand-contract.md. Три фази на часовій смузі; зелене — зворотні
# кроки (стара й нова форми живі), червоне — єдиний незворотний крок (згорнути).
def fig_phases():
    W, H = 880, 500
    p = []
    p.append(text(W / 2, 26, "Одна незворотна зміна схеми = ланцюг окремо зворотних кроків", size=14, bold=True))
    p.append(text(W / 2, 46, "розгорнути → мігрувати → згорнути; лише останній крок незворотний", size=10.5, color=MUTED))

    x0, xA, xB, x1 = 185, 430, 650, 842

    # Фонові плитки фаз: зелене — зворотні фази, червоне — незворотна.
    p.append(rect(x0, 60, xA - x0 - 3, 356, fill="#eef9f1", stroke="#eef9f1", rx=4))
    p.append(rect(xA, 60, xB - xA - 3, 356, fill="#eef9f1", stroke="#eef9f1", rx=4))
    p.append(rect(xB, 60, x1 - xB, 356, fill="#fdf0ee", stroke="#fdf0ee", rx=4))

    # Заголовки фаз
    heads = [(x0, xA, "1 · РОЗГОРНУТИ", "expand", FIELD),
             (xA, xB, "2 · МІГРУВАТИ", "migrate", FIELD),
             (xB, x1, "3 · ЗГОРНУТИ", "contract", POS)]
    for a, b, t, en, col in heads:
        p.append(rect(a + 6, 66, b - a - 15, 30, fill="#ffffff", stroke=col, sw=1.5))
        p.append(text((a + b) / 2, 78, t, size=12, bold=True, color=col))
        p.append(text((a + b) / 2, 91, "(" + en + ")", size=9, color=MUTED))

    # Лінія життя старої форми: жива в expand+migrate, гине в contract
    yOld = 135
    p.append(text(x0 - 14, yOld - 3, "стара форма", size=10.5, bold=True, anchor="end"))
    p.append(text(x0 - 14, yOld + 12, "колонка total", size=9, color=MUTED, anchor="end"))
    p.append(rect(x0, yOld - 12, xB - x0, 24, fill="#eef2fb", stroke=NEG, sw=1.6))
    p.append(text((x0 + xB) / 2, yOld + 4, "жива — читати можна будь-коли", size=10, color=NEG))
    p.append(text((xB + x1) / 2, yOld - 18, "прибрано: DROP COLUMN", size=9.5, bold=True, color=POS))
    p.append(line(xB + 8, yOld, x1 - 6, yOld, color=MUTED, sw=1.2, dash="5,4"))

    # Лінія життя нової форми: народжується в expand, лишається назавжди
    yNew = 185
    p.append(text(x0 - 14, yNew - 3, "нова форма", size=10.5, bold=True, anchor="end"))
    p.append(text(x0 - 14, yNew + 12, "amount_minor", size=9, color=MUTED, anchor="end"))
    p.append(rect(x0, yNew - 12, x1 - x0, 24, fill="#e7f7ee", stroke=FIELD, sw=1.6))
    p.append(text((x0 + xB) / 2, yNew + 4, "додано (NULL) → заповнено → єдина", size=10, color=FIELD))

    # Дужка перекриття
    yb = 228
    p.append(line(x0, yb, xB, yb, color=INK, sw=1.4))
    p.append(line(x0, yb, x0, yb - 6, color=INK, sw=1.4))
    p.append(line(xB, yb, xB, yb - 6, color=INK, sw=1.4))
    p.append(text((x0 + xB) / 2, yb + 17, "інваріант: обидві форми дійсні одночасно", size=10.5, bold=True, color=INK))

    # Стан читань/записів у кожній фазі
    ys = 272
    col_states = [
        ((x0 + xA) / 2, ["писати в ОБИДВІ", "читати стару"]),
        ((xA + xB) / 2, ["заднє заповнення пакетами", "читати обидві + звіряти", "перевести читання на нову"]),
        ((xB + x1) / 2, ["читати/писати", "лише нову"]),
    ]
    for cx, lines in col_states:
        for i, ln in enumerate(lines):
            p.append(text(cx, ys + i * 15, ln, size=9.5, color=INK))

    # Рядок відкату
    yr = 366
    p.append(text(x0 - 14, yr + 3, "відкіт кроку:", size=10.5, bold=True, anchor="end"))
    cE, cM, cC = (x0 + xA) / 2, (xA + xB) / 2, (xB + x1) / 2
    p.append(arrow(cE + 62, yr, cE - 62, yr, color=FIELD, sw=1.8))
    p.append(text(cE, yr + 20, "прибрати нову колонку", size=9.5, color=FIELD, bold=True))
    p.append(arrow(cM + 62, yr, cM - 62, yr, color=FIELD, sw=1.8))
    p.append(text(cM, yr + 20, "читання назад на стару", size=9.5, color=FIELD, bold=True))
    p.append(text(cC, yr - 4, "незворотно ⟶", size=10, color=POS, bold=True))
    p.append(text(cC, yr + 20, "нове вже доведено", size=9.5, color=INK))

    p.append(text(W / 2, H - 18,
                  "Кожен крок відкотний окремо; система замикається лише на останньому — коли нове вже перевірене живими даними",
                  size=10.5, italic=True, color=INK))
    render(os.path.join(OUT, "phases.svg"), W, H, *p)


# ── 9. Подвійний запис і подвійне читання зі звірянням ───────────────────────
def fig_dual_rw():
    W, H = 900, 450
    p = []
    p.append(text(W / 2, 26, "Подвійний запис і подвійне читання зі звірянням тримають інваріант", size=14, bold=True))
    p.append(text(W / 2, 46, "поки живуть обидві форми: кожен запис оновлює дві, кожне читання їх звіряє", size=10.5, color=MUTED))

    # ── ЛІВОРУЧ: подвійний запис ──
    p.append(text(240, 84, "ПОДВІЙНИЙ ЗАПИС", size=12, bold=True, color=NEG))
    b, _, _ = textbox(240, 122, "застосунок пише\nзамовлення", size=11, fill="#eef2fb", stroke=NEG, color=INK)
    p.append(b)
    b, _, _ = textbox(150, 250, "стара:\ntotal", size=10.5, fill="#eef2fb", stroke=NEG, bold=True)
    p.append(b)
    b, _, _ = textbox(340, 250, "нова:\namount_minor", size=10.5, fill="#e7f7ee", stroke=FIELD, bold=True)
    p.append(b)
    p.append(arrow(212, 146, 165, 226, color=INK, sw=1.7))
    p.append(arrow(268, 146, 330, 226, color=INK, sw=1.7))
    p.append(text(245, 302, "amount_minor = round(total · 100)", size=10, color=INK))
    p.append(text(245, 324, "один запис торкає обидві — не розходяться", size=9.5, italic=True, color=MUTED))

    # роздільник
    p.append(line(455, 106, 455, 360, color=MUTED, sw=1, dash="4,4"))

    # ── ПРАВОРУЧ: подвійне читання + звіряння ──
    p.append(text(672, 84, "ПОДВІЙНЕ ЧИТАННЯ + ЗВІРЯННЯ", size=12, bold=True, color=FIELD))
    b, _, _ = textbox(672, 122, "застосунок читає", size=11, fill=FILL, stroke=INK)
    p.append(b)
    b, _, _ = textbox(590, 188, "total", size=10.5, fill="#eef2fb", stroke=NEG)
    p.append(b)
    b, _, _ = textbox(758, 188, "amount_minor", size=10.5, fill="#e7f7ee", stroke=FIELD)
    p.append(b)
    p.append(arrow(648, 140, 600, 172, color=INK, sw=1.5))
    p.append(arrow(700, 140, 752, 172, color=INK, sw=1.5))
    b, _, _ = textbox(672, 256, "minor == round(total·100)?", size=10.5, fill=FILL, stroke=INK, bold=True)
    p.append(b)
    p.append(arrow(598, 204, 652, 242, color=INK, sw=1.5))
    p.append(arrow(756, 204, 700, 242, color=INK, sw=1.5))
    b, _, _ = textbox(586, 338, "збіг →\nвіддати нову", size=10, fill="#e7f7ee", stroke=FIELD)
    p.append(b)
    b, _, _ = textbox(782, 338, "розбіжність →\nтривога, стоп", size=10, fill="#fdecea", stroke=POS)
    p.append(b)
    p.append(arrow(650, 274, 600, 314, color=FIELD, sw=1.6))
    p.append(arrow(694, 274, 764, 314, color=POS, sw=1.6))

    p.append(text(W / 2, H - 16,
                  "Звіряння робить із «сподіваюся, збігається» — «виміряно, що збігається»; саме воно дає право згортати",
                  size=10.5, italic=True, color=INK))
    render(os.path.join(OUT, "dual-rw.svg"), W, H, *p)


# ── 10. Межа: доки вистачає паралельної зміни, а де потрібен strangler-fig ────
def fig_scale():
    W, H = 820, 320
    p = []
    p.append(text(W / 2, 26, "Доки вистачає паралельної зміни, а де потрібен strangler-fig", size=14, bold=True))
    p.append(text(W / 2, 46, "той самий прийом — але масштаб однобічних дверей вирішує форму", size=10.5, color=MUTED))

    axy = 150
    ax0, ax1 = 80, 760
    p.append(line(ax0, axy, ax1, axy, color=INK, sw=1.6))
    p.append(arrow(ax1 - 2, axy, ax1 + 10, axy, color=INK, sw=1.6))

    nodes = [(130, "колонка"), (275, "таблиця"), (415, "схема"),
             (565, "контракт\nміж сервісами"), (712, "успадкований\nзастосунок")]
    for x, lbl in nodes:
        p.append(circle(x, axy, 6, fill=INK, stroke=INK, sw=1.5))
        lines = lbl.split("\n")
        base = axy - 16 - (len(lines) - 1) * 13
        for i, ln in enumerate(lines):
            p.append(text(x, base + i * 13, ln, size=10, color=INK, bold=True))

    # межа власності / розгортання
    thr = 490
    p.append(line(thr, 96, thr, 210, color=POS, sw=1.4, dash="5,4"))
    p.append(text(thr, 88, "межа власності / розгортання", size=9.5, color=POS, bold=True))

    # дужки під віссю
    def bracket(a, b, y, title, sub, col):
        p.append(line(a, y, b, y, color=col, sw=1.6))
        p.append(line(a, y, a, y - 6, color=col, sw=1.6))
        p.append(line(b, y, b, y - 6, color=col, sw=1.6))
        p.append(text((a + b) / 2, y + 17, title, size=10.5, bold=True, color=col))
        p.append(text((a + b) / 2, y + 33, sub, size=9.5, color=MUTED))

    bracket(ax0 + 10, thr - 8, 232, "паралельна зміна: expand → migrate → contract",
            "один власник, одна БД — цього досить", FIELD)
    bracket(thr + 8, ax1, 232, "потрібен strangler-fig",
            "нове росте навколо старого за фасадом", POS)

    render(os.path.join(OUT, "scale.svg"), W, H, *p)


# ── 11. Премія = розрив Єнсена на опуклій функції виграшу (math-real-options) ───
# Дві дії-прямі; їхній max — опукла галочка V(s). Хорда між крайніми станами лежить
# на рівні E[V]; прогин обгортки в середній точці — V(E[s]). Розрив між ними = премія.
def fig_jensen():
    W, H = 840, 500
    p = []
    p.append(text(W / 2, 30, "Премія за зворотність = розрив Єнсена: E[V] мінус V(E[s])",
                  size=13.5, bold=True))

    xL, xR = 200, 690
    yTop, yBot = 130, 380

    def Y(v):                       # v ∈ [3,9] → координата
        return yBot - (v - 3) / 6.0 * (yBot - yTop)

    def X(s):                       # s ∈ [0,1] → координата
        return xL + s * (xR - xL)

    ax_y = yBot + 34
    p.append(line(xL - 40, ax_y, xR + 22, ax_y, color=INK, sw=1.4))
    p.append(arrow(xR + 12, ax_y, xR + 28, ax_y, color=INK, sw=1.4))
    p.append(text(xR + 24, ax_y - 8, "стан s →", size=10.5, color=INK, anchor="end"))
    p.append(line(xL - 40, ax_y, xL - 40, yTop - 12, color=INK, sw=1.4))
    p.append(arrow(xL - 40, yTop, xL - 40, yTop - 18, color=INK, sw=1.4))
    p.append(text(xL - 40, yTop - 24, "виграш V", size=10.5, color=INK, anchor="middle"))
    for v in (3, 6, 9):
        p.append(line(xL - 44, Y(v), xL - 40, Y(v), color=MUTED, sw=1))
        p.append(text(xL - 48, Y(v) + 4, str(v), size=10, color=MUTED, anchor="end"))

    p.append(line(X(0), Y(9), X(1), Y(3), color=NEG, sw=1.6, dash="5,4"))    # просте — спадає
    p.append(line(X(0), Y(3), X(1), Y(9), color=FIELD, sw=1.6, dash="5,4"))  # масштабоване — зростає
    p.append(text(X(0.17), Y(9 - 0.17 * 6) - 20, "дія «просте»", size=10.5, color=NEG, anchor="start"))
    p.append(text(X(0.17), Y(3 + 0.17 * 6) + 22, "дія «масштабоване»", size=10.5, color=FIELD, anchor="start"))

    p.append(poly([(X(0), Y(9)), (X(0.5), Y(6)), (X(1), Y(9))], color=INK, sw=3.2))

    p.append(line(X(0), Y(9), X(1), Y(9), color=POS, sw=1.6, dash="2,3"))
    p.append(text(X(0.80), Y(9) - 10, "хорда: E[V(s)] = 9", size=10.5, color=POS))

    xm = X(0.5)
    p.append(line(xm, Y(6), xm, Y(9), color=POS, sw=2.6))
    p.append(circle(xm, Y(9), 4, fill=POS, stroke=POS, sw=1))
    p.append(circle(xm, Y(6), 4, fill=INK, stroke=INK, sw=1))
    p.append(circle(X(0), Y(9), 4, fill=INK, stroke=INK, sw=1))
    p.append(circle(X(1), Y(9), 4, fill=INK, stroke=INK, sw=1))
    p.append(text(xm + 8, Y(8.7), "Π = 9 − 6 = 3", size=11.5, color=POS, bold=True, anchor="start"))
    p.append(text(xm + 8, Y(8.7) + 16, "= премія зворотності", size=9.5, color=POS, anchor="start"))

    p.append(line(xm, Y(6) + 4, xm, Y(6) + 37, color=MUTED, sw=1))
    p.append(text(xm, Y(6) + 52, "V(E[s]) = 6  (жорсткий вибір)", size=10.5, color=INK))

    for s, lbl in [(0.0, "s_L (низький попит)"), (0.5, "E[s]"), (1.0, "s_H (високий попит)")]:
        p.append(line(X(s), ax_y, X(s), ax_y + 5, color=INK, sw=1))
        p.append(text(X(s), ax_y + 20, lbl, size=9.5, color=MUTED))

    render(os.path.join(OUT, "jensen-gap.svg"), W, H, *p)


# ── 12. Премія росте з дисперсією: обидві горбами тягнуться до p=½ ──────────────
def fig_premium_variance():
    W, H = 820, 440
    p = []
    p.append(text(W / 2, 30, "Премія за зворотність росте з невизначеністю — як і дисперсія стану",
                  size=13.5, bold=True))

    x0, x1 = 130, 700
    yb, yt = 350, 110

    def X(pp):
        return x0 + pp * (x1 - x0)

    def Y(val):                     # val ∈ [0,1], пік нормовано до 1
        return yb - val * (yb - yt)

    p.append(line(x0, yb, x1 + 16, yb, color=INK, sw=1.4))
    p.append(arrow(x1 + 6, yb, x1 + 22, yb, color=INK, sw=1.4))
    p.append(text(x1 + 18, yb + 20, "p →", size=10.5, color=INK, anchor="end"))
    p.append(line(x0, yb, x0, yt - 6, color=INK, sw=1.4))
    p.append(text(x0 - 4, yt - 8, "величина", size=10.5, color=INK, anchor="start"))
    for pp, lbl in [(0.0, "0"), (0.5, "½"), (1.0, "1")]:
        p.append(line(X(pp), yb, X(pp), yb + 5, color=INK, sw=1))
        p.append(text(X(pp), yb + 20, lbl, size=10, color=MUTED))

    p.append(poly([(X(0), Y(0)), (X(0.5), Y(1.0)), (X(1), Y(0))], color=FIELD, sw=3.0))
    par = [(X(i / 40.0), Y(4 * (i / 40.0) * (1 - i / 40.0))) for i in range(41)]
    p.append(poly(par, color=NEG, sw=2.4, dash="6,4"))

    p.append(line(X(0.5), yb, X(0.5), Y(1.0), color=MUTED, sw=1, dash="3,3"))
    p.append(text(X(0.5), Y(1.0) - 12, "p = ½: пік невизначеності — пік премії", size=10.5, color=INK))
    p.append(text(X(0.03), yb - 12, "певність", size=9.5, color=MUTED, anchor="start"))
    p.append(text(X(0.97), yb - 12, "певність", size=9.5, color=MUTED, anchor="end"))

    p.append(line(160, 398, 194, 398, color=FIELD, sw=3))
    p.append(text(202, 402, "премія гнучкості  ∝  min(p, 1 − p)", size=10.5, color=INK, anchor="start"))
    p.append(line(160, 420, 194, 420, color=NEG, sw=3, dash="6,4"))
    p.append(text(202, 424, "дисперсія стану  ∝  p · (1 − p)", size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "premium-variance.svg"), W, H, *p)


# ── 13. Правило 70% строго: перетин граничних кривих і повнота знання ───────────
def fig_timing():
    import math
    W, H = 860, 500
    p = []
    p.append(text(W / 2, 28, "Правило 70%: чекай, доки цінність знання більша за ціну зволікання",
                  size=13.5, bold=True))

    x0, x1 = 120, 720
    tMax, lam, k = 4.0, 1.0, 0.30

    def X(t):
        return x0 + (t / tMax) * (x1 - x0)

    tstar = -math.log(k) / lam            # e^(−λt)=k → t*≈1.204
    t90 = -math.log(0.1) / lam            # I=0.9 → t≈2.303

    yb1, yt1 = 236, 92

    def Y1(v):
        return yb1 - v * (yb1 - yt1)

    p.append(line(x0, yb1, x1 + 14, yb1, color=INK, sw=1.3))
    p.append(arrow(x1 + 4, yb1, x1 + 20, yb1, color=INK, sw=1.3))
    p.append(text(x1 + 16, yb1 + 18, "час →", size=10, color=INK, anchor="end"))
    p.append(line(x0, yb1, x0, yt1 - 4, color=INK, sw=1.3))

    mb = [(X(i * tMax / 60.0), Y1(math.exp(-lam * i * tMax / 60.0))) for i in range(61)]
    p.append(poly(mb, color=FIELD, sw=2.6))
    p.append(line(x0, Y1(k), x1, Y1(k), color=POS, sw=2.2))
    p.append(line(X(tstar), yb1, X(tstar), Y1(k), color=MUTED, sw=1.2, dash="4,3"))
    p.append(circle(X(tstar), Y1(k), 4.5, fill=INK, stroke=INK, sw=1))

    p.append(text(X(tstar) - 46, 110, "ЧЕКАЙ", size=11, color=FIELD, bold=True, anchor="end"))
    p.append(text(X(tstar) + 46, 110, "ВИРІШУЙ", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(430, 120, "гранична цінність очікування  ρ₀λ·e^(−λt)", size=10, color=FIELD, anchor="start"))
    p.append(text(x1 - 4, Y1(k) - 8, "гранична ціна зволікання  k", size=10, color=POS, anchor="end"))
    p.append(text(X(tstar), yb1 + 18, "t* — останній відповідальний момент", size=10, color=INK))

    yb2, yt2 = 432, 300

    def Y2(v):
        return yb2 - v * (yb2 - yt2)

    p.append(line(x0, yb2, x1 + 14, yb2, color=INK, sw=1.3))
    p.append(arrow(x1 + 4, yb2, x1 + 20, yb2, color=INK, sw=1.3))
    p.append(text(x1 + 16, yb2 + 18, "час →", size=10, color=INK, anchor="end"))
    p.append(line(x0, yb2, x0, yt2 - 4, color=INK, sw=1.3))
    p.append(text(x0 - 4, yt2 - 6, "повнота знання I(t)", size=10, color=INK, anchor="start"))

    it = [(X(i * tMax / 60.0), Y2(1 - math.exp(-lam * i * tMax / 60.0))) for i in range(61)]
    p.append(poly(it, color=NEG, sw=2.6))
    p.append(line(x0, Y2(0.7), x1, Y2(0.7), color=MUTED, sw=1, dash="3,3"))
    p.append(line(x0, Y2(0.9), x1, Y2(0.9), color=MUTED, sw=1, dash="3,3"))
    p.append(text(x0 - 6, Y2(0.7) + 4, "70%", size=9.5, color=INK, anchor="end"))
    p.append(text(x0 - 6, Y2(0.9) + 4, "90%", size=9.5, color=INK, anchor="end"))
    p.append(line(X(tstar), yb2, X(tstar), Y2(0.7), color=MUTED, sw=1.2, dash="4,3"))
    p.append(circle(X(tstar), Y2(0.7), 4.5, fill=NEG, stroke=NEG, sw=1))
    p.append(line(X(t90), yb2, X(t90), Y2(0.9), color=MUTED, sw=1.2, dash="4,3"))
    p.append(circle(X(t90), Y2(0.9), 4.5, fill=MUTED, stroke=MUTED, sw=1))
    p.append(text(X(tstar) + 10, yt2 + 6, "t* дає ~70% знання", size=10, color=NEG, anchor="start"))
    p.append(text(X(t90) + 10, Y2(0.9) - 10, "90% — дорогий плаский хвіст", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "waiting-time.svg"), W, H, *p)


if __name__ == "__main__":
    fig_spectrum()
    fig_seam()
    fig_mistakes()
    fig_lineage()
    fig_anatomy()
    fig_option()
    fig_erosion()
    fig_phases()
    fig_dual_rw()
    fig_scale()
    fig_jensen()
    fig_premium_variance()
    fig_timing()
    print("figs done")
