# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми «Non-Maximum Suppression» (NMS)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig1_iou_box_suppression():
    """Геометрія перекриття IoU та принцип придушення надлишкових рамок."""
    w, h = 900, 450
    p = []

    # Фон лівої панелі (Обчислення метрики IoU)
    p.append(rect(20, 20, 415, 410, fill="none", stroke="#bdc3c7", sw=1.5, rx=6))
    p.append(text(227, 48, "Геометрична метрика IoU (Intersection over Union)", size=13, color="#1b4f72", bold=True, anchor="middle"))

    # Рамка A (Winner Box)
    ax, ay, aw, ah = 55, 80, 180, 140
    p.append(rect(ax, ay, aw, ah, fill="none", stroke="#27ae60", sw=2.5, rx=3))
    p.append(text(ax + 10, ay + 22, "Рамка A (Score = 0.92)", size=12, color="#1e8449", bold=True, anchor="start"))
    p.append(text(ax + 10, ay + 38, "Переможець (Keep)", size=11, color="#1e8449", anchor="start"))

    # Рамка B (Candidate Box)
    bx, by, bw, bh = 145, 140, 180, 140
    p.append(rect(bx, by, bw, bh, fill="none", stroke="#c0392b", sw=2, rx=3))
    p.append(text(bx + bw - 10, by + bh - 10, "Рамка B (Score = 0.78)", size=12, color="#922b21", bold=True, anchor="end"))

    # Перетин (Intersection)
    ix, iy = max(ax, bx), max(ay, by)
    iw, ih = min(ax + aw, bx + bw) - ix, min(ay + ah, by + bh) - iy
    p.append(rect(ix, iy, iw, ih, fill="#f9e79f", stroke="#d4ac0d", sw=2, rx=2))
    p.append(text(ix + iw / 2, iy + ih / 2 - 4, "Перетин", size=11, color="#7d6608", bold=True, anchor="middle"))
    p.append(text(ix + iw / 2, iy + ih / 2 + 10, "A ∩ B", size=11, color="#7d6608", bold=True, anchor="middle"))

    # Координатні мітки кутів перетину
    p.append(circle(ix, iy, 3.5, fill="#d4ac0d", stroke="#7d6608"))
    p.append(text(ix - 6, iy - 6, "(max x₁, max y₁)", size=10, color="#7d6608", anchor="end"))
    p.append(circle(ix + iw, iy + ih, 3.5, fill="#d4ac0d", stroke="#7d6608"))
    p.append(text(ix + iw + 6, iy + ih + 14, "(min x₂, min y₂)", size=10, color="#7d6608", anchor="start"))

    # Формульний блок внизу лівої панелі
    p.append(fitbox(35, 305, 385, 110,
                    "Формула розрахунку:\n"
                    "IoU(A, B) = Area(A ∩ B) / Area(A ∪ B)\n"
                    "Area(A ∪ B) = Area(A) + Area(B) − Area(A ∩ B)\n"
                    "IoU = 0.68  ≥  Порог T_nms (0.50)  →  ПРИДУШИТИ B",
                    size=12, pad=6, fill="#f8f9fa", stroke="#7f8c8d", color="#2c3e50", bold=False))

    # Фон правої панелі (Процес придушення на сцені детекції)
    p.append(rect(455, 20, 425, 410, fill="none", stroke="#bdc3c7", sw=1.5, rx=6))
    p.append(text(667, 48, "Придушення дублікатів на множині кандидатів", size=13, color="#512e5f", bold=True, anchor="middle"))

    # Сцена з об'єктом 1 (Людина ліворуч) та об'єктом 2 (Людина праворуч)
    # Об'єкт 1: три рамки-кандидати
    p.append(rect(475, 75, 150, 215, fill="none", stroke="#27ae60", sw=2.5, rx=3))
    p.append(text(485, 96, "Box 1: Score 0.94", size=11, color="#1e8449", bold=True, anchor="start"))
    p.append(text(485, 112, "Переможець M₁ [ЗБЕРЕЖЕНО]", size=10, color="#1e8449", bold=True, anchor="start"))

    p.append(rect(490, 88, 145, 208, fill="none", stroke="#c0392b", sw=1.8, rx=3))
    p.append(text(630, 142, "Box 2: 0.81 (IoU=0.74)", size=10, color="#c0392b", anchor="end"))
    p.append(text(630, 155, "Придушено Box 1", size=9, color="#c0392b", italic=True, anchor="end"))

    p.append(rect(465, 100, 155, 198, fill="none", stroke="#e67e22", sw=1.8, rx=3))
    p.append(text(470, 275, "Box 3: 0.65 (IoU=0.61)", size=10, color="#b9770e", anchor="start"))
    p.append(text(470, 288, "Придушено Box 1", size=9, color="#b9770e", italic=True, anchor="start"))

    # Об'єкт 2: окремий об'єкт поруч із невисоким перекриттям
    p.append(rect(675, 80, 145, 210, fill="none", stroke="#2980b9", sw=2.5, rx=3))
    p.append(text(685, 101, "Box 4: Score 0.89", size=11, color="#1b4f72", bold=True, anchor="start"))
    p.append(text(685, 116, "Переможець M₂ [ЗБЕРЕЖЕНО]", size=10, color="#1b4f72", bold=True, anchor="start"))

    p.append(rect(690, 95, 140, 200, fill="none", stroke="#8e44ad", sw=1.8, rx=3))
    p.append(text(825, 272, "Box 5: 0.72 (IoU=0.68)", size=10, color="#6c3483", anchor="end"))
    p.append(text(825, 285, "Придушено Box 4", size=9, color="#6c3483", italic=True, anchor="end"))

    # Пояснення просторового розділення між Object 1 та Object 2
    p.append(fitbox(470, 310, 395, 105,
                    "Просторове розділення об'єктів:\n"
                    "IoU(Box 1, Box 4) = 0.12  <  T_nms (0.50)\n"
                    "Обидва бокси зберігаються як незалежні фізичні цілі.\n"
                    "Результат NMS: 2 фінальні рамки замість 5 вхідних дублікатів.",
                    size=12, pad=6, fill="#f8f9fa", stroke="#2c3e50", color="#1c2833"))

    render(os.path.join(OUT, "iou-box-suppression.svg"), w, h, *p)


def fig2_greedy_nms_flowchart():
    """Алгоритмічна блок-схема жадібного алгоритму Non-Maximum Suppression."""
    w, h = 900, 480
    p = []

    # 1. Вхідний блок
    b1 = fitbox(25, 50, 200, 75,
                "Вхідні дані детектора:\n"
                "• N рамок B = {b₁, …, b_N}\n"
                "• Скори впевненості S\n"
                "• Пороги T_score, T_nms",
                size=12, pad=6, fill="#eaf2f8", stroke="#2980b9", color="#1b4f72")
    p.append(b1)

    # 2. Попередня фільтрація за скором
    b2 = fitbox(265, 50, 190, 75,
                "Фільтрація за скором:\n"
                "Видалити всі рамки b_i,\n"
                "де s_i < T_score\n"
                "(відсікання фонового шуму)",
                size=12, pad=6, fill="#fef9e7", stroke="#d4ac0d", color="#7d6608")
    p.append(b2)
    p.append(arrow(225, 87, 265, 87, color=LINE, sw=1.8))

    # 3. Сортування за спаданням
    b3 = fitbox(495, 50, 180, 75,
                "Сортування (Sorting):\n"
                "Впорядкувати рамки:\n"
                "s₁ ≥ s₂ ≥ … ≥ s_M\n"
                "Складність: O(M log M)",
                size=12, pad=6, fill="#f4ecf7", stroke="#8e44ad", color="#512e5f")
    p.append(b3)
    p.append(arrow(455, 87, 495, 87, color=LINE, sw=1.8))

    # 4. Ініціалізація вихідного списку
    b4 = fitbox(715, 50, 160, 75,
                "Ініціалізація:\n"
                "Фінальний список D = ∅\n"
                "Кандидати C = {b₁, …, b_M}",
                size=12, pad=6, fill="#e8f8f5", stroke="#16a085", color="#0e6251")
    p.append(b4)
    p.append(arrow(675, 87, 715, 87, color=LINE, sw=1.8))

    # Стрілка вниз до циклу
    p.append(arrow(795, 125, 795, 180, color=LINE, sw=1.8))

    # 5. Перевірка умови циклу
    b5 = fitbox(705, 180, 180, 65,
                "Умова циклу:\n"
                "Чи список C непорожній?",
                size=12, pad=6, fill="#fdf2e9", stroke="#d35400", color="#7e3200", bold=True)
    p.append(b5)

    # Гілка ТАК: вибір максимуму
    p.append(arrow(705, 212, 600, 212, color=FIELD, sw=1.8))
    p.append(text(650, 202, "ТАК", size=12, color=FIELD, bold=True))

    b6 = fitbox(380, 175, 220, 75,
                "Вибір максимуму:\n"
                "Витягнути перший елемент M\n"
                "Додати M до списку D\n"
                "C = C \\ {M}",
                size=12, pad=6, fill="#eafaf1", stroke="#27ae60", color="#145a32")
    p.append(b6)

    # 6. Порівняння IoU та придушення
    p.append(arrow(380, 212, 260, 212, color=LINE, sw=1.8))

    b7 = fitbox(25, 175, 235, 75,
                "Попарне порівняння IoU:\n"
                "Для кожної рамки b_j ∈ C:\n"
                "Обчислити iou = IoU(M, b_j)\n"
                "Якщо iou ≥ T_nms → видалити b_j",
                size=12, pad=6, fill="#fdecea", stroke="#c0392b", color="#78281f")
    p.append(b7)

    # Зворотна петля циклу
    p.append(line(142, 250, 142, 305, color=LINE, sw=1.5))
    p.append(line(142, 305, 795, 305, color=LINE, sw=1.5))
    p.append(arrow(795, 305, 795, 245, color=LINE, sw=1.8))
    p.append(text(468, 295, "Повернення на наступну ітерацію з оновленою множиною C", size=11, color=MUTED, italic=True))

    # Гілка НІ: вихід
    p.append(arrow(795, 245, 795, 360, color=POS, sw=1.8))
    p.append(text(810, 335, "НІ", size=12, color=POS, bold=True))

    # Фінальний блок
    b_out = fitbox(640, 360, 235, 80,
                   "Остаточний вихід:\n"
                   "Список чистих детекцій D\n"
                   "Рівно одна оптимальна рамка\n"
                   "на кожен фізичний об'єкт",
                   size=12, pad=6, fill="#ffffff", stroke="#2c3e50", color="#1c2833", bold=True)
    p.append(b_out)

    # Пояснювальний блок зліва внизу
    b_note = fitbox(25, 360, 580, 80,
                    "Часова складність та оптимізація:\n"
                    "• Найгірший випадок: O(N²) попарних перевірок IoU\n"
                    "• Реальний час після фільтрації за скором (M ≪ N): O(M log M + K·M)\n"
                    "• На вбудованих CPU сортування Top-K QuickSelect скорочує час у рази.",
                    size=12, pad=6, fill="#f4f6f7", stroke="#7f8c8d", color="#2c3e50")
    p.append(b_note)

    render(os.path.join(OUT, "iou-box-suppression.svg"), w, h, *p)


if __name__ == "__main__":
    fig1_iou_box_suppression()
    fig2_greedy_nms_flowchart()
    print("Фігури NMS згенеровано успішно.")
