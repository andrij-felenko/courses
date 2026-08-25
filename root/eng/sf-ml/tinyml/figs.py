# -*- coding: utf-8 -*-
"""Фігури для детальної статті TinyML. Запуск із цієї теки: python figs.py
Виводить SVG у ./img/. Імпортує спільний svgkit зі scripts/ (чотири рівні вгору)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

FIT_FILL = "#e8f6ee"   # світло-зелений — влазить
OVR_FILL = "#fdecea"   # світло-червоний — переповнено
AMBER    = "#b8860b"   # застереження текстом


# ── Фігура 1: чотири бюджети мікроконтролера ────────────────────────────────
def fig_four_budgets():
    W, H = 900, 410
    TRACK_X, TRACK_W = 320, 320
    BUDGET_X = TRACK_X + TRACK_W          # 640 — межа місткости чипа
    frags = []

    rows = [
        ("Флеш (ПЗП)", "тримає ваги моделі",        0.85, False, "тісно, та влазить"),
        ("ОЗП",        "тримає активації (пік)",     1.35, True,  "не влазить!"),
        ("Такти",      "множення-накопичення (MAC)", 0.92, False, "ледь устигає"),
        ("Енергія",    "мВт, час автономности",      0.60, False, "з запасом"),
    ]
    ys = [95, 175, 255, 335]

    # межа місткости чипа — одна вертикальна пунктирна лінія на всі рядки
    frags.append(line(BUDGET_X, 60, BUDGET_X, 372, color=MUTED, sw=1.5, dash="5 4"))
    frags.append(text(BUDGET_X, 52, "місткість чипа", size=12, color=MUTED))

    for (name, hold, demand, over, note), cy in zip(rows, ys):
        if over:  # підсвітити рядок ОЗП
            frags.append(rect(18, cy - 34, W - 36, 68, fill="#fff5f5", stroke="none", sw=0, rx=8))
        # ліва підпис-рамка
        frags.append(fitbox(25, cy - 30, 280, 60, name + "\n" + hold,
                            size=15, fill=FILL, stroke=LINE))
        # трек = бюджет (порожня місткість)
        frags.append(rect(TRACK_X, cy - 16, TRACK_W, 32, fill=BG, stroke=MUTED, sw=1.4))
        # смуга попиту
        bw = demand * TRACK_W
        fill, st = (OVR_FILL, POS) if demand > 1.0 else (FIT_FILL, FIELD)
        frags.append(rect(TRACK_X, cy - 14, bw, 28, fill=fill, stroke=st, sw=2))
        # ратіо в смузі
        frags.append(text(TRACK_X + min(bw, TRACK_W) / 2, cy + 5,
                          ("%.2f× бюджету" % demand), size=12,
                          color=(POS if over else INK)))
        # нотатка праворуч
        frags.append(text(805, cy + 5, note, size=13,
                          color=(POS if over else FIELD), bold=over))

    render(os.path.join(IMG, 'four-budgets.svg'), W, H, *frags,
           title="Чотири різні бюджети — переповнюється зазвичай ОЗП")


# ── Фігура 2: час життя тензорів і пік активацій = розмір арени ──────────────
def fig_tensor_lifetimes():
    W, H = 820, 470
    base = 400          # y для «пам'ять = 0»
    SCALE = 300.0 / 14000.0   # px на байт
    frags = []

    def h(b):
        return b * SCALE

    # осі
    frags.append(arrow(95, base, 95, 118))          # вгору — пам'ять
    frags.append(text(95, 108, "пам'ять (Б)", size=12, color=MUTED))
    frags.append(arrow(110, base, 740, base))       # праворуч — час
    frags.append(text(726, base + 20, "час →", size=12, color=MUTED))

    # гридлайни кроків обчислення
    for gx, lbl in [(270, "порах. t1"), (430, "порах. t2"), (590, "порах. t3")]:
        frags.append(line(gx, 120, gx, base, color=MUTED, sw=1.0, dash="4 4"))
        frags.append(text(gx, base + 20, lbl, size=12, color=MUTED))

    # тензори: (x1, x2, розмір_байтів, зверху_від_offset_байтів, підпис, підпис_усередині)
    def bar(x1, x2, size_b, off_b, label, inside=True):
        y2 = base - h(off_b)
        y1 = base - h(off_b + size_b)
        frags.append(rect(x1, y1, x2 - x1, y2 - y1, fill=FILL, stroke=LINE, sw=1.6))
        if inside:
            frags.append(fitbox(x1 + 4, y1 + (y2 - y1) / 2 - 15, x2 - x1 - 8, 30, label,
                                size=13, fill="none", stroke="none"))
        else:
            frags.append(text((x1 + x2) / 2, y1 - 8, label, size=12, color=INK))

    bar(120, 270, 4000, 0,    "x0 · 4000 Б")     # живе [t0..t1]
    bar(270, 430, 8000, 4000, "t1 · 8000 Б")     # стоїть над x0 у миті піку
    bar(430, 590, 2000, 0,    "t2 · 2000 Б")     # перевикор. звільнене низом
    bar(590, 720,  500, 2000, "t3 · 500 Б", inside=False)

    # лінія піку = висота арени
    peak_y = base - h(12000)
    frags.append(line(110, peak_y, 725, peak_y, color=POS, sw=1.8, dash="7 4"))
    frags.append(text(360, peak_y - 9, "пік = розмір арени = 12000 Б", size=13, color=POS, bold=True))

    # дужка «арена» праворуч
    bx = 750
    frags.append(line(bx, peak_y, bx, base, color=FIELD, sw=2))
    frags.append(line(bx - 6, peak_y, bx + 6, peak_y, color=FIELD, sw=2))
    frags.append(line(bx - 6, base, bx + 6, base, color=FIELD, sw=2))
    frags.append(text(bx + 30, (peak_y + base) / 2, "арена", size=13, color=FIELD, bold=True))

    render(os.path.join(IMG, 'tensor-lifetimes.svg'), W, H, *frags,
           title="Потрібна ОЗП — це пік одночасно живих тензорів, а не їх сума")


# ── Фігура 3: устрій рушія виводу (флеш ↔ рушій ↔ арена) ─────────────────────
def fig_interpreter_anatomy():
    W, H = 920, 470
    frags = []

    # Сенсор
    frags.append(fitbox(30, 200, 110, 70, "Сенсор\nзвук / кадр", size=13,
                        fill=FILL, stroke=LINE))

    # ФЛЕШ (тільки читання)
    frags.append(rect(175, 55, 330, 150, fill="#f0f4fb", stroke=NEG, sw=1.6))
    frags.append(text(340, 78, "ФЛЕШ (ПЗП) · тільки читання", size=13, color=NEG, bold=True))
    frags.append(fitbox(190, 95, 150, 95, "Модель (flatbuffer):\nграф операцій\n+ 8-бітні ваги",
                        size=12, fill=BG, stroke=LINE))
    frags.append(fitbox(350, 95, 140, 95, "Ядра операцій:\nзгортка · +\n· активація",
                        size=12, fill=BG, stroke=LINE))

    # РУШІЙ
    frags.append(fitbox(560, 185, 160, 100, "Рушій виводу\nіде графом\n→ кличе ядро",
                        size=13, fill=FILL, stroke=INK, sw=2))

    # ОЗП / Арена
    frags.append(rect(175, 265, 330, 155, fill="#f0f9f2", stroke=FIELD, sw=1.6))
    frags.append(text(340, 288, "ОЗП · робоча пам'ять", size=13, color=FIELD, bold=True))
    frags.append(fitbox(190, 300, 300, 70,
                        "Арена активацій: єдиний буфер під усі проміжні\nтензори, перевикористаний за їхніми часами життя",
                        size=12, fill=BG, stroke=LINE))
    frags.append(fitbox(190, 378, 300, 34, "Службовий стан рушія", size=12, fill=BG, stroke=LINE))

    # Результат
    frags.append(fitbox(770, 200, 120, 70, "Результат\nклас · ✓ / ✗", size=13,
                        fill=FILL, stroke=LINE))

    # стрілки
    frags.append(arrow(140, 250, 188, 330))                      # сенсор → арена
    frags.append(text(150, 300, "вхід", size=11, color=MUTED, anchor="start"))
    frags.append(arrow(505, 150, 558, 210))                      # флеш → рушій
    frags.append(text(512, 178, "граф · ваги · ядра", size=11, color=MUTED, anchor="start"))
    # арена ↔ рушій: дві НЕ перехресні смуги (верхня — вхідні, нижня — вихідні),
    # підписи впритул до кожної власної лінії й перед лівим краєм рушія (x<558) —
    # так вони не заходять ні в рамку рушія, ні в шлях сусідньої стрілки
    frags.append(arrow(505, 300, 558, 258))                      # арена → рушій (вхідні тензори)
    frags.append(text(555, 246, "вхідні тензори", size=11, color=MUTED, anchor="end"))
    frags.append(arrow(558, 302, 505, 348))                      # рушій → арена (вихідні тензори)
    frags.append(text(555, 364, "вихідні тензори", size=11, color=MUTED, anchor="end"))
    frags.append(arrow(722, 235, 768, 235))                      # рушій → результат
    frags.append(text(745, 222, "вихід", size=11, color=MUTED))

    render(os.path.join(IMG, 'interpreter-anatomy.svg'), W, H, *frags,
           title="Рушій виводу: модель у флеші, активації в арені ОЗП")


# ── Фігура 4: каскад «завжди напоготові» ────────────────────────────────────
def fig_cascade():
    W, H = 920, 420
    frags = []

    # вхід — звук завжди
    frags.append(fitbox(25, 120, 95, 70, "Звук\nзавжди", size=13, fill=FILL, stroke=LINE))

    stages = [
        (230, "Крихітна модель\n(кілька КБ)",  "завжди · мкВт",       FIELD, "#f0f9f2"),
        (500, "Більша модель\n(точніша)",       "зрідка · мВт",        AMBER, "#fdf6e3"),
        (770, "Головний CPU\nчи хмара",         "дуже зрідка · сотні мВт", POS, "#fdecea"),
    ]
    bw, bh, by = 190, 110, 100
    cy = by + bh / 2
    for cx, name, tag, col, bg in stages:
        frags.append(rect(cx - bw / 2, by, bw, bh, fill=bg, stroke=col, sw=1.8))
        frags.append(fitbox(cx - bw / 2 + 8, by + 18, bw - 16, 74, name, size=14,
                            fill="none", stroke="none"))
        frags.append(fitbox(cx - bw / 2 + 10, by + bh + 14, bw - 20, 34, tag,
                            size=13, fill=BG, stroke=col, color=col))

    # стрілки з умовами спрацювання (короткі підписи в проміжках)
    frags.append(arrow(120, cy, 230 - bw / 2 - 4, cy))                # вхід → s1
    frags.append(arrow(230 + bw / 2, cy, 500 - bw / 2, cy))           # s1 → s2
    frags.append(text(365, cy - 12, "«схоже?»", size=12, color=MUTED))
    frags.append(arrow(500 + bw / 2, cy, 770 - bw / 2, cy))           # s2 → s3
    frags.append(text(635, cy - 12, "«точно?»", size=12, color=MUTED))

    # підсумок
    frags.append(fitbox(120, 300, 680, 66,
                        "Помнож потужність кожної стадії на частку часу, коли вона активна — і середнє\nтримається в мікроватах, хоч найдорожча стадія й коштує на порядки більше.",
                        size=13, fill="#f0f9f2", stroke=FIELD))

    render(os.path.join(IMG, 'cascade.svg'), W, H, *frags,
           title="Каскад: дешева стадія працює завжди, дорога — зрідка")


# ── Фігура 5: шість об'єктів TFLM і один виклик (карта API) ──────────────────
def fig_api_wiring():
    W, H = 880, 690
    BX, BW, BH = 210, 470, 74
    ys = [66, 168, 270, 372, 474, 576]
    frags = []

    boxes = [
        ("const unsigned char g_model[]",
         "модель-flatbuffer як байти (xxd -i): граф + int8-ваги"),
        ("MicroMutableOpResolver<N> resolver",
         "resolver.Add…() — лише ті ядра, що є в моделі"),
        ("alignas(16) uint8_t tensor_arena[kArenaSize]",
         "єдиний робочий буфер під усі тензори"),
        ("MicroInterpreter interp(model, resolver, arena, size)",
         "зшиває модель, ядра й арену докупи"),
        ("interp.AllocateTensors()",
         "розмічає арену; тут падає мала арена / брак ядра"),
        ("interp.input(0) → interp.Invoke() → interp.output(0)",
         "наповни int8-вхід · прожени граф · читай int8-вихід"),
    ]

    for i, ((code, role), y) in enumerate(zip(boxes, ys)):
        cy = y + BH / 2
        # стрілка від попередньої коробки
        if i > 0:
            frags.append(arrow(BX + BW / 2, ys[i - 1] + BH, BX + BW / 2, y))
        # номер кроку
        frags.append(circle(178, cy, 17, fill=FILL, stroke=INK, sw=1.8))
        frags.append(text(178, cy + 5, str(i + 1), size=15, bold=True))
        # коробка з двома рядками
        frags.append(fitbox(BX, y, BW, BH, code + "\n" + role, size=14,
                            fill=FILL, stroke=INK, sw=1.8))

    # праві теги пам'яті
    frags.append(fitbox(702, ys[0] + 8, 158, 58, "у ФЛЕШі\n(тільки читання)",
                        size=13, fill="#f0f4fb", stroke=NEG, color=NEG))
    frags.append(fitbox(702, ys[2] + 8, 158, 58, "в ОЗП\n(читання-запис)",
                        size=13, fill="#f0f9f2", stroke=FIELD, color=FIELD))
    # стрілки-звʼязки тегів
    frags.append(line(680, ys[0] + BH / 2, 702, ys[0] + BH / 2, color=NEG, sw=1.4, dash="4 3"))
    frags.append(line(680, ys[2] + BH / 2, 702, ys[2] + BH / 2, color=FIELD, sw=1.4, dash="4 3"))

    render(os.path.join(IMG, 'api-wiring.svg'), W, H, *frags,
           title="Контракт TFLM: шість обʼєктів і один виклик Invoke()")


# ── Фігура 6: підбір розміру арени (arena_used_bytes vs kArenaSize) ───────────
def fig_api_arena_sizing():
    W, H = 940, 400
    KB = 11.0            # px на кілобайт
    X0 = 300
    frags = []

    # ── Рядок А: арена з запасом → OK ──────────────────────────────────
    yA = 100
    frags.append(fitbox(28, yA - 8, 250, 58, "kArenaSize = 40 КБ\n(поставили з запасом)",
                        size=13, fill=BG, stroke=MUTED))
    frags.append(rect(X0, yA, 40 * KB, 40, fill=BG, stroke=MUTED, sw=1.4))      # весь бюджет
    used = 28 * KB
    frags.append(rect(X0, yA + 2, used, 36, fill=FIT_FILL, stroke=FIELD, sw=2)) # використано
    frags.append(fitbox(X0 + 4, yA + 6, used - 8, 28, "arena_used_bytes() = 28 КБ",
                        size=12, fill="none", stroke="none"))
    frags.append(text(X0 + used + (40 * KB - used) / 2, yA + 24, "12 КБ запас",
                      size=12, color=MUTED))
    frags.append(fitbox(760, yA - 2, 160, 44, "AllocateTensors()\n→ kTfLiteOk",
                        size=13, fill="#f0f9f2", stroke=FIELD, color=FIELD, bold=True))

    # ── Рядок Б: арена замала → Error ──────────────────────────────────
    yB = 220
    frags.append(fitbox(28, yB - 8, 250, 58, "kArenaSize = 20 КБ\n(замала)",
                        size=13, fill=BG, stroke=MUTED))
    frags.append(rect(X0, yB, 20 * KB, 40, fill=BG, stroke=MUTED, sw=1.4))       # маленький бюджет
    need = 28 * KB
    frags.append(rect(X0, yB + 2, need, 36, fill=OVR_FILL, stroke=POS, sw=2))    # треба більше
    wall = X0 + 20 * KB
    frags.append(line(wall, yB - 6, wall, yB + 46, color=INK, sw=2.2))           # стінка буфера
    frags.append(text(wall, yB - 12, "кінець буфера", size=11, color=INK))
    frags.append(text((wall + X0 + need) / 2, yB + 24, "бракує 8 КБ", size=12,
                      color=POS, bold=True))
    frags.append(fitbox(760, yB - 2, 160, 44, "AllocateTensors()\n→ kTfLiteError",
                        size=13, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # підсумковий рецеп
    frags.append(fitbox(120, 320, 700, 52,
                        "Підбір: постав арену з запасом → AllocateTensors() → звузь kArenaSize\nдо arena_used_bytes() плюс невеликий резерв.",
                        size=13, fill="#f0f9f2", stroke=FIELD))

    render(os.path.join(IMG, 'api-arena-sizing.svg'), W, H, *frags,
           title="Розмір арени: замала — AllocateTensors() повертає помилку")


# ── Фігура 7 (вставка proj): мапа арени для прикладу з пропущеним зв'язком ────
def fig_arena_skip():
    W, H = 880, 480
    ox, base, top = 150, 420, 95          # початок осі часу; y офсета 0; y офсета 14000
    STEP = 118
    PEAK = 14000
    sy = (base - top) / PEAK              # px на байт

    def X(step): return ox + step * STEP
    def Y(off):  return base - off * sy

    frags = []
    # осі
    frags.append(arrow(ox, base, ox, top - 14))
    frags.append(text(ox, top - 22, "байти арени", size=12, color=MUTED))
    frags.append(arrow(ox, base, X(5) + 22, base))
    frags.append(text(X(5) + 28, base + 4, "крок →", size=12, color=MUTED, anchor="start"))

    # позначки офсетів
    for off in (0, 4000, 8000, 12000, 14000):
        yy = Y(off)
        frags.append(line(ox - 5, yy, ox, yy, color=MUTED, sw=1.2))
        frags.append(text(ox - 10, yy + 4, str(off), size=11, color=MUTED, anchor="end"))
    # позначки кроків
    for s in range(6):
        frags.append(line(X(s), base, X(s), base + 5, color=MUTED, sw=1.2))
        frags.append(text(X(s), base + 20, str(s), size=11, color=MUTED))

    def block(s0, s1, o0, o1, label, fill, st, inside=True):
        xa, xb = X(s0), X(s1)
        ya, yb = Y(o1), Y(o0)
        frags.append(rect(xa, ya, xb - xa, yb - ya, fill=fill, stroke=st, sw=1.8))
        if inside:
            frags.append(text((xa + xb) / 2, (ya + yb) / 2 + 4, label, size=12, color=INK))
        else:
            frags.append(text((xa + xb) / 2, ya - 6, label, size=11, color=INK))

    block(0, 4, 0, 4000, "x0 · 4000 Б  (живе весь час — пропущений зв'язок)", "#eaf0fd", NEG)
    block(1, 2, 4000, 12000, "t1 · 8000 Б", FIT_FILL, FIELD)
    block(2, 3, 12000, 14000, "t2 · 2000 Б", FIT_FILL, FIELD)
    block(3, 4, 4000, 4500, "t3 · 500 Б", "#e8f6ee", FIELD, inside=False)
    block(4, 5, 4500, 9000, "t4 · 4500 Б", "#fdf6e3", AMBER)

    # лінія піку = розмір арени
    yp = Y(PEAK)
    frags.append(line(ox, yp, X(5), yp, color=POS, sw=1.8, dash="7 4"))
    frags.append(text(X(5), yp - 8, "пік = арена = 14000 Б", size=12, color=POS,
                      bold=True, anchor="end"))
    # мить піку — вертикаль по межі кроку 2
    frags.append(line(X(2), yp, X(2), base, color=POS, sw=1.1, dash="3 3"))
    frags.append(text(X(2), base + 40, "пік (крок 2): 3 живі", size=11, color=POS))

    render(os.path.join(IMG, 'arena-skip.svg'), W, H, *frags,
           title="Мапа арени: жадібний first-fit влучає в пік 14000")


# ── Фігура 8 (вставка proj): фрагментація — порядок вирішує (10 проти 8) ──────
def fig_arena_fragment():
    W, H = 900, 450
    base = 385
    sy = 26.0                              # px на байт (розміри тут дрібні)
    SX = 52                                # px на крок

    def panel(origin, title, blocks, arena_off, waste=None, peak=None):
        f = [text(origin + 135, 66, title, size=14, color=INK, bold=True)]

        def X(s): return origin + s * SX
        def Y(o): return base - o * sy

        f.append(arrow(origin, base, origin, Y(arena_off) - 14))
        f.append(text(origin, Y(arena_off) - 22, "байти", size=11, color=MUTED))
        f.append(arrow(origin, base, X(5) + 16, base))
        f.append(text(X(5) + 20, base + 4, "крок →", size=11, color=MUTED, anchor="start"))
        for s in range(6):
            f.append(text(X(s), base + 18, str(s), size=10, color=MUTED))

        if waste:
            s0, s1, o0, o1 = waste
            f.append(rect(X(s0), Y(o1), X(s1) - X(s0), Y(o0) - Y(o1),
                          fill=OVR_FILL, stroke=POS, sw=1.2, rx=3))
            f.append(text((X(s0) + X(s1)) / 2, (Y(o0) + Y(o1)) / 2 - 3, "2 Б вільні —",
                          size=10, color=POS))
            f.append(text((X(s0) + X(s1)) / 2, (Y(o0) + Y(o1)) / 2 + 11, "D не влазить",
                          size=10, color=POS))

        for s0, s1, o0, o1, lab, fill, st in blocks:
            f.append(rect(X(s0), Y(o1), X(s1) - X(s0), Y(o0) - Y(o1),
                          fill=fill, stroke=st, sw=1.6, rx=3))
            f.append(text((X(s0) + X(s1)) / 2, (Y(o0) + Y(o1)) / 2 + 4, lab, size=12, color=INK))

        if peak is not None:
            f.append(line(origin, Y(peak), X(5), Y(peak), color=MUTED, sw=1.2, dash="4 3"))
            f.append(text(X(5) + 4, Y(peak) + 4, "пік 8", size=10, color=MUTED, anchor="start"))

        f.append(line(origin, Y(arena_off), X(5), Y(arena_off), color=POS, sw=1.6, dash="6 3"))
        return f

    GRN, BLU, AMB = "#e8f6ee", "#eaf0fd", "#fdf6e3"
    left = panel(60, "за народженням → 10", [
        (0, 2, 0, 2, "A", GRN, FIELD),
        (1, 3, 2, 4, "B", BLU, NEG),
        (2, 4, 4, 6, "C", GRN, FIELD),
        (3, 5, 6, 10, "D", AMB, AMBER),
    ], arena_off=10, waste=(3, 5, 0, 2), peak=8)
    left.append(text(60 + 135, 96, "арена = 10 Б", size=12, color=POS, bold=True))

    right = panel(500, "за спаданням розміру (як TFLM) → 8", [
        (3, 5, 0, 4, "D", AMB, AMBER),
        (0, 2, 0, 2, "A", GRN, FIELD),
        (1, 3, 4, 6, "B", BLU, NEG),
        (2, 4, 6, 8, "C", GRN, FIELD),
    ], arena_off=8)
    right.append(text(500 + 135, 150, "арена = 8 Б = пік", size=12, color=FIELD, bold=True))

    legend = text(W / 2, base + 44, "розміри: A, B, C = 2 Б · D = 4 Б", size=11, color=MUTED)

    render(os.path.join(IMG, 'arena-fragment.svg'), W, H, *left, *right, legend,
           title="Той самий жадібний — різний порядок: фрагментація чи впритул")


# ── Фігура 9 (вставка hist): збіг трьох ліній → названа галузь ────────────────
def fig_convergence():
    W, H = 940, 470
    frags = []

    SX, SW, SH = 40, 250, 90
    sources = [
        (64,  "Застосунок: «завжди слухаю»\nслово-пробудження\nChen 2014 · Hey Siri 2015",
              FIELD, "#f0f9f2"),
        (182, "Метод + залізо\nint8-квантування →\nдешеве ціле множення · МК ~1 мВт",
              NEG, "#f0f4fb"),
        (300, "Рушій\nтлумач без malloc і ОС,\nу кілобайтах · TFLite Micro 2019",
              AMBER, "#fdf6e3"),
    ]

    CX, CW, CH, CY = 590, 320, 140, 175
    entry = [CY + 30, CY + CH / 2, CY + CH - 30]   # входи стрілок на лівій межі центру

    frags.append(text(750, 150, "збіг наприкінці 2010-х", size=12, color=MUTED))

    for (y, txt, col, bg), ey in zip(sources, entry):
        cy = y + SH / 2
        frags.append(fitbox(SX, y, SW, SH, txt, size=13, fill=bg, stroke=col, sw=1.8))
        frags.append(arrow(SX + SW, cy, CX, ey, color=col, sw=2.0))

    frags.append(rect(CX, CY, CW, CH, fill="#eef2f7", stroke=INK, sw=2.4))
    frags.append(fitbox(CX + 14, CY + 16, CW - 28, CH - 32,
                        "TinyML — названа галузь\n2018 · есе Вордена\n2019 · книга + tinyML Summit",
                        size=15, fill="none", stroke="none"))

    frags.append(fitbox(40, 408, 860, 48,
                        "Жодної лінії окремо не досить — галузь виникла аж коли всі три доспіли\nводночас, і хтось назвав цей збіг.",
                        size=13, fill="#f0f9f2", stroke=FIELD))

    render(os.path.join(IMG, 'convergence.svg'), W, H, *frags,
           title="Збіг трьох ліній: чому TinyML склався саме на межі 2018–2019")


if __name__ == '__main__':
    fig_four_budgets()
    fig_tensor_lifetimes()
    fig_interpreter_anatomy()
    fig_cascade()
    fig_api_wiring()
    fig_api_arena_sizing()
    fig_arena_skip()
    fig_arena_fragment()
    fig_convergence()
    print("OK: 9 фігур у ./img/")
