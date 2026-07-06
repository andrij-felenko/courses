# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


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


if __name__ == "__main__":
    fig_sieve()
    fig_five_kinds()
    fig_budget()
    fig_preempt()
    print("figures written")
