# -*- coding: utf-8 -*-
"""Фігури до статті «Ковзний хеш (rolling hash)».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def cell_box(x, y, label, w=44, h=44, fill=FILL, stroke=LINE, sw=1.5, tcolor=INK, tsize=16, bold=False):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=5)
    if label != "":
        out += text(x + w / 2, y + h / 2 + tsize * 0.35, label, size=tsize, color=tcolor, bold=bold)
    return out


# ── Фігура 1: Концепція ковзного вікна ──────────────────────────────────────
def fig_rolling_window():
    W, H = 860, 360
    parts = []

    # Заголовок
    parts.append(text(W / 2, 32, "Механіка ковзного хешу: зсув вікна за O(1)", size=17, bold=True))

    # Стрічка символів: "A L G O R I T H M S"
    chars = ["A", "L", "G", "O", "R", "I", "T", "H", "M", "S"]
    sx, sy = 120, 80
    cw, ch = 48, 48

    for i, ch_val in enumerate(chars):
        x = sx + i * (cw + 6)
        if i == 1: # 'L' - вибуває
            fill_c = "#fdecea"
            stk_c = POS
            txt_c = POS
        elif i in (2, 3, 4): # 'G', 'O', 'R' - залишаються
            fill_c = "#eaf0fd"
            stk_c = NEG
            txt_c = INK
        elif i == 5: # 'I' - прибуває
            fill_c = "#eafaf1"
            stk_c = FIELD
            txt_c = FIELD
        else:
            fill_c = BG
            stk_c = MUTED
            txt_c = MUTED

        parts.append(cell_box(x, sy, ch_val, w=cw, h=ch, fill=fill_c, stroke=stk_c, sw=1.8, tcolor=txt_c, bold=True))
        parts.append(text(x + cw / 2, sy - 12, str(i), size=12, color=MUTED))

    # Рамка для старого вікна
    old_w_x = sx + 1 * (cw + 6) - 4
    old_w_w = 4 * (cw + 6) + 2
    parts.append(rect(old_w_x, sy - 5, old_w_w, ch + 10, fill="none", stroke=POS, sw=1.5, rx=6))
    parts.append(text(old_w_x + 60, sy + ch + 22, "Старе вікно: \"LGOR\"", size=13, color=POS, bold=True))

    # Рамка для нового вікна
    new_w_x = sx + 2 * (cw + 6) - 4
    new_w_w = 4 * (cw + 6) + 2
    parts.append(rect(new_w_x, sy - 9, new_w_w, ch + 18, fill="none", stroke=FIELD, sw=1.5, rx=8))
    parts.append(text(new_w_x + new_w_w - 60, sy + ch + 22, "Нове вікно: \"GORI\"", size=13, color=FIELD, bold=True))

    # Схема математичного оновлення хешу нижче
    box_y = 200
    parts.append(rect(60, box_y, W - 120, 125, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    parts.append(text(W / 2, box_y + 26, "Обчислення нового хешу без повного перерахунку:", size=14, bold=True))

    # Крок 1: віднімаємо L
    parts.append(text(190, box_y + 56, "1. Віднімаємо 'L' · B³", size=13, color=POS, bold=True))

    # Крок 2: множимо на B
    parts.append(text(430, box_y + 56, "2. Зсуваємо розряди (× B)", size=13, color=NEG, bold=True))

    # Крок 3: додаємо I
    parts.append(text(670, box_y + 56, "3. Додаємо новий 'I'", size=13, color=FIELD, bold=True))

    # Підсумкова формула
    parts.append(text(W / 2, box_y + 100, "H_new = ( (H_old − s[i] · Bᵏ⁻¹) · B + s[i+k] ) mod P", size=15, bold=True, color=INK))

    path = os.path.join(IMG, 'rolling-window-concept.svg')
    return render(path, W, H, "\n".join(parts))


# ── Фігура 2: Пошук підрядка за алгоритмом Рабіна-Карпа ─────────────────────
def fig_rabin_karp():
    W, H = 840, 360
    parts = []

    parts.append(text(W / 2, 30, "Алгоритм Рабіна-Карпа: фільтрація вікон за хешем", size=17, bold=True))

    # Шаблон і його хеш
    parts.append(rect(50, 60, 740, 50, fill="#f0f4fe", stroke=NEG, sw=1.5, rx=6))
    parts.append(text(180, 90, "Шаблон (Pattern): \"CAT\"", size=14, bold=True, color=NEG))
    parts.append(text(580, 90, "Хеш шаблону: H(pattern) = 8412", size=14, bold=True, color=INK))

    # Порівняння вікон у тексті
    y_start = 140
    rows = [
        ("Вікно 0: \"THE\"", "H = 1923", "1923 ≠ 8412", "Нічого (пропускаємо)", MUTED, BG),
        ("Вікно 1: \"HE \"", "H = 5011", "5011 ≠ 8412", "Нічого (пропускаємо)", MUTED, BG),
        ("Вікно 2: \"CAT\"", "H = 8412", "8412 == 8412", "Збіг хешу! Посимвольна перевірка → УСПІХ", FIELD, "#eafaf1"),
        ("Вікно 3: \"ATC\"", "H = 8412", "8412 == 8412", "Колізія! Перевірка: \"ATC\" ≠ \"CAT\" (хибне)", POS, "#fdecea")
    ]

    for idx, (win_title, win_hash, comp_res, action_txt, color_theme, bg_color) in enumerate(rows):
        ry = y_start + idx * 48
        parts.append(rect(50, ry, 740, 42, fill=bg_color, stroke=color_theme, sw=1.2, rx=5))

        parts.append(text(120, ry + 26, win_title, size=13, bold=True, anchor="start"))
        parts.append(text(300, ry + 26, win_hash, size=13, anchor="start", color=INK))
        parts.append(text(430, ry + 26, comp_res, size=13, bold=True, anchor="start", color=color_theme))
        parts.append(text(580, ry + 26, action_txt, size=12.5, bold=True, anchor="start", color=color_theme))

    path = os.path.join(IMG, 'rabin-karp-search.svg')
    return render(path, W, H, "\n".join(parts))


# ── Фігура 3: Дедуплікація та Content-Defined Chunking (CDC) ─────────────────
def fig_rsync_cdc():
    W, H = 860, 400
    parts = []

    parts.append(text(W / 2, 28, "Порівняння підходів до чанкінгу при дедуплікації даних", size=17, bold=True))

    # Верхня частина: Фіксований розмір блоків (Fixed-size chunking)
    parts.append(text(60, 62, "1. Фіксований поділ (Fixed-size Chunking) — чутливий до зсуву:", size=14, bold=True, anchor="start"))

    fy1 = 82
    parts.append(text(60, fy1 + 22, "Оригінал:", size=12.5, anchor="start", color=MUTED))
    colors_a = ["#dbeafe", "#bfdbfe", "#93c5fd", "#60a5fa"]
    for i in range(4):
        parts.append(rect(140 + i * 150, fy1, 144, 34, fill=colors_a[i], stroke=NEG, sw=1.2, rx=4))
        parts.append(text(140 + i * 150 + 72, fy1 + 22, f"Блок A{i+1}", size=13, bold=True))

    fy2 = 130
    parts.append(text(60, fy2 + 22, "+1 байт:", size=12.5, anchor="start", color=POS))
    for i in range(4):
        parts.append(rect(140 + i * 150, fy2, 144, 34, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
        parts.append(text(140 + i * 150 + 72, fy2 + 22, f"Змінено! ({i+1})", size=12, color=POS, bold=True))
    parts.append(text(W - 40, fy2 + 22, "0% збігів!", size=13, bold=True, color=POS, anchor="end"))

    # Розділювач
    parts.append(line(50, 185, W - 50, 185, color=MUTED, sw=1, dash="4,4"))

    # Нижня частина: Поділ за вмістом (Content-Defined Chunking)
    parts.append(text(60, 215, "2. Поділ за вмістом (CDC з ковзним хешем) — стійкий до зсуву:", size=14, bold=True, anchor="start"))

    fy3 = 238
    parts.append(text(60, fy3 + 22, "Оригінал:", size=12.5, anchor="start", color=MUTED))
    widths_cdc = [120, 190, 110, 160]
    x_acc = 140
    for i, w in enumerate(widths_cdc):
        parts.append(rect(x_acc, fy3, w - 6, 34, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
        parts.append(text(x_acc + (w - 6) / 2, fy3 + 22, f"Блок B{i+1}", size=13, bold=True, color=FIELD))
        if i < 3:
            parts.append(line(x_acc + w - 3, fy3 - 4, x_acc + w - 3, fy3 + 38, color=FIELD, sw=2, dash="2,2"))
        x_acc += w

    fy4 = 300
    parts.append(text(60, fy4 + 22, "+1 байт:", size=12.5, anchor="start", color=FIELD))
    x_acc = 140
    parts.append(rect(x_acc, fy4, 126 - 6, 34, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    parts.append(text(x_acc + 60, fy4 + 22, "Блок B1'", size=12.5, bold=True, color=POS))
    x_acc += 126

    widths_cdc_b = [190, 110, 160]
    for i, w in enumerate(widths_cdc_b):
        parts.append(rect(x_acc, fy4, w - 6, 34, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
        parts.append(text(x_acc + (w - 6) / 2, fy4 + 22, f"Блок B{i+2}", size=13, bold=True, color=FIELD))
        x_acc += w

    parts.append(text(W - 40, fy4 + 22, "75% збігів!", size=13, bold=True, color=FIELD, anchor="end"))
    parts.append(text(W / 2, 375, "Межа блоку спрацьовує коли H(вікно) mod S == 0 (маркер вмісту)", size=12.5, color=MUTED, italic=True))

    path = os.path.join(IMG, 'rsync-cdc-chunking.svg')
    return render(path, W, H, "\n".join(parts))


if __name__ == '__main__':
    fig_rolling_window()
    fig_rabin_karp()
    fig_rsync_cdc()
    print("Фігури ковзного хешу успішно згенеровано.")
