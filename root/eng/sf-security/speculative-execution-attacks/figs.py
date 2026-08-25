# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми speculative-execution-attacks.
Використовує svgkit зі scripts/.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

def fig_flush_reload():
    w, h = 820, 430
    frags = []
    
    frags.append(text(w / 2, 28, "Три фази сайд-каналу Flush+Reload", size=18, bold=True))
    
    col_w = 230
    gap = 35
    start_x = 45
    
    phases = [
        ("1. FLUSH (Очищення)", [
            "Атакуючий викликає clflush",
            "для всіх 256 ліній масиву probe.",
            "",
            "Масив повністю витіснено",
            "з L1/L2/L3 у повільну DRAM.",
            "Кеш-пам'ять «холодна»."
        ], NEG, "#edf2fc"),
        ("2. SPECULATE (Спекуляція)", [
            "Жертва або спекулятивний код",
            "читає секрет S і робить доступ:",
            "probe[S * 4096]",
            "",
            "Лінія з індексом S завантажується",
            "в апаратний кеш L1D ядра.",
            "Решта 255 ліній лишаються в DRAM."
        ], POS, "#fdf0ed"),
        ("3. RELOAD (Вимірювання)", [
            "Атакуючий проходить 0..255,",
            "заміряючи rdtscp до probe[i * 4096]:",
            "",
            "i != S → DRAM miss (~200 тактів)",
            "i == S → L1 cache HIT (~10 тактів)",
            "",
            "Значення S відновлено за часом!"
        ], FIELD, "#edf8f1")
    ]
    
    for idx, (p_title, p_lines, p_color, p_bg) in enumerate(phases):
        x = start_x + idx * (col_w + gap)
        y = 65
        
        # Рамка фази
        frags.append(rect(x, y, col_w, 335, fill=p_bg, stroke=p_color, sw=2, rx=8))
        
        # Шапка картки
        frags.append(text(x + col_w / 2, y + 28, p_title, size=13, bold=True, color=p_color))
        frags.append(line(x + 15, y + 42, x + col_w - 15, y + 42, color=p_color, sw=1, dash="3,3"))
        
        # Вміст
        line_y = y + 70
        for ln in p_lines:
            if not ln:
                line_y += 12
                continue
            is_hl = "HIT" in ln or "S *" in ln or "clflush" in ln
            frags.append(text(x + col_w / 2, line_y, ln, size=12, bold=is_hl, color=p_color if is_hl else INK))
            line_y += 20

        if idx < 2:
            ax1 = x + col_w + 5
            ax2 = ax1 + gap - 10
            ay = y + 165
            frags.append(arrow(ax1, ay, ax2, ay, color=LINE, sw=2.5))
            frags.append(text(ax1 + (gap - 5) / 2, ay - 12, "далі", size=11, color=MUTED, bold=True))

    render(os.path.join(OUT_DIR, "flush-reload-timeline.svg"), w, h, *frags)

def fig_meltdown():
    w, h = 860, 480
    frags = []
    
    frags.append(text(w / 2, 28, "Мікроархітектурний витік пам'яті ядра в атаці Meltdown", size=18, bold=True))
    
    box_code, _, _ = textbox(240, 95, "Код у просторі користувача (Ring 3):\n1: mov al, byte [kernel_ptr]   ; Читання забороненої адреси ядра\n2: shl rax, 12                 ; rax = секрет * 4096 байт\n3: mov rbx, [probe + rax]      ; Звернення до масиву-зонда", size=12, fill="#f8fafc", stroke=LINE, sw=1.5, min_w=430)
    frags.append(box_code)
    
    frags.append(rect(490, 60, 340, 390, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(660, 85, "Апаратний конвеєр процесора (OoO Core)", size=13, bold=True, color=INK))
    
    frags.append(rect(505, 115, 150, 240, fill="#fdf0ed", stroke=POS, sw=1.5, rx=6))
    frags.append(text(580, 138, "Транзитне виконання", size=12, bold=True, color=POS))
    frags.append(text(580, 160, "L1D Cache Hit", size=11, bold=True, color=INK))
    frags.append(text(580, 180, "Байт ядра віддано", size=11, color=INK))
    frags.append(text(580, 198, "в транзитний регістр", size=11, color=INK))
    
    frags.append(arrow(580, 215, 580, 245, color=POS, sw=2))
    frags.append(text(580, 265, "Forwarding інструкції 3:", size=11, bold=True, color=POS))
    frags.append(text(580, 285, "probe[secret * 4096]", size=11, bold=True, color=INK))
    frags.append(text(580, 305, "завантажено в L1D!", size=11, bold=True, color=POS))
    frags.append(text(580, 335, "[Слід у кеші закріплено]", size=11, color=POS))

    frags.append(rect(670, 115, 145, 240, fill="#edf2fc", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(742, 138, "Перевірка прав (MMU)", size=12, bold=True, color=NEG))
    frags.append(text(742, 165, "Читання біта U/S", size=11, color=INK))
    frags.append(text(742, 185, "у таблиці сторінок", size=11, color=INK))
    frags.append(text(742, 215, "Виявлено порушення:", size=11, bold=True, color=NEG))
    frags.append(text(742, 235, "User mode читає Ring 0", size=11, color=INK))
    frags.append(arrow(742, 250, 742, 275, color=NEG, sw=2))
    frags.append(text(742, 295, "Генерація виключення", size=11, bold=True, color=NEG))
    frags.append(text(742, 315, "#PF (Page Fault)", size=11, bold=True, color=NEG))
    frags.append(text(742, 335, "при Commit у ROB", size=11, color=INK))

    frags.append(rect(505, 370, 310, 65, fill="#fbf0f0", stroke=POS, sw=2, rx=6))
    frags.append(text(660, 395, "Скидання архітектурного стану (ROB Squash)", size=12, bold=True, color=POS))
    frags.append(text(660, 418, "Регістри al, rax, rbx скасовано. АЛЕ кеш L1D НЕ очищено!", size=11, color=INK))

    box_note, _, _ = textbox(240, 305, "Фізична причина шпарини:\nL1D Data Cache віддає байти залежним інструкціям\nдо того, як MMU завершить перевірку прав доступу.\n\nАрхітектурно: програма отримує сигнал SIGSEGV.\nМікроархітектурно: секретний байт витік у кеш.", size=12, fill="#f4f6f8", stroke=MUTED, sw=1.5, min_w=430)
    frags.append(box_note)

    render(os.path.join(OUT_DIR, "meltdown-mechanism.svg"), w, h, *frags)

def fig_spectre_v1():
    w, h = 860, 460
    frags = []
    
    frags.append(text(w / 2, 28, "Спекулятивний обхід перевірки меж (Spectre v1)", size=18, bold=True))
    
    frags.append(rect(40, 65, 235, 360, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(157, 95, "Фаза 1: Навчання PHT", size=14, bold=True, color=INK))
    frags.append(text(157, 125, "Код жертви:", size=12, bold=True, color=MUTED))
    frags.append(text(157, 150, "if (x < arr1_len)", size=12, bold=True, color=INK))
    frags.append(text(157, 172, "  y = arr2[arr1[x]*4096];", size=12, color=INK))
    
    frags.append(rect(55, 210, 205, 110, fill="#edf8f1", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(157, 235, "Тренування валідними x:", size=11, bold=True, color=FIELD))
    frags.append(text(157, 258, "x = 0, 1, 2, 3 (< len)", size=11, color=INK))
    frags.append(text(157, 280, "Гілка завжди TAKEN (11)", size=11, color=INK))
    frags.append(text(157, 302, "PHT впевнений у переході", size=11, bold=True, color=FIELD))
    
    frags.append(text(157, 355, "Провісник запам'ятовує:", size=11, color=MUTED))
    frags.append(text(157, 375, "«Умова if завжди істинна»", size=12, bold=True, color=INK))

    frags.append(rect(310, 65, 250, 360, fill="#fdf0ed", stroke=POS, sw=2, rx=8))
    frags.append(text(435, 95, "Фаза 2: Спекулятивний вихід", size=14, bold=True, color=POS))
    
    frags.append(text(435, 125, "1. clflush(arr1_len)", size=11, bold=True, color=NEG))
    frags.append(text(435, 145, "Довжина витіснена в DRAM", size=11, color=MUTED))
    frags.append(text(435, 170, "2. Подаємо шкідливий x_bad", size=11, bold=True, color=POS))
    frags.append(text(435, 190, "(вказує на секрет у пам'яті)", size=11, color=INK))
    
    frags.append(rect(325, 215, 220, 115, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    frags.append(text(435, 238, "Перевірка (x < len) зависла", size=11, color=NEG))
    frags.append(text(435, 258, "CPU спекулює: бере тіло if!", size=11, bold=True, color=POS))
    frags.append(text(435, 280, "Читає arr1[x_bad] = S", size=11, bold=True, color=POS))
    frags.append(text(435, 302, "Тягне arr2[S * 4096] в L1D", size=11, bold=True, color=POS))

    frags.append(text(435, 355, "Пам'ять за межами масиву", size=11, color=POS))
    frags.append(text(435, 375, "прочитано спекулятивно!", size=11, bold=True, color=POS))

    frags.append(rect(595, 65, 225, 360, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(707, 95, "Фаза 3: Відкат і витік", size=14, bold=True, color=INK))
    
    frags.append(rect(610, 125, 195, 105, fill="#edf2fc", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(707, 150, "arr1_len прибула з DRAM:", size=11, bold=True, color=NEG))
    frags.append(text(707, 172, "x_bad >= len → FALSE", size=11, bold=True, color=NEG))
    frags.append(text(707, 195, "Конвеєр скидає тіло if", size=11, color=INK))
    frags.append(text(707, 215, "Регістри y скасовано", size=11, color=INK))

    frags.append(rect(610, 245, 195, 120, fill="#edf8f1", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(707, 270, "АЛЕ рядок arr2[S * 4096]", size=11, bold=True, color=FIELD))
    frags.append(text(707, 292, "лишився в кеші L1D!", size=11, bold=True, color=FIELD))
    frags.append(text(707, 318, "Reload-сканування arr2", size=11, color=INK))
    frags.append(text(707, 340, "знаходить гарячий індекс S", size=11, bold=True, color=FIELD))

    frags.append(arrow(280, 245, 305, 245, color=LINE, sw=2))
    frags.append(arrow(565, 245, 590, 245, color=LINE, sw=2))

    render(os.path.join(OUT_DIR, "spectre-v1-pipeline.svg"), w, h, *frags)

def fig_mitigations():
    w, h = 860, 470
    frags = []
    
    frags.append(text(w / 2, 28, "Карта захисних заходів проти спекулятивних атак", size=18, bold=True))
    
    items = [
        ("Meltdown (CVE-2017-5754)", "KPTI (Kernel Page Table Isolation)", "Розділення CR3 користувача і ядра; пам'ять ядра взагалі не змаплена в Ring 3.", "Апаратний фікс у нових CPU (блокування читання до U/S перевірки).", NEG, "#edf2fc"),
        ("Spectre v1 (CVE-2017-5753)", "LFENCE / Speculation Barriers", "Бар'єр зупиняє спекулятивне виконання до розв'язання гілки меж; або маскування індексу (SLH).", "Програмна вставка lfence у вразливі місця ядра та браузерів.", FIELD, "#edf8f1"),
        ("Spectre v2 (CVE-2017-5715)", "Retpoline + IBRS / IBPB", "Retpoline замінює непрямі стрибки на стек RSB; IBRS/eIBRS забороняє вплив з Ring 3 на Ring 0; IBPB чистить BTB.", "Апаратний eIBRS у нових поколіннях із нульовим штрафом.", POS, "#fdf0ed"),
        ("MDS / L1TF / Cross-SMT", "STIBP + Core Scheduling", "STIBP ізолює провісники між гіперпотоками (SMT); скидання L1D при перемиканні VM; вимкнення SMT у хмарах.", "Заборона спільного використання ядра різними доменами безпеки.", INK, "#f8fafc")
    ]
    
    card_y = 65
    card_h = 90
    card_gap = 12
    
    for idx, (vuln, mit_name, mit_desc, mit_hw, col, bg) in enumerate(items):
        y = card_y + idx * (card_h + card_gap)
        frags.append(rect(40, y, 780, card_h, fill=bg, stroke=col, sw=2, rx=6))
        
        frags.append(rect(55, y + 12, 220, 66, fill=BG, stroke=col, sw=1.5, rx=4))
        frags.append(text(165, y + 36, vuln.split(" (")[0], size=13, bold=True, color=col))
        if "(" in vuln:
            frags.append(text(165, y + 58, "(" + vuln.split(" (")[1], size=11, color=MUTED))

        frags.append(text(295, y + 26, "Захист: " + mit_name, size=13, bold=True, color=INK, anchor="start"))
        frags.append(text(295, y + 48, mit_desc, size=11, color=INK, anchor="start"))
        frags.append(text(295, y + 68, "Статус: " + mit_hw, size=11, color=MUTED, italic=True, anchor="start"))

    render(os.path.join(OUT_DIR, "mitigations-map.svg"), w, h, *frags)

if __name__ == "__main__":
    fig_flush_reload()
    fig_meltdown()
    fig_spectre_v1()
    fig_mitigations()
    print("Всі 4 фігури згенеровано успішно.")
