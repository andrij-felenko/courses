# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Звірка стану (Reconciliation)'."""

import sys
import os

# scripts/ знаходиться на 4 рівні вище: book/programming/distributed-systems/reconciliation -> 4 рівні до кореня
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_edge_vs_level():
    """Фігура 1: Порівняння edge-triggered (імперативного) та level-triggered (декларативного) підходів."""
    w, h = 860, 420
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Імперативний (Edge-triggered) проти Декларативного (Level-triggered) підходу", size=16, bold=True))

    # Ліва колонка: Edge-triggered
    frags.append(rect(20, 50, 395, 350, fill="#fdfafb", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(217, 78, "Edge-triggered (Реакція на переходи / події)", size=13, bold=True, color=POS))

    # Кроки лівої колонки
    frags.append(rect(35, 98, 365, 48, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
    frags.append(text(217, 118, "1. Команда: «Створити вузол +1»", size=12, bold=True, color=INK))
    frags.append(text(217, 134, "Надсилається одиночна RPC-подія", size=10, color=MUTED))

    frags.append(arrow(217, 148, 217, 168, color=POS, sw=1.5))

    frags.append(rect(35, 170, 365, 52, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(217, 190, "2. Мережевий збій або перезавантаження", size=11, bold=True, color=POS))
    frags.append(text(217, 208, "Пакет втрачено, повторна спроба не надійшла", size=10, color=POS))

    frags.append(arrow(217, 224, 217, 244, color=POS, sw=1.5))

    frags.append(rect(35, 246, 365, 60, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
    frags.append(text(217, 266, "3. Розрив внутрішнього стану:", size=11, bold=True, color=INK))
    frags.append(text(217, 283, "База: вважає що вузлів 5 (запит відправлено)", size=10, color=MUTED))
    frags.append(text(217, 297, "Реальність: працює лише 4 вузли", size=10, color=POS))

    frags.append(rect(35, 318, 365, 66, fill="#fff1f2", stroke=POS, sw=1.2, rx=5))
    frags.append(text(217, 338, "Наслідок: незворотний прихований дрейф", size=11, bold=True, color=POS))
    frags.append(text(217, 356, "Система «сліпа» до фізичної реальності,", size=10, color=INK))
    frags.append(text(217, 370, "наступні команди спираються на хибний стан", size=10, color=INK))

    # Права колонка: Level-triggered
    frags.append(rect(445, 50, 395, 350, fill="#f6fbf8", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(642, 78, "Level-triggered (Звірка стану / Reconciliation)", size=13, bold=True, color=FIELD))

    # Кроки правої колонки
    frags.append(rect(460, 98, 365, 48, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
    frags.append(text(642, 118, "1. Декларація: «Бажаний стан = 5 вузлів»", size=12, bold=True, color=INK))
    frags.append(text(642, 134, "Зафіксовано декларативну специфікацію (Spec)", size=10, color=MUTED))

    frags.append(arrow(642, 148, 642, 168, color=FIELD, sw=1.5))

    frags.append(rect(460, 170, 365, 52, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(642, 190, "2. Спостереження (Observe) та Diff", size=11, bold=True, color=FIELD))
    frags.append(text(642, 208, "Фактично працює 4 вузли. Обчислено Δ = +1", size=10, color=INK))

    frags.append(arrow(642, 224, 642, 244, color=FIELD, sw=1.5))

    frags.append(rect(460, 246, 365, 60, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
    frags.append(text(642, 266, "3. Ідемпотентна дія (Act) та перевірка", size=11, bold=True, color=INK))
    frags.append(text(642, 283, "Створюється відсутній 5-й вузол.", size=10, color=MUTED))
    frags.append(text(642, 297, "Навіть якщо пакет втрачено, цикл повторить спробу", size=10, color=FIELD))

    frags.append(rect(460, 318, 365, 66, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=5))
    frags.append(text(642, 338, "Наслідок: самовідновлення та збіжність", size=11, bold=True, color=FIELD))
    frags.append(text(642, 356, "Стан гарантовано зійдеться до бажаного,", size=10, color=INK))
    frags.append(text(642, 370, "незалежно від кількості втрачених повідомлень", size=10, color=INK))

    return frags, w, h


def fig_reconciliation_lifecycle():
    """Фігура 2: Повний життєвий цикл циклу узгодження (Control Loop Lifecycle)."""
    w, h = 860, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 26, "Архітектура та життєвий цикл циклу звірки (Reconciliation Loop)", size=16, bold=True))

    # Джерело істини (Spec / Storage)
    frags.append(rect(25, 60, 220, 80, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(135, 88, "Джерело істини", size=13, bold=True, color=NEG))
    frags.append(text(135, 108, "Бажаний стан (Spec / etcd / Git)", size=10, color=INK))
    frags.append(text(135, 124, "resourceVersion = 1042", size=10, bold=True, color=MUTED))

    # Подія / Watch
    frags.append(arrow(247, 100, 305, 100, color=LINE, sw=1.5))
    frags.append(text(276, 90, "Watch", size=10, color=MUTED))

    # Інформер і локальний кеш
    frags.append(rect(307, 60, 245, 80, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(429, 88, "Informer / Lister Кеш", size=13, bold=True, color=INK))
    frags.append(text(429, 108, "List-Watch + Рефлектор", size=10, color=MUTED))
    frags.append(text(429, 124, "Періодичний resync (30 хв)", size=10, color=MUTED))

    # Черга повідомлень з обмеженням швидкості
    frags.append(arrow(554, 100, 610, 100, color=LINE, sw=1.5))
    frags.append(text(582, 90, "Enqueue", size=10, color=MUTED))

    frags.append(rect(612, 60, 225, 80, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=6))
    frags.append(text(724, 88, "Rate-Limited WorkQueue", size=12, bold=True, color="#b45309"))
    frags.append(text(724, 108, "Дедуплікація ключів (Set)", size=10, color=INK))
    frags.append(text(724, 124, "Exponential Backoff + Jitter", size=10, color=MUTED))

    # Стрілка вниз до Reconciler
    frags.append(arrow(724, 142, 724, 195, color=LINE, sw=1.5))
    frags.append(text(765, 170, "Pop key", size=10, color=MUTED))

    # Головний блок: Цикл звірки (Reconciler Engine)
    frags.append(rect(25, 198, 812, 175, fill="#f8fafc", stroke=LINE, sw=2, rx=8))
    frags.append(text(150, 224, "Reconcile(Request) — Виконавче ядро", size=13, bold=True, color=INK))

    # Підблоки всередині Reconcile
    # 1. Observe
    frags.append(rect(45, 240, 225, 115, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(157, 266, "1. Спостереження (Observe)", size=12, bold=True, color=NEG))
    frags.append(text(157, 288, "• Читання бажаного стану", size=10, color=INK))
    frags.append(text(157, 306, "• Запит стану реальних систем", size=10, color=INK))
    frags.append(text(157, 324, "• Перевірка блокувань (Finalizers)", size=10, color=MUTED))

    frags.append(arrow(272, 297, 308, 297, color=LINE, sw=1.5))

    # 2. Diff
    frags.append(rect(310, 240, 235, 115, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(427, 266, "2. Аналіз розбіжностей (Diff)", size=12, bold=True, color="#d97706"))
    frags.append(text(427, 288, "• 3-way merge (Spec, Actual, Last)", size=10, color=INK))
    frags.append(text(427, 306, "• Обчислення дельти Δ", size=10, color=INK))
    frags.append(text(427, 324, "• Ігнорування системних полів", size=10, color=MUTED))

    frags.append(arrow(547, 297, 583, 297, color=LINE, sw=1.5))

    # 3. Act
    frags.append(rect(585, 240, 235, 115, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(702, 266, "3. Дія (Act & Converge)", size=12, bold=True, color=FIELD))
    frags.append(text(702, 288, "• Ідемпотентне застосування змін", size=10, color=INK))
    frags.append(text(702, 306, "• Створення / видалення / мутація", size=10, color=INK))
    frags.append(text(702, 324, "• Оновлення Observed Status", size=10, color=FIELD))

    # Стрілка вниз від Act до Реального світу
    frags.append(arrow(702, 375, 702, 408, color=FIELD, sw=2))

    # Блок: Реальний світ (Cloud API, Hardware)
    frags.append(rect(450, 410, 387, 55, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(643, 432, "Фізична інфраструктура / Реальний світ", size=12, bold=True, color=FIELD))
    frags.append(text(643, 450, "Хмарні API, балансувальники, віртуальні машини, контейнери", size=10, color=INK))

    # Стрілка зворотного зв'язку до сховища для оновлення статусу
    frags.append(arrow(45, 357, 45, 437, color=NEG, sw=1.5))
    frags.append(line(45, 437, 200, 437, color=NEG, sw=1.5))
    frags.append(arrow(200, 437, 200, 142, color=NEG, sw=1.5))
    frags.append(rect(65, 415, 120, 38, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    frags.append(text(125, 432, "Оновлення Status", size=9, bold=True, color=NEG))
    frags.append(text(125, 444, "(Optimistic Lock)", size=9, color=MUTED))

    return frags, w, h


def fig_state_drift():
    """Фігура 3: Графік дрейфу стану в часі та монотонного збігання."""
    w, h = 840, 380
    frags = []

    # Заголовок
    frags.append(text(w / 2, 26, "Динаміка дрейфу та монотонне зведення розбіжностей у часі", size=16, bold=True))

    # Осі координат
    # Вісь Y: Кількість робочих реплік
    frags.append(line(70, 320, 70, 60, color=LINE, sw=1.5))
    frags.append(arrow(70, 70, 70, 55, color=LINE, sw=1.5))
    frags.append(text(65, 50, "Стан S(t)", size=11, bold=True, anchor="end", color=INK))

    # Позначки Y
    for val, y in [(5, 100), (4, 150), (3, 200), (2, 250), (0, 320)]:
        frags.append(line(65, y, 75, y, color=LINE, sw=1))
        frags.append(text(55, y + 4, str(val), size=10, anchor="end", color=MUTED))

    # Вісь X: Час t
    frags.append(line(70, 320, 800, 320, color=LINE, sw=1.5))
    frags.append(arrow(785, 320, 805, 320, color=LINE, sw=1.5))
    frags.append(text(805, 338, "Час (t)", size=11, bold=True, anchor="end", color=INK))

    # Лінія бажаного стану (Desired State = 4)
    frags.append(line(70, 150, 780, 150, color=NEG, sw=2))
    frags.append(rect(630, 125, 145, 22, fill="#eff6ff", stroke=NEG, sw=1, rx=3))
    frags.append(text(702, 140, "Бажаний стан S* = 4", size=10, bold=True, color=NEG))

    # Траєкторія фактичного стану (Actual State)
    pts = [
        (70, 150), (160, 150), (160, 200), (230, 200), (230, 250),
        (330, 250), (330, 200), (430, 200), (430, 150), (550, 150),
        (550, 100), (640, 100), (640, 150), (780, 150)
    ]
    path_d = ["M %d %d" % pts[0]]
    for p in pts[1:]:
        path_d.append("L %d %d" % p)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_d), FIELD))

    # Позначки подій
    # Подія 1: Аварія
    frags.append(rect(140, 265, 125, 45, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(text(202, 282, "t1, t2: Аварії вузлів", size=9, bold=True, color=POS))
    frags.append(text(202, 298, "Дрейф Δ = +2 (брак)", size=9, color=POS))
    frags.append(line(202, 265, 202, 215, color=POS, sw=1))

    # Подія 2: Збіжність
    frags.append(rect(350, 65, 140, 45, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(420, 82, "t3, t4: Цикл звірки", size=9, bold=True, color=FIELD))
    frags.append(text(420, 98, "Монотонне відновлення", size=9, color=FIELD))
    frags.append(line(420, 110, 420, 185, color=FIELD, sw=1))

    # Подія 3: Зовнішнє втручання
    frags.append(rect(540, 265, 135, 45, fill="#fff7ed", stroke="#f97316", sw=1, rx=4))
    frags.append(text(607, 282, "t5: Ручне втручання", size=9, bold=True, color="#c2410c"))
    frags.append(text(607, 298, "Дрейф Δ = -1 (надлишок)", size=9, color="#c2410c"))
    frags.append(line(607, 265, 607, 120, color="#f97316", sw=1))

    # Подія 4: Виправлення надлишку
    frags.append(rect(675, 65, 115, 45, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(732, 82, "t6: Prune / Drain", size=9, bold=True, color=FIELD))
    frags.append(text(732, 98, "Видалення зайвого", size=9, color=FIELD))
    frags.append(line(732, 110, 732, 135, color=FIELD, sw=1))

    # Легенда знизу
    frags.append(rect(180, 345, 480, 26, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(line(195, 358, 220, 358, color=NEG, sw=2))
    frags.append(text(275, 362, "Бажаний стан S*", size=10, bold=True, color=INK))
    frags.append(line(375, 358, 400, 358, color=FIELD, sw=2.5))
    frags.append(text(465, 362, "Фактичний стан S(t)", size=10, bold=True, color=INK))
    frags.append(text(585, 362, "Відстань D(t) = |S(t) - S*|", size=10, color=MUTED))

    return frags, w, h


def fig_workqueue_architecture():
    """Фігура 4: Архітектура черги завдань контролера (Rate-Limiting WorkQueue)."""
    w, h = 860, 400
    frags = []

    # Заголовок
    frags.append(text(w / 2, 26, "Архітектура черги звірки: коалесценція, обмеження швидкості та бекоф", size=16, bold=True))

    # Вхідний потік подій
    frags.append(rect(20, 60, 160, 260, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(100, 85, "Події Informer", size=12, bold=True, color=INK))

    events = [
        ("Add(pod-1)", "#eff6ff", NEG),
        ("Update(pod-1)", "#eff6ff", NEG),
        ("Update(pod-1)", "#eff6ff", NEG),
        ("Update(pod-2)", "#f0fdf4", FIELD),
        ("Update(pod-1)", "#eff6ff", NEG),
    ]
    for i, (ev, bg_c, txt_c) in enumerate(events):
        ey = 105 + i * 40
        frags.append(rect(30, ey, 140, 32, fill=bg_c, stroke=txt_c, sw=1, rx=4))
        frags.append(text(100, ey + 20, ev, size=10, bold=True, color=txt_c))

    # Стрілка до Dirty Set
    frags.append(arrow(182, 190, 225, 190, color=LINE, sw=1.5))
    frags.append(text(204, 180, "Push", size=9, color=MUTED))

    # Блок WorkQueue внутрішньої структури
    frags.append(rect(227, 50, 395, 330, fill="#ffffff", stroke=LINE, sw=1.8, rx=8))
    frags.append(text(424, 75, "Rate-Limited WorkQueue (Ядро черги)", size=13, bold=True, color=INK))

    # 1. Dirty Set (Коалесценція)
    frags.append(rect(245, 95, 170, 110, fill="#eff6ff", stroke=NEG, sw=1.2, rx=5))
    frags.append(text(330, 118, "Dirty Set (Множина)", size=11, bold=True, color=NEG))
    frags.append(text(330, 136, "Дедуплікація ключів:", size=9, color=MUTED))
    frags.append(rect(255, 145, 150, 24, fill="#ffffff", stroke=NEG, sw=1, rx=3))
    frags.append(text(330, 161, "key: 'default/pod-1'", size=9, bold=True, color=INK))
    frags.append(rect(255, 173, 150, 24, fill="#ffffff", stroke=FIELD, sw=1, rx=3))
    frags.append(text(330, 189, "key: 'default/pod-2'", size=9, bold=True, color=INK))

    # 2. FIFO Queue
    frags.append(rect(435, 95, 170, 110, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=5))
    frags.append(text(520, 118, "Впорядкована черга", size=11, bold=True, color=INK))
    frags.append(text(520, 136, "FIFO для обробки:", size=9, color=MUTED))
    frags.append(rect(445, 145, 150, 24, fill="#ffffff", stroke="#94a3b8", sw=1, rx=3))
    frags.append(text(520, 161, "[0] default/pod-1", size=9, color=INK))
    frags.append(rect(445, 173, 150, 24, fill="#ffffff", stroke="#94a3b8", sw=1, rx=3))
    frags.append(text(520, 189, "[1] default/pod-2", size=9, color=INK))

    frags.append(arrow(417, 150, 433, 150, color=LINE, sw=1.2))

    # 3. Processing Set
    frags.append(rect(245, 220, 360, 65, fill="#fffbeb", stroke="#f59e0b", sw=1.2, rx=5))
    frags.append(text(425, 242, "Processing Set (Активна обробка)", size=11, bold=True, color="#b45309"))
    frags.append(text(425, 260, "Запобігає паралельній обробці одного ключа різними воркерами", size=9, color=INK))
    frags.append(text(425, 274, "Поки ключ тут, нові оновлення чекають у Dirty Set", size=9, color=MUTED))

    # 4. Rate Limiter (Token Bucket + Backoff)
    frags.append(rect(245, 295, 360, 70, fill="#fef2f2", stroke=POS, sw=1.2, rx=5))
    frags.append(text(425, 316, "RateLimiter: TokenBucket + Exponential Backoff", size=11, bold=True, color=POS))
    frags.append(text(425, 334, "При помилці: затримка 200мс -> 400мс -> 800мс -> ... + Jitter", size=9, color=INK))
    frags.append(text(425, 350, "Захист від перевантаження (Thundering Herd Protection)", size=9, color=POS))

    # Стрілка до пулу воркерів
    frags.append(arrow(624, 190, 665, 190, color=LINE, sw=1.5))
    frags.append(text(644, 180, "Pop()", size=9, color=MUTED))

    # Пул воркерів
    frags.append(rect(667, 60, 173, 260, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(753, 85, "Пул воркерів", size=12, bold=True, color=FIELD))

    for w_idx in range(1, 4):
        wy = 85 + w_idx * 48
        frags.append(rect(677, wy, 153, 40, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
        frags.append(text(753, wy + 18, "Worker #%d" % w_idx, size=10, bold=True, color=FIELD))
        frags.append(text(753, wy + 32, "Reconcile(key)", size=9, color=MUTED))

    # Зворотний зв'язок: Forget() або Requeue()
    frags.append(arrow(753, 295, 753, 355, color=LINE, sw=1.2))
    frags.append(line(753, 355, 607, 355, color=LINE, sw=1.2))
    frags.append(rect(655, 340, 95, 28, fill="#ffffff", stroke=LINE, sw=1, rx=3))
    frags.append(text(702, 357, "Done / Requeue", size=9, bold=True, color=INK))

    return frags, w, h


def main():
    figs = [
        ("edge-vs-level-trigger.svg", fig_edge_vs_level),
        ("reconciliation-loop-lifecycle.svg", fig_reconciliation_lifecycle),
        ("reconciliation-state-drift.svg", fig_state_drift),
        ("workqueue-coalescing-backoff.svg", fig_workqueue_architecture),
    ]

    for fname, func in figs:
        frags, w, h = func()
        path = os.path.join(OUT, fname)
        render(path, w, h, *frags)
        print("Generated: %s (%dx%d)" % (path, w, h))


if __name__ == "__main__":
    main()
