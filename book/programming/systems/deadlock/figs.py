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
    W, H = 760, 360
    frags = []

    # Заголовок / опис графа
    frags.append(text(W / 2, 28, "Граф виділення ресурсів: замкнений цикл очікування (дедлок)", size=15, bold=True))

    # Позиції вузлів
    t1_x, t1_y = 200, 190
    t2_x, t2_y = 560, 190

    r1_x, r1_y = 380, 100
    r2_x, r2_y = 380, 280

    # Тіла вузлів
    # Ресурс R1 (М'ютекс A)
    frags.append(rect(r1_x - 70, r1_y - 30, 140, 60, fill="#eafaf1", stroke=C_RES, sw=2, rx=6))
    frags.append(text(r1_x, r1_y - 6, "Ресурс R₁", size=13, bold=True, color=INK))
    frags.append(text(r1_x, r1_y + 14, "(М'ютекс A)", size=11, color=MUTED))

    # Ресурс R2 (М'ютекс B)
    frags.append(rect(r2_x - 70, r2_y - 30, 140, 60, fill="#eafaf1", stroke=C_RES, sw=2, rx=6))
    frags.append(text(r2_x, r2_y - 6, "Ресурс R₂", size=13, bold=True, color=INK))
    frags.append(text(r2_x, r2_y + 14, "(М'ютекс B)", size=11, color=MUTED))

    # Потік T1
    frags.append(rect(t1_x - 75, t1_y - 35, 150, 70, fill="#ebf3fd", stroke=C_THREAD, sw=2, rx=10))
    frags.append(text(t1_x, t1_y - 10, "Потік T₁", size=14, bold=True, color=C_THREAD))
    frags.append(text(t1_x, t1_y + 10, "Тримає: R₁", size=11, bold=True, color=C_HOLD))
    frags.append(text(t1_x, t1_y + 24, "Чекає: R₂", size=11, color=C_REQ))

    # Потік T2
    frags.append(rect(t2_x - 75, t2_y - 35, 150, 70, fill="#ebf3fd", stroke=C_THREAD, sw=2, rx=10))
    frags.append(text(t2_x, t2_y - 10, "Потік T₂", size=14, bold=True, color=C_THREAD))
    frags.append(text(t2_x, t2_y + 10, "Тримає: R₂", size=11, bold=True, color=C_HOLD))
    frags.append(text(t2_x, t2_y + 24, "Чекає: R₁", size=11, color=C_REQ))

    # Стрілки утримання (Ресурс -> Потік)
    # R1 -> T1
    frags.append(arrow(r1_x - 70, r1_y + 10, t1_x + 30, t1_y - 35, color=C_HOLD, sw=2))
    frags.append(text(275, 115, "Виділено для T₁", size=10, bold=True, color=C_HOLD))

    # R2 -> T2
    frags.append(arrow(r2_x + 70, r2_y - 10, t2_x - 30, t2_y + 35, color=C_HOLD, sw=2))
    frags.append(text(485, 265, "Виділено для T₂", size=10, bold=True, color=C_HOLD))

    # Стрілки очікування (Потік -> Ресурс)
    # T1 -> R2
    frags.append(arrow(t1_x + 30, t1_y + 35, r2_x - 70, r2_y - 10, color=C_REQ, sw=2, dash="5 3"))
    frags.append(text(275, 265, "T₁ чекає на R₂", size=10, bold=True, color=C_REQ))

    # T2 -> R1
    frags.append(arrow(t2_x - 30, t2_y - 35, r1_x + 70, r1_y + 10, color=C_REQ, sw=2, dash="5 3"))
    frags.append(text(485, 115, "T₂ чекає на R₁", size=10, bold=True, color=C_REQ))

    # Центральний маркер циклу
    frags.append(rect(320, 175, 120, 30, fill="#fdf2e9", stroke=POS, sw=1.5, rx=4))
    frags.append(text(380, 195, "ЦИКЛ: T₁ → R₂ → T₂ → R₁ → T₁", size=8, bold=True, color=POS))

    # Легенда внизу
    frags.append(line(80, 335, 120, 335, color=C_HOLD, sw=2))
    frags.append(text(195, 339, "Утримання (ресурс виділено)", size=11, color=INK))

    frags.append(line(370, 335, 410, 335, color=C_REQ, sw=2, dash="5 3"))
    frags.append(text(495, 339, "Запит (очікування на замок)", size=11, color=INK))

    return svg(W, H, "".join(frags))


# ── Фігура 2: Ієрархія замків (DAG проти циклу) ─────────────────────────────
def fig_lock_hierarchy():
    W, H = 760, 360
    frags = []

    frags.append(text(W / 2, 28, "Запобігання дедлоку: ациклічний порядок захоплення замків", size=15, bold=True))

    # Ліва колонка: Хаотичний порядок (є цикл)
    frags.append(rect(20, 55, 345, 285, fill="#fffaf9", stroke="#f5b7b1", sw=1.5, rx=8))
    frags.append(text(192, 80, "✗ Довільний порядок (ризик циклу)", size=13, bold=True, color=POS))

    # Вузли ліворуч
    frags.append(rect(60, 110, 110, 45, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    frags.append(text(115, 137, "М'ютекс A", size=12, bold=True))

    frags.append(rect(215, 110, 110, 45, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    frags.append(text(270, 137, "М'ютекс B", size=12, bold=True))

    # Стрілки ліворуч
    frags.append(arrow(170, 125, 215, 125, color=POS, sw=2))
    frags.append(text(192, 118, "Потік 1", size=10, bold=True, color=POS))

    frags.append(arrow(215, 142, 170, 142, color=NEG, sw=2))
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

    return svg(W, H, "".join(frags))


# ── Фігура 3: Порівняння Дедлок vs Лайвлок vs Штатна робота ─────────────────
def fig_deadlock_vs_livelock():
    W, H = 760, 390
    frags = []

    frags.append(text(W / 2, 26, "Порівняння станів конкурентності", size=15, bold=True))

    # Рядок 1: Дедлок
    frags.append(rect(20, 50, 720, 95, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    frags.append(rect(35, 65, 130, 30, fill=POS, stroke=POS, rx=4))
    frags.append(text(100, 85, "Дедлок (Deadlock)", size=12, bold=True, color="#ffffff"))
    frags.append(text(260, 78, "Стан потоків: СПЛЯТЬ / ЗАБЛОКОВАНІ", size=11, bold=True, color=POS))
    frags.append(text(260, 98, "Навантаження CPU: 0%", size=11, color=INK))
    frags.append(text(540, 78, "Поведінка: кожен потік спить в очікуванні ресурсу.", size=10, color=INK))
    frags.append(text(540, 95, "Змін стану немає, прогрес відсутній назавжди.", size=10, color=INK))
    frags.append(text(540, 112, "Лікування: перезапуск, таймаут або аборт транзакції.", size=10, color=MUTED))

    # Рядок 2: Лайвлок
    frags.append(rect(20, 160, 720, 95, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=8))
    frags.append(rect(35, 175, 130, 30, fill="#f39c12", stroke="#f39c12", rx=4))
    frags.append(text(100, 195, "Лайвлок (Livelock)", size=12, bold=True, color="#ffffff"))
    frags.append(text(260, 188, "Стан потоків: АКТИВНІ (АКТИВНИЙ ЦИКЛ)", size=11, bold=True, color="#b9770e"))
    frags.append(text(260, 208, "Навантаження CPU: 100%", size=11, color=INK))
    frags.append(text(540, 188, "Поведінка: потоки відпускають ресурси й повторюють", size=10, color=INK))
    frags.append(text(540, 205, "спробу синхронно, знову заважаючи один одному.", size=10, color=INK))
    frags.append(text(540, 222, "Лікування: випадкова експоненційна затримка (jitter).", size=10, color=MUTED))

    # Рядок 3: Штатна робота
    frags.append(rect(20, 270, 720, 95, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    frags.append(rect(35, 285, 130, 30, fill=FIELD, stroke=FIELD, rx=4))
    frags.append(text(100, 305, "Штатний прогрес", size=12, bold=True, color="#ffffff"))
    frags.append(text(260, 298, "Стан потоків: ВИКОНАННЯ ЗА ЧЕРГОЮ", size=11, bold=True, color=FIELD))
    frags.append(text(260, 318, "Навантаження CPU: Корисна робота", size=11, color=INK))
    frags.append(text(540, 298, "Поведінка: замки захоплюються в єдиному порядку або", size=10, color=INK))
    frags.append(text(540, 315, "атомарно через std::scoped_lock / std::lock.", size=10, color=INK))
    frags.append(text(540, 332, "Результат: дедлоки та лайвлоки математично неможливі.", size=10, color=MUTED))

    return svg(W, H, "".join(frags))


if __name__ == '__main__':
    with open(os.path.join(OUT, 'rag-deadlock.svg'), 'w', encoding='utf-8') as f:
        f.write(fig_rag_deadlock())
    with open(os.path.join(OUT, 'lock-hierarchy.svg'), 'w', encoding='utf-8') as f:
        f.write(fig_lock_hierarchy())
    with open(os.path.join(OUT, 'deadlock-vs-livelock.svg'), 'w', encoding='utf-8') as f:
        f.write(fig_deadlock_vs_livelock())
    print("SVG figures generated successfully.")
