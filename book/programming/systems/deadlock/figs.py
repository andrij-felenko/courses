# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

C_THREAD = "#2457d6"    # потік (синій)
C_RES    = "#27ae60"    # ресурс (зелений)
C_REQ    = "#c0392b"    # запит очікування (червоний)
C_HOLD   = "#1e824c"    # утримання (темно-зелений)
C_BG_BOX = "#f8f9fa"


# ── Фігура 1: Граф виділення ресурсів (RAG) із замкненим циклом ─────────────
def fig_rag_deadlock():
    W, H = 760, 370
    frags = []

    frags.append(text(W / 2, 28, "Граф виділення ресурсів: замкнений цикл очікування (дедлок)", size=15, bold=True))

    t1_x, t1_y = 190, 190
    t2_x, t2_y = 570, 190

    r1_x, r1_y = 380, 95
    r2_x, r2_y = 380, 285

    # Ресурс R1 (М'ютекс A)
    frags.append(rect(r1_x - 70, r1_y - 28, 140, 56, fill="#eafaf1", stroke=C_RES, sw=2, rx=6))
    frags.append(text(r1_x, r1_y - 6, "Ресурс R₁", size=13, bold=True, color=INK))
    frags.append(text(r1_x, r1_y + 14, "(М'ютекс A)", size=11, color=MUTED))

    # Ресурс R2 (М'ютекс B)
    frags.append(rect(r2_x - 70, r2_y - 28, 140, 56, fill="#eafaf1", stroke=C_RES, sw=2, rx=6))
    frags.append(text(r2_x, r2_y - 6, "Ресурс R₂", size=13, bold=True, color=INK))
    frags.append(text(r2_x, r2_y + 14, "(М'ютекс B)", size=11, color=MUTED))

    # Потік T1
    frags.append(rect(t1_x - 75, t1_y - 35, 150, 70, fill="#ebf3fd", stroke=C_THREAD, sw=2, rx=10))
    frags.append(text(t1_x, t1_y - 12, "Потік T₁", size=14, bold=True, color=C_THREAD))
    frags.append(text(t1_x, t1_y + 8, "Тримає: R₁", size=11, bold=True, color=C_HOLD))
    frags.append(text(t1_x, t1_y + 24, "Чекає: R₂", size=11, color=C_REQ))

    # Потік T2
    frags.append(rect(t2_x - 75, t2_y - 35, 150, 70, fill="#ebf3fd", stroke=C_THREAD, sw=2, rx=10))
    frags.append(text(t2_x, t2_y - 12, "Потік T₂", size=14, bold=True, color=C_THREAD))
    frags.append(text(t2_x, t2_y + 8, "Тримає: R₂", size=11, bold=True, color=C_HOLD))
    frags.append(text(t2_x, t2_y + 24, "Чекає: R₁", size=11, color=C_REQ))

    # Стрілки утримання (Ресурс -> Потік)
    # R1 -> T1
    frags.append(arrow(r1_x - 70, r1_y + 10, t1_x + 35, t1_y - 35, color=C_HOLD, sw=2))
    frags.append(text(240, 115, "Виділено для T₁", size=10, bold=True, color=C_HOLD))

    # R2 -> T2
    frags.append(arrow(r2_x + 70, r2_y - 10, t2_x - 35, t2_y + 35, color=C_HOLD, sw=2))
    frags.append(text(520, 265, "Виділено для T₂", size=10, bold=True, color=C_HOLD))

    # Стрілки очікування (Потік -> Ресурс)
    # T1 -> R2
    frags.append(arrow(t1_x + 35, t1_y + 35, r2_x - 70, r2_y - 10, color=C_REQ, sw=2))
    frags.append(text(240, 265, "T₁ чекає на R₂", size=10, bold=True, color=C_REQ))

    # T2 -> R1
    frags.append(arrow(t2_x - 35, t2_y - 35, r1_x + 70, r1_y + 10, color=C_REQ, sw=2))
    frags.append(text(520, 115, "T₂ чекає на R₁", size=10, bold=True, color=C_REQ))

    # Центральний маркер циклу
    frags.append(rect(280, 175, 200, 30, fill="#fdf2e9", stroke=POS, sw=1.5, rx=4))
    frags.append(text(380, 195, "ЦИКЛ: T₁ → R₂ → T₂ → R₁ → T₁", size=9, bold=True, color=POS))

    # Легенда внизу
    frags.append(line(80, 345, 120, 345, color=C_HOLD, sw=2))
    frags.append(text(195, 349, "Утримання (ресурс виділено)", size=11, color=INK))

    frags.append(line(370, 345, 410, 345, color=C_REQ, sw=2))
    frags.append(text(495, 349, "Запит (очікування на замок)", size=11, color=INK))

    render(os.path.join(OUT, 'rag-deadlock.svg'), W, H, *frags)


# ── Фігура 2: Ієрархія замків (DAG проти циклу) ─────────────────────────────
def fig_lock_hierarchy():
    W, H = 760, 360
    frags = []

    frags.append(text(W / 2, 28, "Запобігання дедлоку: ациклічний порядок захоплення замків", size=15, bold=True))

    # Ліва колонка: Хаотичний порядок (є цикл)
    frags.append(rect(20, 55, 345, 285, fill="#fffaf9", stroke="#f5b7b1", sw=1.5, rx=8))
    frags.append(text(192, 80, "✗ Довільний порядок (ризик циклу)", size=13, bold=True, color=POS))

    # Вузли ліворуч
    frags.append(rect(60, 110, 105, 45, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    frags.append(text(112, 137, "М'ютекс A", size=12, bold=True))

    frags.append(rect(220, 110, 105, 45, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    frags.append(text(272, 137, "М'ютекс B", size=12, bold=True))

    # Стрілки ліворуч
    frags.append(arrow(165, 125, 220, 125, color=POS, sw=2))
    frags.append(text(192, 118, "Потік 1", size=10, bold=True, color=POS))

    frags.append(arrow(220, 142, 165, 142, color=NEG, sw=2))
    frags.append(text(192, 158, "Потік 2", size=10, bold=True, color=NEG))

    frags.append(rect(40, 205, 305, 115, fill="#ffffff", stroke="#ebccd1", sw=1, rx=6))
    frags.append(text(192, 230, "Потік 1: бере A → намагається взяти B", size=11, color=INK))
    frags.append(text(192, 255, "Потік 2: бере B → намагається взяти A", size=11, color=INK))
    frags.append(text(192, 285, "Наслідок: взаємне блокування (дедлок)", size=11, bold=True, color=POS))

    # Права колонка: Сувора ієрархія рангів (DAG)
    frags.append(rect(395, 55, 345, 285, fill="#f4faf6", stroke="#a9dfbf", sw=1.5, rx=8))
    frags.append(text(567, 80, "✓ Сувора ієрархія рангів (DAG)", size=13, bold=True, color=FIELD))

    # Рівні ієрархії
    frags.append(rect(435, 105, 265, 40, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(480, 129, "Рівень 1:", size=11, bold=True, color=FIELD))
    frags.append(text(585, 129, "М'ютекс мережі (Ранг 100)", size=11))

    frags.append(arrow(567, 145, 567, 175, color=FIELD, sw=2))

    frags.append(rect(435, 175, 265, 40, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(480, 199, "Рівень 2:", size=11, bold=True, color=FIELD))
    frags.append(text(585, 199, "М'ютекс сесії (Ранг 200)", size=11))

    frags.append(arrow(567, 215, 567, 245, color=FIELD, sw=2))

    frags.append(rect(435, 245, 265, 40, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(480, 269, "Рівень 3:", size=11, bold=True, color=FIELD))
    frags.append(text(585, 269, "М'ютекс диска (Ранг 300)", size=11))

    frags.append(text(567, 315, "Правило: захоплення тільки у порядку зростання рангу", size=10, bold=True, color=INK))

    render(os.path.join(OUT, 'lock-hierarchy.svg'), W, H, *frags)


# ── Фігура 3: Порівняння Дедлок vs Лайвлок vs Штатна робота ─────────────────
def fig_deadlock_vs_livelock():
    W, H = 760, 390
    frags = []

    frags.append(text(W / 2, 26, "Порівняння станів конкурентності", size=15, bold=True))

    # Рядок 1: Дедлок
    frags.append(rect(20, 50, 720, 95, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    frags.append(rect(35, 65, 130, 30, fill=POS, stroke=POS, rx=4))
    frags.append(text(100, 85, "Дедлок (Deadlock)", size=12, bold=True, color="#ffffff"))
    frags.append(text(275, 78, "Стан потоків: СПЛЯТЬ / ЗАБЛОКОВАНІ", size=11, bold=True, color=POS))
    frags.append(text(275, 98, "Навантаження CPU: 0%", size=11, color=INK))
    frags.append(text(550, 78, "Поведінка: кожен потік спить в очікуванні ресурсу.", size=10, color=INK))
    frags.append(text(550, 95, "Змін стану немає, прогрес відсутній назавжди.", size=10, color=INK))
    frags.append(text(550, 112, "Лікування: перезапуск, таймаут або аборт транзакції.", size=10, color=MUTED))

    # Рядок 2: Лайвлок
    frags.append(rect(20, 160, 720, 95, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=8))
    frags.append(rect(35, 175, 130, 30, fill="#f39c12", stroke="#f39c12", rx=4))
    frags.append(text(100, 195, "Лайвлок (Livelock)", size=12, bold=True, color="#ffffff"))
    frags.append(text(275, 188, "Стан потоків: АКТИВНІ (АКТИВНИЙ ЦИКЛ)", size=11, bold=True, color="#b9770e"))
    frags.append(text(275, 208, "Навантаження CPU: 100%", size=11, color=INK))
    frags.append(text(550, 188, "Поведінка: потоки відпускають ресурси й повторюють", size=10, color=INK))
    frags.append(text(550, 205, "спробу синхронно, знову заважаючи один одному.", size=10, color=INK))
    frags.append(text(550, 222, "Лікування: випадкова експоненційна затримка (jitter).", size=10, color=MUTED))

    # Рядок 3: Штатна робота
    frags.append(rect(20, 270, 720, 95, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    frags.append(rect(35, 285, 130, 30, fill=FIELD, stroke=FIELD, rx=4))
    frags.append(text(100, 305, "Штатний прогрес", size=12, bold=True, color="#ffffff"))
    frags.append(text(275, 298, "Стан потоків: ВИКОНАННЯ ЗА ЧЕРГОЮ", size=11, bold=True, color=FIELD))
    frags.append(text(275, 318, "Навантаження CPU: Корисна робота", size=11, color=INK))
    frags.append(text(550, 298, "Поведінка: замки захоплюються в єдиному порядку або", size=10, color=INK))
    frags.append(text(550, 315, "атомарно через std::scoped_lock / std::lock.", size=10, color=INK))
    frags.append(text(550, 332, "Результат: дедлоки та лайвлоки математично неможливі.", size=10, color=MUTED))

    render(os.path.join(OUT, 'deadlock-vs-livelock.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_rag_deadlock()
    fig_lock_hierarchy()
    fig_deadlock_vs_livelock()
    print("SVG figures generated successfully.")
