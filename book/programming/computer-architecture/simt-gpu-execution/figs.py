# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми SIMT: модель виконання потоків і варпів на GPU."""

import os
import sys

# Додаємо scripts до шляху пошуку
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_simd_vs_simt():
    """Фігура 1: Порівняння SIMD (векторні регістри) та SIMT (потоки у варпі)."""
    w, h = 860, 390
    frags = []

    # Заголовок панелей
    frags.append(text(220, 30, "SIMD на CPU: явний векторний регістр", size=15, bold=True, color=INK))
    frags.append(text(640, 30, "SIMT на GPU: скалярні потоки у варпі", size=15, bold=True, color=INK))

    # Ліва панель: SIMD
    frags.append(rect(30, 48, 380, 322, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(220, 75, "Один потік керування (1 PC, 1 потік ОС)", size=12, color=MUTED))

    # Векторний регістр
    frags.append(rect(50, 95, 340, 52, fill="#e2e8f0", stroke="#94a3b8", rx=4))
    frags.append(text(220, 114, "Векторний регістр (наприклад, 256-бітний YMM)", size=12, bold=True))
    lanes = ["Lane 0 (f32)", "Lane 1 (f32)", "Lane 2 (f32)", "Lane 3 (f32)"]
    for i, ln in enumerate(lanes):
        frags.append(rect(55 + i * 82, 124, 78, 18, fill="#cbd5e1", stroke="#94a3b8", rx=2))
        frags.append(text(94 + i * 82, 137, ln, size=10, color=INK))

    frags.append(arrow(220, 155, 220, 185, color=LINE))
    frags.append(text(220, 175, "1 векторна інструкція (vaddps)", size=11, color=POS, bold=True))

    # Векторне АЛП
    frags.append(rect(50, 195, 340, 60, fill="#fee2e2", stroke=POS, rx=4))
    frags.append(text(220, 215, "Векторне АЛП (4 паралельні доріжки)", size=12, bold=True, color=POS))
    for i in range(4):
        frags.append(rect(58 + i * 82, 226, 72, 22, fill="#fca5a5", stroke=POS, rx=2))
        frags.append(text(94 + i * 82, 241, "ALU %d" % i, size=11, bold=True, color=INK))

    frags.append(text(220, 285, "Програміст вручну упаковує вектори", size=11, bold=True, color=INK))
    frags.append(text(220, 305, "Векторизація жорстко зафіксована в ISA", size=11, color=MUTED))
    frags.append(text(220, 325, "Розгалуження всередині регістра неможливе", size=11, color=MUTED))

    # Розділювач
    frags.append(line(430, 48, 430, 370, color="#cbd5e1", sw=1.5, dash="4,4"))

    # Права панель: SIMT
    frags.append(rect(450, 48, 380, 322, fill="#f0fdf4", stroke="#bbf7d0", rx=8))
    frags.append(text(640, 75, "32 незалежні потоки з власними регістрами", size=12, color=MUTED))

    # Скалярні потоки
    threads = ["Потік 0", "Потік 1", "Потік 2", "...", "Потік 31"]
    for i, th in enumerate(threads):
        x = 465 + i * 70
        frags.append(rect(x, 95, 64, 52, fill="#dcfce7", stroke=FIELD, rx=4))
        frags.append(text(x + 32, 114, th, size=11, bold=True, color=FIELD))
        frags.append(text(x + 32, 134, "R0..R15", size=10, color=MUTED))

    # Об'єднання у варп
    frags.append(rect(460, 155, 360, 30, fill="#fef08a", stroke="#ca8a04", rx=4))
    frags.append(text(640, 175, "Варп (32 потоки): 1 спільний лічильник команд (PC)", size=11, bold=True, color="#854d0e"))

    frags.append(arrow(640, 190, 640, 210, color=LINE))

    # Апаратні конвеєри SIMT
    frags.append(rect(460, 215, 360, 50, fill="#dbeafe", stroke=NEG, rx=4))
    frags.append(text(640, 233, "32 паралельні конвеєри (SIMT Execution Lanes)", size=11, bold=True, color=NEG))
    for i in range(5):
        lbl = "ALU %d" % i if i < 3 else ("..." if i == 3 else "ALU 31")
        frags.append(rect(468 + i * 70, 242, 60, 18, fill="#bfdbfe", stroke=NEG, rx=2))
        frags.append(text(498 + i * 70, 255, lbl, size=10, color=INK))

    frags.append(text(640, 285, "Програміст пише звичайний скалярний код", size=11, bold=True, color=INK))
    frags.append(text(640, 305, "Залізо саме об'єднує потоки у варпи по 32", size=11, color=MUTED))
    frags.append(text(640, 325, "Кожен потік має свій стек, адресу й дані", size=11, color=MUTED))

    render(os.path.join(IMG_DIR, "simd-vs-simt.svg"), w, h, *frags)


def fig_execution_hierarchy():
    """Фігура 2: Ієрархія виконання GPU: Grid -> Blocks на SM -> Warps -> Threads."""
    w, h = 880, 440
    frags = []

    # Grid
    frags.append(rect(20, 20, 840, 400, fill="#f8fafc", stroke="#64748b", sw=2, rx=8))
    frags.append(text(130, 45, "Сітка (Grid / NDRange)", size=16, bold=True, color=INK))
    frags.append(text(500, 45, "Мільйони потоків, розбиті на незалежні блоки", size=12, color=MUTED))

    # Streaming Multiprocessors (SM)
    sms = [
        ("Мультипроцесор SM 0", 40, 70),
        ("Мультипроцесор SM 1", 450, 70),
    ]

    for sm_title, sm_x, sm_y in sms:
        frags.append(rect(sm_x, sm_y, 390, 335, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
        frags.append(text(sm_x + 195, sm_y + 24, sm_title, size=13, bold=True, color=NEG))

        # Thread Block inside SM
        frags.append(rect(sm_x + 15, sm_y + 35, 360, 130, fill="#ffffff", stroke="#93c5fd", rx=5))
        frags.append(text(sm_x + 195, sm_y + 55, "Блок потоків (Thread Block / CTA)", size=12, bold=True, color=INK))
        frags.append(text(sm_x + 195, sm_y + 72, "Спільна пам'ять (Shared Memory) + Бар'єри (__syncthreads)", size=10, color=MUTED))

        # Warps inside Block
        warps = [("Варп 0 (0..31)", sm_x + 20), ("Варп 1 (32..63)", sm_x + 140), ("Варп N (...)", sm_x + 260)]
        for w_title, wx in warps:
            frags.append(rect(wx, sm_y + 82, 110, 70, fill="#fef9c3", stroke="#eab308", rx=3))
            frags.append(text(wx + 55, sm_y + 105, w_title, size=11, bold=True, color="#854d0e"))
            frags.append(text(wx + 55, sm_y + 125, "32 потоки", size=10, color=MUTED))
            frags.append(text(wx + 55, sm_y + 140, "синхронно", size=9, color=MUTED))

        # Апаратні ресурси SM
        frags.append(rect(sm_x + 15, sm_y + 175, 360, 145, fill="#ffffff", stroke="#94a3b8", rx=5))
        frags.append(text(sm_x + 195, sm_y + 195, "Апаратні ресурси SM", size=11, bold=True, color=INK))

        # Warp Schedulers
        frags.append(rect(sm_x + 25, sm_y + 208, 165, 48, fill="#f1f5f9", stroke="#64748b", rx=3))
        frags.append(text(sm_x + 107, sm_y + 228, "Планувальники варпів", size=10, bold=True))
        frags.append(text(sm_x + 107, sm_y + 245, "Warp Schedulers (4 шт.)", size=9, color=MUTED))

        # Register File
        frags.append(rect(sm_x + 200, sm_y + 208, 165, 48, fill="#fef2f2", stroke=POS, rx=3))
        frags.append(text(sm_x + 282, sm_y + 228, "Регістровий файл", size=10, bold=True, color=POS))
        frags.append(text(sm_x + 282, sm_y + 245, "64K x 32-bit (нуль копіювань)", size=9, color=MUTED))

        # Execution units
        frags.append(rect(sm_x + 25, sm_y + 266, 340, 44, fill="#ecfdf5", stroke=FIELD, rx=3))
        frags.append(text(sm_x + 195, sm_y + 284, "Виконавчі блоки: 128 FP32 ALUs + 64 INT32", size=10, bold=True, color=FIELD))
        frags.append(text(sm_x + 195, sm_y + 300, "Виконують інструкції готових варпів щотакту", size=9, color=MUTED))

    render(os.path.join(IMG_DIR, "execution-hierarchy.svg"), w, h, *frags)


def fig_warp_divergence():
    """Фігура 3: Дивергенція варпу: розгалуження, маскування та серіалізація виконання."""
    w, h = 880, 440
    frags = []

    # Заголовок та опис
    frags.append(text(440, 30, "Дивергенція варпу: виконання гілок if (threadIdx.x < 16) / else", size=15, bold=True, color=INK))
    frags.append(text(440, 52, "Один лічильник команд (PC) змушує виконувати обидві гілки послідовно через активну маску", size=12, color=MUTED))

    # Хід у часі
    times = [
        ("Крок 1: Обчислення умови if", 80, "#f8fafc", "#cbd5e1"),
        ("Крок 2: Виконання гілки THEN (потоки 0..15)", 180, "#eff6ff", NEG),
        ("Крок 3: Виконання гілки ELSE (потоки 16..31)", 280, "#fff7ed", POS),
    ]

    for title, y, f_col, s_col in times:
        frags.append(rect(40, y, 800, 85, fill=f_col, stroke=s_col, rx=6))
        frags.append(text(180, y + 25, title, size=12, bold=True, color=INK))

    # Стан потоків на Кроці 1
    frags.append(text(180, 125, "Всі 32 потоки обчислюють умову розгалуження", size=10, color=MUTED))
    for i in range(8):
        x = 420 + i * 50
        lbl = "T%d" % i if i < 4 else ("..." if i < 6 else "T%d" % (26 + i))
        frags.append(rect(x, 98, 44, 30, fill="#e2e8f0", stroke="#94a3b8", rx=3))
        frags.append(text(x + 22, 117, lbl, size=10, bold=True))
    frags.append(text(620, 150, "Маска: 1111...0000 (умова ділить варп навпіл)", size=10, color=INK))

    # Стан потоків на Кроці 2 (THEN)
    frags.append(text(180, 225, "Активна маска вмикає ліву половину, права спить", size=10, color=MUTED))
    for i in range(8):
        x = 420 + i * 50
        lbl = "T%d" % i if i < 4 else ("..." if i < 6 else "T%d" % (26 + i))
        is_active = i < 4
        f_box = "#bbf7d0" if is_active else "#f1f5f9"
        s_box = FIELD if is_active else "#cbd5e1"
        txt_col = FIELD if is_active else "#94a3b8"
        status = "ВКЛ" if is_active else "ВИМК"
        frags.append(rect(x, 198, 44, 46, fill=f_box, stroke=s_box, rx=3))
        frags.append(text(x + 22, 216, lbl, size=10, bold=True, color=INK))
        frags.append(text(x + 22, 235, status, size=9, bold=True, color=txt_col))

    frags.append(text(620, 252, "Обчислювальна ефективність = 50% (16 потоків простоюють)", size=10, bold=True, color=POS))

    # Стан потоків на Кроці 3 (ELSE)
    frags.append(text(180, 325, "Маска інвертується: права половина активна, ліва спить", size=10, color=MUTED))
    for i in range(8):
        x = 420 + i * 50
        lbl = "T%d" % i if i < 4 else ("..." if i < 6 else "T%d" % (26 + i))
        is_active = i >= 4
        f_box = "#fed7aa" if is_active else "#f1f5f9"
        s_box = POS if is_active else "#cbd5e1"
        txt_col = POS if is_active else "#94a3b8"
        status = "ВКЛ" if is_active else "ВИМК"
        frags.append(rect(x, 298, 44, 46, fill=f_box, stroke=s_box, rx=3))
        frags.append(text(x + 22, 316, lbl, size=10, bold=True, color=INK))
        frags.append(text(x + 22, 335, status, size=9, bold=True, color=txt_col))

    frags.append(text(620, 352, "Сумарний час = Час(THEN) + Час(ELSE) замість max(T1, T2)", size=10, bold=True, color=POS))

    # Точка реконвергенції
    frags.append(rect(40, 385, 800, 36, fill="#f0fdf4", stroke=FIELD, rx=4))
    frags.append(text(440, 408, "Точка реконвергенції: маска відновлюється (1111...1111), варп знову працює зі 100% ККД", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "warp-divergence.svg"), w, h, *frags)


def fig_latency_hiding():
    """Фігура 4: Планувальник варпів і приховування латентності (Latency Hiding)."""
    w, h = 880, 370
    frags = []

    frags.append(text(440, 25, "Приховування латентності VRAM через перемикання варпів за 0 тактів", size=15, bold=True, color=INK))
    frags.append(text(440, 45, "Поки Варп 0 чекає на дані з пам'яті (400 тактів), АЛП завантажені обчисленнями інших варпів", size=12, color=MUTED))

    # Часова шкала
    frags.append(line(80, 80, 820, 80, color=LINE, sw=2))
    frags.append(arrow(800, 80, 825, 80, color=LINE, sw=2))
    frags.append(text(845, 84, "Час (такти)", size=11, bold=True, color=INK))

    cycles = [
        ("Такт 0", 110),
        ("Такт 1", 230),
        ("Такт 2", 350),
        ("Такт 3", 470),
        ("... 400 тактів", 590),
        ("Такт 401", 720),
    ]

    for lbl, cx in cycles:
        frags.append(line(cx, 75, cx, 85, color=LINE, sw=1.5))
        frags.append(text(cx, 70, lbl, size=10, bold=True, color=MUTED))

    # Рядки варпів
    warp_rows = [
        ("Варп 0", 120, "#eff6ff", NEG),
        ("Варп 1", 170, "#f0fdf4", FIELD),
        ("Варп 2", 220, "#fefce8", "#ca8a04"),
        ("Варп 3", 270, "#fdf2f8", "#db2777"),
    ]

    for w_name, y, bg_col, br_col in warp_rows:
        frags.append(rect(40, y - 18, 70, 38, fill=bg_col, stroke=br_col, rx=4))
        frags.append(text(75, y + 5, w_name, size=11, bold=True, color=br_col))

    # Дії на часовій шкалі
    # Варп 0: Запит на читання з VRAM
    frags.append(rect(100, 100, 100, 40, fill="#fee2e2", stroke=POS, rx=4))
    frags.append(text(150, 117, "LD.E (Global)", size=10, bold=True, color=POS))
    frags.append(text(150, 132, "Запит у VRAM", size=9, color=MUTED))

    # Варп 0 очікує 400 тактів (пунктир)
    frags.append(rect(210, 108, 480, 24, fill="#fef2f2", stroke=POS, rx=3, sw=1))
    frags.append(text(450, 124, "Очікування даних із глобальної пам'яті (~400 тактів латентності VRAM)", size=10, color=POS))

    # Варп 0 отримує дані й рахує
    frags.append(rect(700, 100, 100, 40, fill="#dbeafe", stroke=NEG, rx=4))
    frags.append(text(750, 117, "FADD (Math)", size=10, bold=True, color=NEG))
    frags.append(text(750, 132, "Дані готові", size=9, color=FIELD))

    # Варп 1 рахує в такт 1
    frags.append(rect(220, 150, 100, 40, fill="#dcfce7", stroke=FIELD, rx=4))
    frags.append(text(270, 167, "FFMA (Math)", size=10, bold=True, color=FIELD))
    frags.append(text(270, 182, "Обчислення", size=9, color=MUTED))

    # Варп 2 рахує в такт 2
    frags.append(rect(340, 200, 100, 40, fill="#fef08a", stroke="#ca8a04", rx=4))
    frags.append(text(390, 217, "FMUL (Math)", size=10, bold=True, color="#854d0e"))
    frags.append(text(390, 232, "Обчислення", size=9, color=MUTED))

    # Варп 3 рахує в такт 3
    frags.append(rect(460, 250, 100, 40, fill="#fbcfe8", stroke="#db2777", rx=4))
    frags.append(text(510, 267, "FADD (Math)", size=10, bold=True, color="#9d174d"))
    frags.append(text(510, 282, "Обчислення", size=9, color=MUTED))

    # Підсумок
    frags.append(rect(40, 315, 800, 36, fill="#f8fafc", stroke="#64748b", rx=4))
    frags.append(text(440, 337, "Результат: АЛП зайняті на 100% кожного такту, час очікування пам'яті повністю прихований", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "latency-hiding-scheduler.svg"), w, h, *frags)


def fig_memory_coalescing():
    """Фігура 5: Коалесцинг пам'яті: злитий доступ (1 транзакція) проти розрізненого (32 транзакції)."""
    w, h = 880, 410
    frags = []

    frags.append(text(440, 25, "Коалесцинг пам'яті: злиття запитів варпу до глобальної VRAM", size=15, bold=True, color=INK))

    # Верхня панель: Coalesced
    frags.append(rect(30, 45, 820, 165, fill="#f0fdf4", stroke=FIELD, rx=8))
    frags.append(text(220, 68, "Злитий доступ (Coalesced Access): ідеально", size=13, bold=True, color=FIELD))
    frags.append(text(220, 86, "Потік i читає елемент a[base + i] (послідовні 4 байти float)", size=10, color=MUTED))

    # Потоки
    for i in range(8):
        x = 50 + i * 98
        lbl = "Потік %d" % i if i < 6 else ("..." if i == 6 else "Потік 31")
        frags.append(rect(x, 100, 90, 28, fill="#dcfce7", stroke=FIELD, rx=3))
        frags.append(text(x + 45, 118, lbl, size=10, bold=True, color=FIELD))
        frags.append(arrow(x + 45, 128, x + 45, 145, color=FIELD))

    # 128-байтова кеш-лінія
    frags.append(rect(50, 148, 776, 32, fill="#bbf7d0", stroke=FIELD, rx=4, sw=2))
    frags.append(text(438, 168, "1 суцільна 128-байтова транзакція шини (32 потоки x 4 байти = 128 байтів, ККД шини = 100%)", size=11, bold=True, color=INK))

    frags.append(text(438, 198, "Шина пам'яті завантажена повністю корисною інформацією за 1 звернення", size=10, color=FIELD))

    # Нижня панель: Non-coalesced / Strided
    frags.append(rect(30, 225, 820, 170, fill="#fef2f2", stroke=POS, rx=8))
    frags.append(text(240, 248, "Незлитий доступ (Strided / Non-coalesced): деградація", size=13, bold=True, color=POS))
    frags.append(text(240, 266, "Потік i читає елемент a[base + i * 32] (крок через масив структур AoS)", size=10, color=MUTED))

    # Потоки з розрізненими стрілками
    for i in range(8):
        x = 50 + i * 98
        lbl = "Потік %d" % i if i < 6 else ("..." if i == 6 else "Потік 31")
        frags.append(rect(x, 280, 90, 28, fill="#fee2e2", stroke=POS, rx=3))
        frags.append(text(x + 45, 298, lbl, size=10, bold=True, color=POS))
        frags.append(arrow(x + 45, 308, x + 45, 325, color=POS))

    # 32 окремі сектори
    for i in range(8):
        x = 50 + i * 98
        lbl = "Сектор %d" % i if i < 6 else ("..." if i == 6 else "Сектор 31")
        frags.append(rect(x, 328, 90, 28, fill="#fca5a5", stroke=POS, rx=3))
        frags.append(text(x + 45, 345, lbl, size=9, bold=True, color=INK))

    frags.append(text(438, 380, "32 окремі 32-байтові транзакції! З 1024 байтів шини корисно використано лише 128 (ККД = 12.5%, пропускна здатність впала у 8-32 рази)", size=10, bold=True, color=POS))

    render(os.path.join(IMG_DIR, "memory-coalescing.svg"), w, h, *frags)


def fig_shared_memory_banks():
    """Фігура 6: Спільна пам'ять (Shared Memory) та конфлікти банків (Bank Conflicts)."""
    w, h = 880, 420
    frags = []

    frags.append(text(440, 25, "Організація спільної пам'яті (Shared Memory) у 32 банки по 4 байти", size=15, bold=True, color=INK))
    frags.append(text(440, 45, "Слова пам'яті чергуються між банками: Word 0 в Bank 0, Word 1 в Bank 1, ..., Word 32 знову в Bank 0", size=11, color=MUTED))

    panels = [
        ("Випадок А: Безконфліктний доступ (1 такт)", 30, 70, 260, "#f0fdf4", FIELD),
        ("Випадок Б: Трансляція (Broadcast, 1 такт)", 310, 70, 260, "#eff6ff", NEG),
        ("Випадок В: 2-кратний конфлікт банків (2 такти)", 590, 70, 260, "#fef2f2", POS),
    ]

    for p_title, px, py, pw, f_col, s_col in panels:
        frags.append(rect(px, py, pw, 330, fill=f_col, stroke=s_col, rx=6))
        frags.append(text(px + pw / 2, py + 22, p_title, size=10, bold=True, color=s_col))

    # Випадок А: 1-to-1
    frags.append(text(160, 115, "Потік i читає Банк i", size=10, color=MUTED))
    for i in range(4):
        y = 135 + i * 36
        frags.append(rect(45, y, 70, 26, fill="#dcfce7", stroke=FIELD, rx=3))
        frags.append(text(80, y + 17, "Потік %d" % i, size=10, bold=True))
        frags.append(arrow(115, y + 13, 170, y + 13, color=FIELD))
        frags.append(rect(170, y, 105, 26, fill="#bbf7d0", stroke=FIELD, rx=3))
        frags.append(text(222, y + 17, "Банк %d [Слово %d]" % (i, i), size=9, bold=True))

    frags.append(text(160, 310, "32 потоки звертаються", size=10, bold=True))
    frags.append(text(160, 328, "до 32 різних банків", size=10, bold=True))
    frags.append(text(160, 360, "ККД = 100%, 1 такт", size=12, bold=True, color=FIELD))

    # Випадок Б: Broadcast
    frags.append(text(440, 115, "Усі потоки читають те саме слово", size=10, color=MUTED))
    for i in range(4):
        y = 135 + i * 36
        frags.append(rect(325, y, 70, 26, fill="#dbeafe", stroke=NEG, rx=3))
        frags.append(text(360, y + 17, "Потік %d" % i, size=10, bold=True))
        frags.append(arrow(395, y + 13, 455, 185, color=NEG))

    frags.append(rect(455, 170, 100, 32, fill="#bfdbfe", stroke=NEG, rx=3))
    frags.append(text(505, 190, "Банк 0 [Слово 0]", size=10, bold=True))

    frags.append(text(440, 310, "Апаратний Broadcast:", size=10, bold=True))
    frags.append(text(440, 328, "одне слово летить усім", size=10, bold=True))
    frags.append(text(440, 360, "Конфлікту немає, 1 такт", size=12, bold=True, color=NEG))

    # Випадок В: 2-way bank conflict
    frags.append(text(720, 115, "Потоки читають різні слова одного банку", size=9, color=MUTED))

    # Потік 0 -> Банк 0 (Слово 0)
    frags.append(rect(605, 135, 65, 26, fill="#fee2e2", stroke=POS, rx=3))
    frags.append(text(637, 152, "Потік 0", size=10, bold=True))
    frags.append(arrow(670, 148, 725, 148, color=POS))
    frags.append(rect(725, 135, 110, 26, fill="#fca5a5", stroke=POS, rx=3))
    frags.append(text(780, 152, "Банк 0 [Слово 0]", size=9, bold=True))

    # Потік 16 -> Банк 0 (Слово 32)
    frags.append(rect(605, 175, 65, 26, fill="#fee2e2", stroke=POS, rx=3))
    frags.append(text(637, 192, "Потік 16", size=10, bold=True))
    frags.append(arrow(670, 188, 725, 188, color=POS))
    frags.append(rect(725, 175, 110, 26, fill="#fca5a5", stroke=POS, rx=3))
    frags.append(text(780, 192, "Банк 0 [Слово 32]", size=9, bold=True))

    frags.append(text(720, 230, "Різні адреси в одному банку!", size=10, bold=True, color=POS))
    frags.append(text(720, 250, "Апаратна серіалізація:", size=10, bold=True))
    frags.append(text(720, 270, "Такт 1: читання для Потоку 0", size=9, color=MUTED))
    frags.append(text(720, 290, "Такт 2: читання для Потоку 16", size=9, color=MUTED))
    frags.append(text(720, 360, "Швидкість падає вдвічі (2 такти)", size=11, bold=True, color=POS))

    render(os.path.join(IMG_DIR, "shared-memory-banks.svg"), w, h, *frags)


def main():
    print("Генерація SVG-фігур для simt-gpu-execution...")
    fig_simd_vs_simt()
    fig_execution_hierarchy()
    fig_warp_divergence()
    fig_latency_hiding()
    fig_memory_coalescing()
    fig_shared_memory_banks()
    print("Фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
