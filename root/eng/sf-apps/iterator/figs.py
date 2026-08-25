# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_uniform():
    """Три різні колекції (масив, список, дерево) кожна народжує свій ітератор;
    усі ітератори показують той самий інтерфейс hasNext()/next(); один цикл
    праворуч смикає ці два методи, не знаючи форми колекції за ними."""
    W, H = 980, 500
    f = []

    rows = [
        (120, "Масив", "3 · 1 · 4 · 1  за індексом"),
        (250, "Список", "вузол → вузол → вузол"),
        (380, "Дерево", "вглиб / вшир / за ключем"),
    ]

    col_cx = 150      # центр колонки колекцій
    col_w = 210
    it_cx = 500       # центр колонки ітераторів
    it_w = 220
    loop_x = 760      # ліва межа блоку циклу
    loop_w = 200

    for cy, name, hint in rows:
        # колекція
        f.append(fitbox(col_cx - col_w / 2, cy - 36, col_w, 72,
                        name + "\n" + hint, size=13, bold=True, fill="#eef2f7"))
        # ітератор
        f.append(fitbox(it_cx - it_w / 2, cy - 33, it_w, 66,
                        "ітератор\nhasNext() · next()", size=13,
                        fill="#f6faf6", stroke=FIELD))
        # стрілка колекція -> ітератор
        f.append(arrow(col_cx + col_w / 2 + 6, cy, it_cx - it_w / 2 - 6, cy,
                       color=NEG, sw=2))
        f.append(text((col_cx + col_w / 2 + it_cx - it_w / 2) / 2, cy - 12,
                      "iterator()", size=11, color=NEG))
        # стрілка ітератор -> цикл
        f.append(arrow(it_cx + it_w / 2 + 6, cy, loop_x - 8, cy, color=INK, sw=2))

    # блок єдиного циклу праворуч, спільний на всі три
    f.append(rect(loop_x, 92, loop_w, 320, fill="#eef2f7", stroke=INK, sw=2))
    f.append(text(loop_x + loop_w / 2, 122, "єдиний цикл", size=14, bold=True))
    f.append(mtext(loop_x + loop_w / 2, 210,
                   ["while (it.hasNext())", "    use( it.next() )"],
                   size=13, lh=1.6, color=INK))
    f.append(mtext(loop_x + loop_w / 2, 300,
                   ["той самий", "для масиву,", "списку й дерева"],
                   size=12, lh=1.35, color=MUTED))

    # стіна незнання — пунктир між ітераторами й циклом
    wall_x = (it_cx + it_w / 2 + loop_x) / 2
    f.append(line(wall_x, 96, wall_x, 408, color=MUTED, sw=1.4, dash="6 5"))
    f.append(text(wall_x, 78, "стіна незнання", size=11.5, color=MUTED))

    # нижня примітка
    note = "Цикл не знає, масив там, список чи дерево — бачить лише hasNext() / next()"
    f.append(fitbox(W / 2 - 330, 440, 660, 42, note, size=12.5,
                    fill="#f6faf6", stroke=FIELD))

    render(os.path.join(IMG, 'iterator-uniform.svg'), W, H, *f,
           title="Одна форма обходу над різними колекціями")


def fig_control():
    """Зовнішній ітератор проти внутрішньої ітерації: хто крутить цикл.
    Ліворуч кермо в клієнта (тягне next()); праворуч кермо в колекції
    (сама кличе передану функцію на кожному елементі)."""
    W, H = 960, 470
    f = []

    div = 480
    f.append(line(div, 60, div, 430, color=MUTED, sw=1.4, dash="6 5"))

    # ── ліва панель: зовнішній ─────────────────────────────────────────────
    lx = 240
    f.append(text(lx, 78, "Зовнішній ітератор", size=15, bold=True, color=NEG))
    # драйвер зверху
    f.append(fitbox(lx - 100, 100, 200, 58, "Клієнт", size=14, bold=True,
                    fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(lx - 110, 300, 220, 58, "Ітератор", size=14, bold=True,
                    fill="#eef2f7"))
    # керує: вниз next()
    f.append(arrow(lx - 30, 160, lx - 30, 298, color=NEG, sw=2.4))
    f.append(mtext(lx - 44, 205, ["керує:", "тягне", "next()"], size=11.5,
                   color=NEG, anchor="end"))
    # віддає елемент: вгору
    f.append(arrow(lx + 40, 298, lx + 40, 160, color=MUTED, sw=1.8))
    f.append(mtext(lx + 54, 215, ["віддає", "елемент"], size=11, color=MUTED,
                   anchor="start"))
    # бейдж хто крутить
    f.append(fitbox(lx - 105, 388, 210, 40, "цикл крутить КЛІЄНТ", size=12.5,
                    bold=True, fill="#eaf0fd", stroke=NEG))

    # ── права панель: внутрішній ───────────────────────────────────────────
    rx = 720
    f.append(text(rx, 78, "Внутрішня ітерація", size=15, bold=True, color=FIELD))
    f.append(fitbox(rx - 110, 100, 220, 58, "Колекція", size=14, bold=True,
                    fill="#f6faf6", stroke=FIELD))
    f.append(fitbox(rx - 110, 300, 220, 58, "Функція клієнта", size=13.5,
                    bold=True, fill="#eef2f7"))
    # керує: вниз кличе функцію
    f.append(arrow(rx - 30, 160, rx - 30, 298, color=FIELD, sw=2.4))
    f.append(mtext(rx - 44, 200, ["керує:", "кличе", "функцію"], size=11.5,
                   color=FIELD, anchor="end"))
    # спершу віддав функцію: вгору
    f.append(arrow(rx + 46, 298, rx + 46, 160, color=MUTED, sw=1.8))
    f.append(mtext(rx + 60, 205, ["спершу", "віддав", "функцію"], size=11,
                   color=MUTED, anchor="start"))
    f.append(fitbox(rx - 115, 388, 230, 40, "цикл крутить КОЛЕКЦІЯ", size=12.5,
                    bold=True, fill="#f6faf6", stroke=FIELD))

    render(os.path.join(IMG, 'iterator-control.svg'), W, H, *f,
           title="Хто керує обходом")


def fig_lazy():
    """Ітератор як потік на витягування: нескінченне джерело ліворуч, ітератор-
    клапан пропускає по одному елементу на кожен next(), споживач бере лише три
    перші й спиняється — решта послідовності ніколи не обчислюється."""
    W, H = 960, 420
    f = []

    cy = 150
    # джерело
    f.append(fitbox(70, cy - 46, 210, 92,
                    "Нескінченне джерело\n(Фібоначчі)\n0 1 1 2 3 5 8 … ∞",
                    size=13, bold=False, fill="#eef2f7"))
    # ітератор-клапан
    f.append(fitbox(390, cy - 34, 170, 68, "ітератор\nnext(): 1 елемент",
                    size=13, bold=True, fill="#f6faf6", stroke=FIELD))
    # споживач
    f.append(fitbox(660, cy - 46, 220, 92,
                    "Споживач бере 3\nотримав 0 · 1 · 1\n→ стоп",
                    size=13, bold=False, fill="#eaf0fd", stroke=NEG))

    # стрілки
    f.append(arrow(280 + 6, cy, 390 - 6, cy, color=INK, sw=2))
    f.append(text((280 + 390) / 2, cy - 12, "тягне", size=11, color=MUTED))
    f.append(arrow(560 + 6, cy, 660 - 6, cy, color=NEG, sw=2))
    f.append(text((560 + 660) / 2, cy - 12, "по 1", size=11, color=NEG))

    # часова стрічка викликів next() унизу
    ty = 300
    f.append(text(W / 2, ty - 34, "виклики next() у часі →", size=12.5,
                  color=MUTED))
    cw, ch, gap = 96, 44, 14
    x0 = 150
    done = ["next() → 0", "next() → 1", "next() → 1"]
    for i, lab in enumerate(done):
        x = x0 + i * (cw + gap)
        f.append(fitbox(x, ty, cw, ch, lab, size=12, fill="#eaf0fd", stroke=NEG))
    # стоп-межа
    xstop = x0 + len(done) * (cw + gap)
    f.append(line(xstop + 2, ty - 10, xstop + 2, ty + ch + 10, color=POS,
                  sw=2, dash="4 4"))
    f.append(text(xstop + 12, ty - 16, "стоп", size=11.5, color=POS,
                  bold=True, anchor="start"))
    # не обчислені
    for i in range(2):
        x = xstop + 16 + i * (cw + gap)
        f.append(fitbox(x, ty, cw, ch, "next()…", size=12, fill="#f7f7f7",
                        stroke="#cfcfcf", sw=1.2, color="#9aa0a6"))
    f.append(text(xstop + 16 + 2 * (cw + gap) + 90, ty + ch / 2 + 4,
                  "… ніколи не викликано", size=12, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'iterator-lazy.svg'), W, H, *f,
           title="Лінивий обхід: елементи на вимогу")


def fig_four_acts():
    """Чотири втілення однієї ідеї обходу на осі часу: курсор бази (механізм),
    ітератори CLU (мовна конструкція), GoF (канон), STL (бібліотека)."""
    W, H = 1160, 470
    f = []

    cx = [175, 445, 715, 985]
    half = 115
    years = ["≈1974", "1974–75", "1994", "1994"]
    names = [
        "Курсор бази даних\nSEQUEL · System R",
        "Ітератори CLU\nБ. Лісков · MIT",
        "GoF «Ітератор / Курсор»\nбанда чотирьох",
        "C++ STL\nСтепанов · HP",
    ]
    kinds = [
        "МЕХАНІЗМ\nрантайм-курсор",
        "МОВНА КОНСТРУКЦІЯ\nyield · корутина",
        "КАНОН\nпатерн дістав ім'я",
        "БІБЛІОТЕКА\nкатегорії ітераторів",
    ]
    essence = [
        ["Бере записи по одному,", "ховає «де я в наборі»"],
        ["Обхід пишеш звичайно —", "мова морозить стан"],
        ["Зібрали, назвали,", "поклали в каталог"],
        ["Клей між контейнером", "і алгоритмом"],
    ]
    k_fill = ["#eef2f7", "#f6faf6", "#eaf0fd", "#fdecea"]
    k_stroke = [MUTED, FIELD, NEG, POS]

    # дужка над двома подіями 1994 року
    bx1, bx2 = cx[2] - 110, cx[3] + 110
    f.append(line(bx1, 56, bx2, 56, color=MUTED, sw=1.4))
    f.append(line(bx1, 56, bx1, 64, color=MUTED, sw=1.4))
    f.append(line(bx2, 56, bx2, 64, color=MUTED, sw=1.4))
    f.append(text((bx1 + bx2) / 2, 48, "1994 — той самий рік, дві події",
                  size=12.5, color=MUTED))

    # вісь часу
    f.append(line(60, 106, 1100, 106, color=INK, sw=1.6))

    for i, x in enumerate(cx):
        f.append(text(x, 90, years[i], size=15, bold=True, color=INK))
        f.append(circle(x, 106, 5, fill=INK, stroke=INK))
        f.append(fitbox(x - half, 126, 2 * half, 74, names[i], size=13,
                        bold=True, fill="#ffffff", stroke=INK))
        f.append(fitbox(x - half, 214, 2 * half, 56, kinds[i], size=12.5,
                        bold=True, fill=k_fill[i], stroke=k_stroke[i]))
        f.append(mtext(x, 302, essence[i], size=12, color=MUTED, lh=1.35))

    # підсумкова стрічка
    f.append(rect(60, 360, 1040, 66, fill="#f6faf6", stroke=FIELD, sw=1.5))
    f.append(text(580, 388,
                  "Та сама думка на чотирьох висотах:", size=14, bold=True))
    f.append(text(580, 410,
                  "ідея (курсор) → мовна конструкція (CLU) → канон (GoF) → "
                  "бібліотека (STL)", size=13, color=INK))

    render(os.path.join(IMG, 'iterator-four-acts.svg'), W, H, *f,
           title="Обхід, винайдений чотири рази")


def fig_yield_lineage():
    """Дві незалежні родоводи ітератора: ліворуч корутина й слово yield
    (CLU → Sather → Python, окремо Ruby, вливається Icon); праворуч —
    узагальнений вказівник STL. Різні предки, одне слово «ітератор»."""
    W, H = 1180, 510
    f = []

    # ── ліва лінія: корутина / yield ───────────────────────────────────────
    # корінь CLU
    f.append(fitbox(40, 218, 220, 60, "CLU · 1975\nyield · ітератор-корутина",
                    size=13, bold=True, fill="#f6faf6", stroke=FIELD))
    clu_c = (150, 248)
    # нащадки
    f.append(fitbox(455, 109, 180, 56, "Ruby\nблоки + yield (Matz)",
                    size=13, fill="#eef2f7"))
    f.append(fitbox(455, 220, 180, 56, "Sather\nyield (ICSI)",
                    size=13, fill="#eef2f7"))
    f.append(fitbox(455, 330, 180, 56, "Icon\nгенератори",
                    size=13, fill="#eef2f7"))
    f.append(fitbox(700, 220, 220, 56, "Python 2.2 · 2001\nгенератори (PEP 255)",
                    size=13, bold=True, fill="#eaf0fd", stroke=NEG))

    # стрілки лівої лінії
    f.append(arrow(260, 238, 452, 150, color=INK, sw=1.8))
    f.append(text(345, 178, "ітератори", size=11, color=MUTED))
    f.append(arrow(260, 250, 452, 248, color=INK, sw=1.8))
    f.append(text(355, 240, "yield", size=11, color=MUTED))
    f.append(arrow(637, 248, 698, 248, color=INK, sw=1.8))
    f.append(arrow(560, 330, 720, 278, color=INK, sw=1.8))
    f.append(text(628, 322, "генератори", size=11, color=MUTED))

    # ── розділювач ─────────────────────────────────────────────────────────
    f.append(line(955, 70, 955, 458, color=MUTED, sw=1.4, dash="6 5"))

    # ── права лінія: узагальнений вказівник ────────────────────────────────
    f.append(fitbox(960, 150, 200, 60, "Узагальнений вказівник\ngeneric programming",
                    size=12, bold=True, fill="#fdecea", stroke=POS))
    f.append(fitbox(960, 280, 200, 58, "C++ STL · 1994\nітератори-категорії",
                    size=12, bold=True, fill="#fdecea", stroke=POS))
    f.append(arrow(1060, 210, 1060, 280, color=INK, sw=1.8))
    f.append(fitbox(950, 398, 220, 54, "позиція-об'єкт,\nа не корутина",
                    size=12, fill="#f7f7f7", stroke=MUTED, sw=1.2, color=MUTED))

    # ── нижній підпис на всю ширину ────────────────────────────────────────
    f.append(mtext(W / 2, 478,
                   ["Ліворуч ітератор ВИРОБЛЯЄ значення (yield); "
                    "праворуч ітератор — це УЗАГАЛЬНЕНИЙ ВКАЗІВНИК на позицію.",
                    "Різні предки — одне слово «ітератор»."],
                   size=12.5, color=INK, lh=1.4))

    render(os.path.join(IMG, 'iterator-yield-lineage.svg'), W, H, *f,
           title="Дві родоводи «ітератора» й мандри слова yield")


def fig_fold_collapse():
    """Згортка як катаморфізм: список 3:1:4:[] переписують заміною
    конструкторів ((:) -> f, [] -> z), а тоді вираз сходить зсередини
    назовні в одне значення. Праворуч — що це і що воно значить."""
    W, H = 1040, 470
    f = []

    cx = 340  # центр конвеєра згортання

    # ── ряд «список» (cons-цепочка) ────────────────────────────────────────
    f.append(text(cx, 66, "колекція як список (cons-цепочка)", size=12.5,
                  color=MUTED))
    bw, by, bh = 58, 84, 48
    cells = [(175, "3"), (270, "1"), (365, "4"), (460, "[]")]
    for x, val in cells:
        f.append(fitbox(x, by, bw, bh, val, size=16, bold=True, fill="#eef2f7"))
    for gx in (249, 344, 439):
        f.append(text(gx, by + 32, ":", size=20, bold=True, color=MUTED))

    # стрілка вниз + правило заміни
    f.append(arrow(cx, 142, cx, 184, color=INK, sw=2))
    f.append(text(362, 166, "заміни конструктори:   (:) ↦ f,   [] ↦ z",
                  size=12.5, color=INK, anchor="start"))

    # вкладений вираз
    f.append(fitbox(175, 190, 330, 46, "f(3, f(1, f(4, z)))", size=17,
                    bold=True, fill=FILL))

    # стрілка вниз + напрям обчислення
    f.append(arrow(cx, 242, cx, 282, color=INK, sw=2))
    f.append(text(362, 264, "рахуємо зсередини (z) назовні", size=12.5,
                  color=MUTED, anchor="start"))

    # покрокове згортання
    f.append(text(cx, 300, "з f = (+),  z = 0 :", size=13.5, color=INK))
    f.append(text(cx, 326,
                  "f(4, 0) = 4   →   f(1, 4) = 5   →   f(3, 5) = 8",
                  size=14, color=INK))

    # результат
    f.append(fitbox(280, 350, 120, 52, "8", size=20, bold=True,
                    fill="#eaf7ee", stroke=FIELD))
    f.append(text(cx, 424, "усю структуру згорнуто в одне значення",
                  size=12.5, color=MUTED))

    # ── права колонка: що це ────────────────────────────────────────────────
    f.append(fitbox(690, 88, 320, 116,
                    "катаморфізм\n(гр. kata — «вниз»  +  morphe — «форма»)\n"
                    "згортає структуру ВНИЗ\nдо одного значення",
                    size=12.5, fill=FILL))
    f.append(arrow(850, 214, 850, 300, color=MUTED, sw=2))
    f.append(fitbox(690, 306, 320, 96,
                    "внутрішня ітерація\n(reduce · forEach · map)\n"
                    "= згортка над колекцією",
                    size=13, fill="#f6faf6", stroke=FIELD))

    render(os.path.join(IMG, 'iterator-fold-collapse.svg'), W, H, *f,
           title="Згортка: заміна конструкторів і сходження до значення")


def fig_defunc():
    """Виворіт: та сама згортка, але заморожена. Ліворуч колекція сама
    рекурсує вираз до кінця; праворуч вираз застигає на f(3, ▢), дірка ▢
    стає явним станом q, а клієнт тягне next()."""
    W, H = 1060, 480
    f = []

    # роздільник
    f.append(line(530, 58, 530, 442, color=MUTED, sw=1.4, dash="6 5"))
    # верхня стрічка-підпис вивороту
    f.append(text(530, 44, "інверсія керування  +  defunctionalization",
                  size=12.5, bold=True, color=INK))

    # ── ліва панель: внутрішня згортка ─────────────────────────────────────
    lx = 270
    f.append(text(lx, 78, "Внутрішня згортка (fold)", size=15, bold=True,
                  color=FIELD))
    f.append(fitbox(135, 92, 270, 54, "колекція\n[3, 1, 4]", size=13, bold=True,
                    fill="#f6faf6", stroke=FIELD))
    f.append(arrow(lx, 150, lx, 196, color=INK, sw=2))
    f.append(text(lx + 18, 176, "сама рекурсує до кінця", size=12, color=MUTED,
                  anchor="start"))
    f.append(fitbox(135, 200, 270, 46, "f(3, f(1, f(4, z)))", size=15,
                    bold=True, fill=FILL))
    f.append(arrow(lx, 250, lx, 296, color=INK, sw=2))
    f.append(fitbox(185, 300, 170, 50, "одне значення", size=13,
                    fill="#eaf7ee", stroke=FIELD))
    f.append(fitbox(120, 384, 300, 48,
                    "керує КОЛЕКЦІЯ\nкрок f неявний у рекурсії", size=12,
                    bold=True, fill="#f6faf6", stroke=FIELD))

    # ── права панель: зовнішній ітератор ───────────────────────────────────
    rx = 790
    f.append(text(rx, 78, "Зовнішній ітератор", size=15, bold=True, color=NEG))
    f.append(fitbox(650, 92, 280, 54, "стан q = решта обходу", size=13.5,
                    bold=True, fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(650, 168, 280, 46, "f(3, ▢)      ▢ = q", size=15,
                    bold=True, fill=FILL))
    f.append(fitbox(700, 300, 180, 52, "клієнт", size=14, bold=True,
                    fill="#eaf0fd", stroke=NEG))
    f.append(arrow(rx, 300, rx, 216, color=NEG, sw=2.2))
    f.append(text(rx + 18, 256, "next() → 3", size=12.5, color=NEG,
                  anchor="start"))
    f.append(text(rx + 18, 274, "q ↦ q′", size=12, color=MUTED,
                  anchor="start"))
    f.append(fitbox(645, 384, 290, 48,
                    "керує КЛІЄНТ\n«решту» згорнуто в дані (defunctionalization)",
                    size=11, bold=True, fill="#eaf0fd", stroke=NEG))

    # стрілка вивороту через роздільник (ліва згортка -> права дірка)
    f.append(arrow(408, 223, 648, 191, color=INK, sw=2))

    render(os.path.join(IMG, 'iterator-defunc.svg'), W, H, *f,
           title="Виворіт згортки: континуацію обертають на явний стан")


def fig_automaton():
    """Зовнішній ітератор як детермінований автомат обходу: ланцюг станів
    q0 -> q1 -> ... -> qn з переходами δ, що видають елементи; для списку
    стани — суфікси, фінальний стан дає hasNext()=false."""
    W, H = 1080, 470
    f = []

    y = 170
    states = [(150, "q₀", "[3,1,4]"),
              (370, "q₁", "[1,4]"),
              (590, "q₂", "[4]"),
              (810, "q₃", "[]")]

    # переходи (стрілки + підписи над ними) — малюємо ПЕРЕД колами
    trans = [(188, 332, "next() → 3"),
             (408, 552, "→ 1"),
             (628, 766, "→ 4")]
    for x1, x2, lab in trans:
        f.append(arrow(x1, y, x2, y, color=NEG, sw=2.2))
        f.append(text((x1 + x2) / 2, y - 20, lab, size=12.5, color=NEG))

    # стани-кола
    for i, (x, q, suf) in enumerate(states):
        if i == len(states) - 1:                 # фінальний — подвійне коло
            f.append(circle(x, y, 44, fill="#fdeeee", stroke=POS, sw=2))
            f.append(circle(x, y, 37, fill="#fdeeee", stroke=POS, sw=2))
        else:
            f.append(circle(x, y, 37, fill="#eef2f7", stroke=INK, sw=1.8))
        f.append(text(x, y + 6, q, size=17, bold=True))
        f.append(text(x, y + 78, suf, size=12.5, color=MUTED))

    # початковий і фінальний маркери
    f.append(text(150, 78, "q₀ від колекції", size=12, color=MUTED))
    f.append(arrow(150, 92, 150, 126, color=MUTED, sw=1.6))
    f.append(mtext(905, 158, ["◀ фінальний", "hasNext() = false"],
                   size=11.5, color=POS, anchor="start", lh=1.5))

    # легенда
    f.append(rect(115, 300, 850, 128, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(mtext(540, 332, [
        "стан q — «що лишилось обійти», обернена на дані (defunctionalization);"
        "   δ(q) = (елемент, наступний q)",
        "hasNext() = «q не фінальний»;    next() = застосувати перехід δ",
        "список:  q — суфікс [3,1,4] → [1,4] → [4] → []"
        "        дерево (in-order):  q — стек напівпройдених вузлів",
    ], size=13, color=INK, lh=1.85))

    render(os.path.join(IMG, 'iterator-automaton.svg'), W, H, *f,
           title="Зовнішній ітератор як автомат обходу")


def fig_stack_invariant():
    """Явний стек напівпройдених вузлів: збалансоване дерево 1..7, обхід дійшов
    до «3». Вузли розфарбовані (віддано / на стеку / не торкались); поряд —
    сам стек [4,3] з вершиною-наступним і формулюванням інваріанта."""
    W, H = 1020, 560
    f = []
    DONE_F, STK_F, OFF_F = "#e8f7ee", "#e7effe", "#f4f4f5"
    OFF_S = "#c9cbcf"

    # ── дерево ліворуч ──
    R = 22
    pos = {
        4: (240, 100), 2: (150, 205), 6: (330, 205),
        1: (105, 310), 3: (195, 310), 5: (285, 310), 7: (375, 310),
    }
    edges = [(4, 2), (4, 6), (2, 1), (2, 3), (6, 5), (6, 7)]
    for a, b in edges:
        x1, y1 = pos[a]; x2, y2 = pos[b]
        f.append(line(x1, y1, x2, y2, color=MUTED, sw=1.6))
    state = {1: "done", 2: "done", 3: "stk", 4: "stk",
             5: "off", 6: "off", 7: "off"}
    for k, (cx, cy) in pos.items():
        st = state[k]
        if st == "done":
            fill, stroke, col, bold = DONE_F, FIELD, INK, False
        elif st == "stk":
            fill, stroke, col, bold = STK_F, NEG, INK, True
        else:
            fill, stroke, col, bold = OFF_F, OFF_S, MUTED, False
        f.append(circle(cx, cy, R, fill=fill, stroke=stroke, sw=2))
        f.append(text(cx, cy + 5, str(k), size=16, color=col, bold=bold))
    f.append(text(240, 62, "дерево (обхід дійшов до «3»)", size=13, color=MUTED))

    # легенда під деревом
    ly = 380

    def swatch(x, fill, stroke, label):
        return (circle(x, ly, 10, fill=fill, stroke=stroke, sw=2)
                + text(x + 18, ly + 5, label, size=12.5, color=INK, anchor="start"))
    f.append(swatch(70, DONE_F, FIELD, "віддано"))
    f.append(swatch(198, STK_F, NEG, "на стеку — ще віддати"))
    f.append(swatch(398, OFF_F, OFF_S, "не торкались"))

    # ── стек праворуч ──
    sx, sw_ = 580, 160
    f.append(text(sx + sw_ / 2, 76, "явний стек", size=14, bold=True))
    f.append(fitbox(sx, 96, sw_, 52, "3  ← вершина", size=13.5, bold=True,
                    fill=STK_F, stroke=NEG))
    f.append(fitbox(sx, 150, sw_, 52, "4", size=15, bold=True,
                    fill=STK_F, stroke=NEG))
    f.append(text(sx + sw_ / 2, 224, "↑ дно стека", size=11.5, color=MUTED))
    f.append(arrow(sx + sw_ + 120, 122, sx + sw_ + 8, 122, color=NEG, sw=2.2))
    f.append(text(sx + sw_ + 128, 112, "next()", size=13, color=NEG,
                  anchor="start", bold=True))
    f.append(mtext(sx + sw_ + 128, 132,
                   ["віддасть «3»,", "далі pushLeft(∅):", "стек стане [4]"],
                   size=11, color=MUTED, anchor="start", lh=1.35))

    # інваріант унизу
    inv = ("Інваріант: вершина стека — завжди наступний ключ за зростанням.\n"
           "Нижче лежать лише предки «згори-ліворуч» — ті, чий власний ключ і праве піддерево ще попереду.\n"
           "Такі предки утворюють ланцюг, тому стек не глибший за висоту дерева h.")
    f.append(fitbox(60, 440, 900, 98, inv, size=13, fill="#f6faf6", stroke=FIELD))

    render(os.path.join(IMG, 'iterator-stack-invariant.svg'), W, H, *f,
           title="Стек напівпройдених вузлів: інваріант обходу")


def fig_next_step():
    """Один крок next() у трьох панелях: стек [4] → pop вершину 4 (віддали «4»)
    → pushLeft(праве[4]=6) заганяє 6 і 5 → стек [6,5], наступний = 5."""
    W, H = 1040, 420
    f = []
    STK_F, DONE_F = "#e7effe", "#e8f7ee"

    # before
    f.append(text(150, 92, "стек ДО кроку", size=13, color=MUTED))
    f.append(fitbox(105, 150, 90, 48, "4", size=15, bold=True,
                    fill=STK_F, stroke=NEG))
    f.append(text(150, 216, "вершина=4=наступний", size=10.5, color=MUTED))
    f.append(arrow(212, 174, 362, 174, color=INK, sw=2))

    # op box
    op = ("next() — один крок:\n"
          "1) pop вершину 4  →  віддати «4»\n"
          "2) pushLeft(праве[4]=6):\n"
          "     штовхнути 6,\n"
          "     тоді 5 (це 6.ліве),\n"
          "     5.ліве порожнє → стоп")
    f.append(fitbox(374, 92, 296, 172, op, size=12.5,
                    fill="#f6faf6", stroke=FIELD))
    f.append(fitbox(420, 300, 200, 42, "віддано ключ:  4", size=13.5, bold=True,
                    fill=DONE_F, stroke=FIELD))
    f.append(arrow(682, 174, 832, 174, color=INK, sw=2))

    # after
    f.append(text(920, 92, "стек ПІСЛЯ", size=13, color=MUTED))
    f.append(fitbox(875, 150, 92, 48, "5 ← верш.", size=13, bold=True,
                    fill=STK_F, stroke=NEG))
    f.append(fitbox(875, 202, 92, 48, "6", size=15, bold=True,
                    fill=STK_F, stroke=NEG))
    f.append(text(920, 268, "наступний = 5", size=10.5, color=MUTED))

    render(os.path.join(IMG, 'iterator-next-step.svg'), W, H, *f,
           title="Один крок next(): pop вершину, спуск лівим хребтом правого сина")


def fig_amortized():
    """Три факти складності одним поглядом: кожен вузол push/pop рівно раз →
    O(n) на обхід; поодинокі кроки коштують O(h) (довгий лівий хребет), але в
    середньому O(1); пам'ять — глибина стека O(h)."""
    W, H = 1020, 480
    f = []
    STK_F, DONE_F, OFF_F = "#e7effe", "#e8f7ee", "#f4f4f5"

    # ── ліворуч: кожен вузол двічі ──
    f.append(text(205, 66, "Кожен вузол — рівно двічі", size=14, bold=True))
    xs = [70, 112, 154, 196, 238, 280, 322]
    for i, x in enumerate(xs):
        f.append(circle(x, 150, 15, fill=OFF_F, stroke=MUTED, sw=1.6))
        f.append(text(x, 155, str(i + 1), size=12, color=MUTED))
    f.append(text(205, 200, "входить у стек 1 раз, виходить 1 раз",
                  size=12, color=INK))
    f.append(text(205, 224, "(1× push  +  1× pop на вузол)",
                  size=11.5, color=MUTED))
    f.append(fitbox(55, 262, 300, 60,
                    "усього за обхід:\n2n операцій  =  O(n)", size=14, bold=True,
                    fill=DONE_F, stroke=FIELD))

    # ── праворуч: вартість одного next() ──
    f.append(text(735, 66, "Вартість одного next()", size=14, bold=True))
    base = 300
    heights = [26, 26, 26, 118, 26, 26, 26, 118, 26]
    bx = 542
    for h in heights:
        col = NEG if h > 60 else "#b9c2cc"
        fl = STK_F if h > 60 else OFF_F
        f.append(rect(bx, base - h, 24, h, fill=fl, stroke=col, sw=1.5, rx=3))
        bx += 40
    f.append(line(538, base, bx - 12, base, color=INK, sw=1.6))
    f.append(text(730, base + 22, "кроки next() у часі →", size=11.5, color=MUTED))
    # пунктир середнього
    f.append(line(538, base - 40, bx - 12, base - 40, color=FIELD, sw=1.4, dash="5 4"))
    f.append(text(bx - 6, base - 44, "середнє ≈ O(1)", size=11, color=FIELD,
                  anchor="start", bold=True))
    f.append(fitbox(560, 332, 360, 56,
                    "високі стовпці — спуск довгим лівим хребтом O(h);\nдешеві кроки їх гасять → у середньому O(1)",
                    size=12, fill="#f6faf6", stroke=NEG))

    # ── знизу: пам'ять ──
    mem = ("Пам'ять — це глибина стека, O(h): збалансоване дерево — O(log n), "
           "вироджене (ланцюг) — O(n). Повний обхід — O(n) часу.")
    f.append(fitbox(60, 410, 900, 52, mem, size=13, fill="#eef3fb", stroke=NEG))

    render(os.path.join(IMG, 'iterator-amortized.svg'), W, H, *f,
           title="Складність: O(n) на обхід, O(1) амортизовано на крок, O(h) пам'яті")


if __name__ == '__main__':
    fig_uniform()
    fig_control()
    fig_lazy()
    fig_four_acts()
    fig_yield_lineage()
    fig_fold_collapse()
    fig_defunc()
    fig_automaton()
    fig_stack_invariant()
    fig_next_step()
    fig_amortized()
    print("ok")
