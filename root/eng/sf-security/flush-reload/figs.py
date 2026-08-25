# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми flush-reload.
Використовує svgkit зі scripts/.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

def fig_flush_reload_phases():
    w, h = 860, 400
    frags = []
    
    frags.append(text(w / 2, 28, "Три фази циклу вимірювання Flush+Reload", size=17, bold=True))
    
    col_w = 246
    gap = 26
    start_x = 35
    
    phases = [
        ("1. FLUSH (Очищення)", [
            "Атакуючий виконує інструкцію",
            "clflush для цільової адреси:",
            "",
            "Лінія витісняється з L1, L2",
            "та інклюзивного L3 в DRAM.",
            "Кеш стає «холодним» для всіх ядер."
        ], NEG, "#f0f4fc"),
        ("2. VICTIM / WAIT (Жертва)", [
            "Програма-жертва виконує код.",
            "Якщо виконано гілку з секретом:",
            "",
            "Процесор звертається до адреси,",
            "і лінія підтягується в L1/L2/L3.",
            "Якщо секрет інший — лінія в DRAM."
        ], POS, "#fdf2f0"),
        ("3. RELOAD (Вимірювання)", [
            "Атакуючий зчитує цільову адресу,",
            "заміряючи час через rdtsc / rdtscp:",
            "",
            "Швидко (< 80 тактів) → Cache HIT",
            "(жертва зверталась до даних!)",
            "Повільно (> 180 тактів) → Cache MISS"
        ], FIELD, "#f0f8f3")
    ]
    
    for idx, (p_title, p_lines, p_color, p_bg) in enumerate(phases):
        x = start_x + idx * (col_w + gap)
        y = 56
        
        # Рамка фази
        frags.append(rect(x, y, col_w, 310, fill=p_bg, stroke=p_color, sw=2, rx=8))
        
        # Заголовок фази
        t_box, _, _ = textbox(x + col_w / 2, y + 26, p_title, size=14, bold=True, color=p_color, fill=BG, stroke=p_color, sw=1.5, rx=5)
        frags.append(t_box)
        
        # Текст фази
        frags.append(mtext(x + col_w / 2, y + 90, p_lines, size=13, color=INK, lh=1.4))
        
        # Стрілка між колонками
        if idx < 2:
            arr_x1 = x + col_w + 4
            arr_x2 = x + col_w + gap - 4
            arr_y = y + 155
            frags.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color=LINE, sw=2))
    
    render(os.path.join(OUT_DIR, "flush-reload-phases.svg"), w, h, *frags)

def fig_inclusive_llc_sharing():
    w, h = 860, 460
    frags = []
    
    frags.append(text(w / 2, 26, "Спільна сторінка у віртуальній пам'яті та інклюзивний кеш LLC", size=17, bold=True))
    
    # Два процеси вгорі
    p1_box, _, _ = textbox(215, 68, "Процес А (Атакуючий)\nВіртуальна адреса 0x7fff_1000\nВикликає clflush(addr)", size=13, fill="#f0f4fc", stroke=NEG, sw=1.5)
    p2_box, _, _ = textbox(645, 68, "Процес Б (Жертва / OpenSSL)\nВіртуальна адреса 0x7f88_4000\nЗвертається до T-table[k]", size=13, fill="#fdf2f0", stroke=POS, sw=1.5)
    frags.extend([p1_box, p2_box])
    
    # ОС і сторінкова таблиця посередині
    os_box, _, _ = textbox(w / 2, 160, "Сторінкова пам'ять ядра ОС (Page Cache / mmap / libcrypto.so)\nОбидві віртуальні адреси вказують на ОДИН фізичний фрейм (0x1A4000)", size=13, fill="#fcf8e8", stroke="#b8860b", sw=1.5)
    frags.append(os_box)
    
    # Стрілки від процесів до спільного фрейму
    frags.append(arrow(215, 106, 320, 134, color=NEG, sw=1.8))
    frags.append(arrow(645, 106, 540, 134, color=POS, sw=1.8))
    
    # Кеш-ієрархія ядер
    c1_box, _, _ = textbox(215, 265, "Ядро 0 (L1D / L2 кеш)\nПриватний кеш атакуючого", size=12, fill=FILL, stroke=LINE, sw=1.2)
    c2_box, _, _ = textbox(645, 265, "Ядро 1 (L1D / L2 кеш)\nПриватний кеш жертви", size=12, fill=FILL, stroke=LINE, sw=1.2)
    frags.extend([c1_box, c2_box])
    
    frags.append(arrow(340, 186, 230, 240, color=LINE, sw=1.5))
    frags.append(arrow(520, 186, 630, 240, color=LINE, sw=1.5))
    
    # Спільний LLC
    llc_box, _, _ = textbox(w / 2, 345, "Спільний кеш останнього рівня (Inclusive L3 / LLC)\nІнклюзивна властивість: витіснення з LLC інвалідує лінію в L1/L2 обох ядер", size=13, fill="#edf8f1", stroke=FIELD, sw=2)
    frags.append(llc_box)
    
    frags.append(arrow(215, 290, 320, 320, color=LINE, sw=1.5))
    frags.append(arrow(645, 290, 540, 320, color=LINE, sw=1.5))
    
    # Оперативна пам'ять DRAM
    dram_box, _, _ = textbox(w / 2, 420, "Фізична оперативна пам'ять DRAM (150–300 тактів затримки)", size=13, fill="#f8f9fa", stroke=MUTED, sw=1.2)
    frags.append(dram_box)
    
    frags.append(arrow(w / 2, 370, w / 2, 396, color=MUTED, sw=1.5))
    
    render(os.path.join(OUT_DIR, "inclusive-llc-sharing.svg"), w, h, *frags)

def fig_timing_histogram():
    w, h = 900, 440
    frags = []
    
    frags.append(text(w / 2, 28, "Розподіл часу доступу: розділення Hit (L3) та Miss (DRAM)", size=17, bold=True))
    
    # Вісь часу
    ox1, ox2 = 70, 830
    oy = 360
    frags.append(line(ox1, oy, ox2, oy, color=LINE, sw=2))
    frags.append(arrow(ox2 - 10, oy, ox2 + 20, oy, color=LINE, sw=2))
    frags.append(text(ox2 + 25, oy + 5, "Час (такти)", size=13, anchor="start", bold=True))
    
    # Поділки на осі
    ticks = [
        (180, "30–50", "L1/L2 Hit"),
        (280, "60–80", "L3/LLC Hit"),
        (450, "120–140", "Поріг T"),
        (680, "200–280", "DRAM Miss")
    ]
    for tx, val_str, lbl_str in ticks:
        frags.append(line(tx, oy - 6, tx, oy + 6, color=LINE, sw=1.5))
        frags.append(text(tx, oy + 22, val_str, size=12, bold=True))
        frags.append(text(tx, oy + 38, lbl_str, size=11, color=MUTED))
    
    # Крива Cache Hit (зелена)
    # Пік біля x=230
    poly_hit = [
        (130, oy),
        (160, oy - 40),
        (190, oy - 140),
        (230, oy - 230),
        (260, oy - 160),
        (290, oy - 60),
        (330, oy)
    ]
    path_hit_pts = " ".join(f"{px},{py}" for px, py in poly_hit)
    frags.append(f'<polygon points="{path_hit_pts}" fill="#edf8f1" stroke="{FIELD}" stroke-width="2"/>')
    
    hit_lbl, _, _ = textbox(170, 110, "Розподіл Cache HIT\n(дані були в кеші)", size=12, color=FIELD, bold=True, fill=BG, stroke=FIELD, sw=1.2)
    frags.append(hit_lbl)
    
    # Крива Cache Miss (червона)
    # Пік біля x=680
    poly_miss = [
        (550, oy),
        (590, oy - 50),
        (640, oy - 150),
        (680, oy - 220),
        (720, oy - 140),
        (760, oy - 40),
        (800, oy)
    ]
    path_miss_pts = " ".join(f"{px},{py}" for px, py in poly_miss)
    frags.append(f'<polygon points="{path_miss_pts}" fill="#fdf2f0" stroke="{POS}" stroke-width="2"/>')
    
    miss_lbl, _, _ = textbox(730, 110, "Розподіл Cache MISS\n(читання з DRAM)", size=12, color=POS, bold=True, fill=BG, stroke=POS, sw=1.2)
    frags.append(miss_lbl)
    
    # Поріг відсікання T (пунктир)
    frags.append(line(450, 60, 450, oy, color=NEG, sw=2, dash="6,4"))
    
    thresh_box, _, _ = textbox(450, 70, "Калібрований поріг T (~130 тактів)\nЧас < T ⇒ Жертва читала лінію\nЧас > T ⇒ Жертва не торкалася", size=12, color=NEG, bold=True, fill="#edf2fc", stroke=NEG, sw=1.5)
    frags.append(thresh_box)
    
    render(os.path.join(OUT_DIR, "timing-histogram-separation.svg"), w, h, *frags)

def fig_cache_attack_matrix():
    w, h = 860, 390
    frags = []
    
    frags.append(text(w / 2, 26, "Порівняння властивостей методів кеш-атак", size=17, bold=True))
    
    cards = [
        ("Flush+Reload", [
            "• Потребує: спільну пам'ять (mmap)",
            "• Інструкція: clflush / clflushopt",
            "• Точність: лінія кешу (64 байти)",
            "• Рівень шуму: надзвичайно низький",
            "• Швидкість: до 1–2 МБ/с",
            "• Кеш: інклюзивний LLC (L3)"
        ], POS, "#fdf2f0"),
        ("Prime+Probe", [
            "• Потребує: спільний набір кешу",
            "• Не потребує спільної пам'яті!",
            "• Точність: набір кешу (Set)",
            "• Рівень шуму: середній / високий",
            "• Швидкість: 10–100 КБ/с",
            "• Використовує: заповнення ліній"
        ], "#d97706", "#fef9ee"),
        ("Flush+Flush", [
            "• Потребує: спільну пам'ять (mmap)",
            "• Заміряє час САМОЇ clflush",
            "• Не викликає завантаження в кеш",
            "• Stealth: не видно у лічильниках",
            "• Рівень шуму: високий",
            "• Швидкість: середня"
        ], NEG, "#f0f4fc"),
        ("Evict+Reload", [
            "• Потребує: спільну пам'ять",
            "• Без clflush (наприклад, ARM / JS)",
            "• Витіснення через набір ліній",
            "• Точність: лінія кешу (64 байти)",
            "• Рівень шуму: помірний",
            "• Працює без спец-інструкцій"
        ], FIELD, "#f0f8f3")
    ]
    
    card_w = 186
    card_gap = 16
    start_x = 35
    
    for idx, (c_title, c_bullets, c_color, c_bg) in enumerate(cards):
        cx = start_x + idx * (card_w + card_gap)
        cy = 58
        
        frags.append(rect(cx, cy, card_w, 305, fill=c_bg, stroke=c_color, sw=1.8, rx=8))
        
        t_box, _, _ = textbox(cx + card_w / 2, cy + 24, c_title, size=14, bold=True, color=c_color, fill=BG, stroke=c_color, sw=1.5, rx=5)
        frags.append(t_box)
        
        frags.append(mtext(cx + 12, cy + 78, c_bullets, size=11.5, color=INK, anchor="start", lh=1.4))
    
    render(os.path.join(OUT_DIR, "cache-attack-comparison.svg"), w, h, *frags)

if __name__ == "__main__":
    fig_flush_reload_phases()
    fig_inclusive_llc_sharing()
    fig_timing_histogram()
    fig_cache_attack_matrix()
    print("Усі фігури згенеровано успішно.")
