# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. До/після: клієнт у павутинні підсистеми vs клієнт крізь одні двері ────
def fig_before_after():
    W, H = 900, 470
    frags = []
    frags.append(text(W/2, 30, "Фасад: одні двері замість павутиння викликів", size=17, bold=True))

    # роздільна вісь
    frags.append(line(W/2, 60, W/2, 448, color=MUTED, sw=1.2, dash="5 5"))

    # ── ЛІВОРУЧ: без фасаду — клієнт тягне лінії до кожної частини ──
    frags.append(text(225, 66, "БЕЗ ФАСАДУ", size=14, color=POS, bold=True))
    frags.append(text(225, 86, "клієнт знає всі частини й порядок", size=11.5, color=MUTED, italic=True))
    # клієнт зверху
    frags.append(rect(225 - 70, 104, 140, 40, fill=FILL, stroke=INK, sw=2, rx=8))
    frags.append(text(225, 129, "Клієнт", size=13, color=INK, bold=True))
    # чотири частини підсистеми внизу
    parts = [("Кодек", 70), ("Аудіо", 160), ("Тара", 250), ("Файли", 340)]
    py = 300
    for label, x in parts:
        frags.append(rect(x, py, 78, 38, fill="#fdecea", stroke=MUTED, sw=1.4, rx=6))
        frags.append(text(x + 39, py + 24, label, size=12, color=INK))
        # лінія від клієнта до кожної частини
        frags.append(line(225, 144, x + 39, py, color=POS, sw=1.5))
    frags.append(text(225, 400, "4 залежності, 6 кроків у голові клієнта", size=11.5, color=POS))
    frags.append(text(225, 420, "нова частина → правка клієнта", size=11.5, color=MUTED, italic=True))

    # ── ПРАВОРУЧ: із фасадом — одна лінія до фасаду ──
    frags.append(text(675, 66, "ІЗ ФАСАДОМ", size=14, color=FIELD, bold=True))
    frags.append(text(675, 86, "клієнт знає лише фасад", size=11.5, color=MUTED, italic=True))
    frags.append(rect(675 - 70, 104, 140, 40, fill=FILL, stroke=INK, sw=2, rx=8))
    frags.append(text(675, 129, "Клієнт", size=13, color=INK, bold=True))
    # фасад посередині
    frags.append(rect(675 - 90, 196, 180, 44, fill="#eafaf0", stroke=FIELD, sw=2.5, rx=10))
    frags.append(text(675, 223, "Фасад", size=14, color=FIELD, bold=True))
    frags.append(line(675, 144, 675, 196, color=FIELD, sw=2))
    frags.append(text(675 + 100, 172, "одна", size=10.5, color=MUTED, anchor="start"))
    frags.append(text(675 + 100, 186, "лінія", size=10.5, color=MUTED, anchor="start"))
    # ті самі частини, лінії тепер від фасаду
    for label, x in parts:
        # зсунемо праву половину частин у праву колонку
        rx = x + 450
        frags.append(rect(rx, py, 78, 38, fill=FILL, stroke=MUTED, sw=1.4, rx=6))
        frags.append(text(rx + 39, py + 24, label, size=12, color=MUTED))
        frags.append(line(675, 240, rx + 39, py, color=MUTED, sw=1.2))
    frags.append(text(675, 400, "1 залежність, порядок сховано у фасаді", size=11.5, color=FIELD))
    frags.append(text(675, 420, "нова частина → правка лише фасаду", size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'before-after.svg'), W, H, *frags)


# ── 2. Фасад — двері, а не мур: підсистема лишається доступною напряму ───────
def fig_door_not_wall():
    W, H = 820, 400
    frags = []
    frags.append(text(W/2, 30, "Фасад — це двері, а не мур", size=17, bold=True))

    # велика рамка підсистеми
    sx, sy, sw_, sh = 250, 70, 520, 290
    frags.append(rect(sx, sy, sw_, sh, fill="#f8f9fb", stroke=MUTED, sw=1.6, rx=12))
    frags.append(text(sx + sw_/2, sy + 24, "ПІДСИСТЕМА", size=13, color=MUTED, bold=True))

    # частини всередині
    inner = [
        ("Кодек", sx + 60, sy + 70),
        ("Аудіо", sx + 210, sy + 70),
        ("Тара", sx + 360, sy + 70),
        ("Буфери", sx + 130, sy + 160),
        ("Метадані", sx + 290, sy + 160),
    ]
    for label, x, y in inner:
        frags.append(rect(x, y, 100, 40, fill=FILL, stroke=INK, sw=1.4, rx=6))
        frags.append(text(x + 50, y + 25, label, size=12, color=INK))

    # фасад — на межі підсистеми (двері в стіні)
    fx, fy = 90, 150
    frags.append(rect(fx, fy, 120, 60, fill="#eafaf0", stroke=FIELD, sw=2.5, rx=10))
    frags.append(text(fx + 60, fy + 27, "Фасад", size=14, color=FIELD, bold=True))
    frags.append(text(fx + 60, fy + 46, "прості двері", size=10.5, color=MUTED, italic=True))

    # клієнт А — крізь фасад (звичайний шлях)
    frags.append(rect(40, 80, 130, 36, fill=FILL, stroke=NEG, sw=1.8, rx=8))
    frags.append(text(105, 104, "Клієнт (звичай)", size=11.5, color=NEG, bold=True))
    frags.append(arrow(105, 116, 130, fy, color=NEG, sw=1.8))
    # фасад → углиб (кілька)
    frags.append(arrow(fx + 120, fy + 20, sx + 60, sy + 90, color=FIELD, sw=1.6))
    frags.append(arrow(fx + 120, fy + 30, sx + 130, sy + 180, color=FIELD, sw=1.6))

    # клієнт Б — напряму до частини (рідкісний випадок, двері не замикають)
    frags.append(rect(40, 300, 150, 36, fill=FILL, stroke=MUTED, sw=1.6, rx=8))
    frags.append(text(115, 324, "Клієнт (тонкий тюнінг)", size=11, color=MUTED, bold=True))
    frags.append(arrow(190, 306, sx + 130, sy + 180, color=MUTED, sw=1.5))

    frags.append(text(W/2, 386, "звичайний клієнт іде крізь фасад; хто мусить — усе одно дістане частину напряму",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'door-not-wall.svg'), W, H, *frags)


# ── 3. Три сусіди: фасад vs адаптер vs посередник ───────────────────────────
def fig_three_neighbors():
    W, H = 900, 400
    frags = []
    frags.append(text(W/2, 30, "Схожі на вигляд, різні за задачею", size=17, bold=True))

    cols = [
        ("ФАСАД", "СПРОСТИТИ", "багато частин → одні прості двері;\nпорядок і зв'язки сховано",
         "структурний · однобічно:\nклієнт → підсистема", FIELD, 40),
        ("АДАПТЕР", "ПЕРЕКЛАСТИ", "чужий інтерфейс → наш очікуваний;\nзазвичай одна обгортка",
         "структурний · переклад,\nа не спрощення", NEG, 330),
        ("ПОСЕРЕДНИК", "РОЗВ'ЯЗАТИ", "частини не кличуть одна одну\nнапряму — усе через центр",
         "поведінковий · двобічно:\nчастини ⇄ центр", POS, 620),
    ]
    cw = 250
    top = 58
    for title, verb, what, kind, col, x in cols:
        frags.append(rect(x, top, cw, 44, fill="#f4f6f8", stroke=col, sw=2.5, rx=10))
        frags.append(text(x + cw/2, top + 21, title, size=14, color=col, bold=True))
        frags.append(text(x + cw/2, top + 37, verb, size=11.5, color=MUTED, bold=True))
        # що робить
        wl = what.split("\n")
        wy = top + 78
        for ln in wl:
            frags.append(text(x + cw/2, wy, ln, size=11.5, color=INK))
            wy += 18
        # рід/напрям — у рамці fitbox
        frags.append(fitbox(x, top + 150, cw, 60, kind, size=11.5, pad=10,
                            fill=BG, stroke=col, sw=1.4, rx=8, color=MUTED))

    # спільний рядок унизу
    frags.append(text(W/2, 350, "усі троє стоять МІЖ клієнтом і рештою — але з різною метою",
                      size=12.5, color=MUTED, italic=True))
    frags.append(text(W/2, 372, "фасад спрощує · адаптер перекладає · посередник розв'язує зв'язки",
                      size=12, color=INK))

    render(os.path.join(OUT, 'three-neighbors.svg'), W, H, *frags)


# ── 4. Часова смуга: як «фасад» став іменованим патерном (для hist-вставки) ──
def fig_timeline():
    W, H = 940, 430
    frags = []
    frags.append(text(W/2, 30, "Як «фасад» став іменованим патерном", size=17, bold=True))

    # головна вісь часу
    axis_y = 150
    x0, x1 = 70, 870
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.5))
    frags.append(arrow(x1 - 2, axis_y, x1 + 20, axis_y, color=INK, sw=2.5))

    # віхи: (рік, підпис-угорі, підпис-унизу, колір, x)
    marks = [
        ("1977", "Александер", "«A Pattern Language»\n— патерн у зодчестві", NEG, 150),
        ("1990", "OOPSLA, BOF", "Гамма й Гелм\nзнаходять одне одного", FIELD, 360),
        ("1991", "дисертація", "каталог патернів\nз ET++ (Гамма)", MUTED, 545),
        ("1994", "«Design Patterns»", "банда чотирьох:\nфасад канонізовано", POS, 770),
    ]
    for year, top_lbl, bot_lbl, col, x in marks:
        frags.append(circle(x, axis_y, 8, fill=BG, stroke=col, sw=3))
        frags.append(text(x, axis_y - 40, year, size=15, color=col, bold=True))
        frags.append(text(x, axis_y - 22, top_lbl, size=11.5, color=INK, bold=True))
        for i, ln in enumerate(bot_lbl.split("\n")):
            frags.append(text(x, axis_y + 30 + i * 17, ln, size=11, color=MUTED))

    # нижня плашка з наміром GoF
    by = 330
    box_body, bw, bh = textbox(W/2, by + 30,
        "Намір (GoF): дати уніфікований інтерфейс до набору\n"
        "інтерфейсів підсистеми; фасад визначає інтерфейс вищого\n"
        "рівня, що робить підсистему простішою у використанні.",
        size=12, pad=14, fill=FILL, stroke=POS, sw=1.6, color=INK, rx=10)
    frags.append(box_body)

    render(os.path.join(OUT, 'facade-timeline.svg'), W, H, *frags)


# ── 5. Сага оформлення: кроки й компенсації при відкоті (для proj-вставки) ───
def fig_checkout_saga():
    W, H = 900, 560
    frags = []
    frags.append(text(W/2, 30, "Оформлення як сага: кожен крок має компенсацію", size=17, bold=True))

    # чотири кроки згори вниз, ліва колонка
    step_x = 300
    step_w = 220
    ys = [80, 190, 300, 410]
    steps = [
        ("1. Резерв товару", "inventory.reserve", FIELD),
        ("2. Платіж", "payments.charge", FIELD),
        ("3. Запис замовлення", "orders.create", FIELD),
        ("4. Лист (некритичний)", "mailer.sendConfirmation", MUTED),
    ]
    cx = step_x + step_w / 2
    for (title, call, col), y in zip(steps, ys):
        frags.append(rect(step_x, y, step_w, 62, fill="#eafaf0" if col == FIELD else FILL,
                          stroke=col, sw=2, rx=9))
        frags.append(text(cx, y + 26, title, size=13, color=INK, bold=True))
        frags.append(text(cx, y + 46, call + "()", size=11, color=MUTED, italic=True))
        # стрілка «далі» до наступного кроку
        if y != ys[-1]:
            frags.append(arrow(cx, y + 62, cx, y + 62 + (ys[1] - ys[0] - 62), color=INK, sw=1.8))

    # ── компенсації: дуги ПРАВОРУЧ від кроків, знизу вгору ──
    comp_x = step_x + step_w + 40   # старт компенсаційних написів
    # платіж упав → зняти резерв (крок2 → крок1)
    frags.append(line(step_x + step_w, ys[1] + 31, comp_x + 30, ys[1] + 31, color=POS, sw=1.6, dash="4 4"))
    frags.append(line(comp_x + 30, ys[1] + 31, comp_x + 30, ys[0] + 31, color=POS, sw=1.6, dash="4 4"))
    frags.append(arrow(comp_x + 30, ys[0] + 31, step_x + step_w, ys[0] + 31, color=POS, sw=1.6))
    frags.append(text(comp_x + 45, ys[0] + 20, "платіж упав →", size=11, color=POS, anchor="start"))
    frags.append(text(comp_x + 45, ys[0] + 36, "release(резерв)", size=11, color=POS, anchor="start", italic=True))

    # запис упав → refund + release (крок3 → крок2 і крок1)
    frags.append(line(step_x + step_w, ys[2] + 31, comp_x + 150, ys[2] + 31, color=NEG, sw=1.6, dash="4 4"))
    frags.append(line(comp_x + 150, ys[2] + 31, comp_x + 150, ys[1] + 46, color=NEG, sw=1.6, dash="4 4"))
    frags.append(arrow(comp_x + 150, ys[1] + 46, step_x + step_w, ys[1] + 46, color=NEG, sw=1.6))
    frags.append(text(comp_x + 165, ys[2] + 8, "запис упав →", size=11, color=NEG, anchor="start"))
    frags.append(text(comp_x + 165, ys[2] + 24, "refund(платіж)", size=11, color=NEG, anchor="start", italic=True))
    frags.append(text(comp_x + 165, ys[2] + 40, "+ release(резерв)", size=11, color=NEG, anchor="start", italic=True))

    # лист некритичний — окрема плашка, БЕЗ відкоту
    frags.append(fitbox(comp_x, ys[3] + 6, 250, 50,
                        "лист упав → нічого не відкочуємо:\nгроші взято, товар зарезервовано",
                        size=11, pad=8, fill=BG, stroke=MUTED, sw=1.4, rx=8, color=MUTED))

    # легенда ліворуч
    frags.append(text(70, ys[0] + 6, "кроки", size=12, color=INK, bold=True, anchor="start"))
    frags.append(text(70, ys[0] + 24, "вперед ↓", size=11, color=MUTED, anchor="start"))
    frags.append(text(70, ys[1] + 6, "компенсації", size=12, color=POS, bold=True, anchor="start"))
    frags.append(text(70, ys[1] + 24, "назад ↑ у", size=11, color=MUTED, anchor="start"))
    frags.append(text(70, ys[1] + 40, "зворотному", size=11, color=MUTED, anchor="start"))
    frags.append(text(70, ys[1] + 56, "порядку", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'checkout-saga.svg'), W, H, *frags)


# ── 6. Зчеплення клієнта до/після фасаду: два стовпчики (для proj-вставки) ───
def fig_coupling_before_after():
    W, H = 860, 470
    frags = []
    frags.append(text(W/2, 30, "Зчеплення клієнта з підсистемою: до і після фасаду", size=17, bold=True))

    base_y = 400            # низ стовпчиків
    max_h = 300             # висота найбільшого

    # ── лівий стовпчик: БЕЗ фасаду — 6 типів + порядок + відкіт, ×N місць ──
    lx = 210
    bar_w = 150
    l_h = max_h
    frags.append(rect(lx - bar_w/2, base_y - l_h, bar_w, l_h, fill="#fdecea", stroke=POS, sw=2, rx=8))
    frags.append(text(lx, base_y - l_h - 16, "БЕЗ ФАСАДУ", size=14, color=POS, bold=True))
    # шари всередині стовпчика
    layers_l = [
        "6 типів підсистеми",
        "+ знання порядку 4 кроків",
        "+ знання відкоту",
    ]
    ly = base_y - l_h + 34
    for ln in layers_l:
        frags.append(text(lx, ly, ln, size=12, color=INK, bold=True))
        ly += 30
    frags.append(text(lx, base_y - 40, "× кожне місце", size=12, color=POS, bold=True))
    frags.append(text(lx, base_y - 20, "оформлення", size=12, color=POS, bold=True))

    # ── правий стовпчик: ІЗ фасадом — 1 тип, 0 порядку, 0 відкоту ──
    rx = 650
    r_h = 90
    frags.append(rect(rx - bar_w/2, base_y - r_h, bar_w, r_h, fill="#eafaf0", stroke=FIELD, sw=2.5, rx=8))
    frags.append(text(rx, base_y - r_h - 16, "ІЗ ФАСАДОМ", size=14, color=FIELD, bold=True))
    frags.append(text(rx, base_y - r_h + 30, "1 тип підсистеми", size=12.5, color=INK, bold=True))
    frags.append(text(rx, base_y - r_h + 52, "(сам фасад)", size=11.5, color=MUTED, italic=True))
    frags.append(text(rx, base_y - r_h + 72, "0 порядку · 0 відкоту", size=11.5, color=FIELD, bold=True))

    # спільна вісь-основа
    frags.append(line(90, base_y, 780, base_y, color=INK, sw=2))
    frags.append(text(90, base_y + 20, "число зв'язків клієнта з підсистемою →", size=11.5,
                      color=MUTED, anchor="start", italic=True))

    # велика стрілка «падіння» між стовпчиками
    frags.append(arrow(lx + bar_w/2 + 20, base_y - l_h/2, rx - bar_w/2 - 20, base_y - r_h/2, color=INK, sw=2.5))
    frags.append(text((lx + rx)/2, base_y - 210, "6 → 1", size=20, color=INK, bold=True))
    frags.append(text((lx + rx)/2, base_y - 186, "фасад стягує в одну точку", size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'coupling-before-after.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_before_after()
    fig_door_not_wall()
    fig_three_neighbors()
    fig_timeline()
    fig_checkout_saga()
    fig_coupling_before_after()
    print("figures written to", OUT)
