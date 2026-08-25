# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


# ── Фігура 1: сито вимог — крізь архітектуру проходить лише мала частина ──────
def fig_sieve():
    W, H = 780, 440
    frags = []

    lx, ly = 40, 78
    lw = 220
    frags.append(text(lx + lw / 2, 44, "Усі вимоги до системи", size=15, bold=True))
    items = [
        "«кнопка синя»",
        "формат звіту — PDF",
        "витримати 10× пік",
        "закон: дані лишаються в ЄС",
        "заміна БД за тиждень",
        "текст підказки на екрані",
        "відмова вузла — без простою",
        "мова інтерфейсу",
    ]
    is_driver = [False, False, True, True, True, False, True, False]
    box_h = 36
    gap = 8
    left_centers = []
    yy = ly
    for i, it in enumerate(items):
        col = FIELD if is_driver[i] else MUTED
        fill = "#eafaf1" if is_driver[i] else FILL
        frags.append(fitbox(lx, yy, lw, box_h, it, size=12, fill=fill, stroke=col, sw=1.6))
        left_centers.append((lx + lw, yy + box_h / 2, is_driver[i]))
        yy += box_h + gap

    # Сито — вертикальна пунктирна межа з підписом
    sx = 380
    frags.append(text(sx, 42, "Сито архітектора", size=15, bold=True))
    frags.append(text(sx, 62, "«чи змінить це структуру?»", size=12, color=MUTED))
    frags.append(line(sx, 76, sx, H - 26, color=INK, sw=2, dash="4,6"))

    # Права колонка — тільки драйвери
    rx = 560
    rw = 185
    frags.append(text(rx + rw / 2, 44, "Архітектурні драйвери", size=15, bold=True))
    drivers = [it for it, d in zip(items, is_driver) if d]
    ry = 90
    right_centers = []
    for it in drivers:
        frags.append(fitbox(rx, ry, rw, box_h, it, size=12, fill="#eafaf1", stroke=FIELD, sw=1.7))
        right_centers.append((rx, ry + box_h / 2))
        ry += box_h + gap

    # Стрілки: кожен драйвер зліва -> крізь сито -> у відповідну праву рамку
    ri = 0
    for (cx, cy, drv) in left_centers:
        if drv:
            tx, ty = right_centers[ri]
            frags.append(line(cx + 2, cy, sx - 3, cy, color=FIELD, sw=1.7))
            frags.append(arrow(sx + 3, cy, tx - 5, ty, color=FIELD, sw=1.7))
            ri += 1

    render(os.path.join(IMG, "sieve.svg"), W, H, *frags)


# ── Фігура 2: п'ять різновидів драйверів сходяться у структуру ───────────────
def fig_five_kinds():
    W, H = 820, 440
    frags = []
    cx, cy = W / 2, H / 2
    body, bw, bh = textbox(cx, cy, ["Структура", "системи"], size=17, bold=True,
                           fill="#eafaf1", stroke=FIELD, sw=2.2, min_w=190)

    # П'ять рамок по колу; кожна — заголовок + короткий підпис, з великим запасом
    kinds = [
        ("Мета проєкту", "нащо система існує"),
        ("Якісні атрибути", "швидко · надійно · змінно"),
        ("Головна функціональність", "кілька дій, що роблять систему собою"),
        ("Обмеження", "тверді рамки: закон · стек · дедлайн"),
        ("Турботи", "рішення поза вимогами: логи · збірка"),
    ]
    # позиції (x,y) центрів рамок — розкидані, щоб стрілки не збігалися
    pos = [
        (150, 90),
        (150, H - 90),
        (W - 160, 90),
        (W - 160, H - 90),
        (cx, H - 60),
    ]
    for (title, sub), (px, py) in zip(kinds, pos):
        b, w, h = textbox(px, py, [title, sub], size=12, min_w=210,
                          fill=FILL, stroke=INK, sw=1.6)
        frags.append(b)
        # стрілка від краю рамки до краю центральної
        # напрям — від (px,py) до (cx,cy)
        dx, dy = cx - px, cy - py
        import math
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        # старт — від краю малої рамки, кінець — за 6px до краю центральної
        sx0 = px + ux * (w / 2 + 4)
        sy0 = py + uy * (h / 2 + 4)
        ex0 = cx - ux * (bw / 2 + 8)
        ey0 = cy - uy * (bh / 2 + 8)
        frags.append(arrow(sx0, sy0, ex0, ey0, color=INK, sw=1.7))

    frags.append(body)  # центр поверх стрілок
    render(os.path.join(IMG, "five-kinds.svg"), W, H, *frags)


# ── Фігура 3: бюджет 50 мс — з чого складається шлях до безпечного стану ─────
def fig_budget():
    W, H = 860, 340
    frags = []
    frags.append(text(W / 2, 34, "Бюджет 50 мс: куди йде час від відмови до безпечного стану",
                      size=15, bold=True))

    # Вісь часу — суцільна смуга 0..50 мс
    bx, by = 60, 150
    bw, bh = 740, 46
    total_ms = 50.0
    # сегменти: (підпис, мс, колір-заливка, колір-рамка)
    segs = [
        ("очікування такту", 1.0, "#fdecea", POS),      # до 1 мс, поки тик помітить
        ("вхід у переривання", 0.02, FILL, MUTED),      # латентність переривання (умовно)
        ("робота обробника", 0.03, "#eafaf1", FIELD),   # знеструмити привод
        ("запас (margin)", 47.95, FILL, INK),           # решта до 50
    ]
    # ширини непропорційні реальним мс (перші три — крихітні), тож малюємо
    # їх з мінімальною видимою шириною, а «запас» забирає решту
    min_w = 120
    fixed = min_w * 3
    margin_w = bw - fixed
    x = bx
    seg_geo = []
    for i, (label, ms, fill, col) in enumerate(segs):
        w = margin_w if i == 3 else min_w
        frags.append(rect(x, by, w, bh, fill=fill, stroke=col, sw=1.8))
        seg_geo.append((x, w, label, ms, col))
        x += w

    # мітки шкали під смугою: 0, ~1 мс (межа виявлення), 50 мс
    def tick(px, ms_label, sub=None):
        out = line(px, by + bh, px, by + bh + 10, color=INK, sw=1.4)
        out += text(px, by + bh + 26, ms_label, size=12, bold=True)
        if sub:
            out += text(px, by + bh + 42, sub, size=10, color=MUTED)
        return out
    frags.append(tick(bx, "0 мс", "відмова датчика"))
    frags.append(tick(bx + fixed, "≈1 мс", "виявлено + оброблено"))
    frags.append(tick(bx + bw, "50 мс", "тверда межа"))

    # підписи сегментів — над смугою, з нахилом-виноскою, щоб не накладались
    label_y = [92, 74, 92, 120]
    for i, (sx, sw_, label, ms, col) in enumerate(seg_geo):
        cx = sx + sw_ / 2
        ly = label_y[i]
        if i < 3:
            b, w, h = textbox(cx, ly, label, size=11, fill="#ffffff", stroke=col, sw=1.4)
            frags.append(b)
            frags.append(line(cx, ly + h / 2, cx, by - 1, color=col, sw=1.2, dash="3,4"))
        else:
            b, w, h = textbox(cx, ly, [label, "тут прошивка вільна:", "екран, зв'язок, логи"],
                              size=11, fill="#ffffff", stroke=col, sw=1.4)
            frags.append(b)

    # підсумковий рядок під шкалою
    frags.append(text(W / 2, H - 18,
                      "критичний шлях з'їдає ≈1 мс із 50 — решта 49 лишається фону",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "budget.svg"), W, H, *frags)


# ── Фігура 4: переривання прориває фон — критичний шлях не залежить від фону ──
def fig_preempt():
    W, H = 860, 420
    frags = []
    frags.append(text(W / 2, 30, "Високопріоритетне переривання прориває фон у будь-яку мить",
                      size=15, bold=True))

    lane_x = 200
    lane_w = 600
    # дві доріжки
    bg_y = 260
    isr_y = 120
    lane_h = 34

    frags.append(text(lane_x - 14, bg_y + lane_h / 2 + 4, "фоновий цикл", size=12,
                      bold=True, anchor="end"))
    frags.append(text(lane_x - 14, isr_y + lane_h / 2 + 4, "таймер, пріор. 0", size=12,
                      bold=True, anchor="end", color=POS))

    # фон — довгий блок роботи (екран/зв'язок/логи), із «діркою» під переривання
    ev_x = lane_x + 330          # мить відмови
    gap_a = ev_x - lane_x
    isr_w = 60                   # видима ширина роботи переривання
    frags.append(rect(lane_x, bg_y, gap_a, lane_h, fill=FILL, stroke=MUTED, sw=1.6))
    frags.append(text(lane_x + gap_a / 2, bg_y + lane_h / 2 + 4,
                      "display · comms · log", size=11, color=MUTED))
    resume_x = ev_x + isr_w
    frags.append(rect(resume_x, bg_y, lane_x + lane_w - resume_x, lane_h,
                      fill=FILL, stroke=MUTED, sw=1.6))
    frags.append(text((resume_x + lane_x + lane_w) / 2, bg_y + lane_h / 2 + 4,
                      "…фон триває далі", size=11, color=MUTED))

    # переривання — короткий блок на верхній доріжці рівно над подією
    frags.append(rect(ev_x, isr_y, isr_w, lane_h, fill="#eafaf1", stroke=FIELD, sw=1.9))
    frags.append(text(ev_x + isr_w / 2, isr_y + lane_h / 2 + 4, "safe", size=11, bold=True))

    # подія відмови — вертикальна лінія-тригер від верху фонового блоку до низу переривання
    frags.append(line(ev_x, bg_y, ev_x, isr_y + lane_h, color=POS, sw=1.6, dash="4,5"))
    # маркер події — «+» осторонь лінії, щоб її не перетинати
    frags.append(plus(ev_x - 16, bg_y + lane_h / 2, r=8))
    b, w, h = textbox(ev_x, isr_y - 36, ["датчик замовк →", "витиснення фону"],
                      size=11, fill="#ffffff", stroke=POS, sw=1.4)
    frags.append(b)

    # стрілки: фон -> перерив (витиснення) і перерив -> фон (повернення)
    frags.append(arrow(ev_x - 2, bg_y, ev_x - 2, isr_y + lane_h + 2, color=FIELD, sw=1.6))
    frags.append(arrow(ev_x + isr_w + 2, isr_y + lane_h, resume_x + 2, bg_y, color=MUTED, sw=1.4))

    # дужка критичного шляху — ПІД фоновою доріжкою (нижче всіх вертикальних ліній),
    # щоб жодна лінія не перетинала підпис
    ry = bg_y + lane_h + 34
    frags.append(line(ev_x, ry, ev_x + isr_w, ry, color=INK, sw=1.4))
    frags.append(line(ev_x, ry, ev_x, ry - 7, color=INK, sw=1.4))
    frags.append(line(ev_x + isr_w, ry, ev_x + isr_w, ry - 7, color=INK, sw=1.4))
    b, w, h = textbox(ev_x + isr_w / 2, ry + 26,
                      "критичний шлях: фіксований, байдужий до довжини фону",
                      size=11, fill="#ffffff", stroke=INK, sw=1.3)
    frags.append(b)

    render(os.path.join(IMG, "preempt.svg"), W, H, *frags)


# ── Фігура 5: драйвер викреслює області простору можливих структур ───────────
def fig_decision_space():
    W, H = 760, 470
    frags = []
    frags.append(text(W / 2, 30, "Кожен драйвер викреслює свою область простору структур",
                      size=15, bold=True))
    frags.append(text(W / 2, 52, "те, що переживає всіх драйверів одразу, — вузька зона здійсненного",
                      size=12, color=MUTED, italic=True))

    frags.append(rect(50, 70, 660, 370, fill=BG, stroke=INK, sw=1.8))

    # три викреслені (заборонені) області — кожна зі своїм драйвером-причиною
    frags.append(fitbox(80, 105, 300, 95, ["викреслено законом:", "дані поза ЄС"],
                        size=13, fill="#f0f0f0", stroke=POS, sw=1.7))
    frags.append(fitbox(405, 110, 285, 90, ["не тримає 10× пік:", "спільна вузька БД"],
                        size=13, fill="#f0f0f0", stroke=POS, sw=1.7))
    frags.append(fitbox(80, 300, 250, 105, ["заборонено політикою:", "чужий стек"],
                        size=13, fill="#f0f0f0", stroke=POS, sw=1.7))

    # зона здійсненного — зелена
    frags.append(fitbox(375, 300, 305, 105,
                        ["здійсненні структури:", "пережили всіх драйверів"],
                        size=13, fill="#eafaf1", stroke=FIELD, sw=2.2, bold=True))

    render(os.path.join(IMG, "decision-space.svg"), W, H, *frags)


# ── Фігура 6: межа Парето — обидві цілі найкращими одночасно недосяжні ────────
def fig_tradeoff_pareto():
    W, H = 680, 480
    frags = []
    frags.append(text(W / 2, 30, "Межа компромісу: обидві цілі найкращими — недосяжно",
                      size=15, bold=True))

    ox, oy = 95, 395            # початок координат
    frags.append(arrow(ox, oy, 610, oy, color=INK, sw=1.6))   # X →
    frags.append(arrow(ox, oy, ox, 68, color=INK, sw=1.6))    # Y ↑
    frags.append(text(ox - 8, 58, "швидкодія ↑", size=12, color=MUTED, anchor="start"))
    frags.append(text(360, 428, "вартість →", size=12, color=MUTED))

    # межа Парето: дешево-повільно (низ-ліво) → дорого-швидко (верх-право)
    front = [(150, 340), (250, 265), (360, 195), (480, 130)]
    frags.append(polyline(front, color=INK, sw=2.2))
    for (px, py) in front:
        frags.append(circle(px, py, 5, fill=BG, stroke=INK, sw=1.6))

    # обраний баланс — зелена точка C, підпис над нею
    frags.append(circle(360, 195, 7, fill=FIELD, stroke=FIELD, sw=2))
    b, w, h = fit_and_box(360, 168, "обраний баланс", FIELD)
    frags.append(b)

    # домінована точка (дорожче й повільніше за межу)
    frags.append(circle(430, 322, 5, fill="#dddddd", stroke=MUTED, sw=1.5))
    frags.append(text(512, 326, "домінований", size=11, color=MUTED))

    # мрійний недосяжний кут: дешево І швидко (верх-ліво)
    frags.append(minus(150, 112, r=9))
    frags.append(line(163, 112, 235, 112, color=NEG, sw=1.3, dash="3,4"))
    b, w, h = fit_and_box(330, 112, "дешево і швидко — недосяжно", NEG)
    frags.append(b)

    # крайні підписи межі
    b, w, h = fit_and_box(200, 368, "дешево, та повільно", MUTED)
    frags.append(b)
    b, w, h = fit_and_box(540, 118, "дорого, зате швидко", MUTED)
    frags.append(b)

    render(os.path.join(IMG, "tradeoff-pareto.svg"), W, H, *frags)


def fit_and_box(cx, cy, s, stroke):
    """Дрібна рамка-підпис на білому тлі (щоб напис не зливався з лініями)."""
    return textbox(cx, cy, s, size=11, fill="#ffffff", stroke=stroke, sw=1.4, pad=7)


# ── Фігура 7: дерево корисності — куди цілити увагу рев'ю ─────────────────────
def fig_utility_tree():
    W, H = 780, 480
    frags = []
    frags.append(text(W / 2, 30, "Дерево корисності: куди цілити увагу рев'ю",
                      size=15, bold=True))

    gx, gy, cw, ch = 110, 80, 150, 110      # сітка 3×3
    # клітини
    for r in range(3):
        for c in range(3):
            x = gx + c * cw
            y = gy + r * ch
            fill, stroke, sw = BG, "#cccccc", 1.3
            if r == 0 and c == 2:            # важливо + важко
                fill, stroke, sw = "#eafaf1", FIELD, 2.2
            if r == 2 and c == 0:            # дрібно + легко
                fill, stroke, sw = "#f0f0f0", MUTED, 1.4
            frags.append(rect(x, y, cw, ch, fill=fill, stroke=stroke, sw=sw))

    # сценарії в клітинах (кожен у своїй)
    def cell(r, c, s, col=INK):
        x = gx + c * cw
        y = gy + r * ch
        return fitbox(x + 10, y + 22, cw - 20, ch - 44, s, size=12, fill="none",
                      stroke="none", sw=0, color=col)
    frags.append(cell(0, 2, "10× пік\nу пік-дні", FIELD))
    frags.append(cell(0, 1, "відмова вузла —\nбез простою"))
    frags.append(cell(1, 0, "нова валюта\nу звіті"))
    frags.append(cell(2, 0, "колір кнопки\n(шум)", MUTED))

    # підписи важливості (рядки) ліворуч
    frags.append(text(78, 66, "важливість", size=11, bold=True, color=MUTED))
    for r, lab in enumerate(["висока", "середня", "низька"]):
        frags.append(text(100, gy + r * ch + ch / 2 + 4, lab, size=11, color=MUTED, anchor="end"))

    # підписи складності (стовпці) знизу
    for c, lab in enumerate(["низька", "середня", "висока"]):
        frags.append(text(gx + c * cw + cw / 2, gy + 3 * ch + 24, lab, size=11, color=MUTED))
    frags.append(text(gx + 1.5 * cw, gy + 3 * ch + 46, "складність для архітектури",
                      size=11, bold=True, color=MUTED))

    # виноска до зеленого кута
    b, w, h = fit_and_box(gx + 2 * cw + cw / 2, 62, "атакувати першими", FIELD)
    frags.append(b)

    render(os.path.join(IMG, "utility-tree.svg"), W, H, *frags)


# ── Фігура 8: остання відповідальна мить — перетин двох вартостей ─────────────
def fig_lrm():
    W, H = 720, 450
    frags = []
    frags.append(text(W / 2, 30, "Остання відповідальна мить: перетин двох вартостей",
                      size=15, bold=True))

    ox, oy = 90, 370
    frags.append(arrow(ox, oy, 660, oy, color=INK, sw=1.6))   # час →
    frags.append(arrow(ox, oy, ox, 68, color=INK, sw=1.6))    # вартість ↑
    frags.append(text(ox - 8, 58, "вартість ↑", size=12, color=MUTED, anchor="start"))

    now = [(120, 110), (200, 150), (300, 205), (380, 250), (480, 285), (600, 305)]
    defer = [(120, 320), (220, 285), (320, 235), (400, 190), (500, 135), (600, 95)]
    frags.append(polyline(now, color=NEG, sw=2.4))
    frags.append(polyline(defer, color=POS, sw=2.4))

    # вертикаль LRM (обривається нижче підпису, щоб його не перетнути)
    frags.append(line(345, oy, 345, 104, color=INK, sw=1.6, dash="5,5"))
    frags.append(circle(345, 222, 5, fill=INK, stroke=INK, sw=1))
    b, w, h = textbox(345, 84, "остання відповідальна мить", size=12,
                      fill="#ffffff", stroke=INK, sw=1.4, pad=7)
    frags.append(b)

    # підписи кривих (кожен осторонь, поза лініями)
    b, w, h = textbox(185, 92, ["ціна вирішити зараз", "(мало фактів → ризик)"],
                      size=11, fill="#ffffff", stroke=NEG, sw=1.3, pad=7)
    frags.append(b)
    b, w, h = textbox(520, 100, ["ціна зволікання", "(варіанти зачиняються)"],
                      size=11, fill="#ffffff", stroke=POS, sw=1.3, pad=7)
    frags.append(b)

    # підписи зон під віссю
    frags.append(text(200, 392, "зарано: наосліп", size=11, color=NEG))
    frags.append(text(470, 392, "запізно: вибір звузивсь", size=11, color=POS))
    frags.append(text(632, 392, "час →", size=11, color=MUTED))

    render(os.path.join(IMG, "last-responsible-moment.svg"), W, H, *frags)


# ── Фігура 9: трасувальний хребет драйвер → рішення → в'ю → стейкхолдер ───────
def fig_traceability_spine():
    W, H = 860, 290
    frags = []
    frags.append(text(W / 2, 34, "Трасувальний хребет: від драйвера до того, хто його бачить",
                      size=15, bold=True))

    y = 155
    centers = [120, 340, 560, 770]
    labels = ["Драйвер", "Рішення (ADR)", "В'ю (C4 · 4+1)", "Стейкхолдер"]
    cols = [POS, INK, NEG, FIELD]
    edges = []
    boxes = []
    for cx, lab, col in zip(centers, labels, cols):
        b, w, h = textbox(cx, y, lab, size=14, bold=True, min_w=150,
                          fill=FILL, stroke=col, sw=1.9)
        boxes.append(b)
        edges.append((cx - w / 2, cx + w / 2))

    # зворотна стрілка «чому?» згори
    frags.append(arrow(edges[3][1] - 10, 100, edges[0][0] + 10, 100, color=MUTED, sw=1.5))
    frags.append(text(W / 2, 88, "чому? — назад до драйвера", size=12, color=MUTED))

    # прямі стрілки між рамками + підписи над ними
    fwd = ["породжує", "втілюється в", "читає"]
    for i in range(3):
        x1 = edges[i][1] + 4
        x2 = edges[i + 1][0] - 4
        frags.append(arrow(x1, y, x2, y, color=INK, sw=1.7))
        frags.append(text((x1 + x2) / 2, y - 12, fwd[i], size=11, color=MUTED))

    frags.extend(boxes)
    render(os.path.join(IMG, "traceability-spine.svg"), W, H, *frags)


# ── Фігура 10: крива корисності — скільки цінності додає тактика (CBAM) ───────
def fig_utility_curve():
    W, H = 720, 460
    frags = []
    frags.append(text(W / 2, 30, "Крива корисності: скільки цінності додає тактика",
                      size=15, bold=True))

    ox, oy = 95, 380
    frags.append(arrow(ox, oy, 665, oy, color=INK, sw=1.6))   # відгук →
    frags.append(arrow(ox, oy, ox, 70, color=INK, sw=1.6))    # корисність ↑
    frags.append(text(ox + 4, 60, "корисність (0–100)", size=12, color=MUTED, anchor="start"))
    frags.append(text(400, 418, "рівень відгуку (гірше → краще)", size=12, color=MUTED))

    # S-подібна крива корисності: спершу майже задарма, тоді круто, тоді насичення
    curve = [(115, 358), (175, 348), (250, 320), (320, 250),
             (380, 195), (440, 140), (520, 108), (610, 92)]
    frags.append(polyline(curve, color=INK, sw=2.4))

    # поточний рівень (U = 20) і рівень після тактики (U = 80) для сценарію «10× пік»
    xc, yc = 250, 320
    xa, ya = 440, 140
    frags.append(line(xc, oy, xc, yc, color=MUTED, sw=1.3, dash="4,5"))
    frags.append(line(ox, yc, xc, yc, color=MUTED, sw=1.3, dash="4,5"))
    frags.append(circle(xc, yc, 5, fill=BG, stroke=INK, sw=1.7))
    frags.append(text(xc, oy + 18, "поточна", size=11, color=INK))
    frags.append(text(ox - 8, yc + 4, "20", size=11, color=INK, anchor="end"))

    frags.append(line(xa, oy, xa, ya, color=FIELD, sw=1.3, dash="4,5"))
    frags.append(line(ox, ya, xa, ya, color=FIELD, sw=1.3, dash="4,5"))
    frags.append(circle(xa, ya, 6, fill=FIELD, stroke=FIELD, sw=2))
    frags.append(text(xa, oy + 18, "після тактики", size=11, color=FIELD))
    frags.append(text(ox - 8, ya + 4, "80", size=11, color=FIELD, anchor="end"))

    # дужка ΔU між двома рівнями (ліворуч від крутого коліна кривої)
    bx = 205
    frags.append(line(bx, ya, bx, yc, color=INK, sw=1.5))
    frags.append(line(bx - 5, ya, bx + 5, ya, color=INK, sw=1.5))
    frags.append(line(bx - 5, yc, bx + 5, yc, color=INK, sw=1.5))
    b, w, h = textbox(150, (ya + yc) / 2, "ΔU = 60", size=12,
                      fill="#ffffff", stroke=INK, sw=1.4, pad=7)
    frags.append(b)

    # зона насичення — далі відгук майже не додає корисності (золочення)
    frags.append(line(560, 168, 560, 110, color=MUTED, sw=1.2, dash="3,4"))
    b, w, h = textbox(560, 190, ["насичення:", "далі — золочення"],
                      size=11, fill="#ffffff", stroke=MUTED, sw=1.3, pad=6)
    frags.append(b)

    render(os.path.join(IMG, "utility-curve.svg"), W, H, *frags)


# ── Фігура 11: ранжування тактик за ROI під бюджетом ──────────────────────────
def fig_roi_budget():
    W, H = 800, 360
    frags = []
    frags.append(text(W / 2, 30, "Ранжування тактик за віддачею (ROI) під бюджетом",
                      size=15, bold=True))
    frags.append(text(W / 2, 50, "беремо згори вниз, доки вистачає бюджету; збиткові — ніколи",
                      size=12, color=MUTED, italic=True))

    x0 = 300                      # вісь ROI = 0
    scale = 80                    # px на одиницю ROI
    frags.append(line(x0, 78, x0, 300, color=INK, sw=1.5))
    # позначки шкали під віссю
    for k in (0, 1, 2):
        px = x0 + k * scale
        frags.append(line(px, 300, px, 306, color=MUTED, sw=1.2))
        frags.append(text(px, 320, str(k), size=10, color=MUTED))

    # рядки: (назва, вартість, ROI, колір-заливки, колір-рамки, статус, колір-статусу)
    rows = [
        ("шар-провайдер", "12 $k", 2.13, "#eafaf1", FIELD, "фінансуємо", FIELD),
        ("кеш + репліки", "30 $k", 2.10, "#eafaf1", FIELD, "фінансуємо", FIELD),
        ("синхронне перемикання", "40 $k", 0.40, FILL, MUTED, "не влізло в бюджет", MUTED),
        ("мікросервіси", "150 $k", -0.36, "#fdecea", POS, "збиткова — відкинуто", POS),
    ]
    ycs = [100, 160, 220, 278]
    bh = 30
    for (name, cost, roi, fill, stroke, status, scol), ycn in zip(rows, ycs):
        # назва + вартість — колонка ліворуч
        frags.append(text(248, ycn - 3, name, size=11, color=INK, anchor="end"))
        frags.append(text(248, ycn + 13, cost, size=10, color=MUTED, anchor="end"))
        # смуга ROI
        wpx = abs(roi) * scale
        if roi >= 0:
            frags.append(rect(x0, ycn - bh / 2, wpx, bh, fill=fill, stroke=stroke, sw=1.8))
            frags.append(text(x0 + wpx + 8, ycn + 4, "%.2f" % roi, size=12,
                              color=stroke, bold=True, anchor="start"))
        else:
            frags.append(rect(x0 - wpx, ycn - bh / 2, wpx, bh, fill=fill, stroke=stroke, sw=1.8))
            frags.append(text(x0 - wpx - 8, ycn + 4, "−0.36", size=12,
                              color=stroke, bold=True, anchor="end"))
        # статус — колонка праворуч
        frags.append(text(560, ycn + 4, status, size=11, color=scol, anchor="start"))

    frags.append(text(W / 2, 345,
                      "бюджет 45 $k → шар-провайдер (12) + кеш+репліки (30) = 42; "
                      "решта за межею",
                      size=11, color=INK))
    render(os.path.join(IMG, "roi-budget.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_sieve()
    fig_five_kinds()
    fig_budget()
    fig_preempt()
    fig_decision_space()
    fig_tradeoff_pareto()
    fig_utility_tree()
    fig_lrm()
    fig_traceability_spine()
    fig_utility_curve()
    fig_roi_budget()
    print("figures written")
