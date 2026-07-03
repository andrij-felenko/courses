# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_recipe():
    W, H = 720, 300
    frags = []
    # центральна "картка рецепта"
    cx, cy = 360, 165
    bw, bh = 200, 150
    frags.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill="#eef6ff", stroke=NEG, sw=2))
    frags.append(text(cx, cy - bh / 2 + 28, "РЕЦЕПТ", size=15, color=NEG, bold=True))
    frags.append(text(cx, cy - 8, 'bake_bread()', size=15, bold=True))
    frags.append(text(cx, cy + 20, "записаний", size=12, color=MUTED))
    frags.append(text(cx, cy + 38, "один раз", size=12, color=MUTED))

    # складники ліворуч
    lx = 120
    frags.append(text(lx, 60, "складники", size=13, color=FIELD, bold=True))
    frags.append(text(lx, 78, "(параметри, вхід)", size=11, color=MUTED))
    b1, w1, h1 = textbox(lx, 120, "борошно", size=13, fill="#eafaf1", stroke=FIELD)
    b2, w2, h2 = textbox(lx, 165, "вода", size=13, fill="#eafaf1", stroke=FIELD)
    b3, w3, h3 = textbox(lx, 210, "сіль", size=13, fill="#eafaf1", stroke=FIELD)
    frags += [b1, b2, b3]
    frags.append(arrow(lx + 55, 120, cx - bw / 2 - 6, 150))
    frags.append(arrow(lx + 55, 165, cx - bw / 2 - 6, 165))
    frags.append(arrow(lx + 55, 210, cx - bw / 2 - 6, 180))

    # результат праворуч
    rx = 610
    frags.append(text(rx, 60, "результат", size=13, color=POS, bold=True))
    frags.append(text(rx, 78, "(повернене", size=11, color=MUTED))
    frags.append(text(rx, 93, "значення, вихід)", size=11, color=MUTED))
    bb, wb, hb = textbox(rx, 165, "буханець", size=14, fill="#fdecea", stroke=POS, bold=True)
    frags.append(bb)
    frags.append(arrow(cx + bw / 2 + 6, 165, rx - wb / 2 - 6, 165))

    render(os.path.join(OUT, 'recipe.svg'), W, H, *frags)


def fig_call_return():
    W, H = 720, 340
    frags = []
    # main зліва
    mx = 180
    frags.append(rect(mx - 110, 55, 220, 250, fill="#f4f6f8", stroke=LINE))
    frags.append(text(mx, 78, "main()", size=15, bold=True))
    frags.append(fitbox(mx - 92, 100, 184, 34, "int sum =", size=13, fill=BG))
    # рядок виклику виділено
    frags.append(fitbox(mx - 92, 140, 184, 34, "add(3, 4);", size=13, fill="#fff6e6", stroke=POS))
    frags.append(fitbox(mx - 92, 210, 184, 34, "printf(sum);", size=13, fill=BG))
    frags.append(text(mx, 288, "виконання йде далі", size=11, color=MUTED))

    # add справа
    ax = 545
    frags.append(rect(ax - 120, 90, 240, 180, fill="#eef6ff", stroke=NEG, sw=1.8))
    frags.append(text(ax, 114, "int add(int a, int b)", size=13, bold=True))
    frags.append(fitbox(ax - 104, 132, 208, 32, "a = 3   b = 4", size=13, fill=BG))
    frags.append(fitbox(ax - 104, 172, 208, 32, "result = a + b;", size=13, fill=BG))
    frags.append(fitbox(ax - 104, 220, 208, 34, "return result;", size=13, fill="#eafaf1", stroke=FIELD))

    # стрибок туди (з рядка виклику у функцію) — стрілка тулиться до ВЕРХУ проміжку,
    # підпис лягає нижче лінії (щоб лінія не різала текст)
    frags.append(arrow(mx + 92, 152, ax - 120, 108, color=POS))
    frags.append(text(365, 150, "стрибок усередину", size=12, color=POS, bold=True))
    frags.append(text(365, 165, "(аргументи → параметри)", size=11, color=MUTED))

    # повернення назад (з return у той самий рядок) — стрілка тулиться до НИЗУ проміжку,
    # підпис лягає вище лінії; результат 7
    frags.append(arrow(ax - 120, 258, mx + 92, 196, color=FIELD))
    frags.append(text(365, 200, "повернення: 7", size=12, color=FIELD, bold=True))
    frags.append(text(365, 214, "точно на місце виклику", size=11, color=MUTED))

    render(os.path.join(OUT, 'call-return.svg'), W, H, *frags)


def fig_stack_frames():
    W, H = 720, 340
    frags = []
    # три фази зліва направо
    def frame_stack(cx, top_label, has_add, phase_title):
        base_y = 285
        fw = 150
        # кадр main (низ)
        frags.append(rect(cx - fw / 2, base_y - 70, fw, 70, fill="#f4f6f8", stroke=LINE))
        frags.append(text(cx, base_y - 46, "кадр main", size=12, bold=True))
        frags.append(text(cx, base_y - 28, "локальні,", size=10, color=MUTED))
        frags.append(text(cx, base_y - 14, "адреса повернення", size=10, color=MUTED))
        if has_add:
            frags.append(rect(cx - fw / 2, base_y - 145, fw, 70, fill="#eef6ff", stroke=NEG, sw=1.8))
            frags.append(text(cx, base_y - 121, "кадр add", size=12, bold=True, color=NEG))
            frags.append(text(cx, base_y - 103, "a, b, result,", size=10, color=MUTED))
            frags.append(text(cx, base_y - 89, "адреса повернення", size=10, color=MUTED))
        frags.append(text(cx, 60, phase_title, size=13, bold=True))
        frags.append(text(cx, base_y + 20, top_label, size=11, color=MUTED))

    frame_stack(150, "лише main", False, "1. до виклику")
    frame_stack(390, "add зверху", True, "2. main кличе add")
    frame_stack(630, "кадр знято", False, "3. add повернулась")

    # стрілки між фазами
    frags.append(arrow(232, 200, 300, 200, color=POS))
    frags.append(text(266, 188, "push", size=11, color=POS, bold=True))
    frags.append(arrow(472, 200, 540, 200, color=NEG))
    frags.append(text(506, 188, "pop", size=11, color=NEG, bold=True))

    render(os.path.join(OUT, 'stack-frames.svg'), W, H, *frags)


def fig_wheeler_jump():
    # Історична фігура для hist-subroutine.md: стрибок Вілера на EDSAC.
    # Ліворуч — програма, що кличе; праворуч — підпрограма, що САМА себе
    # переписує: перший наказ вкладає адресу повернення у власний останній наказ.
    W, H = 760, 380
    frags = []

    # ── Програма, що кличе (ліворуч) ──
    mx = 175
    frags.append(rect(mx - 130, 70, 260, 250, fill="#f4f6f8", stroke=LINE))
    frags.append(text(mx, 94, "програма", size=14, bold=True))
    frags.append(fitbox(mx - 112, 112, 224, 46,
                        "42:  занеси 43\n     в акумулятор", size=12, fill="#fff6e6", stroke=POS))
    frags.append(fitbox(mx - 112, 166, 224, 30, "     стрибни в 100", size=12, fill="#fff6e6", stroke=POS))
    frags.append(fitbox(mx - 112, 236, 224, 30, "43:  наступний наказ", size=12, fill=BG, stroke=FIELD))
    frags.append(text(mx, 300, "адреса 43 = «куди вернутись»", size=11, color=MUTED))

    # ── Підпрограма (праворуч) ──
    ax = 575
    frags.append(rect(ax - 135, 70, 270, 250, fill="#eef6ff", stroke=NEG, sw=1.8))
    frags.append(text(ax, 94, "підпрограма (адреса 100)", size=13, bold=True))
    frags.append(fitbox(ax - 118, 112, 236, 46,
                        "100: візьми акумулятор,\n     впиши у наказ 137", size=12, fill="#eafaf1", stroke=FIELD))
    frags.append(fitbox(ax - 118, 166, 236, 30, "…   тіло роботи …", size=12, fill=BG))
    frags.append(fitbox(ax - 118, 206, 236, 46,
                        "137: стрибни в 0\n     → стало: стрибни в 43", size=12, fill="#fdecea", stroke=POS))
    frags.append(text(ax, 300, "останній наказ переписав сам себе", size=11, color=MUTED))

    # ── Стрибок туди: несемо адресу повернення в акумуляторі ──
    # стрілка тулиться до ВЕРХУ проміжку, підпис — нижче лінії (лінія не різатиме текст)
    frags.append(arrow(mx + 130, 176, ax - 135, 106, color=NEG))
    frags.append(text(378, 158, "стрибок у 100", size=12, color=NEG, bold=True))
    frags.append(text(378, 173, "(акумулятор несе 43)", size=11, color=MUTED))

    # ── Повернення: за вписаною адресою назад у 43 ──
    # стрілка тулиться до НИЗУ проміжку, підпис — вище лінії
    frags.append(arrow(ax - 135, 262, mx + 130, 200, color=FIELD))
    frags.append(text(378, 196, "повернення у 43", size=12, color=FIELD, bold=True))
    frags.append(text(378, 210, "за щойно вписаною адресою", size=11, color=MUTED))

    render(os.path.join(OUT, 'wheeler-jump.svg'), W, H, *frags)


# ── Фігури ДЕТАЛЬНОЇ версії (c-functions-d.md) ─────────────────────────────

def fig_frame_anatomy():
    # Анатомія одного кадру на стеку: що саме в ньому лежить, куди росте стек,
    # де вказівник стека (SP) і кадру (FP).
    W, H = 720, 430
    frags = []
    cx = 300
    fw = 300
    x = cx - fw / 2
    # смуги кадру згори (високі адреси) вниз (низькі) — стек росте ВНИЗ
    rows = [
        ("аргументи (що не влізли в регістри)", "#eef6ff", NEG),
        ("адреса повернення", "#fff6e6", POS),
        ("збережений FP попередника", "#f4f6f8", LINE),
        ("збережені регістри (r4…r11)", "#f4f6f8", LINE),
        ("локальні змінні функції", "#eafaf1", FIELD),
    ]
    top = 70
    rh = 52
    for i, (label, fill, stroke) in enumerate(rows):
        y = top + i * rh
        frags.append(fitbox(x, y, fw, rh - 8, label, size=13, fill=fill, stroke=stroke))
    bottom = top + len(rows) * rh
    # дужка "один кадр"
    frags.append(line(x - 18, top, x - 18, bottom - 8, color=INK, sw=2))
    frags.append(line(x - 18, top, x - 10, top, color=INK, sw=2))
    frags.append(line(x - 18, bottom - 8, x - 10, bottom - 8, color=INK, sw=2))
    frags.append(text(x - 60, (top + bottom) / 2, "кадр", size=13, bold=True))
    frags.append(text(x - 60, (top + bottom) / 2 + 18, "виклику", size=13, bold=True))

    # FP — угорі кадру, SP — унизу (на вершині стека)
    rx = x + fw + 20
    frags.append(text(rx + 60, top + 12, "FP → верх кадру", size=12, color=NEG, bold=True, anchor="start"))
    frags.append(arrow(rx + 55, top + 8, x + fw + 4, top + 8, color=NEG))
    sp_y = top + (len(rows) - 1) * rh + (rh - 8) / 2
    frags.append(text(rx + 60, sp_y, "SP → вершина стека", size=12, color=FIELD, bold=True, anchor="start"))
    frags.append(arrow(rx + 55, sp_y, x + fw + 4, sp_y, color=FIELD))

    # стрілка напрямку росту стека
    frags.append(arrow(cx, top - 22, cx, bottom + 6, color=MUTED, sw=2))
    frags.append(text(cx, top - 30, "високі адреси", size=11, color=MUTED))
    frags.append(text(cx, bottom + 24, "стек росте вниз → низькі адреси", size=11, color=MUTED))

    render(os.path.join(OUT, 'frame-anatomy.svg'), W, H, *frags)


def fig_regs_vs_stack():
    # Передавання аргументів: перші чотири — у регістрах r0..r3,
    # решта "спливає" на стек. Показує, чому багато аргументів — дорожче.
    W, H = 720, 360
    frags = []
    # виклик угорі, по центру
    frags.append(fitbox(160, 34, 400, 40, "f(a, b, c, d, e, g)",
                        size=15, fill="#fff6e6", stroke=POS, bold=True))
    frags.append(text(360, 92, "шість аргументів розкладаються так:", size=12, color=MUTED))

    # дві колонки нижче, БЕЗ діагональних стрілок крізь підписи
    col_top = 120
    # ── ліва колонка: регістри ──
    regx = 200
    frags.append(text(regx, col_top, "у регістрах (швидко)", size=13, color=NEG, bold=True))
    regs = ["r0 = a", "r1 = b", "r2 = c", "r3 = d"]
    for i, r in enumerate(regs):
        frags.append(fitbox(regx - 70, col_top + 16 + i * 38, 140, 30, r, size=13, fill="#eef6ff", stroke=NEG))
    frags.append(text(regx, col_top + 16 + 4 * 38 + 14, "перші чотири", size=11, color=MUTED))

    # ── права колонка: стек ──
    stx = 520
    frags.append(text(stx, col_top, "на стеку (повільніше)", size=13, color=FIELD, bold=True))
    stk = ["e", "g"]
    for i, r in enumerate(stk):
        frags.append(fitbox(stx - 70, col_top + 16 + i * 38, 140, 30, r, size=13, fill="#eafaf1", stroke=FIELD))
    frags.append(text(stx, col_top + 16 + 2 * 38 + 14, "решта — в пам'ять", size=11, color=MUTED))
    frags.append(text(stx, col_top + 16 + 2 * 38 + 30, "і зчитати назад: зайві такти", size=11, color=MUTED))

    # тонкий роздільник між колонками (не перетинає підписів)
    frags.append(line(360, col_top + 8, 360, col_top + 16 + 4 * 38, color=MUTED, sw=1, dash="5,5"))

    render(os.path.join(OUT, 'regs-vs-stack.svg'), W, H, *frags)


def fig_recursion_frames():
    # Рекурсія factorial(3): кадри накопичуються вниз до бази, тоді
    # згортаються знизу вгору, перемножуючи по дорозі.
    W, H = 760, 400
    frags = []
    calls = [
        ("fact(3)", "чекає 3 · fact(2)", "#f4f6f8", LINE),
        ("fact(2)", "чекає 2 · fact(1)", "#eef6ff", NEG),
        ("fact(1)", "чекає 1 · fact(0)", "#eef6ff", NEG),
        ("fact(0)", "база: повертає 1", "#eafaf1", FIELD),
    ]
    top = 70
    fw, fh = 210, 60
    x = 90
    for i, (name, note, fill, stroke) in enumerate(calls):
        y = top + i * (fh + 8)
        frags.append(rect(x, y, fw, fh, fill=fill, stroke=stroke, sw=1.8))
        frags.append(text(x + fw / 2, y + 24, name, size=14, bold=True))
        frags.append(text(x + fw / 2, y + 44, note, size=11, color=MUTED))
    # стрілка вниз "виклики глибшають"
    frags.append(arrow(x - 24, top, x - 24, top + 3 * (fh + 8) + fh, color=POS, sw=2))
    frags.append(text(x - 60, top + 120, "виклики", size=12, color=POS, bold=True))
    frags.append(text(x - 60, top + 138, "глибшають", size=12, color=POS, bold=True))

    # праворуч — згортання з результатами
    rx = x + fw + 150
    results = [("1", "fact(0)=1"), ("1·1=1", "fact(1)=1"), ("2·1=2", "fact(2)=2"), ("3·2=6", "fact(3)=6")]
    for i, (calc, res) in enumerate(results):
        y = top + (3 - i) * (fh + 8)
        frags.append(fitbox(rx, y + 12, 180, fh - 20, calc + "   →   " + res, size=12,
                            fill="#fdf0ea", stroke=POS))
    ret_x = rx + 180 + 22
    frags.append(arrow(ret_x, top + 3 * (fh + 8) + fh, ret_x, top + 12, color=FIELD, sw=2))
    frags.append(text(rx + 90, top + 3 * (fh + 8) + fh + 22, "повернення множать угору", size=11, color=FIELD))

    # міст між колонками
    frags.append(text((x + fw + rx) / 2, top - 30, "кожен виклик — свій кадр на стеку", size=13, bold=True))

    render(os.path.join(OUT, 'recursion-frames.svg'), W, H, *frags)


def fig_tail_call():
    # Хвостовий виклик проти звичайного: ліворуч стос кадрів росте,
    # праворуч — один кадр перевикористовується (стек не росте).
    W, H = 760, 360
    frags = []

    def stack_col(cx, title, n_frames, reuse):
        frags.append(text(cx, 55, title, size=14, bold=True))
        base = 300
        fh = 40
        if reuse:
            # один кадр, стрілка-петля "оновлюється на місці"
            y = base - fh
            frags.append(rect(cx - 80, y, 160, fh, fill="#eafaf1", stroke=FIELD, sw=1.8))
            frags.append(text(cx, y + 25, "той самий кадр", size=12, bold=True))
            frags.append(arrow(cx + 95, y + 8, cx + 95, y + fh - 4, color=FIELD))
            frags.append(text(cx + 100, y + fh / 2, "оновлюється", size=11, color=FIELD, anchor="start"))
            frags.append(text(cx, base + 30, "стек НЕ росте", size=12, color=FIELD, bold=True))
        else:
            for i in range(n_frames):
                y = base - (i + 1) * (fh + 4)
                fill = "#eef6ff" if i < n_frames - 1 else "#fdecea"
                frags.append(rect(cx - 80, y, 160, fh, fill=fill, stroke=NEG if i < n_frames - 1 else POS, sw=1.6))
                frags.append(text(cx, y + 25, "кадр #%d" % (i + 1), size=12))
            frags.append(text(cx, base + 30, "стек росте з глибиною", size=12, color=POS, bold=True))

    stack_col(200, "звичайна рекурсія", 4, False)
    stack_col(560, "хвостовий виклик", 1, True)

    # роздільник
    frags.append(line(380, 60, 380, 320, color=MUTED, sw=1, dash="5,5"))

    render(os.path.join(OUT, 'tail-call.svg'), W, H, *frags)


def fig_static_vs_stack():
    """Чому рекурсія й стек народилися разом: та сама функція, викликана,
    поки перший виклик ще не скінчився. Статично (Fortran) — один спільний
    слот, другий виклик затирає перший. Стеково (ALGOL 60) — окремий кадр на
    кожен виклик, обидва живі."""
    W, H = 760, 380
    frags = []
    frags.append(text(W / 2, 30, " f() кличе f(), поки перший виклик ще працює", size=15, bold=True))

    # ── ЛІВОРУЧ: статичне розміщення (Fortran) ──
    lx = 205
    frags.append(text(lx, 66, "статично (Fortran)", size=14, bold=True, color=POS))
    frags.append(text(lx, 84, "один слот на функцію, назавжди", size=11, color=MUTED))
    slot_y, slot_h = 150, 90
    frags.append(rect(lx - 95, slot_y, 190, slot_h, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(text(lx, slot_y + 24, "слот f()", size=13, bold=True))
    frags.append(text(lx, slot_y + 46, "локальні + адреса", size=11, color=MUTED))
    frags.append(text(lx, slot_y + 62, "повернення", size=11, color=MUTED))
    # два виклики цілять в ОДИН слот
    frags.append(text(lx - 60, 300, "1-й виклик", size=12, color=NEG))
    frags.append(text(lx + 60, 300, "2-й виклик", size=12, color=POS, bold=True))
    frags.append(arrow(lx - 60, 292, lx - 30, slot_y + slot_h + 4, color=NEG))
    frags.append(arrow(lx + 60, 292, lx + 30, slot_y + slot_h + 4, color=POS))
    frags.append(text(lx, 340, "другий затирає перший", size=12, color=POS, bold=True))
    frags.append(text(lx, 358, "повернутися вже нікуди", size=11, color=MUTED))

    # роздільник
    frags.append(line(W / 2, 60, W / 2, 360, color=MUTED, sw=1, dash="5,5"))

    # ── ПРАВОРУЧ: стекове розміщення (ALGOL 60) ──
    rx = 555
    frags.append(text(rx, 66, "стеково (ALGOL 60)", size=14, bold=True, color=FIELD))
    frags.append(text(rx, 84, "свіжий кадр на КОЖЕН виклик", size=11, color=MUTED))
    fh = 52
    base = 300
    # два кадри один на одному
    y1 = base - fh
    y2 = base - 2 * fh - 6
    frags.append(rect(rx - 95, y1, 190, fh, fill="#eef6ff", stroke=NEG, sw=1.8))
    frags.append(text(rx, y1 + 22, "кадр f() — виклик 1", size=12))
    frags.append(text(rx, y1 + 40, "свої дані, ціле", size=10, color=MUTED))
    frags.append(rect(rx - 95, y2, 190, fh, fill="#eafaf1", stroke=FIELD, sw=1.8))
    frags.append(text(rx, y2 + 22, "кадр f() — виклик 2", size=12, bold=True))
    frags.append(text(rx, y2 + 40, "окремі дані, ціле", size=10, color=MUTED))
    frags.append(text(rx, base + 26, "обидва живі — рекурсія працює", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, 'static-vs-stack.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_recipe()
    fig_call_return()
    fig_stack_frames()
    fig_wheeler_jump()
    fig_frame_anatomy()
    fig_regs_vs_stack()
    fig_recursion_frames()
    fig_tail_call()
    fig_static_vs_stack()
    print("done")
