# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Витік пам'яті» (memory-leak)."""

import os
import sys

# Підключаємо спільну бібліотеку svgkit з scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_why_leak_happens():
    """Фігура 1: Механіка витоку: втрата вказівника на зайнятий блок купи."""
    w, h = 820, 430
    frags = []

    # Заголовки стовпців
    frags.append(textbox(200, 35, "Стек процесу (локальні змінні)", size=15, bold=True, fill="#eaf2f8", stroke="#2980b9")[0])
    frags.append(textbox(620, 35, "Купа (Heap Memory Manager)", size=15, bold=True, fill="#fef9e7", stroke="#f39c12")[0])

    # Сценарій А: Нормальне звільнення
    frags.append(rect(40, 75, 330, 150, fill="none", stroke="#27ae60", rx=8, sw=1.5))
    frags.append(text(205, 98, "Сценарій А: Коректне звільнення", size=13, bold=True, color="#1e8449"))
    frags.append(textbox(205, 135, "Покажчик ptr = 0x7fa0\n(на стеку в кадрі функції)", size=12, fill="#ffffff", stroke="#27ae60")[0])
    frags.append(textbox(205, 190, "Виклик free(ptr) перед виходом\n→ блок повернуто алокатору", size=11, fill="#e8f8f5", stroke="#27ae60", color="#196f3d")[0])

    # Блок на купі А (звільнений)
    frags.append(textbox(620, 140, "Блок пам'яті 0x7fa0 [4 KB]\nСтатус: ВІЛЬНИЙ (FREED)\nДоступний для повторного malloc", size=12, fill="#e8f8f5", stroke="#27ae60", color="#196f3d")[0])
    frags.append(arrow(340, 135, 480, 135, color="#27ae60", sw=2))
    frags.append(text(410, 125, "free()", size=11, bold=True, color="#27ae60"))

    # Сценарій Б: Витік пам'яті
    frags.append(rect(40, 250, 330, 160, fill="none", stroke="#c0392b", rx=8, sw=1.5))
    frags.append(text(205, 273, "Сценарій Б: Витік пам'яті (Memory Leak)", size=13, bold=True, color="#922b21"))
    frags.append(textbox(205, 315, "Кадр функції завершився,\nпокажчик ptr ЗНИЩЕНО зі стека", size=12, fill="#ffffff", stroke="#c0392b", color="#922b21")[0])
    frags.append(textbox(205, 375, "Адресу 0x8bc0 назавжди втрачено;\nпрограма не має доступу", size=11, fill="#fadbd8", stroke="#c0392b", color="#78281f")[0])

    # Блок на купі Б (витік)
    frags.append(textbox(620, 325, "Блок пам'яті 0x8bc0 [4 KB]\nСтатус: ЗАЙНЯТИЙ (ALLOCATED)\nВказівників немає (UNREACHABLE)", size=12, fill="#fadbd8", stroke="#c0392b", color="#78281f")[0])
    
    # Перекреслена стрілка зв'язку
    frags.append(line(340, 315, 470, 315, color="#c0392b", sw=2, dash="5,4"))
    frags.append(line(395, 300, 415, 330, color="#c0392b", sw=3))
    frags.append(line(415, 300, 395, 330, color="#c0392b", sw=3))
    frags.append(text(405, 290, "Втрачено зв'язок", size=11, bold=True, color="#c0392b"))

    render(os.path.join(OUT_DIR, "why-leak-happens.svg"), w, h, *frags)


def fig_true_leak_vs_stale_ref():
    """Фігура 2: Справжній витік проти логічного утримання посилань."""
    w, h = 820, 400
    frags = []

    # Ліва колонка: Справжній витік (C / C++)
    frags.append(rect(30, 20, 365, 360, fill="none", stroke="#c0392b", rx=10, sw=1.5))
    frags.append(textbox(212, 55, "Справжній витік (True Leak)\nМови без GC (C, C++, Assembly)", size=14, bold=True, fill="#fadbd8", stroke="#c0392b", color="#78281f")[0])

    frags.append(textbox(212, 125, "Root-покажчик на стеку\nзнищено або перезаписано", size=12, fill="#f4f6f7", stroke="#7f8c8d")[0])
    frags.append(line(212, 155, 212, 185, color="#c0392b", sw=2, dash="4,4"))
    frags.append(text(212, 175, "✕ немає зв'язку", size=11, bold=True, color="#c0392b"))

    frags.append(textbox(212, 230, "Об'єкт у купі (Heap Object)\nФізично зайнятий в алокаторі,\nале недосяжний (Unreachable)", size=12, fill="#fce4ec", stroke="#c0392b", color="#880e4f")[0])
    frags.append(textbox(212, 320, "Наслідок: пам'ять неможливо\nзвільнити жодним штатним кодом\nдо завершення процесу", size=11, fill="#fff3e0", stroke="#e67e22", color="#d35400")[0])

    # Права колонка: Логічне утримання (Java, JS, Python, Go)
    frags.append(rect(425, 20, 365, 360, fill="none", stroke="#2980b9", rx=10, sw=1.5))
    frags.append(textbox(607, 55, "Логічне утримання (Stale Reference)\nКеровані мови з GC (Java, JS, Go)", size=14, bold=True, fill="#ebf5fb", stroke="#2980b9", color="#1b4f72")[0])

    frags.append(textbox(607, 125, "GC Root (статична мапа,\nглобальний Event Listener, замикання)", size=12, fill="#d4e6f1", stroke="#2980b9", color="#154360")[0])
    frags.append(arrow(607, 155, 607, 195, color="#2980b9", sw=2))
    frags.append(text(655, 175, "сильне посилання", size=10, color="#2980b9"))

    frags.append(textbox(607, 230, "Непотрібний об'єкт (Stale Data)\nДані більше ніколи не будуть потрібні,\nале GC вважає їх живими (Reachable)", size=12, fill="#d6eaf8", stroke="#2980b9", color="#154360")[0])
    frags.append(textbox(607, 320, "Наслідок: GC не має права\nвидалити живий ланцюг об'єктів;\nпам'ять невпинно зростає", size=11, fill="#fff3e0", stroke="#e67e22", color="#d35400")[0])

    render(os.path.join(OUT_DIR, "true-leak-vs-stale-reference.svg"), w, h, *frags)


def fig_system_degradation_oom():
    """Фігура 3: Каскадна деградація ОС: робочий набір, свопінг та OOM Killer."""
    w, h = 820, 380
    frags = []

    # Фаза 1
    frags.append(rect(30, 30, 230, 320, fill="none", stroke="#27ae60", rx=8, sw=1.5))
    frags.append(textbox(145, 65, "Фаза 1: Розбухання\n(Working Set Bloat)", size=13, bold=True, fill="#d5f5e3", stroke="#27ae60", color="#196f3d")[0])
    frags.append(textbox(145, 150, "Анонімна пам'ять (RSS)\nпостійно зростає.\nКупа витісняє кеші сторінок\n(Page Cache).", size=11, fill="#ffffff", stroke="#a9dfbf")[0])
    frags.append(textbox(145, 265, "Симптом:\nЗниження швидкодії дискового I/O,\nпадіння пропускної здатності", size=11, fill="#eafaf1", stroke="#27ae60", color="#145a32")[0])

    # Стрілка 1 -> 2
    frags.append(arrow(265, 180, 295, 180, color="#e67e22", sw=2.5))

    # Фаза 2
    frags.append(rect(300, 30, 230, 320, fill="none", stroke="#f39c12", rx=8, sw=1.5))
    frags.append(textbox(415, 65, "Фаза 2: Свопінг і пробуксовка\n(Page Thrashing)", size=13, bold=True, fill="#fdebd0", stroke="#f39c12", color="#9c640c")[0])
    frags.append(textbox(415, 150, "RAM вичерпано.\nЯдро витісняє сторінки в swap.\nkswapd споживає 100% CPU.\nДисковий I/O заблоковано.", size=11, fill="#ffffff", stroke="#f9e79f")[0])
    frags.append(textbox(415, 265, "Симптом:\nЗатримки (latency) стрибають\nвід мілісекунд до десятків секунд;\nсистема «зависає»", size=11, fill="#fef5e7", stroke="#f39c12", color="#7e5109")[0])

    # Стрілка 2 -> 3
    frags.append(arrow(535, 180, 565, 180, color="#c0392b", sw=2.5))

    # Фаза 3
    frags.append(rect(570, 30, 220, 320, fill="none", stroke="#c0392b", rx=8, sw=1.5))
    frags.append(textbox(680, 65, "Фаза 3: Спрацювання\nLinux OOM Killer", size=13, bold=True, fill="#fadbd8", stroke="#c0392b", color="#78281f")[0])
    frags.append(textbox(680, 150, "Вичерпано і RAM, і Swap.\nЯдро обчислює oom_score:\npoints = RSS + swap_usage.\nSIGKILL надсилається процесу.", size=11, fill="#ffffff", stroke="#f5b7b1")[0])
    frags.append(textbox(680, 265, "Симптом:\nАварійне вбивство сервісу\nабо випадкового сусіда\n(out-of-memory crash)", size=11, fill="#fdedec", stroke="#c0392b", color="#641e16")[0])

    render(os.path.join(OUT_DIR, "system-degradation-oom.svg"), w, h, *frags)


def fig_nonvirtual_dtor():
    """Фігура 4: Витік ресурсів при невіртуальному деструкторі."""
    w, h = 820, 410
    frags = []

    # Невіртуальний деструктор (Помилка)
    frags.append(rect(30, 20, 365, 370, fill="none", stroke="#c0392b", rx=8, sw=1.5))
    frags.append(textbox(212, 55, "Без virtual ~Base()\n(Статичне зв'язування деструктора)", size=13, bold=True, fill="#fadbd8", stroke="#c0392b", color="#78281f")[0])
    frags.append(textbox(212, 120, "Base* p = new Derived();\ndelete p; // виклик через Base*", size=12, fill="#ffffff", stroke="#c0392b")[0])

    frags.append(textbox(212, 190, "1. Викликається Base::~Base() ✓", size=11, fill="#d5f5e3", stroke="#27ae60", color="#196f3d")[0])
    frags.append(textbox(212, 250, "2. Derived::~Derived() НЕ викликається! ✕\n(динамічний буфер Derived::buf витікає)", size=11, fill="#fadbd8", stroke="#c0392b", color="#78281f")[0])
    frags.append(textbox(212, 340, "Результат: витік внутрішніх ресурсів\nнащадка та невизначена поведінка (UB)", size=11, fill="#fadbd8", stroke="#c0392b", color="#78281f")[0])

    # Віртуальний деструктор (Виправлено)
    frags.append(rect(425, 20, 365, 370, fill="none", stroke="#27ae60", rx=8, sw=1.5))
    frags.append(textbox(607, 55, "З virtual ~Base() = default;\n(Динамічна диспетчеризація vtable)", size=13, bold=True, fill="#d5f5e3", stroke="#27ae60", color="#196f3d")[0])
    frags.append(textbox(607, 120, "Base* p = new Derived();\ndelete p; // виклик через vptr", size=12, fill="#ffffff", stroke="#27ae60")[0])

    frags.append(textbox(607, 190, "1. Викликається Derived::~Derived() ✓\n(звільняє буфер Derived::buf)", size=11, fill="#d5f5e3", stroke="#27ae60", color="#196f3d")[0])
    frags.append(textbox(607, 250, "2. Автоматично викликається Base::~Base() ✓", size=11, fill="#d5f5e3", stroke="#27ae60", color="#196f3d")[0])
    frags.append(textbox(607, 340, "Результат: повне і коректне очищення\nвсієї ієрархії об'єкта без витоків", size=11, fill="#d5f5e3", stroke="#27ae60", color="#196f3d")[0])

    render(os.path.join(OUT_DIR, "nonvirtual-dtor-leak.svg"), w, h, *frags)


def fig_sanitizers_detection():
    """Фігура 5: Спектр інструментів виявлення: Valgrind, LSan та eBPF memleak."""
    w, h = 820, 390
    frags = []

    # Інструмент 1: Valgrind Memcheck
    frags.append(rect(30, 25, 235, 340, fill="none", stroke="#8e44ad", rx=8, sw=1.5))
    frags.append(textbox(147, 65, "Valgrind Memcheck\n(Емуляція двійкового коду)", size=13, bold=True, fill="#f4ecf7", stroke="#8e44ad", color="#5b2c6f")[0])
    frags.append(textbox(147, 140, "Як працює:\nJIT-трансляція у VEX IR,\nпобайтова тіньова пам'ять (A/V-біти),\nдерево всіх виділень.", size=11, fill="#ffffff", stroke="#d2b4de")[0])
    frags.append(textbox(147, 235, "Швидкодія: 10×–30× сповільнення.\nДе застосовувати:\nГлибоке налагодження в тестах,\nнепридатний для продакшену.", size=11, fill="#f5eef8", stroke="#8e44ad", color="#4a235a")[0])
    frags.append(textbox(147, 320, "Класифікація витоків:\nDefinite, Indirect, Possible, Reachable", size=10, fill="#ebdef0", stroke="#8e44ad")[0])

    # Інструмент 2: LeakSanitizer (LSan / ASan)
    frags.append(rect(292, 25, 235, 340, fill="none", stroke="#2980b9", rx=8, sw=1.5))
    frags.append(textbox(409, 65, "LeakSanitizer (LSan)\n(Компіляторна інструментація)", size=13, bold=True, fill="#ebf5fb", stroke="#2980b9", color="#1b4f72")[0])
    frags.append(textbox(409, 140, "Як працює:\nПерехоплення malloc/free,\nMark-and-Sweep сканування коренів\n(стек, регістри, .data/.bss) при exit().", size=11, fill="#ffffff", stroke="#aed6f1")[0])
    frags.append(textbox(409, 235, "Швидкодія: ~1.5×–2× сповільнення.\nДе застосовувати:\nCI/CD пайплайни, інтеграційні тести,\nщоденна розробка (-fsanitize=leak).", size=11, fill="#eaf2f8", stroke="#2980b9", color="#154360")[0])
    frags.append(textbox(409, 320, "Миттєвий звіт:\nСтек виклику точки алокації", size=10, fill="#d4e6f1", stroke="#2980b9")[0])

    # Інструмент 3: eBPF memleak
    frags.append(rect(555, 25, 235, 340, fill="none", stroke="#27ae60", rx=8, sw=1.5))
    frags.append(textbox(672, 65, "eBPF memleak\n(Трасування ядра наживо)", size=13, bold=True, fill="#eafaf1", stroke="#27ae60", color="#145a32")[0])
    frags.append(textbox(672, 140, "Як працює:\nUprobes на libc malloc/free,\nагрегація активних алокацій у BPF-мапах\nбез зупинки процесу.", size=11, fill="#ffffff", stroke="#a9dfbf")[0])
    frags.append(textbox(672, 235, "Швидкодія: < 2% накладних витрат.\nДе застосовувати:\nЖивий продакшен під навантаженням,\nпошук повільних витоків на серверах.", size=11, fill="#e8f8f5", stroke="#27ae60", color="#0e6251")[0])
    frags.append(textbox(672, 320, "Аналіз у часі:\nСтек + тривалість життя блоку", size=10, fill="#d5f5e3", stroke="#27ae60")[0])

    render(os.path.join(OUT_DIR, "sanitizers-detection-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_why_leak_happens()
    fig_true_leak_vs_stale_ref()
    fig_system_degradation_oom()
    fig_nonvirtual_dtor()
    fig_sanitizers_detection()
    print("Всі фігури для memory-leak згенеровано успішно.")
