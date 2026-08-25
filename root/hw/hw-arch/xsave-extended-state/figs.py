# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Світлі заливки під усталений вигляд рамок
F_BLUE = "#f3f5fd"
F_RED  = "#fdf4f4"
F_GRN  = "#eef7ee"
F_GLD  = "#fff8e8"
F_GREY = "#f4f6f8"
GOLD_LINE = "#b8860b"


# ── 1. xsave-evolution: зростання обсягу стану процесора ──────────────────────
def fig_xsave_evolution():
    W, H = 760, 360
    p = [text(W / 2, 24, "Еволюція обсягу стану процесора в архітектурі x86", size=15, bold=True)]
    p.append(text(W / 2, 42, "Зростання регістрового контексту від 108 байтів до понад 10 кілобайтів",
                  size=10.5, color=MUTED, italic=True))

    steps = [
        ("FSAVE (1980)", "108 Б", "8087 / 80386\nx87 FPU стек\n(8 x 80-біт)", F_GREY, LINE, 80),
        ("FXSAVE (1999)", "512 Б", "Pentium III / x86-64\nx87 + SSE\n(XMM0-15 + MXCSR)", F_BLUE, NEG, 100),
        ("XSAVE AVX (2011)", "832 Б", "Sandy Bridge\nAVX (YMM_H)\n+ заголовок 64 Б", F_GRN, FIELD, 125),
        ("AVX-512 (2016)", "~2.7 КБ", "Skylake-SP\nZMM + Opmask k0-7\n+ Hi16_ZMM", F_GLD, GOLD_LINE, 160),
        ("AMX (2023)", ">10 КБ", "Sapphire Rapids\nTilecfg + 8 КБ TMM\nдинамічний стан", F_RED, POS, 210),
    ]

    x_start = 45
    spacing = 138
    base_y = 285

    for i, (name, sz, desc, fill, stroke, bar_h) in enumerate(steps):
        cx = x_start + i * spacing + 50
        bx = cx - 48
        by = base_y - bar_h

        # Стовпчик
        p.append(rect(bx, by, 96, bar_h, fill=fill, stroke=stroke, sw=1.8, rx=4))
        # Розмір над стовпчиком
        p.append(text(cx, by - 8, sz, size=12, bold=True, color=stroke))
        # Назва покоління
        p.append(text(cx, base_y + 16, name, size=11, bold=True))
        # Опис під стовпчиком
        lines = desc.split("\n")
        for li, line_txt in enumerate(lines):
            p.append(text(cx, base_y + 32 + li * 13, line_txt, size=9.5, color=MUTED))

    # Вісь знизу
    p.append(line(30, base_y, 730, base_y, color=LINE, sw=1.5))

    render(os.path.join(OUT, "xsave-evolution.svg"), W, H, *p)


# ── 2. xsave-frame-layout: розкладка пам'яті кадру XSAVE ──────────────────────
def fig_xsave_frame_layout():
    W, H = 760, 440
    p = [text(W / 2, 24, "Структура кадру збереження стану XSAVE у пам'яті", size=15, bold=True)]
    p.append(text(W / 2, 42, "Вирівнювання на 64 байти: застаріла область, заголовок стану та розширена зона",
                  size=10.5, color=MUTED, italic=True))

    lx, w = 60, 640

    # 1. Legacy Region (512B)
    y1 = 65
    h1 = 105
    p.append(rect(lx, y1, w, h1, fill=F_BLUE, stroke=NEG, sw=1.8))
    p.append(text(lx + 15, y1 + 22, "Legacy Region (байти 0 .. 511, розмір 512 Б)", size=12, bold=True, color=NEG, anchor="start"))
    p.append(text(lx + 15, y1 + 38, "Повна сумісність із форматом FXSAVE", size=9.5, color=MUTED, italic=True, anchor="start"))

    # Внутрішні блоки Legacy Region
    p.append(rect(lx + 15, y1 + 48, 160, 45, fill=BG, stroke=NEG, sw=1.2))
    p.append(text(lx + 95, y1 + 66, "x87 FPU стан (160 Б)", size=10, bold=True))
    p.append(text(lx + 95, y1 + 82, "FCW, FSW, FTW, ST0-ST7", size=9, color=MUTED))

    p.append(rect(lx + 185, y1 + 48, 200, 45, fill=BG, stroke=NEG, sw=1.2))
    p.append(text(lx + 285, y1 + 66, "SSE стан: XMM0-15 (256 Б)", size=10, bold=True))
    p.append(text(lx + 285, y1 + 82, "16 регістрів по 128 бітів", size=9, color=MUTED))

    p.append(rect(lx + 395, y1 + 48, 110, 45, fill=BG, stroke=NEG, sw=1.2))
    p.append(text(lx + 450, y1 + 66, "MXCSR (32 Б)", size=10, bold=True))
    p.append(text(lx + 450, y1 + 82, "керування SSE", size=9, color=MUTED))

    p.append(rect(lx + 515, y1 + 48, 110, 45, fill=F_GREY, stroke=LINE, sw=1.0))
    p.append(text(lx + 570, y1 + 66, "Резерв (64 Б)", size=9.5, color=MUTED))
    p.append(text(lx + 570, y1 + 82, "заповнено 0", size=9, color=MUTED))

    # 2. XSAVE Header (64B)
    y2 = 180
    h2 = 95
    p.append(rect(lx, y2, w, h2, fill=F_GLD, stroke=GOLD_LINE, sw=1.8))
    p.append(text(lx + 15, y2 + 20, "XSAVE Header (байти 512 .. 575, розмір 64 Б)", size=12, bold=True, color=GOLD_LINE, anchor="start"))
    p.append(text(lx + 15, y2 + 35, "Керує відновленням та форматом упаковки стану", size=9.5, color=MUTED, italic=True, anchor="start"))

    p.append(rect(lx + 15, y2 + 42, 195, 42, fill=BG, stroke=GOLD_LINE, sw=1.2))
    p.append(text(lx + 112, y2 + 60, "XSTATE_BV (8 байтів)", size=10, bold=True))
    p.append(text(lx + 112, y2 + 75, "маска активних компонентів", size=9, color=MUTED))

    p.append(rect(lx + 220, y2 + 42, 195, 42, fill=BG, stroke=GOLD_LINE, sw=1.2))
    p.append(text(lx + 317, y2 + 60, "XCOMP_BV (8 байтів)", size=10, bold=True))
    p.append(text(lx + 317, y2 + 75, "біт 63=стиснений формат", size=9, color=MUTED))

    p.append(rect(lx + 425, y2 + 42, 200, 42, fill=F_GREY, stroke=LINE, sw=1.0))
    p.append(text(lx + 525, y2 + 60, "Резерв (48 байтів)", size=9.5, color=MUTED))
    p.append(text(lx + 525, y2 + 75, "мусить бути 0 (#GP)", size=9, color=MUTED))

    # 3. Extended Region (576+ B)
    y3 = 285
    h3 = 135
    p.append(rect(lx, y3, w, h3, fill=F_GRN, stroke=FIELD, sw=1.8))
    p.append(text(lx + 15, y3 + 20, "Extended Region (байти 576 і далі, змінний розмір)", size=12, bold=True, color=FIELD, anchor="start"))
    p.append(text(lx + 15, y3 + 35, "Розміщення компонентів за зсувами з CPUID Leaf 0xD", size=9.5, color=MUTED, italic=True, anchor="start"))

    ext_items = [
        ("YMM_Hi128 (256 Б)", "верхня половина YMM0-15"),
        ("Opmask k0-k7 (64 Б)", "маски вибірки AVX-512"),
        ("ZMM_Hi256 (512 Б)", "верхня чверть ZMM0-15"),
        ("Hi16_ZMM (1024 Б)", "повні регістри ZMM16-31"),
        ("AMX Tile / PKRU", "конфігурація + 8 КБ даних"),
    ]
    ew = 118
    for ei, (ename, edesc) in enumerate(ext_items):
        ex = lx + 15 + ei * (ew + 6)
        p.append(rect(ex, y3 + 45, ew, 75, fill=BG, stroke=FIELD, sw=1.2))
        p.append(text(ex + ew / 2, y3 + 68, ename, size=9.5, bold=True))
        lines = edesc.split("\n") if "\n" in edesc else [edesc]
        for li, ltxt in enumerate(lines):
            p.append(text(ex + ew / 2, y3 + 88 + li * 14, ltxt, size=9, color=MUTED))

    render(os.path.join(OUT, "xsave-frame-layout.svg"), W, H, *p)


# ── 3. xsave-instruction-matrix: сімейство інструкцій XSAVE ───────────────────
def fig_xsave_instruction_matrix():
    W, H = 760, 360
    p = [text(W / 2, 24, "Порівняння властивостей інструкцій сімейства XSAVE", size=15, bold=True)]
    p.append(text(W / 2, 42, "Привілеї виконання, формати пакування та апаратні оптимізації шини",
                  size=10.5, color=MUTED, italic=True))

    cols = [
        ("Інструкція", 110),
        ("Рівень привілеїв", 120),
        ("Формат кадру", 120),
        ("Оптимізація запису", 140),
        ("Підтримка станів", 110),
    ]

    rows = [
        ("XSAVE", "Ring 0–3 (User)", "Стандартний (з дірками)", "Немає (пише все)", "Тільки XCR0 (User)", F_GREY, LINE),
        ("XSAVEOPT", "Ring 0–3 (User)", "Стандартний", "Відстеження змін (In-Use)", "Тільки XCR0 (User)", F_BLUE, NEG),
        ("XSAVEC", "Ring 0–3 (User)", "Стиснений (Compact)", "Пропуск нульових станів", "Тільки XCR0 (User)", F_GLD, GOLD_LINE),
        ("XSAVES", "Ring 0 (Supervisor)", "Стиснений (Compact)", "Відстеження змін + Стиснення", "XCR0 + IA32_XSS (MSR)", F_RED, POS),
    ]

    table_x = 35
    table_y = 65
    row_h = 42

    # Заголовок таблиці
    cur_x = table_x
    for cname, cw in cols:
        p.append(rect(cur_x, table_y, cw, 34, fill=F_GREY, stroke=LINE, sw=1.2))
        p.append(text(cur_x + cw / 2, table_y + 21, cname, size=10, bold=True))
        cur_x += cw + 6

    # Рядки
    for ri, (iname, priv, fmt, opt, states, rfill, rstroke) in enumerate(rows):
        ry = table_y + 40 + ri * (row_h + 8)
        cur_x = table_x
        vals = [iname, priv, fmt, opt, states]
        for vi, val in enumerate(vals):
            cw = cols[vi][1]
            p.append(rect(cur_x, ry, cw, row_h, fill=rfill, stroke=rstroke, sw=1.2))
            is_b = (vi == 0)
            c_col = rstroke if is_b else INK
            p.append(text(cur_x + cw / 2, ry + 25, val, size=9.5, bold=is_b, color=c_col))
            cur_x += cw + 6

    # Висновок під таблицею
    hint_box, _, _ = textbox(W / 2, 315,
                             "XSAVES та XRSTORS у ядрі ОС поєднують стиснений формат пам'яті,\n"
                             "відстеження модифікацій та безпечне збереження системних MSR-станів (CET, LBR, UINTR).",
                             size=9.5, pad=8, fill=F_GRN, stroke=FIELD)
    p.append(hint_box)

    render(os.path.join(OUT, "xsave-instruction-matrix.svg"), W, H, *p)


# ── 4. os-context-switch-fpu: перемикання контексту FPU/AVX у ядрі ─────────────
def fig_os_context_switch_fpu():
    W, H = 760, 420
    p = [text(W / 2, 24, "Перемикання розширеного контексту в планувальнику ядра ОС", size=15, bold=True)]
    p.append(text(W / 2, 42, "Збереження модифікованого стану Потоку А та завантаження стану Потоку Б",
                  size=10.5, color=MUTED, italic=True))

    # Схема: Потік А -> Ядро (switch_to) -> Потік Б
    # 1. Потік А
    ax = 140
    p.append(rect(ax - 90, 70, 180, 80, fill=F_BLUE, stroke=NEG, sw=1.8))
    p.append(text(ax, 95, "Потік А (Користувач)", size=12, bold=True, color=NEG))
    p.append(text(ax, 115, "Активні YMM / ZMM", size=10, color=INK))
    p.append(text(ax, 132, "Переривання таймера / yield", size=9, color=MUTED, italic=True))

    # Стрілка вниз у ядро
    p.append(arrow(ax, 150, ax, 195, color=NEG, sw=2.0))
    p.append(text(ax + 45, 175, "Трап у ядро", size=9.5, color=NEG))

    # 2. Область ядра (Центральна зона)
    kx, ky, kw, kh = 60, 200, 640, 120
    p.append(rect(kx, ky, kw, kh, fill=F_GREY, stroke=LINE, sw=1.8))
    p.append(text(kx + 20, ky + 22, "Ядро ОС (Ring 0): функція switch_to() / fpu__suspend()", size=11, bold=True, anchor="start"))

    # Блок 1: XSAVES Потоку А
    p.append(rect(kx + 20, ky + 35, 270, 70, fill=F_RED, stroke=POS, sw=1.4))
    p.append(text(kx + 155, ky + 58, "1. XSAVES [thread_A->fpstate]", size=10.5, bold=True, color=POS))
    p.append(text(kx + 155, ky + 76, "зберігає тільки брудні компоненти", size=9.5, color=INK))
    p.append(text(kx + 155, ky + 92, "XSTATE_BV фіксує модифіковані регістри", size=9, color=MUTED))

    # Блок 2: Планувальник
    p.append(arrow(kx + 290, ky + 70, kx + 350, ky + 70, color=LINE, sw=1.5))
    p.append(text(kx + 320, ky + 60, "Вибір", size=9, color=MUTED))

    # Блок 3: XRSTORS Потоку Б
    p.append(rect(kx + 350, ky + 35, 270, 70, fill=F_GRN, stroke=FIELD, sw=1.4))
    p.append(text(kx + 485, ky + 58, "2. XRSTORS [thread_B->fpstate]", size=10.5, bold=True, color=FIELD))
    p.append(text(kx + 485, ky + 76, "відновлює дані з пам'яті", size=9.5, color=INK))
    p.append(text(kx + 485, ky + 92, "скидає неактивні в апаратний нуль", size=9, color=MUTED))

    # 3. Потік Б
    bx = 620
    # Стрілка вгору в Потік Б
    p.append(arrow(bx, 200, bx, 150, color=FIELD, sw=2.0))
    p.append(text(bx - 45, 175, "IRET / sysret", size=9.5, color=FIELD))

    p.append(rect(bx - 90, 70, 180, 80, fill=F_GRN, stroke=FIELD, sw=1.8))
    p.append(text(bx, 95, "Потік Б (Користувач)", size=12, bold=True, color=FIELD))
    p.append(text(bx, 115, "Регістри завантажено", size=10, color=INK))
    p.append(text(bx, 132, "Виконання векторного коду", size=9, color=MUTED, italic=True))

    # Нижній пояснювальний напис
    p.append(text(W / 2, 355, "Оптимізація скидання (Init-Optimization): якщо біт XSTATE_BV[i] = 0,", size=10, bold=True))
    p.append(text(W / 2, 372, "процесор не читає пам'ять, а миттєво ініціалізує регістри значенням за замовчуванням.", size=9.5, color=MUTED))

    render(os.path.join(OUT, "os-context-switch-fpu.svg"), W, H, *p)


if __name__ == "__main__":
    fig_xsave_evolution()
    fig_xsave_frame_layout()
    fig_xsave_instruction_matrix()
    fig_os_context_switch_fpu()
    print("Всі фігури згенеровано успішно.")
