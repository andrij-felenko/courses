# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN_FILL, WARN_STROKE = "#fff6e0", "#caa24a"
GOOD_FILL, GOOD_STROKE = "#eef6ef", FIELD
NEW_FILL, NEW_STROKE = "#eaf0fd", NEG


# ── 1. Небезпечне вікно: стерти → записати, збій усередині лишає нецілі дані ───
def fig_window():
    W, H = 720, 300
    p = []
    ox, lane_y = 60, 150
    seg_w = 220
    # дві фази на часовій смузі
    p.append(rect(ox, lane_y - 26, seg_w, 52, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text(ox + seg_w / 2, lane_y - 4, "стирання сектора", size=14, color=POS, bold=True))
    p.append(text(ox + seg_w / 2, lane_y + 15, "мілісекунди", size=11, color=MUTED))
    p.append(rect(ox + seg_w, lane_y - 26, seg_w, 52, fill="#fdf0e0", stroke=WARN_STROKE, sw=1.6))
    p.append(text(ox + seg_w + seg_w / 2, lane_y - 4, "запис байтів", size=14, color="#b9791f", bold=True))
    p.append(text(ox + seg_w + seg_w / 2, lane_y + 15, "не миттєво", size=11, color=MUTED))
    # вісь часу
    p.append(arrow(ox, lane_y + 50, ox + 2 * seg_w + 40, lane_y + 50, color=INK, sw=1.6))
    p.append(text(ox + 2 * seg_w + 36, lane_y + 70, "час", size=12, color=INK, italic=True, anchor="end"))
    # дужка «небезпечне вікно»
    bx0, bx1, by = ox, ox + 2 * seg_w, lane_y - 44
    p.append(line(bx0, by, bx1, by, color=POS, sw=2))
    p.append(line(bx0, by, bx0, by + 10, color=POS, sw=2))
    p.append(line(bx1, by, bx1, by + 10, color=POS, sw=2))
    p.append(text((bx0 + bx1) / 2, by - 8, "небезпечне вікно", size=14, color=POS, bold=True))
    # удар збою посередині
    sx = ox + seg_w + 40
    p.append(line(sx, lane_y - 70, sx, lane_y + 36, color=NEG, sw=2.2, dash="6 4"))
    p.append(text(sx, lane_y - 78, "збій живлення", size=13, color=NEG, bold=True))
    # підсумок-плашка
    box, bw, bh = textbox(W / 2, 250, "Збій усередині: ні старого (вже затерте), ні нового (ще недописане)",
                          size=13, color=INK, fill=WARN_FILL, stroke=WARN_STROKE, sw=1.4, pad=12)
    p.append(box)
    return render(os.path.join(OUT, "danger-window.svg"), W, H, *p)


# ── 2. Розірваний запис гірший за втрату ─────────────────────────────────────
def fig_torn_vs_loss():
    W, H = 720, 300
    p = []
    # ЛІВОРУЧ: втрата оновлення → лишається старе ціле
    lx = 70
    p.append(text(lx + 130, 60, "Втрата оновлення", size=15, color=FIELD, bold=True))
    b, bw, bh = textbox(lx + 130, 130, "старе значення\n(ціле, чинне)", size=13,
                        color=FIELD, fill=GOOD_FILL, stroke=GOOD_STROKE, sw=1.8, pad=14)
    p.append(b)
    p.append(text(lx + 130, 215, "пристрій працює далі —", size=12, color=INK))
    p.append(text(lx + 130, 233, "наче ви й не міняли", size=12, color=INK))
    # роздільник
    p.append(line(W / 2, 50, W / 2, 250, color=MUTED, sw=1.2, dash="4 4"))
    # ПРАВОРУЧ: розірваний запис → сміття
    rx = 400
    p.append(text(rx + 130, 60, "Розірваний запис (torn write)", size=15, color=POS, bold=True))
    # півнового / півстарого
    half = 78
    p.append(rect(rx + 130 - half, 105, half, 50, fill=NEW_FILL, stroke=NEW_STROKE, sw=1.6))
    p.append(text(rx + 130 - half / 2, 135, "нове", size=12, color=NEG, bold=True))
    p.append(rect(rx + 130, 105, half, 50, fill="#f1e3e1", stroke=POS, sw=1.6))
    p.append(text(rx + 130 + half / 2, 135, "старе", size=12, color=POS, bold=True))
    p.append(text(rx + 130, 178, "читається як сміття", size=13, color=POS, bold=True))
    bb, bw, bh = textbox(rx + 130, 224, "пристрій повірить йому\nяк справжнім даним", size=12,
                         color=INK, fill="#f1e3e1", stroke=POS, sw=1.4, pad=11)
    p.append(bb)
    return render(os.path.join(OUT, "torn-vs-loss.svg"), W, H, *p)


# ── 3. Атомарність: пиши нове поряд, тоді перемкни одним кроком ────────────────
def fig_atomic_switch():
    W, H = 760, 280
    p = []
    y = 120
    # три стани зліва направо
    b1, w1, h1 = textbox(140, y, "старе ціле\n(чинне)", size=13, color=FIELD,
                         fill=GOOD_FILL, stroke=GOOD_STROKE, sw=1.8, pad=14, min_w=150)
    p.append(b1)
    p.append(arrow(140 + w1 / 2, y, 300, y, color=MUTED, sw=1.8))
    p.append(text((140 + w1 / 2 + 300) / 2, y - 14, "пишемо поряд", size=11, color=MUTED))
    b2, w2, h2 = textbox(380, y, "старе + нове\n(обидва на чипі)", size=13, color=INK,
                         fill=FILL, stroke=INK, sw=1.6, pad=14, min_w=170)
    p.append(b2)
    p.append(arrow(380 + w2 / 2, y, 560, y, color=POS, sw=2.4))
    p.append(text((380 + w2 / 2 + 560) / 2, y - 14, "1 крок", size=12, color=POS, bold=True))
    b3, w3, h3 = textbox(630, y, "нове чинне\n(перемкнуто)", size=13, color=FIELD,
                         fill=GOOD_FILL, stroke=GOOD_STROKE, sw=1.8, pad=14, min_w=150)
    p.append(b3)
    # точка фіксації
    p.append(text((380 + w2 / 2 + 560) / 2, y + 26, "↑ точка фіксації", size=12, color=POS, bold=True))
    # підсумок
    box, bw, bh = textbox(W / 2, 230, "Збій ДО перемикача → лишається старе · ПІСЛЯ → нове · проміжного стану нема",
                          size=12.5, color=INK, fill=WARN_FILL, stroke=WARN_STROKE, sw=1.4, pad=12)
    p.append(box)
    return render(os.path.join(OUT, "atomic-switch.svg"), W, H, *p)


# ── 4. Контрольна сума: порахуй із даних, звір при читанні ────────────────────
def fig_checksum():
    W, H = 740, 300
    p = []
    # ЗАПИС
    p.append(text(190, 56, "Запис", size=15, color=INK, bold=True))
    b, bw, bh = textbox(150, 120, "дані", size=13, color=INK, fill=FILL, stroke=INK, sw=1.6, pad=16, min_w=110)
    p.append(b)
    p.append(arrow(150 + bw / 2, 120, 300, 120, color=INK, sw=1.6))
    p.append(text((150 + bw / 2 + 300) / 2, 106, "правило", size=10, color=MUTED))
    c, cw, ch = textbox(360, 120, "сума", size=13, color=FIELD, fill=GOOD_FILL, stroke=GOOD_STROKE, sw=1.8, pad=14, min_w=90)
    p.append(c)
    p.append(text(255, 158, "число кладемо ПОРУЧ із даними", size=11, color=MUTED))
    # роздільник
    p.append(line(W / 2 + 30, 50, W / 2 + 30, 250, color=MUTED, sw=1.2, dash="4 4"))
    # ЧИТАННЯ
    rx = 470
    p.append(text(rx + 90, 56, "Читання", size=15, color=INK, bold=True))
    p.append(text(rx + 90, 96, "рахуємо число знову", size=12, color=INK))
    # дві гілки
    g, gw, gh = textbox(rx + 30, 150, "збіг →\nцілі", size=12, color=FIELD, fill=GOOD_FILL, stroke=GOOD_STROKE, sw=1.7, pad=11)
    p.append(g)
    b2, b2w, b2h = textbox(rx + 160, 150, "розбіжність →\nвідкинути", size=12, color=POS, fill="#f1e3e1", stroke=POS, sw=1.7, pad=11)
    p.append(b2)
    # підсумок
    box, bw, bh = textbox(W / 2, 240, "Сума не лагодить дані — вона викриває зіпсовані",
                          size=13, color=INK, fill=WARN_FILL, stroke=WARN_STROKE, sw=1.4, pad=12)
    p.append(box)
    return render(os.path.join(OUT, "checksum.svg"), W, H, *p)


# ── 5. Два слоти A/B з версією й сумою; при старті — найновіший, що пройшов суму ─
def fig_double_slot():
    W, H = 740, 320
    p = []

    def slot(cx, cy, name, ver, ok, active):
        stroke = GOOD_STROKE if ok else POS
        fill = GOOD_FILL if ok else "#f1e3e1"
        bw, bh = 150, 96
        out = rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=fill, stroke=stroke, sw=2.2 if active else 1.5)
        out += text(cx, cy - 26, "слот " + name, size=14, color=INK, bold=True)
        out += text(cx, cy - 4, "версія " + str(ver), size=12, color=INK)
        out += text(cx, cy + 16, "дані + сума", size=11, color=MUTED)
        out += text(cx, cy + 34, "✓ сума" if ok else "✗ сума", size=11,
                    color=FIELD if ok else POS, bold=True)
        if active:
            out += text(cx, cy - bh / 2 - 10, "← беремо цей", size=12, color=FIELD, bold=True)
        return out

    p.append(slot(200, 130, "A", 9, True, True))
    p.append(slot(540, 130, "B", 8, True, False))
    p.append(text(370, 100, "пишемо завжди\nв старіший слот".split("\n")[0], size=12, color=MUTED))
    p.append(arrow(440, 130, 300, 130, color=MUTED, sw=1.6))
    p.append(text(370, 150, "(інший стоїть запасом)", size=11, color=MUTED))
    # правило старту
    box, bw, bh = textbox(W / 2, 250, "При старті: беремо слот із найбільшою версією, що проходить суму",
                          size=13, color=INK, fill=WARN_FILL, stroke=WARN_STROKE, sw=1.4, pad=12)
    p.append(box)
    p.append(text(W / 2, 292, "хоч би коли обірвалось живлення — ціла копія є", size=11.5, color=MUTED))
    return render(os.path.join(OUT, "double-slot.svg"), W, H, *p)


# ── 6. Хто це робить за вас: NVS/LittleFS самі; «голий» Flash — ваша турбота ───
def fig_who_does_it():
    W, H = 720, 300
    p = []
    # ЛІВОРУЧ: бібліотеки беруть на себе
    b, bw, bh = textbox(200, 120, "NVS · LittleFS", size=15, color=FIELD, bold=True,
                        fill=GOOD_FILL, stroke=GOOD_STROKE, sw=2, pad=16, min_w=220)
    p.append(b)
    p.append(text(200, 185, "журнал · copy-on-write · перемикачі", size=11.5, color=INK))
    p.append(text(200, 205, "захист цілості — задарма", size=12.5, color=FIELD, bold=True))
    # роздільник
    p.append(line(W / 2, 50, W / 2, 250, color=MUTED, sw=1.2, dash="4 4"))
    # ПРАВОРУЧ: голий Flash
    b2, b2w, b2h = textbox(520, 120, "«голий» Flash", size=15, color=POS, bold=True,
                           fill="#f1e3e1", stroke=POS, sw=2, pad=16, min_w=220)
    p.append(b2)
    p.append(text(520, 185, "атомарність · суми · слоти —", size=11.5, color=INK))
    p.append(text(520, 205, "усе на ваших плечах", size=12.5, color=POS, bold=True))
    # підсумок
    box, bw, bh = textbox(W / 2, 255, "Тримайтеся NVS і LittleFS — більшість роботи вже зроблено",
                          size=13, color=INK, fill=WARN_FILL, stroke=WARN_STROKE, sw=1.4, pad=12)
    p.append(box)
    return render(os.path.join(OUT, "who-does-it.svg"), W, H, *p)


# ── вставка proj-atomic-config: два слоти (детальніше, з полями) ──────────────
def fig_slots_detail():
    W, H = 720, 280
    p = []

    def slot(cx, name, ver, active):
        bw, bh = 200, 130
        cy = 140
        out = rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=FILL, stroke=INK, sw=2.2 if active else 1.5)
        out += text(cx, cy - 44, "слот " + name, size=15, color=INK, bold=True)
        out += rect(cx - bw / 2 + 14, cy - 28, bw - 28, 24, fill=NEW_FILL, stroke=NEW_STROKE, sw=1.2)
        out += text(cx, cy - 11, "версія " + str(ver), size=12, color=NEG)
        out += rect(cx - bw / 2 + 14, cy, bw - 28, 24, fill="#f4f6f8", stroke=LINE, sw=1.2)
        out += text(cx, cy + 17, "дані (payload)", size=12, color=INK)
        out += rect(cx - bw / 2 + 14, cy + 28, bw - 28, 24, fill=GOOD_FILL, stroke=GOOD_STROKE, sw=1.2)
        out += text(cx, cy + 45, "контрольна сума", size=12, color=FIELD)
        if active:
            out += text(cx, cy - bh / 2 - 12, "найновіший", size=12, color=FIELD, bold=True)
        return out

    p.append(slot(200, "A", 9, True))
    p.append(slot(520, "B", 8, False))
    p.append(arrow(420, 140, 300, 140, color=POS, sw=1.8))
    p.append(text(360, 120, "пишемо в старіший", size=12, color=POS, bold=True))
    p.append(text(360, 248, "окремі сектори: стирання одного не чіпає іншого", size=11.5, color=MUTED, anchor="middle"))
    return render(os.path.join(OUT, "slots-detail.svg"), W, H, *p)


# ── вставка proj-atomic-config: порядок запису, підпис ОСТАННІМ ───────────────
def fig_write_order():
    W, H = 720, 300
    p = []
    steps = [
        ("1", "стерти слот", MUTED, FILL),
        ("2", "записати дані (payload)", INK, FILL),
        ("3", "записати {версія, сума}", POS, "#f1e3e1"),
    ]
    y0 = 90
    for i, (n, label, col, fill) in enumerate(steps):
        y = y0 + i * 62
        p.append(circle(110, y, 16, fill=fill, stroke=col, sw=2))
        p.append(text(110, y + 5, n, size=15, color=col, bold=True))
        bw = 360
        p.append(rect(140, y - 22, bw, 44, fill=fill, stroke=col, sw=1.8))
        p.append(text(140 + bw / 2, y + 5, label, size=14, color=col, bold=(i == 2)))
        if i < 2:
            p.append(arrow(110, y + 16, 110, y + 46, color=MUTED, sw=1.6))
    # позначка точки фіксації коло кроку 3
    y3 = y0 + 2 * 62
    p.append(text(540, y3, "← точка фіксації", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(540, y3 + 20, "(ОСТАННІМ!)", size=11, color=POS, anchor="start"))
    # підсумок
    box, bw, bh = textbox(W / 2, 270, "Доти слот недійсний; збій до кроку 3 → інший слот, після → цей",
                          size=12.5, color=INK, fill=WARN_FILL, stroke=WARN_STROKE, sw=1.4, pad=12)
    p.append(box)
    return render(os.path.join(OUT, "write-order.svg"), W, H, *p)


if __name__ == "__main__":
    fns = [fig_window, fig_torn_vs_loss, fig_atomic_switch, fig_checksum,
           fig_double_slot, fig_who_does_it, fig_slots_detail, fig_write_order]
    for fn in fns:
        path = fn()
        print("wrote", os.path.basename(path))
