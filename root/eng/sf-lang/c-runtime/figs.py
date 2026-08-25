# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# локальні відтінки понад палітру svgkit
GOLD = "#b8860b"   # «частково готове» / проміжний стан
VIO  = "#8a5fb0"   # додатковий акцент (скидання / окремий шлях)


# ── language-runtime: піраміда шарів під кодом користувача ─────────────────────
# Ідея: «гола» програма не гола — під нею завжди стоїть рантайм. Верхні шари
# спираються на нижні; найнижчий роздвоюється: ОС (ПК) дає опору, порт (МК) мусить.

def fig_language_runtime():
    W, H = 760, 360
    p = []
    cx = W / 2

    # шар 1 — ваш код (найвужчий, згори)
    y1, h = 56, 50
    w1 = 300
    p.append(rect(cx - w1 / 2, y1, w1, h, fill="#eef0f5", stroke=INK, sw=2))
    p.append(text(cx, y1 + 21, "ВАШ КОД", size=14, color=INK, bold=True))
    p.append(text(cx, y1 + 39, "setup() · loop() · main()", size=10, color=MUTED))

    # шар 2 — стандартна бібліотека
    y2 = y1 + h + 14
    w2 = 460
    p.append(rect(cx - w2 / 2, y2, w2, h, fill="#eef6ef", stroke=FIELD, sw=2))
    p.append(text(cx, y2 + 21, "Стандартна бібліотека (newlib / libc)", size=13, color=FIELD, bold=True))
    p.append(text(cx, y2 + 39, "printf · malloc · memcpy · math", size=10, color=MUTED))

    # шар 3 — роздвоєння: ОС (ПК) ліворуч, порт/фреймворк (МК) праворуч
    y3 = y2 + h + 14
    w3 = 300
    gap = 20
    lx = cx - gap / 2 - w3
    rx = cx + gap / 2
    p.append(rect(lx, y3, w3, h, fill="#e9eefb", stroke=NEG, sw=2))
    p.append(text(lx + w3 / 2, y3 + 21, "ОС / glibc (ПК)", size=13, color=NEG, bold=True))
    p.append(text(lx + w3 / 2, y3 + 39, "системні виклики — є", size=10, color=MUTED))
    p.append(rect(rx, y3, w3, h, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(rx + w3 / 2, y3 + 21, "Порт / фреймворк (МК)", size=13, color=POS, bold=True))
    p.append(text(rx + w3 / 2, y3 + 39, "_write · _sbrk — хтось мусить", size=10, color=MUTED))

    # шар 4 — залізо (найширший, унизу)
    y4 = y3 + h + 14
    w4 = 660
    p.append(rect(cx - w4 / 2, y4, w4, 46, fill="#e4e4e4", stroke=MUTED, sw=1.5))
    p.append(text(cx, y4 + 28, "Залізо (процесор · Flash · RAM · UART)", size=12, color=INK, bold=True))

    # стрілки опори (знизу вгору: кожен шар спирається на нижній)
    p.append(arrow(cx, y2, cx, y1 + h + 2, color=INK, sw=1.7))
    p.append(arrow(lx + w3 / 2, y3, lx + w3 / 2 + 30, y2 + h + 2, color=NEG, sw=1.6))
    p.append(arrow(rx + w3 / 2, y3, rx + w3 / 2 - 30, y2 + h + 2, color=POS, sw=1.6))
    p.append(arrow(lx + w3 / 2, y4, lx + w3 / 2, y3 + h + 2, color=INK, sw=1.5))
    p.append(arrow(rx + w3 / 2, y4, rx + w3 / 2, y3 + h + 2, color=INK, sw=1.5))

    render(os.path.join(OUT, "language-runtime.svg"), W, H, *p,
           title="«Гола» програма не гола: під нею завжди стоїть рантайм")


# ── crt0-deep: три дії crt0 як передумови + що зламається без кожної ───────────
# Ідея: кожен крок crt0 — необхідна умова, не ритуал; порядок строгий: спершу
# стек, тоді .data/.bss (інакше crt0 зруйнує власний стек).

def fig_crt0_deep():
    W, H = 760, 360
    p = []
    cx = W / 2

    # стрічка порядку згори: спершу стек → .data → .bss
    oy = 60
    p.append(text(cx, oy - 10, "Порядок строгий (згори вниз):", size=11, color=INK, bold=True))

    steps = [
        ("1. Вказівник стека (SP)",
         "ставить векторний reset ще ДО будь-якого виклику",
         "без нього: перший виклик функції валить машину",
         VIO, "#f2ecf8"),
        ("2. Копія .data: Flash → RAM",
         "початкові значення — у Flash, змінні живуть у RAM",
         "без неї: ініціалізований глобал = сміття",
         POS, "#fdecea"),
        ("3. Обнулення .bss",
         "стандарт C: нульовий глобал = 0 на старті",
         "без нього: нульовий глобал = сміття",
         FIELD, "#eef6ef"),
    ]
    bw, bh = 560, 74
    bx = cx - bw / 2
    y = oy + 6
    centers = []
    for title_s, ok_s, bad_s, col, fill in steps:
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=col, sw=1.8))
        p.append(text(bx + 16, y + 22, title_s, size=12, color=col, anchor="start", bold=True))
        p.append(text(bx + 16, y + 42, ok_s, size=10, color=INK, anchor="start"))
        p.append(text(bx + 16, y + 60, bad_s, size=10, color=POS, anchor="start", italic=True))
        centers.append(y + bh)
        y += bh + 20

    # стрілки послідовності між блоками
    for cyb in centers[:-1]:
        p.append(arrow(cx, cyb + 2, cx, cyb + 18, color=INK, sw=1.8))

    p.append(text(cx, H - 16,
                  "Спершу стек — інакше crt0 зруйнує власний стек, записуючи в RAM-діапазон .bss",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "crt0-deep.svg"), W, H, *p,
           title="crt0 зблизька: три передумови і що зламається без кожної")


# ── init-array: таблиця покажчиків на конструктори, crt0 обходить її ───────────
# Ідея: компілятор збирає покажчики на конструктори глобальних C++-об'єктів у
# .init_array; crt0 обходить таблицю й кличе кожен запис ДО main()/setup().

def fig_init_array():
    W, H = 760, 340
    p = []

    # ліворуч — джерело: глобальні об'єкти в коді
    src_x, src_y, src_w = 40, 70, 220
    p.append(text(src_x, src_y - 12, "Глобальні C++-об'єкти", size=11, color=INK, anchor="start", bold=True))
    objs = ["Sensor g_sensor(0x40);", "Logger g_log;", "Config g_cfg;"]
    oy = src_y
    obh = 40
    obj_centers = []
    for o in objs:
        p.append(fitbox(src_x, oy, src_w, obh, o, size=11, fill="#eef0f5", stroke=INK, sw=1.4))
        obj_centers.append(oy + obh / 2)
        oy += obh + 14
    p.append(text(src_x + src_w / 2, oy + 4, "компілятор збирає\nпокажчики на ctor()",
                  size=10, color=MUTED))

    # центр — таблиця .init_array (масив покажчиків)
    tab_x = 330
    tab_y = 64
    tab_w = 180
    rowh = 34
    p.append(text(tab_x + tab_w / 2, tab_y - 14, ".init_array", size=12, color=NEG, bold=True))
    p.append(rect(tab_x, tab_y, tab_w, rowh * 3 + 8, fill="#e9eefb", stroke=NEG, sw=2))
    rows = ["&ctor g_sensor", "&ctor g_log", "&ctor g_cfg"]
    row_centers = []
    ry = tab_y + 4
    for r in rows:
        p.append(rect(tab_x + 8, ry + 4, tab_w - 16, rowh - 8, fill=BG, stroke=NEG, sw=1.2))
        p.append(text(tab_x + tab_w / 2, ry + rowh / 2 + 4, r, size=10, color=INK))
        row_centers.append(ry + rowh / 2)
        ry += rowh
    p.append(text(tab_x + tab_w / 2, ry + 18, "таблиця покажчиків", size=10, color=MUTED))

    # стрілки: об'єкти → записи таблиці
    for sc, rc in zip(obj_centers, row_centers):
        p.append(arrow(src_x + src_w + 2, sc, tab_x - 2, rc, color=MUTED, sw=1.3))

    # праворуч — crt0 обходить і кличе кожен запис
    crt_x = 600
    crt_y = 110
    cb, cbw, cbh = textbox(crt_x + 60, crt_y, "crt0\nобходить →\nкличе ctor()",
                           size=12, bold=True, color=FIELD, fill="#eef6ef", stroke=FIELD, sw=1.8)
    # стрілки від кожного запису таблиці до блоку crt0
    for rc in row_centers:
        p.append(arrow(tab_x + tab_w + 2, rc, crt_x + 60 - cbw / 2 - 2, crt_y, color=FIELD, sw=1.3))
    p.append(cb)

    # підсумок: усе це ДО main()
    p.append(line(crt_x + 60, crt_y + cbh / 2, crt_x + 60, H - 56, color=FIELD, sw=1.6))
    p.append(arrow(crt_x + 60, H - 56, crt_x + 60, H - 40, color=FIELD, sw=1.7))
    done, dw, dh = textbox(crt_x + 60, H - 28, "до main() / setup()",
                           size=11, bold=True, color=INK, fill="#fff", stroke=INK, sw=1.4)
    p.append(done)

    render(os.path.join(OUT, "init-array.svg"), W, H, *p,
           title=".init_array: конструктори глобальних об'єктів до main()")


# ── syscall-stubs: дві доріжки printf→_write→UART і malloc→_sbrk→RAM ───────────
# Ідея: «слабкий» символ = навмисна заглушка; без порту printf мовчить,
# malloc=NULL; купа і стек ростуть назустріч.

def fig_syscall_stubs():
    W, H = 760, 360
    p = []

    def track(y, a, b, c, mid_label, tail):
        bw, bh, step = 150, 50, 50
        x = 60
        boxes = [a, b, c]
        cols = [INK, GOLD, INK]
        fills = [FILL, "#fff6e0", "#eef6ef"]
        edges = [None]
        for i, (lab, col, fill) in enumerate(zip(boxes, cols, fills)):
            p.append(fitbox(x, y - bh / 2, bw, bh, lab, size=11, fill=fill, stroke=col, sw=1.6, bold=True, color=col))
            if i > 0:
                prev_right = x - step           # правий край попереднього блоку
                p.append(arrow(prev_right + 2, y, x - 2, y, color=INK, sw=1.7))
            x += bw + step
        # підпис над середнім блоком («слабка дірка»)
        p.append(text(60 + bw + step + bw / 2, y - bh / 2 - 8, mid_label, size=9, color=GOLD))
        # хвіст-наслідок праворуч
        p.append(text(x - step + 6, y + bh / 2 + 16, tail, size=10, color=POS, anchor="start", italic=True))

    p.append(text(60, 70, "printf:", size=12, color=INK, anchor="start", bold=True))
    track(100, "printf\n(форматує)", "_write\n(слабкий)", "UART / Serial\n(фреймворк)",
          "«дірка» в newlib", "без порту: printf мовчить")

    p.append(text(60, 190, "malloc:", size=12, color=INK, anchor="start", bold=True))
    track(220, "malloc(n)", "_sbrk\n(слабкий)", "вільна RAM\n(.bss↔стек)",
          "«дірка» в newlib", "без порту: malloc → NULL")

    # нижня нота: купа і стек ростуть назустріч
    ny = 290
    p.append(rect(120, ny, 520, 40, fill="#f8f8f8", stroke=MUTED, sw=1.2))
    p.append(text(150, ny + 24, "купа →", size=11, color=POS, anchor="start", bold=True))
    p.append(text(610, ny + 24, "← стек", size=11, color=NEG, anchor="end", bold=True))
    p.append(arrow(205, ny + 20, 360, ny + 20, color=POS, sw=1.5))
    p.append(arrow(555, ny + 20, 400, ny + 20, color=NEG, sw=1.5))

    p.append(text(W / 2, H - 14,
                  "«Слабкий» символ — навмисна заглушка; порт вписує реальне залізо. Купа і стек ростуть назустріч.",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "syscall-stubs.svg"), W, H, *p,
           title="Syscall-стаби: половину libc дописує порт")


# ── data-life: трасування 4 глобалів крізь стадії старту (сітка станів) ────────
# Ідея: візуальний відповідник текстової таблиці — кожна змінна від «сміття»
# до «готово»; усе гарантовано лише після init_array.

def fig_data_life():
    W, H = 820, 340
    p = []

    cols = ["reset", "копія\n.data", "обнул.\n.bss", "init_\narray", "main() /\nsetup()"]
    rows = [
        ("g_baud  (.data)",      ["сміття", "115200", "115200", "115200", "готово"]),
        ("g_count (.bss)",       ["сміття", "—",      "0",      "0",      "готово"]),
        ("g_sensor (.data+ctor)", ["сміття", "частк.", "частк.", "ctor()", "готово"]),
        ("g_buf  (.bss)",        ["сміття", "—",      "нулі",   "нулі",   "готово"]),
    ]

    lab_w = 168
    x0 = 24
    cw = (W - x0 * 2 - lab_w) / len(cols)
    head_y = 60
    head_h = 40
    rowh = 50
    grid_x = x0 + lab_w

    # заголовки колонок (стадії)
    p.append(rect(x0, head_y, lab_w, head_h, fill="#f0f0f0", stroke=MUTED, sw=1.4))
    p.append(text(x0 + lab_w / 2, head_y + head_h / 2 + 4, "змінна", size=11, color=INK, bold=True))
    for j, c in enumerate(cols):
        cx = grid_x + j * cw
        p.append(rect(cx, head_y, cw, head_h, fill="#e9eefb", stroke=NEG, sw=1.3))
        p.append(mtext(cx + cw / 2, head_y + 16, c, size=10, color=NEG, bold=True))

    # значення кольором: сміття=POS, проміжне=GOLD, готове/значення=FIELD, «—»=MUTED
    def cell_color(v):
        if v in ("сміття",):
            return POS, "#fdecea"
        if v in ("—",):
            return MUTED, "#f8f8f8"
        if v in ("частк.",):
            return GOLD, "#fff6e0"
        return FIELD, "#eef6ef"

    y = head_y + head_h
    for name, vals in rows:
        p.append(rect(x0, y, lab_w, rowh, fill="#f8f8f8", stroke=MUTED, sw=1.2))
        p.append(text(x0 + 10, y + rowh / 2 + 4, name, size=10, color=INK, anchor="start", bold=True))
        for j, v in enumerate(vals):
            cx = grid_x + j * cw
            col, fill = cell_color(v)
            p.append(rect(cx + 2, y + 4, cw - 4, rowh - 8, fill=fill, stroke=col, sw=1.1))
            p.append(text(cx + cw / 2, y + rowh / 2 + 4, v, size=10, color=col, bold=True))
        y += rowh

    p.append(text(W / 2, y + 26,
                  "Лише після init_array всі дані гарантовано готові для setup() / main()",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "data-life.svg"), W, H, *p,
           title="Доля глобальних даних: від reset до main()")


# ── freestanding: той самий C-код на двох фундаментах ─────────────────────────
# Ідея: один і той самий C стоїть на двох різних фундаментах; hosted дає ОС,
# freestanding гарантує лише мову — решту мусить принести порт. __STDC_HOSTED__.

def fig_freestanding():
    W, H = 760, 360
    p = []
    half = W / 2

    # спільний код-камінь згори по центру
    code, cw, ch = textbox(half, 64, "той самий C-код",
                           size=13, bold=True, color=INK, fill="#fff6e0", stroke=GOLD, sw=2, pad=16)
    p.append(code)

    panels = [
        (40, "HOSTED — ПК", NEG, "#e9eefb",
         ["ОС готова", "повна glibc", "main() — вхід", "усе є до main()"],
         "__STDC_HOSTED__ = 1"),
        (half + 20, "FREESTANDING — МК", POS, "#fdecea",
         ["ОС немає", "гарантована лише мова", "newlib + стаби + crt0", "приносить порт/фреймворк"],
         "__STDC_HOSTED__ = 0"),
    ]
    pw = half - 60
    ptop = 130
    pbot = H - 70
    for px, head, col, fill, items, macro in panels:
        cxp = px + pw / 2
        # стрілка від спільного коду вниз до панелі
        p.append(arrow(half + (-1 if px < half else 1) * cw * 0.18, 64 + ch / 2,
                       cxp, ptop - 4, color=col, sw=1.6))
        p.append(rect(px, ptop, pw, pbot - ptop, fill=fill, stroke=col, sw=2))
        p.append(text(cxp, ptop + 24, head, size=13, color=col, bold=True))
        iy = ptop + 50
        for it in items:
            p.append(text(cxp, iy, it, size=11, color=INK))
            iy += 23
        # фундамент-плита
        p.append(rect(px + 10, pbot - 32, pw - 20, 26, fill=BG, stroke=col, sw=1.3))
        p.append(text(cxp, pbot - 14, macro, size=11, color=col, bold=True))

    p.append(text(half, H - 16,
                  "Один і той самий C стоїть на двох різних фундаментах",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "freestanding.svg"), W, H, *p,
           title="Hosted проти freestanding: два фундаменти під тим самим C")


if __name__ == "__main__":
    fig_language_runtime()
    fig_crt0_deep()
    fig_init_array()
    fig_syscall_stubs()
    fig_data_life()
    fig_freestanding()
    print("OK: figures written to", OUT)
