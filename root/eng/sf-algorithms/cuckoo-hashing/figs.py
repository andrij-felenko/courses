# -*- coding: utf-8 -*-
"""Фігури до статті «Хешування зозулею (Cuckoo Hashing)».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/. Усі тексти та розмітки сумісні з svgkit та svgcheck.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CW, CH = 64, 34          # ширина/висота комірки
FILLED = "#eaf0fd"       # зайнята комірка
EMPTY  = BG              # порожня комірка
DISPL  = "#fdecea"       # комірка витіснення (червонувата)
TARGET = "#e8f8f0"       # цільова вільна комірка (зеленкувата)


def cell(x, y, label, w=CW, h=CH, fill=FILL, stroke=LINE, sw=1.5, tcolor=INK, tsize=13, bold=False):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4)
    if label != "":
        out += text(x + w / 2, y + h / 2 + tsize * 0.35, label, size=tsize, color=tcolor, bold=bold)
    return out


# ── Фігура 1: Пошук та ланцюжок витіснення ──────────────────────────────────
def fig_lookup_and_eviction():
    W, H = 960, 470
    parts = []

    # Заголовки панелей
    parts.append(text(240, 32, "Пошук: гарантовано ≤ 2 звернення", size=16, bold=True))
    parts.append(text(720, 32, "Вставка: ланцюжок витіснення (eviction)", size=16, bold=True))
    parts.append(line(480, 20, 480, 450, color=MUTED, sw=1, dash="4,4"))

    # ── Ліва панель: Пошук ──
    # Опис угорі
    parts.append(text(240, 58, "Ключ x перевіряє ТІЛЬКИ дві фіксовані комірки", size=12, color=MUTED))

    # Масив T1
    parts.append(text(130, 85, "Таблиця T₁", size=14, bold=True))
    parts.append(text(130, 102, "h₁(x) = 2", size=12, color=NEG))
    t1_x, t1_y = 100, 115
    for i in range(6):
        y = t1_y + i * (CH + 6)
        parts.append(text(t1_x - 14, y + CH / 2 + 4, str(i), size=11, color=MUTED, anchor="end"))
        if i == 2:
            parts.append(cell(t1_x, y, "інший", fill=DISPL, tcolor=POS, bold=True))
        elif i == 0:
            parts.append(cell(t1_x, y, "k_a", fill=FILLED))
        elif i == 4:
            parts.append(cell(t1_x, y, "k_b", fill=FILLED))
        else:
            parts.append(cell(t1_x, y, "—", fill=EMPTY, tcolor=MUTED))

    # Масив T2
    parts.append(text(350, 85, "Таблиця T₂", size=14, bold=True))
    parts.append(text(350, 102, "h₂(x) = 4", size=12, color=FIELD))
    t2_x, t2_y = 320, 115
    for i in range(6):
        y = t2_y + i * (CH + 6)
        parts.append(text(t2_x - 14, y + CH / 2 + 4, str(i), size=11, color=MUTED, anchor="end"))
        if i == 4:
            parts.append(cell(t2_x, y, "x", fill=TARGET, tcolor=FIELD, bold=True))
        elif i == 1:
            parts.append(cell(t2_x, y, "k_c", fill=FILLED))
        elif i == 3:
            parts.append(cell(t2_x, y, "k_d", fill=FILLED))
        else:
            parts.append(cell(t2_x, y, "—", fill=EMPTY, tcolor=MUTED))

    # Вхідний запит пошуку
    parts.append(rect(190, 370, 100, 36, fill="#fff8e7", stroke="#d48806", sw=1.5, rx=5))
    parts.append(text(240, 393, "Пошук(x)", size=13, bold=True, color="#873800"))

    # Стрілки пошуку
    parts.append(arrow(215, 370, t1_x + CW + 4, t1_y + 2 * (CH + 6) + CH / 2, color=NEG, sw=1.6))
    parts.append(arrow(265, 370, t2_x - 4, t2_y + 4 * (CH + 6) + CH / 2, color=FIELD, sw=1.6))

    parts.append(text(240, 435, "Якщо x немає в T₁[2] і T₂[4] — його немає взагалі", size=11.5, color=MUTED))

    # ── Права панель: Вставка та витіснення ──
    parts.append(text(720, 58, "Вставка x: покрокове виштовхування до вільного гнізда", size=12, color=MUTED))

    p1_x, p1_y = 580, 115
    p2_x, p2_y = 800, 115

    parts.append(text(610, 85, "Таблиця T₁", size=14, bold=True))
    parts.append(text(830, 85, "Таблиця T₂", size=14, bold=True))

    for i in range(6):
        y1 = p1_y + i * (CH + 6)
        parts.append(text(p1_x - 14, y1 + CH / 2 + 4, str(i), size=11, color=MUTED, anchor="end"))
        if i == 1:
            parts.append(cell(p1_x, y1, "x", fill=TARGET, tcolor=FIELD, bold=True))
        elif i == 4:
            parts.append(cell(p1_x, y1, "k_c", fill=TARGET, tcolor=FIELD, bold=True))
        else:
            parts.append(cell(p1_x, y1, "—", fill=EMPTY, tcolor=MUTED))

        y2 = p2_y + i * (CH + 6)
        parts.append(text(p2_x - 14, y2 + CH / 2 + 4, str(i), size=11, color=MUTED, anchor="end"))
        if i == 3:
            parts.append(cell(p2_x, y2, "k_b", fill=TARGET, tcolor=FIELD, bold=True))
        else:
            parts.append(cell(p2_x, y2, "—", fill=EMPTY, tcolor=MUTED))

    # Стрілки кроків витіснення
    # Крок 1: x вселяється в T1[1], витісняючи k_b
    parts.append(rect(495, 140, 70, 26, fill="#fff8e7", stroke="#d48806", sw=1.2, rx=4))
    parts.append(text(530, 157, "1. Вхід x", size=11, bold=True, color="#873800"))
    parts.append(arrow(565, 153, p1_x - 4, p1_y + 1 * (CH + 6) + CH / 2, color=POS, sw=1.6))

    # Крок 2: k_b витіснений з T1[1], переміщується в T2[3]
    y_k1 = p1_y + 1 * (CH + 6) + CH / 2
    y_k2 = p2_y + 3 * (CH + 6) + CH / 2
    parts.append(arrow(p1_x + CW + 4, y_k1, p2_x - 4, y_k2, color=POS, sw=1.8))
    parts.append(text(720, y_k1 + 8, "2. k_b → T₂[3]", size=11, bold=True, color=POS))

    # Крок 3: k_c витіснений з T2[3], переміщується в T1[4]
    y_k3 = p1_y + 4 * (CH + 6) + CH / 2
    parts.append(arrow(p2_x - 4, y_k2 + 8, p1_x + CW + 4, y_k3, color=FIELD, sw=1.8))
    parts.append(text(720, y_k3 - 8, "3. k_c → T₁[4] (вільно!)", size=11, bold=True, color=FIELD))

    parts.append(text(720, 395, "Ланцюжок зупинився: знайдено вільне місце в T₁[4]", size=12, bold=True, color=FIELD))
    parts.append(text(720, 435, "Якщо утворюється цикл витіснення → виконується перехешування (rehash)", size=11.5, color=MUTED))

    render(os.path.join(IMG, "cuckoo-lookup-and-eviction.svg"), W, H, *parts)


# ── Фігура 2: Граф зозулі та фазовий перехід ────────────────────────────────
def fig_cuckoo_graph_cycles():
    W, H = 960, 460
    parts = []

    parts.append(text(240, 32, "Успіх: дерево або 1 простий цикл", size=16, bold=True))
    parts.append(text(720, 32, "Колізія: 2 цикли (біциклічний компонент)", size=16, bold=True))
    parts.append(line(480, 20, 480, 440, color=MUTED, sw=1, dash="4,4"))

    # ── Ліва панель: Коректний двочастковий граф ──
    parts.append(text(240, 58, "Кожен ключ — ребро між слотами T₁ і T₂. Ребер ≤ Вершин", size=12, color=MUTED))

    # Вершини лівої частки (T1)
    lx1, lx2 = 120, 360
    ly = [110, 180, 250, 320]

    parts.append(text(lx1, 85, "Слоти T₁", size=13, bold=True))
    parts.append(text(lx2, 85, "Слоти T₂", size=13, bold=True))

    for i in range(4):
        parts.append(circle(lx1, ly[i], 18, fill=FILLED, stroke=NEG, sw=1.6))
        parts.append(text(lx1, ly[i] + 4, f"u{i}", size=12, bold=True, color=NEG))

        parts.append(circle(lx2, ly[i], 18, fill=FILLED, stroke=FIELD, sw=1.6))
        parts.append(text(lx2, ly[i] + 4, f"v{i}", size=12, bold=True, color=FIELD))

    # Орієнтовані ребра (ключі): in-degree <= 1
    # Ребро e1: u0 -> v0 (ключ k1 в v0)
    parts.append(arrow(lx1 + 18, ly[0], lx2 - 18, ly[0], color=INK, sw=1.5))
    parts.append(text(240, ly[0] - 8, "k₁", size=11, bold=True))

    # Ребро e2: u1 -> v1 (ключ k2 в v1)
    parts.append(arrow(lx1 + 18, ly[1], lx2 - 18, ly[1], color=INK, sw=1.5))
    parts.append(text(200, ly[1] - 8, "k₂", size=11, bold=True))

    # Ребро e3: v1 -> u2 (ключ k3 в u2)
    parts.append(arrow(lx2 - 18, ly[1] + 6, lx1 + 18, ly[2] - 6, color=INK, sw=1.5))
    parts.append(text(280, ly[1] + 32, "k₃", size=11, bold=True))

    # Ребро e4: u2 -> v2 (ключ k4 в v2)
    parts.append(arrow(lx1 + 18, ly[2] + 4, lx2 - 18, ly[2] + 4, color=INK, sw=1.5))
    parts.append(text(240, ly[2] + 20, "k₄", size=11, bold=True))

    # Ребро e5: v2 -> u1 (ключ k5 в u1) — замикає цикл (u1, v1, u2, v2)
    parts.append(arrow(lx2 - 18, ly[2] - 6, lx1 + 18, ly[1] + 6, color=INK, sw=1.5))
    parts.append(text(200, ly[2] - 25, "k₅", size=11, bold=True))

    parts.append(text(240, 390, "Компонент: 4 вершини, 4 ребра (1 цикл)", size=12, bold=True, color=FIELD))
    parts.append(text(240, 415, "Орієнтація можлива: кожен слот містить ≤ 1 ключ", size=11.5, color=MUTED))

    # ── Права панель: Біциклічний граф (глухий кут) ──
    parts.append(text(720, 58, "Ребер більше, ніж вершин (|E| > |V|). Замкнена пастка", size=12, color=MUTED))

    rx1, rx2 = 600, 840
    ry = [110, 180, 250, 320]

    parts.append(text(rx1, 85, "Слоти T₁", size=13, bold=True))
    parts.append(text(rx2, 85, "Слоти T₂", size=13, bold=True))

    for i in range(4):
        parts.append(circle(rx1, ry[i], 18, fill=FILLED, stroke=NEG, sw=1.6))
        parts.append(text(rx1, ry[i] + 4, f"u{i}", size=12, bold=True, color=NEG))

        parts.append(circle(rx2, ry[i], 18, fill=FILLED, stroke=FIELD, sw=1.6))
        parts.append(text(rx2, ry[i] + 4, f"v{i}", size=12, bold=True, color=FIELD))

    # 4 вершини {u0, u1, v0, v1}, але 5 ключів (2 цикли)
    parts.append(arrow(rx1 + 18, ry[0], rx2 - 18, ry[0], color=POS, sw=1.6))
    parts.append(text(720, ry[0] - 8, "k₁", size=11, bold=True, color=POS))

    parts.append(arrow(rx2 - 18, ry[0] + 6, rx1 + 18, ry[1] - 6, color=POS, sw=1.6))
    parts.append(text(760, ry[0] + 32, "k₂", size=11, bold=True, color=POS))

    parts.append(arrow(rx1 + 18, ry[1], rx2 - 18, ry[1], color=POS, sw=1.6))
    parts.append(text(720, ry[1] + 16, "k₃", size=11, bold=True, color=POS))

    parts.append(arrow(rx2 - 18, ry[1] - 6, rx1 + 18, ry[0] + 6, color=POS, sw=1.6))
    parts.append(text(680, ry[1] - 25, "k₄", size=11, bold=True, color=POS))

    # 5-й ключ k_extra між u0 та v1: утворює другий цикл
    parts.append(line(rx1 + 18, ry[0] + 12, rx2 - 18, ry[1] + 12, color=POS, sw=2, dash="3,3"))
    parts.append(text(720, ry[0] + 70, "k_extra (конфлікт!)", size=11, bold=True, color=POS))

    parts.append(text(720, 390, "4 слоти не можуть вмістити 5 ключів", size=12, bold=True, color=POS))
    parts.append(text(720, 415, "Нескінченне витіснення → поріг перехешування", size=11.5, color=MUTED))

    render(os.path.join(IMG, "cuckoo-graph-cycles.svg"), W, H, *parts)


# ── Фігура 3: Блокове хешування та схованка (Stash) ─────────────────────────
def fig_bucketized_cuckoo():
    W, H = 960, 440
    parts = []

    parts.append(text(W / 2, 28, "Блокове хешування (b = 4 слоти на кошик) та схованка (Stash)", size=16, bold=True))
    parts.append(text(W / 2, 52, "Один кошик = один кеш-рядок (64 байти). Коефіцієнт заповнення α зростає з 50% до 95%+", size=12.5, color=MUTED))

    # Таблиця T1: кошики з 4 слотів
    t1_x, t1_y = 120, 100
    parts.append(text(t1_x + 130, t1_y - 12, "Таблиця T₁ (Кошики по 4 комірки)", size=13, bold=True))

    bw, bh = 260, 36
    sw = bw / 4
    for b in range(4):
        by = t1_y + b * (bh + 14)
        parts.append(text(t1_x - 16, by + bh / 2 + 4, f"B{b}", size=11, color=MUTED, anchor="end"))
        is_target = (b == 1)
        fill = TARGET if is_target else FILL
        parts.append(rect(t1_x, by, bw, bh, fill=fill, stroke=LINE, sw=1.4, rx=4))
        for s in range(4):
            sx = t1_x + s * sw
            if s > 0:
                parts.append(line(sx, by, sx, by + bh, color=MUTED, sw=1))
            lbl = "k_1" if (b == 1 and s == 0) else ("k_2" if (b == 1 and s == 1) else ("вільно" if (b == 1 and s >= 2) else "запис"))
            tc = FIELD if (b == 1 and s >= 2) else (POS if (b == 1 and s < 2) else INK)
            parts.append(text(sx + sw / 2, by + bh / 2 + 4, lbl, size=11, color=tc))

    # Таблиця T2: кошики з 4 слотів
    t2_x, t2_y = 560, 100
    parts.append(text(t2_x + 130, t2_y - 12, "Таблиця T₂ (Кошики по 4 комірки)", size=13, bold=True))

    for b in range(4):
        by = t2_y + b * (bh + 14)
        parts.append(text(t2_x - 16, by + bh / 2 + 4, f"B{b}", size=11, color=MUTED, anchor="end"))
        is_target = (b == 3)
        fill = TARGET if is_target else FILL
        parts.append(rect(t2_x, by, bw, bh, fill=fill, stroke=LINE, sw=1.4, rx=4))
        for s in range(4):
            sx = t2_x + s * sw
            if s > 0:
                parts.append(line(sx, by, sx, by + bh, color=MUTED, sw=1))
            lbl = "k_a" if (b == 3 and s == 0) else ("вільно" if (b == 3 and s >= 1) else "запис")
            tc = FIELD if (b == 3 and s >= 1) else (POS if (b == 3 and s == 0) else INK)
            parts.append(text(sx + sw / 2, by + bh / 2 + 4, lbl, size=11, color=tc))

    # Запит і стрілки вибору
    parts.append(rect(420, 310, 120, 34, fill="#fff8e7", stroke="#d48806", sw=1.5, rx=5))
    parts.append(text(480, 332, "Ключ x (h₁, h₂)", size=12, bold=True, color="#873800"))

    parts.append(arrow(430, 310, t1_x + bw + 4, t1_y + 1 * (bh + 14) + bh / 2, color=NEG, sw=1.6))
    parts.append(arrow(530, 310, t2_x - 4, t2_y + 3 * (bh + 14) + bh / 2, color=FIELD, sw=1.6))

    parts.append(text(480, 270, "8 слотів-кандидатів (4 + 4)", size=11.5, bold=True, color=INK))

    # Схованка (Stash) унизу
    st_x, st_y = 280, 375
    st_w, st_h = 400, 34
    st_slot = st_w / 4
    parts.append(text(st_x - 20, st_y + st_h / 2 + 4, "Схованка (Stash):", size=12, bold=True, anchor="end"))
    parts.append(rect(st_x, st_y, st_w, st_h, fill="#fff0f6", stroke="#c41d7f", sw=1.4, rx=4))
    for s in range(4):
        sx = st_x + s * st_slot
        if s > 0:
            parts.append(line(sx, st_y, sx, st_y + st_h, color="#eb2f96", sw=1))
        lbl = "виняток 1" if s == 0 else "вільно"
        tc = "#c41d7f" if s == 0 else MUTED
        parts.append(text(sx + st_slot / 2, st_y + st_h / 2 + 4, lbl, size=11, color=tc))

    parts.append(text(W / 2, 428, "Схованка на s = 4 елементи знижує ймовірність перехешування з O(1/n) до O(1/n⁴)", size=11.5, color=MUTED))

    render(os.path.join(IMG, "bucketized-cuckoo.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_lookup_and_eviction()
    fig_cuckoo_graph_cycles()
    fig_bucketized_cuckoo()
    print("All figures generated successfully.")
