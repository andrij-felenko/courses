# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Асиметрія свободи: над лінією прив'язані, під лінією вільні ────────────
def fig_asymmetry():
    W, H = 900, 470
    p = []

    ly = 232  # лінія-контракт по центру; мітка розриває лінію, тож лінія її не перетинає
    lbl, lw, lh = textbox(W / 2, ly, "  контракт: інтерфейс — обіцянка  ",
                          size=14, bold=True, fill="#eef4ff", stroke=INK, sw=1.8, pad=8)
    p.append(line(70, ly, W / 2 - lw / 2 - 4, ly, color=INK, sw=3))
    p.append(line(W / 2 + lw / 2 + 4, ly, W - 70, ly, color=INK, sw=3))
    p.append(lbl)

    # ── ВЕРХ: хто викликає (прив'язаний до обіцянки) ──
    p.append(text(W / 2, 42, "НАД лінією — ті, хто викликає: прив'язані до обіцянки",
                  size=14, bold=True))
    callers = ["звіт", "форма", "журнал", "тест"]
    cw = 150
    gap = (W - 140 - len(callers) * cw) / (len(callers) - 1)
    for i, c in enumerate(callers):
        x = 70 + i * (cw + gap)
        p.append(rect(x, 68, cw, 50, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
        p.append(text(x + cw / 2, 98, c, size=13, bold=True, color=INK))
        # короткий стуб-стрілка над лінією (не чіпає ні підпис вище, ні мітку на лінії)
        p.append(arrow(x + cw / 2, ly - 36, x + cw / 2, ly - 20, color=POS, sw=1.7))
    p.append(text(W / 2, 148, "зміниш обіцянку — усі вони ламаються",
                  size=12.5, bold=True, color=POS))

    # ── НИЗ: як саме зроблено (вільно міняти) ──
    p.append(text(W / 2, ly + 46, "ПІД лінією — як саме зроблено: вільно переписати будь-коли",
                  size=14, bold=True))
    impls = ["буфер і кеш", "структури даних", "алгоритм", "блокування"]
    iw = 150
    gap2 = (W - 140 - len(impls) * iw) / (len(impls) - 1)
    for i, c in enumerate(impls):
        x = 70 + i * (iw + gap2)
        p.append(rect(x, ly + 68, iw, 50, fill="#eaf6ef", stroke=FIELD, sw=1.6, rx=8))
        p.append(text(x + iw / 2, ly + 98, c, size=12.5, color=INK))
    p.append(text(W / 2, ly + 150, "переписуй нутрощі — над лінією ніхто не помітить",
                  size=12.5, bold=True, color=FIELD))

    render(os.path.join(IMG, 'asymmetry.svg'), W, H, *p,
           title="Лінія рішення: над нею платиш за зміну, під нею — ні")


# ── 2. Один інтерфейс — кілька прихованих реалізацій за ним ───────────────────
def fig_one_interface_many():
    W, H = 900, 500
    p = []

    # клієнт зверху
    cw = 300
    cx = W / 2
    p.append(rect(cx - cw / 2, 60, cw, 58, fill="#fdecea", stroke=POS, sw=1.8, rx=9))
    p.append(text(cx, 84, "клієнт", size=13.5, bold=True, color=INK))
    p.append(text(cx, 104, "знає лише інтерфейс SensorReader", size=11.5, color=MUTED))

    # інтерфейс — вузька смуга-обіцянка
    iy = 166
    p.append(rect(cx - cw / 2, iy, cw, 46, fill="#eef4ff", stroke=INK, sw=2, rx=8))
    p.append(text(cx, iy + 20, "float read()  ·  bool ok()", size=13, bold=True, color=INK))
    p.append(text(cx, iy + 37, "єдина обіцянка — те, що видно", size=10.5, color=MUTED))

    # стрілка клієнт → інтерфейс
    p.append(arrow(cx, 120, cx, iy - 4, color=POS, sw=1.8))

    # три реалізації внизу за одним інтерфейсом
    impls = [
        ("FakeSensor", ["повертає стале число", "для тесту — без заліза"], "#eaf6ef", FIELD),
        ("I2cSensor", ["читає регістр по шині I2C", "реальний давач"], "#eaf6ef", FIELD),
        ("FileSensor", ["бере рядок із файлу", "відтворення запису"], "#eaf6ef", FIELD),
    ]
    bw = 250
    total = len(impls) * bw + (len(impls) - 1) * 26
    startx = (W - total) / 2
    by = 320
    for i, (nm, desc, fill, col) in enumerate(impls):
        x = startx + i * (bw + 26)
        p.append(rect(x, by, bw, 96, fill=fill, stroke=col, sw=1.6, rx=9))
        p.append(text(x + bw / 2, by + 26, nm, size=13, bold=True, color=INK))
        for j, d in enumerate(desc):
            p.append(text(x + bw / 2, by + 50 + j * 20, d, size=11, color=MUTED))
        # пунктир від інтерфейсу вниз до кожної реалізації — «виконує обіцянку»
        p.append(line(cx, iy + 46, x + bw / 2, by, color=FIELD, sw=1.5, dash="6,5"))

    p.append(text(cx, H - 26,
                  "підміна реалізації внизу не чіпає клієнта вгорі — обіцянка та сама",
                  size=12.5, bold=True, color=FIELD))

    render(os.path.join(IMG, 'one-interface-many.svg'), W, H, *p,
           title="Одна обіцянка, різні нутрощі: реалізацію підставляють ззовні")


# ── 3. Дві декомпозиції KWIC Парнаса: за кроками vs за прихованим рішенням ─────
def fig_kwic_two_ways():
    W, H = 940, 560
    p = []

    # заголовки двох колонок
    lx, rx_ = 250, 710
    p.append(text(lx, 34, "Розклад за кроками роботи", size=14.5, bold=True, color=POS))
    p.append(text(rx_, 34, "Розклад за прихованим рішенням", size=14.5, bold=True, color=FIELD))
    p.append(text(lx, 56, "(як тече потік даних)", size=11, color=MUTED))
    p.append(text(rx_, 56, "(що найімовірніше зміниться)", size=11, color=MUTED))

    # ── ЛІВО: ланцюг кроків, усі знають спільний формат сховища ──
    steps = ["Ввід", "Циклічний\nзсув", "Впорядкування", "Вивід"]
    bw, bh = 180, 50
    ly0 = 96
    vgap = 32
    lcx = lx + 42   # ланцюг зсунуто праворуч, щоб зліва лишити місце під формат-рамку
    for i, s in enumerate(steps):
        y = ly0 + i * (bh + vgap)
        p.append(rect(lcx - bw / 2, y, bw, bh, fill="#fdecea", stroke=POS, sw=1.7, rx=8))
        p.append(mtext(lcx, y + bh / 2 - 4, s.split("\n"), size=12.5, bold=True, color=INK))
        if i < len(steps) - 1:
            p.append(arrow(lcx, y + bh, lcx, y + bh + vgap, color=POS, sw=1.7))
    # спільне знання формату — збоку зліва, пунктири «всі знають» до кожного кроку
    kbx = lcx - bw / 2 - 92
    kby = ly0 + 1.5 * (bh + vgap)
    kb, kw_, kh = textbox(kbx, kby, "формат\nсховища\nрядків",
                          size=11, bold=True, fill="#fff3f0", stroke=POS, sw=1.6, pad=7)
    for i in range(len(steps)):
        y = ly0 + i * (bh + vgap) + bh / 2
        p.append(line(kbx + kw_ / 2, kby, lcx - bw / 2, y, color=POS, sw=1.2, dash="4,4"))
    p.append(kb)
    p.append(text(lx, ly0 + len(steps) * (bh + vgap) + 8,
                  "формат знають УСІ модулі", size=12, bold=True, color=POS))
    p.append(text(lx, ly0 + len(steps) * (bh + vgap) + 28,
                  "зміниш його — правити скрізь", size=11.5, color=POS))

    # ── ПРАВО: сховище як окремий модуль, що ховає свій формат ──
    #   Master + споживачі говорять із Line Storage лише через операції
    rmods = ["Ввід", "Циклічний зсув", "Впорядкування", "Вивід"]
    rbw, rbh = 150, 44
    # споживачі в колонці
    rcol_x = rx_ + 95
    rcol_y0 = 96
    rvg = 22
    for i, s in enumerate(rmods):
        y = rcol_y0 + i * (rbh + rvg)
        p.append(rect(rcol_x - rbw / 2, y, rbw, rbh, fill="#eaf6ef", stroke=FIELD, sw=1.6, rx=8))
        p.append(text(rcol_x, y + rbh / 2 + 4, s, size=11.5, bold=True, color=INK))
    # модуль-сховище зліва в правій половині
    stx = rx_ - 140
    sty = rcol_y0 + 1.5 * (rbh + rvg)
    sb, sbw, sbh = textbox(stx, sty, "Сховище рядків\n(операції: додай,\nдай слово)",
                           size=11.5, bold=True, fill="#e3f4ea", stroke=FIELD, sw=2, pad=10)
    p.append(sb)
    # стрілки від кожного споживача → до операцій сховища (не до формату!)
    for i in range(len(rmods)):
        y = rcol_y0 + i * (rbh + rvg) + rbh / 2
        p.append(line(rcol_x - rbw / 2, y, stx + sbw / 2, sty, color=FIELD, sw=1.3))
    # прихований формат — маленька рамка ВСЕРЕДИНІ впливу сховища, замкнена
    hid_y = sty + sbh / 2 + 40
    hb, hbw, hbh = textbox(stx, hid_y, "формат сховища —\nсховано ТУТ",
                           size=10.5, bold=True, fill="#ffffff", stroke=FIELD, sw=1.5, pad=7)
    p.append(line(stx, sty + sbh / 2, stx, hid_y - hbh / 2, color=FIELD, sw=1.4, dash="3,3"))
    p.append(hb)
    p.append(text(rx_, H - 44,
                  "формат знає ЛИШЕ сховище", size=12, bold=True, color=FIELD))
    p.append(text(rx_, H - 24,
                  "зміниш його — правиш один модуль", size=11.5, color=FIELD))

    # вертикальний розділювач колонок
    p.append(line(470, 76, 470, H - 60, color=MUTED, sw=1, dash="2,6"))

    render(os.path.join(IMG, 'kwic-two-ways.svg'), W, H, *p,
           title="KWIC у Парнаса: розклад за кроками проти розкладу за прихованим рішенням")


# ── 4. Непрозорий вказівник: один заголовок над трьома реалізаціями ───────────
def fig_opaque_swap():
    W, H = 900, 600
    p = []
    cx = W / 2

    # клієнт (незмінний) угорі
    cb, cbw, cbh = textbox(cx, 78, "клієнт main.c — той самий для всіх трьох",
                           size=14.5, bold=True, fill="#eef4ff", stroke=NEG, sw=2, pad=12)
    p.append(cb)
    p.append(text(cx, 122, "бачить лише заголовок; тримає Stack*, не будову",
                  size=12, color=MUTED, italic=True))
    p.append(arrow(cx, 132, cx, 168, color=NEG, sw=2))

    # заголовок stack.h — незмінна смуга-контракт
    hy = 176
    hh = 96
    p.append(rect(66, hy, W - 132, hh, fill="#f0fbf3", stroke=FIELD, sw=2.5, rx=9))
    p.append(text(cx, hy + 26, "stack.h — обіцянка, НЕ міняється ні на символ",
                  size=14.5, bold=True, color=INK))
    p.append(text(cx, hy + 52, "stack_new   stack_push   stack_pop   stack_size   stack_free",
                  size=12.5, color=INK))
    p.append(text(cx, hy + 76, "typedef struct Stack Stack;   (тип є, будова прихована)",
                  size=11.5, color=MUTED, italic=True))

    # три реалізації внизу (змінні)
    top = 360
    bw, bh = 250, 150
    gap = (W - 132 - 3 * bw) / 2
    xs = [66 + i * (bw + gap) for i in range(3)]
    impls = [
        ("#1  масив 64", POS,
         ["struct { int data[64];", "         size_t top; }", "",
          "стеля 64 елементи", "один malloc / один free"]),
        ("#2  динамічний масив", "#b8860b",
         ["struct { int *data;", "         size_t len, cap; }", "",
          "росте вдвічі, без стелі", "перевірка переповнення"]),
        ("#3  потокобезпечний", FIELD,
         ["struct { int data[64];", "         size_t top;", "         mtx_t lock; }", "",
          "замок на push / pop"]),
    ]
    for x, (title, col, lines) in zip(xs, impls):
        p.append(arrow(x + bw / 2, hy + hh + 2, x + bw / 2, top - 4, color=MUTED, sw=1.5))
        p.append(rect(x, top, bw, bh, fill=FILL, stroke=col, sw=2, rx=9))
        p.append(text(x + bw / 2, top + 24, title, size=13.5, bold=True, color=col))
        ly = top + 48
        for ln in lines:
            if ln:
                is_code = ("{" in ln or "}" in ln or "size_t" in ln or "int " in ln)
                p.append('<text x="%.1f" y="%.1f" font-family="monospace" '
                         'font-size="11" fill="%s" text-anchor="middle">%s</text>'
                         % (x + bw / 2, ly, INK if is_code else MUTED, esc(ln)))
            ly += 20

    p.append(text(cx, top + bh + 32,
                  "змінюється ЛИШЕ цей рівень — клієнт і заголовок ні",
                  size=13, bold=True, color=MUTED))

    render(os.path.join(IMG, 'opaque-swap.svg'), W, H, *p)


if __name__ == "__main__":
    fig_asymmetry()
    fig_one_interface_many()
    fig_kwic_two_ways()
    fig_opaque_swap()
    print("figures written to", IMG)
