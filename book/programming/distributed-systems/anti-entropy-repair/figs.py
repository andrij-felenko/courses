# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Анти-ентропія та відновлення узгодженості'."""

import sys
import os

# scripts/ знаходиться на 4 рівні вище
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_entropy_drift():
    """Фігура 1: Джерела ентропії реплік — мережевий збій, вичерпання натяків та сліпа зона холодних ключів."""
    w, h = 820, 380
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Джерела накопичення ентропії у безлідерному кластері", size=16, bold=True))

    # Секція 1: Запис із кворумом W=2 при відмові вузла
    frags.append(rect(20, 50, 245, 305, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(142, 75, "1. Запис при W=2 (N=3)", size=14, bold=True, color=INK))

    frags.append(rect(35, 95, 215, 45, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=5))
    frags.append(text(142, 115, "Клієнт: Set(k, v2)", size=12, bold=True, color=NEG))
    frags.append(text(142, 130, "Координатор надсилає 3 запити", size=10, color=MUTED))

    # Репліки 1, 2 (ОК) і 3 (збій)
    frags.append(rect(35, 155, 215, 36, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(142, 177, "Репліка 1: ОК (v2 записано)", size=11, bold=True, color=FIELD))

    frags.append(rect(35, 198, 215, 36, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(142, 220, "Репліка 2: ОК (v2 записано)", size=11, bold=True, color=FIELD))

    frags.append(rect(35, 241, 215, 42, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(142, 260, "Репліка 3: ЗБІЙ МЕРЕЖІ", size=11, bold=True, color=POS))
    frags.append(text(142, 275, "Оновлення v2 пропущено", size=10, color=POS))

    frags.append(rect(35, 295, 215, 48, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(142, 314, "Кворум W=2 досягнуто:", size=11, bold=True, color=INK))
    frags.append(text(142, 331, "Клієнт отримав успіх 200 OK", size=11, color=FIELD))

    # Стрілка між секцією 1 та 2
    frags.append(arrow(268, 202, 295, 202, color=LINE, sw=2))

    # Секція 2: Обмеження відкладеної передачі (Hinted Handoff)
    frags.append(rect(298, 50, 245, 305, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(420, 75, "2. Відкладена передача", size=14, bold=True, color=INK))

    frags.append(rect(313, 95, 215, 60, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=5))
    frags.append(text(420, 118, "Буфер натяків (Hints)", size=12, bold=True, color=INK))
    frags.append(text(420, 134, "Зберігає пропущені мутації", size=10, color=MUTED))
    frags.append(text(420, 147, "для Репліки 3 локально", size=10, color=MUTED))

    frags.append(arrow(420, 160, 420, 185, color=LINE, sw=1.5))

    frags.append(rect(313, 190, 215, 65, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(420, 212, "Ліміт часу / пам'яті:", size=11, bold=True, color=POS))
    frags.append(text(420, 229, "max_hint_window (3 год)", size=11, color=INK))
    frags.append(text(420, 245, "Натяки скинуто на диск/стерто", size=10, color=POS))

    frags.append(rect(313, 270, 215, 73, fill="#fff7ed", stroke="#f97316", sw=1.5, rx=5))
    frags.append(text(420, 292, "Наслідок вичерпання:", size=11, bold=True, color="#c2410c"))
    frags.append(text(420, 310, "Репліка 3 оживає, але", size=10, color=INK))
    frags.append(text(420, 326, "не отримує пропущених оновлень", size=10, color=INK))

    # Стрілка між секцією 2 та 3
    frags.append(arrow(546, 202, 573, 202, color=LINE, sw=2))

    # Секція 3: Сліпа зона відновлення при читанні (Read Repair)
    frags.append(rect(576, 50, 224, 305, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(688, 75, "3. Сліпа зона читання", size=14, bold=True, color=INK))

    frags.append(rect(588, 95, 200, 75, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(688, 118, "Гарячі дані (~5%)", size=12, bold=True, color=FIELD))
    frags.append(text(688, 136, "Часто читаються клієнтами", size=10, color=INK))
    frags.append(text(688, 153, "Лагодяться через Read Repair", size=10, color=FIELD))

    frags.append(rect(588, 185, 200, 158, fill="#fdecea", stroke=POS, sw=2, rx=5))
    frags.append(text(688, 208, "Холодні дані (~95%)", size=12, bold=True, color=POS))
    frags.append(text(688, 228, "Рідко або ніколи не читаються", size=10, color=INK))
    frags.append(text(688, 248, "Ентропія лишається!", size=11, bold=True, color=POS))
    frags.append(text(688, 270, "При падінні Репліки 1 чи 2", size=10, color=INK))
    frags.append(text(688, 288, "кворум R=2 прочитає стару v1", size=10, bold=True, color=POS))
    frags.append(text(688, 308, "із Репліки 3 (мовчазний збій)", size=10, color=POS))

    return render(os.path.join(OUT, "entropy-drift-sources.svg"), w, h, *frags)


def fig_merkle_sync():
    """Фігура 2: Звіряння реплік через дерева Меркла — пропуск однакових гілок і передача лише дельти."""
    w, h = 820, 420
    frags = []

    frags.append(text(w / 2, 26, "Анти-ентропійне звіряння за деревами Меркла між двома репліками", size=16, bold=True))

    # Контейнер для Репліки A (зліва)
    frags.append(rect(20, 45, 370, 315, fill="#fafbfc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(205, 68, "Репліка A (Діапазон токенів [0, 2⁶⁴))", size=13, bold=True, color=NEG))

    # Дерево Меркла A
    # Корінь A
    frags.append(rect(140, 85, 130, 34, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(205, 106, "Корінь: 0x9F4A", size=12, bold=True, color=POS))

    # Рівень 1 A
    frags.append(line(175, 119, 105, 150, color=LINE, sw=1.5))
    frags.append(line(235, 119, 305, 150, color=LINE, sw=1.5))

    frags.append(rect(45, 150, 120, 34, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(105, 171, "Гілка L: 0x3C11", size=11, bold=True, color=FIELD))

    frags.append(rect(245, 150, 120, 34, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(305, 171, "Гілка R: 0x88F0", size=11, bold=True, color=POS))

    # Рівень 2 (Листя) A
    frags.append(line(85, 184, 60, 215, color=LINE, sw=1.2))
    frags.append(line(125, 184, 150, 215, color=LINE, sw=1.2))
    frags.append(line(285, 184, 260, 215, color=LINE, sw=1.2))
    frags.append(line(325, 184, 350, 215, color=LINE, sw=1.2))

    frags.append(rect(28, 215, 65, 30, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(60, 234, "0x1A", size=10, color=FIELD))

    frags.append(rect(118, 215, 65, 30, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(150, 234, "0x5E", size=10, color=FIELD))

    frags.append(rect(228, 215, 65, 30, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(260, 234, "0x7B", size=10, color=FIELD))

    frags.append(rect(318, 215, 65, 30, fill="#fdecea", stroke=POS, sw=2, rx=4))
    frags.append(text(350, 234, "0x99", size=10, bold=True, color=POS))

    # Діапазони листя A
    frags.append(text(60, 262, "Діапазон 1", size=9, color=MUTED))
    frags.append(text(150, 262, "Діапазон 2", size=9, color=MUTED))
    frags.append(text(260, 262, "Діапазон 3", size=9, color=MUTED))
    frags.append(text(350, 262, "Діапазон 4", size=9, bold=True, color=POS))

    frags.append(rect(30, 280, 350, 68, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=5))
    frags.append(text(205, 300, "Вміст Діапазону 4 на Репліці A:", size=11, bold=True, color=INK))
    frags.append(text(205, 318, "Ключ K41 = 'data_v2' (ts: 1700000500)", size=10, color=FIELD))
    frags.append(text(205, 334, "Ключ K42 = 'data_v1' (ts: 1700000100)", size=10, color=INK))

    # Контейнер для Репліки B (справа)
    frags.append(rect(430, 45, 370, 315, fill="#fafbfc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(615, 68, "Репліка B (Діапазон токенів [0, 2⁶⁴))", size=13, bold=True, color=NEG))

    # Дерево Меркла B
    # Корінь B
    frags.append(rect(550, 85, 130, 34, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(615, 106, "Корінь: 0xE41B", size=12, bold=True, color=POS))

    # Рівень 1 B
    frags.append(line(585, 119, 515, 150, color=LINE, sw=1.5))
    frags.append(line(645, 119, 715, 150, color=LINE, sw=1.5))

    frags.append(rect(455, 150, 120, 34, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(515, 171, "Гілка L: 0x3C11", size=11, bold=True, color=FIELD))

    frags.append(rect(655, 150, 120, 34, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(715, 171, "Гілка R: 0x12A4", size=11, bold=True, color=POS))

    # Рівень 2 (Листя) B
    frags.append(line(495, 184, 470, 215, color=LINE, sw=1.2))
    frags.append(line(535, 184, 560, 215, color=LINE, sw=1.2))
    frags.append(line(695, 184, 670, 215, color=LINE, sw=1.2))
    frags.append(line(735, 184, 760, 215, color=LINE, sw=1.2))

    frags.append(rect(438, 215, 65, 30, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(470, 234, "0x1A", size=10, color=FIELD))

    frags.append(rect(528, 215, 65, 30, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(560, 234, "0x5E", size=10, color=FIELD))

    frags.append(rect(638, 215, 65, 30, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(670, 234, "0x7B", size=10, color=FIELD))

    frags.append(rect(728, 215, 65, 30, fill="#fdecea", stroke=POS, sw=2, rx=4))
    frags.append(text(760, 234, "0x2C", size=10, bold=True, color=POS))

    # Діапазони листя B
    frags.append(text(470, 262, "Діапазон 1", size=9, color=MUTED))
    frags.append(text(560, 262, "Діапазон 2", size=9, color=MUTED))
    frags.append(text(670, 262, "Діапазон 3", size=9, color=MUTED))
    frags.append(text(760, 262, "Діапазон 4", size=9, bold=True, color=POS))

    frags.append(rect(440, 280, 350, 68, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=5))
    frags.append(text(615, 300, "Вміст Діапазону 4 на Репліці B:", size=11, bold=True, color=INK))
    frags.append(text(615, 318, "Ключ K41 = 'data_v1' (ts: 1700000050)", size=10, color=POS))
    frags.append(text(615, 334, "Ключ K42 = 'data_v1' (ts: 1700000100)", size=10, color=INK))

    # Порівняння між деревами
    # Порівняння коренів (≠)
    frags.append(line(275, 102, 545, 102, color=POS, sw=1.5, dash="4,3"))
    frags.append(rect(385, 90, 50, 24, fill="#fdecea", stroke=POS, sw=1, rx=3))
    frags.append(text(410, 106, "≠ спуск", size=10, bold=True, color=POS))

    # Порівняння лівих гілок (=)
    frags.append(line(170, 167, 450, 167, color=FIELD, sw=1.5, dash="4,3"))
    frags.append(rect(385, 155, 50, 24, fill="#f0fdf4", stroke=FIELD, sw=1, rx=3))
    frags.append(text(410, 171, "= пропуск", size=9, bold=True, color=FIELD))

    # Нижня панель підсумку синхронізації
    frags.append(rect(20, 368, 780, 42, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(410, 386, "Результат: 75% даних пропущено без пересилки (0 байтів). Локалізовано Діапазон 4.", size=11, bold=True, color=NEG))
    frags.append(text(410, 401, "Потокова передача: Репліка A передає лише ключ K41 (v2) -> Репліка B оновлює свій стан.", size=10, color=INK))

    return render(os.path.join(OUT, "merkle-tree-sync.svg"), w, h, *frags)


def fig_tombstone_gc():
    """Фігура 3: Небезпека зомбі-даних та захисний часовий бар'єр gc_grace_seconds."""
    w, h = 820, 390
    frags = []

    frags.append(text(w / 2, 26, "Механіка виникнення зомбі-записів та бар'єр gc_grace_seconds", size=16, bold=True))

    # Верхній сценарій: Катастрофа без анти-ентропії (Resurrection)
    frags.append(rect(20, 45, 780, 150, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(180, 68, "Сценарій А: Ремонт запізнився (> gc_grace_seconds) — ЗОМБІ-ДАНІ", size=12, bold=True, color=POS))

    # Таймлайн А
    frags.append(line(50, 130, 750, 130, color=LINE, sw=2))
    frags.append(arrow(750, 130, 770, 130, color=LINE, sw=2))

    # Точки часу А
    # День 0: Видалення
    frags.append(circle(90, 130, 6, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(90, 95, "День 0", size=11, bold=True, color=INK))
    frags.append(text(90, 110, "DELETE k1", size=10, bold=True, color=POS))
    frags.append(text(90, 150, "Вузол 1,2: Tombstone", size=9, color=INK))
    frags.append(text(90, 163, "Вузол 3: ВІДКЛЮЧЕНО", size=9, color=POS))

    # День 10: Ліміт gc_grace
    frags.append(circle(320, 130, 6, fill="#f97316", stroke=LINE, sw=1.5))
    frags.append(text(320, 95, "День 10: gc_grace", size=11, bold=True, color="#c2410c"))
    frags.append(text(320, 110, "Compaction", size=10, color=INK))
    frags.append(text(320, 150, "Вузол 1, 2 стерли", size=9, color=INK))
    frags.append(text(320, 163, "Tombstone назавжди!", size=9, bold=True, color=POS))

    # День 14: Вузол 3 вмикається і воскрешає дані
    frags.append(circle(580, 130, 6, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(580, 95, "День 14", size=11, bold=True, color=POS))
    frags.append(text(580, 110, "Вузол 3 оживає", size=10, color=INK))
    frags.append(text(580, 150, "Містить старе k1 (v1)", size=9, color=INK))
    frags.append(text(580, 163, "без надгробка!", size=9, color=POS))

    frags.append(rect(660, 95, 125, 75, fill="#ffffff", stroke=POS, sw=1.5, rx=5))
    frags.append(text(722, 115, "КАТАСТРОФА:", size=10, bold=True, color=POS))
    frags.append(text(722, 130, "Вузол 3 розсилає", size=9, color=INK))
    frags.append(text(722, 144, "k1 як 'новий' запис.", size=9, color=INK))
    frags.append(text(722, 158, "Видалене воскресло!", size=9, bold=True, color=POS))

    # Нижній сценарій: Коректний ремонт у межах gc_grace
    frags.append(rect(20, 205, 780, 170, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(200, 228, "Сценарій Б: Регулярний ремонт (< gc_grace_seconds) — БЕЗПЕЧНО", size=12, bold=True, color=FIELD))

    # Таймлайн Б
    frags.append(line(50, 290, 750, 290, color=LINE, sw=2))
    frags.append(arrow(750, 290, 770, 290, color=LINE, sw=2))

    # Точки часу Б
    # День 0: Видалення
    frags.append(circle(90, 290, 6, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(90, 255, "День 0", size=11, bold=True, color=INK))
    frags.append(text(90, 270, "DELETE k1", size=10, bold=True, color=POS))
    frags.append(text(90, 310, "Вузол 1,2: Tombstone", size=9, color=INK))
    frags.append(text(90, 323, "Вузол 3: ВІДКЛЮЧЕНО", size=9, color=POS))

    # День 5: Вузол 3 оживає і виконується Anti-Entropy Repair
    frags.append(circle(320, 290, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(320, 255, "День 5: Ремонт", size=11, bold=True, color=FIELD))
    frags.append(text(320, 270, "Anti-Entropy Repair", size=10, bold=True, color=NEG))
    frags.append(text(320, 310, "Вузол 1 передає", size=9, color=INK))
    frags.append(text(320, 323, "Tombstone на Вузол 3", size=9, bold=True, color=FIELD))

    # День 10: Безпечний Compaction на всіх вузлах
    frags.append(circle(580, 290, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(580, 255, "День 10: gc_grace", size=11, bold=True, color=FIELD))
    frags.append(text(580, 270, "Compaction", size=10, color=INK))
    frags.append(text(580, 310, "Усі 3 вузли мають надгробок;", size=9, color=INK))
    frags.append(text(580, 323, "k1 безпечно видалено назавжди.", size=9, color=FIELD))

    frags.append(rect(660, 260, 125, 75, fill="#ffffff", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(722, 280, "УСПІХ:", size=10, bold=True, color=FIELD))
    frags.append(text(722, 295, "Дані видалено", size=9, color=INK))
    frags.append(text(722, 309, "узгоджено на всіх", size=9, color=INK))
    frags.append(text(722, 323, "трьох репліках!", size=9, bold=True, color=FIELD))

    return render(os.path.join(OUT, "tombstone-gc-grace.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_entropy_drift()
    fig_merkle_sync()
    fig_tombstone_gc()
    print("Figures generated successfully.")
