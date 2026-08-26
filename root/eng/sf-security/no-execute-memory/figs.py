# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми no-execute-memory (Пам'ять без права виконання).
Всі фігури відповідають канону: білий фон, контрастні кольори, відсутність накладань.
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_nx_pte_architecture():
    """Ілюстрація структури 64-бітного запису таблиці сторінок (PTE) та логіки перевірки MMU."""
    w, h = 920, 520
    frags = []

    # Заголовок
    frags.append(textbox(460, 25, "Апаратна перевірка біта No-Execute (NX / XD) в таблицях сторінок x86-64", size=14, bold=True, fill="#f4f6f8", stroke=LINE)[0])

    # 1. Структура 64-бітного PTE
    frags.append(text(460, 65, "Формат 64-розрядного запису таблиці сторінок (Page Table Entry, PTE)", size=12, bold=True, color=INK))

    # Відображення бітів PTE (зліва направо: 63 -> 0)
    # Біт 63: NX
    frags.append(rect(40, 85, 110, 55, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(text(95, 105, "Біт 63: NX", size=11, bold=True, color=POS))
    frags.append(text(95, 125, "1 = No-Execute", size=10, color=POS))

    # Біти 62..52: Доступні ОС / Службові
    frags.append(rect(155, 85, 130, 55, fill="#f4f6f8", stroke=LINE, sw=1.2))
    frags.append(text(220, 105, "Біти 62..52", size=11, bold=True, color=INK))
    frags.append(text(220, 125, "Ignored / OS", size=10, color=MUTED))

    # Біти 51..12: Базова адреса фізичного кадру
    frags.append(rect(290, 85, 340, 55, fill="#eaf2f8", stroke=NEG, sw=1.5))
    frags.append(text(460, 105, "Біти 51..12: Physical Frame Base Address", size=11, bold=True, color=NEG))
    frags.append(text(460, 125, "Базова фізична адреса сторінки 4 КіБ у DRAM", size=10, color=MUTED))

    # Біти 11..3: Прапорці пам'яті (G, PAT, D, A, PCD, PWT)
    frags.append(rect(635, 85, 140, 55, fill="#f4f6f8", stroke=LINE, sw=1.2))
    frags.append(text(705, 105, "Біти 11..3", size=11, bold=True, color=INK))
    frags.append(text(705, 125, "G, PAT, D, A, PCD", size=10, color=MUTED))

    # Біти 2..0: U/S, R/W, P
    frags.append(rect(780, 85, 100, 55, fill="#eafaf1", stroke=FIELD, sw=1.5))
    frags.append(text(830, 105, "U/S | R/W | P", size=11, bold=True, color=FIELD))
    frags.append(text(830, 125, "Біти 2, 1, 0", size=10, color=MUTED))

    # Лінія розділу
    frags.append(line(40, 160, 880, 160, color="#d1d5db", sw=1.0, dash="4,4"))

    # 2. Логіка перевірки блоком MMU
    # Процесорне ядро / Instruction Fetch
    b_cpu, _, _ = textbox(160, 240, "Процесорне ядро (CPU)\nФаза Instruction Fetch\nЗчитування за адресою RIP", size=11, bold=True, fill="#ffffff", stroke=LINE)
    frags.append(b_cpu)

    # Блок MMU / Перевірка PTE
    b_mmu, _, _ = textbox(460, 240, "Блок керування пам'яттю (MMU)\nТрансляція адреси крізь CR3 -> PTE\nАпаратна перевірка біта 63 (NX)", size=11, bold=True, fill="#f4f6f8", stroke=LINE)
    frags.append(b_mmu)

    # Стрілка від CPU до MMU
    frags.append(arrow(260, 240, 320, 240, color=LINE, sw=1.8))
    frags.append(text(290, 225, "Fetch", size=10, color=INK, bold=True))

    # Дві гілки від MMU: NX = 0 (Дозвіл) та NX = 1 (Збій)
    # Гілка 1: NX = 0 (Успішне виконання)
    frags.append(arrow(600, 220, 680, 195, color=FIELD, sw=1.8))
    frags.append(text(640, 195, "NX = 0", size=11, color=FIELD, bold=True))

    b_ok, _, _ = textbox(790, 195, "L1i Cache & Decoder\nІнструкція декодується\nта виконується ядром", size=11, bold=True, fill="#eafaf1", stroke=FIELD)
    frags.append(b_ok)

    # Гілка 2: NX = 1 (Апаратне блокування)
    frags.append(arrow(600, 260, 680, 290, color=POS, sw=1.8))
    frags.append(text(640, 295, "NX = 1", size=11, color=POS, bold=True))

    b_trap, _, _ = textbox(790, 295, "Page Fault (#PF, Вектор 14)\nКод помилки: I/D = 1\nЯдро надсилає SIGSEGV", size=11, bold=True, fill="#fdecea", stroke=POS)
    frags.append(b_trap)

    # Підсумковий блок
    frags.append(textbox(460, 430, "Апаратний захист: Спроба вибірки інструкції (Instruction Fetch) зі сторінки з бітом NX = 1\nперехоплюється транслятором MMU ще до потрапляння в чергу декодера інструкцій.\nПроцес негайно аварійно завершується через сигнал SIGSEGV (SEGV_ACCERR).", size=11, fill="#fff8f8", stroke=POS)[0])

    render(os.path.join(IMG_DIR, "nx-bit-pte-architecture.svg"), w, h, *frags)


def fig_w_xor_x_transitions():
    """Ілюстрація принципу W^X: безпечні та заборонені стани віртуальних сторінок."""
    w, h = 900, 480
    frags = []

    # Заголовок
    frags.append(textbox(450, 25, "Принцип W^X (Write XOR Execute): Розподіл прав та переходи станів", size=14, bold=True, fill="#f4f6f8", stroke=LINE)[0])

    # Три легітимні безпечні стани
    # 1. Стан коду (RX)
    b_rx, _, _ = textbox(170, 130, "Сегмент коду (.text)\nПрава: PROT_READ | PROT_EXEC\nТільки читання та виконання", size=11, bold=True, fill="#eafaf1", stroke=FIELD)
    frags.append(b_rx)

    # 2. Стан даних (RW)
    b_rw, _, _ = textbox(450, 130, "Сегмент даних (Stack / Heap)\nПрава: PROT_READ | PROT_WRITE\nЧитання та запис (без виконання)", size=11, bold=True, fill="#eaf2f8", stroke=NEG)
    frags.append(b_rw)

    # 3. Стан констант (RO)
    b_ro, _, _ = textbox(730, 130, "Константи (.rodata)\nПрава: PROT_READ\nТільки читання", size=11, bold=True, fill="#f4f6f8", stroke=LINE)
    frags.append(b_ro)

    # Заборонений небезпечний стан (RWX)
    b_rwx, _, _ = textbox(450, 280, "ЗАБОРОНЕНИЙ СТАН: RWX\nПрава: PROT_READ | PROT_WRITE | PROT_EXEC\nОдночасна модифікація та виконання пам'яті", size=12, bold=True, fill="#fdecea", stroke=POS, sw=2.0)
    frags.append(b_rwx)

    # Переходи станів
    # Легітимний перехід JIT: RW -> mprotect() -> RX
    frags.append(arrow(320, 120, 280, 120, color=FIELD, sw=1.8))
    frags.append(text(350, 95, "mprotect(RX)", size=10, bold=True, color=FIELD))

    # Легітимне очищення/запис: RX -> mprotect() -> RW
    frags.append(arrow(280, 145, 320, 145, color=NEG, sw=1.8))
    frags.append(text(350, 165, "mprotect(RW)", size=10, bold=True, color=NEG))

    # Стрілки заборони до RWX
    frags.append(line(450, 185, 450, 235, color=POS, sw=2.0, dash="4,4"))
    frags.append(text(495, 210, "✗ ЗАБОРОНЕНО", size=11, bold=True, color=POS, anchor="start"))

    # Підсумковий блок інваріанта
    frags.append(textbox(450, 400, "Фундаментальний інваріант безпеки пам'яті:\nЖодна сторінка віртуальної пам'яті не повинна одночасно мати права на запис (W) і виконання (X).\nW ⊕ X = 1  (або  ¬(W ∧ X))\nЯкщо сторінка змінюється — вона не виконується; якщо виконується — вона захищена від змін.", size=11, fill="#f0fdf4", stroke=FIELD)[0])

    render(os.path.join(IMG_DIR, "w-xor-x-principle-and-transitions.svg"), w, h, *frags)


def fig_jit_dual_mapping():
    """Ілюстрація безпечної архітектури Dual Mapping для JIT-компіляторів."""
    w, h = 920, 500
    frags = []

    # Заголовок
    frags.append(textbox(460, 25, "Архітектура подвійного відображення (Dual Mapping) для JIT-компіляторів", size=14, bold=True, fill="#f4f6f8", stroke=LINE)[0])

    # Ліва частина: Віртуальний адресний простір
    frags.append(rect(40, 60, 400, 310, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(240, 85, "Віртуальний адресний простір процесу", size=12, bold=True, color=INK))

    # Віртуальна сторінка 1: RW (Тільки для компілятора)
    b_v_rw, _, _ = textbox(240, 145, "Віртуальна адреса V_write\nПрава: PROT_READ | PROT_WRITE\nВикористовується потоком генерації JIT", size=11, bold=True, fill="#eaf2f8", stroke=NEG)
    frags.append(b_v_rw)

    # Віртуальна сторінка 2: RX (Тільки для виконання)
    b_v_rx, _, _ = textbox(240, 275, "Віртуальна адреса V_exec\nПрава: PROT_READ | PROT_EXEC\nВикористовується потоком виконання коду", size=11, bold=True, fill="#eafaf1", stroke=FIELD)
    frags.append(b_v_rx)

    # Права частина: Фізична пам'ять (DRAM)
    frags.append(rect(580, 60, 300, 310, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(730, 85, "Фізична оперативна пам'ять (DRAM)", size=12, bold=True, color=INK))

    # Фізичний кадр (Page Frame)
    b_phys, _, _ = textbox(730, 210, "Спільний фізичний кадр\n(Physical Frame #4128)\nМістить скомпільований машинний код", size=11, bold=True, fill="#fef9e7", stroke="#d4ac0d")
    frags.append(b_phys)

    # Мапінг стрілками від віртуальних адрес до одного фізичного кадру
    # Стрілка від V_write до фізичного кадру
    frags.append(arrow(375, 145, 605, 195, color=NEG, sw=1.8))
    frags.append(text(490, 155, "mmap(fd, PROT_RW)", size=10, bold=True, color=NEG))

    # Стрілка від V_exec до фізичного кадру
    frags.append(arrow(375, 275, 605, 225, color=FIELD, sw=1.8))
    frags.append(text(490, 265, "mmap(fd, PROT_RX)", size=10, bold=True, color=FIELD))

    # Пояснювальний блок внизу
    frags.append(textbox(460, 425, "Переваги Dual Mapping:\n1. Нульові накладні витрати на mprotect() та скидання TLB під час генерації нових функцій.\n2. Відсутність вікна гонитви (Race Condition): сторінка виконання V_exec завжди залишається тільки для читання (RX).\n3. Повне дотримання правила W^X в кожен момент часу без модифікації прав під час роботи потоків.", size=11, fill="#f0fdf4", stroke=FIELD)[0])

    render(os.path.join(IMG_DIR, "jit-dual-mapping-architecture.svg"), w, h, *frags)


def fig_nx_bypass_rop():
    """Ілюстрація еволюції експлуатації: від ін'єкції шелкоду до Return-to-libc та ROP."""
    w, h = 920, 520
    frags = []

    # Заголовок
    frags.append(textbox(460, 25, "Еволюція атак на пам'ять: як біт NX змусив перейти від Shellcode до ROP", size=14, bold=True, fill="#f4f6f8", stroke=LINE)[0])

    # Ліва панель: Класична ін'єкція шелкоду (до NX)
    frags.append(rect(40, 55, 400, 350, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    frags.append(text(240, 80, "До появи NX: Пряма ін'єкція Shellcode", size=12, bold=True, color=POS))

    # Стек з шелкодом
    b_stk1, _, _ = textbox(240, 140, "Стек процесу (Права: RWX)\n[ Буфер: байти шелкоду execve() ]\n[ Збережений RBP ]\n[ Адреса повернення -> вказівник на стек ]", size=10, bold=True, fill="#fdecea", stroke=POS)
    frags.append(b_stk1)

    # Стрибок на стек
    frags.append(arrow(240, 205, 240, 240, color=POS, sw=1.8))
    frags.append(text(240, 225, "ret -> стрибок на стек", size=10, bold=True, color=POS))

    # Виконання коду на стеку
    b_sh1, _, _ = textbox(240, 275, "Виконання коду зі стека\nПроцесор виконує ін'єктований код\nВідкривається командна оболонка", size=10, fill="#fdecea", stroke=POS)
    frags.append(b_sh1)

    # Блокування NX
    b_block, _, _ = textbox(240, 355, "З появою NX (Non-Executable Stack):\nСпроба виконання стека викликає #PF -> SIGSEGV.\nПряма ін'єкція шелкоду заблокована назавжди.", size=10, bold=True, fill="#fff5f5", stroke=POS)
    frags.append(b_block)

    # Права панель: Повторне використання коду (Return-to-libc та ROP)
    frags.append(rect(480, 55, 400, 350, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(680, 80, "Після NX: Повторне використання коду (ROP)", size=12, bold=True, color=NEG))

    # Стек з адресами ґаджетів
    b_stk2, _, _ = textbox(680, 140, "Стек процесу (Права: RW, тільки дані)\n[ Адреса ґаджета 1: pop rdi; ret ]\n[ Аргумент: адреса рядка '/bin/sh' ]\n[ Адреса ґаджета 2: адреса system() ]", size=10, bold=True, fill="#eaf2f8", stroke=NEG)
    frags.append(b_stk2)

    # Стрибок на наявний код
    frags.append(arrow(680, 205, 680, 240, color=NEG, sw=1.8))
    frags.append(text(680, 225, "ret -> ланцюжок ґаджетів", size=10, bold=True, color=NEG))

    # Виконання в RX сегменті libc
    b_sh2, _, _ = textbox(680, 275, "Виконання в наявному .text / libc (RX)\nПроцесор виконує легітимні інструкції бібліотеки.\nБіт NX не спрацьовує, бо сторінки коду мають RX.", size=10, fill="#eafaf1", stroke=FIELD)
    frags.append(b_sh2)

    # Висновок щодо захисту
    b_mitig, _, _ = textbox(680, 355, "Протидія атакам типу ROP:\nПотрібні комплексні бар'єри: ASLR, Shadow Stack,\nканарейки стека та Control-Flow Integrity (CFI).", size=10, bold=True, fill="#f0fdf4", stroke=FIELD)
    frags.append(b_mitig)

    # Загальний підсумок
    frags.append(textbox(460, 460, "Висновок: Біт NX унеможливив виконання чужих ін'єктованих байтів у пам'яті даних,\nперевівши вектор атак від виконання шелкоду до маніпуляції ланцюжками наявного коду (ROP).", size=11, fill="#f4f6f8", stroke=LINE)[0])

    render(os.path.join(IMG_DIR, "nx-bypass-evolution-rop.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_nx_pte_architecture()
    fig_w_xor_x_transitions()
    fig_jit_dual_mapping()
    fig_nx_bypass_rop()
    print("Всі SVG-фігури для no-execute-memory успішно згенеровано.")
