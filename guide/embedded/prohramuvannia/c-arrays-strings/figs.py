# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Масиви й рядки» (guide/embedded/prohramuvannia).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def cell(x, y, w, h, val, idx=None, fill=FILL, stroke=INK, val_size=16, idx_color=MUTED):
    """Клітинка масиву: значення всередині, індекс під нею."""
    out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=4)]
    out.append(text(x + w / 2, y + h / 2 + val_size * 0.35, val, size=val_size, bold=True))
    if idx is not None:
        out.append(text(x + w / 2, y + h + 16, str(idx), size=12, color=idx_color))
    return "".join(out)


# ── Фігура 1: масив — суцільна смуга комірок, індекс = зсув ──────────────────
def fig_array_layout():
    W, H = 720, 260
    n = 6
    cw, ch = 78, 56
    x0 = (W - n * cw) / 2
    y0 = 96
    vals = ["21", "37", "12", "50", "9", "44"]
    frags = [text(W / 2, 40, "int t[6];  — шість цілих поспіль у пам'яті", size=15, bold=True)]

    # адреса-лінійка зверху
    base = 0x2000
    for i in range(n):
        frags.append(cell(x0 + i * cw, y0, cw, ch, vals[i], idx=i))
        addr = "0x%04X" % (base + i * 4)
        frags.append(text(x0 + i * cw + cw / 2, y0 - 14, addr, size=10.5, color=NEG))

    # підпис "адреса" ліворуч від лінійки адрес
    frags.append(text(x0 - 12, y0 - 14, "адреса:", size=10.5, color=NEG, anchor="end"))
    frags.append(text(x0 - 12, y0 + ch + 16, "індекс:", size=12, color=MUTED, anchor="end"))

    # формула зсуву
    fbox = fitbox((W - 560) / 2, 196, 560, 40,
                  "адреса t[i] = адреса t[0] + i × 4 байти   (int = 4 байти)",
                  size=14, fill="#eef7f0", stroke=FIELD)
    frags.append(fbox)

    render(os.path.join(IMG, 'array-layout.svg'), W, H, *frags)


# ── Фігура 2: рядок = масив char + невидимий '\0' ───────────────────────────
def fig_string_bytes():
    W, H = 720, 250
    chars = ['П', 'i', 'н', 'г', '\\0', '?', '?']
    codes = ["…", "…", "…", "…", "0", "", ""]
    show = ['П', 'i', 'н', 'г', '\\0', '', '']
    labels = ["", "", "", "", "кінець", "сміття", "сміття"]
    n = 7
    cw, ch = 84, 56
    x0 = (W - n * cw) / 2
    y0 = 92

    frags = [text(W / 2, 38, 'char s[] = "Пінг";  — компілятор сам дописав \\0', size=15, bold=True)]
    for i in range(n):
        if i < 4:
            fl = "#eef7f0"; st = FIELD
        elif i == 4:
            fl = "#fdecea"; st = POS
        else:
            fl = "#f0f0f0"; st = MUTED
        frags.append(cell(x0 + i * cw, y0, cw, ch, show[i], idx=i, fill=fl, stroke=st))
        if labels[i]:
            frags.append(text(x0 + i * cw + cw / 2, y0 + ch + 34, labels[i], size=11,
                              color=(POS if i == 4 else MUTED)))

    note = fitbox((W - 620) / 2, 190, 620, 44,
                  "Функції рядків ідуть по комірках, доки не впораються в \\0.\n"
                  "Нема \\0 — вони читають далі в сусіднє сміття.",
                  size=13, fill="#fff8e1", stroke="#e0a800")
    frags.append(note)
    render(os.path.join(IMG, 'string-bytes.svg'), W, H, *frags)


# ── Фігура 3: переповнення — запис повз межу масиву ─────────────────────────
def fig_overflow():
    W, H = 720, 250
    frags = [text(W / 2, 38, "char buf[4];  — а пишемо 6 символів", size=15, bold=True)]

    n_owned = 4
    cw, ch = 74, 54
    total = 6
    x0 = (W - total * cw) / 2
    y0 = 96
    put = ['1', '2', '3', '4', '5', '6']
    for i in range(total):
        if i < n_owned:
            fl = "#eef7f0"; st = FIELD; lab = "наш buf"
        else:
            fl = "#fdecea"; st = POS; lab = "чужа пам'ять"
        frags.append(cell(x0 + i * cw, y0, cw, ch, put[i], idx=i, fill=fl, stroke=st))

    # дужки-підписи діапазонів
    frags.append(line(x0, y0 + ch + 30, x0 + n_owned * cw, y0 + ch + 30, color=FIELD, sw=2))
    frags.append(text(x0 + n_owned * cw / 2, y0 + ch + 48, "виділено 4 байти", size=12, color=FIELD))
    frags.append(line(x0 + n_owned * cw, y0 + ch + 30, x0 + total * cw, y0 + ch + 30, color=POS, sw=2))
    frags.append(text(x0 + n_owned * cw + (total - n_owned) * cw / 2, y0 + ch + 48,
                      "затерто!", size=12, color=POS, bold=True))
    render(os.path.join(IMG, 'overflow.svg'), W, H, *frags)


# ═══ Фігури до вставки hist-buffer-overflow ═════════════════════════════════

# ── hbo 1: два способи зберегти рядок — префікс довжини vs нуль-термінатор ────
def fig_hbo_repr():
    W, H = 720, 340
    cw, ch = 62, 52
    frags = [text(W / 2, 34, "Той самий текст «Пінг» — два способи його зберегти",
                  size=15, bold=True)]

    # --- BCPL: перша комірка = довжина ---
    y1 = 92
    cells1 = ["4", "П", "i", "н", "г"]
    n1 = len(cells1)
    x1 = (W - n1 * cw) / 2
    frags.append(text(x1 - 12, y1 + ch / 2 + 5, "BCPL:", size=13, bold=True,
                      color=NEG, anchor="end"))
    for i, v in enumerate(cells1):
        if i == 0:
            fl, st = "#eaf0fd", NEG
        else:
            fl, st = "#eef7f0", FIELD
        frags.append(cell(x1 + i * cw, y1, cw, ch, v, fill=fl, stroke=st))
    frags.append(text(x1 + cw / 2, y1 + ch + 18, "довжина", size=11, color=NEG))
    frags.append(text(x1 + cw + (n1 - 1) * cw / 2, y1 + ch + 18,
                      "самі символи", size=11, color=FIELD))
    frags.append(text(x1 + n1 * cw + 14, y1 + ch / 2 + 5,
                      "розмір відомий одразу", size=11.5, color=MUTED, anchor="start"))

    # --- C: завершальний нуль ---
    y2 = 208
    cells2 = ["П", "i", "н", "г", "\\0"]
    n2 = len(cells2)
    x2 = (W - n2 * cw) / 2
    frags.append(text(x2 - 12, y2 + ch / 2 + 5, "C:", size=13, bold=True,
                      color=POS, anchor="end"))
    for i, v in enumerate(cells2):
        if i == n2 - 1:
            fl, st = "#fdecea", POS
        else:
            fl, st = "#eef7f0", FIELD
        frags.append(cell(x2 + i * cw, y2, cw, ch, v, fill=fl, stroke=st))
    frags.append(text(x2 + (n2 - 1) * cw / 2, y2 + ch + 18,
                      "самі символи", size=11, color=FIELD))
    frags.append(text(x2 + (n2 - 1) * cw + cw / 2, y2 + ch + 18, "кінець", size=11, color=POS))
    frags.append(text(x2 + n2 * cw + 14, y2 + ch / 2 + 5,
                      "довжину треба дійти й полічити", size=11.5, color=MUTED, anchor="start"))

    box = fitbox((W - 640) / 2, 292, 640, 38,
                 "Префікс довжини знає межу наперед; нуль-термінатор економить думку про лічильник,\n"
                 "але змушує щоразу бігти до кінця — і нікого не спиняє, якщо кінця немає.",
                 size=11.5, fill="#fff8e1", stroke="#e0a800")
    frags.append(box)
    render(os.path.join(IMG, 'hbo-repr.svg'), W, H, *frags)


# ── hbo 2: лінія часу BCPL → B → C ──────────────────────────────────────────
def fig_hbo_timeline():
    W, H = 720, 300
    frags = [text(W / 2, 34, "Як зник лічильник довжини: BCPL → B → C",
                  size=15, bold=True)]

    ax_y = 96
    frags.append(line(60, ax_y, W - 40, ax_y, color=MUTED, sw=2))
    stops = [
        (150, "1967", "BCPL", "Мартін Річардс",
         "перша комірка —\nчисло символів"),
        (370, "~1969", "B", "Кен Томпсон, PDP-7",
         "лічильник прибрано,\nкінець — байт '*e'"),
        (600, "~1971", "C", "Денніс Рітчі, PDP-11",
         "той самий прийом,\nкінець — байт '\\0'"),
    ]
    colors = [NEG, FIELD, POS]
    for (x, yr, lang, who, what), col in zip(stops, colors):
        frags.append(circle(x, ax_y, 7, fill=col, stroke=col))
        frags.append(text(x, ax_y - 22, yr, size=13, bold=True, color=col))
        frags.append(text(x, ax_y - 40, lang, size=15, bold=True))
        frags.append(text(x, ax_y + 30, who, size=11, color=MUTED))
        frags.append(mtext(x, ax_y + 52, what, size=11.5, color=INK, lh=1.25))
    frags.append(arrow(240, ax_y, 300, ax_y, color=MUTED))
    frags.append(arrow(470, ax_y, 530, ax_y, color=MUTED))

    box = fitbox((W - 660) / 2, 244, 660, 42,
                 "Причина в Рітчі прямим текстом: лічильник у 8–9-бітній комірці обмежував довжину рядка,\n"
                 "а тримати його було «менш зручно, ніж мати термінатор». Зручність одного дня — вада на пів століття.",
                 size=11.5, fill="#eef7f0", stroke=FIELD)
    frags.append(box)
    render(os.path.join(IMG, 'hbo-timeline.svg'), W, H, *frags)


# ── hbo 3: чому переповнення стеку небезпечне — буфер і адреса повернення ────
def fig_hbo_stack():
    W, H = 720, 330
    frags = [text(W / 2, 34, "Чому саме стек: поряд із буфером лежить адреса повернення",
                  size=15, bold=True)]

    # стек росте вниз; малюємо кадр функції як стос комірок
    bx = 150
    bw = 250
    rows = [
        ("буфер[0]", "#eef7f0", FIELD),
        ("буфер[1]", "#eef7f0", FIELD),
        ("буфер[2]", "#eef7f0", FIELD),
        ("буфер[3]", "#eef7f0", FIELD),
        ("… решта буфера", "#eef7f0", FIELD),
        ("адреса повернення", "#fdecea", POS),
    ]
    rh = 38
    y0 = 70
    for i, (lab, fl, st) in enumerate(rows):
        y = y0 + i * rh
        frags.append(rect(bx, y, bw, rh, fill=fl, stroke=st, sw=1.6, rx=4))
        frags.append(text(bx + bw / 2, y + rh / 2 + 5, lab, size=12,
                          bold=(i == len(rows) - 1)))

    # дужка "наш буфер"
    buf_top = y0
    buf_bot = y0 + 5 * rh
    frags.append(line(bx - 14, buf_top, bx - 14, buf_bot, color=FIELD, sw=2))
    frags.append(text(bx - 22, (buf_top + buf_bot) / 2, "буфер", size=12,
                      color=FIELD, anchor="end"))

    # стрілка "запис ллється далі, ніж треба"
    ax = bx + bw + 40
    frags.append(text(ax + 60, y0 + 20, "запис", size=12, bold=True, color=POS))
    frags.append(arrow(ax, y0 + 30, ax, y0 + 5 * rh + 24, color=POS, sw=2.2))
    frags.append(text(ax + 90, y0 + 3 * rh,
                      "лізе за межу", size=11.5, color=POS, anchor="middle"))
    frags.append(text(ax + 90, y0 + 3 * rh + 18,
                      "буфера…", size=11.5, color=POS, anchor="middle"))
    frags.append(text(ax + 95, y0 + 5 * rh + 6,
                      "…і затирає", size=11.5, color=POS, anchor="middle", bold=True))
    frags.append(text(ax + 95, y0 + 5 * rh + 24,
                      "адресу повернення", size=11.5, color=POS, anchor="middle", bold=True))

    box = fitbox((W - 660) / 2, 286, 660, 38,
                 "Функція, доробивши, стрибає за адресою повернення. Підмінив її — і керування піде,\n"
                 "куди захотів чужий, а не туди, звідки функцію викликали. Ось чому переповнення стеку — зброя.",
                 size=11.5, fill="#fdecea", stroke=POS)
    frags.append(box)
    render(os.path.join(IMG, 'hbo-stack.svg'), W, H, *frags)


# ═══ Фігури до ДЕТАЛЬНОЇ версії (c-arrays-strings-d) ═════════════════════════

# ── d1: та сама формула зсуву, але масштаб залежить від типу елемента ────────
def fig_stride_scaling():
    W, H = 720, 420
    frags = [text(W / 2, 34, "Зсув той самий — крок різний: індекс множиться на розмір елемента",
                  size=15, bold=True)]

    cw = 66
    ch = 46
    n = 5

    # рядок 1: int8_t (крок 1 байт)
    def strip(y, stride, label, col, base):
        x0 = (W - n * (cw + 6)) / 2
        out = [text(x0 - 14, y + ch / 2 + 5, label, size=12.5, bold=True,
                    color=col, anchor="end")]
        for i in range(n):
            x = x0 + i * (cw + 6)
            out.append(rect(x, y, cw, ch, fill="#eef7f0", stroke=FIELD, sw=1.5, rx=4))
            out.append(text(x + cw / 2, y + ch / 2 + 5, "[%d]" % i, size=13, bold=True))
            addr = base + i * stride
            out.append(text(x + cw / 2, y - 10, "0x%04X" % addr, size=9.5, color=NEG))
            out.append(text(x + cw / 2, y + ch + 15, "+%d" % (i * stride), size=10.5, color=MUTED))
        return out

    frags += strip(92, 1, "int8_t  (крок 1)", FIELD, 0x2000)
    frags += strip(196, 2, "int16_t (крок 2)", NEG, 0x2000)
    frags += strip(300, 4, "int32_t (крок 4)", POS, 0x2000)

    fb = fitbox((W - 600) / 2, 380, 600, 40,
                "адреса a[i] = адреса a[0] + i × sizeof(елемент)\n"
                "той самий i, але «на скільки байтів» щоразу інше — бо клітинка іншого розміру",
                size=12.5, fill="#fff8e1", stroke="#e0a800")
    frags.append(fb)
    render(os.path.join(IMG, 'stride-scaling.svg'), W, H, *frags)


# ── d2: розпад масиву — одне ім'я, два різні значення ────────────────────────
def fig_array_decay():
    W, H = 720, 400
    frags = [text(W / 2, 34, "Одне ім'я arr — але воно означає різне залежно від місця",
                  size=15, bold=True)]

    # ліворуч: sizeof / & — «цілий масив»
    lx = 60
    lw = 285
    ly = 74
    frags.append(rect(lx, ly, lw, 250, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=8))
    frags.append(text(lx + lw / 2, ly + 26, "під sizeof arr та &arr", size=13.5, bold=True, color=FIELD))
    frags.append(text(lx + lw / 2, ly + 46, "arr = ВЕСЬ масив", size=12.5, color=INK))
    # намалюємо цілу смугу
    n = 5
    ccw = 44
    cy0 = ly + 80
    cx0 = lx + (lw - n * ccw) / 2
    for i in range(n):
        frags.append(rect(cx0 + i * ccw, cy0, ccw, 40, fill=BG, stroke=FIELD, sw=1.4, rx=3))
        frags.append(text(cx0 + i * ccw + ccw / 2, cy0 + 25, "[%d]" % i, size=12))
    frags.append(line(cx0, cy0 + 56, cx0 + n * ccw, cy0 + 56, color=FIELD, sw=2))
    frags.append(text(lx + lw / 2, cy0 + 74, "sizeof arr = 5 × sizeof елемента", size=11.5, color=FIELD))
    frags.append(text(lx + lw / 2, cy0 + 110, "тип &arr — «покажчик на масив із 5»", size=11, color=MUTED))

    # праворуч: будь-де інде — «покажчик на [0]»
    rx0 = 375
    rw = 285
    frags.append(rect(rx0, ly, rw, 250, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    frags.append(text(rx0 + rw / 2, ly + 26, "будь-де інше (вираз, виклик)", size=13.5, bold=True, color=POS))
    frags.append(text(rx0 + rw / 2, ly + 46, "arr → &arr[0]", size=12.5, color=INK))
    # покажчик на першу клітинку
    pcx = rx0 + 60
    pcy = ly + 90
    frags.append(rect(pcx, pcy, 44, 40, fill=BG, stroke=POS, sw=1.6, rx=3))
    frags.append(text(pcx + 22, pcy + 25, "[0]", size=12, bold=True))
    for i in range(1, 4):
        frags.append(rect(pcx + i * 44, pcy, 44, 40, fill=BG, stroke=MUTED, sw=1.1, rx=3))
        frags.append(text(pcx + i * 44 + 22, pcy + 25, "[%d]" % i, size=11, color=MUTED))
    frags.append(arrow(rx0 + rw / 2 + 40, pcy - 22, pcx + 22, pcy - 3, color=POS, sw=2))
    frags.append(text(rx0 + rw / 2 + 70, pcy - 30, "лишається сама адреса", size=11, color=POS, anchor="middle"))
    frags.append(text(rx0 + rw / 2, pcy + 78, "sizeof (покажчик) = 4 чи 8 байтів —", size=11.5, color=POS))
    frags.append(text(rx0 + rw / 2, pcy + 95, "розмір АДРЕСИ, не масиву!", size=11.5, color=POS, bold=True))

    fb = fitbox((W - 640) / 2, 344, 640, 42,
                "Виняток лише для sizeof, &, та ініціалізації рядкового масиву літералом.\n"
                "Скрізь інде ім'я масиву «розпадається» на адресу першого елемента — і довжина губиться.",
                size=11.5, fill="#fff8e1", stroke="#e0a800")
    frags.append(fb)
    render(os.path.join(IMG, 'array-decay.svg'), W, H, *frags)


# ── d3: двовимірний масив — рядок за рядком в одну смугу ─────────────────────
def fig_row_major():
    W, H = 720, 430
    rows, cols = 3, 4
    frags = [text(W / 2, 34, "uint8_t m[3][4] — таблиця, а в пам'яті одна смуга рядок за рядком",
                  size=15, bold=True)]

    # ліворуч: таблиця 3×4
    tcw, tch = 48, 44
    tx0 = 70
    ty0 = 90
    palette = ["#eef7f0", "#eaf0fd", "#fdecea"]
    strokes = [FIELD, NEG, POS]
    for y in range(rows):
        frags.append(text(tx0 - 14, ty0 + y * tch + tch / 2 + 5, "y=%d" % y, size=11, color=strokes[y], anchor="end"))
        for x in range(cols):
            frags.append(rect(tx0 + x * tcw, ty0 + y * tch, tcw, tch, fill=palette[y], stroke=strokes[y], sw=1.4, rx=3))
            frags.append(text(tx0 + x * tcw + tcw / 2, ty0 + y * tch + tch / 2 + 5, "%d,%d" % (y, x), size=11))
    for x in range(cols):
        frags.append(text(tx0 + x * tcw + tcw / 2, ty0 - 10, "x=%d" % x, size=11, color=MUTED))
    frags.append(text(tx0 + cols * tcw / 2, ty0 + rows * tch + 24, "як ми її уявляємо", size=12, color=MUTED))

    # праворуч/знизу: лінійна смуга з 12 комірок
    lx0 = 60
    ly0 = 270
    lcw = 50
    total = rows * cols
    # смуга може не влізти в ширину — робимо компактні клітинки
    lcw = (W - 2 * lx0) / total
    for k in range(total):
        y = k // cols
        x = k % cols
        frags.append(rect(lx0 + k * lcw, ly0, lcw - 2, 40, fill=palette[y], stroke=strokes[y], sw=1.3, rx=3))
        frags.append(text(lx0 + k * lcw + lcw / 2 - 1, ly0 + 18, "%d,%d" % (y, x), size=10))
        frags.append(text(lx0 + k * lcw + lcw / 2 - 1, ly0 + 33, "#%d" % k, size=9, color=MUTED))
    # дужки під рядками
    for y in range(rows):
        x1 = lx0 + y * cols * lcw
        x2 = lx0 + (y + 1) * cols * lcw - 2
        frags.append(line(x1, ly0 + 50, x2, ly0 + 50, color=strokes[y], sw=2.2))
        frags.append(text((x1 + x2) / 2, ly0 + 66, "рядок y=%d" % y, size=10.5, color=strokes[y]))
    frags.append(text(W / 2, ly0 - 12, "як воно лежить у пам'яті — одна неперервна смуга", size=12, color=MUTED))

    fb = fitbox((W - 620) / 2, 362, 620, 50,
                "лінійний номер комірки m[y][x]  =  y × (к-сть стовпців) + x  =  y × 4 + x\n"
                "напр. m[2][1] → 2×4 + 1 = комірка #9 від початку смуги",
                size=12, fill="#fff8e1", stroke="#e0a800")
    frags.append(fb)
    render(os.path.join(IMG, 'row-major.svg'), W, H, *frags)


# ── d4: char arr[] (копія, писати можна) vs char *p (у Flash, писати НЕ можна) ─
def fig_str_storage():
    W, H = 720, 400
    frags = [text(W / 2, 34, "Два «рядки» — але живуть у різній пам'яті з різними правами",
                  size=15, bold=True)]

    # верх: літерал у Flash (.rodata)
    fx, fy, fw = 300, 74, 360
    frags.append(rect(fx, fy, fw, 66, fill="#f0f0f0", stroke=MUTED, sw=1.6, rx=6))
    frags.append(text(fx + fw / 2, fy + 22, ".rodata (Flash) — тільки читання", size=12.5, bold=True, color=MUTED))
    lit = ['O', 'K', '\\0']
    lcw = 40
    lx = fx + fw / 2 - len(lit) * lcw / 2
    for i, c in enumerate(lit):
        frags.append(rect(lx + i * lcw, fy + 34, lcw, 26, fill=BG, stroke=MUTED, sw=1.2, rx=3))
        frags.append(text(lx + i * lcw + lcw / 2, fy + 52, c, size=13, bold=True))

    # ліворуч-низ: char arr[] — копія в RAM (стек)
    ax, ay, aw = 60, 200, 280
    frags.append(rect(ax, ay, aw, 120, fill="#eef7f0", stroke=FIELD, sw=1.7, rx=8))
    frags.append(text(ax + aw / 2, ay + 24, 'char arr[] = "OK";', size=13, bold=True, color=FIELD))
    frags.append(text(ax + aw / 2, ay + 42, "RAM (стек) — своя КОПІЯ", size=11.5, color=FIELD))
    acw = 40
    axx = ax + aw / 2 - len(lit) * acw / 2
    for i, c in enumerate(lit):
        frags.append(rect(axx + i * acw, ay + 56, acw, 30, fill=BG, stroke=FIELD, sw=1.4, rx=3))
        frags.append(text(axx + i * acw + acw / 2, ay + 76, c, size=13, bold=True))
    frags.append(text(ax + aw / 2, ay + 106, "arr[0]='X'  — можна ✓", size=11.5, color=FIELD, bold=True))
    # стрілка копіювання з Flash
    frags.append(arrow(fx, fy + 40, ax + aw / 2, ay - 4, color=FIELD, sw=1.8))
    frags.append(text(ax + aw - 6, ay - 12, "копія при старті", size=10.5, color=FIELD, anchor="end"))

    # праворуч-низ: char *p — лише адреса, вказує у Flash
    px, py, pw = 380, 200, 280
    frags.append(rect(px, py, pw, 120, fill="#fdecea", stroke=POS, sw=1.7, rx=8))
    frags.append(text(px + pw / 2, py + 24, 'char *p = "OK";', size=13, bold=True, color=POS))
    frags.append(text(px + pw / 2, py + 42, "лише адреса → у Flash", size=11.5, color=POS))
    # маленька комірка-покажчик
    frags.append(rect(px + pw / 2 - 45, py + 56, 90, 30, fill=BG, stroke=POS, sw=1.4, rx=3))
    frags.append(text(px + pw / 2, py + 76, "0x08...", size=12, color=POS))
    frags.append(text(px + pw / 2, py + 106, "p[0]='X'  — КРАХ ✗", size=11.5, color=POS, bold=True))
    # стрілка з покажчика назад у Flash — веду ПРАВИМ краєм, повз усі центровані написи
    frags.append(arrow(px + pw - 16, py + 30, fx + fw - 24, fy + 66, color=POS, sw=1.8))

    fb = fitbox((W - 640) / 2, 344, 640, 42,
                "arr[] копіює літерал у власну (записувану) пам'ять — правиш вільно.\n"
                "p лише запам'ятовує адресу літерала у Flash — спроба запису = невизначена поведінка.",
                size=11.5, fill="#fff8e1", stroke="#e0a800")
    frags.append(fb)
    render(os.path.join(IMG, 'str-storage.svg'), W, H, *frags)


# ═══ Фігури до вставки proj-ring-buffer ══════════════════════════════════════

def _rb_cell(x, y, w, h, val, fill, stroke, idx=None, idx_below=False):
    """Комірка кільцевого буфера: значення всередині, індекс [i] над/під коміркою."""
    out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=4)]
    if val:
        out.append(text(x + w / 2, y + h / 2 + 6, val, size=15, bold=True))
    if idx is not None:
        iy = (y + h + 16) if idx_below else (y - 10)
        out.append(text(x + w / 2, iy, "[%d]" % idx, size=11.5, color=MUTED))
    return "".join(out)


def _mark_down(cx, y_cell_top, label, col):
    """Стрілка ЗВЕРХУ вниз у комірку + підпис над нею (для голови/хвоста)."""
    a0 = y_cell_top - 38
    a1 = y_cell_top - 4
    return (arrow(cx, a0, cx, a1, color=col, sw=2.2) +
            text(cx, a0 - 8, label, size=12, color=col, bold=True))


# ── rb1: смуга, зімкнена в кільце — голова пише, хвіст читає слідом ───────────
def fig_rb_ring():
    W, H = 720, 300
    n = 8
    cw, ch = 68, 50
    x0 = (W - n * cw) / 2
    y0 = 120
    # дані лежать у комірках [tail .. head-1] = [2..5]; голова й хвіст — межі
    tail, head = 2, 6
    vals = {2: "A", 3: "B", 4: "C", 5: "D"}

    frags = [text(W / 2, 34, "Кільцевий буфер: та сама смуга, зімкнена в кільце", size=15, bold=True)]
    for i in range(n):
        has = tail <= i < head
        fl = "#eef7f0" if has else BG
        st = FIELD if has else MUTED
        frags.append(_rb_cell(x0 + i * cw, y0, cw, ch, vals.get(i, ""), fl, st, idx=i, idx_below=True))

    # хвіст → перша непрочитана; голова → наступна вільна під запис (маркери ЗВЕРХУ)
    frags.append(_mark_down(x0 + tail * cw + cw / 2, y0, "хвіст (читати)", NEG))
    frags.append(_mark_down(x0 + head * cw + cw / 2, y0, "голова (писати)", POS))

    # обгортання: акуратна «дротина» ПІД смугою — з-за [7] назад у [0]
    xr = x0 + n * cw + 4               # праворуч від [7]
    xl = x0 - 4                        # ліворуч від [0]
    yb = y0 + ch                       # низ комірок
    ybot = yb + 66                     # горизонталь дротини — нижче індексів
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
                 % (xr, yb, xr, ybot, xl, ybot, xl, yb + 4, MUTED))
    frags.append(text(W / 2, ybot + 18, "після [7] знову [0]  —  обгортання",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'rb-ring.svg'), W, H, *frags)


# ── rb2: порожньо чи повно? head==tail неоднозначне → лишаємо одну вільну ─────
def fig_rb_empty_full():
    W, H = 720, 380
    n = 6
    cw, ch = 66, 46
    x0 = (W - n * cw) / 2

    frags = [text(W / 2, 34, "Порожньо чи повно? head==tail означає і те, і те", size=15, bold=True)]

    # --- Смуга А: порожньо, всі вільні, head і tail на одній комірці ---
    yA = 92
    frags.append(text(x0 - 14, yA + ch / 2 + 5, "ПОРОЖНІЙ", size=12.5, bold=True,
                      color=FIELD, anchor="end"))
    for i in range(n):
        frags.append(_rb_cell(x0 + i * cw, yA, cw, ch, "", BG, MUTED, idx=i))
    cA = x0 + 3 * cw + cw / 2
    frags.append(arrow(cA, yA + ch + 34, cA, yA + ch + 4, color=INK, sw=2.2))
    frags.append(text(cA, yA + ch + 50, "head = tail = 3", size=12, bold=True))
    frags.append(text(x0 + n * cw + 16, yA + ch / 2 + 5, "жодного байта → порожньо",
                      size=11.5, color=FIELD, anchor="start"))

    # --- Смуга Б: повно за трюком — одна комірка навмисно вільна ---
    yB = 226
    tail, head = 1, 0                 # дані [1..5], вільна лише [0]; head одразу за tail
    frags.append(text(x0 - 14, yB + ch / 2 + 5, "ПОВНИЙ", size=12.5, bold=True,
                      color=POS, anchor="end"))
    lets = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    for i in range(n):
        free = (i == head)
        fl = BG if free else "#eef7f0"
        st = POS if free else FIELD
        frags.append(_rb_cell(x0 + i * cw, yB, cw, ch, lets.get(i, ""), fl, st, idx=i))
    cH = x0 + head * cw + cw / 2
    cT = x0 + tail * cw + cw / 2
    frags.append(arrow(cH, yB + ch + 34, cH, yB + ch + 4, color=POS, sw=2.2))
    frags.append(text(cH, yB + ch + 50, "head 0", size=12, bold=True, color=POS))
    frags.append(arrow(cT, yB + ch + 34, cT, yB + ch + 4, color=NEG, sw=2.2))
    frags.append(text(cT, yB + ch + 50, "tail 1", size=12, bold=True, color=NEG))
    frags.append(text(x0 + n * cw + 16, yB + ch / 2 + 5, "[0] лишена вільною навмисно",
                      size=11.5, color=POS, anchor="start"))

    box = fitbox((W - 660) / 2, 332, 660, 42,
                 "Заборонивши заповнювати ОСТАННЮ вільну комірку, розводимо стани:\n"
                 "порожньо ⇔ head == tail;   повно ⇔ (head + 1) % SIZE == tail.",
                 size=12.5, fill="#fff8e1", stroke="#e0a800")
    frags.append(box)
    render(os.path.join(IMG, 'rb-empty-full.svg'), W, H, *frags)


# ── rb3: степінь двійки — & (SIZE-1) лишає молодші біти = остача ──────────────
def fig_rb_mask():
    W, H = 720, 360
    frags = [text(W / 2, 34, "Степінь двійки: x & (SIZE−1) == x % SIZE", size=15, bold=True)]

    nb = 7                              # 7 бітів: 64…1
    bw, bh = 42, 34
    x0 = (W - nb * bw) / 2 + 40         # трохи праворуч, ліворуч — підписи рядків
    places = [64, 32, 16, 8, 4, 2, 1]

    # заголовок розрядів
    for j in range(nb):
        frags.append(text(x0 + j * bw + bw / 2, 66, str(places[j]), size=10.5, color=MUTED))

    rows = [
        ("SIZE = 64",        [1, 0, 0, 0, 0, 0, 0], "",            INK),
        ("маска = 63",       [0, 1, 1, 1, 1, 1, 1], "SIZE − 1",    FIELD),
        ("індекс = 70",      [1, 0, 0, 0, 1, 1, 0], "",            NEG),
        ("70 & 63",          [0, 0, 0, 0, 1, 1, 0], "= 6",         POS),
    ]
    y0 = 78
    rh = 52
    for r, (lab, bits, note, col) in enumerate(rows):
        y = y0 + r * rh
        frags.append(text(x0 - 16, y + bh / 2 + 5, lab, size=12.5, bold=True,
                          color=col, anchor="end"))
        for j in range(nb):
            low = (j >= 1)             # молодші 6 бітів (усе, крім розряду 64)
            on = bits[j] == 1
            if r == 3 and on:
                fl, st = "#fdecea", POS
            elif on:
                fl, st = "#eef7f0", FIELD
            else:
                fl, st = BG, MUTED
            frags.append(rect(x0 + j * bw, y, bw, bh, fill=fl, stroke=st, sw=1.4, rx=3))
            frags.append(text(x0 + j * bw + bw / 2, y + bh / 2 + 5, str(bits[j]),
                              size=14, bold=on, color=(INK if on else MUTED)))
        if note:
            frags.append(text(x0 + nb * bw + 14, y + bh / 2 + 5, note, size=12.5,
                              color=col, bold=True, anchor="start"))

    # вертикальна риска: розряд 64 відсікається, молодші 6 лишаються
    xsep = x0 + bw
    frags.append(line(xsep, y0 - 6, xsep, y0 + 4 * rh - 14, color=POS, sw=1.6, dash="4 3"))
    frags.append(text(x0 + bw / 2, y0 + 4 * rh - 2, "відкидається", size=10, color=POS))
    frags.append(text(x0 + bw + (nb - 1) * bw / 2, y0 + 4 * rh - 2,
                      "молодші 6 бітів лишаються", size=10.5, color=FIELD))

    box = fitbox((W - 660) / 2, H - 40, 660, 34,
                 "Маска 63 = шість молодших одиниць; & лишає саме їх — а це й є остача від ділення на 64.",
                 size=12, fill="#eef7f0", stroke=FIELD)
    frags.append(box)
    render(os.path.join(IMG, 'rb-mask.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_array_layout()
    fig_string_bytes()
    fig_overflow()
    fig_hbo_repr()
    fig_hbo_timeline()
    fig_hbo_stack()
    fig_stride_scaling()
    fig_array_decay()
    fig_row_major()
    fig_str_storage()
    fig_rb_ring()
    fig_rb_empty_full()
    fig_rb_mask()
    print("OK: 13 SVG у", IMG)
