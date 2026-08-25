# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Фільтр Блума» (bloom-filter)."""

import os
import sys

# Підключення svgkit із кореня репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_bloom_lookup():
    """Фігура 1: Принцип роботи фільтра Блума — запис двох ключів і перевірка двох запитів."""
    dw = 1040
    dh = 460
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (dw, dh, dw, dh),
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % LINE,
        '  </marker>',
        '  <marker id="arrow-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % FIELD,
        '  </marker>',
        '  <marker id="arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % POS,
        '  </marker>',
        '  <marker id="arrow-blue" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % NEG,
        '  </marker>',
        '</defs>',
        '<rect width="100%%" height="100%%" fill="%s"/>' % BG,
    ]

    # Заголовки секцій
    out.append(text(250, 25, "1. Додавання ключів у фільтр", size=15, bold=True, color=INK))
    out.append(text(780, 25, "2. Перевірка наявності ключів", size=15, bold=True, color=INK))

    # Розділювач вертикальний пунктир
    out.append(line(510, 15, 510, 445, color=MUTED, sw=1.2, dash="4,4"))

    # Ліва частина: Запис ключів
    b1, _, _ = textbox(140, 65, 'Ключ X ("user_102")', size=12, bold=True, fill="#eef2f7", stroke=NEG)
    b2, _, _ = textbox(360, 65, 'Ключ Y ("order_841")', size=12, bold=True, fill="#fcedec", stroke=POS)
    out.append(b1)
    out.append(b2)

    # Геш-функції ліворуч (багаторядкові, компактні)
    b_hx, _, _ = textbox(140, 125, "h₁(X) = 1\nh₂(X) = 5\nh₃(X) = 11", size=11, fill="#eef2f7", stroke=NEG)
    b_hy, _, _ = textbox(360, 125, "h₁(Y) = 5\nh₂(Y) = 8\nh₃(Y) = 14", size=11, fill="#fcedec", stroke=POS)
    out.append(b_hx)
    out.append(b_hy)

    out.append(arrow(140, 82, 140, 98, color=NEG))
    out.append(arrow(360, 82, 360, 98, color=POS))

    # Бітовий масив ліворуч
    cell_w = 26
    cell_h = 30
    start_x = 42
    y_cells = 220

    bits_val = [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]
    for i in range(16):
        cx = start_x + i * cell_w
        is_set = bits_val[i] == 1
        fill_c = "#d4edda" if is_set else "#ffffff"
        border_c = FIELD if is_set else LINE
        sw_c = 1.8 if is_set else 1.0
        out.append(rect(cx, y_cells, cell_w, cell_h, fill=fill_c, stroke=border_c, sw=sw_c, rx=2))
        out.append(text(cx + cell_w / 2, y_cells + 19, str(bits_val[i]), size=13, bold=is_set, color=FIELD if is_set else MUTED))
        out.append(text(cx + cell_w / 2, y_cells + 44, str(i), size=10, color=MUTED))

    # Підпис масиву знизу під індексами
    out.append(text(250, 280, "Бітовий масив m=16 розрядів (усі біти спочатку 0)", size=11, bold=True, color=INK))

    # Стрілки запису від блоків гешів до бітового масиву
    out.append(arrow(105, 155, start_x + 1 * cell_w + 13, y_cells - 4, color=NEG))
    out.append(arrow(140, 155, start_x + 5 * cell_w + 8, y_cells - 4, color=NEG))
    out.append(arrow(175, 155, start_x + 11 * cell_w + 8, y_cells - 4, color=NEG))

    out.append(arrow(325, 155, start_x + 5 * cell_w + 18, y_cells - 4, color=POS))
    out.append(arrow(360, 155, start_x + 8 * cell_w + 13, y_cells - 4, color=POS))
    out.append(arrow(395, 155, start_x + 14 * cell_w + 13, y_cells - 4, color=POS))

    # Пояснення ліворуч знизу
    b_l_desc, _, _ = textbox(250, 365, "Результат запису:\n• Ключ X встановив біти: 1, 5, 11\n• Ключ Y встановив біти: 5, 8, 14\n(Біт 5 став спільним внаслідок геш-колізії)", size=11, fill="#f4f6f8", stroke=LINE)
    out.append(b_l_desc)

    # Права частина: Запити перевірки
    # Запит 1: Ключ Z1 (True Negative)
    b_q1, _, _ = textbox(640, 65, 'Запит Z₁ ("guest_99")', size=12, bold=True, fill="#ffffff", stroke=LINE)
    out.append(b_q1)
    b_qz1, _, _ = textbox(640, 130, "h₁(Z₁) = 1  → біт 1 = 1\nh₂(Z₁) = 3  → біт 3 = 0 (СТОП!)\nh₃(Z₁) = 8  → біт 8 = 1", size=11, fill="#fff8f8", stroke=POS)
    out.append(b_qz1)
    out.append(arrow(640, 82, 640, 102, color=LINE))

    b_res1, _, _ = textbox(640, 235, "Біт 3 = 0 ⇒ ГАРАНТОВАНО ВІДСУТНІЙ\n100% точний True Negative\n0 звернень до повільної пам'яті!", size=11, fill="#e8f5e9", stroke=FIELD, bold=True)
    out.append(b_res1)
    out.append(arrow(640, 160, 640, 202, color=FIELD))

    # Запит 2: Ключ Z2 (False Positive)
    b_q2, _, _ = textbox(890, 65, 'Запит Z₂ ("item_404")', size=12, bold=True, fill="#ffffff", stroke=LINE)
    out.append(b_q2)
    b_qz2, _, _ = textbox(890, 130, "h₁(Z₂) = 1  → біт 1 = 1\nh₂(Z₂) = 5  → біт 5 = 1\nh₃(Z₂) = 14 → біт 14 = 1", size=11, fill="#fff8e1", stroke=LINE)
    out.append(b_qz2)
    out.append(arrow(890, 82, 890, 102, color=LINE))

    b_res2, _, _ = textbox(890, 235, "Усі біти = 1 (хибний збіг)\nХибнопозитивне (False Positive)\nПотрібна перевірка у сховищі", size=11, fill="#fde8e8", stroke=POS, bold=True)
    out.append(b_res2)
    out.append(arrow(890, 160, 890, 202, color=POS))

    # Підсумок внизу справа
    b_r_sum, _, _ = textbox(765, 365, "Асиметрія відповідей:\n• Відповідь «Ні» — абсолютно точна (відсутній 100%)\n• Відповідь «Так» — ймовірна (потребує звернення до пам'яті)", size=11, fill="#f4f6f8", stroke=LINE)
    out.append(b_r_sum)

    out.append("</svg>")
    path = os.path.join(OUT_DIR, "bloom-lookup.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def fig_cache_blocked_bloom():
    """Фігура 2: Класичний фільтр Блума (промахи кешу) проти блочного кеш-орієнтованого фільтра."""
    dw = 980
    dh = 460
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (dw, dh, dw, dh),
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % LINE,
        '  </marker>',
        '  <marker id="arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % POS,
        '  </marker>',
        '  <marker id="arrow-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % FIELD,
        '  </marker>',
        '</defs>',
        '<rect width="100%%" height="100%%" fill="%s"/>' % BG,
    ]

    # Верхній блок: Класичний фільтр (Cache Misses)
    out.append(text(490, 25, "Класичний фільтр: k випадкових звернень по всьому простору RAM", size=15, bold=True, color=POS))
    
    b_cpu1, _, _ = textbox(100, 95, "CPU Ядро\nЗапит ключа", size=11, bold=True, fill="#f4f6f8", stroke=LINE)
    out.append(b_cpu1)

    out.append(arrow(160, 95, 210, 95, color=POS))

    # Велика RAM
    out.append(rect(220, 50, 730, 90, fill="#fff8f8", stroke=POS, sw=1.5, rx=5))
    out.append(text(585, 70, "Оперативна пам'ять (DRAM) — фільтр Блума на 64 МБ (мільйони кеш-ліній)", size=12, bold=True, color=INK))

    cache_line_x = [290, 480, 670, 860]
    labels_cl = ["Лінія #1204\n(промах L3)", "Лінія #89021\n(промах L3)", "Лінія #3412\n(промах L3)", "Лінія #55018\n(промах L3)"]
    
    for i in range(4):
        bx, _, _ = textbox(cache_line_x[i], 108, labels_cl[i], size=10, fill="#ffebee", stroke=POS)
        out.append(bx)

    b_sum1, _, _ = textbox(490, 165, "Ціна 1 запиту: k = 4–8 незалежних промахів кешу L3 → ~200–400 нс затримки конвеєра!", size=11, bold=True, fill="#ffebee", stroke=POS)
    out.append(b_sum1)

    # Розділювальна смуга
    out.append(line(40, 200, 940, 200, color=MUTED, sw=1.2, dash="6,6"))

    # Нижній блок: Блочний фільтр Блума
    out.append(text(490, 228, "Блочний фільтр (Blocked Bloom): локалізація всередині 1 кеш-лінії 64 байти", size=15, bold=True, color=FIELD))

    b_cpu2, _, _ = textbox(100, 310, "CPU Ядро\nSIMD (AVX2/512)", size=11, bold=True, fill="#e8f5e9", stroke=FIELD)
    out.append(b_cpu2)

    # Вибір блоку
    b_h0, _, _ = textbox(250, 310, "Геш h₀(x)\nВибір блоку", size=11, fill=FILL, stroke=LINE)
    out.append(b_h0)
    out.append(arrow(160, 310, 200, 310, color=FIELD))

    # Єдина кеш-лінія 64 байти
    out.append(rect(340, 260, 600, 100, fill="#f0fff4", stroke=FIELD, sw=1.8, rx=6))
    out.append(text(640, 282, "Єдина кеш-лінія CPU (64 байти = 512 бітів)", size=12, bold=True, color=FIELD))

    # Стрілка від h0 до кеш-лінії
    out.append(arrow(300, 310, 335, 310, color=FIELD))

    # Усередині кеш-лінії: SIMD / побітові операції
    b_simd, _, _ = textbox(640, 322, "Локальні геші h₁..h_k(x) встановлюють і тестують біти ВИКЛЮЧНО в цих 512 бітах\nОбробка через побітове AND + AVX2 за 1–3 процесорні такти!", size=10, fill="#ffffff", stroke=FIELD)
    out.append(b_simd)

    b_sum2, _, _ = textbox(490, 415, "Ціна 1 запиту: рівно 1 звернення до кешу (64 байти) → 5–10 разів швидше за класичний фільтр!", size=11, bold=True, fill="#e8f5e9", stroke=FIELD)
    out.append(b_sum2)

    out.append("</svg>")
    path = os.path.join(OUT_DIR, "cache-blocked-bloom.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def fig_snoop_filter():
    """Фігура 3: Апаратний Snoop Filter у багатосокетній системі на основі фільтра Блума."""
    dw = 980
    dh = 440
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (dw, dh, dw, dh),
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % LINE,
        '  </marker>',
        '  <marker id="arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % POS,
        '  </marker>',
        '  <marker id="arrow-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % FIELD,
        '  </marker>',
    ]

    out.append(text(490, 25, "Апаратний Snoop Filter: фільтрація когерентних запитів між сокетами", size=15, bold=True, color=INK))

    # Лівий сокет (Socket 0)
    out.append(rect(30, 60, 260, 260, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
    out.append(text(160, 85, "Процесорний сокет #0", size=13, bold=True, color=INK))

    b_c0, _, _ = textbox(95, 130, "Ядро 0\nL1/L2", size=11, fill="#ffffff", stroke=LINE)
    b_c1, _, _ = textbox(225, 130, "Ядро 1\nL1/L2", size=11, fill="#ffffff", stroke=LINE)
    out.extend([b_c0, b_c1])

    b_l3_0, _, _ = textbox(160, 210, "Спільний кеш L3 (LLC)\nSocket 0", size=11, bold=True, fill="#eef2f7", stroke=NEG)
    out.append(b_l3_0)
    out.append(arrow(95, 150, 135, 185, color=LINE))
    out.append(arrow(225, 150, 185, 185, color=LINE))

    b_mc0, _, _ = textbox(160, 285, "Контролер шини / QPI", size=10, fill="#ffffff", stroke=LINE)
    out.append(b_mc0)
    out.append(arrow(160, 235, 160, 268, color=LINE))

    # Центральний вузол: Апаратний Snoop Filter
    out.append(rect(370, 70, 240, 240, fill="#e8f5e9", stroke=FIELD, sw=1.8, rx=8))
    out.append(text(490, 95, "Snoop Filter (Апаратний)", size=13, bold=True, color=FIELD))
    b_sf_desc, _, _ = textbox(490, 165, "Бітовий масив відбитків\nкеш-ліній у сокетах\n\nТест Блума:\n«Чи є адреса в сокеті #1?»", size=11, fill="#ffffff", stroke=FIELD)
    out.append(b_sf_desc)

    b_sf_stat, _, _ = textbox(490, 270, "Фільтрує 85–95% запитів\nбез завантаження шини", size=10, bold=True, fill="#d4edda", stroke=FIELD)
    out.append(b_sf_stat)

    # Правий сокет (Socket 1)
    out.append(rect(690, 60, 260, 260, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
    out.append(text(820, 85, "Процесорний сокет #1", size=13, bold=True, color=INK))

    b_mc1, _, _ = textbox(820, 285, "Контролер шини / QPI", size=10, fill="#ffffff", stroke=LINE)
    out.append(b_mc1)

    b_l3_1, _, _ = textbox(820, 210, "Спільний кеш L3 (LLC)\nSocket 1", size=11, bold=True, fill="#eef2f7", stroke=NEG)
    out.append(b_l3_1)
    out.append(arrow(820, 268, 820, 235, color=LINE))

    b_c2, _, _ = textbox(755, 130, "Ядро 2\nL1/L2", size=11, fill="#ffffff", stroke=LINE)
    b_c3, _, _ = textbox(885, 130, "Ядро 3\nL1/L2", size=11, fill="#ffffff", stroke=LINE)
    out.extend([b_c2, b_c3])
    out.append(arrow(795, 185, 755, 150, color=LINE))
    out.append(arrow(845, 185, 885, 150, color=LINE))

    # Стрілки когерентності
    # 1. Запит на запис від Socket 0 до Snoop Filter
    out.append(arrow(220, 285, 360, 210, color=NEG))
    out.append(text(285, 230, "Запит запису\n(Invalidate)", size=10, color=NEG))

    # 2. Результат від Snoop Filter
    out.append(text(490, 340, "Відповідь фільтра = 0 ⇒ Лінії гарантовано немає в Socket 1", size=11, bold=True, color=FIELD))
    out.append(text(490, 360, "Міжсокетна шина лишається вільною, кеш Socket 1 не турбують!", size=10, color=FIELD))

    # Шлях Б (якщо 1) - червона стрілка
    out.append(arrow(620, 210, 680, 285, color=POS))
    out.append(text(670, 230, "Лише якщо 1:\nSnoop запит", size=10, color=POS))

    b_bot, _, _ = textbox(490, 405, "Без фільтра: кожна операція запису широкомовно глушить шину між сокетами.", size=11, fill="#f4f6f8", stroke=LINE)
    out.append(b_bot)

    out.append("</svg>")
    path = os.path.join(OUT_DIR, "snoop-filter.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def main():
    fig_bloom_lookup()
    fig_cache_blocked_bloom()
    fig_snoop_filter()
    print("Фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
