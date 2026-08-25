# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми capability-based-security.
Всі фігури відповідають канону: білий фон, контрастні кольори, відсутність накладань.
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_confused_deputy():
    """Ілюстрація проблеми Confused Deputy (ACL vs Capability)."""
    w, h = 900, 500
    frags = []

    # Заголовки двох панелей
    frags.append(textbox(220, 30, "Класична модель ACL (Ambient Authority)", size=14, bold=True, fill="#fdecea", stroke=POS)[0])
    frags.append(textbox(670, 30, "Модель повноважень (Capability-Based)", size=14, bold=True, fill="#eafaf1", stroke=FIELD)[0])

    # Розділювач панелей
    frags.append(line(450, 20, 450, 480, color="#d1d5db", sw=1.5, dash="4,4"))

    # === Ліва панель: ACL / Confused Deputy ===
    # Клієнт (Атакувальник / Непривілейований)
    b_c1, _, _ = textbox(110, 110, "Зловмисник\n(UID 1000)\nНемає доступу до /etc", size=12, bold=True, fill="#ffffff", stroke=LINE)
    frags.append(b_c1)

    # Deputy (Компілятор / Сервіс друку)
    b_dep1, _, _ = textbox(340, 110, "Deputy (Сервіс)\n(UID 0 / root)\nМає повний доступ", size=12, bold=True, fill="#ffffff", stroke=POS)
    frags.append(b_dep1)

    # Цільовий ресурс
    b_file1, _, _ = textbox(340, 300, "Файл: /etc/passwd\n(Власник: root)", size=12, bold=True, fill="#fdecea", stroke=POS)
    frags.append(b_file1)

    # Стрілка 1: Запит на запис з іменем шляху
    frags.append(arrow(185, 110, 260, 110, color=POS, sw=1.8))
    frags.append(text(222, 90, "1. Шлях '/etc/passwd'", size=11, color=POS, bold=True))

    # Стрілка 2: Сервіс звертається до ядра від свого імені
    frags.append(arrow(340, 160, 340, 260, color=POS, sw=1.8))
    # Текст збоку від стрілки, не перетинаючи її
    frags.append(text(355, 200, "2. open('/etc/passwd')", size=11, color=POS, bold=True, anchor="start"))
    frags.append(text(355, 218, "з правами UID 0", size=11, color=POS, bold=True, anchor="start"))

    # Висновок лівої панелі
    frags.append(textbox(220, 420, "Провал безпеки:\nСервіс використовує власні фонові права (ambient authority)\nдля доступу до файлу, який клієнт не мав права змінювати.", size=11, fill="#fff5f5", stroke=POS)[0])

    # === Права панель: Capability ===
    # Клієнт
    b_c2, _, _ = textbox(550, 110, "Клієнт\nВолодіє CPtr 3\n(лише /tmp/out.log)", size=12, bold=True, fill="#ffffff", stroke=LINE)
    frags.append(b_c2)

    # Deputy
    b_dep2, _, _ = textbox(780, 110, "Сервіс (Deputy)\nПрацює в пісочниці\nБез неявних прав", size=12, bold=True, fill="#ffffff", stroke=FIELD)
    frags.append(b_dep2)

    # Цільові ресурси
    b_tmp, _, _ = textbox(660, 300, "Файл: /tmp/out.log\n(Доступ дозволено)", size=12, bold=True, fill="#eafaf1", stroke=FIELD)
    frags.append(b_tmp)
    b_pass2, _, _ = textbox(815, 300, "Файл: /etc/passwd\n(Немає capability)", size=12, bold=True, fill="#f4f6f8", stroke="#9ca3af")
    frags.append(b_pass2)

    # Стрілка 1: Передача capability разом із запитом
    frags.append(arrow(620, 110, 700, 110, color=FIELD, sw=1.8))
    frags.append(text(660, 90, "1. Передача CPtr 3 (Cap)", size=11, color=FIELD, bold=True))

    # Стрілка 2: Запис через надане повноваження
    frags.append(arrow(750, 160, 680, 260, color=FIELD, sw=1.8))
    frags.append(text(670, 205, "2. Запис через Cap", size=11, color=FIELD, bold=True, anchor="end"))

    # Заборонений шлях до /etc/passwd
    frags.append(line(795, 160, 815, 260, color=POS, sw=1.5, dash="3,3"))
    frags.append(text(830, 205, "✗ Неможливо\nадресувати", size=11, color=POS, bold=True, anchor="start"))

    # Висновок правої панелі
    frags.append(textbox(670, 420, "Захист за побудовою:\nСервіс може записати лише в той об'єкт, на який клієнт\nявно передав невдаване повноваження (explicit delegation).", size=11, fill="#f0fdf4", stroke=FIELD)[0])

    render(os.path.join(IMG_DIR, "confused-deputy-problem.svg"), w, h, *frags)


def fig_cheri_capability():
    """Анатомія апаратного повноваження CHERI (Fat Pointer з теговим бітом)."""
    w, h = 880, 440
    frags = []

    # Заголовок
    frags.append(textbox(440, 25, "Апаратна структура повноваження CHERI (128-біт + 1-біт Tag)", size=14, bold=True, fill="#f4f6f8", stroke=LINE)[0])

    # Теговий біт (поза пам'яттю)
    b_tag, _, _ = textbox(105, 100, "Теговий біт (Tag)\n1 біт (поза DRAM)\n1 = чинне, 0 = недійсне", size=11, bold=True, fill="#fdecea", stroke=POS)
    frags.append(b_tag)

    # 128-бітне тіло capability
    # Секція метаданих (64 біти)
    frags.append(fitbox(210, 75, 310, 50, "Метадані (64 біти)\n[ Права (Perms) | Межі (Bounds: Base/Top) | Тип (Type) ]", size=11, bold=True, fill="#eaf0fd", stroke=NEG))

    # Секція віртуальної адреси / курсора (64 біти)
    frags.append(fitbox(530, 75, 320, 50, "Курсор / Адреса (64 біти)\nПоточна віртуальна адреса (Address / Offset)", size=11, bold=True, fill="#eafaf1", stroke=FIELD))

    # Зв'язок тегу з тілом
    frags.append(arrow(180, 100, 205, 100, color=POS, sw=1.8))

    # Розшифровка полів метаданих
    frags.append(fitbox(40, 175, 245, 110, "Права доступу (Permissions):\n• Read / Write / Execute\n• Load / Store Capability\n• User / System perms", size=10, fill="#ffffff", stroke=LINE))

    frags.append(fitbox(315, 175, 250, 110, "Просторові межі (Bounds):\n• Base: нижня межа пам'яті\n• Top: верхня межа (Base+Length)\n(стиснення CHERI Concentrate)", size=10, fill="#ffffff", stroke=LINE))

    frags.append(fitbox(595, 175, 250, 110, "Стан запечатування (Sealing):\n• OType: тип об'єкта\n• Sealed: запечатано (незмінне)\n• Unsealed: доступне до розіменування", size=10, fill="#ffffff", stroke=LINE))

    # Нижній блок: апаратні інваріанти
    b_inv, _, _ = textbox(440, 360, "Ключові апаратні гарантії CHERI:\n1. Невдаваність: зміна хоча б 1 біта інструкціями цілочисельної арифметики автоматично скидає Tag у 0.\n2. Монотонність: права та межі можна лише звужувати (attenuation), розширення блокується апаратно.\n3. Розіменування вказівника з Tag=0 генерує апаратний виняток (Hardware Capability Trap).", size=11, fill="#fdfbf7", stroke="#d97706")
    frags.append(b_inv)

    render(os.path.join(IMG_DIR, "capability-anatomy-cheri.svg"), w, h, *frags)


def fig_sel4_cspace():
    """Організація простору повноважень (CSpace, CNode) та дерева похідних (CDT) у seL4."""
    w, h = 900, 460
    frags = []

    # Заголовок
    frags.append(textbox(450, 25, "Простір повноважень (CSpace) і дерево похідних (CDT) у seL4", size=14, bold=True, fill="#f4f6f8", stroke=LINE)[0])

    # Процес / TCB
    b_tcb, _, _ = textbox(110, 120, "Потік (TCB)\nМає регістр CSpace Root", size=12, bold=True, fill="#ffffff", stroke=LINE)
    frags.append(b_tcb)

    # Кореневий CNode
    b_cnode, _, _ = textbox(330, 120, "Кореневий CNode\nСлот 0: Endpoint Cap (RW)\nСлот 1: Untyped Memory\nСлот 2: Child CNode Cap", size=11, bold=True, fill="#eaf0fd", stroke=NEG)
    frags.append(b_cnode)

    frags.append(arrow(180, 120, 240, 120, color=NEG, sw=1.8))
    frags.append(text(210, 105, "CPtr", size=11, color=NEG, bold=True))

    # Дочірній CNode
    b_child_cnode, _, _ = textbox(630, 120, "Дочірній CNode\nСлот 0: Endpoint Cap (Read-Only)\n(створено через seL4_CNode_Mint)", size=11, bold=True, fill="#eafaf1", stroke=FIELD)
    frags.append(b_child_cnode)

    frags.append(arrow(425, 120, 495, 120, color=FIELD, sw=1.8))
    frags.append(text(460, 105, "Слот 2", size=11, color=FIELD, bold=True))

    # Фізичний об'єкт ядра
    b_obj, _, _ = textbox(480, 270, "Об'єкт ядра (Kernel Object)\nСинхронний Endpoint для IPC", size=12, bold=True, fill="#fdecea", stroke=POS)
    frags.append(b_obj)

    # Стрілки посилань на об'єкт
    frags.append(arrow(340, 175, 430, 235, color=NEG, sw=1.5))
    frags.append(text(345, 220, "Cap (RW)", size=10, color=NEG, bold=True, anchor="end"))

    frags.append(arrow(600, 175, 525, 235, color=FIELD, sw=1.5))
    frags.append(text(595, 220, "Cap (R-only)", size=10, color=FIELD, bold=True, anchor="start"))

    # Дерево похідних прав (CDT)
    b_cdt, _, _ = textbox(450, 380, "Дерево похідних прав (Capability Derivation Tree):\n• Батьківське повноваження: CNode[0] (Endpoint RW)\n• Дочірнє повноваження: Child_CNode[0] (Endpoint Read-Only)\n• Каскадне відкликання: виклик seL4_CNode_Revoke(CNode, 0) рекурсивно знищує всі дочірні копії у системі.", size=11, fill="#f9fafb", stroke=LINE)
    frags.append(b_cdt)

    render(os.path.join(IMG_DIR, "sel4-cspace-cnode-tree.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_confused_deputy()
    fig_cheri_capability()
    fig_sel4_cspace()
    print("Всі фігури згенеровано успішно.")
