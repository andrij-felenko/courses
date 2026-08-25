# -*- coding: utf-8 -*-
"""Фігури до статті «Фільтр Кукушки (Cuckoo Filter)».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/. Усі тексти та розмітки сумісні з svgkit та svgcheck.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CW, CH = 52, 32          # розміри комірки одного відбитка
FILLED = "#eaf0fd"       # зайнятий слот
EMPTY  = "#ffffff"       # порожній слот
HIGHLIGHT = "#fdecea"    # слот, куди потрапляє елемент
ACCENT = "#e8f8f0"       # цільовий слот

def slot(x, y, label, w=CW, h=CH, fill=FILLED, stroke=LINE, sw=1.2, tcolor=INK, tsize=12, bold=False):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=3)
    if label != "":
        out += text(x + w / 2, y + h / 2 + tsize * 0.35, label, size=tsize, color=tcolor, bold=bold)
    return out

def draw_bucket(x, y, b_idx, slots, is_active=False, active_color=FIELD):
    out = []
    bw = 4 * CW + 10
    bh = CH + 8
    border_col = active_color if is_active else LINE
    bg_col = "#fafbfc" if not is_active else "#f4faf6"
    sw = 2.0 if is_active else 1.2
    out.append(rect(x, y, bw, bh, fill=bg_col, stroke=border_col, sw=sw, rx=4))
    
    # Номер кошика зліва
    label_col = active_color if is_active else MUTED
    out.append(text(x - 14, y + bh / 2 + 4, f"[{b_idx}]", size=12, color=label_col, anchor="end", bold=is_active))
    
    for s in range(4):
        sx = x + 5 + s * CW
        sy = y + 4
        val = slots[s] if s < len(slots) else ""
        if val == "":
            out.append(slot(sx, sy, "—", fill=EMPTY, tcolor=MUTED))
        else:
            fill_c = HIGHLIGHT if (is_active and "0x" in val) else FILLED
            txt_c = POS if (is_active and "0x" in val) else INK
            out.append(slot(sx, sy, val, fill=fill_c, tcolor=txt_c, bold=is_active))
    return "".join(out)


# ── Фігура 1: Архітектура та часткове зозулине хешування ────────────────────
def fig_architecture():
    W, H = 940, 480
    parts = []

    parts.append(text(W / 2, 28, "Архітектура фільтра Кукушки та часткове зозулине хешування", size=16, bold=True))

    # Лівий блок: вхідний ключ і обчислення хешів
    kx, ky = 70, 70
    kw, kh = 320, 370
    parts.append(rect(kx, ky, kw, kh, fill="#fdfefe", stroke=MUTED, sw=1.0, rx=8))
    parts.append(text(kx + kw / 2, ky + 26, "Обчислення адрес для ключа x", size=14, bold=True))

    # Ключ x
    tb_key, _, _ = textbox(kx + kw / 2, ky + 70, 'Ключ: x = "user_42"', size=13, pad=8, fill="#eaf0fd", stroke=NEG, bold=True)
    parts.append(tb_key)

    # Відбиток
    tb_fp, _, _ = textbox(kx + kw / 2, ky + 140, "f = fingerprint(x) = 0xA3\n(короткий хеш: 8 бітів)", size=12, pad=7, fill="#fff8e7", stroke="#d48806")
    parts.append(tb_fp)

    # Первинний індекс
    tb_i1, _, _ = textbox(kx + kw / 2, ky + 220, "i₁ = hash(x) mod m = 2\n(первинний кошик)", size=12, pad=7, fill="#fdecea", stroke=POS)
    parts.append(tb_i1)

    # Вторинний індекс
    tb_i2, _, _ = textbox(kx + kw / 2, ky + 300, "i₂ = (i₁ ⊕ hash(f)) mod m = 6\n(альтернативний кошик)", size=12, pad=7, fill="#e8f8f0", stroke=FIELD)
    parts.append(tb_i2)

    # Стрілки всередині лівого блоку
    parts.append(arrow(kx + kw / 2, ky + 92, kx + kw / 2, ky + 118, color=MUTED, sw=1.4))
    parts.append(arrow(kx + kw / 2, ky + 168, kx + kw / 2, ky + 198, color=MUTED, sw=1.4))
    parts.append(arrow(kx + kw / 2, ky + 248, kx + kw / 2, ky + 278, color=MUTED, sw=1.4))

    # Симетрія внизу
    parts.append(text(kx + kw / 2, ky + 352, "Симетрія: i₁ = (i₂ ⊕ hash(f)) mod m", size=11, color=MUTED, italic=True))

    # Правий блок: масив кошиків
    bx = 490
    by = 70
    parts.append(text(bx + 110, by + 16, "Масив кошиків T (m = 8, b = 4 слоти на кошик)", size=14, bold=True))

    table_data = [
        ["0x1F", "0x44", "0x9B", "—"],      # 0
        ["0x0C", "0x77", "—", "—"],          # 1
        ["0x12", "0x89", "0xA3", "—"],      # 2 (i1) - активний
        ["0x55", "0x61", "0x90", "0x3E"],    # 3
        ["0xAA", "—", "—", "—"],             # 4
        ["0x23", "0x48", "0xBC", "—"],      # 5
        ["0x31", "—", "—", "—"],             # 6 (i2) - альтернативний
        ["0x7F", "0x88", "0x05", "0x66"]     # 7
    ]

    for idx, slots in enumerate(table_data):
        y_pos = by + 34 + idx * (CH + 14)
        is_i1 = (idx == 2)
        is_i2 = (idx == 6)
        is_act = is_i1 or is_i2
        col = POS if is_i1 else (FIELD if is_i2 else LINE)
        parts.append(draw_bucket(bx, y_pos, idx, slots, is_active=is_act, active_color=col))

    # Стрілки від i1 та i2 до кошиків
    y_target_i1 = by + 34 + 2 * (CH + 14) + (CH + 8) / 2
    y_target_i2 = by + 34 + 6 * (CH + 14) + (CH + 8) / 2
    parts.append(arrow(kx + kw, ky + 220, bx - 35, y_target_i1, color=POS, sw=1.8))
    parts.append(arrow(kx + kw, ky + 300, bx - 35, y_target_i2, color=FIELD, sw=1.8))

    # Підписи пошуку праворуч від стрілок
    parts.append(text(bx + 4 * CW + 35, y_target_i1 + 4, "← Знайдено f = 0xA3 у T[2]", size=12, color=POS, bold=True, anchor="start"))
    parts.append(text(bx + 4 * CW + 35, y_target_i2 + 4, "← Резервний кошик T[6]", size=12, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "cuckoo-filter-architecture.svg"), W, H, *parts)


# ── Фігура 2: Каскадне витіснення (Kicking / Random Walk) ────────────────────
def fig_kicking():
    W, H = 940, 430
    parts = []

    parts.append(text(W / 2, 28, "Каскадне витіснення відбитків (Kicking) під час вставки", size=16, bold=True))

    # Крок 1: Вставка x
    s1_x = 40
    parts.append(text(s1_x + 130, 65, "Крок 1: Вставка нового відбитка", size=13, bold=True))
    parts.append(text(s1_x + 130, 85, "x має f = 0x4B, цілиться в T[1]", size=11.5, color=MUTED))
    parts.append(draw_bucket(s1_x + 25, 105, 1, ["0x11", "0x82", "0x33", "0x44"], is_active=True, active_color=POS))
    parts.append(text(s1_x + 130, 165, "Кошик T[1] повністю заповнений!", size=11.5, color=POS, bold=True))
    parts.append(text(s1_x + 130, 185, "Обираємо жертву: слот 2 (0x82)", size=11, color=MUTED))

    # Стрілка переходу 1 -> 2
    parts.append(arrow(s1_x + 245, 125, s1_x + 295, 125, color=MUTED, sw=2.0))

    # Крок 2: Виштовхування 0x82
    s2_x = 330
    parts.append(text(s2_x + 130, 65, "Крок 2: Заміна та виселення", size=13, bold=True))
    parts.append(text(s2_x + 130, 85, "0x4B займає слот, 0x82 витіснено", size=11.5, color=MUTED))
    parts.append(draw_bucket(s2_x + 25, 105, 1, ["0x11", "0x4B", "0x33", "0x44"], is_active=True, active_color=FIELD))
    parts.append(text(s2_x + 130, 165, "Обчислення альтернативи для 0x82:", size=11.5, color=INK, bold=True))
    parts.append(text(s2_x + 130, 185, "i_alt = 1 ⊕ hash(0x82) = 4", size=12, color=FIELD, bold=True))

    # Стрілка переходу 2 -> 3
    parts.append(arrow(s2_x + 245, 125, s2_x + 295, 125, color=MUTED, sw=2.0))

    # Крок 3: Поселення у вільному гнізді
    s3_x = 620
    parts.append(text(s3_x + 130, 65, "Крок 3: Поселення у кошику T[4]", size=13, bold=True))
    parts.append(text(s3_x + 130, 85, "Перевірка кошика T[4] на наявність місця", size=11.5, color=MUTED))
    parts.append(draw_bucket(s3_x + 25, 105, 4, ["0x7A", "0x9F", "—", "—"], is_active=True, active_color=POS))
    parts.append(text(s3_x + 130, 165, "Знайдено вільний слот 3!", size=11.5, color=FIELD, bold=True))
    parts.append(text(s3_x + 130, 185, "0x82 записується в T[4][2] → Успіх", size=11.5, color=FIELD, bold=True))

    # Нижній пояснювальний блок
    bot_y = 235
    parts.append(rect(40, bot_y, 860, 160, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=6))
    parts.append(text(470, bot_y + 26, "Ключові властивості каскадного витіснення (Kicking Walk)", size=13.5, bold=True))

    pts = [
        "1. Без збереження вихідного ключа: переміщення можливе завдяки XOR-симетрії i_alt = i_curr ⊕ hash(f).",
        "2. Обмеження блукання: лічильник MAX_KICKS (зазвичай 500) запобігає зацикленню при переповненні.",
        "3. Високий коефіцієнт заповнення: кошики розміром b = 4 дозволяють досягати понад 95% заповнення таблиці.",
        "4. Амортизована складність: понад 98% вставок знаходять вільне місце без жодного витіснення (O(1))."
    ]
    for idx, p in enumerate(pts):
        parts.append(text(60, bot_y + 55 + idx * 26, p, size=11.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "cuckoo-filter-kicking.svg"), W, H, *parts)


# ── Фігура 3: Порівняння пам'яті (Cuckoo vs Bloom vs Counting Bloom) ─────────
def fig_memory_comparison():
    W, H = 840, 430
    parts = []

    parts.append(text(W / 2, 28, "Витрати пам'яті (біт/елемент) залежно від хибних спрацьовувань (FPR)", size=16, bold=True))

    ox, oy = 90, 340
    gw, gh = 660, 260

    # Осі
    parts.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    parts.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))

    # Підписи осей
    parts.append(text(ox + gw / 2, oy + 45, "Цільова ймовірність хибного спрацьовування (FPR, ε)", size=13, bold=True))
    parts.append(text(ox - 50, oy - gh / 2, "Біти на елемент (bits / item)", size=13, bold=True, anchor="middle"))

    # Сітка та мітки X (FPR)
    x_ticks = [
        (0.15, "10% (0.1)"),
        (0.40, "3% (0.03)"),
        (0.65, "1% (0.01)"),
        (0.90, "0.1% (0.001)")
    ]
    for rel_x, lbl in x_ticks:
        xp = ox + int(rel_x * gw)
        parts.append(line(xp, oy, xp, oy - gh, color="#e5e7eb", sw=1.0, dash="3,3"))
        parts.append(line(xp, oy, xp, oy + 5, color=LINE, sw=1.5))
        parts.append(text(xp, oy + 20, lbl, size=11, color=MUTED))

    # Сітка та мітки Y (Bits)
    y_ticks = [
        (0, "0"),
        (8, "8"),
        (16, "16"),
        (24, "24"),
        (32, "32"),
        (40, "40")
    ]
    for val, lbl in y_ticks:
        yp = oy - int((val / 42.0) * gh)
        parts.append(line(ox, yp, ox + gw, yp, color="#e5e7eb", sw=1.0, dash="3,3"))
        parts.append(line(ox - 5, yp, ox, yp, color=LINE, sw=1.5))
        parts.append(text(ox - 12, yp + 4, lbl, size=11, color=MUTED, anchor="end"))

    # Лінія Counting Bloom Filter (4-бітні лічильники: ~30-40 бітів)
    cbf_pts = [(0.15, 26), (0.40, 32), (0.65, 38), (0.90, 42)]
    cbf_coords = [(ox + int(rx * gw), oy - int((by / 42.0) * gh)) for rx, by in cbf_pts]
    for i in range(len(cbf_coords) - 1):
        parts.append(line(cbf_coords[i][0], cbf_coords[i][1], cbf_coords[i+1][0], cbf_coords[i+1][1], color=POS, sw=2.5))
    for x, y in cbf_coords:
        parts.append(circle(x, y, 4, fill=POS, stroke=BG, sw=1.5))

    # Лінія Standard Bloom Filter (1.44 * log2(1/e): ~5..15 бітів)
    bf_pts = [(0.15, 4.8), (0.40, 7.3), (0.65, 9.6), (0.90, 14.4)]
    bf_coords = [(ox + int(rx * gw), oy - int((by / 42.0) * gh)) for rx, by in bf_pts]
    for i in range(len(bf_coords) - 1):
        parts.append(line(bf_coords[i][0], bf_coords[i][1], bf_coords[i+1][0], bf_coords[i+1][1], color=MUTED, sw=2.2, dash="4,4"))
    for x, y in bf_coords:
        parts.append(circle(x, y, 4, fill=MUTED, stroke=BG, sw=1.5))

    # Лінія Cuckoo Filter (b=4, f=ceil(log2(2b/e)): ~6..14 бітів)
    cf_pts = [(0.15, 6.3), (0.40, 7.3), (0.65, 8.4), (0.90, 12.6)]
    cf_coords = [(ox + int(rx * gw), oy - int((by / 42.0) * gh)) for rx, by in cf_pts]
    for i in range(len(cf_coords) - 1):
        parts.append(line(cf_coords[i][0], cf_coords[i][1], cf_coords[i+1][0], cf_coords[i+1][1], color=FIELD, sw=3.0))
    for x, y in cf_coords:
        parts.append(circle(x, y, 4.5, fill=FIELD, stroke=BG, sw=1.5))

    # Легенда
    leg_x = ox + 30
    leg_y = 52
    parts.append(rect(leg_x, leg_y, 450, 78, fill="#ffffff", stroke=MUTED, sw=1.0, rx=5))
    
    # CBF
    parts.append(line(leg_x + 15, leg_y + 16, leg_x + 45, leg_y + 16, color=POS, sw=2.5))
    parts.append(circle(leg_x + 30, leg_y + 16, 3.5, fill=POS, stroke=BG, sw=1.0))
    parts.append(text(leg_x + 55, leg_y + 20, "Підрахунковий фільтр Блума (CBF, 4-бітні лічильники)", size=11, color=INK, anchor="start"))

    # Bloom
    parts.append(line(leg_x + 15, leg_y + 38, leg_x + 45, leg_y + 38, color=MUTED, sw=2.0, dash="4,4"))
    parts.append(circle(leg_x + 30, leg_y + 38, 3.5, fill=MUTED, stroke=BG, sw=1.0))
    parts.append(text(leg_x + 55, leg_y + 42, "Стандартний фільтр Блума (без підтримки видалення)", size=11, color=INK, anchor="start"))

    # Cuckoo
    parts.append(line(leg_x + 15, leg_y + 60, leg_x + 45, leg_y + 60, color=FIELD, sw=3.0))
    parts.append(circle(leg_x + 30, leg_y + 60, 4.0, fill=FIELD, stroke=BG, sw=1.0))
    parts.append(text(leg_x + 55, leg_y + 64, "Фільтр Кукушки (b = 4, підтримка видалення + 2 кеш-лінії)", size=11, color=FIELD, bold=True, anchor="start"))

    # Зона виграшу: розміщуємо у правому верхньому куті, де немає ліній сітки
    tb_win, _, _ = textbox(ox + 550, 85, "Точка переваги (FPR < 3%):\nКукушка компактніша за Блум\nі в 3-4 рази менша за CBF", size=10.5, pad=6, fill="#e8f8f0", stroke=FIELD)
    parts.append(tb_win)

    render(os.path.join(IMG, "cuckoo-vs-bloom-memory.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_architecture()
    fig_kicking()
    fig_memory_comparison()
    print("Фігури успішно згенеровано.")
