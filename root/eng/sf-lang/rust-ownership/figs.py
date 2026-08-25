# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── three-ways: три способи керувати пам'яттю ────────────────────────────────
# Ідея: ручне звільнення (швидко, але помилки), збирач сміття (безпечно, але
# коштує під час виконання) і власність Rust (безпечно й безкоштовно —
# перевірка на етапі компіляції).

def fig_three_ways():
    W, H = 760, 340
    p = []
    colw = 230
    gap = 20
    x0 = 30
    ytop = 70
    boxh = 210

    cols = [
        ("Ручне звільнення", "C / C++",
         ["ти сам кажеш", "free / delete", "", "швидко, без рантайму", "АЛЕ помилки —", "на тобі"],
         POS, "#fbe0da", "помилка можлива"),
        ("Збирач сміття", "Java / Go / C#",
         ["рантайм сам", "знаходить сміття", "", "безпечно, зручно", "АЛЕ платиш", "часом виконання"],
         NEG, "#dbe6fb", "коштує на ходу"),
        ("Власність", "Rust",
         ["компілятор доводить", "коли звільняти", "", "безпечно", "І безкоштовно —", "перевірка при збірці"],
         FIELD, "#d5f0e0", "нуль під час роботи"),
    ]

    p.append(text(W / 2, 32, "Три способи впоратися з пам'яттю", size=17, bold=True))

    for i, (title, lang, lines, col, fill, tag) in enumerate(cols):
        x = x0 + i * (colw + gap)
        p.append(rect(x, ytop, colw, boxh, fill=fill, stroke=col, sw=2, rx=8))
        p.append(text(x + colw / 2, ytop + 26, title, size=14, bold=True, color=col))
        p.append(text(x + colw / 2, ytop + 44, lang, size=11, italic=True, color=MUTED))
        yy = ytop + 74
        for ln in lines:
            if ln:
                p.append(text(x + colw / 2, yy, ln, size=12, color=INK))
            yy += 19
        # підсумковий ярлик знизу
        b, w1, h1 = textbox(x + colw / 2, ytop + boxh + 22, tag, size=12, pad=8,
                            fill=BG, stroke=col, bold=True)
        p.append(b)

    render(os.path.join(OUT, "three-ways.svg"), W, H, *p)


# ── move: присвоєння переносить власність, старе ім'я стає недійсним ──────────
# Ідея: значення в купі має рівно одного власника; b = a переносить право на
# власника b, а ім'я a більше не можна вживати — тож звільнення станеться
# рівно раз, коли помре b.

def fig_move():
    W, H = 720, 380
    p = []
    cx = W / 2

    # купа — один блок даних
    heap_x, heap_y, heap_w, heap_h = 470, 150, 190, 80
    p.append(rect(heap_x, heap_y, heap_w, heap_h, fill="#f0f1f3", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(heap_x + heap_w / 2, heap_y - 12, "дані в купі", size=12, bold=True, color=MUTED))
    p.append(text(heap_x + heap_w / 2, heap_y + heap_h / 2 + 5, "[ 1, 2, 3 ]", size=15, bold=True, color=INK))

    # дві змінні ліворуч
    ax, ay = 130, 110
    bx, by = 130, 270

    # a — колишній власник (позначаємо ✕-бейджем збоку, без лінії поверх літери)
    b, wa, ha = textbox(ax, ay, "a", size=18, pad=16, fill="#fbe0da", stroke=POS, bold=True)
    p.append(b)
    p.append(circle(ax + wa / 2, ay - ha / 2, 11, fill=BG, stroke=POS, sw=2))
    p.append(text(ax + wa / 2, ay - ha / 2 + 5, "✕", size=14, bold=True, color=POS))
    p.append(text(ax, ay - ha / 2 - 14, "більше не власник", size=12, bold=True, color=POS))
    p.append(text(ax, ay + ha / 2 + 18, "вжити a — помилка", size=11, italic=True, color=POS))

    # b — новий власник
    b, wb, hb = textbox(bx, by, "b", size=18, pad=16, fill="#d5f0e0", stroke=FIELD, bold=True)
    p.append(b)
    p.append(text(bx, by + hb / 2 + 16, "єдиний власник", size=12, bold=True, color=FIELD))

    # старий (розірваний) зв'язок a → дані: обриваємо лінію на пів-дорозі,
    # щоб напис-мітку поставити ПОЗА нею (у прогалині), а не поверх лінії
    a_sx, a_sy = ax + wa / 2 + 4, ay
    a_ex, a_ey = heap_x - 8, heap_y + 20
    gx, gy = a_sx + (a_ex - a_sx) * 0.42, a_sy + (a_ey - a_sy) * 0.42   # кінець першого відрізка
    hx, hy = a_sx + (a_ex - a_sx) * 0.68, a_sy + (a_ey - a_sy) * 0.68   # початок другого
    p.append(line(a_sx, a_sy, gx, gy, color=POS, sw=1.6, dash="6,5"))
    p.append(line(hx, hy, a_ex, a_ey, color=POS, sw=1.6, dash="6,5"))
    # мітка розриву — у прогалині між відрізками, збоку від їхньої лінії
    p.append(text((gx + hx) / 2 + 16, (gy + hy) / 2 - 4, "розірвано", size=11, bold=True, color=POS))

    # новий живий зв'язок b → дані
    p.append(arrow(bx + wb / 2 + 4, by, heap_x - 8, heap_y + heap_h - 20, color=FIELD, sw=2))

    # підпис руху
    p.append(text(cx, H - 22, "b = a  —  право власності переїхало до b; звільнення станеться рівно раз",
                  size=12, italic=True, color=MUTED))

    render(os.path.join(OUT, "move.svg"), W, H, *p)


# ── borrow-rule: спільне АБО змінне, ніколи разом ────────────────────────────
# Ідея: у будь-який момент або скільки завгодно читачів (&T), або рівно один,
# хто пише (&mut T) — але не обидва. Саме це виключає гонки й псування даних
# з-під ніг того, хто дивиться.

def fig_borrow_rule():
    W, H = 720, 360
    p = []

    data_w, data_h = 120, 56
    # ── ЛІВОРУЧ: багато читачів — дозволено ──
    lcx = 190
    dy = 180
    p.append(text(lcx, 46, "Або багато читачів", size=15, bold=True, color=NEG))
    p.append(text(lcx, 66, "&T  (спільне позичання)", size=11, italic=True, color=NEG))
    # дані (широка коробка, підпис зсунемо вниз, щоб стрілки не різали його)
    p.append(rect(lcx - data_w / 2, dy, data_w, data_h, fill="#f0f1f3", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(lcx, dy + data_h - 10, "дані", size=13, bold=True, color=INK))
    # три читачі зверху — стрілки йдуть ПРЯМО вниз на три окремі точки верхнього
    # краю коробки (не сходяться до центру, не перетинають підпис)
    for rx in (lcx - 72, lcx, lcx + 72):
        ry = dy - 74
        b, w1, h1 = textbox(rx, ry, "читач", size=11, pad=7, fill="#dbe6fb", stroke=NEG)
        p.append(b)
        p.append(arrow(rx, ry + h1 / 2 + 3, rx, dy - 3, color=NEG, sw=1.5))
    b, w1, h1 = textbox(lcx, dy + data_h + 44, "усі лише читають → безпечно", size=11, pad=8,
                        fill="#d5f0e0", stroke=FIELD, bold=True)
    p.append(b)

    # роздільник
    p.append(line(W / 2, 40, W / 2, H - 30, color=MUTED, sw=1, dash="5,5"))

    # ── ПРАВОРУЧ: рівно один, хто пише ──
    rcx = 530
    p.append(text(rcx, 46, "Або один, хто пише", size=15, bold=True, color=POS))
    p.append(text(rcx, 66, "&mut T  (виняткове позичання)", size=11, italic=True, color=POS))
    p.append(rect(rcx - data_w / 2, dy, data_w, data_h, fill="#f0f1f3", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(rcx, dy + data_h - 10, "дані", size=13, bold=True, color=INK))
    # один письменник — стрілка на лівий край коробки, повз підпис
    wcx = rcx - 34
    b, w1, h1 = textbox(wcx, dy - 74, "письменник", size=11, pad=7, fill="#fbe0da", stroke=POS)
    p.append(b)
    p.append(arrow(wcx, dy - 74 + h1 / 2 + 3, wcx, dy - 3, color=POS, sw=2))
    # заборонені інші — праворуч, з ✕-бейджем (без лінії поверх напису)
    fx = rcx + 82
    b, w1, h1 = textbox(fx, dy - 74, "ще хтось", size=11, pad=7, fill=BG, stroke=MUTED, color=MUTED)
    p.append(b)
    p.append(circle(fx + w1 / 2, dy - 74 - h1 / 2, 10, fill=BG, stroke=POS, sw=2))
    p.append(text(fx + w1 / 2, dy - 74 - h1 / 2 + 4, "✕", size=13, bold=True, color=POS))
    b, w1, h1 = textbox(rcx, dy + data_h + 44, "поки він пише — більше нікого", size=11, pad=8,
                        fill="#fbe0da", stroke=POS, bold=True)
    p.append(b)

    p.append(text(W / 2, H - 12, "Ніколи водночас: доки хтось змінює дані, ніхто інший їх не бачить",
                  size=12, italic=True, color=MUTED))

    render(os.path.join(OUT, "borrow-rule.svg"), W, H, *p)


# ── rust-timeline: народження Rust як розтягнутий розворот ───────────────────
# Ідея (для hist-вставки): не одна дата, а лінія. 2006 — особистий проєкт зі
# збирачем сміття; 2009 — Mozilla; ~2013 — ГОЛОВНА подія: збирача сміття
# викинуто на користь власності; 2015 — стабільна 1.0 фіксує результат.
# Підписи ставимо з великим запасом: станції рознесені, текст під кожною —
# у власній колонці-рамці (textbox), лінія-вісь проходить нижче написів-років.

def fig_rust_timeline():
    W, H = 900, 380
    p = []

    axis_y = 150
    x0, x1 = 120, W - 120
    p.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.5))
    # наконечник осі (час іде праворуч)
    p.append(arrow(x1 - 2, axis_y, x1 + 18, axis_y, color=INK, sw=2.5))

    # чотири станції: (частка вздовж осі, рік, короткий заголовок, опис-рядки,
    #                  колір, чи це головна подія)
    stops = [
        (0.00, "2006", "Особистий проєкт",
         ["Грейдон Гоар пише сам,", "у вільний час.", "Компілятор — на OCaml.", "МАЄ збирача сміття (@T)."],
         MUTED, False),
        (0.34, "2009", "Mozilla підхоплює",
         ["Офіційне спонсорство;", "мета — безпечний", "рушій браузера (Servo).", "Показ світу — 2010."],
         NEG, False),
        (0.68, "~2013", "Збирача сміття ВИКИНУТО",
         ["Головна подія.", "GC прибрано на користь", "власності; типостани", "й зайве — теж геть."],
         POS, True),
        (1.00, "2015", "Стабільна 1.0",
         ["15 травня 2015.", "Розворот завершено;", "обіцянка сумісності.", "Модель уже усталена."],
         FIELD, False),
    ]

    colw = 190  # ширина колонки-опису — з великим запасом під найдовший рядок
    for frac, year, head, lines, col, main in stops:
        x = x0 + (x1 - x0) * frac
        # точка на осі
        r = 11 if main else 8
        p.append(circle(x, axis_y, r, fill=(col if main else BG), stroke=col, sw=2.5))
        if main:
            p.append(circle(x, axis_y, r + 6, fill="none", stroke=col, sw=1.5))

        # рік — просто НАД точкою, велике, без накладань (вісь нижче написів-опису)
        p.append(text(x, axis_y - 26, year, size=17, bold=True, color=col))

        # опис — колонка-рамка ПІД віссю; кожна станція у своїй колонці, не тісно.
        # x колонки затиснуто в межі полотна, щоб крайні станції не вилазили.
        by = axis_y + 46
        bx = min(max(x - colw / 2, 10), W - 10 - colw)
        b = fitbox(bx, by, colw, 96, "\n".join(lines), size=12,
                   fill=("#fdecea" if main else FILL),
                   stroke=col, sw=(2 if main else 1.5))
        p.append(b)
        # заголовок станції — над її колонкою (між віссю і рамкою), у власному місці
        p.append(text(bx + colw / 2, by - 12, head, size=12, bold=True, color=col))

    p.append(text(W / 2, H - 16,
                  "Rust народжувався відніманням: головна подія — не старт, а викидання збирача сміття",
                  size=12, italic=True, color=MUTED))

    render(os.path.join(OUT, "rust-timeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_three_ways()
    fig_move()
    fig_borrow_rule()
    fig_rust_timeline()
    print("figs written to", OUT)
