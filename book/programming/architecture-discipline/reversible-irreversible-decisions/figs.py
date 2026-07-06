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


if __name__ == "__main__":
    fig_spectrum()
    fig_seam()
    fig_mistakes()
    fig_lineage()
    print("figs done")
