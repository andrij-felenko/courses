# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми use-after-free."""

import sys
import os

# scripts/ у корені репо: з root/eng/sf-security/use-after-free — це 4 рівні вгору
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_uaf_lifecycle():
    """Ілюстрація 1: Життєвий цикл вразливості Use-After-Free."""
    w, h = 880, 360
    frags = []

    # 4 етапи
    steps = [
        ("1. Виділення пам'яті", 115, "#eaf0fd", NEG),
        ("2. Звільнення (free)", 330, "#fdecea", POS),
        ("3. Перевиділення", 545, "#e8f8f0", FIELD),
        ("4. Розіменування UAF", 760, "#fdf0ed", POS),
    ]

    for title, cx, bg_c, border_c in steps:
        frags.append(fitbox(cx - 95, 20, 190, 34, title, size=13, bold=True, fill=bg_c, stroke=border_c))

    # Стрілки між етапами зверху
    frags.append(arrow(215, 37, 230, 37, color=LINE, sw=1.5))
    frags.append(arrow(430, 37, 445, 37, color=LINE, sw=1.5))
    frags.append(arrow(645, 37, 660, 37, color=LINE, sw=1.5))

    # Крок 1 вміст: Вказівник P -> Об'єкт А
    frags.append(fitbox(30, 75, 170, 50, "Вказівник ptr\n(адреса 0x6000)", size=12, fill=FILL, stroke=LINE))
    frags.append(arrow(115, 130, 115, 170, color=NEG, sw=1.8))
    frags.append(fitbox(25, 175, 180, 140, "Блок 0x6000 (Об'єкт A)\n-------------------\nint user_id = 42\nvoid (*fn)() = do_work\nСтатус: АКТИВНИЙ", size=12, fill="#eaf0fd", stroke=NEG))

    # Крок 2 вміст: free(ptr) -> Dangling pointer -> Блок звільнено
    frags.append(fitbox(245, 75, 170, 50, "Завислий вказівник ptr\n(все ще 0x6000!)", size=12, bold=True, fill="#fdecea", stroke=POS))
    frags.append(arrow(330, 130, 330, 170, color=POS, sw=1.8))
    frags.append(fitbox(240, 175, 180, 140, "Блок 0x6000 (Вільний)\n-------------------\nПам'ять повернуто в купу\nВказівник НЕ обнулено\nСтатус: ТЕМПОРАЛЬНИЙ РОЗРИВ", size=12, fill=FILL, stroke=POS))

    # Крок 3 вміст: Новий об'єкт B займає 0x6000
    frags.append(fitbox(460, 75, 170, 50, "Вказівник new_obj\n(отримав 0x6000)", size=12, fill="#e8f8f0", stroke=FIELD))
    frags.append(arrow(545, 130, 545, 170, color=FIELD, sw=1.8))
    frags.append(fitbox(455, 175, 180, 140, "Блок 0x6000 (Об'єкт B)\n-------------------\nchar payload[16] =\n'AAAA\\xef\\xbe\\xad\\xde...'\nСтатус: ПЕРЕЗАПИСАНО", size=12, fill="#e8f8f0", stroke=FIELD))

    # Крок 4 вміст: ptr->fn() викликає дані з об'єкта B
    frags.append(fitbox(675, 75, 170, 50, "Виклик ptr->fn()\n(через старий ptr)", size=12, bold=True, fill="#fdecea", stroke=POS))
    frags.append(arrow(760, 130, 760, 170, color=POS, sw=2.0))
    frags.append(fitbox(670, 175, 180, 140, "Плутанина типів (0x6000)\n-------------------\nCPU зчитує байти з B\nяк адресу функції A\nПерехоплення потоку керування!", size=12, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG_DIR, "uaf-lifecycle.svg"), w, h, *frags)


def fig_heap_allocator_reuse():
    """Ілюстрація 2: Механіка перевикористання блоків у tcache glibc."""
    w, h = 880, 320
    frags = []

    # Заголовок tcache_entry масиву
    frags.append(fitbox(30, 20, 220, 60, "tcache_perthread_struct\n(потоковий кеш розміру 48 байт)\nentry[idx] -> head", size=12, bold=True, fill="#eaf0fd", stroke=NEG))

    # Звільнений чанк 1
    frags.append(fitbox(310, 20, 230, 110, "Звільнений чанк 1 (0x5555...20)\n-----------------------------\nprev_size | size = 0x30 | P=1\nfd: вказівник -> 0x5555...60\n(тіло блоку зберігає лінк)", size=12, fill="#fdf0ed", stroke=POS))

    # Звільнений чанк 2
    frags.append(fitbox(610, 20, 230, 110, "Звільнений чанк 2 (0x5555...60)\n-----------------------------\nprev_size | size = 0x30 | P=1\nfd: вказівник -> NULL\n(кінець списку LIFO)", size=12, fill=FILL, stroke=LINE))

    # Стрілки LIFO ланцюжка
    frags.append(arrow(255, 50, 305, 50, color=NEG, sw=1.8))
    frags.append(arrow(545, 50, 595, 50, color=POS, sw=1.8))

    # Пояснення операцій malloc/free нижче
    frags.append(fitbox(30, 160, 390, 130, "Операція free(chunk1):\n1. Алокатор записує адресу старого топа в chunk1->fd.\n2. entry[idx] = chunk1 (стек LIFO).\n3. Метадані не стираються, пам'ять не обнуляється.\nРезультат: швидке повернення без блокування арени.", size=12, fill=FILL, stroke=LINE))

    frags.append(fitbox(450, 160, 400, 130, "Наступний виклик malloc(32):\n1. Алокатор негайно повертає chunk1 (0x5555...20).\n2. entry[idx] = chunk1->fd (0x5555...60).\n3. Той самий адресний діапазон видається новому об'єкту!\nНаслідок: 100% передбачуваність для UAF-атаки.", size=12, fill="#e8f8f0", stroke=FIELD))

    render(os.path.join(IMG_DIR, "heap-allocator-reuse-tcache.svg"), w, h, *frags)


def fig_asan_shadow_memory():
    """Ілюстрація 3: Тіньова пам'ять AddressSanitizer (Shadow Memory) та отруєння."""
    w, h = 880, 340
    frags = []

    # Верхній блок: Простір пам'яті застосунку
    frags.append(fitbox(30, 20, 370, 70, "Пам'ять застосунку (8 байтів)\nАдреси: 0x1000 ... 0x1007\n[ B0 | B1 | B2 | B3 | B4 | B5 | B6 | B7 ]", size=12, bold=True, fill="#eaf0fd", stroke=NEG))

    # Формула посередині
    frags.append(fitbox(430, 25, 410, 60, "Формула адресації тіні (x86-64):\nShadow = (AppAddr >> 3) + 0x7fff8000\nМасштаб 1:8 (1 байт тіні на 8 байтів ОЗП)", size=12, bold=True, fill=FILL, stroke=LINE))

    # Стрілка трансляції
    frags.append(arrow(215, 95, 215, 135, color=NEG, sw=1.8))
    frags.append(arrow(635, 90, 635, 135, color=LINE, sw=1.5))

    # Нижній блок: Тіньовий байт і його значення
    frags.append(fitbox(30, 140, 370, 60, "Тіньовий байт (1 байт за ShadowAddr)\nВідповідає коміркам 0x1000..0x1007", size=12, bold=True, fill="#e8f8f0", stroke=FIELD))

    # Таблиця значень тіньових байтів
    frags.append(fitbox(30, 215, 810, 105, "Словник станів тіньової пам'яті (AddressSanitizer):\n  0x00      : Усі 8 байтів доступні для читання й запису (чиста виділена пам'ять)\n  0x01..07  : Перші k байтів доступні, решта 8-k байтів — у червоній зоні (хвіст буфера)\n  0xFD      : kAsanHeapFreeMagic — пам'ять звільнено (знаходиться в карантині)\n  0xFA/0xFB : kAsanHeapLeftRedzoneMagic / kAsanHeapRightRedzoneMagic — червоні межі\n  Перевірка : перед читанням/записом компілятор вставляє: if (*shadow != 0) __asan_report_error();", size=11, fill="#fdf0ed", stroke=POS))

    render(os.path.join(IMG_DIR, "asan-shadow-memory.svg"), w, h, *frags)


def fig_arm_mte():
    """Ілюстрація 4: Апаратне тегування пам'яті ARM MTE."""
    w, h = 880, 320
    frags = []

    # Верхній блок: 64-бітний вказівник з логічним тегом у верхньому байті
    frags.append(fitbox(30, 20, 810, 80, "64-бітний вказівник (Top-Byte-Ignore / ARM MTE)\n[ 63 .. 60 | 59 .. 56 (Тег = 0x9) | 55 .. 48 (TBI) | 47 ........................... 0 (Віртуальна адреса 0x6000) ]\nЛогічний тег (4 біти) зберігається прямо у вказівнику", size=12, bold=True, fill="#eaf0fd", stroke=NEG))

    # Стрілка вниз
    frags.append(arrow(220, 105, 220, 150, color=NEG, sw=1.8))
    frags.append(arrow(620, 105, 620, 150, color=POS, sw=1.8))

    # Гранула пам'яті 1 (валідний доступ)
    frags.append(fitbox(30, 155, 380, 140, "Гранула ОЗП (16 байтів)\nФізичний тег алокації = 0x9\n--------------------------------\nЛогічний тег вказівника (0x9)\n== Фізичний тег пам'яті (0x9)\nРЕЗУЛЬТАТ: Доступ дозволено (MATCH)", size=12, fill="#e8f8f0", stroke=FIELD))

    # Гранула пам'яті 2 (UAF збій після free)
    frags.append(fitbox(450, 155, 390, 140, "Гранула ОЗП після free() (16 байтів)\nФізичний тег оновлено на = 0x4\n--------------------------------\nЗавислий вказівник має тег 0x9\n0x9 != 0x4 (TAG MISMATCH!)\nРЕЗУЛЬТАТ: Апаратне переривання SIGSEGV (SEGV_MTESERR)", size=12, bold=True, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG_DIR, "arm-mte-tagging.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_uaf_lifecycle()
    fig_heap_allocator_reuse()
    fig_asan_shadow_memory()
    fig_arm_mte()
    print("Всі 4 фігури згенеровано успішно.")
